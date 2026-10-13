# Novas provas e lista - CV4

Fonte autorizada: exclusivamente PROVAS/NOVAS_PROVAS/ (oito PDFs).
Inventario: 75 questoes numeradas, alem de referencias a exercicios do
livro ja presentes no catalogo. Paginas de resolucao/comentarios nao sao
novas questoes. Enunciado prevalece sobre gabarito inconsistente.

Cada ocorrencia e registrada em tools/content/exams.py com documento,
pagina PDF e questao. Repeticoes exatas apontam para um exercicio canonico;
valores ou perguntas diferentes recebem variante propria. A prioridade
do exercicio dentro de seu assunto cresce com a recorrencia confirmada.

## Checkpoints

Apos CADA questao: gerador, catalogo, cobertura da fonte, teste numerico,
mutacao do editor C, renderizacao das telas e compilacao CEdev.
O pacote aprovado e copiado para releases/provas/NNN-documento-qXX/.
O arquivo checkpoint.json registra os arquivos, tamanhos e SHA256.
O conteudo autoral das provas tambem e salvo junto do pacote.

O ultimo checkpoint fica indicado em .ai-tasks/exams-progress.json.
Em caso de interrupcao, use o pacote completo daquele diretorio; bin/
pode estar sendo refeito para a questao seguinte. Nao misture programa
e AppVars de checkpoints diferentes. Arquive todos os CV4DAT na TI.

Retomada: confira OCCURRENCES, o ultimo checkpoint e a cobertura pendente.
Nao recrie questoes aprovadas. Nenhum checkpoint antigo deve ser apagado.
Nenhum commit autorizado. Teste fisico ainda necessario.

~~~powershell
python tools/checkpoint_exam.py
python tests/test_exam_coverage.py --complete
~~~

O checkpoint 000-base preserva o pacote anterior de 374 exercicios.

## Fechamento de 2026-10-06

Cobertura completa: 75/75 questoes numeradas e 18/18 referencias ao livro.
Sao 66 novos exercicios canonicos e nove repeticoes exatas reutilizadas.
O catalogo passou de 374 para 440 entradas, todas editaveis, com
374 receitas em Flash e 66 narradores, 287 figuras (43 novas),
1.074 parametros escalares e 280 templates. Formato v2r3 mantido.

As referencias do livro apontam para 19 entradas existentes: 11.41 tem
as variantes a/b. Nao duplicar essas entradas nem carregar o catalogo
das versoes anteriores. So estes oito PDFs foram autorizados nesta entrega.

### Documentos

| Codigo | PDF | Questoes numeradas |
|---|---|---:|
| L25 | Lista-de-exercicios_2025-1.pdf | 40 |
| R1A | P1-Rec_2025-05-15_versaoA_com-resolucao.pdf | 5 |
| P1B | P1_2025-05-07_versaoB_com-resolucao.pdf | 6 |
| R2A | P2-Rec_2025-06-25_versaoA_com-resolucao.pdf | 6 |
| P2A | P2_2025-06-18_versaoA_com-resolucao.pdf | 5 |
| P2B | P2_2025-06-18_versaoB_com-resolucao.pdf | 5 |
| P22 | Prova2_2022-11_Voldi_CA_versaoA.pdf | 4 |
| T26 | Teste1_2026_com-resposta-do-professor.pdf | 4 |

### Questao -> exercicio canonico

O titulo exibido de uma repeticao e o do exercicio canonico. Por exemplo,
L25 Q14 aparece como Problema 9.35, e R2A Q5 como P2A Q4.
A prioridade negativa considera ocorrencias e referencias confirmadas
nos PDFs, dentro do conteudo correspondente.

| Origem | Pagina PDF | ID canonico |
|---|---:|---|
| L25 Q1 | 1 | e_l25_01 |
| L25 Q2 | 1 | e_l25_02 |
| L25 Q3 | 1 | e_l25_03 |
| L25 Q4 | 1 | e_l25_04 |
| L25 Q5 | 1 | e_l25_05 |
| L25 Q6 | 1 | e_l25_06 |
| L25 Q7 | 1 | e_l25_07 |
| L25 Q8 | 1 | e_l25_08 |
| L25 Q9 | 1 | e_l25_09 |
| L25 Q10 | 1 | e_l25_10 |
| L25 Q11 | 2 | e_l25_11 |
| L25 Q12 | 2 | e_l25_12 |
| L25 Q13 | 2 | e_l25_13 |
| L25 Q14 | 2 | p9_35 |
| L25 Q15 | 2 | e_l25_15 |
| L25 Q16 | 3 | e_l25_16 |
| L25 Q17 | 3 | e_l25_17 |
| L25 Q18 | 3 | p9_37 |
| L25 Q19 | 3 | e_r1a_02 |
| L25 Q20 | 3 | e_p1b_03 |
| L25 Q21 | 4 | e_l25_21 |
| L25 Q22 | 4 | p10_1 |
| L25 Q23 | 4 | e_l25_23 |
| L25 Q24 | 4 | e_l25_24 |
| L25 Q25 | 4 | e_l25_25 |
| L25 Q26 | 5 | e_l25_26 |
| L25 Q27 | 5 | e_l25_27 |
| L25 Q28 | 5 | e_l25_28 |
| L25 Q29 | 5 | e_l25_29 |
| L25 Q30 | 5 | e_l25_30 |
| L25 Q31 | 5 | e_l25_31 |
| L25 Q32 | 6 | e_l25_32 |
| L25 Q33 | 6 | e_l25_33 |
| L25 Q34 | 6 | e_l25_34 |
| L25 Q35 | 6 | e_r2a_03 |
| L25 Q36 | 6 | e_l25_36 |
| L25 Q37 | 6 | e_l25_37 |
| L25 Q38 | 6 | e_l25_38 |
| L25 Q39 | 7 | e_l25_39 |
| L25 Q40 | 7 | e_l25_40 |
| P1B Q1 | 1 | e_p1b_01 |
| P1B Q2 | 1 | e_p1b_02 |
| P1B Q3 | 2 | e_p1b_03 |
| P1B Q4 | 2 | e_p1b_04 |
| P1B Q5 | 3 | e_p1b_05 |
| P1B Q6 | 4 | e_p1b_06 |
| P22 Q1 | 1 | e_t26_02 |
| P22 Q2 | 1 | e_p22_02 |
| P22 Q3 | 1 | e_p22_03 |
| P22 Q4 | 1 | e_p22_04 |
| P2A Q1 | 1 | e_p2a_01 |
| P2A Q2 | 1 | e_p2a_02 |
| P2A Q3 | 2 | e_p2a_03 |
| P2A Q4 | 2 | e_p2a_04 |
| P2A Q5 | 3 | e_p2a_05 |
| P2B Q1 | 1 | e_p2b_01 |
| P2B Q2 | 1 | e_p2b_02 |
| P2B Q3 | 2 | e_p2b_03 |
| P2B Q4 | 2 | e_p2b_04 |
| P2B Q5 | 3 | e_p2b_05 |
| R1A Q1 | 1 | e_r1a_01 |
| R1A Q2 | 2 | e_r1a_02 |
| R1A Q3 | 3 | e_r1a_03 |
| R1A Q4 | 4 | e_p22_03 |
| R1A Q5 | 5 | e_r1a_05 |
| R2A Q1 | 1 | e_r2a_01 |
| R2A Q2 | 1 | e_r2a_02 |
| R2A Q3 | 2 | e_r2a_03 |
| R2A Q4 | 2 | e_r2a_04 |
| R2A Q5 | 2 | e_p2a_04 |
| R2A Q6 | 3 | e_r2a_06 |
| T26 Q1 | 1 | e_t26_01 |
| T26 Q2 | 1 | e_t26_02 |
| T26 Q3 | 2 | e_t26_03 |
| T26 Q4 | 3 | e_t26_04 |

### Referencias da pagina 1 da lista L25

| Problema | ID existente |
|---|---|
| 9.35 | p9_35 |
| 9.37 | p9_37 |
| 9.43 | p9_43 |
| 9.44 | p9_44 |
| 9.56 | p9_56 |
| 10.1 | p10_1 |
| 10.7 | p10_7 |
| 10.26 | p10_26 |
| 11.1 | p11_1 |
| 11.8 | p11_8 |
| 11.15 | p11_15 |
| 11.38 | p11_38 |
| 11.41 | p11_41a, p11_41b |
| 11.53 | p11_53 |
| 11.69 | p11_69 |
| 12.7 | p12_7 |
| 12.14 | p12_14 |
| 12.25 | p12_25 |

### Convencoes e divergencias conferidas

Enunciado e figura prevalecem sobre as contas impressas. Todas as fontes
desenhadas conservam edicao de magnitude, fase e inversao de polaridade.
R, C, L e Z usam registros eletricos; outras grandezas fornecidas sao
parametros. Resposta, resolucao e diagrama fasorial usam dados atuais.

Em L25 Q36 e Q38, Zs aparece sem valor no desenho: assume-se fonte ideal,
explicitamente no enunciado do app. Em L25 Q39, o texto usa VAN numa fonte
delta; interpreta-se a tensao de fase VP como Vab, conforme o desenho.
L25 Q28 tem omega=100 pi, nao 100; Q13 tem fonte 100 V, nao 10 V.

Receitas de ondas desprezam partes de S menores que 1e-7 |S|, limitadas
pela precisao float; isso evita micro-VAR espurios numa carga resistiva.
Nao e um piso absoluto em SI e nao impede editar componentes pequenos.

As conversoes delta/Y de fonte sao equivalencias de tensao terminal;
edite as fontes do modelo equivalente. Os casos de tres fios preservam
o neutro flutuante quando os dados sao desequilibrados; nao acrescentar
um quarto fio para simplificar o calculo. L25 Q24 resolve por MNA cada
frequencia com sua mascara de fontes e soma somente no dominio do tempo.

- P22 Q1: Mesmos valores, tres ramos em paralelo; solicita Zeq.
- P22 Q2: Fonte dependente injeta 0.5 Ix no no superior; KCL: Ic=1.5 Ix.
- R1A Q1: Seno convertido para cosseno; nao usar a fase do gabarito sem -90deg.
- R1A Q4: Mesma rede e mesmos fasores: duas malhas horarias.
- R1A Q5: Gabarito soma retangular incorreta; recalcule V_Is e V_Vs sem arredondar.
- P2A Q1: Q em VAR; calcular Z com corrente RMS. Gabarito mistura Irms e Ipico.
- P2A Q3: Potencia aparente e |Sk|, nao Sk. Q=-913.45 VAR.
- P2A Q5: Gabarito usa ACB, mas o enunciado exige ABC. Correntes recalculadas para ABC.
- R2A Q2: Diferenca de fase -10deg: FP=cos(10), nao 0.866 do gabarito.
- R2A Q3: O PDF troca VL=380 por 400 no calculo; usar o enunciado.
- R2A Q4: 220 V no enunciado; a resolucao impressa troca indevidamente por 200 V.
- R2A Q5: Mesma carga delta, fonte ABC e Vab=380/_0 V RMS.
- L25 Q14: Exatamente o problema 9.35: 50 cos(200t), R10, C5mF, L20mH.
- L25 Q18: Admitancia do mesmo paralelo 4, j8 e -j10 ohm do livro.
- L25 Q19: Mesmos dados, sentido de Io e pedido no dominio do tempo.
- L25 Q20: Mesma fonte 120/_10 e mesma rede 2 + [(4-j6)||(3+j4)].
- L25 Q22: Mesmo circuito e fonte 2 cos(10t) V do problema 10.1.
- L25 Q35: Mesma carga delta: P=5kW, FP=0.8, VL=380V RMS.
- L25 Q36: Desenho Y-Y: nao confundir a carga estrela com delta. Zs sem valor: fonte ideal.
- L25 Q38: Zs sem valor no desenho: fonte ideal. Nao omitir Zlinha=1+j2.
- L25 Q39: O texto chama a tensao de fase delta de VAN. Interpretar VP como Vab conforme a figura.

### Validacao final

- 4.542 cenarios do leitor/editor C: valores, fase, polaridade, frequencia,
  parametros, resolucao e resultados; zero falhas.
- 3.790 cenarios de receitas em float contra double/MNA independente;
  66 novas referencias numericas derivadas das fontes; zero falhas.
- Diagrama fasorial executado pelo desenhador C depois de editar:
  sete casos, eixos, quatro quadrantes, zero e escalas pequenas/grandes.
- Regressao C em double/float; validacao binaria, cobertura integral,
  ASCII, topologia e ausencia de pernas soltas.
- 43 figuras novas e 389 paginas de texto/resolucao renderizadas;
  revisao visual das figuras e das telas de calculo em 320x240.
- Compilacao apos cada questao, checkpoints recuperaveis e build final limpo.
- Hardware: NAO testado nesta entrega; teste na TI-84 Plus CE ainda necessario.

Pacote final: CIRCVIE4.8xp e CV4DAT0.8xv ate CV4DAT4.8xv (seis arquivos).
Use o ultimo diretorio informado em .ai-tasks/exams-progress.json.
Todos os cinco AppVars precisam estar arquivados e ser do mesmo build.
Os checkpoints anteriores permanecem preservados; nenhum commit realizado.
