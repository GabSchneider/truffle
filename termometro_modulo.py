import sqlite3

def calcular_termometro_b3(db_file="truffle_institutional.db"):
    """Calcula o índice de sentimento global do Ibovespa para o termômetro."""
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT sentimento, score_nlp FROM noticias")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"status": "Neutro", "score": 0.0, "percentual": 50, "total": 0, "positivas": 0, "negativas": 0, "neutras": 0}
            
        total = len(rows)
        positivas = sum(1 for r in rows if r["sentimento"] == "Positivo")
        negativas = sum(1 for r in rows if r["sentimento"] == "Negativo")
        neutras = total - (positivas + negativas)
        
        score_medio = sum(r["score_nlp"] for r in rows) / total
        percentual = int(round((score_medio + 1) * 50))
        
        if score_medio > 0.15:
            status = "🔥 Alta Otimista (Bullish)"
        elif score_medio < -0.15:
            status = "❄️ Pressão Pessimista (Bearish)"
        else:
            status = "⚖️ Mercado Lateral / Neutro"
            
        return {
            "status": status,
            "score": round(score_medio, 2),
            "percentual": max(0, min(100, percentual)),
            "total": total,
            "positivas": positivas,
            "negativas": negativas,
            "neutras": neutras
        }
    except Exception as e:
        return {"status": "Neutro", "score": 0.0, "percentual": 50, "total": 0, "positivas": 0, "negativas": 0, "neutras": 0}
