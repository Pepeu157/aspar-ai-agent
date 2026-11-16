# Desenvolvimento local

## Requisitos

Python 3.11+, Node.js 20+, npm e Git. Não é necessário Microsoft 365, banco ou chave de IA.

## Windows PowerShell

A partir da raiz:

```powershell
py -3.11 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Em um segundo terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Testes backend, executados na raiz:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest -c pytest.ini -q
```

Build frontend:

```powershell
Set-Location frontend
npm run build
```

## Linux/macOS

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cp .env.example .env
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Em outro terminal: `cd frontend && npm install && npm run dev`. Testes: `backend/.venv/bin/python -m pytest -c pytest.ini -q`. Build: `cd frontend && npm run build`.

## Configuração e segurança

Pydantic Settings lê `.env` na raiz e variáveis de processo; variáveis do processo prevalecem. `.env` não é versionado. A API atual usa regras locais e armazenamento em memória. Utilize apenas mensagens sintéticas. Nenhum acesso externo ou credencial é necessário.

API local: `http://127.0.0.1:8000`; OpenAPI: `http://127.0.0.1:8000/docs`; painel: `http://localhost:5173`.
