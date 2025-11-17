# app.py
import logging

from flask import Flask, render_template, request, redirect, url_for, flash
import numpy as np

from dss_core import (
    CRITERIA,
    parse_matrix_from_form,
    parse_weights_from_form,
    compute_saw,
    compute_topsis_from_R,
)
from excel_utils import parse_excel_file

app = Flask(__name__)
app.secret_key = "dev-secret-key"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/input", methods=["GET", "POST"])
def input_data():
    if request.method == "POST":
        try:
            names, X = parse_matrix_from_form(request.form)
            if len(names) < 2:
                raise ValueError("Minimal harus ada 2 alternatif konten.")

            weights_arr, weights_raw = parse_weights_from_form(request.form)

            R_saw = compute_saw(X)
            V_saw = (R_saw * weights_arr).sum(axis=1)

            topsis = compute_topsis_from_R(R_saw, weights_arr)

            score = topsis["score"]
            indices = np.argsort(-score)

            ranking = []
            for rank, idx in enumerate(indices, start=1):
                ranking.append(
                    {
                        "rank": rank,
                        "name": names[idx],
                        "score": float(score[idx]),
                        "saw_value": float(V_saw[idx]),
                        "values": [float(x) for x in X[idx].tolist()],
                        "r_saw": [float(x) for x in R_saw[idx].tolist()],
                        "y": [float(x) for x in topsis["Y"][idx].tolist()],
                        "d_pos": float(topsis["D_pos"][idx]),
                        "d_neg": float(topsis["D_neg"][idx]),
                    }
                )

            criteria_names = [c[0] for c in CRITERIA]

            return render_template(
                "results.html",
                criteria=criteria_names,
                raw_matrix=X.tolist(),
                R_saw=R_saw.tolist(),
                weights=[round(w, 6) for w in weights_arr.tolist()],
                V_saw=[float(x) for x in V_saw.tolist()],
                Y=topsis["Y"].tolist(),
                ideal_pos=[float(x) for x in topsis["ideal_pos"].tolist()],
                ideal_neg=[float(x) for x in topsis["ideal_neg"].tolist()],
                D_pos=[float(x) for x in topsis["D_pos"].tolist()],
                D_neg=[float(x) for x in topsis["D_neg"].tolist()],
                score=[float(x) for x in topsis["score"].tolist()],
                ranking=ranking,
                names=names,
            )
        except ValueError as ve:
            flash(str(ve), "danger")
            return redirect(url_for("input_data"))
        except Exception:
            logger.exception("Unexpected error while processing input")
            flash("Terjadi kesalahan pada server saat memproses data.", "danger")
            return redirect(url_for("input_data"))

    return render_template("input.html", criteria=CRITERIA)


@app.route("/upload", methods=["GET", 'POST'])
def upload_excel():
    criteria_names = [c[0] for c in CRITERIA]

    if request.method == "POST":
        file = request.files.get("excel")
        if not file or file.filename == "":
            flash("File Excel belum dipilih.", "danger")
            return redirect(url_for("upload_excel"))

        try:
            names, data, weights = parse_excel_file(file, criteria_names)

            return render_template(
                "upload_preview.html",
                criteria=criteria_names,
                names=names,
                data=data,
                weights=weights,
            )
        except Exception as e:
            logger.exception("Error saat membaca Excel")
            flash(f"Gagal membaca file Excel: {e}", "danger")
            return redirect(url_for("upload_excel"))

    return render_template("upload.html", criteria=criteria_names)


if __name__ == "__main__":
    app.run(debug=True)
