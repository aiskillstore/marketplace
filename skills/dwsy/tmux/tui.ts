#!/usr/bin/env bun
/**
 * Tmux Session Manager TUI
 * Clean, minimal interface for managing tmux sessions
 */

import { render } from 'ink';
import React, { useState, useEffect } from 'react';
import { Box, Text, useInput, useApp, useStdin } from 'ink';
import { $ } from 'bun';
import { TmuxManager } from './lib.ts';
import type { TmuxSession } from './types/index.js';

interface AppProps {
  tmux: TmuxManager;
}

const STATUS_COLORS = { running: 'green', idle: 'yellow', exited: 'red' };
const STATUS_LABELS = { running: '运行中/Running', idle: '空闲/Idle', exited: '已退出/Exited' };
const CATEGORY_COLORS = { task: 'cyan', service: 'magenta', agent: 'blue' };
const CATEGORY_LABELS = { task: '任务/Task', service: '服务/Service', agent: '代理/Agent' };

function App({ tmux }: AppProps) {
  const { exit } = useApp();
  const { stdin, setRawMode } = useStdin();
  
  useEffect(() => {
    if (stdin?.isTTY) setRawMode(true);
    return () => { if (stdin?.isTTY) setRawMode(false); };
  }, [stdin, setRawMode]);

  const [sessions, setSessions] = useState<TmuxSession[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [mode, setMode] = useState<'list' | 'capture' | 'status' | 'attach' | 'create' | 'confirm'>('list');
  const [output, setOutput] = useState('');
  
  const [nameInput, setNameInput] = useState('');
  const [commandInput, setCommandInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('task');
  const [inputStep, setInputStep] = useState<'name' | 'command' | 'category'>('name');

  // Load sessions on mount and refresh periodically
  useEffect(() => {
    const loadSessions = async () => {
      await tmux.syncWithTmux();
      const list = await tmux.listSessions();
      setSessions(list);
    };
    
    loadSessions();
    const interval = setInterval(loadSessions, 5000);
    return () => clearInterval(interval);
  }, [tmux]);

  useInput((input, key) => {
    if (mode === 'list') {
      if (key.upArrow) setSelectedIndex(p => Math.max(0, p - 1));
      else if (key.downArrow) setSelectedIndex(p => Math.min(sessions.length - 1, p + 1));
      else if (input === 'r') {
        // Force refresh
        tmux.syncWithTmux().then(() => tmux.listSessions().then(setSessions));
      }
      else if (input === 'q' || key.escape) exit();
      else if (input === 'n') {
        setMode('create');
        setNameInput(''); setCommandInput(''); setCategoryInput('task');
        setInputStep('name');
      }
      else if (sessions.length > 0) {
        if (key.return) handleAttach();
        else if (input === 'k') setMode('confirm');
        else if (input === 'c') handleCapture();
        else if (input === 's') handleStatus();
        else if (input === 'a') handleAttach();
      }
    } else if (mode === 'confirm') {
      if (input === 'y') handleKill();
      else if (input === 'n' || key.escape) setMode('list');
    } else if (mode === 'create') {
      if (key.return) {
        if (inputStep === 'name' && nameInput) setInputStep('command');
        else if (inputStep === 'command' && commandInput) setInputStep('category');
        else if (inputStep === 'category') handleCreate();
      } else if (key.escape) {
        setMode('list');
      } else if (key.backspace || key.delete) {
        if (inputStep === 'name') setNameInput(p => p.slice(0, -1));
        else if (inputStep === 'command') setCommandInput(p => p.slice(0, -1));
        else if (inputStep === 'category') setCategoryInput(p => p.slice(0, -1));
      } else if (input.length === 1) {
        if (inputStep === 'name') setNameInput(p => p + input);
        else if (inputStep === 'command') setCommandInput(p => p + input);
        else if (inputStep === 'category') setCategoryInput(p => p + input);
      }
    } else if (mode === 'capture' || mode === 'status' || mode === 'attach') {
      if (key.escape) { setMode('list'); setOutput(''); }
      else if (mode === 'attach' && input === 'y') handleCopyCommand();
    }
  });

  const handleKill = async () => {
    if (sessions[selectedIndex]) {
      await tmux.killSession(sessions[selectedIndex].id);
      const list = await tmux.listSessions();
      setSessions(list);
      setMode('list');
    }
  };

  const handleCapture = async () => {
    if (sessions[selectedIndex]) {
      const result = await tmux.capturePane(sessions[selectedIndex].target, 200);
      setOutput(result);
      setMode('capture');
    }
  };

  const handleStatus = async () => {
    if (sessions[selectedIndex]) {
      const s = sessions[selectedIndex];
      const status = await tmux.getSessionStatus(s.target);
      setOutput(`Session ID: ${s.id}\nName: ${s.name}\nCategory: ${s.category}\nStatus: ${status}\nCreated: ${s.createdAt}`);
      setMode('status');
    }
  };

  const handleAttach = async () => {
    if (sessions[selectedIndex]) {
      const s = sessions[selectedIndex];
      const attachCmd = `tmux -S ${s.socket} attach -t ${s.id}`;
      setOutput(`${attachCmd}\n\nDetach: Ctrl+b d`);
      setMode('attach');
    }
  };

  const handleCopyCommand = async () => {
    if (output && mode === 'attach') {
      const cmd = output.split('\n')[0];
      try {
        await $`echo "${cmd}" | pbcopy`.nothrow();
        setOutput(`${cmd}\n\n✓ 已复制到剪贴板 / Copied to clipboard!\n\nDetach: Ctrl+b d`);
      } catch (err) {
        setOutput(`${cmd}\n\n✗ 复制失败 / Copy failed\n\nDetach: Ctrl+b d`);
      }
    }
  };

  const handleCreate = async () => {
    if (nameInput && commandInput) {
      await tmux.createSession(nameInput, commandInput, categoryInput as any);
      const list = await tmux.listSessions();
      setSessions(list);
      setMode('list');
    }
  };

  const formatAge = (dateStr: string) => {
    const age = Math.floor((Date.now() - new Date(dateStr).getTime()) / 60000);
    if (age < 60) {
      return `${age}分钟/minutes`;
    } else {
      const hours = Math.floor(age / 60);
      return `${hours}小时/hours`;
    }
  };

  // Create mode
  if (mode === 'create') {
    const labels = { name: '名称/Name', command: '命令/Command', category: '分类/Category' };
    const values = { name: nameInput, command: commandInput, category: categoryInput };
    const current = values[inputStep];
    return React.createElement(Box, { flexDirection: 'column' },
      React.createElement(Text, { bold: true, color: 'green' }, ' 创建新会话 / Create New Session '),
      React.createElement(Text, {}, '\n'),
      Object.entries(labels).map(([k, v], idx) =>
        React.createElement(Box, { key: `field-${idx}-${k}` },
          React.createElement(Text, { color: inputStep === k ? 'cyan' : 'gray' }, `${v}: `),
          React.createElement(Text, { color: inputStep === k ? 'white' : 'dim' }, values[k as keyof typeof values])
        )
      ),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'gray' }, ' 按 Enter 继续/Press Enter to continue，按 Esc 取消/Press Esc to cancel '),
      React.createElement(Text, {}, '\n'),
      React.createElement(Box, {},
        React.createElement(Text, { color: 'magenta' }, '> '),
        React.createElement(Text, {}, current),
        React.createElement(Text, { inverse: true, color: 'white' }, ' ')
      )
    );
  }

  // Confirm kill mode
  if (mode === 'confirm') {
    return React.createElement(Box, { flexDirection: 'column' },
      React.createElement(Text, { bold: true, color: 'red' }, ' 确认终止 / Confirm Kill '),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, {}, ` 确定要终止以下会话吗？/Are you sure you want to kill session:`),
      React.createElement(Text, { color: 'yellow' }, `  ${sessions[selectedIndex]?.id}`),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'cyan' }, '[Y] 是/Yes  [N] 否/No')
    );
  }

  // Capture output mode
  if (mode === 'capture') {
    return React.createElement(Box, { flexDirection: 'column' },
      React.createElement(Text, { bold: true, color: 'green' }, ' 捕获输出 / Capture Output '),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'yellow' }, sessions[selectedIndex]?.id),
      React.createElement(Text, {}, '\n'),
      ...output.split('\n').slice(0, 30).map((line, i) =>
        React.createElement(Text, { key: `capture-line-${i}` }, line)
      ),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'gray' }, ' 按 Esc 返回 / Press Esc to return ')
    );
  }

  // Status mode
  if (mode === 'status') {
    return React.createElement(Box, { flexDirection: 'column' },
      React.createElement(Text, { bold: true, color: 'green' }, ' 会话状态 / Session Status '),
      React.createElement(Text, {}, '\n'),
      ...output.split('\n').map((line, i) =>
        React.createElement(Text, { key: `status-line-${i}` }, line)
      ),
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'gray' }, ' 按 Esc 返回 / Press Esc to return ')
    );
  }

  // Attach mode
  if (mode === 'attach') {
    const lines = output.split('\n');
    const commandLine = lines[0] || '';
    const hasCopySuccess = output.includes('✓ 已复制');
    const hasCopyError = output.includes('✗ 复制失败');
    
    return React.createElement(Box, { flexDirection: 'column' },
      React.createElement(Text, { bold: true, color: 'green' }, ' 连接命令 / Attach Command '),
      React.createElement(Text, {}, '\n'),
      React.createElement(Box, { borderStyle: 'single', borderColor: 'cyan' },
        React.createElement(Text, { color: 'yellow' }, ' ' + commandLine + ' ')
      ),
      React.createElement(Text, {}, '\n'),
      hasCopySuccess 
        ? React.createElement(Text, { color: 'green' }, ' ✓ 已复制到剪贴板 / Copied to clipboard! ')
        : hasCopyError
          ? React.createElement(Text, { color: 'red' }, ' ✗ 复制失败 / Copy failed ')
          : null,
      React.createElement(Text, {}, '\n'),
      React.createElement(Text, { color: 'gray' }, ' 按 [y] 复制命令 / Press [y] to copy command '),
      React.createElement(Text, { color: 'gray' }, ' 按 [Esc] 返回 / Press [Esc] to return ')
    );
  }

  // Main list mode
  const sessionElements = sessions.map((s, i) => {
    const selected = i === selectedIndex;
    const statusLabel = STATUS_LABELS[s.status as keyof typeof STATUS_LABELS];
    const categoryLabel = CATEGORY_LABELS[s.category as keyof typeof CATEGORY_LABELS];
    return React.createElement(Box, { key: `session-${s.id}-${s.status}`, gap: 2 },
      React.createElement(Text, {
        backgroundColor: selected ? 'cyan' : undefined,
        color: selected ? 'black' : 'gray',
        width: 30
      }, s.id.slice(0, 29)),
      React.createElement(Text, {
        backgroundColor: selected ? 'cyan' : undefined,
        color: selected ? 'black' : CATEGORY_COLORS[s.category as keyof typeof CATEGORY_COLORS],
        width: 12
      }, s.name.slice(0, 11)),
      React.createElement(Text, {
        backgroundColor: selected ? 'cyan' : undefined,
        color: selected ? 'black' : CATEGORY_COLORS[s.category as keyof typeof CATEGORY_COLORS],
        width: 12
      }, categoryLabel.slice(0, 11)),
      React.createElement(Text, {
        backgroundColor: selected ? 'cyan' : undefined,
        color: selected ? 'black' : STATUS_COLORS[s.status as keyof typeof STATUS_COLORS],
        width: 14
      }, statusLabel.slice(0, 13)),
      React.createElement(Text, {
        backgroundColor: selected ? 'cyan' : undefined,
        color: selected ? 'black' : 'gray'
      }, formatAge(s.lastActivityAt))
    );
  });

  return React.createElement(Box, { flexDirection: 'column', key: `main-${mode}` },
    React.createElement(Box, { justifyContent: 'space-between', key: 'header' },
      React.createElement(Text, { bold: true, color: 'green' }, ' Tmux 会话管理器 / Session Manager '),
      React.createElement(Text, { color: 'gray' }, ` ${sessions.length} 个会话 / sessions `)
    ),
    React.createElement(Text, { key: 'header-spacer' }, '\n'),
    React.createElement(Box, { key: 'table-header', gap: 2 },
      React.createElement(Text, { color: 'gray', bold: true, width: 30 }, ' 会话ID/ID'),
      React.createElement(Text, { color: 'gray', bold: true, width: 12 }, ' 名称/Name'),
      React.createElement(Text, { color: 'gray', bold: true, width: 12 }, ' 分类/Category'),
      React.createElement(Text, { color: 'gray', bold: true, width: 14 }, ' 状态/Status'),
      React.createElement(Text, { color: 'gray', bold: true }, ' 活动时间/Age')
    ),
    React.createElement(Text, { key: 'divider' }, '─'.repeat(80)),
    sessions.length === 0
      ? React.createElement(Text, { color: 'yellow', key: 'empty-msg' }, ' 没有找到会话/No sessions found。按 [n] 创建新会话/Press [n] to create a new session。 ')
      : sessionElements,
    React.createElement(Text, { key: 'footer-spacer' }, '\n'),
    React.createElement(Text, { color: 'gray', key: 'help-1' }, ' [↑↓] 导航/Navigate  [Enter/a] 连接/Attach  [r] 刷新/Refresh  [n] 新建/New  [q] 退出/Quit '),
    React.createElement(Text, { color: 'gray', key: 'help-2' }, ' [c] 捕获/Capture  [s] 状态/Status  [k] 终止/Kill  [Esc] 返回/Return ')
  );
}

async function main() {
  const tmux = new TmuxManager();
  const { waitUntilExit } = render(React.createElement(App, { tmux }));
  await waitUntilExit();
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});