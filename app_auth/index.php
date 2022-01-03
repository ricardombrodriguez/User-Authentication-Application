<?php 
session_start();
include("connection.php");
?>
<!DOCTYPE html>
<html lang="zxx">

<head>
    <meta charset="UTF-8">
    <meta name="description" content="Ogani Template">
    <meta name="keywords" content="Ogani, unica, creative, html">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Spoton</title>

    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@200;300;400;600;900&display=swap" rel="stylesheet">

    <!-- Css Styles -->
    <link rel="stylesheet" href="css/bootstrap.min.css" type="text/css">
    <link rel="stylesheet" href="css/font-awesome.min.css" type="text/css">
    <link rel="stylesheet" href="css/elegant-icons.css" type="text/css">
    <link rel="stylesheet" href="css/nice-select.css" type="text/css">
    <link rel="stylesheet" href="css/jquery-ui.min.css" type="text/css">
    <link rel="stylesheet" href="css/owl.carousel.min.css" type="text/css">
    <link rel="stylesheet" href="css/slicknav.min.css" type="text/css">
    <link rel="stylesheet" href="css/style.css" type="text/css">
    <link href='https://fonts.googleapis.com/css?family=Roboto:400,100,300,700' rel='stylesheet' type='text/css'>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
</head>

<body>

    <?php
    
    $result = $conn->query("SELECT * FROM trips") or die($conn->error);
    $token = $_GET['token'];

    $_SESSION['LOGGED'] = False;
    $hello_user = False;

    if (!empty($token)) {

        $query = "SELECT * from users where token='". $token ."'";
        $resultado = mysqli_query($conn,$query);
        $linha = mysqli_fetch_array($resultado);
        if ($linha) {
            $current_time = date(time());
            $user = strtoupper($linha["nome"]);

            if ( $current_time > $linha["expire_time"]) {
                $_SESSION['LOGGED'] = False;

            } else {
                if ($linha["token"] == $token) {
                    $_SESSION['LOGGED'] = True;

                } else {
                    $_SESSION['LOGGED'] = False;
                }
            }
        }

        if ($_SESSION['LOGGED']) {
            $_SESSION['user_id'] = $linha["id"] ;
        } else {
            $_SESSION['user_id'] = -1;
        }

        
    }

    ?>

    <!-- Page Preloder -->
    <div id="preloder">
        <div class="loader"></div>
    </div>

    <!-- Humberger Begin -->
    <div class="humberger__menu__overlay"></div>
    <div class="humberger__menu__wrapper">
        <div class="humberger__menu__logo">
            <a href="./index.php"><img src="img/logo.png" alt=""></a>
        </div>
        <div class="humberger__menu__cart">
            <ul>
                <li><a href="#"><i class="fa fa-heart"></i> <span>1</span></a></li>
                <li><a href="#"><i class="fa fa-shopping-bag"></i> <span>3</span></a></li>
            </ul>
        </div>
        <div class="humberger__menu__widget">
            <div class="header__top__right__language">
                <img src="img/language.png" alt="">
                <div>English</div>
                <span class="arrow_carrot-down"></span>
                <ul>
                    <li><a href="#">Spanis</a></li>
                    <li><a href="#">English</a></li>
                </ul>
            </div>
            <div class="header__top__right__auth">
                <a href="#"><i class="fa fa-user"></i> Login</a>
            </div>
        </div>
        <nav class="humberger__menu__nav mobile-menu">
            <ul>
                <li><a href="./index.php">Shop</a></li>
                <li><a href="./contact.php">Contact</a></li>
            </ul>
        </nav>
        <div id="mobile-menu-wrap"></div>
        <div class="header__top__right__social">
            <a href="#"><i class="fa fa-facebook"></i></a>
            <a href="#"><i class="fa fa-twitter"></i></a>
            <a href="#"><i class="fa fa-linkedin"></i></a>
            <a href="#"><i class="fa fa-pinterest-p"></i></a>
        </div>
        <div class="humberger__menu__contact">
            <ul>
                <li><i class="fa fa-envelope"></i> hello@colorlib.com</li>
                <li>Free Shipping for all Order of $99</li>
            </ul>
        </div>
    </div>
    <!-- Humberger End -->

    <!-- Header Section Begin -->
    <header class="header">
        <div class="container">
            <div class="row">
                <div class="col-lg-3">
                    <div class="header__logo" >
                        <a href="./index.php"><img src="img/logo.png" height="60px" alt=""></a>
                    </div>
                </div>
                <div class="col-lg-6">
                    <nav class="header__menu">
                        <ul>
                            <li class="active"><a href="./index.php">Shop</a></li>
                            <li><a href="./contact.php">Contact</a></li>
                        </ul>
                    </nav>
                </div>
                <div class="col-lg-3">
                    <div class="header__cart">
                        <ul>
                            <?php if ($_SESSION['LOGGED']): ?>

                            <form method='POST'>
                                <input type="hidden" id="logout" name="logout" value="">
                                <li><a href="./index.php" style="color: green"><i class="fa fa-sign-out"></i> Logout</a></li>
                            </form>
                            <?php else : ?>

                            <li>
                            <form action='http://localhost:5002/dns' method='POST'>
                                <input type="hidden" id="dns" name="dns" value="<?php echo "http://$_SERVER[HTTP_HOST]" ?>">
                                <input type="hidden" id="api_dns" name="api_dns" value="<?php echo "http://172.2.0.3:5001" ?>">
                                <i class="fa fa-sign-in"> </i><button type="submit" style="color: green; border: none; background: none; padding: 0;"> Login</a>
                            </form>
                            </li>
                            <?php endif; ?>

                            <li><a href="./shoping-cart.php" style="color: green"><i class="fa fa-shopping-cart"></i> Shopping Cart</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="humberger__open">
                <i class="fa fa-bars"></i>
            </div>
        </div>
    </header>
    <!-- Header Section End -->


    <!-- Hero Section Begin -->
    <section class="hero">
        <div class="container">
            <div class="row">
                <div class="col-lg-12">
                    <div class="hero__item set-bg" data-setbg="img/banner/travel_HD.jpg">
                        <div class="hero__text">
                            <?php if ($_SESSION["LOGGED"]): ?>
                            <h4 style="	font-size: 14px;text-transform: uppercase;font-weight: 700;letter-spacing: 4px;color: #252525;">WELCOME <?php echo $user; ?></h4>
                            <?php else : ?>
                            <span>TRAVEL AGENCY</span>
                            <?php endif; ?>
                            <h2>Travel <br />with pleasure.</h2>
                            <p>The best choice for your trips.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <!-- Hero Section End -->

     <!-- Hero Section Begin -->
     <section class="hero hero-normal">
        <div class="container">
            <div class="row">
                <div class="col-lg-12">
                    <div class="hero__search" id="inner">
                        <div class="hero__search__form">
                            <form method="GET">
                                <input type="text" placeholder="Where do you want to travel?" name="searchitem">
                                <button type="submit" class="site-btn" style="text-align: center;" name="searchbtn">SEARCH</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <!-- Hero Section End -->

    <!-- Product table  -->
    <section class="ftco-section">
		<div class="container">
			<div class="row">
				<div class="col-md-12">
					<div class="table-wrap">
						<table class="table">
					    <thead class="thead-primary">
					      <tr>
					        <th>Trip</th>
					        <th>Location</th>
					        <th>Price</th>
                            <th>Score</th>
					        <th>Details</th>
					      </tr>
					    </thead>
					    <tbody>
                        <?php

                        if (isset($_GET["searchitem"])) {
                            
                            $search = mysqli_real_escape_string($conn, $_GET["searchitem"]);
                            $q = "SELECT * from trips where lugar like '%".$search."%'";
                            $result = mysqli_query($conn,$q);

                            if (!$result){
                                echo("</table></div>".mysqli_error($conn));

                            }
                        }

                        foreach($result as $row): ?>
                            <tr>
                                <form method="POST" name="trip" action="shop-details.php">
                                    <td class="border-bottom-0" value="<?= $row['nome'] ?>"><?php echo $row['nome']; ?></td>
                                    <td class="border-bottom-0" value="<?= $row['lugar'] ?>"><?php echo $row['lugar']; ?></td>
                                    <td class="border-bottom-0" value="<?= $row['preco'] ?>"><?php echo $row['preco']; ?></td>
                                    <td class="border-bottom-0"><?php echo $row['avaliacao']; ?></td>
                                    <td class="border-bottom-0">
                                        <input type="hidden" name="nome" value="<?= $row['nome'] ?>" />
                                        <input type="hidden" name="preco" value="<?= $row['preco'] ?>" />
                                        <input type="hidden" name="lugar" value="<?= $row['lugar'] ?>" />
                                        <input type="hidden" name="avaliacao" value="<?= $row['avaliacao'] ?>" />
                                        <input type="hidden" name="descricao" value="<?= $row['descricao'] ?>" />
                                        <input type="hidden" name="trip_id" value="<?= $row['id'] ?>" />
                                        <button type="submit" class="btn btn-primary" style="text-align: center;" name="see_more">Details</button>
                                    </td>
                                </form>
					        </tr>

                            
                        <?php endforeach; ?>
					    </tbody>
					  </table>
					</div>
				</div>
			</div>
		</div>
	</section>
    <!-- Product table end  -->

    <!-- Js Plugins -->
    <script src="js/jquery-3.3.1.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/jquery.nice-select.min.js"></script>
    <script src="js/jquery-ui.min.js"></script>
    <script src="js/jquery.slicknav.js"></script>
    <script src="js/mixitup.min.js"></script>
    <script src="js/owl.carousel.min.js"></script>
    <script src="js/main.js"></script>



</body>
</html>