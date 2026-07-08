# app.py — Relatório de Visitas (Streamlit)

import streamlit as st
from datetime import date
from auth import requer_login, logout
from sheets import gravar_visitas
from config import MARCAS, MOTIVOS_NAO_VENDA, BASE_URL_FOTOS

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Relatório de Visitas",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo e tipografia */
    [data-testid="stAppViewContainer"] { background: #0f1117; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Card de cliente */
    .cliente-card {
        background: #1a1d27;
        border: 1px solid #2a2d3d;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .cliente-header {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #5b6fff;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* Botão primário */
    .stButton > button[kind="primary"] {
        background: #5b6fff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: background 0.2s;
    }
    .stButton > button[kind="primary"]:hover { background: #4455ee; }

    /* Botão de adicionar cliente */
    .stButton > button[kind="secondary"] {
        border: 1px dashed #2a2d3d;
        background: transparent;
        color: #888;
        border-radius: 8px;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #5b6fff;
        color: #5b6fff;
    }

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div {
        background: #12141e !important;
        border-color: #2a2d3d !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
    }

    /* Ocultar menu e rodapé padrão */
    #MainMenu, footer { visibility: hidden; }

    /* Badge de status */
    .badge-sim { color: #4ade80; font-weight: 600; font-size:0.85rem; }
    .badge-nao { color: #f87171; font-weight: 600; font-size:0.85rem; }

    /* Resumo */
    .resumo-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2a2d3d;
        font-size: 0.88rem;
        color: #c0c0c0;
    }
    .resumo-row:last-child { border-bottom: none; }
</style>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ── Autenticação ─────────────────────────────────────────────────────────────
requer_login()

vendedor = st.session_state["vendedor"]

# ── Inicializar estado dos clientes ──────────────────────────────────────────
if "clientes" not in st.session_state:
    st.session_state.clientes = [{}]  # começa com 1 cliente em branco

if "enviado" not in st.session_state:
    st.session_state.enviado = False

# ── Header ───────────────────────────────────────────────────────────────────
col_title, col_user = st.columns([3, 1])
with col_title:
    st.markdown("## 📋 Relatório de Visitas")
with col_user:
    st.markdown(f"<p style='text-align:right;color:#888;font-size:0.85rem;padding-top:0.6rem;'>👤 {vendedor}</p>", unsafe_allow_html=True)
    if st.button("Sair", use_container_width=True):
        logout()

st.divider()

# ── Tela de sucesso ──────────────────────────────────────────────────────────
if st.session_state.enviado:
    st.success("✅ Relatório enviado com sucesso!")
    st.markdown(f"""
    <div style="background:#1a1d27;border-radius:12px;padding:1.5rem;text-align:center;margin-top:1rem;">
        <div style="font-size:3rem;">🎉</div>
        <h3 style="color:#e0e0e0;margin:0.5rem 0;">Tudo certo, {vendedor.capitalize()}!</h3>
        <p style="color:#888;">Suas visitas foram gravadas na planilha.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Novo relatório", type="primary", use_container_width=True):
        st.session_state.clientes = [{}]
        st.session_state.enviado = False
        st.rerun()
    st.stop()

# ── Dados do dia ─────────────────────────────────────────────────────────────
with st.container():
    st.markdown("#### 📅 Dados do dia")
    col1, col2 = st.columns(2)
    with col1:
        data_visita = st.date_input("Data da visita", value=date.today())
    with col2:
        km_dia = st.number_input("KMs percorridos", min_value=0, step=1, value=0)

st.divider()

# ── Bloco por cliente ─────────────────────────────────────────────────────────
st.markdown("#### 🏪 Clientes visitados")

clientes_data = []

for i, _ in enumerate(st.session_state.clientes):
    idx = i + 1
    with st.container():
        st.markdown(f'<div class="cliente-header">Cliente {idx}</div>', unsafe_allow_html=True)

        col_id1, col_id2 = st.columns(2)
        with col_id1:
            cnpj = st.text_input(
                "CNPJ",
                placeholder="00.000.000/0000-00",
                key=f"cnpj_{i}",
            )
        with col_id2:
            codigo = st.text_input(
                "Código Interno",
                placeholder="Até 7 dígitos (números)",
                max_chars=7,
                key=f"codigo_{i}",
            )

        vendeu = st.radio(
            "Vendeu?",
            options=["SIM", "NÃO"],
            index=1,
            horizontal=True,
            key=f"vendeu_{i}",
        )

        motivo = ""
        marcas = []

        if vendeu == "NÃO":
            motivo = st.selectbox(
                "Motivo da não venda",
                options=[""] + MOTIVOS_NAO_VENDA,
                key=f"motivo_{i}",
            )
        else:
            marcas = st.multiselect(
                "Marcas vendidas",
                options=MARCAS,
                key=f"marcas_{i}",
            )

        comentario = st.text_area(
            "Comentário (opcional)",
            placeholder="Observações sobre o cliente...",
            key=f"comentario_{i}",
            height=80,
        )

        foto = st.file_uploader(
            "Foto do cliente (opcional)",
            type=["jpg", "jpeg", "png"],
            key=f"foto_{i}",
        )

        clientes_data.append({
            "data_visita": str(data_visita),
            "vendedor": vendedor,
            "km_dia": km_dia,
            "ordem_cliente": idx,
            "cnpj": cnpj,
            "codigo_cliente": codigo,
            "vendeu": vendeu,
            "motivo_nao_venda": motivo,
            "marcas_vendidas": ", ".join(marcas),
            "comentario": comentario,
            "foto_objeto": foto,
        })

        st.markdown("---")

# ── Botão adicionar cliente ───────────────────────────────────────────────────
col_add, col_remove = st.columns([3, 1])
with col_add:
    if len(st.session_state.clientes) < 10:
        if st.button("＋ Adicionar cliente", use_container_width=True):
            st.session_state.clientes.append({})
            st.rerun()
with col_remove:
    if len(st.session_state.clientes) > 1:
        if st.button("Remover último", use_container_width=True):
            st.session_state.clientes.pop()
            st.rerun()

st.divider()

# ── Resumo antes do envio ─────────────────────────────────────────────────────
with st.expander("📊 Ver resumo antes de enviar", expanded=False):
    total = len(clientes_data)
    ativos = [c for c in clientes_data if (c["cnpj"].strip() or c["codigo_cliente"].strip())]
    total_ativos = len(ativos) if ativos else total
    
    vendidos = sum(1 for c in clientes_data if (c["cnpj"].strip() or c["codigo_cliente"].strip()) and c["vendeu"] == "SIM")
    nao_vendidos = total_ativos - vendidos

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Clientes visitados", total_ativos)
    col_r2.metric("✅ Vendas", vendidos)
    col_r3.metric("❌ Não vendas", nao_vendidos)

    st.markdown("")
    for c in clientes_data:
        cnpj_val = c["cnpj"].strip()
        cod_val = c["codigo_cliente"].strip()
        
        if not (cnpj_val or cod_val):
            continue
            
        if cnpj_val and cod_val:
            cnpj_label = f"{cnpj_val} ({cod_val})"
        elif cnpj_val:
            cnpj_label = cnpj_val
        else:
            cnpj_label = f"Cód: {cod_val}"
            
        status = "✅ SIM" if c["vendeu"] == "SIM" else "❌ NÃO"
        detalhe = ", ".join(c["marcas_vendidas"].split(", ")) if c["vendeu"] == "SIM" else c["motivo_nao_venda"]
        st.markdown(
            f'<div class="resumo-row"><span>{cnpj_label}</span><span>{status}</span><span style="color:#888">{detalhe}</span></div>',
            unsafe_allow_html=True,
        )

# ── Envio ─────────────────────────────────────────────────────────────────────
st.markdown("")

# Validações básicas
erros = []

clientes_preenchidos = [c for c in clientes_data if (c["cnpj"].strip() or c["codigo_cliente"].strip())]
if not clientes_preenchidos:
    erros.append("Preencha o CNPJ ou o Código Interno de pelo menos um cliente.")

for c in clientes_data:
    is_preenchido = bool(c["cnpj"].strip() or c["codigo_cliente"].strip())
    if is_preenchido:
        cod = c["codigo_cliente"].strip()
        if cod and not cod.isdigit():
            erros.append(f"O código do cliente {c['ordem_cliente']} deve conter apenas números (até 7 dígitos).")
            
        if c["vendeu"] == "NÃO" and not c["motivo_nao_venda"]:
            erros.append(f"Selecione o motivo de não venda do cliente {c['ordem_cliente']}.")

if erros:
    for erro in erros:
        st.warning(erro)

enviar = st.button(
    "📤 Enviar relatório",
    type="primary",
    use_container_width=True,
    disabled=bool(erros),
)

if enviar:
    linhas = [c.copy() for c in clientes_data if (c["cnpj"].strip() or c["codigo_cliente"].strip())]
    
    import os
    from datetime import datetime
    
    os.makedirs("static", exist_ok=True)
    
    for c in linhas:
        foto_obj = c.pop("foto_objeto", None)
        if foto_obj is not None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(foto_obj.name)[1]
            if not ext:
                ext = ".jpg"
            safe_filename = f"{ts}_{c['vendedor']}_cliente_{c['ordem_cliente']}{ext}"
            safe_filename = "".join(ch for ch in safe_filename if ch.isalnum() or ch in "._-")
            filepath = os.path.join("static", safe_filename)
            
            with open(filepath, "wb") as f:
                f.write(foto_obj.getbuffer())
                
            c["foto_cliente"] = f'=HYPERLINK("{BASE_URL_FOTOS}{safe_filename}"; "Ver Foto")'
        else:
            c["foto_cliente"] = ""
            
    with st.spinner("Gravando no Google Sheets..."):
        sucesso = gravar_visitas(linhas)
    if sucesso:
        st.session_state.enviado = True
        st.rerun()
