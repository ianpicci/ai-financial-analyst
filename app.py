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
    padding: 12px 16px 18px 16px;
    margin-bottom: 24px;
}

.st-key-asset_header [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 4px;
}

.logo-fallback {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    background-color: #1f2937;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    font-weight: 800;
    margin: 0 !important;
    flex-shrink: 0;
}

.asset-ticker {
    font-size: 26px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 4px;
}

.asset-name {
    font-size: 15px;
    font-weight: 500;
    color: #4b5563;
    margin-bottom: 4px;
}

.asset-name {
    font-size: 15px;
    font-weight: 500;
    color: #4b5563;
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


@st.cache_data
def buscar_info(ticker):
    ativo = yf.Ticker(ticker)
    return ativo.info


@st.cache_data
def buscar_historico(ticker, periodo):
    ativo = yf.Ticker(ticker)

    if periodo == "1d":
        return ativo.history(period="1d", interval="5m")

    return ativo.history(period=periodo)


def calcular_dividend_yield_12m(ativo, preco_atual):
    dividendos = ativo.dividends

    if dividendos.empty or preco_atual == 0:
        return "N/A"

    data_limite = pd.Timestamp.now(tz=dividendos.index.tz) - pd.DateOffset(months=12)
    dividendos_12m = dividendos[dividendos.index >= data_limite]

    total_dividendos_12m = dividendos_12m.sum()
    dividend_yield = total_dividendos_12m / preco_atual

    return f"{dividend_yield * 100:.2f}%"


def calcular_cagr_5a(ativo):
    historico_5a = buscar_historico(ativo.ticker, "5y")

    if historico_5a.empty:
        return "N/A"

    preco_inicial = historico_5a["Close"].iloc[0]
    preco_final = historico_5a["Close"].iloc[-1]

    if preco_inicial == 0:
        return "N/A"

    cagr = (preco_final / preco_inicial) ** (1 / 5) - 1

    return f"{cagr * 100:.2f}%"


def calcular_valor_investido(ativo, periodo, valor_investido):
    historico_periodo = buscar_historico(ativo.ticker, periodo)

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

    resposta = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    return json.loads(resposta.output_text)


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

if "periodo" not in st.session_state:
    st.session_state.periodo = "1d"

if "ticker" not in st.session_state:
    st.session_state.ticker = "PETR4.SA"

if "analise_ia" not in st.session_state:
    st.session_state.analise_ia = ""

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
    top_col1, top_col2, spacer = st.columns([1, 2, 2], gap="small")

    with top_col1:
        st.markdown(
            '<div class="top-title">AI Financial Analyst</div>',
            unsafe_allow_html=True
        )

    with top_col2:
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

    with spacer:
        st.empty()


if analisar and ticker_digitado.strip() != "":
    st.session_state.ticker = normalizar_ticker(ticker_digitado)
    st.session_state.periodo = "1d"
    st.session_state.analise_ia = ""
    # ao pesquisar novo ativo, resetar visual do simulador para 1d (mesmo padrão do gráfico)
    sim_label = None
    for k, v in periodos.items():
        if v == st.session_state.periodo:
            sim_label = k
            break
    st.session_state.sim_period = sim_label or "1D"


ticker = st.session_state.ticker
periodo = st.session_state.periodo


try:
    ativo = yf.Ticker(ticker)
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

        moeda = ativo.fast_info.get("currency", "BRL")

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

        dividend_yield_formatado = calcular_dividend_yield_12m(ativo, preco_atual)

        with st.container(key="asset_header"):
            logo_col, text_col = st.columns([0.06, 1], gap="small")

            with logo_col:
                st.markdown(criar_logo_fallback(ticker), unsafe_allow_html=True)

            with text_col:
                st.markdown(
                    f"""
                    <div class="asset-ticker">{ticker.replace(".SA", "")}</div>
                    <div class="asset-name">{nome_ativo.upper()}</div>
                    """,
                    unsafe_allow_html=True
                )

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
                ("CAGR 5 anos", calcular_cagr_5a(ativo)),
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

            valor_final = calcular_valor_investido(ativo, periodo_investimento, valor_investido)
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