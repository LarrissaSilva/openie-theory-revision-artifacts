# Comparação em Graph Rewriting para E4/S009

## Qualificadores epistemológicos

- **FATO OBSERVADO:** informação sustentada por artefato de execução, trace, código ou resultado armazenado no notebook.
- **DECISÃO DE MODELAGEM:** escolha explícita adotada para representar os fatos no framework de Graph Rewriting.
- **HIPÓTESE:** interpretação ainda não validada como regra geral do DptOIE.

## 1. Objetivo e justificativa do experimento

**FATO OBSERVADO:** o experimento investiga a divergência de fronteira entre `REL` e o segundo argumento na extração piloto da sentença S009:

> Catalano voltou para a área depois de viver em Londres e em Glasgow, onde estudou design de jóias na Glasgow School of Art.

O DptOIE produziu:

`(Catalano, voltou, para a área)`

O GOLD registra:

`(Catalano, voltou para, a área)`

O elemento que distingue as duas fronteiras é a preposição `para`.

**FATO OBSERVADO:** S009 foi escolhido como caso piloto porque a planilha experimental o associa à regra E4, o erro foi reproduzido de maneira controlada e a cadeia que produziu a extração foi observada por instrumentação. O caso permite comparar dois estados que diferem, no aspecto central de E4, pela associação do mesmo token a `ARG1` ou a `REL`.

**DECISÃO DE MODELAGEM:** a análise é restrita à extração piloto de S009. O nome `R_impl_observado_E4_S009` registra essa restrição e evita apresentar a instância como regra geral do DptOIE.

O objetivo é representar, no mesmo framework:

1. a construção observada do DptOIE, de `G_base` para `G_impl`;
2. a construção esperada segundo E4, de `G_base` para `G_gold`;
3. a transformação corretiva já modelada, de `G_impl` para um estado equivalente a `G_gold`.

Essa organização permite comparar diretamente duas regras de construção que partem do mesmo estado inicial, sem confundir a regra esperada com a transformação corretiva.

## 2. Regra linguística E4

**FATO OBSERVADO — formulação em linguagem natural:**

> “Se o verbo rege uma preposição, ela deve ser incluída em REL.”

Os predicados empregados são:

- \(EmREL(x,e)\): o elemento \(x\) integra a relação da extração \(e\);
- \(Rege(v,p)\): o verbo \(v\) rege a preposição \(p\).

**FATO OBSERVADO — formalização em Lógica de Primeira Ordem:**

\[
\forall e\;\forall v\;\forall p\;[(EmREL(v,e) \land Rege(v,p)) \rightarrow EmREL(p,e)]
\]

**DECISÃO DE MODELAGEM:** `Rege(v,p)` é representado na camada linguística. Ele não é atribuído ao código como uma condição comprovadamente avaliada pelo DptOIE. No notebook, essa relação é conhecimento linguístico fornecido à representação do estado esperado.

## 3. Reprodução controlada do erro

**FATO OBSERVADO:** o erro foi inicialmente reproduzido em uma única execução do `DptOIE.jar` distribuído, usando:

- Eclipse Temurin Java `1.8.0_504`;
- `CC=false`;
- `SC=false`;
- `appositive=0`;
- `pt-pos-tagger.model`, SHA-256 `3025001fb828b7bb73b7f7de6cf6e303126e23aa4f175c8e7f1ad69988a8635b`;
- `pt-dep-parser.gz`, SHA-256 `341e6b5bfc2288b8e7991ee746b2517b02dfb2ef7e540b3666f2b969bd4db30d`.

A execução terminou com exit code `0` e reproduziu exatamente `(Catalano, voltou, para a área)`. O procedimento e os hashes dos artefatos estão registrados em `docs/reproducao_s009_e4.md`.

**FATO OBSERVADO:** o código-fonte original foi compilado contemporaneamente com Java 8 e Maven 3.9.16. O JAR gerado a partir do fonte não modificado também reproduziu a extração piloto. Para S009, as sete linhas funcionais de extração e o parse foram iguais aos obtidos com o JAR distribuído, respeitadas as diferenças periféricas de cabeçalho/encoding documentadas para o CSV.

**FATO OBSERVADO — parse crítico reproduzido:**

| ID | FORM | POS | HEAD | DEPREL |
|---:|---|---|---:|---|
| 1 | Catalano | PNOUN | 2 | nsubj |
| 2 | voltou | VERB | 0 | root |
| 3 | para | ADP | 5 | case |
| 4 | a | DET | 5 | det |
| 5 | área | NOUN | 2 | nmod |

**LIMITAÇÃO FACTUAL:** o modelo de dependências foi obtido da origem atualmente indicada pelo projeto. Não está comprovado que seja o mesmo arquivo usado na execução histórica que originou a anotação de S009. Por isso, a reprodução não é caracterizada como reprodução histórica exata.

## 4. Identificação da proveniência no código

O procedimento de proveniência foi realizado em quatro etapas.

1. **FATO OBSERVADO — análise estática:** foram localizados o fluxo de entrada, a representação de tokens e dependências e os métodos responsáveis por sujeito, REL, segundo argumento e serialização da tripla. Os pontos principais foram `Extracao1.buscaSujeito`, `Extracao1.buscaRelacao`, `Extracao1.extraiClausulas`, `Extracao1.retornaTokenConcatenadoSujeitoArgumentos`, `SujeitoRelacaoArgumentos.addArg2` e `Main.main`.
2. **DECISÃO EXPERIMENTAL:** foi acrescentado trace exclusivamente observacional, desabilitado por padrão e habilitado por `-Ddptoie.e4trace=true`. Os eventos foram escritos em `stderr`, receberam prefixo `[E4TRACE]` e contador monotônico `seq`, sem modificar condições, DFS, coleções ou dependências aceitas.
3. **FATO OBSERVADO — validação de não interferência:** com o trace desabilitado, a execução instrumentada produziu os mesmos outputs funcionais do baseline para S009 e zero eventos `[E4TRACE]`.
4. **FATO OBSERVADO — execução instrumentada:** uma única execução com o trace habilitado terminou com exit code `0` e produziu 133 eventos, de `seq=1` a `seq=133`. Os outputs funcionais foram byte a byte idênticos aos da execução trace-off.

O commit da instrumentação foi `db6af3e90c9a99ad2a61f6f0327e89503aeb63cc`. O JAR instrumentado possuía SHA-256 `3c4b9a72dafe03c41045367be437c638eabeb9e71a1bf2edab7ce329c826290d`.

## 5. Evidências para `R_impl_observado_E4_S009`

As evidências abaixo são fatos da execução instrumentada:

| Seq | Evento observado | Evidência relevante |
|---:|---|---|
| 1 | seleção do sujeito | `Catalano`, token 1, foi selecionado com `head=2` e `deprel=nsubj` |
| 2 | inicialização do núcleo de REL | `voltou`, token 2, foi definido como núcleo inicial |
| 13 | reavaliação do núcleo | o núcleo permaneceu no token 2 |
| 14 | REL final | `REL=[2]`, isto é, `REL=[voltou]` |
| 3–12 | travessia de REL | os candidatos examinados foram os tokens 1, 5, 8 e 26; o token 3, `para`, não foi visitado |
| 16 | exame da raiz do argumento | `área`, token 5, foi examinada como filha de `voltou`, com `deprel=nmod` |
| 17 | início da concatenação | a concatenação do argumento começou em `área` |
| 18–19 | exame de `para` e intervalo | `para`, filho de `área`, foi examinado e acionou o intervalo ordinal `[3,5]` |
| 20–22 | aplicação do intervalo | a mesma operação adicionou `para`, `a` e `área` |
| 24–26 | criação do argumento | o argumento final continha os tokens `[3,4,5]` e foi adicionado como ARG2 |
| 127 | extração final | o mesmo objeto de argumento foi usado em `(Catalano, voltou, para a área)` |

**FATO OBSERVADO:** `para` não foi rejeitado durante a construção de REL; ele não foi visitado nessa travessia.

**FATO OBSERVADO:** a operação que o incluiu no argumento foi observada como um intervalo com limites 3–5. A mesma operação adicionou os três tokens `[para,a,área]`.

**DECISÃO DE MODELAGEM:** os limites concretos `[3,5]` são preservados como proveniência da instância. Na regra, a operação é parametrizada como \(I(p,n)=\{q\mid ordem(p)\leq ordem(q)\leq ordem(n)\}\), evitando transformar IDs de S009 em condição geral.

**DECISÃO DE MODELAGEM:** `case`, `det` e `nmod` são preservados como propriedades do parse. `case` não é apresentado como a condição operacional responsável pela inclusão de `para`, pois o trace não demonstra essa causalidade.

## 6. Construção de `G_base`, `G_impl` e `G_gold`

O notebook separa cinco camadas:

- `DEPENDENCIA`: relações observadas no parse;
- `LINGUISTICA`: conhecimento de regência;
- `OPENIE`: associações `ARG0`, `REL` e `ARG1`;
- `CONSTRUCAO`: candidato a núcleo e operações de construção;
- `PROVENIENCIA`: eventos da execução, mantidos fora do matching.

### `G_base`

**DECISÃO DE MODELAGEM:** `G_base` é o estado inicial comum das duas regras de construção. Ele contém:

- a extração `e1`;
- os tokens `t1=Catalano`, `t2=voltou`, `t3=para`, `t4=a` e `t5=área`;
- as dependências `nsubj(t1,t2)`, `nmod(t5,t2)`, `case(t3,t5)` e `det(t4,t5)`;
- a relação linguística `Rege(t2,t3)`;
- `ARG0(e1,t1)`;
- `t2` como candidato a núcleo de REL;
- nenhuma associação `REL` ou `ARG1` ainda produzida.

O estado OpenIE é:

`ARG0=[Catalano]; REL=[]; ARG1=[]`.

**DECISÃO DE MODELAGEM:** `nsubj` permanece no contexto observado, mas não é guarda específica da divergência E4.

### `G_impl`

**FATO DO RESULTADO MODELADO:** a aplicação de `R_impl_observado_E4_S009` sobre uma cópia de `G_base` produz:

`ARG0=[Catalano]; REL=[voltou]; ARG1=[para,a,área]`.

### `G_gold`

**FATO DO RESULTADO MODELADO:** a aplicação independente de `R_gold_esperado_E4_S009` sobre outra cópia do mesmo `G_base` produz:

`ARG0=[Catalano]; REL=[voltou,para]; ARG1=[a,área]`.

## 7. Representação das regras em Graph Rewriting

### `R_impl_observado_E4_S009: G_base → G_impl`

**DECISÃO DE MODELAGEM — contexto/LHS:**

- `Extracao(e)`;
- `CandidatoNucleoREL(e,v)`;
- `dep(n,v,nmod)`;
- `dep(p,n,case)`;
- `dep(d,n,det)`.

**DECISÃO DE MODELAGEM — guardas operacionais:**

- `CandidatoNucleoREL(e,v)`;
- `nmod(n,v)`;
- `filho(p,n)`;
- `ordem(p)<ordem(n)`;
- disponibilidade de `I(p,n)`.

**DECISÃO DE MODELAGEM — RHS/efeitos OpenIE:**

- `REL(e,v)`;
- `ARG1(e,p)`;
- `ARG1(e,d)`;
- `ARG1(e,n)`.

Essa representação conserva como proveniência, sem convertê-los em guardas, os fatos de que `p` não foi visitado na construção de REL, `n` iniciou o argumento e o intervalo adicionou `p`, `d` e `n`.

### `R_gold_esperado_E4_S009: G_base → G_gold`

**DECISÃO DE MODELAGEM — contexto/LHS:** é utilizado o mesmo contexto estrutural de `R_impl_observado_E4_S009`, permitindo a comparação a partir de `G_base`.

**DECISÃO DE MODELAGEM — guardas:**

- `CandidatoNucleoREL(e,v)`;
- `Rege(v,p)`.

**DECISÃO DE MODELAGEM — RHS/efeitos OpenIE:**

- `REL(e,v)`;
- `REL(e,p)`;
- `ARG1(e,d)`;
- `ARG1(e,n)`.

Na aplicação, após `v` integrar REL, o notebook verifica `EmREL(v,e) ∧ Rege(v,p)` antes de adicionar `p` a REL. Os efeitos sobre `d` e `n` descrevem o estado esperado específico de S009.

### `R_gold_correcao_E4: G_impl → G_gold_corrigido`

**DECISÃO DE MODELAGEM:** a regra corretiva preservada do notebook anterior é mantida como um terceiro objeto. Ela encontra `REL(e,v)`, `Rege(v,p)` e `ARG1(e,p)`, remove `ARG1(e,p)` e adiciona `REL(e,p)`.

Essa regra não substitui `R_gold_esperado_E4_S009`: a primeira corrige um estado já produzido; a segunda representa a construção esperada a partir de `G_base`.

## 8. Comparação estrutural das condições e dos efeitos

O diff é calculado a partir dos campos estruturados das regras, e não por uma lista de diferenças codificada manualmente.

| Dimensão | Comum | Somente implementação observada | Somente GOLD esperado |
|---|---|---|---|
| Contexto | `Extracao(e)`, candidato a núcleo, `nmod`, `case`, `det` | — | — |
| Guardas | `CandidatoNucleoREL(e,v)` | `nmod(n,v)`, `filho(p,n)`, `ordem(p)<ordem(n)`, `I(p,n) disponível` | `Rege(v,p)` |
| Efeitos | `REL(e,v)`, `ARG1(e,d)`, `ARG1(e,n)` | `ARG1(e,p)` | `REL(e,p)` |

**FATO DO RESULTADO DO NOTEBOOK:** o conflito de componente detectado é:

```text
elemento: p
implementação observada: ARG1
GOLD esperado: REL
```

**DECISÃO DE MODELAGEM:** as propriedades de dependência comuns contextualizam a instância, mas não são confundidas com o conhecimento linguístico `Rege(v,p)` nem com todas as guardas efetivamente usadas pela construção observada.

## 9. Resultado central

O diff dos estados OpenIE produzidos mantém em comum:

- `ARG0(e1,t1)`;
- `REL(e1,t2)`;
- `ARG1(e1,t4)`;
- `ARG1(e1,t5)`.

A única diferença estrutural registrada para o token crítico é:

\[
G_{impl}: ARG1(e,p)
\qquad\text{versus}\qquad
G_{gold}: REL(e,p)
\]

Na instanciação de S009, `p=t3=para`. Assim:

- `G_impl` representa `(Catalano, voltou, para a área)`;
- `G_gold` representa `(Catalano, voltou para, a área)`.

**FATO DO MODELO:** não faltam nem sobram os tokens `v`, `d` e `n` entre os efeitos comparados. A divergência central modelada é o componente OpenIE atribuído a `p`.

## 10. Validação da transformação corretiva

**FATO DO RESULTADO DO NOTEBOOK:** `R_gold_correcao_E4` encontrou um match em `G_impl`, removeu a associação de `p` a `ARG1` e adicionou sua associação a `REL`.

O estado resultante foi:

`ARG0=[Catalano]; REL=[voltou,para]; ARG1=[a,área]`.

A assinatura OpenIE desse estado foi comparada com a assinatura de `G_gold`, e o notebook registrou:

`CORRECTION VALIDATION: True`.

As asserções armazenadas também confirmam:

- os três estados exatos;
- `p` em `ARG1` somente em `G_impl`;
- `p` em `REL` somente em `G_gold`;
- o intervalo instanciado como `(t3,t4,t5)`;
- o diff de regras e de estados;
- a ausência de IDs concretos e do intervalo `[3,5]` nas definições abstratas das duas regras de construção.

**DECISÃO DE MODELAGEM:** essa validação demonstra consistência interna da transformação para a instância S009 no modelo. Ela não constitui uma Theory Revision validada e não demonstra que uma alteração equivalente no extrator preserve outros exemplos.

## 11. Limitações

- **FATO OBSERVADO:** a proveniência operacional foi confirmada para a extração piloto de S009 sob uma configuração específica de Java, modelos e parâmetros.
- **FATO OBSERVADO:** a instrumentação foi validada quanto à não interferência apenas para S009 e nas condições testadas.
- **FATO OBSERVADO:** `para` não foi visitado na travessia observada de REL. O experimento não sustenta a formulação “`para` foi rejeitado de REL”.
- **FATO OBSERVADO:** o trace mostra que `para` acionou o intervalo e foi incluído no argumento, mas não demonstra que todo token `case` tenha esse comportamento nem que `case` seja a condição operacional responsável.
- **DECISÃO DE MODELAGEM:** `Rege(voltou,para)` é uma premissa linguística de E4 fornecida ao grafo; não é uma relação descoberta automaticamente pelo notebook nem uma guarda comprovadamente usada pelo DptOIE.
- **DECISÃO DE MODELAGEM:** `R_impl_observado_E4_S009` descreve a instância observada e não deve ser generalizada sem novos casos e novas evidências.
- **HIPÓTESE NÃO VALIDADA:** o mesmo esquema operacional pode explicar outros outputs ou outras sentenças com E4. Isso requer reprodução e proveniência independentes.
- **HIPÓTESE NÃO VALIDADA:** transformar o diff identificado em uma revisão do DptOIE corrigiria E− e preservaria E+. Nenhuma regra revisada foi implementada ou avaliada.
- **LIMITE METODOLÓGICO:** a transformação `R_gold_correcao_E4` valida a passagem de `G_impl` para `G_gold` no modelo de S009; ela não é apresentada como Theory Revision, como regra revisada definitiva ou como correção funcionalmente validada do sistema.

Portanto, o resultado consolidado deste experimento é um diagnóstico formal e reproduzível da divergência E4 na instância S009, acompanhado de proveniência e comparação estrutural. A etapa de Theory Revision permanece posterior e depende de um conjunto experimental com E−, E+ e controles adequados.
