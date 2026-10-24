# 操作を止めないミューテーション

順番が仕様のミューテーションは、`useMutation` に同じ `scope: { id }` を渡して作る。同じ `scope.id` のミューテーションは順番に実行される。原典の `useActionState` のキューイングはこれで置き換える。

- 順番が仕様の列は、同じ `scope.id` に載せる
- 画面は `useOptimistic` と `startTransition` ですぐ更新する
- pending は半透明などの演出に使う

## 使わないもの

- ボタンの無効化で、pending のあいだ操作列全体を止めない。ユーザーは続けて操作したい
- 順番が仕様の列を、`Effect.all` の `concurrency: "unbounded"` や別々の scope に載せない。後の操作が先に終わり、サーバーの状態が壊れる
- キューを `useRef` や Effect Atom で自前実装しない。`scope.id` がすでに順番を保証する
- `useActionState` と `useFormStatus` の代わりに `useMutation` を使う。pending と error を TanStack Query に集める

一度きりの送信フォームは、`disabled={mutation.isPending}` と `aria-busy={mutation.isPending}` で二重送信を防いでよい。操作を連打させたい列だけ、上の規則を適用する。
