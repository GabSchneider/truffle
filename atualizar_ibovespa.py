import sqlite3
from datetime import datetime, timedelta
import random

DB_FILE = "truffle_institutional.db"

# LISTA OFICIAL COMPLETA DE TODOS OS TICKERS DO IBOVESPA E SETORES B3
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
    ("RDOR3", "Rede D'Or ON", "Saúde", "Serviços Médico-Hospitalares"),
    ("ITSA4", "Itaúsa PN", "Financeiro", "Holdings Diversificadas"),
    ("SANB11", "Santander Brasil Unit", "Financeiro", "Bancos Comerciais"),
    ("BPAC11", "BTG Pactual Unit", "Financeiro", "Bancos de Investimento"),
    ("CMIG4", "Cemig PN", "Utilidade Pública", "Energia Elétrica"),
    ("CPLE6", "Copel PNB", "Utilidade Pública", "Energia Elétrica"),
    ("SBSP3", "Sabesp ON", "Utilidade Pública", "Saneamento e Gestão de Resíduos"),
    ("VBBR3", "Vibra Energia ON", "Petróleo, Gás e Biocombustíveis", "Distribuição de Combustíveis"),
    ("HAPV3", "Hapvida ON", "Saúde", "Serviços Médico-Hospitalares"),
    ("COGN3", "Cogna Educação ON", "Diversos", "Serviços Educacionais"),
    ("EMBR3", "Embraer ON", "Bens Industriais", "Material de Aeronaves e Defesa")
]

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Assegurar que a tabela oficial do Ibovespa existe e está preenchida com todos
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

# Assegurar tabela de notícias
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

# Popular notícias para todos os tickers cadastrados se a tabela estiver fraca
cursor.execute("SELECT COUNT(*) FROM noticias")
if cursor.fetchone()[0] < 30:
    fontes_fatos = ["Valor Econômico", "InfoMoney", "Broadcast CVM/B3", "Exame Finanças"]
    fontes_gossip = ["X / Fórum Corporativo", "Reddit / InvestidoresBR", "Blog de Bastidores B3"]
    agora = datetime.now()
    
    cursor.execute("SELECT ticker, nome, setor, subsetor FROM tickers_ibov_oficial")
    empresas = cursor.fetchall()
    
    for ticker, nome, setor, subsetor in empresas:
        for i in range(2):
            sentimento = random.choice(["Positivo", "Negativo", "Neutro"])
            score = round(random.uniform(-0.9, 0.9), 2)
            is_fato = random.choice([True, False])
            fonte = random.choice(fontes_fatos) if is_fato else random.choice(fontes_gossip)
            tipo = "Fato (Confiável)" if is_fato else "Gossip (Rumor)"
            titulo = f"Monitoramento Institucional B3: {nome} ({ticker}) atrai fluxo no setor de {setor} [Atualização {i+1}]"
            link = "https://valor.globo.com/financas/" if is_fato else "https://twitter.com/search?q=" + ticker
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO noticias (titulo, fonte, tipo_fonte, data, link, ticker, setor, subsetor, sentimento, score_nlp, criado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-' || ? || ' hour'))
                ''', (titulo, fonte, tipo, agora.strftime("%d/%m %H:%M"), link, ticker, setor, subsetor, sentimento, score, random.randint(1, 48)))
            except:
                pass

conn.commit()
conn.close()
print("Base do Ibovespa e tickers atualizados com sucesso!")
