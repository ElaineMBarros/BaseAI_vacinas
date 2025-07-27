# Configuração do Azure Blob Storage para VaciVida AI

## 🔧 Como configurar o Azure Blob Storage:

### 1. **Criar Storage Account no Azure:**

1. Acesse o [Portal do Azure](https://portal.azure.com)
2. Vá em "Storage accounts" > "Create"
3. Configure:
   - **Resource group**: Crie um novo (ex: "vacivida-rg")
   - **Storage account name**: Nome único (ex: "vacividastorage2025")
   - **Region**: Escolha uma região próxima
   - **Performance**: Standard
   - **Redundancy**: LRS (mais barato)
4. Clique em "Review + create"

### 2. **Obter a Connection String:**

1. Vá para sua Storage Account criada
2. Menu lateral > "Access keys"
3. Copie a "Connection string" da Key1

### 3. **Configurar localmente:**

Adicione no seu arquivo `.env`:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

### 4. **Para o Streamlit Cloud:**

No Streamlit Cloud, vá em Settings > Secrets e adicione:

```toml
OPENAI_API_KEY = "sua_chave_openai"
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=..."
```

### 5. **Comandos para testar:**

```bash
# Testar o Azure Blob Manager
python azure_blob_manager.py

# Fazer upload do banco
python -c "from azure_blob_manager import AzureBlobManager; m = AzureBlobManager(); m.upload_database('vacivida.db')"
```

## 💰 **Custos estimados:**

- **Storage Account**: ~$0.02/GB/mês
- **Transferências**: ~$0.09/GB
- **Para um banco de 150MB**: < $1/mês

## 🔒 **Segurança:**

- Connection strings são mantidas em segredo
- Acesso controlado por chaves do Azure
- Dados criptografados em trânsito e em repouso

## 🚀 **Benefícios:**

✅ Banco acessível globalmente
✅ Backup automático
✅ Escalabilidade
✅ Integração perfeita com aplicações
✅ Sem limite de tamanho do GitHub
