# JSON-LD Schema Templates

Ready-to-use JSON-LD structured data templates for SEO and GEO optimization.

---

## 1. FAQPage Schema (+40% AI Visibility)

**Best for:** FAQ sections, knowledge base pages, product pages with Q&A.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is [Your Product/Service]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Comprehensive answer with statistics. According to X, 85% of users report Y benefit.]"
      }
    },
    {
      "@type": "Question",
      "name": "How does [Product/Service] work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Step-by-step explanation. First, you... Then... Finally...]"
      }
    },
    {
      "@type": "Question",
      "name": "What are the benefits of [Product/Service]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[List key benefits with data. Users save an average of X hours per week.]"
      }
    },
    {
      "@type": "Question",
      "name": "How much does [Product/Service] cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Pricing information. Plans start at $X/month with a free tier available.]"
      }
    },
    {
      "@type": "Question",
      "name": "How do I get started with [Product/Service]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Installation/signup instructions. Run: curl -fsSL example.com/install.sh | bash]"
      }
    }
  ]
}
```

---

## 2. WebPage Schema

**Best for:** Standard content pages, landing pages.

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "[Page Title]",
  "description": "[Page description, 150-160 characters]",
  "url": "https://example.com/page",
  "datePublished": "2024-01-15",
  "dateModified": "2024-12-20",
  "inLanguage": "en-US",
  "isPartOf": {
    "@type": "WebSite",
    "name": "[Site Name]",
    "url": "https://example.com"
  },
  "author": {
    "@type": "Person",
    "name": "[Author Name]",
    "url": "https://example.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Organization Name]",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": ["h1", ".summary", ".key-points"]
  }
}
```

---

## 3. Article Schema

**Best for:** Blog posts, news articles, tutorials.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Article Title - Max 110 characters]",
  "description": "[Article summary]",
  "image": [
    "https://example.com/image-1x1.jpg",
    "https://example.com/image-4x3.jpg",
    "https://example.com/image-16x9.jpg"
  ],
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-12-20T10:30:00+00:00",
  "author": {
    "@type": "Person",
    "name": "[Author Name]",
    "url": "https://example.com/author/name",
    "jobTitle": "[Job Title]",
    "worksFor": {
      "@type": "Organization",
      "name": "[Company]"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher Name]",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/article-url"
  },
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "articleSection": "[Category]",
  "wordCount": 2500
}
```

---

## 4. SoftwareApplication Schema

**Best for:** Tools, apps, software products.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[App Name]",
  "description": "[App description]",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Cross-platform",
  "url": "https://example.com",
  "downloadUrl": "https://example.com/download",
  "softwareVersion": "1.0.0",
  "releaseNotes": "https://example.com/changelog",
  "screenshot": "https://example.com/screenshot.png",
  "featureList": [
    "Feature 1 description",
    "Feature 2 description",
    "Feature 3 description"
  ],
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "150",
    "bestRating": "5",
    "worstRating": "1"
  },
  "author": {
    "@type": "Organization",
    "name": "[Company Name]",
    "url": "https://example.com"
  }
}
```

---

## 5. Organization Schema

**Best for:** About pages, company pages.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Organization Name]",
  "alternateName": "[Alternate Name]",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "[Organization description]",
  "foundingDate": "2024",
  "founders": [
    {
      "@type": "Person",
      "name": "[Founder Name]"
    }
  ],
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "addressCountry": "[Country]"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer service",
    "email": "support@example.com"
  },
  "sameAs": [
    "https://twitter.com/example",
    "https://github.com/example",
    "https://linkedin.com/company/example"
  ]
}
```

---

## 6. Product Schema

**Best for:** E-commerce product pages.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "description": "[Product description]",
  "image": [
    "https://example.com/product-image-1.jpg",
    "https://example.com/product-image-2.jpg"
  ],
  "sku": "[SKU]",
  "brand": {
    "@type": "Brand",
    "name": "[Brand Name]"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "99.99",
    "priceValidUntil": "2025-12-31",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "[Seller Name]"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "89"
  },
  "review": [
    {
      "@type": "Review",
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5"
      },
      "author": {
        "@type": "Person",
        "name": "[Reviewer Name]"
      },
      "reviewBody": "[Review text]"
    }
  ]
}
```

---

## 7. HowTo Schema

**Best for:** Tutorials, guides, how-to articles.

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [Do Something]",
  "description": "[Brief description of what this guide covers]",
  "image": "https://example.com/how-to-image.jpg",
  "totalTime": "PT15M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": "0"
  },
  "supply": [
    {
      "@type": "HowToSupply",
      "name": "[Required item 1]"
    }
  ],
  "tool": [
    {
      "@type": "HowToTool",
      "name": "[Required tool 1]"
    }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step 1: [Step Name]",
      "text": "[Detailed step instructions]",
      "image": "https://example.com/step-1.jpg",
      "url": "https://example.com/guide#step1"
    },
    {
      "@type": "HowToStep",
      "name": "Step 2: [Step Name]",
      "text": "[Detailed step instructions]",
      "image": "https://example.com/step-2.jpg",
      "url": "https://example.com/guide#step2"
    },
    {
      "@type": "HowToStep",
      "name": "Step 3: [Step Name]",
      "text": "[Detailed step instructions]",
      "image": "https://example.com/step-3.jpg",
      "url": "https://example.com/guide#step3"
    }
  ]
}
```

---

## 8. BreadcrumbList Schema

**Best for:** All pages with navigation hierarchy.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "[Category]",
      "item": "https://example.com/category"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[Current Page]",
      "item": "https://example.com/category/page"
    }
  ]
}
```

---

## 9. LocalBusiness Schema

**Best for:** Local business pages.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "description": "[Business description]",
  "image": "https://example.com/business-image.jpg",
  "url": "https://example.com",
  "telephone": "+1-555-555-5555",
  "email": "contact@example.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street Address]",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "postalCode": "[ZIP]",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ],
  "priceRange": "$$"
}
```

---

## 10. SpeakableSpecification (GEO Enhancement)

**Best for:** Voice search optimization, AI extraction.

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "[Page Title]",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [
      "h1",
      ".summary",
      ".key-takeaways",
      ".faq-answer"
    ]
  }
}
```

---

## Combined Schema Example

For a software product page with FAQ:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebPage",
      "name": "OPC Skills - AI Agent Skills for Solopreneurs",
      "description": "10+ agent skills for Claude Code, Cursor, Codex. Domain hunting, social media research, logo creation.",
      "url": "https://opc.dev",
      "dateModified": "2024-12-20",
      "speakable": {
        "@type": "SpeakableSpecification",
        "cssSelector": ["h1", ".hero-description", ".faq-answer"]
      }
    },
    {
      "@type": "SoftwareApplication",
      "name": "OPC Skills",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "Cross-platform",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is OPC Skills?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OPC Skills is a collection of 10+ AI agent skills for solopreneurs, supporting Claude Code, Cursor, and Codex."
          }
        }
      ]
    },
    {
      "@type": "Organization",
      "name": "OPC Skills",
      "url": "https://opc.dev",
      "sameAs": ["https://github.com/ReScienceLab/opc-skills"]
    }
  ]
}
```

---

## Validation Tools

1. **Google Rich Results Test**
   ```
   https://search.google.com/test/rich-results?url={your-url}
   ```

2. **Schema.org Validator**
   ```
   https://validator.schema.org/?url={your-url}
   ```

3. **Google Search Console**
   - Check "Enhancements" for schema issues
   - Monitor rich result performance
