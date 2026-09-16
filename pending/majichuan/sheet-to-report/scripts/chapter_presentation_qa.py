"""Read-only final OOXML checks against the independently bound source projection."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from chapter_presentation import validate_projection

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def normalized(value):
    return re.sub(r"\s+", "", str(value))


def numbers(parent, xpath):
    points = parent.findall(xpath + "/c:numRef/c:numCache/c:pt", NS)
    if not points:
        points = parent.findall(xpath + "/c:numLit/c:pt", NS)
    return [float(p.find("c:v", NS).text) for p in sorted(points, key=lambda p: int(p.attrib["idx"]))]


def close_values(actual, expected):
    return len(actual) == len(expected) and all(
        a is not None and b is not None and math.isclose(a, b, rel_tol=1e-13, abs_tol=1e-10)
        for a, b in zip(actual, expected))


def strings(parent, xpath):
    points = parent.findall(xpath + '/c:strRef/c:strCache/c:pt', NS)
    if not points:
        points = parent.findall(xpath + '/c:strLit/c:pt', NS)
    return [normalized(p.find('c:v', NS).text or '') for p in
            sorted(points, key=lambda p: int(p.attrib['idx']))]


def inspect(path: Path, deck: dict, model: dict, selection: dict, scene: dict | None = None,
            sample_pages: list[int] | None = None, story: dict | None = None,
            review_pages: list[str] | None = None) -> dict:
    validate_projection(deck, model, selection, story)
    slides = deck['slides']
    if sample_pages is None and review_pages is None and scene and scene.get('purpose') in {'design-sample','design-review'}:
        raise ValueError('A design sample/review cannot be accepted as a full deck')
    if review_pages is not None:
        ids=[s['id'] for s in slides]
        if (sample_pages is not None or not review_pages or len(set(review_pages))!=len(review_pages)
            or any(p not in ids for p in review_pages)):
            raise ValueError('Design review needs unique bound source page IDs, separate from theme samples')
        indices=[ids.index(p) for p in review_pages]
        if indices!=sorted(indices):raise ValueError('Design review must preserve source order')
        if (not scene or scene.get('source')!=deck['sha256'] or scene.get('purpose')!='design-review'
            or scene.get('page_indices')!=indices):raise ValueError('Design review source mapping mismatch')
        slides=[slides[i] for i in indices]
    if sample_pages is not None:
        if (len(sample_pages) != 2 or any(type(p) is not int or not 1 <= p <= len(slides) for p in sample_pages)
                or slides[sample_pages[0]-1]['kind'] != 'cover'
                or slides[sample_pages[1]-1]['kind'] != 'chart'):
            raise ValueError('Sample must select a source cover and a source chart')
        indices = [p-1 for p in sample_pages]
        if (not scene or scene.get('source') != deck['sha256'] or scene.get('purpose') != 'design-sample'
                or scene.get('page_indices') != indices):
            raise ValueError('Sample page mapping missing or mismatched')
        slides = [slides[i] for i in indices]
    errors, chart_count, value_checks, text_checks = [], 0, 0, 0
    geometry_checks = 0
    if selection['target'] == 'slideviber' and (not scene or scene.get('source') != deck['sha256']):
        errors.append('SlideViber requires a source-bound scene for geometry verification')
    with ZipFile(path) as archive:
        names = archive.namelist()
        pages = sorted([n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)],
                       key=lambda n: int(re.search(r"slide(\d+)", n)[1]))
        if len(pages) != len(slides):
            errors.append("slide count differs from projection")
        for index, (name, slide) in enumerate(zip(pages, slides), 1):
            root = ET.fromstring(archive.read(name))
            if scene and (selection['target']=='slideviber' or deck['chart_views'].get(slide['chart_id'],{}).get('kind')=='waterfall'):
                from chapter_vector_qa import inspect_vector
                vector_errors, count = inspect_vector(root, deck['chart_views'].get(slide['chart_id']),
                    selection['config']['palette']['chart'], scene['scene'][index-1],scene.get('vector_line_mode'),scale=1.5 if selection['target']=='slideviber' else 1)
                errors.extend(f'slide {index}: {e}' for e in vector_errors)
                geometry_checks += count
            # Only audience-visible shape text, never notes or hidden alt labels.
            text = normalized("".join(t.text or "" for t in root.findall(".//a:t", NS)))
            required = [slide["title"], *[b["text"] for b in slide["blocks"]]]
            if deck['chart_views'].get(slide['chart_id'],{}).get('kind')=='scatter':
                required.extend(f'{i+1} {label}' for i,label in enumerate(deck['chart_views'][slide['chart_id']]['labels']))
            composition = scene['compositions'][index-1] if scene and scene.get('compositions') else {}
            if composition.get('source_fragments'):
                action = slide.get('visual',{}).get('action_layout')
                expected = ([{'block_index':action['block_index'],'texts':[p['text'] for p in action['parts']]}]
                            if action else None)
                if composition['source_fragments'] != expected:
                    errors.append(f'slide {index}: unbound content fragmentation')
                else:
                    for fragment in expected:
                        original=slide['blocks'][fragment['block_index']]['text']
                        if ''.join(fragment['texts']) != original:
                            errors.append(f'slide {index}: fragmented source content lost or reordered')
                        else:
                            required.remove(original)
                            required.extend(fragment['texts'])
                    required.extend(p['label'] for p in action['parts'])
            if slide['kind'] != 'cover':
                required += [slide['navigation']['eyebrow'], slide['navigation']['phase'],
                             f"{deck['slides'].index(slide)+1:02d} / {len(deck['slides'])}"]
            if slide['kind'] == 'overview':
                required += [slide['period'], *[b['label'] for b in slide['blocks']]]
            if slide['kind'] == 'summary':
                required.extend(b['label'] for b in slide['blocks'] if b['label'] not in {'判断', '判断（续）'})
            if scene and scene.get('compositions') and scene['compositions'][index-1].get('layout') in {'chart-with-bound-labels','chart-with-bound-comparison'}:
                view=deck['chart_views'][slide['chart_id']]
                for i in slide['visual']['focus_indices']:
                    required.append(view['labels'][i])
                    for series in view['series']:
                        value=f"{series['values'][i]:,.2f}".rstrip('0').rstrip('.')
                        required.extend([series['label'],value+series['unit']])
            if selection['target'] == 'slideviber' and scene and scene.get('compositions'):
                composition = scene['compositions'][index-1]
                context_id = composition.get('contextSource')
                if context_id:
                    context = next((s for s in deck['slides'] if s['id'] == context_id), None)
                    if (not context or context['kind'] != 'chapter' or context['owner'] != slide['owner']
                            or not set(context['evidence_ids']).intersection(slide['evidence_ids'])):
                        errors.append(f'slide {index}: unbound judgement sidebar')
                    else:
                        block_index=composition.get('contextBlockIndex',0)
                        if type(block_index) is not int or not 0<=block_index<len(context['blocks']):
                            errors.append(f'slide {index}: invalid sidebar block index')
                        else:
                            required.append(context['blocks'][block_index]['text'])
            for item in required:
                text_checks += 1
                if normalized(item) not in text:
                    errors.append(f"slide {index}: missing bound visible text: {item[:50]}")
            relname = str(PurePosixPath(name).parent / "_rels" / (PurePosixPath(name).name + ".rels"))
            rels = ET.fromstring(archive.read(relname)) if relname in names else []
            relation = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
            parts = []
            for element in root.findall(".//c:chart", NS):
                target = relation[element.attrib[f"{{{NS['r']}}}id"]]
                import posixpath
                part = (posixpath.normpath(target).lstrip("/") if target.startswith("/")
                        else posixpath.normpath(posixpath.join(str(PurePosixPath(name).parent), target)))
                if part.startswith("../") or part not in names:
                    raise ValueError(f"Invalid package chart relationship: {target}")
                parts.append(ET.fromstring(archive.read(part)))
            chart_count += len(parts)
            if not slide["chart_id"]:
                if parts:
                    errors.append(f"slide {index}: unexpected chart")
                continue
            view = deck["chart_views"][slide["chart_id"]]
            if selection["target"] == "slideviber":
                if parts:
                    errors.append(f"slide {index}: vector output unexpectedly contains native chart")
                continue  # Vector geometry is verified from the shared scene separately.
            if view["kind"] == "waterfall":
                if parts:
                    errors.append(f"slide {index}: waterfall native chart not declared")
                continue
            expected_count = 2 if view["kind"] == "paired" else 1
            if len(parts) != expected_count:
                errors.append(f"slide {index}: expected {expected_count} native chart(s)")
                continue
            for part_index, chart in enumerate(parts):
                from chapter_chart_qa import native_semantics
                errors.extend(f'slide {index}: {e}' for e in native_semantics(chart,view,part_index if expected_count==2 else None))
                source_series = [view["series"][part_index]] if expected_count == 2 else view["series"]
                actual_series = chart.findall(".//c:ser", NS)
                if len(actual_series) != len(source_series):
                    errors.append(f"slide {index}: series count mismatch")
                    continue
                for actual, expected in zip(actual_series, source_series):
                    label = strings(actual, 'c:tx')
                    if not label:
                        label = [normalized(actual.findtext('c:tx/c:v', '', NS))]
                    if label != [normalized(expected['label'])]:
                        errors.append(f'slide {index}: series name differs')
                    observed = numbers(actual, "c:val") or numbers(actual, "c:yVal")
                    values = expected["values"]
                    horizontal = view["kind"] in {"bar", "paired"}
                    if horizontal:
                        values = list(reversed(values))
                    categories = strings(actual, 'c:cat')
                    if not numbers(actual, 'c:xVal'):
                        expected_labels = list(reversed(view['labels'])) if horizontal else view['labels']
                        if view['kind']=='histogram':
                            fmt=lambda v:format(v,',.2f').rstrip('0').rstrip('.') if not float(v).is_integer() else format(v,',.0f')
                            expected_labels=[f"[{fmt(a)}, {fmt(b)}"+(']' if i==len(view['labels'])-1 else ')') for i,(a,b) in enumerate(zip(view['bin_lower'],view['bin_upper']))]
                        if categories != [normalized(v) for v in expected_labels]:
                            errors.append(f'slide {index}: categories differ or reordered')
                    if not close_values(observed, values):
                        errors.append(f"slide {index}: native numeric values differ")
                    value_checks += len(values)
                    x_values = numbers(actual, "c:xVal")
                    if x_values:
                        expected_x = view["x_values"]
                        if view["axes"]["x"]["scale"] == "time":
                            expected_x = [v / 86400000 + 25569 for v in expected_x]
                        if not close_values(x_values, expected_x):
                            errors.append(f"slide {index}: numeric x coordinates differ")
                        value_checks += len(expected_x)
        rasters = [n for n in names if n.startswith("ppt/media/") and n.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        if rasters:
            errors.append("unexpected raster images in evidence deck")
    return {"passed": not errors, "errors": errors, "slides": len(pages), "native_charts": chart_count,
            "numeric_cells_checked": value_checks, "visible_text_checks": text_checks,
            "vector_geometry_checks": geometry_checks,
            "raster_images": len(rasters), "source_model_sha256": model["sha256"],
            "projection_sha256": deck["sha256"], "visual": "separate_review_required",
            "native_application": "not_verified", "purpose": "design-review" if review_pages else "design-sample" if sample_pages else "full-deck",
            "sample_pages": sample_pages, "review_pages":review_pages}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ["model", "selection", "projection", "pptx", "output"]:
        parser.add_argument("--" + field, required=True, type=Path)
    parser.add_argument('--scene', type=Path)
    parser.add_argument('--story',type=Path)
    parser.add_argument('--sample-pages', help='Explicit two-page design sample, e.g. 1,6; never full-deck acceptance')
    parser.add_argument('--review-pages',help='Explicit source page IDs for design review; never full-deck acceptance')
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    result = inspect(args.pptx, read(args.projection), read(args.model), read(args.selection),
                     read(args.scene) if args.scene else None,
                     [int(p) for p in args.sample_pages.split(',')] if args.sample_pages else None,
                     read(args.story) if args.story else None,
                     args.review_pages.split(',') if args.review_pages else None)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
