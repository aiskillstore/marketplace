// Watch mode: re-scan on change, as a local interactive loop.
//
// `--watch` is a convenience for a writer sitting in an editor, not a CI
// facility. It never resolves an exit code: the process keeps running until
// interrupted, so a script waiting for its status would hang rather than learn
// anything. The help text and docs/GLOSSARY.md say so in the same words.
//
// Implementation notes, all of them load-bearing:
//
//   * `fs.watch` is the only dependency-free mechanism available at the
//     project's Node 18 floor, and it is the reason the caveat below exists.
//   * Directories are watched, not files. An editor that saves through a
//     temporary file and a rename replaces the inode, and a watch on the old
//     inode would go quiet forever; a watch on the containing directory sees
//     the replacement. So every input path contributes its parent directory,
//     plus the directory itself when the input is a directory.
//   * Recursive watching is deliberately NOT requested. `fs.watch` gained a
//     `recursive` option on macOS and Windows in Node 20 and is still
//     unsupported on Linux at the Node 18 floor, so asking for it would make
//     the same command work on one machine and throw on another. Instead the
//     watcher set is recomputed from the collected files on every rescan, so a
//     newly created sub-directory is picked up on the next pass even though the
//     change that created it was not itself observed. The one gap this leaves
//     is documented rather than papered over: a brand new nested directory is
//     noticed on the following change inside it, not on its creation.
//   * There is no polling loop. Rescans are driven purely by fs.watch events,
//     debounced so a single editor save that emits several events performs one
//     scan, never a spin of them.
//   * A deleted or replaced file, a removed directory, and a scan that throws
//     are all reported and survived: the watcher set is rebuilt and the loop
//     continues. `close()` is idempotent and always reached on shutdown, so no
//     watcher is leaked.

import fs from 'node:fs';
import path from 'node:path';

/** Debounce window: one editor save emits several fs.watch events. */
export const DEBOUNCE_MS = 120;

export class WatchError extends Error {}

/**
 * The directories worth watching for a set of input paths: the parent of every
 * file, and the directory itself when the input is one. Deduplicated and
 * sorted so the watcher's behaviour does not depend on filesystem ordering.
 */
export function watchTargets(inputs, { cwd = process.cwd() } = {}) {
  const targets = new Set();
  for (const input of inputs) {
    const resolved = path.resolve(cwd, input);
    let stat = null;
    try {
      stat = fs.statSync(resolved);
    } catch {
      // A path that does not exist yet still has a parent worth watching: the
      // run that follows its creation is the whole point of watching.
      targets.add(path.dirname(resolved));
      continue;
    }
    if (stat.isDirectory()) targets.add(resolved);
    else targets.add(path.dirname(resolved));
  }
  return [...targets].sort();
}

/**
 * A watcher that survives deletion, replacement and rescan.
 *
 * The public surface is intentionally small: `stop()` is safe to call more than
 * once, and no method throws after construction. Errors are handed to `onError`
 * as text, because the only reader is a terminal.
 */
export class Watcher {
  /**
   * @param {object} options
   * @param {() => number[]} options.targets      directories to watch
   * @param {() => void} options.onChange         called after the debounce
   * @param {(line: string) => void} [options.onError]
   * @param {() => void} [options.onIdle]         called after every rescan
   * @param {number} [options.debounceMs]
   */
  constructor({ targets, onChange, onError = () => {}, onIdle = () => {}, debounceMs = DEBOUNCE_MS }) {
    this.targets = targets;
    this.onChange = onChange;
    this.onError = onError;
    this.onIdle = onIdle;
    this.debounceMs = debounceMs;
    this.watchers = [];
    this.timer = null;
    this.stopped = false;
    this.running = false;
    this.scans = 0;
    this.open();
  }

  /** (Re)build the watcher set. Never throws: an unwatchable path is reported. */
  open() {
    this.closeWatchers();
    for (const target of this.targets) {
      try {
        this.watchers.push(fs.watch(target, () => this.schedule()));
      } catch (err) {
        this.onError(`cannot watch ${target}: ${err.message}`);
      }
    }
  }

  /**
   * One rescan per burst of events, and never concurrently with another: a
   * second event arriving mid-scan sets a single pending flag instead of
   * starting a second scan on top of the first.
   */
  schedule() {
    if (this.stopped) return;
    if (this.running) { this.pending = true; return; }
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => { this.timer = null; this.scan(); }, this.debounceMs);
    if (typeof this.timer.unref === 'function') this.timer.unref();
  }

  scan() {
    if (this.stopped) return;
    this.running = true;
    this.pending = false;
    try {
      this.onChange();
      this.scans += 1;
    } catch (err) {
      this.onError(`rescan failed: ${err && err.message ? err.message : String(err)}`);
    } finally {
      this.running = false;
    }
    try {
      this.onIdle();
    } catch { /* the scan already reported whatever went wrong */ }
    if (this.pending && !this.stopped) this.schedule();
  }

  closeWatchers() {
    for (const watcher of this.watchers) {
      try { watcher.close(); } catch { /* already closed */ }
    }
    this.watchers = [];
  }

  /** Idempotent: safe from a signal handler and from ordinary teardown. */
  stop() {
    if (this.stopped) return;
    this.stopped = true;
    if (this.timer) { clearTimeout(this.timer); this.timer = null; }
    this.closeWatchers();
  }
}
