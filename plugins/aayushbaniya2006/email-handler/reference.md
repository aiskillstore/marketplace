# Email Architecture Reference

## Core Files
- **Templates**: `src/emails/*.tsx`
- **Base Layout**: `src/emails/components/Layout.tsx`
- **Sender Utility**: `src/lib/email/sendMail.ts`

## React Email Components
Common imports:
```tsx
import { 
  Html, 
  Button, 
  Text, 
  Heading, 
  Link, 
  Img, 
  Hr, 
  Container 
} from "@react-email/components";
```

## Sending Pattern
```typescript
const html = await render(Template({ prop: "value" }));
await sendMail(to, subject, html);
```

## Best Practices
1.  **Preview Text**: Always pass a `previewText` prop to `<Layout>`.
2.  **Type Safety**: Define explicit interfaces for Email Props.
3.  **Environment**: Use `process.env.NEXT_PUBLIC_APP_URL` for absolute links.
4.  **Styling**: Use `bg-primary`, `text-foreground`, `text-muted` to match app theme (defined in Layout).

