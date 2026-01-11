---
name: setup-dev-env
description: 開発環境セットアップスキル（依存関係インストール、DB初期化、環境変数設定）
---

# Setup Dev Env Skill - 開発環境セットアップスキル

## 役割

開発環境のセットアップを自動化するスキルです。依存関係のインストール、データベース初期化、環境変数設定を行います。

## 実行フロー

### Phase 1: 環境確認
```bash
# Java バージョン確認
java -version

# Node.js バージョン確認
node -version

# pnpm インストール確認
pnpm -version

# Docker 確認
docker --version
docker-compose --version
```

### Phase 2: Backend セットアップ（target="backend"/"both"時）
```bash
cd backend

# Gradle Wrapper 実行権限付与
chmod +x gradlew

# 依存関係ダウンロード
./gradlew build -x test
```

### Phase 3: Frontend セットアップ（target="frontend"/"both"時）
```bash
cd frontend

# 依存関係インストール
pnpm install
```

### Phase 4: Database セットアップ（target="db"/"both"時）
```bash
# Docker Compose でPostgreSQL起動
docker-compose up -d db

# DBの起動待機
sleep 10

# Flywayマイグレーション実行
cd backend
./gradlew flywayMigrate
```

### Phase 5: 環境変数設定確認
```bash
# Backend .env確認
ls backend/.env

# Frontend .env.local確認
ls frontend/.env.local
```

### Phase 6: セットアップ検証
```bash
# Backend ビルド確認
cd backend
./gradlew build -x test

# Frontend ビルド確認
cd frontend
pnpm run build
```

### Phase 7: 完了報告
```markdown
## Setup Dev Env 完了報告

### Backend
- ✅ Java 21 確認済み
- ✅ Gradle依存関係インストール完了
- ✅ ビルド成功

### Frontend
- ✅ Node.js 20+ 確認済み
- ✅ pnpm依存関係インストール完了
- ✅ ビルド成功

### Database
- ✅ PostgreSQL起動完了
- ✅ Flywayマイグレーション完了

### 環境変数
- ✅ backend/.env 確認済み
- ✅ frontend/.env.local 確認済み

### 次のステップ
開発サーバーを起動できます:
- Backend: `cd backend && ./gradlew bootRun`
- Frontend: `cd frontend && pnpm dev`
```
