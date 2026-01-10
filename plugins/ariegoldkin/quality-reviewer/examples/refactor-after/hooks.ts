// @ts-nocheck
/* eslint-disable */
/**
 * ✅ AFTER REFACTOR - Hooks file (Logic only)
 *
 * NOTE: This is an EXAMPLE file for educational purposes.
 * Type checking is disabled to avoid false errors.
 *
 * This is 2 of 3 files from the refactor. Total lines: ~70
 *
 * Responsibilities:
 * - Form state management
 * - Validation logic
 * - Submission handling
 * - Error handling
 *
 * UI extracted to: Component.tsx
 * Types extracted to: types.ts
 */

import { useState, useCallback, type ChangeEvent, type FormEvent } from 'react';

import type { IFormData, IFormErrors, IUseFormLogicReturn } from './types';

const INITIAL_FORM_DATA: IFormData = {
  name: '',
  email: '',
  role: '',
  experience: 0,
  skills: [],
};

const MIN_NAME_LENGTH = 2;
const MAX_NAME_LENGTH = 50;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function useFormLogic(): IUseFormLogicReturn {
  const [formData, setFormData] = useState<IFormData>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<IFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateField = useCallback((name: keyof IFormData, value: string): string => {
    if (name === 'name') {
      if (value.length < MIN_NAME_LENGTH) {
        return `Name must be at least ${MIN_NAME_LENGTH} characters`;
      }
      if (value.length > MAX_NAME_LENGTH) {
        return `Name must be less than ${MAX_NAME_LENGTH} characters`;
      }
    }

    if (name === 'email') {
      if (!EMAIL_REGEX.test(value)) {
        return 'Invalid email address';
      }
    }

    return '';
  }, []);

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      const { name, value } = event.target;

      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));

      // Clear error for this field
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    },
    []
  );

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>): Promise<void> => {
      event.preventDefault();

      // Validate all fields
      const newErrors: IFormErrors = {};
      Object.keys(formData).forEach((key) => {
        const error = validateField(key as keyof IFormData, String(formData[key as keyof IFormData]));
        if (error) {
          newErrors[key as keyof IFormData] = error;
        }
      });

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return;
      }

      // Submit form
      setIsSubmitting(true);
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setIsSuccess(true);
      } catch (error) {
        setErrors({ submit: 'Submission failed. Please try again.' });
      } finally {
        setIsSubmitting(false);
      }
    },
    [formData, validateField]
  );

  return {
    formData,
    errors,
    isSubmitting,
    isSuccess,
    handleChange,
    handleSubmit,
  };
}
