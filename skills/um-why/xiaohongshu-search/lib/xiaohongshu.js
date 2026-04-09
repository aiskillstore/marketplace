/**
 * 小红书笔记搜索模块
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
function optionFormat(type, sort, limit, output) {
  type = type || 0;
  sort = sort || 0;
  limit = limit || 10;
  output = output || "json";
  if (type !== 0 && type !== 1 && type !== 2) {
    utils.printError(`搜索类型 ${type} 无效, 请使用 0, 1, 2。 默认值为 0`);
    type = 0;
  }
  if (sort !== 0 && sort !== 1 && sort !== 2 && sort !== 3 && sort !== 4) {
    utils.printError(
      `排序依据 ${sort} 无效, 请使用 0, 1, 2, 3, 4。 默认值为 0`,
    );
    sort = 0;
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
  return [type, sort, limit, output];
}

function formatMessage(keyword, result) {
  let message = `**小红书笔记搜索结果**: ${keyword}\n`;
  message += "-".repeat(35) + "\n\n";
  for (let i = 0; i < result.length; i++) {
    const item = result[i];
    message += `**${i + 1} .** ${item.title || "[无标题]"}\n`;
    message += `**发布时间**: ${item.publish_time || "[未知]"}\n`;
    message += `**链接**: ${item.url || "[未知]"}\n`;
    message += `**发布人**: ${item.user.nickname || "[未知]"}\n`;
    if (item.image_list && item.image_list.length > 0) {
      message += `**图文**: ${item.image_list.slice(0, 3).join(", ")}...\n`;
    }
    message += `**点赞**: ${item.liked_count || 0}\t`;
    message += `**评论**: ${item.comment_count || 0}\t`;
    message += `**收藏**: ${item.collected_count || 0}\t`;
    message += `**分享**: ${item.shared_count || 0}\n`;
    message += "\n";
  }
  message += "-".repeat(35) + "\n";
  message += `**共 ${result.length} 条结果**\n`;
  return message;
}

async function createWithRetry(token, keyword, type, sort, limit) {
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
        createSearchTask(token, keyword, type, sort, limit),
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
 * 创建小红书笔记搜索任务
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} type - 搜索类型, 0: 全部, 1: 视频, 2: 图文
 * @param {number} sort - 排序依据, 0: 综合, 1: 最新, 2: 最多点赞, 3: 最多评论, 4: 最多收藏
 * @param {number} limit - 搜索数量, 1-60
 * @returns {Promise<Object>} 搜索任务状态
 * @throws {Error} API调用失败时抛出错误
 */
async function createSearchTask(token, keyword, type, sort, limit) {
  return new Promise((resolve, reject) => {
    const url = "/api/xiaohongshu/note-search/keyword";
    const params = { _: Date.now(), token: token };
    const data = JSON.stringify({
      keyword,
      type,
      sort,
      limit,
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

async function searchWithRetry(token, keyword, type, sort, limit) {
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
        getSearchTask(token, keyword, type, sort, limit),
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
 * 获取小红书笔记搜索任务结果
 * @param {string} token - API令牌
 * @param {string} keyword - 搜索关键词
 * @param {number} type - 搜索类型, 0: 全部, 1: 视频, 2: 图文
 * @param {number} sort - 排序依据, 0: 综合, 1: 最新, 2: 最多点赞, 3: 最多评论, 4: 最多收藏
 * @param {number} limit - 搜索数量, 1-60
 * @returns {Promise<Array>} 搜索结果数组
 * @throws {Error} API调用失败时抛出错误
 */
async function getSearchTask(token, keyword, type, sort, limit) {
  return new Promise((resolve, reject) => {
    const url = "/api/xiaohongshu/note-search/info";
    const params = {
      _: Date.now(),
      token: token,
      keyword: keyword,
      type: type,
      sort: sort,
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
                if (item.id && item.xsec_token) {
                  json.data[i].url =
                    "https://www.xiaohongshu.com/explore/" +
                    item.id +
                    "?xsec_token=" +
                    item.xsec_token;
                }
                if (item.user && item.user.user_id && item.user.xsec_token) {
                  json.data[i].user.url =
                    "https://www.xiaohongshu.com/user/profile/" +
                    item.user.user_id +
                    "?xsec_token=" +
                    item.user.xsec_token;
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
