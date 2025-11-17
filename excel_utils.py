# excel_utils.py
import logging
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def parse_excel_file(upload_file, criteria_names: List[str]) -> Tuple[List[str], list, Optional[list]]:
    xls = pd.ExcelFile(upload_file)
    sheet_main = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_main)

    if df.shape[1] < len(criteria_names) + 1:
        raise ValueError(
            "Jumlah kolom pada Excel belum sesuai: "
            "minimal 1 kolom nama + semua kolom kriteria."
        )

    raw_cols = [str(c).strip() for c in df.columns]
    header_map = {}

    for j, cname in enumerate(criteria_names):
        target = cname.lower()
        found_idx = None
        for idx_col, col_name in enumerate(raw_cols[1:], start=1):
            if str(col_name).strip().lower() == target:
                found_idx = idx_col
                break
        if found_idx is None:
            raise ValueError(
                f"Kolom untuk kriteria '{cname}' tidak ditemukan di header Excel."
            )
        header_map[j] = found_idx

    names = []
    data = []
    weights = None

    for _, row in df.iterrows():
        first_cell = str(row.iloc[0]).strip()

        if first_cell == "" or first_cell.lower() in ("nan", "none"):
            continue

        # baris bobot
        if first_cell.lower() == "bobot":
            tmp_weights = []
            for j in range(len(criteria_names)):
                v = row.iloc[header_map[j]]
                if pd.isna(v):
                    raise ValueError(
                        f"Bobot untuk kriteria '{criteria_names[j]}' di baris Bobot kosong."
                    )
                tmp_weights.append(float(v))
            weights = tmp_weights
            continue

        # baris alternatif
        alt_name = first_cell
        vals = []
        for j in range(len(criteria_names)):
            v = row.iloc[header_map[j]]
            if pd.isna(v):
                raise ValueError(
                    f"Nilai '{criteria_names[j]}' kosong untuk alternatif '{alt_name}'."
                )
            vals.append(float(v))

        names.append(alt_name)
        data.append(vals)

    if len(names) < 2:
        raise ValueError("Minimal harus ada 2 alternatif pada file Excel.")

    # sheet weights 
    if "weights" in xls.sheet_names and weights is None:
        dfw = pd.read_excel(xls, "weights")
        row0 = dfw.iloc[0].tolist()
        tmp_weights = []
        for j in range(len(criteria_names)):
            tmp_weights.append(float(row0[j]))
        weights = tmp_weights

    return names, data, weights
