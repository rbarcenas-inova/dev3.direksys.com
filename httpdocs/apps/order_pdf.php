<?php
	ini_set('display_errors', '1');
	error_reporting(E_ALL);

	include('class.manageruploadfile.php');

	## Recibe el archivo.
	$manager_upload = new MangerUploadFile();
	$manager_upload->allow_file_type('pdf');

    if( $_POST['e'] )
    {
    	$manager_upload->storage_path = '../../files/e'.$_POST['e'].'/orders_pdf/';
    	$manager_upload->max_allowed_size = 1048576; // In Bytes
    	$response = $manager_upload->get_file( $_POST['id_orders'].'.pdf' );
    }
	
	# Si se recibio correctamente....
	if( $response['result'] ){
		echo( $response['file'] );
	}else{
        switch ( $response['response'] ) {
            case 'invalid_file_type':
                echo "El tipo de archivo es incorrecto. Solo pueden ser archivos PDF.";
                break;
            
            default:
                echo $response['response'];
                break;
        }
		
	}
	