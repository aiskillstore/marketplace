// @ts-nocheck
/* eslint-disable */
/**
 * ❌ BAD EXAMPLE - Multiple violations
 *
 * NOTE: This is an EXAMPLE file showing INTENTIONAL VIOLATIONS for educational purposes.
 * Type checking is disabled since this code demonstrates what NOT to do.
 *
 * Violations (11 total):
 * 1. No 'I' prefix on interface (line 20)
 * 2. Direct import instead of type import (line 22)
 * 3. Relative import instead of alias (line 23)
 * 4. Using 'any' type (line 21)
 * 5. Magic numbers without constants (lines 32, 34)
 * 6. console.log in production code (line 33)
 * 7. No JSDoc comments
 * 8. No early returns (nested conditions)
 * 9. Inconsistent naming (data vs userData)
 * 10. Missing type for event parameter (line 28)
 * 11. Complexity too high (nested ifs)
 */

interface QuestionProps {  // ❌ Missing 'I' prefix
  data: any;  // ❌ Using 'any'
}

import { ReactElement } from 'react';  // ❌ Not type-only import
import { Button } from '../../../shared/ui/button';  // ❌ Relative import

export function BadQuestion(props: QuestionProps): ReactElement {
  const handleClick = (e) => {  // ❌ No type for 'e'
    if (props.data) {
      if (props.data.length > 80) {  // ❌ Magic number
        console.log('Too long');  // ❌ console.log
        if (props.data.length > 100) {  // ❌ Magic number, nested ifs
          return;
        }
      }
    }
  };

  // ❌ No validation, just returns potentially broken UI
  return (
    <div>
      <h3>{props.data.title}</h3>
      <Button onClick={handleClick}>{props.data.label}</Button>
    </div>
  );
}

// ❌ Additional violations in this file:
// - No interface exports
// - Hardcoded strings ('Too long')
// - No error handling
// - Missing prop validation
// - No accessibility attributes
