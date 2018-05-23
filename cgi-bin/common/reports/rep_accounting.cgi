#!/usr/bin/perl
##################################################################
#   REPORTS : ACCOUNTING
##################################################################

#############################################################################
#############################################################################
#   Function: rep_accounting_auxiliary
#
#       Es: Reporte Auxiliar de Movimientos Contables
#       En: 
#
#
#    Created on: 2016-07-20
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: Variable para determinar que se debe generar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_accounting_auxiliary {
#############################################################################
#############################################################################
	# Obtenemos informacion de la empresa
	&get_company_info();

	$va{'expanditem'} = 3;
	$va{'html_print'};

	if ($in{'action'}){
		$va{'csv'} .= qq|$va{'company_name'}\n|;
		$va{'csv'} .= qq|REPORTE DE MOVIMIENTOS AUXILIARES\n\n|;
		$va{'csv'} .= qq|"FECHA","NO DE CUENTA","CUENTA","ID JOURNAL ENTRY","CATEGORIA","MEMO","ID","NAME","DEBIT","CREDIT","ID CREDITMEMO","INVOICE"\n|;

		my $add_sql = '';
		$add_sql .= ($in{'effdate_from'} and $in{'effdate_from'} ne '')? " AND sl_movements.EffDate>='".$in{'effdate_from'}."'":"";
		$add_sql .= ($in{'effdate_to'} and $in{'effdate_to'} ne '')? " AND sl_movements.EffDate<='".$in{'effdate_to'}."'":"";
		$add_sql .= ($in{'id_journalentries'} and $in{'id_journalentries'} > 0)? " AND sl_movements.ID_journalentries=".$in{'id_journalentries'}:"";

		my $custom_fname = ($in{'filename'} and $in{'filename'} ne '')? $in{'filename'}:'';
		
		if($in{'id_accounts'}){
			my (@ary_accounts) = split(/\|/,$in{'id_accounts'});
			$add_sql .= (scalar(@ary_accounts) > 0)?" AND sl_movements.ID_accounts IN (". join(',', @ary_accounts) .") ":"";
		}

		my $sql_extra = '';
		if( $in{'posted'} eq 'Posted' ){
			$sql_extra = " INNER JOIN sl_journalentries ON sl_movements.ID_journalentries = sl_journalentries.ID_journalentries AND sl_journalentries.Status = 'Posted' ";
		}

		## Definicion de valores
		my (%tbl_ref) = (
		'sl_orders'=>'Orders',
		'sl_purchaseorders'=>'Purchase Orders',
		'sl_adjustments'=>'Adjustments',
		'sl_vendors'=>'Deposits',
		'sl_bills'=>'Bills',
		'sl_creditmemos'=>'Credit Memos');

		$query = "SELECT 
			sl_movements.ID_movements
			, sl_movements.EffDate
			, sl_accounts.ID_accounting
			, UPPER(sl_accounts.Name)Name
			, IF(sl_movements.Credebit='Debit',sl_movements.Amount,'')Debit
			, IF(sl_movements.Credebit='Credit',sl_movements.Amount,'')Credit
			, sl_movements.Category
			, sl_movements.ID_journalentries
			, sl_movements.tableused
			, sl_movements.ID_tableused
			, sl_movements.tablerelated
			, sl_movements.ID_tablerelated
		FROM sl_movements
			INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
			$sql_extra
		WHERE sl_movements.Status='Active'
		$add_sql
		ORDER BY sl_movements.ID_movements";
		$sth = &Do_SQL($query);
		my ($total_debit, $total_credit);
		while(my $row = $sth->fetchrow_hashref()){
			
			my $id_accounting = &format_account($row->{'ID_accounting'});
			my $debit = ($row->{'Debit'} > 0)? &format_price($row->{'Debit'}):"";
			my $credit = ($row->{'Credit'} > 0)? &format_price($row->{'Credit'}):"";

			$total_debit += $row->{'Debit'};
			$total_credit += $row->{'Credit'};

			## Valores extra requeridos en el reporte
			my ($memo,$id,$tname,$id_rel,$reference)= &get_extra_values_for_accounting_reports($row->{'tableused'},$row->{'ID_tableused'},$row->{'tablerelated'},$row->{'ID_tablerelated'},$row->{'ID_journalentries'});

			## Category -> Diario
			if ($row->{'Category'} eq 'Diario'){
				my ($sth_aux) = &Do_SQL("SELECT FieldValue FROM sl_movements_auxiliary WHERE ID_movements = ".$row->{'ID_movements'}." AND FieldName = 'Description';");
				$memo = $sth_aux->fetchrow_array();
			}

			$va{'csv'} .= qq|"$row->{'EffDate'}","$id_accounting","$row->{'Name'}","$row->{'ID_journalentries'}","$row->{'Category'}","$memo","$id","$tname","$debit","$credit","$id_rel","$reference"\n|;

		}

		## Totales y Saldo
		$balance = 0;
		$balance = $total_debit - $total_credit;
		$va{'csv'} .= qq|"Totales","","","","","","","","|.&format_price($total_debit).qq|","|.&format_price($total_credit).qq|","|.&format_price($balance).qq|"\n|;
		
		## Pie de reporte
		$va{'csv'} .= &report_footer();

		## Impresion de archivo CSV
		my $f = lc($cfg{"app_title"}."-Movimientos-Auxiliares");
		$f = ($custom_fname ne '')?$custom_fname : $f;
		
		$f =~ s/ /_/g;
		print "Content-Disposition: attachment; filename=$f.csv;";
		print "Content-type: text/csv\n\n";
		print $va{'csv'};
		
		return;
	}else{
		$va{'id_accouns_options'} = &build_select_accounting;

	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_accounting_auxiliary.html');
}

#############################################################################
#############################################################################
#   Function: get_extra_values_for_accounting_reports
#
#       Es: Funcion para obtener informacion extra requerida por Contabilidad
#       En: 
#
#
#    Created on: 2016-07-21
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_extra_values_for_accounting_reports{
#############################################################################
#############################################################################
	## tableused, ID_tableused, tablerelated, ID_tablerelated, Category, ID_journalentries
	# ID_journalentries = $ary[5]
	my (@ary) = @_;

	++$contador;
	my $tname = 'N/A';
	my $memo = 'N/A';
	my $anexo1;
	my $consolidated = 0; #para ordenes sku

	############################################
	############################################
	########
	######## 1. Separamos por tipo de tabla
	########
	############################################
	############################################

	#CATEGORIA VENTA
	if($ary[0] eq 'sl_orders'){

		############
		############ sl_orders
		############

		my ($sth_temp) = &Do_SQL("SELECT IF(LENGTH(company_name > 3),company_name, CONCAT(FirstName, ' ', LastName1))  FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE ID_orders = '$ary[1]';");
		$tname = $sth_temp->fetchrow();
	
	#CATEGORIA COMPRAS
	}elsif($ary[0] eq 'sl_purchaseorders'){

		############
		############ sl_purchaseorders
		############

		my ($sth_temp) = &Do_SQL("SELECT ID_vendors, CompanyName FROM sl_vendors INNER JOIN sl_purchaseorders USING(ID_vendors) WHERE ID_purchaseorders = '$ary[1]';");
		($this_id_vendors, $tname) = $sth_temp->fetchrow();
		$anexo1 = $ary[3];

		$consolidated = &is_exportation_order($ary[1]);
	
	#CATEGORIA GASTOS Y PAGOS
	}elsif($ary[0] eq 'sl_bills') {

		############
		############ sl_bills
		############

		my ($sth_temp) = &Do_SQL("SELECT ID_vendors,CompanyName,Memo,Invoice FROM sl_vendors INNER JOIN sl_bills USING(ID_vendors) WHERE ID_bills = '$ary[1]';");
		($this_id_vendors,$tname, $memo, $anexo1) = $sth_temp->fetchrow();

	}elsif($ary[0] eq 'sl_vendors') {

		############
		############ sl_vendors
		############
		my ($sth_temp) = &Do_SQL("SELECT CompanyName FROM sl_vendors WHERE ID_vendors = '$ary[1]';");
		$tname = $sth_temp->fetchrow();

	}elsif($ary[0] eq 'sl_banks_movements'){ #Agregar el Banco que origina el movimiento al campo MEMO de la poliza @ivanmiranda 

		############
		############ sl_banks_movements
		############


		my ($sth_temp) = &Do_SQL("SELECT ban.Name, mov.Refnum, mov.doc_type, mov.RefNumCustom
			FROM sl_banks_movements mov
			INNER JOIN sl_banks ban ON ban.ID_banks = mov.ID_banks
			WHERE mov.ID_banks_movements = $ary[1];");
		($memo, $ref_num, $doc_type, $concept) = $sth_temp->fetchrow();					

	}elsif($ary[0] eq 'sl_creditmemos'){

		############
		############ sl_creditmemos
		############

		my ($sth_temp) = &Do_SQL("SELECT IF(LENGTH(company_name > 3),company_name, CONCAT(FirstName, ' ', LastName1)), sl_creditmemos.ID_creditmemos  FROM sl_customers INNER JOIN sl_creditmemos USING(ID_customers) WHERE ID_creditmemos = '$ary[1]';");
		($tname,$memo) = $sth_temp->fetchrow();

	}

	my $modquery = " AND ID_tableused = '$ary[1]' AND tableused = '$ary[0]' ";
	$modquery .= ($ary[5] > 0)? " AND ID_journalentries = '$ary[5]'":"";
	$modquery .= ($ary[3] > 0 and $ary[2] ne '') ? " AND ID_tablerelated = '$ary[3]' AND tablerelated = '$ary[2]'" : " AND (ID_tablerelated = '0' OR ID_tablerelated IS NULL) AND (tablerelated IS NULL OR tablerelated = '$ary[2]')";
	($ary[0] eq 'sl_vendors' and $ary[2] eq 'sl_bills' and $ary[3] > 0 and $ary[4] eq 'Pagos') and ($ary[0] = $ary[2]) and ($ary[1]  = $ary[3]) and ($modquery = " AND ID_tablerelated = '$ary[3]' AND tablerelated = '$ary[2]' ");

	my ($sth_c2) = &Do_SQL("SELECT ID_accounts,tablerelated,ID_tableused, tableused, ID_tablerelated,Reference,sl_movements.Category,Credebit,ID_segments,EffDate,Amount,YEAR(EffDate) AS TYear, MONTH(EffDate) AS TMonth FROM sl_movements LEFT JOIN sl_accounts USING(ID_accounts) WHERE 1 $modquery AND sl_movements.Status = 'Active' ORDER BY EffDate,Credebit DESC,ID_movements;");
	my ($rows) = $sth_c2->rows();
	my $actual_row = 0; my $sumdebits = 0; $sumcredits = 0;
	#INICIA RECORRIDO POR CADA MOVIMIENTO
	while (my $rec = $sth_c2->fetchrow_hashref) {
		$actual_row++;
		my $account = &load_name('sl_accounts', 'ID_accounts', $rec->{'ID_accounts'}, 'ID_accounting');
		my $account_name = &load_name('sl_accounts', 'ID_accounts', $rec->{'ID_accounts'}, 'Name');
		my $segment_name = &load_name('sl_accounts_segments', 'ID_accounts_segments', $rec->{'ID_segments'}, 'Name');
		my $debit = lc($rec->{'Credebit'}) eq 'debit' ? $rec->{'Amount'} : '';
		my $credit = lc($rec->{'Credebit'}) eq 'credit' ? $rec->{'Amount'} : '';
		my $this_type = $tbl_ref{$ary[0]};
		$sumdebits += round($debit,3);
		$sumcredits += round($credit,3);

		############################################
		############################################
		########
		######## GASTOS DE ATERRIZAJE (COMPRAS)
		########
		############################################
		############################################
		my $index = 0;
		my $s = substr($rec->{'Reference'}, $index, 9);

		$s =~ s/ //g;

		$s =~ s/^\s+|\s+$//g;
		
		my($sql) = '';

		if ($s eq 'VendorGA') {
			$sql = "
				SELECT IFNULL(er.exchange_rate,0)
				FROM sl_wreceipts r
				INNER JOIN sl_exchangerates er ON er.ID_exchangerates = r.ID_exchangerates
				WHERE r.ID_wreceipts = ".$rec->{'ID_tablerelated'}."
			";
			my ($sth_exch) = &Do_SQL($sql);
			my($exchange_rate) = $sth_exch->fetchrow();

			$exchange_rate += 0;

			my $reference = $rec->{'Reference'};
			my $find = "Vendor GA: ";
			my $replace = "";

			$reference =~ s/$find/$replace/g;
			my $vendor_ga = $reference;

			$vendor_ga += 0;

			if ($exchange_rate > 0 and $vendor_ga > 0 and $rec->{'ID_tableused'} > 0 and $rec->{'ID_tablerelated'} > 0 and $rec->{'Amount'} > 0 and $rec->{'tablerelated'} eq 'sl_wreceipts' and $rec->{'tableused'} eq 'sl_purchaseorders') {
				$sql = "
					SELECT CONCAT_WS(':',poa.Type, poa.Description)
					FROM sl_purchaseorders_adj poa
					WHERE 1
					AND poa.ID_purchaseorders = ".$rec->{'ID_tableused'}."
					AND poa.ID_vendors = ".$vendor_ga."
					AND poa.ID_wreceipts = ".$rec->{'ID_tablerelated'}."
					AND FORMAT(poa.Amount,2) = FORMAT(".$rec->{'Amount'}."/".$exchange_rate.",2);
				";
				my ($sth_poa) = &Do_SQL($sql);
				($memo) = $rec->{'Reference'}.':'.$sth_poa->fetchrow();
			}

			if ($cfg{'use_customs_info'} and $cfg{'use_customs_info'} == 1 and $rec->{'tablerelated'} eq 'sl_wreceipts' and $rec->{'ID_tablerelated'} > 0) {
				$sql = "SELECT GROUP_CONCAT(ci.import_declaration_number)
					FROM sl_wreceipts wr
					INNER JOIN sl_skus_trans st ON st.ID_trs = wr.ID_wreceipts
						AND st.tbl_name = 'sl_wreceipts'
					INNER JOIN cu_customs_info ci ON ci.ID_customs_info = st.ID_customs_info
					WHERE wr.ID_wreceipts = ".$rec->{'ID_tablerelated'}."
					;";
				my ($sth_impdecnum) = &Do_SQL($sql);
				($memo) .= '::Pedimento(s):'.$sth_impdecnum->fetchrow();
			}
		}

		############################################
		############################################
		########
		######## NO INVENTARIABLES (COMPRAS)
		########
		############################################
		############################################
		if ($ary[0] eq 'sl_purchaseorders') {
			$add_sql = ($ary[5] > 0)?" AND mov.ID_journalentries = ".$ary[5]."":"";
			$sql = "
				SELECT GROUP_CONCAT(DISTINCT ni.Name)
				FROM sl_purchaseorders po
				INNER JOIN sl_movements mov ON mov.ID_tableused = po.ID_purchaseorders
					AND mov.tableused = 'sl_purchaseorders'
					$add_sql
				INNER JOIN sl_purchaseorders_items poi ON poi.ID_purchaseorders = po.ID_purchaseorders
					AND poi.ID_products >= 500000000
				INNER JOIN sl_noninventory ni ON ni.ID_noninventory = (poi.ID_products-500000000)
				WHERE 1
				AND po.ID_purchaseorders = ".$ary[1]."
				;
			";
			my ($sth_noninv) = &Do_SQL($sql);
			my($tmp_non_inventory) = $sth_noninv->fetchrow();

			if ($tmp_non_inventory) {
				$memo = $tmp_non_inventory;
			}
		}

		############################################
		############################################
		########
		######## 2. Aplicamos filtros especiales por categoria
		########     # $base se refiere al ID actual, sirve como bandera
		########
		############################################
		############################################


		if($ary[0] eq 'sl_orders'){
			#print "$contador : $rec->{'Category'}<br/>";

			if($rec->{'Category'} eq 'Anticipo Clientes'){

				######
				###### Anticipo Clientes
				######
				if($base ne $ary[1]){
					my ($sth_temp) =  &Do_SQL("SELECT Type,CapDate FROM sl_orders_payments WHERE ID_orders = '$ary[1]' AND Status = 'Approved' AND ABS(Amount - $rec->{'Amount'}) = 0 AND CapDate <= '$rec->{'EffDate'}' AND Reason = 'Sale' ORDER BY CapDate DESC LIMIT 1;");
					($memo,$reference)  = $sth_temp->fetchrow();

					$base = $ary[1];

				}

				$rec->{'Reference'} = $reference;

			}elsif($rec->{'Category'} =~ /Ventas|Cambios Fisicos/ ){ #} eq 'Ventas'){
			
				######
				###### Ventas
				######
				my $capdate; my $invoices;

				if($base ne $ary[1] or $basedate ne $rec->{'EffDate'}){
				
					if($ary[3] > 0 and $ary[2] eq 'cu_invoices'){

						my ($sth) = &Do_SQL("SELECT 
												CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
											FROM cu_invoices
											WHERE ID_invoices = '". int($ary[3]) ."';");
						$anexo1 = $sth->fetchrow;

					}

					my ($sth_temp) =  &Do_SQL("SELECT Ptype,PostedDate FROM sl_orders WHERE ID_orders = '$ary[1]';");
					($memo, $pdate)  = $sth_temp->fetchrow();

					my ($sth_temp) = &Do_SQL("SELECT 
												COUNT(*)
												, CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
											FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) 
											WHERE 
												ID_orders = '$ary[1]' 
												AND invoice_type = 'ingreso' 
												AND cu_invoices.Status IN('Certified','InProcess','Confirmed','New','Cancelled')
												/*AND cu_invoices.Date >= '$pdate'*/ 
												GROUP BY 
													ID_invoices 
												ORDER BY 
													FIELD(cu_invoices.Status, 'Certified','InProcess','Confirmed','New','Cancelled'), 
													ABS(DATEDIFF(cu_invoices.Date , '$rec->{'EffDate'}')) 
												LIMIT 1;");
					($invoices, $reference) = $sth_temp->fetchrow();

					(!$invoices) and ($rec->{'Reference'} = 'S/TIMBRAR');

					$base = $ary[1];
					$basedate = $rec->{'EffDate'};

				}

				$rec->{'Reference'} = $reference;

			}elsif($rec->{'Category'} eq 'Devoluciones'){
			
				######
				###### Devoluciones
				######
				my $capdate; my $invoices;

				if($base ne $ary[1] or $basedate ne $rec->{'EffDate'}){

					if($ary[2] eq 'sl_creditmemos'){

						$anexo1 = $ary[3];
						
					} else {

						my ($sth_temp) =  &Do_SQL("SELECT Ptype,ID_creditmemos FROM sl_orders INNER JOIN sl_creditmemos_payments USING(ID_orders) INNER JOIN sl_creditmemos USING(ID_creditmemos) WHERE ID_orders = '$ary[1]' AND sl_creditmemos.Date = '$rec->{'EffDate'}' AND sl_creditmemos.Status = 'Approved';");
						($memo, $anexo1)  = $sth_temp->fetchrow();

					}

					(!$anexo1 and $ary[2] = 'sl_creditmemos') and ($anexo1 = $ary[3]);
					(!$memo) and ($memo = &load_name('sl_creditmemos','ID_creditmemos',$ary[3],'Reference'));
					
					if($ary[2] eq 'cu_invoices') {
						
						my ($sth_temp) = &Do_SQL("SELECT 
													COUNT(*)
													, CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
													FROM cu_invoices 
													WHERE 
														ID_invoices = '$anexo1' 
													LIMIT 1;");
						($invoices, $reference) = $sth_temp->fetchrow();

					} else {
						
						my ($sth_temp) = &Do_SQL("SELECT 
													COUNT(*)
													, CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
												FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) 
												WHERE 
													ID_creditmemos = '$anexo1' 
													AND invoice_type = 'egreso' 
													AND cu_invoices.Date >= '$rec->{'EffDate'}'
													AND cu_invoices.Status IN('Certified','InProcess','Confirmed','New') 
												GROUP BY 
													ID_invoices 
												ORDER BY 
													ABS(DATEDIFF(cu_invoices.Date , '$rec->{'EffDate'}')) 
												LIMIT 1;");
						($invoices, $reference) = $sth_temp->fetchrow();
					}

					(!$invoices) and ($rec->{'Reference'} = 'S/TIMBRAR');
					$base = $ary[1];

				}

				$rec->{'Reference'} = $reference;


			}elsif($rec->{'Category'} eq 'Reembolsos'){

				######
				###### Reembolsos
				######
				if($base ne $ary[1]){

					my ($sth_temp) =  &Do_SQL("SELECT CapDate, AuthCode FROM sl_orders_payments WHERE ID_orders = '$ary[1]' AND Status = 'Credit' AND ABS( ABS(Amount)  - $rec->{'Amount'}) < 1 AND CapDate <= '$rec->{'EffDate'}' AND Reason = 'Refund' ORDER BY CapDate DESC LIMIT 1;");
					($memo, $reference) = $sth_temp->fetchrow();

					if(!$memo){

						my ($sth_temp) =  &Do_SQL("SELECT CapDate, AuthCode FROM sl_orders_payments WHERE ID_orders = '$ary[1]' AND Status = 'Approved' AND ABS( ABS(Amount)  - $rec->{'Amount'}) < 1 AND CapDate <= '$rec->{'EffDate'}' AND Reason = 'Refund' ORDER BY CapDate DESC LIMIT 1;");
						($memo, $reference) = $sth_temp->fetchrow();

					}

					$base = $ary[1];
					$rec->{'Reference'} = $reference;
				}

			}elsif($rec->{'Category'} eq 'Cobranza'){

				######
				###### Cobranza
				######
				if($base ne $ary[1]){

					my ($sth_temp) = &Do_SQL("SELECT sl_banks_movements.RefNum /*, sl_banks_movements.Memo*/
												FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) INNER JOIN sl_banks USING(ID_banks) 
												INNER JOIN 
												(
													SELECT ID_orders_payments, Amount FROM sl_orders_payments WHERE ID_orders = '$ary[1]' AND Status = 'Approved' AND ABS(Amount - $rec->{'Amount'}) < 1 AND CapDate <= '$rec->{'EffDate'}' AND Reason = 'Sale' ORDER BY CapDate DESC LIMIT 1
												)tmp
												ON ID_orders_payments = tableid
												WHERE tablename = 'orders_payments'
												AND tmp.Amount = AmountPaid
												AND sl_banks_movrel.Date = '$rec->{'EffDate'}';");
					($reference) = $sth_temp->fetchrow();

					my ($sth_temp) =  &Do_SQL("SELECT PostedDate FROM sl_orders WHERE ID_orders = '$ary[1]';");
					($pdate)  = $sth_temp->fetchrow();

					my ($sth_temp) = &Do_SQL("SELECT CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) WHERE ID_orders = '$ary[1]' AND invoice_type = 'ingreso' AND cu_invoices.Date >= '$pdate' GROUP BY ID_invoices ORDER BY cu_invoices.id_invoices desc LIMIT 1;");
					($memo) = $sth_temp->fetchrow();

					$base = $ary[1];

				}
				$rec->{'Reference'} = $reference;

			}elsif($rec->{'Category'} eq 'Costos'){

				if($ary[2] eq 'cu_invoices') {
						
					my ($sth_temp) = &Do_SQL("SELECT 
												CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
												FROM cu_invoices 
												WHERE 
													ID_invoices = '". $ary[3] ."' 
												LIMIT 1;");
					($reference) = $sth_temp->fetchrow();

				} else {
					
					my ($sth_temp) = &Do_SQL("SELECT 
												CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
											FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) 
											WHERE 
												ID_creditmemos = '". $ary[3] ."' 
												AND invoice_type = 'egreso' 
												AND cu_invoices.Date >= '". $rec->{'EffDate'} ."'
												AND cu_invoices.Status IN('Certified','InProcess','Confirmed','New') 
											GROUP BY 
												ID_invoices 
											ORDER BY 
												ABS(DATEDIFF(cu_invoices.Date , '$rec->{'EffDate'}')) 
											LIMIT 1;");
					($reference) = $sth_temp->fetchrow();

				}
				$rec->{'Reference'} = $reference;

			}

		}elsif($ary[0] eq 'sl_creditmemos'){

			############
			############ Credit Memos
			############
			$anexo1 = $ary[1];
			$ary[1] = '';
			$rec->{'Reference'} = '';

		}elsif($ary[0] eq 'sl_purchaseorders'){

			if($rec->{'Reference'} ne '' and $rec->{'Reference'} =~ /:/){
			
				my ($t, $this_id_vendors) = split(':',$rec->{'Reference'});
				$this_id_vendors = int($this_id_vendors);
				$rec->{'Reference'} = $t;

				my ($sth_temp) = &Do_SQL("SELECT CompanyName FROM sl_vendors WHERE ID_vendors = '$this_id_vendors';");
				my ($temp_tname) = $sth_temp->fetchrow();

				$tname = ($temp_tname ne '')? $temp_tname:$tname;

				
			}elsif( $rec->{'Reference'} =~ /VCE/i ){
				$rec->{'Reference'} = $rec->{'ID_tablerelated'};
			}

		}
		$anexo1 = $this_id_vendors;
		#ELIMINAMOS COMILLAS DOBLES DEL MEMO PARA QUE NO SE CORTE EL EXCEL
		$memo   =~ s/"//g;

		#($ary[0] eq 'sl_purchaseorders') and ($memo = $rec->{'Reference'}) and ($rec->{'Reference'} = '');
		($ary[0] eq 'sl_purchaseorders' and !$rec->{'Reference'} and $rec->{'ID_tablerelated'}) and ($rec->{'Reference'} = $rec->{'ID_tablerelated'});
		#($ary[2] eq 'sl_bills' and $rec->{'Category'} eq 'Pagos') and ($memo = 'Anticipo') and ($rec->{'Reference'} = '');

		############################################
		############################################
		########
		######## FOLIO FISCAL
		########
		############################################
		############################################
		my $folio = '';

		if ($ary[0] eq 'sl_bills') {
			my ($sth_folio) = &Do_SQL("
				SELECT Invoice
				FROM sl_bills b
				WHERE b.ID_bills = ".$ary[1]."
				;"
			);
			($folio) = $sth_folio->fetchrow();
		}
		
		my $ID_creditmemos;
		if ($ary[0] eq 'sl_creditmemos' or $ary[2] eq 'sl_creditmemos') {
			if ($ary[0] eq 'sl_creditmemos') {
				$ID_creditmemos = $ary[1];
			} elsif ($ary[2] eq 'sl_creditmemos') {
				$ID_creditmemos = $ary[3];
			}
			if ($ID_creditmemos) {
				my $sql = "
					SELECT DISTINCT cmpay.ID_orders
					FROM sl_creditmemos cm
					INNER JOIN sl_creditmemos_payments cmpay ON cmpay.ID_creditmemos = cm.ID_creditmemos
					INNER JOIN sl_orders o ON o.ID_orders = cmpay.ID_orders
					WHERE cm.ID_creditmemos = ".$ID_creditmemos."
					LIMIT 1
				";
				my ($sth_order) = &Do_SQL($sql);
				my ($ID_orders_m) = $sth_order->fetchrow();
				if ($ID_orders_m and $ID_orders_m != $ary[1]) {
					$memo = "Orden=".$ID_orders_m;
				} else {
					$memo = 'N/A';
				}
			}
		}

		############################################
		############################################
		########
		######## CONCEPTO, FOLIO FACTURA, UUID
		########
		############################################
		############################################
		my $ID_orders_memo = ''; 

		if ($ary[0] eq 'sl_orders' and $rec->{'Category'} eq 'Costos') {
			my $filterCost = '';
			$concept = '';
			$folio = '';

			
			if ($ary[0] eq 'sl_orders') {
				$filterCost = " WHERE il.ID_orders = ".$ary[1]." ";
			} 
			if ($ary[2] eq 'sl_creditmemos') {
				$filterCost = " WHERE il.ID_creditmemos = ".$ary[3]." ";
			}
			my $sql = "
				SELECT IFNULL((
					SELECT CASE i.invoice_type
						WHEN 'ingreso' THEN 'factura'
						WHEN 'egreso' THEN 'nota de credito'
						ELSE ''
					END
					FROM cu_invoices_lines il
					INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
					".$filterCost."
					ORDER BY 1 DESC
					LIMIT 1
				),'') concept, IFNULL((
					SELECT CONCAT(i.doc_serial, i.doc_num)
					FROM cu_invoices_lines il
					INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
					".$filterCost."
					ORDER BY 1 DESC
					LIMIT 1
				),'') folioFactura, IFNULL((
					SELECT i.xml_uuid
					FROM cu_invoices_lines il
					INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
					".$filterCost."
					ORDER BY 1 DESC
					LIMIT 1
				),'') uuid;
			";
			my ($sth_order) = &Do_SQL($sql);
			($concept, $rec->{'Reference'}, $folio) = $sth_order->fetchrow();
		}elsif ($ary[0] eq 'sl_orders' and $rec->{'Category'} eq 'Refacturacion') {
			######
			###### Refacturacion
			######
			### ID_tablerelated = ID_invoices
			if( $ary[2] eq 'cu_invoices' and $ary[3] and $ary[3] ne ''){
				my $sth_inv = &Do_SQL("SELECT IF(invoice_type = 'ingreso', 'factura', 'nota de credito') AS invoice_type, CONCAT(doc_serial, doc_num) AS reference, xml_uuid FROM cu_invoices WHERE ID_invoices = ".int($ary[3]).";");
				($concept, $rec->{'Reference'}, $folio) = $sth_inv->fetchrow_array();
			}
		}


		if ($rec->{'Category'} eq 'Costos' and $this_type eq 'Credit Memos' and $rec->{'tableused'} eq 'sl_creditmemos') {
			my ($sth_descript) = &Do_SQL("
				SELECT cm.Description
				FROM sl_creditmemos cm
				WHERE cm.ID_creditmemos = '". $rec->{'ID_tableused'}."'
				;"
			);
			($memo) = $rec->{'ID_tableused'}.'::'.$sth_descript->fetchrow();
			
			my ($sth_folio_memo) = &Do_SQL("
				SELECT IFNULL((
					SELECT i.xml_uuid
					FROM cu_invoices_lines il
					INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
					WHERE il.ID_creditmemos = '". $rec->{'ID_tableused'}."'
					ORDER BY 1 DESC
					LIMIT 1
				),'') uuid;"
			);
			($folio) = $sth_folio_memo->fetchrow();
		}

		####
		#### Evaluamos sumas para mostrar diferencias
		####
		my $modline = $actual_row == $rows ? ",\"". round($sumdebits - $sumcredits,2) .qq"\"\n" : qq"\n";

		$rec->{'Reference'} = $ref_num if( (!$rec->{'Reference'} or $rec->{'Reference'} eq '') and ($ary[0] eq 'sl_banks_movements' and ($doc_type eq 'Check' or $doc_type eq 'NA')) );

		return ($memo,$ary[1],$tname,$ary[3],$rec->{'Reference'});

	} #END WHILE 2
}


#############################################################################
#############################################################################
#   Function: rep_aux_account_payable
#
#       Es: Reporte Auxiliar de Cuentas por Pagar
#       En: 
#
#
#    Created on: 2016-097-22
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: Variable para determinar que se debe generar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_aux_account_payable {
#############################################################################
#############################################################################
	# Obtenemos informacion de la empresa
	&get_company_info();

	$va{'expanditem'} = 3;
	$va{'html_print'};

	if ($in{'action'} and int($in{'id_vendors'})){

		$in{'id_vendors'} = int($in{'id_vendors'});
		$in{'effdate_from'} = &filter_values($in{'effdate_from'});
		$in{'effdate_to'} = &filter_values($in{'effdate_to'});
		my $add_sql = '';

		if ($in{'effdate_from'} and $in{'effdate_to'}) {
			$add_sql .= "AND sl_movements.EffDate BETWEEN '". $in{'effdate_from'} ."' AND '". $in{'effdate_to'} ."'";
		} elsif ($in{'effdate_from'}) {
			$add_sql .=  "AND sl_movements.EffDate >= '". $in{'effdate_from'} ."'";
		} elsif ($in{'effdate_to'}) {
			$add_sql .=  "AND sl_movements.EffDate <= '". $in{'effdate_to'} ."'";
		}else{
			$add_sql .=  "AND sl_movements.EffDate >= '2016-01-01' ";

		}

		$query = "SELECT GROUP_CONCAT(ID_accounts_credit) cuentas
		FROM (
			SELECT sl_vendors.ID_accounts_credit
			FROM sl_vendors
			INNER JOIN sl_accounts ON sl_vendors.ID_accounts_credit = sl_accounts.ID_accounts
			WHERE sl_vendors.ID_accounts_credit !=0
			GROUP BY sl_vendors.ID_accounts_credit
		)tmp";
		my $sth_cuentas = &Do_SQL($query);
		my $row_cuentas = $sth_cuentas->fetchrow_hashref();
		my $cuentas = $row_cuentas->{'cuentas'};

		$add_sql .= ($cuentas and $cuentas ne '')? " AND sl_movements.ID_accounts IN (".$cuentas.")":"";

		$query = "SELECT 
					sl_vendors.ID_vendors
					, sl_vendors.CompanyName
					, sl_vendors.RFC
					, UPPER(sl_vendors.POTerms)POTerms
					, sl_vendors.Status
					, NOW() report_date
					, sl_vendors.ID_accounts_debit
					, sl_vendors.ID_accounts_credit 
					, sl_accounts.ID_accounting
					, CONCAT(sl_accounts.Name)CuentaContableVendor
					, sl_vendors.Currency
				FROM sl_vendors 
				LEFT JOIN sl_accounts ON sl_accounts.ID_accounts = sl_vendors.ID_accounts_credit
				WHERE 
					ID_vendors = ". $in{'id_vendors'} .";";
		my $sth = &Do_SQL($query);
		my $row_vendors = $sth->fetchrow_hashref();
		my $report_date = $row_vendors->{'report_date'};

		$va{'csv'} .= qq|"$va{'company_name'}"\n|;
		$va{'csv'} .= qq|"REPORTE AUXILIAR DE CUENTAS POR PAGAR"\n\n|;
		## Informacin del proveedor
		$va{'csv'} .= qq|"ID PROVEEDOR:","$row_vendors->{ID_vendors}","PROVEEDOR:","$row_vendors->{'CompanyName'}","RFC:","$row_vendors->{'RFC'}","TERMINOS DE COMPRA:","$row_vendors->{'POTerms'}",MONEDA,"$row_vendors->{'Currency'}","ESTATUS:","$row_vendors->{'Status'}","CUENTA CONTABLE ABONO:","|.&format_account($row_vendors->{'ID_accounting'}).qq| [|.$row_vendors->{'ID_accounts_credit'}.qq|] $row_vendors->{'CuentaContableVendor'}"\n\n|;		
		## Cabeceras de Columnas
		$va{'csv'} .= qq|"FECHA","TIPO DE MOVIMIENTO","TOTAL/PARCIAL","ID ORDEN DE COMPRA","FACTURA/NOTA DE CREDITO","FOLIO DE RECEPCION","ID BILL","BANCO","CARGO","ABONO","SALDO","TIPO CAMBIO","DESCRIPCION","ID JOURNAL","FECHA JOURNAL","CAIDA CONTABLE","CUENTA CONTABLE","ID MOVIMIENTO"\n|;


		## Informacion Contable
		$query = "SELECT 
					*
					, sl_journalentries.ID_journalentries
					, sl_journalentries.Date AS JEDate
				FROM sl_movements
				INNER JOIN sl_movements_aux ON sl_movements_aux.ID_movements=sl_movements.ID_movements
				INNER JOIN sl_journalentries ON sl_journalentries.ID_journalentries=sl_movements.ID_journalentries
				INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
				WHERE 
					sl_movements_aux.ID_vendors = ". $in{'id_vendors'} ."
					". $add_sql ."
				ORDER BY
					sl_movements.EffDate
					, sl_movements.ID_movements;";
		$sth_mov = &Do_SQL($query);

		my $saldo = 0;
		my $total_cargo = 0;
		my $total_abono = 0;

		while(my $row_mov = $sth_mov->fetchrow_hashref()){
			
			my $currency_exchange = 1;
			my ($total_partial,$id_purchaseorders,$id_purchaseorders_original,$bill_invoice,$bill_memo,$folio_recepcion,$bill_id,$cargo,$abono,$banco, $caida_contable, $cuenta_contable);
			$id_purchaseorders = $row_mov->{'ID_tableused'};

			## Analisis de Caida contable
			$caida_contable = ($row_mov->{'ID_accounts'} != $row_vendors->{'ID_accounts_credit'})? "INCORRECTA":"CORRECTA";
			$cuenta_contable = &format_account($row_mov->{'ID_accounting'});

			if ($row_mov->{'Credebit'} eq 'Credit') {

				## Credit => Abono
				$abono = $row_mov->{'Amount'};
				$saldo += $row_mov->{'Amount'};
				$total_abono += $row_mov->{'Amount'};

			}else{

				## Debit => Cargo  
				$cargo = $row_mov->{'Amount'};
				$saldo -= $row_mov->{'Amount'};
				$total_cargo += $row_mov->{'Amount'};

			}

			###
			## Datos del BILL
			###
			if ($row_mov->{'tablerelated'} eq 'sl_bills'){

				$query = "SELECT Invoice, Amount, Currency, Memo FROM sl_bills WHERE id_bills = $row_mov->{'ID_tablerelated'};";
				$sth_bill = &Do_SQL($query);
				my $row_bill = $sth_bill->fetchrow_hashref();
				$bill_invoice = $row_bill->{'Invoice'};
				$bill_memo = $row_bill->{'Memo'};
				$bill_id = $row_mov->{'ID_tablerelated'};

			}
			
			
			if ($row_mov->{'tablerelated'} eq 'sl_wreceipts' and lc($row_mov->{'Category'}) eq lc('Compras')){

				###
				## Si es de tipo RECEPCION INVENTARIABLES
				###

				$folio_recepcion = $row_mov->{'ID_tablerelated'};

				if ($folio_recepcion){

					$query = "SELECT IF ((SUM(IFNULL(sl_purchaseorders_items.Qty,0)) - SUM(IFNULL(sl_wreceipts_items.Qty,0))) > 0, 'PARCIAL','TOTAL') AS 'Recepcion'
					FROM sl_wreceipts INNER JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_wreceipts = sl_wreceipts.ID_wreceipts
					INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_items.ID_purchaseorders = sl_wreceipts.ID_purchaseorders
					WHERE sl_wreceipts.ID_wreceipts = ". $folio_recepcion .";";
					$sth_recepcion = &Do_SQL($query);
					my $row_recepcion = $sth_recepcion->fetchrow_hashref();
					$total_partial = $row_recepcion->{'Recepcion'};

				}


				if($row_vendors->{'Currency'} ne $cfg{'acc_default_currency'}){

					## Currency Exchange
					if($folio_recepcion){

						## Inventory Items
						my $q3 = "SELECT exchange_rate FROM sl_wreceipts INNER JOIN sl_exchangerates USING(ID_exchangerates) WHERE ID_wreceipts = ". $folio_recepcion .";";
						my ($sth) = &Do_SQL($q3);
						$currency_exchange = $sth->fetchrow();

					}

				} # acc_default_currency

			}elsif(!$row_mov->{'tablerelated'} and $row_mov->{'tableused'} eq 'sl_purchaseorders' and lc($row_mov->{'Category'}) eq lc('Compras')){

				###
				## Si es de tipo RECEPCION NO INVENTARIABLES
				###

				if($row_vendors->{'Currency'} ne $cfg{'acc_default_currency'}){

					## Non Inventory Items
					my $sumtot = 0;
					$q2 = "SELECT Notes FROM sl_purchaseorders_notes WHERE sl_purchaseorders_notes.ID_purchaseorders = ". $id_purchaseorders ." AND sl_purchaseorders_notes.Notes LIKE 'Warehouse Receipt%';";
					my ($sth) = &Do_SQL($q2);
					while(($this_id_wreceipts_notes) = $sth->fetchrow()){

						if($this_id_wreceipts_notes){

							## Exchange Rate From Notes
							my @ary = split(/\n/, $this_id_wreceipts_notes);
							for(0..$#ary){

								if($ary[$_] =~ /Received: (.+)/){

									$sumtot += int($1);

								}elsif($ary[$_] =~ /Exchange Rate: \$ (.+)/){

									$currency_exchange = &round($1,2);

								}

							}

						}

					}

					$total_partial = 'TOTAL';
					if($sumtot){

						## Comparacion de total recibido vs total PO
						my ($sth) = &Do_SQL("SELECT IF(SUM(sl_purchaseorders_items.Qty) - ". $sumtot ." > 0,'PARCIAL','TOTAL') FROM sl_purchaseorders_items WHERE ID_purchaseorders = ". $id_purchaseorders .";");
						$total_partial = $sth->fetchrow();

					}

				}

			}elsif ($row_mov->{'tablerelated'} eq 'sl_bills'){ #and (lc($row_mov->{'Category'}) eq lc('Pagos') or lc($row_mov->{'Category'}) eq lc('Aplicacion Anticipos AP'))){

				###
				## Si es de tipo PAGOS
				###

				my $wr_currency_exchange = 0;

				if($row_mov->{'tableused'} eq 'sl_purchaseorders'){

					## Currency Exchange From Closest Date
					$query = "SELECT 
								IFNULL(sl_exchangerates.exchange_rate,0)
							FROM 
								sl_wreceipts INNER JOIN sl_exchangerates ON sl_exchangerates.ID_exchangerates = sl_wreceipts.ID_exchangerates
							WHERE 
								sl_wreceipts.ID_purchaseorders = ".$row_mov->{'ID_tableused'}."
								AND sl_wreceipts.Date <= '". $row_mov->{'EffDate'} ."'
							ORDER BY
								sl_wreceipts.ID_wreceipts DESC LIMIT 1;";
					$sth_wr = &Do_SQL($query);
					($wr_currency_exchange) = $sth_wr->fetchrow();			


				}

				if ($row_mov->{'ID_tablerelated'}){

					$query = "SELECT 
								sl_banks.Name
								, sl_banks_movements.currency_exchange
							FROM 
								sl_banks_movrel
							INNER JOIN sl_banks_movements ON sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
							INNER JOIN sl_banks ON sl_banks.ID_banks=sl_banks_movements.ID_banks
							WHERE 
								sl_banks_movrel.tablename = 'bills' 
								AND sl_banks_movrel.tableid = ". $row_mov->{'ID_tablerelated'} .";";

					$sth_bank = &Do_SQL($query);
					($banco, $currency_exchange) = $sth_bank->fetchrow();
					$currency_exchange = $wr_currency_exchange if $wr_currency_exchange;

				}

			}

			## Valores extra requeridos en el reporte
			# my ($memo,$id,$tname)= &get_extra_values_for_accounting_reports($row->{'tableused'},$row->{'ID_tableused'},$row->{'tablerelated'},$row->{'ID_tablerelated'},$row->{'ID_journalentries'});

			$va{'csv'} .= qq|"$row_mov->{'EffDate'}","$row_mov->{'Category'}","$total_partial","$id_purchaseorders","$bill_invoice","$folio_recepcion","$bill_id","$banco","|.&format_price($cargo).qq|","|.&format_price($abono).qq|","|.&format_price($saldo).qq|","|.&format_price($currency_exchange,4).qq|","$bill_memo","$row_mov->{'ID_journalentries'}","$row_mov->{'JEDate'}","$caida_contable","$cuenta_contable [$row_mov->{'ID_accounts'}] $row_mov->{'Name'}","$row_mov->{'ID_movements'}"\n|;

		}


		## Totales
		$va{'csv'} .= qq|"Total de movimientos","","","","","","","","|.&format_price($total_cargo).qq|","|.&format_price($total_abono).qq|","","","","",""\n|;
		$va{'csv'} .= qq|"Saldo final","","","","","","","","","","|.&format_price($saldo).qq|","","","",""\n|;

		###
		##  POs Not Paid Yet
		###
		$query = "SELECT
					sl_bills.Date AS EffDate
					, 'Por Pagar' AS Category 
					, sl_bills_pos.ID_purchaseorders
					, sl_bills.Invoice
					, sl_bills.ID_bills
					, sl_bills_pos.Amount
					, IF(sl_exchangerates.exchange_rate IS NULL, 1,sl_exchangerates.exchange_rate) AS Currency_Exchange
					, sl_bills.Memo
				FROM
					sl_bills 
					INNER JOIN sl_bills_pos ON sl_bills.ID_bills = sl_bills_pos.ID_bills
					INNER JOIN 
					(
						SELECT 
							sl_exchangerates.Date_exchange_rate
							, sl_exchangerates.exchange_rate
						FROM 
							sl_exchangerates
						WHERE
							sl_exchangerates.exchange_rate > 0
						ORDER BY
							DATEDIFF(CURDATE(), sl_exchangerates.Date_exchange_rate)
						LIMIT 1			
					)sl_exchangerates ON sl_exchangerates.Date_exchange_rate = CURDATE()
				WHERE
					1
					AND sl_bills.ID_vendors = ". $in{'id_vendors'} ."
					AND sl_bills.`Status`IN('New','Pending','Processed','To Pay')
				ORDER BY 
					sl_bills.ID_bills;";
		my ($sth_bills) = &Do_SQL($query);
		while(my $row_bills = $sth_bills->fetchrow_hashref()){

			my $this_monetarized = $row_vendors->{'Currency'} ne $cfg{'acc_default_currency'} ? &round($row_bills->{'Amount'} * $row_bills->{'Currency_Exchange'},2) : &round($row_bills->{'Amount'},2);
			$va{'csv'} .= qq|"$row_bills->{'EffDate'}","$row_bills->{'Category'}","","$row_bills->{'ID_purchaseorders'}","$row_bills->{'Invoice'}","","$row_bills->{'ID_bills'}","","|.&format_price(0).qq|","|.&format_price($this_monetarized).qq|","|.&format_price($saldo).qq|","|.&format_price($row_bills->{'Currency_Exchange'}).qq|","$row_bills->{'Memo'}","0","","","",""\n|;

		}

		
		## Informacion de Compras de articulos no inventariables o servicios
		
		## Pie de reporte
		$va{'csv'} .= &report_footer();
		
		## Impresion de archivo CSV
		my $f = lc($cfg{"app_title"}."-Auxiliar-de-Cuentas-por-pagar");
		
		$f =~ s/ /_/g;
		#print "Content-type: text/html\n\n";

		print "Content-Disposition: attachment; filename=$f.csv;";
		print "Content-type: text/csv\n\n";
		print $va{'csv'};
		
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_aux_account_payable.html');
}


#############################################################################
#############################################################################
#   Function: rep_aux_vendor_deposit
#
#       Es: Reporte Auxiliar de Cuentas por Pagar
#       En: 
#
#
#    Created on: 2016-10-14
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: Variable para determinar que se debe generar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_aux_vendor_deposit {
#############################################################################
#############################################################################
	# Obtenemos informacion de la empresa
	&get_company_info();

	$va{'expanditem'} = 3;
	$va{'html_print'};

	if ($in{'action'} and int($in{'id_vendors'})){

		$in{'id_vendors'} = int($in{'id_vendors'});
		$in{'effdate_from'} = &filter_values($in{'effdate_from'});
		$in{'effdate_to'} = &filter_values($in{'effdate_to'});
		my $add_sql = '';

		if ($in{'effdate_from'} and $in{'effdate_to'}) {
			$add_sql .= "AND sl_movements.EffDate BETWEEN '". $in{'effdate_from'} ."' AND '". $in{'effdate_to'} ."'";
		} elsif ($in{'effdate_from'}) {
			$add_sql .=  "AND sl_movements.EffDate >= '". $in{'effdate_from'} ."'";
		} elsif ($in{'effdate_to'}) {
			$add_sql .=  "AND sl_movements.EffDate <= '". $in{'effdate_to'} ."'";
		}else{
			$add_sql .=  "AND sl_movements.EffDate >= '2016-01-01' ";

		}

		$query = "SELECT 
					GROUP_CONCAT(ID_accounts_debit) cuentas
				FROM (
					SELECT 
						sl_vendors.ID_accounts_debit
					FROM 
						sl_vendors INNER JOIN sl_accounts ON sl_vendors.ID_accounts_debit = sl_accounts.ID_accounts
					WHERE 
						sl_vendors.ID_accounts_debit > 0
					GROUP BY 
						sl_vendors.ID_accounts_credit
				)tmp";
		my $sth_cuentas = &Do_SQL($query);
		my $row_cuentas = $sth_cuentas->fetchrow_hashref();
		my $cuentas = $row_cuentas->{'cuentas'};

		$add_sql .= ($cuentas and $cuentas ne '')? " AND sl_movements.ID_accounts IN (".$cuentas.")":"";

		$query = "SELECT 
					sl_vendors.ID_vendors
					, sl_vendors.CompanyName
					, sl_vendors.RFC
					, UPPER(sl_vendors.POTerms)POTerms
					, sl_vendors.Status
					, NOW() report_date
					, sl_vendors.ID_accounts_debit
					, sl_vendors.ID_accounts_credit 
					, sl_accounts.ID_accounting
					, CONCAT(sl_accounts.Name)CuentaContableVendor
					, sl_vendors.Currency
				FROM sl_vendors 
				LEFT JOIN sl_accounts ON sl_accounts.ID_accounts = sl_vendors.ID_accounts_credit
				WHERE 
					ID_vendors = ". $in{'id_vendors'} .";";
		my $sth = &Do_SQL($query);
		my $row_vendors = $sth->fetchrow_hashref();
		my $report_date = $row_vendors->{'report_date'};

		$va{'csv'} .= qq|"$va{'company_name'}"\n|;
		$va{'csv'} .= qq|"REPORTE AUXILIAR DE ANTICIPO A PROVEEDORES"\n\n|;
		## Informacin del proveedor
		$va{'csv'} .= qq|"ID PROVEEDOR:","$row_vendors->{ID_vendors}","PROVEEDOR:","$row_vendors->{'CompanyName'}","RFC:","$row_vendors->{'RFC'}","TERMINOS DE COMPRA:","$row_vendors->{'POTerms'}",MONEDA,"$row_vendors->{'Currency'}","ESTATUS:","$row_vendors->{'Status'}","CUENTA CONTABLE ABONO:","|.&format_account($row_vendors->{'ID_accounting'}).qq| [|.$row_vendors->{'ID_accounts_credit'}.qq|] $row_vendors->{'CuentaContableVendor'}"\n\n|;		
		## Cabeceras de Columnas
		$va{'csv'} .= qq|"FECHA","TIPO DE MOVIMIENTO","ID ORDEN DE COMPRA","ID BILL SERVICIO","FACTURA","ID BILL ANTICIPO","BANCO","CARGO","ABONO","SALDO","TIPO CAMBIO","DESCRIPCION","ID JOURNAL","FECHA JOURNAL","CAIDA CONTABLE","CUENTA CONTABLE","ID MOVIMIENTO"\n|;


		## Informacion Contable
		$query = "SELECT 
					*
					, sl_journalentries.ID_journalentries
					, sl_journalentries.Date AS JEDate
				FROM sl_movements
				INNER JOIN sl_movements_aux ON sl_movements_aux.ID_movements=sl_movements.ID_movements
				INNER JOIN sl_journalentries ON sl_journalentries.ID_journalentries=sl_movements.ID_journalentries
				INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
				WHERE 
					sl_movements_aux.ID_vendors = ". $in{'id_vendors'} ."
					". $add_sql ."
				ORDER BY
					sl_movements.EffDate;";
		$sth_mov = &Do_SQL($query);

		my $saldo = 0;
		my $total_cargo = 0; #326
		my $total_abono = 0;

		while(my $row_mov = $sth_mov->fetchrow_hashref()){
			
			my $currency_exchange = 1;
			my ($bill_id_applied,$id_purchaseorders,$id_purchaseorders_original,$bill_invoice,$bill_memo,$bill_id,$cargo,$banco, $abono, $caida_contable, $cuenta_contable);
			
			## Analisis de Caida contable
			$caida_contable = ($row_mov->{'ID_accounts'} != $row_vendors->{'ID_accounts_credit'})? "INCORRECTA":"CORRECTA";
			$cuenta_contable = &format_account($row_mov->{'ID_accounting'});

			if ($row_mov->{'Credebit'} eq 'Credit') {

				## Credit => Abono
				$abono = $row_mov->{'Amount'};
				$saldo += $row_mov->{'Amount'};
				$total_abono += $row_mov->{'Amount'};

			}else{

				## Debit => Cargo  
				$cargo = $row_mov->{'Amount'};
				$saldo -= $row_mov->{'Amount'};
				$total_cargo += $row_mov->{'Amount'};

			}

			###
			## Datos del BILL(De Pago)
			###
			if ($row_mov->{'tablerelated'} eq 'sl_bills'){

				$query = "SELECT Invoice, Amount, Currency, Memo FROM sl_bills WHERE id_bills = $row_mov->{'ID_tablerelated'};";
				$sth_bill = &Do_SQL($query);
				my $row_bill = $sth_bill->fetchrow_hashref();
				$bill_memo = $row_bill->{'Memo'};
				$bill_id = $row_mov->{'ID_tablerelated'};

			}

			if($row_bill->{'Currency'} ne $cfg{'acc_default_currency'}){

				$query = "SELECT 
							sl_banks.Name
							, sl_banks_movements.currency_exchange
						FROM 
							sl_banks_movrel
						INNER JOIN sl_banks_movements ON sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
						INNER JOIN sl_banks ON sl_banks.ID_banks=sl_banks_movements.ID_banks
						WHERE 
							sl_banks_movrel.tablename = 'bills' 
							AND sl_banks_movrel.tableid = ". $row_mov->{'ID_tablerelated'} .";";

				$sth_bank = &Do_SQL($query);
				($banco, $currency_exchange) = $sth_bank->fetchrow();
				$currency_exchange = $wr_currency_exchange if $wr_currency_exchange;

			}
			
			
			if ($row_mov->{'tableused'} eq 'sl_vendors'){

				###
				## Pago de Anticipo
				###
				$id_purchaseorders = 0;
				$bill_id_applied = 0;

			}elsif($row_mov->{'tableused'} eq 'sl_purchaseorders'){

				###
				## Aplicacion PO
				###
				$id_purchaseorders = $row_mov->{'ID_tableused'};
				$bill_id_applied = 0;

			}elsif ($row_mov->{'tableused'} eq 'sl_bills'){ #and (lc($row_mov->{'Category'}) eq lc('Pagos') or lc($row_mov->{'Category'}) eq lc('Aplicacion Anticipos AP'))){

				###
				## Aplicacion Expense
				###
				$id_purchaseorders = 0;
				$bill_id_applied = $row_mov->{'ID_tableused'};

				$query = "SELECT Invoice Memo FROM sl_bills WHERE id_bills = $row_mov->{'ID_tableused'};";
				$sth_bill = &Do_SQL($query);
				my $row_bill = $sth_bill->fetchrow_hashref();
				$bill_invoice = $row_bill->{'Invoice'};
				$bill_memo = $row_bill->{'Memo'};


			}

			$va{'csv'} .= qq|"$row_mov->{'EffDate'}","$row_mov->{'Category'}","$id_purchaseorders","$bill_id_applied","$bill_invoice","$bill_id","$banco","|.&format_price($cargo).qq|","|.&format_price($abono).qq|","|.&format_price($saldo).qq|","|.&format_price($currency_exchange,4).qq|","$bill_memo","$row_mov->{'ID_journalentries'}","$row_mov->{'JEDate'}","$caida_contable","$cuenta_contable [$row_mov->{'ID_accounts'}] $row_mov->{'Name'}","$row_mov->{'ID_movements'}"\n|;

		}


		## Totales
		$va{'csv'} .= qq|"Total de movimientos","","","","","","","|.&format_price($total_cargo).qq|","|.&format_price($total_abono).qq|","","","","",""\n|;
		$va{'csv'} .= qq|"Saldo final","","","","","","","","","|.&format_price($saldo).qq|","","","",""\n|;

		
		## Pie de reporte
		$va{'csv'} .= &report_footer();
		
		## Impresion de archivo CSV
		my $f = lc($cfg{"app_title"}."-Auxiliar-de-Anticipo-Proveedores");
		
		$f =~ s/ /_/g;
		#print "Content-type: text/html\n\n";

		print "Content-Disposition: attachment; filename=$f.csv;";
		print "Content-type: text/csv\n\n";
		print $va{'csv'};
		
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_aux_vendor_deposit.html');
}


#############################################################################
#############################################################################
#   Function: rep_aux_account_customers
#
#       Es: Reporte Auxiliar de Cuentas por Cobrar(basado en el Reporte Auxiliar de Cuentas por Pagar)
#       En: 
#
#
#    Created on: 2016-10-04
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#
#   Parameters:
#
#      - export: Variable para determinar que se debe generar el reporte exportable
#      - id_customer  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub rep_aux_account_customers {
#############################################################################
#############################################################################
	# Obtenemos informacion de la empresa
	&get_company_info();

	$va{'expanditem'} = 3;
	$va{'html_print'};

	if ($in{'action'} and int($in{'id_customers'})){

		$in{'id_customers'} = int($in{'id_customers'});
		$in{'effdate_from'} = &filter_values($in{'effdate_from'});
		$in{'effdate_to'} = &filter_values($in{'effdate_to'});
		my $add_sql = '';

		if ($in{'effdate_from'} and $in{'effdate_to'}) {
			$add_sql .= "AND sl_movements.EffDate BETWEEN '". $in{'effdate_from'} ."' AND '". $in{'effdate_to'} ."'";
		} elsif ($in{'effdate_from'}) {
			$add_sql .=  "AND sl_movements.EffDate >= '". $in{'effdate_from'} ."'";
		} elsif ($in{'effdate_to'}) {
			$add_sql .=  "AND sl_movements.EffDate <= '". $in{'effdate_to'} ."'";
		}else{
			$add_sql .=  "AND sl_movements.EffDate >= '2016-01-01' ";

		}

		$query = "SELECT GROUP_CONCAT(ID_accounts_debit) cuentas
		FROM (
			SELECT sl_customers.ID_accounts_debit
			FROM sl_customers
			INNER JOIN sl_accounts ON sl_customers.ID_accounts_debit = sl_accounts.ID_accounts
			WHERE sl_customers.ID_accounts_debit > 0
			GROUP BY sl_accounts.ID_accounts
		)tmp";
		my $sth_cuentas = &Do_SQL($query);
		my $row_cuentas = $sth_cuentas->fetchrow_hashref();
		my $cuentas = $row_cuentas->{'cuentas'};

		$add_sql .= ($cuentas and $cuentas ne '')? " AND sl_movements.ID_accounts IN (".$cuentas.")":"";


		$query = "SELECT 
					sl_customers.ID_customers
					, sl_customers.company_name
					, sl_customers.RFC
					, UPPER(sl_customers.PTerms)PTerms
					, sl_customers.`Status`
					, NOW() report_date
					, sl_customers.ID_accounts_debit
					, sl_customers.ID_accounts_credit 
					, sl_accounts.ID_accounting
					, CONCAT(sl_accounts.Name)AccountCustomer
					, sl_customers.Currency
					, sl_customers.`Type`
				FROM sl_customers 
					LEFT JOIN sl_accounts ON sl_accounts.ID_accounts = sl_customers.ID_accounts_debit
				WHERE 
					sl_customers.ID_customers = ". $in{'id_customers'} .";";
		my $sth = &Do_SQL($query);
		my $row_customers = $sth->fetchrow_hashref();
		my $report_date = $row_customers->{'report_date'};

		$va{'csv'} .= qq|"$va{'company_name'}"\n|;
		$va{'csv'} .= qq|"REPORTE AUXILIAR DE CUENTAS POR COBRAR"\n\n|;
		## Informacin del proveedor
		$customer_account = '';
		if( $row_customers->{'ID_accounting'} ){
			$customer_account = &format_account($row_customers->{'ID_accounting'})."[".$row_customers->{'ID_accounts_debit'}."]".$row_customers->{'AccountCustomer'};
		}
		$va{'csv'} .= qq|"ID CLIENTE:","$row_customers->{ID_customers}","CLIENTE:","$row_customers->{'company_name'}","RFC:","$row_customers->{'RFC'}","TERMINOS DE COMPRA:","$row_customers->{'PTerms'}",MONEDA,"$row_customers->{'Currency'}","ESTATUS:","$row_customers->{'Status'}","CUENTA CONTABLE CARGO:","$customer_account"\n\n|;
		## Cabeceras de Columnas		
		$va{'csv'} .= qq|"FECHA","TIPO DE MOVIMIENTO","ID ORDER","CREDIT MEMO","FACTURA/NOTA DE CREDITO","ID ANTICIPO","ID COBRO","CUENTA BANCO","BANCO","CARGO","ABONO","SALDO","DESCRIPCION","REFERENCIA","ID JOURNAL","FECHA JOURNAL","CAIDA CONTABLE","CUENTA CONTABLE","ID MOVIMIENTO"\n|;


		## Informacion Contable
		$query = "SELECT 
					sl_movements_aux.*
					, sl_movements.*
					, sl_journalentries.ID_journalentries
					, sl_journalentries.Date AS JEDate
					, sl_accounts.ID_accounting
					, sl_accounts.Name AS AccName
				FROM sl_movements
					INNER JOIN sl_movements_aux ON sl_movements_aux.ID_movements=sl_movements.ID_movements
					LEFT JOIN sl_journalentries ON sl_journalentries.ID_journalentries=sl_movements.ID_journalentries
					INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
				WHERE 
					sl_movements_aux.ID_customers = ". $in{'id_customers'} ."
					". $add_sql ."
				ORDER BY sl_movements.EffDate, sl_movements.ID_movements, sl_movements.ID_tableused, sl_movements.ID_tablerelated;";
		$sth_mov = &Do_SQL($query);

		my $saldo = 0;
		my $total_cargo = 0;
		my $total_abono = 0;

		while(my $row_mov = $sth_mov->fetchrow_hashref()){
			
			my ($id_order, $id_creditmemo, $invoice, $id_anticipo, $id_cobro, $cargo, $abono, $cuenta_banco, $banco, $cuenta_contable, $descripcion, $referencia, $caida_contable);

			## Analisis de Caida contable
			$caida_contable = ($row_mov->{'ID_accounts'} != $row_customers->{'ID_accounts_debit'})? "INCORRECTA":"CORRECTA";
			$cuenta_contable = &format_account($row_mov->{'ID_accounting'});

			if ($row_mov->{'Credebit'} eq 'Debit') {

				## Debit => Cargo
				$cargo = $row_mov->{'Amount'};
				$saldo += $row_mov->{'Amount'};
				$total_cargo += $row_mov->{'Amount'};

			}else{

				## Credit => Abono
				$abono = $row_mov->{'Amount'};
				$saldo -= $row_mov->{'Amount'};
				$total_abono += $row_mov->{'Amount'};

			}

			### ---------------------------------------------
			### Ventas
			### ---------------------------------------------
			if ($row_mov->{'tableused'} eq 'sl_orders' and lc($row_mov->{'Category'}) eq lc('Ventas')){
				
				$id_order = $row_mov->{'ID_tableused'};

				my $this_sql = '';
				if( $row_mov->{'tablerelated'} eq 'cu_invoices' and $row_mov->{'ID_tablerelated'} ){
					$this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice
								FROM cu_invoices
								WHERE ID_invoices = ".int($row_mov->{'ID_tablerelated'}).";
								";
				} else {
					$this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice
								FROM cu_invoices
									INNER JOIN cu_invoices_lines USING(ID_invoices)
								WHERE ID_orders = ".int($id_order)."
								GROUP BY cu_invoices.ID_invoices;
								";
				}
				my $this_sth = &Do_SQL($this_sql);
				$invoice = $this_sth->fetchrow();

			### ---------------------------------------------
			### Devoluciones
			### ---------------------------------------------
			}elsif ($row_mov->{'tableused'} eq 'sl_orders' and lc($row_mov->{'Category'}) eq lc('Devoluciones')){

				$id_order = $row_mov->{'ID_tableused'};

				if( $row_mov->{'tablerelated'} eq 'sl_creditmemos' ){
					$id_creditmemo = $row_mov->{'ID_tablerelated'};

					my $this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice
									FROM cu_invoices
										INNER JOIN cu_invoices_lines USING(ID_invoices)
									WHERE cu_invoices_lines.ID_creditmemos = ".int($row_mov->{'ID_tablerelated'})."
									GROUP BY cu_invoices_lines.ID_invoices;
									";
					my $this_sth = &Do_SQL($this_sql);
					$invoice = $this_sth->fetchrow();

				} elsif ( $row_mov->{'tablerelated'} eq 'cu_invoices' ){

					my $this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice, cu_invoices_lines.ID_creditmemos
									FROM cu_invoices
										INNER JOIN cu_invoices_lines USING(ID_invoices)	
									WHERE cu_invoices_lines.ID_invoices = ".int($row_mov->{'ID_tablerelated'})."
									GROUP BY cu_invoices_lines.ID_invoices;
									";
					my $this_sth = &Do_SQL($this_sql);
					my $this_rec = $this_sth->fetchrow_hashref();
					$invoice = $this_rec->{'invoice'};
					$id_creditmemo = $this_rec->{'ID_creditmemos'};

				} elsif ( !$row_mov->{'tablerelated'} ){

					my $this_sql = "SELECT sl_creditmemos_payments.ID_creditmemos
										, CONCAT(doc_serial, ' ', doc_num) invoice
										, sl_creditmemos.Reference
										, sl_creditmemos.Description
									FROM sl_creditmemos_payments
										INNER JOIN sl_creditmemos USING(ID_creditmemos)
										INNER JOIN sl_orders_payments USING(ID_orders_payments)
										LEFT JOIN cu_invoices_lines ON sl_creditmemos.ID_creditmemos = cu_invoices_lines.ID_creditmemos
										LEFT JOIN cu_invoices USING(ID_invoices)
									WHERE sl_orders_payments.ID_orders = ".int($id_order)."
									GROUP BY cu_invoices_lines.ID_invoices;
									";
					my $this_sth = &Do_SQL($this_sql);
					my $this_rec = $this_sth->fetchrow_hashref();
					$invoice = $this_rec->{'invoice'};
					$id_creditmemo = $this_rec->{'ID_creditmemos'};
					$referencia = $this_rec->{'Reference'};
					$descripcion = $this_rec->{'Description'};

				}

			}elsif ($row_mov->{'tableused'} eq 'sl_creditmemos' and lc($row_mov->{'Category'}) eq lc('Devoluciones')){

				$id_creditmemo = $row_mov->{'ID_tableused'};

				my $this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice, sl_creditmemos.Status
								FROM cu_invoices
									INNER JOIN cu_invoices_lines USING(ID_invoices)
									INNER JOIN sl_creditmemos ON sl_creditmemos.ID_creditmemos = cu_invoices_lines.ID_creditmemos
								WHERE cu_invoices_lines.ID_creditmemos = ".int($row_mov->{'ID_tableused'})."
								GROUP BY cu_invoices_lines.ID_invoices;
								";
				my $this_sth = &Do_SQL($this_sql);
				my $this_rec = $this_sth->fetchrow_hashref();
				$invoice = $this_rec->{'invoice'};
				$cm_status = $this_rec->{'Status'};
				if( $cm_status eq 'Applied' ){
					$id_order = &load_name('sl_creditmemos_payments', 'ID_creditmemos', int($id_creditmemo), 'ID_orders');
				}

			### ---------------------------------------------
			### Cobranza
			### ---------------------------------------------
			}elsif ($row_mov->{'tableused'} eq 'sl_orders' and lc($row_mov->{'Category'}) eq lc('Cobranza')){

				$id_order = $row_mov->{'ID_tableused'};

				if( $row_mov->{'tablerelated'} eq 'sl_orders_payments' ){
					$id_cobro = $row_mov->{'ID_tablerelated'};

					my $this_sql = "SELECT sl_banks.ID_banks
										, sl_banks.Name AS BankName
										, sl_accounts.ID_accounts
										, sl_accounts.ID_accounting
										, sl_accounts.Name AccName
										, sl_banks_movements.RefNum
										, sl_banks_movements.Memo
									FROM sl_banks_movements
										INNER JOIN sl_banks_movrel ON sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
										INNER JOIN sl_orders_payments ON sl_banks_movrel.tableid = sl_orders_payments.ID_orders_payments AND sl_banks_movrel.tablename = 'orders_payments'
										INNER JOIN sl_banks ON sl_banks_movements.ID_banks = sl_banks.ID_banks
										LEFT JOIN sl_accounts ON sl_banks.ID_accounts = sl_accounts.ID_accounts
									WHERE sl_orders_payments.ID_orders_payments = ".int($row_mov->{'ID_tablerelated'}).";";
					my $this_sth = &Do_SQL($this_sql);
					my $this_rec = $this_sth->fetchrow_hashref();

					$cuenta_banco = &format_account($this_rec->{'ID_accounting'}).' '.$this_rec->{'AccName'};
					$banco = $this_rec->{'BankName'};
					$referencia = $this_rec->{'RefNum'};
					$descripcion = $this_rec->{'Memo'};

				} elsif ( $row_mov->{'tablerelated'} eq 'sl_creditmemos' ){
					$id_creditmemo = $row_mov->{'ID_tablerelated'};

					my $this_sql = "SELECT CONCAT(doc_serial, ' ', doc_num) invoice
									FROM cu_invoices
										INNER JOIN cu_invoices_lines USING(ID_invoices)
									WHERE cu_invoices_lines.ID_creditmemos = ".int($row_mov->{'ID_tablerelated'})."
									GROUP BY cu_invoices_lines.ID_invoices;
									";
					my $this_sth = &Do_SQL($this_sql);
					$invoice = $this_sth->fetchrow();

				} elsif ( $row_mov->{'tablerelated'} eq 'sl_customers_advances' ){
					$id_anticipo = $row_mov->{'ID_tablerelated'};					

					my $this_sql = "SELECT sl_banks.ID_banks
										, sl_banks.Name AS BankName
										, sl_accounts.ID_accounts
										, sl_accounts.ID_accounting
										, sl_accounts.Name AccName
										, sl_banks_movements.RefNum
										, sl_banks_movements.Memo
									FROM sl_banks_movements	
										INNER JOIN sl_banks_movrel ON sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
											AND sl_banks_movrel.tablename = 'customers_advances'
										INNER JOIN sl_banks ON sl_banks_movements.ID_banks = sl_banks.ID_banks
										LEFT JOIN sl_accounts ON sl_banks.ID_accounts = sl_accounts.ID_accounts
									WHERE sl_banks_movrel.tableid = ".int($row_mov->{'ID_tablerelated'}).";";
					my $this_sth = &Do_SQL($this_sql);
					my $this_rec = $this_sth->fetchrow_hashref();

					$cuenta_banco = &format_account($this_rec->{'ID_accounting'}).' '.$this_rec->{'AccName'};
					$banco = $this_rec->{'BankName'};
					$referencia = $this_rec->{'RefNum'};
					$descripcion = $row_mov->{'Reference'};

				} elsif ( !$row_mov->{'tablerelated'} ){
					### Banks Movements -> ID_orders_payments
					my $this_sql = "SELECT ID_orders_payments
									FROM sl_orders_payments	
									WHERE ID_orders = ".int($id_order)."
										AND `Status` = 'Approved'
										AND Captured = 'Yes'
									LIMIT 1;";
					my $this_sth = &Do_SQL($this_sql);
					$id_cobro = $this_sth->fetchrow();

					if( $id_cobro ){
						my $this_sql = "SELECT sl_banks.ID_banks
											, sl_banks.Name AS BankName
											, sl_accounts.ID_accounts
											, sl_accounts.ID_accounting
											, sl_accounts.Name AccName
											, sl_banks_movements.RefNum
											, sl_banks_movements.Memo
										FROM sl_banks_movements	
											INNER JOIN sl_banks_movrel ON sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
												AND sl_banks_movrel.tablename = 'orders_payments'
											INNER JOIN sl_banks ON sl_banks_movements.ID_banks = sl_banks.ID_banks
											LEFT JOIN sl_accounts ON sl_banks.ID_accounts = sl_accounts.ID_accounts
										WHERE sl_banks_movrel.tableid = ".int($id_cobro).";";
						my $this_sth = &Do_SQL($this_sql);
						my $this_rec = $this_sth->fetchrow_hashref();

						$cuenta_banco = &format_account($this_rec->{'ID_accounting'}).' '.$this_rec->{'AccName'};
						$banco = $this_rec->{'BankName'};
						$referencia = $this_rec->{'RefNum'};
						$descripcion = $row_mov->{'Reference'};
					}

				}

			### ---------------------------------------------
			### Ancitipos
			### ---------------------------------------------
			}elsif ($row_mov->{'tableused'} eq 'sl_customers_advances' and $row_mov->{'tablerelated'} eq 'sl_banks_movements' and lc($row_mov->{'Category'}) eq lc('Anticipo Clientes')){

				$id_anticipo = $row_mov->{'ID_tableused'};
				
				my $this_sql = "SELECT sl_banks.ID_banks
									, sl_banks.Name AS BankName
									, sl_accounts.ID_accounts
									, sl_accounts.ID_accounting
									, sl_accounts.Name AccName
									, sl_banks_movements.RefNum
									, sl_banks_movements.Memo
								FROM sl_banks_movements	
									INNER JOIN sl_banks ON sl_banks_movements.ID_banks = sl_banks.ID_banks
									LEFT JOIN sl_accounts ON sl_banks.ID_accounts = sl_accounts.ID_accounts
								WHERE sl_banks_movements.ID_banks_movements = ".int($row_mov->{'ID_tablerelated'}).";";
				my $this_sth = &Do_SQL($this_sql);
				my $this_rec = $this_sth->fetchrow_hashref();

				$cuenta_banco = &format_account($this_rec->{'ID_accounting'}).' '.$this_rec->{'AccName'};
				$banco = $this_rec->{'BankName'};
				$referencia = $this_rec->{'RefNum'};
				$descripcion = $this_rec->{'Memo'};

			}
			
			$va{'csv'} .= qq|"$row_mov->{'EffDate'}","$row_mov->{'Category'}","$id_order","$id_creditmemo","$invoice","$id_anticipo","$id_cobro","$cuenta_banco","$banco","|.&format_price($cargo).qq|","|.&format_price($abono).qq|","|.&format_price($saldo).qq|","$descripcion","$referencia","$row_mov->{'ID_journalentries'}","$row_mov->{'JEDate'}","$caida_contable","$cuenta_contable [$row_mov->{'ID_accounts'}] $row_mov->{'AccName'}","$row_mov->{'ID_movements'}"\n|;

		}

		###
		##  POs Not Paid Yet
		###

		## Totales
		$va{'csv'} .= qq|"Total de movimientos","","","","","","","","","|.&format_price($total_cargo).qq|","|.&format_price($total_abono).qq|","","","","",""\n|;
		$va{'csv'} .= qq|"Saldo final","","","","","","","","","","","|.&format_price($saldo).qq|","","","",""\n|;
		
		## Informacion de Compras de articulos no inventariables o servicios
		
		## Pie de reporte
		$user = $usr{'firstname'};
		$user .= ($usr{'lastname'} ne '')? " ".$usr{'lastname'}:"";
		$user .= ($usr{'middlename'} ne '')? " ".$usr{'middlename'}:"";
		$va{'csv'} .= qq|\n"GENERADO POR:","$user"|;
		$va{'csv'} .= qq|\n"GENERADO EL:","$report_date"|;
		
		## Impresion de archivo CSV
		my $f = lc($cfg{"app_title"}."-Auxiliar-de-Clientes");
		
		$f =~ s/ /_/g;
		#print "Content-type: text/html\n\n";

		print "Content-Disposition: attachment; filename=$f.csv;";
		print "Content-type: text/csv\n\n";
		print $va{'csv'};
		
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('rep_aux_account_customers.html');
}

1;