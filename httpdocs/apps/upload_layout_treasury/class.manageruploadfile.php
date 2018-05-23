<?php
	class mangeruploadfile{

		private $allowed_extensions = array();
		public $storage_path = null;
		public $max_allowed_size = null;
		private $name_treatment = null; // null = mismo nombre / timestamp = nombredefault+timestamp / numeric = nombredefault+numnero incremental
		private $default_name;

		public function allow_file_type($extensions)
		{
			$extensions = explode(',', $extensions);
			foreach ($extensions as &$value) {
				$value = strtolower( trim($value) );
			}
			$this->allowed_extensions = $extensions;
		}

		public function validate_file(){

			$err 		= 0;
			$str_errors = '';

			if( $_FILES['file']['name'] == "" ){	
				$err++;
				$str_errors = 'required';
			
			}else{
				$size 		= $_FILES['file']['size']; // In Bytes
				$file_name 	= $_FILES['file']['name'];
				$pos_ext 	= strrpos($file_name, '.');
				$file_ext 	= strtolower(substr($file_name, $pos_ext+1));

				if( $size > $this->max_allowed_size ){
					$err++;
					$str_errors = 'too_large';
				}
				
				if( !in_array($file_ext, $this->allowed_extensions) and count($this->allowed_extensions) > 0  ){
					$err++;
					$str_errors = 'invalid_file_type';
				}
				
				if( !is_uploaded_file($_FILES['file']['tmp_name']) ){
					$err++;
					$str_errors = 'wrong_upload_protocol';
				}

				if( is_null($this->name_treatment) and file_exists( $this->storage_path.$file_name ) ){
					$err++;
					$str_errors = 'file_already_upload';
				}

			}

			return array($err, $str_errors);
		}

		private function get_extension_file( $file_name ){
			$pos_ext 	= strrpos($file_name, '.');
			$file_ext 	= strtolower(substr($file_name, $pos_ext+1));
			return $file_ext;
		}

		public function naming( $name, $treatment ){

			$this->default_name 	= $name;
			$this->name_treatment 	= $treatment;
		}

		private function get_name(){
			
			$ext_file = $this->get_extension_file($_FILES['file']['name']);

			if( is_null($this->name_treatment) ){
				return $_FILES['file']['name'];

			}elseif( $this->name_treatment == 'timestamp' ){
					return $this->default_name.date('_Ymd_His').'.'.$ext_file;
	
			}elseif( $this->name_treatment == 'numeric' ){
				$list = '';
				$count = 0;
				foreach ( glob($this->storage_path.'*' ) as $nombre_fichero) { //$default_name.
					$pos = strrpos( $nombre_fichero, $this->default_name)+strlen($this->default_name);
					$lenght = (strlen( $ext_file )+1) * -1;
					$value = intval((substr( $nombre_fichero, $pos, $lenght )));
					if($count < $value){
						$count = $value;
					}
				}

				$count++;
				return $this->default_name.$count.'.'.$ext_file;
			}
		}

		public function get_file()
		{
			list($err, $str_errors) = $this->validate_file();

			if( $err > 0 ){
				return array('result'=>false, 'response'=>$str_errors);
			}else{
				if( !empty($this->storage_path) )
				{
					$file_name 	= $this->get_name();
					$path_file = $this->storage_path.$file_name;

					if( move_uploaded_file( $_FILES['file']['tmp_name'], $path_file) ){
						chmod($path_file, 0777);
						return array('result'=>true, 'file'=>$file_name);
					}else{
						return array('result'=>false, 'response'=>'unable_handle_file');
					}
				}
			}
		}

		public function get_path_temporal_file()
		{
			list($err, $str_errors) = $this->validate_file();

			if( $err > 0 ){
				return array('result'=>false, 'response'=>$str_errors);
			}else{
				if( $_FILES['file']['tmp_name'] ){
					return array('result'=>true, 'file'=>$_FILES['file']['tmp_name']);
				}else{
					return array('result'=>false, 'response'=>'unable_handle_file');
				}
			}
		}

		public function get_temporal_file_content()
		{
			list($err, $str_errors) = $this->validate_file();

			if( $err > 0 ){
				return array('result'=>false, 'response'=>$str_errors);
			}else{
				if( $_FILES['file']['tmp_name'] ){
					$content = base64_encode ( file_get_contents($_FILES['file']['tmp_name']) );
					return array('result'=>true, 'content'=>$content);
				}else{
					return array('result'=>false, 'response'=>'unable_handle_file');
				}
			}
		}


	}