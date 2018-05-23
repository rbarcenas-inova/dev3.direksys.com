#!/usr/bin/perl
############################################################################
############  RECONCILIACION SOSL/CYBERSOURCE
############################################################################


sub fin_report_conciliation{
#-----------------------------------------
# Created on: 01/15/09  12:09:51 By  Roberto Barcenas
# Forms Involved: fin_report_conciliation.html
# Description :
# Parameters :
# Last Modified RB: 02/17/09  17:31:04 -- Order > 0 validation
# Last Modification by JRG : 03/09/2009 : Se agrega el log
# Last Modified RB: 03/17/09  12:48:07 -- Funcion &fixauthcode repara authcodes en 0000 para preorders|orders
# Last Modified on: 04/20/09 10:34:25
# Last Modified by: MCC C. Gabriel Varela S: Se quita referencia a precustomers
# Last Modified on: 05/13/09 12:37:29
# Last Modified by: MCC C. Gabriel Varela S: Se quita referencia a precustomers
 
	my ($err,$rec_date);
	(!$in{'base'}) and ($in{'base'} = 'cyb');
	my ($date) = $in{'date'};

	($va{'tab1'},$va{'tab2'},$va{'tab3'},$va{'tab4'}) = ('off','off','off','off');
	($in{'base'} eq 'cyb') and ($va{'tab1'} = 'on');
	($in{'base'} eq 'sosl_pre') and ($va{'tab2'} = 'on');
	($in{'base'} eq 'sosl_ord') and ($va{'tab3'} = 'on');
	($in{'base'} eq 'cash') and ($va{'tab4'} = 'on');

	if ($date){
		## 1st step - check if there is data in sl_cybcaptreport
		my ($sth) = &Do_SQL("SELECT COUNT(ID_orders) FROM sl_cybcaptreport WHERE Date='".&filter_values($date)."' ");
		$va{'matches'} = $sth->fetchrow();
		if($va{'matches'} == 0){
			$err = 1;
			$va{'message'} = &trans_txt('No_cybersource_data');
			$error{'date'} = &trans_txt('invalid')
		}
		(!$in{'date'}) and ($error{'date'} = &trans_txt('required'));
	}else{
		++$err;
	}
	if(!$err){
		my ($id_orders_payment,$first,$qs,$payment,$err1,$err2,$orders,$customers,$tbl,$sth);
		if ($in{'base'} eq 'cyb'){
			$rec_date = &sqldate_plus($date,-1);
			###################################
			###### CYBSOURCE VS SOSL
			###################################

			if($in{'export'}){
				print "Content-type: application/octet-stream\n";
				print "Content-disposition: attachment; filename=conciliation_$date.csv\n\n";
				print "ID Order,Amount,Card,Amount,Card,CapDate\r\n";
				$sth = &Do_SQL("SELECT * FROM sl_cybcaptreport WHERE Date='".&filter_values($date)."'  ORDER BY ID_orders DESC;");
			}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
				$sth = &Do_SQL("SELECT * FROM sl_cybcaptreport WHERE Date='".&filter_values($date)."'  ORDER BY ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
			}

			while($rec = $sth->fetchrow_hashref){
				$rec->{'CardType'} =~ s/ - Debit| - Credit//g;
				$rec->{'CustomerData'} =~ s/\n/<br>/g;
				$rec->{'Comments'} =~ s/\n/<br>/g;
				if($rec->{'ID_orders'}> 0){
					#########################
					#### orders
					#########################
					my ($sth2) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders=$rec->{'ID_orders'};");
					$orders = $sth2->fetchrow_hashref();

					$orders->{'PostedDate'} = &repairOrderDates($rec->{'ID_orders'}) if (!$orders->{'PostedDate'} or $orders->{'PostedDate'} eq '0000-00-00');

					my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=$orders->{'ID_customers'};");
					$customers = $sth2->fetchrow_hashref();

					my ($sth2) = &Do_SQL("SELECT Data,ID_orders_payments FROM sl_orders_plogs WHERE DATA LIKE '%$rec->{'TransRefNo'}%' AND ID_orders=$rec->{'ID_orders'};");
					($data,$id_orders_payment) = $sth2->fetchrow;
					if (!$id_orders_payment){
						($id_orders_payment) = &load_plogs($data,'ID_orders_payments');
					}
					if ($id_orders_payment){
						my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders_payments=$id_orders_payment;");
						$payment = $sth2->fetchrow_hashref();
					}else{
						$payment = '';
					}
					$tbl = 'orders';

					## Payment Without PostedDate
					$err4 = '';
					if($id_orders_payment and (!$payment->{'PostedDate'} or $payment->{'PostedDate'} eq '0000-00-00' or !$payment->{'CapDate'} or $payment->{'CapDate'} eq '0000-00-00' or ($payment->{'Amount'} > 0 and  $payment->{'PostedDate'} ne $orders->{'PostedDate'}))){
						my $amtOrder = &load_order_total($rec->{'ID_orders'},$orders->{'PostedDate'});
						my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = $rec->{'ID_orders'} AND Amount > 0 AND ID_orders_payments <> $id_orders_payment  AND Status NOT IN('Order Cancelled','Cancelled') ");
						my ($amtPay) = $sth->fetchrow + $payment->{'Amount'};

						#($rec->{'ID_orders'}eq'91740') and (&cgierr("$amtPay - $amtOrder  == $orders->{'PostedDate'}"));
						if($amtOrder == 0){
								&Do_SQL("UPDATE sl_orders_payments SET PostedDate = IF( PostedDate IS NOT NULL AND PostedDate != '0000-00-00' AND PostedDate != '', PostedDate, IF( CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '', CapDate, Date ) ) ,CapDate = IF( CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '', CapDate, Date ) ,Reason = 'Refund' WHERE ID_orders_payments = $id_orders_payment ");
								&auth_logging('opr_orders_pay_updated',$id_orders_payment);
						}else{
							($amtPay - $amtOrder <= 1 and $amtPay - $amtOrder >=0 and $rec->{'Amount'} > 0)?
								&Do_SQL("UPDATE sl_orders_payments SET PostedDate = '$orders->{'PostedDate'}' ,CapDate = IF( CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '', CapDate, Date ) ,Reason = 'Sale' WHERE ID_orders_payments = $id_orders_payment "):
								&Do_SQL("UPDATE sl_orders_payments SET PostedDate = IF( PostedDate IS NOT NULL AND PostedDate != '0000-00-00' AND PostedDate != '', PostedDate, IF( CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '', CapDate, Date ) ) ,CapDate = IF( CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '', CapDate, Date ) ,Reason = 'Other' WHERE ID_orders_payments = $id_orders_payment ");
								&auth_logging('opr_orders_pay_updated',$id_orders_payment);
						}
					}
				}

				&fixauthcode($tbl,$id_orders_payment,$rec->{'ID_orders'})	if(($payment->{'AuthCode'} eq '0000' or $payment->{'AuthCode'} eq '') and $id_orders_payment and $payment->{'Amount'} > 0);

				(!$orders->{'PostedDate'}) and ($orders->{'PostedDate'} = 'N/A');
				if($rec->{'ID_orders'} <= 0){ $payment->{'Amount'} = 0; $payment->{'CapDate'} = 'Unknown'; $payment->{'PmtField1'} = 'Unknown';}


				## Error in Amount	
				($rec->{'Amount'}-$payment->{'Amount'} >0)?
					($err3 = qq|<a href="#" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Unknown Transaction in Cybersource</span></a>|):
					($err3 = '');
				## Error in Date
				($payment->{'CapDate'} ne $rec_date and !$err3) ?
					($err1 = qq|<a href="#" onClick="delete_div('err1$rec->{'ID_cybcaptreport'}');update_dbfield('&tbl=sl_|.$tbl.qq|_payments&id_name=id_|.$tbl.qq|_payments&id_value=$payment->{'ID_'.$tbl.'_payments'}&updfield=CapDate','$rec_date')" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Incorrect Capture Date.<br>Click to Adjust to :$rec_date</span></a>|):
					($err1='');

				## Error in Credit Card Type
				(lc($rec->{'CardType'}) ne lc($payment->{'PmtField1'}) and !$err3)?
					($err2 = qq|<a href="#" onClick="delete_div('err2$rec->{'ID_cybcaptreport'}');update_dbfield('&tbl=sl_|.$tbl.qq|_payments&id_name=id_|.$tbl.qq|_payments&id_value=$payment->{'ID_'.$tbl.'_payments'}&updfield=PmtField1','$rec->{'CardType'}')" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Incorrect Credit Card Type<br>Click to Adjust to:$rec->{'CardType'}</span></a>|):
					($err2='');

				if($in{'export'}){
					print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'CardType'},$payment->{'Amount'},$payment->{'PmtField1'},$payment->{'CapDate'}\r\n";
				}else{

						$va{'searchresults'} .= qq|
						<tr>
							<td class="smalltext" nowrap align="right"><a href="/cgi-bin/mod/admin/dbman?cmd=opr_$tbl&view=$rec->{'ID_orders'}">$rec->{'ID_orders'}</a></td>
							<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
								<span><u>Order Data</u><br>
									Sale Date : $orders->{'PostedDate'}<br>
									Order Net : $orders->{'OrderNet'}<br>
									Bill State : $orders->{'State'}<br>
									Ship State : $orders->{'shp_State'}<br>
									<u>Customer</u><br>
									$customers->{'FirstName'} $customers->{'LastName1'} $customers->{'LastName2'}
								</span></a></td>
							<td bgcolor="#C0C0C0" width="1"></td>
							<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|</td>
							<td class="smalltext">$rec->{'CardType'}</td>
							<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
								<span><u>Customer Data</u><br>
									$rec->{'CustomerData'}<br>
									XXX-XXX-XXX-$rec->{'AccountSuffix'}<br>
									<u>Comments</u><br>
									$rec->{'Comments'}
								</span></a></td>
							<td bgcolor="#C0C0C0" width="1"></td>
							<td class="smalltext" align="right">|.&format_price($payment->{'Amount'}).qq|</td>
							<td><div id="err4$rec->{'ID_cybcaptreport'}">$err4</div></td>
							<td><div id="err3$rec->{'ID_cybcaptreport'}">$err3</div></td>
							<td class="smalltext">$payment->{'PmtField1'}</td>
							<td><div id="err2$rec->{'ID_cybcaptreport'}">$err2</div></td>
							<td class="smalltext">$payment->{'CapDate'}</td>
							<td><div id="err1$rec->{'ID_cybcaptreport'}">$err1</div></td>
							<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
								<span><u>Payment Info</u><br>
									$payment->{'PmtField2'}<br>
									XXX-XXX-XXX-|.substr($payment->{'PmtField3'},-4).qq|<br>
									AuthCode : $payment->{'AuthCode'}<br>
									Paymentdate : $payment->{'Paymentdate'}
								</span></a></td>
						</tr>\n|;
				}
			}

		}elsif ($in{'base'} eq 'sosl_ord' or $in{'base'} eq 'sosl_pre'){
			$rec_date = &sqldate_plus($date,+1);

			###################################
			###### SOSL VS CYBSOURCE / PREORDERS/ORDERS
			###################################
			my ($recid,$cyb,$pref,$rtype);
			$rtype = 'Order';

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_".$pref."orders_payments WHERE CapDate='".&filter_values($date)."' AND Type IN ('Credit-Card','Layaway');");
			$va{'matches'} = $sth->fetchrow;
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT * FROM sl_".$pref."orders_payments WHERE CapDate='".&filter_values($date)."'  ORDER BY ID_".$pref."orders DESC LIMIT $first,$usr{'pref_maxh'};");
			while($rec = $sth->fetchrow_hashref){
				my ($sth2) = &Do_SQL("SELECT * FROM sl_".$pref."orders WHERE ID_".$pref."orders=$rec->{'ID_'.$pref.'orders'};");
				$orders = $sth2->fetchrow_hashref();

				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=$orders->{'ID_customers'};");
				$customers = $sth2->fetchrow_hashref();

				my ($sth2) = &Do_SQL("SELECT Data FROM sl_".$pref."orders_plogs WHERE DATA LIKE '%ccCaptureReply_reconciliationID%' AND ID_".$pref."orders_payments=$rec->{'ID_'.$pref.'orders_payments'};");
				$data = $sth2->fetchrow;
				($recid) = &load_plogs($data,'ccCaptureReply_reconciliationID');
				if ($recid){
					my ($sth2) = &Do_SQL("SELECT * FROM sl_cybcaptreport WHERE TransRefNo='$recid';");
					$cyb = $sth2->fetchrow_hashref;
					$cyb->{'CardType'} =~ s/ - Debit| - Credit//g;
					$cyb->{'CustomerData'} =~ s/\n/<br>/g;
					$cyb->{'Comments'} =~ s/\n/<br>/g;
				}else{
					$cyb = '';
				}
				(!$orders->{'PostedDate'}) and ($orders->{'PostedDate'} = 'N/A');
				## Error in Amount
				($rec->{'Amount'}-$cyb->{'Amount'} >0)?
					($err3 = qq|<a href="#" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Unknown Transaction in Cybersource or Different Amount in Cybersource</span></a>|):
					($err3 = '');
				## Error in Date
				($cyb->{'Date'} ne $rec_date and !$err3) ?
					($err1 = qq|<a href="#" onClick="delete_div('err1$rec->{'ID_'.$pref.'orders_payments'}');update_dbfield('&tbl=sl_|.$pref.qq|orders_payments&id_name=id_|.$pref.qq|orders_payments&id_value=$rec->{'ID_'.$pref.'orders_payments'}&updfield=CapDate','|.&sqldate_plus($cyb->{'Date'},-1).qq|')" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Incorrect Capture Date.<br>Click to Adjust to :|.&sqldate_plus($cyb->{'Date'},-1).qq|</span></a>|):
					($err1='');

				## Error in Credit Card Type
				(lc($rec->{'CardType'}) ne lc($payment->{'PmtField1'}) and !$err3)?
					($err2 = qq|<a href="#" onClick="delete_div('err2$rec->{'ID_'.$pref.'orders_payments'}');update_dbfield('&tbl=sl_|.$pref.qq|orders_payments&id_name=id_|.$pref.qq|orders_payments&id_value=$rec->{'ID_'.$pref.'orders_payments'}&updfield=PmtField1','$rec->{'CardType'}')" class='Info'><img src="$va{'imgurl'}/$usr{'pref_style'}/b_warning.png" title="Error" alt="" border="0"><span>Incorrect Credit Card Type<br>Click to Adjust to:$rec->{'CardType'}</span></a>|):
					($err2='');

				$va{'searchresults'} .= qq|
				<tr>
					<td class="smalltext" nowrap align="right"><a href="/cgi-bin/mod/admin/dbman?cmd=opr_|.$pref.qq|orders&view=$rec->{'ID_'.$pref.'orders'}">$rec->{'ID_'.$pref.'orders'}</a></td>
					<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
						<span><u>$rtype Data</u><br>
							Sale Date : $orders->{'PostedDate'}<br>
							Order Net : $orders->{'OrderNet'}<br>
							Bill State : $orders->{'State'}<br>
							Ship State : $orders->{'shp_State'}<br>
							<u>Customer</u><br>
							$customers->{'FirstName'} $customers->{'LastName1'} $customers->{'LastName2'}
						</span></a></td>
					<td bgcolor="#C0C0C0" width="1"></td>
					<td class="smalltext" align="right">|.&format_price($cyb->{'Amount'}).qq|</td>
					<td class="smalltext">$cyb->{'CardType'}</td>
					<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
						<span><u>Captured Date</u> : $cyb->{'Date'}<br>
							<u>Customer Data</u><br>
							$cyb->{'CustomerData'}<br>
							XXX-XXX-XXX-$cyb->{'AccountSuffix'}<br>
							<u>Comments</u><br>
							$cyb->{'Comments'}
						</span></a></td>
					<td bgcolor="#C0C0C0" width="1"></td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|</td>
					<td><div id="err3$rec->{'ID_'.$pref.'orders_payments'}">$err3</div></td>
					<td class="smalltext">$rec->{'PmtField1'}</td>
					<td><div id="err2$rec->{'ID_'.$pref.'orders_payments'}">$err2</div></td>
					<td class="smalltext">$rec->{'CapDate'}</td>
					<td><div id="err1$rec->{'ID_'.$pref.'orders_payments'}">$err1</div></td>
					<td class="smalltext"><a href="#" class="info"><img src='$va{'imgurl'}/$usr{'pref_style'}/_ichelpsmall.gif' title="More Info" alt="" border="0">
						<span><u>Payment Info</u><br>
							$rec->{'PmtField2'}<br>
							XXX-XXX-XXX-|.substr($rec->{'PmtField3'},-4).qq|<br>
							AuthCode : $rec->{'AuthCode'}<br>
							Paymentdate : $rec->{'Paymentdate'}<br>
							PaymentID : $rec->{'ID_'.$pref.'orders_payments'}
						</span></a></td>
				</tr>\n|;

			}

		}

		if($in{'export'}){
			return;
		}elsif ($va{'searchresults'}){
			print "Content-type: text/html\n\n";
			print &build_page('fin_report_conciliation_list.html');
			return;
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_report_conciliation.html');

}



sub fin_cybcaptreport {
# --------------------------------------------------------
# Created on: 01/15/09 @ 14:16:15
# Author: Carlos Haas
# Last Modified on: 01/15/09 @ 14:16:15
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 


	print "Content-type: text/html\n\n";
	my ($key,$line,$line_complete);
	my $old_report=0;
	if ($in{'action'}){
		foreach my $key ( keys %in){
			if ($in{$key} eq 'Process File'){
				if (open(my $capt, "<", "$cfg{'path_upfiles'}capture/$key")){
					$old_report = 1	if($key=~	/old/);
					LINE: while (<$capt>) {
						$line = $_;
						next LINE if(!$old_report and $line !~	/^innintl/);
						if (($old_report and $line =~ /\"Success/) or (!$old_report and $line =~ /Settlement\(Accept\)/) and !$line_complete){  #"
							$line_complete = $line;
						}elsif (($old_report and $line =~ /\"Success/) or (!$old_report and $line =~ /Settlement\(Accept\)/)){  #"
							## process Line
							&proc_cyb_capture($line_complete)	if $old_report;
							&proc_cyb_capture_new($line_complete)	if !$old_report;
							$line_complete = $line;
						}elsif($line_complete){
							$line_complete .= $line;
						}elsif($line and !$line_complete){
							$line_complete = $line;
						}
					}
					## Process Line
					&proc_cyb_capture($line_complete)	if $old_report;
					&proc_cyb_capture_new($line_complete)	if !$old_report;
					unlink("$cfg{'path_upfiles'}capture/$key");
					$va{'message'} = "file Processed $in{'count'} : " . $in{$key};
				}else{
					$va{'message'} = "$cfg{'path_upfiles'}capture/$key $!";
				}
			}
		}
	}
	my (@files,$file);
	## Captured Files
	opendir (AUTHDIR, "$cfg{'path_upfiles'}capture") || &cgierr("Unable to open directory $cfg{'path_upfiles'}capture",604,$!);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
	closedir (AUTHDIR);
	FILE: foreach my $file (@files) {
		next if ($file =~ /^\./);		# Skip "." and ".." entries..
		next if ($file =~ /^index/);		# Skip index.htm type files..
		$va{'searchresults'} .= qq|
			<tr>
				<td class="smalltext">$file</td>
				<td class="smalltext">|.localtime((stat("$cfg{'path_upfiles'}capture/$file"))[9]).qq|</td>
				<td><input type="submit" name="$file" value="Process File" class="button"></td>
			</tr>\n|;

	}
	if (!$va{'searchresults'}){
		$va{'searchresults'} .= qq|
			<tr>
				<td class="smalltext" align="center" colspan="3">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	#print "Content-type: text/html\n\n";
	print &build_page('fin_cybcaptreport.html');
}

sub proc_cyb_capture {
# --------------------------------------------------------
# Last Modification by JRG : 03/09/2009 : Se agrega el log

	my ($line) = @_;
	my (@ary) = split(/","/, $line);
	my (@cols,$query);
	my (@colsnames) = ('CardType','ID_orders','Date','TransRefNo','AccountSuffix','Amount','CustomerData','Comments');

	$cols[0] = $ary[1]; # CardType
	$cols[1] = $ary[2]; # ID_orders
	$ary[3] =~ /([^\/]+)\/([^\/]+)\/([^\s]+)\s/;
	$cols[2] = "$3-$1-$2"; # Date
	#$cols[2] = $ary[3];
	$cols[3] = $ary[4]; # TransRefNo
	$cols[4] = $ary[5]; # AccountSuffix
	$cols[5] = $ary[6]; # Amount
	$cols[6] = $ary[7]; # CustomerData
	$cols[7] = $ary[9]; # Comments
	for (0..$#colsnames){
		$cols[$_] =~ s/"//g;  #"
		$query .= "$colsnames[$_]='".&filter_values($cols[$_])."',";
	}
	chop($query);
	my ($sth) = &Do_SQL("INSERT INTO sl_cybcaptreport SET $query");
	&auth_logging('cybcaptreport_added',$sth->{'mysql_insertid'});
	++$in{'count'};
}


sub proc_cyb_capture_new {
#-----------------------------------------
# Created on: 10/22/09  11:39:15 By  Roberto Barcenas
# Forms Involved: 
# Description : New cybersource report format as of Septmeber/03/2009 
# Parameters : 

	my ($line) = @_;
	my (@ary) = split(/,/, $line);
	my (@cols,$query);
	my (@colsnames) = ('CardType','ID_orders','Date','TransRefNo','AccountSuffix','Amount','CustomerData','Comments');

#	$cols[0] = $ary[6]; # CardType
#	$cols[1] = $ary[4]; # ID_orders
#	$cols[2] = $ary[2];#"$3-$1-$2"; # Date
#	$cols[3] = $ary[5]; # TransRefNo
#	$cols[4] = '0000'; # AccountSuffix
#	$cols[5] = $ary[8]; # Amount
#	$cols[6] = 'N/A'; # CustomerData
#	$cols[7] = $ary[3]; # Comments

	$cols[0] = $ary[14]; # CardType
	$cols[1] = $ary[4]; # ID_orders
	$ary[2] =~ /([^\/]+)\/([^\/]+)\/([^\s]+)\s/;
	$cols[2] = "$3-$1-$2"; # Date
	$cols[3] = int($ary[16]); # TransRefNo
	$cols[4] = $ary[10]; # AccountSuffix
	$cols[5] = $ary[8]; # Amount
	$cols[6] = $ary[5] .' '.$ary[6]; # CustomerData
	$cols[7] = $ary[3]; # Comments


	for (0..$#colsnames){
		$cols[$_] =~ s/"//g;  #"

		if($colsnames[$_] eq 'Date'){
			$query .= "$colsnames[$_]=DATE_ADD('".&filter_values($cols[$_])."',INTERVAL 1 DAY),";
		}else{
			$query .= "$colsnames[$_]='".&filter_values($cols[$_])."',";
		}
	}
	chop($query);
	my ($sth) = &Do_SQL("INSERT INTO sl_cybcaptreport SET $query");
	&auth_logging('cybcaptreport_added',$sth->{'mysql_insertid'});
	++$in{'count'};
}


sub fixauthcode{
#-----------------------------------------
# Created on: 03/17/09  11:07:47 By  Roberto Barcenas
# Forms Involved: fin_report_conciliation
# Description : Repara el authcode de preorders y orders cuando esta en 0000 y si existe en paylogs
# Parameters : 

	my ($prefix,$id_orders_payment,$id_orders)	=	@_;

	my ($sth) = &Do_SQL("SELECT TRIM( SUBSTR( DATA , LOCATE( 'ccAuthReply_authorizationCode', Data ) +32, 12 ) ) FROM sl_".$prefix."_plogs WHERE ID_$prefix = '$id_orders' AND ID_".$prefix."_payments = '$id_orders_payment' AND LOCATE( 'ccAuthService_run = true', Data ) > 1 AND LOCATE( 'decision = ACCEPT', Data ) > 1 AND LOCATE( 'ccAuthReply_authorizationCode', Data ) > 1 ORDER BY Date DESC LIMIT 1");
	my ($authcode) =	$sth->fetchrow();
	$authcode =~	s/\n.*//g;

	&Do_SQL("UPDATE sl_".$prefix."_payments SET AuthCode = '$authcode' WHERE ID_".$prefix."_payments = '$id_orders_payment' AND (AuthCode = '0000' OR AuthCode = '' OR AuthCode IS NULL) ");

}	

############################################################################################
############################################################################################
#	Function: fin_enter_cod
#   	Genera de forma dinamica el campo Status para el form manifests_form
#
#	Created by:
#		02/09/2009::Jose Ramirez Garcia
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
# Last Modified on: 03/09/09 12:13:28
# Last Modified by: MCC C. Gabriel Varela S: Se corrige update que tiene where ID_warehouses = . Observaci�n hecha por Jos�.
# Last Modification by JRG : 03/09/2009 : Se agrega el log
# Last Modified on: 03/11/09 16:28:51
# Last Modified by: MCC C. Gabriel Varela S: Se hace que sea posible agregar las notas al paylog
# Last Modified RB: 03/31/09  10:46:46 -- Se pasaron los paylogs y las parts a la orden.
# Last Modified on: 04/01/09 11:51:14
# Last Modified by: MCC C. Gabriel Varela S: Se comenta &cgierr("$cols[$i]");
# Last Modified on: 04/07/09 16:51:16
# Last Modified by: MCC C. Gabriel Varela S: Se da un porcentaje de error para pagos COD.
# Last Modified on: 04/16/09 12:45:28
# Last Modified by: MCC C. Gabriel Varela S: Se arregla para aceptar pagos de m�s del 3%
# Last Modified on: 04/17/09 17:13:26
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_admin_users por min�sculas en $usr y otros cambios(se comenta precustomers a customers)
# Last Modified on: 04/20/09 11:12:17
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para funcionamiento de una sola tabla de customers
# Last Modified on: 04/24/09 10:48:16
# Last Modified by: MCC C. Gabriel Varela S: Se corrige conversi�n a orden.
# Last Modified RB: 06/19/09  11:00:19 -- Se agregan los movimientos de contabilidad
# Last Modified on: 07/20/09 12:10:05
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para entrar pago con cc.
# Last Modified by RB on 07/12/2010 : Se agrega verificacion del id_warehouses asignado
# Last Modified by RB on 12/24/2010 : Se agrega sl_skus_trans y se busca item por costo para descargar del inventario
# Last Modified by RB on 04/30/2013 : Se pasa el registro de sl_skus_trans a funcion y se agregaron 2 campos para registrar el Warehouse y el Location
# Last Modified by AD on 30/10/2013 : Se corrige query que obtenia el warehouse
#
#      >>> MUY IMPORTANTE >>> SI SE MODIFICA DEBES MODIFICAR LA FUNCION EN cgi-bin\common\subs\libs\lib.inventory.pl
#
sub fin_enter_cod {
############################################################################################
############################################################################################
	my ($err, $id_customer, $ordernet, $status, $idpp, $cod_order_paid, $ida_banks);
	my (@cols);

	if ($in{'cc'}){
		@cols = ('id_orders','id_warehouses','amount','notes','pmtfield1','pmtfield2','pmtfield3','month','year','pmtfield5','pmtfield6','paymentdate');
		$va{'mocash'} = 'off';
		$va{'cc'} = 'on';
	}else{
		@cols = ('id_orders','id_warehouses','date','amount');
		$va{'mocash'} = 'on';
		$va{'cc'} = 'off';
	}

	if ($in{'action'}){

		$log = '';
		$va{'debug_id_orders'} = $in{'id_orders'};
		my $idwh_assigned;

		if ($in{'id_orders'}){

			$in{'id_orders'} = int($in{'id_orders'});
			$sql = "SELECT COUNT(*) FROM sl_orders WHERE ID_orders = '". $in{'id_orders'} ."' AND Status = 'Processed' and Ptype!='Credit-Card'";
			$log .= $sql."\n\n";
			my ($sth) = &Do_SQL($sql);
			my ($matches) = $sth->fetchrow;
			my($sumprod, $sumpay, $sumdiff);

			## Movs?
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $in{'id_orders'} ."' AND tableused = 'sl_orders' AND Status = 'Active';");
			my ($tmovs) = $sth->fetchrow();

			## Must vs Done
			# $q1 = Lo que salió
			# $q2 = Lo que debió salir
			my $parts_difference;
			my ($sth) = &Do_SQL("SELECT 
									sl_skus_parts.ID_parts
									,SUM(sl_orders_products.Quantity * sl_skus_parts.Qty) AS TQty2 
								FROM sl_orders_products 
									LEFT JOIN sl_skus_parts ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
								WHERE sl_orders_products.ID_orders = " . $in{'id_orders'} . " AND sl_orders_products.Status = 'Active'	
								GROUP BY sl_skus_parts.ID_parts 
								ORDER BY sl_skus_parts.ID_parts;");
			TMvTD:while(my($id_parts, $q2) = $sth->fetchrow()){

				if( $id_parts ){
					my $sth_q1 = &Do_SQL("SELECT 
											SUM(sl_orders_parts.Quantity) Quantity
										FROM sl_orders_parts
											INNER JOIN sl_orders_products USING(ID_orders_products)
										WHERE sl_orders_products.ID_orders = " . $in{'id_orders'} . " 
											AND sl_orders_parts.ID_parts = " . $id_parts . "
										GROUP BY sl_orders_parts.ID_parts;");
					my $q1 = $sth_q1->fetchrow();

					if($q1 ne $q2){

						$va{'message'} .= qq|$id_parts $q1 vs $q2<br>|;
						++$parts_difference; 

					}
				}
				
			}


			if ($matches > 0 and !$tmovs and !$parts_difference){

				$sql = "SELECT ID_customers, OrderNet, Status, ID_warehouses FROM sl_orders WHERE ID_orders=$in{'id_orders'} and Ptype!='Credit-Card'";
				$log .= $sql."\n\n";
				my ($sth) = &Do_SQL($sql);
				($id_customer, $ordernet, $status, $this_driver) = $sth->fetchrow_array();
				$log .= qq|($id_customer, $ordernet, $status, $this_driver)|."\n\n";
				
				$sql = "SELECT
							toProd
							, toPay
							, ABS(toProd - toPay)
						FROM
						(

							SELECT ID_orders, ROUND(SUM(Amount),2) AS toPay 
						FROM sl_orders_payments 
						WHERE ID_orders = " . $in{'id_orders'} . "
							AND Type = 'COD'
							AND Status IN('Approved', 'Pending') 
							AND (Captured = 'No' OR Captured IS NULL) 
							AND (CapDate = '0000-00-00' OR CapDate IS NULL)
						)tmp
						INNER JOIN
						(
							SELECT ID_orders, ROUND(SUM(SalePrice - Discount + Shipping + Tax + ShpTax)) AS toProd
							FROM sl_orders_products
							WHERE ID_orders = " . $in{'id_orders'} . "
							AND Status = 'Active'
						)tmp2
						USING(ID_orders);";
				$log .= $sql."\n\n";
				my ($sth) = &Do_SQL($sql);
				($sumprod, $sumpay, $sumdiff) =  $sth->fetchrow();
				my $strdiff = $sumdiff > 0.50 ? qq|<span style="color:red">Amount Difference: $sumdiff</span>| : '';
				$log .= "sumprod=$sumprod"."\n\n";
				$va{'order_info'} = "Customer: ($id_customer) " . &load_db_names('sl_customers','ID_customers',$id_customer,'[FirstName] [LastName1] [LastName2]') ."<br>Order : <a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$in{'id_orders'}'>$in{'id_orders'}</a> <br> Status: $status<br>Amount Products: $sumprod<br>Amount Payment: $sumpay<br>$strdiff";

				if($sumdiff > 0.50){

					$va{'message'} .= trans_txt('opr_orders_cod_prodpay_difference');
					++$err;

				}

				(!$in{'amount'}) and ($in{'amount'} = $sumpay);
				$log .= "amount=$in{'amount'}"."\n\n";
			
			}else{

				$error{'id_orders'} = &trans_txt('invalid');
				($tmovs) and ($error{'id_orders'} .= " ($tmovs) ");
				++$err;

			}

			## Verificamos que la orden este In Transit
			$sql = "SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '". $in{'id_orders'} ."';";
			$log .= $sql."\n\n";
			my ($sthp) = &Do_SQL($sql);
			if ($sthp->fetchrow() < 1){
				
				$va{'message'} .= &trans_txt('fin_enter_cod_order_no_in_transit');
				++$err;

			}


			$sql = "SELECT 
						sl_warehouses_batches.ID_warehouses
					FROM sl_entershipments 
						INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
					WHERE 
						sl_entershipments.id_orders = '". $in{'id_orders'} ."'
					AND LOWER(sl_entershipments.Status) = 'ok' 
					AND LOWER(sl_entershipments.Type) = 'cod' 
					ORDER BY 
						sl_entershipments.ID_entershipments DESC;";
			$log .= $sql."\n\n";
			my ($sthd) = &Do_SQL($sql);
			($idwh_assigned) = $sthd->fetchrow();
			
			if (!$idwh_assigned){

				$va{'message'} .= &trans_txt('fin_enter_cod_order_no_cod_or_no_in_transit');
				++$err;

			}
			
			$log .= "idwh_assigned = $idwh_assigned"."\n\n";
			$log .= "in{'id_warehouses'} = $in{'id_warehouses'}"."\n\n";

		}


		if ($idwh_assigned ne $in{'id_warehouses'} and $in{'id_warehouses'} ne ''){

			$log .= "idwh_assigned=$idwh_assigned"."\n\n";
			$log .= "in{'id_warehouses'}=$in{'id_warehouses'}"."\n\n";

			$error{'id_warehouses'} = &trans_txt('invalid');
			my ($original_whname)= &load_name('sl_warehouses','ID_warehouses',$idwh_assigned,'Name');
			my ($new_whname)= &load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name');
			$va{'message'} = 'Order was originally assigned to '. $original_whname;
			++$err;

		}elsif($idwh_assigned and !$in{'id_warehouses'}){

			$in{'id_warehouses'} = $idwh_assigned;

		}

		for my $i(0..$#cols){
			$in{$cols[$i]}=&filter_values($in{$cols[$i]});
			if (!$in{$cols[$i]}){
				$error{$cols[$i]} = &trans_txt('required');
				++$err;
			}
		}


		if ($in{'date'} eq ''){
			$error{'date'} = &trans_txt('required');
			++$err;
		}

		if ($in{'id_banks'}){

			my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts FROM sl_banks INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE ID_banks = ". $in{'id_banks'} ." AND sl_banks.Status = 'Active' AND sl_accounts.Status = 'Active' LIMIT 1;");
			$ida_banks = $sth->fetchrow();

			if (!$ida_banks){
				$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
				++$err;	
			}

		}

		if ($in{'amount'} eq '' or $in{'amount'} < 0){
			$error{'amount'} = &trans_txt('required');
			++$err;
		}
		$in{'amount'} =~ s/,|\$\s//g;

		my ($sthdate) = &Do_SQL("SELECT IF( MONTH( CURDATE( ) ) <10, CONCAT( '0', MONTH( CURDATE( ) ) ) , MONTH( CURDATE( ) ) ) AS MONTH , YEAR( CURDATE( ) ) AS Year;");
		my ($tmonth,$tyear)	= $sthdate->fetchrow();

		if ($in{'cc'}){

	        if( int(2000+$in{'year'}) <  int($tyear)   or ( int(2000+$in{'year'}) ==  int($tyear) and int($in{'month'}) <=	int($tmonth)) ){

				$error{'pmtfield4'} = &trans_txt('invalid');
				$va{'message'} .= 'Expired Card';
				++$err;

	        }
		}

		### Valida que no haya otra transaccion en proceso
		my $rslt_val = &transaction_validate($in{'cmd'}, $in{'id_orders'}, 'check');


		if (!$err and $in{'id_orders'} and !$rslt_val){

			### Se bloquea la transaccion para evitar duplicidad
        	my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_orders'}, 'insert');
        	my $flag_acc; my $flag_wh; my $flag_acc_string; my $acc_status; my $acc_string;
        	$va{'this_accounting_time'} = time();

        	my ($sth_logtime) = &Do_SQL("SELECT NOW();");
			my $start_at = $sth_logtime->fetchrow_array();
			$log .= "\n\nstart_at = ".$start_at."\n- - - - - - - - - - - - - - S T A R T - - - - - - - - - - - - - - >\n\n";
			&Do_SQL("START TRANSACTION");

			my $str;
			$in{'id_orders'} = int($in{'id_orders'});
			$in{'notes'} = &filter_values($in{'notes'});
			$in{'refid'} = &filter_values($in{'refid'});
			$in{'refid'} = '' if !$in{'refid'};
			$in{'pmtfield4'}="$in{'month'}$in{'year'}";
			$in{'amount'} =~	s/\$|,//;
			$in{'date2'} = $in{'date'}; ## Se toma para contabilidad
			$in{'date'} = &get_sql_date();# if !$in{'date'};

			### Create Order from preorder
			my ($rec,$rec_cust,$query,$id_orders,$id_customers,$amount,$idpp,$oldamount);
			$sql = "SELECT 
						ID_orders_payments,
						Amount,
						Amount * (1 - $cfg{'porcerror'}/100) AS MinPay,  
						Amount * (1+$cfg{'porcerror'}/100) AS MaxPay,
						IF( ABS($in{'amount'} - Amount) < 1 OR ($in{'amount'} <= Amount * (1+$cfg{'porcerror'} / 100) AND $in{'amount'} >= Amount * (1 - $cfg{'porcerror'} / 100)) ,1,0)AS Valid 
						FROM 
						sl_orders_payments 
						WHERE ID_orders = '". $in{'id_orders'} ."' 
						AND Amount >= 0
						AND (Captured = 'No' OR Captured IS NULL OR Captured='') 
						AND (CapDate = '0000-00-00' OR CapDate IS NULL)
						AND Status IN ('Approved','Pending')
						AND Type = 'COD'
						ORDER BY  ABS($in{'amount'} - Amount), Paymentdate DESC LIMIT 1;";
			$log .= $sql."\n\n";
			my ($sth) = &Do_SQL($sql);	

			$rec = $sth->fetchrow_hashref;
			$idpp = $rec->{'ID_orders_payments'};
			$oldamount = round($rec->{'Amount'},2);
			$log .= "idpp=".$idpp."\n\n";
			$log .= "oldamount=".$oldamount."\n\n";

			my $min_amount = round($rec->{'MinPay'},2);
			my $max_amount = round($rec->{'MaxPay'},2);
			my $valid_amount = $rec->{'Valid'};
			$log .= "min_amount=".$min_amount."\n\n";
			$log .= "max_amount=".$max_amount."\n\n";
			$log .= "valid_amount=".$valid_amount."\n\n";

			### Cero aritmético
			if( $cfg{'arithmetic_zero'} == 1 ){
				### Se corrige el monto Cero en SalePrice
				&Do_SQL("UPDATE sl_orders_products SET 
							sl_orders_products.SalePrice = '".$cfg{'arithmetic_zero_amt'}."'
							, sl_orders_products.Discount = '".$cfg{'arithmetic_zero_amt'}."'
						 WHERE sl_orders_products.ID_orders = ".$in{'id_orders'}." 
							AND sl_orders_products.`Status` = 'Active' 
							AND sl_orders_products.SalePrice = 0
						 ;");
				### Se recalculan los montos para el pedido
				&Do_SQL("UPDATE sl_orders 
							INNER JOIN(
								SELECT sl_orders_products.ID_orders, SUM(sl_orders_products.SalePrice) TotalNet, SUM(sl_orders_products.Discount) TotalDisc
								FROM sl_orders_products
								WHERE sl_orders_products.ID_orders = ".$in{'id_orders'}." 
									AND sl_orders_products.`Status` = 'Active'
							)sl_orders_products ON sl_orders_products.ID_orders = sl_orders.ID_orders
						 SET sl_orders.OrderNet = sl_orders_products.TotalNet, sl_orders.OrderDisc = sl_orders_products.TotalDisc
						 WHERE sl_orders.ID_orders = ".$in{'id_orders'}.";");
			}


			if ($idpp and $valid_amount){

				$log .= "if ($idpp and $valid_amount)\n\n";

				my $modquery;

				##Insert Note:
				my $querydata = "\nRefID=$in{'refid'}\nPaid method=COD\nNotes:$in{'notes'}";
				if ($oldamount != $in{'amount'}){
					$log .= "if ($oldamount != $in{'amount'})\n\n";
					
					$sql = "INSERT INTO sl_orders_notes SET ID_orders='$in{'id_orders'}',Notes = 'Old amount=".&format_price($oldamount)."\nNew Amount=".&format_price($in{'amount'})." ',Type='Low', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'";
					$log .= $sql."\n\n";

					&add_order_notes_by_type($in{'id_orders'},"Old amount=".&format_price($oldamount)."\nNew Amount=".&format_price($in{'amount'}),"Low");
				}

				$in{'db'} = 'sl_orders';

				## Credit Card
				if ($in{'cc'}){

					#borra pago anterior
					&Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders_payments = $idpp;");

					#crea pago nuevo con cc
					my $sth=&Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Type='Credit-Card',PmtField1='$in{'pmtfield1'}',PmtField2='$in{'pmtfield2'}',PmtField3='$in{'pmtfield3'}',PmtField4='$in{'pmtfield4'}',PmtField5='$in{'pmtfield5'}',PmtField6='$in{'pmtfield6'}',PmtField7='$in{'pmtfield7'}',PmtField8='$in{'refid'}',PmtField9='$in{'pmtfield9'}',Amount=$in{'amount'},Reason='$rec->{'Reason'}',Paymentdate='$in{'paymentdate'}',Status='Approved',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					#Se asigna a $idpp nuevo pago.
					$idpp= $sth->{'mysql_insertid'};


					#Se determina si se pago la preorden: Mandar a llamar a autorizar o a capturar.
					require ("../../common/apps/cybersubs.cgi");
					my ($status,$msg,$code) = &sltvcyb_sale($in{'id_orders'}, $idpp);
					if ($status eq 'OK'){
						&auth_logging('opr_orders_payments_paid',$in{'id_orders'});
						$va{'message'} .= "Payment Updated";
						$cod_order_paid =1;
						### Creating PayLog
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$in{'id_orders'}',ID_orders_payments = $idpp,Data='$querydata', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					}else{
						$va{'message'} .= "$status\n$msg\n";
						$cod_order_paid =0;
					}

				}else{	

					## Pago dentro del Rango
					$sql = "UPDATE sl_orders_payments SET PmtField8 = '$in{'refid'}', Amount = '$in{'amount'}', Paymentdate = '$in{'date'}', Captured = 'Yes', Status = 'Approved', CapDate = '$in{'date'}' WHERE ID_orders_payments = '$idpp';";
					$log .= $sql."\n\n";
					my ($sth) = &Do_SQL($sql);
					$in{'db'}='sl_orders';
					&auth_logging('opr_orders_payments_paid', $in{'id_orders'});
					$va{'message'} .= "Payment Updated";
					$cod_order_paid = 1;
					
					### Creating PayLog
					$sql = "INSERT INTO sl_orders_plogs SET ID_orders='$in{'id_orders'}', ID_orders_payments = $idpp, Data='$querydata', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'";
					$log .= $sql."\n\n";
					&Do_SQL($sql);
					
					#######
					####### Movimientos de contabilidad
					#######
					my ($order_type, $ctype, $ptype,@params);
					$sql = "SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';";
					$log .= "\n\n--------- CONTABILIDAD COBRO -----------\n\n" . $sql ."\n\n";
					my ($sth) = &Do_SQL($sql);
					($order_type, $ctype) = $sth->fetchrow();
					@params = !$ida_banks ? ($in{'id_orders'}, $idpp, 1) : ($in{'id_orders'}, $idpp, $ida_banks, 1);
					$log .= qq|params = !$ida_banks ? ($in{'id_orders'}, $idpp, 1) : ($in{'id_orders'}, $idpp, $ida_banks, 1)|."\n\n";
					$ptype = 'COD';
					my $key_order_deposit = &filter_values('order_deposit_'. lc($ctype) .'_'. lc($order_type) .'_'. lc($ptype));
					($acc_status, $acc_string) = &accounting_keypoints($key_order_deposit, \@params );
					++$flag_acc if $acc_status; $flag_acc_string .= qq|<br>|. $acc_string;
					$log .= qq|accounting_keypoints('|.$key_order_deposit."', ".join(':', @params).qq|" )|."\nAcc: $acc_status, $acc_str\n\n";

				}

			}else{

				$log .= "else -> if ($idpp and $valid_amount)\n\n";


				$va{'message'} .= "Invalid Payment Amount: " . &format_price($in{'amount'});
				$log .= "Invalid Payment Amount: " . &format_price($in{'amount'})."\n\n";
				$error{'amount'} = &trans_txt('invalid');
				++$err

			}

			if ($cod_order_paid and !$flag_acc){


				###
				##   Only COD paids and no accounting errors
				###
				my $failed_upcs = '';
				$sql = "SELECT 
							ID_orders_products
							, ID_sku_products
							, sl_orders_parts.ID_parts
							, UPC
							, SUM(sl_orders_parts.Quantity)
							, CONCAT(sl_orders_parts.Cost,':',sl_orders_parts.Cost_Adj,':',sl_orders_parts.Cost_Add)
						FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products)
						LEFT JOIN sl_skus ON ID_sku_products = 400000000 + ID_parts
						WHERE ID_orders = '". $in{'id_orders'} ."' 
						AND sl_orders_parts.Status = 'Shipped'
						GROUP BY ID_orders_products, ID_sku_products, sl_orders_parts.Cost;";
				$log .= $sql."\n\n";
				my ($sth3) = &Do_SQL($sql);
				my %ids; my $num = 0;

				PRODUCTS:while (my($id_orders_products, $id_skus, $id_parts, $this_upc, $this_quantity, $this_cost) = $sth3->fetchrow()){

					do{

						++$num;
						--$this_quantity;
						$ids{$num}[0] = $id_skus;
						$ids{$num}[1] = $this_upc;
						$ids{$num}[2] = 'OK';
						$ids{$num}[3] = "SET:$id_orders_products,$id_parts";
						$ids{$num}[4] = $this_cost; # Include cost for perfect match search
						$ids{$num}[5] = 1; # Flag to indicate COD sale

					}while($this_quantity > 0);
					$str .= "$id_orders_products, $id_skus, $id_parts, $this_upc, $this_quantity, $this_cost, $num<br>";

				}

				# Cost Inventory Params ($shpdate, $tracking, $trktype, $id_orders, $id_warehouses, $num, $doflexi, $domiddle, $doinventory, $domessag, %ids)
				my ($status, $msg) = &cost_inventory('', '', '', $in{'id_orders'}, $in{'id_warehouses'}, $num, 0, 0, 1, 1,%ids);

				if (lc($status) ne 'ok'){

					###
					### ERROR
					###
					$va{'message'} = qq|ERROR:<br> | . $msg;# . qq|<br><br>| . $log;
					$flag_wh++;

				}else{

					$sql = "UPDATE sl_orders_payments SET CapDate = '". $in{'date2'} ."' WHERE ID_orders_payments = '". $idpp ."';";
					$log .= $sql."\n\n";
					&Do_SQL($sql);

					###########################
					### sl_orders_parts
					###########################
					$sql = "UPDATE sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) SET sl_orders_products.PostedDate = CURDATE(), sl_orders_parts.PostedDate = CURDATE() WHERE ID_orders =  (". $in{'id_orders'} .");";
					$log .= $sql."\n\n";
					&Do_SQL($sql);

					###
					### OK
					###

					### Payments Lost
					if( $in{'payment_lost'} > 0){

						## Payment not received
						$in{'set_payment_lost'} = 1;

					}elsif( $in{'fake_delivery'} > 0){

						## Payment Lost, Piracy merchandise delivered
						$in{'set_fake_delivery'} = 1;
						&add_order_notes_by_type($in{'id_orders'},"Enter COD Payment","Fake Delivery");
					
					}elsif( $in{'charging_carrier'} > 0){

						### Se obtiene la cuenta asignada a la mensajeria
						my $sql_w = "SELECT ID_accounts FROM sl_warehouses WHERE ID_warehouses = ". $in{'id_warehouses'} .";";
						my $sth_w = &Do_SQL($sql_w);
						my $ida_lost = $sth_w->fetchrow();

						$in{'set_charging_carrier'} = int($ida_lost);
					}

					## Log FD
					$log .= qq|ID Bank: $in{'id_banks'}\nPayment Lost: $in{'set_payment_lost'}\nFake Delivery: $in{'set_fake_delivery'}\nCharge Carrier: $in{'set_charging_carrier'}|;

					### Sale
					sleep(1);
					@params = ($in{'id_orders'});
					($acc_status, $acc_string) = &accounting_keypoints('order_cod_delivered', \@params );
					++$flag_acc if $acc_status; $flag_acc_string .= qq|<br>|. $acc_string;
					$log .= qq|\naccounting_keypoints('order_cod_delivered', [$in{'id_orders'}] )|."\nAcc: $acc_status, $acc_str\n\n";

					$va{'message'} .= ($va{'message'} eq '')? '':'<br>';
					$va{'message'} .= &trans_txt('fin_enter_cod_order_order_processed_successfully').": $in{'id_orders'}";


					$sql = "UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders='".$in{'id_orders'}."' AND Captured <> 'Yes' AND (CapDate IS NULL OR CapDate='0000-00-00') ;";
					$log .= $sql."\n\n";
					&Do_SQL($sql);

					### Insert note from this order.
					&add_order_notes_by_type($in{'id_orders'},"Enter COD Payment","Low");

					
					### Reset Form
					for my $i(0..$#cols){

						$str .= $cols[$i] . ' = ' . $in{$cols[$i]} . "<br>";
						delete($in{$cols[$i]});

					}

					($in{'id_banks'}) and (delete($in{'id_banks'}));
					($in{'refid'}) and (delete($in{'refid'}));
					($in{'notes'}) and (delete($in{'notes'}));
					($in{'id_orders'}) and (delete($in{'id_orders'}));
					($va{'order_info'}) and (delete($va{'order_info'}));
					($in{'set_payment_lost'}) and (delete($in{'set_payment_lost'}));
					($in{'set_fake_delivery'}) and (delete($in{'set_fake_delivery'}));
					($in{'set_charging_carrier'}) and (delete($in{'set_charging_carrier'}));

				}

			}
			
			## Revalidation for not to duplicate
			if (&validate_scan_duplicated($id_orders,"Sale") > 0 or !$cod_order_paid){

				&Do_SQL("ROLLBACK;");
				$log .= "ROLLBACK -> validate_scan_duplicated($id_orders,Sale)\n\n";

				$va{'error'} = 'ERROR';
				$va{'message'} = "<br>".&trans_txt("opr_orders_already_scanned");
				$va{'message'} .= "<br> COD order paid negativo";

			}elsif($flag_acc){

				## Accouting Failed
				&Do_SQL("ROLLBACK;");
				$log .= "ROLLBACK -> Accounting Failed --> ". $flag_acc_string ."\n\n";

				$va{'error'} = 'ERROR';
				$va{'message'} = "<br>".&trans_txt("acc_general") . $flag_acc_string;

			}else{

				if($flag_wh){

					## WH Inventory Failed
					&Do_SQL("ROLLBACK");
					$log .= "ROLLBACK\n\n";

				}else{

					##
					### Final Validation
					##
					$sql = "SELECT
								SUM(IF(Keypoint LIKE 'order_deposit_%',1,0))AS Deposit
								, SUM(IF(Keypoint LIKE 'order_products_inventoryout_%',1,0))AS Inventory
								, SUM(IF(Keypoint = 'order_cod_delivered',1,0))AS Sale
							FROM 
								sl_movements_logs 
							WHERE 
								Date =  CURDATE() 
								AND (
										Keypoint LIKE 'order_deposit_%'
										OR Keypoint LIKE 'order_products_inventoryout_%'
										OR Keypoint LIKE 'order_cod_delivered'
									)
							AND Params LIKE '". $va{'debug_id_orders'} .";;%' 
							AND LOWER(Status) = 'ok';";

					my ($sth) = &Do_SQL($sql);
					my ($this_deposit, $this_inventory, $this_sale) = $sth->fetchrow();
					$log .= "$sql\n\n";

					if(!$this_deposit or !$this_inventory or !$this_sale){

						##
						### Any keypoint Failed
						##
						&Do_SQL("ROLLBACK;");
						$log .= "ROLLBACK -> Keypoint Failed !$this_deposit or !$this_inventory or !$this_sale\n\n";

						$va{'error'} = 'ERROR';
						$va{'message'} = "<br>".&trans_txt("acc_general_keypoints");

					}else{	

						### Log Order Status
						&status_logging($in{'id_orders'},'Shipped');

						##
						### Everything OK
						##

						&Do_SQL("COMMIT;");
						$log .= "COMMIT\n\n";
						# &Do_SQL("ROLLBACK;"); # Debug only
					
					}

				} ## WH Inventory

			}
			
			### Elimina el registro de la transaccion activa de este proceso
	    	&transaction_validate('fin_enter_cod', $va{'debug_id_orders'}, 'delete');
	    	delete($va{'this_accounting_time'});

	    	###----------------------------------------------------
			### Validacion final
			###----------------------------------------------------
			if( int($cfg{'validate_cod_payment'}) == 1 ){
				sleep(1);
				my $sth_ord = &Do_SQL("SELECT `Status` FROM sl_orders WHERE ID_orders = ".$va{'debug_id_orders'}.";");
				my $ord_status = $sth_ord->fetchrow();

				my $sth_inv = &Do_SQL("SELECT cu_invoices.ID_invoices
										FROM cu_invoices
											INNER JOIN cu_invoices_lines ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
										WHERE cu_invoices_lines.id_orders=".$va{'debug_id_orders'}."
											AND cu_invoices.`Status` != 'Cancelled'
										GROUP BY cu_invoices_lines.id_orders;");
				my $invoice = $sth_inv->fetchrow();

				my $sth_mov = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE tableused='sl_orders' AND id_tableused=".$va{'debug_id_orders'}." AND `Status`='Active';");
				my $movs_count = $sth_mov->fetchrow();

				### Captura de cobro incompleto
				if( ($ord_status ne 'Shipped' and int($invoice) > 0) or ($ord_status eq 'Shipped' and $movs_count < 6) ){

					if( int($invoice) > 0 ){
						# &Do_SQL("UPDATE cu_invoices SET `Status`='Void' WHERE ID_invoices = ".$invoice." AND `Status` NOT IN('InProcess','Certified');");
					}

					# $va{'message'} .= "\n<br />Error en el proceso, por favor intente capturar nuevamente el cobro";

					my $body = "ID de Pedido : ".$va{'debug_id_orders'}."<br />\n";
					$body .= "Movimientos Contables : ".$movs_count."<br />\n";
					$body .= "Factura : ".$invoice."<br />\n";

					### Email
					my $subject = 'Error!!! : Enter COD Payment - '.$cfg{'app_title'};
					&send_mandrillapp_email($cfg{'from_email_info'},$cfg{'team_direksys_email'},$subject,$body,$body,'none');
				}
			}
			###----------------------------------------------------

		}elsif( $rslt_val ){
			$va{'message'} = &trans_txt('transaction_duplicate');
		}

		my ($sth_logtime) = &Do_SQL("SELECT NOW(), TIMEDIFF(NOW(),'$start_at');");
		my ($finish_at, $execution_time) = $sth_logtime->fetchrow_array();
		$log .= "finish_at = ". $finish_at ."\n- - - - - - - - - - - - - - F I N I S H - - - - - - - - - - - - - - >\n\n";
		$log .= "Execution Time = ". $execution_time ."\n\n";


		### DEBUG
		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('fin_enter_cod', '$va{'debug_id_orders'}', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	}

	print "Content-type: text/html\n\n";
	print &build_page("fin_enter_cod$in{'cc'}.html");	

}

sub fin_payment_bills{
#-----------------------------------------
# Created on: 29/05/14  11:39:15 By  Arturo Hernandez
# Forms Involved: 
# Description : Screen Payment Bill
# Parameters : 

	use JSON;
	use CGI;
	use Data::Dumper qw(Dumper);
	$va{'totalsinput'} = 0;
	$va{'display2'} = "display:none;";
	$va{'display3'} = "display:none;";

	my $log = '';
	my $ida_banks = 0;
	
	if($in{'process'}){

		$va{'display'} = 'display:none;';
		
		if (!$in{'id_banks'} or $in{'id_banks'} eq ""){
		
			$error{'id_banks'} = &trans_txt('required');
			++$err;
			$in{'action'} = 1;
		
		}else{

			my $query = "SELECT sl_banks.ID_accounts FROM sl_banks INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE ID_banks = ". $in{'id_banks'} ." AND sl_banks.Status = 'Active' AND sl_accounts.Status = 'Active' LIMIT 1;";
			my ($sth) = &Do_SQL($query);
			$ida_banks = $sth->fetchrow();
			$log .= $query;

			if(!$ida_banks){
				$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
				++$err;	
			}
		}

		if (!$in{'bankdate'} or $in{'bankdate'} eq ""){

			$error{'bankdate'} = &trans_txt('required');
			++$err;
			$in{'action'} = 1;

		}
		
		# si el currency del banco es != al currency de bill es requerido en tipo de cambio
		$in{'currency_exchange'} = &filter_values($in{'currency_exchange'});
		my $currency_bank = &load_name("sl_banks","ID_banks",$in{'id_banks'},"Currency");
		my $currency_bill = &load_name("sl_bills","ID_bills",$in{'id_bills'},"Currency");
		$log .= "\nCurrency Bank: ".$currency_bank;
		$log .= "\nCurrency Bill: ".$currency_bill;

		if ($currency_bank ne $in{'currency'} ) {

			if (!$in{'currency_exchange'} or $in{'currency_exchange'} <= 0) {

				$error{'currency_exchange'} = &trans_txt('required');
				++$err;
			
			}

		}else{

			if($cfg{'acc_default_currency'} ne $currency_bank){

				if(!$in{'currency_exchange'} or $in{'currency_exchange'} <= 0){

					#my ($sth) = &Do_SQL("SELECT exchange_rate FROM sl_exchangerates WHERE Date_exchange_rate = curdate() AND Currency = '$currency_bank';");
					$exchg_date = ($in{'bankdate'}) ? "'".$in{'bankdate'}."'" : 'curdate()';
					my $query = "SELECT exchange_rate FROM sl_exchangerates WHERE Date_exchange_rate = $exchg_date AND Currency = '$currency_bank';";
					my ($sth) = &Do_SQL($query);
					$in{'currency_exchange'} = $sth->fetchrow();
					if ( !$in{'currency_exchange'} ) {
						$in{'currency_exchange'} = 1;
					}
					$log .= "\n".$query;

				}

			}else{

				$in{'currency_exchange'} = 1;

			}
			$log .= "\nCurrency Exchange: " . $in{'currency_exchange'};

		}

		if(!$err){

			$q = new CGI;
			my @matriz = $q->param();
			my %varsvh;			

			for my $key (@matriz){

				$i++;
				$value{$key} = $q->param($key);

				if($key =~ /-/){
					
					my @name_field = split("-", $key);
					my $idVendor = $name_field[1];
					my $valuekey = $value{$key};
					
					if($name_field[0] =~ /amount/){
						if($value{$key} ne '' and $value{$key} ne 0){
							$varsvh{$idVendor}{'total'} = $valuekey;
						}
					}
					
					if($name_field[0] =~ /ref/){
						if($value{$key} ne '' and $value{$key} ne 0){
							$varsvh{$idVendor}{'ref'} = $value{$key};
						}
					}
					if($name_field[0] =~ /num_auto/){
						if($value{$key} eq 1){
							$varsvh{$idVendor}{'auto'} = $value{$key};
						}
					}
					if($name_field[1] =~ /#/){
						my @bill = split("#",$name_field[1]);
						$varsvh{$bill['0']}{'bill'}{$bill['1']} = $value{$key};	 
					}	
					
				}

			}


			if($in{'hd_layout_extraction'}){

				###
				##  1. Extraccion de Layout
				###
				$va{'display3'} = 'display:none;';
				$va{'display'} = 'display:none;';
				$va{'display2'} = '';
				
				my $text_data;
				for my $idVendor( keys %varsvh){

					# 1.1. Generacion de layout Each Vendor
					my $totalVendor = $varsvh{$idVendor}{'total'};
					$text_data .= &get_layout_load_bank_payments($idVendor, $varsvh{$idVendor}{'total'}, $in{'hd_layout_extraction_type'});

				}

				if(!$va{'message'}){	

					## Impresion de archivo CSV
					my $f = lc($cfg{"app_title"}) . '_' . lc($bankinfo{'shortname'}) . '_' . &get_sql_date() . '_' . $in{'hd_layout_extraction_type'};
					$f =~ s/ /_/g;

					print "Content-Disposition: attachment; filename=$f.txt;";
					print "Content-type: text/text\n\n";
					print $text_data;
					return;

				}

			}else{

				###
				##  2. Aplicacion Pagos en Direksys
				###

				#my $htmlresult;
				for my $idVendor( keys %varsvh){

					my $vendors = &load_db_names('sl_vendors','ID_vendors',$idVendor,'([ID_vendors]) [CompanyName]');

					$va{'searchresultapply'} .= qq|<tr>
						<td><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$idVendor\">$vendors</a></td>
						</tr>
						<tr>
						<td>
						<table width="100%" border="0" cellspacing="0" cellpadding="4" class="gborder" align="center">
						<td class="menu_bar_title">ID Bill</td>
						<td class="menu_bar_title">Amount</td>
						<td class="menu_bar_title">Amount Due</td>
						<td class="menu_bar_title">ID Bank Movement</td>
						<td class="menu_bar_title">Ref Auto</td>
						<td class="menu_bar_title">Ref Custom</td>|;
					my $totalVendor = $varsvh{$idVendor}{'total'};
					my $refVendor = $varsvh{$idVendor}{'ref'};
					my $refAutoVendor = $varsvh{$idVendor}{'auto'};
					
					my $sql_add_refnum = "AND RefNum = '".&filter_values($refVendor)."'";
					
					if (!$err and !$refAutoVendor and !$refVendor and !$refVendor) {
						$error{'refnum'} = &trans_txt('required');
						++$err;
					}
					if (!$err and $refAutoVendor) {
					
						#Se verifica que no existe un registro con la misma informacion
						# 1  validar que los bills no esten pagados
						# 2 validar que no existe un movrel para bills con estos ID
						my $query = "SELECT `RefNum` +1 FROM `sl_banks_movements` WHERE 1 AND Type='Credits' AND doc_type='$in{'doc_type'}' AND ID_banks='".&filter_values($in{'id_banks'})."' ORDER BY cast(`RefNum` as unsigned) DESC LIMIT 1;";
						my ($sth_refnum) = &Do_SQL($query);
						my ($refAutoVendor) = $sth_refnum->fetchrow_array();
						$log .= "\n".$query;
						
						if (!$refAutoVendor){
							# $error{'refnum'} = &trans_txt('required');
							# ++$err;

							$in{'refnum'} = 1;
						}else{
							$in{'refnum'} = $refAutoVendor;
						}
						$sql_add_refnum = "AND RefNum = '".&filter_values($in{'refnum'})."'";
					}
					
					my $query = "SELECT COUNT(*) 
								FROM sl_banks_movements 
								WHERE 1 AND Type = 'Credits' 
								AND ID_banks = '".&filter_values($in{'id_banks'})."'
								AND BankDate = '".&filter_values($in{'bankdate'})."'
								AND doc_type = '".&filter_values($in{'doc_type'})."'
								$sql_add_refnum";
					my ($sth2) = &Do_SQL($query);
					my ($duplicate) = $sth2->fetchrow_array();
					$log .= "\n".$query;

					if (!$duplicate) {

						$log .= "\nSTART TRANSACTION;";
						&Do_SQL("START TRANSACTION;");

						my $add_amountcurrency = " AmountCurrency = NULL, ";
						$flag_calculate = 0;
						
						if ($cfg{'acc_default_currency'} ne $in{'currency'} and $in{'currency_exchange'} > 0) {

							$flag_calculate = 1;
							$amount_calculate = $totalVendor * $in{'currency_exchange'};
							$add_amountcurrency = " AmountCurrency = '$totalVendor', ";

						}
						
						###
						### Se obtiene la cuenta de banco del proveedor
						###
						my $sth_bnk = &Do_SQL("SELECT BankAccount FROM sl_vendors WHERE ID_vendors = ".int($idVendor).";");
						my $bank_account = $sth_bnk->fetchrow();
						my $sql_bank_account = '';
						if( $bank_account ){
							$sql_bank_account = " RefBankAccount = '*".substr($bank_account, -5)."', ";
						}

						my $add_amount = ($flag_calculate) ? $amount_calculate : $totalVendor;
						my $sql_refnumcustom = ($refVendor)? " RefNumCustom = '".&filter_values($refVendor)."', ":" RefNumCustom =NULL, ";
						my $query = "INSERT INTO sl_banks_movements SET
									ID_banks= '".&filter_values($in{'id_banks'})."',
									TYPE = 'Credits', 
									doc_type = '".$in{'doc_type'}."',
									BankDate = '".&filter_values($in{'bankdate'})."',
									RefNum = '".&filter_values($in{'refnum'})."', 
									$sql_refnumcustom
									$sql_bank_account
									Memo  = '".&filter_values($in{'memo'})."', 
									Amount = '".$add_amount."',
									$add_amountcurrency
									currency_exchange = '".$in{'currency_exchange'}."',
									DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'";
						my ($sth) = &Do_SQL($query);
						$id_banks_movements = $sth->{'mysql_insertid'};
						$log .= "\n".$query;
						$log .= "\nNew ID_banks_movements: ".$id_banks_movements;
						$va{'id_banks_movements'} = $id_banks_movements;

						if ($sth->rows() == 1) {

							$in{'db'} = "sl_banks_movements";
							&auth_logging('fin_banks_movements_added', $id_banks_movements);
							
							foreach my $k(keys $varsvh{$idVendor}{'bill'}){

								my $log_foreach = '';
								my $id_bills = int($k);
								my $vcat;
								my $this_type;
								my $this_vendor_currency;
								
								my $query = "SELECT COUNT(*) FROM sl_bills WHERE ID_bills = '".$k."' AND Status = 'To Pay'";
								my ($sthvalid) = &Do_SQL($query);
								$totalbill = $sthvalid->fetchrow;
								$log_foreach = "\n".$query;
								
								if($varsvh{$idVendor}{'bill'}{$k} > 0 and $totalbill == 1){

									$va{'bill_amount_due_after'} = &bills_amount_due($k);
									$va{'searchresultapply'} .= qq| <tr>
									<td><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$k\">$k</a></td>
									<td>|.&format_price($varsvh{$idVendor}{'bill'}{$k}).qq|</td>
									<td>|.&format_price($va{'bill_amount_due_after'}).qq|</td>
									<td><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$id_banks_movements\">$id_banks_movements</a></td>
									<td>$in{'refnum'}</td>
									<td>$refVendor</td>
									</tr> |;

									my $query = "INSERT INTO sl_banks_movrel SET 
												ID_banks_movements = '$id_banks_movements', 
												tablename = 'bills', 
												tableid = '".$k."', 
												AmountPaid = '".$varsvh{$idVendor}{'bill'}{$k}."',
												DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'";
									my ($sth) = &Do_SQL($query);
									my ($this_movrel) = $sth->{'mysql_insertid'};
									$id_banks_movrel .= $this_movrel.',';
									$va{'bill_amount_due'} = &bills_amount_due($k);
									$log_foreach .= "\n".$query;
									$log_foreach .= "\nNew ID_banks_movrel: ".$id_banks_movrel.", Bill Amount Due: ".$va{'bill_amount_due'};

									###-----------------------------------------------
									### Genera el sql para actualizar el metodo
									### de pago del bill
									###-----------------------------------------------
									my $qry_pmt_method = '';
									if( $in{'doc_type'} ne 'NA' ){
										$qry_pmt_method = ", PaymentMethod = '".$in{'doc_type'}."'";
									}
									###-----------------------------------------------

									if ($va{'bill_amount_due'} == 0){

										my $query = "UPDATE sl_bills SET Status = 'Paid' $qry_pmt_method WHERE ID_bills = '".$k."' LIMIT 1;";
										my ($sth2) = &Do_SQL($query);
										$log_foreach .= "\n".$query;

										# Log
										$in{'db'} = "sl_bills";
										&auth_logging('bills_paid',$k);

										###-------------------------------------------------------
										## Se actualiza el campo Paid en purchaseorders_adj
										###-------------------------------------------------------
										&payment_po_adj($k);
										###-------------------------------------------------------

									}elsif($va{'bill_amount_due'} > 0){

										my $query = "UPDATE sl_bills SET Status = 'Partly Paid' $qry_pmt_method WHERE ID_bills = '".$k."' LIMIT 1;";
										my ($sth2) = &Do_SQL($query);
										$log_foreach .= "\n".$query;

										# Log
										$in{'db'} = "sl_bills";
										&auth_logging('bills_partial_payment',$k);
									}

									my $query = "SELECT Type FROM sl_bills WHERE ID_bills = '".$k."'";
									my ($sthsql) = &Do_SQL($query);
									my ($typeBills) = $sthsql->fetchrow_array();
									$log_foreach .= "\n".$query." ==> result: ".$typeBills;

									if($typeBills eq 'Deposit' or $typeBills eq  'Debit'){

										my $str_pos;
										########################################################
										########################################################
										## Movimientos de contabilidad
										########################################################
										########################################################
										my $amount_remaining = $varsvh{$idVendor}{'bill'}{$k};
										my $id_vendors = &load_name('sl_bills','ID_bills', $k, 'ID_vendors');
										my $vendor_category = &load_name('sl_vendors','ID_vendors', $id_vendors,'Category');
										my $bill_type = &load_name('sl_bills','ID_bills', $k, 'Type');
										$in{'currency_exchange'} = 0 if !$in{'currency_exchange'};
										my @params = ($id_vendors, $k, $ida_banks,$in{'bankdate'}, $amount_remaining, $in{'currency_exchange'});
										#&cgierr('vendor_' . lc($bill_type) . '_' . lc($vendor_category) . " $id_vendors,$ida_banks,$amount_remaining,$in{'currency_exchange'} ");
										&accounting_keypoints('vendor_' . lc($bill_type) . '_' . lc($vendor_category), \@params );

										my $str_params = join(', ', @params);
										$log_foreach .= "\nKey Point: vendor_".lc($bill_type) . '_' . lc($vendor_category).", Params: ".$str_params;

									}
									else{

										#
										#Contabilidad
										#
										#
										my $x = 0;my $str_pos;my $str_bills;my $str;
										
										my $amount = $varsvh{$idVendor}{'bill'}{$k};
										my $amount_derived = $amount;
										my $pct_derived = 1;
										
										my $amt_negative = 0;
										
										#################################
										#################################
										## PO o Expense?
										#################################
										#################################

										my $query = "SELECT ID_vendors
														, Category
														, IF(ID_purchaseorders > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders,0) AS ID_po
														, IF(ID_bills_expenses > 0 AND sl_bills_expenses.Amount > 0,ID_bills_expenses,0) AS ID_expense
														, IF(ID_purchaseorders_adj > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders_adj,0) AS ID_po_adj
														, $amount / sl_bills.Amount 
														, sl_vendors.Currency
													FROM sl_bills 
														INNER JOIN sl_vendors USING(ID_vendors) 
														LEFT JOIN sl_bills_pos USING(ID_bills) 
														LEFT JOIN sl_bills_expenses USING(ID_bills) 
													WHERE sl_bills.ID_bills = '".$id_bills."' 
													HAVING ID_po > 0 OR ID_expense > 0 OR ID_po_adj > 0 
													ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;";
										$log_foreach .= "\n".$query;
										my ($sth) = &Do_SQL($query);
										my $rows = $sth->rows();
										while(my($id_vendors, $vendor_category, $id_po, $id_expenses, $id_po_adj, $paid_pct, $vendor_currency) = $sth->fetchrow()) {

											++$x;
											(!$vcat) and ($vcat = $vendor_category);
											$this_vendor_currency = $vendor_currency;
											
											if($id_po) {

												(!$this_type) and ($this_type = 'po');
												($x == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_pos'));
												##################
												##################
												### Pago de PO
												##################
												##################
												my ($sth) = &Do_SQL("SELECT  
																	SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) / SUM(Amount) AS PctPaid , 
																	( (SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
																	FROM sl_bills_pos WHERE ID_bills = '". $id_bills ."';");
												my($pct , $this_pct) = $sth->fetchrow();

												my $this_amount = $x < $rows ? round($this_pct * $amount ,3) : $amount_derived;
												$amount_derived -= $this_amount;
												$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

												my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$in{'currency_exchange'}, $id_po_adj);
												($this_acc_st, $this_acc_str) = &accounting_keypoints('po_payment_'. lc($vendor_category), \@params );
												my $exchange_rate = $in{'currency_exchange'} > 0 ? $in{'currency_exchange'} : 1;
												&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $in{'currency_exchange'}\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
												$str_pos .= "$id_po,";

												$this_acc_flag++ if $this_acc_st;
												$log .= qq|\nAcc: $this_acc_str|;

												my $str_params = $str_params = join(', ', @params);
												$log_foreach .= "\nPO Payment ==> Key Point: po_payment_".lc($vendor_category).", Params: ".$str_params;

											}elsif($id_expenses){

												(!$this_type) and ($this_type = 'expenses');
												($x == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_expenses'));
												##################
												##################
												### Pago de Expense
												##################
												##################
												my ($sth) = &Do_SQL("SELECT 
																	SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) / SUM(Amount) AS PctPaid,
																	( (SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
																	FROM sl_bills_expenses WHERE ID_bills = '". $id_bills ."';");
												my($pct, $this_pct) = $sth->fetchrow();

												my $this_amount = $x < $rows ? round($this_pct * $amount ,3) : $amount_derived;
												$amount_derived -= $this_amount;
												$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

												my @params = ($id_bills,$ida_banks,$this_amount,$this_pct,$in{'currency_exchange'});
												&accounting_keypoints('bills_expenses_payment_'. lc($vendor_category), \@params );
												my $exchange_rate = $in{'currency_exchange'} > 0 ? $in{'currency_exchange'} : 1;
												&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $in{'currency_exchange'}\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
												$str_bills .= "$id_bills,";
												
												my $str_params = $str_params = join(', ', @params);
												$log_foreach .= "\nExpenses Payment ==> Key Point: bills_expenses_payment_".lc($vendor_category).", Params: ".$str_params;

											}else{
												(!$this_type) and ($this_type = 'po_adj'); 
												($x == $rows ) and ($amt_negative = &load_bill_amt_negative($id_bills,'sl_bills_pos'));
												##################
												##################
												### Pago de PO_Adj
												##################
												##################
												my ($sth) = &Do_SQL("SELECT  
																		SUM(IF(ID_purchaseorders_adj = '$id_po_adj',Amount,0)) / SUM(Amount) AS PctPaid , 
																		((SUM(IF(ID_purchaseorders_adj = '$id_po_adj',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
																	 FROM sl_bills_pos 
																	 WHERE ID_bills = '". $id_bills ."';");
												my($pct , $this_pct) = $sth->fetchrow();

												my $this_amount = $x < $rows ? round($this_pct * $amount ,3) : $amount_derived;
												$amount_derived -= $this_amount;
												$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

												$id_po = &load_name("sl_purchaseorders_adj", "ID_purchaseorders_adj", $id_po_adj, "ID_purchaseorders");
												my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$in{'currency_exchange'}, $id_po_adj);
												&accounting_keypoints('po_payment_'. lc($vendor_category), \@params );
												my $exchange_rate = $in{'currency_exchange'} > 0 ? $in{'currency_exchange'} : 1;
												&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po_adj', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $in{'currency_exchange'}\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
												$str_pos .= "$id_po,";

												my $str_params = $str_params = join(', ', @params);
												$log_foreach .= "\nPO-Adj Payment ==> Key Point: po_payment_".lc($vendor_category).", Params: ".$str_params;
											}

										}									
										chop($str_pos);
										chop($str_bills);									

										########################################
										### Se liga bills con banks_movements
										########################################	
										my $modquery = '';
										my $modquery_bills_pos = '';
										if( $str_pos ne '' ){										
											$modquery = "ID_tableused IN ($str_pos) AND tableused = 'sl_purchaseorders' AND";	
											$modquery_bills_pos = ", Reference = 'BM:$id_banks_movements'";
										}else{
											if( $str_bills ne '' ){											
												$modquery = "ID_tableused IN ($str_bills) AND tableused = 'sl_bills' AND";
											}
											$modquery_bills_pos = ", tablerelated = 'sl_banks_movements' , ID_tablerelated = '$id_banks_movements' ";
										}
										#my $modquery = $str_pos ne '' ? "ID_tableused IN ($str_pos) AND tableused = 'sl_purchaseorders'" : "ID_tableused IN ($str_bills) AND tableused = 'sl_bills'";
										my $query_to_paid = "UPDATE sl_movements SET EffDate = '".&filter_values($in{'bankdate'})."', ID_journalentries = 0 $modquery_bills_pos WHERE $modquery TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 15 AND ID_admin_users = '$usr{'id_admin_users'}';";
										&Do_SQL($query_to_paid);									
										##Fin contabilidad

										$log_foreach .= "\n".$query_to_paid;
									}
									
									
									##################
									##################
									### Pago de Expense
									##################
									##################
									if($this_type eq 'expenses' and $vcat and $this_vendor_currency ne $cfg{'acc_default_currency'}){

										##########
										########## Revision de Expense Pagado
										##########
										my @params = ($id_bills);
										#&cgierr('bills_'. $this_type .'_paid_' . lc($vcat) . " -- $id_expenses,0,$ida_deposit,$this_amount,$currency_exchange,$pct");
										&accounting_keypoints('bills_'. $this_type .'_paid_' . lc($vcat), \@params );

										my $str_params = $str_params = join(', ', @params);
										$log_foreach .= "\nExpenses Payment ==> Key Point: bills_".$this_type.'_paid_' . lc($vcat).", Params: ".$str_params;

									}
									
									#########
									######### Guardamos en sl_vars temporalmente. Datos pueden ser utilizados si se quiere cancelar un movimiento bancario o un pago de bill especifico
									#########
									my ($sqlloop) = "SELECT GROUP_CONCAT(DISTINCT ID_movements) 
													FROM sl_movements WHERE 
														EffDate = '$in{'bankdate'}' 
														AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 30 
														AND ( 
																(ID_tableused = '$id_bills' AND tableused = 'sl_bills') 
																OR 
																(ID_tablerelated = '$id_bills' AND tablerelated = 'sl_bills') 
														);";
									my ($sth6) = &Do_SQL($sqlloop);
									my ($movements) = $sth6->fetchrow(); 
									&Do_SQL("INSERT INTO sl_vars (VName, VValue, Subcode, Definition_En, Comment_En ) VALUES ('Bank_Movements_Applied', '$id_banks_movements', '$id_bills', '$movements', DATE_ADD(CURDATE(), INTERVAL 3 MONTH) );");

								}

								## Log Debug
								&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('fin_payment_bills', '$id_bills', '".&filter_values($log.$log_foreach)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

							}
							
						}
						
						chop($id_bills_paid) if($id_bills_paid ne '');
						chop($id_bills_nopaid) if($id_bills_nopaid ne '');
						chop($id_banks_movrel) if($id_banks_movrel ne '');

						&Do_SQL("COMMIT");
						
					}else {
						## Enviar mensaje de error, no se puede procesar un pago que ya fue procesado
						$va{'messages'} = &trans_txt('bills_notprocess');
						delete($in{'process'});
					}
					
					$va{'searchresultapply'} .= qq|</table></td></tr>|;
					if( &check_permissions($in{'cmd'},'_print','') and lc($in{'doc_type'}) eq 'check' and $va{'id_banks_movements'} ){
						$va{'btn_print_check'} = '<a class="button" href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=fin_banks_movements&search=Print&toprint='.$va{'id_banks_movements'}.'" target="_blank" name="btnPrint" style="padding: 7px;">Print Check</a>';
					}
				}

			}

		}else{

			if($val_dc_amount_bill eq ''){

				$flag=1;
				$va{'messages'} = &trans_txt('bills_required');
				$va{'messages'} = &trans_txt('bills_amount_invalid') if ($va{'bills_total_amount'} <= 0);
				$va{'messages'} = &trans_txt('bills_amounts_not_match') if ($va{'bills_total_amount'} > $va{'bills_total_amount_due'});
				delete($in{'process'});
			
			}

		}

		$va{'totalsinput'} = 0;
		$va{'display3'} = '';

	}
	
	if($in{'action'}){

		$va{'display3'} = 'display:none;';
		$va{'display'} = 'display:none;';
		$va{'display2'} = '';
		my ($query);
		
		if($in{'id_vendors'}){
			$query .= " AND ID_vendors = ".&filter_values($in{'id_vendors'})." ";
			$in{'doc_type'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"PaymentMethod") if (!$in{'doc_type'});
		}
		
		if($in{'currency'}){
			$query .= " AND Currency = '".&filter_values($in{'currency'})."' ";
		}

		if($in{'id_bills'} ){
			$query .= " AND ID_bills = ".&filter_values($in{'id_bills'})." ";
		}
		
		if($in{'duedate'}){
			$query .= " AND DueDate >= '".&filter_values($in{'duedate'})."' ";
			if($in{'toduedate'}){
				$query .= " AND DueDate <= '".&filter_values($in{'toduedate'})."' ";
			}
		}
		if($in{'from_amount'}){
			$query .= " AND Amount >= '".&filter_values($in{'from_amount'})."' ";
		}

		if($in{'to_amount'}){
			$query .= " AND Amount <= '".&filter_values($in{'to_amount'})."' ";
		}
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) 
			FROM  sl_bills as bills
			WHERE bills.Status IN('To Pay')
			
			AND (SELECT IFNULL(bills.Amount - (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')
					) + (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Debit')
					) - (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Credits'
					) + (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Debits'
					), 0)
					) > 0 
			AND Amount > 0 $query ");
		$va{'matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		if ($va{'matches'}) { 
			my ($sth) = &Do_SQL("SELECT bills.ID_vendors,sl_vendors.CompanyName
				FROM  sl_bills as bills
				INNER JOIN (SELECT ID_vendors, CompanyName FROM sl_vendors)sl_vendors ON sl_vendors.ID_vendors=bills.ID_vendors
				WHERE bills.Status IN('To Pay')
				AND bills.`Type` IN('Bill', 'Deposit')
				AND ( Amount - (
					SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')
					) + (
					SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Debit')
					) - (
					SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Credits'
					) + (
					SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Debits'
					)
				) > 0 
				AND Amount > 0 
				$query GROUP by bills.ID_vendors ORDER BY sl_vendors.CompanyName ");
			$select_creddep = '';
			my @totalAmount;
			my @vendorList;
			my @json ;
			while($rec = $sth->fetchrow_hashref) {
				$i++;
				$vendors = $rec->{'CompanyName'};
				$select_creddep .= qq|<option value="|.$rec->{'ID_bills'}.qq|">|.$rec->{'ID_bills'}.qq|</option>|;
				$d = 1 - $d;
				if(!&in_array(\@vendorList, $rec->{'ID_vendors'})){
					push(@vendorList, $rec->{'ID_vendors'});
					$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]'>
						<td><img id="link_$rec->{'ID_vendors'}" class="collapse" style="cursor:pointer;" src="/sitimages/icon-collapse-plus.gif"  /> <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>
						<td><input type="text" name="ref-$rec->{'ID_vendors'}" id="refVendor_$rec->{'ID_vendors'}" class="refnum" /> <input type="checkbox" value="1" name="num_auto-$rec->{'ID_vendors'}" class="refauto" id="refauto_$rec->{'ID_vendors'}" /> 
						<label for="refnum_auto">Auto</label></td>
						<td id="amountTotal_$rec->{'ID_vendors'}" align="right"></td>
						<td id="amountDueTotal_$rec->{'ID_vendors'}" align="right"></td>
						<td><input type="text" id="valueVendorAmount_$rec->{'ID_vendors'}" readonly="readonly"  class="amountVendorTotal" name="amount-$rec->{'ID_vendors'}" /></td>
					</tr>
					|;
					my ($sth) = &Do_SQL("SELECT *
					,( Amount - (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')
						) + (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Debit')
						) - (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Credits'
						) + (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Debits'
						)
					)as AmountAvailable 
					FROM  sl_bills as bills
					WHERE bills.Status IN('To Pay')
					AND ID_vendors = '$rec->{'ID_vendors'}'
					
					AND ( Amount - (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Deposit','Credit')
						) + (
						SELECT IFNULL(SUM(sl_bills_applies.Amount),0)as Amount FROM sl_bills_applies INNER JOIN sl_bills USING(ID_bills) WHERE ID_bills_applied = bills.ID_bills AND sl_bills.Type IN ('Debit')
						) - (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Credits'
						) + (
						SELECT IFNULL(SUM(AmountPaid),0) as Amount FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements) WHERE 1 AND tablename = 'bills' AND tableid = bills.ID_bills AND type = 'Debits'
						)
					) > 0 
					AND Amount > 0 
					$query ORDER BY DueDate");
					$idVendor = $rec->{'ID_vendors'};
					$va{'searchresults'} .= qq|<tr id="list_$rec->{'ID_vendors'}" style="display:none;">
					<td colspan="5">
					<table border="0" cellspacing="0" cellpadding="2" class="gborder" align="center" width="90%">
						<td class="menu_bar_title">ID Bill
						<input type="hidden" id="collapse_$rec->{'ID_vendors'}" value="close" />
						</td>
						<td class="menu_bar_title">&nbsp;</td>
						<td class="menu_bar_title">Due Date</td>
						<td class="menu_bar_title">Currency</td>
						<td class="menu_bar_title">Type</td>
						<td class="menu_bar_title">Amount</td>
						<td class="menu_bar_title">Amount Due</td>
						<td class="menu_bar_title">&nbsp;</td>
						<td class="menu_bar_title">&nbsp;</td>|;
					while($rec = $sth->fetchrow_hashref){
						my ($inputdisabled);
						if($rec->{'Type'} eq 'Deposit' or $rec->{'Type'} eq 'Debit'){
							$inputdisabled = 'readonly="readonly"';
						}
						$a = 1 - $a;
						$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$a]'>
						<td><input type="checkbox" class="checkbill checkbill_$idVendor check_$idVendor" id="check_$rec->{ID_bills}" /></td>
						<td ><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{ID_bills}</a></td>
						<td >$rec->{DueDate}</td>
						<td >$rec->{Currency}</td>
						<td >$rec->{Type}</td>
						<td align="right">|.&format_price($rec->{Amount}).qq|</td>
						<td align="right"><span style="color:#ff0f0f;cursor:pointer;" onclick="print_amount('value_$rec->{ID_bills}', $rec->{AmountAvailable})">|.&format_price($rec->{AmountAvailable}).qq|</span><input type="hidden" id="valueAmountDue_$rec->{ID_bills}" value="$rec->{AmountAvailable}" class="classAmountDue_$idVendor a" /> </td>
						<td><input type="number" class="valueIdVendor_$idVendor inputBill" id="value_$rec->{ID_bills}" disabled="disabled" name="bill-$idVendor#$rec->{ID_bills}" $inputdisabled /></td>
						<td style="color:#ff0f0f;" width="12%" id="error_$rec->{ID_bills}"></td>
						</tr>|;
						
						$json{$idVendor}{'Amount'} += $rec->{'Amount'};
						$json{$idVendor}{'AmountDue'} += $rec->{'AmountAvailable'};
						
						$va{'totalsinput'} +=  $rec->{AmountAvailable};
						
					}
					$json{$idVendor}{'AmountDue'} = &format_price($json{$idVendor}{'AmountDue'});
					$json{$idVendor}{'Amount'} = &format_price($json{$idVendor}{'Amount'});
					$va{'searchresults'} .= qq| </td></table></tr>|;
				}
			}
		}
		$va{'currency'} = $in{'currency'};
		$va{bills_amount_invalid} = &trans_txt('bills_amount_invalid');
		$va{'json'} = encode_json \%json;
		$va{'button_e'} = qq| <input type="button" class="button" value="Export File" id="btn_export_02" style="display:">
								<input type="button" class="button" value="Export File SPEI" id="btn_export_04" style="display:">
								&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|;
		$va{'button_p'} = qq| <input type="submit" class="button" value="Pay Bills" id="btn_pay" style="display:">|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page("fin_payment_bills.html");	
}

sub payment_po_adj{
	my($id_bill) = @_;

	# Se obtiene el currency del proveedor del PO al que corresponden los gastos(adj)
	$sthProv = &Do_SQL("SELECT Currency
						FROM sl_purchaseorders_adj
							INNER JOIN sl_bills_pos ON sl_purchaseorders_adj.ID_purchaseorders_adj = sl_bills_pos.ID_purchaseorders_adj
							INNER JOIN sl_vendors ON sl_purchaseorders_adj.ID_vendors = sl_vendors.ID_vendors
						WHERE sl_bills_pos.ID_bills = ".$id_bill."
						LIMIT 1;");
	my $currency_vendor = $sthProv->fetchrow();	

	# Se obtiene el listado de los gastos(adj) que se están pagando con el bill actual
	my $sth = &Do_SQL("SELECT 
							sl_purchaseorders_adj.ID_purchaseorders_adj,
							sl_purchaseorders_adj.Amount_original,
							sl_purchaseorders_adj.Total,
							sl_purchaseorders_adj.TotalOriginal,
							sl_purchaseorders_adj.`Status`,
							sl_bills_pos.Amount AS AmountBill
						FROM sl_purchaseorders_adj
							INNER JOIN sl_bills_pos ON sl_purchaseorders_adj.ID_purchaseorders_adj = sl_bills_pos.ID_purchaseorders_adj
						WHERE sl_bills_pos.ID_bills = ".$id_bill.";");
	while ( $rec = $sth->fetchrow_hashref() ) {
		my $amount_adj = 0;
		if( $currency_vendor eq 'MX$' ){
			if( $rec->{'TotalOriginal'} > 0 ){
				$amount_adj = round($rec->{'TotalOriginal'},2);
			}elsif( $rec->{'Status'} eq "Processed" or $rec->{'Status'} eq "Active" ){
				$amount_adj = $rec->{'Amount_original'};
			}
		}else{
			$amount_adj = $rec->{'Total'};
		}

		# se obtiene el monto total pagado en otros bills del gasto(adj) actual
		$sth2 = &Do_SQL("SELECT SUM(sl_bills_pos.Amount) TotalPaid
						 FROM sl_bills_pos
							INNER JOIN sl_bills USING(ID_bills)
						 WHERE sl_bills_pos.ID_purchaseorders_adj = ".$rec->{'ID_purchaseorders_adj'}."
						 	AND sl_bills.ID_bills <> ".$id_bill."
							AND sl_bills.`Status` = 'Paid'
						 GROUP BY sl_bills_pos.ID_purchaseorders_adj;");
		my $amount_adj_paid = $sth2->fetchrow();
		$amount_adj_paid = 0 if( !$amount_adj_paid );

		my $total_amount_paid = round($rec->{'AmountBill'} + $amount_adj_paid,2);

		#&cgierr("Currency: ".$currency_vendor.", amount_adj: ".$amount_adj." -> total_amount_paid: ".$total_amount_paid.", amount_adj_paid: ".$amount_adj_paid);
		if( $total_amount_paid >= $amount_adj ){
			&Do_SQL("UPDATE sl_purchaseorders_adj
						SET Paid = 1 
					 WHERE ID_purchaseorders_adj = ".$rec->{'ID_purchaseorders_adj'}.";");
		}

	}

}


############################################################################################
############################################################################################
#	Function: fin_payment_bills_layouts
#
#   	ES: Genera Layout bancario para pagos masivos
#
#	Created by: _RB_
#		
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub fin_payment_bills_layouts {
############################################################################################
############################################################################################


	if($in{'action'} and $in{'id_banks'}){

		$va{'message'} = '';
		my $txt_data;
		&load_cfg('sl_banks');
		my (%bankinfo) = &get_record('ID_banks', $in{'id_banks'},'sl_banks');
		$bankinfo{'bankname'} = lc($bankinfo{'bankname'});

		## Generacion de layout
		my $text_data = &get_layout_load_bank_payments(0,0,$in{'hd_layout_extraction_type'});
		
		if(!$va{'message'}){
			

			## Impresion de archivo CSV
			my $f = lc($cfg{"app_title"}) . '_' . lc($bankinfo{'shortname'}) . '_' . &get_sql_date();		
			$f =~ s/ /_/g;

			print "Content-Disposition: attachment; filename=$f.txt;";
			print "Content-type: text/text\n\n";
			print $text_data;
			return;

		}
				

	}elsif($in{'action'} and !$in{'id_banks'}){

		$err{'id_banks'} = &trans_txt('required');

	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_payment_bills_layouts.html');

}

1;

