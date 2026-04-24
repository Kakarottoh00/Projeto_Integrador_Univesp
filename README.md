# EstoqueSimples 📦
Sistema Web para Gestão de Estoque de Pequenos Negócios
Projeto Integrador — UNIVESP | Grupo 1

## Como rodar o projeto

### 1. Instale o Python (3.10+)
https://www.python.org/downloads/

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
# Windows:
python -m venv venv
# Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Inicie o servidor
```bash
python app.py
```

### 5. Acesse no navegador
```
http://localhost:5000
```

---

## Funcionalidades
- ✅ Dashboard com resumo do estoque
- ✅ Cadastro, edição e exclusão de produtos (CRUD)
- ✅ Registro de entradas e saídas de mercadorias
- ✅ Alertas de estoque baixo/zerado
- ✅ Filtro por categoria e busca por nome
- ✅ Cálculo automático do valor total em estoque
- ✅ Histórico completo de movimentações

## Tecnologias
- **Backend:** Python + Flask
- **Banco de dados:** SQLite (arquivo `estoque.db` criado automaticamente)
- **Frontend:** HTML5, CSS3 (sem frameworks externos)
- **Controle de versão:** Git (recomendado)

## Integrantes
- Edmar Egidio Da Silva Ricieri
- Eder Gomes do Nascimento
- Rebeca Gomide dos Santos de Oliveira
- Rony José da Silva

**Orientadora:** Fernanda Moreira De Souza Berretta
