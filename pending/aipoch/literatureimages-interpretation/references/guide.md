# Literature Image Interpretation Reference Checklist

## Input Checklist

- Caption text
- Relevant body text descriptions
- Image files (usually located in the `*-images` folder with the same name as the literature)

## Output Checklist

- Figure/Chart interpretation descriptions
- Key trends and comparative conclusions
- Uncertainty prompts

## Output Format

- First organize an image list to filter out non-chart images; do not generate an image list file, the final output only retains image interpretations.
- Must examine all images in the `*-images` folder one by one; do not skip.
- Only interpret images identified as charts/diagrams/flowcharts/tables.
- Interpretation must be based on the image content itself, not just on captions or body text descriptions.
- Each interpretation includes three parts: variables, trends, and conclusions.
- Output as a UTF-8 encoded Markdown document.
- Do not generate or output an image list file.

## Quality Check

- Correct identification of image types (text blocks are not interpreted as charts).
- Descriptions are consistent with the actual trends in the charts.
- Accurate interpretation of significance and error bars.
- Retain only one `*-figure-interpretation.md` output.

## Common Issues

- Failure to distinguish between body text blocks and charts first.
- Ignoring statistical markers or units.
- Over-inferring conclusions beyond the figures.