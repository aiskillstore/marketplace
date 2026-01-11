---
name: check-migration
description: Flywayマイグレーションチェックスキル - マイグレーションファイルの検証、バージョン番号の競合チェック、命名規則チェック、SQL構文チェックを実施します。mainブランチとの競合確認も行い、マイグレーションの品質を保証します。
---

# Check Migration Skill - Flywayマイグレーションチェックスキル

## 役割

Flywayマイグレーションファイルの検証を行うスキルです。バージョン番号の競合チェック、命名規則チェック、SQL構文チェックを実施します。

## 実行フロー

### Phase 1: マイグレーションファイル一覧取得
```bash
# マイグレーションファイル一覧
ls -l backend/src/main/resources/db/migration/

# バージョン番号抽出
ls backend/src/main/resources/db/migration/ | grep -E "^V[0-9]+__.*\.sql$"
```

### Phase 2: バージョン番号チェック
1. バージョン番号の連続性確認
2. 重複チェック
3. 欠番チェック

### Phase 3: 命名規則チェック
- 形式: `V{連番}__{説明}.sql`
- 例: `V001__create_users_table.sql`

### Phase 4: mainブランチとの競合チェック
```bash
# mainブランチの最新マイグレーションファイル取得
git fetch origin
git diff origin/main...HEAD --name-only | grep "db/migration"

# 競合するバージョン番号がないか確認
```

### Phase 5: SQL構文チェック（簡易）
- CREATE TABLE の存在確認
- IF NOT EXISTS の使用確認（冪等性）

### Phase 6: 完了報告
```markdown
## Check Migration 完了報告

### マイグレーションファイル
- 総数: [数] ファイル
- 最新バージョン: V[番号]

### チェック結果
- ✅ バージョン番号: 連続性OK、重複なし
- ✅ 命名規則: 準拠
- ✅ mainブランチとの競合: なし
- ✅ 冪等性: IF NOT EXISTS使用

### 次のステップ
マイグレーションファイルは問題ありません。
```
