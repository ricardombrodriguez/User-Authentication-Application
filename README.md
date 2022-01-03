# 2nd  Project SIO 2021/2022 - **Authentication**



## Introduction

For the 2nd assignment of the [Segurança Informática e nas Organizações](https://www.ua.pt/pt/uc/4143) course, we decided to focus on the website we worked on for the first project and improve the security components implementing a new authentication protocol and exploring it. For this, we created a new component that is responsible for authenticating the user login information and redirecting the user to the web-server if all is right, where as in the last project this was all done by the web-server component.


## Description

When the user enters the ***Spoton*** website for the first time, a *Login* button is displayed in the top right corner of the screen. If the user clicks it, the authentication process will start. The website will send its DNS to the *UAP*, so that the latter knows that a user is asking for an authentication in that website. In the same time, the user is redirected to the *UAP*, running in the client computer. 

The first step asks the user for cryptography credentials (encryption and decryption). It's the first time that the user enters the *UAP*, the introduced credentials will be used to encrypt and decrypt the file where the credentials are stored for now on. If the user tries to use other credentials than the ones used in the first time, he will get an error as the credentials are invalid. This can be done because if the cryptography credentials are correct, the file can be decrypted correctly and the first bytes of the file will show a "success" message and we then know the credentials were correct. Otherwise, the error will be shown and the *UAP* asks again for credentials.





## Protocol

 - User inserts email and password;
 - Sends email to server;
 - Server creates the first challenge and sends it to the uap;
 - Uap also creates a challenge and solves the new one, ( hash of received challenge + password + challenge created);
 - From now on the server and uap will check if the other solved correctly their challenge, as well as solving the one they received;
 - If any service detects a wrong answer, it will start to produce randoms challenges and the connection won't be made;
 - The process ends with the server accepting that the uap is safe and the login will be completed.


 ## Entities

 - **app_auth**:

    Our website is hosted in this directory, which contains our web application, ***Spoton**.* The website is the same one we delivered in the first project with the necessary change to accomodate our new authentication protocol.

 - **uap**:

    The *uap* is where the main part of our new protocol is implemented. It runs in the client's computer and the user will use it to login to our application. It also needs an encription password to encript and store the username-password values in a database.

#### **How to execute:**

- Inside the main folder run:

    ```bash
    ./run.sh
    ```
    
    You may need to grant permission by using the command::
    
    ```bash
    chmod -R +x run.sh
    ```

​		This will run the website, the MySQL database and the flask application on the server side.



To access the website, type this URL in your browser:

```
http://172.2.0.2/
```







## **Authors**

| NMEC  | Name              |                   Email  |
| ----- | ----------------- | -----------------------: |
| 98474 | João Reis         |       joaoreis16@ua.pt   |
| 98595 | Diogo Cruz        |         diogophc@ua.pt   |
| 98388 | Ricardo Rodriguez | ricardorodriguez@ua.pt   |
| 93310 | Gonçalo Pereira   |  pereira.goncalo@ua.pt   |
