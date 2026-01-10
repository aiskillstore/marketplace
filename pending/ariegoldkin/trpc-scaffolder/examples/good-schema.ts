/**
 * EXAMPLE: Good Schema Pattern
 * This file demonstrates best practices for Zod schemas in DevPrep AI
 *
 * Note: This is an example file for documentation purposes.
 * It uses @ts-nocheck to prevent IDE errors.
 */
// @ts-nocheck
/* eslint-disable */

/**
 * User Profile Schemas
 * Zod schemas for user profile types
 * Used by tRPC procedures for runtime validation
 */
import { z } from "zod";

// ✅ Constants for validation rules (maintainability)
const MIN_NAME_LENGTH = 1;
const MAX_NAME_LENGTH = 100;
const MIN_EXPERIENCE_YEARS = 0;
const MAX_EXPERIENCE_YEARS = 50;

// ✅ Enums for type safety
export const experienceLevelSchema = z.enum([
  "junior",
  "mid",
  "senior",
  "lead",
]);

export const roleSchema = z.enum([
  "frontend",
  "backend",
  "fullstack",
  "devops",
  "mobile",
]);

/**
 * User Profile Schema
 * ✅ Complete entity definition with validation
 */
export const userProfileSchema = z.object({
  id: z.string(),
  name: z
    .string()
    .min(MIN_NAME_LENGTH, "Name is required")
    .max(MAX_NAME_LENGTH, "Name too long"),
  email: z.string().email("Invalid email format"),
  role: roleSchema,
  experienceLevel: experienceLevelSchema,
  yearsOfExperience: z
    .number()
    .int()
    .min(MIN_EXPERIENCE_YEARS)
    .max(MAX_EXPERIENCE_YEARS),
  technologies: z.array(z.string()).min(1, "At least one technology required"),
  // ✅ Optional fields clearly marked
  bio: z.string().optional(),
  avatarUrl: z.string().url().optional(),
  // ✅ Dates as strings (ISO format)
  createdAt: z.string(),
  updatedAt: z.string(),
});

/**
 * Get User Profile Input Schema
 * ✅ Clear, descriptive naming
 */
export const getUserProfileInputSchema = z.object({
  userId: z.string().min(1, "User ID is required"),
});

/**
 * Get User Profile Output Schema
 * ✅ Wraps response with success indicator
 */
export const getUserProfileOutputSchema = z.object({
  profile: userProfileSchema,
  success: z.boolean(),
});

/**
 * Update User Profile Input Schema
 * ✅ Uses .partial() for optional updates
 * ✅ Omits read-only fields
 */
export const updateUserProfileInputSchema = z.object({
  userId: z.string(),
  profileData: userProfileSchema
    .partial()
    .omit({ id: true, createdAt: true, updatedAt: true }),
});

/**
 * Update User Profile Output Schema
 */
export const updateUserProfileOutputSchema = z.object({
  profile: userProfileSchema,
  success: z.boolean(),
});

// ✅ Export inferred types (critical for type safety!)
export type ExperienceLevel = z.infer<typeof experienceLevelSchema>;
export type Role = z.infer<typeof roleSchema>;
export type UserProfile = z.infer<typeof userProfileSchema>;
export type GetUserProfileInput = z.infer<typeof getUserProfileInputSchema>;
export type GetUserProfileOutput = z.infer<typeof getUserProfileOutputSchema>;
export type UpdateUserProfileInput = z.infer<
  typeof updateUserProfileInputSchema
>;
export type UpdateUserProfileOutput = z.infer<
  typeof updateUserProfileOutputSchema
>;

// ✅ Example usage in router:
// import {
//   getUserProfileInputSchema,
//   getUserProfileOutputSchema,
//   type UserProfile,
// } from "../schemas/user.schema";
//
// getProfile: publicProcedure
//   .input(getUserProfileInputSchema)
//   .output(getUserProfileOutputSchema)
//   .query(async ({ input }) => { ... })
