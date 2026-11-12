# Protocolo de Theory Revision v4 — E4

## 1. Objetivo e escopo

Este protocolo define a primeira implementação de Theory Revision de E4 baseada em **operadores explícitos de edição sobre objetos-regra formais**. O objetivo é superar a limitação metodológica identificada na auditoria do experimento v3: naquele experimento, C0, C1 e C2 foram implementadas como transformações procedurais condicionadas de fronteiras previamente informadas, e não como regras derivadas por edição verificável de uma regra de origem.

O v4 deverá:

1. representar a regra implementada observada, suas condições, seus efeitos e sua proveniência como um objeto imutável;
2. produzir cada candidata por uma sequência registrada de operadores sobre uma cópia dessa regra;
3. calcular automaticamente o diff e o custo de edição entre regras;
4. fazer o matcher derivar do grafo os tokens e o intervalo necessários à aplicação;
5. separar rigorosamente a **derivação das candidatas** da **avaliação experimental**.

Este documento é um protocolo prospectivo. Ele não contém resultados do v4, não altera retrospectivamente o v3 e não afirma que uma revisão já tenha sido validada no DptOIE Java.

## 2. Relação com os experimentos anteriores

### 2.1 Evidência preservada

Os seguintes resultados são tratados como evidência anterior, não como resultados produzidos pelo v4:

- o DptOIE reproduziu, para S009-A41, `(Catalano, voltou, para a área)`;
- o GOLD de S009-A41 é `(Catalano, voltou para, a área)`;
- o trace instrumentado mostrou `REL=[voltou]` e a criação de `ARG1=[para,a,área]` — denominado `ARG2` no código Java — por uma operação de intervalo `[3,5]`;
- `para` não foi visitado na travessia observada de construção de REL;
- o notebook v2 representou `G_base`, `G_impl`, `G_gold`, as duas regras de construção e a transformação corretiva;
- o v3 avaliou C0, C1 e C2 sobre oito construções modeladas, mas recebeu manualmente as fronteiras dos componentes e não editou objetos-regra;
- a auditoria do v3 registrou quatro E− da mesma sentença, quatro controles modelados, onze outputs baseline ainda não modelados, ausência de E+ específicos de E4 e ausência de testes efetivos com `INDETERMINATE`.

### 2.2 Infraestrutura do v2 que pode ser reaproveitada

Podem ser reaproveitados, após generalização e com testes próprios:

- a representação do grafo com atributos de token e arestas de dependência;
- as dataclasses imutáveis usadas para condições, efeitos, regras e matches;
- as funções de acesso a tokens, dependências e ordem linear;
- a construção de `I(p,n)` por ordem dos tokens;
- o princípio de matching separado da aplicação;
- a comparação estrutural entre conjuntos de guardas e efeitos;
- o registro de proveniência associado às regras.

Precisam ser generalizados:

- efeitos que no v2 são pares simples `componente/elemento`, para aceitarem expressões sobre conjuntos de tokens;
- intervalos, que devem ser objetos formais usados na produção do resultado;
- regras atômicas, para permitirem composição por alternativas explícitas;
- o diff, para considerar guardas, efeitos, intervalos, restrições, ramificações e linhagem;
- a proveniência, para distinguir evidência de código, trace, modelagem e hipótese;
- a aplicação, para não depender de spans completos de ARG0, REL e ARG1 fornecidos manualmente.

A regra corretiva do v2, `R_gold_correcao_E4 : G_impl -> G_gold`, permanece válida apenas no papel já documentado de transformação do estado observado para o esperado. Ela não será usada como substituto de uma revisão da regra de construção.

## 3. Hipóteses e estatuto epistêmico

### 3.1 Hipóteses do v4

- **H1 — representabilidade:** o mecanismo observado em S009-A41 pode ser representado por uma regra formal imutável com contexto, guardas, intervalo, efeitos e proveniência explícitos.
- **H2 — editabilidade:** C0, C1 e C2 podem ser derivadas dessa regra por sequências explícitas de operadores, sem branches procedurais desvinculados de objetos-regra.
- **H3 — execução formal:** o resultado de uma candidata pode ser construído a partir do match e de `I(p,n)`, sem remover `p` de um ARG1 completo previamente conhecido.
- **H4 — auditabilidade:** o diff estrutural e o custo de cada candidata podem ser calculados automaticamente e reconciliados com o histórico de operadores.
- **H5 — preservação limitada:** os controles já modelados podem testar preservação condicional dentro do conjunto fechado atual, sem constituir evidência de generalização.

### 3.2 Categorias obrigatórias

Todo elemento da representação deverá receber uma categoria:

- **EVIDÊNCIA OBSERVADA:** diretamente sustentada pelo parse, saída, código ou trace preservado;
- **DECISÃO DE MODELAGEM:** escolha explícita necessária para formalizar ou executar o experimento;
- **HIPÓTESE:** generalização ainda não demonstrada pelo material empírico;
- **ENTRADA EXPERIMENTAL:** informação fornecida ao experimento, e não derivada pelo matcher;
- **DERIVADO DO GRAFO:** informação calculada pelo matcher a partir do grafo de entrada.

O sistema deverá impedir que uma condição de contexto, como `dep(p,n,case)`, seja automaticamente promovida a guarda operacional ou a prova de `Rege(v,p)`.

## 4. Representação formal

### 4.1 Grafo de entrada

Um grafo de sentença será representado por:

\[
G=(V,E_{dep},E_{oie},A,\prec)
\]

em que:

- `V` é o conjunto de tokens e, quando necessário, nós de extração;
- `E_dep` contém dependências rotuladas;
- `E_oie` contém vínculos OpenIE produzidos ou candidatos;
- `A` contém atributos como `id`, `form`, `lemma` e `pos`;
- `\prec` é a ordem total dos tokens na sentença.

A implementação deverá preservar arestas paralelas semanticamente distintas, por meio de um multigrafo ou de identificadores explícitos de aresta. A escolha concreta deverá ser verificada antes da implementação.

### 4.2 Expressões de conjuntos de tokens

Os efeitos não operarão apenas sobre tokens isolados. O v4 deverá suportar expressões tipadas:

- `Singleton(x) = {x}`;
- `Interval(p,n) = {t in V | ordem(p) <= ordem(t) <= ordem(n)}`;
- `Difference(X,Y)`;
- `Union(X,Y)`;
- `Preserved(U)`, para uma contribuição de ARG1 produzida por mecanismos não formalizados nesta revisão.

Para o caso observado:

\[
I(p,n)=Interval(p,n)
\]

e, na instância S009-A41, `p=para`, `n=área` e `I(p,n)=[para,a,área]`. Os IDs `[3,5]` são evidência da instância, não uma condição geral da regra.

### 4.3 Objeto-regra atômico

Uma regra atômica será uma tupla imutável:

\[
\rho=\langle id,X,C,B,\Gamma,\Phi,\Omega,\Pi,L\rangle
\]

com:

- `id`: identificador estável e hash canônico;
- `X`: variáveis tipadas;
- `C`: contexto estrutural observado, que não implica uso como guarda;
- `B`: binders e expressões derivadas, incluindo `I(p,n)`;
- `Gamma`: guardas efetivamente avaliadas no matching;
- `Phi`: efeitos OpenIE tipados sobre `ARG0`, `REL` e `ARG1`;
- `Omega`: restrições de aplicação e invariantes;
- `Pi`: proveniência por elemento;
- `L`: linhagem, regra-pai e histórico ordenado de edições.

As guardas deverão registrar ao menos: expressão formal, camada (`IMPLEMENTACAO`, `LINGUISTICA` ou `EXPERIMENTAL`), fonte, estatuto epistêmico e evidência. Os efeitos terão a forma `ADD_MEMBERS(componente, expressão_de_tokens)` ou outra operação explicitamente tipada. Nenhuma edição poderá alterar o objeto original.

### 4.4 Regra composta

Uma regra composta será representada por `ChoiceRule`, também imutável:

\[
\chi=\langle id,\{(q_i,\rho_i)\},politica,\Pi,L\rangle
\]

em que os predicados de branch `q_i` devem ser disjuntos e, quando a regra for total para seu domínio, exaustivos. A política deverá declarar prioridade, tratamento de empate e comportamento quando nenhuma alternativa for aplicável.

### 4.5 Ambiente de match

O matcher devolverá um objeto independente da regra:

\[
M=\langle bindings,derivedSets,checks,evidence\rangle
\]

Ele deverá guardar:

- os bindings de `v`, `p`, `n` e demais variáveis;
- `I(p,n)` efetivamente derivado;
- o valor de cada guarda sem reavaliação silenciosa;
- a origem de cada dado;
- as razões de sucesso ou falha do match.

### 4.6 `R_impl_observado_E4_S009_A41`

A regra de origem do v4 será deliberadamente restrita ao mecanismo comprovado para S009-A41. Seu esquema inicial será:

**Contexto observado**

- `Catalano --nsubj--> voltou`, preservado como contexto e proveniência da extração;
- `área --nmod--> voltou`;
- `para --case--> área`;
- `a --det--> área`;
- ordem `para prec a prec área`.

`nsubj` não integrará automaticamente o LHS específico da divergência E4. Sua necessidade deverá ser testada; até lá, permanece contexto de proveniência.

**Guardas de implementação**

- `v` é o núcleo de REL selecionado pelo mecanismo observado;
- `n` é aceito pelo caminho observado como raiz do argumento ligado a `v`;
- `p` satisfaz a condição de código que acionou a operação de intervalo a partir de `n`;
- `I(p,n)` existe e satisfaz os invariantes de ordem.

O predicado que representa a condição de código para acionar o intervalo deverá apontar para a evidência estática e dinâmica correspondente. `dep(p,n,case)` ficará no contexto linguístico enquanto não for demonstrado que o rótulo `case` é a condição operacional responsável.

**Efeitos observados**

\[
ARG0(e,\{s\}),\quad REL(e,\{v\}),\quad ARG1(e,U\cup I(p,n))
\]

`U` representa contribuições de ARG1 externas ao intervalo e produzidas por caminhos ainda não formalizados. Para S009-A41, `U` é vazio. Essa decomposição permite modelar A42–A44 no futuro sem fingir que toda a fronteira do argumento foi produzida pela única operação estudada.

**Proveniência negativa corretamente limitada**

A ausência de visita a `para` na travessia de REL será registrada como evidência do trace da instância. Ela não será convertida em uma guarda geral como “rejeitado de REL” ou “todo token case não é visitado”.

### 4.7 Especificação esperada de E4

A especificação linguística usada como referência permanece:

\[
\forall e\forall v\forall p\;[(EmREL(v,e)\land Rege(v,p))\rightarrow EmREL(p,e)]
\]

No estágio de construção, `R_gold_esperado_E4` parte do mesmo contexto aplicável e, quando `Rege(v,p)` é verdadeiro, produz:

\[
REL(e,\{v\}\cup\{p\}),\quad ARG1(e,U\cup(I(p,n)-\{p\}))
\]

Essa especificação orienta a comparação formal, mas não fornece por si só um procedimento para inferir `Rege`. Ela também não deve ser confundida com `R_gold_correcao_E4`, que recebe `G_impl` pronto e o transforma em `G_gold`. Os operadores do v4 deverão editar a regra de construção que parte de `G_base`.

## 5. Operadores explícitos de revisão

Todos os operadores serão funções puras:

\[
op(\rho,parametros)\rightarrow(\rho',editRecord)
\]

Antes e depois da chamada, o hash canônico de `rho` deverá permanecer igual. `rho'` receberá novo identificador, referência ao pai e um `EditRecord` com pré-condições verificadas, fragmento anterior, fragmento novo e justificativa.

### 5.1 `ADD_GUARD_REGE`

**Assinatura conceitual**

`ADD_GUARD_REGE(regra, v, p, dominio_status) -> nova_regra`

**Pré-condições**

- `v` e `p` são variáveis declaradas e tipadas como tokens;
- não existe guarda contraditória;
- a fonte do valor de regência está declarada e não é inferida apenas de `case` ou `nmod`;
- o domínio de status está explicitado.

**Efeito**

Adiciona uma guarda linguística `Rege(v,p)` ou, na fase experimental, `StatusRege(v,p)=TRUE_PROVISIONAL`, preservando sua origem e incerteza. O operador não move tokens entre componentes.

**Validade**

- a guarda adicionada aparece no diff;
- a regra original é inalterada;
- o matcher distingue `TRUE_PROVISIONAL`, `FALSE_PROVISIONAL` e `INDETERMINATE`;
- GOLD não pode ser consultado para decidir a guarda durante aplicação.

### 5.2 `SPLIT_RULE`

**Assinatura conceitual**

`SPLIT_RULE(regra, particao, especializacoes, politica) -> ChoiceRule`

**Pré-condições**

- todos os branches descendem da mesma regra-pai;
- os predicados são tipados;
- a sobreposição entre branches é detectada;
- a cobertura do domínio é declarada como total ou parcial.

**Efeito**

Cria alternativas formais explícitas. O branch de fallback mantém a semântica da regra-pai; nenhum `else` procedural oculto substitui uma regra ausente.

**Validade**

- branches disjuntos para o mesmo match;
- política determinística;
- cobertura explícita de `INDETERMINATE` quando o split usar regência;
- proveniência e histórico próprios por branch.

### 5.3 `CHANGE_COMPONENT`

**Assinatura conceitual**

`CHANGE_COMPONENT(regra, token_set, origem, destino) -> nova_regra`

**Pré-condições**

- existe um efeito explícito que adiciona `token_set` à origem;
- origem e destino são componentes OpenIE válidos e diferentes;
- a mudança não cria duplicação incompatível;
- as restrições de unicidade e ordem continuam satisfeitas.

**Efeito**

Substitui, no RHS, `ADD_MEMBERS(origem,token_set)` por `ADD_MEMBERS(destino,token_set)`. Para E4, a edição relevante é `ARG1 -> REL` sobre `Singleton(p)`.

**Validade**

O operador só atua sobre o RHS formal. Ele não altera o grafo de entrada, o matcher ou spans experimentais fornecidos externamente.

### 5.4 `RESTRICT_INTERVAL`

**Assinatura conceitual**

`RESTRICT_INTERVAL(regra, efeito, pivot=p, politica=PARTITION) -> nova_regra`

**Pré-condições**

- o RHS contém um efeito sobre `I(p,n)`;
- `p` pertence a `I(p,n)` no match;
- `I(p,n) - {p}` é uma expressão bem tipada;
- a partição preserva todos os tokens do intervalo.

**Efeito**

Normaliza:

\[
ARG1(I(p,n))
\]

em:

\[
ARG1(\{p\})\cup ARG1(I(p,n)-\{p\})
\]

sem mudar ainda o componente de `p`. Essa partição torna o subconjunto a revisar explícito. Aplicado em seguida, `CHANGE_COMPONENT` poderá mover apenas `{p}` para REL. `U` permanece intocado.

**Validade**

- união das partes igual ao intervalo original;
- interseção vazia;
- nenhuma perda, duplicação ou reordenação indevida;
- o intervalo é o produzido pelo matcher, e não um span completo copiado do GOLD.

### 5.5 Primitiva de infraestrutura `ADD_GUARD`

C1 requer guardas sintáticas, não uma guarda de regência. Para não falsificar sua semântica, o v4 poderá usar uma primitiva genérica e auditável:

`ADD_GUARD(regra, guarda_tipificada) -> nova_regra`.

Ela não é um quinto operador científico específico de E4; é a operação estrutural elementar da álgebra de regras da qual `ADD_GUARD_REGE` é uma especialização com validações próprias. Seu uso ficará limitado a tipos de guarda permitidos e aparecerá no histórico e no custo. Se essa primitiva não for aceita na implementação, C1 deverá ser formalizada por `SPLIT_RULE` com os mesmos predicados explícitos, nunca por uso indevido de `ADD_GUARD_REGE`.

## 6. Espaço de revisões e construção das candidatas

Seja `R0 = copy(R_impl_observado_E4_S009_A41)`. Seja:

\[
N(R)=RESTRICT\_INTERVAL(R,ARG1(I(p,n)),p)
\]

e:

\[
T(R)=CHANGE\_COMPONENT(N(R),\{p\},ARG1,REL)
\]

### 6.1 C0 — transferência sem nova guarda

\[
C0=T(R0)
\]

C0 testa o efeito estrutural mínimo do diff, não uma solução linguística já validada. Seu RHS será:

\[
REL(e,\{v\}\cup\{p\}),\quad ARG1(e,U\cup(I(p,n)-\{p\}))
\]

### 6.2 C1 — condicionamento sintático

Seja `P_syn` a conjunção formal das condições sintáticas previamente atribuídas a C1, incluindo os vínculos `p -> n` e `n -> v` com seus rótulos declarados. A construção deverá ser explícita:

1. copiar `R0`;
2. adicionar cada guarda de `P_syn` por `ADD_GUARD`, registrando sua natureza sintática;
3. aplicar `RESTRICT_INTERVAL`;
4. aplicar `CHANGE_COMPONENT`;
5. usar `SPLIT_RULE` para criar um branch `P_syn` revisado e um fallback `not P_syn` semanticamente igual a `R0`.

Assim, C1 não usa `case` como prova de regência; ela testa uma hipótese sintática distinta.

### 6.3 C2 — condicionamento por regência provisória

A construção deverá ser:

1. copiar `R0`;
2. aplicar `ADD_GUARD_REGE` ao branch especializado;
3. aplicar `RESTRICT_INTERVAL`;
4. aplicar `CHANGE_COMPONENT`;
5. aplicar `SPLIT_RULE` com três estados:
   - `TRUE_PROVISIONAL`: branch revisado;
   - `FALSE_PROVISIONAL`: fallback igual a `R0`;
   - `INDETERMINATE`: fallback conservador igual a `R0`, com resultado explicitamente marcado como não decidido.

Esse desenho não resolve a inferência operacional de regência. Ele testa uma candidata condicionada a uma classificação cuja fonte deverá ser declarada.

### 6.4 Imutabilidade e independência

Cada candidata começará de uma cópia lógica de `R0`. C1 não poderá ser derivada do objeto C0, nem C2 do objeto C1, salvo se a linhagem científica declarar intencionalmente essa dependência. A implementação deverá provar por hashes que `R0` e as candidatas irmãs permaneceram inalteradas.

## 7. Diff e custo de edição automáticos

### 7.1 Forma canônica

Cada regra terá serialização canônica independente de ordem acidental de listas ou dicionários. O diff comparará:

- variáveis;
- contexto;
- binders e intervalos;
- guardas adicionadas e removidas;
- efeitos adicionados, removidos e alterados;
- restrições;
- branches e políticas;
- proveniência e linhagem, reportadas separadamente do conteúdo semântico.

### 7.2 Vetor de edição

O resultado principal será um vetor, não apenas um escalar:

\[
D=(g^+,g^-,e^+,e^-,i,r,s)
\]

em que os termos contam adições/remoções de guardas, adições/remoções de efeitos, edições de intervalo, restrições e splits. Alterações de componente deverão ser reconhecidas como substituições correlacionadas, sem depender de descrição manual.

### 7.3 Custo

Antes dos testes, serão fixados pesos públicos para cada tipo de edição. O custo será:

\[
cost(R0,C)=w\cdot D(R0,C)
\]

Também será informado o número de operadores do histórico. O protocolo inicial recomenda pesos unitários como baseline e análise de sensibilidade separada; os pesos não poderão ser ajustados depois de observar qual candidata vence.

Para `ChoiceRule`, branches serão alinhados pela linhagem. A cópia inalterada de fallback não contará como uma sequência fictícia de edições; o split e as edições do branch especializado serão contados explicitamente.

### 7.4 Reconciliação

O histórico de operadores e o diff estrutural serão calculados por caminhos independentes. A candidata será inválida se uma edição estrutural não tiver `EditRecord`, se um `EditRecord` não aparecer no diff esperado ou se o hash da regra-pai tiver mudado.

## 8. Matching e uso efetivo de intervalos

### 8.1 Informações deriváveis do grafo

O matcher deverá derivar, quando a regra permitir:

- tokens e atributos;
- dependências e direção das arestas;
- ordem de `p` e `n`;
- candidatos que satisfazem as guardas da regra;
- `I(p,n)` pela ordem da sentença;
- `I(p,n)-{p}`;
- evidências de sucesso ou falha de cada guarda.

### 8.2 Informações ainda fornecidas como entrada

No primeiro v4, deverão ser declaradas como entradas, até que regras anteriores as derivem:

- identificação da extração e da sentença;
- núcleo candidato `v` de REL, se sua seleção não for formalizada no mesmo experimento;
- raiz candidata `n` do argumento, se sua seleção não for formalizada;
- contribuição preservada `U` de ARG1 quando houver outros mecanismos de construção;
- status provisório de `Rege(v,p)` para C2 e sua justificativa;
- GOLD, exclusivamente para avaliação posterior.

Esses campos não poderão aparecer como se tivessem sido inferidos pela candidata.

### 8.3 Construção do resultado

Na aplicação revisada, o ARG1 será construído por:

\[
ARG1'=U\cup(I(p,n)-\{p\})
\]

e REL por:

\[
REL'=REL_{base}\cup\{p\}
\]

O executor deverá iterar sobre a expressão de intervalo derivada. É proibido implementar o resultado apenas como `arg1_fornecido.remove(p)`. O ARG1 fornecido e o GOLD poderão ser usados para conferir o resultado, nunca para produzi-lo.

### 8.4 Invariantes do intervalo

Para toda aplicação válida:

- `p` e `n` existem no grafo;
- `ordem(p) <= ordem(n)`;
- todos os membros do intervalo existem e estão ordenados;
- `I = {p} union (I-{p})`;
- `{p} intersection (I-{p})` é vazio;
- os tokens diferentes de `p` mantêm multiplicidade e ordem;
- tokens de `U` não são alterados;
- pontuação e lacunas obedecem a uma política declarada, ainda a ser fixada.

## 9. Protocolo experimental

### 9.1 Separação entre derivação e avaliação

O pipeline será dividido em dois estágios sem compartilhamento oculto de GOLD:

**Derivação**

- fonte: evidência de S009-A41, regra do v2, trace e diff estrutural já documentados;
- saída: `R0`, C0, C1, C2, respectivos históricos, diffs e custos;
- GOLD não participa do matching nem da construção dos candidatos.

**Avaliação**

- carrega candidatos já congelados por hash;
- aplica-os aos casos selecionados;
- compara os estados produzidos com as expectativas documentadas;
- não modifica candidatos em resposta aos resultados.

S009-A42, A43 e A44 pertencem à mesma sentença de derivação e não serão tratados como evidência independente de generalização.

### 9.2 Dados disponíveis

O primeiro ciclo poderá usar, com as limitações já auditadas:

- S009-A41 como E− primário;
- S009-A42, A43 e A44 como variantes do mesmo contexto sentencial;
- S003-A20, S005-A28, S010-A51 e S010-A52 como controles modelados;
- os onze outputs baseline ainda não modelados somente após representação e rastreabilidade equivalentes;
- casos formais mínimos criados exclusivamente para testar a infraestrutura, claramente rotulados como fixtures e nunca como evidência de corpus.

Não há, no conjunto atual, E+ específico de E4 confirmado. Essa ausência impede uma avaliação forte de recall e de preservação de aplicações corretas de E4.

### 9.3 Testes obrigatórios

1. **Imutabilidade:** hashes de entrada não mudam após cada operador.
2. **Pré-condições dos operadores:** aplicações inválidas falham explicitamente, sem regra parcial silenciosa.
3. **Linhagem:** toda candidata referencia `R0` e contém histórico completo.
4. **Diff automático:** alterações detectadas correspondem aos `EditRecord`.
5. **Custo automático:** vetor e custo são reprodutíveis a partir das regras, sem tabela manual de resultados.
6. **Matching de S009-A41:** bindings, guardas e `I(p,n)` são verificáveis no grafo.
7. **Correção formal de S009-A41:** a candidata aplicável produz as fronteiras esperadas, sem consultar o GOLD durante aplicação.
8. **Integridade do intervalo:** o executor usa `I(p,n)` e preserva todos os tokens diferentes de `p`.
9. **Preservação de controles:** os quatro controles modelados são avaliados com justificativa do branch selecionado.
10. **Estado `INDETERMINATE`:** fixture formal verifica o branch conservador e a marcação de não decisão.
11. **Fallback:** quando a guarda especializada falha, o estado corresponde formalmente à aplicação de `R0`.
12. **ARG1 composto:** fixture com `U` não vazio verifica que somente a contribuição do intervalo é revisada.
13. **Ausência de vazamento do GOLD:** teste garante que o matcher e o executor não recebem campos GOLD.
14. **Cobertura declarada:** relatório distingue os oito casos modelados dos onze outputs baseline ainda não modelados.

### 9.4 Critérios de avaliação

Uma candidata será avaliada por:

- correção das fronteiras de S009-A41;
- número e natureza das aplicações nos casos modelados;
- preservação dos controles dentro do conjunto fechado;
- comportamento explícito em `INDETERMINATE`;
- satisfação dos invariantes de tokens e intervalos;
- diff e custo de edição automáticos;
- ausência de mutação da regra-pai;
- rastreabilidade entre guarda, match, branch, efeitos e resultado.

Resultados deverão ser classificados separadamente como:

- **correção formal no modelo**;
- **preservação condicional dos controles modelados**;
- **comportamento ainda indeterminado**;
- **não testado**.

Não serão inferidos, a partir deste ciclo, generalização para novas sentenças, inferência operacional autônoma de regência, equivalência com uma revisão Java ou ausência geral de regressões.

## 10. Critérios de consistência metodológica

Antes de qualquer execução, a futura implementação deverá demonstrar por inspeção e testes unitários que:

- C0, C1 e C2 existem como objetos-regra serializáveis;
- cada candidata é reconstruível apenas a partir de `R0` e de sua lista de operadores;
- o resultado não é produzido por branches independentes sem regras correspondentes;
- o intervalo derivado participa materialmente do RHS;
- GOLD está ausente das assinaturas de matching e aplicação;
- condições linguísticas, condições de código e contexto observado têm tipos distintos;
- `case` e `nmod` não determinam automaticamente `Rege`;
- `INDETERMINATE` tem semântica testável;
- a transformação corretiva do v2 não foi reutilizada como regra revisada de construção;
- nenhum resultado v3 foi alterado ou reclassificado silenciosamente.

## 11. Ameaças à validade

### 11.1 Validade de construto

- `Rege(v,p)` ainda não possui inferência operacional independente;
- `v`, `n` e `U` poderão continuar parcialmente fornecidos;
- a decomposição entre intervalo e contribuição preservada é uma decisão de modelagem;
- ARG1 no formalismo corresponde ao segundo argumento, chamado ARG2 no código Java.

### 11.2 Validade interna

- quatro E− vêm da mesma sentença;
- controles podem conter outras divergências e não equivalem a E+ de E4;
- o mecanismo de S009-A41 não foi confirmado para todos os outros casos;
- erros na anotação manual de regência ou de `U` podem controlar o resultado de C2.

### 11.3 Validade externa

- não há E+ específico de E4 confirmado;
- não há E− independente com proveniência equivalente;
- o conjunto atual não cobre variedade suficiente de verbos, preposições e estruturas;
- sucesso no modelo não implica sucesso no DptOIE Java.

### 11.4 Validade de conclusão

- pesos de custo podem favorecer uma candidata se definidos depois dos resultados;
- fixtures de `INDETERMINATE` testam software, não frequência ou comportamento em corpus;
- preservar quatro controles não demonstra ausência geral de regressão;
- igualdade de fronteiras não basta para provar adequação linguística geral.

### 11.5 Reprodutibilidade

- regras, dados, hashes, parâmetros, versão da infraestrutura e resultados deverão ser registrados;
- serialização e ordenação canônicas deverão evitar diferenças incidentais;
- as versões v1, v2 e v3 e seus relatórios permanecerão imutáveis.

## 12. Decisões a verificar antes da implementação

1. **Fonte de `Rege`:** definir um protocolo independente do GOLD para os três estados de regência.
2. **Guarda exata do intervalo:** mapear o predicado formal para a condição de código comprovada, sem transformar `case` em causa por conveniência.
3. **Bindings de `v` e `n`:** decidir se serão entradas explícitas no primeiro ciclo ou derivados por regras formais anteriores.
4. **Contribuição `U`:** definir como será anotada e validada quando ARG1 contiver tokens produzidos por outros mecanismos.
5. **Semântica de intervalo:** fixar tratamento de pontuação, tokens descontínuos, IDs não contíguos e limites inclusivos.
6. **Regra composta:** fixar prioridade, exaustividade e comportamento de branches incompatíveis.
7. **Modelo de grafo:** decidir entre multigrafo e arestas identificadas para preservar relações paralelas.
8. **Primitiva `ADD_GUARD`:** aprovar sua inclusão como infraestrutura genérica para C1 ou formalizar C1 inteiramente via `SPLIT_RULE`.
9. **Custo:** congelar pesos e política de alinhamento de branches antes de avaliar candidatas.
10. **Dados:** definir partição entre derivação, avaliação fechada e futuros casos independentes.
11. **Novos exemplos:** obter E+ específicos de E4 e E− independentes antes de qualquer alegação de generalização.
12. **Critério de avanço ao Java:** estabelecer evidência mínima no modelo antes de propor uma revisão no extrator.

## 13. Resultados permitidos e resultados vedados nesta etapa

O v4 poderá demonstrar, quando implementado e executado:

- que operadores reais transformam uma regra formal em candidatas rastreáveis;
- que o matcher e o executor usam um intervalo derivado;
- que uma candidata corrige formalmente S009-A41 no modelo;
- que os controles modelados são ou não preservados sob condições declaradas;
- que diff e custo são calculados automaticamente.

O v4 inicial não poderá, com os dados atuais, demonstrar:

- uma regra geral do DptOIE para E4;
- inferência autônoma e correta de regência;
- generalização para novas sentenças;
- preservação de E+ específicos de E4;
- ausência geral de regressões;
- revisão implementada ou validada no código Java.

Todas essas propriedades permanecerão marcadas como **A DEMONSTRAR** até que recebam experimentos próprios.
