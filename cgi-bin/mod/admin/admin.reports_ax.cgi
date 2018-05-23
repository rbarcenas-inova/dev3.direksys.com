#!/usr/bin/perl
##
## Run Reports
##

sub ax_wpendings {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($rdate) = @_;
	my ($amount,$count,%rep_cols,@rep_totals);
	$rdate = sqldate_plus($rdate,1);
	my (@cols) = ('bill-add','generaldec','insuffunds','stolen','invalid','avs','pre-approved',
				'missing','check','processor','timedout','cvn','expired','risk','na');
	my (@cols_names) = ('Bill <> Shipping','General Decline','Insuficient Funds','Stolen Card','Invalid Card','AVS not Match','Pre-approved',
				'Missing Info','Check','The processor declined the request based on an issue with the request itself.','Communication Error','Card verification number not matched.','Expired card','Risk Order','Not Available');
	
	
	print qq|<table border="1" cellspacing="0" width="95%" class="formtable" align="center">\n|;
	print "<tr>";
		print "<td class='menu_bar_title' colspan='15' align='center'>Pending - Analisis</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>Type</td>";
	for my $i(1..7){
		my ($ndate) = &sqldate_plus($rdate,-$i);
		print "<td class='menu_bar_title' colspan='2' align='center'>$ndate</td>";
		my (%resp) = &ax_pendings_load(" AND Date='$ndate'");
		for (0..$#cols){
			$rep_cols{$cols[$_]} .= "<td class='smalltext' align='right'>".&format_number($resp{$cols[$_]}[0])."</td>\n";
			$rep_cols{$cols[$_]} .= "<td class='smalltext' align='right'>".&format_price($resp{$cols[$_]}[1])."</td>\n";
			$amount  += $resp{$cols[$_]}[1];
			$count += $resp{$cols[$_]}[0];
		}
		$rep_totals[$i] .= "<td class='smalltext' align='right'>".&format_number($count)."</td>\n";
		$rep_totals[$i] .= "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
	}
	print "</tr>";
	for (0..$#cols){
		print "<tr>";
		print "<td class='smalltext'>$cols_names[$_]</td>";
		print $rep_cols{$cols[$_]};
		print "</tr>";
	}
	print "<tr>";
	print "<td class='smalltext' align='right'>Total = </td>";
	for my $i(1..7){
		print $rep_totals[$i];
	}
	print "</tr>";	
	print "</table>&nbsp;";	
}

sub ax_dmas {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount,%tcant,%tmnt);
	my (@cols) = ('1','2','9','3','6','8','4','16','12','14','20','25','10','18','5','35','15','28','55','27','23','43','13','19','7','38','63','124','126');

	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='".($#months*2+3)."' align='center'>ORDERS BY DMA</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By DMA</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";


	for my $d(0..$#cols){
		print "<tr>";
		###
		### Orders by Before First Month
		###
		##my ($sth) = &Do_SQL("SELECT sl_orders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]'  AND ID_products > 100000  GROUP BY sl_orders.Status");
		my ($sth) = &Do_SQL("SELECT CONCAT(RANK,' ',DMA_DESC),COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders WHERE sl_zipdma.ZipCode=sl_orders.Zip AND RANK=$cols[$d]  AND sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[0]}[2] GROUP BY RANK");
		my ($name,$num,$amount) = $sth->fetchrow_array();
		print "<td class='smalltext'>$name</td>";
		print "<td class='smalltext'>$num</td>";
		print "<td class='smalltext'>$amount</td>";
		$tcant{$months[0]} += $num;
		$tmnt{$months[0]}  += $amount;
		###
		### Orders by DMAs
		###		
		for my $m(1..$#months){
			my ($sth) = &Do_SQL("SELECT CONCAT(RANK,' ',DMA_DESC),COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders WHERE sl_zipdma.ZipCode=sl_orders.Zip AND RANK=$cols[$d]  AND sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]  GROUP BY RANK");
			my ($name,$num,$amount) = $sth->fetchrow_array();
			print "<td class='smalltext'>$num</td>";
			print "<td class='smalltext'>$amount</td>";
			$tcant{$months[$m]}  += $num;
			$tmnt{$months[$m]}  += $amount;
		}
		print "</tr>";

	}
	print "<tr>";
	print "<td class='smalltext'>Other</td>";
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders WHERE sl_zipdma.ZipCode=sl_orders.Zip AND sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[0]}[2]");
	my ($num,$amount) = $sth->fetchrow_array();
	print "<td class='smalltext'>$num</td>";
	print "<td class='smalltext'>$amount</td>";	
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_zipdma,sl_orders WHERE sl_zipdma.ZipCode=sl_orders.Zip AND sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]");
		my ($num,$amount) = $sth->fetchrow_array();
		print "<td class='smalltext'>".(int(($num-$tcant{$months[$m]})*100)/ 100)."</td>";
		print "<td class='smalltext'>".(int(($amount-$tmnt{$months[$m]})*100)/ 100)."</td>";
	}
	print "</tr>";
	print "</table>&nbsp;";

}


sub ax_mso {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount,%tcant,%tmnt);
	my (@cols_names) = ('Dish Network','Time Warner Cable','DirecTV','Web Only');
	my (@cols_query) = ("ID_stations IN ('1008','1009')","ID_stations IN ('1010','1011','1012','1014','1015')","ID_stations IN ('1013')","ID_stations IN ('1017')");
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='".($#months*2+3)."' align='center'>ORDERS BY MSO</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By MSO</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";


	for my $d(0..$#cols_query){
		print "<tr>";
		###
		### Orders by Before First Month
		###
		##my ($sth) = &Do_SQL("SELECT sl_orders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]'  AND ID_products > 100000  GROUP BY sl_orders.Status");
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_orders WHERE $cols_query[$d] AND  Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[0]}[2]");
		my ($num,$amount) = $sth->fetchrow_array();
		print "<td class='smalltext'>$cols_names[$d]</td>";
		print "<td class='smalltext'>$num</td>";
		print "<td class='smalltext'>$amount</td>";
		$tcant{$months[0]} += $num;
		$tmnt{$months[0]}  += $amount;
		###
		### Orders by DMAs
		###		
		for my $m(1..$#months){
			my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_orders WHERE $cols_query[$d] AND sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]");
			my ($num,$amount) = $sth->fetchrow_array();
			print "<td class='smalltext'>$num</td>";
			print "<td class='smalltext'>$amount</td>";
			$tcant{$months[$m]}  += $num;
			$tmnt{$months[$m]}  += $amount;
		}
		print "</tr>";

	}
	print "<tr>";
	print "<td class='smalltext'>Other</td>";
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_orders WHERE sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[0]}[2]");
	my ($num,$amount) = $sth->fetchrow_array();
	print "<td class='smalltext'>$num</td>";
	print "<td class='smalltext'>$amount</td>";	
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderNet) FROM sl_orders WHERE sl_orders.Status NOT IN ('Void','System Error') AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]");
		my ($num,$amount) = $sth->fetchrow_array();
		print "<td class='smalltext'>".(int(($num-$tcant{$months[$m]})*100)/ 100)."</td>";
		print "<td class='smalltext'>".(int(($amount-$tmnt{$months[$m]})*100)/ 100)."</td>";
	}
	print "</tr>";
	print "</table>&nbsp;";

}

sub ax_wvoid {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($rdate) = @_;
	my ($amount,$count,%rep_cols,@rep_totals);
	$rdate = sqldate_plus($rdate,1);
	my (@cols) = ('bill-add','generaldec','insuffunds','stolen','invalid','avs','pre-approved',
				'missing','check','processor','timedout','cvn','expired','risk','na');
	my (@cols_names) = ('Bill <> Shipping','General Decline','Insuficient Funds','Stolen Card','Invalid Card','AVS not Match','Pre-approved',
				'Missing Info','Check','The processor declined the request based on an issue with the request itself.','Communication Error','Card verification number not matched.','Expired card','Risk Order','Not Available');
	
	
	print qq|<table border="1" cellspacing="0" width="95%" class="formtable" align="center">\n|;
	print "<tr>";
		print "<td class='menu_bar_title' colspan='15' align='center'>Void - Analisis</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>Type</td>";
	for my $i(1..7){
		my ($ndate) = &sqldate_plus($rdate,-$i);
		print "<td class='menu_bar_title' colspan='2' align='center'>$ndate</td>";
		my (%resp) = &ax_pendings_load(" AND Date='$ndate'",'Void');
		for (0..$#cols){
			$rep_cols{$cols[$_]} .= "<td class='smalltext' align='right'>".&format_number($resp{$cols[$_]}[0])."</td>\n";
			$rep_cols{$cols[$_]} .= "<td class='smalltext' align='right'>".&format_price($resp{$cols[$_]}[1])."</td>\n";
			$amount  += $resp{$cols[$_]}[1];
			$count += $resp{$cols[$_]}[0];
		}
		$rep_totals[$i] .= "<td class='smalltext' align='right'>".&format_number($count)."</td>\n";
		$rep_totals[$i] .= "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
	}
	print "</tr>";
	for (0..$#cols){
		print "<tr>";
		print "<td class='smalltext'>$cols_names[$_]</td>";
		print $rep_cols{$cols[$_]};
		print "</tr>";
	}
	print "<tr>";
	print "<td class='smalltext' align='right'>Total = </td>";
	for my $i(1..7){
		print $rep_totals[$i];
	}
	print "</tr>";	
	print "</table>&nbsp;";	
}

sub ax_pendings {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($rdate) = @_;
	my ($amount,$count);
	my (%resp) = &ax_pendings_load(" AND Date='$in{'rdate'}'");
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable" align="center">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='5' align='center'>Pending - Analisis</td>";
	print "</tr>";		
	my (@cols) = ('bill-add','generaldec','insuffunds','stolen','invalid','avs','pre-approved',
				'missing','check','processor','timedout','cvn','expired','risk','na');
	my (@cols_names) = ('Bill <> Shipping','General Decline','Insuficient Funds','Stolen Card','Invalid Card','AVS not Match','Pre-approved',
				'Missing Info','Check','The processor declined the request based on an issue with the request itself.','Communication Error','Card verification number not matched.','Expired card','Risk Order','Not Available');
	for (0..$#cols){
		print "<tr>";
		print "<td class='smalltext'>$cols_names[$_]</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$cols[$_]}[0])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$cols[$_]}[1])."</td>";
		print "</tr>";
		$amount  += $resp{$cols[$_]}[1];
		$count += $resp{$cols[$_]}[0];
	}
	print "<tr>";
		print "<td class='smalltext' align='right'>Total = </td>";
		print "<td class='smalltext' align='right'>".&format_number($count)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";	
	print "</table>&nbsp;";

}


sub ax_pendings_load {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($filter,$status) = @_;
	my (%resp,$num,$amount);
	if (!$status){
		$status = 'Pending';
	}
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE Status='$status' $filter");
	IDORDEN: while ($rec = $sth->fetchrow_hashref()){
		if ($rec->{'Address1'} ne $rec->{'shp_Address1'} or $rec->{'Zip'} ne $rec->{'shp_Zip'}){
			$resp{'bill-add'}[0] +=  1;
			$resp{'bill-add'}[1] +=  $rec->{'OrderNet'};
			next IDORDEN;
		}
		my ($sth2) = &Do_SQL("SELECT Data FROM sl_orders_plogs WHERE ID_orders='$rec->{'ID_orders'}' ORDER BY ID_orders_plogs DESC LIMIT 0,1");
		$plog_data = $sth2->fetchrow();
		if ($plog_data =~ /reasonCode = 203/i){
			$resp{'generaldec'}[0] +=  1;
			$resp{'generaldec'}[1] +=  $rec->{'OrderNet'};
		}elsif ($plog_data =~ /reasonCode = 204/i){
			$resp{'insuffunds'}[0] +=  1;
			$resp{'insuffunds'}[1] +=  $rec->{'OrderNet'};	
		}elsif ($plog_data =~ /reasonCode = 205/i){
			$resp{'stolen'}[0] +=  1;
			$resp{'stolen'}[1] +=  $rec->{'OrderNet'};
		}elsif ($plog_data =~ /reasonCode = 233/i){
			$resp{'processor'}[0] +=  1;
			$resp{'processor'}[1] +=  $rec->{'OrderNet'};	
		}elsif ($plog_data =~ /reasonCode = 202/i){  ## Expired card
			$resp{'expired'}[0] +=  1;
			$resp{'expired'}[1] +=  $rec->{'OrderNet'};		
			
		}elsif ($plog_data =~ /reasonCode = 231|reasonCode = 211/i){  ##Invalid account number.
			$resp{'invalid'}[0] +=  1;
			$resp{'invalid'}[1] +=  $rec->{'OrderNet'};		
		}elsif ($plog_data =~ /pre - APPROVED MODE|Auto Approved|reasonCode = 150|reasonCode = 250/i){
			$resp{'check'}[0] +=  1;
			$resp{'check'}[1] +=  $rec->{'OrderNet'};	
		}elsif ($plog_data =~ /reasonCode = 520/i){	 ## Cheque
			$resp{'bill-add'}[0] +=  1;
			$resp{'bill-add'}[1] +=  $rec->{'OrderNet'};		
		}elsif ($plog_data =~ /PayNetTransactionID/i){	 ## Cheque
			$resp{'pre-approved'}[0] +=  1;
			$resp{'pre-approved'}[1] +=  $rec->{'OrderNet'};	
		}elsif ($plog_data =~ /reasonCode = 102|reasonCode = 101/i){  ## Missing Info
			$resp{'missing'}[0] +=  1;
			$resp{'missing'}[1] +=  $rec->{'OrderNet'};	
		}elsif ($plog_data =~ /reasonCode = 201/i){   #Card verification number not matched.
			$resp{'cvn'}[0] +=  1;
			$resp{'cvn'}[1] +=  $rec->{'OrderNet'};					
		}elsif ($plog_data =~ /msg_avsCode = No match/i){
			$resp{'avs'}[1] +=  $rec->{'OrderNet'};
			$resp{'avs'}[0] +=  1;	
		}elsif ($plog_data =~ /timed out|FailedCheck/i){
			$resp{'timedout'}[1] +=  $rec->{'OrderNet'};
			$resp{'timedout'}[0] +=  1;		
		}elsif (!$plog_data){  # no plog
			$resp{'na'}[0] +=  1;
			$resp{'na'}[1] +=  $rec->{'OrderNet'};	
			#print "ID_orders: $rec->{'ID_orders'}<br>";
		}else{
			if (&check_rman($rec->{'ID_orders'}) ne 'OK'){
				$resp{'risk'}[0] +=  1;
				$resp{'risk'}[1] +=  $rec->{'OrderNet'};
			}else{
				$resp{'na'}[0] +=  1;
				$resp{'na'}[1] +=  $rec->{'OrderNet'};	
				#if ($plog_data !~ /reasonCode = 100/i){
				#	print "<pre>";
				#	print $plog_data;
				#	return;
				#}
				#print "ID_orders: $rec->{'ID_orders'}<br>";
			}
		}
	} #&cgierr(%resp);
	return (%resp);
}


sub ax_good_bad_debt {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount,$query_pmts);
	

	#print "months = $range{'months'}<br>";
	#return;
	###
	### Flexipagos : Good v/s Bad Debt
	###
	#@months = ('Feb-08');
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='18' align='center'>Flexipagos - Analisis - Qty</td>";
	print "</tr>";
	print "<tr>";
		print "<td class='menu_bar_title'>FP Analisis</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Totals</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>OK</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>w/Errors</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Sgl Pmt</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Good Debt</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Bad Deb Low</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Bad Deb Mid</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Bad Deb Hi</td>";
	print "</tr>";	
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[0]}[2] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') GROUP BY ID_orders");
	IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
		#print "$months[0]\t$name\t$num\t$amount<br>";
		++$resp{$months[0]}{$status}[1];
		$resp{$months[0]}{$status}[2] += $amount;
		## Check Totals
		$tot_check = &check_ord_totals($id);
		if ($tot_check  eq 'OK'){
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
			if ($sth2->fetchrow >0){
				## Tiene Returns
				++$resp{$months[0]}{$status}[5];
				$resp{$months[0]}{$status}[6] += $amount;
			}else{
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
				if ($sth2->fetchrow >0){
					## Tiene Returns
					++$resp{$months[0]}{$status}[5];
					$resp{$months[0]}{$status}[6] += $amount;
				}else{
					++$resp{$months[0]}{$status}[3];
					$resp{$months[0]}{$status}[4] += $amount;
				}
			}
		}else{
			++$resp{$months[0]}{$status}[5];
			$resp{$months[0]}{$status}[6] += $amount;
		}
		## Check Risk
		#if ( &check_rman($id) eq 'OK'){
		#	++$resp{$months[0]}{$status}[7];
		#	$resp{$months[0]}{$status}[8] += $amount;
		#}else{
		#	++$resp{$months[0]}{$status}[9];
		#	$resp{$months[0]}{$status}[10] += $amount;
		#}
		if ($tot_check  eq 'OK'){
			($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
			if ($payments eq 1){
				++$resp{$months[0]}{$status}[11];
				$resp{$months[0]}{$status}[12] += $amount;
			}elsif($pay_status eq 'GOOD'){
				++$resp{$months[0]}{$status}[13];
				$resp{$months[0]}{$status}[14] += $amount;
				
			}else{  #Bad
				$resp{$months[0]}{$status}[14] += ($amount-$unpaid);
				#print "$id unpaid:$unpaid<br>";
				if ($pay_status  eq 'BAD1'){
					++$resp{$months[0]}{$status}[15];
					$resp{$months[0]}{$status}[16] += $unpaid;
				}elsif ($pay_status  eq 'BAD2'){
					++$resp{$months[0]}{$status}[17];
					$resp{$months[0]}{$status}[18] += $unpaid;
				}else{
					++$resp{$months[0]}{$status}[19];
					$resp{$months[0]}{$status}[20] += $unpaid;
				}
			}
		}
	}
	$status[$s] = 'Shipped';

	print "<tr>";
	print "<td class='smalltext'>$months[0]</td>";
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[1])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[2])."</td>";
	
	## Totals
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[3])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[4])."</td>";
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[5])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[6])."</td>";

	## Sgl Payments
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[11])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[12])."</td>";
	
	## Good Debt
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[13])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[14])."</td>";			

	## Bad Debt  Low
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[15])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[16])."</td>";
	## Bad Debt  Mid
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[17])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[18])."</td>";
	## Bad Debt  High >=3
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[19])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[20])."</td>";
	print "</tr>";

	
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') GROUP BY ID_orders");
		IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
			#print "$months[$m]\t$name\t$num\t$amount<br>";
			++$resp{$months[$m]}{$status}[1];
			$resp{$months[$m]}{$status}[2] += $amount;
			## Check Totals
			$tot_check = &check_ord_totals($id);
			if ($tot_check  eq 'OK'){
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
				if ($sth2->fetchrow >0){
					## Tiene Returns
					++$resp{$months[$m]}{$status}[5];
					$resp{$months[$m]}{$status}[6] += $amount;
				}else{
					my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
					if ($sth2->fetchrow >0){
						## Tiene Returns
						++$resp{$months[$m]}{$status}[5];
						$resp{$months[$m]}{$status}[6] += $amount;
					}else{
						++$resp{$months[$m]}{$status}[3];
						$resp{$months[$m]}{$status}[4] += $amount;
					}
				}
			}else{
				++$resp{$months[0]}{$status}[5];
				$resp{$months[0]}{$status}[6] += $amount;
			}
			## Check Risk
			#if ( &check_rman($id) eq 'OK'){
			#	++$resp{$months[$m]}{$status}[7];
			#	$resp{$months[$m]}{$status}[8] += $amount;
			#}else{
			#	++$resp{$months[$m]}{$status}[9];
			#	$resp{$months[$m]}{$status}[10] += $amount;
			#}
			if ($tot_check  eq 'OK'){
				($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
				if ($payments eq 1){
					++$resp{$months[$m]}{$status}[11];
					$resp{$months[$m]}{$status}[12] += $amount;
				}elsif($pay_status eq 'GOOD'){
					++$resp{$months[$m]}{$status}[13];
					$resp{$months[$m]}{$status}[14] += $amount;
					
				}else{
					$resp{$months[$m]}{$status}[14] += ($amount-$unpaid);
					#print "$id unpaid:$unpaid<br>";
					if ($pay_status  eq 'BAD1'){
						++$resp{$months[$m]}{$status}[15];
						$resp{$months[$m]}{$status}[16] += $unpaid;
					}elsif ($pay_status  eq 'BAD2'){
						++$resp{$months[$m]}{$status}[17];
						$resp{$months[$m]}{$status}[18] += $unpaid;
					}else{
						++$resp{$months[$m]}{$status}[19];
						$resp{$months[$m]}{$status}[20] += $unpaid;
					}
				}
			}
		}
		$status[$s] = 'Shipped';

		print "<tr>";
		print "<td class='smalltext'>$months[$m]</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
		
		## Totals
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[3])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[4])."</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[5])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[6])."</td>";

		## Sgl Payments
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[11])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[12])."</td>";
		
		## Good Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[13])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[14])."</td>";			


		## Bad Debt  Low
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[15])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[16])."</td>";
		## Bad Debt  Mid
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[17])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[18])."</td>";
		## Bad Debt  High >=3
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[19])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[20])."</td>";
		print "</tr>";
	}
	print "</table>&nbsp;";
}


sub ax_checkdebt {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	
	##print "months = $range{'months'}<br>";
	#return;
	###
	### Flexipagos : Good v/s Bad Debt
	###
	#@months = ('Feb-08');
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='19' align='center'>Flexipagos - Analisis - Aging</td>";
	print "</tr>";
	print "<tr>";
		print "<td class='menu_bar_title'>FP Analisis</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Totals</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>OK</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>w/Errors</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Sgl Pmt</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Good Debt</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>5-30</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>31-60</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>61-90</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>90</td>";
	print "</tr>";	
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[0]}[2] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') GROUP BY ID_orders");
	IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
		#print "$months[0]\t$name\t$num\t$amount<br>";
		++$resp{$months[0]}{$status}[1];
		$resp{$months[0]}{$status}[2] += $amount;
		## Check Totals
		$tot_check = &check_ord_totals($id);
		if ($tot_check  eq 'OK'){
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
			if ($sth2->fetchrow >0){
				## Tiene Returns
				++$resp{$months[0]}{$status}[5];
				$resp{$months[0]}{$status}[6] += $amount;
			}else{
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
				if ($sth2->fetchrow >0){
					## Tiene Returns
					++$resp{$months[0]}{$status}[5];
					$resp{$months[0]}{$status}[6] += $amount;
				}else{
					++$resp{$months[0]}{$status}[3];
					$resp{$months[0]}{$status}[4] += $amount;
				}
			}
		}else{
			++$resp{$months[0]}{$status}[5];
			$resp{$months[0]}{$status}[6] += $amount;
		}
		## Check Risk
		#if ( &check_rman($id) eq 'OK'){
		#	++$resp{$months[0]}{$status}[7];
		#	$resp{$months[0]}{$status}[8] += $amount;
		#}else{
		#	++$resp{$months[0]}{$status}[9];
		#	$resp{$months[0]}{$status}[10] += $amount;
		#}
		if ($tot_check  eq 'OK'){
			($payments,$pay_status,$paid,$unpaid) = &check_payments_dates($id);
			if ($payments eq 1){
				++$resp{$months[0]}{$status}[11];
				$resp{$months[0]}{$status}[12] += $amount;
			}elsif($pay_status eq 'GOOD'){
				++$resp{$months[0]}{$status}[13];
				$resp{$months[0]}{$status}[14] += $amount;
				
			}else{  #Bad
				$resp{$months[0]}{$status}[14] += ($amount-$unpaid);
				#print "$id unpaid:$unpaid<br>";
				if ($pay_status  eq '5'){
					++$resp{$months[0]}{$status}[15];
					$resp{$months[0]}{$status}[16] += $unpaid;
				}elsif ($pay_status  eq '30'){
					++$resp{$months[0]}{$status}[17];
					$resp{$months[0]}{$status}[18] += $unpaid;
				}elsif ($pay_status  eq '60'){
					++$resp{$months[0]}{$status}[19];
					$resp{$months[0]}{$status}[20] += $unpaid;
				}else{
					++$resp{$months[0]}{$status}[21];
					$resp{$months[0]}{$status}[22] += $unpaid;
				}
			}
		}
	}
	$status[$s] = 'Shipped';


	print "<tr>";
		print "<td class='smalltext'>$months[0]</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[2])."</td>";
		
		## Totals
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[3])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[4])."</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[5])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[6])."</td>";
	
		## Sgl Payments
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[11])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[12])."</td>";
		
		## Good Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[13])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[14])."</td>";			
	
		## Bad Debt  5-30
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[15])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[16])."</td>";
		## Bad Debt  31-60
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[17])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[18])."</td>";
		## Bad Debt  60-90
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[19])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[20])."</td>";
		## Bad Debt  90
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[21])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[22])."</td>";
	print "</tr>";

	
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') GROUP BY ID_orders");
		IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
			#print "$months[$m]\t$name\t$num\t$amount<br>";
			++$resp{$months[$m]}{$status}[1];
			$resp{$months[$m]}{$status}[2] += $amount;
			## Check Totals
			$tot_check = &check_ord_totals($id);
			if ($tot_check  eq 'OK'){
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled','Counter Finance')");
				if ($sth2->fetchrow >0){
					## Tiene Returns
					++$resp{$months[$m]}{$status}[5];
					$resp{$months[$m]}{$status}[6] += $amount;
				}else{
					my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
					if ($sth2->fetchrow >0){
						## Tiene Returns
						++$resp{$months[$m]}{$status}[5];
						$resp{$months[$m]}{$status}[6] += $amount;
					}else{
						++$resp{$months[$m]}{$status}[3];
						$resp{$months[$m]}{$status}[4] += $amount;
					}
				}
			}else{
				++$resp{$months[0]}{$status}[5];
				$resp{$months[0]}{$status}[6] += $amount;
			}
			## Check Risk
			#if ( &check_rman($id) eq 'OK'){
			#	++$resp{$months[$m]}{$status}[7];
			#	$resp{$months[$m]}{$status}[8] += $amount;
			#}else{
			#	++$resp{$months[$m]}{$status}[9];
			#	$resp{$months[$m]}{$status}[10] += $amount;
			#}
			if ($tot_check  eq 'OK'){
				($payments,$pay_status,$paid,$unpaid) = &check_payments_dates($id);
				if ($payments eq 1){
					++$resp{$months[$m]}{$status}[11];
					$resp{$months[$m]}{$status}[12] += $amount;
				}elsif($pay_status eq 'GOOD'){
					++$resp{$months[$m]}{$status}[13];
					$resp{$months[$m]}{$status}[14] += $amount;
					
				}else{  #Bad
					$resp{$months[$m]}{$status}[14] += ($amount-$unpaid);
					#print "$id unpaid:$unpaid<br>";
					if ($pay_status  eq '5'){
						++$resp{$months[$m]}{$status}[15];
						$resp{$months[$m]}{$status}[16] += $unpaid;
					}elsif ($pay_status  eq '30'){
						++$resp{$months[$m]}{$status}[17];
						$resp{$months[$m]}{$status}[18] += $unpaid;
					}elsif ($pay_status  eq '60'){
						++$resp{$months[$m]}{$status}[19];
						$resp{$months[$m]}{$status}[20] += $unpaid;
					}else{
						++$resp{$months[$m]}{$status}[21];
						$resp{$months[$m]}{$status}[22] += $unpaid;
					}
				}
			}
		}
		$status[$s] = 'Shipped';

		print "<tr>";
		print "<td class='smalltext'>$months[$m]</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
			
			## Totals
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[3])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[4])."</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[5])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[6])."</td>";
	
			## Sgl Payments
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[11])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[12])."</td>";
			
			## Good Debt
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[13])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[14])."</td>";			
	
	
			## Bad Debt  5-30
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[15])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[16])."</td>";
			## Bad Debt  30-60
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[17])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[18])."</td>";
			## Bad Debt  60-90
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[19])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[20])."</td>";
			## Bad Debt  90
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[21])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[22])."</td>";
		print "</tr>";
	}
	print "</table>&nbsp;";
}


sub ax_ord_by_status {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	
	###
	### Orders by Before First Month
	###
	my ($sth) = &Do_SQL("SELECT sl_orders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]'  AND ID_products > 100000  GROUP BY sl_orders.Status");
	while (($name,$num,$amount) = $sth->fetchrow_array()) {
		#print "$months[$m]\t$name\t$num\t$amount\n";
		$resp{$months[$m]}{$name}[1] = $num;
		$resp{$months[$m]}{$name}[2] = $amount;
	}
	
	###
	### Orders by Status Months
	###
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_orders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]  AND ID_products > 100000  GROUP BY sl_orders.Status");
		while (($name,$num,$amount) = $sth->fetchrow_array()) {
			#print "$months[$m]\t$name\t$num\t$amount\n";
			$resp{$months[$m]}{$name}[1] = $num;
			$resp{$months[$m]}{$name}[2] = $amount;
		}
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>Orders by Status</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By Status</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	for my $s(0..$#status){
		print "<tr>";
		print "<td class='smalltext'>$status[$s]</td>";
		for my $m(0..$#months){
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
		}
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_preord_by_status {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',"New,In Process,Paid,Expired");
	
	###
	### PREOrders by Before First Month
	###
	my ($sth) = &Do_SQL("SELECT sl_preorders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_preorders_products, sl_preorders WHERE sl_preorders_products.ID_preorders=sl_preorders.ID_preorders AND sl_preorders_products.Status='Active' AND YEAR(sl_preorders.Date)='$range{$months[0]}[2]'  AND ID_products > 100000  GROUP BY sl_preorders.Status");
	while (($name,$num,$amount) = $sth->fetchrow_array()) {
		#print "$months[$m]\t$name\t$num\t$amount\n";
		$resp{$months[$m]}{$name}[1] = $num;
		$resp{$months[$m]}{$name}[2] = $amount;
	}
	
	###
	### PREOrders by Status Months
	###
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_preorders.Status,COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_preorders_products, sl_preorders WHERE sl_preorders_products.ID_preorders=sl_preorders.ID_preorders AND sl_preorders_products.Status='Active' AND YEAR( sl_preorders.Date )=$range{$months[$m]}[2] AND MONTH( sl_preorders.Date )=$range{$months[$m]}[1]  AND ID_products > 100000  GROUP BY sl_preorders.Status");
		while (($name,$num,$amount) = $sth->fetchrow_array()) {
			#print "$months[$m]\t$name\t$num\t$amount\n";
			$resp{$months[$m]}{$name}[1] = $num;
			$resp{$months[$m]}{$name}[2] = $amount;
		}
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>PREOrders by Status</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By Status</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	for my $s(0..$#status){
		print "<tr>";
		print "<td class='smalltext'>$status[$s]</td>";
		for my $m(0..$#months){
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
		}
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_ord_by_week {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	###
	### Sales by Week
	###
	print qq|<table border="0" cellspacing="0" width="450" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='5' align='center'>Sales By Week</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'>Week</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Tot Qty</td>";
	print "<td class='menu_bar_title' align='center'>Tot Amount</td>";
	print "</tr>";	
	
	for my $i(1..6){
		my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND sl_orders.Status='Shipped' AND 
			sl_orders.Date>=DATE_ADD('$range{'weeklysale_to'}',INTERVAL ".(-($i+1)*7-1)." DAY) AND sl_orders.Date<=DATE_ADD('$range{'weeklysale_to'}',INTERVAL ".(-$i*7)." DAY)  AND ID_products > 100000");
		($num,$amount) = $sth->fetchrow_array();
		my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(SalePrice*Quantity) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND 
			sl_orders.Date>=DATE_ADD('$range{'weeklysale_to'}',INTERVAL ".(-($i+1)*7-1)." DAY) AND sl_orders.Date<=DATE_ADD('$range{'weeklysale_to'}',INTERVAL ".(-$i*7)." DAY)  AND ID_products > 100000");
		($tnum,$tamount) = $sth->fetchrow_array();
		print "<tr>";
		print "<td class='smalltext'>".&sqldate_plus($range{'weeklysale_to'},-($i-1)*7)." - ".&sqldate_plus($range{'weeklysale_to'},-$i*7)."</td>";
		print "<td class='smalltext' align='right'>".&format_number($num)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "<td class='smalltext' align='right'>".&format_number($tnum)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($tamount)."</td>";
		print "</tr>";
	}	
	print "</table>&nbsp;";
}

sub ax_ord_by_week_day {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	###
	### Sales by Week day
	###
	@weekdays = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='15' align='center'>Sales By Week</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'></td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Sun</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Mon</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Tue</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Wed</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Thu</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Fri</td>";
	print "<td class='menu_bar_title' align='center' colspan='2'>Sat</td>";
	print "</tr>";	
	print "<tr>";
	print "<td class='menu_bar_title' align='center'>Week</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(OrderNet) AS amounts FROM sl_orders WHERE Date<='$range{'weeklysale_to'}' GROUP BY Date ORDER BY Date DESC ");
	
	for my $i(1..6){
			
			print "<tr>";
			print "<td class='smalltext'>".&sqldate_plus($range{'weeklysale_to'},-$i*7)." - ".&sqldate_plus($range{'weeklysale_to'},-($i-1)*7)."</td>";
			
			for my $w(0..6){
				($num,$amount) = $sth->fetchrow_array();
				print "<td class='smalltext' align='right'>".&format_number($num)."</td>";
				print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
			}
			print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_ord_by_paytype {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (%resp,$num,$amount);
	###
	### Sales by Pay Type
	###
	@status = ('Credit-Card', 'Check', 'WesternUnion', 'Money Order');

	###
	### Orders by Before First Month
	###
	my ($sth) = &Do_SQL("SELECT sl_orders_payments.Type,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders_payments.Status<>'Cancelled' AND YEAR( sl_orders.Date )=$range{$months[0]}[2]  AND sl_orders.Status IN ('Shipped')  GROUP BY sl_orders_payments.Type");
	while (($name,$num,$amount) = $sth->fetchrow_array()) {
		#print "$months[$m]\t$name\t$num\t$amount\n";
		$resp{$months[$m]}{$name}[1] = $num;
		$resp{$months[$m]}{$name}[2] = $amount;
	}

	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_orders_payments.Type,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders_payments.Status<>'Cancelled' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1]  AND sl_orders.Status IN ('Shipped')  GROUP BY sl_orders_payments.Type");
		while (($name,$num,$amount) = $sth->fetchrow_array()) {
			$resp{$months[$m]}{$name}[1] = $num;
			$resp{$months[$m]}{$name}[2] = $amount;
		}
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>Sales by Pay Type</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By Type</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	for my $s(0..$#status){
		print "<tr>";
		print "<td class='smalltext'>$status[$s]</td>";
		for my $m(0..$#months){
			#print "\t\t $resp{$months[$m]}{$status[$s]}[2]";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
		}
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_ord_shipping {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (%resp,$num,$amount,$m);
	
	###
	### Shipping Before First Month
	###
	my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(OrderShp) AS amounts FROM sl_orders WHERE YEAR(Date)='$range{$months[0]}[2]' AND sl_orders.Status='Shipped'");
	while (($num,$amount) = $sth->fetchrow_array()) {
		#print "$months[$m]\t$name\t$num\t$amount\n";
		$resp{$months[0]}{'shipping'}[1] = $num;
		$resp{$months[0]}{'shipping'}[2] = $amount;
	}
	
	###
	### Shipping by  Months
	###
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(OrderShp) AS amounts FROM sl_orders WHERE YEAR(Date)=$range{$months[$m]}[2] AND MONTH(Date)=$range{$months[$m]}[1] AND sl_orders.Status='Shipped'");
		while (($num,$amount) = $sth->fetchrow_array()) {
			#print "$months[$m]\t'shipping'\t$num\t$amount\n";
			$resp{$months[$m]}{'shipping'}[1] = $num;
			$resp{$months[$m]}{'shipping'}[2] = $amount;
		}
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>Shipping</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>Shipping Charges</td>";
	for my $m(0..$#months){
			print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	print "<tr>";
	print "<td class='smalltext'>Shipping by Order Date</td>";
	for my $m(0..$#months){
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{'shipping'}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{'shipping'}[2])."</td>";
	}
	print "</tr>";
	
	
	###
	### Shipping Before First Month
	###
	my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(Shipping) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders_products.ShpDate)='$range{$months[0]}[2]'  AND ID_products > 100000   AND sl_orders.Status='Shipped'");
	while (($num,$amount) = $sth->fetchrow_array()) {
		#print "$months[$m]\t'shipping'\t$num\t$amount\n";
		$resp{$months[$m]}{'shipping'}[1] = $num;
		$resp{$months[$m]}{'shipping'}[2] = $amount;
	}
	
	###
	### Shipping by  Months
	###
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT COUNT(*)AS nums,SUM(Shipping) AS amounts FROM sl_orders_products, sl_orders WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR( sl_orders_products.ShpDate )=$range{$months[$m]}[2] AND MONTH( sl_orders_products.ShpDate )=$range{$months[$m]}[1]  AND ID_products > 100000  AND sl_orders.Status='Shipped'");
		while (($num,$amount) = $sth->fetchrow_array()) {
			#print "$months[$m]\t'shipping'\t$num\t$amount\n";
			$resp{$months[$m]}{'shipping'}[1] = $num;
			$resp{$months[$m]}{'shipping'}[2] = $amount;
		}
	}
	print "<tr>";
	print "<td class='smalltext'>Shipping by ShipDate Date</td>";
	for my $m(0..$#months){
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{'shipping'}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{'shipping'}[2])."</td>";
	}
	print "</tr>";
	
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(OrderShp) FROM `sl_orders` WHERE `Status`='Shipped'");
	($num,$amount) = $sth->fetchrow_array();
	print "<tr>";
	print "<td class='smalltext'>Totals</td>";
	print "<td class='smalltext' align='right'>".&format_number($num)."</td>";
	print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
	print "<td class='smalltext' align='right' colspan='".($#months*2)."'></td>";
	print "</tr>";

	print "</table>&nbsp;";
	
}

	
sub ax_ord_by_tdc {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	###
	### Credit Card Type
	###	
	print qq|<table border="0" cellspacing="0" width="250" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='3' align='center'>Sales Credit Card Type</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'>Type</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	my ($sth) = &Do_SQL("
	SELECT PmtField1,COUNT(*),SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') AND Type='Credit-Card'
AND sl_orders.Date>='$range{'from_date'}' and sl_orders.Date<='$range{'to_date'}'
GROUP BY PmtField1");	
	while (($name,$num,$amount) = $sth->fetchrow_array()) {
		print "<tr>";
		print "<td class='smalltext'>$name</td>";
		print "<td class='smalltext' align='right'>".&format_number($num)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_preord_by_week {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	###
	### Presale by Status
	###	
	print qq|<table border="0" cellspacing="0" width="250" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='3' align='center'>Presale by Status</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'>Status</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	my ($sth) = &Do_SQL("SELECT Status,COUNT(*),SUM(OrderNet) FROM sl_preorders WHERE Date>='$range{'from_date'}' AND Date<='$range{'to_date'}' GROUP BY Status");
	while (($name,$num,$amount) = $sth->fetchrow_array()) {
		print "<tr>";
		print "<td class='smalltext'>$name</td>";
		print "<td class='smalltext' align='right'>".&format_number($num)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	}
	print "</table>&nbsp;";
}


	
sub ax_fp_payments {
# ------------------------------------------------------
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	###
	### FLEXIPAGOS PAYMENTS
	###	
	print qq|<table border="0" cellspacing="0" width="250" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='3' align='center'>Flexipagos Payments</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'>Payments</td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	my ($sth) = &Do_SQL("SELECT num,count(num), sum(total)
							FROM (
							SELECT COUNT(*) AS num, SUM(Amount) as total FROM sl_orders,sl_orders_payments
							WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders.Status='Shipped' AND sl_orders.Date>='$range{'from_date'}'  AND sl_orders.Date<='$range{'to_date'}'  AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') AND Amount>0 AND Type = 'Credit-Card'
							GROUP BY (sl_orders_payments.ID_orders)) as fp
							GROUP BY num");
	while (@ary = $sth->fetchrow_array){
		print "<tr>";
		print "<td class='smalltext'>Orders with $ary[0] payments</td>";
		print "<td class='smalltext' align='right'>".&format_number($ary[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($ary[2])."</td>";
		print "</tr>";
	}
	print "</table>&nbsp;";	
}

sub ax_fp_aging {
# ------------------------------------------------------
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	
	### 
	### FLEXIPAGOS AGING
	###
	print qq|<table border="0" cellspacing="0" width="250" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='3' align='center'>Flexipagos - Aging</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'> </td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	
	my ($query) = "WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders_payments.Status<>'Cancelled' AND sl_orders.Date>='$range{'from_date'}'  AND sl_orders.Date<='$range{'to_date'}' AND sl_orders.Status='Shipped'";
	## FP Due (90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00') AND (Captured='No' OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (61-90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	## FP Due (31-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (31-60 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	

	## FP Due (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (1-30 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
		
	## FP Due (Today)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (Today)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	
	## FP AR (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (1-30 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	## FP AR (30-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (30-60 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";


	## FP AR (61-90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (61-90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	## FP AR (91 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00')  AND (Captured='No'OR CapDate='0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (91 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	
	## FP PAID
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (Captured='Yes' OR CapDate<>'0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (Captured='Yes' OR CapDate<>'0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>Paid</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	print "</table>&nbsp;";	
}

sub ax_fp_monterey {
# ------------------------------------------------------
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	
	### 
	### FLEXIPAGOS AGING
	###
	print qq|<table border="0" cellspacing="0" width="250" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='3' align='center'>Flexipagos - Monterey</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title' align='center'> </td>";
	print "<td class='menu_bar_title' align='center'>Qty</td>";
	print "<td class='menu_bar_title' align='center'>Amount</td>";
	print "</tr>";	
	
	my ($query) = "WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND sl_orders_payments.Status='Financed' AND sl_orders.Date>='$range{'from_date'}'  AND sl_orders.Date<='$range{'to_date'}' AND sl_orders.Status='Shipped'";
	## FP Due (90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-90 AND Paymentdate<>'0000-00-00')  ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-60 AND DATEDIFF(Paymentdate,Curdate())>=-90 AND Paymentdate<>'0000-00-00')  ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (61-90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	## FP Due (31-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<-30 AND DATEDIFF(Paymentdate,Curdate())>=-60 AND Paymentdate<>'0000-00-00') ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (31-60 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	

	## FP Due (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())<0 AND DATEDIFF(Paymentdate,Curdate())>=-30 AND Paymentdate<>'0000-00-00') ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (1-30 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
		
	## FP Due (Today)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (Paymentdate=Curdate() AND Paymentdate<>'0000-00-00') ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP Due (Today)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	
	## FP AR (1-30 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00') ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (1-30 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";
	
	## FP AR (30-60 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (30-60 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";


	## FP AR (61-90 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=90 AND Paymentdate<>'0000-00-00')  ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (61-90 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	## FP AR (91 days)
	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments $query AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00') ");
	my ($amount) = $sth->fetchrow;
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query  AND Type='Credit-Card' AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00')  ");
	my ($qty) = $sth->fetchrow;
		print "<tr>";
		print "<td class='smalltext'>FP AR (91 days)</td>";
		print "<td class='smalltext' align='right'>".&format_number($qty)."</td>";
		print "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
		print "</tr>";

	
	print "</table>&nbsp;";	
}

sub ax_by_categ {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (%resp,$num,$amount);

	###
	### Load Categories
	###
	my ($sth) = &Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active' AND ID_parent='0' ORDER BY Title;");
	while (($id_cat,$cat_name) = $sth->fetchrow_array()){
		push (@categories,$cat_name);
		push (@id_cat,$id_cat);
	}
	push (@categories,'Other');
	push (@id_cat,'x');
	my ($tnum,$amount);
	for my $i(0..$#id_cat-1){
		my ($query) = "WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]' AND ID_products > 100000
				 AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$id_cat[$i]') ";
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders $query");
		my ($num,$amount) = $sth->fetchrow_array();
		$resp{$months[0]}{$id_cat[$i]}[1] = $num;
		$resp{$months[0]}{$id_cat[$i]}[2] = $amount;
		$tnum += $num;
		$tamount += $amount;

	}
	my ($query) = "WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]' AND ID_products > 100000 ";
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders $query");
	my ($num,$amount) = $sth->fetchrow_array();
	$resp{$months[0]}{'x'}[1] = $num-$tnum;
	$resp{$months[0]}{'x'}[2] = $amount-$tamount;
	
	###
	### Orders by Status Months
	###
	for my $m(1..$#months){
		$tnum   = 0;
		$tamount = 0;
		for my $i(0..$#id_cat-1){
			my ($query) = "WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1] AND ID_products > 100000
					 AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT ID_products FROM sl_products_categories WHERE ID_top='$id_cat[$i]') ";
			my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders $query");
			my ($num,$amount) = $sth->fetchrow_array();
			$resp{$months[$m]}{$id_cat[$i]}[1] = $num;
			$resp{$months[$m]}{$id_cat[$i]}[2] = $amount;
			$tnum += $num;
			$tamount += $amount;
		}
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders 
				WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)=$range{$months[$m]}[2] AND MONTH(sl_orders.Date)=$range{$months[$m]}[1] AND ID_products > 100000");
		my ($num,$amount) = $sth->fetchrow_array();
		$resp{$months[$m]}{'x'}[1] = $num-$tnum;
		$resp{$months[$m]}{'x'}[2] = $amount-$tamount;
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>Categories</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By Category</td>";
	for my $m(0..$#months){
		print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	for my $s(0..$#id_cat){
		print "<tr>";
		print "<td class='smalltext'>$categories[$s]</td>";
		for my $m(0..$#months){
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$id_cat[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$id_cat[$s]}[2])."</td>";
		}
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_by_categ_min {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%range) = @_;
	my (@months) = split(',',$range{'months'});
	my (%resp,$num,$amount);

	###
	### Load Categories
	###
	my ($sth) = &Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active' AND ID_parent='0' ORDER BY Title;");
	while (($id_cat,$cat_name) = $sth->fetchrow_array()){
		push (@categories,$cat_name);
		push (@id_cat,$id_cat);
	}
	push (@categories,'Other');
	push (@id_cat,'x');
	my ($tnum,$amount);
	for my $i(0..$#id_cat-1){
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(sMin) FROM sl_orders_products,sl_orders,sl_shows_items WHERE sl_orders_products.ID_orders=sl_orders.ID_orders 
									AND sl_orders_products.Status='Active' 
									AND YEAR(sl_orders.Date)='$range{$months[0]}[2]' 
									AND sl_orders_products.ID_products > 100000
									AND sl_shows_items.ID_products=RIGHT(sl_orders_products.ID_products,6) 
									AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT sl_orders_products.ID_products 
									FROM sl_products_categories WHERE ID_top='$id_cat[$i]')");
		my ($num,$amount) = $sth->fetchrow_array();
		$resp{$months[0]}{$id_cat[$i]}[1] = $num;
		$resp{$months[0]}{$id_cat[$i]}[2] = $amount;
		$tnum += $num;
		$tamount += $amount;
		print "$num $amount<br>";
	}
	return;
	
	my ($query) = "WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)='$range{$months[0]}[2]' AND ID_products > 100000 ";
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders $query");
	my ($num,$amount) = $sth->fetchrow_array();
	$resp{$months[0]}{'x'}[1] = $num-$tnum;
	$resp{$months[0]}{'x'}[2] = $amount-$tamount;
	
	###
	### Orders by Status Months
	###
	for my $m(1..$#months){
		$tnum   = 0;
		$tamount = 0;
		for my $i(0..$#id_cat-1){
			my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(sMin) FROM sl_orders_products,sl_orders,sl_shows_items WHERE sl_orders_products.ID_orders=sl_orders.ID_orders 
									AND sl_orders_products.Status='Active' 
									AND YEAR(sl_orders.Date)='$range{$months[$m]}[2]' 
									AND sl_orders_products.ID_products > 100000
									AND sl_shows_items.ID_products=RIGHT(sl_orders_products.ID_products,6) 
									AND RIGHT(sl_orders_products.ID_products,6) IN (SELECT sl_orders_products.ID_products 
									FROM sl_products_categories WHERE ID_top='$id_cat[$i]')");
			my ($num,$amount) = $sth->fetchrow_array();
			$resp{$months[$m]}{$id_cat[$i]}[1] = $num;
			$resp{$months[$m]}{$id_cat[$i]}[2] = $amount;
			$tnum += $num;
			$tamount += $amount;
		}
		my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(SalePrice*Quantity) FROM sl_orders_products,sl_orders 
				WHERE sl_orders_products.ID_orders=sl_orders.ID_orders AND sl_orders_products.Status='Active' AND YEAR(sl_orders.Date)=$range{$months[$m]}[2] AND MONTH(sl_orders.Date)=$range{$months[$m]}[1] AND ID_products > 100000");
		my ($num,$amount) = $sth->fetchrow_array();
		$resp{$months[$m]}{'x'}[1] = $num-$tnum;
		$resp{$months[$m]}{'x'}[2] = $amount-$tamount;
	}
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='13' align='center'>Categories</td>";
	print "</tr>";
	print "<tr>";
	print "<td class='menu_bar_title'>By Category</td>";
	for my $m(0..$#months){
		print "<td class='menu_bar_title' colspan='2' align='center'>$months[$m]</td>";
	}
	print "</tr>";
	for my $s(0..$#id_cat){
		print "<tr>";
		print "<td class='smalltext'>$categories[$s]</td>";
		for my $m(0..$#months){
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$id_cat[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$id_cat[$s]}[2])."</td>";
		}
		print "</tr>";
	}
	print "</table>&nbsp;";
}

sub ax_good_bad_debti{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/05/08 09:24:39
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my (%range) = @_;;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount);
	
	#print "months = $range{'months'}<br>";
	#return;
	###
	### Flexipagos : Good v/s Bad Debt
	###
	#@months = ('Feb-08');
	print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
	print "<tr>";
	print "<td class='menu_bar_title' colspan='19' align='center'>Flexipagos - Analisis - Qty</td>";
	print "</tr>";
	print "<tr>";
		print "<td class='menu_bar_title'>FP Analisis</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Totals</td>";
#		print "<td class='menu_bar_title' colspan='2' align='center'>OK</td>";
#		print "<td class='menu_bar_title' colspan='2' align='center'>w/Errors</td>";
#		print "<td class='menu_bar_title' colspan='2' align='center'>Sgl Pmt</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Good Debt<=1500</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Good Debt>1500</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Bad Deb</td>";
		print "<td class='menu_bar_title' colspan='2' align='center'>Paid</td>";
	print "</tr>";	
	
	###########Será ésta parte entre septiembre de 2007 y la fecha actual############
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND Paymentdate between '2007-09-01' and Curdate() AND sl_orders_payments.Status IN ('Approved','Denied','Pending') GROUP BY ID_orders");
	IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
		#print "$months[0]\t$name\t$num\t$amount<br>";
		++$resp{$months[0]}{$status}[1];
		$resp{$months[0]}{$status}[2] += $amount;
		## Check Totals
		$tot_check = &check_ord_totals($id);
#		if ($tot_check  eq 'OK'){
#			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
#			if ($sth2->fetchrow >0){
#				## Tiene Returns
#				++$resp{$months[0]}{$status}[5];
#				$resp{$months[0]}{$status}[6] += $amount;
#			}else{
#				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
#				if ($sth2->fetchrow >0){
#					## Tiene Returns
#					++$resp{$months[0]}{$status}[5];
#					$resp{$months[0]}{$status}[6] += $amount;
#				}else{
#					++$resp{$months[0]}{$status}[3];
#					$resp{$months[0]}{$status}[4] += $amount;
#				}
#			}
#		}else{
#			++$resp{$months[0]}{$status}[5];
#			$resp{$months[0]}{$status}[6] += $amount;
#		}

		if ($tot_check  eq 'OK'){
			($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
			if ($payments eq 1){
#				++$resp{$months[0]}{$status}[11];
#				$resp{$months[0]}{$status}[12] += $amount;
			}elsif($pay_status eq 'GOOD'){
				++$resp{$months[0]}{$status}[19];
				$resp{$months[0]}{$status}[20] += $paid;
				
				if($amount<=1500)
				{
					++$resp{$months[0]}{$status}[13];
					$resp{$months[0]}{$status}[14] += $amount;
				}
				else
				{
					++$resp{$months[0]}{$status}[15];
					$resp{$months[0]}{$status}[16] += $amount;
				}
				
			}else{  #Bad
				if($amount<=1500)
				{
					$resp{$months[0]}{$status}[14] += ($amount-$unpaid);
				}
				else
				{
					$resp{$months[0]}{$status}[16] += ($amount-$unpaid);
				}
				#print "$id unpaid:$unpaid<br>";
				if ($pay_status  =~ /BAD/){
					++$resp{$months[0]}{$status}[17];
					$resp{$months[0]}{$status}[18] += $unpaid;
				}
#				elsif ($pay_status  eq 'BAD2'){
#					++$resp{$months[0]}{$status}[17];
#					$resp{$months[0]}{$status}[18] += $unpaid;
#				}else{
#					++$resp{$months[0]}{$status}[19];
#					$resp{$months[0]}{$status}[20] += $unpaid;
#				}
			}
		}
	}
	$status[$s] = 'Shipped';

	print "<tr>";
	print "<td class='smalltext'>$months[0]</td>";
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[1])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[2])."</td>";
	
	## Totals
#	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[3])."</td>";
#	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[4])."</td>";
#	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[5])."</td>";
#	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[6])."</td>";
#
#	## Sgl Payments
#	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[11])."</td>";
#	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[12])."</td>";
	
	## Good Debt
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[13])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[14])."</td>";		
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[15])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[16])."</td>";		

	## Bad Debt
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[17])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[18])."</td>";
	
	##Paid
	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[19])."</td>";
	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[20])."</td>";
	## Bad Debt  Mid
#	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[17])."</td>";
#	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[18])."</td>";
#	## Bad Debt  High >=3
#	print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[19])."</td>";
#	print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[20])."</td>";
	print "</tr>";
#	###########Termina la parte entre septiembre de 2007 y la fecha actual############
	
	my ($sth) = &Do_SQL("SELECT date_format( now( ) , '%Y-%m-%d' )");
	#my $firstdate='2007-09-01';
	my $firstdate=$sth->fetchrow;
	my $seconddate;
	#for my $m(1..25)#$#months)
	for my $m(1..$#months+1)
	{
		
		my ($sth1)=&Do_SQL("Select date_add('$firstdate',interval 14 day)");
		$seconddate=$sth1->fetchrow();
		#my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1] AND sl_orders_payments.Status IN ('Approved','Denied','Pending') GROUP BY ID_orders");
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND Paymentdate between '$firstdate' and '$seconddate' AND sl_orders_payments.Status IN ('Approved','Denied','Pending') GROUP BY ID_orders");
		IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
			#print "$months[$m]\t$name\t$num\t$amount<br>";
			++$resp{$months[$m]}{$status}[1];
			$resp{$months[$m]}{$status}[2] += $amount;
			## Check Totals
			$tot_check = &check_ord_totals($id);
#			if ($tot_check  eq 'OK'){
#				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
#				if ($sth2->fetchrow >0){
#					## Tiene Returns
#					++$resp{$months[$m]}{$status}[5];
#					$resp{$months[$m]}{$status}[6] += $amount;
#				}else{
#					my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
#					if ($sth2->fetchrow >0){
#						## Tiene Returns
#						++$resp{$months[$m]}{$status}[5];
#						$resp{$months[$m]}{$status}[6] += $amount;
#					}else{
#						++$resp{$months[$m]}{$status}[3];
#						$resp{$months[$m]}{$status}[4] += $amount;
#					}
#				}
#			}else{
#				++$resp{$months[0]}{$status}[5];
#				$resp{$months[0]}{$status}[6] += $amount;
#			}
			if ($tot_check  eq 'OK'){
				($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
				if ($payments eq 1){
#					++$resp{$months[$m]}{$status}[11];
#					$resp{$months[$m]}{$status}[12] += $amount;
				}elsif($pay_status eq 'GOOD'){
					++$resp{$months[$m]}{$status}[19];
					$resp{$months[$m]}{$status}[20] += $paid;
					if($amount<=1500)
					{
						++$resp{$months[$m]}{$status}[13];
						$resp{$months[$m]}{$status}[14] += $amount;
					}
					else
					{
						++$resp{$months[$m]}{$status}[15];
						$resp{$months[$m]}{$status}[16] += $amount;
					}
					
				}else{
					if($amount<=1500)
					{
						#$resp{$months[$m]}{$status}[14] += ($amount-$unpaid);
						$resp{$months[$m]}{$status}[14] += ($amount);
					}
					else
					{
						#$resp{$months[$m]}{$status}[16] += ($amount-$unpaid);
						$resp{$months[$m]}{$status}[16] += ($amount);
					}
					if ($pay_status  =~ /BAD/){
						++$resp{$months[$m]}{$status}[17];
						$resp{$months[$m]}{$status}[18] += $unpaid;
					}
				}
			}
		}
		$status[$s] = 'Shipped';

		print "<tr>";
		#print "<td class='smalltext'>$months[$m]</td>";
		print "<td class='smalltext'>$firstdate-$seconddate</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
		
		## Totals
#		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[3])."</td>";
#		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[4])."</td>";
#		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[5])."</td>";
#		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[6])."</td>";

		## Sgl Payments
#		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[11])."</td>";
#		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[12])."</td>";
		
		## Good Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[13])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[14])."</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[15])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[16])."</td>";			


		## Bad Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[17])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[18])."</td>";
		
		## Paid
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[19])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[20])."</td>";

		print "</tr>";
		$sth1=&Do_SQL("Select date_add('$seconddate',interval 1 day)");
		$firstdate=$sth1->fetchrow;
	}
	print "</table>&nbsp;";
}


sub ax_aranalisis {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($prnlist,%range) = @_;;
	my (@months) = split(',',$range{'months'});
	my (@status) = split(',',$range{'status'});
	my (%resp,$num,$amount,$query_pmts,$headermsg);
	
	### Only qith "qty" of payments
	if ($range{'qty_payments'} >0){
		$query_pmts = "AND $range{'qty_payments'}=(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND  Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled','Counter Finance'))";
		$headermsg  = "<br>Qty of Payment : $range{'qty_payments'}";
	}
	
	###
	### Flexipagos : Good v/s Bad Debt
	###
	



	if (!$prnlist){
		print qq|<table border="0" cellspacing="0" width="95%" class="formtable">\n|;
		print "<tr>";
		print "<td class='menu_bar_title' colspan='22' align='center'><b>Flexipagos - Analisis - Qty$headermsg</b></td>";
		print "</tr>";
		print "<tr>";
			print "<td class='menu_bar_title'>AR Analisis</td>";
			print "<td class='menu_bar_title' colspan='2' align='center'>Totals</td>";        ## 1/2
			print "<td class='menu_bar_title' colspan='2' align='center'>OK</td>";            ## 3/4
			print "<td class='menu_bar_title' colspan='2' align='center'>w/Errors</td>";      ## 5/6
			print "<td class='menu_bar_title' colspan='2' align='center'>Paid</td>";          ## 7/8
			print "<td class='menu_bar_title' colspan='4' align='center'>Financed (Paid/Financed))</td>";      ## 9/10
			print "<td class='menu_bar_title' colspan='4' align='center'>On Collection (Paid/On Collection)</td>"; ## 11/12
			print "<td class='menu_bar_title' colspan='2' align='center'>AR Good Debt</td>";  ## 13/14
			print "<td class='menu_bar_title' colspan='2' align='center'>AR Bad Debt</td>";   ## 15/16
		print "</tr>";
	}
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[0]}[2] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled','Counter Finance') $query_pmts GROUP BY ID_orders");
	IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
		#print "$months[0]\t$name\t$num\t$amount<br>";
		++$resp{$months[0]}{$status}[1];
		$resp{$months[0]}{$status}[2] += $amount;
		## Check Totals
		$tot_check = &check_ord_totals($id);
		if ($tot_check  eq 'OK'){
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('On Collection')");
			if ($sth2->fetchrow >0){
				## Load Payments
				($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
				
				## Orden On Collection
				++$resp{$months[0]}{$status}[11];
				$resp{$months[0]}{$status}[12] += $amount-$paid;
				++$resp{$months[0]}{$status}[19];
				$resp{$months[0]}{$status}[20] += $paid;
				
			}else{
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status='Financed'");
				if ($sth2->fetchrow >0){
					## Load Payments
					($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
	
					## Orden Financiada
					++$resp{$months[0]}{$status}[9];
					$resp{$months[0]}{$status}[10] += $amount-$paid;
					++$resp{$months[0]}{$status}[17];
					$resp{$months[0]}{$status}[18] += $paid;
				}else{
					my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
					if ($sth2->fetchrow >0){
						## Tiene Returns
						++$resp{$months[0]}{$status}[5];
						$resp{$months[0]}{$status}[6] += $amount;
					}else{
						my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
						if ($sth2->fetchrow >0){
							## Tiene Returns
							++$resp{$months[0]}{$status}[5];
							$resp{$months[0]}{$status}[6] += $amount;
						}else{
							## Total OK
							++$resp{$months[0]}{$status}[3];
							$resp{$months[0]}{$status}[4] += $amount;
							
							## Good and Bad AR and Paid
							($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
							if ($payments eq 1){
								++$resp{$months[0]}{$status}[7];
								$resp{$months[0]}{$status}[8] += $amount;
							}elsif($pay_status eq 'GOOD'){
								## Paid
								++$resp{$months[0]}{$status}[7];
								$resp{$months[0]}{$status}[8] += $paid;
								
								## Good AR
								++$resp{$months[0]}{$status}[13];
								$resp{$months[0]}{$status}[14] += $unpaid;
								
							}else{  #Bad
								## Paid
								++$resp{$months[0]}{$status}[7];
								$resp{$months[0]}{$status}[8] += $paid;
								
								## Bad AR
								++$resp{$months[0]}{$status}[15];
								$resp{$months[0]}{$status}[16] += $unpaid;
							}							
							
						}
					}
				}
			}
		}else{
			++$resp{$months[0]}{$status}[5];
			$resp{$months[0]}{$status}[6] += $amount;
		}
	}
	$status[$s] = 'Shipped';

	if (!$prnlist){
		print "<tr>";
		print "<td class='smalltext'>$months[0]</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[1])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[2])."</td>";
		
		## Totals OK
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[3])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[4])."</td>";
		
		## Totals Error
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[5])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[6])."</td>";
	
		## Paid
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[7])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[8])."</td>";
		
		## Financed
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[17])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[18])."</td>";		
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[9])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[10])."</td>";			
	
		## On collection
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[19])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[20])."</td>";
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[11])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[12])."</td>";
		
		## Good Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[13])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[14])."</td>";
		## Bad Debt
		print "<td class='smalltext' align='right'>".&format_number($resp{$months[0]}{$status[$s]}[15])."</td>";
		print "<td class='smalltext' align='right'>".&format_price($resp{$months[0]}{$status[$s]}[16])."</td>";
		print "</tr>";
	}
	
	for my $m(1..$#months){
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Status,SUM(Amount) FROM sl_orders_payments, sl_orders WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders AND Type='Credit-Card' AND sl_orders.Status='Shipped' AND YEAR( sl_orders.Date )=$range{$months[$m]}[2] AND MONTH( sl_orders.Date )=$range{$months[$m]}[1] AND sl_orders_payments.Status NOT IN ('Credit','ChargeBack','Void','Order Cancelled','Cancelled') $query_pmts GROUP BY ID_orders");
		IDORDEN: while (my ($id,$status,$amount) = $sth->fetchrow_array){
			#print "$months[$m]\t$name\t$num\t$amount<br>";
			++$resp{$months[$m]}{$status}[1];
			$resp{$months[$m]}{$status}[2] += $amount;
			## Check Totals
			$tot_check = &check_ord_totals($id);
			if ($tot_check  eq 'OK'){
				my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status = 'On Collection'");
				$oncollect = $sth2->fetchrow;
				if ($oncollect>0){
					## Load Payments
					($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
					## Orden On Collection
					++$resp{$months[$m]}{$status}[11];
					$resp{$months[$m]}{$status}[12] += $oncollect;
					++$resp{$months[$m]}{$status}[19];
					$resp{$months[$m]}{$status}[20] += $paid;					
				}else{
					my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status='Financed'");
					$financed = $sth2->fetchrow;
					if ($financed>0){
						## Load Payments
						($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
						
						## Orden Financiada
						++$resp{$months[$m]}{$status}[9];
						$resp{$months[$m]}{$status}[10] += $financed;
						++$resp{$months[$m]}{$status}[17];
						$resp{$months[$m]}{$status}[18] += $paid;
					}else{
						my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id  AND sl_orders_payments.Status IN ('Credit','ChargeBack','Order Cancelled')");
						if ($sth2->fetchrow >0){
							## Tiene Returns
							++$resp{$months[$m]}{$status}[5];
							$resp{$months[$m]}{$status}[6] += $amount;

						}else{
							my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id  AND SalePrice<0 AND Status<>'Cancelled'");
							if ($sth2->fetchrow >0){
								## Tiene Returns
								++$resp{$months[$m]}{$status}[5];
								$resp{$months[$m]}{$status}[6] += $amount;
							}else{
								## Total OK
								++$resp{$months[$m]}{$status}[3];
								$resp{$months[$m]}{$status}[4] += $amount;
								
								## Good and Bad AR and Paid
								if ($prnlist){
									&print_payments_qty($id,$prnlist);
								}else{
									($payments,$pay_status,$paid,$unpaid) = &check_payments_qty($id);
									if ($payments eq 1){
										++$resp{$months[$m]}{$status}[7];
										$resp{$months[$m]}{$status}[8] += $amount;
									}elsif($pay_status eq 'GOOD'){
										## Paid
										++$resp{$months[$m]}{$status}[7];
										$resp{$months[$m]}{$status}[8] += $paid;
										
										## Good AR
										++$resp{$months[$m]}{$status}[13];
										$resp{$months[$m]}{$status}[14] += $unpaid;
										
									}else{  #Bad
										## Paid
										++$resp{$months[$m]}{$status}[7];
										$resp{$months[$m]}{$status}[8] += $paid;
										if ($paid<0){
											$outstr = qq|
										($payments,$pay_status,$paid,$unpaid) = check_payments_qty($id);
select COUNT(*),SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND Status  IN ('Approved','Denied','Pending','Financed','On Collection')

SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND(DATEDIFF(Paymentdate,Curdate())<=-5 AND Paymentdate<>'0000-00-00') AND (Captured='No'OR CapDate='0000-00-00') AND (AuthCode<>'' OR AuthCode IS NOT NULL OR AuthCode<>'0000') AND Status IN ('Approved','Denied','Pending')

select SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection')
select SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$order' AND Type='Credit-Card' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied','Pending','Financed','On Collection')
											
											|; #'
											#$outstr =~ s/\n/<br><br>/g;
											#&cgierr($outstr);
											
										}
										
										
										## Bad AR
										++$resp{$months[$m]}{$status}[15];
										$resp{$months[$m]}{$status}[16] += $unpaid;
									}							
								}
							}
						}
					}
				}
			}else{
				++$resp{$months[$m]}{$status}[5];
				$resp{$months[$m]}{$status}[6] += $amount;
			}
		}
		if (!$prnlist){
			print "<tr>";
			print "<td class='smalltext'>$months[$m]</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[1])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[2])."</td>";
			
			## Totals OK
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[3])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[4])."</td>";
			
			## Totals Err
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[5])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[6])."</td>";
	
			## Paid
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[7])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[8])."</td>";
			
			## Financed
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[17])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[18])."</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[9])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[10])."</td>";			
	
	
			## On collection
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[19])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[20])."</td>";
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[11])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[12])."</td>";
	
			## Good Debt
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[13])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[14])."</td>";
	
			## Bad Debt
			print "<td class='smalltext' align='right'>".&format_number($resp{$months[$m]}{$status[$s]}[15])."</td>";
			print "<td class='smalltext' align='right'>".&format_price($resp{$months[$m]}{$status[$s]}[16])."</td>";
			print "</tr>";
		}
	}
	if (!$prnlist){
		print "</table>&nbsp;";
	}
}


sub ax_set_report_background {
# --------------------------------------------------------
# Created :  Huitzilihuitl Ceja 06/10/2017 10:19:35 AM
# Last Update : 
# Locked by : 
# Description : Toma los datos que 
#
#
	my( $cmd, $parameters, $sql ) = @_;

    $sql =~ s/^\s+|\s+$|//g;
	$sql =~ s/\'/\"/g;
	#$sql =~ s/\"/\"/g;

	my %qty_status = { 'New'=>0, 'Processing'=>0, 'Finished'=>0 };
	my %id_report = { 'New'=>0, 'Processing'=>0, 'Finished'=>0 };
	my %result, $status;

    $cmd_check = ($cmd =~ /^repmans/)? 'repmans' : $cmd;

	## ...verifica si el reporte solicitado esta configurado para solicitarse por Background
	my $sth = &Do_SQL("SELECT COUNT(*) exist FROM sl_vars_config WHERE Command = 'ax_set_report_background' AND Code = '$cmd_check';");
	my $exist = $sth->fetchrow_array();

	if( $exist == 0 )
	{
		## En caso de no este registrado en sl_vars_config envia el mensaje de "Fail" que 
		## del lado del subrutina del reporte debera continuar con su ejecución normal
		$result{'status'} = 'Fail';
		return \%result;
	}

	## Busca si el reporte con los mismos parametros ha sido solicitado con anterioridad, y en que status se encuentra ...
	my ($sth) = &Do_SQL("SELECT MAX(id_background_reports) id, status, COUNT(*) exist 
	                    FROM sl_background_reports 
	                    WHERE 
                            cmd='$cmd' AND 
                            parameters='$parameters' AND 
                            query='$sql' AND 
                            status NOT IN('To Cancel', 'Cancelled', 'Delete')
	                    GROUP BY status;");

	while( my($id, $status, $exist) = $sth->fetchrow_array())
	{
	    $qty_status{$status} = $exist;
	    $id_report{$status} = $id;
	}

	## ... pues en caso de encontrarse en proceso o ya extraido el proceso omitir crear una nueva solicitud, ...
	if( $qty_status{'Finished'}>0 || $qty_status{'New'}>0 || $qty_status{'Processing'}>0 )
	{
	    if( $qty_status{'Finished'}>0 ){
	        $status = 'Finished'; 
	    }elsif( $qty_status{'Processing'}>0 ){
	        $status = 'Processing';
	    }elsif( $qty_status{'New'}>0 ){
	        $status = 'New';
	    }

	    $result{'status'} = $status;
	    $result{'id'} = $id_report{$status};
	}
	## ... o en caso de no haberse hecho esta solicitud con anterioridad ...
	elsif( $qty_status{'New'}==0 && $qty_status{'Processing'}==0 && $qty_status{'Processing'}==0 )
	{
	    ## ... registrala en sl_background_reports.
	    my ($sth) = &Do_SQL("INSERT INTO sl_background_reports (cmd, parameters, query, status, date, time, id_admin_users) 
	                        VALUES
	                        ('".$cmd."','".$parameters."','".$sql."', 'New',Curdate(),Curtime(),'".$usr{'id_admin_users'}."')");
	    $result{'status'} = 'New';
	    $result{'id'} = $sth->{'mysql_insertid'};

	}

    ## Se registra en sl_reports_asked_by el usuario que hace la solicitud.
    &Do_SQL("INSERT INTO sl_reports_asked_by (id_background_reports, status, date, time, id_admin_users) 
            VALUES ('".$result{'id'}."','Waiting', Curdate(), Curtime(), '".$usr{'id_admin_users'}."');");


	return \%result;

}


1;