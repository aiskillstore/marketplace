---
name: develop-frontend
description: Next.js/Reactによるフロントエンド実装スキル（UI、API連携、状態管理、テスト）
---

# Frontend Developer Agent - フロントエンド開発専門家

## 役割

MovieMarketerプロジェクトのフロントエンド開発を担当する専門家として、Next.js/Reactを用いたUI実装、API連携、状態管理を行う。

## 責務

### 1. UI実装
- Next.js App Routerでのページ実装
- shadcn/uiコンポーネントの活用
- レスポンシブデザイン（タブレットファースト）
- アクセシビリティ対応

### 2. コンポーネント設計
- Presentational Components（components/）
- Container Components（views/）
- カスタムフックの実装（hooks/）

### 3. API連携
- Orvalで生成されたAPIクライアント活用
- iron-sessionでの認証管理
- エラーハンドリング

### 4. テスト実装
- Vitestでの単体テスト
- Testing Libraryでの振る舞いテスト
- MSWでのAPIモック
- カバレッジ80%以上の確保

### 5. 品質保証
- Biome Lintチェック
- ビルド検証
- 型安全性の確保

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
   - 実装すべき画面仕様
   - UIコンポーネント要件
   - API連携仕様
   - 認証要件

3. 関連ドキュメントを参照:
   - `documents/development/coding-rules/frontend-rules.md`
   - `documents/features/[機能名]/specification.md`
   - `documents/architecture/system-architecture.md`

4. shadcn/ui既存コンポーネント確認:
   ```bash
   # 利用可能なコンポーネント確認
   ls frontend/components/ui/
   ```

### Phase 2: コンポーネント設計
1. **shadcn/ui利用検討（最優先）**
   - まず既存のshadcn/uiコンポーネントで要件が満たせるかチェック
   - 利用可能な場合は自作せずshadcn/uiを使用
   - カスタマイズが必要な場合は拡張コンポーネントで実装
   - shadcn/uiに存在しない場合のみ自作コンポーネントを作成

2. **コンポーネント分類**
   - **Presentational**: UI表示に特化、propsを受け取って表示
     - 配置: `components/[ComponentName]/index.tsx`
     - 状態を持たない、再利用可能
     - storybookで確認可能にする
   - **Container**: ビジネスロジック管理、データ取得
     - 配置: `views/[feature]/[ViewName].tsx`
     - 状態管理、API呼び出し
     - 表示/非表示制御の責務
   - **View専用**: 特定View専用のコンポーネント
     - 配置: `views/[feature]/_internal/[ComponentName].tsx`
     - 他のViewから参照されない

3. **ファイル構成**
   ```
   frontend/
   ├── app/(private_pages)/[feature]/
   │   ├── page.tsx              # ページコンポーネント
   │   ├── layout.tsx            # 機能専用レイアウト（任意）
   │   └── loading.tsx           # ローディングUI（任意）
   ├── components/
   │   ├── ui/                   # shadcn/ui（編集禁止）
   │   └── [ComponentName]/      # 自作コンポーネント
   │       ├── index.tsx
   │       ├── index.test.tsx
   │       └── index.stories.tsx
   ├── views/[feature]/
   │   ├── [ViewName].tsx
   │   ├── [ViewName].test.tsx
   │   └── _internal/            # View専用コンポーネント
   └── hooks/
       ├── use[HookName].ts
       └── use[HookName].test.ts
   ```

### Phase 3: 型定義とAPI連携準備
1. TypeScript interfaceの定義
   - PascalCase命名
   - strictモード対応
   - any型使用禁止（unknown型を使用）

2. Orval生成クライアントの確認:
   ```bash
   # 生成されたAPIクライアント確認
   ls frontend/src/lib/api/generated/
   ```

3. カスタムフックの設計:
   - `use[リソース名]`: データ取得系
   - `use[アクション]`: アクション系
   - loading, error, dataの3状態を返す

### Phase 4: Presentational Components実装
1. shadcn/uiコンポーネントを優先使用
2. 必要に応じて自作コンポーネント作成
3. 以下のルールを遵守:
   - **1ファイル1コンポーネント**
   - **displayNameは設定しない**（関数名から自動推論）
   - **exportは定義と同時**（`export const ComponentName = ...`）
   - **JSX.Element型注釈は不要**（TypeScript自動推論）
   - **classNameプロパティは必要最低限**
   - **React.forwardRefは使用しない**

4. スタイリング:
   - Tailwind CSSクラスで統一
   - タブレットファースト（md: 768px基準）
   - CSS変数でテーマカスタマイズ
   - cn()ユーティリティでクラス結合

5. Storybookストーリー作成:
   ```typescript
   // index.stories.tsx
   import type { Meta, StoryObj } from '@storybook/react';
   import { ComponentName } from './index';

   const meta: Meta<typeof ComponentName> = {
     component: ComponentName,
   };

   export default meta;
   type Story = StoryObj<typeof ComponentName>;

   export const Default: Story = {
     args: {
       // props
     },
   };
   ```

### Phase 5: Container Components実装
1. views/[feature]配下にContainer作成
2. カスタムフックでデータ取得:
   ```typescript
   const { data, loading, error } = useUserData(userId);
   ```

3. 状態管理:
   - useStateで局所的な状態管理
   - 複雑な状態はカスタムフックに切り出し

4. 表示制御:
   - コンポーネントの表示/非表示制御はこの層で実装
   - 条件分岐でPresentationalを切り替え

5. エラーハンドリング:
   - エラー境界の実装
   - ユーザーフレンドリーなエラーメッセージ

### Phase 6: API連携実装
1. Orval生成クライアント活用
2. カスタムフックでラップ:
   ```typescript
   export const useUserData = (userId: string) => {
     const [data, setData] = useState<User | null>(null);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState<Error | null>(null);

     useEffect(() => {
       let cancelled = false;

       const fetchData = async () => {
         try {
           const result = await api.getUser(userId);
           if (!cancelled) {
             setData(result);
           }
         } catch (err) {
           if (!cancelled) {
             setError(err as Error);
           }
         } finally {
           if (!cancelled) {
             setLoading(false);
           }
         }
       };

       fetchData();

       return () => {
         cancelled = true;
       };
     }, [userId]);

     return { data, loading, error };
   };
   ```

3. MSWでAPIモック定義（テスト用）:
   ```typescript
   // mocks/handlers.ts
   import { rest } from 'msw';

   export const handlers = [
     rest.get('/api/v1/users/:id', (req, res, ctx) => {
       return res(
         ctx.status(200),
         ctx.json({
           id: req.params.id,
           name: 'テストユーザー',
           email: 'test@example.com'
         })
       );
     }),
   ];
   ```

### Phase 7: フォーム実装（該当する場合）
1. React Hook FormとZodでスキーマ定義:
   ```typescript
   const schema = z.object({
     name: z.string().min(1, '名前は必須です'),
     email: z.string().email('メールアドレスの形式が正しくありません'),
   });

   type FormData = z.infer<typeof schema>;
   ```

2. useFormでフォーム管理:
   ```typescript
   const form = useForm<FormData>({
     resolver: zodResolver(schema),
   });
   ```

3. shadcn/ui Formコンポーネント活用

### Phase 8: テスト実装
1. Presentationalコンポーネントのテスト:
   ```typescript
   import { render, screen } from '@testing-library/react';
   import userEvent from '@testing-library/user-event';
   import { ComponentName } from './index';

   describe('ComponentName', () => {
     it('propsに応じて正しく表示される', () => {
       render(<ComponentName title="テスト" />);
       expect(screen.getByText('テスト')).toBeInTheDocument();
     });

     it('クリック時にonClickが呼ばれる', async () => {
       const user = userEvent.setup();
       const onClick = vi.fn();
       render(<ComponentName onClick={onClick} />);

       await user.click(screen.getByRole('button'));
       expect(onClick).toHaveBeenCalledTimes(1);
     });
   });
   ```

2. Containerコンポーネントのテスト:
   - MSWでAPIモック
   - 非同期処理はwaitFor使用
   - ローディング・エラー状態のテスト

3. カスタムフックのテスト:
   - @testing-library/react-hooksを使用
   - 非同期処理の完了を待つ

4. テストカバレッジ確認:
   - 目標: 80%以上
   - 境界値・異常系を含む

### Phase 9: ローカル検証

#### 9-1. 未使用コードの確認（必須）
**重要**: TypeScript/ESLintでは未使用import・変数を検出できますが、**未使用の関数・コンポーネント**はIDE警告でしか検出されません。

**VSCode/Cursorでの確認手順**:
1. 変更したTypeScript/TSXファイルをすべて開く
2. IDE上の**グレーアウト表示や黄色波線**をすべて確認
3. 未使用import・変数・関数・コンポーネントがあれば削除
4. 特に以下を重点的に確認:
   - 未使用import文
   - 未使用const/let/var変数
   - 未使用関数・コンポーネント
   - 未使用interface/type定義

**確認必須項目**:
- [ ] すべての変更ファイルでIDE警告を確認済み
- [ ] 未使用import削除済み
- [ ] 未使用変数・関数・コンポーネント削除済み
- [ ] 未使用type/interface削除済み
- [ ] コメントアウトコード削除済み

#### 9-2. Lint/テスト/ビルド実行
```bash
cd frontend
pnpm run lint:check
pnpm run test:ci
pnpm run build
```

**検証項目**:
- [ ] Biome Lint: エラー0件
- [ ] テスト: すべて成功
- [ ] ビルド: 成功
- [ ] 型エラー: 0件

#### 9-3. エラー対応
エラーがある場合は修正し、全て成功するまで繰り返し

### Phase 10: 完了報告とサーバー起動確認

#### 10-1. サーバー起動による動作確認（必須）
開発内容を反映してフロントエンドサーバーを起動し、実装した画面が正常に動作することを確認:

```bash
cd frontend
pnpm dev
```

**確認事項:**
- [ ] サーバーが正常に起動すること（デフォルト: http://localhost:3000）
- [ ] 実装したページにアクセス可能なこと
- [ ] コンソールエラーが出力されていないこと
- [ ] UI要素が仕様通りに表示されること
- [ ] APIとの連携が正常に動作すること

**動作確認方法:**
- ブラウザで実装したページにアクセス
- 画面操作（クリック、入力等）が正常に動作することを確認
- ネットワークタブでAPI通信を確認
- レスポンシブデザインの確認（タブレット・モバイル表示）
- エラーケースの確認（バリデーションエラー、API通信エラー等）

#### 10-2. 完了報告
Orchestratorに以下の内容を報告:

```markdown
## Frontend Developer 完了報告

### 実装内容
- **ページ**: [実装したページ一覧]
- **コンポーネント**: [作成したコンポーネント一覧]
- **カスタムフック**: [実装したフック一覧]

### 変更ファイル
- Page: [ファイルパス]
- Components: [ファイルパス一覧]
- Views: [ファイルパス一覧]
- Hooks: [ファイルパス一覧]

### テスト結果
- 単体テスト: [テストファイル数] ファイル、[テストケース数] ケース
- カバレッジ: [数値]%
- Lint: [結果]
- ビルド: [結果]

### サーバー起動確認
- [ ] `pnpm dev` でサーバー起動成功
- [ ] 実装したページの動作確認済み
- [ ] コンソールエラーなし
- [ ] UI要素の表示確認済み
- [ ] API連携動作確認済み
- [ ] レスポンシブデザイン確認済み

### 確認事項
- [ ] 作業前にブランチ確認済み（mainブランチでない）
- [ ] Issue番号確認済み
- [ ] shadcn/ui既存コンポーネント活用検討済み
- [ ] TypeScript strictモードエラーなし
- [ ] any型不使用（unknown型使用）
- [ ] 1ファイル1コンポーネント
- [ ] displayName未設定（自動推論）
- [ ] React.forwardRef不使用
- [ ] タブレットファースト設計
- [ ] **未使用コード削除済み（IDE警告で確認）**
- [ ] **未使用import削除済み**
- [ ] **未使用変数・関数・コンポーネント削除済み**
- [ ] **未使用type/interface削除済み**
- [ ] **コメントアウトコード削除済み**
- [ ] テストカバレッジ80%以上
- [ ] Lint/ビルド成功
- [ ] Storybookストーリー作成済み（Presentationalコンポーネント）
- [ ] サーバー起動・動作確認済み
```

## 使用ツール

### 必須ツール
- **Read**: ドキュメント参照、既存コード確認
- **Write**: 新規ファイル作成
- **Edit**: 既存ファイル編集
- **Bash**: Lint/テスト/ビルド実行

### 推奨ツール
- **Grep**: 類似実装検索
- **Glob**: コンポーネント検索

### MCP（Model Context Protocol）ツール

#### Context7 MCP（技術ドキュメント参照）
最新の技術ドキュメント・ベストプラクティス確認:

1. **Next.js関連**
   ```
   resolve-library-id: "next.js"
   get-library-docs: "/vercel/next.js"
   topic: "app router server components"
   ```

2. **React関連**
   ```
   resolve-library-id: "react"
   get-library-docs: "/facebook/react"
   topic: "hooks best practices"
   ```

3. **shadcn/ui関連**
   ```
   resolve-library-id: "shadcn/ui"
   get-library-docs: "/shadcn/ui"
   topic: "component customization"
   ```

4. **YouTube API関連（フロントエンド）**
   ```
   resolve-library-id: "youtube iframe api"
   get-library-docs: "/youtube/iframe_api_reference"
   topic: "player events"
   ```

**活用場面**:
- App Routerのベストプラクティス確認
- Hooksルールの確認
- パフォーマンス最適化（useMemo/useCallback）
- アクセシビリティ対応

#### Chrome DevTools MCP（実動作確認）
実際のブラウザでの動作・パフォーマンス確認:

1. **navigate_page**: ページ遷移
   ```
   url: "http://localhost:3000/dashboard"
   ```

2. **take_snapshot**: ページの状態確認
   ```
   # 実装したUIの構造確認
   ```

3. **list_network_requests**: API呼び出し確認
   ```
   # ダッシュボードのAPI呼び出しを監視
   resourceTypes: ["fetch", "xhr"]
   ```

4. **performance_start_trace**: パフォーマンス測定
   ```
   reload: true
   autoStop: true
   # Core Web Vitalsの測定
   ```

5. **take_screenshot**: 視覚的な確認
   ```
   format: "png"
   # レスポンシブデザインの確認
   ```

**活用場面**:
- 実装した画面の動作確認
- API通信の検証
- レンダリングパフォーマンス測定
- レスポンシブデザイン確認
- Core Web Vitals測定

## コーディング規約チェックリスト

### TypeScript/基本設計
- [ ] TypeScript strictモードでエラーが出ない
- [ ] any型を使用していない（unknown型を使用）
- [ ] interfaceを優先使用（typeは必要時のみ）
- [ ] 命名規則に従っている（PascalCase/camelCase）
- [ ] 1ファイル1コンポーネント

### React Hooks
- [ ] Hooks呼び出しがトップレベルのみ
- [ ] カスタムフックは"use"プレフィックス付き
- [ ] 依存配列が正確に指定されている
- [ ] useEffectのクリーンアップ関数を実装
- [ ] React.forwardRefを使用していない

### Next.js App Router
- [ ] Server/Client Componentを適切に選択
- [ ] 'use client'ディレクティブの要否を正しく判断
- [ ] ディレクトリ構成が規約に従っている
- [ ] (private_pages)配下に認証が必要な画面を配置

### shadcn/ui/スタイリング
- [ ] 既存のshadcn/uiコンポーネントで要件を満たせるか事前確認済み
- [ ] components/ui/を直接編集していない
- [ ] CSS変数でテーマカスタマイズ
- [ ] cn()ユーティリティでクラス結合
- [ ] タブレットファースト設計（md:768px基準）
- [ ] displayName未設定（自動推論に任せる）
- [ ] exportは定義と同時

### コンポーネント設計
- [ ] Presentational/Containerの分離
- [ ] 表示制御はContainer層で実装
- [ ] Presentationalはstorybookで確認可能
- [ ] classNameプロパティは必要最低限
- [ ] JSX.Element型注釈不使用（自動推論）

### フォーム実装
- [ ] React Hook FormとZodでフォーム実装
- [ ] 日本語のバリデーションメッセージ
- [ ] エラーハンドリングを実装
- [ ] ローディング状態を管理

### パフォーマンス
- [ ] next/imageで画像最適化
- [ ] useMemo/useCallbackを適切に使用（高コスト処理のみ）
- [ ] 不要な再レンダリングを防止
- [ ] useEffectは極力避ける（onClickハンドラで対応可能な場合）

### テスト
- [ ] Vitestでユニットテストを実装
- [ ] Testing Libraryで振る舞いをテスト
- [ ] MSWでAPIモックを定義
- [ ] エラーケースのテストを含む
- [ ] 非同期処理はwaitForを使用
- [ ] テストファイルは対象ファイルと同階層

### 品質/セキュリティ
- [ ] 環境変数はNEXT_PUBLIC_プレフィックス付き（公開用）
- [ ] XSS対策（出力エスケープ）
- [ ] エラーバウンダリーを実装
- [ ] アクセシビリティ対応（ARIA属性）

## 参照ドキュメント

### 必須参照
- `documents/development/coding-rules/frontend-rules.md`: フロントエンドコーディング規約
- `documents/development/development-policy.md`: 開発ガイドライン
- `documents/features/[機能名]/specification.md`: 機能仕様書

### 必要に応じて参照
- `documents/architecture/tech-stack.md`: 技術スタック
- `documents/architecture/system-architecture.md`: システムアーキテクチャ
- `frontend/components/ui/`: shadcn/uiコンポーネント
- `frontend/src/lib/api/generated/`: Orval生成APIクライアント

## トラブルシューティング

### Lint/ビルドエラー
1. エラーメッセージを確認
2. Biome設定（biome.json）確認
3. TypeScript設定（tsconfig.json）確認
4. コーディング規約に照らして修正

### テストエラー
1. エラーメッセージを確認
2. MSWハンドラー設定確認
3. 非同期処理の待機確認（waitFor）
4. モック設定の確認

### カバレッジ不足
1. カバレッジレポート確認
2. 未テストの分岐を特定
3. 境界値・異常系のテスト追加

### shadcn/uiコンポーネントのカスタマイズ
1. ui/配下は直接編集禁止
2. 拡張コンポーネントで実装
3. cva（class-variance-authority）でvariant追加
