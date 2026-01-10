# Third-Party Library Typing

**Official Documentation:**
- [DefinitelyTyped Repository](https://github.com/DefinitelyTyped/DefinitelyTyped)
- [TypeScript Module Resolution](https://www.typescriptlang.org/docs/handbook/module-resolution.html)
- [TypeScript Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)

Complete guide for typing untyped third-party libraries.

---

## 1. Installing Type Definitions

```bash
# ✅ Check if @types package exists
npm install --save-dev @types/library-name

# Common type packages
npm install --save-dev @types/node
npm install --save-dev @types/react
npm install --save-dev @types/react-dom
npm install --save-dev @types/jest
npm install --save-dev @types/express
```

---

## 2. Creating Declaration Files

**Basic Declaration File:**

```typescript
// src/types/untyped-library.d.ts

// ✅ DO: Declare module for untyped library
declare module 'untyped-library' {
  export function doSomething(param: string): number
  export function doSomethingElse(param: number): string

  export interface Config {
    apiKey: string
    endpoint: string
  }

  export class Client {
    constructor(config: Config)
    request(path: string): Promise<unknown>
  }
}

// Usage
import { doSomething, Client } from 'untyped-library'

const result = doSomething('hello')  // Type: number
const client = new Client({ apiKey: 'key', endpoint: 'url' })
```

---

## 3. Augmenting Existing Types

**Extend Window Object:**

```typescript
// src/types/global.d.ts

// ✅ DO: Extend global Window interface
declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event',
      eventName: string,
      params?: Record<string, unknown>
    ) => void

    dataLayer: Array<Record<string, unknown>>

    analytics?: {
      track: (event: string, properties?: Record<string, unknown>) => void
    }
  }
}

export {}  // Make this a module

// Usage
window.gtag('event', 'click', { category: 'button' })
window.dataLayer.push({ event: 'pageview' })
window.analytics?.track('signup', { plan: 'pro' })
```

**Extend Process.env:**

```typescript
// src/types/env.d.ts

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test'
      DATABASE_URL: string
      OPENAI_API_KEY: string
      NEXT_PUBLIC_APP_URL: string
      JWT_SECRET: string
    }
  }
}

export {}

// Usage - now type-safe!
const dbUrl: string = process.env.DATABASE_URL
const apiKey: string = process.env.OPENAI_API_KEY
```

**Extend Module:**

```typescript
// src/types/express.d.ts

// ✅ DO: Add custom properties to Express Request
import { User } from '@/types/user'

declare global {
  namespace Express {
    interface Request {
      user?: User
      sessionId?: string
      startTime: number
    }
  }
}

export {}

// Usage in Express middleware
import { Request, Response } from 'express'

app.use((req: Request, res: Response, next) => {
  req.startTime = Date.now()
  next()
})

app.get('/profile', (req: Request, res: Response) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized' })
  }
  res.json(req.user)  // Type-safe!
})
```

---

## 4. Typing Untyped NPM Packages

**Complete Package Declaration:**

```typescript
// src/types/stripe-mock.d.ts

declare module 'stripe-mock' {
  export interface StripeConfig {
    apiKey: string
    apiVersion?: string
  }

  export interface Customer {
    id: string
    email: string
    name: string
    created: number
  }

  export interface PaymentIntent {
    id: string
    amount: number
    currency: string
    status: 'succeeded' | 'pending' | 'failed'
  }

  export class Stripe {
    constructor(apiKey: string, config?: StripeConfig)

    customers: {
      create: (params: {
        email: string
        name: string
      }) => Promise<Customer>

      retrieve: (id: string) => Promise<Customer>
    }

    paymentIntents: {
      create: (params: {
        amount: number
        currency: string
        customer?: string
      }) => Promise<PaymentIntent>

      confirm: (id: string) => Promise<PaymentIntent>
    }
  }

  export default Stripe
}

// Usage
import Stripe from 'stripe-mock'

const stripe = new Stripe('sk_test_...', { apiVersion: '2023-10-16' })

const customer = await stripe.customers.create({
  email: 'test@example.com',
  name: 'Test User'
})
// customer is typed as Customer
```

---

## 5. Typing JavaScript Libraries

**Library with Default Export:**

```typescript
// src/types/chart-library.d.ts

declare module 'chart-library' {
  export interface ChartOptions {
    type: 'line' | 'bar' | 'pie'
    data: {
      labels: string[]
      datasets: Array<{
        label: string
        data: number[]
        backgroundColor?: string
      }>
    }
    options?: {
      responsive?: boolean
      maintainAspectRatio?: boolean
    }
  }

  export default class Chart {
    constructor(canvas: HTMLCanvasElement, options: ChartOptions)
    update(): void
    destroy(): void
  }
}

// Usage
import Chart from 'chart-library'

const chart = new Chart(canvasElement, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Sales',
      data: [10, 20, 30]
    }]
  }
})
```

**Library with Named Exports:**

```typescript
// src/types/date-utils.d.ts

declare module 'date-utils' {
  export function formatDate(date: Date, format: string): string
  export function parseDate(dateString: string): Date
  export function addDays(date: Date, days: number): Date
  export function diffDays(start: Date, end: Date): number

  export const FORMAT_ISO: string
  export const FORMAT_US: string
  export const FORMAT_EU: string
}

// Usage
import { formatDate, FORMAT_ISO } from 'date-utils'

const formatted = formatDate(new Date(), FORMAT_ISO)
```

---

## 6. Typing CSS Modules

```typescript
// src/types/css-modules.d.ts

// ✅ DO: Type CSS modules
declare module '*.module.css' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.module.scss' {
  const classes: { [key: string]: string }
  export default classes
}

// Usage
import styles from './Button.module.css'

<button className={styles.primary}>
  Click me
</button>
// styles.primary is typed as string
```

---

## 7. Typing JSON Files

```typescript
// src/types/json.d.ts

// ✅ DO: Allow JSON imports
declare module '*.json' {
  const value: Record<string, unknown>
  export default value
}

// ✅ BETTER: Specific JSON structure
// src/types/config-json.d.ts
declare module '@/config/app.json' {
  interface AppConfig {
    appName: string
    version: string
    features: {
      analytics: boolean
      darkMode: boolean
    }
  }

  const config: AppConfig
  export default config
}

// Usage
import config from '@/config/app.json'

console.log(config.appName)  // Type-safe!
console.log(config.version)
```

---

## 8. Typing Image Imports

```typescript
// src/types/images.d.ts

// ✅ DO: Type image imports
declare module '*.png' {
  const content: string
  export default content
}

declare module '*.jpg' {
  const content: string
  export default content
}

declare module '*.svg' {
  const content: string
  export default content
}

// ✅ DO: SVG as React component (Next.js/Webpack)
declare module '*.svg' {
  import { FC, SVGProps } from 'react'
  const content: FC<SVGProps<SVGSVGElement>>
  export default content
}

// Usage
import logo from '@/assets/logo.png'
import Icon from '@/assets/icon.svg'

<img src={logo} alt="Logo" />
<Icon className="icon" />
```

---

## 9. Typing Global Variables

```typescript
// src/types/globals.d.ts

declare global {
  // Global constants
  const API_URL: string
  const APP_VERSION: string

  // Global functions (from CDN scripts)
  function trackEvent(name: string, data?: Record<string, unknown>): void

  // Global variables from build tools
  const __DEV__: boolean
  const __PROD__: boolean

  // Webpack specific
  const __webpack_public_path__: string

  // Vite specific
  const import.meta: {
    env: {
      MODE: string
      PROD: boolean
      DEV: boolean
      SSR: boolean
      [key: string]: string | boolean | undefined
    }
  }
}

export {}

// Usage
if (__DEV__) {
  console.log('Development mode')
}

trackEvent('page_view', { path: window.location.pathname })
```

---

## 10. Typing Utility Libraries

**Lodash (if @types/lodash not installed):**

```typescript
// src/types/lodash.d.ts

declare module 'lodash' {
  export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number,
    options?: {
      leading?: boolean
      trailing?: boolean
      maxWait?: number
    }
  ): T & { cancel: () => void }

  export function throttle<T extends (...args: any[]) => any>(
    func: T,
    wait: number,
    options?: {
      leading?: boolean
      trailing?: boolean
    }
  ): T & { cancel: () => void }

  export function get<T = any>(
    object: any,
    path: string | string[],
    defaultValue?: T
  ): T

  export function set<T extends object>(
    object: T,
    path: string | string[],
    value: any
  ): T

  export function cloneDeep<T>(value: T): T

  export function merge<T, U>(object: T, source: U): T & U

  export function isEqual(value: any, other: any): boolean
}

// Usage
import { debounce, get } from 'lodash'

const search = debounce((query: string) => {
  console.log(query)
}, 300)

const userName = get(user, 'profile.name', 'Unknown')
```

---

## 11. Typing Browser APIs

```typescript
// src/types/browser-apis.d.ts

// ✅ DO: Type experimental browser APIs
interface Navigator {
  // Web Share API
  share?: (data: {
    title?: string
    text?: string
    url?: string
  }) => Promise<void>

  // Clipboard API
  clipboard?: {
    writeText: (text: string) => Promise<void>
    readText: () => Promise<string>
  }

  // Battery API
  getBattery?: () => Promise<{
    charging: boolean
    level: number
    chargingTime: number
    dischargingTime: number
  }>
}

// File System Access API
interface Window {
  showOpenFilePicker?: (options?: {
    multiple?: boolean
    types?: Array<{
      description: string
      accept: Record<string, string[]>
    }>
  }) => Promise<FileSystemFileHandle[]>

  showSaveFilePicker?: (options?: {
    suggestedName?: string
    types?: Array<{
      description: string
      accept: Record<string, string[]>
    }>
  }) => Promise<FileSystemFileHandle>
}

interface FileSystemFileHandle {
  getFile(): Promise<File>
  createWritable(): Promise<FileSystemWritableFileStream>
}

interface FileSystemWritableFileStream extends WritableStream {
  write(data: BufferSource | Blob | string): Promise<void>
  close(): Promise<void>
}

// Usage
if (navigator.share) {
  await navigator.share({
    title: 'Check this out',
    url: window.location.href
  })
}

if (window.showSaveFilePicker) {
  const handle = await window.showSaveFilePicker({
    suggestedName: 'document.txt'
  })
  const writable = await handle.createWritable()
  await writable.write('Hello, world!')
  await writable.close()
}
```

---

## 12. Typing Node.js Modules

```typescript
// src/types/node-modules.d.ts

// ✅ DO: Type custom Node.js modules
declare module 'custom-crypto' {
  export function encrypt(data: string, key: string): string
  export function decrypt(encrypted: string, key: string): string
  export function hash(data: string, algorithm?: 'sha256' | 'sha512'): string
}

// ✅ DO: Type CommonJS modules
declare module 'legacy-module' {
  interface LegacyConfig {
    host: string
    port: number
  }

  class LegacyClient {
    constructor(config: LegacyConfig)
    connect(): Promise<void>
    disconnect(): void
  }

  export = LegacyClient
}

// Usage
import LegacyClient = require('legacy-module')

const client = new LegacyClient({ host: 'localhost', port: 3000 })
```

---

## 13. Creating Wrapper Functions

**When you can't modify the library:**

```typescript
// src/lib/typed-analytics.ts

// ✅ DO: Create type-safe wrapper
interface AnalyticsEvent {
  name: string
  properties?: Record<string, string | number | boolean>
  timestamp?: number
}

interface Analytics {
  track: (event: AnalyticsEvent) => void
  identify: (userId: string, traits?: Record<string, unknown>) => void
  page: (name: string) => void
}

// Assume window.analytics is untyped
export const analytics: Analytics = {
  track: (event: AnalyticsEvent) => {
    if (typeof window !== 'undefined' && 'analytics' in window) {
      ;(window as any).analytics.track(event.name, event.properties)
    }
  },

  identify: (userId: string, traits?: Record<string, unknown>) => {
    if (typeof window !== 'undefined' && 'analytics' in window) {
      ;(window as any).analytics.identify(userId, traits)
    }
  },

  page: (name: string) => {
    if (typeof window !== 'undefined' && 'analytics' in window) {
      ;(window as any).analytics.page(name)
    }
  }
}

// Usage - fully typed!
analytics.track({
  name: 'button_clicked',
  properties: { buttonId: 'signup', page: 'home' }
})

analytics.identify('user-123', { plan: 'pro' })
```

---

## 14. Typing GraphQL

```typescript
// src/types/graphql.d.ts

// ✅ DO: Type GraphQL operations
export interface User {
  id: string
  email: string
  name: string
  createdAt: string
}

export interface GetUserQuery {
  user: User | null
}

export interface GetUserVariables {
  id: string
}

export interface CreateUserMutation {
  createUser: User
}

export interface CreateUserVariables {
  email: string
  name: string
}

// Usage with Apollo Client
import { useQuery, useMutation } from '@apollo/client'
import { gql } from '@apollo/client'

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      email
      name
    }
  }
`

function UserProfile({ userId }: { userId: string }) {
  const { data } = useQuery<GetUserQuery, GetUserVariables>(GET_USER, {
    variables: { id: userId }
  })

  if (!data?.user) return null

  return <div>{data.user.name}</div>
}
```

---

## 15. tsconfig.json Configuration

```json
// tsconfig.json

{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,

    // Type declaration paths
    "typeRoots": [
      "./node_modules/@types",
      "./src/types"
    ],

    // Path aliases
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/types/*": ["./src/types/*"]
    }
  },
  "include": [
    "src/**/*",
    "src/types/**/*.d.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
```

---

## 16. Best Practices

**DO:**
- ✅ Create `.d.ts` files in `src/types/` directory
- ✅ Use `declare module` for third-party libraries
- ✅ Use `declare global` for global augmentations
- ✅ Add `export {}` to make global declarations work
- ✅ Install `@types/` packages when available
- ✅ Create type-safe wrappers for untyped libraries
- ✅ Document why types were added manually

**DON'T:**
- ❌ Use `any` as a shortcut
- ❌ Ignore missing type definitions
- ❌ Duplicate types already in DefinitelyTyped
- ❌ Forget to update types when library updates
- ❌ Mix type declarations with implementation

---

## Quick Reference

| Scenario | Solution | File Location |
|----------|----------|---------------|
| Untyped NPM package | `declare module 'package'` | `src/types/package.d.ts` |
| Extend Window | `declare global { interface Window }` | `src/types/global.d.ts` |
| CSS modules | `declare module '*.module.css'` | `src/types/css-modules.d.ts` |
| Image imports | `declare module '*.png'` | `src/types/images.d.ts` |
| JSON imports | `declare module '*.json'` | `src/types/json.d.ts` |
| Env variables | `namespace NodeJS { interface ProcessEnv }` | `src/types/env.d.ts` |
| Express Request | `namespace Express { interface Request }` | `src/types/express.d.ts` |
| Browser API | `interface Navigator` | `src/types/browser-apis.d.ts` |

---

## Testing Type Definitions

```typescript
// src/types/__tests__/type-tests.ts

// ✅ DO: Test type definitions compile
import { expectType } from 'tsd'

// Test window augmentation
expectType<Function>(window.gtag)

// Test env types
expectType<string>(process.env.DATABASE_URL)

// Test module types
import { doSomething } from 'untyped-library'
expectType<number>(doSomething('test'))

// Run with: npx tsd
```

**Test Requirements:**
- All type declarations must compile without errors
- Use `tsd` or similar for type testing
- Document usage examples in comments
- Keep types in sync with library updates
