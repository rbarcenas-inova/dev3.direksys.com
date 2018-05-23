#!/usr/bin/perl
##################################################################
#   REPORTS : FINANCE
##################################################################


sub rep_fin_avsn{
# --------------------------------------------------------
	##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
	##TODO: No pueden haber referecias a los tipos de "e" en codigo

	if($in{'action'}){
		my ($query_tot,$query_list);


		$query = " FROM  `sl_orders_plogs` INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_plogs.ID_orders WHERE LOCATE(  'Submited Info', Data ) =1 AND LOCATE(  'ccAuthReply_avsCode = N', Data, 100 ) >0 ";

		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders_plogs.Date >= '$in{'from_date'}' ";
		}

		$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders_plogs.Date <= '$in{'to_date'}' ";
		}

		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY sl_orders_plogs.Date $in{'sortorder'}, sl_orders.ID_orders";

		$report_name = "AVS N";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) $query ";
		$query_list = "SELECT sl_orders.ID_orders, ID_customers, sl_orders.Date,sl_orders_plogs.Date, sl_orders.Status, OrderNet $query $sb";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){

					my $fname   = 'sosl_cc_avsn-'.$in{'from_date'}.'-'.$in{'to_date'}.'.xls';

					($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
					($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					$fname =~	s/\///g;

					use Spreadsheet::WriteExcel;

					# Send the content type
					#print "Content-type: application/vnd.ms-excel\n\n";
					print "Content-type: application/octetstream\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();
					# Write some text.
					$worksheet->write(0, 0,'ID Order');
					$worksheet->write(0, 1,'Customer Name');
					$worksheet->write(0, 2,'Order Date');
					$worksheet->write(0, 3,'Order Status');
					$worksheet->write(0, 4,'Order Net');

				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;
			while (my ($id_orders,$id_customers,$odate,$pdate,$status,$ordernet) = $sth->fetchrow()){
				$d = 1 - $d;
				my $customer = &load_name('sl_customers','ID_customers',$id_customers,"CONCAT(FirstName,'', LastName1)");
				
				if($in{'export'}){

					# Write data
					$worksheet->write($row, 0,$id_orders);
					$worksheet->write($row, 1,$customer);
					$worksheet->write($row, 2,$odate);
					$worksheet->write($row, 3,$status);
					$worksheet->write($row, 4,$ordernet);
					#print "$id_orders,$date $time,$agent,\n";


				}else{

					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]' style="height:25px;">
										<td align="left" class="smalltext" nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders" title="View Order">$id_orders</a></td>
										<td align="left" class="smalltext" nowrap>$customer</td>
										<td align="center" class="smalltext">$odate</td>
										<td align="center" class="smalltext">$status</td>
										<td align="right" class="smalltext">|. &format_price($ordernet).qq|</td>
									</tr>\n|;
				}
				$row++;
			}

		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="5">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : $report_name</td>
								</tr>
								<tr>
							<td class="smalltext">Report Units</td>
							<td class="smalltext">Products / Sale Price</td>
							</tr>
						$va{'report_tbl'}
							<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
							</tr>
						</table></center>|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_fin_avsn_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_fin_avsn.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_fin_avsn.html');
	}
}



sub rep_fin_wreceipt{
# --------------------------------------------------------
# Forms Involved: administration/rep_fin_wreceipt
# Created on: 21 Sep 2011 15:18:19
# Author: Roberto Barcenas.
# Description : Genera Reporte de Finanzas: Muestra Registro de cuando se reciben Purchase Orders en nuestro Warehouse
# Parameters

	##TODO: Todos los textos deben estar fuera del codigo y/o a traves de transtxt
	##TODO: No pueden haber referecias a los tipos de "e" en codigo

	if($in{'action'}){
		my ($query_tot,$query_list);

		my $tablebase = $in{'tablebase'}eq'wr' ? 'sl_purchaseorders_wreceipts' : 'sl_purchaseorders_items';
		$query = " FROM  `sl_purchaseorders_wreceipts` INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_wreceipts.ID_purchaseorders_items = sl_purchaseorders_items.ID_purchaseorders_items WHERE 1 ";

		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND $tablebase.Date >= '$in{'from_date'}' ";
		}

		$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND $tablebase.Date <= '$in{'to_date'}' ";
		}

		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY $tablebase.Date $in{'sortorder'}, ID_purchaseorders";

		$report_name = "AVS N";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) $query ";
		$query_list = "SELECT ID_purchaseorders,sl_purchaseorders_items.ID_products,sl_purchaseorders_items.Date, sl_purchaseorders_items.Qty,`sl_purchaseorders_wreceipts`.Date, `sl_purchaseorders_wreceipts`.Quantity,sl_purchaseorders_items.Price   $query $sb";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet,$date_format,$price_format,$price_quantity_formula;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){

					my $fname   = 'sosl_report_wreceipt-'.$in{'from_date'}.'-'.$in{'to_date'}.'.xls';

					($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
					($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					$fname =~	s/\///g;

					use Spreadsheet::WriteExcel;

					# Send the content type
					#print "Content-type: application/vnd.ms-excel\n\n";
					print "Content-type: application/octetstream\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();
			
					# Write some text.
					$worksheet->write(0, 0,'ID Purchase Order');
					$worksheet->write(0, 1,'SKU ID');
					$worksheet->write(0, 2,'SKU Name');
					$worksheet->write(0, 3,'Date Ordered');
					$worksheet->write(0, 4,'Quantity Ordered');
					$worksheet->write(0, 5,'Date Received');
					$worksheet->write(0, 6,'Quantity Received');
					$worksheet->write(0, 7,'Unit Price');
					$worksheet->write(0, 8,'Total Received');

					## Formatting
					$date_format = $workbook->add_format(num_format => 'mm/dd/yy');
					$price_format = $workbook->add_format(align => 'right', num_format => '$0.00');

					## Stored Formulas
					$price_quantity_formula = $worksheet->store_formula('=G2*H2');

				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;
			while (my ($idpo,$idp,$date_o,$qty_o,$date_r,$qty_r,$price) = $sth->fetchrow()){
				$d = 1 - $d;
				my $customer = &load_name('sl_customers','ID_customers',$id_customers,"CONCAT(FirstName,'', LastName1)");
				my $pname = &load_name('sl_parts','ID_parts',substr($idp,5,4),"Name");

				if($in{'export'}){

					# Write data
					$worksheet->write_number($row,0,$idpo);
					$worksheet->write_number($row,1,substr($idp,5,4));
					$worksheet->write($row,2,$pname);
					$worksheet->write_date_time($row,3,$date_o,$date_format);
					$worksheet->write_number($row,4,$qty_o);
					$worksheet->write_date_time($row,5,$date_r,$date_format);
					$worksheet->write_number($row,6,$qty_r);
					$worksheet->write_number($row,7,$price,$price_format);
					$worksheet->repeat_formula($row,8,$price_quantity_formula,$price_format,qw/^G2$/, 'G' . ($row+1),qw/^H2$/, 'H' . ($row+1));
					#print "$id_orders,$date $time,$agent,\n";


				}else{

					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]' style="height:25px;">
										<td align="left" class="smalltext" nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$idpo" title="View Purchase Order">$idpo</a></td>
										<td align="left" class="smalltext" nowrap><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=|.substr($idp,5,4).qq|" title="View SKU">|.substr($idp,5,4).qq|</a></td>
										<td align="left" class="smalltext" nowrap>$pname</td>
										<td align="center" class="smalltext" nowrap>$date_o</td>
										<td align="right" class="smalltext" nowrap>$qty_o</td>
										<td align="center" class="smalltext">$date_r</td>
										<td align="right" class="smalltext" nowrap>$qty_r</td>
										<td align="right" class="smalltext" nowrap>|. &format_price($price).qq|</td>
										<td align="right" class="smalltext" nowrap>|. &format_price($qty_r * $price).qq|</td>
									</tr>\n|;
				}
				$row++;
			}

			if($in{'export'}){
				$worksheet->write_formula($row,4,'=SUM(E2:E'.$row.')');
				$worksheet->write_formula($row,6,'=SUM(G2:G'.$row.')');
				$worksheet->write_formula($row,8,'=SUM(I2:I'.$row.')',$price_format);
				exit;
			}


		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="5">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : $report_name</td>
								</tr>
								<tr>
							<td class="smalltext">Report Units</td>
							<td class="smalltext">Products / Sale Price</td>
							</tr>
						$va{'report_tbl'}
							<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
							</tr>
						</table></center>|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_fin_wreceipt_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_fin_wreceipt.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_fin_wreceipt.html');
	}
}

#############################################################################
#############################################################################
#   Function: rep_fin_collection
#
#       Es: Reporte de cobranza para Contabilidad
#       En: 
#
#
#    Created on: 11/07/2013
#
#    Author: AD
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_fin_collection{
#############################################################################
#############################################################################

	if($in{'action'}) {

		my $add_filters = '';

		$add_filters = " AND ID_banks='$in{'id_banks'}'" if ($in{'id_banks'});
		
		$add_filters .= " AND BankDate >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
		$add_filters .= " AND BankDate <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
		
		my ($sth) = &Do_SQL("SELECT COUNT(*)
			FROM sl_orders 
			INNER JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
			INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active'
			INNER JOIN sl_customers USING(ID_customers)
			INNER JOIN sl_banks_movrel ON tablename='orders_payments' AND tableid=sl_orders_payments.ID_orders_payments
			INNER JOIN sl_banks_movements USING(ID_banks_movements)
			INNER JOIN sl_banks USING(ID_banks)
			LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_orders_products.ID_orders_products
			LEFT JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.invoice_type='ingreso' AND cu_invoices.Status='Certified'
			LEFT JOIN cu_company_legalinfo ON PrimaryRecord='Yes'
			WHERE 1
			AND sl_banks_movements.type='Debits'
			AND sl_orders.Status NOT IN('Void','System Error')
			$add_filters
		;");
		
		my ($tot) = $sth->fetchrow();

		if ($tot){
			my $fname   = 'Report_Collection_'.$cfg{'app_title'}.'.csv';
			$fname =~ s/\s/_/g;
			
			my $strHeader = "UN,Fecha Contable de la aplicación,No de cuenta, Banco, No Cliente, Nombre del Cliente, Fecha de depósito, Importe del depósito, Fecha de Pedido, ID de Pedido, Estatus de Pedido, Fecha de Factura, No De Factura, %, Base, IVA, Total, Base Pago, IVA Pago, Total Pago";

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			my ($sth) = &Do_SQL("SELECT 
				cu_company_legalinfo.Name UN
				, sl_orders_payments.CapDate FCONTABLE
				, sl_banks.SubAccountOf CUENTA
				, sl_banks.Name BANCO
				, sl_customers.ID_customers IDCLIENTE
				, (IF(sl_customers.company_name IS NOT NULL,company_name,CONCAT(sl_customers.FirstName,' ',sl_customers.Lastname1)))CLIENTE
				, sl_banks_movements.BankDate FBANCO
				, if (sl_banks_movements.currency_exchange IS NOT NULL AND sl_banks_movements.currency_exchange>1,(sl_banks_movrel.AmountPaid*sl_banks_movements.currency_exchange),sl_banks_movrel.AmountPaid)IMPORTE
				, sl_orders.Date FORDER
				, sl_orders.ID_orders IDORDERS
				, sl_orders.Status
				, cu_invoices.doc_date FFACTURA
				, cu_invoices.ID_invoices IDFACTURA
				, CONCAT(cu_invoices.doc_serial,cu_invoices.doc_num) NOFACTURA
				, sl_orders_products.Tax_percent
				, SUM(sl_orders_products.SalePrice - sl_orders_products.Discount) As Price
				, SUM(sl_orders_products.Tax)AS Tax
				, SUM(sl_orders_products.SalePrice - sl_orders_products.Discount + sl_orders_products.Tax)Base
				, (
					SELECT SUM(SalePrice - Discount + Tax)
					FROM sl_orders_products
					WHERE ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active'
				)TotalOrder
				FROM sl_orders 
				INNER JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
				INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active'
				INNER JOIN sl_customers USING(ID_customers)
				INNER JOIN sl_banks_movrel ON tablename='orders_payments' AND tableid=sl_orders_payments.ID_orders_payments
				INNER JOIN sl_banks_movements USING(ID_banks_movements)
				INNER JOIN sl_banks USING(ID_banks)
				LEFT JOIN cu_invoices_lines ON cu_invoices_lines.ID_orders_products=sl_orders_products.ID_orders_products
				LEFT JOIN cu_invoices ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices AND cu_invoices.invoice_type='ingreso' AND cu_invoices.Status='Certified'
				LEFT JOIN cu_company_legalinfo ON PrimaryRecord='Yes'
				WHERE 1
				AND sl_banks_movements.type='Debits'
				AND sl_orders.Status NOT IN('Void','System Error')
				$add_filters
				GROUP BY sl_orders_payments.ID_orders_payments, sl_orders_products.Tax_percent
				ORDER BY sl_banks_movements.BankDate DESC, sl_orders_payments.ID_orders_payments, sl_orders_products.Tax_percent
				;");
													
			my $records = 0;
			while ($rec = $sth->fetchrow_hashref()) {			
				my $strout;

				$strout .= qq|"$rec->{'UN'}"|;
				$strout .= qq|,$rec->{'FCONTABLE'}|;
				$strout .= qq|,$rec->{'CUENTA'}|;
				$strout .= qq|,"$rec->{'BANCO'}"|;
				$strout .= qq|,$rec->{'IDCLIENTE'}|;
				$strout .= qq|,"$rec->{'CLIENTE'}"|;
				$strout .= qq|,$rec->{'FBANCO'}|;
				$strout .= qq|,$rec->{'IMPORTE'}|;
				$strout .= qq|,$rec->{'FORDER'}|;
				$strout .= qq|,$rec->{'IDORDERS'}|;
				$strout .= qq|,$rec->{'Status'}|;
				$strout .= qq|,$rec->{'FFACTURA'}|;
				# $strout .= qq|,$rec->{'IDFACTURA'}|;
				$strout .= qq|,$rec->{'NOFACTURA'}|;
				$strout .= qq|,$rec->{'Tax_percent'}|;
				$strout .= qq|,$rec->{'Price'}|;
				$strout .= qq|,$rec->{'Tax'}|;
				$strout .= qq|,$rec->{'Base'}|;

				# $strout .= qq|,$rec->{'TotalOrder'}|;

				##  en base al total de la orden se calcula con regla de 3
				$total = $rec->{'TotalOrder'};

				$imp_base = ($total==0)? 0:($rec->{'IMPORTE'} * $rec->{'Price'}) / $total;
				$imp_tax = ($total==0)? 0:($rec->{'IMPORTE'} * $rec->{'Tax'}) / $total;
				$imp_total = $imp_base + $imp_tax;

				$strout .= qq|,$imp_base|;
				$strout .= qq|,$imp_tax|;
				$strout .= qq|,$imp_total\r\n|;


				print $strout;

			}

			&auth_logging('report_view','');
			return;
			
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_fin_collection.html');
}

#############################################################################
#############################################################################
#   Function: rep_fin_payments
#
#       Es: Reporte de Pagos a Proveedores para Contabilidad
#       En: 
#
#
#    Created on: 12/07/2013
#
#    Author: AD
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_fin_payments{
#############################################################################
#############################################################################

	if($in{'action'}) {
		$in{'export'}=1;
		my $add_filters = '';

		$add_filters = " AND ID_banks='$in{'id_banks'}'" if ($in{'id_banks'});
		
		$add_filters .= " AND BankDate >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
		$add_filters .= " AND BankDate <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
		
		my ($sth) = &Do_SQL("SELECT COUNT(*)
			FROM sl_bills 
			INNER JOIN sl_vendors using(ID_vendors)
			INNER JOIN sl_banks_movrel ON tablename='bills' AND tableid=sl_bills.ID_bills
			INNER JOIN sl_banks_movements USING(ID_banks_movements)
			INNER JOIN sl_banks USING(ID_banks)
			INNER JOIN sl_movements ON tableused='sl_bills' AND ID_tableused=sl_bills.ID_bills AND sl_movements.Credebit='Debit'
			INNER JOIN sl_accounts ON sl_movements.ID_accounts=sl_accounts.ID_accounts
			LEFT JOIN cu_company_legalinfo on PrimaryRecord='Yes'
			WHERE 1
			AND sl_banks_movements.type='Credits'
			AND sl_bills.Status NOT IN('Void')
			AND sl_movements.Status = 'Active'
			$add_filters
		;");
		
		my ($tot) = $sth->fetchrow();

		if ($tot){
			my $fname   = 'Report_Payments_'.$cfg{'app_title'}.'.csv';
			$fname =~ s/\s/_/g;
			
			my $strHeader = "UN, Fecha, Metodo de Pago, Banco, Cuenta, Referencia Bancaria, ID Proveedor, Proveedor, Moneda Base, Moneda en Comprobante, Importe Pagado, Tipo de Cambio, ID Comprobante, Fecha Comprobante, Descripcion, No Cuenta Contable, Cuenta Contable, Subtotal Factura, Total Factura, Proporcion Pago";# IVA Factura,

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			
			my ($sth) = &Do_SQL("SELECT
				sl_banks_movements.doc_type
				, sl_banks.Name Bank
				, sl_banks_movements.BankDate
				, sl_banks.SubAccountOf
				, if ((length(RefNumCustom)=0 or RefNumCustom is null ),RefNum,RefNumCustom)RefNum
				, sl_vendors.ID_vendors
				, sl_vendors.CompanyName
				, if (sl_banks_movements.currency_exchange IS NOT NULL AND sl_banks_movements.currency_exchange>1,(sl_banks_movrel.AmountPaid*sl_banks_movements.currency_exchange),sl_banks_movrel.AmountPaid)AmountPaid
				, sl_bills.Currency
				, sl_banks_movements.Amount
				, if (sl_banks_movements.currency_exchange IS NOT NULL AND sl_banks_movements.currency_exchange>1,sl_banks_movements.currency_exchange,'')currency_exchange
				, sl_bills.ID_bills
				, sl_bills.BillDate
				, sl_bills.Memo
				, sl_bills.Status
				, sl_bills.Type
				, sl_bills.Amount AmountBill
				, sl_accounts.ID_accounting
				, sl_accounts.Name AccountsName
				, sl_movements.Amount AmountMovs
				, cu_company_legalinfo.Name UN
				FROM sl_bills 
				INNER JOIN sl_vendors using(ID_vendors)
				INNER JOIN sl_banks_movrel ON tablename='bills' AND tableid=sl_bills.ID_bills
				INNER JOIN sl_banks_movements USING(ID_banks_movements)
				INNER JOIN sl_banks USING(ID_banks)
				INNER JOIN sl_movements ON tableused='sl_bills' AND ID_tableused=sl_bills.ID_bills AND sl_movements.Credebit='Debit'
				INNER JOIN sl_accounts ON sl_movements.ID_accounts=sl_accounts.ID_accounts
				LEFT JOIN cu_company_legalinfo on PrimaryRecord='Yes'
				WHERE 1
				AND sl_banks_movements.type='Credits'
				AND sl_bills.Status NOT IN('Void')
				AND sl_movements.Status = 'Active'
				$add_filters
				ORDER BY sl_banks_movements.BankDate DESC, sl_bills.ID_bills, sl_accounts.ID_accounts
			;");
													
			my $records = 0;
			while ($rec = $sth->fetchrow_hashref()) {			
				my $strout;
				my $accounting_date;
				if (&bills_expenses_detection($rec->{'ID_bills'})) {
					# Fecha contable para bills expenses
					my ($sth2) = &Do_SQL("SELECT LogDate FROM admin_logs WHERE 1 AND tbl_name='sl_bills' AND (Message = 'mer_bills_toprocessed' OR Message = 'bills_processed') AND Action='$rec->{'ID_bills'}' ORDER BY LogDate DESC LIMIT 1;");
					$accounting_date = $sth2->fetchrow_array();

					$accounting_date = $rec->{'BillDate'} if($accounting_date eq '');
				}elsif (&bills_pos_detection($rec->{'ID_bills'})) {
					# Fecha contable para bills pos
					my ($sth2) = &Do_SQL("SELECT sl_wreceipts.Date FROM sl_wreceipts LEFT JOIN sl_bills_pos USING(ID_purchaseorders) WHERE 1 AND ID_bills = '$rec->{'ID_bills'}' AND sl_wreceipts.Status='Processed' ORDER BY sl_wreceipts.Date LIMIT 1;");
					$accounting_date = $sth2->fetchrow_array();

				}elsif ($rec->{'Type'} eq 'Deposit'){
					# Fecha contable para bills deposit
					$accounting_date = $rec->{'BankDate'};
				}
				
				$strout .= qq|"$rec->{'UN'}"|;
				$strout .= qq|,$accounting_date|;
				$strout .= qq|,"$rec->{'doc_type'}"|;
				$strout .= qq|,"$rec->{'Bank'}"|;
				$strout .= qq|,$rec->{'SubAccountOf'}|;
				$strout .= qq|,"$rec->{'RefNum'}"|;
				$strout .= qq|,$rec->{'ID_vendors'}|;
				$strout .= qq|,"$rec->{'CompanyName'}"|;
				$strout .= qq|,"|.&format_price($rec->{'AmountPaid'}).qq|"|;
				$strout .= qq|,$rec->{'Currency'}|;
				$strout .= qq|,"|.&format_price($rec->{'Amount'}).qq|"|;
				$strout .= qq|,$rec->{'currency_exchange'}|;
				$strout .= qq|,$rec->{'ID_bills'}|;
				$strout .= qq|,$rec->{'BillDate'}|;
				$strout .= qq|,"$rec->{'Memo'}"|;
				$strout .= qq|,$rec->{'ID_accounting'}|;
				$strout .= qq|,"$rec->{'AccountsName'}"|;

				##  en base al total del comprobante se calcula con regla de 3
				$total = $rec->{'AmountBill'};

				$imp = ($total==0)? 0:($rec->{'AmountPaid'} * $rec->{'AmountMovs'}) / $total;

				$strout .= qq|,"|.&format_price($rec->{'AmountMovs'}).qq|"|;
				$strout .= qq|,"|.&format_price($rec->{'AmountBill'}).qq|"|;
				$strout .= qq|,"|.&format_price($imp).qq|"\r\n|;

				print $strout;
			}

			&auth_logging('report_view','');
			return;
			
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_fin_payments.html');
}

#############################################################################
#############################################################################
#   Function: rep_fin_chargestdc
#
#       Es: Reporte de Cobros TDC
#       En: 
#
#    Created on: 12/07/2013
#
#    Author: GQ
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#  Returns:
#
#   See Also:
#
#
sub rep_fin_chargestdc{

	if($in{'action'}){
		my ($query_tot,$query_list);


		$query = " FROM  sl_orders 
						INNER JOIN sl_customers USING(ID_customers) 
						INNER JOIN sl_orders_payments USING(ID_orders) 
						LEFT JOIN sl_orders_cardsdata ON sl_orders_payments.ID_orders_payments=sl_orders_cardsdata.ID_orders_payments";

		$query .= " WHERE 1 
						AND sl_orders_payments.`Type`='Credit-Card' 
						AND sl_orders_payments.Status NOT IN ('Financed','Credit','ChargeBack','Void','Claim','Order Cancelled','Cancelled') ";
		####################################################
		# Filtros
		####################################################
		## ID Orden
		if( $in{'equal_id_order'} ){
			$query .= " AND sl_orders.ID_orders = '$in{'equal_id_order'}' ";	
		}else{
			if( $in{'from_id_order'} ){
				$query .= " AND sl_orders.ID_orders >= '$in{'from_id_order'}' ";
			}
			if( $in{'to_id_order'} ){
				$query .= " AND sl_orders.ID_orders <= '$in{'to_id_order'}' ";
			}
		}
		## ID Pago
		if( $in{'equal_id_payment'} ){
			$query .= " AND sl_orders_payments.ID_orders_payments = '$in{'from_id_payment'}' ";	
		}else{
			if( $in{'from_id_payment'} ){
				$query .= " AND sl_orders_payments.ID_orders_payments >= '$in{'from_id_payment'}' ";
			}
			if( $in{'to_id_payment'} ){
				$query .= " AND sl_orders_payments.ID_orders_payments <= '$in{'to_id_payment'}' ";
			}
		}
		## Tipo Pago
		# if( $in{'equal_paytype'} ){
		# 	$query .= " AND sl_orders_payments.Type = '$in{'equal_paytype'}' ";	
		# }
		## Estatus Orden
		if( $in{'equal_status'} ){
			$query .= " AND sl_orders.Status = '$in{'equal_status'}' ";	
		}
		## Cod. Autorizacion
		if( $in{'equal_auth_code'} ){
			$query .= " AND sl_orders_payments.AuthCode = '$in{'equal_auth_code'}' ";	
		}
		## Captura
		if( $in{'equal_captured'} ){
			$query .= " AND sl_orders_payments.Captured = '$in{'equal_captured'}' ";	
		}
		## Fecha
		if( $in{'equal_date'} ){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Equal Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date = '$in{'equal_date'}' ";	
		}else{
			if ($in{'from_date'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
				$query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}
			#$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
			if ($in{'to_date'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
				$query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}
		## Meses a pagar
		if( $in{'month_topay'} ){
			$query .= " AND sl_orders_payments.PmtField8 = '$in{'month_topay'}' ";	
		}
		## ID Cliente
		if( $in{'equal_id_customer'} ){
			$query .= " AND sl_customers.ID_customers = '$in{'equal_id_customer'}' ";	
		}else{
			if( $in{'from_id_customer'} ){
				$query .= " AND sl_customers.ID_customers >= '$in{'from_id_customer'}' ";
			}
			if( $in{'to_id_customer'} ){
				$query .= " AND sl_customers.ID_customers <= '$in{'to_id_customer'}' ";
			}
		}
		## Nombre Cliente  
		if( $in{'equal_name_customer'} ){
			$query .= " AND xCustomerName = '$in{'equal_name_customer'}' ";	
		}
		## Calle y Número
		if( $in{'equal_address'} ){
			$query .= " AND sl_orders.shp_Address1 = '$in{'equal_address'}' ";	
		}
		## Colonia
		if( $in{'equal_urbanization'} ){
			$query .= " AND sl_orders.shp_Urbanization = '$in{'equal_urbanization'}' ";	
		}
		## Delegacion/Municipio
		if( $in{'equal_city'} ){
			$query .= " AND sl_orders.shp_City = '$in{'equal_city'}' ";	
		}
		## Estado
		if( $in{'equal_state'} ){
			$query .= " AND sl_orders.shp_State = '$in{'equal_state'}' ";	
		}
		## CP
		if( $in{'equal_zipcode'} ){
			$query .= " AND sl_orders.shp_Zip = '$in{'equal_zipcode'}' ";	
		}
		## ID Usuario
		if( $in{'equal_id_user'} ){
			$query .= " AND sl_orders.shp_City = '$in{'equal_city'}' ";	
		}else{
			if( $in{'from_id_user'} ){
				$query .= " AND sl_customers.ID_customers >= '$in{'from_id_user'}' ";
			}
			if( $in{'to_id_user'} ){
				$query .= " AND sl_customers.ID_customers <= '$in{'to_id_user'}' ";
			}
		}
		## Forma de Pago
		if( $in{'equal_ptype'} ){
			$query .= " AND sl_orders.Ptype = '$in{'equal_ptype'}' ";	
		}
		## Teléfono
		if( $in{'equal_phone'} ){
			$query .= " AND sl_customers.Phone1 = '$in{'equal_phone'}' ";	
		}
		####################################################

		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY sl_orders.ID_orders DESC";

		$report_name = "Charges TDC";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) $query ";
		$query_list = "SELECT 
							`sl_orders`.`ID_orders`, 
							((SELECT channel FROM sl_salesorigins WHERE sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins LIMIT 1)) xChannel,
							`sl_orders_payments`.`ID_orders_payments`, 
							`sl_orders_payments`.`Type`, 
							`sl_orders_payments`.`Amount`, 
							`sl_orders_payments`.`PmtField3`, 
							`sl_orders_payments`.`PmtField4`, 
							`sl_orders`.`Status`, 
							`sl_orders_cardsdata`.`card_date`, 
							`sl_orders_payments`.`AuthCode`, 
							`sl_orders_payments`.`Captured`, 
							`sl_orders`.`Date`, 
							(if(sl_orders.Ptype<>'COD',sl_orders_payments.CapDate,'')) xCapDate,
							((SELECT GROUP_CONCAT(DISTINCT ShpDate) FROM sl_orders_products WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND ShpDate > '1900-01-01' GROUP BY ID_orders)) xShpDate, 
							`sl_orders_payments`.`PmtField8`, 
							`sl_customers`.`ID_customers`, 
							(CONCAT(sl_customers.FirstName,' ',sl_customers.LastName1,' ', sl_customers.LastName2)) xCustomerName, 
							`sl_orders`.`shp_Address1`, 
							`sl_orders`.`shp_Urbanization`, 
							`sl_orders`.`shp_City`, 
							`sl_orders`.`shp_State`, 
							`sl_orders`.`shp_Zip`, 
							(CASE WHEN sl_orders.shp_type = 1 THEN 'Standard Delivery' WHEN sl_orders.shp_type = 2 THEN 'Express Delivery' WHEN sl_orders.shp_type = 3 THEN 'COD' ELSE '' END) xTypePay, 
							`sl_orders`.`ID_admin_users`, 
							((SELECT CONCAT(UPPER(admin_users.FirstName),' ',UPPER(admin_users.MiddleName),' ',UPPER(admin_users.LastName)) FROM admin_users WHERE admin_users.ID_admin_users=sl_orders.ID_admin_users)) xUserName, 
							`sl_orders`.`Ptype`, 
							`sl_customers`.`Phone1` 
						$query 
						$sb";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){

					my $date_name;
					if( $in{'from_date'} or $in{'to_date'}){
						$date_name = '-'.$in{'from_date'}.'-'.$in{'to_date'};
					}

					my $fname   = 'charges_tdc'.$date_name.'.csv';


					($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
					($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					$fname =~	s/\///g;

					use Spreadsheet::WriteExcel;

					# Send the content type
					#print "Content-type: application/vnd.ms-excel\n\n";
					print "Content-type: text/csv\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();
					# Write some text.
					$worksheet->write(0, 0,'ID Orden');
					$worksheet->write(0, 1,'Canal de Venta');
					$worksheet->write(0, 2,'ID Pago');
					$worksheet->write(0, 3,'Tipo de Pago');
					$worksheet->write(0, 4,'Monto');
					$worksheet->write(0, 5,'No. de Tarjeta');
					$worksheet->write(0, 6,'Estatus Orden');
					$worksheet->write(0, 7,'Fecha de Vencimiento');
					$worksheet->write(0, 8,'Cod. Autorizacion');
					$worksheet->write(0, 9,'Captura');
					$worksheet->write(0, 10,'Fecha Orden');
					$worksheet->write(0, 11,'Fecha Captura');
					$worksheet->write(0, 12,'Fecha Envio');
					$worksheet->write(0, 13,'Meses a Pagar');
					$worksheet->write(0, 14,'ID Cliente');
					$worksheet->write(0, 15,'Cliente');
					$worksheet->write(0, 16,'Calle y Numero');
					$worksheet->write(0, 17,'Colonia');
					$worksheet->write(0, 18,'Delegacion/Municipio');
					$worksheet->write(0, 19,'Estado');
					$worksheet->write(0, 20,'CP');
					$worksheet->write(0, 21,'Tipo de Envio');
					$worksheet->write(0, 22,'ID Usuario');
					$worksheet->write(0, 23,'Usuario');
					$worksheet->write(0, 24,'Forma de Pago');
					$worksheet->write(0, 25,'Telefono');
				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}

			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;
			while ($data = $sth->fetchrow_hashref()){
				$d = 1 - $d;
				my $num_tarj = "";
				my $date_tarj = "";
				if( $data->{'Type'} eq "Credit-Card" ){
					my $num_tarj_dcpt = $data->{'PmtField3'};
					my $date_tarj_dcpt = $data->{'PmtField4'};

					$num_tarj = $num_tarj_dcpt;
					$date_tarj = $date_tarj_dcpt;
				}

				# Se ocultan datos temporalmente
				$data->{'shp_Address1'} = &temp_hide_data($data->{'shp_Address1'});
				$data->{'shp_Urbanization'} = &temp_hide_data($data->{'shp_Urbanization'});
				$data->{'shp_City'} = &temp_hide_data($data->{'shp_City'});
				$data->{'shp_State'} = &temp_hide_data($data->{'shp_State'});
				$data->{'shp_Zip'} = &temp_hide_data($data->{'shp_Zip'});
				$data->{'Phone1'} = &temp_hide_data($data->{'Phone1'},'phone');

				if($in{'export'}){

					# Write data
					$worksheet->write($row, 0, $data->{'ID_orders'});
					$worksheet->write($row, 1, $data->{'xChannel'});
					$worksheet->write($row, 2, $data->{'ID_orders_payments'});
					$worksheet->write($row, 3, $data->{'Type'});
					$worksheet->write($row, 4, $data->{'Amount'});					
					$worksheet->write($row, 5, $num_tarj);
					$worksheet->write($row, 6, $data->{'Status'});
					$worksheet->write($row, 7, $date_tarj);
					$worksheet->write($row, 8, $data->{'AuthCode'});
					$worksheet->write($row, 9, $data->{'Captured'});
					$worksheet->write($row, 10, $data->{'Date'});
					$worksheet->write($row, 11, $data->{'xCapDate'});
					$worksheet->write($row, 12, $data->{'xShpDate'});
					$worksheet->write($row, 13, $data->{'PmtField8'});
					$worksheet->write($row, 14, $data->{'ID_customers'});
					$worksheet->write($row, 15, $data->{'xCustomerName'});
					$worksheet->write($row, 16, $data->{'shp_Address1'});
					$worksheet->write($row, 17, $data->{'shp_Urbanization'});
					$worksheet->write($row, 18, $data->{'shp_City'});
					$worksheet->write($row, 19, $data->{'shp_State'});
					$worksheet->write($row, 20, $data->{'shp_Zip'});
					$worksheet->write($row, 21, $data->{'xTypePay'});
					$worksheet->write($row, 22, $data->{'ID_admin_users'});
					$worksheet->write($row, 23, $data->{'xUserName'});
					$worksheet->write($row, 24, $data->{'Ptype'});
					$worksheet->write($row, 25, $data->{'Phone1'});

				}else{

					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]' style="height:25px;">
										<td class="smalltext">$data->{'ID_orders'}</td>
										<td class="smalltext">$data->{'xChannel'}</td>
										<td class="smalltext">$data->{'ID_orders_payments'}</td>
										<td class="smalltext">$data->{'Type'}</td>
										<td class="smalltext">$data->{'Amount'}</td>
										<td class="smalltext">$num_tarj</td>
										<td class="smalltext">$data->{'Status'}</td>
										<td class="smalltext">$date_tarj</td>
										<td class="smalltext">$data->{'AuthCode'}</td>
										<td class="smalltext">$data->{'Captured'}</td>
										<td class="smalltext">$data->{'Date'}</td>
										<td class="smalltext">$data->{'xCapDate'}</td>
										<td class="smalltext">$data->{'xShpDate'}</td>
										<td class="smalltext">$data->{'PmtField8'}</td>
										<td class="smalltext">$data->{'ID_customers'}</td>
										<td class="smalltext">$data->{'xCustomerName'}</td>
										<td class="smalltext">$data->{'shp_Address1'}</td>
										<td class="smalltext">$data->{'shp_Urbanization'}</td>
										<td class="smalltext">$data->{'shp_City'}</td>
										<td class="smalltext">$data->{'shp_State'}</td>
										<td class="smalltext">$data->{'shp_Zip'}</td>
										<td class="smalltext">$data->{'xTypePay'}</td>
										<td class="smalltext">$data->{'ID_admin_users'}</td>
										<td class="smalltext">$data->{'xUserName'}</td>
										<td class="smalltext">$data->{'Ptype'}</td>
										<td class="smalltext">$data->{'Phone1'}</td>
									</tr>\n|;
				}
				$row++;
			}

		}else{
			
			$va{'message'} = &trans_txt('rep_orders_empty_result');
			print "Content-type: text/html\n\n";
			print &build_page('rep_fin_chargestdc.html');		
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : $report_name</td>
								</tr>
								<tr>									
									<td class="menu_bar_title">ID Orden</td>
									<td class="menu_bar_title">Canal de Venta</td>
									<td class="menu_bar_title">ID Pago</td>
									<td class="menu_bar_title">Tipo de Pago</td>
									<td class="menu_bar_title">Monto</td>
									<td class="menu_bar_title">No. de Tarjeta</td>
									<td class="menu_bar_title">Estatus Orden</td>
									<td class="menu_bar_title">Fecha de Vencimiento</td>
									<td class="menu_bar_title">Cod. Autorizacion</td>
									<td class="menu_bar_title">Captura</td>
									<td class="menu_bar_title">Fecha Orden</td>
									<td class="menu_bar_title">Fecha Captura</td>
									<td class="menu_bar_title">Fecha Envio</td>
									<td class="menu_bar_title">Meses a Pagar</td>
									<td class="menu_bar_title">ID Cliente</td>
									<td class="menu_bar_title">Cliente</td>
									<td class="menu_bar_title">Calle Y Numero</td>
									<td class="menu_bar_title">Colonia</td>
									<td class="menu_bar_title">Delegacion/Municipio</td>
									<td class="menu_bar_title">Estado</td>
									<td class="menu_bar_title">CP</td>
									<td class="menu_bar_title">Tipo de Envio</td>
									<td class="menu_bar_title">ID Usuario</td>
									<td class="menu_bar_title">Usuario</td>
									<td class="menu_bar_title">Forma de Pago</td>
									<td class="menu_bar_title">Telefono</td>
								</tr>
								$va{'report_tbl'}
								<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
								</tr>
							</table>
						</center>|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_fin_chargestdc_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_fin_chargestdc.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_fin_chargestdc.html');
	}
}

#############################################################################
#############################################################################
#   Function: rep_fin_cardfees
#
#       Es: Reporte de Cobros con tarjeta
#       En: 
#
#    Created on: 12/07/2013
#
#    Author: GQ
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#  Returns:
#
#   See Also:
#
#
sub rep_fin_cardfees{
	
	if($in{'action'}){
		my ($query_tot,$query_list);


		$query = " FROM sl_orders 
						INNER JOIN sl_orders_payments ON sl_orders_payments.ID_orders=sl_orders.ID_orders 
						LEFT JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins";

		$query .= " WHERE 1 
						AND sl_orders_payments.Type='Credit-Card' ";
		####################################################
		# Filtros
		####################################################
		## ID Orden
		if( $in{'equal_id_order'} ){
			$query .= " AND sl_orders.ID_orders = '$in{'equal_id_order'}' ";	
		}else{
			if( $in{'from_id_order'} ){
				$query .= " AND sl_orders.ID_orders >= '$in{'from_id_order'}' ";
			}
			if( $in{'to_id_order'} ){
				$query .= " AND sl_orders.ID_orders <= '$in{'to_id_order'}' ";
			}
		}		
		## Fecha pedido
		if( $in{'equal_date_order'} ){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Equal Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date = '$in{'equal_date_order'}' ";	
		}else{
			if ($in{'from_date_order'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
				$query .= " AND sl_orders.Date >= '$in{'from_date_order'}' ";
			}
			#$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
			if ($in{'to_date_order'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
				$query .= " AND sl_orders.Date <= '$in{'to_date_order'}' ";
			}
		}		
		## Forma de Pago
		if( $in{'equal_ptype'} ){
			$query .= " AND sl_orders.Ptype = '$in{'equal_ptype'}' ";	
		}
		## Estatus de Pedido
		if( $in{'equal_status'} ){
			$query .= " AND sl_orders.Status = '$in{'equal_status'}' ";	
		}
		## Fecha de Captura
		if( $in{'equal_date_cap'} ){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Equal Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders.Date = '$in{'equal_date_cap'}' ";	
		}else{
			if ($in{'from_date_cap'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
				$query .= " AND sl_caps.Date >= '$in{'from_date_cap'}' ";
			}
			#$in{'to_date'}	= &get_sql_date()	if !$in{'to_date'};
			if ($in{'to_date_cap'}){
				$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
				$query .= " AND sl_caps.Date <= '$in{'to_date_cap'}' ";
			}
		}
		####################################################

		$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY sl_orders.ID_orders DESC";

		$report_name = "Card Fees";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) $query ";
		$query_list = "SELECT 
							`sl_orders`.`ID_orders`, 
							`sl_orders`.`Date`, 
							`sl_salesorigins`.`Channel`, 
							`sl_orders`.`Ptype`, 
							`sl_orders_payments`.`Amount`, 
							`sl_orders_payments`.`AuthCode`, 
							`sl_orders_payments`.`PmtField3`, 
							`sl_orders`.`Status`, 
							`sl_orders_payments`.`PmtField8`, 							
							((SELECT COUNT(*) AS 'Intentos' FROM sl_orders_plogs WHERE sl_orders_plogs.ID_orders_payments=sl_orders_payments.ID_orders_payments GROUP BY sl_orders_plogs.ID_orders_payments)) xIntentos,  
							`sl_orders_payments`.`CapDate` 
						$query 
						$sb";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){

					my $fname   = 'cardfees-'.$in{'from_date'}.'-'.$in{'to_date'}.'.xls';

					($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
					($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					$fname =~	s/\///g;

					use Spreadsheet::WriteExcel;

					# Send the content type
					#print "Content-type: application/vnd.ms-excel\n\n";
					print "Content-type: application/octetstream\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();
					# Write some text.
					$worksheet->write(0, 0,'ID Orden');
					$worksheet->write(0, 1,'Fecha del Pedido');
					$worksheet->write(0, 2,'Canal de Venta');
					$worksheet->write(0, 3,'Forma de Pago');
					$worksheet->write(0, 4,'Monto');
					$worksheet->write(0, 5,'Cod. Autorizacion');
					$worksheet->write(0, 6,'No. de Tarjeta');
					$worksheet->write(0, 7,'Estatus del Pedido');
					$worksheet->write(0, 8,'Meses a Pagar');
					$worksheet->write(0, 9,'Tipo de Tarjeta');
					$worksheet->write(0, 10,'No. de Intentos');
					$worksheet->write(0, 11,'Banco');
					$worksheet->write(0, 12,'Fecha de Captura');
				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}

			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;
			while ($data = $sth->fetchrow_hashref()){
				$d = 1 - $d;
				my $num_tarj = "";
				my $bank = "";
				my $card_type = "";
				if( $data->{'Ptype'} eq "Credit-Card" ){					
					my $num_tarj_dcpt = &LeoDecrypt($data->{'PmtField3'});
					if ( !&check_permissions('view_info_tdc','','') ){
						$num_tarj = "xxxx-xxxx-xxxx-". substr($num_tarj_dcpt, -4);
					}else{
						$num_tarj = substr($num_tarj_dcpt, 0, 4)."-".substr($num_tarj_dcpt, 4, 2)."xx-xxxx-". substr($num_tarj_dcpt, -4);
					}

					##-- Se obtiene el nombre del banco y el tipo de tarjeta
					my $cod = substr($num_tarj_dcpt, 0, 6);
					my $sthPx = &Do_SQL("SELECT Bank, Type 
										FROM cu_cardprefix 
										WHERE Prefix=$cod;");
					($bank, $card_type) = $sthPx->fetchrow_array();
				}

				if($in{'export'}){
					# Write data
					$worksheet->write($row, 0, $data->{'ID_orders'});
					$worksheet->write($row, 1, $data->{'Date'});
					$worksheet->write($row, 2, $data->{'Channel'});
					$worksheet->write($row, 3, $data->{'Ptype'});
					$worksheet->write($row, 4, $data->{'Amount'});					
					$worksheet->write($row, 5, $data->{'AuthCode'});
					$worksheet->write($row, 6, $num_tarj);
					$worksheet->write($row, 7, $data->{'Status'});
					$worksheet->write($row, 8, $data->{'PmtField8'});
					$worksheet->write($row, 9, $card_type);
					$worksheet->write($row, 10, $data->{'xIntentos'});
					$worksheet->write($row, 11, $bank);
					$worksheet->write($row, 12, $data->{'CapDate'});
				}else{
					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]' style="height:25px;">
										<td class="smalltext">$data->{'ID_orders'}</td>
										<td class="smalltext">$data->{'Date'}</td>
										<td class="smalltext">$data->{'Channel'}</td>
										<td class="smalltext">$data->{'Ptype'}</td>
										<td class="smalltext">$data->{'Amount'}</td>
										<td class="smalltext">$data->{'AuthCode'}</td>
										<td class="smalltext">$num_tarj</td>
										<td class="smalltext">$data->{'Status'}</td>
										<td class="smalltext">$data->{'PmtField8'}</td>										
										<td class="smalltext">$card_type</td>
										<td class="smalltext">$data->{'xIntentos'}</td>
										<td class="smalltext">$bank</td>
										<td class="smalltext">$data->{'CapDate'}</td>
									</tr>\n|;
									#$data->{'PmtField3'}
				}
				$row++;
			}

		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|<tr><td align="center" colspan="5">|.&trans_txt('search_nomatches').qq|</td></tr>|;
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : $report_name</td>
								</tr>
								<tr>									
									<td class="menu_bar_title">ID Orden</td>
									<td class="menu_bar_title">Fecha del Pedido</td>
									<td class="menu_bar_title">Canal de Venta</td>
									<td class="menu_bar_title">Forma de Pago</td>
									<td class="menu_bar_title">Monto</td>
									<td class="menu_bar_title">Cod. Autorizacion</td>
									<td class="menu_bar_title">No. de Tarjeta</td>
									<td class="menu_bar_title">Estatus del Pedido</td>
									<td class="menu_bar_title">Meses a Pagar</td>
									<td class="menu_bar_title">Tipo de Tarjeta</td>
									<td class="menu_bar_title">No. de Intentos</td>
									<td class="menu_bar_title">Banco</td>
									<td class="menu_bar_title">Fecha de Captura</td>
								</tr>
								$va{'report_tbl'}
								<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
								</tr>
							</table>
						</center>|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_fin_cardfees_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_fin_cardfees.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_fin_cardfees.html');
	}
}

#############################################################################
#############################################################################
#   Function: rep_fin_kardex
#
#       Es: Reporte de Kardex de Inventario
#       En: Kardex report
#
#
#    Created on: 21/05/2015
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_fin_kardex {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'sales_journal_v1 '.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my ($add_sql, $add_sql_cm);

		$add_sql .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql .= ($in{'id_orders'})? " AND sl_orders.ID_orders = '$in{'id_orders'}' ":"";
		
		$add_sql_cm .= ($in{'doc_serial'})? " AND cu_invoices.doc_serial = TRIM('$in{'doc_serial'}') ":"";
		$add_sql_cm .= ($in{'doc_num'})? " AND cu_invoices.doc_num = TRIM('$in{'doc_num'}') ":"";
		$add_sql_cm .= ($in{'id_invoices'})? " AND cu_invoices.ID_invoices = TRIM('$in{'id_invoices'}') ":"";
		$add_sql_cm .= ($in{'id_creditmemos'})? " AND sl_creditmemos.ID_creditmemos = '$in{'id_creditmemos'}' ":"";

		$add_sql .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		$add_sql_cm .= ($in{'id_customers'})? " AND cu_invoices.ID_customers = '$in{'id_customers'}' ":"";
		
		$add_sql_cm .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql_cm .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";

		$add_sql .= ($in{'firstname'})? " AND sl_customers.FirstName LIKE (CONCAT('%',TRIM('$in{'firstname'}'),'%')) ":"";
		$add_sql .= ($in{'lastname1'})? " AND sl_customers.Lastname1 LIKE (CONCAT('%',TRIM('$in{'lastname1'}'),'%')) ":"";
		$add_sql .= ($in{'lastname2'})? " AND sl_customers.Lastname2 LIKE (CONCAT('%',TRIM('$in{'lastname2'}'),'%')) ":"";
		
		$add_sql .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";
		$add_sql_cm .= ($in{'customer_fcode'})? " AND cu_invoices.customer_fcode LIKE (CONCAT('%',TRIM('$in{'customer_fcode'}'),'%')) ":"";

		## Filtro por Inovices invoice_type
		my ($string_tmp);
		if ($in{'invoice_type'}){
			if ($in{'invoice_type'} =~ m/\|/){
				my @arr_tmp = split /\|/ , $in{'invoice_type'};
				for (0..$#arr_tmp) {
					$string_tmp .= "'".$arr_tmp[$_]."',";
				}
				chop $string_tmp;
				$add_sql .= " AND cu_invoices.invoice_type IN($string_tmp) ";
				$add_sql_cm .= " AND cu_invoices.invoice_type IN($string_tmp) ";
			}else{
				$add_sql .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
				$add_sql_cm .= " AND cu_invoices.invoice_type IN('$in{'invoice_type'}') ";
			}
		}

		## Filtro por Orders Ptype
		my ($string_tmp);
		if ($in{'ptype'}){
			if ($in{'ptype'} =~ m/\|/){
				my @arr_tmp = split /\|/ , $in{'ptype'};
				for (0..$#arr_tmp) {
					$string_tmp .= "'".$arr_tmp[$_]."',";
				}
				chop $string_tmp;
				$add_sql .= " AND sl_orders.ptype IN($string_tmp) ";
				$add_sql_cm .= " AND sl_creditmemos_payments.ptype IN($string_tmp) ";
			}else{
				$add_sql .= " AND sl_orders.ptype IN('$in{'ptype'}') ";
				$add_sql_cm .= " AND sl_creditmemos_payments.ptype IN('$in{'ptype'}') ";
			}
		}

		## Filtro por Orders Date
		if ($in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'}){
			$add_sql .= " AND sl_orders.Date = '$in{'from_date'}' ";
		}else{
			if ($in{'from_date'}){
				$add_sql .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}

			if ($in{'to_date'}){
				$add_sql .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}

		## Filtro por Invoices doc_date
		if ($in{'from_doc_date'} ne '' and  $in{'to_doc_date'} ne '' and $in{'from_doc_date'} eq $in{'to_doc_date'}){
			$add_sql .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
			$add_sql_cm .= " AND Date(cu_invoices.doc_date) = '$in{'from_doc_date'}' ";
		}else{
			if ($in{'from_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) >= '$in{'from_doc_date'}' ";
			}

			if ($in{'to_doc_date'}){
				$add_sql .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
				$add_sql_cm .= " AND Date(cu_invoices.doc_date) <= '$in{'to_doc_date'}' ";
			}
		}

		## Filtro por Credit Memos Date
		if ($in{'from_doc_date_cm'} ne '' and  $in{'to_doc_date_cm'} ne '' and $in{'from_doc_date_cm'} eq $in{'to_doc_date_cm'}){
			$add_sql_cm .= " AND sl_creditmemos_payments.Date = '$in{'from_doc_date_cm'}' ";
		}else{
			if ($in{'from_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date >= '$in{'from_doc_date_cm'}' ";
			}

			if ($in{'to_doc_date_cm'}){
				$add_sql_cm .= " AND sl_creditmemos_payments.Date <= '$in{'to_doc_date_cm'}' ";
			}
		}
		
		$sql = "";
		my ($sth) = &Do_SQL($sql);
		
		my $out='';
		my $recs=0;
		while (my $rec = $sth->fetchrow_hashref()){
			$recs++;

			$out .= qq|"$rec->{'expediter_fname'}","$rec->{'ID_orders'}","$rec->{'orders_date'}","$rec->{'folio'}","$rec->{'doc_date'}","$rec->{'doc_date'}","$rec->{'ID_customers'}","$rec->{'customer_fcode'}","$rec->{'Cliente'}","$rec->{'Type'}","$rec->{'net'}","$rec->{'tax'}","$rec->{'discount'}","$rec->{'total'}","$rec->{'emitida'}","$rec->{'invoice_type'}","$rec->{'Currency'}","$rec->{'exchange_rate'}","$rec->{'notes'}","$rec->{'Ptype'}","$rec->{'sales_origins'}","$rec->{'COSTO'}","$rec->{'xml_uuid'}"|."\r\n";
			
		}
		
		&auth_logging('report_view','');
		
		if ($recs){				
			my $strHeader = qq|"UNIDAD DE NEGOCIO","NO PEDIDO","FECHA DE PEDIDO","FACTURA","FECHA DE FACTURA","FECHA CONTABLE","ID CLIENTE","RFC RECEPTOR","NOMBRE CLIENTE","TIPO CLIENTE","SUB-TOTAL","IVA","DESCUENTO","TOTAL","ESTADO","TIPO FACTURA","MONEDA","TIPO DE CAMBIO","OBSERVACIONES","FORMA DE PAGO","ORIGEN VENTA","COSTO DE VENTA","UUID"|."\r\n";

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print $strHeader;
			print $out;
			
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_fin_kardex.html');
}


#############################################################################
#############################################################################
#   Function: rep_fin_transfer_warehouse.html
#
#       Es: Reporte de Transferencia de Almacen
#       En: Transfer Warehouse
#
#
#    Created on: 13/07/2015
#
#    Author: LI Huitzilihuitl Ceja
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_fin_transfer_warehouse {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'warehouse_transfers_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my ($add_sql);

		$in{'id_products_sql'} = ($in{'id_products'})? (400000000+$in{'id_products'}):$in{'id_products'};
		$add_sql .= ($in{'id_products'})? " AND sl_skus_trans.ID_products = '$in{'id_products_sql'}' ":"";
		$add_sql .= ($in{'upc'})? " AND sl_sku.UPC = '$in{'upc'}' ":"";

		if ($in{'id_warehouses'}){
			my $tmp_warehouses = $in{'id_warehouses'};
			$tmp_warehouses =~ s/\|/,/g;
			$add_sql .= " AND sl_skus_trans.ID_warehouses IN ($tmp_warehouses) ";
		}

		## Filtro por Orders Date
		if ( $in{'from_date'} ne '' and  $in{'to_date'} ne '' and $in{'from_date'} eq $in{'to_date'} ){
			$add_sql .= " AND sl_skus_trans.Date = '$in{'from_date'}' ";
		}elsif( $in{'from_date'} ne '' and  $in{'to_date'} ne '') {
			if ($in{'from_date'}){
				$add_sql .= " AND sl_skus_trans.Date >= '$in{'from_date'}' ";
			}
			if ($in{'to_date'}){
				$add_sql .= " AND sl_skus_trans.Date <= '$in{'to_date'}' ";
			}
		}elsif ($in{'from_date'}){
			$add_sql .= " AND sl_skus_trans.Date >= '$in{'from_date'}' ";
		}

		if ($in{'from_date'} eq '' and  $in{'to_date'} eq ''){
			$add_sql .= " AND sl_skus_trans.Date = CURDATE() ";
		}
		
		$sql = "
			SELECT
				out_Date AS Fecha
				, out_ID_trs AS 'Pedido'
				, (select CONCAT(sl_parts.Name,'/',sl_parts.Model) from sl_parts inner join sl_skus on sl_skus.ID_sku_products=(400000000+sl_parts.ID_parts) where sl_skus.ID_sku_products=out_ID_products)DESCRIPCION
				, out_ID_warehouses 'W ORIGEN'
				, out_warehouses
				, out_Location 'L ORIGEN'
				, in_ID_warehouses 'W DESTINO'
				, in_warehouses
				, in_Location 'L DESTINO'
				, in_Tipo 'TIPO'
				, IF(in_Tipo='TRANSFERENCIA','',IF(((SELECT Type FROM sl_warehouses WHERE sl_warehouses.ID_warehouses=out_ID_warehouses)='Virtual'),'DEVOLUCION COD','VENTA COD'))SUBTIPO
				, ID_admin_users 'ID USUARIO'
				, Usuario 'USUARIO'
				, out_ID_products AS SKU
				, UPC
				, in_Quantity CANTIDAD
			FROM (
				SELECT
					sl_skus_trans.ID_products out_ID_products
					, sl_skus.UPC
					, ID_products_trans out_ID_products_trans
					, sl_skus_trans.ID_warehouses out_ID_warehouses
					, sl_warehouses.Name out_warehouses
					, Location out_Location
					, sl_skus_trans.Type out_Type
					, Type_trans out_Type_trans
					, tbl_name out_tbl_name
					, ID_trs out_ID_trs
					, SUM(Quantity) out_Quantity
					, sl_skus_trans.Date out_Date
					, sl_skus_trans.Time out_Time
					, CASE tbl_name
						WHEN 'sl_manifests' THEN 'TRANSFERENCIA'
						WHEN 'sl_orders' THEN 'COD'
						ELSE 'DESCONOCIDO'
					END AS out_Tipo
				FROM sl_skus_trans
				LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_skus_trans.ID_products
				INNER JOIN sl_warehouses ON sl_skus_trans.ID_warehouses=sl_warehouses.ID_warehouses
				WHERE sl_skus_trans.Type='Transfer Out'
				$add_sql
				GROUP BY ID_trs, sl_skus_trans.ID_warehouses, Location, sl_skus_trans.ID_products
			 	ORDER BY ID_products_trans DESC
			)Salidas 
			LEFT JOIN 
			(
				SELECT
					ID_products in_ID_products
					, ID_products_trans in_ID_products_trans
					, sl_skus_trans.ID_warehouses in_ID_warehouses
					, sl_warehouses.Name in_warehouses
					, Location in_Location
					, sl_skus_trans.Type in_Type
					, Type_trans in_Type_trans
					, tbl_name in_tbl_name
					, ID_trs in_ID_trs
					, SUM(Quantity) in_Quantity
					, admin_users.ID_admin_users
					, UPPER(CONCAT(admin_users.FirstName,' ',admin_users.MiddleName,' ',admin_users.LastName))Usuario
					, sl_skus_trans.Date in_Date
					, sl_skus_trans.Time in_Time
					, CASE tbl_name
						WHEN 'sl_manifests' THEN 'TRANSFERENCIA'
						WHEN 'sl_orders' THEN 'COD'
						ELSE 'DESCONOCIDO'
					END AS in_Tipo
				FROM sl_skus_trans 
				INNER JOIN admin_users ON admin_users.ID_admin_users=sl_skus_trans.ID_admin_users
				INNER JOIN sl_warehouses ON sl_skus_trans.ID_warehouses=sl_warehouses.ID_warehouses
				WHERE sl_skus_trans.Type='Transfer In'
				$add_sql
				GROUP BY ID_trs, sl_skus_trans.ID_warehouses, Location, sl_skus_trans.ID_products
			)Entradas ON Entradas.in_tbl_name=Salidas.out_tbl_name AND Entradas.in_ID_trs=Salidas.out_ID_trs AND Entradas.in_ID_products=Salidas.out_ID_products;";
		my ($sth) = &Do_SQL($sql);
		
		my $out = '';
		my $recs = 0;
		while (my $rec = $sth->fetchrow_hashref()){
			$recs++;
			$out .= qq|"$rec->{'Fecha'}","$rec->{'Pedido'}","$rec->{'SKU'}","$rec->{'UPC'}","$rec->{'DESCRIPCION'}","$rec->{'W ORIGEN'}-$rec->{'out_warehouses'}","$rec->{'L ORIGEN'}","$rec->{'W DESTINO'}-$rec->{'in_warehouses'}","$rec->{'L DESTINO'}","$rec->{'CANTIDAD'}","$rec->{'TIPO'}","$rec->{'SUBTIPO'}","$rec->{'ID USUARIO'}","$rec->{'USUARIO'}"|."\r\n";
		}
		
		&auth_logging('report_view','');
		
		if ($recs){				
			my $strHeader = qq|"FECHA","ID","SKU","UPC","DESCRIPCION","ALMACEN ORIGEN","GAVETA ORIGEN","ALMACEN DESTINO","GAVETA DESTINO","CANTIDAD","TIPO","SUBTIPO","ID USUARIO","USUARIO"|."\r\n";

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print $strHeader;
			print $out;
			
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_fin_transfer_warehouse.html');
}

#############################################################################
#############################################################################
#   Function: rep_fin_inventory_valuation
#
#       Es: Reporte de Valuacion de Inventario
#       En: Inventory Valuation Report
#
#
#    Created on: 05/10/2015
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub rep_fin_inventory_valuation {
#############################################################################
#############################################################################

	if ($in{'action'}){
		
		my $output = '';
		
		my $fname   = 'inventory_valuation_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;

		my ($add_sql, $add_sql_sku);

		$in{'id_products_sql'} = ($in{'id_products'})? (400000000+$in{'id_products'}):$in{'id_products'};
		$add_sql .= ($in{'id_products'})? " AND sl_warehouses_location.ID_products = '$in{'id_products_sql'}' ":"";
		$add_sql .= ($in{'upc'})? " AND sl_skus.UPC = '$in{'upc'}' ":"";

		if ($in{'id_warehouses'}){
			my $tmp_warehouses = $in{'id_warehouses'};
			$tmp_warehouses =~ s/\|/,/g;
			$add_sql .= " AND sl_warehouses_location.ID_warehouses IN ($tmp_warehouses) ";
			$add_sql_sku = " AND sl_warehouses_location.ID_warehouses IN ($tmp_warehouses) ";
		}

		# , ROUND(SUM(sl_warehouses_location.Quantity) * (
		# 	SELECT AVG(sl_skus_cost.Cost)Cost
		# 	FROM sl_skus_cost
		# 	WHERE sl_skus_cost.ID_warehouses=sl_warehouses_location.ID_warehouses
		# 	AND sl_skus_cost.ID_products=sl_warehouses_location.ID_products
		# 	GROUP BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products
		# ),2) AS 'COSTO'

		## Costo LIFO/FIFO
		my $sql = '';
		if( !$in{'details'} ){
			$sql = "SELECT 
						cu_company_legalinfo.Name AS 'UNIDAD DE NEGOCIO'
						, CURDATE() AS 'FECHA'
						, CURTIME() AS 'HORA'
						, sl_warehouses_location.ID_products AS 'SKU'
						, sl_skus.UPC AS 'UPC'
						, CONCAT(sl_parts.Model,'/',sl_parts.Name) AS 'DESCRIPCION'
						, sl_parts.Classification AS 'CLASIFICACION'
						, SUM(sl_warehouses_location.Quantity) AS 'CANTIDAD'
						, ROUND((
							SELECT SUM(sl_skus_cost.Quantity * sl_skus_cost.Cost)Cost
							FROM sl_skus_cost
							WHERE sl_skus_cost.ID_products=sl_warehouses_location.ID_products
								$add_sql_sku
							GROUP BY sl_skus_cost.ID_products
						),2) AS 'COSTO'
					FROM sl_warehouses_location
						INNER JOIN sl_skus ON sl_skus.ID_sku_products=sl_warehouses_location.ID_products
						INNER JOIN sl_parts ON sl_parts.ID_parts=sl_skus.ID_products AND (400000000+sl_parts.ID_parts)=sl_skus.ID_sku_products
						INNER JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord='Yes'
					WHERE 1 
						AND sl_warehouses_location.Quantity > 0
						$add_sql
					GROUP BY sl_warehouses_location.ID_products
					ORDER BY sl_warehouses_location.ID_products;";
		}else{
			$sql = "
				SELECT 
					cu_company_legalinfo.Name AS 'UNIDAD DE NEGOCIO'
					, CURDATE() AS 'FECHA'
					, CURTIME() AS 'HORA'
					, sl_warehouses_location.ID_warehouses AS 'ID ALMACEN'
					, sl_warehouses.Name AS 'ALMACEN'
					, sl_warehouses.Type AS 'TIPO'
					, sl_warehouses_location.ID_products AS 'SKU'
					, sl_skus.UPC AS 'UPC'
					, CONCAT(sl_parts.Model,'/',sl_parts.Name) AS 'DESCRIPCION'
					, sl_parts.Classification AS 'CLASIFICACION'
					, SUM(sl_warehouses_location.Quantity) AS 'CANTIDAD'
					, ROUND((
						SELECT SUM(sl_skus_cost.Quantity * sl_skus_cost.Cost)Cost
						FROM sl_skus_cost
						WHERE sl_skus_cost.ID_warehouses=sl_warehouses_location.ID_warehouses
						AND sl_skus_cost.ID_products=sl_warehouses_location.ID_products
						GROUP BY sl_skus_cost.ID_warehouses, sl_skus_cost.ID_products
					),2) AS 'COSTO'
				FROM sl_warehouses_location
				INNER JOIN sl_skus ON sl_skus.ID_sku_products=sl_warehouses_location.ID_products
				INNER JOIN sl_parts ON sl_parts.ID_parts=sl_skus.ID_products AND (400000000+sl_parts.ID_parts)=sl_skus.ID_sku_products
				INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_location.ID_warehouses
				INNER JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord='Yes'
				WHERE 1 
					AND sl_warehouses_location.Quantity > 0
					$add_sql
				GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products
				ORDER BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products;";
		}
		my ($sth) = &Do_SQL($sql);
		
		my $out = '';
		my $recs = 0;
		while (my $rec = $sth->fetchrow_hashref()){
			$recs++;

			### Cost
			my $cost = '';
			### Costo promedio
			if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
				my $sql_cost = "SELECT Cost_Avg FROM cu_skus_trans WHERE ID_products = ".$rec->{'SKU'}.";";
				my $sth_cost = &Do_SQL($sql_cost);
				$cost = $sth_cost->fetchrow();
				if( $cost ){
					$rec->{'COSTO'} = round($cost * $rec->{'CANTIDAD'}, 2);
				}else{
					my $sql_cost = "SELECT Cost_Avg FROM sl_skus_trans WHERE ID_products = ".$rec->{'SKU'}." ORDER BY Date DESC, Time DESC, ID_products_trans DESC LIMIT 1;";
					my $sth_cost = &Do_SQL($sql_cost);
					$cost = $sth_cost->fetchrow();
					$rec->{'COSTO'} = round($cost * $rec->{'CANTIDAD'}, 2);
				}
			}

			if( !$in{'details'} ){
				$out .= qq|"$rec->{'UNIDAD DE NEGOCIO'}","$rec->{'FECHA'}","$rec->{'HORA'}","$rec->{'SKU'}","$rec->{'UPC'}","$rec->{'DESCRIPCION'}","$rec->{'CLASIFICACION'}","$cost","$rec->{'CANTIDAD'}","$rec->{'COSTO'}"|."\r\n";
			}else{
				$out .= qq|"$rec->{'UNIDAD DE NEGOCIO'}","$rec->{'FECHA'}","$rec->{'HORA'}","$rec->{'ID ALMACEN'}","$rec->{'ALMACEN'}","$rec->{'TIPO'}","$rec->{'SKU'}","$rec->{'UPC'}","$rec->{'DESCRIPCION'}","$rec->{'CLASIFICACION'}","$cost","$rec->{'CANTIDAD'}","$rec->{'COSTO'}"|."\r\n";				
			}
		}
		
		&auth_logging('report_view','');
		
		if ($recs){
			my $strHeader;
			if( !$in{'details'} ){
				$strHeader = qq|"UNIDAD DE NEGOCIO","FECHA","HORA","SKU","UPC","DESCRIPCION","CLASIFICACION","COSTO UNITARIO","CANTIDAD","COSTO DE INVENTARIO"|."\r\n";
			}else{		
				$strHeader = qq|"UNIDAD DE NEGOCIO","FECHA","HORA","ID ALMACEN","ALMACEN","TIPO","SKU","UPC","DESCRIPCION","CLASIFICACION","COSTO UNITARIO","CANTIDAD","COSTO DE INVENTARIO"|."\r\n";
			}

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print $strHeader;
			print $out;
			
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}

	$va{'method_cost'} = "LIFO/FIFO";
	$va{'method_cost'} = "AVERAGE" if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average');

	print "Content-type: text/html\n\n";
	print &build_page('rep_fin_inventory_valuation.html');
}

1;