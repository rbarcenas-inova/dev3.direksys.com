<?php
namespace Service\Tools;

class Config{
	////Configuracion Base Datos/////
	private static $all = array();
	public static $connections;
	public static function init(){
		if(file_exists(CONFIG_FILE)){
			$cfg = parse_ini_file(CONFIG_FILE, 1);
		}else{
			exit('<b>Error: </b>Debe existir un archivo de configuración');
		}
		foreach ($cfg as $key => $value) {
			self::$all[ucfirst($key)] = $value;
		}
	}
	public static function __callStatic($method, $parameters = []){
		if(count(self::$all) == 0){
			self::init();
		}
		if(count($parameters) > 1){
			return null;
		}
		if(count(self::$all) > 0){
			if (preg_match('/^get(.*)?/i', $method)) {
				preg_match(
					'/^get(.*)?/i',
		    		$method, 
		    		$coincidencias
		    	);
    			// Support Direksys Config General var global cfg
				if($GLOBALS['cfg']){
					if($coincidencias[1] == 'Direksys'){
						if(count($parameters) == 0){
							return (object)$GLOBALS['cfg'];
						}else{
							if(count($parameters) == 1){
								if(isset($GLOBALS['cfg'][$parameters[0]]))
									return $GLOBALS['cfg'][$parameters[0]];
								else{
									$keys = preg_grep("/^".$parameters[0]."/", array_keys($GLOBALS['cfg']));
									$matchedKeys = [];
									foreach ($keys as $key) {
										$matchedKeys[$key] = $GLOBALS['cfg'][$key];
									}
									return (object)$matchedKeys;
								}
							}
						}
					}else{
						if($coincidencias[1] == 'Databases' && count($parameters) == 0){
				    		$parameters = [self::$all['Application']['default_database']];
				    	}
				    	if(count($parameters) == 0 )
							return (object)self::$all[$coincidencias[1]];
						if(is_array(self::$all[$coincidencias[1]][$parameters[0]]))
							return (object)self::$all[$coincidencias[1]][$parameters[0]];
						return self::$all[$coincidencias[1]][$parameters[0]];
					}
				}else{
			    	if($coincidencias[1] == 'Databases' && count($parameters) == 0){
			    		$parameters = [self::$all['Application']['default_database']];
			    	}
			    	if(count($parameters) == 0 )
						return (object)self::$all[$coincidencias[1]];
					if(is_array(self::$all[$coincidencias[1]][$parameters[0]]))
						return (object)self::$all[$coincidencias[1]][$parameters[0]];
					return self::$all[$coincidencias[1]][$parameters[0]];
				}
			} else {
				return null;
			}
		}else{
			return null;
		}
	}
}