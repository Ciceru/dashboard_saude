from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Set
import pandas as pd # Importar pandas

# --- Definições de Dataclasses (Mantidas) ---
@dataclass
class Paciente:
    id: int
    nome: str
    data_nascimento: str # Armazenado como string ISO (YYYY-MM-DD)
    genero: str
    contato: str


@dataclass
class Profissional:
    id: int
    nome: str
    especialidade: str
    contato: str


@dataclass
class Consulta:
    id: int
    id_paciente: int
    id_profissional: int
    data_hora: str # Armazenado como string ISO (YYYY-MM-DDTHH:MM:SS)
    tipo_consulta: str
    status: str  # Agendada, Realizada, Cancelada, Glosada


@dataclass
class Pagamento:
    id: int
    id_consulta: int
    valor: float
    data_pagamento: str # Armazenado como string ISO (YYYY-MM-DD)
    status: str  # Pendente, Pago, Glosado, Estornado


# --- Variáveis Globais para Cache dos Dados ---
_df_dados_carregados: Optional[pd.DataFrame] = None
_pacientes_cache: Optional[List[Paciente]] = None
_profissionais_cache: Optional[List[Profissional]] = None
_consultas_cache: Optional[List[Consulta]] = None
_pagamentos_cache: Optional[List[Pagamento]] = None


# --- Função para Carregar Dados do CSV ---
def _carregar_dados_csv(caminho_arquivo: str = "dados_saude.csv"):
    global _df_dados_carregados, _pacientes_cache, _profissionais_cache, _consultas_cache, _pagamentos_cache

    if _df_dados_carregados is not None:
        return # Dados já carregados, evita recarregar a cada chamada

    try:
        df = pd.read_csv(caminho_arquivo)

        # Convertendo colunas de data para o tipo correto
        df['data_nascimento_paciente'] = pd.to_datetime(df['data_nascimento_paciente']).dt.date
        df['data_hora_consulta'] = pd.to_datetime(df['data_hora_consulta'])
        df['data_pagamento'] = pd.to_datetime(df['data_pagamento']).dt.date

        _df_dados_carregados = df

        # Popular caches de dataclasses a partir do DataFrame
        pacientes_map: Dict[int, Paciente] = {}
        profissionais_map: Dict[int, Profissional] = {}
        consultas_map: Dict[int, Consulta] = {}
        pagamentos_list: List[Pagamento] = []

        for _, row in df.iterrows():
            # Pacientes (garante unicidade pelo ID)
            if row['id_paciente'] not in pacientes_map:
                pacientes_map[row['id_paciente']] = Paciente(
                    id=row['id_paciente'],
                    nome=row['nome_paciente'],
                    data_nascimento=row['data_nascimento_paciente'].isoformat(),
                    genero=row['genero_paciente'],
                    contato=row['contato_paciente']
                )
            # Profissionais (garante unicidade pelo ID)
            if row['id_profissional'] not in profissionais_map:
                profissionais_map[row['id_profissional']] = Profissional(
                    id=row['id_profissional'],
                    nome=row['nome_profissional'],
                    especialidade=row['especialidade_profissional'],
                    contato=row['contato_profissional']
                )
            # Consultas (garante unicidade pelo ID)
            if row['id_consulta'] not in consultas_map:
                consultas_map[row['id_consulta']] = Consulta(
                    id=row['id_consulta'],
                    id_paciente=row['id_paciente'],
                    id_profissional=row['id_profissional'],
                    data_hora=row['data_hora_consulta'].isoformat(),
                    tipo_consulta=row['tipo_consulta'],
                    status=row['status_consulta']
                )
            # Pagamentos (pode haver múltiplos pagamentos para uma consulta, ou um por linha)
            pagamentos_list.append(Pagamento(
                id=row['id_pagamento'],
                id_consulta=row['id_consulta'],
                valor=row['valor_pagamento'],
                data_pagamento=row['data_pagamento'].isoformat(),
                status=row['status_pagamento']
            ))

        _pacientes_cache = list(pacientes_map.values())
        _profissionais_cache = list(profissionais_map.values())
        _consultas_cache = list(consultas_map.values())
        _pagamentos_cache = pagamentos_list

    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado. Usando dados mock.")
        _carregar_dados_mock() # Fallback para dados mock
    except Exception as e:
        print(f"Erro ao carregar dados do CSV: {e}. Usando dados mock.")
        _carregar_dados_mock() # Fallback para dados mock


# --- Funções de Simulação de Dados (Mock Data) - Renomeadas e Centralizadas ---
# Estas funções são usadas APENAS se o CSV não for encontrado ou houver erro.
def _carregar_dados_mock():
    global _pacientes_cache, _profissionais_cache, _consultas_cache, _pagamentos_cache

    _pacientes_cache = [
        Paciente(1, "Ana Silva", "1990-05-15", "Feminino", "ana.s@email.com"),
        Paciente(2, "Bruno Costa", "1985-11-22", "Masculino", "bruno.c@email.com"),
        Paciente(3, "Carla Dias", "1992-03-01", "Feminino", "carla.d@email.com"),
        Paciente(4, "Daniel Rocha", "1978-07-10", "Masculino", "daniel.r@email.com"),
    ]

    _profissionais_cache = [
        Profissional(101, "Dr. João Santos", "Clínico Geral", "joao.s@email.com"),
        Profissional(102, "Dra. Maria Lima", "Pediatra", "maria.l@email.com"),
        Profissional(103, "Dr. Pedro Alves", "Cardiologista", "pedro.a@email.com"),
    ]

    _consultas_cache = [
        Consulta(1001, 1, 101, "2026-01-10T10:00:00", "Rotina", "Realizada"),
        Consulta(1002, 2, 102, "2026-01-10T11:00:00", "Pediátrica", "Realizada"),
        Consulta(1003, 3, 101, "2026-01-11T14:00:00", "Rotina", "Agendada"),
        Consulta(1004, 4, 103, "2026-01-11T15:00:00", "Cardiologia", "Cancelada"),
        Consulta(1005, 1, 102, "2026-02-05T09:00:00", "Pediátrica", "Realizada"),
        Consulta(1006, 2, 101, "2026-02-05T10:00:00", "Rotina", "Realizada"),
        Consulta(1007, 3, 103, "2026-02-06T13:00:00", "Cardiologia", "Agendada"),
        Consulta(1008, 4, 101, "2026-02-06T14:00:00", "Rotina", "Realizada"),
        Consulta(1009, 1, 101, "2026-03-01T10:00:00", "Rotina", "Realizada"),
        Consulta(1010, 2, 102, "2026-03-01T11:00:00", "Pediátrica", "Realizada"),
        Consulta(1011, 3, 101, "2026-03-02T14:00:00", "Rotina", "Agendada"),
        Consulta(1012, 4, 103, "2026-03-02T15:00:00", "Cardiologia", "Cancelada"),
        Consulta(1013, 1, 102, "2026-04-05T09:00:00", "Pediátrica", "Realizada"),
        Consulta(1014, 2, 101, "2026-04-05T10:00:00", "Rotina", "Realizada"),
        Consulta(1015, 3, 103, "2026-04-06T13:00:00", "Cardiologia", "Agendada"),
        Consulta(1016, 4, 101, "2026-04-06T14:00:00", "Rotina", "Realizada"),
        Consulta(1017, 1, 101, "2026-05-10T10:00:00", "Rotina", "Realizada"),
        Consulta(1018, 2, 102, "2026-05-10T11:00:00", "Pediátrica", "Realizada"),
        Consulta(1019, 3, 101, "2026-05-11T14:00:00", "Rotina", "Agendada"),
        Consulta(1020, 4, 103, "2026-05-11T15:00:00", "Cardiologia", "Cancelada"),
        Consulta(1021, 1, 102, "2026-06-05T09:00:00", "Pediátrica", "Realizada"),
        Consulta(1022, 2, 101, "2026-06-05T10:00:00", "Rotina", "Realizada"),
        Consulta(1023, 3, 103, "2026-06-06T13:00:00", "Cardiologia", "Agendada"),
        Consulta(1024, 4, 101, "2026-06-06T14:00:00", "Rotina", "Realizada"),
    ]

    _pagamentos_cache = [
        Pagamento(2001, 1001, 150.00, "2026-01-10", "Pago"),
        Pagamento(2002, 1002, 200.00, "2026-01-10", "Pago"),
        Pagamento(2003, 1003, 150.00, "2026-01-11", "Pendente"),
        Pagamento(2004, 1004, 250.00, "2026-01-11", "Glosado"),
        Pagamento(2005, 1005, 200.00, "2026-02-05", "Pago"),
        Pagamento(2006, 1006, 150.00, "2026-02-05", "Pago"),
        Pagamento(2007, 1007, 250.00, "2026-02-06", "Pendente"),
        Pagamento(2008, 1008, 150.00, "2026-02-06", "Pago"),
        Pagamento(2009, 1009, 150.00, "2026-03-01", "Pago"),
        Pagamento(2010, 1010, 200.00, "2026-03-01", "Pago"),
        Pagamento(2011, 1011, 150.00, "2026-03-02", "Pendente"),
        Pagamento(2012, 1012, 250.00, "2026-03-02", "Glosado"),
        Pagamento(2013, 1013, 200.00, "2026-04-05", "Pago"),
        Pagamento(2014, 1014, 150.00, "2026-04-05", "Pago"),
        Pagamento(2015, 1015, 250.00, "2026-04-06", "Pendente"),
        Pagamento(2016, 1016, 150.00, "2026-04-06", "Pago"),
        Pagamento(2017, 1017, 150.00, "2026-05-10", "Pago"),
        Pagamento(2018, 1018, 200.00, "2026-05-10", "Pago"),
        Pagamento(2019, 1019, 150.00, "2026-05-11", "Pendente"),
        Pagamento(2020, 1020, 250.00, "2026-05-11", "Glosado"),
        Pagamento(2021, 1021, 200.00, "2026-06-05", "Pago"),
        Pagamento(2022, 1022, 150.00, "2026-06-05", "Pago"),
        Pagamento(2023, 1023, 250.00, "2026-06-06", "Pendente"),
        Pagamento(2024, 1024, 150.00, "2026-06-06", "Pago"),
    ]


# --- Funções Públicas que Usam o Cache ---
def listar_pacientes() -> List[Paciente]:
    _carregar_dados_csv()
    return _pacientes_cache


def listar_profissionais() -> List[Profissional]:
    _carregar_dados_csv()
    return _profissionais_cache


def listar_consultas() -> List[Consulta]:
    _carregar_dados_csv()
    return _consultas_cache


def listar_pagamentos() -> List[Pagamento]:
    _carregar_dados_csv()
    return _pagamentos_cache


def tentar_parsear_data(data_str: str) -> Optional[datetime]:
    """Tenta parsear uma string de data/hora em vários formatos."""
    formatos = [
        "%Y-%m-%dT%H:%M:%S",  # Formato ISO de datetime
        "%Y-%m-%d",           # Formato ISO de data
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    return None


def get_min_max_dates() -> Tuple[Optional[date], Optional[date]]:
    """
    Retorna a data mínima e máxima encontradas nos dados de consultas e pagamentos.
    """
    _carregar_dados_csv() # Garante que os dados estejam carregados

    todas_as_datas: List[date] = []

    for consulta in _consultas_cache:
        # A data_hora já está em formato ISO, tentar_parsear_data pode lidar com isso
        data_dt = tentar_parsear_data(consulta.data_hora)
        if data_dt:
            todas_as_datas.append(data_dt.date())

    for pagamento in _pagamentos_cache:
        # A data_pagamento já está em formato ISO
        data_dt = tentar_parsear_data(pagamento.data_pagamento)
        if data_dt:
            todas_as_datas.append(data_dt.date())

    if not todas_as_datas:
        return None, None

    min_date = min(todas_as_datas)
    max_date = max(todas_as_datas)

    return min_date, max_date
