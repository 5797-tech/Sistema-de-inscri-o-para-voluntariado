"""
Teste do Módulo 1 — Introdução de Dados, Validação e Armazenamento em Memória
"""

from modulo1_dados import adicionar_voluntario, voluntarios


print("=" * 60)
print("TESTE 1 — Inserção de dados VÁLIDOS")
print("=" * 60)

casos_validos = [
    ("Ana Silva", "ana@email.com", "912345678"),
    ("João Pereira", "joao.pereira@email.com", "913456789"),
    ("Marta Costa", "marta@email.com", "914567890"),
]

for nome, email, telefone in casos_validos:
    sucesso, resultado = adicionar_voluntario(nome, email, telefone)
    if sucesso:
        print(f"[OK] {resultado.nome} registado com sucesso -> ID: {resultado.idVoluntario}, "
              f"password temporária: {resultado.password}")
    else:
        print(f"[ERRO] {nome}: {resultado}")

print()
print("=" * 60)
print("TESTE 2 — Inserção de dados INVÁLIDOS")
print("=" * 60)

casos_invalidos = [
    ("", "email@email.com", "912345678"),             # nome vazio
    ("Jo", "email@email.com", "912345678"),            # nome muito curto
    ("Pedro Alves", "pedro-email.com", "912345678"),   # email mal formatado
    ("Rita Fonseca", "rita@email.com", "91234"),        # telefone com poucos dígitos
    ("Carlos Nunes", "carlos@email.com", "9123456AB"),  # telefone com letras
]

for nome, email, telefone in casos_invalidos:
    sucesso, resultado = adicionar_voluntario(nome, email, telefone)
    if not sucesso:
        print(f"[ERRO ESPERADO] nome='{nome}', email='{email}', telefone='{telefone}' -> {resultado}")
    else:
        print(f"[FALHA DO TESTE] Dados inválidos foram aceites: {resultado}")

print()
print("=" * 60)
print(f"TOTAL DE VOLUNTÁRIOS GUARDADOS EM MEMÓRIA: {len(voluntarios)}")
print("=" * 60)
for v in voluntarios:
    print(v)
