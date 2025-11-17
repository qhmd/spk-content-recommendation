# dss_core.py
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Criteria definition (fixed)
CRITERIA = [
    ("Reach", "benefit"),
    ("Views", "benefit"),
    ("Engagement Rate", "benefit"),
    ("Branding", "benefit"),
    ("CTA", "benefit"),
    ("Cost Production", "cost"),
]

# toleransi selisih total bobot dari 100
WEIGHT_TOLERANCE = 0  


def parse_matrix_from_form(form):
    names = form.getlist("name[]")
    if not names:
        raise ValueError("Tidak ada alternatif yang dikirimkan (name[] kosong).")

    n_crit = len(CRITERIA)

    cols = []
    for j in range(n_crit):
        fld = form.getlist(f"c{j}[]")
        cols.append(fld)

    m = len(names)
    for j, col in enumerate(cols):
        if len(col) != m:
            raise ValueError(
                f"Kolom c{j}[] panjangnya ({len(col)}) tidak cocok dengan jumlah nama ({m})."
            )

    X = np.zeros((m, n_crit), dtype=float)
    for i in range(m):
        for j in range(n_crit):
            raw = cols[j][i]
            if raw is None or str(raw).strip() == "":
                raise ValueError(
                    f"Nilai kosong pada alternatif #{i + 1} kolom {CRITERIA[j][0]}."
                )
            try:
                X[i, j] = float(raw)
            except Exception:
                raise ValueError(
                    f"Nilai tidak valid pada alternatif #{i + 1} kolom {CRITERIA[j][0]}: '{raw}'"
                )
    return names, X


def parse_weights_from_form(form):
    n_crit = len(CRITERIA)
    weights = []
    for j in range(n_crit):
        raw = form.get(f"w{j}", None)
        if raw is None or str(raw).strip() == "":
            raise ValueError("Semua bobot kriteria harus diisi.")
        try:
            w = float(raw)
        except Exception:
            raise ValueError(f"Bobot untuk '{CRITERIA[j][0]}' tidak valid: '{raw}'")
        if w < 0:
            raise ValueError(f"Bobot tidak boleh negatif untuk '{CRITERIA[j][0]}'.")
        weights.append(w)

    total = sum(weights)
    if total <= 0:
        raise ValueError("Total bobot harus lebih dari 0.")

    if abs(total - 100.0) > WEIGHT_TOLERANCE:
        raise ValueError(f"Total bobot harus = 100 (saat ini {total}).")

    wnorm = [w / total for w in weights]
    return np.array(wnorm, dtype=float), weights


def compute_saw(X):
    m, n = X.shape
    R = np.zeros_like(X, dtype=float)
    for j in range(n):
        col = X[:, j]
        typ = CRITERIA[j][1]
        if typ == "benefit":
            maxv = np.max(col)
            if maxv == 0:
                R[:, j] = 0.0
            else:
                R[:, j] = col / maxv
        else:  # cost
            minv = np.min(col)
            with np.errstate(divide="ignore", invalid="ignore"):
                R[:, j] = np.where(col != 0, minv / col, 0.0)
    return R


def compute_topsis_from_R(R_saw, weights_arr):
    R_norm = R_saw
    Y = R_norm * weights_arr  # (m,n) * (n,)

    m, n = Y.shape
    ideal_pos = np.zeros(n)
    ideal_neg = np.zeros(n)

    for j in range(n):
        typ = CRITERIA[j][1]
        col = Y[:, j]
        if typ == "benefit":
            ideal_pos[j] = col.max()
            ideal_neg[j] = col.min()
        else:  # cost
            ideal_pos[j] = col.min()
            ideal_neg[j] = col.max()

    D_pos = np.sqrt(((ideal_pos - Y) ** 2).sum(axis=1))
    D_neg = np.sqrt(((Y - ideal_neg) ** 2).sum(axis=1))

    denom_score = D_pos + D_neg
    with np.errstate(divide="ignore", invalid="ignore"):
        score = np.where(denom_score != 0, D_neg / denom_score, 0.0)

    return {
        "R_norm": R_norm,
        "Y": Y,
        "ideal_pos": ideal_pos,
        "ideal_neg": ideal_neg,
        "D_pos": D_pos,
        "D_neg": D_neg,
        "score": score,
    }
