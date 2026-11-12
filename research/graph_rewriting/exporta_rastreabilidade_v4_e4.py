#!/usr/bin/env python3
"""Exporta a matriz de rastreabilidade da Theory Revision v4 de E4.

O exportador trata o notebook v4 e a planilha OIEC-PT-GOLD como fontes
congeladas. O notebook é executado somente em memória; uma célula transitória
serializa os objetos formais e os resultados sem alterar o arquivo .ipynb.

Nenhum extrator, JAR ou código Java é executado por este programa.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import nbformat
from nbclient import NotebookClient
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


NOTEBOOK_SHA256 = "bb7506602745d061ae113969c964f6c5fbfc6df85ca06a87a14eaaf125672cca"
SOURCE_WORKBOOK_SHA256 = "a00c037da53f5de90307d8918b8547d226888297eb7243d0272c68d5f337616c"

COMMITS = {
    "protocolo_v4": "4183b5ecddee1f8e42d82f5d21de2381513384b6",
    "decisoes_v4": "54a65af0e2023eb23683f1e020123ac692401c98",
    "implementacao_resultados_v4": "7f3fef2c3e5136bef8758c4c933adf56083bfd05",
}

R_IMPL_HASH = "d4c332a43dd349ee6b7691880933432e455bbe3aa41af35814335e0ceaf4e8c4"
CANDIDATE_HASHES = {
    "C0": "91194d427726f98be1b377d925a5790fc01fbb5596440b90d09c5341b809c427",
    "C1": "af966fec75bce1b08524e3e2d40af12258749ed255e0ad03e28753b9a5395458",
    "C2": "d537c4c7088479d413ddde4cd131bdf012bb137c29bfeecdf1ffed02a01a23fe",
}

EXPECTED_GLOBAL = {
    "C0": {"passes": 5, "falhas": 3, "custo": 5, "resultado": "FAIL_OVERAPPLICATION"},
    "C1": {"passes": 6, "falhas": 2, "custo": 8, "resultado": "FAIL_OVERAPPLICATION"},
    "C2": {"passes": 8, "falhas": 0, "custo": 7, "resultado": "PASS_EXPLORATORY"},
}

EXPECTED_FAILURES = {
    "C0": {"S005-A28", "S010-A51", "S010-A52"},
    "C1": {"S010-A51", "S010-A52"},
    "C2": set(),
}

EXPECTED_SHEETS = [
    "00_Resumo",
    "01_Candidatas",
    "02_Historico_Operadores",
    "03_Resultados_por_Caso",
    "04_Decisoes_por_Alvo",
    "05_Cobertura_Pendente",
    "06_Fixtures",
    "07_Metadados_Dicionario",
    "08_Anotacoes",
]

PENDING_CASES = [
    "S003-A16",
    "S003-A17",
    "S003-A18",
    "S003-A19",
    "S005-A26",
    "S005-A27",
    "S005-A29",
    "S010-A50",
    "S010-A53",
    "S010-A54",
    "S010-A55",
]

PENDING_GUIDANCE = {
    "S003-A16": (
        "controle de não aplicação potencial (expressão temporal/nominal)",
        "validar a análise linguística de 'para 2016', o alvo p/n e as fronteiras formais",
    ),
    "S003-A17": (
        "controle de não aplicação potencial (expressão temporal/nominal)",
        "validar a análise linguística de 'para 2016', o alvo p/n e as fronteiras formais",
    ),
    "S003-A18": (
        "controle geral de não regressão (E1; sem alvo E4 direto já modelado)",
        "modelar componentes e verificar se existe alvo preposicional relevante",
    ),
    "S003-A19": (
        "controle de interação com complemento adjetival e erros E9/E3",
        "anotar regência/complementação independente, alvo e eventual conjunto U",
    ),
    "S005-A26": (
        "hard negative potencial (marcador discursivo)",
        "validar a interpretação de 'en o entanto' e modelar fronteiras",
    ),
    "S005-A27": (
        "controle geral de não regressão sem preposição-alvo evidente",
        "modelar ARG0/REL/ARG1 e confirmar ausência de alvo E4",
    ),
    "S005-A29": (
        "controle geral com possível expressão multivocabular 'por o menos'",
        "validar a expressão e a interação com E9 antes de usá-la para E4",
    ),
    "S010-A50": (
        "controle geral de não regressão sem preposição-alvo evidente",
        "modelar ARG0/REL/ARG1 e confirmar ausência de alvo E4",
    ),
    "S010-A53": (
        "controle de estresse com locativo, finalidade e erros E3/S3",
        "modelar alvos, conjunto U e fronteiras esperadas",
    ),
    "S010-A54": (
        "hard negative potencial com oração de finalidade 'para encontrar'",
        "obter classificação independente de regência e modelar o predicado encaixado",
    ),
    "S010-A55": (
        "controle geral de não regressão com erros E3/S3",
        "modelar componentes, alvos e efeitos residuais não relacionados a E4",
    ),
}

CANDIDATE_DESCRIPTION = {
    "C0": {
        "hipotese": "O diff estrutural, sem guarda adicional, é suficiente para transferir p de ARG1 para REL.",
        "conclusao": "Corrige as quatro variantes de S009, mas sobreaplica em três controles.",
        "limitacao": "Não distingue contextos em que a preposição deve permanecer no argumento.",
    },
    "C1": {
        "hipotese": "As guardas sintáticas case(p,n) e nmod(n,v) são suficientes para condicionar a transferência.",
        "conclusao": "Corrige S009 e preserva dois controles, mas sobreaplica nos dois outputs de S010.",
        "limitacao": "As dependências observadas não distinguem, sozinhas, os contextos locativos testados.",
    },
    "C2": {
        "hipotese": "A transferência deve ser condicionada por Rege(v,p), com fallback conservador.",
        "conclusao": "Satisfaz condicionalmente os oito outputs modelados no conjunto piloto.",
        "limitacao": "Rege(v,p) foi fornecido experimentalmente e depende parcialmente do GOLD; não há reconhecedor operacional independente.",
    },
}

OPERATOR_EFFECT = {
    "ADD_GUARD": "restringe o matching com uma condição sintática explícita",
    "ADD_GUARD_REGE": "adiciona a condição linguística provisória Rege(v,p)",
    "RESTRICT_INTERVAL": "parametriza a construção pelo intervalo ordenado I(p,n)",
    "CHANGE_COMPONENT": "muda o componente OpenIE de destino de p: ARG1 para REL",
    "SPLIT_RULE": "cria branches exclusivos com fallback que preserva a regra-base",
}

OPERATOR_EVIDENCE = {
    "ADD_GUARD": "parse de dependências e hipótese sintática avaliada no v4",
    "ADD_GUARD_REGE": "formalização linguística de E4; status experimental documentado",
    "RESTRICT_INTERVAL": "proveniência de S009: operação de intervalo observada no trace",
    "CHANGE_COMPONENT": "diff estrutural R_impl × R_gold: ARG1(e,p) versus REL(e,p)",
    "SPLIT_RULE": "necessidade de preservar controles por aplicação condicional e fallback",
}

FILL_HEADER = PatternFill("solid", fgColor="17365D")
FILL_SUBHEADER = PatternFill("solid", fgColor="D9EAF7")
FILL_PASS = PatternFill("solid", fgColor="E2F0D9")
FILL_FAIL = PatternFill("solid", fgColor="FCE4D6")
FILL_PENDING = PatternFill("solid", fgColor="FFF2CC")
FILL_FIXTURE = PatternFill("solid", fgColor="E7E6E6")
FILL_NOTE = PatternFill("solid", fgColor="F4F1DE")
FONT_HEADER = Font(color="FFFFFF", bold=True)
FONT_BOLD = Font(bold=True, color="17365D")
THIN_BORDER = Border(
    left=Side(style="thin", color="D9E1F2"),
    right=Side(style="thin", color="D9E1F2"),
    top=Side(style="thin", color="D9E1F2"),
    bottom=Side(style="thin", color="D9E1F2"),
)


class ExportError(RuntimeError):
    """Falha metodológica que deve impedir a produção da planilha."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def find_repo_root(script_path: Path) -> Path:
    for candidate in [Path.cwd().resolve(), *script_path.resolve().parents]:
        if (candidate / ".git").exists():
            return candidate
    raise ExportError("Não foi possível localizar a raiz do repositório Git.")


def verify_frozen_inputs(notebook: Path, source_workbook: Path) -> dict[str, str]:
    if not notebook.is_file():
        raise ExportError(f"Notebook não encontrado: {notebook}")
    if not source_workbook.is_file():
        raise ExportError(f"Planilha-fonte não encontrada: {source_workbook}")

    actual_notebook = sha256_file(notebook)
    actual_source = sha256_file(source_workbook)
    if actual_notebook.lower() != NOTEBOOK_SHA256:
        raise ExportError(
            "Hash do notebook v4 divergiu: "
            f"esperado={NOTEBOOK_SHA256}, observado={actual_notebook}."
        )
    if actual_source.lower() != SOURCE_WORKBOOK_SHA256:
        raise ExportError(
            "Hash da planilha OIEC-PT-GOLD divergiu: "
            f"esperado={SOURCE_WORKBOOK_SHA256}, observado={actual_source}."
        )
    return {"notebook": actual_notebook, "planilha_fonte": actual_source}


def transient_export_cell() -> str:
    """Célula acrescentada somente à cópia em memória do notebook."""

    return r'''
_traceability_edit_chains = {}
for _candidate_name, _candidate_rule in CANDIDATES.items():
    _specialized = specialized_rule(_candidate_rule)
    _traceability_edit_chains[_candidate_name] = {
        "specialized_hash": object_hash(_specialized),
        "specialized_history": canonical(_specialized.edit_history),
        "composite_history": canonical(
            _candidate_rule.edit_history
            if isinstance(_candidate_rule, ChoiceRule)
            else ()
        ),
    }

_traceability_fixtures = {
    "indeterminate": {
        "case": canonical(indeterminate_case),
        "result": canonical(indeterminate_state),
        "targets": canonical(indeterminate_records),
    },
    "u_nonempty": {
        "case": canonical(u_case),
        "result": canonical(u_state),
        "targets": canonical(u_records),
    },
    "ordered_interval": {
        "graph": canonical([
            {"id": node_id, **attributes}
            for node_id, attributes in fixture_graph.nodes(data=True)
        ]),
        "nodes": canonical(tuple(
            node_id
            for node_id, _ in sorted(
                fixture_graph.nodes(data=True),
                key=lambda item: item[1]["ordem"],
            )
        )),
        "interval": canonical(interval_by_order(fixture_graph, 10, 30)),
    },
}

_traceability_payload = {
    "cases": canonical(CASES),
    "oracles": canonical(ORACLES),
    "parses": canonical(PARSES),
    "r_impl": canonical(R_IMPL),
    "r_impl_hash": object_hash(R_IMPL),
    "candidates": {name: canonical(rule) for name, rule in CANDIDATES.items()},
    "candidate_hashes": {name: object_hash(rule) for name, rule in CANDIDATES.items()},
    "diffs": canonical(DIFFS),
    "edit_summaries": canonical(EDIT_SUMMARIES),
    "edit_chains": _traceability_edit_chains,
    "results": canonical(RESULTS),
    "assertions": canonical(ASSERTIONS),
    "final_record": canonical(FINAL_RECORD),
    "fixtures": _traceability_fixtures,
}
print("__TRACEABILITY_EXPORT__=" + json.dumps(_traceability_payload, ensure_ascii=False, sort_keys=True))
'''


def execute_notebook_in_memory(notebook_path: Path, repo: Path) -> dict[str, Any]:
    original = nbformat.read(notebook_path, as_version=4)
    in_memory = copy.deepcopy(original)
    in_memory.cells.append(nbformat.v4.new_code_cell(transient_export_cell()))

    client = NotebookClient(
        in_memory,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(repo)}},
        allow_errors=False,
    )
    executed = client.execute()
    outputs = executed.cells[-1].get("outputs", [])
    marker = "__TRACEABILITY_EXPORT__="
    serialized: str | None = None
    for output in outputs:
        text = output.get("text", "") if isinstance(output, dict) else ""
        if isinstance(text, list):
            text = "".join(text)
        for line in str(text).splitlines():
            if line.startswith(marker):
                serialized = line[len(marker) :]
    if serialized is None:
        raise ExportError("A célula transitória não produziu o payload de rastreabilidade.")
    try:
        return json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise ExportError("O payload transitório não é JSON válido.") from exc


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ExportError(message)


def is_pass(classification: str) -> bool:
    return str(classification).startswith("PASS")


def validate_payload(payload: Mapping[str, Any]) -> None:
    ensure(payload.get("r_impl_hash") == R_IMPL_HASH, "Hash de R_impl inesperado.")
    ensure(payload.get("candidate_hashes") == CANDIDATE_HASHES, "Hashes das candidatas divergiram.")

    cases = payload.get("cases", [])
    results = payload.get("results", [])
    assertions = payload.get("assertions", [])
    ensure(len(cases) == 8, f"Esperados 8 casos, observados {len(cases)}.")
    ensure(len(results) == 24, f"Esperadas 24 aplicações, observadas {len(results)}.")
    ensure(len(assertions) == 31, f"Esperadas 31 asserções, observadas {len(assertions)}.")
    required_fixture_assertions = {
        "DUPLICATE_GUARD_REJECTED",
        "OVERLAPPING_BRANCHES_REJECTED",
        "INTERVAL_PRESERVES_PUNCTUATION",
        "INTERVAL_SUPPORTS_NONCONTIGUOUS_IDS",
        "INDETERMINATE_FALLBACK",
        "INDETERMINATE_BRANCH_EXPLICIT",
        "COMPOSITE_ARG1_U_PRESERVED",
    }
    ensure(
        required_fixture_assertions.issubset(set(assertions)),
        "Asserções obrigatórias das fixtures não estão todas presentes.",
    )
    ensure(set(payload.get("candidates", {})) == {"C0", "C1", "C2"}, "Conjunto de candidatas divergente.")

    by_candidate: dict[str, list[Mapping[str, Any]]] = {name: [] for name in CANDIDATE_HASHES}
    for result in results:
        by_candidate[result["candidate"]].append(result)
    for candidate, expected in EXPECTED_GLOBAL.items():
        rows = by_candidate[candidate]
        passes = sum(is_pass(row["classification"]) for row in rows)
        failures = len(rows) - passes
        observed_failures = {row["case_id"] for row in rows if not is_pass(row["classification"])}
        ensure(passes == expected["passes"], f"{candidate}: contagem de passes divergente.")
        ensure(failures == expected["falhas"], f"{candidate}: contagem de falhas divergente.")
        ensure(observed_failures == EXPECTED_FAILURES[candidate], f"{candidate}: casos de falha divergiram.")

    summaries = payload.get("edit_summaries", {})
    for candidate, expected in EXPECTED_GLOBAL.items():
        summary = summaries[candidate]
        ensure(int(summary["unit_cost"]) == expected["custo"], f"{candidate}: custo estrutural divergente.")

    global_results = payload.get("final_record", {}).get("global_results", {})
    for candidate, expected in EXPECTED_GLOBAL.items():
        ensure(
            global_results.get(candidate) == expected["resultado"],
            f"{candidate}: resultado global publicado divergiu.",
        )

    c2_rows = by_candidate["C2"]
    for row in c2_rows:
        ensure(is_pass(row["classification"]), f"C2 deixou de passar em {row['case_id']}.")
        if str(row["kind"]).startswith("E_MINUS"):
            ensure(row["result"] == row["expected_e4"], f"C2 não corrigiu E4 em {row['case_id']}.")
        else:
            ensure(row["result"] == row["baseline"], f"C2 não preservou o controle {row['case_id']}.")

    for case_id in ("S009-A43", "S009-A44"):
        rows = [row for row in results if row["case_id"] == case_id]
        ensure(all(is_pass(row["classification"]) for row in rows), f"{case_id}: E4 não foi corrigida em todas as candidatas.")
        ensure(all(not row["gold_exact_by_boundary"] for row in rows), f"{case_id}: igualdade integral com GOLD tornou-se verdadeira.")


def normalize_header(value: Any) -> str:
    return str(value or "").strip()


def load_analysis_rows(source_workbook: Path) -> dict[str, dict[str, Any]]:
    workbook = load_workbook(source_workbook, read_only=True, data_only=True)
    if "analise" not in workbook.sheetnames:
        workbook.close()
        raise ExportError("A aba 'analise' não existe na planilha-fonte.")
    sheet = workbook["analise"]
    rows = sheet.iter_rows(values_only=True)
    headers = [normalize_header(value) for value in next(rows)]
    data: dict[str, dict[str, Any]] = {}
    for excel_row, values in enumerate(rows, start=2):
        record = dict(zip(headers, values))
        sentence_id = normalize_header(record.get("id_sentenca"))
        if sentence_id:
            data[f"{sentence_id}-A{excel_row}"] = record
    workbook.close()
    return data


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def display_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)


def clean_excel_text(value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool, datetime)):
        return value
    if isinstance(value, (dict, list, tuple)):
        value = display_json(value)
    text = ILLEGAL_CHARACTERS_RE.sub("", str(value))
    if len(text) > 32767:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        text = text[:32500] + f"\n[TRUNCADO_POR_LIMITE_XLSX sha256={digest}]"
    return text


def index_by(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, Mapping[str, Any]]:
    return {str(item[key]): item for item in items}


def parse_tokens(payload: Mapping[str, Any], sentence_id: str) -> dict[int, Mapping[str, Any]]:
    raw = payload["parses"][sentence_id]
    return {int(token_id): token for token_id, token in raw.items()}


def token_form(tokens: Mapping[int, Mapping[str, Any]], token_id: int | str) -> str:
    return str(tokens[int(token_id)]["form"])


def ids_to_forms(tokens: Mapping[int, Mapping[str, Any]], ids: Iterable[int]) -> list[str]:
    return [token_form(tokens, token_id) for token_id in ids]


def component_text(tokens: Mapping[int, Mapping[str, Any]], ids: Iterable[int]) -> str:
    return " ".join(ids_to_forms(tokens, ids))


def state_component(state: Mapping[str, Any], component: str) -> Any:
    """Lê componentes do estado usando os nomes formais ARG0/REL/ARG1."""

    for key in (component.upper(), component.lower()):
        if key in state:
            return state[key]
    raise ExportError(f"Componente ausente no estado serializado: {component}")


def state_text_from_ids(tokens: Mapping[int, Mapping[str, Any]], state: Mapping[str, Any]) -> str:
    return "(" + ", ".join(
        [
            component_text(tokens, state_component(state, "ARG0")),
            component_text(tokens, state_component(state, "REL")),
            component_text(tokens, state_component(state, "ARG1")),
        ]
    ) + ")"


def candidate_specialized(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    if candidate.get("__type__") == "AtomicRule":
        return candidate
    branch_name = candidate["comparison_branch"]
    for branch in candidate["branches"]:
        if branch["name"] == branch_name:
            return branch["rule"]
    raise ExportError(f"Branch especializada não encontrada: {branch_name}")


def candidate_branches(candidate: Mapping[str, Any]) -> str:
    if candidate.get("__type__") == "AtomicRule":
        return "regra atômica; sem fallback"
    return "; ".join(
        f"{branch['name']}[papel={branch['role']}, condição={canonical_json(branch['condition'])}]"
        for branch in candidate["branches"]
    )


def moved_target(target: Mapping[str, Any]) -> bool:
    return target.get("selected_rule") != "R_impl_observado_E4_S009_A41"


def component_diff(before: Mapping[str, Any], after: Mapping[str, Any]) -> str:
    chunks: list[str] = []
    for component in ("ARG0", "REL", "ARG1"):
        old = list(state_component(before, component))
        new = list(state_component(after, component))
        if old != new:
            chunks.append(f"{component}: {old} → {new}")
    return "; ".join(chunks) if chunks else "SEM_ALTERAÇÃO"


def residual_errors(case: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    notes = str(case.get("notes", ""))
    if case["case_id"] in {"S009-A43", "S009-A44"}:
        return "E3/S3 residuais: E4 corrigida nas fronteiras avaliadas, sem igualdade integral com o GOLD."
    if not result["gold_exact_by_boundary"]:
        return notes or "Há divergência residual entre o estado avaliado e o GOLD."
    return "NENHUM_NA_COMPARAÇÃO_DE_FRONTEIRAS"


def provenance_status(case_id: str) -> str:
    if case_id == "S009-A41":
        return "CONFIRMADA_POR_TRACE"
    if case_id.startswith("S009-"):
        return "VARIANTE_DA_MESMA_SENTENÇA; PROVENIÊNCIA_ESPECÍFICA_NÃO_CONFIRMADA"
    return "DESCONHECIDA_PARA_O_MECANISMO_IMPLEMENTADO"


def result_justification(result: Mapping[str, Any], case: Mapping[str, Any]) -> str:
    classification = result["classification"]
    moved = [target for target in result["targets"] if moved_target(target)]
    moved_text = ", ".join(f"p={target['p']} via {target['branch']}" for target in moved) or "nenhum p"
    if classification == "FAIL_OVERAPPLICATION":
        return f"A candidata transferiu indevidamente {moved_text}; o controle deveria permanecer no baseline."
    if str(case["kind"]).startswith("E_MINUS"):
        return f"A fronteira E4 esperada foi produzida; tokens transferidos: {moved_text}."
    return f"O controle foi preservado; tokens transferidos: {moved_text}."


def expression_trace_text(target: Mapping[str, Any]) -> str:
    return display_json(target.get("expression_trace", []))


def append_table(sheet, headers: Sequence[str], rows: Iterable[Sequence[Any]], start_row: int = 1) -> int:
    for column, header in enumerate(headers, start=1):
        cell = sheet.cell(row=start_row, column=column, value=clean_excel_text(header))
        cell.fill = FILL_HEADER
        cell.font = FONT_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    current = start_row + 1
    for row in rows:
        for column, value in enumerate(row, start=1):
            cell = sheet.cell(row=current, column=column, value=clean_excel_text(value))
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = THIN_BORDER
        current += 1
    if current > start_row + 1:
        sheet.auto_filter.ref = f"A{start_row}:{get_column_letter(len(headers))}{current - 1}"
    sheet.freeze_panes = f"A{start_row + 1}"
    return current


def style_sheet(sheet, widths: Mapping[str, float] | None = None) -> None:
    sheet.sheet_view.showGridLines = False
    sheet.auto_filter.ref = sheet.auto_filter.ref
    sheet.freeze_panes = sheet.freeze_panes or "A2"
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value is not None:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
    if widths:
        for column, width in widths.items():
            sheet.column_dimensions[column].width = width
    else:
        for column_cells in sheet.columns:
            letter = get_column_letter(column_cells[0].column)
            observed = max((len(str(cell.value or "")) for cell in column_cells), default=10)
            sheet.column_dimensions[letter].width = min(max(observed + 2, 12), 55)
    sheet.row_dimensions[1].height = 30


def color_rows_by_value(sheet, header_row: int, column_name: str, mapping: Mapping[str, PatternFill]) -> None:
    headers = {cell.value: cell.column for cell in sheet[header_row]}
    column = headers.get(column_name)
    if not column:
        return
    for row in range(header_row + 1, sheet.max_row + 1):
        value = str(sheet.cell(row=row, column=column).value or "")
        fill = next((style for key, style in mapping.items() if key in value), None)
        if fill:
            for cell in sheet[row]:
                cell.fill = fill


def make_summary_sheet(workbook: Workbook, payload: Mapping[str, Any]) -> None:
    sheet = workbook.create_sheet("00_Resumo")
    sheet["A1"] = "Matriz de rastreabilidade — Theory Revision v4 / E4"
    sheet["A1"].font = Font(bold=True, size=16, color="17365D")
    sheet.merge_cells("A1:F1")
    sheet["A2"] = (
        "Artefato de derivação e avaliação. C0, C1 e C2 são hipóteses exploratórias; "
        "não constituem uma busca completa no espaço de revisões."
    )
    sheet.merge_cells("A2:F2")
    sheet["A2"].fill = FILL_NOTE
    sheet["A2"].alignment = Alignment(wrap_text=True)

    rows = []
    for candidate in ("C0", "C1", "C2"):
        expected = EXPECTED_GLOBAL[candidate]
        rows.append(
            [
                candidate,
                expected["passes"],
                expected["falhas"],
                expected["custo"],
                expected["resultado"],
                CANDIDATE_DESCRIPTION[candidate]["conclusao"],
            ]
        )
    append_table(
        sheet,
        ["Candidata", "Passes", "Falhas", "Custo", "Resultado global", "Síntese"],
        rows,
        start_row=4,
    )
    color_rows_by_value(
        sheet,
        4,
        "Resultado global",
        {"PASS_EXPLORATORY": FILL_PASS, "FAIL": FILL_FAIL},
    )

    coverage_start = 10
    append_table(
        sheet,
        ["Indicador de cobertura", "Quantidade", "Interpretação"],
        [
            ["Outputs E− modelados", 4, "Quatro extrações de uma única sentença independente: S009."],
            ["Controles modelados", 4, "Quatro outputs provenientes de três sentenças: S003, S005 e S010."],
            ["Outputs reais modelados", 8, "Cada um avaliado com C0, C1 e C2: 24 aplicações."],
            ["Outputs pendentes", 11, "Não foram contabilizados como testes aprovados."],
            ["Fixtures sintéticas", 6, "Testam propriedades formais; não são evidência empírica."],
        ],
        start_row=coverage_start,
    )
    note_row = 18
    notes = [
        "PASS_EXPLORATORY não significa igualdade integral com o GOLD.",
        "Em A43 e A44, E4 foi corrigida, mas permanecem divergências residuais E3/S3.",
        "C2 passa condicionalmente porque Rege(v,p) é fornecido como entrada experimental.",
        "Os onze outputs pendentes permanecem fora das contagens de sucesso/falha.",
    ]
    for offset, note in enumerate(notes):
        sheet.cell(note_row + offset, 1, "RESSALVA" if offset == 0 else "")
        sheet.cell(note_row + offset, 2, note)
        sheet.merge_cells(start_row=note_row + offset, start_column=2, end_row=note_row + offset, end_column=6)
        for cell in sheet[note_row + offset]:
            cell.fill = FILL_NOTE
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    style_sheet(sheet, {"A": 28, "B": 16, "C": 16, "D": 12, "E": 25, "F": 72})


def make_candidates_sheet(workbook: Workbook, payload: Mapping[str, Any]) -> None:
    headers = [
        "candidata",
        "hipotese_cientifica",
        "hash_R_impl",
        "hash_candidata",
        "regra_pai",
        "tipo_regra",
        "branches",
        "guardas_regra_especializada",
        "efeitos_regra_especializada",
        "restricoes",
        "fallback",
        "sequencia_operadores",
        "vetor_diff",
        "custo",
        "resultado_global",
        "conclusao_sustentada",
        "limitacao",
    ]
    rows = []
    for name in ("C0", "C1", "C2"):
        candidate = payload["candidates"][name]
        specialized = candidate_specialized(candidate)
        chain = payload["edit_chains"][name]
        operations = [item["operator"] for item in chain["specialized_history"]]
        operations.extend(item["operator"] for item in chain["composite_history"])
        summary = payload["edit_summaries"][name]
        fallback = "NÃO"
        if candidate.get("__type__") == "ChoiceRule":
            fallback = "; ".join(
                branch["name"]
                for branch in candidate["branches"]
                if str(branch.get("role", "")).startswith("FALLBACK")
            )
        rows.append(
            [
                name,
                CANDIDATE_DESCRIPTION[name]["hipotese"],
                payload["r_impl_hash"],
                payload["candidate_hashes"][name],
                "R_impl_observado_E4_S009_A41",
                candidate.get("__type__"),
                candidate_branches(candidate),
                specialized.get("guards"),
                specialized.get("effects"),
                specialized.get("restrictions"),
                fallback,
                " → ".join(operations),
                summary.get("vector"),
                summary.get("unit_cost"),
                EXPECTED_GLOBAL[name]["resultado"],
                CANDIDATE_DESCRIPTION[name]["conclusao"],
                CANDIDATE_DESCRIPTION[name]["limitacao"],
            ]
        )
    sheet = workbook.create_sheet("01_Candidatas")
    append_table(sheet, headers, rows)
    color_rows_by_value(sheet, 1, "resultado_global", {"PASS": FILL_PASS, "FAIL": FILL_FAIL})
    style_sheet(sheet)


def operator_history_rows(payload: Mapping[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for candidate_name in ("C0", "C1", "C2"):
        chain = payload["edit_chains"][candidate_name]
        specialized_history = chain["specialized_history"]
        composite_history = chain["composite_history"]
        combined = [("especializacao", record) for record in specialized_history]
        combined.extend(("composicao", record) for record in composite_history)
        for index, (phase, record) in enumerate(combined, start=1):
            if phase == "especializacao":
                position = specialized_history.index(record)
                if position + 1 < len(specialized_history):
                    hash_after = specialized_history[position + 1]["parent_hash"]
                else:
                    hash_after = chain["specialized_hash"]
            else:
                hash_after = payload["candidate_hashes"][candidate_name]
            operator = record["operator"]
            rows.append(
                [
                    candidate_name,
                    index,
                    phase,
                    operator,
                    record.get("parameters"),
                    record["parent_hash"],
                    hash_after,
                    record.get("before_fragment"),
                    record.get("after_fragment"),
                    OPERATOR_EFFECT.get(operator, "edição formal registrada pelo notebook"),
                    OPERATOR_EVIDENCE.get(operator, "evidência registrada no protocolo v4"),
                    (
                        "formalização E4"
                        if operator == "ADD_GUARD_REGE"
                        else "proveniência/parse/diff e protocolo v4"
                    ),
                ]
            )
    return rows


def make_operator_history_sheet(workbook: Workbook, payload: Mapping[str, Any]) -> None:
    headers = [
        "candidata",
        "passo",
        "fase",
        "operador",
        "parametros",
        "hash_regra_antes",
        "hash_regra_depois",
        "fragmento_antes",
        "fragmento_depois",
        "efeito_cientifico",
        "evidencia_motivadora",
        "relacao_com_evidencias",
    ]
    sheet = workbook.create_sheet("02_Historico_Operadores")
    append_table(sheet, headers, operator_history_rows(payload))
    style_sheet(sheet)


def result_rows(
    payload: Mapping[str, Any], analysis_rows: Mapping[str, Mapping[str, Any]]
) -> list[list[Any]]:
    cases = index_by(payload["cases"], "case_id")
    rows: list[list[Any]] = []
    for result in sorted(payload["results"], key=lambda item: (item["candidate"], item["case_id"])):
        case = cases[result["case_id"]]
        source = analysis_rows.get(result["case_id"], {})
        tokens = parse_tokens(payload, case["sentence_id"])
        baseline = result["baseline"]
        expected = result["expected_e4"]
        produced = result["result"]
        gold = result["gold"]
        moved_targets = [target for target in result["targets"] if moved_target(target)]
        moved_ids = [int(target["p"]) for target in moved_targets]
        is_e_minus = str(case["kind"]).startswith("E_MINUS")
        corrigiu = "SIM" if is_e_minus and produced == expected else ("NÃO" if is_e_minus else "N/A")
        preserved = "SIM" if not is_e_minus and produced == baseline else ("NÃO" if not is_e_minus else "N/A")
        rows.append(
            [
                f"{result['candidate']}::{result['case_id']}",
                result["candidate"],
                result["case_id"],
                case["sentence_id"],
                case["row_id"],
                case["kind"],
                source.get("sentenca_original"),
                source.get("extrator"),
                source.get("tripla_extraida"),
                source.get("gold_de_referencia"),
                component_text(tokens, state_component(baseline, "ARG0")),
                component_text(tokens, state_component(baseline, "REL")),
                component_text(tokens, state_component(baseline, "ARG1")),
                component_text(tokens, state_component(expected, "ARG0")),
                component_text(tokens, state_component(expected, "REL")),
                component_text(tokens, state_component(expected, "ARG1")),
                component_text(tokens, state_component(produced, "ARG0")),
                component_text(tokens, state_component(produced, "REL")),
                component_text(tokens, state_component(produced, "ARG1")),
                component_text(tokens, state_component(gold, "ARG0")),
                component_text(tokens, state_component(gold, "REL")),
                component_text(tokens, state_component(gold, "ARG1")),
                moved_ids,
                ids_to_forms(tokens, moved_ids),
                component_diff(baseline, produced),
                component_diff(gold, produced),
                corrigiu,
                preserved,
                "SIM" if produced == expected else "NÃO",
                "SIM" if produced == gold else "NÃO",
                residual_errors(case, result),
                result["classification"],
                result_justification(result, case),
                provenance_status(result["case_id"]),
                result["graph_hash"],
                result["rule_hash"],
                "research/graph_rewriting/experimento_v4_e4_theory_revision.ipynb",
                "docs/resultados_theory_revision_v4_e4.md; docs/baseline_controles_e4.md",
            ]
        )
    return rows


RESULT_HEADERS = [
    "id_aplicacao",
    "candidata",
    "caso",
    "sentenca_id",
    "linha_planilha",
    "tipo_caso",
    "sentenca_integral",
    "extrator",
    "extracao_baseline_planilha",
    "GOLD_planilha",
    "ARG0_baseline",
    "REL_baseline",
    "ARG1_baseline",
    "ARG0_esperado_E4",
    "REL_esperado_E4",
    "ARG1_esperado_E4",
    "ARG0_produzido",
    "REL_produzido",
    "ARG1_produzido",
    "ARG0_GOLD",
    "REL_GOLD",
    "ARG1_GOLD",
    "tokens_transferidos_ids",
    "tokens_transferidos_forms",
    "diff_baseline",
    "diff_GOLD",
    "corrigiu_E4",
    "preservou_controle",
    "igualdade_de_fronteiras",
    "igualdade_integral_GOLD",
    "erros_residuais",
    "classificacao",
    "justificativa_factual",
    "status_proveniencia",
    "hash_grafo",
    "hash_regra",
    "referencia_notebook",
    "referencias_artefatos",
]


def make_results_sheet(
    workbook: Workbook, payload: Mapping[str, Any], analysis_rows: Mapping[str, Mapping[str, Any]]
) -> None:
    sheet = workbook.create_sheet("03_Resultados_por_Caso")
    append_table(sheet, RESULT_HEADERS, result_rows(payload, analysis_rows))
    color_rows_by_value(
        sheet,
        1,
        "classificacao",
        {"PASS": FILL_PASS, "FAIL": FILL_FAIL},
    )
    style_sheet(sheet)


def decision_rows(payload: Mapping[str, Any]) -> list[list[Any]]:
    cases = index_by(payload["cases"], "case_id")
    rows: list[list[Any]] = []
    for result in sorted(payload["results"], key=lambda item: (item["candidate"], item["case_id"])):
        case = cases[result["case_id"]]
        tokens = parse_tokens(payload, case["sentence_id"])
        for target_index, target in enumerate(result["targets"], start=1):
            p = int(target["p"])
            n = int(target["n"])
            token_p = tokens[p]
            token_n = tokens[n]
            transferred = moved_target(target)
            before_component = "ARG1"
            after_component = "REL" if transferred else "ARG1"
            rows.append(
                [
                    f"{result['candidate']}::{result['case_id']}::T{target_index}",
                    result["candidate"],
                    result["case_id"],
                    case["sentence_id"],
                    target_index,
                    p,
                    token_p["form"],
                    n,
                    token_n["form"],
                    token_p.get("head"),
                    token_p.get("deprel"),
                    token_n.get("head"),
                    token_n.get("deprel"),
                    target.get("interval"),
                    ids_to_forms(tokens, target.get("interval", [])),
                    target.get("status_rege"),
                    target.get("status_origin"),
                    target.get("justification"),
                    "SIM" if target.get("status_uses_gold") else "NÃO",
                    target.get("guard_results"),
                    target.get("branch_evaluations"),
                    target.get("branch"),
                    target.get("selected_rule"),
                    target.get("selected_rule_hash"),
                    expression_trace_text(target),
                    "TRANSFERIDO" if transferred else "PRESERVADO",
                    before_component,
                    after_component,
                    f"token {p} '{token_p['form']}'",
                    result["classification"],
                ]
            )
    return rows


DECISION_HEADERS = [
    "id_decisao",
    "candidata",
    "caso",
    "sentenca_id",
    "alvo_ordinal",
    "p_id",
    "p_form",
    "n_id",
    "n_form",
    "p_head",
    "p_deprel",
    "n_head",
    "n_deprel",
    "intervalo_ids",
    "intervalo_forms",
    "status_Rege_v_p",
    "origem_status_Rege",
    "justificativa_Rege",
    "status_usou_GOLD",
    "resultados_guardas",
    "branches_avaliados",
    "branch_selecionado",
    "regra_selecionada",
    "hash_regra_selecionada",
    "trace_expressoes",
    "acao_token_p",
    "componente_antes",
    "componente_depois",
    "token_transferido_ou_preservado",
    "classificacao_aplicacao",
]


def make_decisions_sheet(workbook: Workbook, payload: Mapping[str, Any]) -> None:
    sheet = workbook.create_sheet("04_Decisoes_por_Alvo")
    append_table(sheet, DECISION_HEADERS, decision_rows(payload))
    color_rows_by_value(
        sheet,
        1,
        "classificacao_aplicacao",
        {"PASS": FILL_PASS, "FAIL": FILL_FAIL},
    )
    style_sheet(sheet)


def make_pending_sheet(
    workbook: Workbook, analysis_rows: Mapping[str, Mapping[str, Any]]
) -> None:
    headers = [
        "caso",
        "sentenca_id",
        "linha_planilha",
        "sentenca_integral",
        "extrator",
        "extracao_DptOIE",
        "GOLD",
        "classificacao_original",
        "observacoes_originais",
        "possivel_papel_avaliacao",
        "informacao_ainda_necessaria",
        "status",
        "contabilizado_como_teste",
    ]
    rows = []
    for case_id in PENDING_CASES:
        source = analysis_rows.get(case_id)
        if source is None:
            raise ExportError(f"Caso pendente não encontrado na aba analise: {case_id}")
        role, needed = PENDING_GUIDANCE[case_id]
        sentence_id, row_id = case_id.split("-", 1)
        rows.append(
            [
                case_id,
                sentence_id,
                row_id,
                source.get("sentenca_original"),
                source.get("extrator"),
                source.get("tripla_extraida"),
                source.get("gold_de_referencia"),
                source.get("classificacao"),
                source.get("observacoes_do_erro"),
                role,
                needed,
                "NÃO_MODELADO",
                "NÃO",
            ]
        )
    sheet = workbook.create_sheet("05_Cobertura_Pendente")
    append_table(sheet, headers, rows)
    color_rows_by_value(sheet, 1, "status", {"NÃO_MODELADO": FILL_PENDING})
    style_sheet(sheet)


def fixture_rows(payload: Mapping[str, Any]) -> list[list[Any]]:
    fixtures = payload["fixtures"]
    indeterminate = fixtures["indeterminate"]
    u_nonempty = fixtures["u_nonempty"]
    ordered = fixtures["ordered_interval"]
    return [
        [
            "FIX-INDETERMINATE",
            "INDETERMINATE",
            "Verificar fallback conservador quando Rege(v,p) não é determinado.",
            indeterminate["case"],
            indeterminate["result"],
            "REL e ARG1 permanecem no estado baseline; branch fallback selecionado.",
            "PASS",
            "NÃO",
        ],
        [
            "FIX-U-NONEMPTY",
            "U não vazio",
            "Verificar que tokens externos ao intervalo I(p,n) são preservados em ARG1.",
            u_nonempty["case"],
            u_nonempty["result"],
            "p migra para REL e U permanece em ARG1.",
            "PASS",
            "NÃO",
        ],
        [
            "FIX-PUNCT",
            "pontuação",
            "Verificar que a pontuação interna participa do intervalo ordenado sem ser perdida.",
            ordered["graph"],
            ordered["interval"],
            "Intervalo calculado na ordem do grafo, incluindo o nó intermediário.",
            "PASS",
            "NÃO",
        ],
        [
            "FIX-NONCONTIGUOUS",
            "IDs não contíguos",
            "Verificar que o intervalo não depende de aritmética sobre IDs contíguos.",
            ordered["nodes"],
            ordered["interval"],
            "I(10,30) usa a ordem dos tokens e não range(10,30).",
            "PASS",
            "NÃO",
        ],
        [
            "FIX-DUP-GUARD",
            "guardas duplicadas",
            "Verificar rejeição de edição que adiciona uma guarda já presente.",
            "regra com guarda existente + ADD_GUARD duplicado",
            "exceção/rejeição esperada",
            "A invariante de unicidade das guardas foi exercitada nas asserções v4.",
            "PASS",
            "NÃO",
        ],
        [
            "FIX-OVERLAP",
            "branches sobrepostos",
            "Verificar exclusividade da regra composta e rejeitar dois branches aplicáveis.",
            "ChoiceRule com branches simultaneamente verdadeiros",
            "exceção/rejeição esperada",
            "A invariante de exclusividade foi exercitada nas asserções v4.",
            "PASS",
            "NÃO",
        ],
    ]


def make_fixtures_sheet(workbook: Workbook, payload: Mapping[str, Any]) -> None:
    headers = [
        "fixture_id",
        "tipo",
        "objetivo",
        "entrada",
        "resultado",
        "asserção",
        "status",
        "EVIDÊNCIA_EMPÍRICA",
    ]
    sheet = workbook.create_sheet("06_Fixtures")
    append_table(sheet, headers, fixture_rows(payload))
    for row in range(2, sheet.max_row + 1):
        for cell in sheet[row]:
            cell.fill = FILL_FIXTURE
    style_sheet(sheet)


def make_metadata_sheet(
    workbook: Workbook,
    repo: Path,
    hashes: Mapping[str, str],
    output_path: Path,
    payload: Mapping[str, Any],
    generated_at: str,
) -> None:
    head = run_git(repo, "rev-parse", "HEAD")
    branch = run_git(repo, "branch", "--show-current")
    metadata = [
        ["metadado", "branch", branch, "branch no momento da exportação"],
        ["metadado", "HEAD", head, "commit no momento da exportação"],
        ["commit", "protocolo_v4", COMMITS["protocolo_v4"], "protocolo formal"],
        ["commit", "decisoes_v4", COMMITS["decisoes_v4"], "decisões de implementação"],
        ["commit", "implementacao_resultados_v4", COMMITS["implementacao_resultados_v4"], "notebook e resultados v4"],
        ["hash", "notebook_v4_sha256", hashes["notebook"], "fonte congelada"],
        ["hash", "planilha_OIEC_PT_GOLD_sha256", hashes["planilha_fonte"], "fonte congelada"],
        ["hash", "R_impl_sha256", payload["r_impl_hash"], "objeto formal serializado canonicamente"],
        ["metadado", "gerado_em_utc", generated_at, "UTC"],
        ["metadado", "arquivo_saida", str(output_path.relative_to(repo)), "artefato novo"],
        ["contagem", "candidatas", 3, "C0, C1 e C2"],
        ["contagem", "casos_reais", 8, "quatro E− e quatro controles"],
        ["contagem", "aplicacoes", 24, "candidata × caso"],
        ["contagem", "assercoes", 31, "asserções do notebook v4"],
        ["contagem", "pendencias", 11, "não contabilizadas como testes"],
        ["definicao", "PASS_EXPLORATORY", "passou no conjunto piloto sob entradas fornecidas", "não implica igualdade integral com GOLD nem generalização"],
        ["definicao", "FAIL_CORRECTION", "não corrigiu um E− E4", "falha de correção"],
        ["definicao", "FAIL_OVERAPPLICATION", "alterou indevidamente um controle", "sobreaplicação"],
        ["definicao", "TRUE_PROVISIONAL", "Rege(v,p) fornecido provisoriamente como verdadeiro", "a origem e o uso de GOLD devem ser lidos por alvo"],
        ["definicao", "FALSE_PROVISIONAL", "Rege(v,p) fornecido provisoriamente como falso", "não equivale a reconhecedor linguístico independente"],
        ["definicao", "INDETERMINATE", "não há evidência suficiente para decidir Rege(v,p)", "C2 seleciona fallback conservador"],
        ["definicao", "NÃO_MODELADO", "output baseline ainda não incorporado ao modelo formal", "não é contabilizado como teste aprovado"],
        ["definicao", "E_MINUS_E4", "output com violação E4 modelada no conjunto piloto", "as quatro ocorrências provêm de S009"],
        ["definicao", "CONTROL", "output modelado para teste de preservação", "não implica E+ E4 confirmado"],
        ["definicao", "CONFIRMADA_POR_TRACE", "proveniência operacional confirmada pela instrumentação", "aplicável especificamente a S009-A41"],
        ["definicao", "VARIANTE_DA_MESMA_SENTENÇA", "output de S009 sem trace específico do objeto correspondente", "não generalizar a proveniência de A41"],
        ["definicao", "DESCONHECIDA", "mecanismo implementado não confirmado por trace para o output", "aplicável aos controles modelados"],
        ["definicao", "output", "uma extração produzida pelo extrator", "vários outputs podem pertencer à mesma sentença"],
        ["definicao", "sentença independente", "texto de entrada distinto", "S009-A41–A44 contam como uma sentença"],
        ["definicao", "controle", "output modelado que a candidata deve preservar", "não equivale automaticamente a E+ específico de E4"],
        ["definicao", "fixture", "entrada sintética para testar propriedade formal", "EVIDÊNCIA_EMPÍRICA=NÃO"],
        ["definicao", "igualdade_de_fronteiras", "estado produzido igual ao estado esperado para a fronteira E4", "pode coexistir com erros residuais"],
        ["definicao", "igualdade_integral_GOLD", "ARG0, REL e ARG1 produzidos iguais ao GOLD modelado", "A43/A44 permanecem NÃO"],
        ["ressalva", "Rege(v,p)", "entrada experimental no v4", "origem registrada por alvo; utiliza parcialmente GOLD e não constitui reconhecedor operacional"],
        ["ressalva", "regeneração", "execução determinística em memória", "não é um novo experimento nem modifica o notebook"],
        ["ressalva", "espaço_de_revisões", "C0/C1/C2 são hipóteses delimitadas", "não esgotam todas as revisões possíveis"],
    ]
    sheet = workbook.create_sheet("07_Metadados_Dicionario")
    append_table(sheet, ["grupo", "chave", "valor", "definicao_ressalva"], metadata)
    style_sheet(sheet, {"A": 18, "B": 35, "C": 70, "D": 70})


ANNOTATION_HEADERS = [
    "id_aplicacao_ou_candidata",
    "tipo_objeto",
    "pesquisadora_revisora",
    "data",
    "decisao_ou_comentario",
    "evidencia_adicional",
    "status_revisao",
    "observacao_orientadora",
]


def read_existing_annotations(output_path: Path) -> list[list[Any]]:
    if not output_path.exists():
        return []
    workbook = load_workbook(output_path, read_only=True, data_only=False)
    if "08_Anotacoes" not in workbook.sheetnames:
        workbook.close()
        return []
    sheet = workbook["08_Anotacoes"]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if not rows:
        return []
    observed_headers = [normalize_header(value) for value in rows[0]]
    if observed_headers != ANNOTATION_HEADERS:
        raise ExportError(
            "A aba 08_Anotacoes existente tem cabeçalho incompatível; "
            "a planilha não será substituída."
        )
    return [list(row) for row in rows[1:] if any(value is not None for value in row)]


def make_annotations_sheet(workbook: Workbook, annotations: Sequence[Sequence[Any]]) -> None:
    sheet = workbook.create_sheet("08_Anotacoes")
    append_table(sheet, ANNOTATION_HEADERS, annotations)
    if not annotations:
        sheet.auto_filter.ref = f"A1:{get_column_letter(len(ANNOTATION_HEADERS))}1"
    for row in range(2, sheet.max_row + 1):
        for cell in sheet[row]:
            cell.fill = FILL_NOTE
    style_sheet(sheet, {"A": 30, "B": 20, "C": 25, "D": 18, "E": 60, "F": 60, "G": 22, "H": 60})


def build_workbook(
    repo: Path,
    output_path: Path,
    source_workbook: Path,
    payload: Mapping[str, Any],
    hashes: Mapping[str, str],
    annotations: Sequence[Sequence[Any]],
    generated_at: str,
) -> Workbook:
    analysis_rows = load_analysis_rows(source_workbook)
    for required in [case["case_id"] for case in payload["cases"]] + PENDING_CASES:
        ensure(required in analysis_rows, f"Linha de análise não encontrada para {required}.")

    workbook = Workbook()
    workbook.remove(workbook.active)
    workbook.properties.title = "Matriz de rastreabilidade da Theory Revision v4 — E4"
    workbook.properties.subject = "Derivação formal e avaliação de C0, C1 e C2"
    workbook.properties.creator = "Exportador reprodutível da pesquisa DptOIE"
    workbook.properties.description = (
        "Gerada a partir do notebook v4 congelado e da planilha OIEC-PT-GOLD; "
        "preserva anotações manuais na aba 08_Anotacoes."
    )
    workbook.properties.created = datetime.now(timezone.utc).replace(tzinfo=None)

    make_summary_sheet(workbook, payload)
    make_candidates_sheet(workbook, payload)
    make_operator_history_sheet(workbook, payload)
    make_results_sheet(workbook, payload, analysis_rows)
    make_decisions_sheet(workbook, payload)
    make_pending_sheet(workbook, analysis_rows)
    make_fixtures_sheet(workbook, payload)
    make_metadata_sheet(workbook, repo, hashes, output_path, payload, generated_at)
    make_annotations_sheet(workbook, annotations)
    ensure(workbook.sheetnames == EXPECTED_SHEETS, "Ordem ou nomes das abas divergiram.")
    return workbook


def validate_generated_workbook(path: Path) -> None:
    workbook = load_workbook(path, read_only=True, data_only=False)
    ensure(workbook.sheetnames == EXPECTED_SHEETS, "A planilha gerada perdeu abas esperadas.")
    ensure(workbook["01_Candidatas"].max_row - 1 == 3, "Contagem de candidatas no XLSX divergente.")
    ensure(workbook["03_Resultados_por_Caso"].max_row - 1 == 24, "Contagem de aplicações no XLSX divergente.")
    ensure(workbook["05_Cobertura_Pendente"].max_row - 1 == 11, "Contagem de pendências no XLSX divergente.")
    ensure(workbook["06_Fixtures"].max_row - 1 == 6, "Contagem de fixtures no XLSX divergente.")
    workbook.close()


def atomic_save(workbook: Workbook, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(output_path.stem + ".tmp.xlsx")
    if temporary.exists():
        temporary.unlink()
    try:
        workbook.save(temporary)
        validate_generated_workbook(temporary)
        os.replace(temporary, output_path)
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_args(repo: Path) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notebook",
        type=Path,
        default=repo / "research/graph_rewriting/experimento_v4_e4_theory_revision.ipynb",
    )
    parser.add_argument(
        "--source-workbook",
        type=Path,
        default=repo / "research/experimento/semana5_experimento_OIEC_PT_GOLD (3)(1).xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo / "research/experimento/rastreabilidade_theory_revision_v4_e4.xlsx",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Executa e valida as fontes em memória, mas não grava o XLSX.",
    )
    return parser.parse_args()


def main() -> int:
    script_path = Path(__file__)
    repo = find_repo_root(script_path)
    args = parse_args(repo)
    notebook = args.notebook.resolve()
    source_workbook = args.source_workbook.resolve()
    output_path = args.output.resolve()

    hashes = verify_frozen_inputs(notebook, source_workbook)
    for label, commit in COMMITS.items():
        try:
            run_git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
        except subprocess.CalledProcessError as exc:
            raise ExportError(f"Commit de referência ausente ({label}={commit}).") from exc

    payload = execute_notebook_in_memory(notebook, repo)
    validate_payload(payload)

    if args.verify_only:
        print("VALIDAÇÃO CONCLUÍDA: fontes e resultados v4 consistentes; nenhum arquivo produzido.")
        return 0

    annotations = read_existing_annotations(output_path)
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    workbook = build_workbook(
        repo=repo,
        output_path=output_path,
        source_workbook=source_workbook,
        payload=payload,
        hashes=hashes,
        annotations=annotations,
        generated_at=generated_at,
    )
    atomic_save(workbook, output_path)
    print(f"PLANILHA GERADA: {output_path}")
    print(f"SHA-256: {sha256_file(output_path)}")
    print("CONTAGENS: 3 candidatas; 8 casos; 24 aplicações; 11 pendências; 31 asserções verificadas.")
    print(f"ANOTAÇÕES PRESERVADAS: {len(annotations)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExportError as exc:
        print(f"ERRO DE VALIDAÇÃO: {exc}", file=sys.stderr)
        raise SystemExit(2)
