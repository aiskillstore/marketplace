# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""web_search.py 的最小回归测试（标准库 unittest，无需 pytest）。

运行：python3 byted-web-search/scripts/test_web_search.py
"""

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import web_search  # noqa: E402


class PrintApiErrorHintTest(unittest.TestCase):
    """Key 无效分支不得因未定义常量抛 NameError，且要指向 Agent Plan 取 Key 页面。"""

    def _assert_hint_ok(self, code: str) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            web_search._print_api_error_hint(code)
        out = buf.getvalue()
        self.assertIn(web_search.AGENT_PLAN_API_KEY_URL, out)

    def test_invalid_api_key_hint_does_not_crash(self) -> None:
        self._assert_hint_ok("invalid_api_key")

    def test_10403_hint_does_not_crash(self) -> None:
        self._assert_hint_ok("10403")


if __name__ == "__main__":
    unittest.main(verbosity=2)
