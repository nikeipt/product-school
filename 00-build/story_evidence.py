"""Evidence IDs and structural checks; semantic scope remains validator-owned."""


def evidence_records(tool, result):
    if 'error' in result:
        return {}
    project = result.get('project_id')
    if tool == 'get_activity':
        return {f"activity:{project}:{item.get('id', item.get('name', index))}":
                {'project_id': project, 'kind': item.get('type'), 'record': item}
                for index, item in enumerate(result.get('activity', []))}
    if tool == 'get_project':
        return {f'project:{project}': {'project_id': project, 'kind': 'scope', 'record': result}}
    if tool == 'get_roadmap':
        return {f'roadmap:{project}': {'project_id': project, 'kind': 'roadmap', 'record': result}}
    return {}


def validate_story_evidence(stories, evidence, project_id, cap):
    if not isinstance(stories, list):
        return ['story proposal must be a list']
    if len(stories) > cap:
        return ['story batch exceeds queue cap']
    reasons = []
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            reasons.append(f'story {index} must include title, remaining_scope and source_refs')
            continue
        for field in ['title', 'remaining_scope']:
            if not isinstance(story.get(field), str) or not story[field].strip():
                reasons.append(f'story {index} is missing {field}')
        refs = story.get('source_refs')
        if not isinstance(refs, list) or not refs:
            reasons.append(f'story {index} is missing source_refs')
            continue
        records = []
        for ref in refs:
            record = evidence.get(ref) if isinstance(ref, str) else None
            if record is None or record.get('project_id') != project_id:
                reasons.append(f'story {index} cites unavailable or wrong-project evidence')
            else:
                records.append(record)
        # Merged implementation alone cannot substantiate unfinished follow-up.
        # An open issue or roadmap can, but the validator must check exact scope.
        if records and not any(r['kind'] in {'issue_open', 'pr_open', 'roadmap'} for r in records):
            reasons.append(f'story {index} has no evidence of remaining work')
    return reasons
