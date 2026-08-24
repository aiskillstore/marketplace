# OT Data Source Operations

Use stable server and operation names. The host may wrap them in a namespace; never copy the wrapper into the workbook.

## 1. Request pacing

Serialize credentialed federal API calls and leave at least three seconds between them, including capability checks. Do not parallelize keyed BLS or Per Diem calls. Honor a longer provider retry interval. Stop and report a rate limit instead of rapidly retrying. Use reasonable pacing for unkeyed services too.

## 2. SOC mapping

Classify the work before selecting a code. Record ambiguous mappings and alternatives queried.

| OT role | Common SOC | BLS title |
|---|---|---|
| IT Program Manager | 11-3021 | Computer and Information Systems Managers |
| Engineering or R&D Manager | 11-9041 | Architectural and Engineering Managers |
| Project Manager | 13-1082 | Project Management Specialists |
| Management Analyst | 13-1111 | Management Analysts |
| Computer Systems Analyst | 15-1211 | Computer Systems Analysts |
| Information Security Analyst | 15-1212 | Information Security Analysts |
| Software Developer | 15-1252 | Software Developers |
| Software QA Analyst or Tester | 15-1253 | Software Quality Assurance Analysts and Testers |
| Data Scientist | 15-2051 | Data Scientists |
| Aerospace Engineer | 17-2011 | Aerospace Engineers |
| Electrical Engineer | 17-2071 | Electrical Engineers |
| Electronics Engineer | 17-2072 | Electronics Engineers, Except Computer |
| Industrial Engineer | 17-2112 | Industrial Engineers |
| Mechanical Engineer | 17-2141 | Mechanical Engineers |
| Multidiscipline physical Systems Engineer | 17-2199 | Engineers, All Other |
| Physicist | 19-2012 | Physicists |
| Chemist | 19-2031 | Chemists |
| Materials Scientist | 19-2032 | Materials Scientists |
| Technical Writer | 27-3042 | Technical Writers |
| Engineering Technician, other | 17-3029 | Engineering Technologists and Technicians, Except Drafters, All Other |

Use 11-1021 for operations management, 11-3021 for IT management, and 11-9041 for physical engineering management unless better evidence supports another code. Do not map every Program Manager to the same SOC.

Robotics, autonomy, artificial intelligence, directed energy, quantum, hypersonics, and similar labels often span disciplines. Price the actual work through supported roles rather than using a fictional specialty SOC. Label every proxy.

## 3. BLS OEWS

### Runtime vintage

Call `detect_latest_year` before wage retrieval. Record the returned year and use it in the Summary, Labor Benchmarking, Methodology, Raw Data, and aging formula. A baseline written in the skill never overrides the runtime result.

### Wage retrieval

Call:

```text
get_wage_data(
  occ_code=<six-character SOC>,
  scope=<metro|state|national>,
  area_code=<MSA or state FIPS>,
  datatypes=["04", "11", "12", "13", "14", "15"]
)
```

The requested data types provide mean plus P10, P25, P50, P75, and P90. Do not send unsupported data types.

Fallback ladder:

1. Metro
2. State, only after the current metro code and series are checked
3. National

Use `list_common_metros` and other server lookup operations to resolve codes. Record every fallback and reason.

When BLS lacks job levels, use a disclosed percentile convention. If no levels are supplied, use P50 and do not invent a junior, mid, and senior mix. Treat any capped percentile as a lower bound after confirming the current reporting cap from the returned data or BLS release metadata.

Keep every performer and location separate. Do not average unlike MSAs unless the user supplies an allocation and approves a weighted calculation.

## 4. CALC+

### Silent-wrong-answer signature

The keyword route is:

```text
/v3/api/ceilingrates/?keyword=<term>
```

Use `keyword=`. Never use `q=`. The wrong parameter may be accepted while returning an unfiltered corpus.

Discovery buckets are found at:

```text
aggregations.labor_category.buckets[*].key
aggregations.labor_category.buckets[*].doc_count
```

### Discovery-first flow

1. Call `suggest_contains(field="labor_category", term=<term>)`.
2. When exact buckets form a usable pool, call `exact_search(field="labor_category", value=<bucket>)`.
3. When buckets are fragmented, call `keyword_search(keyword=<term>)` and disclose that other fields may match.
4. Call `igce_benchmark` or the current equivalent for compact percentiles and sample size.
5. Use `page_size=1` when an operation requires a page size for aggregation retrieval. Never send zero.

For senior roles, keep title-match and experience-match pools separate. Label a small pool as directional. When results are absent, try one broader supported term and then record `No CALC+ data; BLS and other supplied sources only.` Do not invent a defense specialty premium.

CALC+ contains awarded ceiling rates from another market and contract context. It is positioning evidence, not a binding OT rate or a conclusion.

## 5. GSA Per Diem

For one or more nights, call:

```text
estimate_travel_cost(
  city=<civilian locality>,
  state=<state>,
  num_nights=<integer>,
  travel_month=<optional month>,
  fiscal_year=<optional FY>
)
```

Use the returned first/last-day M&IE treatment once. Do not apply 75 percent a second time.

For a day trip, do not pass zero nights to an operation that requires at least one. Use `lookup_city_perdiem`, apply the returned first/last-day M&IE once, and keep lodging at zero.

Translate a military installation or laboratory to the correct civilian GSA locality and record the crosswalk. Verify the returned county when locality boundaries matter.

If the requested fiscal year is not published, retry the most recent available year once, record both years, and flag the data for refresh. Do not silently query a different year.

GSA Per Diem covers CONUS travel. Use OCONUS rates only from a user-supplied approved source.

## 6. Raw-data record

Record compact reproducible fields, not full payloads:

- BLS operation, SOC, scope, area, data types, returned vintage, selected percentile, and fallback
- CALC+ operation, exact bucket or keyword, count, percentiles, query date, and pool limitation
- Per Diem locality, fiscal year, month, nights, lodging, M&IE, and fallback
- Every proxy, derivation, user override, and source date

Do not write API keys, access tokens, user paths, host-generated tool names, or internal prompt text to the workbook.
