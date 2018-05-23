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

# Default la 3 porque este proceso fue diseñado para Mufar
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
	&execute_patch_movements;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_patch_movements
#
#   		This functions reads from several outsourcing callcenters /home/ccname/orders paths. The file inside contains orders created by Listen Up Callcenter to be processed in Direksys. The script validate and create every order and send them to authorize if necessary
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
sub execute_patch_movements{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) :: Correcci&oacute;n de movimientos $process</h4>";
	print '<h3>Limit 200 rows</h3>';

	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	if( !$in{'cta'} ){
		print '<span style="color:red;">El ID de la cuenta es requerido</span>';
		return;
	}
	my $id_account_process = $in{'cta'};

	my ($sthMain) = &Do_SQL("SELECT DISTINCT m.*
							FROM sl_movements m
								INNER JOIN sl_bills b ON m.Amount=b.Amount
							WHERE m.ID_accounts=$id_account_process 
								AND m.Credebit='Credit' 
								AND m.`Status`='Active' 
								AND m.tableused='sl_bills'
							ORDER by m.ID_tableused
							LIMIT 200;");

	my $rows_ok = 0;
	my $rows_no_ok = 0;

	my $finish_trans = '';
	my $msj_ok = '';
	my $msj_error = '';
	if( $in{'process'} eq 'commit' ){
		$finish_trans = 'COMMIT'; 
		$msj_ok = '<span style="color: #209001;">Este registro fu&eacute; procesado correctamente</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO pudo ser procesado</span>';
	} else {
		$finish_trans = 'ROLLBACK'; 
		$msj_ok = '<span style="color: #209001;">Este registro puede ser procesado</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO puede ser procesado</span>';
	}

	my $i = 0;

	&Do_SQL("BEGIN;");
	while ( @row = $sthMain->fetchrow_array() ) {
		++$i;

		$id_tableused = $row[6];
		$effdate = $row[4]; #Fecha de pago
		$amount = $row[2];
		
		#-- Se valida que el registro actual puede ser procesado
		my $valid = &validate_currency_us($id_tableused);

		#-- Se obtiene el id de la cuenta -> (198 ó 202)
		#-- 198 = PROVEEDORES SERVICIOS NACIONALES
		#-- 202 = PROVEEDORES SERVICIOS EXTRANJEROS
		my $id_account = &get_id_account_mov($id_tableused);

		#-- Se obtiene el tipo de cambio en base a la fecha en que se hizo el movimiento
		my $exchange_rate = &get_exchange_rate($effdate);

		#-- Conversión de dolares a pesos
		my $amount_mx = ($amount * $exchange_rate);

		#-- Se obtiene el monto total de la orden, convertido a pesos
		my $total_amount_mx = &get_total_amount_mx($id_tableused, $id_account);

		my $str_sth_upd1 = '';
		my $str_sth_upd2 = '';
		my $result_upd_dif = '';

		my $sum_movs = 0;

		if( $valid == 1 ){
			#-- Se corrige el monto incorrecto(en dls) de ambos movientos(ID_account $id_account_process y ID_account 198 ó 202)
			$str_sth_upd1 = "UPDATE sl_movements m
									SET m.Amount=$amount_mx
								WHERE m.ID_accounts=$id_account AND m.tableused='sl_bills' AND m.Credebit='Debit' AND m.`Status`='Active'
									AND m.EffDate='$effdate' AND m.Amount=$amount;";
			$str_sth_upd2 = "UPDATE sl_movements m
									SET m.Amount=$amount_mx
								WHERE m.ID_accounts=$id_account_process AND m.tableused='sl_bills' AND m.Credebit='Credit' AND m.`Status`='Active'
									AND m.EffDate='$effdate' AND m.Amount=$amount;";
			&Do_SQL($str_sth_upd1);
			&Do_SQL($str_sth_upd2);

			#-- Se obtiene la sumatoria de los movimientos con cuenta $id_account
			$sum_movs = &get_sum_movements($id_tableused, $id_account);

			#-- Se hace la resta del monto total($total_amount_mx), menos la sumatoria obtenida($sum_movs)
			my $dif_amount = $total_amount_mx - $sum_movs;

			$result_upd_dif = &upd_dif_movements($id_tableused, $id_account, $dif_amount);

			$msj_valid = $msj_ok;
			++$rows_ok;
		} else { 
			$msj_valid = $msj_error;
			++$rows_no_ok;
		}
		
		print '<hr />';
		print '<span style="">Registro: '.$i.'</span><br />';
		print '<span style="font-weight: bold;">ID_tableused:</span> '.$id_tableused.'<br />';
		print '<span style="font-weight: bold;">ID_accounts:</span> '.$id_account.'<br />';
		print '<span style="font-weight: bold;">EffDate:</span> '.$effdate.'<br />';
		print '<span style="font-weight: bold;">Exgange rate:</span> '.$exchange_rate.'<br />';
		print '<span style="font-weight: bold;">Conversion:</span> '.$amount.' x '.$exchange_rate.' = $ '.$amount_mx.'<br />';
		print '<span style="font-weight: bold;">Total Amount Bills:</span> '.$total_amount_mx.'<br />';
		print '<span style="font-weight: bold;">Corrigiendo el monto de la cuenta '.$id_account.':</span> <span style="white-space: nowrap;">'.$str_sth_upd1.'</span><br />';
		print '<span style="font-weight: bold;">Corrigiendo el monto de la cuenta '.$id_account_process.':</span> <span style="white-space: nowrap;">'.$str_sth_upd2.'</span><br />';
		print $result_upd_dif;
		print $msj_valid;
	}
	&Do_SQL($finish_trans);

	print '<br /><br /><hr /><hr />';
	print '<span style="font-weight: bold;">Registros Correctos para procesar:</span> <span style="color: #209001;">'.$rows_ok.'</span><br />';
	print '<span style="font-weight: bold;">Registros Con errores:</span> <span style="color: #ff0000;">'.$rows_no_ok.'</span><br />';
	print '<span style="font-weight: bold;">Total de Registros:</span> <span style="color: #0000ff;">'.$i.'</span>';
	print '<hr />';
}

sub get_id_account_mov{
	#-- Recepción de parámetros
	my ($id_tableused) = @_;
	my ($sth) = &Do_SQL("SELECT m.ID_accounts
						FROM sl_movements m
						WHERE m.ID_tableused=$id_tableused 
							AND m.tableused='sl_bills' 
							AND m.ID_accounts In(198,202)
						LIMIT 1;");
	return $sth->fetchrow_array();
}

sub get_exchange_rate{
	my ($date) = @_;
	my ($sth) = &Do_SQL("SELECT e.exchange_rate 
						FROM sl_exchangerates e 
						WHERE e.Date_exchange_rate='$date';");
	return $sth->fetchrow_array();
}

sub get_total_amount_mx{
	#-- Recepción de parámetros
	my ($id_tableused, $id_account) = @_;
	my ($sth) = &Do_SQL("SELECT m.Amount 
						FROM sl_movements m
						WHERE m.ID_tableused=$id_tableused 
							AND m.ID_accounts=$id_account
							AND m.tableused='sl_bills' 
							AND m.`Status`='Active' 
							AND (m.Reference='deductible' OR m.Reference='no')
							AND m.Credebit='Credit';");
	my $amount = $sth->fetchrow_array();
	if( $amount ){
		return $amount;
	} else {
		return -1;
	}
}

#Valida que el monto del tipo de cambio no sea 1, 0 o NULL
sub validate_currency_us{
	#-- Recepción de parámetros
	my ($id_tableused) = @_;
	my ($sth) = &Do_SQL("SELECT b.Currency, b.currency_exchange
						FROM sl_bills b
						Where b.ID_bills=$id_tableused;");
	my ($currency, $currency_exchange) = $sth->fetchrow_array();
	if( $currency eq 'US$' && $currency_exchange > 1 ){
		return 1;
	} else {
		return -1;
	}
}

#Obtiene la sumatoria de todos los movimientos ($id_tableused = 198 ó 202)
#excepto los que coinciden en el monto de la Utilidad o Pérdida cambiaria(583 ó 587)
sub get_sum_movements{
	#-- Recepción de parámetros
	my ($id_tableused, $id_account) = @_;
	my ($sth) = &Do_SQL("SELECT SUM(m.Amount) AS suma 
						FROM sl_movements m
						WHERE m.ID_tableused=$id_tableused 
							AND m.ID_accounts=$id_account
							AND (m.Reference<>'deductible' AND m.Reference<>'no')
							AND m.`Status`='Active'
							AND (m.Amount NOT IN (Select xm.Amount 
													From sl_movements xm 
													Where xm.ID_tableused=$id_tableused 
														And xm.ID_accounts In(583, 587) 
														And xm.`Status`='Active'
												)
								);");
	return $sth->fetchrow_array();
}

#Actualiza los registros de las cuentas de utilidad o pérdida cambiaria.
sub upd_dif_movements{
	#-- Recepción de parámetros
	my ($id_tableused, $id_account, $dif_amount) = @_;
	#-- Se obtiene la cantidad calculada anteriormente con los montos incorrectos y el ID_accounts
	#-- que también será corregido
	my ($sth) = &Do_SQL("SELECT m.Amount, m.ID_accounts 
						FROM sl_movements m
						WHERE m.ID_tableused=$id_tableused 
							AND m.tableused='sl_bills'
							AND m.ID_accounts IN(583, 587)
							AND m.`Status`='Active';");
	my ($dif_amount_obt, $id_account_obt) = $sth->fetchrow_array();

	my $new_credebit_a = ''; #-- 198 ó 202
	my $id_new_account = 0;
	my $new_credebit_na = ''; #-- 583 ó 587
	
	my $str_result = '';
	my $str_sth_upd1 = '';
	my $str_sth_upd2 = '';
	if( $dif_amount_obt && $id_account_obt ){
		if( $dif_amount > 0 ){			
			$new_credebit_a = 'Debit';
			$id_new_account = 583;
			$new_credebit_na = 'Credit';
			
			#-- Actualizando los datos de la cuenta 198 ó 202
			$str_sth_upd1 = "UPDATE sl_movements m
								SET m.Amount=$dif_amount, m.Credebit='$new_credebit_a'
							WHERE m.ID_tableused=$id_tableused 
								AND m.tableused='sl_bills' 
								AND m.ID_accounts=$id_account 
								AND m.Amount=$dif_amount_obt 
								AND m.`Status`='Active';";
			&Do_SQL($str_sth_upd1);
			#-- Actualizando los datos de la cuenta 583 ó 587
			$str_sth_upd2 = "UPDATE sl_movements m
								SET m.Amount=$dif_amount, m.ID_accounts=$id_new_account, m.Credebit='$new_credebit_na'
							WHERE m.ID_tableused=$id_tableused 
								AND m.tableused='sl_bills' 
								AND m.ID_accounts=$id_account_obt
								AND m.Amount=$dif_amount_obt 
								AND m.`Status`='Active';";
			&Do_SQL($str_sth_upd2);
			$str_result = '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida Camb. [Cuenta '.$id_account.']:</span> <span style="white-space: nowrap;">'.$str_sth_upd1.'</span><br />';
			$str_result .= '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida Camb. [Cuenta '.$id_account_obt.']:</span> <span style="white-space: nowrap;">'.$str_sth_upd2.'</span><br />';
		} elsif( $dif_amount < 0 ){
			$new_credebit_a = 'Credit';
			$id_new_account = 587;
			$new_credebit_na = 'Debit';
			
			$dif_amount = abs($dif_amount);
			#-- Actualizando los datos de la cuenta 198 ó 202
			$str_sth_upd1 = "UPDATE sl_movements m
								SET m.Amount=$dif_amount, m.Credebit='$new_credebit_a'
							WHERE m.ID_tableused=$id_tableused 
								AND m.tableused='sl_bills' 
								AND m.ID_accounts=$id_account 
								AND m.Amount=$dif_amount_obt 
								AND m.`Status`='Active';";
			&Do_SQL($str_sth_upd1);
			#-- Actualizando los datos de la cuenta 583 ó 587
			$str_sth_upd2 = "UPDATE sl_movements m
								SET m.Amount=$dif_amount, m.ID_accounts=$id_new_account, m.Credebit='$new_credebit_na'
							WHERE m.ID_tableused=$id_tableused 
								AND m.tableused='sl_bills' 
								AND m.ID_accounts=$id_account_obt
								AND m.Amount=$dif_amount_obt 
								AND m.`Status`='Active';";
			&Do_SQL($str_sth_upd2);
			$str_result = '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida Camb. [Cuenta '.$id_account.']:</span> <span style="white-space: nowrap;">'.$str_sth_upd1.'</span><br />';
			$str_result .= '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida Camb. [Cuenta '.$id_account_obt.']:</span> <span style="white-space: nowrap;">'.$str_sth_upd2.'</span><br />';
		} else {
			$str_result = '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida cambiaria:</span> No existen utilidades ni pérdidas cambiaria<br />';
		}
	} else {
		$str_result = '<span style="font-weight: bold;">Corrigiendo los montos de Utilidad o P&eacute;rdida cambiaria:</span> No existen los registros<br />';
	}

	return $str_result;
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