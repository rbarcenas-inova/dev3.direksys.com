<?php
	class mangeruploadfile{

		public $allowed_extensions = array();
		public $storage_path = null;
		public $max_allowed_size = null;

		public function __construct( $allow_extensions,  $storage_path, $max_size )
		{
			$this->allow_file_type($allow_extensions);
			$this->storage_subdirectory($storage_path);
			$this->max_allowed_size = $max_size;
		}


		public function allow_file_type($extensions)
		{
			$extensions = explode(',', $extensions);
			foreach ($extensions as &$value) {
				$value = trim($value);
			}
			$this->allowed_extensions = $extensions;
		}


		public function storage_subdirectory($path)
		{
			$this->storage_path = $path;
		}



		public function validate_file(){

			$err 		= 0;
			$str_errors = '';

			if( $_FILES['file']['name'] == "" ){	
				$str_errors = 'required';
			}else{

				$size 		= $_FILES['file']['size'];
				$file_name 	= strtolower($_FILES['file']['name']);
				$pos_ext 	= strrpos($file_name, '.');
				$file_ext 	= substr($file_name, $pos_ext+1);

				
				if( $size > $this->max_allowed_size ){
					$str_errors = 'too_large';
				}
				elseif( !in_array($file_ext, $this->allowed_extensions) and count($this->allowed_extensions) > 0  ){
					$str_errors = 'invalid_file_type';
				}
				elseif( !is_uploaded_file($_FILES['file']['tmp_name']) ){
					$str_errors = 'wrong_upload_protocol';
				}
			}

			return array($err, $str_errors);

		}


		public function get_file()
		{

			list($err, $str_errors) = $this->validate_file();


			if( $err > 0 ){
				return array('result'=>false, 'response'=>$str_errors);
			}else{
				if( !empty($this->storage_path) )
				{
					$file_name 	= 'temp';
					$count 		= 0;

					while( file_exists($this->storage_path.$file_name.$count.'.'.$file_ext) ){
						$count++;
					}

					$path_file = $this->storage_path.$file_name.$count.'.'.$file_ext;

					if( move_uploaded_file( $_FILES['file']['tmp_name'], $path_file) ){
						chmod($path_file, 0777);
						return array('result'=>true, 'file'=>$file_name.$count.'.'.$file_ext);
					}else{
						return array('result'=>false, 'response'=>'unable_handle_file');
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