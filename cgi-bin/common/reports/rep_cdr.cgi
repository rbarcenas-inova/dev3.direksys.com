#!/usr/bin/perl
sub rep_cdr_home {
# --------------------------------------------------------
# Last Modified by RB on 05/18/2011 11:12:06 AM : Se agrega vixicom
# Last Modified by RB on 09/29/2011 16:09:26 PM : Se renombran las llamadas perdidas como Drop-In_origin
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt
##TODO: Que los CDR vengan desde los sl_leads

	if ($in{'action'} and ($in{'dnis'} or $in{'dnis_i'})){
		my (%resp,@ary);
		
		if ($in{'from_date'}){
			$in{'from_date'} =~ s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_leads_calls.Date>='$in{'from_date'}'";
		}
		if ($in{'to_date'}){
			$in{'to_date'} =~ s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_leads_calls.Date<='$in{'to_date'}'";
		}
		if($in{'from_time'} or $in{'to_time'}){
			$in{'from_time'} 	= "00:00:00"	if !$in{'from_time'};
			$in{'to_time'} 		= "23:59:59"	if !$in{'to_time'};
			$query .= " AND sl_leads_calls.Time BETWEEN '$in{'from_time'}' AND '$in{'to_time'}'";
		}
		if ($in{'repeted'}){
			$query .= "GROUP BY ID_leads";
		}
		if ($in{'groupby'} eq 'cdr'){
			#print "Content-type: text/html\n\n";
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=reportcdr.csv\n\n";
			#print "DATE,TIME,CALLER ID,DESTINATION,DURATION,DNIS,US-DNIS,CHANNEL,NUMBER 800\n";
			print "DATE,TIME,CALLER ID,DESTINATION,DURATION,DNIS,US-DNIS,NUMBER 800\n";
		}else{
			print "Content-type: text/html\n\n";
		}
		if($in{'dnis'}ne ''){
			$in{'dnis'} =~ s/\n/,/g;
			$in{'dnis'} =~ s/'/,/g; #'
			$in{'dnis'} =~ s/,/','/g;
			$in{'dnis'} = "'".$in{'dnis'}."'";
		}elsif($in{'dnis_i'}ne ''){
			$in{'dnis_i'}=~s/\|/,/g;
			$in{'dnis'}=$in{'dnis_i'};
		}		
		
		my $modquery = &check_permissions('view_phone_info','','') ? "ID_leads " : "CONCAT(LEFT(ID_leads,3),'-XXX-XXXX') AS ID_leads ";
		my ($sth) = &Do_SQL("SELECT 
								sl_leads_calls.Date,
								sl_leads_calls.Time,
								$modquery,
								IF(IO = 'Out','ATC',Destination) AS Destination,
								Duration,
								didmx,
								DIDUS,
								
								num800
							FROM `sl_leads_calls` 
					       LEFT JOIN sl_mediadids ON sl_mediadids.didusa=sl_leads_calls.DIDUS
					       WHERE sl_leads_calls.DIDUS IN ($in{'dnis'}) $query;");
		#channel,					       

		# 0 - date
		# 1 - time
		# 2 - id_leads
		# 3 - destination
		# 4 - duration
		# 5 - didmx
		# 6 - didus
		# 7 - channel
		# 8 - num800

		# 0 DATE(calldate),
		# 1 TIME(calldate),
		# 2 src,
		# 3 lastdata,
		# 4 duration,
		# 5 accountcode,
		# 6 didmx,
		# 7 num800,
		# 8 dstchannel,
		# 9 uniqueid

		while (@ary = $sth->fetchrow_array()){
		
			if ($in{'groupby'} eq 'cdr'){
				print join(",",@ary)."\n" ;
			}else{
				if ($ary[3] eq 'ATC'){
					++$va{'calls_atc'};
				}else{
					#&cgierr($ary[8]);
					if ($ary[8] !~ /SIP/){
						++$va{'calls_flash'};
					}elsif($ary[4] <= 15){
						++$va{'calls_dur<15'};
					}elsif($ary[4] <= 60){
						++$va{'calls_dur<60'};
					}elsif ($ary[4] <= 180){
						++$va{'calls_dur<180'};
					}else{
						++$va{'calls_dur>180'};
					}
					++$resp{$ary[5]};
					$resp{$ary[5].'_800'} = $ary[7];
					$resp{$ary[5].'_mx'} = $ary[6];
					++$va{'calls_total'};
				}
			}
		}
		if ($in{'groupby'} eq 'calls' and $va{'calls_total'}>0){
			$va{'por_flash'} = int($va{'calls_flash'}/$va{'calls_total'}*10000)/100;
			$va{'calls_flash'}= &format_number($va{'calls_flash'});
			
			$va{'por_dur<15'} = int($va{'calls_dur<15'}/$va{'calls_total'}*10000)/100;
			$va{'calls_dur<15'}= &format_number($va{'calls_dur<15'});
			
			$va{'por_dur<60'} = int($va{'calls_dur<60'}/$va{'calls_total'}*10000)/100;
			$va{'calls_dur<60'}= &format_number($va{'calls_dur<60'});
			
			$va{'por_dur<180'} = int($va{'calls_dur<180'}/$va{'calls_total'}*10000)/100;
			$va{'calls_dur<180'}= &format_number($va{'calls_dur<180'});
			
			$va{'por_dur>180'} = int($va{'calls_dur>180'}/$va{'calls_total'}*10000)/100;
			$va{'calls_dur>180'}= &format_number($va{'calls_dur>180'});
			
			$va{'calls_total'}= &format_number($va{'calls_total'});
			
			foreach $key ( sort { $a <=> $b } keys %resp){
				($key =~ /_mx|_800/) and (next);
				$va{'dnis_list'} .= "$key/$resp{$key.'_mx'} (" . substr($resp{$key.'_800'},0,3)."-". substr($resp{$key.'_800'},3,3)."-". substr($resp{$key.'_800'},6,4) .") : $resp{$key} <br>";
			}
			print &build_page('rep_cdr_callsrep.html');
			#print "SELECT DATE(calldate),TIME(calldate),CONCAT(LEFT(src,3),'-XXX-XXXX'),lastdata,duration,accountcode,MXDnis,Number FROM `cdr` LEFT JOIN dnis ON USDnis=accountcode WHERE `accountcode` IN ($in{'dnis'}) AND dstchannel LIKE 'SIP%' $query";
		}elsif($in{'groupby'} eq 'calls'){
			$message= &trans_txt('search_nomatches');
			print &build_page('rep_cdr_home.html');
		}
		&auth_logging('report_view','');
		return;
		
	}elsif($in{'action'} and !$in{'dnis'} and !$in{'dnis_i'}){
		$va{'message'}='Please complete the DNIS row';
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_cdr_home.html');
}


sub rep_cdr_ord {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt
# Last Modified on: 12/11/09 15:30:59
# Last modified by: EP. : Se modificaron querys para tomar en cuenta la tabla sl_leads_calls
	my ($sb,$query);
	$va{'params'} = &get_query_string;

	if ($in{'action'}){
		my $params = '';
		my ($query_tot,$query_list);
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}

		my ($rows) = 0;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND Date>='$in{'from_date'}' ";
			$query_cdr .= " AND sl_leads_calls.Date>='$in{'from_date'}'";
		}
		
		#$in{'to_date'} = &get_sql_date();
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND Date<='$in{'to_date'}' ";
			$query_cdr .= "AND sl_leads_calls.Date<='$in{'to_date'}'";
		}	

		#$query =~	s/and//i;
		#$query_cdr =~	s/and//i;
		if($in{'groupby'} eq 'hour'){
			$query_list = "SELECT HOUR( Time ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR( Time ) ";
			$query_list_cdr .= "SELECT HOUR( sl_leads_calls.Time ) AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY HOUR(sl_leads_calls.Time)";			
			$report_name = &trans_txt(rep_cdr_ord_name_hour);
		}elsif($in{'groupby'} eq 'halfhour'){
			$query_list = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR(Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,group_order ";$query_list = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR(Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,group_order ";
			$query_list_cdr .= "SELECT IF( MINUTE(sl_leads_calls.Time) <=30, CONCAT( HOUR(sl_leads_calls.Time) , ':01 to ', HOUR(sl_leads_calls.Time) , ':30' ) , CONCAT( HOUR(sl_leads_calls.Time) , ':31 to ', HOUR(sl_leads_calls.Time) +1, ':00' ) ) AS group_cdr, COUNT(*) AS calls  FROM sl_leads_calls WHERE 1=1 $query GROUP BY HOUR(sl_leads_calls.Time) , MINUTE(sl_leads_calls.Time ) <=30, MINUTE(sl_leads_calls.Time) >30 ORDER BY HOUR(sl_leads_calls.Time) ,group_cdr ";
			$query_list_cdr .= "";
			$report_name = &trans_txt(rep_cdr_ord_name_30);
		}else{
			$query_list = "SELECT Date AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY Date ";
			$query_list_cdr .= "SELECT sl_leads_calls.Date AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY sl_leads_calls.Date ";
			$report_name = &trans_txt(rep_cdr_ord_name_day);
		}
		
		## build report table
		$tbl_info = $va{'report_tbl'};
		$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
							</tr>
						 <tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq|</td>  
						</tr>
						$tbl_info</table></center>\n|;		
		
		($va{'rep1'},$va{'rep2'},$va{'rep3'}) = ('on','off','off');

		$va{'col1'} = &trans_txt('reports_calls');
		$va{'col3'} = &trans_txt('reports_orders');
		$va{'col5'} = &trans_txt('reports_sales');
	
		$data  = " group_cdr, calls, IF(orders IS NULL,0,orders)AS orders,IF(amounts IS NULL,0,amounts)AS amounts ";
		$sth = &Do_SQL("SELECT $data FROM ($query_list_cdr)AS tmp_cdr LEFT JOIN ($query_list)AS tmp_order ON group_cdr = group_order $sb ");
		
		if($sth->rows() > 0){
			my (@c) = split(/,/,$cfg{'srcolors'});
			while(my($header_data,$calls,$orders,$amounts) = $sth->fetchrow()){
					$d = 1 - $d;
					$va{'searchresults'} .= qq|
						<tr bgcolor="$c[$d]">
							<td width="40%">$header_data</td>
							<td colspan="2" align="center">$calls</td>
							<td colspan="2" align="center">$orders</td>	
							<td colspan="2" align="right">|.&format_price($amounts).qq|</td>|;
					$total_calls 		+= $calls;
					$total_orders 	+= $orders;
					$total_amounts 	+= $amounts;
			}
			$va{'tot_amount'} = &format_price($total_amounts);
			$va{'tot_calls'} = $total_calls;
			$va{'tot_orders'} = $total_orders;
			$va{'calls_orders'} = &round($total_orders/$total_calls,2)*100;
			$va{'matches'} = $sth->rows();
			$va{'pageslist'} = 1;
		}else{
			$va{'tot_cant'} = 0;
			$va{'tot_amount'} = &format_price(0);
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|
						<tr>
							<td colspan="5" align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
		}

			$va{'totinfo'} .= qq|<tr>
									<td>Totals [va_col3]:</td>
									<td align="right">[va_tot_orders]</td>
									<td align="right">([va_calls_orders]%)</td>
								</tr>
								<tr>
									<td>|.&trans_txt('reports_total_amount').qq|:</td>
									<td align="right">[va_tot_amount]</td>
									<td align="right">(100 %)</td>
								</tr>|;
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_cdr_dbl_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_cdr_dbl.html');
		}
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_cdr_ord.html');
}



sub rep_cdr_cod {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt
# Last Modified on: 12/11/09 16:30:59
# Last modified by: EP. : Se modificaron querys para tomar en cuenta la tabla sl_leads_calls
	my ($sb,$query);
	$va{'params'} = &get_query_string;

	if ($in{'action'}){
		my ($query_tot,$query_list);
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}

		my ($rows) = 0;
		
		$query=" and Ptype!='Credit-Card' ";
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND Date>='$in{'from_date'}' ";
			$query_cdr .= " AND sl_leads_calls.Date>='$in{'from_date'}'";
		}
		
		#$in{'to_date'} = &get_sql_date();
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND Date<='$in{'to_date'}' ";
			$query_cdr .= "AND sl_leads_calls.Date<='$in{'to_date'}'";
		}	
		#$query =~	s/and//i;
		#$query_cdr =~	s/and//i;
			
		if($in{'groupby'} eq 'hour'){
			$usr{'pref_maxh'} = 30;
			$query_list = "SELECT HOUR( Time ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR( Time ) ";
			$query_list_cdr .= "SELECT HOUR( sl_leads_calls.Time ) AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY HOUR( sl_leads_calls.Time ) ";
			$report_name = &trans_txt(rep_cdr_ord_name_hour);			
		}elsif($in{'groupby'} eq 'halfhour'){
			$query_list = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR(Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,group_order ";
			$query_list_cdr .= "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(sl_leads_calls.Time) , ':01 to ', HOUR(sl_leads_calls.Time) , ':30' ) , CONCAT( HOUR(sl_leads_calls.Time) , ':31 to ', HOUR(sl_leads_calls.Time) +1, ':00' ) ) AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY HOUR(sl_leads_calls.Time) , MINUTE(sl_leads_calls.Time ) <=30, MINUTE(sl_leads_calls.Time) >30 ORDER BY HOUR(sl_leads_calls.Time) ,group_cdr ";
			$report_name = &trans_txt(rep_cdr_ord_name_30);
		}else{
			$usr{'pref_maxh'} = 30;
			$query_list = "SELECT Date AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS amounts FROM sl_orders WHERE 1=1 $query GROUP BY Date ";
			$query_list_cdr .= "SELECT sl_leads_calls.Date group_cdr, COUNT(*) AS calls FROM sl_leads_calls  WHERE 1=1 $query_cdr GROUP BY sl_leads_calls.Date ";
			$report_name = &trans_txt(rep_cdr_ord_name_day);
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		## build report table
    	$tbl_info = $va{'report_tbl'};
		$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq| : $report_name</td>  
							</tr>
						 <tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq|</td>  
					    	<td class="smalltext">|.&trans_txt('reports_ordernet').qq|</td>  
						</tr>
						$tbl_info</table></center>\n|;		
		
		($va{'rep1'},$va{'rep2'},$va{'rep3'}) = ('off','on','off');

		$va{'col1'} = &trans_txt('reports_calls');
		$va{'col3'} = &trans_txt('reports_orders');
		$va{'col5'} = &trans_txt('reports_sales');
	
		$data  = " group_cdr, calls, IF(orders IS NULL,0,orders)AS orders,IF(amounts IS NULL,0,amounts)AS amounts ";
		$sth = &Do_SQL("SELECT $data FROM ($query_list_cdr)AS tmp_cdr LEFT JOIN ($query_list)AS tmp_order ON group_cdr = group_order $sb ");
		
		if($sth->rows() > 0){
			my (@c) = split(/,/,$cfg{'srcolors'});
			while(my($header_data,$calls,$orders,$amounts) = $sth->fetchrow()){
					$d = 1 - $d;
					$va{'searchresults'} .= qq|
											<tr bgcolor="$c[$d]">
												<td width="40%">$header_data</td>
												<td colspan="2" align="center">$calls</td>
												<td colspan="2" align="center">$orders</td>	
												<td colspan="2" align="right">|.&format_price($amounts).qq|</td>|;
					$total_calls 		+= $calls;
					$total_orders 	+= $orders;
					$total_amounts 	+= $amounts;
			}
			$va{'tot_amount'} = &format_price($total_amounts);
			$va{'tot_calls'} = $total_calls;
			$va{'tot_orders'} = $total_orders;
			$va{'calls_orders'} = &round($total_orders/$total_calls,2)*100;
			$va{'matches'} = $sth->rows();
			$va{'pageslist'} = 1;
		}else{
			$va{'tot_cant'} = 0;
			$va{'tot_amount'} = &format_price(0);
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|
						<tr>
							<td colspan="5" align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
		}

		$va{'totinfo'} .= qq|<tr>
								<td>Totals [va_col3]:</td>
								<td align="right">[va_tot_orders]</td>
								<td align="right">([va_calls_orders]%)</td>
							</tr>
							<tr>
								<td>|.&trans_txt('reports_total_amount').qq|:</td>
								<td align="right">[va_tot_amount]</td>
								<td align="right">(100 %)</td>
							</tr>\n|;	
		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_cdr_dbl_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_cdr_dbl.html');
		}
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_cdr_cod.html');
}


sub rep_cdr_tot {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified on: 08/11/09 11:00:59
# Last modified by: EP. : Se agregaron textos a trans_txt
# Last Modified on: 12/11/09 16:30:59
# Last modified by: EP. : Se Modificaron las referencias a tablas cdr y preorders # Last Modified on: 12/11/09 11:00:59
# Last modified by: EP. : Se Modificaron las referencias a tablas cdr y preorders 
	my ($sb,$query);
	$va{'params'} = &get_query_string;

	if ($in{'action'}){
		my ($query_tot,$query_list);
				
		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}

		my ($rows) = 0;
		
		## Filter by Date
		if ($in{'from_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date').": </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND Date>='$in{'from_date'}' ";
			$query_cdr .= " AND sl_leads_calls.Date >='$in{'from_date'}'";
		}
		
		#$in{'to_date'} = &get_sql_date();
		if ($in{'to_date'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND Date<='$in{'to_date'}' ";
			$query_cdr .= "AND sl_leads_calls.Date <='$in{'to_date'}'";
		}
		#$query =~	s/and//i;
		#$query_cdr =~	s/and//i;
			
		if($in{'groupby'} eq 'hour'){
			$usr{'pref_maxh'} = 30;
			$query_list_cdr = "SELECT HOUR( sl_leads_calls.Time ) AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY HOUR( sl_leads_calls.Time ) ";
			$query_list_ord = "SELECT HOUR( Time ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS ord_amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR( Time ) ";
			$report_name = &trans_txt('rep_cdr_tot_report_name_hour');
		}elsif($in{'groupby'} eq 'halfhour'){
			$query_list_cdr = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(sl_leads_calls.Time) , ':01 to ', HOUR(sl_leads_calls.Time) , ':30' ) , CONCAT( HOUR(sl_leads_calls.Time) , ':31 to ', HOUR(sl_leads_calls.Time) +1, ':00' ) ) AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY HOUR(sl_leads_calls.Time) , MINUTE(sl_leads_calls.Time ) <=30, MINUTE(sl_leads_calls.Time) >30 ORDER BY HOUR(sl_leads_calls.Time) ,group_cdr ";
			$query_list_ord = "SELECT IF( MINUTE(Time ) <=30, CONCAT( HOUR(Time ) , ':01 to ', HOUR(Time ) , ':30' ) , CONCAT( HOUR(Time ) , ':31 to ', HOUR(Time ) +1, ':00' ) ) AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS ord_amounts FROM sl_orders WHERE 1=1 $query GROUP BY HOUR(Time ) , MINUTE(Time ) <=30, MINUTE(Time ) >30 ORDER BY HOUR(Time ) ,group_order ";
			$report_name = &trans_txt('rep_cdr_tot_report_name_30');
		}else{
			$usr{'pref_maxh'} = 30;
			$query_list_cdr = "SELECT sl_leads_calls.Date AS group_cdr, COUNT(*) AS calls FROM sl_leads_calls WHERE 1=1 $query_cdr GROUP BY sl_leads_calls.Date ";
			$query_list_ord = "SELECT Date AS group_order, COUNT( * ) AS orders, SUM(OrderNet) AS ord_amounts FROM sl_orders WHERE 1=1 $query GROUP BY Date ";
			$report_name = &trans_txt('rep_cdr_tot_report_name_day');
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		
		## build report table
    	$tbl_info = $va{'report_tbl'};
		$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
							<tr>
						   		 <td class="menu_bar_title" colspan="2">|.&trans_txt('report_name').qq|: $report_name</td>  
							</tr>
						 <tr>
					    	<td class="smalltext">|.&trans_txt('reports_units').qq|Report Units</td>  
					    	<td class="smalltext">|.&trans_txt('reports_callsnet').qq|</td>  
						</tr>
						$tbl_info</table></center>\n|;
						
		($va{'rep1'},$va{'rep2'},$va{'rep3'}) = ('off','off','on');

		$va{'col1'} = &trans_txt('reports_calls');
		$va{'col2'} = &trans_txt('reports_orders');
		$va{'col3'} = &trans_txt('reports_sales');
		$va{'col4'} = &trans_txt('reports_orders_cod');
		$va{'col5'} = &trans_txt('reports_sales');
	
		$data  = " group_cdr, calls, IF( orders IS NULL , 0, orders ) AS orders, IF( ord_amounts IS NULL , 0, ord_amounts ) AS ord_amounts, 0 AS preorders, 0 AS pre_amounts ";
		$sth = &Do_SQL("SELECT $data FROM ($query_list_cdr)AS tmp_cdr LEFT JOIN ($query_list_ord)AS tmp_order ON group_cdr = group_order $sb ");
		
		if($sth->rows() > 0){
			my (@c) = split(/,/,$cfg{'srcolors'});
			while(my($header_data,$calls,$orders,$ord_amounts,$preorders,$pre_amounts) = $sth->fetchrow()){
					$d = 1 - $d;
					$va{'searchresults'} .= qq|
									<tr bgcolor="$c[$d]">
										<td align="left">$header_data</td>
										<td align="center">$calls</td>
										<td align="center">$orders</td>	
										<td align="right">|.&format_price($ord_amounts).qq|
										<td align="right">$preorders</td>	
										<td align="right">|.&format_price($pre_amounts).qq|
										</td>|;
					$total_calls 		+= $calls;
					$total_orders 	+= $orders;
					$total_ord_amounts 	+= $ord_amounts;
					$total_preorders 	+= $preorders;
					$total_pre_amounts 	+= $pre_amounts;
					$total_amounts += $ord_amounts + $pre_amounts;  
			}
			$va{'tot_calls'} = $total_calls;
			$va{'tot_orders'} = $total_orders;
			$va{'tot_preorders'} = $total_preorders;
			$va{'calls_orders'} = &round($total_orders/$total_calls,2)*100;
			$va{'calls_preorders'} = &round($total_preorders/$total_calls,2)*100;
			$va{'tot_ord_amount'} = &format_price($total_ord_amounts);
			$va{'tot_pre_amount'} = &format_price($total_pre_amounts);
			$va{'am_orders'} = &round($total_ord_amounts/$total_amounts,2)*100;
			$va{'am_preorders'} = &round($total_pre_amounts/$total_amounts,2)*100;
			$va{'tot_amount'} = &format_price($total_amounts);
			$va{'matches'} = $sth->rows();
			$va{'pageslist'} = 1;
		}else{
			$va{'tot_cant'} = 0;
			$va{'tot_amount'} = &format_price(0);
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} .= qq|
						<tr>
							<td colspan="5" align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
		}

		$va{'totinfo'}	=qq|<tr>
								<td>Totals $va{'col2'}:</td>
								<td align="right">$va{'tot_orders'}</td>
								<td align="right">($va{'calls_orders'}%)</td>
							</tr>
							<tr>
								<td>Totals $va{'col4'}:</td>
								<td align="right">$va{'tot_preorders'}</td>
								<td align="right">($va{'calls_preorders'}%)</td>
							</tr>
							<tr><td colspan="2">&nbsp;</td></tr>
							<tr>
								<td>|.&trans_txt('reports_total_amount').qq| $va{'col2'}:</td>
								<td align="right">$va{'tot_ord_amount'}</td>
								<td align="right">($va{'am_orders'}%)</td>
							</tr>
							
							<tr>
								<td>|.&trans_txt('reports_total_amount').qq| $va{'col4'}:</td>
								<td align="right">$va{'tot_pre_amount'}</td>
								<td align="right">($va{'am_preorders'}%)</td>
							</tr>
							<tr>
								<td>|.&trans_txt('reports_total_amount').qq|:</td>
								<td align="right">[va_tot_amount]</td>
								<td align="right">(100 %)</td>
							</tr>\n|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_cdr_dbl_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_orders_dbl.html');
		}
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('rep_cdr_tot.html');
}

sub rep_cdr_didord {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 04/14/11 12:39:54 PM
# Author: MCC C. Gabriel Va rela S.
# Description :   
# Parameters :
# Last modified on 19 Apr 2011 13:36:04
# Last modified by: MCC C. Gabriel Varela S. :Se hace que se obtenga producto de mayor valor
# Se separa por ; y se ponen comillas para los campos.
# Last modified on 20 Apr 2011 13:28:19
# Last modified by: MCC C. Gabriel Varela S. :Se quita filter values a dnis
# Last Modified by RB on 05/18/2011 11:25:09 AM : Se agrega vixicom
# Last Modified by RB on 03/26/2012 04:57:09 PM : Se agrega S8
# Last Modified on: 12/11/09 11:00:59
# Last modified by: EP. : Se Modificaron las referencias a tablas cdr y preorders 

	my $err=0;	
	if($in{'action'}){
		#Comienzan validaciones
		if ($in{'from_date'}){
			$in{'from_date'} = &filter_values($in{'from_date'});
			$in{'from_date'} =~ s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('from_date')." : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_leads_calls.Date >='$in{'from_date'}'";
		}else{
			$error{'from_date'} = &trans_txt('required');
			++$err;
		}
		if ($in{'to_date'}){
			$in{'to_date'} = &filter_values($in{'to_date'});
			$in{'to_date'} =~ s/\//-/g;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('to_date')." : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_leads_calls.Date <='$in{'to_date'}'";
		}else{
			$error{'to_date'} = &trans_txt('required');
			++$err;
		}
		if($in{'dnis'}ne ''){
			#$in{'dnis'} = &filter_values($in{'dnis'});
			$in{'dnis'} =~ s/\n/,/g;
			$in{'dnis'} =~ s/'/,/g; #'
			#$in{'dnis'} =~ s/,/','/g;
			#$in{'dnis'} = "'".$in{'dnis'}."'";
		}elsif($in{'dnis_i'}ne ''){
			$in{'dnis_i'}=~s/\|/,/g;
			$in{'dnis'}=$in{'dnis_i'};
		}
		if(!$in{'dnis'} or $in{'dnis'}eq''){
			$error{'dnis'}=&trans_txt('required');
			++$err;
		}else{
			$dnis = "AND DIDUS IN ($in{'dnis'})";
		}
		
		my $all_calls;
		if ($in{'all_calls'}){
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_all_calls')." : </td><td class='smalltext'>".&trans_txt('reports_yes')."</td></tr>\n";
			$all_calls=' left ';
		}else{
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>".&trans_txt('reports_all_calls')." : </td><td class='smalltext'>".&trans_txt('reports_no')."</td></tr>\n";
			$all_calls=' inner ';
		}
		if($err>0){
			$va{'message'}= &trans_txt('reports_required') ;
		 }else{		
			my $sth=&Do_SQL("SELECT DISTINCT(sl_leads_calls.ID_leads), sl_leads_calls.Date AS date, sl_leads_calls.Time AS time,sl_leads_calls.*,orders_customers.*,payment_type.*
					FROM sl_leads_calls
					$all_calls JOIN (
						Select CID,Phone1,Phone2,Cellphone,orders.* 
						FROM sl_customers
						INNER JOIN (
							Select ID_orders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet
							FROM sl_orders
							WHERE STATUS NOT IN('Cancelled','Void','System Error')
							AND sl_orders.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
						) AS orders ON (orders.ID_customers=sl_customers.ID_customers)
							where sl_customers.Status='Active' 
					)as orders_customers 
						ON (	(right(sl_leads_calls.ID_leads,8)=right(Phone1 ,8)
							or right(sl_leads_calls.ID_leads,8)=right(Phone2 ,8)
							or right(sl_leads_calls.ID_leads,8)=right(Cellphone ,8)
							or right(sl_leads_calls.ID_leads,8)=right(CID,8))
							and(orders_customers.Dateo = sl_leads_calls.Date
							and sl_leads_calls.ID_leads !='')
						)
					LEFT JOIN (
							SELECT ID_orders,if(NCC>0,'CC',if(NMO>0,'MO',if(NCOD>0,'COD',if(NLay>0,'CC',if(NOther>0,'Other','')))))as PayType 
							FROM (
								SELECT sl_orders_payments.ID_orders, sum( if( TYPE = 'Credit-Card', 1, 0 ) ) AS NCC, sum( if( TYPE = 'Money Order', 1, 0 ) ) AS NMO, 
												 sum( if( TYPE = 'COD', 1, 0 ) ) AS NCOD,sum( if( TYPE = 'Layaway', 1, 0 ) ) AS NLay,
												sum( if( TYPE = '', 1, 0 ) ) AS NOther
								FROM sl_orders_payments
								INNER JOIN sl_orders ON ( sl_orders_payments.ID_orders = sl_orders.ID_orders ) 
								WHERE sl_orders_payments.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'
								AND sl_orders.Status NOT IN ('Cancelled', 'Void', 'System Error')
								GROUP BY sl_orders_payments.ID_orders
							) AS types
					) AS payment_type ON payment_type.ID_orders=orders_customers.ID_orders
					WHERE sl_leads_calls.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' 
					$dnis
					GROUP BY sl_leads_calls.ID_leads");
					
			@cols = ('DATE','TIME','DNIS','ID ORDER','ID CUSTOMER','CITY','STATE','ZIP','SHP STATE','NAME','ORDER NET','ORDER SHP','ORDER DISC','ORDER TAX','ORDER NET + ORDER SHP','PAY TYPE');
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=rep_cdr_leads_didord.csv\n\n";
			print '"'.join('","', @cols)."\"\n";					
					
			while($rec=$sth->fetchrow_hashref){
				#Obtiene el producto de la orden:
				my $sthp=&Do_SQL("SELECT Name,SalePrice
						FROM sl_orders_products
						INNER JOIN sl_products on right(sl_orders_products.ID_products,6)=sl_products.ID_products
						WHERE ID_orders='$rec->{'ID_orders'}'
						AND sl_orders_products.Status='Active'
						AND '$rec->{'ID_orders'}'!=''
						ORDER BY SalePrice DESC LIMIT 1");
				my $recp=$sthp->fetchrow_hashref;
				
				print "\"$rec->{'date'}\",\"$rec->{'time'}\",\"$rec->{'DIDUS'}\",\"$rec->{'ID_orders'}\",\"$rec->{'ID_customers'}\",\"$rec->{'City'}\",\"$rec->{'State'}\",\"$rec->{'Zip'}\",\"$rec->{'shp_State'}\",\"'$recp->{'Name'}'\",\"$rec->{'OrderNet'}\",\"$rec->{'OrderShp'}\",\"$rec->{'OrderDisc'}\",\"$rec->{'OrderTax'}\",\"".($rec->{'OrderNet'}+$rec->{'OrderShp'})."\",\"$rec->{'PayType'}\"\n";				
			}

			&auth_logging('report_view','');
			return;
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('rep_cdr_didord.html');
}

sub rep_cdr_leads_flash {
# --------------------------------------------------------
# Created :  Pablo Hdez.
# Last Update : 
# Locked by : 
# Description : Show leads flash for a specfic range of dates
# Last Modified : 

 	my $err=0;
 	
	## Checking Permission
	if ($in{'action'}){
 
		my $query="";
		## Filter by id
		if ($in{'id_leads_flash'}){
			$query .= " AND ID_leads_flash=".&filter_values(int($in{'id_leads_flash'}));
		}
		## Filter by Date
		if ($in{'from_date'}){
			$query .= " AND Date>='".&filter_values($in{'from_date'})."' ";
		}
		if ($in{'to_date'}){
			$query .= " AND Date<='".&filter_values($in{'to_date'})."' ";
		}
				
		#Filter leads
		if ($in{'id_leads'}){
			
			#validate phone
			$in{'id_leads'} = int($in{'id_leads'});		
			if ($in{'id_leads'} < 999999999){
				$error{'id_leads'} = &trans_txt('invalid');	
				$error{'message'} = &trans_txt('tendigitnum');
				++$err;
			}else{				
				$query .= " AND ID_leads='".&filter_values(int($in{'id_leads'}))."' ";
			}
		}
		#Filter name
		if ($in{'name'}){	
			$query .= " AND Name='".&filter_values($in{'name'})."' ";
		}

		#Filter products
		my $products;
		if ($in{'products'}){
			my @arp = split(/\|/,$in{'products'});
			for (0..$#arp){
				$products .= "'".&filter_values($arp[$_])."',";
			}
			chop($products);
			$query .= " AND products IN ($products) ";
		}

		#Filter time
		my $hours;
		if ($in{'contact_time'}){
			my @arh = split(/\|/,$in{'contact_time'});
			for (0..$#arh){
				$hours .= " Contact_time = '".&filter_values($arh[$_])."' OR ";
			}
			$hours = substr($hours,0,-3);
			$query .= " AND ( $hours ) ";
		}
		if ($in{'call_time'}){
			my @arh = split(/\|/,$in{'call_time'});
			for (0..$#arh){
				$hours .= " Call_time = '".&filter_values($arh[$_])."' OR ";
			}
			$hours = substr($hours,0,-3);
			$query .= " AND ( $hours ) ";
		}

		#Filter comments
		if ($in{'comments'}){
			$query .= " AND Comments LIKE '%".&filter_values($in{'comments'})."%' ";
		}
		
		#errors
		if ($err > 0){
			print "Content-type: text/html\n\n";
			print &build_page("rep_cdr_leads_flash.html");	
			exit;
		}
				 	 		
		$query_list   = "SELECT ID_leads_flash, ID_leads, Name, Contact_time, Call_time, Date, Status, Products  FROM sl_leads_flash WHERE 1=1  $query ";
		$query_tot    = "SELECT COUNT(*) as Count FROM sl_leads_flash WHERE 1=1 $query ";
	 		
		my ($sth) = &Do_SQL($query_tot);
		my ($tot_cant) = $sth->rows();
		
		if ($tot_cant>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			my ($sth) = &Do_SQL($query_list);
			$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'}){
				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}
			my (@c) = split(/,/,$cfg{'srcolors'});
			
			while ($rec = $sth->fetchrow_hashref){
			
				$d = 1 - $d;
				$rec->{'Contact_time'} =~  s/\|/&nbsp;-&nbsp;/g;
				
				#results
				$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td align="left">|.$rec->{'ID_leads_flash'}.qq|</td>
							<td  align="left" >|.$rec->{'ID_leads'}.qq|</td>
							<td align="left" nowrap>|.$rec->{'Name'}.qq|</td>
							<td align="left" nowrap>|.$rec->{'Contact_time'}.qq|</td>
							<td align="center" nowrap>|.$rec->{'Call_time'}.qq|</td>
							<td align="left" nowrap>|.$rec->{'Products'}.qq|</td>
							<td align="right" nowrap>|.$rec->{'Status'}.qq|</td>
							<td align="right" nowrap>|.$rec->{'Date'}.qq|</td>
						</tr>\n|;
						
					
			}
			foreach $key (keys %in){
            	$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
	        }
	        
	        #excel link
	        $va{'extabtns'} = qq|&nbsp;&nbsp;					  
					  <a href="$script_url?export=1&$qs')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export' alt='' border='0'></a>|;
	        
	        &auth_logging('report_view','');
	        if ($in{'print'}){
	        	#print
	            print "Content-type: text/html\n\n";
				print &build_page('header_print.html');
	            print &build_page('rep_cdr_leads_flash_print.html');
	        }elsif($in{'export'}){
	        	#excel
				@cols = ('ID Leads Flash','Phone','Name','Contact Hours','Call Time','Products','Status','Date');
				print "Content-type: application/vnd.ms-excel\n";
				print "Content-disposition: attachment; filename=rep_cdr_leads_flash.csv\n\n";
				print '"'.join('","', @cols)."\"\n";
				 $query_list   = "SELECT ID_leads_flash, ID_leads, Name, Contact_time, Call_time, Products, Status, Date FROM sl_leads_flash WHERE 1=1  $query ";
				my ($sth) = &Do_SQL($query_list);
				while (@ary = $sth->fetchrow_array){
					print '"'.join('","', @ary)."\"\n";
				}
				return;				
			}else{
				#results
	            print "Content-type: text/html\n\n";
	            print &build_page('results_cdr_leads_flash.html');
	            print $query_tot;
	        }
        	return;
		}
	}else{
		#form search
		print "Content-type: text/html\n\n";
		print &build_page('rep_cdr_leads_flash.html');
	}
}

#############################################################################
#############################################################################
#   Function: get_query_string
#
#       Es: Obtiene nu string con los valores recibidos en $ENV{'QUERY_STRING'}
#       En: 
#
#
#    Created on: 18/01/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on: 
#
#   Parameters:
#
#
#  Returns:
#
#      - params: Cadena con los valores recibidos en $ENV{'QUERY_STRING'}
#
#   See Also:
#
#
sub get_query_string {
#############################################################################
#############################################################################
	my $params='';

	if (length ($ENV{'QUERY_STRING'}) > 0){
		$buffer = $ENV{'QUERY_STRING'};
		@pairs = split(/&/, $buffer);

		foreach $pair (@pairs){
			($name, $value) = split(/=/, $pair);
			$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
			$params .= "&$name=$value" ;
		}
	}

	return $params;
}


1;