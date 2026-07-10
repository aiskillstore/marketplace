#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import {
	existsSync,
	readFileSync,
	renameSync,
	rmSync,
	writeFileSync,
} from 'node:fs';
import { spawnSync } from 'node:child_process';
import {
	dirname,
	isAbsolute,
	join,
	relative,
	resolve,
	sep,
} from 'node:path';
import { pathToFileURL } from 'node:url';
import { calculatePackageHashes } from './validate-skill-publication.mjs';

const HASH_PATTERN = /^[a-f0-9]{64}$/;
const REPORT_FILENAME = 'skill-report.json';
const ATTESTATION_FILENAME = 'skill-report.attestation.json';
const EXPECTED_PRODUCER_REPOSITORY = 'aiskillstore/skillstore';

function sha256(value) {
	return createHash('sha256').update(value).digest('hex');
}

function skipWhitespace(source, start) {
	let index = start;
	while (/[\t\n\r ]/.test(source[index] ?? '')) index++;
	return index;
}

function readJsonString(source, start) {
	if (source[start] !== '"') throw new Error('expected a JSON string');

	for (let index = start + 1; index < source.length; index++) {
		if (source[index] === '\\') {
			index++;
		} else if (source[index] === '"') {
			const end = index + 1;
			return {
				contentEnd: index,
				contentStart: start + 1,
				end,
				value: JSON.parse(source.slice(start, end)),
			};
		}
	}

	throw new Error('unterminated JSON string');
}

function readJsonArray(source, start) {
	let index = skipWhitespace(source, start + 1);
	if (source[index] === ']') return index + 1;

	while (index < source.length) {
		index = skipJsonValue(source, index);
		index = skipWhitespace(source, index);
		if (source[index] === ']') return index + 1;
		if (source[index] !== ',') throw new Error('expected a comma in JSON array');
		index = skipWhitespace(source, index + 1);
	}

	throw new Error('unterminated JSON array');
}

function readJsonObject(source, start) {
	const members = [];
	let index = skipWhitespace(source, start + 1);
	if (source[index] === '}') return { end: index + 1, members };

	while (index < source.length) {
		const key = readJsonString(source, index);
		index = skipWhitespace(source, key.end);
		if (source[index] !== ':') throw new Error('expected a colon in JSON object');

		const valueStart = skipWhitespace(source, index + 1);
		const valueEnd = skipJsonValue(source, valueStart);
		members.push({ key: key.value, valueEnd, valueStart });

		index = skipWhitespace(source, valueEnd);
		if (source[index] === '}') return { end: index + 1, members };
		if (source[index] !== ',') throw new Error('expected a comma in JSON object');
		index = skipWhitespace(source, index + 1);
	}

	throw new Error('unterminated JSON object');
}

function skipJsonValue(source, start) {
	const index = skipWhitespace(source, start);
	if (source[index] === '"') return readJsonString(source, index).end;
	if (source[index] === '{') return readJsonObject(source, index).end;
	if (source[index] === '[') return readJsonArray(source, index);

	let end = index;
	while (end < source.length && !/[\t\n\r ,}\]]/.test(source[end])) end++;
	if (end === index) throw new Error('expected a JSON value');
	return end;
}

function locateMetaHashSpans(source) {
	const rootStart = skipWhitespace(source, 0);
	if (source[rootStart] !== '{') throw new Error('skill-report.json must contain a JSON object');

	const root = readJsonObject(source, rootStart);
	const metaMembers = root.members.filter((member) => member.key === 'meta');
	if (metaMembers.length !== 1) {
		throw new Error('skill-report.json must contain exactly one top-level meta object');
	}

	const metaStart = metaMembers[0].valueStart;
	if (source[metaStart] !== '{') throw new Error('skill-report.json meta must be a JSON object');
	const meta = readJsonObject(source, metaStart);
	const spans = {};

	for (const field of ['content_hash', 'tree_hash']) {
		const matches = meta.members.filter((member) => member.key === field);
		if (matches.length !== 1) {
			throw new Error(`skill-report.json meta.${field} must appear exactly once`);
		}

		const token = readJsonString(source, matches[0].valueStart);
		if (token.end !== matches[0].valueEnd || !HASH_PATTERN.test(token.value)) {
			throw new Error(
				`skill-report.json meta.${field} must be a 64-character lowercase SHA-256 hash`,
			);
		}
		spans[field] = token;
	}

	return spans;
}

function bindReportHashes(reportPath, rawAuditBytes, hashes) {
	const source = rawAuditBytes.toString('utf8');
	let spans;
	try {
		spans = locateMetaHashSpans(source);
	} catch (error) {
		throw new Error(`${reportPath}: ${error.message}`);
	}

	const replacements = [
		{ ...spans.content_hash, value: hashes.contentHash },
		{ ...spans.tree_hash, value: hashes.treeHash },
	].sort((left, right) => right.contentStart - left.contentStart);
	let bound = source;
	for (const replacement of replacements) {
		bound = [
			bound.slice(0, replacement.contentStart),
			replacement.value,
			bound.slice(replacement.contentEnd),
		].join('');
	}

	const bytes = Buffer.from(bound, 'utf8');
	const report = parseReport(reportPath, bytes);
	if (
		report.meta.content_hash !== hashes.contentHash
		|| report.meta.tree_hash !== hashes.treeHash
	) {
		throw new Error(`${reportPath}: failed to bind final package hashes`);
	}
	return { bytes, report };
}

function isWithin(parentDir, candidatePath) {
	const rel = relative(parentDir, candidatePath);
	return rel === '' || (!rel.startsWith(`..${sep}`) && rel !== '..' && !isAbsolute(rel));
}

function run(command, args, options = {}) {
	return spawnSync(command, args, {
		encoding: 'utf8',
		maxBuffer: 64 * 1024 * 1024,
		...options,
	});
}

function git(worktree, ...args) {
	const result = run('git', ['-C', worktree, ...args]);
	if (result.status !== 0) {
		throw new Error(`git ${args.join(' ')} failed: ${result.stderr.trim()}`);
	}
	return result.stdout.trim();
}

function producerIdentity(auditWorktree) {
	const packagePath = join(auditWorktree, 'package.json');
	const auditSourcePath = join(
		auditWorktree,
		'src',
		'cli',
		'commands',
		'skill',
		'audit.ts',
	);
	if (!existsSync(packagePath) || !existsSync(auditSourcePath)) {
		throw new Error(`${auditWorktree}: audit producer source is incomplete`);
	}
	const status = git(auditWorktree, 'status', '--porcelain');
	if (status !== '') throw new Error(`${auditWorktree}: audit producer worktree must be clean`);
	const remote = git(auditWorktree, 'remote', 'get-url', 'origin')
		.replace(/^git@github\.com:/, 'https://github.com/')
		.replace(/\.git$/, '');
	if (remote !== `https://github.com/${EXPECTED_PRODUCER_REPOSITORY}`) {
		throw new Error(`${auditWorktree}: producer origin must be ${EXPECTED_PRODUCER_REPOSITORY}`);
	}
	const packageDocument = JSON.parse(readFileSync(packagePath, 'utf8'));
	const auditSource = readFileSync(auditSourcePath, 'utf8');
	const versionMatch = auditSource.match(/\bconst VERSION\s*=\s*['"]([^'"]+)['"]/);
	if (!versionMatch) throw new Error(`${auditSourcePath}: audit command version is missing`);
	return {
		audit_command_version: versionMatch[1],
		commit: git(auditWorktree, 'rev-parse', 'HEAD'),
		package_version: packageDocument.version,
		repository: EXPECTED_PRODUCER_REPOSITORY,
	};
}

function parseReport(reportPath, bytes) {
	let report;
	try {
		report = JSON.parse(bytes.toString('utf8'));
	} catch (error) {
		throw new Error(`${reportPath}: invalid JSON: ${error.message}`);
	}
	if (report?.schema_version !== '2.0') {
		throw new Error(`${reportPath}: schema_version must equal 2.0`);
	}
	if (typeof report?.meta?.slug !== 'string' || report.meta.slug === '') {
		throw new Error(`${reportPath}: meta.slug is required`);
	}
	return report;
}

function atomicWrite(path, content) {
	const temporary = join(
		dirname(path),
		`.${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`,
	);
	writeFileSync(temporary, content, { flag: 'wx' });
	renameSync(temporary, path);
}

function restorePackages(prepared) {
	for (const item of prepared) {
		writeFileSync(item.reportPath, item.inputBytes);
		if (item.previousAttestation === null) {
			rmSync(item.attestationPath, { force: true });
		} else {
			writeFileSync(item.attestationPath, item.previousAttestation);
		}
	}
}

function validateAuditWindow(report, startedAt, completedAt, reportPath) {
	if (report.security_audit?.analysis_status !== 'ok') {
		throw new Error(`${reportPath}: fresh audit analysis_status must equal ok`);
	}
	for (const [field, value] of [
		['meta.generated_at', report.meta?.generated_at],
		['security_audit.audited_at', report.security_audit?.audited_at],
	]) {
		const timestamp = Date.parse(value);
		if (
			!Number.isFinite(timestamp)
			|| timestamp < startedAt
			|| timestamp > completedAt
		) {
			throw new Error(`${reportPath}: ${field} is outside this audit invocation`);
		}
	}
}

export async function runAuditBinding({
	auditWorktree,
	model,
	packageDirs,
	skillsRoot,
	slugs,
}) {
	const absoluteAuditWorktree = resolve(auditWorktree);
	const absoluteSkillsRoot = resolve(skillsRoot);
	const normalizedSlugs = [...new Set(slugs)].sort((left, right) => (
		Buffer.compare(Buffer.from(left, 'utf8'), Buffer.from(right, 'utf8'))
	));
	const absolutePackages = [...new Set(packageDirs.map((path) => resolve(path)))].sort(
		(left, right) => Buffer.compare(Buffer.from(left, 'utf8'), Buffer.from(right, 'utf8')),
	);
	if (absolutePackages.length === 0) throw new Error('at least one --package is required');
	if (normalizedSlugs.length !== absolutePackages.length) {
		throw new Error('--slugs must identify every explicit package exactly once');
	}
	if (typeof model !== 'string' || model.trim() === '') throw new Error('--model is required');
	if (!existsSync(absoluteSkillsRoot)) throw new Error(`${absoluteSkillsRoot}: skills root is missing`);
	for (const packageDir of absolutePackages) {
		if (!isWithin(absoluteSkillsRoot, packageDir)) {
			throw new Error(`${packageDir}: package must be inside --skills-root`);
		}
	}

	const producer = producerIdentity(absoluteAuditWorktree);
	const prepared = [];
	try {
		for (const packageDir of absolutePackages) {
			const reportPath = join(packageDir, REPORT_FILENAME);
			const attestationPath = join(packageDir, ATTESTATION_FILENAME);
			if (!existsSync(reportPath)) throw new Error(`${reportPath}: skill-report.json is missing`);
			const inputBytes = readFileSync(reportPath);
			const inputReport = parseReport(reportPath, inputBytes);
			const previousAttestation = existsSync(attestationPath)
				? readFileSync(attestationPath)
				: null;
			const item = {
				attestationPath,
				inputBytes,
				inputDigest: sha256(inputBytes),
				inputHashes: null,
				inputReport,
				packageDir,
				previousAttestation,
				reportPath,
			};
			prepared.push(item);
			item.inputHashes = await calculatePackageHashes(packageDir);
			rmSync(attestationPath, { force: true });
		}
		const reportSlugs = prepared.map((item) => item.inputReport.meta.slug).sort();
		if (JSON.stringify(reportSlugs) !== JSON.stringify([...normalizedSlugs].sort())) {
			throw new Error('--slugs must exactly match the selected report meta.slug values');
		}

		const command = [
			process.execPath,
			'--import',
			'tsx',
			join(absoluteAuditWorktree, 'src', 'cli', 'index.ts'),
			'skill',
			'audit',
			relative(absoluteAuditWorktree, absoluteSkillsRoot),
			'--slugs',
			normalizedSlugs.join(','),
			'--model',
			model,
		];
		const startedAtMs = Date.now();
		const startedAt = new Date(startedAtMs).toISOString();
		const audit = run(command[0], command.slice(1), { cwd: absoluteAuditWorktree });
		const completedAtMs = Date.now();
		const completedAt = new Date(completedAtMs).toISOString();
		if (audit.error) throw new Error(`audit invocation failed: ${audit.error.message}`);
		if (audit.status !== 0) {
			throw new Error(
				`audit invocation exited ${audit.status}: ${(audit.stderr || audit.stdout).trim()}`,
			);
		}

		const proven = [];
		for (const item of prepared) {
			const rawAuditBytes = readFileSync(item.reportPath);
			const rawAuditDigest = sha256(rawAuditBytes);
			if (rawAuditDigest === item.inputDigest) {
				throw new Error(`${item.reportPath}: audit invocation did not replace the selected report`);
			}
			const rawAuditReport = parseReport(item.reportPath, rawAuditBytes);
			if (rawAuditReport.meta.slug !== item.inputReport.meta.slug) {
				throw new Error(`${item.reportPath}: audit changed the report slug`);
			}
			validateAuditWindow(rawAuditReport, startedAtMs, completedAtMs, item.reportPath);
			const finalHashes = await calculatePackageHashes(item.packageDir);
			if (
				finalHashes.contentHash !== item.inputHashes.contentHash
				|| finalHashes.treeHash !== item.inputHashes.treeHash
			) {
				throw new Error(`${item.packageDir}: audit modified privileged package content or modes`);
			}
			const requestedModel = rawAuditReport.meta?.provenance?.model_requested;
			if (requestedModel !== model) {
				throw new Error(`${item.reportPath}: producer model does not match --model`);
			}
			if (!HASH_PATTERN.test(rawAuditDigest)) {
				throw new Error(`${item.reportPath}: invalid raw audit report digest`);
			}

			proven.push({
				...item,
				finalHashes,
				rawAuditBytes,
				rawAuditDigest,
				rawAuditReport,
			});
		}

		const invocationId = randomUUID();
		const stdoutDigest = sha256(audit.stdout);
		const stderrDigest = sha256(audit.stderr);
		const bindings = [];
		for (const item of proven) {
			const bound = bindReportHashes(item.reportPath, item.rawAuditBytes, item.finalHashes);
			const finalDigest = sha256(bound.bytes);
			bindings.push({
				attestationPath: item.attestationPath,
				finalBytes: bound.bytes,
				reportPath: item.reportPath,
				slug: bound.report.meta.slug,
				attestation: {
					schema_version: '1.0',
					slug: bound.report.meta.slug,
					producer,
					invocation: {
						id: invocationId,
						started_at: startedAt,
						completed_at: completedAt,
						cwd: absoluteAuditWorktree,
						command,
						skills_root: absoluteSkillsRoot,
						slugs: normalizedSlugs,
						model,
						stdout_digest: stdoutDigest,
						stderr_digest: stderrDigest,
					},
					report: {
						input_digest: item.inputDigest,
						raw_audit_digest: item.rawAuditDigest,
						final_digest: finalDigest,
					},
					package: {
						content_hash: item.finalHashes.contentHash,
						tree_hash: item.finalHashes.treeHash,
					},
				},
			});
		}

		for (const binding of bindings) {
			atomicWrite(binding.reportPath, binding.finalBytes);
		}
		for (const binding of bindings) {
			atomicWrite(
				binding.attestationPath,
				`${JSON.stringify(binding.attestation, null, 2)}\n`,
			);
			console.log(`ATTESTED ${binding.slug}`);
		}
		return bindings.map((binding) => binding.attestation);
	} catch (error) {
		restorePackages(prepared);
		throw error;
	}
}

function parseArguments(argv) {
	const options = { packageDirs: [] };
	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		if (arg === '--audit-worktree') options.auditWorktree = argv[++index];
		else if (arg === '--skills-root') options.skillsRoot = argv[++index];
		else if (arg === '--slugs') options.slugs = (argv[++index] ?? '').split(',').filter(Boolean);
		else if (arg === '--model') options.model = argv[++index];
		else if (arg === '--package') options.packageDirs.push(argv[++index]);
		else if (arg === '--help' || arg === '-h') options.help = true;
		else throw new Error(`Unknown argument: ${arg}`);
	}
	if (options.help) return options;
	if (!options.auditWorktree || !options.skillsRoot || !options.slugs?.length || !options.model) {
		throw new Error(
			'direct binding is disabled; --audit-worktree, --skills-root, --slugs, and --model are required',
		);
	}
	if (options.packageDirs.length === 0 || options.packageDirs.some((path) => !path)) {
		throw new Error('at least one --package path is required');
	}
	return options;
}

function printHelp() {
	console.log(`Usage:
  node scripts/bind-skill-report-hashes.mjs \
    --audit-worktree <clean-skillstore-worktree> \
    --skills-root <marketplace-skill-root> \
    --slugs <comma-separated-report-slugs> \
    --model <model> \
    --package <dir> [--package <dir> ...]
`);
}

async function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}
	await runAuditBinding(options);
	return 0;
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : '';
if (invokedPath === import.meta.url) {
	runCli(process.argv.slice(2))
		.then((status) => {
			process.exitCode = status;
		})
		.catch((error) => {
			console.error(`ERROR ${error.message}`);
			process.exitCode = 2;
		});
}
