sub po_update{
# --/*----*/--------------------------------------------------
	my $action="";
	print "Content-type: text/html\n\n";
	if(!&check_permissions('mer_po','_edit','')){ return 'error'; };
	$in{'id_po_items'} = int($in{'id_po_items'});

	&Do_SQL("START TRANSACTION;");

	if ($in{'field'} eq 'qty'){
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Qty='".&filter_values($in{'new'})."' WHERE ID_purchaseorders_items='$in{'id_po_items'}' AND Received=0");
		$action = "po_updated_qty";
	}elsif($in{'field'} eq 'taxp'){
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Tax_percent=IF($in{'new'} > 0, $in{'new'}/100,0) WHERE ID_purchaseorders_items='$in{'id_po_items'}' AND Received=0");
		$action = "po_updated_tax";	
	}elsif($in{'field'} eq 'price'){
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Price='".&filter_values($in{'new'})."' WHERE ID_purchaseorders_items='$in{'id_po_items'}' AND Received=0");
		$action = "po_updated_price";
	}elsif($in{'field'} eq 'total'){

		my $total_amt = &filter_values($in{'new'});

		### Se obtiene los datos del servicio
		my $sth_pitems = &Do_SQL("SELECT sl_purchaseorders_items.ID_products 
									, sl_purchaseorders_items.Qty
									, sl_purchaseorders_items.Tax_percent
									, sl_services.ID_services
									, sl_services.Tax AS tax_pct_service
								FROM sl_services
									INNER JOIN sl_purchaseorders_items ON sl_services.ID_services = RIGHT(sl_purchaseorders_items.ID_products, 4)							
								WHERE sl_purchaseorders_items.ID_purchaseorders_items = ".int($in{'id_po_items'}).";");
		my $po_items = $sth_pitems->fetchrow_hashref();

		### Porcentaje de IVA
		my $tax_pct = ( $po_items->{'Tax_percent'} > 0 ) ? $po_items->{'Tax_percent'} : $po_items->{'tax_pct_service'};
		$tax_pct = round($tax_pct / 100, 4) if( $tax_pct > 1 );

		my $sth_ret_count = &Do_SQL("SELECT COUNT(*) ret_exits
									FROM sl_vars_config
									WHERE Command = 'service_account_retention' 
										AND IDValue = ".int($po_items->{'ID_services'})."
										AND LOWER(Largecode) = 'credit';");
		my $ret_exits = $sth_ret_count->fetchrow();

		my $total_net_amt = 0;
		if( int($ret_exits) > 0 ){

			$total_net_amt = $total_amt;
			if( int($ret_exits) == 2 ){
				$total_net_amt = round($total_amt * &filter_values($cfg{'factor_ret_pmt'}), 3) if($cfg{'factor_ret_pmt'});
			} elsif( int($ret_exits) == 1 ){
				$total_net_amt = round($total_amt * &filter_values($cfg{'factor_ret_fght'}), 3) if($cfg{'factor_ret_fght'});				
			}

		} else {

			$total_net_amt = round($total_amt / (1+$tax_pct), 3);

		}		
		### Precio unitario y monto del IVA
		my $price = round($total_net_amt / $po_items->{'Qty'}, 3);
		my $tax = round($total_net_amt * $tax_pct, 2);

		### Se calculan los taxes de las posibles retenciones
		my $log = '';
		my ($tax_hold, $tax_other, $tax_hold_pct, $tax_other_pct) = (0,0,0,0);
		my $sth_ret = &Do_SQL("SELECT Code AS id_accounts
									, Subcode AS percent
									, Largecode AS credebit
									, Description AS extra_account
								FROM sl_vars_config
								WHERE Command = 'service_account_retention' 
									AND IDValue = ".int($po_items->{'ID_services'})."
									AND LOWER(Largecode) = 'credit';");
		while( my $rec = $sth_ret->fetchrow_hashref() ){	

			if( $rec->{'extra_account'} eq 'no' ){

				$tax_hold_pct = (!$rec->{'percent'}) ? 0 : round(($rec->{'percent'} / 100), 4);
				$tax_hold += ($tax_hold_pct > 0) ? round(($tax_hold_pct * $total_net_amt), 2) : 0;
				$log .= "Tax Hold. :: round(($tax_hold_pct * $total_net_amt), 2)<br>\n";

			}else{

				$tax_other_pct = (!$rec->{'percent'}) ? 0 : round(($rec->{'percent'} / 100), 4);
				$tax_other += ($tax_other_pct > 0) ? round(($tax_other_pct * $total_net_amt), 2) : 0;
				$log .= "Tax Other :: round(($tax_other_pct * $total_net_amt), 2)<br>\n";

			}

		}

		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET 
								Price = '".$price."' 
								, Tax_percent = '".$tax_pct."' 				
								, Tax = '".$tax."' 
								, Total = '".$total_amt."' 
								, Tax_withholding_pct = '".$tax_hold_pct."' 
								, Tax_withholding = '".$tax_hold."' 
								, Tax_other_pct = '".$tax_other_pct."' 
								, Tax_other = '".$tax_other."' 
							 WHERE ID_purchaseorders_items = '".$in{'id_po_items'}."' AND Received=0");
		$action = "po_updated_total";

	}

	### Si la linea del PO no es de servicios, entonces se actualiza
	if( $in{'field'} ne 'total' ){
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Tax = IF(Tax_percent > 0, Qty * Price * Tax_percent,0) WHERE ID_purchaseorders_items = '$in{'id_po_items'}';");
		my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Total = Qty * Price + Tax WHERE ID_purchaseorders_items = '$in{'id_po_items'}';");
	}

	$in{'db'} = "sl_purchaseorders";
	$id_po = &load_name('sl_purchaseorders_items','ID_purchaseorders_items',$in{'id_po_items'},'ID_purchaseorders');
	&auth_logging($action,$id_po);

	&Do_SQL("COMMIT;");

	print "ok";
}

#############################################################################
#############################################################################
#   Function: wreceipts_update
#
#       Es: Actualiza la cantidad de producto recibido
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Pe🈣
#    Modifications:
#
#        - Modified on *27/11/2012* by _Enrique Pe𠝠: Se agrego la funcion para actualizar la cantidad recibida
#
#   Parameters:
#
#       - new = Nueva cantidad a modificar
#	- id_wreceipts_items =  id del registro a modificar 
#  Returns:
#
#      - Error/ok dependiendo del resultado
#
#   See Also:
#
#
#
sub wreceipts_update{
#############################################################################
#############################################################################	
	print "Content-type: text/html\n\n";	
	if(!&check_permissions('mer_wreceipts','_edit','')){ return 'error'; };	
	if ($in{'field'} eq 'qty'){
		my ($sth) = &Do_SQL("UPDATE sl_wreceipts_items SET Qty='".&filter_values($in{'new'})."' WHERE ID_wreceipts_items = '$in{'id_wreceipts_items'}'");		
	}
	$in{'db'} = "sl_wreceipts";
	$id_wreceipts = &load_name('sl_wreceipts_items','ID_wreceipts_items',$in{'id_wreceipts_items'},'ID_wreceipts');
	&auth_logging('Wreceipts updated Qty = '.&filter_values($in{'new'}),$id_wreceipts);
	print "ok";
}

#############################################################################
#############################################################################
#   Function: po_adj_validate
#
#       Es: Valida o invalida un Gasto de Aterrizaje
#       En: 
#
#
#    Created on: 11/07/2016  
#
#    Author: Gilberto QC
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#      - ERROR/OK dependiendo del resultado
#
#   See Also:
#
sub po_adj_validate{
#############################################################################
#############################################################################

	my $result = 'OK';	
	my $perm_validate = &check_permissions('mer_po_validate_adj','','');

	if( $in{'id_po_adj'} and int($in{'type_val'}) >= 0 and $perm_validate ){
		&Do_SQL("UPDATE sl_purchaseorders_adj SET Validate=".int($in{'type_val'})." WHERE ID_purchaseorders_adj='".int($in{'id_po_adj'})."';");
	}else{
		$result = 'ERROR';
	}

	print "Content-type: text/html\n\n";
	print $result;
}

#############################################################################
#############################################################################
#   Function: po_items_segments_update
#
#       Es: Actualiza el ID_segments del items de un PO-Services
#       En: 
#
#
#    Created on: 06/01/2017
#
#    Author: Gilberto QC
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#      - ERROR/OK dependiendo del resultado
#
#   See Also:
#
sub po_items_segments_update{
#############################################################################
#############################################################################

	my $result = 'OK';	
	#my $perm_validate = &check_permissions('mer_po_validate_adj','','');

	if( int($in{'id_segments'}) >= 0 ){
		&Do_SQL("UPDATE sl_purchaseorders_items SET ID_segments=".int($in{'id_segments'})." WHERE ID_purchaseorders_items='".int($in{'id_po_items'})."';");
	}else{
		$result = 'ERROR';
	}

	print "Content-type: text/html\n\n";
	print $result;
}

#############################################################################
#############################################################################
#   Function: po_deductible_update
#
#       Es: Actualiza el campo deductible de la OC
#       En: 
#
#
#    Created on: 31/01/2017
#
#    Author: Gilberto QC
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#      - ERROR/OK dependiendo del resultado
#
#   See Also:
#
sub po_deductible_update{
#############################################################################
#############################################################################

	my $result = 'ERROR: '.&trans_txt('perms_insufficient_perms').' or '.&trans_txt('invalid_params');
	
	$in{'deductible'} = &filter_values($in{'deductible'});

	$in{'status'} = &load_name('sl_purchaseorders', 'ID_purchaseorders', int($in{'id_po'}), 'Status');
	if( $in{'deductible'} and ($in{'status'} eq 'In Process' or $in{'status'} eq 'New' or $in{'status'} eq 'Auth Request') and &check_permissions('mer_po','_edit','') ){
		&Do_SQL("UPDATE sl_purchaseorders SET Deductible='".$in{'deductible'}."' WHERE ID_purchaseorders=".int($in{'id_po'}).";");
		$result = 'OK';

		$in{'id_purchaseorders'} = $in{'id_po'};
		$in{'db'} = 'sl_purchaseorders';
		&auth_logging('mer_po_deductible',$in{'id_purchaseorders'});
	}
	
	print "Content-type: text/html\n\n";
	print $result;
}

#############################################################################
#############################################################################
#   Function: po_receipts_services
#
#       Es: Controla el proceso de recepcioón de OC de Servicios
#       En: 
#
#
#    Created on: 27/01/2017
#
#    Author: Gilberto QC
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#      - 
#
#   See Also:
#
sub po_receipts_services{
#############################################################################
#############################################################################

	$in{'id_purchaseorders'} = $in{'view'};

	my $sth_po = &Do_SQL("SELECT sl_purchaseorders.*
								, sl_vendors.RFC
								, sl_vendors.CompanyName
								, sl_vendors.Category
								, sl_vendors.Currency
								, sl_vendors.POTerms
								, sl_vendors.PaymentMethod
							FROM sl_purchaseorders 
								INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors = sl_vendors.ID_vendors
							WHERE sl_purchaseorders.ID_purchaseorders = ".int($in{'id_purchaseorders'}).";");
	my $po = $sth_po->fetchrow_hashref();
	### Info. PO
	$in{'deductible'} = $po->{'Deductible'};
	### Info. Vendor
	$in{'rfc_vendor'} = $po->{'RFC'};
	$in{'vendor'} = $po->{'CompanyName'};
	$in{'id_vendors'} = $po->{'ID_vendors'};
	$in{'currency'} = $po->{'Currency'};
	$in{'poterms'} = $po->{'POTerms'};

	###### -------------------------------------------------------
	######  Procesa la recepción de los servicios
	###### -------------------------------------------------------
	if( int($in{'po_receipt_services'}) == 1 and int($in{'action'}) == 1 and $po->{'Auth'} eq 'Approved' and $po->{'Status'} eq 'In Process' ){

		my %response;
		my (@poi_services, @poi_segments, @poi_amounts, @poi_taxes, $amount);
		my $vendor_category = $po->{'Category'};
		my $deductible = $po->{'Deductible'};

		$response{'result'} = 200;
		&Do_SQL("START TRANSACTION;");

		###
		### Se crea la recepción
		###
		my $sth_wr = &Do_SQL("INSERT INTO sl_wreceipts SET 
								ID_vendors = ".$in{'id_vendors'}."
								, ID_purchaseorders = ".$in{'id_purchaseorders'}."
								, InvoiceDate = CURDATE()
								, `Type` = 'Warehouse Receipt'
								, `Status` = 'Processed'
								, Date = CURDATE()
								, Time = CURTIME()
								, ID_admin_users = ".$usr{'id_admin_users'}.";");
		my $id_wreceipts = $sth_wr->{'mysql_insertid'};
		&auth_logging('wreceipt_created', $id_wreceipts);

		&auth_logging('purchaseorder_wreceipts_added', $id_wreceipts);

		### Se cancela la contabilidad de provisiones
		my @params = ($in{'id_purchaseorders'}, $id_wreceipts);
		&accounting_keypoints('po_services_cancell_prov_'.$vendor_category, \@params);

		### Se determina si se cuenta con la factura
		my $invoice_in = ( $in{'invoice'} and $in{'invoice'} ne '' ) ? 1 : 0;

		### Se crean los items de la recepción
		my $sth_po_items = &Do_SQL("SELECT 
										sl_purchaseorders_items.*
										, sl_services.Name AS ServiceName
										, sl_accounts_segments.Name AS SegmentName
									FROM sl_purchaseorders_items 
										INNER JOIN sl_services ON RIGHT(sl_purchaseorders_items.ID_products, 4) = sl_services.ID_services
										LEFT JOIN sl_accounts_segments ON sl_purchaseorders_items.ID_segments = sl_accounts_segments.ID_accounts_segments
									WHERE ID_purchaseorders = ".$in{'id_purchaseorders'}." 
										AND LEFT(ID_products, 1) = 6 
										AND (Qty - Received) > 0;");
		my $cont = 0;
		while( my $rec_items = $sth_po_items->fetchrow_hashref() ){
			
			### Se crea el item de la recepción
			my $sth_wr_items = &Do_SQL("INSERT INTO sl_wreceipts_items SET 
											ID_wreceipts = ".$id_wreceipts."
											, ID_products = ".$rec_items->{'ID_products'}."
											, Qty = ".$rec_items->{'Qty'}."
											, Date = CURDATE()
											, Time = CURTIME()
											, ID_admin_users = ".$usr{'id_admin_users'}.";");
			my $this_note = "Product: (".$rec_items->{'ID_products'}.") ".$rec_items->{'ServiceName'}."\n";
			$this_note .= "PO Area: ".$rec_items->{'SegmentName'}."\n";
			$this_note .= "Received: ".$rec_items->{'Qty'}."\n";
			$this_note .= "Price: ".$rec_items->{'Price'}."\n";

			### Se guarda la nota de la recepción correspondiente al item actual
			&Do_SQL("INSERT INTO sl_wreceipts_notes SET 
						ID_wreceipts = ".$id_wreceipts." 
						, Notes = '".$this_note."'
						, Type = 'Low'
						, Date = CURDATE()
						, Time = CURTIME()
						, ID_admin_users = ".$usr{'id_admin_users'}.";");

			### Se actualiza la cantidad recibida del item actual
			&Do_SQL("UPDATE sl_purchaseorders_items SET Received = ".$rec_items->{'Qty'}." WHERE ID_purchaseorders_items = ".$rec_items->{'ID_purchaseorders_items'}.";");

			### Se guarda la nota del PO correspondiente al item actual
			&Do_SQL("INSERT INTO sl_purchaseorders_notes SET 
						ID_purchaseorders = ".$in{'id_purchaseorders'}." 
						, Notes = 'W. Receipt: ".$id_wreceipts."\n".$this_note."'
						, Type = 'Low'
						, Date = CURDATE()
						, Time = CURTIME()
						, ID_admin_users = ".$usr{'id_admin_users'}.";");
			
			### Se genera la contabilidad del servicio correspondiente al item actual
			my @params = ($in{'id_purchaseorders'}, $rec_items->{'ID_purchaseorders_items'}, $id_wreceipts, $deductible, $invoice_in);
			&accounting_keypoints('po_wreceipt_services_in_'.$vendor_category, \@params);

			### Info. para Bills
			# $poi_services[$cont] = substr($rec_items->{'ID_products'}, -4);
			# $poi_segments[$cont] = $rec_items->{'ID_segments'};
			# $poi_amounts[$cont] = ($rec_items->{'Price'} * $rec_items->{'Qty'});
			# $poi_taxes[$cont] = $rec_items->{'Tax'};
			# $amount += ($poi_amounts[$cont] + $rec_items->{'Tax'});
			$amount += $rec_items->{'Total'};

			$cont++;

		}

		###
		### Se crea el Bill
		### 
		#------------------------
		# Autorización para pago
		#------------------------
		my $sql_auth_bill = '';
		if( $cfg{'default_auth_bill'} > 0 ){
			$sql_auth_bill = " , AuthBy = ".$usr{'id_admin_users'}.", AuthToPay=1 ";
		}
		#------------------------
		my $sql_bill = "INSERT INTO sl_bills SET
							ID_vendors = ".$in{'id_vendors'}."
							, Type = '".$in{'type'}."'
							, Invoice = '".$in{'invoice'}."'
							, Currency = '".$in{'currency'}."'
							, Date_exchange_rate = NULL 
							, currency_exchange = NULL 
							, Amount = ".$amount."
							, Memo = '".$in{'memo'}."'
							, BillDate = '".$in{'billdate'}."'
							, DueDate = '".$in{'duedate'}."'
							".$sql_auth_bill."
							, PaymentMethod = '".$po->{'PaymentMethod'}."'
							, Status = 'New'
							, Date = CURDATE()
							, Time = CURTIME()
							, ID_admin_users = ".$usr{'id_admin_users'}."
						;";
		my $sth_bill = &Do_SQL($sql_bill);
		my $id_bills = $sth_bill->{'mysql_insertid'};
		### Se crea el item en bills_pos
		my $sql_bill = "INSERT INTO sl_bills_pos SET
							ID_bills = ".int($id_bills)."
							, ID_purchaseorders = ".int($in{'id_purchaseorders'})."
							, ID_purchaseorders_adj = 0							
							, Amount = ".$amount."							
							, Date = CURDATE()
							, Time = CURTIME()
							, ID_admin_users = ".$usr{'id_admin_users'}."
						;";
		my $sth_bill = &Do_SQL($sql_bill);

		###
		### Se modifica la contabilidad para ligarla al nuevo Bill
		###
		&Do_SQL("UPDATE sl_movements SET 
					#Reference = CONCAT('WReceipts: ', ID_tablerelated),
					tablerelated = 'sl_bills',
					ID_tablerelated = ".int($id_bills)." 
				WHERE tableused = 'sl_purchaseorders' 
					AND ID_tableused = ".int($in{'id_purchaseorders'})." 
					AND tablerelated = 'sl_wreceipts' 
					AND ID_tablerelated = ".int($id_wreceipts)."
					AND EffDate = CURDATE()
				;");


		### Se crean las lineas de los Bills - Expenses
		# ITEMS:foreach my $i (0 .. $#poi_services ){

		# 	### Se obtienen las cuentas contables del servicio
		# 	my ($id_account, $id_tax_account) = &load_name('sl_services', 'ID_services', $poi_services[$i], 'PurchaseID_accounts, TaxPurchaseID_accounts');

		# 	if( int($id_account) == 0 or int($id_tax_account) == 0 ){
		# 		$response{'result'} = 400;
		# 		$response{'error'} = 'Falta configurar las cuentas contables del servicio: '.$poi_services[$i];
		# 		last;
		# 	}

		# 	### Se crea la linea de la cuenta
		# 	my $sql = "INSERT INTO sl_bills_expenses SET 
		# 					ID_bills = ".int($id_bills)."
		# 					, Amount = ".$poi_amounts[$i]."
		# 					, ID_accounts = ".$id_account."
		# 					, ID_segments = ".$poi_segments[$i]."
		# 					, Deductible = '".$in{'deductible'}."'
		# 					, Date = CURDATE()
		# 					, Time = CURTIME()
		# 					, ID_admin_users = ".$usr{'id_admin_users'}.";";
		# 	my $sth = &Do_SQL($sql);
		# 	my $id_billss_exp = $sth->{'mysql_insertid'};

		# 	### Se crea la linea del IVA
		# 	if( $poi_taxes[$i] ){
		# 		my $sql = "INSERT INTO sl_bills_expenses SET 
		# 						ID_bills = ".int($id_bills)."
		# 						, Amount = ".$poi_taxes[$i]."
		# 						, ID_accounts = ".$id_tax_account."
		# 						, ID_segments = ".$poi_segments[$i]."
		# 						, Related_ID_bills_expenses = ".$id_billss_exp."
		# 						, Deductible = '".$in{'deductible'}."'
		# 						, Date = CURDATE()
		# 						, Time = CURTIME()
		# 						, ID_admin_users = ".$usr{'id_admin_users'}.";";
		# 		&Do_SQL($sql);
		# 	}

		# }


		###
		### Se actualiza el Status del PO
		###
		&Do_SQL("UPDATE sl_purchaseorders SET 
					`Status` = 'Received' 
				WHERE ID_purchaseorders = ".$in{'id_purchaseorders'}.";");
		$in{'status'} = 'Received';
		&auth_logging('mer_po_received', $in{'id_purchaseorders'});		


		###
		### Validación y confirmación del resultado del proceso
		###
		if( $response{'result'} == 200 ){
			
			###
			### Se liga el Bill con la factura(cfdi)
			###
			if( $in{'invoice'} and $in{'invoice'} ne '' ){
				## Reescribe la conexion a Base de Datos
				&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});
				&Do_SQL("UPDATE direksys2_repo.e".$in{'e'}."_xml_info_vendor SET
							ID_bills = ".int($id_bills).",
							ID_vendors = ".int($in{'id_vendors'})."
						WHERE uuid = '".$in{'invoice'}."'
						LIMIT 1;");
			}
			
			&Do_SQL("COMMIT;");

		} else {

			&Do_SQL("ROLLBACK;"); ## debug

		}	


		###
		### Envió de respuesta
		###
		use JSON;
		print "Content-type: application/json\n\n";
		print encode_json(\%response);


	###### -------------------------------------------------------
	######  Genera el formulario para iniciar la recepción
	###### -------------------------------------------------------
	} elsif( int($in{'po_receipt_services'}) == 1 and $po->{'Auth'} eq 'Approved' and $po->{'Status'} eq 'In Process' ) {		

		###---------------------------
		### Se obtiene la lista de facturas pendientes por pagar
		###---------------------------	
		## Reescribe la conexion a Base de Datos
		&connect_db_w($cfg{'repo_db'},$cfg{'repo_host'},$cfg{'repo_user'},$cfg{'repo_pw'});
		my $sql = "SELECT 
						xml_info_vendor.ID_xml_info_vendor
						, CONCAT(xml_info_vendor.serie, xml_info_vendor.folio) invoice					
						, xml_info_vendor.uuid
						, DATE(xml_info_vendor.fecha_certificacion) fecha_certificacion					
						, CONCAT(xml_info_vendor.total,' ',xml_info_vendor.moneda)total
					FROM direksys2_repo.e".$in{'e'}."_xml_info_vendor xml_info_vendor
					WHERE 1
						AND Status = 'Certified'
						AND rfc = '".$in{'rfc_vendor'}."'
						AND id_vendors is null
						AND id_bills is null
						AND tipo = 'Ingreso'
					ORDER BY ID_xml_info_vendor DESC;";
		my $sth = &Do_SQL($sql);

		$va{'cfdi_vendor_list'} = '';
		while( my $rec = $sth->fetchrow_hashref() ){
			$va{'cfdi_vendor_list'} .= '<option value="'.$rec->{'ID_xml_info_vendor'}.'" data-uuid="'.$rec->{'uuid'}.'">'.$rec->{'uuid'}.' || ['.$rec->{'fecha_certificacion'}.'] || $ '.$rec->{'total'}.'</option>';
		}

		###---------------------------

		print "Content-type: text/html\n\n";
		print &build_page('po_receipt_services.html');

	} else {

		print "Content-type: text/html\n\n";		
		print &build_page('unauth_small.html');

	}
}

#############################################################################
#############################################################################
#   Function: mer_products
#
#       Es: Actualiza la cantidad de producto recibido
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Pe🈣
#    Modifications:
#
#        - Modified on *27/11/2012* by _Enrique Pe𠝠: Se agrego la funcion para actualizar la cantidad recibida
#
#   Parameters:
#
#       - new = Nueva cantidad a modificar
#	- id_wreceipts_items =  id del registro a modificar 
#  Returns:
#
#      - Error/ok dependiendo del resultado
#
#   See Also:
#
#
#
sub mer_products{
#############################################################################
	print "Content-type: text/html\n\n";
	my ($opt) = int($in{'opt'});
    my ($error) = 0;
	my ($saved);
	if ($in{'action'}){
		## update & Validate based on Option
		if(!$in{'id_products'} or !$in{'opt'}) {
			$va{'message'} .= &trans_txt('invalid');
			$error++;
		}

		if(!$error) {
			my @dbcols;
			my @cols;

			if($opt == 1) {
				@dbcols = ('Packing', 'Handling', 'WarehouseHandling', 'ProductType', 'ProductDocs', 'free_shp_opt', 'ExpressShipping' );
				@cols = ('packing', 'handling', 'warehousehandling', 'producttype', 'productdocs', 'free_shp_opt', 'expressshipping' );
			}elsif($opt == 2) {
				@dbcols = ('WholesaleOrigin', 'SLTV_NetCost', 'WholesalePriceOrigin', 'Tariff', 'WholesalePrice', 'Discount' );
				@cols = ('wholesaleorigin', 'sltv_netcost', 'wholesalepriceorigin', 'tariff', 'wholesaleprice', 'discount' );
			}elsif($opt == 3) {
				@dbcols = ('BreakEvenVolume', 'Margin', 'AirTimeMinutes', 'MAP', 'MSRP');
				@cols = ('breakevenvolume', 'margin', 'airtimeminutes', 'map', 'msrp');
			}elsif($opt == 5) {
				@dbcols = ('ID_brands', 'ManufacterSKU', 'Duties', 'Insurance', 'MinimumStock', 'MaximumStock', 'ValidateStock' ,'edt', 'DropShipment', 'ID_services_related', 'ID_products_speech', 'IsFinal', 'web_available', 'user_type' ) ;
				@cols = ('id_brands', 'manufactersku', 'duties', 'insurance', 'minimumstock', 'maximumstock', 'validatestock' ,'edt', 'dropshipment', 'id_services_related', 'id_products_speech', 'isfinal', 'web_available', 'user_type');
			}elsif($opt == 6) {
				@dbcols = ('SmallDescription', 'Description', 'SmallDescription_en', 'Description_en');
				@cols = ('smalldescription', 'description', 'smalldescription_en', 'description_en');
			}

			for (0..$#cols) {
				#($in{$cols[$_]}) and ($queryupd .= ",". $dbcols[$_] . " = '" . &filter_values($in{$cols[$_]}) . "'" );
                ($queryupd .= ",". $dbcols[$_] . " = '" . &filter_values($in{$cols[$_]}) . "'" );
			}
			#if($queryupd){
				$queryupd = "UPDATE sl_products SET Date = Date $queryupd  WHERE ID_products = '$in{'id_products'}';";
				my ($sth) = &Do_SQL($queryupd);
				$saved = $sth->rows;
				if($saved){
					$va{'message'} = &trans_txt('record_updated');
				}
				
			#}

			if($opt == 4) {
				&set_products_dids($in{'id_products'},$in{'dids'});
			}
			
		}
	}
    
	
	
	
    &load_cfg('sl_products');
	%in = &get_record('ID_products',$in{'id_products'},'sl_products');
	$in{'opt'} = $opt;
	if($in{'action'} && $saved == 0){
		$va{'message'} .= &trans_txt('invalid');
	}
    
	print &build_page("ajaxbuild:products_opt".$opt.".html")
}


#############################################################################
#############################################################################
#   Function: parts_productions_edit
#
#       Es: Actualiza las tablas in/out de skus productions
#       En: 
#
#
#    Created on: 03/25/2013  16:20:10
#
#    Author: _RB_
#
#    Modifications:
#		- 2013/07/18 _RB_ : Se agrega validacion para que el producto no se repita en In/Out
#
#   Parameters:
#
#       - id = id_parts_productions
#		- type = in/out
#		- ids = string with pair of idwl:qty
#		- nid = New pair of values
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_mer_parts_productions>
#
sub parts_productions_edit{
#############################################################################
#############################################################################

	my $id_parts_productions = int($in{'id'});
	my $typeprev = &filter_values($in{'type'});
	my ($id_warehouses) = int($in{'id_warehouses'});
	my ($keyword) = &filter_values($in{'keyword'});
	my ($idppi) = int($in{'idppi'});
	my ($data_in) = &filter_values($in{'data_in'});

	print "Content-type: text/html\n\n";

	my ($prefix, $type) = split(/:/, $typeprev);
	my $action = &load_name('sl_parts_productions','ID_parts_productions',$id_parts_productions,'Type');

	if($type =~ /add|drop/) {	

		if($type eq 'add' and (!$id_warehouses or !$id_parts_productions or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif( $type eq 'drop' and !$idppi ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my $str,$str_out,$t;

		if($type eq 'add') {

			my ($id_products, $location , $qty, $pct) = split(/:/, $data_in);

			#################
			################# In/Out validation
			#################
			#my $this_prefix =  $prefix eq 'out' ? 'in' : 'out';
			#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_productions_items WHERE ID_parts_productions = '$id_parts_productions' AND In_out = '". $this_prefix ."' AND ID_products = '". $id_products ."';");
			#my ($totp) = $sth->fetchrow();

			#if($totp > 0) {
			#	print "Error: In/Out must be different";
			#	return;
			#}

			############################
			############################ IMPLODE VALIDATION
			############################

			if(lc($action) eq 'implode' and $prefix eq 'out'){

				####
				#### Se valida que el SKU de salida no seá igual a ninguno de entrada
				####
				my ($sth) = &Do_SQL("SELECT COUNT(*)
									FROM sl_parts_productions_items
									WHERE ID_parts_productions = '".int($id_parts_productions)."'
										AND In_out = 'in' 
										AND ID_products = '$id_products';");
				my ($pinvalid) = $sth->fetchrow();

				if(int($pinvalid) > 0){
					print "Error: Implode accepts only a different sku";
					return;
				}

				####
				#### Implode Out. Debe ser un mismo sku con cantidad maxima igual al sku in
				####
				my ($sth) = &Do_SQL("SELECT 
										COUNT(*)
									FROM sl_parts_productions_items
									WHERE ID_parts_productions = '".int($id_parts_productions)."'
									AND In_out = 'out';");
				my ($pinvalid) = $sth->fetchrow();

				if($pinvalid){
					print "Error: Implode accepts only 1 sku for outcome";
					return;
				}else{

					my ($sth) = &Do_SQL("SELECT 
											SUM(Qty) AS QtyIn
										FROM sl_parts_productions_items
										WHERE ID_parts_productions = '".int($id_parts_productions)."'
										AND In_out = 'in' 
										GROUP BY ID_products 
										ORDER BY SUM( Qty ) DESC 
										LIMIT 1;");
					my ($maxqty) = $sth->fetchrow();

					if( abs($maxqty - $qty) > 0){
						#print "Error: ". &trans_txt('mer_parts_productions_implode_qtyout_different') . " $maxqty";
						#return;
					}

				}

			}elsif(lc($action) eq 'implode' and $prefix eq 'in') {

				####
				#### Implode In. Cantidad maxima igual que los anteriores se validara cuando se mande procesar
				####
				
				

			############################
			############################ EXPLODE VALIDATION
			############################

			}elsif( lc($action) eq 'explode' and $prefix eq 'out' ) {

				####
				#### Explode Out. Porcentaje no puede sumar mayor a 100.
				####

				# if(!$pct) {
				# 	print "Error: " .&trans_txt('reqfields_short');
				# 	return;	
				# }else{
				# 	my ($sth) = &Do_SQL("SELECT SUM(Pct) + $pct FROM sl_parts_productions_items WHERE ID_parts_productions = '$id_parts_productions' AND In_out = 'out' GROUP BY ID_parts_productions;");
				# 	my ($totpct) = $sth->fetchrow();

				# 	if($totpct > 100) {
				# 		print "Error: Pct > 100";
				# 		return;		
				# 	}

				# }

			}elsif(lc($action) eq 'explode' and $prefix eq 'in') {

				####
				#### Explode In. Solo debe haber un sku de entrada
				####

				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_productions_items WHERE ID_parts_productions = '$id_parts_productions' AND In_out = 'in';");
				my ($tin) = $sth->fetchrow();

				if($tin) {
					print "Error: Explode accepts Only 1 Item In";
					return;		
				}
				$pct = 100;
			}



			($pct < 1) and ($pct *= 100);

			$location = &load_name('sl_locations','ID_warehouses',$id_warehouses,'Code') if lc($location) eq 'location';
			my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_parts_productions_items SET ID_parts_productions = '$id_parts_productions', ID_products = '".int($id_products)."',/* ID_warehouses = '$id_warehouses',*/
					Location = '".&filter_values($location)."', In_out = '".lc($prefix)."', Qty = '".int($qty)."', Pct = '".&filter_values($pct)."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			$t = $sth->rows();

		}elsif($type eq 'drop'){	
			my ($sth) = &Do_SQL("DELETE FROM sl_parts_productions_items WHERE ID_parts_productions_items = '$idppi';");
			$t = $sth->rows();
		}

		#if(!$t) {
		#	print "Error: Duplicated Record $t" if $type eq 'add';
		#	print "Error: Record Not Dropped $t" if $type eq 'drop';
		#	return;
		#}

		my ($sth) =  &Do_SQL("SELECT ID_parts_productions_items, sl_parts_productions_items.ID_products, sl_parts.Name, Location,Qty, In_out, 
						IF('$action' = 'explode',Pct,'N/A'), IF( UPC IS NOT NULL, UPC , 'N/A')
	                    FROM sl_parts INNER JOIN sl_parts_productions_items
	                    ON ID_parts = RIGHT(sl_parts_productions_items.ID_products,4) 
	                    LEFT JOIN sl_skus ON sl_parts_productions_items.ID_products = ID_sku_products
	                    WHERE ID_parts_productions = '$id_parts_productions'
	                    AND In_out = '".lc($prefix)."'
	                    ORDER BY ID_parts_productions_items;");
		while(my($idppi,$id_parts,$name,$location,$qty,$type,$pct,$upc) = $sth->fetchrow()){

			$str_out .= qq|<tr id="row-$type-$idppi">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$type-$idppi" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=|.($id_parts - 400000000).qq|">|.&format_sltvid($id_parts).qq|</a></td>\n
								<td>$name</td>\n
								<td>$upc</td>\n
								<td align="center">$location</td>\n 
								<td align="right">$qty</td>\n 
								<td align="right">$pct</td>\n 
							</tr>|;	
		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n 
								<td align="center" class="menu_bar_title">UPC</td>\n 
								<td align="center" class="menu_bar_title">Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
								<td align="center" class="menu_bar_title">Pct (%)</td>\n
							</tr>\n
							$str_out
						</table>\n|;
			print $str_out;				
		}


	}

	return;
}


#############################################################################
#############################################################################
#   Function: parts_productions_save
#				
#       Es: Guarda las tablas in/out de skus productions
#       En: 
#
#
#    Created on: 03/25/2013  19:20:10
#
#    Author: RB
#    Modifications:
#   Parameters:
#
#		- id_parts_productions = id from table
#       - ins = in values
#		- outs = out values
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_mer_parts_productions>
#
sub parts_productions_save {
#############################################################################
#############################################################################

	print "Content-type: text/html\n\n";
	my $id = int($in{'id_parts_productions'});

	if(!$id or !$in{'in'} or !$in{'out'}){
		print "Error: Data was not received";
		return;
	}

	my ($sth) = &Do_SQL("SELECT SUM(Qty_after) FROM sl_parts_productions_items WHERE ID_parts_productions = '$id';");
	my ($t) = $sth->fetchrow();

	if($t){
		print "It seems that the process was previously finished";
		return;
	}
	## Dropping past items
	&Do_SQL("DELETE FROM sl_parts_productions_items WHERE ID_parts_productions = '$id';");

	for (0..1){

		my $type = $_ == 0 ? 'In' : 'Out';
		my @items = split(/,/, $in{lc($type)});

		for(0..$#items){
			my  ($idwl,$qty) = split(/:/, $items[$_]);

			if($idwl and $qty){

				my $id_parts = substr(&load_name('sl_warehouses_location', 'ID_warehouses_location', $idwl, 'ID_products'),-4);
				
				if($id_parts) {
					&Do_SQL("INSERT IGNORE INTO sl_parts_productions_items SET 
					        ID_parts_productions = '$id', ID_parts = '$id_parts', ID_warehouses_location = '$idwl', In_out = '$type', Qty = '$qty', 
							Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'; ");
				}

			}

		}

	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_productions_items WHERE ID_parts_productions = '$id';");
	my ($tf) = $sth->fetchrow();

	if($tf){
		&Do_SQL("UPDATE sl_parts_productions SET Status = 'In Process' WHERE ID_parts_productions = '$id';");
		&auth_logging('mer_parts_productions_itemadded');
		print "ok";
	}else{
		print "Error: Data not saved";
	}

	return;

}

#############################################################################
#############################################################################
#   Function: load_vendor_data
#
#       Es: Extrae informacion del proveedor
#       En: Extract information from the vendor
#
#
#    Created on: 24/04/2013  06:09
#
#    Author: Alejadro Diaz
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#  Returns:
#
#      - **
#
#   See Also:
#
#
#
sub load_vendor_data{
#############################################################################
#############################################################################
	my $id_vendors = $in{'id_vendors'};
	my $output='';

	my ($sth) = &Do_SQL("SELECT CreditDays,Currency,POTerms,CompanyName FROM sl_vendors INNER JOIN sl_terms ON sl_terms.Name=sl_vendors.POTerms WHERE ID_vendors = '$id_vendors';");
	my ($creditdays,$currency,$poterms,$company) = $sth->fetchrow_array();

	if ($currency ne '' and $cfg{'acc_default_currency'} ne $currency){
		$exchange_rate = 'show';
	}else{
		$exchange_rate = 'hide';
	}

	$output .= $creditdays.'|'.$currency.'|'.$poterms.'|'.$company.'|'.$exchange_rate;

	
	print "Content-type: text/html\n\n";
	print $output;
}


sub get_poterms{
#########################################################################################
#########################################################################################

	print "Content-type: text/html\n\n";
	my $output = 0;
	my $tmp = 0;
	my $output = int($in{'id_vendors'}) > 0 ? &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"POTerms") : '';

	if(!output) {
		print "Error: Vendor without Payment Terms";	
		return;
	}
	
	print $output;
	return;
}

#############################################################################
#############################################################################
#	Function: bills_payments_refnum
#
#	Created on: 09/05/2013  12:02:10
#
#	Author: Alejandro Diaz
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:Consecutive number for Ref Num in control payment of bills
#
#	See Also:
#
#
#
sub bills_payments_refnum {
#############################################################################
#############################################################################
	my $value;

	my ($sth) = &Do_SQL("SELECT (VValue+1)value FROM sl_vars WHERE VName='bills_refnum' LIMIT 1;");
	$value = $sth->fetchrow_array();

	if (!$value) {
		my ($sth) = &Do_SQL("INSERT INTO `sl_vars` (`VName`, `VValue`, `Definition_En`, `Definition_Sp`) VALUES ('bills_refnum', '1', 'Consecutive number for Ref Num in control payment of bills', 'Numero consecutivo para control de Ref Num en pago de de bills')");
		$value=1;

	}

	my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue='$value' WHERE VName='bills_refnum' LIMIT 1;");

	print "Content-type: text/html\n\n";
	print $value;
}


#############################################################################
#############################################################################
# Function: overlay_po_items_segment
#
# Es: Carga formulario para agregar/editar direcciones de clientes.
# En: Load to add/edit customer addresses.
#
# Created on: 25/02/2012 10:33:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub overlay_po_items_segment {
#############################################################################
#############################################################################

	use HTML::Entities;
	use Data::Dumper;

	print "Content-type: text/html\n\n";

	$in{'id_po'} = int($in{'id_po'});
	$in{'id_row'} = int($in{'id_row'});
	$in{'ids'} = int($in{'ids'});


	print &build_page('ajaxbuild/overlay_po_segment.html');
	return;
}

#############################################################################
#############################################################################
#   Function: mer_parts
#
#       Es: Edicion de las Especificaciones Tecnicas de un SKU
#       En: Edition of the technical specifications of a SKU
#
#
#    Created on: 25/06/2014  12:20:10
#
#    Author: ISC Alejandro Diaz
#    Modifications:
#
#        -
#
#   Parameters:
#
#       -
#
#   See Also:
#
#
#
sub mer_parts{
#############################################################################
	print "Content-type: text/html\n\n";
	my ($opt) = int($in{'opt'});
    my ($error) = 0;
	my ($saved);
	if ($in{'action'}){
		## Update & Validate based on Option
		if (!$in{'id_parts'} or !$in{'opt'}) {
			$va{'message'} .= &trans_txt('invalid');
			$error++;
		}

		if (!$error and &check_permissions('mer_parts_tech_specs_edition','','')) {
			my @dbcols;
			my @cols;

			if ($opt == 1) {
				@dbcols = ('Description1', 'Description2', 'Description3', 'Description4');
				@cols = ('description1', 'description2', 'description3', 'description4');
			}

			for (0..$#cols) {
                $queryupd .= ($in{$cols[$_]})? ",". $dbcols[$_] . " = '" . &filter_values($in{$cols[$_]}) . "'" : "";
			}

			$queryupd = "REPLACE INTO cu_skus_descriptions SET ID_parts='$in{'id_parts'}' $queryupd , Date=CURDATE() , Time=CURTIME() , ID_admin_users='$usr{'id_admin_users'}'";
			my ($sth) = &Do_SQL($queryupd);
			$saved = $sth->rows;
			if ($saved){
				$va{'message'} = &trans_txt('record_updated');
				
				# LOG
				$in{'db'} = "sl_parts";
				&auth_logging(&trans_txt('mer_parts_tecs_specs_mod'),$in{'id_parts'});
			}
		}elsif(!$error) {
			$va{'message'} = &trans_txt('unauth_action').'<br>';
		}
	}else{
		$in{'opt'} = $opt;

		my ($sth) = &Do_SQL("SELECT  Description1,  Description2,  Description3,  Description4 FROM cu_skus_descriptions WHERE ID_parts='$in{'id_parts'}';");
		while ($rec = $sth->fetchrow_hashref){
			$in{'description1'} = $rec->{'Description1'};
			$in{'description2'} = $rec->{'Description2'};
			$in{'description3'} = $rec->{'Description3'};
			$in{'description4'} = $rec->{'Description4'};
		}
	}

	if($in{'action'} && $saved == 0){
		$va{'message'} .= &trans_txt('invalid');
	}

	print &build_page("ajaxbuild:parts_opt".$opt.".html")
}

#############################################################################
#############################################################################
#   Function: mer_parts_tecs_specs
#
#       Es: Visualizacion de las Especificaciones Tecnicas de un SKU
#       En: View of the technical specifications of a SKU
#
#
#    Created on: 25/06/2014  12:20:10
#
#    Author: ISC Alejandro Diaz
#    Modifications:
#
#        -
#
#   Parameters:
#
#       -
#
#   See Also:
#
#
#
sub mer_parts_tecs_specs{
#############################################################################
	print "Content-type: text/html\n\n";

	if ($in{'id_parts'}) {
		my ($sth) = &Do_SQL("SELECT  Description1,  Description2,  Description3,  Description4 FROM cu_skus_descriptions WHERE ID_parts='$in{'id_parts'}';");
		while ($rec = $sth->fetchrow_hashref){
			$in{'description1'} = $rec->{'Description1'};
			$in{'description2'} = $rec->{'Description2'};
			$in{'description3'} = $rec->{'Description3'};
			$in{'description4'} = $rec->{'Description4'};
		}
	}

	print &build_page("ajaxbuild:parts_techs_specs.html")
}

#############################################################################
#############################################################################
#	Function: bills_print_generate
#
#	Created on: 12/09/2014  03:20:10
#
#	Author: Alejandro Diaz
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:IDs bills sequence for printing
#
#	See Also:
#
#
#
sub bills_print_generate {
#############################################################################
#############################################################################
	my $value;
	my $add_sql;
	
	$in{'id_vendors'} = int($in{'id_vendors'});
	$in{'id_bills_start'} = int($in{'id_bills_start'});
	$in{'id_bills_end'} = int($in{'id_bills_end'});

	$add_sql .= ($in{'id_vendors'})? " AND ID_vendors = '$in{'id_vendors'}'":"";
	$add_sql .= ($in{'id_bills_start'})? " AND ID_bills >= '$in{'id_bills_start'}'":"";
	$add_sql .= ($in{'id_bills_end'})? " AND ID_bills <= '$in{'id_bills_end'}'":"";
	$add_sql .= ($in{'duedate_from'})? " AND DueDate >= '$in{'duedate_from'}'":"";
	$add_sql .= ($in{'duedate_to'})? " AND DueDate <= '$in{'duedate_to'}'":"";

	if($in{'paydate_from'} and $in{'paydate_to'}){
		$add_inner .= '
		INNER JOIN sl_banks_movrel ON ( tablename=\'bills\' and sl_banks_movrel.tableid = sl_bills.ID_bills)
		INNER JOIN sl_banks_movements ON (sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements)';
		$add_sql .= ($in{'paydate_from'})? " AND sl_banks_movements.BankDate >= '$in{'paydate_from'}'":"";
		$add_sql .= ($in{'paydate_to'})? " AND sl_banks_movements.BankDate<= '$in{'paydate_to'}'":"";
		$add_sql .= "";
	}
	
	if ($in{'status'} =~ m/\|/){
		my @arr_status = split /\|/ , $in{'status'};
		for (0..$#arr_status) {
			$string_status .= "'".$arr_status[$_]."',";
		}
		chop $string_status;
		$add_sql .= " AND sl_bills.Status IN($string_status)";
	}else{
		$add_sql .= ($in{'status'})? " AND sl_bills.Status IN('$in{'status'}')":"";
	}

	my $str_ids = '';
	$sql = "SELECT ID_Bills FROM sl_bills $add_inner WHERE 1 $add_sql LIMIT 200;";
	my ($sth) = &Do_SQL($sql);
	while ($rec = $sth->fetchrow_hashref()){
		# generar cadena de ids
		$str_ids .= $rec->{'ID_Bills'}.',';
		# buscar id bills referenciados
	}
	chop ($str_ids);

	print "Content-type: text/html\n\n";
	# print $sql;
	print $str_ids;
}

1;
