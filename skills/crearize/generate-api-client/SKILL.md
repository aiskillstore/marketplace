---
name: generate-api-client
description: Orval APIクライアント生成スキル（OpenAPI仕様書から型安全なAPIクライアントを自動生成）
---

# Generate API Client Skill - Orval APIクライアント生成スキル

## 役割

OpenAPI仕様書（api-docs.yaml）から型安全なAPIクライアントを自動生成するスキルです。

## 実行フロー

### Phase 1: 仕様書確認
```bash
# OpenAPI仕様書の存在確認
ls backend/src/main/resources/static/api-docs.yaml
```

### Phase 2: Orval実行
```bash
cd frontend

# Orvalで型安全なAPIクライアント生成
pnpm run generate:api
```

### Phase 3: 生成確認
```bash
# 生成されたファイル確認
ls frontend/src/lib/api/generated/
```

### Phase 4: 型チェック
```bash
# TypeScript型チェック
npx tsc --noEmit
```

### Phase 5: 完了報告
```markdown
## Generate API Client 完了報告

### 生成結果
- ✅ APIクライアント生成完了
- ✅ 型定義生成完了
- ✅ TypeScript型チェック成功

### 生成ファイル
- frontend/src/lib/api/generated/api.ts
- frontend/src/lib/api/generated/model.ts

### 次のステップ
生成されたAPIクライアントをimportして使用できます。
```
