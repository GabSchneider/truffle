import sqlite3
from datetime import datetime, timedelta
import random

DB_FILE = "truffle_institutional.db"

# Lista Oficial Exata fornecida por você
LISTA_OFICIAL_B3 = [
    ("ALOS3", "Allos", "Consumo Cíclico", "Shoppings"),
    ("ALPA4", "Alpargatas", "Consumo Cíclico", "Calçados"),
    ("ABEV3", "Ambev", "Consumo Não Cíclico", "Bebidas"),
    ("AZZA3", "Arezzo (Azzas 2154)", "Consumo Cíclico", "Vestuário"),
    ("ASAI3", "Assaí", "Consumo Não Cíclico", "Comércio Varejista"),
    ("AURE3", "Auren Energia", "Utilidade Pública", "Energia Elétrica"),
    ("AXIA3", "Axia Energia", "Utilidade Pública", "Energia Elétrica"),
    ("AZUL4", "Azul", "Bens Industriais", "Transporte Aéreo"),
    ("B3SA3", "B3", "Financeiro", "Serviços Financeiros"),
    ("BBAS3", "Banco do Brasil", "Financeiro", "Bancos Comerciais"),
    ("BBSE3", "BB Seguridade", "Financeiro", "Seguros"),
    ("BBDC3", "Bradesco (ON)", "Financeiro", "Bancos Comerciais"),
    ("BBDC4", "Bradesco (PN)", "Financeiro", "Bancos Comerciais"),
    ("BRAP4", "Bradespar", "Materiais Básicos", "Holdings"),
    ("BRKM5", "Braskem", "Materiais Básicos", "Químicos"),
    ("BRAV3", "Brava Energia", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("BRFS3", "BRF", "Consumo Não Cíclico", "Alimentos"),
    ("BPAC11", "BTG Pactual", "Financeiro", "Bancos de Investimento"),
    ("CXSE3", "Caixa Seguridade", "Financeiro", "Seguros"),
    ("CRFB3", "Carrefour", "Consumo Não Cíclico", "Comércio Varejista"),
    ("CCRO3", "Ccr", "Bens Industriais", "Exploração de Rodovias"),
    ("CEAB3", "Cea Modas", "Consumo Cíclico", "Tecidos e Vestuário"),
    ("CMIG4", "Cemig", "Utilidade Pública", "Energia Elétrica"),
    ("CIEL3", "Cielo", "Financeiro", "Serviços Financeiros"),
    ("COGN3", "Cogna", "Diversos", "Serviços Educacionais"),
    ("CSMG3", "Copasa", "Utilidade Pública", "Água e Saneamento"),
    ("CPLE3", "Copel (ON)", "Utilidade Pública", "Energia Elétrica"),
    ("CPLE6", "Copel (PNB)", "Utilidade Pública", "Energia Elétrica"),
    ("CSAN3", "Cosan", "Petróleo, Gás e Biocombustíveis", "Combustíveis"),
    ("CPFE3", "CPFL Energia", "Utilidade Pública", "Energia Elétrica"),
    ("CURY3", "Cury", "Consumo Cíclico", "Construção Civil"),
    ("CYRE3", "Cyrela", "Consumo Cíclico", "Construção Civil"),
    ("DXCO3", "Dexco", "Materiais Básicos", "Madeira e Papel"),
    ("DIRR3", "Direcional", "Consumo Cíclico", "Construção Civil"),
    ("ECOR3", "Ecorodovias", "Bens Industriais", "Exploração de Rodovias"),
    ("ELET3", "Eletrobras (ON)", "Utilidade Pública", "Energia Elétrica"),
    ("ELET6", "Eletrobras (PNB)", "Utilidade Pública", "Energia Elétrica"),
    ("EMBJ3", "Embraer", "Bens Industriais", "Aeronaves"),
    ("ENGI11", "Energisa", "Utilidade Pública", "Energia Elétrica"),
    ("ENEV3", "Eneva", "Utilidade Pública", "Energia Elétrica"),
    ("EGIE3", "Engie Brasil", "Utilidade Pública", "Energia Elétrica"),
    ("EQTL3", "Equatorial", "Utilidade Pública", "Energia Elétrica"),
    ("EZTC3", "Eztec", "Consumo Cíclico", "Construção Civil"),
    ("FLRY3", "Fleury", "Saúde", "Serviços Médicos"),
    ("GGBR4", "Gerdau", "Materiais Básicos", "Siderurgia"),
    ("GOAU4", "Gerdau Metalúrgica", "Materiais Básicos", "Siderurgia"),
    ("GMAT3", "Grupo Mateus", "Consumo Não Cíclico", "Comércio Varejista"),
    ("HAPV3", "Hapvida", "Saúde", "Planos de Saúde"),
    ("HYPE3", "Hypera", "Saúde", "Farmacêuticos"),
    ("IGTI11", "Iguatemi", "Consumo Cíclico", "Shoppings"),
    ("ISAE4", "Isa Energia", "Utilidade Pública", "Energia Elétrica"),
    ("ITUB4", "Itaú Unibanco", "Financeiro", "Bancos Comerciais"),
    ("ITSA4", "Itaúsa", "Financeiro", "Holdings"),
    ("JBSS3", "JBS", "Consumo Não Cíclico", "Alimentos"),
    ("JHSF3", "JHSF", "Consumo Cíclico", "Incorporações"),
    ("KLBN11", "Klabin", "Materiais Básicos", "Celulose e Papel"),
    ("RENT3", "Localiza", "Consumo Cíclico", "Aluguel de Carros"),
    ("LREN3", "Lojas Renner", "Consumo Cíclico", "Tecidos e Vestuário"),
    ("MGLU3", "Magazine Luiza", "Consumo Cíclico", "Varejo Digital"),
    ("POMO4", "Marcopolo", "Bens Industriais", "Material Rodoviário"),
    ("MBRF3", "Marfrig", "Consumo Não Cíclico", "Alimentos"),
    ("BEEF3", "Minerva", "Consumo Não Cíclico", "Alimentos"),
    ("MOTV3", "Motiva", "Diversos", "Diversos"),
    ("MRVE3", "MRV", "Consumo Cíclico", "Construção Civil"),
    ("MULT3", "Multiplan", "Consumo Cíclico", "Shoppings"),
    ("NATU3", "Natura", "Consumo Não Cíclico", "Cosméticos"),
    ("PETR3", "Petrobras (ON)", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("PETR4", "Petrobras (PN)", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("RECV3", "PetroReconcavo", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("PSSA3", "Porto Seguro", "Financeiro", "Seguros"),
    ("PRIO3", "Prio", "Petróleo, Gás e Biocombustíveis", "Exploração e Produção"),
    ("RADL3", "RaiaDrogasil", "Consumo Não Cíclico", "Farmácias"),
    ("RAIZ4", "Raízen", "Petróleo, Gás e Biocombustíveis", "Energia Renovável"),
    ("RDOR3", "Rede D Or", "Saúde", "Serviços Hospitalares"),
    ("RAIL3", "Rumo", "Bens Industriais", "Logística Ferroviária"),
    ("SBSP3", "Sabesp", "Utilidade Pública", "Saneamento"),
    ("SANB11", "Santander Brasil", "Financeiro", "Bancos Comerciais"),
    ("SMTO3", "São Martinho", "Consumo Não Cíclico", "Açúcar e Álcool"),
    ("CSNA3", "Siderúrgica Nacional", "Materiais Básicos", "Siderurgia"),
    ("SIMH3", "Simpar", "Bens Industriais", "Holdings"),
    ("SLCE3", "Slc Agrícola", "Consumo Não Cíclico", "Agricultura"),
    ("SMFT3", "Smart Fit", "Consumo Cíclico", "Serviços Diversos"),
    ("SUZB3", "Suzano", "Materiais Básicos", "Celulose e Papel"),
    ("TAEE11", "Taesa", "Utilidade Pública", "Energia Elétrica"),
    ("VIVT3", "Telefônica Brasil (Vivo)", "Telecomunicações", "Telefonia Fixa e Móvel"),
    ("TIMS3", "Tim", "Telecomunicações", "Telefonia Móvel"),
    ("TOTS3", "Totvs", "Tecnologia", "Software e Serviços"),
    ("UGPA3", "Ultrapar", "Petróleo, Gás e Biocombustíveis", "Distribuição de Combustíveis"),
    ("USIM5", "Usiminas", "Materiais Básicos", "Siderurgia"),
    ("VALE3", "Vale", "Materiais Básicos", "Mineração"),
    ("VAMO3", "Vamos", "Bens Industriais", "Locação de Caminhões"),
    ("VBBR3", "Vibra Energia", "Petróleo, Gás e Biocombustíveis", "Distribuição de Combustíveis"),
    ("VIVA3", "Vivara", "Consumo Cíclico", "Comércio Varejista"),
    ("WEGE3", "Weg", "Bens Industriais", "Máquinas e Equipamentos"),
    ("YDUQ3", "Yduqs", "Diversos", "Serviços Educacionais")
]

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Recriar / atualizar tabela oficial garantindo todos os ativos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickers_ibov_oficial (
        ticker TEXT PRIMARY KEY,
        nome TEXT,
        setor TEXT,
        subsetor TEXT
    )
''')

# Inserir cada um da lista oficial
for item in LISTA_OFICIAL_B3:
    cursor.execute('''
        INSERT OR REPLACE INTO tickers_ibov_oficial (ticker, nome, setor, subsetor)
        VALUES (?, ?, ?, ?)
    ''', item)

# Garantir tabela de notícias caso precise de massa
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

# Popular notícias para cada ativo oficial caso a tabela esteja fraca
cursor.execute("SELECT COUNT(*) FROM noticias")
if cursor.fetchone()[0] < 50:
    fontes_fatos = ["Valor Econômico", "InfoMoney", "Broadcast CVM/B3", "Exame Finanças"]
    fontes_gossip = ["X / Fórum Corporativo", "Reddit / InvestidoresBR", "Blog de Bastidores B3"]
    agora = datetime.now()
    
    for ticker, nome, setor, subsetor in LISTA_OFICIAL_B3:
        for i in range(2):
            sentimento = random.choice(["Positivo", "Negativo", "Neutro"])
            score = round(random.uniform(-0.9, 0.9), 2)
            is_fato = random.choice([True, False])
            fonte = random.choice(fontes_fatos) if is_fato else random.choice(fontes_gossip)
            tipo = "Fato (Confiável)" if is_fato else "Gossip (Rumor)"
            titulo = f"Relatório B3: {nome} ({ticker}) movimenta o setor de {setor} [Atualização {i+1}]"
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
print(f"Sucesso! {len(LISTA_OFICIAL_B3)} ativos oficiais inseridos na base de dados.")
