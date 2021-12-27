<?php

    declare(strict_types=1);

    //report only important errors (not warnings)
    error_reporting(E_ERROR | E_PARSE);

    include("connection.php");

    echo "AI AI AI ".$_POST;

    $received_mail = $_POST['email'];

    $mail = mysqli_real_escape_string($conn, $received_mail);

    $query = "SELECT * FROM users WHERE email='".$mail."'";
    $result = mysqli_query($conn,$query);

    if (!$result){

        // erro, n mostrar ao user que n existe nenhum user com esse mail porque isso é uma vulnerabilidade

    } else {

        $current_user = mysqli_fetch_array($result);

        if ($current_user) {






            $server = stream_socket_server('tcp://localhost:7181', $errno, $errstr);

            if ($server === false) {
                exit(1);
            }

            while (true) {

                $connection = stream_socket_accept($server, -1, $clientAddress);

                if ($connection) {

                    fwrite(STDERR, "Client [{$clientAddress}] connected \n");
                    while ($buffer = fread($connection, 2048)) {
                        if ($buffer !== '') {

                            fwrite($connection, "Server says: $buffer");
                        }
                    }

                    fclose($connection);
                }
            }


            




        } 
    }


    
?>

