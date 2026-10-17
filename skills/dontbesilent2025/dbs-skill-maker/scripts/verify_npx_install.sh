#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "用法：$0 <owner/repo-or-local-path> <skill-name> <source-skill-directory>" >&2
  exit 2
fi

source_locator="$1"
skill_name="$2"
source_skill_directory="$3"
skill_maker_npx="${SKILL_MAKER_NPX:-npx}"
temporary_root="$(mktemp -d)"
temporary_home="$temporary_root/home"

if [[ ! "$skill_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "安装验证失败：Skill 名称格式无效" >&2
  exit 2
fi

if [[ ! -f "$source_skill_directory/SKILL.md" ]]; then
  echo "安装验证失败：源目录缺少 SKILL.md" >&2
  exit 2
fi

if find "$source_skill_directory" -type l -print -quit | grep -q .; then
  echo "安装验证失败：源 Skill 包含软链接" >&2
  exit 2
fi

cleanup() {
  rm -rf "$temporary_root"
}
trap cleanup EXIT

mkdir -p "$temporary_home"

HOME="$temporary_home" "$skill_maker_npx" -y skills add "$source_locator" -g --all

installed_skill=""
while IFS= read -r candidate; do
  installed_skill="$candidate"
  break
done < <(find "$temporary_home" -type f -path "*/skills/$skill_name/SKILL.md" -print)

if [[ -z "$installed_skill" ]]; then
  echo "安装验证失败：未找到 $skill_name/SKILL.md" >&2
  exit 1
fi

if ! grep -Eq "^name:[[:space:]]*['\"]?$skill_name['\"]?[[:space:]]*$" "$installed_skill"; then
  echo "安装验证失败：frontmatter name 与 $skill_name 不一致" >&2
  exit 1
fi

installed_root="$(dirname "$installed_skill")"
checked_count=0
for entry in SKILL.md agents references scripts assets; do
  source_entry="$source_skill_directory/$entry"
  [[ -e "$source_entry" ]] || continue
  if [[ -f "$source_entry" ]]; then
    source_files=("$source_entry")
  else
    source_files=()
    while IFS= read -r source_file; do
      source_files+=("$source_file")
    done < <(find "$source_entry" -type f ! -name '.DS_Store' ! -name '*.pyc' -print)
  fi
  for source_file in "${source_files[@]}"; do
    relative_path="${source_file#"$source_skill_directory/"}"
    installed_file="$installed_root/$relative_path"
    if [[ ! -f "$installed_file" ]]; then
      echo "安装验证失败：缺少资源 $relative_path" >&2
      exit 1
    fi
    if ! cmp -s "$source_file" "$installed_file"; then
      echo "安装验证失败：资源内容不一致 $relative_path" >&2
      exit 1
    fi
    checked_count=$((checked_count + 1))
  done
done

echo "安装验证通过：${installed_skill}（已核对 ${checked_count} 个文件）"
