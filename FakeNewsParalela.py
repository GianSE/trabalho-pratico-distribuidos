"""
Simulação paralela usando threading.Thread.

Cada thread calcula um intervalo exclusivo de linhas da próxima geração.
A geração atual nunca é alterada durante o cálculo; a troca para a nova
geração acontece somente depois que todas as threads terminam.
"""

import argparse
import threading
import time

from FakeNews import (
    ESPALHADOR,
    calcular_linhas,
    contar_estados,
    criar_grade,
    imprimir_grade,
)


def dividir_linhas(total, partes):
    """Divide total linhas em partes equilibradas, sem intervalos vazios."""
    partes = max(1, min(partes, total))
    base, resto = divmod(total, partes)
    intervalos = []
    inicio = 0
    for indice in range(partes):
        tamanho = base + (1 if indice < resto else 0)
        intervalos.append((inicio, inicio + tamanho))
        inicio += tamanho
    return intervalos


def proxima_geracao_paralela(grade, threads=4, limiar_convencimento=2):
    """Calcula a próxima geração dividindo linhas entre threads explícitas."""
    if not grade or not grade[0]:
        raise ValueError("A grade não pode ser vazia")
    if threads < 1:
        raise ValueError("O número de threads deve ser positivo")

    resultados = [None] * len(grade)
    erros = []

    def trabalhador(inicio, fim):
        try:
            resultados[inicio:fim] = calcular_linhas(
                grade, inicio, fim, limiar_convencimento
            )
        except Exception as erro:
            erros.append(erro)

    execucoes = []
    for inicio, fim in dividir_linhas(len(grade), threads):
        thread = threading.Thread(
            target=trabalhador,
            args=(inicio, fim),
            name=f"fake-news-linhas-{inicio}-{fim}",
        )
        execucoes.append(thread)
        thread.start()

    for thread in execucoes:
        thread.join()

    if erros:
        raise RuntimeError("Falha ao calcular uma partição da grade") from erros[0]
    return resultados


def executar_simulacao(
    linhas=100,
    colunas=100,
    geracoes=50,
    percentual_espalhadores=0.02,
    limiar_convencimento=2,
    threads=4,
    mostrar_grade=False,
    semente=42,
):
    grade = criar_grade(linhas, colunas, percentual_espalhadores, semente)
    inicio_tempo = time.perf_counter()

    for geracao in range(geracoes):
        grade = proxima_geracao_paralela(
            grade, threads, limiar_convencimento
        )
        contagem = contar_estados(grade)
        print(
            f"Geração {geracao + 1:03d} | "
            f"Ignorantes: {contagem[0]:>10,} | "
            f"Espalhadores: {contagem[1]:>10,} | "
            f"Inativos: {contagem[2]:>10,}"
        )
        if mostrar_grade:
            imprimir_grade(grade)
        if contagem[ESPALHADOR] == 0:
            break

    tempo = time.perf_counter() - inicio_tempo
    print(
        f"Paralela: {linhas}x{colunas}, {threads} threads, "
        f"{tempo:.4f} segundos"
    )
    return grade, tempo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--linhas", type=int, default=100)
    parser.add_argument("--colunas", type=int, default=100)
    parser.add_argument("--geracoes", type=int, default=50)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--percentual", type=float, default=0.05)
    parser.add_argument("--limiar", type=int, default=3)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--mostrar-grade", action="store_true")
    args = parser.parse_args()
    executar_simulacao(
        args.linhas, args.colunas, args.geracoes, args.percentual,
        args.limiar, args.threads, args.mostrar_grade, args.semente
    )


if __name__ == "__main__":
    main()
