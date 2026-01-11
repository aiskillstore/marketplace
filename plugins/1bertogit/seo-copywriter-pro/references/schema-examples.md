# Exemplos de Schema Markup

Schema JSON-LD prontos para cada tipo de página. Ajuda Google a entender e destacar seu conteúdo.

---

## 1. Schema: Person + Physician (Homepage/Sobre)

```json
{
  "@context": "https://schema.org",
  "@type": ["Person", "Physician"],
  "name": "[Nome Completo]",
  "alternateName": "[Título/Apelido - ex: Criador da Face Moderna]",
  "jobTitle": "[Especialidade]",
  "description": "[Descrição 1-2 frases com credenciais]",
  "image": "[URL da foto profissional]",
  "url": "[URL do site]",
  "sameAs": [
    "[LinkedIn URL]",
    "[Instagram URL]",
    "[YouTube URL]"
  ],
  "knowsAbout": [
    "[Especialidade 1]",
    "[Especialidade 2]",
    "[Especialidade 3]"
  ],
  "alumniOf": {
    "@type": "EducationalOrganization",
    "name": "[Universidade]"
  },
  "memberOf": {
    "@type": "Organization",
    "name": "[Sociedade/Instituto]"
  },
  "award": "[Prêmio ou reconhecimento]"
}
```

---

## 2. Schema: MedicalProcedure (Páginas de Técnica)

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalProcedure",
  "name": "[Nome da Técnica]",
  "alternateName": "[Nome alternativo se houver]",
  "procedureType": "Surgical",
  "bodyLocation": "[Parte do corpo - ex: Face - Terço Médio]",
  "description": "[Descrição do procedimento em 2-3 frases]",
  "howPerformed": "[Descrição breve de como é realizado]",
  "preparation": "[Preparação necessária]",
  "followup": "[Cuidados pós-procedimento]",
  "outcome": "[Resultados esperados]",
  "status": "https://schema.org/ActiveActionStatus"
}
```

---

## 3. Schema: Course (Páginas de Formação)

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "[Nome do Curso]",
  "description": "[Descrição do curso em 2-3 frases]",
  "provider": {
    "@type": "Organization",
    "name": "[Nome do Instituto/Escola]",
    "url": "[URL do site]"
  },
  "instructor": {
    "@type": "Person",
    "name": "[Nome do Instrutor]",
    "jobTitle": "[Título]"
  },
  "courseCode": "[Código se houver]",
  "educationalLevel": "[Nível - ex: Advanced]",
  "teaches": "[O que ensina]",
  "numberOfCredits": "[Horas/créditos se aplicável]",
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "[Online/Presencial/Híbrido]",
    "courseWorkload": "[Carga horária]"
  }
}
```

---

## 4. Schema: FAQPage (Seções de FAQ)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Pergunta 1]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Resposta completa para pergunta 1]"
      }
    },
    {
      "@type": "Question",
      "name": "[Pergunta 2]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Resposta completa para pergunta 2]"
      }
    },
    {
      "@type": "Question",
      "name": "[Pergunta 3]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Resposta completa para pergunta 3]"
      }
    }
  ]
}
```

---

## 5. Schema: MedicalWebPage (Artigos do Blog)

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalWebPage",
  "name": "[Título do Artigo]",
  "description": "[Meta description]",
  "url": "[URL do artigo]",
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "author": {
    "@type": "Person",
    "name": "[Nome do Autor]",
    "url": "[URL do perfil]"
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Nome do Site/Instituto]",
    "logo": {
      "@type": "ImageObject",
      "url": "[URL do logo]"
    }
  },
  "medicalAudience": {
    "@type": "MedicalAudience",
    "audienceType": "[Público - ex: Plastic Surgeons]"
  },
  "about": {
    "@type": "MedicalCondition",
    "name": "[Condição/tema abordado]"
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "[URL canônica]"
  }
}
```

---

## 6. Schema: BreadcrumbList (Navegação)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "[URL home]"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "[Seção]",
      "item": "[URL seção]"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[Página Atual]",
      "item": "[URL atual]"
    }
  ]
}
```

---

## 7. Schema: DefinedTerm (Glossário)

```json
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "[Termo]",
  "description": "[Definição do termo]",
  "inDefinedTermSet": {
    "@type": "DefinedTermSet",
    "name": "[Nome do Glossário]",
    "url": "[URL do glossário]"
  }
}
```

---

## 8. Schema: Organization (Rodapé/Sobre)

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalOrganization",
  "name": "[Nome do Instituto/Clínica]",
  "url": "[URL]",
  "logo": "[URL do logo]",
  "description": "[Descrição da organização]",
  "founder": {
    "@type": "Person",
    "name": "[Nome do Fundador]"
  },
  "foundingDate": "[YYYY]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Endereço]",
    "addressLocality": "[Cidade]",
    "addressRegion": "[Estado]",
    "postalCode": "[CEP]",
    "addressCountry": "[País]"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[Telefone]",
    "contactType": "[Tipo - ex: customer service]",
    "availableLanguage": ["Portuguese", "English", "Spanish"]
  },
  "sameAs": [
    "[LinkedIn]",
    "[Instagram]",
    "[YouTube]"
  ]
}
```

---

## Combinando Múltiplos Schemas

Para páginas que precisam de múltiplos schemas, use array:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      ...
    },
    {
      "@type": "FAQPage",
      ...
    },
    {
      "@type": "BreadcrumbList",
      ...
    }
  ]
}
```

---

## Implementação em Next.js

```tsx
// components/seo/SchemaMarkup.tsx
export function SchemaMarkup({ schema }: { schema: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}

// Uso em página
<SchemaMarkup schema={{
  "@context": "https://schema.org",
  "@type": "MedicalProcedure",
  "name": "Endomidface",
  // ...
}} />
```

---

## Validação

Sempre validar schemas em:
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)

Erros comuns a evitar:
- URLs relativas (usar sempre absolutas)
- Datas em formato errado (usar YYYY-MM-DD)
- Campos obrigatórios faltando
- HTML em campos de texto
