# PR Template Examples

Examples of well-formatted PR descriptions for different scenarios.

## Example 1: New Feature

### English
```markdown
## Summary
- Add real-time notifications using WebSocket
- Implement notification preferences UI
- Include comprehensive error handling and reconnection logic

## Test plan
- [ ] Test WebSocket connection establishment
- [ ] Test notification delivery for different event types
- [ ] Test preferences save and load
- [ ] Test reconnection on network failure
- [ ] Verify no memory leaks during long sessions
- [ ] Test on different browsers (Chrome, Firefox, Safari)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- WebSocketを使用したリアルタイム通知を追加
- 通知設定UIを実装
- 包括的なエラーハンドリングと再接続ロジックを含む

## テスト計画
- [ ] WebSocket接続確立のテスト
- [ ] 異なるイベントタイプの通知配信をテスト
- [ ] 設定の保存と読み込みをテスト
- [ ] ネットワーク障害時の再接続をテスト
- [ ] 長時間セッション中のメモリリークがないことを確認
- [ ] 異なるブラウザでテスト（Chrome、Firefox、Safari）

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 2: Bug Fix

### English
```markdown
## Summary
- Fix race condition in user session management
- Root cause was concurrent requests modifying session state
- Solution implements optimistic locking with version tracking

## Test plan
- [ ] Reproduce original race condition
- [ ] Verify fix prevents concurrent modification
- [ ] Test with high concurrent load (100+ requests/sec)
- [ ] Verify no performance degradation
- [ ] Add unit tests for session locking
- [ ] Add integration tests for concurrent scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- ユーザーセッション管理の競合状態を修正
- 根本原因は同時リクエストによるセッション状態の変更
- 解決策はバージョン追跡による楽観的ロックを実装

## テスト計画
- [ ] 元の競合状態を再現
- [ ] 修正が同時変更を防ぐことを確認
- [ ] 高い同時負荷でテスト（100以上のリクエスト/秒）
- [ ] パフォーマンス低下がないことを確認
- [ ] セッションロックの単体テストを追加
- [ ] 同時実行シナリオの統合テストを追加

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 3: Performance Improvement

### English
```markdown
## Summary
- Optimize database queries using query result caching
- Reduce average API response time by 60%
- Implement Redis-based caching layer with TTL

## Test plan
- [ ] Benchmark before and after performance
- [ ] Test cache invalidation on data updates
- [ ] Verify cache hit/miss ratios
- [ ] Test memory usage under load
- [ ] Ensure stale data is properly invalidated
- [ ] Load test with production-like traffic

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- クエリ結果キャッシュを使用してデータベースクエリを最適化
- 平均APIレスポンス時間を60%削減
- TTL付きRedisベースのキャッシングレイヤーを実装

## テスト計画
- [ ] 改善前後のパフォーマンスをベンチマーク
- [ ] データ更新時のキャッシュ無効化をテスト
- [ ] キャッシュヒット/ミス率を確認
- [ ] 負荷時のメモリ使用量をテスト
- [ ] 古いデータが適切に無効化されることを確認
- [ ] 本番相当のトラフィックで負荷テスト

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 4: Refactoring

### English
```markdown
## Summary
- Refactor authentication module to use dependency injection
- No functional changes - purely structural improvement
- Improve testability and maintainability

## Test plan
- [ ] All existing authentication tests pass
- [ ] No behavioral changes in authentication flow
- [ ] Code coverage maintained at 95%+
- [ ] Integration tests pass without modification
- [ ] Manual testing of login/logout flows

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- 認証モジュールを依存性注入を使用するようリファクタリング
- 機能的な変更なし - 純粋な構造改善
- テスタビリティと保守性を向上

## テスト計画
- [ ] 既存の認証テストがすべてパス
- [ ] 認証フローの動作変更がないことを確認
- [ ] コードカバレッジが95%以上を維持
- [ ] 統合テストが変更なしでパス
- [ ] ログイン/ログアウトフローの手動テスト

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 5: Documentation Update

### English
```markdown
## Summary
- Update API documentation to reflect new endpoints
- Add authentication examples for each endpoint
- Fix outdated parameter descriptions

## Test plan
- [ ] Review for technical accuracy
- [ ] Verify all code examples execute successfully
- [ ] Check all links and references
- [ ] Validate against actual API behavior
- [ ] Peer review by team member

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- 新しいエンドポイントを反映するようAPIドキュメントを更新
- 各エンドポイントの認証例を追加
- 古いパラメータの説明を修正

## テスト計画
- [ ] 技術的正確性をレビュー
- [ ] すべてのコード例が正常に実行されることを確認
- [ ] すべてのリンクと参照をチェック
- [ ] 実際のAPI動作に対して検証
- [ ] チームメンバーによるピアレビュー

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 6: Breaking Change

### English
```markdown
## Summary
- Migrate user API from v1 to v2 with breaking changes
- Improve response format for consistency
- Add pagination support for list endpoints

## Breaking Changes
- Response format changed from snake_case to camelCase
- User ID type changed from integer to UUID string
- List endpoints now return paginated results

## Migration Guide
1. Update client code to use camelCase for all fields
2. Update user ID parsing to handle string UUIDs
3. Implement pagination handling for list requests

## Test plan
- [ ] V2 API endpoints function correctly
- [ ] V1 API still works (deprecated but not removed)
- [ ] Migration script tested on staging
- [ ] Client libraries updated and tested
- [ ] Documentation reflects all breaking changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- ユーザーAPIをv1からv2へ破壊的変更を伴って移行
- 一貫性のためにレスポンス形式を改善
- リストエンドポイントにページネーションサポートを追加

## 破壊的変更
- レスポンス形式がsnake_caseからcamelCaseに変更
- ユーザーIDの型が整数からUUID文字列に変更
- リストエンドポイントがページネーション結果を返すように変更

## マイグレーションガイド
1. クライアントコードをすべてのフィールドでcamelCaseを使用するように更新
2. 文字列UUIDを処理するようにユーザーID解析を更新
3. リストリクエストのページネーション処理を実装

## テスト計画
- [ ] V2 APIエンドポイントが正しく機能
- [ ] V1 APIが引き続き動作（非推奨だが削除されていない）
- [ ] ステージング環境でマイグレーションスクリプトをテスト
- [ ] クライアントライブラリが更新されテスト済み
- [ ] ドキュメントがすべての破壊的変更を反映

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 7: Security Fix

### English
```markdown
## Summary
- Fix SQL injection vulnerability in search endpoint
- Implement parameterized queries for all user inputs
- Add input validation and sanitization

## Test plan
- [ ] Verify SQL injection attempts are blocked
- [ ] Test with various malicious payloads
- [ ] Ensure legitimate searches still work
- [ ] Security audit completed
- [ ] No performance regression

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- 検索エンドポイントのSQLインジェクション脆弱性を修正
- すべてのユーザー入力にパラメータ化クエリを実装
- 入力検証とサニタイゼーションを追加

## テスト計画
- [ ] SQLインジェクションの試行がブロックされることを確認
- [ ] さまざまな悪意のあるペイロードでテスト
- [ ] 正当な検索が引き続き機能することを確認
- [ ] セキュリティ監査完了
- [ ] パフォーマンス低下なし

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Example 8: Multiple Features

### English
```markdown
## Summary
- Add user profile customization features
- Implement avatar upload with image processing
- Add bio and social links editing
- Include privacy controls for profile visibility

## Implementation Details
- Avatar processing uses Sharp for image optimization
- Maximum file size: 5MB, formats: JPG, PNG, WebP
- Bio limited to 500 characters with markdown support
- Privacy settings: public, friends-only, private

## Test plan
- [ ] Test avatar upload and processing
- [ ] Test bio editing with various markdown
- [ ] Test social links validation
- [ ] Test privacy settings enforcement
- [ ] Test file size and format validation
- [ ] Test image processing performance
- [ ] Verify mobile responsiveness

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Japanese
```markdown
## 概要
- ユーザープロフィールカスタマイズ機能を追加
- 画像処理を伴うアバターアップロードを実装
- 自己紹介とソーシャルリンクの編集を追加
- プロフィール公開設定のプライバシーコントロールを含む

## 実装の詳細
- アバター処理はSharpを使用して画像最適化
- 最大ファイルサイズ：5MB、形式：JPG、PNG、WebP
- 自己紹介は500文字まで、マークダウンサポート
- プライバシー設定：公開、友達のみ、非公開

## テスト計画
- [ ] アバターアップロードと処理をテスト
- [ ] さまざまなマークダウンで自己紹介編集をテスト
- [ ] ソーシャルリンク検証をテスト
- [ ] プライバシー設定の適用をテスト
- [ ] ファイルサイズと形式の検証をテスト
- [ ] 画像処理のパフォーマンスをテスト
- [ ] モバイルレスポンシブを確認

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```
