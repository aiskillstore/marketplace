import fs from 'node:fs';
import { architectureSchema, activitySchema } from './models.mjs';
import * as models from './models.mjs';
// Preserve public $defs anchors for consumers of the v1 exchange schemas.
const architectureDefinitions = {
    constraint: models.mapConstraint, language: models.mapLanguage,
    translations: models.mapTranslations, translation: models.mapTranslation,
    id: models.mapId, text: models.mapText, path: models.mapPath,
    questions: models.mapQuestions, evidenceList: models.mapEvidenceList
};
// Export data-only exchange schemas; TypeBox metadata is not serialized.
for (const [name, schema, id] of [
    ['architecture', architectureSchema, 'urn:birdview:architecture:1'],
    ['activity', activitySchema, 'urn:birdview:activity:1']
]) {
    const file = new URL(`../../schemas/${name}.schema.json`, import.meta.url);
    const $defs = name === 'architecture' ? architectureDefinitions : { paths: models.eventPaths };
    const text = JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', $id: id, ...schema, $defs }, null, 2) + '\n';
    if (process.argv.includes('--check')) {
        if (fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n') !== text)
            throw new Error(`Stale ${name} schema: run npm run build.`);
    }
    else
        fs.writeFileSync(file, text);
}
