<!DOCTYPE html>
<html>
  <head>
    <script src="uap.js"></script>
    <meta charset="UTF-8">
    <title>UAP</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">
    <style>
      html, body {
      display: flex;
      justify-content: center;
      font-family: Roboto, Arial, sans-serif;
      font-size: 15px;
      }
      form {
      border: 5px solid #f1f1f1;
      }
      input[type=text]{
      width: 100%;
      padding: 16px 8px;
      margin: 8px 0;
      display: inline-block;
      border: 1px solid #ccc;
      box-sizing: border-box;
      }
      button {
      background-color: #8ebf42;
      color: white;
      padding: 14px 0;
      margin: 10px 0;
      border: none;
      cursor: grabbing;
      width: 100%;
      }
      h1 {
      text-align:center;
      font-size:18;
      }
      button:hover {
      opacity: 0.8;
      }
      .formcontainer {
      text-align: left;
      margin: 24px 50px 12px;
      }
      .container {
      padding: 16px 0;
      text-align:left;
      }
    </style>
  </head>
  <body>
    <form onsubmit="return handleClick(this)">
      <h1>Chave de encriptação</h1>
      <hr/>
      <div class="formcontainer">
        <div class="container">
            <label for="pass"><strong>Password</strong></label>
            <input type="text" placeholder="Password" name="pass" required>
        </div>
        <?php 
          echo "começar";
          $data = json_decode(file_get_contents('php://input'), true);
          echo $data;
        ?>
        <button type="submit">Login</button>
      </div>
    </form>
  </body>
</html>