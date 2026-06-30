// app.js — Lógica do dashboard front-end
// Lê o dados.json gerado pelo Python e monta os gráficos e tabelas.

// ── Variáveis globais ──
let dadosOriginais = null;   // dados completos vindos do JSON
let graficoPizza  = null;    // instância do gráfico de pizza (Chart.js)
let graficoBarras = null;    // instância do gráfico de barras (Chart.js)

// ── Cores por tipo de convênio ──
const CORES = {
  SUS:        { fundo: "#dbeafe", borda: "#1d4ed8" },
  Particular: { fundo: "#dcfce7", borda: "#15803d" },
  Convênio:   { fundo: "#fef9c3", borda: "#854d0e" },
};

const CORES_GRAFICO = {
  SUS:        "#4a90d9",
  Particular: "#27ae60",
  Convênio:   "#f39c12",
};


// ================================================================
// 1. CARREGAR DADOS DO JSON
// ================================================================

async function carregarDados() {
  try {
    // Busca o arquivo dados.json gerado pelo Python
    const resposta = await fetch("dados.json");

    if (!resposta.ok) {
      throw new Error(`Arquivo não encontrado (${resposta.status})`);
    }

    dadosOriginais = await resposta.json();
    atualizarStatus("Dados carregados com sucesso.");
    renderizarTudo(dadosOriginais);
    popularFiltroMes(dadosOriginais);

  } catch (erro) {
    atualizarStatus(`Erro ao carregar dados: ${erro.message}. Rode python main.py → opção 6 primeiro.`);
    console.error(erro);
  }
}


// ================================================================
// 2. RENDERIZAR TUDO (chamado ao carregar e ao filtrar)
// ================================================================

function renderizarTudo(dados) {
  atualizarKPIs(dados);
  atualizarGraficoPizza(dados);
  atualizarGraficoBarras(dados);
  atualizarTabela(dados);
}


// ================================================================
// 3. CARDS DE KPI
// ================================================================

function atualizarKPIs(dados) {
  const vol  = dados.volume;
  const rec  = dados.receita;
  const canc = dados.cancelamento;

  definirTexto("kpi-total",       vol.total);
  definirTexto("kpi-receita",     formatarMoeda(rec.geral.total));
  definirTexto("kpi-ticket",      formatarMoeda(rec.geral.ticket_medio));
  definirTexto("kpi-cancelamento", canc.taxa_cancelamento + "%");
}


// ================================================================
// 4. GRÁFICO DE PIZZA — Volume por tipo
// ================================================================

function atualizarGraficoPizza(dados) {
  const vol    = dados.volume;
  const labels = ["SUS", "Particular", "Convênio"];
  const values = [vol.SUS, vol.Particular, vol["Convênio"]];
  const cores  = labels.map(t => CORES_GRAFICO[t]);

  const ctx = document.getElementById("grafico-pizza").getContext("2d");

  // Destrói o gráfico anterior antes de criar um novo (evita duplicação)
  if (graficoPizza) graficoPizza.destroy();

  graficoPizza = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: cores,
        borderWidth: 2,
        borderColor: "#fff",
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 13 } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.raw} consultas`
          }
        }
      }
    }
  });
}


// ================================================================
// 5. GRÁFICO DE BARRAS — Receita por mês
// ================================================================

function atualizarGraficoBarras(dados) {
  const saldo  = dados.saldo_mes || {};
  const meses  = Object.keys(saldo);
  const values = meses.map(m => saldo[m].receita);

  const ctx = document.getElementById("grafico-barras").getContext("2d");

  if (graficoBarras) graficoBarras.destroy();

  graficoBarras = new Chart(ctx, {
    type: "bar",
    data: {
      labels: meses,
      datasets: [{
        label: "Receita (R$)",
        data: values,
        backgroundColor: "#4a90d9",
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` R$ ${ctx.raw.toFixed(2)}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: val => "R$ " + val.toLocaleString("pt-BR")
          }
        }
      }
    }
  });
}


// ================================================================
// 6. TABELA DE GARGALOS
// ================================================================

function atualizarTabela(dados) {
  const rec  = dados.receita;
  const canc = dados.cancelamento;
  const vol  = dados.volume;
  const corpo = document.getElementById("tabela-corpo");
  const perdas = dados.perdas_por_tipo || {};

  const tipos = ["SUS", "Particular", "Convênio"];
  let html = "";

  tipos.forEach(tipo => {
    const r = rec[tipo];
    const badgeClass = {
      SUS: "badge-sus", Particular: "badge-particular", Convênio: "badge-convenio"
    }[tipo];

    // Calcula canceladas/glosadas por tipo (aproximação proporcional)
    const total  = vol[tipo] || 0;
    const realiz = r.quantidade;

    const cancel = perdas[tipo]?.canceladas || 0;
    const glosa  = perdas[tipo]?.glosadas || 0;

    const classeAlerta =
      (cancel > 0 || glosa > 0)
        ? "celula-alerta"
        : "";

    html += `
      <tr>
        <td><span class="badge ${badgeClass}">${tipo}</span></td>
        <td>${realiz}</td>
       <td class="${cancel > 0 ? 'celula-alerta' : ''}">
          ${cancel}
      </td>

    <td class="${glosa > 0 ? 'celula-alerta' : ''}">
        ${glosa}
    </td>
        <td>R$ ${r.total.toFixed(2)}</td>
        <td>R$ ${r.ticket_medio.toFixed(2)}</td>
      </tr>`;
  });

  // Linha de totais
  html += `
    <tr style="font-weight:600; border-top: 2px solid #e8e8f0;">
      <td><span class="badge badge-geral">Total</span></td>
      <td>${canc.realizadas}</td>
      <td class="${canc.canceladas > 0 ? 'celula-alerta' : ''}">${canc.canceladas} (${canc.taxa_cancelamento}%)</td>
      <td class="${canc.glosadas > 0 ? 'celula-alerta' : ''}">${canc.glosadas} (${canc.taxa_glosa}%)</td>
      <td>R$ ${rec.geral.total.toFixed(2)}</td>
      <td>R$ ${rec.geral.ticket_medio.toFixed(2)}</td>
    </tr>`;

  corpo.innerHTML = html;
}


// ================================================================
// 7. FILTROS
// ================================================================

function popularFiltroMes(dados) {
  const saldo  = dados.saldo_mes || {};
  const select = document.getElementById("filtro-mes");

  Object.keys(saldo).forEach(mes => {
    const op = document.createElement("option");
    op.value = mes;
    op.textContent = mes;
    select.appendChild(op);
  });
}

document.getElementById("btn-atualizar").addEventListener("click", () => {
  if (!dadosOriginais) return;

  const tipo = document.getElementById("filtro-tipo").value;
  const mes  = document.getElementById("filtro-mes").value;

  // Filtra os dados originais conforme seleção
  let dadosFiltrados = JSON.parse(JSON.stringify(dadosOriginais)); // cópia profunda

  // Filtro por tipo: zera os outros tipos nos KPIs
  if (tipo !== "todos") {
    const tiposZerados = ["SUS", "Particular", "Convênio"].filter(t => t !== tipo);
    tiposZerados.forEach(t => {
      dadosFiltrados.volume[t] = 0;
      dadosFiltrados.receita[t] = { total: 0, quantidade: 0, ticket_medio: 0 };
    });
    dadosFiltrados.volume.total    = dadosOriginais.volume[tipo];
    dadosFiltrados.receita.geral   = dadosOriginais.receita[tipo];
  }

  // Filtro por mês: mantém só aquele mês no saldo
  if (mes !== "todos") {
    const saldoCompleto = dadosOriginais.saldo_mes || {};
    dadosFiltrados.saldo_mes = {};
    if (saldoCompleto[mes]) {
      dadosFiltrados.saldo_mes[mes] = saldoCompleto[mes];
    }
  }

  renderizarTudo(dadosFiltrados);
  atualizarStatus(`Filtro aplicado: tipo=${tipo}, mês=${mes}`);
});


// ================================================================
// UTILITÁRIOS
// ================================================================

function formatarMoeda(valor) {
  return "R$ " + Number(valor).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function definirTexto(id, texto) {
  const el = document.getElementById(id);
  if (el) el.textContent = texto;
}

function atualizarStatus(msg) {
  const agora = new Date().toLocaleTimeString("pt-BR");
  definirTexto("status-msg", `${agora} — ${msg}`);
}


// ── Inicia ao carregar a página ──
carregarDados();
