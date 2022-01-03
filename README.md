# 2nd  Project SIO 2021/2022 - **Authentication**

## **1 | Introduction**

For the 2nd assignment of the [Segurança Informática e nas Organizações](https://www.ua.pt/pt/uc/4143) course, we decided to focus on the website we worked on for the first project and improve the security components implementing a new authentication protocol and exploring it. For this, we created a new component that is responsible for authenticating the user login information and redirecting the user to the web-server if all is right, where as in the last project this was all done by the web-server component.



## **2 | Entities**

- ***app_auth***:

    Our website is hosted in this directory, which contains the web application (in *PHP*), the *Flask* API and the *MySQL* database. The website is the same one we delivered in the first project with the necessary change to accomodate our new authentication protocol.

- ***uap***:

    The UAP (User Authentication Application) runs in the client's computer and the user will use it to login to an application. It also needs an encryption password to encrypt and store the username-password values in a database.





## **3 | Description**

When the user enters the **Spoton** website for the first time, a *Login* button is displayed in the top right corner of the screen. If the user clicks it, the authentication process will start. The website will send its DNS to the UAP, so that the latter knows that a user is asking for an authentication in that website. At the same time, the user is redirected to the UAP, running in the client computer.

The first is to ask the user for cryptography credentials (encryption and decryption). It's the first time that the user enters the UAP, the introduced credentials will be used to encrypt and decrypt the file where the credentials are stored from now on. If the user tries to use other credentials than the ones used in the first time, he will get an error as the credentials are invalid. This can be done because if the cryptography credentials are correct, the file can be decrypted correctly and the first bytes of the file will show a "success" message and we then know the credentials were correct. Otherwise, the error will be shown and the UAP asks again for credentials.

In the second step, the user is asked to input the credentials to enter the website he wants to login to. First, the UAP will search if there are credentials for the DNS where the user came. If they exist, they are displayed as an autocomplete dropdown and the password will be automatically set for the selected email.  After the user clicks the *Login* button, the challenge-response protocol will be activated to check if the credentials for that DNS are correct. The challenge-response protocol is executed between both the website server and the UAP, as they have to exchange information between each other to check the (in)validity of the other side.

The inserted email is sent to the server, the latter receives it and confirms if it exists in the database, displaying an error message saying that the credentials are invalid. Otherwise, the challenge-response protocol will start.

The server creates a challenge, which consists of a random integer, and sends it to the UAP, calculating the response and storing it. The UAP will create a new challenge and resolves the challenge sent by the server. The protocol response is calculated by combining the received challenge, password and the created challenge and hashing the result.

The server will follow the same logic and it goes on until the server reaches the maximum number of iterations for the applied protocol.

The reason we chose a 10 iteration challenge-response protocol with 2-bit responses is due to its security and efficiency:

- By choosing 2-bit responses, it creates the possibility of multiple passwords matching the responses to the challenges. So even if the attacker can match a password to the responses, they can still have the wrong one. If we chose to compare, let's say, the first 100 bits of the calculated response, the attacker would only need one match to know they had the right password, as the chance of getting the same 100-bits responses with a wrong password is basically none. This way, he knows he has the right password.

- By choosing 10 iterations, we find a balance between time efficiency, as more iterations mean it's less likely for an attacker to luckily match the calculated responses. On the other hand, too many iterations could create the same problem of the 100-bit responses explained before, by giving to much information to the attacker, besides making the protocol too slow for the user.

Probability of an attacker getting a valid authentication with wrong credentials:

```bash
iterations = 10     # number of challenge-response iterations
prob = 0.25         # probability of matching each 2-bit response
prob ^ iterations = 9.53674316e-7
```

As we can see, it's very unlikely that an attacker passes the authentication method with wrong credentials.

If at any point a service detects a wrong answer, it will start to produce randoms challenges without ending the protocol, although the connection won't be made.

After the website and UAP are done authenticating each other, the server generates a *UUID* token for that user. The database will be updated with a new token associated to a user, with an expire time of 5 minutes for the user to use the token. After this, the website server send a confirmation message that the user is valid and the produced token to the UAP. If the user is valid, he will be redirected to the website URL with the token appended to it (*website_url/?token={token}*).

In the website, if it receives a *token* parameter it will verify the existence of that same token in the database and guarantee that the expiration time for it is not over yet, allowing the user to log-in automatically.

This system is designed to be distributed, meaning several users can request an authentication to the same application at the same time.





## **4 | How to execute:**

- Inside the **root folder** run:

    ```bash
    ./run.sh
    ```

    You may need to grant permission by using the command:

    ```bash
    chmod -R +x run.sh
    ```

    **or**

    ```bash
    # terminal 1
    docker-compose down
    docker-compose build
    docker-compose up
    
    # terminal 2
    cd /uap/src
    python3 uap.py
    ```

    This will run the website, the MySQL database and the Flask application on the server side.

To access the website, type this URL in your browser:

```
<http://172.2.0.2/>
```

### **4.1 | Valid logins**

| Email            | Password |
| ---------------- | -------- |
| admin            | admin    |
| leitono@dil.papi | esti8    |

### **4.2 | Password that is used to encrypt and decrypt credentials.txt**

| Password |
| -------- |
| admin    |

This is the password we use to encrypt the data that is currently in *credentials.txt*.
To use another password, simply delete the data from *credentials.txt* and choose a password to encrypt and decrypt the data from now on.
Be sure you use the same password!

#  

# **Authors**

| NMEC  | Name              |                   Email  |
| ----- | ----------------- | -----------------------: |
| 98474 | João Reis         |       joaoreis16@ua.pt   |
| 98595 | Diogo Cruz        |         diogophc@ua.pt   |
| 98388 | Ricardo Rodriguez | ricardorodriguez@ua.pt   |
| 93310 | Gonçalo Pereira   |  pereira.goncalo@ua.pt   |
