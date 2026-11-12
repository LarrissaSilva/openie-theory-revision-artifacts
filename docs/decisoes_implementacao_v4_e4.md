# Decisões de implementação da Theory Revision v4 — E4

## 1. Finalidade e momento do registro

Este documento fixa as decisões técnicas da implementação v4 antes da execução dos testes. Ele operacionaliza o protocolo versionado no commit `4183b5e` e toma a auditoria metodológica do v3 como restrição prioritária.

O objetivo do v4 é demonstrar que C0, C1 e C2 são objetos-regra completos, obtidos por operadores explícitos aplicados a uma regra formal imutável. O experimento não modifica o DptOIE Java, não executa o extrator, não usa solver e não busca ainda uma Theory Revision generalizada.

As decisões abaixo são classificadas como:

- **EVIDÊNCIA DE CÓDIGO:** diretamente verificável no código-fonte;
- **EVIDÊNCIA DE TRACE:** diretamente registrada no trace de S009-A41;
- **DECISÃO DE IMPLEMENTAÇÃO:** escolha adotada para o v4;
- **ENTRADA EXPERIMENTAL:** informação que o matcher não descobre;
- **HIPÓTESE/LIMITAÇÃO:** elemento ainda não demonstrado empiricamente.

## 2. Condição que acionou o intervalo em S009-A41

### 2.1 Condição de entrada do método

**EVIDÊNCIA DE CÓDIGO:** em `Extracao1.retornaTokenConcatenadoSujeitoArgumentos`, o bloco de concatenação é executado quando o token recebido tem um dos `deprel` aceitos pelo `if` da linha 1339, entre eles `nmod`. Em S009-A41, o token recebido foi `área`, token 5, com `deprel=nmod`.

### 2.2 Condição operacional do intervalo

**EVIDÊNCIA DE CÓDIGO:** dentro do laço sobre `token.getTokensFilhos()`, o teste que inicia a operação é:

```java
tokensFilhos.getId() < tokensFilhos.getHead()
```

A inclusão dos tokens do intervalo ocorre somente enquanto `flag=true`. Após o primeiro filho à esquerda processado, `flag` é alterado para `false`. Os limites usados são inclusivos:

```java
for (int i = tokensFilhos.getId(); i <= tokensFilhos.getHead(); i++)
```

O código não testa `tokensFilhos.getDeprel().equals("case")` nessa decisão.

**EVIDÊNCIA DE CÓDIGO:** `Sentence.mapeamentoSentences` percorre o array da sentença e adiciona cada token à lista de filhos do head nessa ordem. Portanto, no artefato observado, a ordem da lista de filhos acompanha a ordem dos tokens carregados.

**EVIDÊNCIA DE TRACE:** em S009-A41, `para` tinha `id=3`, `head=5`, foi o primeiro filho à esquerda examinado com intervalo disponível e acionou `[3,5]`. A operação adicionou `para`, `a` e `área`.

### 2.3 Representação no v4

O predicado operacional será representado como:

```text
ARG_ROOT_ALLOWED(n)
AND FIRST_LEFT_CHILD(p,n)
AND order(p) < order(n)
```

em que:

- `ARG_ROOT_ALLOWED(n)` verifica o conjunto de `deprel` aceitos pelo método;
- `FIRST_LEFT_CHILD(p,n)` seleciona o primeiro filho de `n`, por ordem de token, que está à esquerda do próprio head;
- `Interval(p,n)` usa limites inclusivos.

`dep(p,n,case)` permanece contexto observado. Ele somente se torna guarda em C1 por `ADD_GUARD`, como hipótese sintática deliberada. Não será apresentado como condição que acionou o intervalo no Java nem como prova de `Rege(v,p)`.

## 3. Informações derivadas e entradas experimentais

### 3.1 Derivadas do grafo

O v4 derivará:

- tokens, formas, POS, heads, `deprel` e ordem;
- arestas de dependência;
- filhos de cada token em ordem;
- o primeiro filho à esquerda `p` de cada raiz candidata `n`;
- `I(p,n)` por ordem de tokens e com limites inclusivos;
- `I(p,n)-{p}`;
- valores das guardas estruturais e sintáticas;
- branch aplicável de cada regra composta;
- componentes resultantes a partir dos efeitos formais.

### 3.2 Entradas experimentais

Continuarão fornecidos:

- identificador da sentença e da extração;
- núcleo candidato `v` de REL;
- raízes candidatas `n` de contribuições ao argumento;
- ARG0 e REL baseline, para os mecanismos anteriores à operação estudada;
- contribuição externa `U` de ARG1;
- status provisório de `Rege(v,p)` e sua origem;
- fronteiras baseline e GOLD, exclusivamente para validação posterior.

**LIMITAÇÃO:** o primeiro v4 não formaliza a seleção de `v`, a descoberta de todas as raízes `n` nem os demais mecanismos que produzem `U`. O experimento testa a edição da fronteira sobre o mecanismo de intervalo já identificado.

### 3.3 Seleção de `p`

`p` não será fornecido ao matcher. Para cada `n` experimental, ele será derivado como o primeiro filho à esquerda segundo a ordem dos tokens. A asserção dos casos reais verificará se o `p` derivado coincide com o token documentado anteriormente.

## 4. Representação de `U`

`U` representa os tokens de ARG1 produzidos por mecanismos externos ao intervalo estudado. Será uma expressão formal `Preserved(ids)` e uma entrada experimental rastreável.

Para cada caso, o baseline deverá ser reconstruído por:

\[
ARG1_{baseline}=U\cup I_1\cup\ldots\cup I_k
\]

e não simplesmente copiado para a execução da revisão. A implementação verificará que essa reconstrução coincide com o span baseline documentado.

Quando uma candidata transferir `p_i`, o resultado será construído por:

\[
ARG1'=U\cup\bigcup_i (I_i-T_i)
\]

em que `T_i={p_i}` apenas para matches com branch de transferência; para fallback, `T_i` é vazio.

**HIPÓTESE/LIMITAÇÃO:** a atribuição de tokens a `U` ou a um intervalo é uma decomposição experimental. Ela não prova qual método do Java produziu cada token fora de S009-A41.

## 5. Ordem, pontuação e intervalos

- A ordem será dada pelo atributo `ordem` carregado do CoNLL; o ID será preservado, mas não será usado como sinônimo obrigatório de posição.
- Os limites do intervalo serão inclusivos e determinados por `ordem(p)` e `ordem(n)`.
- Todos os tokens entre os limites serão incluídos, inclusive pontuação, reproduzindo o laço observado. Não haverá filtragem linguística silenciosa.
- Intervalos descontínuos não serão fabricados: a expressão representa todos os tokens existentes entre os limites na ordem total.
- Um match será inválido se `p` ou `n` não existir, se `p` não for filho de `n`, se `order(p) >= order(n)`, se o intervalo for vazio ou se `p/n` não pertencerem ao intervalo.
- A partição deverá satisfazer união completa, interseção vazia, preservação de multiplicidade e preservação da ordem.

Fixtures específicas testarão pontuação e IDs não contíguos. Essas fixtures validam a infraestrutura, não constituem exemplos do corpus.

## 6. Grafo e arestas paralelas

Será usado `networkx.MultiDiGraph`.

Cada aresta terá chave estável e camada explícita, por exemplo:

- `DEPENDENCY`;
- `OPENIE`;
- `CONSTRUCTION`;
- `LINGUISTIC`.

Isso evita que relações diferentes entre o mesmo par de nós se sobrescrevam. A serialização canônica incluirá origem, destino, chave e atributos da aresta.

## 7. Objetos-regra, exclusividade e fallback

### 7.1 Imutabilidade

Regras, guardas, efeitos, expressões de tokens, proveniência, registros de edição e branches serão dataclasses congeladas com conteúdo composto apenas por tuplas e valores imutáveis. Cada regra terá serialização e hash canônicos.

Todo operador receberá uma regra e retornará nova regra mais `EditRecord`. A implementação verificará que o hash da entrada não muda.

### 7.2 Regras atômicas e compostas

- C0 será uma regra atômica revisada. Se seu LHS não casar, a semântica geral de não aplicação preservará o estado baseline.
- C1 será `ChoiceRule` binária: branch sintático revisado e fallback que preserva `R_impl`.
- C2 será `ChoiceRule` trivalorada: `TRUE_PROVISIONAL` revisa; `FALSE_PROVISIONAL` preserva; `INDETERMINATE` preserva e registra não decisão.

### 7.3 Exclusividade

Cada branch usará predicados formais de status/guarda. Antes da aplicação, `ChoiceRule` verificará:

- no máximo um branch especializado aplicável;
- fallback explícito quando nenhum branch especializado casa;
- cobertura dos três estados de C2;
- erro, e não escolha silenciosa, se branches especializados forem simultaneamente aplicáveis.

O executor será genérico: ele selecionará branches a partir dos objetos-regra. Não conterá `if candidate_name == "C0"/"C1"/"C2"` para implementar seus comportamentos.

## 8. `ADD_GUARD` e derivação de C1

`ADD_GUARD` será uma primitiva genérica da álgebra de regras. Ela adicionará uma guarda tipada, recusará duplicatas e contradições e produzirá `EditRecord`.

C1 será derivada assim:

1. copiar logicamente `R_impl`;
2. `ADD_GUARD(dep(p,n,case))`;
3. `ADD_GUARD(dep(n,v,nmod))`;
4. `RESTRICT_INTERVAL`;
5. `CHANGE_COMPONENT(ARG1,REL,{p})`;
6. `SPLIT_RULE` entre a especialização sintática e o fallback original.

`ADD_GUARD_REGE` será uma especialização de `ADD_GUARD`, com validação do domínio trivalorado e da origem da classificação. Ele não será usado para as guardas sintáticas de C1.

## 9. Fonte e tratamento de `Rege(v,p)`

**QUESTÃO DE PESQUISA NÃO RESOLVIDA:** ainda não existe reconhecedor operacional independente para `Rege(v,p)`.

O v4 reutilizará as classificações provisórias do v3 somente para testar a mecânica formal de C2. Cada status guardará:

- valor `TRUE_PROVISIONAL`, `FALSE_PROVISIONAL` ou `INDETERMINATE`;
- justificativa;
- origem manual;
- indicação explícita de que o GOLD participou ou não da fundamentação.

O matcher e o executor não receberão GOLD. A classificação provisória será uma entrada distinta. O relatório reconhecerá que, nos casos reais atuais, essa entrada foi parcialmente fundamentada pelo GOLD e, portanto, o sucesso de C2 não é validação independente nem reconhecimento de regência.

Um fixture `INDETERMINATE` será criado apenas para testar o branch conservador. Ele não será apresentado como ocorrência real do corpus.

## 10. Diff e custo estrutural

### 10.1 Diff automático

A forma canônica das regras será comparada automaticamente nas dimensões:

- guardas adicionadas/removidas;
- efeitos adicionados/removidos;
- expressões de intervalo alteradas;
- restrições adicionadas/removidas;
- splits e branches;
- proveniência e linhagem, reportadas separadamente.

Mudanças de componente serão pareadas como remoção de um efeito na origem e adição do efeito correspondente no destino.

### 10.2 Pesos congelados antes da avaliação

Serão usados pesos unitários:

```text
guarda adicionada/removida = 1
efeito adicionado/removido = 1
edição/partição de intervalo = 1
restrição adicionada/removida = 1
split de regra = 1
```

O resultado principal será o vetor estrutural; o total será a soma unitária. Proveniência e metadados não terão custo semântico.

Para regras compostas, o fallback inalterado não será contado como cópia de todas as estruturas. Contam o split e as edições do branch especializado. O histórico de operadores será reconciliado com o diff; divergência invalida a candidata.

## 11. Dados reais e fixtures

### 11.1 Casos reais

Serão reutilizados os oito casos já rastreados no v3:

- S009-A41 como E− primário;
- S009-A42, A43 e A44 como variantes da mesma sentença;
- S003-A20, S005-A28, S010-A51 e S010-A52 como controles modelados.

Os hashes da planilha e dos quatro parses deverão ser verificados antes dos testes.

### 11.2 Fixtures de infraestrutura

Serão criados fixtures claramente rotulados para:

- `INDETERMINATE`;
- `U` não vazio;
- intervalo com pontuação;
- IDs não contíguos;
- pré-condição inválida;
- tentativa de branches especializados sobrepostos.

Fixtures não entram na contagem de casos de corpus e não sustentam generalização linguística.

## 12. Escopo reduzido e critérios de interpretação

O v4 poderá demonstrar:

- edição real de objetos-regra;
- derivação independente de C0, C1 e C2;
- matching e uso efetivo do intervalo;
- diff e custo automáticos;
- correção formal de S009-A41 no modelo;
- preservação ou sobreaplicação condicional nos controles modelados;
- funcionamento do fallback `INDETERMINATE` em fixture.

O v4 não demonstrará:

- descoberta operacional de regência;
- mecanismo geral do DptOIE além de S009-A41;
- preservação de E+ E4, ainda ausentes;
- não regressão dos onze outputs baseline não modelados;
- generalização para novas sentenças;
- revisão implementada no Java.

Qualquer decisão não sustentada diretamente — especialmente `U`, raízes `n`, núcleo `v` e status de regência — permanecerá visível como entrada experimental ou limitação, nunca como resultado derivado.
