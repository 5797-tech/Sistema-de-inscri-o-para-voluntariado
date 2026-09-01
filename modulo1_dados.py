"""
Módulo 1 — Introdução de Dados, Validação e Armazenamento em Memória
Sistema de Inscrição e Gestão de Voluntariado

Este módulo é responsável por:
- Validar os dados de um novo voluntário (nome, email, telefone)
- Gerar automaticamente o ID de voluntário e a palavra-passe temporária
- Guardar os voluntários numa estrutura em memória (lista de objetos)
"""

import re
import random
import string
from datetime import date


# ---------------------------------------------------------
# Classe Voluntário (alinhada com o modelo de dados, 2.4.1/2.4.2)
# ---------------------------------------------------------
class Voluntario:
    def __init__(self, idVoluntario, nome, email, telefone, password):
        self.idVoluntario = idVoluntario
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.password = password
        self.dataRegisto = date.today()
        self.ativo = True

    def __repr__(self):
        return (f"Voluntario(id={self.idVoluntario}, nome='{self.nome}', "
                f"email='{self.email}', telefone='{self.telefone}', "
                f"password='{self.password}', dataRegisto={self.dataRegisto}, "
                f"ativo={self.ativo})")


# ---------------------------------------------------------
# Armazenamento em memória
# ---------------------------------------------------------
voluntarios = []          # lista onde os voluntários ficam guardados
_proximo_id = 1           # contador interno para gerar IDs únicos


# ---------------------------------------------------------
# Validação de dados
# ---------------------------------------------------------
def validar_dados(nome, email, telefone):
    """
    Valida os dados de um voluntário.
    Devolve (True, "") se os dados forem válidos,
    ou (False, "mensagem de erro") caso contrário.
    """
    if not nome or not nome.strip():
        return False, "O nome é obrigatório."

    if len(nome.strip()) < 3:
        return False, "O nome deve ter pelo menos 3 caracteres."

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return False, "O email introduzido não é válido."

    telefone_limpo = telefone.replace(" ", "") if telefone else ""
    if not telefone_limpo.isdigit() or len(telefone_limpo) != 9:
        return False, "O telefone deve conter exatamente 9 dígitos numéricos."

    return True, ""


# ---------------------------------------------------------
# Geração de ID e palavra-passe temporária
# ---------------------------------------------------------
def gerar_id():
    global _proximo_id
    novo_id = f"V-{_proximo_id:04d}"
    _proximo_id += 1
    return novo_id


def gerar_password_temporaria(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


# ---------------------------------------------------------
# Função principal: adicionar um voluntário
# ---------------------------------------------------------
def adicionar_voluntario(nome, email, telefone):
    """
    Valida e regista um novo voluntário.
    Devolve (True, objeto_voluntario) em caso de sucesso,
    ou (False, "mensagem de erro") em caso de falha.
    """
    valido, mensagem_erro = validar_dados(nome, email, telefone)

    if not valido:
        return False, mensagem_erro

    novo_id = gerar_id()
    password_temp = gerar_password_temporaria()

    voluntario = Voluntario(novo_id, nome.strip(), email.strip(), telefone.strip(), password_temp)
    voluntarios.append(voluntario)

    return True, voluntario
