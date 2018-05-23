<?php
	#ini_set('display_errors', '1');
	#error_reporting(E_ALL);

	include('upload_picture/class.manageruploadfile.php');

	$cfg = array(
					'allowed_file_extensions' 	=> 'jpg',
					'max_size'					=> 10485760,
				);

	## Recibe el archivo.
	$manager_upload = new MangerUploadFile( $cfg['allowed_file_extensions'], null, $cfg['max_size'] );
	$response = $manager_upload->get_temporal_file_content();


	## Si se recibio correctamente....
	if( $response['result'] ){
		echo( $response['content'] );
	}else{
		echo('error');
	}

