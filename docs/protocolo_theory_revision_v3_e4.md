# Protocolo da primeira Theory Revision exploratória de E4

## Qualificadores epistemológicos

- **FATO OBSERVADO:** informação diretamente sustentada pela planilha, por artefatos de execução do DptOIE, pelo trace ou pelos notebooks consolidados.
- **HIPÓTESE LINGUÍSTICA:** análise gramatical provisória usada para esta experiência, sem validação externa por linguistas.
- **DECISÃO DE MODELAGEM:** escolha explícita feita para representar e testar as regras no framework de Graph Rewriting.
- **COMPORTAMENTO SIMULADO:** resultado produzido exclusivamente pela aplicação de uma regra no modelo de grafo; não equivale a uma execução do DptOIE.
- **NÃO DETERMINADO:** informação que as evidências atuais não permitem decidir.
- **A DEMONSTRAR:** resultado previsto no desenho experimental, mas que somente poderá ser registrado depois da execução do notebook v3.

Este documento foi escrito antes da implementação e da execução do experimento. Ele não contém resultados de C0, C1 ou C2.

## 1. Objetivo científico

Investigar se operadores de revisão aplicados à **regra de construção** representada por `R_impl_observado_E4_S009` podem corrigir a divergência de fronteira E4 observada em S009, produzindo a preposição em REL, e ao mesmo tempo preservar os comportamentos registrados nos controles S003, S005 e S010.

O experimento é exploratório. Ele testa regras no modelo de Graph Rewriting e não modifica nem executa novamente o DptOIE. A transformação `R_gold_correcao_E4: G_impl → G_gold` permanece como demonstração corretiva anterior e não será usada como substituto da revisão da regra de construção.

## 2. Questão experimental e hipóteses

### Questão experimental

Qual combinação mínima, entre alterações de guardas, efeitos, intervalo e estrutura da regra, corrige a fronteira `ARG1(e,p)` versus `REL(e,p)` em S009 sem transferir para REL preposições pertencentes aos argumentos dos controles?

### Hipóteses testadas

**H0 — C0, transferência sem guarda de regência.** O contexto operacional estrutural já seria suficiente para identificar a preposição que deve integrar REL.

- Refutação: C0 não produz o estado esperado de S009 ou transfere qualquer preposição de um controle para REL.
- Um eventual sucesso apenas nos dados atuais não provará generalização; poderá refletir ausência de um controle com o mesmo padrão estrutural.

**H1 — C1, transferência condicionada por dependências.** As condições `case(p,n)` e `nmod(n,v)`, combinadas ao contexto de construção, separariam a preposição regida das preposições que devem permanecer no argumento.

- Refutação: C1 falha em S009 ou altera um controle, especialmente uma construção estruturalmente semelhante, como o locativo de S010.
- `case+nmod` não será interpretado como prova linguística de regência, mesmo que o candidato passe nos casos disponíveis.

**H2 — C2, revisão conservadora por estado explícito de regência.** Um ramo limitado a `TRUE_PROVISIONAL`, acompanhado de um ramo conservador para `FALSE_PROVISIONAL` e `INDETERMINATE`, produziria o GOLD de S009 e preservaria os controles.

- Refutação interna: C2 não corrige S009, altera um caso `FALSE_PROVISIONAL`/`INDETERMINATE`, modifica tokens não envolvidos ou falha nas asserções de estado.
- Limite: um resultado positivo demonstra o comportamento da regra **sob uma anotação fornecida**; não demonstra que o DptOIE consiga reconhecer regência verbal.

## 3. Contexto, proveniência e fontes

### Linha metodológica consolidada

| Commit | Evidência consolidada |
|---|---|
| `2035a75` | contexto científico e análise estática de E4 |
| `5ba5a57` | reprodução de S009 com o JAR distribuído |
| `8297759` | build contemporâneo do fonte não modificado |
| `539cc70` | reprodução baseline de S009 com o JAR compilado |
| `db6af3e` | instrumentação observacional de proveniência |
| `3da8e3a` | validação de não interferência com trace desligado |
| `2e7ee06` | trace de proveniência E4/S009 |
| `67a62a7` | comparação `R_impl × R_gold` em Graph Rewriting |
| `6bde4e2` | baseline dos controles candidatos S003, S005 e S010 |

HEAD no início deste protocolo: `6bde4e276c0a46d1903eb733725bff81f4f5f525`.

### Arquivos de referência e integridade

| Arquivo | SHA-256 |
|---|---|
| `docs/comparacao_graph_rewriting_e4_s009.md` | `d1f6b5c4d190747f6698cbefb9e23ae674b55afc1ffb28bdc2dff92a78a6e5ed` |
| `docs/baseline_controles_e4.md` | `83477c45b9909503928e2c311063f34443ac76ea59cbb0f24f4f13690f506503` |
| `research/graph_rewriting/experimento_v2_e4_impl_gold.ipynb` | `e780723e33f0849798bd54a9650f0606040d95f848862e19f6d78562299ecfb0` |
| `research/experimento/semana5_experimento_OIEC_PT_GOLD (3)(1).xlsx` | `a00c037da53f5de90307d8918b8547d226888297eb7243d0272c68d5f337616c` |

O notebook v2 foi validado com `nbformat`: contém 30 células, 15 células de código executadas e 15 blocos de output. Ele será preservado integralmente.

### Proveniência observada em S009

**FATO OBSERVADO:** o trace demonstrou, para A41, `REL=[voltou]`; `para` não foi visitado na construção de REL; `área` iniciou o argumento; o intervalo ordinal `[3,5]` adicionou `[para,a,área]`; e o mesmo objeto de argumento foi usado na extração final.

**LIMITAÇÃO:** os controles foram reproduzidos e seus parses e outputs foram preservados, mas não houve trace de proveniência do mecanismo interno para eles. O experimento não assumirá que reproduzem o mesmo caminho operacional de S009.

## 4. Dados experimentais

### E− de E4

Todas as quatro ocorrências pertencem à mesma sentença S009 e, portanto, não são evidências linguisticamente independentes.

| Caso | Output DptOIE | GOLD | Papel |
|---|---|---|---|
| S009-A41 | `(Catalano, voltou, para a área)` | `(Catalano, voltou para, a área)` | E− primário e único com proveniência detalhada |
| S009-A42 | `(Catalano, voltou, para a área depois de viver em Londres)` | `(Catalano, voltou para, a área depois de viver em Londres)` | variante E− da mesma sentença |
| S009-A43 | `(Catalano, voltou, para a área depois de viver em Londres e em Glasgow , onde estudou design de jóias)` | `(Catalano, voltou para, a área depois de viver em Londres)` | caso misto E4+E3+S3 |
| S009-A44 | `(Catalano, voltou, para a área depois de viver em Londres e em Glasgow , onde estudou design de jóias en a Glasgow School of Art)` | `(Catalano, voltou para, a área depois de viver em Londres)` | caso misto E4+E3+S3 |

Nos casos mistos, o teste de E4 só poderá alterar a associação de `para`. Não será exigido nem permitido apresentar E3/S3 como corrigidos.

### Controles candidatos

| Caso | Output/GOLD | Pares avaliados | Papel |
|---|---|---|---|
| S005-A28 | correspondência textual exata | `tem–para`, `tem–contra` | finalidade/conteúdo e escopo de predicado encaixado |
| S010-A51 | mesmas fronteiras; `en a`/`em a` | `visitei–em` | locativo |
| S010-A52 | mesmas fronteiras; `en a`/`em a` | `visitei–em`, `visitei–para` | locativo e oração de finalidade |
| S003-A20 | correspondência textual exata | `é–de` | complemento do adjetivo `digno` |

As 15 extrações preservadas no baseline constituem material de não regressão, mas somente serão declaradas testadas se o notebook construir representação suficiente para cada uma delas.

## 5. Protocolo linguístico trivalorado

A unidade de classificação é `(caso, extração, v, p, possível_governador)`. Cada classificação deverá guardar: texto da sentença, componentes baseline/GOLD, dependências observadas, justificativa gramatical e origem manual da decisão.

### Estados

- `TRUE_PROVISIONAL`: `v` é o núcleo de REL; `p` introduz complemento associado ao mesmo sentido verbal; não foi identificado governador concorrente; e o GOLD inclui `p` em REL.
- `FALSE_PROVISIONAL`: `p` pertence justificadamente a adjunto, nome, adjetivo ou predicado encaixado, enquanto o GOLD o mantém no argumento.
- `INDETERMINATE`: evidências insuficientes, conflitantes ou impossíveis de alinhar sem inventar correspondência.

As relações `case`, `mark` e `nmod` serão registradas como **evidência sintática**, nunca como atribuição automática de `Rege(v,p)`.

### Classificações manuais fornecidas ao modelo

| Casos | Par | Estado | Evidência e hipótese |
|---|---|---|---|
| S009-A41–A44 | `voltou–para` | `TRUE_PROVISIONAL` | GOLD inclui `para` em REL; leitura direcional `voltar para`; em A41, parse `para→área(case)` e `área→voltou(nmod)` e proveniência confirmada |
| S005-A28 | `tem–para` | `FALSE_PROVISIONAL` | `para` marca `continuar`; hipótese de finalidade/conteúdo ligado a `dignidade/continuar`, não seleção por `tem` |
| S005-A28 | `tem–contra` | `FALSE_PROVISIONAL` | `contra esse fato` pertence ao predicado encaixado `protestar`, não à REL `tem` |
| S010-A51/A52 | `visitei–em` | `FALSE_PROVISIONAL` | hipótese locativa; GOLD preserva o segmento no argumento apesar do padrão `case+nmod` |
| S010-A52 | `visitei–para` | `FALSE_PROVISIONAL` | `para` marca `encontrar`; hipótese de oração de finalidade, não regência de `visitei` |
| S003-A20 | `é–de` | `FALSE_PROVISIONAL` | `de atenção` complementa o adjetivo `digno`; o parse global possui problemas e será mantido como ressalva |

**Dependência metodológica do GOLD:** o GOLD participa da fundamentação dessas classificações provisórias e também será usado como referência de avaliação. Logo, um acerto não constitui validação independente. O experimento demonstra consistência interna e poder discriminativo dentro dos dados anotados.

## 6. Formalização da revisão

### Regra observada de referência

Seja:

\[
R_I:\ C(e,v,p,n,I) \rightarrow REL(e,v) \cup ARG1(e,I),\quad p\in I
\]

`C` reúne o candidato a núcleo de REL, o argumento iniciado em `n`, a relação de filho entre `p` e `n`, a ordem linear e a disponibilidade do intervalo. Os rótulos de dependência permanecem no contexto do grafo, separados das guardas efetivamente testadas.

### Operadores primitivos

1. `ADD_GUARD_REGE`: acrescenta `StatusRege(v,p)=TRUE_PROVISIONAL`.
2. `SPLIT_RULE`: cria um ramo verdadeiro e um ramo conservador para `FALSE_PROVISIONAL/INDETERMINATE`.
3. `CHANGE_COMPONENT`: altera o efeito de `p` de `ARG1` para `REL` na regra de construção.
4. `RESTRICT_INTERVAL`: produz o argumento com `I\{p}`, preservando ordem e todos os demais tokens.

### C0 — transferência sem guarda de regência

\[
C \rightarrow REL(e,v)\cup REL(e,p)\cup ARG1(e,I\setminus\{p\})
\]

C0 conserva as guardas operacionais abstratas de `R_I`, mas não exige `case`, `nmod` ou estado de regência.

### C1 — transferência condicionada por dependências

\[
C\land case(p,n)\land nmod(n,v)
\rightarrow REL(e,v)\cup REL(e,p)\cup ARG1(e,I\setminus\{p\})
\]

C1 usa os rótulos como condições de matching, sem afirmar que constituem regência linguística.

### C2 — revisão conservadora por regência explícita

\[
C\land StatusRege(v,p)=TRUE\_PROVISIONAL
\rightarrow REL(e,v)\cup REL(e,p)\cup ARG1(e,I\setminus\{p\})
\]

\[
C\land StatusRege(v,p)\in\{FALSE\_PROVISIONAL,INDETERMINATE\}
\rightarrow REL(e,v)\cup ARG1(e,I)
\]

C2 recebe a classificação manual como dado. Ele não contém mecanismo capaz de descobrir regência.

## 7. Espaço de hipóteses

São permitidas somente:

- inclusão das guardas previstas em C1 ou C2;
- divisão da regra nos dois ramos definidos para C2;
- mudança do componente de `p` entre ARG1 e REL;
- exclusão exclusiva de `p` do conjunto ordenado do argumento;
- preservação integral de ARG0, do núcleo verbal, dos demais tokens, dependências e ordem.

Ficam fora do espaço desta experiência:

- alterações em sujeito, seleção do núcleo verbal ou parser;
- novas dependências linguísticas inferidas automaticamente;
- reparos de E3, E9 ou S3;
- mudança, remoção ou reordenação de tokens diferentes de `p`;
- regras aprendidas por solver;
- implementação no Java;
- uso de `R_gold_correcao_E4` como candidato de revisão.

## 8. Critérios de seleção e minimalidade

C0 representa a edição mais permissiva derivada diretamente do conflito de componente. C1 testa a hipótese sintática frequentemente tentadora, mas metodologicamente insuficiente, de usar `case+nmod`. C2 testa a separação explícita entre conhecimento linguístico e estrutura observada.

A complexidade será registrada pelo vetor:

`(guardas adicionadas/removidas, efeitos adicionados/removidos, edições de intervalo, divisões de regra)`.

Cada literal acrescentado ou removido conta uma edição; substituir `ARG1(e,p)` por `REL(e,p)` conta duas edições; trocar `I` por `I\{p}` conta uma; criar os dois ramos de C2 conta uma divisão. O vetor e a soma serão apresentados, sem usar complexidade menor para compensar falha de correção ou regressão.

Alternativas como exceções lexicais por verbo, listas fechadas de preposições, regras por sentença e correção posterior de `G_impl` foram excluídas por sobreajuste ou por não revisarem a construção.

## 9. Procedimento experimental

1. Criar um notebook v3 derivado da infraestrutura do v2, sem modificar o v2.
2. Ler a planilha e os arquivos CoNLL preservados; validar hashes antes de construir os casos.
3. Construir cada grafo com tokens e dependências reais, uma extração identificada e os componentes baseline/GOLD registrados.
4. Mapear spans para IDs somente quando houver alinhamento inequívoco; caso contrário, marcar o caso `INCONCLUSIVE`.
5. Registrar o estado manual de regência e sua justificativa separadamente do grafo de dependência.
6. Aplicar C0, C1 e C2 a cópias independentes do mesmo grafo de entrada. Nenhum candidato receberá o resultado de outro.
7. Produzir, por candidato/caso: checks do matching, ramo aplicado, estado resultante, diff para baseline, diff para GOLD, vetor de edição, asserções e classificação.
8. Nos casos A43/A44, avaliar E4 isoladamente; sobras de E3/S3 permanecerão registradas.
9. Avaliar os controles por identidade de tokens e fronteiras. Em S010, `en a`/`em a` será uma divergência superficial separada, não uma mudança de componente.
10. Executar todas as células em ordem, uma única vez, com kernel Python, preservando outputs e falhando diante de asserção não prevista.

## 10. Critérios de avaliação

### Correção de E−

Para S009, `para` deve integrar REL e deixar ARG1; todos os demais tokens e componentes devem conservar a fronteira que possuíam no estado de referência do caso. Em A41, o estado esperado de E4 é `REL=[voltou,para]` e `ARG1=[a,área]`.

### Preservação e não regressão

- Nenhum par `FALSE_PROVISIONAL` poderá transferir `p` para REL.
- `INDETERMINATE` deverá seguir o ramo conservador de C2.
- Quantidade, ordem e identidade dos tokens não envolvidos deverão permanecer iguais.
- As 15 extrações baseline só poderão ser declaradas preservadas se todas forem representadas e comparadas pelo notebook; caso contrário, o relatório listará exatamente o subconjunto testado.

### Classificação por teste

- `PASS_EXPLORATORY`: corrige o aspecto E4 esperado e preserva o caso dentro do modelo.
- `FAIL_CORRECTION`: não produz a fronteira E4 esperada.
- `FAIL_OVERAPPLICATION`: modifica um controle ou token/componente não autorizado.
- `INCONCLUSIVE`: não há alinhamento, representação ou evidência suficiente para decidir.

Um candidato só poderá receber conclusão global exploratória favorável se corrigir A41, não sobreaplicar nos controles modeláveis e não falhar em asserções estruturais. Isso não o torna revisão validada.

## 11. Ameaças à validade

- Não há E+ específico de E4 confirmado no próprio DptOIE.
- As quatro ocorrências E4 pertencem à mesma sentença; existe apenas um contexto E− independente.
- Apenas A41 possui proveniência interna detalhada.
- As classificações de regência são manuais e provisórias.
- O GOLD participa da classificação e da avaliação, impedindo validação independente.
- Os controles podem não compartilhar o mecanismo interno de S009.
- O parse de S003 possui análise global discutível.
- A diferença `en a`/`em a` em S010 não é meramente encoding, embora preserve fronteiras.
- Um sucesso de C2 demonstra uso correto de uma anotação, não reconhecimento automático de regência.
- O Graph Rewriting é uma representação experimental; não foi demonstrada equivalência geral com a execução Java.

## 12. Reprodutibilidade e artefatos esperados

### Ambiente

- Branch inicial: `modelagem-graph-rewriting-e4`.
- Python `3.12.0` 64-bit.
- NetworkX `3.5`.
- Matplotlib `3.10.3`.
- openpyxl `3.1.5`.
- nbformat `5.10.4`.
- nbclient `0.11.0`.
- ipykernel `6.29.5`.
- IPython `9.4.0`.

### Parses preservados

| Caso | SHA-256 de `output_DP.conll` |
|---|---|
| S009 | `e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f` |
| S003 | `f12731b7b6dc71ffda49d837f947f8eb76119751a4062585c8e564e3d0cb624c` |
| S005 | `49335c1eb391b21f55b6c44a956bfbfcc15ae968e75eb511f364e8a16a20ec2d` |
| S010 | `c3aaab2679596c96ca24e51896134ef572d7f963946c0af5c16ae50c4f4e5cfe` |

### Ordem e produtos

1. Versionar este protocolo em commit próprio.
2. Criar e executar `research/graph_rewriting/experimento_v3_e4_theory_revision.ipynb`.
3. Validar o notebook com `nbformat`, confirmar execução ordenada e ausência de erro.
4. Criar `docs/resultados_theory_revision_e4.md` somente a partir dos outputs reais.
5. Registrar notebook e resultados em segundo commit, sem alterar os arquivos de referência.

Artefatos esperados do notebook: inventário dos dados, classificações de regência, regras C0/C1/C2, matriz de matching, estados antes/depois, diffs, asserções, métricas de edição e resumo de resultados. **Todos permanecem A DEMONSTRAR até a execução.**
