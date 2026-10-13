# Motor CircuitViewer4: contrato atual

A arquitetura separa entradas editaveis, modelo, grandezas derivadas,
narracao e desenho. O formato binario oficial esta em spec_appvar_v2.md;
a autoria esta em ../ADDING_EXERCISES.md.

## Execucao unica

O AppVar arquivado mantem defaults, figura/topologia e programa matematico.
O loader copia apenas o exercicio aberto para RAM, aplica overrides e chama
a mesma rotina na primeira abertura e apos TODAS as edicoes.
Nenhuma pagina de resposta autoral congelada e exibida no v2r3.

Com live_size>0, live_recipe_run executa a receita. Caso contrario,
content_id seleciona um narrador numerico. content_id=255 exige receita.
As telas Resolucao e Resultados atuais vem da MESMA Narration.
Dados invalidos/singularidade geram motivo explicito e ocultam resultados.

## Componentes e modelos

EditComp: kind, na/nb, controlador, flags, valor/default real e imaginario.
16 registros por exercicio, inclusive setas anotativas. Tipos:
R, fonte V/I, C, L, fonte V/I dependente, seta, Z=R+jX.

Registros de R/L/C contem unidades SI. edit_comp_set_magnitude preserva
valores pequenos e a fase do fasor; nao aumenta um capacitor de 10 nF para
100 uF. Menu escalar suporta 64 entradas, com buffers que comportam valor
e indicacao de polaridade.

No 0 e referencia; I positivo na -> nb; fonte V: Vna-Vnb=Vs.
Flags invertem as duas partes do fasor da fonte.
ZC=1/(jwC), ZL=jwL. Em DC, C abre e L fecha. R/Z zero vira curto ideal.
Fontes dependentes permanecem ativas em superposicao e testes de porto.

AOP ideal acrescenta uma incognita de corrente de saida e V+=V-;
nao carrega os pinos de entrada. Representar a realimentacao real.
Cargas nominais usam modelo de potencia, nao resistencia inventada.

## Receita em Flash

tools/live_recipe.py compila AST restrita, valida nomes/indices/pilha.
src/live_recipe.c interpreta bytecode limitado, sem eval/recursao/alocacao.
64 variaveis, pilha 24, ate 4 AOPs, entradas nomeadas e complexos.

flags=1 resolve a MNA; flags=2 obtem Vth e Zth por fonte de teste.
solve(w,mask) resolve parcelas multifrequencia. Estado nodal/porto nao pode
ser lido sem uma solucao valida. Grandezas sao calculadas sequencialmente;
nenhuma resposta derivada pode ser usada como parametro de entrada.

Formato de linha: formula azul, valor vermelho real/retangular/polar.
Linhas longas dividem rotulo e valor; exceder capacidade produz erro.
64 linhas, 32 paginas, sete linhas por pagina. Todas as linhas de resultado
vao para Resultados atuais, nao apenas a ultima pagina/linha.

## Interface e memoria

Inicio e calculadora/busca; CLEAR vazio vai ao menu de conteudos.
MODE dentro do exercicio edita magnitudes, fases, frequencia positiva,
parametros e orientacao. Valores digitados sao decimais SI.
Enunciado original e rastreabilidade; Dados atuais e instancia em RAM.
Fechar/reabrir restaura defaults; nao ha persistencia de edicoes.

Programa e bytecode ficam em Flash. Workspace MNA, pilha da receita e
Narration sao estaticos/limitados para nao estourar o call stack CE.
Na calculadora, double tem 4 bytes; testes de dispositivo usam MNA_FORCE_FLOAT.

## Geracao e aceite

Template so pode ser deduplicado se valores, controles, direcoes, topologia,
geometria, portas, omega e flags coincidirem. Geometria identica NAO implica
defaults identicos. Metadados de menu nao carregam o catalogo antigo.

- 440 entradas com componente/parametro e rota ao vivo (374 livro + 66 provas);
- zero tails congeladas no pacote;
- empacotamento com offsets exatos e cabecalho v2r3;
- editor C real testado para cada componente/parametro e fonte;
- comparacao numerica independente, defaults ancorados no livro;
- erro de dominio/singularidade substitui respostas anteriores;
- renderizacao usa as paginas produzidas pelo runtime C;
- revisão visual das telas alteradas e build CEdev;
- teste fisico continua necessario antes de chamar o pacote validado em hardware.

Nao importar AppVar v1, CV3A, v2r2, provas nao autorizadas ou catalogo legado.
Excecao autorizada: oito PDFs em PROVAS/NOVAS_PROVAS, 75 questoes e 18
referencias ao livro, com deduplicacao, prioridade por recorrencia e
checkpoint compilado apos cada questao. Veja EXAMS_MANIFEST.md.
