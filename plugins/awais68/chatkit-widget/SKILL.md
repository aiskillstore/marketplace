---
name: chatkit-widget
description: |
  Use when integrating OpenAI/ChatKit chat widgets into Next.js/React applications.
  Triggers for: embedding chat widgets, configuring widget appearance, implementing event handlers,
  setting up authenticated chat access, or customizing widget branding.
  NOT for: building custom chat UIs from scratch or backend AI model configuration.
---

# ChatKit Widget Integration Skill

Expert integration of OpenAI/ChatKit chat widgets into Next.js/React applications with secure configuration and custom branding.

## Quick Reference

| Task | File/Component |
|------|----------------|
| Widget component | `components/chat/ChatWidget.tsx` |
| Configuration | `config/chatkit.config.ts` |
| Layout integration | `app/layout.tsx` or `pages/_app.tsx` |
| API proxy | `app/api/chatkit/route.ts` |

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── chatkit/
│   │       └── route.ts          # Secure API proxy
│   ├── components/
│   │   └── chat/
│   │       ├── ChatWidget.tsx    # Main widget component
│   │       └── ChatButton.tsx    # Custom trigger button
│   └── layout.tsx                # Root layout with widget
├── lib/
│   └── chatkit.ts                # Utility functions
└── config/
    └── chatkit.config.ts         # Widget configuration
```

## Widget Configuration

### Configuration File

```typescript
// frontend/config/chatkit.config.ts
import { ChatKitConfig } from "@/lib/chatkit";

interface ChatKitConfig {
  // Public configuration (safe to expose)
  projectId: string;
  publicKey: string;

  // Server-side configuration (fetched from API)
  apiUrl: string;

  // Branding
  theme: {
    primaryColor: string;
    secondaryColor: string;
    textColor: string;
    backgroundColor: string;
    borderRadius: string;
  };

  // Positioning
  position: {
    bottom: string;
    right: string;
    mobileBottom: string;
    mobileRight: string;
  };

  // Behavior
  behavior: {
    defaultOpen: boolean;
    showOnPages: string[]; // Glob patterns
    hideOnPages: string[]; // Glob patterns
    allowedRoles: string[]; // Empty = all users
  };

  // Content
  content: {
    welcomeMessage: string;
    placeholderText: string;
    headerTitle: string;
    headerSubtitle: string;
  };
}

export const chatkitConfig: ChatKitConfig = {
  // Public keys - these can be safely exposed
  projectId: process.env.NEXT_PUBLIC_CHATKIT_PROJECT_ID || "",
  publicKey: process.env.NEXT_PUBLIC_CHATKIT_PUBLIC_KEY || "",

  // API endpoint (server-side only)
  apiUrl: process.env.CHATKIT_API_URL || "https://api.chatkit.com",

  // Branding - school/ERP theme colors
  theme: {
    primaryColor: "#2563EB",      // School blue
    secondaryColor: "#1E40AF",    // Darker blue
    textColor: "#FFFFFF",
    backgroundColor: "#FFFFFF",
    borderRadius: "12px",
  },

  // Position - bottom right corner
  position: {
    bottom: "24px",
    right: "24px",
    mobileBottom: "16px",
    mobileRight: "16px",
  },

  // Behavior
  behavior: {
    defaultOpen: false,
    showOnPages: ["/**"],         // Show on all pages
    hideOnPages: ["/admin/**"],   // Hide on admin pages
    allowedRoles: [],             // Show to all roles
  },

  // Content
  content: {
    welcomeMessage: "Hi! How can I help you today?",
    placeholderText: "Type your question...",
    headerTitle: "ERP Support",
    headerSubtitle: "Ask us anything about grades, fees, or attendance",
  },
};
```

### Environment Variables

```bash
# .env.example

# Public variables (safe to expose in browser)
NEXT_PUBLIC_CHATKIT_PROJECT_ID="your-project-id"
NEXT_PUBLIC_CHATKIT_PUBLIC_KEY="your-public-key"

# Server-only variables (never expose to client)
CHATKIT_SECRET_KEY="your-secret-key"
CHATKIT_API_URL="https://api.chatkit.com/v2"
CHATKIT_BOT_ID="your-bot-id"

# Optional: Custom branding
NEXT_PUBLIC_CHATKIT_PRIMARY_COLOR="#2563EB"
```

## Widget Component

### Main Widget (Lazy Loaded)

```tsx
// frontend/components/chat/ChatWidget.tsx
"use client";

import { useEffect, useState, useCallback } from "react";
import { chatkitConfig } from "@/config/chatkit.config";

interface ChatWidgetProps {
  userRole?: string;
  userId?: string;
  userName?: string;
}

declare global {
  interface Window {
    ChatKit?: {
      init: (config: any) => void;
      destroy: () => void;
    };
  }
}

export function ChatWidget({
  userRole,
  userId,
  userName,
}: ChatWidgetProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isOpen, setIsOpen] = useState(chatkitConfig.behavior.defaultOpen);

  // Check if widget should be shown based on page and role
  const shouldShow = useCallback(() => {
    // Check role-based access
    if (
      chatkitConfig.behavior.allowedRoles.length > 0 &&
      !chatkitConfig.behavior.allowedRoles.includes(userRole || "")
    ) {
      return false;
    }

    return true;
  }, [userRole]);

  // Load ChatKit script dynamically
  useEffect(() => {
    if (!shouldShow()) return;

    const loadChatKit = () => {
      const script = document.createElement("script");
      script.src = `${chatkitConfig.apiUrl}/widget.js`;
      script.async = true;
      script.onload = () => {
        setIsLoaded(true);
        initializeWidget();
      };
      script.onerror = () => {
        console.error("Failed to load ChatKit widget");
      };
      document.body.appendChild(script);
    };

    loadChatKit();

    return () => {
      // Cleanup
      if (window.ChatKit) {
        window.ChatKit.destroy();
      }
      const existingScript = document.querySelector(
        'script[src*="widget.js"]'
      );
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, [shouldShow]);

  const initializeWidget = () => {
    if (!window.ChatKit) return;

    window.ChatKit.init({
      projectId: chatkitConfig.projectId,
      publicKey: chatkitConfig.publicKey,
      container: "#chatkit-container",
      theme: {
        primaryColor: chatkitConfig.theme.primaryColor,
        secondaryColor: chatkitConfig.theme.secondaryColor,
        textColor: chatkitConfig.theme.textColor,
        backgroundColor: chatkitConfig.theme.backgroundColor,
        borderRadius: chatkitConfig.theme.borderRadius,
      },
      user: {
        id: userId || "anonymous",
        name: userName || "Guest",
      },
      onOpen: () => {
        console.log("Chat opened");
        // Optional: Log analytics event
      },
      onClose: () => {
        console.log("Chat closed");
      },
      onMessage: (message: any) => {
        console.log("Message sent:", message);
        // Optional: Track conversation metrics
      },
      onError: (error: any) => {
        console.error("Chat error:", error);
      },
    });
  };

  if (!shouldShow()) return null;

  return (
    <div
      id="chatkit-container"
      className="fixed z-50"
      style={{
        bottom: chatkitConfig.position.bottom,
        right: chatkitConfig.position.right,
      }}
    >
      {/* Chat toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center w-14 h-14 rounded-full shadow-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2"
        style={{
          backgroundColor: chatkitConfig.theme.primaryColor,
          color: chatkitConfig.theme.textColor,
        }}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? (
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        )}
      </button>

      {/* Mobile considerations */}
      <style jsx global>{`
        @media (max-width: 768px) {
          #chatkit-container {
            bottom: ${chatkitConfig.position.mobileBottom} !important;
            right: ${chatkitConfig.position.mobileRight} !important;
          }
        }
      `}</style>
    </div>
  );
}

// Lazy load wrapper for Next.js
import dynamic from "next/dynamic";

export const LazyChatWidget = dynamic(
  () => import("./ChatWidget"),
  {
    loading: () => null,
    ssr: false, // Chat widget is client-only
  }
);
```

### Hook for Widget Control

```typescript
// frontend/hooks/useChatWidget.ts
import { useState, useCallback } from "react";

export function useChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const openChat = useCallback(() => {
    setIsOpen(true);
    setUnreadCount(0);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => {
      if (!prev) setUnreadCount(0);
      return !prev;
    });
  }, []);

  const incrementUnread = useCallback(() => {
    if (!isOpen) {
      setUnreadCount((prev) => prev + 1);
    }
  }, [isOpen]);

  return {
    isOpen,
    unreadCount,
    openChat,
    closeChat,
    toggleChat,
    incrementUnread,
  };
}
```

## Secure API Proxy

### Backend Proxy Route

```typescript
// frontend/app/api/chatkit/route.ts
import { NextRequest, NextResponse } from "next/server";

const CHATKIT_SECRET = process.env.CHATKIT_SECRET_KEY;
const CHATKIT_API_URL = process.env.CHATKIT_API_URL || "https://api.chatkit.com/v2";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { endpoint, method = "POST", payload } = body;

    // Validate endpoint (prevent SSRF)
    const allowedEndpoints = [
      "/messages",
      "/users",
      "/conversations",
    ];

    const isAllowed = allowedEndpoints.some((ep) =>
      endpoint.startsWith(ep)
    );

    if (!isAllowed) {
      return NextResponse.json(
        { error: "Invalid endpoint" },
        { status: 403 }
      );
    }

    // Make request to ChatKit API
    const response = await fetch(`${CHATKIT_API_URL}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${CHATKIT_SECRET}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("ChatKit proxy error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

## Layout Integration

### Root Layout (App Router)

```tsx
// frontend/app/layout.tsx
import { LazyChatWidget } from "@/components/chat/ChatWidget";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {children}

        {/* Chat widget - only on client side */}
        <LazyChatWidget
          userRole={session?.user?.role || "guest"}
          userId={session?.user?.id}
          userName={session?.user?.name}
        />
      </body>
    </html>
  );
}
```

### Page Router (_app.tsx)

```tsx
// frontend/pages/_app.tsx
import type { AppProps } from "next/app";
import { useSession } from "next-auth/react";
import { ChatWidget } from "@/components/chat/ChatWidget";

export default function App({ Component, pageProps }: AppProps) {
  const { data: session } = useSession();

  return (
    <>
      <Component {...pageProps} />
      <ChatWidget
        userRole={session?.user?.role || "guest"}
        userId={session?.user?.id}
        userName={session?.user?.name}
      />
    </>
  );
}
```

## Role-Based Chat Access

```typescript
// frontend/components/chat/RoleBasedChat.tsx
import { LazyChatWidget } from "./ChatWidget";
import { useSession } from "next-auth/react";

export function RoleBasedChat() {
  const { data: session } = useSession();

  // Define role-based chat settings
  const roleConfig: Record<string, { enabled: boolean; welcomeMsg: string }> = {
    admin: {
      enabled: true,
      welcomeMsg: "Welcome, Admin! Need help with system management?",
    },
    teacher: {
      enabled: true,
      welcomeMsg: "Hello! How can I help with your classes today?",
    },
    student: {
      enabled: true,
      welcomeMsg: "Hi! Ask me about grades, homework, or campus info.",
    },
    parent: {
      enabled: true,
      welcomeMsg: "Welcome! I'm here to help with your child's progress.",
    },
    guest: {
      enabled: true,
      welcomeMsg: "Welcome! How can we help you today?",
    },
  };

  const role = session?.user?.role || "guest";
  const config = roleConfig[role] || roleConfig.guest;

  if (!config.enabled) return null;

  return (
    <LazyChatWidget
      userRole={role}
      userId={session?.user?.id}
      userName={session?.user?.name}
    />
  );
}
```

## Dark Mode Support

```typescript
// frontend/components/chat/DarkModeChat.tsx
"use client";

import { useTheme } from "next-themes";
import { chatkitConfig } from "@/config/chatkit.config";

export function DarkModeChat() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const darkTheme = {
    ...chatkitConfig.theme,
    primaryColor: "#3B82F6",
    secondaryColor: "#1D4ED8",
    backgroundColor: "#1F2937",
    textColor: "#F9FAFB",
  };

  const effectiveTheme = isDark ? darkTheme : chatkitConfig.theme;

  // ... rest of component using effectiveTheme
  return null; // Placeholder
}
```

## Event Handling

```typescript
// frontend/lib/chatkit-events.ts
import { useEffect } from "react";

interface ChatEventHandlers {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: ChatMessage) => void;
  onError?: (error: Error) => void;
}

interface ChatMessage {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export function useChatEvents(handlers: ChatEventHandlers) {
  useEffect(() => {
    // Set up global event listeners for ChatKit
    const handleChatOpen = () => handlers.onOpen?.();
    const handleChatClose = () => handlers.onClose?.();

    window.addEventListener("chatkit:open", handleChatOpen);
    window.addEventListener("chatkit:close", handleChatClose);

    return () => {
      window.removeEventListener("chatkit:open", handleChatOpen);
      window.removeEventListener("chatkit:close", handleChatClose);
    };
  }, [handlers]);
}

// Usage in component
export function ChatWithAnalytics() {
  const handleOpen = () => {
    // Log to analytics
    console.log("Chat opened - track in GA/PostHog");
  };

  const handleMessage = (message: ChatMessage) => {
    // Track conversation
    if (message.sender === "user") {
      console.log("User sent message:", message.text);
    }
  };

  useChatEvents({
    onOpen: handleOpen,
    onMessage: handleMessage,
  });

  return <ChatWidget />;
}
```

## Quality Checklist

- [ ] **Mobile-friendly**: Widget doesn't overlap content (proper z-index, positioning)
- [ ] **No hardcoded API keys**: All secrets from environment variables
- [ ] **Dark mode compatible**: Theme adjusts to system preference
- [ ] **Performance**: Widget lazy-loaded, doesn't block core content
- [ ] **SSR-safe**: Dynamic imports with ssr: false
- [ ] **Role-based access**: Only authorized users see widget
- [ ] **Privacy-compliant**: Minimal event logging, no PII in logs

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@frontend-nextjs-app-router` | Layout integration, dynamic imports |
| `@tailwind-css` | Styling, dark mode support |
| `@env-config` | Environment variables management |
| `@auth-integration` | Role-based access control |
| `@error-handling` | Error boundaries for widget errors |

## Customization Examples

### School Branding

```typescript
// Custom school theme
export const schoolTheme = {
  primaryColor: "#8B0000", // School maroon
  secondaryColor: "#FFD700", // Gold accents
  textColor: "#FFFFFF",
  backgroundColor: "#FFFFFF",
  borderRadius: "8px",
  fontFamily: "School Serif, Georgia, serif",
  logoUrl: "/images/school-logo.png",
};
```

### Helpdesk-Specific

```typescript
// Helpdesk configuration
export const helpdeskConfig = {
  welcomeMessage: "Welcome to the Help Desk! How can we assist you?",
  headerTitle: "IT Help Desk",
  headerSubtitle: "Technical support for students and staff",
  categories: [
    { id: "network", label: "Network Issues" },
    { id: "software", label: "Software Problems" },
    { id: "hardware", label: "Hardware Support" },
  ],
};
```

## Documentation Template

```markdown
# ChatKit Widget Usage Guide

## Adding to New Pages

The widget is automatically included in the root layout. To conditionally show/hide:

```tsx
import { ChatWidget } from "@/components/chat/ChatWidget";

function SupportPage() {
  return (
    <div>
      <h1>Support</h1>
      <ChatWidget userRole="student" />
    </div>
  );
}
```

## Customizing for Your Portal

Edit `config/chatkit.config.ts` to customize:

- Colors: Match your school's brand
- Position: Bottom-right is default, adjust for mobile
- Content: Welcome message, header text

## Troubleshooting

### Widget not loading
- Check browser console for errors
- Verify NEXT_PUBLIC_CHATKIT_PROJECT_ID is set
- Ensure API keys are correct

### Widget overlapping content
- Adjust z-index in ChatWidget component
- Check mobile positioning settings

### Dark mode not working
- Verify next-themes is configured
- Check darkTheme object in config
```
