<?php
class BankLayoutStructure{
	
	private $db;
	public $bank;
	public $account;

	public $column_relation;
	public $permitted_values;
	public $filter_by_column;
	public $relationBankAccounts;

	const BNRT	= 'Banorte';
	const BBVA	= 'BBVA';
	const BNMX	= 'Banamex';
	const INBR	= 'Inbursa';
	const SNTD	= 'Santander';
	const MONX	= 'Monex';
	const AZTE	= 'Azteca';
	const AMEX	= 'Amex';
	const PAYP	= 'Paypal';
	const MLTV  = 'Multiva';

	public function __construct( $db ){
		
		global $cfg;

		$this->db = $db;

		/*Buscan el Name de los bancos activos | No repetidos | Activos | En relaciona a uno de los bancos activos*/
		$bancos_activos = "
							SELECT name, 
								CASE
									WHEN name LIKE '%Banorte%' 	 THEN '".self::BNRT."'
									WHEN name LIKE '%BBVA%' OR name LIKE '%Bancomer%' 	THEN '".self::BBVA."'
									WHEN name LIKE '%Banamex%' 	 THEN '".self::BNMX."'
									WHEN name LIKE '%Inbursa%' 	 THEN '".self::INBR."'
									WHEN name LIKE '%Santander%' THEN '".self::SNTD."'
									WHEN name LIKE '%Monex%' 	 THEN '".self::MONX."'
									WHEN name LIKE '%Azteca%' 	 THEN '".self::AZTE."'
									WHEN name LIKE '%Amex%' 	 THEN '".self::AMEX."'
									WHEN name LIKE '%Paypal%' 	 THEN '".self::PAYP."'
									WHEN name LIKE '%Multiva%'   THEN '".self::MLTV."'
									ELSE ''
								END AS banco
							FROM sl_banks
							WHERE Status = 'Active'
							HAVING banco != '';
						";
		if( $bank_list = $this->db->query( $bancos_activos ) ){
			while ( $data = $bank_list->fetch_array()){
				$this->registered_BankAccounts[ $data['banco'] ][] = $data['name'];
			}        
		}


		$this->column_relation = array( 
								self::BNRT	=> array(
													'date_bank' 			=> 0,
													'branch_office' 		=> 4,
													'description_1' 		=> 2,
													'description_2' 		=> 9,
													'description_3' 		=> null,
													'reference' 			=> 1,
													'external_reference' 	=> null,
													'legend_reference' 		=> null,
													'numerical_reference' 	=> null,
													'transaction_code' 		=> 3,
													'movement' 				=> 8,
													'deposit' 				=> 5,
													'retirement' 			=> 6,
													'balance' 				=> 7
												),
								self::BNMX	=> array(
													'date_bank'	 			=> 0,
													'branch_office'	 		=> null,
													'description_1'	 		=> 1,
													'description_2'	 		=> null,
													'description_3'	 		=> null,
													'reference'	 			=> null,
													'external_reference'	=> null,
													'legend_reference'	 	=> null,
													'numerical_reference'	=> null,
													'transaction_code'		=> null,
													'movement'	 			=> null,
													'deposit'	 			=> 2,
													'retirement'	 		=> 3,
													'balance'	 			=> 4
												),
								self::BBVA	=> array(
													'date_bank'	 			=> 0,
													'branch_office'	 		=> null,
													'description_1'	 		=> 1,
													'description_2'	 		=> null,
													'description_3'	 		=> null,
													'reference'	 			=> null,
													'external_reference'	=> null,
													'legend_reference'	 	=> 3,
													'numerical_reference'	=> 2,
													'transaction_code'		=> null,
													'movement'	 			=> null,
													'deposit'	 			=> 5,
													'retirement'	 		=> 4,
													'balance'	 			=> 6
												),
								self::INBR	=> array(
													'date_bank'	 			=> 0,
													'branch_office'	 		=> null,
													'description_1'	 		=> 1,
													'description_2'	 		=> 5,
													'description_3'	 		=> null,
													'reference'	 			=> null,
													'external_reference'	=> 2,
													'legend_reference'	 	=> 3,
													'numerical_reference'	=> 4,
													'transaction_code'		=> null,
													'movement'	 			=> null,
													'deposit'	 			=> 7,
													'retirement'	 		=> 6,
													'balance'	 			=> 8
												),
								self::SNTD	=> array(
													'date_bank' 			=> 0,
													'branch_office' 		=> 2,
													'description_1' 		=> 3,
													'description_2' 		=> 8,
													'description_3' 		=> null,
													'reference' 			=> 7,
													'external_reference' 	=> null,
													'legend_reference' 		=> null,
													'numerical_reference'	=> null,
													'transaction_code' 		=> null,
													'movement' 				=> null,
													'deposit' 				=> 5,
													'retirement' 			=> 4,
													'balance' 				=> 6
												),
								self::MLTV  => array(
													'date_bank'             => 0,
													'branch_office'         => null,
													'description_1'         => 3,
													'description_2'         => null,
													'description_3'         => null,
													'reference'             => null,
													'external_reference'    => null,
													'legend_reference'      => null,
													'numerical_reference'   => 2,
													'transaction_code'      => null,
													'movement'              => null,
													'deposit'               => 5,
													'retirement'            => 4,
													'balance'               => 6
												)
							);		

		$this->position_titles = array(
								self::BNRT	=> array('row'=>'4',	'col'=>0,	'num_cols'=>10),
								self::BBVA	=> array('row'=>'4',	'col'=>0,	'num_cols'=>5),
								self::BNMX	=> array('row'=>'14',	'col'=>0,	'num_cols'=>5),
								self::INBR	=> array('row'=>'6',	'col'=>0,	'num_cols'=>10),
								self::SNTD	=> array('row'=>'4',	'col'=>0,	'num_cols'=>9),
								self::MLTV  => array('row'=>'7',    'col'=>0,   'num_cols'=>7)
							);

		$this->format_date = array(
								self::BNRT	=>	array('m-j-y', 'd/m/Y'),
								self::BBVA	=>	array('m-j-y'),
								self::BNMX	=>	array('m-j-y'),
								self::INBR	=>	array('d/m/Y'),
								self::SNTD	=>	array('m-j-y'),
								self::MLTV  =>  array('d/m/Y')
							);
	}

	public function setByAccount($num_account)
	{

		foreach ($this->registered_BankAccounts as $bank => $accounts)
		{
			if( in_array($num_account, $accounts) )
			{
				$this->bank		= $bank;
				$this->account	= $num_account;
				return true;
			}
		}

		return false;
	}


	public function getColumnRelation()
	{
		if( !empty($this->bank)  ){
			return $this->column_relation[$this->bank];
		}
		return false;
	}

	public function positionTitles()
	{
		if( !empty($this->bank)  ){
			return $this->position_titles[$this->bank];
		}
		return false;
	}

	public function getFormatDate()
	{
		if( !empty($this->bank)  ){
			return $this->format_date[$this->bank];
		}
		return false;
	}

}

