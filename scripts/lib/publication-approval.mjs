const APPROVAL_SCOPE = 'safe_to_publish';
const APPROVAL_SCHEMA_VERSION = '2.0';
const APPROVAL_TTL_MS = 30 * 24 * 60 * 60 * 1000;
const CLOCK_SKEW_MS = 5 * 60 * 1000;
const HASH_PATTERN = /^[a-f0-9]{64}$/;
const SHA_PATTERN = /^[a-f0-9]{40}$/;
const UUID_PATTERN = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const WRITE_PERMISSIONS = new Set(['write', 'maintain', 'admin']);
const ACTIVE_APPROVAL_LABELS = new Set(['pending-approval', 'processing']);
const APPROVAL_ARTIFACT_PATH = '.github/skill-publish-approvals.json';

function requiredString(value, field, errors) {
	if (typeof value !== 'string' || value.trim() === '') {
		errors.push(`${field} is required`);
		return false;
	}
	return true;
}

function requiredInteger(value, field, errors) {
	if (!Number.isSafeInteger(value) || value < 1) {
		errors.push(`${field} must be a positive integer`);
		return false;
	}
	return true;
}

function validateTimestamp(value, field, errors) {
	if (!requiredString(value, field, errors)) return NaN;
	const timestamp = Date.parse(value);
	if (!Number.isFinite(timestamp)) errors.push(`${field} must be an ISO 8601 timestamp`);
	return timestamp;
}

function normalizedRepository(value) {
	return typeof value === 'string' ? value.trim().toLowerCase() : '';
}

function normalizeSourceUrl(value) {
	if (typeof value !== 'string') return '';
	return value.trim().replace(/\.git$/i, '').replace(/\/$/, '');
}

function isBotLogin(login) {
	return typeof login !== 'string'
		|| login.toLowerCase() === 'ai-skill-store[bot]'
		|| /\[bot\]$/i.test(login);
}

function parseGitHubUrl(value, pattern, label) {
	let url;
	try {
		url = new URL(value);
	} catch {
		throw new Error(`${label} must be a valid GitHub URL`);
	}
	const match = url.pathname.match(pattern);
	if (
		url.protocol !== 'https:'
		|| url.hostname !== 'github.com'
		|| url.username !== ''
		|| url.password !== ''
		|| url.search !== ''
		|| !match
	) {
		throw new Error(`${label} must be a valid GitHub URL`);
	}
	return { match, url };
}

export function parseIssueCommentUrl(value) {
	const { match, url } = parseGitHubUrl(
		value,
		/^\/([^/]+)\/([^/]+)\/issues\/([1-9][0-9]*)$/,
		'approval.approval_comment_url',
	);
	const commentMatch = url.hash.match(/^#issuecomment-([1-9][0-9]*)$/);
	if (!commentMatch) {
		throw new Error('approval.approval_comment_url must include an issuecomment fragment');
	}
	return {
		owner: match[1],
		repo: match[2],
		issueNumber: Number(match[3]),
		commentId: Number(commentMatch[1]),
		url: url.href,
	};
}

function parseIssueUrl(value) {
	const { match, url } = parseGitHubUrl(
		value,
		/^\/([^/]+)\/([^/]+)\/issues\/([1-9][0-9]*)$/,
		'approval.approval_issue_url',
	);
	if (url.hash !== '') throw new Error('approval.approval_issue_url must not contain a fragment');
	return {
		owner: match[1],
		repo: match[2],
		issueNumber: Number(match[3]),
		url: url.href,
	};
}

function parsePullUrl(value) {
	const { match, url } = parseGitHubUrl(
		value,
		/^\/([^/]+)\/([^/]+)\/pull\/([1-9][0-9]*)$/,
		'approval.pr_url',
	);
	if (url.hash !== '') throw new Error('approval.pr_url must not contain a fragment');
	return {
		owner: match[1],
		repo: match[2],
		prNumber: Number(match[3]),
		url: url.href,
	};
}

function validateApprovalRecord(approval, index, errors) {
	const prefix = `approvals[${index}]`;
	if (!approval || typeof approval !== 'object' || Array.isArray(approval)) {
		errors.push(`${prefix} must be an object`);
		return;
	}

	for (const field of [
		'slug',
		'content_hash',
		'tree_hash',
		'submission_id',
		'submission_source_url',
		'approval_issue_url',
		'approval_comment_url',
		'actor',
		'created_at',
		'updated_at',
		'expires_at',
		'reason',
		'pr_url',
		'pr_base_sha',
		'pr_head_ref',
		'pr_head_sha',
		'scope',
	]) {
		requiredString(approval[field], `${prefix}.${field}`, errors);
	}
	requiredInteger(approval.approval_issue_number, `${prefix}.approval_issue_number`, errors);
	requiredInteger(approval.approval_comment_id, `${prefix}.approval_comment_id`, errors);
	requiredInteger(approval.pr_number, `${prefix}.pr_number`, errors);

	if (typeof approval.content_hash === 'string' && !HASH_PATTERN.test(approval.content_hash)) {
		errors.push(`${prefix}.content_hash must be a lowercase SHA-256 hash`);
	}
	if (typeof approval.tree_hash === 'string' && !HASH_PATTERN.test(approval.tree_hash)) {
		errors.push(`${prefix}.tree_hash must be a lowercase SHA-256 hash`);
	}
	if (typeof approval.submission_id === 'string' && !UUID_PATTERN.test(approval.submission_id)) {
		errors.push(`${prefix}.submission_id must be a UUID`);
	}
	for (const field of ['pr_base_sha', 'pr_head_sha']) {
		if (typeof approval[field] === 'string' && !SHA_PATTERN.test(approval[field])) {
			errors.push(`${prefix}.${field} must be a lowercase 40-character Git SHA`);
		}
	}
	if (approval.scope !== APPROVAL_SCOPE) {
		errors.push(`${prefix}.scope must equal ${APPROVAL_SCOPE}`);
	}
	if (typeof approval.reason === 'string' && approval.reason.trim().length < 20) {
		errors.push(`${prefix}.reason must contain at least 20 characters`);
	}

	let comment;
	let issue;
	let pull;
	try {
		comment = parseIssueCommentUrl(approval.approval_comment_url);
	} catch (error) {
		errors.push(`${prefix}.approval_comment_url: ${error.message}`);
	}
	try {
		issue = parseIssueUrl(approval.approval_issue_url);
	} catch (error) {
		errors.push(`${prefix}.approval_issue_url: ${error.message}`);
	}
	try {
		pull = parsePullUrl(approval.pr_url);
	} catch (error) {
		errors.push(`${prefix}.pr_url: ${error.message}`);
	}
	if (comment && issue) {
		if (
			comment.owner.toLowerCase() !== issue.owner.toLowerCase()
			|| comment.repo.toLowerCase() !== issue.repo.toLowerCase()
			|| comment.issueNumber !== issue.issueNumber
		) {
			errors.push(`${prefix}: approval comment and issue URLs must identify the same issue`);
		}
		if (comment.issueNumber !== approval.approval_issue_number) {
			errors.push(`${prefix}.approval_issue_number must match the approval URLs`);
		}
		if (comment.commentId !== approval.approval_comment_id) {
			errors.push(`${prefix}.approval_comment_id must match approval_comment_url`);
		}
	}
	if (issue && pull && (
		issue.owner.toLowerCase() !== pull.owner.toLowerCase()
		|| issue.repo.toLowerCase() !== pull.repo.toLowerCase()
	)) {
		errors.push(`${prefix}: approval issue and PR must be in the same repository`);
	}
	if (pull && pull.prNumber !== approval.pr_number) {
		errors.push(`${prefix}.pr_number must match pr_url`);
	}
}

export function validateApprovalDocument(approvalDocument) {
	const errors = [];
	if (!approvalDocument || typeof approvalDocument !== 'object' || Array.isArray(approvalDocument)) {
		return ['approval document must be a JSON object'];
	}
	if (approvalDocument.schema_version !== APPROVAL_SCHEMA_VERSION) {
		errors.push(`approval document schema_version must equal ${APPROVAL_SCHEMA_VERSION}`);
	}
	if (!Array.isArray(approvalDocument.approvals)) {
		errors.push('approval document approvals must be an array');
		return errors;
	}
	for (const [index, approval] of approvalDocument.approvals.entries()) {
		validateApprovalRecord(approval, index, errors);
	}
	return errors;
}

export function createGitHubRequest({ token, fetchImpl }) {
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

function extractSubmissionIdentity(body) {
	if (typeof body !== 'string') return { sourceUrl: '', submissionId: '' };
	const submission = body.match(
		/\*\*Submission ID\*\*:\s*`([a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12})`/i,
	);
	const source = body.match(
		/\*\*Source\*\*:\s*(?:\[[^\]]*\]\()?((?:https:\/\/github\.com\/)[^\s)]+)/i,
	);
	return {
		sourceUrl: normalizeSourceUrl(source?.[1] ?? ''),
		submissionId: (submission?.[1] ?? '').toLowerCase(),
	};
}

function validateLiveTimestamps(approval, now, errors) {
	const createdAt = validateTimestamp(approval.created_at, 'approval.created_at', errors);
	const updatedAt = validateTimestamp(approval.updated_at, 'approval.updated_at', errors);
	const expiresAt = validateTimestamp(approval.expires_at, 'approval.expires_at', errors);
	if (![createdAt, updatedAt, expiresAt].every(Number.isFinite)) return;
	if (createdAt > now + CLOCK_SKEW_MS) errors.push('approval.created_at cannot be in the future');
	if (updatedAt !== createdAt) errors.push('approval comment was edited: updated_at must equal created_at');
	if (expiresAt <= now) errors.push('approval has expired');
	if (expiresAt <= createdAt) errors.push('approval.expires_at must be after created_at');
	if (expiresAt - createdAt > APPROVAL_TTL_MS) {
		errors.push('approval.expires_at may be at most 30 days after created_at');
	}
}

export async function verifyTrackedApproval(report, approval, options = {}) {
	const slug = report.meta.slug;
	const errors = [];
	validateApprovalRecord(approval, 0, errors);
	if (errors.length > 0) return errors.map((error) => error.replace(/^approvals\[0\]/, 'approval'));

	if (
		approval.slug !== slug
		|| approval.content_hash !== report.meta.content_hash
		|| approval.tree_hash !== report.meta.tree_hash
		|| approval.scope !== APPROVAL_SCOPE
	) {
		return [`${slug}: approval must bind the exact slug, content_hash, tree_hash, and scope`];
	}
	if (report.security_audit?.is_blocked === true) {
		return [`${slug}: is_blocked=true cannot be overridden`];
	}

	const now = Number.isFinite(options.now) ? options.now : Date.now();
	validateLiveTimestamps(approval, now, errors);
	if (isBotLogin(approval.actor)) errors.push(`${slug}: bot actors cannot approve publication`);
	if (errors.length > 0) return errors;

	const evidence = parseIssueCommentUrl(approval.approval_comment_url);
	const evidenceRepository = `${evidence.owner}/${evidence.repo}`;
	const githubRepository = options.githubRepository ?? process.env.GITHUB_REPOSITORY ?? '';
	if (!/^[^/]+\/[^/]+$/.test(githubRepository)) {
		return [`${slug}: GITHUB_REPOSITORY is required to verify approval evidence`];
	}
	if (normalizedRepository(evidenceRepository) !== normalizedRepository(githubRepository)) {
		return [
			`${slug}: approval evidence must reference the publication repository ${githubRepository}`,
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
			`/repos/${evidenceRepository}/issues/comments/${approval.approval_comment_id}`,
		);
	} catch (error) {
		return [`${slug}: GitHub comment verification failed: ${error.message}`];
	}
	const expectedIssueApiUrl = `https://api.github.com/repos/${evidenceRepository}/issues/${approval.approval_issue_number}`;
	if (
		comment?.id !== approval.approval_comment_id
		|| comment?.html_url !== approval.approval_comment_url
		|| comment?.issue_url !== expectedIssueApiUrl
	) {
		errors.push(`${slug}: GitHub comment must belong to the exact approval issue and comment id`);
	}
	if (comment?.user?.login !== approval.actor) {
		errors.push(`${slug}: GitHub comment author login must match approval.actor`);
	}
	if (comment?.user?.type !== 'User' || isBotLogin(comment?.user?.login)) {
		errors.push(`${slug}: GitHub comment author must be a human User, never a Bot`);
	}
	if (comment?.created_at !== approval.created_at) {
		errors.push(`${slug}: GitHub comment created_at must match the approval record`);
	}
	if (comment?.updated_at !== approval.updated_at || comment?.updated_at !== comment?.created_at) {
		errors.push(`${slug}: GitHub approval comment was edited`);
	}
	const normalizedBody = typeof comment?.body === 'string'
		? comment.body.replace(/\r\n?/g, '\n')
		: '';
	const [commandLine = '', ...reasonLines] = normalizedBody.split('\n');
	if (commandLine.trim() !== `/approve safe-to-publish ${slug}`) {
		errors.push(`${slug}: GitHub comment must approve safe-to-publish for the exact report slug`);
	}
	if (reasonLines.join('\n').trim() !== approval.reason) {
		errors.push(`${slug}: GitHub comment reason must exactly equal the complete recorded reason`);
	}
	if (errors.length > 0) return errors;

	let issue;
	try {
		issue = await githubRequest(
			`/repos/${evidenceRepository}/issues/${approval.approval_issue_number}`,
		);
	} catch (error) {
		return [`${slug}: GitHub approval issue verification failed: ${error.message}`];
	}
	if (
		issue?.number !== approval.approval_issue_number
		|| issue?.html_url !== approval.approval_issue_url
		|| issue?.pull_request
	) {
		errors.push(`${slug}: approval record must reference the exact non-PR approval issue`);
	}
	if (issue?.state !== 'open') errors.push(`${slug}: approval issue must remain open`);
	const labels = new Set((issue?.labels ?? []).map((label) => (
		typeof label === 'string' ? label : label?.name
	)));
	if (![...ACTIVE_APPROVAL_LABELS].some((label) => labels.has(label))) {
		errors.push(`${slug}: approval issue must retain pending-approval or processing state`);
	}
	const issueIdentity = extractSubmissionIdentity(issue?.body);
	if (issueIdentity.submissionId !== approval.submission_id.toLowerCase()) {
		errors.push(`${slug}: approval issue submission id does not match the tracked submission`);
	}
	if (issueIdentity.sourceUrl !== normalizeSourceUrl(approval.submission_source_url)) {
		errors.push(`${slug}: approval issue source does not match the tracked submission`);
	}
	if (errors.length > 0) return errors;

	let pullRequest;
	try {
		pullRequest = await githubRequest(
			`/repos/${evidenceRepository}/pulls/${approval.pr_number}`,
		);
	} catch (error) {
		return [`${slug}: GitHub PR verification failed: ${error.message}`];
	}
	if (pullRequest?.number !== approval.pr_number || pullRequest?.html_url !== approval.pr_url) {
		errors.push(`${slug}: approval record must reference the exact submission PR`);
	}
	const mergedAt = pullRequest?.merged_at;
	const isOpenPullRequest = pullRequest?.state === 'open';
	const isMergedPullRequest = (
		pullRequest?.state === 'closed'
		&& pullRequest?.merged === true
		&& typeof mergedAt === 'string'
		&& mergedAt.trim() !== ''
	);
	if (!isOpenPullRequest && !isMergedPullRequest) {
		errors.push(`${slug}: submission PR must be open or closed with merged=true and merged_at`);
	}
	if (pullRequest?.base?.sha !== approval.pr_base_sha) {
		errors.push(`${slug}: submission PR base SHA does not match approval.pr_base_sha`);
	}
	if (pullRequest?.head?.ref !== approval.pr_head_ref) {
		errors.push(`${slug}: submission PR head ref does not match approval.pr_head_ref`);
	}
	const prIdentity = extractSubmissionIdentity(pullRequest?.body);
	if (prIdentity.submissionId !== approval.submission_id.toLowerCase()) {
		errors.push(`${slug}: submission PR body has the wrong submission id`);
	}
	if (prIdentity.sourceUrl !== normalizeSourceUrl(approval.submission_source_url)) {
		errors.push(`${slug}: submission PR body has the wrong source`);
	}
	if (errors.length > 0) return errors;

	let commits;
	try {
		commits = await githubRequest(
			`/repos/${evidenceRepository}/pulls/${approval.pr_number}/commits?per_page=100`,
		);
	} catch (error) {
		return [`${slug}: GitHub PR commit verification failed: ${error.message}`];
	}
	if (!Array.isArray(commits) || !commits.some((commit) => commit?.sha === approval.pr_head_sha)) {
		errors.push(`${slug}: approved PR head commit is not part of the exact submission PR`);
	}

	const liveHeadSha = pullRequest?.head?.sha;
	if (!SHA_PATTERN.test(liveHeadSha ?? '')) {
		errors.push(`${slug}: submission PR head SHA is missing or invalid`);
	} else if (liveHeadSha !== approval.pr_head_sha) {
		let comparison;
		try {
			comparison = await githubRequest(
				`/repos/${evidenceRepository}/compare/${approval.pr_head_sha}...${liveHeadSha}`,
			);
		} catch (error) {
			return [`${slug}: GitHub PR head comparison failed: ${error.message}`];
		}
		const changedFiles = Array.isArray(comparison?.files)
			? comparison.files.map((file) => file?.filename)
			: [];
		const comparedCommits = Array.isArray(comparison?.commits)
			? comparison.commits.map((commit) => commit?.sha)
			: [];
		if (
			comparison?.status !== 'ahead'
			|| comparison?.ahead_by !== 1
			|| comparison?.behind_by !== 0
			|| comparison?.total_commits !== 1
			|| comparison?.base_commit?.sha !== approval.pr_head_sha
			|| comparison?.merge_base_commit?.sha !== approval.pr_head_sha
			|| comparedCommits.length !== 1
			|| comparedCommits[0] !== liveHeadSha
			|| changedFiles.length !== 1
			|| changedFiles[0] !== APPROVAL_ARTIFACT_PATH
		) {
			errors.push(
				`${slug}: PR head must be exactly one descendant approval commit changing only ${APPROVAL_ARTIFACT_PATH}`,
			);
		}
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

export async function findHumanApproval(report, approvalDocument, options = {}) {
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
				`${slug}: safe_to_publish=false requires a repository-tracked human approval bound to the current slug, content_hash, tree_hash, submission, and PR head`,
			],
		};
	}
	if (matching.length > 1) {
		return {
			errors: [`${slug}: multiple matching safe_to_publish approval records are not allowed`],
		};
	}

	const approval = matching[0];
	const evidenceErrors = await verifyTrackedApproval(report, approval, options);
	if (evidenceErrors.length > 0) return { errors: evidenceErrors };
	return { approval, errors: [] };
}

export function approvalExpiry(createdAt) {
	return new Date(Date.parse(createdAt) + APPROVAL_TTL_MS).toISOString();
}

export const approvalConstants = {
	artifactPath: APPROVAL_ARTIFACT_PATH,
	schemaVersion: APPROVAL_SCHEMA_VERSION,
	scope: APPROVAL_SCOPE,
};
