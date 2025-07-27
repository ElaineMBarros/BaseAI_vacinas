"""
Teste das correções de SQL no agente VaciVida
"""

from agente_vacivida_azure import VaciVidaAI

def testar_consultas():
    try:
        print("🧪 Testando correções de SQL")
        print("=" * 50)
        
        agente = VaciVidaAI()
        print("✅ Agente inicializado com sucesso!")
        print(f"📊 Status: {agente.get_status_info()}")
        
        # Perguntas que podem gerar SQL problemática
        perguntas_teste = [
            "Quantas doses foram aplicadas por mês?",
            "Quantas doses por laboratório?",
            "Qual a média de idade dos pacientes?",
            "Quantos eventos adversos por sexo?"
        ]
        
        for pergunta in perguntas_teste:
            print(f"\n🔍 Testando: {pergunta}")
            print("-" * 40)
            
            resultado = agente.consultar(pergunta)
            
            if resultado["sucesso"]:
                print("✅ Sucesso!")
                print(f"🤖 Resposta: {resultado['resposta']}")
                print(f"🔧 SQL: {resultado['sql_gerada']}")
            else:
                print("❌ Erro:")
                print(f"   {resultado['erro']}")
        
        print(f"\n🎉 Teste concluído!")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    testar_consultas()
