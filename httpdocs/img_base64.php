<?php
// ini_set('display_errors', 1);
//             ini_set('display_startup_errors', 1);
//             error_reporting(E_ALL);
	
	$bytesCodificados = base64_encode(file_get_contents("sitimages/default/e14.png"));
	echo $bytesCodificados;
?>