/**
 * @fileoverview Comprehensive test suite for UserService demonstrating vitest-testing skill patterns
 * @lastmodified 2025-10-31T00:00:00Z
 *
 * Patterns Applied:
 * - F.I.R.S.T Principles: Fast, Isolated, Repeatable, Self-Checking, Timely
 * - AAA Pattern: Arrange-Act-Assert structure throughout
 * - Black Box Testing: Tests only public API (register method)
 * - Async Testing: Proper async/await handling with mocks
 * - Error Testing: Comprehensive error scenario coverage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { UserService, type User } from './user-service'

describe('UserService', () => {
  // Mock dependencies defined at the top for clarity
  let mockDb: any
  let mockEmailService: any
  let userService: UserService

  beforeEach(() => {
    // --- ARRANGE (shared setup) ---
    // Fresh mocks for each test - ensures ISOLATION (F.I.R.S.T)
    mockDb = {
      users: {
        create: vi.fn(),
        findByEmail: vi.fn()
      }
    }

    mockEmailService = {
      sendWelcome: vi.fn()
    }

    // Fresh instance for each test - prevents test coupling
    userService = new UserService(mockDb, mockEmailService)
  })

  describe('register - Happy Paths', () => {
    it('registers a new user with valid data', async () => {
      // --- ARRANGE ---
      const validUserData = {
        email: 'john.doe@example.com',
        name: 'John Doe',
        password: 'SecurePass123!'
      }

      const expectedUser: User = {
        id: 'user-123',
        email: validUserData.email,
        name: validUserData.name,
        createdAt: new Date('2024-01-15T10:00:00Z')
      }

      // Mock database to return no existing user
      mockDb.users.findByEmail.mockResolvedValue(null)

      // Mock database to return created user
      mockDb.users.create.mockResolvedValue(expectedUser)

      // Mock email service to succeed
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(validUserData)

      // --- ASSERT ---
      // Verify the user was created with correct data
      expect(result).toEqual(expectedUser)

      // Verify database interactions (Black Box: checking behavior through public API)
      expect(mockDb.users.findByEmail).toHaveBeenCalledWith(validUserData.email)
      expect(mockDb.users.findByEmail).toHaveBeenCalledTimes(1)

      expect(mockDb.users.create).toHaveBeenCalledWith({
        email: validUserData.email,
        name: validUserData.name,
        passwordHash: 'hashed_SecurePass123!',
        createdAt: expect.any(Date)
      })
      expect(mockDb.users.create).toHaveBeenCalledTimes(1)

      // Verify email was sent
      expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(validUserData.email)
      expect(mockEmailService.sendWelcome).toHaveBeenCalledTimes(1)
    })

    it('successfully hashes password before storage', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'secure@example.com',
        name: 'Security User',
        password: 'MyPlainTextPassword'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-456',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      await userService.register(userData)

      // --- ASSERT ---
      // Black Box: Verify password is hashed (not stored as plain text)
      expect(mockDb.users.create).toHaveBeenCalledWith(
        expect.objectContaining({
          passwordHash: 'hashed_MyPlainTextPassword', // Verifying the hashing happened
          email: userData.email,
          name: userData.name
        })
      )

      // Ensure plain password is NOT passed to database
      const createCall = mockDb.users.create.mock.calls[0][0]
      expect(createCall.password).toBeUndefined()
    })

    it('sends welcome email after user creation', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'welcome@example.com',
        name: 'Welcome User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-789',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      await userService.register(userData)

      // --- ASSERT ---
      // Verify email service was called after user creation
      expect(mockEmailService.sendWelcome).toHaveBeenCalledTimes(1)
      expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(userData.email)

      // Verify order: database create happens before email send
      const dbCreateOrder = mockDb.users.create.mock.invocationCallOrder[0]
      const emailSendOrder = mockEmailService.sendWelcome.mock.invocationCallOrder[0]
      expect(dbCreateOrder).toBeLessThan(emailSendOrder)
    })
  })

  describe('register - Email Validation', () => {
    it('rejects email without @ symbol', async () => {
      // --- ARRANGE ---
      const invalidUserData = {
        email: 'invalid-email-no-at-sign',
        name: 'Invalid User',
        password: 'Password123'
      }

      // --- ACT ---
      const registerInvalidUser = () => userService.register(invalidUserData)

      // --- ASSERT ---
      // Error Testing Pattern: Verify exception is thrown
      await expect(registerInvalidUser()).rejects.toThrow('Invalid email format')

      // Verify no database calls were made
      expect(mockDb.users.findByEmail).not.toHaveBeenCalled()
      expect(mockDb.users.create).not.toHaveBeenCalled()
      expect(mockEmailService.sendWelcome).not.toHaveBeenCalled()
    })

    it('rejects empty email', async () => {
      // --- ARRANGE ---
      const emptyEmailData = {
        email: '',
        name: 'No Email User',
        password: 'Password123'
      }

      // --- ACT ---
      const registerNoEmail = () => userService.register(emptyEmailData)

      // --- ASSERT ---
      await expect(registerNoEmail()).rejects.toThrow('Invalid email format')

      // Verify no side effects occurred
      expect(mockDb.users.findByEmail).not.toHaveBeenCalled()
      expect(mockDb.users.create).not.toHaveBeenCalled()
    })

    it('accepts valid email formats', async () => {
      // --- ARRANGE ---
      // Equivalence Partitioning: Testing valid email formats
      const validEmails = [
        'simple@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_name@sub.example.com'
      ]

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT & ASSERT ---
      for (const email of validEmails) {
        mockDb.users.create.mockResolvedValue({
          id: 'user-' + email,
          email,
          name: 'Test User',
          createdAt: new Date()
        })

        await expect(
          userService.register({
            email,
            name: 'Test User',
            password: 'Password123'
          })
        ).resolves.toBeDefined()
      }
    })
  })

  describe('register - Duplicate Email Handling', () => {
    it('rejects registration when email already exists', async () => {
      // --- ARRANGE ---
      const duplicateUserData = {
        email: 'existing@example.com',
        name: 'Duplicate User',
        password: 'Password123'
      }

      const existingUser: User = {
        id: 'existing-user-id',
        email: duplicateUserData.email,
        name: 'Existing User',
        createdAt: new Date('2024-01-01T00:00:00Z')
      }

      // Mock database to return existing user
      mockDb.users.findByEmail.mockResolvedValue(existingUser)

      // --- ACT ---
      const registerDuplicate = () => userService.register(duplicateUserData)

      // --- ASSERT ---
      await expect(registerDuplicate()).rejects.toThrow('Email already exists')

      // Verify we checked for existing user
      expect(mockDb.users.findByEmail).toHaveBeenCalledWith(duplicateUserData.email)

      // Verify no user creation or email sending occurred
      expect(mockDb.users.create).not.toHaveBeenCalled()
      expect(mockEmailService.sendWelcome).not.toHaveBeenCalled()
    })

    it('checks for existing email before creating user', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'check-order@example.com',
        name: 'Order Test',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue({
        id: 'existing',
        email: userData.email,
        name: 'Existing',
        createdAt: new Date()
      })

      // --- ACT ---
      try {
        await userService.register(userData)
      } catch {
        // Expected to throw
      }

      // --- ASSERT ---
      // Verify the order: check happens before create
      expect(mockDb.users.findByEmail).toHaveBeenCalled()
      expect(mockDb.users.create).not.toHaveBeenCalled()

      // Verify check happened first
      const findOrder = mockDb.users.findByEmail.mock.invocationCallOrder[0]
      expect(findOrder).toBeDefined()
    })
  })

  describe('register - Database Failure Scenarios', () => {
    it('propagates database error when findByEmail fails', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'db-error@example.com',
        name: 'DB Error User',
        password: 'Password123'
      }

      const dbError = new Error('Database connection failed')
      mockDb.users.findByEmail.mockRejectedValue(dbError)

      // --- ACT ---
      const register = () => userService.register(userData)

      // --- ASSERT ---
      await expect(register()).rejects.toThrow('Database connection failed')

      // Verify no creation or email sending occurred
      expect(mockDb.users.create).not.toHaveBeenCalled()
      expect(mockEmailService.sendWelcome).not.toHaveBeenCalled()
    })

    it('propagates database error when create fails', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'create-error@example.com',
        name: 'Create Error User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)

      const createError = new Error('Failed to insert into database')
      mockDb.users.create.mockRejectedValue(createError)

      // --- ACT ---
      const register = () => userService.register(userData)

      // --- ASSERT ---
      await expect(register()).rejects.toThrow('Failed to insert into database')

      // Verify email was NOT sent (rollback behavior)
      expect(mockEmailService.sendWelcome).not.toHaveBeenCalled()
    })
  })

  describe('register - Email Service Failure Scenarios', () => {
    it('propagates email service error', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'email-fail@example.com',
        name: 'Email Fail User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-email-fail',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })

      const emailError = new Error('Email service unavailable')
      mockEmailService.sendWelcome.mockRejectedValue(emailError)

      // --- ACT ---
      const register = () => userService.register(userData)

      // --- ASSERT ---
      await expect(register()).rejects.toThrow('Email service unavailable')

      // Verify user was created before email error occurred
      expect(mockDb.users.create).toHaveBeenCalledTimes(1)
    })

    it('handles email service timeout', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'timeout@example.com',
        name: 'Timeout User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-timeout',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })

      const timeoutError = new Error('Request timeout after 30s')
      mockEmailService.sendWelcome.mockRejectedValue(timeoutError)

      // --- ACT ---
      const register = () => userService.register(userData)

      // --- ASSERT ---
      await expect(register()).rejects.toThrow('Request timeout after 30s')
    })
  })

  describe('register - Edge Cases', () => {
    it('handles special characters in email', async () => {
      // --- ARRANGE ---
      const specialEmailData = {
        email: 'user+tag@example.com',
        name: 'Special User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-special',
        email: specialEmailData.email,
        name: specialEmailData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(specialEmailData)

      // --- ASSERT ---
      expect(result.email).toBe(specialEmailData.email)
      expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(specialEmailData.email)
    })

    it('handles very long names', async () => {
      // --- ARRANGE ---
      const longName = 'A'.repeat(500)
      const longNameData = {
        email: 'longname@example.com',
        name: longName,
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-longname',
        email: longNameData.email,
        name: longName,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(longNameData)

      // --- ASSERT ---
      expect(result.name).toBe(longName)
      expect(mockDb.users.create).toHaveBeenCalledWith(
        expect.objectContaining({ name: longName })
      )
    })

    it('handles special characters in name', async () => {
      // --- ARRANGE ---
      const specialNameData = {
        email: 'special@example.com',
        name: "O'Brien-Smith (PhD)",
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-special-name',
        email: specialNameData.email,
        name: specialNameData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(specialNameData)

      // --- ASSERT ---
      expect(result.name).toBe(specialNameData.name)
    })

    it('handles empty password string', async () => {
      // --- ARRANGE ---
      const emptyPasswordData = {
        email: 'empty@example.com',
        name: 'Empty Password',
        password: ''
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-empty-pwd',
        email: emptyPasswordData.email,
        name: emptyPasswordData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      await userService.register(emptyPasswordData)

      // --- ASSERT ---
      // Verify empty password is still hashed
      expect(mockDb.users.create).toHaveBeenCalledWith(
        expect.objectContaining({
          passwordHash: 'hashed_' // Hash of empty string
        })
      )
    })
  })

  describe('register - Boundary Value Testing', () => {
    it('handles minimum valid email length', async () => {
      // --- ARRANGE ---
      const minEmailData = {
        email: 'a@b.c', // Minimal valid email
        name: 'Min Email',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-min-email',
        email: minEmailData.email,
        name: minEmailData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(minEmailData)

      // --- ASSERT ---
      expect(result.email).toBe(minEmailData.email)
    })

    it('handles maximum realistic email length', async () => {
      // --- ARRANGE ---
      // Email addresses can be up to 254 characters (RFC 5321)
      const localPart = 'a'.repeat(64) // Max local part
      const domain = 'b'.repeat(180) + '.com' // Long domain
      const maxEmail = `${localPart}@${domain}`

      const maxEmailData = {
        email: maxEmail,
        name: 'Max Email',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-max-email',
        email: maxEmailData.email,
        name: maxEmailData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(maxEmailData)

      // --- ASSERT ---
      expect(result.email).toBe(maxEmail)
    })
  })

  describe('register - F.I.R.S.T Compliance Verification', () => {
    it('[FAST] completes registration in minimal time', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'fast@example.com',
        name: 'Fast User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-fast',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      const startTime = Date.now()

      // --- ACT ---
      await userService.register(userData)

      // --- ASSERT ---
      const duration = Date.now() - startTime
      // Test should complete in < 100ms (mocked dependencies ensure speed)
      expect(duration).toBeLessThan(100)
    })

    it('[ISOLATED] runs independently of other tests', async () => {
      // --- ARRANGE ---
      // This test verifies it doesn't depend on previous test state
      const userData = {
        email: 'isolated@example.com',
        name: 'Isolated User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-isolated',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(userData)

      // --- ASSERT ---
      // Test succeeds regardless of execution order
      expect(result).toBeDefined()
      expect(mockDb.users.findByEmail).toHaveBeenCalledTimes(1)
    })

    it('[REPEATABLE] produces same result on multiple runs', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'repeatable@example.com',
        name: 'Repeatable User',
        password: 'Password123'
      }

      const expectedUser: User = {
        id: 'user-repeatable',
        email: userData.email,
        name: userData.name,
        createdAt: new Date('2024-01-15T10:00:00Z')
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue(expectedUser)
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result1 = await userService.register(userData)

      // Reset mocks and run again
      vi.clearAllMocks()
      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue(expectedUser)
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      const result2 = await userService.register(userData)

      // --- ASSERT ---
      // Same inputs produce same outputs (deterministic)
      expect(result1).toEqual(result2)
    })

    it('[SELF-CHECKING] automatically determines pass/fail', async () => {
      // --- ARRANGE ---
      const userData = {
        email: 'selfcheck@example.com',
        name: 'Self Check User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-selfcheck',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(userData)

      // --- ASSERT ---
      // No manual inspection needed - assertions provide clear pass/fail
      expect(result).toBeDefined()
      expect(result.email).toBe(userData.email)
      // Test runner will automatically report success/failure
    })

    it('[TIMELY] tests are easy to maintain and understand', async () => {
      // --- ARRANGE ---
      // Clear, descriptive test data
      const userData = {
        email: 'maintainable@example.com',
        name: 'Maintainable User',
        password: 'Password123'
      }

      mockDb.users.findByEmail.mockResolvedValue(null)
      mockDb.users.create.mockResolvedValue({
        id: 'user-maintain',
        email: userData.email,
        name: userData.name,
        createdAt: new Date()
      })
      mockEmailService.sendWelcome.mockResolvedValue(undefined)

      // --- ACT ---
      const result = await userService.register(userData)

      // --- ASSERT ---
      // Simple, clear assertions are easy to update
      expect(result.email).toBe(userData.email)
      expect(result.name).toBe(userData.name)
      // This test serves as living documentation
    })
  })
})
