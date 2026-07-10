#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
	existsSync,
	lstatSync,
	readFileSync,
	readdirSync,
	statSync,
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
import { lexer, walkTokens } from 'marked';
import { findHumanApproval } from './lib/publication-approval.mjs';

const HASH_PATTERN = /^[a-f0-9]{64}$/;
const DEFAULT_APPROVALS_PATH = '.github/skill-publish-approvals.json';
const REPORT_FILENAME = 'skill-report.json';
const ATTESTATION_FILENAME = 'skill-report.attestation.json';
const GIT_OUTPUT_BUFFER_BYTES = 64 * 1024 * 1024;
const UUID_PATTERN = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;

function sha256(value) {
	return createHash('sha256').update(value).digest('hex');
}

function normalizeSkillMdContent(content) {
	const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
	if (!frontmatterMatch) return content.trim();

	const frontmatter = frontmatterMatch[1]
		.split('\n')
		.filter((line) => !line.trim().startsWith('version:'))
		.join('\n');
	const body = content.slice(frontmatterMatch[0].length);
	return `---\n${frontmatter}\n---${body}`.trim();
}

function collectPackageFiles(packageDir) {
	const files = [];

	function walk(dir) {
		const entries = readdirSync(dir, { withFileTypes: true });

		for (const entry of entries) {
			const fullPath = join(dir, entry.name);
			const relativePath = relative(packageDir, fullPath);

			if (entry.isSymbolicLink()) {
				throw new Error(`${relativePath}: symbolic links are not allowed in skill packages`);
			}
			if (entry.isDirectory()) {
				walk(fullPath);
			} else if (entry.isFile()) {
				if (![REPORT_FILENAME, ATTESTATION_FILENAME].includes(entry.name)) {
					files.push(fullPath);
				}
			} else {
				throw new Error(`${relativePath}: non-regular package entries are not allowed`);
			}
		}
	}

	walk(packageDir);
	return files.sort((left, right) => Buffer.compare(
		Buffer.from(relative(packageDir, left).split(sep).join('/'), 'utf8'),
		Buffer.from(relative(packageDir, right).split(sep).join('/'), 'utf8'),
	));
}

function markdownDestinations(content) {
	const destinations = [];
	const tokens = lexer(content);
	walkTokens(tokens, (token) => {
		if (
			['link', 'image', 'def'].includes(token.type)
			&& typeof token.href === 'string'
		) {
			destinations.push(token.href);
		}
	});
	return [...new Set(destinations)];
}

function localMarkdownPath(destination) {
	const value = destination.trim();
	if (
		value === ''
		|| value.startsWith('#')
		|| value.startsWith('/')
		|| value.startsWith('//')
		|| /^[a-z][a-z0-9+.-]*:/i.test(value)
	) {
		return null;
	}

	const pathOnly = value.split(/[?#]/, 1)[0];
	if (pathOnly === '') return null;

	try {
		return decodeURIComponent(pathOnly);
	} catch {
		return pathOnly;
	}
}

export async function scanMarkdownLinks(packageDir) {
	const absoluteDir = resolve(packageDir);
	const errors = [];
	let files;

	try {
		files = collectPackageFiles(absoluteDir);
	} catch (error) {
		return [`${absoluteDir}: ${error.message}`];
	}

	for (const markdownPath of files.filter((filePath) => filePath.toLowerCase().endsWith('.md'))) {
		const source = relative(absoluteDir, markdownPath).split(sep).join('/');
		const content = readFileSync(markdownPath, 'utf8');

		for (const destination of markdownDestinations(content)) {
			const localPath = localMarkdownPath(destination);
			if (localPath === null) continue;

			const targetPath = resolve(dirname(markdownPath), localPath);
			if (!isWithin(absoluteDir, targetPath)) {
				errors.push(`${source}: relative Markdown reference escapes package: ${destination}`);
				continue;
			}
			if (!existsSync(targetPath)) {
				errors.push(`${source}: relative Markdown reference does not exist: ${destination}`);
			}
		}
	}

	return errors;
}

export async function calculatePackageHashes(packageDir) {
	const absoluteDir = resolve(packageDir);
	const skillMdPath = join(absoluteDir, 'SKILL.md');
	if (!existsSync(skillMdPath)) {
		throw new Error(`${absoluteDir}: SKILL.md is missing`);
	}

	const files = collectPackageFiles(absoluteDir);
	const fileHashes = files.map((filePath) => {
		const relativePath = relative(absoluteDir, filePath).split(sep).join('/');
		const mode = (lstatSync(filePath).mode & 0o111) === 0 ? '100644' : '100755';
		return `${mode} ${relativePath}\0${sha256(readFileSync(filePath))}`;
	});

	return {
		contentHash: sha256(normalizeSkillMdContent(readFileSync(skillMdPath, 'utf8'))),
		treeHash: sha256(fileHashes.join('\n')),
	};
}

function isWithin(parentDir, candidateDir) {
	const rel = relative(parentDir, candidateDir);
	return rel === '' || (!rel.startsWith(`..${sep}`) && rel !== '..' && !isAbsolute(rel));
}

function walkNamedFiles(rootDir, filename) {
	if (!existsSync(rootDir)) return [];
	const matches = [];

	function walk(dir) {
		const entries = readdirSync(dir, { withFileTypes: true });
		for (const entry of entries) {
			const fullPath = join(dir, entry.name);
			if (entry.isDirectory()) {
				walk(fullPath);
			} else if (entry.isFile() && entry.name === filename) {
				matches.push(fullPath);
			}
		}
	}

	walk(rootDir);
	return matches;
}

export async function discoverPackageDirs(rootDir) {
	const absoluteRoot = resolve(rootDir);
	if (!existsSync(absoluteRoot)) return [];

	const reportDirs = walkNamedFiles(absoluteRoot, 'skill-report.json')
		.map((reportPath) => dirname(reportPath))
		.sort((left, right) => left.length - right.length || left.localeCompare(right));
	const packageDirs = [];

	for (const reportDir of reportDirs) {
		if (!packageDirs.some((packageDir) => isWithin(packageDir, reportDir))) {
			packageDirs.push(reportDir);
		}
	}

	for (const skillPath of walkNamedFiles(absoluteRoot, 'SKILL.md')) {
		const skillDir = dirname(skillPath);
		if (!packageDirs.some((packageDir) => isWithin(packageDir, skillDir))) {
			packageDirs.push(skillDir);
		}
	}

	return packageDirs.sort((left, right) => left.localeCompare(right));
}

function requiredString(value, field, errors) {
	if (typeof value !== 'string' || value.trim() === '') {
		errors.push(`${field} is required`);
		return false;
	}
	return true;
}

function validateDateTime(value, field, errors) {
	if (!requiredString(value, field, errors)) return;
	if (!Number.isFinite(Date.parse(value))) {
		errors.push(`${field} must be an ISO 8601 timestamp`);
	}
}

function validateRequiredGateFields(report) {
	const errors = [];

	if (!report || typeof report !== 'object' || Array.isArray(report)) {
		return ['skill-report.json must contain a JSON object'];
	}
	if (report.schema_version !== '2.0') {
		errors.push('schema_version must equal 2.0');
	}
	requiredString(report.meta?.slug, 'meta.slug', errors);
	validateDateTime(report.meta?.generated_at, 'meta.generated_at', errors);
	requiredString(report.meta?.model, 'meta.model', errors);
	requiredString(report.meta?.analysis_version, 'meta.analysis_version', errors);
	requiredString(report.meta?.content_hash, 'meta.content_hash', errors);
	requiredString(report.meta?.tree_hash, 'meta.tree_hash', errors);
	if (typeof report.meta?.content_hash === 'string' && !HASH_PATTERN.test(report.meta.content_hash)) {
		errors.push('meta.content_hash must be a 64-character lowercase SHA-256 hash');
	}
	if (typeof report.meta?.tree_hash === 'string' && !HASH_PATTERN.test(report.meta.tree_hash)) {
		errors.push('meta.tree_hash must be a 64-character lowercase SHA-256 hash');
	}
	if (
		!report.meta?.provenance
		|| !Array.isArray(report.meta.provenance.fallback_chain)
		|| report.meta.provenance.fallback_chain.length === 0
	) {
		errors.push('meta.provenance.fallback_chain is required');
	}
	if (report.security_audit?.analysis_status !== 'ok') {
		errors.push('security_audit.analysis_status must equal ok');
	}
	if (typeof report.security_audit?.is_blocked !== 'boolean') {
		errors.push('security_audit.is_blocked must be a boolean');
	}
	if (typeof report.security_audit?.safe_to_publish !== 'boolean') {
		errors.push('security_audit.safe_to_publish must be a boolean');
	}
	validateDateTime(report.security_audit?.audited_at, 'security_audit.audited_at', errors);
	requiredString(report.security_audit?.audit_model, 'security_audit.audit_model', errors);

	return errors;
}

function lineCount(filePath) {
	const content = readFileSync(filePath, 'utf8');
	if (content.length === 0) return 0;
	const lines = content.split(/\r\n|\n|\r/);
	if (lines.at(-1) === '') lines.pop();
	return lines.length;
}

function evidenceLocations(report) {
	const locations = [];
	const audit = report.security_audit ?? {};

	for (const [factorIndex, factor] of (audit.risk_factor_evidence ?? []).entries()) {
		for (const [evidenceIndex, evidence] of (factor?.evidence ?? []).entries()) {
			locations.push({
				label: `security_audit.risk_factor_evidence[${factorIndex}].evidence[${evidenceIndex}]`,
				location: evidence,
			});
		}
	}

	for (const [findingIndex, finding] of (audit.static_findings ?? []).entries()) {
		locations.push({
			label: `security_audit.static_findings[${findingIndex}]`,
			location: finding,
		});
	}

	for (const field of [
		'semantic_findings',
		'critical_findings',
		'high_findings',
		'medium_findings',
		'low_findings',
		'dangerous_patterns',
	]) {
		for (const [findingIndex, finding] of (audit[field] ?? []).entries()) {
			for (const [locationIndex, location] of (finding?.locations ?? []).entries()) {
				locations.push({
					label: `security_audit.${field}[${findingIndex}].locations[${locationIndex}]`,
					location,
				});
			}
		}
	}

	return locations;
}

function validateEvidence(packageDir, report) {
	const errors = [];

	for (const { label, location } of evidenceLocations(report)) {
		const file = location?.file;
		const lineStart = location?.line_start;
		const lineEnd = location?.line_end;
		if (typeof file !== 'string' || file.trim() === '') {
			errors.push(`${label}.file is required`);
			continue;
		}
		if (isAbsolute(file)) {
			errors.push(`${label}: evidence path must be package-relative: ${file}`);
			continue;
		}

		const evidencePath = resolve(packageDir, file);
		if (!isWithin(packageDir, evidencePath)) {
			errors.push(`${label}: evidence path escapes the package: ${file}`);
			continue;
		}
		if (!existsSync(evidencePath)) {
			errors.push(`${label}: evidence file ${file} does not exist`);
			continue;
		}
		if (!statSync(evidencePath).isFile()) {
			errors.push(`${label}: evidence path ${file} is not a regular file`);
			continue;
		}
		if (!Number.isInteger(lineStart) || !Number.isInteger(lineEnd) || lineStart < 1 || lineEnd < lineStart) {
			errors.push(`${label}: invalid evidence line range ${lineStart}-${lineEnd}`);
			continue;
		}

		const lines = lineCount(evidencePath);
		if (lineEnd > lines) {
			errors.push(`${label}: evidence line range ${lineStart}-${lineEnd} exceeds ${file} (${lines} lines)`);
		}
	}

	return errors;
}

function validateAuditAttestation(packageDir, report, hashes) {
	const errors = [];
	const attestationPath = join(packageDir, ATTESTATION_FILENAME);
	if (!existsSync(attestationPath)) {
		return [`${attestationPath}: audit attestation is missing`];
	}

	let attestation;
	try {
		attestation = JSON.parse(readFileSync(attestationPath, 'utf8'));
	} catch (error) {
		return [`${attestationPath}: invalid JSON: ${error.message}`];
	}
	if (attestation?.schema_version !== '1.0') {
		errors.push(`${attestationPath}: schema_version must equal 1.0`);
	}
	if (attestation?.slug !== report.meta.slug) {
		errors.push(`${attestationPath}: slug must match the exact report slug`);
	}
	for (const field of ['content_hash', 'tree_hash']) {
		if (!HASH_PATTERN.test(attestation?.package?.[field] ?? '')) {
			errors.push(`${attestationPath}: package.${field} must be a SHA-256 hash`);
		}
	}
	if (attestation?.package?.content_hash !== hashes.contentHash) {
		errors.push(`${attestationPath}: package.content_hash does not match current SKILL.md`);
	}
	if (attestation?.package?.tree_hash !== hashes.treeHash) {
		errors.push(`${attestationPath}: package.tree_hash does not match current package tree`);
	}
	const reportDigest = sha256(readFileSync(join(packageDir, REPORT_FILENAME)));
	for (const field of ['input_digest', 'raw_audit_digest', 'final_digest']) {
		if (!HASH_PATTERN.test(attestation?.report?.[field] ?? '')) {
			errors.push(`${attestationPath}: report.${field} must be a SHA-256 hash`);
		}
	}
	if (attestation?.report?.final_digest !== reportDigest) {
		errors.push(`${attestationPath}: report.final_digest does not match skill-report.json`);
	}
	if (attestation?.report?.input_digest === attestation?.report?.raw_audit_digest) {
		errors.push(`${attestationPath}: audit invocation did not replace the input report`);
	}
	if (attestation?.producer?.repository !== 'aiskillstore/skillstore') {
		errors.push(`${attestationPath}: producer.repository must equal aiskillstore/skillstore`);
	}
	if (!/^[a-f0-9]{40}$/.test(attestation?.producer?.commit ?? '')) {
		errors.push(`${attestationPath}: producer.commit must be a full Git SHA`);
	}
	for (const field of ['package_version', 'audit_command_version']) {
		if (typeof attestation?.producer?.[field] !== 'string' || attestation.producer[field] === '') {
			errors.push(`${attestationPath}: producer.${field} is required`);
		}
	}
	const invocation = attestation?.invocation;
	if (!UUID_PATTERN.test(invocation?.id ?? '')) {
		errors.push(`${attestationPath}: invocation.id must be a UUID`);
	}
	for (const field of ['cwd', 'skills_root']) {
		if (typeof invocation?.[field] !== 'string' || invocation[field].trim() === '') {
			errors.push(`${attestationPath}: invocation.${field} is required`);
		} else if (!isAbsolute(invocation[field])) {
			errors.push(`${attestationPath}: invocation.${field} must be absolute`);
		}
	}
	if (
		!Array.isArray(invocation?.slugs)
		|| invocation.slugs.length === 0
		|| invocation.slugs.some((slug) => typeof slug !== 'string' || slug === '')
		|| new Set(invocation.slugs).size !== invocation.slugs.length
		|| !invocation.slugs.includes(report.meta.slug)
	) {
		errors.push(`${attestationPath}: invocation.slugs must contain the exact report slug`);
	}
	if (typeof invocation?.model !== 'string' || invocation.model.trim() === '') {
		errors.push(`${attestationPath}: invocation.model is required`);
	}
	if (report.meta?.provenance?.model_requested !== invocation?.model) {
		errors.push(`${attestationPath}: report producer model does not match invocation.model`);
	}
	for (const field of ['stdout_digest', 'stderr_digest']) {
		if (!HASH_PATTERN.test(invocation?.[field] ?? '')) {
			errors.push(`${attestationPath}: invocation.${field} must be a SHA-256 hash`);
		}
	}
	const canReconstructCommand = (
		typeof invocation?.cwd === 'string'
		&& invocation.cwd !== ''
		&& typeof invocation?.skills_root === 'string'
		&& invocation.skills_root !== ''
		&& Array.isArray(invocation?.slugs)
		&& typeof invocation?.model === 'string'
	);
	if (
		!Array.isArray(invocation?.command)
		|| invocation.command.length !== 11
		|| !canReconstructCommand
	) {
		errors.push(`${attestationPath}: invocation.command must record the exact argv`);
	} else {
		const expectedCommand = [
			invocation.command[0],
			'--import',
			'tsx',
			join(invocation.cwd, 'src', 'cli', 'index.ts'),
			'skill',
			'audit',
			relative(invocation.cwd, invocation.skills_root),
			'--slugs',
			invocation.slugs.join(','),
			'--model',
			invocation.model,
		];
		if (
			!isAbsolute(invocation.command[0])
			|| JSON.stringify(invocation.command) !== JSON.stringify(expectedCommand)
		) {
			errors.push(`${attestationPath}: invocation.command does not match model and slugs`);
		}
	}
	const startedAt = Date.parse(invocation?.started_at);
	const completedAt = Date.parse(invocation?.completed_at);
	const generatedAt = Date.parse(report.meta.generated_at);
	const auditedAt = Date.parse(report.security_audit.audited_at);
	if (!Number.isFinite(startedAt) || !Number.isFinite(completedAt) || startedAt > completedAt) {
		errors.push(`${attestationPath}: invocation timestamps are invalid`);
	} else {
		for (const [field, timestamp] of [
			['meta.generated_at', generatedAt],
			['security_audit.audited_at', auditedAt],
		]) {
			if (
				!Number.isFinite(timestamp)
				|| timestamp < startedAt
				|| timestamp > completedAt
			) {
				errors.push(`${attestationPath}: ${field} is outside the audit invocation window`);
			}
		}
	}
	return errors;
}

async function validateFreshness(packageDir, report, options = {}) {
	const errors = [];
	let hashes;
	try {
		hashes = await calculatePackageHashes(packageDir);
	} catch (error) {
		return [error.message];
	}

	const contentMatches = report.meta.content_hash === hashes.contentHash;
	const treeMatches = report.meta.tree_hash === hashes.treeHash;
	if (!contentMatches) {
		errors.push(
			`meta.content_hash does not match current SKILL.md: report=${report.meta.content_hash} current=${hashes.contentHash}`,
		);
	}
	if (!treeMatches) {
		errors.push(
			`meta.tree_hash does not match current package tree: report=${report.meta.tree_hash} current=${hashes.treeHash}`,
		);
	}
	const attestationExists = existsSync(join(packageDir, ATTESTATION_FILENAME));
	if (options.requireAuditAttestation || attestationExists) {
		errors.push(...validateAuditAttestation(packageDir, report, hashes));
	}
	return errors;
}

export async function validatePackage(packageDir, options = {}) {
	const absoluteDir = resolve(packageDir);
	const errors = [];
	const reportPath = join(absoluteDir, 'skill-report.json');
	const enforcePublicationPolicy = options.enforcePublicationPolicy !== false;

	if (!existsSync(join(absoluteDir, 'SKILL.md'))) {
		errors.push(`${absoluteDir}: SKILL.md is missing`);
	}
	if (!existsSync(reportPath)) {
		errors.push(`${absoluteDir}: skill-report.json is missing`);
		return { ok: false, packageDir: absoluteDir, errors };
	}

	let report;
	try {
		report = JSON.parse(readFileSync(reportPath, 'utf8'));
	} catch (error) {
		errors.push(`${reportPath}: invalid JSON: ${error.message}`);
		return { ok: false, packageDir: absoluteDir, errors };
	}

	errors.push(...validateRequiredGateFields(report).map((error) => `${reportPath}: ${error}`));
	if (errors.length === 0) {
		errors.push(...(await validateFreshness(absoluteDir, report, options)).map((error) => `${reportPath}: ${error}`));
		errors.push(...validateEvidence(absoluteDir, report).map((error) => `${reportPath}: ${error}`));
		errors.push(...(await scanMarkdownLinks(absoluteDir)).map((error) => `${reportPath}: ${error}`));
	}
	if (errors.length > 0 || !enforcePublicationPolicy) {
		return { ok: errors.length === 0, packageDir: absoluteDir, report, errors };
	}

	const slug = report.meta.slug;
	if (report.security_audit.is_blocked === true) {
		errors.push(`${slug}: is_blocked=true cannot be overridden and forbids publication or sync`);
		return { ok: false, packageDir: absoluteDir, report, errors };
	}

	if (report.security_audit.safe_to_publish === false) {
		const approvalDocument = options.approvalDocument ?? { schema_version: '2.0', approvals: [] };
		const approvalResult = await findHumanApproval(report, approvalDocument, options);
		errors.push(...approvalResult.errors);
		return {
			ok: errors.length === 0,
			packageDir: absoluteDir,
			report,
			approval: approvalResult.approval,
			errors,
		};
	}

	return { ok: true, packageDir: absoluteDir, report, errors };
}

function loadApprovalDocument(approvalsPath) {
	if (!existsSync(approvalsPath)) {
		throw new Error(`${approvalsPath}: approval document is missing`);
	}
	return JSON.parse(readFileSync(approvalsPath, 'utf8'));
}

function parseArguments(argv) {
	const options = {
		packageDirs: [],
		discoverRoots: [],
		approvalsPath: DEFAULT_APPROVALS_PATH,
		integrityOnly: false,
		changedSince: '',
	};

	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		if (arg === '--package') {
			options.packageDirs.push(argv[++index]);
		} else if (arg === '--discover') {
			options.discoverRoots.push(argv[++index]);
		} else if (arg === '--approvals') {
			options.approvalsPath = argv[++index];
		} else if (arg === '--integrity-only') {
			options.integrityOnly = true;
		} else if (arg === '--changed-since') {
			options.changedSince = argv[++index];
		} else if (arg === '--help' || arg === '-h') {
			options.help = true;
		} else {
			throw new Error(`Unknown argument: ${arg}`);
		}
	}

	for (const [name, values] of [
		['--package', options.packageDirs],
		['--discover', options.discoverRoots],
	]) {
		if (values.some((value) => !value)) throw new Error(`${name} requires a path`);
	}
	if (!options.approvalsPath) throw new Error('--approvals requires a path');
	if (argv.includes('--changed-since') && !options.changedSince) {
		throw new Error('--changed-since requires a git revision');
	}

	return options;
}

function inferPackageDir(changedPath, knownPackageDirs) {
	const absolutePath = resolve(changedPath);
	const containing = knownPackageDirs
		.filter((packageDir) => isWithin(packageDir, absolutePath))
		.sort((left, right) => right.length - left.length);
	if (containing.length > 0) return containing[0];

	const normalized = changedPath.split(sep).join('/');
	const parts = normalized.split('/').filter(Boolean);
	if (!['skills', 'pending'].includes(parts[0]) || parts.length < 2) return null;

	const flatDir = resolve(parts[0], parts[1]);
	if (existsSync(join(flatDir, 'SKILL.md')) || existsSync(join(flatDir, 'skill-report.json'))) {
		return flatDir;
	}
	if (parts.length >= 3) return resolve(parts[0], parts[1], parts[2]);
	return flatDir;
}

function parseNullSeparated(buffer) {
	return buffer.toString('utf8').split('\0').filter((value) => value !== '');
}

function gitTreePaths(revision) {
	const result = spawnSync(
		'git',
		['ls-tree', '-r', '-z', '--name-only', revision, '--', 'skills', 'pending'],
		{ maxBuffer: GIT_OUTPUT_BUFFER_BYTES },
	);
	if (result.status !== 0) {
		throw new Error(`git ls-tree ${revision} failed: ${result.stderr.toString('utf8').trim()}`);
	}
	return parseNullSeparated(result.stdout);
}

function packageDirsFromTreePaths(paths) {
	const reportDirs = paths
		.filter((path) => path.endsWith(`/${REPORT_FILENAME}`))
		.map((path) => dirname(path))
		.sort((left, right) => left.length - right.length || left.localeCompare(right));
	const skillDirs = paths
		.filter((path) => path.endsWith('/SKILL.md'))
		.map((path) => dirname(path))
		.sort((left, right) => left.length - right.length || left.localeCompare(right));
	const selected = [];

	for (const candidate of [...reportDirs, ...skillDirs]) {
		const absoluteDir = resolve(candidate);
		if (!selected.some((packageDir) => isWithin(packageDir, absoluteDir))) {
			selected.push(absoluteDir);
		}
	}
	return selected.sort((left, right) => left.localeCompare(right));
}

function changedPathsFromNameStatus(baseRevision) {
	const result = spawnSync(
		'git',
		['diff', '--name-status', '-z', '--find-renames', '--find-copies', baseRevision, 'HEAD'],
		{ maxBuffer: GIT_OUTPUT_BUFFER_BYTES },
	);
	if (result.status !== 0) {
		throw new Error(`git diff failed: ${result.stderr.toString('utf8').trim()}`);
	}
	const records = parseNullSeparated(result.stdout);
	const changedPaths = [];
	for (let index = 0; index < records.length;) {
		const status = records[index++];
		if (/^[RC][0-9]+$/.test(status)) {
			changedPaths.push(records[index++], records[index++]);
		} else {
			changedPaths.push(records[index++]);
		}
	}
	return changedPaths.filter(Boolean);
}

async function discoverChangedPackageDirs(baseRevision) {
	const changedPaths = changedPathsFromNameStatus(baseRevision);
	const basePaths = gitTreePaths(baseRevision);
	const currentPaths = gitTreePaths('HEAD');
	const knownPackageDirs = [
		...packageDirsFromTreePaths(basePaths),
		...packageDirsFromTreePaths(currentPaths),
		...(await discoverPackageDirs('skills')),
		...(await discoverPackageDirs('pending')),
	];
	const selected = new Set();

	for (const changedPath of changedPaths) {
		if (!changedPath.startsWith('skills/') && !changedPath.startsWith('pending/')) continue;
		const packageDir = inferPackageDir(changedPath, knownPackageDirs);
		if (!packageDir) continue;
		const relativePackage = relative(process.cwd(), packageDir).split(sep).join('/');
		const packageStillTracked = currentPaths.some((path) => (
			path === relativePackage || path.startsWith(`${relativePackage}/`)
		));
		if (packageStillTracked || existsSync(packageDir)) selected.add(packageDir);
	}

	return [...selected].sort((left, right) => left.localeCompare(right));
}

function printHelp() {
	console.log(`Usage:
  node scripts/validate-skill-publication.mjs --package <dir> [--package <dir> ...]
  node scripts/validate-skill-publication.mjs --discover <root>

Options:
  --approvals <file>   Repository-tracked approval document
  --integrity-only     Skip publication policy checks
  --changed-since <r>  Validate changed package roots since git revision
`);
}

async function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}
	const packageDirs = new Set(options.packageDirs.map((packageDir) => resolve(packageDir)));
	for (const rootDir of options.discoverRoots) {
		for (const packageDir of await discoverPackageDirs(rootDir)) {
			packageDirs.add(packageDir);
		}
	}
	if (options.changedSince) {
		for (const packageDir of await discoverChangedPackageDirs(options.changedSince)) {
			packageDirs.add(packageDir);
		}
	}
	if (packageDirs.size === 0) {
		console.log('No skill packages found for validation');
		return 0;
	}

	const approvalDocument = options.integrityOnly
		? { schema_version: '2.0', approvals: [] }
		: loadApprovalDocument(resolve(options.approvalsPath));
	let failed = false;

	for (const packageDir of [...packageDirs].sort()) {
		const result = await validatePackage(packageDir, {
			approvalDocument,
			enforcePublicationPolicy: !options.integrityOnly,
			githubRepository: process.env.GITHUB_REPOSITORY,
			githubToken: process.env.GH_TOKEN || process.env.GITHUB_TOKEN,
		});
		if (result.ok) {
			const approvalSuffix = result.approval ? ` (human override: ${result.approval.actor})` : '';
			console.log(`PASS ${relative(process.cwd(), packageDir)}${approvalSuffix}`);
		} else {
			failed = true;
			for (const error of result.errors) console.error(`ERROR ${error}`);
		}
	}

	return failed ? 1 : 0;
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
