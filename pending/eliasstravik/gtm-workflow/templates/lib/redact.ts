const SECRET_NAME = /_(?:KEY|TOKEN|SECRET)$/i;
const SENSITIVE_ASSIGNMENT =
  /((?:["']?(?:api[_-]?key|apikey|key|token|secret|password|authorization)["']?)\s*[:=]\s*)(["']?)([^\s,;&"']+)(["']?)/gi;

export function redact(value: unknown): string {
  let text = value instanceof Error ? value.message : String(value ?? "");

  text = text.replace(/https?:\/\/[^\s"'<>]+/gi, (candidate) => {
    try {
      const url = new URL(candidate);
      url.search = "";
      return url.toString();
    } catch {
      return candidate.replace(/\?.*$/, "");
    }
  });
  text = text.replace(/\bBearer\s+[^\s,;]+/gi, "Bearer [REDACTED]");
  text = text.replace(
    SENSITIVE_ASSIGNMENT,
    (_match, prefix: string, quote: string) => `${prefix}${quote}[REDACTED]${quote}`,
  );

  const environmentSecrets = Object.entries(process.env)
    .filter(([name, secret]) => SECRET_NAME.test(name) && Boolean(secret))
    .map(([, secret]) => secret!)
    .sort((left, right) => right.length - left.length);
  for (const secret of environmentSecrets) text = text.replaceAll(secret, "[REDACTED]");

  return text.slice(0, 500);
}

export function redactValue(value: unknown): unknown {
  if (typeof value === "string") return redact(value);
  if (Array.isArray(value)) return value.map(redactValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, redactValue(item)]),
    );
  }
  return value;
}

export function redactedError(error: unknown): Error {
  const sanitized = new Error(redact(error));
  if (error && typeof error === "object") {
    sanitized.name = String((error as { name?: unknown }).name ?? "Error");
    for (const key of ["providerErrorKind", "stepName", "code"] as const) {
      const value = (error as Record<string, unknown>)[key];
      if (value !== undefined) (sanitized as unknown as Record<string, unknown>)[key] = value;
    }
  }
  return sanitized;
}
