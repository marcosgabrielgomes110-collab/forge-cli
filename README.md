# Forge CLI

> Gerador de projetos Python que realmente funciona. Sem complicação.

Criado por **Marcos Gomes**

---

## O que é?

O Forge CLI é uma ferramenta simples para criar projetos Python com estrutura pronta. Escolheu um template? Em segundos você tem um projeto configurado com ambiente virtual, dependências instaladas e estrutura organizada.

## Instalação Rápida

```bash
# Clone o repositório
git clone <repo-url>
cd forge-cli

# Use diretamente
python main.py --help
```

## Como Usar

### Ver templates disponíveis

```bash
python main.py list
```

### Criar um novo projeto

```bash
# Básico - cria com nome do template
python main.py new cli-tool

# Com nome customizado (-n)
python main.py new cli-tool -n meuapp

# Com todas as opções
python main.py new cli-tool ./projetos/meu-app \
  -n meuapp \
  -a "Seu Nome" \
  -d "Descrição do projeto" \
  -v "1.0.0"
```

### Flags disponíveis

| Flag | Descrição |
|------|-----------|
| `-n, --name` | Nome do projeto (vai no pyproject.toml) |
| `-a, --author` | Nome do autor |
| `-d, --description` | Descrição do projeto |
| `-v, --version` | Versão inicial (padrão: 0.1.0) |
| `-o, --output` | Caminho de saída |
| `--no-venv` | Não cria ambiente virtual |
| `--no-install` | Não instala dependências |
| `--template-dir` | Usa templates de outro diretório |

## Templates Disponíveis

### cli-tool
Estrutura para ferramentas de linha de comando com:
- Sistema de comandos modular
- Logging configurado
- Colorama para cores no terminal
- Comandos de exemplo (hello, status)

### rest-api
API REST completa com:
- FastAPI + Uvicorn
- Rotas organizadas em módulos
- Middleware de logging
- Documentação automática (/docs)

## Exemplos Práticos

```bash
# Criar uma CLI chamada "supercli"
python main.py new cli-tool -n supercli
cd supercli
python main.py hello

# Criar uma API
python main.py new rest-api minha-api -n minhaapi
cd minha-api
python main.py
# Acesse http://localhost:8000/docs
```

## Estrutura dos Projetos Gerados

Todos os projetos já saem com:
- ✅ Ambiente virtual (.venv) criado
- ✅ Dependências instaladas
- ✅ pyproject.toml configurado
- ✅ README com instruções
- ✅ Estrutura de pastas organizada

## Precisa de Ajuda?

```bash
python main.py --help
python main.py new --help
```

---

**Forge CLI** — Feito por Marcos Gomes para simplificar o começo dos projetos Python.
