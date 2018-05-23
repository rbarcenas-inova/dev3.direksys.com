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
	&execute_fix_purchaseorders;
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
sub execute_fix_purchaseorders{
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color: gray; padding:5px;">ANALYZING</span>|:qq|<span style="color: red; font-weight: bold; padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print '<h4 style="border-bottom: 3px double gray;">DIREKSYS '.$cfg{'app_title'}.' e('.$in{'e'}.') :: Correcci&oacute;n de Devoluciones <span style="position: relative; float: right;">Process: '.$process.'</span></h4>';
	
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}

	#Id user
	my $id_user = ( $in{'u'} ) ? $in{'u'} : '3000'; 
		
	#my $rows_ok = 0;
	#my $rows_no_ok = 0;

	my $finish_trans = '';
	#my $msj_ok = '';
	#my $msj_error = '';

	if( $in{'process'} eq 'commit' ){
		$finish_trans = 'COMMIT'; 
		$msj_ok = '<span style="color: #209001;">Este registro fu&eacute; procesado correctamente</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO pudo ser procesado</span>';
	} else {
		$finish_trans = 'ROLLBACK'; 
		$msj_ok = '<span style="color: #209001;">Este registro puede ser procesado</span>';
		$msj_error = '<span style="color: #ff0000;">Este registro NO puede ser procesado</span>';
	}

	my $where_vendor = "";
	if( $in{'e'} == 2 ){
		$where_vendor = "AND po.ID_vendors IN(686, 569, 207)";
	}elsif( $in{'e'} == 3 ){
		$where_vendor = "AND po.ID_vendors IN(569, 301, 207)";
	}elsif( $in{'e'} == 4 ){
		$where_vendor = "AND po.ID_vendors IN(688, 569, 301)";
	}elsif( $in{'e'} == 11 ){
		$where_vendor = "AND po.ID_vendors IN(654, 301, 207)";
	}

	my ($sthMain) = &Do_SQL("SELECT po.*
							FROM sl_purchaseorders po								
							WHERE po.`Type`='Return to Vendor' 
								AND YEAR(po.Date)>=2014 
								AND po.Date < '2015-01-02'
								$where_vendor;");
	my $i = 0;
	&Do_SQL("BEGIN;");
	while ( $refMain = $sthMain->fetchrow_hashref() ) {
		++$i;
		$id_po_rvendor = $refMain->{'ID_purchaseorders'};
		$id_vendor = $refMain->{'ID_vendors'};
		$fecha = $refMain->{'PODate'};

		##--- Se obtiene la fecha de la nota de devolución
		$sthNotes = &Do_SQL("SELECT Date, Notes  
							FROM sl_purchaseorders_notes 
							WHERE ID_purchaseorders='$id_po_rvendor'
								AND Notes LIKE '%Return to Vendor%';");
		my($fecha_rvendor, $notes_rvendor) = $sthNotes->fetchrow_array();
		$shw_fecha_rvendor = ( !$fecha_rvendor ) ? '<span style="color: red; font-weight: bold;">- - -</span>' : $fecha_rvendor;

		#--- Se obtiene el $id_po_original
		my $idx = index($notes_rvendor, 'Order:');
		my $id_po_original = substr($notes_rvendor, $idx+7);
		my $valid_double = ( length($id_po_original) > 4 ) ? 1 : 0;

		print '<hr />';
		print '<span style="background-color: #044f95; color: #ffffff; display: block; font-weight: bold; padding: 3px 2px 3px 5px; width: 100%;">Registro: '.$i.'</span>';
		print '<span style="font-weight: bold; color: #454444;">ID_purchaseorders(RVendor):</span> '.$id_po_rvendor.'<br />';
		print '<span style="font-weight: bold; color: #454444;">ID_purchaseorders(Original):</span> '.$id_po_original.'<br />';
		print '<span style="font-weight: bold; color: #454444;">ID_vendors:</span> '.$id_vendor.'<br />';
		print '<span style="font-weight: bold; color: #454444;">PODate:</span> '.$fecha.'<br />';
		print '<span style="font-weight: bold; color: #454444;">Date Return:</span> '.$shw_fecha_rvendor.'<br />';
		print '<span style="font-weight: bold; color: #454444;">Status:</span> '.$refMain->{'Status'}.'<br />';
		if( $fecha_rvendor ){
			#--------------------------------------------------------------------------#
			#-- PASO: 1, Buscar la contablidad
			#--------------------------------------------------------------------------#
			# print '<br /><span style="border-top: 1px dotted gray; color: blue; display: block; width: 100%;">Procesando los movimientos contables...</span>';
			# #--- Se obtiene la lista de movimientos..
			# $qryMovts = "SELECT * 
			# 			FROM sl_movements 
			# 			WHERE tableused = 'sl_purchaseorders' 
			# 				AND tablerelated = 'sl_purchaseorders' 
			# 				AND ID_tablerelated = '$id_po_rvendor' 
			# 				AND EffDate = '$fecha_rvendor'";
			# $sthMovts = &Do_SQL($qryMovts);
			# print '<span style="white-space: nowrap;">'.$qryMovts.'</span>';
			# if( $sthMovts->rows() > 0 ){
			# 	print '<table style="width: 90%;">';
			# 	print '<tr style="font-weight: bold;">';
			# 	print '	<th>ID_movements</th>';
			# 	print '	<th>ID_accounts</th>';
			# 	print '	<th>Amount</th>';
			# 	print '	<th>EffDate</th>';
			# 	print '	<th>tableused</th>';
			# 	print '	<th>ID_tableused</th>';
			# 	print '	<th>tablerelated</th>';
			# 	print '	<th>ID_tablerelated</th>';
			# 	print '	<th>Category</th>';
			# 	print '	<th>Credebit</th>';
			# 	print '	<th>Status</th>';
			# 	print '</tr>';
			# 	while ( $refMovts = $sthMovts->fetchrow_hashref() ) {
			# 		print '<tr>';
			# 		print '	<td>'.$refMovts->{'ID_movements'}.'</td>';
			# 		print '	<td>'.$refMovts->{'ID_accounts'}.'</td>';
			# 		print '	<td>'.$refMovts->{'Amount'}.'</td>';
			# 		print '	<td>'.$refMovts->{'EffDate'}.'</td>';
			# 		print '	<td>'.$refMovts->{'tableused'}.'</td>';
			# 		print '	<td>'.$refMovts->{'ID_tableused'}.'</td>';
			# 		print '	<td>'.$refMovts->{'tablerelated'}.'</td>';
			# 		print '	<td>'.$refMovts->{'ID_tablerelated'}.'</td>';
			# 		print '	<td>'.$refMovts->{'Category'}.'</td>';
			# 		print '	<td>'.$refMovts->{'Credebit'}.'</td>';
			# 		print '	<td>'.$refMovts->{'Status'}.'</td>';
			# 		print '</tr>';

			# 		##--- Se genera el movimiento contable para cancelar el movimiento actual...
   			#  		$new_credebit = ( $refMovts->{'Credebit'} eq 'Debit' ) ? 'Credit' : 'Debit';
   			#  		my (%overwrite) = ('credebit'=>$new_credebit, 'effdate'=>'CURDATE()', 'category'=>'Compras', 'id_journalentries'=>'0');
			# 		$applied_movts = &Do_selectinsert('sl_movements', "ID_movements = '".$refMovts->{'ID_movements'}."'", " ", " ", %overwrite);
			# 		if( $applied_movts ){
			# 			print '<tr style="color: #016610;">';
			# 			print '	<td>'.$applied_movts.'</td>';
			# 			print '	<td>'.$refMovts->{'ID_accounts'}.'</td>';
			# 			print '	<td>'.$refMovts->{'Amount'}.'</td>';
			# 			print '	<td>'.$refMovts->{'EffDate'}.'</td>';
			# 			print '	<td>'.$refMovts->{'tableused'}.'</td>';
			# 			print '	<td>'.$refMovts->{'ID_tableused'}.'</td>';
			# 			print '	<td>'.$refMovts->{'tablerelated'}.'</td>';
			# 			print '	<td>'.$refMovts->{'ID_tablerelated'}.'</td>';
			# 			print '	<td>Compras</td>';
			# 			print '	<td>'.$new_credebit.'</td>';
			# 			print '	<td>'.$refMovts->{'Status'}.'</td>';
			# 			print '</tr>';
			# 		}
			# 	}
			# 	print '</table>';

			# } else {
			# 	print '<br /><span style="color: gray;">Sin registros de movimientos contables...</span>';
			# }

			#--------------------------------------------------------------------------#
			#-- PASO: 2. Generar la nueva contabilidad
			#--------------------------------------------------------------------------#
			print '<br /><span style="border-top: 1px dotted gray; color: blue; display: block; width: 100%;">Generando la nueva contabilidad...</span>';
			
			$qyrItems = "SELECT (Price*Qty) AS price_total, Tax, Total 
						FROM sl_purchaseorders_items
						WHERE ID_purchaseorders='$id_po_rvendor';";
			$sthItems = &Do_SQL($qyrItems);
			print '<span style="white-space: nowrap;">'.$qyrItems.'</span>';
			my $sum_price_total = 0;
			while ( my($price, $tax, $total) = $sthItems->fetchrow_array() ) {
				$sum_price_total += round($total, 2);
	            
	            #-------------------------------------#
	            #-- 4) Accounting Movements
				#-------------------------------------#
	            my $ptype = &load_name('sl_vendors', 'ID_vendors', $id_vendor, 'Category');
	            $ptype = 'Nacional' if !$ptype;
	            my @params = ($id_po_original, $id_po_rvendor, $price, $tax);
	            &accounting_keypoints('po_rvendor_'. lc($ptype), \@params );
	            print '<br><span style="color: gray; white-space: nowrap;">accounting_keypoints[id_po_original => '.$id_po_original.', id_po_rvendor => '.$id_po_rvendor.', ptype => '.$ptype.', total price => '.$price.', tax => '.$tax.']</span>';
			}			

			print '<br /><span>Sum. Price $ '.$sum_price_total.'</span>';
			if( $valid_double == 0 ){

			} else {
				print '<br /><span style="color: gray;">Doble ID_purchaseorders original ['.$id_po_original.']</span>';
			}
			print '<br />';


			#--------------------------------------------------------------------------#
			#-- PASO: 3. Generar nuevo Bill Tipo Credit y ligarlo al PO del RVendor
			#--------------------------------------------------------------------------#
			print '<br /><span style="border-top: 1px dotted gray; color: blue; display: block; width: 100%;">Generando el nuevo Bill Tipo Credit y lig&aacute;ndolo al PO del RVendor</span>';
			my $currency = &load_name('sl_vendors', 'ID_vendors', $id_vendor, 'Currency');

			$currency_exchange = 0;
			if( $currency eq 'US$' ){
				#----------------------------------------#
				#--- Se obtiene el currency_exchange...
				#----------------------------------------#
				# Se trata de obtener de las notas del purchaseorder actual,
				# en caso de que no esté en alguna de las notas, entonces se obtiene
				# del día de la última recepción para ese purchase order original
				$sthNotaCy = &Do_SQL("SELECT Notes 
				 						FROM sl_purchaseorders_notes 
				 						WHERE ID_purchaseorders='$id_po_rvendor'
				 							AND Notes LIKE '%Currency:%';");
				$nota_cy = $sthNotaCy->fetchrow();
				if( $nota_cy ){
					my $idx = index($nota_cy, 'Currency:');
					$currency_exchange = substr($nota_cy, $idx+9, 6);
				} elsif ( $valid_double == 0 ) {
					#-- Se obtiene la fecha de la última recepción para ese purchase_order original
					$sthFechaEC = &Do_SQL("SELECT InvoiceDate 
					 						FROM sl_wreceipts 
					 						WHERE ID_purchaseorders='$id_po_original' 
					 						ORDER BY InvoiceDate DESC, ID_wreceipts DESC
					 						LIMIT 1;");
					$fecha_ec = $sthFechaEC->fetchrow();
					#-- Con esa fecha, se obtiene el exchange_rate
					$sthExchgCy = &Do_SQL("SELECT exchange_rate 
					 						FROM sl_exchangerates  
					 						WHERE Date_exchange_rate='$fecha_ec'
					 						LIMIT 1;");
					$currency_exchange = round($sthExchgCy->fetchrow(), 2);
				}				
			}
			print 'Currency: '.$currency;
			print '<br />Currency Exchange: '.$currency_exchange;
			if( ($currency eq 'US$' && $currency_exchange > 0) or $currency eq 'MX$' ){
				my $qryBills = "INSERT INTO sl_bills 
		    						SET ID_vendors = '$id_vendor', 
		    							Type = 'Credit', 
		    							Currency = '$currency', 
		    							currency_exchange = '". $currency_exchange ."', 
		    							Amount = '$sum_price_total', 
		    							Memo = 'PO Original: $id_po_original',
		    							BillDate = '2014-12-31', 
		    							DueDate = '2014-12-31', 
		    							AuthBy = '".$id_user."', 
		    							PaymentMethod = 'Wire Transfer', 
		    							Status = 'New', 
		    							Date = '2014-12-31', 
		    							Time = CURTIME(), 
		    							ID_admin_users = '".$id_user."';";
			    my ($sth) = &Do_SQL($qryBills);
			    my $new_bill = $sth->{'mysql_insertid'};
			    print '<br /><span style="white-space: nowrap;">'.$qryBills.'</span>';
			    if($new_bill){
			    	###
		    		### 3.0) Ligamos el nuevo Bill con el PO contablemente
		    		###
		    		$qryUpdMov = "UPDATE sl_movements 
				    					SET tablerelated = 'sl_bills', 
				    						ID_tablerelated = '$new_bill', 
				    						EffDate = '2014-12-31',
				    						Date = '2014-12-31'
				    				WHERE ID_tableused = '". $id_po_rvendor ."' 
				    					AND tableused = 'sl_purchaseorders' 
				    					AND (tablerelated IS NULL OR tablerelated = '') 
				    					AND (ID_tablerelated IS NULL OR ID_tablerelated = 0) 
				    					AND TIMESTAMPDIFF(SECOND, CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 20;";
		    		&Do_SQL($qryUpdMov);
		    		print '<br /><span style="color: #585858; white-space: nowrap;">'.$qryUpdMov.'</span>';

			        #-------------------------------------#
			        #-- 3.1) ligamos el PO al Bill
			        #-------------------------------------#
			        $qryBillsPos = "INSERT INTO sl_bills_pos 
					        			SET ID_bills = '$new_bill', 
						        			ID_purchaseorders = '$id_po_rvendor', 
						        			Amount = '$sum_price_total', 
						        			Date = '2014-12-31', 
						        			Time = CURTIME(), 
						        			ID_admin_users = '".$id_user."';";
			        &Do_SQL($qryBillsPos);
			        print '<br /><span style="white-space: nowrap;">'.$qryBillsPos.'</span>';

			        #-------------------------------------#
			        #-- 3.2) Nota en Bill y PO
			        #-------------------------------------#
			        $qryBillsNotes = "INSERT INTO sl_bills_notes 
					        			SET ID_bills = '$new_bill', 
					        				Notes = 'Automatic Credit Originated From RVendor: $id_po_rvendor', 
					        				Type = 'Low', 
					        				Date = '2014-12-31', 
					        				Time = CURTIME(), 
					        				ID_admin_users = '".$id_user."';";
			        &Do_SQL($qryBillsNotes);
			        print '<br /><span style="color: gray; white-space: nowrap;">'.$qryBillsNotes.'</span>';

			        $qryPosNotes = "INSERT INTO sl_purchaseorders_notes 
					        			SET ID_purchaseorders = '$id_po_rvendor', 
					        				Notes ='New Credit Bill Created: $new_bill', 
					        				Type = 'Low', 
					        				Date = '2014-12-31', 
					        				Time = CURTIME(), 
					        				ID_admin_users = '".$id_user."';";
			        &Do_SQL($qryPosNotes);
			        print '<br /><span style="color: gray; white-space: nowrap;">'.$qryPosNotes.'</span>';
			    }
			} else {
				print '<span style="color: red; display: block; width: 100%;">No se pudo procesar por que no se encontró el "exchange_rate"...</span>';
			}

		} else {
			print '<span style="border-bottom: 1px dotted gray; border-top: 1px dotted gray; color: red; display: block; width: 100%;">No process...</span>';
		}
	}
	&Do_SQL($finish_trans);

	#print '<br /><br /><hr /><hr />';
	#print '<span style="font-weight: bold;">Registros Correctos para procesar:</span> <span style="color: #209001;">'.$rows_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Registros Con errores:</span> <span style="color: #ff0000;">'.$rows_no_ok.'</span><br />';
	#print '<span style="font-weight: bold;">Total de Registros:</span> <span style="color: #0000ff;">'.$i.'</span>';
	#print '<hr />';
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