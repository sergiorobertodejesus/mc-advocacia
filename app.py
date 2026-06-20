from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = 'mc_advocacia_2026'


def criar_banco():

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute('''

    CREATE TABLE IF NOT EXISTS contatos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT,

        whatsapp TEXT,

        mensagem TEXT,

        status TEXT DEFAULT 'Pendente'

    )

    ''')

    cursor.execute('''

    CREATE TABLE IF NOT EXISTS usuarios(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        usuario TEXT UNIQUE,

        senha TEXT

    )

    ''')

    cursor.execute(

        '''

        INSERT OR IGNORE INTO usuarios

        (usuario, senha)

        VALUES (?, ?)

        ''',

        ('admin', '123456')

    )

    conexao.commit()

    conexao.close()


criar_banco()


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']

        senha = request.form['senha']

        conexao = sqlite3.connect('banco.db')

        cursor = conexao.cursor()

        cursor.execute(

            '''

            SELECT *

            FROM usuarios

            WHERE usuario = ?

            AND senha = ?

            ''',

            (usuario, senha)

        )

        usuario_encontrado = cursor.fetchone()

        conexao.close()

        if usuario_encontrado:

            session['usuario'] = usuario

            return redirect('/admin')

        else:

            return '''

            <h1>Usuário ou senha inválidos.</h1>

            <a href="/login">Tentar novamente</a>

            '''

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.pop('usuario', None)

    return redirect('/login')


@app.route('/receber', methods=['POST'])
def receber():

    nome = request.form['nome']

    whatsapp = request.form['whatsapp']

    mensagem = request.form['mensagem']

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        INSERT INTO contatos

        (nome, whatsapp, mensagem)

        VALUES (?, ?, ?)

        ''',

        (nome, whatsapp, mensagem)

    )

    conexao.commit()

    conexao.close()

    return '''

    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="UTF-8">

    <meta http-equiv="refresh" content="3; url=/">

    <title>Mensagem enviada</title>

    </head>

    <body>

    <h1>Mensagem enviada com sucesso.</h1>

    <p>Você será redirecionado em alguns segundos.</p>

    </body>

    </html>

    '''


@app.route('/admin')
def admin():

    if 'usuario' not in session:

        return redirect('/login')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute('SELECT * FROM contatos')

    contatos = cursor.fetchall()

    conexao.close()

    return render_template(

        'admin.html',

        contatos=contatos,

        usuario=session['usuario']

    )


@app.route('/admin/pendentes')
def pendentes():

    if 'usuario' not in session:

        return redirect('/login')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        SELECT *

        FROM contatos

        WHERE status = 'Pendente'

        '''

    )

    contatos = cursor.fetchall()

    conexao.close()

    return render_template(

        'admin.html',

        contatos=contatos,

        usuario=session['usuario']

    )


@app.route('/admin/atendidos')
def atendidos():

    if 'usuario' not in session:

        return redirect('/login')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        SELECT *

        FROM contatos

        WHERE status = 'Atendido'

        '''

    )

    contatos = cursor.fetchall()

    conexao.close()

    return render_template(

        'admin.html',

        contatos=contatos,

        usuario=session['usuario']

    )


@app.route('/pesquisar')
def pesquisar():

    if 'usuario' not in session:

        return redirect('/login')

    nome = request.args.get('nome', '')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        SELECT *

        FROM contatos

        WHERE nome LIKE ?

        ''',

        ('%' + nome + '%',)

    )

    contatos = cursor.fetchall()

    conexao.close()

    return render_template(

        'admin.html',

        contatos=contatos,

        usuario=session['usuario']

    )


@app.route('/atender/<int:id>')
def atender(id):

    if 'usuario' not in session:

        return redirect('/login')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        UPDATE contatos

        SET status = 'Atendido'

        WHERE id = ?

        ''',

        (id,)

    )

    conexao.commit()

    conexao.close()

    return redirect('/admin')


@app.route('/excluir/<int:id>')
def excluir(id):

    if 'usuario' not in session:

        return redirect('/login')

    conexao = sqlite3.connect('banco.db')

    cursor = conexao.cursor()

    cursor.execute(

        '''

        DELETE FROM contatos

        WHERE id = ?

        ''',

        (id,)

    )

    conexao.commit()

    conexao.close()

    return redirect('/admin')


if __name__ == '__main__':

    app.run(debug=True)
