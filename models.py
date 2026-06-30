# models.py — Define a estrutura dos dados do sistema.

def criar_paciente(id, nome, data_nascimento, cpf, convenio, telefone):
    return {"id": id, "nome": nome, "data_nascimento": data_nascimento,
            "cpf": cpf, "convenio": convenio, "telefone": telefone}

def criar_profissional(id, nome, especialidade, crm):
    return {"id": id, "nome": nome, "especialidade": especialidade, "crm": crm}

def criar_consulta(id, paciente_id, profissional_id, data, tipo, valor,
                   status, procedimento=""):
    tipos_validos  = ["SUS", "Particular", "Convênio"]
    status_validos = ["realizada", "cancelada", "glosada"]
    if tipo not in tipos_validos:
        print(f"  Atenção: tipo '{tipo}' inválido. Use: {tipos_validos}")
    if status not in status_validos:
        print(f"  Atenção: status '{status}' inválido. Use: {status_validos}")
    return {"id": id, "paciente_id": paciente_id, "profissional_id": profissional_id,
            "data": data, "tipo": tipo, "procedimento": procedimento,
            "valor": float(valor), "status": status}

def criar_pagamento(id, consulta_id, data_pagamento, valor_pago, forma):
    return {"id": id, "consulta_id": consulta_id, "data_pagamento": data_pagamento,
            "valor_pago": float(valor_pago), "forma": forma}
