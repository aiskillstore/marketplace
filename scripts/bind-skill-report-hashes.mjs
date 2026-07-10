#!/usr/bin/env node

import {
	existsSync,
	readFileSync,
	writeFileSync,
} from 'node:fs';
import {
	join,
	relative,
	resolve,
} from 'node:path';
import { pathToFileURL } from 'node:url';
import { calculatePackageHashes } from './validate-skill-publication.mjs';

const HASH_PATTERN = /^[a-f0-9]{64}$/;

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

function parseReport(reportPath, source) {
	let report;
	try {
		report = JSON.parse(source);
	} catch (error) {
		throw new Error(`${reportPath}: invalid JSON: ${error.message}`);
	}

	if (!report || typeof report !== 'object' || Array.isArray(report)) {
		throw new Error(`${reportPath}: skill-report.json must contain a JSON object`);
	}
	if (report.schema_version !== '2.0') {
		throw new Error(`${reportPath}: schema_version must equal 2.0`);
	}
	if (!report.meta || typeof report.meta !== 'object' || Array.isArray(report.meta)) {
		throw new Error(`${reportPath}: meta must be a JSON object`);
	}
	for (const field of ['content_hash', 'tree_hash']) {
		if (!HASH_PATTERN.test(report.meta[field] ?? '')) {
			throw new Error(
				`${reportPath}: meta.${field} must be a 64-character lowercase SHA-256 hash`,
			);
		}
	}

	let spans;
	try {
		spans = locateMetaHashSpans(source);
	} catch (error) {
		throw new Error(`${reportPath}: ${error.message}`);
	}

	return spans;
}

function replaceHashSpans(source, spans, hashes) {
	const replacements = [
		{ ...spans.content_hash, value: hashes.contentHash },
		{ ...spans.tree_hash, value: hashes.treeHash },
	].sort((left, right) => right.contentStart - left.contentStart);
	let updated = source;

	for (const replacement of replacements) {
		updated = [
			updated.slice(0, replacement.contentStart),
			replacement.value,
			updated.slice(replacement.contentEnd),
		].join('');
	}

	return updated;
}

export async function preparePackageHashBinding(packageDir) {
	const absoluteDir = resolve(packageDir);
	const reportPath = join(absoluteDir, 'skill-report.json');
	if (!existsSync(reportPath)) {
		throw new Error(`${reportPath}: skill-report.json is missing`);
	}

	const source = readFileSync(reportPath, 'utf8');
	const spans = parseReport(reportPath, source);
	const hashes = await calculatePackageHashes(absoluteDir);
	const updated = replaceHashSpans(source, spans, hashes);

	return {
		absoluteDir,
		changed: updated !== source,
		reportPath,
		updated,
	};
}

function parseArguments(argv) {
	const packageDirs = [];
	let help = false;

	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		if (arg === '--package') {
			const packageDir = argv[++index];
			if (!packageDir || packageDir.startsWith('--')) {
				throw new Error('--package requires a path');
			}
			packageDirs.push(packageDir);
		} else if (arg === '--help' || arg === '-h') {
			help = true;
		} else {
			throw new Error(`Unknown argument: ${arg}`);
		}
	}

	if (!help && packageDirs.length === 0) {
		throw new Error('at least one --package path is required');
	}
	return { help, packageDirs };
}

function printHelp() {
	console.log(`Usage:
  node scripts/bind-skill-report-hashes.mjs --package <dir> [--package <dir> ...]
`);
}

async function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}

	const packageDirs = [...new Set(options.packageDirs.map((packageDir) => resolve(packageDir)))]
		.sort((left, right) => left.localeCompare(right));
	const prepared = [];
	for (const packageDir of packageDirs) {
		prepared.push(await preparePackageHashBinding(packageDir));
	}

	for (const binding of prepared) {
		if (binding.changed) writeFileSync(binding.reportPath, binding.updated, 'utf8');
		const status = binding.changed ? 'UPDATED' : 'UNCHANGED';
		console.log(`${status} ${relative(process.cwd(), binding.absoluteDir)}`);
	}

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
