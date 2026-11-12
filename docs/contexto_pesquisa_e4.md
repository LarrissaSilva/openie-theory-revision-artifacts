# Contexto do experimento E4

Este documento usa três qualificadores epistemológicos:

- **FATO**: informação registrada diretamente nos materiais fornecidos.
- **HIPÓTESE**: explicação candidata ainda não confirmada por evidência de código e execução.
- **NÃO DETERMINADO**: informação que os materiais atuais não permitem estabelecer.

## 1. Objetivo desta etapa

**FATO — objetivo metodológico desta etapa:** identificar e formalizar o mecanismo, regra ou conjunto de regras operacionais do DptOIE envolvidos na produção do erro E4, para então representar \(R_{impl}^{E4}\) e, posteriormente, comparar essa representação estruturalmente com \(R_{gold}^{E4}\).

Esta etapa **não consiste ainda em corrigir o DptOIE nem realizar Theory Revision**. Também não inclui alteração de regras de extração. O trabalho atual é de consolidação do contexto científico e preparação da investigação de proveniência.

## 2. Regra linguística E4

**FATO — regra registrada no material de formalização:**

> “Se o verbo rege uma preposição, ela deve ser incluída em REL.”

O material define os seguintes predicados:

- \(Rege(v,p)\): o verbo \(v\) rege a preposição \(p\).
- \(EmREL(x,e)\): o elemento \(x\) está incluído em REL da extração \(e\).

**FATO — formalização em Lógica de Primeira Ordem:**

\[
\forall e\; \forall v\; \forall p\; [(EmREL(v,e) \land Rege(v,p)) \rightarrow EmREL(p,e)]
\]

Leitura registrada no material: verbo em REL + verbo rege preposição → preposição em REL.

## 3. Caso experimental S009

**FATO — sentença:**

> Catalano voltou para a área depois de viver em Londres e em Glasgow, onde estudou design de jóias na Glasgow School of Art.

Na aba `analise`, S009 contém quatro comparações do extrator `DPTOIE` classificadas como `E-` e marcadas com `E4 - Preposição em REL`. Todas as quatro são preservadas abaixo.

**FATO — caso piloto primário desta primeira investigação de proveniência:**

- saída DptOIE: `(Catalano, voltou, para a área)`;
- GOLD: `(Catalano, voltou para, a área)`;
- token crítico: `para`.

As outras três extrações da mesma sentença permanecem documentadas como **variantes relacionadas**, mas não fazem parte do primeiro trace de proveniência. Elas poderão ser usadas posteriormente para verificar se o mecanismo identificado também explica outros outputs da mesma sentença.

| Linha na aba `analise` | Sistema/extrator | Saída produzida | GOLD de referência | Tipo de divergência | Elemento crítico de E4 |
|---:|---|---|---|---|---|
| 41 | `DPTOIE` | `(Catalano, voltou, para a área)` | `(Catalano, voltou para, a área)` | `E-`; “para” ficou no início do argumento em vez de integrar REL | `para` |
| 42 | `DPTOIE` | `(Catalano, voltou, para a área depois de viver em Londres)` | `(Catalano, voltou para, a área depois de viver em Londres)` | `E-`; “para” ficou no início do argumento em vez de integrar REL | `para` |
| 43 | `DPTOIE` | `(Catalano, voltou, para a área depois de viver em Londres e em Glasgow , onde estudou design de jóias)` | `(Catalano, voltou para, a área depois de viver em Londres)` | `E-`; “para” não integra REL; a planilha também registra uma divergência de delimitação fora do foco E4 | `para` |
| 44 | `DPTOIE` | `(Catalano, voltou, para a área depois de viver em Londres e em Glasgow , onde estudou design de jóias en a Glasgow School of Art)` | `(Catalano, voltou para, a área depois de viver em Londres)` | `E-`; “para” não integra REL; a planilha também registra uma divergência de delimitação fora do foco E4 | `para` |

**FATO — comportamento comum nas quatro comparações E4:** o DptOIE produz REL como `voltou`, enquanto o GOLD correspondente contém `voltou para`. O elemento crítico para E4 é a preposição `para`.

**FATO — inconsistência terminológica entre os materiais:** a planilha `analise` e o notebook de Graph Rewriting nomeiam os componentes como `ARG0`, `REL` e `ARG1`; o catálogo do DptOIE descreve a busca dos argumentos como `arg1` e `arg2`. Assim, o componente iniciado por `para` é chamado `ARG1` na planilha/no notebook, mas corresponde ao segundo argumento, denominado `arg2` no catálogo. Esta diferença de convenção é registrada aqui e não é resolvida por suposição.

## 4. R_gold de E4

**FATO — escopo da representação disponível:** o notebook descreve a construção como uma “primeira candidata de \(R_{gold}^{E4}\) para esta classe de violação”. Portanto, a representação abaixo está sustentada para o caso piloto modelado, mas não é tratada aqui como uma regra operacional universal já validada sobre todos os casos.

### LHS

Parte derivada da regra linguística:

\[
EmREL(v,e) \land Rege(v,p)
\]

Condição operacional adicional usada para representar o estado de erro observado:

\[
EmARG1(p,e)
\]

Logo, o LHS usado no notebook procura uma extração \(e\), um verbo \(v\) já em REL, uma preposição \(p\) regida por esse verbo e essa preposição atualmente associada ao argumento.

### Graph Matching

**FATO — correspondência registrada no notebook:**

- extração: `e1`;
- verbo: `t2` = `voltou`;
- preposição: `t3` = `para`;
- `e1 → t2` possui rótulo `REL`;
- `t2 → t3` possui rótulo `REGE`;
- `e1 → t3` possui rótulo `ARG1`;
- o resultado salvo no notebook registra exatamente um match antes da reescrita.

O próprio notebook declara que `Rege(voltou, para)` é uma premissa linguística fornecida ao experimento e que o algoritmo não descobre automaticamente a regência verbal.

### RHS

**FATO — transformação operacional registrada:**

- remover a aresta `("e1", "t3", "ARG1")`;
- adicionar a aresta `("e1", "t3", "REL")`.

Em notação resumida do notebook:

\[
ARG1(p,e) \rightarrow REL(p,e)
\]

### Estado antes

**FATO — estado E− modelado no notebook:**

- `ARG0`: `Catalano`;
- `REL`: `voltou`;
- `ARG1`: `para a área`;
- tripla: `(Catalano, voltou, para a área)`.

### Estado esperado depois

**FATO — estado reconstruído e GOLD usado no notebook:**

- `ARG0`: `Catalano`;
- `REL`: `voltou para`;
- `ARG1`: `a área`;
- tripla: `(Catalano, voltou para, a área)`.

O resultado salvo no notebook registra que a saída reconstruída coincide com esse GOLD e que a diferença entre os grafos contém somente a remoção e a adição de aresta descritas acima. O notebook não foi executado nesta etapa; esta afirmação descreve o resultado já armazenado no material.

### Origem dos elementos da representação

**FATO — elementos pertencentes à regra linguística:**

- \(EmREL(v,e)\);
- \(Rege(v,p)\);
- a consequência \(EmREL(p,e)\).

**FATO — elementos introduzidos para operacionalizar o estado de erro do caso:**

- \(EmARG1(p,e)\) como condição de identificação da violação;
- os identificadores concretos `e1`, `t2` e `t3`;
- a remoção da preposição do argumento;
- a transformação de aresta `ARG1 → REL`;
- a exigência de correspondência exata com o GOLD do caso piloto.

A fórmula original de E4 exige a presença da preposição em REL, mas não determina, por si só, a remoção da preposição do argumento. O material identifica essa remoção como uma decisão de modelagem do erro de fronteira observado.

## 5. Regras candidatas do DptOIE

### HIPÓTESES DE PROVENIÊNCIA

**FATO — presença no catálogo:** D02 e D03 estão registradas na aba `catalogo_regras_dptoie`. A aba `analise` associa D02 à REL e D03 ao argumento nas comparações E4 de S009. Essa associação documental não é prova de que as regras tenham sido executadas no caso.

**D02 — Identificação de rel**

> Depois da identificação do sujeito, uma nova DFS procura a relação. A busca começa no nó pai do sujeito ou em nós filhos do sujeito rotulados como acl:part. A Tabela 2 estabelece que, antes do nó pai do sujeito, são considerados aux, aux:pass, cop, obj, iobj, advmod, expl:pv e mark; depois do nó pai, são considerados expl:pv e acl:part.

**D03 — Identificação de arg2**

> A última etapa consiste em encontrar arg2. Uma nova DFS é executada a partir dos nós filhos da relação. A Tabela 2 considera obj, iobj, nmod, nummod, advmod, amod, xcomp, ccomp, advcl, acl:relcl, conj, appos, acl:part e dep. Para ccomp e advcl, a condição indicada é que não possuam nós filhos rotulados como nsubj ou nsubj:pass.

**HIPÓTESE:** D02 pode ser relevante porque descreve a construção de REL, e D03 pode ser relevante porque descreve a construção do segundo argumento. Elas são candidatas para orientar a busca de proveniência no código.

**NÃO DETERMINADO:** não há ainda evidência de que D02, D03 ou uma interação entre ambas tenha causado o resultado de S009. O catálogo não comprova o caminho realmente executado.

## 6. Diretriz metodológica

**FATO — cadeia metodológica relevante consolidada a partir de `O problema (3).pdf`:**

\[
\text{erro observado}
\rightarrow
\text{proveniência da regra}
\rightarrow
R_{impl}
\rightarrow
R_{gold}
\rightarrow
\text{diff estrutural}
\]

Aplicação nesta etapa:

1. partir da divergência observada entre a saída e o GOLD;
2. instrumentar a proveniência para descobrir qual regra ou mecanismo implementado produziu o resultado;
3. formalizar \(R_{impl}^{E4}\) a partir da evidência real de código e execução;
4. manter \(R_{gold}^{E4}\) no mesmo formalismo comparável;
5. calcular posteriormente o diff estrutural entre as duas representações.

**FATO — exigência metodológica:** a proveniência deve ser confirmada por evidência de código e execução, e não apenas pelo catálogo. O catálogo orienta a investigação, mas não substitui trace, condições avaliadas ou caminho executado.

**FATO — limite da etapa atual:** o material metodológico prevê revisão em fases posteriores, mas esta etapa termina antes de qualquer correção, busca de revisão ou Theory Revision.

## 7. O que sabemos

- **FATO:** E4 determina: “Se o verbo rege uma preposição, ela deve ser incluída em REL.”
- **FATO:** a formalização fornecida é \(\forall e\,\forall v\,\forall p\,[(EmREL(v,e) \land Rege(v,p)) \rightarrow EmREL(p,e)]\).
- **FATO:** S009 contém a sentença registrada na Seção 3.
- **FATO:** nas quatro comparações DptOIE marcadas com E4, `para` não integra a REL produzida; no GOLD correspondente, integra `voltou para`.
- **FATO:** o notebook modela o caso piloto `(Catalano, voltou, para a área)` e o estado esperado `(Catalano, voltou para, a área)`.
- **FATO:** o notebook introduz `EmARG1(p,e)` e a migração `ARG1 → REL` para representar operacionalmente a classe de violação; esses elementos não fazem parte da fórmula linguística original de E4.
- **FATO:** D02 e D03 existem na aba do catálogo referente ao DptOIE e são associadas documentalmente a REL e ao argumento na análise de S009.
- **FATO:** os materiais usam convenções diferentes para nomear o segundo argumento da tripla (`ARG1` versus `arg2`).
- **FATO:** ainda não foi coletada evidência de execução do DptOIE para S009 nesta etapa.

## 8. Hipóteses atuais

- **HIPÓTESE:** D02 participa da proveniência do erro por ser a regra catalogada de identificação de REL.
- **HIPÓTESE:** D03 participa da proveniência do erro por ser a regra catalogada de identificação de `arg2`, componente no qual a preposição aparece na saída observada.
- **HIPÓTESE:** a divergência E4 pode resultar da interação entre a delimitação de REL e a construção do segundo argumento, e não necessariamente de uma única regra isolada.
- **HIPÓTESE:** a candidata de \(R_{gold}^{E4}\) do notebook é uma representação estrutural adequada para a classe de violação em que a preposição regida está no argumento e deve integrar REL.

Nenhuma dessas hipóteses estabelece a causa de S009. Em particular, não se infere \(R_{impl}^{E4}\) a partir de D02/D03.

## 9. O que ainda precisa ser determinado

- **NÃO DETERMINADO:** o parse de dependências realmente recebido pelo DptOIE para S009.
- **NÃO DETERMINADO:** o caminho de execução percorrido no processamento de S009.
- **NÃO DETERMINADO:** as funções efetivamente executadas.
- **NÃO DETERMINADO:** as condições avaliadas e seus resultados.
- **NÃO DETERMINADO:** o tratamento dado ao token crítico `para`.
- **NÃO DETERMINADO:** a regra, combinação de regras ou mecanismo realmente responsável pelo resultado.
- **NÃO DETERMINADO:** a correspondência concreta entre a nomenclatura `ARG1` da planilha/notebook e `arg2` do código durante a execução.
- **NÃO DETERMINADO:** a representação de \(R_{impl}^{E4}\).
- **NÃO DETERMINADO:** o diff estrutural entre \(R_{impl}^{E4}\) e \(R_{gold}^{E4}\).

## 10. Evidências que deverão ser coletadas

Posteriormente, deverão ser produzidos artefatos em `logs/s009/` com:

- **NÃO DETERMINADO — evidência a coletar:** parse de dependências efetivamente usado na execução;
- **NÃO DETERMINADO — evidência a coletar:** trace da construção de REL;
- **NÃO DETERMINADO — evidência a coletar:** trace da construção de ARG2, entendido aqui como o segundo argumento da tripla, preservando no log a nomenclatura real encontrada no código;
- **NÃO DETERMINADO — evidência a coletar:** caminho de chamadas, funções executadas e condições avaliadas;
- **NÃO DETERMINADO — evidência a coletar:** movimentação, inclusão ou exclusão do token `para` em cada componente;
- **NÃO DETERMINADO — evidência a coletar:** saída final produzida pelo DptOIE para S009.

Essas evidências deverão sustentar a proveniência e a construção de \(R_{impl}^{E4}\). Até que sejam coletadas, D02 e D03 permanecem exclusivamente como **HIPÓTESES DE PROVENIÊNCIA**. Nenhuma correção de código ou Theory Revision é proposta nesta etapa.
