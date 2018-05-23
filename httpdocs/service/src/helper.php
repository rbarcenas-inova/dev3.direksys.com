<?php

function parseConsoleArg($argv) {
    $_ARG = array();
    foreach ($argv as $arg) {
		if (preg_match('/--([^=]+)=(.*)/',$arg,$reg)) {
			$_ARG[$reg[1]] = $reg[2];
		} elseif(preg_match('/-([a-zA-Z0-9]+)/',$arg,$reg)) {
			foreach (str_split($reg[1]) as $char) {
				if(is_numeric($char))
					$_ARG[] = $char;
				else
					$_ARG[$char] = 'true';
			}
		} else {
			$_ARG[] = $arg;
		}
	}
	return $_ARG;
}

function logg($data='',$fileName= 'log'){
	$handle = fopen($fileName,'a');
	fwrite($handle,$data.', '.date('Y-m-d @ H:i:s').PHP_EOL);
	fclose($handle);
}

function clearArray($matriz){
	foreach($matriz as $key=>$value){
		$matriz[$key] = limpiar($value);
	}
	return $matriz;
} 

function limpiar($String){
	$String = utf8_encode($String);
    $String = str_replace(array('á','à','â','ã','ª','ä'),"a",$String);
    $String = str_replace(array('Á','À','Â','Ã','Ä'),"A",$String);
    $String = str_replace(array('Í','Ì','Î','Ï'),"I",$String);
    $String = str_replace(array('í','ì','î','ï'),"i",$String);
    $String = str_replace(array('é','è','ê','ë'),"e",$String);
    $String = str_replace(array('É','È','Ê','Ë'),"E",$String);
    $String = str_replace(array('ó','ò','ô','õ','ö','º'),"o",$String);
    $String = str_replace(array('Ó','Ò','Ô','Õ','Ö'),"O",$String);
    $String = str_replace(array('ú','ù','û','ü'),"u",$String);
    $String = str_replace(array('Ú','Ù','Û','Ü'),"U",$String);
    $String = str_replace(array('[','^','´','`','¨','~',']'),"",$String);
    $String = str_replace("ç","c",$String);
    $String = str_replace("Ç","C",$String);
    $String = str_replace("ñ","n",$String);
    $String = str_replace("Ñ","N",$String);
    $String = str_replace("Ý","Y",$String);
    $String = str_replace("ý","y",$String);
     
    $String = str_replace("&aacute;","a",$String);
    $String = str_replace("&Aacute;","A",$String);
    $String = str_replace("&eacute;","e",$String);
    $String = str_replace("&Eacute;","E",$String);
    $String = str_replace("&iacute;","i",$String);
    $String = str_replace("&Iacute;","I",$String);
    $String = str_replace("&oacute;","o",$String);
    $String = str_replace("&Oacute;","O",$String);
    $String = str_replace("&uacute;","u",$String);
    $String = str_replace("&Uacute;","U",$String);
    return $String;
}

function show($var,$type='var'){
	if(DEBUG){
		echo '<pre style="width: 95%; background: yellow none repeat scroll 0% 0%; font-weight: bold; padding: 27px; white-space: pre-wrap;">';
		if($type == 'var'){
			print_r(@$var);
		}elseif ($type == 'xml' || $type == 'html') {
			echo htmlentities($var);
		}
		echo '</pre>';
	}
}

function load_in(){
	return array_merge($_GET, $_POST, $_FILES);
}
function load_e_value($default){
	global $cli, $in, $argv;
	$e = $default;
	if(PHP_SAPI == 'cli'){
	    $cli = parseConsoleArg($argv);
	    if(isset($cli['e']))
	        $e = $cli['e'];
	}elseif (isset($_GET['e'])) {
	    $e = $_GET['e'];
	    setcookie('e', $e);
	    setcookie('e', $e, 0, "/finkok/Facturas/");
	    setcookie('e', $e, 0, "/finkok/");
	    setcookie('e', $e, 0, "/");
	} elseif (isset($in['e'])) {
	    $e = $in['e'];
	    setcookie('e', $e);
	    setcookie('e', $e, 0, "/finkok/Facturas/");
	    setcookie('e', $e, 0, "/finkok/");
	    setcookie('e', $e, 0, "/");
	} elseif (isset($_COOKIE['e']))
	    $e = $_COOKIE['e'];
	
	return $e;
}
function load_sys_data_helper($e = '') {
	$sys = array();
	$cfg = array();
	$cfg_folder = CFG_FOLDER;
	$local = PREFIX_CONFIG;
	$config_files = [$cfg_folder . '/general.ex.cfg'];
	if($e != '')
		$config_files[] = $cfg_folder . '/general.e'. $e . '.cfg';
	foreach ($config_files as $filename) {
		if(file_exists($filename)){
			$handle = fopen($filename, 'r');
			while(!feof($handle)){
				$line = fgets($handle);
				if(strpos($line, '|') !== FALSE && $line[0] != '#'){
					list($type, $name, $value) = array_pad(preg_split("/\||=/", $line, 3), 3, null);
					$cfg[$name] = trim($value);
				}
			}
		}
	}

	return $cfg;
}
