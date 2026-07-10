# config.py — configurações do app

# Usuários permitidos: { "usuario": "senha" }
# Troque por hashes bcrypt em produção
USUARIOS = {
    "matheus": "senha123",
    "ana": "senha456",
    "carlos": "senha789",
}

# Marcas disponíveis para venda
MARCAS = [
    "Cargill",
    "Diageo",
    "Energizer",
    "Hypera",
    "Haleon",
    "Melitta",
    "Nivea",
    "Moet Chandon",
    "Reckitt Core",
    "BIC",
    "Vestacy",
    "Kimberly",
    "VCT",
]

# Motivos de não venda
MOTIVOS_NAO_VENDA = [
    "Comprador ausente",
    "Pediu retorno",
    "Avaliando proposta",
    "Recusou preço",
    "Sem interesse",
    "Estabelecimento fechado",
    "Outro",
]

# Nome da aba na planilha Google Sheets
SHEET_NAME = "Visitas"

# ID da pasta no Google Drive onde as fotos serão salvas
# Crie uma pasta no Drive, compartilhe com a service account e cole o ID aqui
# O ID está na URL: drive.google.com/drive/folders/ESTE_TRECHO_AQUI
DRIVE_PASTA_FOTOS_ID = ""  # preencher no secrets.toml (ver README)

# Colunas da planilha (ordem exata)
COLUNAS = [
    "timestamp_envio",
    "data_visita",
    "vendedor",
    "km_dia",
    "ordem_cliente",
    "cnpj",
    "codigo_cliente",
    "vendeu",
    "motivo_nao_venda",
    "marcas_vendidas",
    "comentario",
    "foto_cliente",
]
