#!/usr/bin/env node

import { createHash, randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";

const DEFAULT_DECK_PATH = fileURLToPath(new URL("../assets/deck.json", import.meta.url));
const SCHEMA_VERSION = "1.0";

export const SPREADS = Object.freeze({
  daily: ["Theme for reflection"],
  "three-card": ["Past or background", "Present dynamic", "Future tendency"],
  decision: ["Situation", "Option A", "Option B", "What to consider", "Grounded next step"],
  relationship: ["You", "Other person or perceived dynamic", "Connection", "Strength", "Challenge", "Constructive next step"],
  "celtic-cross": [
    "Present situation",
    "Challenge or crossing influence",
    "Foundation",
    "Recent past",
    "Conscious aim or possibility",
    "Near-term direction",
    "Your stance",
    "Environment or external influences",
    "Hopes and fears",
    "Outcome tendency",
  ],
  "yes-no": ["Symbolic tendency"],
});

function normalize(value) {
  return String(value)
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function comparableNames(value) {
  const normalized = normalize(value);
  return new Set([normalized, normalized.replace(/^the\s+/, "")]);
}

export function loadDeck(path = DEFAULT_DECK_PATH) {
  const raw = readFileSync(path, "utf8");
  const parsed = JSON.parse(raw);
  return { ...parsed, _path: path, _sha256: createHash("sha256").update(raw).digest("hex") };
}

export function validateDeck(deck) {
  const errors = [];
  if (!Array.isArray(deck.cards)) errors.push("cards must be an array");
  if (deck.count !== deck.cards?.length) errors.push("count must equal cards.length");
  if (deck.cards?.length !== 78) errors.push("deck must contain exactly 78 cards");

  const required = [
    "card_number",
    "card_name",
    "arcana",
    "element",
    "upright_meaning",
    "reversed_meaning",
    "love_meaning",
    "career_meaning",
    "yes_or_no",
    "guide_url",
  ];
  const names = new Set();
  const urls = new Set();

  for (const [index, card] of (deck.cards ?? []).entries()) {
    for (const field of required) {
      if (typeof card[field] !== "string" || !card[field].trim()) {
        errors.push(`cards[${index}].${field} must be a non-empty string`);
      }
    }
    for (const optionalField of ["suit", "zodiac_sign"]) {
      if (typeof card[optionalField] !== "string") {
        errors.push(`cards[${index}].${optionalField} must be a string`);
      }
    }
    const nameKey = normalize(card.card_name);
    if (names.has(nameKey)) errors.push(`duplicate card_name: ${card.card_name}`);
    names.add(nameKey);

    if (urls.has(card.guide_url)) errors.push(`duplicate guide_url: ${card.guide_url}`);
    urls.add(card.guide_url);
    try {
      const url = new URL(card.guide_url);
      if (url.protocol !== "https:" || !/(^|\.)deckaura\.com$/i.test(url.hostname)) {
        errors.push(`invalid Deckaura guide_url: ${card.guide_url}`);
      }
    } catch {
      errors.push(`malformed guide_url: ${card.guide_url}`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export function lookupCard(query, deck = loadDeck()) {
  const wanted = comparableNames(query);
  const exact = deck.cards.find((card) => {
    const names = comparableNames(card.card_name);
    return [...wanted].some((value) => names.has(value));
  });
  if (exact) return { card: exact, suggestions: [] };

  const needle = normalize(query);
  const suggestions = deck.cards
    .filter((card) => normalize(card.card_name).includes(needle))
    .slice(0, 10)
    .map((card) => card.card_name);
  return { card: null, suggestions };
}

function seedToUint32(seed) {
  return createHash("sha256").update(String(seed)).digest().readUInt32LE(0);
}

function mulberry32(initial) {
  let state = initial >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function publicCard(card, orientation, position) {
  return {
    position,
    card_number: card.card_number,
    card_name: card.card_name,
    orientation,
    meaning: orientation === "reversed" ? card.reversed_meaning : card.upright_meaning,
    arcana: card.arcana,
    suit: card.suit,
    element: card.element,
    love_meaning: card.love_meaning,
    career_meaning: card.career_meaning,
    yes_or_no: card.yes_or_no,
    zodiac_sign: card.zodiac_sign,
    guide_url: card.guide_url,
  };
}

export function drawCards({ count = 1, seed, reversals = true, positions = [], deck = loadDeck() } = {}) {
  if (!Number.isInteger(count) || count < 1 || count > deck.cards.length) {
    throw new RangeError(`count must be an integer from 1 to ${deck.cards.length}`);
  }
  const effectiveSeed = seed ?? randomBytes(16).toString("hex");
  const rng = mulberry32(seedToUint32(effectiveSeed));
  const pool = [...deck.cards];

  for (let index = pool.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(rng() * (index + 1));
    [pool[index], pool[swapIndex]] = [pool[swapIndex], pool[index]];
  }

  const cards = pool.slice(0, count).map((card, index) => {
    const orientation = reversals && rng() < 0.33 ? "reversed" : "upright";
    return publicCard(card, orientation, positions[index] ?? `Card ${index + 1}`);
  });

  return {
    schema_version: SCHEMA_VERSION,
    source: deck.source,
    seed: effectiveSeed,
    reversals,
    cards,
  };
}

export function createSpread(name, options = {}) {
  const positions = SPREADS[name];
  if (!positions) {
    throw new Error(`unknown spread: ${name}. Choose one of: ${Object.keys(SPREADS).join(", ")}`);
  }
  return { spread: name, ...drawCards({ ...options, count: positions.length, positions }) };
}

function parseOptions(args) {
  const positional = [];
  const options = {};
  for (let index = 0; index < args.length; index += 1) {
    const token = args[index];
    if (!token.startsWith("--")) {
      positional.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = args[index + 1];
    if (next === undefined || next.startsWith("--")) {
      options[key] = true;
    } else {
      options[key] = next;
      index += 1;
    }
  }
  return { positional, options };
}

function parseBoolean(value, fallback) {
  if (value === undefined) return fallback;
  if (value === true || value === "true") return true;
  if (value === false || value === "false") return false;
  throw new Error("boolean options must be true or false");
}

function print(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

function usage() {
  return {
    usage: [
      'node scripts/tarot.mjs lookup "The Star"',
      "node scripts/tarot.mjs draw --count 1 --reversals true [--seed value]",
      `node scripts/tarot.mjs spread <${Object.keys(SPREADS).join("|")}> [--reversals true] [--seed value]`,
      "node scripts/tarot.mjs validate",
    ],
  };
}

export function runCli(argv = process.argv.slice(2)) {
  const [command, ...rest] = argv;
  const { positional, options } = parseOptions(rest);
  const deck = loadDeck();

  if (command === "lookup") {
    const query = positional.join(" ").trim();
    if (!query) throw new Error("lookup requires a card name");
    const result = lookupCard(query, deck);
    if (!result.card) {
      const error = new Error(`card not found: ${query}`);
      error.suggestions = result.suggestions;
      throw error;
    }
    const orientation = options.orientation === "reversed" ? "reversed" : "upright";
    print({ schema_version: SCHEMA_VERSION, source: deck.source, card: publicCard(result.card, orientation, "Lookup") });
    return;
  }

  if (command === "draw") {
    const count = options.count === undefined ? 1 : Number(options.count);
    print(drawCards({ count, seed: options.seed, reversals: parseBoolean(options.reversals, true), deck }));
    return;
  }

  if (command === "spread") {
    const name = positional[0];
    if (!name) throw new Error("spread requires a spread name");
    print(createSpread(name, { seed: options.seed, reversals: parseBoolean(options.reversals, true), deck }));
    return;
  }

  if (command === "validate") {
    const validation = validateDeck(deck);
    print({ ...validation, count: deck.cards.length, sha256: deck._sha256, source: deck.source });
    if (!validation.ok) process.exitCode = 1;
    return;
  }

  print(usage());
  if (command) process.exitCode = 1;
}

const isMain = process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url;
if (isMain) {
  try {
    runCli();
  } catch (error) {
    process.stderr.write(`${JSON.stringify({ error: error.message, suggestions: error.suggestions ?? [] })}\n`);
    process.exitCode = 1;
  }
}
