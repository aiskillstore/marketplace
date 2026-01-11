#!/usr/bin/env bun
import { readdir, readFile, writeFile, mkdir, stat } from "fs/promises";
import { join, resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { $ } from "bun";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

import type { TmuxSession, TmuxConfig, SessionCategory, SessionStatus, WaitForTextOptions } from "./types/index.js";

const TMPDIR = process.env.TMPDIR || "/tmp";

const DEFAULT_CONFIG: TmuxConfig = {
  socketDir: process.env.PI_TMUX_SOCKET_DIR || join(TMPDIR, "pi-tmux-sockets"),
  defaultSocket: join(TMPDIR, "pi-tmux-sockets", "pi.sock"),
  sessionStore: join(TMPDIR, "pi-tmux-sessions.json"),
  autoCleanup: true,
  cleanupAge: 24,
};

class TmuxManager {
  private config: TmuxConfig;
  private sessions: Map<string, TmuxSession> = new Map();

  constructor(config?: Partial<TmuxConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  private async ensureSocketDir(): Promise<void> {
    await mkdir(this.config.socketDir, { recursive: true });
  }

  private async ensureStoreFile(): Promise<void> {
    const storeDir = dirname(this.config.sessionStore);
    await mkdir(storeDir, { recursive: true });
  }

  private generateSessionId(name: string, category: SessionCategory): string {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[-T:]/g, "");
    return `pi-${category}-${name}-${timestamp}`;
  }

  private getTarget(id: string): string {
    return `${id}:1.1`; // tmux windows and panes are 1-indexed
  }

  private async loadSessions(): Promise<void> {
    try {
      await this.ensureStoreFile();
      const content = await readFile(this.config.sessionStore, "utf-8");
      const data = JSON.parse(content);
      this.sessions = new Map(Object.entries(data.sessions || {}));
    } catch {
      this.sessions = new Map();
    }
  }

  private async saveSessions(): Promise<void> {
    await this.ensureStoreFile();
    const data = {
      sessions: Object.fromEntries(this.sessions),
      lastSync: new Date().toISOString(),
    };
    await writeFile(this.config.sessionStore, JSON.stringify(data, null, 2));
  }

  async createSession(name: string, command: string, category: SessionCategory = "task"): Promise<TmuxSession> {
    await this.ensureSocketDir();
    await this.loadSessions();

    const id = this.generateSessionId(name, category);
    const socket = this.config.defaultSocket;
    const target = this.getTarget(id);
    const now = new Date().toISOString();

    const session: TmuxSession = {
      id,
      name,
      category,
      socket,
      target,
      command,
      status: "running",
      createdAt: now,
      lastActivityAt: now,
    };

    await $`tmux -S ${socket} new -d -s ${id} -n shell`.quiet();
    await $`tmux -S ${socket} send-keys -t ${target} -- ${command} Enter`.quiet();

    this.sessions.set(id, session);
    await this.saveSessions();

    return session;
  }

  async listSessions(filter?: { category?: SessionCategory; status?: SessionStatus }): Promise<TmuxSession[]> {
    await this.loadSessions();
    let sessions = Array.from(this.sessions.values());

    if (filter?.category) {
      sessions = sessions.filter(s => s.category === filter.category);
    }
    if (filter?.status) {
      sessions = sessions.filter(s => s.status === filter.status);
    }

    return sessions.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }

  async getSession(id: string): Promise<TmuxSession | null> {
    await this.loadSessions();
    return this.sessions.get(id) || null;
  }

  async killSession(id: string): Promise<void> {
    await this.loadSessions();
    const session = this.sessions.get(id);
    if (!session) throw new Error(`Session not found: ${id}`);

    await $`tmux -S ${session.socket} kill-session -t ${id}`.quiet();
    this.sessions.delete(id);
    await this.saveSessions();
  }

  async sendKeys(target: string, keys: string, literal: boolean = true): Promise<void> {
    const socket = this.config.defaultSocket;
    const args = literal ? ["-l", "--", keys] : ["--", keys];
    await $`tmux -S ${socket} send-keys -t ${target} ${args}`.quiet();
  }

  async capturePane(target: string, lines: number = 200): Promise<string> {
    const socket = this.config.defaultSocket;
    const result = await $`tmux -S ${socket} capture-pane -p -J -t ${target} -S -${lines}`.quiet();
    return result.stdout.toString().trim();
  }

  async waitForText(target: string, pattern: string, options: WaitForTextOptions = {}): Promise<boolean> {
    const { timeout = 15, interval = 0.5, lines = 1000 } = options;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout * 1000) {
      const output = await this.capturePane(target, lines);
      const regex = new RegExp(pattern);
      if (regex.test(output)) return true;
      await new Promise(r => setTimeout(r, interval * 1000));
    }

    const lastOutput = await this.capturePane(target, lines);
    console.error(`Timeout waiting for pattern: ${pattern}`);
    console.error(`Last output:\n${lastOutput}`);
    return false;
  }

  async getSessionStatus(target: string): Promise<SessionStatus> {
    const socket = this.config.defaultSocket;
    try {
      const result = await $`tmux -S ${socket} display-message -p '#{window_activity_flag}' -t ${target}`.quiet();
      const isActive = result.stdout.toString().trim() === "1";
      return isActive ? "running" : "idle";
    } catch {
      return "exited";
    }
  }

  async updateActivity(id: string): Promise<void> {
    await this.loadSessions();
    const session = this.sessions.get(id);
    if (session) {
      session.lastActivityAt = new Date().toISOString();
      await this.saveSessions();
    }
  }

  async cleanupOldSessions(maxAgeHours: number = this.config.cleanupAge): Promise<number> {
    await this.loadSessions();
    const now = Date.now();
    let cleaned = 0;

    for (const [id, session] of this.sessions) {
      const age = (now - new Date(session.lastActivityAt).getTime()) / (1000 * 60 * 60);
      if (age > maxAgeHours) {
        try {
          await $`tmux -S ${session.socket} kill-session -t ${id}`.quiet();
        } catch {}
        this.sessions.delete(id);
        cleaned++;
      }
    }

    if (cleaned > 0) await this.saveSessions();
    return cleaned;
  }

  async syncWithTmux(): Promise<void> {
    await this.loadSessions();
    const socket = this.config.defaultSocket;

    try {
      const result = await $`tmux -S ${socket} list-sessions -F '#{session_name}'`.quiet();
      const activeSessions = result.stdout.toString().trim().split("\n").filter(Boolean);

      for (const [id, session] of this.sessions) {
        const isActive = activeSessions.includes(id);
        session.status = isActive ? "running" : "exited";
      }
    } catch {
      for (const session of this.sessions.values()) {
        session.status = "exited";
      }
    }

    await this.saveSessions();
  }
}

export { TmuxManager };

const tmux = new TmuxManager();

async function main() {
  const [command, ...args] = process.argv.slice(2);

  switch (command) {
    case "create": {
      const [name, commandStr, category] = args;
      if (!name || !commandStr) {
        console.error("Usage: bun lib.ts create <name> <command> [category]");
        process.exit(1);
      }
      const session = await tmux.createSession(name, commandStr, category as SessionCategory);
      console.log(`✅ Created session: ${session.id}`);
      console.log(`\nTo monitor this session:`);
      console.log(`  tmux -S ${session.socket} attach -t ${session.id}`);
      console.log(`\nOr capture output:`);
      console.log(`  tmux -S ${session.socket} capture-pane -p -J -t ${session.target} -S -200`);
      break;
    }

    case "list": {
      const [filterStr] = args;
      const filter = filterStr ? { category: filterStr as SessionCategory } : undefined;
      const sessions = await tmux.listSessions(filter);
      if (sessions.length === 0) {
        console.log("No sessions found.");
      } else {
        console.log("ID                           NAME      CATEGORY  STATUS    LAST ACTIVITY");
        console.log("─────────────────────────────────────────────────────────────────────────");
        for (const s of sessions) {
          const age = Math.floor((Date.now() - new Date(s.lastActivityAt).getTime()) / 60000);
          const ageStr = age < 60 ? `${age}m ago` : `${Math.floor(age / 60)}h ago`;
          console.log(`${s.id.padEnd(28)} ${s.name.padEnd(9)} ${s.category.padEnd(9)} ${s.status.padEnd(9)} ${ageStr}`);
        }
      }
      break;
    }

    case "status": {
      const [id] = args;
      if (!id) {
        console.error("Usage: bun lib.ts status <id>");
        process.exit(1);
      }
      const session = await tmux.getSession(id);
      if (!session) {
        console.error(`Session not found: ${id}`);
        process.exit(1);
      }
      const status = await tmux.getSessionStatus(session.target);
      console.log(`ID: ${session.id}`);
      console.log(`Name: ${session.name}`);
      console.log(`Category: ${session.category}`);
      console.log(`Status: ${status}`);
      console.log(`Created: ${session.createdAt}`);
      console.log(`Last Activity: ${session.lastActivityAt}`);
      break;
    }

    case "send": {
      const [id, ...keys] = args;
      if (!id || keys.length === 0) {
        console.error("Usage: bun lib.ts send <id> <keys>");
        process.exit(1);
      }
      const session = await tmux.getSession(id);
      if (!session) {
        console.error(`Session not found: ${id}`);
        process.exit(1);
      }
      await tmux.sendKeys(session.target, keys.join(" "));
      await tmux.updateActivity(id);
      console.log(`✅ Sent keys to ${id}`);
      break;
    }

    case "capture": {
      const [id, linesStr] = args;
      if (!id) {
        console.error("Usage: bun lib.ts capture <id> [lines]");
        process.exit(1);
      }
      const session = await tmux.getSession(id);
      if (!session) {
        console.error(`Session not found: ${id}`);
        process.exit(1);
      }
      const lines = linesStr ? parseInt(linesStr) : 200;
      const output = await tmux.capturePane(session.target, lines);
      console.log(output);
      break;
    }

    case "kill": {
      const [id] = args;
      if (!id) {
        console.error("Usage: bun lib.ts kill <id>");
        process.exit(1);
      }
      await tmux.killSession(id);
      console.log(`✅ Killed session: ${id}`);
      break;
    }

    case "cleanup": {
      const [hoursStr] = args;
      const hours = hoursStr ? parseInt(hoursStr) : undefined;
      const cleaned = await tmux.cleanupOldSessions(hours);
      console.log(`✅ Cleaned ${cleaned} old session(s)`);
      break;
    }

    case "attach": {
      const [id] = args;
      if (!id) {
        console.error("Usage: bun lib.ts attach <id>");
        process.exit(1);
      }
      const session = await tmux.getSession(id);
      if (!session) {
        console.error(`Session not found: ${id}`);
        process.exit(1);
      }
      console.log(`To attach to this session, run:`);
      console.log(`  tmux -S ${session.socket} attach -t ${session.id}`);
      console.log(`\nDetach with: Ctrl+b d`);
      break;
    }

    case "sync": {
      await tmux.syncWithTmux();
      console.log("✅ Synced session status with tmux");
      break;
    }

    default:
      console.log(`
Tmux Session Manager for Pi Agent

Usage: bun lib.ts <command> [options]

Commands:
  create <name> <command> [category]  Create a new session
  list [filter]                       List all sessions
  status <id>                         Show session status
  send <id> <keys>                    Send keys to session
  capture <id> [lines]                Capture pane output
  kill <id>                           Kill a session
  cleanup [hours]                     Cleanup old sessions (default: 24h)
  attach <id>                         Print attach command for session
  sync                                Sync session status with tmux

Categories: task, service, agent

Examples:
  bun lib.ts create compile "make all" task
  bun lib.ts create dev-server "npm run dev" service
  bun lib.ts list
  bun lib.ts status pi-task-compile-20250107-123456
  bun lib.ts capture pi-task-compile-20250107-123456
  bun lib.ts kill pi-task-compile-20250107-123456
`);
  }
}

main().catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});