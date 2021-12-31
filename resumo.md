# Projeto 2 Segurança

##   ################################################################################################

## Objetivos

* desenvolver um novo protocolo e uma aplicação Web relacionada para explorá-lo.
* implementar um protocolo para autenticar pessoas em aplicações Web, proporcionando um maior nível de segurança (por exemplo, um protocolo desafio-resposta)
 --> para começar, eles podem implementar um protocolo de resposta de desafio existente com autenticação mútua, como o MS-CHAP-V2
* aplicativo Web desenvolvido no projeto anterior, mas agora explorando o e-CHAP

##   ################################################################################################

## Autenticação de pessoas em aplicativos da web

autenticações podem ser realizadoas na camada de aplicativo
 --> troca de dados dentro da carga útil de solicitações e respostas HTTP
 --> Neste caso, a autenticação é efetuada com formulários HTML, frequentemente mediados por Javascript, onde os utilizadores fornecem diretamente as suas credenciais

##   ################################################################################################

## Autenticação desafio-resposta

(ver slides para mais informações)

* Estes protocolos normalmente produzem uma resposta dada um segredo e um desafio.

* O desafio e a resposta podem ser usados ​​para realizar ataques de descoberta de senha (por exemplo, usando dicionários). Portanto, tais respostas devem ser fornecidas apenas a entidades confiáveis.

* Ambas as partes (a que é autenticada e a que autentica) partilham uma senha (ou a transformação/criptografia dela)
 --> em resumo, eles podem usar credenciais pessoais para executar a chamada **autenticação mútua** (ver conceito)

EXEMPLO DE PROTOCOLO: MS-CHAP-V2
 --> Normalmente, em uma interação cliente-serviço, o servidor é o participante que obtém a primeira resposta (consulte MS-CHAP-V2)

##   ################################################################################################

## Protocolo de autenticação de desafio-resposta nível 14 no Clash Royale (E-CHAP)

* Consiste em executar o protocolo de autenticação N vezes ao invés de 1 vez (ou seja executar o protocolo MS-CHAP-V2 N vezes, por exemplo)
* Quanto maior o N, menor será a probabilidade de haver bandidos a roubar dados

PARA ESTE PROJETO ==> selecionar um valor fixo e razoável para N

* Além disso, durante a execução do protocolo N vezes, cada participante não deve abortar a execução do protocolo após receber uma resposta errada para um determinado desafio. Em vez disso, deve continuar, mas fornecendo respostas aleatórias a partir de então. Dessa forma, se o outro for um impostor, não se beneficiará mais com a informação recebida após a detecção do erro

##   ################################################################################################

## UAP - Aplicativo de autenticação de usuário

Para implementar o E-CHAP, temos que ter uma app sob o controlo do usuário

Esta app chamará a autenticação de usuário e funcionará do seguinte modo:

 1. expõe uma API REST
 2. recebe solicitações HTTP de um navegador (local) para realizar uma autenticação com um determinado servidor (nome DNS)
 3. executa o protocolo de autenticação com esse servidor

O UAP deve implementar as seguintes funcionalidades:

* Ele pode responder a redirecionamentos HTTP do serviço ou a chamadas JavaScript de um recurso fornecido pelo serviço. Além disso, o UAP pode interagir diretamente com o serviço (por meio de solicitações HTTP) ou usar redirecionamentos HTTP por meio do navegador.

* Ele pode ter sua própria interface de usuário ou usar o navegador do usuário para esse fim.

* Deve permitir que o usuário armazene vários pares de nome de usuário e senha para cada nome de serviço DNS).

* Ele deve informar ao usuário sobre o protocolo de autenticação que será executado em seu nome.

* Com relação às execuções do E-CHAP, deve informar ao usuário um erro em uma resposta do serviço, incluindo a fase do protocolo em que ocorreu. Observe, entretanto, que o E-CHAP não deve ser abortado por causa desse erro.

* Como não faz parte do navegador, ele deve ser iniciado de forma autônoma. Ao iniciar, ele deve solicitar uma senha que será usada para criptografar o banco de dados de credenciais do usuário (pares de nome de usuário-senha).

* Todos os dados armazenados devem ser criptografados. Por exemplo, você pode usar um banco de dados SQLite com valores de células criptografados ou um arquivo simples onde você armazena um dicionário JSON criptografado. Por motivos de privacidade, os nomes de serviço também devem ser criptografados e nomes de usuário ou senhas iguais não podem ser detectados. Finalmente, todos os valores criptografados devem incluir algum tipo de sal aleatório, para evitar o vazamento de informações de seu tamanho.

PARA ESTE PROJETO ==> Os alunos devem fornecer uma versão de seu aplicativo Web desenvolvido no projeto anterior, mas agora explorando o e-CHAP. Para começar, eles podem implementar um protocolo de resposta de desafio existente com autenticação mútua, como o MS-CHAP-V2.

##   ################################################################################################

## Entrega do projeto

* app_auth: contém o aplicativo da Web com o protocolo de autenticação estendido, incluindo instruções para executá-lo. Isso representa a página da web, em execução em um servidor remoto.

* uap: contém o UAP, incluindo instruções para executá-lo. Este componente seria executado no computador cliente.

* README.md: contém a descrição do projeto e os autores;


sudo apt install php7.4-cli
