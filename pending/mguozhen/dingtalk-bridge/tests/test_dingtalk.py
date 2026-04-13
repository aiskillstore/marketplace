#!/usr/bin/env python3
"""Regression tests for dingtalk-bridge skill.

Run: python3 test_dingtalk.py
No network access required — all API calls are mocked.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add src to path
SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "src"))


class TestConfig(unittest.TestCase):
    """Test config.py: env vars > config.json > defaults."""

    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {}, clear=False)
        self.env_patcher.start()
        # Force reload of config module each test
        if "config" in sys.modules:
            del sys.modules["config"]
        import config
        self.config = config

    def tearDown(self):
        self.env_patcher.stop()

    def test_env_var_takes_priority(self):
        os.environ["DINGTALK_APP_KEY"] = "env_key_123"
        with patch.object(self.config, "_load_file_config", return_value={"app_key": "file_key"}):
            self.assertEqual(self.config.app_key(), "env_key_123")

    def test_file_config_fallback(self):
        os.environ.pop("DINGTALK_APP_KEY", None)
        with patch.object(self.config, "_load_file_config", return_value={"app_key": "file_key_456"}):
            self.assertEqual(self.config.app_key(), "file_key_456")

    def test_require_raises_on_missing(self):
        os.environ.pop("DINGTALK_APP_KEY", None)
        with patch.object(self.config, "_load_file_config", return_value={}):
            with self.assertRaises(RuntimeError) as ctx:
                self.config.require("app_key")
            self.assertIn("DINGTALK_APP_KEY", str(ctx.exception))

    def test_defaults(self):
        self.assertEqual(self.config.max_reply_len(), 3000)
        self.assertEqual(self.config.keepalive_interval(), 20)
        self.assertEqual(self.config.claude_bin(), "claude")

    def test_env_override_numeric(self):
        os.environ["DINGTALK_MAX_REPLY"] = "5000"
        self.assertEqual(self.config.max_reply_len(), 5000)

    def test_conv_file_default(self):
        path = self.config.conv_file()
        self.assertTrue(str(path).endswith("data/conv.json"))

    def test_conv_file_env_override(self):
        os.environ["DINGTALK_CONV_FILE"] = "/tmp/my_conv.json"
        self.assertEqual(str(self.config.conv_file()), "/tmp/my_conv.json")


class TestSend(unittest.TestCase):
    """Test send.py: message formatting and API call structure."""

    def setUp(self):
        # Ensure config is available with test values
        os.environ["DINGTALK_APP_KEY"] = "test_key"
        os.environ["DINGTALK_APP_SECRET"] = "test_secret"
        if "config" in sys.modules:
            del sys.modules["config"]
        if "send" in sys.modules:
            del sys.modules["send"]
        import send
        self.send = send

    def tearDown(self):
        os.environ.pop("DINGTALK_APP_KEY", None)
        os.environ.pop("DINGTALK_APP_SECRET", None)

    @patch("send.urllib.request.urlopen")
    def test_get_access_token(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"accessToken": "tok_abc"}).encode()
        mock_urlopen.return_value = mock_resp

        token = self.send._get_access_token()
        self.assertEqual(token, "tok_abc")

        # Verify the request payload
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertIn("oauth2/accessToken", req.full_url)
        body = json.loads(req.data)
        self.assertEqual(body["appKey"], "test_key")
        self.assertEqual(body["appSecret"], "test_secret")

    def test_save_conv_info(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            conv_path = Path(tmpdir) / "sub" / "conv.json"
            with patch("send.config") as mock_cfg:
                mock_cfg.conv_file.return_value = conv_path
                self.send.save_conv_info("conv_123", "robot_456")
                self.assertTrue(conv_path.exists())
                data = json.loads(conv_path.read_text())
                self.assertEqual(data["openConversationId"], "conv_123")
                self.assertEqual(data["robotCode"], "robot_456")

    @patch("send.urllib.request.urlopen")
    @patch("send._get_access_token", return_value="tok_xyz")
    @patch("send._get_conv_info", return_value={"openConversationId": "conv1", "robotCode": "bot1"})
    def test_send_markdown_payload(self, mock_conv, mock_token, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"processQueryKey":"ok"}'
        mock_urlopen.return_value = mock_resp

        self.send.send_markdown("Test Title", "**Hello** world")

        req = mock_urlopen.call_args[0][0]
        self.assertIn("groupMessages/send", req.full_url)
        body = json.loads(req.data)
        self.assertEqual(body["robotCode"], "bot1")
        self.assertEqual(body["openConversationId"], "conv1")
        self.assertEqual(body["msgKey"], "sampleMarkdown")
        param = json.loads(body["msgParam"])
        self.assertEqual(param["title"], "Test Title")
        self.assertEqual(param["text"], "**Hello** world")

    @patch("send.urllib.request.urlopen")
    @patch("send._get_access_token", return_value="tok_xyz")
    @patch("send._get_conv_info", return_value={"openConversationId": "conv1", "robotCode": "bot1"})
    def test_send_text_payload(self, mock_conv, mock_token, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"processQueryKey":"ok"}'
        mock_urlopen.return_value = mock_resp

        self.send.send_text("plain message")

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data)
        self.assertEqual(body["msgKey"], "sampleText")
        param = json.loads(body["msgParam"])
        self.assertEqual(param["content"], "plain message")

    @patch("send.urllib.request.urlopen")
    def test_reply_via_webhook(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_urlopen.return_value = mock_resp

        self.send.reply_via_webhook("https://hook.example.com/xxx", "Title", "Content")

        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://hook.example.com/xxx")
        body = json.loads(req.data)
        self.assertEqual(body["msgtype"], "markdown")
        self.assertEqual(body["markdown"]["title"], "Title")
        self.assertEqual(body["markdown"]["text"], "Content")

    def test_get_conv_info_missing_file(self):
        with patch("send.config") as mock_cfg:
            mock_cfg.conv_file.return_value = Path("/nonexistent/conv.json")
            with self.assertRaises(FileNotFoundError):
                self.send._get_conv_info()


class TestStreamBot(unittest.TestCase):
    """Test stream_bot.py: handler logic and execute_prompt."""

    def setUp(self):
        os.environ["DINGTALK_APP_KEY"] = "test_key"
        os.environ["DINGTALK_APP_SECRET"] = "test_secret"
        os.environ["DINGTALK_WORKDIR"] = tempfile.gettempdir()
        for mod in ["config", "send", "stream_bot"]:
            if mod in sys.modules:
                del sys.modules[mod]

    def tearDown(self):
        for key in ["DINGTALK_APP_KEY", "DINGTALK_APP_SECRET", "DINGTALK_WORKDIR"]:
            os.environ.pop(key, None)

    @patch("stream_bot.send_markdown")
    @patch("stream_bot.subprocess.run")
    @patch("stream_bot.reply")
    def test_execute_prompt_success(self, mock_reply, mock_run, mock_send):
        import stream_bot

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="The answer is 42.",
            stderr="",
        )

        stream_bot.execute_prompt("What is the answer?", "https://hook.test")

        # Should have called reply for "Processing" status
        mock_reply.assert_called_once()
        self.assertIn("Processing", mock_reply.call_args[0][2])

        # Should have called send_markdown with result
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        self.assertEqual(args[0], "Done")
        self.assertIn("The answer is 42", args[1])

    @patch("stream_bot.send_markdown")
    @patch("stream_bot.subprocess.run")
    @patch("stream_bot.reply")
    def test_execute_prompt_failure(self, mock_reply, mock_run, mock_send):
        import stream_bot

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: something broke",
        )

        stream_bot.execute_prompt("bad prompt", None)

        mock_send.assert_called()
        args = mock_send.call_args[0]
        self.assertEqual(args[0], "Failed")
        self.assertIn("something broke", args[1])

    @patch("stream_bot.send_markdown")
    @patch("stream_bot.subprocess.run")
    @patch("stream_bot.reply")
    def test_execute_prompt_truncation(self, mock_reply, mock_run, mock_send):
        import stream_bot

        long_output = "x" * 5000
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=long_output,
            stderr="",
        )

        stream_bot.execute_prompt("generate long text", None)

        args = mock_send.call_args[0]
        self.assertIn("truncated", args[1])
        # The total message should respect max_reply_len
        self.assertLess(len(args[1]), 5000)

    @patch("stream_bot.send_markdown")
    @patch("stream_bot.subprocess.run", side_effect=__import__("subprocess").TimeoutExpired(cmd="claude", timeout=300))
    @patch("stream_bot.reply")
    def test_execute_prompt_timeout(self, mock_reply, mock_run, mock_send):
        import stream_bot

        stream_bot.execute_prompt("slow prompt", None)

        args = mock_send.call_args[0]
        self.assertEqual(args[0], "Timeout")

    def test_handler_process_empty_text(self):
        import stream_bot
        import asyncio

        handler = stream_bot.BridgeHandler()
        callback = MagicMock()
        callback.data = {
            "text": {"content": "  "},
            "conversationId": "conv_1",
            "robotCode": "bot_1",
            "sessionWebhook": "",
        }

        loop = asyncio.new_event_loop()
        with patch("stream_bot.save_conv_info"):
            status, msg = loop.run_until_complete(handler.process(callback))
        loop.close()

        from dingtalk_stream import AckMessage
        self.assertEqual(status, AckMessage.STATUS_OK)

    def test_handler_process_spawns_thread(self):
        import stream_bot
        import asyncio

        handler = stream_bot.BridgeHandler()
        callback = MagicMock()
        callback.data = {
            "text": {"content": "hello bot"},
            "conversationId": "conv_1",
            "robotCode": "bot_1",
            "sessionWebhook": "https://hook.test",
        }

        loop = asyncio.new_event_loop()
        with patch("stream_bot.save_conv_info"), \
             patch("stream_bot.execute_prompt") as mock_exec, \
             patch("stream_bot.threading.Thread") as mock_thread:
            mock_thread_inst = MagicMock()
            mock_thread.return_value = mock_thread_inst
            status, msg = loop.run_until_complete(handler.process(callback))
        loop.close()

        mock_thread.assert_called_once()
        call_kwargs = mock_thread.call_args
        self.assertEqual(call_kwargs.kwargs["args"], ("hello bot", "https://hook.test"))
        self.assertTrue(call_kwargs.kwargs["daemon"])
        mock_thread_inst.start.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests: config file round-trip, conv save/load."""

    def test_config_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({
                "app_key": "roundtrip_key",
                "app_secret": "roundtrip_secret",
                "workdir": "/tmp",
            }))

            # Remove env vars so file config is used
            env = {k: v for k, v in os.environ.items()
                   if not k.startswith("DINGTALK_")}
            with patch.dict(os.environ, env, clear=True):
                if "config" in sys.modules:
                    del sys.modules["config"]
                import config
                with patch.object(config, "CONFIG_FILE", cfg_path):
                    self.assertEqual(config.app_key(), "roundtrip_key")
                    self.assertEqual(config.app_secret(), "roundtrip_secret")

    def test_conv_save_and_load(self):
        os.environ["DINGTALK_APP_KEY"] = "k"
        os.environ["DINGTALK_APP_SECRET"] = "s"
        with tempfile.TemporaryDirectory() as tmpdir:
            conv_path = Path(tmpdir) / "conv.json"
            os.environ["DINGTALK_CONV_FILE"] = str(conv_path)

            for mod in ["config", "send"]:
                if mod in sys.modules:
                    del sys.modules[mod]
            import send

            send.save_conv_info("test_conv_id", "test_robot_code")
            loaded = send._get_conv_info()
            self.assertEqual(loaded["openConversationId"], "test_conv_id")
            self.assertEqual(loaded["robotCode"], "test_robot_code")

        os.environ.pop("DINGTALK_CONV_FILE", None)
        os.environ.pop("DINGTALK_APP_KEY", None)
        os.environ.pop("DINGTALK_APP_SECRET", None)


class TestSkillFiles(unittest.TestCase):
    """Verify skill structure completeness."""

    def test_skill_md_exists(self):
        self.assertTrue((SKILL_DIR / "SKILL.md").exists())

    def test_skill_md_has_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: dingtalk-bridge", content)

    def test_required_files_exist(self):
        required = [
            "SKILL.md",
            "config.example.json",
            "src/__init__.py",
            "src/config.py",
            "src/send.py",
            "src/stream_bot.py",
            "scripts/install.sh",
            "tests/test_dingtalk.py",
        ]
        for f in required:
            self.assertTrue(
                (SKILL_DIR / f).exists(),
                f"Missing required file: {f}",
            )

    def test_install_script_executable(self):
        script = SKILL_DIR / "scripts" / "install.sh"
        # Just check it's a bash script
        content = script.read_text()
        self.assertTrue(content.startswith("#!/usr/bin/env bash"))

    def test_config_example_valid_json(self):
        content = (SKILL_DIR / "config.example.json").read_text()
        data = json.loads(content)
        self.assertIn("app_key", data)
        self.assertIn("app_secret", data)

    def test_no_hardcoded_credentials(self):
        """Ensure no real credentials are hardcoded in source files."""
        for src_file in (SKILL_DIR / "src").glob("*.py"):
            content = src_file.read_text()
            # Should not contain the old hardcoded key pattern
            self.assertNotIn("dingvz5dxr6e40nvhxgj", content,
                             f"Hardcoded credential found in {src_file.name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
