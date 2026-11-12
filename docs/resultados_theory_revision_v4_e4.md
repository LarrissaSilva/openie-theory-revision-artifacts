# Resultados da Theory Revision v4 — E4

## 1. Objetivo e estatuto dos resultados

O experimento v4 avaliou se C0, C1 e C2 poderiam ser produzidas por operadores explícitos de edição aplicados a uma regra formal imutável, superando a implementação procedural auditada no v3.

Os resultados aqui registrados são **resultados formais do modelo de Graph Rewriting**. Eles não correspondem a uma nova execução do DptOIE, a uma alteração do Java, a uma revisão implantada no extrator ou a uma demonstração de generalização linguística.

Referências metodológicas:

- protocolo v4: commit `4183b5ecddee1f8e42d82f5d21de2381513384b6`;
- decisões anteriores à avaliação: commit `54a65af0e2023eb23683f1e020123ac692401c98`;
- notebook: `research/graph_rewriting/experimento_v4_e4_theory_revision.ipynb`;
- SHA-256 do notebook executado: `bb7506602745d061ae113969c964f6c5fbfc6df85ca06a87a14eaaf125672cca`.

## 2. Ambiente e integridade das entradas

O notebook foi executado com:

- Python `3.12.0`;
- NetworkX `3.5`;
- openpyxl `3.1.5`;
- nbclient `0.11.0` para execução do notebook.

Foram verificadas antes da construção:

| Entrada | SHA-256 |
|---|---|
| Planilha OIEC-PT-GOLD | `a00c037da53f5de90307d8918b8547d226888297eb7243d0272c68d5f337616c` |
| Parse S009 | `e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f` |
| Parse S003 | `f12731b7b6dc71ffda49d837f947f8eb76119751a4062585c8e564e3d0cb624c` |
| Parse S005 | `49335c1eb391b21f55b6c44a956bfbfcc15ae968e75eb511f364e8a16a20ec2d` |
| Parse S010 | `c3aaab2679596c96ca24e51896134ef572d7f963946c0af5c16ae50c4f4e5cfe` |

O notebook contém 18 células, sendo nove células de código. As nove foram executadas em ordem, com contadores `1..9`, e não há output de erro.

## 3. Decisões efetivamente implementadas

### 3.1 Condição operacional do intervalo

A implementação representa a condição observada no Java sem atribuir causalidade ao rótulo `case`:

- `n` precisa ter um `deprel` aceito pelo método de concatenação;
- `p` é derivado como o primeiro filho de `n`, na ordem dos tokens, que aparece à esquerda do próprio head;
- a guarda operacional testa `order(p) < order(n)`;
- `I(p,n)` usa limites inclusivos;
- `case(p,n)` só é acrescentado por C1 como hipótese sintática.

Em S009-A41, o matcher derivou `p=3`, `n=5` e `I(p,n)=(3,4,5)`.

### 3.2 Informações derivadas

Foram derivados do grafo:

- filhos e sua ordem;
- `p`;
- relações de dependência usadas pelas guardas;
- `I(p,n)` e `I(p,n)-{p}`;
- valores das guardas;
- branch selecionado;
- componentes produzidos pelas expressões formais.

### 3.3 Entradas experimentais preservadas

Continuaram fornecidos:

- núcleo candidato `v`;
- raízes candidatas `n`;
- ARG0 e REL anteriores à operação estudada;
- contribuição externa `U`;
- status provisório de regência e sua origem.

O GOLD e os estados esperados foram armazenados em objetos `EvaluationOracle`, separados dos objetos de construção. Eles só foram consultados depois da aplicação para classificar os resultados.

### 3.4 Representação de `U`

O argumento baseline foi reconstruído como:

\[
ARG1_{baseline}=U\cup I_1\cup\ldots\cup I_k
\]

Todos os oito baselines foram reconstruídos dessa maneira e comparados com os componentes registrados na planilha. O executor não recebeu o ARG1 completo para retirar `p`.

### 3.5 Grafo

Foi usado `networkx.MultiDiGraph`, com chaves de aresta e camadas explícitas. A escolha permite preservar relações paralelas sem sobrescrita.

## 4. Objetos formais e operadores

Foram implementadas dataclasses imutáveis para:

- variáveis;
- contexto;
- guardas;
- expressões de conjuntos de tokens;
- efeitos;
- restrições;
- evidências;
- registros de edição;
- regras atômicas;
- condições e branches;
- regras compostas.

`R_impl_observado_E4_S009_A41` recebeu o hash:

```text
d4c332a43dd349ee6b7691880933432e455bbe3aa41af35814335e0ceaf4e8c4
```

Foram implementados como funções puras:

- `ADD_GUARD`;
- `ADD_GUARD_REGE`;
- `RESTRICT_INTERVAL`;
- `CHANGE_COMPONENT`;
- `SPLIT_RULE`.

Cada operador retorna um novo objeto e acrescenta `EditRecord`. O hash da regra-pai foi verificado antes e depois da derivação e após toda a avaliação.

## 5. Derivação efetiva das candidatas

### 5.1 C0

Sequência aplicada independentemente a `R_impl`:

```text
RESTRICT_INTERVAL
→ CHANGE_COMPONENT(ARG1, REL, {p})
```

Hash de C0:

```text
91194d427726f98be1b377d925a5790fc01fbb5596440b90d09c5341b809c427
```

### 5.2 C1

Sequência do branch especializado:

```text
ADD_GUARD(dep(p,n,case))
→ ADD_GUARD(dep(n,v,nmod))
→ RESTRICT_INTERVAL
→ CHANGE_COMPONENT(ARG1, REL, {p})
→ SPLIT_RULE(branch sintático, fallback)
```

Hash da regra composta C1:

```text
af966fec75bce1b08524e3e2d40af12258749ed255e0ad03e28753b9a5395458
```

### 5.3 C2

Sequência do branch especializado:

```text
ADD_GUARD_REGE(StatusRege=TRUE_PROVISIONAL)
→ RESTRICT_INTERVAL
→ CHANGE_COMPONENT(ARG1, REL, {p})
→ SPLIT_RULE(TRUE_PROVISIONAL, FALSE_PROVISIONAL, INDETERMINATE)
```

Hash da regra composta C2:

```text
d537c4c7088479d413ddde4cd131bdf012bb137c29bfeecdf1ffed02a01a23fe
```

O branch `INDETERMINATE` é explícito e conservador. C0, C1 e C2 foram derivados diretamente da mesma regra-pai; nenhuma candidata recebeu outra candidata como entrada.

## 6. Diff e custo calculados automaticamente

Foram usados pesos unitários congelados antes da avaliação. Proveniência e metadados não receberam custo semântico.

| Candidata | Guardas +/− | Efeitos +/− | Intervalo | Restrições +/− | Split | Custo |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 0/0 | 2/1 | 1 | 1/0 | 0 | 5 |
| C1 | 2/0 | 2/1 | 1 | 1/0 | 1 | 8 |
| C2 | 1/0 | 2/1 | 1 | 1/0 | 1 | 7 |

Os valores foram obtidos do diff entre as formas canônicas das regras. O histórico dos operadores foi reconciliado com o diff.

Esses custos não são numericamente comparáveis aos valores constantes do v3. O v4 contabiliza automaticamente cada efeito adicionado/removido, a restrição formal de partição e o split. A mudança da métrica não altera os resultados funcionais dos candidatos e não sustenta escolher uma candidata apenas por menor custo.

## 7. Testes executados

Foram aprovadas 31 asserções, cobrindo:

- imutabilidade de `R_impl`;
- existência de C0, C1 e C2 como objetos-regra completos;
- linhagem independente;
- reconciliação entre histórico e diff;
- pesos unitários;
- pré-condições de `CHANGE_COMPONENT`;
- rejeição de guarda duplicada;
- rejeição de branches sobrepostos;
- intervalo com pontuação;
- intervalo com IDs não contíguos;
- fallback `INDETERMINATE`;
- ARG1 composto com `U` não vazio;
- separação do GOLD das assinaturas de construção;
- oito casos reais e 24 aplicações;
- reconstrução dos baselines com `U` e intervalos;
- uso de `I(p,n)` pelo executor;
- correção formal de S009-A41 por C0, C1 e C2;
- resultados globais do conjunto fechado;
- sobreaplicações selecionadas;
- preservação condicional dos controles por C2;
- registro da origem das classificações de regência;
- limite dos onze outputs não modelados.

Os fixtures `INDETERMINATE`, `U` não vazio, pontuação e IDs não contíguos são testes de infraestrutura. Eles não foram contados como casos de corpus nem como evidência linguística.

## 8. Resultados nos casos reais

Foram realizadas 24 aplicações formais: três candidatas sobre oito extrações.

| Caso | C0 | C1 | C2 |
|---|---|---|---|
| S009-A41 | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |
| S009-A42 | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |
| S009-A43 | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |
| S009-A44 | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |
| S005-A28 | `FAIL_OVERAPPLICATION` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |
| S010-A51 | `FAIL_OVERAPPLICATION` | `FAIL_OVERAPPLICATION` | `PASS_EXPLORATORY` |
| S010-A52 | `FAIL_OVERAPPLICATION` | `FAIL_OVERAPPLICATION` | `PASS_EXPLORATORY` |
| S003-A20 | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` | `PASS_EXPLORATORY` |

Classificação global no conjunto fechado:

| Candidata | Resultado |
|---|---|
| C0 | `FAIL_OVERAPPLICATION` |
| C1 | `FAIL_OVERAPPLICATION` |
| C2 | `PASS_EXPLORATORY` |

### 8.1 S009-A41

As três candidatas produziram:

```text
ARG0 = [1]       Catalano
REL  = [2,3]     voltou para
ARG1 = [4,5]     a área
```

O resultado foi construído com `I(3,5)=[3,4,5]`, seguido de partição e transferência de `{3}`. Não foi produzido pela remoção de `3` do span ARG1 completo.

### 8.2 Variantes S009-A42–A44

As três candidatas transferiram o token 3 e preservaram `U`. A43 e A44 continuam contendo material associado a E3/S3; `PASS_EXPLORATORY` significa correção do aspecto E4 esperado, não igualdade integral com o GOLD.

### 8.3 C0

C0 transferiu:

- `para` em S005-A28;
- `en` em S010-A51;
- `en` e `para` em S010-A52.

Essas aplicações alteraram os controles e resultaram em `FAIL_OVERAPPLICATION`.

### 8.4 C1

C1 preservou S005-A28 e S003-A20, mas transferiu `en` em S010-A51 e S010-A52. Assim, `case(p,n) ∧ nmod(n,v)` continua insuficiente para separar o caso direcional de S009 do locativo de S010 no conjunto modelado.

### 8.5 C2

C2 transferiu `para` nas quatro representações S009 e preservou os quatro controles modelados. Esse resultado depende diretamente das entradas manuais:

- S009: `TRUE_PROVISIONAL`;
- controles: `FALSE_PROVISIONAL`.

O experimento não implementou nem descobriu um reconhecedor de `Rege(v,p)`.

## 9. Fixtures críticos

### 9.1 `INDETERMINATE`

Um fixture baseado apenas na estrutura de S009 recebeu status `INDETERMINATE`. C2 selecionou explicitamente `REGE_INDETERMINATE` e preservou:

```text
REL=[2]
ARG1=[3,4,5]
```

Isso demonstra a semântica do fallback no software, não a existência de um caso indeterminado real no corpus.

### 9.2 `U` não vazio

Um fixture com `U=[6]` e `I=[3,4,5]` produziu:

```text
REL=[2,3]
ARG1=[4,5,6]
```

O token externo ao intervalo foi preservado.

### 9.3 Ordem, pontuação e IDs

Um fixture com IDs `10,20,30` e pontuação no token 20 produziu o intervalo ordenado `(10,20,30)`. O teste confirma que a implementação usa `ordem` e inclui pontuação, sem fabricar a sequência numérica `10..30`.

## 10. Comparação metodológica com o v3

### 10.1 Limitações do v3 superadas

No v4:

- C0, C1 e C2 são regras formais completas;
- operadores transformam programaticamente cópias lógicas de `R_impl`;
- cada edição deixa proveniência e linhagem;
- o diff e o custo são calculados das regras;
- o matcher deriva `p` e o intervalo;
- o executor usa `I(p,n)` na construção;
- `U` explicita contribuições externas;
- branches e fallback pertencem ao objeto `ChoiceRule`;
- `INDETERMINATE` foi efetivamente testado;
- o código de aplicação não implementa comportamentos por `if candidate_name`.

### 10.2 Resultados preservados

A matriz do conjunto fechado coincide qualitativamente com o v3:

- C0 sobreaplica;
- C1 preserva S005, mas sobreaplica em S010;
- C2 satisfaz condicionalmente os oito casos modelados.

Isso demonstra que os resultados procedurais anteriores podem ser reproduzidos por operadores reais de edição. Não transforma as classificações provisórias de regência em evidência independente.

## 11. Limitações e ameaças à validade

1. `R_impl` continua restrita ao mecanismo comprovado de S009-A41.
2. As quatro ocorrências E− compartilham uma única sentença e o mesmo par `voltou–para`.
3. Os quatro controles não são E+ específicos de E4.
4. Onze dos 15 outputs baseline dos controles permanecem não modelados.
5. `v`, `n`, `U`, ARG0 e REL anteriores continuam sendo entradas experimentais.
6. A atribuição de tokens a `U` é uma decomposição de modelagem, não proveniência confirmada desses tokens no Java.
7. C2 recebe status de regência manual; nos casos reais atuais, o GOLD participou de sua fundamentação.
8. O fixture `INDETERMINATE` testa infraestrutura, não cobertura empírica.
9. A avaliação não contém E+ E4 confirmado.
10. O v4 não foi implementado nem testado no DptOIE Java.
11. Preservação dos quatro controles não demonstra ausência geral de regressões.
12. Custos unitários medem distância estrutural adotada, não qualidade linguística.

## 12. Conclusões sustentadas

O experimento sustenta que:

1. C0, C1 e C2 podem ser derivadas de `R_impl_observado_E4_S009_A41` por operadores explícitos, imutáveis e rastreáveis.
2. O efeito de E4 pode ser modelado na regra de construção usando o intervalo produzido pelo matcher.
3. O diff e o custo podem ser calculados automaticamente dos objetos-regra.
4. C0 e C1 possuem contraexemplos entre os controles modelados.
5. C2 satisfaz o conjunto fechado quando recebe classificações provisórias adequadas.
6. A limitação procedural central do v3 foi superada no modelo formal.

O experimento não sustenta que:

- C2 reconheça regência;
- C2 seja uma revisão generalizada;
- haja preservação de E+ E4;
- os onze outputs não modelados estejam preservados;
- uma revisão Java esteja pronta ou validada;
- os resultados se generalizem a novos verbos, preposições ou sentenças.

O resultado científico correto é, portanto:

> O v4 demonstra uma Theory Revision formal e rastreável da construção modelada para S009-A41, com avaliação exploratória em conjunto fechado. A passagem para uma revisão generalizada permanece impedida pela ausência de reconhecimento operacional independente de regência, de E+ específicos e de contextos E− independentes.
