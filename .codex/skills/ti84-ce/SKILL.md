# TI-84 CE Development Skill

Use esta skill para qualquer tarefa deste projeto envolvendo TI-84 Plus CE, TI-84 Plus CE Python Edition, TI-83 Premium CE, CEdev/toolchain CE, C, build, UI, memoria, emulador ou hardware real.

## Regras obrigatorias

- Nunca invente API, funcao, macro, header, flag, comando ou comportamento da CEdev/toolchain CE.
- Procure primeiro nos headers locais, exemplos locais e arquivos do projeto.
- Prefira documentacao oficial do CE C/C++ Toolchain e exemplos CE-Programming confiaveis.
- Valide o build antes de declarar uma tarefa de codigo como pronta.
- Trate tela 320x240, input por teclas e memoria limitada como restricoes obrigatorias.
- Mantenha codigo pequeno, simples e testavel.
- Documente qualquer suposicao.

## Ordem recomendada de verificacao

1. Leia o pedido e identifique se a tarefa e arquitetura, C, UI, memoria, build, teste ou revisao.
2. Consulte `.codex/knowledge/ti84-ce/` para notas locais do projeto.
3. Procure no projeto por exemplos existentes.
4. Procure nos headers locais e exemplos instalados da toolchain.
5. Consulte documentacao oficial ou repositorios CE-Programming quando necessario.
6. So entao implemente ou revise.

## Validacao minima

- Build limpo.
- Execucao basica quando houver ambiente.
- Navegacao principal.
- Entradas invalidas.
- Saida/quit.
- Riscos de travamento.
- Lista do que ainda precisa ser testado no CEmu ou no hardware real.

## Estilo de implementacao

- Prefira mudancas pequenas e focadas.
- Evite abstracoes genericas sem necessidade.
- Evite alocacao dinamica quando dados estaticos simples resolverem.
- Revise ponteiros, buffers e limites antes de finalizar.
- Informe comandos executados e resultados.
