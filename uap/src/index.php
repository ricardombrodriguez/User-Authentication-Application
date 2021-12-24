<!DOCTYPE html>
<html>
  <head>
    <script src="uap.js"></script>
    <meta charset="UTF-8">
    <title>User Authentication Pa</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
    <link rel="stylesheet" href="uap.css">
  </head>

  <body>
    <form method="POST">
      <h1>Autenticação</h1>
      <hr/>
      <div class="formcontainer">
        <div class="container">
          <label for="username"><strong>UsersID</strong></label>
          <input type="text" id="email" name="email" placeholder="Email">
        </div>
        <div class="container">
          <label for="password"><strong>Password</strong></label>
          <input type="password" id="pass" name="pass" placeholder="Password" required>
        </div>
        <button type="submit" name="bttn">Login</button>
      </div>

      <?php 
          if (isset($_POST['bttn']) ) {

            $mail = $_POST['email'];

            // API URL
            $url = 'https://host.docker.internal:5000/uap.php';

            $data = array(
              'email' => "'" .$mail. "'"
            );

            
            // use key 'http' even if you send the request to https://...
            $options = array(
                'http' => array(
                    'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
                    'method'  => 'POST',
                    'content' => http_build_query($data)
                )
            );
            $context  = stream_context_create($options);
            $result = file_get_contents($url, false, $context);
            if ($result === FALSE) { 
              echo "not connected";
            } else {
              echo "connected!";
            }
            var_dump($result);

          }
        ?>

    </form>
  </body>
</html>