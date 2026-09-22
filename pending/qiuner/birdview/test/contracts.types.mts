import { checkArchitecture, checkActivity } from '../src/contracts/parse.mjs';
import type { Module, ActivityEvent } from '../src/contracts/models.mjs';

function narrowedInputs(map: unknown, event: unknown) {
  if (checkArchitecture(map)) {
    const module: Module | undefined = map.modules[0];
    if (module) {
      const column: number = module.layout.column;
      // @ts-expect-error coordinates cannot be used as strings
      const wrong: string = column;
      void wrong;
    }
  }
  if (checkActivity(event)) {
    const phase: ActivityEvent['phase'] = event.phase;
    // @ts-expect-error unsupported event phases must not typecheck
    const invalid: typeof phase = 'finished';
    void invalid;
  }
  // @ts-expect-error external input remains unknown before validation
  map.modules;
}
void narrowedInputs;
