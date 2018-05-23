#!/usr/bin/perl
require ("admin.fin2.cgi");



sub fin_batch {
# --------------------------------------------------------
	my ($shpdate);
	if ($in{'action'}){
		if ($in{'shipdate'}){
			$shpdate = $in{'shipdate'};
			$shpdate =~ s/\//-/g;
			$in{'db'} = 'sl_orders';
			my ($sth) = &Do_SQL("SELECT DISTINCT(ID_orders) FROM sl_orders_notes WHERE Notes='The Status of the Order has been changed to Shipped on ".&filter_values($in{'shipdate'})."';");
			while ($id = $sth->fetchrow()){
				push(@ids,"$id");
			}
			if ($#ids==-1){
				$va{'message'} = &trans_txt('toprn_none');
			}
		}else{
			$va{'message'} = &trans_txt('toprn_none');
		}
	}

	if ($in{'action'} and $va{'message'}){
		print "Content-type: text/html\n\n";
		#print &build_page('opr_toprint2.html');
		print &build_page('opr_bulkorders_prn2.html');
	}elsif($in{'action'}){
		my ($page,%rec);
		&html_print_headers ('Printing.....');
		print qq|
	<body onload="prn()" style="background-color:#FFFFFF">
<!--
<object id=factory viewastext style="display:none"
classid="clsid:1663ed61-23eb-11d2-b92f-008048fdd814"
  codebase="/ScriptX.cab#Version=5,60,0,375">
</object>
-->
<script defer>
function prn() {
	window.print()
	return false;
}

</script>\n|;
		$in{'db'} = 'sl_orders';
		$in{'toprint'}=1;
		$cmd = 'batch';
		for my $i(0..$#ids){
			&load_cfg('sl_orders');
			if ($ids[$i]){
				$in{'id_orders'} = $ids[$i];
				$in{'toprint'}  = $ids[$i];
				my (%rec) = &get_record($db_cols[0],$ids[$i],$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
					$in{'shpdate'} = $shpdate;
					## User Info
					&get_db_extrainfo('admin_users',$in{'id_admin_users'});

					my ($func) = "view_$cmd";
					if (defined &$func){
						&$func;
					}
					print &build_page($cmd.'_print.html');
					#print &html_print_record(%rec);
				}
			}
			if ($ids[$i+1]>0){
				print "<DIV STYLE='page-break-before:always'></DIV>";
			}
		}
		print qq|</body>\n</html>\n|;

	}else{
		print "Content-type: text/html\n\n";
		print &build_page('fin_batch.html');		
	}	
}

###################################################################
######## REPORTS
###################################################################

sub fin_reporder_day {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_reporder_day.html');
}

sub fin_reporder_day_list {
# --------------------------------------------------------
	$in{'reportdate'}=substr($in{'reportdate'},1,11);
	if(!$in{'reportdate'}){
		my ($sth) = &Do_SQL("SELECT CURDATE() as date");
		$rec = $sth->fetchrow_hashref();
		$in{'reportdate'}=$rec->{'date'};
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Date = '$in{'reportdate'}' and Status='Shipped'");
	$cont_l=$sth->fetchrow;
	if ($cont_l>0){	
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		$va{'matches'} = $cont_l;			
		my($cont)=10;
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT * FROM sl_orders WHERE  Date = '$in{'reportdate'}' and  Status='Shipped' ORDER BY ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d; $cont++;		  
			$amount_price=$rec->{'OrderNet'}+$rec->{'OrderShp'}+$rec->{'OrderTax'};
			 my ($sth1) = &Do_SQL("SELECT MIN(ShpDate) FROM `sl_orders_products` WHERE  id_orders = '$rec->{'ID_orders'}'");
			$min_prod_ship=$sth1->fetchrow;		 
			my ($sth2) = &Do_SQL("SELECT Amount FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' and Paymentdate = '$in{'reportdate'}' and Status='Approved'");
			$first_pay=$sth2->fetchrow;
			if ($first_pay > 0) {
				$amount_dif=$amount_price - $first_pay;
			}else{
				$amount_dif=0;
			}
			my ($sth3) = &Do_SQL("SELECT Type,PmtField1 FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'  group by Type");		  
			$rec3=$sth3->fetchrow_hashref;
			if($rec3->{'Type'} eq 'Credit-Card'){
				$for_pay= $rec3->{'PmtField1'} ;
			}else{
				$for_pay=$rec3->{'Type'};
			}

			my ($sth4) = &Do_SQL("SELECT SUM(SLTV_NetCost) FROM sl_orders_products,sl_products WHERE sl_orders_products.ID_orders = '$rec->{'ID_orders'}' and  RIGHT(sl_orders_products.id_products,6) = sl_products.id_products");
			$sltv_cost=$sth4->fetchrow;
			my ($sth5) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'");
			$number_pay=$sth5->fetchrow;
			if($number_pay==1){
				$pay_type="Regular";
			}else{
				$pay_type="Flex. Pay";
			}
			$page.= qq|
				<tr  bgcolor='$c[$d]'>
					<td valign='top' nowrap>$min_prod_ship</td>										
					<td valign='top' nowrap>$rec->{'ID_orders'}</td>					  
					<td nowrap valign='top'>|.&format_price($rec->{'OrderNet'}) .qq| </td>					  							  
					<td nowrap valign='top'>|.&format_price($rec->{'OrderShp'}) .qq| </td>					  							  
					<td nowrap valign='top'>|.&format_price($rec->{'OrderTax'}) .qq| </td>					  							  							  
					<td nowrap valign='top'>|.&format_price($amount_price) .qq| </td>					  							  							  
					<td nowrap valign='top'>|.&format_price($first_pay) .qq| </td>					  							  
					<td nowrap valign='top'>|.&format_price($amount_dif) .qq| </td>					  							  							 
					<td nowrap valign='top'>|.&format_price($sltv_cost) .qq| </td>					  							  
					<td nowrap valign='top'>$pay_type </td>					  							  
					<td align="right" nowrap valign='top' >$number_pay</td>							  
					<td align="right" nowrap valign='top' >$for_pay</td>							  
				</tr>\n|;
		}
	}else{
		$page = "<tr><td colspan='3' align='center'>".&trans_txt('regist_report')."</td></tr>";
	}
	$va{'searchresults'}=$page;
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_reporder_day_list.html');
}

sub fin_reporder_detail {
# --------------------------------------------------------
#  use Math::FixedPrecision;
	if ($in{'action'}){
		my ($first_pay,$amount_price);
		##0'ORDER-PL',1'ITEM-ID',2'NAME',3'LASTNAME1',4'LASTNAME2',5'PHONE1',6'PHONE2',7'ZIP',8'URBANIZATION',9'CITY',10'STATE',11'ADDRESS'
		my (@xcols) = ('ID_orders','ID_orders_products','ID_productsS','Ship Date','SPrice','Sug. SPrice1','Sug. SPrice1','Sug. SPrice1','Sug. SPrice1','Order Net',
		'Ship&Hand','Tax %','Tax','Shp/# Items','P-DIF','P-SYS','TYPE-P','PAY-TYPE','PAY-DATE','PAY-AMOUNT','ID-CUST',
		'Firstname','Lastname1','Lastname2','Phone1','Phone2','Ship Zip','Ship Urb','Ship City','Ship State',
		'Ship Address');
		if ($in{'reportdatef'} and $in{'reportdatet'}){
			$query = " and ( ISNULL(sl_orders_products.ShpDate) OR sl_orders_products.ShpDate='' OR (sl_orders_products.ShpDate >= '$in{'reportdatef'}' and sl_orders_products.ShpDate <= '$in{'reportdatet'}') ) ";
		}elsif($in{'reportdatef'}){
			$query = " and ( ISNULL(sl_orders_products.ShpDate) OR sl_orders_products.ShpDate='' OR sl_orders_products.ShpDate >= '$in{'reportdatef'}' )";
		}elsif($in{'reportdatet'}){
			$query = " and ( ISNULL(sl_orders_products.ShpDate) OR sl_orders_products.ShpDate='' OR sl_orders_products.ShpDate <= '$in{'reportdatet'}' ) ";  	
		}elsif(!$in{'reportdatef'} and !$in{'reportdatet'}){
			$query = "";
		}
		$sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.id_orders = sl_orders_products.id_orders and  sl_orders.Status='Shipped' 	$query and sl_orders_products.status = 'Active' and  sl_orders_products.ID_products>1000000  order by sl_orders.id_orders,sl_orders_products.id_products");	  
		$cont_l=$sth->fetchrow;
		if ($cont_l>0 and  $query ){	               
			my ($mdate) = &get_date();
			$mdate =~ s/-//g;
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=order_detail_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
			print '"'.join('","', @xcols)."\"\n";

			$sth = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.id_orders = sl_orders_products.id_orders and  sl_orders.Status='Shipped' 	$query and sl_orders_products.status = 'Active' and  sl_orders_products.ID_products>1000000 ");	  
			while ($rec = $sth->fetchrow_hashref()){		
				my (@cols);
				my ($sth11) = &Do_SQL("SELECT * FROM sl_products WHERE ID_products = RIGHT('$rec->{'ID_products'}',6)");
				my ($tmp11) = $sth11->fetchrow_hashref();			
				my ($tax,$taxsale,$amount_price,$first_pay,$amount_dif,$rounded,$number_pay,$pay_type,$for_pay,$paydate,$paydateamount,$paytype, $paydateamount);
				$cols[0] = $rec->{'ID_orders'};						
				$cols[1] = $rec->{'ID_orders_products'};
				$cols[2] = $rec->{'ID_products'};
				$cols[3] = $rec->{'ShpDate'};
				$cols[4] = $tmp11->{'SPrice'};
				$cols[5] = $tmp11->{'SPrice1'};
				$cols[6] = $tmp11->{'SPrice2'};
				$cols[7] = $tmp11->{'SPrice3'};
				$cols[8] = $tmp11->{'SPrice4'};
				$cols[9] = $rec->{'OrderNet'};
				$cols[10] = $rec->{'OrderShp'};							
				$tax=0.00;
				$tax = sprintf("%.2f", $rec->{'OrderTax'});			    			    		    				
				$cols[11] = $tax;	
				if ($tax == 0.00){
					$cols[12] = 0.00;	
				}else{
					$taxsale = $tax * $rec->{'OrderNet'};
					$taxsale = sprintf("%.2f", $taxsale);			    			    		    				
					$cols[12] = $taxsale;
				}											
				my ($sth12) = &Do_SQL("SELECT count(*) FROM `sl_orders_products` WHERE id_orders = '$rec->{'ID_orders'}' AND Status='Active'");
				$count_prod=$sth12->fetchrow;
				if ($count_prod>0){
					$cols[13] =  $rec->{'OrderShp'}/$count_prod ;			
				}else{
					$cols[13] =  '0';
				}



				$amount_price = 0.00;
				$amount_price = $rec->{'OrderNet'} + $rec->{'OrderShp'} + $taxsale;					
				$cols[14] = $amount_price;			
				my ($sth2) = &Do_SQL("SELECT Amount FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' and Status='Approved' ");				
				$first_pay=$sth2->fetchrow;				
				if ($first_pay > 0) {					
					if ($amount_price == $first_pay){
						$cols[15]=0.00;
					}else{						  		    						
						$amount_dif = $amount_price - $first_pay;					
						$rounded = sprintf("%.2f", $first_pay);			    			    		    
						if ($rounded == 0.00){
							$rounded = $rounded * (-1);			    			    		    
					  }	
						$cols[15] = $rounded;						
					}
				}else{
					$cols[15]=0.00;
				}
				$cols[16] = $tmp11->{'SLTV_NetCost'};	 
				my ($sth5) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'  and Status='Approved'");
				$number_pay=$sth5->fetchrow;

				my ($sth13) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'  and Status='Approved' ");
				$amount_pay=$sth13->fetchrow;
				if($amount_pay == $amount_price and $number_pay == 1){
					$pay_type="Regular";
				}elsif($number_pay > 1){
					$pay_type="Flex. Pay";
				}elsif($number_pay == 0){
					$pay_type="Without type pay";
				}

				$cols[17] = $pay_type;	 
				my ($sth3) = &Do_SQL("SELECT Type,PmtField1 FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'  group by Type");		  
				$rec3=$sth3->fetchrow_hashref;
				if($rec3->{'Type'} eq 'Credit-Card'){
					$for_pay= $rec3->{'PmtField1'} ;
				}else{
					$for_pay= $rec3->{'Type'};
				}
				$cols[18] = $for_pay;	
				$paydate='';
				$paydateamount=0.00;
				$paytype='';
				my ($sth13) = &Do_SQL("SELECT CapDate,Amount,Type  FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}' AND Status = 'Approved' order by CapDate,Amount");
				$ind=1;
				while($tmp13=$sth13->fetchrow_hashref()){					
					if ($ind == 1){
						$paydate=$tmp13->{'CapDate'};
						$paydateamount=$tmp13->{'Amount'};	
						$paytype=$tmp13->{'Type'};						
					}
					if ($tmp13->{'Amount'} >= $paydateamount){
						$paydate=$tmp13->{'CapDate'};
						$paydateamount=$tmp13->{'Amount'};	
						$paytype=$tmp13->{'Type'};						
					}
					$ind++;										
				}			
				if ($paytype eq 'Check'){
					$cols[19] = $rec->{'Date'};	
				}else{
					$cols[19] = $paydate;	
				}
				$cols[20] = $paydateamount; 			
				$cols[21] = $rec->{'ID_customers'};
				my ($sth8) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
				my ($tmp) = $sth8->fetchrow_hashref();
				$cols[22] = $tmp->{'FirstName'};
				$cols[23] = $tmp->{'LastName1'};
				$cols[24] = $tmp->{'LastName2'};
				$cols[25] = $tmp->{'Phone1'};
				$cols[26] = $tmp->{'Phone2'};			
				$cols[27] = $rec->{'shp_Zip'};
				$cols[28] = $rec->{'shp_Urbanization'};
				$cols[29] = $rec->{'shp_City'};
				$cols[30] = substr($rec->{'shp_State'},0,2);
				$cols[31] = $rec->{'shp_Address1'} . ' ' . $rec->{'shp_Address2'} . ' ' . $rec->{'shp_Address3'};				
				print '"'.join('","', @cols)."\"\n";;
			}		
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reporder_detail.html');
}



sub fin_reporder_all {
# --------------------------------------------------------
#
	if ($in{'action'}){
		my ($first_pay,$amount_price,$query,$k);
		##0'ORDER-PL',1'ITEM-ID',2'NAME',3'LASTNAME1',4'LASTNAME2',5'PHONE1',6'PHONE2',7'ZIP',8'URBANIZATION',9'CITY',10'STATE',11'ADDRESS'
		my (@xcols) = ('DATE','ID-ORDERS','NET','S&H','TAX%','TAX$','DISC$','AMOUNT','COUNTRY','STATE','CLIENT','NAME','LAST1','LAST2','STATUS');
		if ($in{'reportdatef'} and $in{'reportdatet'}){
			$query = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}' and sl_orders_payments.Capdate <= '$in{'reportdatet'}' ) ";
			$k = " and  sl_orders_payments.Capdate >= '$in{'reportdatef'}' and sl_orders_payments.Capdate <= '$in{'reportdatet'}'  GROUP   BY   sl_orders.ID_orders,sl_orders_payments.Capdate         	ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif($in{'reportdatef'}){
			$query = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}')  ";
			$k = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}')  GROUP   BY   sl_orders.ID_orders,sl_orders_payments.Capdate         	ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif($in{'reportdatet'}){
			$query = " and ( sl_orders_payments.Capdate <= '$in{'reportdatet'}')  ";
			$k = " and ( sl_orders_payments.Capdate <= '$in{'reportdatet'}')  GROUP   BY   sl_orders.ID_orders,sl_orders_payments.Capdate         	ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif(!$in{'reportdatef'} and !$in{'reportdatet'}){
			$query = " ";
			$k = " ";
		}
		$cont_l=0;
		my($tgr) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_payments WHERE sl_orders.id_orders =  sl_orders_payments.id_orders and   sl_orders_payments.Status = 'Approved' and    sl_orders_payments.AuthCode > 0 	$query ");	  
		$cont_l=$tgr->fetchrow;

		if ($cont_l>0 and  $query ){	               
			my ($mdate) = &get_date();
			$mdate =~ s/-//g;
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=order_all_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
			@cols = ('Order Date(Capt)','ID_orcers','OrderNet','OrderShp','Tax %','Tax $','Discount','Total','Shp County','Shp State',
					'ID_customer','First Name','Last Name1','Last Name2','Order Status');
			print '"'.join('","', @cols)."\"\n";;
			my ($sthd) = &Do_SQL("SELECT sl_orders.ID_orders, MIN(sl_orders_payments.Capdate) as x, 
			                      sl_orders.OrderNet, sl_orders.OrderShp, sl_orders.OrderTax, 
			                      sl_orders.OrderDisc, sl_orders.shp_Zip, sl_orders.shp_State,
			                      sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1, sl_customers.LastName2, sl_orders.Status  
			                      FROM sl_orders, sl_orders_payments, sl_customers	  
			                      WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders and 
			                            sl_orders_payments.Status = 'Approved' and 
			                            sl_orders_payments.AuthCode > 0 and	
			                            sl_orders.id_customers = sl_customers.id_customers  $k");				
			while ($rec = $sthd->fetchrow_hashref()){		
				my (@cols);
				my ($tax,$taxsale,$amount_price,$first_pay,$amount_dif,$rounded,$number_pay,$pay_type,$for_pay,$paydate,$paydateamount,$paytype, $paydateamount);
				$cols[0] = $rec->{'x'};						
				$cols[1] = $rec->{'ID_orders'};
				$cols[2] = sprintf("\$ %.2f", $rec->{'OrderNet'});
				$cols[3] = sprintf("\$ %.2f", $rec->{'OrderShp'});

				$cols[4] = sprintf("%.2f \%", $rec->{'OrderTax'}*100);	;	
				$cols[5] = sprintf("\$ %.2f", $rec->{'OrderNet'}*$rec->{'OrderTax'});

				$cols[6] = sprintf("\$ %.2f", $rec->{'OrderDisc'});

				$amount_price = 0.00;
				$amount_price = $rec->{'OrderNet'} + $rec->{'OrderShp'} + $taxsale;											
				$cols[7] = sprintf("\$ %.2f", $amount_price);

				$cols[8] = &load_name('sl_zipcodes','ZipCode',$rec->{'shp_Zip'},'CountyName');
				$cols[9] = $rec->{'shp_State'};
				$cols[10] = $rec->{'ID_customers'};							
				$cols[11] = $rec->{'FirstName'};				
				$cols[12] = $rec->{'LastName1'};				
				$cols[13] = $rec->{'LastName2'};				
				$cols[14] = $rec->{'Status'};				
				print '"'.join('","', @cols)."\"\n";;
			}		
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reporder_all.html');
}
sub fin_reporder_pay {
# --------------------------------------------------------
#

	if ($in{'action'}){
		my ($first_pay,$amount_price,$query,$k);
		##0'ORDER-PL',1'ITEM-ID',2'NAME',3'LASTNAME1',4'LASTNAME2',5'PHONE1',6'PHONE2',7'ZIP',8'URBANIZATION',9'CITY',10'STATE',11'ADDRESS'
		my (@xcols) = ('ID-ORDERS','AMOUNT','CAPDATE','PAYDATE-PROGRAM','PAY-TYE');
		if ($in{'reportdatef'} and $in{'reportdatet'}){
			$query = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}' and sl_orders_payments.Capdate <= '$in{'reportdatet'}' ) ";
			$k = " and  sl_orders_payments.Capdate >= '$in{'reportdatef'}' and sl_orders_payments.Capdate <= '$in{'reportdatet'}'  GROUP   BY   sl_orders_payments.id_orders, sl_orders_payments.ID_orders_payments  ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif($in{'reportdatef'}){
			$query = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}') ";
			$k = " and ( sl_orders_payments.Capdate >= '$in{'reportdatef'}')  GROUP   BY   sl_orders_payments.id_orders, sl_orders_payments.ID_orders_payments  ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif($in{'reportdatet'}){
			$query = " and ( sl_orders_payments.Capdate <= '$in{'reportdatet'}') ";
			$k = " and ( sl_orders_payments.Capdate <= '$in{'reportdatet'}')  GROUP   BY   sl_orders_payments.id_orders, sl_orders_payments.ID_orders_payments  ORDER BY  sl_orders_payments.Capdate ASC ";
		}elsif(!$in{'reportdatef'} and !$in{'reportdatet'}){
			$query = " ";
			$k = " ";
		}
		$cont_l=0;
		my($tgr) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE sl_orders_payments.Status = 'Approved' and 
											sl_orders_payments.AuthCode > 0  and
											sl_orders_payments.CapDate != '0000-00-00' 	$query ");	  

		$cont_l=$tgr->fetchrow;		

		if ($cont_l>0 and  $query ){	               
			my ($mdate) = &get_date();
			$mdate =~ s/-//g;
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=order_pay_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
			@cols = ('ID_orders','ID_orders_payments','Amount','Capt Date','Payment Date','Payment Method','Auth Trans ID','Capt Tran ID','Reconcilation ID'); 
			print '"'.join('","', @cols)."\"\n";;
			my ($sthd) = &Do_SQL("SELECT sl_orders_payments.ID_orders, sl_orders_payments.ID_orders_payments,
														sl_orders_payments.Amount, sl_orders_payments.CapDate,
														sl_orders_payments.Paymentdate, sl_orders_payments.Type, 
														sl_orders_payments.PmtField1, sl_orders_payments.ID_orders_payments
														FROM sl_orders_payments
														WHERE sl_orders_payments.Status = 'Approved' and 
														sl_orders_payments.AuthCode > 0  and
														sl_orders_payments.CapDate != '0000-00-00' $k");				
			while ($rec = $sthd->fetchrow_hashref()){		
				my (@cols);
				my ($tax,$taxsale,$amount_price,$first_pay,$amount_dif,$rounded,$number_pay,$pay_type,$for_pay,$paydate,$paydateamount,$paytype, $paydateamount);

				$cols[0] = $rec->{'ID_orders'};	
				$cols[1] = $rec->{'ID_orders_payments'};						
				$cols[2] = sprintf("\$ %.2f", $rec->{'Amount'});;
				$cols[3] = $rec->{'CapDate'};
				if ($rec->{'Paymentdate'} eq '0000-00-00'){
					$cols[4] = 'N/A';
				}else{
					$cols[4] = $rec->{'Paymentdate'};
				}
				if($rec->{'Type'} eq 'Credit-Card'){
					$for_pay= $rec->{'PmtField1'} ;
				}else{
					$for_pay= $rec->{'Type'};
				}
				$cols[5] = $for_pay;

				my ($authnumber) = &load_name('sl_orders_payments','ID_orders_payments',$rec->{'ID_orders_payments'},'AuthCode');
				$authnumber =~ s/\s//g;
				if ($cols[5] ne 'Check'){
					my ($sth) = &Do_SQL("SELECT Data FROM sl_orders_plogs WHERE ID_orders='$rec->{'ID_orders_payments'}' AND (Data like '%ccauthreply_authorizationcode=$authnumber%' OR Data like '%ccAuthReply_authorizationCode = $authnumber%');");
					my (@ary) = split (/\n/, $sth->fetchrow);
					for (0..$#ary){
						if ($ary[$_] =~ /^requestid =(.*)/i){
							$cols[6] = $1;
						}elsif ($ary[$_] =~ /^requestid=(\d+)\|\d+/i){
							$cols[6] = $1;
						}
					}
					if ($cols[6]){
						my ($sth) = &Do_SQL("SELECT Data FROM sl_orders_plogs WHERE ID_orders='$rec->{'ID_orders_payments'}' AND Data like '%ccCaptureService_authRequestID = $cols[6]%';");
						my (@ary) = split (/\n/, $sth->fetchrow);
						for (0..$#ary){
							if ($ary[$_] =~ /^ccCaptureReply_reconciliationID = (.*)/i){
								$cols[8] = "'".$1;
							}elsif ($ary[$_] =~ /^requestID = (\d+)/i){
								$cols[7] = "'".$1;
							}
						}
						$cols[6] = "'".$cols[6];
					}else{
						$cols[6] = "Not Found";
					}
				}elsif($cols[5] eq 'Check'){
					my ($sth) = &Do_SQL("SELECT Data FROM sl_orders_plogs WHERE ID_orders='$rec->{'ID_orders'}' AND (Data like '%PayNetECheckAuthorizationNumber=$authnumber%');");
					my (@ary) = split (/\n/, $sth->fetchrow);
					for (0..$#ary){
						if ($ary[$_] =~ /^requestID = (.*)/i){
							$cols[6] = "'".$1;
						}elsif ($ary[$_] =~ /^PayNet_Transaction_id=(\d+)/i){
							$cols[6] = "'".$1;
						}
					}
					(!$cols[6]) and ($cols[6] = "Not Found");
					#$cols[7] = "SELECT Data FROM sl_orders_plogs WHERE ID_orders='$rec->{'ID_orders'}' AND (Data like '%PayNetECheckAuthorizationNumber=$authnumber%');";
				}else{
					$cols[6] = 'N/A';
				}
				print '"'.join('","', @cols)."\"\n";;
			}		
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reporder_pay.html');
}



sub fin_reporder_prod {
# --------------------------------------------------------
	if ($in{'action'}){
		my ($first_pay,$amount_price,$query,$k);
		if ($in{'reportdatef'} and $in{'reportdatet'}){
			$query = " and (  sl_orders_products.ShpDate  >= '$in{'reportdatef'}' and  sl_orders_products.ShpDate  <= '$in{'reportdatet'}' ) ";
			$k = " and   sl_orders_products.ShpDate  >= '$in{'reportdatef'}' and  sl_orders_products.ShpDate  <= '$in{'reportdatet'}'  ORDER   BY   sl_orders_products.ShpDate, sl_orders.id_orders  ";
		}elsif($in{'reportdatef'}){
			$query = " and (  sl_orders_products.ShpDate  >= '$in{'reportdatef'}') ";
			$k = " and (  sl_orders_products.ShpDate  >= '$in{'reportdatef'}')  ORDER   BY   sl_orders_products.ShpDate, sl_orders.id_orders  ";
		}elsif($in{'reportdatet'}){
			$query = " and (  sl_orders_products.ShpDate  <= '$in{'reportdatet'}') ";
			$k = " and (  sl_orders_products.ShpDate  <= '$in{'reportdatet'}')  ORDER   BY   sl_orders_products.ShpDate, sl_orders.id_orders ";
		}elsif(!$in{'reportdatef'} and !$in{'reportdatet'}){
			$query = " ";
			$k = " ";
		}
		$cont_l=0;
		my ($tgr) = &Do_SQL("SELECT COUNT(*)
												FROM sl_orders, sl_orders_products , sl_products    
												WHERE sl_orders.ID_orders = sl_orders_products.ID_orders and     
												RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products and
												sl_orders_products.Status = 'Active'	 $query ");	  
		$cont_l=$tgr->fetchrow;				

		if ($cont_l>0 and  $query ){	               
			my ($mdate) = &get_date();
			$mdate =~ s/-//g;
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=order_prod_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
			@cols = ('ID_orders','ID_orders_products','ShipDate','Sale Price','Cost','T','ID_product','Ship Charges');
			print '"'.join('","', @cols)."\"\n";;
			my ($sthd) = &Do_SQL("SELECT sl_orders.ID_orders, sl_orders_products.ID_orders_products ,
								sl_orders_products.ShpDate, sl_orders_products.ID_products ,
								sl_products.Sprice, sl_orders_products.Shipping
								FROM sl_orders, sl_orders_products , sl_products    
								WHERE sl_orders.ID_orders = sl_orders_products.ID_orders and     
								RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products and
								sl_orders_products.Status = 'Active'	$k");
			while ($rec = $sthd->fetchrow_hashref()){		
				my (@cols);
				my ($prod_cost);				
				$cols[0] = $rec->{'ID_orders'};						
				$cols[1] = $rec->{'ID_orders_products'};
				$cols[2] = $rec->{'ShpDate'};
				$cols[3] = sprintf("\$ %.2f", $rec->{'Sprice'});;
				my ($sth2) = &Do_SQL("SELECT AVG(Cost)
						FROM sl_skus_cost
						WHERE RIGHT('$rec->{'ID_products'}',6) = RIGHT(sl_skus_cost.ID_products,6)");
				$prod_cost=$sth2->fetchrow;
				if (!$prod_cost){
					$prod_cost = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'SLTV_NetCost');
					$cols[5] = 'F';
				}else{
					$cols[5] = 'A';
				}
				$cols[4] = sprintf("\$ %.2f", $prod_cost);;					
				$cols[6] = &format_sltvid($rec->{'ID_products'});
				if (!$rec->{'Shipping'}){
					$cols[7] = &load_regular_shipping(substr($rec->{'ID_products'},3,6));
				}else{
					$cols[7] = $rec->{'Shipping'};
				}
				$cols[7] = sprintf("\$ %.2f", $cols[7]);
				print '"'.join('","', @cols)."\"\n";;
			}		
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reporder_prod.html');
}


#################################################################
# OPERATIONS :SETUP     #
#################################################################

sub fin_reports_fp {
# --------------------------------------------------------
	if ($in{'action'}){
		my ($query_tot,$query_list);

		if ($in{'sortby'}){
			$sb = "ORDER BY $in{'sortby'} $in{'sortorder'}";
		}
		$query = "WHERE  sl_orders.id_orders = sl_orders_payments.id_orders AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card'";
		my ($rows) = 0;

		## Filter by Date
		if ($in{'from_date'}){
			++$rows;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>From Date : </td><td class='smalltext'>$in{'from_date'}</td></tr>\n";
			$query .= " AND sl_orders_payments.Paymentdate>='$in{'from_date'}' ";
		}
		if ($in{'to_date'}){
			++$rows;
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>To Date : </td><td class='smalltext'>$in{'to_date'}</td></tr>\n";
			$query .= " AND sl_orders_payments.Paymentdate<='$in{'to_date'}' ";
		}		

		## Filter by Status
		if ($in{'status'}){
			$in{'status'} =~ s/\|/','/g;
			++$rows;			
			$va{'report_tbl'} .= "<tr><td width='100' class='smalltext'>Status : </td><td class='smalltext'>$in{'status'}</td></tr>\n";						
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}

		## Filter BeWeekly | Monthly
		if($in{'period'}  ne ''){
			$query .= " AND sl_orders.dayspay = '$in{'period'}' ";		
		}

		## build report table
    	if ($rows > 0){
    		$tbl_info = $va{'report_tbl'};
			$va{'report_tbl'} = qq |
				<center>
					<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
						<tr>
					    <td class="menu_bar_title" colspan="2">Report : Selected Fields</td>  
						</tr> |;  
			$va{'report_tbl'} .= "$tbl_info</table></center>\n";	
		}

		## Group records by
		if ($in{'reptype'} eq 'day'){
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
			$query_list = "SELECT sl_orders_payments.Paymentdate,COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY sl_orders_payments.Paymentdate $sb ";
		}elsif($in{'reptype'} eq 'week'){
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
			$query_list = "SELECT WEEK(sl_orders_payments.Paymentdate),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY WEEK(sl_orders_payments.Paymentdate) $sb ";
		}elsif($in{'reptype'} eq 'month'){
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
			$query_list = "SELECT MONTH(sl_orders_payments.Paymentdate),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY MONTH(sl_orders_payments.Paymentdate) $sb ";		
		}else{
			$query_tot  = "SELECT COUNT(*),SUM(amount) FROM sl_orders_payments,sl_orders $query";
			$query_list = "SELECT CONCAT(sl_orders.ID_orders,' ',(SELECT CONCAT(FirstName,' ',LastName1) FROM sl_customers WHERE ID_customers=sl_orders.ID_customers),'<br>',Paymentdate,' ',PmtField1 ,' \$ ',Amount),COUNT(*) AS nums,SUM(amount) AS amounts FROM sl_orders_payments,sl_orders $query GROUP BY sl_orders_payments.ID_orders_payments $sb ";
		}
		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}
		&fin_reports_list($query_tot,$query_list);
		return;
	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_reports_fp.html');
}


sub fin_reports_list {
# --------------------------------------------------------
	my ($query_tot,$query_list) = @_;
	my ($sth) = &Do_SQL($query_tot);
	my ($tot_cant,$tot_amount) = $sth->fetchrow_array();

	if ($tot_cant>0 and $tot_amount>0){
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
		while (@ary = $sth->fetchrow_array){
			$va{'searchresults'} .= qq|
				<tr>
					<td>$ary[0]</td>
					<td align="right">|.&format_number($ary[1]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[1]/$tot_cant*100).qq| %)</td>
					<td align="right">|.&format_price($ary[2]).qq|</td>
					<td nowrap class="help_on">&nbsp; (|.&format_number($ary[2]/$tot_amount*100).qq| %)</td>
				</tr>\n|;
		}
		$va{'tot_cant'} = $tot_cant;
		$va{'tot_amount'} = &format_price($tot_amount);
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
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('fin_reports_list_print.html');
	}else{
		($va{'rep1'},$va{'rep2'},$va{'rep3'}) = ('off','on','off');
		print "Content-type: text/html\n\n";
		print &build_page('fin_reports_list.html');
	}
}


sub fin_reporder_cogs {
# --------------------------------------------------------
	if ($in{'action'}){
		my ($query);
		$in{'fromid'} = int($in{'fromid'});
		$in{'toid'} = int($in{'toid'});
		if ($in{'fromid'} and $in{'toid'}){
			$query = "WHERE ID_orders >= '$in{'fromid'}' AND ID_orders <= '$in{'toid'}'";
		}elsif ($in{'toid'}){
			$query = "WHERE ID_orders <= '$in{'toid'}'  ";
		}elsif ($in{'fromid'}){
			$query = "WHERE ID_orders >= '$in{'fromid'}'  ";
		}

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders $query");
		if ($sth->fetchrow > 0){
			#print "Content-type: text/html\n\n";
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=order_cogs.csv\n\n";
			my (@cols) = ('ID_orders','Cost','Type');
			print '"'.join('","', @cols)."\"\n";;
			my ($sth) = &Do_SQL("SELECT ID_orders FROM sl_orders $query");
			while ($cols[0] = $sth->fetchrow){
				$cols[1] = 0;
				my ($sth2) = &Do_SQL("SELECT ID_products FROM sl_orders_products WHERE ID_orders='$cols[0]' AND Status='Active'");
				while ($id_products = $sth2->fetchrow){
					my ($sth3) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost WHERE RIGHT('$id_products',6) = RIGHT(ID_products,6)");
					$cols[1] += $sth3->fetchrow;
					if (!$cols[1] and $id_products ){
						$cols[1] += &load_name('sl_products','ID_products',substr($id_products,3,6),'SLTV_NetCost');
						$cols[2] = 'F';
					}else{
						$cols[2] = 'A';
					}
				}
				$cols[1] = &format_price($cols[1]);
				print '"'.join('","', @cols)."\"\n";
			}
			return;
		}else{
			$va{'message'} = &trans_txt('novalues');	
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
			return;	
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_reporder_cogs.html');
}


sub fin_search_order {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 12/11/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : 

	if ($in{'action'}){
		my ($query);
		if ($in{'pmtfield2'}){
			$query = " AND (PmtField2 like '%".&filter_values($in{'pmtfield2'})."%' AND PmtField2 !='' AND PmtField2 IS NOT NULL )";
		}elsif($in{'pmtfield3'}){
			$query = " AND (PmtField3 like '%".&filter_values($in{'pmtfield3'})."' AND PmtField3 !='' AND PmtField3 IS NOT NULL )";
		}elsif($in{'authcode'}){
			$query = " AND AuthCode = '".&filter_values($in{'authcode'})."'";	
		}
		if ($query){
			if ($in{'refid'}){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders");
				$va{'matches'} = $sth->rows;
				if ($va{'matches'}>0 ){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});								
					&fin_search_order_list("SELECT *,sl_orders.Status AS Status FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'}");
					return;
				}else{
					$va{'message'} = &trans_txt('search_nomatches');
				}
			}else{
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='$in{'type'}' $query GROUP BY sl_orders.ID_orders");
				$va{'matches'} = $sth->rows;
				if ($va{'matches'}>0 ){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});			
					&fin_search_order_list("SELECT *,sl_orders.Status AS Status FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='$in{'type'}' $query GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'}");
					return;
				}else{
					$va{'message'} = &trans_txt('search_nomatches');
				}
			}
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}

	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_search_order.html');
}


sub fin_search_order_list {
# --------------------------------------------------------
	my ($query) = @_;
	my ($sth) = &Do_SQL($query);
	my ($rec);
	my (@c) = split(/,/,$cfg{'srcolors'});
	while ($rec = $sth->fetchrow_hashref()){
		$d = 1 - $d;
		$va{'searchresults'} .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick="trjump('$cfg{'pathcgi_adm_dbman'}?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2')">
				<td class="smalltext" align="right" valign="top" nowrap>$rec->{'ID_orders'}</td>
				<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Date'}</td>
				<td class="smalltext" nowrap class="help_on" valign="top" nowrap>|. &load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},'[FirstName] [LastName1] [LastName2]').qq|</td>
				<td class="smalltext" nowrap class="help_on" valign="top" nowrap>&nbsp; $rec->{'Status'}</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_search_order_list.html');	
}

sub fin_enter_moneyorder {
# --------------------------------------------------------
# Last Modified on: 07/23/08 13:27:26
# Last Modified by: MCC C. Gabriel Varela S and Lic. Roberto C. B�rcenas A.: Se corrigue error de actualizaci�n en sl_preorders sin tener ID_orders
# Last Modified on: 08/22/08 13:23:19
# Last Modified by: MCC C. Gabriel Varela S: 
# Last Modified on: 09/04/08 16:48:18
# Last Modified by: MCC C. Gabriel Varela S: Se agrega funci�n &calc_tax_disc_shp
# Last Modified on: 09/08/08 16:53:04
# Last Modified by: MCC C. Gabriel Varela S: Se modifica la forma de llamar a calc_tax_etc.
# Last Modified RB: 12/30/08  09:35:05 - MO Layaway
# Last Modified on: 02/27/09 16:47:12
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta de validaci�n de pago por porcentaje de error. Estaba mal. 
#Tambi�n se crea paylog para preorders. Correcciones generales.Se cambia el status de la preorden a 'In process' cuando se completa el monto de la venta.
# Last Modified on: 03/02/09 13:22:40
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se guarde el ID del payment al insertar el logo.
# Last Modification by JRG : 03/09/2009 : Se agrega el log
# Last Modified on: 04/17/09 17:12:06
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_admin_users por min�sculas en $usr y otros cambios
# Last Modified RB: 09/04/09  16:28:49 -- Se agregaron los movimientos contables
# Last Modified RB: 09/21/09  11:04:54 -- Cuando se paga una orden, se envia el movimiento contable a la funcion order_deposit
# Last Modified RB: 03/22/10  15:48:54 -- Se cambia el query inicial buscando que lo pagado sea menor que la suma de productos
# Last Modified RB: 06/16/10  12:22:54 -- Se agrega posibilidad de traspaso COD -> Money Order. 
# Last Modified RB: 06/16/10  12:22:54 -- Se agrega OR para ordenes COD Shipped permitan pago extra. 


	my ($err,$id_customer,$ordernet,$status,$idpp,$amt,$max,$min);
	my (@cols) = ('ordertype','order','date','amount','paytype','refid','notes');
	my ($valid) = 1;
	if ($in{'action'}){
		$in{'ordertype'} = 'orders';
		$in{'order'} = int($in{'order'});
		for my $i(0..$#cols){
			if (!$in{$cols[$i]}){
				$error{$cols[$i]} = &trans_txt('required');
				++$err;
			}
		}

		if ($in{'ordertype'} and $in{'order'} > 0 ){
			my ($sth) = &Do_SQL("SELECT IF(Payments IS NULL OR ABS(Payments - Products) > 5,1,0)AS matches FROM sl_$in{'ordertype'}
			LEFT JOIN(SELECT ID_$in{'ordertype'},SUM(Saleprice-Discount+Shipping+Tax)AS Products FROM sl_$in{'ordertype'}_products WHERE ID_$in{'ordertype'} = '$in{'order'}' AND Status NOT IN('Order Cancelled','Inactive') GROUP BY ID_$in{'ordertype'})AS tmp
			ON sl_$in{'ordertype'}.ID_$in{'ordertype'} = tmp.ID_$in{'ordertype'}
			LEFT JOIN(SELECT ID_$in{'ordertype'},SUM(Amount)AS Payments FROM sl_$in{'ordertype'}_payments WHERE ID_$in{'ordertype'} = '$in{'order'}' AND Status='Approved' AND CapDate IS NOT NULL AND CapDate != '' AND CapDate !='0000-00-00'  GROUP BY ID_$in{'ordertype'})AS tmp2
			ON sl_$in{'ordertype'}.ID_$in{'ordertype'} = tmp.ID_$in{'ordertype'}
			WHERE sl_$in{'ordertype'}.ID_$in{'ordertype'}= '$in{'order'}' AND Status NOt IN('Cancelled','Void','System Error') ");
			my ($matches) = $sth->fetchrow;

			if ($matches>0){
				if ($in{'ordertype'} eq 'orders'){
					my ($sth) = &Do_SQL("SELECT ID_customers,Ptype,OrderNet,Status,StatusPrd,StatusPay FROM sl_$in{'ordertype'} WHERE ID_$in{'ordertype'}='$in{'order'}'");	
					my ($id_customer,$ptype,$ordernet,$status,$statuspay, $statusprod) = $sth->fetchrow_array();
					$va{'order_info'} = "($id_customer) " . &load_db_names('sl_customers','ID_customers',$id_customer,'[FirstName] [LastName1] [LastName2]') ."<br>Order : <a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$in{'order'}&tab=2'>$in{'order'}</a> &nbsp;&nbsp; Type: $ptype &nbsp;&nbsp;  Status: $status &nbsp;&nbsp; xPay: $statuspay &nbsp;&nbsp; xProd: $statusprod";
				}
			}else{
				$error{'order'} = &trans_txt('invalid');
				$va{'message'}= &trans_txt('invalid');
				++$err;
			}
		}

		my $cod_query = "";
		### Revisar si la orden es COD y no esta en transito
		my ($sth_shp) = &Do_SQL("SELECT Ptype,IF( (Status IN('New','Pending','Processed') AND PartSent IS NULL) OR Status='Shipped',1,0) AS valid FROM sl_orders 
						LEFT JOIN
							(
								SELECT ID_orders,COUNT(*) AS PartSent FROM sl_orders_products INNER JOIN sl_orders_parts
								ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
								WHERE ID_orders = '$in{'order'}'  GROUP BY ID_orders
							)tmp
							ON sl_orders.ID_orders = tmp.ID_orders
							WHERE sl_orders.ID_orders = '$in{'order'}'; ");
		my($ptype,$valid) = $sth_shp->fetchrow();

		if($ptype eq 'COD' and $valid){
				$cod_query = ", Ptype='Money Order' ";
		}elsif($ptype eq 'COD'){
			$err++;
		}

		## Revisamos si hay pago dentro del rango
		if(!$in{'btn_search'}){
			my ($sth) = &Do_SQL("SELECT 
									ID_orders_payments,Amount,
									ROUND(Amount*(1+($cfg{'porcerror'}+3)/100),2)AS maxp,
									ROUND(Amount*(1-$cfg{'porcerror'}/100),2)AS minp,
									IF(ABS($in{'amount'})<= Amount*(1+($cfg{'porcerror'}+3)/100) AND ABS($in{'amount'}) >= Amount*(1-$cfg{'porcerror'}/100),1,0)AS valid 
								FROM sl_orders_payments WHERE ID_orders='$in{'order'}'  
								AND (Captured='No' OR Captured IS NULL) AND Status NOT IN ('Order Cancelled','Cancelled','Void') 
								ORDER BY ID_orders_payments  DESC LIMIT 1");
			($idpp,$amt,$max,$min,$valid) = $sth->fetchrow();

			## Pago es menor, creamos un nuevo pago y actualizamos el anterior
			if(!$valid and $in{'amount'} < $amt){

				if($idpp){
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Amount = Amount - $in{'amount'}  WHERE ID_orders_payments = '$idpp' ;");
				}

				my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'order'}',Type='$in{'paytype'}',PmtField1='$in{'paytype'}',Amount='$in{'amount'}',Captured='Yes',Status='Approved',CapDate='$in{'date'}', PostedDate=$in{'date'}, Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				$idpp=$sth->{'mysql_insertid'};
				&auth_logging('opr_orders_pay_created',$idpp);
				$valid=1;

			}

			if(!$valid){
				$va{'message'} .= qq|Payment is |.&format_price($amt).qq|. Allowed payments between |.&format_price($min).qq| and |.&format_price($max).qq|<br>|;
				$err++;
			}

		}

		if (!$err){

			$in{'notes'} = &filter_values($in{'notes'});
			$in{'refid'} = &filter_values($in{'refid'});
			$in{'paytype'} = &filter_values($in{'paytype'});
			if ($in{'ordertype'} eq 'orders'){
				## Pago dentro del Rango
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Type='$in{'paytype'}',PmtField9='$in{'refid'}',Amount=$in{'amount'},Captured='Yes',Status='Approved',CapDate='$in{'date'}' WHERE ID_orders_payments = $idpp");
				&auth_logging('opr_orders_pay_updated',$idpp);
				### Creating PayLog
				$query = "RefID=$in{'refid'}\nPaid method=$in{'paytype'}\n$in{'notes'}\nOrder ID:$in{'order'}";
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$in{'order'}',ID_orders_payments = $idpp,Data='$query', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('opr_orders_plogadded',$sth->{'mysql_insertid'});

				## Movimientos Contables
				my ($order_type, $ctype, $ptype,@params);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'order'}';");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = get_deposit_type($idpp,'');
				@params = ($in{'order'},$idpp,1);
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );


				$in{'db'} = 'sl_orders';
				&auth_logging('opr_orders_payments_paid',$in{'order'});
				$va{'message'} = &trans_txt('orders_payments_updated') . "<br>" . 'order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype;


				#Se cambia el status de la preorden a 'In process'
				$sth=&Do_SQL("Update sl_orders set Status=IF(Status='Shipped',Status,'Processed'),shp_type=IF(shp_type=3,1,shp_type) $cod_query where ID_orders=$in{'order'}");

				if($ptype eq 'COD'){
					#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='COD To $in{'paytype'}',Type='Low' ,ID_orders='$in{'order'}',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
					&add_order_notes_by_type($in{'order'},"COD To $in{'paytype'}","Low");
				}

			}

			if (!$err){
				### Reset Form
				for my $i(0..$#cols){
					delete($in{$cols[$i]});
				}
			}

		}elsif($ptype eq 'COD' and $valid){
			if($in{'btn_search'}){
				for (keys %error){
					delete $error{$_};
				}
			}else{
				$va{'message'} .= &trans_txt('cod_order_notvalid');
			}
		}else{
			if($in{'btn_search'}){
				for (keys %error){
					delete $error{$_};
				}
			}else{
				$va{'message'} = &trans_txt('reqfields') if $valid;
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_enter_moneyorder.html');	

}


sub fin_enter_refund{
#-----------------------------------------
# Created on: 09/21/09  11:51:22 By  Roberto Barcenas
# Forms Involved: fin_enter_refund.html 
# Description : Captura un refund en el sistema realizado con cheque.
# Parameters : 

	my ($err,$id_customer,$ordernet,$status);
	my (@cols) = ('ordertype','order','date','amount','paytype','refid','notes');
	if ($in{'action'}){
		$in{'amount'} *= -1	if	$in{'amount'} > 0;
		$in{'ordertype'} = 'orders';
		$in{'order'} = int($in{'order'});
		for my $i(0..$#cols){
			if (!$in{$cols[$i]}){
				$error{$cols[$i]} = &trans_txt('required');
				++$err;
			}
		}
		if ($in{'ordertype'} and $in{'order'}){

			if ($in{'ordertype'} eq 'orders'){
				my ($sth) = &Do_SQL("SELECT ID_customers,OrderNet,Status,StatusPrd,StatusPay FROM sl_$in{'ordertype'} WHERE ID_$in{'ordertype'}='$in{'order'}'");	
				my ($id_customer,$ordernet,$status,$statuspay, $statusprod) = $sth->fetchrow_array();
				$va{'order_info'} = "($id_customer) " . &load_db_names('sl_customers','ID_customers',$id_customer,'[FirstName] [LastName1] [LastName2]') ."<br>Order : <a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$in{'order'}&tab=2'>$in{'order'}</a> &nbsp;&nbsp; Status: $status &nbsp;&nbsp; xPay: $statuspay &nbsp;&nbsp; xProd: $statusprod";
			}

			if($in{'amount'} > 0){
				$error{'amount'} = &trans_txt('invalid');
				++$err;
			}
		}
		if (!$err){
			$in{'notes'} = &filter_values($in{'notes'});
			$in{'refid'} = &filter_values($in{'refid'});
			$in{'paytype'} = &filter_values($in{'paytype'});
			if ($in{'ordertype'} eq 'orders'){
				my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders='$in{'order'}' AND (ABS($in{'amount'})<= ABS(Amount*(1+$cfg{'porcerror'}/100)) AND (Captured='No' OR Captured IS NULL) AND ABS($in{'amount'}) >= (Amount*(1-$cfg{'porcerror'}/100))) AND Amount < 0 AND Status NOT IN ('Order Cancelled','Cancelled','Void') ORDER BY ID_orders_payments  DESC LIMIT 1");
				$idpp = $sth->fetchrow();
				if ($idpp){
					## Pago dentro del Rango
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Type='$in{'paytype'}',PmtField9='$in{'refid'}',Amount=$in{'amount'},Captured='Yes',Status='Approved',CapDate='$in{'date'}' WHERE ID_orders_payments = $idpp");
					&auth_logging('opr_orders_pay_updated',$idpp);
					### Creating PayLog
					$query = "RefID=$in{'refid'}\nPaid method=$in{'paytype'}\n$in{'notes'}\nOrder ID:$in{'order'}";
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$in{'order'}',ID_orders_payments = $idpp,Data='$query', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('opr_orders_plogadded',$sth->{'mysql_insertid'});
					#Se cambia el status de la preorden a 'In process'
					$sth=&Do_SQL("Update sl_orders set StatusPay='None' where ID_orders=$in{'order'}");

					my ($order_type, $ctype, $ptype,@params);
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'order'}';");
					($order_type, $ctype) = $sth->fetchrow();
					$ptype = get_deposit_type($idpp,'');
					@params = ($in{'order'}, $idpp);
					&accounting_keypoints('order_refund_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );

					$in{'db'} = 'sl_orders';
					&auth_logging('opr_orders_payments_paid',$in{'order'});
					$va{'message'} = "Payment Updated";
				}else{
					$va{'message'} = "The Amount entered is different than the amount found.";
					++$err;
				}
			}
			if (!$err){
				### Reset Form
				for my $i(0..$#cols){
					delete($in{$cols[$i]});
				}
			}
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_enter_refund.html');	

}


###################################################################
######## FACTORING
###################################################################

sub fin_factoring_list {
# --------------------------------------------------------
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($count);
	my($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE Status='Financed' GROUP BY CapDate");
	$va{'matches'} = $sth->rows;
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
	my ($sth) = &Do_SQL("SELECT CapDate,COUNT(*) as num,SUM(Amount) as Total FROM sl_orders_payments WHERE Status='Financed' GROUP BY CapDate LIMIT $first,$usr{'pref_maxh'}");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$rec->{'RiskMsg'} =~ s/   /<br>/;

		$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				<td class="smalltext" valign='top' nowrap>$rec->{'CapDate'}</td>
				<td class="smalltext" valign='top' nowrap>Monterey</td>
				<td class="smalltext" valign='top'>|.&format_number($rec->{'num'}).qq|</td>
				<td class="smalltext" valign='top'>|.&format_price($rec->{'Total'}).qq|</td>
			</tr>|;
	}
	if (!$va{'searchresults'}){
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = "<tr><td colspan='5' align='center'>".&trans_txt("search_nomatches")."</td></tr>";
	}

	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_factoring_list.html');
}


sub fin_factoring_monterey {
# --------------------------------------------------------
	if ($in{'action'}){
		my ($query);
		$in{'from_id'} = int($in{'from_id'});
		$in{'to_id'} = int($in{'to_id'});
		if (!$in{'capdate'}){
			$va{'message'}  = &trans_txt('reqfields');
		}
		if ($in{'from_id'}){
			$query .= " AND ID_orders>='$in{'from_id'}' ";
		}
		if ($in{'to_id'}){
			$query .= " AND ID_orders<='$in{'to_id'}' ";
		}
		if ($va{'message'}){
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}else{
			$stdate = $in{'capdate'};
			$stdate =~ s/\///g;
			$end_date = &sqldate_plus(&get_sql_date(),15);
			$end_date_num = &date_to_unixtime($end_date);

			$np_date = &sqldate_plus(&get_sql_date(),35);
			$np_date_num = &date_to_unixtime($np_date);
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=monterey$stdate.csv\n\n";
			my (@cols) = ("Contract ID","Sale Amount","Down Payment","Original Term","Remaining Term (Months)","Note Date","Amount Financed","Remaining Principal Balance Amount","Date of First Payment","Date of Last Payment","Credit Card Number","Expiration Date","Last Name","First Name","Middle Initial","Address 1","Address 2","City","State","Zip","Country","Home Phone","Work Phone","Carrier (UPS FED EX etc.)","Tracking Number","Monthly payment amount","Date of next payment","Product description");
			print '"'.join('","',@cols) . "\"\n";
			my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE 1<(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=sl_orders.ID_orders AND Type='Credit-Card') AND Status='Shipped' AND StatusPay='None' $query");
			while ($order = $sth->fetchrow_hashref()){
				$line = &monterey_order($end_date_num,$np_date_num,1,$order);
				if ($line){
					print "$line\n";
				}else{
					print "$order->{'ID_orders'} ERR\n";
				}
			}
		}
		return;
	}
	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_factoring_monterey.html');
}


sub fin_factoring_bulk {
# --------------------------------------------------------
# Last Modified on: 12/23/08 18:01:19
# Last Modified by: MCC C. Gabriel Varela S: Solicitud de Carlos se agrega s�lo para ejecutar una vez.
# Last Modification by JRG : 03/09/2009 : Se agrega el log
	my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
	if ($in{'action'} and !$in{'pfaction'}){
		$va{'message'}  = &trans_txt('reqfields');
		$error{'pfaction'} = &trans_txt('required');
	}elsif ($in{'action'} and $#ary<0){
		$va{'message'}  = &trans_txt('reqfields');
		$error{'id_orders_bulk'} = &trans_txt('required');
	}elsif ($in{'action'} and $in{'pfaction'} eq 'bb'){
		########################
		##MFS BUY BACK##
		########################
		my ($order_mfs,$rec,$old_query,$sum_fin,$returns,$newstatus,$old_query,$last_created,$sum_fin_neg);
		my ($query,$rpd,$orddate);
		#@buy_backs = (56785);
		for my $i(0..$#ary){
			$order_mfs = $ary[$i];
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$order_mfs' AND Status='Counter Finance'");
			if ($sth->fetchrow >0){
				$va{'changeresult'} .= "$ary[$i] : Already Done<br>";
			}else{
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE id_orders='$order_mfs'");
				if ($sth->fetchrow ==0){	
					$va{'changeresult'} .= "$ary[$i] : ".&trans_txt('invalid')."<br>";
				}else{
					my ($sth) = &Do_SQL("SELECT *, SUM(Amount) as sum_fin FROM sl_orders_payments WHERE id_orders='$order_mfs' AND Status='Financed' GROUP BY ID_orders");
					$rec = $sth->fetchrow_hashref;
					$old_query = ",Type='$rec->{'Type'}',PmtField1='$rec->{'PmtField1'}',PmtField2='$rec->{'PmtField2'}',PmtField3='$rec->{'PmtField3'}',PmtField4='$rec->{'PmtField4'}',PmtField5='$rec->{'PmtField5'}',PmtField6='$rec->{'PmtField6'}',PmtField7='$rec->{'PmtField7'}',PmtField8='$rec->{'PmtField8'}',PmtField9='$rec->{'PmtField9'}' ";
					$sum_fin = $rec->{'sum_fin'};
					if($sum_fin){
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$order_mfs',Amount='$sum_fin',Status='Financed',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
						my ($sth) = &Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
						$last_created = $sth->fetchrow;
						&auth_logging('orders_payments_added',$last_created);
						$sum_fin_neg = $rec->{'sum_fin'}*-1;
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$order_mfs',Amount='$sum_fin_neg',Status='Counter Finance',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
						&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
						my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Approved',CapDate='0000-00-00',Captured='No' WHERE Status='Financed' AND ID_orders='$order_mfs' AND ID_orders_payments<>$last_created");
						&auth_logging('opr_orders_pay_updated',$order_mfs);
					}
					$va{'changeresult'} .= "$ary[$i] : BB Updated<br>";
					#print "$order_mfs,BB Updated,".&check_ord_totals($order_mfs).",".&check_rman($order_mfs).",".&check_returns($order_mfs)."\n";
				}
			}
		}
	}elsif ($in{'action'} and $in{'pfaction'} eq 'fpd'){
		########################
		##MFS FPD##
		########################						
		#@fpd = (69651);
		my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
		my ($query,$rpd,$orddate);
		#@buy_backs = (56785);
		for my $i(0..$#ary){
			$order_mfs = $ary[$i];
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE id_orders='$order_mfs' AND Status='Counter Finance'");
			if ($sth->fetchrow >0){
				$va{'changeresult'} .= "$ary[$i] : AlreadyDone<br>";
				#print "$order_mfs,AlreadyDone,".&check_ord_totals($order_mfs).",".&check_rman($order_mfs).",".&check_returns($order_mfs)."\n";
			}else{
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE id_orders='$order_mfs'");
				if ($sth->fetchrow ==0){	
					$va{'changeresult'} .= "$ary[$i] : ".&trans_txt('invalid')." <br>";
				}else{
					my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_returns, sl_orders_products WHERE sl_returns.id_orders_products=sl_orders_products.id_orders_products AND sl_orders_products.id_orders='$order_mfs';");
					$returns = $sthr->fetchrow;
					if($returns){
						$newstatus= "Cancelled";
					} else {
						$newstatus= "Approved";
					}
					my ($sth) = &Do_SQL("SELECT *, SUM(Amount) as sum_fin FROM sl_orders_payments WHERE id_orders='$order_mfs' AND Status='Financed' GROUP BY ID_orders");
					$rec = $sth->fetchrow_hashref;
					$old_query = ",Type='$rec->{'Type'}',PmtField1='$rec->{'PmtField1'}',PmtField2='$rec->{'PmtField2'}',PmtField3='$rec->{'PmtField3'}',PmtField4='$rec->{'PmtField4'}',PmtField5='$rec->{'PmtField5'}',PmtField6='$rec->{'PmtField6'}',PmtField7='$rec->{'PmtField7'}',PmtField8='$rec->{'PmtField8'}',PmtField9='$rec->{'PmtField9'}' ";
					$sum_fin = $rec->{'sum_fin'};
					if($sum_fin){
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$order_mfs',Amount='$sum_fin',Status='Financed',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
						my ($sth) = &Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
						$last_created = $sth->fetchrow;
						&auth_logging('orders_payments_added',$last_created);
						$sum_fin_neg = $rec->{'sum_fin'}*-1;
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$order_mfs',Amount='$sum_fin_neg',Status='Counter Finance',Captured='Yes',CapDate='$rec->{'CapDate'}',PostedDate=CURDATE(),Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'".$old_query);
						&auth_logging('orders_payments_added',$sth->{'mysql_insertid'});
						my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='$newstatus',CapDate='0000-00-00',Captured='No' WHERE Status='Financed' AND ID_orders='$order_mfs' AND ID_orders_payments<>$last_created");						
						&auth_logging('opr_orders_pay_updated',$order_mfs);
						my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPay='On Collection' WHERE ID_orders='$order_mfs'");
						&auth_logging('opr_orders_updated',$order_mfs);
						$in{'statuspay'} = 'On Collection';
					}
					$va{'changeresult'} .= "$ary[$i] : FPD Updated<br>";
					#print "$order_mfs,FPD Updated,".&check_ord_totals($order_mfs).",".&check_rman($order_mfs).",".&check_returns($order_mfs)."\n";
				}
			}
		}
	}

	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_factoring_bulk.html');
}

sub fin_factoring_list_sko {
# --------------------------------------------------------
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($count);
	my($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE Status='On Collection' GROUP BY CapDate");
	$va{'matches'} = $sth->rows;
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
	my ($sth) = &Do_SQL("SELECT CapDate,COUNT(*) as num,SUM(Amount) as Total FROM sl_orders_payments WHERE Status='On Collection' GROUP BY CapDate LIMIT $first,$usr{'pref_maxh'}");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$rec->{'RiskMsg'} =~ s/   /<br>/;

		$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
				<td class="smalltext" valign='top' nowrap>$rec->{'CapDate'}</td>
				<td class="smalltext" valign='top' nowrap>SKO</td>
				<td class="smalltext" valign='top'>|.&format_number($rec->{'num'}).qq|</td>
				<td class="smalltext" valign='top'>|.&format_price($rec->{'Total'}).qq|</td>
			</tr>|;
	}
	if (!$va{'searchresults'}){
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = "<tr><td colspan='5' align='center'>".&trans_txt("search_nomatches")."</td></tr>";
	}

	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_factoring_list.html');
}

sub fin_factoring_sko{
#-----------------------------------------
# Forms Involved: fin_facttoring_sko.html
# Created on: 07/22/08  17:34:14
# Last Modified on: 07/22/08  17:34:14
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas | based on CH fin_factoring_monterey
# Description : create a file with orders On Collection and depends on testmode variable received, modify the DB rows
# Parameters : from_id, to_id, capdate, testmode
# Last Modified on: 08/28/08 11:39:56
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta para omitir los que tengan un pago Financed y no tengan CounterF

	if ($in{'action'}){
		my ($query);
		if (!$in{'capdate'}){
			$va{'message'}  = &trans_txt('reqfields');
		}

		if ($va{'message'}){
			print "Content-type: text/html\n\n";
			print &build_page('toprint_msg.html');
		}else{

			&rep_check_sko;
			return;
			my ($stdate) = $in{'capdate'};
			$stdate =~ s/\///g;

			print "Content-type: application/vnd.ms-excel\n";
			($in{'tcollection'} eq 'sko') and (print "Content-disposition: attachment; filename=sko_$stdate.csv\n\n") and (my (@cols) = ("Contract ID","Sale Source","Last Name","First Name","Middle Name","Address 1","Address 2","City","State","ZipCode","Country","Phone Number1","Phone Number2","Email","Original Amount","Current Amount Balance","Order Date","Shipping Date","ID Product","Product Name","Credit-Card","# Installments","Carrier (UPS FED EX etc.)","Tracking Number","Date of first payment","Date of last payment", "First Payment Expired "));
			($in{'tcollection'} eq 'mty') and (print "Content-disposition: attachment; filename=mty_$stdate.csv\n\n") and (my (@cols) = ("Contract ID","Sale Amount","Down Payment","Original Term","Remaining Term (Months)","Note Date","Amount Financed","Remaining Principal Balance Amount","Date of First Payment","Date of Last Payment","Credit Card Number","Expiration Date","Last Name","First Name","Middle Initial","Address 1","Address 2","City","State","Zip","Country","Home Phone","Work Phone","Carrier (UPS FED EX etc.)","Tracking Number","Monthly payment amount","Date of next payment","Product description"));
			print '"'.join('","',@cols) . "\"\n";
			my ($sth) = &Do_SQL("SELECT sum(if(TYPE = 'Credit-Card', 1 , 0 )) as Typing,sum(if(sl_orders_payments.Status = 'Counter Finance', 1  , 0 )) as CounterF,sum(if(sl_orders_payments.Status = 'Financed', 1  , 0 )) as Financed, sl_orders. * 
														FROM sl_orders
														INNER JOIN sl_orders_payments ON ( sl_orders.ID_orders = sl_orders_payments.ID_orders ) 
														WHERE sl_orders.Status = 'Shipped'
														AND StatusPay = 'On Collection'
														AND StatusPrd = 'None' $query
														GROUP BY sl_orders.ID_orders
														having Typing >1 and ((CounterF=0 and Financed=0)or(CounterF>0 and Financed>0))");

			while ($order = $sth->fetchrow_hashref()){
				if($in{'tcollection'} eq 'sko'){
					print &col_sko_order($end_date_num,$np_date_num,$order) ."\n";
				}else{
					print &col_monterey_order($end_date_num,$np_date_num,$order) ."\n";
				}
			}
		}
		return;
	}
	print "Content-type: text/html\n\n";
	$va{'page_title'} = trans_txt("pageadmin");
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('fin_factoring_sko.html');
}



sub fin_flexipagos {
# --------------------------------------------------------
	if ($in{'action'}){
		my ($first_pay,$amount_price,$query,$rec_ord,$id_orders,$shpdate);
		if ($in{'reportdatef'} and $in{'reportdatet'}){
			$query = " and ( ShpDate >= '$in{'reportdatef'}' and ShpDate <= '$in{'reportdatet'}' ) ";
		}elsif($in{'reportdatef'}){
			$query = " and ( ShpDate >= '$in{'reportdatef'}') ";
		}elsif($in{'reportdatet'}){
			$query = " and ( ShpDate <= '$in{'reportdatet'}') ";
		}

		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=order_pay_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
		@cols = ('ID_orders','Sale Amount','Date','Amount','Capt Date','Payment Date','Payment Method','Auth Trans ID','Capt Tran ID','Reconcilation ID'); 
		print '"'.join('","', @cols)."\"\n";;
		my ($sth) = &Do_SQL("SELECT ID_orders,ShpDate FROM sl_orders_products WHERE Status='Active' AND ShpDate<>'0000-00-00' AND ShpDate IS NOT NULL $query GROUP BY ID_orders ORDER BY ShpDate ASC");				
		while (($id_orders,$shpdate) = $sth->fetchrow_array()){		
			$ary[0] = $id_orders;

			## Order Info
			my ($sth2) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders=$id_orders");							
			$rec_ord = $sth2->fetchrow_hashref();
			$ary[1] = &format_price($rec_ord->{'OrderNet'}+$rec_ord->{'OrderShp'}+$rec_ord->{'OrderNet'}*$rec_ord->{'OrderTax'});

			## Payments
			my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders=$id_orders ORDER BY Paymentdate");	


			##
			## Skip Orders Check or Pay in Full
			##

			$ary[5] = $shpdate;
			print '"'.join('","', @ary)."\"\n";;

			###
			### Nota: Check Orders Totals : Skip Orders with Errors and Report it.
			###
		}		
		return;
	}	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reports_flexipagos.html');
}




sub fin_repoper_day {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/21/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Call the templete to print the general and by type reports of daily operations
# Parameters : 

	print "Content-type: text/html\n\n";
	print &build_page('fin_repoper_day.html');
}

sub fin_repoper_day_list {
# --------------------------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 2/12/2008 9:43AM
# Last Modified on: 3/06/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Receives the comands and executes the apropiate functions to build all accounting operation daily reports
# Parameters : [action:the call to execute a report] [reportdate:the date to report] [type: 1|3 to build by pay/return] [detail: 1|2|3  call the function to build the detailed reports]

	if(!$in{'action'})
	{
			$va{'message'} = 'You need to execute an action';
			&fin_repoper_day();	
	}else{

		$in{'reportdate'} =~	s/\|//g;
		if(!$in{'reportdate'} and !$in{'reportdateto'} and $in{'sameday'}){
			$in{'reportdate'} = &get_sql_date;
			$in{'reportdateto'} = &get_sql_date;
		}

		############ date to show from
		if($in{'reportdate'}	=~	/\d+/){
			if($in{'reportdate'} =~ /^\|/){
				$in{'reportdate'}=substr($in{'reportdate'},1,11);	
			}
			$in{'reportdateto'} = $in{'reportdate'} if ($in{'sameday'});
		}else{
			my ($sth) = &Do_SQL("SELECT Date FROM sl_orders ORDER BY Date LIMIT 1");
			$in{'reportdate'}= $sth->fetchrow();
		}

		############ date to show to
		if($in{'reportdateto'}){
			if($in{'reportdateto'} =~ /^\|/){
				$in{'reportdateto'}=substr($in{'reportdateto'},1,11);	
			}
		}else{
			$in{'reportdateto'} = &get_sql_date;
		}

		my (@acumulate);

		### General Report
		if(!$in{'export'}){

			@acumulate = &fin_repoper_extract_acumulate_sales_shpdate($in{'reportdate'},$in{'reportdateto'},$in{'type'},'');

			(!$in{'export'}) and ($va{'searchresults'} .= &fin_repoper_sales_shpdate('',@acumulate));
			($in{'export'}) and ($va{'searchresults'} .= &fin_repoper_sales_export('',@acumulate));

			delete($in{'action'});

			############### Print Report	
			if($in{'print'}){
					&printPage($in{'cmd'}.'_print.html');
			############## On Screen	
			}else{
					print "Content-type: text/html\n\n";
					print &build_page($in{'cmd'}.'.html');			
			}


		### Details
		}elsif($in{'export'}){
					&fin_repoper_detail_export_shpdate($in{'reportdate'},$in{'reportdateto'});						
			###	Purchase Orders	
		}
	}
}

sub fin_repoper_detail_export_shpdate{
#-----------------------------------------
# Forms Involved: fin_repoper_sales_detail.html
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/21/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Build the detailed report of payments received in an specific date
# Parameters : [date: The date to report]
# Last Modified RB: 11/19/08  12:07:37 -- Added Refund and Replacement Detailed Data
# Last Modified RB: 02/18/09  11:00:43 -- Skip cancellation operations when apply and fix it Debits extraction in Cancellation Section
# Last Modified RB: 03/09/09  13:29:57 -- Fixed MO deposits counted as Sale Deposits and taking CDA from preorders only with 2 or more payments(Excluded MO and WU deposits)
# Last Modified RB: 03/12/09  16:25:25 -- Fixed CD when MO change to CC
# Last Modified RB: 03/16/09  15:39:46 -- Se agrega rubro de paylog moved from para pagos traspasados de una preorden a otra.
# Last Modified RB: 09/24/09  13:26:34 -- El Csutomer deposits de COD se toma completo(ya no se descuenta el fee)




	my ($datef,$datet,$type) = @_;
	my (@orders,$report,$txc,$page,$date_start,$str);

	print "Content-type: application/octet-stream\n";
	print "Content-disposition: attachment; filename=closebatch_$datef_$datet.csv\n\n";								

	############################											##############################
	############################		SALES SECTION			##############################
	############################											##############################


		$page = qq|\n\n,,,,Report Operation Detailed\n,,,From:,$datef\n,,,To:,$datet\n\n\n|;
    	    
    		#SALES
      	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders  
        									ON sl_orders.ID_orders = sl_orders_products.ID_orders 
        									WHERE sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND sl_orders_products.PostedDate = sl_orders.PostedDate 
        									AND SalePrice > 0 AND ID_products <> '600001018'
        									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ");
        										
      	my ($cont) = $sth->fetchrow;
      	if ($cont > 0){	
      			
      			print  "Sales\nID Order,Product,Regular Price,Discount,Final Price,State,City,County,Tax,Shipping,Item,COGS,Posted Date\n";
      			
      			my $sth = &Do_SQL("SELECT SalePrice,Cost,ID_products,sl_orders.ID_orders,OrderTax,OrderShp,OrderDisc,sl_orders_products.PostedDate,shp_Zip,Shipping,Tax,Discount 
        									FROM sl_orders_products INNER JOIN sl_orders  
        									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND sl_orders_products.PostedDate = sl_orders.PostedDate AND SalePrice > 0 AND ID_products <> '600001018'
        									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ORDER BY ID_products,sl_orders.PostedDate ");									
        									
       			while(my ($ts,$tc,$idp,$ido,$ot,$os,$od,$pd,$sz,$prShp,$prTax,$prDis) = $sth->fetchrow){
       			$txc = '';

       		
       					if(substr($idp,0,1) eq '6'){	$ti = 'Service';
       					}else{	$ti = 'Product';	($tc == 0) and ($tc = &repoper_cogs_product($idp)); }
       		
       					$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName') if $prTax > 0;
       					$txc = &load_name('sl_orders','ID_orders',$ido," CONCAT(LEFT(shp_State,2),',',shp_City) ").",$txc" if $txc ne '';
       					$txc = ',,'	if $txc eq '';
								print "$ido,".&format_sltvid($idp).",$ts,$prDis,".($ts-$prDis).",$txc,$prTax,$prShp,$ti,$tc,$pd\n";		
       			}
       	}
       	
       	
       	#DISCOUNT SERVICES
      	my $sth = &Do_SQL("SELECT COUNT(*) 
        									FROM sl_orders_products INNER JOIN sl_orders  
        									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
        									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND sl_orders.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND SalePrice < 0 AND LEFT(ID_products,1) = 6
        									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ");
        										
      	my ($cont) = $sth->fetchrow;
      	if ($cont > 0){	
      		
      			my $sth = &Do_SQL("SELECT ABS(SalePrice),Cost,ID_products,sl_orders.ID_orders,OrderTax,OrderShp,OrderDisc,sl_orders_products.PostedDate  
        									FROM sl_orders_products INNER JOIN sl_orders  
        									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
        									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND sl_orders.PostedDate BETWEEN '$datef' AND '$datet' 
        									AND SalePrice < 0 AND LEFT(ID_products,1) = 6
        									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ORDER BY sl_orders.ID_orders");									
        									
       			while(my ($ts,$tc,$idp,$ido,$ot,$os,$od,$pd) = $sth->fetchrow){
       			
       					$txc = '';
								$ti = 'Discount';
          			print "$ido,".format_sltvid($idp).",$ts,$od,$ts,$txc,$ot,$os,$ti,$tc,$pd\n";		
       			}
       	}
       	

	############################											##############################
	############################		PAYMENTS SECTION			##############################
	############################											##############################

	## SALE DEPOSITS
	my $sth = &Do_SQL("SELECT  sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders 
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders
											WHERE sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate = sl_orders.PostedDate
											AND (CapDate = sl_orders_payments.PostedDate OR (Capdate < sl_orders_payments.PostedDate 
											AND CapDate BETWEEN '$datef' AND '$datet'))
											AND Amount >0 AND IF( TYPE IN ('Credit-Card', 'Check'), sl_orders_payments.Status = 'Approved'
											AND AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000',
											sl_orders_payments.Status = 'Approved' ) 
											AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND ID_products = '600001018')
											ORDER BY PmtField3,sl_orders_payments.ID_orders ");


	print "\n\n\nSales Deposits\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec =	$sth->fetchrow_hashref()){
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');
		$rec->{'Amount'} -= ($rec->{'Amount'}*0.04)	if $rec->{'Type'} eq 'COD';

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n"	if $rec->{'Type'} !~	/Web Order|Money Order|COD/;
	}


	## CUSTOMER DEPOSITS APPLYING TODAY
my $sth = &Do_SQL("SELECT sl_orders_payments.*
				FROM sl_orders_payments INNER JOIN sl_orders
				ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
				WHERE sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'  AND sl_orders_payments.PostedDate = sl_orders.PostedDate
				AND CapDate IS NOT NULL AND CapDate != '0000-00-00' AND (CapDate < '$datef' OR (CapDate <= '$datet' 
				AND Amount > 0 AND IF(TYPE IN ('Credit-Card', 'Check'), (sl_orders_payments.Status = 'Approved'
				AND AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000' AND ((CapDate <> '0000-00-00' ) OR Captured = 'Yes')), sl_orders_payments.Status = 'Approved' ) 
				AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND ID_products = '600001018')
				ORDER BY PmtField3,sl_orders_payments.ID_orders ");




	print "\n\n\nCustomer Deposits Applying Today\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');
		#$rec->{'Amount'} -= ($rec->{'Amount'}*0.04)	if $rec->{'Type'} eq 'COD';

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
	}


	## CONSECUTIVE DEPOSITS (FP)
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE CapDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate < CapDate
											AND sl_orders_payments.PostedDate = sl_orders.PostedDate 
											AND Amount > 0 AND Type = 'Credit-Card' AND sl_orders_payments.Status = 'Approved' 
											AND AuthCode IS NOT NULL AND AuthCode !='' AND AuthCode !='0000' 
											ORDER BY PmtField3,sl_orders_payments.ID_orders ");

	print "\n\n\nConsecutive Deposits(FP)\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\r\n";


	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n"	if $rec->{'Type'} !~	/Web Order|Money Order|COD/;
	}


	## FINANCED
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE CapDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate < CapDate
											AND sl_orders_payments.PostedDate = sl_orders.PostedDate 
											AND Amount > 0 AND Type = 'Credit-Card' AND sl_orders_payments.Status = 'Financed' 
											ORDER BY PmtField3,sl_orders_payments.ID_orders ");

	print "\n\n\nFinanced\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n"	if $rec->{'Type'} !~	/Web Order|Money Order|COD/;
	}


	## CUSTOMER DEPOSITS
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
						FROM sl_orders_payments INNER JOIN sl_orders 
						ON sl_orders.ID_orders = sl_orders_payments.ID_orders
						WHERE CapDate BETWEEN '$datef' AND '$datet'
						AND (sl_orders_payments.PostedDate > '$datet' OR sl_orders_payments.PostedDate IS NULL)
						AND (sl_orders_payments.PostedDate = sl_orders.PostedDate OR sl_orders.PostedDate IS NULL)
						AND Amount >0 AND sl_orders_payments.Status = 'Approved' ORDER BY PmtField3,sl_orders_payments.ID_orders ");

	print "\n\n\nCustomer Deposits\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');



		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n" if $rec->{'Type'} !~	/Web Order|Money Order|COD/;
	}



		#######
		####### ORDER MODIFICATIONS
		#######	


	## RETURN PRODUCTS    
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders  
  									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
  									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND 
  									(SalePrice < 0  OR ID_products IN(600001006,600001014) ) 
  									AND IF(SalePrice < 0,sl_orders_products.Status = 'Returned',
  									sl_orders_products.Status NOT IN('Order Cancelled','Inactive')) ");
  										
	my ($cont) = $sth->fetchrow;
	if ($cont > 0){	

			print  "\n\n\nReturns\nID Order,Product,Regular Price,Discount,Final Price,State,City,County,Tax,Shipping,COGS,Posted Date\n";

			my $sth = &Do_SQL("SELECT ABS(SalePrice),ABS(Cost),ID_products,sl_orders.ID_orders,OrderTax,OrderShp,OrderDisc,sl_orders_products.PostedDate,shp_Zip,ABS(Shipping),ABS(Tax),ABS(Discount) 
  									FROM sl_orders_products INNER JOIN sl_orders  
  									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
  									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND 
  									(SalePrice < 0  OR ID_products IN(600001006,600001014) ) 
  									AND IF(SalePrice < 0,sl_orders_products.Status = 'Returned',
  									sl_orders_products.Status NOT IN('Order Cancelled','Inactive'))
  									ORDER BY ID_products");									
  									
 			while(my ($ts,$tc,$idp,$ido,$ot,$os,$od,$pd,$sz,$prShp,$prTax,$prDis) = $sth->fetchrow){
 			$txc = '';

 		
 					if(substr($idp,0,1) ne '6'){
 						($tc == 0) and ($tc = &repoper_cogs_product($idp));
 						$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName') if $prTax > 0;
       			$txc = &load_name('sl_orders','ID_orders',$ido," CONCAT(LEFT(shp_State,2),',',shp_City) ").",$txc" if $txc ne '';
       			$txc = ',,'	if $txc eq '';
 						print "$ido,".&format_sltvid($idp).",$ts,$prDis,".($ts-$prDis).",$txc,$prTax,$prShp,$tc,$pd\r\n";
 					}else{
 						if($idp ne '600001006' and $idp ne '600001014'){
 							$strser .= "$ido,".&format_sltvid($idp).",$ts,$pd\r\n";
 						}else{
 							$strfee .= "$ido,".&format_sltvid($idp).",$ts,$pd\r\n";
 						}
 					}			
 			}
 			($strser) and (print  "\r\n\r\nReturn Services\r\nID Order,Product,Regular Price,Posted Date\r\n$strser");
			($strfee) and (print  "\r\n\r\nReturn & Restock Fees\r\nID Order,Product,Amount,Posted Date\r\n$strfee");
 	}


	## REPLACE PRODUCTS    
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders  
	  									ON sl_orders.ID_orders = sl_orders_products.ID_orders 
	  									AND sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
	  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND SalePrice > 0
	  									AND  IF(LEFT(ID_products,1) <> 6,((ShpDate IS NOT NULL AND ShpDate <> '' AND ShpDate <> '0000-00-00') OR (Tracking IS NOT NULL AND Tracking <> '')),ID_products = 600001004)
	  									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ");
  										
	my ($cont) = $sth->fetchrow;
	if ($cont > 0){	

			print  "\n\n\nReplacements\nID Order,Product,Regular Price,Discount,Final Price,State,City,County,Tax,Shipping,Item,COGS,Posted Date\n";

			my $sth = &Do_SQL("SELECT SalePrice,Cost,ID_products,sl_orders.ID_orders,OrderTax,OrderShp,OrderDisc,sl_orders_products.PostedDate,shp_Zip,Shipping,Tax,Discount 
  										FROM sl_orders_products INNER JOIN sl_orders  
	  									ON sl_orders.ID_orders = sl_orders_products.ID_orders 
	  									AND sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
	  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND SalePrice > 0
	  									AND  IF(LEFT(ID_products,1) <> 6,((ShpDate IS NOT NULL AND ShpDate <> '' AND ShpDate <> '0000-00-00') OR (Tracking IS NOT NULL AND Tracking <> '')),ID_products = 600001004)
	  									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') 
	  									ORDER BY sl_orders.ID_orders");									
  									
 			while(my ($ts,$tc,$idp,$ido,$ot,$os,$od,$pd,$sz,$prShp,$prTax,$prDis) = $sth->fetchrow){
 			$txc = '';

 		
 					if(substr($idp,0,1) eq '6'){	$ti = 'Service';
 					}else{	$ti = 'Product';	($tc == 0) and ($tc = &repoper_cogs_product($idp)); }
 		
 					$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName') if $prTax > 0;
					$txc = &load_name('sl_orders','ID_orders',$ido," CONCAT(LEFT(shp_State,2),',',shp_City) ").",$txc" if $txc ne '';
       		$txc = ',,'	if $txc eq '';
					print "$ido,".&format_sltvid($idp).",$ts,$prDis,".($ts-$prDis).",$txc,$prTax,$prShp,$ti,$tc,$pd\n";		
 			}
 	}


	## REFUND TRANSACTIONS 
	my $sth = &Do_SQL("SELECT sl_orders_payments.*,sl_orders.PostedDate AS opd
											FROM sl_orders_payments INNER JOIN sl_orders  
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE Reason IN ('Refund','Other') AND CapDate BETWEEN '$datef' AND '$datet' AND Captured = 'Yes'
											AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate > sl_orders.PostedDate
											AND sl_orders_payments.Status IN ('Approved','Credit','ChargeBack')
											AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders
											AND ID_products = 600001018) ");

	print "\n\n\nRefund Transactions\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');

		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
		my ($return_order) = '';
		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$rec->{'opd'}' AND PostedDate <> '0000-00-00' ");
		if($sth->fetchrow() == 0){
			$return_order = 'No Return Founded';
		}else{
				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$rec->{'opd'}' AND PostedDate <> '0000-00-00' ");
				my($res) = $sth->fetchrow();

				$return_order = 'Return in Previous Date' if $res == 1;
				$return_order = 'Return in Posterior Date' if $res == 2;

		}

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'},$return_order\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n"	if $rec->{'Type'} !~	/Web Order|Money Order|COD/;
	}

	## CANCELL TRANSACTIONS
	my $sth = &Do_SQL("SELECT ID_products,SalePrice AS CancelFee, 
											SUM(IF(Amount > 0,Amount,0)) AS Debits, 
											SUM( IF( Amount <0 AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS Credits,
											SUM( IF( Amount >0 AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS debit,
											sl_orders_payments.*
											FROM sl_orders_products INNER JOIN sl_orders_payments ON sl_orders_products.ID_orders = sl_orders_payments.ID_orders
											WHERE ID_products = '600001018' AND sl_orders_payments.Status IN('Approved','Credit','ChargeBack') AND  Captured = 'Yes' AND 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders_products.ID_orders AND Amount <0 AND CapDate BETWEEN '$datef' AND '$datet')
											GROUP BY sl_orders_products.ID_orders ORDER BY PmtField3");										

	print "\n\n\nCancell Transactions\nID Order,ID_Service,Total Debit,Cancell Fee,Total Credit,Method,Posted Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');
		$rec->{'PayPD'} = &load_name('sl_orders_payments','Amount',$rec->{'Credits'},'PostedDate');

		print "$rec->{'ID_orders'},$rec->{'ID_products'},$rec->{'Debits'},$rec->{'CancelFee'},$rec->{'Credits'},$rec->{'Type'},$rec->{'PayPD'}\n";
		$str .= "$rec->{'Type'},$rec->{'Credits'},$rec->{'ID_orders'}\r\n";
		$str .= "$rec->{'Type'},$rec->{'debit'},$rec->{'ID_orders'}\r\n"	if ($rec->{'debit'} > 0);
	}


	## REPLACEMENT TRANSACTIONS 
	my $sth = &Do_SQL("SELECT sl_orders_payments.*,sl_orders.PostedDate AS opd
											FROM sl_orders_payments INNER JOIN sl_orders  
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE Reason IN ('Exchange','Reship') AND CapDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
											AND sl_orders_payments.PostedDate > sl_orders.PostedDate 
											AND sl_orders_payments.Status = 'Approved' ");										

	print "\n\n\nReplacement Transactions\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');


		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
		my ($return_order) = '';
		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$rec->{'opd'}' AND PostedDate <> '0000-00-00' ");
		if($sth->fetchrow() == 0){
			$return_order = 'No Return Founded';
		}else{
				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$rec->{'opd'}' AND PostedDate <> '0000-00-00' ");
				my($res) = $sth->fetchrow();

				$return_order = 'Return in Previous Date' if $res == 1;
				$return_order = 'Return in Later Date' if $res == 2;

		}

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n";
	}		


	## RANGE BEFORE
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders  
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet' 
											AND sl_orders_payments.PostedDate > sl_orders.PostedDate
											AND sl_orders_payments.PostedDate < '$datef' 
											AND sl_orders_payments.Status IN ('Approved','Credit') ");										

	print "\n\n\nBefore Range\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');


		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
		my ($return_order) = '';
		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
		if($sth->fetchrow() == 0){
			$return_order = 'No Return Founded';
		}else{
				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
				my($res) = $sth->fetchrow();

				$return_order = 'Return in Previous Date' if $res == 1;
				$return_order = 'Return in Later Date' if $res == 2;

		}

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n";
	}


	## AFTER RANGE
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders  
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet' 
											AND sl_orders_payments.PostedDate > sl_orders.PostedDate
											AND sl_orders_payments.PostedDate > '$datet' 
											AND sl_orders_payments.Status IN ('Approved','Credit') ");										

	print "\n\n\nAfter Range\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');


		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
		my ($return_order) = '';
		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
		if($sth->fetchrow() == 0){
			$return_order = 'No Return Founded';
		}else{
				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
				my($res) = $sth->fetchrow();

				$return_order = 'Return in Minor Date' if $res == 1;
				$return_order = 'Return in Major Date' if $res == 2;

		}

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n";
	}


	## APPLIED TODAY
	my $sth = &Do_SQL("SELECT sl_orders_payments.*
											FROM sl_orders_payments INNER JOIN sl_orders  
											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet' 
											AND sl_orders_payments.PostedDate > sl_orders.PostedDate AND CapDate < '$datef' AND Capdate <> '0000-00-00' AND Captured = 'Yes' 
											AND sl_orders_payments.Status IN ('Approved','Credit') ");										

	print "\n\n\nApplied Today\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";

	while($rec = $sth->fetchrow_hashref){
       
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');


		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
		my ($return_order) = '';
		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
		if($sth->fetchrow() == 0){
			$return_order = 'No Return Founded';
		}else{
				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
				my($res) = $sth->fetchrow();

				$return_order = 'Return in Minor Date' if $res == 1;
				$return_order = 'Return in Major Date' if $res == 2;

		}

		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
	}
	print "\r\n\r\nOperations Resume\r\n$str";
}

sub fin_repoper_detail_export_movements{
#-----------------------------------------
# Created on: 09/14/09  17:04:31 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified on: 12/06/10 15:13:33
# Last Modified by: MCC C. Gabriel Varela S: Se hace que los campos de exportaci�n no contengan comas, para que no se recorran las columnas.
# Last Time Modified by RB on 02/13/2012: Se agregan columnas Admin User, User Type, Customer Type

	my ($datef,$datet,$type) = @_;
	my (@orders,$report,$txc,$page,$date_start,$str);

	#print "Content-type: text/html\n\n";
	print "Content-type: application/octet-stream\n";
	print "Content-disposition: attachment; filename=cb_detailed_movements_$datef_$datet.csv\n\n";								

	############################											##############################
	############################		SALES SECTION			##############################
	############################											##############################


		$page = qq|\n\n,,,,Detailed Movements Report\n,,,From:,$datef\n,,,To:,$datet\n\n\n|;
    	    
    		#SALES
      	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  ID_accounts IN(41,89,152,170,180,185,187,193/*,311,327*/) 
					  									AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Sale' 
					  									AND sl_movements.Status = 'Active' GROUP BY ID_tableused ");
        										
      	my ($cont) = $sth->fetchrow;
      	if ($cont > 0){	
      			
      			print  "Sales\nID Order,State,City,County,Products,Discount,Final Price,Services,Tax,Shipping,Order Total,Account R.,COGS,Effective Date,Over Payment,Under Payment,Customer Refund,Admin User,User Type,Customer Type\n";
      			
      			#SALES
					  my $sth = &Do_SQL("SELECT
	tmp.ID_tableused AS ID_orders,sl_orders.ID_admin_users,ID_customers,
	shp_Zip AS sz,
	SUM(AR)AS AR,
	SUM(ARPR)AS ARPR,
	SUM(Inventory)AS Inventory,
	SUM(Tax)AS Tax,
	SUM(Products)AS Products,
	SUM(Services)AS Services,
	SUM(Shipping)AS Shipping,
	SUM(Discounts)AS Discounts,
	SUM(COGS)AS COGS,
	EffDate,
	SUM(DiffDebit)AS DiffDebit,
	SUM(DiffCredit)AS DiffCredit,
	SUM(IF(Refunds=1,0,CRefund))AS CRefund  
FROM 
	(
		SELECT 
			ID_tableused,EffDate,
			SUM(IF(ID_accounts=41 AND Credebit = 'Debit',Amount,0)) AS AR,
			SUM(IF(ID_accounts=65 AND Credebit = 'Debit',Amount,0)) AS ARPR,
			SUM(IF(ID_accounts=89 AND Credebit = 'Credit',Amount,0)) AS Inventory,
			SUM(IF(ID_accounts=152 AND Credebit = 'Credit',Amount,0)) AS Tax,
			SUM(IF(ID_accounts=170 AND Credebit = 'Credit',Amount,0)) AS Products,
			SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Services,
			SUM(IF(ID_accounts=185 AND Credebit = 'Credit',Amount,0)) AS Shipping,
			SUM(IF(ID_accounts=187 AND Credebit = 'Debit',Amount,0)) AS Discounts,
			SUM(IF(ID_accounts=193 AND Credebit = 'Debit',Amount,0)) AS COGS,
			SUM(IF(ID_accounts=311 AND Credebit = 'Debit',Amount,0)) AS DiffDebit,
			SUM(IF(ID_accounts=311 AND Credebit = 'Credit',Amount,0)) AS DiffCredit,
			SUM(IF(ID_accounts=327 AND Credebit = 'Credit',Amount,0)) AS CRefund
		FROM	
			sl_movements 
		WHERE  
			ID_accounts IN(41,65,89,152,170,180,185,187,193,311,327) 
			AND EffDate BETWEEN '$datef' AND '$datet' 
			AND tableused='sl_orders' 
			AND Category='Sale' 
			AND Status = 'Active'
			GROUP BY ID_tableused
	)AS tmp
	INNER JOIN sl_orders ON ID_orders = tmp.ID_tableused
LEFT JOIN
	(
		SELECT 
			ID_tableused,
			COUNT(*) AS Refunds 
		FROM 
			sl_movements 
		WHERE 
			ID_accounts=327 
			AND Credebit = 'Debit' 
			AND EffDate BETWEEN '$datef' AND '$datet' 
			AND tableused='sl_orders' 
			AND Category='Sale' 
			AND Status = 'Active'
			GROUP BY ID_tableused  
	)AS tmp2
ON 
	tmp.ID_tableused=tmp2.ID_tableused 
GROUP BY tmp.ID_tableused ORDER BY tmp.ID_tableused;");

				while(my($id_orders,$idau,$idc,$sz,$ar,$apr,$in,$tax,$prod,$ser,$shp,$dis,$cogs,$effdate,$opay,$upay,$cref) = $sth->fetchrow()){
       				$txc = '';
       				$city='';
       				if ($tax > 0)
       				{
	     					$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName');

	     					$city= &load_name('sl_orders','id_orders',$id_orders,'shp_City');
	     					$city=~s/,//g;
	     					$txc = &load_name('sl_orders','ID_orders',$id_orders," CONCAT(LEFT(shp_State,2),',','$city') ").",$txc" if $txc ne '';
	     				}
     					$txc = ',,'	if $txc eq '';

					##
					my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
					my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
					my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

					print "$id_orders,$txc,$prod,$dis,".($prod-$dis).",$ser,$tax,$shp,".($prod-$dis+$ser+$tax+$shp).",".($ar+$apr).",$cogs,$effdate,$opay,$upay,$cref,$adminu,$utype,$ctype\n";
       			}
       	}
       	
       	

	############################											##############################
	############################		PAYMENTS SECTION			##############################
	############################											##############################

	## SALE DEPOSITS
	my $sale_str = '';
	my $sth = &Do_SQL("SELECT
					ID_tableused,
					IF(ID_accounts=1,'Cash',
					IF(ID_accounts=12,'Visa/MC',
					IF(ID_accounts=14,'Amex',
					IF(ID_accounts=16,'Discover',
					IF(ID_accounts=20,'PayPal',
					IF(ID_accounts=329,'Google',
					IF(ID_accounts=330,'Amazon',
					IF(ID_accounts=331,'Descuentolibre',
					IF(ID_accounts=22,'MO/COD','Undefined')))))))))AS PayType,
					Amount,EffDate
					FROM sl_movements
					WHERE  ID_accounts IN(1,12,14,16,20,22,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Sale' AND Credebit='Debit' AND Status = 'Active' ORDER BY EffDate,ID_accounts;");


	while(my($id_orders,$payType,$amount,$effdate) =	$sth->fetchrow()){
		my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
		my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
		my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
		my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

		$sale_str .="$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n";
		$str .= "$payType,$amount,$id_orders,$adminu,$utype,$ctype\r\n"	if $payType !~	/Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
	}


	## COD Sales/CUSTOMER DEPOSITS APPLYING TODAY
	my $sth = &Do_SQL("SELECT
						sl_movements.ID_tableused, 
					  IF(
							  IF(Cash IS NOT NULL,Cash,0) > 0 ,'Cash',
							  IF(IF(VMC IS NOT NULL,VMC,0) > 0 ,'VMC',
							  IF(IF(Amex IS NOT NULL,Amex,0) > 0 ,'Amex',
							  IF(IF(Discover IS NOT NULL,Discover,0) > 0 ,'Discover',
							  IF(IF(PayPal IS NOT NULL,PayPal,0) > 0 ,'PayPal',
							  IF(IF(Google IS NOT NULL,Google,0) > 0 ,'Google',
							  IF(IF(Amazon IS NOT NULL,Amazon,0) > 0 ,'Amazon',
							  IF(IF(Descuentolibre IS NOT NULL,Descuentolibre,0) > 0 ,'Descuentolibre',
							  IF(IF(COD IS NOT NULL,COD,0) > 0 ,'COD','Undefined'))))))))
						)AS PayType,
					  sl_movements.Amount,
					  sl_movements.EffDate,
					  IF(tmp_o.EffDate < '$datef','CDA',IF(tmp_o.EffDate <= sl_movements.EffDate,'Sale','COD')) AS Type
					FROM sl_movements
					LEFT JOIN 
					  (
					     SELECT ID_orders FROM sl_orders WHERE Status ='Shipped'
					  )AS tmp
					ON ID_tableused = tmp.ID_orders
					LEFT JOIN(
					    SELECT
					      ID_tableused,Amount,EffDate,
					      IF(ID_accounts=1,Amount,0) AS Cash,
							  IF(ID_accounts=12,Amount,0) AS VMC,
							  IF(ID_accounts=14,Amount,0) AS Amex,
							  IF(ID_accounts=16,Amount,0) AS Discover,
							  IF(ID_accounts=20,Amount,0) AS PayPal,
							  IF(ID_accounts=329,Amount,0) AS Google,
							  IF(ID_accounts=330,Amount,0) AS Amazon,
							  IF(ID_accounts=331,Amount,0) AS Descuentolibre,
							  IF(ID_accounts=22,Amount,0) AS COD
							FROM sl_movements
							   WHERE  ID_accounts IN(1,12,14,16,20,22,129,329,330,331) AND tableused='sl_orders' AND Category='Deposit' AND Credebit='Debit' AND Status = 'Active' 
					)AS tmp_o
					ON tmp_o.ID_tableused = sl_movements.ID_tableused
					AND tmp_o.Amount = sl_movements.Amount
					AND tmp_o.EffDate <= sl_movements.EffDate  
					WHERE  ID_accounts = 129 AND sl_movements.EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Sale' AND Credebit='Debit' AND sl_movements.Status = 'Active' ORDER BY Type,sl_movements.ID_tableused;");

	my $cod_str = '';
	my $cda_str = '';
	while(my($id_orders,$payType,$amount,$effdate,$type) = $sth->fetchrow()){

		my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
		my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
		my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
		my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');


		$cod_str .="$id_orders,$amount,$payType,$effdate,,$adminu,$utype,$ctype\n"	if $type eq 'COD';
		$cda_str .="$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n"	if $type eq 'CDA';
		$sale_str .="$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n"	if $type eq 'Sale';
		$str .= "$payType,$amount,$id_orders,$adminu,$utype,$ctype\r\n"	if $payType !~	/Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
	}
	print "\n\n\nSale Deposits\nID Order,Amount,Method,Effective Date,Admin User,User Type, Customer Type\r\n$sale_str";
	print "\n\n\nCustomer Deposits Applied\nID Order,Amount,Method,Effective Date,Admin User,User Type, Customer Type\r\n$cda_str";
	print "\n\n\nBofA COD\nID Order,Amount,Method,Effective Date,ID Preorder,Admin User,User Type, Customer Type\r\n$cod_str";


	## SALE REFUND
	########
	########
	######## Falta especificar que el dinero devuelto tenga un customer refund "Sale" en el mismo periodo
	######## 
	########
	########
	########


	my $sth = &Do_SQL("SELECT
  sl_movements.ID_tableused,
  IF(ID_accounts=1,'Cash',
  IF(ID_accounts=12,'Visa/MC',
  IF(ID_accounts=14,'Amex',
  IF(ID_accounts=16,'Discover',
  IF(ID_accounts=20,'PayPal',
  IF(ID_accounts=329,'Google',
  IF(ID_accounts=330,'Amazon',
  IF(ID_accounts=331,'Descuentolibre',
  IF(ID_accounts=22,'MO/COD','Undefined')))))))))AS PayType,
  Amount,EffDate 
  FROM sl_movements
  INNER JOIN
  (
  	SELECT ID_tableused,COUNT(*) FROM sl_movements WHERE ID_accounts IN(170,180) AND tableused='sl_orders'  AND EffDate BETWEEN '$datef' AND '$datet'  AND Category='Sale' AND Credebit='Credit' AND Status = 'Active' GROUP BY ID_tableused
  )AS tmp
  ON sl_movements.ID_tableused = tmp.ID_tableused
  INNER JOIN
  (
  	SELECT ID_tableused,COUNT(*) FROM sl_movements WHERE ID_accounts =327 AND tableused='sl_orders' AND EffDate BETWEEN '$datef' AND '$datet' AND Category='Sale' AND Credebit='Debit' AND Status = 'Active' GROUP BY ID_tableused
  )AS tmp2
  ON sl_movements.ID_tableused = tmp2.ID_tableused
  WHERE  
  ID_accounts IN(1,12,14,16,20,22,329,330,331) 
  AND EffDate BETWEEN '$datef' AND '$datet' 
  AND tableused='sl_orders' 
  AND Category='Sale' 
  AND Credebit='Credit' 
  AND Status = 'Active'
  GROUP BY sl_movements.ID_tableused;");

	print "\n\n\nSale Refunds\nID Order,Amount,Method,Effective Date,Admin User,User Type, Customer Type\n";

	while(my($id_orders,$payType,$amount,$effdate) =	$sth->fetchrow()){

		my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
		my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
		my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
		my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

		print "$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n";
		$str .= "$payType,".($amount*-1).",$id_orders,$adminu,$utype,$ctype\r\n"	if $payType !~ /Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
	}


	## CONSECUTIVE DEPOSITS (FP)
	my $sth = &Do_SQL("SELECT
					ID_tableused,
					IF(ID_accounts=1,'Cash',
				IF(ID_accounts=12,'Visa/MC',
				IF(ID_accounts=14,'Amex',
				IF(ID_accounts=16,'Discover',
				IF(ID_accounts=20,'PayPal',
				IF(ID_accounts=329,'Google',
				IF(ID_accounts=330,'Amazon',
				IF(ID_accounts=331,'Descuentolibre',
				IF(ID_accounts=22,'MO/COD',
				IF(ID_accounts=26,'SKO',
				IF(ID_accounts=265,'BadDebt',
				IF(ID_accounts=306,'CollectionFees','Undefined'))))))))))))AS PayType,
				Amount,EffDate
				FROM sl_movements WHERE  ID_accounts IN(1,12,14,16,20,22,26,265,306,329,330,331)
				AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders'
				AND Category='Flexpay' AND Credebit='Debit'
				AND Status = 'Active' ORDER BY EffDate,ID_accounts; ");

	print "\n\n\nConsecutive Deposits(FP)\nID Order,Amount,Method,Effective Date,Admin User,User Type, Customer Type\r\n";


	while(my($id_orders,$payType,$amount,$effdate) = $sth->fetchrow()){

		my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
		my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
		my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
		my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

		print "$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n";
		$str .= "$payType,$amount,$id_orders,$adminu,$utype,$ctype\r\n"	if $payType !~ /Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
	}


	## CUSTOMER DEPOSITS
	my $sth = &Do_SQL("SELECT
					ID_orders,
					IF(
							IF(Cash IS NOT NULL,Cash,0) > 0 ,'Cash',
							IF(IF(VMC IS NOT NULL,VMC,0) > 0 ,'VMC',
							IF(IF(Amex IS NOT NULL,Amex,0) > 0 ,'Amex',
							IF(IF(Discover IS NOT NULL,Discover,0) > 0 ,'Discover',
							IF(IF(PayPal IS NOT NULL,PayPal,0) > 0 ,'PayPal',
							IF(IF(Google IS NOT NULL,Google,0) > 0 ,'Google',
							IF(IF(Amazon IS NOT NULL,Amazon,0) > 0 ,'Amazon',
							IF(IF(Descuentolibre IS NOT NULL,Descuentolibre,0) > 0 ,'Descuentolibre',
							IF(IF(COD IS NOT NULL,COD,0) > 0 ,'COD','Undefined'))))))))
					)AS PayType,
					sl_movements.Amount,
					EffDate
				FROM sl_movements
				LEFT JOIN
				(
					SELECT ID_tableused AS ID_orders,Amount,ID_accounts,
					SUM(IF(ID_accounts=1,Amount,0)) AS Cash,
				SUM(IF(ID_accounts=12,Amount,0)) AS VMC,
				SUM(IF(ID_accounts=14,Amount,0)) AS Amex,
				SUM(IF(ID_accounts=16,Amount,0)) AS Discover,
				SUM(IF(ID_accounts=20,Amount,0)) AS PayPal,
				SUM(IF(ID_accounts=329,Amount,0)) AS Google,
				SUM(IF(ID_accounts=330,Amount,0)) AS Amazon,
				SUM(IF(ID_accounts=331,Amount,0)) AS Descuentolibre,
				SUM(IF(ID_accounts=22,Amount,0)) AS COD
				FROM sl_movements
				WHERE  ID_accounts IN(1,12,14,16,20,22,329,330,331) AND '$datet' < (SELECT  IF( ShpDate IS NOT NULL AND ShpDate != '0000-00-00', MIN( ShpDate ) , DATE_ADD('$datet',INTERVAL 100 DAY) ) FROM sl_orders_products WHERE ID_orders = sl_movements.ID_tableused) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Deposit' AND Credebit='Debit' AND Status = 'Active'
				GROUP BY ID_tableused
				)AS tmp
				ON ID_tableused = ID_orders
				AND sl_movements.Amount = tmp.Amount AND sl_movements.ID_accounts = tmp.ID_accounts
				WHERE  sl_movements.ID_accounts IN(1,12,14,16,20,22,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND Category='Deposit' AND Credebit='Debit' AND Status = 'Active'
				HAVING ID_orders > 0
				ORDER BY sl_movements.ID_accounts; ");

	print "\n\n\nCustomer Deposits\nID Order,Amount,Method,Effective Date,Admin User,User Type, Customer Type\r\n";

	while(my($id_orders,$payType,$amount,$effdate) = $sth->fetchrow()){

		my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
		my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
		my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
		my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

		print "$id_orders,$amount,$payType,$effdate,,$adminu,$utype,$ctype\n";
		$str .= "$payType,$amount,$id_orders,$adminu,$utype,$ctype\r\n"	if $payType !~ /Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
	}


		#######
		####### ORDER MODIFICATIONS
		#######	


	## RETURN PRODUCTS    
	#SALES
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  ID_accounts IN(41,89,152,170,180,185,187,193) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category = 'Return' AND Status = 'Active';");
  										
	my ($cont) = $sth->fetchrow;
	if ($cont > 0){	

			print  "\n\nReturns\nID Order,State,City,County,Products,Discount,Final Price,Services,Tax,Shipping,Return Fees,Return Total,Account R.,Customer Refund,Effective Date,COGS,Admin User,User Type,Customer Type\n";

			#SALES
		  my $sth = &Do_SQL("SELECT
	ID_tableused,shp_Zip,  
  SUM(IF(ID_accounts=41 AND Credebit = 'Credit',Amount,0)) AS AR,
  SUM(IF(ID_accounts=89 AND Credebit = 'Debit',Amount,0)) AS Inventory,
  SUM(IF(ID_accounts=152 AND Credebit = 'Debit',Amount,0)) AS Tax,
  SUM(IF(ID_accounts=170 AND Credebit = 'Debit',Amount,0)) AS Products,
  SUM(IF(ID_accounts=180 AND Credebit = 'Debit',Amount,0)) AS Services,
  SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Fees,
  SUM(IF(ID_accounts=185 AND Credebit = 'Debit',Amount,0)) AS Shipping,
  SUM(IF(ID_accounts=187 AND Credebit = 'Credit',Amount,0)) AS Discounts,
  SUM(IF(ID_accounts=193 AND Credebit = 'Credit',Amount,0)) AS COGS,
  SUM(IF(ID_accounts=327 AND Credebit = 'Credit',Amount,0)) AS CRefund,
  EffDate
  FROM sl_movements 
  INNER JOIN sl_orders ON ID_orders = ID_tableused
  WHERE  ID_accounts IN(41,89,152,170,180,185,187,193,327) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category = 'Return' AND sl_orders.Status NOT IN('Cancelled', 'Void', 'System Error') AND sl_movements.Status = 'Active' GROUP BY ID_tableused ORDER BY ID_tableused;");

			while(my($id_orders,$sz,$ar,$in,$tax,$prod,$ser,$rfees,$shp,$dis,$cogs,$cref,$effdate) = $sth->fetchrow()){

				$txc = '';
				$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName') if $tax > 0;
				$txc = &load_name('sl_orders','ID_orders',$id_orders," CONCAT(LEFT(shp_State,2),',',shp_City) ").",$txc" if $txc ne '';
				$txc = ',,'	if $txc eq '';

				my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
				my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
				my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
				my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
				my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');


				print "$id_orders,$txc,$prod,$dis,".($prod-$dis).",$ser,$tax,$shp,$rfees,".($prod-$dis-$rfees+$ser+$tax+$shp).",$ar,$cref,$effdate,$cogs,$adminu,$utype,$ctype\r\n";		
 			}
 	}


	## REFUND TRANSACTIONS
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  ID_accounts IN(1,12,14,16,20,22) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Refund' AND Credebit='Credit' AND Status = 'Active';");
  										
	my ($cont) = $sth->fetchrow;
	if ($cont > 0){

		my $sth = &Do_SQL("SELECT
						ID_tableused,
						IF(ID_accounts=1,'Cash',
						IF(ID_accounts=12,'Visa/MC',
						IF(ID_accounts=14,'Amex',
						IF(ID_accounts=16,'Discover',
						IF(ID_accounts=20,'PayPal',
						IF(ID_accounts=329,'Google',
						IF(ID_accounts=330,'Amazon',
						IF(ID_accounts=331,'Descuentolibre',
						IF(ID_accounts=22,'MO/COD','Undefined')))))))))AS PayType,
						Amount,EffDate
					FROM sl_movements
					WHERE
						ID_accounts IN(1,12,14,16,20,22,329,330,331)
						AND EffDate BETWEEN '$datef' AND '$datet'
						AND tableused='sl_orders'
						AND Category='Refund'
						AND Credebit='Credit'
						AND Status = 'Active'
						GROUP BY ID_tableused;");

		print "\n\nRefunds\nID Order,Amount,Method,Effective Date,Admin User,User Type,Customer Type\n";

		while(my($id_orders,$payType,$amount,$effdate) =	$sth->fetchrow()){

			my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
			my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
			my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
			my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
			my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

			print "$id_orders,$amount,$payType,$effdate,$adminu,$utype,$ctype\n";
			$str .= "$payType,".($amount*-1).",$id_orders,$adminu,$utype,$ctype\r\n" if $payType !~ /Cash|PayPal|Google|Amazon|Descuentolibre|COD/;
		}
	}

	## REPLACES
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE  ID_accounts IN(41,89,152,170,180,185,187,193) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category = 'Exchange' AND Status = 'Active';");
  										
	my ($cont) = $sth->fetchrow;
	if ($cont > 0){	

			print  "\n\nExchanges\nID Order,State,City,County,Products,Discount,Final Price,Services,Tax,Shipping,Exchange Total,Account R.,Customer Refund,Effective Date,COGS,Admin User,User Type,Customer Type\n";

			#SALES
		  my $sth = &Do_SQL("SELECT
	ID_tableused,shp_Zip,  
  SUM(IF(ID_accounts=41 AND Credebit = 'Debit',Amount,0)) AS AR,
  SUM(IF(ID_accounts=89 AND Credebit = 'Credit',Amount,0)) AS Inventory,
  SUM(IF(ID_accounts=152 AND Credebit = 'Credit',Amount,0)) AS Tax,
  SUM(IF(ID_accounts=170 AND Credebit = 'Credit',Amount,0)) AS Products,
  SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Services,
  SUM(IF(ID_accounts=185 AND Credebit = 'Credit',Amount,0)) AS Shipping,
  SUM(IF(ID_accounts=187 AND Credebit = 'Debit',Amount,0)) AS Discounts,
  SUM(IF(ID_accounts=193 AND Credebit = 'Debit',Amount,0)) AS COGS,
  SUM(IF(ID_accounts=327 AND Credebit = 'Debit',Amount,0)) AS CRefund,
  EffDate
  FROM sl_movements 
  INNER JOIN sl_orders ON ID_orders = ID_tableused
  WHERE  ID_accounts IN(41,89,152,170,180,185,187,193,327) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category = 'Exchange' AND sl_orders.Status NOT IN('Cancelled', 'Void', 'System Error') AND sl_movements.Status = 'Active' GROUP BY ID_tableused ORDER BY ID_tableused;");

			while(my($id_orders,$sz,$ar,$in,$tax,$prod,$ser,$shp,$dis,$cogs,$cref,$effdate) = $sth->fetchrow()){
 				$txc = '';
				$txc = &load_name('sl_zipcodes','ZipCode',$sz,'CountyName') if $tax > 0;
				$txc = &load_name('sl_orders','ID_orders',$id_orders," CONCAT(LEFT(shp_State,2),',',shp_City) ").",$txc" if $txc ne '';
				$txc = ',,'	if $txc eq '';

				my $idau = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
				my $idc = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
				my $adminu = &load_db_names('admin_users','ID_admin_users',$idau,"[FirstName] [LastName]")  . '(' . $idau . ')';
				my $utype = &load_name('admin_users','ID_admin_users',$idau,'user_type');
				my $ctype = &load_name('sl_customers','id_customers',$idc,'Type');

				print "$id_orders,$txc,$prod,$dis,".($prod-$dis).",$ser,$tax,$shp,".($prod-$dis+$ser+$tax+$shp).",$ar,$cref,$effdate,$cogs,$adminu,$utype,$ctype\r\n";
 			}
 	}
#	
#	
#	
#	## CANCELL TRANSACTIONS
#	my $sth = &Do_SQL("SELECT ID_products,SalePrice AS CancelFee, 
#											SUM(IF(Amount > 0,Amount,0)) AS Debits, 
#											SUM( IF( Amount <0 AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS Credits,
#											SUM( IF( Amount >0 AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS debit,
#											sl_orders_payments.*
#											FROM sl_orders_products INNER JOIN sl_orders_payments ON sl_orders_products.ID_orders = sl_orders_payments.ID_orders
#											WHERE ID_products = '600001018' AND sl_orders_payments.Status IN('Approved','Credit','ChargeBack') AND  Captured = 'Yes' AND 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders_products.ID_orders AND Amount <0 AND CapDate BETWEEN '$datef' AND '$datet')
#											GROUP BY sl_orders_products.ID_orders ORDER BY PmtField3");										
#		
#	print "\n\n\nCancell Transactions\nID Order,ID_Service,Total Debit,Cancell Fee,Total Credit,Method,Posted Date\n";
#	
#	while($rec = $sth->fetchrow_hashref){
#       
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField2'} eq 'Web Order') and ($rec->{'Type'} = 'Web Order');
#		$rec->{'PayPD'} = &load_name('sl_orders_payments','Amount',$rec->{'Credits'},'PostedDate');
#		
#		print "$rec->{'ID_orders'},$rec->{'ID_products'},$rec->{'Debits'},$rec->{'CancelFee'},$rec->{'Credits'},$rec->{'Type'},$rec->{'PayPD'}\n";
#		$str .= "$rec->{'Type'},$rec->{'Credits'},$rec->{'ID_orders'}\r\n";
#		$str .= "$rec->{'Type'},$rec->{'debit'},$rec->{'ID_orders'}\r\n"	if ($rec->{'debit'} > 0);
#	}
#	
#
#
#	## RANGE BEFORE
#	my $sth = &Do_SQL("SELECT sl_orders_payments.*
#											FROM sl_orders_payments INNER JOIN sl_orders  
#											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
#											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet' 
#											AND sl_orders_payments.PostedDate > sl_orders.PostedDate
#											AND sl_orders_payments.PostedDate < '$datef' 
#											AND sl_orders_payments.Status IN ('Approved','Credit') ");										
#		
#	print "\n\n\nBefore Range\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";
#	
#	while($rec = $sth->fetchrow_hashref){
#       
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
#		
#		
#		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
#		my ($return_order) = '';
#		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#		if($sth->fetchrow() == 0){
#			$return_order = 'No Return Founded';
#		}else{
#				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
#												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#				my($res) = $sth->fetchrow();
#				
#				$return_order = 'Return in Previous Date' if $res == 1;
#				$return_order = 'Return in Later Date' if $res == 2;
#												
#		}
#		
#		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
#		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n";
#	}
#	
#	
#	## AFTER RANGE
#	my $sth = &Do_SQL("SELECT sl_orders_payments.*
#											FROM sl_orders_payments INNER JOIN sl_orders  
#											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
#											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet' 
#											AND sl_orders_payments.PostedDate > sl_orders.PostedDate
#											AND sl_orders_payments.PostedDate > '$datet' 
#											AND sl_orders_payments.Status IN ('Approved','Credit') ");										
#		
#	print "\n\n\nAfter Range\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";
#	
#	while($rec = $sth->fetchrow_hashref){
#       
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
#		
#		
#		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
#		my ($return_order) = '';
#		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#		if($sth->fetchrow() == 0){
#			$return_order = 'No Return Founded';
#		}else{
#				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
#												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#				my($res) = $sth->fetchrow();
#				
#				$return_order = 'Return in Minor Date' if $res == 1;
#				$return_order = 'Return in Major Date' if $res == 2;
#												
#		}
#		
#		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
#		$str .= "$rec->{'Type'},$rec->{'Amount'},$rec->{'ID_orders'}\r\n";
#	}
#	
#	
#	## APPLIED TODAY
#	my $sth = &Do_SQL("SELECT sl_orders_payments.*
#											FROM sl_orders_payments INNER JOIN sl_orders  
#											ON sl_orders.ID_orders = sl_orders_payments.ID_orders 
#											WHERE Reason IN ('Refund','Exchange','Reship','Other') AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet' 
#											AND sl_orders_payments.PostedDate > sl_orders.PostedDate AND CapDate < '$datef' AND Capdate <> '0000-00-00' AND Captured = 'Yes' 
#											AND sl_orders_payments.Status IN ('Approved','Credit') ");										
#		
#	print "\n\n\nApplied Today\nID Order,Amount,Method,Reason,Status,Posted Date,Capture Date\n";
#	
#	while($rec = $sth->fetchrow_hashref){
#       
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^3/) and ($rec->{'Type'} = 'American Express');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^4/) and ($rec->{'Type'} = 'Visa');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^5/) and ($rec->{'Type'} = 'Master Card');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} =~ /^6/) and ($rec->{'Type'} = 'Discover');
#		($rec->{'Type'} eq 'Credit-Card') and ( $rec->{'PmtField3'} !~ /^[3-6]/) and ($rec->{'Type'} = 'Undefined');
#		
#		
#		### Searching its return (1->PostedDate < rango , 2->PostedDate > rango,0->PostedDate dentro del rango. Si vacio, no hay return)
#		my ($return_order) = '';
#		my $sth = &Do_SQL("SELECT COUNT(1) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#		if($sth->fetchrow() == 0){
#			$return_order = 'No Return Founded';
#		}else{
#				my $sth = &Do_SQL("SELECT IF( PostedDate < '$datef',1,IF( PostedDate > '$datet', 2, 0 ) ) AS total FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}' 
#												AND SalePrice <0 AND Status NOT IN ('Order Cancelled', 'Inactive') AND PostedDate > '$opd' AND PostedDate <> '0000-00-00' ");
#				my($res) = $sth->fetchrow();
#				
#				$return_order = 'Return in Minor Date' if $res == 1;
#				$return_order = 'Return in Major Date' if $res == 2;
#												
#		}
#		
#		print "$rec->{'ID_orders'},$rec->{'Amount'},$rec->{'Type'},$rec->{'Reason'},$rec->{'Status'},$rec->{'PostedDate'},$rec->{'CapDate'}\n";
#	}
	print "\r\n\r\nOperations Resume\r\nType,Amount,ID Order,Admin User,User Type,Customer Type\r\n$str";
}


sub fin_repoper_extract_acumulate_sales_shpdate{
#-----------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 3/22/2008 9:43AM
# Author: Roberto Barcenas
# Description : Extract the data to report general and by type close_batch
# Parameters : date from, date to, type of report, query modifier
#
#	Locked By: Roberto Barcenas
#
# Last Modified on: 08/11/08 09:23:23
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Add comparison with sl_orders.PostedDate to get only sales data. 
# When PostedDate is minor than products and payments PostedDate, data is the result from  a return operation
#

	my ($datef,$datet,$type,$query) = @_;
	my (@acumulate,@orders,$total_sale,$total_service,$total_cogs,$total_tax,$total_shp,$total_dis,$total_deposits,$total_sales_deposits,$total_predeposits_sales,$total_acre,$total_fpays_deposits,$total_financed_deposits);
	my ($total_return_sale_in,$total_return_cogs_in,$total_return_sale_out,$total_return_service_out,$total_return_cogs_out,$total_replace_debits,$total_return_credits);
	my ($total_return_shp_in,$total_return_dis_in,$total_return_shp_out,$total_return_dis_out,$total_return_fees_in,$total_return_debits,$total_replace_credits,$total_sale_claims);
	my ($total_claim_deposits,$total_claim_ar,$total_pdeposits,$total_modlow_credits,$total_modlow_debits,$total_modup_credits,$total_modup_debits,$total_modapp_credits,$total_modapp_debits,$total_return_tax_in,$total_return_tax_out);
	my ($total_return_service_in,$total_cancell_debits,$total_cancell_credits,$total_cancell_fees,$total_movedfrom_credits,$total_movedfrom_debits);

		##
		##	ORIGINAL TRANSACTION
		##

	## SALES PRODUCTS
	($total_sale,$total_service,$total_cogs,$total_tax,$total_shp,$total_dis,$total_sale_claims) = split(/:/,&products_sale_aux($datef,$datet),7);
	## SALES DEPOSITS	
	$total_sales_deposits = &payments_sale_aux($datef,$datet);
	## CLAIM	DEPOSITS
	($total_claim_deposits,$total_claim_ar) = split(/:/,&payments_claim_aux($datef,$datet),2);
	## CUSTOMER DEPOSITS APPLYING TODAY
	$total_predeposits_sales = &payments_applied_aux($datef,$datet);
	## CONSECUTIVE DEPOSITS (FP)
	$total_fpays_deposits = &payments_flexpay_aux($datef,$datet);
	## FINANCED
	$total_financed_deposits = &payments_financed_aux($datef,$datet);
	#CUSTOMER DEPOSITS
	$total_deposits = &payments_deposit_aux($datef,$datet);
	#CUSTOMER DEPOSITS FROM PREORDERS
	$total_pdeposits = &payments_layaway_aux($datef,$datet);


		##
		##	MODIFICATIONS
		##

	# RETURNS
	($total_return_sale_in,$total_return_service_in,$total_return_fees_in,$total_return_shp_in,$total_return_cogs_in,$total_return_dis_in,$total_return_tax_in) = split(/:/,&products_return_aux($datef,$datet),7);
	# REPLACEMENTS
	($total_return_sale_out,$total_return_service_out,$total_return_shp_out,$total_return_cogs_out,$total_return_dis_out,$total_return_tax_out) = split(/:/,&products_replace_aux($datef,$datet),6);
	# REFUNDS DEBIT & CREDIT 
	($total_return_credits,$total_return_debits) = split(/:/,&payments_return_aux($datef,$datet),2);
	# REPLACEMENTS DEBITS & CREDITS
	($total_replace_debits,$total_replace_credits) = split(/:/,&payments_replace_aux($datef,$datet),2);
	# CANCELLATION
	($total_cancell_credits,$total_cancell_debits,$total_cancell_fees) = split(/:/,&payments_cancell_aux($datef,$datet),3);
	# DEBITS & CREDITS < RANGE
	($total_modlow_credits,$total_modlow_debits) = split(/:/,&payments_modlow_aux($datef,$datet),2);
	# DEBITS & CREDITS > RANGE
	($total_modup_credits,$total_modup_debits) = split(/:/,&payments_modup_aux($datef,$datet),2);
	# DEBITS & CREDITS APPLIED TODAY
	($total_modapp_credits,$total_modapp_debits) = split(/:/,&payments_modapp_aux($datef,$datet),2);
	# DEBITS & CREDITS MOVED FROM OTHER PAYMENT
	($total_movedfrom_credits,$total_movedfrom_debits) = split(/:/,&payments_movedfrom_aux($datef,$datet),2);


     
	$acumulate[0]  = $total_sale;
	$acumulate[1]  = $total_tax;
	$acumulate[2]  = $total_shp;
	$acumulate[3]  = $total_sales_deposits;
	$acumulate[4]  = $total_cogs;
	$acumulate[5]  = $total_deposits;
	$acumulate[6]  = 0;#$total_acre;
	$acumulate[7]  = $total_fpays_deposits;
	$acumulate[8]  = $total_dis;
	$acumulate[9]  = $total_service;
	$acumulate[10]  = $total_predeposits_sales;
	$acumulate[11]  = $total_return_sale_in;
	$acumulate[12]  = $total_return_cogs_in;
	$acumulate[13]  = $total_return_sale_out;
	$acumulate[14]  = $total_return_service_out;
	$acumulate[15]  = $total_return_cogs_out;
	$acumulate[16]  = $total_return_debits;
	$acumulate[17]  = $total_return_credits;
	$acumulate[18]  = $total_financed_deposits;
	$acumulate[19]  = $total_return_shp_in;
	$acumulate[20]  = $total_return_dis_in;
	$acumulate[21]  = $total_return_shp_out;
	$acumulate[22]  = $total_return_dis_out;
	$acumulate[23]  = $total_return_fees_in;
	$acumulate[24]  = $total_replace_debits;
	$acumulate[25]  = $total_replace_credits;
	$acumulate[26]  = $total_sale_claims;
	$acumulate[27]  =	$total_claim_deposits;
	$acumulate[28]  =	$total_claim_ar;
	$acumulate[29]  = $total_pdeposits;
	$acumulate[30]  = $total_modlow_credits;
	$acumulate[31]  = $total_modlow_debits;
	$acumulate[32]  = $total_modup_credits;
	$acumulate[33]  = $total_modup_debits;
	$acumulate[34]  = $total_modapp_credits;
	$acumulate[35]  = $total_modapp_debits;
	$acumulate[36]  = $total_return_tax_in;
	$acumulate[37]  = $total_return_tax_out;
	$acumulate[38]  = $total_return_service_in;
	$acumulate[39]  = $total_cancell_debits;
	$acumulate[40]  = $total_cancell_credits;
	$acumulate[41]  = $total_cancell_fees;
	$acumulate[42]  = $total_movedfrom_credits;
	$acumulate[43]  = $total_movedfrom_debits;

	return @acumulate;
}

sub fin_repoper_sales_shpdate{
#-----------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/21/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Build general and by type reports for sales given a date
# Parameters : acumulates, type of report
# Last Modified RB: 03/16/09  15:38:30 -- Se agrega rubro de paylog moved from para pagos traspasados de una preorden a otra.



   	my ($type,@acumulates) = @_;
		my ($total_sale,$total_service,$total_cogs,$total_tax,$total_shp,$total_dis,$total_deposits,$total_sales_deposits,$total_predeposits_sales,$total_acre,$total_fpays_deposits);
   	my ($total_return_sale_in,$total_return_cogs_in,$total_return_sale_out,$total_return_service_out,$total_return_cogs_out,$total_replace_debits,$total_return_credits);
		my ($total_return_shp_in,$total_return_dis_in,$total_return_shp_out,$total_return_dis_out,$total_return_fees_in,$total_return_debits,$total_replace_credits,$customer_credit,$total_sale_claims);
		my ($total_claim_deposits,$total_claim_ar,$total_pdeposits,$total_modlow_credits,$total_modlow_debits,$total_modup_credits,$total_modup_debits,$total_modapp_credits,$total_modapp_debits,$total_return_tax_in,$total_return_tax_out);
		my ($total_return_service_in,$total_cancell_debits,$total_cancell_credits,$total_cancell_fees,$total_movedfrom_credits,$total_movedfrom_debits);
    
  	$total_sale =$acumulates[0];
  	$total_service =$acumulates[9];
		$total_tax  = $acumulates[1];
		$total_dis  = $acumulates[8];
		$total_shp  = $acumulates[2];
		$total_sales_deposits = $acumulates[3];
		$total_cogs = $acumulates[4];
		$total_deposits = $acumulates[5];
		$total_acre =  $acumulates[6];
	  $total_fpays_deposits = $acumulates[7];
	  $total_predeposits_sales = $acumulates[10];
	  $total_return_sale_in = $acumulates[11] ;
		$total_return_cogs_in = $acumulates[12];
		$total_return_sale_out = $acumulates[13];
		$total_return_service_out = $acumulates[14];
		$total_return_cogs_out = $acumulates[15];
		$total_return_debits = $acumulates[16];
		$total_return_credits = $acumulates[17];
		$total_financed_deposits = $acumulates[18];
		$total_return_shp_in = $acumulates[19];
		$total_return_dis_in = $acumulates[20];
		$total_return_shp_out = $acumulates[21]; 
		$total_return_dis_out = $acumulates[22];
    $total_return_fees_in = $acumulates[23];
    $total_replace_debits = $acumulates[24];
    $total_replace_credits = $acumulates[25];
    $total_sale_claims = $acumulates[26];
    $total_claim_deposits = $acumulates[27];
    $total_claim_ar = $acumulates[28];
    $total_pdeposits = $acumulates[29];
    $total_modlow_credits = $acumulates[30];
		$total_modlow_debits = $acumulates[31];
		$total_modup_credits = $acumulates[32];
		$total_modup_debits = $acumulates[33];
		$total_modapp_credits = $acumulates[34];
		$total_modapp_debits = $acumulates[35];
		$total_return_tax_in = $acumulates[36];
		$total_return_tax_out = $acumulates[37];
		$total_return_service_in = $acumulates[38];
		$total_cancell_debits = $acumulates[39];
		$total_cancell_credits = $acumulates[40];
		$total_cancell_fees = $acumulates[41];
		$total_movedfrom_credits = $acumulates[42];
		$total_movedfrom_debits = $acumulates[43];
    
    
    ###### A/R for sales. 
  	$total_acre = (($total_sale+$total_sale_claims+$total_service+$total_tax+$total_shp) - ($total_dis+$total_sales_deposits+$total_claim_deposits+$total_claim_ar+$total_predeposits_sales));
  	###### A/R for consecutive payments. This one is just the negative of payment
  	$acReS = $total_fpays_deposits * -1;
  	###### Return Debit and Credit
  	$returnDebit   = $total_return_sale_in+$total_return_service_in+$total_return_shp_in+$total_return_tax_in+$total_return_debits;
  	$returnCredit  = $total_return_dis_in+$total_return_fees_in+$total_return_credits;
  	#&cgierr("$total_movedfrom_credits -- $total_movedfrom_debits");
  	###### Replacement Debit and Credit
  	#($total_replace_credits > 0) and ($customer_credit = $total_replace_credits);
  	$replaceDebit  = $total_return_deposits+$total_return_dis_out+$total_replace_debits+$customer_credit+$total_modapp_debits;
  	$replaceCredit = $total_return_sale_out+$total_return_service_out+$total_return_shp_out+$total_return_tax_out+$total_replace_credits;
  	###### Decrease A/R for Returns
  	$arReturns = $returnDebit + $replaceDebit - $returnCredit - $replaceCredit;
  	($arReturns < 0) and ($arReplaces = $arReturns*-1) and ($arReturns = 0);
  	$returnCredit += $arReturns;
  	$replaceDebit += $arReplaces;
  	#&cgierr("$arReturns = $returnDebit + $replaceDebit - $returnCredit - $replaceCredit
  	
  
  	
  	$page .= qq|
  							<div class="accordion-products">
  							<ul id="cbaccordion">
									<li><h3>Sales Facts</h3>
	        					<div>&nbsp;
											<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
												<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
												<tr>
				  								<td nowrap valign="top" align="left" width="25%">Sales Products</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sale) .qq|</td>
					  						</tr>
					  						<!--<tr>
				  								<td nowrap valign="top" align="left" width="25%">Undefined Sales Products</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sale_claims) .qq|</td>
					  						</tr>-->
					  						<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">Sales Services</td>
					  							<td nowrap valign="top" align="right"></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_service).qq|</td>
					  						</tr>	
					  						<tr>
					  							<td nowrap valign="top" align="left">Taxes</td>
					  							<td nowrap valign="top" align="right"></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_tax).qq|</td>
					  						</tr>	
					  						<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">Shipping</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_shp).qq|</td>
					  						</tr>
					  						<tr>
					  							<td nowrap valign="top" align="left">Discounts</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_dis).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>
					  						<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">Total BofA</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_sales_deposits).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;

		if($total_claim_deposits > 0){
					$page .= qq|	<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">Total BofA Claims</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_claim_ar).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;	
			}  						

						$page .= qq|		  						
					  						<tr>
					  							<td nowrap valign="top" align="center">Customer Deposits</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_predeposits_sales).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>
					  						<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">A/R</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_acre).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;

		if($total_claim_ar > 0){
					$page .= qq|	<tr style="background-color:#EEEEE0;">
					  							<td nowrap valign="top" align="left">A/R Claims</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_claim_ar).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;	
		}

					$page .= qq|		  						
					  						<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_dis+$total_sales_deposits+$total_claim_ar+$total_claim_deposits+$total_predeposits_sales+$total_acre).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_sale+$total_sale_claims+$total_service+$total_tax+$total_shp).qq|</strong></td>
					  						</tr>
					  						<tr>
					  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
					  						</tr>
					  						<tr>
					  							<td nowrap valign="top" align="left">Inventory</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_cogs).qq|</td>
					  							</tr>
					  						<tr>
					  							<td nowrap valign="top" align="left">COGS</td>
					  							<td nowrap valign="top" align="right">|.&format_price($total_cogs).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  							</tr>
	  									</table>
	  									&nbsp;
		  							</div>
									</li>

        					<li><h3>Sale Deposits</h3>
	        					<div>&nbsp;
			  							<table width="50%" border="0" cellspacing="0" cellpadding="0" align="center">|;

		  			## Sales Deposits
		  			$i=0;
		  			while (my ($type, $amount) = each(typeOfPaySales) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|	
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_sales_deposits) .qq|</strong></td>
	        							</tr>
	        						</table>
	        						&nbsp;
	        					</div>
	        				</li>	
        						
        					<li><h3>Customer Deposits Applied</h3>
	        					<div>&nbsp;
			  							<table width="50%" border="0" cellspacing="0" cellpadding="0" align="center">|;
        		
        		
        		## Customer Deposits Applying to Sale
		  			$i=0;
		  			while ( my ($type, $amount) = each(typeOfPayPreDptSales) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_predeposits_sales) .qq|</strong></td>
	        							</tr>		
	        						</table>
	        						&nbsp;
										</div>
									</li>	

									<li><h3>Consecutive Deposits (Flexpays)</h3>
	        					<div>&nbsp;
			  							<table width="50%" border="0" cellspacing="0" cellpadding="0" align="center">|;
        		
        		
        		## Flex Pays
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayFpDpt) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_fpays_deposits) .qq|</strong></td>
	        							</tr>	
	        						</table>
	        						&nbsp;
	        					</div>
	        				</li>	

									<li><h3>Financed</h3>
	        					<div>&nbsp;
			  							<table width="50%" border="0" cellspacing="0" cellpadding="0" align="center">|;

        		
        		## Financed
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayFinDpt) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_financed_deposits) .qq|</strong></td>
	        							</tr>	
	        						</table>
	        						&nbsp;
	        					</div>
	        				</li>	

        					<li><h3>Customer Deposits</h3>
	        					<div>&nbsp;
			  							<table width="70%" border="0" cellspacing="0" cellpadding="0" align="center">
				  							<tr style="background-color:#519241; color:#F0FFF0;">
		        								<td valign='top' align='center' colspan="2"><strong>From Orders</strong></td> 
		        						</tr>|;
        		
        		
        		## Customer Deposits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayDpt) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_deposits) .qq|</strong></td>
	        							</tr>	
	        							<tr>
	        								<td valign='top' align='center' colspan="2">&nbsp;</td> 
	        							</tr>
	        							<tr style="background-color:#519241; color:#F0FFF0;">
	        								<td valign='top' align='center' colspan="2"><strong>From Preorders</strong></td> 
	        							</tr>|;
        							
        		## Customer Deposits Preorders
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayPDpt) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
        			$i++;
        		}				
        					
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_pdeposits) .qq|</strong></td>
	        							</tr>
	        						&nbsp;|;

	        	if($total_movedfrom_credits > 0 or $total_movedfrom_debits > 0){					

	        		$page.=qq|
	        						<tr>
	        								<td valign='top' align='center' colspan="2">&nbsp;</td> 
	        						</tr>
							  			<tr style="background-color:#519241; color:#F0FFF0;">
			  								<td valign='top' align='center' colspan="2"><strong>Moved From</td>
					  					</tr>|;


		        		## MovedFrom Debits
				  			$i=0;
				  			while ( my ($type, $amount) = each(%typeOfPayMovefromDebit) ){
				  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
				  				($i%2 eq 1) and ($stlyetd = '');
		        			$page .= qq|<tr>
		        										<td valign='top' align='right' $stlyetd>$type</td>
						  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
		        									</tr>|;
		        			$i++;
		        		}

        		
		        		$page .=qq|
		        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='right'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right' style="color:red"><strong>|.&format_price($total_movedfrom_debits) .qq|</strong></td>
	        							</tr>|;
						}							  			

							$page.=qq|
										</table>  			
	        					</div>
	        				</li>
									&nbsp;
          				<li><h3>Returns & Replacements</h3>
	        					<div>&nbsp;
			  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
			  								<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									Returns
			  									</td>
			  								</tr>
			  								<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
												</tr>	
												<tr>
				  								<td nowrap valign="top" align="left" width="25%">Sales Products</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_return_sale_in).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>	
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Sales Services</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_return_service_in).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>
					  						<tr>
				  								<td nowrap valign="top" align="left" width="25%">Shipping</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_return_shp_in).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Tax</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_return_tax_in).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;

				  	## Return Debits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayReturnDebit) ){
		  				($i%2 eq 1) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 0) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">|.&format_price($amount).qq|</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
        									</tr>|;
        			$i++;
        		}	

					  	$page .=qq|	
					  						<tr>
				  								<td nowrap valign="top" align="left" width="25%">Discounts</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_dis_in).qq|</td>
					  						</tr>
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Restocking and return Fees</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_fees_in).qq|</td>
					  						</tr>|;
        		
        		## Return Credits
		  			$i=1;
		  			while ( my ($type, $amount) = each(%typeOfPayReturnCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		
        		if($arReturns > 0){
		        		$page .=	qq|
		        							<tr>
					  								<td nowrap valign="top" align="left" width="25%">A/R</td>
						  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($arReturns).qq|</td>
						  						</tr>|;
				  	}

				  	$page .=	qq|
	        							<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($returnDebit).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($returnCredit).qq|</strong></td>
					  						</tr>		
	        							<tr>
					  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
					  						</tr>
					  						<tr>
							  					<td nowrap valign="top" align="left">Inventory</td>
							  					<td nowrap valign="top" align="right">|.&format_price($total_return_cogs_in).qq|</td>
							  					<td valign='top' align='right'>&nbsp;</td>
							  					<td nowrap valign="top" align="right">&nbsp;</td>
							  				</tr>
							  				<tr>
							  					<td nowrap valign="top" align="left">COGS</td>
							  					<td nowrap valign="top" align="right">&nbsp;</td>
							  					<td valign='top' align='right'>&nbsp;</td>
							  					<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_cogs_in).qq|</td>
							  				</tr>
							  			</table>
							  			&nbsp;
							  			<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
							  				<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									Replacements
			  									</td>
			  								</tr>
			  								<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
												</tr>
												<tr>
				  								<td nowrap valign="top" align="left" width="25%">Sales Products</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_sale_out).qq|</td>
					  						</tr>	
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Sales Services</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_service_out).qq|</td>
					  						</tr>
					  						<tr>
				  								<td nowrap valign="top" align="left" width="25%">Shipping</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_shp_out).qq|</td>
					  						</tr>
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Tax</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_tax_out).qq|</td>
					  						</tr>|;

				  ## Replacements
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayReplaceCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        								

				  	$page .=qq|					
					  						<tr>
				  								<td nowrap valign="top" align="left" width="25%">Discounts</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_return_dis_out).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;
        		
        		if($total_modapp_debits > 0){
        			$page .=qq|					
					  						<tr style="background-color:#EEEEE0;">
				  								<td nowrap valign="top" align="left" width="25%">Customer Deposits</td>
					  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_modapp_debits).qq|</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right">&nbsp;</td>
					  						</tr>|;
        			
        		}
        		
        		## Replacements
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayReplaceDebit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">|.&format_price($amount).qq|</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right">&nbsp;</td>
        									</tr>|;
        			$i++;
        		}
        		
        		if($arReplaces > 0){
		        		$page .=	qq|
		        							<tr>
					  								<td nowrap valign="top" align="left" width="25%">A/R</td>
						  							<td nowrap valign="top" align="right" width="50%">|.&format_price($arReplaces).qq|</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right">&nbsp;</td>
						  						</tr>|;
				  	}
        		
        		$page .=qq|
        							<tr style="background-color:#CDCDC1;">
				  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
				  							<td nowrap valign="top" align="right"><strong>|.&format_price($replaceDebit).qq|</strong></td>
				  							<td valign='top' align='right'>&nbsp;</td>
				  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($replaceCredit).qq|</strong></td>
				  						</tr>		
											<tr>
				  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
				  						</tr>
				  						<tr>
						  					<td nowrap valign="top" align="left">Inventory</td>
						  					<td nowrap valign="top" align="right">&nbsp;</td>
						  					<td valign='top' align='right'>&nbsp;</td>
						  					<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_return_cogs_out).qq|</td>
						  				</tr>
						  				<tr>
						  					<td nowrap valign="top" align="left">COGS</td>
						  					<td nowrap valign="top" align="right">|.&format_price($total_return_cogs_out).qq|</td>
						  					<td valign='top' align='right'>&nbsp;</td>
						  					<td nowrap valign="top" align="right">&nbsp;</td>
						  				</tr>
						  			</table>
						  			&nbsp;
        					</div>
        				</li>

								<li><h3>Other Debits & Credits</h3>
        					<div>
	        					&nbsp;
	        					<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
			  								<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									Layaway Cancellation
			  									</td>
			  								</tr>
			  								<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
					  						</tr>|;

				  	## Cancellations Credits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayCancellCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		
        		if($total_cancell_fees > 0){
	        		$page .=	qq|
	        							<tr>
				  								<td nowrap valign="top" align="left" width="25%">Cancellation Fees</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_cancell_fees).qq|</td>
					  						</tr>|;
				  	}	
        		

				  	$page .=	qq|
					  						<tr>
					  								<td nowrap valign="top" align="left" width="25%">Customer Deposits</td>
						  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_cancell_debits).qq|</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top">&nbsp;</td>
						  					</tr>
	        							<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_cancell_debits).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_cancell_credits).qq|</strong></td>
					  						</tr>
							  			</table>
							  			&nbsp;
			  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
			  								<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									Before Range (F.P.)
			  									</td>
			  								</tr>
			  								<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
					  						</tr>|;

				  	## ModLow Debits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayModLowDebit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">|.&format_price($amount).qq|</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
        									</tr>|;
        			$i++;
        		}	
        		
        		## ModLow Credits
		  			$i=1;
		  			while ( my ($type, $amount) = each(%typeOfPayModLowCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr $stlyetd>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		

					  	$page .=	qq|
	        							<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_modlow_debits).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_modlow_credits).qq|</strong></td>
					  						</tr>
							  			</table>
							  			&nbsp;
							  			<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
							  				<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									After Range (C.D.)
			  									</td>
					  						</tr>|;

				  ## ModUp Credits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayModUpCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		
        		## ModUp Debits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayModUpDebit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">|.&format_price($amount).qq|</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right">&nbsp;</td>
        									</tr>|;
        			$i++;
        		}
        		
	        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_modup_debits).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_modup_credits).qq|</strong></td>
					  						</tr>
							  			</table>
							  			&nbsp;
							  			<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
							  				<tr style="background-color:#CDCDC1;">
			  									<td colspan="4" align="center" style="font-size:14px; font-weight:bold;background:#8FBC8F;">
			  									Applied Today (vs C.D.)
			  									</td>
					  						</tr>|;

				  ## ModApp Credits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayModAppCredit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		
        		## ModApp Debits
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayModAppDebit) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr>
        										<td nowrap valign="top" align="left" width="25%">$type</td>
				  									<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
				  									<td valign='top' align='right'>&nbsp;</td>
				  									<td nowrap valign="top" align="right" style="color:red">|.&format_price($amount).qq|</td>
        									</tr>|;
        			$i++;
        		}
        		
	        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
					  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
					  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_modapp_credits).qq|</strong></td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_modapp_debits).qq|</strong></td>
					  						</tr>
							  			</table>
							  			&nbsp;
	        					</div>
	        				<li>
	        			</ul>
	        			</div>|;

    return $page;

}


########## Close Batch basado en Movements


sub fin_movements_list {
# --------------------------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 2/12/2008 9:43AM
# Last Modified on: 3/06/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Reporte basado en movimientos
# Parameters :
# Last Modified on: 10/04/10 15:50:32
# Last Modified by: MCC C. Gabriel Varela S: Se quita validaci�n de same day para cuando no vienen datos de fecha

	my (@acumulate);

	$in{'reportdate'} =~	s/\|//g;
	if(!$in{'reportdate'} and !$in{'reportdateto'}){
		$in{'reportdate'} = &get_sql_date;
		$in{'reportdateto'} = &get_sql_date;
	}

	############ date to show from
	if($in{'reportdate'}	=~	/\d+/){
		if($in{'reportdate'} =~ /^\|/){
			$in{'reportdate'}=substr($in{'reportdate'},1,11);	
		}
		$in{'reportdateto'} = $in{'reportdate'} if ($in{'sameday'});
	}else{
		my ($sth) = &Do_SQL("SELECT Date FROM sl_orders ORDER BY Date LIMIT 1");
		$in{'reportdate'}= $sth->fetchrow();
	}

	############ date to show to
	if($in{'reportdateto'}){
		if($in{'reportdateto'} =~ /^\|/){
			$in{'reportdateto'}=substr($in{'reportdateto'},1,11);	
		}
	}else{
		$in{'reportdateto'} = &get_sql_date;
	}



	### General Report
	if(!$in{'export'}){
		@acumulate = &fin_movements_extract($in{'reportdate'},$in{'reportdateto'});

		$va{'searchresults'} = &fin_movements_report('',@acumulate);
		delete($in{'action'});
		############### Print Report	
		if($in{'print'}){
				&printPage($in{'cmd'}.'_print.html');
		############## On Screen	
		}else{
				print "Content-type: text/html\n\n";
				print &build_page($in{'cmd'}.'.html');			
		}
	### Details
	}elsif($in{'export'}){
				&fin_repoper_detail_export_movements($in{'reportdate'},$in{'reportdateto'});						
	}
}


sub fin_movements_extract{
#-----------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 3/22/2008 9:43AM
# Author: Roberto Barcenas
# Description : Extract the data to report general and by type close_batch
# Parameters : date from, date to, type of report, query modifier
#
#	Locked By: Roberto Barcenas
#
# Last Modified on: 08/11/08 09:23:23
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Add comparison with sl_orders.PostedDate to get only sales data. 
# When PostedDate is minor than products and payments PostedDate, data is the result from  a return operation
#

	my ($datef,$datet,$type,$query) = @_;
	my (@acumulate,@orders);

		##
		##	ORIGINAL TRANSACTION
		##


	## SALES PRODUCTS
	my ($total_ar,$total_ar_pr,$total_inventory,$total_tax,$total_sale,$total_service,$total_shp,$total_dis,$total_cogs,$total_diffp_debit,$total_diffp_credit,$total_refund_sale) = &products_sale_mov($datef,$datet);
	## SALES DEPOSITS	
	my ($total_sales_deposits,$total_sales_refund) = &payments_sale_mov($datef,$datet);
	## CUSTOMER DEPOSITS APPLYING TODAY
	my($total_deposits_applied,$tmpsale,$total_codsale) = &payments_applied_mov($datef,$datet);
	$total_sales_deposits+=$tmpsale; 
	## CONSECUTIVE DEPOSITS (FP)
	my ($total_fpays_deposits,$total_sko_decrement,$total_cr_decrement,$total_ar_decrement) = &payments_flexpay_mov($datef,$datet);

	#CUSTOMER DEPOSITS
	my ($total_deposits,$deposits,$total_predeposits,$predeposits) = &payments_deposit_mov($datef,$datet);
	#CUSTOMER DEPOSITS FROM PREORDERS
	my ($total_predeposits_debit,$total_predeposits_credit) = &payments_predeposit_mov($datef,$datet);

		##
		##	MODIFICATIONS
		##

	# RETURNS
	my ($total_ar_return,$total_inventory_return,$total_tax_return,$total_sale_return,$total_service_return,$total_fee_return,$total_shp_return,$total_dis_return,$total_cogs_return,$total_cref_return) = &products_return_mov($datef,$datet);
	# REFUNDS
	my ($total_refund,$total_cref_refund) = &payments_refund_mov($datef,$datet);
	# REPLACEMENTS
	my ($total_ar_exchange,$total_inventory_exchange,$total_tax_exchange,$total_sale_exchange,$total_service_exchange,$total_shp_exchange,$total_dis_exchange,$total_cogs_exchange,$total_cref_exchange) = &products_exchange_mov($datef,$datet);
	# EXCHANGE DEPOSITS
	my $total_deposits_exchange = &payments_exchange_mov($datef,$datet);


  ### Original Movements  
	$acumulate[0]  	= 	$total_sale;
	$acumulate[1]  	= 	$total_service;
	$acumulate[2]  	= 	$total_tax;
	$acumulate[3]  	= 	$total_shp;
	$acumulate[4]  	= 	$total_dis;
	$acumulate[5]  	= 	$total_ar;
	$acumulate[6]  	= 	$total_ar_pr;
	$acumulate[7]  	= 	$total_cogs;
	$acumulate[8]  	= 	$total_inventory;
	$acumulate[9]  	=		$total_diffp_debit;
	$acumulate[10]  =		$total_diffp_credit;
	$acumulate[11]	=		$total_refund_sale;

	### Original Movements Deposits/Credits
	$acumulate[12]  = 	$total_sales_deposits;
	$acumulate[13]  = 	$total_sales_refund;
	$acumulate[14]  = 	$total_codsale;
	$acumulate[15]  = 	$total_deposits_applied;
	$acumulate[16]  = 	$total_fpays_deposits;
	$acumulate[17]  = 	$total_sko_decrement;
	$acumulate[18]  = 	$total_cr_decrement;
	$acumulate[19]  = 	$total_ar_decrement;
	$acumulate[20]  = 	$total_deposits;
	$acumulate[21]  = 	$deposits;
	$acumulate[22]  = 	$total_predeposits;
	$acumulate[23]  = 	$predeposits;

	### Return Movements
	$acumulate[24]  =	$total_ar_return;
	$acumulate[25]  =	$total_inventory_return;
	$acumulate[26]  =	$total_tax_return;
	$acumulate[27]  =	$total_sale_return;
	$acumulate[28]  =	$total_service_return;
	$acumulate[29]  =	$total_fee_return;
	$acumulate[30]  =	$total_shp_return;
	$acumulate[31]  =	$total_dis_return;
	$acumulate[32]  =	$total_cogs_return;
	$acumulate[33]  =	$total_cref_return;

	### Refund Movements
	$acumulate[34]  =	$total_cref_refund;
	$acumulate[35]  =	$total_refund;

	### Replace Movements  
	$acumulate[36]  = 	$total_sale_exchange;
	$acumulate[37]  = 	$total_service_exchange;
	$acumulate[38]  = 	$total_tax_exchange;
	$acumulate[39]  = 	$total_shp_exchange;
	$acumulate[40]  = 	$total_dis_exchange;
	$acumulate[41]  = 	$total_ar_exchange;
	$acumulate[42]  = 	$total_cogs_exchange;
	$acumulate[43]  = 	$total_inventory_exchange;
	$acumulate[44]  =	$total_cref_exchange;
	$acumulate[45]  =	$total_deposits_exchange;


	return @acumulate;
}


sub fin_movements_report{
#-----------------------------------------
# Forms Involved: fin_repoper_day.html
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/21/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Build general and by type reports for sales given a date
# Parameters : acumulates, type of report
# Last Modified RB: 03/16/09  15:38:30 -- Se agrega rubro de paylog moved from para pagos traspasados de una preorden a otra.



  my ($type,@acumulate) = @_;

	### Original Movements
  my $total_sale 								= 	$acumulate[0];
	my $total_service 						= 	$acumulate[1];
	my $total_tax 								= 	$acumulate[2];
	my $total_shp 								= 	$acumulate[3];
	my $total_dis 								= 	$acumulate[4];
	my $total_ar 									= 	$acumulate[5];
	my $total_ar_pr 							= 	$acumulate[6];
	my $total_cogs 								= 	$acumulate[7];
	my $total_inventory 					= 	$acumulate[8];
	my $total_diffp_debit					=		$acumulate[9];
	my $total_diffp_credit				=		$acumulate[10];
	my $total_refund_sale					=		$acumulate[11];

	### Original Movements Deposits
  my $total_sales_deposits			=		$acumulate[12];
  my $total_sales_refund				=		$acumulate[13];
  my $total_codsale							=		$acumulate[14];
  my $total_deposits_applied		=		$acumulate[15];
  my $total_fpays_deposits			=		$acumulate[16];
	my $total_sko_decrement				=		$acumulate[17];
	my $total_cr_decrement				=		$acumulate[18];
	my $total_ar_decrement				=		$acumulate[19];
	my $total_deposits						=		$acumulate[20];
	my $deposits									=		$acumulate[21];
	my $total_predeposits					=		$acumulate[22];
	my $predeposits								=		$acumulate[23];	
  
  ### Return Movements
	my $total_ar_return						=		$acumulate[24];
	my $total_inventory_return		=		$acumulate[25];
	my $total_tax_return					=		$acumulate[26];
	my $total_sale_return					=		$acumulate[27];
	my $total_service_return			=		$acumulate[28];
	my $total_fee_return					=		$acumulate[29];
	my $total_shp_return					=		$acumulate[30];
	my $total_dis_return					=		$acumulate[31];
	my $total_cogs_return					=		$acumulate[32];
	my $total_cref_return					=		$acumulate[33];
  
  ### Refund Movements
	my $total_cref_refund					=		$acumulate[34];
	my $total_refund							=		$acumulate[35];

	### Replacements Movements
	my $total_sale_exchange 			= 	$acumulate[36];
	my $total_service_exchange 		= 	$acumulate[37];
	my $total_tax_exchange 				= 	$acumulate[38];
	my $total_shp_exchange 				= 	$acumulate[39];
	my $total_dis_exchange 				= 	$acumulate[40];
	my $total_ar_exchange 				= 	$acumulate[41];
	my $total_cogs_exchange 			= 	$acumulate[42];
	my $total_inventory_exchange 	= 	$acumulate[43];
	my $total_cref_exchange				=		$acumulate[44];
	my $total_deposits_exchange		=		$acumulate[45];	
  	
  	$page .= qq|
  							<div class="accordion-products">
  							<ul id="cbaccordion">|;
  							
  							## Sale
  							if($total_sale > 0 or $total_service > 0){
  							
  								$page .=qq|
													<li><h3>Sales Facts</h3>
					        					<div>&nbsp;
															<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
																<tr style="background-color:#CDCDC1;">
																	<td valign='top' align='left'><strong>Description</strong></td>
																	<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
																	<td valign='top' align='center' width="15%">&nbsp;</td>
																	<td valign='top' align='right'><strong>Credit</strong></td>
																<tr>
								  								<td nowrap valign="top" align="left" width="25%">Sales Products</td>
									  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sale) .qq|</td>
									  						</tr>
									  						<tr style="background-color:#EEEEE0;">
									  							<td nowrap valign="top" align="left">Sales Services</td>
									  							<td nowrap valign="top" align="right"></td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_service).qq|</td>
									  						</tr>	
									  						<tr>
									  							<td nowrap valign="top" align="left">Taxes</td>
									  							<td nowrap valign="top" align="right"></td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_tax).qq|</td>
									  						</tr>	
									  						<tr style="background-color:#EEEEE0;">
									  							<td nowrap valign="top" align="left">Shipping</td>
									  							<td nowrap valign="top" align="right">&nbsp;</td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_shp).qq|</td>
									  						</tr>|;

									  						if ($total_diffp_credit > 0){
									  							$page .=qq|
									  													<tr>
																  							<td nowrap valign="top" align="left">Difference In Payments</td>
																  							<td nowrap valign="top" align="right">&nbsp;</td>
																  							<td valign='top' align='right'>&nbsp;</td>
																  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_diffp_credit).qq|</td>
																  						</tr>|;

									  						}

									  						## Customer Refunds
									  						if ($total_refund_sale > 0){
									  							$page .=qq|
									  													<tr style="background-color:#EEEEE0;">
																  							<td nowrap valign="top" align="left">Customer Refund</td>
																  							<td nowrap valign="top" align="right">&nbsp;</td>
																  							<td valign='top' align='right'>&nbsp;</td>
																  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_refund_sale).qq|</td>
																  						</tr>|;

									  						}

									  						## Sale Refunds
									  						if ($total_sales_refund > 0){
									  							$page .=qq|
									  													<tr>
																  							<td nowrap valign="top" align="left">BofA Customer Refund</td>
																  							<td nowrap valign="top" align="right">&nbsp;</td>
																  							<td valign='top' align='right'>&nbsp;</td>
																  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sales_refund).qq|</td>
																  						</tr>|;

									  						}


									  						## Discounts
									  						if ($total_dis > 0){
															  	$page.=qq|			
															  						<tr>
															  							<td nowrap valign="top" align="left">Discounts</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_dis).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;
															  }

											$page.=qq|			  
									  						<tr style="background-color:#EEEEE0;">
									  							<td nowrap valign="top" align="left">Total BofA</td>
									  							<td nowrap valign="top" align="right">|.&format_price($total_sales_deposits).qq|</td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right">&nbsp;</td>
									  						</tr>|;


									  						## COD Sale Deposits
									  						if($total_codsale > 0){
									  							$page.=qq|
																						<tr>
															  							<td nowrap valign="top" align="left">Cash COD</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_codsale).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;

															  }

									  						## Customer Deposits Applied
									  						if($total_deposits_applied > 0){
									  							$page.=qq|
																						<tr style="background-color:#EEEEE0;">
															  							<td nowrap valign="top" align="left">Customer Deposits</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_deposits_applied).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;

															  }

									  						## A/R
									  						if($total_ar > 0){			

									  							$page.=qq|
															  						<tr>
															  							<td nowrap valign="top" align="left">A/R</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_ar).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;

															  }

															  ## A/R Puerto Rico
															  if($total_ar_pr > 0){			

									  							$page.=qq|
															  						<tr>
															  							<td nowrap valign="top" align="left">A/R Puerto Rico</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_ar_pr).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;

															  }

															  if($total_diffp_debit > 0){			

									  							$page.=qq|
															  						<tr style="background-color:#EEEEE0;">
															  							<td nowrap valign="top" align="left">Difference In Payments</td>
															  							<td nowrap valign="top" align="right">|.&format_price($total_diffp_debit ).qq|</td>
															  							<td valign='top' align='right'>&nbsp;</td>
															  							<td nowrap valign="top" align="right">&nbsp;</td>
															  						</tr>|;

															  }

											$page.=qq|	  
									  						<tr style="background-color:#CDCDC1;">
									  							<td nowrap valign="top" align="left"><strong>Total</strong</td>
									  							<td nowrap valign="top" align="right"><strong>|.&format_price($total_dis+$total_codsale+$total_deposits_applied+$total_sales_deposits+$total_claim_deposits+$total_predeposits_sales+$total_diffp_debit+$total_ar+$total_ar_pr).qq|</strong></td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_sale+$total_sale_claims+$total_service+$total_tax+$total_shp+$total_diffp_credit+$total_refund_sale+$total_sales_refund).qq|</strong></td>
									  						</tr>
									  						<tr>
									  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
									  						</tr>
									  						<tr>
									  							<td nowrap valign="top" align="left">Inventory</td>
									  							<td nowrap valign="top" align="right">&nbsp;</td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_inventory).qq|</td>
									  							</tr>
									  						<tr>
									  							<td nowrap valign="top" align="left">COGS</td>
									  							<td nowrap valign="top" align="right">|.&format_price($total_cogs).qq|</td>
									  							<td valign='top' align='right'>&nbsp;</td>
									  							<td nowrap valign="top" align="right">&nbsp;</td>
									  						</tr>
					  									</table>
					  									&nbsp;
						  							</div>
													</li>|;
								}

								## Sales Deposits	
								if($total_sales_deposits){

									$page.=qq|		
														<li><h3>Sale Deposits</h3>
						        					<div>&nbsp;
								  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">|;


							  			$i=0;
							  			while (my ($type, $amount) = each(typeOfPaySales) ){
							  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
							  				($i%2 eq 1) and ($stlyetd = '');
					        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
					        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
					        			$i++;
					        		}

					        		$page .=qq|	
						        							<tr style="background-color:#CDCDC1;">
						        								<td valign='top' align='right'><strong>Total</strong></td> 
						        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_sales_deposits) .qq|</strong></td>
						        							</tr>
						        						</table>
						        						&nbsp;
						        					</div>
						        				</li>|;
						    }



						    ## Sales Refund(BofA Customer Refund)	
								if($total_sales_refund){

									$page.=qq|		
														<li><h3>BofA Customer Refund</h3>
						        					<div>&nbsp;
								  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">|;


							  			$i=0;
							  			while (my ($type, $amount) = each(typeOfPaySalesC) ){
							  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
							  				($i%2 eq 1) and ($stlyetd = '');
					        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td> 
					        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td></tr>|;
					        			$i++;
					        		}

					        		$page .=qq|	
						        							<tr style="background-color:#CDCDC1;">
						        								<td valign='top' align='right'><strong>Total</strong></td> 
						        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_sales_refund) .qq|</strong></td>
						        							</tr>
						        						</table>
						        						&nbsp;
						        					</div>
						        				</li>|;
						    }



	        ## Flex Pays				
	        if($total_fpays_deposits > 0){		

	        	$page .=qq|			
	        					<li><h3>Consecutive Deposits (Flexpays)</h3>
	        					<div>&nbsp;
			  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
			  								<tr style="background-color:#CDCDC1;">
													<td valign='top' align='left'><strong>Description</strong></td>
													<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
													<td valign='top' align='center' width="15%">&nbsp;</td>
													<td valign='top' align='right'><strong>Credit</strong></td>
											<tr>|;

				if($total_ar_decrement > 0) {
				
					$page .=qq|						
												<tr>
				  								<td nowrap valign="top" align="right" width="25%">Account Receivable</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_ar_decrement) .qq|</td>
					  						</tr>|;
        		}

        		if($total_sko_decrement > 0) {
				
					$page .=qq|						
											<tr>
				  								<td nowrap valign="top" align="right" width="25%">On Collection Receivable</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sko_decrement) .qq|</td>
					  						</tr>|;
        		}


				if($total_cr_decrement > 0) {
				
					$page .=qq|						
											<tr>
				  								<td nowrap valign="top" align="right" width="25%">Customer Refund</td>
					  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
					  							<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_cr_decrement) .qq|</td>
					  						</tr>|;
        		}        		

        		
        		
        	
		  			$i=0;
		  			while ( my ($type, $amount) = each(%typeOfPayFpDpt) ){
		  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		  				($i%2 eq 1) and ($stlyetd = '');
        			$page .= qq|<tr><td valign='top' align='right' $stlyetd>$type</td>
        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td>
        									<td colspan="2" $stlyetd>&nbsp;</td></tr>|;
        			$i++;
        		}
        		
        		$page .=qq|
	        							<tr style="background-color:#CDCDC1;">
	        								<td valign='top' align='left'><strong>Total</strong></td> 
	        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_fpays_deposits) .qq|</strong></td>
	        								<td valign='top' align='right'>&nbsp;</td>
					  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_ar_decrement) .qq|</strong></td>
	        							</tr>	
	        						</table>
	        						&nbsp;
	        					</div>
	        				</li>|;
	 					}


		 				## Customer Deposits
		 				if($total_deposits > 0 or $total_predeposits > 0){



	 						$page .= qq|
				        				<li><h3>Customer Deposits</h3>
				        					<div>&nbsp;
						  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
						  								|;


						  ## From Orders	
		 					if($total_deposits > 0){

						  	$page .= qq|								
				  									<tr style="background-color:#519241; color:#F0FFF0;">
				        							<td valign='top' align='center' colspan="4"><strong>From  Orders</strong></td> 
				        						</tr>
					  								<tr style="background-color:#CDCDC1;">
															<td valign='top' align='left'><strong>Description</strong></td>
															<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
															<td valign='top' align='center' width="15%">&nbsp;</td>
															<td valign='top' align='right'><strong>Credit</strong></td>
														<tr>
														<tr>
						  								<td nowrap valign="top" align="left" width="25%">Customer Deposit</td>
							  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
							  							<td valign='top' align='right'>&nbsp;</td>
							  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($deposits) .qq|</td>
							  						</tr>|;


				  			$i=0;
				  			while ( my ($type, $amount) = each(%typeOfPayDpt) ){
				  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
				  				($i%2 eq 1) and ($stlyetd = '');
		        			$page .= qq|<tr><td valign='top' align='left' $stlyetd>$type</td>
		        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td>
		        									<td colspan="2" $stlyetd>&nbsp;</td></tr>|;
		        			$i++;
		        		}

		        		$page .=qq|
			        							<tr style="background-color:#CDCDC1;">
			        								<td valign='top' align='left'><strong>Total</strong></td> 
			        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_deposits) .qq|</strong></td>
			        								<td valign='top' align='right'>&nbsp;</td>
							  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($deposits) .qq|</strong></td>
			        							</tr>
			        							<tr>
				        							<td colspan="4">&nbsp;</td> 
				        						</tr>|;
			        }						


			        ## From PreOrders	
		 					if($total_predeposits > 0){

			        	$page .= qq|					
			        						<tr style="background-color:#519241; color:#F0FFF0;">
			        							<td valign='top' align='center' colspan="4"><strong>From  PreOrders</strong></td> 
			        						</tr>	
			        						<tr style="background-color:#CDCDC1;">
														<td valign='top' align='left'><strong>Description</strong></td>
														<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
														<td valign='top' align='center' width="15%">&nbsp;</td>
														<td valign='top' align='right'><strong>Credit</strong></td>
													<tr>
													<tr>
					  								<td nowrap valign="top" align="left" width="25%">Customer Deposit</td>
						  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($predeposits) .qq|</td>
						  						</tr>|;


		        		## Customer Deposits PreOrders
				  			$i=0;
				  			while ( my ($type, $amount) = each(%typeOfPayPDptP) ){
				  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
				  				($i%2 eq 1) and ($stlyetd = '');
		        			$page .= qq|<tr><td valign='top' align='left' $stlyetd>$type</td>
		        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq| </td>
		        									<td colspan="2" $stlyetd>&nbsp;</td></tr>|;
		        			$i++;
		        		}

	        		$page .=qq|
		        							<tr style="background-color:#CDCDC1;">
		        								<td valign='top' align='left'><strong>Total</strong></td> 
		        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_predeposits) .qq|</strong></td>
		        								<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($predeposits) .qq|</strong></td>
		        							</tr>
		        							<tr>
			        							<td colspan="4">&nbsp;</td> 
			        						</tr>|;
			        }

			        $page .=qq|							
		        						</table>
		        						&nbsp;
		        					</div>
		        				</li>|;
		        }

		        ## Returns , Refunds  & Replacements
		        if($total_sale_return > 0 or $total_sale_exchange > 0 or $total_cref_refund > 0 or $total_refund > 0 or $total_cref_exchange > 0){

		        	$page .=qq|
		        							<li><h3>Returns and Replacements</h3>
				        					<div>&nbsp;
						  							<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
						  								|;


						  ## Returns	
		 					if($total_sale_return > 0){

						  	$page .= qq|								
				  									<tr style="background-color:#519241; color:#F0FFF0;">
				        							<td valign='top' align='center' colspan="4"><strong>Returns</strong></td> 
				        						</tr>
					  								<tr style="background-color:#CDCDC1;">
															<td valign='top' align='left'><strong>Description</strong></td>
															<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
															<td valign='top' align='center' width="15%">&nbsp;</td>
															<td valign='top' align='right'><strong>Credit</strong></td>
														<tr>|;

														### Sales
														if($total_sale_return > 0){

															$page.=qq|
																				<tr>
												  								<td nowrap valign="top" align="left" width="25%">Products</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_sale_return) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;
									  				}

									  				### Services
									  				if($total_service_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Services</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_service_return) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;
													  }


													  ### Shipping
									  				if($total_shp_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Shipping</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_shp_return) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;
													  }


													  ### Tax
									  				if($total_tax_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Tax</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_tax_return) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;	
		        								}

		        								### Discount
									  				if($total_dis_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Discounts</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_dis_return) .qq|</td>
													  						</tr>|;	
		        								}

		        								### Return Fees
									  				if($total_fee_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Restocking & Returning Fees</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_fee_return) .qq|</td>
													  						</tr>|;	
		        								}

		        								### A/R Return
									  				if($total_ar_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Account Receivable</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_ar_return) .qq|</td>
													  						</tr>|;	
		        								}

		        								### Customer Refund
									  				if($total_cref_return > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Customer Refund</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_cref_return) .qq|</td>
													  						</tr>|;	
		        								}


		        		$page .=qq|
		        							<tr style="background-color:#CDCDC1;">
		        								<td valign='top' align='left'><strong>Total</strong></td> 
		        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_sale_return+$total_service_return+$total_shp_return+$total_tax_return) .qq|</strong></td>
		        								<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_ar_return+$total_dis_return+$total_fee_return+$total_cref_return) .qq|</strong></td>
	        								</tr>	
		        							<tr>
						  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
						  						</tr>
						  						<tr>
						  							<td nowrap valign="top" align="left">Inventory</td>
						  							<td nowrap valign="top" align="right">|.&format_price($total_inventory_return).qq|</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
						  							</tr>
						  						<tr>
						  							<td nowrap valign="top" align="left">COGS</td>
						  							<td nowrap valign="top" align="right">&nbsp;</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_cogs_return).qq|</td>
						  						</tr>
						  						<tr>
						  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
						  						</tr>|;						

		        	}


		        	## Refunds	
		 					if($total_cref_refund > 0 or $total_refund){

						  	$page .= qq|								
				  									<tr style="background-color:#519241; color:#F0FFF0;">
				        							<td valign='top' align='center' colspan="4"><strong>Refunds</strong></td> 
				        						</tr>
					  								<tr style="background-color:#CDCDC1;">
															<td valign='top' align='left'><strong>Description</strong></td>
															<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
															<td valign='top' align='center' width="15%">&nbsp;</td>
															<td valign='top' align='right'><strong>Credit</strong></td>
														<tr>|;

														### Customer Refund
														if($total_cref_refund > 0){

															$page.=qq|
																				<tr>
												  								<td nowrap valign="top" align="left" width="25%">Customer Refund</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_cref_refund) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;
									  				}

									  				### Refunds
									  				if($total_refund > 0){
									  					$i=0;
											  			while ( my ($type, $amount) = each(%typeOfPayRef) ){
											  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
											  				($i%2 eq 1) and ($stlyetd = '');
									        			$page .= qq|<tr><td valign='top' align='left' $stlyetd>$type</td>
									        									<td nowrap valign='top' align='right' $stlyetd>&nbsp;</td>
									        									<td $stlyetd>&nbsp;</td>
									        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq|</td>
									        									</tr>|;
									        			$i++;
									        		}
		        								}
		        		$page .=qq|
		        							<tr style="background-color:#CDCDC1;">
		        								<td valign='top' align='left'><strong>Total</strong></td> 
		        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_cref_refund) .qq|</strong></td>
		        								<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_refund) .qq|</strong></td>
	        								</tr>
	        								<tr>
						  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
						  						</tr>|;						
		        	}

		        	## Replacements	
		 					if($total_sale_exchange > 0){

						  	$page .= qq|								
				  									<tr style="background-color:#519241; color:#F0FFF0;">
				        							<td valign='top' align='center' colspan="4"><strong>Replacements</strong></td> 
				        						</tr>
					  								<tr style="background-color:#CDCDC1;">
															<td valign='top' align='left'><strong>Description</strong></td>
															<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
															<td valign='top' align='center' width="15%">&nbsp;</td>
															<td valign='top' align='right'><strong>Credit</strong></td>
														<tr>|;

														### Sales
														if($total_sale_exchange > 0){

															$page.=qq|
																				<tr>
												  								<td nowrap valign="top" align="left" width="25%">Products</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_sale_exchange) .qq|</td>
													  						</tr>|;
									  				}

									  				### Services
									  				if($total_service_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Services</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_service_exchange) .qq|</td>
													  						</tr>|;
													  }


													  ### Shipping
									  				if($total_shp_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Shipping</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_shp_exchange) .qq|</td>
													  						</tr>|;
													  }


													  ### Tax
									  				if($total_tax_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Tax</td>
													  							<td nowrap valign="top" align="right" width="50%">&nbsp;</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_tax_exchange) .qq|</td>
													  						</tr>|;	
		        								}

		        								### Discount
									  				if($total_dis_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Discount</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_dis_exchange) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;	
		        								}


		        								### A/R Exchange
									  				if($total_ar_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Account Receivable</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_ar_exchange).qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;	
		        								}

		        								### Customer Refund
									  				if($total_cref_exchange > 0){

									  					$page.=qq|
													  						<tr>
												  								<td nowrap valign="top" align="left" width="25%">Customer Refund</td>
													  							<td nowrap valign="top" align="right" width="50%">|.&format_price($total_cref_exchange) .qq|</td>
													  							<td valign='top' align='right'>&nbsp;</td>
													  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
													  						</tr>|;	
		        								}

		        								### Exchange Deposits
									  				if($total_deposits_exchange > 0){
									  					$i=0;
											  			while ( my ($type, $amount) = each(%typeOfPayEx) ){
											  				($i%2 eq 0) and ($stlyetd = 'style="background-color:#EEEEE0;"');
											  				($i%2 eq 1) and ($stlyetd = '');
									        			$page .= qq|<tr><td valign='top' align='left' $stlyetd>$type</td>
									        									<td nowrap valign='top' align='right' $stlyetd>|.&format_price($amount) .qq|</td>
									        									<td $stlyetd>&nbsp;</td>
									        									<td nowrap valign='top' align='right' $stlyetd>&nbsp;</td>
									        									</tr>|;
									        			$i++;
									        		}
		        								}


		        		$page .=qq|
		        							<tr style="background-color:#CDCDC1;">
		        								<td valign='top' align='left'><strong>Total</strong></td> 
		        								<td nowrap valign='top' align='right'><strong>|.&format_price($total_ar_exchange+$total_dis_exchange+$total_cref_exchange+$total_deposits_exchange) .qq|</strong></td>
		        								<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red"><strong>|.&format_price($total_sale_exchange+$total_service_exchange+$total_shp_exchange+$total_tax_exchange).qq|</strong></td>
	        								</tr>	
		        							<tr>
						  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
						  						</tr>
						  						<tr>
						  							<td nowrap valign="top" align="left">Inventory</td>
						  							<td nowrap valign="top" align="right">&nbsp;</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">|.&format_price($total_inventory_exchange).qq|</td>
						  							</tr>
						  						<tr>
						  							<td nowrap valign="top" align="left">COGS</td>
						  							<td nowrap valign="top" align="right">|.&format_price($total_cogs_exchange).qq|</td>
						  							<td valign='top' align='right'>&nbsp;</td>
						  							<td nowrap valign="top" align="right" style="color:red">&nbsp;</td>
						  						</tr>
						  						<tr>
						  							<td nowrap valign="top" align="center" colspan="3">&nbsp;</td>
						  						</tr>|;						

		        	}


		        	$page .=qq|							
		        						</table>
		        						&nbsp;
		        					</div>
		        				</li>|;							


		        }


	        $page .=qq|				
		        			</ul>
		        			</div>|;

    return $page;

}


sub fin_movements_error{
#-----------------------------------------
# Created on: 07/20/09  15:20:39 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

		######
		###### Orders
		######


		####### Difference Debits vs Credits
		$va{'searchresults'} .=&fin_showdiff_movements($in{'reportdate'},$in{'reportdateto'});
		####### Movements in Zero.
		$va{'searchresults'} .=&fin_zero_movements($in{'reportdate'},$in{'reportdateto'});




		print "Content-type: text/html\n\n";
		print &build_page('fin_movements_error.html');	
}


sub fin_movements_summary{
#-----------------------------------------
# Created on: 07/20/09  15:20:39 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	




	my ($sth) = &Do_SQL("SELECT ID_accounting, Name, SUM( IF( Credebit = 'Debit', Amount, 0 ) ) AS Debits, SUM( IF( Credebit = 'Credit', Amount, 0 ) ) AS Credits
FROM `sl_movements`
INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_movements.ID_accounts
WHERE EffDate BETWEEN '$in{'reportdate'}' AND '$in{'reportdateto'}'
GROUP BY sl_movements.ID_accounts
ORDER BY sl_movements.ID_accounts");

	while(my($id_account,$name,$debit,$credit) = $sth->fetchrow()){
		($i%2 eq 1) and ($stlyetd = 'style="background-color:#EEEEE0;"');
		($i%2 eq 0) and ($stlyetd = '');

		$va{'searchresults'} .= qq|
									<tr>
										<td valign='top' align='left' $stlyetd>$id_account</a></td>
										<td $stlyetd>$name</td>
      							<td nowrap valign='top' align='right' $stlyetd>|.&format_price($debit) .qq| </td>
      							<td nowrap valign='top' align='right' $stlyetd>|.&format_price($credit) .qq| </td>
      						</tr>|;
    $va{'tdebits'} 	+= $debit;
    $va{'tcredits'} += $credit;
		$i++;
	}

		$va{'tdebits'} 	= &format_price($va{'tdebits'});
    $va{'tcredits'} = &format_price($va{'tcredits'});										
		print "Content-type: text/html\n\n";

		if($in{'print'}){
			print &build_page('fin_movements_summary_print.html');
		}else{
			print &build_page('fin_movements_summary.html');	
		}
}


sub repoper_cogs_orders{
#----------------------------------------------------------
# Forms Involved:
# Created on: 2/15/2008 9:43AM
# Last Modified on: 5/09/2008
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the cogs for an order given a date and order specifics
# Parameters : [date:the date to report] [idorder: The id_order]  
  
   my ($date,$idorder) = @_;
   my $cogs,$net,$query;
   
   $cogs=0;
   $net=0;
   $query= " AND Date <= '$date' ";
   $str = "";
   $diff = 0;

   my ($sth1) = &Do_SQL("SELECT ID_products,Status,SalePrice,Cost,IF(ShpDate IS NOT NULL AND ShpDate != '0000-00-00' AND ShpDate <= '$date',1,0)AS ShpDate 
   											FROM sl_orders_products WHERE ID_orders = $idorder $query AND Status IN('Active','Returned','Exchange')
   											ORDER BY ID_products,Date");
   
   while ($rec1 = $sth1->fetchrow_hashref){
   			$prod_cost = 0;
   			if (substr($rec1->{'ID_products'},0,1) != 6){
       		if($rec1->{'Cost'} eq '' or $rec1->{'Cost'} <= 0){
          		#####Searching from sl_po_items
          		my ($sth2) = &Do_SQL("SELECT AVG(Price) FROM sl_purchaseorders_items WHERE ID_products = $rec1->{'ID_products'} ");
       				$prod_cost=$sth2->fetchrow;
       				if (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0){
           			#####Searching from sl_skus_cost
           			my ($sth3) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost WHERE ID_products = RIGHT('$rec1->{'ID_products'}',6)");
           			$prod_cost=$sth3->fetchrow;
           			if (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0){ 
            			#####Searching from sl_products.SLTV_NetCost
              		$prod_cost = &load_name('sl_products','ID_products',substr($rec1->{'ID_products'},3,6),'SLTV_NetCost');
            		}
          		}
       		}else{
          		 #### Take the cost from sl_orders_products
           		$prod_cost  = $rec1->{'Cost'};
       		}
       	}
       	#
				#($idorder == 68813) and (&cgierr("ID:$idorder - ID:$rec1->{'ID_products'} Diff:$diff - ShpDate :$rec1->{'ShpDate'}"));
        ($rec1->{'Status'} ne 'Active') and ($cogs -= $prod_cost) and ($net -= $rec1->{'SalePrice'});
        ($rec1->{'Status'} eq 'Active') and ($cogs += $prod_cost) and ($net += $rec1->{'SalePrice'});
   }
  	#($idorder == 68813) and (&cgierr("ID:$idorder - ID:$rec1->{'ID_products'} Net:$net  y $cogs"));
  
   return "$net:$cogs";
}

sub repoper_cogs_products{
#-----------------------------------------
# Forms Involved:
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/22/2008
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the cogs for a product given a product and order specifics
# Parameters : [idorder: The id_order] [idproduct: The id_product]
   
    my ($idorder,$idproduct) = @_;
    my $cogs=0;
   
    if($cfg{'close_batch_type'} eq ''){
        my ($sth1) = &Do_SQL("SELECT Cost FROM sl_orders_products WHERE ID_orders = $idorder AND RIGHT(ID_products,6) = $idproduct
                              AND Status IN('Exchange', 'Returned') ORDER BY ID_products,Date ");
   
        return abs($sth1->fetchrow);
    }else{
        my ($prod_cost);
        my ($sth2) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost
                             WHERE $idproduct = RIGHT(sl_skus_cost.ID_products,6)");
        $prod_cost=$sth2->fetchrow;
        if (!$prod_cost){
            $prod_cost = &load_name('sl_products','ID_products',$idproduct,'SLTV_NetCost');
        }
    }   
}

sub repoper_cogs_product{

		my ($idproduct) = @_;

		#####Searching from sl_po_items
    my ($sth2) = &Do_SQL("SELECT AVG(Price) FROM sl_purchaseorders_items WHERE ID_products = '$idproduct'");
    $prod_cost=$sth2->fetchrow;
    if (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0){
    		#####Searching from sl_skus_cost
        my ($sth3) = &Do_SQL("SELECT AVG(Cost) FROM sl_skus_cost WHERE ID_products = RIGHT('$idproduct',6)");
        $prod_cost=$sth3->fetchrow;
        if (!$prod_cost or $prod_cost eq '' or $prod_cost <= 0){ 
        		#####Searching from sl_products.SLTV_NetCost
        		(length($idproduct) > 6) and ($idproduct = substr($idproduct,3));
         		$prod_cost = &load_name('sl_products','ID_products',$idproduct,'SLTV_NetCost');
        }
    }
    
    #($idproduct eq '100469403') and (&cgierr("$prod_cost"));
    
    return $prod_cost;	
}	


sub repoper_flexypay{
#-----------------------------------------
# Forms Involved: 
# Created on: 2/12/2008 9:43AM
# Last Modified on: 2/21/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : The payments made for an order before the given date
# Parameters : [idorder: The id_order] [date: The date to search for]

	my ($idorders,$date) = @_;
	#($idorders eq '66195') and (&cgierr("SELECT COUNT(CapDate) FROM sl_orders_payments WHERE ID_orders = $idorders AND CapDate < '$date' AND Status != 'Cancelled'"));
	my ($sth) = &Do_SQL("SELECT COUNT(CapDate) FROM sl_orders_payments WHERE ID_orders = $idorders AND CapDate < '$date' AND Capdate != '0000-00-00' AND Status != 'Cancelled' ");
	return $sth->fetchrow;
}

sub repoper_postdatedorder{
#-----------------------------------------
# Forms Involved: 
# Created on: 06/05/2008 9:43AM
# Last Modified on: 6/05/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Tells if a previous payment was a postdated fee
# Parameters : [idorder: The id_order] [date: The date to search for]

	my ($idorders,$date) = @_;
	#($idorders eq '66244') and (&cgierr("SELECT IF(PmtField8 = 'Post-Dated Fee',1,0) FROM sl_orders_payments WHERE ID_orders = $idorders AND CapDate <= '$date' AND Capdate != '0000-00-00' AND Status != 'Cancelled'"));
	my ($sth) = &Do_SQL("SELECT IF(PmtField8 = 'Post-Dated Fee',1,0) FROM sl_orders_payments WHERE ID_orders = $idorders AND CapDate <= '$date' AND Capdate != '0000-00-00' AND Status != 'Cancelled' ");
	return $sth->fetchrow;
}

sub repoper_fpays{
#-----------------------------------------
# Forms Involved: 
# Created on: 06/05/2008 9:43AM
# Last Modified on: 6/05/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the total number of payments for the order
# Parameters : [idorder: The id_order]

	my ($idorders) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = $idorders");
	return $sth->fetchrow;
}

sub repoper_amountpaid{
#-----------------------------------------
# Forms Involved: 
# Created on: 06/05/2008 9:43AM
# Last Modified on: 6/05/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the corresponding amount paid to items/services
# Parameters : [idorder: The id_order]

	my ($datef,$idorders,$dpay,$amount,$tax,$shp,$npay,$pd) = @_;
	my ($str,$i,$j,@itemop1,@itemop2,@ids,@possibilities,@position,$cicle,$icicle,$scicle,$np,$tpossibilities,$flag,@fp);
	my ($query);
	$query = "";

	#($idorders ==66510) and (&cgierr("orden:$idorders , postdated:$pd, npago:$npay,amount:$amount"));
	#($cfg{'salesreport'} eq 'capdate') and ($query= " AND Date <= '$date' ");
	#($cfg{'salesreport'} eq 'shpdate') and ($query= " AND PostedDate = '$date' ");
	my ($sth) = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6) AS idp, SalePrice
											FROM sl_orders_products WHERE ID_orders = $idorders 
											AND sl_orders_products.Status = 'Active'
											AND Date <= '$datef'");


	($dpay==15) and ($dpay=2);
	($dpay==30) and ($dpay=1);
	$np=0;
	$fp[0]=1;
	$totp = 0;
	$flag=0;
	$i=0;
	$j=0;
	$str="";	

	#### Items into array
	$x=1;									
	while($recp = $sth->fetchrow_hashref){
		$va{'item_'.$x.'_op1'} = $recp->{'SalePrice'};
		$va{'ids_'.$x} = $recp->{'idp'};


		if(substr($recp->{'idp'},0,1) == 0){
			$j++;
		}else{
			$i++;
			$fp[0] = &load_name("sl_products","ID_products",$recp->{'idp'},"Flexipago");
		}

		($fp[0] > 24) and ($fp[0] = 24);
		($fp[0] == 0) and ($fp[0] = 1);
		#($idorders == 66510) and (&cgierr("$fp[0] y $x y $i y $j"));

		$va{'item_'.$x.'_op2'} = $recp->{'SalePrice'}/$fp[0];
		$totp += $recp->{'SalePrice'};

		$str .= 'ID:'.$recp->{'idp'}.'<br>Op1:'.$va{'item_'.$x.'_op1'}.'<br>Op2:'.$va{'item_'.$x.'_op2'}.'<br><br>';
		$x++;
	}

	#($idorders == 71631) and (&cgierr("$str"));
	#############################
	#############################
	## ORDER WITHOUT SERVICES
	#############################
	#############################
	($j == 0) and (return "$amount:0.00");
	############################

	## The total of possibilities
	$tpossibilities = 2**($i+$j);

	#($idorders eq '66567') and (cgierr("i:$i, j:$j, possibilities:$tpossibilities, orden:$idorders , postdated:$pd, npago:$npay\namount:$amount"));


	# Checking all possibilities
	FINAL: for $cicle(1..2){# Deberia ser hasta $tpossibilities

			# 1 = one payment
			# 2 = flexpays
			$randomposition = "";
			$sumitems = 0;
			$sumser = 0;
			if($cicle == 1){
				for (1..$i+$j){
					$randomposition .= "1";
				}
				#$randomposition = substr($randomposition,0,(($i+$j)*2) - 1);
			}elsif($cicle == 2){
				for (1..$i+$j){
					$randomposition .= "2";
				}
				#$randomposition = substr($randomposition,0,(($i+$j)*2) - 1);
			}else{
				#$vueltas = 1;
				RND: while(1){
					$randomposition = "";
					for (1..$i+$j){
							$rndnumber = int(rand(2)) + 1;
							$randomposition .=  "$rndnumber";
					}
					#$randomposition = substr($randomposition,0,$i+$j);	
					last RND if(!grep(/$randomposition/, @possibilities));
					#$vueltas++;			
				}
			}


			## Record the possibilitie used
			push(@possibilities, $randomposition); 	

			## Spliting the order
			@position = split(//,$randomposition);

			## SUM ITEMS AND SERVICES WITH RANDOM POSITION
			for $icicle(1..$i+$j){
				##SUM ITEMS
				if(substr($va{'ids_'.$icicle},0,1) != 0){
					 $sumitems += $va{'item_'.$icicle.'_op'.$position[$icicle-1]};
				## SUM SERVICES
				}else{
					 $sumser   += $va{'item_'.$icicle.'_op'.$position[$icicle-1]};
				}
			}

			##
			#($idorders == 66510) and (&cgierr("$sumitems + $sumser + $tax + $shp - $amount"));
			$diff  = abs($sumitems + $sumser + $tax + $shp - $amount);
			$diff2 = abs($sumitems + $sumser - $amount);



			if(($npay == 0 or ($npay == 1 and $pd = 1)) and $diff  < 1){
				 $sumitems = $sumitems+$tax+$shp;
				 $flag=1;
			}elsif(($npay  > 1 or ($npay == 1 and $pd = 0)) and $diff2 < 1){
				$flag=1;
			}

			last FINAL if($flag == 1);

#			($cicle > 2 and $flag == 1) and (&cgierr("
#							order:$idorders\n
#							dpago:$dpay\n
#							pd:$pd\n
#							fp:$fp\n
#							amount:$amount\n
#							items:$i\n
#							servis:$j\n
#							possi:$tpossibilities\n
#							cicle:$cicle\n
#							option:$randomposition\n
#							str:$str\n
#							sumi:$sumitems\n
#							sums:$sumser\n
#							opt2 = $opt2\n
#							ids0:$va{'ids_1'}  - price:$va{'item_1_op2'}\n
#							ids1:$va{'ids_2'}  - price:$va{'item_2_op1'}\n
#							dif1:$diff\n
#							dif2:$diff2"));
	}

	($flag==1) and (return "$sumitems:$sumser");
	($flag==0) and (return "$amount:0.00");
}

sub repoper_split_amount{
#-----------------------------------------
# Forms Involved: 
# Created on: 06/05/2008 9:43AM
# Last Modified on: 6/05/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the corresponding amount paid to items/services
# Parameters : [idorder: The id_order]

	my ($datef,$idorders,$amount,$ot,$os,$od,$dpay,$sale) = @_;
	my ($str,$i,$j,@itemop1,@itemop2,@ids,@possibilities,@position,$cicle,$icicle,$scicle,$np,$tpossibilities,$flag,@fp);
	my ($query);
	$query = "AND Date <= '$datef' ";


	($sale == 1) and ($query = "AND PostedDate = '$datef' ");
	my ($sth) = &Do_SQL("SELECT RIGHT(sl_orders_products.ID_products,6) AS idp, SalePrice
											FROM sl_orders_products WHERE ID_orders = $idorders 
											AND sl_orders_products.Status = 'Active'
											$query ");


	($dpay==15) and ($dpay=2);
	($dpay==30) and ($dpay=1);
	$np=0;
	$fp[0]=1;
	$totp = 0;
	$flag=0;
	$i=0;
	$j=0;
	$str="";	


	#### Items into array
	$x=1;									
	while($recp = $sth->fetchrow_hashref){
		$va{'item_'.$x.'_op1'} = $recp->{'SalePrice'};
		$va{'ids_'.$x} = $recp->{'idp'};


		if(substr($recp->{'idp'},0,1) == 0){
			$j++;
		}else{
			$i++;
			$fp[0] = &load_name("sl_products","ID_products",$recp->{'idp'},"Flexipago");
		}

		($fp[0] > 24) and ($fp[0] = 24);
		($fp[0] == 0) and ($fp[0] = 1);

		$va{'item_'.$x.'_op2'} = $recp->{'SalePrice'}/$fp[0];
		$totp += $recp->{'SalePrice'};

		$str .= 'ID:'.$recp->{'idp'}.'<br>Op1:'.$va{'item_'.$x.'_op1'}.'<br>Op2:'.$va{'item_'.$x.'_op2'}.'<br><br>';
		$x++;
	}

	#############################
	#############################
	## ORDER WITHOUT SERVICES
	#############################
	#############################
	($j == 0) and (return "$amount:0.00");
	############################

	## The total of possibilities
	$tpossibilities = 2**($i+$j);

	# Checking all possibilities
	FINAL: for $cicle(1..$tpossibilities){# Deberia ser hasta $tpossibilities

			# 1 = one payment
			# 2 = flexpays
			$randomposition = "";
			$sumitems = 0;
			$sumser = 0;
			if($cicle == 1){
				for (1..$i+$j){
					$randomposition .= "1";
				}
			}elsif($cicle == 2){
				for (1..$i+$j){
					$randomposition .= "2";
				}
			}else{
				RND: while(1){
					$randomposition = "";
					for (1..$i+$j){
							$rndnumber = int(rand(2)) + 1;
							$randomposition .=  "$rndnumber";
					}
					last RND if(!grep(/$randomposition/, @possibilities));	
				}
			}

			## Record the possibilitie used
			push(@possibilities, $randomposition);

			## Spliting the order
			@position = split(//,$randomposition);

			## SUM ITEMS AND SERVICES WITH RANDOM POSITION
			for $icicle(1..$i+$j){
				##SUM ITEMS
				if(substr($va{'ids_'.$icicle},0,1) != 0){
					 $sumitems += $va{'item_'.$icicle.'_op'.$position[$icicle-1]};
				## SUM SERVICES
				}else{
					 $sumser   += $va{'item_'.$icicle.'_op'.$position[$icicle-1]};
				}
			}

			#$ot = $sumitems * $ot;
			($cicle == 1) and ($titems = $sumitems) and ($tser = $sumser) and ($ot = ($titems+$tser)*$ot);


			($sale == 1) and ($diff  = abs($sumitems + $sumser + $ot + $os - $od - $amount));
			($sale == 0) and ($diff = abs($sumitems + $sumser - $amount));


			if($sale == 1 and $diff  < 1){
				 $sumitems = $sumitems+$ot+$os;
				 $flag=1;
			}elsif($diff < 1){
				$flag=1;
			}
			last FINAL if($flag == 1);
	}

		if($flag == 0){
				$pctp = (100/($titems+$tser)) * $titems;
				$sumitems = $amount * ($pctp/100);
				$sumser = $amount - $sumitems;

		}	
		return "$sumitems:$sumser";
}

sub repoper_product_exchange{
#-----------------------------------------
# Forms Involved: fin_repoper* 
# Created on: 3/07/2008 12:49PM
# Last Modified on: 3/07/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Check if a payment has been made just next a product exchange operation in sl_orders_products
# Parameters : [idorder: The id_order] [date: The date to search for]

	my ($idorders,$date) = @_;
	my $exchange = 0;
	## Fisrt, we need to extract both dates, the date of last retrn and the last pay before this
	my ($sth1) = &Do_SQL("SELECT Date FROM sl_orders_products WHERE ID_orders = $idorders AND Date < '$date' AND Status = 'Exchange' ORDER BY Date DESC LIMIT 1 ");
	my ($sth2) = &Do_SQL("SELECT CapDate FROM sl_orders_payments WHERE ID_orders = $idorders AND CapDate < '$date' ORDER BY Date DESC LIMIT 1 ");

	($sth1->fetchrow > $sth2->fetchrow) and ($exchange = 1);

	return $exchange;

}

sub repoper_product_exchange_price{
#-----------------------------------------
# Forms Involved: fin_repoper_sale* 
# Created on: 3/07/2008 12:49PM
# Last Modified on: 3/07/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Return the SalePrice of a Product in Exchange
# Parameters : [idorder: The id_order] [date: The date to search for]

	my ($idorders,$date) = @_;
	my (%tmp);
	my ($sth1) = &Do_SQL("SELECT SalePrice,Cost,ID_admin_users FROM sl_orders_products WHERE ID_orders = $idorders AND ShpDate < '$date' AND Status = 'Active'ORDER BY ShpDate DESC LIMIT 1 ");

	return $sth1->fetchrow;

}

sub printPage{
	my ($page) = @_;

	&html_print_headers ('Printing.....');
	print qq|
					<body onload="prn()" style="background-color:#FFFFFF">
					<!--
						<object id=factory viewastext style="display:none" 
						bclassid="clsid:1663ed61-23eb-11d2-b92f-008048fdd814"
  					codebase="/ScriptX.cab#Version=5,60,0,375">
						</object>
					-->
					<script defer>
						function prn() {
							window.print()
							return false;
						}
					</script>\n|;
	print &build_page($page);	

}	



###################
###################	AUXILIAR FUNCTIONS FOR CLOSE BATCH REPORT BASED ON OPERATIONS
###################

	##
	## ORIGINAL TRANSACTION
	##

sub products_sale_aux{


	my ($datef,$datet) = @_;
	#SALES
  my $sth = &Do_SQL("SELECT SalePrice,Cost,ID_products,sl_orders.ID_orders,OrderTax,OrderShp,OrderDisc,Shipping,Tax,Discount 
  									FROM sl_orders_products INNER JOIN sl_orders  
  									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
  									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND sl_orders_products.PostedDate = sl_orders.PostedDate AND SalePrice > 0
  									AND ID_products <> '600001018' AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ORDER BY sl_orders.ID_orders,ID_products");
  									
 while(my ($ts,$tc,$idp,$ido,$ot,$os,$od,$prShp,$prTax,$prDis) = $sth->fetchrow){
 		
 		if(substr($idp,0,1) eq '6'){	$total_service += $ts;
 		}else{	
 			($tc == 0) and ($tc = &repoper_cogs_product($idp)); 									
 			$total_sale += $ts;
 			$total_cogs += $tc;
 		}
 		
 		$total_tax += $prTax;
    $total_shp += $prShp;
    $total_dis += $prDis;
 }
 
 
 # DISCOUNT SERVICES
 my $sth = &Do_SQL("SELECT $total_dis + IF(SUM(ABS(SalePrice)) > 0,SUM(ABS(SalePrice)),0) 
  									FROM sl_orders_products INNER JOIN sl_orders  
  									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
  									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND sl_orders.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND SalePrice < 0 AND LEFT(ID_products,1) = 6
  									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive')");
 
 $total_dis = $sth->fetchrow;
 
 return ("$total_sale:$total_service:$total_cogs:$total_tax:$total_shp:$total_dis:$total_sale_claims");
}

sub payments_sale_aux{
#----------------------------------------------
# Last Modified RB: 02/18/09  10:52:43 - Se descartan registros de cancellation
# Last Modified RB: 03/09/09  13:33:11 - Last Modified RB: 03/09/09  13:29:57 -- Fixed MO deposits counted as Sale Deposits and taking CDA from preorders only with 2 or more payments(Excluded MO and WU deposits)

	my ($datef,$datet) = @_;
	#SALES DEPOSITS	
	my $sth = &Do_SQL("SELECT 
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =3, Amount, 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =4, Amount, 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =5, Amount, 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =6, Amount, 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='PayPal', Amount, 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='Google-checkout', Amount, 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='Amazon', Amount, 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='descuentolibre.com', Amount, 0 ) ) AS Descuentolibre,
					SUM( IF(Type = 'Credit-Card' AND PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
					SUM( IF(Type = 'Check', Amount, 0 ) ) AS chk ,
					SUM( IF(Type = 'WesternUnion', Amount, 0 ) ) AS WesternUnion,
					SUM( IF(Type = 'Money Order', Amount, 0 ) ) AS MoneyOrder,
					SUM(Amount) AS Total
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate = sl_orders.PostedDate
					AND (CapDate = sl_orders_payments.PostedDate OR (Capdate < sl_orders_payments.PostedDate
					AND CapDate BETWEEN '$datef' AND '$datet'))
					AND Amount >0 AND IF( TYPE IN ('Credit-Card', 'Check'), sl_orders_payments.Status = 'Approved'
					AND AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000',
					sl_orders_payments.Status = 'Approved' )
					AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND ID_products = '600001018') ");

	my($ae,$vi,$mc,$dc,$pp,$gc,$am,$dl,$wo,$ck,$wu,$mo,$to) = $sth->fetchrow;
	($ae > 0) and ($typeOfPaySales{'American Express'} = $ae);
	($vi > 0) and ($typeOfPaySales{'Visa'} = $vi);
	($mc > 0) and ($typeOfPaySales{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPaySales{'Discover'} = $dc);
	($pp > 0) and ($typeOfPaySales{'PayPal'} = $pp);
	($gc > 0) and ($typeOfPaySales{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPaySales{'Amazon'} = $am);
	($dl > 0) and ($typeOfPaySales{'Descuentolibre'} = $dl);
	($wo > 0) and ($typeOfPaySales{'Web Order'} = $wo);
	($ck > 0) and ($typeOfPaySales{'Check'} = $ck);
	($wu > 0) and ($typeOfPaySales{'Western Union'} = $wu);
	($mo > 0) and ($typeOfPaySales{'Money Order'} = $mo);
	$total_sales_deposits = $to;
	my $un = $to - $ae - $vi - $mc - $dc - $pp - $gc - $am - $dl - $wo - $ck - $wu - $mo;
	$typeOfPaySales{'Undefined'} = $un if $un >= 0.01;

	return $total_sales_deposits;
}

sub payments_claim_aux{


	my ($datef,$datet) = @_;
	# CLAIM	DEPOSITS
	my $sth = &Do_SQL("SELECT 
					SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =3 AND AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =4 AND AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =5 AND AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =6 AND AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
					SUM( IF(Type = 'Check' AND AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet', Amount, 0 ) ) AS chk ,
					SUM( IF(Type = 'WesternUnion', Amount, 0 ) ) AS WesternUnion,
					SUM( IF(Type = 'Money Order', Amount, 0 ) ) AS MoneyOrder,
					SUM(IF(AuthCode <> '0000' AND AuthCode IS NOT NULL AND AuthCode <> '' AND CapDate BETWEEN '$datef' AND '$datet',Amount,0)) AS TotalPay,
					SUM(IF(AuthCode = '0000' OR AuthCode IS NULL OR AuthCode = '',Amount,0)) AS TotalNpay
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate > sl_orders.PostedDate
					AND Amount >0 AND Reason = 'Sale' AND sl_orders_payments.Status = 'Claim' ");

	my($ae,$vi,$mc,$dc,$wo,$ck,$wu,$mo,$tp,$ta) = $sth->fetchrow;
	($ae > 0) and ($typeOfPayClaim{'American Express'} = $ae);
	($vi > 0) and ($typeOfPayClaim{'Visa'} = $vi);
	($mc > 0) and ($typeOfPayClaim{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPayClaim{'Discover'} = $dc);
	($wo > 0) and ($typeOfPayClaim{'Web Order'} = $wo);
	($ck > 0) and ($typeOfPayClaim{'Check'} = $ck);
	($wu > 0) and ($typeOfPayClaim{'Western Union'} = $wu);
	($mo > 0) and ($typeOfPayClaim{'Money Order'} = $mo);
	$total_claim_deposits = $tp;
	$total_claim_ar = $ta;
	my $un = $tp - $ae - $vi - $mc - $dc - $wo - $ck - $wu - $mo;
	$typeOfPayClaim{'Undefined'} = $un if $un >= 0.01;

	return ("$total_claim_deposits:$total_claim_ar");
}

sub payments_applied_aux{
#----------------------------------------------
# Last Modified RB: 02/18/09  10:52:43 - Se descartan registros de cancellation
# Last Modified RB: 02/19/09  17:01:23 - CapDate = $datef si tiene Preorden
# Last Modified RB: 03/09/09  13:33:11 - Last Modified RB: 03/09/09  13:29:57 -- Fixed MO deposits counted as Sale Deposits and taking CDA from preorders only with 2 or more payments(Excluded MO and WU deposits)


	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS APPLYING TODAY
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =3, Amount, 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =4, Amount, 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =5, Amount, 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND LEFT( PmtField3, 1 ) =6, Amount, 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='PayPal', Amount, 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='Google-checkout', Amount, 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='Amazon', Amount, 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND PmtField3='descuentolibre.com', Amount, 0 ) ) AS Descuentolibre,
					SUM( IF(Type = 'Credit-Card' AND PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
					SUM( IF(Type = 'Check', Amount, 0 ) ) AS chk ,
					SUM( IF(Type = 'WesternUnion', Amount, 0 ) ) AS WesternUnion,
					SUM( IF(Type = 'Money Order', Amount, 0 ) ) AS MoneyOrder,
					SUM(IF(Type = 'COD', Amount, 0 ) ) AS COD,
					SUM(IF(Type = 'COD', Amount*.04, 0 ) ) AS CODFee,
					SUM(Amount) AS Total
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'  AND sl_orders_payments.PostedDate = sl_orders.PostedDate
					AND CapDate IS NOT NULL AND CapDate != '0000-00-00' AND (CapDate < '$datef' OR (CapDate <= '$datet' ))
					AND Amount > 0 AND IF(TYPE IN ('Credit-Card', 'Check'), (sl_orders_payments.Status = 'Approved'
					AND AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000' AND ((CapDate <> '0000-00-00' ) OR Captured = 'Yes')), sl_orders_payments.Status = 'Approved' )
					AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders AND ID_products = '600001018')");


	my($ae,$vi,$mc,$dc,$pp,$gc,$am,$dl,$wo,$ck,$wu,$mo,$cod,$codf,$to) = $sth->fetchrow;
	($ae > 0) and ($typeOfPayPreDptSales{'American Express'} = $ae);
	($vi > 0) and ($typeOfPayPreDptSales{'Visa'} = $vi);
	($mc > 0) and ($typeOfPayPreDptSales{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPayPreDptSales{'Discover'} = $dc);
	($pp > 0) and ($typeOfPayPreDptSales{'Paypal'} = $pp);
	($gc > 0) and ($typeOfPayPreDptSales{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPayPreDptSales{'Amazon'} = $am);
	($dl > 0) and ($typeOfPayPreDptSales{'Descuentolibre'} = $dl);
	($wo > 0) and ($typeOfPayPreDptSales{'Web Order'} = $wo);
	($ck > 0) and ($typeOfPayPreDptSales{'Check'} = $ck);
	($wu > 0) and ($typeOfPayPreDptSales{'Western Union'} = $wu);
	($mo > 0) and ($typeOfPayPreDptSales{'Money Order'} = $mo);
	($cod > 0) and ($typeOfPayPreDptSales{'COD'} = $cod);
	$total_predeposits_sales = $to;
	my $un = $to - $ae - $vi - $mc - $dc - $pp - $gc - $am - $wo - $ck - $wu - $mo - $cod;
	$typeOfPayPreDptSales{'Undefined'} = $un if $un >= 0.01;

	return $total_predeposits_sales;
}

sub payments_flexpay_aux{
#-----------------------------------------
# Created on: 09/14/09  17:06:32 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my ($datef,$datet) = @_;
	#CONSECUTIVE DEPOSITS (FP)
	my $sth = &Do_SQL("SELECT
					SUM( IF( LEFT( PmtField3, 1 ) =3, Amount, 0 ) ) AS AmericanExpress,
					SUM( IF( LEFT( PmtField3, 1 ) =4, Amount, 0 ) ) AS Visa,
					SUM( IF( LEFT( PmtField3, 1 ) =5, Amount, 0 ) ) AS MasterCard,
					SUM( IF( LEFT( PmtField3, 1 ) =6, Amount, 0 ) ) AS Discover,
					SUM( IF(PmtField3='PayPal', Amount, 0 ) ) AS PayPal,
					SUM( IF(PmtField3='Google-checkout', Amount, 0 ) ) AS GoogleCheckout,
					SUM( IF(PmtField3='Amazon', Amount, 0 ) ) AS Amazon,
					SUM( IF(PmtField3='descuentolibre.com', Amount, 0 ) ) AS Descuentolibre,
					SUM( IF( PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
					SUM(Amount) AS Total
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE CapDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate < CapDate
					AND sl_orders_payments.PostedDate = sl_orders.PostedDate
					AND Amount > 0 AND Type = 'Credit-Card' AND sl_orders_payments.Status = 'Approved'
					AND AuthCode IS NOT NULL AND AuthCode !='' AND AuthCode !='0000' ");

	my($ae,$vi,$mc,$dc,$pp,$gc,$am,$dl,$wo,$to) = $sth->fetchrow;
	($ae > 0) and ($typeOfPayFpDpt{'American Express'} = $ae);
	($vi > 0) and ($typeOfPayFpDpt{'Visa'} = $vi);
	($mc > 0) and ($typeOfPayFpDpt{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPayFpDpt{'Discover'} = $dc);
	($pp > 0) and ($typeOfPayFpDpt{'Paypal'} = $pp);
	($gc > 0) and ($typeOfPayFpDpt{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPayFpDpt{'Amazon'} = $am);
	($dl > 0) and ($typeOfPayFpDpt{'Descuentolibre'} = $dl);
	($wo > 0) and ($typeOfPayFpDpt{'Web Order'} = $wo);
	$total_fpays_deposits = $to;
	my $un = $to - $ae - $vi - $mc - $dc - $pp - $gc - $am - $dl - $wo;
	$typeOfPayFpDpt{'Undefined'} = $un if $un >= 0.01;

	return $total_fpays_deposits;
}

sub payments_financed_aux{
#-----------------------------------------
# Created on: 09/14/09  17:06:38 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my ($datef,$datet) = @_;
	# FINANCED
	my $sth = &Do_SQL("SELECT
					SUM( IF( LEFT( PmtField3, 1 ) =3, Amount, 0 ) ) AS AmericanExpress,
					SUM( IF( LEFT( PmtField3, 1 ) =4, Amount, 0 ) ) AS Visa,
					SUM( IF( LEFT( PmtField3, 1 ) =5, Amount, 0 ) ) AS MasterCard,
					SUM( IF( LEFT( PmtField3, 1 ) =6, Amount, 0 ) ) AS Discover,
					SUM( IF( PmtField3='PayPal', Amount, 0 ) ) AS PayPal,
					SUM( IF( PmtField3='Google-checkout', Amount, 0 ) ) AS GoogleCheckout,
					SUM( IF( PmtField3='Amazon', Amount, 0 ) ) AS Amazon,
					SUM( IF( PmtField3='descuentolibre.com', Amount, 0 ) ) AS Descuentolibre,
					SUM( IF( PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
					SUM(Amount) AS Total
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE CapDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate < CapDate
					AND sl_orders_payments.PostedDate = sl_orders.PostedDate
					AND Amount > 0 AND Type = 'Credit-Card' AND sl_orders_payments.Status = 'Financed' ");

	my($ae,$vi,$mc,$dc,$pp,$gc,$am,$dl,$wo,$to) = $sth->fetchrow;
	($ae > 0) and ($typeOfPayFinDpt{'American Express'} = $ae);
	($vi > 0) and ($typeOfPayFinDpt{'Visa'} = $vi);
	($mc > 0) and ($typeOfPayFinDpt{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPayFinDpt{'Discover'} = $dc);
	($pp > 0) and ($typeOfPayFinDpt{'PayPal'} = $pp);
	($gc > 0) and ($typeOfPayFinDpt{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPayFinDpt{'Amazon'} = $am);
	($dl > 0) and ($typeOfPayFinDpt{'Descuentolibre'} = $dl);
	($wo > 0) and ($typeOfPayFinDpt{'Web Order'} = $wo);
	$total_financed_deposits = $to;
	my $un = $to - $ae - $vi - $mc - $dc - $pp - $gc - $am - $dl - $wo;
	$typeOfPayFinDpt{'Undefined'} = $un if $un >= 0.01;

	return $total_financed_deposits;
}

sub payments_deposit_aux{
#-----------------------------------------------------------------------
# Last Modified RB: 03/12/09  16:25:25 -- Fixed CD when MO change to CC	

	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS
  my $sth = &Do_SQL("SELECT 
				SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =3, Amount, 0 ) ) AS AmericanExpress,
				SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =4, Amount, 0 ) ) AS Visa,
				SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =5, Amount, 0 ) ) AS MasterCard,
				SUM( IF(Type = 'Credit-Card' AND  LEFT( PmtField3, 1 ) =6, Amount, 0 ) ) AS Discover,
				SUM( IF(Type = 'Credit-Card' AND PmtField3='PayPal', Amount, 0 ) ) AS PayPal,
				SUM( IF(Type = 'Credit-Card' AND PmtField3='Google-checkout', Amount, 0 ) ) AS GoogleCheckout,
				SUM( IF(Type = 'Credit-Card' AND PmtField3='Amazon', Amount, 0 ) ) AS Amazon,
				SUM( IF(Type = 'Credit-Card' AND PmtField3='descuentolibre.com', Amount, 0 ) ) AS Descuentolibre,
				SUM( IF(Type = 'Credit-Card' AND PmtField2 = 'Web Order' AND (Pmtfield3 = '' OR PmtField3 IS NULL OR LEFT(PmtField3,1) < 3 OR LEFT(PmtField3,1) > 6), Amount, 0 ) ) AS WebOrder,
				SUM( IF(Type = 'Check', Amount, 0 ) ) AS chk ,
				SUM( IF(Type = 'WesternUnion', Amount, 0 ) ) AS WesternUnion,
				SUM( IF(Type = 'Money Order', Amount, 0 ) ) AS MoneyOrder,
				SUM(Amount) AS Total
				FROM sl_orders_payments INNER JOIN sl_orders
				ON sl_orders.ID_orders = sl_orders_payments.ID_orders
				WHERE CapDate BETWEEN '$datef' AND '$datet'
				AND (sl_orders_payments.PostedDate > '$datet' OR sl_orders_payments.PostedDate IS NULL)
				AND (sl_orders_payments.PostedDate = sl_orders.PostedDate OR sl_orders.PostedDate IS NULL)
				AND Amount >0 AND sl_orders_payments.Status = 'Approved'");

	my($ae,$vi,$mc,$dc,$pp,$gc,$am,$dl,$wo,$ck,$wu,$mo,$to) = $sth->fetchrow;
	($ae > 0) and ($typeOfPayDpt{'American Express'} = $ae);
	($vi > 0) and ($typeOfPayDpt{'Visa'} = $vi);
	($mc > 0) and ($typeOfPayDpt{'Master Card'} = $mc);
	($dc > 0) and ($typeOfPayDpt{'Discover'} = $dc);
	($pp > 0) and ($typeOfPayDpt{'PayPal'} = $pp);
	($gc > 0) and ($typeOfPayDpt{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPayDpt{'Amazon'} = $am);
	($dl > 0) and ($typeOfPayDpt{'Descuentolibre'} = $dl);
	($wo > 0) and ($typeOfPayDpt{'Web Order'} = $wo);
	($ck > 0) and ($typeOfPayDpt{'Check'} = $ck);
	($wu > 0) and ($typeOfPayDpt{'Western Union'} = $wu);
	($mo > 0) and ($typeOfPayDpt{'Money Order'} = $mo);
	$total_deposits = $to;
	my $un = $to - $ae - $vi - $mc - $dc - $pp - $gc - $am - $dl - $wo - $ck - $wu - $mo;
	$typeOfPayDpt{'Undefined'} = $un if $un >= 0.01;

	return $total_deposits;
}

sub payments_layaway_aux{
#-----------------------------------------
# Created on: 09/17/09  12:17:44 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters :
# Last Modified RB: 09/24/09  13:25:21 -- El COD se extrae sin el fee
 	
	return 0;
}

	##
	## MODIFICATIONS
	##


sub products_return_aux{
#-----------------------------------------
# Created on: 09/16/09  11:51:54 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	# RETURNS IN 
  my $sth = &Do_SQL("SELECT ID_orders_products,ID_products,
  									IF(SalePrice < 0 AND LEFT(ID_products,1) != 6,ABS(SalePrice),0) AS SalePrice,
  									IF(SalePrice < 0 AND LEFT(ID_products,1) = 6,ABS(SalePrice),0) AS ServicePrice,
  									IF(ID_products IN (600001006,600001014),SalePrice,0) AS Fees,  
  									ABS(Shipping),ABS(Cost),ABS(Discount), ABS(Tax)
  									FROM sl_orders_products INNER JOIN sl_orders  
  									ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE 
  									sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND 
  									(SalePrice < 0  OR ID_products IN(600001006,600001014) ) 
  									AND IF(SalePrice < 0,sl_orders_products.Status = 'Returned',
  									sl_orders_products.Status NOT IN('Order Cancelled','Inactive')) ");
  									# ");
  									
	 while(my($idop,$idp,$ts,$tser,$tf,$tsh,$tc,$tdis,$ttax) = $sth->fetchrow){

	 		($tc == 0) and ($tc = &repoper_cogs_product($idp)); 									
	 		$total_return_sale_in += $ts;
	 		$total_return_service_in += $tser;
	 		$total_return_fees_in += $tf;
	 		$total_return_shp_in += $tsh;
	 		$total_return_cogs_in += $tc;
	 		$total_return_dis_in += $tdis;
	 		$total_return_tax_in += $ttax;
	}

	return ("$total_return_sale_in:$total_return_service_in:$total_return_fees_in:$total_return_shp_in:$total_return_cogs_in:$total_return_dis_in:$total_return_tax_in");	
}	

sub products_replace_aux{
#-----------------------------------------
# Created on: 09/16/09  11:51:59 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	# REPLACEMENTS 
	my $sth = &Do_SQL("SELECT ID_orders_products,ID_products,
											IF(LEFT(ID_products,1) <> 6,SalePrice,0)AS SalePrice,
											IF(LEFT(ID_products,1) = 6,SalePrice,0)AS ServicePrice,
											Shipping,Cost,Discount,Tax
	  									FROM sl_orders_products INNER JOIN sl_orders  
	  									ON sl_orders.ID_orders = sl_orders_products.ID_orders 
	  									AND sl_orders_products.PostedDate BETWEEN '$datef' AND '$datet' 
	  									AND sl_orders_products.PostedDate > sl_orders.PostedDate AND SalePrice > 0
	  									AND  IF(LEFT(ID_products,1) <> 6,((ShpDate IS NOT NULL AND ShpDate <> '' AND ShpDate <> '0000-00-00') OR (Tracking IS NOT NULL AND Tracking <> '')),ID_products = 600001004)
	  									AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive') ");


	while(my($idop,$idp,$ts,$tser,$tsh,$tc,$tdis,$ttax) = $sth->fetchrow){

	 				($tc == 0) and ($tc = &repoper_cogs_product($idp)); 									
	 				$total_return_sale_out += $ts;
	 				$total_return_service_out += $tser;
	 				$total_return_shp_out += $tsh;
	 				$total_return_cogs_out += $tc;
	 				$total_return_dis_out += $tdis;
	 				$total_return_tax_out += $ttax;
	}

	return ("$total_return_sale_out:$total_return_service_out:$total_return_shp_out:$total_return_cogs_out:$total_return_dis_out:$total_return_tax_out");			
}


sub payments_return_aux{
#-----------------------------------------
# Created on: 09/16/09  11:52:06 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;

	# REFUNDS DEBIT & CREDIT 
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS Descuentolibre,
					SUM( IF(Amount < 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS chk ,
					SUM( IF(Amount < 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS mo ,
					SUM( IF(Amount < 0,ABS(Amount),0)) AS TotalCredit,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS DAmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS DVisa,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS DMasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS DDiscover,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS DPayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS DGoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS DAmazon,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS DDescuentolibre,
					SUM( IF(Amount > 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS Dchk ,
					SUM( IF(Amount > 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS Dmo ,
					SUM( IF(Amount > 0,ABS(Amount),0)) AS TotalDebit
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE Reason IN ('Refund','Other') AND sl_orders_payments.CapDate BETWEEN '$datef' AND '$datet' AND Captured = 'Yes'
					AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate > sl_orders.PostedDate
					AND sl_orders_payments.Status IN ('Approved','Credit','ChargeBack')
					AND 1 > (SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = sl_orders.ID_orders
					AND ID_products = 600001018)");

	my($cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit,$dae,$dvi,$dmc,$ddc,$dpp,$dgc,$dam,$ddl,$dck,$dmo,$tdebit) = $sth->fetchrow;
	($cae > 0) and ($typeOfPayReturnCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayReturnCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayReturnCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayReturnCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayReturnCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayReturnCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayReturnCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayReturnCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayReturnCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayReturnCredit{'Money Order'} = $cmo);
	$total_return_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp - $cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayReturnCredit{'Undefined'} = $un if $un >= 0.01;
	($dae > 0) and ($typeOfPayReturnDebit{'American Express'} = $dae);
	($dvi > 0) and ($typeOfPayReturnDebit{'Visa'} = $dvi);
	($dmc > 0) and ($typeOfPayReturnDebit{'Master Card'} = $dmc);
	($ddc > 0) and ($typeOfPayReturnDebit{'Discover'} = $ddc);
	($dpp > 0) and ($typeOfPayReturnDebit{'PayPal'} = $dpp);
	($dgc > 0) and ($typeOfPayReturnDebit{'Google Checkout'} = $dgc);
	($dam > 0) and ($typeOfPayReturnDebit{'Amazon'} = $dam);
	($ddl > 0) and ($typeOfPayReturnDebit{'Descuentolibre'} = $ddl);
	($dck > 0) and ($typeOfPayReturnDebit{'Check'} = $dck);
	($dmo > 0) and ($typeOfPayReturnDebit{'Money Order'} = $dmo);
	$total_return_debits = $tdebit;
	my $un = $tdebit - $dae - $dvi - $dmc - $ddc - $dpp - $dgc - $dam - $ddl - $dck - $dmo;
	$typeOfPayReturnDebit{'Undefined'} = $un if $un >= 0.01;

	return ("$total_return_credits:$total_return_debits");	
}


sub payments_replace_aux{
#-----------------------------------------
# Created on: 09/16/09  11:52:12 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

		my ($datef,$datet) = @_;

		my $sth = &Do_SQL("SELECT
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS AmericanExpress,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS Visa,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS MasterCard,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS Discover,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS PayPal,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS GoogleCheckout,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS Amazon,
						SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS Descuentolibre,
						SUM( IF(Amount > 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS chk ,
						SUM( IF(Amount > 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS mo ,
						SUM( IF(Amount > 0,ABS(Amount),0)) AS TotalDebit,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS CAmericanExpress,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS CVisa,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS CMasterCard,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS CDiscover,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS CPayPal,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS CGoogleCheckout,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS CAmazon,
						SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre', ABS(Amount), 0 ) ) AS CDescuentolibre,
						SUM( IF(Amount < 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS Cchk ,
						SUM( IF(Amount < 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS Cmo ,
						SUM( IF(Amount < 0,ABS(Amount),0)) AS TotalCredit
						FROM sl_orders_payments INNER JOIN sl_orders
						ON sl_orders.ID_orders = sl_orders_payments.ID_orders
						WHERE Reason IN ('Exchange','Reship') AND CapDate BETWEEN '$datef' AND '$datet'
						AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
						AND sl_orders_payments.PostedDate > sl_orders.PostedDate
						AND sl_orders_payments.Status = 'Approved'");

	my($dae,$dvi,$dmc,$ddc,$dpp,$dgc,$dam,$ddl,$dck,$dmo,$tdebit,$cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit) = $sth->fetchrow;
	($dae > 0) and ($typeOfPayReplaceDebit{'American Express'} = $dae);
	($dvi > 0) and ($typeOfPayReplaceDebit{'Visa'} = $dvi);
	($dmc > 0) and ($typeOfPayReplaceDebit{'Master Card'} = $dmc);
	($ddc > 0) and ($typeOfPayReplaceDebit{'Discover'} = $ddc);
	($dpp > 0) and ($typeOfPayReplaceDebit{'PayPal'} = $dpp);
	($dgc > 0) and ($typeOfPayReplaceDebit{'Google Checkout'} = $dgc);
	($dam > 0) and ($typeOfPayReplaceDebit{'Amazon'} = $dam);
	($ddl > 0) and ($typeOfPayReplaceDebit{'Descuentolibre'} = $ddl);
	($dck > 0) and ($typeOfPayReplaceDebit{'Check'} = $dck);
	($dmo > 0) and ($typeOfPayReplaceDebit{'Money Order'} = $dmo);
	$total_replace_debits = $tdebit;
	my $un = $tdebit - $dae - $dvi - $dmc - $ddc - $dpp - $dgc - $dam - $ddl - $dck - $dmo;
	$typeOfPayReplaceDebit{'Undefined'} = $un if $un >= 0.01;
	($cae > 0) and ($typeOfPayReplaceCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayReplaceCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayReplaceCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayReplaceCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayReplaceCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayReplaceCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayReplaceCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayReplaceCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayReplaceCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayReplaceCredit{'Money Order'} = $cmo);
	$total_replace_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp - $cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayReplaceCredit{'Undefined'} = $un if $un >= 0.01;

	return ("$total_replace_debits:$total_replace_credits");

}


sub payments_cancell_aux{
#----------------------------------------------
# Last Modified RB: 02/18/09  10:56:02 -- Se corrigio linea para extraccion de Debits

	my ($datef,$datet) = @_;
	# DEBIT & CREDIT 
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3 AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4 AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5 AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6 AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre.com' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS Descuentolibre,
					SUM( IF(Amount < 0 AND Type = 'Check' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS chk ,
					SUM( IF(Amount < 0 AND Type = 'Money Order' AND CapDate BETWEEN '$datef' AND '$datet', ABS(Amount), 0 ) ) AS mo ,
					SUM( IF(Amount < 0 AND CapDate BETWEEN '$datef' AND '$datet',ABS(Amount),0)) AS TotalCredit,
					SUM(IF(Amount > 0,Amount,0)) AS Debits
					FROM sl_orders_products INNER JOIN sl_orders_payments ON sl_orders_products.ID_orders = sl_orders_payments.ID_orders
					WHERE ID_products = '600001018' AND sl_orders_payments.Status IN('Approved','Credit','ChargeBack') AND Captured = 'Yes' AND 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders_products.ID_orders AND Amount <0 AND CapDate BETWEEN '$datef' AND '$datet')");

	my($cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit,$tdebit) = $sth->fetchrow;
	($cae > 0) and ($typeOfPayCancellCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayCancellCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayCancellCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayCancellCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayCancellCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayCancellCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayCancellCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayCancellCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayCancellCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayCancellCredit{'Money Order'} = $cmo);
	$total_cancell_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp - $cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayCancellCredit{'Undefined'} = $un if $un >= 0.01;
	$total_cancell_debits = $tdebit;
	$total_cancell_fees = $tdebit - $tcredit;
	$total_cancell_credits += $total_cancell_fees if $total_cancell_fees > 0;


	return ("$total_cancell_credits:$total_cancell_debits:$total_cancell_fees");	
}


sub payments_modlow_aux{
#-----------------------------------------
# Created on: 09/16/09  11:52:19 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	# DEBIT & CREDIT 
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS Descuentolibre,
					SUM( IF(Amount < 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS chk ,
					SUM( IF(Amount < 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS mo ,
					SUM( IF(Amount < 0,ABS(Amount),0)) AS TotalCredit,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS DAmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS DVisa,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS DMasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS DDiscover,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS DPayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS DGoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS DAmazon,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS DDescuentolibre,
					SUM( IF(Amount > 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS Dchk ,
					SUM( IF(Amount > 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS Dmo ,
					SUM( IF(Amount > 0,ABS(Amount),0)) AS TotalDebit
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate > sl_orders.PostedDate
					AND sl_orders_payments.PostedDate < '$datef'
					AND sl_orders_payments.Status IN ('Approved','Credit') ");

	my($cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit,$dae,$dvi,$dmc,$ddc,$dpp,$dgc,$dam,$ddl,$dck,$dmo,$tdebit) = $sth->fetchrow;
	($cae > 0) and ($typeOfPayModLowCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayModLowCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayModLowCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayModLowCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayModLowCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayModLowCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayModLowCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayModLowCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayModLowCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayModLowCredit{'Money Order'} = $cmo);
	$total_modlow_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp - $cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayModLowCredit{'Undefined'} = $un if $un >= 0.01;
	($dae > 0) and ($typeOfPayModLowDebit{'American Express'} = $dae);
	($dvi > 0) and ($typeOfPayModLowDebit{'Visa'} = $dvi);
	($dmc > 0) and ($typeOfPayModLowDebit{'Master Card'} = $dmc);
	($ddc > 0) and ($typeOfPayModLowDebit{'Discover'} = $ddc);
	($dpp > 0) and ($typeOfPayModLowDebit{'PayPal'} = $dpp);
	($dgc > 0) and ($typeOfPayModLowDebit{'Google Checkout'} = $dgc);
	($dam > 0) and ($typeOfPayModLowDebit{'Amazon'} = $dam);
	($ddl > 0) and ($typeOfPayModLowDebit{'Descuentolibre'} = $ddl);
	($dck > 0) and ($typeOfPayModLowDebit{'Check'} = $dck);
	($dmo > 0) and ($typeOfPayModLowDebit{'Money Order'} = $dmo);
	$total_modlow_debits = $tdebit;
	my $un = $tdebit - $dae - $dvi - $dmc - $ddc - $dpp - $dgc - $dam - $ddl - $dck - $dmo;
	$typeOfPayModLowDebit{'Undefined'} = $un if $un >= 0.01;

	return ("$total_modlow_credits:$total_modlow_debits");	
}

sub payments_modup_aux{
#-----------------------------------------
# Created on: 09/16/09  11:52:27 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	# DEBIT & CREDIT 
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS Descuentolibre,
					SUM( IF(Amount < 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS chk ,
					SUM( IF(Amount < 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS mo ,
					SUM( IF(Amount < 0,ABS(Amount),0)) AS TotalCredit,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS DAmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS DVisa,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS DMasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS DDiscover,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS DPayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS DGoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS DAmazon,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS DDescuentolibre,
					SUM( IF(Amount > 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS Dchk ,
					SUM( IF(Amount > 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS Dmo ,
					SUM( IF(Amount > 0,ABS(Amount),0)) AS TotalDebit
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE Reason IN ('Refund','Exchange','Reship','Other') AND CapDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate > sl_orders.PostedDate
					AND sl_orders_payments.PostedDate > '$datet'
					AND sl_orders_payments.Status IN ('Approved','Credit') ");

	my($cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit,$dae,$dvi,$dmc,$ddc,$dpp,$dgc,$dam,$ddl,$dck,$dmo,$tdebit) = $sth->fetchrow;
	($cae > 0) and ($typeOfPayModUpCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayModUpCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayModUpCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayModUpCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayModUpCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayModUpCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayModUpCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayModUpCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayModUpCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayModUpCredit{'Money Order'} = $cmo);
	$total_modup_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp - $cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayModUpCredit{'Undefined'} = $un if $un >= 0.01;
	($dae > 0) and ($typeOfPayModUpDebit{'American Express'} = $dae);
	($dvi > 0) and ($typeOfPayModUpDebit{'Visa'} = $dvi);
	($dmc > 0) and ($typeOfPayModUpDebit{'Master Card'} = $dmc);
	($ddc > 0) and ($typeOfPayModUpDebit{'Discover'} = $ddc);
	($dpp > 0) and ($typeOfPayModUpDebit{'PayPal'} = $dpp);
	($dgc > 0) and ($typeOfPayModUpDebit{'Google Checkout'} = $dgc);
	($dam > 0) and ($typeOfPayModUpDebit{'Amazon'} = $dam);
	($ddl > 0) and ($typeOfPayModUpDebit{'Descuentolibre'} = $ddl);
	($dck > 0) and ($typeOfPayModUpDebit{'Check'} = $dck);
	($dmo > 0) and ($typeOfPayModUpDebit{'Money Order'} = $dmo);
	$total_modup_debits = $tdebit;
	my $un = $tdebit - $dae - $dvi - $dmc - $ddc - $dpp - $dgc - $dam - $ddl - $dck - $dmo;
	$typeOfPayModUpDebit{'Undefined'} = $un if $un >= 0.01;

	return ("$total_modup_credits:$total_modup_debits");	
}

sub payments_modapp_aux{
#-----------------------------------------
# Created on: 09/16/09  11:52:33 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	# DEBIT & CREDIT APPLIED TODAY 
	my $sth = &Do_SQL("SELECT
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS AmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS Visa,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS MasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS Discover,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS PayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS GoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS Amazon,
					SUM( IF(Type = 'Credit-Card' AND Amount < 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS Descuentolibre,
					SUM( IF(Amount < 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS chk ,
					SUM( IF(Amount < 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS mo ,
					SUM( IF(Amount < 0,ABS(Amount),0)) AS TotalCredit,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =3, ABS(Amount), 0 ) ) AS DAmericanExpress,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =4, ABS(Amount), 0 ) ) AS DVisa,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =5, ABS(Amount), 0 ) ) AS DMasterCard,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND LEFT( PmtField3, 1 ) =6, ABS(Amount), 0 ) ) AS DDiscover,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='PayPal', ABS(Amount), 0 ) ) AS DPayPal,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Google-checkout', ABS(Amount), 0 ) ) AS DGoogleCheckout,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='Amazon', ABS(Amount), 0 ) ) AS DAmazon,
					SUM( IF(Type = 'Credit-Card' AND Amount > 0 AND PmtField3='descuentolibre.com', ABS(Amount), 0 ) ) AS DDescuentolibre,
					SUM( IF(Amount > 0 AND Type = 'Check', ABS(Amount), 0 ) ) AS Dchk ,
					SUM( IF(Amount > 0 AND Type = 'Money Order', ABS(Amount), 0 ) ) AS Dmo ,
					SUM( IF(Amount > 0,ABS(Amount),0)) AS TotalDebit
					FROM sl_orders_payments INNER JOIN sl_orders
					ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE Reason IN ('Refund','Exchange','Reship','Other') AND sl_orders_payments.PostedDate BETWEEN '$datef' AND '$datet'
					AND sl_orders_payments.PostedDate > sl_orders.PostedDate AND CapDate < '$datef' AND Capdate <> '0000-00-00' AND Captured = 'Yes'
					AND sl_orders_payments.Status IN ('Approved','Credit')");

	my($cae,$cvi,$cmc,$cdc,$cpp,$cgc,$cam,$cdl,$cck,$cmo,$tcredit,$dae,$dvi,$dmc,$ddc,$dpp,$dgc,$dam,$ddl,$dck,$dmo,$tdebit) = $sth->fetchrow;
	($cae > 0) and ($typeOfPayModAppCredit{'American Express'} = $cae);
	($cvi > 0) and ($typeOfPayModAppCredit{'Visa'} = $cvi);
	($cmc > 0) and ($typeOfPayModAppCredit{'Master Card'} = $cmc);
	($cdc > 0) and ($typeOfPayModAppCredit{'Discover'} = $cdc);
	($cpp > 0) and ($typeOfPayModAppCredit{'PayPal'} = $cpp);
	($cgc > 0) and ($typeOfPayModAppCredit{'Google Checkout'} = $cgc);
	($cam > 0) and ($typeOfPayModAppCredit{'Amazon'} = $cam);
	($cdl > 0) and ($typeOfPayModAppCredit{'Descuentolibre'} = $cdl);
	($cck > 0) and ($typeOfPayModAppCredit{'Check'} = $cck);
	($cmo > 0) and ($typeOfPayModAppCredit{'Money Order'} = $cmo);
	$total_modapp_credits = $tcredit;
	my $un = $tcredit - $cae - $cvi - $cmc - $cdc - $cpp -$cgc - $cam - $cdl - $cck - $cmo;
	$typeOfPayModAppCredit{'Undefined'} = $un if $un >= 0.01;
	($dae > 0) and ($typeOfPayModAppDebit{'American Express'} = $dae);
	($dvi > 0) and ($typeOfPayModAppDebit{'Visa'} = $dvi);
	($dmc > 0) and ($typeOfPayModAppDebit{'Master Card'} = $dmc);
	($ddc > 0) and ($typeOfPayModAppDebit{'Discover'} = $ddc);
	($dpp > 0) and ($typeOfPayModAppDebit{'PayPal'} = $dpp);
	($dgc > 0) and ($typeOfPayModAppDebit{'Google Checkout'} = $dgc);
	($dam > 0) and ($typeOfPayModAppDebit{'Amazon'} = $dam);
	($ddl > 0) and ($typeOfPayModAppDebit{'Descuentolibre'} = $ddl);
	($dck > 0) and ($typeOfPayModAppDebit{'Check'} = $dck);
	($dmo > 0) and ($typeOfPayModAppDebit{'Money Order'} = $dmo);
	$total_modapp_debits = $tdebit;
	my $un = $tdebit - $dae - $dvi - $dmc - $ddc - $dpp - $dgc - $dam - $ddl - $dck - $dmo;
	$typeOfPayModAppDebit{'Undefined'} = $un if $un >= 0.01;

	return ("$total_modapp_credits:$total_modapp_debits");	
}


sub payments_movedfrom_aux{
#--------------------------------------------------------
# Last Modified RB: 03/16/09  13:03:00

	return("0:0");

}



###################
###################	AUXILIAR FUNCTIONS FOR CLOSE BATCH REPORT BASED ON MOVEMENTS
###################

	##
	## ORIGINAL TRANSACTION
	##

sub products_sale_mov{
#-----------------------------------------
# Created on: 09/16/09  11:52:44 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	
# Last Modified RB: 10/23/09  17:11:57 -- Se modifica para extraer el customer refund solamente si no hay movimiento de devolucion de dinero en el mismo periodo


	my ($datef,$datet) = @_;
	#SALES
  my $sth = &Do_SQL("SELECT
	SUM(AR)AS AR,
	SUM(ARPR)AS ARPR,
	SUM(Inventory)AS Inventory,
	SUM(Tax)AS Tax,
	SUM(Products)AS Products,
	SUM(Services)AS Services,
	SUM(Shipping)AS Shipping,
	SUM(Discounts)AS Discounts,
	SUM(COGS)AS COGS,
	SUM(DiffDebit)AS DiffDebit,
	SUM(DiffCredit)AS DiffCredit,
	SUM(IF(Refunds=1,0,CRefund))AS CRefund  
FROM 
	(
		SELECT 
			ID_tableused,
			SUM(IF(ID_accounts=41 AND Credebit = 'Debit',Amount,0)) AS AR,
			SUM(IF(ID_accounts=65 AND Credebit = 'Debit',Amount,0)) AS ARPR,
			SUM(IF(ID_accounts=89 AND Credebit = 'Credit',Amount,0)) AS Inventory,
			SUM(IF(ID_accounts=152 AND Credebit = 'Credit',Amount,0)) AS Tax,
			SUM(IF(ID_accounts=170 AND Credebit = 'Credit',Amount,0)) AS Products,
			SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Services,
			SUM(IF(ID_accounts=185 AND Credebit = 'Credit',Amount,0)) AS Shipping,
			SUM(IF(ID_accounts=187 AND Credebit = 'Debit',Amount,0)) AS Discounts,
			SUM(IF(ID_accounts=193 AND Credebit = 'Debit',Amount,0)) AS COGS,
			SUM(IF(ID_accounts=311 AND Credebit = 'Debit',Amount,0)) AS DiffDebit,
			SUM(IF(ID_accounts=311 AND Credebit = 'Credit',Amount,0)) AS DiffCredit,
			SUM(IF(ID_accounts=327 AND Credebit = 'Credit',Amount,0)) AS CRefund
		FROM	
			sl_movements 
		WHERE  
			ID_accounts IN(41,65,89,152,170,180,185,187,193,311,327) 
			AND EffDate BETWEEN '$datef' AND '$datet' 
			AND tableused='sl_orders' 
			AND Category='Sale' 
			AND Status = 'Active'
			GROUP BY ID_tableused
	)AS tmp
LEFT JOIN
	(
		SELECT 
			ID_tableused,
			COUNT(*) AS Refunds 
		FROM 
			sl_movements 
		WHERE 
			ID_accounts=327 
			AND Credebit = 'Debit' 
			AND EffDate BETWEEN '$datef' AND '$datet' 
			AND tableused='sl_orders' 
			AND Category='Sale' 
			AND Status = 'Active'
			GROUP BY ID_tableused  
	)AS tmp2
ON 
	tmp.ID_tableused=tmp2.ID_tableused 
ORDER BY tmp.ID_tableused;");
  									
	my ($ar,$arpr,$in,$tax,$prod,$ser,$shipp,$dis,$cogs,$dpd,$dpc,$cref) = $sth->fetchrow();

 return ($ar,$arpr,$in,$tax,$prod,$ser,$shipp,$dis,$cogs,$dpd,$dpc,$cref);
 
}


sub payments_sale_mov{
#----------------------------------------------
# Last Modified RB: 09/16/09  11:18:07 -- Retorna los valores para Depositos de venta


	my ($datef,$datet) = @_;
	#SALES DEPOSITS	

my $sth = &Do_SQL("SELECT
				SUM(IF(Cash IS NOT NULL,Cash,0)) AS Cash,
				SUM(IF(VMC IS NOT NULL,VMC,0)) AS VMC,
				SUM(IF(Amex IS NOT NULL,Amex,0)) AS Amex,
				SUM(IF(Discover IS NOT NULL,Discover,0)) AS Discover,
				SUM(IF(PayPal IS NOT NULL,PayPal,0)) AS PayPal,
				SUM(IF(Google IS NOT NULL,Google,0)) AS Google,
				SUM(IF(Amazon IS NOT NULL,Amazon,0)) AS Amazon,
				SUM(IF(Descuentolibre IS NOT NULL,Descuentolibre,0)) AS Descuentolibre,
				SUM(IF(COD IS NOT NULL,COD,0)) AS COD,
				SUM(IF(AmountD IS NOT NULL,AmountD,0)) AS AmountD,
				SUM(IF(CashC IS NOT NULL,CashC,0)) AS CashC,
				SUM(IF(VMCC IS NOT NULL,VMCC,0)) AS VMCC,
				SUM(IF(AmexC IS NOT NULL,AmexC,0)) AS AmexC,
				SUM(IF(DiscoverC IS NOT NULL,DiscoverC,0)) AS DiscoverC,
				SUM(IF(PayPalC IS NOT NULL,PayPalC,0)) AS PayPalC,
				SUM(IF(GoogleC IS NOT NULL,GoogleC,0)) AS GoogleC,
				SUM(IF(AmazonC IS NOT NULL,AmazonC,0)) AS AmazonC,
				SUM(IF(DescuentolibreC IS NOT NULL,DescuentolibreC,0)) AS DescuentolibreC,
				SUM(IF(CODC IS NOT NULL,CODC,0)) AS CODC,
				SUM(IF(AmountC IS NOT NULL,AmountC,0)) AS AmountC
				FROM
				(
				SELECT
					ID_tableused AS ID_debits,
					SUM(IF(ID_accounts=1,Amount,0)) AS Cash,
					SUM(IF(ID_accounts=12,Amount,0)) AS VMC,
					SUM(IF(ID_accounts=14,Amount,0)) AS Amex,
					SUM(IF(ID_accounts=16,Amount,0)) AS Discover,
					SUM(IF(ID_accounts=20,Amount,0)) AS PayPal,
					SUM(IF(ID_accounts=329,Amount,0)) AS Google,
					SUM(IF(ID_accounts=330,Amount,0)) AS Amazon,
					SUM(IF(ID_accounts=331,Amount,0)) AS Descuentolibre,
					SUM(IF(ID_accounts=22,Amount,0)) AS COD,
					SUM(Amount)AS AmountD
					FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status) WHERE  ID_accounts IN(1,12,14,16,20,22,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Sale' AND Credebit='Debit' AND Status = 'Active'
					GROUP BY ID_debits
				)AS tmp_debits
				LEFT JOIN
				(
				SELECT
					ID_tableused AS ID_credits,
					SUM(IF(ID_accounts=1,Amount,0)) AS CashC,
					SUM(IF(ID_accounts=12,Amount,0)) AS VMCC,
					SUM(IF(ID_accounts=14,Amount,0)) AS AmexC,
					SUM(IF(ID_accounts=16,Amount,0)) AS DiscoverC,
					SUM(IF(ID_accounts=20,Amount,0)) AS PayPalC,
					SUM(IF(ID_accounts=329,Amount,0)) AS GoogleC,
					SUM(IF(ID_accounts=330,Amount,0)) AS AmazonC,
					SUM(IF(ID_accounts=331,Amount,0)) AS DescuentolibreC,
					SUM(IF(ID_accounts=22,Amount,0)) AS CODC,
					SUM(Amount) AS AmountC
				FROM
					sl_movements
				USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status)
				WHERE
					ID_accounts IN(1,12,14,16,20,22,329,330,331)
					AND EffDate BETWEEN '$datef' AND '$datet'
					AND tableused='sl_orders'
					AND Category='Sale'
					AND Credebit='Credit'
					AND Status = 'Active'
					AND 0 <
					(
						SELECT COUNT(*) FROM sl_movements WHERE ID_accounts IN(170,180) AND tableused='sl_orders' AND ID_tableused = sl_movements.ID_tableused AND EffDate BETWEEN '$datef' AND '$datet'  AND Category='Sale' AND Credebit='Credit' AND Status = 'Active'
					) GROUP BY ID_credits
				)AS tmp_credits
				ON ID_debits = ID_credits;"); 


	my($cash,$vmc,$ae,$dc,$pp,$gc,$am,$dl,$cod,$total_sale,$cashc,$vmcc,$aec,$dcc,$ppc,$gcc,$amc,$dlc,$codc,$total_scredit) = $sth->fetchrow;
	($cash > 0) and ($typeOfPaySales{'Cash'} = $cash);
	($vmc > 0) and ($typeOfPaySales{'Visa/Masterd Card'} = $vmc);
	($ae > 0) and ($typeOfPaySales{'American Express'} = $ae);
	($dc > 0) and ($typeOfPaySales{'Discover'} = $dc);
	($pp > 0) and ($typeOfPaySales{'PayPal'} = $pp);
	($gc > 0) and ($typeOfPaySales{'Google Checkout'} = $gc);
	($am > 0) and ($typeOfPaySales{'Amazon'} = $am);
	($dl > 0) and ($typeOfPaySales{'Descuentolibre'} = $dl);
	($cod > 0) and ($typeOfPaySales{'COD'} = $cod);
	my $total_sales_deposits = $total_sale;

	($cashc > 0) and ($typeOfPaySalesC{'Cash'} = $cashc);
	($vmcc > 0) and ($typeOfPaySalesC{'Visa/Masterd Card'} = $vmcc);
	($aec > 0) and ($typeOfPaySalesC{'American Express'} = $aec);
	($dcc > 0) and ($typeOfPaySalesC{'Discover'} = $dcc);
	($ppc > 0) and ($typeOfPaySalesC{'PayPal'} = $ppc);
	($gcc > 0) and ($typeOfPaySalesC{'Google Checkout'} = $gcc);
	($amc > 0) and ($typeOfPaySalesC{'Amazon'} = $amc);
	($dlc > 0) and ($typeOfPaySalesC{'Descuentolibre'} = $dlc);
	($codc > 0) and ($typeOfPaySalesC{'COD'} = $codc);
	my $total_sales_credits = $total_scredit;

	return ($total_sales_deposits,$total_sales_credits);
}


sub payments_applied_mov{
#-----------------------------------------
# Created on: 09/16/09  11:52:54 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified RB: 09/23/09  12:54:34 -- Se saca el amount por tipo de cuenta.


	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS APPLYING TODAY
	my $sth = &Do_SQL("SELECT
	/* CDA */
	SUM(IF(Cash IS NOT NULL AND tmp_o.EffDate < '$datef',Cash,0))AS CashCDA,
	SUM(IF(VMC IS NOT NULL AND tmp_o.EffDate < '$datef',VMC,0))AS VMCCDA,
	SUM(IF(Amex IS NOT NULL AND tmp_o.EffDate < '$datef',Amex,0))AS AmexCDA,
	SUM(IF(Discover IS NOT NULL AND tmp_o.EffDate < '$datef',Discover,0))AS DiscoverCDA,
	SUM(IF(PayPal IS NOT NULL AND tmp_o.EffDate < '$datef',PayPal,0))AS PayPalCDA,
	SUM(IF(Google IS NOT NULL AND tmp_o.EffDate < '$datef',Google,0))AS GoogleCDA,
	SUM(IF(Amazon IS NOT NULL AND tmp_o.EffDate < '$datef',Amazon,0))AS AmazonCDA,
	SUM(IF(Descuentolibre IS NOT NULL AND tmp_o.EffDate < '$datef',Descuentolibre,0))AS DescuentolibreCDA,
	SUM(IF(COD IS NOT NULL AND tmp_o.EffDate < '$datef',COD,0))AS CODCDA,
	SUM(IF(tmp_o.EffDate < '$datef',sl_movements.Amount,0)) AS TotalCDA,
	/* CDA/CD = Sale */
	SUM(IF(Cash IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Cash,0))AS CashSale,
	SUM(IF(VMC IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,VMC,0))AS VMCSale,
	SUM(IF(Amex IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Amex,0))AS AmexSale,
	SUM(IF(Discover IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Discover,0))AS DiscoverSale,
	SUM(IF(PayPal IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,PayPal,0))AS PayPalSale,
	SUM(IF(Google IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Google,0))AS GoogleSale,
	SUM(IF(Amazon IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Amazon,0))AS AmazonSale,
	SUM(IF(Descuentolibre IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,Descuentolibre,0))AS DescuentolibreSale,
	SUM(IF(COD IS NOT NULL AND tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,COD,0))AS CODSale,
	SUM(IF(tmp_o.EffDate >= '$datef' AND tmp_o.EffDate <= sl_movements.EffDate,sl_movements.Amount,0)) AS TotalSale,
	/* COD Sales */
	SUM(IF(Cash IS NOT NULL AND tmp_o.EffDate IS NULL,Cash,0))AS CashCOD,
	SUM(IF(VMC IS NOT NULL AND tmp_o.EffDate IS NULL,VMC,0))AS VMCCOD,
	SUM(IF(Amex IS NOT NULL AND tmp_o.EffDate IS NULL,Amex,0))AS AmexCOD,
	SUM(IF(Discover IS NOT NULL AND tmp_o.EffDate IS NULL,Discover,0))AS DiscoverCOD,
	SUM(IF(PayPal IS NOT NULL AND tmp_o.EffDate IS NULL,PayPal,0))AS PayPalCOD,
	SUM(IF(Google IS NOT NULL AND tmp_o.EffDate IS NULL,Google,0))AS GoogleCOD,
	SUM(IF(Amazon IS NOT NULL AND tmp_o.EffDate IS NULL,Amazon,0))AS AmazonCOD,
	SUM(IF(Descuentolibre IS NOT NULL AND tmp_o.EffDate IS NULL,Descuentolibre,0))AS DescuentolibreCOD,
	SUM(IF(COD IS NOT NULL AND tmp_o.EffDate IS NULL,COD,0))AS CODCOD,
	SUM(IF(tmp_o.EffDate IS NULL,sl_movements.Amount,0)) AS TotalCOD 
FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused)
  LEFT JOIN 
  (
     SELECT ID_orders FROM sl_orders USE INDEX (Status) WHERE Status ='Shipped'
  )AS tmp
  ON ID_tableused = tmp.ID_orders
LEFT JOIN(
    SELECT
      ID_tableused,Amount,EffDate,
      IF(ID_accounts=1,Amount,0) AS Cash,
  IF(ID_accounts=12,Amount,0) AS VMC,
  IF(ID_accounts=14,Amount,0) AS Amex,
  IF(ID_accounts=16,Amount,0) AS Discover,
  IF(ID_accounts=20,Amount,0) AS PayPal,
  IF(ID_accounts=329,Amount,0) AS Google,
  IF(ID_accounts=330,Amount,0) AS Amazon,
  IF(ID_accounts=331,Amount,0) AS Descuentolibre,
  IF(ID_accounts=22,Amount,0) AS COD
FROM sl_movements USE INDEX (ID_accounts,Category,EffDate,tableused)
   WHERE  ID_accounts IN(1,12,14,16,20,22,129,329,330,331) AND tableused='sl_orders' AND Category='Deposit' AND Credebit='Debit' AND Status = 'Active' 
)AS tmp_o
ON tmp_o.ID_tableused = sl_movements.ID_tableused
AND tmp_o.Amount = sl_movements.Amount
AND tmp_o.EffDate <= sl_movements.EffDate  
WHERE  ID_accounts = 129 AND sl_movements.EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Sale' AND Credebit='Debit' AND sl_movements.Status = 'Active';");

	my ($cashcda,$vmccda,$aecda,$dccda,$ppcda,$gccda,$amcda,$dlcda,$codcda,$dep_cda,$cashsale,$vmcsale,$aesale,$dcsale,$ppsale,$gcsale,$amsale,$dlsale,$codsale,$dep_sale,$cashcod,$vmccod,$aecod,$dccod,$ppcod,$gccod,$amcod,$dlcod,$codcod,$dep_cod) = $sth->fetchrow();
	($cashcda 	> 0) and ($typeOfPayApp{'Cash'} = $cashcda);
	($vmccda 	> 0) and ($typeOfPayApp{'Visa/Masterd Card'} = $vmccda);
	($aecda 	> 0) and ($typeOfPayApp{'American Express'} = $aecda);
	($dccda 	> 0) and ($typeOfPayApp{'Discover'} = $dccda);
	($ppcda 	> 0) and ($typeOfPayApp{'PayPal'} = $ppcda);
	($gccda 	> 0) and ($typeOfPayApp{'Google Checkout'} = $gccda);
	($amcda 	> 0) and ($typeOfPayApp{'Amazon'} = $amcda);
	($dlcda 	> 0) and ($typeOfPayApp{'Descuentolibre'} = $dlcda);
	($codcda 	> 0) and ($typeOfPayApp{'COD'} = $codcda);

	($cashsale 	> 0) and ($typeOfPaySales{'Cash'} += $cashsale );
	($vmcsale  	> 0) and ($typeOfPaySales{'Visa/Masterd Card'} += $vmcsale);
	($aesale  	> 0) and ($typeOfPaySales{'American Express'} += $aesale);
	($dcsale  	> 0) and ($typeOfPaySales{'Discover'} += $dcsale );
	($ppsale  	> 0) and ($typeOfPaySales{'PayPal'} += $ppsale );
	($gcsale  	> 0) and ($typeOfPaySales{'Google Checkout'} += $gcsale );
	($amsale  	> 0) and ($typeOfPaySales{'Amazon'} += $amsale );
	($dlsale  	> 0) and ($typeOfPaySales{'Descuentolibre'} += $dlsale );
	($codsale  	> 0) and ($typeOfPaySales{'COD'} += $codsale );

	($cashcod 	> 0) and ($typeOfPayCODSale{'Cash'} += $cashcod );
	($vmccod  	> 0) and ($typeOfPayCODSale{'Visa/Masterd Card'} += $vmccod);
	($aecod  	> 0) and ($typeOfPayCODSale{'American Express'} += $aecod);
	($dccod  	> 0) and ($typeOfPayCODSale{'Discover'} += $dccod );
	($ppcod  	> 0) and ($typeOfPayCODSale{'PayPal'} += $ppcod );
	($gccod  	> 0) and ($typeOfPayCODSale{'Google Checkout'} += $gccod );
	($amcod  	> 0) and ($typeOfPayCODSale{'Amazon'} += $amcod );
	($dlcod  	> 0) and ($typeOfPayCODSale{'Descuentolibre'} += $dlcod );
	($codcod  	> 0) and ($typeOfPayCODSale{'COD'} += $codcod );



	return ($dep_cda,$dep_sale,$dep_cod);
}


sub payments_flexpay_mov{
#-----------------------------------------
# Created on: 09/16/09  11:51:01 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	#CONSECUTIVE DEPOSITS (FP)
	my $sth = &Do_SQL("SELECT 
					SUM(IF(ID_accounts=1 AND Credebit='Debit',Amount,0)) AS Cash,
					SUM(IF(ID_accounts=12 AND Credebit='Debit',Amount,0)) AS VMC,
					SUM(IF(ID_accounts=14 AND Credebit='Debit',Amount,0)) AS Amex,
					SUM(IF(ID_accounts=16 AND Credebit='Debit',Amount,0)) AS Discover,
					SUM(IF(ID_accounts=20 AND Credebit='Debit',Amount,0)) AS PayPal,
					SUM(IF(ID_accounts=329 AND Credebit='Debit',Amount,0)) AS Google,
					SUM(IF(ID_accounts=330 AND Credebit='Debit',Amount,0)) AS Amazon,
					SUM(IF(ID_accounts=331 AND Credebit='Debit',Amount,0)) AS Descuentolibre,
					SUM(IF(ID_accounts=22 AND Credebit='Debit',Amount,0)) AS COD,
					SUM(IF(ID_accounts=26 AND Credebit='Debit',Amount,0)) AS SKO,
					SUM(IF(ID_accounts=235 AND Credebit='Debit',Amount,0)) AS BDEBT,
					SUM(IF(ID_accounts=306 AND Credebit='Debit',Amount,0)) AS CFEES,
					SUM(IF(ID_accounts=26 AND Credebit='Credit',Amount,0)) AS SKOAR,
					SUM(IF(ID_accounts=327 AND Credebit='Credit',Amount,0)) AS CR,
					SUM(IF(ID_accounts=41 AND Credebit='Credit',Amount,0)) AS AR
					FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused) 
					WHERE  ID_accounts IN(1,12,14,16,20,22,26,41,235,306,327,329,330) 
					AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' 
					AND Category='Flexpay'
					AND Status = 'Active' ORDER BY ID_accounts; ");

	my($cash,$vmc,$ae,$dc,$pp,$gc,$am,$dl,$cod,$sko,$bde,$cfe,$skoar,$cref,$ar) = $sth->fetchrow;
	($cash 	> 0) and ($typeOfPayFpDpt{'Cash'} = $cash);
	($vmc 	> 0) and ($typeOfPayFpDpt{'Visa/Masterd Card'} = $vmc);
	($ae 		> 0) and ($typeOfPayFpDpt{'American Express'} = $ae);
	($dc 		> 0) and ($typeOfPayFpDpt{'Discover'} = $dc);
	($pp 		> 0) and ($typeOfPayFpDpt{'PayPal'} = $pp);
	($gc 		> 0) and ($typeOfPayFpDpt{'Google Checkout'} = $gc);
	($am 		> 0) and ($typeOfPayFpDpt{'Amazon'} = $am);
	($dl 		> 0) and ($typeOfPayFpDpt{'Descuentolibre'} = $dl);
	($cod 	> 0) and ($typeOfPayFpDpt{'COD'} = $cod);
	($sko > 0) and ($typeOfPayFpDpt{'SKO'} = $sko);
	($bde > 0) and ($typeOfPayFpDpt{'BAD DEBT'} = $bde);
	($cfe > 0) and ($typeOfPayFpDpt{'COLLECTION FEES'} = $cfe);
	my $total_fpays_deposits 	= $cash+$vmc+$ae+$dc+$pp+$gc+$am+$dl+$cod+$sko+$bde+$cfe;

	return ($total_fpays_deposits,$skoar,$cref,$ar);
}


sub payments_deposit_mov{
#-----------------------------------------
# Created on: 09/16/09  11:16:43 By  Roberto Barcenas
# Forms Involved: 
# Description : Retorna los valores para los depositos de cliente basado en movimientos contables
# Parameters : 
#Last modified on 29 Sep 2010 15:13:42
#Last modified by: MCC C. Gabriel Varela S. : Se optimiza consulta. Saludos.
#UrgentNote: Revisar esta consulta, al parecer es la que toma mas tiempo.

	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS
	my $sth = &Do_SQL("SELECT
					SUM(IF(CashOrder IS NOT NULL,CashOrder,0)) AS CashOrder,
					SUM(IF(VMCOrder IS NOT NULL,VMCOrder,0)) AS VMCOrder,
					SUM(IF(AmexOrder IS NOT NULL,AmexOrder,0)) AS AmexOrder,
					SUM(IF(DiscoverOrder IS NOT NULL,DiscoverOrder,0)) AS DiscoverOrder,
					SUM(IF(PayPalOrder IS NOT NULL,PayPalOrder,0)) AS PayPalOrder,
					SUM(IF(GoogleOrder IS NOT NULL,GoogleOrder,0)) AS GoogleOrder,
					SUM(IF(AmazonOrder IS NOT NULL,AmazonOrder,0)) AS AmazonOrder,
					SUM(IF(DescuentolibreOrder IS NOT NULL,DescuentolibreOrder,0)) AS DescuentolibreOrder,
					SUM(IF(CODOrder IS NOT NULL,CODOrder,0)) AS CODOrder,
					SUM(IF(DepositsOrder IS NOT NULL,DepositsOrder,0)) AS DepositsOrder
					FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status)
					LEFT JOIN
					(
						SELECT ID_tableused AS ID_orders,Amount,ID_accounts,
						SUM(IF(ID_accounts=1,Amount,0)) AS CashOrder,
						SUM(IF(ID_accounts=12,Amount,0)) AS VMCOrder,
						SUM(IF(ID_accounts=14,Amount,0)) AS AmexOrder,
						SUM(IF(ID_accounts=16,Amount,0)) AS DiscoverOrder,
						SUM(IF(ID_accounts=20,Amount,0)) AS PayPalOrder,
						SUM(IF(ID_accounts=329,Amount,0)) AS GoogleOrder,
						SUM(IF(ID_accounts=330,Amount,0)) AS AmazonOrder,
						SUM(IF(ID_accounts=331,Amount,0)) AS DescuentolibreOrder,
						SUM(IF(ID_accounts=22,Amount,0)) AS CODOrder,
						SUM(IF(ID_accounts=129,Amount,0)) AS DepositsOrder,
						SUM(IF(ID_accounts IN(1,12,14,16,20,22,329,330,331),Amount,0)) - SUM(IF(ID_accounts=129,Amount,0)) AS Conciliation
						FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status)
						WHERE  ID_accounts IN(1,12,14,16,20,22,129,329,330,331) AND '$datet' < (SELECT  IF( ShpDate IS NOT NULL AND ShpDate != '0000-00-00', MIN( ShpDate ) , DATE_ADD('$datet',INTERVAL 100 DAY) ) FROM sl_orders_products WHERE ID_orders = sl_movements.ID_tableused ) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Deposit' AND IF(ID_accounts=129,Credebit='Credit',Credebit='Debit') AND Status = 'Active'
						GROUP BY ID_tableused  HAVING Conciliation = 0
					)AS tmp
					ON ID_tableused = ID_orders
					AND sl_movements.Amount = tmp.Amount AND sl_movements.ID_accounts = tmp.ID_accounts
					WHERE  sl_movements.ID_accounts IN(1,12,14,16,20,22,129,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND Category='Deposit' AND IF(sl_movements.ID_accounts=129,Credebit='Credit',Credebit='Debit') AND Status = 'Active' ORDER BY sl_movements.ID_accounts; ");

	my($cash,$vmc,$ae,$dc,$pp,$gc,$am,$dl,$cod,$deposits) = $sth->fetchrow;
	($cash 	> 0) and ($typeOfPayDpt{'Cash'} = $cash);
	($vmc 	> 0) and ($typeOfPayDpt{'Visa/Masterd Card'} = $vmc);
	($ae 		> 0) and ($typeOfPayDpt{'American Express'} = $ae);
	($dc 		> 0) and ($typeOfPayDpt{'Discover'} = $dc);
	($pp 		> 0) and ($typeOfPayDpt{'PayPal'} = $pp);
	($gc 		> 0) and ($typeOfPayDpt{'Google Checkout'} = $gc);
	($am 		> 0) and ($typeOfPayDpt{'Amazon'} = $am);
	($dl 		> 0) and ($typeOfPayDpt{'Descuentolibre'} = $dl);
	($cod 	> 0) and ($typeOfPayDpt{'COD'} = $cod);
	my $total_deposits 	= $cash+$vmc+$ae+$dc+$pp+$gc+$am+$dl+$cod;	

	return ($total_deposits,$deposits,0);
}


sub payments_predeposit_mov{
#-----------------------------------------
# Created on: 09/16/09  11:51:20 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Time Modified by RB On 03/10/2011: We extract first the ID_preorders with an order in further date than the range
# Note: Evaluate the last date We had a sl_preorders movement so if the from_date value is greater We don't need to do this query anymore 

	return (0,0);

}

#####
##### MODIFICATIONS
#####

sub products_return_mov{
#-----------------------------------------
# Created on: 10/26/09  15:43:31 By  Roberto Barcenas
# Forms Involved: 
# Description : 
# Parameters : 	


	my ($datef,$datet) = @_;
	#SALES
  my $sth = &Do_SQL("SELECT  
				SUM(IF(ID_accounts=41 AND Credebit = 'Credit',Amount,0)) AS AR,
				SUM(IF(ID_accounts=89 AND Credebit = 'Debit',Amount,0)) AS Inventory,
				SUM(IF(ID_accounts=152 AND Credebit = 'Debit',Amount,0)) AS Tax,
				SUM(IF(ID_accounts=170 AND Credebit = 'Debit',Amount,0)) AS Products,
				SUM(IF(ID_accounts=180 AND Credebit = 'Debit',Amount,0)) AS Services,
				SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Fees,
				SUM(IF(ID_accounts=185 AND Credebit = 'Debit',Amount,0)) AS Shipping,
				SUM(IF(ID_accounts=187 AND Credebit = 'Credit',Amount,0)) AS Discounts,
				SUM(IF(ID_accounts=193 AND Credebit = 'Credit',Amount,0)) AS COGS,
				SUM(IF(ID_accounts=327 AND Credebit = 'Credit',Amount,0)) AS CRefund
				FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status) WHERE  ID_accounts IN(41,89,152,170,180,185,187,193,327) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category = 'Return' AND Status = 'Active' ORDER BY ID_accounts;");
  									
	my ($ar,$in,$tax,$prod,$ser,$fees,$shipp,$dis,$cogs,$cref) = $sth->fetchrow();

 return ($ar,$in,$tax,$prod,$ser,$fees,$shipp,$dis,$cogs,$cref);
 
}


sub products_exchange_mov{
#-----------------------------------------
# Created on: 10/26/09  15:43:48 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my ($datef,$datet) = @_;
	#EXCHANGES
  my $sth = &Do_SQL("SELECT  
				SUM(IF(ID_accounts=41 AND Credebit = 'Debit',Amount,0)) AS AR,
				SUM(IF(ID_accounts=89 AND Credebit = 'Credit',Amount,0)) AS Inventory,
				SUM(IF(ID_accounts=152 AND Credebit = 'Credit',Amount,0)) AS Tax,
				SUM(IF(ID_accounts=170 AND Credebit = 'Credit',Amount,0)) AS Products,
				SUM(IF(ID_accounts=180 AND Credebit = 'Credit',Amount,0)) AS Services,
				SUM(IF(ID_accounts=185 AND Credebit = 'Credit',Amount,0)) AS Shipping,
				SUM(IF(ID_accounts=187 AND Credebit = 'Debit',Amount,0)) AS Discounts,
				SUM(IF(ID_accounts=193 AND Credebit = 'Debit',Amount,0)) AS COGS,
				SUM(IF(ID_accounts=327 AND Credebit = 'Debit',Amount,0)) AS CRefund
				FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status) WHERE  ID_accounts IN(41,89,152,170,180,185,187,193,327) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Exchange' AND Status = 'Active' ORDER BY ID_accounts;");
  									
	my ($ar,$in,$tax,$prod,$ser,$shipp,$dis,$cogs,$cref) = $sth->fetchrow();

 return ($ar,$in,$tax,$prod,$ser,$shipp,$dis,$cogs,$cref);
 
}


sub payments_refund_mov{
#-----------------------------------------
# Created on: 10/26/09  15:43:54 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS
	my $sth = &Do_SQL("SELECT 
					SUM(IF(ID_accounts=1,Amount,0)) AS Cash,
					SUM(IF(ID_accounts=12,Amount,0)) AS VMC,
					SUM(IF(ID_accounts=14,Amount,0)) AS Amex,
					SUM(IF(ID_accounts=16,Amount,0)) AS Discover,
					SUM(IF(ID_accounts=20,Amount,0)) AS PayPal,
					SUM(IF(ID_accounts=329,Amount,0)) AS Google,
					SUM(IF(ID_accounts=330,Amount,0)) AS Amazon,
					SUM(IF(ID_accounts=331,Amount,0)) AS Descuentolibre,
					SUM(IF(ID_accounts=22,Amount,0)) AS COD,
					SUM(IF(ID_accounts=327,Amount,0)) AS CRefund
					FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status)
					WHERE  ID_accounts IN(1,12,14,16,20,22,327,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Refund' AND IF(ID_accounts=327,Credebit='Debit',Credebit='Credit') AND Status = 'Active' ORDER BY ID_accounts; ");

	my($cash,$vmc,$ae,$dc,$ppal,$gc,$am,$dl,$cod,$crefund) = $sth->fetchrow;
	($cash 	> 0) and ($typeOfPayRef{'Cash'} = $cash);
	($vmc 	> 0) and ($typeOfPayRef{'Visa/Masterd Card'} = $vmc);
	($ae 		> 0) and ($typeOfPayRef{'American Express'} = $ae);
	($dc 		> 0) and ($typeOfPayRef{'Discover'} = $dc);
	($ppal 	> 0) and ($typeOfPayRef{'PayPal'} = $ppal);
	($gc 	> 0) and ($typeOfPayRef{'Google Checkout'} = $gc);
	($am 	> 0) and ($typeOfPayRef{'Amazon'} = $am);
	($dl 	> 0) and ($typeOfPayRef{'Descuentolibre'} = $dl);
	($cod 	> 0) and ($typeOfPayRef{'COD'} = $cod);
	my $total_refund 	= $cash+$vmc+$ae+$dc+$ppal+$gc+$am+$dl+$cod;

	return ($total_refund,$crefund);
}


sub payments_exchange_mov{
#-----------------------------------------
# Created on: 10/26/09  15:44:04 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($datef,$datet) = @_;
	#CUSTOMER DEPOSITS
	my $sth = &Do_SQL("SELECT 
					SUM(IF(ID_accounts=1,Amount,0)) AS Cash,
					SUM(IF(ID_accounts=12,Amount,0)) AS VMC,
					SUM(IF(ID_accounts=14,Amount,0)) AS Amex,
					SUM(IF(ID_accounts=16,Amount,0)) AS Discover,
					SUM(IF(ID_accounts=20,Amount,0)) AS PayPal,
					SUM(IF(ID_accounts=329,Amount,0)) AS Google,
					SUM(IF(ID_accounts=330,Amount,0)) AS Amazon,
					SUM(IF(ID_accounts=331,Amount,0)) AS Descuentolibre,
					SUM(IF(ID_accounts=22,Amount,0)) AS COD
					FROM sl_movements USE INDEX (ID_accounts,Category,Credebit,EffDate,tableused,Status)
					WHERE  ID_accounts IN(1,12,14,16,20,22,329,330,331) AND EffDate BETWEEN '$datef' AND '$datet' AND tableused='sl_orders' AND Category='Exchange' AND Credebit='Debit' AND Status = 'Active' ORDER BY ID_accounts; ");

	my($cash,$vmc,$ae,$dc,$ppal,$gc,$am,$dl,$cod) = $sth->fetchrow;
	($cash 	> 0) and ($typeOfPayEx{'Cash'} = $cash);
	($vmc 	> 0) and ($typeOfPayEx{'Visa/Masterd Card'} = $vmc);
	($ae 		> 0) and ($typeOfPayEx{'American Express'} = $ae);
	($dc 		> 0) and ($typeOfPayEx{'Discover'} = $dc);
	($ppal 	> 0) and ($typeOfPayEx{'PayPal'} = $ppal);
	($gc 	> 0) and ($typeOfPayEx{'Google Checkout'} = $gc);
	($am 	> 0) and ($typeOfPayEx{'Amazon'} = $am);
	($dl 	> 0) and ($typeOfPayEx{'Descuentolibre'} = $dl);
	($cod 	> 0) and ($typeOfPayEx{'COD'} = $cod);
	my $total_deposits 	= $cash+$vmc+$ae+$dc+$ppal+$gc+$am+$dl+$cod;

	return ($total_deposits);
}


sub fin_showdiff_movements{
#-----------------------------------------
# Created on: 09/09/09  11:04:58 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my ($datef,$datet) = @_;
	my $output = '';


	my ($sth) = &Do_SQL("SELECT tmpdeb.`ID_tableused`,Debits,Credits 
					FROM
					(SELECT `ID_tableused`,SUM(Amount) AS Debits FROM sl_movements USE INDEX (Credebit,EffDate,tableused,Status)
					WHERE `tableused` = 'sl_orders' AND `Credebit`='Debit' AND Status='Active'
					AND `EffDate` BETWEEN '$datef' AND '$datet' GROUP BY `ID_tableused`)AS tmpdeb
					INNER JOIN
					(SELECT `ID_tableused`,SUM(Amount) AS Credits FROM sl_movements USE INDEX (Credebit,EffDate,tableused,Status)
					WHERE `tableused` = 'sl_orders' AND `Credebit`='Credit' AND Status='Active'
					AND `EffDate` BETWEEN '$datef' AND '$datet' GROUP BY `ID_tableused`)AS tmpcre
					ON tmpdeb.`ID_tableused` =  tmpcre.`ID_tableused`
					WHERE ABS(Debits-Credits) > .01
					ORDER BY tmpdeb.`ID_tableused`");

	my $rows = $sth->rows();

	if($rows > 0){
		$output .=qq|
					<li><h3>Debits vs Credits</h3>
					<div>&nbsp;
					<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
						<tr style="background-color:#CDCDC1;">
							<td valign='top' align='left'><strong>ID Orders</strong></td>
							<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
							<td valign='top' align='center' width="15%">&nbsp;</td>
							<td valign='top' align='right'><strong>Credit</strong></td>
						<tr>|;

		$i=0;
		while(my($id_orders,$debit,$credit) = $sth->fetchrow()){
			($i%2 eq 1) and ($stlyetd = 'style="background-color:#EEEEE0;"');
			($i%2 eq 0) and ($stlyetd = '');

			$output .= qq|
						<tr>
							<td valign='top' align='left' $stlyetd><a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$id_orders&tab=15">$id_orders</a></td>
							<td nowrap valign='top' align='right' $stlyetd>|.&format_price($debit) .qq| </td>
							<td $stlyetd>&nbsp;</td>
							<td nowrap valign='top' align='right' $stlyetd>|.&format_price($credit) .qq| </td>
        				</tr>|;
			$i++;
		}
		$output .=qq|
									</table>
									&nbsp;
								</div>
								</li>|;
	} 												

	return $output;											
}


sub fin_zero_movements{
#-----------------------------------------
# Created on: 09/09/09  11:05:06 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my ($datef,$datet) = @_;
	my $output = '';


	my ($sth) = &Do_SQL("SELECT sl_movements.`ID_tableused`,IF(Debits IS NULL,0,Debits) AS Debits,IF(Credits IS NULL,0,Credits) AS Credits 
						FROM sl_movements USE INDEX (EffDate,tableused,Status)  LEFT JOIN
						(SELECT `ID_tableused`,COUNT(*) AS Debits FROM sl_movements USE INDEX (Credebit,EffDate,tableused,Status) 
						WHERE `tableused` = 'sl_orders' AND `Credebit`='Debit' AND Amount=0 AND Status='Active'
						AND `EffDate` BETWEEN '$datef' AND '$datet' GROUP BY `ID_tableused`)AS tmpdeb
						ON sl_movements.ID_tableused = tmpdeb.ID_tableused
						LEFT JOIN
						(SELECT `ID_tableused`,COUNT(*) AS Credits FROM sl_movements USE INDEX (Credebit,EffDate,tableused,Status) 
						WHERE `tableused` = 'sl_orders' AND `Credebit`='Credit' AND Amount=0 AND Status='Active'
						AND `EffDate` BETWEEN '$datef' AND '$datet' GROUP BY `ID_tableused`)AS tmpcre
						ON sl_movements.`ID_tableused` =  tmpcre.`ID_tableused`
						WHERE sl_movements.`tableused` = 'sl_orders' AND sl_movements.Amount = 0 
						AND `EffDate` BETWEEN '$datef' AND '$datet' AND sl_movements.Status='Active'
						GROUP BY sl_movements.ID_tableused ORDER BY sl_movements.`ID_tableused`");

	my $rows = $sth->rows();

	if($rows > 0){
$output .=qq|
			<li><h3>Debits/Credits Amount in Zero</h3>
			<div>&nbsp;
			<table width="80%" border="0" cellspacing="0" cellpadding="0" align="center">
				<tr>
					<td colspan="3" align="center"><a name="azero" id="azero">&nbsp;</a>
				</tr>
				<tr style="background-color:#CDCDC1;">
					<td valign='top' align='left'><strong>ID Orders</a></strong></td>
					<td valign='top' align='right'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Debit</strong></td>
					<td valign='top' align='center' width="15%">&nbsp;</td>
					<td valign='top' align='right'><strong>Credit</strong></td>
				<tr>|;

		$i=0;
		while(my($id_orders,$debit,$credit) = $sth->fetchrow()){
			($i%2 eq 1) and ($stlyetd = 'style="background-color:#EEEEE0;"');
			($i%2 eq 0) and ($stlyetd = '');

			$output .= qq|
							<tr>
								<td valign='top' align='left' $stlyetd>
									<!--<a href="javascript:return false();" onClick="edit_movements();">-->$id_orders<!--</a>-->&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
									<a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$id_orders&tab=15">$id_orders</a>
								</td>
								<td nowrap valign='top' align='right' $stlyetd>$debit</td>
								<td $stlyetd>&nbsp;</td>
								<td nowrap valign='top' align='right' $stlyetd>$credit</td>
        					</tr>|;
			$i++;
		}
		$output .=qq|
									</table>
									&nbsp;
								</div>
								</li>|;
	} 												

	return $output;											
}


sub fin_report_debitscredits{
#-----------------------------------------
# Created on: 09/09/09  11:05:19 By  Roberto Barcenas
# Forms Involved: 
# Description : Muestra las ordenes/con errores en debits vs credits
# Parameters : 	
#Last modified on 13 Jul 2011 17:11:57
#Last modified by: MCC C. Gabriel Varela S. :The second query had > instead of >= . The "order by" clausule is deleted in the first query, since it only is a count. The date is going to be 3 months maximum

	### Solamente visible por developers y miembros de finanzas
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements_dvc");
	$va{'matches'} = $sth->fetchrow();

	if($va{'matches'} > 0){
		my (@c) = split(/,/,$cfg{'srcolors'});

		if(!$in{'print'}){
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			$modquery = "LIMIT $first,$usr{'pref_maxh'}";
		}else{
			$va{'pageslist'} =1;
			$modquery = "";
		}

		my ($sth) = &Do_SQL("SELECT * FROM sl_movements_dvc ORDER BY Difference DESC $modquery ;");

		$script_url =~	s/admin$/dbman/;
		while(my($id,$id_orders,$debits,$credits,$diff) = $sth->fetchrow()){
			$d = 1 - $d;
			my $linkorder = '';
			my $stred = '';
			my $date=&load_name('sl_orders','ID_Orders',$id_orders,'Date');

			if(!$in{'print'}){
				$linkorder = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders#tabs" title="View Order">$id_orders</a>|;
			}else{
				$linkorder = "$id_orders";
			}

			$stred= 'style="color:red;"'	if $diffo > 0;

			$va{'searchresults'} .= qq|
								<tr bgcolor="|.$c[$d].qq|" onmouseover="m_over(this)" onmouseout="m_out(this)">
									<td align="left">$linkorder</td>
									<td align="left">$date</td>
									<td align="right">|.&format_price(round($debits,2)).qq|</td>
									<td align="right">|.&format_price(round($credits,2)).qq|</td>
									<td align="right" $stred>|.&format_price(round($diff,2)).qq|</td>
								</tr>|;
		}
	}


	print "Content-type: text/html\n\n";
	if($in{'print'}){
		print &build_page('fin_debitscredits_print.html');
	}else{	
		print &build_page('fin_debitscredits_list.html');
	}
}


#   Function: fin_ccbonus_dn
#
#   This function shows files reporting callcenter operator bonuses for each biweeky period.
#   Note: Files over NFS directory in S3
#
#   Parameters:
#
#      None
#
#   Returns:
#
#      Creates a variable containing the csv files listing
#
#   See Also:
#
#      None
sub fin_ccbonus_dn {

	if($in{'dn'}>0){
		print "Content-type: application/octetstream\n";
		print "Content-disposition: attachment; filename=".&load_db_names('sl_rewards_logs','ID_rewards_logs',$in{'dn'},'ccbonus_[fromdate]_to_[todate]').".csv\n\n";
		if (open(XLS, "<$cfg{'path_upfiles'}/files_s3/ccbonus/$in{'dn'}.csv")){
			print <XLS>;
			close XLS;
		}
		return;
	}


	my ($n) = 1;
	my ($sth) = &Do_SQL("SELECT * FROM sl_rewards_logs ORDER BY ID_rewards_logs DESC");
	my ($total)=$sth->rows();
	while ($rec = $sth->fetchrow_hashref() ) {
		($n==1) and ($va{'reports'} .= "<tr>");
		$info = "  $rec->{'FromDate'} -> $rec->{'ToDate'}<br>Created on: $rec->{'Date'} $rec->{'Time'}";

		++$n;
		if (-e "$cfg{'path_upfiles'}/files_s3/ccbonus/$rec->{'ID_rewards_logs'}.csv"){
			$va{'reports'} .= "<td class='smalltxt' align='center'><a href='/cgi-bin/mod/admin/admin?cmd=fin_ccbonus_dn&dn=$rec->{'ID_rewards_logs'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xls.gif'></a>$info</td>";
		}

		if ($n>4){
			$va{'reports'} .= "</tr>";
			$n=1;
		}
	}
	if ($total==0){
		$va{'reports'} = "<td class='smalltxt' align='center'>". &trans_txt('notmatch'). "</td>";
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_ccbonus_dn.html');    
}


###################################################################################
###################################################################################
#	Function: fin_reports_amazon
#
#  	List orders by Amazon
#
#	Created by: _Alejandro Diaz_
#
#	Modified By:
#
#   Parameters:
#		- date_from: Date From
#		- date_to: Date To
#		- shippedby: Shipped by
#
#   Returns:
#
#   See Also: None
#
sub fin_reports_amazon {
###################################################################################
###################################################################################

	if($in{'action'} == 1){

		if($in{'from_date'}) {
			$va{'descfilters'} .= qq|
				<tr>
    				<td class="smalltext">From date:</td>
    				<td class="smalltext">|.$in{'from_date'}.qq|</td>
    			</tr>\n|;
		}

		if($in{'to_date'}) {
			$va{'descfilters'} .= qq|
				<tr>
    				<td class="smalltext">To date:</td>
    				<td class="smalltext">|.$in{'to_date'}.qq|</td>
    			</tr>\n|;
		}

		my $desc_shipped_by = "All";
		my $filter_type = '';
		if($in{'shipped_by'}) {
			$desc_shipped_by = $in{'shipped_by'} == 1 ? " Amazon FBA" : " by Direksys";
			$filter_type = $in{'shipped_by'} == 1 ? " AND tmp.ID_orders IS NOT NULL " : " AND tmp.ID_orders IS NULL ";
		}

		$va{'descfilters'} .= qq|
				<tr>\n
    				<td class="smalltext">Fulfilled by:</td>\n
    				<td class="smalltext">|.$desc_shipped_by.qq|</td>\n
    			</tr>\n
				<tr>\n
    				<td class="smalltext">Created by :</td>\n
    				<td class="smalltext">[ur_ID_admin_users] - [ur_FirstName] [ur_LastName]</td>\n
    			</tr>\n|;		

		$usr{'pref_maxh'} = 30;
		my $filterX='';
		my $filterY='';
		my $filterZ='';
		$filterX .= $in{'from_date'} ? " AND  sl_orders.Date >= '".&filter_values($in{'from_date'})."'" : " AND  sl_orders.Date >= CURDATE()";
		$filterX .= $in{'to_date'} ? " AND  sl_orders.Date <= '".&filter_values($in{'to_date'})."'" : " AND  sl_orders.Date <= CURDATE()";

		$filterY .= $in{'from_date'} ? " AND  sl_orders_products.Date >= '".&filter_values($in{'from_date'})."'" : " AND  sl_orders_products.Date >= CURDATE()";
		$filterY .= $in{'to_date'} ? " AND  sl_orders_products.Date <= '".&filter_values($in{'to_date'})."'" : " AND  sl_orders_products.Date <= CURDATE()";

		$filterZ .= $in{'from_date'} ? " AND  sl_orders_notes.Date >= '".&filter_values($in{'from_date'})."'" : " AND  sl_orders_notes.Date >= CURDATE()";
		$filterZ .= $in{'to_date'} ? " AND  sl_orders_notes.Date <= '".&filter_values($in{'to_date'})."'" : " AND  sl_orders_notes.Date <= CURDATE()";


		$modfba .=  " LEFT JOIN (
								SELECT 
									ID_orders 
								FROM 
									sl_orders_notes 
								WHERE 
									Notes = 'The Order has been Fulfilled and Shipped by Amazon' 
								GROUP BY 
									ID_orders
								)tmp 
						USING(ID_orders) ";



		my $query="SELECT COUNT(*) FROM sl_orders_notes
					$modfba WHERE Type='AmazonID' $filterZ 
					$filter_type"; 

		my ($sth) = &Do_SQL($query);
		$va{'matches'} = $sth->fetchrow();

		if($va{'matches'} > 0){
			my (@c) = split(/,/,$cfg{'srcolors'});


			if(!$in{'print'} and !$in{'export'}){

				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin", $va{'matches'}, $usr{'pref_maxh'});
				$va{'qs'} = $qs;
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
				$modquery = "LIMIT $first, $usr{'pref_maxh'}";
			}else{
				$va{'pageslist'} =1;
				$modquery = "";
			}

			$query="SELECT 
				sl_orders.ID_orders
				, IF(tmp.ID_orders IS NULL,'Direksys','Amazon') AS FulfilledBy
				, sl_orders.Date
				, sl_orders_notes.Notes AS AmazonID
				, CONCAT( FirstName,' ', LastName1)AS Name
				, Saleprice
				, Shipping
				, Tax				
				FROM sl_orders
				INNER JOIN sl_orders_notes USING(ID_orders)
				INNER JOIN sl_customers USING(ID_customers)
				INNER JOIN 
				(
					SELECT 
						ID_orders,
						SUM(Saleprice)AS Saleprice,
						SUM(Shipping)AS Shipping,
						SUM(Tax)AS Tax
					 FROM sl_orders_products
					 WHERE Saleprice > 0
					 AND Status = 'Active'
					".$filterY."
					GROUP BY ID_orders
				)tmp2
				USING(ID_orders)
				$modfba WHERE sl_orders_notes.Type='AmazonID' 
				".$filterX . $filter_type ." 
				GROUP BY sl_orders.ID_orders $modquery;";


			$sth=&Do_SQL($query);
			while($rec=$sth->fetchrow_hashref){			

				$script_url =~ s/admin$/dbman/;
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]'>
						<td class='smalltext' valign='top'><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}">$rec->{'ID_orders'}</a></td>
						<td class='smalltext' valign='top' align='left'>$rec->{'FulfilledBy'}</td>
						<td class='smalltext' valign='top'>$rec->{'Date'}</td>
						<td class='smalltext' valign='top'>$rec->{'AmazonID'}</td>
						<td class='smalltext' valign='top'>$rec->{'Name'}</td>
						<td class='smalltext' valign='top' align='right'>$rec->{'Saleprice'}</td>
						<td class='smalltext' valign='top' align='right'>$rec->{'Shipping'}</td>
						<td class='smalltext' valign='top' align='right'>$rec->{'Tax'}</td>
					</tr>\n|;
			}
		}else {

			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='9' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		if($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('fin_reports_amazon_print.html');

		}elsif($in{'export'}){

			@cols = ('ID orders','Fulfilled By','Date','Amazon ID','Customer','Saleprice','Shipping','Tax');
			print "Content-type: application/vnd.ms-excel\n";
			print "Content-disposition: attachment; filename=fin_report_amazon.csv\n\n";
			print '"'.join('","', @cols)."\"\n";
			$query_list   = $query;
			my ($sth) = &Do_SQL($query_list);
			while (@ary = $sth->fetchrow_array){
				print '"'.join('","', @ary)."\"\n";
			}
			return;

		}else{

			print "Content-type: text/html\n\n";
			print &build_page('fin_reports_amazon_list.html');

		}

	}else{
		print "Content-type: text/html\n\n";
		print &build_page('fin_reports_amazon.html');
	}

}



sub fin_reconcile{
#-----------------------------------------
# Created on: 5/16/2013 2:51:48 PM By  	carlos haas
# Forms Involved: 
# Description :
# Parameters :

	$va{'select_bank'} = '';
	my ($sth) = &Do_SQL("SELECT ID_banks, SubAccountOf, Name FROM sl_banks;");
	while ($rec = $sth->fetchrow_hashref) {
		$va{'select_bank'} .= qq|<option value="$rec->{'ID_banks'}">$rec->{'Name'} / $rec->{'SubAccountOf'}</option>|;
	}
	if ($in{'action'}){
		my ($err);
		$in{'id_banks'} = int($in{'id_banks'} );
		$in{'balance'} = $in{'balance'}*1;
		#&setCookie('mi_cookie1','valor_mi_cookie1',365,'mi_color1');
		
		
		if ($in{'exct_id'}) {
			#cgierr(&GetCookies());
			my @exct_ids = split /\|/, $in{'exct_id'};
			my @exct_linked_ids = split /\|/, $in{'exct_linked_id'};

			for my $i (0..$#exct_ids) {
				if ($exct_linked_ids[$i] > 0) {
					if ($exct_linked_ids[$i] =~ m/\,/) {
						my @aux_linked_ids = split /\,/, $exct_linked_ids[$i];
						
						my ($sth_amount_bm) = &Do_SQL("SELECT SUM(Amount) as total_amount, BankDate, Type FROM sl_banks_movements WHERE ID_banks_movements IN($exct_linked_ids[$i]) AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00') GROUP BY ID_banks;");
						my $date_amount_bm = $sth_amount_bm->fetchrow_hashref;
						my ($sth_select_bs) = &Do_SQL("SELECT BankDate, Amount, Type FROM sl_bank_statements WHERE ID_bank_statements=$exct_ids[$i] AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00');");
						my $date_amount_bs = $sth_select_bs->fetchrow_hashref;
						
						if (((($date_amount_bm->{'total_amount'} - $date_amount_bs->{'Amount'}) < 0.2) and
							(($date_amount_bm->{'total_amount'} - $date_amount_bs->{'Amount'}) > -0.2)) and
							($date_amount_bm->{'BankDate'} eq $date_amount_bs->{'BankDate'} and
							 $date_amount_bm->{'Type'} eq $date_amount_bs->{'Type'})) {
							
							for my $j (0..$#aux_linked_ids) {
								my ($sth) = &Do_SQL("UPDATE sl_banks_movements SET ConsDate=CURDATE(),ID_bank_statements='$exct_ids[$i]' WHERE ID_banks_movements=$aux_linked_ids[$j] AND ID_banks=$in{'id_banks'} LIMIT 1;");
							}
							my ($sth) = &Do_SQL("UPDATE sl_bank_statements SET ConsDate=CURDATE() WHERE ID_bank_statements=$exct_ids[$i] AND ID_banks=$in{'id_banks'} LIMIT 1;");
							
						} else {
							$va{'message'} = 'The amount, date or type does not match';
							last;
						}
						
					} else {
						my ($sth_select_bm) = &Do_SQL("SELECT BankDate, Amount, Type FROM sl_banks_movements WHERE ID_banks_movements=$exct_linked_ids[$i] AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00');");
						my $date_amount_bm = $sth_select_bm->fetchrow_hashref;
						my ($sth_select_bs) = &Do_SQL("SELECT BankDate, Amount, Type FROM sl_bank_statements WHERE ID_bank_statements=$exct_ids[$i] AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00');");
						my $date_amount_bs = $sth_select_bs->fetchrow_hashref;
						
						if ($date_amount_bm->{'BankDate'} eq $date_amount_bs->{'BankDate'} and $date_amount_bm->{'Amount'} == $date_amount_bs->{'Amount'} and $date_amount_bm->{'Type'} eq $date_amount_bs->{'Type'}) {
							my ($sth) = &Do_SQL("UPDATE sl_banks_movements SET ConsDate=CURDATE(), ID_bank_statements='$exct_ids[$i]' WHERE ID_banks_movements=$exct_linked_ids[$i] AND ID_banks=$in{'id_banks'} LIMIT 1;");
							my ($sth) = &Do_SQL("UPDATE sl_bank_statements SET ConsDate=CURDATE() WHERE ID_bank_statements=$exct_ids[$i] AND ID_banks=$in{'id_banks'} LIMIT 1;");
						} else {
							$va{'message'} = 'The amount, date or type does not match';
							last;
						}
						
					}
					
				}
			}
			$va{'message'} = 'The bank reconciliation ran successfully';
			print "Content-type: text/html\n\n";
			print &build_page('fin_reconcile.html');
			return;
		}
		
		
		if (0 and $in{'con_amounts'}) {
			#cgierr(&GetCookies());
			my @idbanksmovementsval = split /\|/, $in{'con_idbanksmovements'};
			my @idselectedval = split /\|/, $in{'con_idselected'};

			for my $i (0..$#idselectedval) {
				if ($idselectedval[$i] > 0) {
					my ($sth) = &Do_SQL("UPDATE sl_banks_movements SET ConsDate=CURDATE() WHERE ID_banks_movements=$idselectedval[$i] AND ID_banks=$in{'id_banks'} LIMIT 1;");
				}
			}
		}
		
		
		if (!$in{'id_banks'}){
			++$err;
			$error{'id_banks'}  = &trans_txt('required')
		}
		
		#if (!$in{'balance'}){
		#	++$err;
		#	$error{'balance'}  = &trans_txt('required')
		#}
		
		if (!$in{'from_date'}){
			++$err;
			$error{'from_date'}  = &trans_txt('required')
		}
		if (!$err){
			&fin_reconcile_list;
			return;
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_reconcile.html');										
}

sub fin_reconcile_list{
#-----------------------------------------
# Created on: 5/16/2013 2:51:48 PM By  	carlos haas
# Forms Involved: 
# Description :
# Parameters : 	

	$va{'total_balance_amount'} = 0;
	$va{'debit_amount'} = 0;
	$va{'credit_amount'} = 0;
	my $start_date = '2013-06-01';
	## Previus Balance
	#load_name('sl_banks','ID_banks',$in{'id_banks'},'OpeningBalance');
	my ($sth_banks) = &Do_SQL("SELECT SubAccountOf, Name FROM sl_banks WHERE ID_banks = '$in{'id_banks'}';");
	my $rec_banks = $sth_banks->fetchrow_hashref;
	$va{'bank_name'} = $rec_banks->{'Name'};
	$va{'bank_account'} = $rec_banks->{'SubAccountOf'};
	
	my $balance = 0;
	my $balance_aut_recon = 0;
	my ($sth) = &Do_SQL("SELECT SUM(IF(Type='Debits',Amount,-Amount)) AS Total,MAX(ConsDate) FROM sl_banks_movements WHERE ConsDate AND ID_banks=$in{'id_banks'}");
	($va{'prev_balance'}, $va{'prev_balance_date'}) = $sth->fetchrow_array();
	$va{'prev_balance'} += &load_name('sl_banks','ID_banks',$in{'id_banks'},'OpeningBalance');
	$va{'prev_balance_fmt'}  = &format_price($va{'prev_balance'});
	$va{'new_balance_fmt'}   = &format_price($in{'balance'});
	
	$va{'difference'} = $va{'prev_balance'} + $in{'balance'};

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_banks_movements WHERE BankDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00') AND ID_banks=$in{'id_banks'}");
	$va{'matches'} = $sth->fetchrow();
	$va{'pageslist'} = 1;

	my ($sth) = &Do_SQL("SELECT sl_banks_movements.*,
						(SUBSTRING( SUBSTRING(sl_banks_movements_notes.Notes, LOCATE('[|',sl_banks_movements_notes.Notes) + 2), 1, CHAR_LENGTH( SUBSTRING(sl_banks_movements_notes.Notes, LOCATE('[|',sl_banks_movements_notes.Notes) + 2)) - 3 )) as Clasification
						FROM sl_banks_movements
						LEFT JOIN sl_banks_movements_notes on ( sl_banks_movements.ID_banks_movements = sl_banks_movements_notes.ID_banks_movements AND Notes LIKE 'Carga automatica%' )
						WHERE (BankDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}') AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00') AND ID_banks=$in{'id_banks'} ORDER BY BankDate ASC;");
	
	# ************************************************************************************************************************************
	# Opening balance and closing balance
	my $only_reconciled = 0;
	my $opening_amount = &calculate_opening_amount($in{'id_banks'},$start_date,$in{'from_date'},$only_reconciled);
	my $opening_balance = &load_name('sl_banks','ID_banks',$in{'id_banks'},'OpeningBalance') + $opening_amount;
	my $closing_amount = &calculate_closing_amount($in{'id_banks'},$start_date,$in{'to_date'},$only_reconciled);
	my $closing_balance = $opening_balance + $closing_amount;
	
	$only_reconciled = 1;
	my $opening_amount_or = &calculate_opening_amount($in{'id_banks'},$start_date,$in{'from_date'},$only_reconciled);
	my $opening_balance_or = &load_name('sl_banks','ID_banks',$in{'id_banks'},'OpeningBalance') + $opening_amount_or;
	my $closing_amount_or = &calculate_closing_amount($in{'id_banks'},$start_date,$in{'to_date'},$only_reconciled);
	my $closing_balance_or = $opening_balance + $closing_amount_or;
	
	$va{'opening_balance'} = $opening_balance;
	$va{'opening_balance_or'} = $opening_balance_or;
	$va{'closing_balance'} = $closing_balance;
	$va{'closing_balance_or'} = $closing_balance_or;
	
	$va{'amount_o'} = $opening_amount;
	$va{'amount_c'} = $closing_amount;
	$va{'amount_or'} = $opening_amount_or;
	$va{'amount_cor'} = $closing_amount_or;
	$va{'op_balance'} = &load_name('sl_banks','ID_banks',$in{'id_banks'},'OpeningBalance');
	$va{'balance_aut_recon'} = '';
	$va{'ids_amounts'} = '';
	# ************************************************************************************************************************************
	$balance = $opening_balance;
	$balance_aut_recon = $opening_balance;
	# ************************************************************************************************************************************
	while ($rec = $sth->fetchrow_hashref){
		
		if ($rec->{'Type'} eq 'Credits'){
			$rec->{'Amount_credit'} = $rec->{'Amount'};
			$rec->{'Amount_debit'} = 0;
			$rec->{'Amount'} = -$rec->{'Amount'};
		}else{
			$rec->{'Amount_debit'} = $rec->{'Amount'};
			$rec->{'Amount_credit'} = 0;
			
		}
		$va{'ids_amounts'} .= qq|$rec->{'ID_banks_movements'} : $rec->{'Amount'},|;
		
		$balance += ($rec->{'Amount_debit'} - $rec->{'Amount_credit'});
		
		$va{'searchresults'} .= qq|
			<tr>
				<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}" name="a_id_mments">$rec->{'ID_banks_movements'}</a></td>
				<td>$rec->{'BankDate'}</td>
				<td>$rec->{'Refnum'}</td>
				<td>$rec->{'Memo'}</td>
				<td align="right" nowrap>|.&format_price($rec->{'Amount_debit'}).qq|</td>
				<td align="right" nowrap>|.&format_price($rec->{'Amount_credit'}).qq|</td>
				<td align="right" nowrap>
					<input type="hidden" name="con_idbanksmovements" value="|.$rec->{'ID_banks_movements'}.qq|" />
					<input type="hidden" name="con_idselected" value="" />
					<input type="hidden" name="con_amounts" value="|.($rec->{'Amount_debit'} - $rec->{'Amount_credit'}).qq|" />
					|.&format_price($balance).qq|</td>
				<td align="right" nowrap>
					$rec->{'Clasification'}
				</td>
				<td align="center" nowrap>
				<!--
				<input type="checkbox" class="checkbox" OnClick="update_balance()" name="amount_ok" value="$rec->{'Amount'}">
				-->
				</td>
			</tr>\n|;
	}
	$va{'total_balance'} = $balance;
	$va{'ids_amounts'} =   '{'.substr($va{'ids_amounts'}, 0, -1).'}';
	# ************************************************************************************************************************************
	# Banking extracts
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bank_statements WHERE BankDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate = '' OR ConsDate = '0000-00-00');");
	$va{'ext_matches'} = $sth->fetchrow();
	
	if ($va{'ext_matches'} > 0) {
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_bank_statements WHERE BankDate BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' AND ID_banks=$in{'id_banks'} AND (ConsDate IS NULL OR ConsDate = '' OR ConsDate = '0000-00-00') ORDER BY BankDate ASC;");
		while ($rec = $sth->fetchrow_hashref){
			if ($rec->{'Type'} eq 'Credits'){
				$rec->{'Amount_credit'} = $rec->{'Amount'};
				$rec->{'Amount_debit'} = 0;
				$rec->{'Amount'} = -$rec->{'Amount'};
			}else{
				$rec->{'Amount_debit'} = $rec->{'Amount'};
				$rec->{'Amount_credit'} = 0;
			}
			$va{'total_balance_amount'} += -1 * $rec->{'Amount_credit'} + $rec->{'Amount_debit'};
			$va{'debit_amount'} += $rec->{'Amount_debit'};
			$va{'credit_amount'} += $rec->{'Amount_credit'};
			my ($matched_ids,$matched_lines) = &reconcilable_mments($in{'id_banks'},$rec->{'BankDate'},$rec->{'Amount'},$rec->{'Type'},$rec->{'ID_bank_statements'});
			my $arrow_down = qq|<img src="$va{'imgurl'}/$usr{'pref_style'}/arr.down.gif" title="Show related movements" style="cursor:pointer;" name="show_rel_mments" lang="$rec->{'ID_bank_statements'}" altsrc="$va{'imgurl'}/$usr{'pref_style'}/arr.up.gif"  />| if($matched_ids =~ m/\,/);
			my $empty_span = qq|<img src="$va{'imgurl'}/$usr{'pref_style'}/null.gif" width="15" />| if(length($arrow_down) == 0);
			$matched_ids = '' if($matched_ids =~ m/\,/);
			
			if ( $matched_ids > 0) {
				$balance_aut_recon += $rec->{'Amount_debit'} - $rec->{'Amount_credit'};
			}
			
			
			$va{'extracts'} .= qq|
				<tr>
					<td>$rec->{'ID_bank_statements'}</td>
					<td>$rec->{'BankDate'}</td>
					<td>$rec->{'Refnum'}</td>
					<td>$rec->{'Memo'}</td>
					<td align="right" nowrap>|.&format_price($rec->{'Amount_debit'}).qq|</td>
					<td align="right" nowrap>|.&format_price($rec->{'Amount_credit'}).qq|</td>
					<td align="right" nowrap>
						
						|.&format_price($rec->{'Balance'}).qq|</td>
					<td align="right" nowrap>
						<input type="hidden" name="exct_id" value="$rec->{'ID_bank_statements'}" />
						<input type="text" name="exct_linked_id" value="|.$matched_ids.qq|" disabled="disabled" />
						<img src="$va{'imgurl'}/$usr{'pref_style'}/b_edit.png" title="Relate to movement" style="cursor:pointer;" name="ed_rel_ids" />
						$arrow_down
						$empty_span
					</td>
					<td align="center" nowrap>
						<input type="hidden" name="banking_exct_amount" value="|.($rec->{'Amount_debit'} - $rec->{'Amount_credit'}).qq|" />
						<!--
						<input type="checkbox" value="$rec->{'Amount'}" name="exct_amount_ok" onclick="select_int_movement(this);" class="checkbox" />
						-->
					</td>
				</tr>
				$matched_lines
				\n|;
		}
		&format_price();
		$va{'total_balance_amount'} = &format_price($va{'total_balance_amount'});
		$va{'debit_amount'} = &format_price($va{'debit_amount'});
		$va{'credit_amount'} = &format_price($va{'credit_amount'});
		$va{'balance_aut_recon'} = $balance_aut_recon;
	}
	
	
	print "Content-type: text/html\n\n";
	print &build_page('fin_reconcile_list.html');		
}
sub calculate_opening_amount{
	my $id_banks = $_[0];
	my $start_date = $_[1];
	my $from_date = $_[2];
	if ( $_[3] eq 1 ) {
		
		my ($sth_opening_amount) = &Do_SQL("SELECT SUM(IF(Type='Credits', -1 * Amount, Amount)) as total_amount FROM sl_banks_movements WHERE (BankDate <= '$from_date' AND BankDate >= '$start_date') AND ID_banks=$id_banks AND (ConsDate IS NOT NULL OR ConsDate != '' OR ConsDate != '0000-00-00') GROUP BY ID_banks;");
		my $opening_amount = $sth_opening_amount->fetchrow();
		return $opening_amount;
		
	} else {
		
		my ($sth_opening_amount) = &Do_SQL("SELECT SUM(IF(Type='Credits', -1 * Amount, Amount)) as total_amount FROM sl_banks_movements WHERE (BankDate <= '$from_date' AND BankDate >= '$start_date') AND ID_banks=$id_banks GROUP BY ID_banks;");
		my $opening_amount = $sth_opening_amount->fetchrow();
		return $opening_amount;
		
	}
	
	
}
sub calculate_closing_amount{
	my $id_banks = $_[0];
	my $start_date = $_[1];
	my $to_date = $_[2];
	if ( $_[3] eq 1 ) {
		
		my ($sth_closing_amount) = &Do_SQL("SELECT SUM(IF(Type='Credits', -1 * Amount, Amount)) as total_amount FROM sl_banks_movements WHERE BankDate <= '$to_date' AND BankDate >= '$start_date' AND ID_banks=$id_banks  AND (ConsDate IS NOT NULL OR ConsDate != '' OR ConsDate != '0000-00-00') GROUP BY ID_banks;");
		my $closing_amount = $sth_closing_amount->fetchrow();
		return $closing_amount;
		
	} else {
		
		my ($sth_closing_amount) = &Do_SQL("SELECT SUM(IF(Type='Credits', -1 * Amount, Amount)) as total_amount FROM sl_banks_movements WHERE BankDate <= '$to_date' AND BankDate >= '$start_date' AND ID_banks=$id_banks GROUP BY ID_banks;");
		my $closing_amount = $sth_closing_amount->fetchrow();
		return $closing_amount;
		
	}
}
sub reconcilable_mments {
	my $id_banks = $_[0];
	my $bank_date = $_[1];
	my $bank_amount = abs($_[2]);
	my $type = $_[3];
	my $id_stment= $_[4];
	my $recon_lines = '';
	my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_banks_movements) as ids FROM sl_banks_movements WHERE Type='$type' AND BankDate = '$bank_date' AND Amount = '$bank_amount' AND ID_banks='$id_banks' AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00');");
	my $hashref_movements = $sth->fetchrow_hashref();
	
	my ($sth2) = &Do_SQL("SELECT ID_banks_movements,Memo,Type,BankDate,Amount,RefNum,RefNumCustom FROM sl_banks_movements WHERE Type='$type' AND BankDate = '$bank_date' AND Amount = '$bank_amount' AND ID_banks='$id_banks' AND (ConsDate IS NULL OR ConsDate='' OR ConsDate='0000-00-00');");
	
	while ($hashref_movements2 = $sth2->fetchrow_hashref){
		$recon_lines .= qq|	<tr style="display: none;" name="recon_lines_$id_stment">
								<td colspan="9" >
								ID: $hashref_movements2->{'ID_banks_movements'} Type: $hashref_movements2->{'Type'} Date: $hashref_movements2->{'BankDate'} Amount: $hashref_movements2->{'Amount'} Ref1: $hashref_movements2->{'RefNum'} Ref2: $hashref_movements2->{'RefNumCustom'} Memo: $hashref_movements2->{'Memo'} <img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" title="Relate" style="cursor:pointer;" name="show_rel_mments" lang="$id_stment" />
								</td>
							</tr>|;
	}
	
	return ($hashref_movements->{'ids'},$recon_lines);
}

sub fin_make_checks{
#-----------------------------------------

	my (@c) = split(/,/,$cfg{'srcolors'});

	my ($sth) = &Do_SQL("SELECT SUM( Amount ) , COUNT( * ) FROM `sl_bills` WHERE STATUS = 'Processed'");
	($va{'newbills'},$va{'newbills_qty'}) = $sth->fetchrow_array();
	$va{'newbills'} = &format_price($va{'newbills'});

	my ($sth) = &Do_SQL("SELECT SUM( Amount ) , COUNT( * ) FROM `sl_bills` WHERE STATUS = 'Partly Paid'");
	($va{'ppbills'},$va{'ppbills_qty'}) = $sth->fetchrow_array();
	$va{'ppbills'} = &format_price($va{'ppbills'});


	#######################
	#### Bank List
	#######################
	my ($sth) = &Do_SQL("SELECT sl_banks.ID_banks,CONCAT(Name,' (',RIGHT(`ABA-ACH`,4), ')') as N,`OpeningBalance`,
							SUM(IF(Type='Debits',Amount,-Amount))+OpeningBalance AS Balance,
							IF (ConsDate,
							SUM(IF(Type='Debits',Amount,-Amount)) ,0)+OpeningBalance AS CBalance
							FROM `sl_banks` 
							LEFT JOIN sl_banks_movements ON sl_banks.ID_banks=sl_banks_movements.ID_banks 
							WHERE Status='Active'
							GROUP BY sl_banks.ID_banks");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$va{'bankslists'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td class='smalltext'><a <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks&view=$rec->{'ID_banks'}"><span  class='smalltext'>$rec->{'N'}</span></a></td>
				<td class='smalltext' align="right">|.&format_price($rec->{'Balance'}).qq|</td>
				<td class='smalltext' align="right">|.&format_price($rec->{'CBalance'}).qq|</td>
			</tr>\n|;
	}
	my ($q_status,$showlist);
	if(!$in{'status'}){
		$q_status = " IN ('Processed','Partly Paid')";
	}else{
		$q_status = " = '$in{'status'}' ";
	}

	if ($in{'byvendors'}){
		$va{'tab_vendors'} = 'selected' if ($in{'status'} eq 'Processed');
		$va{'tab_ppvendors'} = 'selected' if ($in{'status'} eq 'Partly Paid');
		$va{'tab_avendors'} = 'selected' if (!$in{'status'});
		$va{'bills_style'} = "display:none";
		#######################
		#### BY VENDORS List
		#######################

		my ($sth) = &Do_SQL("SELECT sl_bills.*, CompanyName, sl_vendors.Currency AS VCurrency, POTerms ,
				SUM(Amount) AS TDue, COUNT(*) AS Tqty
				FROM sl_bills LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=sl_bills.ID_vendors
				WHERE sl_bills.Status $q_status GROUP BY sl_vendors.ID_vendors ORDER BY sl_bills.ID_bills,DueDate ASC");
		$va{'matches'} = $sth->rows();
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'total'} += $rec->{'TDue'};
			my $amount_due = &bills_amount_due_by_vendor($rec->{'ID_vendors'});
			$va{'total_due'} += $amount_due;
			$showlist=1;
			($line<$first) and ($showlist=0);
			($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
			++$line;
			if ($showlist){

				$va{'byvendors_list'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td class='smalltext'>
					 <a href="/cgi-bin/mod/admin/admin?cmd=mer_bills_payments&amp;id_vendors=$rec->{'ID_vendors'}" ><img src="[va_imgurl]/[ur_pref_style]/b_cauth.gif" title="Pay" alt="Pay" border="0"></a>
					</td>
					<td class='smalltext' align='right'><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}"><span  class='smalltext'>$rec->{'ID_vendors'}</span></a></td>
					<td class='smalltext'>$rec->{'CompanyName'}</td>
					<td class='smalltext' align='right'>|.$rec->{'Tqty'}.qq|</td>
					<td class='smalltext' align='right'>|.&format_price($rec->{'TDue'}).qq|</td>
					<td class='smalltext' align='right'>|.&format_price($amount_due).qq|</td>
					<td class='smalltext' align='center'>$rec->{'VCurrency'}</td>
				</tr>\n|;
			}
		}
		$va{'total'} = &format_price($va{'total'});
		$va{'total_due'} = &format_price($va{'total_due'});
		if (!$va{'byvendors_list'}){
			$va{'pageslist'} = 1;
			$va{'byvendors_list'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}else{
		#######################
		#### Bills List
		#######################
		$va{'tab_bills'} = 'selected' if ($in{'status'} eq 'Processed');
		$va{'tab_ppbills'} = 'selected' if ($in{'status'} eq 'Partly Paid');
		$va{'tab_abills'} = 'selected' if (!$in{'status'});
		$va{'vendors_style'} = "display:none";

		my ($sth) = &Do_SQL("SELECT sl_bills.*, CompanyName, sl_vendors.Currency AS VCurrency, POTerms ,
				DATEDIFF(CURDATE(),DueDate) AS DDays
				FROM sl_bills LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=sl_bills.ID_vendors
				WHERE sl_bills.Status  $q_status ORDER BY sl_bills.ID_bills,DueDate ASC ");
		$va{'matches'} = $sth->rows();
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'total'} += $rec->{'Amount'};
			my $amount_due = &bills_amount_due($rec->{'ID_bills'});
			$va{'total_due'} += $amount_due;
			$showlist=1;
			($line<$first) and ($showlist=0);
			($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
			++$line;
			if ($showlist){
				$rec->{'DDays'} = "<span style='Color:Red'>$rec->{'DDays'}</span>" if ($rec->{'DDays'}<0);
				$va{'bills_list'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td class='smalltext'>
						<a href="/cgi-bin/mod/admin/admin?cmd=mer_bills_payments&amp;id_vendors=$rec->{'ID_vendors'}" ><img src="[va_imgurl]/[ur_pref_style]/b_cauth.gif" title="Pay" alt="Pay" border="0"></a>
						<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}"><span  class='smalltext'>$rec->{'ID_bills'}</span></a></td>
					<td class='smalltext'>(<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}"><span  class='smalltext'>$rec->{'ID_vendors'}</span></a>) $rec->{'CompanyName'}</td>
					<td class='smalltext' align='right'>|.&format_price($rec->{'Amount'}).qq|</td>
					<td class='smalltext' align='right'>|.&format_price($amount_due).qq|</td>
					<td class='smalltext' align='center'>$rec->{'VCurrency'}</td>
					<td class='smalltext'>$rec->{'POTerms'}</td>
					<td class='smalltext' nowrap>$rec->{'DueDate'} ($rec->{'DDays'})</td>
					<td class='smalltext'>$rec->{'Memo'}</td>
				</tr>\n|;
			}
		}
		$va{'total'} = &format_price($va{'total'});
		$va{'total_due'} = &format_price($va{'total_due'});
		if (!$va{'bills_list'}){
			$va{'pageslist'} = 1;
			$va{'bills_list'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('fin_make_checks.html');	


}

#############################################################################
#############################################################################
#   Function: fin_pending_bills
#
#       Es: Listado de Bills pendentes de autorizacion
#       En: 
#
#
#    Created on: 2013-06-03
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_pending_bills {
#############################################################################
#############################################################################
	$in{'id_bills'} = int($in{'id_bills'});
	$in{'auth_bills'} = &filter_values($in{'auth_bills'});
	if ($in{'to_process'} and $in{'auth_bills'}) {
		my @ids = ();
		@ids = split /\|/, $in{'auth_bills'};
		
		foreach my $id_bill (@ids) {
			my ($sth) = &Do_SQL("SELECT amount,currency_exchange,Status,Type,currency FROM sl_bills WHERE ID_bills='$id_bill'");
			($in{'amount'},$in{'currency_exchange'},$in{'status'},$in{'type'},$in{'currency'}) = $sth->fetchrow_array();
			my ($t_amount) =  $in{'amount'};
			$in{'amount'} = $in{'amount'}*$in{'currency_exchange'} if ($in{'currency'} ne $cfg{'acc_default_currency'} and $in{'currency_exchange'});
			if  ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'Pending'){
				
				if (&check_permissions('mer_bills_pendauth','','')){
					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Processed',AuthBy=$usr{'id_admin_users'} WHERE ID_bills='$id_bill';");
					&auth_logging('mer_bills_toprocessed',$id_bill);
					$va{'message'} = &trans_txt('mer_bills_toprocessed');
					$in{'status'} = 'Processed';
				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}
			} elsif (!($t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})})) {
				$va{'message'} = &trans_txt('mer_bills_autoproc');
			}
			
			if ($in{'status'} eq 'Processed'){
				# Detectamos si es un Bill de Expenses
				&bills_to_processed($id_bill,$in{'currency_exchange'});	
			}
		}
	}
	
	#if ($in{'to_process'} and $in{'id_bills'}){
	#	my ($sth) = &Do_SQL("SELECT amount,currency_exchange,Status,Type,currency FROM sl_bills WHERE ID_bills=$in{'id_bills'}");
	#	($in{'amount'},$in{'currency_exchange'},$in{'status'},$in{'type'},$in{'currency'}) = $sth->fetchrow_array();
	#	my ($t_amount) =  $in{'amount'};
	#	$in{'amount'} = $in{'amount'}*$in{'currency_exchange'} if ($in{'currency'} ne $cfg{'acc_default_currency'} and $in{'currency_exchange'});
	#	if  ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'Pending'){
	#		if (&check_permissions('mer_bills_pendauth','','')){
	#			my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Processed',AuthBy=$usr{'id_admin_users'} WHERE ID_bills='$in{'id_bills'}';");
	#			&auth_logging('mer_bills_toprocessed',$in{'id_bills'});
	#			$va{'message'} = &trans_txt('mer_bills_toprocessed');
	#			$in{'status'} = 'Processed';
	#		}else{
	#			$va{'message'} = &trans_txt('unauth_action');
	#		}
	#	}
	#	if ($in{'status'} eq 'Processed'){
	#		# Detectamos si es un Bill de Expenses
	#		&bills_to_processed($in{'id_bills'},$in{'currency_exchange'});
	#	}
	#}

	if ($in{'type'}){
		$va{'tab_'.lc($in{'type'})} = 'selected';
		$add_sql = " AND Type='$in{'type'}' ";
	}else{
		$va{'tab_all'} = 'selected';
		$add_sql = '';
	}

	my ($sth) = &Do_SQL("SELECT sl_bills.*, CompanyName, sl_vendors.Currency AS VCurrency, POTerms ,
				DATEDIFF(CURDATE(),DueDate) AS DDays
				FROM sl_bills LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=sl_bills.ID_vendors
				WHERE sl_bills.Status='Pending' $add_sql ORDER BY sl_bills.ID_bills,DueDate ASC ");
	$va{'matches'} = $sth->rows();
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$va{'total'} += $rec->{'Amount'};
		$showlist=1;
		#($line<$first) and ($showlist=0);
		#($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
		#++$line;
		if ($showlist){
			$rec->{'DDays'} = "<span style='Color:Red'>$rec->{'DDays'}</span>" if ($rec->{'DDays'}<0);
			$va{'bills_list'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td class='smalltext'>
					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}"><span  class='smalltext'>$rec->{'ID_bills'}</span></a></td>
				<td class='smalltext'>$rec->{'CompanyName'}</td>

				<td class='smalltext' align='right'>|.&format_price($rec->{'Amount'}).qq|</td>
				<td class='smalltext' align='center'>$rec->{'VCurrency'}</td>
				<td class='smalltext'>$rec->{'POTerms'}</td>
				<td class='smalltext' nowrap>$rec->{'DueDate'} ($rec->{'DDays'})</td>
				<td class='smalltext'>$rec->{'Memo'}</td>
				<td class='smalltext'>&nbsp;<input type="checkbox" name="auth_bills" value="$rec->{'ID_bills'}" /></td>
			</tr>\n|;
		}
	}
	$va{'total'} = &format_price($va{'total'});
	if (!$va{'bills_list'}){
		$va{'pageslist'} = 1;
		$va{'bills_list'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_pending_bills.html');	


}

#############################################################################
#############################################################################
#   Function: fin_new_bills
#
#       Es: Listado de Bills nuevos
#       En: 
#
#
#    Created on: 2013-07-09
#
#    Author: _EO_
#
#    Modifications:
#
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_new_bills {
#############################################################################
#############################################################################
	$in{'id_bills'} = int($in{'id_bills'});
	$in{'auth_bills'} = &filter_values($in{'auth_bills'});
	if ($in{'to_pending'} and $in{'auth_bills'}) {
		my @ids = ();
		@ids = split /\|/, $in{'auth_bills'};
		
		foreach my $id_bill (@ids) {
			my ($sth) = &Do_SQL("SELECT amount,currency_exchange,Status,Type,currency FROM sl_bills WHERE ID_bills='$id_bill'");
			($in{'amount'},$in{'currency_exchange'},$in{'status'},$in{'type'},$in{'currency'}) = $sth->fetchrow_array();
			my ($t_amount) =  $in{'amount'};
			$in{'amount'} = $in{'amount'}*$in{'currency_exchange'} if ($in{'currency'} ne $cfg{'acc_default_currency'} and $in{'currency_exchange'});
			if  ($cfg{'bills_autoproc_'.lc($in{'type'})} and $t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})}  and $in{'status'} eq 'New'){
				
				if (&check_permissions('mer_bills_pendauth','','')){
					my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Pending',AuthBy=$usr{'id_admin_users'} WHERE ID_bills='$id_bill';");
					&auth_logging('mer_bills_topending',$id_bill);
					$va{'message'} = &trans_txt('mer_bills_topending');
					$in{'status'} = 'Pending';
				}else{
					$va{'message'} = &trans_txt('unauth_action');
				}
			} elsif (!($t_amount > $cfg{'bills_autoproc_'.lc($in{'type'})})) {
				$va{'message'} = &trans_txt('mer_bills_autoproc');
			}
			#if ($in{'status'} eq 'Pending'){
			#	# Detectamos si es un Bill de Expenses
			#	&bills_to_processed($id_bill,$in{'currency_exchange'});	
			#}
		}
	}
	
	if ($in{'type'}){
		$va{'tab_'.lc($in{'type'})} = 'selected';
		$add_sql = " AND Type='$in{'type'}' ";
	}else{
		$va{'tab_all'} = 'selected';
		$add_sql = '';
	}

	my ($sth) = &Do_SQL("SELECT sl_bills.*, CompanyName, sl_vendors.Currency AS VCurrency, POTerms ,
				DATEDIFF(CURDATE(),DueDate) AS DDays
				FROM sl_bills LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=sl_bills.ID_vendors
				WHERE sl_bills.Status='New' $add_sql ORDER BY sl_bills.ID_bills,DueDate ASC ");
	$va{'matches'} = $sth->rows();
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$va{'total'} += $rec->{'Amount'};
		$showlist=1;
		#($line<$first) and ($showlist=0);
		#($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
		#++$line;
		if ($showlist){
			$rec->{'DDays'} = "<span style='Color:Red'>$rec->{'DDays'}</span>" if ($rec->{'DDays'}<0);
			$va{'bills_list'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td class='smalltext'>
					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}"><span  class='smalltext'>$rec->{'ID_bills'}</span></a></td>
				<td class='smalltext'>$rec->{'CompanyName'}</td>

				<td class='smalltext' align='right'>|.&format_price($rec->{'Amount'}).qq|</td>
				<td class='smalltext' align='center'>$rec->{'VCurrency'}</td>
				<td class='smalltext'>$rec->{'POTerms'}</td>
				<td class='smalltext' nowrap>$rec->{'DueDate'} ($rec->{'DDays'})</td>
				<td class='smalltext'>$rec->{'Memo'}</td>
				<td class='smalltext'>&nbsp;<input type="checkbox" name="auth_bills" value="$rec->{'ID_bills'}" /></td>
			</tr>\n|;
		}
	}
	$va{'total'} = &format_price($va{'total'});
	if (!$va{'bills_list'}){
		$va{'pageslist'} = 1;
		$va{'bills_list'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_new_bills.html');	

}

sub fin_banks_movements_make_checks_list {
#-----------------------------------------
# Created on: 5/16/2013 2:51:48 PM By  	carlos haas
# Forms Involved: 
# Description :
# Parameters : 	
    
	$in{'id_bills'} = int($in{'id_bills'});
	$in{'auth_bills'} = &filter_values($in{'auth_bills'});
	my $template_exists = 0;
	my $sql_date_between = '';
	my $sql_idbanks = '';
	my $sql_idbanks_movements = '';
	my $sql_idvendors = '';
	$in{'from_date'} = &filter_values($in{'from_date'});
	$in{'to_date'} = &filter_values($in{'to_date'});
	$in{'id_banks'} = &filter_values($in{'id_banks'});
	$in{'id_banks_movements'} = &filter_values($in{'id_banks_movements'});
	$in{'id_vendors'} = &filter_values($in{'id_vendors'});
	
	if ($in{'to_date'} and $in{'from_date'}) {
		$sql_date_between = "AND sl_banks_movements.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}'";
	} elsif ($in{'from_date'}) {
		$sql_date_between =  "AND sl_banks_movements.Date >= '$in{'from_date'}'";
	} elsif ($in{'to_date'}) {
		$sql_date_between =  "AND sl_banks_movements.Date <= '$in{'to_date'}'";
	}
	
	$sql_idbanks = "AND sl_banks.ID_banks='$in{'id_banks'}'" if ($in{'id_banks'});
	$sql_idbanks_movements = "AND sl_banks_movements.ID_banks_movements='$in{'id_banks_movements'}'" if($in{'id_banks_movements'});
	$sql_idvendors = "AND sl_vendors.ID_vendors='$in{'id_vendors'}'" if($in{'id_vendors'});
	$sql_vendors_name = "AND sl_vendors.CompanyName LIKE '%$in{'company_name'}%'" if($in{'company_name'});
	
	my ($sth) = &Do_SQL("SELECT
							sl_banks_movements.ID_banks_movements, sl_banks_movements.Date, sl_banks_movements.Type, sl_banks_movements.Amount,
							sl_banks. NAME,sl_banks.SubAccountOf as account,
							sl_vendors.CompanyName, sl_vendors.ID_vendors
						FROM
							sl_banks_movements
						INNER JOIN sl_banks ON (sl_banks_movements.ID_banks = sl_banks.ID_banks)
						INNER JOIN sl_banks_movrel ON (sl_banks_movrel.ID_banks_movements = sl_banks_movements.ID_banks_movements)
						INNER JOIN sl_bills ON (sl_banks_movrel.tablename = 'bills' AND sl_banks_movrel.tableid = sl_bills.ID_bills)
						INNER JOIN sl_vendors ON (sl_vendors.ID_vendors = sl_bills.ID_vendors)
						WHERE
							sl_banks_movements.Type = 'Credits' $sql_date_between $sql_idbanks $sql_idbanks_movements $sql_idvendors $sql_vendors_name
						GROUP BY
							sl_banks_movements.ID_banks_movements
						ORDER BY
							sl_banks_movements.ID_banks_movements ASC;");
							
    my @sys_checks = split /,/, $sys{'db_fin_banks_movements_prntemp'};
	
	$va{'matches'} = $sth->rows();
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		$va{'total'} += $rec->{'Amount'};
		$showlist=1;
		($line<$first) and ($showlist=0);
		($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
		++$line;
		if ($showlist or $va{'matches'} == 1){
			#cgierr($va{'matches'});
			foreach my $key (keys @sys_checks) {
				if ($sys_checks[$key] =~ /$rec->{'NAME'}/i) {
					
					my $format = ($key == 0)?'':'f='.($key + 1);
					$va{'print_check'} =  qq|
					<a style="display: inline;" class="anchorclass modulo" href="#" onclick="javascript:prnwin('/cgi-bin/mod/admin/dbman?cmd=fin_banks_movements&search=Print&toprint=$rec->{'ID_banks_movements'}&$format'); return false;">
						<img border="0" alt="" title="Print" src="/sitimages/default/b_print.gif">
					</a>
					|;
					$template_exists = 1;
				}
			}
			$va{'print_check'} = '' if(!$template_exists);
			$template_exists = 0;
			$rec->{'DDays'} = "<span style='Color:Red'>$rec->{'DDays'}</span>" if ($rec->{'DDays'}<0);
			$va{'banks_movements_list'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td>
					$va{'print_check'}
				</td>
				<td class='smalltext'>
					<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}"><span  class='smalltext'>$rec->{'ID_banks_movements'}</span></a></td>
				<td class='smalltext' align="left" >$rec->{'Date'}</td>
                <td class='smalltext'>$rec->{'Type'}</td>
				<td class='smalltext' align='right'>|.&format_price($rec->{'Amount'}).qq|</td>
				<td class='smalltext' align="left" >$rec->{'NAME'}</td>
				<td class='smalltext' align="right">$rec->{'account'}</td>
				<td class='smalltext' align="right">$rec->{'CompanyName'}</td>
				<td class='smalltext' align="right">$rec->{'ID_vendors'}</td>
			</tr>\n|;
		}
	}
	$va{'total'} = &format_price($va{'total'});
	if (!$va{'banks_movements_list'}){
		$va{'pageslist'} = 1;
		$va{'banks_movements_list'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_banks_movements_make_checks_list.html');		
}

#############################################################################
#############################################################################
#   Function: fin_banks_movements_precon
#
#       Es: Genera Reporte en Excel con los movimientos bancarios y su afectacion operativa
#       En: 
#
#
#    Created on: 2014-08-00
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - in_export: Variable para determinar que se degenerar el reporte exportable
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub fin_banks_movements_precon {
#############################################################################
#############################################################################


	if($in{'export'}){


		if(!$in{'from_date'}){

			$error{'from_date'} = &trans_txt('invalid');
			$err++;

		}

		if(!$err){

			my $from_date = $in{'from_date'};
			my $to_date = $in{'to_date'} ? $in{'to_date'} : &get_sql_date();
			my $this_emp = $cfg{'company_name'};

			#print "Content-type: text/html\n\n";
			print "Content-type: application/octet-stream\n";
			print "Content-disposition: attachment; filename=bank_movemements_detailed_$this_emp_$from_date_$to_date.csv\n\n";
			print qq|"Bank Movement","Type","Bank Date","Amount in Currency","Amount","Exchange Rate","Ref Num","Memo","Table Type","Table ID","Table Related ID","Amount Paid","Journal Entry"\n|;

			my $query = "SELECT 
							sl_banks_movrel.ID_banks_movements
							, sl_banks_movements.`Type`
							, sl_banks_movements.BankDate
							, sl_banks_movements.AmountCurrency
							, sl_banks_movements.Amount
							, sl_banks_movements.currency_exchange
							, sl_banks_movements.RefNum
							, sl_banks_movements.Memo
							, sl_banks_movrel.tablename
							, sl_banks_movrel.tableid
							, sl_banks_movrel.AmountPaid * IF(sl_banks_movements.currency_exchange IS NULL,1,sl_banks_movements.currency_exchange) AS AmountPaid
							, CONCAT(sl_banks_movements.Date,' ',sl_banks_movements.Time) AS AppDate
						FROM sl_banks_movements INNER JOIN sl_banks_movrel USING(ID_banks_movements)
						LEFT JOIN sl_orders_payments ON ID_orders_payments = sl_banks_movrel.tableid
						WHERE sl_banks_movements.`Status` = 'Active'
						AND sl_banks_movements.BankDate BETWEEN '$from_date' AND '$to_date'
						ORDER BY 
							sl_banks_movements.ID_banks_movements
							, sl_banks_movements.`Type`
							, sl_banks_movements.BankDate
							, sl_banks_movrel.tablename";

			my ($sth) = &Do_SQL($query);
			while (my ($id_banks_movements, $type, $bank_date, $amount_currency, $amount, $currency_exchange, $refnum, $memo, $table_name, $table_id, $amount_paid, $app_date) = $sth->fetchrow() ){

				my $table_related_id;
				if($table_name eq 'orders_payments'){

					####
					#### Extraemos del Pago el ID_orders 
					####
					$table_id = &load_name('sl_orders_payments', 'ID_orders_payments', $table_id, 'ID_orders');


				}elsif($table_name eq 'accounts'){

					####
					#### table_id es el mismo movimiento bancario
					####
					$table_id = $id_banks_movements;

				}elsif($table_name eq 'bills'){

					####
					#### Buscamos si el Bill pertenece a una purchase_order
					####
					my ($sth) = &Do_SQL("SELECT ID_tableused FROM sl_movements WHERE ID_tablerelated = '$table_id' AND tablerelated = 'sl_bills' AND EffDate = '$bank_date' AND tableused = 'sl_purchaseorders' LIMIT 1;");
					my ($id_purchaseorders) = $sth->fetchrow();
					$table_related_id = $table_id if $id_purchaseorders;
					$table_id = $id_purchaseorders if $id_purchaseorders;
					$table_name = 'purchase_order' if $id_purchaseorders;


				}

				###
				### Buscamos Journal Relacionado
				###
				my ($sth2) = &Do_SQL("SELECT ID_journalentries FROM sl_movements WHERE ID_tableused = '$table_id' AND TIMESTAMPDIFF(MINUTE, '$app_date', CONCAT(Date,' ',Time)) = 0 LIMIT 1;");
				my ($id_journalentries) = $sth2->fetchrow();

				print qq|"$id_banks_movements","$type","$bank_date","$amount_currency","$amount","$currency_exchange","$refnum","$memo","$table_name","$table_id","$table_related_id","$amount_paid","$id_journalentries"\n|;

			}

			return;
		}

	}

	print "Content-type: text/html\n\n";
	print &build_page('fin_banks_movements_precon.html');
}


sub fin_diestel_transactions{
	my $curdate = &Do_SQL("SELECT DATE_FORMAT(NOW(),'%Y%m%d') now;")->fetchrow();
	if($in{'export'}){
	$where = "AND CapDate >= '$in{'fromdate'}' AND Date <= '$in{'todate'}' ";
	$query = "SELECT 
			id_orders_payments,
		id_orders,
			Pmtfield11,
			Pmtfield6,
		DATE_FORMAT(CapDate, '%d/%m/%Y') date,
		time,
		AuthCode,
		amount
	FROM 
		sl_orders_payments 
	WHERE 1
		$where
		AND PmtField1 = 'Mastercard - Puntos'
		AND Captured = 'Yes'
	ORDER BY
		id_orders_payments DESC";
	my $rs = &Do_SQL($query);
		
		$va{'csv'} = "HDR|$curdate\n";
	my $aux = 1;
	while(my $row = $rs->fetchrow_hashref() ){
			$referencia = $row->{'id_orders_payments'};
			if($row->{'amount'} == 1){
				$referencia = $row->{'Pmtfield11'};
			}
			$encryp_card_number = &Do_SQL("SELECT sl_orders_cardsdata.card_number from sl_orders_cardsdata where id_orders='$row->{'id_orders'}' limit 1")->fetchrow();
			$card_number = &LeoDecrypt($encryp_card_number);
			$va{'csv'} .= "REG|$aux|$row->{'date'}|$row->{'time'}|8470040100008|$row->{'AuthCode'}|$card_number|".format_number($row->{'amount'},2,1)."|$row->{'Pmtfield6'}|$cfg{'diestel_reference_number'}|$referencia\n";
		$aux++;
	}
	my ($totalRow, $totalMount) = &Do_SQL("SELECT 
		count(*),
		sum(Amount)
	FROM 
		sl_orders_payments 
	WHERE 1
		$where
		AND PmtField9 = 'Mastercard - Puntos'
		AND Captured = 'Yes'
	ORDER BY
		id_orders_payments DESC")->fetchrow();
	$va{'csv'} .= "TRL|$totalRow|".format_number($totalMount,2,1);
	}
	if($in{'export'}){
		my $f = "IU$curdate";
		print "Content-Disposition: attachment; filename=$f.txt;";
		print "Content-type: text/txt\n\n";
		print $va{'csv'};
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('fin_diestel_transactions.html');	
	}
}


1;
