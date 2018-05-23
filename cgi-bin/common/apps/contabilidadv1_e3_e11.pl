#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

#use strict;
#use Perl::Critic;
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
#local(%in) = &parse_form;
local ($in{'e'}) = 11 if (!$in{'e'});
# chdir($dir);

$in{'process'} = 'commit';

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ('cybersubs.cgi');
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

#################################################################
#################################################################
#	Function: main
#
#   		Main function: Calls execution scripts. Script called from cron task
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By: Alejandro Diaz
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#
#   	See Also:
#
sub main {
#################################################################
#################################################################

	$|++;
	&connect_db;
	&accounting;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: execute_outsourcing_batch
#
#   		This functions reads from several outsourcing callcenters /home/ccname/orders paths. The file inside contains orders created by Listen Up Callcenter to be processed in Direksys. The script validate and create every order and send them to authorize if necessary
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:Alejandro Diaz
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#
#   	See Also:
#
sub accounting{
#################################################################
#################################################################
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - CONTABILIDAD $process</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}
	
	## Definicion de rango de fechas
	$in{'date_from'} = '2014-01-01';
	$in{'date_to'} = '2014-11-11'; # Solo cambiar el mes, para no buscar dia de fin de mes

	$sys{'fmt_curr_decimal_digits'} = 2 if(!$sys{'fmt_curr_decimal_digits'});

# if ($in{'fact'} == 1) {

	print qq|<H2 style="color:red;">F A C T U R A S</H2>|;
	# FACTURAS
	# Recorrer las facturas cu_invoices
	# Extraer su ID_orders o ID_creditmemos
	$doc_date = $in{'doc_date'} if($in{'doc_date'});
	$sql = "
	SELECT 
		cu_invoices.invoice_type
		,cu_invoices_lines.ID_invoices_lines
		,cu_invoices_lines.ID_invoices
		,cu_invoices.doc_serial
		,cu_invoices.doc_num
		,cu_invoices.ID_customers
		,sl_customers.Currency
		,cu_invoices_lines.ID_orders
		,cu_invoices_lines.ID_creditmemos
		,cu_invoices_lines.ID_debitmemos
		,cu_invoices_lines.ID_orders_products
		,cu_invoices_lines.description
		,DATE(cu_invoices.doc_date)doc_date
		,cu_invoices.invoice_net
		,cu_invoices.total_taxes_transfered
		,cu_invoices.invoice_total
		,(cu_invoices.invoice_net+cu_invoices.total_taxes_transfered)TOTAL_SQL
		, SUM(sl_orders_products.Cost) Cost
		, SUM(sl_orders_products.Shipping) Shipping
		, SUM(sl_orders_products.SalePrice-sl_orders_products.Discount) SalePrice
	FROM cu_invoices INNER JOIN cu_invoices_lines ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices
	LEFT JOIN sl_orders_products ON sl_orders_products.ID_orders_products=cu_invoices_lines.ID_orders_products
	INNER JOIN sl_customers ON sl_customers.ID_customers=cu_invoices.ID_customers
	WHERE cu_invoices.Status='Certified'
	AND cu_invoices.invoice_type='ingreso'
	AND DATE(cu_invoices.doc_date) >= '$in{'date_from'}'
	AND DATE(cu_invoices.doc_date) < '$in{'date_to'}'
	/* AND cu_invoices_lines.ID_orders='100196' */
	GROUP BY cu_invoices_lines.ID_invoices
	ORDER BY cu_invoices_lines.ID_invoices";
	&print_query($sql);
	my ($sth) = &Do_SQL($sql);
	print qq|<table border="1" style="font-size:10px;" padding="2">
	<tr>
		<td>invoice_type</td>
		<td>ID_invoices_lines</td>
		<td>ID_invoices</td>
		<td>doc_serial</td>
		<td>doc_num</td>
		<td>ID_customers</td>
		<td>Currency</td>
		<td>ID_orders</td>
		<td>ID_creditmemos</td>
		<td>ID_debitmemos</td>
		<td>ID_orders_products</td>
		<td>description</td>
		<td>doc_date</td>
		<td>invoice_net</td>
		<td>Shipping</td>
		<td>total_taxes_transfered</td>
		<td>invoice_total</td>
		<td>TOTAL_SQL</td>
		<td>Cost</td>
	</tr>|;
	while ( my $rec = $sth->fetchrow_hashref()){
		print qq|
		<tr>
			<td>&nbsp;$rec->{'invoice_type'}</td>
			<td>&nbsp;$rec->{'ID_invoices_lines'}</td>
			<td>&nbsp;$rec->{'ID_invoices'}</td>
			<td>&nbsp;$rec->{'doc_serial'}</td>
			<td>&nbsp;$rec->{'doc_num'}</td>
			<td>&nbsp;$rec->{'ID_customers'}</td>
			<td>&nbsp;$rec->{'Currency'}</td>
			<td>&nbsp;$rec->{'ID_orders'}</td>
			<td>&nbsp;$rec->{'ID_creditmemos'}</td>
			<td>&nbsp;$rec->{'ID_debitmemos'}</td>
			<td>&nbsp;$rec->{'ID_orders_products'}</td>
			<td>&nbsp;$rec->{'description'}</td>
			<td>&nbsp;$rec->{'doc_date'}</td>
			<td>&nbsp;$rec->{'invoice_net'}</td>
			<td>&nbsp;$rec->{'Shipping'}</td>
			<td>&nbsp;$rec->{'total_taxes_transfered'}</td>
			<td>&nbsp;$rec->{'invoice_total'}</td>
			<td>&nbsp;$rec->{'TOTAL_SQL'}</td>
			<td>&nbsp;$rec->{'Cost'}</td>
		</tr>|;

		# Se modifican Status a sl_movements
		$sql = "UPDATE sl_movements SET Status='Direksys_Active' WHERE tableused='sl_orders' AND ID_tableused='$rec->{'ID_orders'}' AND Status='Active' AND DATE <= '2014-11-12';";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		$sql = "UPDATE sl_movements SET Status='Direksys_Pending' WHERE tableused='sl_orders' AND ID_tableused='$rec->{'ID_orders'}' AND Status='Pending' AND DATE <= '2014-11-12';";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');

		# Se genera nueva contabilidad para esta factura / orden
		# Se inserta 1 por cada cuenta contable

		$sql = "SELECT ID_orders, Date, ID_salesorigins, Ptype FROM sl_orders WHERE ID_orders='$rec->{'ID_orders'}';";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql);
		my ($id_orders, $date, $id_salesorigins, $ptype) = $sth2->fetchrow();
		
		# Cuentas contables
		my $cta_clientes;
		
		# Internacionales = $cta_clientes = 79;
		# Nacionales = $cta_clientes = 76;
		$cta_clientes = ($rec->{'Currency'} ne 'MX$')? 79 : 76;
		
		my $cta_ventas = 354;
		my $cta_envio = 355;
		my $cta_iva = 264;
		my $cta_iva2 = 265;
		my $cta_costo = 367;
		my $cta_inventario = 137;

		## Se insertan Mov Contables
		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_clientes', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_ventas', '$rec->{'SalePrice'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_envio', '$rec->{'Shipping'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($rec->{'Shipping'} > 0 and $in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_iva', '$rec->{'total_taxes_transfered'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($rec->{'total_taxes_transfered'} > 0 and $in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_costo', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');

		$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
		VALUES (NULL, '$cta_inventario', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Ventas', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');

		##
		## Al final se debe mandar ejecutar &accounting_set_segment($id_orders, $id_salesorigins)
		&accounting_set_segment($id_orders, $id_salesorigins);

		##
		## COBRANZA
		print qq|<H5 style="color:red;">COBRANZA [$rec->{'ID_orders'}]</H5>|;

		$sql = "
		SELECT sl_banks_movements.BankDate
			, sl_banks_movements.Amount
			, sl_banks_movements.AmountCurrency
			, if(ifnull(sl_banks_movements.currency_exchange,1)=0,1,ifnull(sl_banks_movements.currency_exchange,1))currency_exchange
			, sl_banks_movrel.AmountPaid
			, (SELECT ID_accounts FROM sl_accounts INNER JOIN sl_banks ON sl_accounts.Description = sl_banks.`ABA-ACH` WHERE sl_accounts.ID_accategories = '1' AND ID_banks = sl_banks_movements.ID_banks)ID_accounts
			, ROUND(ifnull(sl_banks_movrel.AmountPaid,1) * if(ifnull(sl_banks_movements.currency_exchange,1)=0,1,ifnull(sl_banks_movements.currency_exchange,1)),2)TotalPaid
			, sl_banks_movements.ID_banks
		FROM sl_banks_movements 
		INNER JOIN sl_banks_movrel ON sl_banks_movements.ID_banks_movements=sl_banks_movrel.ID_banks_movements
		LEFT JOIN sl_orders_payments ON sl_orders_payments.ID_orders_payments=sl_banks_movrel.tableid AND sl_banks_movrel.tablename='orders_payments' 
		WHERE sl_orders_payments.ID_orders='$rec->{'ID_orders'}'
		AND sl_banks_movements.Status='Active'
		AND sl_banks_movrel.Status='Active';";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql);
		my ($bankdate, $amount, $amountcurrency, $currency_exchange, $amountpaid, $cta_banco, $totalpaid, $id_banks) = $sth2->fetchrow();

		if ($cta_banco){
			## Se insertan Mov Contables
			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_banco', '$totalpaid', '', '$bankdate', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Cobranza', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_clientes', '$totalpaid', '', '$bankdate', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Cobranza', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			## Calculo de Tasas de IVA
			my $percent_paid;
			my $total_iva;
			if ($rec->{'total_taxes_transfered'} > 0){
				$percent_paid = ($totalpaid * 100) / $rec->{'invoice_total'};
				$total_iva = ($percent_paid * $rec->{'total_taxes_transfered'}) / 100;
				# print "<span style='color:red'>percent_paid = $percent_paid<br />total_iva = $total_iva</span>";

				$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
				VALUES (NULL, '$cta_iva', '$total_iva', '', '$bankdate', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Cobranza', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
				&print_query($sql);
				&Do_SQL($sql) if ($total_iva > 0 and $in{'process'} eq 'commit');

				$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
				VALUES (NULL, '$cta_iva2', '$total_iva', '', '$bankdate', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Cobranza', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
				&print_query($sql);
				&Do_SQL($sql) if ($total_iva > 0 and $in{'process'} eq 'commit');
			}


		}else{
			print "<span style='color:red'>NO hay cuenta contable para el banco: $id_banks </span>";
		}
	

	}
	print qq|</table><hr />|;

	# print "hasta aqui llegamos...";
	# return;
# }

# if ($in{'ndc_cm'} == 1) {

	# NOTAS DE CREDITO
	print qq|<H2 style="color:red;">N O T A S   DE   C R E D I T O -- CREDITMEMOS</H2>|;

	# Recorrer las facturas cu_invoices
	# Extraer su ID_orders o ID_creditmemos
	$doc_date = $in{'doc_date'} if($in{'doc_date'});
	$sql = "
	SELECT 
		cu_invoices.invoice_type
		, cu_invoices_lines.ID_invoices_lines
		, cu_invoices_lines.ID_invoices
		, cu_invoices.ID_customers
		, sl_customers.Currency
		, sl_creditmemos_payments.ID_orders
		, cu_invoices_lines.ID_creditmemos
		, cu_invoices_lines.ID_debitmemos
		, cu_invoices_lines.ID_orders_products
		, cu_invoices_lines.description
		, DATE(cu_invoices.doc_date)doc_date
		, cu_invoices.invoice_net
		, cu_invoices.total_taxes_transfered
		, cu_invoices.invoice_total
		, (cu_invoices.invoice_net+cu_invoices.total_taxes_transfered)TOTAL_SQL
		, sl_creditmemos_products.Cost
		, sl_creditmemos_products.Shipping
		, sl_creditmemos_products.SalePrice
		, sl_creditmemos_products.Type
	FROM cu_invoices INNER JOIN cu_invoices_lines ON cu_invoices.ID_invoices=cu_invoices_lines.ID_invoices
	INNER JOIN sl_creditmemos ON sl_creditmemos.ID_creditmemos=cu_invoices_lines.ID_creditmemos
	LEFT JOIN (
		SELECT 
			sl_creditmemos_products.ID_creditmemos
			, SUM((sl_creditmemos_products.SalePrice*sl_creditmemos_products.Quantity)-sl_creditmemos_products.Discount)SalePrice
			, SUM(sl_creditmemos_products.Cost) Cost
			, SUM(sl_creditmemos_products.Shipping) Shipping
			, IF(MAX(sl_creditmemos_products.ID_products)<500000000,'Devolucion','Servicios') Type
		FROM sl_creditmemos_products
		WHERE sl_creditmemos_products.Status='Active'
		GROUP BY sl_creditmemos_products.ID_creditmemos
	)sl_creditmemos_products ON sl_creditmemos_products.ID_creditmemos=sl_creditmemos.ID_creditmemos
	LEFT JOIN (
		SELECT 
			sl_creditmemos_payments.ID_creditmemos
			, sl_creditmemos_payments.ID_orders
		FROM sl_creditmemos_payments
		GROUP BY sl_creditmemos_payments.ID_creditmemos
	)sl_creditmemos_payments ON sl_creditmemos_payments.ID_creditmemos=sl_creditmemos.ID_creditmemos
	INNER JOIN sl_customers ON sl_customers.ID_customers=cu_invoices.ID_customers
	WHERE cu_invoices.Status='Certified'
	AND sl_creditmemos.Status IN ('Applied')
	AND cu_invoices.invoice_type='egreso'
	AND (cu_invoices_lines.ID_creditmemos > 0 AND cu_invoices_lines.ID_creditmemos IS NOT NULL)
	AND DATE(cu_invoices.doc_date) >= '$in{'date_from'}'
	AND DATE(cu_invoices.doc_date) < '$in{'date_to'}'
	GROUP BY cu_invoices_lines.ID_invoices
	ORDER BY cu_invoices_lines.ID_invoices";
	&print_query($sql);
	my ($sth) = &Do_SQL($sql);
	print qq|<table border="1" style="font-size:10px;" padding="2">
	<tr>
		<td>invoice_type</td>
		<td>ID_invoices_lines</td>
		<td>ID_invoices</td>
		<td>ID_orders</td>
		<td>ID_creditmemos</td>
		<td>ID_debitmemos</td>
		<td>ID_orders_products</td>
		<td>description</td>
		<td>doc_date</td>
		<td>invoice_net</td>
		<td>Shipping</td>
		<td>total_taxes_transfered</td>
		<td>invoice_total</td>
		<td>TOTAL_SQL</td>
		<td>Cost</td>
		<td>Type</td>
	</tr>|;
	while ( my $rec = $sth->fetchrow_hashref()){
		print qq|
		<tr>
			<td>&nbsp;$rec->{'invoice_type'}</td>
			<td>&nbsp;$rec->{'ID_invoices_lines'}</td>
			<td>&nbsp;$rec->{'ID_invoices'}</td>
			<td>&nbsp;$rec->{'ID_orders'}</td>
			<td>&nbsp;$rec->{'ID_creditmemos'}</td>
			<td>&nbsp;$rec->{'ID_debitmemos'}</td>
			<td>&nbsp;$rec->{'ID_orders_products'}</td>
			<td>&nbsp;$rec->{'description'}</td>
			<td>&nbsp;$rec->{'doc_date'}</td>
			<td>&nbsp;$rec->{'invoice_net'}</td>
			<td>&nbsp;$rec->{'Shipping'}</td>
			<td>&nbsp;$rec->{'total_taxes_transfered'}</td>
			<td>&nbsp;$rec->{'invoice_total'}</td>
			<td>&nbsp;$rec->{'TOTAL_SQL'}</td>
			<td>&nbsp;$rec->{'Cost'}</td>
			<td>&nbsp;$rec->{'Type'}</td>
		</tr>|;
		
		# Se modifican Status a sl_movements
		$sql = "UPDATE sl_movements SET Status='Direksys_Active' WHERE tableused='sl_orders' AND ID_tableused='$rec->{'ID_orders'}' AND Status='Active' AND DATE <= '2014-11-12' AND DATE >= '2014-01-01'";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		$sql = "UPDATE sl_movements SET Status='Direksys_Pending' WHERE tableused='sl_orders' AND ID_tableused='$rec->{'ID_orders'}' AND Status='Pending' AND DATE <= '2014-11-12' AND DATE >= '2014-01-01'";
		&print_query($sql);
		&Do_SQL($sql) if ($in{'process'} eq 'commit');
		
		# Se genera nueva contabilidad para esta factura / orden
		# Se inserta 1 por cada cuenta contable

		$sql = "SELECT ID_orders, Date, ID_salesorigins, Ptype FROM sl_orders WHERE ID_orders='$rec->{'ID_orders'}';";
		&print_query($sql);
		my ($sth2) = &Do_SQL($sql);
		my ($id_orders, $date, $id_salesorigins, $ptype) = $sth2->fetchrow();
		
		# Cuentas contables
		my $cta_dev = 359;
		my $cta_dev_iva = 264;

		# Internacionales = $cta_clientes = 79;
		# Nacionales = $cta_clientes = 76;
		$cta_clientes = ($rec->{'Currency'} ne 'MX$')? 79 : 76;
		my $cta_dev_inventario = 137;
		my $cta_dev_costo = 367;
		my $cta_dev_desc = 363;

		## Se insertan Mov Contables
		if ($rec->{'Type'} ne 'Servicios'){
			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev', '$rec->{'SalePrice'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev_iva', '$rec->{'total_taxes_transfered'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($rec->{'Currency'} eq 'MX$' and $rec->{'total_taxes_transfered'} > 0 and $in{'process'} eq 'commit');
			
			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_clientes', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev_inventario', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev_costo', '$rec->{'Cost'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');
		}else{
			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev_desc', '$rec->{'SalePrice'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_dev_iva', '$rec->{'total_taxes_transfered'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($rec->{'Currency'} eq 'MX$' and $rec->{'total_taxes_transfered'} > 0 and $in{'process'} eq 'commit');
			
			$sql = "INSERT INTO sl_movements (ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users) 
			VALUES (NULL, '$cta_clientes', '$rec->{'invoice_total'}', '', '$rec->{'doc_date'}', 'sl_orders', '$rec->{'ID_orders'}', 'cu_invoices', '$rec->{'ID_invoices'}', 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), 1);";
			&print_query($sql);
			&Do_SQL($sql) if ($in{'process'} eq 'commit');

		}

		##
		## Al final se debe mandar ejecutar &accounting_set_segment($id_orders, $id_salesorigins)
		&accounting_set_segment($id_orders, $id_salesorigins);
	}
	print qq|</table><hr />|;
	return;

}



##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
	my (@sys_err) = @_;

	print "\nCGI ERROR\n==========================================\n";
	$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
	$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
	$sys_err[2]	and print "System Message      : $sys_err[2]\n";
	$0			and print "Script Location     : $0\n";
	$]			and print "Perl Version        : $]\n";
	$sid		and print "Session ID          : $sid\n";
	
	exit -1;
}

sub load_settings {
	my ($fname);
	
	if ($in{'e'}) {
		$fname = "../general.e".$in{'e'}.".cfg";
	}else {
		$fname = "../general.ex.cfg";
	}

	## general
	open (CFG, "<$fname") or &cgierr ("Unable to open: $fname,160,$!");
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		if ($td eq "conf") {
			$cfg{$name} = $value;
			next LINE;
		}elsif ($td eq "sys"){
			$sys{$name} = $value;
			next LINE;
		}
	}
	close CFG;

}

sub parse_form {
# --------------------------------------------------------
	my (@pairs, %in);
	my ($buffer, $pair, $name, $value);

	if ($ENV{'REQUEST_METHOD'} eq 'GET') {
		@pairs = split(/&/, $ENV{'QUERY_STRING'});
	}elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
 		@pairs = split(/&/, $buffer);
	}else {
		&cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
	}
	PAIR: foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);

		$name =~ tr/+/ /;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$name = lc($name);

		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		$value =~ s/^\s+//g;
		$value =~ s/\s+$//g;

		#$value =~ s/\r//g;
		$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
		if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		(exists $in{$name}) ?
			($in{$name} .= "|$value") :		# If we have multiple select, then we tack on
			($in{$name}  = $value);			# using the ~~ as a seperator.
	}
	return %in;
}

sub print_query{
	my ($sql) = @_;
	# print qq|<div style="border:solid 1px #666;padding:3px;"><span style="font-size:10px;color:#0099FF;">$sql</span></div>|;
}

sub accounting_set_segment{
#############################################################################
#############################################################################

	my ($id_orders, $id_salesorigins) = @_;

	if($cfg{'accounting_use_segments'}) {

		my ($id_segments);

			(!$id_salesorigins) and ($id_salesorigins = $cfg{'default_origin'});
			my ($sth) = &Do_SQL("SELECT ID_accounts_segments FROM sl_salesorigins WHERE ID_salesorigins = '$id_salesorigins' LIMIT 1;");
			$id_segments = $sth->fetchrow();
		
		if($id_segments) {

			&Do_SQL("SET group_concat_max_len = 204800;");
			my ($stha) = &Do_SQL("SELECT GROUP_CONCAT(ID_accounts) FROM sl_accounts WHERE Segment =  'Yes';");
			my ($id_accounts_grouped) = $stha->fetchrow();

			if($id_accounts_grouped){
				my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_segments = '$id_segments' WHERE ID_tableused = '$id_orders' AND ID_segments = 0 AND ID_accounts IN($id_accounts_grouped) AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0 ;");
			}

		}

	}

}
