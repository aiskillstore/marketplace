// user-service.ts
export interface User {
  id: string
  email: string
  name: string
  createdAt: Date
}

export class UserService {
  constructor(
    private db: { users: { create(data: any): Promise<User>; findByEmail(email: string): Promise<User | null> } },
    private emailService: { sendWelcome(email: string): Promise<void> }
  ) {}

  async register(data: { email: string; name: string; password: string }): Promise<User> {
    // Validate email
    if (!data.email.includes('@')) {
      throw new Error('Invalid email format')
    }

    // Check if user exists
    const existing = await this.db.users.findByEmail(data.email)
    if (existing) {
      throw new Error('Email already exists')
    }

    // Create user
    const user = await this.db.users.create({
      email: data.email,
      name: data.name,
      passwordHash: this.hashPassword(data.password),
      createdAt: new Date()
    })

    // Send welcome email
    await this.emailService.sendWelcome(user.email)

    return user
  }

  private hashPassword(password: string): string {
    // Simplified - in reality use bcrypt
    return `hashed_${password}`
  }
}
