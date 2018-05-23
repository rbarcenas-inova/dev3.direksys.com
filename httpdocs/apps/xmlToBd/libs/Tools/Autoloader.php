<?php
#Autoload Simple Clases Sueltas
function autoloadTools($clase){
    if(file_exists (__DIR__.'/classes/class.'.$clase . '.php'))
    	require_once(__DIR__.'/classes/class.'.$clase . '.php');
    elseif (file_exists(__DIR__.'/classes/'.$clase.'.php'))
    	require_once(__DIR__.'/classes/'.$clase . '.php');
}
spl_autoload_register('autoloadTools');
