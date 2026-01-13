// @ts-nocheck
/* eslint-disable */
/**
 * ✅ AFTER REFACTOR - Types file (Type definitions only)
 *
 * NOTE: This is an EXAMPLE file for educational purposes.
 * Type checking is disabled to avoid false errors.
 *
 * This is 3 of 3 files from the refactor. Total lines: ~40
 *
 * Responsibilities:
 * - Type definitions
 * - Interface declarations
 * - Type exports
 *
 * UI extracted to: Component.tsx
 * Logic extracted to: hooks.ts
 */

import type { ChangeEvent, FormEvent } from 'react';

/**
 * Form data structure
 */
export interface IFormData {
  name: string;
  email: string;
  role: string;
  experience: number;
  skills: string[];
}

/**
 * Form validation errors
 */
export interface IFormErrors {
  name?: string;
  email?: string;
  role?: string;
  experience?: string;
  skills?: string;
  submit?: string;
}

/**
 * Return type for useFormLogic hook
 */
export interface IUseFormLogicReturn {
  formData: IFormData;
  errors: IFormErrors;
  isSubmitting: boolean;
  isSuccess: boolean;
  handleChange: (event: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}
