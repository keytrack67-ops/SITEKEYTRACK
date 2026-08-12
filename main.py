import os
import sqlite3
import time
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="KeyTrack API",
    description="API para gestão de chaves, salas e acesso",
    version="1.0.0"
)

# --- CONFIGURAÇÃO DE ACESSO (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def conectar_banco():
    conn = sqlite3.connect(
        'KTLiteDefinitivoV2.db',
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Tabela de Docentes/Colaboradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Docentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            cargo TEXT,
            senha TEXT
        )
    ''')
    
    # Tabela de salas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            status TEXT
        )
    ''')
    
    # Tabela de reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala TEXT,
            professor TEXT,
            data TEXT
        )
    ''')
    
    # Insere o usuário Administrador padrão inicial de forma segura
    cursor.execute("SELECT * FROM Docentes WHERE nome = 'Audice'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO Docentes (nome, cargo, senha) VALUES ('Audice', 'Administrador', 'audice123')")
        
    conn.commit()
    conn.close()

criar_tabelas()

# --- ROTAS DA APLICAÇÃO ---

@app.get("/")
def home():
    return {"status": "sucesso", "mensagem": "API KeyTrack rodando perfeitamente!"}

@app.get("/salas")
def listar_salas():
    conn = conectar_banco()
    cursor = conn.cursor()
    salas = cursor.execute("SELECT * FROM salas").fetchall()
    conn.close()
    return [dict(s) for s in salas]

@app.post("/confirmar-reserva")
def confirmar_reserva(sala: str = Form(...), professor: str = Form(...), data: str = Form(...)):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reservas (sala, professor, data) VALUES (?, ?, ?)", 
                   (sala, professor, data))
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": f"Reserva salva no banco: {sala} para {professor}"}

@app.delete("/cancelar-reserva/{id}")
def cancelar_reserva(id: int):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": "Reserva cancelada com sucesso!"}

@app.post("/cadastrar-colaborador")
def cadastrar_colaborador(
    nome: str = Form(...),
    id_re: str = Form(...),
    cargo: str = Form(...)
):
    senha_pin = id_re.strip()

    if len(senha_pin) != 6:
        return {
            "status": "erro",
            "mensagem": f"A senha/PIN deve conter exatamente 6 dígitos! Você digitou {len(senha_pin)}."
        }

    conn = None
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Docentes (nome, cargo, senha)
            VALUES (?, ?, ?)
        """, (nome, cargo, senha_pin))

        conn.commit()
        return {
            "status": "sucesso",
            "mensagem": f"Colaborador {nome} cadastrado com sucesso!"
        }
    except sqlite3.IntegrityError:
        return {
            "status": "erro",
            "mensagem": "Este nome já está cadastrado no sistema."
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": str(e)
        }
    finally:
        if conn:
            conn.close()

@app.get("/listar-reservas")
def listar_reservas():
    conn = conectar_banco()
    cursor = conn.cursor()
    reservas = cursor.execute("SELECT * FROM reservas").fetchall()
    conn.close()
    return [dict(r) for r in reservas]

@app.get("/listar-professores")
def listar_professores():
    conn = conectar_banco()
    cursor = conn.cursor()
    professores = cursor.execute("SELECT * FROM Docentes").fetchall()
    conn.close()
    return [dict(p) for p in professores]

@app.post("/login")
def login(nome: str = Form(...), senha: str = Form(...)):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM Docentes WHERE nome = ? AND senha = ?", 
        (nome.strip(), senha.strip())
    )
    professor = cursor.fetchone()
    conn.close()
    
    if professor:
        professor_dict = dict(professor)
        return { 
            "status": "sucesso", 
            "mensagem": f"Bem-vindo, {professor_dict['nome']}!",      
            "nome": professor_dict['nome']
        }
    else:
        return {"status": "erro", "mensagem": "Nome ou Senha/PIN incorretos!"}

@app.post("/login-adm")
def login_adm(usuario: str = Form(...), senha: str = Form(...)):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM Docentes WHERE nome = ? AND senha = ? AND cargo = 'Administrador'", 
        (usuario.strip(), senha.strip())
    )
    admin = cursor.fetchone()
    conn.close()
    
    if admin:
        admin_dict = dict(admin)
        return { 
            "status": "sucesso", 
            "mensagem": f"Acesso Administrativo concedido! Bem-vindo, {admin_dict['nome']}.",
            "nome": admin_dict['nome']
        }
    else:
        return {"status": "erro", "mensagem": "Usuário ou senha de administrador incorretos!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)