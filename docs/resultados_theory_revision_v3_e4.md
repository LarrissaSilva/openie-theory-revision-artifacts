# Resultados da primeira Theory Revision exploratória de E4

## Qualificadores epistemológicos

- **FATO OBSERVADO NO DPTOIE:** sustentado por planilha, parse, output ou trace de uma execução anterior do extrator.
- **RESULTADO FORMAL DO MODELO:** produzido pela execução do notebook v3 em Graph Rewriting; não equivale a execução do DptOIE.
- **HIPÓTESE LINGUÍSTICA:** classificação provisória fornecida manualmente ao modelo.
- **LIMITAÇÃO:** aspecto que impede interpretar o resultado como validação geral ou independente.

## 1. Objetivo e protocolo

O experimento avaliou três revisões candidatas da regra de construção associada à divergência E4 de S009. O objetivo foi verificar se cada candidato transferia a preposição `para` de ARG1 para REL nos quatro outputs E4 da sentença e preservava os quatro controles modelados.

O protocolo foi registrado **antes da implementação e execução**:

- arquivo: `docs/protocolo_theory_revision_e4.md`;
- commit: `79e77b8fb8408fb64a8936ff77c76a0a030e2031`;
- SHA-256 atual: `7e63d1aa217d0b860f3a1de5ae6ed367b67a6b4d8197db75e7b459d4966403cb`.

## 2. Ambiente e procedimento efetivamente utilizados

- Python `3.12.0` 64-bit;
- NetworkX `3.5`;
- openpyxl `3.1.5`;
- nbformat `5.10.4`;
- nbclient `0.11.0`;
- ipykernel `6.29.5`;
- IPython `9.4.0`.

Notebook executado:

- `research/graph_rewriting/experimento_v3_e4_theory_revision.ipynb`;
- SHA-256: `da2ef408d976a4afea809b21c23a63413414b25463ef6bdfcadcf24b67ddd099`;
- 14 células, das quais 7 de código;
- células executadas uma vez e em ordem, com `execution_count=1..7`;
- 6 blocos de output;
- zero outputs de erro;
- notebook validado com `nbformat` antes e depois da execução.

Os hashes da planilha e dos quatro CoNLL foram verificados pelo notebook antes da construção dos casos. Foram construídos grafos independentes para oito extrações e cada um recebeu C0, C1 e C2, totalizando 24 testes. Cada grafo de entrada continha dependências, ARG0 e candidato a núcleo de REL, mas nenhuma aresta REL ou ARG1. Os componentes resultantes foram adicionados somente após o matching; portanto, os candidatos atuaram na construção e não corrigiram um `G_impl` já produzido.

O DptOIE não foi executado, nenhum solver foi utilizado e nenhum arquivo Java foi alterado.

## 3. Modificações ou desvios em relação ao protocolo

Não houve desvio científico do espaço de hipóteses, dos casos selecionados, das classificações de regência ou dos critérios de avaliação.

Registro técnico:

- a execução foi feita diretamente com `nbclient 0.11.0`, pois `nbconvert` não está instalado no ambiente;
- o processo externo apresentou apenas um aviso do ZMQ sobre o event loop Proactor do Windows; nenhuma célula falhou e o aviso não integra os outputs científicos;
- conforme previsto no protocolo, não foi declarada não regressão das 15 extrações dos controles: somente quatro desses outputs possuíam representação completa neste notebook.

## 4. Resultados individuais dos candidatos

### C0 — transferência sem guarda de regência

**RESULTADO FORMAL DO MODELO:** C0 corrigiu o aspecto E4 nos quatro casos S009, mas sobreaplicou em três controles:

- S005-A28: transferiu `para` para REL, produzindo `REL=tem para` e removendo `para` do argumento;
- S010-A51: transferiu `en`, produzindo `REL=visitei en`;
- S010-A52: transferiu `en` e `para`, produzindo `REL=visitei en para`;
- S003-A20: preservou o baseline.

Classificação global: `FAIL_OVERAPPLICATION`.

### C1 — `case+nmod`

**RESULTADO FORMAL DO MODELO:** C1 corrigiu o aspecto E4 nos quatro casos S009 e preservou S005-A28 e S003-A20. Entretanto, o padrão `case(p,n) ∧ nmod(n,v)` também ocorreu no locativo de S010:

- S010-A51: transferiu `en` para REL;
- S010-A52: transferiu `en` para REL, mantendo `para` no argumento porque este possui `deprel=mark`.

Classificação global: `FAIL_OVERAPPLICATION`.

Esse resultado demonstra, dentro dos casos modelados, que `case+nmod` não discrimina sozinho regência verbal de uma estrutura locativa.

### C2 — ramo conservador por estado explícito de regência

**RESULTADO FORMAL DO MODELO:** C2 transferiu `para` nos quatro casos S009, todos anotados como `TRUE_PROVISIONAL`, e usou o ramo conservador em todos os pares dos controles, anotados como `FALSE_PROVISIONAL`.

- A41: `REL=voltou para`; `ARG1=a área`;
- A42: `REL=voltou para`; `ARG1=a área depois de viver em Londres`;
- A43/A44: apenas `para` mudou de componente; as sobras E3/S3 permaneceram;
- S005-A28, S010-A51/A52 e S003-A20: componentes baseline preservados.

Classificação global: `PASS_EXPLORATORY`.

**LIMITAÇÃO CENTRAL:** C2 recebeu o estado de regência manualmente. O resultado demonstra que a divisão da regra usa essa anotação de maneira consistente; não demonstra capacidade operacional de reconhecer `Rege(v,p)`.

## 5. Matriz completa de testes

| Caso | Tipo | C0 | Tokens transferidos C0 | C1 | Tokens transferidos C1 | C2 | Tokens transferidos C2 |
|---|---|---|---|---|---|---|---|
| S009-A41 | E− primário | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` |
| S009-A42 | variante E− | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` |
| S009-A43 | misto E4+E3+S3 | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` |
| S009-A44 | misto E4+E3+S3 | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` | PASS_EXPLORATORY | `para(3)` |
| S005-A28 | controle | FAIL_OVERAPPLICATION | `para(18)` | PASS_EXPLORATORY | nenhum | PASS_EXPLORATORY | nenhum |
| S010-A51 | controle | FAIL_OVERAPPLICATION | `en(6)` | FAIL_OVERAPPLICATION | `en(6)` | PASS_EXPLORATORY | nenhum |
| S010-A52 | controle | FAIL_OVERAPPLICATION | `en(6), para(11)` | FAIL_OVERAPPLICATION | `en(6)` | PASS_EXPLORATORY | nenhum |
| S003-A20 | controle | PASS_EXPLORATORY | nenhum | PASS_EXPLORATORY | nenhum | PASS_EXPLORATORY | nenhum |

Resumo global:

| Candidato | Classificação |
|---|---|
| C0 | `FAIL_OVERAPPLICATION` |
| C1 | `FAIL_OVERAPPLICATION` |
| C2 | `PASS_EXPLORATORY` |

## 6. Asserções executadas

As asserções verificaram:

- integridade SHA-256 da planilha e dos quatro parses;
- exatamente 8 casos e 24 testes;
- ausência de REL/ARG1 nos grafos de entrada;
- presença de ARG0 nos grafos de entrada;
- estado exato de A41 após C0, C1 e C2: `ARG0=[1]`, `REL=[2,3]`, `ARG1=[4,5]`;
- resultados globais C0/C1/C2;
- sobreaplicação de C0 em S005;
- preservação de S005 por C1;
- sobreaplicação de C1 em S010-A51;
- `PASS_EXPLORATORY` de C2 nos oito casos;
- ausência de transferência por C2 nos controles;
- transferência do token 3 por C2 nos quatro casos S009;
- impossibilidade de declarar não regressão completa das 15 extrações.

Resultado das asserções: `PASS`.

## 7. Análise das correções produzidas

Nos quatro casos S009, os três candidatos produziram a mesma alteração de E4:

\[
ARG1(e,para) \longrightarrow REL(e,para)
\]

O núcleo `voltou`, ARG0 e todos os demais tokens permaneceram em seus componentes anteriores. A41 e A42 passaram a coincidir com o GOLD por fronteira de tokens. A43 e A44 continuaram diferentes do GOLD completo porque seus argumentos preservaram material adicional associado a E3/S3. Essa persistência é esperada e impede apresentar C0/C1/C2 como correção integral desses dois outputs.

O resultado de S009 é uma demonstração formal dentro do modelo. A única evidência empírica direta do mecanismo do DptOIE continua sendo a proveniência anteriormente observada em A41.

## 8. Sobreaplicação e regressões

C0 não separou a preposição regida de marcadores de finalidade ou locativos. C1 eliminou a sobreaplicação em `mark`, mas permaneceu incapaz de distinguir o `case+nmod` direcional de S009 do `case+nmod` locativo de S010.

C2 preservou os quatro controles modelados. Essa preservação é condicional às anotações `FALSE_PROVISIONAL`; não constitui evidência de que uma implementação futura classificaria automaticamente esses casos.

A diferença `en a`/`em a` de S010 foi mantida como divergência superficial. O teste avaliou identidade de fronteiras e mudança de componente, sem normalizar o token `en` para forçar igualdade textual.

Estado da não regressão ampla: `INCONCLUSIVE_NOT_FULLY_MODELED`. Quatro dos 15 outputs baseline dos controles foram testados; os outros 11 não foram representados e não são declarados preservados.

## 9. Complexidade e minimalidade estrutural

| Candidato | Guardas | Efeitos | Intervalo | Divisão de regra | Total | Resultado global |
|---|---:|---:|---:|---:|---:|---|
| C0 | 0 | 2 | 1 | 0 | 3 | FAIL_OVERAPPLICATION |
| C1 | 2 | 2 | 1 | 0 | 5 | FAIL_OVERAPPLICATION |
| C2 | 1 | 2 | 1 | 1 | 5 | PASS_EXPLORATORY |

C0 é a menor edição, mas não satisfaz os controles. C1 e C2 possuem a mesma soma segundo a métrica pré-registrada, embora distribuam a complexidade de forma diferente. Portanto, o experimento não sustenta escolher C2 por menor distância de edição; sustenta apenas que C2 foi o único candidato que satisfez os casos modelados.

## 10. Discussão das hipóteses

- **H0/C0: refutada nos dados modelados.** A estrutura operacional permissiva também casou com finalidade e locativos.
- **H1/C1: refutada nos dados modelados.** `case+nmod` corrigiu S009, mas sobreaplicou no locativo de S010.
- **H2/C2: sustentada condicionalmente dentro do modelo.** O ramo verdadeiro corrigiu S009 e o ramo conservador preservou os controles quando recebeu as classificações manuais.

Não se conclui que C2 seja superior em geral. O teste não avaliou reconhecimento automático de regência, E+ E4 verdadeiros ou contextos E− independentes.

## 11. Limitações e ameaças à validade

- As quatro ocorrências E4 derivam da mesma sentença.
- Apenas A41 possui proveniência detalhada do código.
- Não há E+ específico de E4 confirmado no conjunto.
- O estado de regência foi fornecido manualmente e é provisório.
- O GOLD fundamentou parte da classificação e foi usado na avaliação, logo não há validação independente.
- Os controles não foram demonstrados como instâncias do mesmo mecanismo interno de A41.
- S003 possui parse global discutível.
- Apenas quatro dos 15 outputs baseline dos controles foram modelados.
- Os resultados são formais no Graph Rewriting e não demonstram comportamento de uma versão Java revisada.

## 12. Conclusão científica sustentada

Dentro do espaço de hipóteses e dos oito casos modelados:

1. transferir a preposição sem guarda de regência é insuficiente;
2. usar apenas `case+nmod` também é insuficiente;
3. uma divisão conservadora condicionada por uma anotação explícita de regência produz o estado esperado de E4 em S009 e preserva os controles modelados;
4. esse resultado valida o **uso** da anotação no modelo, não a sua descoberta pelo sistema;
5. nenhuma regra revisada do DptOIE foi implementada ou validada.

Assim, C2 é o candidato exploratório que satisfez este conjunto fechado, mas ainda não é `R'_impl` generalizada nem revisão pronta para o código.

## 13. Próximos experimentos necessários

1. obter E− E4 de sentenças independentes, com outros verbos, preposições e padrões de dependência;
2. obter E+ E4 do próprio DptOIE, nos quais a condição seja aplicável e a preposição já esteja corretamente em REL;
3. ampliar controles com padrões sintáticos semelhantes a S009, mas `Rege(v,p)` falso;
4. investigar uma representação operacional observável para regência que não dependa diretamente do GOLD;
5. modelar ou executar a não regressão dos 11 outputs dos controles ainda não representados;
6. somente depois avaliar uma implementação Java e repetir reprodução, proveniência e não regressão.

## Natureza das evidências

**Empírico no DptOIE:** parses preservados, outputs baseline, GOLD da planilha e trace anterior de A41.

**Formal no modelo:** matches de C0/C1/C2, grafos resultantes, diffs, métricas de edição, asserções e classificações deste notebook.

**Ainda não demonstrado:** reconhecimento operacional de regência, generalização, equivalência funcional no Java e revisão validada de E4.
