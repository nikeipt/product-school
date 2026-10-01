from pathlib import Path
import sys
import unittest
from unittest.mock import patch

build = Path(__file__).resolve().parent
sys.path.insert(0, str(build))
import agent
import tools

class BoundaryTests(unittest.TestCase):
    def test_effective_caps(self):
        self.assertEqual(3, agent.MAX_ITERATIONS)
        self.assertEqual(5, tools.MAX_QUEUE_ITEMS)
        self.assertEqual('rejected', tools.propose_stories('P-NORTH', ['story'] * 6)['status'])

    def test_only_one_retry(self):
        with patch.dict(tools.TOOLS, broken=unittest.mock.Mock(side_effect=RuntimeError)):
            result = agent.call_tool_with_retries('broken', {})
            self.assertEqual(2, tools.TOOLS['broken'].call_count)
            self.assertEqual('tool_retrieval_failed', result['error'])

    def test_roadmap_is_project_scoped(self):
        result = tools.get_roadmap('P-NORTH')
        self.assertIn('Northstar', result['roadmap'])
        self.assertNotIn('Vega', result['roadmap'])
        self.assertNotIn('Orbit', str(result))
        self.assertNotIn('Pulsar', str(result))

    def test_ambiguous_and_restricted_queries_fail_closed(self):
        for query in ['', 'roadmap', 'P-ORBIT', 'P-PULSAR']:
            self.assertIn('error', tools.get_roadmap(query))
            self.assertIn('error', tools.search_past_updates(query))

    def test_missing_and_confidential_projects_disclose_no_records(self):
        for pid in ['P-HALO', 'P-ORBIT', 'P-PULSAR']:
            for retrieve in [tools.get_project, tools.get_activity]:
                result = retrieve(pid)
                self.assertEqual('project_not_found', result['error'])
                self.assertNotIn('known_projects', result)
                self.assertNotIn('prd_summary', result)

    def test_memory_lookup_has_no_cross_project_fallback(self):
        result = tools.search_past_updates('P-NORTH')
        matches = result['matches']
        self.assertTrue(all(item['project'] in {'Northstar', 'team'} for item in matches))
        self.assertEqual(2, len([item for item in matches if 'week' in item]))

    def test_brief_and_norms_redact_restricted_names(self):
        for text in [tools.get_task('jailbreak')['body'], tools.get_norms()['norms']]:
            self.assertNotIn('Orbit', text)
            self.assertNotIn('Pulsar', text)
        self.assertIn('SYSTEM OVERRIDE', tools.get_task('jailbreak')['body'])


    def test_recorded_prd_alias_resolves_to_same_scoped_evidence(self):
        self.assertEqual(tools.get_roadmap('P-NORTH'), tools.get_roadmap('PRD-Northstar-v3'))
        self.assertEqual(tools.search_past_updates('P-NORTH'),
                         tools.search_past_updates('PRD-Northstar-v3'))

    def test_invalid_queries_are_not_reported_as_missing_projects(self):
        self.assertEqual('invalid_project_query', tools.get_roadmap('not-a-project')['error'])
        self.assertEqual('invalid_project_query', tools.search_past_updates('')['error'])
        self.assertEqual('project_not_found', tools.get_project('P-HALO')['error'])

    def test_confidential_prd_alias_does_not_bypass_blocking(self):
        result = tools.get_roadmap('PRD-Orbit-v0')
        self.assertEqual('invalid_project_query', result['error'])
        self.assertNotIn('roadmap', result)

if __name__ == '__main__':
    unittest.main()
