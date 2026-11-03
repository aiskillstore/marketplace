#!/usr/bin/env node
import {PromptClient} from './client.mjs';
import {PublicCatalogClient,publicCapabilities} from './public-catalog.mjs';
const [action, query, ...rest] = process.argv.slice(2);
const publicQuery = ['models','capabilities'].includes(action);
if ((!publicQuery && (!['search','optimize'].includes(action) || !query || rest.length)) || (publicQuery && (query !== undefined || rest.length))) {
  console.error('Usage: node scripts/prompts.mjs models|capabilities\n       node scripts/prompts.mjs search|optimize "your keywords or image idea"');
  process.exitCode = 2;
} else {
  try {
    if (action === 'capabilities') console.log(JSON.stringify(publicCapabilities()));
    else if (action === 'models') console.log(JSON.stringify(await new PublicCatalogClient().models()));
    else {
      const client = new PromptClient({origin:process.env.INKROOM_PROMPTS_ORIGIN});
      console.log(JSON.stringify(await client[action](query)));
    }
  } catch (error) {
    console.log(JSON.stringify({error:{code:error.code || 'unexpected_error',message:error.code ? error.message : 'Prompt operation failed.',retryAfter:error.retryAfter ?? null}}));
    process.exitCode = 1;
  }
}
