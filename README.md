# Código Python entregue

Esta pasta contém somente os arquivos Python usados na implementação,
validação e medição da propagação de fake news.

## Arquivos

- `FakeNews.py`: versão sequencial de referência;
- `FakeNewsParalela.py`: versão paralela com `threading.Thread`;
- `FakeNewsDistribuida.py`: versão distribuída com sockets TCP;
- `test_implementacoes.py`: testes de equivalência entre as versões;
- `benchmark.py`: medição reproduzível de tempos, speedup e eficiência.

Não são necessárias bibliotecas externas.

## Execução

### Versão sequencial

```text
python FakeNews.py
```

### Versão paralela

```text
python FakeNewsParalela.py --linhas 300 --colunas 300 --geracoes 10 --threads 4
```

### Versão distribuída

Em dois terminais, inicie os trabalhadores:

```text
python FakeNewsDistribuida.py worker --host 127.0.0.1 --port 5001
python FakeNewsDistribuida.py worker --host 127.0.0.1 --port 5002
```

Em outro terminal, execute o coordenador:

```text
python FakeNewsDistribuida.py coordinator --workers 127.0.0.1:5001,127.0.0.1:5002 --linhas 300 --colunas 300 --geracoes 10
```

Para utilizar máquinas diferentes, substitua `127.0.0.1` pelos endereços dos
hosts dos trabalhadores.

### Testes de equivalência

```text
python -m unittest -v test_implementacoes.py
```

### Benchmark

```text
python benchmark.py
```

O benchmark usa matriz `300 x 300`, dez gerações, 5% de espalhadores
iniciais, limiar 3 e semente 42. Ele gera `resultados_benchmark.csv` na
própria pasta, com tempos, speedup e eficiência.
