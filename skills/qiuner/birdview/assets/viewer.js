// Generated from src/viewer/main.mts. Do not edit directly.
"use strict";
(() => {
  var __defProp = Object.defineProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };

  // src/viewer/routing.mts
  function requiredAt(values, index) {
    const value = values[index];
    if (value === void 0) throw new Error(`Missing routing grid value at ${index}.`);
    return value;
  }
  function routeArchitecture(relationships, positions2) {
    const gap = 10;
    const boxes = [...positions2].map(([id, p]) => ({ id, x: p.x, y: p.y, w: 164, h: 72 }));
    const boxById = new Map(boxes.map((b) => [b.id, b]));
    const obstacles = boxes.map((b) => ({ x: b.x - gap, y: b.y - gap, w: b.w + gap * 2, h: b.h + gap * 2 }));
    const ports = /* @__PURE__ */ new Map();
    const routes = relationships.map((relation) => {
      const from = boxById.get(relation.from), to = boxById.get(relation.to);
      if (!from || !to) throw new Error(`Missing position for ${relation.from} \u2192 ${relation.to}.`);
      const dx = to.x - from.x, dy = to.y - from.y;
      let sides = from === to ? ["top", "right"] : Math.abs(dx) >= Math.abs(dy) ? dx >= 0 ? ["right", "left"] : ["left", "right"] : dy >= 0 ? ["bottom", "top"] : ["top", "bottom"];
      if (Math.abs(dx) >= from.w + gap * 2 && Math.abs(dy) >= from.h + gap * 2) {
        const horizontal = dx > 0 ? ["right", "left"] : ["left", "right"];
        const vertical = dy > 0 ? ["bottom", "top"] : ["top", "bottom"];
        const candidates = [[vertical[0], horizontal[1]], [horizontal[0], vertical[1]]];
        const load = (pair2) => (ports.get(`${from.id}:${pair2[0]}`)?.length || 0) + (ports.get(`${to.id}:${pair2[1]}`)?.length || 0);
        candidates.sort((a, b) => load(a) - load(b));
        sides = requiredAt(candidates, 0);
      }
      const pair = [from, to].map((box, index) => {
        const port = { box, side: requiredAt(sides, index), peer: index ? from : to };
        const key = `${box.id}:${port.side}`;
        const list = ports.get(key) ?? [];
        list.push(port);
        ports.set(key, list);
        return port;
      });
      return { relation, start: requiredAt(pair, 0), end: requiredAt(pair, 1) };
    });
    for (const list of ports.values()) {
      const horizontal = ["top", "bottom"].includes(requiredAt(list, 0).side);
      list.sort((a, b) => horizontal ? a.peer.x - b.peer.x : a.peer.y - b.peer.y);
      list.forEach((port, index) => {
        const { box, side } = port;
        const offset = (index + 1) / (list.length + 1);
        port.point = horizontal ? [box.x + 16 + (box.w - 32) * offset, box.y + (side === "bottom" ? box.h : 0)] : [box.x + (side === "right" ? box.w : 0), box.y + 12 + (box.h - 24) * offset];
        port.stub = [
          port.point[0] + (side === "left" ? -gap : side === "right" ? gap : 0),
          port.point[1] + (side === "top" ? -gap : side === "bottom" ? gap : 0)
        ];
      });
    }
    const used = [];
    const centers = (values, size) => {
      const sorted = [...new Set(values)].sort((a, b) => a - b);
      return sorted.slice(1).map((value, i) => (requiredAt(sorted, i) + size + value) / 2);
    };
    const lanesX = centers(boxes.map((b) => b.x), 164);
    const lanesY = centers(boxes.map((b) => b.y), 72);
    const outerY = Math.max(...boxes.map((b) => b.y + b.h)) + 24;
    return routes.map(({ start, end, relation }) => {
      const startStub = start.stub, endStub = end.stub, startPoint = start.point, endPoint = end.point;
      if (!startStub || !endStub || !startPoint || !endPoint) throw new Error("Routing ports have not been positioned.");
      const xs = [.../* @__PURE__ */ new Set([...lanesX, ...obstacles.flatMap((b) => [b.x - 8, b.x, b.x + b.w, b.x + b.w + 8]), startStub[0], endStub[0]])].sort((a, b) => a - b);
      const ys = [.../* @__PURE__ */ new Set([...lanesY, outerY, outerY + 10, ...obstacles.flatMap((b) => [b.y - 8, b.y, b.y + b.h, b.y + b.h + 8]), startStub[1], endStub[1]])].sort((a, b) => a - b);
      const pointAt = (id) => [requiredAt(xs, id % xs.length), requiredAt(ys, Math.floor(id / xs.length))];
      const indexOf = (p) => ys.indexOf(p[1]) * xs.length + xs.indexOf(p[0]);
      const clear = (a, b) => !obstacles.some((r) => a[0] === b[0] ? a[0] > r.x && a[0] < r.x + r.w && Math.max(a[1], b[1]) > r.y && Math.min(a[1], b[1]) < r.y + r.h : a[1] > r.y && a[1] < r.y + r.h && Math.max(a[0], b[0]) > r.x && Math.min(a[0], b[0]) < r.x + r.w);
      const source = indexOf(startStub), target = indexOf(endStub);
      const axis = (p) => p.side === "left" || p.side === "right" ? 0 : 1;
      const initial = source * 2 + axis(start);
      const distance = /* @__PURE__ */ new Map([[initial, 0]]), previous = /* @__PURE__ */ new Map();
      const queue = [{ state: initial, cost: 0, rank: 0 }];
      let found;
      while (queue.length) {
        queue.sort((a2, b) => b.rank - a2.rank);
        const current = queue.pop();
        if (!current) break;
        if (current.cost !== distance.get(current.state)) continue;
        const id = Math.floor(current.state / 2), a = pointAt(id);
        if (id === target) {
          found = current.state;
          break;
        }
        const col = id % xs.length, row = Math.floor(id / xs.length);
        const neighbors = [
          col > 0 ? id - 1 : -1,
          col + 1 < xs.length ? id + 1 : -1,
          row > 0 ? id - xs.length : -1,
          row + 1 < ys.length ? id + xs.length : -1
        ];
        for (const next of neighbors) {
          if (next < 0) continue;
          const b = pointAt(next), direction = a[0] === b[0] ? 1 : 0;
          if (!clear(a, b)) continue;
          let penalty = current.state % 2 === direction ? 0 : 18;
          if (next === target && direction !== axis(end)) penalty += 18;
          for (const [c, d2] of used) {
            const otherDirection = c[0] === d2[0] ? 1 : 0;
            if (direction === otherDirection) {
              const fixed = direction === 0 ? 1 : 0;
              const overlap = Math.min(Math.max(a[direction], b[direction]), Math.max(c[direction], d2[direction])) - Math.max(Math.min(a[direction], b[direction]), Math.min(c[direction], d2[direction]));
              const separation = Math.abs(a[fixed] - c[fixed]);
              if (overlap > 0 && separation < 8) penalty += overlap * (1 - separation / 8) * 2;
            } else if (Math.min(a[0], b[0]) <= Math.max(c[0], d2[0]) && Math.max(a[0], b[0]) >= Math.min(c[0], d2[0]) && Math.min(a[1], b[1]) <= Math.max(c[1], d2[1]) && Math.max(a[1], b[1]) >= Math.min(c[1], d2[1])) penalty += 24;
          }
          const cost = current.cost + Math.abs(b[0] - a[0]) + Math.abs(b[1] - a[1]) + penalty;
          const state = next * 2 + direction;
          if (cost >= (distance.get(state) ?? Infinity)) continue;
          distance.set(state, cost);
          previous.set(state, current.state);
          queue.push({ state, cost, rank: cost + Math.abs(b[0] - endStub[0]) + Math.abs(b[1] - endStub[1]) });
        }
      }
      if (found === void 0) throw new Error(`Cannot route ${relation.from} \u2192 ${relation.to} without crossing a module.`);
      const middle = [];
      for (let state = found; state !== void 0; state = previous.get(state)) middle.push(pointAt(Math.floor(state / 2)));
      const points = [startPoint, ...middle.reverse(), endPoint];
      for (let i = points.length - 2; i > 0; i--) {
        const a = requiredAt(points, i - 1), b = requiredAt(points, i), c = requiredAt(points, i + 1);
        if (a[0] === b[0] && b[0] === c[0] || a[1] === b[1] && b[1] === c[1]) points.splice(i, 1);
      }
      for (let i = 1; i < points.length; i++) used.push([requiredAt(points, i - 1), requiredAt(points, i)]);
      let d = `M ${requiredAt(points, 0).join(" ")}`;
      for (let i = 1; i < points.length - 1; i++) {
        const a = requiredAt(points, i - 1), b = requiredAt(points, i), c = requiredAt(points, i + 1);
        const before = Math.hypot(b[0] - a[0], b[1] - a[1]), after = Math.hypot(c[0] - b[0], c[1] - b[1]);
        const radius = Math.min(6, before / 2, after / 2);
        const entry = b.map((v, k) => v + (requiredAt(a, k) - v) * radius / before);
        const exit = b.map((v, k) => v + (requiredAt(c, k) - v) * radius / after);
        d += ` L ${entry.join(" ")} Q ${b.join(" ")} ${exit.join(" ")}`;
      }
      d += ` L ${requiredAt(points, points.length - 1).join(" ")}`;
      return { points, d };
    });
  }

  // src/viewer/i18n.mts
  var i18n_exports = {};
  __export(i18n_exports, {
    availableLanguages: () => availableLanguages,
    isChinese: () => isChinese,
    localized: () => localized,
    selectLanguage: () => selectLanguage,
    translate: () => translate,
    uiTranslations: () => uiTranslations
  });
  var uiTranslations = {
    "\u67B6\u6784\u6807\u8BC6": "Architecture identity",
    "\u524D\u7AEF": "Frontend",
    "\u540E\u7AEF": "Backend",
    "\u7F13\u5B58": "Cache",
    "\u6570\u636E\u5B58\u50A8": "Data store",
    "\u4EFB\u52A1\u4E0E\u961F\u5217": "Tasks / Queue",
    "\u5B89\u5168": "Security",
    "\u901A\u7528\u6A21\u5757": "Generic",
    "\u5173\u95ED\u8BE6\u60C5": "Close details",
    "\u67E5\u770B\u8BE6\u60C5": "Inspect module",
    "\u770B\u89C1 AI \u5982\u4F55\u6539\u53D8\u4F60\u7684\u7CFB\u7EDF": "See how AI changes your system",
    "\u67B6\u6784\u5FEB\u7167": "Architecture snapshot",
    "\u7CFB\u7EDF\u67B6\u6784": "System architecture",
    "\u9879\u76EE\u67B6\u6784": "Project architecture",
    "\u7F29\u5C0F": "Zoom out",
    "\u653E\u5927": "Zoom in",
    "\u7F29\u653E\u6BD4\u4F8B": "Zoom level",
    "\u9002\u914D\u5168\u56FE": "Fit diagram",
    "\u539F\u59CB\u5927\u5C0F": "Actual size",
    "\u6A21\u5757\u5173\u7CFB": "Module relationships",
    "\u67B6\u6784\u5FEB\u7167 \xB7 \u5C1A\u65E0\u4FEE\u6539\u6D3B\u52A8": "Architecture snapshot \xB7 No change activity",
    "\u6A21\u5757\u8BE6\u60C5": "Module details",
    "\u6587\u4EF6\u5F52\u5C5E": "File ownership",
    "\u6E90\u7801\u8BC1\u636E": "Source evidence",
    "\u5F85\u786E\u8BA4": "Uncertain",
    "\u76F8\u5173\u8FDE\u63A5": "Related connections",
    "\u5207\u6362\u5230\u6DF1\u8272": "Switch to dark theme",
    "\u5207\u6362\u5230\u6D45\u8272": "Switch to light theme",
    "\u5173\u7CFB\u65B9\u5411\u52A8\u753B\uFF0C\u4E0D\u4EE3\u8868\u5B9E\u65F6\u6570\u636E\u4F20\u8F93": "Relationship direction, not live data transfer",
    "\u6D41\u5411": "Flow",
    "\u5916\u90E8\u670D\u52A1": "External service",
    "\u672C\u5730\u6A21\u5757": "Local module",
    "\u6709\u6765\u6E90\u8BC1\u636E": "Source-backed",
    "\u65E0\u672C\u5730\u6587\u4EF6\u5F52\u5C5E": "No local file ownership",
    "\u65E0\u6765\u6E90\u8BC1\u636E": "No source evidence",
    "\u65E0\u5DF2\u8BB0\u5F55\u7684\u5F85\u786E\u8BA4\u9879": "No recorded open questions",
    "\u65E0\u5DF2\u8BB0\u5F55\u7684\u5173\u7CFB": "No recorded relationships"
  };
  function availableLanguages(map2) {
    const languages = /* @__PURE__ */ new Set([map2.language || "zh", "zh", "en"]);
    for (const item of [map2.project, ...map2.modules, ...map2.relationships, ...map2.groups || [], ...map2.constraints || []]) {
      for (const locale of Object.keys(item.translations || {})) languages.add(locale);
      for (const source of item.evidence || []) for (const locale of Object.keys(source.translations || {})) languages.add(locale);
    }
    return languages;
  }
  function selectLanguage(base, available, stored, requested) {
    let language2 = base || "zh";
    if (stored !== null && available.has(stored)) language2 = stored;
    if (requested !== null && available.has(requested)) language2 = requested;
    return language2;
  }
  var isChinese = (language2) => language2.split("-")[0] === "zh";
  var translate = (text, language2) => isChinese(language2) ? text : uiTranslations[text] || text;
  function localized(item, field, language2) {
    return item.translations?.[language2]?.[field] ?? item[field] ?? "";
  }

  // src/viewer/constraint-canvas.mts
  function mountConstraintCanvas(container, data) {
    const root = container;
    root.classList.add("bv-constraints");
    const element2 = (tag, className = "", content) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (content !== void 0) node.textContent = content;
      return node;
    };
    const text = (zh, en) => document.documentElement.lang.startsWith("zh") ? zh : en;
    const button = (className, label2, action) => {
      const node = element2("button", className, label2);
      node.type = "button";
      node.onclick = action;
      return node;
    };
    const topicNodes = data.nodes;
    let directoryMode = false, filteredRules = null;
    const nodes = new Map(data.nodes.map((node) => [node.id, node]));
    const children = new Map(data.nodes.map((node) => [node.id, []]));
    for (const node of data.nodes) if (node.parent) children.get(node.parent)?.push(node.id);
    const rootNode = data.nodes.find((node) => !node.parent);
    if (!rootNode) throw new Error("Constraint graph requires a root node.");
    const top = rootNode.id;
    const expanded = /* @__PURE__ */ new Set([top]);
    let selected = top, filterIds = null, query2 = "", matching = null, searchMessage = "";
    let positions2 = /* @__PURE__ */ new Map(), visible = [], camera = { x: 0, y: 0, scale: 1 }, fitted = false;
    let directoryOpen = !matchMedia("(max-width:700px)").matches;
    const toolbar = element2("div", "cv-toolbar");
    const toggleDirectory = button("cv-directory-toggle", "\u2630", () => {
      directoryOpen = !directoryOpen;
      directory.hidden = !directoryOpen;
      toggleDirectory.setAttribute("aria-expanded", String(directoryOpen));
      if (directoryOpen) search.focus();
    });
    const title = element2("span", "cv-title");
    const grouping = element2("select", "cv-grouping");
    grouping.append(new Option("\u6309\u4E3B\u9898", "topics"), new Option("\u6309\u76EE\u5F55", "directories"));
    grouping.hidden = !data.directoryNodes;
    const resetFilter = button("cv-reset-filter", "", () => api.filter(null));
    const zoomOut = button("cv-zoom-out", "\u2212", () => zoomAt(camera.scale / 1.2));
    const zoomLabel = element2("span", "cv-zoom-label");
    const zoomIn = button("cv-zoom-in", "+", () => zoomAt(camera.scale * 1.2));
    const fitButton = button("cv-fit", "", () => fit());
    const legendButton = button("cv-legend-toggle", "", () => {
      legend.hidden = !legend.hidden;
      legendButton.setAttribute("aria-expanded", String(!legend.hidden));
    });
    const coverageButton = button("cv-coverage", "", () => {
      selected = top;
      showDetails2(top);
      render();
    });
    toolbar.append(toggleDirectory, grouping, title, resetFilter, zoomOut, zoomLabel, zoomIn, fitButton, legendButton, coverageButton);
    const workspace2 = element2("div", "cv-workspace");
    const directory = element2("nav", "cv-directory");
    directory.hidden = !directoryOpen;
    const directoryHeading = element2("div", "cv-directory-heading");
    const directoryTitle = element2("span");
    const directoryClose = button("", "\xD7", () => {
      directoryOpen = false;
      directory.hidden = true;
      toggleDirectory.setAttribute("aria-expanded", "false");
      toggleDirectory.focus();
    });
    directoryHeading.append(directoryTitle, directoryClose);
    const search = element2("input", "cv-search");
    search.type = "search";
    search.autocomplete = "off";
    const tree = element2("div", "cv-tree");
    const empty = element2("div", "cv-empty");
    empty.setAttribute("role", "status");
    directory.append(directoryHeading, search, tree, empty);
    const viewport2 = element2("div", "cv-viewport");
    viewport2.tabIndex = 0;
    const stage = element2("div", "cv-stage");
    const help = element2("span", "cv-help");
    viewport2.append(stage, help);
    const reader = element2("section", "cv-reader");
    reader.hidden = true;
    const readerHeader = element2("div", "cv-reader-header");
    const readerTitle = element2("h2", "cv-reader-title");
    const readerClose = button("cv-reader-close", "\xD7", () => {
      reader.hidden = true;
      focusSelected();
      focusButton();
    });
    const readerMeta = element2("p", "cv-reader-meta");
    const readerBody = element2("div", "cv-reader-body");
    readerHeader.append(readerTitle, readerClose);
    reader.append(readerHeader, readerMeta, readerBody);
    const dialog = element2("dialog", "cv-dialog");
    const dialogTitle = element2("h2", "cv-dialog-title");
    const dialogClose = button("cv-dialog-close", "\xD7", () => dialog.close());
    const dialogHeader = element2("div", "cv-reader-header");
    dialogHeader.append(dialogTitle, dialogClose);
    const dialogContent = element2("div", "cv-dialog-content");
    dialog.append(dialogHeader, dialogContent);
    root.append(dialog);
    dialog.setAttribute("aria-label", text("\u8BE6\u7EC6\u8BF4\u660E", "Detailed explanation"));
    dialogClose.ariaLabel = text("\u5173\u95ED\u8BE6\u60C5", "Close details");
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
    dialog.addEventListener("keydown", (event) => event.stopPropagation());
    dialog.addEventListener("close", () => focusButton());
    let lastCardClick = { id: null, time: 0 };
    function openDialog(id) {
      const wasHidden = reader.hidden;
      showDetails2(id);
      dialogTitle.textContent = readerTitle.textContent;
      dialogContent.replaceChildren(readerMeta.cloneNode(true), readerBody.cloneNode(true));
      reader.hidden = wasHidden;
      dialog.showModal();
      dialogContent.scrollTop = 0;
      dialogClose.focus();
    }
    workspace2.append(directory, viewport2, reader);
    const legend = element2("section", "cv-legend");
    legend.hidden = true;
    root.append(toolbar, workspace2, legend);
    grouping.onchange = () => {
      directoryMode = grouping.value === "directories";
      data.nodes = directoryMode ? data.directoryNodes : topicNodes;
      nodes.clear();
      children.clear();
      for (const node of data.nodes) {
        nodes.set(node.id, node);
        children.set(node.id, []);
      }
      for (const node of data.nodes) if (node.parent) children.get(node.parent)?.push(node.id);
      if (dialog.open) dialog.close();
      api.filter(filteredRules);
    };
    function allowed(id) {
      return (!filterIds || filterIds.has(id)) && (!matching || matching.has(id));
    }
    function visibleChildren(id) {
      return (children.get(id) || []).filter(allowed);
    }
    function ancestors(id, set) {
      for (let node = nodes.get(id); node; node = node.parent ? nodes.get(node.parent) : void 0) set.add(node.id);
    }
    function roleStyle(node, target) {
      const role = data.roles?.[node.role || "generic"];
      if (!role) return;
      const light = document.documentElement.dataset.theme === "light";
      const colors = light ? role.light : role.dark;
      ["accent", "bg", "border"].forEach((key, index) => target.style.setProperty(`--cv-role-${key}`, colors[index]));
    }
    function label(node) {
      if (node.kind === "rule") {
        const role = data.roles?.[node.role || "generic"];
        const en = { frontend: "Frontend", backend: "Backend", cache: "Cache", database: "Data store", queue: "Tasks / Queue", security: "Security", generic: "Generic" };
        return `R${String(node.ordinal).padStart(3, "0")} \xB7 ${node.version ? "v" + node.version : text("\u7248\u672C\u672A\u8FFD\u8E2A", "Untracked")} \xB7 ${text(role?.name || "", en[node.role || "generic"])}`;
      }
      if (filterIds || matching) return text("\u7B5B\u9009\u8303\u56F4", "Filtered scope");
      return node.label || node.desc;
    }
    function applyCamera() {
      stage.style.transform = `translate(${camera.x}px,${camera.y}px) scale(${camera.scale})`;
      zoomLabel.textContent = `${Math.round(camera.scale * 100)}%`;
      zoomOut.disabled = camera.scale <= 0.15;
      zoomIn.disabled = camera.scale >= 2;
    }
    function zoomAt(scale, x = viewport2.clientWidth / 2, y = viewport2.clientHeight / 2) {
      const next = Math.max(0.15, Math.min(2, scale)), ratio = next / camera.scale;
      camera.x = x - (x - camera.x) * ratio;
      camera.y = y - (y - camera.y) * ratio;
      camera.scale = next;
      applyCamera();
    }
    function fit() {
      if (!positions2.size || viewport2.clientWidth < 1 || viewport2.clientHeight < 1) return;
      const minY = Math.min(...[...positions2.values()].map((p) => p.y));
      const width2 = Math.max(...[...positions2.values()].map((p) => p.x)) + 176;
      const height2 = Math.max(...[...positions2.values()].map((p) => p.y)) - minY + 76;
      const widthScale = (viewport2.clientWidth - 80) / width2;
      const heightScale = (viewport2.clientHeight - 100) / height2;
      camera.scale = Math.max(0.48, Math.min(1, widthScale, heightScale));
      camera.x = width2 * camera.scale < viewport2.clientWidth - 120 ? 56 : 28;
      camera.y = height2 * camera.scale > viewport2.clientHeight - 60 ? 28 : (viewport2.clientHeight - height2 * camera.scale) / 2;
      camera.y -= minY * camera.scale;
      fitted = true;
      applyCamera();
    }
    function focusSelected() {
      const point = positions2.get(selected);
      if (!point) return;
      camera.x = viewport2.clientWidth * 0.43 - (point.x + 88) * camera.scale;
      camera.y = viewport2.clientHeight / 2 - (point.y + 38) * camera.scale;
      applyCamera();
    }
    function focusButton() {
      [...stage.querySelectorAll(".cv-card")].find((node) => node.dataset.id === selected)?.focus({ preventScroll: true });
    }
    function activate(id, fromDirectory = false) {
      const prior = positions2.get(id);
      const screen = prior && { x: camera.x + prior.x * camera.scale, y: camera.y + prior.y * camera.scale };
      selected = id;
      const descendants = visibleChildren(id);
      if (!query2) {
        const collapse = descendants.length && expanded.has(id);
        expanded.clear();
        ancestors(id, expanded);
        if (collapse || !descendants.length) expanded.delete(id);
      }
      if (!descendants.length) showDetails2(id);
      render();
      if (screen && reader.hidden) {
        const point = positions2.get(id);
        if (point) {
          camera.x = screen.x - point.x * camera.scale;
          camera.y = screen.y - point.y * camera.scale;
          applyCamera();
        }
      } else focusSelected();
      if (fromDirectory && matchMedia("(max-width:700px)").matches) {
        directoryOpen = false;
        directory.hidden = true;
        toggleDirectory.setAttribute("aria-expanded", "false");
        focusSelected();
      }
      if (!fromDirectory || !reader.hidden) focusButton();
    }
    function showDetails2(id) {
      const node = nodes.get(id);
      if (!node) return;
      reader.hidden = false;
      reader.scrollTop = 0;
      readerTitle.textContent = node.title;
      readerMeta.textContent = label(node);
      readerBody.replaceChildren();
      const body = data.documents[id]?.body || node.desc || "";
      let code = null, quote = null;
      for (const line of body.split("\n")) {
        if (line.startsWith("```")) {
          if (code) code = null;
          else {
            code = element2("pre");
            readerBody.append(code);
          }
          continue;
        }
        if (code) {
          code.textContent += line + "\n";
          continue;
        }
        if (line.startsWith("# ")) continue;
        if (line.startsWith("> ")) {
          if (!quote) {
            quote = element2("blockquote");
            readerBody.append(quote);
          }
          quote.textContent += (quote.textContent ? "\n" : "") + line.slice(2);
          continue;
        }
        quote = null;
        if (!line.trim()) continue;
        const heading = line.match(/^#{2,6}\s+(.*)/);
        readerBody.append(element2(heading ? "h3" : "p", "", heading ? heading[1] : line.replace(/\*\*([^*]+)\*\*/g, "$1").replace(/`([^`]+)`/g, "$1")));
      }
    }
    function render() {
      positions2 = /* @__PURE__ */ new Map();
      visible = [];
      let cursor = 0;
      function place(id, depth) {
        if (!allowed(id)) return;
        visible.push(id);
        const list = query2 || expanded.has(id) ? visibleChildren(id) : [];
        let y;
        if (list.length) {
          for (const child of list) place(child, depth + 1);
          y = (positions2.get(list[0]).y + positions2.get(list.at(-1)).y) / 2;
        } else {
          y = cursor;
          cursor += 92;
        }
        positions2.set(id, { x: depth * 280, y });
      }
      if (query2) place(top, 0);
      else if (allowed(top)) {
        positions2.set(top, { x: 0, y: 0 });
        visible.push(top);
        let parent = top, depth = 1;
        while (expanded.has(parent)) {
          const list = visibleChildren(parent);
          const start = positions2.get(parent).y - (list.length - 1) * 92 / 2;
          list.forEach((id, index) => {
            positions2.set(id, { x: depth * 280, y: start + index * 92 });
            visible.push(id);
          });
          parent = list.find((id) => expanded.has(id)) || "";
          if (!parent) break;
          depth++;
        }
        visible = [];
        const visit = (id) => {
          if (!positions2.has(id)) return;
          visible.push(id);
          for (const child of visibleChildren(id)) visit(child);
        };
        visit(top);
      }
      const focus = /* @__PURE__ */ new Set([selected, ...visibleChildren(selected)]);
      const selectedParent = nodes.get(selected)?.parent;
      if (selectedParent) focus.add(selectedParent);
      const focusing = selected !== top && !query2;
      stage.replaceChildren();
      tree.replaceChildren();
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.classList.add("cv-edges");
      svg.setAttribute("aria-hidden", "true");
      stage.append(svg);
      for (const id of visible) {
        const node = nodes.get(id), point = positions2.get(id), parent = node.parent ? positions2.get(node.parent) : void 0;
        if (parent) {
          const edge = document.createElementNS(svg.namespaceURI, "path");
          const x1 = parent.x + 176, y1 = parent.y + 38, x2 = point.x, y2 = point.y + 38;
          const middle = (x1 + x2) / 2;
          const direction = Math.sign(y2 - y1);
          const radius = Math.min(6, Math.abs(y2 - y1) / 2);
          edge.setAttribute("d", direction === 0 ? `M ${x1} ${y1} H ${x2}` : `M ${x1} ${y1} H ${middle - radius} Q ${middle} ${y1} ${middle} ${y1 + direction * radius} V ${y2 - direction * radius} Q ${middle} ${y2} ${middle + radius} ${y2} H ${x2}`);
          edge.classList.add("cv-edge");
          if (!query2 && (id === selected || node.parent === selected)) edge.classList.add("cv-relevant");
          else if (focusing && (!focus.has(id) || !focus.has(node.parent))) edge.classList.add("cv-muted-branch");
          svg.append(edge);
        }
        const card = button("cv-card", "", (event) => {
          const now = performance.now();
          if (event.detail && lastCardClick.id === id && now - lastCardClick.time < 400) {
            lastCardClick = { id: null, time: 0 };
            openDialog(id);
            return;
          }
          lastCardClick = { id, time: now };
          activate(id);
        });
        card.dataset.id = id;
        card.ondblclick = () => {
          if (!dialog.open) openDialog(id);
        };
        if (focusing && !focus.has(id)) card.classList.add("cv-muted-branch");
        card.style.left = point.x + "px";
        card.style.top = point.y + "px";
        roleStyle(node, card);
        card.title = node.title + "\n" + node.desc;
        card.setAttribute("aria-current", String(selected === id));
        const cardTitle = element2("span", "cv-card-title");
        cardTitle.append(element2("i", "cv-dot"), element2("span", "", node.title));
        card.append(cardTitle, element2("span", "cv-card-meta", label(node)));
        const list = visibleChildren(id);
        if (list.length) {
          card.setAttribute("aria-expanded", String(!!query2 || expanded.has(id)));
          card.append(element2("span", "cv-expand-count", `${expanded.has(id) || query2 ? "\u2212" : "+"}${list.length}`));
        }
        card.onkeydown = (event) => {
          if (event.key === "Enter" && event.shiftKey) {
            event.preventDefault();
            openDialog(id);
          }
          if (event.key === "ArrowRight" && list.length) {
            event.preventDefault();
            expanded.clear();
            ancestors(id, expanded);
            selected = list[0];
            render();
            focusSelected();
            focusButton();
          }
          if (event.key === "ArrowLeft" && node.parent) {
            event.preventDefault();
            selected = node.parent;
            expanded.clear();
            ancestors(selected, expanded);
            render();
            focusSelected();
            focusButton();
          }
        };
        stage.append(card);
        const row = button("cv-tree-row", "", () => activate(id, true));
        row.dataset.id = id;
        row.style.paddingLeft = 8 + point.x / 280 * 12 + "px";
        row.setAttribute("aria-current", String(selected === id));
        if (list.length) row.setAttribute("aria-expanded", String(!!query2 || expanded.has(id)));
        row.append(element2("span", "cv-tree-marker", list.length ? expanded.has(id) || query2 ? "\u25BE" : "\u25B8" : "\xB7"), element2("span", "", node.title));
        tree.append(row);
      }
      empty.hidden = !searchMessage && visible.length > 0;
      empty.textContent = searchMessage || text("\u6CA1\u6709\u5339\u914D\u7684\u89C4\u5219", "No matching rules");
      applyCamera();
    }
    function searchNodes() {
      query2 = search.value.trim().toLocaleLowerCase();
      matching = null;
      searchMessage = "";
      if (query2) {
        matching = /* @__PURE__ */ new Set();
        let count = 0;
        for (const node of data.nodes) {
          if (filterIds && !filterIds.has(node.id)) continue;
          const body = node.kind === "group" ? "" : data.documents[node.id]?.body;
          if (![node.title, node.desc, body].join(" ").toLocaleLowerCase().includes(query2)) continue;
          count++;
          if (count <= 100) ancestors(node.id, matching);
        }
        if (count > 100) searchMessage = text(`\u627E\u5230 ${count} \u9879\uFF0C\u663E\u793A\u524D 100 \u9879\uFF1B\u8BF7\u7F29\u5C0F\u641C\u7D22\u8303\u56F4\u3002`, `${count} matches; showing the first 100. Refine your search.`);
      }
      render();
      fit();
    }
    search.oninput = searchNodes;
    let gesture = null, moved = false;
    const pointers = /* @__PURE__ */ new Map();
    viewport2.onpointerdown = (event) => {
      if (event.button !== 0) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      moved = false;
      if (pointers.size === 1) gesture = { x: event.clientX, y: event.clientY, camera: { ...camera } };
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        gesture = { distance: Math.hypot(a.x - b.x, a.y - b.y), scale: camera.scale };
      }
      if (!(event.target instanceof Element) || !event.target.closest("button")) viewport2.setPointerCapture(event.pointerId);
    };
    viewport2.onpointermove = (event) => {
      if (!pointers.has(event.pointerId)) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 2 && gesture?.distance) {
        const [a, b] = [...pointers.values()], rect = viewport2.getBoundingClientRect();
        zoomAt(gesture.scale * Math.hypot(a.x - b.x, a.y - b.y) / gesture.distance, (a.x + b.x) / 2 - rect.left, (a.y + b.y) / 2 - rect.top);
        moved = true;
      } else if (gesture?.camera) {
        const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
        if (Math.hypot(dx, dy) > 4) moved = true;
        if (moved) {
          viewport2.setPointerCapture(event.pointerId);
          camera.x = gesture.camera.x + dx;
          camera.y = gesture.camera.y + dy;
          applyCamera();
        }
      }
    };
    const release = (event) => {
      pointers.delete(event.pointerId);
      gesture = null;
    };
    viewport2.onpointerup = release;
    viewport2.onpointercancel = release;
    viewport2.addEventListener("click", (event) => {
      if (moved) {
        event.preventDefault();
        event.stopPropagation();
        moved = false;
      }
    }, true);
    viewport2.addEventListener("wheel", (event) => {
      event.preventDefault();
      if (event.ctrlKey || event.metaKey) {
        const rect = viewport2.getBoundingClientRect();
        zoomAt(camera.scale * Math.exp(-event.deltaY * 3e-3), event.clientX - rect.left, event.clientY - rect.top);
      } else {
        camera.x -= event.deltaX;
        camera.y -= event.deltaY;
        applyCamera();
      }
    }, { passive: false });
    viewport2.onkeydown = (event) => {
      if (event.target !== viewport2) return;
      if (event.key === "+" || event.key === "=") zoomAt(camera.scale * 1.2);
      if (event.key === "-") zoomAt(camera.scale / 1.2);
      if (event.key === "0") fit();
      const shifts = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] };
      const shift = shifts[event.key];
      if (shift) {
        event.preventDefault();
        camera.x += shift[0];
        camera.y += shift[1];
        applyCamera();
      }
    };
    root.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (dialog.open) dialog.close();
      else if (!legend.hidden) {
        legend.hidden = true;
        legendButton.setAttribute("aria-expanded", "false");
        legendButton.focus();
      } else if (!reader.hidden) readerClose.click();
      else if (!directory.hidden && matchMedia("(max-width:700px)").matches) directoryClose.click();
    });
    const api = {
      filter(ids) {
        filteredRules = ids ? [...ids] : null;
        lastCardClick = { id: null, time: 0 };
        filterIds = ids ? /* @__PURE__ */ new Set() : null;
        if (filterIds) for (const id of ids || []) ancestors(id, filterIds);
        selected = top;
        expanded.clear();
        expanded.add(top);
        reader.hidden = true;
        search.value = "";
        query2 = "";
        matching = null;
        searchMessage = "";
        resetFilter.hidden = !filterIds;
        render();
        fit();
        refreshLabels();
      },
      refresh() {
        const scroll = reader.scrollTop;
        refreshLabels();
        render();
        if (!reader.hidden) {
          showDetails2(selected);
          reader.scrollTop = scroll;
        }
      },
      resize() {
        if (!fitted && viewport2.clientWidth > 0) fit();
      }
    };
    function refreshLabels() {
      grouping.ariaLabel = text("\u7EA6\u675F\u5206\u7EC4\u65B9\u5F0F", "Constraint grouping");
      grouping.options[0].textContent = text("\u6309\u4E3B\u9898", "By topic");
      grouping.options[1].textContent = text("\u6309\u76EE\u5F55", "By directory");
      title.textContent = filterIds ? text("\u6A21\u5757\u5173\u8054\u89C4\u5219", "Module-linked rules") : data.mode === "sources" ? text("\u6765\u6E90\u7D22\u5F15 \xB7 \u672A\u5B8C\u6210\u8BED\u4E49\u5BA1\u67E5", "Source index \xB7 Semantic review pending") : text("\u5DF2\u6574\u7406\u89C4\u5219", "Reviewed rules") + ` \xB7 ${data.nodes.filter((node) => node.kind === "rule").length}`;
      title.title = data.scope;
      toggleDirectory.title = toggleDirectory.ariaLabel = text("\u89C4\u5219\u76EE\u5F55", "Rule directory");
      toggleDirectory.setAttribute("aria-expanded", String(directoryOpen));
      directoryTitle.textContent = data.mode === "sources" ? text("\u6765\u6E90\u76EE\u5F55", "Sources") : text("\u89C4\u5219\u76EE\u5F55", "Rules");
      directory.setAttribute("aria-label", directoryTitle.textContent);
      directoryClose.ariaLabel = text("\u6536\u8D77\u76EE\u5F55", "Close directory");
      search.placeholder = text("\u641C\u7D22\u89C4\u5219\u4E0E\u539F\u6587", "Search rules and sources");
      search.ariaLabel = search.placeholder;
      resetFilter.textContent = text("\u67E5\u770B\u5168\u90E8\u89C4\u5219", "Show all rules");
      resetFilter.hidden = !filterIds;
      fitButton.textContent = text("\u9002\u914D\u5168\u56FE", "Fit graph");
      zoomIn.ariaLabel = text("\u653E\u5927", "Zoom in");
      zoomOut.ariaLabel = text("\u7F29\u5C0F", "Zoom out");
      legendButton.textContent = text("\u89D2\u8272\u56FE\u4F8B", "Role legend");
      legendButton.hidden = !data.roles;
      legendButton.setAttribute("aria-expanded", String(!legend.hidden));
      coverageButton.textContent = text("\u9605\u8BFB\u8303\u56F4", "Coverage");
      readerClose.ariaLabel = text("\u5173\u95ED\u8BE6\u60C5", "Close details");
      dialogClose.ariaLabel = readerClose.ariaLabel;
      dialog.setAttribute("aria-label", text("\u8BE6\u7EC6\u8BF4\u660E", "Detailed explanation"));
      viewport2.ariaLabel = text("\u7EA6\u675F\u56FE\u753B\u5E03\uFF1B\u65B9\u5411\u952E\u5E73\u79FB\uFF0C\u52A0\u51CF\u952E\u7F29\u653E\uFF0C0 \u9002\u914D", "Constraint canvas; arrows to pan, plus/minus to zoom, 0 to fit");
      help.textContent = text("\u62D6\u52A8\u5E73\u79FB \xB7 Ctrl + \u6EDA\u8F6E\u7F29\u653E \xB7 \u53CC\u51FB / Shift+Enter \u9605\u8BFB\u8BE6\u60C5", "Drag to pan \xB7 Ctrl + scroll to zoom \xB7 Double-click / Shift+Enter for details");
      legend.replaceChildren(element2("strong", "", text("\u9002\u7528\u89D2\u8272", "Applicable roles")));
      const en = { frontend: "Frontend", backend: "Backend", cache: "Cache", database: "Data store", queue: "Tasks / Queue", security: "Security", generic: "Generic" };
      for (const [id, role] of Object.entries(data.roles || {})) {
        const row = element2("div", "cv-legend-row");
        roleStyle({ role: id }, row);
        row.append(element2("i", "cv-dot"), element2("span", "", text(role.name, en[id])), element2("b", "", String(data.nodes.filter((node) => node.kind === "rule" && (node.role || "generic") === id && (!filterIds || filterIds.has(node.id))).length)));
        legend.append(row);
      }
      legend.append(
        element2("p", "", text("\u7F16\u53F7\u5206\u4E3B\u9898\uFF0C\u989C\u8272\u5206\u89D2\u8272\uFF0C\u4E0D\u4EE3\u8868\u5408\u89C4\u7ED3\u679C\u3002\u901A\u7528\u542B\u8DE8\u89D2\u8272\u4E0E\u672A\u660E\u786E\u5F52\u5C5E\u3002", "Numbers identify topics; colors identify roles, not compliance. Generic includes mixed or unknown roles.")),
        element2("p", "", text("\u89C4\u5219\u539F\u6587\u7248\u672C\u4E0E\u9879\u76EE\u5FEB\u7167\u5206\u522B\u8BB0\u5F55\u3002\u5B9E\u73B0\u5C1A\u672A\u6838\u9A8C\u3002", "Source-range versions and project snapshot are separate. Implementation is unverified.")),
        element2("p", "", data.revision)
      );
    }
    const resizeObserver = new ResizeObserver(() => api.resize());
    resizeObserver.observe(viewport2);
    const themeObserver = new MutationObserver(() => api.refresh());
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "lang"] });
    refreshLabels();
    render();
    requestAnimationFrame(() => api.resize());
    return api;
  }

  // src/viewer/main.mts
  var { map, icons, brandLogo } = DATA;
  function required(value) {
    if (value === null || value === void 0) throw new Error("Missing required viewer data or element.");
    return value;
  }
  function element(value, ctor) {
    if (!(value instanceof ctor)) throw new Error("Unexpected viewer element.");
    return value;
  }
  function $(id) {
    const node = document.getElementById(id);
    if (id === "connections" || id === "overview-connections") return element(node, SVGSVGElement);
    if (id === "activity-step") return element(node, HTMLSelectElement);
    if (id === "activity-disclosure") return element(node, HTMLDetailsElement);
    if (id === "guide-progress") return element(node, HTMLProgressElement);
    return element(node, HTMLElement);
  }
  var buttonById = (id) => element(document.getElementById(id), HTMLButtonElement);
  var query = (selector, root = document) => element(root.querySelector(selector), HTMLElement);
  var iconMarkup = (name) => required(icons[name]);
  var roles = {
    frontend: { tone: "blue", icon: "panels-top-left", label: "\u524D\u7AEF" },
    backend: { tone: "teal", icon: "code", label: "\u540E\u7AEF" },
    cache: { tone: "cyan", icon: "zap", label: "\u7F13\u5B58" },
    database: { tone: "violet", icon: "database", label: "\u6570\u636E\u5B58\u50A8" },
    queue: { tone: "amber", icon: "list-ordered", label: "\u4EFB\u52A1\u4E0E\u961F\u5217" },
    security: { tone: "rose", icon: "shield-check", label: "\u5B89\u5168" },
    generic: { tone: "slate", icon: "box", label: "\u901A\u7528\u6A21\u5757" }
  };
  var { uiTranslations: uiTranslations2 } = i18n_exports;
  var availableLanguages2 = availableLanguages(map);
  var storedLanguage = null;
  try {
    storedLanguage = localStorage.getItem("birdview-language");
  } catch {
  }
  var requestedLanguage = new URLSearchParams(location.hash.slice(1)).get("lang");
  var language = selectLanguage(map.language, availableLanguages2, storedLanguage, requestedLanguage);
  var isChinese2 = () => isChinese(language);
  var t = (text) => translate(text, language);
  function localized2(item, field) {
    return localized(item, field, language);
  }
  var staticLabels = [];
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (node.textContent !== null && Object.hasOwn(uiTranslations2, node.textContent)) staticLabels.push({ node, source: node.textContent });
  }
  var staticAttributes = [];
  document.querySelectorAll("[title], [aria-label]").forEach((node) => {
    for (const attr of ["title", "aria-label"]) {
      const source = node.getAttribute(attr);
      if (source !== null && Object.hasOwn(uiTranslations2, source)) staticAttributes.push({ node, attr, source });
    }
  });
  var languageSelect = document.createElement("select");
  languageSelect.id = "language";
  languageSelect.setAttribute("aria-label", "\u8BED\u8A00 / Language");
  for (const value of availableLanguages2) {
    const option = document.createElement("option");
    option.value = value;
    let label = value;
    try {
      label = new Intl.DisplayNames([value], { type: "language" }).of(value) ?? value;
    } catch {
    }
    option.textContent = value === "zh" ? "\u4E2D\u6587" : value === "en" ? "English" : label;
    languageSelect.append(option);
  }
  query(".header-actions").prepend(languageSelect);
  function applyLanguage() {
    document.documentElement.lang = language;
    languageSelect.value = language;
    for (const { node, source } of staticLabels) node.textContent = t(source);
    for (const { node, attr, source } of staticAttributes) node.setAttribute(attr, t(source));
    $("project").textContent = localized2(map.project, "name");
    document.title = `${localized2(map.project, "name")} | Birdview`;
    const count = map.modules.filter((module) => module.status === "uncertain").length;
    $("uncertainty").textContent = isChinese2() ? `${count} \u4E2A\u6A21\u5757\u5F85\u786E\u8BA4` : `${count} uncertain modules`;
    $("uncertainty").hidden = count === 0;
    flowLabel.title = t("\u5173\u7CFB\u65B9\u5411\u52A8\u753B\uFF0C\u4E0D\u4EE3\u8868\u5B9E\u65F6\u6570\u636E\u4F20\u8F93");
    required(flowLabel.lastChild).textContent = t("\u6D41\u5411");
    required(relationView.options[0]).textContent = isChinese2() ? "\u6982\u89C8" : "Overview";
    required(relationView.options[1]).textContent = isChinese2() ? "\u5168\u90E8\u5173\u7CFB" : "All relations";
    relationView.setAttribute("aria-label", isChinese2() ? "\u5173\u7CFB\u663E\u793A\u8303\u56F4" : "Relationship visibility");
    themeButton();
    updateActivity();
    roleLegend.replaceChildren();
    for (const key of new Set(map.modules.map((module) => module.role || "generic"))) {
      const role = roles[key];
      const entry = document.createElement("span");
      entry.dataset.tone = role.tone;
      const icon = document.createElement("span");
      icon.innerHTML = iconMarkup(role.icon);
      entry.append(icon, document.createTextNode(`${t(role.label)} \xB7 ${map.modules.filter((module) => (module.role || "generic") === key).length}`));
      roleLegend.append(entry);
    }
    closeDetails.title = closeDetails.ariaLabel = t("\u5173\u95ED\u8BE6\u60C5");
    showDetails.title = showDetails.ariaLabel = t("\u67E5\u770B\u8BE6\u60C5");
    for (const { label, group } of groupFrames) {
      const groupRoles = { interaction: ["\u4EA4\u4E92\u5C42", "Interaction"], runtime: ["\u8FD0\u884C\u5C42", "Runtime"], "external-services": ["\u5916\u90E8\u670D\u52A1", "External services"], generic: ["\u901A\u7528\u5206\u7EC4", "General"] };
      const role = groupRoles[group.role || "generic"][isChinese2() ? 0 : 1];
      label.textContent = `${localized2(group, "name")} \xB7 ${role}`;
      label.title = `${label.textContent}
${group.evidence.map((source) => `${source.path}: ${localized2(source, "note")}`).join("\n")}`;
    }
    for (const module of map.modules) {
      const button = required(buttons.get(module.id));
      const name = query("strong", button);
      name.textContent = localized2(module, "name");
      name.dir = "auto";
      name.style.fontSize = "13px";
      query("small", button).textContent = localized2(module, "responsibility");
      query("small", button).dir = "auto";
      button.title = `${localized2(module, "name")}
${localized2(module, "responsibility")}`;
      button.setAttribute("aria-label", `${localized2(module, "name")}${module.status === "uncertain" ? `, ${t("\u5F85\u786E\u8BA4")}` : ""}`);
      const mark = button.querySelector(".uncertain-mark");
      if (mark) {
        mark.title = t("\u5F85\u786E\u8BA4");
        mark.setAttribute("aria-label", t("\u5F85\u786E\u8BA4"));
      }
      for (let size = 13; size > 10 && name.scrollHeight > name.clientHeight; size--) name.style.fontSize = `${size - 1}px`;
    }
    for (const { path, relation } of edges) required(path.querySelector("title")).textContent = localized2(relation, "label");
    select(map.modules.find((module) => module.id === selectedModuleId) || required(map.modules[0]));
    if (fitting) updateZoom();
  }
  languageSelect.onchange = () => {
    language = languageSelect.value;
    try {
      localStorage.setItem("birdview-language", language);
    } catch {
    }
    const hash = new URLSearchParams(location.hash.slice(1));
    hash.set("lang", language);
    try {
      history.replaceState(null, "", `#${hash}`);
    } catch {
    }
    applyLanguage();
  };
  var brandImage = document.createElement("img");
  brandImage.className = "brand-logo";
  brandImage.src = brandLogo;
  brandImage.alt = "";
  $("brand-icon").replaceChildren(brandImage);
  $("project").textContent = map.project.name;
  document.title = `${map.project.name} | Birdview`;
  $("identity").textContent = `${map.project.id} / ${map.mapId} / v${map.revision}`;
  $("uncertainty").textContent = `${map.modules.filter((module) => module.status === "uncertain").length} \u4E2A\u6A21\u5757\u5F85\u786E\u8BA4`;
  function themeButton() {
    const light = document.documentElement.dataset.theme === "light";
    $("theme").innerHTML = iconMarkup(light ? "moon" : "sun");
    $("theme").title = $("theme").ariaLabel = t(light ? "\u5207\u6362\u5230\u6DF1\u8272" : "\u5207\u6362\u5230\u6D45\u8272");
  }
  $("theme").onclick = () => {
    const theme = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("birdview-theme", theme);
    } catch {
    }
    themeButton();
  };
  themeButton();
  var rows = [...new Set(map.modules.map((module) => module.layout.row))].sort((a, b) => a - b);
  var columns = [...new Set(map.modules.map((module) => module.layout.column))].sort((a, b) => a - b);
  function trackOffsets(tracks, modules, axis, step) {
    const offsets = [0];
    const members = new Map(modules.map((module) => [module.id, module]));
    for (let i = 1; i < tracks.length; i++) {
      const boundary = required(tracks[i]);
      const load = map.relationships.filter((relation) => {
        const from = members.get(relation.from), to = members.get(relation.to);
        return from && to && Math.min(from.layout[axis], to.layout[axis]) < boundary && Math.max(from.layout[axis], to.layout[axis]) >= boundary;
      }).length;
      offsets.push(required(offsets[i - 1]) + step + Math.min(96, Math.max(0, load - 2) * 12));
    }
    return offsets;
  }
  var columnOffsets = trackOffsets(columns, map.modules, "column", 220);
  var rowOffsets = trackOffsets(rows, map.modules, "row", 140);
  var positions = new Map(map.modules.map((module) => [module.id, { x: 28 + required(columnOffsets[columns.indexOf(module.layout.column)]), y: 30 + required(rowOffsets[rows.indexOf(module.layout.row)]) }]));
  var width = Math.max(300, required(columnOffsets.at(-1)) + 220);
  var height = Math.max(220, required(rowOffsets.at(-1)) + 140);
  var groupFrames = [];
  var groupLayer = document.createElement("div");
  groupLayer.id = "groups";
  $("map").prepend(groupLayer);
  if (map.groups?.length) {
    const assigned = new Set(map.groups.flatMap((group) => group.members));
    const ungrouped = map.modules.filter((module) => !assigned.has(module.id));
    let offset = 28;
    const sections = [...map.groups.map((group) => ({ group, modules: map.modules.filter((module) => group.members.includes(module.id)) })), ...ungrouped.length ? [{ modules: ungrouped }] : []];
    height = 220;
    for (const section of sections) {
      const sectionRows = [...new Set(section.modules.map((module) => module.layout.row))].sort((a, b) => a - b);
      const sectionColumns = [...new Set(section.modules.map((module) => module.layout.column))].sort((a, b) => a - b);
      const xs = trackOffsets(sectionColumns, section.modules, "column", 204);
      const ys = trackOffsets(sectionRows, section.modules, "row", 128);
      const sectionWidth = required(xs.at(-1)) + 220;
      const sectionHeight = required(ys.at(-1)) + 176;
      for (const module of section.modules) positions.set(module.id, { x: offset + 20 + required(xs[sectionColumns.indexOf(module.layout.column)]), y: 70 + required(ys[sectionRows.indexOf(module.layout.row)]) });
      if (section.group) {
        const frame = document.createElement("div");
        frame.className = "group-frame";
        frame.dataset.role = section.group.role || "generic";
        Object.assign(frame.style, { left: `${offset}px`, top: "22px", width: `${sectionWidth}px`, height: `${sectionHeight}px` });
        const label = document.createElement("span");
        label.className = "group-label";
        frame.append(label);
        groupLayer.append(frame);
        groupFrames.push({ label, group: section.group });
      }
      height = Math.max(height, sectionHeight + 44);
      offset += sectionWidth + 44;
    }
    width = offset - 16;
  }
  $("map").style.width = `${width}px`;
  $("map").style.height = `${height}px`;
  var zoom = 1;
  var fitting = true;
  var viewport = query(".map-scroll");
  function updateZoom() {
    if (fitting) {
      const availableHeight = Math.max(180, Math.min(viewport.clientHeight - 40, window.innerHeight - viewport.getBoundingClientRect().top - 70));
      zoom = Math.min(1, viewport.clientWidth / width, availableHeight / height);
    }
    $("map").style.transform = `scale(${zoom})`;
    $("map-stage").style.width = `${width * zoom}px`;
    $("map-stage").style.height = `${height * zoom}px`;
    const overview = document.getElementById("overview-map");
    if (overview) {
      overview.style.transform = `scale(${zoom})`;
      $("overview-stage").style.width = `${width * zoom}px`;
      $("overview-stage").style.height = `${height * zoom}px`;
    }
    $("zoom-value").textContent = `${Math.round(zoom * 100)}%`;
    buttonById("zoom-in").disabled = zoom >= 2;
    buttonById("zoom-out").disabled = zoom <= 0.1;
    $("fit").setAttribute("aria-pressed", String(fitting));
  }
  for (const [id, icon] of Object.entries({ "zoom-in": "zoom-in", "zoom-out": "zoom-out", fit: "maximize", actual: "scan" })) $(id).innerHTML = icons[icon] || "";
  $("zoom-in").onclick = () => {
    fitting = false;
    zoom = Math.min(2, zoom + 0.15);
    updateZoom();
  };
  $("zoom-out").onclick = () => {
    fitting = false;
    zoom = Math.max(0.1, zoom - 0.15);
    updateZoom();
  };
  $("actual").onclick = () => {
    fitting = false;
    zoom = 1;
    updateZoom();
  };
  $("fit").onclick = () => {
    fitting = true;
    updateZoom();
    viewport.scrollTo(0, 0);
    document.getElementById("overview-scroll")?.scrollTo(0, 0);
  };
  new ResizeObserver(() => {
    if (fitting) updateZoom();
  }).observe(viewport);
  window.addEventListener("resize", () => {
    if (fitting) updateZoom();
  });
  updateZoom();
  var svgNS = "http://www.w3.org/2000/svg";
  $("connections").setAttribute("viewBox", `0 0 ${width} ${height}`);
  $("connections").style.width = `${width}px`;
  $("connections").style.height = `${height}px`;
  var defs = document.createElementNS(svgNS, "defs");
  var marker = document.createElementNS(svgNS, "marker");
  for (const [key, value] of Object.entries({ id: "arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "6", markerHeight: "6", orient: "auto-start-reverse" })) marker.setAttribute(key, value);
  var arrow = document.createElementNS(svgNS, "path");
  arrow.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
  arrow.setAttribute("fill", "#809487");
  marker.append(arrow);
  defs.append(marker);
  $("connections").append(defs);
  var edges = [];
  var selectedModuleId;
  var hoveredModuleId;
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var flowLabel = document.createElement("label");
  flowLabel.className = "flow-toggle";
  flowLabel.title = "\u5173\u7CFB\u65B9\u5411\u52A8\u753B\uFF0C\u4E0D\u4EE3\u8868\u5B9E\u65F6\u6570\u636E\u4F20\u8F93";
  var flowToggle = document.createElement("input");
  flowToggle.type = "checkbox";
  flowToggle.checked = true;
  flowToggle.id = "flow-toggle";
  flowLabel.append(flowToggle, document.createTextNode("\u6D41\u5411"));
  query(".map-tools").prepend(flowLabel);
  var relationView = document.createElement("select");
  relationView.id = "relation-view";
  relationView.add(new Option("", "overview"));
  relationView.add(new Option("", "all"));
  relationView.value = "overview";
  var relationCount = document.createElement("span");
  relationCount.id = "relation-count";
  relationCount.setAttribute("aria-live", "polite");
  query(".map-tools").prepend(relationView, relationCount);
  relationView.onchange = () => {
    hoveredModuleId = void 0;
    updateFlow();
  };
  function updateFlow() {
    const activeModuleId = hoveredModuleId;
    const activeButton = activeModuleId ? buttons.get(activeModuleId) : void 0;
    const accent = activeButton ? getComputedStyle(activeButton).getPropertyValue("--node-accent").trim() : "var(--mint)";
    const neighbors = /* @__PURE__ */ new Set([activeModuleId]);
    for (const relation of map.relationships) {
      if (relation.from === activeModuleId || relation.to === activeModuleId) {
        neighbors.add(relation.from);
        neighbors.add(relation.to);
      }
    }
    for (const [id, button] of buttons) {
      button.classList.toggle("flow-hover", id === activeModuleId);
      button.classList.toggle("context-muted", Boolean(activeModuleId) && !neighbors.has(id));
    }
    $("connections").style.setProperty("--flow-accent", accent);
    let visibleCount = 0;
    for (const edge of edges) {
      edge.path.classList.toggle("relevant", edge.relation.from === activeModuleId || edge.relation.to === activeModuleId);
      const relevant = edge.path.classList.contains("relevant");
      const visible = relationView.value === "all" || edge.relation.visibility === "overview" || relevant || edge.path.classList.contains("constraint-highlight");
      edge.path.style.display = visible ? "" : "none";
      edge.path.classList.toggle("context-muted", Boolean(activeModuleId) && !relevant);
      if (visible) visibleCount++;
      const active = visible && flowToggle.checked && !reducedMotion.matches && !document.hidden && relevant;
      edge.dot.style.display = active ? "" : "none";
      if (!active) {
        edge.animation?.cancel();
        edge.animation = void 0;
        continue;
      }
      if (edge.animation) continue;
      const length = edge.path.getTotalLength();
      const frames = Array.from({ length: 61 }, (_, index) => {
        const point = edge.path.getPointAtLength(length * index / 60);
        return { transform: `translate(${point.x}px, ${point.y}px)` };
      });
      edge.animation = edge.dot.animate(frames, { duration: 1600, iterations: Infinity, easing: "linear" });
    }
    relationCount.textContent = isChinese2() ? `\u663E\u793A ${visibleCount}/${edges.length} \u6761\u5173\u7CFB` : `${visibleCount}/${edges.length} relations shown`;
    relationCount.title = isChinese2() ? "\u60AC\u6D6E\u6A21\u5757\u53EF\u4E34\u65F6\u663E\u793A\u5176\u5168\u90E8\u76F4\u63A5\u5173\u7CFB" : "Hover a module to reveal all its direct relationships";
    for (const module of map.modules) {
      const button = required(buttons.get(module.id));
      const badge = query(".hidden-relations", button);
      const count = edges.filter((edge) => edge.path.style.display === "none" && (edge.relation.from === module.id || edge.relation.to === module.id)).length;
      const hint = isChinese2() ? `\u8FD8\u6709 ${count} \u6761\u76F4\u63A5\u5173\u7CFB\u672A\u663E\u793A` : `${count} more direct relationships hidden`;
      badge.hidden = count === 0;
      badge.textContent = count ? `+${count}` : "";
      badge.title = hint;
      button.setAttribute("aria-label", `${localized2(module, "name")}${module.status === "uncertain" ? `, ${t("\u5F85\u786E\u8BA4")}` : ""}${count ? `, ${hint}` : ""}`);
    }
    syncOverview();
  }
  flowToggle.onchange = updateFlow;
  reducedMotion.addEventListener("change", updateFlow);
  document.addEventListener("visibilitychange", updateFlow);
  var routedConnections = routeArchitecture(map.relationships, positions);
  for (const [relationIndex, relation] of map.relationships.entries()) {
    const path = document.createElementNS(svgNS, "path");
    const { d } = required(routedConnections[relationIndex]);
    path.setAttribute("d", d);
    path.setAttribute("class", "edge");
    path.setAttribute("marker-end", "url(#arrow)");
    if (relation.status === "uncertain") path.setAttribute("stroke-dasharray", "5 4");
    const title = document.createElementNS(svgNS, "title");
    title.textContent = relation.label;
    path.append(title);
    $("connections").append(path);
    const dot = document.createElementNS(svgNS, "circle");
    dot.setAttribute("r", "3");
    dot.setAttribute("class", "flow-dot");
    dot.setAttribute("aria-hidden", "true");
    dot.style.display = "none";
    $("connections").append(dot);
    edges.push({ path, relation, dot });
  }
  var buttons = /* @__PURE__ */ new Map();
  for (const module of map.modules) {
    const button = document.createElement("button");
    button.className = "node";
    const hiddenRelations = document.createElement("span");
    hiddenRelations.className = "hidden-relations";
    hiddenRelations.hidden = true;
    hiddenRelations.setAttribute("aria-hidden", "true");
    button.append(hiddenRelations);
    button.dataset.module = module.id;
    button.dataset.kind = module.kind;
    const role = roles[module.role || "generic"];
    button.dataset.tone = role.tone;
    button.style.left = `${required(positions.get(module.id)).x}px`;
    button.style.top = `${required(positions.get(module.id)).y}px`;
    button.setAttribute("aria-label", module.name);
    const icon = document.createElement("span");
    icon.className = "node-top";
    icon.innerHTML = iconMarkup(role.icon);
    const name = document.createElement("strong");
    name.textContent = module.name;
    const status = document.createElement("small");
    status.textContent = module.responsibility;
    button.title = `${module.name}
${module.responsibility}`;
    button.append(icon, name, status);
    if (module.status === "uncertain") {
      const mark = document.createElement("span");
      mark.className = "uncertain-mark";
      mark.textContent = "?";
      mark.title = "\u5F85\u786E\u8BA4";
      mark.setAttribute("aria-label", "\u5F85\u786E\u8BA4");
      button.append(mark);
      button.setAttribute("aria-label", `${module.name}\uFF0C\u5F85\u786E\u8BA4`);
    }
    button.onclick = () => {
      if (constraintPanelOpen) {
        constraintFilter = "module";
        selectedConstraintId = void 0;
      }
      select(module);
      setInspector(true);
    };
    button.onpointerenter = (event) => {
      if (event.pointerType === "touch") return;
      hoveredModuleId = module.id;
      updateFlow();
    };
    button.onpointerleave = () => {
      if (hoveredModuleId !== module.id) return;
      hoveredModuleId = void 0;
      updateFlow();
    };
    $("nodes").append(button);
    for (let size = 13; size > 10 && name.scrollHeight > name.clientHeight; size--) name.style.fontSize = `${size - 1}px`;
    buttons.set(module.id, button);
  }
  var moduleMeta = document.createElement("div");
  var roleLegend = document.createElement("div");
  roleLegend.className = "role-legend";
  query(".legend").prepend(roleLegend);
  moduleMeta.className = "module-meta";
  $("module-name").after(moduleMeta);
  var workspace = query(".workspace");
  var inspector = query("aside");
  document.addEventListener("pointerdown", () => {
    document.documentElement.dataset.motionInput = "pointer";
  }, true);
  document.addEventListener("keydown", () => {
    document.documentElement.dataset.motionInput = "keyboard";
  }, true);
  var closeDetails = document.createElement("button");
  closeDetails.id = "close-details";
  closeDetails.innerHTML = iconMarkup("x");
  inspector.prepend(closeDetails);
  var showDetails = document.createElement("button");
  showDetails.id = "show-details";
  showDetails.innerHTML = icons["panel-right"] || "";
  query(".map-tools").append(showDetails);
  function setInspector(open) {
    workspace.classList.toggle("inspector-open", open);
    showDetails.setAttribute("aria-expanded", String(open));
    updateConstraints();
    if (fitting) updateZoom();
  }
  closeDetails.onclick = () => {
    setInspector(false);
    showDetails.focus();
  };
  showDetails.onclick = () => setInspector(!workspace.classList.contains("inspector-open"));
  inspector.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeDetails.click();
  });
  function select(module) {
    selectedModuleId = module.id;
    for (const [id, button] of buttons) {
      button.classList.toggle("selected", id === module.id);
      button.setAttribute("aria-pressed", String(id === module.id));
    }
    $("module-name").textContent = localized2(module, "name");
    moduleMeta.textContent = `${t(roles[module.role || "generic"].label)} \xB7 ${t(module.kind === "external" ? "\u5916\u90E8\u670D\u52A1" : "\u672C\u5730\u6A21\u5757")} \xB7 ${t(module.status === "uncertain" ? "\u5F85\u786E\u8BA4" : "\u6709\u6765\u6E90\u8BC1\u636E")}`;
    $("responsibility").textContent = localized2(module, "responsibility");
    $("ownership").replaceChildren();
    for (const owner of module.ownership) {
      const li = document.createElement("li");
      li.textContent = owner.path;
      $("ownership").append(li);
    }
    if (!module.ownership.length) $("ownership").textContent = t("\u65E0\u672C\u5730\u6587\u4EF6\u5F52\u5C5E");
    $("evidence").textContent = module.evidence.map((item) => `${item.path}${item.line ? `:${item.line}` : ""}${item.symbol ? ` \xB7 ${item.symbol}` : ""}
${localized2(item, "note")}`).join("\n\n") || t("\u65E0\u6765\u6E90\u8BC1\u636E");
    $("questions").textContent = localized2(module, "openQuestions").join("\n") || t("\u65E0\u5DF2\u8BB0\u5F55\u7684\u5F85\u786E\u8BA4\u9879");
    $("relations").replaceChildren();
    for (const { path, relation } of edges) {
      const relevant = relation.from === module.id || relation.to === module.id;
      path.classList.toggle("relevant", relevant);
      if (!relevant) continue;
      const li = document.createElement("li");
      const title = document.createElement("strong");
      title.textContent = `${localized2(required(map.modules.find((item) => item.id === relation.from)), "name")} \u2192 ${localized2(required(map.modules.find((item) => item.id === relation.to)), "name")}`;
      const label = document.createElement("span");
      label.textContent = [localized2(relation, "label"), ...relation.evidence.map((item) => `${item.path}${item.line ? `:${item.line}` : ""} \xB7 ${localized2(item, "note")}`), ...localized2(relation, "openQuestions")].join(" \xB7 ");
      li.append(title, label);
      $("relations").append(li);
    }
    if (!$("relations").children.length) $("relations").textContent = t("\u65E0\u5DF2\u8BB0\u5F55\u7684\u5173\u7CFB");
    updateConstraints();
    updateFlow();
  }
  var activityEvents = DATA.events || [];
  var activityIndex = DATA.simulation ? 0 : Math.max(0, activityEvents.length - 1);
  var activityMode = activityEvents.length ? "activity" : "architecture";
  var activityPanel = document.createElement("section");
  activityPanel.className = "activity-panel";
  activityPanel.hidden = !activityEvents.length;
  activityPanel.innerHTML = '<div class="activity-toolbar"><div id="activity-mode" role="group"></div><span id="activity-source"></span><div class="activity-history"><button id="activity-prev"></button><select id="activity-step"></select><button id="activity-next"></button><button id="activity-latest"></button></div></div><div id="activity-summary" aria-live="polite"></div><details id="activity-disclosure"><summary></summary><div id="activity-details"></div></details>';
  query(".workspace").before(activityPanel);
  var mapHeading = query(".map-heading");
  new ResizeObserver(() => workspace.style.setProperty("--toolbar-height", `${mapHeading.offsetHeight}px`)).observe(mapHeading);
  var mapTools = query(".map-tools");
  var relationTools = document.createElement("div");
  relationTools.className = "relation-tools";
  relationTools.append(relationView, flowLabel);
  var zoomTools = document.createElement("div");
  zoomTools.className = "zoom-tools";
  $("actual").replaceChildren($("zoom-value"));
  zoomTools.append($("zoom-out"), $("actual"), $("zoom-in"), $("fit"));
  mapTools.replaceChildren(relationTools, zoomTools, showDetails);
  if (activityEvents.length) {
    element(mapHeading.firstElementChild, HTMLElement).hidden = true;
    mapHeading.prepend($("activity-mode"));
  }
  required(query(".legend").lastElementChild).before(relationCount);
  query(".activity-toolbar", activityPanel).append($("activity-summary"));
  var viewModes = { architecture: ["\u5B8C\u6574\u67B6\u6784", "Architecture", "layers"], activity: ["\u66F4\u6539\u89C6\u56FE", "Changes", "focus"], compare: ["\u5E76\u6392\u5BF9\u7167", "Compare", "columns-2"] };
  for (const [mode, labels] of Object.entries(viewModes)) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.view = mode;
    button.innerHTML = `${icons[labels[2]] || ""}<span>${labels[0]}</span>`;
    button.onclick = () => {
      if (mode !== "architecture" && mode !== "activity" && mode !== "compare") throw new Error("Unknown view mode.");
      activityMode = mode;
      hoveredModuleId = void 0;
      updateActivity();
      updateFlow();
    };
    $("activity-mode").append(button);
  }
  var activityStep = $("activity-step");
  var phaseNames = { planned: ["\u8BA1\u5212", "Planned"], editing: ["\u4FEE\u6539", "Editing"], verifying: ["\u9A8C\u8BC1", "Verifying"], completed: ["\u7ED3\u675F", "Completed"], failed: ["\u5931\u8D25", "Failed"], cancelled: ["\u53D6\u6D88", "Cancelled"] };
  for (const [id, icon] of Object.entries({ "activity-prev": "chevron-left", "activity-next": "chevron-right", "activity-latest": "skip-forward" })) $(id).innerHTML = iconMarkup(icon);
  activityStep.onchange = () => {
    activityIndex = Number(activityStep.value);
    updateActivity();
  };
  $("activity-prev").onclick = () => {
    activityIndex = Math.max(0, activityIndex - 1);
    updateActivity();
  };
  $("activity-next").onclick = () => {
    activityIndex = Math.min(activityEvents.length - 1, activityIndex + 1);
    updateActivity();
  };
  $("activity-latest").onclick = () => {
    activityIndex = activityEvents.length - 1;
    updateActivity();
  };
  $("activity-disclosure").ontoggle = () => {
    if (fitting) updateZoom();
  };
  var mapPanes = document.createElement("div");
  mapPanes.className = "map-panes";
  viewport.before(mapPanes);
  var changePane = document.createElement("section");
  changePane.className = "map-pane";
  changePane.innerHTML = '<h2 class="pane-title" id="change-title"></h2>';
  changePane.append(viewport);
  mapPanes.append(changePane);
  if (activityEvents.length) {
    const overviewPane = document.createElement("section");
    overviewPane.id = "overview-pane";
    overviewPane.className = "map-pane";
    overviewPane.hidden = true;
    overviewPane.innerHTML = '<h2 class="pane-title" id="overview-title"></h2><div class="map-scroll" id="overview-scroll"><div id="overview-stage"></div></div>';
    mapPanes.prepend(overviewPane);
    const clone = $("map").cloneNode(true);
    if (!(clone instanceof HTMLElement)) throw new Error("Invalid map clone.");
    const overview = clone;
    for (const element2 of [overview, ...overview.querySelectorAll("[id]")]) element2.id = `overview-${element2.id}`;
    overview.querySelectorAll("[marker-end]").forEach((edge) => edge.setAttribute("marker-end", "url(#overview-arrow)"));
    overview.querySelectorAll(".flow-dot").forEach((dot) => dot.remove());
    $("overview-stage").append(overview);
    overview.querySelectorAll(".node").forEach((button) => {
      button.onclick = () => {
        if (constraintPanelOpen) {
          constraintFilter = "module";
          selectedConstraintId = void 0;
        }
        select(required(map.modules.find((module) => module.id === button.dataset.module)));
        setInspector(true);
      };
      button.onpointerenter = (event) => {
        if (event.pointerType !== "touch") {
          hoveredModuleId = button.dataset.module;
          updateFlow();
        }
      };
      button.onpointerleave = () => {
        hoveredModuleId = void 0;
        updateFlow();
      };
    });
    for (const [source, destination] of [[viewport, $("overview-scroll")], [$("overview-scroll"), viewport]]) {
      source.addEventListener("scroll", () => {
        if (activityMode !== "compare") return;
        if (destination.scrollLeft !== source.scrollLeft) destination.scrollLeft = source.scrollLeft;
        if (destination.scrollTop !== source.scrollTop) destination.scrollTop = source.scrollTop;
      });
    }
  }
  for (const scroll of mapPanes.querySelectorAll(".map-scroll")) {
    scroll.tabIndex = 0;
    let pan;
    scroll.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || event.pointerType === "touch" || event.target instanceof Element && event.target.closest("button")) return;
      pan = { x: event.clientX, y: event.clientY, left: scroll.scrollLeft, top: scroll.scrollTop };
      scroll.setPointerCapture(event.pointerId);
    });
    scroll.addEventListener("pointermove", (event) => {
      if (!pan) return;
      scroll.scrollLeft = pan.left + pan.x - event.clientX;
      scroll.scrollTop = pan.top + pan.y - event.clientY;
    });
    scroll.addEventListener("lostpointercapture", () => {
      pan = void 0;
    });
    scroll.addEventListener("pointerup", (event) => {
      pan = void 0;
      if (scroll.hasPointerCapture(event.pointerId)) scroll.releasePointerCapture(event.pointerId);
    });
  }
  function syncOverview() {
    const overview = document.getElementById("overview-map");
    if (!overview) return;
    for (const button of overview.querySelectorAll(".node")) {
      const source = required(buttons.get(required(button.dataset.module)));
      button.className = source.className;
      button.classList.remove("activity-outside", "activity-scope", "activity-target", "context-muted");
      for (const attr of ["title", "aria-label", "aria-pressed"]) {
        if (source.hasAttribute(attr)) button.setAttribute(attr, required(source.getAttribute(attr)));
      }
      if (button.innerHTML !== source.innerHTML) button.innerHTML = source.innerHTML;
    }
    overview.querySelectorAll(".group-label").forEach((label, index) => {
      label.textContent = required(groupFrames[index]).label.textContent;
      label.title = required(groupFrames[index]).label.title;
    });
    overview.querySelectorAll(".edge").forEach((edge, index) => {
      edge.setAttribute("class", required(edges[index]).path.getAttribute("class") ?? "");
      edge.classList.remove("activity-edge-outside", "context-muted");
      edge.style.display = required(edges[index]).path.style.display;
      required(edge.querySelector("title")).textContent = required(required(edges[index]).path.querySelector("title")).textContent;
    });
    $("overview-connections").style.setProperty("--flow-accent", $("connections").style.getPropertyValue("--flow-accent"));
  }
  function updateActivity() {
    const zh = isChinese2();
    updateConstraints();
    document.body.classList.toggle("show-activity-context", activityMode === "activity");
    $("change-title").textContent = viewModes[activityMode === "architecture" ? "architecture" : "activity"][zh ? 0 : 1];
    viewport.setAttribute("aria-label", $("change-title").textContent);
    if (!activityEvents.length) return;
    const event = required(activityEvents[activityIndex]);
    const active = activityMode !== "architecture";
    const context = $("activity-context");
    query(".activity-toolbar", activityPanel).hidden = activityMode !== "activity";
    const terminalPhase = ["completed", "failed", "cancelled"].includes(event.phase);
    const targetLabel = terminalPhase ? zh ? "\u65E0\u5F53\u524D\u76EE\u6807" : "No current targets" : event.phase === "planned" ? zh ? "\u4E0B\u4E00\u6B65\u76EE\u6807" : "Next-step targets" : event.phase === "verifying" ? zh ? "\u9A8C\u8BC1\u76EE\u6807" : "Verification targets" : zh ? "\u4FEE\u6539\u76EE\u6807" : "Edit targets";
    mapPanes.classList.toggle("compare", activityMode === "compare");
    $("overview-pane").hidden = activityMode !== "compare";
    $("overview-title").textContent = viewModes.architecture[zh ? 0 : 1];
    $("overview-scroll").setAttribute("aria-label", $("overview-title").textContent);
    $("activity-mode").setAttribute("aria-label", zh ? "\u89C6\u56FE" : "View");
    for (const button of $("activity-mode").querySelectorAll("button")) {
      const mode = button.dataset.view;
      const labels = mode === "activity" || mode === "compare" ? viewModes[mode] : viewModes.architecture;
      query("span", button).textContent = required(labels[zh ? 0 : 1]) || labels[0];
      button.setAttribute("aria-pressed", String(button.dataset.view === activityMode));
    }
    activityStep.setAttribute("aria-label", zh ? "\u6D3B\u52A8\u5386\u53F2" : "Activity history");
    activityStep.replaceChildren(...activityEvents.map((record, index) => new Option(`${record.sequence} \xB7 ${record.taskId} \xB7 ${phaseNames[record.phase][zh ? 0 : 1]}`, String(index))));
    activityStep.value = String(activityIndex);
    for (const [id, labels] of Object.entries({ "activity-prev": ["\u4E0A\u4E00\u6761", "Previous record"], "activity-next": ["\u4E0B\u4E00\u6761", "Next record"], "activity-latest": ["\u6700\u65B0\u8BB0\u5F55", "Latest record"] })) $(id).title = $(id).ariaLabel = required(labels[zh ? 0 : 1]);
    buttonById("activity-prev").disabled = activityIndex === 0;
    buttonById("activity-next").disabled = buttonById("activity-latest").disabled = activityIndex === activityEvents.length - 1;
    const source = DATA.simulation ? zh ? "\u6A21\u62DF\u6D3B\u52A8 \xB7 \u975E\u771F\u5B9E\u6267\u884C" : "Simulation \xB7 no real execution" : zh ? "Agent \u58F0\u660E \xB7 \u6587\u4EF6\u5FEB\u7167" : "Agent-declared \xB7 file snapshot";
    $("activity-source").hidden = false;
    $("activity-source").textContent = source;
    query("header .simulation").textContent = source;
    const names = (ids) => ids.map((id) => localized2(required(map.modules.find((module) => module.id === id)), "name")).join(", ");
    $("activity-summary").textContent = localized2(event, "reason");
    $("activity-context-label").textContent = zh ? "\u5F53\u524D\u4FEE\u6539" : "Current change";
    $("activity-context-summary").textContent = localized2(event, "reason");
    const contextDetails = $("activity-context-details");
    contextDetails.replaceChildren();
    query("summary", $("activity-disclosure")).textContent = `${targetLabel}${terminalPhase ? "" : ` \xB7 ${event.targets.length}`} \xB7 ${zh ? "\u8BE6\u60C5" : "Details"}`;
    const details = $("activity-details");
    details.replaceChildren();
    const fields = [
      [zh ? "\u8BA1\u5212\u8303\u56F4" : "Planned scope", names(event.scope)],
      [targetLabel, terminalPhase ? "-" : names(event.targets)],
      [zh ? "\u672C\u6B65\u9AA4\u6587\u4EF6\uFF08\u58F0\u660E\uFF09" : "Step files (declared)", event.files.join("\n") || "-"],
      [zh ? "\u672A\u5F52\u5C5E\u6587\u4EF6" : "Unmapped files", event.unmappedFiles.join("\n") || "-"],
      [zh ? "\u9A8C\u8BC1\u8BB0\u5F55" : "Checks", event.checks.map((check) => `${check.command}
${check.status} \xB7 exit ${check.exitCode ?? "-"} \xB7 ${localized2(check, "summary")}`).join("\n\n") || (zh ? "\u672A\u8BB0\u5F55\u9A8C\u8BC1\u7ED3\u679C" : "No checks recorded")]
    ];
    for (const [label, value] of fields) {
      const field = document.createElement("div");
      const heading = document.createElement("strong");
      heading.textContent = label;
      const content = document.createElement("div");
      content.textContent = value;
      field.append(heading, content);
      details.append(field);
    }
    const contextFields = [
      [targetLabel, terminalPhase ? "-" : names(event.targets)],
      [zh ? "\u8BA1\u5212\u8303\u56F4" : "Planned scope", names(event.scope)],
      [zh ? "\u6587\u4EF6" : "Files", event.files.join("\n") || "-"],
      [zh ? "Git \u63D0\u4EA4" : "Git commit", event.gitCommit || "-"],
      [zh ? "\u53D1\u751F\u65F6\u95F4" : "Timestamp", ("timestamp" in event && typeof event.timestamp === "string" ? event.timestamp : "") || "-"],
      [zh ? "\u9A8C\u8BC1" : "Checks", event.checks.map((check) => `${check.status} \xB7 ${localized2(check, "summary")}`).join("\n") || (zh ? "\u672A\u8BB0\u5F55" : "Not recorded")]
    ];
    for (const [label, value] of contextFields) {
      const field = document.createElement("div");
      const heading = document.createElement("strong");
      heading.textContent = label;
      const content = document.createElement("div");
      content.textContent = value;
      field.append(heading, content);
      contextDetails.append(field);
    }
    context.hidden = activityMode !== "activity";
    $("activity-summary").hidden = $("activity-disclosure").hidden = activityMode !== "activity";
    for (const [id, button] of buttons) {
      const target = !terminalPhase && event.targets.includes(id);
      button.classList.toggle("activity-outside", active && !target);
      button.classList.toggle("activity-scope", active && event.scope.includes(id));
      button.classList.toggle("activity-target", active && target);
    }
    for (const edge of edges) edge.path.classList.toggle("activity-edge-outside", active && (terminalPhase || !event.targets.includes(edge.relation.from) && !event.targets.includes(edge.relation.to)));
    const legend = required(query(".legend").lastElementChild);
    legend.replaceChildren();
    if (active) {
      for (const [kind, label] of [["planned", zh ? "\u8BA1\u5212\u8303\u56F4" : "Planned scope"], ["active", targetLabel], ["", zh ? "\u975E\u5F53\u524D\u76EE\u6807" : "Other modules"]]) {
        const entry = document.createElement("span");
        const swatch = document.createElement("i");
        swatch.className = kind;
        entry.append(swatch, document.createTextNode(label));
        legend.append(entry);
      }
    } else legend.textContent = source;
    syncOverview();
    updateZoom();
    if (activityMode === "compare") $("overview-scroll").scrollTo(viewport.scrollLeft, viewport.scrollTop);
  }
  var constraintRules = map.constraints || [];
  var constraintPanelOpen = false;
  var selectedConstraintId;
  var constraintFilter = "applicable";
  var constraintText = (zh, en) => isChinese2() ? zh : en;
  var freshnessStates = {
    unchanged: ["\u5173\u8054\u6587\u4EF6\u672A\u53D8", "Linked files unchanged"],
    changed: ["\u5F85\u590D\u6838", "Needs review"],
    missing: ["\u6587\u4EF6\u7F3A\u5931", "File missing"],
    unverified: ["\u672A\u6838\u5BF9\u53D8\u5316", "Changes not checked"]
  };
  var constraintStates = {
    applicable: ["\u9002\u7528", "Applicable"],
    superseded: ["\u5DF2\u88AB\u8986\u76D6", "Superseded"],
    "not-applicable": ["\u4E0D\u9002\u7528", "Not applicable"],
    uncertain: ["\u5F85\u786E\u8BA4", "Uncertain"],
    conflict: ["\u51B2\u7A81", "Conflict"],
    unverified: ["\u672A\u9A8C\u8BC1", "Unverified"],
    supported: ["\u6709\u8BC1\u636E\u652F\u6301", "Evidence-supported"],
    violated: ["\u4E0D\u6EE1\u8DB3", "Not satisfied"]
  };
  var constraintButton = document.createElement("button");
  constraintButton.id = "show-constraints";
  constraintButton.setAttribute("aria-controls", "constraints-panel");
  mapTools.append(constraintButton);
  var moduleContent = document.createElement("div");
  moduleContent.id = "module-content";
  moduleContent.append(...[...inspector.children].filter((child) => child !== closeDetails));
  inspector.append(moduleContent);
  var moduleConstraints = document.createElement("section");
  moduleConstraints.id = "module-constraints";
  moduleConstraints.className = "detail";
  moduleContent.append(moduleConstraints);
  var constraintsPanel = document.createElement("section");
  constraintsPanel.id = "constraints-panel";
  constraintsPanel.hidden = true;
  inspector.append(constraintsPanel);
  constraintButton.onclick = () => {
    constraintPanelOpen = !(constraintPanelOpen && workspace.classList.contains("inspector-open"));
    selectedConstraintId = void 0;
    setInspector(constraintPanelOpen);
    if (constraintPanelOpen) constraintsPanel.querySelector("select")?.focus();
  };
  showDetails.onclick = () => {
    const open = constraintPanelOpen || !workspace.classList.contains("inspector-open");
    constraintPanelOpen = false;
    selectedConstraintId = void 0;
    setInspector(open);
  };
  closeDetails.onclick = () => {
    setInspector(false);
    (constraintPanelOpen ? constraintButton : showDetails).focus();
  };
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && workspace.classList.contains("inspector-open") && !document.querySelector("dialog[open]")) closeDetails.click();
  });
  function constraintModules(rule) {
    return /* @__PURE__ */ new Set([...rule.modules, ...map.relationships.filter((relation) => rule.relationships.includes(relation.id)).flatMap((relation) => [relation.from, relation.to])]);
  }
  function constraintApplies(rule, event) {
    if (rule.applicability !== "applicable") return false;
    if (rule.scope === "task") return event?.taskId === rule.taskId;
    return !event || rule.scope === "project" || [...constraintModules(rule)].some((id) => event.scope.includes(id));
  }
  function updateConstraints() {
    const event = activityMode === "architecture" ? void 0 : activityEvents[activityIndex];
    const applicable = constraintRules.filter((rule) => constraintApplies(rule, event));
    const open = constraintPanelOpen && workspace.classList.contains("inspector-open");
    constraintButton.innerHTML = iconMarkup("shield-check");
    const buttonLabel = document.createElement("span");
    const discoveryRecorded = !!map.constraintDiscovery;
    const emptyState = DATA.constraintView ? constraintText("\u7EA6\u675F\u56FE\u5DF2\u6574\u7406\u89C4\u5219\uFF1B\u6B64\u5904\u5C1A\u672A\u8BB0\u5F55\u67B6\u6784\u5173\u8054\u3002", "Rules are available in the constraint graph; architecture links are not recorded here.") : discoveryRecorded ? constraintText("\u5DF2\u8BB0\u5F55\u6765\u6E90\u68C0\u67E5\uFF0C\u4F46\u5C1A\u65E0\u6574\u7406\u540E\u7684\u67B6\u6784\u89C4\u5219\uFF1B\u4E0D\u4EE3\u8868\u6CA1\u6709\u7EA6\u675F\u3002", "Source inspection recorded, but no architecture rules curated; this does not mean there are no constraints.") : constraintText("\u5C1A\u672A\u8BB0\u5F55\u672C\u5730\u7EA6\u675F\u626B\u63CF\uFF0C\u4E0D\u80FD\u5224\u65AD\u662F\u5426\u5B58\u5728\u9002\u7528\u7EA6\u675F\u3002", "Local constraint discovery is not recorded; applicable constraints are unknown.");
    buttonLabel.textContent = constraintRules.length ? `${constraintText("\u9002\u7528\u7EA6\u675F", "Applicable constraints")} \xB7 ${applicable.length}` : DATA.constraintView ? constraintText("\u7EA6\u675F \xB7 \u672A\u5173\u8054", "Constraints \xB7 Unlinked") : discoveryRecorded ? constraintText("\u7EA6\u675F \xB7 \u5F85\u6574\u7406", "Constraints \xB7 Pending review") : constraintText("\u7EA6\u675F \xB7 \u672A\u626B\u63CF", "Constraints \xB7 Not scanned");
    constraintButton.append(buttonLabel);
    const attention = constraintRules.filter((rule) => ["uncertain", "conflict"].includes(rule.applicability)).length;
    if (attention) {
      const count = document.createElement("span");
      count.className = "constraint-attention-count";
      count.textContent = String(attention);
      count.title = constraintText(`${attention} \u6761\u5F85\u786E\u8BA4\u6216\u51B2\u7A81\u89C4\u5219`, `${attention} uncertain or conflicting rules`);
      count.ariaLabel = count.title;
      constraintButton.append(count);
    }
    constraintButton.title = constraintButton.ariaLabel = constraintText("\u67E5\u770B\u7EA6\u675F\u4E0E\u6765\u6E90", "Inspect constraints and sources");
    constraintButton.setAttribute("aria-expanded", String(open));
    workspace.classList.toggle("constraints-open", open);
    moduleContent.hidden = constraintPanelOpen;
    constraintsPanel.hidden = !constraintPanelOpen;
    moduleConstraints.replaceChildren();
    const moduleHeading = document.createElement("div");
    moduleHeading.className = "field-label";
    moduleHeading.textContent = constraintText("\u9002\u7528\u7EA6\u675F", "Applicable constraints");
    moduleConstraints.append(moduleHeading);
    const moduleRules = applicable.filter((rule) => ["project", "task"].includes(rule.scope) || constraintModules(rule).has(selectedModuleId ?? ""));
    for (const rule of moduleRules) {
      const button = document.createElement("button");
      button.className = "constraint-module-link";
      button.textContent = localized2(rule, "name");
      button.onclick = () => {
        selectedConstraintId = rule.id;
        constraintPanelOpen = true;
        setInspector(true);
        constraintsPanel.querySelector(`[data-constraint="${rule.id}"]`)?.focus();
      };
      moduleConstraints.append(button);
    }
    if (!moduleRules.length) {
      const empty = document.createElement("p");
      empty.textContent = constraintRules.length ? constraintText("\u6B64\u6A21\u5757\u672A\u8BB0\u5F55\u9002\u7528\u7EA6\u675F", "No applicable constraints recorded for this module") : emptyState;
      moduleConstraints.append(empty);
    }
    constraintsPanel.replaceChildren();
    const eyebrow = document.createElement("div");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = constraintText("\u89C4\u5219\u4E0E\u4F9D\u636E", "RULES & EVIDENCE");
    const heading = document.createElement("h2");
    heading.textContent = constraintText("\u7EA6\u675F", "Constraints");
    const context = document.createElement("p");
    context.className = "constraint-context";
    context.textContent = event ? `${event.taskId} \xB7 ${constraintText("\u6B65\u9AA4", "Step")} ${event.sequence}` : constraintText("\u9879\u76EE\u67B6\u6784\u5FEB\u7167", "Project architecture snapshot");
    constraintsPanel.append(eyebrow, heading, context);
    const freshness = DATA.constraintFreshness;
    const snapshot = document.createElement("div");
    snapshot.className = "constraint-snapshot";
    const snapshotTitle = document.createElement("strong");
    const pending = constraintRules.filter((rule) => freshness?.rules[rule.id]?.status === "changed").length;
    const unchecked = constraintRules.filter((rule) => !freshness?.rules[rule.id] || freshness.rules[rule.id]?.status === "unverified").length;
    snapshotTitle.textContent = freshness ? constraintText(`${pending} \u6761\u5F85\u590D\u6838 \xB7 ${unchecked} \u6761\u672A\u6838\u5BF9`, `${pending} need review \xB7 ${unchecked} unchecked`) : constraintText("\u5C1A\u672A\u6838\u5BF9\u5173\u8054\u6587\u4EF6\u53D8\u5316", "Linked file changes not yet checked");
    const snapshotNote = document.createElement("p");
    snapshotNote.textContent = freshness ? `${constraintText("\u6587\u4EF6\u53D8\u5316\u5FEB\u7167", "File change snapshot")} \xB7 ${freshness.checkedAt}
${constraintText("\u68C0\u6D4B\u63D0\u4EA4", "Inspected commit")} ${freshness.head.slice(0, 12)}
${constraintText("\u5305\u542B\u5F53\u65F6\u7684\u6682\u5B58\u533A\u4E0E\u5DE5\u4F5C\u533A\uFF1B\u4E0D\u4EE3\u8868\u5F53\u524D\u72B6\u6001\u6216\u5408\u89C4\u7ED3\u8BBA\u3002", "Includes the index and working tree at inspection; not a live status or compliance verdict.")}` : constraintText("\u9002\u7528\u6027\u3001\u6587\u4EF6\u53D8\u5316\u4E0E\u9A8C\u8BC1\u7ED3\u679C\u5206\u522B\u8BB0\u5F55\u3002", "Applicability, file changes and verification are recorded separately.");
    snapshot.append(snapshotTitle, snapshotNote);
    constraintsPanel.append(snapshot);
    const discovery = document.createElement("details");
    discovery.className = "constraint-discovery";
    const discoverySummary = document.createElement("summary");
    discoverySummary.textContent = map.constraintDiscovery ? `${constraintText("\u5DF2\u68C0\u67E5", "Inspected")} ${map.constraintDiscovery.checkedPaths.length} \xB7 ${constraintText("\u672A\u68C0\u67E5", "Uninspected")} ${map.constraintDiscovery.uninspectedPaths.length}` : constraintText("\u672A\u8BB0\u5F55\u672C\u5730\u7EA6\u675F\u68C0\u67E5", "Local constraint discovery not recorded");
    discovery.append(discoverySummary);
    if (map.constraintDiscovery) {
      const details = document.createElement("p");
      details.textContent = `${map.constraintDiscovery.checkedAt}
${constraintText("\u5DF2\u68C0\u67E5", "Inspected")}: ${map.constraintDiscovery.checkedPaths.join(", ") || "\u2014"}
${constraintText("\u672A\u68C0\u67E5", "Uninspected")}: ${map.constraintDiscovery.uninspectedPaths.join(", ") || "\u2014"}`;
      discovery.append(details);
    }
    constraintsPanel.append(discovery);
    const filter = document.createElement("select");
    filter.id = "constraint-filter";
    filter.ariaLabel = constraintText("\u7EA6\u675F\u7B5B\u9009", "Filter constraints");
    for (const [value, zh, en] of [["applicable", "\u672C\u6B21\u9002\u7528", "Applicable"], ["module", "\u9009\u4E2D\u6A21\u5757", "Selected module"], ["review", "\u53D8\u5316\u5F85\u590D\u6838", "Changes needing review"], ["attention", "\u5F85\u786E\u8BA4\u4E0E\u51B2\u7A81", "Uncertain & conflicting"], ["all", "\u5168\u90E8\u89C4\u5219", "All rules"]]) filter.add(new Option(constraintText(zh, en), value));
    filter.value = constraintFilter;
    filter.onchange = () => {
      constraintFilter = filter.value;
      selectedConstraintId = void 0;
      updateConstraints();
      $("constraint-filter").focus();
    };
    constraintsPanel.append(filter);
    const visible = constraintRules.filter((rule) => constraintFilter === "all" || (constraintFilter === "review" ? freshness?.rules[rule.id]?.status === "changed" : constraintFilter === "attention" ? ["uncertain", "conflict"].includes(rule.applicability) : constraintFilter === "module" ? applicable.includes(rule) && (["project", "task"].includes(rule.scope) || constraintModules(rule).has(selectedModuleId ?? "")) : applicable.includes(rule)));
    const selected = constraintRules.find((rule) => rule.id === selectedConstraintId);
    if (selected && !visible.includes(selected)) visible.unshift(selected);
    const list = document.createElement("div");
    list.className = "constraint-list";
    for (const rule of visible) {
      const row = document.createElement("button");
      row.className = "constraint-row";
      row.dataset.constraint = rule.id;
      row.setAttribute("aria-pressed", String(rule.id === selectedConstraintId));
      const meta = document.createElement("span");
      meta.className = "constraint-row-meta";
      meta.textContent = `${rule.origin === "local" ? constraintText("\u672C\u5730\u89C4\u8303", "Local rule") : rule.origin === "user" ? constraintText("\u7528\u6237\u8981\u6C42", "User request") : constraintText("\u4EE3\u7801\u63A8\u65AD", "Inferred")} \xB7 ${rule.strength === "required" ? constraintText("\u786C\u6027\u8981\u6C42", "Required") : constraintText("\u504F\u597D", "Preferred")}`;
      const name = document.createElement("strong");
      name.textContent = localized2(rule, "name");
      const state = document.createElement("span");
      state.className = "constraint-state";
      state.dataset.state = rule.applicability;
      state.textContent = constraintStates[rule.applicability][isChinese2() ? 0 : 1];
      const review = event?.constraintReviews?.find((item) => item.constraintId === rule.id);
      state.dataset.result = review?.status || "unverified";
      if (event && applicable.includes(rule)) state.textContent += ` \xB7 ${constraintStates[review?.status || "unverified"][isChinese2() ? 0 : 1]}`;
      row.append(meta, name, state);
      const fileReview = freshness?.rules[rule.id];
      const fileState = document.createElement("span");
      fileState.className = "constraint-freshness";
      fileState.dataset.state = fileReview?.status || "unverified";
      fileState.textContent = freshnessStates[fileReview?.status || "unverified"][isChinese2() ? 0 : 1];
      row.append(fileState);
      row.onclick = () => {
        selectedConstraintId = selectedConstraintId === rule.id ? void 0 : rule.id;
        updateConstraints();
        constraintsPanel.querySelector(`[data-constraint="${rule.id}"]`)?.focus();
      };
      list.append(row);
      if (rule.id === selectedConstraintId) {
        const detail = document.createElement("div");
        detail.className = "constraint-detail";
        const field = (label, value) => {
          const title = document.createElement("h3");
          title.textContent = label;
          const content = document.createElement("p");
          content.textContent = value;
          detail.append(title, content);
        };
        field(constraintText("\u9002\u7528\u4F9D\u636E", "Applicability"), localized2(rule, "note"));
        if (rule.explanation) field(constraintText("\u5177\u4F53\u89E3\u91CA", "Explanation"), localized2(rule, "explanation"));
        const names = [...constraintModules(rule)].map((id) => localized2(required(map.modules.find((module) => module.id === id)), "name"));
        field(constraintText("\u4F5C\u7528\u8303\u56F4", "Scope"), names.join(" \xB7 ") || (rule.scope === "task" ? required(rule.taskId) : constraintText("\u6574\u4E2A\u9879\u76EE", "Project-wide")));
        for (const source of rule.evidence) {
          const sourceDetails = document.createElement("details");
          sourceDetails.className = "constraint-source";
          const location2 = document.createElement("summary");
          location2.textContent = `${source.path}${source.line ? `:${source.line}${source.endLine ? `\u2013${source.endLine}` : ""}` : ""}${source.symbol ? ` \xB7 ${source.symbol}` : ""}`;
          const sourceNote = document.createElement("p");
          sourceNote.textContent = localized2(source, "note");
          sourceDetails.append(location2);
          if (source.quote) {
            sourceDetails.open = true;
            const quoteLabel = document.createElement("h3");
            quoteLabel.textContent = constraintText("\u6765\u6E90\u6458\u5F55\uFF08\u539F\u8BED\u8A00\uFF09", "Source excerpt (original language)");
            const quote = document.createElement("blockquote");
            quote.textContent = source.quote;
            sourceDetails.append(quoteLabel, quote);
          }
          sourceDetails.append(sourceNote);
          detail.append(sourceDetails);
        }
        field(constraintText("\u5173\u8054\u4EE3\u7801", "Linked code"), (rule.code || []).map(
          (source) => `${source.path}${source.line ? `:${source.line}` : ""}${source.symbol ? ` \xB7 ${source.symbol}` : ""}
${localized2(source, "note")}`
        ).join("\n\n") || constraintText("\u672A\u8BB0\u5F55\u4EE3\u7801\u5173\u8054", "No code links recorded"));
        field(constraintText("\u53D8\u5316\u6838\u5BF9", "Change inspection"), fileState.textContent || "");
        if (rule.baselineCommit) field(constraintText("\u57FA\u51C6\u63D0\u4EA4", "Baseline commit"), rule.baselineCommit);
        for (const id of [rule.supersededBy, ...rule.conflictsWith || []].filter(Boolean)) {
          const linked = constraintRules.find((item) => item.id === id);
          const link = document.createElement("button");
          link.className = "constraint-module-link";
          link.textContent = `${constraintText("\u5173\u8054\u89C4\u5219", "Related rule")}: ${localized2(required(linked), "name")}`;
          link.onclick = () => {
            selectedConstraintId = id;
            constraintFilter = "all";
            updateConstraints();
          };
          detail.append(link);
        }
        field(constraintText("\u9A8C\u8BC1\u65B9\u5F0F", "Verification"), localized2(rule, "verification"));
        if (event && applicable.includes(rule)) {
          field(constraintText("\u672C\u6B21\u65B9\u6848", "Task plan"), review ? localized2(review, "plan") : constraintText("\u672A\u8BB0\u5F55", "Not recorded"));
          field(constraintText("\u9A8C\u8BC1\u7ED3\u679C", "Result"), `${constraintStates[review?.status || "unverified"][isChinese2() ? 0 : 1]}${review ? ` \xB7 ${review.method === "test" ? constraintText("\u6D4B\u8BD5", "Test") : constraintText("\u4EBA\u5DE5\u6838\u5BF9", "Manual review")}` : ""}`);
          if (review?.evidence) field(constraintText("\u7ED3\u679C\u4F9D\u636E", "Result evidence"), localized2(review, "evidence"));
          if (review?.checkedAt) field(constraintText("\u590D\u6838\u8BB0\u5F55", "Review record"), `${review.checkedAt}${review.gitCommit ? `
${review.gitCommit}` : ""}`);
          for (const index of review?.checkIndexes || []) {
            const check = required(event.checks[index]);
            field(check.command, `${check.status} \xB7 exit ${check.exitCode ?? "\u2014"}
${localized2(check, "summary")}`);
          }
        }
        list.append(detail);
      }
    }
    if (!visible.length) {
      const empty = document.createElement("p");
      empty.className = "constraint-empty";
      empty.textContent = constraintRules.length ? constraintText("\u6B64\u8303\u56F4\u672A\u8BB0\u5F55\u7EA6\u675F", "No constraints recorded in this scope") : emptyState;
      list.append(empty);
    }
    constraintsPanel.append(list);
    const highlighted = open && selected ? constraintModules(selected) : /* @__PURE__ */ new Set();
    for (const [id, button] of buttons) button.classList.toggle("constraint-highlight", highlighted.has(id));
    for (const edge of edges) edge.path.classList.toggle("constraint-highlight", Boolean(open && selected?.relationships.includes(edge.relation.id)));
    updateFlow();
  }
  applyLanguage();
  var guideKey = "birdview-guide-v1";
  var guideLaunch = document.createElement("button");
  guideLaunch.id = "guide-launch";
  query(".header-actions").append(guideLaunch);
  var guideInvite = document.createElement("div");
  guideInvite.id = "guide-invite";
  guideInvite.innerHTML = '<span></span><button id="guide-start"></button><button id="guide-dismiss"></button>';
  query("main").prepend(guideInvite);
  try {
    guideInvite.hidden = localStorage.getItem(guideKey) === "seen";
  } catch {
  }
  var guideDialog = document.createElement("dialog");
  guideDialog.id = "guide-dialog";
  guideDialog.setAttribute("aria-labelledby", "guide-title");
  guideDialog.setAttribute("aria-describedby", "guide-copy");
  guideDialog.innerHTML = '<div id="guide-spot" aria-hidden="true"></div><section id="guide-card"><div class="guide-top"><span id="guide-count" aria-live="polite"></span><button id="guide-close">\xD7</button></div><progress id="guide-progress"></progress><h2 id="guide-title"></h2><p id="guide-copy"></p><div class="guide-actions"><button id="guide-prev"></button><button id="guide-skip"></button><button id="guide-next" class="primary"></button></div></section>';
  document.body.append(guideDialog);
  var guideSteps = activityEvents.length ? ["architecture", "activity", "compare", "details", "history"] : ["architecture", "details"];
  var guideCopy = {
    architecture: ["\u5B8C\u6574\u67B6\u6784", "\u4E86\u89E3\u7CFB\u7EDF\u6709\u54EA\u4E9B\u6A21\u5757\uFF0C\u4EE5\u53CA\u5B83\u4EEC\u5982\u4F55\u8FDE\u63A5\u3002\u5206\u7EC4\u5E95\u8272\u8868\u793A\u804C\u8D23\u7C7B\u522B\uFF0C\u4E0D\u8868\u793A\u4FEE\u6539\u72B6\u6001\u3002", "Architecture", "See the system modules and their connections. Group backgrounds classify responsibilities, not change status."],
    activity: ["\u672C\u6B21\u4FEE\u6539", "\u4EAE\u8D77\u7684\u662F\u6240\u9009\u6B65\u9AA4\u7684\u76EE\u6807\uFF0C\u7070\u8272\u6A21\u5757\u4E0D\u662F\u5F53\u524D\u76EE\u6807\uFF1B\u9A8C\u8BC1\u9636\u6BB5\u7684\u4EAE\u8D77\u8868\u793A\u9A8C\u8BC1\u76EE\u6807\u3002\u7EC8\u6001\u4E0D\u518D\u9AD8\u4EAE\u76EE\u6807\u3002", "Current changes", "Bright modules are targets of the selected step; gray modules are not. During verification, highlights mean verification targets. Terminal steps clear highlights."],
    compare: ["\u540C\u65F6\u5BF9\u7167", "\u5B8C\u6574\u67B6\u6784\u4E0E\u66F4\u6539\u89C6\u56FE\u5E76\u6392\u5C55\u793A\uFF0C\u9009\u62E9\u3001\u7F29\u653E\u548C\u6EDA\u52A8\u4FDD\u6301\u8054\u52A8\u3002\u7A84\u5C4F\u65F6\u4E0A\u4E0B\u6392\u5217\u3002", "Compare views", "Compare architecture and changes with linked selection, zoom and scrolling. Narrow screens stack the views."],
    details: ["\u67E5\u770B\u4F9D\u636E", "\u70B9\u51FB\u6A21\u5757\u53EF\u67E5\u770B\u804C\u8D23\u3001\u6587\u4EF6\u5F52\u5C5E\u4E0E\u6E90\u7801\u8BC1\u636E\u3002\u60AC\u6D6E\u6A21\u5757\u53EF\u8FFD\u8E2A\u76F4\u63A5\u8FDE\u63A5\uFF0C\u5DE5\u5177\u680F\u53EF\u5207\u6362\u5168\u90E8\u5173\u7CFB\u6216\u9002\u914D\u5168\u56FE\u3002", "Inspect evidence", "Select a module for responsibilities, file ownership and source evidence. Hover to trace direct connections; use the toolbar for all relations or fit to view."],
    history: ["\u8DDF\u8E2A\u8FC7\u7A0B", "\u5386\u53F2\u8BB0\u5F55\u5C55\u793A\u8BA1\u5212\u3001\u7F16\u8F91\u548C\u9A8C\u8BC1\u6B65\u9AA4\u3002\u5C55\u5F00\u8BE6\u60C5\u67E5\u770B\u6587\u4EF6\u548C\u68C0\u67E5\u7ED3\u679C\uFF1B\u4EFB\u52A1\u5B8C\u6210\u4E0D\u4EE3\u8868\u68C0\u67E5\u901A\u8FC7\u3002", "Follow progress", "History shows planning, editing and verification steps. Expand details for files and check results; completion alone does not prove checks passed."]
  };
  var guideIndex = 0;
  var guideSaved;
  var guideTarget;
  var guideFrame = 0;
  var guideViewState = {
    architecture: { mode: "architecture", inspector: false, history: false },
    activity: { mode: "activity", inspector: false, history: false },
    compare: { mode: "compare", inspector: false, history: false },
    details: { mode: "architecture", inspector: true, history: false },
    history: { mode: "activity", inspector: false, history: true }
  };
  function guideLabels() {
    const zh = isChinese2();
    guideLaunch.textContent = zh ? "\u4F7F\u7528\u6307\u5F15" : "Guide";
    query("span", guideInvite).textContent = zh ? "\u4E86\u89E3\u600E\u4E48\u770B\u56FE" : "Learn to read the map";
    $("guide-start").textContent = zh ? "\u5F00\u59CB" : "Start";
    $("guide-dismiss").textContent = zh ? "\u6682\u4E0D" : "Not now";
    for (const [id, labels] of Object.entries({ "guide-close": ["\u5173\u95ED\u6307\u5F15", "Close guide"], "guide-prev": ["\u4E0A\u4E00\u6B65", "Previous"], "guide-skip": ["\u8DF3\u8FC7\u6307\u5F15", "Skip guide"] })) {
      $(id).ariaLabel = required(labels[zh ? 0 : 1]);
      if (id !== "guide-close") $(id).textContent = required(labels[zh ? 0 : 1]);
    }
    const copy = guideCopy[required(guideSteps[guideIndex])];
    $("guide-title").textContent = copy[zh ? 0 : 2];
    $("guide-copy").textContent = copy[zh ? 1 : 3];
    $("guide-count").textContent = zh ? `\u7B2C ${guideIndex + 1} / ${guideSteps.length} \u6B65` : `Step ${guideIndex + 1} of ${guideSteps.length}`;
    $("guide-progress").max = guideSteps.length;
    $("guide-progress").value = guideIndex + 1;
    $("guide-progress").ariaLabel = $("guide-count").textContent;
    buttonById("guide-prev").disabled = guideIndex === 0;
    $("guide-next").textContent = guideIndex === guideSteps.length - 1 ? zh ? "\u5B8C\u6210" : "Done" : zh ? "\u4E0B\u4E00\u6B65" : "Next";
  }
  function positionGuide() {
    if (!guideDialog.open || !guideTarget) return;
    const rect = guideTarget.getBoundingClientRect();
    const w = innerWidth, h = innerHeight;
    const left = Math.max(6, Math.min(w - 12, rect.left - 5));
    const top = Math.max(6, Math.min(h - 12, rect.top - 5));
    const right = Math.max(left + 6, Math.min(w - 6, rect.right + 5));
    const bottom = Math.max(top + 6, Math.min(h - 6, rect.bottom + 5));
    Object.assign($("guide-spot").style, { left: `${left}px`, top: `${top}px`, width: `${right - left}px`, height: `${bottom - top}px` });
    const card = $("guide-card");
    const cw = card.offsetWidth, ch = card.offsetHeight;
    let x = left, y = bottom + 14;
    if (y + ch > h - 12) {
      if (top - ch - 14 >= 12) y = top - ch - 14;
      else if (right + cw + 14 < w - 12) {
        x = right + 14;
        y = top;
      } else {
        x = w - cw - 12;
        y = h - ch - 12;
      }
    }
    card.style.left = `${Math.max(12, Math.min(w - cw - 12, x))}px`;
    card.style.top = `${Math.max(12, Math.min(h - ch - 12, y))}px`;
  }
  var guideAnimation;
  function showGuideStep(animate = false) {
    const card = $("guide-card");
    const previous = card.getBoundingClientRect();
    guideAnimation?.cancel();
    guideAnimation = void 0;
    const saved = required(guideSaved);
    const step = required(guideSteps[guideIndex]);
    const state = guideViewState[step];
    hoveredModuleId = void 0;
    setInspector(state.inspector);
    activityMode = state.mode;
    if (step === "activity") {
      const plan = activityEvents.findIndex((event) => event.phase === "planned" && event.targets.length);
      activityIndex = plan >= 0 ? plan : saved.index;
    } else activityIndex = saved.index;
    $("activity-disclosure").open = state.history;
    fitting = true;
    updateActivity();
    updateFlow();
    updateZoom();
    if (step === "details") select(map.modules.find((module) => module.id === saved.selected) || required(map.modules[0]));
    guideTarget = step === "details" ? inspector : step === "history" ? activityPanel : step === "compare" ? $("activity-mode") : step === "activity" ? viewport : activityEvents.length ? query('[data-view="architecture"]') : viewport;
    guideTarget.scrollIntoView({ block: "nearest", behavior: "instant" });
    guideLabels();
    positionGuide();
    if (animate && !reducedMotion.matches) {
      const next = card.getBoundingClientRect();
      const x = Math.max(12, Math.min(innerWidth - next.width - 12, previous.left)) - next.left;
      const y = Math.max(12, Math.min(innerHeight - next.height - 12, previous.top)) - next.top;
      guideAnimation = card.animate([
        { transform: `translate(${x}px, ${y}px)` },
        { transform: "translate(0, 0)" }
      ], { duration: 200, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
    }
    requestAnimationFrame(positionGuide);
    $("guide-next").focus({ preventScroll: true });
  }
  function dismissGuideInvite() {
    guideInvite.hidden = true;
    try {
      localStorage.setItem(guideKey, "seen");
    } catch {
    }
  }
  function startGuide() {
    if (guideDialog.open) return;
    dismissGuideInvite();
    guideSaved = { mode: activityMode, index: activityIndex, selected: selectedModuleId, inspector: workspace.classList.contains("inspector-open"), zoom, fitting, disclosure: $("activity-disclosure").open, focus: document.activeElement, x: scrollX, y: scrollY, constraints: { open: constraintPanelOpen, selected: selectedConstraintId, filter: constraintFilter }, panes: [...mapPanes.querySelectorAll(".map-scroll")].map((el) => [el, el.scrollLeft, el.scrollTop]) };
    guideIndex = 0;
    constraintPanelOpen = false;
    guideDialog.showModal();
    showGuideStep();
  }
  function finishGuide() {
    if (!guideDialog.open) return;
    guideAnimation?.cancel();
    guideAnimation = void 0;
    guideDialog.close();
    const saved = required(guideSaved);
    activityMode = saved.mode;
    activityIndex = saved.index;
    constraintPanelOpen = saved.constraints.open;
    selectedConstraintId = saved.constraints.selected;
    constraintFilter = saved.constraints.filter;
    fitting = false;
    setInspector(saved.inspector);
    $("activity-disclosure").open = saved.disclosure;
    updateActivity();
    select(map.modules.find((module) => module.id === saved.selected) || required(map.modules[0]));
    zoom = saved.zoom;
    updateZoom();
    fitting = saved.fitting;
    for (const [el, x, y] of saved.panes) el.scrollTo(x, y);
    window.scrollTo(saved.x, saved.y);
    (saved.focus instanceof HTMLElement && saved.focus.isConnected && !saved.focus.closest("#guide-invite") ? saved.focus : guideLaunch).focus({ preventScroll: true });
  }
  guideLaunch.onclick = $("guide-start").onclick = startGuide;
  $("guide-dismiss").onclick = dismissGuideInvite;
  $("guide-close").onclick = $("guide-skip").onclick = finishGuide;
  $("guide-prev").onclick = (event) => {
    if (guideIndex) {
      guideIndex--;
      showGuideStep(event.detail > 0);
    }
  };
  $("guide-next").onclick = (event) => {
    if (guideIndex === guideSteps.length - 1) finishGuide();
    else {
      guideIndex++;
      showGuideStep(event.detail > 0);
    }
  };
  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches) guideAnimation?.cancel();
  });
  guideDialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    finishGuide();
  });
  languageSelect.addEventListener("change", () => {
    guideAnimation?.cancel();
    guideLabels();
    positionGuide();
  });
  var repositionGuide = () => {
    guideAnimation?.cancel();
    cancelAnimationFrame(guideFrame);
    guideFrame = requestAnimationFrame(positionGuide);
  };
  window.addEventListener("resize", repositionGuide);
  document.addEventListener("scroll", repositionGuide, true);
  new ResizeObserver(() => {
    cancelAnimationFrame(guideFrame);
    guideFrame = requestAnimationFrame(positionGuide);
  }).observe($("guide-card"));
  guideLabels();
  if (DATA.constraintView) {
    const view = DATA.constraintView;
    const main = query("body > main");
    const nav = document.createElement("nav");
    nav.id = "project-views";
    const architecture = document.createElement("button");
    const constraints = document.createElement("button");
    architecture.type = constraints.type = "button";
    nav.append(architecture, constraints);
    query("header .task").after(nav);
    main.id = "architecture-view";
    architecture.setAttribute("aria-controls", main.id);
    const panel = document.createElement("section");
    panel.id = "constraint-view";
    panel.hidden = true;
    constraints.setAttribute("aria-controls", panel.id);
    main.after(panel);
    const related = document.createElement("button");
    related.id = "open-related-constraints";
    related.type = "button";
    $("module-content").append(related);
    let active = false;
    let canvas;
    const label = (zh, en) => isChinese2() ? zh : en;
    const sync = () => {
      nav.setAttribute("aria-label", label("\u9879\u76EE\u89C6\u56FE", "Project views"));
      architecture.textContent = label("\u67B6\u6784", "Architecture");
      constraints.textContent = label("\u7EA6\u675F", "Constraints");
      architecture.setAttribute("aria-pressed", String(!active));
      constraints.setAttribute("aria-pressed", String(active));
      const count = view.rules.filter((rule) => rule.modules.includes(selectedModuleId ?? "")).length;
      related.textContent = count ? label(`\u67E5\u770B\u5173\u8054\u7EA6\u675F\u56FE \xB7 ${count}`, `View related rules \xB7 ${count}`) : label("\u5C1A\u672A\u8BB0\u5F55\u6A21\u5757\u4E0E\u89C4\u5219\u7684\u5173\u8054", "No module-rule links recorded");
      related.disabled = !count;
    };
    const show = (value) => {
      active = value;
      main.hidden = value;
      panel.hidden = !value;
      if (value && !canvas) canvas = mountConstraintCanvas(panel, view.graph);
      const hash = new URLSearchParams(location.hash.slice(1));
      hash.set("view", value ? "constraints" : "architecture");
      try {
        history.replaceState(null, "", `#${hash}`);
      } catch {
      }
      sync();
      requestAnimationFrame(() => canvas?.resize());
      window.dispatchEvent(new Event("resize"));
    };
    architecture.onclick = () => show(false);
    constraints.onclick = () => show(true);
    related.onclick = () => {
      show(true);
      canvas?.filter(view.rules.filter((rule) => rule.modules.includes(selectedModuleId ?? "")).map((rule) => rule.id));
    };
    new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    new MutationObserver(sync).observe($("module-constraints"), { childList: true, subtree: true });
    show(new URLSearchParams(location.hash.slice(1)).get("view") === "constraints");
  }
})();
