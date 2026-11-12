# Análise estática do DptOIE para o experimento E4

- **Branch:** `experimento-proveniencia-e4`
- **Commit-base do código original:** `1a5ef708b1ed0a888aac63a7a4512af3cccad315`
- **Caso piloto S009:** saída DptOIE `(Catalano, voltou, para a área)`; GOLD `(Catalano, voltou para, a área)`; token crítico `para`.
- **Escopo:** análise estática dos componentes que deverão ser observados posteriormente em runtime.

**FATO DE CÓDIGO — integridade do código-fonte:** nenhum arquivo de código-fonte foi alterado para produzir esta análise. O DptOIE não foi executado, e nenhum logging foi adicionado.

**FATO DE CÓDIGO — limite metodológico:** esta análise localiza componentes e correspondências estruturais no código, mas não deriva \(R_{impl}^{E4}\), não atribui causalidade a D02 ou D03 e não propõe correção.

## 1. Ponto de entrada

**FATO DE CÓDIGO**

- **Arquivo:** `pom.xml` e `src/main/java/extrai_clausulas/Main.java`.
- **Classe:** `extrai_clausulas.Main`.
- **Método:** `public static void main(String[] args)`.
- **Responsabilidade:** interpretar os argumentos de linha de comando, preparar ou receber a árvore de dependências, carregar as sentenças, iniciar a extração e escrever as triplas.
- **Condições principais:** reconhece `-sentencesIN`, `-dependencyTreeIN`, `-CC`, `-SC` e `-appositive`. Se nem sentenças nem árvore forem fornecidas, lança exceção.
- **Chamador:** o launcher Java, pois o `pom.xml` declara `extrai_clausulas.Main` como `mainClass`.
- **Etapa seguinte:** se não houver `-dependencyTreeIN`, chama o pré-processamento e o parser; depois chama `Sentence.loadData`, `Sentence.mapeamentoSentences`, `Extracao1.realizaExtracao` e `Extracao1.imprimeExtracoes`.
- **Relação com D02/D03:** não implementa diretamente essas regras; apenas orquestra os métodos nos quais há correspondência estrutural com elas.

**FATO DE CÓDIGO:** os valores iniciais são `CC=false`, `SC=false` e `appositive=0`. Eles podem ser alterados pelos argumentos de linha de comando.

**HIPÓTESE QUE EXIGE RUNTIME:** ainda não é possível saber quais argumentos e opções foram empregados na execução que produziu as saídas de S009.

## 2. Parser utilizado

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/pre_processamento/PreProcessamento.java`.
- **Classe:** `pre_processamento.PreProcessamento`.
- **Métodos principais:** `retornaTokensSentencasSeparadoPorEspaco`, `geraEntradaConllParaDependencyParser` e `dependencyParser`.
- **Responsabilidade:** tokenizar as sentenças, atribuir POS, produzir a entrada CoNLL e executar o parser de dependências.
- **Chamador:** `Main.main`.
- **Etapa seguinte:** `Sentence.loadData` carrega o CoNLL resultante.

**FATO DE CÓDIGO:** `retornaTokensSentencasSeparadoPorEspaco` instancia `StanfordCoreNLP` com os anotadores `tokenize,ssplit`. A opção `tokenize.language` está configurada como `es`, embora os modelos carregados nas etapas seguintes sejam os modelos portugueses do projeto.

**FATO DE CÓDIGO:** `geraEntradaConllParaDependencyParser` usa `edu.stanford.nlp.tagger.maxent.MaxentTagger` com o modelo `pt-models/pt-pos-tagger.model`.

**FATO DE CÓDIGO:** `dependencyParser` usa `edu.stanford.nlp.parser.nndep.DependencyParser`, carrega `pt-models/pt-dep-parser.gz` e chama `testCoNLL`.

**FATO DE CÓDIGO:** se `-dependencyTreeIN` for fornecido, `Main.main` não chama o parser e usa diretamente o arquivo CoNLL informado.

**FATO DE CÓDIGO:** não foi encontrada referência no código-fonte ao arquivo `StanfordCoreNLP-pt.properties`; os caminhos dos modelos empregados por `PreProcessamento` estão definidos diretamente na classe.

**HIPÓTESE QUE EXIGE RUNTIME:** para S009, é necessário confirmar se a árvore foi gerada por `DependencyParser` durante a execução ou fornecida previamente por `-dependencyTreeIN`.

## 3. Representação dos tokens e dependências

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/extrai_clausulas/Token.java`.
- **Classe:** `extrai_clausulas.Token`.
- **Estrutura:** cada token mantém `id`, `form`, `lemma`, `cpostag`, `postag`, `feats`, `head`, `deprel`, `phead`, `pdeprel` e `tokensFilhos`.
- **Responsabilidade:** representar uma linha do formato CoNLL e a ligação do token com seu head e seus dependentes.

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/extrai_clausulas/Sentence.java`.
- **Classe:** `extrai_clausulas.Sentence`.
- **Métodos:** `loadData` e `mapeamentoSentences`.
- **Responsabilidade:** `loadData` lê as dez colunas CoNLL e cria os objetos `Token`; `mapeamentoSentences` adiciona cada token à coleção `tokensFilhos` do token apontado por `head`.
- **Chamador:** `Main.main`.
- **Etapa seguinte:** a sentença mapeada é entregue ao construtor de `Extracao1`.

**FATO DE CÓDIGO:** `Sentence` insere um token raiz sintético no índice zero. O mapeamento usa o valor de `head` para localizar diretamente o pai na lista da sentença.

**FATO DE CÓDIGO:** `SujeitoRelacao` mantém os deques do sujeito e da relação, os índices de seus núcleos, identificadores de módulos e vetores de tokens visitados.

**FATO DE CÓDIGO:** `Argumento` mantém uma pilha de segmentos de tokens que compõem um argumento.

**FATO DE CÓDIGO:** `SujeitoRelacaoArgumentos` reúne um `SujeitoRelacao` e sua lista de objetos `Argumento`.

## 4. Identificação do sujeito

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/extrai_clausulas/Extracao1.java`.
- **Classe:** `extrai_clausulas.Extracao1`.
- **Método:** `buscaSujeito(boolean SC)`.
- **Responsabilidade:** encontrar núcleos de sujeito e expandir seus constituintes.
- **Chamador:** `realizaExtracao`.
- **Etapa seguinte:** `realizaExtracao` chama `buscaRelacao`.

**FATO DE CÓDIGO:** um token inicia um sujeito quando sua relação é `nsubj` ou `nsubj:pass`.

**FATO DE CÓDIGO:** a expansão em profundidade do sujeito considera `nummod`, `advmod`, `nmod`, `amod`, `dep`, `obj`, relações que contêm `det`, `case`, pontuação aceita e alguns casos de `appos` e `conj`.

**FATO DE CÓDIGO:** quando `SC` está habilitado, `realizaExtracao` também chama o módulo de tratamento de pronome relativo.

**FATO DE CÓDIGO:** esse método não corresponde diretamente a D02 ou D03; ele fornece o sujeito e o índice de seu núcleo, que são pré-condições para a busca da relação descrita por D02.

**HIPÓTESE QUE EXIGE RUNTIME:** é necessário confirmar se `Catalano` recebeu `nsubj` ou `nsubj:pass`, qual foi seu `head` e se algum módulo adicional de sujeito foi acionado para S009.

## 5. Construção de REL

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/extrai_clausulas/Extracao1.java`.
- **Classe:** `extrai_clausulas.Extracao1`.
- **Método principal:** `buscaRelacao()`.
- **Auxiliares relevantes:** `buscaRelacaoAclPart`, `adicionaPedacoSujeitoRelacao`, `retornaTokenConcatenadoRelacao` e `setNovoIndiceNucleoRelacao`.
- **Responsabilidade:** iniciar REL no pai do núcleo do sujeito, expandi-la por DFS, registrar os tokens visitados e eventualmente ajustar seu núcleo.
- **Chamador:** `realizaExtracao`.
- **Etapa seguinte:** `buscaRelacaoAclPart`; depois, conforme as opções, processamento de coordenação; em seguida `carregaSRA`.

**FATO DE CÓDIGO:** o pai do sujeito é inicialmente definido como núcleo de REL e recebe identificador de módulo de extração `1`.

**FATO DE CÓDIGO:** para dependentes anteriores ao núcleo de REL, a busca aceita `aux:pass`, `obj`, `iobj`, `advmod`, `cop`, `aux`, `expl:pv`, `mark` e pontuação conforme a condição implementada.

**FATO DE CÓDIGO:** para dependentes posteriores ao pai do sujeito, aceita `flat`, `expl:pv`, hífen com `punct` e `acl:part` sujeito a `verificaAclPartPrimeiroFilhoRelacao`.

**FATO DE CÓDIGO:** `retornaTokenConcatenadoRelacao` concatena o núcleo diretamente; trata `obj`, `aux:pass`, `iobj`, `advmod`, `cop`, `aux`, `dep` e `mark` por intervalo; e trata diretamente `flat`, `acl:part`, `punct` e `expl:pv`.

**FATO DE CÓDIGO:** `case` não aparece como relação aceita explicitamente na DFS principal de `buscaRelacao` nem nas condições explícitas de `retornaTokenConcatenadoRelacao`.

**FATO DE CÓDIGO:** a estrutura de `buscaRelacao` e `buscaRelacaoAclPart` possui correspondência direta com D02: a busca parte do pai do sujeito e contempla o caso alternativo `acl:part`.

**FATO DE CÓDIGO:** a implementação não é uma transcrição literal e isolada do catálogo: há condições posicionais, tratamento de `flat` e pontuação, alteração possível do núcleo e funções auxiliares adicionais.

**HIPÓTESE QUE EXIGE RUNTIME:** se `para` estiver anotado como `case` de um complemento nominal, ele não será selecionado diretamente pelas condições explícitas da DFS principal de REL. A anotação real e possíveis formas indiretas de concatenação ainda precisam ser observadas.

**HIPÓTESE QUE EXIGE RUNTIME:** a correspondência estrutural com D02 não demonstra que D02, isoladamente, tenha produzido a REL `voltou` de S009.

## 6. Construção do segundo argumento

**FATO DE CÓDIGO**

- **Arquivo:** `src/main/java/extrai_clausulas/Extracao1.java`.
- **Classe:** `extrai_clausulas.Extracao1`.
- **Métodos principais:** `carregaSRA`, `extraiClausulas` e `extraiClausulasQuebradas`.
- **Auxiliares relevantes:** `adicionaPedacoArgumento`, `retornaTokenConcatenadoSujeitoArgumentos`, `verificaTokenFilhoSujeito` e `separaParteTokensRelacaoEmArgumentos`.
- **Responsabilidade:** copiar cada `SujeitoRelacao` para um `SujeitoRelacaoArgumentos`, percorrer os filhos do núcleo de REL e construir um ou mais segundos argumentos.
- **Chamador:** `realizaExtracao`.
- **Etapa seguinte:** módulos opcionais e pós-processamentos; ao final, as estruturas ficam disponíveis para impressão e escrita no CSV.

**FATO DE CÓDIGO:** em `extraiClausulas`, a DFS parte dos filhos do núcleo da relação.

**FATO DE CÓDIGO:** a seleção considera `nmod`, `xcomp`, `dobj`, `obj`, `acl:relcl`, `iobj`, `conj`, `acl:part`, `nummod`, `advmod`, `appos`, `amod`, `ccomp`, `advcl`, `dep` e certos casos de `punct`.

**FATO DE CÓDIGO:** para `ccomp` e `advcl`, a inclusão direta exige que `verificaTokenFilhoSujeito` não encontre sujeito; há tratamento separado quando `SC` está ativo e existe sujeito subordinado.

**FATO DE CÓDIGO:** os argumentos produzidos são anexados à estrutura pelo método `SujeitoRelacaoArgumentos.addArg2`.

**FATO DE CÓDIGO:** `retornaTokenConcatenadoSujeitoArgumentos` trata, entre outras relações, um token `nmod`. Quando um filho desse token aparece antes de seu próprio head, o método adiciona à cláusula todos os tokens do intervalo entre o filho e o head, inclusive.

**FATO DE CÓDIGO:** `extraiClausulasQuebradas`, chamado logo após `extraiClausulas`, pode produzir argumentos alternativos; o código atribui identificador de módulo `7` aos argumentos dessa etapa, enquanto `extraiClausulas` usa o identificador `1`.

**FATO DE CÓDIGO:** a lista de dependências e o início da DFS nos filhos de REL apresentam correspondência direta com D03. A condição especial para `ccomp` e `advcl` sem `nsubj`/`nsubj:pass` também aparece na implementação por meio de `verificaTokenFilhoSujeito`.

**HIPÓTESE QUE EXIGE RUNTIME:** se o parser representar `área` como `nmod` ligado a `voltou` e `para` como um filho anterior de `área`, o intervalo construído por `retornaTokenConcatenadoSujeitoArgumentos` pode incluir `para` no segundo argumento.

**HIPÓTESE QUE EXIGE RUNTIME:** essa configuração explicaria estruturalmente como `para a área` poderia ser construído como argumento, mas ainda não prova que esse foi o parse ou o caminho percorrido em S009.

**HIPÓTESE QUE EXIGE RUNTIME:** não é possível determinar estaticamente se a extração piloto veio de `extraiClausulas`, `extraiClausulasQuebradas` ou de alguma transformação posterior.

## 7. Montagem da tripla

**FATO DE CÓDIGO**

- **Estrutura de montagem:** `src/main/java/extrai_clausulas/SujeitoRelacaoArgumentos.java`.
- **Responsabilidade:** manter juntos o sujeito/REL e a lista de segundos argumentos antes da serialização.

**FATO DE CÓDIGO**

- **Arquivo e método de formatação:** `Extracao1.retornaExtracaoComArgumentoEspecifico`.
- **Responsabilidade:** obter as representações textuais do sujeito, de REL e de um argumento específico e formar a extração exibida.
- **Chamador:** `Extracao1.imprimeExtracoes`.
- **Etapa seguinte:** impressão da extração e de eventuais subextrações.

**FATO DE CÓDIGO**

- **Arquivo e método de saída CSV:** `Main.main`.
- **Responsabilidade:** para cada `SujeitoRelacaoArgumentos` e cada `Argumento`, obter `getStringSujeitoSemMarkInicio()`, `getStringRelacao()` e `Argumento.toString()` e escrever a linha final.
- **Etapa seguinte:** fechamento do escritor ao terminar todas as sentenças.

**FATO DE CÓDIGO:** no código, o componente que o contexto científico chama de `ARG0` é representado como `sujeito`. O CSV usa o cabeçalho `ARG1`, `REL`, `ARG2`, confirmando a inconsistência de nomenclatura já documentada no contexto.

## 8. Correspondência estática com D02 e D03

| Regra catalogada | Correspondência encontrada | Classificação |
|---|---|---|
| D02 — identificação de REL a partir do pai do sujeito ou de `acl:part` | `Extracao1.buscaRelacao`, `buscaRelacaoAclPart`, `retornaTokenConcatenadoRelacao` e auxiliares | **FATO DE CÓDIGO:** correspondência estrutural forte, mas não identidade completa com a descrição do catálogo |
| D03 — DFS nos filhos de REL para construir o segundo argumento | `Extracao1.extraiClausulas`, `extraiClausulasQuebradas`, `retornaTokenConcatenadoSujeitoArgumentos` e `verificaTokenFilhoSujeito` | **FATO DE CÓDIGO:** correspondência estrutural forte, com heurísticas e módulos adicionais não resumidos pelo catálogo |
| D02 como causa de S009 | O código contém o mecanismo candidato, mas não informa quais ramos foram percorridos nessa execução | **HIPÓTESE QUE EXIGE RUNTIME** |
| D03 como causa de S009 | O código contém o mecanismo candidato, mas não informa qual módulo originou a saída piloto | **HIPÓTESE QUE EXIGE RUNTIME** |
| Interação D02–D03 | A fronteira entre REL e o segundo argumento pode depender das duas etapas | **HIPÓTESE QUE EXIGE RUNTIME** |

**FATO DE CÓDIGO:** esta análise localiza correspondências de implementação, mas não estabelece que D02, D03 ou sua interação tenham causado o erro.

**FATO DE CÓDIGO:** nenhuma representação de \(R_{impl}^{E4}\) foi derivada nesta etapa.

## 9. Caminho estático provável

**FATO DE CÓDIGO:** para o caminho padrão iniciado por `-sentencesIN`, a sequência estática é:

| Transição | Arquivo, classe e método |
|---|---|
| sentença → parser | `Main.main` → `PreProcessamento.retornaTokensSentencasSeparadoPorEspaco` → `geraEntradaConllParaDependencyParser` → `dependencyParser` |
| parser → estrutura de dependências | `Main.main` → `Sentence.loadData` → `Sentence.mapeamentoSentences` |
| dependências → identificação do sujeito | `Extracao1.realizaExtracao` → `Extracao1.buscaSujeito` |
| sujeito → construção de REL | `Extracao1.realizaExtracao` → `Extracao1.buscaRelacao` → `buscaRelacaoAclPart` |
| REL → construção do segundo argumento | `Extracao1.carregaSRA` → `Extracao1.extraiClausulas` → `extraiClausulasQuebradas` |
| sujeito + REL + segundo argumento → tripla | `SujeitoRelacaoArgumentos` → `Extracao1.retornaExtracaoComArgumentoEspecifico`/`imprimeExtracoes` e `Main.main` para o CSV |

**HIPÓTESE QUE EXIGE RUNTIME:** o caminho específico da extração piloto pode ser um subconjunto desse fluxo e pode incluir pós-processamentos adicionais executados por `realizaExtracao`.

## 10. Pontos que exigem confirmação em runtime

- **HIPÓTESE QUE EXIGE RUNTIME:** qual modalidade de entrada foi usada para S009: `-sentencesIN` com parser interno ou `-dependencyTreeIN` com árvore previamente produzida.
- **HIPÓTESE QUE EXIGE RUNTIME:** quais valores efetivos foram usados para `CC`, `SC` e `appositive`.
- **HIPÓTESE QUE EXIGE RUNTIME:** o parse completo realmente recebido pelo extrator, incluindo `id`, `form`, `lemma`, POS, `head` e `deprel` de cada token.
- **HIPÓTESE QUE EXIGE RUNTIME:** a relação de dependência atribuída a `para`, seu head e sua posição em relação a esse head.
- **HIPÓTESE QUE EXIGE RUNTIME:** se `Catalano` foi identificado como `nsubj`/`nsubj:pass` de `voltou`.
- **HIPÓTESE QUE EXIGE RUNTIME:** se `voltou` foi efetivamente selecionado como pai do sujeito e núcleo inicial de REL.
- **HIPÓTESE QUE EXIGE RUNTIME:** quais condições de `buscaRelacao`, `buscaRelacaoAclPart` e `setNovoIndiceNucleoRelacao` foram avaliadas e quais produziram resultado verdadeiro.
- **HIPÓTESE QUE EXIGE RUNTIME:** se `para` foi examinado na construção de REL, recusado por não satisfazer as relações aceitas ou alcançado indiretamente por alguma concatenação.
- **HIPÓTESE QUE EXIGE RUNTIME:** se `área` foi representado como `nmod`, `obj` ou outra relação aceita na construção do segundo argumento.
- **HIPÓTESE QUE EXIGE RUNTIME:** se `para` foi incorporado ao argumento pelo intervalo criado em `retornaTokenConcatenadoSujeitoArgumentos`.
- **HIPÓTESE QUE EXIGE RUNTIME:** qual chamada de `addArg2` originou especificamente `(Catalano, voltou, para a área)`.
- **HIPÓTESE QUE EXIGE RUNTIME:** se a saída piloto foi produzida pelo módulo principal de argumentos, pelo módulo de cláusulas quebradas ou por algum pós-processamento.
- **HIPÓTESE QUE EXIGE RUNTIME:** quais identificadores de módulo foram associados ao sujeito, à relação e ao argumento dessa extração.
- **HIPÓTESE QUE EXIGE RUNTIME:** se o mesmo caminho também originou as três variantes relacionadas da sentença.
- **HIPÓTESE QUE EXIGE RUNTIME:** se D02, D03, a interação entre ambas ou outro mecanismo constitui a proveniência efetiva do resultado.
- **HIPÓTESE QUE EXIGE RUNTIME:** a representação de \(R_{impl}^{E4}\), que permanece não determinada.
