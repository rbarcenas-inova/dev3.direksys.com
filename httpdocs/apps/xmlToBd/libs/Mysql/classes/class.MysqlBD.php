<?php
class MysqlBD{
	protected static $server;
	protected static $user;
	protected static $pass;
	protected static $database;
	protected static $conexion=false;
	protected static $motor='mysql';
	protected static $n=0;
	public static $querys = array();
	public static function config($server=false, $user=false, $pass=false, $database=false,$motor='mysql') {
		self::$server = ($server) ? $server : Config::$server;
		self::$user = ($user) ? $user : Config::$user;
		self::$pass = ($pass) ? $pass : Config::$pass;
		self::$database = ($database) ? $database : Config::$bd;
		self::$motor=$motor;
		self::$conexion=self::conectar();
		self::$n=1;
	}
	public static function getConexion(){
		if(self::$n==0)
			self::config();
		return self::$conexion;
	}
	public static function conectar(){
		if(!self::$conexion){
			try{
				self::$conexion = new PDO(self::$motor.':host='.self::$server.';dbname='.self::$database, self::$user, self::$pass);
		  		self::$conexion->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		  		return self::$conexion;
		  	}catch(PDOException $e){
		  		echo $e->getMessage();
		  	}
		}else
			return self::$conexion;
	}
	public static function crear(Tabla $datos){
		if(self::$n==0)
			self::config();
		$query="insert into ";
		$origen=$datos->getDatos();
		$lastkey=array_keys($origen);
		foreach ($origen as $key => $value) {
			if($key=="tabla")
				$query.=$value.'(';
			else
				if($key==$lastkey[count($lastkey)-1])
					$query.=$key.')';
				else
					$query.=$key.',';
		}
		unset($origen['tabla']);
		$query.=" values(";
		for($i=0;$i<sizeof($origen);$i++)
			if($i==sizeof($origen)-1)
				$query.="?)";
			else
				$query.="?,";
		$queso=array();
		foreach ($origen as $value)
			$queso[]=$value;

		try{
			self::$querys[] = $query;
			$stmt =self::$conexion->prepare($query);
			$row=$stmt->execute($queso);
			return ($row == 1) ?  true : false;
		}catch(Exception $e){
			echo $e;
			echo $query;
			return false;
		}
	}
	public static function consultarTabla($tabla,$campos=[],$num=0,$l=0,$ll=0,$o=0,$co=0){
		if(self::$n==0)
			self::config();
		$orden= ($o==0)?'ASC':'DESC';
		if(empty($campos))
			$query='select * from '.$tabla;
		else
			$query = 'select '.implode(',',$campos).' from '.$tabla;
		$query.=($co!=0)? 'order by '.$co.' '.$orden : '';
		$query.=($l!=0) ? ' limit '.$l.','.$ll : '';
		$resultados=array();
		self::$querys[] = $query;
		try{
			$stmt =self::$conexion->query($query);
			$result = null;
			if($num==1)
				$result =  new Tabla($stmt->fetch(PDO::FETCH_ASSOC));
			$result =  new Tabla($stmt->fetchAll(PDO::FETCH_ASSOC));
			self::$conexion = null;
			return $result;
		}catch(PDOException $e){
			echo 'Error: ' . $e->getMessage();
			return false;
		}

 	}
 	/*
	*Params 
	array(
		'tabla'=>'',
		'campos'=>array()
		'from'=>array()
		'join'=>array()
		'where'=>array()
		'group'=>array()
		'order'=>array()
		
	)
	
 	*/
 	public static function select($params = array()){
		

 	}
	public static function consultarTablaF($tabla,$campos=array(),$filtros=array(),$num=0,$o=0,$co=0,$limit = 0){
		if(self::$n==0)
			self::config();
		$orden= ($o==0)? 'ASC':'DESC';
		if(empty($campos))
			$query='select * from '.$tabla;
		else
			$query = 'select '.implode(',',$campos).' from '.$tabla;
		$query='select * from '.$tabla;
		if(count($filtros)>0)
			$query.=' where ';
		$lastkey=array_keys($filtros);
		foreach ($filtros as $key => $value) {
			if($key==$lastkey[count($lastkey)-1]){
				if($value[0]=='!')
					$query.=$key.' != "'.substr($value,1).'" ';
				elseif($value[0]=='#')
					$query.=$key.' like "'.substr($value,1).'" ';
				elseif($value[0]=='>')
					$query.=$key.' > "'.substr($value,1).'" ';
				elseif($value[0]=='<')
					$query.=$key.' < "'.substr($value,1).'" ';
				elseif($value[0]=='>=')
					$query.=$key.' >= "'.substr($value,1).'" ';
				elseif($value[0]=='<=')
					$query.=$key.' <= "'.substr($value,1).'" ';
				else
					$query.=$key.' = "'.$value.'" ';
			}
			else{
				if($value[0]=='!')
					$query.=$key.' != "'.$value.'" and ';
				elseif($value[0]=='#')
					$query.=$key.' like "'.substr($value,1).'" and ';
				elseif($value[0]=='>')
					$query.=$key.' > "'.substr($value,1).'" and ';
				elseif($value[0]=='<')
					$query.=$key.' < "'.substr($value,1).'" and ';
				elseif($value[0]=='>=')
					$query.=$key.' >= "'.substr($value,1).'" and ';
				elseif($value[0]=='<=')
					$query.=$key.' <= "'.substr($value,1).'" and ';
				else
					$query.=$key.' = "'.$value.'" and ';
			}
		}
		$query.=($co!==0) ? ' order by '.$co.' '.$orden : '';
		if($limit > 0){
			$query.=' limit '.$limit;
		}
		$resultados=array();
		self::$querys[] = $query;
		try{
			$stmt =self::$conexion->query($query);
			$result = null;
			if($num==1)
				$result =  new Tabla($stmt->fetch(PDO::FETCH_ASSOC));
			$result =  new Tabla($stmt->fetchAll(PDO::FETCH_ASSOC));
			// self::$conexion = null;
			return $result;
		}catch(PDOException $e){
			echo $query;
			echo 'Error: ' . $e->getMessage();
			exit;
		}
 	}
	public static function guardar(Tabla $datos,$num=0){
		if(self::$n==0)
			self::config();
		$origens=$datos->getDatos();
		if(!isset($origens['where'])){
			$query="update ".$datos->tabla.' set ';
			$origen=$datos->getDatos();
			unset($origen['tabla']);
			$llave=array_keys($origen);
			$llave=array_shift($llave);
			$id=array_shift($origen);
			$lastkey=array_keys($origen);
			foreach ($origen as $key => $value)
				if($key==$lastkey[count($lastkey)-1])
					$query.=$key.'=?';
				else
					$query.=$key.'=?,';
			$query.=" where ".$llave.'=?';
			$queso=array();
			foreach ($origen as $value)
				$queso[]=$value;
			$queso[]=$id;
		}else{
			$query="update ".$datos->tabla.' set ';
			$origen=$datos->getDatos();
			$where=$datos->where;
			unset($origen['tabla']);
			unset($origen['where']);
			$llave=array_keys($origen);
			$llave=array_shift($llave);
			$lastkey=array_keys($origen);
			foreach ($origen as $key => $value)
				if($key==$lastkey[count($lastkey)-1])
					$query.=$key.'=?';
				else
					$query.=$key.'=?,';
			$queso=array();
			$lastkey=array_keys($where);
			$query.=" where ";
			foreach ($where as $key => $value) {
				if($key==$lastkey[count($lastkey)-1])
					$query.=$key.'=?';
				else
					$query.=$key.'=? and ';
			}
			foreach ($origen as $value)
				$queso[]=$value;
			foreach ($where as $value)
				$queso[]=$value;
		}
		//return $query;
		self::$querys[] = $query;
		try{
			$stmt =self::$conexion->prepare($query);
			$row=$stmt->execute($queso);
			return ($row >= 1) ?  true : false;
		}catch(Exception $e){
			echo $e;
			echo $query.'<br>';
			exit;
		}
	}
	// USELESS
	// public static function contarReg($tabla){
	// 	if(self::$n==0)
	// 		self::config();
	// 	return self::$conexion->query('select count(*) from '.$tabla)->fetchColumn();
	// }
	public static function selectQuery($query){
		if($query == '')
			return false;
		self::config();
		$result = new Tabla(self::$conexion->query($query)->fetchAll(PDO::FETCH_ASSOC));
		self::$conexion =null;
		return $result;
	}
	public static function executeQuery($query){
		if($query == '')
			return false;
		self::config();
		$result = self::$conexion->exec($query);
		self::$conexion =null;
		return $result;
	}
	public static function borrar(Tabla $datos){
 		if(self::$n==0)
			self::config();
		$origens=$datos->getDatos();
		if(!isset($origens['where']))
			return 'Error';
		$llave=array_keys($origens['where']);
		$query='delete from '.$datos->tabla.' where '.$llave[0].' = '.$origens['where'][$llave[0]];
		try{
			$row=self::$conexion->query($query);
			return ($row >= 1) ?  true : false;
		}catch(Exception $e){
			echo $e;
			echo $query.'<br>';
			exit;
		}
 	}
}
?>