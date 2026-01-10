#!/usr/bin/env node
/**
 * Helper functions for common Bitbucket pipeline operations
 * These provide intuitive, high-level wrappers around the CLI
 */

import { execSync } from 'child_process';
import { fileURLToPath, pathToFileURL } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Execute CLI command and return parsed JSON result
 */
function runCli(args) {
  const cliPath = join(__dirname, '..', 'bitbucket-mcp', 'dist', 'index-cli.js');
  const command = `node "${cliPath}" ${args}`;

  try {
    const output = execSync(command, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] , maxBuffer: 100 * 1024 * 1024 });
    return JSON.parse(output);
  } catch (error) {
    throw new Error(`CLI command failed: ${error.message}\n${error.stderr || ''}`);
  }
}

/**
 * Execute CLI command and return raw text result (for logs)
 */
function runCliText(args) {
  const cliPath = join(__dirname, '..', 'bitbucket-mcp', 'dist', 'index-cli.js');
  const command = `node "${cliPath}" ${args}`;

  try {
    return execSync(command, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] , maxBuffer: 100 * 1024 * 1024 });
  } catch (error) {
    throw new Error(`CLI command failed: ${error.message}\n${error.stderr || ''}`);
  }
}

/**
 * Get the latest failed pipeline for a repository
 */
export function getLatestFailedPipeline(workspace, repo) {
  const result = runCli(`list-pipelines "${workspace}" "${repo}" 1 FAILED`);

  if (!result.values || result.values.length === 0) {
    return null;
  }

  return result.values[0];
}

/**
 * Get the latest pipeline (any status) for a repository
 */
export function getLatestPipeline(workspace, repo) {
  const result = runCli(`list-pipelines "${workspace}" "${repo}" 1`);

  if (!result.values || result.values.length === 0) {
    return null;
  }

  return result.values[0];
}

/**
 * Get pipeline details by build number
 * Note: Requires looking up UUID first
 */
export function getPipelineByNumber(workspace, repo, buildNumber) {
  // List recent pipelines to find the UUID
  const result = runCli(`list-pipelines "${workspace}" "${repo}" 50`);

  const pipeline = result.values?.find(p => p.build_number === parseInt(buildNumber));

  if (!pipeline) {
    throw new Error(`Pipeline #${buildNumber} not found in recent pipelines`);
  }

  return pipeline;
}

/**
 * Get all steps for a pipeline
 */
export function getPipelineSteps(workspace, repo, pipelineUuid) {
  return runCli(`get-pipeline-steps "${workspace}" "${repo}" "${pipelineUuid}"`);
}

/**
 * Get only the failed steps from a pipeline
 */
export function getFailedSteps(workspace, repo, pipelineUuid) {
  const steps = runCli(`get-pipeline-steps "${workspace}" "${repo}" "${pipelineUuid}"`);

  if (!steps.values) {
    return [];
  }

  return steps.values.filter(step =>
    step.state?.result?.name === 'FAILED' || step.state?.result?.name === 'ERROR'
  );
}

/**
 * Download logs for a specific step
 */
export function downloadStepLogs(workspace, repo, pipelineUuid, stepUuid) {
  return runCliText(`get-step-logs "${workspace}" "${repo}" "${pipelineUuid}" "${stepUuid}"`);
}

/**
 * Download logs for all failed steps and save to project directory
 * Returns array of objects with step info and log file path
 */
export function downloadFailedStepLogs(workspace, repo, pipelineUuid, buildNumber) {
  const failedSteps = getFailedSteps(workspace, repo, pipelineUuid);

  if (failedSteps.length === 0) {
    return [];
  }

  // Create .pipeline-logs directory in current working directory
  const logDir = join(process.cwd(), '.pipeline-logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const results = [];

  for (const step of failedSteps) {
    const stepName = step.name || 'unnamed';
    const safeStepName = stepName.replace(/[^a-z0-9-]/gi, '_');
    const logFileName = `pipeline-${buildNumber}-${safeStepName}.log`;
    const logFilePath = join(logDir, logFileName);

    try {
      const logs = downloadStepLogs(workspace, repo, pipelineUuid, step.uuid);
      fs.writeFileSync(logFilePath, logs);

      results.push({
        stepName,
        stepUuid: step.uuid,
        logFilePath,
        size: logs.length,
        status: step.state?.result?.name
      });
    } catch (error) {
      console.error(`Failed to download logs for step ${stepName}:`, error.message);
    }
  }

  return results;
}

/**
 * Get pipeline info with friendly formatting
 */
export function getPipelineInfo(workspace, repo, pipelineUuid) {
  const pipeline = runCli(`get-pipeline "${workspace}" "${repo}" "${pipelineUuid}"`);
  const steps = runCli(`get-pipeline-steps "${workspace}" "${repo}" "${pipelineUuid}"`);

  return {
    buildNumber: pipeline.build_number,
    status: pipeline.state?.name,
    branch: pipeline.target?.ref_name,
    commit: {
      hash: pipeline.target?.commit?.hash?.substring(0, 7),
      message: pipeline.target?.commit?.message
    },
    createdOn: pipeline.created_on,
    completedOn: pipeline.completed_on,
    durationSeconds: pipeline.duration_in_seconds,
    steps: steps.values?.map(step => ({
      name: step.name,
      status: step.state?.name,
      result: step.state?.result?.name,
      durationSeconds: step.duration_in_seconds
    })) || []
  };
}

/**
 * Trigger a pipeline run
 */
export function triggerPipeline(workspace, repo, branch, customPipeline = null) {
  const args = customPipeline
    ? `run-pipeline "${workspace}" "${repo}" "${branch}" "${customPipeline}"`
    : `run-pipeline "${workspace}" "${repo}" "${branch}"`;

  return runCli(args);
}

/**
 * Stop a running pipeline
 */
export function stopPipeline(workspace, repo, pipelineUuid) {
  return runCli(`stop-pipeline "${workspace}" "${repo}" "${pipelineUuid}"`);
}

/**
 * Monitor progress of a running pipeline
 * Returns current status and tail of logs for running steps
 */
export function monitorPipelineProgress(workspace, repo, pipelineUuid, tailLines = 40) {
  const bytesToFetch = tailLines * 80; // ~80 chars per line

  // Get all steps
  const steps = runCli(`get-pipeline-steps "${workspace}" "${repo}" "${pipelineUuid}"`);

  // Filter by status
  const runningSteps = steps.values?.filter(s => s.state?.name === "IN_PROGRESS") || [];
  const completedSteps = steps.values?.filter(s => s.state?.name === "COMPLETED") || [];
  const pendingSteps = steps.values?.filter(s => s.state?.name === "PENDING") || [];

  const progress = {
    total: steps.values?.length || 0,
    completed: completedSteps.length,
    running: runningSteps.length,
    pending: pendingSteps.length,
    runningDetails: []
  };

  // Get tail logs for running steps
  for (const step of runningSteps) {
    const logTail = runCliText(
      `tail-step-log "${workspace}" "${repo}" "${pipelineUuid}" "${step.uuid}" ${bytesToFetch}`
    );

    progress.runningDetails.push({
      stepName: step.name,
      stepUuid: step.uuid,
      startedOn: step.started_on,
      duration: step.duration_in_seconds || 0,
      logTail: logTail.trim().split('\n').slice(-tailLines).join('\n')
    });
  }

  return progress;
}

/**
 * Get current status of pipeline (simplified monitor)
 */
export function getCurrentPipelineStatus(workspace, repo, pipelineUuid) {
  return monitorPipelineProgress(workspace, repo, pipelineUuid, 20);
}
/**
 * Get branching model (available pipeline types)
 */
export function getBranchingModel(workspace, repo) {
  return runCli(`get-branching-model "${workspace}" "${repo}"`);
}

/**
 * List recent pipelines with optional filters
 */
export function listPipelines(workspace, repo, limit = 10, status = null) {
  const statusArg = status ? ` ${status}` : '';
  return runCli(`list-pipelines "${workspace}" "${repo}" ${limit}${statusArg}`);
}

// ============ GIT OPERATIONS ============

/**
 * Load credentials for git operations
 * Reads from same sources as CLI, returns credentials object
 */
function loadCredentials() {
  const credentialPaths = [
    join(process.cwd(), "credentials.json"),
    join(process.cwd(), ".bitbucket-credentials"),
    join(os.homedir(), ".bitbucket-credentials"),
    join(os.homedir(), ".claude", "skills", "bitbucket-devops", "credentials.json"),
  ];

  for (const credPath of credentialPaths) {
    if (fs.existsSync(credPath)) {
      try {
        const content = fs.readFileSync(credPath, "utf-8");
        return JSON.parse(content);
      } catch (error) {
        continue;
      }
    }
  }

  throw new Error('No credentials file found. Please create credentials.json from template.');
}

/**
 * Build authenticated git URL for HTTPS operations
 * Uses username (workspace slug) for git auth, not user_email
 * @param {string} workspace - Bitbucket workspace slug
 * @param {string} repo - Repository slug
 * @returns {string} Fully authenticated git URL
 */
export function buildGitUrl(workspace, repo) {
  const creds = loadCredentials();

  // Git operations use username (workspace slug), not user_email
  const gitUsername = creds.username;
  const password = creds.password || creds.app_password;

  if (!password) {
    throw new Error('Password/app-password required for git operations');
  }

  // URL-encode password for special characters
  const encodedPassword = encodeURIComponent(password);

  return `https://${gitUsername}:${encodedPassword}@bitbucket.org/${workspace}/${repo}.git`;
}

/**
 * Test git connectivity to a repository
 * @param {string} workspace - Bitbucket workspace slug
 * @param {string} repo - Repository slug
 * @returns {object} Result with success flag and commit hash or error
 */
export function testGitAuth(workspace, repo) {
  try {
    const gitUrl = buildGitUrl(workspace, repo);
    const result = execSync(`git ls-remote ${gitUrl} HEAD`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    const commit = result.trim().split('\t')[0];
    return {
      success: true,
      commit,
      message: `Git authentication successful for ${workspace}/${repo}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.stderr || error.message,
      message: `Git authentication failed for ${workspace}/${repo}`
    };
  }
}

/**
 * Clone a repository to a local directory
 * @param {string} workspace - Bitbucket workspace slug
 * @param {string} repo - Repository slug
 * @param {string} targetDir - Target directory (defaults to repo name)
 * @returns {object} Result with success flag and directory path
 */
export function cloneRepository(workspace, repo, targetDir = null) {
  try {
    const gitUrl = buildGitUrl(workspace, repo);
    const target = targetDir || repo;

    execSync(`git clone ${gitUrl} ${target}`, {
      encoding: 'utf-8',
      stdio: 'inherit'  // Show git output to user
    });

    return {
      success: true,
      directory: target,
      message: `Successfully cloned ${workspace}/${repo} to ${target}`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `Failed to clone ${workspace}/${repo}`
    };
  }
}

// CLI entry point
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [command, ...args] = process.argv.slice(2);

  try {
    let result;

    switch (command) {
      case 'get-latest-failed':
        result = getLatestFailedPipeline(args[0], args[1]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'get-latest':
        result = getLatestPipeline(args[0], args[1]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'get-by-number':
        result = getPipelineByNumber(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'get-failed-steps':
        result = getFailedSteps(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'download-failed-logs':
        result = downloadFailedStepLogs(args[0], args[1], args[2], args[3]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'get-info':
        result = getPipelineInfo(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;


      case 'stop-pipeline':
        result = stopPipeline(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'monitor-progress':
        result = monitorPipelineProgress(args[0], args[1], args[2], args[3] ? parseInt(args[3]) : 40);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'current-status':
        result = getCurrentPipelineStatus(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'test-git-auth':
        result = testGitAuth(args[0], args[1]);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'clone-repo':
        result = cloneRepository(args[0], args[1], args[2]);
        console.log(JSON.stringify(result, null, 2));
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.error('\nAvailable commands:');
        console.error('  Pipeline commands:');
        console.error('    get-latest-failed <workspace> <repo>');
        console.error('    get-latest <workspace> <repo>');
        console.error('    get-by-number <workspace> <repo> <build_number>');
        console.error('    get-failed-steps <workspace> <repo> <pipeline_uuid>');
        console.error('    download-failed-logs <workspace> <repo> <pipeline_uuid> <build_number>');
        console.error('    get-info <workspace> <repo> <pipeline_uuid>');
        console.error('    stop-pipeline <workspace> <repo> <pipeline_uuid>');
        console.error('    monitor-progress <workspace> <repo> <pipeline_uuid> [tail_lines]');
        console.error('    current-status <workspace> <repo> <pipeline_uuid>');
        console.error('');
        console.error('  Git commands:');
        console.error('    test-git-auth <workspace> <repo>');
        console.error('    clone-repo <workspace> <repo> [target_dir]');
        process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}
