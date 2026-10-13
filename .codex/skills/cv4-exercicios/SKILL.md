---
name: cv4-exercicios
description: Adicione, edite, valide ou remova exercicios editaveis do catalogo AppVar CV4A v2r3 do CircuitViewer4 para TI-84 Plus CE, com resposta e resolucao recalculadas.
---

# Exercicios do CircuitViewer4

Use tools/content/ e os modulos live_solutions, live_networks e live_specials.
Leia ADDING_EXERCISES.md completamente antes de alterar conteudo.
Ao mudar formato/runtime, leia tambem .ai-tasks/spec_appvar_v2.md e
.ai-tasks/spec_v4_engine.md. Este skill nao autoriza commits.

## Contrato essencial

O CV4 aceita exclusivamente CV4A 02 03. Nunca importe v1, v2r2, CV3A,
o catalogo antigo ou as provas antigas em PROVAS/.
Todo componente/dado de entrada alteravel deve possuir registro e uma
rota numerica real. Resposta E todas as etapas recalculam na abertura e
depois de editar. Proibido manter tail fixa ou mandar refazer a substituicao.

Use modelo matematico geral, nunca resposta esperada como parametro.
AOP exige V+=V- e Ient=0. Controle de dependentes deve ser resolvido
inclusive com rotulo numerico de ganho. Cargas W/VA/FP nao sao resistores.
Fontes desconhecidas pedidas no problema sao saidas, nao entradas inventadas.
Verifique pico/RMS, unidade SI, fase/sentido e ponto de medicao.

params: ate 64, nomes unicos <=12; componentes: ate 16.
Receita: 64 variaveis, pilha 24, rotulo <=34, formula <=37, unidade <=8.
Narration: 64 linhas; exercicio: 32 paginas, sete linhas por pagina.
Diferentes frequencias devem conservar parcelas temporais independentes.
Nunca aumentar silenciosamente valores pequenos (nF/pF) para um piso arbitrario.

## Procedimento

1. Extraia com book_extract.py e inspecione visualmente a pagina de
   Problemas do livro/PDF; indices e OCR podem errar dados e sinais.
2. Edite modulo autoral e receita/narrador; preserve os outros arquivos
   e o estado sujo do usuario. Nao edite gerados em bin/ e exercises.c.
3. Rode gerador, topology, audit_holes, audit_strings, test_pack_v2,
   test_catalog, run_host_tests e test_all_editable_routes.
4. Teste cada entrada, fonte/fase/orientacao e dominio invalido. Compare
   cada grandeza com referencia independente, nao so texto/contagem.
   Invariancia fisica pode ser correta; confira unchanged-edits.json.
5. Rode render_catalog DEPOIS do teste C do AppVar: ele renderiza as
   resolucoes reais salvas em runtime-pages.json. Inspecione figuras e
   paginas alteradas, inclusive cabecalho, capacitor, fios e resultados.
6. Compile CEdev. make clean vem ANTES do gerador; programa e TODOS
   os AppVars precisam ser entregues juntos. Teste em hardware e informe
   claramente se essa etapa nao foi executada.
7. So abencoe a baseline depois de confirmar mudanca intencional.

## Interface e provas

Inicio obrigatorio na calculadora/busca; CLEAR com entrada vazia abre
menu de conteudos. MODE edita dentro do exercicio; ON sai.
Edicoes sao temporarias em RAM. Entrada numerica e decimal em SI:
prefixos mostrados na tela nao sao digitaveis como unidade.

Futuras provas do conteudo atual podem orientar priority; documente
recorrencia confirmada. As provas antigas nunca influenciam a busca.
