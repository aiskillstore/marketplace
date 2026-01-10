---
name: figma-to-tailwind
description: Figma MCPで取得したデザイン変数をTailwind CSS標準クラスに変換する。Figma MCPのコード生成後やデザイン実装時に自動起動。
---

# Figma Variables → Tailwind CSS 変換スキル

このスキルは、Figma MCPで取得したデザイン変数（Variables）を、Tailwind CSS標準クラスに自動変換するためのガイドです。

## いつ使用するか

以下の状況で、このスキルを自動的に適用してください：

1. **Figma MCPでデザインを取得した後**
   - `mcp__figma-mcp__get_design_context`や`mcp__figma-mcp__get_variable_defs`を実行した直後
   - Figma MCPが生成したコードに`var(--spacing-*)`や`var(--width-*)`などの変数が含まれている場合

2. **デザイン実装中**
   - コンポーネントのスタイリング時
   - レイアウト調整時
   - Figma変数を使用しているコードを発見した場合

3. **コードレビュー時**
   - `px-[var(--spacing-4)]`のようなFigma変数の直接使用を発見した場合
   - インラインスタイルで`style={{ fontSize: 'var(--h4-font-size)' }}`のような記述を発見した場合

## 変換手順

### ステップ1: マッピングファイルを確認

`frontend/lib/figma-tailwind-map.ts`を参照して、Figma変数がTailwind標準クラスに変換可能か確認します。

```typescript
import {
  spacingMap,
  widthMap,
  heightMap,
  borderRadiusMap,
  typographyMap,
  figmaVarToTailwindClass,
  isStandardTailwindClass
} from '@/lib/figma-tailwind-map'
```

### ステップ2: 変換ルールの適用

#### スペーシング（spacing）

```typescript
// ❌ Figma MCPが生成したコード
<div className="px-[var(--spacing-4,16px)] py-[var(--spacing-2,8px)] gap-[var(--spacing-3,12px)]">

// ✅ Tailwind標準クラスに変換
<div className="px-4 py-2 gap-3">
```

**変換マッピング:**
- `spacing/1` → `1` (4px)
- `spacing/2` → `2` (8px)
- `spacing/3` → `3` (12px)
- `spacing/4` → `4` (16px)
- `spacing/1-5` → `1.5` (6px) ※カスタム
- `spacing/2-5` → `2.5` (10px) ※カスタム

#### サイズ（width/height）

```typescript
// ❌ Figma MCPが生成したコード
<div className="w-[var(--width-w-4,16px)] h-[var(--height-h-5,20px)]">

// ✅ Tailwind標準クラスに変換
<div className="w-4 h-5">
```

#### ボーダー半径（border-radius）

```typescript
// ❌ Figma MCPが生成したコード
<div className="rounded-[var(--border-radius-rounded-md,8px)]">

// ✅ Tailwind標準クラスに変換
<div className="rounded-md">
```

#### タイポグラフィ（typography）

```typescript
// ❌ Figma MCPが生成したコード（インラインスタイル）
<h1 style={{
  fontFamily: 'var(--h4-font-family)',
  fontSize: 'var(--h4-font-size)',
  fontWeight: 'var(--h4-font-weight)',
  lineHeight: 'var(--h4-line-height)',
}}>

// ✅ Tailwind標準クラスに変換
<h1 className="text-h4">

// または Tailwind標準で代用可能な場合
<p className="text-sm">  // body2と同等 (14px/20px)
<p className="text-base">  // body1と同等 (16px/24px)
```

**実装済みのカスタムクラス:**（tailwind.config.tsで定義済み）

- `text-h4`: 24px/32px/bold
- `text-h5`: 20px/28px/bold
- `text-title`: 18px/28px/bold
- `text-body1`: 16px/24px/normal
- `text-body2`: 14px/20px/normal
- `text-body3`: 12px/16px/normal

**注意**: 新規デザイン変換時は必ずFigma MCPのHEX/px値を確認し、既存クラスと比較すること。名前の類似性だけで判断しない。

### ステップ3: カラーの扱い

カラーは**Figma MCPから届くHEX値を確認**して、適切に変換します。

```typescript
// ❌ Figma独自変数の直接使用は禁止
<div className="bg-[var(--base-primary)]">
<div className="text-[var(--base-foreground)]">

// ✅ 正しい実装
// 1. まずFigmaのHEX値と既存のshadcn/ui変数を比較
//    --base-primary: #00a0e9 = --primary: #00a0e9 → 同じ色！
<div className="bg-primary text-primary-foreground">

// 2. shadcn/uiにない独自色の場合はtailwind.config.tsに追加
//    --base-dark-primary: #006cab → shadcn/uiにない
//    → tailwind.config.tsに 'dark-primary': '#006cab' を追加
<div className="text-dark-primary">
```

**重要な原則:**
- **名前の類似性だけで判断しない** - 必ずHEX値を確認する
- Figma MCPからはHEX形式で届くので、既存のshadcn/ui変数(HSL形式)と比較
- 同じ色なら既存の変数を使用（例: `bg-primary`）
- 異なる色ならtailwind.config.tsにカスタム定義を追加

### ステップ4: 標準にない値の対応

マッピングにない値を発見した場合：

1. **tailwind.config.tsに追加**
   ```typescript
   theme: {
     extend: {
       spacing: {
         '13': '52px',  // 新しいカスタム値
       }
     }
   }
   ```

2. **figma-tailwind-map.tsに追加**
   ```typescript
   export const spacingMap: Record<string, number | string> = {
     // ... 既存のマッピング
     'spacing/13': 13,  // 新しいマッピング
   }
   ```

3. **実装で使用**
   ```typescript
   <div className="px-13">
   ```

## 禁止事項

### ❌ Figma変数の直接使用

```typescript
// 禁止
<div className="px-[var(--spacing-4)]">
<div className="gap-[var(--spacing-2,8px)]">
<div style={{ width: 'var(--width-w-4)' }}>
```

### ❌ カスタムユーティリティクラス

```css
/* globals.cssに以下を追加するのは禁止 */
.w-spacing-2 {
  width: var(--spacing-2);
}

.header-base {
  height: var(--height-h-16);
}
```

### ❌ インラインスタイルの乱用

```typescript
// 特別な理由がない限り禁止
<div style={{
  fontSize: 'var(--h4-font-size)',
  padding: 'var(--spacing-4)'
}}>
```

## 実装例

### Before（Figma MCPが生成）

```tsx
export default function Main() {
  return (
    <div className="bg-[var(--base/background-gray,#f6f8f9)] border-[var(--base/border,#edeef1)] border-b-0 border-l-[var(--border-width/border,1px)]">
      <div className="bg-[var(--base/background,#ffffff)] h-[64px] px-[var(--spacing/4,16px)] py-0">
        <div className="gap-[var(--spacing/2,8px)]">
          <div className="rounded-[var(--border-radius/rounded-md,8px)] size-[28px]">
            <Icon className="size-[16px]" />
          </div>
          <div className="gap-[var(--spacing/3,12px)]">
            <div style={{
              fontFamily: 'var(--h5-font-family)',
              fontSize: 'var(--h5-font-size)',
              fontWeight: 'var(--h5-font-weight)',
              lineHeight: 'var(--h5-line-height)',
            }}>
              サポート
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### After（Tailwind標準クラスに変換）

```tsx
export default function Main() {
  return (
    <div className="bg-muted border border-l border-b-0">
      <div className="bg-background h-16 px-4 py-0">
        <div className="gap-2">
          <div className="rounded-md size-7">
            <Icon className="size-4" />
          </div>
          <div className="gap-3">
            <div className="text-h5">
              サポート
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

## チェックリスト

変換時に以下を確認してください：

- [ ] `var(--spacing-*)`を`px-*`, `py-*`, `gap-*`等に変換
- [ ] `var(--width-*)`を`w-*`に変換
- [ ] `var(--height-*)`を`h-*`に変換
- [ ] `var(--border-radius-*)`を`rounded-*`に変換
- [ ] インラインスタイルのフォント指定を`text-*`クラスに変換
- [ ] カラーはCSS変数のまま保持
- [ ] 標準にない値は`tailwind.config.ts`に追加
- [ ] カスタムユーティリティクラスを作成していない

## 参照ドキュメント

- **変換マッピング**: `frontend/lib/figma-tailwind-map.ts`
- **Tailwind設定**: `frontend/tailwind.config.ts`
- **開発ガイド**: `documents/development/coding-rules/frontend-rules.md` セクション12

## 注意事項

- このスキルは**Figma MCPのコード生成後に自動的に適用**されるべきです
- 変換後のコードは必ずLintとBuildチェックを行ってください
- 疑問がある場合は、必ず`figma-tailwind-map.ts`を参照してください
- カラー定義は例外として、常にCSS変数を使用してください
