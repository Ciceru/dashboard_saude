from __future__ import annotations

from datetime import date, datetime
from typing import Any
import locale

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, State, dcc, html
from dateutil.relativedelta import relativedelta

from dashboard import formatar_moeda, formatar_percentual
from rules import resumo_kpis
from services import get_min_max_dates, listar_consultas


app = Dash(__name__)
server = app.server

min_date_data, max_date_data = get_min_max_dates()

if min_date_data is None or max_date_data is None:
    hoje = date.today()
    min_date_data = hoje
    max_date_data = hoje

TIPOS_CONSULTA = sorted({c.tipo_consulta for c in listar_consultas()})


def get_month_year_options(min_dt: date, max_dt: date) -> list[dict]:
    options = []
    current_dt = min_dt.replace(day=1)
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "pt_BR")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, "Portuguese_Brazil")
            except locale.Error:
                pass
    while current_dt <= max_dt:
        options.append({
            "label": current_dt.strftime("%B %Y").capitalize(),
            "value": current_dt.strftime("%Y-%m"),
        })
        current_dt += relativedelta(months=1)
    return options


MONTH_YEAR_OPTIONS = get_month_year_options(min_date_data, max_date_data)


TEMA = {
    "fundo_geral": "linear-gradient(180deg, #003366 0%, #005A8D 50%, #E0F2F7 100%)",
    "painel": "rgba(255, 255, 255, 0.95)",
    "borda_painel": "#66B2FF",
    "card": "#FFFFFF",
    "card_borda": "#00B050",
    "titulo": "#005A8D",
    "texto": "#212529",
    "texto_secundario": "#6C757D",
    "botao": "#00B050",
    "cabecalho_tabela": "#005A8D",
    "linha_tabela": "#F8F9FA",
    "sombra": "0 20px 60px rgba(0, 51, 102, 0.25)",
    "periodo_cor": "#00B050",
}


def _estilo_painel() -> dict:
    return {
        "backgroundColor": TEMA["card"],
        "border": f"1px solid {TEMA[chr(99)+chr(97)+chr(114)+chr(100)+'_borda']}",
        "borderRadius": "16px",
        "padding": "18px",
        "marginTop": "18px",
        "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.08)",
    }


def _borda_card():
    return TEMA["card_borda"]


def _estilo_painel_v2() -> dict:
    return {
        "backgroundColor": TEMA["card"],
        "border": "1px solid " + TEMA["card_borda"],
        "borderRadius": "16px",
        "padding": "18px",
        "marginTop": "18px",
        "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.08)",
    }


def card_kpi(titulo: str, valor: Any) -> html.Div:
    return html.Div(
        [
            html.Div(titulo, style={
                "fontSize": "13px",
                "color": TEMA["titulo"],
                "fontWeight": "bold",
                "marginBottom": "10px",
            }),
            html.Div(str(valor), style={
                "fontSize": "22px",
                "fontWeight": "bold",
                "color": TEMA["texto"],
            }),
        ],
        style={
            "backgroundColor": TEMA["card"],
            "border": "2px solid " + TEMA["card_borda"],
            "borderRadius": "16px",
            "padding": "16px",
            "minWidth": "220px",
            "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.12)",
        },
    )


def tabela_html(titulo: str, colunas: list, linhas: list) -> html.Div:
    if linhas:
        corpo_linhas = []
        for i, linha in enumerate(linhas):
            fundo = TEMA["linha_tabela"] if i % 2 == 0 else "#FFFFFF"
            corpo_linhas.append(html.Tr([
                html.Td(valor, style={
                    "padding": "10px 12px",
                    "borderBottom": "1px solid #D1D5DB",
                    "backgroundColor": fundo,
                    "color": TEMA["texto"],
                })
                for valor in linha
            ]))
        corpo = html.Tbody(corpo_linhas)
    else:
        corpo = html.Tbody([html.Tr([html.Td(
            "Sem dados para exibir",
            colSpan=len(colunas),
            style={
                "padding": "12px",
                "textAlign": "center",
                "color": TEMA["texto_secundario"],
                "backgroundColor": "#FFFFFF",
            },
        )])])

    cabecalho = html.Thead(html.Tr([
        html.Th(col, style={
            "backgroundColor": TEMA["cabecalho_tabela"],
            "color": "white",
            "padding": "12px",
            "textAlign": "left",
            "borderBottom": "2px solid " + TEMA["card_borda"],
        })
        for col in colunas
    ]))

    return html.Div(
        [
            html.H3(titulo, style={
                "marginBottom": "12px",
                "color": TEMA["titulo"],
                "fontWeight": "bold",
            }),
            html.Div(
                html.Table([cabecalho, corpo], style={
                    "width": "100%",
                    "borderCollapse": "collapse",
                    "borderRadius": "12px",
                    "overflow": "hidden",
                }),
                style={"overflowX": "auto"},
            ),
        ],
        style=_estilo_painel_v2(),
    )


def grafico_pizza(receita_por_tipo: dict) -> html.Div:
    cores = ["#00B050", "#66B2FF", "#005A8D", "#FFD700", "#FF6347", "#8A2BE2"]
    tipos = list(receita_por_tipo.keys())
    valores = list(receita_por_tipo.values())
    fig = go.Figure()
    if not tipos:
        return html.Div("Sem dados para o periodo.", style={
            "padding": "18px",
            "color": TEMA["texto_secundario"],
            "textAlign": "center",
        })
    fig.add_trace(go.Pie(
        labels=tipos,
        values=valores,
        hole=0.5,
        marker={"colors": cores[:len(tipos)]},
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Receita: R$ %{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title_text="Distribuicao de receita por tipo de consulta",
        title_x=0.5,
        title_font={"color": TEMA["titulo"], "size": 17},
        height=340,
        margin={"l": 100, "r": 10, "t": 50, "b": 10},
        paper_bgcolor="white",
        showlegend=True,
        legend={"orientation": "v", "x": -0.1, "y": 0.5, "xanchor": "left",
                "yanchor": "middle", "font": {"size": 14, "color": TEMA["texto"]}},
        font={"color": TEMA["texto"], "size": 14},
    )
    return html.Div(
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}),
        style=_estilo_painel_v2(),
    )


def grafico_receita_ticket(receita_por_tipo, ticket_medio_por_tipo, tipos_selecionados):
    tipos_base = tipos_selecionados or TIPOS_CONSULTA
    tipos = [t for t in TIPOS_CONSULTA if t in tipos_base]
    if not tipos:
        return html.Div("Sem dados disponiveis.", style={"padding": "18px", "color": TEMA["texto_secundario"]})

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=tipos,
        y=[receita_por_tipo.get(t, 0) for t in tipos],
        name="Receita total",
        marker_color=TEMA["periodo_cor"],
        offsetgroup=0,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=tipos,
        y=[ticket_medio_por_tipo.get(t, 0) for t in tipos],
        name="Ticket medio",
        mode="lines+markers",
        line={"color": "#66B2FF", "width": 3},
        marker={"size": 9},
    ), secondary_y=True)
    fig.update_layout(
        barmode="group", height=430,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        paper_bgcolor="white", plot_bgcolor="white",
        legend={"orientation": "h", "y": 1.15, "x": 0, "font": {"size": 14}},
        font={"color": TEMA["texto"], "size": 14},
    )
    fig.update_xaxes(title_text="Tipo de consulta", title_font={"size": 14}, tickfont={"size": 12})
    fig.update_yaxes(title_text="Receita total (R$)", secondary_y=False,
                     tickprefix="R$ ", rangemode="tozero", title_font={"size": 14}, tickfont={"size": 12})
    fig.update_yaxes(title_text="Ticket medio (R$)", secondary_y=True,
                     tickprefix="R$ ", rangemode="tozero", title_font={"size": 14}, tickfont={"size": 12})
    return html.Div(
        [
            html.H3("Receita total e ticket medio por tipo", style={"marginBottom": "8px", "color": TEMA["titulo"], "fontWeight": "bold"}),
            html.Div("Barras = receita total | Linha = ticket medio.", style={"marginBottom": "14px", "color": TEMA["texto_secundario"], "fontSize": "13px"}),
            dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True}, style={"height": "470px"}),
        ],
        style=_estilo_painel_v2(),
    )


def _dropdown_mes_ano(id_dropdown: str, label: str) -> html.Div:
    return html.Div(
        [
            html.Label(label, style={
                "display": "block", "marginBottom": "8px",
                "color": TEMA["periodo_cor"], "fontWeight": "bold", "fontSize": "14px",
            }),
            dcc.Dropdown(
                id=id_dropdown,
                options=MONTH_YEAR_OPTIONS,
                value=MONTH_YEAR_OPTIONS[0]["value"] if id_dropdown == "mes-ano-inicio" else MONTH_YEAR_OPTIONS[-1]["value"],
                clearable=False,
                searchable=False,
                style={"color": TEMA["texto"]},
            ),
        ],
        style={"flex": "1 1 200px"},
    )


def _secao_filtros() -> html.Div:
    return html.Div(
        [
            _dropdown_mes_ano("mes-ano-inicio", "Mes/Ano Inicial"),
            _dropdown_mes_ano("mes-ano-fim", "Mes/Ano Final"),
            html.Div(
                [html.Button(
                    "Atualizar dashboard",
                    id="btn-atualizar",
                    n_clicks=0,
                    style={
                        "padding": "12px 18px", "cursor": "pointer",
                        "border": "none", "borderRadius": "12px",
                        "backgroundColor": TEMA["botao"], "color": "white",
                        "fontWeight": "bold", "width": "100%",
                        "boxShadow": "0 6px 16px rgba(5, 150, 105, 0.28)",
                    },
                )],
                style={"flex": "0 0 200px", "display": "flex", "alignItems": "end"},
            ),
        ],
        style={"display": "flex", "flexWrap": "wrap", "gap": "16px", "alignItems": "end", "marginBottom": "20px"},
    )


def _secao_filtro_tipo() -> html.Div:
    return html.Div(
        [
            html.Label("Filtro por tipo de consulta", style={
                "display": "block", "marginBottom": "8px",
                "color": TEMA["texto"], "fontWeight": "bold",
            }),
            dcc.Dropdown(
                id="filtro-tipos-receita",
                options=[{"label": t, "value": t} for t in TIPOS_CONSULTA],
                value=TIPOS_CONSULTA,
                multi=True,
                placeholder="Selecione os tipos de consulta...",
                style={"color": TEMA["texto"]},
            ),
        ],
        style={
            "backgroundColor": "#FFFFFF",
            "border": "1px solid " + TEMA["card_borda"],
            "borderRadius": "16px", "padding": "16px", "marginBottom": "18px",
            "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.08)",
        },
    )


app.layout = html.Div(
    [html.Div(
        [
            html.H1("Dashboard de Gestao em Saude", style={
                "marginBottom": "8px", "color": TEMA["titulo"],
                "fontSize": "34px", "fontWeight": "bold",
            }),
            html.Div("Analise financeira e operacional - SUS", style={
                "color": TEMA["texto_secundario"], "marginBottom": "24px", "fontSize": "15px",
            }),
            _secao_filtros(),
            _secao_filtro_tipo(),
            html.Div(id="cards-kpi", style={"display": "flex", "flexWrap": "wrap", "gap": "14px", "marginBottom": "6px"}),
            html.Div(id="sec-pizza"),
            html.Div(id="sec-receita"),
            html.Div(id="sec-volume"),
            html.Div(id="sec-taxa"),
            html.Div(id="sec-saldo"),
            html.Div(id="mensagem-erro", style={"color": "#B91C1C", "fontWeight": "bold", "marginTop": "20px"}),
        ],
        style={
            "maxWidth": "1200px", "margin": "0 auto", "padding": "28px",
            "backgroundColor": TEMA["painel"],
            "border": "1px solid " + TEMA["borda_painel"],
            "borderRadius": "24px", "boxShadow": TEMA["sombra"],
        },
    )],
    style={
        "minHeight": "100vh", "padding": "24px",
        "background": TEMA["fundo_geral"], "fontFamily": "Arial, sans-serif",
    },
)


@app.callback(
    Output("cards-kpi", "children"),
    Output("sec-pizza", "children"),
    Output("sec-receita", "children"),
    Output("sec-volume", "children"),
    Output("sec-taxa", "children"),
    Output("sec-saldo", "children"),
    Output("mensagem-erro", "children"),
    Input("btn-atualizar", "n_clicks"),
    Input("filtro-tipos-receita", "value"),
    State("mes-ano-inicio", "value"),
    State("mes-ano-fim", "value"),
)
def atualizar_dashboard(n_clicks, tipos_selecionados, mes_ano_inicio, mes_ano_fim):
    try:
        if isinstance(tipos_selecionados, str):
            tipos_selecionados = [tipos_selecionados]
        if not tipos_selecionados:
            tipos_selecionados = TIPOS_CONSULTA

        start_obj = None
        end_obj = None
        if mes_ano_inicio:
            start_obj = datetime.strptime(mes_ano_inicio, "%Y-%m").date()
        if mes_ano_fim:
            end_obj = (datetime.strptime(mes_ano_fim, "%Y-%m") + relativedelta(months=1, days=-1)).date()

        start_str = start_obj.strftime("%Y-%m-%d") if start_obj else None
        end_str = end_obj.strftime("%Y-%m-%d") if end_obj else None

        kpis = resumo_kpis(data_inicio=start_str, data_fim=end_str)

        total_c = kpis["taxa_cancelamento_glosa"]["total_consultas"]
        taxa_c = kpis["taxa_cancelamento_glosa"]["taxa_cancelamento_glosa_%"]
        saldo_t = sum(i["saldo"] for i in kpis["saldo_por_periodo"])

        cards = [
            card_kpi("Receita total", formatar_moeda(kpis["receita_total"])),
            card_kpi("Total de consultas", total_c),
            card_kpi("Taxa cancel./glosa", formatar_percentual(taxa_c)),
            card_kpi("Saldo total", formatar_moeda(saldo_t)),
        ]

        volume_linhas = [[t, q] for t, q in kpis["volume_por_tipo"].items()]

        taxa = kpis["taxa_cancelamento_glosa"]
        taxa_linhas = [
            ["Total de consultas", taxa["total_consultas"]],
            ["Canceladas", f'{taxa["canceladas"]} ({formatar_percentual(taxa["taxa_cancelamento_%"])})'],
            ["Glosadas", f'{taxa["glosadas"]} ({formatar_percentual(taxa["taxa_glosa_%"])})'],
            ["Taxa combinada", formatar_percentual(taxa["taxa_cancelamento_glosa_%"])],
        ]

        saldo_linhas = [
            [i["periodo"], formatar_moeda(i["receita_recebida"]),
             formatar_moeda(i["perdas_glosa_estorno"]), formatar_moeda(i["saldo"]), i["qtd_pagamentos"]]
            for i in kpis["saldo_por_periodo"]
        ]

        return (
            cards,
            grafico_pizza(kpis["receita_por_tipo"]),
            grafico_receita_ticket(kpis["receita_por_tipo"], kpis["ticket_medio_por_tipo"], tipos_selecionados),
            tabela_html("Volume de consultas por tipo", ["Tipo", "Quantidade"], volume_linhas),
            tabela_html("Taxa de cancelamento e glosa", ["Indicador", "Valor"], taxa_linhas),
            tabela_html("Saldo financeiro por periodo", ["Periodo", "Receita recebida", "Perdas", "Saldo", "Qtd. pagamentos"], saldo_linhas),
            "",
        )

    except Exception as exc:
        return [], html.Div(), html.Div(), html.Div(), html.Div(), html.Div(), f"Erro ao carregar dashboard: {exc}"


if __name__ == "__main__":
    app.run(debug=True)
