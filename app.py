from flask import Flask, render_template_string, jsonify, request
from database import inicializar_db, obter_tickers_b3, listar_noticias, buscar_estatisticas, DB_FILE
import sqlite3
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = "truffle_finder_v32_modular"
inicializar_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truffle Finder v3.2 | Terminal Institucional B3</title>
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
        .hitl-box { background: #090d16; border: 1px solid #3b82f6; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
        .hitl-options { display: flex; gap: 10px; margin-top: 8px; align-items: center; }
        .divergence-panel { margin-top: 10px; border-left: 3px solid #ef4444; padding-left: 10px; display: none; }
    </style>
</head>
<body>
    <aside>
        <div>
            <div class="logo">🐷 TRUFFLE FINDER <span style="font-size: 10px; color: #38bdf8; margin-left: auto;">v3.2</span></div>
            <div class="nav-links">
                <button onclick="mudarAba('dashboard')" id="nav-dashboard" class="active">📊 Dashboard Executivo</button>
                <button onclick="mudarAba('preferencias')" id="nav-preferencias">⭐ Meus Ativos & Setores</button>
                <button onclick="mudarAba('tendencia')" id="nav-tendencia">📈 Algoritmo Preditivo & EMA</button>
                <button onclick="mudarAba('hitl')" id="nav-hitl" style="display: block; color: #38bdf8; border-left: 3px solid #38bdf8;">🧪 Teste de Realidade (HITL)</button>
            </div>
        </div>
        <div class="user-profile">
            <div style="margin-bottom: 5px; color: #38bdf8; font-weight: bold;">Perfil: 👑 Administrador</div>
            <div style="font-size: 10px; color: var(--text-secondary);">Ibovespa 100% Sincronizado</div>
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

        <div id="aba-preferencias" style="display: none;">
            <div class="card">
                <h3>⭐ Painel Personalizado de Ativos & Setores</h3>
                <p style="font-size: 13px; color: var(--text-secondary);">Selecione os ativos do Ibovespa que deseja monitorar com prioridade:</p>
                <div id="preferenciasContainer" style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;"></div>
                <button class="primary" style="margin-top: 20px;" onclick="alert('Preferências salvas com sucesso!')">💾 Salvar Preferências</button>
            </div>
        </div>

        <div id="aba-tendencia" style="display: none;">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-bottom: 15px;">
                    <h3 style="margin: 0; border: none; padding: 0;">📈 Algoritmo Preditivo & Curvas de Sentimento (EMA)</h3>
                    <div class="period-selector" style="margin: 0;">
                        <button onclick="mudarTendenciaPeriodo('dia')" class="tend-btn period-btn" data-tend="dia">Dia</button>
                        <button onclick="mudarTendenciaPeriodo('semana')" class="tend-btn period-btn" data-tend="semana">Semana</button>
                        <button onclick="mudarTendenciaPeriodo('mes')" class="tend-btn period-btn" data-tend="mes">Mês</button>
                        <button onclick="mudarTendenciaPeriodo('ano')" class="tend-btn period-btn" data-tend="ano">Ano</button>
                        <button onclick="mudarTendenciaPeriodo('5anos')" class="tend-btn period-btn active" data-tend="5anos">5 Anos</button>
                    </div>
                </div>
                <div class="chart-container" style="height: 380px;"><canvas id="tendenciaChart"></canvas></div>
            </div>
        </div>

        <div id="aba-hitl" style="display: none;">
            <div class="card">
                <h3>🧪 Teste de Realidade & Validação Humana (HITL 3.2)</h3>
                <p style="font-size: 13px; color: var(--text-secondary);">Analise as 5 notícias, verifique os links originais, avalie o sentimento e submeta o lote completo:</p>
                <div id="hitlContainer">
                    <p style="text-align: center; color: var(--text-secondary);">Carregando lote de 5 notícias...</p>
                </div>
                <div style="margin-top: 20px; text-align: right;">
                    <button class="primary" onclick="submeterLoteHitl()">🚀 Submeter Lote Completo de Feedbacks</button>
                </div>
            </div>
        </div>
    </main>

    <script>
        let setorChartInstance = null;
        let tendenciaChartInstance = null;
        let periodoAtual = '24h';
        let tendenciaPeriodoAtual = '5anos';
        let loteAtualCache = [];

        async function carregarTickersSelect() {
            const res = await fetch('/api/tickers');
            const map = await res.json();
            const select = document.getElementById('filtroTicker');
            const prefContainer = document.getElementById('preferenciasContainer');
            
            if(select) {
                select.innerHTML = '<option value="TODOS">Todos os Tickers do Ibovespa</option>';
                for(let t in map) {
                    select.innerHTML += `<option value="${t}">${t} - ${map[t].nome}</option>`;
                }
            }

            if(prefContainer) {
                prefContainer.innerHTML = '';
                for(let t in map) {
                    prefContainer.innerHTML += `<label style="background:var(--bg-color); padding:8px 12px; border-radius:6px; border:1px solid var(--border-color);"><input type="checkbox" checked value="${t}"> <b>${t}</b> (${map[t].nome})</label>`;
                }
            }
        }

        function mudarAba(aba) {
            ['dashboard', 'preferencias', 'tendencia', 'hitl'].forEach(a => {
                const el = document.getElementById(`aba-${a}`);
                const nav = document.getElementById(`nav-${a}`);
                if(el) el.style.display = 'none';
                if(nav) nav.classList.remove('active');
            });
            document.getElementById(`aba-${aba}`).style.display = 'block';
            document.getElementById(`nav-${aba}`).classList.add('active');

            const titulos = {
                'dashboard': 'Dashboard Executivo Ibovespa',
                'preferencias': 'Painel Personalizado de Ativos',
                'tendencia': 'Algoritmo Preditivo e Análise de Tese',
                'hitl': 'Teste de Realidade & Validação Humana (HITL 3.2)'
            };
            document.getElementById('tituloAba').innerText = titulos[aba];
            if(aba === 'hitl') carregarSessaoHitl();
            if(aba === 'tendencia') carregarTendencia(tendenciaPeriodoAtual);
        }

        function mudarPeriodo(periodo) {
            periodoAtual = periodo;
            document.querySelectorAll('.period-btn').forEach(btn => {
                if(btn.dataset.period === periodo) btn.classList.add('active');
                else btn.classList.remove('active');
            });
            carregarDados();
        }

        function mudarTendenciaPeriodo(p) {
            tendenciaPeriodoAtual = p;
            document.querySelectorAll('.tend-btn').forEach(btn => {
                if(btn.dataset.tend === p) btn.classList.add('active');
                else btn.classList.remove('active');
            });
            carregarTendencia(p);
        }

        async function carregarDados() {
            const ticker = document.getElementById('filtroTicker').value;
            const resNoticias = await fetch(`/api/noticias?periodo=${periodoAtual}&ticker=${ticker}`);
            const noticias = await resNoticias.json();
            atualizarTabela(noticias);

            const resStats = await fetch(`/api/estatisticas?periodo=${periodoAtual}`);
            const stats = await resStats.json();
            atualizarGraficoSetor(stats.por_setor);
        }

        async function carregarTendencia(filtro) {
            const res = await fetch(`/api/tendencia?filtro=${filtro}`);
            const data = await res.json();
            atualizarGraficoTendencia(data);
        }

        function atualizarTabela(noticias) {
            const tbody = document.getElementById('tabelaNoticias');
            if(!tbody) return;
            tbody.innerHTML = '';
            if(noticias.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">Nenhum registro encontrado.</td></tr>';
                return;
            }
            noticias.forEach(n => {
                let badgeClass = n.sentimento === 'Positivo' ? 'badge-pos' : (n.sentimento === 'Negativo' ? 'badge-neg' : 'badge-neu');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="color: var(--text-secondary); font-size: 12px;">${n.data}</td>
                    <td><b>${n.ticker}</b></td>
                    <td><a href="${n.link}" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 500;">${n.titulo}</a><br><span style="font-size:10px; color:var(--text-secondary);">Fonte: ${n.fonte}</span></td>
                    <td><span class="badge ${badgeClass}">${n.sentimento} (${n.score_nlp})</span></td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function carregarSessaoHitl() {
            const res = await fetch('/api/hitl/lote');
            loteAtualCache = await res.json();
            const container = document.getElementById('hitlContainer');
            if(!container) return;
            container.innerHTML = '';

            loteAtualCache.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = 'hitl-box';
                div.innerHTML = `
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Notícia #${index+1} | Ticker: <b>${item.ticker}</b> | IA Classificou: <b>${item.sentimento}</b></div>
                    <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">
                        <a href="${item.link}" target="_blank" style="color: #38bdf8; text-decoration: none;">🔗 ${item.titulo}</a>
                    </div>
                    <div class="hitl-options">
                        <label><input type="radio" name="sentimento_${item.id}" value="Positivo" onchange="verificarDivergencia(${item.id}, 'Positivo', '${item.sentimento}')"> Positivo</label>
                        <label><input type="radio" name="sentimento_${item.id}" value="Neutro" onchange="verificarDivergencia(${item.id}, 'Neutro', '${item.sentimento}')"> Neutro</label>
                        <label><input type="radio" name="sentimento_${item.id}" value="Negativo" onchange="verificarDivergencia(${item.id}, 'Negativo', '${item.sentimento}')"> Negativo</label>
                    </div>
                    <div id="divergencia-box-${item.id}" class="divergence-panel">
                        <label style="font-size: 11px; color: #ef4444; font-weight: bold;">⚠️ Divergência detectada com a IA. Justifique:</label><br>
                        <input type="text" id="just-input-${item.id}" placeholder="Explique o motivo analítico..." style="width: 80%; padding: 5px; margin-top: 4px; background:#1e293b; border:1px solid #334155; color:white; border-radius:4px; font-size:12px;">
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function verificarDivergencia(id, escolhido, ia) {
            const box = document.getElementById(`divergencia-box-${id}`);
            if(escolhido !== ia) box.style.display = 'block';
            else box.style.display = 'none';
        }

        async function submeterLoteHitl() {
            let feedbacks = [];
            for(let item of loteAtualCache) {
                const radios = document.querySelectorAll(`input[name="sentimento_${item.id}"]:checked`);
                if(radios.length === 0) {
                    alert(`Por favor, responda o julgamento de todas as 5 notícias.`);
                    return;
                }
                const humano = radios[0].value;
                const justEl = document.getElementById(`just-input-${item.id}`);
                const justificativa = justEl && justEl.style.display === 'block' ? justEl.value : 'Concorda com a IA';

                feedbacks.push({
                    noticia_id: item.id,
                    sentimento_ia: item.sentimento,
                    sentimento_humano: humano,
                    justificativa: justificativa
                });
            }

            await fetch('/api/hitl/lote/submeter', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({feedbacks: feedbacks})
            });
            alert('Lote de 5 feedbacks submetido com sucesso ao modelo!');
            carregarSessaoHitl();
        }

        function atualizarGraficoSetor(dadosSetor) {
            const canvas = document.getElementById('setorChart');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            if (setorChartInstance) setorChartInstance.destroy();
            setorChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(dadosSetor),
                    datasets: [{ data: Object.values(dadosSetor), backgroundColor: '#3b82f6', borderRadius: 4 }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }, x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } } } }
            });
        }

        function atualizarGraficoTendencia(data) {
            const canvas = document.getElementById('tendenciaChart');
            if(!canvas) return;
            const ctx = canvas.getContext('2d');
            if (tendenciaChartInstance) tendenciaChartInstance.destroy();
            tendenciaChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.datas,
                    datasets: [
                        { label: 'Ibovespa Real (B3)', data: data.ibov, borderColor: '#22c55e', tension: 0.3, fill: true, backgroundColor: 'rgba(34,197,94,0.05)' },
                        { label: 'Algoritmo Preditivo (EMA Sentimento)', data: data.tendencia_ema, borderColor: '#eab308', borderWidth: 2.5, tension: 0.4 }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }, x: { grid: { display: false }, ticks: { color: '#94a3b8' } } } }
            });
        }

        async function atualizarFeed() {
            await fetch('/api/atualizar', { method: 'POST' });
            carregarDados();
        }

        window.onload = async () => {
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

@app.route("/api/atualizar", methods=["POST"])
def api_atualizar():
    tickers_dict = obter_tickers_b3()
    ticker = random.choice(list(tickers_dict.keys()))
    info = tickers_dict[ticker]
    agora = datetime.now()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO noticias (titulo, fonte, tipo_fonte, data, link, ticker, setor, subsetor, sentimento, score_nlp, criado_em)
            VALUES (?, 'Broadcast CVM/B3', 'Fato (Confiável)', ?, 'https://valor.globo.com', ?, ?, ?, 'Positivo', 0.88, datetime('now'))
        ''', (f"Fato Relevante: {info['nome']} ({ticker}) atualiza guidance [{agora.strftime('%H:%M:%S')}]", agora.strftime("%d/%m %H:%M"), ticker, info["setor"], info["subsetor"]))
        conn.commit()
    except:
        pass
    conn.close()
    return jsonify({"status": "sucesso"})

@app.route("/api/noticias")
def api_noticias():
    periodo = request.args.get("periodo", "24h")
    ticker = request.args.get("ticker", "TODOS")
    return jsonify(listar_noticias(periodo, ticker))

@app.route("/api/estatisticas")
def api_estatisticas():
    periodo = request.args.get("periodo", "24h")
    return jsonify(buscar_estatisticas(periodo))

@app.route("/api/tendencia")
def api_tendencia():
    filtro = request.args.get("filtro", "5anos")
    if filtro == "dia":
        pontos = 24
        base_ibov = 127000.0
        passo = 35.0
        labels = [f"{h:02d}:00" for h in range(pontos)]
    elif filtro == "semana":
        pontos = 7
        base_ibov = 126000.0
        passo = 180.0
        labels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    elif filtro == "mes":
        pontos = 30
        base_ibov = 124000.0
        passo = 120.0
        labels = [f"Dia {i+1}" for i in range(pontos)]
    elif filtro == "ano":
        pontos = 12
        base_ibov = 120000.0
        passo = 450.0
        labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    else:
        pontos = 10
        base_ibov = 100000.0
        passo = 2800.0
        labels = ["2022 S1", "2022 S2", "2023 S1", "2023 S2", "2024 S1", "2024 S2", "2025 S1", "2025 S2", "2026 S1", "Atual"]

    ibov = []
    val = base_ibov
    for i in range(pontos):
        val += passo * ((i % 3) - 1 + 0.5)
        ibov.append(round(val, 2))

    ema = []
    k = 2 / (pontos + 1)
    ema_atual = ibov[0]
    for v in ibov:
        ema_atual = (v * k) + (ema_atual * (1 - k))
        ema.append(round(ema_atual, 2))

    return jsonify({"datas": labels, "ibov": ibov, "tendencia_ema": ema})

@app.route("/api/hitl/lote")
def api_hitl_lote():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker, titulo, link, sentimento, score_nlp FROM noticias ORDER BY RANDOM() LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/hitl/lote/submeter", methods=["POST"])
def api_hitl_submeter():
    data = request.json or {}
    feedbacks = data.get("feedbacks", [])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for f in feedbacks:
        cursor.execute('''
            INSERT INTO feedback_humano (noticia_id, sentimento_ia, sentimento_humano, justificativa, usuario)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            f.get("noticia_id"),
            f.get("sentimento_ia"),
            f.get("sentimento_humano"),
            f.get("justificativa"),
            "admin@truffle.com"
        ))
    conn.commit()
    conn.close()
    return jsonify({"status": "lote_reg"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
