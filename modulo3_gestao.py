"""
Módulo 3 — Remover, Editar e Guardar em Ficheiro
Sistema de Inscrição e Gestão de Voluntariado
"""

import json

from modulo1_dados import voluntarios, validar_dados


# ---------------------------------------------------------
# Remover
# ---------------------------------------------------------
def remover_voluntario(idVoluntario):
    """
    Remove um voluntário da lista com base no ID.
    Devolve (True, "mensagem") ou (False, "mensagem de erro").
    """
    for v in voluntarios:
        if v.idVoluntario == idVoluntario:
            voluntarios.remove(v)
            return True, f"Voluntário {idVoluntario} removido com sucesso."

    return False, f"Não existe nenhum voluntário com o ID '{idVoluntario}'."


# ---------------------------------------------------------
# Editar
# ---------------------------------------------------------
def editar_voluntario(idVoluntario, nome=None, email=None, telefone=None):
    """
    Edita os dados de um voluntário existente.
    Apenas os campos fornecidos (não None) são alterados.
    Os novos dados são validados antes de serem guardados.
    Devolve (True, objeto_voluntario) ou (False, "mensagem de erro").
    """
    voluntario_encontrado = None
    for v in voluntarios:
        if v.idVoluntario == idVoluntario:
            voluntario_encontrado = v
            break

    if voluntario_encontrado is None:
        return False, f"Não existe nenhum voluntário com o ID '{idVoluntario}'."

    novo_nome = nome if nome is not None else voluntario_encontrado.nome
    novo_email = email if email is not None else voluntario_encontrado.email
    novo_telefone = telefone if telefone is not None else voluntario_encontrado.telefone

    valido, mensagem_erro = validar_dados(novo_nome, novo_email, novo_telefone)
    if not valido:
        return False, mensagem_erro

    voluntario_encontrado.nome = novo_nome.strip()
    voluntario_encontrado.email = novo_email.strip()
    voluntario_encontrado.telefone = novo_telefone.strip()

    return True, voluntario_encontrado


# ---------------------------------------------------------
# Guardar em ficheiro (JSON)
# ---------------------------------------------------------
def guardar_em_ficheiro(nome_ficheiro="voluntarios.json"):
    """
    Guarda todos os voluntários atualmente em memória num ficheiro JSON.
    Devolve (True, "mensagem") ou (False, "mensagem de erro").
    """
    try:
        dados = []
        for v in voluntarios:
            dados.append({
                "idVoluntario": v.idVoluntario,
                "nome": v.nome,
                "email": v.email,
                "telefone": v.telefone,
                "dataRegisto": str(v.dataRegisto),
                "ativo": v.ativo,
            })

        with open(nome_ficheiro, "w", encoding="utf-8") as ficheiro:
            json.dump(dados, ficheiro, indent=4, ensure_ascii=False)

        return True, f"{len(dados)} voluntário(s) guardado(s) em '{nome_ficheiro}'."

    except (IOError, OSError) as erro:
        return False, f"Erro ao escrever no ficheiro: {erro}"


def ler_de_ficheiro(nome_ficheiro="voluntarios.json"):
    """
    Lê e devolve o conteúdo do ficheiro JSON de voluntários.
    Devolve (True, dados) ou (False, "mensagem de erro").
    """
    try:
        with open(nome_ficheiro, "r", encoding="utf-8") as ficheiro:
            dados = json.load(ficheiro)
        return True, dados

    except FileNotFoundError:
        return False, f"O ficheiro '{nome_ficheiro}' não foi encontrado."
    except json.JSONDecodeError as erro:
        return False, f"Erro ao interpretar o ficheiro JSON: {erro}"
