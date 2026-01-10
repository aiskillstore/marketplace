---
name: seo-copywriter-pro
description: >
  Agente especializado em criação massiva de conteúdo SEO seguindo a metodologia James/Diesel Dudes.
  Use para criar 50+ páginas otimizadas rapidamente, gerar artigos em batch, traduzir para múltiplos
  idiomas, e rankear no Google em 30 dias. Ideal para sites de serviços locais, profissionais liberais,
  médicos, advogados, e qualquer negócio que precise dominar SEO local.
  Triggers: criar páginas SEO, gerar conteúdo em massa, rankear no Google, SEO local, criar artigos batch.
---

# SEO Copywriter Pro

Agente especializado em criação massiva de conteúdo SEO seguindo a metodologia comprovada que rankeou no Top 3 do Google em menos de 24 horas.

## Metodologia Core (James/Diesel Dudes)

### Princípios Fundamentais

1. **Keywords de Alta Intenção** - Focar onde pessoas estão prontas para agir
2. **Páginas Hiperlocalizadas** - Conteúdo único por localização/serviço
3. **Conteúdo Profundo** - 2000+ palavras por página
4. **Schema Markup Completo** - Ajudar Google entender o conteúdo
5. **Internal Linking Massivo** - Criar autoridade tópica
6. **Velocidade Extrema** - Score 90+ PageSpeed

### Categorias de Keywords

| Categoria | Descrição | Exemplo |
|-----------|-----------|---------|
| Emergency | Alta urgência, pronto para ligar | "encanador 24h São Paulo" |
| Service | Serviços específicos | "lifting facial minimamente invasivo" |
| Problem | Dores/problemas do cliente | "como resolver infiltração" |
| Location | Áreas geográficas | "dentista Pinheiros SP" |
| Authority | Busca por marca/pessoa | "Dr. Robério Brandão" |

## Workflow de Criação

### Fase 1: Mapeamento (Dia 1)

```
1. Identificar nicho e público-alvo
2. Mapear 50-100 keywords por categoria
3. Analisar competição (geralmente fraca em nichos locais)
4. Definir arquitetura de URLs
5. Criar inventário de copy (se houver material validado)
```

### Fase 2: Estrutura (Dia 2-3)

```
1. Criar arquitetura de site
2. Definir templates por tipo de página
3. Configurar SEO técnico (sitemap, robots, schema)
4. Preparar componentes reutilizáveis
```

### Fase 3: Criação Massiva (Dia 4-15)

```
1. Gerar páginas de serviço (10-15 páginas)
2. Gerar páginas de localização (10-20 páginas)
3. Gerar artigos do blog (15-25 artigos)
4. Criar glossário (se aplicável)
5. Implementar internal linking
```

### Fase 4: Otimização (Dia 16-20)

```
1. Otimizar velocidade (imagens WebP, lazy loading)
2. Validar schemas (Rich Results Test)
3. Testar mobile responsiveness
4. Verificar Core Web Vitals
```

### Fase 5: Tradução (Dia 21-25) [Opcional]

```
1. Traduzir páginas principais
2. Configurar hreflang
3. Adaptar culturalmente (não traduzir literalmente)
```

### Fase 6: Deploy (Dia 26-30)

```
1. Deploy em Vercel/Netlify
2. Submeter sitemap ao Search Console
3. Configurar analytics
4. Monitorar indexação
```

## Estrutura de Página SEO

### Meta Tags Obrigatórias

```html
<title>[Keyword Principal] | [Marca] - [Diferencial]</title>
<!-- Max 60 chars, keyword no início -->

<meta name="description" content="[Benefício] [Keyword] [CTA]">
<!-- Max 160 chars, keyword natural -->

<link rel="canonical" href="[URL absoluta]">
<link rel="alternate" hreflang="pt-BR" href="[URL PT]">
<link rel="alternate" hreflang="en" href="[URL EN]">
```

### Estrutura de Conteúdo

```markdown
# H1: [Keyword Principal] - Único por página

## Introdução (150-300 palavras)
- Identificar o problema
- Prometer a solução
- Estabelecer autoridade

## H2: [Keyword Secundária 1]
- Conteúdo profundo (300-500 palavras)
- Dados/estatísticas quando possível
- Internal links relevantes

## H2: [Keyword Secundária 2]
- Mesma estrutura

## H2: Resultados/Benefícios
- Dados concretos
- Comparativos (quando aprovados)

## FAQ (5-7 perguntas)
- Perguntas reais do público
- Schema FAQPage

## CTA Final
- Headline forte
- Botão de ação
```

## Referências Disponíveis

- **references/stack-astro.md** - Stack técnica Astro 5.x completa
- **references/copy-bank.md** - Banco de copy validada (headlines, frases, citações)
- **references/keywords.md** - Mapeamento de keywords por categoria
- **references/tone-guide.md** - Diretrizes de tom e voz
- **references/page-templates.md** - Templates por tipo de página
- **references/schema-examples.md** - Exemplos de schema markup

## Stack Técnica Padrão

| Tecnologia | Uso |
|------------|-----|
| **Astro 5.x** | Framework SSG/SSR |
| **@astrojs/react** | React islands |
| **styled-components** | Estilização React |
| **Tailwind CSS** | Utilitários CSS |
| **Swiper** | Carrosséis |

**Sempre consultar `references/stack-astro.md` para configurações detalhadas.**

## Scripts Disponíveis

- **scripts/generate-batch.py** - Gerar múltiplas páginas de uma vez
- **scripts/translate-content.py** - Traduzir conteúdo para outros idiomas
- **scripts/validate-seo.py** - Validar SEO de páginas criadas

## Regras de Tom (Padrão)

### ✅ Fazer

- Usar dados objetivos sem confronto direto
- Posicionar como evolução, não revolução
- Demonstrar empatia com dores do cliente
- Usar metáforas elegantes para simplificar
- Focar em benefícios práticos

### ❌ Evitar

- Ataques diretos a concorrentes
- Tom esnobe ou arrogante
- Perguntas provocativas/pretensiosas
- Jargão incompreensível para o público
- Promessas exageradas sem dados

## Checklist por Página

```
[ ] URL otimizada com keyword (max 3-5 palavras)
[ ] Title < 60 chars com keyword no início
[ ] Description < 160 chars com CTA
[ ] H1 único com keyword principal
[ ] H2s com keywords secundárias
[ ] Conteúdo 2000+ palavras
[ ] 5+ internal links
[ ] Imagens com alt text
[ ] Schema JSON-LD válido
[ ] FAQ section (5-7 perguntas)
[ ] CTA claro
[ ] Mobile responsivo
```

## Uso com Sub-Agentes

Para acelerar criação, lance múltiplos agentes:

```
Agent 1: Páginas de serviço
Agent 2: Páginas de localização  
Agent 3: Artigos do blog
Agent 4: Otimização técnica
Agent 5: Traduções
```

## Métricas de Sucesso

| Prazo | Meta |
|-------|------|
| 7 dias | 20+ páginas indexadas |
| 14 dias | 5+ keywords no Top 20 |
| 30 dias | 3+ keywords no Top 5 |
| 60 dias | 1+ keyword no Top 3 |
| 90 dias | Tráfego orgânico consistente |

## Exemplo de Prompt para Criar Página

```
Crie uma página SEO completa para:

**URL:** /tecnicas/endomidface/
**Keyword Principal:** endomidface visão direta
**Público:** Cirurgiões plásticos
**Objetivo:** Educar e gerar leads para curso

Requisitos:
- 2500+ palavras
- Schema MedicalProcedure
- FAQ com 7 perguntas
- CTA para /formacao/

Use o copy bank em references/copy-bank.md para headlines e citações aprovadas.
Siga o tom definido em references/tone-guide.md.
```
