from flask import Flask, render_template_string, jsonify, request
from database import inicializar_db, obter_tickers_b3, listar_noticias, buscar_estatisticas, DB_FILE
from hierarquia import construir_arvore_b3
from termometro_modulo import calcular_termometro_b3
from termometro import calcular_termometro_global
import sqlite3
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = "truffle_finder_v35_hierarquia"
inicializar_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truffle Finder v3.5 | Terminal Institucional B3</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --accent-blue: #3b82f6;
            --border-color: #334155;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg-color); color: var(--text-primary); margin: 0; display: flex; height: 100vh; overflow: hidden; }
        aside { width: 260px; background-color: #090d16; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; justify-content: space-between; padding: 20px; }
        .logo { font-size: 18px; font-weight: bold; color: #38bdf8; margin-bottom: 30px; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; flex-direction: column; gap: 8px; }
        .nav-links button { background: transparent; color: var(--text-secondary); border: none; text-align: left; padding: 10px 12px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px; }
        .nav-links button:hover, .nav-links button.active { background-color: var(--card-bg); color: var(--text-primary); }
        .user-profile { background: var(--card-bg); padding: 12px; border-radius: 6px; font-size: 12px; border: 1px solid var(--border-color); }
        main { flex: 1; padding: 30px; overflow-y: auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 25px; }
        h2 { margin: 0; font-size: 22px; color: #38bdf8; }
        .controls { display: flex; gap: 10px; align-items: center; }
        button, select { background-color: var(--card-bg); color: var(--text-primary); border: 1px solid var(--border-color); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; }
        button:hover { background-color: #334155; }
        button.primary { background-color: #0284c7; border-color: #0369a1; }
        .grid-container { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 25px; }
        .card { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h3 { margin-top: 0; color: #38bdf8; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
        .news-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        .news-table th, .news-table td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border-color); }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .badge-pos { background-color: rgba(34, 197, 94, 0.2); color: var(--accent-green); }
        .badge-neg { background-color: rgba(239, 68, 68, 0.2); color: var(--accent-red); }
        .badge-neu { background-color: rgba(148, 163, 184, 0.2); color: var(--text-secondary); }
        .chart-container { position: relative; height: 300px; width: 100%; }
        .period-selector { display: flex; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
        .period-btn { background-color: var(--card-bg); color: var(--text-secondary); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
        .period-btn.active { background-color: #0284c7; color: white; border-color: #0369a1; }
        .macro-setor { background: #090d16; border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .subsetor-box { margin-left: 20px; margin-top: 10px; border-left: 2px solid #3b82f6; padding-left: 15px; }
        .ticker-pill { display: inline-block; background: #1e293b; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; margin: 4px; font-size: 12px; cursor: pointer; }
        .ticker-pill:hover { background: #0284c7; color: white; }
    </style>
</head>
<body>
    <aside>
        <div>
            <div class="logo">🐷 TRUFFLE FINDER <span style="font-size: 10px; color: #38bdf8; margin-left: auto;">v3.5</span></div>
            <div class="nav-links">
                <button onclick="mudarAba('dashboard')" id="nav-dashboard" class="active">📊 Dashboard Executivo</button>
                <button onclick="mudarAba('hierarquia')" id="nav-hierarquia">🌳 Árvore Setorial (B3)</button>
                <button onclick="mudarAba('preferencias')" id="nav-preferencias">⭐ Meus Ativos & Setores</button>
                <button onclick="mudarAba('tendencia')" id="nav-tendencia">📈 Algoritmo Preditivo & EMA</button>
                <button onclick="mudarAba('hitl')" id="nav-hitl" style="color: #38bdf8; border-left: 3px solid #38bdf8;">🧪 Teste de Realidade (HITL)</button>
            </div>
        </div>
        <div class="user-profile">
            <div style="margin-bottom: 5px; color: #38bdf8; font-weight: bold;">Perfil: 👑 Administrador</div>
            <div style="font-size: 10px; color: var(--text-secondary);">Ibovespa Completo na Barra</div>
        </div>
    </aside>

    <main>
        <header>
            <h2 id="tituloAba">Dashboard Executivo Ibovespa</h2>
            <div class="controls">
                <select id="filtroTicker" onchange="carregarDados()">
                    <option value="TODOS">Todos os Tickers do Ibovespa</option>
                </select>
                <button class="primary" onclick="atualizarFeed()">🔄 Sincronizar Feed</button>
            </div>
        </header>

        <div id="aba-dashboard">

            <div class="card" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #38bdf8; margin-bottom: 25px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h3 style="margin: 0; border: none; padding: 0; color: #38bdf8;">🌡️ Termômetro de Sentimento do Mercado (Ibovespa)</h3>
                    <span id="termometroStatus" style="font-size: 13px; font-weight: bold; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 4px 10px; border-radius: 6px;">Carregando...</span>
                </div>
                <div style="background: #334155; border-radius: 8px; height: 14px; width: 100%; overflow: hidden; position: relative;">
                    <div id="termometroBarra" style="background: linear-gradient(90deg, #ef4444 0%, #eab308 50%, #22c55e 100%); width: 50%; height: 100%; transition: width 0.5s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
                    <span>🔴 Pessimista (Bearish)</span>
                    <span id="termometroDetalhes">Total analisado: 0 notícias</span>
                    <span>🟢 Otimista (Bullish)</span>
                </div>
            </div>
    
            <div class="period-selector">
                <button onclick="mudarPeriodo('hoje')" class="period-btn" data-period="hoje">☀️ Hoje</button>
                <button onclick="mudarPeriodo('24h')" class="period-btn active" data-period="24h">⏳ Últimas 24h</button>
                <button onclick="mudarPeriodo('semana')" class="period-btn" data-period="semana">📅 Esta Semana</button>
                <button onclick="mudarPeriodo('mes')" class="period-btn" data-period="mes">📊 Este Mês</button>
                <button onclick="mudarPeriodo('ano')" class="period-btn" data-period="ano">📈 Este Ano</button>
            </div>

            <div class="grid-container">
                <div class="card">
                    <h3>⚡ Stream de Fatos & Gossips em Tempo Real (Ibovespa)</h3>
                    <div style="max-height: 380px; overflow-y: auto;">
                        <table class="news-table">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Ativo</th>
                                    <th>Título / Fonte B3</th>
                                    <th>Sentimento (IA)</th>
                                </tr>
                            </thead>
                            <tbody id="tabelaNoticias"></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <h3>📊 Macrosetores (B3)</h3>
                    <div class="chart-container"><canvas id="setorChart"></canvas></div>
                </div>
            </div>
        </div>

        <div id="aba-hierarquia" style="display: none;">
            <div class="card">
                <h3>🌳 Painel Hierárquico Oficiais B3 (Macrosetor → Subsetor → Ticker)</h3>
                <div id="arvoreContainer" style="margin-top: 20px;">
                    <p style="color: var(--text-secondary);">Carregando estrutura hierárquica...</p>
                </div>
            </div>
        </div>

        <div id="aba-preferencias" style="display: none;">
            <div class="card">
                <h3>⭐ Painel Personalizado de Ativos & Setores</h3>
                <div id="preferenciasContainer" style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;"></div>
            </div>
        </div>

        <div id="aba-tendencia" style="display: none;">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 0; border: none; padding: 0;">📈 Algoritmo Preditivo & Curvas de Sentimento (EMA)</h3>
                </div>
                <div class="chart-container" style="height: 380px;"><canvas id="tendenciaChart"></canvas></div>
            </div>
        </div>

        <div id="aba-hitl" style="display: none;">
            <div class="card">
                <h3>🧪 Teste de Realidade & Validação Humana (HITL)</h3>
                <div id="hitlContainer"></div>
            </div>
        </div>
    </main>

    <script>
        let setorChartInstance = null;
        let tendenciaChartInstance = null;
        let periodoAtual = '24h';
        let loteAtualCache = [];

        async function carregarTickersSelect() {
            const res = await fetch('/api/tickers');
            const map = await res.json();
            const select = document.getElementById('filtroTicker');
            if(select) {
                select.innerHTML = '<option value="TODOS">Todos os Tickers do Ibovespa</option>';
                for(let t in map) {
                    select.innerHTML += `<option value="${t}">${t} - ${map[t].nome}</option>`;
                }
            }
        }

        async function carregarArvoreHierarquica() {
            const res = await fetch('/api/hierarquia');
            const arvore = await res.json();
            const container = document.getElementById('arvoreContainer');
            if(!container) return;
            container.innerHTML = '';
            for(let macro in arvore) {
                let macroDiv = document.createElement('div');
                macroDiv.className = 'macro-setor';
                let htmlMacro = `<h4 style="margin:0 0 10px 0; color:#38bdf8;">🏢 Macrosetor: ${macro}</h4>`;
                for(let subsetor in arvore[macro]) {
                    htmlMacro += `<div class="subsetor-box"><strong style="color:var(--text-primary); font-size:13px;">🔹 Subsetor: ${subsetor}</strong><div style="margin-top:6px;">`;
                    arvore[macro][subsetor].forEach(ativo => {
                        htmlMacro += `<span class="ticker-pill" onclick="filtrarPorTicker('${ativo.ticker}')"><b>${ativo.ticker}</b> (${ativo.nome})</span>`;
                    });
                    htmlMacro += `</div></div>`;
                }
                macroDiv.innerHTML = htmlMacro;
                container.appendChild(macroDiv);
            }
        }

        function filtrarPorTicker(ticker) {
            document.getElementById('filtroTicker').value = ticker;
            mudarAba('dashboard');
            carregarDados();
        }

        function mudarAba(aba) {
            ['dashboard', 'hierarquia', 'preferencias', 'tendencia', 'hitl'].forEach(a => {
                const el = document.getElementById(`aba-${a}`);
                const nav = document.getElementById(`nav-${a}`);
                if(el) el.style.display = 'none';
                if(nav) nav.classList.remove('active');
            });
            document.getElementById(`aba-${aba}`).style.display = 'block';
            document.getElementById(`nav-${aba}`).classList.add('active');
            if(aba === 'hierarquia') carregarArvoreHierarquica();
        }

        function mudarPeriodo(periodo) {
            periodoAtual = periodo;
            carregarDados();
        }

        async function carregarDados() {
            const ticker = document.getElementById('filtroTicker').value;
            const resNoticias = await fetch(`/api/noticias?periodo=${periodoAtual}&ticker=${ticker}`);
            const noticias = await resNoticias.json();
            const tbody = document.getElementById('tabelaNoticias');
            tbody.innerHTML = '';
            noticias.forEach(n => {
                let badgeClass = n.sentimento === 'Positivo' ? 'badge-pos' : (n.sentimento === 'Negativo' ? 'badge-neg' : 'badge-neu');
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${n.data}</td><td><b>${n.ticker}</b></td><td><a href="${n.link}" target="_blank" style="color: #38bdf8;">${n.titulo}</a></td><td><span class="badge ${badgeClass}">${n.sentimento}</span></td>`;
                tbody.appendChild(tr);
            });
        }

        
        async function carregarTermometro() {
            try {
                const res = await fetch('/api/termometro');
                const data = await res.json();
                document.getElementById('termometroStatus').innerText = data.status;
                document.getElementById('termometroBarra').style.width = data.percentual + '%';
                document.getElementById('termometroDetalhes').innerText = `Total: ${data.total} notícias (🟢 ${data.positivas} | 🔴 ${data.negativas} | 🟡 ${data.neutras})`;
            } catch(e) {
                console.error("Erro ao carregar termômetro", e);
            }
        }
    
        window.onload = async () => {
            carregarTermometro();
            await carregarTickersSelect();
            carregarDados();
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/tickers")
def api_tickers():
    return jsonify(obter_tickers_b3())

@app.route("/api/hierarquia")
def api_hierarquia():
    return jsonify(construir_arvore_b3())

@app.route("/api/noticias")
def api_noticias():
    periodo = request.args.get("periodo", "24h")
    ticker = request.args.get("ticker", "TODOS")
    return jsonify(listar_noticias(periodo, ticker))

@app.route("/api/estatisticas")
def api_estatisticas():
    return jsonify({"por_setor": {"Financeiro": 5, "Materiais Básicos": 4, "Petróleo e Gás": 6}})

@app.route("/api/atualizar", methods=["POST"])
def api_atualizar():
    return jsonify({"status": "sucesso"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route("/api/termometro")
def api_termometro():
    return jsonify(calcular_termometro_global())
