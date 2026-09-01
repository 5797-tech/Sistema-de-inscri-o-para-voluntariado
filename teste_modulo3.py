"""
Teste do Módulo 3 — Remover, Editar e Guardar em Ficheiro
"""

from modulo1_dados import adicionar_voluntario, voluntarios
from modulo2_listagem import imprimir_lista
from modulo3_gestao import remover_voluntario, editar_voluntario, guardar_em_ficheiro, ler_de_ficheiro


# Preparar alguns dados de teste
sucesso, v1 = adicionar_voluntario("Ana Silva", "ana@email.com", "912345678")
sucesso, v2 = adicionar_voluntario("João Pereira", "joao@email.com", "913456789")
sucesso, v3 = adicionar_voluntario("Marta Costa", "marta@email.com", "914567890")

print("=" * 60)
print("Estado inicial")
print("=" * 60)
imprimir_lista(voluntarios)

print()
print("=" * 60)
print("TESTE 1 — Editar um voluntário existente")
print("=" * 60)
ok, resultado = editar_voluntario(v2.idVoluntario, telefone="911111111")
if ok:
    print(f"[OK] Voluntário {resultado.idVoluntario} atualizado -> novo telefone: {resultado.telefone}")
else:
    print(f"[ERRO] {resultado}")

print()
print("=" * 60)
print("TESTE 2 — Editar com dados inválidos (deve falhar)")
print("=" * 60)
ok, resultado = editar_voluntario(v2.idVoluntario, email="email-invalido")
if not ok:
    print(f"[ERRO ESPERADO] {resultado}")
else:
    print(f"[FALHA DO TESTE] Dados inválidos foram aceites: {resultado}")

print()
print("=" * 60)
print("TESTE 3 — Remover um voluntário existente")
print("=" * 60)
ok, mensagem = remover_voluntario(v1.idVoluntario)
print(f"[OK] {mensagem}" if ok else f"[ERRO] {mensagem}")
imprimir_lista(voluntarios)

print()
print("=" * 60)
print("TESTE 4 — Remover um voluntário inexistente (deve falhar)")
print("=" * 60)
ok, mensagem = remover_voluntario("V-9999")
print(f"[ERRO ESPERADO] {mensagem}" if not ok else f"[FALHA DO TESTE] {mensagem}")

print()
print("=" * 60)
print("TESTE 5 — Guardar em ficheiro")
print("=" * 60)
ok, mensagem = guardar_em_ficheiro("voluntarios.json")
print(f"[OK] {mensagem}" if ok else f"[ERRO] {mensagem}")

print()
print("=" * 60)
print("TESTE 6 — Ler e confirmar o conteúdo do ficheiro")
print("=" * 60)
ok, dados = ler_de_ficheiro("voluntarios.json")
if ok:
    print(f"[OK] Ficheiro lido com sucesso. Conteúdo:")
    for registo in dados:
        print(registo)
else:
    print(f"[ERRO] {dados}")
