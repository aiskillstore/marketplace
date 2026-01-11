# Animations - Pattern A Split-Panel Combat UI

## Animation Categories

| Category | Purpose | Duration |
|----------|---------|----------|
| **Feedback** | User action response | 150-300ms |
| **Combat** | Attack/damage visuals | 300-600ms |
| **Transition** | State changes | 200-400ms |
| **Ambient** | Continuous effects | Infinite |

---

## CSS Keyframe Definitions

### Floating Text Animations

```css
/* Standard float up (damage, heal, status) */
@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  20% {
    opacity: 1;
    transform: translateY(-70px) scale(1.15);
  }
  100% {
    opacity: 0;
    transform: translateY(-150px) scale(0.8);
  }
}

/* Critical hit (dramatic shake + scale) */
@keyframes critFloat {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1) rotate(0deg);
  }
  10% {
    transform: translateY(-20px) scale(1.2) rotate(-3deg);
  }
  20% {
    transform: translateY(-40px) scale(1.4) rotate(3deg);
  }
  30% {
    transform: translateY(-60px) scale(1.3) rotate(-2deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-80px) scale(1.2) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translateY(-150px) scale(0.9) rotate(0deg);
  }
}

/* Miss/evade (subtle fade) */
@keyframes fadeOnly {
  0% {
    opacity: 1;
    transform: translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateY(-30px);
  }
}
```

### Screen Shake

```css
/* Light shake (normal hit) */
@keyframes shakeLite {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

/* Medium shake (critical hit) */
@keyframes shakeMedium {
  0%, 100% { transform: translateX(0); }
  10%, 90% { transform: translateX(-2px); }
  20%, 80% { transform: translateX(3px); }
  30%, 50%, 70% { transform: translateX(-4px); }
  40%, 60% { transform: translateX(4px); }
}

/* Heavy shake (boss attack) */
@keyframes shakeHeavy {
  0%, 100% { transform: translate(0, 0); }
  10% { transform: translate(-5px, -2px); }
  20% { transform: translate(5px, 2px); }
  30% { transform: translate(-5px, 2px); }
  40% { transform: translate(5px, -2px); }
  50% { transform: translate(-3px, 3px); }
  60% { transform: translate(3px, -3px); }
  70% { transform: translate(-2px, 2px); }
  80% { transform: translate(2px, -2px); }
  90% { transform: translate(-1px, 1px); }
}
```

### Character Attack Animation

```css
/* Player attacks (lunge right) */
@keyframes playerAttack {
  0% { transform: translateX(0); }
  30% { transform: translateX(50px); }
  50% { transform: translateX(40px); }
  100% { transform: translateX(0); }
}

/* Enemy attacks (lunge left) */
@keyframes enemyAttack {
  0% { transform: translateX(0); }
  30% { transform: translateX(-50px); }
  50% { transform: translateX(-40px); }
  100% { transform: translateX(0); }
}

/* Damage received (recoil) */
@keyframes recoil {
  0% { transform: translateX(0); }
  20% { transform: translateX(-15px); }
  40% { transform: translateX(10px); }
  60% { transform: translateX(-5px); }
  100% { transform: translateX(0); }
}

/* Death fade */
@keyframes deathFade {
  0% {
    opacity: 1;
    filter: grayscale(0) brightness(1);
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    filter: grayscale(0.5) brightness(0.8);
    transform: scale(0.98);
  }
  100% {
    opacity: 0.3;
    filter: grayscale(1) brightness(0.5);
    transform: scale(0.95);
  }
}
```

### UI Element Animations

```css
/* Pulse glow (active toggle, selection) */
@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(251, 191, 36, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
  }
}

/* Card hover lift */
@keyframes cardLift {
  0% {
    transform: translateY(0) scale(1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  100% {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  }
}

/* Phase indicator advance */
@keyframes phaseAdvance {
  0% {
    transform: scale(1);
    background-color: rgb(63, 63, 70); /* zinc-700 */
  }
  50% {
    transform: scale(1.2);
    background-color: rgb(245, 158, 11); /* amber-500 */
  }
  100% {
    transform: scale(1);
    background-color: rgb(245, 158, 11);
  }
}

/* Turn change spotlight */
@keyframes spotlightShift {
  0% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
  100% {
    opacity: 0.3;
  }
}
```

### VS Divider Effects

```css
/* Energy clash pulse */
@keyframes clashPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

/* Aura collision */
@keyframes auraCollide {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* VS text pulse */
@keyframes vsPulse {
  0%, 100% {
    text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
  }
  50% {
    text-shadow: 0 0 20px rgba(245, 158, 11, 0.8),
                 0 0 30px rgba(245, 158, 11, 0.4);
  }
}
```

### Resource Bar Animations

```css
/* HP drain (smooth decrease) */
@keyframes hpDrain {
  0% {
    width: var(--from-width);
  }
  100% {
    width: var(--to-width);
  }
}

/* Low HP warning pulse */
@keyframes lowHpPulse {
  0%, 100% {
    opacity: 1;
    box-shadow: inset 0 0 10px rgba(239, 68, 68, 0.3);
  }
  50% {
    opacity: 0.9;
    box-shadow: inset 0 0 20px rgba(239, 68, 68, 0.5);
  }
}

/* Chakra regeneration shimmer */
@keyframes cpRegen {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

---

## Tailwind Animation Classes

### Add to tailwind.config.ts

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      keyframes: {
        floatUp: {
          '0%': { opacity: '1', transform: 'translateY(0) scale(1)' },
          '20%': { opacity: '1', transform: 'translateY(-70px) scale(1.15)' },
          '100%': { opacity: '0', transform: 'translateY(-150px) scale(0.8)' },
        },
        critFloat: {
          '0%': { opacity: '1', transform: 'translateY(0) scale(1) rotate(0deg)' },
          '20%': { transform: 'translateY(-40px) scale(1.4) rotate(3deg)' },
          '50%': { opacity: '1', transform: 'translateY(-80px) scale(1.2)' },
          '100%': { opacity: '0', transform: 'translateY(-150px) scale(0.9)' },
        },
        fadeOnly: {
          '0%': { opacity: '1', transform: 'translateY(0)' },
          '100%': { opacity: '0', transform: 'translateY(-30px)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 90%': { transform: 'translateX(-2px)' },
          '20%, 80%': { transform: 'translateX(3px)' },
          '30%, 50%, 70%': { transform: 'translateX(-4px)' },
          '40%, 60%': { transform: 'translateX(4px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(251, 191, 36, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(251, 191, 36, 0.5)' },
        },
        playerAttack: {
          '0%': { transform: 'translateX(0)' },
          '30%': { transform: 'translateX(50px)' },
          '100%': { transform: 'translateX(0)' },
        },
        enemyAttack: {
          '0%': { transform: 'translateX(0)' },
          '30%': { transform: 'translateX(-50px)' },
          '100%': { transform: 'translateX(0)' },
        },
      },
      animation: {
        'float-up': 'floatUp 1.2s ease-out forwards',
        'crit-float': 'critFloat 1.2s ease-out forwards',
        'fade-only': 'fadeOnly 1s ease-out forwards',
        'shake': 'shake 0.4s cubic-bezier(.36,.07,.19,.97) both',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'player-attack': 'playerAttack 0.4s ease-out',
        'enemy-attack': 'enemyAttack 0.4s ease-out',
      },
    },
  },
};
```

---

## Animation Utility Classes

### Usage in Components

```typescript
// Floating text types
const FLOATING_TEXT_ANIMATION = {
  damage: 'animate-float-up',
  crit: 'animate-crit-float',
  heal: 'animate-float-up',
  miss: 'animate-fade-only',
  block: 'animate-float-up',
  status: 'animate-float-up',
  chakra: 'animate-float-up',
};

// Screen shake trigger
const triggerShake = (intensity: 'lite' | 'medium' | 'heavy') => {
  document.body.classList.add(`animate-shake-${intensity}`);
  setTimeout(() => {
    document.body.classList.remove(`animate-shake-${intensity}`);
  }, 400);
};

// Card interaction states
const CARD_ANIMATIONS = {
  idle: 'transition-all duration-200',
  hover: 'hover:scale-[1.02] hover:-translate-y-1',
  selected: 'scale-105 animate-pulse-glow',
  disabled: 'opacity-50 cursor-not-allowed',
};
```

---

## Animation Timing Reference

### Duration Guidelines

| Animation Type | Duration | Easing |
|----------------|----------|--------|
| Micro-interaction | 150ms | ease-out |
| Button feedback | 200ms | ease-out |
| Card hover | 200ms | ease-out |
| Panel transition | 300ms | ease-in-out |
| Attack animation | 400ms | ease-out |
| Floating text | 1200ms | ease-out |
| Screen shake | 400ms | cubic-bezier |
| Death fade | 600ms | ease-in |

### Easing Functions

```typescript
const EASING = {
  // Standard
  linear: 'linear',
  easeIn: 'ease-in',
  easeOut: 'ease-out',
  easeInOut: 'ease-in-out',

  // Custom
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
  smooth: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  shake: 'cubic-bezier(0.36, 0.07, 0.19, 0.97)',
};
```

---

## React Animation Hooks

### useScreenShake

```typescript
import { useCallback } from 'react';

export const useScreenShake = () => {
  const shake = useCallback((intensity: 'lite' | 'medium' | 'heavy' = 'medium') => {
    const root = document.getElementById('combat-root');
    if (!root) return;

    const className = {
      lite: 'animate-shake-lite',
      medium: 'animate-shake',
      heavy: 'animate-shake-heavy',
    }[intensity];

    root.classList.add(className);
    setTimeout(() => root.classList.remove(className), 400);
  }, []);

  return { shake };
};
```

### useCharacterAnimation

```typescript
import { useState, useCallback } from 'react';

type AnimationState = 'idle' | 'attacking' | 'damaged' | 'dead';

export const useCharacterAnimation = () => {
  const [state, setState] = useState<AnimationState>('idle');

  const playAttack = useCallback(() => {
    setState('attacking');
    setTimeout(() => setState('idle'), 400);
  }, []);

  const playDamaged = useCallback(() => {
    setState('damaged');
    setTimeout(() => setState('idle'), 300);
  }, []);

  const playDeath = useCallback(() => {
    setState('dead');
    // No reset - stays dead
  }, []);

  return {
    state,
    playAttack,
    playDamaged,
    playDeath,
    className: {
      idle: '',
      attacking: 'animate-player-attack', // or enemy-attack
      damaged: 'animate-recoil',
      dead: 'animate-death-fade',
    }[state],
  };
};
```

### useFloatingText

```typescript
import { useState, useCallback, useRef } from 'react';

interface FloatingText {
  id: string;
  value: string;
  type: 'damage' | 'crit' | 'heal' | 'miss' | 'block' | 'status' | 'chakra';
  position: { x: number; y: number };
}

export const useFloatingText = () => {
  const [texts, setTexts] = useState<FloatingText[]>([]);
  const idCounter = useRef(0);

  const spawn = useCallback((
    target: 'player' | 'enemy',
    value: string,
    type: FloatingText['type'],
    targetRef: React.RefObject<HTMLElement>
  ) => {
    const rect = targetRef.current?.getBoundingClientRect();
    if (!rect) return;

    const id = `float-${idCounter.current++}`;
    const randomOffset = (Math.random() - 0.5) * 60;

    const newText: FloatingText = {
      id,
      value,
      type,
      position: {
        x: rect.left + rect.width / 2 + randomOffset,
        y: rect.top + rect.height * 0.4,
      },
    };

    setTexts(prev => [...prev, newText]);

    // Auto-remove after animation
    setTimeout(() => {
      setTexts(prev => prev.filter(t => t.id !== id));
    }, 1200);
  }, []);

  return { texts, spawn };
};
```

---

## Reduced Motion Support

```typescript
// Check user preference
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Conditional animation class
const getAnimationClass = (animation: string) => {
  if (prefersReducedMotion) {
    return 'transition-opacity duration-300'; // Simple fade only
  }
  return animation;
};

// CSS media query
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Animation Event Mapping

| Game Event | Animation(s) | Target |
|------------|--------------|--------|
| Player attacks | playerAttack + floatingText | Player sprite + enemy panel |
| Enemy attacks | enemyAttack + floatingText + shake | Enemy sprite + player panel + screen |
| Critical hit | critFloat + shakeMedium | Floating text + screen |
| Skill selected | pulseGlow | Skill card |
| Turn change | spotlightShift | Active panel |
| Buff applied | floatUp (status) | Character panel |
| Low HP | lowHpPulse | HP bar |
| Death | deathFade | Character sprite |
| Phase advance | phaseAdvance | Phase indicator node |
