#!/usr/bin/env bun
/**
 * Configuration Manager Demo
 * Demonstrates the TUI configuration management features
 */

import { TUIConfigManager } from './config.ts';

async function main() {
  const configManager = new TUIConfigManager();

  console.log('╔══════════════════════════════════════════════════════════════════════════╗');
  console.log('║              Tmux TUI - 配置管理演示/Configuration Demo               ║');
  console.log('╚══════════════════════════════════════════════════════════════════════════╝\n');

  console.log('当前配置/Current Configuration:\n');
  const config = configManager.getAll();
  
  console.log('语言/Language:'.padEnd(30) + config.language);
  console.log('刷新间隔/Refresh Interval:'.padEnd(30) + `${config.refreshInterval}秒/s`);
  console.log('显示时间戳/Show Timestamps:'.padEnd(30) + (config.showTimestamps ? '是/Yes' : '否/No'));
  console.log('颜色主题/Color Theme:'.padEnd(30) + config.colorTheme);
  console.log('最大输出行数/Max Output Lines:'.padEnd(30) + config.maxOutputLines);
  console.log('自动清理时间/Auto Cleanup:'.padEnd(30) + `${config.autoCleanupHours}小时/hours`);
  console.log('确认终止/Confirm Kill:'.padEnd(30) + (config.confirmKill ? '是/Yes' : '否/No'));
  console.log('显示完整命令/Show Full Command:'.padEnd(30) + (config.showFullCommand ? '是/Yes' : '否/No'));

  console.log('\n─────────────────────────────────────────────────────────────────────────\n');

  console.log('配置选项说明/Configuration Options:\n');
  console.log('🌐 语言/Language');
  console.log('   • bilingual: 双语显示/Bilingual display (默认/default)');
  console.log('   • zh: 仅中文/Chinese only');
  console.log('   • en: 仅英文/English only\n');

  console.log('⏱️ 刷新间隔/Refresh Interval');
  console.log('   • 自动刷新会话列表的时间间隔/Time interval for auto-refreshing session list');
  console.log('   • 单位：秒/Unit: seconds');
  console.log('   • 默认值：5秒/Default: 5s\n');

  console.log('📝 显示时间戳/Show Timestamps');
  console.log('   • 在输出中显示时间戳/Show timestamps in output');
  console.log('   • 默认值：是/Default: Yes\n');

  console.log('🎨 颜色主题/Color Theme');
  console.log('   • default: 默认主题/Default theme');
  console.log('   • dark: 深色主题/Dark theme');
  console.log('   • light: 浅色主题/Light theme\n');

  console.log('📊 最大输出行数/Max Output Lines');
  console.log('   • 捕获输出时的最大行数/Maximum lines when capturing output');
  console.log('   • 默认值：200行/Default: 200 lines\n');

  console.log('🧹 自动清理时间/Auto Cleanup Hours');
  console.log('   • 自动清理会话的时间阈值/Time threshold for auto-cleanup');
  console.log('   • 单位：小时/Unit: hours');
  console.log('   • 默认值：24小时/Default: 24h\n');

  console.log('⚠️ 确认终止/Confirm Kill');
  console.log('   • 终止会话前是否需要确认/Whether confirmation is required before killing session');
  console.log('   • 默认值：是/Default: Yes\n');

  console.log('🔤 显示完整命令/Show Full Command');
  console.log('   • 是否显示完整的命令行/Whether to show full command line');
  console.log('   • 默认值：否/Default: No\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('修改配置示例/Modify Configuration Examples:\n');
  console.log('// 设置语言为仅中文/Set language to Chinese only');
  console.log('configManager.set("language", "zh");');
  console.log('await configManager.save();\n');

  console.log('// 设置刷新间隔为 10 秒/Set refresh interval to 10 seconds');
  console.log('configManager.set("refreshInterval", 10);');
  console.log('await configManager.save();\n');

  console.log('// 禁用终止确认/Disable kill confirmation');
  console.log('configManager.set("confirmKill", false);');
  console.log('await configManager.save();\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('重置配置/Reset Configuration:\n');
  console.log('// 重置为默认值/Reset to default values');
  console.log('configManager.reset();');
  console.log('await configManager.save();\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('配置文件位置/Configuration File Location:\n');
  console.log(`${process.env.HOME}/.pi-tmux-tui-config.json\n`);

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('💡 提示/Tips:\n');
  console.log('• 配置修改后需要重启 TUI 才能生效');
  console.log('• Configuration changes require TUI restart to take effect');
  console.log('• 您可以直接编辑配置文件');
  console.log('• You can edit the configuration file directly');
  console.log('• 配置文件使用 JSON 格式');
  console.log('• Configuration file uses JSON format\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('查看当前配置文件/View Current Configuration File:\n');
  console.log('cat ~/.pi-tmux-tui-config.json\n');

  console.log('─────────────────────────────────────────────────────────────────────────\n');

  console.log('演示完成/Demo completed！');
}

main().catch(err => {
  console.error('错误/Error:', err.message);
  process.exit(1);
});