# storage.py — Lê e salva dados nos arquivos CSV.
# Usa caminhos absolutos para funcionar de qualquer lugar.

import csv
import os

_BASE       = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(_BASE, "dados")

ARQUIVO_PACIENTES     = os.path.join(PASTA_DADOS, "pacientes.csv")
ARQUIVO_PROFISSIONAIS = os.path.join(PASTA_DADOS, "profissionais.csv")
ARQUIVO_CONSULTAS     = os.path.join(PASTA_DADOS, "consultas.csv")
ARQUIVO_PAGAMENTOS    = os.path.join(PASTA_DADOS, "pagamentos.csv")

def garantir_pasta():
    os.makedirs(PASTA_DADOS, exist_ok=True)

def _ler_csv(caminho):
    if not os.path.exists(caminho):
        return []
    try:
        with open(caminho, mode="r", encoding="utf-8") as f:
            return [dict(r) for r in csv.DictReader(f)]
    except Exception as e:
        print(f"  Erro ao ler '{caminho}': {e}")
        return []

def _escrever_csv(caminho, lista, colunas):
    garantir_pasta()
    try:
        with open(caminho, mode="w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore")
            w.writeheader()
            w.writerows(lista)
    except Exception as e:
        print(f"  Erro ao salvar '{caminho}': {e}")

def carregar_pacientes():
    return _ler_csv(ARQUIVO_PACIENTES)

def carregar_profissionais():
    return _ler_csv(ARQUIVO_PROFISSIONAIS)

def carregar_consultas():
    registros = _ler_csv(ARQUIVO_CONSULTAS)
    for r in registros:
        try:
            r["id"]              = int(r["id"])
            r["paciente_id"]     = int(r["paciente_id"])
            r["profissional_id"] = int(r["profissional_id"])
            r["valor"]           = float(r["valor"])
        except (ValueError, KeyError):
            pass
    return registros

def carregar_pagamentos():
    registros = _ler_csv(ARQUIVO_PAGAMENTOS)
    for r in registros:
        try:
            r["id"]          = int(r["id"])
            r["consulta_id"] = int(r["consulta_id"])
            r["valor_pago"]  = float(r["valor_pago"])
        except (ValueError, KeyError):
            pass
    return registros

def salvar_pacientes(lista):
    _escrever_csv(ARQUIVO_PACIENTES, lista,
                  ["id","nome","data_nascimento","cpf","convenio","telefone"])

def salvar_profissionais(lista):
    _escrever_csv(ARQUIVO_PROFISSIONAIS, lista,
                  ["id","nome","especialidade","crm"])

def salvar_consultas(lista):
    _escrever_csv(ARQUIVO_CONSULTAS, lista,
                  ["id","paciente_id","profissional_id","data","tipo",
                   "procedimento","valor","status"])

def salvar_pagamentos(lista):
    _escrever_csv(ARQUIVO_PAGAMENTOS, lista,
                  ["id","consulta_id","data_pagamento","valor_pago","forma"])
