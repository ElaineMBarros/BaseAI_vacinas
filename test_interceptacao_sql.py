#!/usr/bin/env python3
"""
Teste direto da classe FixedSQLDatabase para interceptar SQLs problemáticas
"""

import sqlite3
import tempfile
from sqlalchemy import create_engine
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a classe customizada
try:
    from agente_vacivida_cloud import FixedSQLDatabase
except ImportError:
    print("❌ Erro ao importar FixedSQLDatabase")
    exit(1)

def criar_banco_teste():
    """Cria um banco de teste com as tabelas corretas"""
    # Cria um banco temporário
    db_temp = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(db_temp)
    cursor = conn.cursor()
    
    # Cria as tabelas corretas
    cursor.execute('''
    CREATE TABLE vcvd_dose (
        vcvd_doseid INTEGER PRIMARY KEY,
        vcvd_laboratorio TEXT,
        vcvd_sexo INTEGER,
        vcvd_idade INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE vcvd_evento_adverso (
        Id INTEGER PRIMARY KEY,
        VCVD_SEXO INTEGER,
        VCVD_GRAVE_ENCERRAMENTO_EAG INTEGER
    )
    ''')
    
    # Insere alguns dados de teste
    cursor.execute("INSERT INTO vcvd_dose VALUES (1, 'PFIZER', 1, 30)")
    cursor.execute("INSERT INTO vcvd_dose VALUES (2, 'ASTRAZENECA', 2, 45)")
    cursor.execute("INSERT INTO vcvd_evento_adverso VALUES (1, 1, 0)")
    
    conn.commit()
    conn.close()
    
    return db_temp

def teste_fixed_sql_database():
    """Testa se a FixedSQLDatabase corrige SQLs automaticamente"""
    
    print("🔍 TESTE DA CLASSE FixedSQLDatabase")
    print("=" * 50)
    
    # Cria banco de teste
    db_path = criar_banco_teste()
    
    try:
        # Cria a engine e database customizada
        engine = create_engine(f"sqlite:///{db_path}")
        db = FixedSQLDatabase(
            engine, 
            include_tables=["vcvd_dose", "vcvd_evento_adverso"]
        )
        
        print("✅ FixedSQLDatabase inicializada com sucesso!")
        
        # Testa SQLs problemáticas que devem ser corrigidas automaticamente
        sqls_teste = [
            'SELECT COUNT(*) FROM "Tabela com doses de vacinas"',
            'SELECT * FROM doses',
            'SELECT COUNT(*) FROM vcvd_dose',  # Já correto
        ]
        
        sucessos = 0
        
        for sql in sqls_teste:
            print(f"\n🧪 Testando SQL: {sql}")
            try:
                resultado = db.run(sql)
                print(f"  ✅ Sucesso! Resultado: {resultado}")
                sucessos += 1
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
        print(f"\n📊 Resultado: {sucessos}/{len(sqls_teste)} SQLs executadas com sucesso")
        
        # Fecha conexão antes de limpar arquivo
        engine.dispose()
        
        # Tenta limpar arquivo temporário (pode falhar no Windows)
        try:
            os.unlink(db_path)
        except (PermissionError, OSError):
            pass  # Ignora erro de limpeza no Windows
        
        return sucessos == len(sqls_teste)
        
    except Exception as e:
        print(f"❌ Erro ao testar FixedSQLDatabase: {e}")
        # Tenta limpar arquivo mesmo em caso de erro
        try:
            if 'engine' in locals():
                engine.dispose()
            if os.path.exists(db_path):
                os.unlink(db_path)
        except (PermissionError, OSError):
            pass  # Ignora erro de limpeza
        return False

if __name__ == "__main__":
    print("🚀 TESTE DE INTERCEPTAÇÃO DE SQL")
    print("=" * 50)
    
    if teste_fixed_sql_database():
        print("\n🎉 Interceptação funcionando! SQLs problemáticas são corrigidas automaticamente.")
        exit(0)
    else:
        print("\n⚠️ Interceptação falhou. Verifique os detalhes acima.")
        exit(1)
