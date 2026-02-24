#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 获取项目根目录（脚本所在目录的上级目录）
const projectRoot = path.dirname(__dirname);

// 需要添加的语言列表
const languages = [
  'ar.json', 'fr.json', 'id.json', 'ja.json', 'ru.json', 'vi.json',
  'de.json', 'es.json', 'hi.json', 'it.json', 'pt.json', 'th.json', 'zh-hk.json', "ko.json"
];

// 语言代码映射（去掉.json后缀）
const languageCodes = languages.map(lang => lang.replace('.json', ''));

// 语言名称映射
const languageNames = {
  ar: 'العربية',
  de: 'Deutsch',
  es: 'Español',
  fr: 'Français',
  hi: 'हिन्दी',
  id: 'Bahasa Indonesia',
  it: 'Italiano',
  ja: '日本語',
  pt: 'Português',
  ru: 'Русский',
  th: 'ไทย',
  vi: 'Tiếng Việt',
  'zh-hk': '繁體中文',
  ko: '한국어'
};

// 目标目录列表（相对于项目根目录）
const targetDirs = [
  'i18n/messages',
  'i18n/pages/landing'
];

// 配置文件路径（相对于项目根目录）
const configFiles = {
  locale: 'i18n/locale.ts',
  request: 'i18n/request.ts',
  sitemap: 'public/sitemap.xml'
};

/**
 * 复制文件
 * @param {string} source 源文件路径
 * @param {string} target 目标文件路径
 */
function copyFile(source, target) {
  try {
    fs.copyFileSync(source, target);
    console.log(`✅ 已创建: ${target}`);
  } catch (error) {
    console.error(`❌ 创建失败 ${target}:`, error.message);
  }
}

/**
 * 检查文件是否存在
 * @param {string} filePath 文件路径
 * @returns {boolean}
 */
function fileExists(filePath) {
  return fs.existsSync(filePath);
}

/**
 * 检查目录是否存在
 * @param {string} dirPath 目录路径
 * @returns {boolean} 目录是否存在
 */
function checkDirectoryExists(dirPath) {
  return fs.existsSync(dirPath);
}

/**
 * 获取绝对路径
 * @param {string} relativePath 相对路径
 * @returns {string} 绝对路径
 */
function getAbsolutePath(relativePath) {
  return path.resolve(projectRoot, relativePath);
}

/**
 * 更新locale.ts文件
 */
function updateLocaleFile() {
  console.log('\n📝 更新 locale.ts 文件...');
  const localeFilePath = getAbsolutePath(configFiles.locale);
  
  // 检查文件是否存在
  if (!fileExists(localeFilePath)) {
    console.log('⏭️  locale.ts 文件不存在，跳过更新');
    return;
  }
  
  try {
    let content = fs.readFileSync(localeFilePath, 'utf8');
    
    // 确保有必要的导入
    if (!content.includes('import { Pathnames }')) {
      content = 'import { Pathnames } from "next-intl/routing";\n\n' + content;
    }
    
    // 读取现有的locales数组
    const localesMatch = content.match(/export const locales = \[(.*?)\];/s);
    if (localesMatch) {
      const currentLocales = localesMatch[1].split(',').map(l => l.trim().replace(/["']/g, ''));
      const allLocales = [...new Set([...currentLocales, ...languageCodes])].filter(l => l);
      const newLocalesArray = allLocales.map(l => `"${l}"`).join(', ');
      content = content.replace(/export const locales = \[(.*?)\];/s, `export const locales = [${newLocalesArray}];`);
    }
    
    // 更新localeNames对象
    const localeNamesMatch = content.match(/export const localeNames: any = \{([\s\S]*?)\};/);
    if (localeNamesMatch) {
      const currentNames = localeNamesMatch[1];
      const existingEntries = [];
      const newEntries = [];
      
      // 解析现有条目
      const entryRegex = /\s*(\w+|"[^"]+")\s*:\s*"[^"]*"/g;
      let match;
      while ((match = entryRegex.exec(currentNames)) !== null) {
        const key = match[1].replace(/"/g, '');
        existingEntries.push(key);
      }
      
      // 添加新的语言名称
      Object.entries(languageNames).forEach(([code, name]) => {
        if (!existingEntries.includes(code)) {
          const keyFormat = code.includes('-') ? `"${code}"` : code;
          newEntries.push(`  ${keyFormat}: "${name}"`);
        }
      });
      
      if (newEntries.length > 0) {
        // 重新构建localeNames对象
        const allEntries = [];
        
        // 保留现有条目（清理格式）
        const cleanCurrentNames = currentNames.replace(/\s*,\s*$/g, ''); // 移除末尾逗号
        if (cleanCurrentNames.trim()) {
          allEntries.push(cleanCurrentNames.trim());
        }
        
        // 添加新条目
        allEntries.push(...newEntries);
        
        const newNamesContent = allEntries.join(',\n');
        content = content.replace(/export const localeNames: any = \{([\s\S]*?)\};/, `export const localeNames: any = {\n${newNamesContent}\n};`);
      }
    }
    
    fs.writeFileSync(localeFilePath, content);
    console.log('✅ locale.ts 更新完成');
  } catch (error) {
    console.error('❌ 更新 locale.ts 失败:', error.message);
  }
}

/**
 * 更新request.ts文件
 */
function updateRequestFile() {
  console.log('\n📝 更新 request.ts 文件...');
  const requestFilePath = getAbsolutePath(configFiles.request);
  
  // 检查文件是否存在
  if (!fileExists(requestFilePath)) {
    console.log('⏭️  request.ts 文件不存在，跳过更新');
    return;
  }
  
  try {
    let content = fs.readFileSync(requestFilePath, 'utf8');
    
    // 确保有必要的导入
    if (!content.includes('import { getRequestConfig }')) {
      content = 'import { getRequestConfig } from "next-intl/server";\n' + content;
    }
    
    // 检查是否需要添加新的语言映射
    const zhCNMatch = content.match(/if \(\["zh-CN"\]\.includes\(locale\)\) \{[\s\S]*?\}/);
    if (zhCNMatch) {
      // 添加新的语言映射逻辑
      const newMappingLogic = `
  // 语言代码映射
  if (["zh-CN"].includes(locale)) {
    locale = "zh";
  }
  
  if (["zh-HK", "zh-hk"].includes(locale)) {
    locale = "zh-hk";
  }`;
      
      content = content.replace(
        /if \(\["zh-CN"\]\.includes\(locale\)\) \{[\s\S]*?\}/,
        newMappingLogic.trim()
      );
    }
    
    fs.writeFileSync(requestFilePath, content);
    console.log('✅ request.ts 更新完成');
  } catch (error) {
    console.error('❌ 更新 request.ts 失败:', error.message);
  }
}

/**
 * 更新sitemap.xml文件
 */
function updateSitemapFile() {
  console.log('\n📝 更新 sitemap.xml 文件...');
  const sitemapFilePath = getAbsolutePath(configFiles.sitemap);
  
  // 检查文件是否存在
  if (!fileExists(sitemapFilePath)) {
    console.log('⏭️  sitemap.xml 文件不存在，跳过更新');
    return;
  }
  
  try {
    let content = fs.readFileSync(sitemapFilePath, 'utf8');
    
    // 从现有sitemap中提取基础域名
    const locMatch = content.match(/<loc>([^<]+)<\/loc>/);
    if (!locMatch) {
      console.error('❌ 无法从sitemap中提取域名');
      return;
    }
    
    const firstUrl = locMatch[1];
    const baseUrl = firstUrl.replace(/\/[a-z-]+\/?$/, ''); // 移除语言路径
    const baseDomain = baseUrl.endsWith('/') ? baseUrl : baseUrl + '/';
    
    console.log(`📍 检测到域名: ${baseDomain}`);
    
    // 获取现有的语言链接
    const existingLangs = [];
    const hreflangMatches = content.matchAll(/hreflang="([^"]+)"/g);
    for (const match of hreflangMatches) {
      if (match[1] !== 'x-default') {
        existingLangs.push(match[1]);
      }
    }
    
    // 合并所有语言（包括现有的和新的）
    const allLangs = [...new Set([...existingLangs, ...languageCodes])];
    
    // 生成新的hreflang链接
    const generateHreflangs = (langs) => {
      return langs.map(lang => 
        `    <xhtml:link rel="alternate" hreflang="${lang}" href="${baseDomain}${lang === 'en' ? '' : lang}"/>`
      ).join('\n') + `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${baseDomain}"/>`;
    };
    
    // 生成新的URL条目
    const generateUrlEntries = (langs) => {
      return langs.map(lang => {
        const url = lang === 'en' ? baseDomain : `${baseDomain}${lang}`;
        return `  <url>
    <loc>${url}</loc>
    <lastmod>2025-06-15T10:00:00+00:00</lastmod>
${generateHreflangs(langs)}
  </url>`;
      }).join('\n');
    };
    
    // 重新生成整个sitemap内容
    const newContent = `<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${generateUrlEntries(allLangs)}
</urlset>`;
    
    fs.writeFileSync(sitemapFilePath, newContent);
    console.log('✅ sitemap.xml 更新完成');
  } catch (error) {
    console.error('❌ 更新 sitemap.xml 失败:', error.message);
  }
}

/**
 * 在指定目录下添加语言文件
 * @param {string} dir 目录路径（相对于项目根目录）
 */
function addLanguagesInDir(dir) {
  const absoluteDir = getAbsolutePath(dir);
  console.log(`\n📁 处理目录: ${absoluteDir}`);
  
  // 检查目录是否存在
  if (!checkDirectoryExists(absoluteDir)) {
    console.error(`❌ 目录不存在: ${absoluteDir}`);
    console.log(`💡 提示: 请先创建目录 ${absoluteDir}`);
    return;
  }
  
  const enFilePath = path.join(absoluteDir, 'en.json');
  
  // 检查 en.json 是否存在
  if (!fileExists(enFilePath)) {
    console.error(`❌ 源文件不存在: ${enFilePath}`);
    console.log(`💡 提示: 请确保在 ${absoluteDir} 目录下存在 en.json 文件作为模板`);
    return;
  }
  
  // 为每种语言创建文件
  languages.forEach(lang => {
    const targetPath = path.join(absoluteDir, lang);
    
    // 如果文件已存在，跳过
    if (fileExists(targetPath)) {
      console.log(`⏭️  文件已存在，跳过: ${targetPath}`);
      return;
    }
    
    // 复制 en.json 到目标语言文件
    copyFile(enFilePath, targetPath);
  });
}

/**
 * 检查项目结构
 * @returns {boolean} 项目结构是否有效
 */
function checkProjectStructure() {
  console.log('🔍 检查项目结构...');
  
  // 检查是否在正确的项目根目录
  const packageJsonPath = getAbsolutePath('package.json');
  if (!fileExists(packageJsonPath)) {
    console.error('❌ 未找到 package.json 文件');
    console.log('💡 请确保脚本在 Next.js 项目的 scripts 目录下运行');
    return false;
  }
  
  console.log(`✅ 项目根目录: ${projectRoot}`);
  return true;
}

/**
 * 主函数
 */
function main() {
  console.log('🚀 开始添加多语言支持...');
  console.log(`📋 需要添加的语言: ${languages.join(', ')}`);
  
  // 检查项目结构
  if (!checkProjectStructure()) {
    process.exit(1);
  }
  
  let hasErrors = false;
  
  // 处理语言文件目录
  targetDirs.forEach(dir => {
    try {
      addLanguagesInDir(dir);
    } catch (error) {
      console.error(`❌ 处理目录 ${dir} 时出错:`, error.message);
      hasErrors = true;
    }
  });
  
  // 更新配置文件
  try {
    updateLocaleFile();
    updateRequestFile();
    updateSitemapFile();
  } catch (error) {
    console.error('❌ 更新配置文件时出错:', error.message);
    hasErrors = true;
  }
  
  if (hasErrors) {
    console.log('\n⚠️  部分操作完成，但存在错误，请检查上述错误信息');
  } else {
    console.log('\n✅ 多语言支持添加完成！');
  }
  
  console.log('\n📋 已完成的操作:');
  console.log('   • 复制语言文件到目标目录');
  console.log('   • 更新 locale.ts 配置文件（如果存在）');
  console.log('   • 更新 request.ts 配置文件（如果存在）');
  console.log('   • 更新 sitemap.xml 文件（如果存在）');
  console.log('\n💡 使用提示:');
  console.log('   • 确保项目根目录有 package.json 文件');
  console.log('   • 确保目标目录存在并包含 en.json 作为模板文件');
  console.log('   • 可以修改脚本顶部的配置来适应不同的项目结构');
}

// 运行脚本
main();