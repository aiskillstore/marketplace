# Stack Técnica - Astro 5.x

Configuração técnica padrão para projetos SEO seguindo metodologia James/Diesel Dudes.

---

## Stack Principal

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Astro** | 5.x | Framework principal (SSG/SSR) |
| **React** | 18.x | Islands interativos |
| **Tailwind CSS** | 3.x | Estilização utilitária |
| **styled-components** | 6.x | Componentes React estilizados |
| **Swiper** | 11.x | Carrosséis e sliders |

---

## Configuração Inicial

### 1. Criar Projeto Astro

```bash
# Criar projeto
npm create astro@latest drroberiobrandao-site

# Entrar no projeto
cd drroberiobrandao-site

# Instalar dependências principais
npm install @astrojs/react @astrojs/tailwind @astrojs/sitemap
npm install react react-dom
npm install styled-components
npm install swiper
npm install -D tailwindcss postcss autoprefixer
```

### 2. Configurar astro.config.mjs

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://drroberiobrandao.com',
  integrations: [
    react(),
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap({
      i18n: {
        defaultLocale: 'pt-BR',
        locales: {
          'pt-BR': 'pt-BR',
          'en': 'en',
          'es': 'es',
        },
      },
    }),
  ],
  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR', 'en', 'es'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  vite: {
    ssr: {
      noExternal: ['styled-components'],
    },
  },
});
```

### 3. Configurar tailwind.config.mjs

```javascript
// tailwind.config.mjs
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Cores da marca Face Moderna
        primary: {
          50: '#e8eef5',
          100: '#c5d5e8',
          200: '#9eb9d9',
          300: '#779dca',
          400: '#5987be',
          500: '#1e3a5f', // Azul principal
          600: '#1a3354',
          700: '#152b47',
          800: '#11233a',
          900: '#0a1525',
        },
        accent: {
          50: '#faf6eb',
          100: '#f2e9cc',
          200: '#e9d9a9',
          300: '#dfc986',
          400: '#d4b96d',
          500: '#c9a961', // Dourado accent
          600: '#b89750',
          700: '#9a7d42',
          800: '#7c6435',
          900: '#5e4b28',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
```

### 4. Configurar postcss.config.cjs

```javascript
// postcss.config.cjs
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

---

## Estrutura de Pastas

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   └── Navigation.astro
│   ├── ui/
│   │   ├── Button.astro
│   │   ├── Card.astro
│   │   ├── CTA.astro
│   │   └── DataCard.astro
│   ├── seo/
│   │   ├── SEOHead.astro
│   │   ├── SchemaMarkup.astro
│   │   └── Analytics.astro
│   └── islands/
│       ├── Carousel.tsx        # client:load
│       ├── MobileMenu.tsx      # client:load
│       ├── ContactForm.tsx     # client:idle
│       └── GlossarySearch.tsx  # client:load
├── layouts/
│   └── BaseLayout.astro
├── pages/
│   ├── index.astro                    # pt-BR (default)
│   ├── sobre.astro
│   ├── face-moderna/
│   │   ├── index.astro
│   │   └── pilares.astro
│   ├── tecnicas/
│   │   ├── index.astro
│   │   ├── endomidface.astro
│   │   ├── browlift.astro
│   │   └── deep-neck.astro
│   ├── formacao/
│   │   └── index.astro
│   ├── blog/
│   │   ├── index.astro
│   │   └── [...slug].astro
│   ├── glossario/
│   │   ├── index.astro
│   │   └── [termo].astro
│   ├── faq.astro
│   └── [lang]/                        # i18n (en, es)
│       ├── index.astro
│       ├── about.astro
│       ├── modern-face/
│       │   └── index.astro
│       ├── techniques/
│       │   ├── index.astro
│       │   ├── endomidface.astro
│       │   ├── browlift.astro
│       │   └── deep-neck.astro
│       ├── training/
│       │   └── index.astro
│       ├── blog/
│       │   ├── index.astro
│       │   └── [...slug].astro
│       └── glossary/
│           └── index.astro
├── content/
│   ├── config.ts
│   └── blog/
│       ├── pt/
│       │   └── *.mdx
│       ├── en/
│       │   └── *.mdx
│       └── es/
│           └── *.mdx
├── data/
│   ├── glossary.json
│   ├── testimonials.json
│   └── faq.json
├── locales/
│   ├── pt-BR.json
│   ├── en.json
│   └── es.json
├── styles/
│   └── global.css
└── lib/
    ├── i18n.ts
    ├── utils.ts
    └── getStaticPaths.ts

public/
├── fonts/
│   └── *.woff2
├── images/
│   ├── og/
│   ├── blog/
│   └── techniques/
├── robots.txt
└── favicon.svg
```

---

## Google Fonts (Self-Hosted)

### Configurar Fontes (src/styles/global.css)

```css
/* src/styles/global.css */

/* Font Face Declarations - Self-hosted Inter */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/inter-latin-400.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('/fonts/inter-latin-500.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/inter-latin-600.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/fonts/inter-latin-700.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}

/* Tailwind Base */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Base Styles */
@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
    scroll-behavior: smooth;
  }
  
  body {
    @apply bg-white text-gray-800 antialiased;
  }
}
```

### Preload Fonts no Head

```astro
<!-- No SEOHead.astro ou BaseLayout.astro -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />

<!-- Preload critical fonts -->
<link 
  rel="preload" 
  href="/fonts/inter-latin-400.woff2" 
  as="font" 
  type="font/woff2" 
  crossorigin 
/>
<link 
  rel="preload" 
  href="/fonts/inter-latin-600.woff2" 
  as="font" 
  type="font/woff2" 
  crossorigin 
/>
```

---

## GA4 + Google Tag Manager

### Criar arquivo de configuração (.env)

```bash
# .env
PUBLIC_GA4_ID=G-XXXXXXXXXX
PUBLIC_GTM_ID=GTM-XXXXXXX
```

### Componente Analytics (src/components/seo/Analytics.astro)

```astro
---
// src/components/seo/Analytics.astro
const GA4_ID = import.meta.env.PUBLIC_GA4_ID;
const GTM_ID = import.meta.env.PUBLIC_GTM_ID;
---

{GA4_ID && (
  <>
    <!-- Google Analytics 4 -->
    <script async src={`https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`}></script>
    <script define:vars={{ GA4_ID }}>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', GA4_ID, {
        page_path: window.location.pathname,
      });
    </script>
  </>
)}

{GTM_ID && (
  <>
    <!-- Google Tag Manager -->
    <script define:vars={{ GTM_ID }}>
      (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
      })(window,document,'script','dataLayer',GTM_ID);
    </script>
  </>
)}
```

### GTM Noscript (no body)

```astro
<!-- Adicionar logo após <body> no BaseLayout.astro -->
{GTM_ID && (
  <noscript>
    <iframe 
      src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`}
      height="0" 
      width="0" 
      style="display:none;visibility:hidden"
    ></iframe>
  </noscript>
)}
```

---

## SEO Head Completo

### Componente SEOHead.astro

```astro
---
// src/components/seo/SEOHead.astro
interface Props {
  title: string;
  description: string;
  keywords?: string[];
  canonicalUrl?: string;
  ogImage?: string;
  ogType?: 'website' | 'article';
  locale?: string;
  alternateLocales?: { locale: string; url: string }[];
  article?: {
    publishedTime?: string;
    modifiedTime?: string;
    author?: string;
    section?: string;
    tags?: string[];
  };
  noindex?: boolean;
}

const {
  title,
  description,
  keywords = [],
  canonicalUrl,
  ogImage = '/images/og/default.jpg',
  ogType = 'website',
  locale = 'pt_BR',
  alternateLocales = [],
  article,
  noindex = false,
} = Astro.props;

const siteUrl = 'https://drroberiobrandao.com';
const fullCanonical = canonicalUrl ? `${siteUrl}${canonicalUrl}` : Astro.url.href;
const fullOgImage = ogImage.startsWith('http') ? ogImage : `${siteUrl}${ogImage}`;
---

<!-- Primary Meta Tags -->
<title>{title}</title>
<meta name="title" content={title} />
<meta name="description" content={description} />
{keywords.length > 0 && <meta name="keywords" content={keywords.join(', ')} />}
{noindex && <meta name="robots" content="noindex, nofollow" />}

<!-- Canonical -->
<link rel="canonical" href={fullCanonical} />

<!-- Alternate Languages -->
{alternateLocales.map(({ locale, url }) => (
  <link rel="alternate" hreflang={locale} href={`${siteUrl}${url}`} />
))}
<link rel="alternate" hreflang="x-default" href={fullCanonical} />

<!-- Open Graph / Facebook -->
<meta property="og:type" content={ogType} />
<meta property="og:url" content={fullCanonical} />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={fullOgImage} />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:locale" content={locale} />
<meta property="og:site_name" content="Dr. Robério Brandão" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:url" content={fullCanonical} />
<meta name="twitter:title" content={title} />
<meta name="twitter:description" content={description} />
<meta name="twitter:image" content={fullOgImage} />

<!-- Article specific (for blog posts) -->
{article && (
  <>
    {article.publishedTime && <meta property="article:published_time" content={article.publishedTime} />}
    {article.modifiedTime && <meta property="article:modified_time" content={article.modifiedTime} />}
    {article.author && <meta property="article:author" content={article.author} />}
    {article.section && <meta property="article:section" content={article.section} />}
    {article.tags?.map(tag => <meta property="article:tag" content={tag} />)}
  </>
)}

<!-- Preload Critical Assets -->
<link rel="preload" href="/fonts/inter-latin-400.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/fonts/inter-latin-600.woff2" as="font" type="font/woff2" crossorigin />

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
```

---

## Schema Markup (JSON-LD)

### Componente SchemaMarkup.astro

```astro
---
// src/components/seo/SchemaMarkup.astro
interface Props {
  schema: object | object[];
}

const { schema } = Astro.props;

const schemaData = Array.isArray(schema)
  ? { "@context": "https://schema.org", "@graph": schema }
  : { "@context": "https://schema.org", ...schema };
---

<script type="application/ld+json" set:html={JSON.stringify(schemaData)} />
```

### Exemplo de uso com Article Schema

```astro
---
import SchemaMarkup from '@/components/seo/SchemaMarkup.astro';

const articleSchema = {
  "@type": "Article",
  "headline": "Cirurgia Facial com Bioestimuladores",
  "description": "Guia completo sobre cirurgia facial...",
  "image": "https://drroberiobrandao.com/images/article.jpg",
  "datePublished": "2024-12-14",
  "dateModified": "2024-12-14",
  "author": {
    "@type": "Person",
    "name": "Dr. Robério Brandão",
    "url": "https://drroberiobrandao.com/sobre/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Face Moderna",
    "logo": {
      "@type": "ImageObject",
      "url": "https://drroberiobrandao.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://drroberiobrandao.com/blog/bioestimuladores/"
  }
};
---

<SchemaMarkup schema={articleSchema} />
```

---

## React Islands com Swiper

### Componente Carousel.tsx

```tsx
// src/components/islands/Carousel.tsx
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import styled from 'styled-components';

// Import Swiper styles
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

interface Slide {
  image: string;
  title: string;
  description?: string;
}

interface CarouselProps {
  slides: Slide[];
  autoplay?: boolean;
}

const CarouselWrapper = styled.div`
  .swiper {
    width: 100%;
    padding-bottom: 50px;
  }
  
  .swiper-pagination-bullet-active {
    background: #1e3a5f;
  }
  
  .swiper-button-next,
  .swiper-button-prev {
    color: #1e3a5f;
  }
`;

const SlideContent = styled.div`
  text-align: center;
  padding: 20px;
  
  img {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 12px;
  }
  
  h3 {
    margin-top: 16px;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e3a5f;
  }
  
  p {
    margin-top: 8px;
    color: #6b7280;
  }
`;

export default function Carousel({ slides, autoplay = true }: CarouselProps) {
  return (
    <CarouselWrapper>
      <Swiper
        modules={[Navigation, Pagination, Autoplay]}
        spaceBetween={30}
        slidesPerView={1}
        navigation
        pagination={{ clickable: true }}
        autoplay={autoplay ? { delay: 5000, disableOnInteraction: false } : false}
        breakpoints={{
          640: { slidesPerView: 2 },
          1024: { slidesPerView: 3 },
        }}
      >
        {slides.map((slide, index) => (
          <SwiperSlide key={index}>
            <SlideContent>
              <img 
                src={slide.image} 
                alt={slide.title}
                loading={index === 0 ? "eager" : "lazy"}
              />
              <h3>{slide.title}</h3>
              {slide.description && <p>{slide.description}</p>}
            </SlideContent>
          </SwiperSlide>
        ))}
      </Swiper>
    </CarouselWrapper>
  );
}
```

### Uso do Island no Astro

```astro
---
// src/pages/index.astro
import BaseLayout from '@/layouts/BaseLayout.astro';
import Carousel from '@/components/islands/Carousel';

const testimonials = [
  {
    image: '/images/testimonial-1.jpg',
    title: 'Dra. Maria Silva',
    description: 'Transformou minha prática cirúrgica',
  },
  {
    image: '/images/testimonial-2.jpg',
    title: 'Dr. João Santos',
    description: 'Resultados consistentes desde o primeiro caso',
  },
];
---

<BaseLayout>
  <section class="py-20">
    <h2 class="text-3xl font-bold text-center mb-12">Depoimentos</h2>
    
    <!-- React Island com client:load para interatividade -->
    <Carousel 
      client:load 
      slides={testimonials} 
      autoplay={true} 
    />
  </section>
</BaseLayout>
```

---

## Performance: Imagens com fetchpriority

```astro
---
// Hero image com alta prioridade
---

<!-- LCP Image - Alta prioridade -->
<img 
  src="/images/hero-dr-roberio.jpg"
  alt="Dr. Robério Brandão - Criador da Face Moderna"
  width="800"
  height="600"
  fetchpriority="high"
  decoding="async"
  class="w-full h-auto"
/>

<!-- Imagens below the fold - Lazy loading -->
<img 
  src="/images/technique-preview.jpg"
  alt="Técnica Endomidface"
  width="400"
  height="300"
  loading="lazy"
  decoding="async"
  class="w-full h-auto"
/>
```

---

## Scripts package.json

```json
{
  "name": "drroberiobrandao-site",
  "type": "module",
  "version": "1.0.0",
  "scripts": {
    "dev": "astro dev",
    "start": "astro dev",
    "build": "astro check && astro build",
    "preview": "astro preview",
    "astro": "astro",
    "sitemap": "astro build && echo 'Sitemap generated at dist/sitemap-index.xml'",
    "lint": "eslint src --ext .ts,.tsx,.astro",
    "format": "prettier --write ."
  },
  "dependencies": {
    "@astrojs/react": "^3.x",
    "@astrojs/sitemap": "^3.x",
    "@astrojs/tailwind": "^5.x",
    "astro": "^5.x",
    "react": "^18.x",
    "react-dom": "^18.x",
    "styled-components": "^6.x",
    "swiper": "^11.x"
  },
  "devDependencies": {
    "@types/react": "^18.x",
    "@types/react-dom": "^18.x",
    "autoprefixer": "^10.x",
    "postcss": "^8.x",
    "tailwindcss": "^3.x",
    "typescript": "^5.x"
  }
}
```

---

## Checklist de Performance

```
[ ] Fonts self-hosted em .woff2
[ ] Preload para fonts críticas
[ ] fetchpriority="high" na imagem LCP
[ ] loading="lazy" em imagens below fold
[ ] client:load apenas em islands interativos
[ ] client:idle para islands não críticos
[ ] Tailwind purge configurado
[ ] Imagens otimizadas (WebP/AVIF)
[ ] GA4/GTM via env vars (não hardcoded)
[ ] Schema JSON-LD em todas as páginas
[ ] Sitemap gerado automaticamente
```

---

## Deploy (Vercel)

```bash
# vercel.json
{
  "framework": "astro",
  "buildCommand": "npm run build",
  "outputDirectory": "dist"
}
```

### Variáveis de Ambiente no Vercel

```
PUBLIC_GA4_ID=G-XXXXXXXXXX
PUBLIC_GTM_ID=GTM-XXXXXXX
```
