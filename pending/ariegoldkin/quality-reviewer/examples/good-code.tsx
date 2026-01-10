// @ts-nocheck
/* eslint-disable */
/**
 * ✅ PERFECT EXAMPLE - Follows all DevPrep AI standards
 *
 * NOTE: This is an EXAMPLE file for educational purposes.
 * Type checking is disabled to avoid false errors from missing dependencies.
 *
 * Standards demonstrated:
 * ✓ Interface with 'I' prefix (line 28)
 * ✓ Type-only imports (lines 20-21)
 * ✓ Path aliases @shared/ (line 23)
 * ✓ Constants for magic numbers (lines 25-26)
 * ✓ Complexity <15 (simple, focused logic)
 * ✓ File <180 lines
 * ✓ Proper JSDoc comments
 * ✓ Early returns for validation
 * ✓ No 'any' types
 * ✓ Descriptive naming
 */

import type { ReactElement, MouseEvent } from 'react';

import { Button } from '@shared/ui/button';
import { cn } from '@shared/utils/cn';

const MAX_TITLE_LENGTH = 100;
const MIN_TITLE_LENGTH = 3;

interface IQuestionCardProps {
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  onSelect: (id: string) => void;
  isSelected?: boolean;
  className?: string;
}

/**
 * Displays a question card with title, description, and difficulty
 *
 * @param props - Component props
 * @returns Rendered question card
 */
export function QuestionCard({
  title,
  description,
  difficulty,
  onSelect,
  isSelected = false,
  className,
}: IQuestionCardProps): ReactElement {
  // Early validation returns
  if (title.length < MIN_TITLE_LENGTH) {
    return <div>Title too short</div>;
  }

  if (title.length > MAX_TITLE_LENGTH) {
    return <div>Title too long</div>;
  }

  const handleClick = (event: MouseEvent<HTMLButtonElement>): void => {
    event.preventDefault();
    onSelect(title);
  };

  const getDifficultyColor = (): string => {
    const colorMap = {
      easy: 'neon-glow-green',
      medium: 'neon-glow-orange',
      hard: 'neon-glow-red',
    };

    return colorMap[difficulty];
  };

  return (
    <div
      className={cn(
        'glass-card p-6 rounded-lg',
        isSelected && 'border-2 border-primary',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">{title}</h3>
        <span className={cn('badge', getDifficultyColor())}>{difficulty}</span>
      </div>

      <p className="text-gray-300 mb-4">{description}</p>

      <Button onClick={handleClick} className="btn-primary-glass">
        {isSelected ? 'Selected' : 'Select Question'}
      </Button>
    </div>
  );
}
