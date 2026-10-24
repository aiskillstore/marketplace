# skill を作る

skill を新しく作るときの手順である。

1. skills CLI の `skills init <name>` で `SKILL.md` を作る
2. 本文を、必要な理由と達成したい状態から導いて書く
3. `skills-ref validate <dir>` を通す
4. 参照するファイルと、名前で委ねた skill が存在することを確かめる
5. 構造的な内容ならテストケースを書く。主観的な内容なら書かない
6. リポジトリの手順で PR を出す

複数のリポジトリで使う skill は masseater/skills の `skills/` に置く。ここに置いた skill は Claude Code プラグイン `masseater-skills` にも入る。

返答には、skill の要約、主な設計判断、検証の結果を書く。
