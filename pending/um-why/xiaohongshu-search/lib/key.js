/**
 * TOKEN管理模块
 */
const utils = require("./utils");
function apiKey(token) {
  let isDefault = false;
  if (token == undefined) {
    isDefault = true;
  } else if (token == "") {
    isDefault = true;
  } else if (typeof token != "string") {
    isDefault = true;
  } else if (token.length != 32) {
    isDefault = true;
  }
  if (isDefault) {
    utils.printError(
      "未正确设置 GUAIKEI_API_TOKEN 环境变量, 将使用默认值, 可能影响搜索效率或搜索频率受限, 建议升级为私有TOKEN以获得更好的搜索体验",
    );
    return "e10adc3949ba59abbe56e057f20f883e";
  } else {
    return token;
  }
}

module.exports = {
  apiKey,
};
