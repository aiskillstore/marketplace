/**
 * Rate Limiter with LRU Eviction
 *
 * Per-session rate limiting to prevent abuse while avoiding memory exhaustion.
 * Uses LRU (Least Recently Used) eviction when session count exceeds limit.
 */

interface RateLimitConfig {
  maxRequestsPerHour: number;
  maxRequestsPerDay: number;
  maxSessions: number;  // LRU eviction threshold
}

interface UsageRecord {
  hourlyCount: number;
  dailyCount: number;
  hourlyReset: number;  // Timestamp
  dailyReset: number;   // Timestamp
  lastAccess: number;   // For LRU eviction
}

const DEFAULT_CONFIG: RateLimitConfig = {
  maxRequestsPerHour: 60,
  maxRequestsPerDay: 200,
  maxSessions: 10000,  // Prevent memory exhaustion
};

// Session usage tracking
const usageMap = new Map<string, UsageRecord>();

let config = { ...DEFAULT_CONFIG };

/**
 * Configure rate limits
 */
export function configureRateLimits(newConfig: Partial<RateLimitConfig>): void {
  config = { ...config, ...newConfig };
}

/**
 * Get or create usage record for a session
 */
function getOrCreateUsage(sessionId: string): UsageRecord {
  const now = Date.now();

  let usage = usageMap.get(sessionId);

  if (!usage) {
    // LRU eviction if at capacity
    if (usageMap.size >= config.maxSessions) {
      evictLeastRecentlyUsed();
    }

    usage = {
      hourlyCount: 0,
      dailyCount: 0,
      hourlyReset: now + 60 * 60 * 1000,   // 1 hour from now
      dailyReset: now + 24 * 60 * 60 * 1000, // 24 hours from now
      lastAccess: now,
    };
    usageMap.set(sessionId, usage);
  }

  // Reset counters if windows have passed
  if (now >= usage.hourlyReset) {
    usage.hourlyCount = 0;
    usage.hourlyReset = now + 60 * 60 * 1000;
  }

  if (now >= usage.dailyReset) {
    usage.dailyCount = 0;
    usage.dailyReset = now + 24 * 60 * 60 * 1000;
  }

  // Update last access for LRU
  usage.lastAccess = now;

  return usage;
}

/**
 * Evict the least recently used session
 */
function evictLeastRecentlyUsed(): void {
  let oldestKey: string | null = null;
  let oldestTime = Infinity;

  for (const [key, usage] of usageMap) {
    if (usage.lastAccess < oldestTime) {
      oldestTime = usage.lastAccess;
      oldestKey = key;
    }
  }

  if (oldestKey) {
    usageMap.delete(oldestKey);
    console.log(`[RateLimiter] Evicted LRU session: ${oldestKey.slice(0, 8)}...`);
  }
}

/**
 * Check if a session is within rate limits
 */
export function checkRateLimit(sessionId: string): {
  allowed: boolean;
  message?: string;
  remaining?: number;
} {
  const usage = getOrCreateUsage(sessionId);

  // Check hourly limit
  if (usage.hourlyCount >= config.maxRequestsPerHour) {
    const resetIn = Math.ceil((usage.hourlyReset - Date.now()) / 60000);
    return {
      allowed: false,
      message: `Hourly limit reached (${config.maxRequestsPerHour} requests). Resets in ${resetIn} minutes.`,
      remaining: 0,
    };
  }

  // Check daily limit
  if (usage.dailyCount >= config.maxRequestsPerDay) {
    const resetIn = Math.ceil((usage.dailyReset - Date.now()) / 3600000);
    return {
      allowed: false,
      message: `Daily limit reached (${config.maxRequestsPerDay} requests). Resets in ${resetIn} hours.`,
      remaining: 0,
    };
  }

  return {
    allowed: true,
    remaining: Math.min(
      config.maxRequestsPerHour - usage.hourlyCount,
      config.maxRequestsPerDay - usage.dailyCount
    ),
  };
}

/**
 * Increment usage counter after successful request
 */
export function incrementUsage(sessionId: string): void {
  const usage = getOrCreateUsage(sessionId);
  usage.hourlyCount++;
  usage.dailyCount++;
}

/**
 * Get usage statistics for a session
 */
export function getUsageStats(sessionId: string): {
  hourlyUsed: number;
  hourlyLimit: number;
  dailyUsed: number;
  dailyLimit: number;
  hourlyResetsIn: number;  // minutes
  dailyResetsIn: number;   // hours
} {
  const usage = getOrCreateUsage(sessionId);
  const now = Date.now();

  return {
    hourlyUsed: usage.hourlyCount,
    hourlyLimit: config.maxRequestsPerHour,
    dailyUsed: usage.dailyCount,
    dailyLimit: config.maxRequestsPerDay,
    hourlyResetsIn: Math.max(0, Math.ceil((usage.hourlyReset - now) / 60000)),
    dailyResetsIn: Math.max(0, Math.ceil((usage.dailyReset - now) / 3600000)),
  };
}

/**
 * Clean up expired sessions (call periodically)
 */
export function cleanupExpiredSessions(): number {
  const now = Date.now();
  const expiredThreshold = 24 * 60 * 60 * 1000; // 24 hours
  let cleaned = 0;

  for (const [key, usage] of usageMap) {
    if (now - usage.lastAccess > expiredThreshold) {
      usageMap.delete(key);
      cleaned++;
    }
  }

  if (cleaned > 0) {
    console.log(`[RateLimiter] Cleaned up ${cleaned} expired sessions`);
  }

  return cleaned;
}

/**
 * Get current session count (for monitoring)
 */
export function getSessionCount(): number {
  return usageMap.size;
}

// Optional: Run cleanup every hour
if (typeof setInterval !== 'undefined') {
  setInterval(cleanupExpiredSessions, 60 * 60 * 1000);
}
