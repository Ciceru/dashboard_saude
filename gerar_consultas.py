import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path("dados")
BASE.mkdir(exist_ok=True)

TOTAL = 10000

procedimentos = [
    "Consulta Clínica",
    "Retorno",
    "Eletrocardiograma",
    "Ultrassom",
    "Exame Laboratorial",
    "Avaliação Médica",
    "Raio-X"
]

inicio = datetime(2024, 1, 1)

with open(BASE / "consultas.csv", "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "id",
        "paciente_id",
        "profissional_id",
        "data",
        "tipo",
        "procedimento",
        "valor",
        "status"
    ])

    for i in range(1, TOTAL + 1):

        tipo = random.choices(
            ["SUS", "Particular", "Convênio"],
            weights=[37, 14, 49],
            k=1
        )[0]

        status = random.choices(
            ["realizada", "cancelada", "glosada"],
            weights=[79, 11, 10],
            k=1
        )[0]

        if tipo == "SUS":
            valor = round(random.uniform(70, 100), 2)
        elif tipo == "Particular":
            valor = round(random.uniform(250, 500), 2)
        else:
            valor = round(random.uniform(180, 350), 2)

        data = inicio + timedelta(
            days=random.randint(0, 730)
        )

        writer.writerow([
            i,
            random.randint(1, 3000),
            random.randint(1, 100),
            data.strftime("%Y-%m-%d"),
            tipo,
            random.choice(procedimentos),
            valor,
            status
        ])

print("consultas.csv gerado com sucesso.")