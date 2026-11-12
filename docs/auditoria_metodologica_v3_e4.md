# Auditoria metodológica da primeira Theory Revision exploratória de E4

## Qualificadores da auditoria

- **DADO EMPÍRICO:** obtido da planilha, dos outputs, dos parses ou do trace preservado do DptOIE.
- **DADO FORNECIDO AO MODELO:** codificação manual usada como entrada do experimento v3.
- **RESULTADO FORMAL:** consequência da execução do código do notebook sobre as entradas codificadas.
- **NÃO DEMONSTRADO:** propriedade não coberta pelas entradas, pelo matching ou pelas asserções executadas.

Esta auditoria é somente estática e documental. O notebook v3 não foi reexecutado e nenhum resultado anterior foi modificado.

## 1. Objetivo da auditoria

Verificar se as conclusões registradas para C0, C1 e C2 correspondem ao que o notebook efetivamente implementa e testa, distinguindo:

1. evidências reais do DptOIE;
2. hipóteses linguísticas fornecidas manualmente;
3. abstrações de Graph Rewriting;
4. resultados formais internos ao modelo;
5. afirmações que exigiriam novos dados ou implementação no extrator.

A auditoria também verifica a correspondência entre o protocolo pré-registrado, o notebook executado e o relatório de resultados, sem corrigir retrospectivamente qualquer um desses artefatos.

## 2. Experimentos e evidências examinados

### Artefatos principais

- `docs/protocolo_theory_revision_e4.md`, commit `79e77b8`;
- `research/graph_rewriting/experimento_v3_e4_theory_revision.ipynb`, commit `a04254d`;
- `docs/resultados_theory_revision_e4.md`, commit `a04254d`;
- `docs/comparacao_graph_rewriting_e4_s009.md`, commit `67a62a7`;
- `docs/baseline_controles_e4.md`, commit `6bde4e2`;
- planilha OIEC-PT-GOLD e CoNLL preservados de S003, S005, S009 e S010;
- trace de S009, commit `2e7ee06`, e validação de não interferência, commit `3da8e3a`.

### Integridade do notebook auditado

- SHA-256: `da2ef408d976a4afea809b21c23a63413414b25463ef6bdfcadcf24b67ddd099`;
- 14 células, 7 de código;
- contadores de execução contínuos `1..7`;
- zero outputs de erro;
- 24 combinações registradas: 3 candidatos × 8 extrações.

### Evidências reais lidas pelo v3

O notebook lê e verifica por SHA-256:

- a planilha experimental;
- `output_DP.conll` de S003, S005, S009 e S010.

Da planilha são lidos identificador da sentença, extrator, classificação, extração e componentes textuais. Dos CoNLL são lidos `ID`, `FORM`, `POS`, `HEAD` e `DEPREL` de todos os tokens. O notebook confirma que as oito linhas selecionadas pertencem ao DptOIE e que os textos dos spans baseline codificados para ARG0, REL e ARG1 coincidem com os componentes extraídos da planilha, após normalização de espaços.

## 3. Escopo real da implementação

### Informações fornecidas manualmente

Em `CASES`, o notebook codifica manualmente, para cada extração:

- IDs de ARG0, REL e ARG1 baseline;
- IDs esperados depois da alteração de E4;
- IDs usados para representar o GOLD;
- núcleo de REL (`relation_core`);
- token preposicional `p` e raiz nominal/verbal local `n`;
- classe `E_MINUS_*` ou `CONTROL`;
- `TRUE_PROVISIONAL` ou `FALSE_PROVISIONAL`;
- justificativa linguística e observações de escopo;
- valores de complexidade atribuídos a C0, C1 e C2.

Os spans baseline não são descobertos a partir do grafo: são fornecidos e depois validados contra o texto extraído da planilha. Os spans esperados e do GOLD também são fornecidos como tuplas de IDs; não há asserção equivalente que os reconstrua automaticamente do texto GOLD.

### Construção dos grafos

`build_input_graph` cria um grafo com:

- todos os tokens e dependências reais da sentença;
- ARG0 previamente conhecido;
- o núcleo de REL fornecido como `CANDIDATO_NUCLEO_REL`;
- nenhuma aresta REL ou ARG1.

`apply_construction` calcula os alvos transferidos e somente então adiciona ao grafo:

- os IDs de REL baseline já fornecidos;
- as preposições cujo matching teve sucesso;
- todos os IDs de ARG1 baseline, exceto as preposições transferidas.

Logo, não é aplicada a transformação corretiva `G_impl → G_gold` sobre um estado final já materializado. Entretanto, a construção também não descobre REL e ARG1 a partir das dependências: ela monta o resultado usando fronteiras baseline previamente conhecidas.

**Conclusão de escopo:** o v3 implementa uma **transformação condicionada de uma construção com componentes conhecidos**. Ele representa revisão dos efeitos de fronteira no nível abstrato, mas não reproduz de ponta a ponta o mecanismo de construção do DptOIE.

### Matching implementado

C0 testa:

- `p` pertence ao ARG1 baseline fornecido;
- `n` tem como head o núcleo `v` fornecido;
- `p` tem como head `n`;
- `p` precede `n`;
- existe pelo menos um token entre as ordens de `p` e `n`.

C1 acrescenta:

- `deprel(p)=case`;
- `deprel(n)=nmod`.

C2 acrescenta ao matching-base:

- `status_rege == TRUE_PROVISIONAL`.

Qualquer alvo de C2 que não seja `TRUE_PROVISIONAL` segue o ramo conservador. Não existe caso executado com `INDETERMINATE`.

### Intervalo e efeitos

O intervalo `p..n` é calculado e sua não vacuidade participa do matching. Contudo, os seus tokens não são usados para construir ARG1. O efeito `RESTRICT_INTERVAL` é operacionalizado retirando `p` do **span ARG1 completo fornecido**, e não reconstruindo explicitamente `I(p,n)\{p}`.

Essa implementação produz o efeito desejado nos casos codificados, mas constitui uma abstração do intervalo observado no trace de A41.

## 4. Rastreabilidade entre dados, hipóteses, operadores e resultados

| Afirmação científica | Evidência correspondente | Limitação |
|---|---|---|
| O DptOIE produziu a divergência E4 em S009-A41 | reprodução baseline, planilha e trace versionados | proveniência detalhada somente para A41 |
| Em A41, `para` entrou em ARG1 pela operação de intervalo | eventos do trace e `docs/proveniencia_e4_s009.md` | não demonstra regra geral nem mecanismo dos controles |
| C0 corrige o aspecto E4 nos quatro outputs S009 | matriz v3 e estados resultantes | quatro outputs compartilham a mesma sentença, parse e par `voltou–para` |
| C0 sobreaplica em S005 e S010 | matching procedural do v3 e matriz executada | comportamento simulado sobre alvos e spans fornecidos; não execução do Java |
| `case+nmod` é insuficiente nos casos modelados | C1 transfere `en` em S010-A51/A52 | evidência negativa baseada em um único contexto locativo independente |
| C2 preserva os quatro controles modelados | `FALSE_PROVISIONAL` bloqueia transferência e asserções passam | preservação condicionada por rótulos manuais derivados também do GOLD |
| C2 corrige os E− modelados | `TRUE_PROVISIONAL` habilita transferência de `para` | o modelo recebe a decisão de regência; não a infere |
| A43/A44 mantêm E3/S3 | estado esperado preserva todos os tokens exceto `para` | não há avaliação integral desses outputs contra o GOLD |
| C0 é estruturalmente menor que C1/C2 | vetores de complexidade pré-registrados e reproduzidos | valores são constantes fornecidas, não diffs calculados de objetos-regra |
| C2 foi o único candidato que satisfez o conjunto fechado | classificação global e asserções do v3 | não implica superioridade fora do conjunto nem revisão validada |
| A não regressão dos 15 outputs foi demonstrada | nenhuma | somente quatro dos 15 outputs dos controles foram modelados |
| Há capacidade operacional de reconhecer regência | nenhuma | `StatusRege` é fornecido manualmente |

### Influência do GOLD

O GOLD participa de duas etapas:

1. fundamenta as classificações manuais `TRUE_PROVISIONAL`/`FALSE_PROVISIONAL`;
2. fornece a referência de avaliação e ajuda a definir os estados esperados.

Assim, especialmente em C2, parte da informação usada para decidir o ramo da regra provém da mesma fonte usada para avaliar o resultado. O teste demonstra consistência condicional com a anotação, não validação independente ou descoberta da regra linguística.

## 5. Avaliação da validade interna

### Aspectos sustentados

- Os arquivos de entrada foram verificados por hash.
- Os oito outputs selecionados e os spans baseline foram ligados a dados reais da planilha e dos parses.
- Os candidatos foram aplicados a cópias independentes dos grafos.
- REL e ARG1 estavam ausentes nos grafos de entrada, afastando a interpretação de simples aplicação de `R_gold_correcao_E4` sobre `G_impl`.
- As classificações globais relatadas correspondem ao código e aos outputs preservados.
- C0 e C1 efetivamente encontram contraexemplos dentro do conjunto modelado.
- O relatório original distingue corretamente o sucesso condicional de C2 de reconhecimento automático de regência.

### Propriedades demonstradas pelas asserções

As asserções confirmam:

- integridade de planilha e parses;
- oito casos e 24 testes;
- ausência de REL/ARG1 na entrada;
- estado exato de A41 após os três candidatos;
- classificações globais esperadas;
- contraexemplos selecionados de C0 e C1;
- transferência de `para` nos quatro S009 por C2;
- ausência de transferência nos quatro controles por C2;
- cobertura inferior às 15 extrações baseline.

### Propriedades não testadas pelas asserções

- reconstrução automática dos spans GOLD;
- descoberta automática do núcleo de REL, de `p`, de `n` ou do span do argumento;
- comportamento do ramo `INDETERMINATE` com um exemplo efetivo;
- preservação das 11 extrações baseline não modeladas;
- equivalência entre o matching procedural do v3 e os métodos Java;
- proveniência do mecanismo em A42–A44 e nos controles;
- cálculo automático da distância de edição entre regras;
- generalização para outro par verbo–preposição;
- existência de E+ E4 verdadeiros.

## 6. Limitações, ameaças e divergências identificadas

### Cobertura real

- Oito extrações foram testadas, provenientes de quatro sentenças.
- Quatro E− são variantes da mesma sentença S009; não constituem quatro contextos independentes.
- Quatro controles foram modelados, provenientes de S003, S005 e S010.
- Onze dos 15 outputs baseline das três sentenças de controle não foram modelados.
- Não há E+ específico de E4, isto é, caso com `Rege(v,p)` verdadeiro e preposição já correta em REL.
- Não há caso `INDETERMINATE` executado, embora o estado exista no vocabulário e no protocolo.

### Divergências entre protocolo, implementação e relatório

1. **Reutilização da infraestrutura do v2:** o v3 reutiliza o esquema conceitual de camadas e grafos, mas não reutiliza diretamente `RegraGraphRewriting`, `MatchRegra`, `diff_regras` ou as funções de aplicação do v2. C0/C1/C2 são objetos descritivos e branches procedurais. A expressão “reutilização da infraestrutura” deve ser entendida como reutilização conceitual, não de código.
2. **Revisão de objetos-regra:** o protocolo apresenta operadores sobre uma regra. O notebook não transforma programaticamente um objeto `R_impl`; ele implementa diretamente três comportamentos em `match_target` e `apply_construction`. Portanto, os resultados validam implementações procedurais dos candidatos, não um mecanismo geral de edição de regras.
3. **Intervalo:** o protocolo formaliza `I\{p}`. No código, `I` apenas precisa ser não vazio; ARG1 resulta do span baseline completo menos `p`. A equivalência ocorre nas instâncias codificadas, mas não foi demonstrada como propriedade geral.
4. **Registro detalhado por teste:** `RESULTS` contém checks, estados, diffs e hashes enquanto o notebook é executado, porém os outputs persistidos exibem somente a matriz resumida e o registro final. A reprodução recupera os detalhes, mas nem todos foram serializados como output visível.
5. **Afirmação de ausência de desvio científico no relatório:** precisa ser qualificada pelos itens anteriores. Eles não invalidam a matriz obtida, mas reduzem a interpretação de “revisão de regra” para uma simulação procedural de efeitos sobre fronteiras fornecidas.
6. **Minimalidade:** a métrica é pré-atribuída aos candidatos; não é calculada por diff entre `R_impl` e regras revisadas materializadas. A comparação de complexidade é coerente com a convenção do protocolo, mas não constitui demonstração automática de revisão mínima.

Nenhuma dessas divergências altera retrospectivamente os resultados C0/C1/C2. Elas delimitam o que esses resultados significam.

## 7. Conclusões sustentadas

1. **Correção formal no modelo:** C0, C1 e C2 transferem `para` para REL nas quatro representações S009 e produzem a fronteira E4 esperada.
2. **Contraexemplos formais:** C0 sobreaplica em S005 e S010; C1 sobreaplica no locativo de S010. Logo, dentro do conjunto modelado, as respectivas condições são insuficientes.
3. **Preservação condicional:** C2 preserva os quatro controles quando recebe `FALSE_PROVISIONAL` e corrige S009 quando recebe `TRUE_PROVISIONAL`.
4. **Construção, não correção pós-hoc:** os resultados são montados a partir de grafos sem REL/ARG1; `R_gold_correcao_E4` não é aplicada.
5. **Escopo fechado:** C2 é o único candidato que satisfaz as oito representações codificadas, sob as anotações fornecidas.

A formulação cientificamente segura é:

> No modelo v3, dadas fronteiras baseline conhecidas e uma classificação manual de regência, C2 realiza corretamente a transferência de E4 em S009 e preserva os quatro controles representados.

## 8. Conclusões que ainda não podem ser afirmadas

Não se pode afirmar que:

- C2 infere ou reconhece `Rege(v,p)`;
- C2 é superior para sentenças não observadas;
- existe revisão generalizada de `R_impl`;
- os oito testes representam oito contextos independentes;
- os controles compartilham o mecanismo interno de A41;
- os 15 outputs baseline foram preservados;
- casos indeterminados seguem corretamente o ramo conservador em execução efetiva;
- os operadores são edições automaticamente aplicadas a uma regra formal materializada;
- a complexidade registrada prova minimalidade global;
- o comportamento foi implementado ou validado no DptOIE Java;
- uma futura implementação preservará E+ E4, pois nenhum E+ desse tipo foi testado.

## 9. Recomendações para o próximo experimento

1. **Separar derivação e avaliação:** usar S009 apenas para derivar candidatos e reservar sentenças independentes como conjunto de teste não usado nas classificações ou na escolha das regras.
2. **Adicionar cobertura crítica:** incluir E− com outros verbos/preposições, E+ E4 verdadeiros, controles estruturalmente semelhantes e pelo menos um caso genuinamente `INDETERMINATE`.
3. **Materializar as regras:** representar C0/C1/C2 como instâncias completas de `RegraGraphRewriting` e aplicar operadores de edição sobre uma cópia explícita de `R_impl`, calculando guardas, efeitos e distância de edição automaticamente.
4. **Reduzir fronteiras fornecidas:** alinhar spans a partir da planilha e do parse por procedimento auditável; testar separadamente descoberta do núcleo, formação do argumento e transferência da preposição.
5. **Testar o intervalo real:** fazer o efeito operar sobre `I(p,n)` produzido pelo matching e verificar todos os tokens de `I\{p}`, em vez de retirar `p` do ARG1 completo conhecido.
6. **Eliminar o oráculo do GOLD:** propor e avaliar uma fonte operacional de regência independente do GOLD; manter GOLD somente para avaliação.
7. **Completar não regressão:** representar ou executar os 11 outputs baseline restantes antes de declarar preservação das três sentenças de controle.
8. **Preservar os níveis de evidência:** continuar separando resultados formais do Graph Rewriting, evidência empírica do DptOIE e hipóteses linguísticas.

Somente após esses passos será metodologicamente adequado avaliar uma alteração no Java. O próximo experimento deve primeiro testar uma revisão formal materializada e uma condição operacional de regência em dados independentes.
