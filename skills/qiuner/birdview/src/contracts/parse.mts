import { Ajv2020 } from 'ajv/dist/2020.js';
import { architectureSchema, activitySchema, type Architecture, type ActivityEvent } from './models.mjs';

// Preserve existing format policy: timestamps are annotations, not new rejection rules.
const ajv = new Ajv2020({ allErrors: true, strict: true, formats: { 'date-time': true } });
export const checkArchitecture = ajv.compile<Architecture>(architectureSchema);
export const checkActivity = ajv.compile<ActivityEvent>(activitySchema);
