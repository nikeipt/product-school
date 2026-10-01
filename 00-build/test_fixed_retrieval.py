import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch
import agent
import tools

class FixedRetrievalTests(unittest.TestCase):
    def test_each_source_is_fetched_once_with_canonical_id(self):
        context = tools.resolve_task_project('Project: PRD-Northstar-v3')
        with patch.object(agent, 'call_tool_with_retries', wraps=agent.call_tool_with_retries) as call:
            bundle, refs, error = agent.retrieve_evidence_bundle(context)
        self.assertIsNone(error)
        self.assertEqual(5, call.call_count)
        self.assertEqual(5, len(bundle))
        for entry in call.call_args_list:
            self.assertEqual({'P-NORTH'}, set(entry.args[1].values()))
        self.assertIn('activity:P-NORTH:#825', refs)

    def test_unavailable_source_stops_before_model_access(self):
        with patch.dict(tools.TOOLS, get_activity=Mock(return_value={'error':'source_unavailable'})), \
             patch.object(agent, 'OpenAI') as client, patch.object(agent, 'emit_deliverable') as emit:
            with redirect_stdout(io.StringIO()):
                agent.run('happy')
        client.assert_not_called()
        self.assertFalse(emit.call_args.kwargs['accepted'])

    def test_temporary_failure_retries_once_then_preserves_bundle(self):
        retrieve = Mock(side_effect=[RuntimeError(), tools.get_activity('P-NORTH')])
        with patch.dict(tools.TOOLS, get_activity=retrieve), redirect_stdout(io.StringIO()):
            bundle, refs, error = agent.retrieve_evidence_bundle(
                tools.resolve_task_project('Project: P-NORTH'))
        self.assertIsNone(error)
        self.assertEqual(2, retrieve.call_count)
        self.assertIn('get_activity', bundle)

    def test_persistent_failure_stops_after_one_retry(self):
        retrieve = Mock(side_effect=RuntimeError())
        with patch.dict(tools.TOOLS, get_activity=retrieve), redirect_stdout(io.StringIO()):
            bundle, refs, error = agent.retrieve_evidence_bundle(
                tools.resolve_task_project('Project: P-NORTH'))
        self.assertEqual(2, retrieve.call_count)
        self.assertIsNotNone(error)
        self.assertIn('get_project', bundle)

    def test_bundle_contains_no_restricted_fixture_names(self):
        bundle, refs, error = agent.retrieve_evidence_bundle(
            tools.resolve_task_project('Project: P-NORTH'))
        self.assertNotIn('Orbit', str(bundle))
        self.assertNotIn('Pulsar', str(bundle))
