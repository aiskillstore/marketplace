#!/usr/bin/env bun
/**
 * Filter Manager Demo
 * Demonstrates the session filtering and sorting features
 */

import { TmuxManager } from './lib.ts';
import { FilterManager } from './filter.ts';
import type { TmuxSession } from './types/index.js';

async function main() {
  const tmux = new TmuxManager();
  const filterManager = new FilterManager();

  console.log('╔══════════════════════════════════════════════════════════════════════════╗');
  console.log('║                Tmux TUI - 过滤管理演示/Filter Demo                    ║');
  console.log('╚══════════════════════════════════════════════════════════════════════════╝\n');

  console.log('创建示例会话/Creating example sessions...\n');

  // Create example sessions
  const sessions = [
    {
      name: 'dev-server',
      command: 'echo "Dev server" && sleep 60',
      category: 'service',
    },
    {
      name: 'build-task',
      command: 'echo "Building..." && sleep 30',
      category: 'task',
    },
    {
      name: 'test-runner',
      command: 'echo "Testing..." && sleep 45',
      category: 'task',
    },
    {
      name: 'db-service',
      command: 'echo "Database" && sleep 120',
      category: 'service',
    },
    {
      name: 'agent-worker',
      command: 'echo "Agent working" && sleep 90',
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

  // Get all sessions
  const allSessions = await tmux.listSessions();
  console.log(`总会话数/Total Sessions: ${allSessions.length}\n`);

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 1: 按分类过滤/Demo 1: Filter by Category\n');
  console.log('显示所有任务会话/Show task sessions:\n');
  
  filterManager.setCategory('task');
  const taskSessions = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  taskSessions.forEach(s => {
    console.log(`  ${s.id}`);
    console.log(`  分类/Category: ${s.category} | 状态/Status: ${s.status}\n`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 2: 按状态过滤/Demo 2: Filter by Status\n');
  console.log('显示运行中的会话/Show running sessions:\n');
  
  filterManager.reset();
  filterManager.setStatus('running');
  const runningSessions = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  runningSessions.forEach(s => {
    console.log(`  ${s.id}`);
    console.log(`  分类/Category: ${s.category} | 状态/Status: ${s.status}\n`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 3: 组合过滤/Demo 3: Combined Filter\n');
  console.log('显示运行中的服务会话/Show running service sessions:\n');
  
  filterManager.reset();
  filterManager.setCategory('service');
  filterManager.setStatus('running');
  const filteredSessions = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  filteredSessions.forEach(s => {
    console.log(`  ${s.id}`);
    console.log(`  分类/Category: ${s.category} | 状态/Status: ${s.status}\n`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 4: 搜索功能/Demo 4: Search Function\n');
  console.log('搜索包含 "dev" 的会话/Search sessions containing "dev":\n');
  
  filterManager.reset();
  filterManager.setSearchQuery('dev');
  const searchResults = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  searchResults.forEach(s => {
    console.log(`  ${s.id}`);
    console.log(`  名称/Name: ${s.name} | 命令/Command: ${s.command}\n`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 5: 排序功能/Demo 5: Sorting\n');
  console.log('按名称排序（升序）/Sort by name (ascending):\n');
  
  filterManager.reset();
  filterManager.setSortBy('name');
  filterManager.setSortOrder('asc');
  const sortedByName = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  sortedByName.forEach(s => {
    console.log(`  ${s.name} (${s.category})`);
  });

  console.log('\n按最后活动时间排序（降序）/Sort by last activity (descending):\n');
  
  filterManager.setSortBy('lastActivityAt');
  filterManager.setSortOrder('desc');
  const sortedByActivity = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  sortedByActivity.forEach(s => {
    const age = Math.floor((Date.now() - new Date(s.lastActivityAt).getTime()) / 60000);
    console.log(`  ${s.name} (${age}m ago)`);
  });

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示 6: 清除过滤器/Demo 6: Clear Filter\n');
  console.log('清除所有过滤器，显示全部会话/Clear all filters, show all sessions:\n');
  
  filterManager.reset();
  const allFiltered = filterManager.apply(allSessions);
  console.log(filterManager.getFilterSummary(allSessions));
  console.log('─'.repeat(80));
  allFiltered.forEach(s => {
    console.log(`  ${s.id}`);
  });

  console.log('\n─────────────────────────────────────────────────────────────────────────\n');

  console.log('TUI 中的过滤快捷键/Filter Shortcuts in TUI:\n');
  console.log('按 [f] 进入过滤器模式/Press [f] to enter filter mode\n');
  console.log('按分类过滤/Filter by Category:');
  console.log('  [1] 任务/Task');
  console.log('  [2] 服务/Service');
  console.log('  [3] 代理/Agent\n');
  console.log('按状态过滤/Filter by Status:');
  console.log('  [4] 运行中/Running');
  console.log('  [5] 空闲/Idle');
  console.log('  [6] 已退出/Exited\n');
  console.log('其他/Other:');
  console.log('  [c] 清除过滤/Clear filter');
  console.log('  [Esc] 返回列表/Return to list\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('💡 提示/Tips:\n');
  console.log('• 过滤器可以组合使用，例如同时按分类和状态过滤');
  console.log('• Filters can be combined, e.g., filter by both category and status');
  console.log('• 搜索功能会匹配会话 ID、名称和命令');
  console.log('• Search matches session ID, name, and command');
  console.log('• 排序不影响过滤结果，只改变显示顺序');
  console.log('• Sorting doesn\'t affect filtered results, only changes display order\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示完成/Demo completed！');
  console.log('\n清理示例会话/Cleaning up example sessions...');
  await tmux.cleanupOldSessions(0);
  console.log('✅ 已清理/Cleaned up');
}

main().catch(err => {
  console.error('错误/Error:', err.message);
  process.exit(1);
});