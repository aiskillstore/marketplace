# shadcn/ui Component Mapping Guide

Decision guide for mapping HTML prototype elements to shadcn/ui components.

---

## Decision Tree

### Buttons & Actions

```
Is it a button or clickable action?
├─ Primary CTA?
│  └─ <Button variant="default" className="btn-primary-glass">
├─ Secondary action?
│  └─ <Button variant="outline" className="btn-glass">
├─ Icon only?
│  └─ <Button variant="ghost" size="icon">
└─ Link-style?
   └─ <Button variant="link">
```

**HTML → shadcn Examples**:
```tsx
// HTML: <button class="btn-primary">Start</button>
<Button className="btn-primary-glass">Start</Button>

// HTML: <button class="btn-glass">Cancel</button>
<Button variant="outline" className="btn-glass">Cancel</Button>
```

---

## Cards & Containers

```
Is it a content container?
├─ Card with header and content?
│  └─ <Card> with <CardHeader> and <CardContent>
├─ Simple container?
│  └─ <div className="glass-card">
├─ Clickable card?
│  └─ <Card className="glass-card cursor-pointer hover:bg-white/[0.08]">
└─ List of items?
   └─ Multiple <Card> in grid/flex layout
```

**HTML → shadcn Examples**:
```tsx
// HTML: <div class="glass-card">...</div>
<Card className="glass-card">
  <CardContent>...</CardContent>
</Card>

// HTML: <div class="glass-card"><h3>Title</h3><p>Content</p></div>
<Card className="glass-card">
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

---

## Form Elements

### Text Input
```
Is it a text input?
├─ Single line?
│  └─ <Input type="text" />
├─ Multiple lines?
│  └─ <Textarea />
├─ Password?
│  └─ <Input type="password" />
└─ With label?
   └─ <Label> + <Input>
```

**HTML → shadcn Examples**:
```tsx
// HTML: <input type="text" placeholder="Name">
<div className="space-y-2">
  <Label htmlFor="name">Name</Label>
  <Input id="name" type="text" placeholder="Name" />
</div>

// HTML: <textarea>...</textarea>
<Textarea placeholder="Enter description..." />
```

### Dropdown
```
Is it a dropdown/select?
├─ Simple select?
│  └─ <Select> with <SelectTrigger> and <SelectContent>
├─ Searchable?
│  └─ Combobox pattern (Command + Popover)
└─ Multi-select?
   └─ Multiple <Checkbox> items
```

**HTML → shadcn Examples**:
```tsx
// HTML: <select><option>...</option></select>
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

### Checkbox & Radio
```
Is it a boolean choice?
├─ Single toggle?
│  └─ <Checkbox> or <Switch>
├─ Multiple choices?
│  └─ Multiple <Checkbox>
└─ Single choice from many?
   └─ <RadioGroup> with <RadioGroupItem>
```

**HTML → shadcn Examples**:
```tsx
// HTML: <input type="checkbox" id="agree"><label>I agree</label>
<div className="flex items-center space-x-2">
  <Checkbox id="agree" />
  <Label htmlFor="agree">I agree</Label>
</div>

// HTML: <input type="radio" name="choice" value="a">Option A
<RadioGroup>
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="a" id="a" />
    <Label htmlFor="a">Option A</Label>
  </div>
</RadioGroup>
```

---

## Display Components

### Badges & Tags
```
Is it a label/badge/tag?
├─ Status indicator?
│  └─ <Badge variant="outline">
├─ Count/number?
│  └─ <Badge variant="secondary">
└─ Action tag?
   └─ <Badge variant="default">
```

**HTML → shadcn Examples**:
```tsx
// HTML: <span class="badge">New</span>
<Badge variant="outline" className="neon-glow-cyan">New</Badge>

// HTML: <span class="count">5</span>
<Badge variant="secondary">5</Badge>
```

### Progress & Sliders
```
Is it a progress indicator or range?
├─ Progress bar?
│  └─ <Progress value={percentage} />
├─ Range slider?
│  └─ <Slider value={[value]} />
└─ Loading indicator?
   └─ <Progress value={undefined} /> (indeterminate)
```

**HTML → shadcn Examples**:
```tsx
// HTML: <div class="progress-bar" style="width: 60%"></div>
<Progress value={60} className="glass-card" />

// HTML: <input type="range" min="0" max="10">
<Slider min={0} max={10} step={1} value={[value]} />
```

---

## Interactive Components

### Tooltips & Popovers
```
Is it a hover/click overlay?
├─ Simple info on hover?
│  └─ <Tooltip>
├─ Rich content on click?
│  └─ <Popover>
└─ Menu with actions?
   └─ <DropdownMenu>
```

**HTML → shadcn Examples**:
```tsx
// HTML: <button title="Help text">?</button>
<Tooltip>
  <TooltipTrigger>?</TooltipTrigger>
  <TooltipContent>Help text</TooltipContent>
</Tooltip>
```

### Alerts & Messages
```
Is it a notification/alert?
├─ Inline message?
│  └─ <Alert>
├─ Toast notification?
│  └─ toast() from useToast
└─ Error display?
   └─ <Alert variant="destructive">
```

**HTML → shadcn Examples**:
```tsx
// HTML: <div class="alert alert-success">Success!</div>
<Alert className="glass-card neon-glow-green">
  <AlertTitle>Success</AlertTitle>
  <AlertDescription>Operation completed</AlertDescription>
</Alert>
```

---

## Layout Components

### Tabs
```tsx
// HTML: <div class="tabs">...</div>
<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

### Accordion
```tsx
// HTML: <details><summary>Title</summary>Content</details>
<Accordion type="single" collapsible>
  <AccordionItem value="item1">
    <AccordionTrigger>Title</AccordionTrigger>
    <AccordionContent>Content</AccordionContent>
  </AccordionItem>
</Accordion>
```

### Scroll Area
```tsx
// HTML: <div class="scrollable">Long content...</div>
<ScrollArea className="h-[400px] glass-card">
  Long content...
</ScrollArea>
```

---

## Component Import Patterns

```tsx
// Buttons
import { Button } from "@shared/ui/button";

// Cards
import { Card, CardContent, CardHeader, CardTitle } from "@shared/ui/card";

// Forms
import { Input } from "@shared/ui/input";
import { Label } from "@shared/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@shared/ui/select";
import { Checkbox } from "@shared/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@shared/ui/radio-group";
import { Textarea } from "@shared/ui/textarea";
import { Slider } from "@shared/ui/slider";

// Display
import { Badge } from "@shared/ui/badge";
import { Progress } from "@shared/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@shared/ui/alert";

// Interactive
import { Tooltip, TooltipContent, TooltipTrigger } from "@shared/ui/tooltip";
import { Popover, PopoverContent, PopoverTrigger } from "@shared/ui/popover";

// Layout
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@shared/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@shared/ui/accordion";
import { ScrollArea } from "@shared/ui/scroll-area";

// Utils
import { cn } from "@shared/utils/cn";
```

---

## Decision Checklist

When mapping HTML to shadcn:

1. ✅ **Identify semantic purpose** (not just appearance)
2. ✅ **Check if shadcn component exists** for that purpose
3. ✅ **Apply glassmorphism classes** via className prop
4. ✅ **Preserve accessibility** (labels, ARIA attributes)
5. ✅ **Use TypeScript types** from shadcn components
