import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Dados Base ---
pacientes_base = [
    {"id": 1, "nome": "Ana Silva", "data_nascimento": "1990-05-15", "genero": "Feminino", "contato": "ana.s@email.com"},
    {"id": 2, "nome": "Bruno Costa", "data_nascimento": "1985-11-22", "genero": "Masculino", "contato": "bruno.c@email.com"},
    {"id": 3, "nome": "Carla Dias", "data_nascimento": "1992-03-01", "genero": "Feminino", "contato": "carla.d@email.com"},
    {"id": 4, "nome": "Daniel Rocha", "data_nascimento": "1978-07-10", "genero": "Masculino", "contato": "daniel.r@email.com"},
    {"id": 5, "nome": "Eduarda Lima", "data_nascimento": "1995-08-20", "genero": "Feminino", "contato": "eduarda.l@email.com"},
    {"id": 6, "nome": "Felipe Souza", "data_nascimento": "1980-01-30", "genero": "Masculino", "contato": "felipe.s@email.com"},
    {"id": 7, "nome": "Gabriela Alves", "data_nascimento": "1988-04-12", "genero": "Feminino", "contato": "gabriela.a@email.com"},
    {"id": 8, "nome": "Hugo Pereira", "data_nascimento": "1975-09-05", "genero": "Masculino", "contato": "hugo.p@email.com"},
]

profissionais_base = [
    {"id": 101, "nome": "Dr. João Santos", "especialidade": "Clínico Geral", "contato": "joao.s@email.com"},
    {"id": 102, "nome": "Dra. Maria Lima", "especialidade": "Pediatra", "contato": "maria.l@email.com"},
    {"id": 103, "nome": "Dr. Pedro Alves", "especialidade": "Cardiologista", "contato": "pedro.a@email.com"},
    {"id": 104, "nome": "Dra. Laura Mendes", "especialidade": "Clínico Geral", "contato": "laura.m@email.com"},
    {"id": 105, "nome": "Dr. Ricardo Costa", "especialidade": "Ortopedista", "contato": "ricardo.c@email.com"},
    {"id": 106, "nome": "Dra. Sofia Nunes", "especialidade": "Ortopedista", "contato": "sofia.n@email.com"},
]

tipos_consulta_base = ["Rotina", "Pediátrica", "Cardiologia", "Clínico Geral", "Ortopedista"]
status_consulta_base = ["Realizada", "Agendada", "Cancelada"]
status_pagamento_base = ["Pago", "Pendente", "Glosado", "Estornado"]

# --- Geração de Dados Aleatórios ---
num_consultas_adicionais = 4000
data_inicio_periodo = datetime(2023, 1, 1)
data_fim_periodo = datetime(2026, 12, 31)

dados_finais = []
consulta_id_counter = 10000
pagamento_id_counter = 20000

for _ in range(num_consultas_adicionais):
    paciente = random.choice(pacientes_base)
    profissional = random.choice(profissionais_base)
    tipo_consulta = random.choice(tipos_consulta_base)
    status_consulta = random.choice(status_consulta_base)

    # Gerar data/hora aleatória
    time_delta = data_fim_periodo - data_inicio_periodo
    random_days = random.randint(0, time_delta.days)
    random_seconds = random.randint(0, 24 * 3600 - 1)
    data_hora_consulta = data_inicio_periodo + timedelta(days=random_days, seconds=random_seconds)

    # Gerar pagamento
    valor_pagamento = round(random.uniform(100.0, 500.0), 2)
    status_pagamento = random.choice(status_pagamento_base)
    data_pagamento = data_hora_consulta.date() # Data do pagamento é a mesma da consulta

    # Se a consulta foi cancelada ou glosada, o pagamento pode ser pendente/estornado
    if status_consulta == "Cancelada" and status_pagamento == "Pago":
        status_pagamento = random.choice(["Pendente", "Estornado"])
    if status_pagamento == "Glosado" and status_consulta == "Realizada":
        status_consulta = "Glosada" # Um status de consulta "Glosada" pode ser útil

    dados_finais.append({
        "id_consulta": consulta_id_counter,
        "id_paciente": paciente["id"],
        "nome_paciente": paciente["nome"],
        "data_nascimento_paciente": paciente["data_nascimento"],
        "genero_paciente": paciente["genero"],
        "contato_paciente": paciente["contato"],
        "id_profissional": profissional["id"],
        "nome_profissional": profissional["nome"],
        "especialidade_profissional": profissional["especialidade"],
        "contato_profissional": profissional["contato"],
        "data_hora_consulta": data_hora_consulta.isoformat(),
        "tipo_consulta": tipo_consulta,
        "status_consulta": status_consulta,
        "id_pagamento": pagamento_id_counter,
        "valor_pagamento": valor_pagamento,
        "data_pagamento": data_pagamento.isoformat(),
        "status_pagamento": status_pagamento,
    })
    consulta_id_counter += 1
    pagamento_id_counter += 1

# Criar DataFrame e salvar em CSV
df_final = pd.DataFrame(dados_finais)
df_final.to_csv("dados_saude.csv", index=False)

print(f"Arquivo 'dados_saude.csv' gerado com {len(df_final)} registros.")
