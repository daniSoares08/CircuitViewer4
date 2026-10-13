# CIRCVIE4

Aplicativo oficial para TI-84 Plus CE. Catalogo novo dos capitulos 9 a 12,
com dados editaveis, respostas recalculadas e resolucao passo a passo.
Nenhum catalogo legado e carregado. Os oito PDFs explicitamente autorizados
em PROVAS/NOVAS_PROVAS foram incorporados; outras provas permanecem excluidas.

## Catalogo e recalculo

440 entradas: 374 do livro (93, 96, 98 e 87 dos caps. 9--12) e 66 novos
exercicios das provas/lista. Cobertura de 75 questoes numeradas e 18
referencias ao livro, sem duplicar repeticoes exatas. Ha 287 figuras e
1.074 parametros escalares nomeados. Veja EXAMS_MANIFEST.md para a origem.

Todas as 440 entradas possuem uma rota de calculo executada na abertura
e depois de cada edicao. Sao 374 receitas matematicas compiladas para Flash
e 66 rotas de narradores numericos. Nao existem respostas fixas como
substituto do recalculo nem instrucoes para o aluno refazer a substituicao.

As receitas permitem algebra complexa, formas de onda/RMS, projeto,
potencia, fontes dependentes, AOP ideal e trifasico. A mesma fonte de dados
alimenta os passos e as telas `Resultados atuais`; resultados extensos
ocupam varias paginas, sem perder as etapas intermediarias.

`Enunciado original` registra o caso do livro. `Dados atuais` mostra os
parametros vigentes; os componentes desenhados e o menu MODE mostram os
valores da instancia aberta. Edicoes sao temporarias: fechar/reabrir
restaura os defaults. Dados que tornem o modelo indefinido ou singular
geram um aviso, sem conservar a resposta anterior.

## Inicio e controles

O app inicia na tela de calculadora/busca, nao na lista de conteudos.
CLEAR apaga a entrada; com a entrada vazia, CLEAR retorna ao menu de
conteudos. O menu separa os exercicios por assunto e oferece Buscar.
ON sai do app.

Na busca: Y=, WINDOW, ZOOM, TRACE e GRAPH selecionam as quantidades de
resistores, fontes V, fontes I, capacitores e indutores; 2nd reduz a
quantidade seguinte. ALPHA mostra os nomes; MATH mostra as contagens.
SIN/COS acessam os atalhos de catalogo; ENTER executa a busca.

No exercicio: esquerda/direita ou ENTER navegam pelas paginas, cima/baixo
mudam o exercicio, MODE abre a edicao e CLEAR volta.
MODE permite valores/magnitudes, fases, frequencia positiva em rad/s,
parametros e orientacao das fontes. A inversao muda o fasor inteiro.
Para Z, magnitude e fase determinam suas partes real/imaginaria.

Os valores digitados sao decimais em unidades SI: por exemplo, 10 nF deve
ser digitado como 0.00000001. O prefixo mostrado na tela e uma formatacao,
nao uma unidade que o teclado interprete. Nao ha um piso de 0.0001 para
componentes pequenos.

## Instalacao do pacote atual

Transfira juntos os seis arquivos de `bin/` ou do ultimo checkpoint aprovado
indicado em `.ai-tasks/exams-progress.json`:

- `CIRCVIE4.8xp`;
- `CV4DAT0.8xv`, `CV4DAT1.8xv`, `CV4DAT2.8xv`, `CV4DAT3.8xv`, `CV4DAT4.8xv`.

Todos os AppVars devem ficar arquivados. O formato e exclusivamente
`CV4A 02 03` (v2r3). O novo programa rejeita v2r2, v1 e CV3A:
substitua os dados junto com o programa, nao apenas o .8xp.
Chunks adicionais gerados no futuro tambem fazem parte do pacote.

## Gerar e verificar

~~~powershell
make clean
python tools/generate_cv4.py
python tools/topology.py
python tools/audit_holes.py
python tools/audit_strings.py
python tests/test_pack_v2.py
python tests/test_catalog.py
python tests/test_exam_coverage.py --complete
python tests/test_exam_diagram.py
python tests/run_host_tests.py
python tests/test_all_editable_routes.py
python tools/render_catalog.py
python tests/test_baseline.py
make
~~~

`make clean` remove os AppVars: sempre regenere depois dele.
A baseline so deve ser atualizada com `--bless` depois da revisao de uma
mudanca intencional. Nao commitar sem autorizacao.

O teste integral executa o leitor/editor C com os AppVars gerados e salva
as paginas reais em `tmp/live-qa/runtime-pages.json`. O renderer utiliza
essas resolucoes, nao as antigas strings de resposta do livro. Inspecione
visualmente as telas alteradas em `tmp/catalog-render/`: coordenadas
validas nao garantem ausencia de sobreposicoes.

Testes de host nao substituem o teste do pacote final em uma TI-84 Plus CE.

## Autoria e arquitetura

Edite `tools/content/ch09*.py`, `ch10*.py`, `ch11*.py`, `ch12*.py`
e `exams.py`; receitas em `live_solutions.py`, `live_networks.py`, `live_specials.py`.
Nao edite manualmente `src/exercises.c` nem `bin/CV4DAT*`.

- `src/live_recipe.c`: avaliador limitado de bytecode em Flash;
- `src/mna.c`: solver DC/CA, dependentes e AOP ideal;
- `src/engine.c`: componentes, edicao e conversao para MNA;
- `src/appvar.c`: validacao binaria, carga, recalculo e paginacao;
- `src/main.c`: interface e menus de ate 64 parametros;
- `tools/live_recipe.py`: compilador restrito de expressoes;
- `tools/generate_cv4.py`: templates, prioridades e empacotamento;
- `tools/render_catalog.py`: QA de figuras e resolucoes do runtime.

Consulte `ADDING_EXERCISES.md`, `EXERCISE_MANIFEST.md`,
`EDITABLE_RESOLUTION_AUDIT.md`, `EXAMS_MANIFEST.md` e `.ai-tasks/spec_appvar_v2.md`.

As provas fora de PROVAS/NOVAS_PROVAS continuam excluidas. A recorrencia
nos PDFs autorizados orienta a prioridade dentro dos assuntos e nas buscas.
Depois de cada nova questao, tools/checkpoint_exam.py valida, compila e
preserva o pacote em releases/provas/. Nao misture arquivos de checkpoints.

MIT License - Daniel Soares (github.com/daniSoares08).
