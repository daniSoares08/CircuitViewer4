# Autoria de exercicios editaveis do CIRCVIE4

Contrato atual: AppVar CV4A v2r3. O exercicio e composto por entradas,
modelo matematico, etapas calculadas e apresentacao; uma resposta fixa
nunca substitui o modelo.

## Fluxo obrigatorio

1. Confira enunciado e figura no livro/PDF renderizado. O indice textual
   pode encontrar revisao em vez de Problemas ou errar a pagina. Registre
   a origem e a convencao de sinais, unidades, pico/RMS e referencias.
2. Edite o modulo de capitulo em tools/content/. Toda entrada alteravel
   deve ser componente ou parametro nomeado; nunca exponha a resposta
   calculada como se fosse um dado de entrada.
3. Defina uma receita ao vivo ou um narrador existente que resolva
   exatamente o que foi pedido. Casos sem rota sao erro de geracao.
4. Gere o pacote e execute os testes estruturais, numericos e de edicao.
   Compare defaults com uma referencia independente do modelo.
5. Altere cada entrada, fase e orientacao. Confira etapas e resultados,
   inclusive dados pequenos, cancelamentos e dominios invalidos.
6. Renderize as paginas reais do runtime, revise as figuras alteradas e
   faca o build final. Atualize a baseline somente apos a revisao.

Nao edite src/exercises.c ou bin/ manualmente. Nao importe o catalogo antigo
nem provas nao autorizadas. NOVAS_PROVAS e a excecao autorizada em 2026-10-06;
veja EXAMS_MANIFEST.md. Nao commitar sem autorizacao.

## Dados de autoria

Cada item precisa de id unico, title, subject, source e statement.
priority menor aparece primeiro dentro da secao e na busca.
expected e apenas referencia de teste; nao e resposta do runtime.

A figura fica em CIRCUITS[id]. engine pode informar omega em rad/s,
target_op_index (op eletrica, zero-based), port_labels, peak,
dep_resolve e profile. diagram_only marca uma figura explicativa, como
forma de onda, que nao deve virar MNA.

params usa pares (nome, valor): ate 64 entradas, nome unico ASCII com
ate 12 caracteres, valores finitos em unidades SI. Complexos escalares
usam entradas separadas para real/imaginario ou modulo/fase.
PARAM_FIX em live_solutions.py permite corrigir o banco de dados antigo;
EXTRA_PARAMS em live_specials.py acrescenta entradas especificas.

static/solution/visual_only continuam existindo nos modulos antigos apenas
como metadados de autoria. NAO autorizam uma resolucao congelada:
o gerador precisa de receita e elimina tail; o loader v2r3 rejeita tail.
Uma deducao simbolica deve possuir tambem a substituicao numerica ao vivo.

## Receitas matematicas

O contrato esta em tools/live_recipe.py e src/live_recipe.c.
Exemplo de corpo para dados RMS R_ohm, X_ohm, V_V e V_deg:

~~~python
from content.live_solutions import recipe
spec = recipe(
    ('Z', 'complex(R_ohm,X_ohm)', 'ohm', 'Z=R+jX'),
    ('I', 'polar(V_V,V_deg)/Z', 'A', 'I=V/Z', 2),
    ('P', 'real(Z)*abs(I)**2', 'W', 'P=R |I_RMS|^2'),
)
~~~

Vincule spec ao ID em SCALAR ou special_recipe. Tambem e permitido
live_recipe no proprio item, como em content/exams.py. Os bancos devem
conter somente os dados fornecidos. Se o problema for aberto, identifique
claramente quais numeros sao um exemplo de projeto editavel.

Cada etapa e (chave, rotulo, expressao, unidade, formula, modo).
O helper recipe aceita (chave, expressao, unidade, formula, modo) e usa a
chave como rotulo. Modos: 0 interno, 1 retangular/real, 2 polar.
Formula geral aparece em azul; valor calculado aparece em vermelho.
Rotulo <=34 caracteres, formula <=37, unidade <=8. Nao inclua numeros
originais na formula quando devem variar.

Referencias:

- p0, p1... ou o nome do parametro: entrada escalar atual;
- c0, c1...: valor complexo atual do componente, com orientacao da fonte;
- z0, z1...: impedancia do componente na omega atual;
- v0, v1...: tensoes nodais da ultima solucao (v0=0);
- i0, i1...: correntes na -> nb;
- s0, s1...: V(na-nb) conj(I), convencao passiva, sem fator pico automatico;
- omega: frequencia angular atual; vth/zth: porto calculado;
- chave de etapa anterior: grandeza derivada, nunca uma entrada duplicada.

Aritmetica real/complexa; abs, arg, real, imag, conj, sqrt, csqrt,
sin, cos, tan, acos, atan, exp, log, polar, complex, min e max.
Trigonometria e polar usam graus; omega usa rad/s.
guard(condicao) encerra dados fora do dominio.
Nao ha eval de Python, recursao nem acesso a arquivos na calculadora.

flags=1 resolve a rede inicialmente. flags=2 faz circuito aberto e fonte
de teste 1 A no porto. remove retira uma carga mantendo indices estaveis.
opamps recebe tuplas (saida, positivo, negativo): V+=V-, Ient=0.
solve(omega, mascara) reexecuta a MNA para uma frequencia e conjunto de
fontes independentes; fontes dependentes ficam ativas. Some respostas
de frequencias diferentes NO TEMPO, nunca os seus fasores.

Capacidade: 64 variaveis derivadas, pilha de 24 valores, 64 linhas narradas,
32 paginas no exercicio. Etapas internas nao ocupam tela. Respostas longas
podem ocupar duas linhas: verifique a contagem real, nao apenas a prevista.
As paginas Resultados atuais devem incluir todos os valores exibidos na
resolucao, sem cortar o ultimo resultado.

## Eletrica e convencoes

Use imp_h/v para R+jX ja fornecido, cap_h/v e ind_h/v para C/L fisicos.
O parser aceita 4+j8, -j10, 2k+j4k, 100/_20V, 6/_-30A,
50uF, 10nF, 200pF e 1M. Para impedancia jX dada, omega=1 apenas ativa
o dominio fasorial; mudar omega nao altera esse X ja definido.

Corrente positiva e na -> nb; fonte V: Vna-Vnb=Vs. O flag de inversao
nega TODO o fasor, nao so sua parte real.
Resolva o controle de toda fonte dependente, inclusive quando o rotulo
contem apenas o ganho numerico. Verifique o no do resistor/corrente pedido,
nao o primeiro ramo proximo que pareca plausivel.

AOP deve representar a realimentacao correta: nunca aterre o pino negativo
para contornar a restricao que falta. Carga especificada por W/VA/FP e um
modelo de potencia; nao invente uma resistencia para tornar a figura editavel.
Fontes desconhecidas pedidas na questao sao SAIDAS, nao entradas arbitrarias.

Potencia: S=V conj(I) em RMS, S=V conj(I)/2 em pico. No Cap. 11 a
nota do livro usa pico antes do 11.22; depois usa RMS salvo indicacao.
Wattimetro: W=Re(Vbobina conj(Ibobina)), incluindo a polaridade.
RMS por trechos: integral dos quadrados dividida pelo periodo total;
qualquer nivel ou duracao alteravel deve entrar nessa integral.

## QA e comandos

Provas: registre cada ocorrencia com documento, pagina e questao em
content/exams.py. Repita apenas quando os dados ou pedidos diferirem;
alias reutiliza o ID de um caso exatamente igual. BOOK_REFERENCES registra
referencias ao livro sem duplicar entradas. Referencias numericas de
exam_anchors sao de teste, nunca respostas na calculadora.

Apos CADA nova questao rode python tools/checkpoint_exam.py e so avance
quando o build for aprovado. Preserve todos os checkpoints. Em caso de
interrupcao use .ai-tasks/exams-progress.json e seu pacote completo;
bin/ pode estar incompleto. Para encerrar rode cobertura --complete,
regressoes, revisao visual e checkpoint --clean. EXAMS_MANIFEST.md mapeia
as questoes que aparecem com o titulo de outro exercicio canonico.

Diagrama fasorial: diagram_only e flags2=8 usam os parametros Acos, Asin,
nesta ordem. O vetor Acos-j Asin e desenhado com escala automatica a cada
edicao. Nao desenhe um vetor congelado para dados numericos editaveis.
tests/test_exam_diagram.py confere o desenhador C, nao apenas o preview.
Terminal a/b fica acima do fio; diagramas e renderer devem concordar.

~~~powershell
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

Se usar make clean, execute-o ANTES do gerador. Transfira o programa
e TODOS os CV4DAT*.8xv do mesmo build.

test_live_recipes compara cada grandeza em float do dispositivo com
aritmetica double/MNA independente e referencias numericas selecionadas.
test_appvar_live executa o leitor/editor C real, altera componentes,
parametros, frequencia, fase e polaridade, verifica paginacao e salva as
telas. Nao basta contar campos ou verificar apenas que o texto mudou.

Edicoes invariantes podem ser corretas: potencia nao depende da fase global,
RMS triangular nao depende da escala de tempo, impedancia fixa nao depende
de omega. Examine os casos registrados em unchanged-edits.json; nunca force
uma resposta a mudar sem fundamento matematico.

Renderize depois do teste do runtime. Confira rotulos sobre componentes,
capacitancias sobre o cabecalho, textos sobre fios, footer e todos os passos.
Mantenha a geometria ligada ao modelo: mover uma ponta pode mudar a MNA.
Terminais unidos usam coordenadas exatas; setas/rotulos nao sao ramos.

O app continua iniciando na calculadora/busca. CLEAR com entrada vazia
abre o menu de conteudos; MODE edita apenas dentro de um exercicio.
Novas provas atuais podem modificar priority mediante recorrencia documentada.
