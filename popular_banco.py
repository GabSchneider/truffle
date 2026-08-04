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

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Garantir tabela de tickers
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

# Garantir tabela de notícias
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

# Inserir massa robusta se estiver vazio
cursor.execute("SELECT COUNT(*) FROM noticias")
total = cursor.fetchone()[0]

if total == 0:
    fontes_fatos = ["Valor Econômico", "InfoMoney", "Broadcast CVM/B3", "Exame Finanças"]
    fontes_gossip = ["X / Fórum Corporativo", "Reddit / InvestidoresBR", "Blog de Bastidores B3", "Canal M&A"]
    agora = datetime.now()
    
    cursor.execute("SELECT ticker, nome, setor, subsetor FROM tickers_ibov_oficial")
    empresas = cursor.fetchall()
    
    for ticker, nome, setor, subsetor in empresas:
        for i in range(3):
            sentimento = random.choice(["Positivo", "Negativo", "Neutro"])
            score = round(random.uniform(-0.9, 0.9), 2)
            is_fato = random.choice([True, False])
            fonte = random.choice(fontes_fatos) if is_fato else random.choice(fontes_gossip)
            tipo = "Fato (Confiável)" if is_fato else "Gossip (Rumor)"
            titulo = f"Relatório Institucional: {nome} ({ticker}) movimenta o setor de {setor} [Ref: {i+1}]"
            link = "https://valor.globo.com/financas/" if is_fato else "https://twitter.com/search?q=" + ticker
            
            try:
                cursor.execute('''
                    INSERT INTO noticias (titulo, fonte, tipo_fonte, data, link, ticker, setor, subsetor, sentimento, score_nlp, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-' || ? || ' hour'))
                ''', (titulo, fonte, tipo, agora.strftime("%d/%m %H:%M"), link, ticker, setor, subsetor, sentimento, score, random.randint(1, 24)))
            except:
                pass

conn.commit()
conn.close()
print("Banco de dados populado com sucesso!")
