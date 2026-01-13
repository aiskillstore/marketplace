# Templates de Páginas SEO

Templates prontos para cada tipo de página, seguindo metodologia James/Diesel Dudes.

---

## Template 1: HOMEPAGE

```markdown
---
title: "[Nome] | [Título/Especialidade] - [Diferencial Único]"
description: "[Benefício principal]. [Credencial]. [CTA implícito]."
---

# HERO SECTION
## Headline Principal
[Use headline aprovada do copy-bank - ex: H01, H06, H08]

## Subtítulo
[Expandir benefício em 1-2 frases com dados]

## CTAs
- Primário: [Ação principal - ex: "Conhecer Formação"]
- Secundário: [Ação de descoberta - ex: "Ver Técnicas"]

---

# SEÇÃO: QUEM É [NOME]
## Credenciais em Números
- [Dado 1]: [Número] [Contexto]
- [Dado 2]: [Número] [Contexto]
- [Dado 3]: [Número] [Contexto]

## Citação Destacada
> [Usar citação ⭐⭐⭐⭐⭐ do copy-bank]

## CTA: Conhecer mais sobre [Nome]

---

# SEÇÃO: [METODOLOGIA/FILOSOFIA]
## Os [N] Pilares
1. **[Pilar 1]**: [Descrição curta]
2. **[Pilar 2]**: [Descrição curta]
3. **[Pilar 3]**: [Descrição curta]

## CTA: Explorar [Metodologia]

---

# SEÇÃO: TÉCNICAS/SERVIÇOS
## Cards (3-4)
### [Técnica 1]
- Descrição: [1-2 frases]
- Benefício: [Principal resultado]
- CTA: Saiba mais

[Repetir para cada técnica]

---

# SEÇÃO: RESULTADOS EM NÚMEROS
## Grid de Dados
- [Dado 1]: [Número grande] + [Contexto curto]
- [Dado 2]: [Número grande] + [Contexto curto]
- [Dado 3]: [Número grande] + [Contexto curto]
- [Dado 4]: [Número grande] + [Contexto curto]

---

# SEÇÃO: CTA FINAL
## Headline
[Pergunta que gera reflexão ou promessa]

## Citação
> [Usar citação ⭐⭐⭐⭐ do copy-bank]

## Botão
[CTA principal]
```

---

## Template 2: PÁGINA DE TÉCNICA/SERVIÇO

```markdown
---
title: "[Técnica]: [Benefício Principal] | [Marca]"
description: "[O que é]. [Dado de destaque]. [Para quem]."
schema: MedicalProcedure
palavras: 2500+
---

# H1: [Técnica]: [Subtítulo Descritivo]

## Introdução (200-300 palavras)
[Parágrafo 1: O que é e qual problema resolve]
[Parágrafo 2: Por que é diferente/melhor]
[Parágrafo 3: Para quem é indicado]

---

## H2: O Que É [Técnica]?

### Definição
[Explicação clara em 2-3 parágrafos]

### Objetivos
- [Objetivo 1]
- [Objetivo 2]
- [Objetivo 3]

### Diferencial
[Por que esta abordagem específica - 1-2 parágrafos]

---

## H2: Como Funciona [Técnica]

### O Processo
[Descrição do procedimento em linguagem acessível]

### Etapas
1. **[Etapa 1]**: [Descrição]
2. **[Etapa 2]**: [Descrição]
3. **[Etapa 3]**: [Descrição]

### Metáfora Didática
> [Usar metáfora do copy-bank para explicar conceito complexo]

---

## H2: Indicações e Contraindicações

### Para Quem é Indicado
- [Indicação 1]
- [Indicação 2]
- [Indicação 3]

### Casos Especiais
[Situações onde se destaca - ex: bioestimuladores]

### Contraindicações
- [Relativa 1]
- [Relativa 2]

---

## H2: Resultados e Segurança

### Dados Documentados
| Métrica | Resultado |
|---------|-----------|
| [Métrica 1] | [Dado] |
| [Métrica 2] | [Dado] |
| [Métrica 3] | [Dado] |

### Recuperação
[Timeline de recuperação]

### Longevidade
[Duração dos resultados]

---

## H2: [Técnica] vs [Alternativa Comum]

### Comparativo Objetivo
| Aspecto | [Técnica] | [Alternativa] |
|---------|-----------|---------------|
| [Aspecto 1] | [Dado] | [Dado] |
| [Aspecto 2] | [Dado] | [Dado] |

### Posicionamento
[Posicionar como complementares, não competidores]

---

## FAQ

### [Pergunta 1]?
[Resposta concisa]

### [Pergunta 2]?
[Resposta concisa]

[5-7 perguntas no total]

---

## CTA Final

### Headline
[Chamada para ação]

### Citação
> [Citação relevante do copy-bank]

### Botões
- [CTA Primário]
- [CTA Secundário]
```

---

## Template 3: ARTIGO DE BLOG

```markdown
---
# META SEO
title: "[Keyword Principal]: [Promessa/Benefício]"
description: "[O que o leitor vai aprender]. [Credencial]. [CTA implícito]." # 120-155 chars
slug: "[keyword-principal-separada-por-hifen]"
keywords: ["keyword1", "keyword2", "keyword3"]

# INFORMAÇÕES DO ARTIGO
author: "Dr. Robério Brandão"
date: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
category: "[técnica|anatomia|casos|educacional|comparativo]"
tags: ["tag1", "tag2", "tag3"]
readingTime: "X min"

# IMAGENS
coverImage: "/images/blog/[slug]/cover.jpg"
coverImageAlt: "[Descrição da imagem de capa]"
ogImage: "/images/og/[slug].jpg"

# SCHEMA
schema: ["MedicalWebPage", "FAQPage", "Article"]
---

# H1: [Título Principal com Keyword]

## Subtítulo (opcional)
[Complemento do título - expande ou qualifica]

**Autor:** Dr. Robério Brandão | **Publicado:** [Data] | **Atualizado:** [Data]  
**Tempo de leitura:** X minutos

---

## Resumo (Lead/Chapô)

[1-3 frases que apresentam a ideia principal e prendem o leitor. Responde: "Por que devo ler isso?" Este texto aparece em previews e cards.]

---

## Índice

1. [Introdução](#introducao)
2. [Seção 1: Contexto/Definição](#secao-1)
3. [Seção 2: Desenvolvimento](#secao-2)
4. [Seção 3: Exemplos/Casos](#secao-3)
5. [Seção 4: Boas Práticas](#secao-4)
6. [Conclusão](#conclusao)
7. [FAQ](#faq)
8. [Referências](#referencias)

---

## Introdução {#introducao}

[Parágrafo 1: Contextualização - Qual problema ou situação estamos abordando?]

[Parágrafo 2: Relevância - Por que isso importa para o leitor?]

[Parágrafo 3: Promessa - O que o leitor vai aprender/ganhar ao final?]

[Parágrafo 4: Credencial - Por que o autor é qualificado para falar disso?]

> [Citação relevante do Dr. Robério do copy-bank, se aplicável]

---

## H2: [Seção 1 - Contexto/Definição] {#secao-1}

[Introdução da seção - o que vamos abordar]

### H3: [Subtópico 1.1]

[Conteúdo - 2-4 parágrafos curtos]

[Link interno para página relacionada](/tecnicas/endomidface/)

### H3: [Subtópico 1.2]

[Conteúdo com dados quando possível]

| Dado | Valor |
|------|-------|
| [Métrica] | [Número] |

---

## H2: [Seção 2 - Desenvolvimento/Argumentos] {#secao-2}

[Introdução da seção]

### H3: [Subtópico 2.1]

[Conteúdo desenvolvendo o argumento principal]

### H3: [Subtópico 2.2]

**Passo a passo (se for tutorial):**

1. **[Passo 1]**: [Descrição]
2. **[Passo 2]**: [Descrição]
3. **[Passo 3]**: [Descrição]

---

## H2: [Seção 3 - Exemplos/Casos/Ilustrações] {#secao-3}

[Introdução da seção]

### Caso/Exemplo 1

[Descrição do caso com contexto, problema, solução e resultado]

### Caso/Exemplo 2

[Idem]

![Descrição da imagem](/images/blog/[slug]/exemplo.jpg)
*Legenda da imagem explicando o que está sendo mostrado*

---

## H2: [Seção 4 - Boas Práticas/Recomendações] {#secao-4}

[Introdução da seção]

### O que fazer ✅

- [Recomendação 1]
- [Recomendação 2]
- [Recomendação 3]

### O que evitar ❌

- [Anti-padrão 1]
- [Anti-padrão 2]

### Dica do especialista

> [Citação ou insight do Dr. Robério]

---

## Conclusão (Takeaway) {#conclusao}

### Em Resumo

[Parágrafo sintetizando os principais aprendizados - 3-4 frases]

### Principais Pontos

- **[Ponto 1]**: [Resumo de uma frase]
- **[Ponto 2]**: [Resumo de uma frase]
- **[Ponto 3]**: [Resumo de uma frase]

### Próximos Passos

[O que o leitor deve fazer agora? CTA claro]

> [Citação final inspiradora do copy-bank]

---

## FAQ {#faq}

### [Pergunta 1]?

[Resposta concisa e direta - 2-4 frases]

### [Pergunta 2]?

[Resposta]

### [Pergunta 3]?

[Resposta]

### [Pergunta 4]?

[Resposta]

### [Pergunta 5]?

[Resposta]

[Mínimo 5 perguntas, máximo 10]

---

## Referências e Leituras Adicionais {#referencias}

### Artigos Relacionados

- [Título do Artigo 1](/blog/artigo-1/)
- [Título do Artigo 2](/blog/artigo-2/)
- [Título do Artigo 3](/blog/artigo-3/)

### Páginas de Técnicas

- [Endomidface por Visão Direta](/tecnicas/endomidface/)
- [Face Moderna](/face-moderna/)

### Fontes Externas (se aplicável)

- [Nome da Fonte] - [Descrição breve]

---

## Créditos

**Autor:** Dr. Robério Brandão  
**Revisão:** [Nome se houver]  
**Imagens:** [Crédito/Licença]

---

## CTA Final

[Componente CTA com:
- Headline forte
- Descrição curta
- Botão primário
- Botão secundário (opcional)
- Citação do Dr. Robério]
```

### Especificações Técnicas do Artigo

| Elemento | Especificação |
|----------|---------------|
| **Comprimento** | 1.500-2.500 palavras (guias aprofundados) |
| **Parágrafos** | Curtos, 2-4 linhas máximo |
| **H1** | Apenas 1 por página (título) |
| **H2** | 4-6 seções principais |
| **H3** | 2-3 por H2 |
| **Imagens** | Capa + 2-4 internas, todas com alt text |
| **Links internos** | Mínimo 5 |
| **FAQ** | 5-10 perguntas |
| **Meta title** | < 60 caracteres |
| **Meta description** | 120-155 caracteres |
| **URL/Slug** | Limpo, com keyword, sem stopwords |

### Checklist de Qualidade

```
ESTRUTURA
[ ] H1 único com keyword principal
[ ] Subtítulo complementar (se necessário)
[ ] Autor, data e tempo de leitura
[ ] Resumo/Lead atraente (1-3 frases)
[ ] Índice para artigos > 1500 palavras
[ ] Introdução contextualiza e promete valor
[ ] Seções bem divididas com H2/H3
[ ] Conclusão com takeaways claros
[ ] FAQ com 5+ perguntas
[ ] Referências e links relacionados
[ ] CTA final

CONTEÚDO
[ ] 1500+ palavras
[ ] Parágrafos curtos (2-4 linhas)
[ ] Dados/estatísticas quando possível
[ ] Citações do copy-bank
[ ] Tom conforme tone-guide
[ ] Exemplos práticos
[ ] Listas para escaneabilidade

SEO
[ ] Title < 60 chars com keyword
[ ] Description 120-155 chars
[ ] URL limpa com keyword
[ ] 5+ links internos
[ ] Schema Article + FAQPage
[ ] Imagens com alt text descritivo

ACESSIBILIDADE
[ ] Hierarquia de headings correta
[ ] Alt text em todas imagens
[ ] Legendas em imagens informativas
[ ] Contraste adequado
[ ] Links descritivos (não "clique aqui")
```

---

## Template 4: PÁGINA DE CURSO/CONVERSÃO

```markdown
---
title: "[Nome do Curso] | [Resultado Principal] - [Marca]"
description: "[O que vai aprender]. [Credencial do instrutor]. [Benefício principal]."
schema: Course
---

# H1: [Nome do Curso]

## Hero
### Headline
[Headline de alta conversão do copy-bank]

### Subtítulo
[Expandir benefício com dados]

### CTA Principal
[Botão destacado]

---

## Para Quem É Este Curso

### Perfil Ideal
- [Característica 1]
- [Característica 2]
- [Característica 3]

### Não É Para Você Se
- [Exclusão honesta 1]
- [Exclusão honesta 2]

---

## O Que Você Vai Aprender

### Módulos
1. **[Módulo 1]**: [Descrição + resultado]
2. **[Módulo 2]**: [Descrição + resultado]
[...]

### Bônus
- [Bônus 1]
- [Bônus 2]

---

## Sobre o Instrutor

### Credenciais
[Dados de autoridade]

### Citação
> [Citação sobre missão de ensinar]

---

## Resultados dos Alunos

### Depoimentos
[Depoimento 1]
[Depoimento 2]

### Números
- [Dado de resultado 1]
- [Dado de resultado 2]

---

## Investimento

### Valor
[Preço + justificativa de ROI]

### Garantia
[Política de garantia]

### CTA
[Botão principal]

---

## FAQ

### [Pergunta sobre formato]?
[Resposta]

### [Pergunta sobre suporte]?
[Resposta]

[5-7 perguntas]

---

## CTA Final

### Headline de Urgência/Escassez
[Se aplicável - honesto]

### Citação Final
> [Citação inspiradora]

### Botão
[CTA principal]
```

---

## Template 5: GLOSSÁRIO (Termo Individual)

```markdown
---
title: "[Termo]: Definição e Aplicação | Glossário [Marca]"
description: "O que é [Termo]. Definição técnica, contexto de uso e aplicação prática em [área]."
schema: DefinedTerm
palavras: 500-1000
---

# H1: [Termo]

## Definição
[Definição clara em 1-2 parágrafos]

## Contexto de Uso
[Onde e quando este termo é aplicado]

## Relação com Outros Conceitos
- [Conceito relacionado 1]: [Como se conecta]
- [Conceito relacionado 2]: [Como se conecta]

## Na Prática
[Aplicação prática do conceito]

## Ver Também
- [Link termo relacionado 1]
- [Link termo relacionado 2]
- [Link página de técnica relacionada]
```

---

## Checklist de Criação de Página

```
PRÉ-CRIAÇÃO
[ ] Keyword principal definida
[ ] Keywords secundárias mapeadas
[ ] Template apropriado selecionado
[ ] Copy do copy-bank identificada

DURANTE CRIAÇÃO
[ ] Title < 60 chars com keyword
[ ] Description < 160 chars
[ ] H1 único com keyword
[ ] H2s com keywords secundárias
[ ] Conteúdo no tamanho especificado
[ ] 5+ internal links incluídos
[ ] Citações do copy-bank usadas
[ ] Tom conforme tone-guide
[ ] FAQ incluído (5-7 perguntas)
[ ] CTA claro

PÓS-CRIAÇÃO
[ ] Schema adicionado
[ ] Imagens com alt text
[ ] Links funcionando
[ ] Mobile responsivo
[ ] Velocidade OK
```
