# Arquivos por etapa metodológica

Este índice indica onde estão os artefatos correspondentes às seis etapas da metodologia. Os caminhos são relativos à raiz deste repositório.

| Etapa metodológica | Evidências disponibilizadas | Caminhos principais |
|---|---|---|
| **1. Identificação das divergências** | Planilhas de extrações, classificação dos exemplos e análise das regras associadas às divergências. | `research/experimento/experimento fase 1 - quali.xlsx`; `research/experimento/semana5_experimento_OIEC_PT_GOLD (3)(1).xlsx`; `research/catalogo/catalogo de regras(8).xlsx`; `docs/contexto_pesquisa_e4.md` |
| **2. Formalização em LPO** | Formalização das especificações linguísticas e contextualização da regra E4. | `research/formalizacao/Resultados Formalismo Lógico - PO(1).pdf`; `docs/contexto_pesquisa_e4.md` |
| **3. Investigação operacional** | Reprodução do caso, análise estática, documentação da instrumentação, validação de não interferência, proveniência e registros de execução. | `docs/reproducao_s009_e4.md`; `docs/analise_estatica_e4.md`; `docs/validacao_instrumentacao_trace_off_e4.md`; `docs/proveniencia_e4_s009.md`; `logs/s009/reproducao_instrumentada_trace_on/e4trace.txt` |
| **4. Graph Rewriting** | Representações do grafo-base e das regras observada, esperada e corretiva. | `docs/comparacao_graph_rewriting_e4_s009.md`; `research/graph_rewriting/experimento_v2_e4_impl_gold.ipynb` |
| **5. DIFF estrutural** | Documentação e resultados da comparação estrutural entre a regra observada e a regra esperada. | `docs/comparacao_graph_rewriting_e4_s009.md`; `research/graph_rewriting/experimento_v2_e4_impl_gold.ipynb` |
| **6. Revisão de Teorias** | Protocolos, operadores explícitos, regras candidatas, decisões de implementação, resultados e matrizes de rastreabilidade. | `docs/protocolo_theory_revision_v4_e4.md`; `docs/decisoes_implementacao_v4_e4.md`; `research/graph_rewriting/experimento_v4_e4_theory_revision.ipynb`; `docs/resultados_theory_revision_v4_e4.md`; `research/experimento/rastreabilidade_theory_revision_v4_e4.xlsx`; `research/experimento/rastreabilidade_simplificada_theory_revision_v4_e4.xlsx` |

## Integridade e reprodutibilidade

Os arquivos transversais às seis etapas estão na raiz do repositório:

- `manifests/SHA256SUMS.txt`: hashes SHA-256 dos artefatos;
- `REPRODUCIBILITY.md`: ambiente, dependências e limites de reprodução;
- `CITATION.cff`: metadados para citação;
- `NOTICE.md` e `LICENSE-NOTICE.md`: proveniência e condições de redistribuição.

Os relatórios distinguem fato observado, decisão de modelagem, hipótese e informação não determinada. Essa distinção deve ser preservada na interpretação e na citação dos resultados.
