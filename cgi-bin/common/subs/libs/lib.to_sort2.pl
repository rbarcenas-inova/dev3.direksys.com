sub report_orders {
# --------------------------------------------------------
	my ($query);
	my (@ary_st) = ('New', 'Processed', 'Pending', 'Shipped', 'Cancelled', 'Void');
	my (@ary_pt) = ('Credit-Card', 'Check', 'WesternUnion', 'Money Order', 'Flexipago', 'COD');
	## Headers
	$va{'title_prdsts'} = '';
	for my $x (0..$#ary_st){
		$va{'title_status'} .= qq|<td class="menu_bar_title" align="center">$ary_st[$x]</td>\n|;
	}

	## Orders by Payment Type
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)),sl_orders.Status,Type FROM sl_orders INNER JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders GROUP BY Status,Type");
	while (my($qty,$status,$pt)  = $sth->fetchrow_array()){
		$va{lc($pt).'_'.lc($status)}	 = &format_number($qty);
	}
	$va{'paytype'} = '';
	for my $x (0..$#ary_pt){
		$va{'paytype'} .= "<tr>\n<td class='smalltext' nowrap>$ary_pt[$x]</td>\n";
		for my $i (0..$#ary_st){
			(!$va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}) and ($va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}='---');
			$va{'paytype'} .= qq|		  	<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=advSearch&paytbl=1&Status=$ary_st[$i]&Type=$ary_pt[$x]&sb=id_orders&so=DESC')">$va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}</td>\n|;
		}
		$va{'paytype'} .= "<tr>\n";
	}


	## Orders by Payment Type
	my (@ary_st) = ('New', 'Pending', 'In Process', 'Paid', 'Expired', 'Void', 'Cancelled');
	$va{'title_prdsts'} = '';
	for my $x (0..$#ary_st){
		$va{'title_pstatus'} .= qq|<td class="menu_bar_title" align="center">$ary_st[$x]</td>\n|;
	}
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)),sl_orders.Status,Type FROM sl_orders INNER JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders GROUP BY Status,Type");
	while (my($qty,$status,$pt)  = $sth->fetchrow_array()){
		$va{lc($pt).'_'.lc($status)}	 = &format_number($qty);
	}
	$va{'ppaytype'} = '';
	for my $x (0..$#ary_pt){
		$va{'ppaytype'} .= "<tr>\n<td class='smalltext' nowrap>$ary_pt[$x]</td>\n";
		for my $i (0..$#ary_st){
			(!$va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}) and ($va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}='---');
			$va{'ppaytype'} .= qq|		  	<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=advSearch&paytbl=1&Status=$ary_st[$i]&Type=$ary_pt[$x]&sb=id_orders&so=DESC')">$va{lc($ary_pt[$x]).'_'.lc($ary_st[$i])}</td>\n|;
		}
		$va{'ppaytype'} .= "<tr>\n";
	}
	
	return &build_page('func:orders.html');	
}

sub report_orders_adv {
# --------------------------------------------------------
	### Orders
	my (@ary_q1name) = ('all','nw', 'pr', 'pe', 'ca', 'sh', 'rv', 'rt', 'ps',
						'flall','flnw', 'flpr', 'flpe', 'flca', 'flsh','flrv', 'flrt', 'flps',
						'caall','canw', 'capr', 'cape', 'caca', 'cash', 'carv', 'cart', 'caps',
						'prall','prnw', 'prpr', 'prpe', 'prca', 'prsh', 'prrv', 'prrt', 'prps');
	my (@ary_query1) = ('',"Status='New'", "Status='Processed'", "Status='Pending'", "Status='Cancelled'", "Status='Shipped'", "Status='Void'",
				"shp_State='FL-Florida'","Status='New' AND shp_State='FL-Florida'", "Status='Processed' AND shp_State='FL-Florida'", "Status='Pending' AND shp_State='FL-Florida'", "Status='Cancelled' AND shp_State='FL-Florida'", "Status='Shipped' AND shp_State='FL-Florida'","Status='Review' AND shp_State='FL-Florida'","Status='Returned' AND shp_State='FL-Florida'","Status='Postdated' AND shp_State='FL-Florida'",
				"shp_State='CA-California'","Status='New' AND shp_State='CA-California'", "Status='Processed' AND shp_State='CA-California'", "Status='Pending' AND shp_State='CA-California'", "Status='Cancelled' AND shp_State='CA-California'", "Status='Shipped' AND shp_State='CA-California'", "Status='Review' AND shp_State='CA-California'", "Status='Returned' AND shp_State='CA-California'", "Status='Postdated' AND shp_State='CA-California'",
				"shp_State='PR-Puerto Rico'","Status='New' AND shp_State='PR-Puerto Rico'", "Status='Processed' AND shp_State='PR-Puerto Rico'", "Status='Pending' AND shp_State='PR-Puerto Rico'", "Status='Cancelled' AND shp_State='PR-Puerto Rico'", "Status='Shipped' AND shp_State='PR-Puerto Rico'", "Status='Review' AND shp_State='PR-Puerto Rico'", "Status='Returned' AND shp_State='PR-Puerto Rico'", "Status='Postdated' AND shp_State='PR-Puerto Rico'");
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($ary_query1[$i] = "WHERE $ary_query1[$i]");
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders $ary_query1[$i]");
		$va{'ords_'.$ary_q1name[$i]}= &format_number($sth->fetchrow);
	}
	
	### Orders / Products / w/pl
	my (@ary_q1name) = ('all','nw', 'pr', 'pe', 'ca', 'sh', 'rv', 'rt', 'ps',);
	my (@ary_query1) = ("","sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Review'", "sl_orders.Status='Void'");
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($ary_query1[$i] = "AND $ary_query1[$i]");
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders_products.Status='Active' AND sl_orders_products.ID_packinglist>0 $ary_query1[$i]");
		$va{'gpl_'.$ary_q1name[$i]}= &format_number($sth->fetchrow);
	}
	### Orders / Products / wo/pl
	my (@ary_q1name) = ('all','nw', 'pr', 'pe', 'ca', 'sh', 'rv', 'rt', 'ps',);
	my (@ary_query1) = ("","sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Review'", "sl_orders.Status='Returned'", "sl_orders.Status='Postdated'");
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($ary_query1[$i] = "AND $ary_query1[$i]");
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active' AND (sl_orders_products.ID_packinglist=0 OR ISNULL(sl_orders_products.ID_packinglist)) $ary_query1[$i]");
		$va{'gnpl_'.$ary_q1name[$i]}= &format_number($sth->fetchrow);
	}	
	### Orders / Products / w / Drop Shipment
	my (@ary_q1name) = ('all','nw', 'pr', 'pe', 'ca', 'sh', 'rv', 'rt', 'ps',);
	my (@ary_query1) = ("","sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Review'", "sl_orders.Status='Returned'", "sl_orders.Status='Postdated'");
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($ary_query1[$i] = "AND $ary_query1[$i]");
		my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active' AND 'Yes'=(SELECT DropShipment FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6)) $ary_query1[$i]");
		$va{'ds_'.$ary_q1name[$i]}= &format_number($sth->fetchrow);
	}

	### Orders / Products / w / Multiples
	my (@ary_q1name) = ('all','nw', 'pr', 'pe', 'ca', 'sh', 'rv', 'rt', 'ps',);
	my (@ary_query1) = ("","sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Review'", "sl_orders.Status='Returned'", "sl_orders.Status='Postdated'");
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($ary_query1[$i] = " $ary_query1[$i] AND");
		my ($sth) = &Do_SQL("select count(sl_orders.id_orders) from sl_orders where  $ary_query1[$i] sl_orders.id_orders in ( select id_orders  from sl_orders_products  where sl_orders_products.id_orders = sl_orders.id_orders  ) and 1 < (select count(sl_orders_products.id_products) from sl_products,sl_orders_products where sl_products.id_products=RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders=sl_orders.id_orders) ");
		$va{'gml_'.$ary_q1name[$i]}= &format_number($sth->fetchrow);
	}

	
	### Orders / Payments
	my ($query);
	my (@ary_q1name) = ('all','new', 'processed', 'pending', 'cancelled', 'shipped', 'void');
	my (@ary_query1) = ('',"sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Void'");
	my (@ary_q2name) = ('t', 'fl', 'cc', 'chk','wu');
	my (@ary_query2) = ('',"Type='Flexipago'" , "Type='Credit-Card'", "Type='Check'", "Type='WesternUnion'");
	for my $i(0..$#ary_q1name){
		for my $x(0..$#ary_q2name){
			if ($ary_query1[$i] and $ary_query2[$x]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query1[$i] AND $ary_query2[$x]";
			}elsif ($ary_query2[$x]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query2[$x]";
			}elsif ($ary_query1[$i]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query1[$i]";
			}else{
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders";
			}
			my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query");
			$va{'pay_'.$ary_q1name[$i].'_'.$ary_q2name[$x]}= &format_number($sth->fetchrow);
		}
	}
	
	my ($query);
	my (@ary_q1name) = ('all','new', 'processed', 'pending', 'cancelled', 'shipped', 'void');
	my (@ary_query1) = ('',"sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='Void'");
	my (@ary_q2name) = ('d','w','lw');
	my (@ary_query2) = ("DATE_FORMAT(sl_orders.date,'%Y-%m-%d') = CURDATE()","DATE_FORMAT(sl_orders.date,'%Y-%v') = DATE_FORMAT(CURDATE(),'%Y-%v')","DATE_FORMAT(sl_orders.date,'%Y-%v')=DATE_FORMAT(DATE_SUB(CURDATE(),INTERVAL 1 WEEK),'%Y-%v')");	
	for my $i(0..$#ary_q1name){	
		for my $x(0..$#ary_q2name){	
			if ($ary_query1[$i] and $ary_query2[$x]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query1[$i] AND $ary_query2[$x]";
			}elsif ($ary_query2[$x]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query2[$x]";
			}else{
				$query = " WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders";
			}
			my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments $query ");
			$va{'date_'.$ary_q1name[$i].'_'.$ary_q2name[$x]}= &format_number($sth->fetchrow);
		}
	}
	return &build_page('func:orders_adv.html');	
}

sub report_orders_links {
# --------------------------------------------------------
	my (@ary_st) = ('New', 'Processed', 'Pending', 'Shipped', 'Cancelled', 'Void');
	my (@ary_prd) = ('Out of Stock', 'In Fulfillment', 'In Dropshipment', 'Dropship Sent', 'Partial Shipment', 'Partial Dropship', 'For Return', 'For Exchange', 'For Re-Ship', 'Undeliverable', 'In Claim', 'None');
	my (@ary_pay) = ('Review Order', 'Review Address', 'Payment Declined', 'Insufficient Funds', 'Post-Dated', 'For Refund', 'Pending Payment', 'Pending Refund', 'FP:Review Payment', 'FP:Insufficient Funds', 'Oasis', 'On Collection', 'Void', 'ChargeBack', 'Pending Buy Back', 'Layaway Due', 'In Bankruptcy', 'None');

	## Headers
	$va{'title_prdsts'} = '';
	for my $x (0..$#ary_st){
		$va{'title_status'} .= qq|<td class="menu_bar_title" align="center">$ary_st[$x]</td>\n|;
	}

	## Status
	my ($sth) = &Do_SQL("SELECT COUNT(*),Status FROM sl_orders GROUP BY Status");
	while (my($qty,$status)  = $sth->fetchrow_array()){
		$va{lc($status).'_t'}	 = &format_number($qty);
	}
	for my $i (0..$#ary_st){
		(!$va{lc($ary_prd[$x]).'_'.lc($ary_st[$i])}) and ($va{lc($ary_prd[$x]).'_'.lc($ary_st[$i])}='---');
		$va{'sts_links'} .= qq|<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=advSearch&status=$ary_st[$i]&sb=id_orders&so=DESC')">$va{lc($ary_st[$i]).'_t'}</td>\n|;
	}

	## Prd Status
	my ($sth) = &Do_SQL("SELECT COUNT(*),Status,StatusPrd FROM sl_orders GROUP BY Status,StatusPrd");
	while (my($qty,$status,$prd)  = $sth->fetchrow_array()){
		$va{lc($prd).'_'.lc($status)}	 = &format_number($qty);
	}
	$va{'prd_links'} = '';
	for my $x (0..$#ary_prd){
		$va{'prd_links'} .= "<tr>\n<td class='smalltext' nowrap>$ary_prd[$x]</td>\n";
		for my $i (0..$#ary_st){
			(!$va{lc($ary_prd[$x]).'_'.lc($ary_st[$i])}) and ($va{lc($ary_prd[$x]).'_'.lc($ary_st[$i])}='---');
			$va{'prd_links'} .= qq|<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=advSearch&status=$ary_st[$i]&StatusPrd=$ary_prd[$x]&sb=id_orders&so=DESC')">$va{lc($ary_prd[$x]).'_'.lc($ary_st[$i])}</td>\n|;
		}
		$va{'prd_links'} .= "<tr>\n";
	}
	
	## Pay Status
	my ($sth) = &Do_SQL("SELECT COUNT(*),Status,StatusPay FROM sl_orders GROUP BY Status,StatusPay");
	while (my($qty,$status,$pay)  = $sth->fetchrow_array()){
		$va{lc($pay).'_'.lc($status)}	 = &format_number($qty);
	}
	$va{'pay_links'} = '';
	for my $x (0..$#ary_pay){
		$va{'pay_links'} .= "<tr>\n<td class='smalltext' nowrap>$ary_pay[$x]</td>\n";
		for my $i (0..$#ary_st){
			(!$va{lc($ary_pay[$x]).'_'.lc($ary_st[$i])}) and ($va{lc($ary_pay[$x]).'_'.lc($ary_st[$i])}='---');
			$va{'pay_links'} .= qq|<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=advSearch&status=$ary_st[$i]&StatusPay=$ary_pay[$x]&sb=id_orders&so=DESC')">$va{lc($ary_pay[$x]).'_'.lc($ary_st[$i])}</td>\n|;
		}
		$va{'pay_links'} .= "<tr>\n";
	}	
	
	return &build_page('func:orders_links.html');	
}



sub report_products {
# --------------------------------------------------------
	my ($query);
	my (@ary_q1name) = ('all','new', 'processed', 'pending', 'cancelled', 'shipped','void');
	my (@ary_query1) = ('',"sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'","sl_orders.Status='Void'");
	my (@ary_q2name) = ('t', 'fl', 'cc', 'chk','wu');
	my (@ary_query2) = ('',"State='FL-Florida'" , "Type='Credit-Card'", "Type='Check'", "Type='WesternUnion'");
	for my $i(0..$#ary_q1name){
		for my $x(0..$#ary_q2name){
			if ($ary_query1[$i] and $ary_query2[$x]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query1[$i] AND $ary_query2[$x])";								
			}elsif ($ary_query2[$x]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query2[$x])";				
			}elsif ($ary_query1[$i]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query1[$i])";				
			}else{
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders )";				
			}
			my ($sth) = &Do_SQL("select count(sl_orders_products.ID_products) FROM sl_products,sl_orders_products $query");
			$va{$ary_q1name[$i].'_'.$ary_q2name[$x]}= &format_number($sth->fetchrow);
		}
	}
	
	my ($query);
	my (@ary_q1name) = ('all','new', 'processed', 'pending', 'cancelled', 'shipped','void');
	my (@ary_query1) = ('',"sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'","sl_orders.Status='Void'");
	my (@ary_q2name) = ('mt', 'mfl', 'mcc', 'mchk','mwu');
	my (@ary_query2) = ('',"State='FL-Florida'" , "Type='Credit-Card'", "Type='Check'", "Type='WesternUnion'");
	for my $i(0..$#ary_q1name){
		for my $x(0..$#ary_q2name){
			if ($ary_query1[$i] and $ary_query2[$x]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query1[$i] AND $ary_query2[$x])";
			}elsif ($ary_query2[$x]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query2[$x])";
			}elsif ($ary_query1[$i]){
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders AND $ary_query1[$i])";
			}else{
				$query = " WHERE '$in{'id_products'}' = sl_products.id_products and sl_products.id_products = RIGHT(sl_orders_products.id_products,6) and sl_orders_products.id_orders in( select sl_orders.id_orders from sl_orders,sl_orders_payments where sl_orders_products.id_orders=sl_orders.id_orders AND sl_orders_payments.id_orders=sl_orders.id_orders)";
			}
			my ($sth) = &Do_SQL("select sum(sl_orders_products.SalePrice) FROM sl_products,sl_orders_products $query ");			                                 
			$va{$ary_q1name[$i].'_'.$ary_q2name[$x]}= &format_price($sth->fetchrow);
		}
	}
	

	return &build_page('func:products.html');	
}

sub report_flexpay {
# --------------------------------------------------------
	my ($query);
	my (@ary_q1name) = ('all','test', 'ona', 'wo', 'act','ina');
	my (@ary_query1) = ('',"Status='Testing'","Status='On-Air'","Status='Web Only'","Status='Active'","Status='Inactive'");
	for my $i(0..$#ary_q1name){
		for my $x(1..6){
			if ($ary_query1[$i]){
				$query = " WHERE $ary_query1[$i] AND Flexipago=$x";
			}else{
				$query = " WHERE Flexipago=$x";
			}
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products $query ");
			$va{$ary_q1name[$i].'_'.$x}= &format_number($sth->fetchrow);
		}
	}
	return &build_page('func:flexpay.html');	
}

sub report_orders_fp {
# --------------------------------------------------------
	my ($query);
	my (@ary_q1name) = ('all','due','today', 'tweek', 'nweek', 'tmonth', 'nmonth');
	my (@ary_query1) = ("(Paymentdate<>'Approved')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%m-%d')<CURDATE() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%m-%d')=CURDATE() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%v')=DATE_FORMAT(CURDATE(),'%Y-%v')  AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%v')=DATE_FORMAT(DATE_ADD(CURDATE(),INTERVAL 1 WEEK),'%Y-%v') AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%m')=DATE_FORMAT(CURDATE(),'%Y-%m') AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')",
		"(DATE_FORMAT(sl_orders_payments.Paymentdate,'%Y-%m')=DATE_FORMAT(DATE_ADD(CURDATE(),INTERVAL 1 MONTH),'%Y-%m') AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')");
	my (@ary_q2name) = ('all','new', 'processed', 'review', 'returned', 'pending', 'cancelled', 'shipped', 'postdated');
	my (@ary_query2) = ('',"sl_orders.Status='New'","sl_orders.Status='Processed'","sl_orders.Status='Review'",
		"sl_orders.Status='Returned'","sl_orders.Status='Pending'","sl_orders.Status='Cancelled'","sl_orders.Status='Shipped'","sl_orders.Status='Postdated'");
	for my $i(0..$#ary_q1name){
		for my $x(0..$#ary_q2name){
			if ($ary_query2[$x]){
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query1[$i] AND $ary_query2[$x]";
			}else{
				$query = " WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND $ary_query1[$i] ";
			}
			my ($sth) = &Do_SQL("SELECT SUM(sl_orders_payments.Amount) FROM sl_orders,sl_orders_payments $query ");
			$va{$ary_q2name[$x].'_'.$ary_q1name[$i]} = &format_price($sth->fetchrow);
			#"SELECT SUM(sl_orders_payments.Amount) FROM sl_orders,sl_orders_payments $query ";
			#;
		}
	}
	return &build_page('func:orders_fp.html');	
}

sub build_select_paymentterms {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_popt'});	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		#$output .= "<input type='checkbox' name='paymentterms' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_poshpvia {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# 
# Modified on : 12/20/2007
# Modified by : Rafael Sobrino
# Notes :

	my ($output);
	my (@ary) = split(/,/,$cfg{'po_shpvia'});	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		#$output .= "<input type='checkbox' name='paymentterms' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub order_customerid {
# --------------------------------------------------------
# Last Modified on: 07/22/08 18:00:52
# Last Modified by: MCC C. Gabriel Varela S: Se contempla tambi?n para follow-up

	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			$in{'customers.'.lc($key)} = uc($rec->{$key});
			#$script_url=~/cgi-bin\/(.*)\//;
			# 	
			#if($script_url =~ /admin/){
			#	#$in{'customers.'.lc($key)} = $rec->{$key};
			#}else{
			#	#$in{lc($key)} = $rec->{$key};
			#}
		}
	}
	
	if ($in{'add'}){
		return &build_page('forms:customers_add.html');
	}elsif($in{'search'}) {
		return &build_page('forms:customers_search.html');
	}else{
		return &build_page('forms:customers_info.html');
	}
		
	#return qq|<input type="text" name="id_products_exchange" value="[in_id_products_exchange]" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'><a href="#productsexchange" id="productsexchange" onClick="document.getElementById('ex').checked=true;add_ritem()"><img src="[va_imgurl]/[ur_pref_style]/icsearchsmall.gif" border="0"></a>|;
}

sub excange_desc{
# --------------------------------------------------------
	if ($in{'id_products_exchange'}){
		return "<span class='help_on'>".&load_db_names('sl_products','ID_products',substr($in{'id_products_exchange'},3,6),'[Model]<br>[Name]').&load_choices($in{'id_products_exchange'})."</span>";
	}
}

sub product_payments{
# --------------------------------------------------------
# Forms Involved: \cgi-bin\inbound , administration
# Created on: 26/may/2008 11:48AM GMT -0600
# Last Modified on: 7/18/2008 11:07:01 AM
# Last Modified by: Carlos Haas
# Author: L.I. Roberto Barcenas Adame
# Description : Show the payment options for a product
# Parameters : idproduct,flexipays,type[30 days, 15 days],$sprice, $downpaymemt 

	my ($idproduct,$nflexipay,$type,$sprice,$downpayment) = @_;
	my (@payments,$rec,$discountpc,$sumpayments);
	
	$discountpc = $cfg{'fpdiscount'.$nflexipay};
	($discountpc eq '') and ($discountpc = 0);
	$sumpayments=0;
	if ($idproduct =~ /$cfg{'disc40'}/ and $type == 1){
		$payments[0] = $sprice - ($sprice * 40  / 100);
	}elsif ($idproduct =~ /$cfg{'disc30'}/ and $type == 1){
		$payments[0] = $sprice - ($sprice * 30  / 100);
	}elsif ($type == 1){
  		#### One Payment
		$payments[0] = $sprice - ($sprice * $discountpc  / 100);
	}elsif($type eq '7y'){
		$nflexipay = $nflexipay*4+int($nflexipay/3);
		$in{'weeklypago'} = $nflexipay;
		if($downpayment > 0){
	  		### With Downpayment
	  		for my $i(1..$nflexipay){
	  			$payments[$i] = ($sprice - $downpayment) / $nflexipay;
	  			$sumpayments += ($sprice - $downpayment) / $nflexipay;
	  		}
	  		$payments[0] = $sprice - $sumpayments;
		}else{
			### Without Downpayment
			for my $i(0..$nflexipay - 1){
				$payments[$i] = $sprice / $nflexipay;
			}
		}		
	}elsif($type == 7){
		if($downpayment > 0){
	  		### With Downpayment
	  		for my $i(1..$nflexipay){
	  			$payments[$i] = ($sprice - $downpayment) / $nflexipay;
	  			$sumpayments += ($sprice - $downpayment) / $nflexipay;
	  		}
	  		$payments[0] = $sprice - $sumpayments;
		}else{
			### Without Downpayment
			for my $i(1..$nflexipay){
				$payments[$i] = $sprice / $nflexipay;
			}
		}
		#$payments[0] = $sprice * .07;	
	}elsif($type == 15){
		##### BeWeekly Payments
		if($downpayment > 0){
	  		### With Downpayment
	  		for my $i(1..$nflexipay){
	  			$payments[$i] = ($sprice - $downpayment) / $nflexipay;
	  			$sumpayments += ($sprice - $downpayment) / $nflexipay;
	  		}
	  		$payments[0] = ($sprice - $sumpayments)+ ($sprice*.07);	
		}else{
	  		### Without Downpayment
	  		for my $i(1..$nflexipay){
	  			$payments[$i] = $sprice / $nflexipay;
	  		}
	  		#$payments[0] = $sprice * .07;	
	  	}
	}elsif($type == 30){
		##### Monthly Payments
		if($downpayment > 0){
	  		### With Downpayment
	  		for my $i(1..$nflexipay){
	  			$payments[$i] = ($sprice - $downpayment) / $nflexipay;
	  			$sumpayments += ($sprice - $downpayment) / $nflexipay;
	  		}
	  		$payments[0] = $sprice - $sumpayments;
		}else{
	  		### Without Downpayment
	  		for my $i(0..$nflexipay - 1){
	  			$payments[$i] = $sprice / $nflexipay;
	  		}
		}
	}
	return @payments;
}



sub product_payments_view{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 26/may/2008 11:48AM GMT -0600
# Last Modified on: 7/10/2008 11:23:19 AM
# Last Modified by:CH
# Author: L.I. Roberto Barcenas Adame
# Description : Show the payment options for a product
# Parameters : idproduct,flexipays,type[30 days, 15 days] 
# Last Modified on: 10/23/08 16:31:55
# Last Modified by: MCC C. Gabriel Varela S: Se valida que Rebate sea ,mayor que cero, en lugar de que exista solamente
# Last Modified on: 10/28/08 16:49:15
# Last Modified by: MCC C. Gabriel Varela S,L.I. Roberto Barcenas Adame: Se agregan mensajes para lay-away.
# Last Modified on: 10/30/08 10:29:18
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales. Se corrige formato de etiquetas span. Tambi?n se habilita tipo de pago weekly 2 en caso de que haya law-away. Se deja s?lo opci?n basada en 52 semanas
# Last Modified on: 11/06/08 13:25:17
# Last Modified by: MCC C. Gabriel Varela S: Se muestra el pago de membres?a.

	my (@onepay,@weekly,@weekly2,@biweek,@monthly,$datatable);
	my $sth=&Do_SQL("SELECT * FROM `sl_products` WHERE ID_products = $in{'id_products'}");
	$rec = $sth->fetchrow_hashref();
	
	@onepay  = &product_payments($in{'id_products'},$in{'flexipago'},1,$rec->{'SPrice'},$rec->{'Downpayment'});
	
	if ($rec->{'Rebate'}>0){
		$onepay[0] = $rec->{'SPrice'};
		$datatable = " <b>One Payment:</b><br> 1 payment of &nbsp; ".&format_price($rec->{'SPrice'}-$rec->{'Rebate'})." (After ".&format_price($rec->{'Rebate'})." Mail in Rebate )<br>";
	}elsif($rec->{'FPPrice'}>0){
		$onepay[0] = $rec->{'SPrice'};
		$datatable = " <b>One Payment:</b><br> 1 payment of &nbsp; ".&format_price($rec->{'SPrice'})." (Discount Included )<br>";
	}elsif	($in{'id_products'} =~ /$cfg{'disc40'}/){
		$datatable = " <b>One Payment:</b><br> 1 payment of &nbsp; ".&format_price($onepay[0])." (40 %  Discount Included )<br>";
	}elsif ($in{'id_products'} =~ /$cfg{'disc30'}/){
		$datatable = " <b>One Payment:</b><br> 1 payment of &nbsp; ".&format_price($onepay[0])." (30 %  Discount Included )<br>";
	}else{
		$datatable = " <b>One Payment:</b><br> 1 payment of &nbsp; ".&format_price($onepay[0])." (". &format_number($cfg{'fpdiscount'.$in{'flexipago'}})." %  Discount Included )<br>";
	}
	
	####################################################
	#####One payment with Membership####################
	if ($cfg{'membership'}==1 and $rec->{'MemberPrice'}!=0){
		my $pricetoshow;
		$pricetoshow=$rec->{'SPrice'};
		$pricetoshow=$rec->{'MemberPrice'} if($rec->{'MemberPrice'}>0);
		$datatable .= " <b>One Payment with Membership:</b><br> 1 payment of &nbsp; ".&format_price($pricetoshow)." (". &format_number(($rec->{'SPrice'}-$pricetoshow)/$rec->{'SPrice'}*100)." %  Discount)<br>";
	}
	####################################################
	####################################################
	
	if ($cfg{'fp3promo'}){
		$datatable .= " <b>3 Payments (Promotions):</b><br> 3 payment of &nbsp; ".&format_price($onepay[0]/3)." (0-15-30 Days)<br>";
	}
	#&cgierr("Flexipagos: ".$in{'flexipago'}.",".$rec->{'FPPrice'}.",".$rec->{'PayType'});
	if ($in{'flexipago'}>1){
		if ($rec->{'FPPrice'}>0){
			@biweek  = &product_payments($in{'id_products'},$in{'flexipago'}*2,15,$rec->{'FPPrice'},$rec->{'Downpayment'});
			@weekly  = &product_payments($in{'id_products'},$in{'flexipago'}*4,7,$rec->{'FPPrice'},$rec->{'Downpayment'});
			@weekly2  = &product_payments($in{'id_products'},$in{'flexipago'},'7y',$rec->{'FPPrice'},$rec->{'Downpayment'});
			@monthly = &product_payments($in{'id_products'},$in{'flexipago'},30,$rec->{'FPPrice'},$rec->{'Downpayment'});
		}else{
			@biweek  = &product_payments($in{'id_products'},$in{'flexipago'}*2,15,$rec->{'SPrice'},$rec->{'Downpayment'});
			@weekly  = &product_payments($in{'id_products'},$in{'flexipago'}*4,7,$rec->{'SPrice'},$rec->{'Downpayment'});
			@weekly2  = &product_payments($in{'id_products'},$in{'flexipago'},'7y',$rec->{'SPrice'},$rec->{'Downpayment'});
			@monthly = &product_payments($in{'id_products'},$in{'flexipago'},30,$rec->{'SPrice'},$rec->{'Downpayment'});
		}
		my $cadlay="";
		$cadlay="Lay away" if($rec->{'PayType'}=~/Layaway/);
		if($rec->{'Downpayment'} > 0){
			#$datatable .= qq|<b>$cadlay Weekly <span class='help_on'>(Based on 4 weeks per Month)</span></a>:</b><br>1 payment of |.&format_price($weekly[0]).qq|  and |.($in{'flexipago'}*4).qq| payments of |.&format_price($weekly[1]).qq|<br>\n| if ($cfg{'fpweekly'} or $rec->{'PayType'}=~/Layaway/);
			$datatable .= qq|<b>$cadlay Weekly <span class='help_on'>(Based on 52 weeks per Year)</span></a>:</b><br>  $in{'weeklypago'} payments  of |.&format_price($weekly2[1]).qq|<br>\n| if ($cfg{'f2pweekly'} or $rec->{'PayType'}=~/Layaway/);
			$datatable .= qq|<b>$cadlay BiWeekly:</b><br>1 payment of |.&format_price($biweek[0]).qq|  and |.($in{'flexipago'}*2).qq| payments of |.&format_price($biweek[1]).qq|<br>\n| if ($cfg{'fpbiweekly'} or $rec->{'PayType'}=~/Layaway/);
			$datatable .= qq|<b>Monthly:</b><br> 1 payment of |.&format_price($monthly[0]).qq| and $in{'flexipago'} payments of |.&format_price($monthly[1]).qq|<br>\n| unless (!$cfg{'fpmonthly'}  or $rec->{'PayType'}!~/Credit-Card-30/);
		}else{
			#$datatable .= qq|<b>$cadlay Weekly <span class='help_on'>(Based on 4 weeks per Month)</span></a>:</b><br>|.($in{'flexipago'} * 4).qq| payments  of |.&format_price($weekly[1]).qq|<br>\n| if ($cfg{'fpweekly'} or $rec->{'PayType'}=~/Layaway/);
			$datatable .= qq|<b>$cadlay Weekly <span class='help_on'>(Based on 52 weeks per Year)</span></a>:</b><br>  $in{'weeklypago'} payments  of |.&format_price($weekly2[1]).qq|<br>\n| if ($cfg{'f2pweekly'} or $rec->{'PayType'}=~/Layaway/);
			$datatable .= qq|<b>$cadlay BiWeekly:</b><br> |.($in{'flexipago'} * 2).qq| payments  of |.&format_price($biweek[1]).qq|<br>\n| if ($cfg{'fpbiweekly'} or $rec->{'PayType'}=~/Layaway/);
			($cfg{'fpmonthly'} and $rec->{'PayType'}=~/Credit-Card/i) and
				($datatable .= qq|<b>Monthly:</b><br> $in{'flexipago'} payment(s) of |.&format_price($monthly[0]).qq|<br>\n|);
		}
	}

	return $datatable;
}


sub build_pretab_list{
#-----------------------------------------
# Created on: 11/18/08  17:32:27 By  Roberto Barcenas
# Forms Involved: any_tab.cgi
# Description : Builds any standard tab list
# Parameters : table, row to compare, value to compare, order row, rows to print

	my ($ttable,$trow,$rvalue,$rorder,@data) =	@_;
	my ($cmd);

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $ttable WHERE $trow ='$rvalue'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM $ttable WHERE $trow	=	'$rvalue' ORDER BY $rorder DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM $ttable WHERE $trow =	'$rvalue' ORDER BY $rorder DESC LIMIT $first,$usr{'pref_maxh'};");
		}
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			$st = $data[$#data][3];

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			for (0..$#data-1){
				if($data[$_] =~	/ID_(.+)/){
					$cmd = $1;		
					$cmd = &load_prefixtab($cmd) if $script_url =~	/admin/;	
					$va{'searchresults'} .= "   <td class='smalltext'><a href=\"$script_url?cmd=$cmd&view=$rec->{''.$data[$_].''}\">$rec->{''.$data[$_].''}</a></td>\n";
				}else{
					$va{'searchresults'} .= "   <td class='smalltext'>$rec->{''.$data[$_].''}</td>\n";
				}
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
}

sub load_prefixtab{
#-----------------------------------------
# Created on: 11/18/08  17:29:30 By  Roberto Barcenas
# Forms Involved: any_tabs.cgi
# Description : Return the prefix for a command to build the link in the build_pretab_list function
# Parameters : When a column starts with ID_ , the next part of it is received as $cmd
		
	my ($cmd) = @_;
	
	if($sys{'db_'.$cmd.''}){
		return $cmd;
	}
	elsif($sys{'db_opr_'.$cmd.''}){
		return "opr_$cmd";
	}elsif($sys{'db_mer_'.$cmd.''}){
		return "mer_$cmd";
	}elsif($sys{'db_fin_'.$cmd.''}){
		return "fin_$cmd";
	}elsif($sys{'db_dev_'.$cmd.''}){
		return "dev_$cmd";
	}elsif($sys{'db_man_'.$cmd.''}){
		return "man_$cmd";
	}elsif($sys{'db_mkt_'.$cmd.''}){
		return "mkt_$cmd";
	}elsif($sys{'db_mm_'.$cmd.''}){
		return "mm_$cmd";
	}elsif($sys{'db_oso_'.$cmd.''}){
		return "oso_$cmd";
	}elsif($sys{'db_pla_'.$cmd.''}){
		return "pla_$cmd";
	}elsif($sys{'db_usr_'.$cmd.''}){
		return "usr_$cmd";
	}
}




sub check_callnote{
#-----------------------------------------
# Created on: 10/02/09  14:47:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Busca notas de llamadas para el reporte drop_calls (Supervisor)
# Parameters : 	
# Last Modified on: 10/19/09 17:25:52
# Last Modified by: MCC C. Gabriel Varela S: Se corrige error encontrado al no mandar Do_SQL con el par?metro adicional ext.
# Last Modified by RB on 2010/01/21: Se hace busqueda eliminando los signos "+"

	
	my ($id_cdr,$calldate) = @_;
	my $output='';
	
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM cdr_s7_notes WHERE src = REPLACE('$id_cdr','+','') AND calldate='$calldate';",1);
	my ($total) = $sth->fetchrow();
	&connect_db_w($cfg{'dbi_db'},$cfg{'dbi_host'},$cfg{'dbi_user'},$cfg{'dbi_pw'});
	

	if($total > 0){
		$output .= qq|<a href="javascript:return false;" onClick="popup_show('viewcn_|.$id_cdr.qq|', 'ajax_vdrag_|.$id_cdr.qq|', 'ajax_vexit_|.$id_cdr.qq|', 'element-right', -1, -1,'showcn_|.$id_cdr.qq|');">
								<img src="|.$va{'imgurl'}.qq|default/Bloc%20Note.png" width="20px" height="20px" title="Revisar Notas"></a>|	if	!$in{'print'};
	}else{
		$output .="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
	}
		
	$output .= qq|<a href="javascript:return false;" onClick="popup_show('postcn_|.$id_cdr.qq|', 'ajax_pdrag_|.$id_cdr.qq|', 'ajax_pexit_|.$id_cdr.qq|', 'element-right', -1, -1,'showcn_|.$id_cdr.qq|');">
								<img src="|.$va{'imgurl'}.qq|default/lists.png" width="20px" height="20px" title="Ingresar Nota"></a>|	if	!$in{'print'};
	return $output;
}



sub promocode_generate {
# --------------------------------------------------------
    my ($p1,$p2,$p3,$c);
    my ($starpoint) = @_;

    if($starpoint ne '0'){
	    srand($starpoint);
    }else{
	    srand( time ^ $$ ^ unpack "%L*", `ps axww | gzip -f` );
    }
        
    $va{'old_coupon'} = $va{'coupon_value'};
    $c = (int(rand(1000000000)) + 1) .  (int(rand(1000000000)) + 1).  (int(rand(1000000000)) + 1);
    $p1 = substr($c,0,5); 
    $p2 = substr($c,7,5); 
    $p3 = substr($c,8,3); 
    return (promocode_dv($p1). $p1. promocode_dv($p1.$p2). $p2. promocode_dv($p2) . $p3);
}

sub promocode_validate {
# --------------------------------------------------------
    my ($c) = @_;
    my ($p1,$p2,$p3);
    $p1 = substr($c,1,5);
    $p2 = substr($c,7,5);
    $p3 = substr($c,13,3);
    $dv1 = substr($c,0,1);
    $dv2 = substr($c,12,1);
    $dv3 = substr($c,6,1);
    
    if ($dv1 eq promocode_dv($p1) and $dv2 eq promocode_dv($p2) and $dv3 eq promocode_dv($p1.$p2)){
        return "true";
    }else{
        return "false";
    }
}

sub promocode_dv {
# --------------------------------------------------------
    my ($input,$tot) = @_;
    my ($lg,$dv);
    $lg = length($input);
    for (0..$lg){
        $tot += ord(substr($input,$_,1)) + ord(substr($input,$_+1,1)) - 30 - $_;
    }
    $dv = int(($tot/11-int($tot/11))*11);
    ($dv==10) and ($dv='0');
    return $dv;
}


sub show_wait_dialog{
	
	return qq|	
	YAHOO.namespace("example.container");
	if (!YAHOO.example.container.wait) {

        // Initialize the temporary Panel to display while waiting for external content to load

        YAHOO.example.container.wait = 
                new YAHOO.widget.Panel("wait",  
                                                { width: "240px", 
                                                  fixedcenter: true, 
                                                  close: false, 
                                                  draggable: false, 
                                                  zindex:4,
                                                  modal: true,
                                                  visible: false
                                                } 
                                            );

        YAHOO.example.container.wait.setHeader("Loading, please wait...");
        YAHOO.example.container.wait.setBody("<img src='http://l.yimg.com/a/i/us/per/gr/gp/rel_interstitial_loading.gif'/>");
        YAHOO.example.container.wait.render(document.body);

    }|;
}


sub replace_in_string{
#-----------------------------------------
# Created on: 01/12/2012 By  Roberto Barcenas
# Forms Involved:
# Description: Reemplaza contenido de texto en cadena
# Parameters: $str_txt
# Last time Modified 

	my ($str_txt) = @_;
	$str_txt =~ s/\[.*?\]//g;
	return $str_txt;

}


sub agent_reward {
#-----------------------------------------
# Created on: 02/24/2012 By OS
# Forms Involved:
# Description: Devuelve el calculo de la comision para el agente
# Parameters: completed, agent, day_start, day_end
# Last Time Modified by RB on 03/05/2012: Se verifican calculos vs excel
# Last Time Modified by RB on 04/10/2012: Se agregan bonos por datos y descuentos

	my ($agent, $day_start, $day_end) = @_;
	my $sth, $str_sql;
	my $str_status;
	my $base_order=0;
	my $pot_base_order=0;
	my $base_sale=0;
	my $pot_base_sale=0;
	my $pct=0;
	my $qty_sales = 0;
	my $total_sales=0;
	my $pot_total_sales=0;
	my $ticket_prom=0;
	my $pot_ticket_prom=0;
	my $Conv_TDC=0;
	my $pot_Conv_TDC=0;
	my $orders_data=0;
	my $bonus_data_amt=0;
	my $discount_data_amt=0;
	my $pot_orders_data=0;
	my $pot_bonus_data_amt=0;
	my $pot_discount_data_amt=0;
	my $total_orders_bonus=0;

	my $str_orders='';
	my @ary_orders;


	$str_sql = "SELECT pbase_order, pbase_sale, fulldata_bonus, cs_discount FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active' ";
	$sth=&Do_SQL($str_sql);
	my ($pbase_order, $pbase_sale, $bonus_data, $discount_data) = $sth->fetchrow();

	## User Type Agent available for bonus?
	if($pbase_order or $pbase_sale){
			
			## Quantity Orders / Total Orders / Total orders TDC
			my $qty_orders=0;$total_orders=0;$total_orders_tdc=0;
			$str_sql = "SELECT Status,
					COUNT(*)AS Quantity,
					SUM(OrderNet)AS Amount,
					SUM(IF(Ptype='Credit-Card',OrderNet,0))AS TDC
					FROM sl_orders WHERE Date BETWEEN '$day_start' AND '$day_end'
					AND ID_admin_users = $agent GROUP BY Status;";
			$sth=&Do_SQL($str_sql);
			while(my($status,$qty,$amt,$tdc) = $sth->fetchrow()){
				$str_orders .= "$qty;$amt;$tdc|";
				push(@ary_orders, $status);

				#if($status !~ /Void|System/){
					$qty_orders += $qty;
					$total_orders += $amt;
					$total_orders_tdc += $tdc;
				#}

				$total_orders_bonus += $status !~ /Void|System/ ? $amt : 0;

			}
			chop($str_orders);

			## Quantity Sales / Total Sales
			$str_sql = "SELECT COUNT(OrderNet), SUM(OrderNet) FROM sl_orders WHERE PostedDate BETWEEN '$day_start' AND '$day_end' AND ID_admin_users = $agent; ";
			$sth=&Do_SQL($str_sql);
			($qty_sales, $total_sales) = $sth->fetchrow_array();

			## Potential Quantity Sales	/ Total Sales / Total  Sales TDC
			$str_sql = "SELECT COUNT(OrderNet), SUM(OrderNet), SUM(IF(Ptype='Credit-Card',OrderNet,0)) FROM sl_orders WHERE ID_admin_users = $agent AND Status IN ('New', 'Processed', 'Pending'); ";
			$sth=&Do_SQL($str_sql);
			my ($pot_qty_sales, $pot_total_sales, $pot_sales_tdc) = $sth->fetchrow_array();


			## Data Bonus / Data Discount
			$str_sql = "SELECT
						COUNT(*)AS Total_Orders_Qty,
						/*GROUP_CONCAT(ID_orders)AS ID_orders*/
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND (LENGTH(Phone2) >= 10 OR LENGTH(Cellphone) >= 10) AND Email LIKE '%@%',1,0))AS Total_Data_Qty,
						SUM(DataDiscount)AS Total_Discount_Qty,
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND (LENGTH(Phone2) >= 10 OR LENGTH(Cellphone) >= 10) AND Email LIKE '%@%' ,$bonus_data,0))AS Bonus_Data,
						SUM(IF(DataDiscount > 0,$discount_data,0))AS Discount_Data FROM
					(
						SELECT ID_customers,ID_orders,SUM(IF(Type = 'C.E.L C/ERROR',1,0))AS DataDiscount
						FROM
						(
							SELECT ID_customers,ID_orders FROM sl_orders
							WHERE Date BETWEEN '$day_start' AND '$day_end'
							AND ID_admin_users = '$agent'
							AND Status NOT IN('Void','System Error')
						)tmp2
						INNER JOIN sl_orders_notes
						USING(ID_orders)
						GROUP BY tmp2.ID_orders
					)tmp
					INNER JOIN sl_customers USING(ID_customers);";

			$sth=&Do_SQL($str_sql);
			($orders_data, $bonus_data_qty, $discount_data_qty, $bonus_data_amt, $discount_data_amt) = $sth->fetchrow();


			## Potential Data Bonus / Data Discount
			$str_sql = "SELECT
						COUNT(*)AS Total_ORders,
						SUM(IF(DataDiscount = 0 AND LENGTH(Phone1) >= 10 AND LENGTH(Phone2) >= 10 AND Email LIKE '%@%' ,$bonus_data,0))AS Bonus_Data,
						SUM(IF(DataDiscount > 0,$discount_data,0))AS Discount_Data FROM
					(
						SELECT ID_customers,ID_orders,SUM(IF(Type = 'C.E.L C/ERROR',1,0))AS DataDiscount
						FROM
						(
							SELECT ID_customers,ID_orders FROM sl_orders
							WHERE ID_admin_users = '$agent'
							AND Status NOT IN('Void','System Error')
						)tmp2
						INNER JOIN sl_orders_notes
						USING(ID_orders)
						GROUP BY tmp2.ID_orders
					)tmp
					INNER JOIN sl_customers USING(ID_customers);";

			$sth=&Do_SQL($str_sql);
			($pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt) = $sth->fetchrow();

			
			## Sales OR Orders
			if ($qty_orders or $qty_sales){

					## Ticket Prom
					if ($qty_sales) {
						$ticket_prom = $total_sales / $qty_sales;
					}

					## Potential Ticket Prom
					if ($pot_qty_sales > 0) {
						$pot_ticket_prom = $pot_total_sales / $pot_qty_sales;
					}

					## TDC Conversion
					if ($total_orders_tdc > 0) {
						$Conv_TDC = $total_orders_tdc / $total_orders;
					}
					(!$Conv_TDC) and ($Conv_TDC=0);


					## Potential TDC Conversion
					if ($pot_total_sales > 0) {
						$pot_Conv_TDC = $pot_sales_tdc / $pot_total_sales; 
					}
					(!$pot_Conv_TDC) and ($pot_Conv_TDC=0);
					
					## Order Bonus
					if ($pbase_order) {
						$base_order = $total_orders_bonus * $pbase_order / 100;
					}
					(!$base_order) and ($base_order=0);
					
					$str_sql = "SELECT
					IF($Conv_TDC*100>tdc_55,tdc_c55*100/100,
					IF($Conv_TDC*100>tdc_45,IF(($Conv_TDC*100-tdc_45-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_45-2)/3)) / POW(2,(1 +(tdc_55-tdc_45-2)/3))) * (tdc_c55-tdc_c45)+tdc_c45,tdc_c45*100/100),
					IF($Conv_TDC*100>tdc_35,IF(($Conv_TDC*100-tdc_35-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_35-2)/3)) / POW(2,(1 +(tdc_45-tdc_35-2)/3))) * (tdc_c45-tdc_c35)+tdc_c35,tdc_c35*100/100),
					IF($Conv_TDC*100>tdc_25,IF(($Conv_TDC*100-tdc_25-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_25-2)/3)) / POW(2,(1 +(tdc_35-tdc_25-2)/3))) * (tdc_c35-tdc_c25)+tdc_c25,tdc_c25*100/100),
					IF($Conv_TDC*100>tdc_10,IF(($Conv_TDC*100-tdc_10-2)>0,( POW(2,(1 +($Conv_TDC*100-tdc_10-2)/3)) / POW(2,(1 +(tdc_25-tdc_10-2)/3))) * (tdc_c25-tdc_c10)+tdc_c10,tdc_c10*100/100), 0
					)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
					
					$sth=&Do_SQL($str_sql);
					$bono_tdc = eval($sth->fetchrow());
					(!$bono_tdc) and ($bono_tdc=0);

					## Potential TDC Bonus
					$str_sql = "SELECT 
							IF($pot_Conv_TDC*100>tdc_55,tdc_c55*100/100,
							IF($pot_Conv_TDC*100>tdc_45,IF(($pot_Conv_TDC*100-tdc_45-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_45-2)/3)) / POW(2,(1 +(tdc_55-tdc_45-2)/3))) * (tdc_c55-tdc_c45)+tdc_c45,tdc_c45*100/100),
							IF($pot_Conv_TDC*100>tdc_35,IF(($pot_Conv_TDC*100-tdc_35-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_35-2)/3)) / POW(2,(1 +(tdc_45-tdc_35-2)/3))) * (tdc_c45-tdc_c35)+tdc_c35,tdc_c35*100/100),
							IF($pot_Conv_TDC*100>tdc_25,IF(($pot_Conv_TDC*100-tdc_25-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_25-2)/3)) / POW(2,(1 +(tdc_35-tdc_25-2)/3))) * (tdc_c35-tdc_c25)+tdc_c25,tdc_c25*100/100),
							IF($pot_Conv_TDC*100>tdc_10,IF(($pot_Conv_TDC*100-tdc_10-2)>0,( POW(2,(1 +($pot_Conv_TDC*100-tdc_10-2)/3)) / POW(2,(1 +(tdc_25-tdc_10-2)/3))) * (tdc_c25-tdc_c10)+tdc_c10,tdc_c10*100/100), 0
							)))))
					FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
					
					$sth=&Do_SQL($str_sql);
					$pot_bono_tdc = eval($sth->fetchrow());
					(!$pot_bono_tdc) and ($pot_bono_tdc=0);

					$bono_ticket = 9.6; # Se afecta y se pone manual por peticion de Crystian Mendoza
					$pot_bono_ticket = 9.6; # Se afecta y se pone manual por peticion de Crystian Mendoza

					if(!$bono_ticket){
					
						## Ticket Bonus
						$str_sql = "SELECT IF($ticket_prom>ticket_200,ticket_c200*100/100,
						  IF($ticket_prom>ticket_170,IF(($ticket_prom-ticket_170-2)>0,( POW(2,(1 +($ticket_prom-ticket_170-2)/3)) / POW(2,(1 +(ticket_200-ticket_170-2)/3))) * (ticket_c200-ticket_c170)+ticket_c170,ticket_c170*100/100),
						  IF($ticket_prom>ticket_160,IF(($ticket_prom-ticket_160-2)>0,( POW(2,(1 +($ticket_prom-ticket_160-2)/3)) / POW(2,(1 +(ticket_170-ticket_160-2)/3))) * (ticket_c170-ticket_c160)+ticket_c160,ticket_c160*100/100),
						  IF($ticket_prom>ticket_150,IF(($ticket_prom-ticket_150-2)>0,( POW(2,(1 +($ticket_prom-ticket_150-2)/3)) / POW(2,(1 +(ticket_160-ticket_150-2)/3))) * (ticket_c160-ticket_c150)+ticket_c150,ticket_c150*100/100),
						  IF($ticket_prom>ticket_140,IF(($ticket_prom-ticket_140-2)>0,( POW(2,(1 +($ticket_prom-ticket_140-2)/3)) / POW(2,(1 +(ticket_150-ticket_140-2)/3))) * (ticket_c150-ticket_c140)+ticket_c140,ticket_c140*100/100), 0
						)))))
						FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
						$sth=&Do_SQL($str_sql);
						$bono_ticket = eval($sth->fetchrow());
						(!$bono_ticket) and ($bono_ticket=0);

						## Potential Ticket Bonus
						$str_sql = "SELECT IF($pot_ticket_prom>ticket_200,ticket_c200*100/100,
						  IF($pot_ticket_prom>ticket_170,IF(($pot_ticket_prom-ticket_170-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_170-2)/3)) / POW(2,(1 +(ticket_200-ticket_170-2)/3))) * (ticket_c200-ticket_c170)+ticket_c170,ticket_c170*100/100),
						  IF($pot_ticket_prom>ticket_160,IF(($pot_ticket_prom-ticket_160-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_160-2)/3)) / POW(2,(1 +(ticket_170-ticket_160-2)/3))) * (ticket_c170-ticket_c160)+ticket_c160,ticket_c160*100/100),
						  IF($pot_ticket_prom>ticket_150,IF(($pot_ticket_prom-ticket_150-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_150-2)/3)) / POW(2,(1 +(ticket_160-ticket_150-2)/3))) * (ticket_c160-ticket_c150)+ticket_c150,ticket_c150*100/100),
						  IF($pot_ticket_prom>ticket_140,IF(($pot_ticket_prom-ticket_140-2)>0,( POW(2,(1 +($pot_ticket_prom-ticket_140-2)/3)) / POW(2,(1 +(ticket_150-ticket_140-2)/3))) * (ticket_c150-ticket_c140)+ticket_c140,ticket_c140*100/100), 0
						)))))
						FROM sl_rewards WHERE user_type='$usr{'user_type'}' AND Status='Active'; ";
						$sth=&Do_SQL($str_sql);
						$pot_bono_ticket = eval($sth->fetchrow());
						(!$pot_bono_ticket) and ($pot_bono_ticket=0);

					}

					## Sale completed Bonus
					$base_sale  = round($pbase_sale + $bono_ticket + $bono_tdc,2) * $total_sales / 100;
					$pct = $base_sale * 100 / $total_sales if $base_sale > 0;
					#print "Agente:$agent<br>Ventas: $qty_sales<br>Venta Total:$total_sales<br>Ticket Promedio: $ticket_prom<br>Conversion TDC:$Conv_TDC<br>";
					#print "Comision Venta(%): ". $base_sale * 100 / $total_sales ."<br>";
					#print "ComisionVenta($base_sale)  = (Bonofijo($pbase_sale) + BonoTicket($bono_ticket) + BonoTDC($bono_tdc)) * VentaTotal($total_sales) / 100<br>";
					
			}  # $qty_orders or $qty_sales
			$pot_base_sale  = round($pbase_sale + $pot_bono_ticket + $pot_bono_tdc,2) * $pot_total_sales / 100;
			#print "Potencial: $pot_base_sale  = int($pbase_sale + $pot_bono_ticket + $pot_bono_tdc) * $pot_total_sales / 100;<br>";
	}  # $pbase_order or $pbase_sale
	#print "base_order = $base_order, base_sale = $base_sale, pot_base_sale = $pot_base_sale, pbase_order = $pbase_order, pbase_sale = $pbase_sale, bono_ticket = $bono_ticket, pot_bono_ticket = $pot_bono_ticket, bono_tdc = $bono_tdc, pot_bono_tdc = $pot_bono_tdc, ticket_prom = $ticket_prom, pot_ticket_prom = $pot_ticket_prom, Conv_TDC = $Conv_TDC, pot_Conv_TDC = $pot_Conv_TDC<hr>";	#&cgierr(scalar @ary_orders);
	return ($total_orders_tdc, $base_order, $base_sale, $pot_base_sale, $pbase_order, $pbase_sale, $bonus_data, $discount_data, $bono_ticket, $pot_bono_ticket, $bono_tdc, $pot_bono_tdc, $ticket_prom, $pot_ticket_prom, $Conv_TDC, $pot_Conv_TDC, $orders_data, $bonus_data_qty, $bonus_data_amt, $discount_data_qty, $discount_data_amt, $pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt, $qty_sales, $total_sales, $str_orders, @ary_orders);

}  # End function


1;