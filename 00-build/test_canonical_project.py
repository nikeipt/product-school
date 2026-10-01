import unittest
from unittest.mock import patch
import agent
import tools

class CanonicalProjectTests(unittest.TestCase):
    def test_task_accepts_exact_id_name_and_prd_alias(self):
        for selector in ['P-NORTH (Northstar)', 'Northstar', 'PRD-Northstar-v3']:
            context = tools.resolve_task_project('Project: ' + selector)
            self.assertEqual('P-NORTH', context['project_id'])

    def test_missing_multiple_unknown_and_restricted_selection_stop(self):
        for body in ['', 'Project: P-NORTH\nProject: P-VEGA',
                     'Project: P-HALO', 'Project: PRD-Orbit-v0']:
            self.assertIn('error', tools.resolve_task_project(body))

    def test_all_project_tools_use_the_pinned_id(self):
        context = tools.resolve_task_project('Project: P-NORTH')
        for name, key in [('get_project','project_id'), ('get_activity','project_id'),
                          ('get_roadmap','query'), ('search_past_updates','query')]:
            self.assertEqual('P-NORTH', agent.pin_project_args(
                name, {key:'PRD-Northstar-v3'}, context)[key])

    def test_cross_project_or_unknown_argument_is_rejected(self):
        context = tools.resolve_task_project('Project: P-NORTH')
        for selector in ['P-VEGA', 'P-HALO', 'made-up']:
            with self.assertRaises(ValueError):
                agent.pin_project_args('get_activity', {'project_id':selector}, context)

    def test_restricted_task_stops_before_model_client_creation(self):
        with patch.object(agent.tools, 'get_task', return_value={'body':'Project: P-ORBIT'}), \
             patch.object(agent, 'OpenAI') as client, \
             patch.object(agent, 'emit_deliverable') as emit:
            agent.run('happy')
        client.assert_not_called()
        self.assertFalse(emit.call_args.kwargs['accepted'])
