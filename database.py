import sqlite3
from datetime import datetime, timedelta
import random

DB_FILE = "truffle_institutional.db"

COMPOSICAO_IBOV_OFICIAL = [
    ("PETR4", "Petrobras PN", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("PETR3", "Petrobras ON", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("VALE3", "Vale ON", "Materiais Básicos", "Mineração"),
    ("ITUB4", "Itaú Unibanco PN", "Financeiro", "Bancos Comerciais"),
    ("BBDC4", "Bradesco PN", "Financeiro", "Bancos Comerciais"),
    ("BBAS3", "Banco do Brasil ON", "Financeiro", "Bancos Comerciais"),
    ("B3SA3", "B3 S.A. ON", "Financeiro", "Serviços Financeiros Diversos"),
    ("ABEV3", "Ambev ON", "Consumo Não Cíclico", "Bebidas"),
    ("MGLU3", "Magazine Luiza ON", "Consumo Cíclico", "Varejo Digital"),
    ("WEGE3", "Weg ON", "Bens Industriais", "Máquinas e Equipamentos"),
    ("SUZB3", "Suzano ON", "Materiais Básicos", "Madeira e Celulose"),
    ("ELET3", "Eletrobras ON", "Utilidade Pública", "Energia Elétrica"),
    ("JBSS3", "JBS ON", "Consumo Não Cíclico", "Carnes e Derivados"),
    ("RENT3", "Localiza ON", "Consumo Cíclico", "Aluguel de Carros"),
    ("LREN3", "Lojas Renner ON", "Consumo Cíclico", "Tecido, Vestuário e Calçados"),
    ("RADL3", "RaiaDrogasil ON", "Consumo Não Cíclico", "Comércio Varejista de Medicamentos"),
    ("PRIO3", "Prio ON", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("EQTL3", "Equatorial ON", "Utilidade Pública", "Energia Elétrica"),
    ("CSAN3", "Cosan ON", "Petróleo, Gás e Biocombustíveis", "Combustíveis e Lubrificantes"),
    ("RDOR3", "Rede D'Or ON", "Saúde", "Serviços Médico-Hospitalares")
]

def inicializar_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickers_ibov_oficial (
            ticker TEXT PRIMARY KEY,
            nome TEXT,
            setor TEXT,
            subsetor TEXT
        )
    ''')
    for t in COMPOSICAO_IBOV_OFICIAL:
        cursor.execute('INSERT OR REPLACE INTO tickers_ibov_oficial (ticker, nome, setor, subsetor) VALUES (?, ?, ?, ?)', t)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT UNIQUE,
            fonte TEXT,
            tipo_fonte TEXT,
            data TEXT,
            link TEXT,
            ticker TEXT,
            setor TEXT,
            subsetor TEXT,
            sentimento TEXT,
            score_nlp REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_humano (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            noticia_id INTEGER,
            sentimento_ia TEXT,
            sentimento_humano TEXT,
            justificativa TEXT,
            usuario TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM noticias")
    if cursor.fetchone()[0] == 0:
        gerar_massa_robusta(cursor)
        
    conn.commit()
    conn.close()

def obter_tickers_b3():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickers_ibov_oficial ORDER BY ticker ASC")
    rows = cursor.fetchall()
    conn.close()
    return {r["ticker"]: {"nome": r["nome"], "setor": r["setor"], "subsetor": r["subsetor"]} for r in rows}

def gerar_massa_robusta(cursor):
    tickers_dict = obter_tickers_b3()
    fontes_fatos = ["Valor Econômico", "InfoMoney", "Broadcast CVM/B3", "Exame Finanças"]
    fontes_gossip = ["X / Fórum Corporativo", "Reddit / InvestidoresBR", "Blog de Bastidores B3", "Canal M&A"]
    
    templates = [
        ("Fato Relevante: {nome} ({ticker}) reporta resultado trimestral acima das projeções da B3.", "Fato (Confiável)", "Positivo", 0.85),
        ("Conselho de Administração da {nome} ({ticker}) aprova distribuição de dividendos extraordinários.", "Fato (Confiável)", "Positivo", 0.75),
        ("Setor de {setor} enfrenta volatilidade regulatória com reflexos diretos em {ticker}.", "Fato (Confiável)", "Negativo", -0.55),
        ("Boato forte no pregão: {nome} ({ticker}) estuda operação corporativa surpresa.", "Gossip (Rumor)", "Positivo", 0.60),
        ("Especulação de bastidor aponta movimentações atípicas nos papéis de {ticker}.", "Gossip (Rumor)", "Negativo", -0.65)
    ]
    
    agora = datetime.now()
    for ticker, info in tickers_dict.items():
        for i in range(3):
            t = random.choice(templates)
            titulo = f"{t[0].format(nome=info['nome'], ticker=ticker, setor=info['setor'])} [Ref: {i+1}]"
            fonte = random.choice(fontes_fatos) if t[1] == "Fato (Confiável)" else random.choice(fontes_gossip)
            link = "https://valor.globo.com/financas/" if "Fato" in t[1] else "https://twitter.com/search?q=" + ticker
            try:
                cursor.execute('''
                    INSERT INTO noticias (titulo, fonte, tipo_fonte, data, link, ticker, setor, subsetor, sentimento, score_nlp, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-' || ? || ' hour'))
                ''', (titulo, fonte, t[1], agora.strftime("%d/%m %H:%M"), link, ticker, info["setor"], info["subsetor"], t[2], t[3], random.randint(1, 48)))
            except:
                pass

def listar_noticias(periodo, filtro_ticker=None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM noticias WHERE 1=1"
    agora = datetime.now()
    
    if periodo == "hoje":
        query += f" AND criado_em LIKE '{agora.strftime('%Y-%m-%d')}%'"
    elif periodo == "24h":
        query += f" AND criado_em >= '{(agora - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}'"
    elif periodo == "semana":
        query += f" AND criado_em >= '{(agora - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')}'"
    elif periodo == "mes":
        query += f" AND criado_em >= '{(agora - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')}'"
    elif periodo == "ano":
        query += f" AND criado_em >= '{(agora - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')}'"
        
    if filtro_ticker and filtro_ticker != "TODOS":
        query += f" AND ticker = '{filtro_ticker}'"
        
    query += " ORDER BY id DESC LIMIT 200"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def buscar_estatisticas(periodo):
    noticias = listar_noticias(periodo)
    setores = {}
    for n in noticias:
        s = n["setor"]
        setores[s] = setores.get(s, 0) + 1
    return {"por_setor": setores}
