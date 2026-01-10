/**
 * EXAMPLE: Good Router Pattern
 * This file demonstrates best practices for tRPC routers in DevPrep AI
 *
 * Note: This is an example file for documentation purposes.
 * It uses @ts-nocheck to prevent IDE errors since it references non-existent schemas.
 */
// @ts-nocheck
/* eslint-disable */

/**
 * User Router
 * Contains all user-related tRPC procedures
 *
 * Endpoints:
 * - getProfile (Phase X) ✅
 * - updateProfile (Phase X) ✅
 * - deleteAccount (Phase X) - TODO
 */
import { TRPCError } from "@trpc/server";

import { publicProcedure, router } from "../init";
import {
  getUserProfileInputSchema,
  getUserProfileOutputSchema,
  updateUserProfileInputSchema,
  updateUserProfileOutputSchema,
} from "../schemas/user.schema";

/**
 * User-related procedures
 */
export const userRouter = router({
  /**
   * Get User Profile
   * Retrieves user profile data by ID
   *
   * @input userId
   * @output profile (name, email, role, experienceLevel, etc.)
   */
  getProfile: publicProcedure
    .input(getUserProfileInputSchema)
    .output(getUserProfileOutputSchema)
    .query(async ({ input }) => {
      // ✅ Validate input
      const { userId } = input;

      // ✅ Fetch data (business logic in separate service)
      const profile = await fetchUserProfile(userId);

      // ✅ Handle not found
      if (!profile) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: `User profile not found for id: ${userId}`,
        });
      }

      // ✅ Return typed response
      return {
        profile,
        success: true,
      };
    }),

  /**
   * Update User Profile
   * Updates user profile fields
   *
   * @input userId, profileData
   * @output updatedProfile, success
   */
  updateProfile: publicProcedure
    .input(updateUserProfileInputSchema)
    .output(updateUserProfileOutputSchema)
    .mutation(async ({ input }) => {
      // ✅ Destructure input
      const { userId, profileData } = input;

      // ✅ Validate existence
      const existingProfile = await fetchUserProfile(userId);
      if (!existingProfile) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "User profile not found",
        });
      }

      // ✅ Handle errors gracefully
      try {
        // Business logic
        const updatedProfile = await updateUserProfile(userId, profileData);

        return {
          profile: updatedProfile,
          success: true,
        };
      } catch (error) {
        // ✅ Proper error handling
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: "Failed to update profile",
          cause: error,
        });
      }
    }),
});

// ✅ Export router for registration in _app.ts
// Then register in _app.ts:
// export const appRouter = router({
//   ai: aiRouter,
//   user: userRouter, // <-- Add here
// });
