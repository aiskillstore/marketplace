#!/usr/bin/env bun
/**
 * Beautiful TUI Demo
 * Demonstrates the improved UI with better spacing and design
 */

import { TmuxManager } from './lib.ts';

async function main() {
  const tmux = new TmuxManager();

  console.log('╔══════════════════════════════════════════════════════════════════════════╗');
  console.log('║              Tmux TUI - 美观界面演示/Beautiful UI Demo                ║');
  console.log('╚══════════════════════════════════════════════════════════════════════════╝\n');

  console.log('✨ 界面改进/UI Improvements:\n');

  console.log('📐 间距优化/Spacing Optimization');
  console.log('   • 增加了元素之间的间距/Increased spacing between elements');
  console.log('   • 改善了视觉层次结构/Improved visual hierarchy');
  console.log('   • 更好的可读性/Better readability\n');

  console.log('🎨 视觉设计/Visual Design');
  console.log('   • 统一的边框样式/Unified border styles');
  console.log('   • 更好的颜色搭配/Better color combinations');
  console.log('   • 图标增强/Enhanced icons\n');

  console.log('📊 布局改进/Layout Improvements');
  console.log('   • 清晰的表头/Clear column headers');
  console.log('   • 对齐的文本/Aligned text');
  console.log('   • 合理的宽度分配/Reasonable width distribution\n');

  console.log('🔤 双语标签/Bilingual Labels');
  console.log('   • 状态标签：运行中/Running、空闲/Idle、已退出/Exited');
  console.log('   • 分类标签：任务/Task、服务/Service、代理/Agent');
  console.log('   • 所有关键文本双语显示/All key text bilingual\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('当前会话/Current Sessions:\n');
  const sessions = await tmux.listSessions();
  
  if (sessions.length === 0) {
    console.log('📭 没有会话/No sessions found\n');
  } else {
    console.log('─'.repeat(100));
    console.log('');
    
    sessions.forEach((session, index) => {
      const statusIcon = session.status === 'running' ? '●' : session.status === 'idle' ? '○' : '●';
      const statusColor = session.status === 'running' ? '🟢' : session.status === 'idle' ? '🟡' : '🔴';
      const categoryIcon = session.category === 'task' ? '📋' : session.category === 'service' ? '🔧' : '🤖';
      
      console.log(`${index + 1}. ${categoryIcon} ${session.name}`);
      console.log(`   ID: ${session.id}`);
      console.log(`   状态/Status: ${statusColor} ${statusIcon} ${session.status}`);
      console.log(`   分类/Category: ${session.category}`);
      console.log(`   最后活动/Last Activity: ${session.lastActivityAt}`);
      console.log('');
    });
    
    console.log('─'.repeat(100));
    console.log('');
  }

  console.log('启动美观 TUI/Launch Beautiful TUI:\n');
  console.log('  bun tui-beautiful.ts\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('界面特性/UI Features:\n');
  console.log('📦 组件化设计/Component-based Design');
  console.log('   • 独立的界面组件/Separate interface components');
  console.log('   • 可复用的布局/Reusable layouts');
  console.log('   • 一致的样式/Consistent styling\n');

  console.log('🎯 交互增强/Enhanced Interaction');
  console.log('   • 清晰的焦点指示/Clear focus indication');
  console.log('   • 即时反馈/Instant feedback');
  console.log('   • 流畅的导航/Smooth navigation\n');

  console.log('🌈 多主题支持/Multi-theme Support');
  console.log('   • 默认主题/Default theme');
  console.log('   • 深色主题/Dark theme');
  console.log('   • 浅色主题/Light theme\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('快捷键参考/Keyboard Reference:\n');
  console.log('导航/Navigation:');
  console.log('  [↑/↓] 上下选择/Select up/down');
  console.log('  [r]    刷新列表/Refresh list\n');

  console.log('会话操作/Session Actions:');
  console.log('  [n]    新建会话/New session');
  console.log('  [c]    捕获输出/Capture output');
  console.log('  [s]    显示状态/Show status');
  console.log('  [a]    连接命令/Attach command');
  console.log('  [k]    终止会话/Kill session\n');

  console.log('其他/Other:');
  console.log('  [f]    过滤器/Filter');
  console.log('  [h/?]  帮助/Help');
  console.log('  [q/Esc] 退出/Exit\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('💡 设计原则/Design Principles:\n');
  console.log('1. 清晰性/Clarity');
  console.log('   • 信息层次清晰/Clear information hierarchy');
  console.log('   • 视觉焦点明确/Clear visual focus');
  console.log('   • 文本易读/Readable text\n');

  console.log('2. 一致性/Consistency');
  console.log('   • 统一的样式/Unified styling');
  console.log('   • 一致的布局/Consistent layout');
  console.log('   • 标准的交互/Standardized interaction\n');

  console.log('3. 美观性/Aesthetics');
  console.log('   • 平衡的间距/Balanced spacing');
  console.log('   • 和谐的色彩/Harmonious colors');
  console.log('   • 优雅的图标/Elegant icons\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('准备就绪/Ready!\n');
  console.log('现在启动美观 TUI 体验更好的界面:');
  console.log('Now launch the beautiful TUI to experience the improved interface:\n');
  console.log('  bun tui-beautiful.ts\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('提示/Tips:\n');
  console.log('• 使用 ↑↓ 键在会话列表中导航');
  console.log('• Use ↑↓ keys to navigate in session list');
  console.log('• 按 [c] 查看会话输出');
  console.log('• Press [c] to view session output');
  console.log('• 按 [s] 查看详细状态');
  console.log('• Press [s] to view detailed status');
  console.log('• 按 [f] 使用过滤器快速查找');
  console.log('• Press [f] to use filters for quick search\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示完成/Demo completed！');
  console.log('\n按 Ctrl+C 退出此演示/Press Ctrl+C to exit this demo.');
  console.log('会话将保留，可以在 TUI 中管理。');
  console.log('Sessions will remain and can be managed in TUI.\n');
}

main().catch(err => {
  console.error('错误/Error:', err.message);
  process.exit(1);
});