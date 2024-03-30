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

Parâmetros sigilosos de configuração, como usuários e senhas da base de dados ou do Django são configuradas através de variáveis de ambiente.

Essas variáveis de ambiente serão lidas de um arquivo `.env` (**não** incluso no repositório, por questão de segurança) e inseridas no ambiente do docker .

Existe um modelo (`.env_template`), com valores vazios, no diretório raiz do projeto que deve ser copiado para `.env` no mesmo diretório e preenchido com os valores sigilosos (cuidado com uso de caracteres especiais no shell, ex: `'`).

**IMPORTANTE**:

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

## Uso do projeto

### Endpoints

O endereço base dos endpoints é: `http://localhost:8000/`

No caso deste desafio técnico, os endpoints estão agrupados no caminho `/api`, por questão de organização e se tratar de uma API RESTful.

O endpoint de conversão de moedas se encontra em:

http://localhost:8000/api/currency/conversion/

Ele usa o método `GET` e aceita os parâmetros mencionados na descrição do problema (`from`, `to` e `amount`) como uma query string (ex:`?from=BTC&to=EUR&amount=123.45`)

As chamadas à API externa de taxas de câmbio de moedas é cacheada, sendo que a retenção do cache pode ser configurada em `settings` através da variável `EXCHANGE_RATES_CACHE_TIMEOUT` (inicialmente ajustada em 30 minutos).

O endpoint faz várias verificações a respeito da presença dos parâmetros de requisição, da existência dos acrônimos das moedas e validação dos dados recebidos da API externa (ver mais detalhes nos testes unitários).

Além desse endpoint existe um outro, não solicitado, mas que foi muito útil para o desenvolvimento, pois ele permite limpar o cache do Redis.

Esse endpoint, que deve ser acessado através de um método `POST` sem parâmetros está em:

http://localhost:8000/api/cache/clear/

### Administração das moedas

A lista de moedas disponíveis para conversão estão armazenadas numa tabela, representada pelo modelo `Currency`.

O modelo está disponível no admin do Django, de modo que é possível acrescentar moedas adicionais ou remover as existentes além das indicadas na especificação do problema, que já foram inseridas automaticamente através de uma migration do Django.

Este modelo possui um método de classe que permite a obtenção da lista das moedas e utiliza o Redis como cache, de maneira que a operação normal do sistema não sobrecarregue a base de dados.

O tempo de retenção desse outro cache pode ser configurado em `settings` através da variável `ACRONYMS_LIST_CACHE_TIMEOUT`, configurada inicialmente com 10 minutos.

Isso significa que alguma alteração nas moedas disponíveis pode demorar até 10 minutos (ou o tempo configurado na variável) para terem efeito.

O acrônimo da moeda sendo inserida é limitado a 3 caracteres, ele será convertido automaticamente para maiúsculas ao ser armazenado na base e valores não alfabéticos serão rejeitados.

Para poder utilizar o admin do Django é necessário criar um usuário de administração.

Isso pode ser feito através do seguinte comando de `make`:

```shell
make create_admin_superuser
```

Será solicitado o nome do usuário e a senha.

### Testes unitários

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

Foi utilizado um ambiente containerizado em Docker para simplificar a criação e manutenção do ambiente do desafio técnico.

Os containers são completamente configurados através de variáveis de ambiente que também carregam informações sigilosas como as credenciais de acesso à base de dados e aplicação (como recomendado pelo [Twelve-Factor App](https://12factor.net/)).

Como descrito acima existe um `Makefile` com comandos de operação dos containers (building, parada, início, status) e da aplicação (testes, logs, migrations, shell).

Isso facilita tanto o desenvolvimento como a utilização do ambiente do desafio técnico.

Como indicado acima, para evitar problems de desempenho e sobrecarga de chamadas à API de obtenção de taxas de câmbio, foi usado o cache do Django (usando Redis), para cachear as requisições àquela API.

Do mesmo modo, o acesso à lista de moedas suportadas pela aplicação poderia impor uma carga desnecessária á tabela de moedas (`Currency`), por isso criei um método de classe que usa diretamente o Redis para cachear também esse resultado.

A API externa para obtenção das taxas de câmbio atualizadas que escolhi foi a do URL https://cdn.moeda.info/api/latest.json, conforme configurado em `settings.EXCHANGE_RATES_API_URL`, pois foi a única que encontrei completamente gratuita e sem limitações, embora seja uma API mais simples e atualizada a cada hora.

Essa API é tem como lastro o `USD` (como solicitado) e foi talvez a única a fornecer cotação do `ETH`(Ethereum).

A decisão de usar uma tabela apenas para guardar os acrônimos das moedas se baseou no fato de que já temos a atualização das cotações através da API e assim me pareceu de pouca valia guardar as taxas na tabela.

Mesmo em caso de indisponibilidade da API de taxas talvez faça mais sentido não fazer a conversão do que a fazer com dados desatualizados (mas isso dependeria da aplicação real e aqui é apenas um desafio).

No caso de que fosse necessário guardar as cotações das moedas, seria preciso verificar se houve um `miss` no acesso do cache de página do Django (`cache_page`) e somente então providenciar a requisição real na API externa e armazená-la na base de dados apenas nesse momento.

Não consegui encontrar a informação de como fazê-lo através do cache do Django e como precisei administrar o tempo para o resto do desafio, deixei essa possibilidade (que não era obrigatória) de lado.

Para a API usei um serializador apenas para validar os dados de entrada, uma vez que a saída era simples e desvinculada de um modelo não vi necessidade de usar um serializador para isso.

### Limitações do desafio

A maioria das limitações abaixo (se não todas) devem-se principalmente ao escopo reduzido do projeto e à necessidade de administrar o tempo para completá-lo com qualidade.

- Não foi configurado um container com um proxy reverso (como o `nginx`, por exemplo), que seria uma necessidade para uma aplicação exposta à Internet.

- Não foram criados certificados e não foram configuradas conexões TLS / HTTPS para os serviços.

- Como indicado anteriormente, as taxas de câmbio não foram armazenadas localmente, pois sua utilidade poderia ser limitada e isso não fazia parte do escopo do desafio de forma clara.

- Apesar de que houveram validação e restrições na entrada de dados das moedas na tabela pelo admin do Django, ainda poderiam ter sido verificada se a moeda entrada existe na API externa.

- O Redis não foi configurado com usuário e senha para acesso seguro ao cache (que no caso descrito não possui informações confidenciais).
