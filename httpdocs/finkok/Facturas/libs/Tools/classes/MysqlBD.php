<?php
class MysqlBD{
	protected static $configConections;
	protected static $conexion=false;
	protected static $n;
	protected static $numberOfConections;
	protected static $motor='mysql';
	protected static $activeConection='Main';
	public static $querys = array();
	public static function config($name='Main', $server=false, $user=false, $pass=false, $database=false,$motor='mysql') {
		if(isset(Config::$connections)){
			if(is_array(self::$configConections))
				self::$configConections = array_merge(Config::$connections, self::$configConections);
			else
				self::$configConections = Config::$connections;
		}else{
			$config = array(
				'server'=>$server,
				'user'=>$user,
				'pass'=>$pass,
				'database'=>$bd
			);
			self::$configConections[$name] = $config;
		}
		self::$motor=$motor;
		self::$conexion[$name]=self::conectar($name);
		self::$n[$name]=1;
	}
	public static function addConnection($name, Array $config){
		self::$configConections[$name] = $config;
	}
	public static function setActiveConnection($name){
		self::$activeConection = $name;
	}
	public static function getConexion($name= 'Main'){
		if(isset(self::$n[$name])){
			if(self::$n[$name]==0)
				self::config($name);
			return self::$conexion[$name];
		}else{
			self::config($name);
			return self::$conexion[$name];
		}
	}
	public static function conectar($name = 'Main'){
		if(!isset(self::$conexion[$name])){
			try{

				self::$conexion[$name] = new PDO(self::$motor.':host='.self::$configConections[$name]['server'].';dbname='.self::$configConections[$name]['database'], self::$configConections[$name]['user'], self::$configConections[$name]['pass']);
		  		self::$conexion[$name]->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		  		// self::$conexion[$name]->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_OBJ);
		  		return self::$conexion[$name];
		  	}catch(PDOException $e){
		  		echo $e->getMessage();
		  	}
		}else
			return self::$conexion[$name];
	}
	public static function crear(Tabla $datos){
		self::getConexion(self::$activeConection);
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
			$stmt =self::$conexion[self::$activeConection]->prepare($query);
			$row=$stmt->execute($queso);
			return ($row == 1) ?  true : false;
		}catch(Exception $e){
			echo $e;
			echo $query;
			return false;
		}
	}
	public static function consultarTabla($tabla,$campos=[],$num=0,$l=0,$ll=0,$o=0,$co=0){
		self::getConexion(self::$activeConection);
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
			$stmt =self::$conexion[self::$activeConection]->query($query);
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
		self::getConexion(self::$activeConection);
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
			$stmt =self::$conexion[self::$activeConection]->query($query);
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
		self::getConexion(self::$activeConection);
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
			$stmt =self::$conexion[self::$activeConection]->prepare($query);
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
		self::$querys[] = $query;
		$result = new Tabla(self::$conexion[self::$activeConection]->query($query)->fetchAll(PDO::FETCH_ASSOC));
		// self::$conexion =null;
		return $result;
	}
	public static function executeQuery($query){
		if($query == '')
			return false;
		self::config();
		self::$querys[] = $query;
		$result = self::$conexion[self::$activeConection]->exec($query);
		// self::$conexion =null;
		return $result;
	}
	public static function borrar(Tabla $datos){
 		self::getConexion(self::$activeConection);
		$origens=$datos->getDatos();
		if(!isset($origens['where']))
			return 'Error';
		$llave=array_keys($origens['where']);
		$query='delete from '.$datos->tabla.' where '.$llave[0].' = '.$origens['where'][$llave[0]];
		try{
			$row=self::$conexion[self::$activeConection]->query($query);
			return ($row >= 1) ?  true : false;
		}catch(Exception $e){
			echo $e;
			echo $query.'<br>';
			exit;
		}
 	}
}
?>