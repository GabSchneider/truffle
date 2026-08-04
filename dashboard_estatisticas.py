import sqlite3

def obter_estatisticas_avancadas(db_file="truffle_institutional.db"):
    """Retorna dados agregados por setor e sentimento para alimentar gráficos e contadores."""
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contagem por setor
        cursor.execute("SELECT setor, COUNT(*) as total FROM noticias GROUP BY setor")
        setores = {row["setor"]: row["total"] for row in cursor.fetchall()}
        
        # Contagem por sentimento
        cursor.execute("SELECT sentimento, COUNT(*) as total FROM noticias GROUP BY sentimento")
        sentimentos = {row["sentimento"]: row["total"] for row in cursor.fetchall()}
        
        conn.close()
        return {
            "setores": setores,
            "sentimentos": sentimentos
        }
    except Exception as e:
        return {"setores": {}, "sentimentos": {}}
