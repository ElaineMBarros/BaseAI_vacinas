# 🚀 Como Publicar o VaciVida AI no Streamlit Cloud

## 📋 Passo a Passo Completo:

### 1. **Subir o Projeto para o GitHub**

```bash
# No terminal do seu projeto (Git Bash ou PowerShell)
cd d:\projetos\repo_git\BaseAI_vacinas

# Inicializar repositório Git (se ainda não fez)
git init

# Adicionar todos os arquivos
git add .

# Fazer o primeiro commit
git commit -m "🎉 Primeira versão do VaciVida AI - Sistema de consultas inteligentes"

# Conectar com repositório remoto no GitHub
# (Primeiro crie um repositório público no GitHub chamado "vacivida-ai")
git remote add origin https://github.com/SEU_USUARIO/vacivida-ai.git

# Subir o código
git branch -M main
git push -u origin main
```

### 2. **Publicar no Streamlit Cloud**

1. **Acesse:** https://share.streamlit.io/
2. **Faça login** com sua conta GitHub
3. **Clique em "New app"**
4. **Selecione:**
   - Repository: `SEU_USUARIO/vacivida-ai`
   - Branch: `main`
   - Main file path: `app.py`
5. **Clique em "Deploy!"**

### 3. **Configurar Secrets (IMPORTANTE!)**

1. **No Streamlit Cloud, vá em "Settings" > "Secrets"**
2. **Adicione o seguinte conteúdo:**

```toml
OPENAI_API_KEY = "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"
```

3. **Salve as configurações**

### 4. **Aguardar o Deploy**

- O Streamlit Cloud irá instalar as dependências automaticamente
- Aguarde alguns minutos para o app ficar online
- Você receberá uma URL como: `https://vacivida-ai.streamlit.app/`

### 5. **Testar a Aplicação**

- Acesse a URL fornecida
- Teste algumas consultas:
  - "Quantas doses foram aplicadas?"
  - "Quantas doses por laboratório?"
  - "Quantos eventos adversos por sexo?"

## 🎯 **Dicas Importantes:**

- ✅ **Arquivo .env não será enviado** (está no .gitignore)
- ✅ **Chave da API fica segura** nos secrets do Streamlit
- ✅ **App atualiza automaticamente** quando você fizer push no GitHub
- ✅ **É gratuito** para repositórios públicos

## 🔧 **Se der algum erro:**

1. **Verifique os logs** no Streamlit Cloud
2. **Confirme que todas as dependências** estão no requirements.txt
3. **Verifique se a chave da API** está correta nos secrets
4. **O banco vacivida.db** deve estar incluído no repositório

## 📱 **Resultado Final:**

Sua aplicação estará disponível publicamente em uma URL como:
`https://vacivida-ai.streamlit.app/`

E qualquer pessoa poderá fazer consultas inteligentes nos seus dados de vacinação! 🎉

---

**Precisa de ajuda?** Siga os passos acima e me informe se encontrar algum problema!
