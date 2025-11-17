document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("dssForm");
  const altsBody = document.getElementById("altsBody");
  const addAltBtn = document.getElementById("addAlt");
  const resetBtn = document.getElementById("resetForm");
  const submitBtn = document.getElementById("submitBtn");
  const formMsg = document.getElementById("formMsg");
  const weightInfo = document.getElementById("weightInfo");

  function syncNumericInput(input) {
    const hidden = input.parentElement.querySelector(".numeric-hidden");
    if (!hidden) return;
    let raw = input.value || "";
    raw = raw.replace(/[^0-9,.\-]/g, "");
    raw = raw.replace(",", ".");
    const num = parseFloat(raw);
    if (isNaN(num)) {
      hidden.value = "";
    } else {
      hidden.value = String(num);
    }
  }

  function attachNumericHandlers(scope) {
    scope.querySelectorAll(".numeric-input").forEach((inp) => {
      inp.addEventListener("input", () => syncNumericInput(inp));
      inp.addEventListener("blur", () => syncNumericInput(inp));
    });
  }

  const weightInputs = document.querySelectorAll(".weight-input");

  function updateWeightInfo() {
    if (!weightInfo || !weightInputs.length) return;

    let total = 0;
    weightInputs.forEach((inp) => {
      const v = parseFloat(inp.value);
      if (!isNaN(v)) total += v;
    });

    weightInfo.textContent = `Total bobot: ${total.toFixed(2)}% (harus 100%)`;

    weightInfo.className =
      "inline-block text-sm py-2 px-3 rounded " +
      (Math.abs(total - 100) <= 1
        ? "bg-emerald-600/70"
        : total > 100
        ? "bg-red-600/80"
        : "bg-amber-500/80");
  }

  weightInputs.forEach((inp) => {
    inp.addEventListener("input", updateWeightInfo);
  });

  updateWeightInfo();

  //  tambah / hapus baris alternatif
  if (addAltBtn && altsBody) {
    addAltBtn.addEventListener("click", () => {
      const rows = altsBody.querySelectorAll(".alt-row");
      if (!rows.length) return;
      const lastRow = rows[rows.length - 1];
      const clone = lastRow.cloneNode(true);

      // kosongkan input
      clone.querySelectorAll("input").forEach((inp) => {
        inp.value = "";
        inp.classList.remove("input-invalid");
      });

      altsBody.appendChild(clone);
      attachNumericHandlers(clone);
    });

    altsBody.addEventListener("click", (e) => {
      const btn = e.target.closest(".remove-row");
      if (!btn) return;
      const rows = altsBody.querySelectorAll(".alt-row");
      if (rows.length <= 1) {
        alert("Minimal harus ada 1 baris. Hapus di form saja jika tidak terpakai.");
        return;
      }
      btn.closest(".alt-row").remove();
    });

    attachNumericHandlers(altsBody);
  }

  // reset form 
  if (resetBtn && form) {
    resetBtn.addEventListener("click", () => {
      form.reset();
      // bersihkan hidden numeric
      form.querySelectorAll(".numeric-hidden").forEach((h) => (h.value = ""));
      form.querySelectorAll(".input-invalid").forEach((el) =>
        el.classList.remove("input-invalid")
      );
      if (formMsg) formMsg.textContent = "";
      updateWeightInfo();
    });
  }

  // submit form & validasi 
  if (form && submitBtn) {
    form.addEventListener("submit", (e) => {
      formMsg.textContent = "";

      // sinkron semua numeric
      form.querySelectorAll(".numeric-input").forEach((inp) =>
        syncNumericInput(inp)
      );

      // cek minimal 2 alternatif
      const rows = altsBody ? altsBody.querySelectorAll(".alt-row") : [];
      if (rows.length < 2) {
        e.preventDefault();
        formMsg.textContent = "Minimal harus ada 2 alternatif.";
        formMsg.className = "text-sm text-red-400";
        return;
      }

      let hasError = false;
      form.querySelectorAll("input[required]").forEach((inp) => {
        if (!inp.value) {
          hasError = true;
          inp.classList.add("input-invalid");
        } else {
          inp.classList.remove("input-invalid");
        }
      });

      if (hasError) {
        e.preventDefault();
        formMsg.textContent = "Masih ada isian yang kosong / tidak valid.";
        formMsg.className = "text-sm text-red-400";
        return;
      }

      // cek total bobot di sisi client
      let total = 0;
      weightInputs.forEach((inp) => {
        const v = parseFloat(inp.value);
        if (!isNaN(v)) total += v;
      });
      if (Math.abs(total - 100) > 1) {
        e.preventDefault();
        formMsg.textContent =
          "Total bobot harus 100%. Sekarang " + total.toFixed(2) + "%.";
        formMsg.className = "text-sm text-red-400";
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Menghitung...";
    });
  }
});
