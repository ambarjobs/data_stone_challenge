# Desafio Técnico Data Stone - Desenvolvedor Backend Python/Django

Este projeto corresponde ao desafio técnico para a vaga de Desenvolvedor Backend Python/Django na Data Stone.

## O problema

O problema apresentado corresponde à construção de uma API que permita a conversão de valores entre duas moedas.

A conversão deve ser feita usando taxas de câmbio reais e atualizadas.

A moeda de lastro deve ser `USD` (dólar americano).

A API deve inicialmente calcular a conversão entre qualquer par das seguintes moedas:

- `USD`
- `BRL`
- `EUR`
- `BTC`
- `ETH`

A requisição deve receber os seguintes parâmetros:

- a moeda de origem
- o valor a ser convertido
- a moeda de destino

Exemplo:
`?from=BTC&to=EUR&amount=123.45`

### Requisitos

O código deve rodar em Linux Ubuntu (preferencialmente dentro de um container Docker).

Para executar o seu código deve ser preciso apenas rodar os seguintes comandos:

- git clone $seu-fork
- cd $seu-fork
- comando para instalar as dependências
- comando para executar a aplicação

## Instalando o projeto

### Obtendo a cópia do código

O código deve ser baixado do repositório do projeto

```shell
git clone *********
cd *********
```

### Docker

Este projeto usa um container Docker.

Assim o serviço do Docker deve estar instalado, habilitado e sendo executado em background na máquina onde ele será executado.

Além disso serão necessários os comandos `docker` e `docker-compose` (que normalmente são instalados junto com o pacote `docker`).

Aqui se pode encontrar os detalhes de como fazer a instalação na sua máquina Linux se necessário:

https://docs.docker.com/engine/install/#server

(prefira a instalação do pacote da sua distribuição)

### Utilitários de Make

Para simplificar o processo de building, inicialização e operação em geral do container há um `Makefile` com comandos para ajudá-lo nessas tarefas.

No diretório raiz do projeto execute:

```shell
make
```
para obter uma lista dos comandos disponíveis.

### Variáveis de ambiente

Parâmetros sigilosos de configuração, como usuários e senhas da base de dados ou do Django são configuradas através de variáveis de ambiente (como recomendado pelo ).

Essas variáveis de ambiente serão lidas de um arquivo `.env` (**não** incluso no repositório, por questão de segurança) e inseridas no ambiente do docker .

Existe um modelo (`.env_template`), com valores vazios, no diretório raiz do projeto que deve ser copiado para `.env` no mesmo diretório e preenchido com os valores sigilosos (cuidado com uso de caracteres especiais no shell, ex: `'`).

Não se esqueça de configurar esse arquivo **antes** de construir (build) os containers.

### Construindo (building) os containers

Certifique-se de que o daemon/service do docker esteja iniciado.

Para construir os containers você deve usar o seguinte comando:

```shell
make build
```

Isso irá construir containers para o `PostgreSQL`, o `Redis` e a `aplicação` (Django) e configurá-los conforme as variáveis de ambiente.

Além disso, esse comando inicializará os serviços, incluindo o servidor interno do Django e realizará as migrações de base de dados iniciais necessárias.

O servidor estará disponível apenas após o término dessas migrações (a construção dos containers pode demorar um pouquinho).

## Project execution

### Endpoints

O endereço base dos endpoints é: `http://localhost:8000/`

No caso deste desafio técnico, os endpoints estão agrupados no caminho `/api`, por se tratar de uma API RESTful.

O endpoint de conversão de moedas se encontra em:

http://localhost:8000/api/currency/conversion/

Ele usa o método `GET` e aceita os parâmetros mencionados na descrição do problema (`from`, `to` e `amount`) como uma query string (ex:`?from=BTC&to=EUR&amount=123.45`)

### Unit tests

Os testes unitários podem ser executados dentro do container docker usando comandos `make`.

Para executar todos os testes disponíveis use:

```shell
make test
```

Para executar um teste específico use os parâmetros de `make test` para escolher o nível de detalhe dos testes:

```shell
make test module=api class=TestExchangeApi test=test_get_exchange_rates__general_case
```

Conforme se omite parâmetros do lado direito se executa testes progressivamente mais amplos.

Por exemplo o comando abaixo executa todos os testes do módulo `api`:

```shell
make test module=api
```
## Decisões de projeto

Terminar de escrever


### Limitações do desafio

- Limitação 1
