/**
 * 抖音搜索模块
 */
const https = require("https");
const querystring = require("querystring");
const BASE_URL = "www.guaikei.com";
const utils = require("./utils");

/**
 * 检查搜索关键词是否符合要求
 */
function notIdealFormat(keyword) {
  keyword = keyword.trim();
  if (keyword.length < 2) {
    utils.printError(`搜索关键词长度不能小于 2 个字符`);
    return false;
  }
  if (keyword.length > 50) {
    utils.printError(`搜索关键词长度不能超过 50 个字符`);
    return false;
  }
  if (/[<>\"'&]/g.test(keyword)) {
    utils.printError(`搜索关键词包含特殊字符, 请输入普通关键词, 例如: 新媒体`);
    return false;
  }
  if (keyword.includes("http")) {
    utils.printError(
      `搜索关键词包含 http 链接, 请输入普通关键词, 例如: 新媒体`,
    );
    return false;
  }
  return true;
}

/**
 * 清洗搜索关键词
 */
function sanitizeKeyword(keyword) {
  let trimmed = keyword.trim();
  return trimmed.replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?# ，。！？]/g, "");
}

/**
 * 格式化搜索选项, 并检查是否有效
 */
function optionFormat(sort, time, limit, output) {
  sort = sort || 0;
  time = time || 0;
  limit = limit || 10;
  output = output || "json";
  if (sort !== 0 && sort !== 1 && sort !== 2) {
    utils.printError(`排序依据 ${sort} 无效, 请使用 0, 1, 2。 默认值为 0`);
    sort = 0;
  }
  if (time !== 0 && time !== 1 && time !== 7 && time !== 180) {
    utils.printError(`发布时间 ${time} 无效, 请使用 0, 1, 7, 180。 默认值为 0`);
    time = 0;
  }
  if (limit < 1 || limit > 60) {
    utils.printError(`搜索数量 ${limit} 无效, 请使用 1-60。 默认值为 10`);
    limit = 10;
  }
  if (output !== "json" && output !== "markdown") {
    utils.printError(
      `输出格式 ${output} 无效, 请使用 json, markdown。 默认值为 json`,
    );
    output = "json";
  }
  return [sort, time, limit, output];
}

function formatMessage(keyword, result) {
  let message = `**抖音综合搜索结果**: ${keyword}\n`;
  message += "-".repeat(35) + "\n\n";
  for (let i = 0; i < result.length; i++) {
    const item = result[i];
    message += `**${i + 1} .** ${item.desc || "[无标题]"}\n`;
    message += `**发布人**: ${item.author_nickname || "[未知]"}\n`;
    message += `**发布时间**: ${item.create_time_str || "[未知]"}\n`;
    message += `**链接**: ${item.url || "[未知]"}\n`;
    if (item.dynamic_cover && item.dynamic_cover.length > 0) {
      message += `**封面**: ${item.dynamic_cover[0] || ""}\n`;
    }
    if (item.play_addr) {
      message += `**视频**: ${item.play_addr}\n`;
    }
    if (item.images && item.images.length > 0) {
      message += `**图文**: ${item.images.slice(0, 3).join(", ")}...\n`;
    }
    message += `**点赞**: ${item.digg_count || 0}\t`;
    message += `**评论**: ${item.comment_count || 0}\t`;
    message += `**收藏**: ${item.collect_count || 0}\t`;
    message += `**分享**: ${item.share_count || 0}\n`;
    message += "\n";
  }
  message += "-".repeat(35) + "\n";
  message += `**共 ${result.length} 条结果**\n`;
  return message;
}

async function createWithRetry(token, keyword, sort, time, limit) {
  let lastError = null;
  const retryIntervals = [1000, 2000, 3000];
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(
          () => reject(new Error(`创建任务超时 (${attempt + 1}/3)`)),
          10000,
        ),
      );
      const task = await Promise.race([
        createSearchTask(token, keyword, sort, time, limit),
        timeoutPromise,
      ]);
      if (task.errcode === 0) return task;
      throw new Error(`创建任务失败, 错误信息: ${JSON.stringify(task.errmsg)}`);
    } catch (error) {
      lastError = error;
      utils.printInfo(
        `【创建任务重试】 ${attempt + 1}/3 次 - ${error.message}`,
      );
      if (attempt < 2) {
        await new Promise((resolve) =>
          setTimeout(resolve, retryIntervals[attempt]),
        );
      }
    }
  }
  throw lastError || new Error("创建搜索任务失败, 3次重试均失败");
}

/**
 * 创建抖音搜索任务
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} sort - 排序依据, 0: 综合排序, 1: 最多点赞, 2: 最新发布
 * @param {number} time - 发布时间, 0: 全部, 1: 一天内, 7: 七天内, 180: 半年内
 * @param {number} limit - 搜索数量, 1-60
 * @returns {Promise<Object>} 搜索任务状态
 * @throws {Error} API调用失败时抛出错误
 */
async function createSearchTask(token, keyword, sort, time, limit) {
  return new Promise((resolve, reject) => {
    const url = "/api/douyin/general-search/keyword";
    const params = { _: Date.now(), token: token };
    const data = JSON.stringify({
      keyword,
      sort_type: sort,
      publish_time: time,
      limit: limit,
    });
    const options = {
      hostname: BASE_URL,
      path: url + "?" + querystring.stringify(params),
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(data),
      },
      timeout: 20000,
    };
    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        if (res.statusCode === 200) {
          try {
            const json = JSON.parse(body);
            if (json.errcode === 0) {
              resolve(json);
            } else {
              reject(new Error(`请求错误信息: ${json.errmsg}`));
              return;
            }
          } catch (error) {
            reject(new Error(`解析响应失败: ${error.message}`));
            return;
          }
        } else if (
          res.statusCode === 401 ||
          res.statusCode === 407 ||
          res.statusCode === 403 ||
          res.statusCode === 410 ||
          res.statusCode === 408
        ) {
          reject(new Error(`GUAIKEI_API_TOKEN 无效, 请检查环境变量`));
        } else {
          reject(new Error(`请求失败, 状态码: ${res.statusCode}`));
        }
      });
    });
    req.on("error", (err) => {
      reject(err);
    });
    req.write(data);
    req.end();
  });
}

async function searchWithRetry(token, keyword, sort, time, limit) {
  let lastError = null;
  const maxAttempts = 60;
  const retryInterval = 2000;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error(`查询结果超时 (${attempt + 1}/${maxAttempts})`));
        }, 5000);
      });
      const data = await Promise.race([
        getSearchTask(token, keyword, sort, time, limit),
        timeoutPromise,
      ]);
      if (Array.isArray(data) && data.length > 0) return data;
      throw new Error(`第 ${attempt + 1} 次查询无结果`);
    } catch (error) {
      lastError = error;
      utils.printInfo(
        `【查询结果重试】尝试 ${attempt + 1} / ${maxAttempts} - ${error.message}`,
      );
      await new Promise((resolve) => setTimeout(resolve, retryInterval));
    }
  }
  throw lastError || new Error(`查询搜索结果失败, ${maxAttempts}次重试均失败`);
}

/**
 * 获取抖音搜索任务结果
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} sort - 排序依据, 0: 综合排序, 1: 最多点赞, 2: 最新发布
 * @param {number} time - 发布时间, 0: 全部, 1: 一天内, 7: 七天内, 180: 半年内
 * @param {number} limit - 搜索数量, 1-60
 * @returns {Promise<Array>} 搜索结果数组
 * @throws {Error} API调用失败时抛出错误
 */
async function getSearchTask(token, keyword, sort, time, limit) {
  return new Promise((resolve, reject) => {
    const url = "/api/douyin/general-search/info";
    const params = {
      _: Date.now(),
      token: token,
      keyword: keyword,
      sort_type: sort,
      publish_time: time,
      limit: limit,
    };
    const options = {
      hostname: BASE_URL,
      path: url + "?" + querystring.stringify(params),
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 20000,
    };
    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        if (res.statusCode === 200) {
          try {
            const json = JSON.parse(body);
            if (json.errcode === 0) {
              for (let i = 0; i < json.data.length; i++) {
                const item = json.data[i];
                if (item.author_sec_uid) {
                  json.data[i].author_url =
                    "https://www.douyin.com/user/" + item.author_sec_uid;
                }
                if (item.create_time && !item.create_time_str) {
                  json.data[i].create_time_str = new Date(
                    item.create_time * 1000,
                  ).toLocaleString();
                }
              }
              resolve(json.data);
            } else {
              reject(new Error(`请求错误信息: ${json.errmsg}`));
              return;
            }
          } catch (error) {
            reject(new Error(`解析响应失败: ${error.message}`));
            return;
          }
        } else if (
          res.statusCode === 401 ||
          res.statusCode === 407 ||
          res.statusCode === 403 ||
          res.statusCode === 410 ||
          res.statusCode === 408
        ) {
          reject(new Error(`GUAIKEI_API_TOKEN 无效, 请检查环境变量`));
        } else {
          reject(new Error(`请求失败, 状态码: ${res.statusCode}`));
        }
      });
    });
    req.on("error", (err) => {
      reject(err);
    });
    req.end();
  });
}

module.exports = {
  createWithRetry,
  formatMessage,
  optionFormat,
  notIdealFormat,
  sanitizeKeyword,
  searchWithRetry,
};
