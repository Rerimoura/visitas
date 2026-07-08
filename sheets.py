# sheets.py — leitura e escrita no Google Sheets via gspread

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from config import SHEET_NAME, COLUNAS
import pandas as pd
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def get_client():
    """Retorna cliente gspread autenticado via service account."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_sheet():
    client = get_client()
    # Abre a planilha pelo ID ou nome configurado nos secrets
    spreadsheet = client.open_by_key(st.secrets["google_sheets"]["spreadsheet_id"])
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        # Cria a aba se não existir e adiciona cabeçalho
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=20)
        sheet.append_row(COLUNAS)
    return sheet


def garantir_cabecalho(sheet):
    """Garante que o cabeçalho existe na primeira linha."""
    primeira = sheet.row_values(1)
    if primeira != COLUNAS:
        sheet.insert_row(COLUNAS, index=1)


def gravar_visitas(linhas: list[dict]) -> bool:
    """
    Recebe lista de dicts com os dados de cada cliente e grava no Sheets.
    Retorna True se sucesso, False se erro.
    """
    try:
        sheet = get_sheet()
        garantir_cabecalho(sheet)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows_to_append = []
        for linha in linhas:
            linha["timestamp_envio"] = timestamp
            row = [str(linha.get(col, "")) for col in COLUNAS]
            rows_to_append.append(row)
        sheet.append_rows(rows_to_append, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        st.error(f"Erro ao gravar no Google Sheets: {e}")
        return False


def carregar_visitas() -> pd.DataFrame:
    """Carrega todas as visitas como DataFrame (para tela de histórico)."""
    try:
        sheet = get_sheet()
        dados = sheet.get_all_records()
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()
