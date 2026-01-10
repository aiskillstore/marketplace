// @ts-nocheck
/* eslint-disable */
/**
 * ✅ AFTER REFACTOR - Component file (UI only)
 *
 * NOTE: This is an EXAMPLE file for educational purposes.
 * Type checking is disabled to avoid false errors from missing dependencies.
 *
 * This is 1 of 3 files from the refactor. Total lines: ~80
 *
 * Responsibilities:
 * - Rendering UI
 * - Calling hooks
 * - Passing props
 *
 * Logic extracted to: hooks.ts
 * Types extracted to: types.ts
 */

import type { ReactElement } from 'react';

import { Button } from '@shared/ui/button';
import { Input } from '@shared/ui/input';

import { useFormLogic } from './hooks';
import type { IFormData } from './types';

export function RefactoredForm(): ReactElement {
  const {
    formData,
    errors,
    isSubmitting,
    isSuccess,
    handleChange,
    handleSubmit,
  } = useFormLogic();

  if (isSuccess) {
    return (
      <div className="glass-card p-8 text-center">
        <h2 className="text-2xl font-bold text-white mb-4">Success!</h2>
        <p className="text-gray-300">Your form has been submitted.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
      <h2 className="text-2xl font-bold text-white mb-6">Registration Form</h2>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
          Name
        </label>
        <Input
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="glass-card-static"
          aria-invalid={Boolean(errors.name)}
        />
        {errors.name && (
          <p className="text-red-400 text-sm mt-1">{errors.name}</p>
        )}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
          Email
        </label>
        <Input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className="glass-card-static"
          aria-invalid={Boolean(errors.email)}
        />
        {errors.email && (
          <p className="text-red-400 text-sm mt-1">{errors.email}</p>
        )}
      </div>

      <Button
        type="submit"
        disabled={isSubmitting}
        className="btn-primary-glass w-full"
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    </form>
  );
}
