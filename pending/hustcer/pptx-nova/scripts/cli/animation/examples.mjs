#!/usr/bin/env node
// Reproducible two-slide examples, using only the public xdoc CLI and Node.
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

/** Right-exit position for a center-rotated rectangle with no visual effects. */
export function rightExitPosition({ slideWidth, x, y, w, h, rotation = 0, margin }) {
  for (const n of [slideWidth, x, y, w, h, rotation, margin]) assert.ok(Number.isFinite(n))
  assert.ok(slideWidth > 0 && w > 0 && h > 0 && margin > 0)
  const radians = (rotation * Math.PI) / 180
  const halfWidth = (Math.abs(w * Math.cos(radians)) + Math.abs(h * Math.sin(radians))) / 2
  return { x: Math.ceil(slideWidth + margin + halfWidth - w / 2), y }
}

function main(args) {
  if (args.includes('--help')) {
    console.log(
      'Usage: node <skill-root>/scripts/cli/animation/examples.mjs --example focus|kpi|exit --run-dir <new-directory> [--xdoc <executable>]',
    )
    return
  }
  const options = {}
  for (let i = 0; i < args.length; i += 2) {
    assert.ok(['--example', '--run-dir', '--xdoc'].includes(args[i]), `Unknown option: ${args[i]}`)
    assert.ok(args[i + 1] && !args[i + 1].startsWith('--'), `Missing value: ${args[i]}`)
    assert.equal(options[args[i]], undefined, `Duplicate option: ${args[i]}`)
    options[args[i]] = args[i + 1]
  }
  const example = options['--example']
  assert.ok(['focus', 'kpi', 'exit'].includes(example), 'Choose focus, kpi, or exit.')
  assert.ok(options['--run-dir'], '--run-dir is required.')
  const run = resolve(options['--run-dir'])
  mkdirSync(dirname(run), { recursive: true })
  mkdirSync(run) // A run is an audit record; never overwrite an existing one.
  const xdoc = options['--xdoc'] || 'xdoc'
  const file = (name) => resolve(run, name)
  const save = (name, value) =>
    writeFileSync(file(name), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' })
  function command(name, argv, report = true) {
    const stdout = execFileSync(xdoc, argv, {
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
      timeout: 60000,
    })
    writeFileSync(file(name), stdout, { flag: 'wx' })
    const result = JSON.parse(stdout)
    if (report) assert.equal(result.status, 'success', `${name}: command failed`)
    return result
  }
  function inspect(name, input) {
    return command(name, ['pptx', 'inspect', input, '--json'])
  }
  function apply(name, ops, input) {
    save(`${name}.patch.json`, { schemaVersion: 'pptx-patch/v1', ops })
    const output = file(name === 'edit' ? 'candidate.pptx' : `${name}.pptx`)
    const argv = [
      'pptx',
      'apply',
      '--patch',
      file(`${name}.patch.json`),
      '--output',
      output,
      '--json',
    ]
    if (input) argv.push('--input', input)
    command(`${name}.dry-run.json`, [...argv, '--dry-run', '--explain'])
    command(`${name}.apply.json`, argv)
    return output
  }
  const emu = (n) => `${Math.round(n)}emu`
  const shape = (slide, name) => {
    const matches = slide.shapes.filter((s) => s.name === name)
    assert.equal(matches.length, 1, `Expected one ${name} on slide ${slide.index}`)
    return matches[0]
  }
  writeFileSync(file('xdoc-version.txt'), execFileSync(xdoc, ['--version'], { encoding: 'utf8' }), {
    flag: 'wx',
  })
  command('schema-index.json', ['schema', '--mode', 'index', '--minimal'], false)
  const operations = [
    'add-slide',
    'add-shape',
    'add-text-box',
    'set-text-frame',
    'set-shape',
    'duplicate-slide',
    'set-slide-transition',
  ]
  const schema = command(
    'schema-ops.json',
    ['schema', '--mode', 'ops', '--ops', operations.join(','), '--minimal'],
    false,
  )
  for (const op of operations)
    assert.ok(
      schema.operations.some((o) => o.op === op),
      `Runtime does not disclose ${op}`,
    )
  const transition = schema.operations.find((o) => o.op === 'set-slide-transition').jsonSchema
  assert.ok(
    transition.$defs.transitionType.enum.includes('morph'),
    'Runtime does not disclose Morph.',
  )
  assert.ok(
    transition.$defs.morphMode.enum.includes('by-object'),
    'Runtime does not disclose by-object Morph.',
  )

  const actor = example === 'kpi' ? '!!actor-kpi' : '!!actor-product'
  const scene = '!!scene-surface'
  // Initialize the source, then read the runtime's actual slide size.
  const blank = apply('blank', [{ op: 'add-slide', layout: 'blank' }])
  const blankInfo = inspect('blank.inspect.json', blank)
  const width = Number(blankInfo.presentation.slideSize.wEmu)
  const height = Number(blankInfo.presentation.slideSize.hEmu)
  assert.ok(width > 0 && height > 0)
  const source = apply(
    'source',
    [
      {
        op: 'add-shape',
        slide: 0,
        kind: 'rectangle',
        name: scene,
        x: '0emu',
        y: '0emu',
        w: emu(width),
        h: emu(height),
      },
      {
        op: 'set-shape',
        slide: 0,
        shape: { name: scene },
        fill: { type: 'solid', color: '#F2F5F9' },
      },
      {
        op: 'add-text-box',
        slide: 0,
        name: 'caption',
        x: emu(width * 0.08),
        y: emu(height * 0.08),
        w: emu(width * 0.84),
        h: emu(height * 0.13),
        text: {
          focus: 'Follow the object',
          kpi: 'One metric, one focus',
          exit: 'A deliberate exit',
        }[example],
      },
      {
        op: 'set-text-frame',
        slide: 0,
        shape: { name: 'caption' },
        font: { name: 'Arial', size: '28pt', color: '#17324D' },
      },
      {
        op: 'add-text-box',
        slide: 0,
        name: actor,
        x: emu(width * 0.12),
        y: emu(height * 0.36),
        w: emu(width * 0.25),
        h: emu(height * 0.22),
        text: example === 'kpi' ? '42%' : 'Product',
      },
      {
        op: 'set-shape',
        slide: 0,
        shape: { name: actor },
        fill: { type: 'solid', color: '#2864D7' },
        rotation: example === 'exit' ? 18 : 0,
      },
      {
        op: 'set-text-frame',
        slide: 0,
        shape: { name: actor },
        font: { name: 'Arial', size: example === 'kpi' ? '36pt' : '26pt', color: '#FFFFFF' },
        frame: { verticalAnchor: 'middle' },
      },
    ],
    blank,
  )
  const sourceInfo = inspect('source.inspect.json', source)
  const copied = apply('copy', [{ op: 'duplicate-slide', slide: 0 }], source)
  const copyInfo = inspect('copy.inspect.json', copied)
  const sourceParts = new Set(sourceInfo.slides.map((s) => s.partName))
  const added = copyInfo.slides.filter((s) => !sourceParts.has(s.partName))
  assert.equal(added.length, 1, 'Expected exactly one new slide part.')
  const destination = added[0]
  const sourceSlide = copyInfo.slides.find((s) => s.partName === sourceInfo.slides[0].partName)
  assert.equal(destination.index, sourceSlide.index + 1, 'Morph pair must be adjacent.')
  const target = shape(destination, actor)
  assert.ok(shape(sourceSlide, actor))
  assert.ok(shape(destination, scene))
  const bounds = target.bbox
  let position
  let size
  if (example === 'exit') {
    position = rightExitPosition({
      slideWidth: width,
      x: Number(bounds.xEmu),
      y: Number(bounds.yEmu),
      w: Number(bounds.wEmu),
      h: Number(bounds.hEmu),
      rotation: 18,
      margin: width * 0.02,
    })
  } else {
    const factor = example === 'kpi' ? 1.75 : 1.2
    size = { w: Number(bounds.wEmu) * factor, h: Number(bounds.hEmu) * factor }
    position = { x: width / 2 - size.w / 2, y: height * 0.52 - size.h / 2 }
  }
  const duration = example === 'exit' ? 650 : 850
  const edits = [
    {
      op: 'set-shape',
      slide: destination.index,
      shape: { id: target.id },
      position: { x: emu(position.x), y: emu(position.y) },
      ...(size ? { size: { w: emu(size.w), h: emu(size.h) } } : {}),
    },
  ]
  if (example === 'kpi')
    edits.push({
      op: 'set-text-frame',
      slide: destination.index,
      shape: { id: target.id },
      font: { size: '63pt' },
    })
  edits.push({
    op: 'set-slide-transition',
    slide: destination.index,
    kind: 'morph',
    morphMode: 'by-object',
    duration,
  })
  const candidate = apply('edit', edits, copied)
  const final = inspect('candidate.inspect.json', candidate)
  const actualBounds = shape(final.slides[destination.index], actor).bbox
  const expectedBounds = {
    xEmu: position.x,
    yEmu: position.y,
    wEmu: size?.w ?? Number(bounds.wEmu),
    hEmu: size?.h ?? Number(bounds.hEmu),
  }
  for (const [key, value] of Object.entries(expectedBounds)) {
    assert.equal(
      Number(actualBounds[key]),
      Math.round(value),
      `Actor ${key} did not match the intended endpoint.`,
    )
  }
  const check = command('morph-check.json', [
    'pptx',
    'morph-check',
    candidate,
    '--from-slide',
    String(sourceSlide.index + 1),
    '--to-slide',
    String(destination.index + 1),
    '--json',
  ])
  assert.equal(check.pairs.length, 1)
  const pair = check.pairs[0]
  assert.deepEqual(pair.matched.map((m) => m.name).sort(), [scene, actor].sort())
  assert.equal(pair.matched.find((m) => m.name === actor).geometryChanged, true)
  assert.equal(pair.matched.find((m) => m.name === scene).geometryChanged, false)
  const expectedFinding = (f) =>
    f.code === 'morph_pair_no_visible_change' && f.name === scene && f.severity === 'info'
  assert.ok(
    pair.findings.every(expectedFinding),
    'Unexpected Morph findings; inspect morph-check.json.',
  )
  const targetTransition = final.slides[destination.index].transition
  assert.equal(targetTransition.kind, 'morph')
  assert.equal(targetTransition.morphMode, 'by-object')
  assert.equal(targetTransition.durationMs, duration)
  assert.equal(targetTransition.extensionWrapped, true)
  assert.equal(targetTransition.fallbackKind, 'fade')
  save('evidence-summary.json', {
    status: 'passed',
    example,
    candidate: 'candidate.pptx',
    expectedNames: [scene, actor],
    fromSlideIndex: sourceSlide.index,
    toSlideIndex: destination.index,
    durationMs: duration,
    findings: pair.findings,
    checks: [
      'dry-run/apply',
      'copy target rediscovery',
      'inspect transition',
      'explicit pairs',
      'actor endpoint matches intended geometry',
      'static scene retained',
    ],
    powerPoint: { cleanOpen: 'not-run', playback: 'not-run' },
    staticLayout: 'not-reviewed',
  })
  console.log(JSON.stringify({ status: 'passed', example, runDir: run, candidate }, null, 2))
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main(process.argv.slice(2))
  } catch (error) {
    console.error(error.message)
    process.exitCode = 1
  }
}
