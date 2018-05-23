<?php
	
	require("imageupload/functions.php");
    #########################################################
    #### INIT System Data
    #########################################################
    $in  = array();
    $va  = array();
    $trs = array();
    $usr = array();
    $sys = array();
    $cfg = array();
    $tpl = array();
    $cses= array();
    $error= array();
    $device=array();

    define('DATE_FORMAT_LONG', '%A %d %B, %Y');

    ######################################################
    ##### Configuration File
    ######################################################
    get_values();
    load_custom_data($in['e']);

    ######################################################
    ##### Save Note and file into DB
    ######################################################	

    // Conexion    	
	$conex = new mysqli($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw'], $cfg['dbi_db']);
	if ($conex->connect_errno) {
	    echo "MySQLi Error :: (" . $conex->connect_errno . ") " . $conex->connect_error;
	    exit();
	}

	$tbl_notes = substr($in['tbl'], 3);
	$sql = "SELECT content, extension FROM sl_notes_attached WHERE ID_notes_attached=".$in['id'].";";
	$rslt = $conex->query($sql);

	if( $rslt ){

		$data = $rslt->fetch_object();

        if( preg_match(str_replace(',', '|', $cfg['file_extensions_images']), $data->extension) === 1 ){
    		header("Content-type: image/".$data->extension."\n\n");
    		echo $data->content;
    		return;
        }elseif( $data->extension == 'pdf' ){
            header("Content-type: application/".$data->extension."\n\n");
            echo $data->content;
            return;
        }else{
            header("Content-Description: File Transfer");
            header("Content-Type: application/octet-stream; ");
            header("Content-Disposition: attachment; filename=file.".$data->extension);
            header("Content-Transfer-Encoding: binary");
            
            // agregar el contenido
            print_r($data->content);
        }

	}else{
		echo "MySQLi Error :: (" . $conex->errno . ") " . $conex->error;
		$conex->query("ROLLBACK;");
		exit();
	}

?>