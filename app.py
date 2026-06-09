import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import math
import os
import json
import requests

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(page_title="AI Financial Analyst", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #d6d9de;
}

[data-testid="stHeader"],
[data-testid="stToolbar"] {
    display: none;
}

.block-container {
    padding-top: 95px !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 100% !important;
}

/* ===== BANNER FIXO ===== */
.st-key-top_bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
    background-color: #1f1f1f;
    padding: 18px 28px;
    margin: 0;
}

.st-key-top_bar [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-top_bar input {
    height: 44px !important;
    min-height: 44px !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    padding: 0px 12px !important;
    line-height: 44px !important;
}

.st-key-top_bar button {
    height: 44px !important;
    min-height: 44px !important;
    width: 52px !important;
    border-radius: 10px !important;
    font-size: 18px !important;
    padding: 0 !important;
}

.top-title {
    color: white;
    font-size: 28px;
    font-weight: 800;
    white-space: nowrap;
    padding-top: 4px;
}

/* ===== HEADER DO ATIVO ===== */
.st-key-asset_header {
    background-color: #eef0f3;
    border: 1px solid #b8bec8;
    border-radius: 14px;
    padding: 22px 25px 30px 25px;
    margin-bottom: 24px;
}

.st-key-asset_header [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 4px;
}

.logo-fallback {
    width: 80px;
    height: 80px;
    border-radius: 12px;
    background-color: #1f2937;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 800;
    margin: 0 !important;
    flex-shrink: 0;
}

.asset-logo {
    width: 80px;
    height: 80px;
    border-radius: 12px;
    background-color: white;
    object-fit: contain;
    padding: 5px;
    border: 1px solid #b8bec8;
    flex-shrink: 0;
}

.asset-ticker {
    font-size: 32px;
    font-weight: 800;
    color: #111827;
    line-height: 1;
    margin-bottom: 0px;
}

.asset-name {
    font-size: 18px;
    font-weight: 600;
    color: #4b5563;
    line-height: 1.2;
    margin-top: 2px;
}

/* ===== CARDS NUMÉRICOS ===== */
.number-card {
    background-color: white;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.number-label {
    background-color: #1f2937;
    color: white;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: 600;
}

.number-value {
    background-color: white;
    color: black;
    padding: 14px 12px;
    font-size: 28px;
    font-weight: 700;
}

.positive {
    color: green;
}

.negative {
    color: red;
}

/* ===== CARD DO GRÁFICO ===== */
.st-key-chart_card {
    background-color: white;
    border: 1px solid #b8bec8;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.st-key-chart_header {
    background-color: #1f2937;
    padding: 10px 14px;
    display: flex;
    align-items: center;
}

.chart-title {
    color: white;
    font-size: 15px;
    font-weight: 700;
    padding-top: 6px;
}

.st-key-chart_header button {
    min-height: 34px !important;
    height: 34px !important;
    padding: 0px 10px !important;
    font-size: 12px !important;
    border-radius: 8px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    vertical-align: middle !important;
}

.st-key-chart_header button:disabled {
    background-color: #9ca3af !important;
    color: #f3f4f6 !important;
    opacity: 1 !important;
    cursor: default !important;
}

.st-key-chart_header button > div {
    white-space: nowrap !important;
}

.st-key-chart_body {
    background-color: white;
    padding: 14px;
}

/* ===== MÁXIMA E MÍNIMA ===== */
.period-stats-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 8px;
}

.period-stat-card {
    background-color: white;
    border: 1px solid #b8bec8;
    border-radius: 10px;
    padding: 8px 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.period-stat-label {
    color: #4b5563;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 2px;
}

.period-stat-value {
    color: #111827;
    font-size: 17px;
    font-weight: 400;
}

.period-stat-value .period-stat-amount {
    font-weight: 800;
}

.period-stat-value .period-stat-date {
    font-weight: 400;
    font-size: 13px;
    color: #6b7280;
    margin-left: 6px;
}

/* ===== INDICADORES ===== */
.fund-title {
    color: #111827;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 14px;
}

.indicator-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.indicator-card {
    background-color: white;
    border: 1px solid #b8bec8;
    border-radius: 12px;
    padding: 12px 10px;
    min-height: 78px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.indicator-label {
    color: #4b5563;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
}

.indicator-value {
    color: #111827;
    font-size: 18px;
    font-weight: 800;
}

/* ===== ÁREA DE IA ===== */
.ai-card {
    margin-top: 24px;
    background-color: white;
    border: 1px solid #b8bec8;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.ai-header {
    background-color: #1f2937;
    color: white;
    padding: 12px 16px;
    font-size: 17px;
    font-weight: 800;
}

.ai-body {
    padding: 18px;
}

.ai-grid-response {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
}

.ai-response-box {
    background-color: white;
    border: 1px solid #b8bec8;
    border-radius: 12px;
    overflow: hidden;
}

.ai-response-title {
    background-color: #1f2937;
    color: white;
    padding: 9px 12px;
    font-size: 14px;
    font-weight: 800;
}

.ai-response-content {
    padding: 14px 16px;
    color: #111827;
    font-size: 15px;
    line-height: 1.65;
}

.ai-response-content ul {
    margin: 0;
    padding-left: 18px;
}

.ai-response-content li {
    margin-bottom: 7px;
}

.ai-full {
    grid-column: span 2;
}

.ai-disclaimer {
    margin-top: 14px;
    color: #6b7280;
    font-size: 12px;
}
.ai-card + .stButton {
    margin-top: 0 !important;
}
.ai-card + .stButton > button {
    width: 100% !important;
    background-color: #1f2937 !important;
    color: white !important;
    border: none !important;
    border-radius: 0 0 14px 14px !important;
    height: 50px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}
.ai-card + .stButton > button:hover {
    background-color: #111827 !important;
}

/* ===== AJUSTE INTERATIVIDADE (MENUS E SELECTBOXES) ===== */
div[data-testid="stSelectbox"], 
div[data-testid="stSelectbox"] * {
    cursor: pointer !important;
    user-select: none !important;
}

div[data-testid="stSelectbox"] input {
    caret-color: transparent !important;
    pointer-events: none !important; /* Impede digitação e seleção de texto */
}
</style>
""", unsafe_allow_html=True)


def normalizar_ticker(ticker):
    ticker = ticker.strip().upper()

    if "." in ticker or "-" in ticker:
        return ticker

    if any(char.isdigit() for char in ticker):
        return ticker + ".SA"

    return ticker


def valor_valido(valor):
    return valor is not None and not (isinstance(valor, float) and math.isnan(valor))


def formatar_moeda(valor, moeda):
    if not valor_valido(valor):
        return "N/A"

    # Formatar com ponto de milhar e vírgula decimal (padrão brasileiro)
    valor_formatado = f"{valor:,.2f}".replace(",", "|").replace(".", ",").replace("|", ".")

    if moeda == "BRL":
        return f"R$ {valor_formatado}"
    elif moeda == "USD":
        return f"US$ {valor_formatado}"

    return f"{moeda} {valor_formatado}"


def formatar_numero(valor):
    if not valor_valido(valor):
        return "N/A"

    return f"{valor:.2f}"


def formatar_percentual(valor):
    if not valor_valido(valor):
        return "N/A"

    return f"{valor * 100:.2f}%"


def formatar_percentual_de_valor_percentual(valor):
    if not valor_valido(valor):
        return "N/A"

    return f"{valor:.2f}%"


def obter_brapi_token():
    return os.getenv("BRAPI_API_KEY") or os.getenv("BRAPI_TOKEN")


def normalizar_ticker_brapi(ticker):
    return ticker.strip().upper().replace(".SA", "")


def obter_valor_aninhado(dados, caminhos):
    for caminho in caminhos:
        atual = dados
        for parte in caminho.split("."):
            if not isinstance(atual, dict) or parte not in atual:
                atual = None
                break
            atual = atual.get(parte)

        if valor_valido(atual):
            return atual

    return None


def executar_requisicao_brapi(ticker, params=None):
    ticker = normalizar_ticker_brapi(ticker)
    token = obter_brapi_token()
    url = f"https://brapi.dev/api/quote/{ticker}"
    headers = {}
    params = params.copy() if params else {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, params=params, headers=headers, timeout=20)

    if response.status_code == 401:
        raise ValueError("Token da brapi ausente ou invÃ¡lido. Configure BRAPI_API_KEY no ambiente do site.")

    if response.status_code == 429:
        raise ValueError("Limite de requisiÃ§Ãµes da brapi excedido. Tente novamente em alguns minutos ou aumente o plano da API.")

    response.raise_for_status()

    data = response.json()

    if data.get("error"):
        raise ValueError(data.get("message", "Erro ao consultar a brapi."))

    resultados = data.get("results", [])

    if not resultados:
        return {}

    return resultados[0]


@st.cache_data(ttl=300)
def buscar_info(ticker):
    resultado = executar_requisicao_brapi(
        ticker,
        {
            "modules": "summaryProfile,defaultKeyStatistics,financialData"
        }
    )

    return {
        "symbol": resultado.get("symbol"),
        "shortName": resultado.get("shortName"),
        "longName": resultado.get("longName") or resultado.get("shortName"),
        "currency": resultado.get("currency", "BRL"),
        "regularMarketPrice": resultado.get("regularMarketPrice"),
        "regularMarketOpen": resultado.get("regularMarketOpen"),
        "trailingPE": obter_valor_aninhado(resultado, [
            "trailingPE",
            "priceEarnings",
            "defaultKeyStatistics.trailingPE",
            "defaultKeyStatistics.priceEarnings",
        ]),
        "priceToBook": obter_valor_aninhado(resultado, [
            "priceToBook",
            "defaultKeyStatistics.priceToBook",
        ]),
        "payoutRatio": obter_valor_aninhado(resultado, [
            "payoutRatio",
            "defaultKeyStatistics.payoutRatio",
        ]),
        "profitMargins": obter_valor_aninhado(resultado, [
            "profitMargins",
            "financialData.profitMargins",
        ]),
        "grossMargins": obter_valor_aninhado(resultado, [
            "grossMargins",
            "financialData.grossMargins",
        ]),
        "ebitdaMargins": obter_valor_aninhado(resultado, [
            "ebitdaMargins",
            "financialData.ebitdaMargins",
        ]),
        "enterpriseToEbitda": obter_valor_aninhado(resultado, [
            "enterpriseToEbitda",
            "defaultKeyStatistics.enterpriseToEbitda",
        ]),
        "returnOnEquity": obter_valor_aninhado(resultado, [
            "returnOnEquity",
            "financialData.returnOnEquity",
        ]),
        "debtToEquity": obter_valor_aninhado(resultado, [
            "debtToEquity",
            "financialData.debtToEquity",
        ]),
        "dividendYield": obter_valor_aninhado(resultado, [
            "dividendYield",
            "defaultKeyStatistics.dividendYield",
        ]),
    }


@st.cache_data(ttl=60)
def buscar_historico(ticker, periodo):
    intervalo = "5m" if periodo == "1d" else "1d"
    resultado = executar_requisicao_brapi(
        ticker,
        {
            "range": periodo,
            "interval": intervalo
        }
    )

    historico = resultado.get("historicalDataPrice", [])

    if not historico:
        return pd.DataFrame()

    df = pd.DataFrame(historico)

    if "date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["date"], unit="s", errors="coerce")

    colunas = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }

    df = df.rename(columns=colunas)
    colunas_necessarias = ["Open", "High", "Low", "Close"]

    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            return pd.DataFrame()

    df = df.dropna(subset=["Date", "Close"]).set_index("Date").sort_index()

    return df


@st.cache_data(ttl=3600)
def buscar_dividendos(ticker):
    resultado = executar_requisicao_brapi(ticker, {"dividends": "true"})
    dividendos_data = resultado.get("dividendsData") or {}
    dividendos = dividendos_data.get("cashDividends") or dividendos_data.get("stockDividends") or []

    if not dividendos:
        return pd.DataFrame()

    df = pd.DataFrame(dividendos)

    data_coluna = next((col for col in ["paymentDate", "lastDatePrior", "approvedOn", "date"] if col in df.columns), None)
    valor_coluna = next((col for col in ["rate", "value", "amount", "cashDividends"] if col in df.columns), None)

    if not data_coluna or not valor_coluna:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df[data_coluna], errors="coerce")
    df["Dividend"] = pd.to_numeric(df[valor_coluna], errors="coerce")
    df = df.dropna(subset=["Date", "Dividend"]).set_index("Date").sort_index()

    return df


# Camada de dados ativa: usa yfinance com cache para reduzir o risco de rate limit.
# As funcoes abaixo sobrescrevem as funcoes antigas da brapi acima.
def erro_rate_limit(erro):
    texto = str(erro).lower()
    return "too many requests" in texto or "rate limit" in texto or "429" in texto


def normalizar_historico_yfinance(df):
    if df is None or df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    colunas = ["Open", "High", "Low", "Close", "Volume"]
    colunas_existentes = [coluna for coluna in colunas if coluna in df.columns]
    df = df[colunas_existentes].copy()

    for coluna in ["Open", "High", "Low", "Close"]:
        if coluna not in df.columns:
            return pd.DataFrame()

    return df.dropna(subset=["Close"]).sort_index()


def filtrar_ultimo_pregao(df):
    if df.empty:
        return df

    try:
        ultimo_dia = df.index.max().date()
        return df[df.index.date == ultimo_dia]
    except Exception:
        return df.tail(1)


def primeiro_valor_linha(df, nomes_linhas):
    if df is None or df.empty:
        return None

    for nome in nomes_linhas:
        if nome in df.index:
            serie = pd.to_numeric(df.loc[nome], errors="coerce").dropna()

            if not serie.empty:
                return float(serie.iloc[0])

    return None


def definir_se_ausente(info, chave, valor):
    if not valor_valido(info.get(chave)) and valor_valido(valor):
        info[chave] = valor


def preencher_info_por_demonstrativos(ativo, info):
    try:
        demonstracao_resultado = ativo.income_stmt
        balanco = ativo.balance_sheet
        fluxo_caixa = ativo.cashflow
    except Exception as erro:
        info["statements_error"] = str(erro)
        return info

    preco = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("regularMarketPreviousClose")
        or info.get("regularMarketPrice")
    )
    valor_mercado = info.get("marketCap")

    receita = primeiro_valor_linha(demonstracao_resultado, ["Total Revenue", "Operating Revenue"])
    lucro_liquido = primeiro_valor_linha(demonstracao_resultado, [
        "Net Income",
        "Net Income Common Stockholders",
        "Net Income From Continuing Operation Net Minority Interest",
    ])
    lucro_bruto = primeiro_valor_linha(demonstracao_resultado, ["Gross Profit"])
    ebitda = primeiro_valor_linha(demonstracao_resultado, ["EBITDA", "Normalized EBITDA"])
    lucro_por_acao = primeiro_valor_linha(demonstracao_resultado, ["Diluted EPS", "Basic EPS"])

    patrimonio = primeiro_valor_linha(balanco, [
        "Common Stock Equity",
        "Stockholders Equity",
        "Total Equity Gross Minority Interest",
    ])
    divida_total = primeiro_valor_linha(balanco, ["Total Debt"])
    caixa = primeiro_valor_linha(balanco, [
        "Cash Cash Equivalents And Short Term Investments",
        "Cash And Cash Equivalents",
    ])
    dividendos_pagos = primeiro_valor_linha(fluxo_caixa, [
        "Cash Dividends Paid",
        "Common Stock Dividend Paid",
    ])

    if not valor_valido(valor_mercado) and valor_valido(preco) and valor_valido(patrimonio):
        acoes = primeiro_valor_linha(balanco, ["Ordinary Shares Number", "Share Issued"])
        if valor_valido(acoes):
            valor_mercado = preco * acoes
            info["marketCap"] = valor_mercado

    if valor_valido(preco) and valor_valido(lucro_por_acao) and lucro_por_acao != 0:
        definir_se_ausente(info, "trailingPE", preco / lucro_por_acao)
    elif valor_valido(valor_mercado) and valor_valido(lucro_liquido) and lucro_liquido != 0:
        definir_se_ausente(info, "trailingPE", valor_mercado / lucro_liquido)

    if valor_valido(valor_mercado) and valor_valido(patrimonio) and patrimonio != 0:
        definir_se_ausente(info, "priceToBook", valor_mercado / patrimonio)

    if valor_valido(dividendos_pagos) and valor_valido(lucro_liquido) and lucro_liquido != 0:
        definir_se_ausente(info, "payoutRatio", abs(dividendos_pagos) / lucro_liquido)

    if valor_valido(receita) and receita != 0:
        definir_se_ausente(info, "profitMargins", lucro_liquido / receita if valor_valido(lucro_liquido) else None)
        definir_se_ausente(info, "grossMargins", lucro_bruto / receita if valor_valido(lucro_bruto) else None)
        definir_se_ausente(info, "ebitdaMargins", ebitda / receita if valor_valido(ebitda) else None)

    if valor_valido(valor_mercado) and valor_valido(ebitda) and ebitda != 0:
        valor_empresa = valor_mercado
        valor_empresa += divida_total if valor_valido(divida_total) else 0
        valor_empresa -= caixa if valor_valido(caixa) else 0
        definir_se_ausente(info, "enterpriseToEbitda", valor_empresa / ebitda)

    if valor_valido(lucro_liquido) and valor_valido(patrimonio) and patrimonio != 0:
        definir_se_ausente(info, "returnOnEquity", lucro_liquido / patrimonio)

    if valor_valido(divida_total) and valor_valido(patrimonio) and patrimonio != 0:
        definir_se_ausente(info, "debtToEquity", divida_total / patrimonio)

    return info


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def buscar_info(ticker):
    ativo = yf.Ticker(ticker)
    info = {
        "symbol": ticker,
        "shortName": ticker,
        "longName": ticker,
        "currency": "BRL" if ticker.endswith(".SA") else "USD",
    }

    try:
        fast_info = dict(ativo.fast_info or {})
        info["currency"] = fast_info.get("currency") or info["currency"]
        info["regularMarketPrice"] = fast_info.get("last_price")
        info["regularMarketOpen"] = fast_info.get("open")
    except Exception:
        pass

    try:
        info_yf = ativo.info or {}
        info.update(info_yf)
    except Exception as erro:
        if erro_rate_limit(erro):
            info["rate_limit"] = True
        else:
            info["info_error"] = str(erro)

    # Fallback para logo via brapi caso o yfinance não retorne (comum em .SA)
    if not info.get("logo_url"):
        try:
            brapi_res = executar_requisicao_brapi(ticker)
            if brapi_res.get("logourl"):
                info["logo_url"] = brapi_res.get("logourl")
        except:
            pass

    return info


@st.cache_data(ttl=120, show_spinner=False)
def buscar_historico(ticker, periodo):
    intervalo = "5m" if periodo == "1d" else "1d"

    try:
        if periodo == "15y":
            inicio = (pd.Timestamp.today() - pd.DateOffset(years=15)).strftime("%Y-%m-%d")
            historico = yf.download(
                ticker,
                start=inicio,
                interval=intervalo,
                progress=False,
                auto_adjust=False,
                threads=False
            )
        else:
            historico = yf.download(
                ticker,
                period=periodo,
                interval=intervalo,
                progress=False,
                auto_adjust=False,
                threads=False
            )

        historico = normalizar_historico_yfinance(historico)

        if historico.empty and periodo == "1d":
            tentativas_fallback = [
                ("2d", "5m"),
                ("5d", "15m"),
                ("5d", "1d"),
            ]

            for periodo_fallback, intervalo_fallback in tentativas_fallback:
                historico_fallback = yf.download(
                    ticker,
                    period=periodo_fallback,
                    interval=intervalo_fallback,
                    progress=False,
                    auto_adjust=False,
                    threads=False
                )
                historico = normalizar_historico_yfinance(historico_fallback)

                if not historico.empty:
                    return filtrar_ultimo_pregao(historico)

        return historico

    except Exception as erro:
        if erro_rate_limit(erro):
            raise RuntimeError("Yahoo Finance bloqueou temporariamente novas consultas por excesso de requests.")
        raise


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def buscar_dividendos(ticker):
    try:
        dividendos = yf.Ticker(ticker).dividends
    except Exception:
        return pd.DataFrame()

    if dividendos is None or dividendos.empty:
        return pd.DataFrame()

    return dividendos.to_frame(name="Dividend")


def calcular_dividend_yield_12m(ticker, preco_atual, info):
    dividendos = buscar_dividendos(ticker)

    if not dividendos.empty and preco_atual != 0:
        data_limite = pd.Timestamp.now(tz=dividendos.index.tz) - pd.DateOffset(months=12)
        dividendos_12m = dividendos[dividendos.index >= data_limite]
        total_dividendos_12m = dividendos_12m["Dividend"].sum()

        if total_dividendos_12m > 0:
            dividend_yield = total_dividendos_12m / preco_atual
            return formatar_percentual(dividend_yield)

    dy_anual = info.get("trailingAnnualDividendYield")
    if valor_valido(dy_anual):
        return formatar_percentual(dy_anual)

    dy_info = info.get("dividendYield")
    if valor_valido(dy_info):
        return formatar_percentual_de_valor_percentual(dy_info)

    return "N/A"


def calcular_cagr_5a(ticker):
    historico_5a = buscar_historico(ticker, "5y")

    if historico_5a.empty:
        return "N/A"

    preco_inicial = historico_5a["Close"].iloc[0]
    preco_final = historico_5a["Close"].iloc[-1]

    if preco_inicial == 0:
        return "N/A"

    cagr = (preco_final / preco_inicial) ** (1 / 5) - 1

    return f"{cagr * 100:.2f}%"


def calcular_valor_investido(ticker, periodo, valor_investido):
    historico_periodo = buscar_historico(ticker, periodo)

    if historico_periodo.empty or valor_investido <= 0:
        return None

    preco_inicial = historico_periodo["Open"].iloc[0] if periodo == "1d" else historico_periodo["Close"].iloc[0]
    preco_final = historico_periodo["Close"].iloc[-1]

    if preco_inicial == 0:
        return None

    fator_retorno = preco_final / preco_inicial
    return valor_investido * fator_retorno


def obter_label_periodo(periodo):
    labels = {
        "1d": "1 dia",
        "5d": "5 dias",
        "1mo": "1 mês",
        "6mo": "6 meses",
        "ytd": "YTD",
        "1y": "1 ano",
        "5y": "5 anos",
        "10y": "10 anos",
        "15y": "15 anos"
    }

    return labels.get(periodo, periodo)


def criar_logo_fallback(ticker):
    letra = ticker.replace(".SA", "")[0]

    return f"""
    <div class="logo-fallback">
        {letra}
    </div>
    """


def criar_card(label, valor, classe_extra=""):
    st.markdown(
        f"""
        <div class="number-card">
            <div class="number-label">{label}</div>
            <div class="number-value {classe_extra}">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def criar_indicadores_html(indicadores):
    cards = ""

    for label, valor in indicadores:
        cards += f"""
<div class="indicator-card">
    <div class="indicator-label">{label}</div>
    <div class="indicator-value">{valor}</div>
</div>
"""

    return f"""
<div class="indicator-grid">
{cards}
</div>
"""

def normalizar_score(score):
    if score is None:
        return None

    if isinstance(score, str):
        texto = score.strip().replace(",", ".")

        if "/" in texto:
            texto = texto.split("/")[0].strip()

        if ":" in texto:
            texto = texto.split(":")[-1].strip()

        try:
            return float(texto)
        except ValueError:
            return None

    try:
        return float(score)
    except (TypeError, ValueError):
        return None


def cor_score(score):
    score = normalizar_score(score)
    if score is None:
        return "#6b7280"
    if score <= 3:
        return "#dc2626"
    elif score <= 5:
        return "#ff7a00"
    elif score <= 7:
        return "#ffd500"
    elif score <= 8:
        return "#9be000"
    elif score <= 9:
        return "#4caf50"
    else:
        return "#0f9d58"


def criar_score_html(score):
    score = normalizar_score(score)
    cor = cor_score(score)
    score_texto = f"{score:.1f}" if score is not None else "N/A"

    return f"""
<div style="
    background-color: {cor};
    color: black;
    padding: 18px;
    border-radius: 10px;
    font-size: 26px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
">
    Score da IA: {score_texto} / 10
</div>
"""

# =========================
# NOVO - BUSCAR NOTÍCIAS
# =========================
def buscar_noticias(ticker):
    try:
        url = "https://api.marketaux.com/v1/news/all"

        params = {
            "symbols": ticker,
            "language": "en",
            "filter_entities": True,
            "limit": 5,
            "api_token": os.getenv("NEWS_API_KEY")
        }

        response = requests.get(url, params=params)
        data = response.json()

        noticias = []

        for item in data.get("data", []):
            noticias.append({
                "titulo": item.get("title"),
                "sentimento": item.get("sentiment", "neutral")
            })

        return noticias

    except:
        return []

def gerar_analise_openai(
    ticker,
    nome_ativo,
    preco_atual,
    moeda,
    variacao_periodo,
    dividend_yield,
    maxima_periodo,
    minima_periodo,
    periodo,
    info
):

    noticias = buscar_noticias(ticker)

    noticias_texto = "\n".join([
        f"- {n['titulo']} ({n['sentimento']})"
        for n in noticias
    ]) if noticias else "Sem notícias relevantes."

    prompt = f"""
Você é um analista financeiro profissional.

Faça uma análise COMPLETA considerando:
- fundamentos
- risco
- qualidade do ativo
- NOTÍCIAS recentes

RETORNE SOMENTE JSON:

{{
  "score": número de 0 a 10,
  "resumo_executivo": "",
  "pontos_positivos": [],
  "pontos_atencao": [],
  "perfil_ativo": "",
  "resumo_noticias": "",
  "conclusao_educativa": ""
}}

DADOS:

Ativo: {ticker}
Empresa: {nome_ativo}

Preço: {formatar_moeda(preco_atual, moeda)}
Variação: {variacao_periodo:.2f}%
Dividend Yield: {dividend_yield}

P/L: {formatar_numero(info.get("trailingPE"))}
ROE: {formatar_percentual(info.get("returnOnEquity"))}
Margem Líquida: {formatar_percentual(info.get("profitMargins"))}
Dívida/Patrimônio: {formatar_numero(info.get("debtToEquity"))}

NOTÍCIAS:
{noticias_texto}

REGRAS:
- Interprete, não repita números
- Notícias negativas reduzem score
- Notícias positivas aumentam score
- "resumo_noticias" deve explicar impacto no ativo
"""

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um analista financeiro profissional especializado em mercado de capitais."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(resposta.choices[0].message.content)


def lista_para_html(lista):
    if not lista:
        return "<p>Dado não disponível.</p>"

    itens = "".join([f"<li>{item}</li>" for item in lista])
    return f"<ul>{itens}</ul>"


def criar_bloco_ia(titulo, conteudo, full=False):
    classe_extra = " ai-full" if full else ""

    return f"""
<div class="ai-response-box{classe_extra}">
    <div class="ai-response-title">{titulo}</div>
    <div class="ai-response-content">
        {conteudo}
    </div>
</div>
"""


def criar_analise_openai_html(analise):

    score_html = ""
    if "score" in analise:
        score_html = criar_score_html(analise["score"])

    return f"""
{score_html}

<div class="ai-grid-response">
    {criar_bloco_ia("Resumo executivo", f"<p>{analise.get('resumo_executivo', 'N/A')}</p>")}
    {criar_bloco_ia("Perfil do ativo", f"<p>{analise.get('perfil_ativo', 'N/A')}</p>")}
    {criar_bloco_ia("Pontos positivos", lista_para_html(analise.get("pontos_positivos", [])))}
    {criar_bloco_ia("Pontos de atenção", lista_para_html(analise.get("pontos_atencao", [])))}
    {criar_bloco_ia("Resumo das notícias", f"<p>{analise.get('resumo_noticias', 'N/A')}</p>", full=True)}
    {criar_bloco_ia("Conclusão educativa", f"<p>{analise.get('conclusao_educativa', 'N/A')}</p>", full=True)}
</div>

<div class="ai-disclaimer">
Análise gerada por IA com base nos dados disponíveis. Não é recomendação de investimento.
</div>
"""



periodos = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "6M": "6mo",
    "YTD": "ytd",
    "1A": "1y",
    "5A": "5y",
    "10A": "10y",
    "15A": "15y",
    "Máx": "max"
}

# --- Persistência de Dados Local ---
WATCHLIST_FILE = "watchlist.json"

def carregar_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"Favoritos": []}
    return {"Favoritos": []}

def salvar_watchlist():
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.watchlist, f, indent=4)
# ----------------------------------

if "periodo" not in st.session_state:
    st.session_state.periodo = "1d"

if "ticker" not in st.session_state:
    st.session_state.ticker = "PETR4.SA"

if "analise_ia" not in st.session_state:
    st.session_state.analise_ia = ""

if "watchlist" not in st.session_state:
    st.session_state.watchlist = carregar_watchlist()

if "lista_selecionada" not in st.session_state:
    st.session_state.lista_selecionada = list(st.session_state.watchlist.keys())[0] if st.session_state.watchlist else "Favoritos"

if "listas_periodo" not in st.session_state:
    st.session_state.listas_periodo = "1d"

if "listas_sort" not in st.session_state:
    st.session_state.listas_sort = "Alfabeto"

if "pagina" not in st.session_state:
    st.session_state.pagina = "Análise"

if "last_updated" not in st.session_state:
    st.session_state.last_updated = pd.Timestamp.now().strftime("%H:%M:%S")

# simulador acompanha mudança do gráfico (apenas visualmente)
if "sim_period" not in st.session_state:
     # encontra o rótulo correspondente ao período atual
     sim_label = None
     for k, v in periodos.items():
          if v == st.session_state.periodo:
                sim_label = k
                break
     st.session_state.sim_period = sim_label or "1D"

with st.container(key="top_bar"):
    top_col_nav, top_col_search, top_col_spacer = st.columns([1.5, 2, 1.5], gap="small")

    with top_col_nav:
        nav_col, refresh_col = st.columns([0.8, 0.2])
        with nav_col:
            selected_nav_page = st.selectbox(
                "Navegação",
                ["Análise", "Listas"],
                label_visibility="collapsed",
                index=0 if st.session_state.pagina == "Análise" else 1
            )
            if selected_nav_page != st.session_state.pagina:
                st.session_state.pagina = selected_nav_page
                st.rerun()
        with refresh_col:
            if st.button("🔄", help=f"Forçar atualização de dados. Última atualização: {st.session_state.last_updated}"):
                st.cache_data.clear()
                st.session_state.last_updated = pd.Timestamp.now().strftime("%H:%M:%S")
                st.rerun()

    with top_col_search:
        with st.form(key="form_ativo"):
            search_col, button_col = st.columns([9, 1])

            with search_col:
                ticker_digitado = st.text_input(
                    "Pesquisar ativo",
                    value="",
                    placeholder="Pesquisar por ativos",
                    label_visibility="collapsed"
                )

            with button_col:
                analisar = st.form_submit_button("🔍")

    with top_col_spacer:
        st.markdown('<div class="top-title" style="text-align:right">AI Analyst</div>', unsafe_allow_html=True)

if analisar and ticker_digitado.strip() != "":
    st.session_state.ticker = normalizar_ticker(ticker_digitado)
    st.session_state.periodo = "1d"
    st.session_state.analise_ia = ""
    st.session_state.pagina = "Análise"
    # ao pesquisar novo ativo, resetar visual do simulador para 1d (mesmo padrão do gráfico)
    sim_label = None
    for k, v in periodos.items():
        if v == st.session_state.periodo:
            sim_label = k
            break
    st.session_state.sim_period = sim_label or "1D"

def criar_sparkline(df, cor_fundo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        line=dict(color='white', width=2),
        hoverinfo='none'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=35,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        dragmode=False
    )
    return fig

def exibir_pagina_favoritos():
    # Exibe mensagens de sucesso pendentes (que sobreviveram ao rerun)
    if "msg_sucesso" in st.session_state:
        st.success(st.session_state.msg_sucesso)
        del st.session_state.msg_sucesso

    st.markdown('<div class="fund-title">📋 Minhas Listas de Ativos</div>', unsafe_allow_html=True)
    
    # Área de Gerenciamento de Listas
    with st.expander("🛠️ Gerenciar Listas", expanded=False):
        col_l1, col_l2 = st.columns([3, 1])
        nova_lista_nome = col_l1.text_input("Nome da nova lista", placeholder="Ex: Dividendos, Tech...")
        col_l2.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        if col_l2.button("Criar Lista", use_container_width=True) and nova_lista_nome:
            if nova_lista_nome not in st.session_state.watchlist:
                st.session_state.watchlist[nova_lista_nome] = []
                st.session_state.lista_selecionada = nova_lista_nome
                salvar_watchlist()
                st.session_state.msg_sucesso = "Lista criada com sucesso"
                st.rerun()

    if not st.session_state.watchlist:
        st.info("Crie uma lista para começar.")
        return

    # Filtros e Adição
    f_col_sort, f_col_ref, f_col_spacer = st.columns([1, 0.2, 2.3])
    with f_col_sort:
        st.session_state.listas_sort = st.selectbox(
            "Ordenar por", 
            options=["Alfabeto", "Preço", "Variação (%)"]
        )
    with f_col_ref:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        if st.button("🔄", key="ref_listas", help=f"Atualizar cotações da lista. Última atualização: {st.session_state.last_updated}"):
            # Limpa o cache para garantir que buscar_info e buscar_historico tragam dados novos
            st.cache_data.clear()
            st.session_state.last_updated = pd.Timestamp.now().strftime("%H:%M:%S")
            st.rerun()
    
    st.markdown("---")
    c1, c2, c3 = st.columns([2, 2, 1])
    
    # Sincroniza o índice da lista selecionada para evitar o reset ao atualizar as cotações
    opcoes_disponiveis = list(st.session_state.watchlist.keys())
    idx_selecionado = 0
    if st.session_state.lista_selecionada in opcoes_disponiveis:
        idx_selecionado = opcoes_disponiveis.index(st.session_state.lista_selecionada)

    # Removemos o 'key' para evitar conflitos de sincronização interna do Streamlit durante o rerun
    lista_selecao = c1.selectbox(
        "Selecione a Lista", 
        options=opcoes_disponiveis,
        index=idx_selecionado
    )
    
    # Se a seleção mudou manualmente, atualizamos o estado e forçamos o rerun
    if lista_selecao != st.session_state.lista_selecionada:
        st.session_state.lista_selecionada = lista_selecao
        st.rerun()

    lista_atual = st.session_state.lista_selecionada

    novo_ativo_lista = c2.text_input("Adicionar ativo à lista", placeholder="PETR4.SA, AAPL...")
    c3.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
    if c3.button("Adicionar", use_container_width=True) and novo_ativo_lista:
        ticker_norm = normalizar_ticker(novo_ativo_lista)
        if ticker_norm not in st.session_state.watchlist[lista_atual]:
            st.session_state.watchlist[lista_atual].append(ticker_norm)
            salvar_watchlist()
            st.session_state.msg_sucesso = f"Ativo adicionado a {lista_atual}"
            st.rerun()

    ativos_na_lista = st.session_state.watchlist[lista_atual]
    
    if not ativos_na_lista:
        st.info(f"A lista '{lista_atual}' está vazia.")
        return

    # Busca dados em lote
    tickers_str = " ".join(ativos_na_lista)
    try:
        with st.spinner("Atualizando cotações..."):
            dados = yf.download(tickers_str, period="2d", interval="1d", progress=False, group_by='ticker')
        
        lista_resumo = []
        for t in ativos_na_lista:
            try:
                # Correção: yfinance retorna MultiIndex apenas para múltiplos ativos.
                # Se houver apenas 1, o DataFrame é plano e deve ser usado diretamente.
                if isinstance(dados.columns, pd.MultiIndex):
                    df_t = dados[t]
                else:
                    df_t = dados
                
                df_t = df_t.dropna(subset=["Close"])
                
                if len(df_t) >= 1:
                    preco = df_t["Close"].iloc[-1]
                    ref = df_t["Close"].iloc[-2] if len(df_t) > 1 else df_t["Open"].iloc[-1]
                    variacao = ((preco - ref) / ref) * 100
                    
                    lista_resumo.append({
                        "Ativo": t,
                        "Preço": round(preco, 2),
                        "Variação (%)": round(variacao, 2),
                        "historico": df_t
                    })
            except:
                continue

        if lista_resumo:
            # Ordenação
            if st.session_state.listas_sort == "Alfabeto":
                lista_resumo.sort(key=lambda x: x['Ativo'])
            elif st.session_state.listas_sort == "Preço":
                lista_resumo.sort(key=lambda x: x['Preço'], reverse=True)
            elif st.session_state.listas_sort == "Variação (%)":
                lista_resumo.sort(key=lambda x: x['Variação (%)'], reverse=True)

            # Design em Cards (Caixinhas)
            cols_per_row = 5
            
            # CSS injetado uma única vez para garantir o visual dos 3 pontos (⋮)
            st.markdown("""
                <style>
                div[data-testid="stPopover"] {
                    margin-top: -125px !important; 
                    display: flex !important;
                    justify-content: flex-end !important;
                    background: transparent !important;
                    z-index: 100 !important;
                }
                
                div[data-testid="stPopover"] > button {
                    background: none !important;
                    background-color: transparent !important;
                    border: none !important;
                    box-shadow: none !important;
                    color: white !important;
                    font-size: 26px !important;
                    font-weight: 900 !important;
                    padding: 0 !important;
                    margin-right: 12px !important;
                    min-height: unset !important;
                }

                div[data-testid="stPopover"] > button:hover, 
                div[data-testid="stPopover"] > button:active, 
                div[data-testid="stPopover"] > button:focus {
                    background: transparent !important;
                    background-color: transparent !important;
                    color: #cbd5e1 !important;
                }

                div[data-testid="stPopover"] [data-testid="stIcon"] {
                    display: none !important;
                }
                </style>
            """, unsafe_allow_html=True)

            for i in range(0, len(lista_resumo), cols_per_row):
                row_items = lista_resumo[i : i + cols_per_row]
                cols = st.columns(cols_per_row)
                
                for idx, item in enumerate(row_items):
                    with cols[idx]:
                        cor_fundo = "#166534" if item["Variação (%)"] >= 0 else "#991b1b"
                        seta = "▲" if item["Variação (%)"] >= 0 else "▼"

                        # Card unificado com ticker, preço e valorização
                        st.markdown(f"""
                            <div style="background-color: {cor_fundo}; padding: 18px 12px; border-radius: 12px; color: white; text-align: center; min-height: 125px;">
                                <div style="font-size: 18px; margin-bottom: 2px;"><b>{item['Ativo'].replace('.SA', '')}</b></div>
                                <div style="font-size: 14px; opacity: 0.85;">R$ {item['Preço']:.2f}</div>
                                <div style="font-size: 21px; font-weight: 900; margin-top: 10px;">{seta} {item['Variação (%)']:.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)

                        with st.popover("**⋮**", key=f"menu_{item['Ativo']}"):
                            if st.button("Ver", key=f"view_{item['Ativo']}", use_container_width=True):
                                st.session_state.ticker = item['Ativo']
                                st.session_state.pagina = "Análise"
                                st.rerun()
                            if st.button("Excluir", key=f"del_{item['Ativo']}", use_container_width=True):
                                st.session_state.watchlist[lista_atual].remove(item['Ativo'])
                                salvar_watchlist()
                                st.rerun()
                        st.markdown("<div style='margin-bottom:25px;'></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div style='font-size: 11px; color: #6b7280; margin-bottom: 5px;'>Última atualização dos dados: {st.session_state.last_updated}</div>", unsafe_allow_html=True)
            if st.button(f"Excluir Lista '{lista_atual}'", type="secondary"):
                del st.session_state.watchlist[lista_atual]
                if st.session_state.watchlist:
                    st.session_state.lista_selecionada = list(st.session_state.watchlist.keys())[0]
                salvar_watchlist()
                st.rerun()
        else:
            st.warning("Não foi possível carregar os dados dos ativos no momento.")
    except Exception as e:
        st.error(f"Erro ao carregar favoritos: {e}")

if st.session_state.pagina == "Listas":
    exibir_pagina_favoritos()
    st.stop()

ticker = st.session_state.ticker
periodo = st.session_state.periodo


try:
    historico = buscar_historico(ticker, periodo)

    if historico.empty:
        st.error("Não foi possível encontrar esse ativo.")
    else:
        info = buscar_info(ticker)

        nome_ativo = info.get("longName") or info.get("shortName") or ticker
        preco_atual = historico["Close"].iloc[-1]

        if periodo == "1d":
            preco_inicial = historico["Open"].iloc[0]
            label_variacao = "Variação no dia"
        else:
            preco_inicial = historico["Close"].iloc[0]
            label_variacao = "Variação no período"

        abertura_dia = historico["Open"].iloc[0]
        variacao_periodo = ((preco_atual - preco_inicial) / preco_inicial) * 100

        moeda = info.get("currency", "BRL")

        maxima_periodo = historico["High"].max()
        minima_periodo = historico["Low"].min()
        # datas de ocorrência do mínimo e máximo
        try:
            idx_min = historico["Low"].idxmin()
            idx_max = historico["High"].idxmax()
        except Exception:
            idx_min = None
            idx_max = None

        def _format_date_for_display(ts):
            if ts is None or (isinstance(ts, float) and math.isnan(ts)):
                return "N/A"
            try:
                # se houver componente de tempo intradiário (1d), mostrar hora
                if periodo == "1d" or (hasattr(ts, "hour") and (ts.hour != 0 or ts.minute != 0 or ts.second != 0)):
                    return ts.strftime("%d/%m/%Y %H:%M")
                return ts.strftime("%d/%m/%Y")
            except Exception:
                return str(ts)

        minima_data_str = _format_date_for_display(idx_min)
        maxima_data_str = _format_date_for_display(idx_max)

        dividend_yield_formatado = calcular_dividend_yield_12m(ticker, preco_atual, info)

        with st.container(key="asset_header"):
            logo_col, text_col, fav_col = st.columns([0.1, 1, 0.2], gap="small")

            with logo_col:
                logo_url = info.get("logo_url")
                if logo_url:
                    st.markdown(f'<img src="{logo_url}" class="asset-logo">', unsafe_allow_html=True)
                else:
                    st.markdown(criar_logo_fallback(ticker), unsafe_allow_html=True)

            with text_col:
                st.markdown(
                    f"""
                    <div class="asset-ticker">{ticker.replace(".SA", "")}</div>
                    <div class="asset-name">{nome_ativo.upper()}</div>
                    """,
                    unsafe_allow_html=True
                )
            
            with fav_col:
                # Na página de análise, salva na primeira lista por padrão ou "Favoritos"
                primeira_lista = list(st.session_state.watchlist.keys())[0] if st.session_state.watchlist else "Favoritos"
                if primeira_lista not in st.session_state.watchlist:
                    st.session_state.watchlist[primeira_lista] = []
                    salvar_watchlist()
                
                esta_salvo = ticker in st.session_state.watchlist[primeira_lista]
                label_fav = "⭐ Na Lista" if esta_salvo else "☆ Salvar"
                if st.button(label_fav, use_container_width=True, help=f"Salvar na lista '{primeira_lista}'"):
                    if esta_salvo: 
                        st.session_state.watchlist[primeira_lista].remove(ticker)
                    else: 
                        st.session_state.watchlist[primeira_lista].append(ticker)
                    salvar_watchlist()
                    st.rerun()

        seta = "▲" if variacao_periodo >= 0 else "▼"
        classe_variacao = "positive" if variacao_periodo >= 0 else "negative"
        variacao_formatada = f"{seta} {variacao_periodo:.2f}%"

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            criar_card("Cotação", formatar_moeda(preco_atual, moeda))

        with col2:
            criar_card("Abertura do dia", formatar_moeda(abertura_dia, moeda))

        with col3:
            criar_card(label_variacao, variacao_formatada, classe_variacao)

        with col4:
            criar_card("Dividend Yield 12M", dividend_yield_formatado)

        st.markdown("<br>", unsafe_allow_html=True)

        chart_col, info_col = st.columns([1.4, 1])

        with chart_col:
            with st.container(key="chart_card"):

                with st.container(key="chart_header"):
                    title_col, buttons_col = st.columns([1.4, 1.6], gap="small")

                    with title_col:
                        st.markdown(
                            f'<div class="chart-title">Histórico de preço - {ticker}</div>',
                            unsafe_allow_html=True
                        )

                    with buttons_col:
                        button_cols = st.columns(len(periodos), gap="small")

                        for i, (label, valor) in enumerate(periodos.items()):
                            with button_cols[i]:
                                botao_ativo = st.session_state.periodo == valor

                                if st.button(
                                    label,
                                    use_container_width=True,
                                    disabled=botao_ativo
                                ):
                                    st.session_state.periodo = valor
                                    # sincroniza visual do simulador para acompanhar o gráfico
                                    st.session_state.sim_period = label
                                    st.rerun()

                with st.container(key="chart_body"):
                    fig = go.Figure()

                    moeda_prefixo = "R$" if moeda == "BRL" else "US$"
                    hovertemplate = f"<b>{moeda_prefixo} %{{y:,.2f}}</b><extra></extra>"

                    fig.add_trace(
                        go.Scatter(
                            x=historico.index,
                            y=historico["Close"],
                            mode="lines",
                            name="Preço de fechamento",
                            line=dict(color="#2563eb", width=2),
                            hovertemplate=hovertemplate,
                            hoverlabel=dict(
                                bgcolor="white",
                                bordercolor="#d1d5db",
                                font=dict(family="Arial Black, sans-serif", size=18, color="black")
                            )
                        )
                    )

                    fig.update_layout(
                        xaxis_title="Data",
                        yaxis_title="Preço",
                        hovermode="x unified",
                        height=380,
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        margin=dict(l=20, r=20, t=20, b=20)
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Feature: Exportação de dados
                    csv = historico.to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Baixar dados históricos (CSV)",
                        data=csv,
                        file_name=f'{ticker}_historico.csv',
                        mime='text/csv',
                    )

            st.markdown(
                f"""
    <div class="period-stats-row">
        <div class="period-stat-card">
            <div class="period-stat-label">Mínima do período</div>
            <div class="period-stat-value"><span class="period-stat-amount">{formatar_moeda(minima_periodo, moeda)}</span> <span class="period-stat-date">({minima_data_str})</span></div>
        </div>
        <div class="period-stat-card">
            <div class="period-stat-label">Máxima do período</div>
            <div class="period-stat-value"><span class="period-stat-amount">{formatar_moeda(maxima_periodo, moeda)}</span> <span class="period-stat-date">({maxima_data_str})</span></div>
        </div>
    </div>
                    """,
                unsafe_allow_html=True
            )
            st.markdown(f"<div style='font-size: 10px; color: #6b7280; text-align: right; margin-top: 4px;'>Última atualização: {st.session_state.last_updated}</div>", unsafe_allow_html=True)

        with info_col:
            st.markdown(
                '<div class="fund-title">Indicadores Fundamentalistas</div>',
                unsafe_allow_html=True
            )

            indicadores = [
                ("P/L", formatar_numero(info.get("trailingPE"))),
                ("P/VP", formatar_numero(info.get("priceToBook"))),
                ("Payout", formatar_percentual(info.get("payoutRatio"))),
                ("Margem Líquida", formatar_percentual(info.get("profitMargins"))),
                ("Margem Bruta", formatar_percentual(info.get("grossMargins"))),
                ("Margem EBITDA", formatar_percentual(info.get("ebitdaMargins"))),
                ("P / EBITDA", formatar_numero(info.get("enterpriseToEbitda"))),
                ("ROE", formatar_percentual(info.get("returnOnEquity"))),
                ("ROIC", "N/A"),
                ("Dív. Líq. / Patrim.", formatar_numero(info.get("debtToEquity"))),
                ("Dív. Líq. / EBITDA", "N/A"),
                ("CAGR 5 anos", calcular_cagr_5a(ticker)),
            ]

            st.markdown(
                criar_indicadores_html(indicadores),
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="fund-title" style="margin-top: 20px;">Simulação de investimento</div>',
                unsafe_allow_html=True
            )

            linha_col1, linha_col2, linha_col3, linha_col4, linha_col5 = st.columns([0.15, 0.22, 0.08, 0.22, 0.33], gap="small")
            linha_col1.markdown("Se você tivesse investido")
            valor_investido = linha_col2.number_input(
                "",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
            linha_col3.markdown("há")
            investimento_periodo = linha_col4.selectbox(
                "",
                options=["1D", "5D", "1M", "6M", "YTD", "1A", "5A", "10A", "15A"],
                key="sim_period",
                label_visibility="collapsed"
            )
            linha_col5.markdown("hoje você teria")

            periodo_investimento = {
                "1D": "1d",
                "5D": "5d",
                "1M": "1mo",
                "6M": "6mo",
                "YTD": "ytd",
                "1A": "1y",
                "5A": "5y",
                "10A": "10y",
                "15A": "15y"
            }.get(investimento_periodo, "1y")

            valor_final = calcular_valor_investido(ticker, periodo_investimento, valor_investido)
            cor_resultado = "green" if valor_final is not None and valor_final >= valor_investido else "red"
            texto_resultado = "N/A"

            if valor_final is not None:
                texto_resultado = formatar_moeda(valor_final, moeda)

            valor_investido_formatado = formatar_moeda(valor_investido, moeda)

            st.markdown(
                f"<div style='margin-top: 8px; font-size: 23px;'>"
                f"Se você tivesse investido <strong>{valor_investido_formatado}</strong> há <strong>{obter_label_periodo(periodo_investimento)}</strong>,<br>hoje você teria "
                f"<span style='color: {cor_resultado}; font-weight: 800; font-size: 28px;'>{texto_resultado}</span>."
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            """
<div class="ai-card">
    <div class="ai-header">Análise com IA</div>
""",
            unsafe_allow_html=True
        )

        if st.button("🚀 Gerar análise com IA agora", use_container_width=True):
            if not os.getenv("OPENAI_API_KEY"):
                st.error("Chave da OpenAI não encontrada. Verifique se o arquivo .env está correto.")
            else:
                with st.spinner("Gerando análise com IA..."):
                    try:
                        st.session_state.analise_ia = gerar_analise_openai(
                            ticker=ticker,
                            nome_ativo=nome_ativo,
                            preco_atual=preco_atual,
                            moeda=moeda,
                            variacao_periodo=variacao_periodo,
                            dividend_yield=dividend_yield_formatado,
                            maxima_periodo=maxima_periodo,
                            minima_periodo=minima_periodo,
                            periodo=periodo,
                            info=info
                        )

                    except Exception as erro:
                        st.error(f"Erro ao gerar análise com IA: {erro}")

        if st.session_state.analise_ia:
            st.markdown(
                criar_analise_openai_html(st.session_state.analise_ia),
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
<div class="ai-text">
Clique no botão acima para gerar uma análise fundamentalista automática com IA.
</div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
</div>
""",
            unsafe_allow_html=True
        )

except Exception as erro:
    st.error("Ocorreu um erro ao buscar o ativo.")
    st.write(erro)
