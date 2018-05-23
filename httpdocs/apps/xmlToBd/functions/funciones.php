<?php
function detectarAddenda($rfc=''){
	if($rfc == 'DLI931201MI9')
		return 'Liverpool';
	return '';
}
function pintar($var,$type='var'){
	if($type== 'xml'){
		header("Content-type: text/xml");
		echo $var;
	}
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
function isNumberArray($array){
	if(!is_array($array))
		return FALSE;
	foreach(array_keys($array) as $key) {
		if (!is_int($key)) return FALSE;
	}
	return TRUE;
}
function load_in_data(){
	$in = array();
	$in['thisurl'] = '';
	foreach ($_GET as $key => $value) {
		if (substr(strtolower($key), 0, 4) == "chk:") {
			list ($aux, $name) = split(":", $key);
			$name = str_replace("_", " ", $name);
			if (array_key_exists(strtolower($value), $in)) {
				$in[strtolower($value)] .= "|$name";
			} else {
				$in[strtolower($value)] .= "$name";
			}
		} else {
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help') {
			$in['thisurl'] .= strtolower($key) . "=$value&";
		}
	}
	foreach ($_POST as $key => $value) {
		if (substr(strtolower($key), 0, 4) == "chk:") {
			list ($aux, $name) = split(":", $key);
			$name = str_replace("_", " ", $name);
			if (array_key_exists(strtolower($value), $in)) {
				$in[strtolower($value)] .= "|$name";
			} else {
				$in[strtolower($value)] .= "$name";
			}
		} else {
			$in[strtolower($key)] = $value;
		}
		if (strtolower($key) != 'help') {
			$in['thisurl'] .= strtolower($key) . "=$value&";
		}
	}
	$in['thisurl'] = substr($in['thisurl'],0,-1);
	return $in;
}
function load_sys_data($e = '') {
	$sys = array();
	$cfg = array();
	$cfg_folder = CFG_FOLDER;
	$local = PREFIX_CONFIG;
	if (file_exists($cfg_folder . "/general." . $local . ".cfg")) {
		if ($handle = fopen($cfg_folder . "/general." . $local . ".cfg", 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					list($type,$name,$value) = preg_split("/\||=/", $line, 3);
					if ($type == 'sys') {
						$sys[$name] = trim($value);
					} elseif ($type == 'conf' or $type == 'conf_local') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}
			}
		}
	}

	if (file_exists($cfg_folder . "/general." . $local . ".e" . $e . ".cfg")) {
		if ($handle = fopen($cfg_folder . "/general." . $local . ".e" . $e . ".cfg", 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					list($type, $name, $value) = preg_split("/\||=/", $line, 3);
					if ($type == 'sys') {
						$sys[$name] = trim($value);
					} elseif ($type == 'conf') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}

			}
		}
	}

	if (file_exists($cfg['cfg_dir'] . 'general.e' . $e . '.cfg')) {
		if ($handle = fopen($cfg['cfg_dir'] . 'general.e' . $e . '.cfg', 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					list($type, $name, $value) = preg_split("/\||=/", $line, 3);
					if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type == 'conf') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}
			}
		}
	}

	if (file_exists($cfg['cfg_dir'] . 'general.ex.cfg')) {            
		if ($handle = fopen($cfg['cfg_dir'] . 'general.ex.cfg', 'r')) {
			while (!feof($handle)) {
				$line = fgets($handle);
				if(strpos($line,'|') !== FALSE and $line[0] != '#'){
					list($type, $name, $value) = preg_split("/\||=/", $line, 3);
					if (($name == 'auth_logoff' ) and $type == 'conf') {
						$cfg[$name] = trim($value);
					}

					if (($name == 'gensessiontype' ) and $type == 'conf') {
						$cfg[$name] = trim($value);
					}
				}else{
					continue;
				}
			}
		}
	} 
	return array($sys, $cfg);
}
function format_price($num) {
	return ("$ " . number_format($num, 2));
}
function get_ip() {
	if (getenv('REMOTE_ADDR')) {
		return getenv('REMOTE_ADDR');
	} elseif (getenv('REMOTE_HOST')) {
		return getenv('REMOTE_HOST');
	} elseif (getenv('HTTP_CLIENT_IP')) {
		return getenv('HTTP_CLIENT_IP');
	} else {
		return "Unknown";
	}
}



function ConectFTP(){
	$connFTP=ftp_connect(SERVER,PORT); //Obtiene un manejador del Servidor FTP
	ftp_login($connFTP,USER,PASSWORD); //Se loguea al Servidor FTP
	ftp_pasv($connFTP,PASV); //Establece el modo de conexión
	return $connFTP; //Devuelve el manejador a la función
}

function UploadFile($LocalFile,$ServerFile){
	//Sube archivo de la maquina Cliente al Servidor (Comando PUT)
	$connFTP=ConectFTP(); //Obtiene un manejador y se conecta al Servidor FTP
	ftp_put($connFTP,$ServerFile,$LocalFile,FTP_BINARY); //Sube archivo al Servidor FTP en modo Binario
	ftp_quit($connFTP); //Cierra la conexion FTP
	usleep(LAGTIME);
}

function GetPath(){
	//Obriene ruta del directorio del Servidor FTP 
	$connFTP=ConectFTP(); //Obtiene un manejador y se conecta al Servidor FTP
	$Directorio=ftp_pwd($connFTP); //Devuelve ruta actual
	ftp_quit($connFTP); //Cierra la conexion FTP
	return $Directorio; //Devuelve la ruta a la función
}

function DeleteFile($File){
//Elimina un archivo del Servidor FTP
	$connFTP=ConectFTP();
	$Path=ftp_pwd($connFTP);
	ftp_delete($connFTP, $Path.$File);
}

function DownloadFile($ServerFile, $LocalFile){
//Descarga (copia) un archivo a la ruta local
	$connFTP=ConectFTP();
	ftp_get($connFTP, $LocalFile, $ServerFile, FTP_BINARY);
	ftp_quit($connFTP);
	usleep(LAGTIME);
}

function OpenFile($ServerFile){
//Abre un archivo
	$connFTP=ConectFTP();
	$Path=ftp_pwd($connFTP);
	$Size=ftp_size($connFTP,$ServerFile);
	ftp_quit($connFTP);
	if($Size>0){
		$File="ftp://".USER.":".PASSWORD."@".SERVER.$Path.$ServerFile;
		return header("location: ".$File);
	}else{return 0;}
}

function ListFiles($ServerPath="."){
//Enlista los archivos en la carpeta FTP
	$connFTP=ConectFTP();
	$Files=ftp_nlist($connFTP, $ServerPath);
	ftp_quit($connFTP);
	foreach($Files as $File){
		$linkFTP = "ftp://".USER.":".PASSWORD."@".SERVER.$ServerPath.$File;
		// if(is_dir($linkFTP)){
		// 	echo '['.$File.']'."<br />";
		// }else{
		echo '<a href="'.$linkFTP.'" target="_blank">'.$File."</a><br />";
		// }
	}
}

function ListFilesArray($ServerPath="."){
//Enlista los archivos en la carpeta FTP
	$connFTP=ConectFTP();
	$Files=ftp_nlist($connFTP, $ServerPath);
	ftp_quit($connFTP);
	$arrayFiles = array();
	$x = 0;
	foreach($Files as $File){
		$x++;
		$arrayFiles[$x] = $File;		
	}
	return $arrayFiles;
}

function SearchFile($FileName){
//Revisa si existe un archivo y devuelve su nombre
	$FileName=explode('/',$FileName);
	$tot_f=count($FileName)-1;
	if($tot_f>0){
		for($x=0; $x<$tot_f; $x++){
			$Path.=$FileName[$x].'/';
		}
		#$Path=$FileName[$tot_f-2].'/'.$FileName[$tot_f-1].'/';
	}else{$Path='.'; $tot_f=0;}
	if($Path=='/'){$Path='.';}
	$connFTP=ConectFTP();
	$Files=ftp_nlist($connFTP, $Path);
	ftp_quit($connFTP);	
	foreach($Files as $File){
		$Name=explode('/',$File);
		$Tot=count($Name)-1;
		if($Tot<0){$Tot=0;}
		if($Name[$Tot]==$FileName[$tot_f]){return true;}
	}
}

function ftp_get_recursive_paths($path = '/', $max_level = 0){
    $files = array();
    $connFTP=ConectFTP();
    if($max_level < 0) return $files;
    if($path !== '/' && $path[strlen($path) - 1] !== '/') $path .= '/';
    $files_list = ftp_nlist($connFTP, $path);
    
    foreach($files_list as $f){
        if($f !== '.' && $f !== '..' && $f !== $path){
            if(strpos($f, '.') === FALSE){
                $files[$f] = ftp_get_recursive_paths($f, $max_level-1);
            }else{
                $files[] = basename($f);
            }    
        }
    }
    
    return $files;
}

function ReWriteFile($ServerFile){
	if(SearchFile($ServerFile)){
		$connFTP=ConectFTP();
		$Path=ftp_pwd($connFTP);
		$File="ftp://".USER.":".PASSWORD."@".SERVER.$Path.$ServerFile;
		$Handle = fopen($File, 'rb');
		$Content = fread($Handle, filesize($File));		
		fclose($Handle);
		ftp_quit($connFTP);
	}
	return $Content;
}

function UrlFile($ServerFile){
//Abre un archivo
	$connFTP=ConectFTP();
	$Path=ftp_pwd($connFTP);
	$Size=ftp_size($connFTP,$ServerFile);
	ftp_quit($connFTP);
	if($Size>0){
		$File="ftp://".USER.":".PASSWORD."@".SERVER.$Path.$ServerFile;
		return $File;
	}else{return 0;}
}

function MoveFile($FileNameOrigin, $FileNameDestiny){
//Renombra y/o mueve archivo a otra ruta dentro del servidor FTP
	$connFTP=ConectFTP();
	ftp_rename($connFTP, $FileNameOrigin, $FileNameDestiny);
	ftp_quit($connFTP);
	#usleep(1000000);
}

function MakeDir($DirName){
//Crea un directorio dentro del servicor FTP
	$connFTP=ConectFTP();
	ftp_mkdir($connFTP, $DirName);
	ftp_quit($connFTP);
	usleep(LAGTIME);
}

function CheckFolder($FolderName){
//Verifica la existencia de un directorio dentro del servicor FTP
	#$connFTP=ConectFTP();
	#$Path=ftp_pwd($connFTP);
	#ftp_quit($connFTP);
	if(is_dir($Folder="ftp://".USER.":".PASSWORD."@".SERVER.$Path.$FolderName)){
		return 1;
	}else{
		return 0;
	}	
}