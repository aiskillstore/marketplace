# LLM Prompts

## 1. Funnel Plot Description
**Role**: System
**Task**: Describe the funnel plot based on title, outcome name, and statistics.
**Constraint**: Output 300+ words in {{language}}.

## 2. Egger's Test Table
**Role**: Clinical Medical Expert
**Task**: Generate a Markdown table for Egger's test based on statistics.
**Fields**: Effect Size (beta), Standard Error (se.beta), Intercept, Standard Error (se.intercept), Statistic (t-value), Significance (p-value), Degrees of Freedom (df).
**Constraint**: Output ONLY the table wrapped in curly braces `{}`.

## 3. Begg's Test Table
**Role**: Clinical Medical Expert
**Task**: Generate a Markdown table for Begg's test.
**Fields**: Kendall’s score, Standard Error, Statistic (z-value), Significance (p-value).
**Constraint**: Output ONLY the table wrapped in curly braces `{}`.

## 4. Trim and Fill Table
**Role**: Clinical Medical Expert
**Task**: Generate a Markdown table for Trim and Fill method.
**Constraint**: Output ONLY the table wrapped in curly braces `{}`.
