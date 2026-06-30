# usuarios.py — Autenticação e gerenciamento de usuários.

import hashlib, csv, os

_BASE            = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_USUARIOS = os.path.join(_BASE, "dados", "usuarios.csv")
COLUNAS          = ["id","login","nome","senha_hash","perfil"]
PERFIS_VALIDOS   = ["admin","gestor","operador"]

def _hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _carregar():
    if not os.path.exists(ARQUIVO_USUARIOS):
        return []
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            return [dict(r) for r in csv.DictReader(f)]
    except Exception as e:
        print(f"  Erro ao ler usuários: {e}")
        return []

def _salvar(lista):
    os.makedirs(os.path.dirname(ARQUIVO_USUARIOS), exist_ok=True)
    try:
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore")
            w.writeheader()
            w.writerows(lista)
    except Exception as e:
        print(f"  Erro ao salvar usuários: {e}")

def _proximo_id(lista):
    return max((int(u["id"]) for u in lista), default=0) + 1

def autenticar(login, senha):
    h = _hash(senha.strip())
    for u in _carregar():
        if u["login"].strip().lower() == login.strip().lower():
            return u if u["senha_hash"].strip() == h else None
    return None

def cadastrar_usuario(login, nome, senha, perfil):
    if perfil not in PERFIS_VALIDOS:
        print(f"  Perfil inválido. Use: {PERFIS_VALIDOS}"); return None
    if len(senha) < 6:
        print("  Senha deve ter no mínimo 6 caracteres."); return None
    usuarios = _carregar()
    if any(u["login"].lower() == login.lower() for u in usuarios):
        print(f"  Login '{login}' já existe."); return None
    novo = {"id": _proximo_id(usuarios), "login": login.lower(),
            "nome": nome, "senha_hash": _hash(senha), "perfil": perfil}
    usuarios.append(novo)
    _salvar(usuarios)
    print(f"  Usuário '{login}' criado (perfil: {perfil}).")
    return novo

def listar_usuarios():
    return [{k:v for k,v in u.items() if k != "senha_hash"} for u in _carregar()]

def alterar_senha(login, senha_atual, nova_senha):
    usuarios = _carregar()
    for u in usuarios:
        if u["login"].lower() == login.lower():
            if u["senha_hash"] != _hash(senha_atual):
                print("  Senha atual incorreta."); return False
            if len(nova_senha) < 6:
                print("  Nova senha muito curta."); return False
            if senha_atual == nova_senha:
                print("  Nova senha igual à atual."); return False
            u["senha_hash"] = _hash(nova_senha)
            _salvar(usuarios)
            print("  Senha alterada com sucesso.")
            return True
    print(f"  Usuário '{login}' não encontrado."); return False

def redefinir_senha_admin(login, nova_senha):
    if len(nova_senha) < 6:
        print("  Senha muito curta."); return False
    usuarios = _carregar()
    for u in usuarios:
        if u["login"].lower() == login.lower():
            u["senha_hash"] = _hash(nova_senha)
            _salvar(usuarios)
            print(f"  Senha de '{login}' redefinida.")
            return True
    print(f"  Usuário '{login}' não encontrado."); return False

def alterar_perfil(login, novo_perfil):
    if novo_perfil not in PERFIS_VALIDOS:
        print(f"  Perfil inválido. Use: {PERFIS_VALIDOS}"); return False
    usuarios = _carregar()
    for u in usuarios:
        if u["login"].lower() == login.lower():
            ant = u["perfil"]; u["perfil"] = novo_perfil
            _salvar(usuarios)
            print(f"  Perfil de '{login}': {ant} → {novo_perfil}.")
            return True
    print(f"  Usuário '{login}' não encontrado."); return False

def remover_usuario(login, solicitante):
    if login.lower() == solicitante.lower():
        print("  Você não pode remover seu próprio usuário."); return False
    usuarios = _carregar()
    alvo = next((u for u in usuarios if u["login"].lower() == login.lower()), None)
    if not alvo:
        print(f"  Usuário '{login}' não encontrado."); return False
    if alvo["perfil"] == "admin" and sum(1 for u in usuarios if u["perfil"]=="admin") <= 1:
        print("  Não é possível remover o único administrador."); return False
    _salvar([u for u in usuarios if u["login"].lower() != login.lower()])
    print(f"  Usuário '{login}' removido.")
    return True

# ── Menu ──
def _ln(n=50): print("  " + "─"*n)
def _pausar(): input("  Pressione Enter para continuar...")

def _tabela(usuarios):
    if not usuarios: print("  Nenhum usuário."); return
    print(f"\n  {'ID':>4}  {'Login':<14}  {'Nome':<26}  Perfil")
    _ln()
    for u in usuarios:
        print(f"  {u['id']:>4}  {u['login']:<14}  {u['nome']:<26}  {u['perfil']}")
    _ln(); print(f"  Total: {len(usuarios)}\n")

def menu_usuarios(usuario_logado):
    admin = usuario_logado["perfil"] == "admin"
    while True:
        print("\n  " + "═"*50)
        print("  GERENCIAMENTO DE USUÁRIOS")
        print("  " + "═"*50)
        print("  1. Listar usuários")
        if admin:
            print("  2. Cadastrar novo usuário")
            print("  3. Alterar perfil")
            print("  4. Redefinir senha de usuário")
            print("  5. Remover usuário")
        print("  6. Alterar minha senha")
        print("  0. Voltar")
        op = input("\n  Escolha: ").strip()

        if op == "1":
            _tabela(listar_usuarios()); _pausar()

        elif op == "2" and admin:
            print("\n  CADASTRAR USUÁRIO"); _ln()
            login  = input("  Login: ").strip()
            nome   = input("  Nome completo: ").strip()
            senha  = input("  Senha (mín. 6 caracteres): ").strip()
            print("  Perfil: 1-admin  2-gestor  3-operador")
            perfil = {"1":"admin","2":"gestor","3":"operador"}.get(
                         input("  Escolha: ").strip(), "operador")
            print(); cadastrar_usuario(login, nome, senha, perfil); _pausar()

        elif op == "3" and admin:
            print("\n  ALTERAR PERFIL"); _ln()
            _tabela(listar_usuarios())
            login  = input("  Login do usuário: ").strip()
            print("  Novo perfil: 1-admin  2-gestor  3-operador")
            perfil = {"1":"admin","2":"gestor","3":"operador"}.get(
                         input("  Escolha: ").strip())
            if perfil: alterar_perfil(login, perfil)
            _pausar()

        elif op == "4" and admin:
            print("\n  REDEFINIR SENHA"); _ln()
            _tabela(listar_usuarios())
            login = input("  Login do usuário: ").strip()
            nova  = input("  Nova senha: ").strip()
            print(); redefinir_senha_admin(login, nova); _pausar()

        elif op == "5" and admin:
            print("\n  REMOVER USUÁRIO"); _ln()
            _tabela(listar_usuarios())
            login = input("  Login a remover: ").strip()
            conf  = input(f"  Confirma remoção de '{login}'? (s/n): ").strip().lower()
            if conf == "s": remover_usuario(login, usuario_logado["login"])
            else: print("  Cancelado.")
            _pausar()

        elif op == "6":
            print("\n  ALTERAR MINHA SENHA"); _ln()
            atual    = input("  Senha atual: ").strip()
            nova     = input("  Nova senha: ").strip()
            confirma = input("  Confirme: ").strip()
            print()
            if nova != confirma: print("  Senhas não coincidem.")
            else: alterar_senha(usuario_logado["login"], atual, nova)
            _pausar()

        elif op == "0":
            break
