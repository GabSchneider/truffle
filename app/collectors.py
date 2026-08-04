import feedparser
import requests
import yfinance as yf
from datetime import datetime
from urllib.parse import quote
import os

SETOR_NORMALIZER = {
    # Petróleo e Gás
    "Petróleo, Gás e Biocombustíveis": "Petróleo e Gás", "Energia & Petróleo": "Petróleo e Gás", "Petróleo e Gás": "Petróleo e Gás", "Energia": "Petróleo e Gás",
    # Commodities & Mineração
    "Mineração": "Materiais Básicos", "Siderurgia e Metalurgia": "Materiais Básicos", "Papel e Celulose": "Materiais Básicos", "Materiais Básicos": "Materiais Básicos",
    # Financeiro
    "Intermediários Financeiros": "Financeiro", "Serviços Financeiros Diversos": "Financeiro", "Previdência e Seguros": "Financeiro", "Financeiro": "Financeiro",
    # Consumo e Varejo
    "Comércio": "Consumo e Varejo", "Alimentos Processados": "Consumo e Varejo", "Bebidas": "Consumo e Varejo", "Tecnologia da Informação": "Consumo e Varejo", "Consumo e Varejo": "Consumo e Varejo",
    # Indústria & Logística
    "Bens de Capital": "Indústria", "Material de Transporte": "Indústria", "Transporte": "Indústria", "Indústria": "Indústria",
    # Saúde e Serviços / Imobiliário
    "Serviços Médico - Hospitalares": "Saúde e Serviços", "Comércio e Distribuição": "Saúde e Serviços", "Imobiliário": "Saúde e Serviços", "Saúde e Serviços": "Saúde e Serviços"
}

# Carteira Completa Ibovespa B3
TICKERS_BASE = {
    # Energia & Petróleo
    'PETR4': {'empresa': 'Petrobras', 'setor_bruto': 'Petróleo, Gás e Biocombustíveis', 'escala': 'large_cap', 'yf_symbol': 'PETR4.SA'},
    'PETR3': {'empresa': 'Petrobras ON', 'setor_bruto': 'Petróleo, Gás e Biocombustíveis', 'escala': 'large_cap', 'yf_symbol': 'PETR3.SA'},
    'PRIO3': {'empresa': 'PRIO', 'setor_bruto': 'Petróleo, Gás e Biocombustíveis', 'escala': 'mid_cap', 'yf_symbol': 'PRIO3.SA'},
    'VBBR3': {'empresa': 'Vibra Energia', 'setor_bruto': 'Petróleo, Gás e Biocombustíveis', 'escala': 'mid_cap', 'yf_symbol': 'VBBR3.SA'},
    'ELET3': {'empresa': 'Eletrobras', 'setor_bruto': 'Energia Elétrica', 'escala': 'large_cap', 'yf_symbol': 'ELET3.SA'},
    'EQTL3': {'empresa': 'Equatorial', 'setor_bruto': 'Energia Elétrica', 'escala': 'mid_cap', 'yf_symbol': 'EQTL3.SA'},
    'CMIG4': {'empresa': 'Cemig', 'setor_bruto': 'Energia Elétrica', 'escala': 'mid_cap', 'yf_symbol': 'CMIG4.SA'},
    'CPLE6': {'empresa': 'Copel', 'setor_bruto': 'Energia Elétrica', 'escala': 'mid_cap', 'yf_symbol': 'CPLE6.SA'},

    # Commodities & Mineração
    'VALE3': {'empresa': 'Vale', 'setor_bruto': 'Mineração', 'escala': 'large_cap', 'yf_symbol': 'VALE3.SA'},
    'SUZB3': {'empresa': 'Suzano', 'setor_bruto': 'Papel e Celulose', 'escala': 'large_cap', 'yf_symbol': 'SUZB3.SA'},
    'KLBN11': {'empresa': 'Klabin', 'setor_bruto': 'Papel e Celulose', 'escala': 'mid_cap', 'yf_symbol': 'KLBN11.SA'},
    'GGBR4': {'empresa': 'Gerdau', 'setor_bruto': 'Siderurgia e Metalurgia', 'escala': 'mid_cap', 'yf_symbol': 'GGBR4.SA'},
    'CSNA3': {'empresa': 'Siderurgica Nacional', 'setor_bruto': 'Siderurgia e Metalurgia', 'escala': 'mid_cap', 'yf_symbol': 'CSNA3.SA'},

    # Financeiro & Bancos
    'ITUB4': {'empresa': 'Itaú Unibanco', 'setor_bruto': 'Intermediários Financeiros', 'escala': 'large_cap', 'yf_symbol': 'ITUB4.SA'},
    'BBDC4': {'empresa': 'Bradesco', 'setor_bruto': 'Intermediários Financeiros', 'escala': 'large_cap', 'yf_symbol': 'BBDC4.SA'},
    'BBAS3': {'empresa': 'Banco do Brasil', 'setor_bruto': 'Intermediários Financeiros', 'escala': 'large_cap', 'yf_symbol': 'BBAS3.SA'},
    'BPAC11': {'empresa': 'BTG Pactual', 'setor_bruto': 'Serviços Financeiros Diversos', 'escala': 'large_cap', 'yf_symbol': 'BPAC11.SA'},
    'SANB11': {'empresa': 'Santander Brasil', 'setor_bruto': 'Intermediários Financeiros', 'escala': 'large_cap', 'yf_symbol': 'SANB11.SA'},
    'B3SA3': {'empresa': 'B3 Brasil Bolsa Balcão', 'setor_bruto': 'Serviços Financeiros Diversos', 'escala': 'large_cap', 'yf_symbol': 'B3SA3.SA'},

    # Consumo & Varejo & Alimentos
    'ABEV3': {'empresa': 'Ambev', 'setor_bruto': 'Bebidas', 'escala': 'large_cap', 'yf_symbol': 'ABEV3.SA'},
    'MGLU3': {'empresa': 'Magazine Luiza', 'setor_bruto': 'Comércio', 'escala': 'mid_cap', 'yf_symbol': 'MGLU3.SA'},
    'LREN3': {'empresa': 'Lojas Renner', 'setor_bruto': 'Comércio', 'escala': 'mid_cap', 'yf_symbol': 'LREN3.SA'},
    'JBSS3': {'empresa': 'JBS', 'setor_bruto': 'Alimentos Processados', 'escala': 'large_cap', 'yf_symbol': 'JBSS3.SA'},
    'BRFS3': {'empresa': 'BRF', 'setor_bruto': 'Alimentos Processados', 'escala': 'mid_cap', 'yf_symbol': 'BRFS3.SA'},
    'BEEF3': {'empresa': 'Minerva', 'setor_bruto': 'Alimentos Processados', 'escala': 'mid_cap', 'yf_symbol': 'BEEF3.SA'},
    'NTCO3': {'empresa': 'Natura &Co', 'setor_bruto': 'Comércio', 'escala': 'mid_cap', 'yf_symbol': 'NTCO3.SA'},
    'ASAI3': {'empresa': 'Assaí Atacadista', 'setor_bruto': 'Comércio', 'escala': 'mid_cap', 'yf_symbol': 'ASAI3.SA'},
    'CRFB3': {'empresa': 'Carrefour Brasil', 'setor_bruto': 'Comércio', 'escala': 'mid_cap', 'yf_symbol': 'CRFB3.SA'},

    # Indústria, Logística & Tecnologia
    'WEGE3': {'empresa': 'WEG', 'setor_bruto': 'Bens de Capital', 'escala': 'large_cap', 'yf_symbol': 'WEGE3.SA'},
    'EMBR3': {'empresa': 'Embraer', 'setor_bruto': 'Material de Transporte', 'escala': 'mid_cap', 'yf_symbol': 'EMBR3.SA'},
    'RAIL3': {'empresa': 'Rumo Logística', 'setor_bruto': 'Transporte', 'escala': 'mid_cap', 'yf_symbol': 'RAIL3.SA'},
    'CCRO3': {'empresa': 'CCR', 'setor_bruto': 'Transporte', 'escala': 'mid_cap', 'yf_symbol': 'CCRO3.SA'},
    'TOTS3': {'empresa': 'Totvs', 'setor_bruto': 'Tecnologia da Informação', 'escala': 'mid_cap', 'yf_symbol': 'TOTS3.SA'},

    # Saúde, Serviços & Imobiliário
    'HAPV3': {'empresa': 'Hapvida', 'setor_bruto': 'Serviços Médico - Hospitalares', 'escala': 'mid_cap', 'yf_symbol': 'HAPV3.SA'},
    'RADL3': {'empresa': 'RaiaDrogasil', 'setor_bruto': 'Comércio e Distribuição', 'escala': 'large_cap', 'yf_symbol': 'RADL3.SA'},
    'RENT3': {'empresa': 'Localiza', 'setor_bruto': 'Imobiliário', 'escala': 'large_cap', 'yf_symbol': 'RENT3.SA'},
    'MULT3': {'empresa': 'Multiplan', 'setor_bruto': 'Imobiliário', 'escala': 'mid_cap', 'yf_symbol': 'MULT3.SA'},
    'ALSO3': {'empresa': 'Iguatemi Aliansce', 'setor_bruto': 'Imobiliário', 'escala': 'mid_cap', 'yf_symbol': 'ALSO3.SA'},
    'CYRE3': {'empresa': 'Cyrela', 'setor_bruto': 'Imobiliário', 'escala': 'mid_cap', 'yf_symbol': 'CYRE3.SA'}
}

RELIABLE_SOURCES = ['valor econômico', 'reuters', 'bloomberg', 'estadão', 'exame', 'info money', 'infomoney', 'o globo', 'brazil journal', 'neofeed', 'suno', 'cvm', 'money times', 'bp money']
GOSSIP_SOURCES = ['fofoca', 'rumor', 'boato', 'blog', 'forum', 'x.com', 'twitter', 'reddit', 'farialimabets', 'investimentos']

def get_normalized_ticker_map():
    normalized_map = {}
    for ticker, info in TICKERS_BASE.items():
        sector_raw = info.get('setor_bruto', 'Outros')
        norm_sector = SETOR_NORMALIZER.get(sector_raw, "Consumo e Varejo")
        normalized_map[ticker] = {
            'empresa': info['empresa'],
            'setor': norm_sector,
            'escala': info['escala'],
            'yf_symbol': info['yf_symbol']
        }
    return normalized_map

TICKERS_MAP = get_normalized_ticker_map()

def fetch_b3_quotes():
    quotes = {}
    try:
        symbols = [info['yf_symbol'] for info in TICKERS_MAP.values()]
        # Busca em lotes de 15 para não sobrecarregar
        for i in range(0, len(symbols), 15):
            chunk = symbols[i:i+15]
            data = yf.Tickers(" ".join(chunk))
            for ticker, info in TICKERS_MAP.items():
                if info['yf_symbol'] in chunk:
                    try:
                        fast = data.tickers[info['yf_symbol']].fast_info
                        price = fast.get('lastPrice', 0.0)
                        prev_close = fast.get('previousClose', price)
                        var_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
                        quotes[ticker] = {'preco': round(price, 2), 'var_pct': round(var_pct, 2)}
                    except Exception:
                        pass
    except Exception as e:
        print(f"Erro cotações: {e}")
    return quotes

def classify_source(source_name: str) -> str:
    name_lower = source_name.lower()
    if any(s in name_lower for s in RELIABLE_SOURCES):
        return 'confiavel'
    elif any(s in name_lower for s in GOSSIP_SOURCES):
        return 'gossip'
    return 'media'

def fetch_rss_news(ticker: str):
    empresa_info = TICKERS_MAP.get(ticker)
    if not empresa_info:
        return []

    # Busca multicanal (Mídia Oficial + Redes Sociais via RSS / Google Search Indexing)
    queries = [
        f"{empresa_info['empresa']} OR {ticker}",
        f"site:twitter.com OR site:x.com {ticker}",
        f"site:reddit.com {ticker}"
    ]

    articles = []
    for q in queries:
        url = f"https://news.google.com/rss/search?q={quote(q)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            pub_date = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])

            fonte_nome = entry.source.title if hasattr(entry, 'source') and hasattr(entry.source, 'title') else "Google News"
            is_cvm = "fato relevante" in entry.title.lower() or "cvm" in entry.title.lower()
            is_social = "twitter" in entry.link.lower() or "x.com" in entry.link.lower() or "reddit" in entry.link.lower()

            canal = 'midia_oficial'
            if is_cvm: canal = 'cvm_oficial'
            elif is_social: canal = 'gossip_social'

            articles.append({
                'titulo': entry.title,
                'fonte': fonte_nome if not is_cvm else "CVM Oficial",
                'fonte_tipo': 'confiavel' if is_cvm else ('gossip' if is_social else classify_source(fonte_nome)),
                'origem_canal': canal,
                'data': pub_date,
                'link': entry.link,
                'ticker': ticker,
                'empresa': empresa_info['empresa'],
                'setor': empresa_info['setor'],
                'escala': empresa_info['escala'],
                'pais': 'BR'
            })
    return articles
