<?php

// Include loader class
require_once __DIR__ . DIRECTORY_SEPARATOR . 'Autoloader.php';

// Register autoload
$cfdiMxAutoloader = new  cfdiMx\Autoloader();
$cfdiMxAutoloader->addIncludePath(__DIR__);
$cfdiMxAutoloader->register();
