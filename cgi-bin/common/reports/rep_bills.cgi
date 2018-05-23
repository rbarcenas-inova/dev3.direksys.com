#!/usr/bin/perl
##################################################################
#   REPORTS : BILLS
##################################################################

#############################################################################
#############################################################################
#   Function: rep_bills_flow
#
#       Es: Reporte de Detalle de Flujo para Cuentas por Pagar
#       En: Flow Detail Report for Accounts Payable
#
#
#    Created on: 28/05/2013
#
#    Author: Alejandro Diaz
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
sub rep_bills_flow{
#############################################################################
#############################################################################

	if($in{'action'}) {

		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';

		my $add_filters='';
		
		###### Busqueda por rango de fecha
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};

		
		my $fname   = 'bills_flow_detail_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = qq|"Unidad de Negocio","Proveedor","Nombre","Comprobante","Estatus","Factura No","Fecha Contable","Tipo Comprobante","Factura","<8","<15","<21","<30","<60","<90","<9999",">8",">15",">21",">30",">60",">90",">9999","Moneda","Tipo de cambio","TOTAL VENCIDO","TOTAL NO VENCIDO","TOTAL SEM.","No Cuenta","Cuenta"|;

		my $add_sql = ($in{'filter'} and $in{'filter'} eq 'topay')? " AND sl_bills.Status ='To Pay'":" AND sl_bills.Status NOT IN ('Paid','Void')";
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors=sl_vendors.ID_vendors WHERE 1 $add_sql AND sl_bills.Amount > 0");
		my ($total) = $sth->fetchrow();

		if($total) {
			# print "Content-type: text/html\n\n";
			#print '<meta http-equiv="Content-Type" content="text/html;charset=iso-8859-1" />';

			$sql = "SELECT GROUP_CONCAT(DISTINCT sl_vendors.ID_accounts_credit)ID_accounts FROM sl_vendors WHERE sl_vendors.ID_accounts_credit > 0;";
			my $sth_accounts = &Do_SQL($sql);
			my $possible_accounts = $sth_accounts->fetchrow_array();

			my $sth2 = &Do_SQL("SELECT 
			cu_company_legalinfo.Name
			, sl_bills.ID_vendors
			, sl_vendors.CompanyName
			, sl_bills.ID_bills
			, sl_bills.Status
			, sl_bills.Invoice
			, sl_bills.BillDate
			, sl_bills.Type
			, sl_bills.Memo
			, IF(sl_bills.currency_exchange > 0, sl_bills.currency_exchange, 1) AS currency_exchange
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<0 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-8,1,0)NOVENCIDO8
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-9 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-15,1,0)NOVENCIDO15
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-16 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-21,1,0)NOVENCIDO21
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-22 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-30,1,0)NOVENCIDO30
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-31 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-60,1,0)NOVENCIDO60
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-61 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=-90,1,0)NOVENCIDO90
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=-91,1,0)NOVENCIDO9999
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=0 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=8,1,0)VENCIDO8
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=9 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=15,1,0)VENCIDO15
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=16 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=21,1,0)VENCIDO21
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=22 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=30,1,0)VENCIDO30
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=31 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=60,1,0)VENCIDO60
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=61 AND DATEDIFF('$in{'from_date'}', sl_bills.DueDate)<=90,1,0)VENCIDO90
			, IF(DATEDIFF('$in{'from_date'}', sl_bills.DueDate)>=91,1,0)VENCIDO9999
			, sl_bills.Currency
			, sl_bills_pos.ID_bills_pos
			, sl_bills_pos.ID_purchaseorders
			FROM sl_bills
			LEFT JOIN sl_bills_pos ON sl_bills_pos.ID_bills=sl_bills.ID_bills
			LEFT JOIN cu_company_legalinfo ON PrimaryRecord='YES'
			INNER JOIN sl_vendors ON sl_bills.ID_vendors=sl_vendors.ID_vendors
			WHERE 1 $add_sql AND sl_bills.Amount > 0
			GROUP BY sl_bills.ID_bills
			ORDER BY cu_company_legalinfo.Name;");

			my $records = 0;
			my $strout = '';
			while ($rec = $sth2->fetchrow_hashref()) {
				$records++;
				my ($bill_amount_payable) = &bills_amount_due($rec->{'ID_bills'});
				
				## Revisar si es una Nota de Credito, sl_bills.Type='Credit'   Monto que se debe es igual (* -1)
				if ($rec->{'Type'} eq 'Credit'){
					$bill_amount_payable = &credit_amount_due($rec->{'ID_bills'});
					if ($bill_amount_payable >= 0){
						 $bill_amount_payable = ($bill_amount_payable * -1);
						#&cgierr($bill_amount_payable);
					}

				}
				
				my $venc=0;
				my $novenc=0;
				my $total_venc=0;
				my $total_novenc=0;
				
				$strout .= qq|"$rec->{'Name'}","$rec->{'ID_vendors'}","$rec->{'CompanyName'}","$rec->{'ID_bills'}","$rec->{'Status'}","$rec->{'Invoice'}","$rec->{'BillDate'}","$rec->{'Type'}","$rec->{'Memo'}"|;
				
				if ($rec->{'VENCIDO8'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO15'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO21'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO30'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO60'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO90'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'VENCIDO9999'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$venc=1;
					$total_venc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO8'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO15'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO21'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO30'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO60'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO90'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				if ($rec->{'NOVENCIDO9999'} == 1) {
					$strout .= qq|,"$bill_amount_payable"|;
					$novenc=1;
					$total_novenc += $bill_amount_payable;
				}else{
					$strout .= qq|,"0"|;
				}

				# Moneda
				$strout .= qq|,"$rec->{'Currency'}"|;

				# Tipo de cambio
				$strout .= qq|,"$rec->{'currency_exchange'}"|;

				# TOTAL VENCIDO
				$strout .= qq|,"$total_venc"|;
				
				# TOTAL NO VENCIDO
				$strout .= qq|,"$total_novenc"|;
				
				# TOTAL SEM.
				$strout .= qq|,"$bill_amount_payable"|;

				## Informacion Contable
				## Si son BILLS de PO
				if ($rec->{'ID_bills_pos'}){
					$sql = "SELECT sl_accounts.ID_accounting, sl_accounts.Name
					FROM sl_movements
					INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
					WHERE sl_movements.tablerelated='sl_bills'
					AND sl_movements.ID_tablerelated=$rec->{'ID_bills'}
					AND sl_movements.Credebit='Credit'
					-- AND sl_movements.ID_accounts IN ($possible_accounts)
					ORDER BY sl_movements.ID_movements
					LIMIT 1;";
				}else{
					$sql = "SELECT sl_accounts.ID_accounting, sl_accounts.Name
					FROM sl_movements
					INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
					WHERE sl_movements.tableused='sl_bills'
					AND sl_movements.ID_tableused=$rec->{'ID_bills'}
					AND sl_movements.Credebit='Credit'
					AND sl_movements.ID_accounts IN ($possible_accounts)
					ORDER BY sl_movements.ID_movements
					LIMIT 1;";
				}

				my $sth_info = &Do_SQL($sql);
				my $rec_info = $sth_info->fetchrow_hashref();

				## Si aun asi no lo encontro
				if ($rec_info->{'ID_accounting'} eq '' and $rec->{'ID_purchaseorders'} > 0){
					$sql = "SELECT sl_accounts.ID_accounting, sl_accounts.Name
					FROM sl_movements
					INNER JOIN sl_accounts ON sl_accounts.ID_accounts=sl_movements.ID_accounts
					WHERE 1
					AND sl_movements.tableused='sl_purchaseorders' 
					AND sl_movements.ID_tableused=$rec->{'ID_purchaseorders'}
					AND sl_movements.ID_accounts IN ($possible_accounts)
					AND sl_movements.Credebit='Credit'
					ORDER BY sl_movements.ID_movements
					LIMIT 1;";
					$sth_info = &Do_SQL($sql);
					$rec_info = $sth_info->fetchrow_hashref();
				}
				

				$strout .= qq|,"|.&format_account($rec_info->{'ID_accounting'}).qq|","$rec_info->{'Name'}"\r\n|;

			}
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			print "$strHeader\r\n";
			print $strout;

			&auth_logging('report_view','');
			return;

		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bills_flow.html');

}

#############################################################################
#############################################################################
#   Function: rep_bills_banks
#
#       Es: Reporte de Detalle de Pagos
#       En: 
#
#
#    Created on: 03/06/2013
#
#    Author: EO
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
sub rep_bills_banks{
#############################################################################
#############################################################################

	if($in{'action'}) {

		my ($query_list);
		my $maxprod=1;
		my $info_user =	'';
		my $info_pprod = '';
		my $info_oprod = '';
		my $info_time = '';
		my $strout = '';
		my $add_filters = '';

		$add_filters = " AND ID_banks='$in{'id_banks'}'" if ($in{'id_banks'});

		my $fname   = 'bills_banks_detail_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		my $strHeader = "Fecha, Metodo de Pago, Referencia, ID Proveedor, Proveedor, Importe Pago, Moneda, ID Aviso, No. Factura, Importe Pagado, Mensaje, Banco, Cuenta, UN";
		my ($sth_ext) = &Do_SQL("SELECT sl_bills.ID_bills, sl_bills.Amount, sl_bills.Memo,
									sl_vendors.CompanyName, sl_vendors.ID_vendors, sl_vendors.Currency, sl_vendors.PaymentMethod,
									cu_company_legalinfo.Name as UN
									FROM sl_bills 
									INNER JOIN sl_vendors using(ID_vendors)
									LEFT JOIN cu_company_legalinfo on PrimaryRecord='Yes'
									WHERE ID_bills IN (SELECT tableid FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE tablename='bills' $add_filters);");
									
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		
		while ($rec_ext = $sth_ext->fetchrow_hashref()) {
				my $sql_filters = '';
				$sql_filters .= " AND BankDate >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
				$sql_filters .= " AND BankDate <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
				
				my ($sth_int) = &Do_SQL("SELECT BankDate, doc_type, ifnull(RefNumCustom,RefNum)RefNum,Amount,Name,SubAccountOf,Memo,if (sl_banks_movements.currency_exchange IS NOT NULL AND sl_banks_movements.currency_exchange>1,(sl_banks_movrel.AmountPaid*sl_banks_movements.currency_exchange),sl_banks_movrel.AmountPaid)AmountPaid
									FROM sl_banks_movements
									INNER JOIN sl_banks USING(ID_banks)
									INNER JOIN sl_banks_movrel USING(ID_banks_movements)
									WHERE tablename='bills' AND tableid='$rec_ext->{'ID_bills'}'
									AND Type='Credits'
									$sql_filters;");
											
				my $records = 0;
				while ($rec_int = $sth_int->fetchrow_hashref()) {
					# Extraer nombre de beneficiario
					$beneficiary = $rec_int->{'Memo'};
					
					
					my $strout;
					$strout .= qq|"$rec_int->{'BankDate'}"|;
					$strout .= qq|,"$rec_int->{'doc_type'}"|;
					$strout .= qq|,"$rec_int->{'RefNum'}"|;
					$strout .= qq|,"$rec_ext->{'ID_vendors'}"|;
					$strout .= qq|,"$rec_ext->{'CompanyName'}"|;
					$strout .= qq|,"$rec_int->{'AmountPaid'}"|;
					$strout .= qq|,"$rec_ext->{'Currency'}"|;
					$strout .= qq|,"$rec_ext->{'ID_bills'}"|;
					$strout .= qq|,"$rec_ext->{'Memo'}"|;
					$strout .= qq|,"$rec_int->{'Amount'}"|;
					$strout .= qq|,"$beneficiary"|;
					$strout .= qq|,"$rec_int->{'Name'}"|;
					$strout .= qq|,"$rec_int->{'SubAccountOf'}"|;
					
					# TOTAL SEM.
					$strout .= qq|,"$rec_ext->{'UN'}"\r\n|;
					
					print $strout;
				}
		}

		&auth_logging('report_view','');
		return;
		
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bills_banks.html');

}

#############################################################################
#############################################################################
#   Function: rep_bills_po_payable
#
#       Es: Reporte de Detalle de Pagos
#       En: 
#
#
#    Created on: 07/03/2013
#
#    Author: EO
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
sub rep_bills_po_payable{
#############################################################################
#############################################################################

	if ($in{'action'}) {

		my $strout = '';
		my $sql_filters = '';
		my $fname   = 'bills_po_payable_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		$sql_filters .= " AND sl_purchaseorders.ID_purchaseorders='".&filter_values($in{'id_purchaseorders'})."'" if ($in{'id_purchaseorders'});
		$sql_filters .= " AND sl_purchaseorders.ID_vendors='".&filter_values($in{'id_vendors'})."'" if ($in{'id_vendors'});
		$sql_filters .= " AND sl_purchaseorders.Date >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
		$sql_filters .= " AND sl_purchaseorders.Date <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
		
		my $strHeader = qq|"UN","ID Proveedor","Proveedor","Moneda","PO","PO Fecha","Total sin IVA","IVA","Total","Recepcion sin IVA","Recepcion IVA","Recepcion Total","BIlls Total"|;
		my ($sth) = &Do_SQL("
		SELECT
			cu_company_legalinfo.Name 
			, sl_vendors.ID_vendors
			, sl_vendors.CompanyName
			, sl_vendors.Currency
			, sl_purchaseorders.ID_purchaseorders
			, sl_purchaseorders.PODate
			, ROUND(SUM(sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price),2)MontosinIVARecepcion
			, ROUND(SUM(sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price * sl_purchaseorders_items.Tax_percent),2)IVARecepcion
			, ROUND(SUM((sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price) + (sl_purchaseorders_wreceipts.Quantity * sl_purchaseorders_items.Price * sl_purchaseorders_items.Tax_percent)),2)TotalRecepcion
			,(
				SELECT ROUND(SUM(sl_bills_pos.Amount),2)
				FROM sl_bills_pos
				INNER JOIN sl_bills ON sl_bills_pos.ID_bills=sl_bills.ID_bills
				WHERE sl_bills_pos.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders
				AND sl_bills.Status NOT IN ('Void')
				GROUP BY sl_bills_pos.ID_purchaseorders
			)BillsAmount
		FROM sl_purchaseorders
		INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders
		INNER JOIN sl_purchaseorders_wreceipts ON sl_purchaseorders_wreceipts.ID_purchaseorders_items=sl_purchaseorders_items.ID_purchaseorders_items
		INNER JOIN sl_wreceipts_items ON sl_wreceipts_items.ID_wreceipts_items=sl_purchaseorders_wreceipts.ID_wreceipts_items
		INNER JOIN sl_vendors ON sl_vendors.ID_vendors=sl_purchaseorders.ID_vendors
		LEFT JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord='Yes'
		WHERE 1
		$sql_filters
		GROUP BY sl_purchaseorders_items.ID_purchaseorders;");
									
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		while ($rec = $sth->fetchrow_hashref()) {
				
				my ($sth_po) = &Do_SQL("SELECT 
					sl_purchaseorders_items.ID_purchaseorders
					, SUM(sl_purchaseorders_items.Price * sl_purchaseorders_items.Qty)TotalsinIVA
					, SUM(sl_purchaseorders_items.Tax)Tax
					, SUM(sl_purchaseorders_items.Total)Total
				FROM sl_purchaseorders_items
				WHERE sl_purchaseorders_items.ID_purchaseorders='$rec->{'ID_purchaseorders'}'
				GROUP BY sl_purchaseorders_items.ID_purchaseorders");
				my $rec_po = $sth_po->fetchrow_hashref();
											
				$strout .= qq|"$rec->{'Name'}",|;
				$strout .= qq|"$rec->{'ID_vendors'}",|;
				$strout .= qq|"$rec->{'CompanyName'}",|;
				$strout .= qq|"$rec->{'Currency'}",|;
				$strout .= qq|"$rec->{'ID_purchaseorders'}",|;
				$strout .= qq|"$rec->{'PODate'}",|;
				$strout .= qq|"|.&format_price($rec_po->{'TotalsinIVA'}).qq|",|;
				$strout .= qq|"|.&format_price($rec_po->{'Tax'}).qq|",|;
				$strout .= qq|"|.&format_price($rec_po->{'Total'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'MontosinIVARecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'IVARecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'TotalRecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'BillsAmount'}).qq|"\r\n|;
		}
		print $strout;

		&auth_logging('report_view','');
		return;
		
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bills_po_payable.html');

}

#############################################################################
#############################################################################
#   Function: rep_bills_po_ni_payable
#
#       Es: Reporte de Detalle de Pagos para recepciones no inventariables
#       En: 
#
#
#    Created on: 07/03/2013
#
#    Author: EO
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
sub rep_bills_po_ni_payable {
#############################################################################
#############################################################################

	if ($in{'action'}) {

		my $strout = '';
		my $sql_filters = '';
		my $fname   = 'bills_po_payable_'.$cfg{'app_title'}.'.csv';
		$fname =~ s/\s/_/g;
		
		$sql_filters .= " AND sl_purchaseorders.ID_purchaseorders='".&filter_values($in{'id_purchaseorders'})."'" if ($in{'id_purchaseorders'});
		$sql_filters .= " AND sl_purchaseorders.ID_vendors='".&filter_values($in{'id_vendors'})."'" if ($in{'id_vendors'});
		$sql_filters .= " AND sl_purchaseorders.Date >= '".&filter_values($in{'from_date'})."'" if ($in{'to_date'});
		$sql_filters .= " AND sl_purchaseorders.Date <= '".&filter_values($in{'to_date'})."'" if ($in{'to_date'});
		
		my $strHeader = qq|"UN","ID Proveedor","Proveedor","Moneda","PO","PO Fecha","Total sin IVA","IVA","Total","Recepcion sin IVA","Recepcion IVA","Recepcion Total","BIlls Total"|;
		my ($sth) = &Do_SQL("
		SELECT
			cu_company_legalinfo.Name 
			, sl_vendors.ID_vendors
			, sl_vendors.CompanyName
			, sl_vendors.Currency
			, sl_purchaseorders.ID_purchaseorders
			, sl_purchaseorders.PODate
			, ROUND(SUM(sl_purchaseorders_items.Received * sl_purchaseorders_items.Price),2)MontosinIVARecepcion
			, ROUND(SUM(sl_purchaseorders_items.Received * sl_purchaseorders_items.Price * sl_purchaseorders_items.Tax_percent),2)IVARecepcion
			, ROUND(SUM((sl_purchaseorders_items.Received * sl_purchaseorders_items.Price) + (sl_purchaseorders_items.Received * sl_purchaseorders_items.Price * sl_purchaseorders_items.Tax_percent)),2)TotalRecepcion
			,(
				SELECT ROUND(SUM(sl_bills_pos.Amount),2)
				FROM sl_bills_pos
				INNER JOIN sl_bills ON sl_bills_pos.ID_bills=sl_bills.ID_bills
				WHERE sl_bills_pos.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders
				AND sl_bills.Status NOT IN ('Void')
				GROUP BY sl_bills_pos.ID_purchaseorders
			)BillsAmount
		FROM sl_purchaseorders
		INNER JOIN sl_purchaseorders_items ON sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders
		INNER JOIN sl_vendors ON sl_vendors.ID_vendors=sl_purchaseorders.ID_vendors
		LEFT JOIN cu_company_legalinfo ON cu_company_legalinfo.PrimaryRecord='Yes'
		WHERE sl_purchaseorders_items.ID_products>=500000000
		$sql_filters
		GROUP BY sl_purchaseorders_items.ID_purchaseorders;");
									
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=$fname\n\n";
		print "$strHeader\r\n";
		
		while ($rec = $sth->fetchrow_hashref()) {
				
				my ($sth_po) = &Do_SQL("SELECT 
					sl_purchaseorders_items.ID_purchaseorders
					, SUM(sl_purchaseorders_items.Price * sl_purchaseorders_items.Qty)TotalsinIVA
					, SUM(sl_purchaseorders_items.Tax)Tax
					, SUM(sl_purchaseorders_items.Total)Total
				FROM sl_purchaseorders_items
				WHERE sl_purchaseorders_items.ID_purchaseorders='$rec->{'ID_purchaseorders'}'
				GROUP BY sl_purchaseorders_items.ID_purchaseorders");
				my $rec_po = $sth_po->fetchrow_hashref();
											
				$strout .= qq|"$rec->{'Name'}",|;
				$strout .= qq|"$rec->{'ID_vendors'}",|;
				$strout .= qq|"$rec->{'CompanyName'}",|;
				$strout .= qq|"$rec->{'Currency'}",|;
				$strout .= qq|"$rec->{'ID_purchaseorders'}",|;
				$strout .= qq|"$rec->{'PODate'}",|;
				$strout .= qq|"|.&format_price($rec_po->{'TotalsinIVA'}).qq|",|;
				$strout .= qq|"|.&format_price($rec_po->{'Tax'}).qq|",|;
				$strout .= qq|"|.&format_price($rec_po->{'Total'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'MontosinIVARecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'IVARecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'TotalRecepcion'}).qq|",|;
				$strout .= qq|"|.&format_price($rec->{'BillsAmount'}).qq|"\r\n|;
		}
		print $strout;

		&auth_logging('report_view','');
		return;
		
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_bills_po_payable.html');

}

1;