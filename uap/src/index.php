<!DOCTYPE html>
<html>
  <head>
    <script src="uap.js"></script>
    <meta charset="UTF-8">
    <title>User Authentication Application</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
    <link rel="stylesheet" href="uap.css">
  </head>

  <body>
  <?php

    // {"mail": "admin", "pass": "admin"}
    $string = file_get_contents("credentials.json");  
    $autofill_mail = "";
    $autofill_pass = "";

    if ($string != null) {

      echo "entrou";

      $credential = json_decode($string, true);
      if ($credential === null) {
        echo "ERROR";
      }
      
      foreach ($credential as $u) {
        foreach ($u as $k => $v) {  
          if ($k === "mail") {
            $autofill_mail = $v;
          } else if ($k === "pass") {
            $autofill_pass = $v;
          }
        }
        break;
      }

    }
  ?>
    <form method="POST">
      <h1>Autenticação</h1>
      <hr/>
      <div class="formcontainer">
        <div class="container"></div>
          <label for="username"><strong>UsersID</strong></label>
          <input type="text" id="email" name="email" value=<?php echo $autofill_mail ?> required>
        </div>
        <div class="container">
          <label for="password"><strong>Password</strong></label>
          <input type="password" id="pass" name="pass" placeholder="Password" value=<?php echo $autofill_pass ?> required>
        </div>
        <button type="submit" name="bttn">Login</button>
      </div>

      <?php

        if (isset($_POST['bttn']) ) {

          $mail = $_POST['email'];

          $data = array(
            'email' => "'" .$mail. "'"
          );

          $curl = curl_init();
          $url = "http://localhost:5000/uap.php";
          curl_setopt($curl,CURLOPT_URL,$url);
          curl_setopt($curl,CURLOPT_POST, true);
          curl_setopt($curl,CURLOPT_POSTFIELDS, http_build_query($data));
          curl_setopt($curl,CURLOPT_RETURNTRANSFER, true);
          curl_setopt($curl,CURLOPT_CONNECTTIMEOUT ,10);
          curl_setopt($curl,CURLOPT_TIMEOUT, 30);
          $response = curl_exec($curl);
          echo $response;
          var_dump($response);  
          curl_close ($curl);


          // localmente
          $_ENV["mail"] = $mail;
          putenv('MAIL="'. $mail .'"');

        }
      ?>

    </form>
  </body>
</html>