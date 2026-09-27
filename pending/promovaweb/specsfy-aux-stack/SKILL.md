---
name: specsfy-aux-stack
description: Monitorar manifests e arquivos estruturais para criar ou atualizar .specsfy/STACK.md de forma aditiva. Use quando o monitor de contexto apontar stack pendente; quando framework, linguagem, runtime, pacote estrutural, ferramenta de teste ou persistência mudar; quando a documentação técnica estiver incompleta; ou após adicionar Laravel, Next.js, Astro ou dependências relevantes. Preserva conteúdo humano existente.
---

# Manter o stack

## Preparação obrigatória

Antes de executar esta skill, carregue obrigatoriamente `$specsfy-setup` na
raiz do projeto. Em handoff automático, carregue-o de novo antes desta etapa.
Reutilize a raiz confirmada na conversa e não prossiga se o setup apontar uma
pendência.

## Modo de interação

Modo de interação: `sem perguntas`.
Não formule perguntas nesta skill. Quando faltar informação confirmada,
sinalize o campo pendente para a etapa conversacional responsável.

1. Ler instruções locais, `PROJECT.md` e o `STACK.md` existente.
2. Executar `node scripts/update_stack.mjs --project <raiz>`.
3. Conferir cada linha contra manifests, lockfiles e configurações presentes.
4. Manter decisões, notas e linhas humanas fora do bloco
   `specsfy:stack`; nunca removê-las.
5. Acrescentar manualmente somente fatos sustentados por uma fonte executável e
   citar essa fonte na coluna `Evidência`.
6. Se a mudança também alterar persistência, carregar
   `$specsfy-aux-database`.
7. Executar `$specsfy-setup` em modo de monitoramento e não devolver o handoff
   enquanto `.specsfy/STACK.md` continuar pendente.

Não copiar árvores inteiras de dependências. Registrar tecnologias estruturais,
suas responsabilidades e evidências úteis para agentes compreenderem o sistema.
