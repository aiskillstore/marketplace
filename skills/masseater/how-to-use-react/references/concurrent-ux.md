# 並行 UI

`<ViewTransition>`、`<Activity>`、`useEffectEvent` の使いどころである。設計の前提は [`design-theory`](design-theory.md) も読むこと。

- 遷移の出入りは `<ViewTransition>` に乗せる
- 行き来しても状態を残したい画面は `<Activity>` で隠す
- 購読のたびに最新でなくてよい値は `useEffectEvent` に移す

## ViewTransition

遷移、Suspense の表示、deferred 更新に乗る出入りは `<ViewTransition>` で包む。`startTransition` の中で状態を変える。

## Activity

タブ、サイドバー、行き来しても入力を残したい画面は `<Activity mode={open ? "visible" : "hidden"}>` で切り替える。`hidden` のあいだ Effect は破棄される。

## useEffectEvent

Effect が購読する対象は依存配列に残す。購読のたびに最新でなくてよい値は `useEffectEvent` に移す。その関数は依存配列に入れない。同一性がレンダーごとに変わり、Effect が毎レンダー実行し直すためである。
