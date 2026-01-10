# High Quality Commit - Examples

このドキュメントでは、実際の開発シナリオでの具体的な使用例を示します。

## 例1: 初回実装でのgitコミット

### シナリオ

新機能「ユーザープロフィール編集」を実装し、初めてgit commitする

### 手順

```bash
# 1. ブランチ状況確認
git status
# On branch feature/user-profile-edit
# Changes not staged for commit:
#   modified:   src/components/UserProfile.tsx
#   modified:   src/api/user.ts
#   new file:   src/components/ProfileEditForm.tsx

git log --oneline --graph origin/main..HEAD
# (no commits yet on this branch)

# 2. 戦略判断: ブランチに初めてのgitコミット → 新規gitコミット

# 3. git commit実行
git add -A
git commit
```

### gitコミットメッセージ

```
feat: add user profile editing feature

Implement profile editing functionality:
- Add ProfileEditForm component with validation
- Add PUT /api/users/:id endpoint
- Integrate form with existing UserProfile component

Users can now update their display name, email, and bio.

Closes #234
```

## 例2: レビュー指摘への対応（Squash）

### シナリオ

PR作成後、レビューで「バリデーションロジックを改善してください」という指摘を受けた

### 手順

```bash
# 1. 現在のコミット確認
git log --oneline --graph origin/main..HEAD
# * a1b2c3d feat: add user profile editing feature

# 2. 指摘箇所を修正
# src/components/ProfileEditForm.tsx を編集...

# 3. 戦略判断: 既存コミットと同じテーマ → Squash

# 4. 既存コミットに統合
git add -A
git commit --amend
```

### 更新されたコミットメッセージ

```
feat: add user profile editing feature

Implement profile editing functionality:
- Add ProfileEditForm component with enhanced validation
- Add PUT /api/users/:id endpoint
- Integrate form with existing UserProfile component

Validation improvements:
- Email format validation with regex
- Display name length constraints (3-50 chars)
- Real-time validation feedback

Users can now update their display name, email, and bio.

Closes #234
```

```bash
# 6. 強制push（PRを更新）
git push --force-with-lease
```

## 例3: 独立した機能追加（新規コミット）

### シナリオ

ユーザープロフィール編集機能の実装後、別途「プロフィール画像アップロード」機能を追加することになった

### 手順

```bash
# 1. 現在のコミット確認
git log --oneline --graph origin/main..HEAD
# * a1b2c3d feat: add user profile editing feature

# 2. プロフィール画像アップロード機能を実装
# ...

# 3. 戦略判断: 既存コミットとは独立した機能 → 新規コミット

# 4. 新規コミット作成
git add -A
git commit
```

### gitコミットメッセージ

```
feat: add profile picture upload

Implement profile picture upload functionality:
- Add image upload component with drag-and-drop
- Add POST /api/users/:id/avatar endpoint
- Add image cropping and preview
- Store images in cloud storage

Supports JPEG, PNG, and WebP formats up to 5MB.

Closes #235
```

```bash
# 5. 結果確認
git log --oneline --graph origin/main..HEAD
# * e4f5g6h feat: add profile picture upload
# * a1b2c3d feat: add user profile editing feature
```

## 例4: WIPコミットの整理（Interactive Rebase）

### シナリオ

開発中に多数の小さなコミットを作成してしまった。PR作成前に整理したい。

### 現状のコミット履歴

```bash
git log --oneline --graph origin/main..HEAD
# * h7i8j9k WIP: fix typo
# * e4f5g6h WIP: add validation
# * b2c3d4e feat: add profile form
# * y9z0a1b WIP: experiment with layout
# * v6w7x8y feat: add user model
# * s3t4u5v fix: import statement
```

### 手順

```bash
# 1. Interactive rebaseを開始
git rebase -i origin/main

# 2. エディタが開く
```

### エディタでの編集

変更前：
```
pick v6w7x8y feat: add user model
pick s3t4u5v fix: import statement
pick y9z0a1b WIP: experiment with layout
pick b2c3d4e feat: add profile form
pick e4f5g6h WIP: add validation
pick h7i8j9k WIP: fix typo
```

変更後：
```
pick v6w7x8y feat: add user model
squash s3t4u5v fix: import statement
drop y9z0a1b WIP: experiment with layout
pick b2c3d4e feat: add profile form
squash e4f5g6h WIP: add validation
squash h7i8j9k WIP: fix typo
```

### 保存後の編集

2つのコミットメッセージを編集：

**1つ目のコミット：**
```
feat: add user profile model

Define user profile data structure with TypeScript:
- User interface with profile fields
- Profile validation schema
- Type-safe profile operations

Includes display name, email, bio, and avatar URL.
```

**2つ目のコミット：**
```
feat: add profile editing form

Implement profile editing UI component:
- Form layout with Material-UI
- Real-time field validation
- Success/error feedback

Users can update their profile information with immediate validation.
```

### 結果確認

```bash
git log --oneline --graph origin/main..HEAD
# * m1n2o3p feat: add profile editing form
# * j4k5l6m feat: add user profile model

# クリーンな履歴に整理された！
```

## 例5: 複数機能の段階的実装

### シナリオ

大きな機能「認証システム」を、Model → API → UIの順で段階的に実装

### 手順

#### ステップ1: モデル実装

```bash
# 実装...

git add src/models/
git commit -m "feat: add authentication model

Define authentication data structures:
- User model with credentials
- JWT token interface
- Session management types

Provides type-safe authentication operations."

git push
```

#### ステップ2: API実装

```bash
# 実装...

git add src/api/auth.ts
git commit -m "feat: add authentication API endpoints

Implement authentication REST API:
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- POST /api/auth/refresh - Token refresh
- GET /api/auth/me - Get current user

Uses JWT for secure token-based authentication."

git push
```

#### ステップ3: UI実装

```bash
# 実装...

git add src/components/auth/
git commit -m "feat: add authentication UI components

Implement authentication user interface:
- LoginForm component with validation
- Protected route wrapper
- Session persistence
- Auto token refresh

Provides complete authentication UX."

git push
```

### 最終的な履歴

```bash
git log --oneline --graph origin/main..HEAD
# * q5r6s7t feat: add authentication UI components
# * n2o3p4q feat: add authentication API endpoints
# * k8l9m0n feat: add authentication model

# 各コミットが独立してレビュー可能
# 各コミットが単独でビルド・テスト可能
```

## 例6: バグ修正とテスト追加

### シナリオ

バグを発見し、修正とテストを同時に実施

### 手順

```bash
# 1. 現在の作業を確認
git status
# On branch fix/validation-bug

# 2. バグ修正とテスト追加
# src/utils/validation.ts を修正
# src/utils/validation.test.ts を追加

# 3. コミット
git add -A
git commit
```

### gitコミットメッセージ

```
fix: correct email validation regex

Fix email validation to properly handle plus signs (+) in addresses.
Previously, emails like "user+tag@example.com" were incorrectly rejected.

Changes:
- Update regex pattern to include + character
- Add comprehensive test cases for edge cases

Closes #456
```

## まとめ

これらの例から学べる重要なポイント：

1. **適切な戦略選択**: シナリオに応じてSquash/新規gitコミット/Rebaseを使い分け
2. **明確なメッセージ**: 「なぜ」その変更が必要だったのかを記述
3. **論理的な単位**: 各gitコミットが独立して理解できる粒度
4. **継続的な改善**: レビューフィードバックを反映して品質向上

これらの原則に従うことで、チーム全体の生産性が向上します。
