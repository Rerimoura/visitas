# 📋 App de Relatório de Visitas

App Streamlit para registro de visitas de vendedores, com gravação automática no Google Sheets.

---

## Stack

- **Frontend**: Streamlit
- **Backend de dados**: Google Sheets via gspread
- **Autenticação**: Login simples por usuário/senha (configurável em `config.py`)
- **Deploy**: Streamlit Community Cloud (gratuito)

---

## Setup local

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Google Sheets

#### 2a. Criar Service Account no Google Cloud
1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto (ou use um existente)
3. Ative as APIs: **Google Sheets API** e **Google Drive API**
4. Vá em "IAM e Admin" → "Service Accounts" → "Criar conta de serviço"
5. Baixe o arquivo JSON de credenciais

#### 2b. Criar a planilha
1. Crie uma planilha no Google Sheets
2. Compartilhe com o e-mail da service account (com permissão de Editor)
3. Copie o ID da planilha da URL:  
   `https://docs.google.com/spreadsheets/d/**ID_AQUI**/edit`

#### 2c. Configurar secrets
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Preencha `secrets.toml` com as credenciais do JSON baixado e o ID da planilha.

### 3. Rodar localmente

```bash
streamlit run app.py
```

---

## Configuração de usuários

Edite `config.py` → dicionário `USUARIOS`:

```python
USUARIOS = {
    "matheus": "senha123",
    "ana": "senha456",
}
```

> Em produção, substitua por hashes bcrypt + banco de dados.

---

## Deploy no Streamlit Community Cloud

1. Suba o código para um repositório GitHub (sem o `secrets.toml`)
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. "New app" → conecte o repositório → arquivo principal: `app.py`
4. Em "Advanced settings" → "Secrets": cole o conteúdo do `secrets.toml`
5. Deploy ✅

---

## Estrutura de arquivos

```
app_visitas/
├── app.py              # App principal
├── auth.py             # Módulo de autenticação
├── sheets.py           # Integração Google Sheets
├── config.py           # Usuários, marcas, motivos
├── requirements.txt
└── .streamlit/
    └── secrets.toml    # Credenciais (não commitar)
```

---

## Próximos passos (v2)

- [ ] Login via Microsoft OAuth (conta corporativa)
- [ ] Migração para SharePoint via Graph API
- [ ] Tela de histórico de visitas por vendedor
- [ ] Dashboard de conversão integrado
