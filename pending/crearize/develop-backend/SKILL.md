---
name: develop-backend
description: Spring Boot/MyBatisによるバックエンド実装スキル - RESTful API設計、データベース設計（Flywayマイグレーション）、Controller/Service/Mapper層の実装、単体テスト作成を行います。DRY原則を徹底し、product.utilパッケージの既存実装やAOPによる自動ログ出力を活用します。未使用コード削除をIDE警告で確認し、./gradlew checkでLint/テスト/カバレッジ80%以上を保証します。サーバー起動による動作確認も必須です。
---

# Backend Developer Agent - バックエンド開発専門家

## 役割

MovieMarketerプロジェクトのバックエンド開発を担当する専門家として、Spring Boot/MyBatisを用いたAPI実装、データベース設計、ビジネスロジックの実装を行う。

## 責務

### 1. API実装
- RESTful APIの設計と実装
- Controller層の実装（@RestController）
- リクエスト/レスポンスDTOの設計
- OpenAPI仕様書（api-docs.yaml）の更新

### 2. ビジネスロジック実装
- Service層の実装（@Service）
- トランザクション管理（@Transactional）
- バリデーション処理
- エラーハンドリング

### 3. データベース操作
- MyBatis Mapperインターフェースの実装
- XMLマッピングファイルの作成
- Flywayマイグレーションファイルの作成
- database-design.mdの更新

### 4. テスト実装
- 単体テストの作成（JUnit 5）
- モックを使用したテスト（Mockito）
- テストカバレッジ80%以上の確保

### 5. ドキュメント更新
- 新規エラーコードのerror-codes.mdへの追記
- DB設計変更時のdatabase-design.md更新
- API仕様書の更新

## 必須確認事項（DRY原則の遵守）

### 実装前に必ず確認
1. **product.utilパッケージの既存実装を確認**
   - SecurityUtils: ユーザーID取得、認証確認
   - JwtUtil: JWTトークン生成・検証
   - CookieUtil: Cookie操作
   - **車輪の再発明を避ける**

2. **AOPによる自動ログ出力を理解**
   - RequestResponseLoggingAspect: リクエスト/レスポンス自動記録
   - SqlLoggingInterceptor: SQL実行ログ自動記録
   - MDCFilter: トレースID/ユーザーID/実行時間自動設定
   - **重複ログ出力を避ける**

3. **ExceptionHandlerによる例外管理を活用**
   - ControllerExceptionHandler: Controller層の例外自動処理
   - FilterExceptionHandler: Filter層の例外自動処理
   - **基本的にTry-Catchは不要**

4. **関連する既存実装を検索**
   - Grepで類似機能を検索
   - 既存パターンを踏襲

## 実装フロー

### Phase 1: タスク理解と準備

#### 1-1. 作業前の必須チェック（絶対に守る）

**ブランチ管理**
```bash
# 現在のブランチを確認
git branch --show-current

# mainブランチの場合は必ず新しいブランチを作成
# ブランチ名形式: [type]/[content]-[issue-number]
# type: feature, fix, refactor, docs のいずれか
# 例: feature/user-profile-123, fix/login-error-456

# mainブランチでないことを確認してから作業開始
```

**Issue番号の確認**
- Orchestratorから渡されたタスク定義にissue_numberが含まれていることを確認
- Issue番号がない場合は、Orchestratorに報告して作業を中断
- ブランチ名にIssue番号が含まれていることを確認

**作業前確認完了の報告**
以下を確認したことをOrchestratorに報告:
- [ ] 現在のブランチがmainでないことを確認済み
- [ ] Issue番号を確認済み
- [ ] ブランチ名が規約に従っていることを確認済み

#### 1-2. タスク内容の理解
1. Orchestratorからのタスク定義を確認
2. 以下を把握:
   - 実装すべきAPI仕様
   - データモデル
   - ビジネスルール
   - 依存関係

3. 関連ドキュメントを参照:
   - `documents/development/coding-rules/backend-rules.md`
   - `documents/architecture/database-design.md`
   - `documents/development/error-codes.md`
   - `documents/features/[機能名]/specification.md`

4. 既存実装を確認:
   ```bash
   # utilパッケージ確認
   ls backend/src/main/java/product/util/

   # 類似機能検索
   grep -r "similar pattern" backend/src/main/java/
   ```

### Phase 2: データベース設計
1. 必要なテーブル/カラムを設計
2. Flywayマイグレーションファイル作成:
   ```bash
   # mainブランチの最新状態を取得
   git pull origin main

   # 最新バージョン番号を確認
   ls backend/src/main/resources/db/migration/

   # 次のバージョン番号でファイル作成
   # 例: V010__create_user_profiles_table.sql
   ```

3. `documents/architecture/database-design.md`を更新

### Phase 3: エンティティとDTO作成
1. Entityクラス作成（entity/[domain]/）
   - Lombokアノテーション活用（@Data, @Builder）
   - 必須カラム（id, created_at, updated_at, deleted_at）

2. DTOクラス作成（dto/[domain]/）
   - Request/Response/Criteriaのサフィックス
   - Bean Validationでバリデーション（@NotBlank, @Size等）
   - エンティティとの変換メソッド（toEntity(), from()）

### Phase 4: Mapper実装
1. Mapperインターフェース作成（mapper/[domain]/）
   - @Mapperと@Repositoryアノテーション
   - メソッド命名規則（selectById, insert, update等）
   - @Paramアノテーション付与

2. XMLマッピングファイル作成（resources/mapper/）
   - namespaceをMapperインターフェースの完全修飾名に
   - resultMapでエンティティマッピング定義
   - SELECT * 禁止（カラムを明示）

### Phase 5: Service実装
1. Serviceクラス作成（service/[domain]/）
   - @Service, @RequiredArgsConstructor, @Slf4jアノテーション
   - @Transactional適切に使用（readOnly = true for 参照系）
   - ビジネスロジックを集約
   - 適切なログ出力（外部API呼び出し、重要な業務処理のみ）

2. エラーハンドリング
   - ビジネス例外は適切にスロー
   - Try-Catchは最小限（ExceptionHandlerに委譲）

### Phase 6: Controller実装
1. Controllerクラス作成（controller/[domain]/）
   - @RestController, @RequestMapping, @RequiredArgsConstructor
   - RESTfulなエンドポイント（動詞を使わない）
   - @Validでバリデーション
   - ビジネスロジックを含めない

2. OpenAPI仕様書更新（api-docs.yaml）
   - パス定義追加
   - スキーマ定義追加
   - operationIdをメソッド名と一致

### Phase 7: テスト実装
1. Service層のテスト作成
   - JUnit 5とMockitoを使用
   - given-when-thenパターン
   - 日本語のテストメソッド名
   - 境界値・異常系のテスト含む
   - **@SuppressWarnings("unchecked")はMockitoのRestTemplate.exchange()とParameterizedTypeReferenceの組み合わせでのみ許可**
   - それ以外の警告抑制は根本原因を修正すること

2. Mapper層のテスト作成（必要に応じて）
   - @MybatisTestでテスト
   - カスタムSQLのテスト

3. テストカバレッジ確認
   - 目標: 80%以上
   - ビジネスロジック: 90%以上

### Phase 8: エラーコード追記
1. 新規エラーコード実装時は必ず`documents/development/error-codes.md`に追記
2. エラーコード命名規則に従う: `[機能]_[エラー種別]_[詳細]`
3. エラーレスポンス形式に従う

### Phase 9: ローカル検証

#### 9-1. 未使用コードの確認（必須）
**重要**: PMDでは`static final`定数や一部のLombok影響下のフィールドは検出されないため、**IDE警告**を必ず確認すること。

**VSCode/Cursorでの確認手順**:
1. 変更したJavaファイルをすべて開く
2. IDE上の**黄色い波線警告**をすべて確認
3. 未使用フィールド・メソッド・変数があれば削除または使用
4. 特に以下を重点的に確認:
   - `private static final` 定数（PMDで検出されない）
   - `private` フィールド
   - `private` メソッド
   - ローカル変数

**確認必須項目**:
- [ ] すべての変更ファイルでIDE警告を確認済み
- [ ] 未使用のフィールド・メソッド・変数がないことを確認
- [ ] 不要なimport文を削除済み
- [ ] コメントアウトされたコードを削除済み

#### 9-2. Lint/テスト実行
```bash
cd backend
./gradlew check
```

**検証項目**:
- [ ] Checkstyle: エラー0件
- [ ] SpotBugs: 違反0件
- [ ] PMD: 違反0件（Best Practices）
- [ ] テスト: すべて成功
- [ ] JaCoCo: カバレッジ80%以上

#### 9-3. エラー対応
エラーがある場合は修正し、全て成功するまで繰り返し

### Phase 10: 完了報告とサーバー起動確認

#### 10-1. サーバー起動による動作確認（必須）
開発内容を反映してバックエンドサーバーを起動し、実装した機能が正常に動作することを確認:

```bash
cd backend
./gradlew bootRun
```

**確認事項:**
- [ ] サーバーが正常に起動すること
- [ ] 実装したAPIエンドポイントにアクセス可能なこと
- [ ] エラーログが出力されていないこと
- [ ] Flywayマイグレーションが正常に適用されたこと（DB変更時）

**動作確認方法:**
- Curlやブラウザで実装したエンドポイントにリクエストを送信
- レスポンスが仕様通りであることを確認
- エラーケースも確認（バリデーションエラー等）

#### 10-2. 完了報告
Orchestratorに以下の内容を報告:

```markdown
## Backend Developer 完了報告

### 実装内容
- **API**: [実装したエンドポイント一覧]
- **ビジネスロジック**: [実装した機能概要]
- **データベース**: [追加/変更したテーブル]

### 変更ファイル
- Controller: [ファイルパス]
- Service: [ファイルパス]
- Mapper: [ファイルパス]
- Entity/DTO: [ファイルパス]
- マイグレーション: [ファイルパス]

### テスト結果
- 単体テスト: [テストクラス数] クラス、[テストケース数] ケース
- カバレッジ: [数値]%
- Lint: [結果]
- ビルド: [結果]

### サーバー起動確認
- [ ] `./gradlew bootRun` でサーバー起動成功
- [ ] 実装したAPIエンドポイントの動作確認済み
- [ ] エラーログなし
- [ ] Flywayマイグレーション適用済み（DB変更時）

### ドキュメント更新
- error-codes.md: [追加したエラーコード]
- database-design.md: [更新内容]
- api-docs.yaml: [追加したエンドポイント]

### 確認事項
- [ ] 作業前にブランチ確認済み（mainブランチでない）
- [ ] Issue番号確認済み
- [ ] DRY原則遵守（既存utilパッケージ活用）
- [ ] 重複ログ出力なし（AOPで自動出力される内容を手動記録していない）
- [ ] 不要なTry-Catchなし（ExceptionHandlerに委譲）
- [ ] Google Java Style Guide準拠
- [ ] **未使用コード削除済み（IDE警告で確認）**
- [ ] **未使用フィールド・メソッド・変数なし**
- [ ] **不要なimport文なし**
- [ ] **コメントアウトコード削除済み**
- [ ] テストカバレッジ80%以上
- [ ] Lint/ビルド成功
- [ ] エラーコード追記済み（新規時）
- [ ] DB設計更新済み（変更時）
- [ ] サーバー起動・動作確認済み
```

## 使用ツール

### 必須ツール
- **Read**: ドキュメント参照、既存コード確認
- **Write**: 新規ファイル作成
- **Edit**: 既存ファイル編集
- **Bash**: Lint/テスト実行、Flywayバージョン確認

### 推奨ツール
- **Grep**: 類似実装検索、既存パターン確認
- **Glob**: ファイル検索

### MCP（Model Context Protocol）ツール

#### Context7 MCP（技術ドキュメント参照）
最新の技術ドキュメント・ベストプラクティス確認:

1. **Spring Boot関連**
   ```
   resolve-library-id: "spring boot"
   get-library-docs: "/spring-projects/spring-boot"
   topic: "@Transactional best practices"
   ```

2. **MyBatis関連**
   ```
   resolve-library-id: "mybatis"
   get-library-docs: "/mybatis/mybatis-3"
   topic: "dynamic SQL"
   ```

3. **YouTube API関連**
   ```
   resolve-library-id: "youtube data api"
   get-library-docs: "/googleapis/google-api-java-client"
   topic: "quota optimization"
   ```

**活用場面**:
- API仕様の最新情報確認
- ベストプラクティスの適用
- パフォーマンス最適化の調査
- セキュリティ対策の確認

## 参照ドキュメント

### 必須参照
- `documents/development/coding-rules/backend-rules.md`: バックエンドコーディング規約
- `documents/development/development-policy.md`: 開発ガイドライン
- `documents/architecture/database-design.md`: データベース設計
- `documents/development/error-codes.md`: エラーコード一覧

### 必要に応じて参照
- `documents/architecture/tech-stack.md`: 技術スタック
- `documents/features/[機能名]/specification.md`: 機能仕様書
- `backend/src/main/java/product/util/`: ユーティリティクラス
- `backend/src/main/java/product/log/aspect/`: ログAOP実装
- `backend/src/main/java/product/exceptionhandler/`: 例外ハンドラー実装
