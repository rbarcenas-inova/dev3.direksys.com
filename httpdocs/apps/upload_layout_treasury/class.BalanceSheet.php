<?php
	class BalanceSheet{

		private $db;

		public $data;
		public $e;
		public $id_admin_users;
		public $bank;
		public $account;
		public $bankLayout;
		public $inserted;

		public function __construct($sheetData, $empresa, $id_admin_users, $db)
		{
			global $cfg;

			$this->data 			= $sheetData;
			$this->e 				= $empresa;
			$this->id_admin_users 	= $id_admin_users;
			$this->bankLayout		= new BankLayoutStructure( $db );
			$this->db 				= $db;
		}

		public function identify_BankAccount()
		{
			$response = false;

			foreach ( $this->bankLayout->registered_BankAccounts as $key => $accounts_num )
			{
				foreach ( $accounts_num as $value )
				{
					## Busca en el Area comprendida desde la Fila 1 / Columna 0 hasta la Fila 4 / Columna 4 
					if( $found = $this->searchInArea( 0, 0, 4, 4, $value ) )
					{
						$this->bankLayout->setByAccount( $value );
						$response = true;
						break 2;
					}
				}
			}

			if( $response ){
				$this->bank 	= $this->bankLayout->bank;
				$this->account 	= $this->bankLayout->account;
			}

			return $response;
		}

		public function searchInArea( $up, $left, $down, $right, $regex )
		{

			$regex = preg_replace('/\//','\/', $regex);
			$regex = '/'.$regex.'/';

			for( $row=$up; $row<=$down; $row++ )
			{
				$in_area = false;
				foreach ($this->data[$row] as $col => $value)
				{
					$value = preg_replace('/\s+/', ' ', $value);  
					
					if($col==$left) $in_area = true;

					if( $in_area )
					{
						if( preg_match( $regex, $value ) )
						{
							return array($value, $row, $col);
						}
					}
					
					if($col==$right) break;
				}
			}
			return false;
		}

		public function storagePreview()
		{
			global $cfg;

			$col 		= $this->bankLayout->getColumnRelation();
			$date_formats		= $this->bankLayout->getFormatDate();

			## Cuenta cuantos registros existe antes de la inserción
			$count = $this->db->query( "SELECT COUNT(*) quantity FROM sl_treasury_review WHERE ID_admin_users = $this->id_admin_users" );
			$data =	$count->fetch_array(MYSQLI_ASSOC);
			$qty_before = $data['quantity']; 


			$group_values = array();

			$titles = $this->bankLayout->positionTitles();
			$row = $titles['row'] + 1;
			

			for (; isset($this->data[$row]); $row++) 
			{ 
				unset($date_bank);

				//La primer celda de la fila  data[$row][0]  es la fecha en los estados de la cuenta de cualquier banco por lo que:
				// - Si esta vacia se descarta esa fila
				if( trim( $this->data[$row][ $col['date_bank'] ]) == '' ){
					continue;
				}

				// - Si el valor no es numerico posiblemente tenga un formato de fecha, 
				// valor que es probado para verificar si es posible extraer una fecha. De no serlo se omite esta fila
				#echo $this->data[$row][$col['date_bank']]."\n";


				if( !is_numeric($this->data[$row][ $col['date_bank'] ]) ){
					foreach ($date_formats as $format) {
						$date_bank = DateTime::createFromFormat($format, trim($this->data[$row][ $col['date_bank'] ]));
						if( $date_bank != false) 
							break;
					}

					if($date_bank == false){
						#die('No es numero y no es fecha:'. $this->data[$row][ $col['date_bank'] ]);
						continue;
					}
				}


				$hash = '';
				foreach( $this->data[$row] as $column => $cell)
				{

					if( $column == $col['deposit'] || $column == $col['retirement'] || $column == $col['balance'])
					{
						$this->data[$row][$column] = sprintf('%.2f',$cell);
						$hash .= sprintf('%.2f',$cell);

					}elseif( in_array( $column, $col, true) ){
						$hash .= strval($cell);

					}

				}

				$values = '(';	
				$values .= "MD5('".$hash."'),";											# HASH PARA IDENTIFICACIÓN UNICA
				$values .= "'".$this->bank."',";										# bank
				$values .= "'".$this->account."',";										# cuenta

				if( isset($date_bank) && $date_bank != false) 
					$values .= "'".date_format($date_bank, 'Y-m-d')."',";													
				else
					$values .= " DATE_ADD('1900-01-01', INTERVAL (".$this->data[$row][ $col['date_bank'] ]."-2) DAY ),";		
				
				$values .= ( is_null($col['branch_office']) )? 		"''," : "'".trim($this->data[$row][ $col['branch_office'] ])."',";
				$values .= ( is_null($col['description_1']) )? 		"''," : "'".trim($this->data[$row][ $col['description_1'] ])."',";
				$values .= ( is_null($col['description_2']) )? 		"''," : "'".trim($this->data[$row][ $col['description_2'] ])."',";
				$values .= ( is_null($col['description_3']) )? 		"''," : "'".trim($this->data[$row][ $col['description_3'] ])."',";
				$values .= ( is_null($col['reference']) )?			"''," : "'".trim($this->data[$row][ $col['reference'] ])."',";
				$values .= ( is_null($col['external_reference']) )?	"''," : "'".trim($this->data[$row][ $col['external_reference'] ])."',";
				$values .= ( is_null($col['legend_reference']) )?	"''," : "'".trim($this->data[$row][ $col['legend_reference'] ])."',";	
				$values .= ( is_null($col['numerical_reference']) )?"''," : "'".trim($this->data[$row][ $col['numerical_reference'] ])."',";
				$values .= ( is_null($col['transaction_code']) )?	"''," : "'".trim($this->data[$row][ $col['transaction_code'] ])."',";
				$values .= ( is_null($col['movement']) )?			"''," : "'".trim($this->data[$row][ $col['movement'] ])."',";
				$values .= ( is_null($col['deposit']) )?			"''," : "'".trim($this->data[$row][ $col['deposit'] ])."',";
				$values .= ( is_null($col['retirement']) )?			"''," : "'".trim($this->data[$row][ $col['retirement'] ])."',";
				$values .= ( is_null($col['balance']) )?			"''," : "'".trim($this->data[$row][ $col['balance'] ])."',";	
				$values .= "'".date('Y-m-d')."',";										# date
				$values .= "'".date('H:i:s')."',";										# time
				$values .= "'".$this->id_admin_users."'";								# ID_admin_users
				$values .= ')';

				$group_values[] = $values;
				
			}

			## Prepara el query.
			
			
			$query_init = "INSERT IGNORE INTO sl_treasury_review ( hash, bank, cuenta, date_bank, branch_office, description_1, description_2, description_3, reference, external_reference, legend_reference, numerical_reference, transaction_code, movement, deposit, retirement, balance, date, time, ID_admin_users) VALUES ";
			$query_init .= implode(',', $group_values).';';


			$query_init = mb_convert_encoding($query_init, 'ISO-8859-1', 'UTF-8');
			$result = $this->db->query( $query_init );

			if( $result ){
				$count 	= $this->db->query( "SELECT COUNT(*) quantity FROM sl_treasury_review WHERE ID_admin_users = $this->id_admin_users" );
				$data 	= $count->fetch_array(MYSQLI_ASSOC);
				$qty_after = $data['quantity'];
				$this->inserted = $qty_after - $qty_before;
			}

			return $result;
		}

	}

