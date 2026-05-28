# AI-Assisted Curation Reference

Inspired by the SpikeAgent method, this is a guide for unit curation using AI visual analysis.

## Overview

AI-assisted curation leverages vision-language models to analyze spike sorting visualization results, providing quality assessments similar to those of human experts.

### Workflow

```
Traditional Method:  Metrics → Threshold → Labels
AI-Enhanced Method: Metrics → AI Visual Analysis → Confidence Score → Labels
```

## Claude Code Integration

When using this skill in Claude Code, Claude can directly analyze waveform plots without needing API configuration. Simply:

1. Generate unit reports or charts
2. Ask Claude to analyze the visualization
3. Claude will provide expert-level curation decisions

Example workflow in Claude Code:
```python
# Generate a chart for a unit
npa.plot_unit_summary(analyzer, unit_id=0, output='unit_0_summary.png')

# Then ask Claude: "Please analyze this unit's waveforms and autocorrelogram
# to determine if it's a well-isolated single unit, multi-unit activity, or noise"
```

Claude can evaluate:
- Waveform consistency and shape
- Refractory period violations in the autocorrelogram
- Amplitude stability over time
- Overall quality of unit isolation

## Quick Start

### Generate Unit Report

```python
import neuropixels_analysis as npa

# Create a visual report for a unit
report = npa.generate_unit_report(analyzer, unit_id=0, output_dir='reports/')

# The report includes:
# - Waveforms, Templates, Autocorrelogram
# - Amplitudes over time, ISI histogram
# - Quality metrics summary
# - Base64 encoded images for the API
```

### AI Visual Analysis

```python
from anthropic import Anthropic

# Set up API client
client = Anthropic()

# Analyze a single unit
result = npa.analyze_unit_visually(
    analyzer,
    unit_id=0,
    api_client=client,
    model='claude-opus-4.5',
    task='quality_assessment'
)

print(f"Classification: {result['classification']}")
print(f"Reasoning: {result['reasoning']}")
```

### Batch Analysis

```python
# Analyze all units
results = npa.batch_visual_curation(
    analyzer,
    api_client=client,
    output_dir='ai_curation/',
    progress_callback=lambda i, n: print(f"Progress: {i}/{n}")
)

# Get labels
ai_labels = {uid: r['classification'] for uid, r in results.items()}
```

## Interactive Curation Session

For human-in-the-loop curation with AI assistance:

```python
# Create session
session = npa.CurationSession.create(
    analyzer,
    output_dir='curation_session/',
    sort_by_confidence=True  # Prioritize showing uncertain units
)

# Process units
while True:
    unit = session.current_unit()
    if unit is None:
        break

    print(f"Unit {unit.unit_id}:")
    print(f"  Auto: {unit.auto_classification} (conf: {unit.confidence:.2f})")

    # Generate report
    report = npa.generate_unit_report(analyzer, unit.unit_id)

    # Get AI opinion
    ai_result = npa.analyze_unit_visually(analyzer, unit.unit_id, api_client=client)
    session.set_ai_classification(unit.unit_id, ai_result['classification'])

    # Human decision
    decision = input("Decision (good/mua/noise/skip): ")
    if decision != 'skip':
        session.set_decision(unit.unit_id, decision)

    session.next_unit()

# Export results
labels = session.get_final_labels()
session.export_decisions('final_curation.csv')
```

## Analysis Tasks

### Quality Assessment (Default)

Analyze waveform shape, refractory period, and amplitude stability.

```python
result = npa.analyze_unit_visually(analyzer, uid, task='quality_assessment')
# Returns: 'good', 'mua', or 'noise'
```

### Merge Candidate Detection

Determine if two units should be merged.

```python
result = npa.analyze_unit_visually(analyzer, uid, task='merge_candidate')
# Returns: 'merge' or 'keep_separate'
```

### Drift Assessment

Assess motion/drift in the recording.

```python
result = npa.analyze_unit_visually(analyzer, uid, task='drift_assessment')
# Returns drift magnitude and correction suggestions
```

## Custom Prompts

Create custom analysis prompts:

```python
from neuropixels_analysis.ai_curation import create_curation_prompt

# Get base prompt
prompt = create_curation_prompt(
    task='quality_assessment',
    additional_context='Focus on waveform amplitude consistency'
)

# Or fully customize
custom_prompt = """
Analyze this unit and determine if it represents a fast-spiking interneuron.

Look for:
1. Narrow waveform (peak-to-trough < 0.5ms)
2. High firing rate
3. Regular ISI distribution

Classify as: FSI (fast-spiking interneuron) or OTHER
"""

result = npa.analyze_unit_visually(
    analyzer, uid,
    api_client=client,
    custom_prompt=custom_prompt
)
```

## Combining AI with Metrics

Best practice: Use both AI and quantitative metrics.

```python
def hybrid_curation(analyzer, metrics, api_client):
    """Combine metrics and AI for robust curation."""
    labels = {}

    for unit_id in metrics.index:
        row = metrics.loc[unit_id]

        # Cases with high confidence based on metrics alone
        if row['snr'] > 10 and row['isi_violations_ratio'] < 0.001:
            labels[unit_id] = 'good'
            continue

        if row['snr'] < 1.5:
            labels[unit_id] = 'noise'
            continue

        # Uncertain cases: Use AI
        result = npa.analyze_unit_visually(
            analyzer, unit_id, api_client=api_client
        )
        labels[unit_id] = result['classification']

    return labels
```

## Session Management

### Resume Session

```python
# Resume an interrupted session
session = npa.CurationSession.load('curation_session/20250101_120000/')

# Check progress
summary = session.get_summary()
print(f"Progress: {summary['progress_pct']:.1f}%")
print(f"Remaining: {summary['remaining']} units")

# Continue from where you left off
unit = session.current_unit()
```

### Navigate Session

```python
# Jump to a specific unit
session.go_to_unit(42)

# Previous/Next
session.prev_unit()
session.next_unit()

# Update decision
session.set_decision(42, 'good', notes='Clear refractory period')
```

### Export Results

```python
# Get final labels (Priority: Human > AI > Auto)
labels = session.get_final_labels()

# Export detailed results
df = session.export_decisions('curation_results.csv')

# Summary
summary = session.get_summary()
print(f"Good: {summary['decisions'].get('good', 0)}")
print(f"MUA: {summary['decisions'].get('mua', 0)}")
print(f"Noise: {summary['decisions'].get('noise', 0)}")
```

## Visual Report Components

The generated report contains 6 panels:

| Panel | Content | Focus |
|-------|---------|------------------|
| Waveforms | Individual spike waveforms | Consistency, shape |
| Template | Mean ± SD | Clear negative peak, physiological shape |
| Autocorrelogram | Spike time intervals | Gap at 0ms (refractory period) |
| Amplitudes | Amplitude over time | Stability, no drift |
| ISI Histogram | Inter-spike intervals | Refractory period gap < 1.5ms |
| Metrics | Quality values | SNR, ISI violation rate, presence ratio |

## API Support

Currently supported APIs:

| Provider | Client | Model Example |
|----------|--------|----------------|
| Anthropic | `anthropic.Anthropic()` | claude-opus-4.5 |
| OpenAI | `openai.OpenAI()` | gpt-4-vision-preview |
| Google | `google.generativeai` | gemini-pro-vision |

### Anthropic Example

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")
result = npa.analyze_unit_visually(analyzer, uid, api_client=client)
```

### OpenAI Example

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")
result = npa.analyze_unit_visually(
    analyzer, uid,
    api_client=client,
    model='gpt-4-vision-preview'
)
```

## Best Practices

1. **Use AI for uncertain cases** - Don't waste API calls on obvious good/noise units.
2. **Combine with metrics** - AI should complement, not replace, quantitative measurements.
3. **Human supervision** - Review AI decisions, especially for critical analyses.
4. **Save sessions** - Always use `CurationSession` to track decisions.
5. **Record reasoning** - Use the notes field to record the basis for decisions.

## Cost Optimization

```python
# Use AI only for uncertain units
uncertain_units = metrics.query("""
    snr > 2 and snr < 8 and
    isi_violations_ratio > 0.001 and isi_violations_ratio < 0.1
""").index.tolist()

# Batch process only these units
results = npa.batch_visual_curation(
    analyzer,
    unit_ids=uncertain_units,
    api_client=client
)
```

## References

- [SpikeAgent](https://github.com/SpikeAgent/SpikeAgent) - AI-driven sorting assistant
- [Anthropic Vision API](https://docs.anthropic.com/en/docs/vision)
- [GPT-4 Vision](https://platform.openai.com/docs/guides/vision)