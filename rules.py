from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from services import listar_consultas, listar_pagamentos
from dashboard import formatar_data # Importar a nova função de formatação de data


def resumo_kpis(data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> Dict[str, Any]:
    consultas = listar_consultas()
    pagamentos = listar_pagamentos()

    # Parsear datas de filtro
    data_inicio_dt: Optional[datetime] = None
    data_fim_dt: Optional[datetime] = None

    if data_inicio:
        data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
    if data_fim:
        data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")

    # Filtrar consultas e pagamentos pelo período
    consultas_filtradas = []
    for c in consultas:
        consulta_data_hora = datetime.fromisoformat(c.data_hora)
        if (data_inicio_dt is None or consulta_data_hora >= data_inicio_dt) and \
           (data_fim_dt is None or consulta_data_hora <= (data_fim_dt + timedelta(days=1, microseconds=-1))):
            consultas_filtradas.append(c)

    pagamentos_filtrados = []
    for p in pagamentos:
        pagamento_data = datetime.fromisoformat(p.data_pagamento).date()
        if (data_inicio_dt is None or pagamento_data >= data_inicio_dt.date()) and \
           (data_fim_dt is None or pagamento_data <= data_fim_dt.date()):
            pagamentos_filtrados.append(p)

    # --- Cálculos de KPIs ---

    # Receita Total
    receita_total = sum(p.valor for p in pagamentos_filtrados if p.status == "Pago")

    # Volume de Consultas por Tipo
    volume_por_tipo: Dict[str, int] = {}
    for c in consultas_filtradas:
        volume_por_tipo[c.tipo_consulta] = volume_por_tipo.get(c.tipo_consulta, 0) + 1

    # Receita e Ticket Médio por Tipo
    receita_por_tipo: Dict[str, float] = {}
    contagem_por_tipo: Dict[str, int] = {}
    for p in pagamentos_filtrados:
        if p.status == "Pago":
            consulta_associada = next((c for c in consultas_filtradas if c.id == p.id_consulta), None)
            if consulta_associada:
                receita_por_tipo[consulta_associada.tipo_consulta] = receita_por_tipo.get(consulta_associada.tipo_consulta, 0.0) + p.valor
                contagem_por_tipo[consulta_associada.tipo_consulta] = contagem_por_tipo.get(consulta_associada.tipo_consulta, 0) + 1

    ticket_medio_por_tipo: Dict[str, float] = {
        tipo: receita_por_tipo[tipo] / contagem_por_tipo[tipo]
        for tipo in receita_por_tipo if contagem_por_tipo[tipo] > 0
    }

    # Taxa de Cancelamento e Glosa
    total_consultas = len(consultas_filtradas)
    canceladas = sum(1 for c in consultas_filtradas if c.status == "Cancelada")
    glosadas = sum(1 for p in pagamentos_filtrados if p.status == "Glosado") # Glosa é um status de pagamento

    taxa_cancelamento = (canceladas / total_consultas * 100) if total_consultas > 0 else 0
    taxa_glosa = (glosadas / total_consultas * 100) if total_consultas > 0 else 0 # Glosa sobre total de consultas
    taxa_cancelamento_glosa = taxa_cancelamento + taxa_glosa

    # Saldo Financeiro por Período (Mês)
    saldo_por_periodo: Dict[str, Dict[str, Any]] = {}
    for p in pagamentos_filtrados:
        pagamento_data = datetime.fromisoformat(p.data_pagamento).date()
        periodo_str = pagamento_data.strftime("%Y-%m") # Formato YYYY-MM

        if periodo_str not in saldo_por_periodo:
            saldo_por_periodo[periodo_str] = {
                "periodo": periodo_str,
                "receita_recebida": 0.0,
                "perdas_glosa_estorno": 0.0,
                "saldo": 0.0,
                "qtd_pagamentos": 0,
            }

        saldo_por_periodo[periodo_str]["qtd_pagamentos"] += 1

        if p.status == "Pago":
            saldo_por_periodo[periodo_str]["receita_recebida"] += p.valor
            saldo_por_periodo[periodo_str]["saldo"] += p.valor
        elif p.status in ["Glosado", "Estornado"]:
            saldo_por_periodo[periodo_str]["perdas_glosa_estorno"] += p.valor
            saldo_por_periodo[periodo_str]["saldo"] -= p.valor

    # Ordenar por período e formatar a string do período
    saldo_ordenado = sorted(saldo_por_periodo.values(), key=lambda x: x["periodo"])
    for item in saldo_ordenado:
        item["periodo"] = formatar_data(item["periodo"], "%m/%Y") # <--- MUDANÇA AQUI: Formata para MM/AAAA

    return {
        "receita_total": receita_total,
        "volume_por_tipo": volume_por_tipo,
        "receita_por_tipo": receita_por_tipo,
        "ticket_medio_por_tipo": ticket_medio_por_tipo,
        "taxa_cancelamento_glosa": {
            "total_consultas": total_consultas,
            "canceladas": canceladas,
            "taxa_cancelamento_%": taxa_cancelamento,
            "glosadas": glosadas,
            "taxa_glosa_%": taxa_glosa,
            "taxa_cancelamento_glosa_%": taxa_cancelamento_glosa,
        },
        "saldo_por_periodo": saldo_ordenado,
    }
