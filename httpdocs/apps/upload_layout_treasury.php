<?php
	ini_set('display_errors', '1');
	ini_set('memory_limit','256M');
	error_reporting(E_ALL);

	include('upload_layout_treasury/class.manageruploadfile.php');
	include('upload_layout_treasury/class.BalanceSheet.php');
	include('upload_layout_treasury/class.BankLayoutStructure.php');
	include('php_excel_1.8.0/PHPExcel/IOFactory.php');
	include('upload_layout_treasury/config.php');
	include('upload_layout_treasury/class.db_mysqli.php');

	## Identifica la Empresa
	$e = $_POST['e'];
	$id_admin_users = $_POST['user'];

	## Establece conexión a BD
	$db	= new db_mysqli( $cfg['db_host_e'.$e ], $cfg['db_user_e'.$e], $cfg['db_pw_e'.$e], $cfg['db_name_e'.$e], '3306' );

	## Recibe el archivo
	$manager_upload = new MangerUploadFile();
	$manager_upload->max_allowed_size 	= $cfg['max_size'];
	$manager_upload->storage_path 		= $cfg['storage_path'].$e.$cfg['storage_path_post'];
	$manager_upload->allow_file_type( $cfg['allowed_file_extensions'] );
	$manager_upload->naming('layout_treasury', 'timestamp');

	$response = $manager_upload->get_file();


	## Si se recibio correctamente....
	if( $response['result'] ){

		## Lee el archivo y lo transpola a un array de arrays (filas x columnas)
		## Concatena el array obtenido de una pagina, con el de la pagina siguiente 
		$objPHPExcel_Reader = PHPExcel_IOFactory::createReaderForFile( $manager_upload->storage_path.$response['file'] );
		$objPHPExcel_Reader->setReadDataOnly(true);
		$objPHPExcel 		= $objPHPExcel_Reader->load($manager_upload->storage_path.$response['file']);
				

		$sheetData = array();
		$sheets = $objPHPExcel->getSheetNames();

		foreach ($sheets as $value) {
			$max_row	= $objPHPExcel->getSheetByName($value)->getHighestRow();
			$temp 		= $objPHPExcel->getSheetByName($value)->rangeToArray('A1:L'.$max_row);
			$sheetData 	= array_merge( $sheetData, $temp );			
		}
		
		$balance_sheet	= new BalanceSheet( $sheetData, $e, $id_admin_users, $db );

		if( $balance_sheet->identify_BankAccount() ){
			if( $result = $balance_sheet->storagePreview() ){
				echo $balance_sheet->inserted;
			}else{
				echo "Falló el proceso de almacenamiento.";
			}
		}else{
			echo "No se ha identificado el Banco de Origen";
		}

	}else{
		echo(var_dump($response));
	}
