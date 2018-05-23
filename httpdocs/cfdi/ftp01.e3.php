<?
/**
*			Funciones para Conexión a Servidor FTP vía PHP
*@author	Oscar Maldonado
*
*/

/*Prueba local*
define("SERVER","172.20.20.26"); //IP o Nombre del Servidor
define("PORT",21); //Puerto
define("USER","ftp_test"); //Nombre de Usuario
define("PASSWORD","12345"); //Contraseña de acceso
define("PASV",true); //Activa modo pasivo
define("LAGTIME",100000); //Tiempo de espera para ejecutar otro comando
/**/

/**/
//Datos para conexión a carpeta donde se colocan los TXT para timbrado
define("SERVER","172.16.1.7"); //IP o Nombre del Servidor
define("PORT",21); //Puerto
define("USER","Ti_Port"); //Nombre de Usuario
define("PASSWORD","prnport13"); //Contraseña de acceso
define("PASV",true); //Activa modo pasivo
define("LAGTIME",100000); //Tiempo de espera para ejecutar otro comando
/**/

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

function ListFiles(){
//Enlista los archivos en la carpeta FTP
	$connFTP=ConectFTP();
	$Files=ftp_nlist($connFTP, ".");
	ftp_quit($connFTP);
	foreach($Files as $File){
		echo $File."<br />";
	}
}

function SearchFile($FileName){
//Revisa si existe un archivo y devuelve su nombre
	$connFTP=ConectFTP();
	$Files=ftp_nlist($connFTP, ".");
	ftp_quit($connFTP);
	foreach($Files as $File){
		$Name=explode('/',$File);
		if($Name[1]==$FileName){return true;}
	}
}

function ReWriteFile($ServerFile, $LocalFile){
	if(SearchFile($ServerFile)){
		$connFTP=ConectFTP();
		$Path=ftp_pwd($connFTP);
		$Handle = fopen($LocalFile, 'w');
		ftp_fget($connFTP, $Handle, $ServerFile, FTP_BINARY, 1);
		ftp_close($connFTP);
		fclose($Handle);
	}
}
?>