# OrionProv# OrionProv

![Status do Projeto](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![Linguagem](https://img.shields.io/badge/python-3.8%2B-blue)
![Banco de Dados](https://img.shields.io/badge/database-SQLite%20%7C%20PostgreSQL-darkblue)
![Foco](https://img.shields.io/badge/foco-Seguran%C3%A7a%20%26%20Proveni%C3%AAncia-red)

O **OrionProv** é uma ferramenta de segurança e auditoria dedicada à captura, armazenamento e análise de dados de **proveniência de dados (Data Provenance)** e monitoramento de processos de baixo nível. O sistema rastreia o ciclo de vida das informações, mapeando a origem, as transformações intermediárias e o destino dos arquivos, permitindo auditorias completas, conformidade de segurança e suporte a análises forenses digitais.

## 🚀 Funcionalidades Principais

- **Captura de Proveniência Ativa:** Rastreamento completo da linhagem de dados (Data Lineage), identificando quem manipulou o dado, quando e por meio de qual processo.
- **Monitoramento de Processos:** Captura em tempo real de chamadas de sistema, criação, execução e encerramento de processos executados pelo sistema operacional.
- **Rastreamento de Arquivos:** Monitoramento de eventos críticos em arquivos do sistema, tais como criação, leitura, modificação e deleção (CRUD de arquivos).
- **Armazenamento Estruturado:** Persistência robusta das trilhas de auditoria e grafos de proveniência utilizando bancos de dados estruturados para otimização de consultas complexas.
- **Foco em Segurança Forense:** Geração de históricos imutáveis que auxiliam na detecção de anomalias, acessos não autorizados e quebras de integridade de dados.

## 🛠️ Tecnologias Utilizadas

- **Linguagem Principal:** [Python 3.x](https://www.python.org/)
- **Persistência de Dados:** SQLite (para desenvolvimento ágil e testes locais) e PostgreSQL (para ambientes de produção)
- **Modelagem de Proveniência:** Inspirado no modelo conceitual padrão **W3C PROV-DM** (mapeamento baseado em _Entities_, _Activities_ e _Agents_).

## 📋 Pré-requisitos

Antes de iniciar o ambiente de desenvolvimento, você precisará ter instalado em sua máquina:

- Python 3.8 ou superior
- Gerenciador de pacotes `pip`
- Sistema operacional Linux (altamente recomendado para a captura nativa de chamadas de sistema/processos) ou Windows com as devidas dependências de API

## 🔧 Instalação e Configuração

Siga os passos abaixo para configurar o repositório localmente:

### Clonar o Repositório

```bash
git clone [https://github.com/laurabgularte/OrionProv.git](https://github.com/laurabgularte/OrionProv.git)
cd OrionProv



# Criar o ambiente virtual (venv)

python3 -m venv venv

# Ativar o ambiente virtual

# No Linux/macOS:

source venv/bin/activate

# No Windows:

venv\Scripts\activate

# Instalar as dependências

pip install -r requirements.txt

#Como executar

python main.py

```
