#!/usr/bin/env bun
/**
 * Bilingual TUI Demo
 * Demonstrates the bilingual interface of the tmux TUI
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('╔══════════════════════════════════════════════════════════════════════════╗');
  console.log('║              Tmux TUI - 双语界面演示/Bilingual Interface Demo           ║');
  console.log('╚══════════════════════════════════════════════════════════════════════════╝\n');

  console.log('创建示例会话/Creating example sessions...\n');

  // Create different types of sessions
  const sessions = [
    {
      name: 'dev-server',
      command: 'echo "开发服务器运行中/Development server running" && sleep 60',
      category: 'service',
    },
    {
      name: 'build-task',
      command: 'echo "构建任务进行中/Build task in progress" && sleep 30',
      category: 'task',
    },
    {
      name: 'test-runner',
      command: 'echo "测试运行中/Tests running" && sleep 45',
      category: 'task',
    },
  ];

  for (const session of sessions) {
    const created = await tmux.createSession(session.name, session.command, session.category as any);
    console.log(`✅ 已创建/Created ${session.category}: ${created.id}`);
  }

  console.log('\n─────────────────────────────────────────────────────────────────────────\n');
  console.log('TUI 双语界面特性/Bilingual TUI Features:\n');
  console.log('📋 会话列表/Session List');
  console.log('   - 双语表头显示/Bilingual headers');
  console.log('   - 双语状态标签/Bilingual status labels');
  console.log('   - 双语分类标签/Bilingual category labels');
  console.log('   - 自动刷新/Auto-refresh (5秒/s)\n');
  console.log('⌨️ 键盘快捷键/Keyboard Shortcuts');
  console.log('   - 所有快捷键提示均为双语/All shortcut prompts are bilingual\n');
  console.log('🎨 子界面/Sub-interfaces');
  console.log('   - 创建会话/Create Session');
  console.log('   - 捕获输出/Capture Output');
  console.log('   - 状态详情/Status Detail');
  console.log('   - 连接命令/Attach Command');
  console.log('   - 确认终止/Confirm Kill\n');
  console.log('─────────────────────────────────────────────────────────────────────────\n');
  console.log('启动双语 TUI/Launch Bilingual TUI:\n');

  // Display current sessions
  const list = await tmux.listSessions();
  console.log('当前会话/Current Sessions:');
  console.log('─────────────────────────────────────────────────────────────────────────');
  
  // Display header
  console.log('会话ID/Session ID'.padEnd(35) + '名称/Name'.padEnd(15) + '分类/Category'.padEnd(15) + '状态/Status');
  console.log('─'.repeat(80));
  
  for (const session of list) {
    const categoryLabel = session.category === 'task' ? '任务/Task' : 
                          session.category === 'service' ? '服务/Service' : '代理/Agent';
    const statusLabel = session.status === 'running' ? '运行中/Running' : 
                        session.status === 'idle' ? '空闲/Idle' : '已退出/Exited';
    
    console.log(
      session.id.padEnd(35) + 
      session.name.padEnd(15) + 
      categoryLabel.padEnd(15) + 
      statusLabel
    );
    console.log(`   命令/Command: ${session.command}\n`);
  }

  console.log('─────────────────────────────────────────────────────────────────────────\n');
  console.log('运行命令启动 TUI/Run command to launch TUI:\n');
  console.log('  bun tui.ts\n');
  console.log('─────────────────────────────────────────────────────────────────────────\n');
  console.log('💡 双语界面优势/Bilingual Interface Advantages:\n');
  console.log('   • 同时支持中文和英文用户');
  console.log('   • 同时支持 Chinese and English users');
  console.log('   • 清晰的双语标签和提示');
  console.log('   • Clear bilingual labels and prompts');
  console.log('   • 无需切换语言设置');
  console.log('   • No need to switch language settings\n');
  console.log('─────────────────────────────────────────────────────────────────────────\n');
  console.log('查看详细文档/View detailed documentation:\n');
  console.log('  cat TUI.md\n');
  console.log('─────────────────────────────────────────────────────────────────────────\n');
  console.log('按 Ctrl+C 退出此演示/Press Ctrl+C to exit this demo.\n');
}

main().catch(err => {
  console.error('错误/Error:', err.message);
  process.exit(1);
});