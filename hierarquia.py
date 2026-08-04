from database import obter_tickers_b3

def construir_arvore_b3():
    """Agrupa os tickers oficiais da B3 de forma hierárquica: Macrosetor -> Subsetor -> Tickers"""
    tickers_dict = obter_tickers_b3()
    arvore = {}
    
    for ticker, info in tickers_dict.items():
        setor = info["setor"]
        subsetor = info["subsetor"]
        
        if setor not in arvore:
            arvore[setor] = {}
        if subsetor not in arvore[setor]:
            arvore[setor][subsetor] = []
            
        arvore[setor][subsetor].append({
            "ticker": ticker,
            "nome": info["nome"]
        })
        
    return arvore
