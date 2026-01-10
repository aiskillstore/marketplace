# Common Design Patterns

Recurring patterns in DevPrep AI HTML prototypes and their React implementations.

---

## Pattern 1: 20/80 Split Layout

**Use Case**: Question panel (20%) + Editor/Answer area (80%)

**HTML Prototype**:
```html
<div class="flex h-screen">
  <div class="w-1/5 glass-card">Question panel</div>
  <div class="w-4/5">Editor</div>
</div>
```

**React Implementation**:
```tsx
export function SessionLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Question Panel - 20% */}
      <aside className="w-1/5 glass-card overflow-y-auto">
        <div className="p-6 space-y-4">
          {/* Question content */}
        </div>
      </aside>

      {/* Editor/Answer Area - 80% */}
      <main className="w-4/5 flex-1">
        {children}
      </main>
    </div>
  );
}
```

---

## Pattern 2: Stats Grid

**Use Case**: Metrics display (5K+ users, 98% success, etc.)

**HTML Prototype**:
```html
<div class="grid grid-cols-3 gap-6">
  <div class="glass-card neon-glow-cyan">
    <div class="text-4xl">5K+</div>
    <div>Users</div>
  </div>
  <!-- Repeat 2 more times -->
</div>
```

**React Implementation**:
```tsx
interface IStatCardProps {
  value: string;
  label: string;
  className?: string;
}

function StatCard({ value, label, className }: IStatCardProps) {
  return (
    <Card className={cn("glass-card neon-glow-cyan text-center", className)}>
      <CardContent className="pt-6">
        <div className="text-4xl font-bold text-glow">{value}</div>
        <div className="text-sm text-[rgba(229,229,255,0.7)] mt-2">
          {label}
        </div>
      </CardContent>
    </Card>
  );
}

export function StatsGrid({ stats }: { stats: IStatCardProps[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {stats.map((stat) => (
        <StatCard key={stat.label} {...stat} />
      ))}
    </div>
  );
}
```

---

## Pattern 3: Progressive Hints Panel

**Use Case**: Accordion-style hint system

**HTML Prototype**:
```html
<div class="glass-card">
  <h3>Hints</h3>
  <div class="hint-item">
    <button class="btn-glass">Show Hint 1</button>
    <div class="hint-content hidden">Hint content...</div>
  </div>
</div>
```

**React Implementation**:
```tsx
interface IHint {
  level: number;
  content: string;
  revealed: boolean;
}

interface IHintsPanelProps {
  hints: IHint[];
  onRevealHint: (level: number) => void;
}

export function HintsPanel({ hints, onRevealHint }: IHintsPanelProps) {
  return (
    <Card className="glass-card neon-glow-purple">
      <CardHeader>
        <CardTitle className="text-glow">Progressive Hints</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {hints.map((hint) => (
          <div key={hint.level} className="space-y-2">
            {!hint.revealed ? (
              <Button
                variant="outline"
                className="btn-glass w-full"
                onClick={() => onRevealHint(hint.level)}
              >
                Show Hint {hint.level}
              </Button>
            ) : (
              <Alert className="glass-card-static neon-glow-cyan">
                <AlertDescription>{hint.content}</AlertDescription>
              </Alert>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

---

## Pattern 4: Wizard Navigation

**Use Case**: Multi-step wizard with progress indicator

**HTML Prototype**:
```html
<nav class="glass-header">
  <div class="step active">1. Welcome</div>
  <div class="step">2. Profile</div>
  <div class="step">3. Setup</div>
</nav>
```

**React Implementation**:
```tsx
interface IWizardStep {
  number: number;
  label: string;
}

interface IWizardNavProps {
  steps: IWizardStep[];
  currentStep: number;
}

export function WizardNav({ steps, currentStep }: IWizardNavProps) {
  return (
    <nav className="glass-header py-4">
      <div className="container-xl">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={cn(
                "flex items-center space-x-2",
                step.number === currentStep
                  ? "text-[#7877c6] text-glow"
                  : "text-[rgba(229,229,255,0.5)]"
              )}
            >
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center",
                  step.number === currentStep
                    ? "bg-[#7877c6] neon-glow-purple"
                    : "bg-white/10"
                )}
              >
                {step.number}
              </div>
              <span className="text-sm font-medium">{step.label}</span>
              {index < steps.length - 1 && (
                <div className="w-12 h-0.5 bg-white/20 mx-4" />
              )}
            </div>
          ))}
        </div>
      </div>
    </nav>
  );
}
```

---

## Pattern 5: Feature Card Grid

**Use Case**: Landing page features section

**HTML Prototype**:
```html
<div class="grid grid-cols-3 gap-6">
  <div class="glass-card">
    <i data-lucide="brain-circuit"></i>
    <h3>AI-Powered</h3>
    <p>Description...</p>
  </div>
  <!-- Repeat 2 more times -->
</div>
```

**React Implementation**:
```tsx
import { Brain, Zap, Target } from "lucide-react";

interface IFeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}

function FeatureCard({ icon: Icon, title, description }: IFeatureCardProps) {
  return (
    <Card className="glass-card hover:bg-white/[0.08] transition-all duration-300">
      <CardContent className="pt-6 space-y-4">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center icon-glow">
          <Icon className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-xl font-bold gradient-text">{title}</h3>
        <p className="text-sm text-[rgba(229,229,255,0.7)]">
          {description}
        </p>
      </CardContent>
    </Card>
  );
}

export function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Claude AI generates personalized questions",
    },
    {
      icon: Zap,
      title: "Real-time Feedback",
      description: "Get instant evaluation and suggestions",
    },
    {
      icon: Target,
      title: "Focused Practice",
      description: "Target specific skills and technologies",
    },
  ];

  return (
    <section className="py-16">
      <div className="container-xl">
        <h2 className="gradient-text text-3xl font-bold text-center mb-12">
          Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}
```

---

## Pattern 6: Hero Section with CTA

**Use Case**: Landing page hero

**HTML Prototype**:
```html
<section class="glass-card-static">
  <h1 class="gradient-text">Welcome to DevPrep AI</h1>
  <p>Description...</p>
  <button class="btn-primary-glass pulse-glow">Get Started</button>
</section>
```

**React Implementation**:
```tsx
export function HeroSection() {
  return (
    <section className="glass-card-static py-24">
      <div className="container-xl text-center space-y-8">
        <Badge variant="outline" className="neon-glow-cyan mb-4">
          🚀 New: AI-Powered Hints
        </Badge>

        <h1 className="gradient-text text-5xl md:text-6xl font-bold">
          Welcome to DevPrep AI
        </h1>

        <p className="text-lg text-[rgba(229,229,255,0.7)] max-w-2xl mx-auto">
          Master technical interviews with AI-generated questions and real-time
          feedback
        </p>

        <div className="flex gap-4 justify-center">
          <Button className="btn-primary-glass pulse-glow" size="lg">
            Get Started
          </Button>
          <Button variant="outline" className="btn-glass" size="lg">
            Learn More
          </Button>
        </div>
      </div>
    </section>
  );
}
```

---

## Pattern 7: Feedback Modal

**Use Case**: Show evaluation results after answer submission

**HTML Prototype**:
```html
<div class="modal">
  <div class="glass-card">
    <h3>Feedback</h3>
    <div class="score neon-glow-green">8.5/10</div>
    <p>Evaluation text...</p>
  </div>
</div>
```

**React Implementation**:
```tsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@shared/ui/dialog";

interface IFeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  score: number;
  feedback: string;
}

export function FeedbackModal({
  isOpen,
  onClose,
  score,
  feedback,
}: IFeedbackModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="glass-card neon-glow-purple">
        <DialogHeader>
          <DialogTitle className="gradient-text text-2xl">
            Feedback
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Card className="glass-card-static neon-glow-green text-center">
            <CardContent className="pt-6">
              <div className="text-4xl font-bold text-glow">
                {score}/10
              </div>
            </CardContent>
          </Card>

          <p className="text-sm text-[rgba(229,229,255,0.85)] leading-relaxed">
            {feedback}
          </p>

          <Button
            className="btn-primary-glass w-full"
            onClick={onClose}
          >
            Continue
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Common State Patterns

### Toggle Visibility
```tsx
const [isVisible, setIsVisible] = React.useState(false);

<Button onClick={() => setIsVisible(!isVisible)}>
  {isVisible ? "Hide" : "Show"}
</Button>
```

### Progressive Disclosure
```tsx
const [revealedCount, setRevealedCount] = React.useState(0);

const handleReveal = () => {
  setRevealedCount((prev) => Math.min(prev + 1, maxItems));
};
```

### Form State
```tsx
const [formData, setFormData] = React.useState({
  field1: "",
  field2: "",
});

const handleChange = (field: string, value: string) => {
  setFormData((prev) => ({ ...prev, [field]: value }));
};
```

---

## Responsive Breakpoints

DevPrep AI uses these Tailwind breakpoints:

```tsx
// Mobile-first approach
<div className="
  grid
  grid-cols-1          /* Mobile */
  md:grid-cols-2       /* Tablet (768px+) */
  lg:grid-cols-3       /* Desktop (1024px+) */
  xl:grid-cols-4       /* Large desktop (1280px+) */
  gap-6
">
```

Common responsive utilities:
- `hidden md:block` - Hidden on mobile, visible on tablet+
- `text-2xl md:text-4xl` - Smaller text on mobile
- `py-8 md:py-16` - Less padding on mobile
- `flex-col md:flex-row` - Stack on mobile, row on tablet+
