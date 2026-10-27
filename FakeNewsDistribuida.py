"""
Coordenador e trabalhador TCP para a simulação distribuída.

Uso:
  python FakeNewsDistribuida.py worker --port 5001
  python FakeNewsDistribuida.py coordinator --workers 127.0.0.1:5001,127.0.0.1:5002
"""

import argparse
import pickle
import socket
import struct
import time

from FakeNews import (
    ESPALHADOR,
    calcular_linhas,
    contar_estados,
    criar_grade,
    imprimir_grade,
)
from FakeNewsParalela import dividir_linhas

HOST_PADRAO = "0.0.0.0"
TAMANHO_CABECALHO = 4


def enviar(conexao, valor):
    dados = pickle.dumps(valor, protocol=pickle.HIGHEST_PROTOCOL)
    conexao.sendall(struct.pack("!I", len(dados)) + dados)


def receber(conexao):
    cabecalho = receber_bytes(conexao, TAMANHO_CABECALHO)
    tamanho = struct.unpack("!I", cabecalho)[0]
    if tamanho <= 0:
        raise ConnectionError("Mensagem TCP inválida")
    return pickle.loads(receber_bytes(conexao, tamanho))


def receber_bytes(conexao, quantidade):
    partes = []
    restante = quantidade
    while restante:
        parte = conexao.recv(restante)
        if not parte:
            raise ConnectionError("Conexão encerrada durante uma mensagem")
        partes.append(parte)
        restante -= len(parte)
    return b"".join(partes)


def executar_worker(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, port))
        servidor.listen()
        print(f"Trabalhador aguardando conexões em {host}:{port}", flush=True)
        conexao, endereco = servidor.accept()
        with conexao:
            print(f"Coordenador conectado: {endereco}", flush=True)
            while True:
                mensagem = receber(conexao)
                if mensagem["comando"] == "encerrar":
                    break
                if mensagem["comando"] != "calcular":
                    raise ValueError("Comando distribuído desconhecido")
                grade_local = mensagem["grade_local"]
                inicio_global = mensagem["inicio_global"]
                fim_global = mensagem["fim_global"]
                inicio_local = inicio_global - mensagem["offset_local"]
                fim_local = fim_global - mensagem["offset_local"]
                resultado = calcular_linhas(
                    grade_local,
                    inicio_local,
                    fim_local,
                    mensagem["limiar"],
                )
                enviar(conexao, {"inicio": inicio_global, "linhas": resultado})


def conectar_trabalhadores(enderecos, timeout):
    conexoes = []
    try:
        for host, port in enderecos:
            conexao = socket.create_connection((host, port), timeout=timeout)
            conexao.settimeout(timeout)
            conexoes.append(conexao)
    except Exception:
        for conexao in conexoes:
            conexao.close()
        raise
    return conexoes


def proxima_geracao_distribuida(grade, conexoes, limiar=2, timeout=30):
    """Envia a geração e um halo de uma linha para cada trabalhador."""
    if not conexoes:
        raise ValueError("É necessário pelo menos um trabalhador")
    intervalos = dividir_linhas(len(grade), len(conexoes))
    tarefas = []
    for conexao, (inicio, fim) in zip(conexoes, intervalos):
        halo_inicio = max(0, inicio - 1)
        halo_fim = min(len(grade), fim + 1)
        enviar(
            conexao,
            {
                "comando": "calcular",
                "grade_local": grade[halo_inicio:halo_fim],
                "offset_local": halo_inicio,
                "inicio_global": inicio,
                "fim_global": fim,
                "limiar": limiar,
            },
        )
        tarefas.append((conexao, inicio, fim))

    nova_grade = [None] * len(grade)
    for conexao, inicio, fim in tarefas:
        resposta = receber(conexao)
        if resposta["inicio"] != inicio or len(resposta["linhas"]) != fim - inicio:
            raise RuntimeError("Resposta de trabalhador não corresponde à partição")
        nova_grade[inicio:fim] = resposta["linhas"]
    return nova_grade


def executar_simulacao(
    linhas=100,
    colunas=100,
    geracoes=50,
    percentual_espalhadores=0.02,
    limiar_convencimento=2,
    trabalhadores=("127.0.0.1", 5001),
    mostrar_grade=False,
    semente=42,
):
    grade = criar_grade(linhas, colunas, percentual_espalhadores, semente)
    inicio_tempo = time.perf_counter()
    conexoes = conectar_trabalhadores(trabalhadores, 30)
    try:
        for geracao in range(geracoes):
            grade = proxima_geracao_distribuida(
                grade, conexoes, limiar_convencimento
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
    finally:
        for conexao in conexoes:
            try:
                enviar(conexao, {"comando": "encerrar"})
            finally:
                conexao.close()

    tempo = time.perf_counter() - inicio_tempo
    print(
        f"Distribuída: {linhas}x{colunas}, {len(trabalhadores)} trabalhadores, "
        f"{tempo:.4f} segundos"
    )
    return grade, tempo


def ler_enderecos(valor):
    enderecos = []
    for item in valor.split(","):
        host, porta = item.rsplit(":", 1)
        enderecos.append((host, int(porta)))
    return enderecos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="modo", required=True)
    worker = subparsers.add_parser("worker")
    worker.add_argument("--host", default=HOST_PADRAO)
    worker.add_argument("--port", type=int, required=True)
    coordinator = subparsers.add_parser("coordinator")
    coordinator.add_argument("--workers", required=True)
    coordinator.add_argument("--linhas", type=int, default=100)
    coordinator.add_argument("--colunas", type=int, default=100)
    coordinator.add_argument("--geracoes", type=int, default=50)
    coordinator.add_argument("--percentual", type=float, default=0.05)
    coordinator.add_argument("--limiar", type=int, default=3)
    coordinator.add_argument("--semente", type=int, default=42)
    coordinator.add_argument("--mostrar-grade", action="store_true")
    args = parser.parse_args()
    if args.modo == "worker":
        executar_worker(args.host, args.port)
    else:
        executar_simulacao(
            args.linhas, args.colunas, args.geracoes, args.percentual,
            args.limiar, ler_enderecos(args.workers),
            args.mostrar_grade, args.semente
        )


if __name__ == "__main__":
    main()
