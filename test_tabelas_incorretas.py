#!/usr/bin/env python3
"""
Teste específico para o erro de tabelas inexistentes
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

try:
    from agente_vacivida import VaciVidaAI
except ImportError as e:
    print(f"❌ Erro ao importar o agente: {e}")
    exit(1)

def teste_validacao_tabelas():
    """Testa se o agente está usando as tabelas corretas"""
    
    print("🔍 TESTE DE VALIDAÇÃO DE TABELAS")
    print("=" * 50)
    
    try:
        agente = VaciVidaAI()
        print("✅ Agente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        return False
    
    # Testa a função de validação diretamente
    casos_teste = [
        ('SELECT COUNT(*) FROM "Tabela com doses de vacinas"', 'SELECT COUNT(*) FROM vcvd_dose'),
        ('SELECT * FROM doses', 'SELECT * FROM vcvd_dose'),
        ('SELECT * FROM "eventos_adversos"', 'SELECT * FROM vcvd_evento_adverso'),
        ('SELECT * FROM vcvd_dose', 'SELECT * FROM vcvd_dose'),  # Já correto
    ]
    
    print("\n🧪 Testando validação de SQL:")
    for sql_entrada, sql_esperada in casos_teste:
        sql_corrigida = agente._validar_sql(sql_entrada)
        if sql_corrigida == sql_esperada:
            print(f"✅ '{sql_entrada}' -> '{sql_corrigida}'")
        else:
            print(f"❌ '{sql_entrada}' -> '{sql_corrigida}' (esperado: '{sql_esperada}')")
    
    # Testa consultas que anteriormente causavam erro
    consultas_teste = [
        "Quantas doses foram aplicadas?",
        "Quantos eventos adversos foram registrados?",
        "Quantas doses por laboratório?",
    ]
    
    print(f"\n🔍 Testando consultas que causavam erro de tabela:")
    sucessos = 0
    
    for consulta in consultas_teste:
        print(f"\n• Testando: {consulta}")
        resultado = agente.consultar(consulta)
        
        if resultado["sucesso"]:
            print(f"  ✅ Sucesso!")
            print(f"  📝 SQL: {resultado['sql_gerada']}")
            
            # Verifica se não há tabelas incorretas na SQL
            sql = resultado['sql_gerada']
            if sql and "Tabela com" not in sql and "tabela_" not in sql:
                print(f"  ✅ SQL usa tabelas corretas")
            else:
                print(f"  ⚠️ SQL ainda pode ter problemas: {sql}")
            
            sucessos += 1
        else:
            print(f"  ❌ Falha: {resultado['erro']}")
    
    print(f"\n📊 Resultado: {sucessos}/{len(consultas_teste)} consultas bem-sucedidas")
    return sucessos == len(consultas_teste)

if __name__ == "__main__":
    print("🚀 TESTE DE CORREÇÃO - TABELAS INEXISTENTES")
    print("=" * 50)
    
    if teste_validacao_tabelas():
        print("\n🎉 Correção bem-sucedida! O problema de tabelas inexistentes foi resolvido.")
        exit(0)
    else:
        print("\n⚠️ Ainda há problemas. Verifique os detalhes acima.")
        exit(1)
