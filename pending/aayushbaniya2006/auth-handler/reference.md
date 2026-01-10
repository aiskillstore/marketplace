# Auth Architecture Reference

## Key Files
- **Config**: `src/auth.ts` (NextAuth v5, Providers, Adapter)
- **Schema**: `src/db/schema/user.ts`
- **Middleware**: `src/proxy.ts` (Route protection)

## Helpers
- `src/lib/auth/withAuthRequired.ts`
- `src/lib/auth/withSuperAdminAuthRequired.ts`
- `src/lib/auth/cronAuthRequired.ts`
- `src/lib/users/useUser.ts` (Frontend hook)

## Best Practices
1. **Defense in Depth**: Middleware (`proxy.ts`) is the first layer, but route wrappers are mandatory.
2. **Database**: Update `src/db/schema/user.ts` for user model changes.
3. **Environment**: Check `AUTH_SECRET`, `GOOGLE_CLIENT_ID`, `SUPER_ADMIN_EMAILS`.

## Common Tasks
- **Debugging Login**: Check providers in `auth.ts`.
- **Impersonation**: Supported via custom Credentials provider.

