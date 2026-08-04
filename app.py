from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from backend import buscar_noticias_reais

st.set_page_config(
    page_title="Truffle Finder | Intelligence Dashboard",
    page_icon="💎",
    layout="wide",
)

dados_brutos = buscar_noticias_reais()
df = pd.DataFrame(dados_brutos)

st.sidebar.title("💎 Truffle Finder")
st.sidebar.markdown("Centro de Comando e Inteligência de Mídia B3")
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Filtros do Dashboard")

periodo = st.sidebar.selectbox("Período de Análise", ["Hoje", "Últimas 24h", "Semana", "Mês", "Ano"])
tickers_disponíveis = ["TODOS"] + list(df["ticker"].unique())
ticker_selecionado = st.sidebar.selectbox("Filtrar por Ticker / Empresa", tickers_disponíveis)
fontes_disponiveis = ["TODAS"] + list(df["tipo_fonte"].unique())
fonte_selecionada = st.sidebar.selectbox("Categoria de Fonte", fontes_disponiveis)

df_filtrado = df.copy()
if ticker_selecionado != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["ticker"] == ticker_selecionado]
if fonte_selecionada != "TODAS":
    df_filtrado = df_filtrado[df_filtrado["tipo_fonte"] == fonte_selecionada]

st.title("🚀 Truffle Finder: Intelligence Dashboard")
st.markdown("Monitoramento em tempo real de notícias, análise de sentimento por IA e termômetro do mercado B3.")
st.markdown("---")

total_noticias = len(df_filtrado)
positivas = len(df_filtrado[df_filtrado["sentimento"] == "Positivo"])
negativas = len(df_filtrado[df_filtrado["sentimento"] == "Negativo"])
neutras = len(df_filtrado[df_filtrado["sentimento"] == "Neutro"])

score_global = (positivas - negativas) / total_noticias if total_noticias > 0 else 0
if score_global > 0.2:
    termometro = "🔥 Alta Otimista (Bullish)"
elif score_global < -0.2:
    termometro = "❄️ Pressão Pessimista (Bearish)"
else:
    termometro = "⚖️ Mercado Neutro / Lateral"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="📊 Total de Notícias", value=total_noticias, delta=f"Filtro: {ticker_selecionado}")
with kpi2:
    st.metric(label="🌡️ Termômetro do Mercado", value=termometro)
with kpi3:
    st.metric(label="🟢 Sentimento Positivo", value=f"{positivas} ({(positivas/total_noticias*100) if total_noticias>0 else 0:.1f}%)")
with kpi4:
    st.metric(label="🔴 Sentimento Negativo", value=f"{negativas} ({(negativas/total_noticias*100) if total_noticias>0 else 0:.1f}%)")

st.markdown("---")

col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    st.subheader("📈 Distribuição de Sentimento por Ticker")
    if not df_filtrado.empty:
        fig_sentimento = px.histogram(
            df_filtrado, x="ticker", color="sentimento", barmode="group",
            color_discrete_map={"Positivo": "#00CC96", "Neutro": "#FFA15A", "Negativo": "#EF553B"},
            labels={"ticker": "Ticker", "count": "Quantidade de Notícias"}
        )
        st.plotly_chart(fig_sentimento, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para os filtros selecionados.")

with col_graf2:
    st.subheader("📰 Proporção por Categoria de Fonte")
    if not df_filtrado.empty:
        fig_fontes = px.pie(df_filtrado, names="tipo_fonte", hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_fontes, use_container_width=True)
    else:
        st.info("Nenhum dado disponível.")

st.markdown("---")
st.subheader("🔍 Feed de Notícias & Avaliações da Inteligência Artificial")

for index, row in df_filtrado.iterrows():
    with st.expander(f"[{row['ticker']}] {row['titulo']} — *Fonte: {row['fonte']} ({row['tipo_fonte']})*"):
        col_det1, col_det2 = st.columns([3, 1])
        with col_det1:
            st.markdown(f"**Data/Hora:** {row['data'].strftime('%d/%m/%Y %H:%M')}")
            st.markdown(f"**Link Original:** [Acessar Notícia]({row['link']})")
            st.markdown(f"**Parecer da IA:** *{row['analise_ia']}*")
        with col_det2:
            sentimento_cor = "🟢 Positivo" if row["sentimento"] == "Positivo" else ("🔴 Negativo" if row["sentimento"] == "Negativo" else "🟡 Neutro")
            st.markdown(f"**Sentimento:** {sentimento_cor}")
            st.metric(label="Score de Impacto", value=f"{row['score_ia']:.2f}")

st.markdown("---")
st.subheader("📑 Clipping Semanal / Resumo Executivo Automático")
st.info("**Resumo do Período:** O mercado brasileiro apresentou forte foco em commodities (VALE3 e PETR3) impulsionadas pelo cenário macro externo, enquanto o setor financeiro (ITUB4) manteve estabilidade com relatórios consistentes. Acompanhamento de rumores (Gossip) manteve-se restrito, reduzindo ruídos especulativos nos papéis de varejo.")
