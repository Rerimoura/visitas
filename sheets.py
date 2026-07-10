# sheets.py — leitura e escrita no Google Sheets via gspread

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from config import SHEET_NAME, COLUNAS
import pandas as pd
import io
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


def get_drive_service():
    """Retorna cliente autenticado da Google Drive API."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=creds)


def upload_foto_drive(foto_bytes: bytes, filename: str, mimetype: str = "image/jpeg") -> str:
    """
    Faz upload de uma foto para a pasta do Google Drive configurada nos secrets.
    Retorna o link público de visualização, ou string vazia se falhar.
    """
    try:
        pasta_id = st.secrets["google_drive"]["pasta_fotos_id"]
        service = get_drive_service()

        file_metadata = {
            "name": filename,
            "parents": [pasta_id],
        }
        media = MediaIoBaseUpload(
            io.BytesIO(foto_bytes),
            mimetype=mimetype,
            resumable=False,
        )
        arquivo = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
        ).execute()

        file_id = arquivo.get("id")

        # Tornar o arquivo público (leitura para qualquer pessoa com o link)
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        return f"https://drive.google.com/file/d/{file_id}/view"

    except Exception as e:
        st.warning(f"Foto não pôde ser enviada: {e}")
        return ""


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
