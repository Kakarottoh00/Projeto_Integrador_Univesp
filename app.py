from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'estoque_secretkey_2026'

DB_PATH = 'estoque.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            categoria TEXT,
            preco_custo REAL NOT NULL DEFAULT 0,
            preco_venda REAL NOT NULL DEFAULT 0,
            quantidade INTEGER NOT NULL DEFAULT 0,
            estoque_minimo INTEGER NOT NULL DEFAULT 5,
            criado_em TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
            quantidade INTEGER NOT NULL,
            observacao TEXT,
            data TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    conn = get_db()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    total_produtos = len(produtos)
    valor_total = sum(p['preco_custo'] * p['quantidade'] for p in produtos)
    estoque_baixo = [p for p in produtos if p['quantidade'] <= p['estoque_minimo']]
    movimentacoes = conn.execute('''
        SELECT m.*, p.nome as produto_nome 
        FROM movimentacoes m 
        JOIN produtos p ON m.produto_id = p.id 
        ORDER BY m.data DESC LIMIT 8
    ''').fetchall()
    conn.close()
    return render_template('dashboard.html',
        total_produtos=total_produtos,
        valor_total=valor_total,
        estoque_baixo=estoque_baixo,
        movimentacoes=movimentacoes,
        produtos=produtos
    )

@app.route('/produtos')
def listar_produtos():
    conn = get_db()
    busca = request.args.get('busca', '')
    categoria = request.args.get('categoria', '')
    query = 'SELECT * FROM produtos WHERE 1=1'
    params = []
    if busca:
        query += ' AND (nome LIKE ? OR descricao LIKE ?)'
        params += [f'%{busca}%', f'%{busca}%']
    if categoria:
        query += ' AND categoria = ?'
        params.append(categoria)
    query += ' ORDER BY nome'
    produtos = conn.execute(query, params).fetchall()
    categorias = conn.execute('SELECT DISTINCT categoria FROM produtos WHERE categoria != "" ORDER BY categoria').fetchall()
    conn.close()
    return render_template('produtos.html', produtos=produtos, categorias=categorias, busca=busca, categoria=categoria)

@app.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco_custo = float(request.form['preco_custo'].replace(',', '.'))
        preco_venda = float(request.form['preco_venda'].replace(',', '.'))
        quantidade = int(request.form['quantidade'])
        estoque_minimo = int(request.form.get('estoque_minimo', 5))
        if not nome:
            flash('O nome do produto é obrigatório.', 'erro')
            return render_template('form_produto.html', produto=None)
        conn = get_db()
        conn.execute('''
            INSERT INTO produtos (nome, descricao, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, descricao, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        flash(f'Produto "{nome}" cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_produtos'))
    return render_template('form_produto.html', produto=None)

@app.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
def editar_produto(id):
    conn = get_db()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    if not produto:
        flash('Produto não encontrado.', 'erro')
        return redirect(url_for('listar_produtos'))
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        preco_custo = float(request.form['preco_custo'].replace(',', '.'))
        preco_venda = float(request.form['preco_venda'].replace(',', '.'))
        estoque_minimo = int(request.form.get('estoque_minimo', 5))
        conn.execute('''
            UPDATE produtos SET nome=?, descricao=?, categoria=?, preco_custo=?, preco_venda=?, estoque_minimo=?
            WHERE id=?
        ''', (nome, descricao, categoria, preco_custo, preco_venda, estoque_minimo, id))
        conn.commit()
        conn.close()
        flash(f'Produto "{nome}" atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_produtos'))
    conn.close()
    return render_template('form_produto.html', produto=produto)

@app.route('/produtos/<int:id>/excluir', methods=['POST'])
def excluir_produto(id):
    conn = get_db()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    if produto:
        conn.execute('DELETE FROM movimentacoes WHERE produto_id = ?', (id,))
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.commit()
        flash(f'Produto "{produto["nome"]}" excluído.', 'sucesso')
    conn.close()
    return redirect(url_for('listar_produtos'))

@app.route('/movimentacoes')
def listar_movimentacoes():
    conn = get_db()
    tipo = request.args.get('tipo', '')
    query = '''
        SELECT m.*, p.nome as produto_nome 
        FROM movimentacoes m 
        JOIN produtos p ON m.produto_id = p.id
    '''
    params = []
    if tipo:
        query += ' WHERE m.tipo = ?'
        params.append(tipo)
    query += ' ORDER BY m.data DESC'
    movimentacoes = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('movimentacoes.html', movimentacoes=movimentacoes, tipo=tipo)

@app.route('/movimentacoes/nova', methods=['GET', 'POST'])
def nova_movimentacao():
    conn = get_db()
    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        tipo = request.form['tipo']
        quantidade = int(request.form['quantidade'])
        observacao = request.form.get('observacao', '').strip()
        produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,)).fetchone()
        if not produto:
            flash('Produto não encontrado.', 'erro')
            return redirect(url_for('nova_movimentacao'))
        if tipo == 'saida' and produto['quantidade'] < quantidade:
            flash(f'Estoque insuficiente! Disponível: {produto["quantidade"]} unidades.', 'erro')
            produtos = conn.execute('SELECT * FROM produtos ORDER BY nome').fetchall()
            conn.close()
            return render_template('form_movimentacao.html', produtos=produtos)
        nova_qtd = produto['quantidade'] + quantidade if tipo == 'entrada' else produto['quantidade'] - quantidade
        conn.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_qtd, produto_id))
        conn.execute('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (produto_id, tipo, quantidade, observacao, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        acao = 'Entrada' if tipo == 'entrada' else 'Saída'
        flash(f'{acao} de {quantidade} unidade(s) de "{produto["nome"]}" registrada!', 'sucesso')
        return redirect(url_for('listar_movimentacoes'))
    produtos = conn.execute('SELECT * FROM produtos ORDER BY nome').fetchall()
    conn.close()
    return render_template('form_movimentacao.html', produtos=produtos)

@app.route('/api/produto/<int:id>')
def api_produto(id):
    conn = get_db()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    if produto:
        return jsonify(dict(produto))
    return jsonify({}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
