
from flask import Flask, request, send_file, render_template
import re
import pandas as pd
from PyPDF2 import PdfReader
import io
import os

app = Flask(__name__)

def procesar_pdf(file_stream):
    reader = PdfReader(file_stream)
    resultados = {}

    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue

        cliente_match = re.search(r"Linea Aerea:\*\*(.*?)\*\*", text)
        if cliente_match:
            cliente = cliente_match.group(1).strip()
        else:
            continue

        total_match = re.search(r"Total General\s+([\d,]+\.\d+)", text)
        if total_match:
            total = float(total_match.group(1).replace(",", ""))
        else:
            continue

        resultados[cliente] = resultados.get(cliente, 0) + total

    df = pd.DataFrame(list(resultados.items()), columns=["Cliente", "Total USD"])
    return df


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        df = procesar_pdf(file)

        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return send_file(
            output,
            download_name="resumen_clientes.xlsx",
            as_attachment=True
        )

    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



