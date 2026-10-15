"""Require drawable art plans before generation and bind semantic reviews to inputs."""
import argparse
import json
from pathlib import Path
import numpy as np
from style_choice import digest, verify_style

HUMAN_ORDER = ('head', 'neck', 'torso', 'left_arm', 'right_arm', 'lower_body')


def validate_plan(plan):
    if plan.get('outline_strategy') not in ('visible_source_ink', 'explicit_mask'):
        raise ValueError('Choose visible source contours or an aligned explicit outline mask before generation')
    if not plan.get('composition') or not plan.get('drawability_reason'):
        raise ValueError('Plan the composition and explain drawing feasibility before generation')
    parts, subjects = plan.get('parts', []), plan.get('subjects', [])
    identities = [part.get('id') for part in parts]
    if not parts or not all(identities) or len(set(identities)) != len(identities):
        raise ValueError('A drawing plan needs unique semantic parts')
    if plan.get('outline_order') != identities or plan.get('fill_order') != identities:
        raise ValueError('Outline and fill must use the same planned part order')
    subject_map = {subject['id']: subject for subject in subjects}
    if not subjects or len(subject_map) != len(subjects):
        raise ValueError('Declare each visible subject and its kind')
    for part in parts:
        if part.get('subject') not in subject_map or not part.get('role') or not part.get('stroke_groups'):
            raise ValueError('Each part needs a subject, semantic role and independently lifted stroke groups')
        if not isinstance(part['stroke_groups'], list) or not all(isinstance(group,str) and group.strip() for group in part['stroke_groups']):
            raise ValueError('Describe real strokes, not one whole-frame reveal')
        if part['role'] in ('whole', 'whole_frame', 'person', 'body') and subject_map[part['subject']].get('kind') == 'human':
            raise ValueError('A human figure cannot be a single semantic part')
    for subject in subjects:
        if subject.get('kind') not in ('human', 'animal', 'object', 'environment'):
            raise ValueError('Unknown subject kind')
        selected = [part for part in parts if part['subject'] == subject['id']]
        if not selected:
            raise ValueError('Every declared subject needs parts')
        if subject['kind'] == 'human':
            roles = [part['role'] for part in selected]
            omitted = subject.get('omitted_roles', {})
            if any(role not in roles and not omitted.get(role) for role in HUMAN_ORDER):
                raise ValueError('Human plan must account for head, neck, torso, left/right arms and lower body, including occlusion')
            indices = [HUMAN_ORDER.index(role) for role in roles if role in HUMAN_ORDER]
            if indices != sorted(indices) and not subject.get('order_exception'):
                raise ValueError('Human part order is head, neck, torso, left arm, right arm, lower body; explain any actual composition exception')
        elif len(selected) == 1 and subject['kind'] == 'animal':
            raise ValueError('Animals also need separate anatomical parts')
    if plan.get('spatial_order') != 'top_to_bottom_left_to_right' and not plan.get('order_exception'):
        raise ValueError('Use top-to-bottom, left-to-right order or explain the composition exception')
    return True


def validate_narrative_requirements(plan, review, narration):
    requirements = plan.get('narrative_requirements', [])
    if not requirements or len({item.get('id') for item in requirements}) != len(requirements):
        raise ValueError('Every production illustration needs distinct observable narrative requirements')
    checks = {item.get('id'): item for item in review.get('narrative_checks', [])}
    for requirement in requirements:
        quote = requirement.get('narration_quote', '')
        if not requirement.get('id') or not quote or quote not in narration or not requirement.get('observable'):
            raise ValueError('Narrative requirements must cite actual narration and state what must be visibly present')
        check = checks.get(requirement['id'], {})
        if check.get('status') != 'pass' or not check.get('evidence'):
            raise ValueError('An illustration has an unverified or failed narrative requirement: ' + requirement['id'])
    return len(requirements)


def preflight(job, plan_path):
    job, plan_path = Path(job).resolve(), Path(plan_path).resolve()
    style = verify_style(job)
    plan_document = json.loads(plan_path.read_text())
    plans = plan_document.get('illustrations', [])
    if not plans or len({plan['id'] for plan in plans}) != len(plans):
        raise ValueError('Drawing plans need unique illustration ids')
    for plan in plans:
        validate_plan(plan)
        requirements = plan.get('narrative_requirements', [])
        if not requirements or any(not all(item.get(key) for key in ('id','narration_quote','observable')) for item in requirements):
            raise ValueError('Define quoted narration and observable narrative requirements before generating the illustration')
    receipt = {'status': 'ready_for_generation', 'plan_sha256': digest(plan_path),
               'style_sha256': style['resolved_sha256'], 'illustrations': [plan['id'] for plan in plans]}
    path = plan_path.with_suffix('.preflight.json')
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    return receipt


def illustration_actions(manifest):
    for page in manifest['pages']:
        for group in [*page['beats'], *page.get('visual_groups', [])]:
            for action in group.get('actions', []):
                if action['type'] == 'illustration':
                    yield action


def verify_drawing_plans(job, manifest, style):
    reference = manifest.get('drawing_plan')
    if not reference:
        raise ValueError('A pre-generation drawing_plan is mandatory for every production job')
    path = Path(job) / reference
    document = json.loads(path.read_text())
    receipt = json.loads(path.with_suffix('.preflight.json').read_text())
    if receipt.get('status') != 'ready_for_generation' or receipt.get('plan_sha256') != digest(path) or receipt.get('style_sha256') != style['resolved_sha256']:
        raise ValueError('Drawing preflight is missing or stale; repair the plan before generating assets')
    plans = {plan['id']: plan for plan in document['illustrations']}
    for plan in plans.values():
        validate_plan(plan)
    reviews = json.loads((Path(job) / manifest['drawing_review']).read_text())
    if reviews.get('style_sha256') != style['resolved_sha256']:
        raise ValueError('Drawing review belongs to another resolved style')
    if reviews.get('plan_sha256') != digest(path):
        raise ValueError('Drawing review belongs to another plan')
    inspected = {entry['plan_id']: entry for entry in reviews.get('illustrations', [])}
    checked = 0
    narration = ''.join(beat['text'] for page in manifest['pages'] for beat in page['beats'])
    for action in illustration_actions(manifest):
        identity = action.get('drawing_plan_id')
        if identity not in plans:
            raise ValueError('Illustration has no pre-generation drawing plan')
        plan, review = plans[identity], inspected.get(identity, {})
        expected = [part['id'] for part in plan['parts']]
        actual = [part['id'] for part in action.get('parts', [])]
        if expected != actual:
            raise ValueError('Actual part masks must match the planned outline/fill order')
        source = Path(action['source'])
        source = source if source.is_absolute() else Path(job) / source
        if review.get('status') != 'pass' or review.get('source_sha256') != digest(source) or review.get('crop') != action.get('crop'):
            raise ValueError('Semantic drawing review is missing, failed, or belongs to another image/crop')
        for field in ('anatomy_and_occlusion', 'part_boundaries', 'stroke_breaks', 'outline_then_fill', 'spatial_order'):
            if not review.get(field):
                raise ValueError('Actual-image drawing review needs evidence for ' + field)
        validate_narrative_requirements(plan, review, narration)
        if plan['outline_strategy'] == 'explicit_mask' and not action.get('outline_mask'):
            raise ValueError('This style needs its planned aligned outline mask')
        if action.get('outline_mask'):
            mask_path = Path(job) / action['outline_mask']
            if review.get('outline_mask_sha256') != digest(mask_path):
                raise ValueError('Outline mask changed after semantic review')
            from PIL import Image
            with Image.open(source) as image, Image.open(mask_path) as mask:
                if image.size != mask.size:
                    raise ValueError('Outline mask must align with the complete source image before cropping')
        checked += 1
    return {'plan_sha256': digest(path), 'reviewed_illustrations': checked}


def validate_strokes(metadata):
    segments = metadata['segments']
    previous_ink = None
    for segment in segments:
        if segment['end'] <= segment['start']:
            raise ValueError('Every stroke and pen lift needs a positive duration')
        if segment['kind'] != 'ink':
            continue
        points = np.asarray(segment['points'], dtype=float)
        if len(points) < 2 or not np.isfinite(points).all() or (np.linalg.norm(np.diff(points, axis=0), axis=1) > 1.5).any():
            raise ValueError('A pen stroke bridges disconnected outline points; split and lift the pen')
        if previous_ink is not None and segment['start'] <= previous_ink['end'] + 1e-10:
            raise ValueError('Separate strokes require a pen-up interval, even at a shared endpoint')
        previous_ink = segment
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    parser.add_argument('plan', type=Path)
    arguments = parser.parse_args()
    print(json.dumps(preflight(arguments.job, arguments.plan), ensure_ascii=False))
