<?
/**
*			Funciones para Conexión a Servidor FTP vía PHP
*@author	Oscar Maldonado
*
*/

//Datos para conexión a carpeta donde se reciben los XML y PDF con timbrado
// if($_SERVER['HTTP_HOST']=='mx.direksys.com'){
/*FTP Producción*/
	define("SERVER","172.16.1.23"); //IP o Nombre del Servidor
	define("PORT",21); //Puerto
	define("USER","EDX"); //Nombre de Usuario
	define("PASSWORD","F4cXmL.13#"); //Contraseña de acceso
	define("PASV",true); //Activa modo pasivo
	define("LAGTIME",100000); //Tiempo de espera para ejecutar otro comando
/**/
// }else{
// /*Prueba local*/
// 	define("SERVER","172.20.20.26"); //IP o Nombre del Servidor
// 	define("PORT",21); //Puerto
// 	define("USER","ftp_test"); //Nombre de Usuario
// 	define("PASSWORD","12345"); //Contraseña de acceso
// 	define("PASV",true); //Activa modo pasivo
// 	define("LAGTIME",100000); //Tiempo de espera para ejecutar otro comando
// /**/
// }
function ConectFTP(){
//Conexión Servidor FTP
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
	return 1;}else{return 0;}	
}
?>