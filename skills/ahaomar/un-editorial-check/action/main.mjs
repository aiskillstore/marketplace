// GitHub Action entry point: the CLI itself, unchanged.
//
// GitHub runs this with no shell step, so the workspace is entered
// explicitly and each input is translated into the same argv a user would
// type. The CLI's exit code becomes the action result: 0 pass, 1
// error-severity editorial findings, 2 usage or configuration failure.
import { run } from '../lib/cli.mjs';

const workspace = process.env.GITHUB_WORKSPACE;
if (workspace) process.chdir(workspace);

const args = [];
if (process.env.INPUT_PATH) args.push(process.env.INPUT_PATH);
if (process.env.INPUT_CONFIG) args.push('--config', process.env.INPUT_CONFIG);
if (process.env.INPUT_BASELINE) args.push('--baseline', process.env.INPUT_BASELINE);

process.exitCode = run(args);
