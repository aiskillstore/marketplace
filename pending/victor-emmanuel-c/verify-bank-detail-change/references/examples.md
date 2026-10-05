# Bank-detail examples

Public test accounts, fictional supplier; requests and conditional expectations,
not captured live output. Do not use these accounts for a real transfer.
An agent makes these checks only as native MCP tool calls. Each curl block is
this package's build check for maintainers, never run by an agent, and no
Expected line is a result for anyone's request.

## Scenario 1: Claimed change, then a different draft account

Input: "IBAN gewijzigd volgens de mail. Onze administratie én de eerste mail
noemen BE68 5390 0754 7034. Een tweede concept noemt BE71096123456769.
Vergelijk beide apart voor onze Belgische testleverancier en verander niets."

```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"check_payment_change","arguments":{"newIban":"BE68 5390 0754 7034","ibanOnFile":"BE68539007547034","supplierCountry":"BE"}}}'
```
```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_payment_change","arguments":{"newIban":"BE71096123456769","ibanOnFile":"BE68539007547034","supplierCountry":"BE"}}}'
```
```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"verify_iban","arguments":{"iban":"BE71096123456769","expectedCountry":"BE"}}}'
```

Expected: matching normalized accounts should return no_change; the different
account should require verify_first. Read actual flags and check results.
Limits: no_change does not explain the contradictory email. Callback uses a
number from one's own administration. Structure/checksum is not ownership.

## Scenario 2: Broken checksum and a foreign-account alternative

Input: "Please check two drafts separately: BE68 5390 0754 7035 and
DE89370400440532013000; the Belgian supplier is on file as BE68539007547034.
Do not update the account or pay."

```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"check_payment_change","arguments":{"newIban":"BE68 5390 0754 7035","ibanOnFile":"BE68539007547034","supplierCountry":"BE"}}}'
```
```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"verify_iban","arguments":{"iban":"BE68 5390 0754 7035","expectedCountry":"BE"}}}'
```
```bash
curl -s https://jithox.com/api/mcp \
  -A 'verify-bank-detail-change/1.0' \
  -H 'x-jithox-probe: gebruik1-build' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"check_payment_change","arguments":{"newIban":"DE89370400440532013000","ibanOnFile":"BE68539007547034","supplierCountry":"BE"}}}'
```

Expected: the bad checksum should produce invalid_new_account and a failed
structure check: workflow stop. A country mismatch should produce stop; preserve
actual flags rather than inventing fraud. If the service fails, report unknown.
Limits: stop is not proof of fraud; correct/confirm independently. No record changes,
no payment, and no response is never a pass.
