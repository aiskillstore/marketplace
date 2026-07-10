#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
	existsSync,
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

const HASH_PATTERN = /^[a-f0-9]{64}$/;
const APPROVAL_SCOPE = 'safe_to_publish';
const DEFAULT_APPROVALS_PATH = '.github/skill-publish-approvals.json';
const WRITE_PERMISSIONS = new Set(['write', 'maintain', 'admin']);

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
		const entries = readdirSync(dir, { withFileTypes: true })
			.sort((left, right) => left.name.localeCompare(right.name));

		for (const entry of entries) {
			const fullPath = join(dir, entry.name);
			const relativePath = relative(packageDir, fullPath);

			if (entry.isSymbolicLink()) {
				throw new Error(`${relativePath}: symbolic links are not allowed in skill packages`);
			}
			if (entry.isDirectory()) {
				walk(fullPath);
			} else if (entry.isFile()) {
				if (entry.name !== 'skill-report.json') files.push(fullPath);
			} else {
				throw new Error(`${relativePath}: non-regular package entries are not allowed`);
			}
		}
	}

	walk(packageDir);
	return files;
}

function markdownDestinations(content) {
	const destinations = [];
	const withoutFencedCode = content.replace(
		/^[ \t]*(`{3,}|~{3,})[^\n]*\n[\s\S]*?^[ \t]*\1[ \t]*$/gm,
		'',
	);
	const inlineLinkPattern = /!?\[[^\]]*\]\(\s*(?:<([^>\n]+)>|([^)\s]+))(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?\s*\)/g;
	const referenceDefinitionPattern = /^[ \t]{0,3}\[[^\]]+\]:[ \t]*(?:<([^>\n]+)>|(\S+))/gm;

	for (const pattern of [inlineLinkPattern, referenceDefinitionPattern]) {
		for (const match of withoutFencedCode.matchAll(pattern)) {
			destinations.push(match[1] ?? match[2]);
		}
	}

	return destinations;
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
		return `${relativePath}:${sha256(readFileSync(filePath))}`;
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

function validateApprovalDocument(approvalDocument) {
	const errors = [];
	if (!approvalDocument || typeof approvalDocument !== 'object' || Array.isArray(approvalDocument)) {
		return ['approval document must be a JSON object'];
	}
	if (approvalDocument.schema_version !== '1.0') {
		errors.push('approval document schema_version must equal 1.0');
	}
	if (!Array.isArray(approvalDocument.approvals)) {
		errors.push('approval document approvals must be an array');
		return errors;
	}
	for (const [index, approval] of approvalDocument.approvals.entries()) {
		const field = `approvals[${index}].evidence_url`;
		if (!requiredString(approval?.evidence_url, field, errors)) continue;
		try {
			parseIssueCommentEvidenceUrl(approval.evidence_url);
		} catch (error) {
			errors.push(`${field}: ${error.message}`);
		}
	}
	return errors;
}

function parseIssueCommentEvidenceUrl(value) {
	let url;
	try {
		url = new URL(value);
	} catch {
		throw new Error('approval.evidence_url must be a valid GitHub issue-comment URL');
	}

	const pathMatch = url.pathname.match(/^\/([^/]+)\/([^/]+)\/issues\/([1-9][0-9]*)$/);
	const commentMatch = url.hash.match(/^#issuecomment-([1-9][0-9]*)$/);
	if (
		url.protocol !== 'https:'
		|| url.hostname !== 'github.com'
		|| url.username !== ''
		|| url.password !== ''
		|| url.search !== ''
		|| !pathMatch
		|| !commentMatch
	) {
		throw new Error('approval.evidence_url must be a GitHub issue-comment URL');
	}

	return {
		owner: pathMatch[1],
		repo: pathMatch[2],
		issueNumber: pathMatch[3],
		commentId: commentMatch[1],
		url: url.href,
	};
}

function createGitHubRequest({ token, fetchImpl }) {
	return async (apiPath) => {
		if (typeof token !== 'string' || token.trim() === '') {
			throw new Error('GH_TOKEN or GITHUB_TOKEN is required to verify publication approval');
		}
		if (typeof fetchImpl !== 'function') {
			throw new Error('GitHub API fetch implementation is unavailable');
		}

		const response = await fetchImpl(`https://api.github.com${apiPath}`, {
			headers: {
				Accept: 'application/vnd.github+json',
				Authorization: `Bearer ${token}`,
				'X-GitHub-Api-Version': '2022-11-28',
			},
		});
		if (!response?.ok) {
			throw new Error(`GitHub API request failed with status ${response?.status ?? 'unknown'}`);
		}
		try {
			return await response.json();
		} catch {
			throw new Error('GitHub API returned invalid JSON');
		}
	};
}

async function verifyApprovalEvidence(report, approval, options) {
	const slug = report.meta.slug;
	const errors = [];
	let evidence;
	try {
		evidence = parseIssueCommentEvidenceUrl(approval.evidence_url);
	} catch (error) {
		return [`${slug}: ${error.message}`];
	}

	const githubRepository = options.githubRepository ?? process.env.GITHUB_REPOSITORY ?? '';
	if (typeof githubRepository !== 'string' || !/^[^/]+\/[^/]+$/.test(githubRepository)) {
		return [`${slug}: GITHUB_REPOSITORY is required to verify approval evidence`];
	}
	const evidenceRepository = `${evidence.owner}/${evidence.repo}`;
	if (evidenceRepository.toLowerCase() !== githubRepository.toLowerCase()) {
		return [
			`${slug}: approval.evidence_url must reference the publication repository ${githubRepository}`,
		];
	}

	const githubRequest = options.githubRequest ?? createGitHubRequest({
		token: Object.hasOwn(options, 'githubToken')
			? options.githubToken
			: (process.env.GH_TOKEN || process.env.GITHUB_TOKEN || ''),
		fetchImpl: options.fetchImpl ?? globalThis.fetch,
	});

	let comment;
	try {
		comment = await githubRequest(
			`/repos/${evidenceRepository}/issues/comments/${evidence.commentId}`,
		);
	} catch (error) {
		return [`${slug}: GitHub comment verification failed: ${error.message}`];
	}

	if (comment?.id !== Number(evidence.commentId) || comment?.html_url !== approval.evidence_url) {
		errors.push(`${slug}: GitHub comment does not match approval.evidence_url`);
	}
	if (comment?.user?.login !== approval.actor) {
		errors.push(`${slug}: GitHub comment author login must match approval.actor`);
	}
	if (comment?.user?.type !== 'User') {
		errors.push(`${slug}: GitHub comment author user.type must be exactly User`);
	}
	if (comment?.created_at !== approval.approved_at) {
		errors.push(`${slug}: GitHub comment created_at must match approval.approved_at`);
	}

	const normalizedBody = typeof comment?.body === 'string'
		? comment.body.replace(/\r\n?/g, '\n')
		: '';
	const [commandLine = '', ...reasonLines] = normalizedBody.split('\n');
	const expectedCommand = `/approve safe-to-publish ${slug}`;
	if (commandLine.trim() !== expectedCommand) {
		errors.push(`${slug}: GitHub comment must explicitly approve safe-to-publish for the exact report slug`);
	}
	const recordedReason = approval.reason.trim();
	if (!reasonLines.join('\n').includes(recordedReason)) {
		errors.push(`${slug}: GitHub comment must contain the recorded approval reason`);
	}
	if (errors.length > 0) return errors;

	let permission;
	try {
		permission = await githubRequest(
			`/repos/${evidenceRepository}/collaborators/${encodeURIComponent(approval.actor)}/permission`,
		);
	} catch (error) {
		return [`${slug}: GitHub collaborator permission verification failed: ${error.message}`];
	}
	if (!WRITE_PERMISSIONS.has(permission?.permission)) {
		errors.push(`${slug}: approval actor must have write, maintain, or admin collaborator permission`);
	}
	return errors;
}

async function findHumanApproval(report, approvalDocument, options) {
	const documentErrors = validateApprovalDocument(approvalDocument);
	if (documentErrors.length > 0) return { errors: documentErrors };

	const slug = report.meta.slug;
	const matching = approvalDocument.approvals.filter((approval) => (
		approval?.slug === slug
		&& approval?.content_hash === report.meta.content_hash
		&& approval?.tree_hash === report.meta.tree_hash
		&& approval?.scope === APPROVAL_SCOPE
	));

	if (matching.length === 0) {
		return {
			errors: [
				`${slug}: safe_to_publish=false requires a repository-tracked human approval bound to the current content_hash and tree_hash`,
			],
		};
	}
	if (matching.length > 1) {
		return {
			errors: [
				`${slug}: multiple matching safe_to_publish approval records are not allowed`,
			],
		};
	}

	const approval = matching[0];
	const invalidErrors = [];
	requiredString(approval.actor, 'approval.actor', invalidErrors);
	requiredString(approval.approved_at, 'approval.approved_at', invalidErrors);
	const approvedAt = Date.parse(approval.approved_at);
	if (typeof approval.approved_at === 'string' && !Number.isFinite(approvedAt)) {
		invalidErrors.push(`${slug}: approval.approved_at must be an ISO 8601 timestamp`);
	} else if (Number.isFinite(approvedAt) && approvedAt > Date.now() + 5 * 60 * 1000) {
		invalidErrors.push(`${slug}: approval.approved_at cannot be in the future`);
	}
	requiredString(approval.reason, 'approval.reason', invalidErrors);
	if (typeof approval.reason === 'string' && approval.reason.trim().length < 20) {
		invalidErrors.push(`${slug}: approval.reason must contain at least 20 characters`);
	}
	requiredString(approval.evidence_url, 'approval.evidence_url', invalidErrors);
	if (invalidErrors.length > 0) return { errors: invalidErrors };

	const evidenceErrors = await verifyApprovalEvidence(report, approval, options);
	if (evidenceErrors.length > 0) return { errors: evidenceErrors };
	return { approval, errors: [] };
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

async function validateFreshness(packageDir, report) {
	const errors = [];
	let hashes;
	try {
		hashes = await calculatePackageHashes(packageDir);
	} catch (error) {
		return [error.message];
	}

	if (report.meta.content_hash !== hashes.contentHash) {
		errors.push(
			`meta.content_hash does not match current SKILL.md: report=${report.meta.content_hash} current=${hashes.contentHash}`,
		);
	}
	if (report.meta.tree_hash !== hashes.treeHash) {
		errors.push(
			`meta.tree_hash does not match current package tree: report=${report.meta.tree_hash} current=${hashes.treeHash}`,
		);
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
		errors.push(...(await validateFreshness(absoluteDir, report)).map((error) => `${reportPath}: ${error}`));
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
		const approvalDocument = options.approvalDocument ?? { schema_version: '1.0', approvals: [] };
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

async function discoverChangedPackageDirs(baseRevision) {
	const result = spawnSync('git', ['diff', '--name-only', '--diff-filter=ACMRT', baseRevision, 'HEAD'], {
		encoding: 'utf8',
	});
	if (result.status !== 0) {
		throw new Error(`git diff failed: ${result.stderr.trim()}`);
	}

	const changedPaths = result.stdout.split('\n').map((value) => value.trim()).filter(Boolean);
	const knownPackageDirs = [
		...(await discoverPackageDirs('skills')),
		...(await discoverPackageDirs('pending')),
	];
	const selected = new Set();

	for (const changedPath of changedPaths) {
		if (!changedPath.startsWith('skills/') && !changedPath.startsWith('pending/')) continue;
		const packageDir = inferPackageDir(changedPath, knownPackageDirs);
		if (packageDir && existsSync(packageDir)) selected.add(packageDir);
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
		? { schema_version: '1.0', approvals: [] }
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
