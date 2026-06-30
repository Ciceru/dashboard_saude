# main.py — Ponto de entrada. Execute: python main.py

from services import (cadastrar_paciente, listar_pacientes, buscar_paciente,
                      cadastrar_profissional, listar_profissionais, buscar_profissional,
                      cadastrar_consulta, listar_consultas, cancelar_consulta,
                      cadastrar_pagamento, listar_pagamentos)
from dashboard import (exibir_dashboard, gerar_json,
                       exibir_tabela_consultas, exibir_tabela_pacientes)
from usuarios import autenticar, menu_usuarios

def _cab(t): print(f"\n{'═'*52}\n  {t}\n{'═'*52}")
def _pausar(): input("\n  Pressione Enter para voltar ao menu...")

# ── Login ──
def tela_login():
    for tentativa in range(3):
        _cab("SISTEMA DE GESTÃO EM SAÚDE — LOGIN")
        login = input("  Login: ").strip()
        senha = input("  Senha: ").strip()
        print()
        u = autenticar(login, senha)
        if u:
            print(f"  Bem-vindo(a), {u['nome']}!  |  Perfil: {u['perfil']}")
            return u
        restantes = 2 - tentativa
        if restantes > 0:
            print(f"  Login ou senha incorretos. {restantes} tentativa(s) restante(s).")
        else:
            print("  Número máximo de tentativas atingido.")
            raise SystemExit
    return None

# ── Pacientes ──
def menu_pacientes():
    while True:
        _cab("PACIENTES")
        print("  1. Cadastrar\n  2. Listar todos\n  3. Filtrar por convênio"
              "\n  4. Buscar por nome ou ID\n  0. Voltar")
        op = input("\n  Escolha: ").strip()
        if op == "1":
            _cab("CADASTRAR PACIENTE")
            nome  = input("  Nome completo: ").strip()
            nasc  = input("  Data nascimento (AAAA-MM-DD): ").strip()
            cpf   = input("  CPF: ").strip()
            print("  Convênio: 1-SUS  2-Particular  3-Convênio")
            conv  = {"1":"SUS","2":"Particular","3":"Convênio"}.get(input("  Escolha: ").strip(),"SUS")
            tel   = input("  Telefone: ").strip()
            print(); cadastrar_paciente(nome, nasc, cpf, conv, tel); _pausar()
        elif op == "2":
            _cab("TODOS OS PACIENTES")
            exibir_tabela_pacientes(listar_pacientes()); _pausar()
        elif op == "3":
            _cab("FILTRAR POR CONVÊNIO")
            print("  1-SUS  2-Particular  3-Convênio")
            conv = {"1":"SUS","2":"Particular","3":"Convênio"}.get(input("  Escolha: ").strip())
            if conv: exibir_tabela_pacientes(listar_pacientes(convenio=conv))
            _pausar()
        elif op == "4":
            _cab("BUSCAR PACIENTE")
            res = buscar_paciente(input("  Nome ou ID: ").strip())
            print(f"\n  {len(res)} resultado(s):")
            exibir_tabela_pacientes(res); _pausar()
        elif op == "0": break

# ── Profissionais ──
def menu_profissionais():
    while True:
        _cab("PROFISSIONAIS")
        print("  1. Cadastrar\n  2. Listar todos\n  3. Buscar\n  0. Voltar")
        op = input("\n  Escolha: ").strip()
        if op == "1":
            _cab("CADASTRAR PROFISSIONAL")
            nome = input("  Nome: ").strip()
            esp  = input("  Especialidade: ").strip()
            crm  = input("  CRM: ").strip()
            print(); cadastrar_profissional(nome, esp, crm); _pausar()
        elif op == "2":
            _cab("TODOS OS PROFISSIONAIS")
            profs = listar_profissionais()
            if not profs: print("  Nenhum profissional.")
            else:
                print(f"\n  {'ID':>4}  {'Nome':<26}  {'Especialidade':<24}  CRM")
                print("  " + "─"*64)
                for p in profs:
                    print(f"  {p['id']:>4}  {p['nome']:<26}  {p['especialidade']:<24}  {p['crm']}")
            _pausar()
        elif op == "3":
            _cab("BUSCAR PROFISSIONAL")
            res = buscar_profissional(input("  Nome ou ID: ").strip())
            print(f"\n  {len(res)} resultado(s):")
            for p in res: print(f"  → ID {p['id']}: {p['nome']} | {p['especialidade']}")
            _pausar()
        elif op == "0": break

# ── Consultas ──
def menu_consultas():
    while True:
        _cab("CONSULTAS")
        print("  1. Cadastrar\n  2. Listar todas\n  3. Filtrar por tipo"
              "\n  4. Filtrar por status\n  5. Filtrar por mês/ano"
              "\n  6. Cancelar consulta\n  0. Voltar")
        op = input("\n  Escolha: ").strip()
        if op == "1":
            _cab("CADASTRAR CONSULTA")
            try:
                pac_id  = int(input("  ID do paciente: ").strip())
                prof_id = int(input("  ID do profissional: ").strip())
            except ValueError:
                print("  ID inválido."); _pausar(); continue
            data = input("  Data (AAAA-MM-DD): ").strip()
            print("  Tipo: 1-SUS  2-Particular  3-Convênio")
            tipo = {"1":"SUS","2":"Particular","3":"Convênio"}.get(input("  Escolha: ").strip(),"SUS")
            proc = input("  Procedimento: ").strip()
            try: valor = float(input("  Valor: ").strip())
            except ValueError: valor = 0.0
            print(); cadastrar_consulta(pac_id, prof_id, data, tipo, valor, procedimento=proc)
            _pausar()
        elif op == "2":
            _cab("TODAS AS CONSULTAS")
            exibir_tabela_consultas(listar_consultas()); _pausar()
        elif op == "3":
            _cab("FILTRAR POR TIPO")
            print("  1-SUS  2-Particular  3-Convênio")
            tipo = {"1":"SUS","2":"Particular","3":"Convênio"}.get(input("  Escolha: ").strip())
            if tipo: exibir_tabela_consultas(listar_consultas(tipo=tipo))
            _pausar()
        elif op == "4":
            _cab("FILTRAR POR STATUS")
            print("  1-Realizada  2-Cancelada  3-Glosada")
            st = {"1":"realizada","2":"cancelada","3":"glosada"}.get(input("  Escolha: ").strip())
            if st: exibir_tabela_consultas(listar_consultas(status=st))
            _pausar()
        elif op == "5":
            _cab("FILTRAR POR MÊS/ANO")
            mes = input("  Mês (01-12): ").strip()
            ano = input("  Ano (ex: 2024): ").strip()
            exibir_tabela_consultas(listar_consultas(mes=mes, ano=ano)); _pausar()
        elif op == "6":
            _cab("CANCELAR CONSULTA")
            try: cancelar_consulta(int(input("  ID da consulta: ").strip()))
            except ValueError: print("  ID inválido.")
            _pausar()
        elif op == "0": break

# ── Pagamentos ──
def menu_pagamentos():
    while True:
        _cab("PAGAMENTOS")
        print("  1. Registrar\n  2. Listar\n  0. Voltar")
        op = input("\n  Escolha: ").strip()
        if op == "1":
            _cab("REGISTRAR PAGAMENTO")
            try:
                cid   = int(input("  ID da consulta: ").strip())
                valor = float(input("  Valor pago: ").strip())
            except ValueError:
                print("  Valor inválido."); _pausar(); continue
            data  = input("  Data (AAAA-MM-DD): ").strip()
            print("  Forma: 1-Dinheiro  2-PIX  3-Cartão  4-Convênio  5-SUS")
            forma = {"1":"dinheiro","2":"pix","3":"cartão","4":"convênio","5":"SUS"}.get(
                        input("  Escolha: ").strip(),"dinheiro")
            print(); cadastrar_pagamento(cid, data, valor, forma); _pausar()
        elif op == "2":
            _cab("LISTA DE PAGAMENTOS")
            pags = listar_pagamentos()
            if not pags: print("  Nenhum pagamento.")
            else:
                print(f"\n  {'ID':>4}  {'Consulta':>8}  {'Data':<12}  {'Valor':>10}  Forma")
                print("  " + "─"*52)
                for p in pags:
                    print(f"  {p['id']:>4}  {p['consulta_id']:>8}  "
                          f"{p['data_pagamento']:<12}  "
                          f"R$ {float(p['valor_pago']):>7.2f}  {p['forma']}")
            _pausar()
        elif op == "0": break

# ── Menu principal ──
def main():
    usuario = tela_login()
    while True:
        _cab(f"MENU PRINCIPAL  [{usuario['login']} • {usuario['perfil']}]")
        print("  1. Pacientes\n  2. Profissionais\n  3. Consultas\n  4. Pagamentos"
              "\n  5. Ver Dashboard\n  6. Exportar dados (gera JSON para front-end)"
              "\n  7. Gerenciar usuários\n  0. Sair")
        op = input("\n  Escolha: ").strip()
        if   op == "1": menu_pacientes()
        elif op == "2": menu_profissionais()
        elif op == "3": menu_consultas()
        elif op == "4": menu_pagamentos()
        elif op == "5": exibir_dashboard(); _pausar()
        elif op == "6": print(); gerar_json(); _pausar()
        elif op == "7": menu_usuarios(usuario)
        elif op == "0":
            print(f"\n  Até logo, {usuario['nome']}!\n"); break
        else:
            print("\n  Opção inválida."); _pausar()

if __name__ == "__main__":
    main()
