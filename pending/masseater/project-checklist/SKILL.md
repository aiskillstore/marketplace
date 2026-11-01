---
name: project-checklist
description: プロジェクトの設計で検討すべき事項が充足しているかを、実物で確認して判定する。masseater/typescript-template から作ったリポジトリでは、GitHub の設定とテンプレートへの移行も扱う。新しいリポジトリの作成時、AI に移行を任せたあと、大きな変更の前、既存のプロジェクトの見直しで使う。
---

# project-checklist

- 各項目は、現状を確認し、充足条件と比較して判定する
- 判定には、確認した場所と結果を添える
- 判定は「充足」「不足」「未確認」「対象外」のいずれかにする
- 判定の作業中は修正しない。不足は一覧として渡す。修正しながら判定すると、判定が修正の結果に置き換わる

## この skill が必要な理由と達成したい状態

この skill が必要な理由は、設計で検討すべき事項の多くが、検討しなくてもプロジェクトが動いてしまうことにある。誰も決めなければデフォルトがそのまま答えになり、ビルドもテストも通るので、決めていないことに気づかない。問題は、公開した後に請求や情報漏えいとして見つかる。

この skill で達成したい状態は、設計で検討すべきすべての事項について、プロジェクトの現状を実物の根拠つきで説明できることである。

## 判定の方法

- 現状は、本番環境、ビルドの出力、リポジトリのファイルの順に確認する。本番に近いものほど、意図ではなく事実を表すからである。本番での確認方法は measure-dont-guess に従う
- 方針や設定が書いてあるだけでは「充足」にしない。書いてあっても機能していないことがある
- 数値で決まる項目は、計測した数値で判定する
- 対象プロジェクトの AGENTS.md や CLAUDE.md に決まりがあれば、それを充足条件にする。そのプロジェクトで下した判断が一般的な基準より優先するからである
- 確認できなかった項目は「未確認」とし、確認できなかった理由を書く。推測で埋めると、確認していない内容が確認済みの内容と区別できなくなる
- 当てはまらない項目は「対象外」とし、プロジェクトの実物から言える理由を書く。理由を書けない対象外は不足として扱う
- 検査や lint を緩めて通した形跡は、それ自体を不足として扱う。タスクの削除、severity や ignorePatterns の緩和、抑止コメントの増加がこれにあたる。緩んでいるかもしれない検査は、ほかの判定の根拠に使えないからである

## 項目

次もすべて読むこと。

- [`requirements`](references/requirements.md)。利用者と目的、想定する規模
- [`access`](references/access.md)。ページと API ごとの公開範囲と、認証と認可
- [`rendering`](references/rendering.md)。ページごとのレンダリング方式
- [`data`](references/data.md)。データの保存先、スキーマの変更手順、キャッシュ
- [`security`](references/security.md)。シークレット、依存パッケージの脆弱性、レスポンスヘッダー、動的スキャン、レート制限
- [`cost`](references/cost.md)。1 回のアクセスで発生する課金、暴走時の上限、実際の請求額
- [`performance`](references/performance.md)。Web Vitals とサーバーの応答時間
- [`search-and-sharing`](references/search-and-sharing.md)。検索エンジンへの掲載、掲載ページの内容、SNS で共有したときの表示
- [`accessibility`](references/accessibility.md)。自動検査で見つかる違反と、キーボード操作
- [`observability`](references/observability.md)。本番リクエストの追跡、計測、障害の検知
- [`reliability`](references/reliability.md)。データの復旧、リソースの再作成、外部呼び出しの失敗
- [`delivery`](references/delivery.md)。CI とデプロイの経路、ロールバック、環境変数
- [`dependencies`](references/dependencies.md)。依存パッケージの選定とライセンス、第三者の素材、Node.js のバージョン
- [`privacy`](references/privacy.md)。収集している個人情報と、その削除
- [`publishing`](references/publishing.md)。公開しているものの一覧、URL の変更、撤去手順
- [`testing`](references/testing.md)。テストのためだけの本番コード

masseater/typescript-template から作ったリポジトリでは、次も読むこと。

- [`typescript-template`](references/typescript-template.md)。テンプレートの骨格が導入され、機能し、旧構成が残っていないか

## 用途

次を読むこと。

- [`check`](usecases/check.md)。プロジェクトの現状を確認して判定する
- [`setup`](usecases/setup.md)。テンプレートから作ったリポジトリの GitHub 側の設定を gh で揃える
