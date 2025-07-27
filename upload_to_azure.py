"""
Script para fazer upload do banco VaciVida para o Azure Blob Storage
"""

import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

class SimpleAzureBlobManager:
    """
    Gerenciador simples para Azure Blob Storage (sem Streamlit)
    """
    
    def __init__(self):
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Pega a connection string
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = "vacivida-data"
        self.blob_name = "vacivida.db"
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        else:
            self.blob_service_client = None
    
    def upload_database(self, local_db_path):
        """
        Faz upload do banco de dados local para o Azure Blob Storage
        """
        if not self.blob_service_client:
            raise ValueError("Azure connection string não configurada")
        
        try:
            # Criar o container se não existir
            container_client = self.blob_service_client.get_container_client(self.container_name)
            try:
                container_client.create_container()
                print(f"✅ Container '{self.container_name}' criado com sucesso")
            except Exception:
                print(f"ℹ️ Container '{self.container_name}' já existe")
            
            # Upload do arquivo
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=self.blob_name
            )
            
            print("🔄 Iniciando upload... (pode demorar alguns minutos)")
            with open(local_db_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"✅ Database '{local_db_path}' enviado para Azure Blob Storage com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar database para Azure: {e}")
            return False
    
    def get_database_info(self):
        """
        Obtém informações sobre o banco no Azure
        """
        if not self.blob_service_client:
            return "Azure não configurado"
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=self.blob_name
            )
            
            if blob_client.exists():
                properties = blob_client.get_blob_properties()
                size_mb = properties.size / (1024 * 1024)
                return f"Banco encontrado no Azure: {size_mb:.1f}MB, última modificação: {properties.last_modified}"
            else:
                return "Banco não encontrado no Azure"
                
        except Exception as e:
            return f"Erro ao obter informações: {e}"

def main():
    print("🚀 VaciVida AI - Upload para Azure Blob Storage")
    print("=" * 50)
    
    # Verificar se o banco local existe
    if not os.path.exists("vacivida.db"):
        print("❌ Arquivo 'vacivida.db' não encontrado na pasta atual")
        print("📁 Certifique-se de que o arquivo está na mesma pasta deste script")
        return
    
    # Obter tamanho do arquivo
    size_mb = os.path.getsize("vacivida.db") / (1024 * 1024)
    print(f"📊 Tamanho do banco: {size_mb:.1f}MB")
    
    # Criar o gerenciador Azure
    try:
        azure_manager = SimpleAzureBlobManager()
        print("✅ Azure Blob Manager inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar Azure: {e}")
        print("🔧 Verifique se a AZURE_STORAGE_CONNECTION_STRING está configurada")
        return
    
    # Verificar informações atuais
    print(f"📋 {azure_manager.get_database_info()}")
    
    # Confirmar upload
    resposta = input(f"\n📤 Deseja fazer upload do banco ({size_mb:.1f}MB) para o Azure? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        print("\n🔄 Iniciando upload...")
        success = azure_manager.upload_database("vacivida.db")
        
        if success:
            print("✅ Upload concluído com sucesso!")
            print("📋 Informações atualizadas:")
            print(f"   {azure_manager.get_database_info()}")
            print("\n🎉 Agora sua aplicação pode acessar o banco do Azure!")
            print("💡 Execute 'streamlit run app.py' para testar")
        else:
            print("❌ Falha no upload")
    else:
        print("❌ Upload cancelado")

if __name__ == "__main__":
    main()
