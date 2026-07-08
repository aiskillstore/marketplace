#!/usr/bin/env bun
/**
 * Comprehensive TUI Features Demo
 * Demonstrates all TUI features including filtering and configuration
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('╔══════════════════════════════════════════════════════════════════════════╗');
  console.log('║            Tmux TUI - 综合功能演示/Comprehensive Features Demo          ║');
  console.log('╚══════════════════════════════════════════════════════════════════════════╝\n');

  console.log('创建示例会话/Creating example sessions...\n');

  // Create example sessions
  const sessions = [
    {
      name: 'web-server',
      command: 'echo "Web server on :3000" && sleep 60',
      category: 'service',
    },
    {
      name: 'api-server',
      command: 'echo "API server on :4000" && sleep 60',
      category: 'service',
    },
    {
      name: 'build-process',
      command: 'echo "Building..." && sleep 30',
      category: 'task',
    },
    {
      name: 'test-suite',
      command: 'echo "Running tests..." && sleep 45',
      category: 'task',
    },
    {
      name: 'data-processor',
      command: 'echo "Processing data..." && sleep 90',
      category: 'agent',
    },
  ];

  for (const session of sessions) {
    await tmux.createSession(session.name, session.command, session.category as any);
    console.log(`✅ Created ${session.category}: ${session.name}`);
  }

  console.log('\n─────────────────────────────────────────────────────────────────────────\n');

  // Wait for sessions to be created
  await new Promise(resolve => setTimeout(resolve, 500));

  console.log('TUI 功能总览/TUI Features Overview:\n');

  console.log('📋 核心功能/Core Features:');
  console.log('   • 双语界面/Bilingual interface');
  console.log('   • 可视化会话列表/Visual session list');
  console.log('   • 颜色编码/Color coding');
  console.log('   • 自动刷新/Auto-refresh\n');

  console.log('⌨️ 键盘操作/Keyboard Operations:');
  console.log('   [↑/↓] 导航/Navigate');
  console.log('   [r]   刷新/Refresh');
  console.log('   [n]   新建/New');
  console.log('   [c]   捕获/Capture');
  console.log('   [s]   状态/Status');
  console.log('   [a]   连接/Attach');
  console.log('   [k]   终止/Kill');
  console.log('   [f]   过滤/Filter');
  console.log('   [h/?] 帮助/Help');
  console.log('   [q/Esc] 退出/Exit\n');

  console.log('🔍 过滤功能/Filter Features:');
  console.log('   • 按分类过滤/Filter by category (task/service/agent)');
  console.log('   • 按状态过滤/Filter by status (running/idle/exited)');
  console.log('   • 搜索功能/Search functionality');
  console.log('   • 排序功能/Sorting functionality');
  console.log('   • 组合过滤/Combined filters\n');

  console.log('⚙️ 配置管理/Configuration Management:');
  console.log('   • 语言设置/Language settings (bilingual/zh/en)');
  console.log('   • 刷新间隔/Refresh interval');
  console.log('   • 颜色主题/Color theme');
  console.log('   • 输出行数/Output lines');
  console.log('   • 自动清理/Auto-cleanup');
  console.log('   • 终止确认/Kill confirmation\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('启动 TUI/Launch TUI:\n');
  console.log('  基础版本/Basic version:');
  console.log('    bun tui.ts\n');
  console.log('  增强版本/Enhanced version (with filtering):');
  console.log('    bun tui-enhanced.ts\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示脚本/Demo Scripts:\n');
  console.log('  bun demo-tui.ts         - 完整演示/Full demo');
  console.log('  bun demo-bilingual.ts   - 双语界面演示/Bilingual demo');
  console.log('  bun demo-config.ts      - 配置管理演示/Config demo');
  console.log('  bun demo-filter.ts      - 过滤功能演示/Filter demo\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('文档/Documentation:\n');
  console.log('  cat TUI.md              - TUI 详细文档/TUI detailed docs');
  console.log('  cat README.md           - 项目总览/Project overview');
  console.log('  cat BILINGUAL_REPORT.md - 双语化报告/Bilingualization report');
  console.log('  cat COMPLETION_SUMMARY.md - 完成总结/Completion summary\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('💡 使用技巧/Usage Tips:\n');
  console.log('1. 使用过滤器快速找到目标会话');
  console.log('   Use filters to quickly find target sessions');
  console.log('2. 按 [f] 进入过滤器模式，按数字键快速过滤');
  console.log('   Press [f] to enter filter mode, press number keys to filter quickly');
  console.log('3. 按 [h] 或 [?] 查看帮助信息');
  console.log('   Press [h] or [?] to view help information');
  console.log('4. 配置文件位于 ~/.pi-tmux-tui-config.json');
  console.log('   Configuration file is at ~/.pi-tmux-tui-config.json');
  console.log('5. 双语界面同时显示中文和英文，方便不同语言用户');
  console.log('   Bilingual interface displays both Chinese and English\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('当前会话/Current Sessions:\n');
  const currentSessions = await tmux.listSessions();
  console.log('─'.repeat(80));
  currentSessions.forEach(session => {
    const categoryLabel = session.category === 'task' ? '任务/Task' : 
                          session.category === 'service' ? '服务/Service' : '代理/Agent';
    console.log(`  ${session.name}`);
    console.log(`  分类/Category: ${categoryLabel} | 状态/Status: ${session.status}\n`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('准备就绪/Ready!\n');
  console.log('现在可以启动 TUI 开始使用:');
  console.log('You can now launch TUI to start using:\n');
  console.log('  bun tui-enhanced.ts\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('按 Ctrl+C 退出此演示/Press Ctrl+C to exit this demo.');
  console.log('会话将保留，可以在 TUI 中管理。');
  console.log('Sessions will remain and can be managed in TUI.\n');
}

main().catch(err => {
  console.error('错误/Error:', err.message);
  process.exit(1);
});