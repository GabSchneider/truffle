import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import news_collection, setup_indexes
from app.collectors import fetch_rss_news, fetch_b3_quotes, TICKERS_MAP
from app.sentiment import SentimentAnalyzer
from typing import Optional
from datetime import datetime, timedelta
import os

app = FastAPI(title="Truffle Finder API v9.0 Pro Analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentAnalyzer()

def run_full_collection():
    print(f"[{datetime.now()}] 🔄 Varredura Noturna v9.0 (Full Ibovespa) iniciada...")
    total_saved = 0
    for ticker in TICKERS_MAP.keys():
        rss_items = fetch_rss_news(ticker)
        for item in rss_items:
            sentiment = analyzer.analyze(
                item["titulo"], 
                item.get("fonte_tipo", "media"), 
                item.get("origem_canal", "midia_oficial"),
                ticker
            )
            item["sentimento"] = sentiment

            if not news_collection.find_one({"link": item["link"]}):
                news_collection.insert_one(item)
                total_saved += 1
    print(f"[{datetime.now()}] ✅ Varredura concluída! {total_saved} novas notícias salvas.")
    return total_saved

async def background_worker_247():
    while True:
        try:
            run_full_collection()
        except Exception as e:
            print(f"Erro no worker: {e}")
        await asyncio.sleep(900)

@app.on_event("startup")
def startup_event():
    try:
        setup_indexes()
    except Exception as e:
        print(f"Aviso DB: {e}")
    asyncio.create_task(background_worker_247())

@app.get("/")
def read_index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Truffle Finder API v9.0 Ativa"}

@app.post("/api/v1/collect")
def collect_and_process():
    total_saved = run_full_collection()
    return {"status": "success", "novas_noticias": total_saved}

@app.get("/api/v1/quotes")
def get_quotes():
    return fetch_b3_quotes()

@app.get("/api/v1/ibovespa/sentiment-index")
def get_ibovespa_index():
    seven_days = datetime.now() - timedelta(days=7)
    pipeline = [
        {"$match": {"data": {"$gte": seven_days}}},
        {"$group": {"_id": "$sentimento.label", "count": {"$sum": 1}}}
    ]
    results = list(news_collection.aggregate(pipeline))
    total = sum(r["count"] for r in results) or 1
    
    pos = next((r["count"] for r in results if r["_id"] == "positivo"), 0)
    neg = next((r["count"] for r in results if r["_id"] == "negativo"), 0)
    neu = next((r["count"] for r in results if r["_id"] == "neutro"), 0)

    net_score = (pos - neg) / total
    
    pct_pos = round((pos / total) * 100, 1)
    pct_neg = round((neg / total) * 100, 1)
    pct_neu = round((neu / total) * 100, 1)

    status = "NEUTRO"
    if net_score > 0.05:
        status = "BULLISH (FLUXO OTIMISTA)"
    elif net_score < -0.05:
        status = "BEARISH (FLUXO PESSIMISTA)"

    return {
        "status_geral": status,
        "net_sentiment_score": round(net_score, 3),
        "total_noticias_7d": total,
        "otimista_pct": pct_pos,
        "pessimista_pct": pct_neg,
        "neutro_pct": pct_neu
    }

@app.get("/api/v1/dashboard/timeline")
def get_sentiment_timeline():
    seven_days = datetime.now() - timedelta(days=7)
    pipeline = [
        {"$match": {"data": {"$gte": seven_days}}},
        {
            "$project": {
                "dia": {"$dateToString": {"format": "%Y-%m-%d", "date": "$data"}},
                "score": "$sentimento.score"
            }
        },
        {
            "$group": {
                "_id": "$dia",
                "score_medio": {"$avg": "$score"},
                "total": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    return list(news_collection.aggregate(pipeline))

@app.get("/api/v1/dashboard/top-rankings")
def get_top_rankings():
    seven_days = datetime.now() - timedelta(days=7)
    pipeline = [
        {"$match": {"data": {"$gte": seven_days}}},
        {
            "$group": {
                "_id": "$ticker",
                "score_medio": {"$avg": "$sentimento.score"},
                "total_noticias": {"$sum": 1}
            }
        }
    ]
    raw = list(news_collection.aggregate(pipeline))
    sorted_data = sorted(raw, key=lambda x: x["score_medio"], reverse=True)
    
    return {
        "top_otimistas": [
            {"ticker": item["_id"], "score": round(item["score_medio"], 3), "noticias": item["total_noticias"]}
            for item in sorted_data[:5]
        ],
        "top_pessimistas": [
            {"ticker": item["_id"], "score": round(item["score_medio"], 3), "noticias": item["total_noticias"]}
            for item in reversed(sorted_data[-5:])
        ]
    }

@app.get("/api/v1/heatmap")
def get_heatmap():
    """Retorna dados detalhados por empresa: contagem exata de boas, ruins e neutras"""
    pipeline = [
        {
            "$group": {
                "_id": {"ticker": "$ticker", "setor": "$setor"},
                "total": {"$sum": 1},
                "score_medio": {"$avg": "$sentimento.score"},
                "positivas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "positivo"]}, 1, 0]}},
                "negativas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "negativo"]}, 1, 0]}},
                "neutras": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "neutro"]}, 1, 0]}}
            }
        }
    ]
    raw = list(news_collection.aggregate(pipeline))
    heatmap_data = []
    for item in raw:
        t = item["_id"]["ticker"]
        s = item["_id"]["setor"]
        score = item["score_medio"]
        temp = "neutro"
        if score > 0.05: temp = "positivo"
        elif score < -0.05: temp = "negativo"

        heatmap_data.append({
            "ticker": t,
            "setor": s,
            "total_noticias": item["total"],
            "score": round(score, 3),
            "positivas": item["positivas"],
            "negativas": item["negativas"],
            "neutras": item["neutras"],
            "temperatura": temp
        })
    return heatmap_data

@app.get("/api/v1/news")
def get_news(
    ticker: Optional[str] = None, 
    setor: Optional[str] = None, 
    escala: Optional[str] = None,
    relevancia: Optional[str] = None,
    fonte_tipo: Optional[str] = None,
    pais: Optional[str] = None,
    periodo: Optional[str] = None,
    limit: int = 35
):
    query = {}
    if ticker and ticker != "TODOS" and ticker.strip() != "":
        query["ticker"] = ticker.upper().strip()
    if setor and setor != "TODOS":
        query["setor"] = setor
    if escala and escala != "TODOS":
        query["escala"] = escala
    if relevancia and relevancia != "TODAS":
        query["sentimento.relevancia"] = relevancia
    if fonte_tipo and fonte_tipo != "TODOS":
        query["fonte_tipo"] = fonte_tipo
    if pais and pais != "TODOS":
        query["pais"] = pais

    if periodo:
        now = datetime.now()
        if periodo == "hoje":
            query["data"] = {"$gte": now.replace(hour=0, minute=0, second=0)}
        elif periodo == "24h":
            query["data"] = {"$gte": now - timedelta(days=1)}
        elif periodo == "semana":
            query["data"] = {"$gte": now - timedelta(days=7)}

    results = list(news_collection.find(query, {"_id": 0}).sort("data", -1).limit(limit))
    return results

@app.get("/api/v1/dashboard/sector-consensus")
def get_sector_consensus():
    pipeline = [
        {
            "$group": {
                "_id": "$setor",
                "total": {"$sum": 1},
                "score_medio": {"$avg": "$sentimento.score"},
                "positivas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "positivo"]}, 1, 0]}},
                "negativas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "negativo"]}, 1, 0]}},
                "neutras": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "neutro"]}, 1, 0]}}
            }
        },
        {"$sort": {"total": -1}}
    ]
    return list(news_collection.aggregate(pipeline))

@app.get("/api/v1/clipping/weekly")
def get_weekly_clipping():
    seven_days_ago = datetime.now() - timedelta(days=7)
    pipeline = [
        {"$match": {"data": {"$gte": seven_days_ago}}},
        {
            "$group": {
                "_id": "$ticker",
                "total": {"$sum": 1},
                "score_medio": {"$avg": "$sentimento.score"}
            }
        },
        {"$sort": {"total": -1}}
    ]
    data = list(news_collection.aggregate(pipeline))
    total_noticias = sum(item["total"] for item in data)
    top_positivo = max(data, key=lambda x: x["score_medio"]) if data else None
    top_negativo = min(data, key=lambda x: x["score_medio"]) if data else None

    resumo = "Analise quantitativa e micro de sentimento da B3 ativa."
    if top_positivo and top_positivo["score_medio"] > 0.05:
        resumo += f" Destaque otimista para {top_positivo['_id']}."
    if top_negativo and top_negativo["score_medio"] < -0.05:
        resumo += f" Alerta de pressao em {top_negativo['_id']}."

    return {
        "periodo": "Últimos 7 dias",
        "total_analisado": total_noticias,
        "ticker_mais_positivo": top_positivo["_id"] if top_positivo else "N/A",
        "ticker_mais_negativo": top_negativo["_id"] if top_negativo else "N/A",
        "resumo_avaliativo": resumo,
        "detalhes": data
    }

@app.get("/api/v1/dashboard/metrics")
def get_dashboard_metrics(setor: Optional[str] = None):
    match_stage = {}
    if setor and setor != "TODOS":
        match_stage = {"setor": setor}

    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {
            "$group": {
                "_id": "$ticker",
                "total": {"$sum": 1},
                "score_medio": {"$avg": "$sentimento.score"},
                "positivas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "positivo"]}, 1, 0]}},
                "negativas": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "negativo"]}, 1, 0]}},
                "neutras": {"$sum": {"$cond": [{"$eq": ["$sentimento.label", "neutro"]}, 1, 0]}}
            }
        },
        {"$sort": {"total": -1}}
    ]
    return list(news_collection.aggregate(pipeline))

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
