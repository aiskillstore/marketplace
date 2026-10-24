# 重い派生は一貫性を外す

入力と重い一覧を同じレンダーに載せると、入力の反映が一覧の再レンダーまで遅れる。入力と一覧を分ける。

- いまの入力は Effect Atom にすぐ書く
- 一覧に渡す値は `useDeferredValue` で遅らせる
- 遅れていることを示すなら `useTransition` の pending を使う

タイマーデバウンスは使わない。`useRef` と `setTimeout` と二重の state で作るものも、手書きの `useDebounced*` も、原典の続編にあるトランジション対応の自前デバウンスも、`useDeferredValue` で置き換える。
