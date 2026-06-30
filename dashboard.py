from datetime import datetime

def formatar_moeda(valor: float) -> str:
    """Formata um valor float para o padrão monetário brasileiro (R$ X.XXX,XX)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor: float) -> str:
    """Formata um valor float para o padrão percentual brasileiro (X,XX%)."""
    return f"{valor:.2f}%".replace(".", ",")

def formatar_data(data_str: str, formato_saida: str = "%d/%m/%Y") -> str:
    """
    Formata uma string de data (ISO ou YYYY-MM) para o padrão brasileiro.
    Tenta parsear vários formatos comuns.
    """
    if not data_str:
        return ""

    dt_obj = None
    # Tenta parsear como YYYY-MM-DDTHH:MM:SS (ISO datetime)
    try:
        dt_obj = datetime.fromisoformat(data_str)
    except ValueError:
        pass

    # Tenta parsear como YYYY-MM-DD (ISO date)
    if dt_obj is None:
        try:
            dt_obj = datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError:
            pass

    # Tenta parsear como YYYY-MM (mês/ano)
    if dt_obj is None:
        try:
            dt_obj = datetime.strptime(data_str, "%Y-%m")
        except ValueError:
            pass

    if dt_obj:
        return dt_obj.strftime(formato_saida)
    else:
        return data_str # Retorna a string original se não conseguir parsear
