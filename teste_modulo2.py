"""
Teste do Módulo 2 — Listagem, Pesquisa e Ordenação
"""

from modulo1_dados import adicionar_voluntario
from modulo2_listagem import listar_voluntarios, imprimir_lista, pesquisar_voluntario, ordenar_voluntarios


# Preparar alguns dados de teste
adicionar_voluntario("Marta Costa", "marta@email.com", "914567890")
adicionar_voluntario("Ana Silva", "ana@email.com", "912345678")
adicionar_voluntario("João Pereira", "joao@email.com", "913456789")
adicionar_voluntario("Beatriz Nunes", "beatriz@email.com", "915678901")


print("=" * 60)
print("TESTE 1 — Listagem de todos os voluntários")
print("=" * 60)
imprimir_lista(listar_voluntarios())

print()
print("=" * 60)
print("TESTE 2 — Pesquisa (dados existentes)")
print("=" * 60)
resultado = pesquisar_voluntario("nome", "ana")
print(f"Pesquisa por nome='ana' -> {len(resultado)} resultado(s) encontrado(s)")
imprimir_lista(resultado)

print()
print("=" * 60)
print("TESTE 3 — Pesquisa (dados inexistentes)")
print("=" * 60)
resultado = pesquisar_voluntario("nome", "xpto-inexistente")
print(f"Pesquisa por nome='xpto-inexistente' -> {len(resultado)} resultado(s) encontrado(s)")
imprimir_lista(resultado)

print()
print("=" * 60)
print("TESTE 4 — Ordenação crescente por nome")
print("=" * 60)
imprimir_lista(ordenar_voluntarios("nome", decrescente=False))

print()
print("=" * 60)
print("TESTE 5 — Ordenação decrescente por nome")
print("=" * 60)
imprimir_lista(ordenar_voluntarios("nome", decrescente=True))
