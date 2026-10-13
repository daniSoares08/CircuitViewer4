# Motor CA implementado

Contrato detalhado: spec_v4_engine.md e spec_appvar_v2.md (v2r3).

MNA fasorial, impedancias R+jX, C/L fisicos, fontes V/I independentes
e dependentes, AOP ideal. Edicao de componentes, fases, orientacao,
frequencia positiva e ate 64 parametros escalares nomeados.
Receitas de algebra/RMS/projeto e narradores recalculam resposta e passos
na primeira abertura e depois de editar. Nao ha resolucao congelada.

## Formulas e convencoes

~~~text
ZL=jwL; ZC=1/(jwC)
S_RMS=V conj(I); S_pico=V conj(I)/2
Pmax_RMS=|Vth|^2/(4Rth)
Pmax_pico=|Vth|^2/(8Rth)
ZL_otimo=conj(Zth)             # carga complexa
RL_otimo=|Zth|                # restricao puramente resistiva
ZY=Zdelta/3
Vfase=Vlinha/sqrt(3) com fase relativa correta
Wattimetro: W=Re(Vbobina conj(Ibobina))
~~~

Pico/RMS nao deve ser inferido pela aparencia da fonte.
No Cap. 11, antes de 11.22 usar pico, salvo indicacao especifica.
Frequencias diferentes sao resolvidas por parcelas e somadas no tempo.
No submodelo DC: C abre, L fecha; fonte CA inativa vira zero,
mas dependentes continuam presentes.

## Referencias selecionadas

9.35: 4.789 A /_-16.70 graus; 9.37: Y=250-j25 mS;
9.43: 499.7 mA /_-28.85; 9.44: 0.9601 A /_-7.955;
9.56: |Z|=41.9544 ohm /_-58.866.
10.1: 1.9704 A /_5.653; 10.7: 124.08 V /_-154.0;
10.26: 39.528 mA /_-18.435.
11.1: Pmed=13.7775 kW; 11.7: P10ohm=160 W;
11.8: P40ohm=43.78 W (pico, NAO 87.57 W RMS);
11.15: ZL=0.5-j0.5 ohm, Pmax=90 W.
12.7: Ia=44 A /_53.13; 12.25: Ia=17.74 A /_4.775.
12.66: W1=360 W, W2=300 W, W3=240 W.

Referencias sao testes, nunca constantes da resposta do runtime.

## Capacidade e teste

9 nos, 20 elementos, dimensao real maxima 32 na MNA complexa;
16 registros de componentes, 64 parametros, 64 linhas, 32 paginas.
VM: 64 variaveis derivadas e pilha de 24 valores complexos.

Use tests/run_host_tests.py e tests/test_all_editable_routes.py.
Regressao float reproduz a precisao da calculadora; numerica independente
usa double. O build CEdev e uma verificacao adicional distinta do host.
