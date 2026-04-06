#!/usr/bin/env node

const utils = require("../lib/utils");
const key = require("../lib/key");
const douyin = require("../lib/douyin");
const fs = require("fs");
const path = require("path");

/**
 * 打印帮助信息
 */
function printHelp() {
  console.log(`
用法: node scripts/search.js <关键词> [选项]

选项:
  --keyword \t<关键词> \t搜索关键词
  --sort \t<排序> \t排序依据, 0: 综合排序(默认), 1: 最多点赞, 2: 最新发布
  --time \t<时间> \t发布时间, 0: 全部(默认), 1: 一天内, 7: 七天内, 180: 半年内
  --limit \t<数量> \t搜索数量 (默认 10, 最大 60)
  --output \t<格式> \t输出格式, json, markdown (默认 json)
  --help \t显示帮助信息

示例1: node scripts/search.js AI
示例2: node scripts/search.js "AI 模型"
示例3: node scripts/search.js --keyword AI --sort 0 --time 0 --limit 10 --output json
示例4: node scripts/search.js --keyword "AI 模型" --sort 1 --time 180 --limit 20 --output markdown

注意: 
  - 关键词建议 2-50 个汉字，避免特殊符号
  - 请确保环境变量 GUAIKEI_API_TOKEN 已配置
  - 所有参数都会自动清洗和验证
`);
}

process.on("SIGTERM", () => {
  utils.printWarn("OpenClaw 终止任务， 清理临时文件...");
  const outputPath = path.join(__dirname, "last-search.json");
  if (fs.existsSync(outputPath)) {
    fs.unlinkSync(outputPath);
  }
  process.exit(0);
});

async function main() {
  const startTime = Date.now();
  const args = process.argv.slice(2);
  if (args.length === 0) {
    printHelp();
    return;
  }

  let keyword = "",
    sort = 0,
    time = 0,
    limit = 10,
    output = "json";
  args.forEach((arg, index) => {
    if (arg === "--keyword") {
      keyword = args[index + 1] || "";
    } else if (arg === "--sort") {
      sort = args[index + 1] || 0;
      sort = Number(sort);
    } else if (arg === "--time") {
      time = args[index + 1] || 0;
      time = Number(time);
    } else if (arg === "--limit") {
      limit = args[index + 1] || 10;
      limit = Number(limit);
    } else if (arg === "--output") {
      output = args[index + 1] || "json";
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      return;
    } else if (arg.startsWith("--") === false && keyword === "") {
      keyword = arg;
    }
  });
  if (keyword === "") {
    utils.printError(`未提供关键词`);
    printHelp();
    return;
  }

  utils.printBanner();
  utils.printInfo(`原始关键词: ${keyword}`);
  let isRight = douyin.notIdealFormat(keyword);
  if (!isRight) {
    return;
  }
  keyword = douyin.sanitizeKeyword(keyword);
  utils.printInfo(`清洗后关键词: ${keyword}`);

  [sort, time, limit, output] = douyin.optionFormat(sort, time, limit, output);
  utils.printInfo(
    `排序: ${sort}, 时间: ${time}, 数量: ${limit}, 输出格式: ${output}`,
  );

  // 幂等性校验： 同一关键词+参数 2 分钟内不重复执行
  const taskId = `${keyword}_${sort}_${time}_${limit}`;
  const taskLockFile = path.join(__dirname, `.lock_${taskId}`);
  if (fs.existsSync(taskLockFile)) {
    const lockTime = fs.statSync(taskLockFile).mtimeMs;
    if (Date.now() - lockTime < 2 * 60 * 1000) {
      utils.printError(`同一任务 2 分钟内执行, 避免重复请求 API`);
      process.exit(1);
    } else {
      fs.unlinkSync(taskLockFile);
    }
  }
  // 创建锁文件
  fs.writeFileSync(taskLockFile, Date.now().toString(), { mode: 0o600 });

  const token = key.apiKey(process.env.GUAIKEI_API_TOKEN);
  let searchTask = null;
  try {
    const status = await douyin.createWithRetry(
      token,
      keyword,
      sort,
      time,
      limit,
    );
    if (status.errcode !== 0) {
      throw new Error(
        `搜索任务创建失败时, 遇到未知错误, 请反馈给开发者 ${status} - ${Date.now()}`,
      );
    }
    utils.printSuccess(`搜索任务创建成功, 正在搜索中...`);

    searchTask = await douyin.searchWithRetry(
      token,
      keyword,
      sort,
      time,
      limit,
    );
  } catch (error) {
    const errorOutput = {
      status: "error",
      keyword: keyword,
      message: error.message,
      error_code: error.code || "UNKNOWN",
      sort: sort,
      time: time,
      limit: limit,
      output_format: output,
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(errorOutput, null, 2));
    return;
  } finally {
    // 删除锁文件
    if (fs.existsSync(taskLockFile)) {
      fs.unlinkSync(taskLockFile);
    }
  }
  if (!searchTask || !Array.isArray(searchTask) || searchTask.length === 0) {
    utils.printError(`搜索任务没有返回结果, 请稍后重试或联系开发者`);
    const emptyOutput = {
      status: "empty",
      keyword: keyword,
      message: "没有找到匹配的视频或图文内容",
      sort: sort,
      time: time,
      limit: limit,
      output_format: output,
      timestamp: new Date().toLocaleString(),
      results: [],
    };
    console.log(JSON.stringify(emptyOutput, null, 2));
    return;
  }

  // 输出搜索结果
  const finalOutput = {
    status: "success",
    keyword: keyword,
    message: "搜索任务完成",
    sort: sort,
    time: time,
    limit: limit,
    output_format: output,
    total: searchTask.length,
    timestamp: new Date().toLocaleString(),
    openclaw_metadata: {
      skill_version: "1.1.1",
      runtime_version: process.versions.node,
      execution_time: Date.now() - startTime,
    },
    results: searchTask,
  };
  if (output === "markdown") {
    const message = douyin.formatMessage(keyword, searchTask);
    utils.printInfo(message);
    utils.printSuccess(`搜索任务完成, 共返回 ${searchTask.length} 条结果`);
  } else {
    console.log(JSON.stringify(finalOutput, null, 2));
    utils.printSuccess(`搜索任务完成, 共返回 ${finalOutput.total} 条结果`);
  }

  // 保存搜索结果到文件
  const outputPath = path.join(__dirname, "last-search.json");
  fs.writeFileSync(outputPath, JSON.stringify(finalOutput, null, 2));
  utils.printSuccess(`  → 已保存到 ${outputPath}`);
}

main().catch((error) => {
  utils.printError(error);
  process.exit(1);
});
