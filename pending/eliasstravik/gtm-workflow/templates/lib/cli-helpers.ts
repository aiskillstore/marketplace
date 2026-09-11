export const HELP = `gtm run <workflow> --input <file> [--dry-run] [--checkpoint N] [--url <origin>] [--wait-live] [--background]
gtm runs get <id> [--wait <seconds>] [--url <origin>]
gtm verify <workflow> --input <file> [--url <origin>]
gtm check
gtm query --sql "<select>" [--format json|markdown|csv] [--cloud]
gtm diagram <workflow> [--format json|svg|png|web] [--run <id>] [--url <origin>]
gtm approve <token> --yes|--no [--comment <text>] [--url <origin>]
gtm cancel <id> [--reason <text>] [--url <origin>]
gtm upgrade [ref] [--yes]
gtm help
`;

/** Migration files whose content hash is not yet in the applied-migrations ledger. */
export function pendingFrom(files: { file: string; hash: string }[], applied: Set<string>): string[] {
  return files.filter((entry) => !applied.has(entry.hash)).map((entry) => entry.file);
}

/** The argv a detached waiter receives: the same run, without the flag that spawned it. */
export function backgroundArgv(args: string[]): string[] {
  return args.filter((value) => value !== "--background");
}
