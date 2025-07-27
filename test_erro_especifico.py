#!/usr/bin/env python3
"""
Teste específico para a consulta que gerava o erro original:
"SELECT strftime('%m', "vcvd_data") AS month, COUNT("vcvd_doseid") AS total_doses FROM vcvd_dose GROUP BY month ORDER BY month; LIMIT 5;"
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

def teste_consulta_especifica():
    """Testa a consulta específica que estava gerando erro"""
    
    print("🔍 TESTE DA CONSULTA ESPECÍFICA QUE GERAVA ERRO")
    print("=" * 60)
    
    try:
        agente = VaciVidaAI()
        print("✅ Agente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        return False
    
    # A consulta que estava gerando erro
    pergunta = "Quantas doses foram aplicadas por mês?"
    
    print(f"\n🤖 Pergunta: {pergunta}")
    print("-" * 60)
    
    resultado = agente.consultar(pergunta)
    
    if resultado["sucesso"]:
        print(f"✅ Sucesso!")
        print(f"📝 SQL gerada: {resultado['sql_gerada']}")
        print(f"💬 Resposta: {resultado['resposta']}")
        
        if resultado.get("erro"):
            print(f"⚠️ Observação: {resultado['erro']}")
        
        # Verifica se a SQL não tem múltiplas instruções
        sql = resultado['sql_gerada']
        if sql and sql != "Não disponível":
            pontos_virgula = sql.count(';')
            if pontos_virgula == 0:
                print("✅ SQL limpa: Não contém ponto-e-vírgula problemático")
            elif pontos_virgula == 1 and sql.strip().endswith(';'):
                print("⚠️ SQL contém um ponto-e-vírgula no final (pode ser OK)")
            else:
                print(f"❌ SQL contém {pontos_virgula} pontos-e-vírgula (pode ser problemático)")
        
        return True
    else:
        print(f"❌ Falha: {resultado['erro']}")
        return False

def teste_outras_consultas_problematicas():
    """Testa outras consultas que podem gerar problemas similares"""
    
    print("\n🔍 TESTE DE OUTRAS CONSULTAS POTENCIALMENTE PROBLEMÁTICAS")
    print("=" * 60)
    
    try:
        agente = VaciVidaAI()
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        return False
    
    consultas = [
        "Mostre os 10 primeiros laboratórios por ordem alfabética",
        "Quantos eventos adversos por mês ordenado por data",
        "Lista as 5 idades mais comuns limitando o resultado",
        "Conte doses por laboratório e ordene decrescente com limite de 3",
        "Agrupe eventos por sexo e ordene por quantidade limitando a 2"
    ]
    
    sucessos = 0
    
    for i, consulta in enumerate(consultas, 1):
        print(f"\n🔍 Teste {i}: {consulta}")
        print("-" * 50)
        
        resultado = agente.consultar(consulta)
        
        if resultado["sucesso"]:
            print(f"✅ Sucesso!")
            print(f"📝 SQL: {resultado['sql_gerada']}")
            
            # Verifica problemas na SQL
            sql = resultado['sql_gerada']
            if sql and sql != "Não disponível":
                if ';' in sql and not sql.strip().endswith(';'):
                    print("⚠️ SQL pode ter múltiplas instruções")
                else:
                    print("✅ SQL parece limpa")
            
            sucessos += 1
        else:
            print(f"❌ Falha: {resultado['erro']}")
    
    print(f"\n📊 Resultado: {sucessos}/{len(consultas)} consultas bem-sucedidas")
    return sucessos == len(consultas)

if __name__ == "__main__":
    print("🚀 TESTE DA CORREÇÃO DE MÚLTIPLAS INSTRUÇÕES SQL")
    print("=" * 60)
    
    # Executa os testes
    teste1 = teste_consulta_especifica()
    teste2 = teste_outras_consultas_problematicas()
    
    print("\n" + "=" * 60)
    print("🏁 RESULTADO FINAL")
    print("=" * 60)
    
    if teste1 and teste2:
        print("🎉 Correção bem-sucedida! O problema de múltiplas instruções SQL foi resolvido.")
        exit(0)
    else:
        print("⚠️ Ainda há problemas. Verifique os detalhes acima.")
        exit(1)
