# p11 Components

p11 documents are React modules that export a default component and use only document-safe components from `@p11-core/components`.

## Basic Document

```tsx
import { Document, Heading, Section, Text } from "@p11-core/components";

export default function Proposal() {
  return (
    <Document>
      <Section>
        <Heading level={1}>Proposal</Heading>
        <Text>Write the document body here.</Text>
      </Section>
    </Document>
  );
}
```

## Supported Exports

```txt
Document
Page
Section
Heading
Text
List
ListItem
DefinitionList
DefinitionTerm
DefinitionDescription
Quote
Strikethrough
CodeBlock
Table
TableHeader
TableBody
TableRow
TableHead
TableCell
Figure
Caption
Divider
PageBreak
code
```

Use `code` with `CodeBlock` for readable multiline snippets.

`Document` accepts `mode?: "page" | "pageless"`. Pageless is the default screen view. Use `<PageBreak />` to force a new page.

Do not import or render app/control components such as `Alert`, `Badge`, `Button`, `Card`, `Separator`, `Stack`, `Tabs`, or `Accordion`.

Do not use native interactive tags inside authored content: `button`, `input`, `select`, `textarea`, `form`, or `nav`.
