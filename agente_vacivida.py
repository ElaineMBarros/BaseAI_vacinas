import os
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine

class VaciVidaAI:
    """
    Agente AI para consultas no banco de dados VaciVida
    """
    
    def __init__(self):
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Verifica se a chave da OpenAI está definida (local ou Streamlit Cloud)
        api_key = None
        
        # Primeiro tenta pegar do .env (para local)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Se não encontrou e o Streamlit está disponível, tenta os secrets
        if not api_key and STREAMLIT_AVAILABLE and hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
        
        if not api_key:
            raise ValueError("A variável de ambiente OPENAI_API_KEY não está definida.")
        
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Configuração do banco de dados
        self.engine = create_engine("sqlite:///vacivida.db")
        self.db = SQLDatabase(
            self.engine, 
            sample_rows_in_table_info=3, 
            max_string_length=300, 
            include_tables=["vcvd_dose", "vcvd_evento_adverso"]
        )
        
        # Configuração do modelo OpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k", 
            temperature=0,
            max_tokens=1000
        )
        
        # Criação do chain SQL
        self.db_chain = SQLDatabaseChain.from_llm(
            llm=self.llm, 
            db=self.db, 
            verbose=False,  # Desabilitamos verbose para a interface web
            return_intermediate_steps=True
        )
    
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

    def _limpar_sql(self, sql: str) -> str:
        """
        Limpa e corrige a SQL gerada para evitar problemas com múltiplas instruções
        """
        if not sql:
            return sql
            
        # Remove pontos-e-vírgulas extras que podem causar múltiplas instruções
        sql = sql.strip()
        
        # Se termina com ponto-e-vírgula, remove
        if sql.endswith(';'):
            sql = sql[:-1]
        
        # Se há múltiplos pontos-e-vírgula, pega apenas a primeira instrução
        if ';' in sql:
            sql = sql.split(';')[0].strip()
        
        return sql

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
                        break
            
            # Limpar e validar a SQL gerada
            if sql_query != "Não disponível":
                sql_query = self._limpar_sql(sql_query)
                sql_query = self._validar_sql(sql_query)
            
            return {
                "sucesso": True,
                "pergunta": pergunta,
                "sql_gerada": sql_query,
                "resposta": resposta,
                "erro": None
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
                        "erro": f"Resolvido automaticamente (erro original: múltiplas instruções SQL)"
                    }
                    
                except Exception as e2:
                    return {
                        "sucesso": False,
                        "pergunta": pergunta,
                        "sql_gerada": None,
                        "resposta": None,
                        "erro": f"Erro original: {erro_str}. Erro no fallback: {str(e2)}"
                    }
            
            return {
                "sucesso": False,
                "pergunta": pergunta,
                "sql_gerada": None,
                "resposta": None,
                "erro": erro_str
            }
    
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
        
        # Teste básico
        resultado = agente.consultar("Quantas doses foram aplicadas?")
        if resultado["sucesso"]:
            print(f"🤖 Resposta: {resultado['resposta']}")
        else:
            print(f"❌ Erro: {resultado['erro']}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
