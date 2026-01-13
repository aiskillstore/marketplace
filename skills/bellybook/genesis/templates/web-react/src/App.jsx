/**
 * [INPUT]: React, framer-motion, lucide-react, UI 组件
 * [OUTPUT]: App 根组件
 * [POS]: 应用根组件，承载页面布局与路由
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import { motion } from 'framer-motion'
import { Sparkles, Zap, Palette, Code2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ======================================== */}
      {/*  Hero Section                           */}
      {/* ======================================== */}
      <main className="flex flex-col items-center justify-center min-h-screen p-8 gap-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="flex items-center justify-center gap-3 mb-6">
            <Sparkles className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold">Web Project</h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-md">
            React 19 + Vite + TailwindCSS V4 + shadcn/ui
          </p>
        </motion.div>

        {/* ======================================== */}
        {/*  Component Showcase                     */}
        {/* ======================================== */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-4xl"
        >
          <Card className="p-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="w-6 h-6" />
                Design System Preview
              </CardTitle>
              <CardDescription>
                Micro-neumorphism with gradients and 3D shadows
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              {/* Buttons */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Buttons</h3>
                <div className="flex flex-wrap gap-3">
                  <Button>Default</Button>
                  <Button variant="primary">Primary</Button>
                  <Button variant="accent">Accent</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="destructive">Destructive</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost</Button>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Button size="sm">Small</Button>
                  <Button size="default">Default</Button>
                  <Button size="lg">Large</Button>
                  <Button size="xl">Extra Large</Button>
                </div>
              </div>

              {/* Badges */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Badges</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge>Default</Badge>
                  <Badge variant="secondary">Secondary</Badge>
                  <Badge variant="destructive">Destructive</Badge>
                  <Badge variant="outline">Outline</Badge>
                </div>
              </div>

              {/* Input */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Input</h3>
                <div className="max-w-sm">
                  <Input placeholder="Type something..." />
                </div>
              </div>

              {/* Cards */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-muted-foreground">Cards</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card variant="elevated" className="p-4">
                    <div className="flex items-center gap-3">
                      <Zap className="w-8 h-8 text-primary" />
                      <div>
                        <h4 className="font-semibold">Elevated Card</h4>
                        <p className="text-sm text-muted-foreground">With hover lift effect</p>
                      </div>
                    </div>
                  </Card>
                  <Card variant="inset" className="p-4">
                    <div className="flex items-center gap-3">
                      <Code2 className="w-8 h-8 text-accent" />
                      <div>
                        <h4 className="font-semibold">Inset Card</h4>
                        <p className="text-sm text-muted-foreground">Sunken appearance</p>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Footer hint */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-sm text-muted-foreground"
        >
          Edit <code className="px-2 py-1 bg-muted rounded">src/App.jsx</code> to get started
        </motion.p>
      </main>
    </div>
  )
}

export default App
