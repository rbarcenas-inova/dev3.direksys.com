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
use MIME::Base64;
use File::Slurp;

# Default la 11 porque este proceso fue diseñado para Importaciones
#local(%in) = &parse_form;
$in{'e'} = 11;
$in{'process'} = 'test';

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
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
	&execute_create_users_vendors;
	&disconnect_db;
}


#################################################################
#################################################################
#	Function: execute_create_users_vendors
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
sub execute_create_users_vendors{

	print "Content-type: text/html\n\n";
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	&load_settings;

	my $process = ($in{'process'} ne 'commit') ? qq|<span style="color: gray; padding:5px;">TESTING</span>| : qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Usuarios para Proveedores <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';

	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';

	my $debug = ($in{'process'} ne 'commit') ? 1 : 0;
	my $debug_mail = 'gquirino@inovaus.com';
	my $toprint = '';
	my $logs = '';	
	my $send_email = 0;
	my $filename = 'GuiaProveedoresInova.pdf';

	print '<h5>DEBUG = '.$debug.'</h5>';

	my $sthMain = &Do_SQL("SELECT ID_vendors_contacts, ID_vendors, UPPER(FirstName)FirstName, UPPER(LastName1)LastName1, UPPER(LastName2)LastName2, LOWER(Email)Email
							FROM sl_vendors_contacts
							WHERE DATE>='2017-04-10' AND `Status`='Active' AND ID_admin_users=1;");

	$toprint = '<table style="width: 100%;" border=1>';
	$toprint .= '<tr>';
	$toprint .= '<td>ID_vendors</td>';
	$toprint .= '<td>ID_vendors_contacts</td>';
	$toprint .= '<td>FirstName</td>';
	$toprint .= '<td>LastName1</td>';
	$toprint .= '<td>LastName2</td>';
	$toprint .= '<td>Email</td>';
	$toprint .= '<td>Logs</td>';
	$toprint .= '</tr>';

	&Do_SQL("START TRANSACTION;");
	while ( my $contacts = $sthMain->fetchrow_hashref() ) {
		
		$toprint .= '<tr>';
		$toprint .= '<td>'.$contacts->{'ID_vendors'}.'</td>';
		$toprint .= '<td>'.$contacts->{'ID_vendors_contacts'}.'</td>';
		$toprint .= '<td>'.$contacts->{'FirstName'}.'</td>';
		$toprint .= '<td>'.$contacts->{'LastName1'}.'</td>';
		$toprint .= '<td>'.$contacts->{'LastName2'}.'</td>';
		$toprint .= '<td>'.$contacts->{'Email'}.'</td>';

		$logs = '================================'."\n";

		### Nuevo usuario y password generado
		my $new_pswd = &gen_rand_pswd();
		my $this_username = 'vendor'.$contacts->{'ID_vendors_contacts'};

		### -----------------------------------------------
		### Se crea el nuevo usuario de Direksys
		### -----------------------------------------------
		my $sth_chk = &Do_SQL("SELECT ID_admin_users FROM admin_users WHERE Email = '".$contacts->{'Email'}."' LIMIT 1;");
		my $exists_user = $sth_chk->fetchrow();		
		my $this_new_id = 0;
		if( int($exists_user) == 0 ){
			my $this_sql = &sql_create_user($contacts->{'FirstName'}, $contacts->{'LastName1'}, $contacts->{'LastName2'}, $contacts->{'Email'}, $this_username, $new_pswd);
			my $usr = &Do_SQL($this_sql);
			$this_new_id = $usr->{'mysql_insertid'};			

			$logs .= '<br />'.$this_sql."\n";
			$logs .= '<br />********* Usuario Direksys creado: '.$this_new_id."\n";
		} else {
			$this_new_id = $exists_user;
			$new_pswd = &load_name('admin_users', 'ID_admin_users', $exists_user, 'tempPasswd');

			$logs .= '<br />********* Usuario Direksys existente: '.$this_new_id."\n";
		}
		### -----------------------------------------------
		### Si el usuario de Direksys se creó correctamente, se crea el usuario del portal
		### -----------------------------------------------
		if( $this_new_id > 0 ){
			my $usrv_chk = &Do_SQL("SELECT id_admin_users_vendors 
									FROM admin_users_vendors 
									WHERE Email = '".$contacts->{'Email'}."' 
										AND ID_vendors = ".$contacts->{'ID_vendors'}."
									;");
			my $exists_user_vendor = $usrv_chk->fetchrow();
			if( int($exists_user_vendor) == 0 ){
				my $this_sql = &sql_create_user_vendor($this_new_id, $contacts->{'ID_vendors'}, $contacts->{'Email'}, $new_pswd);
				my $uvendor = &Do_SQL($this_sql);

				$logs .= '<br />'.$this_sql."\n";
				$logs .= '<br />********* Usuario Proveedor creado: '.$uvendor->{'mysql_insertid'}."\n";
			} else {
				$logs .= '<br />********* Usuario Proveedor existente: '.$exists_user_vendor."\n";
			}
			
			### Se envia el email
			if( $send_email == 1 and int($exists_user) == 0 ){
				my $text_file = read_file($filename);
				my $file_encoded = encode_base64($text_file);

				my %attachments = (
			        'PortalProveedoresInova-GuiaRapida.pdf' => $file_encoded
			    );

				my $from_email = 'no-reply@inova.com.mx';
				my $to_email = $contacts->{'Email'};
				#my $to_email = $debug_mail;
				my $subject = 'Cuenta de acceso al portal de proveedores Inova';
				my $body = 'Estimado '.$contacts->{'FirstName'}.', este mensaje es para notificarle que se le ha generado una cuenta de acceso al portal de proveedores de Inova, la cual se muestra a continuación:';
				$body .= '<br />Sitio Web: https://proveedor.inova.com.mx';
				$body .= '<br />Nombre de usuario: '.$contacts->{'Email'};
				$body .= '<br />Contraseña: '.$new_pswd;
				$body .= '<br /><br />Por seguridad, es importante que genere su propia su contraseña una vez haya ingresado al portal.';
				$body = decode('utf-8', $body);

				### Se envía el correo de notificacion
				$rslt_mail = &send_mandrillapp_email_attachment($from_email, $to_email, $subject, $body, "textmail", \%attachments);
				$rslt_mail = &send_mandrillapp_email_attachment($from_email, $debug_mail, $subject, $body, 'none', 'none');

				$logs .= '<br /> Email enviado a '.$to_email."\n";
			}

		}
		$logs .= '<br />================================'."\n";

		### -----------------------------------------------
		### Se recorren las demás BDs para crear los usuarios
		### -----------------------------------------------
		EMP:for($e = 1; $e <= $cfg{'max_e'}; $e++) {
			next EMP if( $in{'e'} == $e );
			next EMP if( $e != 2 and $e != 3 and $e != 4 and $e != 11 );
			 
			my %tmp_cfg;
			if(open (my $cfg, "<", $home_dir.'/general.e'.$e.'.cfg')) {
				LINE: while (<$cfg>) {
					(/^#/)      and next LINE;
					(/^\s*$/)   and next LINE;
					$line = $_;
					$line =~ s/\n|\r//g;
					my ($td,$name,$value) = split (/\||\=/, $line,3);
					if ($td eq "conf" and $name =~ /^dbi_/) {
						$tmp_cfg{$name} = $value;
					}
				}
				close $cfg;

				$logs .= '<br /> - - - - - > e'.$e."\n";
				### Conexion a la nueva BD
				&connect_db_w($tmp_cfg{'dbi_db'},$tmp_cfg{'dbi_host'},$tmp_cfg{'dbi_user'},$tmp_cfg{'dbi_pw'});
				$db = $tmp_cfg{'dbi_db'};

				my $sth_chk = &Do_SQL("SELECT ID_vendors_contacts, ID_vendors, admin_users.ID_admin_users 
										FROM direksys2_e".$e.".sl_vendors_contacts 
											LEFT JOIN admin_users ON sl_vendors_contacts.Email = admin_users.Email 
										WHERE sl_vendors_contacts.Email = '".$contacts->{'Email'}."'
											AND sl_vendors_contacts.`Status` = 'Active'
										;", 1);
				my $id_admin_users = 0;
				while( my $contact_ex = $sth_chk->fetchrow_hashref() ){
					### El email existe en otra empresa
					if( int($contact_ex->{'ID_vendors_contacts'}) > 0 ){
						$logs .= '<br />Existe Email en e'.$e.' :: ID_vendors='.$contact_ex->{'ID_vendors'}."\n";
						### Aún no existe usuario Direksys
						if( !$contact_ex->{'ID_admin_users'} and $id_admin_users == 0 ){
							$logs .= '<br /> &nbsp;&nbsp;&nbsp;==> No-Direksys'."\n";

							my $this_username = 'vendor'.$contact_ex->{'ID_vendors_contacts'};							
							
							my $this_sql = &sql_create_user($contacts->{'FirstName'}, $contacts->{'LastName1'}, $contacts->{'LastName2'}, $contacts->{'Email'}, $this_username, $new_pswd);
							my $usr = &Do_SQL($this_sql, 1);							
							$id_admin_users = $usr->{'mysql_insertid'};
							
							&Do_SQL("DELETE FROM admin_users WHERE ID_admin_users = ".$id_admin_users.";") if( $debug == 1 );

							$logs .= '<br />'.$this_sql."\n";
							$logs .= '<br />User-Direksys Creado :: '.$id_admin_users."\n";
						} else {
							$id_admin_users = $contact_ex->{'ID_admin_users'};

							$logs .= '<br />User-Direksys existente: '.$contact_ex->{'ID_admin_users'}."\n";
						}

						### Se crea el user-vendor
						if( $id_admin_users > 0 ){
							my $usrv_chk = &Do_SQL("SELECT id_admin_users_vendors 
													FROM admin_users_vendors 
													WHERE Email = '".$contacts->{'Email'}."' 
														AND ID_vendors = ".$contacts->{'ID_vendors'}."
													;", 1);
							my $exists_user_vendor = $usrv_chk->fetchrow();
							if( int($exists_user_vendor) == 0 ){
								my $this_sql = &sql_create_user_vendor($id_admin_users, $contact_ex->{'ID_vendors'}, $contacts->{'Email'}, $new_pswd);
								my $uvendor = &Do_SQL($this_sql, 1);
								my $this_id_uvendor = $uvendor->{'mysql_insertid'};
								
								&Do_SQL("DELETE FROM admin_users_vendors WHERE id_admin_users_vendors = ".$this_id_uvendor.";") if( $debug == 1 );

								$logs .= '<br />'.$this_sql."\n";
								$logs .= '<br />User-Vendor Creado :: '.$this_id_uvendor."\n";

							} else {
								$logs .= '<br />User-Vendor existente: '.$exists_user_vendor."\n";
							}
						}
					}
				}## fin del while( my $contact_ex = $sth_chk->fetchrow_hashref() )

			}

		}
		### -----------------------------------------------		

		$toprint .= '<td>'.$logs.'</td>';
		$toprint .= '</tr>';
	}
	$toprint .= '</table>';

	if( $debug == 1 ){
		&Do_SQL("ROLLBACK;");
	} else {
		&Do_SQL("COMMIT;");
	}

	# File
	my $file_path = '../../../files/e'.$in{'e'}.'/';
	my $file_name = 'create_users_vendors_logs.txt';

	open(logs_fix,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
	print logs_fix $toprint;
	close(logs_fix);

	print $toprint;



	return;
	####################################################################################################

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

sub sql_create_user{
	my ($firstname, $lastname1, $lastname2, $email, $username, $password) = @_;

	my $sql = "INSERT INTO admin_users SET 
					  FirstName = '".$firstname."'
					, LastName = '".$lastname1."'
					, MiddleName ='".$lastname2."'
					, Email = '".$email."'
					, Username = '".$username."'
					, tempPasswd = '".$password."'
					, `Password` = sha1('".$password."')
					, change_pass = 'No'
					, pref_table_width = 100
					, expiration = '0000-00-00'
					, IPFilter = '192.168.0.0'
					, application = 'admin'
					, MultiApp = 'admin'
					, user_type = 'Vendors'
					, `Status` = 'Inactive'
					, `Date` = CURDATE()
					, `Time` = CURTIME()
					, CreatedBy = 1
					;";

	return $sql;
}

sub sql_create_user_vendor{
	my ($id_admin_users, $id_vendors, $email, $password) = @_;

	my $sql = "INSERT INTO admin_users_vendors SET 
					id_admin_users = ".$id_admin_users."
					, id_vendors = ".$id_vendors."
					, email = '".$email."'
					, password = sha1('".$password."')
					, `status` = 'Active';";

	return $sql;
}

sub gen_rand_pswd {

	my $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890';
	my $pswd_lgth = 10;
	my $pswd = '';

	for( my $i=0; $i <= $pswd_lgth; $i++ ){
		my $rand_pos = int( rand( length($chars) ) );
		$pswd .= substr($chars, $rand_pos, 1);
	}

	return $pswd;

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