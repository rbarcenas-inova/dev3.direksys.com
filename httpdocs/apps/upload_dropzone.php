<?php
	ini_set('display_errors', '1');
	error_reporting(E_ALL);

	include('class.manageruploadfile.php');




	## Recibe el archivo.
	$manager_upload = new MangerUploadFile();
	$manager_upload->allow_file_type('csv');

	$manager_upload->storage_path = $_POST['path'].'/';
	$manager_upload->max_allowed_size = 10485760; // In Bytes
	#$manager_upload->naming('accounting_movements','numeric');
	$response = $manager_upload->get_file();
	

	# Si se recibio correctamente....
	if( $response['result'] ){
		echo( $response['file'] );
	}else{
		echo($response['response']);
	}
	