#!/usr/bin/perl
####################################################################
########              Home Page                     ########
####################################################################

###############################################################
############             EXTENSION SUBS         ###############
###############################################################

sub build_grpcheckbox {
# --------------------------------------------------------
	my ($perm) = @_;
	my (@ary) = split(/,/, $perm);
	my ($output,$output_tabs,$checkmark);
	for (0..$#ary){
		$checkmark = '';
		if ($ary[$_] =~ /(.+)_add$/){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			$output .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> Add &nbsp;</span>";
		}elsif  ($ary[$_] =~ /(.+)_view$/){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			$output .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> View &nbsp;</span>";
		}elsif  ($ary[$_] =~ /(.+)_edit$/){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			$output .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> Edit &nbsp;</span>";
		}elsif  ($ary[$_] =~ /(.+)_del$/){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			$output .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> Del &nbsp;</span>";
		}elsif  ($ary[$_] =~ /(.+)_tab(\d+)$/){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			($2 eq 1) and ($output_tabs .= "<br>");
			$output_tabs .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> Tab $2 &nbsp;</span>";
		}elsif($ary[$_]){
			($in{'perm'} =~ /$ary[$_]=on/) and ($checkmark = 'checked');
			$output .= "<span style='white-space:nowrap'><input type='checkbox' $checkmark name='perm_$ary[$_]' value='on' class='checkbox'> $ary[$_] &nbsp;</span>"
		}
	}
	return $output . $output_tabs;
}

sub load_new_prodid {
# --------------------------------------------------------
	################
	### REVISAR
	################
	my ($first) = 100000;
	while (!$in{'id_products'}){
		my ($sth) = &Do_SQL("SELECT ID_products FROM sl_products WHERE ID_products>=$first;");
		$in{'id_products'} = $sth->fetchrow + 1;
		$first = $in{'id_products'};
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_products='$in{'id_products'}';");
		if ($sth->fetchrow >0){
			delete($in{'id_products'});
		}
	}
}

sub gen_passwd {
# --------------------------------------------------------
# Form: validate_man_users in dbman.html.cgi
# Service: 
# Type : subroutine
# Time Last : 9/06/2007 4:34PM
# Author: Rafael Sobrino
# Description : generates a 6-character (upper/lower alpha + numeric) random password 

	my ($len) = 6;		# length of the random password
	my @chars=('a'..'z','A'..'Z','0'..'9','_');
	my ($password);
	foreach (1..$len){
		$password.=$chars[rand @chars];
	}
	return $password;	
}

sub monterey_order {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Carlos Haas
# Description : 
# Last Modification by JRG : 03/11/2009 : Se agrega log

	my ($end_date_num,$np_date_num,$from_fnmty,$order) = @_;
	my ($status,%pdata,$num,@cols,$err,$errmsg,$aux);
	my ($debug) = 0;
	my ($null_return)= "......\n";
	
	###  cols (0"Contract ID",1"Sale Amount",2"Down Payment",3"Original Term",4"Remaining Term (Months)",5"Note Date",6"Amount Financed",
	###		7"Remaining Principal Balance Amount",8"Date of First Payment",9"Date of Last Payment",10"Credit Card Number",11"Expiration Date",
	###    12"Last Name",13"First Name",14"Middle Initial",15"Address 1",16"Address 2",17"City",18"State",19"Zip",20"Country",21"Home Phone",
	###    22"Work Phone",23"Carrier (UPS FED EX etc.)",24"Tracking Number",25"Monthly payment amount",26"Date of next payment",
	###    27"Product description");

	if ($order->{'dayspay'} eq 20){
		$err = "20 Days";
	}elsif ($order->{'dayspay'} eq 15 and $order->{'ID_orders'} > 69429){
		$err = "15 Days";
	}elsif ($order->{'dayspay'} eq ''){
		$err = "No dayspay";
	} 

	#$status = &check_ord_totals($order->{'ID_orders'});
	$status = 'OK';
	if ($status eq 'OK'){
		### Count Payments
		my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled')");
		($payments,$tot_ord) = $sth2->fetchrow_array();		
		if ($payments>1){
			## Do nothing
		}else{
			$err = "Paid in Full";
		}
		
		### Check Returns
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE Status NOT IN ('Void','Resolved') AND ID_orders_products IN (SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$order->{'ID_orders'}')");
		if ($sth2->fetchrow>0){
			$err = "Returns in Process";
		}

		### Load Payments
		my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') ORDER BY PaymentDate ASC");
		PAY:while ($rec = $sth2->fetchrow_hashref()){
			if ($rec->{'Status'} eq 'Denied'){
				$err = "Denied Payment";
			}
			if ($rec->{'Status'} eq 'Financed'){
				$err = "Financed Payment";
			}
			if ($rec->{'PmtField1'} eq 'Visa' or  $rec->{'PmtField1'} eq 'Mastercard'){
				## Do nothing
			}else{
				$err = "Only Visa and MC";
				$errmsg = $rec->{'PmtField1'};
			}
		
			++$num;
			$pdata{$rec->{'Paymentdate'}}{'Amount'} = $rec->{'Amount'};
			$pdata{$rec->{'Paymentdate'}}{'card'} = $rec->{'PmtField1'};
			$pdata{$rec->{'Paymentdate'}}{'Status'} = $rec->{'Status'};
			$pdata{$rec->{'Paymentdate'}}{'ID_orders_payments'} = $rec->{'ID_orders_payments'};
			$pdata{$num}=$rec->{'Paymentdate'};
			$pdata{'totorder'} += $rec->{'Amount'};
			if ($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000'){
				$pdata{$rec->{'Paymentdate'}}{'paid'} = 'yes';
				$pdata{'paid'} += $rec->{'Amount'};
				$pdata{'lastpaid'}=$rec->{'Paymentdate'};
			}else{
				if (&date_to_unixtime($rec->{'Paymentdate'})<$end_date_num){ 
					$pdata{$rec->{'Paymentdate'}}{'paid'} = 'sltv';
					$pdata{'paid'} += $rec->{'Amount'};
					#&cgierr(" $order->{'ID_orders'} $rec->{'Paymentdate'} : ".&date_to_unixtime($rec->{'Paymentdate'})." $end_date_num ");
				}else{
					$pdata{$rec->{'Paymentdate'}}{'paid'} = 'no';
					$pdata{'unpaid'} += $rec->{'Amount'};
					++$pdata{'unpaidqty'};
					(!$pdata{'nextpayment'}) and ($pdata{'nextpayment'}=$rec->{'Paymentdate'});
				}
			}
			if ($num eq 1) {
				### Load Customer Info ###
				my ($sth3) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$order->{'ID_customers'}'");
				$customer = $sth3->fetchrow_hashref();
				##"Credit Card Number","Expiration Date","Last Name","First Name","Middle Initial","Address 1","Address 2","City","State","Zip","Country","Home Phone","Work Phone","Carrier (UPS FED EX etc.)","Tracking Number","Monthly payment amount","Date of next payment","Product description"
				@cols[10..21] = ($rec->{'PmtField3'},$rec->{'PmtField4'},$customer->{'LastName1'},$customer->{'FirstName'},' ',$order->{'Address1'},$order->{'Address2'},$order->{'City'},$order->{'State'},$order->{'Zip'},'USA',$rec->{'PmtField6'},$customer->{'Phone1'},);
					
				my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$order->{'ID_orders'}' AND Status='Active' ORDER BY Shpdate ASC");
				while ($tmp = $sth3->fetchrow_hashref()){
					if (!$cols[23] and !$cols[24]){
						$cols[23] = $tmp->{'ShpProvider'};
						$cols[24] = $tmp->{'Tracking'};
					}
					if ($tmp->{'ID_products'}){
						$cols[27] .= &load_db_names('sl_products','ID_products',substr($tmp->{'ID_products'},3,6),'[Name] [Model], ');
					}else{
						$cols[27] .= $tmp->{'ID_products'};
					}
				}
			}elsif ($num>=3){
				#if ($pdata{$pdata{2}}{'Amount'} ne $rec->{'Amount'}){
				#	($debug) and (return "2,$pdata{$pdata{2}}{'Amount'} ne $rec->{'Amount'},$order->{'ID_orders'},$order->{'OrderNet'},Differents Payments,$pdata{1},$pdata{$pdata{1}}{'Amount'},$pdata{2},$pdata{$pdata{2}}{'Amount'},$pdata{3},$pdata{$pdata{3}}{'Amount'},$rec->{'Amount'}");
				#	return $null_return;
				#}
			}
		}

		if ($err and $from_fnmty){
			($debug) and (return "Debug:$debug,$err,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'}");
			return $null_return;
		}elsif($pdata{'unpaid'}<=0 and $from_fnmty){
			($debug) and (return "Paid in Full,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
			return $null_return;
		}elsif($pdata{'unpaid'}>0){
			@cols[0..7] = ($order->{'ID_orders'},$pdata{'totorder'},$pdata{$pdata{1}}{'Amount'},$num,$pdata{'unpaidqty'},$order->{'Date'},$pdata{'totorder'}-$pdata{$pdata{1}}{'Amount'},$pdata{'unpaid'});
			$cols[25] = $pdata{$pdata{$num}}{'Amount'};
			$cols[26] = $pdata{'nextpayment'};
			$cols[8] = $pdata{2};
			$cols[9] = $pdata{'lastpaid'};
			for (0..$#cols){
				$cols[$_] =~ s/,|"//g;  #"
				$cols[$_] =~ s/á/a/g;
				$cols[$_] =~ s/é/e/g;
				$cols[$_] =~ s/í/i/g;
				$cols[$_] =~ s/ó/o/g;
				$cols[$_] =~ s/ú/u/g;
				$cols[$_] =~ s/Á/A/g;
				$cols[$_] =~ s/É/E/g;
				$cols[$_] =~ s/Í/I/g;
				$cols[$_] =~ s/Ó/O/g;
				$cols[$_] =~ s/Ú/U/g;
				$cols[$_] =~ s/ñ/n/g;
				$cols[$_] =~ s/Ñ/N/g;
			}			
			##
			##if ($num % 2 == 1){
			##	return '';
			##	     return "$order->{'ID_orders'}   ????";
			##}elsif 
			if ($order->{'dayspay'} eq 30){
				($debug) and ($cols[0] = "$cols[0] 30days");
				####}elsif ($order->{'ID_orders'} > 35250 and $order->{'ID_orders'}<54177 and $pdata{'unpaidqty'}==1){
				FP:for my $i(1..$num){
					if ($pdata{$i} eq $cols[26]){
						if ($pdata{$pdata{$i+1}}{'paid'} ne 'yes'){
							##$cols[0] = "$cols[0] impar1";
							#$cols[26] = $pdata{$i+1};
						}
						last FP;
					}
				}
			}elsif ((($order->{'dayspay'} eq 15 or $order->{'ID_orders'} > 35250 and $order->{'ID_orders'}<54177) or $order->{'ID_orders'}>56596) and ($pdata{'unpaidqty'} % 2) == 1 and $pdata{'unpaidqty'}>1){
				########}elsif ($order->{'ID_orders'} > 35250 and $order->{'ID_orders'}<54177 and $pdata{'unpaidqty'} % 2 == 1 and $pdata{'unpaidqty'}>1){
				$a='';
				FP:for my $i(1..$num){
					if ($pdata{$i} eq $cols[26]){
						$a .= " $pdata{$i} eq $cols[26] ## $pdata{$pdata{$i-1}}{'paid'} ## $pdata{$i+1} ## $pdata{$i-1}";
						if ($pdata{$pdata{$i-1}}{'paid'} eq 'yes'){
							$cols[26] = $pdata{$i+1};
							$cols[7] -= $pdata{$pdata{$i+1}}{'Amount'};
							$pdata{$pdata{$i+1}}{'paid'} = 'no';
							#$cols[25] -= 2;
							#$pdata{'unpaidqty'} -= 2;
							
						}else{
							$cols[26] = $pdata{$i-1};
							$cols[7] += $pdata{$pdata{$i-1}}{'Amount'};
							$pdata{$pdata{$i-1}}{'paid'} = 'no';
						}
						last FP;
					}
				}
				($debug) and ($cols[0] = "$cols[0] impar");
				$cols[3] = $cols[3]/2 ; #Original Term
				$cols[4] = ($pdata{'unpaidqty'}+1)/2 ; #Remaining Term (Months)
				$cols[25] = $cols[25]*2 ; #Monthly payment amount
				#($debug) and (return "8,$order->{'ID_orders'},$order->{'OrderNet'},Impar,$cols[3],$cols[4],$cols[25],$a ");
				#return '';		
				## Re
			}elsif(($order->{'ID_orders'} > 35250 and $order->{'ID_orders'}<54177) or $order->{'ID_orders'}>56596){
				##}elsif($order->{'ID_orders'} > 35250 and $order->{'ID_orders'}<54177){
				($debug) and ($cols[0] = "$cols[0] par 15 ");
				$cols[3] = $cols[3]/2 ; #Original Term
				$cols[4] = $cols[4]/2 ; #Remaining Term (Months)
				$cols[25] = $cols[25]*2 ; #Monthly payment amount
				FP:for my $i(1..$num){
					if ($pdata{$i} eq $cols[26]){
						$cols[26] = $pdata{$i+1};
						last FP;
					}
				}
			}
			if ($cols[3] ne int($cols[3]) and $cols[4] eq 1){
				$cols[3] = $cols[3]*2;
			}
			
			if ($cols[4] ne int($cols[4]) or $cols[3] ne int($cols[3])){
				$err = "Invalid Terms";
				$errmsg = "$cols[4] ne int($cols[4]) or $cols[3] ne int($cols[3])";
			}
			if ($cols[4]>12){
				$err = "Too Many Months";
				$errmsg = "Remaining Month";
			}
			if (&date_to_unixtime($cols[26])>$np_date_num){ 
				$err = "Next Payment to far";
				$errmsg = "$cols[26]";
			}

			$sth3 = &Do_SQL("SELECT if(CapDate ='0000-00-00','',CapDate) FROM sl_orders_payments WHERE ID_orders = '".$cols[0]."'
											AND sl_orders_payments.AuthCode IS NOT NULL
											AND sl_orders_payments.AuthCode != ''
											AND sl_orders_payments.AuthCode != '0000'
											ORDER BY AuthDateTime DESC LIMIT 1");
			$cols[9]=$sth3->fetchrow;
			
			### make Payment Even
			$cols[25] = int($cols[7]/$cols[4]*100)/100;
			$cols[7]  = $cols[25]*$cols[4];


			if ($from_fnmty){
				if ($cols[25]<20){
					$err = "Payment to Small";
					$errmsg = "Payment Amount";
				}
				if ($cols[7]>3000){
					$err = "Balance Due to Big";
					$errmsg = "Balance Due to Big";
				}
				
				if ($cols[7]>1500 and &date_to_unixtime($cols[5])>&date_to_unixtime('2008-06-30')){
					$err = "Balance Due to Big";
					$errmsg = "Balance Due to Big";
				}
				#if ($cols[7]<1500){
				#	$err = "Amount < 1500";
				#	$errmsg = "Payment Amount";					
				#}
				if ($cols[4]>=5 and $cols[7]<300){
					$err = "Invalid Amount/Terms";
					$errmsg = "Invalid Amount/Terms";
				}
				if ($cols[4]<2){
					$err = "Low Payments Left";
					$errmsg = "Payment Amount";
				}
				
				#### Fix First?last  Payment 
				if (&date_to_unixtime($cols[8])>&date_to_unixtime($cols[9])){
					$cols[8] = $cols[5];
				}
			}
			
			## Update Status
			if($from_fnmty){
				if ($err){
					($debug) and (return "$err,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
					return $null_return;
				}elsif(!$in{'testmode'}){
					$in{'fintotal'} += $cols[7];
					if ($in{'fintotal'}>$in{'limit'} and $in{'limit'}){
						exit 1;
					}
					for my $i(1..$num){
						if ($pdata{$pdata{$i}}{'paid'} eq 'no'){
							my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET Status='Financed',Captured='Yes',CapDate='$in{'capdate'}' WHERE ID_orders_payments='$pdata{$pdata{$i}}{'ID_orders_payments'}'");
							&auth_logging('orders_payments_updated',$order->{'ID_orders'});
						}
					}
					my ($sth2) = &Do_SQL("INSERT INTO sl_orders_plogs SET Data='Monterey Payments\nRemaining Term (Months)=$cols[4]\nAmount Financed=$cols[6]\nRemaining Principal Balance Amount=$cols[7]\nMonthly payment amount=$cols[25]\nDate of next payment=$cols[26]',ID_orders='$order->{'ID_orders'}',Date=Curdate(),Time=NOW(),ID_admin_users='$rec->{'ID_admin_users'}'");
					&auth_logging('opr_orders_plogadded',$order->{'ID_orders'});
				}
			}
			
			if ($debug){
				return "OK,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ,".join(',', @cols);
			}else{
				return join(',', @cols);
			}
			
			#$tot_unpaid += $unpaid;
			#$tot_ord = $tot_ord + $unpaid + $paid;
			#for (0..$#ids){
			#	my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET Status='Financed',Captured='Yes',CapDate=NOW() WHERE ID_orders_payments='$ids[$_]'");
			#}
		}else{
			($debug) and (return "Unpaid Restriction,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
			return $null_return;
		}
		#($lines>10) and (last IDORDEN);
	}else{
		($debug) and (return "Total Error,$order->{'ID_orders'},$order->{'OrderNet'},0,Total Error: $status");
		return $null_return;
	}
}


sub col_monterey_order {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Carlos Haas
# Description : 
# Last Modification by JRG : 03/11/2009 : Se agrega el log

	my ($end_date_num,$np_date_num,$order) = @_;
	my ($status,%pdata,$num,@cols,$err,$errmsg,$aux);
	my ($debug) = 0;
	my ($null_return)= "......\n";
	
	###  cols (0"Contract ID",1"Sale Amount",2"Down Payment",3"Original Term",4"Remaining Term (Months)",5"Note Date",6"Amount Financed",
	###		7"Remaining Principal Balance Amount",8"Date of First Payment",9"Date of Last Payment",10"Credit Card Number",11"Expiration Date",
	###    12"Last Name",13"First Name",14"Middle Initial",15"Address 1",16"Address 2",17"City",18"State",19"Zip",20"Country",21"Home Phone",
	###    22"Work Phone",23"Carrier (UPS FED EX etc.)",24"Tracking Number",25"Monthly payment amount",26"Date of next payment",
	###    27"Product description");

	### Count Payments
	my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled')");
	($payments,$tot_ord) = $sth2->fetchrow_array();		
	if ($payments>1){
		## Do nothing
	}else{
		$err = "Paid in Full";
	}
	
	### Check Returns
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE Status NOT IN ('Void','Resolved') AND ID_orders_products IN (SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$order->{'ID_orders'}')");
	if ($sth2->fetchrow>0){
		$err = "Returns in Process";
	}

	### Load Payments
	my ($financed) = 0;
	my ($cfinanced) = 0;
	my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') ORDER BY PaymentDate ASC");
	PAY:while ($rec = $sth2->fetchrow_hashref()){
		if ($rec->{'Status'} eq 'On Collection'){
			$err = "Already On Collection";
		}elsif ($rec->{'Status'} eq 'Financed'){
			$financed = 1;
		}elsif ($rec->{'Status'} eq 'Counter Finance'){
			$cfinanced = 1;
		}
		if ($rec->{'PmtField1'} eq 'Visa' or  $rec->{'PmtField1'} eq 'Mastercard'){
			## Do nothing
		}else{
			#$err = "Only Visa and MC";
			#$errmsg = $rec->{'PmtField1'};
		}
	
		++$num;
		$pdata{$rec->{'Paymentdate'}}{'Amount'} = $rec->{'Amount'};
		$pdata{$rec->{'Paymentdate'}}{'card'} = $rec->{'PmtField1'};
		$pdata{$rec->{'Paymentdate'}}{'Status'} = $rec->{'Status'};
		$pdata{$rec->{'Paymentdate'}}{'ID_orders_payments'} = $rec->{'ID_orders_payments'};
		$pdata{$num}=$rec->{'Paymentdate'} if ($rec->{'Paymentdate'}>0);
		(!$pdata{1} and $rec->{'Paymentdate'}>0) and ($pdata{1}=$rec->{'Paymentdate'});
		$pdata{'totorder'} += $rec->{'Amount'};
		if ($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000'){
			$pdata{$rec->{'Paymentdate'}}{'paid'} = 'yes';
			$pdata{'paid'} += $rec->{'Amount'};
			$pdata{'lastpaid'}=$rec->{'Paymentdate'};
		}else{
			if (&date_to_unixtime($rec->{'Paymentdate'})<$end_date_num){ 
				$pdata{$rec->{'Paymentdate'}}{'paid'} = 'sltv';
				$pdata{'paid'} += $rec->{'Amount'};
				#&cgierr(" $order->{'ID_orders'} $rec->{'Paymentdate'} : ".&date_to_unixtime($rec->{'Paymentdate'})." $end_date_num ");
			}else{
				$pdata{$rec->{'Paymentdate'}}{'paid'} = 'no';
				$pdata{'unpaid'} += $rec->{'Amount'};
				++$pdata{'unpaidqty'};
				(!$pdata{'nextpayment'}) and ($pdata{'nextpayment'}=$rec->{'Paymentdate'});
			}
		}
		if ($num eq 1) {
			### Load Customer Info ###
			my ($sth3) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$order->{'ID_customers'}'");
			$customer = $sth3->fetchrow_hashref();
			##"Credit Card Number","Expiration Date","Last Name","First Name","Middle Initial","Address 1","Address 2","City","State","Zip","Country","Home Phone","Work Phone","Carrier (UPS FED EX etc.)","Tracking Number","Monthly payment amount","Date of next payment","Product description"
			@cols[10..21] = ($rec->{'PmtField3'},$rec->{'PmtField4'},$customer->{'LastName1'},$customer->{'FirstName'},' ',$order->{'Address1'},$order->{'Address2'},$order->{'City'},$order->{'State'},$order->{'Zip'},'USA',$rec->{'PmtField6'},$customer->{'Phone1'},);
				
			my ($sth3) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$order->{'ID_orders'}' AND Status='Active' ORDER BY Shpdate ASC");
			while ($tmp = $sth3->fetchrow_hashref()){
				if (!$cols[23] and !$cols[24]){
					$cols[23] = $tmp->{'ShpProvider'};
					$cols[24] = $tmp->{'Tracking'};
				}
				if ($tmp->{'ID_products'}){
					$cols[27] .= &load_db_names('sl_products','ID_products',substr($tmp->{'ID_products'},3,6),'[Name] [Model], ');
				}else{
					$cols[27] .= $tmp->{'ID_products'};
				}
			}
		}elsif ($num>=3){
			#if ($pdata{$pdata{2}}{'Amount'} ne $rec->{'Amount'}){
			#	($debug) and (return "2,$pdata{$pdata{2}}{'Amount'} ne $rec->{'Amount'},$order->{'ID_orders'},$order->{'OrderNet'},Differents Payments,$pdata{1},$pdata{$pdata{1}}{'Amount'},$pdata{2},$pdata{$pdata{2}}{'Amount'},$pdata{3},$pdata{$pdata{3}}{'Amount'},$rec->{'Amount'}");
			#	return $null_return;
			#}
		}
	}

	## Check for Financed and Not Counter Financed
	if ($cfinanced and !$cfinanced){
		$err = "Financed Order";
	}

	if ($err){
		($debug) and (return "Debug,$err,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'}");
		return $null_return;
	}elsif($pdata{'unpaid'}<=0){
		($debug) and (return "Paid in Full,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
		return $null_return;
	}elsif($pdata{'unpaid'}>0){
		@cols[0..7] = ($order->{'ID_orders'},$pdata{'totorder'},$pdata{$pdata{1}}{'Amount'},$num,$pdata{'unpaidqty'},$order->{'Date'},$pdata{'totorder'}-$pdata{$pdata{1}}{'Amount'},$pdata{'unpaid'});
		$cols[25] = $pdata{$pdata{$num}}{'Amount'};
		$cols[26] = $pdata{'nextpayment'};
		$cols[8] = $pdata{2};
		$cols[9] = $pdata{'lastpaid'};
		for (0..$#cols){
			$cols[$_] =~ s/,|"//g;  #"
			$cols[$_] =~ s/á/a/g;
			$cols[$_] =~ s/é/e/g;
			$cols[$_] =~ s/í/i/g;
			$cols[$_] =~ s/ó/o/g;
			$cols[$_] =~ s/ú/u/g;
			$cols[$_] =~ s/Á/A/g;
			$cols[$_] =~ s/É/E/g;
			$cols[$_] =~ s/Í/I/g;
			$cols[$_] =~ s/Ó/O/g;
			$cols[$_] =~ s/Ú/U/g;
			$cols[$_] =~ s/ñ/n/g;
			$cols[$_] =~ s/Ñ/N/g;
		}			

		$sth3 = &Do_SQL("SELECT if(CapDate ='0000-00-00','',CapDate) FROM sl_orders_payments WHERE ID_orders = '".$cols[0]."'
										AND sl_orders_payments.AuthCode IS NOT NULL
										AND sl_orders_payments.AuthCode != ''
										AND sl_orders_payments.AuthCode != '0000'
										ORDER BY AuthDateTime DESC LIMIT 1");
		$cols[9]=$sth3->fetchrow;
		


		#### Fix First?last  Payment 
		if (&date_to_unixtime($cols[8])>&date_to_unixtime($cols[9])){
			$cols[8] = $cols[5];
		}

		
		## Update Status
		if ($error){
			($debug) and (return "$error,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
			return '';
		}elsif(!$in{'testmode'}){
			my ($st_type);
			($in{'tcollection'} eq 'sko') and ($st_type = 'On Collection');
			($in{'tcollection'} eq 'mty') and ($st_type = 'On Collection MTY');
			$in{'fintotal'} += $cols[15];
			if ($in{'fintotal'}>$in{'limit'} and $in{'limit'}){
				exit 1;
			}
			for my $i(1..$num){
				if ($pdata{$pdata{$i}}{'paid'} eq 'no'){
					my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET Status='$st_type',
					CapDate=Curdate(),Captured='Yes' WHERE ID_orders_payments='$pdata{$pdata{$i}}{'ID_orders_payments'}'");
					&auth_logging('orders_payments_updated',$order->{'ID_orders'});
				}
			}				
			#my ($sth2) = &Do_SQL("UPDATE sl_orders SET");
			my ($sth3) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders=$order->{'ID_orders'}, Data='Sent to $st_type:\nTotal Sent : ".&format_price($cols[15])." ',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			&auth_logging('opr_orders_plogadded',$order->{'ID_orders'});
		}
		if ($debug){
			return "OK,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ,".join(',', @cols);
		}else{
			return join(',', @cols);
		}

	}else{
		($debug) and (return "Unpaid Restriction,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
		return $null_return;
	}
}

sub col_sko_order {
# --------------------------------------------------------	
# Last Modification by JRG : 03/11/2009 : Se agrega log
	my ($end_date_num,$np_date_num,$order) = @_;
	my ($status,%pdata,$num,@cols,$error,$errmsg);
	my ($debug) = 0;
	my ($source_sale) = 'Phone';
	$pdata{'firstpayment'} = '';
	$pdata{'firstpaymentex'} = '';
	
	
	###  0"Contract ID",1"PhoneSale/WebSale",2"Last Name",3"First Name",4"Middle Initial",5"Address 1",
	###  6"Address 2",7"City",8"State",9"Zip",10"Country",11"Home Phone",12"Work Phone",13"email",
	###	 14"Original Amount,15"Current Balance",16"OrderDate","17"ShpDate",18"Product Code",19"Product Name",
	###	 20"CreditCard",21"#Pagos,22"ShpProvider",23"Tracking,
	###  24"First Payment",25"Last Paid",26"First Payment Expired"

	#### sl_orders  = 0,1,5,6,7,8,9,(10),16,19
	#### sl_customers = 2,3,4,11,12,13
	#### sl_orders_products = 15,17,22,23
	#### sl_orders_payments = 14,20,21,24,25,26
	#### sl_products = 18


	$status = &check_ord_totals($order->{'ID_orders'});
	if ($status eq 'OK'){
		### Count Payments
		my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled')");
		($payments,$tot_ord) = $sth2->fetchrow_array();		
		if ($payments>1){
			## Do nothing
		}else{
			$error = "Paid in Full";
		}
		
		### Check Returns
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE Status NOT IN ('Void','Resolved') AND ID_orders_products IN (SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$order->{'ID_orders'}')");
		if ($sth2->fetchrow>0){
			$error = "Returns in Process";
		}

		### Load Payments
		my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$order->{'ID_orders'}' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled','On Collection','Financed','Counter Finance') ORDER BY PaymentDate ASC");
		PAY:while ($rec = $sth2->fetchrow_hashref()){
			++$num;
			$pdata{$rec->{'Paymentdate'}}{'Amount'} = $rec->{'Amount'};
			$pdata{$rec->{'Paymentdate'}}{'card'} = $rec->{'PmtField1'};
			$pdata{$rec->{'Paymentdate'}}{'Status'} = $rec->{'Status'};
			$pdata{$rec->{'Paymentdate'}}{'ID_orders_payments'} = $rec->{'ID_orders_payments'};
			$pdata{$num}=$rec->{'Paymentdate'};
			$pdata{'totorder'} += $rec->{'Amount'};
			if ($rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000' and $rec->{'Captured'} eq 'Yes'){
				$pdata{$rec->{'Paymentdate'}}{'paid'} = 'yes';
				$pdata{'paid'} += $rec->{'Amount'};
				$pdata{'lastpaid'}=$rec->{'Paymentdate'};
				$pdata{'cc'}= $rec->{'PmtField1'};
				($pdata{'firstpayment'} eq '') and ($pdata{'firstpayment'} = $rec->{'CapDate'});
			}else{
				$pdata{$rec->{'Paymentdate'}}{'paid'} = 'no';
				$pdata{'unpaid'} += $rec->{'Amount'};
				++$pdata{'unpaidqty'};
				(!$pdata{'nextpayment'}) and ($pdata{'nextpayment'}=$rec->{'Paymentdate'});
				($pdata{'firstpaymentex'} eq '') and ($pdata{'firstpaymentex'} = $rec->{'Paymentdate'});
			}
			
			if ($num eq 1) {
				### Load Customer Info ###
				my ($sth3) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$order->{'ID_customers'}'");
				$customer = $sth3->fetchrow_hashref();
				
				## Load Shipment Info ###
				my ($sth4) = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6) AS ID_products, sl_orders_parts.ShpDate, sl_orders_parts.ShpProvider, sl_orders_parts.Tracking 
					FROM sl_orders_products 
					LEFT JOIN sl_orders_parts ON sl_orders_parts.ID_orders_products=sl_orders_products.ID_orders_products 
					WHERE ID_orders =  '$order->{'ID_orders'}' AND  sl_orders_parts.ShpDate IS NOT NULL AND  sl_orders_parts.ShpDate <> '' AND  sl_orders_parts.ShpDate != '0000-00-00' AND sl_orders_products.Status != 'Cancelled' ORDER BY  sl_orders_parts.ShpDate LIMIT 1");
				$shipp = $sth4->fetchrow_hashref();
				
				$product_name =  &load_name('sl_products','ID_products',$shipp->{'ID_products'},'Name');
				@cols[1..13] = ($source_sale,$customer->{'LastName1'},$customer->{'FirstName'},'',$order->{'Address1'},$order->{'Address2'},$order->{'City'},$order->{'State'},$order->{'Zip'},'USA',$rec->{'PmtField6'},$customer->{'Phone1'},$customer->{'Email'});
			}
		}

		if ($error){
			($debug) and (return "$error,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'}");
			return '';
		}elsif($pdata{'unpaid'}>0){
			$cols[0] = $order->{'ID_orders'};
			#$cols[24] = $pdata{'lastpaid'};
			for (0..$#cols){
				$cols[$_] =~ s/,|"//g;  #"
				$cols[$_] =~ s/á/a/g;
				$cols[$_] =~ s/é/e/g;
				$cols[$_] =~ s/í/i/g;
				$cols[$_] =~ s/ó/o/g;
				$cols[$_] =~ s/ú/u/g;
				$cols[$_] =~ s/Á/A/g;
				$cols[$_] =~ s/É/E/g;
				$cols[$_] =~ s/Í/I/g;
				$cols[$_] =~ s/Ó/O/g;
				$cols[$_] =~ s/Ú/U/g;
				$cols[$_] =~ s/ñ/n/g;
				$cols[$_] =~ s/Ñ/N/g;
			}
			$cols[14] = $pdata{'paid'}+$pdata{'unpaid'};
			$cols[15] = $pdata{'unpaid'};
			$cols[16] = $order->{'Date'};
			$cols[17] = $shipp->{'ShpDate'};
			$cols[18] = $shipp->{'ID_products'};
			$cols[19] = $product_name;
			$cols[20] = $pdata{'cc'};
			$cols[21] = $num;
			$cols[22] = $shipp->{'ShpProvider'};
			$cols[23] = $shipp->{'Tracking'};
			$cols[24] = $pdata{'firstpayment'};
			$cols[25] = $pdata{'lastpaid'};
			$cols[26] = $pdata{'firstpaymentex'};
			
			## Update Status
			if ($error){
				($debug) and (return "$error,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
				return '';
			}elsif(!$in{'testmode'}){
				$in{'fintotal'} += $cols[15];
				if ($in{'fintotal'}>$in{'limit'} and $in{'limit'}){
					exit 1;
				}
				for my $i(1..$num){
					if ($pdata{$pdata{$i}}{'paid'} eq 'no'){
#						my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET Status='$st_type',
#						CapDate=Curdate(),Captured='Yes' WHERE ID_orders_payments='$pdata{$pdata{$i}}{'ID_orders_payments'}'");
#						&auth_logging('orders_payments_updated',$order->{'ID_orders'});
					}
				}				
#				#my ($sth2) = &Do_SQL("UPDATE sl_orders SET");
#				my ($sth3) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders=$order->{'ID_orders'}, Data='Sent to $st_type:\nTotal Sent : ".&format_price($cols[15])." ',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
#				&auth_logging('opr_orders_plogadded',$order->{'ID_orders'});
			}
			
			if ($debug){
				return "OK,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ,".join(',', @cols);
			}else{
				return join(',', @cols);
			}
			
		}else{
			($debug) and (return "Unpaid Restriction,$order->{'ID_orders'},$order->{'OrderNet'},$pdata{'unpaid'},$errmsg ");
			return "";
		}
		#($lines>10) and (last IDORDEN);
	}else{
		($debug) and (return "Total Error,$order->{'ID_orders'},$order->{'OrderNet'},0,Total Error: $status");
		return '';
	}
}


sub check_payments_qty {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Carlos Haas
# Description : 

	my ($order) = @_;
	my ($status,%pdata,$num,@cols,$financed);
	###  cols (0"Contract ID",1"Sale Amount",2"Down Payment",3"Original Term",4"Remaining Term (Months)",5"Note Date",6"Amount Financed",
	###		7"Remaining Principal Balance Amount",8"Date of First Payment",9"Date of Last Payment",10"Credit Card Number",11"Expiration Date",
	###    12"Last Name",13"First Name",14"Middle Initial",15"Address 1",16"Address 2",17"City",18"State",19"Zip",20"Country",21"Home Phone",
	###    22"Work Phone",23"Carrier (UPS FED EX etc.)",24"Tracking Number",25"Monthly payment amount",26"Date of next payment",
	###    27"Product description");

	### Count Payments
	my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND Status  IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
	($payments,$tot_ord) = $sth2->fetchrow_array();		
	($payments>1) or (return ('1','GOOD',$tot_ord,'0','0'));

	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-5 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied','Pending')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE Amount>0 AND  ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
		$unpaid = $sth2->fetchrow();
		return ($payments,'BAD'.$duepmts,($tot_ord-$unpaid),$unpaid);
	}else{
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE Amount>0 AND ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
		$unpaid = $sth2->fetchrow();
		return ($payments,'GOOD',($tot_ord-$unpaid),$unpaid);
	}
}

sub print_payments_qty {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Carlos Haas
# Description : 

	my ($order,$prnlist) = @_;
	my ($status,%pdata,$num,@cols,$financed);
	###  cols (0"Contract ID",1"Sale Amount",2"Down Payment",3"Original Term",4"Remaining Term (Months)",5"Note Date",6"Amount Financed",
	###		7"Remaining Principal Balance Amount",8"Date of First Payment",9"Date of Last Payment",10"Credit Card Number",11"Expiration Date",
	###    12"Last Name",13"First Name",14"Middle Initial",15"Address 1",16"Address 2",17"City",18"State",19"Zip",20"Country",21"Home Phone",
	###    22"Work Phone",23"Carrier (UPS FED EX etc.)",24"Tracking Number",25"Monthly payment amount",26"Date of next payment",
	###    27"Product description");

	### Count Payments
	my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND Status  IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
	($payments,$tot_ord) = $sth2->fetchrow_array();		
	($payments>1) or (return '');

	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-5 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied','Pending')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0 and $prnlist eq 'bad'){
		#&cgierr(" SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-5 AND Paymentdate<>'0000-00-00') AND (Captured<>'Yes' OR ISNULL(Captured) OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied','Pending')");
		my ($sth2) = &Do_SQL("SELECT Date,Amount,Paymentdate FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
		while (($date,$amount,$paymentdate) = $sth2->fetchrow_array()){
			print "$order,$date,$amount,$paymentdate\n";
		}
	}else{
		
		my ($sth2) = &Do_SQL("SELECT Date,Amount,Paymentdate FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection','On Collection MTY')");
		while (($date,$amount,$paymentdate) = $sth2->fetchrow_array()){
			print "$order,$date,$amount,$paymentdate\n";
		}
		#$unpaid = $sth2->fetchrow();
		#return ($payments,'GOOD',($tot_ord-$unpaid),$unpaid);
	}

}



sub check_payments_dates {
# --------------------------------------------------------	
# Form: 
# Service: 
# Type : subroutine
# Time Last : 9/05/2007 4:34PM
# Author: Carlos Haas
# Description : validates an email address

	my ($order) = @_;
	my ($status,%pdata,$num,@cols,$duepmts,$unpaid);
	###  cols (0"Contract ID",1"Sale Amount",2"Down Payment",3"Original Term",4"Remaining Term (Months)",5"Note Date",6"Amount Financed",
	###		7"Remaining Principal Balance Amount",8"Date of First Payment",9"Date of Last Payment",10"Credit Card Number",11"Expiration Date",
	###    12"Last Name",13"First Name",14"Middle Initial",15"Address 1",16"Address 2",17"City",18"State",19"Zip",20"Country",21"Home Phone",
	###    22"Work Phone",23"Carrier (UPS FED EX etc.)",24"Tracking Number",25"Monthly payment amount",26"Date of next payment",
	###    27"Product description");

	### Count Payments
	my ($sth2) = &Do_SQL("SELECT COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled')");
	my ($payments,$tot_ord) = $sth2->fetchrow_array();		
	($payments>1) or (return ('1',$tot_ord,'0'));


	## Test
	#my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<-5 AND Paymentdate<>'0000-00-00') AND (Captured<>'Yes' OR ISNULL(Captured) OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')");
	#$duepmts = $sth2->fetchrow_array();
	#if ($duepmts>=3){
	#	print "$payments $tot_ord : SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-90 AND Paymentdate<>'0000-00-00') AND (Captured<>'Yes' OR ISNULL(Captured) OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')<br><br>";
	#}
	## Financed
	#my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND Status = 'Financed'");
	#$duepmts = $sth2->fetchrow_array();
	#if ($duepmts>0){
	#	my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
	#	$unpaid = $sth2->fetchrow();
	#	return ($payments,'90',($tot_ord-$unpaid),$unpaid);
	#}
	

	## Over 90 Days
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
		$unpaid = $sth2->fetchrow();
		return ($payments,'90',($tot_ord-$unpaid),$unpaid);
	}

	## Over 60-90 Days
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
		$unpaid = $sth2->fetchrow();
		return ($payments,'60',($tot_ord-$unpaid),$unpaid);
	}
	## Over 30-60 Days
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
		$unpaid = $sth2->fetchrow();
		return ($payments,'30',($tot_ord-$unpaid),$unpaid);
	}	
	## Over 5-30 Days
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<-5 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied')");
	$duepmts = $sth2->fetchrow_array();
	if ($duepmts>0){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
		$unpaid = $sth2->fetchrow();
		#if (($tot_ord-$unpaid)<0){
		#	print "$order<br>";
		#}
		return ($payments,'5',($tot_ord-$unpaid),$unpaid);
	}	

	### Good Debt
	my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
	$unpaid = $sth2->fetchrow();
	return ($payments,'GOOD',($tot_ord-$unpaid),$unpaid);

}

#JRG start 23-06-2008
sub build_listpayments{
# --------------------------------------------------------
# Forms Involved: products_tab2
# Created on: 06/20/2008 13:00 PM
# Last Modified on:
# Last Modified by:
# Author: Jose Ramirez Garcia
# Description : it shows the distinct payments
# Parameters :
	## Items List
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}'");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT DISTINCT * FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' GROUP BY PmtField3, Status ORDER BY Status");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			if ($rec->{'Type'} eq "Check"){
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>P/C</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";
				$va{'searchpayresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
				}
				$va{'searchpayresults'} .= "   </td>"; 
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>$rec->{'PmtField4'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title' colspan='5'>WesterUnion Payment</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";
				$va{'searchpayresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';

				}
				$va{'searchpayresults'} .= "   </td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";	
			}elsif($rec->{'Type'} eq "Credit-Card"){

				(!&check_permissions('view_info_tdc','','')) and ($rec->{'PmtField3'} = 'xxxx-xxxx-xxxx-'.substr($rec->{'PmtField3'},-4));
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Exp</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>CVN</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$va{'searchpayresults'} .= " </tr>\n";
				$va{'searchpayresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
				}
				$va{'searchpayresults'} .= "   </td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField4'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField5'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";
			}else{
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Pay Form</td>\n";	
				$va{'searchpayresults'} .= "   <td class='menu_bar_title' colspan='2'>Manual Payment</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status</td>\n";	
				$va{'searchpayresults'} .= " </tr>\n";
				$va{'searchpayresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' nowrap>$rec->{'Type'}</td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' nowrap>$rec->{'PmtField1'}</td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top' colspan='2'> No Extra Information Required for This Type of Payment</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";
			}
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchpayresults'} = qq|
		    <tr>
				<td colspan='8' class='menu_bar_title' align="center">&nbsp;</td>
			</tr>
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $va{'searchpayresults'};
}
#JRG end 23-06-2008

sub build_listpayments_preorders{
#-----------------------------------------
# Created on: 11/05/08  12:52:29 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	## Items List
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_preorders_payments WHERE ID_preorders='$in{'id_preorders'}'");
	$va{'matches'} = $sth->fetchrow;
	if($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT DISTINCT * FROM sl_preorders_payments WHERE ID_preorders='$in{'id_preorders'}' GROUP BY PmtField3, Status ORDER BY Status");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			if ($rec->{'Type'} eq "Check"){
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>P/C</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";
				$va{'searchpayresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
				}
				$va{'searchpayresults'} .= "   </td>"; 
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>$rec->{'PmtField4'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField8'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField5'}<br> $rec->{'PmtField6'}<br>$rec->{'PmtField7'}<br>$rec->{'PmtField9'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title' colspan='5'>WesterUnion Payment</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";
				$va{'searchpayresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';

				}
				$va{'searchpayresults'} .= "   </td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";							
				$va{'searchpayresults'} .= "</tr>\n";	
			}elsif($rec->{'Type'} eq "Credit-Card" or $rec->{'Type'} eq "Layaway"){ 
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Exp</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>CVN</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status<br>Cod Auth</td>\n";			
				$va{'searchpayresults'} .= " </tr>\n";
				$va{'searchpayresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td nowrap>";
				if ($rec->{'Status'} eq 'Cancelled'){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
				}
				$va{'searchpayresults'} .= "   </td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField4'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField5'}</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";
			}else{
				$va{'searchpayresults'} .= "<tr>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Pay Form</td>\n";	
				$va{'searchpayresults'} .= "   <td class='menu_bar_title' colspan='2'>Manual Payment</td>\n";
				$va{'searchpayresults'} .= "	<td class='menu_bar_title'>Status</td>\n";	
				$va{'searchpayresults'} .= " </tr>\n";
				$va{'searchpayresults'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchpayresults'} .= "   <td>&nbsp;</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' nowrap>$rec->{'Type'}</td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' nowrap>$rec->{'PmtField1'}</td>";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top' colspan='2'> No Extra Information Required for This Type of Payment</td>\n";
				$va{'searchpayresults'} .= "   <td class='smalltext' $decor valign='top'> $rec->{'Status'}<br>$rec->{'AuthCode'}</td>\n";
				$va{'searchpayresults'} .= "</td>\n";
				$va{'searchpayresults'} .= "</tr>\n";
			}
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchpayresults'} = qq|
		    <tr>
				<td colspan='8' class='menu_bar_title' align="center">&nbsp;</td>
			</tr>
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $va{'searchpayresults'};
}



########################################################################
########################################################################
#
#	Function: update_mediacontracts
#   		Reset sl_orders, sl_leads_calls ID_orders, ID_mediacontracts, ID_order_assign, ID_mediacontracr_assign rows
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_mediacontracts : ID_mediacontracts
#		- estday esttime: Old Date
#		- edit_estday: New Date
#
#   	Returns:
#
#   	See Also:
#
sub mediacontracts_edit_estday{
#########################################################################


	my $dest_did_ni = 9996;
	my $original_date = $in{'old_dates'};
	my $new_date = "$in{'estday'} $in{'esttime'}";
	my $didusa = load_name('sl_mediadids','didmx',$in{'destinationdid'},'didusa');
	my ($orders_edited,$orders_assigned,$l1,$leads_assigned);


	my ($sth) = &Do_SQL("SELECT IF(/* Backward */'$in{'estday'} $in{'esttime'}' < '$original_date',CONCAT('past;;$in{'estday'} $in{'esttime'};;',NextDate),
				IF(/* Forward */'$original_date' < '$new_date', CONCAT('future;;',LastDate,';;$in{'estday'} $in{'esttime'}') ,0) )
				FROM
					(SELECT $in{'destinationdid'} AS DID, CONCAT(ESTDay,' ',ESTTime)AS LastDate FROM sl_mediacontracts WHERE TIMESTAMPDIFF(SECOND, '$original_date' , CONCAT(ESTDay,' ',ESTTime) ) < 0 AND DestinationDID = '$in{'destinationdid'}' ORDER BY TIMESTAMPDIFF(SECOND, '$original_date' , CONCAT(ESTDay,' ',ESTTime)) DESC LIMIT 1)tmplast
				LEFT JOIN
					(SELECT $in{'destinationdid'} AS DID, CONCAT(ESTDay,' ',ESTTime)AS NextDate FROM sl_mediacontracts WHERE TIMESTAMPDIFF(SECOND, '$original_date' , CONCAT(ESTDay,' ',ESTTime) ) > 0 AND DestinationDID = '$in{'destinationdid'}' ORDER BY TIMESTAMPDIFF(SECOND, '$original_date' , CONCAT(ESTDay,' ',ESTTime)) LIMIT 1)tmpnext
				USING(DID);");

	my($dates) = $sth->fetchrow();

	## Date remain equal
	if(!$dates){
		return ;
	}

	@ary_dates = split(/;;/,$dates);
	my $from_date = $ary_dates[1];
	my $to_date = $ary_dates[2];

	
	my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");

	my $type = $ary_dates[0];
	## We need to know the contracts that affected orders that range
	## Fetching mediacontracts
	my $query = "SELECT GROUP_CONCAT(sl_mediacontracts.ID_mediacontracts) FROM sl_mediacontracts 
				INNER JOIN
							(
								SELECT DISTINCT ID_mediacontracts FROM sl_orders WHERE CONCAT(Date,' ',Time) BETWEEN '$from_date' AND '$to_date' 
							)tmp
				ON tmp.ID_mediacontracts = sl_mediacontracts.ID_mediacontracts
				WHERE DestinationDID = $in{'destinationdid'}  OR sl_mediacontracts.ID_mediacontracts = '$in{'id_mediacontracts'}' ;";
	my ($sth) = &Do_SQL($query);
	my ($id_mediacontracts_grouped) = $sth->fetchrow();
	$id_mediacontracts_grouped = $in{'id_mediacontracts'} if !$id_mediacontracts_grouped;

	if(!$id_mediacontracts_grouped){
		&send_text_mail($cfg{'cservice_email'},$cfg{'to_email_debug'},'Mediacontracts: Warning Mediacontracts',$query);
	}

	## Contratos no identificados
	my $query = "SELECT GROUP_CONCAT(ID_mediacontracts) FROM sl_mediacontracts WHERE DestinationDID = '$dest_did_ni' AND ESTDay >= DATE('$from_date') AND ESTDay < DATE('$to_date');";
	my ($sth) = &Do_SQL($query);
	my ($id_ni_grouped) = $sth->fetchrow();

	$id_mediacontracts_grouped .= ',' . $id_ni_grouped if $id_ni_grouped;

	## Grouping Orders (Incluye ordenes del contrato y contratos no identificados)
	$query = "SELECT GROUP_CONCAT(ID_orders) FROM sl_orders WHERE ID_mediacontracts IN($id_mediacontracts_grouped) AND DNIS='$in{'destinationdid'}' AND DIDS7='$didusa';";
	my ($sth) = &Do_SQL($query);
	my ($id_orders_grouped) = $sth->fetchrow();

	my($o1,$o2);
	if($id_orders_grouped) {

		## Order R1, R2
		$query = "SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_orders IN($id_orders_grouped) ORDER BY CONCAT(Date,' ',Time) LIMIT 1;";
		my ($sth) = &Do_SQL($query);
		$o1 = $sth->fetchrow();

		$query = "SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_orders IN($id_orders_grouped) ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
		my ($sth) = &Do_SQL($query);
		$o2 = $sth->fetchrow();

		$mod = "OR ID_orders IN($id_orders_grouped)
				OR ID_order_assign IN($id_orders_grouped) ";

	}

	## LeadCalls
	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE
				(DIDUS = '$didusa' AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				)
				$mod 
			ORDER BY CONCAT(Date,' ',Time) LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	my ($lc1) = $sth->fetchrow();

	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE 
				(DIDUS = '$didusa' AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				)
				$mod
			ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	my ($lc2) = $sth->fetchrow();


	#1) Reseting LeadCalls
	$query = "UPDATE sl_leads_calls SET 
				ID_order_assign = 0, 
				ID_orders = 0, 
				ID_mediacontract_assign = 0, 
				ID_mediacontracts = 0 
			WHERE 
				(DIDUS = '$didusa' AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				)
				$mod;";

	my ($sth) = &Do_SQL($query);
	my ($leads_edited) = $sth->rows();		

	###########################
	###########################
	#######
	###########################
	###########################

	if($id_orders_grouped){
		#2) Reseting Orders // Nota. Este punto es utilizado actualmente
		$query = "UPDATE sl_orders SET ID_mediacontracts = 0 WHERE ID_orders IN($id_orders_grouped);";
		my ($sth) = &Do_SQL($query);
		$orders_edited = $sth->rows();
	}

	if(!$orders_edited){
		&send_text_mail($cfg{'cservice_email'},$cfg{'to_email_debug'},'Mediacontracts: warning:orders_edited',$query);
	}

	if($id_mediacontracts_grouped){
		#3) Reseting Mediacontracts Status
		$query = "UPDATE sl_mediacontracts SET Status = 'Programado', MediaStatus='Open' WHERE ID_mediacontracts IN($id_mediacontracts_grouped);";
		my ($sth) = &Do_SQL($query);
	}

	
	require ('../../common/apps/leadsDids.cgi');
	#4) Reassigning Orders
	($orders_assigned,$l1) = &assign_orders($o1, $o2) if($o1 and $o2);
	#5) Reassigning Leads
	$leads_assigned = &assign_leads_no_order($lc1, $lc2) if ($lc1 and $lc2);
	$leads_assigned += $l1;

	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='$field edited\nOld:".$original_date."\nNew:".$new_date."\nDates Period: $from_date - $to_date\nContracts affected:$id_mediacontracts_grouped',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Data Changed\nOrders: $orders_assigned / $orders_edited\nLeads: $leads_assigned / $leads_edited',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

	#6) Updating Status
	&status_contracts($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

	#7) Ratios Summary
	&run_ratiossummary($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

	$in{'status'} = &load_name('sl_mediacontracts','ID_mediacontracts',$in{'id_mediacontracts'},'Status');

}



########################################################################
########################################################################
#
#	Function: update_mediacontracts
#   		Reset sl_orders, sl_leads_calls ID_orders, ID_mediacontracts, ID_order_assign, ID_mediacontracr_assign rows
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_mediacontracts : ID_mediacontracts
#		- in_reset: New DID
#		- destinationdid: Old DID
#
#   	Returns:
#
#   	See Also:
#
sub mediacontracts_edit_did{
#########################################################################

	my ($query);
	my $dest_did_ni=9996;
	my ($r1,$r2,$c1,$c2,$o1,$o2,$orders_edited);

	my $didusa_prev = load_name('sl_mediadids','didmx',$in{'destinationdid'},'didusa');
	my $didusa_new = load_name('sl_mediadids','didmx',$in{'edit_did'},'didusa');
	my $product_new = load_name('sl_mediadids','didmx',$in{'edit_did'},'product');
	my ($sth)=&Do_SQL("UPDATE sl_mediacontracts SET Offer = '$product_new' WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
	
	my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");

	## 1) Fechas 1a y ultima orden con ese contrato)
	my ($sth)=&Do_SQL("SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY CONCAT(Date,' ',Time) LIMIT 1;");		
	$r1 = $sth->fetchrow();
	$r1 = "$in{'estday'} $in{'esttime'}" if !$r1;

	my ($sth)=&Do_SQL("SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");		
	$r2 = $sth->fetchrow();

	# 2) Contratos nuevo DID Agrupados 
	my ($sth)=&Do_SQL("SELECT CONCAT(ESTDay,' ',ESTTime) FROM sl_mediacontracts WHERE DestinationDID = '$in{'edit_did'}'
						AND TIMESTAMPDIFF(SECOND, CONCAT(ESTDay,' ',ESTTime), '$r1' ) > 0 
						AND Status IN(". $cfg{'contract_valid_status'}.") 
						ORDER BY TIMESTAMPDIFF(SECOND, CONCAT(ESTDay,' ',ESTTime), '$r1' ) LIMIT 1;");		
	$c1 = $sth->fetchrow();


	## Si no hay fecha de orden ultima, buscar fecha de proximo contrato
	if(!$r2){
		my ($sth)=&Do_SQL("SELECT CONCAT(ESTDay,' ',ESTTime) FROM sl_mediacontracts WHERE DestinationDID = '$in{'edit_did'}'
						AND Status IN(". $cfg{'contract_valid_status'}.") 
						AND CONCAT(ESTDay,' ',ESTTime) > '$in{'estday'} $in{'esttime'}' ORDER BY CONCAT(Date,' ',Time) LIMIT 1;");		
		$r2 = $sth->fetchrow();
		$c2 = $r2;
	}else{


		my ($sth)=&Do_SQL("SELECT CONCAT(ESTDay,' ',ESTTime) FROM sl_mediacontracts WHERE DestinationDID = '$in{'edit_did'}'
							AND TIMESTAMPDIFF(SECOND, CONCAT(ESTDay,' ',ESTTime), '$r2' ) > 0 
							AND Status IN(". $cfg{'contract_valid_status'}.") 
							ORDER BY TIMESTAMPDIFF(SECOND, CONCAT(ESTDay,' ',ESTTime), '$r2' ) LIMIT 1;");	
		$c2 = $sth->fetchrow();
	}		

	my ($sth)=&Do_SQL("SELECT GROUP_CONCAT(DISTINCT ID_mediacontracts) FROM sl_mediacontracts 
	 					WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' OR (DestinationDID = '$in{'edit_did'}' 
	 					AND CONCAT(ESTDay,' ',ESTTime) BETWEEN '$c1' AND '$c2' 
	 					AND Status IN(". $cfg{'contract_valid_status'}.")) ;");
	my ($id_mediacontracts_grouped) = $sth->fetchrow();

	## Contratos no identificados
	my $query = "SELECT GROUP_CONCAT(ID_mediacontracts) FROM sl_mediacontracts WHERE DestinationDID = '$dest_did_ni' 
				AND ESTDay >= DATE('$c1') AND ESTDay <= DATE('$c2');";
	my ($sth) = &Do_SQL($query);
	my ($id_ni_grouped) = $sth->fetchrow();
	$id_mediacontracts_grouped .= ',' . $id_ni_grouped if $id_ni_grouped;


	#3) Ordenes Agrupadas
	my ($sth)=&Do_SQL("SELECT GROUP_CONCAT(ID_orders) FROM sl_orders WHERE ID_mediacontracts IN($id_mediacontracts_grouped) 
						AND DNIS IN($in{'edit_did'},$in{'destinationdid'});");
	my ($id_orders_grouped) = $sth->fetchrow();

	## Order R1, R2
	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_orders IN($id_orders_grouped) ORDER BY CONCAT(Date,' ',Time) LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	$o1 = $sth->fetchrow();
	$o1 = $r1 if !$o1;

	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_orders IN($id_orders_grouped) ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	$o2 = $sth->fetchrow();
	$o2 = $r2 if !$o2;

	## LeadCalls
	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE 
				ID_orders IN($id_orders_grouped)
				OR ID_order_assign IN($id_orders_grouped) 
				OR (DIDUS IN ($didusa_prev,$didusa_new) AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				)
			ORDER BY CONCAT(Date,' ',Time) LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	my ($lc1) = $sth->fetchrow();

	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE 
				ID_orders IN($id_orders_grouped)
				OR ID_order_assign IN($id_orders_grouped) 
				OR (DIDUS IN ($didusa_prev,$didusa_new) AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				)
			ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	my ($lc2) = $sth->fetchrow();

	#4) Reseting LeadCalls
	$query = "UPDATE sl_leads_calls SET 
				ID_order_assign = 0, 
				ID_orders = 0, 
				ID_mediacontract_assign = 0, 
				ID_mediacontracts = 0 
			WHERE 
				ID_orders IN($id_orders_grouped)
				OR ID_order_assign IN($id_orders_grouped) 
				OR (DIDUS IN ($didusa_prev,$didusa_new) AND 
					(ID_mediacontracts IN($id_mediacontracts_grouped) OR
					 ID_mediacontract_assign IN($id_mediacontracts_grouped) 	
					)
				);";

	my ($sth) = &Do_SQL($query);
	my ($leads_edited) = $sth->rows();		


	#5) Reseting Orders
	if($id_orders_grouped){
		$query = "UPDATE sl_orders SET ID_mediacontracts = 0 WHERE ID_orders IN($id_orders_grouped);";
		my ($sth) = &Do_SQL($query);
		$orders_edited = $sth->rows();
	}


	if($id_mediacontracts_grouped){
	#6) Reseting Mediacontracts Status
		$query = "UPDATE sl_mediacontracts SET Status = 'Programado', MediaStatus='Open' WHERE ID_mediacontracts IN($id_mediacontracts_grouped);";
		my ($sth) = &Do_SQL($query);
	}


	require ('../../common/apps/leadsDids.cgi');
	my ($orders_assigned,$l1) = &assign_orders($o1, $o2);
	#7) Reassigning Leads
	my $leads_assigned = &assign_leads_no_order($lc1, $lc2);
	$leads_assigned += $l1;

	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='DID edited\nOld:".$in{'destinationdid'}."\nNew:".$in{'edit_did'}."\nDates Period: $o1 - $o2\nContracts affected:$id_mediacontracts_grouped',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Data Changed\nOrders: $orders_assigned / $orders_edited\nLeads: $leads_assigned / $leads_edited',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

	#8) Updating Status
	&status_contracts($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

	#9) Ratios Summary
	&run_ratiossummary($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

	$in{'status'} = &load_name('sl_mediacontracts','ID_mediacontracts',$in{'id_mediacontracts'},'Status');

}


########################################################################
########################################################################
#
#	Function: mediacontracts_edit_status
#   		Reset sl_orders, sl_leads_calls ID_orders, ID_mediacontracts, ID_order_assign, ID_mediacontracr_assign rows
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_mediacontracts : ID_mediacontracts
#		- chgstatus: New Status
#		- destinationdid: DID
#
#   	Returns:
#
#   	See Also:
#
sub mediacontracts_edit_status{
#########################################################################



	if($in{'chgstatus'} !~ /Error/){
		return;
	}

	my ($query);
	my $dest_did_ni=9996;
	my($o1,$o2,$id_orders_grouped,$id_mediacontracts_grouped,$mod,$lc1,$lc2,$leads_edited,$orders_edited,$orders_assigned,$l1,$leads_assigned);

	my $didusa = load_name('sl_mediadids','didmx',$in{'destinationdid'},'didusa');
	

	my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
	## 1) Fechas 1a y ultima orden con ese contrato)
	my ($sth)=&Do_SQL("SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY CONCAT(Date,' ',Time) LIMIT 1;");		
	$o1 = $sth->fetchrow();

	my ($sth)=&Do_SQL("SELECT CONCAT(Date,' ',Time) FROM sl_orders WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");		
	$o2 = $sth->fetchrow();


	if($o1 and $o2){
	#3) Ordenes Agrupadas
		my ($sth)=&Do_SQL("SELECT GROUP_CONCAT(ID_orders) FROM sl_orders WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'");
		$id_orders_grouped = $sth->fetchrow();

		my ($sth)=&Do_SQL("SELECT GROUP_CONCAT(ID_mediacontracts) FROM sl_mediacontracts WHERE CONCAT(ESTDay,' ',ESTTime) BETWEEN  DATE_SUB('$o1', INTERVAL 1 DAY) AND '$o2' AND ID_mediacontracts <> '$in{'id_mediacontracts'}'");
		$id_mediacontracts_grouped = $sth->fetchrow();		
	}


	if($id_orders_grouped){
		$mod = "OR ID_orders IN($id_orders_grouped)
				OR ID_order_assign IN($id_orders_grouped) ";
	}

	if($id_mediacontracts_grouped){
		$mod2 = "OR (
						ID_mediacontracts IN($id_mediacontracts_grouped) 
						OR ID_mediacontract_assign IN($id_mediacontracts_grouped) 
					)";
	}

	## LeadCalls
	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE 
				( 
					(
						ID_mediacontracts = '$in{'id_mediacontracts'}' 
						OR ID_mediacontract_assign = '$in{'id_mediacontracts'}'
					)
					$mod2
				)
				$mod
			ORDER BY CONCAT(Date,' ',Time) LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	$lc1 = $sth->fetchrow();

	$query = "SELECT CONCAT(Date,' ',Time) FROM sl_leads_calls WHERE 
				( 
					(
						ID_mediacontracts = '$in{'id_mediacontracts'}' 
						OR ID_mediacontract_assign = '$in{'id_mediacontracts'}'
					)
					$mod2
				)
				$mod
			ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;";
	my ($sth) = &Do_SQL($query);
	$lc2 = $sth->fetchrow();


	#4) Reseting LeadCalls
	$query = "UPDATE sl_leads_calls SET 
				ID_order_assign = 0, 
				ID_orders = 0, 
				ID_mediacontract_assign = 0, 
				ID_mediacontracts = 0 
			WHERE 
				( 
					(
						ID_mediacontracts = '$in{'id_mediacontracts'}' 
						OR ID_mediacontract_assign = '$in{'id_mediacontracts'}'
					)
					$mod2
				)
				$mod ;";

	my ($sth) = &Do_SQL($query);
	$leads_edited = $sth->rows();		


	if($id_orders_grouped){
	#5) Reseting Orders
		$query = "UPDATE sl_orders SET ID_mediacontracts = 0 WHERE ID_orders IN($id_orders_grouped);";
		my ($sth) = &Do_SQL($query);
		$orders_edited = $sth->rows();
	}


	if($id_mediacontracts_grouped){
	#6) Reseting Mediacontracts Status
		$query = "UPDATE sl_mediacontracts SET Status = 'Programado', MediaStatus='Open' WHERE ID_mediacontracts IN($id_mediacontracts_grouped);";
		my ($sth) = &Do_SQL($query);
	}


	require ('../../common/apps/leadsDids.cgi');
	($orders_assigned,$l1) = &assign_orders($o1, $o2) if ($o1 and $o2);
	#7) Reassigning Leads
	$leads_assigned = &assign_leads_no_order($lc1, $lc2) if ($lc1 and $lc2);
	$leads_assigned += $l1;

	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Status edited\nOld:".$in{'status'}."\nNew:".$in{'chgstatus'}."\nDates Period: $o1 - $o2\nContracts affected:$in{'id_mediacontracts'}',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
	my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Data Changed\nOrders: $orders_assigned / $orders_edited\nLeads: $leads_assigned / $leads_edited',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
	my ($sth) = &Do_SQL("DELETE FROM sl_mediacontracts_stats WHERE ID_mediacontracts=$in{'id_mediacontracts'};");

	#8) MediaContracts Status
	&status_contracts($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

	#9) Ratios Summary
	&run_ratiossummary($id_mediacontracts_grouped) if $id_mediacontracts_grouped;

}


#####################################################################
#####################################################################
#	Function: run_ratiossummary
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#
#   	Returns:
#
#   	See Also: 
# 				
# 				#####################################
# 				##################################### ATENCION!!!!!! Esta funcion tambien se encuentra en cron_scripts en la ruta
# 				##################################### /cgi-bin/subs/sub.fun.s3.html.cgi
# 
#
sub run_ratiossummary{
#####################################################################
#####################################################################

	my ($id_mediacontracts_grouped)= @_;
	my ($c);
	
	### Bulding Report
	my ($sth) = &Do_SQL("SELECT * FROM `sl_mediacontracts` WHERE ID_mediacontracts IN($id_mediacontracts_grouped) AND Status IN(". $cfg{'contract_valid_status'} .") ORDER BY ESTDay ASC");
	while ($rec = $sth->fetchrow_hashref() ) {
		my ($tmp) = load_contract_totals($rec->{'ID_mediacontracts'},$rec->{'ESTTime'},$rec->{'ESTDay'},$rec->{'DestinationDID'});
		
		### Load Calls
		$sth2 = &Do_SQL("SELECT 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,1,0))AS P1, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3,

			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,Duration,0))AS D1, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,Duration,0))AS D2, 
			SUM(IF(TIMESTAMPDIFF(MINUTE, '$rec->{'ESTDay'} $rec->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,Duration,0))AS D3				
			
			FROM sl_leads_calls WHERE ID_mediacontracts = '$rec->{'ID_mediacontracts'}' AND IO='In'");
			($rec->{'P1Calls'},$rec->{'P2Calls'},$rec->{'P3Calls'},$rec->{'P1CallsSec'},$rec->{'P2CallsSec'},$rec->{'P3CallsSec'})=$sth2->fetchrow();
			

		## Totals 
		$rec->{'tcalls'} = $rec->{'P1Calls'}+$rec->{'P2Calls'}+$rec->{'P3Calls'};
		$rec->{'qOrders'} = $tmp->{'P1qtyTDC'}+$tmp->{'P2qtyTDC'}+$tmp->{'P3qtyTDC'}+$tmp->{'P1qtyCOD'}+$tmp->{'P2qtyCOD'}+$tmp->{'P3qtyCOD'};
		$rec->{'tOrders'} = $tmp->{'P1totTDC'}+$tmp->{'P2totTDC'}+$tmp->{'P3totTDC'}+$tmp->{'P1totCOD'}+$tmp->{'P2totCOD'}+$tmp->{'P3totCOD'};		
		
		## CPC
		if ($rec->{'tcalls'}>0){
			$rec->{'cpc'} = &round($rec->{'Cost'}/$rec->{'tcalls'},2);
			$rec->{'conv'} = &round($rec->{'qOrders'}/$rec->{'tcalls'}*100,2);
		}else{
			$rec->{'cpc'} =  0;
			$rec->{'conv'} = 0;
		}
		if ($rec->{'tOrders'}>0){
			$rec->{'tottdc'} = $tmp->{'P1totTDC'}+$tmp->{'P2totTDC'}+$tmp->{'P3totTDC'};
			
		}else{
			$rec->{'ptdc'} =  0;
			$rec->{'ratio'} =  0;
		}
		if ($rec->{'Cost'}>1){  ## Cost .01 no llevan ratio
			$rec->{'ratio'} = &round($rec->{'tOrders'}/$rec->{'Cost'},2);
		}else{
			$rec->{'ratio'} = 0;
		}
		if ($rec->{'qOrders'}>0){
			$rec->{'cpo'} = &round($rec->{'Cost'}/$rec->{'qOrders'},2);
			$rec->{'aov'} = &round($rec->{'tOrders'}/$rec->{'qOrders'},2)
		}else{
			$rec->{'cpo'} = 0;
			$rec->{'aov'} = 0;
		}
		
		
		my ($sth2) = &Do_SQL("REPLACE INTO sl_mediacontracts_stats SET
					ID_mediacontracts=$rec->{'ID_mediacontracts'},
					Calls = '$rec->{'tcalls'}',
					CPC   = '$rec->{'cpc'}',
					Conv  = '$rec->{'conv'}',
					QtyOrders = '$rec->{'qOrders'}',
					TotOrders = '$rec->{'tOrders'}',
					TotTDC = '$rec->{'tottdc'}',
					CPO = '$rec->{'cpo'}',
					AOV = '$rec->{'aov'}',
					Ratio = '$rec->{'ratio'}',
					FamProd = '". &product_family($rec->{'Offer'})."'
						");
		++$c;
	}

}



1;
