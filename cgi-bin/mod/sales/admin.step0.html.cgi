#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 0 : CUSTOMER SEARCH
##################################################################
# Created on: 08/12/08 @ 11:12:30
# Author: Carlos Haas
# Last Modified on: 08/12/08 @ 11:12:30
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   
# Last Modified on: 09/18/08 12:16:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia inner por left con sl_orders
# Last Modified on: 04/21/09 13:31:16
# Last Modified by: MCC C. Gabriel Varela S: Se habilita búsqueda por CID.
# Last Modified on: 05/26/09 17:20:22
# Last Modified by: MCC C. Gabriel Varela S: Se optimiza búsqueda por CID.
# if ($cses{'cid'}) {

	$va{'speechname'}= 'ccinbound:0- Customer Search';
	
	#JRG start#
	delete($cses{"id_customers"});
	#delete($in{"id_customers"});
	$st2 = 'trjump("/cgi-bin/mod/sales/admin?cmd=console_order&step=2&id_customers=0")';
	
	$in{'search'} = "form";
	$va{'content'}="[ip_forms:customers_confirm_form]<input type='submit' value='Buscar Cliente' class='button' name='customer_search'>&nbsp;<input type='button' value='Cliente Nuevo' class='button' name='customer_new' onclick='".$st2."'>";
	if($in{'customer_search'} eq "Buscar Cliente"){			#-> List
		if($in{'search'} eq "form"){
			$cond = "";
			$va{'speechname'}= 'ccinbound:0- Customer Search';
			if($in{'id_customers'}){
				$cond .= "sl_customers.ID_customers='".$in{'id_customers'}."' ";
			}
			if($in{'id_orders'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				$cond .= "sl_orders.ID_orders='".$in{'id_orders'}."' ";
			}
			if($in{'firstname'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				$cond .= "sl_customers.FirstName LIKE '%".$in{'firstname'}."%' ";
			}
			if($in{'lastname1'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				$cond .= "sl_customers.LastName1 LIKE '%".$in{'lastname1'}."%' ";
			}
			if($in{'lastname2'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				$cond .= "sl_customers.LastName2 LIKE '%".$in{'lastname2'}."%' ";
			}
			if($in{'phone'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				$cond .= "(sl_customers.Phone1 LIKE '%".$in{'phone'}."%' OR sl_customers.Phone2 LIKE '%".$in{'phone'}."%' OR sl_customers.Cellphone LIKE '%".$in{'phone'}."%') ";
			}
			if($in{'cidt'}){
				if($cond ne ""){
					$cond .= "$in{'st'} ";
				}
				#$cond .= "(sl_customers.CID LIKE '%".$in{'cidt'}."%') ";
				$cond .= "(sl_customers.CID = '$in{'cidt'}') ";
			}
			$qry = "sl_customers left JOIN sl_orders ON(sl_customers.ID_customers=sl_orders.ID_customers) ";
			if($cond ne ""){
				$qry.= "WHERE ".$cond." ";
			}
			#JRG start 12/06/2008 change all the customer search
			$qry .= "/* GROUP BY sl_customers.FirstName,sl_customers.LastName1,sl_customers.LastName2 */ ORDER BY  sl_orders.ID_customers ";
			@db_cols = ('ID_customers','FirstName','LastName1','LastName2','Phone1','Phone2','Cellphone','State','Date');
			@headerfields = @db_cols;
			my($sth) = &Do_SQL('SELECT COUNT(DISTINCT sl_customers.ID_customers,sl_customers.FirstName,sl_customers.LastName1,sl_customers.LastName2,sl_customers.Phone1,sl_customers.Phone2,sl_customers.Cellphone,sl_customers.State,sl_orders.Date) FROM '.$qry);
			$va{'matches'} = $sth->rows;
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			if($va{'matches'}>0){
				my ($sth) = &Do_SQL('SELECT DISTINCT sl_customers.ID_customers,sl_customers.FirstName,sl_customers.LastName1,sl_customers.LastName2,sl_customers.Phone1,sl_customers.Phone2,sl_customers.Cellphone,sl_customers.State,sl_orders.Date FROM '.$qry.' LIMIT '.$first.','.$usr{'pref_maxh'}.' ');
				$page .= "<table border='0' cellspacing='0' cellpadding='4' width='100%' class='formtable'>";
				$page .= "<tr><th align='center' colspan='2' class='menu_bar_title'>Resultados de B&uacute;squeda</th></tr><tr><td class='tbltextttl'>Customers : $va{'matches'}</td><td class='tbltextttl' align='right'>P&aacute;ginas :  $va{'pageslist'}</td></tr></table>";
				$page .= "	<table border='0' cellspacing='0' cellpadding='4' width='100%'><tr><th class='menu_bar_title'>ID cliente</th><th class='menu_bar_title'>Nombres</th><th class='menu_bar_title'>Apellidos</th><th class='menu_bar_title'>N&uacutemeros de tel&eacute;fono</th><th class='menu_bar_title'>Estado</th><th class='menu_bar_title'>Fecha &uacute;ltima orden</th></tr>";
				my (@c) = split(/,/,$cfg{'srcolors'});
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;
					$page .= qq|		    <tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="question($rec->{'ID_customers'})">\n|;
					$tel = "";
					if($rec->{'Phone1'}){
						$tel .= "$rec->{'Phone1'}<br>";
					}
					if($rec->{'Phone2'}){
						$tel .= "$rec->{'Phone2'}<br>";
					}
					if($rec->{'Cellphone'}){
						$tel .= "$rec->{'Cellphone'}<br>";
					}										
					$page .= qq|		    <td>$rec->{'ID_customers'}</td><td>$rec->{'FirstName'}</td><td>$rec->{'LastName1'} $rec->{'LastName2'}</td><td>$tel</td><td>$rec->{'State'}</td><td>$rec->{'Date'}</td>\n|;
					$page .= qq|		    </tr>\n|;
				}
				$page .= "</table>";
				$va{'content'} = "[ip_forms:customers_confirm_form]<input type='submit' value='Buscar Cliente' class='button' name='customer_search'>&nbsp;<input type='button' value='Cliente Nuevo' class='button' name='customer_new' onclick='".$st2."'><br><br>";
				$va{'content'} .= $page;							
			} else {
				$va{'content'} = "[ip_forms:customers_confirm_form]<input type='submit' value='Buscar Cliente' class='button' name='customer_search'>&nbsp;<input type='button' value='Cliente Nuevo' class='button' name='customer_new' onclick='".$st2."'><br><br>".&trans_txt('search_nomatches');
			}
			#JRG end 12/06/2008
		} else {
			$va{'speechname'}= 'ccinbound:0- Customer Search';
			$in{'search'} = "form";
			$va{'content'}="[ip_forms:customers_confirm_form]<input type='submit' value='Buscar Cliente' class='button' name='customer_search'>&nbsp;<input type='button' value='Cliente Nuevo' class='button' name='customer_new' onclick='".$st2."'>";
		}
#		} elsif($in{'customer_new'} eq "Cliente Nuevo"){		#-> step 2 without customer
#			$va{'speechname'}= 'ccinbound:0- Customer Search';
#			$in{'search'} = "form";
#			$va{'content'}="step 2";
	} elsif($in{'customer_search'} eq "Otra Busqueda"){	#-> Search Form
		$va{'speechname'}= 'ccinbound:0- Customer Search';
		$in{'search'} = "form";
		$va{'content'}="[ip_forms:customers_confirm_form]<input type='submit' value='Buscar Cliente' class='button' name='customer_search'>&nbsp;<input type='button' value='Cliente Nuevo' class='button' name='customer_new' onclick='".$st2."'>";
	}
	#JRG end#
# }else{
# 	$error{'cid'} = &trans_txt('required');	
# 	++$errors;

# 	print "Content-type: text/html\n\n";
# 	print &build_page("console_newcall.html");
# 	exit;
# }

1;