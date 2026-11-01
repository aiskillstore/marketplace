# CPU data sources

Snapshot checked: **2026-11-01**. Source-listed models are not independently verified release or availability claims.

## Inventory

The following Wikipedia pages and their contributors are the source of the normalized Intel/AMD model inventory. Wikipedia text is available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); page histories linked from each article identify its contributors.

- [List of Intel Core desktop processors](https://en.wikipedia.org/wiki/List_of_Intel_Core_desktop_processors)
- [List of Intel Core mobile processors](https://en.wikipedia.org/wiki/List_of_Intel_Core_mobile_processors)
- [List of Intel Core embedded processors](https://en.wikipedia.org/wiki/List_of_Intel_Core_embedded_processors)
- [List of Intel processors](https://en.wikipedia.org/wiki/List_of_Intel_processors)
- [List of AMD Ryzen processors](https://en.wikipedia.org/wiki/List_of_AMD_Ryzen_processors)
- [EPYC](https://en.wikipedia.org/wiki/Epyc)
- [List of AMD Athlon processors](https://en.wikipedia.org/wiki/List_of_AMD_Athlon_processors)

Transformations: selected the requested generations/families, removed footnotes and prices, expanded merged cells and optional PRO variants, normalized names, added stable IDs and classification fields, deduplicated model names, and marked missing scores. `cpu_catalog.json` and generated catalog tables are distributed under CC BY-SA 4.0. This data license is separate from the repository's MIT code license.

Additional factual inventory sources:

- [CPU-Monkey Apple M series](https://www.cpu-monkey.com/en/cpu_family-apple_m_series): source-listed chip/core configurations.
- [Geekbench Mac benchmark chart](https://browser.geekbench.com/mac-benchmarks): model names, CPU descriptions and configuration-specific detail URLs. **Scores from this chart are not imported**, because the chart and some details have conflicting Geekbench 6/7 labels.
- CPU-Monkey product pages linked by individual supplementary records.

## Benchmark references

- [CPU-Monkey Geekbench 6 Single-Core](https://www.cpu-monkey.com/en/cpu_benchmark-geekbench_6_single_core)
- [CPU-Monkey Geekbench 6 Multi-Core](https://www.cpu-monkey.com/en/cpu_benchmark-geekbench_6_multi_core)
- Earlier x86 comparison-page references may be retained when no refreshed pair is available; their original `source_url` and date remain attached.

The score table stores factual numbers with product and chart URLs, an explicit benchmark version, and a verification date. These are public reference values, not official averages, project-run measurements or warranties of performance. Geekbench 6 and 7 values are never mixed. Missing data remains missing. A mapped Mac uses a labeled CPU reference, not a score copied from its version-conflicting Mac chart.

The scope, import format and refresh procedure are documented in the repository's `docs/cpu-data.md`.
