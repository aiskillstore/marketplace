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


function deleteFromArray(arr, idx) {
  if (!arr) return;
  if (Array.isArray(arr)) {
    if (idx >= 0) arr.splice(idx, 1);
    return;
  }
  if (typeof arr.delete === "function") {
    arr.delete(idx, 1);
  }
}

function listKeys(map) {
  if (!map) return [];
  if (typeof map.keys === "function") {
    return Array.from(map.keys());
  }
  return Object.keys(map);
}

const input = readStdin();
const docState = input.doc_state;
const stateVector = input.state_vector;
const rowIds = new Set(input.row_ids || []);
const viewIds = input.view_ids || [];

if (!Array.isArray(docState) || !Array.isArray(input.row_ids)) {
  throw new Error("Invalid input: doc_state and row_ids must be arrays");
}

const doc = new Y.Doc();
Y.applyUpdate(doc, Uint8Array.from(docState));

const dataRoot = doc.getMap("data");
const database = getMapValue(dataRoot, "database");
if (!database) {
  throw new Error("Missing database map in collab data");
}

const views = getMapValue(database, "views");
if (!views) {
  throw new Error("Missing views map in database collab");
}

const targetViewIds = viewIds.length > 0 ? viewIds : listKeys(views);

for (const viewId of targetViewIds) {
  const view = getMapValue(views, viewId);
  if (!view) continue;
  const rowOrders = getMapValue(view, "row_orders");
  if (!rowOrders) continue;
  const rows = asArray(rowOrders);
  for (let i = rows.length - 1; i >= 0; i -= 1) {
    const row = rows[i];
    const rowId = getMapValue(row, "id");
    if (rowIds.has(rowId)) {
      deleteFromArray(rowOrders, i);
    }
  }
  // row_orders 已在原地更新，无需重新 set
}

const update = Array.isArray(stateVector)
  ? Y.encodeStateAsUpdate(doc, Uint8Array.from(stateVector))
  : Y.encodeStateAsUpdate(doc);
const output = { update: Array.from(update) };
process.stdout.write(JSON.stringify(output));
