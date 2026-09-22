// Generated from src/viewer/constraint-canvas.mts. Do not edit directly.
"use strict";
var BirdviewConstraintCanvas = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // src/viewer/constraint-canvas.mts
  var constraint_canvas_exports = {};
  __export(constraint_canvas_exports, {
    mountConstraintCanvas: () => mountConstraintCanvas
  });
  function mountConstraintCanvas(container, data) {
    const root = container;
    root.classList.add("bv-constraints");
    const element = (tag, className = "", content) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (content !== void 0) node.textContent = content;
      return node;
    };
    const text = (zh, en) => document.documentElement.lang.startsWith("zh") ? zh : en;
    const button = (className, label2, action) => {
      const node = element("button", className, label2);
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
    let selected = top, filterIds = null, query = "", matching = null, searchMessage = "";
    let positions = /* @__PURE__ */ new Map(), visible = [], camera = { x: 0, y: 0, scale: 1 }, fitted = false;
    let directoryOpen = !matchMedia("(max-width:700px)").matches;
    const toolbar = element("div", "cv-toolbar");
    const toggleDirectory = button("cv-directory-toggle", "\u2630", () => {
      directoryOpen = !directoryOpen;
      directory.hidden = !directoryOpen;
      toggleDirectory.setAttribute("aria-expanded", String(directoryOpen));
      if (directoryOpen) search.focus();
    });
    const title = element("span", "cv-title");
    const grouping = element("select", "cv-grouping");
    grouping.append(new Option("\u6309\u4E3B\u9898", "topics"), new Option("\u6309\u76EE\u5F55", "directories"));
    grouping.hidden = !data.directoryNodes;
    const resetFilter = button("cv-reset-filter", "", () => api.filter(null));
    const zoomOut = button("cv-zoom-out", "\u2212", () => zoomAt(camera.scale / 1.2));
    const zoomLabel = element("span", "cv-zoom-label");
    const zoomIn = button("cv-zoom-in", "+", () => zoomAt(camera.scale * 1.2));
    const fitButton = button("cv-fit", "", () => fit());
    const legendButton = button("cv-legend-toggle", "", () => {
      legend.hidden = !legend.hidden;
      legendButton.setAttribute("aria-expanded", String(!legend.hidden));
    });
    const coverageButton = button("cv-coverage", "", () => {
      selected = top;
      showDetails(top);
      render();
    });
    toolbar.append(toggleDirectory, grouping, title, resetFilter, zoomOut, zoomLabel, zoomIn, fitButton, legendButton, coverageButton);
    const workspace = element("div", "cv-workspace");
    const directory = element("nav", "cv-directory");
    directory.hidden = !directoryOpen;
    const directoryHeading = element("div", "cv-directory-heading");
    const directoryTitle = element("span");
    const directoryClose = button("", "\xD7", () => {
      directoryOpen = false;
      directory.hidden = true;
      toggleDirectory.setAttribute("aria-expanded", "false");
      toggleDirectory.focus();
    });
    directoryHeading.append(directoryTitle, directoryClose);
    const search = element("input", "cv-search");
    search.type = "search";
    search.autocomplete = "off";
    const tree = element("div", "cv-tree");
    const empty = element("div", "cv-empty");
    empty.setAttribute("role", "status");
    directory.append(directoryHeading, search, tree, empty);
    const viewport = element("div", "cv-viewport");
    viewport.tabIndex = 0;
    const stage = element("div", "cv-stage");
    const help = element("span", "cv-help");
    viewport.append(stage, help);
    const reader = element("section", "cv-reader");
    reader.hidden = true;
    const readerHeader = element("div", "cv-reader-header");
    const readerTitle = element("h2", "cv-reader-title");
    const readerClose = button("cv-reader-close", "\xD7", () => {
      reader.hidden = true;
      focusSelected();
      focusButton();
    });
    const readerMeta = element("p", "cv-reader-meta");
    const readerBody = element("div", "cv-reader-body");
    readerHeader.append(readerTitle, readerClose);
    reader.append(readerHeader, readerMeta, readerBody);
    const dialog = element("dialog", "cv-dialog");
    const dialogTitle = element("h2", "cv-dialog-title");
    const dialogClose = button("cv-dialog-close", "\xD7", () => dialog.close());
    const dialogHeader = element("div", "cv-reader-header");
    dialogHeader.append(dialogTitle, dialogClose);
    const dialogContent = element("div", "cv-dialog-content");
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
      showDetails(id);
      dialogTitle.textContent = readerTitle.textContent;
      dialogContent.replaceChildren(readerMeta.cloneNode(true), readerBody.cloneNode(true));
      reader.hidden = wasHidden;
      dialog.showModal();
      dialogContent.scrollTop = 0;
      dialogClose.focus();
    }
    workspace.append(directory, viewport, reader);
    const legend = element("section", "cv-legend");
    legend.hidden = true;
    root.append(toolbar, workspace, legend);
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
    function zoomAt(scale, x = viewport.clientWidth / 2, y = viewport.clientHeight / 2) {
      const next = Math.max(0.15, Math.min(2, scale)), ratio = next / camera.scale;
      camera.x = x - (x - camera.x) * ratio;
      camera.y = y - (y - camera.y) * ratio;
      camera.scale = next;
      applyCamera();
    }
    function fit() {
      if (!positions.size || viewport.clientWidth < 1 || viewport.clientHeight < 1) return;
      const minY = Math.min(...[...positions.values()].map((p) => p.y));
      const width = Math.max(...[...positions.values()].map((p) => p.x)) + 176;
      const height = Math.max(...[...positions.values()].map((p) => p.y)) - minY + 76;
      const widthScale = (viewport.clientWidth - 80) / width;
      const heightScale = (viewport.clientHeight - 100) / height;
      camera.scale = Math.max(0.48, Math.min(1, widthScale, heightScale));
      camera.x = width * camera.scale < viewport.clientWidth - 120 ? 56 : 28;
      camera.y = height * camera.scale > viewport.clientHeight - 60 ? 28 : (viewport.clientHeight - height * camera.scale) / 2;
      camera.y -= minY * camera.scale;
      fitted = true;
      applyCamera();
    }
    function focusSelected() {
      const point = positions.get(selected);
      if (!point) return;
      camera.x = viewport.clientWidth * 0.43 - (point.x + 88) * camera.scale;
      camera.y = viewport.clientHeight / 2 - (point.y + 38) * camera.scale;
      applyCamera();
    }
    function focusButton() {
      [...stage.querySelectorAll(".cv-card")].find((node) => node.dataset.id === selected)?.focus({ preventScroll: true });
    }
    function activate(id, fromDirectory = false) {
      const prior = positions.get(id);
      const screen = prior && { x: camera.x + prior.x * camera.scale, y: camera.y + prior.y * camera.scale };
      selected = id;
      const descendants = visibleChildren(id);
      if (!query) {
        const collapse = descendants.length && expanded.has(id);
        expanded.clear();
        ancestors(id, expanded);
        if (collapse || !descendants.length) expanded.delete(id);
      }
      if (!descendants.length) showDetails(id);
      render();
      if (screen && reader.hidden) {
        const point = positions.get(id);
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
    function showDetails(id) {
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
            code = element("pre");
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
            quote = element("blockquote");
            readerBody.append(quote);
          }
          quote.textContent += (quote.textContent ? "\n" : "") + line.slice(2);
          continue;
        }
        quote = null;
        if (!line.trim()) continue;
        const heading = line.match(/^#{2,6}\s+(.*)/);
        readerBody.append(element(heading ? "h3" : "p", "", heading ? heading[1] : line.replace(/\*\*([^*]+)\*\*/g, "$1").replace(/`([^`]+)`/g, "$1")));
      }
    }
    function render() {
      positions = /* @__PURE__ */ new Map();
      visible = [];
      let cursor = 0;
      function place(id, depth) {
        if (!allowed(id)) return;
        visible.push(id);
        const list = query || expanded.has(id) ? visibleChildren(id) : [];
        let y;
        if (list.length) {
          for (const child of list) place(child, depth + 1);
          y = (positions.get(list[0]).y + positions.get(list.at(-1)).y) / 2;
        } else {
          y = cursor;
          cursor += 92;
        }
        positions.set(id, { x: depth * 280, y });
      }
      if (query) place(top, 0);
      else if (allowed(top)) {
        positions.set(top, { x: 0, y: 0 });
        visible.push(top);
        let parent = top, depth = 1;
        while (expanded.has(parent)) {
          const list = visibleChildren(parent);
          const start = positions.get(parent).y - (list.length - 1) * 92 / 2;
          list.forEach((id, index) => {
            positions.set(id, { x: depth * 280, y: start + index * 92 });
            visible.push(id);
          });
          parent = list.find((id) => expanded.has(id)) || "";
          if (!parent) break;
          depth++;
        }
        visible = [];
        const visit = (id) => {
          if (!positions.has(id)) return;
          visible.push(id);
          for (const child of visibleChildren(id)) visit(child);
        };
        visit(top);
      }
      const focus = /* @__PURE__ */ new Set([selected, ...visibleChildren(selected)]);
      const selectedParent = nodes.get(selected)?.parent;
      if (selectedParent) focus.add(selectedParent);
      const focusing = selected !== top && !query;
      stage.replaceChildren();
      tree.replaceChildren();
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.classList.add("cv-edges");
      svg.setAttribute("aria-hidden", "true");
      stage.append(svg);
      for (const id of visible) {
        const node = nodes.get(id), point = positions.get(id), parent = node.parent ? positions.get(node.parent) : void 0;
        if (parent) {
          const edge = document.createElementNS(svg.namespaceURI, "path");
          const x1 = parent.x + 176, y1 = parent.y + 38, x2 = point.x, y2 = point.y + 38;
          const middle = (x1 + x2) / 2;
          const direction = Math.sign(y2 - y1);
          const radius = Math.min(6, Math.abs(y2 - y1) / 2);
          edge.setAttribute("d", direction === 0 ? `M ${x1} ${y1} H ${x2}` : `M ${x1} ${y1} H ${middle - radius} Q ${middle} ${y1} ${middle} ${y1 + direction * radius} V ${y2 - direction * radius} Q ${middle} ${y2} ${middle + radius} ${y2} H ${x2}`);
          edge.classList.add("cv-edge");
          if (!query && (id === selected || node.parent === selected)) edge.classList.add("cv-relevant");
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
        const cardTitle = element("span", "cv-card-title");
        cardTitle.append(element("i", "cv-dot"), element("span", "", node.title));
        card.append(cardTitle, element("span", "cv-card-meta", label(node)));
        const list = visibleChildren(id);
        if (list.length) {
          card.setAttribute("aria-expanded", String(!!query || expanded.has(id)));
          card.append(element("span", "cv-expand-count", `${expanded.has(id) || query ? "\u2212" : "+"}${list.length}`));
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
        if (list.length) row.setAttribute("aria-expanded", String(!!query || expanded.has(id)));
        row.append(element("span", "cv-tree-marker", list.length ? expanded.has(id) || query ? "\u25BE" : "\u25B8" : "\xB7"), element("span", "", node.title));
        tree.append(row);
      }
      empty.hidden = !searchMessage && visible.length > 0;
      empty.textContent = searchMessage || text("\u6CA1\u6709\u5339\u914D\u7684\u89C4\u5219", "No matching rules");
      applyCamera();
    }
    function searchNodes() {
      query = search.value.trim().toLocaleLowerCase();
      matching = null;
      searchMessage = "";
      if (query) {
        matching = /* @__PURE__ */ new Set();
        let count = 0;
        for (const node of data.nodes) {
          if (filterIds && !filterIds.has(node.id)) continue;
          const body = node.kind === "group" ? "" : data.documents[node.id]?.body;
          if (![node.title, node.desc, body].join(" ").toLocaleLowerCase().includes(query)) continue;
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
    viewport.onpointerdown = (event) => {
      if (event.button !== 0) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      moved = false;
      if (pointers.size === 1) gesture = { x: event.clientX, y: event.clientY, camera: { ...camera } };
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        gesture = { distance: Math.hypot(a.x - b.x, a.y - b.y), scale: camera.scale };
      }
      if (!(event.target instanceof Element) || !event.target.closest("button")) viewport.setPointerCapture(event.pointerId);
    };
    viewport.onpointermove = (event) => {
      if (!pointers.has(event.pointerId)) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 2 && gesture?.distance) {
        const [a, b] = [...pointers.values()], rect = viewport.getBoundingClientRect();
        zoomAt(gesture.scale * Math.hypot(a.x - b.x, a.y - b.y) / gesture.distance, (a.x + b.x) / 2 - rect.left, (a.y + b.y) / 2 - rect.top);
        moved = true;
      } else if (gesture?.camera) {
        const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;
        if (Math.hypot(dx, dy) > 4) moved = true;
        if (moved) {
          viewport.setPointerCapture(event.pointerId);
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
    viewport.onpointerup = release;
    viewport.onpointercancel = release;
    viewport.addEventListener("click", (event) => {
      if (moved) {
        event.preventDefault();
        event.stopPropagation();
        moved = false;
      }
    }, true);
    viewport.addEventListener("wheel", (event) => {
      event.preventDefault();
      if (event.ctrlKey || event.metaKey) {
        const rect = viewport.getBoundingClientRect();
        zoomAt(camera.scale * Math.exp(-event.deltaY * 3e-3), event.clientX - rect.left, event.clientY - rect.top);
      } else {
        camera.x -= event.deltaX;
        camera.y -= event.deltaY;
        applyCamera();
      }
    }, { passive: false });
    viewport.onkeydown = (event) => {
      if (event.target !== viewport) return;
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
        query = "";
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
          showDetails(selected);
          reader.scrollTop = scroll;
        }
      },
      resize() {
        if (!fitted && viewport.clientWidth > 0) fit();
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
      viewport.ariaLabel = text("\u7EA6\u675F\u56FE\u753B\u5E03\uFF1B\u65B9\u5411\u952E\u5E73\u79FB\uFF0C\u52A0\u51CF\u952E\u7F29\u653E\uFF0C0 \u9002\u914D", "Constraint canvas; arrows to pan, plus/minus to zoom, 0 to fit");
      help.textContent = text("\u62D6\u52A8\u5E73\u79FB \xB7 Ctrl + \u6EDA\u8F6E\u7F29\u653E \xB7 \u53CC\u51FB / Shift+Enter \u9605\u8BFB\u8BE6\u60C5", "Drag to pan \xB7 Ctrl + scroll to zoom \xB7 Double-click / Shift+Enter for details");
      legend.replaceChildren(element("strong", "", text("\u9002\u7528\u89D2\u8272", "Applicable roles")));
      const en = { frontend: "Frontend", backend: "Backend", cache: "Cache", database: "Data store", queue: "Tasks / Queue", security: "Security", generic: "Generic" };
      for (const [id, role] of Object.entries(data.roles || {})) {
        const row = element("div", "cv-legend-row");
        roleStyle({ role: id }, row);
        row.append(element("i", "cv-dot"), element("span", "", text(role.name, en[id])), element("b", "", String(data.nodes.filter((node) => node.kind === "rule" && (node.role || "generic") === id && (!filterIds || filterIds.has(node.id))).length)));
        legend.append(row);
      }
      legend.append(
        element("p", "", text("\u7F16\u53F7\u5206\u4E3B\u9898\uFF0C\u989C\u8272\u5206\u89D2\u8272\uFF0C\u4E0D\u4EE3\u8868\u5408\u89C4\u7ED3\u679C\u3002\u901A\u7528\u542B\u8DE8\u89D2\u8272\u4E0E\u672A\u660E\u786E\u5F52\u5C5E\u3002", "Numbers identify topics; colors identify roles, not compliance. Generic includes mixed or unknown roles.")),
        element("p", "", text("\u89C4\u5219\u539F\u6587\u7248\u672C\u4E0E\u9879\u76EE\u5FEB\u7167\u5206\u522B\u8BB0\u5F55\u3002\u5B9E\u73B0\u5C1A\u672A\u6838\u9A8C\u3002", "Source-range versions and project snapshot are separate. Implementation is unverified.")),
        element("p", "", data.revision)
      );
    }
    const resizeObserver = new ResizeObserver(() => api.resize());
    resizeObserver.observe(viewport);
    const themeObserver = new MutationObserver(() => api.refresh());
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "lang"] });
    refreshLabels();
    render();
    requestAnimationFrame(() => api.resize());
    return api;
  }
  return __toCommonJS(constraint_canvas_exports);
})();
