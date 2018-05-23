#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Copy;
use Encode;
use Date::Calc qw();

# Default la 11 porque este proceso fue diseñado para Importaciones
local(%in) = &parse_form;

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
#	Created by: Ing. Gilberto Quirino
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
	&execute_fix_orders_payments;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_fix_orders_payments
#
#
#	Created by: Gilberto Quirino
#
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
sub execute_fix_orders_payments{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">TESTING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	#my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Fix de Ordenes: Products-Payments <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	my $q_anio = '';
	if( $in{'a'} ){
		if( $in{'a'} == 2012 or $in{'a'} == 2013 or $in{'a'} == 2014 or $in{'a'} == 2015 ){
			$q_anio = " AND YEAR(sl_orders.Date)=".$in{'a'};
		}
	}

	my $logs = '';
	my $finish_trans = '';
	my $msj_ok = '';
	my $msj_error = '';
	my $total_process = 0;

	if( $in{'process'} eq 'commit' ){
		$finish_trans = 'COMMIT;'; 
		$msj_ok = '<span style="color: #209001;">Este registro fu&eacute; procesado correctamente</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO pudo ser procesado</span>';
	} else {
		$finish_trans = 'ROLLBACK;'; 
		$msj_ok = '<span style="color: #209001;">Este registro puede ser procesado</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO puede ser procesado</span>';
	}
	
	print '<table border=1 style="border-spacing: 0; width: 90%;">';	

	my ($sthMain) = &Do_SQL("SELECT sl_orders.ID_orders
							FROM sl_orders 
								INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
							WHERE LENGTH(sl_orders_products.Related_ID_products) < 5 
								AND sl_orders_products.`Status`='Active' 
								AND sl_orders.`Status` = 'Shipped'
								".$q_anio."
							GROUP BY sl_orders.ID_orders
							ORDER BY sl_orders.ID_orders;");
	my $i = 0;
	&Do_SQL("BEGIN;");	
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		my $id_order = $refMain->{'ID_orders'};
		
		
		print '<tr>';
		print '	<td style="font-size: 14pt; font-weight: bold;">ID_orders: '.$id_order.'</td>';
		print '</tr>';

		$logs .= "----------------------------------------------------------------------------\n";
		$logs .= "--- Inicia el proceso de la orden: $id_order\n";
		$logs .= "----------------------------------------------------------------------------\n";
		## Se obtienen los IDs de los productos(CM) que se van a cancelar
		my $sthProd = &Do_SQL("SELECT GROUP_CONCAT(ID_orders_products)
		 						FROM sl_orders_products
			 					WHERE ID_orders=".$id_order." AND ID_products >= 800000000 AND `Status`='Active' 
			 					GROUP BY ID_orders;");
		my $ids_products = $sthProd->fetchrow();
		my $qry_prod = ( $ids_products ) ? "UPDATE sl_orders_products SET `Status`='Inactive' WHERE Id_orders=$id_order AND ID_orders_products IN($ids_products);\n" : "No hubo UPDATE en orders_products";
		$logs .= "Se cancelan los productos: $ids_products\n";

		## Se obtienen los IDs de los pagos(payments) que se van a cancelar
		## Parte 1
		my $sthPay = &Do_SQL("SELECT GROUP_CONCAT(ID_orders_payments)
		 					FROM sl_orders_payments
		 					WHERE ID_orders=".$id_order." AND Reason='Refund' AND Amount < 0 AND (`Status`='Approved' OR `Status`='Credit')
		 					GROUP BY ID_orders;");
		my $ids_payments = $sthPay->fetchrow();
		my $qry_pay1 = '';
		my $qry_xtra = '';
		if( $ids_payments ){
			$qry_pay1 = "UPDATE sl_orders_payments SET `Status`='Cancelled' WHERE Id_orders=$id_order AND ID_orders_payments IN($ids_payments);";
			$qry_xtra = "AND ID_orders_payments NOT IN($ids_payments)";
		}else{
			$qry_pay1 =  "No hubo UPDATE 1 en orders_payments";
			$qry_xtra = "";
		}
		$logs .= "Se cancelan los pagos: $ids_payments\n";
		## Parte 2
		my $sthPay = &Do_SQL("SELECT GROUP_CONCAT(ID_orders_payments)
							FROM sl_orders_payments 
							WHERE ID_orders=".$id_order." AND Reason='Refund' AND (AuthCode='' OR AuthCode IS NULL) AND Amount>0 $qry_xtra
							GROUP BY ID_orders;");
		my $ids_payments = $sthPay->fetchrow();
		my $qry_pay2 = ( $ids_payments ) ? "UPDATE sl_orders_payments SET `Status`='Cancelled' WHERE Id_orders=$id_order AND ID_orders_payments IN($ids_payments);" : "No hubo UPDATE 2 en orders_payments";
		$logs .= "Se cancelan los pagos: $ids_payments\n";

		## Se obtienen los IDs de los CreditMemos que se van a insertar
		my $sthCM = &Do_SQL("SELECT GROUP_CONCAT(sl_creditmemos.ID_creditmemos)
		 					FROM sl_creditmemos
								INNER JOIN sl_creditmemos_payments USING(ID_creditmemos)
							WHERE sl_creditmemos_payments.ID_orders=".$id_order." 
								AND (sl_creditmemos.`Status` = 'Applied' OR sl_creditmemos.`Status` = 'Approved') 
								AND sl_creditmemos_payments.Amount > 0
								AND sl_creditmemos.ID_creditmemos NOT IN(Select sl_orders_payments.AuthCode From sl_orders_payments Where sl_orders_payments.ID_orders=".$id_order.")
							GROUP BY sl_creditmemos_payments.ID_orders;");
		my $ids_cm = $sthCM->fetchrow();
		my $qry_cm = ( $ids_cm ) ? "INSERT INTO sl_orders_payments(`ID_orders`, `Amount`, `Reason`, `Paymentdate`, `AuthCode`, `Captured`, `CapDate`, `PostedDate`, `Status`, `Date`, `Time`, `ID_admin_users`)
									SELECT $id_order, sl_creditmemos_payments.Amount, 'Refund', sl_creditmemos_payments.Date, sl_creditmemos.ID_creditmemos, 'Yes', CURDATE(), CURDATE(), 'Approved', CURDATE(), CURTIME(), 1111
									FROM sl_creditmemos
										INNER JOIN sl_creditmemos_payments USING(ID_creditmemos)
									WHERE sl_creditmemos.ID_creditmemos IN($ids_cm)
										AND sl_creditmemos_payments.ID_orders=".$id_order.";" 
								 : "No hubo INSERT de CMs en orders_payments";
		$logs .= "Se insertan los CreditMemos: $ids_cm\n";

		##----------------------------
		## Se ejecutan los query
		##----------------------------
		&Do_SQL($qry_prod)	if( $qry_prod !~ /No hubo/ );
		&Do_SQL($qry_pay1)	if( $qry_pay1 !~ /No hubo/ );
		&Do_SQL($qry_pay2)	if( $qry_pay2 !~ /No hubo/ );
		&Do_SQL($qry_cm)	if( $qry_cm !~ /No hubo/ );
		##----------------------------

		## Se obtienen los montos de los productos y los pagos
		my $sthAmt = &Do_SQL("SELECT IFNULL(SUM(SalePrice+Tax-Discount), 0)
							  FROM sl_orders_products
							  WHERE id_orders=$id_order AND `Status`='Active';");
		my $amt_prod = $sthAmt->fetchrow();

		my $sthAmt = &Do_SQL("SELECT IFNULL(SUM(Amount), 0)
							  FROM sl_orders_payments
							  WHERE id_orders=$id_order AND (`Status`='Approved' OR `Status`='Credit');");
		my $amt_pay = $sthAmt->fetchrow();
		my $qry_dif = "";
		if( round($amt_prod-$amt_pay, 2) >= 0.01 ){
			## Se inserta el pago pendiente
			$qry_dif = "INSERT INTO sl_orders_payments(`ID_orders`, `Amount`, `Paymentdate`, `Captured`, `CapDate`, `PostedDate`, `Status`, `Date`, `Time`, `ID_admin_users`) 
						VALUES ($id_order, ".round($amt_prod-$amt_pay, 3).", '2015-04-01', NULL, NULL, '2015-04-01', 'Approved', CURDATE(), CURTIME(), 1111);";

		}
		my $qry_grp_pays = "";
		if($qry_dif ne ''){
			my $py_add = &Do_SQL($qry_dif);
			my ($new_id) = $py_add->{'mysql_insertid'};
			$logs .= "Se insertan el pago pendiente: ".$new_id."\n";

			## Se reagrupan los pagos pendientes en uno solo en caso de existan varios
			my $sthPendPay = &Do_SQL("SELECT COUNT(*), GROUP_CONCAT(ID_orders_payments), MAX(ID_orders_payments), SUM(Amount)
										FROM sl_orders_payments
										WHERE ID_orders=".$id_order." AND `Status`='Approved' AND AuthCode='' AND (Captured='' OR Captured IS NULL) AND Reason='Sale' AND (CapDate='0000-00-00' OR CapDate IS NULL);");
			my($cant, $ids_pend_pay, $last_id_pay, $amt_pend_pay) = $sthPendPay->fetchrow_array();
			if( $cant > 1 ){
				$logs .= "Se reagrupan los pagos ".$ids_pend_pay." en ".$last_id_pay."\n";
				## Se cancelan todos los pagos pendiente excepto el ultimo insertado
				my $qry = "UPDATE sl_orders_payments 
						   	SET `Status`='Cancelled' 
						   WHERE ID_orders=".$id_order." AND ID_orders_payments!=".$last_id_pay." AND `Status`='Approved' AND AuthCode='' AND (Captured='' OR Captured IS NULL) AND Reason='Sale' AND (CapDate='0000-00-00' OR CapDate IS NULL);";
				&Do_SQL($qry);
				$qry_grp_pays = $qry."<br />";
				## Se actualiza el monto en el ultimo pago pendiente insertado
				my $qry = "UPDATE sl_orders_payments
								SET Amount=".$amt_pend_pay." 
							WHERE ID_orders_payments=".$last_id_pay.";";
				&Do_SQL($qry);
				$qry_grp_pays .= $qry;
			}else{
				$qry_grp_pays = "<br />Sin agrupacion de pagos pendientes";
			}
		}

		print '<tr>';
		print '<td>'.$qry_prod.'<br />'.$qry_pay1.'<br />'.$qry_pay2.'<br />'.$qry_cm.'<br />'.$qry_dif.$qry_grp_pays.'</td>';
		print '</tr>';

		++$total_process;

	}
	&Do_SQL($finish_trans);
	if( $in{'process'} ne 'commit' ){
		# Date
		my ($y, $m, $d) = Date::Calc::Today();
		my ($h, $n, $s) = Date::Calc::Now();
		my $date = sprintf('%02d%02d%02d%02d%02d', $y, $m, $d, $h, $n);
		# File
		my $file_path = '../../../files/e'.$in{'e'}.'/';
		my $file_name = 'fix_orders_payments_log_'.$date.'.txt';

		open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
		print logs_fix $logs;
		close(logs_fix);
	}

	print '</table>';

	print '<br /><br /><hr /><hr />';
	print '<span style="font-weight: bold;">Ordenes procesadas: </span> <span style="color: #209001;">'.$total_process.'</span><br />';
	#print '<span style="font-weight: bold;">Registros Con errores:</span> <span style="color: #ff0000;">'.$rows_no_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Total de Registros:</span> <span style="color: #0000ff;">'.$i.'</span>';
	print '<hr />';
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