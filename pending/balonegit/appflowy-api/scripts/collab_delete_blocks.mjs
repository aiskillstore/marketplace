import fs from "fs";
import * as Y from "yjs";

function readStdin() {
  const input = fs.readFileSync(0, "utf-8").trim();
  if (!input) {
    throw new Error("Missing JSON input on stdin");
  }
  return JSON.parse(input);
}

function asArray(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value.slice();
  if (typeof value.toArray === "function") return value.toArray();
  return [];
}

function getMapValue(map, key) {
  if (!map) return undefined;
  if (typeof map.get === "function") {
    return map.get(key);
  }
  return map[key];
}

function deleteFromArray(arr, target) {
  if (!arr) return;
  if (Array.isArray(arr)) {
    const idx = arr.indexOf(target);
    if (idx >= 0) arr.splice(idx, 1);
    return;
  }
  if (typeof arr.toArray === "function" && typeof arr.delete === "function") {
    const list = arr.toArray();
    const idx = list.indexOf(target);
    if (idx >= 0) arr.delete(idx, 1);
  }
}

const input = readStdin();
const docState = input.doc_state;
const stateVector = input.state_vector;
const deleteBlockIds = input.delete_block_ids || [];
if (!Array.isArray(docState) || !Array.isArray(deleteBlockIds)) {
  throw new Error("Invalid input: doc_state and delete_block_ids must be arrays");
}

const doc = new Y.Doc();
Y.applyUpdate(doc, Uint8Array.from(docState));

const dataRoot = doc.getMap("data");
const root = dataRoot.get("document");
if (!root) {
  throw new Error("Missing document map in collab data");
}
const blocks = root.get("blocks");
const meta = root.get("meta");
const childrenMap = meta && typeof meta.get === "function" ? meta.get("children_map") : undefined;
const textMap = meta && typeof meta.get === "function" ? meta.get("text_map") : undefined;

function getBlock(id) {
  return getMapValue(blocks, id);
}

function getBlockField(block, key) {
  return getMapValue(block, key);
}

function getChildrenIds(blockId) {
  const block = getBlock(blockId);
  if (!block) return [];
  const childrenKey = getBlockField(block, "children");
  if (!childrenKey) return [];
  const arr = getMapValue(childrenMap, childrenKey);
  return asArray(arr);
}

const toDelete = new Set();

function collectDescendants(blockId) {
  if (toDelete.has(blockId)) return;
  toDelete.add(blockId);
  const children = getChildrenIds(blockId);
  for (const childId of children) {
    collectDescendants(childId);
  }
}

for (const id of deleteBlockIds) {
  collectDescendants(id);
}

function removeFromParent(blockId) {
  const block = getBlock(blockId);
  if (!block) return;
  const parentId = getBlockField(block, "parent");
  if (!parentId) return;
  const parent = getBlock(parentId);
  if (!parent) return;
  const parentChildrenKey = getBlockField(parent, "children");
  if (!parentChildrenKey) return;
  const arr = getMapValue(childrenMap, parentChildrenKey);
  deleteFromArray(arr, blockId);
}

for (const blockId of toDelete) {
  const block = getBlock(blockId);
  if (!block) continue;

  removeFromParent(blockId);

  const childrenKey = getBlockField(block, "children");
  if (childrenKey) {
    if (typeof childrenMap.delete === "function") {
      childrenMap.delete(childrenKey);
    } else {
      delete childrenMap[childrenKey];
    }
  }

  const externalId = getBlockField(block, "external_id");
  if (externalId) {
    if (typeof textMap.delete === "function") {
      textMap.delete(externalId);
    } else {
      delete textMap[externalId];
    }
  }

  if (typeof blocks.delete === "function") {
    blocks.delete(blockId);
  } else {
    delete blocks[blockId];
  }
}

const update = Array.isArray(stateVector)
  ? Y.encodeStateAsUpdate(doc, Uint8Array.from(stateVector))
  : Y.encodeStateAsUpdate(doc);
const output = { update: Array.from(update) };
process.stdout.write(JSON.stringify(output));
