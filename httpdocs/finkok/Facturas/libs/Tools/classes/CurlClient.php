<?php
class CurlClient{
	public static $config;
	public static $request;
	public static $errors;
	/**
	*	Params Array $config ( 
	*		method => 'post'
	*		url => ''
	*		params => array
	*		header => array
	*		auth => array ( type => 'basic' , user => ,password => )
	*		parseFrom => (xml,json)
	*	)
	*/
	public static function request($config = array()){
		if(count($config) > 0)
			self::$config = $config;
		else
			$config = self::$config;
		// exit;
		extract($config);
		if(!isset($method) || !isset($url))
			return FALSE;
		$curl = curl_init();
		curl_setopt($curl, CURLOPT_CUSTOMREQUEST,$method);
		// if(strtoupper($method) == 'POST'){
		// 	// curl_setopt($curl, CURLOPT_POST,TRUE );
		// }
		// else{
		// 	// curl_setopt($curl, CURLOPT_POST,FALSE );
		// }
		if(isset($header))
			curl_setopt($curl, CURLOPT_HTTPHEADER,$header);
		if(isset($auth)){
			extract($auth);
			if($type == 'ntlm')
				curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_NTLM);
			elseif($type == 'basic')
				curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
			else
				curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_ANY);
			curl_setopt($curl, CURLOPT_USERPWD, $user . ":" . $password);
		}
		curl_setopt($curl, CURLOPT_URL, $url );   
		curl_setopt($curl, CURLOPT_POSTFIELDS,$params);
		curl_setopt($curl, CURLOPT_CONNECTTIMEOUT, 40); 
		curl_setopt($curl, CURLOPT_TIMEOUT,        40); 
		curl_setopt($curl, CURLOPT_RETURNTRANSFER, TRUE );
		curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, FALSE);
		// curl_setopt($curl, CURLOPT_VERBOSE, TRUE );
		// curl_setopt($curl, CURLOPT_STDERR,$verbose = fopen('php://temp', 'rw+'));
		curl_setopt($curl, CURLOPT_FOLLOWLOCATION, TRUE);
		 // => TRUE,
		// var_dump(stream_get_contents($curl));
		$response = curl_exec($curl);
		self::$errors = curl_error($curl);
		self::$request = curl_getinfo($curl, CURLINFO_HEADER_OUT);//curl_getinfo($curl, CURLINFO_HEADER_OUT);
		// echo "Verbose information:\n", !rewind($verbose), stream_get_contents($verbose), "\n";
		curl_close($curl);
		if(isset($parseFrom)){
			if($parseFrom == 'json')
				return json_decode($response);
			elseif($parseFrom == 'xml')
				return self::parseResult($response);
			else
				return $response;
		}else{
			return $response;
		}

	}
	/**
	*	Basic xml parser for soap ONLY
	*/
	public static function parseResult($response){
		$xmlResponse = simplexml_load_string($response);
		$namespaces = $xmlResponse->getNamespaces(true);
		$res = json_decode(json_encode($xmlResponse->children($namespaces['soap'])->Body->children()));
		return $res;
	}
}