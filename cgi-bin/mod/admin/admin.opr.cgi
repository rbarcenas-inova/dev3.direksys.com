#!/usr/bin/perl
##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################
sub opr_orders_sales {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html.cgi
# Parameters : It takes any parameter from status table sl_orders



	if ($in{'tab'} eq 2){
		($va{'tab1'},$va{'tab2'},$va{'tab3'}) = ('','selected','');
		$va{'report_info'} = &report_orders;
	}elsif($in{'tab'} eq 3){
		($va{'tab1'},$va{'tab2'},$va{'tab3'}) = ('','','selected');
		$va{'report_info'} = &report_orders_adv;
	}else{
		($va{'tab1'},$va{'tab2'},$va{'tab3'}) = ('selected','','');
		$va{'report_info'} = &report_orders_links;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_sales.html');
}

sub opr_orders_changeso {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 8/05/2012 16:43PM
# Last Modified on:
# Last Modified by:
# Author: Pablo H. Hdez.
# Description :Change the origins of orders  
# Parameters :ID's Orders
# Last Modified: 

    if($in{'action'}){
        if(!$in{'id_orders_changeso'} || !$in{'id_salesorigins'}){
            $va{'message'} = &trans_txt('required');
            $err++;
        }
        if(!$err){
        		my $so = &load_name('sl_salesorigins','ID_salesorigins',int($in{'id_salesorigins'}),'Channel');
            @list = split (/\s+|,|\n|\t/,$in{'id_orders_changeso'});
            for (0..$#list){
	            $tnum = int($list[$_]);
            	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='".$tnum."';");
                if ($sth->fetchrow()>0){
	                $query_list = "UPDATE sl_orders SET ID_salesorigins=".int($in{'id_salesorigins'})." WHERE ID_orders='".$tnum."';";                                
	                $sth = &Do_SQL($query_list);
	                &auth_logging('sl_orders_updated',$tnum);

	                &add_order_notes_by_type($tnum,"Sale Origin changed to $so","Low");

	                $va{'changeresult'} .= $tnum.": ".&trans_txt('tochg_so')." <br>";
                }else{
                	$va{'changeresult'} .= $tnum.": ".&trans_txt('invalid')." <br>";
                }
            }
        }else{
        	$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none_so')."</p>";    
        }
    }else{
    	$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none_so')."</p>";
    }
    
    print "Content-type: text/html\n\n";
    print &build_page('opr_orders_changeso.html'); 
}

sub opr_orders_home {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html.cgi
# Parameters : It takes any parameter from sl_orders.Status
# Last Modified RB: 10/19/09  15:56:33 -- La lista de ordenes con credito listo para aplicar solamente aparecen para grupo developers|finance


	my (@colsx) = ('non','rf','frv','fif','oc','frr');
	my (@colsy) = ('all','90','61','31','16','1','0','f1','f16','f31','f61','f90');
	for my $x(0..$#colsx){
		for my $y(0..$#colsy){
			$va{$colsx[$x].'_'.$colsy[$y]} ='----';
		}
	}
	
	$va{'for_refund'}= "";
	
	$va{'for_refund'}	=	qq|
					<tr>
				  	<td class="smalltext" nowrap>&nbsp;&nbsp; For Refund</td>
				  	<td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=90')">$va{'rf_90'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=61')">$va{'rf_61'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=30')">$va{'rf_31'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=16')">$va{'rf_16'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=1')">$va{'rf_1'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=now')">$va{'rf_0'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f1')">$va{'rf_f1'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f16')">$va{'rf_f16'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f30')">$va{'rf_f31'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f61')">$va{'rf_f61'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f90')">$va{'rf_f90'}</td>
				    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/admin?cmd=opr_orders_fpbatch&StatusPay=For Refund&due=f90')">$va{'rf_all'}</td>
			 	</tr>|	if	$usr{'usergroup'}	=~	/1|8/;			 	
	
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_home.html');
}


sub opr_orders_rep_prodqty{
#-----------------------------------------
# Created on: 11/25/08  15:54:52 By  Roberto Barcenas
# Forms Involved: opr_orders_prodqty_list , opr_orders_prodqty_print
# Description : Report of Items Summary for Processed Orders
# Parameters : 

	my ($sth);

	if($in{'export'}){
		$in{'export'} = int($in{'export'});
		&opr_orders_repsltvid if $in{'export'} > 0;
		return;
	}

	$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,SUM(Quantity) AS Total
									FROM sl_orders
									INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
									AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00') 
									AND sl_orders.Status='Processed' AND sl_orders_products.Status = 'Active'
									AND sl_orders_products.ID_products>1000000
									INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
									GROUP BY sl_orders_products.ID_products ORDER BY SUM(Quantity) DESC");
									
	$va{'matches'} = $sth->rows();
	
	if ($va{'matches'}>0){
		
		if($in{'printlist'}){
			
			$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'<br>',Model)AS PName,SUM(Quantity) AS Total
													FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
													AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00') 
													AND sl_orders.Status='Processed' AND sl_orders_products.Status = 'Active'
													AND sl_orders_products.ID_products>1000000
													INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
													GROUP BY sl_orders_products.ID_products ORDER BY SUM(Quantity) DESC");
			
		}else{
		
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
	
		
			####### Extracts product,name/model , Quantity
			$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'<br>',Model)AS PName,SUM(Quantity) AS Total
													FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
													AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00') 
													AND sl_orders.Status='Processed' AND sl_orders_products.Status = 'Active'
													AND sl_orders_products.ID_products>1000000
													INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
													GROUP BY sl_orders_products.ID_products ORDER BY SUM(Quantity) 
													DESC LIMIT $first,$usr{'pref_maxh'}; ");
		}

		while($rec = $sth->fetchrow_hashref()){
	
			###### Products Paid in Full
			my ($stpf) = &Do_SQL("SELECT COUNT( * )
														FROM sl_orders_products INNER JOIN (
														SELECT sl_orders.ID_orders FROM `sl_orders_payments`
														INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_payments.ID_orders
														INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
														WHERE sl_orders.Status = 'Processed'
														AND ID_products = '$rec->{'ID'}' 
														GROUP BY sl_orders.ID_orders
														HAVING COUNT( sl_orders.ID_orders ) = 1
														) AS pf ON pf.ID_orders = sl_orders_products.ID_orders
														WHERE ID_products = '$rec->{'ID'}' AND Status = 'Active'
														AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')");
														
			my	($fullp) = $stpf->fetchrow();
		
		
			######## Products Paid in FP
			my ($stfp) = &Do_SQL("SELECT COUNT( * )
														FROM sl_orders_products INNER JOIN (
														SELECT sl_orders.ID_orders FROM `sl_orders_payments`
														INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_payments.ID_orders
														INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
														WHERE sl_orders.Status = 'Processed'
														AND ID_products = '$rec->{'ID'}' 
														GROUP BY sl_orders.ID_orders
														HAVING COUNT( sl_orders.ID_orders ) >1
														) AS pf ON pf.ID_orders = sl_orders_products.ID_orders
														WHERE ID_products = '$rec->{'ID'}' AND Status = 'Active'
														AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')");
													
			my	($fpp) = $stfp->fetchrow();
			
			my ($stin) = &Do_SQL("SELECT IF(SUM(Quantity) > 0,SUM(Quantity),0) FROM sl_warehouses_location WHERE ID_warehouses = 1003 AND  ID_products = '$rec->{'ID'}'");
			my ($inventory) = $stin->fetchrow();
		
		
			if($in{'printlist'}){
				$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext' valign='top'>|.format_sltvid($rec->{'ID'}).qq|</td>
							<td class='smalltext' valign='top'>$rec->{'PName'}</td>
							<td class='smalltext' valign='top'>$rec->{'Total'}</td>
							<td class='smalltext' valign='top'>$fullp</td>
							<td class='smalltext' valign='top'>$fpp</td>
							<td class='smalltext' valign='top'>$inventory</td>
							<td class='smalltext' valign='top'>|.($inventory - $rec->{'Total'}).qq|</td>
							<td class='smalltext' valign='top'>&nbsp;</td>
						</tr>\n|;
			}else{
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext' valign='top'><a href="$cfg{'pathcgi_adm_dbman'}?cmd=mer_products&view=|.substr($rec->{'ID'},3).qq|">|.format_sltvid($rec->{'ID'}).qq|</a></td>
							<td class='smalltext' valign='top'>$rec->{'PName'}</td>
							<td class='smalltext' valign='top' align='center'>$rec->{'Total'}</td>
							<td class='smalltext' valign='top' align='center'>$fullp</td>
							<td class='smalltext' valign='top' align='center'>$fpp</td>
							<td class='smalltext' valign='top' align='center'>$inventory</td>
							<td class='smalltext' valign='top' align='center'>|.($inventory - $rec->{'Total'}).qq|</td>
							<td class='smalltext' valign='top' align='right'><a href="$cfg{'pathcgi_adm_admin'}?cmd=opr_orders_rep_prodqty&export=$rec->{'ID'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xls.gif' title='Export |.format_sltvid($rec->{'ID'}).qq| Info' alt='' border='0'></a></td>
						</tr>\n|;
			}
		}	
	}else{
		$va{'searchresults'} = qq|
														<tr>
															<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
														</tr>\n|;
	}

	
	if($in{'printlist'}){
		print "Content-type: text/html\n\n";
		print &build_page('opr_orders_prodqty_print.html');	
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_prodqty_list.html');	
}



sub opr_orders_rep_prodmoney{
#-----------------------------------------
# Created on: 01/06/09  17:54:52 By  Roberto Barcenas
# Forms Involved: opr_preorders_prodqty_list , opr_preorders_prodqty_print
# Description : Report of Money Summary for Preorders
# Parameters : 
# Last Modified on: 01/27/09 16:41:27
# Last Modified by: MCC C. Gabriel Varela S: Se agregan totales

	my ($sth);

	if($in{'export'}){
		$in{'export'} = int($in{'export'});
		&opr_orders_repsltvid if $in{'export'} > 0;
		return;
	}

	$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Quantity,0)) AS qweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Amount,0)) AS aweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Total,0)) AS tweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,SalePrice,0)) AS sweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Quantity,0)) AS qmonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Amount,0)) AS amonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Total,0)) AS tmonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,SalePrice,0)) AS smonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Quantity,0)) AS qother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Amount,0)) AS aother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Total,0)) AS tother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,SalePrice,0)) AS sother
									FROM sl_orders
									INNER JOIN (SELECT ID_orders, SUM(IF(Status IN('Denied','Pending','On Collection'), 1, 0 )) AS Denied,
									SUM(IF(Captured='Yes' AND Amount > 0,Amount,0)) AS Amount ,
									SUM( IF(Status = 'Approved' AND Amount > 0, Amount, 0 ) ) AS Total , Paymentdate
									FROM sl_orders_payments WHERE Type = 'Layaway' AND Status <> 'Cancelled' GROUP BY ID_orders HAVING Denied  = 0) AS d
									ON sl_orders.ID_orders = d.ID_orders AND Ptype!='Credit-Card' AND Paymentdate >= CURDATE() AND sl_orders.Status = 'Processed' 
									INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
									AND sl_orders_products.Status = 'Active' AND SalePrice > 0
									AND sl_orders_products.ID_products>1000000
									INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
									GROUP BY sl_orders_products.ID_products");
									
	$va{'matches'} = $sth->rows();
	
	if ($va{'matches'}>0){
		
		if($in{'printlist'}){
			
			$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Quantity,0)) AS qweek,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Amount,0)) AS aweek,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Total,0)) AS tweek,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,SalePrice,0)) AS sweek,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Quantity,0)) AS qmonth,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Amount,0)) AS amonth,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Total,0)) AS tmonth,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,SalePrice,0)) AS smonth,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Quantity,0)) AS qother,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Amount,0)) AS aother,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Total,0)) AS tother,
											SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,SalePrice,0)) AS sother
											FROM sl_orders
											INNER JOIN (SELECT ID_orders, SUM(IF(Status IN('Denied','Pending','On Collection'), 1, 0 )) AS Denied,
											SUM(IF(Captured='Yes' AND Amount > 0,Amount,0)) AS Amount ,
											SUM( IF(Status = 'Approved' AND Amount > 0, Amount, 0 ) ) AS Total , Paymentdate
											FROM sl_orders_payments WHERE Type = 'Layaway' AND Status <> 'Cancelled' GROUP BY ID_orders HAVING Denied  = 0) AS d
											ON sl_orders.ID_orders = d.ID_orders  AND Ptype!='Credit-Card' AND Paymentdate >= CURDATE() AND sl_orders.Status = 'Processed'
											INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
											AND sl_orders_products.Status = 'Active' AND SalePrice > 0
											AND sl_orders_products.ID_products>1000000
											INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
											GROUP BY sl_orders_products.ID_products");
			
		}else{
		
			$usr{'pref_maxh'} = 10;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
	
		
			####### Extracts product,name/model , Quantity
			$sth = &Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Quantity,0)) AS qweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Amount,0)) AS aweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,Total,0)) AS tweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 0 AND 7,SalePrice,0)) AS sweek,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Quantity,0)) AS qmonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Amount,0)) AS amonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,Total,0)) AS tmonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) BETWEEN 8 AND 30,SalePrice,0)) AS smonth,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Quantity,0)) AS qother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Amount,0)) AS aother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,Total,0)) AS tother,
									SUM(IF(DATEDIFF(Paymentdate,CURDATE()) > 30,SalePrice,0)) AS sother
									FROM sl_orders
									INNER JOIN (SELECT ID_orders, SUM(IF(Status IN('Denied','Pending','On Collection'), 1, 0 )) AS Denied,
									SUM(IF(Captured='Yes' AND Amount > 0,Amount,0)) AS Amount ,
									SUM( IF(Status = 'Approved' AND Amount > 0, Amount, 0 ) ) AS Total , Paymentdate
									FROM sl_orders_payments WHERE Type = 'Layaway' AND Status <> 'Cancelled' GROUP BY ID_orders HAVING Denied  = 0) AS d
									ON sl_orders.ID_orders = d.ID_orders  AND Ptype!='Credit-Card' AND Paymentdate >= CURDATE() AND sl_orders.Status = 'Processed'
									INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
									AND sl_orders_products.Status = 'Active' AND SalePrice > 0
									AND sl_orders_products.ID_products>1000000
									INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
									GROUP BY sl_orders_products.ID_products LIMIT $first,$usr{'pref_maxh'}; ");
		}
		my $totqty,$totcost,$tottotcost,$tottotsale,$totprofit;

		while($rec = $sth->fetchrow_hashref()){	
			$totqty=$totcost=$tottotcost=$tottotsale=$totprofit=0;
		
			my ($sltvcost, $cost_adj) = &load_sltvcost($rec->{'ID'});

				$d = 1 - $d;
				$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td class='smalltext' valign='top'><a href="$cfg{'pathcgi_adm_dbman'}?cmd=mer_products&view=|.substr($rec->{'ID'},3).qq|">|.format_sltvid($rec->{'ID'}).qq|</a></td>
							<td class='smalltext' valign='top'>$rec->{'PName'}</td>
						</tr>
						<tr bgcolor='$c[$d]'>
							<td colspan="2">
								<table align="center" width="100%" border="1">
									<tr>
										<td class="gcell_off" align="center">&nbsp;</td>
										<td class="gcell_off" align="center">Quantity</td>
										<td class="gcell_off" align="center">Cost</td>
										<td class="gcell_off" align="center">Tot. Cost</td>
										<td class="gcell_off" align="center">Tot. Sale</td>
										<td class="gcell_off" align="center">Profit</td>										
									</tr>|;
							
						## Week 1-7 Days			
						if($rec->{'qweek'} > 0){
								$va{'searchresults'} .= qq|		
									<tr>
										<td class='smalltext' valign='top' align='center'>1-7 Days</td>
										<td class='smalltext' valign='top' align='center'>$rec->{'qweek'}</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($sltvcost).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'qweek'} * $sltvcost).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'sweek'}).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'sweek'} - ($rec->{'qweek'} * $sltvcost)).qq|</td>
									</tr>|;
								$totqty+=$rec->{'qweek'};
								$totcost+=$sltvcost;
								$tottotcost+=$rec->{'qweek'} * $sltvcost;
								$tottotsale+=$rec->{'sweek'};
								$totprofit+=$rec->{'sweek'} - ($rec->{'qweek'} * $sltvcost);
						}
								
						## Month 8-30 Days			
						if($rec->{'qmonth'} > 0){
							$va{'searchresults'} .= qq|		
									<tr>
										<td class='smalltext' valign='top' align='center'>8-30 Days</td>
										<td class='smalltext' valign='top' align='center'>$rec->{'qmonth'}</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($sltvcost).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'qmonth'} * $sltvcost).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'smonth'}).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'smonth'} - ($rec->{'qmonth'} * $sltvcost)).qq|</td>
									</tr>|;
								$totqty+=$rec->{'qmonth'};
								$totcost+=$sltvcost;
								$tottotcost+=$rec->{'qmonth'} * $sltvcost;
								$tottotsale+=$rec->{'smonth'};
								$totprofit+=$rec->{'smonth'} - ($rec->{'qmonth'} * $sltvcost);
							}
								
							## Month > 30 Days			
							if($rec->{'qother'} > 0){
								$va{'searchresults'} .= qq|
										<tr>
											<td class='smalltext' valign='top' align='center'> 30 Days</td>
											<td class='smalltext' valign='top' align='center'>$rec->{'qother'}</td>
											<td class='smalltext' valign='top' align='center'>|.&format_price($sltvcost).qq|</td>
											<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'qother'} * $sltvcost).qq|</td>
											<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'sother'}).qq|</td>
										<td class='smalltext' valign='top' align='center'>|.&format_price($rec->{'sother'} - ($rec->{'qother'} * $sltvcost)).qq|</td>
										</tr>|;
									$totqty+=$rec->{'qother'};
									$totcost+=$sltvcost;
									$tottotcost+=$rec->{'qother'} * $sltvcost;
									$tottotsale+=$rec->{'sother'};
									$totprofit+=$rec->{'sother'} - ($rec->{'qother'} * $sltvcost);
								}		
						$va{'searchresults'} .= qq|
										<tr>
											<td class='smalltext' valign='top' align='center' style="font:bold 11px"> Totals</td>
											<td class='smalltext' valign='top' align='center' style="font:bold 11px">$totqty</td>
											<td class='smalltext' valign='top' align='center' style="font:bold 11px">|.&format_price($totcost).qq|</td>
											<td class='smalltext' valign='top' align='center' style="font:bold 11px">|.&format_price($tottotcost).qq|</td>
											<td class='smalltext' valign='top' align='center' style="font:bold 11px">|.&format_price($tottotsale).qq|</td>
										<td class='smalltext' valign='top' align='center' style="font:bold 11px">|.&format_price($totprofit).qq|</td>
										</tr>|;
									
						$va{'searchresults'} .= qq|		
								</table>
							</td>
						</tr>|;
		}	
	}else{
		$va{'searchresults'} = qq|
														<tr>
															<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
														</tr>\n|;
	}

	
	if($in{'printlist'}){
		print "Content-type: text/html\n\n";
		print &build_page('opr_orders_prodmoney_print.html');	
		return;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_prodmoney_list.html');	
}


sub opr_orders_repsltvid{
#-----------------------------------------
# Created on: 11/26/08  10:32:05 By  Roberto Barcenas
# Forms Involved: 
# Description : Returns excel file with specific item data summary for Processed Orders
# Parameters : 	
	
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=all_$in{'export'}.csv\n\n";
	my (@cols) = ("ID_Orders","Date","StatusPrd","StatusPay","Status","ID_customers","First Name","Last Name",
					"Address1","Address2","City","State","Zip","Phone1","Phone2","Phone3","B-Day","Sex","Email",
					"Qty","Pay Type","Payments");
	
	print '"'.join('","',@cols) . "\"\r\n";
	
	
	my ($sth) = &Do_SQL("SELECT sl_orders.* ,COUNT(ID_products) AS Qty,Type, Payments FROM sl_orders_products INNER JOIN sl_orders 
											ON sl_orders.ID_orders = sl_orders_products.ID_orders AND ID_products = '$in{'export'}' AND sl_orders.Status = 'Processed' 
											AND sl_orders_products.Status = 'Active' AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')
											INNER JOIN (SELECT ID_orders,Type,COUNT(ID_orders) AS Payments FROM sl_orders_payments WHERE Status<>'Cancelled' GROUP BY ID_orders) 
											AS paym ON paym.ID_orders = sl_orders.ID_orders
											GROUP BY sl_orders.ID_orders ORDER BY Payments,Qty DESC");
											
	while ($rec = $sth->fetchrow_hashref() ) {
			$ary[0] = $rec->{'ID_orders'};
			$ary[1] = $rec->{'Date'};
			$ary[2] = $rec->{'StatusPrd'};
			$ary[3] = $rec->{'StatusPay'};
			$ary[4] = $rec->{'Status'};
			
			my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
			$rec_cust = $sth2->fetchrow_hashref();
			$ary[5] = $rec->{'ID_customers'};
			$ary[6] = $rec_cust->{'FirstName'};
			$ary[7] = $rec_cust->{'LastName1'};
			$ary[8] = $rec->{'Address1'};
			$ary[9] = $rec->{'Address2'};
			$ary[10] = $rec->{'City'};
			$ary[11] = $rec->{'State'};
			$ary[12] = $rec->{'Zip'};
			$ary[13] = $rec_cust->{'Phone1'};
			$ary[14] = $rec_cust->{'Phone2'};
			$ary[15] = $rec_cust->{'Cellphone'};
			$ary[16] = "$rec_cust->{'bday_month'}-$rec_cust->{'bday_day'}";
			$ary[17] = $rec_cust->{'Sex'};
			$ary[18] = $rec_cust->{'Email'};
			
			$ary[19] = $rec->{'Qty'};
			$ary[20] = $rec->{'Type'};
			$ary[21] = $rec->{'Payments'};
			print '"'.join('","',@ary) . "\"\r\n";
	}
}


sub opr_pendings {
# --------------------------------------------------------
	if ($in{'action'} and $in{'rdate'}){
		my ($amount,$count);
		
		my (%resp) = &ax_pendings_load(" AND Date='$in{'rdate'}'");
		$va{'output'} = qq|<table border="0" cellspacing="0" width="95%" class="formtable" align="center">\n|;
		$va{'output'} .= "<tr>";
		$va{'output'} .= "<td class='menu_bar_title' colspan='5' align='center'>Pending - Analisis</td>";
		$va{'output'} .= "</tr>";		
		my (@cols) = ('bill-add','generaldec','insuffunds','stolen','invalid','avs','pre-approved',
					'missing','check','processor','timedout','cvn','expired','risk','na');
		my (@cols_names) = ('Bill <> Shipping','General Decline','Insuficient Funds','Stolen Card','Invalid Card','AVS not Match','Pre-approved',
					'Missing Info','Check','The processor declined the request based on an issue with the request itself.','Communication Error','Card verification number not matched.','Expired card','Risk Order','Not Available');
		for (0..$#cols){
			$va{'output'} .= "<tr>";
			$va{'output'} .= "<td class='smalltext'>$cols_names[$_]</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_number($resp{$cols[$_]}[0])."</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_price($resp{$cols[$_]}[1])."</td>";
			$va{'output'} .= "</tr>";
			$amount  += $resp{$cols[$_]}[1];
			$count += $resp{$cols[$_]}[0];
		}
		$va{'output'} .= "<tr>";
			$va{'output'} .= "<td class='smalltext' align='right'>Total = </td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_number($count)."</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
			$va{'output'} .= "</tr>";	
		$va{'output'} .= "</table>&nbsp;";
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_pendings.html');
	
	
}


sub opr_voids {
# --------------------------------------------------------
	if ($in{'action'} and $in{'rdate'}){
		my ($amount,$count);
		
		my (%resp) = &ax_pendings_load(" AND Date='$in{'rdate'}'",'Void');
		$va{'output'} = qq|<table border="0" cellspacing="0" width="95%" class="formtable" align="center">\n|;
		$va{'output'} .= "<tr>";
		$va{'output'} .= "<td class='menu_bar_title' colspan='5' align='center'>Pending - Analisis</td>";
		$va{'output'} .= "</tr>";		
		my (@cols) = ('bill-add','generaldec','insuffunds','stolen','invalid','avs','pre-approved',
					'missing','check','processor','timedout','cvn','expired','risk','na');
		my (@cols_names) = ('Bill <> Shipping','General Decline','Insuficient Funds','Stolen Card','Invalid Card','AVS not Match','Pre-approved',
					'Missing Info','Check','The processor declined the request based on an issue with the request itself.','Communication Error','Card verification number not matched.','Expired card','Risk Order','Not Available');
		for (0..$#cols){
			$va{'output'} .= "<tr>";
			$va{'output'} .= "<td class='smalltext'>$cols_names[$_]</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_number($resp{$cols[$_]}[0])."</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_price($resp{$cols[$_]}[1])."</td>";
			$va{'output'} .= "</tr>";
			$amount  += $resp{$cols[$_]}[1];
			$count += $resp{$cols[$_]}[0];
		}
		$va{'output'} .= "<tr>";
			$va{'output'} .= "<td class='smalltext' align='right'>Total = </td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_number($count)."</td>";
			$va{'output'} .= "<td class='smalltext' align='right'>".&format_price($amount)."</td>";
			$va{'output'} .= "</tr>";	
		$va{'output'} .= "</table>&nbsp;";
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_voids.html');
	
	
}


sub opr_orders_board {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_board.html');
}


sub opr_orders_board2 {
# --------------------------------------------------------
# Last Time Modified By RB on 2/10/10 1:24 PM : Las llamadas se sacan de S7
# Last Modified by RB on 06/06/2011 11:20:08 AM : Se agrega vixicom

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Date=Curdate()");
	$va{'numsales'} = &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT SUM(OrderNet) FROM sl_orders WHERE Date=Curdate()");
	$va{'totalsales'} = &format_price($sth->fetchrow);	

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_inorders WHERE Date=Curdate()");
	$va{'numinorders'} = &format_number($sth->fetchrow);
	

	$query .=" AND grupo IN('','US') "	if $in{'e'}	==	1;
	$query .=" AND grupo = 'GTS' "		if $in{'e'}	==	4;
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	my ($sth) = &Do_SQL("SELECT /*src,dstchannel,duration,calldate,grupo,accountcode,didusa*/ COUNT(*) from cdr inner join sl_numbers ON didusa = accountcode where accountcode IS NOT NULL AND accountcode !='' AND (LOCATE('SIP',dstchannel) > 0 OR LOCATE('vixicom',dstchannel) > 0) AND duration > 60 $query AND DATE(calldate) = CURDATE()",1);
	$va{'numcalls'} = &format_number($sth->fetchrow);
	&disconnect_db();
	&connect_db_w($cfg{'dbi_db'},$cfg{'dbi_host'},$cfg{'dbi_user'},$cfg{'dbi_pw'});

	

	## Logs
	$in{'date'} = 'today';
	&load_cfg('sl_orders');
	my ($numhits, @hits) = &query('sl_orders');

	if ($numhits>0){
		my (%tmp, $qs);
		my (@c) = split(/,/,$cfg{'srcolors'});
		@headerfields = split(/,/, $sys{"db_opr_orders_list"});
		my ($rows) = ($#hits+1)/($#db_cols+1);
		$script_url   = $cfg{'pathcgi_adm_dbman'};
		for (0 .. $rows-1) {
			$d = 1 - $d;
			%tmp = &array_to_hash($_, @hits);
			$page .= qq|		    <tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>\n|;
			for (0..$#headerfields){
				if ($headerfields[$_] =~ /^(\w{2})_([^:]+):([^\.]+)\.([^\.]+)/){
					
					## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
					$page .= "	<td valign='top'><a href='".&build_link("$1_$2",$4,$tmp{$3})."' class='error' target='_top'>". &load_name("$1_$2","ID_$2",$tmp{$3},$4) ."</a></td>\n";
				}elsif($headerfields[$_] =~ /^admin_users:([^\.]+)\.([^\.]+)/){
					
					## tbl_name:field_id.field_name 1)DB  2)ID  3)Name
					$page .= "	<td valign='top'><a href='".&build_link("admin_users",$2,$tmp{$1})."' class='error'>". &load_name("admin_users","ID_admin_users",$tmp{$1},$2) ."</a></td>\n";
				}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
					$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
					$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
				}else{
					$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
					$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
				}
			}
			$page .= "		</tr>";
		}
		$va{'searchresults'} = $page;
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_board2.html');
	
}

sub opr_orders_dashboard {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_dashboard.html');
}

sub opr_orders_dashboard2 {
# --------------------------------------------------------

	#########################################
	#####  TOTAL SALES
	#########################################
	my (%totals,$result,$query,$out);
	my (@ary_q1name) = ('all','new', 'processed', 'pending', 'cancelled', 'shipped', 'syserr');
	my (@ary_query1) = ('',"sl_orders.Status='New'", "sl_orders.Status='Processed'", "sl_orders.Status='Pending'", "sl_orders.Status='Cancelled'", "sl_orders.Status='Shipped'", "sl_orders.Status='System Error'");
	my (@ary_q2name) = ('t', 'm', 'w', 'n');
	my (@ary_query2) = ('', 'DATE_FORMAT(sl_orders.date,\'%Y%m\')=DATE_FORMAT(NOW(),\'%Y%m\')', 'DATE_FORMAT(sl_orders.date,\'%Y%v\')=DATE_FORMAT(NOW(),\'%Y%v\')', 'DATE_FORMAT(sl_orders.date,\'%Y%m%d\')=DATE_FORMAT(NOW(),\'%Y%m%d\')');
	for my $x(0..$#ary_q2name){
		($ary_query2[$x]) ?  ($query =" AND $ary_query2[$x]"):($query = '');
		my ($sth) = &Do_SQL("SELECT SUM(SalePrice) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active' $query");
		$res = $sth->fetchrow;
		$va{$ary_q1name[0].'_'.$ary_q2name[$x].'sales'} = &format_price($res);
		$total{$ary_q2name[$x].'sales'} = $res;
	}	
	for my $i(1..$#ary_q1name){
		($ary_query1[$i]) and ($query =  " AND ". $ary_query1[$i]);
		for my $x(0..$#ary_q2name){
			if ($query and $ary_query2[$x]){
				$query = " $query AND $ary_query2[$x]";
			}elsif (!$query and $ary_query2[$x]){
				$query = " AND $ary_query2[$x]";
			}elsif ($query){
				$query = $query;
			}
			my ($sth) = &Do_SQL("SELECT SUM(SalePrice) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active' $query");
			$result = $sth->fetchrow;
			$va{$ary_q1name[$i].'_'.$ary_q2name[$x].'sales'}= &format_price($result);
			($total{$ary_q2name[$x].'sales'}>0) ?
				($va{$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = int($result/$total{$ary_q2name[$x].'sales'}*1000)/10):
				($va{$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = 0);
			($ary_query1[$i]) and ($query =  " AND ". $ary_query1[$i]);
		}
	}
	


	#########################################
	#####  SALES BY PAYMENT
	#########################################
	my (%totals,$result,$query,$out);
	my (@ary_q1name) = ('all','cc','chk', 'wu','ot');
	my (@ary_query1) = ('',"Type='Credit-Card'", "Type='Check'", "Type='WesternUnion'","Type NOT IN('Credit-Card','Check','WesternUnion')");
	my (@ary_q2name) = ('t', 'm', 'w', 'n');
	my (@ary_query2) = ('','DATE_FORMAT(date,\'%Y%m\')=DATE_FORMAT(NOW(),\'%Y%m\')', 'DATE_FORMAT(date,\'%Y%v\')=DATE_FORMAT(NOW(),\'%Y%v\')', 'DATE_FORMAT(date,\'%Y%m%d\')=DATE_FORMAT(NOW(),\'%Y%m%d\')');
	for my $x(0..$#ary_q2name){
		($ary_query2[$x]) ?  ($query =" AND $ary_query2[$x]"):($query = '');
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE Status NOT IN ('Cancelled','Order Cancelled','Void') $query");
		$res = $sth->fetchrow;
		$va{'pmts'.$ary_q1name[0].'_'.$ary_q2name[$x].'sales'}= &format_price($res);
		$total{$ary_q2name[$x].'pmts'} = $res;
	}	
	for my $i(1..$#ary_q1name){
		($ary_query1[$i]) and ($query =  " AND ". $ary_query1[$i]);
		for my $x(0..$#ary_q2name){
			if ($query and $ary_query2[$x]){
				$query = " $query AND $ary_query2[$x]";
			}elsif (!$query and $ary_query2[$x]){
				$query = " AND $ary_query2[$x]";
			}elsif ($query){
				$query = $query;
			}
			my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE Status NOT IN ('Cancelled','Order Cancelled','Void') $query");
			$result = $sth->fetchrow;
			$va{'pmts'.$ary_q1name[$i].'_'.$ary_q2name[$x].'sales'}= &format_price($result);
			($total{$ary_q2name[$x].'pmts'}>0) ?
				($va{'pmts'.$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = int($result/$total{$ary_q2name[$x].'pmts'}*1000)/10):
				($va{'pmts'.$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = 0);
		}
	}
	
	#########################################
	#####  SALES BY CATEGORIES
	#########################################
	my (%totals,$result,$query,$out);
	my (@ary_q1name) = ('126','9','2','12','7','4','6','3','1','11','8','10');
	my (@ary_query1) = ("ID_top='126'", "ID_top='9'", "ID_top='2'", "ID_top='12'", "ID_top='7'","ID_top='4'","ID_top='6'","ID_top='3'","ID_top='1'","ID_top='11'","ID_top='8'","ID_top='10'");
	my (@ary_q2name) = ('t', 'm', 'w', 'n');
	my (@ary_query2) = ('', 'DATE_FORMAT(sl_orders_products.date,\'%Y%m\')=DATE_FORMAT(NOW(),\'%Y%m\')', 'DATE_FORMAT(sl_orders_products.date,\'%Y%v\')=DATE_FORMAT(NOW(),\'%Y%v\')', 'DATE_FORMAT(sl_orders_products.date,\'%Y%m%d\')=DATE_FORMAT(NOW(),\'%Y%m%d\')');
	for my $i(0..$#ary_q1name){
		($ary_query1[$i]) and ($query =  " AND ". $ary_query1[$i]);
		for my $x(0..$#ary_q2name){
			if ($query and $ary_query2[$x]){
				$query = " $query AND $ary_query2[$x]";
			}elsif (!$query and $ary_query2[$x]){
				$query = " AND $ary_query2[$x]";
			}elsif ($query){
				$query = $query;
			}
			my ($sth) = &Do_SQL("SELECT SUM(SalePrice) FROM sl_products_categories,sl_orders_products WHERE RIGHT(sl_orders_products.id_products,6) = sl_products_categories.id_products AND sl_orders_products.Status='Active' $query");
			#my ($sth) = &Do_SQL("SELECT SUM(sl_orders_products.SalePrice) FROM sl_orders_products,sl_products_categories WHERE  $query2 RIGHT(sl_orders_products.id_products,6) = sl_products_categories.id_products  $query");    			
			$result = $sth->fetchrow;
			$va{$ary_q1name[$i].'_'.$ary_q2name[$x].'sales'}= &format_price($result);
			($total{$ary_q2name[$x].'sales'}>0) ?
				($va{$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = int($result/$total{$ary_q2name[$x].'sales'}*1000)/10):
				($va{$ary_q1name[$i].'_'.$ary_q2name[$x].'salespp'} = 0);
		}
	}			
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_dashboard2.html');
}





##################################################################
#    OPERATIONS : REPORTS
##################################################################

sub opr_orders_eofd {
# --------------------------------------------------------
	if ($in{'action'}){
		if ($in{'rdate'} =~ /^run(.*)/){
			require ("admin.reports.cgi");
			my ($cmdname) = "admin_rep_".$1;
			if (defined &$cmdname){
				&$cmdname();
				return;
			}else{
				$va{'message'} = &trans_txt('reqfields');
			}
		}elsif ($in{'rdate'}){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND ShpDate='$in{'rdate'}' AND sl_orders_products.Status='Active'");
			if ($sth->fetchrow>0){
				&opr_orders_eofd_run;
				return
			}else{
				$va{'message'} = &trans_txt('search_nomatches');
			}
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_eofd.html');
}

sub opr_orders_eofd_run {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND ShpDate='$in{'rdate'}' AND sl_orders_products.Status='Active' GROUP BY ID_products,SalePrice");
	$va{'matches'} = $sth->rows;

	my ($choices,$sth);
	if ($in{'print'}){
		($sth) = &Do_SQL("SELECT *,SUM(Quantity) AS totqty FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND ShpDate='$in{'rdate'}' AND sl_orders_products.Status='Active' GROUP BY ID_products,SalePrice ORDER BY ID_products");
	}else{
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
		($sth) = &Do_SQL("SELECT *,SUM(Quantity) AS totqty FROM sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND ShpDate='$in{'rdate'}' AND sl_orders_products.Status='Active' GROUP BY ID_products,SalePrice ORDER BY ID_products LIMIT $first,$usr{'pref_maxh'}");
	}
	while ($rec = $sth->fetchrow_hashref){
		my ($sth2) = &Do_SQL("SELECT sl_products.SLTV_NetCost, sl_products.Model, sl_products.Name, sl_products.totqty FROM sl_products WHERE ID_products='".substr($rec->{'ID_products'},3,6)."'");	
		my ($tmp) = $sth2->fetchrow_hashref;
		$choices = &load_choices($rec->{'ID_products'});
		($rec->{'SalePrice'}==0) and ($rec->{'SalePrice'}=$tmp->{'SLTV_NetCost'});
		($rec->{'SalePrice'}==0) and ($rec->{'SalePrice'}=1);
		$va{'searchresults'} .= qq|
			<tr>
				<td class="smalltext" valign='top' nowrap>|.&format_sltvid($rec->{'ID_products'}) . qq|</td>
				<td class="smalltext" valign='top'>$tmp->{'Model'}<br>$tmp->{'Name'}$choices</td>
				<td class="smalltext" valign='top' align="right">$rec->{'totqty'}</td>
				<td class="smalltext" valign='top' nowrap align="right">|.&format_price($tmp->{'SLTV_NetCost'}).qq|</td>
				<td class="smalltext" valign='top' nowrap align="right">|.&format_price($tmp->{'SLTV_NetCost'}*$rec->{'totqty'}).qq|</td>
				<td class="smalltext" valign='top' nowrap align="right">|.&format_price($rec->{'SalePrice'}*$rec->{'totqty'}).qq|</td>
				<td class="smalltext" valign='top' nowrap align="right">|.&format_price($rec->{'SalePrice'}*$rec->{'totqty'}-$tmp->{'SLTV_NetCost'}*$rec->{'totqty'}).qq|</td>
				<td class="smalltext" valign='top' align="right">|.&format_number((100*($rec->{'SalePrice'}-$tmp->{'SLTV_NetCost'}))/$rec->{'SalePrice'},2).qq|%</td>
			</tr>
		|;
		$va{'tot_cost'} += $tmp->{'SLTV_NetCost'}*$rec->{'totqty'};
		$va{'tot_sales'} += $rec->{'SalePrice'}*$rec->{'totqty'};
	}
	$va{'tot_profit'} = &format_price($va{'tot_sales'}-$va{'tot_cost'});
	$va{'tot_pp'} = &format_number(100*($va{'tot_sales'}-$va{'tot_cost'})/$va{'tot_sales'},2);
	$va{'tot_cost'} = &format_price($va{'tot_cost'});
	$va{'tot_sales'} = &format_price($va{'tot_sales'});
	

	if (!$va{'searchresults'}){
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = "<tr><td colspan='9' align='center'>".&trans_txt("search_nomatches")."</td></tr>";
	}

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('opr_eofd_list.html');
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('opr_eofd_list.html');
	}
	
}







#################################################################
# OPERATIONS : SETUP SHIPPING #
#################################################################

sub opr_changestatus {
#-----------------------------------------
# Forms Involved: 
# Created on:
# Author: Unknown
# Description :
# Parameters :
#
# Last Modified on: 09/04/08  10:58:55
# Last Modified by: Roberto Barcenas
# Last Modified Desc: adding posteddate set up and skipnote variable 
# Last Modification by JRG : 03/09/2009 : Se agrega el log
# Last Time Modified by RB on 23/11/2011: Se agrega autorizacion para downsale
# Last Time Modified by RB on 23/11/2011: Se agrega Posibilidad de agregar bulk notes


	if ($in{'action'} and ( $in{'new_status'} eq 'Shipped' or ($in{'status'} eq 'Shipped' and $in{'new_status'} ne 'Shipped')  ) ){

		$va{'message'} = &trans_txt('reqfields');
		$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none')."</p>";
		$error{'status'} = &trans_txt('invalid');

	}elsif($in{'action'}){

		if(check_permissions('bulk_changestatus','','')){

			if ($in{'id_orders_bulk'}){

				$in{'db'} = 'sl_orders';
				my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
				my ($query,$rpd,$orddate);
				
				ORDERS:for my $i(0..$#ary){

					$orddate = '';
					$rpd = '';

					$va{'changeresult'} .= "$ary[$i] : ";

					my $st = &load_name('sl_orders','ID_orders',int($ary[$i]),'Status');

					if($st eq 'Shipped'){

						$va{'changeresult'} .= &trans_txt('invalid') . ' status ' . $st;
						next ORDERS;

					}

					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='".&filter_values($ary[$i])."'");
					if ($sth->fetchrow()>0){
						$query = '';
						
						if ($in{'new_paystatus'} ne "" and $in{'new_paystatus'} ne "---") {
							$query .= ",StatusPay='$in{'new_paystatus'}' ";
						}
						if ($in{'new_prdstatus'} ne "" and $in{'new_prdstatus'} ne "---") {
							$query .= ",StatusPrd='$in{'new_prdstatus'}' ";
						}
						if($in{'new_status'} eq '' or $in{'new_status'} eq '---'){
							my ($sth2) = &Do_SQL("SELECT Status FROM sl_orders WHERE ID_orders='".&filter_values($ary[$i])."'");
							$new_status = $sth2->fetchrow();
						}else{
							$new_status = $in{'new_status'};
						}							
						my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='$new_status' $query WHERE ID_orders='".&filter_values($ary[$i])."';");
						&auth_logging('opr_orders_st' . $in{'new_status'},$ary[$i]);
						&status_logging($ary[$i], $in{'new_status'});

						if(!$in{'skipnote'}){

							&add_order_notes_by_type(&filter_values($ary[$i]),"The Status of the Order has been changed to $in{'new_status'} on ".&filter_values($in{'shipdate'}),"Low");
							&auth_logging('opr_orders_noteadded',$ary[$i]);
						}
						
						## Trying to Set PostedDate to Orders
						if($in{'new_status'} eq 'Shipped'){

							my ($sth) = &Do_SQL("SELECT Date FROM sl_orders WHERE ID_orders='".&filter_values($ary[$i])."' AND (PostedDate IS NULL OR PostedDate = '0000-00-00');");
							my ($orddate) = $sth->fetchrow; 
							if ($orddate ne ''){
								$respd = &posteddate_order(&filter_values($ary[$i]),$orddate);
								($respd ne 'ok') and ($rpd = ' - '.$respd);
							}
						}	
						
						if ($in{'new_status'}){
							&auth_logging('opr_orders_st'.$in{'new_status'},$ary[$i]);
						}
						if ($in{'new_paystatus'}){
							&auth_logging('opr_orders_stp'.$in{'new_paystatus'},$ary[$i]);
						}
						if ($in{'new_prdstatus'}){
							&auth_logging('opr_orders_str'.$in{'new_prdstatus'},$ary[$i]);
						}
						$va{'changeresult'} .= &trans_txt('tochg_changed')." $in{'new_status'} $rpd ";
					}else{
						$va{'changeresult'} .= &trans_txt('invalid')." $rpd ";
					}

					

					if($in{'notes'}){
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='".&filter_values($ary[$i])."' AND Status <> 'Shipped';");
						if ($sth->fetchrow()>0){
							(!$in{'notestype'}) and ($in{'notestype'} = 'Low');
							


							&add_order_notes_by_type(int($ary[$i]),&filter_values($in{'notes'}),$in{'notestype'});

							&auth_logging('opr_orders_noteadded',int($ary[$i]));

							$va{'changeresult'} .= " NoteOK ";
						}


					}

					$va{'changeresult'} .= "<br>";

				}
			}else{
				$va{'message'} = &trans_txt('reqfields');
				$error{'status'} = &trans_txt('invalid') if (!$in{'new_status'});
				$error{'shipdate'} = &trans_txt('invalid') if (!$in{'shipdate'});
				$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none')."</p>";
			}
		}else{
			$va{'changeresult'} .= &trans_txt('unauth_action');
		}
	}else{
		$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none')."</p>";
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_changestatus.html');		
}

#GV Inicia
sub opr_authnumber{
# --------------------------------------------------------	
#MCC C Gabriel Varela S
#31 de marzo de 2008 19:25
# Last Modification by JRG : 03/09/2009 : Se agrega el log
	my ($num,$cad);
	if ($in{'action'}){
		$in{'id_orders'} = int($in{'id_orders'});
		if (!$in{'id_orders'}){
			#### Message!!
			$va{'message'}="No se ha introducido una orden.";
		}else{
			## Revisar que el numero de la orden este en Proccessed o Shipped
			my($orderrs)=&Do_SQL("SELECT Status FROM sl_orders WHERE ID_orders=$in{'id_orders'}");
			my($orderrsresult)=$orderrs->fetchrow();
			if ($orderrsresult eq "Processed" or $orderrsresult eq "Shipped"){
				## generoi numero
				$num=int(rand 10000);
				$cad=sprintf ("%.04d",$num);
				$va{'authnumr'}=$cad;
				#insert sl_vars SET VNAME="Auth Order",VValue=$id_order,$id_user,$num
				my ($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName='Auth Order' AND VValue LIKE '$in{'id_orders'},%'");
				if ($sth->fetchrow() >0){
					my ($sth)=&Do_SQL("UPDATE sl_vars SET VValue='$in{'id_orders'},$usr{'id_admin_users'},$cad', Subcode = DATE_ADD(CURDATE(), INTERVAL 5 DAY)  WHERE VName='Auth Order' AND VValue LIKE '$in{'id_orders'},%'");
					&auth_logging('var_updated',$in{'id_orders'});
				}else{
					my ($sth)=&Do_SQL("INSERT INTO sl_vars SET VName='Auth Order',VValue='$in{'id_orders'},$usr{'id_admin_users'},$cad', Subcode = DATE_ADD(CURDATE(), INTERVAL 5 DAY)");
					&auth_logging('var_added',$sth->{'mysql_insertid'});
				}
				
			}else{
				### message error
				$va{'message'}="No se ha generado el numero de autorizacion debido a que la orden no tiene el status adecuado o la orden no existe.";
			}
		}
	}else{

		$num=int(rand 10000);
		$cad=sprintf ("%.04d",$num);
		$va{'authnumr'}=$cad;

		&Do_SQL("REPLACE INTO sl_vars SET VName='Authorization Code',VValue='$usr{'id_admin_users'},$cad';");		
		&auth_logging('var_updated',"");

		$va{'authnumr_downsale'} = '----';
		if( $cfg{'use_downsale_authorization_number'} and $cfg{'use_downsale_authorization_number'} == 1 ){
			$num = int(rand 10000);
			$cad = sprintf ("%.04d",$num);
			$va{'authnumr_downsale'} = $cad;

			&Do_SQL("REPLACE INTO sl_vars SET VName='Downsale Price $usr{'id_admin_users'}',VValue='$usr{'id_admin_users'},$cad',Definition_En='Downsale Price Authorizathion';");
		}

	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_authnumber.html');		
}
#GV Termina


sub opr_bulkorders_prn {
# --------------------------------------------------------
# Last Modified on: 17/12/12 10:21:02
# Last Modified by: Cesar Cedillo - Pasa a ser en lugar de opr_toprint
	my (@ids);
	my $prefix="orders";
	#$prefix=$in{'prefix'}if $in{'prefix'};
	if ($in{'action'}){
		if ($in{'id_orders_bulk'}){
			$in{'db'} = "sl_$prefix";
			my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
			for my $i(0..$#ary){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_$prefix WHERE ID_$prefix='".&filter_values($ary[$i])."';");
				if ($sth->fetchrow()>0){
					if ($in{'type'} eq 'opr_packinglist' or $in{'type'} eq 'opr_ppackinglist'){
						my ($sth) = &Do_SQL("SELECT ID_".$prefix."_products FROM sl_".$prefix."_products WHERE ID_$prefix='".&filter_values($ary[$i])."' AND Status='Active' AND (ISNULL(Tracking) OR Tracking ='');");
						while ($id = $sth->fetchrow()){
							push(@ids,"$ary[$i],$id");
						}
					}else{
						push(@ids,$ary[$i]);
					}
				}
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
		print &build_page('toprint_msg.html');
	}elsif($in{'action'} and $in{'page'}=~/^exportfile.*/){
		&build_export_setup($prefix,@ids);
	}
	elsif($in{'action'}){
		my ($page,%rec);
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		$in{'db'} = 'sl_orders';
		$in{'toprint'}=1;
		$cmd = $in{'type'};
		#opr_finance
		for my $i(0..$#ids){
			&load_cfg('sl_orders');
			if ($ids[$i]){
				if ($in{'type'} eq 'opr_packinglist' or $in{'type'} eq 'opr_ppackinglist'){
					($in{'id_orders'},$in{'id_orders_products'}) = split(/,/,$ids[$i],2);
					$in{'toprint'} = $in{'id_orders'};
					$ids[$i] = $in{'id_orders'};
				}else{
					$in{'id_orders'} = $ids[$i];
					$in{'toprint'}  = $ids[$i];
				}
				my (%rec) = &get_record($db_cols[0],$ids[$i],$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
				
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
		print &build_page('opr_bulkorders_prn.html');		
	}
}




sub opr_toprint {
# --------------------------------------------------------
# Last Modified on: 09/11/09 17:41:02
# Last Modified by: MCC C. Gabriel Varela S: Se habilita exportaciones y tambi�n para pre�rdenes
	my (@ids);
	my $prefix="orders";
	#$prefix=$in{'prefix'}if $in{'prefix'};
	if ($in{'action'}){
		if ($in{'id_orders_bulk'}){
			$in{'db'} = "sl_$prefix";
			my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
			for my $i(0..$#ary){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_$prefix WHERE ID_$prefix='".&filter_values($ary[$i])."';");
				if ($sth->fetchrow()>0){
					if ($in{'type'} eq 'opr_packinglist' or $in{'type'} eq 'opr_ppackinglist'){
						my ($sth) = &Do_SQL("SELECT ID_".$prefix."_products FROM sl_".$prefix."_products WHERE ID_$prefix='".&filter_values($ary[$i])."' AND Status='Active' AND (ISNULL(Tracking) OR Tracking ='');");
						while ($id = $sth->fetchrow()){
							push(@ids,"$ary[$i],$id");
						}
					}else{
						push(@ids,$ary[$i]);
					}
				}
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
		print &build_page('opr_toprint2.html');
	}elsif($in{'action'} and $in{'page'}=~/^exportfile.*/){
		&build_export_setup($in{'prefix'},@ids);
	}
	elsif($in{'action'}){
		my ($page,%rec);
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		$in{'db'} = 'sl_orders';
		$in{'toprint'}=1;
		$cmd = $in{'type'};
		#opr_finance
		for my $i(0..$#ids){
			&load_cfg('sl_orders');
			if ($ids[$i]){
				if ($in{'type'} eq 'opr_packinglist' or $in{'type'} eq 'opr_ppackinglist'){
					($in{'id_orders'},$in{'id_orders_products'}) = split(/,/,$ids[$i],2);
					$in{'toprint'} = $in{'id_orders'};
					$ids[$i] = $in{'id_orders'};
				}else{
					$in{'id_orders'} = $ids[$i];
					$in{'toprint'}  = $ids[$i];
				}
				my (%rec) = &get_record($db_cols[0],$ids[$i],$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
				
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
		print &build_page('opr_toprint.html');		
	}
}

sub opr_orders_proccbatch {
# --------------------------------------------------------
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='Credit-Card' AND sl_orders.Status='New'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='New' AND Type='Credit-Card' ");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		$va{'searchresults'} = &orders_wreport("cprarpfpd"," sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='New' AND Type='Credit-Card' GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders ASC ");

	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Update Va's & Print Page
	($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('on','off','off','off','off');
	$va{'title'} = "Procesing New Orders With Credit Cards";
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_pbatch.html');	
}

sub opr_orders_prockbatch {
# --------------------------------------------------------
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='New' AND Type='Check' ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='New' AND Type='Check'");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		$va{'searchresults'} = &orders_wreport("cprarpfpd"," sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='New' AND Type='Check' ORDER BY sl_orders.ID_orders ASC");

	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	## Update Va's & Print Page
	($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('off','on','off','off','off');
	$va{'title'} = "Procesing New Orders With Checks";
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_pbatch.html');	
}

sub opr_orders_captbatch {
# --------------------------------------------------------
# Last Modified on: 01/15/09 12:37:20
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la valicaci�n del Authcode
# Last Modified on: 05/27/09 13:55:16
# Last Modified by: MCC C. Gabriel Varela S: Se optimiza consulta
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void','Financed','Counter Finance') AND sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='Credit-Card' and not isnull(AuthCode) and Authcode!='' and Authcode!='0000' AND (Captured='No') AND sl_orders.Status='Shipped'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void','Financed','Counter Finance') AND sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='Credit-Card' and not isnull(AuthCode) and Authcode!='' and Authcode!='0000' AND (Captured='No') AND sl_orders.Status='Shipped'");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		$va{'searchresults'} = &orders_wreport("fx","  sl_orders,sl_orders_payments WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void','Financed','Counter Finance') AND sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='Credit-Card' and not isnull(AuthCode) and Authcode!='' and Authcode!='0000' AND (Captured='No') AND sl_orders.Status='Shipped' ORDER BY sl_orders.ID_orders DESC");

	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	## Update Va's & Print Page
	($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('off','off','off','on','off');
	$va{'title'} = "Orders Ready To Capture";
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_pbatch.html');	
}

sub opr_orders_postdated {
# --------------------------------------------------------
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Pending' AND StatusPay='Post-Dated'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND  sl_orders.Status='Pending' AND StatusPay='Post-Dated'");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		$va{'searchresults'} = &orders_wreport("cprarpfpd","  sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND  sl_orders.Status='Pending' AND StatusPay='Post-Dated' ORDER BY sl_orders.ID_orders ASC");

	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	## Update Va's & Print Page
	($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('off','off','on','off','off');
	$va{'title'} = "Orders Post Dated";
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_pbatch.html');	
}


sub opr_orders_fpbatch {
# --------------------------------------------------------
# Last Modified RB: 10/19/09  15:45:51 -- Se descartan creditos y ordenes que tengan un proceso de return abierto que sea Return for Refund


	my ($query,$subtitle);
	my $extamount = " AND Amount > 0 ";
	my $noretref = " AND 1 > (SELECT COUNT(*) FROM sl_returns WHERE ID_orders = sl_orders.ID_orders AND Type='Returned for Refund') ";
	
	if ($in{'all'}){
		$query = " AND Paymentdate<=Curdate() AND StatusPay<>'On Collection'  ";
	}else{
		if ($in{'due'} eq 'f90'){
			$subtitle .= "<br><span class='stdtext'>Receivables more than 90 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())>90 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq 'f61'){
			$subtitle .= "<br><span class='stdtext'>Receivables 61-90 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())>60 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq 'f31'){
			$subtitle .= "<br><span class='stdtext'>Receivables 31-60 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())>30 AND DATEDIFF(Paymentdate,Curdate())<=60 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq 'f16'){
			$subtitle .= "<br><span class='stdtext'>Receivables 16-30 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())>15 AND DATEDIFF(Paymentdate,Curdate())<=30 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq 'f1'){
			$subtitle .= "<br><span class='stdtext'>Receivables 1-15 Days </span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())>0 AND DATEDIFF(Paymentdate,Curdate())<=15 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		
		}elsif($in{'due'} eq 'now'){
			$subtitle .= "<br><span class='stdtext'>Due Today </span>";
			$query = " AND Paymentdate=Curdate()  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq '1'){
			$subtitle .= "<br><span class='stdtext'>OverDue 1-15 Days <</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate()) BETWEEN -15 AND -1 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq '16'){
			$subtitle .= "<br><span class='stdtext'>OverDue 16-30 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate()) BETWEEN -30 AND -16 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq '30'){
			$subtitle .= "<br><span class='stdtext'>OverDue 31-60 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate()) BETWEEN -60 AND -31 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq '61'){
			$subtitle .= "<br><span class='stdtext'>OverDue 61-90 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate()) BETWEEN -90 AND -61 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}elsif($in{'due'} eq '90'){
			$subtitle .= "<br><span class='stdtext'>OverDue more than 90 days</span>";
			$query = " AND (DATEDIFF(Paymentdate,Curdate())< -90 AND Paymentdate<>'0000-00-00')  AND StatusPay<>'On Collection'  ";
		}
		
		if ($in{'statuspay'} eq 'For Refund'){
			$extamount =~	s/>/</;
			$noretref='';
			$subtitle .= "<br><span class='stdtext'>xPay Status : For Refund</span>";
			$query .= "AND StatusPay IN('For Refund','Pending Refund')  AND StatusPay<>'On Collection'  ";
		}elsif ($in{'statuspay'} eq 'FP:Review Payment'){
			$subtitle .= "<br><span class='stdtext'>xPay Status : FP:Review Payment</span>";
			$query .= "AND StatusPay='FP:Review Payment'  AND StatusPay<>'On Collection'  ";
		}elsif ($in{'statuspay'} eq 'FP:Insufficient Funds'){
			$subtitle .= "<br><span class='stdtext'>xPay Status : FP:Insufficient Funds</span>";
			$query .= "AND StatusPay='FP:Insufficient Funds'  AND StatusPay<>'On Collection'  ";
		}elsif ($in{'statuspay'} eq 'Payment Declined'){
			$subtitle .= "<br><span class='stdtext'>xPay Status : Payment Declined</span>";
			$query .= "AND StatusPay='Payment Declined'  AND StatusPay<>'On Collection'  ";	
		}elsif ($in{'statuspay'} eq 'On Collection'){
			$subtitle .= "<br><span class='stdtext'>xPay Status : On Collection</span>";
			$query .= "AND StatusPay='On Collection' ";	
		}else{
			$query .= "AND StatusPay='None' ";
		}
		if ($in{'statusprd'} eq 'For Return'){
			$query .= " AND StatusPrd='For Return' ";
		#}else{
			#$query .= " AND StatusPrd='None' ";
		}
	}
	$query .= $extamount . $noretref;
	
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders)) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND Type='Credit-Card' AND (AuthCode='0000' OR AuthCode='') AND (Captured<>'Yes' OR CapDate='0000-00-00' OR ISNULL(Captured)) $query AND Paymentdate<>'0000-00-00' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void')");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0 and !$in{'export'} and !$in{'process'}){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND Type='Credit-Card' AND (AuthCode='0000' OR AuthCode='') AND (Captured<>'Yes' OR CapDate='0000-00-00' OR ISNULL(Captured)) $query AND Paymentdate<>'0000-00-00' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void')");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		$va{'searchresults'} = &orders_wreport("f","sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND Type='Credit-Card' AND (AuthCode='0000' OR AuthCode='') AND (Captured<>'Yes' OR CapDate='0000-00-00' OR ISNULL(Captured)) $query AND Paymentdate<>'0000-00-00' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders DESC");
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	## Update Va's & Print Page
	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('opr_orders_pbatch_print.html');
	}elsif($in{'export'}){
		my (@cols) = ('ID Order','Date','ID_customers','StatusPrd','StatusPay','Status');
		#print "Content-type: text/html\n\n";
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=order_detail_$in{'reportdatef'}_$in{'reportdatet'}.csv\n\n";
		print '"'.join('","', @cols)."\"\n";
		&orders_wreport_xls("sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND Type='Credit-Card' AND (AuthCode='0000' OR AuthCode='') AND (Captured<>'Yes' OR CapDate='0000-00-00' OR ISNULL(Captured)) $query AND Paymentdate<>'0000-00-00' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders DESC");
	}elsif($in{'process'}){
		my (@cols) = ('ID Order','Date','Amount','Auth Code','Payment Result');
		#print "Content-type: text/html\n\n";
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=fpautocapture.csv\n\n";
		print '"'.join('","', @cols)."\"\n";
		&orders_wreport_cyb("sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status='Shipped' AND Type='Credit-Card' AND (AuthCode='0000' OR AuthCode='') AND (Captured<>'Yes' OR CapDate='0000-00-00' OR ISNULL(Captured)) $query AND Paymentdate<>'0000-00-00' AND sl_orders_payments.Status NOT IN ('Cancelled','Order Cancelled','Void') GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders DESC");
	}else{
		$va{'morebtns'} = qq| &nbsp; <a href="javascript:prnwin('[va_script_url]?export=1&[va_qs]')"><img src='[va_imgurl]/[ur_pref_style]/b_xls.gif' title='Export List' alt='' border='0'></a> &nbsp;|;
		if ($cfg{'oper_mode'} eq 'cleanup' or $usr{'usergroup'} eq 1 or $usr{'usergroup'} eq 2){
			$va{'morebtns'} .= qq|<a href="javascript:prnwin('[va_script_url]?process=1&[va_qs]')"><img src='[va_imgurl]/[ur_pref_style]/b_fpauth.gif' title='Process All Payments List' alt='' border='0'></a> &nbsp;|;
		}
		($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('off','off','off','off','on');
		$va{'title'} = "Procesing Orders With Flexipago$subtitle";
		print "Content-type: text/html\n\n";
		print &build_page('opr_orders_pbatch.html');
	}
}



sub opr_orders_prnbatch {
# --------------------------------------------------------
	if ($in{'print'}){
		my ($type,$idkey);
		if ($in{'type'} eq 'order'){
			$type = 'order';
			$in{'type'} = 'opr_orders';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'inv'){
			$type = 'inv';
			$in{'type'} = 'opr_pinvoices';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'pl_pdf'){
			$type = 'inv';
			$in{'type'} = 'opr_pinvoices';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'inv_pdf'){
			$type = 'inv_pdf';
			$in{'type'} = 'opr_invoices';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'fin-inv'){
			$type = 'inv_pdf';
			$in{'type'} = 'opr_invoices';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'paylog'){
			$type = 'paylog';
			$in{'tab'} = 3;
			$in{'tabcmd'} = 'orders';
			$in{'type'} = 'opr_paylogs';
			$idkey = 'ID_orders';
		}elsif ($in{'type'} eq 'export'){
			$idkey = 'ID_orders';
			$type = 'export';
		}elsif ($in{'type'} eq 'pl_man_summary'){
			$idkey = 'ID_orders';
			$type = 'pl_man_summary';	
		}elsif ($in{'type'} eq 'pl_man_detailed'){
			$idkey = 'ID_orders';
			$type = 'pl_man_detailed';	
		}
		my ($sth) = &Do_SQL("SELECT $idkey FROM sl_prnmanifest WHERE Printed !='Yes' and Type='$type';");
		while ($id = $sth->fetchrow()){
			push(@ids,$id);
		}
		if ($#ids==-1){
			$va{'message'} = &trans_txt('toprn_none');
			print "Content-type: text/html\n\n";
			print &build_page('opr_toprnt2.html');
			return;
		}


		if ($type eq 'export'){
			&opr_orders_export(@ids);
			return;
		}


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

		if($type eq 'pl_man_summary'){
			&opr_orders_plms(@ids);
			return;
		}elsif($type eq 'pl_man_detailed'){
			&opr_orders_plmd(@ids);
			return;
		}

		$in{'db'} = 'sl_orders';
		$in{'toprint'}=1;
		$cmd = $in{'type'};
		require "dbman.html.cgi";
		if ($in{'tab'} and $in{'tabcmd'} and -e "../common/tabs/$in{'tabcmd'}.cgi"){
			require "../common/tabs/$in{'tabcmd'}.cgi";	
		}
		for my $i(0..$#ids){
			if ($ids[$i]){
				&load_cfg('sl_orders');
				$in{'id_orders'} = $ids[$i];
				$in{'toprint'}  = $ids[$i];
				my (%rec) = &get_record($db_cols[0],$ids[$i],$in{'db'});
				if ($rec{lc($db_cols[0])}){
					foreach $key (sort keys %rec) {
						$in{lc($key)} = $rec{$key};
						($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>/g);
					}
				
					## User Info
					&get_db_extrainfo('admin_users',$in{'id_admin_users'});
					
					if ($in{'tab'} and $in{'tabcmd'} and -e "../common/tabs/$in{'tabcmd'}.cgi"){
						print &print_tabs;
					}else{
						my ($func) = "view_$cmd";
						if (defined &$func){
							&$func;
						}
						print &build_page($cmd.'_print.html');
						#print &html_print_record(%rec);
					}
				}
			}
			if ($ids[$i+1]>0){
				print "<DIV STYLE='page-break-before:always'></DIV>";
			}
		}

	}else{
		if ($in{'done'}){
			my ($sth) = &Do_SQL("UPDATE sl_prnmanifest SET Printed='Yes',PrintedBy='$usr{'id_admin_users'}' WHERE Printed != 'Yes' AND Type='$in{'type'}'");
			&auth_logging('opr_orders_prndone',$in{'id_orders'});
		}
		my ($sth) = &Do_SQL("SELECT COUNT(*),Type FROM sl_prnmanifest WHERE Printed != 'Yes' GROUP BY Type");
		while (@ary = $sth->fetchrow_array){
			$va{'prn_'.$ary[1]} = &format_number($ary[0]);
			if ($ary[0]>0){
				$va{'done_'.$ary[1]} = qq|<a href="/cgi-bin/mod/admin/admin?cmd=opr_orders_prnbatch&done=1&type=$ary[1]"><img src="[va_imgurl]/[ur_pref_style]/flag_green.gif" border=0></a>|;
			}
		}

		print "Content-type: text/html\n\n";
		print &build_page('opr_orders_prnbatch.html');	
	}
}

sub gmt_to_ptm {
# --------------------------------------------------------
	my ($mdate) = @_;
	my ($sth) = &Do_SQL("SELECT CONVERT_TZ('$mdate', 'GMT', 'US/Pacific');");
	my ($xdate)  = $sth->fetchrow;
	
	return substr($xdate,0,10);
	
	##my ($xdate,$xhora,$null) = split(/\s/,$mdate);
	##2007-09-30 19:40:24 GMT
	#3my ($year,$month,$day,$hour,$null) = split(/\s|-|:/,$mdate);
	##if ($month eq 11 and )
	##SELECT CONVERT_TZ( '2007-09-30 19:40:24', 'GMT', 'US/Pacific' ) ;
	##my (@months_num) = (0,31,59,90,120,151,181,212,243,273,304,334);
	##$num = $months_num[$month-1];
	
	
}

sub opr_orders_plmd {
# --------------------------------------------------------
	my (@ids) = @_;
	print "Content-type: text/html\n\n";
	print "<pre>";
	for (0..$#ids){
		print "$ids[$_]\n";
	}
}

sub orders_wreport {
# --------------------------------------------------------
# Last Modified on: 01/27/09 09:49:18
# Last Modified by: MCC C. Gabriel Varela S: Se hace que las fuentes de las consultas sean variables
	my ($btns,$query,$prefx) = @_;
	my ($output,$d,$rec,$sth);
	#return "SELECT * FROM $query DESC LIMIT $first,$usr{'pref_maxh'};";
		$cadtborders="sl_orders";
		$cadidorders="ID_orders";
		$cadtbcustomers="sl_customers";
		$cadidcustomers="ID_customers";
		$cadtbordersproducts="sl_orders_products";
		$cadidordersproducts="ID_orders_products";
		$cadtborderspayments="sl_orders_payments";
		$cadidorderspayments="ID_orders_payments";
		$cadcmd="opr_orders";
		$fxcreditcard="creditcard";
		$fxccsale="ccsale";
		$fxcapture="capture";
		$fxtocapture="tocapture";
		#$in{'prefx'}="";

	if ($in{'print'}){
		($sth) = &Do_SQL("SELECT DISTINCT($cadtborders.$cadidorders),$cadidcustomers,OrderNotes,BillingNotes,shp_Notes FROM $query;");
	}else{
		($sth) = &Do_SQL("SELECT DISTINCT($cadtborders.$cadidorders),$cadidcustomers,OrderNotes,BillingNotes,shp_Notes FROM $query LIMIT $first,$usr{'pref_maxh'};");
	}
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		################
		####  ORDER INFO
		################
		$rec->{'OrderNotes'} =~ s/\n/<br>/g;
		$output .= "<tr bgcolor='$c[$d]' valign='top'>\n";
		$output .= qq| <td class='smalltext' valign='top'><div id='divorder$rec->{$cadidorders}'>
					<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=check_address&$cadidorders=$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_checkaddress.gif' title='Check Address' alt='' border='0'></a><br>
					<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_viewnotes&$cadidorders=$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_notes.gif' title='View Notes' alt='' border='0'></a><br>\n|;

		($btns =~ /c/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=order_tocancelled&$cadidorders=$rec->{$cadidorders}');delete_div('divorder$rec->{$cadidorders}');delete_div('divpayment$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_tocancelled.gif' title='To Cancelled' alt='' border='0'></a><br>\n|);
		($btns =~ /p/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=order_topending&$cadidorders=$rec->{$cadidorders}');delete_div('divorder$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_topending.gif' title='To Pending' alt='' border='0'></a><br>\n|);
		($btns =~ /ra/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=order_toreview_address&$cadidorders=$rec->{$cadidorders}');delete_div('divorder$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toreview_address.gif' title='To Review Address' alt='' border='0'></a><br>\n|);
		($btns =~ /rp/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=order_toreview_payment&$cadidorders=$rec->{$cadidorders}');delete_div('divorder$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_toreview_payment.gif' title='To Review Payment' alt='' border='0'></a><br>\n|);
		($btns =~ /pd/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=order_topostdated&$cadidorders=$rec->{$cadidorders}');delete_div('divorder$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_topostdated.gif' title='To Post Dated' alt='' border='0'></a><br>\n|);
		($btns =~ /f/i) and ($output .= qq|	<a href="#order$rec->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=add_flags&$cadidorders=$rec->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_flags.gif' title='Add Flags' alt='' border='0'></a><br>\n|);
					
					
		$output .= qq| 	</div></td>\n|;
		$output .= "  <td class='smalltext'><a name='order$rec->{$cadidorders}' id='order$rec->{$cadidorders}' href='/cgi-bin/mod/admin/dbman?cmd=$cadcmd&view=$rec->{$cadidorders}'>$rec->{$cadidorders}</a> ".&load_db_names("$cadtbcustomers","$cadidcustomers",$rec->{$cadidcustomers},"[FirstName] [LastName1]");
		
		####################
		#### Items List
		#####################
		my ($tot_qty,$tot_ord);
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM $cadtbordersproducts WHERE $cadidorders='$rec->{$cadidorders}' AND Status='Active'");
		if ($sth2->fetchrow>0){				
			my ($sth1) = &Do_SQL("SELECT * FROM $cadtbordersproducts WHERE $cadidorders='$rec->{$cadidorders}' AND Status='Active' ORDER BY $cadidordersproducts DESC;");
			my ($col);
			$output .= qq|
			<table border='0' cellspacing='0' width='100%'>
			   	<tr>         	
					<td class="menu_bar_title" nowrap>Item ID</td>
					<td class="menu_bar_title">Model/Name</td>
					<td class="menu_bar_title" nowrap>Qty</td>
					<td class="menu_bar_title" nowrap>Sale Price</td>
			 	</tr>\n|;
			while ($col = $sth1->fetchrow_hashref){
				$d = 1 - $d;
				$sku_id_p=substr($col->{'ID_products'},3,6);
				$sku_id_e=$col->{'ID_products'};
				$sku_id_d=format_sltvid($col->{'ID_products'});
										
				$choices = &load_choices($col->{'ID_products'});
																
				$output .= "<tr bgcolor='$c[$d]'>\n";
				$output .= " <td class='smalltext' valign='top'>";

				if($col->{'ID_products'} < 99999){    
	            	### Service        	#GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
					my ($sth5) = &Do_SQL("SELECT * FROM sl_services WHERE ID_services = '$col->{'ID_products'}';");  	
					$serdata = $sth5->fetchrow_hashref;
					$output .="".$col->{'ID_products'}."</td>\n";		
					$output .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($serdata->{'Name'},0,30)."</td>\n";
				}else{
	            	### Products
	            	$output .= &format_sltvid($col->{'ID_products'})."</td>\n";		
					($status,%tmp) = &load_product_info($sku_id_p);
					$output .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($tmp{'name'},0,30)." ".$choices."</td>\n";
				}
				$tot_qty += $col->{'Quantity'};
				$tot_ord +=$col->{'SalePrice'}*$col->{'Quantity'};
				$output .= "  <td class='smalltext' align='right' valign='top'>".&format_number($col->{'Quantity'})."</td>\n";
				$output .= "  <td class='smalltext' align='right' valign='top'>".&format_price($col->{'SalePrice'})."</td>\n";
				$output .= "</tr>\n";						
			}
			$output .= "</table>\n";
		}
		####################
		#### Payments List
		#####################
		my ($tot_payments);
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM $cadtborderspayments WHERE $cadidorders='$rec->{$cadidorders}' AND Status!='Cancelled'");
		if ($sth2->fetchrow>0){				
			my ($sth1) = &Do_SQL("SELECT * FROM $cadtborderspayments WHERE $cadidorders='$rec->{$cadidorders}' AND Status!='Cancelled' ORDER BY $cadidorderspayments DESC;");
			my ($col,$ptype);
			while ($col = $sth1->fetchrow_hashref){	
				$output .= qq|\n		<table border='0' cellspacing='0' width='100%'>\n|;			
				if ($col->{'Type'} eq 'Credit-Card' or $col->{'Type'} eq 'Layaway'){
					if ($ptype ne $col->{'Type'} or !$ptype){
						$output .= qq|
						  <tr>
								<td class='menu_bar_title' width="30">&nbsp;</td>
								<td class='menu_bar_title' width="100">Type</td>
								<td class='menu_bar_title' nowrap>Name on Card<br>Card Number</td>
								<td class='menu_bar_title' width="40">Exp</td>
								<td class='menu_bar_title' width="50">CVN</td>
								<td class='menu_bar_title' width="110">Status<br>Cod Auth</td>			
								<td class='menu_bar_title' nowrap align="right">Amount</td>
						   </tr>\n|;
					}
					$output .= " <tr bgcolor='$c[$d]'>\n";
					$output .= "   <td nowrap width='30'>";
					if (&date_to_unixtime($col->{'Paymentdate'}) > &date_to_unixtime(&get_sql_date()) or $col->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $col->{'Status'} eq 'Financed'){
						## Skip
						$output .= "&nbsp;";
					}elsif($col->{'Status'} ne 'Cancelled' and (($col->{'Status'} ne 'Approved' or $col->{'AuthCode'} eq '0000') or ($col->{'Status'} eq 'Approved' and !$col->{'AuthCode'}))){
					#}elsif($col->{'Status'} ne 'Cancelled' and ($col->{'Status'} ne 'Approved' or $col->{'AuthCode'} eq '0000')){
						## Auth and Sale
						$output .= qq| <div id="divpayment$rec->{$cadidorders}"><a href="#order$col->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$fxcreditcard&$cadidorders=$col->{$cadidorders}&$cadidorderspayments=$col->{$cadidorderspayments}&e=$in{'e'}');delete_div('divorder$col->{$cadidorders}');delete_div('divpayment$col->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
						$output .= qq| <div id="divpayment$rec->{$cadidorders}"><a href="#order$col->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$fxccsale&$cadidorders=$col->{$cadidorders}&$cadidorderspayments=$col->{$cadidorderspayments}&e=$in{'e'}');delete_div('divorder$col->{$cadidorders}');delete_div('divpayment$col->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_fpauth.gif' title='Facil Pago Authorize/Capture' alt='' border='0'></a></div>|;					
					}elsif($col->{'Status'} eq 'Approved' and $col->{'AuthCode'} and $col->{'AuthCode'} ne '0000' and $col->{'Captured'} ne 'Yes'){
						## Capture & Force Capt
						$output .= qq| <div id="divpayment$col->{$cadidorderspayments}"><a href="#order$col->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$fxcapture&$cadidorders=$col->{$cadidorders}&$cadidorderspayments=$col->{$cadidorderspayments}&e=$in{'e'}');delete_div('divpayment$col->{$cadidorderspayments}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_cauth.gif' title='Capture' alt='' border='0'></a></div>|;
						($btns =~ /x/i) and ($output .= qq| <div id="divpayment$col->{$cadidorderspayments}"><a href="#order$col->{$cadidorders}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=$fxtocapture&$cadidorders=$col->{$cadidorders}&$cadidorderspayments=$col->{$cadidorderspayments}&e=$in{'e'}');delete_div('divpayment$col->{$cadidorderspayments}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xauth.gif' title='To Capture' alt='' border='0'></a></div>|);
					}
					$output .= "   </td>";
					$output .= "   <td class='smalltext' $decor valign='top' width='100'> $col->{'PmtField1'}</td>\n";
					$output .= "   <td class='smalltext' $decor valign='top' nowrap> $col->{'PmtField2'}<br>$col->{'PmtField3'}</td>\n";
					$output .= "   <td class='smalltext' $decor valign='top' width='40'> $col->{'PmtField4'}</td>\n";
					$output .= "   <td class='smalltext' $decor valign='top' width='50'> $col->{'PmtField5'}</td>\n";
					$output .= "   <td class='smalltext' $decor valign='top' width='110'> $col->{'Status'}<br>$col->{'AuthCode'}</td>\n";
					$output .= "   <td class='smalltext' $decor align='right' valign='top' nowrap> ".&format_price($col->{'Amount'})."<br>$col->{'Paymentdate'}</td>\n";
					$output .= "</tr>\n";
					$tot_payments += $col->{'Amount'};
					
				}elsif ($col->{'Type'}  eq 'Check'){
					if ($ptype ne $col->{'Type'} or !$ptype){
						$output .= qq|
										<tr>
											<td class='menu_bar_title'>&nbsp;</td>
											<td class='menu_bar_title'>Name on Check</td>
											<td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>
											<td class='menu_bar_title'>P/C</td>
											<td class='menu_bar_title'>D.O.B<br>License/State<br>Phone</td>
											<td class='menu_bar_title'>Status<br>Cod Auth</td>							
											<td class='menu_bar_title'>Amount</td>
										</tr>\n|;
					}
					$output .= " <tr bgcolor='$c[$d]'>\n";
					$output .= "   <td nowrap>";
					
					
					if($col->{'Status'} ne 'Cancelled' and (($col->{'Status'} ne 'Approved' or $col->{'AuthCode'} eq '0000') or ($col->{'Status'} eq 'Approved' and !$col->{'AuthCode'}))){
		
					#if ($col->{'Status'} ne 'Approved' or $col->{'AuthCode'} eq '0000'){
						$output .= qq| <div id="divpayment$rec->{$cadidorders}"><a href="#order$col->{$cadidorders}" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$col->{$cadidorders}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=certegycheck&$cadidorders=$rec->{$cadidorders}&$cadidorderspayments=$col->{$cadidorderspayments}&e=$in{'e'}');delete_div('divorder$col->{$cadidorders}');delete_div('divpayment$col->{$cadidorders}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Authorize' alt='' border='0'></a></div>|;
					}
					$output .= "   </td>";
					$output .= "   <td class='smalltext' valign='top'> $col->{'PmtField1'}</td>\n";
					$output .= "   <td class='smalltext' valign='top'> $col->{'PmtField2'}<br>$col->{'PmtField3'}<br>$col->{'PmtField4'}</td>\n";
					$output .= "   <td class='smalltext' valign='top'> $col->{'PmtField8'}</td>\n";
					$output .= "   <td class='smalltext' valign='top'> $col->{'PmtField5'}<br> $col->{'PmtField6'}<br>$col->{'PmtField7'}<br>$col->{'PmtField9'}</td>\n";
					$output .= "   <td class='smalltext' valign='top'> $col->{'Status'}<br>$col->{'AuthCode'}</td>\n";							
					$output .= "   <td class='smalltext' valign='top' align='right' nowrap> ".&format_price($col->{'Amount'})."</td>\n";
					$output .= "</tr>\n";
					$tot_payments += $col->{'Amount'};

					
				}elsif ($col->{'Type'} eq 'WesternUnion'){
				}
				$output .= "</table>\n";
				$ptype = $col->{'Type'};
			}
			

		}else{
			$output .= qq|
						<table border='0' cellspacing='0' width='100%'>
						  <tr>
						  	<td>No Payment defined</td>
						  </tr>
						</table>
						 |;
		}

		####################
		#### ORDERS NOTES
		#####################
		if ($rec->{'OrderNotes'} or $rec->{'BillingNotes'} or $rec->{'shp_Notes'}){
			$output .= qq|<table border="0" cellspacing="0" width="100%">
				<tr>
					<td class="menu_bar_title" width="33%">Order Notes</td>
					<td class="menu_bar_title" width="33%">Billing Notes</td>
					<td class="menu_bar_title" width="33%">Shp Notes</td>
				</tr>			
				<tr>
					<td class='help_on' width="33%">$rec->{'OrderNotes'}</td>
					<td class='help_on' width="33%">$rec->{'BillingNotes'}</td>
					<td class='help_on' width="33%">$rec->{'shp_Notes'}</td>
				</tr>
				</table>\n|;
		}
		$output .= "</td>\n";
		$output .= "  <td class='smalltext' align='right' valign='top' nowrap>".&format_price($tot_payments)."</td>\n";
		$output .= "</tr>\n";
		$output .= qq|
			<tr>
				<td colspan='3' bgcolor="#A4FFBB" height="1"></td>
			</tr>\n|;
	}
	return $output;
}

sub orders_wreport_cyb {
# --------------------------------------------------------
# Last Modified RB: 10/19/09  16:11:13 -- Se descartan pagos de ordenes que tengan un proceso de Return for Refund abierto


	my ($query) = @_;
	my ($rec,$sth,$sth2,$sth3,$col,@ary);
	require "../../common/apps/cybersubs.cgi";
	
	##('ID Order','Date','Amount','Auth Code','Payment Result')
	($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders),ID_customers,OrderNotes,BillingNotes,shp_Notes FROM $query;");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		#####################
		#### Payments List
		#####################
		my ($tot_payments);
		my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND Status!='Cancelled'");
		if ($sth2->fetchrow>0){				
			my ($sth1) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND Type='Credit-Card' AND Status!='Cancelled';");
			while ($col = $sth1->fetchrow_hashref){
				if (&date_to_unixtime($col->{'Paymentdate'}) > &date_to_unixtime(&get_sql_date()) or $col->{'Captured'} eq 'Yes'){
					## Skip						
				}elsif($col->{'Status'} ne 'Cancelled' and (($col->{'Status'} ne 'Approved' or $col->{'AuthCode'} eq '0000' or $col->{'AuthCode'} eq '') or ($col->{'Status'} eq 'Approved' and !$col->{'AuthCode'}))){

					## SALE
					##('ID Order','Date','Amount','Auth Code','Payment Result')
					$ary[0] = $rec->{'ID_orders'};
					$ary[1] = $col->{'Paymentdate'};
					$ary[2] = $col->{'Amount'};
					my ($status) = &check_ord_totals($rec->{'ID_orders'});
					if ($status eq 'OK' and $col->{'Amount'}>0){
						my ($sth3) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_plogs WHERE Date=Curdate() AND ID_orders='$rec->{'ID_orders'}' AND Data LIKE '%ID Payments : $col->{'ID_orders_payments'}%decision = REJECT%'");
						#JRG start 02-06-2008
						my ($cnt) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders='$rec->{'ID_orders'}' AND Type='Returned for Refund';");
						$total = $cnt->fetchrow;
						#JRG end 02-06-2008
						if ($sth3->fetchrow()>0){
							$ary[4] = "Payment Skipped, Order Already procesed (Denied) Today";
						}  elsif($total>0){#JRG start 02-06-2008
							#$ary[4] = "Skipped Order ATC folio status is open";#JRG start 02-06-2008
							$ary[4] = "Payment Skipped, Returned for Refund";
						}else{
							($status,$statmsg) = &sltvcyb_sale($rec->{'ID_orders'},$col->{'ID_orders_payments'});
							$statmsg =~ s/<br>/ /g;
							$ary[4] = $statmsg;
						}
						$ary[3] = &load_name('sl_orders_payments','ID_orders_payments',$col->{'ID_orders_payments'},'AuthCode');
					}elsif($col->{'Amount'}<0){
						$ary[4] = "Skipped : Credit Auth";
					}else{
						$ary[3] = 'N/A';
						$ary[4] = $status;
					}
			
					print '"'.join('","', @ary)."\"\n";
				}elsif($col->{'Status'} eq 'Approved' and $col->{'AuthCode'} and $col->{'AuthCode'} ne '0000' and $col->{'Captured'} ne 'Yes'){
					## Capture & Force Capt
				}
			}
		}
	}
	return;
}


sub orders_wreport_xls {
# --------------------------------------------------------
	my ($query) = @_;
	my ($output,$d,$rec,$sth, @cols);
	($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders),sl_orders.Date,ID_customers,OrderNotes,BillingNotes,shp_Notes, sl_orders.Status, sl_orders.StatusPrd, sl_orders.StatusPay FROM $query;");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		################
		####  ORDER INFO
		################
		$cols[0] = $rec->{'ID_orders'};
		$cols[1] = $rec->{'Date'};
		$cols[2] = $rec->{'ID_customers'};
		$cols[3] = $rec->{'StatusPrd'};
		$cols[4] = $rec->{'StatusPay'};		
		$cols[5] = $rec->{'Status'};
		print '"'.join('","', @cols)."\"\n";
	}
	return $output;
}


sub opr_orders_update {
# --------------------------------------------------------
 
	if ($in{'action'}){
		my ($filename,$key);
		foreach $key (keys %in){
			if ($key =~ /run(.*)/){
				$filename = $1;
				$in{'action'} = 'run';
				&auth_logging('opr_orders_capimp',$filename);
			}elsif($key =~ /del(.*)/){
				$filename = $1;
				$in{'action'} = 'del';
				unlink("$cfg{'path_cybersource'}/imports/$filename");
				&auth_logging('opr_orders_capdimp',$filename);
				$va{'message'} = &trans_txt('opr_orders_capdimp');
			}
		}
		if ($in{'action'} eq 'run'){
			&opr_orders_update_run($filename);
			return;
		}
	}	
	opendir (AUTHDIR, "$cfg{'path_cybersource'}/imports/") || &cgierr("Unable to open directory $cfg{'path_cybersource'}/imports/",604,$!);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
	closedir (AUTHDIR);
	
	if ($#files >=0){
		for (0..$#files){
			next if ($files[$_] =~ /^\./);		# Skip "." and ".." entries..
			$va{'searchresults'} .= qq|
			<tr>
				<td width="20%"><input type="submit" class="button" name="run$files[$_]" value="Run">
					<input type="submit" class="button" name="del$files[$_]" value="Del"></td>
				<td>$files[$_]</td>
			</tr>\n|;
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_update.html');
}


sub opr_orders_update_run {
# --------------------------------------------------------
# Last Modification by JRG : 03/09/2009 : Se agrega log
	my ($fname) = @_;
	my (%cdates);
#	if ($fname eq 'checks.csv'){
#		print "Content-type: application/vnd.ms-excel\n";
#		print "Content-disposition: attachment; filename=all_orders.csv\n\n";	
#		my ($sth) = &Do_SQL("SELECT DISTINCT(sl_orders.ID_orders) FROM `sl_orders` , sl_orders_payments WHERE sl_orders.ID_orders = sl_orders_payments.ID_orders and TYPE = 'Check' AND Authcode>0 AND sl_orders_payments.Status<>'Cancelled'"); 
#		while ($id_orders = $sth->fetchrow){
#			my ($sth2) = &Do_SQL("SELECT CapDate FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Type='Check' AND sl_orders_payments.Status<>'Cancelled' ORDER BY CapDate ASC"); 
#			$captdate = $sth2->fetchrow;
#			my ($sth2) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$id_orders'"); 
#			$rec = $sth2->fetchrow_hashref();
#			print "$id_orders,$captdate,$rec->{'Status'},$rec->{'Date'},".&load_name('sl_zipcodes','ZipCode',$rec->{'shp_Zip'},'CountyName').",$rec->{'shp_State'},$rec->{'OrderNet'},$rec->{'OrderShp'},$rec->{'OrderTax'},".&format_price($rec->{'OrderNet'}*$rec->{'OrderTax'})."\n";;
#		}
#		return;
#	}
  
	if (open (TXT, "<$cfg{'path_cybersource'}/imports/$fname")){
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=order_update.csv\n\n";

		my ($line,%rec,@ary,$output);
		my ($d_id_orders, $d_amount);
		my (@c) = split(/,/,$cfg{'srcolors'});
		LINE: while (<TXT>){
			$d_id_orders=0;
			$line = $_;
			$line =~ s/\r|\n//g;
			
			#@ary = split(/","/,$line);
			$line =~ s/"//g;
			$line =~ s/ics_auth,ics_bill/ics_auth-ics_bill/g;
			$line =~ s/,/, /g;
			@ary = split(/,/,$line);
			# Date 
			
			##if ($ary[$#ary-16] =~ /ics_bill/ and $ary[$#ary-15] eq ' accept' and $ary[$#ary-17] =~ /Visa|MasterCard/){
			##if ($ary[$#ary-16] =~ /ics_credit/ and $ary[$#ary-15] eq ' accept' and $ary[$#ary-17] =~ /Visa|MasterCard/){	
			###if ($ary[$#ary-16] =~ /ics_bill|ics_credit/ and $ary[$#ary-15] eq ' accept' and $ary[$#ary-17] =~ /Visa|MasterCard/){
			if ($ary[$#ary-16] =~ /ics_bill|ics_credit/ and $ary[$#ary-15] eq ' accept'){
       
				#$ary[2] =~ s/\s//g;
				$ary[1]  =~ s/\s//g;
				$ary[3] = int($ary[3]);
				$ary[$#ary-8] =~ s/\s//g;
				my ($sth) = &Do_SQL("SELECT CONVERT_TZ('$ary[2]', 'GMT', 'US/Pacific') as date;");
				$rec = $sth->fetchrow_hashref();
				$captdate = substr($rec->{'date'},0,10);
				$cdates{$captdate} += $ary[$#ary-8];
				if ($line =~ /ID Order : (\d+) /){
					$id_orders = $1;
				}elsif ($ary[3]>0 and $ary[3]< 999999){
					$id_orders = $ary[3];
				}elsif ($ary[9]>0 and $ary[9]< 999999){
					$id_orders = $ary[9];	
				}else{
					my ($sth) = &Do_SQL("SELECT ID_orders FROM sl_orders_plogs WHERE Data like '%$ary[1]%';");
					$id_orders = $sth->fetchrow;
				}
				##if (!$id_orders and $ary[19] ne 'null@cybersource.com'){
				##	my ($sth) = &Do_SQL("SELECT ID_orders FROM sl_customers WHERE Data like '%$ary[1]%';");
				##}				
				if ($id_orders>0){ 
					#&cgierr("Javier:$id_orders=(1)$ary[1]=(2)$ary[2]=(3)$ary[3]=(4)$ary[4]=(5)$ary[5]=(6)$ary[6]=(7)$ary[7]=(8)$ary[8]=(9)$ary[9]=(10)$ary[10]=(11)$ary[11]=(12)$ary[12]=(13)$ary[13]=(14)$ary[14]=(15)$ary[15]=(16)$ary[16]=(44)$ary[44]=(46)$ary[46]");
					$d_id_orders=0; $d_amount=0.00;
					$d_amount = sprintf("%.2f", $ary[44]);
					
					$ary[46] =~ s/ //g;
					my ($sth1) = &Do_SQL("SELECT ID_orders
																FROM  sl_orders
																WHERE ID_orders = '$id_orders'");
					$d_id_orders=$sth1->fetchrow;	
					if ($d_id_orders == $id_orders){
						my ($sth2) = &Do_SQL("SELECT ID_orders_payments
																	FROM  sl_orders_payments
																	WHERE ID_orders = '$id_orders' and AuthCode = '$ary[46]' and 
																	      Amount = '$d_amount' and Status ='Approved' ");
						$d_id_orders_payments = $sth2->fetchrow;	
						#&cgierr("Javier:$d_id_orders_payments =>$id_orders=(46)$ary[46]=(2)$ary[2]=(3)$ary[3]=(4)$ary[4]=(5)$ary[5]=(6)$ary[6]=(7)$ary[7]=(8)$ary[8]=(9)$ary[9]=(10)$ary[10]=(11)$ary[11]=(12)$ary[12]=(13)$ary[13]=(14)$ary[14]=(15)$ary[15]=(16)$ary[16]=(44)$ary[44]=(46)$ary[46]");
						if ($d_id_orders_payments > 0){
							$ary[2] =~ s/ //g;
							$d_date =  substr($ary[2],0,10);
							#&cgierr("Javier:=$d_date=$id_orders=(35)$ary[35]=(2)$ary[2]=(3)$ary[3]=(4)$ary[4]=(5)$ary[5]=(6)$ary[6]=(7)$ary[7]=(8)$ary[8]=(9)$ary[9]=(10)$ary[10]=(11)$ary[11]=(12)$ary[12]=(13)$ary[13]=(14)$ary[14]=(15)$ary[15]=(16)$ary[16]=(44)$ary[44]=(46)$ary[46]");
							my ($sth3) = &Do_SQL("UPDATE sl_orders_payments
																	set  CapDate = '$d_date',Captured='Yes'
																	WHERE ID_orders = '$id_orders' and AuthCode = '$ary[46]' and 
																	       Status ='Approved'");
							&auth_logging('orders_payments_updated',$id_orders);										       
							print '"'.$d_id_orders.'","'.$d_id_orders_payments.'","'.$ary[46].'","'.$d_amount.'","'.$d_date.'","'.$ary[35]."\"\n";																	       
						} 												
					}
					
#					my ($sth) = &Do_SQL("SELECT ID_orders 
#																FROM sl_orders_payments 
#																WHERE id_orders =	$id_orders and 
#																			AuthCode = '$ary[46]'  ;");
#					$rec = $sth->fetchrow_hashref();					
					#$va{'searchresults'} .= "$ary[$#ary-16],$id_orders,$captdate,".&load_name('sl_zipcodes','ZipCode',$rec->{'shp_Zip'},'CountyName').",$rec->{'shp_State'},$rec->{'OrderNet'},$rec->{'OrderShp'},$rec->{'OrderTax'},".&format_price($rec->{'OrderNet'}*$rec->{'OrderTax'})."\n";
					#print "$ary[$#ary-16],$id_orders,$captdate,".&load_name('sl_zipcodes','ZipCode',$rec->{'shp_Zip'},'CountyName').",$rec->{'shp_State'},$rec->{'OrderNet'},$rec->{'OrderShp'},$rec->{'OrderTax'},".&format_price($rec->{'OrderNet'}*$rec->{'OrderTax'})."\n";
				}				
			}	
			@ary="";
			$line="";
			@ary="";
			$output="";
			next LINE;		
		
			
			### "Status","CardType","OrderNumber","Date","TransRefNo","AccountSuffix","Amount","CustomerData","CustomerId","Comments","SourceUser"
#			if ($#ary eq 10){
#				next LINE;
#			}elsif($#ary eq 7){
#				$rec{'PmtField1'} = $ary[1] .'&nbsp;'.$ary[7];
#				$rec{'ID_orders'} = $ary[2];
#				$rec{'captDate'} = $ary[3];
#				$rec{'TransRefNo'} = $ary[4];
#				$rec{'Amount'} = $ary[6];
#				($mm,$dd,$yy,$null) = split(/\s|\//,$rec{'captDate'},4);
#				$rec{'cdate'} = "$yy-$mm-$dd";
#			}elsif($#ary eq 3){
#				if ($rec{'ID_orders'} ne '<Null>' and $rec{'ID_orders'} > 100000){
#					$rec{'ID_customer'} = $ary[1];
#					$rec{'ID_orders'} = $ary[2];
#				}
#				$done = 1;
#			}elsif($#ary eq -1){
#
#			}
#			if ($done){
#				$done = 0;
#				$output = '';
#				$d = 1 - $d;
#				$va{'searchresults'} .= qq|
#			<tr bgcolor='$c[$d]'>
#				<td class="smalltext"><a name="#order$rec{'ID_orders'}" id="order$rec{'ID_orders'}"></a>$rec{'captDate'} </td>
#				<td align='center' class="smalltext">$rec{'PmtField1'}</td>
#				<td align='center' class="smalltext"><a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec{'ID_orders'}&tab=2#tabs'>$rec{'ID_orders'}</a></td>
#				<td align='center' class="smalltext">$rec{'ID_customer'}</td>
#				<td align='center' class="smalltext">|.&format_price($rec{'Amount'}).qq|</td>
#			</tr>
#			<tr>
#				<td colspan="5" bgcolor='$c[$d]' align='center' class="smalltext">\n|;
#				
#				### Check if the transaction has been Proceesed already
#				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_import_log WHERE ID_import_log='$rec{'TransRefNo'}' AND Type='Cybersource';");
#				if ($sth->fetchrow()>0){
#					$va{'searchresults'} .= "Transaction Already been Imported ";
#				}else{
#					### Check if the transaction has been registered in SOSL
#					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$rec{'ID_orders'}' AND Type='Credit-Card' AND Status!='Cancelled' AND Amount='$rec{'Amount'}';");
#					$matches = $sth->fetchrow();
#					if ($matches == 1){
#						## Only One Transaction
#						
#						$va{'searchresults'} .= "Credit Card Captured on : $rec{'cdate'}";
#						my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET  Captured='Yes', CapDate='$rec{'cdate'}' WHERE ID_orders='$rec{'ID_orders'}' AND Type='Credit-Card' AND Status!='Cancelled' AND Amount='$rec{'Amount'}';");
#						my ($sth) = &Do_SQL("INSERT INTO sl_import_log SET ID_import_log='$rec{'TransRefNo'}',Type='Cybersource',ID_orders='$rec{'ID_orders'}',IData='---',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
#					}elsif (!$matches){
#						$va{'searchresults'} .= "Unable to find the Order";
#					}else{
#						## Choose the right one
#						$va{'searchresults'} .= qq|
#							<table border='0' cellspacing='0' width='100%'>
#								  <tr>
#										<td class='menu_bar_title'>&nbsp;</td>
#										<td class='menu_bar_title'>Type</td>
#										<td class='menu_bar_title'>Name on Card<br>Card Number</td>
#										<td class='menu_bar_title'>Exp</td>
#										<td class='menu_bar_title'>CVN</td>
#										<td class='menu_bar_title'>Status<br>Cod Auth</td>			
#										<td class='menu_bar_title'>Amount</td>
#								   </tr>\n|;
#					
#					
#						my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$rec{'ID_orders'}' AND Type='Credit-Card' AND Status!='Cancelled' ORDER BY ID_orders_payments DESC;");
#						while ($col = $sth->fetchrow_hashref){
#							$va{'searchresults'} .= " <tr>\n";
#							$va{'searchresults'} .= qq|   <td nowrap> <div id="divpayment$rec{'ID_orders'}"><a href="#order$rec{'ID_orders'}" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'order$rec{'ID_orders'}');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=importcapture&id_orders=$col->{'ID_orders'}&id_orders_payments=$col->{'ID_orders_payments'}&cdate=$rec{'cdate'}&refnum=$rec{'TransRefNo'}&e=$in{'e'}');delete_div('divorder$col->{'ID_orders'}');delete_div('divpayment$col->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_pauth.gif' title='Set as Captured' alt='' border='0'></a></div></td>|;
#							$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $col->{'PmtField1'}</td>\n";
#							$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $col->{'PmtField2'}<br>$col->{'PmtField3'}</td>\n";
#							$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $col->{'PmtField4'}</td>\n";
#							$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $col->{'PmtField5'}</td>\n";
#							$va{'searchresults'} .= "   <td class='smalltext' $decor valign='top'> $col->{'Status'}<br>$col->{'AuthCode'}</td>\n";
#							$va{'searchresults'} .= "   <td class='smalltext' $decor align='right' valign='top' nowrap> ".&format_price($col->{'Amount'})."<br>$col->{'Paymentdate'}</td>\n";
#							$va{'searchresults'} .= "</tr>\n";
#							
#						}
#						$va{'searchresults'} .= "</table>\n";
#					}
#				}
#				
#				$va{'searchresults'} .= "</td>";
#				$va{'searchresults'} .= qq|
#			<tr>
#				<td colspan='5' height="2" bgcolor="#CEFFCE"></td>
#			</tr>\n|;
#			}
		}
		#$va{'searchresults'} .= "=============<br>";
		#foreach $key (sort keys %cdates){
		#		$va{'searchresults'} .= "$key \t ".&format_price($cdates{$key})."<br>";
		#}
#	}else{
#		$va{'searchresults'} .= qq|
#			<tr>
#				<td colspan='5' align='center'>Unable to open the File : $!</td>
#			</tr>\n|;
	}

	return;
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_update_run.html');
}



#################################################################
# OPERATIONS :SETUP     #
#################################################################
sub opr_check {
# --------------------------------------------------------
	my ($sth);
	## Checking Permission
	if ($in{'action'}){
		my ($query);
		if ($in{'drop'}){
			 ($sth) = &Do_SQL("DELETE FROM cleanup_temp WHERE ID_cleanup_temp='$in{'drop'}';");
		}
		$in{'form_id'} = int($in{'form_id'});
		$in{'to_id'} = int($in{'to_id'});
		if ($in{'form_id'} and $in{'to_id'}){
			$query = "WHERE sl_orders.ID_orders >= '$in{'form_id'}' AND sl_orders.ID_orders <= '$in{'to_id'}'";
		}elsif ($in{'to_id'}){
			$query = "WHERE sl_orders.ID_orders <= '$in{'to_id'}'  ";
		}elsif ($in{'form_id'}){
			$query = "WHERE sl_orders.ID_orders >= '$in{'form_id'}'  ";
		}
		if (!$query){
			if ($in{'form_date'} and $in{'to_date'}){
				$query = "WHERE Date >= '".&filter_values($in{'form_date'})."' AND Date <= '".&filter_values($in{'to_date'})."'";
			}elsif ($in{'to_date'}){
				$query = "WHERE Date <= '".&filter_values($in{'to_date'})."'  ";
			}elsif ($in{'form_date'}){
				$query = "WHERE Date >= '".&filter_values($in{'form_date'})."'  ";
			}
		}
		
		
		####
		####  Query Especial para $in{'checktype'} eq 'msgs'
		####
		if ($in{'checktype'} eq 'msgs'){
			if ($query){
				$query .= " AND cleanup_temp.ID_orders=sl_orders.ID_orders";
			}else{
				$query = " WHERE cleanup_temp.ID_orders=sl_orders.ID_orders";
			}
			($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,cleanup_temp $query");
		}else{
			($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders $query");
		}
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0 ){
			&opr_check_list($query);
			return;
		}else{
			$va{'message'} = &trans_txt('search_nomatches');
		}
	}

	print "Content-type: text/html\n\n";
	print &build_page('opr_check.html');
}

sub opr_check_list {
# --------------------------------------------------------
	my ($query) = @_;
	my ($orderby);
	if ($in{'checktype'} eq 'msgs'){
		$query = "SELECT sl_orders.ID_orders,ID_customers,Date,StatusPrd,StatusPay,Status,ID_cleanup_temp FROM sl_orders,cleanup_temp $query";
	}else{
		$query = "SELECT ID_orders,ID_customers,Date,StatusPrd,StatusPay,Status FROM sl_orders $query";
	}
	#$va{'matches'} = 0;
	
	#my ($sth) = &Do_SQL("$query");
	#while ($rec = $sth->fetchrow_hashref()){
	#	if ($in{'checktype'} eq 'Totals'){
	#		$message = &check_ord_totals($rec->{'ID_orders'});
	#	}else{
	#		$message =  &check_ord_status($rec->{'ID_orders'});
	#	}
	#	if ($message ne 'OK'){
	#		++$va{'matches'};
	#	}
	#}
	$usr{'pref_maxh'} = 50;
	
	if ($in{'form_id'} or $in{'to_id'}){
		$orderby = "ID_orders";
	}else{
		$orderby = "Date";
	}
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
	($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});	
	my (@cols) = ('form_date','erroronly','form_id','checktype','cmd','to_id','to_date','nh','action');
	my ($qs);
	for (0..$#cols){
		$qs .= "$cols[$_]=$in{$cols[$_]}&";
	}
	my ($sth) = &Do_SQL("$query ORDER BY $orderby  LIMIT $first,$usr{'pref_maxh'}");
	my ($rec,$message);
	my (@c) = split(/,/,$cfg{'srcolors'});
	RECORD: while ($rec = $sth->fetchrow_hashref()){
		if ($in{'checktype'} eq 'msgs'){
			$message = 'OK';
		}elsif($in{'checktype'} eq 'Totals'){
			$message = &check_ord_totals($rec->{'ID_orders'});
		}else{
			$message =  &check_ord_status($rec->{'ID_orders'},$rec->{'StatusPrd'},$rec->{'StatusPay'},$rec->{'Status'});
		}
		if ($message eq 'OK'){
			$message = &load_name('cleanup_temp','ID_orders',$rec->{'ID_orders'},'Message');
			if (!$message){
				$message = 'OK';
			}else{
				$message = qq|&nbsp;<a href="/cgi-bin/mod/admin/admin?$qs&drop=$rec->{'ID_cleanup_temp'}">$message</a>|;
			}
		}
		if ($message eq 'OK' and $in{'erroronly'}){
			next RECORD;
		}
		$d = 1 - $d;
		$va{'searchresults'} .= qq|
			<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick="trjump('/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2')">
				<td class="smalltext" align="right" valign="top" nowrap>$rec->{'ID_orders'}</td>
				<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Date'}</td>
				<td class="smalltext" nowrap class="help_on" valign="top">|. &load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},'[FirstName] [LastName1] [LastName2]').qq|</td>
				<td class="smalltext" nowrap class="help_on" valign="top" nowrap>$rec->{'StatusPrd'}<br>
											$rec->{'StatusPay'}<br>
											$rec->{'Status'}</td>
				<td class="smalltext" class="help_on" valign="top">$message</td>
			</tr>\n|;
	}
	if (!$va{'searchresults'}){
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_check_list.html');	
}






sub opr_checkfile_run {
# --------------------------------------------------------
# Last Modification by JRG : 03/09/2009 : Se agrega log
	my ($lines,$errors,$skus,$multi);
	open (CFG, "<$cfg{'path_cufiles'}$in{'form_file'}") or &cgierr ("Unable to open: $cfg{'path_cufiles'}$in{'form_file'},150,$!");
	LINE: while (<CFG>){
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		++$lines;
		if ($in{'filetype'} eq 'pcs'){
			@ary = split(/\t/, $_);
			$ary[0] = &fixdate($ary[0],'mdy');
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$ary[1]'");
			if ($sth->fetchrow()>0){
				my ($sth) = &Do_SQL("SELECT Status FROM sl_orders WHERE ID_orders='$ary[1]'");
				if ($sth->fetchrow() ne 'Shipped'){
					my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$ary[1]',Message='PC Shipped but the Status is not Shipped'");	
					++$errors;
					next LINE;
				}
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$ary[1]' AND Status='Active'");
				if ($sth->fetchrow()>1){
					my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$ary[1]',Message='PC Shipped on $ary[0] but the orther has multiitems'");	
					++$errors;
					++$multi;
					next LINE;
				}else{
					my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ShpDate='$ary[1]' WHERE ID_orders='$ary[1]' AND Status='Active'");
					&auth_logging('orders_products_updated',$ary[1]);
				}
			}
		}
	}
	$va{'cleanupresult'} = qq|
		Lines Imported : $lines<br>
		MultiItems : $multi<br>
		Errors : $errors<br>	
		SKUs Checked :$skus<br>
	|;
	delete($in{'action'})
	&opr_checkfile();
}



sub opr_checkfile_run2 {
# --------------------------------------------------------
# Last Modification by JRG : 03/09/2009 : Se agrega el log

	my $totLines = 0;
	my $totok = 0;
	my $totok_ = 0;
	
	@dsinnova = ('827866','960293','141552','708468','685562','195818','511265','462446','634230','621234','486625','392000');
	@dseagle = ('874613','714509','441340','988139','518660','968708');
	#,'843279','298344','556060','874565','773315');
	        	       	 
	
	$file = $in{'form_file'};
	$tracking = "";
	$shpProv = "";

	open (CFG, "<$file") or &cgierr ("Unable to open: $file,150,$!");
	LINE: while (<CFG>){
		$line = $_;
		
		#my ($date,$idorders,$idproduct) = split (/,/, $line);
		my ($date,$idorders,$idproduct,$shpProv,$tracking) = split (/,/, $line); 
		(!$idorders) and (next LINE);
		
		$shpProv =~ s/\s+$//;
		$idproduct =~ s/-//;
	
		if($idorders != ""){
			my $_1 = '';
			my $_2 = '';
			my $_3 = '';	
			my $er = 0;	
			my ($sthd) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders = $idorders");
			$rec = $sthd->fetchrow_hashref();
			my $idorder = $rec->{'ID_orders'};	
			my $net  = $rec->{'OrderNet'};
			my $ship = $rec->{'OrderShp'};
			my $tax = $rec->{'OrderTax'}*100;
			my $qty = $rec->{'OrderQty'};
			my $totalOrder = $net+$ship+$tax;
		
			if($idorder != ""){
				# Test 1: The OrderNet must be equal to the total of the products Price
				my ($storpr)= &Do_SQL("SELECT SUM(SalePrice) AS tprice FROM sl_orders_products WHERE ID_orders = $idorders AND Status = 'Active'");
				$totalProduct = $storpr->fetchrow();
				
				# Test 2: The TotalPay must be equal to the total of payments
				my ($storpay) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = $idorders and Status != 'Cancelled' ORDER BY Date");
				$payments = $storpay->fetchrow();
				
				# Test3 The idproduct must be equal in sl_orders_products , sl_products and the file
				#if($idproduct != ""){
				#	($tracking == "") and ($idproduct = substr($idproduct,0,6));
				#	($tracking != "") and ($idproduct = substr($idproduct,3,6));
				#	my ($storpr)= &Do_SQL("SELECT COUNT(*) AS valid FROM sl_orders_products INNER JOIN sl_products WHERE RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products AND sl_orders_products.ID_orders = $idorders AND sl_products.ID_products = $idproduct AND sl_orders_products.Status = 'Active' GROUP BY sl_products.ID_products");
				#	$validsku = $storpr->fetchrow();
				#}else{ 
				#	$validsku = 1;
				#}
				my (@ids) = split(/\s+|,|\s+,/,); 
				
				if($totalProduct == $net and $payments == $totalOrder and $validsku == 1){
					$msg = "0k";
				}elsif($totalProduct == $net and $payments == $totalOrder){
					$msg = "Item Error";
					$er = 1;	
				}elsif($totalProduct == $net and $validsku == 1){
					$msg = "Payments Error";
					$er = 1;	
				}elsif($payments == $totalOrder and $validsku == 1){
					$msg = "Total Order Error";
					$er = 1;		
				}elsif($totalProduct == $net){
					$msg = "Payments and Item error";
					$er = 1;	
				}elsif($payments == $totalOrder){
					$msg = "Total Order and Item error";	
					$er = 1;
				}elsif($validsku == 1){
					$msg = "Total Order and Payments error";	
					$er = 1;
				}else{
					$msg = "Error";	
					$er = 1;
				}
					
				if($er == 0 ){
					
					@ardate = split (/\//, $date);
					$date  = "$ardate[2]-$ardate[0]-$ardate[1]";
				
					#Seting the ShipDate to date We have
					($tracking != "") and (&Do_SQL("UPDATE sl_orders_products SET Tracking = '$tracking',ShpProvider = '$shpProv' WHERE ID_orders = $idorders AND RIGHT(ID_products,6) = $idproduct "));
					&Do_SQL("UPDATE sl_orders_products SET ShpDate = '$date' WHERE ID_orders = $idorders ");
					&auth_logging('orders_products_updated',$idorders);
				  
					#Seting PaymentDate to date We have
					my ($stdates) = &Do_SQL("SELECT ID_orders_payments,CapDate FROM sl_orders_payments WHERE ID_orders = $idorders and Status != 'Cancelled' ORDER BY Amount DESC");
					my $flag = 0;
					my $i = 1;
			  		while($recd = $stdates->fetchrow_hashref()){
						&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = DATE_ADD('$date',INTERVAL 30*($i-1) DAY) WHERE ID_orders_payments = $recd->{'ID_orders_payments'} "); 
						&auth_logging('orders_payments_updated',$idorders);
						$i++;
					
						## Checking the CapDate
						if($recd->{'CapDate'} eq "" or $recd->{'CapDate'} eq "0000-00-00"){
							$msg = "0k - To Capture";
							$totok_++;
							$flag = 1;
						}
						
						## Multiple Items in Order
						(length($idproduct) > 15) and ($msg .= " - Multiple Items");	
					}
					
					($flag == 0) and ($totok++);
					
					#Set Order to Shipped
					&Do_SQL("UPDATE sl_orders SET Status = 'Shipped' WHERE ID_orders = $idorders");
					#&auth_logging('opr_orders_updated',$idorders);
					&auth_logging('opr_orders_stShipped',$id_orders);
					&status_logging($id_orders,'Shipped');
				}
		
			}else{ $msg = "Order not Found";}
				## Then insert the results into cleanup_temp.
				&Do_SQL("INSERT INTO cleanup_temp VALUES(0,$idorders,'$msg')");
			}		
			$totLines++;
		}
		close CFG;	
	
		$va{'message'} = "Total Processed Order: $totLines<br>
											Total 0k Orders: $totok<br>
											Total 0k-ToCapture Orders: $totok_<br>
											Total Bad Orders:".($totLines-$totok-$totok_);
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_check_orders.html');
}




sub opr_refill{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 10/09/2008
# Last Modified on: 
# Last Modified by: 
# Description : check all orders to make refill and its movements
# Forms Involved: 
# Parameters : none
# Last Modified on: 03/17/09 16:44:20
# Last Modified by: MCC C. Gabriel Varela S: parametros para sltv_itemshipping
# Last Modified by RB on 12/07/2010: Se agregaron parametros para el calculo de shipping
# Last Modified by RB on 04/15/2011 12:27:30 PM : Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:36:31 PM : Se agrega City como parametro para calculate_taxes


	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products, sl_services WHERE sl_orders_products.ID_products=CONCAT('60000',sl_services.ID_services) AND sl_services.ServiceType='Refill' AND sl_orders_products.Status='Active'");
	while ($row = $sth->fetchrow_hashref){
		$posted = &check_posteddate($row->{'ID_orders_products'});
		$va{'test'}	.= "<br>ORDEN:$row->{'ID_orders'} - SERVICIO:$row->{'ID_products'} - PRODUCTO REFILL:$row->{'ID_products_related'} - REFILL:$row->{'Days'} dias <br>";
		$id_customers = &load_name('sl_orders','ID_orders',$row->{'ID_orders'},'ID_customers');
		if($posted ne "0000-00-00" && $posted ne "NULL" && $posted){
			$va{'test'} .= "<table border=1><tr><td>Fecha Actual</td><td>Dias desde el PostedDate</td><td>Dias para el envio</td><td>Ordenes</td><td>Ordenes Enviadas</td><td>Mensaje</td></tr>";
			$va{'msg'} = "";
			$dia = $posted;
			for($x=0; $x<=150; $x++){
				$va{'msg'} = "";
				my ($sthe) = &Do_SQL("SELECT DATE_ADD('$dia', INTERVAL 1 DAY)");
				$dia = $sthe->fetchrow;
				
				my ($sthd) = &Do_SQL("SELECT DATEDIFF('$dia','$posted')");		#######cambiar a now()
				$dif = $sthd->fetchrow;
				$sends = sprintf("%d",($dif / $row->{'Days'})+1);
				$charges = $dif % $row->{'Days'};
				my ($stho) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers=$id_customers AND (ID_orders='$row->{'ID_orders'}' OR ID_orders_related='$row->{'ID_orders'}')");
				$count = $stho->fetchrow;
				if($sends > $count){
					my($sthor) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$row->{'ID_orders'}'");
					$old_ord = $sthor->fetchrow_hashref;
					my (@dbcols) = ('ID_customers','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','BillingNotes','shp_type','shp_name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Country','shp_Notes','ID_pricelevels','question1','answer1','question2','answer2','question3','answer3','question4','answer4','question5','answer5');
					my ($query) = "";
					for (0..$#dbcols){
						if($old_ord->{$dbcols[$_]}){
							$query .= "$dbcols[$_]='$old_ord->{$dbcols[$_]}',";
						}
					}
					$qo{'orderqty'}=1;
					$edt = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'edt');
					$sizew = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeW');
					$sizeh = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeH');
					$sizel = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SizeL');
					$size = $sizew*$sizeh*$sizel;
					
					$id_packing = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'ID_packingopts');
					$shpcal = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'shipping_table');
					$shpdis = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'shipping_discount');
					
					($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$sizew,$id_packing,$shpcal,$shpdis,substr($row->{'ID_products_related'},3,6));
					$oldordertype = $old_ord->{'shp_type'};
					if($row->{'shp_State'} eq 'PR-Puerto Rico' && $oldordertype){
						$oldordertype .= 'pr';
					}
					$qo{'ordershp'} = $va{'shptotal'.$oldordertype};
					$sprice = &load_name('sl_products','ID_products',substr($row->{'ID_products_related'},3,6),'SPrice');
					if(substr($row->{'ID_products_related'},3,6) =~ /$cfg{'disc40'}/){
						$qo{'orderdisc'} = $sprice * 40/100;
					}elsif (substr($row->{'ID_products_related'},3,6) =~ /$cfg{'disc30'}/){
						$qo{'orderdisc'} = $sprice * 30/100;
					} else {
						$qo{'orderdisc'} = 0;
					}
					$qo{'ordertax'} = &calculate_taxes($old_ord->{'shp_Zip'},$old_ord->{'shp_State'},$old_ord->{'shp_City'},$row->{'ID_orders'});
					$qo{'ordernet'} = $sprice;
					$qo{'dayspay'} = 1;
					$qo{'repeatedcustomer'} = 'Yes';
					my (@cols) = ('OrderQty','OrderShp','OrderDisc','OrderTax','OrderNet','dayspay','repeatedcustomer');
					for(0..$#cols){
						$column = lc($cols[$_]);
						if($qo{$column}){
							$query .= "$cols[$_]='$qo{$column}',";
						} else {
							$query .= "$cols[$_]='0',";
						}
					}
					$total = $qo{'ordernet'}+$qo{'ordershp'}-$qo{'orderdisc'}+(($qo{'ordernet'}-$qo{'orderdisc'})*$qo{'ordertax'});
##creating payment					
					my($sthpa) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$row->{'ID_orders'}' ORDER BY Paymentdate LIMIT 1");
					$query_p = "";
					$pay = $sthpa->fetchrow_hashref;
					for my $i(1..9){
						$column = "PmtField".$i;
						$query_p .= $column."='".$pay->{$column}."', ";
					}
					my ($sth_pay) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$row->{'ID_orders'}',Type='Credit-Card', $query_p Amount='$total',Paymentdate=Curdate(), Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					$new_id_orders_payments = $sth_pay->{'mysql_insertid'};
					require "../../common/apps/cybersubs.cgi";
					my ($status,$msg,$code) = &sltvcyb_auth($row->{'ID_orders'}, $new_id_orders_payments);
					if($status eq "OK"){
##creating order											
						my ($sth_ord) = &Do_SQL("INSERT INTO sl_orders SET $query StatusPrd='None',StatusPay='None',Status='".$cfg{'orderrefillstatus'}."',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
						$new_id_orders = $sth_ord->{'mysql_insertid'};
##switch payment to new order						
						my ($sth_up) = &Do_SQL("UPDATE sl_orders_payments SET ID_orders='$new_id_orders' WHERE ID_orders_payments='$new_id_orders_payments'");
						$va{'msg'} .= "pago autorizado - orden nueva $new_id_orders ";
						my ($sth_rel) = &Do_SQL("UPDATE sl_orders SET ID_orders_related=$row->{'ID_orders'} WHERE ID_orders='$new_id_orders'");
##creating product
						my ($sth_pro) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$new_id_orders',ID_products='$row->{'ID_products_related'}', Related_ID_products='$row->{'ID_products'}', Quantity='1',SalePrice='$qo{'ordernet'}',Shipping='$qo{'ordershp'}',Tax='$qo{'ordertax'}',Discount='$qo{'orderdisc'}',FP='1', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					} elsif ($status ne "OK" && $charges == ($row->{'Days'}-1)){
						my ($sth_in) = &Do_SQL("UPDATE sl_orders_products SET Status='Inactive' WHERE ID_orders_products='$row->{'ID_orders_products'}' ");
						$va{'msg'} .= "refill inactivo ";
						$x=151;
					} elsif(status ne "OK"){
						$va{'msg'} .= "pago rechazado ";
					}
				}
				$diasparaelenvio = $row->{'Days'}-$charges;
				$va{'test'}	.= "<tr><td>$dia</td><td>$dif</td><td>$diasparaelenvio</td><td>$sends</td><td>$count</td><td>$va{'msg'}&nbsp;</td></tr>";
			}
		$va{'test'}	.= "</table>";			
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_refill.html')	
}


##################################################################
#    OPERATIONS : PREORDERS   	#
##################################################################

sub opr_orders_payments{
#-----------------------------------------
# Created on: 11/25/08  10:21:16 By  Roberto Barcenas
# Forms Involved: opr_preorders_payments_list 
# Description : Sow the list of layaway divided by payment
# Parameters : 	
	
	my ($sth,$mod);
	
	$query 	=		'';
	$mod 		=		'';
	
	($in{'range'} eq 'today') and ($mod = ' AND PaymentDate = CURDATE() ') and ($mod2=' AND PaymentDate < CURDATE() ');
	($in{'range'} eq '3d') 		and ($mod = ' AND PaymentDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 3 DAY) AND CURDATE() ') 	and ($mod2=' AND PaymentDate < DATE_SUB(CURDATE(), INTERVAL 3 DAY) ');
	($in{'range'} eq '7d') 		and ($mod = ' AND PaymentDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE() ')		and ($mod2=' AND PaymentDate < DATE_SUB(CURDATE(), INTERVAL 7 DAY) ');
	($in{'range'} eq '15d') 	and ($mod = ' AND PaymentDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 15 DAY) AND CURDATE() ')	and ($mod2=' AND PaymentDate < DATE_SUB(CURDATE(), INTERVAL 15 DAY) ');
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments INNER JOIN (SELECT ID_orders, COUNT( ID_orders ) AS FP
									FROM sl_orders_payments WHERE STATUS NOT IN('Cancelled','Void') GROUP BY ID_orders) AS fp
									ON sl_orders_payments.ID_orders = fp.ID_orders
									LEFT JOIN (SELECT ID_orders, COUNT( ID_orders ) AS Denied
									FROM sl_orders_payments WHERE STATUS = 'Denied' $mod2 GROUP BY ID_orders) AS d
									 ON sl_orders_payments.ID_orders = d.ID_orders
									INNER JOIN (SELECT ID_orders, COUNT( ID_orders ) AS Done FROM sl_orders_payments
									WHERE STATUS = 'Approved' AND Captured = 'Yes' $mod2 GROUP BY ID_orders) AS p 
									ON sl_orders_payments.ID_orders = p.ID_orders
									INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_payments.ID_orders
									$mod AND sl_orders.Status = 'Processed' and Ptype!='Credit-Card' ORDER BY sl_orders.Date");
									
	$va{'matches'} = $sth->fetchrow();
	
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my (@c) = split(/,/,$cfg{'srcolors'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
	
		$sth = &Do_SQL("SELECT sl_orders.ID_orders, sl_orders_payments.Status, IF( Denied >0, Denied, 0 )AS Denied , Done, FP, sl_orders.Date, PaymentDate 
									FROM sl_orders_payments INNER JOIN (SELECT ID_orders, COUNT( ID_orders ) AS FP
									FROM sl_orders_payments WHERE STATUS NOT IN('Cancelled','Void') GROUP BY ID_orders) AS fp
									ON sl_orders_payments.ID_orders = fp.ID_orders
									LEFT JOIN (SELECT ID_orders, COUNT( ID_orders ) AS Denied
									FROM sl_orders_payments WHERE STATUS = 'Denied' $mod2 GROUP BY ID_orders) AS d
									ON sl_orders_payments.ID_orders = d.ID_orders
									INNER JOIN (SELECT ID_orders, COUNT( ID_orders ) AS Done FROM sl_orders_payments
									WHERE STATUS = 'Approved' AND Captured = 'Yes' $mod2 GROUP BY ID_orders) AS p 
									ON sl_orders_payments.ID_orders = p.ID_orders
									INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_payments.ID_orders
									$mod AND sl_orders.Status = 'Processed' and Ptype!='Credit-Card' ORDER BY PaymentDate DESC, sl_orders.Date LIMIT $first,$usr{'pref_maxh'};");
	
	
		while($rec = $sth->fetchrow_hashref()){
	
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
					<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onclick="trjump('$cfg{'pathcgi_adm_dbman'}?cmd=opr_orders&view=$rec->{'ID_orders'}')">
						<td class='smalltext' valign='top'>$rec->{'ID_orders'}</td>
						<td class='smalltext' valign='top'>$rec->{'Status'}</td>
						<td class='smalltext' align='center'>$rec->{'Denied'}</td>
						<td class='smalltext' align='center'>$rec->{'Done'}</td>
						<td class='smalltext' align='center'>$rec->{'FP'}</td>
						<td class='smalltext' align='center'>$rec->{'PaymentDate'}</td>
						<td class='smalltext' align='center'>$rec->{'Date'}</td>
					</tr>\n|;

		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_payments_list.html')	
}


sub opr_orders_tocancel {
#-----------------------------------------
# Created on: 11/26/08  14:20:05 By M.C.C Gabriel Varela Sauceda
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified RB: 11/26/08  14:48:46 Se incluye el exclude fee para no cobrar cancellation fee
# Last Modified on: 12/30/08 12:10:51
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la inserci�n de notas.
# Last Modification by JRG : 03/09/2009 : Se agrega log
	
	my ($excludefee) = 0;
	if ($in{'action'}){
		my ($err,$sth,$rec,$cust);
		$in{'id_orders'} = int($in{'id_orders'});
		if(!$in{'id_orders'}){
			$error{'id_orders'} = &trans_txt("required");
			++$err;
		}else{
			$sth=&Do_SQL("SELECT * FROM sl_orders WHERE ID_orders=$in{'id_orders'} AND Status!='Cancelled' AND Ptype!='Credit-Card'");
			$rec = $sth->fetchrow_hashref;
			if($rec->{'ID_orders'}>0){
				$sth=&Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=$rec->{'ID_customers'}");	
				$cust = $sth->fetchrow_hashref;
				$va{'orderinfo'} = "<br><table algin='left' width='100%'><tr><td><input type='hidden' name='confirmedid' value='$in{'id_orders'}'><input type='checkbox' name='confirmed' value='on' class='checkbox'><span class='help_on'>$cust->{'FirstName'} $cust->{'LastName1'} $cust->{'LastName2'}<br>$cust->{'Phone1'}-$cust->{'Phone2'}<br> $cust->{'City'}, $cust->{'State'} $cust->{'Zip'}</span></td>
															<td align='left' valign='top'><input type='checkbox' name='excludefee' value='on' class='checkbox'><span class='help_on'>Exclude Cancellation Fee</span></td></tr>
															<tr><td colspan='2' style='color:red;font-size:-2'>Mark at least the verification checkbox.</td></tr></table><br>";
			}else{
				$error{'id_orders'} = &trans_txt("invalid");
				++$err;
			}
		}
		if(!$in{'reason'}){
			$error{'reason'} = &trans_txt("required");
			++$err;
		}
		if($err){
			$va{'message'} = &trans_txt('reqfields');
		}elsif ($in{'confirmed'} and $in{'id_orders'} eq $in{'confirmedid'}){
			$excludefee = 1 if $in{'excludefee'};
			$in{'reason'} = &trans_txt('opr_orders_cancelled').": $in{'reason'}";
			$in{'reason'} .= ". No se cobra cancellation fee." if $excludefee == 1;
			if( &cancelorder($in{'id_orders'},$excludefee)==1){

				&add_order_notes_by_type($in{'id_orders'},&filter_values($in{'reason'}),"High");

				&auth_logging('opr_orders_noteadded',$in{'id_orders'});
				$va{'message'} = &trans_txt('opr_orders_cancelled') ." : <a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$in{'id_orders'}&tabs=1&tab=4'>$in{'id_orders'}</a>";
			}else{
				$va{'message'} = "The order could not be cancelled. Verify if the order is already cancelled or if the order status is other than 'Processed'.";
				$error{'id_orders'} = &trans_txt('invalid');
				$va{'message'} = &trans_txt('opr_orders_cerror');
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_tocancel.html')	
}

sub opr_preorders_captbatch {
# --------------------------------------------------------
# Last Modified on: 01/15/09 12:37:20
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la valicaci�n del Authcode
# Last Modified on: 01/26/09 13:08:44
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta, estaba err�nea. Tambi�n se hace que orders_wreport sea para preorders
	### Sale Prices		
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rec);
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_orders.ID_orders))
FROM sl_orders
inner join sl_orders_payments on(sl_orders.ID_orders=sl_orders_payments.ID_orders)
WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Void') 
and sl_orders.Status not in('Void', 'Cancelled')
and Ptype!='Credit-Card'
and not isnull(AuthCode) 
and Authcode!='' 
and Authcode!='0000' 
AND (Captured='No')");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT SUM(Amount) 
FROM sl_orders inner join sl_orders_payments on(sl_orders.ID_orders=sl_orders_payments.ID_orders)
WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Void') 
and not isnull(AuthCode) 
and Authcode!='' 
and Authcode!='0000' 
AND (Captured='No') 
AND sl_orders.Status not in('Void', 'Cancelled')
and Ptype!='Credit-Card'");
		$va{'tot_amount'} = &format_price($sth->fetchrow);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		$va{'searchresults'} = &orders_wreport("fx","  sl_orders,sl_orders_payments WHERE  sl_orders_payments.Status NOT IN ('Cancelled','Void') AND sl_orders.ID_orders=sl_orders_payments.ID_orders and not isnull(AuthCode) and Authcode!='' and Authcode!='0000' AND (Captured='No') AND sl_orders.Status not in('Void', 'Cancelled') and Ptype!='Credit-Card' ORDER BY sl_orders.ID_orders DESC","nopre");

	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	## Update Va's & Print Page
	($va{'op1'},$va{'op2'},$va{'op3'},$va{'op4'},$va{'op5'}) = ('off','off','off','on','off');
	$va{'title'} = "Orders Ready To Capture";
	print "Content-type: text/html\n\n";
	print &build_page('opr_orders_pbatch.html');	
}


sub opr_cod_orders {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
#last modification: JRG : 02/13/2009 se agrega id_warehouses a sl_preorders

	if($in{'id_warehouses'}){	
		$va{'wh_name'} = &load_name("sl_warehouses","ID_warehouses",$in{'id_warehouses'},"Name");	
		$va{'searchresults'} = "";
		$qry = "";
		if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
			$qry .= " AND sl_orders.Date >= '".$in{'from_date'}."' ";
		}
		if($in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
			$qry .= " AND sl_orders.Date <= '".$in{'to_date'}."' ";
		}
		if($in{'from_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/ && $in{'to_date'} =~ /^(\d{4})(\/)(\d{1,2})\2(\d{1,2})$/){
			my ($sth_d) = &Do_SQL("SELECT DATEDIFF('".$in{'to_date'}."','".$in{'from_date'}."')");
			$days = $sth_d->fetchrow_array();
			if($days > 0 || $in{'from_date'} eq $in{'to_date'}){
				#ok
			} else {
				$qry = "";
			}
		}

		my ($sth) = &Do_SQL("SELECT sl_orders_products.* FROM sl_orders, sl_orders_payments, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND LEFT(sl_orders_products.ID_products,1) <> '6' AND sl_orders.ID_warehouses='".$in{'id_warehouses'}."' AND sl_orders.Status='Processed' AND sl_orders.ID_warehouses IS NOT NULL $qry GROUP BY sl_orders_products.ID_orders ");
		$va{'matches'} = $sth->rows;
		if($va{'matches'}>0){
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});			
			my ($sth) = &Do_SQL("SELECT sl_orders_products.* FROM sl_orders, sl_orders_payments, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_payments.Type='COD' AND LEFT(sl_orders_products.ID_products,1) <> '6' AND sl_orders.ID_warehouses='".$in{'id_warehouses'}."' AND sl_orders.Status='Processed' AND sl_orders.ID_warehouses IS NOT NULL $qry GROUP BY sl_orders_products.ID_orders LIMIT $first,$usr{'pref_maxh'}");
			while ($row = $sth->fetchrow_hashref){
				$d = 1 - $d;
				#$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/admin/admin?cmd=opr_cod_match&id_orders=".$row->{'ID_orders'}."&id_warehouses=".$in{'id_warehouses'}."')\">";
				$id_precustomers = &load_name('sl_orders','ID_orders',$row->{'ID_orders'},'ID_customers');
				$va{'searchresults'} .= "<td>".$row->{'ID_orders'}."</td><td>".&load_name('sl_orders','ID_orders',$row->{'ID_orders'},'Date')."</td><td>".&load_name("sl_customers","ID_customers",$id_precustomers,"FirstName")."</td><td>".&load_name("sl_customers","ID_customers",$id_precustomers,"LastName1").&load_name("sl_customers","ID_customers",$row->{'ID_customers'},"LastName2")."</td>";
				$va{'searchresults'} .= "</tr>";
			}
		} else {
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
		}
	} else {
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_cod_orders.html');	
}

sub opr_related_adjustment {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	($in{'error_orders'},$in{'revised_orders'}) = &related_adjustment("orders",0);
	($in{'error_preorders'},$in{'revised_preorders'}) = &related_adjustment("preorders",0);
	if($in{'action'}){
		if($in{'error_orders'} > 0){
			$in{'revised_orders'} = &related_adjustment("orders",1);
		}
		if($in{'error_preorders'} > 0){
			$in{'revised_preorders'} = &related_adjustment("preorders",1);
		}		
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_related_adjustment.html');
}


sub opr_returns_home{
#-----------------------------------------
# Created on: 03/02/09  16:56:36 By  Roberto Barcenas
# Forms Involved: opr_returns_home
# Description : Shows the returns dashboard
# Parameters :  
	
	#####Dates
	my ($sth) = &Do_SQL("SELECT CURDATE() AS d1,
											DATE_SUB(CURDATE(),INTERVAL 7 DAY) AS d7,
											DATE_SUB(CURDATE(),INTERVAL 8 DAY) AS d8,
											DATE_SUB(CURDATE(),INTERVAL 14 DAY) AS d14,
											DATE_SUB(CURDATE(),INTERVAL 15 DAY) AS d15,
											DATE_SUB(CURDATE(),INTERVAL 22 DAY) AS d22,
											DATE_SUB(CURDATE(),INTERVAL 23 DAY) AS d23,
											DATE_SUB(CURDATE(),INTERVAL 30 DAY) AS d30,
											DATE_SUB(CURDATE(),INTERVAL 31 DAY) AS d31;");
											
	($va{'d1'},$va{'d7'},$va{'d8'},$va{'d14'},$va{'d15'},$va{'d22'},$va{'d23'},$va{'d30'},$va{'d31'})	=	$sth->fetchrow();
											
	
	######### Sorting
	my ($sth) = &Do_SQL("SELECT SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS s7,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS s14,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS s22,
											  SUM(IF(Status = 'In process' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS s30,
											  SUM(IF(Status = 'In process' AND Date < '$va{'d30'}',1,0)) AS s31,
											  
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS r7,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS r14,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS r22,
											  SUM(IF(Status = 'Repair' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS r30,
											  SUM(IF(Status = 'Repair' AND Date < '$va{'d30'}',1,0)) AS r31,
											  
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS q7,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS q14,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS q22,
											  SUM(IF(Status = 'QC/IT' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS q30,
											  SUM(IF(Status = 'QC/IT' AND Date < '$va{'d30'}',1,0)) AS q31,
											  
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS a7,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS a14,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS a22,
											  SUM(IF(Status = 'ATC' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS a30,
											  SUM(IF(Status = 'ATC' AND Date < '$va{'d30'}',1,0)) AS a31,
											  
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS p7,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS p14,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS p22,
											  SUM(IF(Status = 'Processed' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS p30,
											  SUM(IF(Status = 'Processed' AND Date < '$va{'d30'}',1,0)) AS p31,
											  
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d7'}' AND '$va{'d1'}',1,0)) AS b7,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d14'}' AND '$va{'d8'}',1,0)) AS b14,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d22'}' AND '$va{'d15'}',1,0)) AS b22,
											  SUM(IF(Status = 'Back to inventory' AND Date BETWEEN '$va{'d30'}' AND '$va{'d23'}',1,0)) AS b30,
											  SUM(IF(Status = 'Back to inventory' AND Date <  '$va{'d30'}',1,0)) AS b31
											  
											  FROM sl_returns WHERE Status IN('In process','Repair','QC/IT','ATC','Processed','Back to inventory')");
	
	($va{'sor_7'},$va{'sor_14'},$va{'sor_22'},$va{'sor_30'},$va{'sor_31'},$va{'rep_7'},$va{'rep_14'},$va{'rep_22'},$va{'rep_30'},$va{'rep_31'},$va{'qc_7'},$va{'qc_14'},$va{'qc_22'},$va{'qc_30'},$va{'qc_31'},$va{'mx_7'},$va{'mx_14'},$va{'mx_22'},$va{'mx_30'},$va{'mx_31'},$va{'mia_7'},$va{'mia_14'},$va{'mia_22'},$va{'mia_30'},$va{'mia_31'},$va{'bti_7'},$va{'bti_14'},$va{'bti_22'},$va{'bti_30'},$va{'bti_31'})	=	$sth->fetchrow();
	
	### Status
	$va{'tot_sorting'}	=	$va{'sor_7'}+$va{'sor_14'}+$va{'sor_22'}+$va{'sor_30'}+$va{'sor_31'};
	$va{'tot_repair'}	=	$va{'rep_7'}+$va{'rep_14'}+$va{'rep_22'}+$va{'rep_30'}+$va{'rep_31'};
	$va{'tot_qcit'}	=	$va{'qc_7'}+$va{'qc_14'}+$va{'qc_22'}+$va{'qc_30'}+$va{'qc_31'};
	$va{'tot_atc'}	=	$va{'mx_7'}+$va{'mx_14'}+$va{'mx_22'}+$va{'mx_30'}+$va{'mx_31'};
	$va{'tot_processed'}	=	$va{'mia_7'}+$va{'mia_14'}+$va{'mia_22'}+$va{'mia_30'}+$va{'mia_31'};
	$va{'tot_bti'}	=	$va{'bti_7'}+$va{'bti_14'}+$va{'bti_22'}+$va{'bti_30'}+$va{'bti_31'};
	
	#### Range
	$va{'tot_31'}	=	$va{'sor_31'} + $va{'rep_31'} + $va{'qc_31'} + $va{'mx_31'} + $va{'mia_31'} + $va{'bti_31'};
	$va{'tot_30'}	=	$va{'sor_30'} + $va{'rep_30'} + $va{'qc_30'} + $va{'mx_30'} + $va{'mia_30'} + $va{'bti_30'};
	$va{'tot_22'}	=	$va{'sor_22'} + $va{'rep_22'} + $va{'qc_22'} + $va{'mx_22'} + $va{'mia_22'} + $va{'bti_22'};
	$va{'tot_14'}	=	$va{'sor_14'} + $va{'rep_14'} + $va{'qc_14'} + $va{'mx_14'} + $va{'mia_14'} + $va{'bti_14'};
	$va{'tot_7'}	=	$va{'sor_7'} + $va{'rep_7'} + $va{'qc_7'} + $va{'mx_7'} + $va{'mia_7'} + $va{'bti_7'};
	$va{'tot_returns'}	= $va{'tot_31'} +	$va{'tot_30'} + $va{'tot_22'} + $va{'tot_14'} + $va{'tot_7'};
	
	
	print "Content-type: text/html\n\n";
	print &build_page('opr_returns_home.html');
}


sub opr_retpackinglistbyprod{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/08/09 12:35:36
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	if($in{'showpackinglist'} or $in{'search'}eq"Print")
	{
		my @id_orders=split(/,/,$in{'id_orders'});
		my @id_orders_products=split(/,/,$in{'id_orders_products'});
		my @id_returns=split(/,/,$in{'id_returns'});
		my %dones;
		for(0..$#id_orders){
			#Muestra el packing list
			if(!$dones{"$id_orders[$_]$id_orders_products[$_]"}){
				#$in{'view'}=$in{'toprint'} if(!$in{'view'});
				$in{'view'}=$id_orders[$_];
				$in{'id_orders_products'}=$id_orders_products[$_];
				$in{'id_returns'}=$id_returns[$_];
				
				#Cargar ines
				my $i=0,@fieldss;
				$sth=&Do_SQL("describe sl_orders");
				while($rec=$sth->fetchrow_hashref)
				{
					$fieldss[$i]=lc($rec->{'Field'});
					$i++;
				}
				$fieldss[$i]="Firstname";
				$i++;
				$fieldss[$i]="LastName1";
				
				$sth=&Do_SQL("SELECT sl_orders.*,sl_customers.Firstname,sl_customers.LastName1 FROM `sl_orders` inner join sl_customers on (sl_orders.ID_customers=sl_customers.ID_customers) WHERE `ID_orders`=$in{'view'}");
				@rec=$sth->fetchrow_array;
				for(0..$#rec)
				{
					$in{$fieldss[$_]}=$rec[$_];
				}
				$va{'packinglist_view'}.=&build_page('forms:packinglist_view.html')."<DIV STYLE='page-break-before:always'></DIV>";
				#$dones{"$id_orders[$_]$id_orders_products[$_]"}=1;
			}
		}
		

		
		if ($in{'search'}eq"Print"){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('opr_retpackinglistbyproduct_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('opr_retpackinglistpbyproduct.html');
		}
	}else{
		
		my $sth,$rec;
		my (@c) = split(/,/,$cfg{'srcolors'});
		$sth=&Do_SQL("SELECT count( qty ) FROM (
	SELECT count( DISTINCT (
	ID_returns
	) ) AS Qty
	FROM sl_returns
	INNER JOIN sl_orders ON ( sl_returns.ID_orders = sl_orders.ID_orders ) 
	INNER JOIN (
	
	SELECT * 
	FROM sl_orders_products
	WHERE (
	ShpDate = ''
	OR isnull( Shpdate ) 
	OR ShpDate = '0000-00-00'
	)
	AND (
	Tracking = ''
	OR isnull( Tracking ) 
	)
	AND SalePrice >=0
	AND Quantity >=0
	AND Shipping >=0
	AND Status!='Inactive') AS tempo ON ( tempo.ID_orders = sl_orders.ID_orders
	AND tempo.ID_products = ID_products_exchange ) 
	INNER JOIN sl_products ON ( right( ID_products_exchange, 6 ) = sl_products.ID_products ) 
	WHERE PackingListStatus != 'Done' AND ((sl_returns.Status = 'Resolved' AND Amount=0) OR (sl_returns.Status = 'Archived' AND Amount !=0))
	GROUP BY ID_products_exchange
	) AS tabtemp");
		$va{'matches'} = $sth->fetchrow;
	
		if ($va{'matches'}>0)
		{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$sth=&Do_SQL("SELECT count(distinct(ID_returns)) as Qty, group_concat(ID_returns separator ',')as ID_returns, group_concat(sl_returns.ID_orders separator ',')as ID_orders, group_concat(sl_returns.ID_orders_products separator ',') as ID_orders_products, group_concat(Amount separator ',') as Amount, group_concat(merAction separator ',') as merAction, group_concat(sl_returns.Status separator ',') AS StatusRet, group_concat(StatusPrd separator ',')as StatusPrd, group_concat(StatusPay separator ',')as StatusPay, group_concat(sl_orders.Status separator ',') AS StatusOrd, ID_products_exchange,group_concat(tempo.ID_orders_products separator ',')as ID_orders_products,sl_products.ID_products,Name,Model
	FROM sl_returns
	INNER JOIN sl_orders ON ( sl_returns.ID_orders = sl_orders.ID_orders ) 
	inner join(select * from sl_orders_products where (ShpDate=''or isnull(Shpdate) or ShpDate='0000-00-00') and (Tracking=''or isnull(Tracking)) and SalePrice>=0 and Quantity>=0 and Shipping>=0 and Status!='Inactive')as tempo on(tempo.ID_orders=sl_orders.ID_orders and tempo.ID_products=ID_products_exchange)
	inner join sl_products on (right(ID_products_exchange,6)=sl_products.ID_products)
	WHERE PackingListStatus != 'Done' AND ((sl_returns.Status = 'Resolved' AND Amount=0) OR (sl_returns.Status = 'Archived' AND Amount !=0))
	group by ID_products_exchange
	order by Qty desc LIMIT $first,$usr{'pref_maxh'};");

			while($rec=$sth->fetchrow_hashref)
			{
				$d = 1 - $d;
				
	#			$id_products=&load_name('sl_orders_products','ID_orders_products',$rec->{'ID_orders_products'},'ID_products');
				my ($sthk) = &Do_SQL("select if(SUM(Quantity) > 0,SUM(Quantity),0) AS Inventory FROM sl_warehouses_location WHERE ID_products = '$rec->{'ID_products_exchange'}' AND Quantity > 0 ;");
				my ($inventory)	=	$sthk->fetchrow;
	#			$choices = &load_choices('-',$reck->{'choice1'},$reck->{'choice2'},$reck->{'choice3'},$reck->{'choice4'});
				
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Qty'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>".&format_sltvid($rec->{'ID_products_exchange'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}<br>$rec->{'Model'}</td>\n";
				$va{'searchresults'} .= qq|   <td class="smalltext" align="right">$inventory
																			<a href="#ajax_inv_$rec->{'ID_products_exchange'}" onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'ajax_inv_$rec->{'ID_products_exchange'}');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=$rec->{'ID_products_exchange'}&cols=ID,Choices,Vendor SKU,Warehouse,Qty');">
			  															<img id="img_ajax_inv_$rec->{'ID_products_exchange'}" src="[va_imgurl]/[ur_pref_style]/b_view.png" title="More Info" alt="More Info" border="0"></a>					
																			&nbsp;&nbsp;&nbsp;<span id="ajax_inv_$rec->{'ID_products_exchange'}">&nbsp;</span>
																		</td>\n|;
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		#$va{'searchresults'} .=	"</table>";
		print "Content-type: text/html\n\n";
		print &build_page('opr_retpackinglistbyproduct.html');
	}
}


sub opr_cod_repsltvid{
#-----------------------------------------
# Created on: 03/18/09  16:20:05 By  Roberto Barcenas
# Forms Involved: opr_preorders_rep_cod_qty
# Description : Returns excel file with specific item data summary for COD Orders
# Parameters : 	
	
	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=cod_$in{'export'}.csv\n\n";
	my (@cols) = ("ID_Orders","Date","ID_customers","First Name","Last Name",
					"Address1","Address2","City","State","Zip","Phone1","Phone2","Phone3","B-Day","Sex","Email","Qty");
	
	print '"'.join('","',@cols) . "\"\r\n";
	
	
	my ($sth) = &Do_SQL("SELECT sl_orders.* ,COUNT(ID_products) AS Qty FROM sl_orders_products INNER JOIN sl_orders 
											ON sl_orders.ID_orders = sl_orders_products.ID_orders AND ID_products = '$in{'export'}'  
											AND sl_orders_products.Status = 'Active' AND (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00')
											INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type= 'COD' AND Status<>'Cancelled') 
											AS paym ON paym.ID_orders = sl_orders.ID_orders
											where Ptype!='Credit-Card'
											GROUP BY sl_orders.ID_orders ORDER BY Qty DESC");
											
	while ($rec = $sth->fetchrow_hashref() ) {
			$ary[0] = $rec->{'ID_orders'};
			$ary[1] = $rec->{'Date'};

			
			my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
			$rec_cust = $sth2->fetchrow_hashref();
			$ary[2] = $rec->{'ID_customers'};
			$ary[3] = $rec_cust->{'FirstName'};
			$ary[4] = $rec_cust->{'LastName1'};
			$ary[5] = $rec->{'Address1'};
			$ary[6] = $rec->{'Address2'};
			$ary[7] = $rec->{'City'};
			$ary[8] = $rec->{'State'};
			$ary[9] = $rec->{'Zip'};
			$ary[10] = $rec_cust->{'Phone1'};
			$ary[11] = $rec_cust->{'Phone2'};
			$ary[12] = $rec_cust->{'Cellphone'};
			$ary[13] = "$rec_cust->{'bday_month'}-$rec_cust->{'bday_day'}";
			$ary[14] = $rec_cust->{'Sex'};
			$ary[15] = $rec_cust->{'Email'};
	
			$ary[16] = $rec->{'Qty'};
			print '"'.join('","',@ary) . "\"\r\n";
	}
}


sub opr_repmemos{
#-----------------------------------------
                
  my ($sth) = &Do_SQL("SELECT sl_orders.*,ID_products FROM sl_orders INNER JOIN sl_repmemos ON sl_orders.ID_orders = sl_repmemos.ID_orders WHERE ID_repmemos='$in{'toprint'}';");
  my $rec = $sth->fetchrow_hashref;
  
  $in{'id_orders'}  = $rec->{'ID_orders'};
  $in{'id_customers'}  = $rec->{'ID_customers'};
  $in{'address1'}  = $rec->{'Address1'};
  $in{'address2'}  = $rec->{'Address2'};
  $in{'address3'}  = $rec->{'Address3'};
  $in{'urbanization'}  = $rec->{'Urbanization'};
  $in{'city'}  = $rec->{'City'};
  $in{'state'}  = $rec->{'State'};
  $in{'zip'}  = $rec->{'Zip'};
  $in{'phone1'}  = $rec->{'Phone1'};
  $in{'shp_address1'}  = $rec->{'shp_Address1'};
  $in{'shp_address2'}  = $rec->{'shp_Address2'};
  $in{'shp_address3'}  = $rec->{'shp_Address3'};
  $in{'urbanization'}  = $rec->{'Urbanization'};
  $in{'shp_city'}  = $rec->{'shp_City'};
  $in{'shp_state'}  = $rec->{'shp_State'};
  $in{'shp_zip'}  = $rec->{'shp_Zip'};
  $in{'shptype'}  = $rec->{'shp_type'};
  $in{'shpdate'}  = $rec->{'PostedDate'};
  $in{'date'}  = $rec->{'Date'};
  $in{'id_products'}  = $rec->{'ID_products'};
  
  $va{'invoice_message'}  = trans_txt('repmemo_invoice');

print "Content-type: text/html\n\n";
print &build_page('opr_repmemos_pinvoice.html');

}



sub opr_export_trackings{
# --------------------------------------------------------
# Last Modified on: 02/10/2012 20:00:02
# Last Modified by RB on 2012/05/30: Se agrega posibilidad de buscar tracking ingresando numero de orden 


	if($in{'action'}){

		if(!$in{'id_orders_bulk'}){
			$va{'message'} = &trans_txt('required');
			$err++;
		}

		if(!$err){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin$/dbman/;

			##ToDo: Los tracking del file estan cortados, en la DB tienen algunos numeros mas a la izquierda
			##ToDo: Buscar los tracking uno a uno, con el RIGHT(Tracking,22) parece que no funciona, o hacer un  OR Tracking LIKE '%tracking' para cada uno
			
			#en Dbl = 420029059403410200829238345209
			#en Excel =       9403410200829238345209

			my ($fname) = 'orders_tracking-'.$in{'from_date'}.'-'.$in{'to_date'};
			

			# Send the content type
			if ($excel){
				$fname   = $fname.'.xls';
				use Spreadsheet::WriteExcel;
				print "Content-type: application/octetstream\n";
				print "Content-disposition: attachment; filename=$fname\n\n";
				# Redirect the output to STDOUT
				$workbook  = Spreadsheet::WriteExcel->new("-");
				$worksheet = $workbook->add_worksheet();
				# Write some text.

				$worksheet->write(0, 1,'Tracking');
				$worksheet->write(0, 2,'Tracking Direksys');
				$worksheet->write(0, 3,'Ship Date');
				$worksheet->write(0, 4,'Order ID');
			}else{
				$fname   = $fname.'.csv';
				print "Content-type: application/vnd.ms-excel\n";
				print "Content-disposition: attachment; filename=$fname\n\n";	
				print "Tracking,Tracking Direksys,Ship Date,Order ID\n";
				
			}
			@list = split (/\n/,$in{'id_orders_bulk'});
			for (0..$#list){
				my $mod;
				$tnum = $list[$_];
				
				if(length($tnum) < 8){
					$mod = " ID_orders = '".&filter_values($tnum)."' ";
				}else{
					$mod = " sl_orders_parts.Tracking like '%".&filter_values($tnum)."%' ";
				}
				
				$query_list = "SELECT sl_orders_parts.Tracking, IF(ID_orders IS NULL,'N/A',ID_orders)AS OrderID,sl_orders_parts.Date 
					FROM sl_orders_parts LEFT JOIN sl_orders_products
					USING(ID_orders_products)
					WHERE $mod
					GROUP BY sl_orders_parts.Tracking";
				$sth = &Do_SQL($query_list);
				my($Tracking,$OrderID,$shipdate) = $sth->fetchrow();
				if ($excel){
					$worksheet->write($row,1,"'".$tnum);
					$worksheet->write($row,2,"'".$Tracking);
					$worksheet->write($row,3,"'".$shipdate);
					$worksheet->write_number($row,4,$OrderID);
					$row++;
				}else{
					print "'$tnum,'$Tracking,$shipdate,$OrderID\n";
				}
			}
			return;
		}

	}

	print "Content-type: text/html\n\n";
	print &build_page('opr_dwntracking.html');		

}

sub opr_customers_home {
# --------------------------------------------------------
	my ($query);
	if ($in{'pterms'} eq 'all' or !$in{'pterms'}){
		$query = '';
	}else{
		$query = "sl_customers.Pterms='".&filter_values($in{'pterms'})."' AND";
	}
	my ($sth) = &Do_SQL("SELECT *							
							FROM (
							SELECT 
							ID_customers, 
							sl_orders.Date AS OrderDate,
							sl_orders.ID_orders, 
							Captured, 
							Amount,
							SUM(IF(Captured='Yes',Amount,0)) AS AmtPaid
							
							FROM sl_orders 
							LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							WHERE sl_orders.Status='Shipped'  
							GROUP BY  sl_orders.ID_orders) AS tmp
							
							LEFT JOIN sl_customers ON tmp.ID_customers=sl_customers.ID_customers
							WHERE $query Status='Active'
							GROUP BY sl_customers.ID_customers;");
	$va{'matches'} = $sth->rows()-1;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_customers LEFT JOIN sl_orders ON sl_customers.ID_customers=sl_orders.ID_customers WHERE $query sl_customers.Status='Active';");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT 
							sl_customers.ID_customers,
							FirstName, LastName1, company_name, COUNT(*) AS QtyOrd,
							MAX(DATEDIFF(CURDATE(),PostedDate)) AS MaxDays,
							MIN(DATEDIFF(CURDATE(),PostedDate)) AS MinDays,
							SUM(AmtPaid) AS Paid,
							SUM(Amount) AS Total,
							Pterms
							
							FROM (
							SELECT 
							ID_customers, 
							sl_orders.PostedDate,
							sl_orders.ID_orders, 
							Captured, 
							Amount,
							SUM(IF(Captured='Yes',Amount,0)) AS AmtPaid
							
							FROM sl_orders 
							LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							WHERE sl_orders.Status='Shipped'  
							GROUP BY  sl_orders.ID_orders) AS tmp
							
							LEFT JOIN sl_customers ON tmp.ID_customers=sl_customers.ID_customers
							WHERE $query Status='Active'
							GROUP BY sl_customers.ID_customers
					ORDER BY MaxDays DESC
					LIMIT $first,$usr{'pref_maxh'};");
		}
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}&&tab=13\">$rec->{'ID_customers'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'FirstName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LastName1'} $rec->{'LastName2'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'company_name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Pterms'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'QtyOrd'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'MaxDays'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'MinDays'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'}-$rec->{'Paid'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td align="center" colspan="7" class='stdtxterr'><p>&nbsp;</p>| . &trans_txt('search_nomatches') . qq|<p>&nbsp;</p></td>
		</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_customers_home.html');		
}


sub opr_ar_addpayment {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html.cgi
# Parameters : It takes any parameter from status table sl_orders

	$in{'id_customers'}=int($in{'id_customers'});
	$va{'info_style'} =  "visibility: hidden";
	if ($in{'action'} and $in{'id_customers'}>0){
		$sth = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=$in{'id_customers'}");
		$rec = $sth->fetchrow_hashref;
		if ($rec->{'ID_customers'}>0){
			$va{'custname'} = "$rec->{'FirstName'} $rec->{'LastName'} / $rec->{'company_name'}";
			$va{'info_style'} = '';
			$va{'payment_frame'} = qq|
			&nbsp;
					<IFRAME SRC="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=customer_addpmt&id_customers=$in{'id_customers'}&$va{'rndnumber'}" name="rcmd" TITLE="Recieve Commands" width="100%" height="450" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
						<H2>Unable to do the script</H2>
						<H3>Please update your Browser</H3>
					</IFRAME>\n|;
		}else{
			$error{'id_customers'} = &trans_txt('invalid');
			$va{'message'} = &trans_txt('reqfields_short');
			delete($in{'id_customers'});
		}
	}else{
		delete($in{'id_customers'});
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_ar_addpayment.html');
}

sub opr_ar_statements {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html.cgi
# Parameters : It takes any parameter from status table sl_orders
	my ($line,$showlist);
	$in{'id_customers'}=int($in{'id_customers'});
	$va{'info_style'} =  "visibility: hidden";
	if ($in{'action'} and $in{'id_customers'}>0){
		$sth = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers=$in{'id_customers'}");
		$rec = $sth->fetchrow_hashref;
		if ($rec->{'ID_customers'}>0){
			$va{'custname'} = "$rec->{'FirstName'} $rec->{'LastName'} / $rec->{'company_name'}";
			$va{'info_style'} = '';

			my ($sth) = &Do_SQL("SELECT * FROM sl_orders 
								LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
								WHERE sl_orders.Status='Shipped' AND  
								ID_customers=$in{'id_customers'}
								GROUP BY sl_orders.ID_orders");
			$va{'matches'} = $sth->rows()-1;
			my (@c) = split(/,/,$cfg{'srcolors'});

			####
			#### CAULQUEIR CAMBIO EN ESTE CODIGO DEBE SER TAMBIEN HECHO EN
			#### COMMON/TABS/CUSTOMERS.CGI &load_tabs13
			####

			if ($va{'matches'}>0){
				(!$in{'nh'}) and ($in{'nh'}=1);
				my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
		
				$sth = &Do_SQL("SELECT 
						sl_orders.ID_orders, 
						sl_orders.Date AS OrderDate,
						sl_orders.PostedDate,
						Paymentdate,
						DATEDIFF(CURDATE(),sl_orders.PostedDate) AS df1,
						DATEDIFF(CURDATE(),Paymentdate) AS df2,
						SUM(Amount) AS Total,
						SUM(IF(Captured='Yes',Amount,0)) AS Paid
						
						FROM sl_orders 
						LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
						WHERE sl_orders.Status='Shipped' AND  
						ID_customers=$in{'id_customers'}
					GROUP BY sl_orders.ID_orders
					HAVING (Total>Paid)
					ORDER BY df1 DESC;");
					my (@steps) = ("90","60","30","1");
					while($rec=$sth->fetchrow_hashref()) {
						$showlist=1;
						($line<$first) and ($showlist=0);
						($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
						++$line;
						for my $i(0..$#steps){
							if ($rec->{'df2'}>$steps[$i] and $rec->{'df2'}>0){
								$va{'due'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
							}elsif(-$rec->{'df2'}>$steps[$i] and $rec->{'df2'}<0){
								$va{'ndue'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
							}elsif($rec->{'df2'} eq 0){
								$va{'due0'} += $rec->{'Total'}-$rec->{'Paid'};
							}
						}
						if ($showlist){
							$d = 1 - $d;
							$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
							$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
							$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'OrderDate'}</td>\n";
							$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PostedDate'}</td>\n";
							$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Paymentdate'}</td>\n";
							if ($rec->{'df2'}<0){
								$va{'searchresults'} .= "   <td class='smalltext' align='right'>".(-$rec->{'df2'})."</td>\n";
							}else{
								$va{'searchresults'} .= "   <td class='smalltext' align='right' style='Color:Red'>$rec->{'df2'}</td>\n";
							}
							$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'}-$rec->{'Paid'})."</td>\n";
							$va{'searchresults'} .= "   <td class='smalltext'>". &invoices_list($rec->{'ID_orders'})."</td>\n";
							$va{'searchresults'} .= "</tr>\n";
						}
						$va{'total_balance'} += $rec->{'Total'}-$rec->{'Paid'}
					}  # End while
					$va{'total_balance'} = &format_price($va{'total_balance'});
					for (0..$#steps){
						$va{'due'.$steps[$_]} = &format_price($va{'due'.$steps[$_]});
						$va{'ndue'.$steps[$_]} = &format_price($va{'ndue'.$steps[$_]});
					}
					$va{'due0'} = &format_price($va{'due0'});
				}else{
					$va{'pageslist'} = 1;
					$va{'searchresults'} = qq|
						<tr>
							<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
						</tr>\n|;
				}  # End if str_sql

		}else{
			$error{'id_customers'} = &trans_txt('invalid');
			$va{'message'} = &trans_txt('reqfields_short');
			delete($in{'id_customers'});
		}
	}else{
		delete($in{'id_customers'});
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_ar_statements.html');
}

sub opr_ar_agging {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : This function goes only here in admin.html.cgi
# Parameters : It takes any parameter from status table sl_orders
	my ($line,$showlist);
	if ($in{'bycustomer'}){
		$va{'tab_customers'} = 'selected';
		$va{'orders_style'} = "display:none";
		my ($sth) = &Do_SQL("SELECT *							
								FROM (
								SELECT 
								ID_customers, 
								sl_orders.Date AS OrderDate,
								sl_orders.ID_orders, 
								Captured, 
								SUM(Amount) AS Total,
								SUM(IF(Captured='Yes',Amount,0)) AS AmtPaid
								FROM sl_orders 
								LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
								WHERE sl_orders.Status='Shipped'  
								GROUP BY  sl_orders.ID_orders
								HAVING (Total>AmtPaid)) AS tmp
								LEFT JOIN sl_customers ON tmp.ID_customers=sl_customers.ID_customers
								WHERE Status <>'Inactive' 
								GROUP BY sl_customers.ID_customers;");
		$va{'matches'} = $sth->rows()-1;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT 
							sl_customers.ID_customers,
							FirstName, LastName1, company_name, COUNT(*) AS QtyOrd,
							MAX(DATEDIFF(CURDATE(),PostedDate)) AS MaxDays,
							MIN(DATEDIFF(CURDATE(),PostedDate)) AS MinDays,
							SUM(AmtPaid) AS Paid,
							SUM(TAmount) AS Total,
							Pterms
							
							FROM (
							SELECT 
							ID_customers, 
							sl_orders.PostedDate,
							sl_orders.ID_orders, 
							Captured, 
							SUM(Amount) AS TAmount,
							SUM(IF(Captured='Yes',Amount,0)) AS AmtPaid
							FROM sl_orders
							LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							WHERE sl_orders.Status='Shipped' AND sl_orders_payments.Status='Approved'
							GROUP BY  sl_orders.ID_orders
							HAVING (TAmount>AmtPaid)) AS tmp
							
							LEFT JOIN sl_customers ON tmp.ID_customers=sl_customers.ID_customers
							WHERE Status <>'Inactive'
							GROUP BY sl_customers.ID_customers
					ORDER BY MaxDays DESC;");
			while ($rec = $sth->fetchrow_hashref){
				$showlist=1;
				($line<$first) and ($showlist=0);
				($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
				++$line;
				if ($showlist){
					$d = 1 - $d;
					$va{'customers_searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}&&tab=13\">$rec->{'ID_customers'}</a></td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext'>$rec->{'FirstName'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext'>$rec->{'LastName1'} $rec->{'LastName2'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext'>$rec->{'company_name'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext'>$rec->{'Pterms'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'QtyOrd'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'MaxDays'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'MinDays'}</td>\n";
					$va{'customers_searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'}-$rec->{'Paid'})."</td>\n";
					$va{'customers_searchresults'} .= "</tr>\n";
				}
				$va{'total_balance'} += $rec->{'Total'}-$rec->{'Paid'}
			}
			$va{'total_balance'} = &format_price($va{'total_balance'});
			$sth = &Do_SQL("SELECT 
				sl_orders.ID_orders, 
				sl_orders.Date AS OrderDate,
				sl_orders.PostedDate,
				Paymentdate,
				DATEDIFF(CURDATE(),sl_orders.PostedDate) AS df1,
				DATEDIFF(CURDATE(),Paymentdate) AS df2,
				SUM(Amount) AS Total,
				SUM(IF(Captured='Yes',Amount,0)) AS Paid
				
				FROM sl_orders 
				LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
				WHERE sl_orders.Status='Shipped' AND sl_orders_payments.Status='Approved'
			GROUP BY sl_orders.ID_orders
			HAVING (Total>Paid)
			ORDER BY df1 DESC;");
			my (@steps) = ("90","60","30","1");
			while($rec=$sth->fetchrow_hashref()) {
				for my $i(0..$#steps){
					if ($rec->{'df2'}>=$steps[$i] and $rec->{'df2'}>0){
						$va{'due'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
					}elsif(-$rec->{'df2'}>=$steps[$i] and $rec->{'df2'}<0){
						$va{'ndue'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
					}elsif($rec->{'df2'} eq 0){
						$va{'due0'} += $rec->{'Total'}-$rec->{'Paid'};
					}
				}
			}  # End while
			for (0..$#steps){
				$va{'due'.$steps[$_]} = &format_price($va{'due'.$steps[$_]});
				$va{'ndue'.$steps[$_]} = &format_price($va{'ndue'.$steps[$_]});
			}
			$va{'due0'} = &format_price($va{'due0'});
		}else{
			$va{'pageslist'} = 1;
			$va{'customers_searchresults'} = qq|
				<tr>
					<td colspan='9' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
			$va{'total_balance'} = &format_price($va{'total_balance'});
		}
	}else{
		################################################################
		#######  AR : ORDERS
		################################################################
		$va{'tab_orders'} = 'selected';
		$va{'customers_style'} = "display:none";
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders 
							LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
							WHERE sl_orders.Status='Shipped' AND sl_orders_payments.Status='Approved'
							GROUP BY sl_orders.ID_orders");
		$va{'matches'} = $sth->rows()-1;
		my (@c) = split(/,/,$cfg{'srcolors'});
	
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/admin/admin",$va{'matches'},$usr{'pref_maxh'});
	
			$sth = &Do_SQL("SELECT 
				sl_orders.ID_orders, 
				sl_orders.Date AS OrderDate,
				sl_orders.PostedDate,
				Paymentdate,
				DATEDIFF(CURDATE(),sl_orders.PostedDate) AS df1,
				DATEDIFF(CURDATE(),Paymentdate) AS df2,
				SUM(Amount) AS Total,
				SUM(IF(Captured='Yes',Amount,0)) AS Paid
				
				FROM sl_orders 
				LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
				WHERE sl_orders.Status='Shipped' AND sl_orders_payments.Status='Approved'
			GROUP BY sl_orders.ID_orders
			HAVING (Total>Paid)
			ORDER BY df1 DESC;");
			my (@steps) = ("90","60","30","1");
			
			while($rec=$sth->fetchrow_hashref()) {
				$showlist=1;
				($line<$first) and ($showlist=0);
				($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
				++$line;
				for my $i(0..$#steps){
					if ($rec->{'df2'}>=$steps[$i] and $rec->{'df2'}>0){
						$va{'due'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
					}elsif(-$rec->{'df2'}>=$steps[$i] and $rec->{'df2'}<0){
						$va{'ndue'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
					}elsif($rec->{'df2'} eq 0){
						$va{'due0'} += $rec->{'Total'}-$rec->{'Paid'};
					}
				}
				
				if ($showlist){
					$d = 1 - $d;
					$va{'orders_searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'orders_searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
					$va{'orders_searchresults'} .= "   <td class='smalltext'>$rec->{'OrderDate'}</td>\n";
					$va{'orders_searchresults'} .= "   <td class='smalltext'>$rec->{'PostedDate'}</td>\n";
					$va{'orders_searchresults'} .= "   <td class='smalltext'>$rec->{'Paymentdate'}</td>\n";
					if ($rec->{'df2'}<0){
						$va{'orders_searchresults'} .= "   <td class='smalltext' align='right'>".(-$rec->{'df2'})."</td>\n";
					}else{
						$va{'orders_searchresults'} .= "   <td class='smalltext' align='right' style='Color:Red'>$rec->{'df2'}</td>\n";
					}
					$va{'orders_searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'}-$rec->{'Paid'})."</td>\n";
					$va{'orders_searchresults'} .= "   <td class='smalltext'>". &invoices_list($rec->{'ID_orders'})."</td>\n";
					$va{'orders_searchresults'} .= "</tr>\n";
				}
				$va{'total_balance'} += $rec->{'Total'}-$rec->{'Paid'}
			}  # End while
			$va{'total_balance'} = &format_price($va{'total_balance'});
			for (0..$#steps){
				$va{'due'.$steps[$_]} = &format_price($va{'due'.$steps[$_]});
				$va{'ndue'.$steps[$_]} = &format_price($va{'ndue'.$steps[$_]});
			}
			$va{'due0'} = &format_price($va{'due0'});
		}else{
			$va{'pageslist'} = 1;
			$va{'total_balance'} = &format_price($va{'total_balance'});
			$va{'orders_searchresults'} = qq|
				<tr>
					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}  # End if str_sql
	}
		
	print "Content-type: text/html\n\n";
	print &build_page('opr_ar_agging.html');
}
1;


#################################################################
# OPERATIONS : SETUP SHIPPING #
#################################################################

sub opr_addnote {
#-----------------------------------------
# Forms Involved: 
# Created on:
# Author: @ivanmiranda
# Description : Agrea notas masivas en ordenes de compra
# Parameters :
#

	if($in{'action'}){

		if ($in{'id_orders_bulk'} and ($in{'notes'} ne '') ){

			$in{'db'} = 'sl_orders';
			my (@ary) = split(/\s+|,|\n|\t/,$in{'id_orders_bulk'});
			my ($query,$rpd,$orddate);
			
			for my $i(0..$#ary){
				

				$orddate = '';
				$rpd = '';

				$va{'changeresult'} .= "$ary[$i] : ";
			

				if($in{'notes'}){
					(!$in{'notestype'}) and ($in{'notestype'} = 'Low');

					&add_order_notes_by_type( int($ary[$i]),&filter_values($in{'notes'}),$in{'typen'});
					&auth_logging('opr_orders_noteadded',int($ary[$i]));
					$va{'changeresult'} .= " NoteOK ";
				}

				$va{'changeresult'} .= "<br>";

			}
			
			delete($in{'notestype'});
			delete($in{'notes'});
			delete($in{'id_orders_bulk'});

		}else{
			$va{'message'} = &trans_txt('reqfields');
			#$error{'status'} = &trans_txt('invalid') if (!$in{'new_status'});
			#$error{'shipdate'} = &trans_txt('invalid') if (!$in{'shipdate'});

			$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none')."</p>";
		}
	}else{
		$va{'changeresult'} = "<p align='center' class='help_on'>".&trans_txt('tochg_none')."</p>";
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_addnote.html');		
}


1;