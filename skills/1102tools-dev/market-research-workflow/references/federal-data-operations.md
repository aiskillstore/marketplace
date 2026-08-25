# Federal data operations

Inspect the installed schemas at runtime. Names below are semantic operations, not generated host prefixes.

## USASpending

Use as needed:

- award search and award count for comparable awards;
- award detail and transactions for amount history and deobligations;
- spending over time for fiscal-year trends;
- spending by recipient, agency, NAICS, PSC, or other available category;
- recipient search and profiles for entity resolution;
- subaward search with explicit coverage limitations;
- agency profiles and geography operations when relevant.

Do not treat a top-value award sample as a population. Current award amount, potential ceiling, obligations, transactions, and subawards are different measures.

## SAM.gov

Use only when the research plan requires:

- entity lookup and search;
- opportunity search and notice details;
- public contract award references;
- registration, exclusion, certification, organization, or responsibility-related public evidence.

Registration does not establish capability or responsibility. An active opportunity flag does not establish that the response deadline remains open.

## Capability failure

If a required server, operation, credential, or schema is missing, report the exact capability and affected research question. Offer a narrower product and obtain approval. Do not call the upstream API directly.

Agent configurations pin `sam-gov-mcp==1.0.9` and `usaspending-gov-mcp==1.0.4` with an explicit three-second pacing safeguard. USASpending uses the `acquisition-agent` tool profile in packaged agents while the standalone server retains its complete tool catalog.
