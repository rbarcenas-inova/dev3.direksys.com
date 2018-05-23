#############################################################################
#############################################################################
#   Function: fin_journalentries
#
#       Es: Genera Reporte en Excel con los movimientos contables asignados a una poliza especifica
#       En: 
#
#
#    Created on: 2013-06-03
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - in_export: Variable para determinar que se debgenerar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_journalentries {
#############################################################################
#############################################################################

	my $cname = lc($cfg{'company_name'});
	$cname =~ s/\s/_/g;
	my $fname =  $cname. '_'  . lc(&trans_txt('acc_journal_entry')) . $in{'id_journalentries'} . '_' . &get_date();
	chop($fname);	

	print "Content-type: application/octet-stream\n";
	print "Content-disposition: attachment; filename=$fname.csv\n\n";
	print "ID_movements, Account Number, Account Name, Entry Date, Journal Entry, Category, Type, Memo, ID, Name, Debit, Credit, Segment, Concept, Reference, Year, Period, Anexo1, Folio, Difference\n";

	my $this_je_records = &journalentries;
	#&cgierr($this_je_records);
	print $this_je_records;
	delete($in{'id_journalentries'});
	
}


#############################################################################
#############################################################################
#   Function: 
#
#       Es: 
#       En: 
#
#
#    Created on: 
#
#    Author: _
#
#    Modifications:
#
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub journalentries {
#############################################################################
#############################################################################

	&Do_SQL("UPDATE sl_movements SET tableused = IF(tableused = '', NULL, tableused), tablerelated = IF(tablerelated = '', NULL, tablerelated) WHERE ID_journalentries = '$in{'id_journalentries'}';");
	############################################
	############################################
	############################################
	#######
	####### Export File
	#######
	############################################
	############################################
	############################################

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE sl_movements.ID_journalentries = '". $in{'id_journalentries'} ."' AND sl_movements.Status = 'Active';");
	$va{'matches'} = $sth->rows();
	my $concept = '';
	my $record = '';

	if ($va{'matches'}>0) {



		my $tot_credit = 0; my $tot_debit = 0; my $base = 0; my $basedate = 0; my $reference;
		my (%tbl_ref) = ('sl_orders'=>'Orders',
						'sl_purchaseorders'=>'Purchase Orders',
						'sl_adjustments'=>'Adjustments',
						'sl_vendors'=>'Deposits',
						'sl_bills'=>'Bills',
						'sl_creditmemos'=>'Credit Memos');


		my $sql1 = "SELECT 
						sl_movements.tableused
						, sl_movements.ID_tableused
						, sl_movements.tablerelated
						, sl_movements.ID_tablerelated
						, sl_movements.Category 
					FROM 
						sl_movements INNER JOIN sl_journalentries on sl_movements.ID_journalentries = sl_journalentries.ID_journalentries
					WHERE 1
						AND sl_movements.ID_journalentries = ". $in{'id_journalentries'} ."
						AND sl_movements.Status = 'Active'
					GROUP BY 
						sl_movements.tablerelated
						, sl_movements.ID_tablerelated
						, sl_movements.tableused
						, sl_movements.ID_tableused 
					ORDER BY 
						sl_movements.tablerelated
						, sl_movements.ID_tablerelated
						, sl_movements.tableused
						, sl_movements.ID_tableused;";

		my ($sth) = &Do_SQL($sql1);
		$contador = 0;
		
		#INICIA RECORRIDO POR CADA TIPO DE JOURNAL(PURCHASE ORDER, ...)
		while (my (@ary) = $sth->fetchrow_array){
			
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
				#$contador++;
				#print "$contador : SELECT IF(LENGTH(company_name > 3),company_name, CONCAT(FirstName, ' ', LastName1))  FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE ID_orders = '$ary[1]';<br/>";
				$tname = $sth_temp->fetchrow();
			
			#CATEGORIA GASTOS Y PAGOS
			}elsif($ary[0] eq 'sl_bills' or $ary[2] eq 'sl_bills') {

				############
				############ sl_bills (Puede ser O.C. pero el Bill es el que tiene el dueno)
				############
				my $this_id = ($ary[0] eq 'sl_purchaseorders' or $ary[0] eq 'sl_vendors') ?  int($ary[3]) : int($ary[1]);

				my ($sth_temp) = &Do_SQL("SELECT ID_vendors,CompanyName,Memo,Invoice FROM sl_vendors INNER JOIN sl_bills USING(ID_vendors) WHERE ID_bills = ". $this_id .";");
				($this_id_vendors,$tname, $memo, $anexo1) = $sth_temp->fetchrow();


			#CATEGORIA COMPRAS
			}elsif($ary[0] eq 'sl_purchaseorders'){

				############
				############ sl_purchaseorders
				############

				my ($sth_temp) = &Do_SQL("SELECT ID_vendors, CompanyName FROM sl_vendors INNER JOIN sl_purchaseorders USING(ID_vendors) WHERE ID_purchaseorders = ". int($ary[1]) .";");
				($this_id_vendors, $tname) = $sth_temp->fetchrow();
				$anexo1 = $ary[3];

				$consolidated = &is_exportation_order($ary[1]);
			
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


				my ($sth_temp) = &Do_SQL("SELECT 
											ban.Name
											, mov.Refnum
											, mov.doc_type
											, mov.RefNumCustom
										FROM 
											sl_banks_movements mov
											INNER JOIN sl_banks ban ON ban.ID_banks = mov.ID_banks
										WHERE 
											mov.ID_banks_movements = ". $ary[1] .";");
				($memo, $ref_num, $doc_type, $concept) = $sth_temp->fetchrow();					

			}elsif($ary[0] eq 'sl_creditmemos'){

				############
				############ sl_creditmemos
				############

				my ($sth_temp) = &Do_SQL("SELECT IF(LENGTH(company_name > 3),company_name, CONCAT(FirstName, ' ', LastName1)), sl_creditmemos.ID_creditmemos  FROM sl_customers INNER JOIN sl_creditmemos USING(ID_customers) WHERE ID_creditmemos = ". $ary[1] .";");
				($tname,$memo) = $sth_temp->fetchrow();

			}


			my $modquery = " AND sl_movements.ID_tableused = ". $ary[1] ." AND sl_movements.tableused = '". $ary[0] ."' ";
			$modquery .= ($ary[3] > 0 and $ary[2] ne '') ? " AND sl_movements.ID_tablerelated = ". $ary[3] ." AND sl_movements.tablerelated = '". $ary[2] ."' " : " AND (sl_movements.ID_tablerelated = '0' OR sl_movements.ID_tablerelated IS NULL) AND (sl_movements.tablerelated IS NULL OR sl_movements.tablerelated = '". $ary[2] ."')";
			($ary[0] eq 'sl_vendors' and $ary[2] eq 'sl_bills' and $ary[3] > 0 and $ary[4] eq 'Pagos') and ($ary[0] = $ary[2]) and ($ary[1]  = $ary[3]) and ($modquery = " AND sl_movements.ID_tablerelated = ". $ary[3] ." AND sl_movements.tablerelated = '". $ary[2] ."' ");

			
			my $sql2 = "SELECT 
							sl_movements.ID_movements
							, sl_accounts.ID_accounts
							, sl_movements.tablerelated
							, sl_movements.ID_tableused
							, sl_movements.tableused
							, sl_movements.ID_tablerelated
							, sl_movements.Reference
							, sl_movements.Category
							, sl_movements.Credebit
							, sl_movements.ID_segments
							, sl_movements.EffDate
							, sl_movements.Amount
							, YEAR(sl_movements.EffDate) AS TYear
							, MONTH(sl_movements.EffDate) AS TMonth 
							, IF(sl_movements.ID_journalentries IS NULL, 0, sl_movements.ID_journalentries) AS JournalID
							, IF(sl_journalentries.Status IS NULL,'---',sl_journalentries.Status)AS JournalStatus 
						FROM 
							sl_movements 
							LEFT JOIN sl_accounts ON sl_movements.ID_accounts = sl_accounts.ID_accounts
							LEFT JOIN sl_journalentries ON sl_movements.ID_journalentries = sl_journalentries.ID_journalentries
						WHERE 1
							AND sl_movements.ID_journalentries = ". $in{'id_journalentries'} ."
							". $modhistory ."
							". $modquery ."
							AND sl_movements.Status = 'Active' 
						ORDER BY 
							sl_movements.EffDate
							, sl_movements.Credebit DESC
							, sl_movements.ID_movements;";


			my ($sth_c2) = &Do_SQL($sql2);
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
					
					my $by_journalentries = ($in{'id_journalentries'})? "AND mov.ID_journalentries = ".$in{'id_journalentries'} : '';
					
					$sql = "
						SELECT GROUP_CONCAT(DISTINCT ni.Name)
						FROM sl_purchaseorders po
						INNER JOIN sl_movements mov ON mov.ID_tableused = po.ID_purchaseorders
							AND mov.tableused = 'sl_purchaseorders'
							".$by_journalentries."
						INNER JOIN sl_purchaseorders_items poi ON poi.ID_purchaseorders = po.ID_purchaseorders
							AND poi.ID_products >= 500000000
						INNER JOIN sl_noninventory ni ON ni.ID_noninventory = (poi.ID_products-500000000)
						WHERE 1
						AND po.ID_purchaseorders = ".$ary[1]."
						;";

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
															ABS(DATEDIFF(cu_invoices.Date , '$rec->{'EffDate'}')),
															cu_invoices.ID_invoices 
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
						$concept = 'nota de credito';


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
					#### Creditmemos - Customers
					if( $rec->{'Category'} eq 'Devoluciones' and $ary[2] eq 'sl_customers' ){									
						my ($sth_temp) = &Do_SQL("SELECT 
													COUNT(*)
													, CONCAT(doc_serial, doc_num, IF(cu_invoices.Status = 'Certified','', CONCAT('-',cu_invoices.Status) ))  
												FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) 
												WHERE 
													ID_creditmemos = ".int($anexo1)." 
													AND invoice_type = 'egreso' 
													AND cu_invoices.Date >= '$rec->{'EffDate'}'
													AND cu_invoices.Status IN('Certified','InProcess','Confirmed','New') 
												GROUP BY 
													ID_invoices 
												ORDER BY 
													ABS(DATEDIFF(cu_invoices.Date , '$rec->{'EffDate'}')) 
												LIMIT 1;");
						($invoices, $rec->{'Reference'}) = $sth_temp->fetchrow();
						$concept = 'nota de credito';							
					}

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
						$filterCost = ($ary[3] > 0 and $ary[2] eq 'cu_invoices') ? " WHERE i.ID_invoices = ".$ary[3]." " : " WHERE il.ID_orders = ".$ary[1]." ";
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
							SELECT 
								CASE i.invoice_type
									WHEN 'ingreso' THEN 'factura'
									WHEN 'egreso' THEN 'nota de credito'
									ELSE ''
								END
							FROM cu_invoices_lines il
								INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
							WHERE il.ID_creditmemos = ".$rec->{'ID_tableused'}."
							ORDER BY 1 DESC
							LIMIT 1
						),'') concept, IFNULL((
							SELECT CONCAT(i.doc_serial, i.doc_num)
							FROM cu_invoices_lines il
								INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
							WHERE il.ID_creditmemos = ".$rec->{'ID_tableused'}."
							ORDER BY 1 DESC
							LIMIT 1
						),'') folioFactura, IFNULL((
							SELECT i.xml_uuid
							FROM cu_invoices_lines il
								INNER JOIN cu_invoices i ON i.ID_invoices = il.ID_invoices
							WHERE il.ID_creditmemos = ".$rec->{'ID_tableused'}."
							ORDER BY 1 DESC
							LIMIT 1
						),'') uuid;"
					);
					($concept, $rec->{'Reference'}, $folio) = $sth_folio_memo->fetchrow();
				}

				## Category -> Diario
				if ($rec->{'Category'} eq 'Diario'){
					my ($sth) = &Do_SQL("SELECT FieldValue FROM sl_movements_auxiliary WHERE ID_movements = ".$rec->{'ID_movements'}." AND FieldName = 'Description';");
					$memo = $sth->fetchrow_array();
				}
				

				####
				#### Evaluamos sumas para mostrar diferencias
				####
				my $modline = $actual_row == $rows ? ",\"". round($sumdebits - $sumcredits,2) .qq"\"\n" : qq"\n";

				$rec->{'Reference'} = $ref_num if( (!$rec->{'Reference'} or $rec->{'Reference'} eq '') and ($ary[0] eq 'sl_banks_movements' and ($doc_type eq 'Check' or $doc_type eq 'NA')) );
				
				$record .=  "\"$rec->{'ID_movements'}\",".&format_account($account) . ",\"$account_name\",\"$rec->{'EffDate'}\",\"$rec->{'JournalID'}\",\"$rec->{'Category'}\",\"$this_type\",\"$memo\",\"$ary[1]\",\"$tname\",\"$debit\",\"$credit\",\"$segment_name\",\"$concept\",\"$rec->{'Reference'}\",\"$rec->{'TYear'}\",\"$rec->{'TMonth'}\",\"$anexo1\",\"$folio\"" . $modline;
	
			} #END WHILE 2

		} #END WHILE 1

		return $record;
	}

}


#############################################################################
#############################################################################
#   Function: fin_journalentries_full
#
#       Es: Genera Reporte en Excel de uno o varios Journal Entries
#       En: 
#
#
#    Created on: 2013-06-03
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - in_action: Variable para determinar que se debgenerar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_journalentries_full {
#############################################################################
#############################################################################

	if( $in{'action'} ){

		my ($query);

		## Filter by Date
		if ($in{'from_date'}){
			$query .= " AND EffDate >= '". $in{'from_date'} ."' ";
		}
		
		$in{'to_date'}	= &get_sql_date() if !$in{'to_date'};
		$query .= " AND EffDate <= '". $in{'to_date'} ."' ";
		
		
		## Filter by Journal Entry
		if ($in{'id_journalentries'} ne ''){

			$in{'id_journalentries'} = int($in{'id_journalentries'});
			$query .= " AND sl_journalentries.ID_journalentries = '". $in{'id_journalentries'} ."' ";
			&Do_SQL("UPDATE sl_movements SET tableused = IF(tableused = '', NULL, tableused), tablerelated = IF(tablerelated = '', NULL, tablerelated) WHERE ID_journalentries = ". $in{'id_journalentries'} .";");

		}elsif($in{'id_journalentries'} eq ''){

			delete $in{'id_journalentries'};

		}
		

		## Filter by Status
		if ($in{'status'}){

			$in{'status'} =~ s/\|/','/g;
			$query .= " AND sl_journalentries.Status IN('". $in{'status'} ."') ";

		}$in{'status'} =~ s/','/\|/g;

		if ($in{'category'}){

			$in{'category'} =~ s/\|/','/g;
			$query .= " AND sl_movements.Category IN('". $in{'category'} ."') ";

		}$in{'category'} =~ s/','/\|/g;

		my ($sth) = &Do_SQL("SELECT 
								DISTINCT sl_journalentries.ID_journalentries 
							FROM 
								sl_movements INNER JOIN sl_journalentries ON sl_journalentries.ID_journalentries = sl_movements.ID_journalentries 
							WHERE 
								1 
								". $query ." 
								AND sl_movements.Status = 'Active';");

		my ($rows) = $sth->rows();
		if($rows){

			my $cname = lc($cfg{'company_name'});
			$cname =~ s/\s/_/g;
			my $fname =  $cname. '_'  . lc(&trans_txt('acc_journal_entry')) . $in{'id_journalentries'} . '_' . &get_date();
			chop($fname);	

			print "Content-type: application/octet-stream\n";
			print "Content-disposition: attachment; filename=$fname.csv\n\n";
			print "ID Movements, Account Number, Account Name, Entry Date, Journal Entry, Category, Type, Memo, ID, Name, Debit, Credit, Segment, Concept, Reference, Year, Period, Anexo1, Folio, Difference\n";

			while (my ($this_id_journal) = $sth->fetchrow()){

				$in{'id_journalentries'} = $this_id_journal;
				my $this_je_records = &journalentries;
				#&cgierr($this_je_records);
				print $this_je_records;
				delete($in{'id_journalentries'});

			}

			return;

		}else{

				$va{'message'} = &trans_txt('notmatch');

		}

	}
	

	print "Content-type: text/html\n\n";
	print &build_page('fin_journalentries_full.html');


}



1;
