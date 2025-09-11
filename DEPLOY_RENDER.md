# Deploy no Render

## Configuração no Render

### 1. Criar Web Service
- Conectar repositório GitHub
- Selecionar branch: `feat-deploy-render`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT run:app`

### 2. Variáveis de Ambiente
Configure as seguintes variáveis no painel do Render:

```
DATABASE_NAME=biblego
DATABASE_USER=biblego
DATABASE_PASSWORD=biblego%123!
DATABASE_HOST=177.70.98.148
DATABASE_PORT=6543
```

### 3. Configurações de Runtime
- Python Version: 3.11.9
- Region: Escolha a mais próxima do seu banco de dados

## Comandos Locais

### Testar localmente:
```bash
# Com gunicorn (simula produção)
gunicorn --bind 0.0.0.0:5000 run:app

# Ou desenvolvimento normal
python run.py
```

### Deploy:
1. Push para branch `feat-deploy-render`
2. Render detectará mudanças automaticamente
3. Build e deploy serão executados automaticamente

## Estrutura de Arquivos Adicionados

- `app/Config/production_database.py` - Configuração com variáveis de ambiente
- `render.yaml` - Configuração opcional do Render
- `.env.example` - Exemplo de variáveis de ambiente
- `DEPLOY_RENDER.md` - Este arquivo com instruções