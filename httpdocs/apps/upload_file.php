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

    //--------------------------------
    // Validacion
    //--------------------------------
    $err = 0;
    $str_errors = '';
    // Type
    if( !isset($in{'notestype'}) ){
    	$str_errors .= '&notestype=required';
    	$err++;
    }
    // Notes
    if( $in{'notestxt'} == '' ){    	
    	$str_errors .= '&notestxt=required';
    	$err++;
    }
    // File
    $file_ext = '';
    if($_FILES['file_attached']['name'] == ""){	
    	$str_errors .= '&file_attached=required';
    	$err++;
    }else{
    	$size = $_FILES['file_attached']['size'];
    	$file_name = strtolower($_FILES['file_attached']['name']);
        $pos_ext = strrpos($file_name, '.');
        $file_ext = substr($file_name, $pos_ext+1);

    	$file_types = explode(',', $cfg['upload_allowed_file_extensions']);
    	if( $size > 1000000 ){// Casi 1MB
    		$str_errors .= '&file_attached=invalid';
    		$err++;
    	}elseif( !in_array($file_ext, $file_types) ){
    		$str_errors .= '&file_attached=invalid';
    		$err++;
    	}
    }

    if( $err == 0 ){

    	// Conexion    	
		$conex = new mysqli($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw'], $cfg['dbi_db']);
		if ($conex->connect_errno) {
		    echo "MySQLi Error :: (" . $conex->connect_errno . ") " . $conex->connect_error;
		    exit();
		}

		//Inicializa la transaccion
		$conex->query("START TRANSACTION;");

		$tbl_notes = substr($in['tbl'], 3);
		$sql = "INSERT INTO sl_".$tbl_notes."_notes SET 
					ID_".$tbl_notes." = ".$in['view'].", 
					Notes = '".$in['notestxt']."',
					Type = '".$in['notestype']."', 
					Date = CURDATE(),
					Time = CURTIME(),
					ID_admin_users = ".$in['id_admin_users'].";";
		$rslt = $conex->query($sql);

		if( $rslt ){

			$new_id_notes = $conex->insert_id;

		    $file_tmp = null;			
			$file_tmp = addslashes(file_get_contents($_FILES['file_attached']['tmp_name']));			
            
			$sql = "INSERT INTO sl_notes_attached(ID_table_notes, table_notes, content, extension, Date, Time, ID_admin_users) 
					VALUES(".$new_id_notes.", 'sl_".$tbl_notes."_notes', '".$file_tmp."', '".$file_ext."', CURDATE(), CURTIME(), ".$in['id_admin_users'].");";
			$rslt = $conex->query($sql);
			if( !$rslt ){
				echo "MySQLi Error :: (" . $conex->errno . ") " . $conex->error."<br >".$sql;
				$conex->query("ROLLBACK;");
				exit();
			}

			$conex->query("COMMIT;");

			header("Location: /cgi-bin/common/apps/schid?cmd=add_notes_attached&cmdmain=".$in['cmdmain']."&tbl=".$in['tbl']."&view=".$in['view']."&tab=".$in['tab']."&rslt=1");

		}else{
			echo "MySQLi Error :: (" . $conex->errno . ") " . $conex->error;
			$conex->query("ROLLBACK;");
			exit();
		}

	}else{
		header("Location: /cgi-bin/common/apps/schid?cmd=add_notes_attached&cmdmain=".$in['cmdmain']."&tbl=".$in['tbl']."&view=".$in['view']."&tab=".$in['tab']."&error=1".$str_errors);
	}

?>