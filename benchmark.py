import csv
import os
import platform
import socket
import subprocess
import sys
import time

from FakeNews import criar_grade, proxima_geracao
from FakeNewsDistribuida import (
    conectar_trabalhadores,
    enviar,
    proxima_geracao_distribuida,
)
from FakeNewsParalela import proxima_geracao_paralela


LINHAS = 300
COLUNAS = 300
GERACOES = 10
PERCENTUAL = 0.05
LIMIAR = 3
SEMENTE = 42


def executar_sequencial():
    grade = criar_grade(LINHAS, COLUNAS, PERCENTUAL, SEMENTE)
    inicio = time.perf_counter()
    for _ in range(GERACOES):
        grade = proxima_geracao(grade, LIMIAR)
    return time.perf_counter() - inicio


def executar_paralela(quantidade_threads):
    grade = criar_grade(LINHAS, COLUNAS, PERCENTUAL, SEMENTE)
    inicio = time.perf_counter()
    for _ in range(GERACOES):
        grade = proxima_geracao_paralela(grade, quantidade_threads, LIMIAR)
    return time.perf_counter() - inicio


def porta_livre():
    with socket.socket() as servidor:
        servidor.bind(("127.0.0.1", 0))
        return servidor.getsockname()[1]


def executar_distribuida():
    portas = [porta_livre(), porta_livre()]
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

        grade = criar_grade(LINHAS, COLUNAS, PERCENTUAL, SEMENTE)
        inicio = time.perf_counter()
        for _ in range(GERACOES):
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
    tempos = {"Sequencial": executar_sequencial()}
    for quantidade in (1, 2, 4, 8):
        tempos[f"Threads ({quantidade})"] = executar_paralela(quantidade)
    tempos["Distribuída (2)"] = executar_distribuida()

    referencia = tempos["Sequencial"]
    caminho = "resultados_benchmark.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            ["versao", "tempo_s", "speedup", "eficiencia"]
        )
        for versao, tempo in tempos.items():
            trabalhadores = 1
            if versao.startswith("Threads"):
                trabalhadores = int(versao.split("(")[1].split(")")[0])
            elif versao.startswith("Distribuída"):
                trabalhadores = 2
            speedup = referencia / tempo
            eficiencia = speedup / trabalhadores
            escritor.writerow([
                versao,
                f"{tempo:.6f}",
                f"{speedup:.4f}",
                f"{eficiencia:.4f}",
            ])
            print(
                f"{versao}: {tempo:.6f} s | "
                f"speedup={speedup:.4f} | eficiência={eficiencia:.4f}"
            )

    print(f"\nResultados salvos em: {os.path.abspath(caminho)}")
    print(f"Python: {platform.python_version()}")
    print(f"Sistema: {platform.platform()}")


if __name__ == "__main__":
    main()
