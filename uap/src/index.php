<!DOCTYPE html>
<html>
  <head>
    <script src="uap.js"></script>
    <meta charset="UTF-8">
    <title>UAP</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
    <link rel="stylesheet" href="uap.css">
  </head>

  <body>
    <form onsubmit="return handleClick(this)">
      <h1>Chave de encriptação</h1>
      <hr/>
      <div class="formcontainer">
        <div class="container">
            <label for="username"><strong>Username</strong></label>
            <input type="text" id="email" name="email" placeholder="Email">
        </div>
        <h3>hwdwdaaaaaaaaaaaaaasssssssssssw3</h3>
        <div class="container">
            <label for="password"><strong>Password</strong></label>
            <hr>
            <input type="password" id="pass" name="pass" placeholder="Password" required>
        </div>
        <button type="submit" name="bttn">Login</button>
      </div>

      <?php 
          if (isset($_POST['bttn']) ) {
							
            $mail = mysqli_real_escape_string($conn, $_POST['email']);
            $pass = md5(mysqli_real_escape_string($conn, $_POST['pass']));

            // API URL
            $url = 'http://localhost:5000/';

            // Create a new cURL resource
            $ch = curl_init($url);

            // Setup request to send json via POST
            $data = array(
              'email' => "'" .$mail. "'",
              'password' => "'" .$pass. "'",
            );
            $payload = json_encode(array("user" => $data));

            // Attach encoded JSON string to the POST fields
            curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

            // Set the content type to application/json
            curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));

            // Return response instead of outputting
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

            // Execute the POST request
            $result = curl_exec($ch);

            // Close cURL resource
            curl_close($ch);

            echo "done";
          }
        ?>

    </form>
  </body>
</html>