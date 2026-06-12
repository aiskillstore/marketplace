"""
browser_utils.py — 通用网页抓取工具模块

提供基于 curl + BeautifulSoup 的网页抓取能力，模拟真实浏览器请求。
其他 Skill 可以直接 import 使用：
    from browser_utils import fetch_page, get_site_config

依赖：pip install beautifulsoup4
"""

import subprocess
import time
import random

# 站点配置
SITE_CONFIG = {
    "US": {"domain": "amazon.com", "zip": "90001", "currency": "USD"},
    "UK": {"domain": "amazon.co.uk", "zip": "SW1A 1AA", "currency": "GBP"},
    "GB": {"domain": "amazon.co.uk", "zip": "SW1A 1AA", "currency": "GBP"},
    "DE": {"domain": "amazon.de", "zip": "10115", "currency": "EUR"},
    "FR": {"domain": "amazon.fr", "zip": "75001", "currency": "EUR"},
    "IT": {"domain": "amazon.it", "zip": "00100", "currency": "EUR"},
    "ES": {"domain": "amazon.es", "zip": "28001", "currency": "EUR"},
    "CA": {"domain": "amazon.ca", "zip": "M5V 2T6", "currency": "CAD"},
    "JP": {"domain": "amazon.co.jp", "zip": "100-0001", "currency": "JPY"},
    "MX": {"domain": "amazon.com.mx", "zip": "06600", "currency": "MXN"},
    "AU": {"domain": "amazon.com.au", "zip": "2000", "currency": "AUD"},
}

# 浏览器 User-Agent 池（轮换降低被检测概率）
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
]


def get_site_config(site_code: str) -> dict:
    """获取站点配置"""
    code = site_code.upper()
    if code not in SITE_CONFIG:
        raise ValueError(f"不支持的站点: {site_code}，支持: {', '.join(SITE_CONFIG.keys())}")
    return SITE_CONFIG[code]


def fetch_page(url: str, timeout: int = 30) -> str:
    """
    用 curl 抓取网页，返回完整 HTML。
    模拟真实浏览器的 HTTP 头，避免被反爬拦截。

    Args:
        url: 目标 URL
        timeout: 超时秒数

    Returns:
        HTML 字符串。抓取失败返回空字符串。
    """
    # 固定使用 Chrome macOS UA，这是验证过能通过亚马逊反爬的组合
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    try:
        result = subprocess.run(
            [
                "curl", "-sL",
                "--max-time", str(timeout),
                "-H", f"User-Agent: {ua}",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "-H", "Accept-Language: en-US,en;q=0.9",
                "-H", "Connection: keep-alive",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        return result.stdout
    except (subprocess.TimeoutExpired, Exception) as e:
        return ""


def check_captcha(html: str) -> bool:
    """检测是否命中验证码/拦截页面"""
    if len(html) < 10000:
        # 正常亚马逊商品页 > 500KB，小于 10KB 基本是拦截页
        lower = html.lower()
        captcha_signals = [
            "enter the characters you see below",
            "sorry, we just need to make sure you're not a robot",
            "api-services-support@amazon.com",
            "automated access to our website",
        ]
        return any(s in lower for s in captcha_signals)
    return False


def throttle(min_sec: float = 1.0, max_sec: float = 3.0):
    """请求间随机延迟，降低被限流概率"""
    time.sleep(random.uniform(min_sec, max_sec))
