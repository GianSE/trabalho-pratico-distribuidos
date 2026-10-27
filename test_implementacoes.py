import socket
import threading
import time
import unittest

from FakeNews import criar_grade, proxima_geracao
from FakeNewsDistribuida import (
    conectar_trabalhadores,
    enviar,
    executar_worker,
    proxima_geracao_distribuida,
)
from FakeNewsParalela import proxima_geracao_paralela


class TestImplementacoes(unittest.TestCase):
    def setUp(self):
        self.grade = criar_grade(18, 23, 0.12, 42)

    def test_paralela_preserva_cada_geracao(self):
        sequencial = self.grade
        paralela = self.grade
        for _ in range(5):
            sequencial = proxima_geracao(sequencial, 2)
            paralela = proxima_geracao_paralela(paralela, 4, 2)
            self.assertEqual(paralela, sequencial)

    def test_distribuida_preserva_cada_geracao(self):
        portas = [self._porta_livre(), self._porta_livre()]
        workers = [
            threading.Thread(
                target=executar_worker,
                args=("127.0.0.1", porta),
                daemon=True,
            )
            for porta in portas
        ]
        for worker in workers:
            worker.start()
        conexoes = []
        try:
            limite = time.time() + 5
            while time.time() < limite:
                try:
                    conexoes = conectar_trabalhadores(
                        [("127.0.0.1", porta) for porta in portas], timeout=0.5
                    )
                    break
                except OSError:
                    time.sleep(0.05)
            if not conexoes:
                raise AssertionError("Worker não abriu a porta no prazo")
            sequencial = self.grade
            distribuida = self.grade
            for _ in range(5):
                sequencial = proxima_geracao(sequencial, 2)
                distribuida = proxima_geracao_distribuida(
                    distribuida, conexoes, 2, timeout=5
                )
                self.assertEqual(distribuida, sequencial)
        finally:
            for conexao in conexoes:
                try:
                    enviar(conexao, {"comando": "encerrar"})
                except (ConnectionError, OSError):
                    pass
                conexao.close()
            for worker in workers:
                worker.join(timeout=5)

    @staticmethod
    def _porta_livre():
        with socket.socket() as servidor:
            servidor.bind(("127.0.0.1", 0))
            return servidor.getsockname()[1]

if __name__ == "__main__":
    unittest.main()
