sub refreshPreviewTreasury{

	use Data::Dumper;
	use JSON;
	use Encode;

	print "Content-type:  text/html\n\n"; 

	# Borra de manera logica los resgistros que reciba en el parametro  $in{'delete'}
	if( $in{'delete'} and  $in{'delete'} ne '' ){
		&Do_SQL("UPDATE sl_treasury_review SET status='inactive', processing_date=now(), processing_id_admin_user='".$usr{'id_admin_users'}."'  WHERE id_treasury_review in (".$in{'delete'}.");");		
	}else{
		# Consulta principal de los registros guardados de los
		my ($sth) = &Do_SQL("
							SELECT 	id_treasury_review,
									bank,
									cuenta,
									date(date_bank) date_bank,
									branch_office,
									description_1,
									description_2,
									description_3,
									reference,
									external_reference,
									legend_reference,
									numerical_reference,
									transaction_code,
									movement,
									deposit,
									retirement,
									balance,
									status,
									date,
									time,
									ID_admin_users 
							FROM sl_treasury_review 
							WHERE status='active' 
							ORDER BY bank, cuenta, id_treasury_review, date_bank;
							");
		my $rows, $title_rows, $bank, $account, $x, $select, $options, @relations, $invalid, $bank_selector, $bank_header;

		while ( my $rec = $sth->fetchrow_hashref() ){

			my $description_concat, $deposit, $retirement; 
			my @descriptions;

			# Si es el primer registro de un nuevo Banco 
			if( $bank ne $rec->{'bank'} )
			{
				$bank 		= $rec->{'bank'};
			}

			# Si es el primer registro de una nueva cuenta de Banco entra
			if( $account ne $rec->{'cuenta'} )
			{
				$bank 		= $rec->{'bank'};
				$account 	= $rec->{'cuenta'};
				$id_account = $rec->{'cuenta'};
				$id_account =~ s/ /_/g;
				$select 	= '';
				$options 	= '';

				# Arma el <select> con las categorias que le corresponde al tipo de Banco
				 my ($sth2) = &Do_SQL("
										SELECT * 
										FROM 
											(
												(SELECT subcode name
												FROM sl_vars_config
												WHERE  sl_vars_config.command IN ('refreshPreviewTreasury') and description = '$bank'
												ORDER BY description, subcode)

												UNION ALL

												(SELECT code name
												FROM sl_vars_config
												WHERE sl_vars_config.command IN ('importTreasury')
												ORDER BY code)
											) categories
										GROUP BY name								
									");

				$options .= '<option>SELECCIONAR CATEGOR&Iacute;A</option>';
				while ( my($category) = $sth2->fetchrow() ){
					$options .= '<option value="'.$category.'">'.$category.'</option>';
				}
				$options .= '<option value="SIN CATEGORIA">SIN CATEGOR&Iacute;A</option>';
				$select = $options.'</select>';


				my ($sth3) = &Do_SQL("	
										SELECT Largecode, Code, Subcode 
										FROM sl_vars_config 
										WHERE Command='refreshPreviewTreasury' and Description = '".$bank."'  
										ORDER BY subcode;
									");
				while ( my( $text, $field, $category ) = $sth3->fetchrow() )
				{
					push(@relations,{'text'=>$text, 'field'=>$field, 'category'=>$category});
				}


				$bank_selector .='
							<div class="account_item" data-status="inactive" data-account="AC_'.$id_account.'">
								<div class="title">
									<img class="logo_bank" src="/sitimages/banks/'.$rec->{'bank'}.'.png" alt="'.$rec->{'cuenta'}.'" title="'.$rec->{'cuenta'}.'">
									<!-- span id="bank_name">'.$rec->{'bank'}.'</span -->
									<span class="account_name" style="display:none;">'.$rec->{'cuenta'}.'</span>
								</div>
							</div>
							';

			}


			## Verifica si en el campo indicado en $D->{'field'} se encuentra el texto $D->{'text'} de acuerdo a una expresión regular
			#my $invalid = 'class="invalid"';
			my $select_already = $select;
			$select_already = '<select id="slct'.$rec->{'id_treasury_review'}.'">'.$select_already;

			Filtrando:foreach my $D ( @relations ){
			
				if( $rec->{ $D->{'field'} } =~ /^$D->{'text'}/ )
				{
					$invalid = '';
					$select_already =~ s/value="$D->{'category'}"/value="$D->{'category'}" selected/g;
					last Filtrando;
				}
			
			} 

			## Concatena los campos Description_x para poder mostrarlos todos en una celda de la tabla
			for( $x=1; $x<=3; $x++ ){
				if( $rec->{'description_'.$x} ne  '' ) {
					push @descriptions, $rec->{'description_'.$x};
				}
			}
			if( $rec->{'transaction_code'} ne  '' ) {
				push @descriptions, 'Transaction code: '.$rec->{'transaction_code'};
			}


			$description_concat = '';
			if( @descriptions ){
				$description_concat = join('<br>', @descriptions);
			}else{
				$description_concat = $rec->{'legend_reference'};
			}



			$rows .= '<tr data-belongs-account="AC_'.$id_account.'" style="display:none;" '.$invalid.'>';
			$rows .= '<td>'.(($invalid)? '': '<input type="checkbox" id="'.$rec->{'id_treasury_review'}.'">').'</td>';
			$rows .= '<td class="date">'.$rec->{'date_bank'}.'</td>';
			$rows .= '<td>'.(($invalid eq 'class="invalid"')? '': $select_already).'</td>';
			$rows .= '<td class="description">'.$description_concat.'</td>';
			#$rows .= '<td>'.$rec->{'movement'}.'</td>';
			#$rows .= '<td>'.$rec->{'transaction_code'}.'</td>';

			$deposit	=($rec->{'deposit'} eq 0)? '' : format_price($rec->{'deposit'},2);
			$retirement	=($rec->{'retirement'} eq 0)? '' : format_price($rec->{'retirement'},2);

			$rows .= '<td class="amount deposit">'.$deposit.'</td>';
			$rows .= '<td class="amount retirement">'.$retirement.'</td>';
			$rows .= '<td class="amount balance">'.format_price($rec->{'balance'},2).'</td>';
			$rows .= '</tr>';
		}

		my %to_refresh;
		$to_refresh{'banks'} = $bank_selector;
		$to_refresh{'rows'} = $rows;

		my $put = encode_json \%to_refresh;

		print $put;
	}

}


sub importTreasury{

	use Data::Dumper;
	use JSON;
	use POSIX qw(strftime);


	my $fecha_actual = strftime "%Y-%m-%d", localtime(time - 7776000); 
	my $email_text = 'CARGA DE MOVS. PARA TESORERIA -- '.localtime.'<br />';

	my $sub_acc_of = $cfg{'sub_acc'};
	my $first_movement_id;
	my $last_movement_id;

	my $sth_banks;
	my $sth_accounts;
	my $rec_banks;
	my $rec_accounts;

	my $registers2 = 0; 
	my $total_regs = 0;
	my @office_desc;

	my %log_by_id;

	print "Content-type:  text/html\n\n"; 

	# Obtiene datos del ULTIMO movimiento
	my ($sth_last_bm) 	= &Do_SQL("SELECT 
									CONCAT_WS(' | ',`ID_banks_movements`,`ID_banks`,`BankDate`,`Amount`,`RefNum`,`RefNumCustom`,`Date`,`Time`,`ID_admin_users`) as last_movement, 
									ID_banks_movements as id_last 
									FROM sl_banks_movements ORDER BY ID_banks_movements DESC LIMIT 1;");
	$rec_last_bm 		= $sth_last_bm->fetchrow_hashref;
	$email_text .= 'Ultimo registro en sl_banks_movements antes de la insercion: '.$rec_last_bm->{'id_last'}."<br />";

	# Se calcula el id del proximo registro a guardar
	$first_movement_id = ($rec_last_bm->{'id_last'} + 1);


	# Obtiene el id del registro del Edo de cuenta (sl_treasury_review) y la categoria asignada.
	$pair = decode_json( $in{'id_treasury'} );
	my @update, @select_id, $update_str, $select_str;
	while( my( $key, $value ) = each $pair ){
		# Inserta la categoria en el registro del Edo de cuenta
		$query = "UPDATE sl_treasury_review SET category = '".$value."' WHERE ID_treasury_review = '".$key."';";
		&Do_SQL($query);
	    push( @select_id, $key);
	}


	$select_str = join(',',@select_id );


	# 				      0            1                 2                       3                              4                                5         6          7         8           9             10        11                12                 13                   14           15           16            17                   18                                                                    
	$query  = "SELECT  cuenta, date(date_bank) date, time(date_bank) time, branch_office, concat( description_1, description_3 ) description, deposit, retirement, balance, movement,  description_2,  reference,  category,  '' cuenta_egresos, '' cuenta_ingresos, '' tipo_cambio, '' field15 , '' field16 ,  id_treasury_review,  UCASE(bank) bank ";
	$query .= "FROM sl_treasury_review WHERE id_treasury_review in (".$select_str.") AND status='active';";


	# Se obtienen los registros del estado de cuenta que indica $in{'id_treasury'}
	my ($sth_reg_treasury) = &Do_SQL($query);

	#Recorre todos los registros obtenidos en base a $in{'id_treasury'}
	lineas:while ( my $treasury = $sth_reg_treasury->fetchrow_hashref() )
	{

		$total_regs++;

		$email_text .= "-------------------------<br />";
		$email_text .= "LINEA $total_regs :<br />";

		# Verifica si el Periodo esta abierto
		my $bank_date = $treasury->{'date'};
		my $valid_periods = &validate_date_in_openperiod($bank_date);


		if( $valid_periods == 0 ){
			$log_by_id{$treasury->{'id_treasury_review'}} = 'Periodo Contable Cerrado';
			$email_text .= "Linea $total_regs: El periodo contable esta cerrado.<br />";
			next lineas;
		}


		my $col_clasification = '';
		my $movement_type = '';
		my $movement_amount = 0;
		my $ref_num_custom = 'NULL';
		my $movement_memo = 'NULL';
		my $id_banks_movrel_new = '';
		my $id_banks_movements_new = '';
		my $table_used = 'sl_banks_movements';
		my $cat_mment_type = '';
		my $mment_type = '';
		my $ach_trans;
		my $ach_trans_cnies;
		my $currency_exchange;
		my @error_on_ids;
		my $segment = '';

		#-------------------------------------------------------------------
		#Obtener la informacion del banco de la linea que se esta procesando
		#-------------------------------------------------------------------
		
		#Ir a la BD para traer los datos del banco, solo si el anteriormente obtenido es distinto al actual
		if($treasury->{'cuenta'} ne $rec_banks->{'Name'}) 
		{
			$query = "SELECT * FROM sl_banks WHERE Name = '$treasury->{'cuenta'}' and sl_banks.status='Active';";
			($sth_banks) = &Do_SQL($query);

			# Si encuentra los datos del Banco busca el ID_accountig
			if($rec_banks = $sth_banks->fetchrow_hashref){
				$query = "SELECT sl_accounts.ID_accounts, sl_accounts.ID_accounting, sl_accounts.Name FROM sl_accounts INNER JOIN sl_banks ON sl_accounts.ID_accounts = sl_banks.ID_accounts ";
				$query .= "WHERE 1 AND sl_banks.ID_banks = ".$rec_banks->{'ID_banks'}." AND sl_banks.Status='Active' AND sl_accounts.Status='Active';";

				($sth_accounts) = &Do_SQL($query);
				$BankAccount = $sth_accounts->fetchrow_hashref;
			}else{ 
				# Si no ecuentra los datos del banco emite el mensaje de datos Banco no existe y continua con la siguiente linea.
				$log_by_id{$treasury->{'id_treasury_review'}} = 'El Banco "'.$treasury->{'cuenta'}.'" no existe';
				$email_text .= "EL BANCO ".$treasury->{'cuenta'}." NO EXISTE<br />";
				next lineas;
			}
		}



		# Si se tiene el nombre del archivo, sin extensión y sin ruta
		# Limpia y establece una serie de Variables
		if( $treasury->{'deposit'} eq '0' ){ $treasury->{'deposit'} = '';}
		if( $treasury->{'retirement'} eq '0' ){ $treasury->{'retirement'} = '';}

		$col_clasification = $treasury->{'category'};
		$col_clasification = decode('UTF-8', $col_clasification);
		$col_clasification = encode('iso-latin-1', $col_clasification);

		$ach_trans = '';
		$ach_trans_cnies = '';


		# Si el registro es Credit
		if ($treasury->{'retirement'} == 0 and $treasury->{'deposit'} > 0 ) {
				$movement_type = 'Debits';
				$mment_type = 'Debit';
				$cat_mment_type = 'Tesoreria';
				$treasury->{'retirement'} =~ s/\$|\,//;
				$movement_amount = $treasury->{'deposit'};
				#$ach_trans = $treasury->{'cuenta_egresos'};
				#$ach_trans_cnies = $treasury->{'field15'};
		}elsif ( $treasury->{'retirement'} > 0 and $treasury->{'deposit'} == 0){
				$movement_type = 'Credits';
				$mment_type = 'Credit';
				$cat_mment_type = 'Tesoreria';
				$treasury->{'deposit'} =~ s/\$|\,//;
				$movement_amount = $treasury->{'retirement'};
				#$ach_trans = $treasury->{'cuenta_ingresos'};
				#$ach_trans_cnies = $treasury->{'field16'};
		}


		# Si no se registra tipo de cambio por defecto es 1
		if( $rec_banks->{'Currency'} ne 'MX$' ){
			$query = "SELECT exchange_rate FROM sl_exchangerates WHERE Date_exchange_rate = '".$bank_date."';";
			($sth_exchange) = &Do_SQL($query);
			$currency_exchange = $sth_exchange->fetchrow;
		}else{
			$currency_exchange = 1;
		}
		
		
		$bank_date 		= $treasury->{'date'};
		$ref_num_custom = $treasury->{'movement'} 		if($treasury->{'movement'} ne '');
		$ref_num 		= $treasury->{'reference'}		if($treasury->{'reference'} ne '');
		$movement_memo 	= $treasury->{'description'}	if($treasury->{'description'} ne '');						


		$registers2++;
		if($bank_date le $fecha_actual) {
			$log_by_id{$treasury->{'id_treasury_review'}} = 'Este registro es anterior a diez dias. No se carga.';
			$email_text .= "Este registro es anterior a diez dias. No se carga.<br />";
			print $email_text;
		} else {

			#---------------------------	
			#CALIFICACION DE MOVIMIENTOS
			#---------------------------
			
			#Cuando es una transferencia a otra cuenta
			if ($col_clasification eq 'TRASPASO' or $col_clasification eq 'TRANSFERENCIA INTERCIA' or $col_clasification eq 'TRASPASO ENTRE CUENTAS')
			{
				#$ach_trans_cnies = &trim($ach_trans_cnies);
				
				#Obtengo la cuenta contable del tercero, de la columna correspondiente (INTERCOMPAÑIA O LOCAL)
				#INTERCOMPAÑIA = $ach_trans_cnies	|	LOCAL = $ach_trans
				$ach = ($col_clasification eq 'TRANSFERENCIA INTERCIA')? $ach_trans_cnies : $ach_trans;

				#Si la cuenta tiene menos de 18 caracteres y no esta contenida en $filter_noaccount lo rellena de CEROS hasta completar 18 caracteres
				if (length($ach) < 18 and $filter_noaccount{lc($in{'file_name'})} eq '') {
					my $diff_length = 18 - length($ach);
					$ach = ( '0' x $diff_length ) . $ach;
				}
				$rec_accounts = $BankAccount;
			
			} else {

				##Si no es una transferencia
				#Cuando es un movimento 'simple', se busca la cuenta contable según la clasificación
				$Query = "
						SELECT * FROM sl_accounts 
						WHERE ID_accounting = (
							SELECT subcode FROM sl_vars_config 
							WHERE command='importTreasury' AND code = '".$col_clasification."' AND Description ='accounting_ids' 
							GROUP BY subcode LIMIT 1
							 ) 
						AND sl_accounts.Status='Active';";
						
				($sth_accounts) = &Do_SQL($Query);
				$rec_accounts = $sth_accounts->fetchrow_hashref;

			}

			##Si el movimiento se maneja en una divisa extranjera, se aplican las conversiones
			if($currency_exchange > 1){
				$amount_currency = $movement_amount;
				$movement_amount = $movement_amount * $currency_exchange;
			}else{
				$amount_currency = "NULL";
			}
			

			#&Do_SQL("START TRANSACTION;");
			#&Do_SQL("ROLLBACK;");
			#&Do_SQL("COMMIT;");


			#Si Tiene cuenta contable hace la inserción en sl_banks_movements, en sl_banks_movrel, en sl_movements
			if ($rec_accounts->{'ID_accounts'})
			{

				###### 	INSERTA UN REGISTRO EN SL_BANKS_MOVEMENTS (MOVIMIENTO BANCARIO)
				$Query = "INSERT INTO sl_banks_movements SET
							ID_banks_movements = NULL
							, ID_banks=".$rec_banks->{'ID_banks'}."
							, Type='".$movement_type."'
							, BankDate='$bank_date'
							, ConsDate = NULL
							, Amount='".$movement_amount."'
							, AmountCurrency = ".$amount_currency."
							, currency_exchange = '".$currency_exchange."'
							, RefNum = '$ref_num'
							, RefNumCustom='$ref_num_custom'
							, doc_type = 'NA'
							, Memo = '$movement_memo'
							, Date = CURDATE()
							, Time=CURTIME()
							, ID_admin_users='".$usr{'id_admin_users'}."';";

				$sth_bmovements = &Do_SQL($Query);
				$id_banks_movements_new = $sth_bmovements->{'mysql_insertid'};
				$id_account_related = $rec_accounts->{'ID_accounting'};

				if (!$id_banks_movements_new){
					$log_by_id{$treasury->{'id_treasury_review'}} = 'Error en la insercion [sl_banks_movements]';
					$email_text .= "No se inserto en sl_banks_movements <br />";
				} else {

					$email_text .= "Se inserto el registro con id=$id_banks_movements_new en sl_banks_movements <br />";

					##----------------------------------------------------------------------------------------------
					###### 	INSERTA UN REGISTRO EN SL_BANKS_MOVREL
					$Query = "INSERT INTO sl_banks_movrel SET
								ID_banks_movrel = NULL
								, ID_banks_movements=".$id_banks_movements_new."
								, tablename= 'accounts'
								, tableid = '$rec_accounts->{'ID_accounts'}'
								, AmountPaid = '$movement_amount'
								, Date = CURDATE()
								, Time=NOW()
								, ID_admin_users='".$usr{'id_admin_users'}."';";

					$sth_bmovrel = &Do_SQL($Query);
					$id_banks_movrel_new = $sth_bmovrel->{'mysql_insertid'};
					
					if (!$id_banks_movrel_new){	
						$log_by_id{$treasury->{'id_treasury_review'}} = 'Error en la insercion [sl_banks_movrel]';
						$email_text .= "No se inserto registro en sl_banks_movrel <br />";
					} else {
						$email_text .= "Se inserto el registro con id=$id_banks_movrel_new en sl_banks_movrel <br />";
					}

					#----------------------------------------------------------------------------------------------
					###### 	INSERTA UN REGISTRO EN SL_MOVEMENTS (MOVIMIENTO CONTABLE)
					$Query = "INSERT INTO sl_movements SET
						ID_movements = NULL
						, ID_accounts = '$BankAccount->{'ID_accounts'}'
						, Amount = '$movement_amount'
						, Reference = '$treasury->{'description_2'}'
						, EffDate = '$bank_date'
						, tableused = '$table_used'
						, ID_tableused = '$id_banks_movements_new'
						, Category = '$cat_mment_type'
						, Credebit = '$mment_type'
						, ID_journalentries = 0
						, Status = 'Active'
						, Date = CURDATE()
						, Time = NOW()
						, ID_admin_users ='".$usr{'id_admin_users'}."';";
					
					$sth_movements = &Do_SQL($Query);
					$id_movements_new = $sth_movements->{'mysql_insertid'};
					
					if (!$id_movements_new){
						$log_by_id{$treasury->{'id_treasury_review'}} = 'Error en la insercion [sl_movements '.$BankAccount->{'ID_accounts'}.']';
						$email_text .= "No se inserto registro en movements<br />";
					} else {
						$email_text .= "Se inserto el registro con id=$id_movements_new en sl_movements <br />";
					}
					
					###### SI ES UN TRASPASO ENTONCES NO TIENE CONTRAPARTIDA
					if ( not ($col_clasification eq 'TRASPASO' or $col_clasification eq 'TRANSFERENCIA INTERCIA' or $col_clasification eq 'TRASPASO ENTRE CUENTAS') ) 
					{

						if( int(substr($rec_accounts->{'ID_accounts'},0,1)) > 3 ){
							$Query = "SELECT Subcode FROM sl_vars_config WHERE Code='$col_clasification' AND Description = 'segments';";
							my $sth_sgmnt = &Do_SQL($Query);
							my $hash_sgmnt = $sth_sgmnt->fetchrow_hashref;
							if( $hash_sgmnt->{'Subcode'} ){
								$segment = $hash_sgmnt->{'Subcode'};
							}
						}else{
							$segment = '0';
						}

						if ( !($segment =~ /^\d+?$/) ){
							$log_by_id{$treasury->{'id_treasury_review'}} = 'No hay registrado un segmento para la categor&iacute;a '.$col_clasification.' / '.$segment;
							$email_text .= "No se inserto registro en movements<br />";
						}else{

							$mment_type = ($mment_type eq 'Debit')?'Credit':'Debit';

							$Query = "INSERT INTO sl_movements SET
									ID_movements = NULL
									, ID_accounts = '$rec_accounts->{'ID_accounts'}'
									, Amount = '$movement_amount'
									, Reference = '$treasury->{'description_2'}'
									, EffDate = '$bank_date'
									, tableused = '$table_used'
									, ID_tableused = '$id_banks_movements_new'
									, Category = '$cat_mment_type'
									, Credebit = '$mment_type'
									, ID_segments = '".$segment."' 
									, ID_journalentries = 0
									, Status = 'Active'
									, Date = CURDATE()
									, Time = NOW()
									, ID_admin_users ='".$usr{'id_admin_users'}."';";

							$sth_movements = &Do_SQL($Query);
							
							$id_movements_new = $sth_movements->{'mysql_insertid'};
							if (!$id_movements_new){
								$log_by_id{$treasury->{'id_treasury_review'}} = 'Error en la insercion [sl_movements '.$rec_accounts->{'ID_accounts'}.']';
								$email_text .= "No se inserto registro en movements<br />";
							} else {
								$email_text .= "Se inserto el registro con id=$id_movements_new en sl_movements <br />";
							}	
							
						}

					}				
				}

			} else {
				#Cuando no se definió una clasificación para el movimiento, este se registra solo para cuestiones de concilicación bancaria
				if( $col_clasification eq '' ) 
				{
					$Query = "INSERT INTO sl_banks_movements SET
							  ID_banks_movements = NULL
							, ID_banks=".$rec_banks->{'ID_banks'}."
							, Type='".$movement_type."'
							, BankDate='$bank_date'
							, Amount='".$movement_amount."'
							, AmountCurrency = NULL
							, currency_exchange = '".$currency_exchange."'
							, RefNum = '$ref_num'
							, RefNumCustom='$ref_num_custom'
							, doc_type = 'NA'
							, Memo = '$movement_memo'
							, Date = CURDATE()
							, Time=NOW()
							, ID_admin_users='".$usr{'id_admin_users'}."';";

					$sth_bmovements = &Do_SQL($Query);

					$id_banks_movements_new = $sth_bmovements->{'mysql_insertid'};
					$id_account_related = 'Registrado solo para cuestiones de concilicaci&oacute;n bancaria';

					if (!$id_banks_movements_new){
						$log_by_id{$treasury->{'id_treasury_review'}} = "Error en la insercion [sl_banks_movements]";
						$email_text .= "No se inserto el movimiento<br />";
					} else {
						$email_text .= "Se inserto el registro con id=$id_banks_movements_new en sl_banks_movements <br />";
					}
				}else{
					#Si no existe una cuenta contable asociada a la clasificación, es un error que merece atención
					$log_by_id{$treasury->{'id_treasury_review'}} = "No se encontro ninguna cuenta contable que corresponda a esa clasificacion"; #$col_clasification.
					$email_text .= "No se encontró alguna cuenta contable que corresponda a esa clasificación $col_clasification";
					next;
				}
			}
			
			#Se inserta el registro en sl_bank_statements para todos los movimientos del Layout
			$Query = "INSERT INTO sl_bank_statements SET
					  ID_bank_statements = NULL
					, ID_banks=".$rec_banks->{'ID_banks'}."
					, Type='".$movement_type."'
					, BankDate='$bank_date'
					, ConsDate = ". (($col_clasification eq '')? 'NULL' : 'NOW()') ."
					, Amount='".$movement_amount."'
					, AmountCurrency = NULL
					, currency_exchange = '".$currency_exchange."'
					, RefNum = '$ref_num'
					, RefNumCustom='$ref_num_custom'
					, doc_type = 'NA'
					, Memo = '$movement_memo'
					, Balance = '$balance'
					, Date = CURDATE()
					, Time=CURTIME()
					, ID_admin_users='".$usr{'id_admin_users'}."';";
		
			$sth_bmovements = &Do_SQL($Query);
		
			$id_bank_statements_new = $sth_bmovements->{'mysql_insertid'};
			if (!$id_bank_statements_new){
				$log_by_id{$treasury->{'id_treasury_review'}} = 'No se inserto el movimiento en sl_bank_statements';
				$email_text .= "No se inserto el movimiento en sl_bank_statements<br />";
			} else {
				$email_text .= "Se inserto el registro con id=$id_bank_statements_new en sl_bank_statements<br />";
			}


			if( !($log_by_id{$treasury->{'id_treasury_review'}}) ){
				$log_by_id{$treasury->{'id_treasury_review'}} = $id_banks_movements_new.'|'.$id_account_related;
				&Do_SQL("UPDATE sl_treasury_review SET status='processed', processing_date=now(), processing_id_admin_user='".$usr{'id_admin_users'}."'  WHERE id_treasury_review = ".$treasury->{'id_treasury_review'}.";");
			}

			#Se inserta el registro en sl_banks_movements_notes para todos los movimientos del layout
			$Query = "INSERT INTO sl_banks_movements_notes SET ID_banks_movements = '$id_banks_movements_new',
						Notes='"."Carga automatica ".$record.' [|'.$col_clasification.'|] '."',Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."';";

			&Do_SQL($Query);
		}
	}


	my ($sth_last_am) = &Do_SQL("SELECT ID_banks_movements id_last FROM sl_banks_movements ORDER BY ID_banks_movements DESC LIMIT 1;");
	$rec_last_am = $sth_last_am->fetchrow_hashref;
	$email_text .= "--------------------------<br />";
	$last_movement_id = $rec_last_am->{'id_last'};	
	$email_text .= 'Ultimo registro en sl_banks_movements despues de la insercion: '.$last_movement_id."<br />";
	
	my $put = encode_json \%log_by_id;

	print $put;

}



############################################################################################
############################################################################################
#	Function: edit_relation_treasury_layout
#   	Permite editar las relaciones entre texto -> categoria -> account
#
#	Created by:
#		01-01-2017:: Huitzilihuitl Ceja
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub edit_relation_treasury_layout{
############################################################################################
############################################################################################
	print "Content-type: text/html\n\n";

	if( $in{'action'} )
	{
		# field:description_1
		# text_filter:pago
		# category:INTERESES  PAGADOS POR PRESTAMO
		# accout:1234234234

		@account = split / - /, $in{'account'};



		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_vars_config WHERE Command='importTreasury' AND Code ='".$in{'category'}."';");
		my $exist = $sth->fetchrow();
		if( $exist > 0 ){
			&Do_SQL("UPDATE sl_vars_config SET  Subcode='".$account[0]."', Date=CURDATE(), Time=CURTIME(), ID_admin_users='".$usr{'id_admin_users'}."' 
					WHERE Command='importTreasury' AND Code ='".$in{'category'}."';");
		}else{
			&Do_SQL("INSERT INTO sl_vars_config (Command, Code, Subcode, Description, Date, Time, ID_admin_users) 
					VALUES ('importTreasury','".$in{'category'}."','".$account[0]."','accounting_ids',CURDATE(), CURTIME(), '".$usr{'id_admin_users'}."');");
		}


		&Do_SQL("INSERT INTO sl_vars_config (Command, Code, Subcode, Largecode, Description, Date, Time, ID_admin_users) 
				VALUES ('refreshPreviewTreasury','".$in{'field'}."','".$in{'category'}."','".$in{'text_filter'}."','".$in{'bank'}."',CURDATE(), CURTIME(), '".$usr{'id_admin_users'}."');");
	

		print "	<center>
				<h2>Relation created correctly<h2>
				</center>";

		return 1;

	}



	$in{'reg'} = int($in{'reg'});

	my $sth = &Do_SQL("SELECT 	id_treasury_review,
								bank,
								cuenta,
								date(date_bank) date_bank,
								branch_office,
								description_1,
								description_2,
								description_3,
								reference,
								external_reference,
								legend_reference,
								numerical_reference,
								transaction_code,
								movement,
								deposit,
								retirement,
								balance,
								status,
								date,
								time,
								ID_admin_users 
						FROM sl_treasury_review 
						WHERE status='active' AND id_treasury_review = '".$in{'reg'}."'
					;");
	$data_reg = $sth->fetchrow_hashref();
	$va{'description_1'} = $data_reg->{'description_1'};
	$va{'description_2'} = $data_reg->{'description_2'};
	$va{'description_3'} = $data_reg->{'description_3'};
	$va{'transaction_code'} = $data_reg->{'transaction_code'};
	$va{'bank'}	= $data_reg->{'bank'};



	my ($sth2) = &Do_SQL("
							SELECT name 
							FROM 
								(
									(SELECT subcode name
									FROM sl_vars_config
									WHERE  sl_vars_config.command IN ('refreshPreviewTreasury')
									ORDER BY description, subcode)

									UNION ALL

									(SELECT code name
									FROM sl_vars_config
									WHERE sl_vars_config.command IN ('importTreasury')
									ORDER BY code)
								) categories
							GROUP BY name								
						");

	my $options = '<select name="category">';
	while ( my($category) = $sth2->fetchrow() ){
		$options .= '<option value="'.$category.'">'.$category.'</option>';
	}
	$options .= '</select>';

	$va{'select_categories'} = $options;





	my ($sth2) = &Do_SQL(" SELECT ID_accounting, Name FROM sl_accounts WHERE Status = 'Active'; ");

	my @options;
	while ( my($accounting, $name) = $sth2->fetchrow() ){
		push @options, '"'.$accounting.' - '.$name.'"';
	}

	$options = join ',', @options;

	$va{'select_accounts'} = $options;

	print &build_page('apporders/edit_relation_treasury_layout.html');
}






1;