# 移行の完了を判定する

テンプレートから作ったリポジトリで、移行が完了しているかを判定する手順である。

1. 対象は、いま作業しているリポジトリである。別のリポジトリを指されたときは、そちらで作業する
2. テンプレートの実物を最新にする。`ghq list -p` にあればその clone を最新にし、無ければ `ghq get masseater/typescript-template` で取る。ghq の無い環境では、一時ディレクトリへ `gh repo clone` する
3. [`typescript-template`](../references/typescript-template.md) の要素を順に、テンプレートの実物と突き合わせる。要素ごとに、確かめたコマンドと出力を控える
4. 対象のリポジトリで `vp install`、続けて `vp run verify` を実行する
5. GitHub 側の設定は [setup](setup.md) の手順で揃え、その「反映を確かめる」まで通す
6. 要素ごとに「要素・判定・根拠」の表と、「移行完了」か「未完了」かの判定を出す。未完了には、欠けを直すための一覧を添える

判定には、主に次の材料を使う。

- 骨格のファイルを、テンプレートと並べて開く
- `git config core.hooksPath` で hook の設定を見る
- `gh run list --branch main --limit 5` と `gh run view <run-id> --log` で main の CI を確かめる
- `skills ls` と `vp exec intent list` でスキルを見る

コマンドの出力は要約せず控える。判定の根拠になる。
