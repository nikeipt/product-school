import json
import io
from contextlib import redirect_stdout
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
import agent
import tools


class CombinedDraftTests(unittest.TestCase):
    def test_revision_fits_three_turns_without_story_tool_turn(self):
        calls = [NS(id=str(i), function=NS(name=name, arguments=json.dumps({'project_id':'P-NORTH'})))
                 for i, name in enumerate(['get_project', 'get_activity'])]
        story = {'title':'Review analytics for contextual tips A/B',
                 'remaining_scope':'Complete the outstanding analytics review in #825',
                 'source_refs':['activity:P-NORTH:#825']}
        payload = {'outcome':'done', 'project_id':'P-NORTH', 'status':'green',
                   'leadership_update':'Grounded update', 'proposed_sprint_stories':[story],
                   'story_proposal_status':'queued_for_approval'}
        def response(tool_calls=None, content=None):
            return NS(usage=NS(prompt_tokens=0, completion_tokens=0),
                      choices=[NS(message=NS(tool_calls=tool_calls, content=content))])
        create = Mock(side_effect=[response(content=json.dumps(payload)),
                                   response(content=json.dumps(payload))])
        client = NS(chat=NS(completions=NS(create=create)))
        verdicts = [{'verdict':'fail', 'reasons':['unsupported detail'], '_usage':{'prompt':0,'completion':0}},
                    {'verdict':'pass', 'reasons':[], '_usage':{'prompt':0,'completion':0}}]
        with redirect_stdout(io.StringIO()), patch.object(agent, 'BudgetClient', return_value=client), patch.object(agent, 'OpenAI'), \
             patch.object(agent, 'review', side_effect=verdicts) as critic, \
             patch.object(agent, 'emit_deliverable') as emit:
            agent.run('happy')
        self.assertEqual(2, create.call_count)
        self.assertEqual(2, critic.call_count)
        self.assertTrue(emit.call_args.kwargs['accepted'])
        for request in create.call_args_list:
            self.assertNotIn("tools", request.kwargs)

import tools
from story_evidence import evidence_records, validate_story_evidence

class StoryReferenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = evidence_records('get_activity', tools.get_activity('P-NORTH'))
        self.evidence.update(evidence_records('get_roadmap', tools.get_roadmap('P-NORTH')))

    def errors(self, refs, scope='Complete the recorded remaining work'):
        story = {'title':'Candidate', 'remaining_scope':scope, 'source_refs':refs}
        return validate_story_evidence([story], self.evidence, 'P-NORTH', 5)

    def test_open_issue_supports_remaining_work(self):
        self.assertEqual([], self.errors(['activity:P-NORTH:#825']))

    def test_merged_implementation_alone_cannot_support_followup(self):
        self.assertTrue(self.errors(['activity:P-NORTH:#820']))

    def test_rollout_can_be_assessed_separately_from_merged_code(self):
        self.assertEqual([], self.errors(['activity:P-NORTH:#820', 'roadmap:P-NORTH'],
                                       'Continue the rollout stated in the roadmap'))

    def test_unknown_and_wrong_project_refs_rejected(self):
        self.assertTrue(self.errors(['activity:P-NORTH:#999']))
        self.evidence['activity:P-VEGA:#440'] = {
            'project_id':'P-VEGA', 'kind':'issue_open', 'record':{}}
        self.assertTrue(self.errors(['activity:P-VEGA:#440']))

    def test_remaining_scope_is_mandatory(self):
        self.assertTrue(self.errors(['activity:P-NORTH:#825'], ''))

    def test_six_stories_rejected_without_queueing(self):
        self.assertTrue(validate_story_evidence([{}] * 6, self.evidence, 'P-NORTH', 5))
