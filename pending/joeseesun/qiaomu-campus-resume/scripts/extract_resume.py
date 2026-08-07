#!/usr/bin/env python3
"""Extract local resume text without sending personal data to external services."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


MAX_BYTES = 25 * 1024 * 1024


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        try:
            xml = archive.read("word/document.xml")
        except KeyError as exc:
            raise ValueError("DOCX 中缺少 word/document.xml") from exc
    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
        chunks = [node.text or "" for node in paragraph.iter(f"{namespace}t")]
        text = "".join(chunks).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def extract_pdf(path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        with tempfile.TemporaryDirectory(prefix="qiaomu-resume-") as temp_dir:
            target = Path(temp_dir) / "resume.txt"
            completed = subprocess.run(
                [pdftotext, "-layout", str(path), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "pdftotext 提取失败")
            return target.read_text(encoding="utf-8", errors="replace")

    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError("未找到 pdftotext 或 pypdf，无法读取 PDF") from exc
    reader = PdfReader(str(path))
    return "\n\n".join((page.extract_text() or "") for page in reader.pages)


def extract(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown", ".csv"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".docx":
        return extract_docx(path)
    if suffix == ".pdf":
        return extract_pdf(path)
    raise ValueError(f"暂不支持 {suffix or '无扩展名'}；请提供 PDF、DOCX、TXT 或 Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description="从本地简历提取文本，不调用外部服务。")
    parser.add_argument("input", help="PDF、DOCX、TXT 或 Markdown 文件")
    parser.add_argument("--output", "-o", required=True, help="UTF-8 文本输出路径")
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    if not source.is_file():
        parser.error(f"输入文件不存在：{source}")
    if source.stat().st_size > MAX_BYTES:
        parser.error("文件超过 25 MB；请先确认文件是否包含无关图片或附件")

    try:
        text = extract(source).strip()
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"提取失败：{exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if len(text) < 20:
        print(
            "提取到的文本过少，文件可能是扫描件。请先征得用户同意后使用本地 OCR，"
            "不要静默上传到在线 OCR 服务。",
            file=sys.stderr,
        )
        raise SystemExit(3)

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8")
    print(f"已提取 {len(text)} 个字符到 {output}")


if __name__ == "__main__":
    main()
