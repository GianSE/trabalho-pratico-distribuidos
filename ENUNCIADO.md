Trabalho Prático
Propagação de Fake News em Sistemas Paralelos e Distribuídos

O trabalho consiste na transformação e evolução de uma aplicação sequencial para versões paralela e distribuída.

O problema aborda a simulação da propagação de fake news em uma população representada por uma matriz bidimensional, inspirada em modelos de autômatos celulares e dinâmica de propagação de informação.

Cada posição da matriz representa um indivíduo da população, que pode assumir diferentes estados:

- Ignorante: ainda não recebeu/acredita na informação;
- Espalhador: acredita e compartilha a informação;
- Inativo: recebeu a informação, mas não compartilha mais.

A propagação ocorre localmente utilizando a vizinhança de Moore (até 8 vizinhos), em gerações discretas. O código sequencial é fornecido em Python. O grupo deverá compreender o funcionamento do algoritmo, refatorar e adaptar a implementação para versões paralela e distribuída.

O grupo deverá:

- Desenvolver uma versão paralela utilizando Threads (Python ou Java);
- Desenvolver uma versão distribuída utilizando Sockets ou RMI;
- Comparar o desempenho entre as versões sequencial, paralela e distribuída, analisando speedup, eficiência, melhorias e limitações.

## Requisitos
Nas versões paralela e distribuída a serem avaliadas, o cálculo da próxima geração deve ser dividido explicitamente entre threads ou processos implementados pelo grupo.

O uso de bibliotecas ou mecanismos de paralelização implícita/automática não será considerado como implementação válida para fins de avaliação. Exemplos: NumPy vetorizado, Pandas, Numba, Cython, GPU/CUDA e frameworks paralelos. Mas será válido o uso explícito da biblioteca multiprocessing ao invés de threading para conseguir o paralelismo real em Python.

Implementação Paralela

A implementação paralela deve:

- utilizar Threads;
- dividir o processamento da matriz entre múltiplas threads;
- manter a consistência entre gerações;
- evitar condições de corrida (race conditions).

Implementação Distribuída

A implementação distribuída deve:

- utilizar Sockets ou RMI;
- dividir o processamento da matriz entre múltiplos processos/máquinas;
- sincronizar as fronteiras da matriz entre processos;
- garantir consistência das gerações.

Código Sequencial fornecido:

- uma implementação sequencial funcional;
- documentação básica do código;
- descrição do modelo computacional.

O grupo poderá:

- reutilizar integralmente o código;
- refatorar o código;
- modificar estruturas e algoritmos;
- implementar melhorias adicionais.

Melhorias e Extensões

É desejável que o grupo proponha melhorias e extensões no modelo original.
As melhorias poderão ser utilizadas como critério de diferenciação entre os trabalhos. O grupo deverá justificar tecnicamente as melhorias implementadas.

Exemplos:

- probabilidades diferentes de convencimento;
- influenciadores digitais;
- bots automatizados;
- múltiplas fake news simultâneas;
- resistência à propagação;
- uso de grafos/redes sociais;
- balanceamento dinâmico de carga;
- visualização gráfica;
- estatísticas adicionais;
- otimizações computacionais;
- redução de comunicação distribuída;
- análise probabilística.

O grupo deve buscar referências bibliográficas para fundamentar tanto o modelo, quanto as otimizações e as decisões de implementação.

Podem ser utilizadas:

- IEEE,
- ACM,
- Scopus,
- artigos científicos,
- livros,
- repositórios acadêmicos,
- documentação técnica.

Medição de Desempenho

O grupo deverá executar experimentos variando:

- tamanho da matriz;
- número de gerações;
- percentual inicial de espalhadores;
- número de threads;
- número de hosts/processos distribuídos.

Os mesmos cenários devem ser executados para as versões sequencial, paralela e distribuída.
As implementações paralela e distribuída devem preservar o comportamento lógico da versão sequencial.

Configuração Experimental

Descrever detalhadamente:

- processador;
- quantidade de núcleos;
- memória RAM;
- sistema operacional;
- linguagem utilizada;
- versão do interpretador/compilador;
- ambiente de execução.

Análise

O grupo deverá apresentar:

- tabelas comparativas;
- gráficos de desempenho;
- speedup;
- eficiência;
- análise de gargalos;
- análise de sincronização;
- análise de custo de comunicação;
- limitações observadas.

## O que deve ser entregue

- Código-fonte compactado contendo todos os códigos e instruções de execução;
- Apresentação (PDF):
- descrição do problema;
- explicação do modelo computacional;
- funcionamento da solução sequencial;
- explicação das versões paralela e distribuída;
- divisão da matriz/processamento;
- tabelas e gráficos;
- speedup e eficiência;
- dificuldades encontradas;
- melhorias implementadas;
- referências bibliográficas;
- contribuição individual dos integrantes.

Vídeo

Deve ser produzido um vídeo entre 10 a 15 minutos por grupo.

Todos os integrantes devem participar da apresentação.

O vídeo deve demonstrar:

- funcionamento da solução sequencial (apenas se houver alteração);
- funcionamento da solução paralela;
- funcionamento da solução distribuída;
- análise dos resultados obtidos.

Durante a apresentação, todos os integrantes devem explicar:

- partes específicas do código;
- decisões de implementação;
- divisão do processamento;
- divisão dos trabalhos entre os membros do grupo;
- sincronização e comunicação utilizadas.


Formato do Vídeo

Fluxo de Vídeo
- Codificador: H264 - MPEG-4 AVC;
- Resolução: 1280 × 720p;
- Taxa de quadros: 30 fps.

Fluxo de Áudio
- Codificador: MPEG AAC Audio;
- Canais: Estéreo;
- Taxa de amostragem: 44100 Hz.

Extensão
- MP4.

Como o vídeo pode ser gravado/editado
Pode-se utilizar ferramentas gratuitas de videoconferência:

- Google Meet,
- Teams,
- Zoom,
- Discord,
- Skype,
- OBS Studio,
- ou equivalentes;

Pode-se utilizar ferramentas gratuitas de gravação/edição;
O vídeo não deve possuir marca d'água;
A edição é permitida apenas para remover partes desnecessárias;
Não é obrigatório editar o vídeo;
Os integrantes devem aparecer com câmera ligada durante a apresentação.

Como o vídeo deve ser entregue

- O vídeo deve ser entregue no formato MP4;
- O nome do arquivo deve seguir o formato:
- AAAA-MM-DD - Grupo XX - FakeNews.mp4
- Exemplo: 2026-06-23 - Grupo 03 - FakeNews.mp4
- O vídeo deve ser enviado juntamente com os demais arquivos em um arquivo `.ZIP`
- Caso o vídeo ultrapasse o limite de envio do Moodle:
- poderá ser utilizado compartilhamento em nuvem;
- o link deve permanecer acessível até o término da avaliação.

Qualquer inadequação a essas regras terá desconto na nota final (0,5 por erro)

Critérios de Avaliação
Item 	Pontuação
Código Paralelo/Distribuído funcionando corretamente 	1
Participação de todos no vídeo 	1
Respostas e explicações técnicas apresentadas 	0,5
Qualidade e organização dos códigos comentados 	1
Resultados experimentais 	1
Melhorias e Inovações* 	até 3
Cumprimento do tempo estabelecido para apresentação 	0,5
Qualidade dos slides e apresentação 	1
Referências utilizadas 	1

*Cada melhoria/inovação poderá acrescentar até 0,5 ponto, limitado ao máximo de 3,0 pontos. É a critério do professor e deverão estar bem documentadas no material entregue.


Observações

- Trabalhos iguais terão nota zero;
- Não será aceito trabalho após o prazo;
- O grupo deve compreender o código desenvolvido;
- O aluno que não participar do vídeo de apresentação ficará com zero no trabalho
- O uso de IA generativa é permitido como apoio, mas não substitui:
- entendimento do código;
- análise experimental;
- fundamentação teórica;
- implementação prática.
- Toda utilização de código externo, IA generativa, artigos, repositórios ou bibliotecas adicionai deve ser devidamente referenciada.
