# Manifesto do catalogo CIRCVIE4

Atualizado em 2026-10-06: todas as entradas numericas possuem recalculo de
resposta E resolucao na abertura e depois de editar.

| Capitulo | Entradas | Parametros escalares |
|---|---:|---:|
| 9: 9.1--9.93 | 93 | 381 |
| 10: 10.1--10.96 | 96 | 23 |
| 11: 11.1--11.97, 11.41a/b | 98 | 299 |
| 12: 12.1--12.87 | 87 | 234 |
| Subtotal livro | 374 | 937 |
| Provas/lista: 66 variantes novas | 66 | 137 |
| Total | 440 | 1074 |

287 figuras (269 eletricas, 18 explicativas).
280 templates globais; 5 AppVars CV4A v2r3.
374 receitas matematicas em Flash e 66 narradores numericos.
Nao ha tail de resposta fixa nem rota que mande refazer a substituicao.

## Prioridade do professor

- Cap. 9: 9.35, 9.37, 9.43, 9.44, 9.56;
- Cap. 10: 10.1, 10.7, 10.26;
- Cap. 11: 11.1, 11.8, 11.15, 11.38, 11.41a/b, 11.53, 11.69;
- Cap. 12: 12.7, 12.14, 12.25.

A ultima referencia do bloco Cap. 12 foi interpretada como 12.25.
O 11.41 possui duas redes, por isso 97 numeros geram 98 registros.

## Cobertura atual

Cap. 9: expressoes complexas, fasores, derivadas/integrais, redes RLC,
pontes e projetos. Entradas de sistemas/operacoes sao operandos reais do
enunciado, nao copias dos resultados anteriormente calculados.

Cap. 10: nodal/malhas, Thevenin, superposicao por frequencia, AOPs ideais,
transferencias e osciladores. AOPs incluem as restricoes V+=V-.
Casos com frequencias distintas conservam parcelas independentes.

Cap. 11: potencia instantanea/media, maxima transferencia, RMS por trechos,
P/Q/S/FP, cargas nominais, compensacao e wattimetros. O fator pico/RMS segue
a nota do livro. Cargas em W/VA/FP nao sao resistores ficticios editaveis.

Cap. 12: Y/delta, equilibrio/desequilibrio, neutro, redes com perdas,
potencia, compensacao e metodos de dois/tres wattimetros.
Nos casos especificados por potencias, fontes continuam editaveis e
correntes sao recalculadas a partir de S e V.

## Validacao e rastreabilidade

tests/test_all_editable_routes.py executa 4.542 cenarios no leitor/editor C
dos 440 itens. tests/test_live_recipes.py compara 3.790 cenarios das 374
receitas em float com calculo double e MNA independente. Os testes C
complementam as referencias dos narradores e exercicios selecionados.

Edicoes matematicamente invariantes/arredondadas sao registradas separadamente.
Dados invalidos devem exibir erro, nunca reutilizar resposta antiga.
Houve revisao numerica e visual dos casos corrigidos; ver o relatorio
EDITABLE_RESOLUTION_AUDIT.md. Essa bateria nao equivale a uma nova
conferencia manual de todos os enunciados nem a um teste em hardware.

## Fontes e pacote

Livro base continua sendo referencia. Os oito PDFs autorizados em
PROVAS/NOVAS_PROVAS foram incluidos: 75 questoes numeradas e 18 referencias
ao livro. Repeticoes exatas reutilizam o ID canonico; recorrencia aumenta
prioridade. Veja EXAMS_MANIFEST.md para cobertura, convencoes e checkpoints.
Provas fora dessa pasta e catalogos legados permanecem fora da geracao.

Fontes autorais: tools/content/ e os tres modulos live_*.py.
Gerados: src/exercises.c e bin/.
Pacote: CIRCVIE4.8xp e CV4DAT0.8xv a CV4DAT4.8xv, todos do mesmo build.
Previews: tmp/catalog-render/. Relatorio de telas: tmp/live-qa/.

Alteracoes sao temporarias em RAM e restauradas ao reabrir.
Nao commitar sem autorizacao.
