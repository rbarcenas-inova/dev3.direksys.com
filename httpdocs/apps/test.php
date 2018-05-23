<?php
extract($_GET, EXTR_PREFIX_ALL, "v");
#extract($_POST, EXTR_PREFIX_ALL, "v");
$opt=getopt("txt:");
#print ($opt['e'].'a');
$content = $opt['txt']."\r\n".date('Y-m-d H:i:s');
if($v_txt || $opt['txt']){
	if($_SERVER['HTTP_HOST']=='mx.direksys.com'){		
		$fp = fopen("/home/www/domains/direksys.com/files/f".date('Ymd_His').".txt","w+");
	}else{
		$fp = fopen("/home/www/domains/dev.omaldonado/dev2.direksys.com/files/f".date('Ymd_His').".txt","w+");
	}
	fwrite($fp,$content);
	fclose($fp);
	$msj="<br/> \r\n Archivo creado.";
}
echo $content.$msj.'<br/>';
echo $_SERVER['HTTP_HOST'];
?>