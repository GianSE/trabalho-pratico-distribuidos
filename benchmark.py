import csv
import os
import platform
import socket
import subprocess
import sys
import time

import matplotlib.pyplot as plt

from FakeNews import criar_grade, proxima_geracao
from FakeNewsDistribuida import (
    conectar_trabalhadores,
    enviar,
    proxima_geracao_distribuida,
)
from FakeNewsParalela import proxima_geracao_paralela


LIMIAR = 3
SEMENTE = 42
THREADS = (1, 2, 4, 8)
TRABALHADORES = (1, 2)
SCENARIOS = (
    (100, 5, 0.02),
    (200, 10, 0.05),
    (300, 10, 0.05),
)


def executar_sequencial(linhas, geracoes, percentual):
    grade = criar_grade(linhas, linhas, percentual, SEMENTE)
    inicio = time.perf_counter()
    for _ in range(geracoes):
        grade = proxima_geracao(grade, LIMIAR)
    return time.perf_counter() - inicio


def executar_paralela(linhas, geracoes, percentual, quantidade_threads):
    grade = criar_grade(linhas, linhas, percentual, SEMENTE)
    inicio = time.perf_counter()
    for _ in range(geracoes):
        grade = proxima_geracao_paralela(grade, quantidade_threads, LIMIAR)
    return time.perf_counter() - inicio


def porta_livre():
    with socket.socket() as servidor:
        servidor.bind(("127.0.0.1", 0))
        return servidor.getsockname()[1]


def executar_distribuida(linhas, geracoes, percentual, quantidade_trabalhadores):
    portas = [porta_livre() for _ in range(quantidade_trabalhadores)]
    processos = []
    conexoes = []
    try:
        for porta in portas:
            processos.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "FakeNewsDistribuida.py",
                        "worker",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(porta),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
            )

        limite = time.time() + 10
        while time.time() < limite:
            try:
                conexoes = conectar_trabalhadores(
                    [("127.0.0.1", porta) for porta in portas],
                    timeout=1,
                )
                break
            except OSError:
                time.sleep(0.05)

        if not conexoes:
            raise RuntimeError("Os trabalhadores não ficaram disponíveis")

        grade = criar_grade(linhas, linhas, percentual, SEMENTE)
        inicio = time.perf_counter()
        for _ in range(geracoes):
            grade = proxima_geracao_distribuida(
                grade, conexoes, LIMIAR, timeout=30
            )
        return time.perf_counter() - inicio
    finally:
        for conexao in conexoes:
            try:
                enviar(conexao, {"comando": "encerrar"})
            except OSError:
                pass
            conexao.close()
        for processo in processos:
            processo.wait(timeout=10)


def main():
    caminho = "resultados_benchmark.csv"
    resultados = []
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            [
                "cenario", "linhas", "geracoes", "percentual",
                "versao", "paralelizadores", "tempo_s", "speedup",
                "eficiencia",
            ]
        )
        for indice, (linhas, geracoes, percentual) in enumerate(SCENARIOS, 1):
            cenario = f"Cenário {indice}"
            tempos = {
                "Sequencial": (
                    1,
                    executar_sequencial(linhas, geracoes, percentual),
                )
            }
            for quantidade in THREADS:
                tempos[f"Threads ({quantidade})"] = (
                    quantidade,
                    executar_paralela(
                        linhas, geracoes, percentual, quantidade
                    ),
                )
            for quantidade in TRABALHADORES:
                tempos[f"Distribuída ({quantidade})"] = (
                    quantidade,
                    executar_distribuida(
                        linhas, geracoes, percentual, quantidade
                    ),
                )

            referencia = tempos["Sequencial"][1]
            for versao, (paralelizadores, tempo) in tempos.items():
                speedup = referencia / tempo
                eficiencia = speedup / paralelizadores
                escritor.writerow([
                    cenario,
                    linhas,
                    geracoes,
                    f"{percentual:.2f}",
                    versao,
                    paralelizadores,
                    f"{tempo:.6f}",
                    f"{speedup:.4f}",
                    f"{eficiencia:.4f}",
                ])
                resultados.append({
                    "cenario": cenario,
                    "linhas": linhas,
                    "geracoes": geracoes,
                    "percentual": percentual,
                    "versao": versao,
                    "tempo": tempo,
                    "speedup": speedup,
                    "eficiencia": eficiencia,
                })
                print(
                    f"{cenario} | {linhas}x{linhas}, {geracoes} gerações, "
                    f"{percentual:.0%} | {versao}: {tempo:.6f} s | "
                    f"speedup={speedup:.4f} | eficiência={eficiencia:.4f}"
                )

    base = [
        item for item in resultados
        if item["cenario"] == "Cenário 3"
    ]
    nomes = [item["versao"] for item in base]
    tempos = [item["tempo"] for item in base]
    speedups = [item["speedup"] for item in base]

    plt.figure(figsize=(10, 5))
    plt.bar(nomes, tempos, color="#4472C4")
    plt.ylabel("Tempo (s)")
    plt.title("Tempo de execução - Cenário 3 (300 x 300, 10 gerações)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig("grafico_tempo.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.bar(nomes, speedups, color="#70AD47")
    plt.axhline(1, color="black", linewidth=0.8)
    plt.ylabel("Speedup")
    plt.title("Speedup - Cenário 3 (referência sequencial)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig("grafico_speedup.png", dpi=180)
    plt.close()

    print(f"\nResultados salvos em: {os.path.abspath(caminho)}")
    print("Gráficos salvos em: grafico_tempo.png e grafico_speedup.png")
    print(f"Python: {platform.python_version()}")
    print(f"Sistema: {platform.platform()}")


if __name__ == "__main__":
    main()
