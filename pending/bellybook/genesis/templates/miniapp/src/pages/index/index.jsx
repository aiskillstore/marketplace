/**
 * [INPUT]: 依赖 @tarojs/components 的 View/Text/Button，依赖 @tarojs/taro 的 useLoad
 * [OUTPUT]: 对外提供 Index 页面组件
 * [POS]: pages/index 的主页面，展示 Taro + React + Tailwind 技术栈
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import { Text, View } from "@tarojs/components";

/* ============================================================
   设计系统展示页
   验证 Cyber Neon 主题是否正确生效
   ============================================================ */

export default function Index() {
  return (
    <View className="min-h-screen bg-background p-4">
      {/* --------------------------------------------------------
          HEADER
          -------------------------------------------------------- */}
      <View className="mb-6">
        <Text className="text-2xl font-bold text-foreground">
          Cyber Neon 设计系统
        </Text>
        <Text className="text-sm text-muted-foreground mt-1 block">
          霓虹粉 × 赛博青 | Tailwind CSS v4
        </Text>
      </View>

      {/* --------------------------------------------------------
          COLOR PALETTE
          -------------------------------------------------------- */}
      <View className="mb-6">
        <Text className="text-lg font-semibold text-foreground mb-3 block">
          色彩系统
        </Text>

        {/* 主色 Primary */}
        <View className="flex items-center mb-2">
          <View className="w-12 h-12 rounded-lg bg-primary mr-3" />
          <View>
            <Text className="text-foreground font-medium block">Primary</Text>
            <Text className="text-muted-foreground text-xs">
              #ff00c8 霓虹粉
            </Text>
          </View>
        </View>

        {/* 强调色 Accent */}
        <View className="flex items-center mb-2">
          <View className="w-12 h-12 rounded-lg bg-accent mr-3" />
          <View>
            <Text className="text-foreground font-medium block">Accent</Text>
            <Text className="text-muted-foreground text-xs">
              #00ffcc 赛博青
            </Text>
          </View>
        </View>

        {/* 次要色 Secondary */}
        <View className="flex items-center mb-2">
          <View className="w-12 h-12 rounded-lg bg-secondary border border-border mr-3" />
          <View>
            <Text className="text-foreground font-medium block">Secondary</Text>
            <Text className="text-muted-foreground text-xs">柔和背景</Text>
          </View>
        </View>

        {/* 危险色 Destructive */}
        <View className="flex items-center">
          <View className="w-12 h-12 rounded-lg bg-destructive mr-3" />
          <View>
            <Text className="text-foreground font-medium block">
              Destructive
            </Text>
            <Text className="text-muted-foreground text-xs">
              #ff3d00 警告红
            </Text>
          </View>
        </View>
      </View>

      {/* --------------------------------------------------------
          BUTTONS
          -------------------------------------------------------- */}
      <View className="mb-6">
        <Text className="text-lg font-semibold text-foreground mb-3 block">
          按钮组件
        </Text>

        <View className="flex flex-wrap gap-2">
          <View className="px-4 py-2 bg-primary text-primary-foreground rounded-lg">
            <Text className="font-medium">Primary</Text>
          </View>

          <View className="px-4 py-2 bg-accent text-accent-foreground rounded-lg">
            <Text className="font-medium">Accent</Text>
          </View>

          <View className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg border border-border">
            <Text className="font-medium">Secondary</Text>
          </View>

          <View className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg">
            <Text className="font-medium">Danger</Text>
          </View>
        </View>
      </View>

      {/* --------------------------------------------------------
          CARDS
          -------------------------------------------------------- */}
      <View className="mb-6">
        <Text className="text-lg font-semibold text-foreground mb-3 block">
          卡片组件
        </Text>

        <View className="bg-card rounded-xl p-4 border border-border">
          <Text className="text-card-foreground font-semibold block mb-1">
            卡片标题
          </Text>
          <Text className="text-muted-foreground text-sm">
            这是一个基础卡片组件，展示了 card 和 border 颜色的配合使用。
          </Text>
        </View>
      </View>

      {/* --------------------------------------------------------
          INPUT
          -------------------------------------------------------- */}
      <View className="mb-6">
        <Text className="text-lg font-semibold text-foreground mb-3 block">
          输入框
        </Text>

        <View className="bg-background border border-input rounded-lg px-3 py-2">
          <Text className="text-muted-foreground">请输入内容...</Text>
        </View>
      </View>

      {/* --------------------------------------------------------
          CHART COLORS
          -------------------------------------------------------- */}
      <View>
        <Text className="text-lg font-semibold text-foreground mb-3 block">
          图表色板
        </Text>

        <View className="flex gap-2">
          <View className="flex-1 h-8 rounded bg-chart-1" />
          <View className="flex-1 h-8 rounded bg-chart-2" />
          <View className="flex-1 h-8 rounded bg-chart-3" />
          <View className="flex-1 h-8 rounded bg-chart-4" />
          <View className="flex-1 h-8 rounded bg-chart-5" />
        </View>
        <View className="flex gap-2 mt-1">
          <Text className="flex-1 text-center text-xs text-muted-foreground">
            1
          </Text>
          <Text className="flex-1 text-center text-xs text-muted-foreground">
            2
          </Text>
          <Text className="flex-1 text-center text-xs text-muted-foreground">
            3
          </Text>
          <Text className="flex-1 text-center text-xs text-muted-foreground">
            4
          </Text>
          <Text className="flex-1 text-center text-xs text-muted-foreground">
            5
          </Text>
        </View>
      </View>
    </View>
  );
}
