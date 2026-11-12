#!/usr/bin/env python3
"""Gera uma visão simplificada da Theory Revision v4 de E4.

A planilha apresenta os operadores e as candidatas em linguagem direta e,
para cada output real modelado, mostra a extração antes e depois de C0, C1 e
C2. As fontes científicas são validadas e o notebook é executado somente em
memória pelo exportador completo já existente.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

import exporta_rastreabilidade_v4_e4 as full


OUTPUT_NAME = "rastreabilidade_simplificada_theory_revision_v4_e4.xlsx"
SHEET_CANDIDATES = "01_Operadores_e_Candidatas"
SHEET_TRANSFORMATIONS = "02_Antes_e_Depois"

EXPECTED_OPERATOR_SEQUENCES = {
    "C0": ["RESTRICT_INTERVAL", "CHANGE_COMPONENT"],
    "C1": ["ADD_GUARD", "ADD_GUARD", "RESTRICT_INTERVAL", "CHANGE_COMPONENT", "SPLIT_RULE"],
    "C2": ["ADD_GUARD_REGE", "RESTRICT_INTERVAL", "CHANGE_COMPONENT", "SPLIT_RULE"],
}

OPERATORS = [
    [
        "ADD_GUARD",
        "Adiciona uma condição sintática ao matching.",
        "C1: uma guarda para case(p,n) e outra para nmod(n,v).",
    ],
    [
        "ADD_GUARD_REGE",
        "Exige que o status experimental de Rege(v,p) seja verdadeiro.",
        "C2.",
    ],
    [
        "RESTRICT_INTERVAL",
        "Separa p do intervalo ordenado I(p,n) e preserva os demais tokens do argumento.",
        "C0, C1 e C2.",
    ],
    [
        "CHANGE_COMPONENT",
        "Muda o componente de p: p deixa ARG1 e passa para REL.",
        "C0, C1 e C2.",
    ],
    [
        "SPLIT_RULE",
        "Cria uma regra especializada e um fallback que preserva a construção original.",
        "C1 e C2.",
    ],
]

CANDIDATE_PRESENTATION = {
    "C0": {
        "question": "O diff estrutural, sozinho, é suficiente?",
        "sequence": "RESTRICT_INTERVAL → CHANGE_COMPONENT",
        "rule": (
            "Sem guarda adicional: transfere p de ARG1 para REL em todo alvo "
            "aceito pela construção modelada."
        ),
        "explanation": (
            "Corrige os quatro outputs de S009 e preserva A20, mas transfere "
            "preposições indevidamente em A28, A51 e A52."
        ),
    },
    "C1": {
        "question": "As dependências case(p,n) e nmod(n,v) são suficientes?",
        "sequence": (
            "ADD_GUARD(case) → ADD_GUARD(nmod) → RESTRICT_INTERVAL → "
            "CHANGE_COMPONENT → SPLIT_RULE"
        ),
        "rule": (
            "Se case(p,n) e nmod(n,v), transfere p de ARG1 para REL; "
            "caso contrário, aplica o fallback e preserva a extração."
        ),
        "explanation": (
            "Corrige S009 e preserva A28/A20, mas as dependências não distinguem "
            "os controles locativos A51 e A52."
        ),
    },
    "C2": {
        "question": "É necessária a condição linguística Rege(v,p)?",
        "sequence": "ADD_GUARD_REGE → RESTRICT_INTERVAL → CHANGE_COMPONENT → SPLIT_RULE",
        "rule": (
            "Se Rege(v,p)=TRUE_PROVISIONAL, transfere p; se o status for falso "
            "ou indeterminado, preserva a extração pelo fallback."
        ),
        "explanation": (
            "Corrige os quatro outputs de S009 e preserva os quatro controles, "
            "mas depende do status de regência fornecido experimentalmente."
        ),
    },
}

RESULT_LABELS = {
    "C0": "FAIL_OVERAPPLICATION — 5/8 acertos; 3 sobreaplicações",
    "C1": "FAIL_OVERAPPLICATION — 6/8 acertos; 2 sobreaplicações",
    "C2": "PASS_EXPLORATORY — 8/8 acertos condicionais",
}

FILL_TITLE = PatternFill("solid", fgColor="17365D")
FILL_SECTION = PatternFill("solid", fgColor="D9EAF7")
FILL_HEADER = PatternFill("solid", fgColor="4472C4")
FILL_GREEN = PatternFill("solid", fgColor="E2F0D9")
FILL_RED = PatternFill("solid", fgColor="F4CCCC")
FILL_ORANGE = PatternFill("solid", fgColor="FCE5CD")
FILL_NOTE = PatternFill("solid", fgColor="FFF2CC")
FILL_ALT = PatternFill("solid", fgColor="F7FBFF")
FONT_WHITE_BOLD = Font(color="FFFFFF", bold=True)
FONT_TITLE = Font(color="FFFFFF", bold=True, size=15)
FONT_SECTION = Font(color="17365D", bold=True, size=12)
THIN_BORDER = Border(
    left=Side(style="thin", color="D9E1F2"),
    right=Side(style="thin", color="D9E1F2"),
    top=Side(style="thin", color="D9E1F2"),
    bottom=Side(style="thin", color="D9E1F2"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def set_cell_style(cell, fill: PatternFill | None = None, font: Font | None = None) -> None:
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    cell.border = THIN_BORDER
    if fill is not None:
        cell.fill = fill
    if font is not None:
        cell.font = font


def write_header(sheet, row: int, headers: Sequence[str]) -> None:
    for column, header in enumerate(headers, start=1):
        cell = sheet.cell(row=row, column=column, value=header)
        set_cell_style(cell, FILL_HEADER, FONT_WHITE_BOLD)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def add_table(sheet, reference: str, name: str) -> None:
    table = Table(displayName=name, ref=reference)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    sheet.add_table(table)


def operator_sequence(payload: Mapping[str, Any], candidate: str) -> list[str]:
    chain = payload["edit_chains"][candidate]
    operations = [record["operator"] for record in chain["specialized_history"]]
    operations.extend(record["operator"] for record in chain["composite_history"])
    return operations


def validate_operator_sequences(payload: Mapping[str, Any]) -> None:
    for candidate, expected in EXPECTED_OPERATOR_SEQUENCES.items():
        observed = operator_sequence(payload, candidate)
        full.ensure(
            observed == expected,
            f"Sequência de operadores de {candidate} divergiu: {observed}.",
        )


def build_candidate_sheet(workbook: Workbook, payload: Mapping[str, Any], generated_at: str) -> None:
    sheet = workbook.create_sheet(SHEET_CANDIDATES)
    sheet.sheet_view.showGridLines = False
    sheet.freeze_panes = "A4"

    sheet.merge_cells("A1:F1")
    sheet["A1"] = "Operadores e regras candidatas — Theory Revision v4 / E4"
    sheet["A1"].fill = FILL_TITLE
    sheet["A1"].font = FONT_TITLE
    sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")
    sheet.row_dimensions[1].height = 28

    sheet.merge_cells("A2:F2")
    sheet["A2"] = (
        "Como ler: os operadores são edições formais combinadas para produzir C0, C1 e C2. "
        "As candidatas são hipóteses exploratórias, não todas as revisões possíveis."
    )
    sheet["A2"].fill = FILL_NOTE
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    sheet.row_dimensions[2].height = 38

    sheet.merge_cells("A3:C3")
    sheet["A3"] = "1. Operadores formais"
    sheet["A3"].fill = FILL_SECTION
    sheet["A3"].font = FONT_SECTION

    operator_headers = ["Operador", "O que faz", "Onde é usado"]
    write_header(sheet, 4, operator_headers)
    for row_index, row in enumerate(OPERATORS, start=5):
        for column, value in enumerate(row, start=1):
            cell = sheet.cell(row=row_index, column=column, value=value)
            set_cell_style(cell)
    add_table(sheet, "A4:C9", "OperadoresV4E4")

    sheet.merge_cells("A11:F11")
    sheet["A11"] = "2. Regras candidatas derivadas de R_impl"
    sheet["A11"].fill = FILL_SECTION
    sheet["A11"].font = FONT_SECTION

    candidate_headers = [
        "Candidata",
        "Pergunta investigada",
        "Sequência de operadores",
        "Regra resultante em linguagem simples",
        "Resultado global",
        "Por que obteve esse resultado",
    ]
    write_header(sheet, 12, candidate_headers)
    for row_index, candidate in enumerate(("C0", "C1", "C2"), start=13):
        presentation = CANDIDATE_PRESENTATION[candidate]
        values = [
            candidate,
            presentation["question"],
            presentation["sequence"],
            presentation["rule"],
            RESULT_LABELS[candidate],
            presentation["explanation"],
        ]
        fill = FILL_GREEN if candidate == "C2" else FILL_RED
        for column, value in enumerate(values, start=1):
            cell = sheet.cell(row=row_index, column=column, value=value)
            set_cell_style(cell, fill)
        sheet.row_dimensions[row_index].height = 78
    add_table(sheet, "A12:F15", "CandidatasV4E4")

    sheet.merge_cells("A17:F17")
    sheet["A17"] = (
        "Limite: PASS_EXPLORATORY não significa solução geral nem igualdade integral com o GOLD. "
        "C2 depende de Rege(v,p) fornecido experimentalmente."
    )
    sheet["A17"].fill = FILL_NOTE
    sheet["A17"].alignment = Alignment(wrap_text=True, vertical="top")

    sheet.merge_cells("A18:F18")
    sheet["A18"] = (
        f"Gerado em {generated_at} | notebook v4 SHA-256 {full.NOTEBOOK_SHA256} | "
        f"31 asserções verificadas"
    )
    sheet["A18"].font = Font(color="666666", italic=True, size=9)
    sheet["A18"].alignment = Alignment(wrap_text=True)

    widths = {"A": 23, "B": 37, "C": 55, "D": 62, "E": 42, "F": 62}
    for column, width in widths.items():
        sheet.column_dimensions[column].width = width
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.fitToWidth = 1
    sheet.sheet_properties.pageSetUpPr.fitToPage = True


def result_by_case(payload: Mapping[str, Any]) -> dict[tuple[str, str], Mapping[str, Any]]:
    return {(result["case_id"], result["candidate"]): result for result in payload["results"]}


def extraction_text(
    payload: Mapping[str, Any], sentence_id: str, state: Mapping[str, Any]
) -> str:
    tokens = full.parse_tokens(payload, sentence_id)
    return full.state_text_from_ids(tokens, state)


def movement_text(payload: Mapping[str, Any], case: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    tokens = full.parse_tokens(payload, case["sentence_id"])
    moved = [target for target in result["targets"] if full.moved_target(target)]
    if not moved:
        return "nenhum token transferido — extração preservada"
    return "; ".join(
        f"{full.token_form(tokens, int(target['p']))}: ARG1 → REL"
        for target in moved
    )


def evaluation_text(case: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    if result["classification"] == "FAIL_OVERAPPLICATION":
        return "ERRO — sobreaplicação"
    if result["classification"] == "FAIL_CORRECTION":
        return "ERRO — não corrigiu E4"
    if str(case["kind"]).startswith("E_MINUS"):
        if case["case_id"] in {"S009-A43", "S009-A44"}:
            return "ACERTO E4, MAS NÃO IGUAL AO GOLD — E3/S3 residuais"
        return "ACERTO — corrigiu E4"
    return "ACERTO — controle preservado"


def methodological_note(case_id: str) -> str:
    if case_id == "S009-A41":
        return "Caso piloto primário; proveniência operacional confirmada por trace."
    if case_id == "S009-A42":
        return "Variante da mesma sentença S009; E4 corrigida no modelo."
    if case_id in {"S009-A43", "S009-A44"}:
        return "E4 corrigida, mas permanecem divergências E3/S3; não há igualdade integral com o GOLD."
    if case_id == "S005-A28":
        return "Controle: C0 sobreaplica; C1 e C2 preservam a extração."
    if case_id in {"S010-A51", "S010-A52"}:
        return "Controle locativo: C0 e C1 sobreaplicam; C2 preserva a extração."
    return "Controle: C0, C1 e C2 preservam a extração."


TRANSFORMATION_HEADERS = [
    "Caso",
    "Tipo",
    "Sentença original — não modificada",
    "Extração ANTES — baseline",
    "GOLD",
    "Dependências do alvo",
    "Resultado das guardas",
    "DEPOIS C0",
    "Movimento C0",
    "Avaliação C0",
    "DEPOIS C1",
    "Movimento C1",
    "Avaliação C1",
    "DEPOIS C2",
    "Movimento C2",
    "Avaliação C2",
    "Observação metodológica",
]


def head_label(tokens: Mapping[int, Mapping[str, Any]], head_id: int) -> str:
    if head_id == 0:
        return "ROOT(0)"
    token = tokens.get(head_id)
    return f"{token['form']}({head_id})" if token else f"ID={head_id}"


def dependency_evidence(
    payload: Mapping[str, Any],
    case: Mapping[str, Any],
    reference_result: Mapping[str, Any],
) -> str:
    tokens = full.parse_tokens(payload, case["sentence_id"])
    evidence: list[str] = []
    for target in reference_result["targets"]:
        p = int(target["p"])
        n = int(target["n"])
        p_token = tokens[p]
        n_token = tokens[n]
        p_head = int(p_token["head"])
        n_head = int(n_token["head"])
        evidence.append(
            f"Alvo {p_token['form']} (p={p}, n={n}): "
            f"{p_token['form']}({p}) —{p_token['deprel']}→ {head_label(tokens, p_head)}; "
            f"{n_token['form']}({n}) —{n_token['deprel']}→ {head_label(tokens, n_head)}"
        )
    return "\n".join(evidence)


def action_label(result_target: Mapping[str, Any] | None) -> str:
    if result_target is None:
        return "NÃO AVALIADO"
    return "TRANSFERE" if full.moved_target(result_target) else "PRESERVA"


def guard_outcomes(
    payload: Mapping[str, Any],
    case: Mapping[str, Any],
    c0: Mapping[str, Any],
    c1: Mapping[str, Any],
    c2: Mapping[str, Any],
) -> str:
    tokens = full.parse_tokens(payload, case["sentence_id"])
    relation_core = int(case["relation_core"])
    targets_by_candidate = {
        "C0": {(int(item["p"]), int(item["n"])): item for item in c0["targets"]},
        "C1": {(int(item["p"]), int(item["n"])): item for item in c1["targets"]},
        "C2": {(int(item["p"]), int(item["n"])): item for item in c2["targets"]},
    }
    outcomes: list[str] = []
    for target in c2["targets"]:
        p = int(target["p"])
        n = int(target["n"])
        key = (p, n)
        p_token = tokens[p]
        n_token = tokens[n]
        case_guard = str(p_token["deprel"]) == "case" and int(p_token["head"]) == n
        nmod_guard = str(n_token["deprel"]) == "nmod" and int(n_token["head"]) == relation_core
        c0_target = targets_by_candidate["C0"].get(key)
        c1_target = targets_by_candidate["C1"].get(key)
        c2_target = targets_by_candidate["C2"].get(key)
        c1_branch = c1_target.get("branch") if c1_target else "NÃO AVALIADO"
        c2_branch = c2_target.get("branch") if c2_target else "NÃO AVALIADO"
        outcomes.append(
            f"Alvo {p_token['form']}({p}): "
            f"C0 sem guarda adicional → {action_label(c0_target)}; "
            f"C1 case={str(case_guard).upper()}, nmod={str(nmod_guard).upper()}, "
            f"branch={c1_branch} → {action_label(c1_target)}; "
            f"C2 Rege={target.get('status_rege')}, branch={c2_branch} → {action_label(c2_target)}"
        )
    return "\n".join(outcomes)


def build_transformation_rows(
    payload: Mapping[str, Any], analysis_rows: Mapping[str, Mapping[str, Any]]
) -> list[list[Any]]:
    results = result_by_case(payload)
    rows: list[list[Any]] = []
    for case in payload["cases"]:
        case_id = case["case_id"]
        source = analysis_rows[case_id]
        c0 = results[(case_id, "C0")]
        c1 = results[(case_id, "C1")]
        c2 = results[(case_id, "C2")]
        case_type = "E− E4" if str(case["kind"]).startswith("E_MINUS") else "CONTROLE"
        rows.append(
            [
                case_id,
                case_type,
                source["sentenca_original"],
                extraction_text(payload, case["sentence_id"], c0["baseline"]),
                extraction_text(payload, case["sentence_id"], c0["gold"]),
                dependency_evidence(payload, case, c2),
                guard_outcomes(payload, case, c0, c1, c2),
                extraction_text(payload, case["sentence_id"], c0["result"]),
                movement_text(payload, case, c0),
                evaluation_text(case, c0),
                extraction_text(payload, case["sentence_id"], c1["result"]),
                movement_text(payload, case, c1),
                evaluation_text(case, c1),
                extraction_text(payload, case["sentence_id"], c2["result"]),
                movement_text(payload, case, c2),
                evaluation_text(case, c2),
                methodological_note(case_id),
            ]
        )
    return rows


def evaluation_fill(value: str) -> PatternFill:
    if value.startswith("ERRO"):
        return FILL_RED
    if "MAS NÃO IGUAL" in value:
        return FILL_ORANGE
    return FILL_GREEN


def build_transformation_sheet(
    workbook: Workbook,
    payload: Mapping[str, Any],
    analysis_rows: Mapping[str, Mapping[str, Any]],
) -> None:
    sheet = workbook.create_sheet(SHEET_TRANSFORMATIONS)
    sheet.sheet_view.showGridLines = False
    sheet.freeze_panes = "F2"
    write_header(sheet, 1, TRANSFORMATION_HEADERS)

    rows = build_transformation_rows(payload, analysis_rows)
    for row_index, row in enumerate(rows, start=2):
        for column, value in enumerate(row, start=1):
            fill = FILL_ALT if row_index % 2 == 0 else None
            cell = sheet.cell(row=row_index, column=column, value=value)
            set_cell_style(cell, fill)
        for evaluation_column in (10, 13, 16):
            cell = sheet.cell(row=row_index, column=evaluation_column)
            cell.fill = evaluation_fill(str(cell.value))
            cell.font = Font(bold=True)
        sheet.row_dimensions[row_index].height = 150

    add_table(sheet, "A1:Q9", "TransformacoesV4E4")
    widths = {
        "A": 16,
        "B": 13,
        "C": 65,
        "D": 54,
        "E": 54,
        "F": 68,
        "G": 90,
        "H": 54,
        "I": 28,
        "J": 31,
        "K": 54,
        "L": 28,
        "M": 31,
        "N": 54,
        "O": 28,
        "P": 31,
        "Q": 58,
    }
    for column, width in widths.items():
        sheet.column_dimensions[column].width = width
    sheet.row_dimensions[1].height = 48
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.fitToWidth = 1
    sheet.sheet_properties.pageSetUpPr.fitToPage = True


def validate_workbook(path: Path) -> None:
    workbook = load_workbook(path, read_only=False, data_only=False)
    full.ensure(
        workbook.sheetnames == [SHEET_CANDIDATES, SHEET_TRANSFORMATIONS],
        "As abas da planilha simplificada divergiram.",
    )
    sheet = workbook[SHEET_TRANSFORMATIONS]
    full.ensure(sheet.max_row == 9, "A aba Antes e Depois deve conter exatamente oito outputs.")
    full.ensure(sheet.max_column == 17, "A aba Antes e Depois deve conter exatamente 17 colunas.")
    headers = {cell.value: cell.column for cell in sheet[1]}
    full.ensure(list(headers) == TRANSFORMATION_HEADERS, "Cabeçalho da comparação divergiu.")

    rows = {
        sheet.cell(row, headers["Caso"]).value: {
            candidate: sheet.cell(row, headers[f"Avaliação {candidate}"]).value
            for candidate in ("C0", "C1", "C2")
        }
        for row in range(2, sheet.max_row + 1)
    }
    for case_id in ("S005-A28", "S010-A51", "S010-A52"):
        full.ensure(
            rows[case_id]["C0"] == "ERRO — sobreaplicação",
            f"C0 deveria sobreaplicar em {case_id}.",
        )
    for case_id in ("S010-A51", "S010-A52"):
        full.ensure(
            rows[case_id]["C1"] == "ERRO — sobreaplicação",
            f"C1 deveria sobreaplicar em {case_id}.",
        )
    full.ensure(
        all(not str(values["C2"]).startswith("ERRO") for values in rows.values()),
        "C2 deveria passar condicionalmente nos oito outputs.",
    )
    for case_id in ("S009-A43", "S009-A44"):
        for candidate in ("C0", "C1", "C2"):
            full.ensure(
                "MAS NÃO IGUAL AO GOLD" in rows[case_id][candidate],
                f"{candidate}/{case_id} perdeu a ressalva sobre E3/S3.",
            )
    a52_row = next(
        row for row in range(2, sheet.max_row + 1)
        if sheet.cell(row, headers["Caso"]).value == "S010-A52"
    )
    a52_dependencies = str(sheet.cell(a52_row, headers["Dependências do alvo"]).value)
    a52_guards = str(sheet.cell(a52_row, headers["Resultado das guardas"]).value)
    full.ensure(
        "en(6) —case→ Universidade(8)" in a52_dependencies
        and "Universidade(8) —nmod→ visitei(2)" in a52_dependencies,
        "S010-A52 perdeu a evidência case(en,Universidade)+nmod(Universidade,visitei).",
    )
    full.ensure(
        "C1 case=TRUE, nmod=TRUE, branch=MATCH_SYNTACTIC → TRANSFERE" in a52_guards
        and "Alvo para(11)" in a52_guards
        and "C1 case=FALSE, nmod=TRUE, branch=FALLBACK → PRESERVA" in a52_guards,
        "S010-A52 perdeu o resultado explícito das guardas de C1.",
    )
    workbook.close()


def save_atomically(workbook: Workbook, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.stem + ".tmp.xlsx")
    if temporary.exists():
        temporary.unlink()
    try:
        workbook.save(temporary)
        validate_workbook(temporary)
        os.replace(temporary, output)
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
        default=repo / "research/experimento" / OUTPUT_NAME,
    )
    return parser.parse_args()


def main() -> int:
    repo = full.find_repo_root(Path(__file__))
    args = parse_args(repo)
    notebook = args.notebook.resolve()
    source_workbook = args.source_workbook.resolve()
    output = args.output.resolve()

    full.verify_frozen_inputs(notebook, source_workbook)
    payload = full.execute_notebook_in_memory(notebook, repo)
    full.validate_payload(payload)
    validate_operator_sequences(payload)
    analysis_rows = full.load_analysis_rows(source_workbook)

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    workbook = Workbook()
    workbook.remove(workbook.active)
    workbook.properties.title = "Rastreabilidade simplificada da Theory Revision v4 — E4"
    workbook.properties.subject = "Operadores, candidatas e transformações antes/depois"
    workbook.properties.creator = "Exportador reprodutível da pesquisa DptOIE"
    workbook.properties.description = (
        "Visão simplificada; a matriz científica completa permanece em artefato separado."
    )
    workbook.properties.created = datetime.now(timezone.utc).replace(tzinfo=None)

    build_candidate_sheet(workbook, payload, generated_at)
    build_transformation_sheet(workbook, payload, analysis_rows)
    save_atomically(workbook, output)

    print(f"PLANILHA SIMPLIFICADA GERADA: {output}")
    print(f"SHA-256: {sha256_file(output)}")
    print("ABAS: 01_Operadores_e_Candidatas; 02_Antes_e_Depois")
    print("COBERTURA: 5 operadores; 3 candidatas; 8 outputs; comparações ANTES -> DEPOIS.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except full.ExportError as exc:
        print(f"ERRO DE VALIDAÇÃO: {exc}", file=sys.stderr)
        raise SystemExit(2)
