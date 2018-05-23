<?php
require 'bootstrap.php';

$routes = require_once BASE . DIRECTORY_SEPARATOR .'routes.php';

$bootstrap = new Service\Framework\App($routes);

$bootstrap->init();
