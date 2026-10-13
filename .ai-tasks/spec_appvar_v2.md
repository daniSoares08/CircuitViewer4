# CV4A AppVar v2, layout revision 3

Unico formato aceito: bytes CV4A 02 03. Rejeitar v1, CV3A e v2r2.
Inteiros little-endian, floats IEEE754 f32, texto cstr ASCII.
CV4DAT0.8xv, CV4DAT1.8xv... arquivados; gerador usa payloads <60.000 bytes.

## Chunk

~~~text
magic[4] = CV4A
version u8 = 2
layout_revision u8 = 3
n_templates u16
template_offset[n_templates] u16  # relativo ao inicio do payload
n_exercises u16
exercise_offset[n_exercises] u16
template blocks
exercise blocks
~~~

Tabelas, offsets crescentes e limites sao verificados contra ti_GetSize.
Cada bloco deve terminar EXATAMENTE no proximo offset (ultimo: fim real).
O simulador pack_v2.sim_parse_chunk e o loader C compartilham o contrato.

## Template

~~~text
n_nodes u8
omega f32
n_comps u8
repeat n_comps:
  kind u8
  na u8, nb u8
  ctrl u8
  ctrl_a u8, ctrl_b u8
  default_re f32
  default_im f32
  default_flags u8                 # total: 15 bytes/componente
n_ops u8
repeat n_ops:
  opcode u8
  a i16, b i16, c i16, d i16
  flag u8
  reg u8                          # 255: texto literal
  label cstr
n_meshes u8
repeat n_meshes:
  edge_count u8
  repeat edge_count: elem u8, sign i8
port_a u8, port_b u8               # 255: nao aplicavel
flags2 u8
~~~

flags2: bit0 pico, bit1 alvo de tensao, bit2 potencia entregue,
bit3 diagrama fasorial ao vivo. Bit3 exige diagram_only e os parametros
Acos, Asin, nesta ordem: vetor (Acos,-Asin), com escala automatica.
Nao acrescenta campos binarios nem muda a revisao de layout; use sempre
o programa e os AppVars do mesmo build para exibir esta funcionalidade.
Limites: 16 componentes, 9 nos, 6 malhas de 6 arestas.
ctrl=255 seleciona controle de tensao ctrl_a-ctrl_b para fonte dependente.
CK_ARROW nao e estampado. Ops permanecem em Flash.

## Exercise

~~~text
template_id u16                   # 65535: sem template
content_id u8
chapter u8, section u8
n_value_overrides u8
repeat: comp_idx u8, re f32, im f32
n_flag_overrides u8
repeat: comp_idx u8, flags u8
target_or_profile u8
n_params u8                       # maximo 64
repeat n_params: value f32, name cstr
title cstr
n_statement_pages u8              # maximo 4
repeat: page_block
n_tail_pages u8 = 0               # loader rejeita tail congelada
live_size u16
live_program[live_size]           # zero: usar narrador content_id
~~~

Nome de parametro <=12, unico na autoria. Valores finitos; indices validos.
content_id 0..8: impedancia, nodal, malhas, superposicao, Thevenin,
potencia, maxima transferencia, trifasico, fasores Cap. 9.
255 exige live_program; nao significa exercicio somente-leitura.

## Page block

~~~text
title cstr
subtitle cstr
result cstr
result_y u8
n_lines u8
repeat: x i16, y i16, color u8, text cstr
~~~

Statement e dado original. Dados atuais/resolucao/resultados sao gerados
em RAM a partir dos valores vigentes, sete linhas por pagina.

## Live program

~~~text
flags u8                         # bit0: solve; bit1: Vth/Zth por teste
port_a u8, port_b u8
remove_comp u8                   # 255: nao remover
n_opamps u8                      # <=4
repeat: output u8, plus u8, minus u8
n_steps u8                       # <=64
repeat:
  label cstr                     # <=34
  formula cstr                   # <=37
  unit cstr                      # <=8
  mode u8                        # 0 interno, 1 retangular, 2 polar
  expr_size u16
  expr_bytecode[expr_size]
~~~

Expressoes postfix. CONST carrega f32; PARAM/COMP/Z/NODE/CURRENT/POWER/VAR
carregam indice u8; OMEGA/VTH/ZTH nao carregam argumento.
Todas as expressoes devem terminar com um valor na pilha limitada de 24.
Referencias VAR apontam apenas para etapas anteriores.
Indices/ranges, texto e comprimento sao limitados em compilacao e runtime.

| Codigo | Operacao |
|---:|---|
| 1 | CONST f32 |
| 2--8 | PARAM, COMP, Z, NODE, CURRENT, POWER, VAR |
| 9--11 | OMEGA, VTH, ZTH |
| 20--25 | ADD, SUB, MUL, DIV, NEG, POW |
| 30--35 | ABS, ARG, REAL, IMAG, CONJ, SQRT |
| 36--42 | SIN, COS, TAN, ACOS, ATAN, EXP, LOG |
| 43--49 | POLAR, COMPLEX, MIN, MAX, CSQRT, SOLVE, GUARD |
| 50--53 | EQ, LT, LE, AND |

SOLVE consome (omega, mascara de fontes independentes). Indices de componente
definem bits da mascara u16. Dependentes permanecem ativas.
remove abre a carga sem reindexar componentes. AOP impõe V+=V-.
POWER e potencia passiva V conj(I); autor aplica /2 quando fasores sao pico.
Trigonometria/ARG/POLAR em graus; omega em rad/s.

Mudancas do layout exigem incrementar revision e regerar programa E dados.
Nao interpretar bytes da revisao anterior com o novo leitor.
