<?php
	class db_mysqli extends mysqli {

	    public function __construct($host, $usuario, $contraseña, $bd, $port) {

	    	if( empty($port) ){
	    		$port = 3306;
	    	}

	        parent::__construct($host, $usuario, $contraseña, $bd, $port);

	        if (mysqli_connect_error()) {
	            die('Error de Conexión (' . mysqli_connect_errno() . ') '. mysqli_connect_error());
	        }
	    }

	    public function query( $query_string ){

	    	$result = parent::query( $query_string );

	    	if($result){
	    		return $result;
	    	}else{
	    		die( "Error al ejecutar: ".$this->errno." | Query: ".$query_string);
	    	}

	    }

	}