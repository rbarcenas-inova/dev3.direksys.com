<?php
//  AUTOLADER PARA FUNCIONES
$allFiles = scandir(__DIR__);
foreach ($allFiles as $key => $value) {
	if(strpos($value,'.php') !== FALSE && $value!="AutoloaderFunc.php"){
		require_once __DIR__.DIRECTORY_SEPARATOR.$value;
	}
}

