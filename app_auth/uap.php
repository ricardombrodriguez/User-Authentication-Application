<?php
    include("connection.php");

    echo $_POST["email"];
    var_dump($_POST);

    $recieved_mail = $_POST['email'];

    $mail = mysqli_real_escape_string($conn, $recieved_mail);

    $query = "SELECT * FROM users WHERE email='".$mail."'";
    $result = mysqli_query($conn,$query);

    if (!$result){

        // enviar mensagem de erro ==> não existe nenhum user com o respetivo mail
        echo "<div class=\"container-login100-form-btn\" ><p style=\" color: red\">Wrong credentials. Try again.</p> </div>";

    } else {

        $current_user = mysqli_fetch_array($result);

        if ($current_user) {

            // criar desafio
            // enviar mensagem para a UAP: mensagem com desafio
            
        } 
    }


    
?>

