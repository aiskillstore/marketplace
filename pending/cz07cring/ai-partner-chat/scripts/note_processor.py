"""
Note Processor - 自动检测和处理项目笔记

用于 Claude Code Skill，自动化处理项目 notes/ 目录中的笔记。
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# 确保可以导入 orchestrator
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import AIPartnerOrchestrator


class NoteProcessor:
    """笔记处理器 - 自动检测和处理项目笔记"""

    def __init__(self, project_root: str = "."):
        """
        初始化笔记处理器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root).resolve()
        self.notes_dir = self.project_root / 'notes'
        self.orchestrator = AIPartnerOrchestrator(project_root=str(self.project_root))

        # 状态文件：记录已处理的笔记
        self.state_file = (
            Path.home() / '.claude/skills/ai-partner-chat/data' /
            'indexes' / 'processed_notes.json'
        )
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """加载处理状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'processed': {}}

    def _save_state(self):
        """保存处理状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def scan_notes(self) -> list:
        """
        扫描 notes/ 目录，查找新的或修改的笔记

        Returns:
            需要处理的笔记列表 [(path, mtime), ...]
        """
        if not self.notes_dir.exists():
            print(f"⚠️  notes/ 目录不存在: {self.notes_dir}")
            return []

        new_or_modified = []

        for note_file in self.notes_dir.glob('**/*.md'):
            note_path = str(note_file.relative_to(self.project_root))
            mtime = note_file.stat().st_mtime

            # 检查是否需要处理
            if note_path not in self.state['processed']:
                # 新笔记
                new_or_modified.append((note_file, mtime))
            elif self.state['processed'][note_path] < mtime:
                # 修改过的笔记
                new_or_modified.append((note_file, mtime))

        return new_or_modified

    def process_note(self, note_path: Path) -> dict:
        """
        处理单个笔记

        Args:
            note_path: 笔记文件路径

        Returns:
            处理结果
        """
        content = note_path.read_text(encoding='utf-8')

        result = self.orchestrator.process_new_note(
            note_path=str(note_path),
            content=content
        )

        # 更新状态
        relative_path = str(note_path.relative_to(self.project_root))
        self.state['processed'][relative_path] = note_path.stat().st_mtime
        self._save_state()

        return result

    def process_all_new_notes(self) -> dict:
        """
        处理所有新的和修改过的笔记

        Returns:
            处理结果摘要
        """
        notes_to_process = self.scan_notes()

        if not notes_to_process:
            print("✅ 没有新笔记需要处理")
            return {
                'processed_count': 0,
                'notes': []
            }

        print(f"📝 发现 {len(notes_to_process)} 个新/修改的笔记")

        results = []
        for note_path, _ in notes_to_process:
            print(f"\n处理: {note_path.name}")
            result = self.process_note(note_path)
            results.append({
                'file': note_path.name,
                'tags': result['tags'],
                'code_blocks': result['code_blocks'],
                'chunks': result['chunks_created']
            })

        print(f"\n✅ 成功处理 {len(results)} 个笔记")

        return {
            'processed_count': len(results),
            'notes': results
        }


# 便捷函数

def check_and_process_notes(project_root: str = ".") -> dict:
    """
    检查并处理项目笔记（便捷函数）

    Args:
        project_root: 项目根目录

    Returns:
        处理结果
    """
    processor = NoteProcessor(project_root)
    return processor.process_all_new_notes()


def list_processed_notes() -> list:
    """
    列出已处理的笔记

    Returns:
        已处理笔记列表
    """
    state_file = (
        Path.home() / '.claude/skills/ai-partner-chat/data' /
        'indexes' / 'processed_notes.json'
    )

    if not state_file.exists():
        return []

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    return list(state['processed'].keys())


# 使用示例
if __name__ == "__main__":
    # 处理当前项目的笔记
    result = check_and_process_notes()

    print("\n" + "="*50)
    print("处理摘要:")
    print(f"  处理笔记数: {result['processed_count']}")
    for note in result['notes']:
        print(f"\n  📝 {note['file']}")
        print(f"     标签: {', '.join(note['tags'][:5])}")
        print(f"     代码块: {note['code_blocks']} 个")
        print(f"     Chunks: {note['chunks']} 个")
