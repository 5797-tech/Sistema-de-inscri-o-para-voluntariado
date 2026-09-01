"""
Módulo 2 — Listagem, Pesquisa e Ordenação
Sistema de Inscrição e Gestão de Voluntariado

Este módulo opera sobre a lista de voluntários criada no Módulo 1
(estrutura em memória partilhada).
"""

from modulo1_dados import voluntarios


# ---------------------------------------------------------
# Listagem
# ---------------------------------------------------------
def listar_voluntarios():
    """Devolve a lista completa de voluntários guardados em memória."""
    return voluntarios


def imprimir_lista(lista):
    """Apresenta uma lista de voluntários de forma organizada."""
    if not lista:
        print("Não existem voluntários para apresentar.")
        return

    print(f"{'ID':<8}{'Nome':<20}{'Email':<25}{'Telefone':<12}{'Ativo':<6}")
    print("-" * 71)
    for v in lista:
        print(f"{v.idVoluntario:<8}{v.nome:<20}{v.email:<25}{v.telefone:<12}{str(v.ativo):<6}")


# ---------------------------------------------------------
# Pesquisa
# ---------------------------------------------------------
def pesquisar_voluntario(criterio, valor):
    """
    Pesquisa voluntários por um critério (campo) e um valor.
    criterio pode ser: 'idVoluntario', 'nome', 'email', 'telefone'
    A pesquisa por nome/email é parcial e não sensível a maiúsculas/minúsculas.
    Devolve uma lista de resultados (pode estar vazia).
    """
    if not hasattr(voluntarios[0], criterio) if voluntarios else False:
        pass  # validação suave — feita abaixo por campo

    resultados = []
    valor_lower = str(valor).strip().lower()

    for v in voluntarios:
        campo = getattr(v, criterio, None)
        if campo is None:
            continue
        if valor_lower in str(campo).strip().lower():
            resultados.append(v)

    return resultados


# ---------------------------------------------------------
# Ordenação
# ---------------------------------------------------------
def ordenar_voluntarios(campo="nome", decrescente=False):
    """
    Devolve uma NOVA lista de voluntários ordenada pelo campo indicado.
    campo pode ser: 'idVoluntario', 'nome', 'email', 'telefone', 'dataRegisto'
    """
    try:
        return sorted(voluntarios, key=lambda v: getattr(v, campo), reverse=decrescente)
    except AttributeError:
        print(f"[ERRO] O campo '{campo}' não existe na estrutura Voluntário.")
        return []
