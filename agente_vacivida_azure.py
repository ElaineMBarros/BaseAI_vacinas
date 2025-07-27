import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from azure_blob_manager import get_database_path

def criar_banco_demo():
    """Cria um banco de dados de demonstração com dados fictícios"""
    conn = sqlite3.connect('demo_vacivida.db')
    cursor = conn.cursor()
    
    # Criar tabela de doses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vcvd_dose (
        Id INTEGER PRIMARY KEY,
        vcvd_laboratorio TEXT,
        vcvd_doseid TEXT,
        vcvd_sexo INTEGER,
        vcvd_idade INTEGER,
        vcvd_data_aplicacao DATE
    )
    ''')
    
    # Criar tabela de eventos adversos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vcvd_evento_adverso (
        Id INTEGER PRIMARY KEY,
        VCVD_SEXO INTEGER,
        VCVD_GRAVE_ENCERRAMENTO_EAG INTEGER,
        vcvd_tipo_evento TEXT,
        vcvd_data_evento DATE
    )
    ''')
    
    # Inserir dados de demonstração para doses
    dados_doses = [
        (1, 'PFIZER/BIONTECH', 'DOSE001', 1, 35, '2021-01-15'),
        (2, 'ASTRAZENECA/OXFORD', 'DOSE002', 2, 42, '2021-01-16'),
        (3, 'SINOVAC/BUTANTAN', 'DOSE003', 1, 28, '2021-01-17'),
        (4, 'JOHNSON & JOHNSON/JANSSEN', 'DOSE004', 2, 55, '2021-01-18'),
        (5, 'PFIZER/BIONTECH', 'DOSE005', 1, 33, '2021-01-19'),
        (6, 'ASTRAZENECA/OXFORD', 'DOSE006', 2, 48, '2021-01-20'),
        (7, 'SINOVAC', 'DOSE007', 1, 25, '2021-01-21'),
        (8, 'PFIZER/BIONTECH', 'DOSE008', 2, 62, '2021-01-22'),
        (9, 'ASTRAZENECA/OXFORD', 'DOSE009', 1, 31, '2021-01-23'),
        (10, 'SINOVAC/BUTANTAN', 'DOSE010', 2, 44, '2021-01-24')
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO vcvd_dose 
    (Id, vcvd_laboratorio, vcvd_doseid, vcvd_sexo, vcvd_idade, vcvd_data_aplicacao)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', dados_doses)
    
    # Inserir dados de demonstração para eventos adversos
    dados_eventos = [
        (1, 1, 0, 'Dor no local', '2021-01-16'),
        (2, 2, 0, 'Febre baixa', '2021-01-17'),
        (3, 1, 1, 'Reação alérgica', '2021-01-18'),
        (4, 2, 0, 'Dor de cabeça', '2021-01-19'),
        (5, 1, 0, 'Fadiga', '2021-01-20')
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO vcvd_evento_adverso 
    (Id, VCVD_SEXO, VCVD_GRAVE_ENCERRAMENTO_EAG, vcvd_tipo_evento, vcvd_data_evento)
    VALUES (?, ?, ?, ?, ?)
    ''', dados_eventos)
    
    conn.commit()
    conn.close()
    return 'demo_vacivida.db'

class VaciVidaAI:
    """
    Agente AI para consultas no banco de dados VaciVida com suporte ao Azure
    """
    
    def __init__(self, forcar_demo=False):
        # Carrega as variáveis de ambiente PRIMEIRO
        load_dotenv()
        
        # Verifica se a chave da OpenAI está definida (local ou Streamlit Cloud)
        api_key = None
        
        # Primeiro tenta pegar do .env (para local)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Se não encontrar no .env, tenta Streamlit secrets (para cloud)
        if not api_key:
            try:
                if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                    api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass  # Ignora erro se não conseguir acessar secrets
        
        if not api_key:
            raise ValueError("A variável de ambiente OPENAI_API_KEY não está definida.")
        
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Configuração do banco de dados
        self.modo_usado = "demo"
        
        if forcar_demo:
            db_path = criar_banco_demo()
            self.modo_usado = "demo"
            if hasattr(st, 'info'):
                st.info("🔄 Usando banco de dados de demonstração (modo forçado)")
        else:
            # Tenta obter o banco do Azure ou local
            db_path = get_database_path()
            
            if db_path and os.path.exists(db_path):
                if "temp" in db_path:
                    self.modo_usado = "azure"
                    if hasattr(st, 'success'):
                        st.success("☁️ Usando banco de dados do Azure Blob Storage")
                else:
                    self.modo_usado = "local"
                    if hasattr(st, 'info'):
                        st.info("💾 Usando banco de dados local")
            else:
                # Fallback para demo
                db_path = criar_banco_demo()
                self.modo_usado = "demo"
                if hasattr(st, 'warning'):
                    st.warning("🔄 Usando banco de dados de demonstração (Azure não configurado)")
            
        # Configuração do banco de dados com informações mais limitadas
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.db = SQLDatabase(
            self.engine, 
            sample_rows_in_table_info=2,  # Reduzido para menos contexto
            max_string_length=200,        # Reduzido para consultas mais simples
            include_tables=["vcvd_dose", "vcvd_evento_adverso"],
            custom_table_info={
                "vcvd_dose": "Tabela com doses de vacinas. Principais colunas: vcvd_laboratorio (texto), vcvd_doseid (ID), vcvd_sexo (1=M, 2=F), vcvd_idade (número)",
                "vcvd_evento_adverso": "Tabela com eventos adversos. Principais colunas: VCVD_SEXO (1=M, 2=F), VCVD_GRAVE_ENCERRAMENTO_EAG (0=não grave, 1=grave)"
            }
        )
        
        # Configuração do modelo OpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k", 
            temperature=0,
            max_tokens=500  # Reduzido para evitar SQLs muito complexas
        )
        
        # Criação do chain SQL com configurações mais restritivas
        self.db_chain = SQLDatabaseChain.from_llm(
            llm=self.llm, 
            db=self.db, 
            verbose=False,
            return_intermediate_steps=True
        )
    
    def get_status_info(self):
        """Retorna informações sobre o status do banco de dados"""
        if self.modo_usado == "azure":
            return "☁️ Conectado ao Azure Blob Storage"
        elif self.modo_usado == "local":
            return "💾 Usando banco local"
        else:
            return "🔄 Modo demonstração (dados fictícios)"
    
    def _validar_sql(self, sql: str) -> str:
        """
        Valida e corrige a SQL gerada para usar apenas tabelas válidas
        """
        if not sql:
            return sql
        
        # Substitui nomes incorretos de tabelas
        sql_corrigida = sql
        
        # Padrões comuns de nomes incorretos que o LLM pode gerar
        padroes_incorretos = [
            (r'"?Tabela com doses de vacinas"?', "vcvd_dose"),
            (r'"?tabela_doses"?', "vcvd_dose"),
            (r'"?doses"?', "vcvd_dose"),
            (r'"?vacinas"?', "vcvd_dose"),
            (r'"?Tabela com eventos adversos"?', "vcvd_evento_adverso"),
            (r'"?eventos_adversos"?', "vcvd_evento_adverso"),
            (r'"?eventos"?', "vcvd_evento_adverso"),
        ]
        
        import re
        for padrao, tabela_correta in padroes_incorretos:
            sql_corrigida = re.sub(padrao, tabela_correta, sql_corrigida, flags=re.IGNORECASE)
        
        return sql_corrigida

    def consultar(self, pergunta: str) -> dict:
        """
        Realiza uma consulta no banco de dados
        
        Args:
            pergunta (str): Pergunta em linguagem natural
            
        Returns:
            dict: Resultado da consulta com SQL gerada e resposta
        """
        try:
            # Melhorar o prompt para ser mais específico sobre as tabelas
            pergunta_melhorada = f"""
            Use APENAS as tabelas 'vcvd_dose' e 'vcvd_evento_adverso' que existem no banco.
            NUNCA invente nomes de tabelas.
            
            Pergunta: {pergunta}
            
            Tabelas disponíveis:
            - vcvd_dose: contém informações sobre doses de vacinas aplicadas
            - vcvd_evento_adverso: contém informações sobre eventos adversos registrados
            """
            
            resultado = self.db_chain.invoke({"query": pergunta_melhorada})
            
            # Extrair informações do resultado
            resposta = resultado.get("result", "Não foi possível obter resposta")
            
            # Tentar extrair o SQL das etapas intermediárias
            sql_query = "Não disponível"
            if "intermediate_steps" in resultado:
                for step in resultado["intermediate_steps"]:
                    if isinstance(step, dict) and "sql_cmd" in step:
                        sql_query = step["sql_cmd"]
                        # Limpar e validar a SQL de problemas comuns
                        sql_query = self._limpar_sql(sql_query)
                        sql_query = self._validar_sql(sql_query)
                        break
            
            return {
                "sucesso": True,
                "pergunta": pergunta,
                "sql_gerada": sql_query,
                "resposta": resposta,
                "erro": None,
                "modo": self.modo_usado
            }
            
        except Exception as e:
            erro_str = str(e)
            
            # Se o erro for relacionado a múltiplas instruções, tenta novamente com fallback
            if "multiple statements" in erro_str.lower() or "You can only execute one statement at a time" in erro_str:
                try:
                    # Tenta uma abordagem mais simples
                    pergunta_simplificada = f"Responda de forma direta e concisa: {pergunta}. Use apenas uma instrução SQL simples."
                    resultado_fallback = self.db_chain.invoke({"query": pergunta_simplificada})
                    
                    resposta = resultado_fallback.get("result", "Não foi possível obter resposta")
                    sql_query = "Não disponível"
                    
                    if "intermediate_steps" in resultado_fallback:
                        for step in resultado_fallback["intermediate_steps"]:
                            if isinstance(step, dict) and "sql_cmd" in step:
                                sql_query = self._limpar_sql(step["sql_cmd"])
                                break
                    
                    return {
                        "sucesso": True,
                        "pergunta": pergunta,
                        "sql_gerada": sql_query,
                        "resposta": resposta,
                        "erro": f"Resolvido automaticamente (erro original: múltiplas instruções SQL)",
                        "modo": self.modo_usado
                    }
                    
                except Exception as e2:
                    return {
                        "sucesso": False,
                        "pergunta": pergunta,
                        "sql_gerada": None,
                        "resposta": None,
                        "erro": f"Erro original: {erro_str}. Erro no fallback: {str(e2)}",
                        "modo": self.modo_usado
                    }
            
            # Se for erro de SQL, tentar uma versão mais simples
            if "one statement at a time" in erro_str:
                erro_str = "Erro na consulta SQL: Query muito complexa. Tente uma pergunta mais simples."
            
            return {
                "sucesso": False,
                "pergunta": pergunta,
                "sql_gerada": None,
                "resposta": None,
                "erro": erro_str,
                "modo": self.modo_usado
            }
    
    def _limpar_sql(self, sql_query: str) -> str:
        """
        Limpa e corrige a SQL gerada para evitar problemas com múltiplas instruções
        """
        if not sql_query:
            return sql_query
        
        # Remove pontos-e-vírgulas extras que podem causar múltiplas instruções
        sql_query = sql_query.strip()
        
        # Se termina com ponto-e-vírgula, remove
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        
        # Se há múltiplos pontos-e-vírgula, pega apenas a primeira instrução
        if ';' in sql_query:
            sql_query = sql_query.split(';')[0].strip()
        
        # Remove quebras de linha excessivas
        sql_query = " ".join(sql_query.split())
        
        return sql_query
    
    def get_schema_info(self) -> str:
        """
        Retorna informações sobre o esquema do banco de dados
        """
        try:
            return self.db.get_table_info()
        except Exception as e:
            return f"Erro ao obter informações do schema: {e}"
    
    def get_exemplos_perguntas(self) -> list:
        """
        Retorna exemplos de perguntas que podem ser feitas
        """
        if self.modo_usado == "demo":
            return [
                "Quantas doses foram aplicadas ao todo?",
                "Quantas doses por laboratório?",
                "Quantos eventos adversos foram registrados?",
                "Quantos eventos adversos por sexo?",
                "Qual a média de idade dos pacientes?",
                "Quantos eventos adversos graves?",
                "Quais laboratórios estão no sistema?",
                "Distribuição de idades dos pacientes",
                "Eventos adversos por tipo",
                "Doses aplicadas por data"
            ]
        else:
            return [
                "Quantas doses foram aplicadas ao todo?",
                "Quantas doses por laboratório?",
                "Quantos eventos adversos foram registrados?",
                "Quantos eventos adversos por sexo?",
                "Qual laboratório aplicou mais doses?",
                "Quantas doses foram aplicadas por mês?",
                "Qual a distribuição de doses por faixa etária?",
                "Quantos eventos adversos graves foram registrados?",
                "Qual a média de idade dos pacientes vacinados?",
                "Quantas primeiras doses vs doses de reforço?"
            ]

# Teste básico
if __name__ == "__main__":
    try:
        agente = VaciVidaAI()
        print("✅ Agente VaciVida AI inicializado com sucesso!")
        print(f"📊 Status: {agente.get_status_info()}")
        
        # Teste básico
        resultado = agente.consultar("Quantas doses foram aplicadas?")
        if resultado["sucesso"]:
            print(f"🤖 Resposta: {resultado['resposta']}")
            print(f"🔧 Modo: {resultado['modo']}")
        else:
            print(f"❌ Erro: {resultado['erro']}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
