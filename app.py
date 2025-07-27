import streamlit as st
import sys
import os
from datetime import datetime

# Adiciona o diretório atual ao path para importar nosso módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agente_vacivida_azure import VaciVidaAI
except ImportError:
    try:
        from agente_vacivida_cloud import VaciVidaAI
    except ImportError:
        try:
            from agente_vacivida import VaciVidaAI
        except ImportError as e:
            st.error(f"Erro ao importar o agente VaciVida: {e}")
            st.stop()

# Configuração da página
st.set_page_config(
    page_title="VaciVida AI - Consultas Inteligentes",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .query-result {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .sql-code {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        border-left: 4px solid #007bff;
    }
    .error-message {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

def inicializar_agente():
    """Inicializa o agente VaciVida AI"""
    if 'agente' not in st.session_state:
        with st.spinner('Inicializando VaciVida AI...'):
            try:
                st.session_state.agente = VaciVidaAI()
                st.session_state.agente_inicializado = True
                return True
            except Exception as e:
                st.error(f"Erro ao inicializar o agente: {e}")
                return False
    return True

def main():
    # Header principal
    st.markdown('<h1 class="main-header">💉 VaciVida AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Consultas Inteligentes em Dados de Vacinação</p>', unsafe_allow_html=True)
    
    # Inicializar agente
    if not inicializar_agente():
        st.stop()
    
    # Sidebar com informações e exemplos
    with st.sidebar:
        st.header("📊 Sobre o Sistema")
        
        # Mostrar status do banco de dados
        if 'agente' in st.session_state:
            status_info = st.session_state.agente.get_status_info()
            st.info(f"**Status do DB:** {status_info}")
        
        st.write("""
        O VaciVida AI permite fazer consultas em linguagem natural sobre:
        
        - 📈 **Doses aplicadas**
        - ⚠️ **Eventos adversos** registrados
        - 🏭 **Laboratórios** e fabricantes
        - 👥 **Demografia** dos pacientes
        """)
        
        st.header("💡 Exemplos de Perguntas")
        exemplos = st.session_state.agente.get_exemplos_perguntas()
        
        for i, exemplo in enumerate(exemplos[:5]):  # Mostra apenas os primeiros 5
            if st.button(exemplo, key=f"exemplo_{i}"):
                st.session_state.pergunta_selecionada = exemplo
        
        with st.expander("Ver mais exemplos"):
            for i, exemplo in enumerate(exemplos[5:], start=5):
                if st.button(exemplo, key=f"exemplo_extra_{i}"):
                    st.session_state.pergunta_selecionada = exemplo
        
        st.header("🔧 Informações Técnicas")
        if st.button("Ver Schema do Banco"):
            schema_info = st.session_state.agente.get_schema_info()
            st.text_area("Schema", schema_info, height=200)
    
    # Área principal de consulta
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Campo de entrada
        pergunta_default = st.session_state.get('pergunta_selecionada', '')
        pergunta = st.text_input(
            "🤔 Faça sua pergunta sobre os dados de vacinação:",
            value=pergunta_default,
            placeholder="Ex: Quantas doses foram aplicadas por laboratório?",
            key="input_pergunta"
        )
        
        # Limpa a pergunta selecionada após usar
        if 'pergunta_selecionada' in st.session_state:
            del st.session_state.pergunta_selecionada
    
    with col2:
        consultar = st.button("🔍 Consultar", type="primary", use_container_width=True)
    
    # Processar consulta
    if consultar and pergunta:
        with st.spinner('Processando sua consulta...'):
            resultado = st.session_state.agente.consultar(pergunta)
            
            if resultado["sucesso"]:
                # Mostrar resultado
                st.markdown('<div class="query-result">', unsafe_allow_html=True)
                st.success("✅ Consulta executada com sucesso!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("🤖 Resposta")
                    st.write(resultado["resposta"])
                
                with col2:
                    st.subheader("📊 Detalhes")
                    st.write(f"**Pergunta:** {resultado['pergunta']}")
                    st.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
                # Mostrar SQL gerada
                if resultado["sql_gerada"] != "Não disponível":
                    st.subheader("🔧 SQL Gerada")
                    st.markdown(f'<div class="sql-code">{resultado["sql_gerada"]}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                # Mostrar erro
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.error(f"❌ Erro ao processar consulta: {resultado['erro']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif consultar and not pergunta:
        st.warning("⚠️ Por favor, digite uma pergunta antes de consultar.")
    
    # Histórico de consultas (opcional)
    if 'historico' not in st.session_state:
        st.session_state.historico = []
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🏥 VaciVida AI - Sistema Inteligente de Consultas em Dados de Vacinação</p>
        <p>Desenvolvido com ❤️ usando Streamlit e LangChain</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
