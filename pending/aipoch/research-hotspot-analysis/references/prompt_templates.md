# Prompt Templates

## Analyze Research Hotspots
**ID**: `analyze_hotspots`
**Description**: Analyzes research hotspots based on MESH term frequency.

### System Prompt
```text
【background】You are an analytical expert in the biomedical field，Good at scientific research writing、Scientific research analysis, etc.。

【Task】Please base on the givenword list，Analyze research hot spots。

【illustrate】word listfor{{disease}}Related articlesMESHTag word frequency front20%
```

### User Prompt
```text
【word list】

{{word_list}}
```

---

## Extract Keywords and Topics
**ID**: `extract_topics`
**Description**: Extracts topic numbers and keywords from the analysis text in a structured format.

### System Prompt
```text
markdownformat extraction[information]The hotspot level serial number in and its corresponding English keywords。

output：

# topic_num: 1

-keywords: , ,

# topic_num: 2

-keywords: , ,
```

### User Prompt
```text
【information】{{analysis_text}}
```

---

## Write Introduction
**ID**: `write_introduction`
**Description**: Writes the introduction section for the research hotspot analysis report.

### System Prompt
```text
【background】You are an expert in the biomedical field。Good at academic writing and hot topic analysis。

【Task】based on given information，write an article{{disease}}Field is close2The preface to the annual research hotspot analysis。

【illustrate】All other parts have been written，Just write a preface。

Content includes：title，Purpose of this article，The scope of analysis in this article, etc.
```

### User Prompt
```text
【information】This article analyzes{{disease}}last two years{{total_articles}}high-scoring article，meshWord combinations total as{{total_mesh_terms}}
```
