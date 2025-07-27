# 💉 VaciVida AI - Sistema Inteligente de Consultas em Dados de Vacinação

Um sistema baseado em IA que permite fazer consultas em linguagem natural sobre dados de vacinação, transformando perguntas em consultas SQL automaticamente.

## 🌟 Funcionalidades

- 🤖 **Consultas em Linguagem Natural**: Faça perguntas como "Quantas doses foram aplicadas por laboratório?"
- 📊 **Análise Automática**: O sistema gera automaticamente consultas SQL complexas
- 🏥 **Dados Reais**: Trabalha com dados reais de vacinação (88.355 doses registradas)
- 💻 **Interface Web**: Interface moderna e intuitiva usando Streamlit
- ⚡ **Respostas Rápidas**: Powered by OpenAI GPT-3.5 Turbo

## 🗃️ Base de Dados

O sistema trabalha com duas tabelas principais:
- **vcvd_dose**: Informações sobre doses aplicadas (laboratório, data, paciente, etc.)
- **vcvd_evento_adverso**: Registros de eventos adversos pós-vacinação

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- Chave da API da OpenAI

### 1. Configuração do Ambiente

```bash
# Clone o repositório (se aplicável)
git clone <seu-repositorio>
cd BaseAI_vacinas

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração da API

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

### 3. Executar a Interface Web

```bash
streamlit run app.py
```

O sistema será aberto automaticamente no seu navegador em `http://localhost:8501`

### 4. Executar o Script Básico (Terminal)

```bash
python main.py
```

## 💡 Exemplos de Perguntas

- "Quantas doses foram aplicadas ao todo?"
- "Quantas doses por laboratório?"
- "Quantos eventos adversos foram registrados?"
- "Quantos eventos adversos por sexo?"
- "Qual laboratório aplicou mais doses?"
- "Quantas doses foram aplicadas por mês?"
- "Qual a distribuição de doses por faixa etária?"
- "Quantos eventos adversos graves foram registrados?"

## 📁 Estrutura do Projeto

```
BaseAI_vacinas/
├── app.py                 # Interface web Streamlit
├── agente_vacivida.py     # Classe principal do agente AI
├── main.py               # Script básico de teste
├── vacivida.db           # Banco de dados SQLite
├── .env                  # Variáveis de ambiente (criar)
├── requirements.txt      # Dependências do projeto
└── README.md            # Este arquivo
```

## 🔧 Componentes Técnicos

- **LangChain**: Framework para aplicações com LLM
- **OpenAI GPT-3.5 Turbo**: Modelo de linguagem para gerar SQL
- **SQLite**: Banco de dados local
- **Streamlit**: Framework para interface web
- **SQLAlchemy**: ORM para conexão com banco de dados

## 🌐 Deploy para Produção

### Streamlit Cloud

1. Faça push do código para GitHub
2. Conecte sua conta no [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy direto do repositório
4. Configure a variável `OPENAI_API_KEY` nas configurações do app

### Heroku

```bash
# Criar Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create vacivida-ai
heroku config:set OPENAI_API_KEY=sua_chave_aqui
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔒 Segurança

- ⚠️ **Nunca commite sua chave da OpenAI no código**
- 🔐 Use sempre variáveis de ambiente para dados sensíveis
- 🛡️ O sistema tem validação de entrada para prevenir SQL injection

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através de [seu-email@exemplo.com].

---

🏥 **VaciVida AI** - Transformando dados de saúde em insights acionáveis através da Inteligência Artificial.
