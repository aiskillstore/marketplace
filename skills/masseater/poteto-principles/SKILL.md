---
name: poteto-principles
description: 設計、実装、修正、リファクタリング、移行、検証、文書の変更に取りかかるときに読む。経験を積んだエンジニアが何度も効いた判断の観点を原則集として持つ。
metadata:
  derived-from: https://github.com/cursor/plugins/tree/c86f349b102feb91f1966f8a6a60882a4e601b50/pstack/skills
---

# poteto-principles

経験を積んだエンジニアが何度も効いた判断の観点を言葉にした、原則集である。

## この skill が必要な理由と達成したい状態

この skill が必要な理由は、作業者がその場で思いつく観点でしか判断を問えないことにある。知らない観点は問いとして浮かばないので、抜けていても気づけず、同じ種類の誤りを繰り返す。経験を積んだエンジニアが、何度も効いた判断の観点を言葉にしたものを借りれば、その抜けを自分の経験を待たずに埋められる。

この skill で達成したい状態は、どの判断も、経験を積んだエンジニアが当てる観点を通っていることである。

## 原則

`references/` はすべて読むこと。

- [`attack-the-premise`](references/attack-the-premise.md)。同じ前提を共有する修正が 2 つ以上同じ検査で落ちたら、修正ではなく前提を疑う
- [`boundary-discipline`](references/boundary-discipline.md)。検証とエラー処理は境界に集め、内部は型を信じ、ロジックは純粋関数に置く
- [`build-the-lever`](references/build-the-lever.md)。手作業でやらず、同じ作業を再実行できる道具を作る
- [`encode-lessons-in-structure`](references/encode-lessons-in-structure.md)。同じ指示を 2 回書いたら、文ではなく lint、メタデータ、検査、スクリプトにする
- [`exhaust-the-design-space`](references/exhaust-the-design-space.md)。前例のない設計は、競合する試作を 2 つか 3 つ作って比べてから決める
- [`experience-first`](references/experience-first.md)。実装の都合より使う人の体験を選び、少なく磨いて出す
- [`explain-the-number`](references/explain-the-number.md)。計った数字を信じる前に、何がそれを制限しているかを言う
- [`fix-root-causes`](references/fix-root-causes.md)。症状ではなく根本原因を直す。再現し、なぜを繰り返し、ガードで黙らせない
- [`foundational-thinking`](references/foundational-thinking.md)。ロジックより先にデータ構造を決め、土台になるものを先に作る
- [`guard-the-context-window`](references/guard-the-context-window.md)。大きな出力はサブエージェントに回し、主スレッドには要約だけ残す
- [`laziness-protocol`](references/laziness-protocol.md)。削除に寄せ、問題を解く最小の変更にする
- [`make-operations-idempotent`](references/make-operations-idempotent.md)。何度実行しても、途中で落ちても、同じ終状態に収束させる
- [`migrate-callers-then-delete-legacy-apis`](references/migrate-callers-then-delete-legacy-apis.md)。新しい API を入れたら、呼び出し元を移して旧 API を同じ波で消す
- [`minimize-reader-load`](references/minimize-reader-load.md)。読み手が辿る層と頭に持つ状態を数え、どちらも減らす
- [`model-the-domain`](references/model-the-domain.md)。分岐を散らさず、ドメインをデータ構造に表す
- [`never-block-on-the-human`](references/never-block-on-the-human.md)。元に戻せる作業は尋ねずに進め、結果を見せる
- [`outcome-oriented-execution`](references/outcome-oriented-execution.md)。計画した移行では、途中の安定より最終状態の整合を優先する
- [`prove-it-works`](references/prove-it-works.md)。完了と言う前に、代理ではなく実物で確かめる
- [`redesign-from-first-principles`](references/redesign-from-first-principles.md)。新しい要件を継ぎ足さず、最初からあったものとして設計し直す
- [`separate-before-serializing-shared-state`](references/separate-before-serializing-shared-state.md)。共有される可変状態は、まず共有をなくし、本当に要るときだけ構造で直列化する
- [`sequence-verifiable-units`](references/sequence-verifiable-units.md)。作業を検証できる小さな単位に切り、1 つずつ確かめて進める
- [`subtract-before-you-add`](references/subtract-before-you-add.md)。足す前に消す。不要なコード、検証、スタブを先に取り除く
- [`test-behavior-not-implementation`](references/test-behavior-not-implementation.md)。利用者と同じ呼び方でコードを呼び、利用者が見る結果そのものを検証する
- [`type-system-discipline`](references/type-system-discipline.md)。不正な状態を型で表せなくし、境界で解析し、コンパイラに嘘をつかない
