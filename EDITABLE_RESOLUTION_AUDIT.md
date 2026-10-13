# Auditoria de edicao, respostas e resolucoes do CV4

Data: 2026-10-04. Escopo: catalogo atual dos capitulos 9 a 12.
Nao foram incluidos exercicios antigos nem provas anteriores.

Este e o registro historico da base de 374 entradas. A extensao de
2026-10-06 inclui os oito PDFs autorizados em NOVAS_PROVAS e eleva o total
para 440. A cobertura, testes e checkpoints atuais estao em EXAMS_MANIFEST.md.

## Resultado

Todas as 374 entradas executam calculo na abertura e depois da edicao.
O pacote contem 308 receitas matematicas compiladas e 66 rotas de
narradores numericos. Nenhuma entrada utiliza uma resposta congelada
como substituto do calculo. Foram expostos 937 parametros escalares,
alem dos componentes, fases, orientacoes de fontes e frequencias.

As paginas de resolucao e de resultados utilizam os mesmos resultados
calculados a partir da instancia editada. Resultados extensos sao
paginados, sem descartar valores intermediarios. O enunciado do livro
continua identificado como original; dados atuais ficam separados.

Edicoes que tornam o modelo indefinido ou singular substituem as
respostas anteriores por IMPOSSIVEL e uma explicacao. Uma entrada
matematicamente invariavel nao precisa mudar o resultado: por exemplo,
uma fonte ideal pode impor uma tensao independentemente de outra carga.

## Problemas corrigidos

- Resolucoes e respostas fixas em questoes escalares e circuitos:
  substituidas por receitas que usam os dados atuais, incluindo algebra
  complexa, formas de onda, RMS, potencia, compensacao e projeto.
- Parametros que eram copias de respostas: substituidos por operandos,
  amplitudes, fases, duracoes e dados nominais reais do enunciado.
- Limitacoes de edicao: suporte a ate 64 parametros e correcao do buffer
  do menu. Removido o piso de 0.0001 que adulterava capacitores em nF.
- Fontes: a inversao aplica o sinal ao fasor inteiro; magnitude e fase
  continuam coerentes. Ganhos e controles de dependentes sao preservados.
- Solver: AOP ideal com V+=V- e corrente de entrada zero; capacitor
  aberto e indutor em curto no DC; curto ideal para impedancia nula.
- Superposicao: cada frequencia e resolvida separadamente, mantendo
  fontes dependentes. Residuos de arredondamento de uma fase de 180 graus
  nao invalidam uma fonte DC real; fases genuinamente complexas invalidam.
- Potencia: fator pico/RMS, polaridade de wattimetros, neutro, cargas
  Y/delta e cargas especificadas por W/VA/FP corrigidos nos casos revisados.
- Formato: CV4A v2r3 valida tamanho real, offsets, contagens e bytecode;
  rejeita formatos anteriores e tails de resposta fixa.
- Apresentacao: formulas e resultados separados, prefixos adequados,
  angulos em graus, labels compactos e paginas completas de resultados.

Tambem foram corrigidos valores, conexoes ou modelos nos casos em que
a revisao do livro revelou divergencia. Entre os principais: 9.49/51/52/
54/55 (incognitas), 10.22/23 (topologia), 10.44--48 (frequencias e DC),
10.71--80 e 10.89--96 (AOPs/osciladores), 11.7/9/10 (dependentes/AOPs),
11.22--37 (RMS por trechos), 11.52/60--64/90/93/94 (cargas/projeto),
12.61/66 e 12.71--74 (trifasico/wattimetros).

## Verificacao executada

| Verificacao | Resultado |
|---|---|
| Leitor/editor C com todos os AppVars | 374 itens, 3.872 cenarios, zero falhas |
| Receitas C float contra oracle double/MNA independente | 308 receitas, 3.120 cenarios, zero falhas |
| Regressoes C de formatacao, MNA e narradores | 11 execucoes, todas aprovadas |
| Catalogo e empacotamento | 374 rotas vivas, 937 parametros, 238 templates, quatro chunks |
| Topologia | 227/227 redes derivadas; 1.280 elementos; zero valores simbolicos desconhecidos |
| Pernas desconectadas | Zero problemas identificados pelo auditor |
| Strings | ASCII e limites de largura aprovados |
| Parser binario | Round-trip e rejeicao de chunks truncados/corrompidos aprovados |
| Baseline regenerada | Nove entradas de tamanho/hash verificadas |
| Build CEdev | CIRCVIE4.8xp gerado com sucesso |

Cada valor de componente e parametro foi perturbado individualmente;
tambem foram testadas fases, inversao de fontes e frequencia, onde cabivel.
As receitas comparam todos os valores derivados, nao apenas a ultima
resposta. Referencias numericas selecionadas usam calculos manuais e o
livro, complementando a comparacao entre implementacoes.

O teste integral executa o loader, as APIs de edicao, o recalculo,
a paginacao e as funcoes de desenho C com primitivas graficas substituidas
no host. Verifica limites de texto/paginas, ausencia de NaN/inf e presenca
dos resultados da resolucao nas paginas de resultados atuais.

236 edicoes invariantes ou arredondadas foram registradas em
tmp/live-qa/unchanged-edits.json. Esse numero inclui paginas que mantem
o mesmo texto; nao e uma lista de falhas de recalculo.

## Verificacao visual e limites

O renderer utiliza tmp/live-qa/runtime-pages.json: sao as paginas reais
do runtime C, nao as antigas respostas estaticas dos arquivos autorais.
As figuras e telas corrigidas foram inspecionadas; os previews completos
ficam em tmp/catalog-render/.
Foram renderizadas 244 figuras e 2.137 paginas de texto, organizadas em
150 folhas de contato. Os limites de coordenadas e texto foram aprovados.

Coordenadas validas e testes numericos nao garantem, isoladamente, ausencia
de sobreposicoes nem fidelidade de todo enunciado ao livro. Esta auditoria
nao representa uma nova conferencia manual de todos os 374 enunciados,
nem inspecao visual individual de todas as telas. O renderer do host
aproxima a fonte da calculadora; hardware pode apresentar diferencas.

Nao foi realizado teste na calculadora fisica nem confirmado o consumo
de RAM em execucao no dispositivo. A entrada via teclado tambem precisa
de teste fisico; no host foram exercitadas as APIs utilizadas pelo editor.

Edicoes sao temporarias e restauradas ao reabrir o exercicio. Nao foi
adicionada persistencia. Valores de componentes devem ser digitados em
SI decimal: 10 nF = 0.00000001. O editor nao interpreta prefixos SI.

## Pacote para transferencia

Programa e AppVars devem ser atualizados juntos. Arquivar os quatro
AppVars na calculadora. O programa atual exige CV4A 02 03 (v2r3).

| Arquivo | Bytes |
|---|---:|
| bin/CIRCVIE4.8xp | 52.480 |
| bin/CV4DAT0.8xv | 59.821 |
| bin/CV4DAT1.8xv | 59.813 |
| bin/CV4DAT2.8xv | 59.680 |
| bin/CV4DAT3.8xv | 19.539 |

Payloads dos chunks: 59.745, 59.737, 59.604 e 19.463 bytes.
Nao misturar esses AppVars com um programa de uma revisao anterior.

## Reproducao

~~~powershell
python tools/generate_cv4.py
python tests/test_catalog.py
python tests/test_pack_v2.py
python tests/run_host_tests.py
python tests/test_all_editable_routes.py
python tools/topology.py
python tools/audit_holes.py
python tools/audit_strings.py
python tools/render_catalog.py
python tests/test_baseline.py
make
~~~

A baseline foi atualizada intencionalmente apos a revisao das mudancas;
nao usar --bless para esconder uma divergencia inesperada.
Documentacao de autoria, formato e skill local atualizadas para exigir
resposta E resolucao dinamicas. Nenhum commit foi realizado nesta tarefa.
