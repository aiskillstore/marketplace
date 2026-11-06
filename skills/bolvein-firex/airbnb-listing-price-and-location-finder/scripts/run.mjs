// Minimal runner: node scripts/run.mjs [input.json | '{"json": "input"}']
// Needs Node 18+ and APIFY_TOKEN. Without an argument it uses references/example-input.json.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const token = process.env.APIFY_TOKEN;
if (!token) {
  console.error('Set APIFY_TOKEN');
  process.exit(1);
}
const actorId = process.env.ACTOR_ID || "nimbryxo-studio~airbnb-listing-price-and-location-finder";
const here = path.dirname(fileURLToPath(import.meta.url));
const arg = process.argv[2];
const raw = !arg
  ? fs.readFileSync(path.join(here, '..', 'references', 'example-input.json'), 'utf8')
  : (arg.trim().startsWith('{') ? arg : fs.readFileSync(arg, 'utf8'));
const input = JSON.parse(raw);

const res = await fetch(`https://api.apify.com/v2/acts/${actorId}/run-sync-get-dataset-items`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
  body: JSON.stringify(input)
});
if (!res.ok) {
  console.error(`HTTP ${res.status}: ${(await res.text()).slice(0, 500)}`);
  process.exit(1);
}
console.log(JSON.stringify(await res.json(), null, 2));
