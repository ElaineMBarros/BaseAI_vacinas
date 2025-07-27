#!/usr/bin/env python3
"""
Teste de robustez do agente VaciVida AI
Testa consultas que anteriormente geravam erros de múltiplas instruções SQL
"""

import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Verifica se a chave da OpenAI está configurada
if not os.getenv("OPENAI_API_KEY"):
    print("❌ A variável OPENAI_API_KEY não está configurada no arquivo .env")
    sys.exit(1)

# Importa o agente
try:
    from agente_vacivida import VaciVidaAI
except ImportError as e:
    print(f"❌ Erro ao importar o agente: {e}")
    sys.exit(1)

def teste_consultas_problematicas():
    """Testa consultas que anteriormente geravam erros"""
    
    print("🧪 Iniciando testes de robustez do agente VaciVida AI...")
    print("=" * 60)
    
    try:
        agente = VaciVidaAI()
        print("✅ Agente inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        return False
    
    # Lista de consultas que anteriormente causavam problemas
    consultas_teste = [
        "Quantas doses foram aplicadas por mês?",
        "Mostre os 5 laboratórios com mais doses aplicadas",
        "Qual a distribuição de doses por faixa etária?",
        "Quantos eventos adversos por tipo ordenado por quantidade?",
        "Liste as primeiras 10 doses aplicadas por data",
        "Quantas doses por laboratório ordenado decrescente?",
        "Média de idade dos pacientes vacinados por sexo",
        "Top 3 tipos de eventos adversos mais comuns",
        "Doses aplicadas em janeiro de 2021",
        "Eventos adversos graves vs não graves"
    ]
    
    resultados = []
    sucessos = 0
    
    for i, consulta in enumerate(consultas_teste, 1):
        print(f"\n🔍 Teste {i}: {consulta}")
        print("-" * 50)
        
        resultado = agente.consultar(consulta)
        
        if resultado["sucesso"]:
            print(f"✅ Sucesso!")
            print(f"📝 SQL: {resultado['sql_gerada']}")
            print(f"💬 Resposta: {resultado['resposta']}")
            if resultado.get("erro"):
                print(f"⚠️ Aviso: {resultado['erro']}")
            sucessos += 1
        else:
            print(f"❌ Falha: {resultado['erro']}")
        
        resultados.append({
            "consulta": consulta,
            "sucesso": resultado["sucesso"],
            "erro": resultado.get("erro")
        })
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Total de testes: {len(consultas_teste)}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {len(consultas_teste) - sucessos}")
    print(f"Taxa de sucesso: {(sucessos / len(consultas_teste)) * 100:.1f}%")
    
    # Detalhes das falhas
    falhas = [r for r in resultados if not r["sucesso"]]
    if falhas:
        print(f"\n❌ CONSULTAS QUE FALHARAM:")
        for falha in falhas:
            print(f"- {falha['consulta']}")
            print(f"  Erro: {falha['erro']}")
    
    return sucessos == len(consultas_teste)

def teste_limpeza_sql():
    """Testa a função de limpeza de SQL"""
    
    print("\n🧽 Testando função de limpeza de SQL...")
    print("-" * 50)
    
    try:
        agente = VaciVidaAI()
    except Exception as e:
        print(f"❌ Erro ao inicializar o agente: {e}")
        return False
    
    casos_teste = [
        ("SELECT * FROM tabela;", "SELECT * FROM tabela"),
        ("SELECT * FROM tabela; LIMIT 5;", "SELECT * FROM tabela"),
        ("SELECT * FROM tabela;; LIMIT 5", "SELECT * FROM tabela"),
        ("SELECT * FROM tabela; ORDER BY id; LIMIT 5", "SELECT * FROM tabela"),
        ("  SELECT * FROM tabela;  ", "SELECT * FROM tabela"),
        ("", ""),
        (None, None)
    ]
    
    sucessos = 0
    for entrada, esperado in casos_teste:
        resultado = agente._limpar_sql(entrada) if entrada is not None else None
        if resultado == esperado:
            print(f"✅ '{entrada}' -> '{resultado}'")
            sucessos += 1
        else:
            print(f"❌ '{entrada}' -> '{resultado}' (esperado: '{esperado}')")
    
    print(f"\n📊 Limpeza SQL: {sucessos}/{len(casos_teste)} casos passaram")
    return sucessos == len(casos_teste)

if __name__ == "__main__":
    print("🚀 TESTE DE ROBUSTEZ DO AGENTE VACIVIDA AI")
    print("=" * 60)
    
    # Executa os testes
    teste1 = teste_limpeza_sql()
    teste2 = teste_consultas_problematicas()
    
    print("\n" + "=" * 60)
    print("🏁 RESULTADO FINAL")
    print("=" * 60)
    
    if teste1 and teste2:
        print("🎉 Todos os testes passaram! O agente está robusto.")
        sys.exit(0)
    else:
        print("⚠️ Alguns testes falharam. Verifique os detalhes acima.")
        sys.exit(1)
