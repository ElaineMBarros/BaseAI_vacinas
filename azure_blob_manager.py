import os
import tempfile
from azure.storage.blob import BlobServiceClient
import streamlit as st
from dotenv import load_dotenv

class AzureBlobManager:
    """
    Gerenciador para Azure Blob Storage
    """
    
    def __init__(self):
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Pega as credenciais do Azure
        self.connection_string = self._get_azure_connection_string()
        self.container_name = "vacivida-data"
        self.blob_name = "vacivida.db"
        
        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        else:
            self.blob_service_client = None
    
    def _get_azure_connection_string(self):
        """Obtém a connection string do Azure de diferentes fontes"""
        # Primeiro tenta pegar do .env (para local)
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        # Se não encontrar no .env, tenta Streamlit secrets (para cloud)
        if not connection_string:
            try:
                if hasattr(st, 'secrets') and 'AZURE_STORAGE_CONNECTION_STRING' in st.secrets:
                    connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
            except:
                pass  # Ignora erro se não conseguir acessar secrets
        
        return connection_string
    
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
            
            with open(local_db_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"✅ Database '{local_db_path}' enviado para Azure Blob Storage com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar database para Azure: {e}")
            return False
    
    def download_database(self, local_db_path=None):
        """
        Baixa o banco de dados do Azure Blob Storage
        """
        if not self.blob_service_client:
            print("⚠️ Azure connection string não configurada, usando modo local")
            return None
        
        try:
            # Se não especificar caminho, usar temporário
            if local_db_path is None:
                local_db_path = os.path.join(tempfile.gettempdir(), "vacivida_temp.db")
            
            # Download do arquivo
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=self.blob_name
            )
            
            with open(local_db_path, "wb") as download_file:
                download_data = blob_client.download_blob()
                download_file.write(download_data.readall())
            
            print(f"✅ Database baixado do Azure para '{local_db_path}'")
            return local_db_path
            
        except Exception as e:
            print(f"❌ Erro ao baixar database do Azure: {e}")
            return None
    
    def database_exists_in_azure(self):
        """
        Verifica se o banco de dados existe no Azure
        """
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=self.blob_name
            )
            return blob_client.exists()
        except Exception:
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

# Função utilitária para usar em outros módulos
def get_database_path():
    """
    Retorna o caminho do banco de dados, baixando do Azure se necessário
    """
    azure_manager = AzureBlobManager()
    
    # Verifica se o banco existe localmente
    local_path = "vacivida.db"
    if os.path.exists(local_path):
        print("✅ Usando banco de dados local")
        return local_path
    
    # Tenta baixar do Azure
    downloaded_path = azure_manager.download_database()
    if downloaded_path:
        print("✅ Banco de dados baixado do Azure")
        return downloaded_path
    
    # Se não conseguir, retorna None (vai usar modo demo)
    print("⚠️ Banco não encontrado localmente nem no Azure, usando modo demo")
    return None

if __name__ == "__main__":
    # Teste do Azure Blob Manager
    manager = AzureBlobManager()
    
    print("🔍 Informações do banco no Azure:")
    print(manager.get_database_info())
    
    if os.path.exists("vacivida.db"):
        print("\n📤 Fazendo upload do banco local para Azure...")
        success = manager.upload_database("vacivida.db")
        if success:
            print("✅ Upload concluído!")
        else:
            print("❌ Falha no upload")
    else:
        print("ℹ️ Banco local não encontrado para upload")
