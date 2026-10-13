# Busca por componentes do CircuitViewer4

`Buscar` e o primeiro item do menu. O usuario informa quantidades minimas e
recebe exercicios cuja figura possui pelo menos os componentes pedidos.

## Classes e teclas

| Indice | Classe | Tecla |
|---:|---|---|
| 0 | resistor | `Y=` |
| 1 | fonte de tensao | `WINDOW` |
| 2 | fonte de corrente | `ZOOM` |
| 3 | capacitor | `TRACE` |
| 4 | indutor | `GRAPH` |

- `2nd` arma a subtracao da proxima classe;
- `alpha` mostra nomes no rodape;
- `enter` executa;
- `clear` volta;
- na lista, a navegacao e a mesma de uma secao.

Fontes dependentes contam na classe correspondente. Setas `arr_h/v` nunca
contam como fonte ou elemento.

## Dados gerados

`tools/generate_cv4.py` calcula cinco contagens por entrada e grava em
`ExMeta.counts`. Entradas sem figura usam zeros. Entradas trabalhadas com
circuito continuam pesquisaveis, embora nao sejam editaveis.

O resultado preserva a ordem global de `ex_meta[]`, que e:

```text
capitulo, secao, priority, ordem de autoria
```

Assim, diminuir `priority` tambem eleva um exercicio nos resultados da busca.
Esse e o mecanismo reservado para a recorrencia nas futuras provas do
conteudo novo.

## Provas

As provas antigas em `PROVAS/` nao podem alterar contagens nem prioridade.
Somente provas novas, conferidas e registradas em `tools/content/exams.py`,
podem justificar uma mudanca.

## Regressao

`tests/test_catalog.py` garante que setas anotativas nao criem nos ou ramos.
Ao adicionar uma op eletrica, confira tambem a contagem produzida em
`src/exercises.c` e execute uma busca manual na calculadora quando disponivel.
