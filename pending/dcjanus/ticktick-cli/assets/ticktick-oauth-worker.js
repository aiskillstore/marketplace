// Cloudflare Worker 的 TickTick OAuth 服务脚本。
// 仅提供 /authorize 与 /callback 两个端点。

const TICKTICK_AUTH_URL = "https://dida365.com/oauth/authorize";
const TICKTICK_TOKEN_URL = "https://dida365.com/oauth/token";
const TICKTICK_REDIRECT_URI =
  "https://ticktick-oauth.dcjanus.workers.dev/callback";

/**
 * 返回 JSON 响应。
 * @param {unknown} data 响应数据
 * @param {number} status HTTP 状态码
 * @returns {Response}
 */
function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/**
 * 构造 TickTick OAuth 授权地址。
 * @param {Object} params 参数集合
 * @param {string} params.clientId 客户端 ID
 * @param {string} params.redirectUri 回调地址
 * @param {string} [params.state] 状态值
 * @param {string} [params.scope] 授权范围
 * @param {string} [params.responseType] 响应类型
 * @returns {string}
 */
function buildAuthorizeUrl({
  clientId,
  redirectUri,
  state,
  scope,
  responseType = "code",
}) {
  const url = new URL(TICKTICK_AUTH_URL);
  url.searchParams.set("client_id", clientId);
  url.searchParams.set("redirect_uri", redirectUri);
  url.searchParams.set("response_type", responseType);
  if (scope) {
    url.searchParams.set("scope", scope);
  }
  if (state) {
    url.searchParams.set("state", state);
  }
  return url.toString();
}

/**
 * 使用授权码换取 Token。
 * @param {Object} params 参数集合
 * @param {string} params.code 授权码
 * @param {string} params.clientId 客户端 ID
 * @param {string} params.clientSecret 客户端密钥
 * @param {string} params.redirectUri 回调地址
 * @returns {Promise<{status: number, data: unknown}>}
 */
async function exchangeCodeForToken({
  code,
  clientId,
  clientSecret,
  redirectUri,
}) {
  const body = new URLSearchParams();
  body.set("grant_type", "authorization_code");
  body.set("code", code);
  body.set("client_id", clientId);
  body.set("client_secret", clientSecret);
  body.set("redirect_uri", redirectUri);

  const response = await fetch(TICKTICK_TOKEN_URL, {
    method: "POST",
    headers: {
      "content-type": "application/x-www-form-urlencoded",
    },
    body,
  });

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  return { status: response.status, data };
}

/**
 * 读取必需的环境变量。
 * @param {Record<string, string>} env Worker 环境绑定
 * @param {string} key 键名
 * @returns {string}
 */
function getEnvVar(env, key) {
  const value = env?.[key];
  if (!value) {
    throw new Error(`Missing env: ${key}`);
  }
  return value;
}

export default {
  /**
   * Cloudflare Worker 入口。
   * @param {Request} request 请求对象
   * @param {Record<string, string>} env 环境变量
   * @param {ExecutionContext} ctx 执行上下文
   * @returns {Promise<Response>}
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/authorize") {
      // 启动 OAuth 授权流程：重定向到 TickTick 授权页面。
      const clientId = getEnvVar(env, "TICKTICK_CLIENT_ID");
      const redirectUri = TICKTICK_REDIRECT_URI;
      const state = url.searchParams.get("state") || "";
      const scope = url.searchParams.get("scope") || "";

      const authorizeUrl = buildAuthorizeUrl({
        clientId,
        redirectUri,
        state,
        scope,
      });
      return new Response(null, {
        status: 302,
        headers: {
          location: authorizeUrl,
          "cache-control": "no-store",
        },
      });
    }

    if (path === "/callback") {
      // 处理 OAuth 回调：使用 code 换取 token。
      const code = url.searchParams.get("code");
      const state = url.searchParams.get("state");
      const error = url.searchParams.get("error");

      if (error) {
        return json({ ok: false, error, state }, 400);
      }

      if (!code) {
        return json({ ok: false, error: "missing_code", state }, 400);
      }

      const clientId = getEnvVar(env, "TICKTICK_CLIENT_ID");
      const clientSecret = getEnvVar(env, "TICKTICK_CLIENT_SECRET");
      const redirectUri = TICKTICK_REDIRECT_URI;

      const tokenResult = await exchangeCodeForToken({
        code,
        clientId,
        clientSecret,
        redirectUri,
      });

      if (tokenResult.status < 200 || tokenResult.status >= 300) {
        return json(
          {
            error: "token_exchange_failed",
            status: tokenResult.status,
            details: tokenResult.data,
          },
          tokenResult.status,
        );
      }

      const accessToken =
        tokenResult.data &&
        typeof tokenResult.data === "object" &&
        "access_token" in tokenResult.data
          ? tokenResult.data.access_token
          : null;

      if (!accessToken) {
        return json(
          {
            error: "missing_access_token",
            status: tokenResult.status,
            details: tokenResult.data,
          },
          502,
        );
      }

      return json({ access_token: accessToken });
    }

    return json({ ok: false, error: "not_found" }, 404);
  },
};
