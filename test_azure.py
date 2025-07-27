"""
Teste simples da conexão Azure Blob Storage
"""

import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def testar_azure():
    print("🧪 Testando conexão com Azure Blob Storage")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Pega a connection string
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if not connection_string:
        print("❌ AZURE_STORAGE_CONNECTION_STRING não encontrada no .env")
        return False
    
    print("✅ Connection string encontrada")
    print(f"📋 Account: {connection_string.split('AccountName=')[1].split(';')[0]}")
    
    try:
        # Testa conexão
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Tenta listar containers (vai dar erro se não conseguir conectar)
        containers = list(blob_service_client.list_containers())
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"📂 Containers existentes: {len(containers)}")
        
        for container in containers:
            print(f"   - {container.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    sucesso = testar_azure()
    
    if sucesso:
        print("\n🎉 Azure configurado corretamente!")
        print("💡 Próximo passo: python upload_to_azure.py")
    else:
        print("\n🔧 Verifique a connection string no arquivo .env")
