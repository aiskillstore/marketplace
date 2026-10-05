"""Observable builder contracts. Run with Python's unittest discovery."""

import base64
from contextlib import redirect_stderr
import importlib.util
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_explorer", ROOT / "scripts" / "build_explorer.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ExplorerBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.manifest = self.folder / "manifest.json"
        self.output = self.folder / "output" / "explore.html"
        self.source = self.folder / "sample.html"
        self.source.write_text('<!doctype html><html><head><style>body{color:#123}</style></head><body>同一内容<script>window.bad=true</script></body></html>', encoding="utf-8")
        self.data = {"schemaVersion": 1, "project": "项目", "brief": "同一内容比较", "round": "01", "candidates": [{"id": "a", "name": "方向一", "concept": "编辑式", "typography": "宋体与黑体", "palette": ["#112233", "#fff"], "traits": ["大标题"], "kind": "html", "source": "sample.html"}]}
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_portable_single_file_and_html_payload(self):
        result = builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        self.assertEqual(result["candidates"], 1)
        self.assertIn("同一内容", page)
        self.assertNotIn(str(self.folder), page)
        self.assertNotIn(builder.MARKER, page)
        self.assertIn("script-src 'none'", page)

    def test_metadata_cannot_close_script(self):
        self.data["project"] = '</script><script>window.injected=true</script>'
        self.save()
        builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        self.assertNotIn(self.data["project"], page)
        self.assertIn('\\u003c/script>', page)

    def test_csp_is_inserted_in_actual_head_not_a_comment(self):
        self.source.write_text('''<!doctype html>
        <!-- Skeleton: <head> \u2028 extra text -->
        <html><head data-note="a > b"></head><body>content</body></html>''', encoding="utf-8")
        content = builder.prepare_html(self.source)
        observed = []
        class Tags(HTMLParser):
            def handle_starttag(self, tag, attrs):
                observed.append((tag, dict(attrs)))
        Tags().feed(content)
        meta = [attrs for tag, attrs in observed if tag == "meta"]
        self.assertEqual(meta, [{"http-equiv": "Content-Security-Policy", "content": builder.PREVIEW_CSP}])
        self.assertEqual([tag for tag, attrs in observed][:3], ["html", "head", "meta"])

    def test_nested_documents_are_rejected_before_replacing_output(self):
        builder.build(self.manifest, self.output)
        original = self.output.read_bytes()
        self.source.write_text('''<html><head></head><body>
        <iframe srcdoc="&lt;img src='https://example.invalid/a.png'&gt;"></iframe>
        </body></html>''', encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output, force=True)
        self.assertEqual(original, self.output.read_bytes())

    def test_existing_output_is_preserved_and_force_is_explicit(self):
        builder.build(self.manifest, self.output)
        original = self.output.read_bytes()
        self.data["project"] = "新项目"
        self.save()
        with self.assertRaises(FileExistsError):
            builder.build(self.manifest, self.output)
        self.assertEqual(original, self.output.read_bytes())
        builder.build(self.manifest, self.output, force=True)
        self.assertNotEqual(original, self.output.read_bytes())

    def test_invalid_resource_keeps_prior_output_even_with_force(self):
        builder.build(self.manifest, self.output)
        original = self.output.read_bytes()
        self.source.write_text('<html><head></head><body><img src="missing.png"></body></html>', encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output, force=True)
        self.assertEqual(original, self.output.read_bytes())

    def test_duplicate_identifier_and_invalid_colors(self):
        self.data["candidates"].append(self.data["candidates"][0].copy())
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)
        self.data["candidates"].pop()
        self.data["candidates"][0]["palette"] = ["url(example)"]
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_text_and_preserved_script_are_not_css_resources(self):
        self.source.write_text('''<html><head><style>
        /* @import "unused.css"; */
        p::after {content: "example url(example.png) @import"}
        </style></head><body><p>Explain @import and url(example.png)</p>
        <script>const example = "url(unused.png)";</script></body></html>''', encoding="utf-8")
        builder.build(self.manifest, self.output)
        self.assertTrue(self.output.is_file())

    def test_css_sources_are_checked_in_styles_and_inline_attributes(self):
        fragments = [
            '<style>.hero{background:image-set("https://example.invalid/a.png" 1x)}</style>',
            '<style>.hero{background:-webkit-image-set("missing.png" 1x)}</style>',
            '<style>.hero{background:u\\72l(missing.png)}</style>',
            '<style>@import "missing.css";</style>',
        ]
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.source.write_text(f'<html><head>{fragment}</head><body>content</body></html>', encoding="utf-8")
                with self.assertRaises(ValueError):
                    builder.build(self.manifest, self.output)
        self.source.write_text('<html><head></head><body style="background:url(missing.png)">content</body></html>', encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)

    def test_source_escape_and_overwriting_inputs_are_rejected(self):
        self.data["candidates"][0]["source"] = "../outside.html"
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)
        self.data["candidates"][0]["source"] = "sample.html"
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.source, force=True)
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.manifest, force=True)

    def test_static_image_embedded_and_content_changes_identity(self):
        image = self.folder / "preview.png"
        image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j7ioAAAAASUVORK5CYII='))
        self.data["candidates"][0].update(kind="image", source="preview.png")
        self.save()
        first = builder.build(self.manifest, self.output)
        self.assertIn("data:image/png;base64,", self.output.read_text(encoding="utf-8"))
        self.data["round"] = "02"
        self.save()
        second = builder.build(self.manifest, self.output, force=True)
        self.assertNotEqual(first["fingerprint"], second["fingerprint"])

    def test_relative_local_assets_are_embedded(self):
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
        (self.folder / "pages" / "img").mkdir(parents=True)
        (self.folder / "pages" / "img" / "dot.png").write_bytes(png)
        (self.folder / "pages" / "a.html").write_text('<!doctype html><html><head><style>.x{background:url("img/dot.png")}</style></head><body><img src="img/dot.png" alt=""></body></html>', encoding="utf-8")
        self.data["candidates"][0]["source"] = "pages/a.html"
        self.save()
        builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        self.assertNotIn("img/dot.png", page)
        self.assertIn("data:image/png;base64,", page)

    def test_local_assets_outside_the_manifest_folder_stay_rejected(self):
        outside = Path(self.tmp.name).parent / f"{Path(self.tmp.name).name}-outside.png"
        outside.write_bytes(b"\x89PNG\r\n\x1a\n")
        self.addCleanup(outside.unlink)
        self.source.write_text(f'<!doctype html><html><head></head><body><img src="../{outside.name}" alt=""><img src="https://example.com/a.png" alt=""></body></html>', encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)

    def test_live_candidates_accept_only_local_dev_servers(self):
        self.data["candidates"].append({"id": "live", "name": "现状", "concept": "当前版本", "typography": "系统字体", "palette": ["#fff"], "traits": ["现有页面"], "kind": "url", "url": "http://localhost:5173/orders", "baseline": True})
        self.save()
        builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        payload = json.loads(page.split("const DATA = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual([c["id"] for c in payload["candidates"]], ["live", "a"])
        for url in ("https://example.com/", "file:///etc/passwd", "http://user:pw@localhost:3000/"):
            self.data["candidates"][1]["url"] = url
            self.save()
            with self.assertRaises(ValueError):
                builder.build(self.manifest, self.output, force=True)

    def test_serve_accepts_command_and_optional_absolute_cwd_and_local_url(self):
        for serve in (
            {"command": "pnpm dev"},
            {"command": "pnpm dev", "cwd": str(self.folder)},
            {"command": "pnpm dev", "cwd": str(self.folder), "url": "http://localhost:3456"},
            {"command": "pnpm dev", "url": "https://127.0.0.1:3456/"},
            {"command": "pnpm dev", "url": "http://[::1]:3456/"},
        ):
            with self.subTest(serve=serve):
                self.data["serve"] = serve
                self.save()
                builder.build(self.manifest, self.output, force=True)
                page = self.output.read_text(encoding="utf-8")
                payload = json.loads(page.split("const DATA = ", 1)[1].split(";\n", 1)[0])
                self.assertEqual(payload["serve"], serve)

    def test_serve_requires_a_nonempty_string_command(self):
        for serve in ({}, {"command": ""}, {"command": "  "}, {"command": 123}, {"command": None}):
            with self.subTest(serve=serve):
                self.data["serve"] = serve
                self.save()
                with self.assertRaisesRegex(ValueError, "serve.command 必须是非空字符串"):
                    builder.build(self.manifest, self.output)
        for serve in (None, [], "pnpm dev"):
            with self.subTest(serve=serve):
                self.data["serve"] = serve
                self.save()
                with self.assertRaisesRegex(ValueError, "serve 必须是对象"):
                    builder.build(self.manifest, self.output)
        self.assertFalse(self.output.exists())

    def test_serve_cwd_must_be_an_absolute_path(self):
        for cwd in ("project", "./project", "~/project", "", None, 123):
            with self.subTest(cwd=cwd):
                self.data["serve"] = {"command": "pnpm dev", "cwd": cwd}
                self.save()
                with self.assertRaisesRegex(ValueError, "serve.cwd 必须是绝对路径"):
                    builder.build(self.manifest, self.output)

    def test_serve_url_must_be_local_http_or_https(self):
        for url in ("https://example.com/", "file:///tmp/index.html", "ftp://localhost/", "http://user:pw@localhost:3456/", "http://localhost:bad/", "http://[::1", "", None, 123):
            with self.subTest(url=url):
                self.data["serve"] = {"command": "pnpm dev", "url": url}
                self.save()
                with self.assertRaisesRegex(ValueError, "serve.*url.*本机"):
                    builder.build(self.manifest, self.output)

    def test_serve_is_embedded_unchanged_without_script_escape(self):
        serve = {"command": "  printf '</script><script>window.injected=true</script>'\u2028\u2029  ", "cwd": str(self.folder / 'a"$`\\b'), "url": "http://localhost:3456", "note": "保留额外元数据"}
        self.data["serve"] = serve
        self.save()
        builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        payload = json.loads(page.split("const DATA = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(payload["serve"], serve)
        self.assertNotIn(serve["command"], page)
        self.assertIn('\\u003c/script>', page)
        self.assertIn('\\u2028\\u2029', page)

    def test_url_candidates_without_serve_warn_but_still_build(self):
        self.data["candidates"][0].update(kind="url", url="http://localhost:3456/")
        self.save()
        messages = io.StringIO()
        with redirect_stderr(messages):
            builder.build(self.manifest, self.output)
        self.assertTrue(self.output.is_file())
        self.assertEqual(len(messages.getvalue().splitlines()), 1)
        self.assertIn("建议在 manifest 顶层补上 serve", messages.getvalue())
        self.data["serve"] = {"command": "pnpm dev"}
        self.save()
        messages = io.StringIO()
        with redirect_stderr(messages):
            builder.build(self.manifest, self.output, force=True)
        self.assertEqual(messages.getvalue(), "")

    def test_shell_connections_allow_only_this_rounds_candidate_origins(self):
        self.data["serve"] = {"command": "pnpm dev", "url": "http://localhost:9999/"}
        urls = ["http://localhost:3456/a?note=\"<script>", "http://localhost:3456/b", "https://127.0.0.1:4443/", "http://[::1]:5173/"]
        self.data["candidates"] = [dict(self.data["candidates"][0], id=f"live{i}", kind="url", url=url) for i, url in enumerate(urls)]
        self.save()
        builder.build(self.manifest, self.output)
        policies = []
        class Policies(HTMLParser):
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy":
                    policies.append(attrs["content"])
        Policies().feed(self.output.read_text(encoding="utf-8"))
        self.assertEqual(policies, ["connect-src http://localhost:3456 http://localhost:5173 https://127.0.0.1:4443"])
        self.data["candidates"] = [dict(self.data["candidates"][0], kind="html")]
        self.save()
        builder.build(self.manifest, self.output, force=True)
        self.assertIn('content="connect-src \'none\'"', self.output.read_text(encoding="utf-8"))

    def test_interactive_html_runs_inline_scripts_only_when_asked(self):
        self.assertIn("script-src 'none'", builder.prepare_html(self.source))
        csp = builder.prepare_html(self.source, interactive=True)
        self.assertIn("script-src 'unsafe-inline'", csp)
        self.assertIn("localStorage", csp)
        self.assertNotIn("localStorage", builder.prepare_html(self.source))
        self.assertIn("default-src 'none'", csp)
        self.data["candidates"][0]["interactive"] = True
        self.save()
        builder.build(self.manifest, self.output)
        self.source.write_text('<html><head><script src="https://example.invalid/a.js"></script></head><body></body></html>', encoding="utf-8")
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output, force=True)
        self.data["candidates"][0].update(kind="image", interactive=True)
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output, force=True)

    def test_local_stylesheets_and_scripts_are_inlined(self):
        (self.folder / "vendor").mkdir()
        (self.folder / "vendor" / "lib.js").write_text("window.lib='</script>'", encoding="utf-8")
        (self.folder / "app.css").write_text("body{color:#123}", encoding="utf-8")
        self.source.write_text('<!doctype html><html><head><link rel="stylesheet" href="app.css">'
                               '<script defer src="vendor/lib.js"></script></head><body><p>内容</p></body></html>', encoding="utf-8")
        static = builder.prepare_html(self.source, root=self.folder)
        self.assertIn("<style>body{color:#123}</style>", static)
        self.assertNotIn("lib.js", static)
        self.assertNotIn("window.lib", static)
        live = builder.prepare_html(self.source, interactive=True, root=self.folder)
        self.assertIn("'unsafe-eval'", live)
        self.assertLess(live.index("<p>内容</p>"), live.index("window.lib"))
        self.assertIn("<\\/script>", live)
        self.data["candidates"][0]["interactive"] = True
        self.save()
        builder.build(self.manifest, self.output)

    def test_only_one_baseline(self):
        second = dict(self.data["candidates"][0], id="b", baseline=True)
        self.data["candidates"][0]["baseline"] = True
        self.data["candidates"].append(second)
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.manifest, self.output)

    def test_template_keeps_documented_comparison_features(self):
        builder.build(self.manifest, self.output)
        page = self.output.read_text(encoding="utf-8")
        hooks = {
            "并排与单张": 'data-layout="loupe"',
            "手机视口": 'data-viewport="mobile"',
            "筛选": 'id="filter-list"',
            "设计说明开关": 'id="notes-toggle"',
            "实际尺寸": '实际尺寸 100%',
            "选择": "st.chosen",
            "备注": 'id="notes"',
            "选择即复制": 'navigator.clipboard',
            "本地地址候选": "c.kind==='url'",
            "服务未运行提示": "开发服务器没有运行",
            "复制启动命令": "button.dataset.copyServe",
            "现状基线": "c.baseline",
            "可操作小样": "c.interactive",
            "按轮次保存": "DATA.fingerprint",
            "存储不可用提示": "浏览器存储不可用",
            "展示北极星": "c.concept",
            "展示色板": "c.palette",
        }
        missing = [name for name, hook in hooks.items() if hook not in page]
        self.assertEqual(missing, [], "模板缺少对比页承诺的功能，见 .github/EXPLORER.md")

    def test_copied_skill_works_from_another_directory(self):
        copy = self.folder / "relocated"
        shutil.copytree(ROOT / "scripts", copy / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "assets", copy / "assets")
        run = subprocess.run([sys.executable, str(copy / "scripts" / "build_explorer.py"), str(self.manifest), "--output", str(self.output)], cwd=self.folder, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(self.output.is_file())


if __name__ == "__main__":
    unittest.main()
