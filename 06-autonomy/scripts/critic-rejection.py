"""Lab fault injection: real model calls, deliberately corrupted drafter story."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '00-build'))
import agent
original_create = agent.BudgetClient.create

def inject_unsupported_story(self, **kwargs):
    response = original_create(self, **kwargs)
    if kwargs.get('response_format', {}).get('type') == 'json_object':
        message = response.choices[0].message
        payload = json.loads(message.content)
        payload.update(outcome='done', project_id='P-NORTH', status='green')
        payload['leadership_update'] = 'Northstar is on track. Issue #825 remains open for contextual tips A/B analytics review.'
        payload['proposed_sprint_stories'] = [{
            'title': 'Launch a referral rewards programme',
            'remaining_scope': 'Build referral rewards and referral tracking for onboarding.',
            'source_refs': ['activity:P-NORTH:#825'],
        }]
        message.content = json.dumps(payload)
        print('\nFAULT INJECTION: replaced drafter story with unsupported referral work; validator response is unmodified.')
    return response

agent.BudgetClient.create = inject_unsupported_story
print('LAB FAULT-INJECTION TEST: not a naturally generated failure. Real retrieval, API budget, critic and escalation path. Fault reinserted after revision to test persistent failure.')
agent.run('happy')
