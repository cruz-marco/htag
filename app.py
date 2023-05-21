"""
Candidato: Marco Antônio da Silva Cruz
E-mail: marco_cruz@hotmail.com.br

LinkedIn: https://www.linkedin.com/in/cruz-marco-rj/
GitHub: https://github.com/cruz-marco
Kaggle: https://www.kaggle.com/abakashi

Estou criando a api pedida da forma mais 'simples' usando apenas 
flask e o sqlite3 como solicitado.

"""

#Importando as bibliotecas necessárias
from flask import Flask, request, render_template
import sqlite3

DBPATH = './database.db' #caminho e nome do banco de dados
TOKEN = 'uhdfaAADF123'

#Criando o banco de dados.
conn = sqlite3.connect(DBPATH)
cursor = conn.cursor()

#Cria as tabelas para o banco de dados, caso não existam.
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nome TEXT,
                  email TEXT,
                  status TEXT,
                  valor INTEGER,
                  forma_pagamento TEXT,
                  parcelas INTEGER,
                  acesso TEXT)                  
                  ''')
cursor.execute('''CREATE TABLE IF NOT EXISTS admins
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nome TEXT,
                  email TEXT,                  
                  senha TEXT)''')

conn.commit()
conn.close()


def db_write(values, fields, table='usuarios'):
    """
    Função que escreve os dados no banco de dados.
    values: Recebe um array-like com os valores a serem escritos.
    fields: Recebe um array-like com os nomes dos campos a serem preenchidos.
    table: tabela a ser utilizada, valor padrão: usuarios.
    """
    conn = sqlite3.connect(DBPATH)
    cursor = conn.cursor()
    cursor.execute(f'''INSERT INTO {table} ({", ".join(fields)})
                     VALUES({("?, "*len(fields))[:-2]})''', (tuple(values)))
    
    conn.commit()
    conn.close()


app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_request():
    """
    Função que vai receber, registrar e analisar os dados recebidos
    pelo webhook.
    """    

    #pega os dados da requisição
    request_data = request.get_json(force=True)
    treat={
        'aprovado' : 'liberado',
        'recusado' : 'bloqueado',
        'reembolsado' : 'revogado'
    }

    #tratativa
    request_data['acesso'] = treat[request_data['status']]
    
    #registra as informações no banco de dados
    db_write(request_data.values(), tuple(request_data.keys()))
    
    returns = {
        'aprovado' : f"Acesso Liberado! Bem vindo {request_data['email']}.",
        'recusado' : 'Pagamento recusado.',
        'reembolsado': 'Acesso ao curso revogado.'
    }
    #retorna a mensagem no corpo da requisição.
    return returns[request_data['status']]

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    """
    Função principal de login no sistema:
    """
    if request.method == 'POST':
        # Obter os dados do formulário de login
        email = request.form['email']
        password = request.form['password']
        qemail = str(request.form['query_email'])
        
        # Realizar a pesquisa no banco de dados
        conn = sqlite3.connect(DBPATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE email=? AND senha=?', (email, password))
        logon = cursor.fetchone()        
        
        #Se houver algo na variável logon:
        if logon:  
            #Verifica se há uma pesquisa por e-mail específico registrada
            if qemail:                
                cursor.execute('SELECT * FROM usuarios WHERE email=?', (qemail,))
                registers = cursor.fetchall()[::-1]
                if registers:
                    #caso haja uma ocorrência retorna ela no corpo do html
                    return render_template('registers.html', registers=registers)
                else:
                    #Caso não haja, retorna a mensagem de erro.
                    return render_template('registers.html', error='Sem resultados!')
            else:
                #Caso não haja um e-mail a ser buscado, retorna todos os webhooks
                cursor.execute('SELECT * FROM usuarios')
                registers = cursor.fetchall()[::-1]
                return render_template('registers.html', registers=registers)          
        else:
            # Se o resultado não for encontrado, exibir uma mensagem de erro na página de login
            return render_template('admin.html', error='Usuário ou senha inválidos.')
        conn.close()
    else:
        # Se for uma requisição GET, exibir o formulário de login
        return render_template('admin.html')




@app.route('/admin_cadastro', methods=['POST', 'GET'])
def cadastro():
    """
    Função que gera o cadastro de administradores
    mediante o fornecimento do token correto.
    """
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        token = request.form['token']

        conn = sqlite3.connect(DBPATH)
        cursor = conn.cursor()
        if token == TOKEN:
            cursor.execute("""INSERT INTO admins (nome, email, senha)
            VALUES(?, ?, ?)
            """, (nome, email, senha))
            conn.commit()
            conn.close()
            return render_template('cadastro.html', conf='Cadastrado com sucesso!')
        else:
            return render_template('cadastro.html', conf='Token inválido')
    else:
        return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

