
##################################################################
#     MERCHANDISING : RESOURCES PAGES       	#
##################################################################
sub mer_reportprod {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	### Products By Status
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Testing'");
	$va{'status_testing'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='on-air'");
	$va{'status_on-air'}= &format_number($sth->fetchrow);	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Active'");
	$va{'status_active'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Inactive'");
	$va{'status_inactive'}= &format_number($sth->fetchrow);	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Web Only'");
	$va{'status_web only'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products");
	$va{'all'}= &format_number($sth->fetchrow);
	
	

	###################################
	### Products By Prices
	###################################
	my (@ranges) = ('','SPrice<1','SPrice>=1.00 AND SPrice<=19.99','SPrice>=19.99 AND SPrice<=29.99',
				'SPrice>=29.99 AND SPrice<=49.99','SPrice>=49.99 AND SPrice<89.99','SPrice>=89.99 AND SPrice<=149.99',
				'SPrice>=149.99 AND SPrice<=999.99','SPrice>=999.99 AND SPrice<=1999.99','SPrice>=1999.99 AND SPrice<5000');
	my (@names) = ('','Without','$1.00 to $19.99','$19.99 to $29.99',
				'$29.99 to $49.99','$49.99 to $89.99','$89.99 to $149.99',
				'$149.99 to $999.99','$999.99 to $1999.99','$1999.99 to ---');
	my (@query) = ('','&to_SPrice=1','From_SPrice=.99&to_Sprice=20&sb=SPrice','From_SPrice=19.98&to_Sprice=30&sb=SPrice',
				'From_SPrice=29.98&to_Sprice=50&sb=SPrice','From_SPrice=49.98&to_Sprice=90&sb=SPrice','From_SPrice=89.98&to_Sprice=150&sb=SPrice',
				'From_SPrice=149.98&to_Sprice=1000&sb=SPrice','From_SPrice=999.98&to_Sprice=2000&sb=SPrice','From_SPrice=1999.98&to_Sprice=5000&sb=SPrice');
	for (1..8){
		%tmp = ('testing'=>0,'on-air'=>0,'active'=>0,'inactive'=>0,'web only'=>0);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE $ranges[$_]");
		$tmp{'all'}= &format_number($sth->fetchrow);
		my ($sth) = &Do_SQL("SELECT Status,COUNT(*) FROM sl_products WHERE $ranges[$_] GROUP BY Status");
		while (@rec = $sth->fetchrow_array()){
			$tmp{lc($rec[0])} = $rec[1];	
		}
		$va{'price_range'} .= qq|
			<tr>
			  	<td class="smalltext" nowrap>&nbsp;&nbsp; $names[$_]</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]')">|.&format_number($tmp{'all'}).qq|</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=testing')">|.&format_number($tmp{'testing'}).qq|</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=on-air')">|.&format_number($tmp{'on-air'}).qq|</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=web only')">|.&format_number($tmp{'web only'}).qq|</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=active')">|.&format_number($tmp{'active'}).qq|</td>
			    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=inactive')">|.&format_number($tmp{'inactive'}).qq|</td>
		 	</tr>\n|;
	}

	###################################
	### Products By Info
	###################################
	my (@ranges) = ('',"Name='None'","SmallDescription='None'","Description='None'",
				"SmallDescription_en='None'","Description_en='None'",'Weight<0.2',
				'SizeW=0 OR SizeH=0 OR SizeL=0','MSRP<1','MAP<1');
	my (@names) = ('','No Name','No Small Description','No Description',
				'No Small Description (en)','No Description (en)','No Weight',
				'No Dimensions','No MSRP','No MAP');
	my (@query) = ('','Name=None','SmallDescription=None','Description=None',
				'SmallDescription_en=None','Description_en=None','To_Weight=0.1',
				'SizeW=0&SizeH=0&SizeL=0&st=or','To_MSRP=1.1','To_MAP=1.1');
	for (1..8){
		%tmp = ('testing'=>0,'on-air'=>0,'active'=>0,'inactive'=>0,'web only'=>0);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE $ranges[$_]");
		$tmp{'all'}= &format_number($sth->fetchrow);
		my ($sth) = &Do_SQL("SELECT Status,COUNT(*) FROM sl_products WHERE $ranges[$_] GROUP BY Status");
		while (@rec = $sth->fetchrow_array()){
			$tmp{lc($rec[0])} = $rec[1];	
		}
		$va{'byinfo'} .= qq|
					<tr>
					  	<td class="smalltext" nowrap>&nbsp;&nbsp; $names[$_]</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1')">|.&format_number($tmp{'all'}).qq|</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=testing')">|.&format_number($tmp{'testing'}).qq|</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=on-air')">|.&format_number($tmp{'on-air'}).qq|</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=web only')">|.&format_number($tmp{'web only'}).qq|</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=active')">|.&format_number($tmp{'active'}).qq|</td>
					    <td class="smalltext" align="center" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&search=Search&$query[$_]&sx=1&status=inactive')">|.&format_number($tmp{'inactive'}).qq|</td>
				 	</tr>\n|;
	}

	

	### Products By missing Info
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Name='None'");
	$va{'infoname'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE SmallDescription='None'");
	$va{'infosmdesc'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Description='None'");
	$va{'infodesc'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE SmallDescription_en='None'");
	$va{'infosmdesc_en'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Description_en='None'");
	$va{'infodesc_en'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Weight='0'");
	$va{'infoweight'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE SizeW='0' OR SizeH=0 OR SizeL=0");
	$va{'infodims'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE MSRP<1");
	$va{'infomsrp'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE MAP<1");
	$va{'infomap'}= &format_number($sth->fetchrow);
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE SLTV_NetCost<1");
	$va{'infocost'}= &format_number($sth->fetchrow);

	print "Content-type: text/html\n\n";
	print &build_page('mer_products_matrix.html');
}


##################################################################
#     MERCHANDISING : CATEGORIES FLIST    	#
##################################################################
sub mer_categories_flist {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
# Last Modification by JRG : 03/09/2009 : Se agrega log
	if ($in{'rebuildcats'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_products_categories;");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("UPDATE sl_products_categories SET ID_top='".&load_topparent_id($rec->{'ID_categories'})."' WHERE ID_products_categories='$rec->{'ID_products_categories'}';");
			&auth_logging('mer_products_catupdated',$rec->{'ID_products_categories'});
		}
		$va{'message'} = "Categories Updated";

	}elsif($in{'exportqry'}){
		print "Content-type: application/vnd.ms-excel\n";
		print "Content-disposition: attachment; filename=all_orders.csv\n\n";
		my (@cols) = ("ID_Orders","Date","Status","ID_customers","First Name","Last Name",
					"Address1","Address2","City","State","Zip","Phone1","Phone2","Phone3","D-Day","Sex","Email",
					"Qty","TotalNet","Shipping","Tax",
					"Station",
					"User Name",
					"ID_Product","Model / Name","Sale Price","Shp Date","Trk Number",
					"Pay Type","Payments",
					"DMA No","DMA","Rank","HH","Hispanics"
					);
		print '"'.join('","',@cols) . "\"\n";
		my ($sth) = &Do_SQL("SELECT *, sl_orders.Date as Date FROM sl_orders_products, sl_orders WHERE sl_orders.ID_orders = sl_orders_products.ID_orders AND sl_orders_products.Status = 'Active';");
		while ($rec = $sth->fetchrow_hashref() ) {
			$ary[0] = $rec->{'ID_orders'};
			$ary[1] = $rec->{'Date'};
			$ary[2] = $rec->{'Status'};
			
			my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$rec->{'ID_customers'}';");
			$rec_cust = $sth2->fetchrow_hashref();
			$ary[3] = $rec->{'ID_customers'};
			$ary[4] = $rec_cust->{'FirstName'};
			$ary[5] = $rec_cust->{'LastName1'};
			$ary[6] = $rec->{'Address1'};
			$ary[7] = $rec->{'Address2'};
			$ary[8] = $rec->{'City'};
			$ary[9] = $rec->{'State'};
			$ary[10] = $rec->{'Zip'};
			$ary[11] = $rec_cust->{'Phone1'};
			$ary[12] = $rec_cust->{'Phone2'};
			$ary[13] = $rec_cust->{'Cellphone'};
			$ary[14] = "$rec_cust->{'bday_month'}-$rec_cust->{'bday_day'}";
			$ary[15] = $rec_cust->{'Sex'};
			$ary[16] = $rec_cust->{'Email'};
			
			$ary[17] = $rec->{'OrderQty'};
			$ary[18] = $rec->{'OrderNet'};
			$ary[19] = $rec->{'OrderShp'};
			$ary[20] = $rec->{'OrderTax'};
			$ary[21] = &load_db_names('sl_pricelevels','ID_pricelevels',$rec->{'ID_pricelevels'},'[Name]');
			$ary[22] = &load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]');
		
			$ary[23] = &format_sltvid($rec->{'ID_products'});
			if (length($rec->{'ID_products'}) >6){
				$ary[24] = &load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Name] [Model]');
			}else{
				$ary[24] = '---';
			}
			$ary[25] = $rec->{'SalePrice'};
			$ary[26] = $rec->{'ShpDate'};
			$ary[27] = "$rec->{'ShpProvider'} $rec->{'Tracking'}";
			
			$ary[29] = 0;
			my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND Status<>'Cancelled';");
			while ($rec_pay = $sth2->fetchrow_hashref()){
				$ary[29] += 1; 
				$ary[28] = $rec_pay->{'Type'};
			}
			
			my ($sth2) = &Do_SQL("SELECT * FROM sl_zipdma WHERE ZipCode='$rec->{'Zip'}';");
			$rec_dma = $sth2->fetchrow_hashref();
			$ary[30] = $rec_dma->{'DMA_NO'};
			$ary[31] = $rec_dma->{'DMA_DESC'};
			$ary[32] = $rec_dma->{'RANK'};
			$ary[33] = $rec_dma->{'Households'};
			$ary[34] = $rec_dma->{'Hispanic'};
			
			print '"'.join('","',@ary) . "\"\n";
		}
		return;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_categories WHERE Status='Active'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' ORDER BY ID_parent;");
		while ($rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_parent'}>0){
				$cols{$rec->{'ID_categories'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'Title'};
			}else{
				$cols{$rec->{'ID_categories'}} = $rec->{'Title'};
			}
		}
			
		foreach $key (sort keys %cols) {
			$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
		}
		
		foreach $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/admin/dbman?cmd=mer_categories&view=$key')\">\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$key &nbsp;&nbsp;</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$cols{$key}</td>\n";
			
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors_categories WHERE ID_categories='$key'");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_number($sth->fetchrow)."&nbsp;&nbsp;</td>\n";	
			
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_categories WHERE ID_categories='$key'");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_number($sth->fetchrow)."&nbsp;&nbsp;</td>\n";			
			$va{'searchresults'} .= "</tr>\n";
		}
		
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}		
	print "Content-type: text/html\n\n";
	print &build_page('mer_categories_flist.html');	
}


##################################################################
#     MERCHANDISING : VENDORS CONTACT   	#
##################################################################
sub mer_vendors_contact {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	## Load Vendor Info
	&load_cfg('sl_vendors');
	my (%rec) = &get_record($db_cols[0],$in{'id_vendors'},'sl_vendors');
	foreach $key (sort keys %rec) {
		$in{'vendors_'.lc($key)} = $rec{$key};
		$in{'vendors_'.lc($key)} =~ s/\n/<br>/g;
	}
	
	## Load Contact Info
	&load_cfg('sl_vendors_contacts');
	my (%rec) = &get_record($db_cols[0],$in{'id_vendors_contacts'},'sl_vendors_contacts');
	foreach $key (sort keys %rec) {
		$in{lc($key)} = $rec{$key};
		$in{lc($key)} =~ s/\n/<br>/g;
	}
	
	## User Info
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});
	
	print "Content-type: text/html\n\n";
	print &build_page('mer_vendors_contact.html');
}

sub mer_addvendor {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($query);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Status='Active' $query;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_vendors WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_parts&view=$in{'id_parts'}&addvendor=$rec->{'ID_vendors'}&tab=2#tabs')">
				<td class="smalltext">$rec->{'ID_vendors'}</td>
				<td class="smalltext">$rec->{'CompanyName'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	$va{'header'} = qq |
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Name</td>
		 </tr>\n|;
		

	print "Content-type: text/html\n\n";
	print &build_page('mer_addvendor.html');
}

sub mer_wreceipt{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 16 Mar 2010 16:15:54
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	if($in{'action'}==1)
	{
		$err=0;
		#Verifica que existan los datos correctos
		my $sth=&Do_SQL("SELECT * FROM sl_purchaseorders INNER JOIN sl_purchaseorders_items on sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders
							WHERE sl_purchaseorders.ID_purchaseorders='$in{'id_purchaseorders'}'
							AND ID_products='$in{'id_supplies'}'");
		if($sth->rows==0){
			$err++;
		}
		$rec=$sth->fetchrow_hashref;
		$max_received=$rec->{'Qty'}-$rec->{'Received'};
		#Valida cantidad
		if($in{'received'}>$max_received or $in{'received'}=='' or $in{'received'}<=0){
			$err++;
			$error{'received'}=&trans_txt("invalid");
		}
		if($err>0){
			$va{'message'}="The information entered is invalid. The max value for received is $max_received";
		}else{
			#Actualiza la información
			&Do_SQL("Update sl_purchaseorders_items set Received=$in{'received'} where ID_purchaseorders_items=$rec->{'ID_purchaseorders_items'}");
			$va{'message'}="The supply has been received";
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('mer_wreceipt.html');
}

#############################################################################
#############################################################################
#	Function: mer_bills_payments
#
#	Created on: 27/02/2013  17:32:10
#
#	Author: Enrique Peña
#
#	Modifications: 08/04/2013-Alejandro Diaz
#					06/26/2013: _RB_: Se agrega contabilidad para aplicacion de depositos en Expenses
#					07/12/2013: _RB_: Se agrega keypoint para perdida/ganancia
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub mer_bills_payments{
#############################################################################
#############################################################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($err,$hide,$legend);
	my $flag=1;
	my $id_ordersttia, $id_po_paid, $id_bills_paid, $id_bills_nopaid;
	my @arr_bills;
	my ($creddep_apply, $creddep_noapply, $id_bills_applies);
	$va{'totals'} = 0;
	$va{'totals_paid'} = 0;
	$va{'totals_unformatted'} = 0;

	$in{'currency'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"Currency") if ($in{'id_vendors'});
	$va{'summary_currency_exchange'} = $in{'currency_exchange'};


	####################
	#################### PROCESAMIENTO
	####################

	if ($in{'process'}) {
		$va{'displayform1'} = 'display:none';
		$va{'displayform2'} = '';

		my $ida_banks;
		my $val_dc_amount_bill = $in{'dc_amount_bill'};
		$val_dc_amount_bill =~ s/\|//g;

		@arr_amount = split /\|/, $in{'amount'};
		@arr_amount_due = split /\|/, $in{'amount_wo_format'};
		$va{'bills_total_amount'}=0;
		for my $i (0..$#arr_amount) {
			$arr_amount[$i] = &filter_values($arr_amount[$i]);
			$arr_amount[$i] =~ s/\,//g;

			$id_ordersttia .= $arr_id_ordersttia[$i].',';
			$string_amount .= $arr_amount[$i].',';

			if ($arr_amount[$i] > 0){
				$va{'bills_total_amount'} += $arr_amount[$i];
			}

			if ($arr_amount[$i] > 0){
				$va{'bills_total_amount_due'} += $arr_amount_due[$i];
			}
		}


		#######################################################################################
		#######################################################################################
		#######################################################################################
		####################
		#################### 			APLICACION DE CREDITS / DEPOSITS
		####################
		#######################################################################################
		#######################################################################################
		#######################################################################################


		if ($in{'id_creddep'}) {		
			my @arr_id_creddep = split /\|/, $in{'id_creddep'};
			my @arr_amount_bill = split /\|/, $in{'dc_amount_bill'};
			my @arr_add_id_creddep = split /\|/, $in{'add_id_creddep'};
			for my $i (0..$#arr_add_id_creddep) {
				my $amount_bill = &filter_values($arr_amount_bill[$i]);
				my $id_creddep = $arr_id_creddep[$i];
				my $add_id_creddep = $arr_add_id_creddep[$i];

				# Validar si vienes los 3 campos requeridos id_creddep , add_id_creddep, dc_amount_bill
				if ($id_creddep and $amount_bill > 0  and $add_id_creddep) {
					# primero confirmamos que realmente este no es un type=bill
					# verificar que el bill al que se va aplicar no este pagado
					# verificar el saldo pendiente de ese bill
					# verificar que coincida el currency del origen y destino
					
					my ($sth) = &Do_SQL("SELECT COUNT(*), Type, (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills))as AmountAvailable
					, (SELECT (Amount - (
						SELECT IFNULL(SUM(AmountPaid),0)as Amount 
						FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
						WHERE tablename='bills' AND tableid=sl_bills.ID_bills AND Type='Credits'
					) + (
						SELECT IFNULL(SUM(AmountPaid),0)as Amount 
						FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
						WHERE tablename='bills' AND tableid=sl_bills.ID_bills AND Type='Debits'
					) - (
						SELECT IFNULL(SUM(Amount),0)as Amount 
						FROM sl_bills_applies WHERE ID_bills_applied = sl_bills.ID_bills
					))as AmountRemaining FROM sl_bills WHERE ID_bills = '$add_id_creddep')as AmountRemaining
					FROM sl_bills WHERE ID_bills = '$id_creddep' 
					AND (if(Type='Deposit',Status ='Paid',Status IN('Processed','Partly Paid')))
					AND Type NOT IN ('Bill') 
					AND Currency=( SELECT Currency FROM sl_bills WHERE ID_bills = '$add_id_creddep' );");
					my ($is_valid_bill, $bill_type, $amount_available, $amount_remaining) = $sth->fetchrow_array();

					 # &cgierr($amount_available.'>0---'.$amount_bill.'---<='.$amount_available.'---'.$amount_remaining.'>0');
					if ($is_valid_bill) {
						if ($amount_available > 0 and $amount_bill <= $amount_available and $amount_remaining > 0 and $amount_bill <= $amount_remaining) {

							&Do_SQL("START TRANSACTION;");

							## aplicamos el Credit/Deposit
							my $sth = &Do_SQL("INSERT INTO sl_bills_applies SET ID_bills='$id_creddep', ID_bills_applied='$add_id_creddep', Amount='$amount_bill', Date=CURDATE(), Time=curtime(), ID_admin_users=$usr{'id_admin_users'};");

							if ($sth->rows() == 1){
								$creddep_apply .= $id_creddep.',';
								$id_bills_applies .= $sth->{'mysql_insertid'}.',';

								#log
								$in{'db'} = "sl_bills";
								&auth_logging('bills_applied',$id_creddep);
								&auth_logging('bills_deposit_credit_applied',$add_id_creddep);

								my ($sth) = &Do_SQL("INSERT INTO sl_bills_notes SET Notes='".&trans_txt('bills_payment_added')." (".&format_price($amount_bill).")',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_bills='$in{'add_id_creddep'}';");
								&auth_logging('bills_note_added',$in{'add_id_creddep'});

								## revisamos si el monto que se debe del bill aplicado == 0 se marca como bill Paid
								
								
								my ($amount_remaining) = &bills_amount_due($add_id_creddep);
								if ($amount_remaining == 0) {
									my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Paid' WHERE ID_bills='$add_id_creddep' LIMIT 1;");
									if ($sth->rows() == 1){

										#log
										# $id_bills_paid .= $add_id_creddep.',';
										$in{'db'} = "sl_bills";
										&auth_logging('bills_paid',$add_id_creddep);

										###-------------------------------------------------------
										## Se actualiza el campo Paid en purchaseorders_adj
										###-------------------------------------------------------
										&payment_po_adj($add_id_creddep);
										###-------------------------------------------------------
									}
								}elsif ($amount_remaining > 0) {
									my ($sth2) = &Do_SQL("UPDATE sl_bills SET Status = 'Partly Paid' WHERE ID_bills = '".$add_id_creddep."' LIMIT 1;");
									if ($sth->rows() == 1){

										# Log
										$in{'db'} = "sl_bills";
										&auth_logging('bills_partial_payment',$add_id_creddep);
									}
								}

								## revisamos si el amount disponible del bill D/C == 0 se marca como Status=Paid
								my ($sth) = &Do_SQL("SELECT (Amount - (
										SELECT IFNULL(SUM(AmountPaid),0)as Amount 
										FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
										WHERE tablename='bills' AND tableid=sl_bills.ID_bills AND Type='Credits'
									) + (
										SELECT IFNULL(SUM(AmountPaid),0)as Amount 
										FROM sl_banks_movrel INNER JOIN sl_banks_movements USING(ID_banks_movements) 
										WHERE tablename='bills' AND tableid=sl_bills.ID_bills AND Type='Debits'
									) - (
										SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies 
										WHERE ID_bills = sl_bills.ID_bills
									))as AmountRemaining FROM sl_bills WHERE ID_bills = '$id_creddep';");
								my ($amount_remaining) = $sth->fetchrow_array();
								if ($amount_remaining == 0) {
									my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Paid' WHERE ID_bills='$id_creddep' LIMIT 1;");
									if ($sth->rows() == 1){

										#log
										$id_bills_paid .= $id_creddep.',';
										&auth_logging('bills_paid',$id_creddep);
									}
								}elsif ($amount_remaining > 0) {
									my ($sth) = &Do_SQL("UPDATE sl_bills SET Status='Partly Paid' WHERE ID_bills='$id_creddep' LIMIT 1;");
									if ($sth->rows() == 1){

										#log
										$id_bills_paid .= $add_id_creddep .',';
										&auth_logging('bills_partial_payment',$id_creddep);
									}
								}

								########################################################
								########################################################
								## Movimientos de contabilidad - APLICACION DE ANTICIPO O CREDITO
								########################################################
								########################################################
								my $j = 0;my $str_pos;my $str_bills;my $str;
								my $id_bills = int($id_creddep);
								my $amount = $amount_bill;
								my $amount_derived = $amount;
								my $amt_negative = 0;


								## Bill Deposit Data
								my ($sth) = &Do_SQL("SELECT sl_bills.Type,ID_vendors,Category,ID_accounts,IF(sl_banks_movements.currency_exchange > 1, sl_banks_movements.currency_exchange, sl_bills.currency_exchange) FROM sl_bills INNER JOIN sl_vendors USING(ID_vendors) INNER JOIN sl_banks_movrel ON tableid = sl_bills.ID_bills AND tablename = 'bills' INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE ID_bills = '".$id_bills."';");
								my($bill_type,$id_vendors,$vendor_category,$ida_deposit,$currency_exchange,$pct_paid) = $sth->fetchrow();
								$currency_exchange = 1 if !$currency_exchange;
								$ida_deposit = 0 if !$ida_deposit;
								my $this_type;

	
								my ($sth) = &Do_SQL("/* $bill_type,$id_vendors,$vendor_category,$currency_exchange */ 
													SELECT 
														IF(ID_purchaseorders > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders,0) AS ID_po
														,IF(ID_bills_expenses > 0 AND sl_bills_expenses.Amount > 0,ID_bills_expenses,0) AS ID_expense
														,IF(ID_purchaseorders_adj > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders_adj,0) AS ID_po_adj
														,$amount / sl_bills.Amount 
													FROM sl_bills  
														LEFT JOIN sl_bills_pos USING(ID_bills) 
														LEFT JOIN sl_bills_expenses USING(ID_bills) 
													WHERE sl_bills.ID_bills = '".$add_id_creddep."' 
													HAVING ID_po > 0 OR ID_expense > 0 OR ID_po_adj > 0 
													ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;");
								my $rows = $sth->rows();

								while(my($id_po, $id_expenses, $id_po_adj, $paid_pct) = $sth->fetchrow()) {

									++$j;


									if($id_po) {

										(!$this_type) and ($this_type = 'po');
										$amt_negative = ($j == $rows ) ? &load_bill_amt_negative($add_id_creddep,'sl_bills_pos') : 0;
										##################
										##################
										### Pago de PO
										##################
										##################

										my ($sth) = &Do_SQL("SELECT  
															SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) / SUM(Amount) AS PctPaid , 
															( (SUM(IF(ID_purchaseorders = '$id_po',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
															FROM sl_bills_pos WHERE ID_bills = '". $add_id_creddep ."';");
										my($pct , $this_pct) = $sth->fetchrow();

										my $this_amount = $j < $rows ? round($this_pct * $amount ,3) : $amount_derived;
										$amount_derived -= $this_amount;
										$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

										my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$currency_exchange);
										&accounting_keypoints('po_apply_' . lc($bill_type) . '_'. lc($vendor_category), \@params );
										&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='$bill_type Applied\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount *  $currency_exchange,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='$bill_type Applied\nTo PO: $id_po\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										$str_pos .= "$id_po,";

									}elsif($id_expenses){

										(!$this_type) and ($this_type = 'expenses');
										$amt_negative = ($j == $rows ) ? &load_bill_amt_negative($add_id_creddep,'sl_bills_expenses') : 0;
										##################
										##################
										### Pago de Expense
										##################
										##################
										#my ($sth) = &Do_SQL("SELECT SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) / SUM(Amount) FROM sl_bills_expenses WHERE ID_bills = '". $add_id_creddep ."';");
										#my($pct) = $sth->fetchrow();

										my $this_query = "SELECT 
															SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) / SUM(Amount) AS PctPaid,
															( (SUM(IF(ID_bills_expenses = '$id_expenses',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
															FROM sl_bills_expenses WHERE ID_bills = '". $add_id_creddep ."';";

										my ($sth) = &Do_SQL($this_query);
										my($pct, $this_pct) = $sth->fetchrow();

										my $this_amount = $j < $rows ? round($this_pct * $amount ,3) : $amount_derived;
										$amount_derived -= $this_amount;
										$str .= "$this_query\n$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

										my @params = ($add_id_creddep,$id_bills,$ida_banks,$ida_deposit,$this_amount,$currency_exchange,$this_pct);
										## Nota: Aqui estaba como primer parametro $add_id_creddep en lugar del expense (confirmar con cxp)

										#&cgierr('bills_expenses_apply_' . lc($bill_type) . '_'. lc($vendor_category) . " -- $id_expenses,$ida_banks,$ida_deposit,$this_amount,$currency_exchange,$pct");
										&accounting_keypoints('bills_expenses_apply_' . lc($bill_type) . '_'. lc($vendor_category), \@params );
										my $exchange_rate = $currency_exchange > 0 ? $currency_exchange : 1;
										&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='$bill_type Applied\nTo Bill: $add_id_creddep\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$add_id_creddep', Notes='$bill_type Applied\nFrom Bill: $id_bills\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										$str_bills .= "$add_id_creddep,";

									}else{
										(!$this_type) and ($this_type = 'po_adj');
										$amt_negative = ($j == $rows ) ? &load_bill_amt_negative($add_id_creddep,'sl_bills_pos') : 0;
										##################
										##################
										### Pago de PO_Adj
										##################
										##################

										my ($sth) = &Do_SQL("SELECT  
																SUM(IF(ID_purchaseorders_adj = '$id_po_adj',Amount,0)) / SUM(Amount) AS PctPaid , 
																((SUM(IF(ID_purchaseorders_adj = '$id_po_adj',Amount,0)) - $amt_negative ) / SUM(Amount)) * $paid_pct
															FROM sl_bills_pos WHERE ID_bills = '". $add_id_creddep ."';");
										my($pct , $this_pct) = $sth->fetchrow();

										my $this_amount = $j < $rows ? round($this_pct * $amount ,3) : $amount_derived;
										$amount_derived -= $this_amount;
										$str .= "$amount : $pct ($pct * $paid_pct = $this_pct) = $this_amount - $amount_derived\n";

										$id_po = &load_name("sl_purchaseorders_adj", "ID_purchaseorders_adj", $id_po_adj, "ID_purchaseorders");

										my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$currency_exchange);
										&accounting_keypoints('po_apply_' . lc($bill_type) . '_'. lc($vendor_category), \@params );
										&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='$bill_type Applied\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount *  $currency_exchange,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										&Do_SQL("INSERT INTO sl_bills_notes SET ID_bills = '$id_bills', Notes='$bill_type Applied\nTo PO: $id_po\nOriginal Amount: $this_amount\nCurrency Exchange: $currency_exchange\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
										$str_pos .= "$id_po,";
									}

								}
								#&cgierr($str);
								chop($str_pos);
								chop($str_bills);

								my $modquery = $str_pos ne '' ? "ID_tableused IN ($str_pos) AND tableused = 'sl_purchaseorders'" : "ID_tableused IN ($str_bills)  AND tableused = 'sl_bills'";
								my $query_to_paid = "UPDATE sl_movements SET ID_journalentries = 0,tablerelated = 'sl_bills', ID_tablerelated = '$id_bills' WHERE $modquery AND (ID_tablerelated = 0 OR ID_tablerelated IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 40 AND ID_admin_users = '$usr{'id_admin_users'}';";
								&Do_SQL($query_to_paid);
								#my $query_to_paid2 = "UPDATE sl_movements SET ID_journalentries = 0, tablerelated = 'sl_bills', ID_tablerelated = '$id_bills' WHERE $modquery AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 5 AND ID_admin_users = '$usr{'id_admin_users'}';";
								#&Do_SQL($query_to_paid2);

								##################
								##################
								### Bill Expense Paid
								##################
								##################
								if($this_type eq 'expenses'){

									##########
									########## Revision de Expense Pagado
									##########
									my @params = ($add_id_creddep);
									#&cgierr('bills_'. $this_type .'_paid_' . lc($vendor_category) . " -- $id_expenses,0,$ida_deposit,$this_amount,$currency_exchange,$pct");
									&accounting_keypoints('bills_'. $this_type .'_paid_' . lc($vendor_category), \@params );

								}

							}else {
								$creddep_noapply .= $id_creddep.',';
								
							}

							&Do_SQL("COMMIT");

						}else {
							$va{'messages'} .= &trans_txt('bills_amount_available_invalid');
							delete($in{'process'});
						}
					}else {
						$va{'messages'} .= &trans_txt('bills_deposit_credit_notprocess').' : Bill '.$id_creddep.'<br>';
						delete($in{'process'});
					}
				}
			}
			chop($creddep_noapply);
			chop($creddep_apply);
			chop($id_bills_applies);
			chop($id_bills_paid);
		}

		#######################################################################################
		#######################################################################################
		#######################################################################################
		####################
		#################### 			PAGO DE BILLS / EXPENSES
		####################
		#######################################################################################
		#######################################################################################
		#######################################################################################


		if ($va{'bills_total_amount'} > 0 and $in{'id_ordersttia'} and $va{'bills_total_amount'} <= $va{'bills_total_amount_due'}) {

			$err=0;
			@arr_id_ordersttia = split /\|/, $in{'id_ordersttia'};
			$id_ordersttia='';
			$amount='';

			chop($id_ordersttia);
			chop($amount);

			if (!$in{'id_banks'} or $in{'id_banks'} eq ""){
				$error{'id_banks'} = &trans_txt('required');
				++$err;
			}else{
				my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts FROM sl_banks INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE ID_banks = ". $in{'id_banks'} ." AND sl_banks.Status = 'Active' AND sl_accounts.Status = 'Active' LIMIT 1;");
				$ida_banks = $sth->fetchrow();

				if(!$ida_banks){
					$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
					++$err;	
				}

			}
			
			if (!$in{'bankdate'} or $in{'bankdate'} eq ""){
				$error{'bankdate'} = &trans_txt('required');
				++$err;
			}
			
			# si el currency del banco es != al currency de bill es requerido en tipo de cambio
			$in{'currency_exchange'} = &filter_values($in{'currency_exchange'});
			my $currency_bank = &load_name("sl_banks","ID_banks",$in{'id_banks'},"Currency");
			my $currency_bill = &load_name("sl_bills","ID_bills",$in{'id_bills'},"Currency");

			if ($currency_bank ne $in{'currency'} ) {
				if (!$in{'currency_exchange'} or $in{'currency_exchange'} <= 0) {
					$error{'currency_exchange'} = &trans_txt('required');
					++$err;
				}
			}else{
				$in{'currency_exchange'} = 1;
			}

			my $sql_add_refnum = "AND RefNum = '".&filter_values($in{'refnum'})."'";
			if ($in{'refnum'}) {
				$in{'refnumcustom'} = $in{'refnum'};
				delete($in{'refnum'})
			}

			if (!$err and !$in{'refnum_auto'} and !$in{'refnum'} and !$in{'refnumcustom'}) {
				$error{'refnum'} = &trans_txt('required');
				++$err;
			}

			# Se hace una validacion extra para saber si es requerible que escriba un RefNum
			if (!$err and $in{'refnum_auto'}) {
				#Se verifica que no existe un registro con la misma informacion
				# 1  validar que los bills no esten pagados
				# 2 validar que no existe un movrel para bills con estos ID
				my ($sth_refnum) = &Do_SQL("SELECT `RefNum` +1 FROM `sl_banks_movements` WHERE 1 AND Type='Credits' AND doc_type='$in{'doc_type'}' AND ID_banks='".&filter_values($in{'id_banks'})."' ORDER BY cast(`RefNum` as unsigned) DESC LIMIT 1;");
				my ($refnum_auto) = $sth_refnum->fetchrow_array();

				if (!$refnum_auto){
					# $error{'refnum'} = &trans_txt('required');
					# ++$err;

					$in{'refnum'} = 1;
				}else{
					$in{'refnum'} = $refnum_auto;
				}
				$sql_add_refnum = "AND RefNum = '".&filter_values($in{'refnum'})."'";
			}

			if (!$err) {
				$flag=0;

				# ################################################
				# Agregar el campo en sl_banks_movrel <- listo en la 19
				# Primero hay que calcular la suma de lo que se va pagar de todos los bills
				# Grabar en el campo nuevo solo la cantidad pagada a este bill
				# Este cambio av repercutir en el tab balance, revisalo y en el tab de banks_movements
				# Si esta suma es menos o igual
				# Si ocurre un error en el proceso tiene que regresar todo a como estaba y no afectar nada

				# ################################################
				# Creo que ahora aplicara si existe en sl_banks_movements algo con este tipo de pago y el mismo refnum entonces enviar error

					my ($sth2) = &Do_SQL("SELECT COUNT(*) 
						FROM sl_banks_movements 
						WHERE 1 AND Type = 'Credits' 
						AND ID_banks = '".&filter_values($in{'id_banks'})."'
						AND BankDate = '".&filter_values($in{'bankdate'})."'
						AND doc_type = '".&filter_values($in{'doc_type'})."'
						$sql_add_refnum");
					my ($duplicate) = $sth2->fetchrow_array();

					if (!$duplicate) {
						&Do_SQL("START TRANSACTION;");

						my $add_amountcurrency = " AmountCurrency = NULL, ";
						$flag_calculate = 0;
						
						if ($cfg{'acc_default_currency'} ne $in{'currency'} and $in{'currency_exchange'} > 0) {
							$flag_calculate = 1;
							$amount_calculate = $va{'bills_total_amount'} * $in{'currency_exchange'};
							$add_amountcurrency = " AmountCurrency = '$va{'bills_total_amount'}', ";
						}
						my $add_amount = ($flag_calculate) ? $amount_calculate : $va{'bills_total_amount'};
						my $sql_refnumcustom = ($in{'refnumcustom'})? " RefNumCustom = '".&filter_values($in{'refnumcustom'})."', ":" RefNumCustom =NULL, ";

						###
						### Se obtiene la cuenta de banco del proveedor
						###
						my $sth_bnk = &Do_SQL("SELECT sl_vendors.BankAccount FROM sl_vendors INNER JOIN sl_bills ON sl_vendors.ID_vendors = sl_bills.ID_vendors WHERE ID_bills = ".int($arr_id_ordersttia[$i]).";");
						my $bank_account = $sth_bnk->fetchrow();
						my $sql_bank_account = '';
						if( $bank_account ){
							$sql_bank_account = " RefBankAccount = '*".substr($bank_account, -5)."', ";
						}

						my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements SET
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
							DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
						$id_banks_movements = $sth->{'mysql_insertid'};
						
						if ($sth->rows() == 1) {
							# Log
							$in{'db'} = "sl_banks_movements";
							&auth_logging('fin_banks_movements_added', $id_banks_movements);

							# Por cada bill pagado se agrega un registro en sl_banks_movrel solo con el Amount Pagado a cada uno
							for my $i (0..$#arr_amount) {
								if ($arr_amount[$i] > 0){
									if ($arr_amount[$i] <= $arr_amount_due[$i]){
										my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET 
											ID_banks_movements = '$id_banks_movements', 
											tablename = 'bills', 
											tableid = '".$arr_id_ordersttia[$i]."', 
											AmountPaid = '".$arr_amount[$i]."',
											DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
										my ($this_movrel) = $sth->{'mysql_insertid'};
										$id_banks_movrel .= $this_movrel.',';

										$va{'bill_amount_remaining_'.$arr_id_ordersttia[$i]} = $arr_amount[$i];

										# Si se inserto vamos a revisar el bill para cambiar el status a Pais o Partly Paid
										$va{'bill_amount_due'} = &bills_amount_due($arr_id_ordersttia[$i]);
										if ($va{'bill_amount_due'} == 0){
											my ($sth2) = &Do_SQL("UPDATE sl_bills SET Status = 'Paid' WHERE ID_bills = '".$arr_id_ordersttia[$i]."' LIMIT 1;");

											# Log
											$in{'db'} = "sl_bills";
											&auth_logging('bills_paid',$arr_id_ordersttia[$i]);

											###-------------------------------------------------------
											## Se actualiza el campo Paid en purchaseorders_adj
											###-------------------------------------------------------
											&payment_po_adj($arr_id_ordersttia[$i]);
											###-------------------------------------------------------
										}elsif($va{'bill_amount_due'} > 0){
											my ($sth2) = &Do_SQL("UPDATE sl_bills SET Status = 'Partly Paid' WHERE ID_bills = '".$arr_id_ordersttia[$i]."' LIMIT 1;");

											# Log
											$in{'db'} = "sl_bills";
											&auth_logging('bills_partial_payment',$arr_id_ordersttia[$i]);
										}

										# Enviar datos al Summary
										$id_bills_paid .= $arr_id_ordersttia[$i].',';

										########################################################
										########################################################
										## Movimientos de contabilidad
										########################################################
										########################################################
										my $x = 0;my $str_pos;my $str_bills;my $str;
										my $id_bills = int($arr_id_ordersttia[$i]);
										my $amount = $arr_amount[$i];
										my $amount_derived = $amount;
										my $pct_derived = 1;
										my $this_type;my $vcat;
										my $amt_negative = 0;


										#################################
										#################################
										## PO o Expense?
										#################################
										#################################

										my ($sth) = &Do_SQL("SELECT ID_vendors
																,Category
																,IF(ID_purchaseorders > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders,0) AS ID_po
																,IF(ID_bills_expenses > 0 AND sl_bills_expenses.Amount > 0,ID_bills_expenses,0) AS ID_expense
																,IF(ID_purchaseorders_adj > 0 AND sl_bills_pos.Amount > 0,ID_purchaseorders_adj,0) AS ID_po_adj
																,$amount / sl_bills.Amount 
															FROM sl_bills 
																INNER JOIN sl_vendors USING(ID_vendors) 
																LEFT JOIN sl_bills_pos USING(ID_bills) 
																LEFT JOIN sl_bills_expenses USING(ID_bills) 
															WHERE sl_bills.ID_bills = '".$id_bills."' 
															HAVING ID_po > 0 OR ID_expense > 0 OR ID_po_adj > 0  
															ORDER BY sl_bills_pos.Amount, sl_bills_expenses.Amount;");
										my $rows = $sth->rows();

										while(my($id_vendors, $vendor_category, $id_po, $id_expenses, $id_po_adj, $paid_pct) = $sth->fetchrow()) {

											++$x;
											(!$vcat) and ($vcat = $vendor_category);

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

												my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$in{'currency_exchange'},$id_po_adj);
												&accounting_keypoints('po_payment_'. lc($vendor_category), \@params );
												my $exchange_rate = $in{'currency_exchange'} > 0 ? $in{'currency_exchange'} : 1;
												&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $in{'currency_exchange'}\nTotal Paid: ".round($this_amount * $exchange_rate,3)." ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
												$str_pos .= "$id_po,";

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
												my @params = ($id_po,$id_bills,$ida_banks,$this_amount,$in{'currency_exchange'},$id_po_adj);
												&accounting_keypoints('po_payment_'. lc($vendor_category), \@params );
												my $exchange_rate = $in{'currency_exchange'} > 0 ? $in{'currency_exchange'} : 1;
												&Do_SQL("INSERT INTO sl_purchaseorders_notes SET ID_purchaseorders = '$id_po', Notes='Payment Posted\nOriginal Amount: $this_amount\nCurrency Exchange: $in{'currency_exchange'}\nTotal Paid: ".round($this_amount * $exchange_rate,3)."\nPO_Adj: $id_po_adj ',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
												$str_pos .= "$id_po,";
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
										my $query_to_paid = "UPDATE sl_movements SET EffDate = '".&filter_values($in{'bankdate'})."', ID_journalentries = 0 $modquery_bills_pos WHERE $modquery TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 10 AND ID_admin_users = '$usr{'id_admin_users'}';";
										&Do_SQL($query_to_paid);


										##################
										##################
										### Pago de Expense
										##################
										##################
										if($this_type eq 'expenses' and $vcat){

											##########
											########## Revision de Expense Pagado
											##########
											my @params = ($id_bills);
											#&cgierr('bills_'. $this_type .'_paid_' . lc($vendor_category) . " -- $id_expenses,0,$ida_deposit,$this_amount,$currency_exchange,$pct");
											&accounting_keypoints('bills_'. $this_type .'_paid_' . lc($vcat), \@params );

										}

									}
								}
							} # Fin for my $i (0..$#arr_amount)
						}else {
							# $id_bills_nopaid .= $arr_id_ordersttia[$i].',';
							# no se aplico el pago
							# delete($in{'process'});
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

			}else {
				if ($val_dc_amount_bill eq '') {
					$flag=1;
					$va{'messages'} = &trans_txt('reqfields_short');
					delete($in{'process'});
				}
			}
		}else {
			if ($val_dc_amount_bill eq '') {
				$flag=1;
				$va{'messages'} = &trans_txt('bills_required');
				$va{'messages'} = &trans_txt('bills_amount_invalid') if ($va{'bills_total_amount'} <= 0);
				$va{'messages'} = &trans_txt('bills_amounts_not_match') if ($va{'bills_total_amount'} > $va{'bills_total_amount_due'});
				delete($in{'process'});
			}
		}

		##########################################
		# Si hubo pagos aplicados a POS
		if ($id_bills_paid ne '') {
			# Se valida si el monto de los PO´S se pago en su totalidad y se cambia de estatus			
			my ($sth5) = &Do_SQL("SELECT * FROM sl_bills_pos WHERE ID_bills IN ($id_bills_paid)");
			while ($rec = $sth5->fetchrow_hashref){

				my ($id_vendors,$amount);
				#Se suma el monto total del PO.
				my ($sth2) = &Do_SQL("SELECT
				IFNULL((SELECT SUM(sl_banks_movements.Amount) FROM sl_bills_pos INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE ID_purchaseorders = '$rec->{'ID_purchaseorders'}' AND tablename = 'bills' AND TIMESTAMPDIFF(SECOND,CONCAT(sl_banks_movements.Date, ' ',sl_banks_movements.Time), NOW()) BETWEEN 0 AND 10),0)as ThisPayment, 
				IFNULL((SELECT SUM(sl_banks_movements.Amount) FROM sl_bills_pos INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE ID_purchaseorders = '$rec->{'ID_purchaseorders'}' AND tablename = 'bills'),0)as TotalPaid
				, IFNULL((SELECT SUM(Total) FROM sl_purchaseorders_items WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0) + IFNULL((SELECT SUM(Total) FROM sl_purchaseorders_adj WHERE ID_purchaseorders = sl_purchaseorders.ID_purchaseorders),0)as TotalPO,
				ID_vendors
				FROM sl_purchaseorders WHERE 1
				AND sl_purchaseorders.Status NOT IN('Cancelled','Paid')
				AND sl_purchaseorders.Auth = 'Approved'
				AND ID_purchaseorders = '$rec->{'ID_purchaseorders'}';");
				($amount, $in{'amount_po_paid'}, $in{'amount_po'}, $id_vendors) = $sth2->fetchrow_array();

				#Se calculo el monto deudor del PO, tomando en cuenta el total dep PO´s menos Pagos hechos
				$amount_due_po = ($in{'amount_po'}-$in{'amount_po_paid'});
				#Si el monto deudor es igual a 0 significa que el PO se encuentra pagado y se actualiza su estatus a Paid
				if($amount_due_po == 0){
					#Se cambia el estatus del PO a Paid
					my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Status = 'Paid' WHERE ID_purchaseorders = '$rec->{'ID_purchaseorders'}' LIMIT 1;");
					#Log
					$in{'db'} = "sl_purchaseorders";
					&auth_logging('mer_po_pay_applied',$rec->{'ID_purchaseorders'});
					&auth_logging('mer_po_paid',$rec->{'ID_purchaseorders'});

					$id_po_paid .= $rec->{'ID_purchaseorders'}.',';

				}else{
					#Log
					$in{'db'} = "sl_purchaseorders";
					&auth_logging('mer_po_pay_applied',$rec->{'ID_purchaseorders'});
				}
				
				########################################################
				########################################################
				## Movimientos de contabilidad
				########################################################
				########################################################
				my $vendor_category = &load_name('sl_vendors','ID_vendors', $id_vendors,'Category');
				my @params = ($rec->{'ID_purchaseorders'},$amount_due_po,$in{'currency_exchange'});
				&accounting_keypoints('po_paid_'. lc($vendor_category), \@params );

			}
		}
	}

	if($flag and !$in{'process'}) {
		$va{'div_summary'} = 'display:none;';
		$va{'displayform1'} = '';
		$va{'displayform2'} = 'display:none';
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
		
		if($in{'id_ordersttia'}) {
			@arr_bills = $in{'id_ordersttia'};
			if ($in{'id_ordersttia'} =~ m/\|/) {
				 @arr_bills = split /\|/, $in{'id_ordersttia'};
			}
		}

		 # /*NOT IN ('Paid','Void')*/
		my ($sth) = &Do_SQL("SELECT COUNT(*) 
			FROM  sl_bills as bills
			WHERE bills.Status IN('Processed','Partly Paid')
			AND Type = 'Bill' 
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
		if ($va{'matches'} > 0 and $in{'id_vendors'}){
			$va{'displayform1'} = 'display:none';
			$va{'displayform2'} = '';
			
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
				WHERE bills.Status IN('Processed','Partly Paid')
				AND Type = 'Bill' 
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
				$query ORDER BY bills.ID_bills; ");

			$select_creddep = '';
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$select_creddep .= qq|<option value="|.$rec->{'ID_bills'}.qq|">|.$rec->{'ID_bills'}.qq|</option>|;
				$d = 1 - $d;

				# rutina para remarcar checkbox seleccionados
				my $checked = '';
				my $temp_id_bill = $rec->{'ID_bills'};
				if(@arr_bills and grep $_ eq $temp_id_bill, @arr_bills) {
					$checked = ' checked="checked" ';
					$va{'totals_paid'} += $rec->{'AmountAvailable'};
				}

				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<input type='hidden' name='id_ordersttia' class='id_ordersttia' value='$rec->{'ID_bills'}'>
						&nbsp;
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}
						</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext">$rec->{'Type'}</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|</td>
					<td class="smalltext" align="right"><a href="#" onclick="return print_amount('amount_$rec->{'ID_bills'}','$rec->{'AmountAvailable'}');">|.&format_price($rec->{'AmountAvailable'}).qq|</a>
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$rec->{'AmountAvailable'}.qq|">
					</td>
					<td class="smalltext" align="right">
						<span class="span_amount" id="span_amount_|.$rec->{'ID_bills'}.qq|" style="display:">
							<input type="text" name="amount" id="amount_|.$rec->{'ID_bills'}.qq|" value="" size="10">
						</span>
					</td>
				</tr>\n|;

				$va{'totals'} += $rec->{'AmountAvailable'};

			}
			$va{'totals_unformatted'} = $va{'totals'};
			$va{'totals'} = &format_price($va{'totals'});
			$va{'totals_paid_unformatted'} = ($va{'totals_paid'} > 0)? $va{'totals_paid'}:0;
			$va{'totals_paid'} = ($va{'totals_paid'} > 0)? &format_price($va{'totals_paid'}):'';
			$va{'button_p'} = qq| <p align="center"><input type="submit" class="button" value="Pay Bills" id="btn_pay" style="display:"></p> |;
			
		}else{

			$va{'pageslist'} = 1;
			if (int($in{'id_vendors'}) == 0) {
				$va{'matches'} = 0;
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='8' align="center">|.&trans_txt('bills_list_deposits_no_vendorid').qq|</td>
					</tr>\n|;
			}else {
				$va{'displayform1'} = 'display:none';
				$va{'displayform2'} = '';
				$va{'searchresults'} = qq|
					<tr>
						<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}
		}

		## list Deposits/Credits to be apllied
		# AND (if(Type='Deposit',Status ='Paid',Status NOT IN ('Void','Paid')))
		my ($sth) = &Do_SQL("SELECT 
								COUNT(*) 
							FROM sl_bills WHERE 1
								AND (IF(Type='Deposit',Status ='Paid',Status IN('Processed','Partly Paid')))
								AND Type IN ('Deposit','Credit') 
								AND Amount > 0 
								AND (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills)) > 0 
								AND ID_vendors = '$in{'id_vendors'}';");

		$va{'dc_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		if ($va{'dc_matches'}>0 and int($in{'id_vendors'}>0)){

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'dc_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'dc_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT *, (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills))as AmountAvailable FROM  sl_bills 
				WHERE 1
				AND (if(Type='Deposit',Status ='Paid',Status IN('Processed','Partly Paid')))
				AND Type IN ('Deposit','Credit') 
				AND Amount > 0 
				AND (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills)) > 0 
				AND ID_vendors = '$in{'id_vendors'}'
			/*LIMIT $first,$usr{'pref_maxh'}*/; ");
			
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$va{'forvendor'} = qq|for Vendor: <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a>|;
				$d = 1 - $d;

				# rutina para remarcar checkbox seleccionados
				my $checked = '';
				my $temp_id_bill = $rec->{'ID_bills'};
				if(@arr_bills and grep $_ eq $temp_id_bill, @arr_bills) {
					$checked = ' checked="checked" ';
					$va{'dc_totals_paid'} += $rec->{'AmountAvailable'};
				}

				$va{'dc_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<!--input type='checkbox' name='id_creddepX' class='id_creddepX' value='$rec->{'ID_bills'}' $checked-->
						<input type='hidden' name='id_creddep' class='id_creddep' value='$rec->{'ID_bills'}' $checked>
						&nbsp;
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class="smalltext">
							<select name="add_id_creddep" >
								<option value="">---</option>
								|.$select_creddep.qq|
							</select>
					</td>
					<!--td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td-->
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext">$rec->{'Type'}</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|
					<td class="smalltext" align="right"><a href="#" onclick="return print_amount('dc_amount_bill_$rec->{'ID_bills'}','|.$rec->{'AmountAvailable'}.qq|');">|.&format_price($rec->{'AmountAvailable'}).qq|</a>
						<input type="hidden" name="dc_amount_wo_format" id="dc_amount_unformatted_$rec->{'ID_bills'}" value="|.$rec->{'AmountAvailable'}.qq|">
					</td>
					<td class="smalltext" align="right"><span class="span_amount_bill" id="dc_span_amount_bill$rec->{'ID_bills'}" style="display:"><input type="text" name="dc_amount_bill" id="dc_amount_bill_$rec->{'ID_bills'}" value="" size="10"></span></td>
				</tr>\n|;

				$va{'dc_totals'} += $rec->{'AmountAvailable'};

			}
			$va{'dc_totals_unformatted'} = $va{'dc_totals'};
			$va{'dc_totals'} = &format_price($va{'dc_totals'});
			$va{'dc_totals_paid_unformatted'} = ($va{'dc_totals_paid'} > 0)? $va{'dc_totals_paid'}:0;
			$va{'dc_totals_paid'} = ($va{'dc_totals_paid'} > 0)? &format_price($va{'dc_totals_paid'}):'';
			
		}else{
			$va{'dc_pageslist'} = 1;
			if (int($in{'id_vendors'}) == 0) {
				$va{'dc_searchresults'} = qq|
					<tr>
						<td colspan='8' align="center">|.&trans_txt('bills_list_deposits_no_vendorid').qq|</td>
					</tr>\n|;
			}else {
				$va{'dc_searchresults'} = qq|
					<tr>
						<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}
		}

		## Vendor Info
		my ($sth) = &Do_SQL("SELECT CompanyName,POTerms,Category,Currency,BankName,BankBranch,BankAccount,BankWT FROM sl_vendors WHERE 1 AND ID_vendors = '$in{'id_vendors'}' ");
		($va{'vinfo_vendor'},$va{'vinfo_terms'},$va{'vinfo_category'},$va{'vinfo_currency'},$va{'vbinfo_name'},$va{'vbinfo_branch'},$va{'vbinfo_account'},$va{'vbinfo_clabe'}) = $sth->fetchrow_array();

	}else {		
		$va{'div_main'} = 'display:none;';
		$va{'messages'} = &trans_txt('bills_pays_noapply_verify_currency') if ($id_bills_nopaid ne '');
		$id_bills_paid=-77 if ($id_bills_paid eq '');
		$id_bills_nopaid=-77 if ($id_bills_nopaid eq '');

		################################################################################
		## Resumen de pagos aplicados		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills WHERE id_bills IN($id_bills_paid) ");
		$va{'summary_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'summary_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'summary_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'summary_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills WHERE id_bills IN($id_bills_paid)LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;
				my $amount_paided = $va{'bill_amount_remaining_'.$rec->{'ID_bills'}};

				$va{'summary_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($amount_paided).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$amount_paided.qq|">
					</td>
				</tr>\n|;

				$va{'summary_totals'} += $amount_paided;

			}
			$va{'summary_totals'} = &format_price($va{'summary_totals'});
			
		}else{
			$va{'summary_pageslist'} = 1;
			$va{'summary_searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		## Resumen de pagos no aplicados
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills WHERE id_bills IN($id_bills_nopaid) ");
		$va{'summaryfail_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'summaryfail_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'summaryfail_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'summaryfail_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills WHERE id_bills IN($id_bills_nopaid)LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;
				my $amount_not_paid = $va{'bill_amount_remaining_'.$rec->{'ID_bills'}};

				$va{'summaryfail_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($amount_not_paid).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$amount_not_paid.qq|">
					</td>
				</tr>\n|;

				$va{'summaryfail_totals'} += $amount_not_paid;

			}
			$va{'summaryfail_totals'} = &format_price($va{'summaryfail_totals'});
			
		}else{
			$va{'summaryfail_pageslist'} = 1;
			$va{'summaryfail_searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		my ($sth) = &Do_SQL("SELECT BankName,SubAccountOf,Currency, CURDATE() as mydate FROM sl_banks WHERE ID_banks = '$in{'id_banks'}'");
		($va{'summary_bankname'},$va{'summary_bankaccount'},$va{'summary_currency'},$va{'summary_date'}) = $sth->fetchrow_array();

		################################################################################
		$creddep_apply=-77 if ($creddep_apply eq '');
		$creddep_noapply=-77 if ($creddep_noapply eq '');
		$id_bills_applies=-77 if ($id_bills_applies eq '');

		## Resumen de Deposits/Credits aplicados		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE id_bills_applies IN($id_bills_applies) ");
		$va{'dc_summary_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'dc_summary_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'dc_summary_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'dc_summary_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills INNER JOIN sl_bills_applies USING(ID_bills) WHERE id_bills_applies IN($id_bills_applies) LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;

				$va{'dc_summary_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class="smalltext">$rec->{'Type'}</td>
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills_applied'}\">$rec->{'ID_bills_applied'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$rec->{'Amount'}.qq|">
					</td>
				</tr>\n|;

				$va{'dc_summary_totals'} += $rec->{'Amount'};

			}
			$va{'dc_summary_totals'} = &format_price($va{'dc_summary_totals'});
			
		}else{
			$va{'dc_summary_pageslist'} = 1;
			$va{'dc_summary_searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		## Resumen de Deposits/Credits no aplicados
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills WHERE id_bills IN($creddep_noapply) ");
		$va{'dc_summaryfail_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'dc_summaryfail_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'dc_summaryfail_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'dc_summaryfail_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills WHERE id_bills IN($creddep_noapply)LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;

				$va{'dc_summaryfail_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$rec->{'Amount'}.qq|">
					</td>
				</tr>\n|;

				$va{'dc_summaryfail_totals'} += $rec->{'Amount'};

			}
			$va{'dc_summaryfail_totals'} = &format_price($va{'dc_summaryfail_totals'});
			
		}else{
			$va{'dc_summaryfail_pageslist'} = 1;
			$va{'dc_summaryfail_searchresults'} = qq|
				<tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		
	}
	$va{'display_only_internationals'} = ($in{'currency'} ne $cfg{'acc_default_currency'})? '':'display:none;';
	$va{'display_only_internationals'} = 'display:none;' if (!$in{'id_vendors'});
	print "Content-type: text/html\n\n";
	print &build_page('mer_bills_payments.html');
	
}

#############################################################################
#############################################################################
#	Function: mer_bills_fileupload
#
#	Created on: 27/02/2013  17:32:10
#
#	Author: Enrique Peña
#
#	Modifications: 08/04/2013-Alejandro Diaz
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub mer_bills_fileupload {
#############################################################################
#############################################################################
	if ($in{'action'}) {
		$va{'div_process'} = '';
		$va{'div_main'} = 'display:none;';

	}else {
		$va{'div_process'} = 'display:none;';
		$va{'div_main'} = '';
	}

	print "Content-type: text/html\n\n";
	print &build_page('mer_bills_fileupload.html');
}

#############################################################################
#############################################################################
#	Function: mer_bills_dd_payments
#
#	Created on: 16/04/2013  11:32:10
#
#	Author: Alejandro Diaz
#
#	Modifications: 08/04/2013-Alejandro Diaz
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub mer_bills_dd_payments{
#############################################################################
#############################################################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($err,$hide,$legend);
	my $flag=1;
	my $id_debdep, $id_po_paid, $id_bills_paid, $id_bills_nopaid;
	my @arr_bills;
	my ($creddep_apply, $creddep_noapply, $id_bills_applies);
	$va{'totals'} = 0;
	$va{'totals_paid'} = 0;
	$va{'totals_unformatted'} = 0;
	$in{'currency'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"Currency") if ($in{'id_vendors'});
	$va{'summary_currency_exchange'} = $in{'currency_exchange'};

	if ($in{'process'}) {
		$va{'displayform1'} = 'display:none';
		$va{'displayform2'} = '';

		##########################################
		# Si se van a pagar depositos o debitos
		if ($in{'id_debdep'}) {
			$err=0;
			@arr_id_debdep = split /\|/, $in{'id_debdep'};
			$id_debdep='';
			$amount='';
			for my $i (0..$#arr_id_debdep) {
				$id_debdep .= $arr_id_debdep[$i].',';
			}
			chop($id_debdep);
			chop($amount);

			if (!$in{'id_banks'} or $in{'id_banks'} eq ""){
				$error{'id_banks'} = &trans_txt('required');
				++$err;
			}else{
				my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts FROM sl_banks INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE ID_banks = ". $in{'id_banks'} ." AND sl_banks.Status = 'Active' AND sl_accounts.Status = 'Active' LIMIT 1;");
				$ida_banks = $sth->fetchrow();

				if(!$ida_banks){
					$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
					++$err;	
				}

			}
			
			if (!$in{'bankdate'} or $in{'bankdate'} eq ""){
				$error{'bankdate'} = &trans_txt('required');
				++$err;
			}
			
			if ($cfg{'acc_default_currency'} ne $in{'currency'} and !$in{'currency_exchange'} or $in{'currency_exchange'} < 0) {
				$error{'currency_exchange'} = &trans_txt('required');
				++$err;
			}

			my $sql_add_refnum = "AND RefNum = '".&filter_values($in{'refnum'})."'";
			if ($in{'refnum'}) {
				$in{'refnumcustom'} = $in{'refnum'};
				delete($in{'refnum'})
			}

			if (!$err and !$in{'refnum_auto'} and !$in{'refnum'} and !$in{'refnumcustom'}) {
				$error{'refnum'} = &trans_txt('required');
				++$err;
			}

			# Se hace una validacion extra para saber si es requerible que escriba un RefNum
			if (!$err and $in{'refnum_auto'}) {
				#Se verifica que no existe un registro con la misma informacion
				# 1  validar que los bills no esten pagados
				# 2 validar que no existe un movrel para bills con estos ID
				my ($sth_refnum) = &Do_SQL("SELECT `RefNum` +1 FROM `sl_banks_movements` WHERE 1 AND Type='Credits' AND doc_type='$in{'doc_type'}' AND ID_banks='".&filter_values($in{'id_banks'})."' ORDER BY cast(`RefNum` as unsigned) DESC LIMIT 1;");
				my ($refnum_auto) = $sth_refnum->fetchrow_array();

				if (!$refnum_auto){
					# $error{'refnum'} = &trans_txt('required');
					# ++$err;

					$in{'refnum'} = 1;
				}else{
					$in{'refnum'} = $refnum_auto;
				}
				$sql_add_refnum = "AND RefNum = '".&filter_values($in{'refnum'})."'";
			}

			if (!$err) {
				$flag=0;

					$in{'currency_exchange'} = &filter_values($in{'currency_exchange'});
					$in{'currency_exchange'} =~ s/\,//g;

					#Se verifica que no existe un registro con la misma informacion
					# 1  validar que los bills no esten pagados
					# 2 validar que no existe un movrel para bills con estos ID
					my ($sth2) = &Do_SQL("SELECT COUNT(*) 
						FROM sl_banks_movements 
						WHERE 1 AND Type = 'Credits' 
						AND ID_banks = '".&filter_values($in{'id_banks'})."'
						AND BankDate = '".&filter_values($in{'bankdate'})."'
						AND doc_type = '".&filter_values($in{'doc_type'})."'
						$sql_add_refnum");
					my ($duplicate) = $sth2->fetchrow_array();
					
					if (!$duplicate) {
						for my $i (0..$#arr_id_debdep) {
							$arr_id_debdep[$i] = int($arr_id_debdep[$i]);
							if ($arr_id_debdep[$i] > 0) {

								my ($sth2) = &Do_SQL("SELECT 
									(SELECT COUNT(*) FROM sl_banks_movrel WHERE tablename = 'bills' AND tableid ='".$arr_id_debdep[$i]."')existinmovrel
									, (SELECT COUNT(*) FROM sl_bills WHERE Status = 'Paid' AND ID_bills ='".$arr_id_debdep[$i]."')alreadypaid
									/*, (SELECT COUNT(*) FROM sl_banks_movements WHERE 1 AND ID_banks = '".&filter_values($in{'id_banks'})."' AND TYPE = 'Debits' AND BankDate = '".&filter_values($in{'bankdate'})."' AND RefNum = '".&filter_values($in{'refnum'})."' AND Memo = '".&filter_values($in{'memo'})."' AND Amount = (SELECT IFNULL(Amount,0)Amount FROM sl_bills WHERE ID_bills='".$arr_id_debdep[$i]."'))duplicate*/
									, (SELECT COUNT(*) FROM sl_banks_movements WHERE 1 AND Type = 'Credits' AND ID_banks = '".&filter_values($in{'id_banks'})."' AND BankDate = '".&filter_values($in{'bankdate'})."' AND doc_type = '".&filter_values($in{'doc_type'})."' $sql_add_refnum)duplicate
									, (SELECT IFNULL(Amount,0)Amount FROM sl_bills WHERE ID_bills='".$arr_id_debdep[$i]."')Amount
									, (SELECT COUNT(*) FROM sl_bills WHERE ID_bills='".$arr_id_debdep[$i]."' AND Currency = ( SELECT Currency FROM sl_banks WHERE ID_banks = '".&filter_values($in{'id_banks'})."' ))Currency");
								my ($in_movrel, $already_paid, $duplicate, $amount_remaining, $is_valid_currency) = $sth2->fetchrow_array();
								
								$va{'bill_amount_remaining_'.$arr_id_debdep[$i]} = $amount_remaining;

								# validar la moneda contra la del cfg
								$is_valid_currency = 0;
								my $add_amountcurrency = " AmountCurrency = NULL, ";
								if ($cfg{'acc_default_currency'} eq $in{'currency'}){
									$is_valid_currency = 1;
								}elsif ($cfg{'acc_default_currency'} ne $in{'currency'} and $in{'currency_exchange'} and $in{'currency_exchange'} > 0) {
									$is_valid_currency = 1;
									$flag_calculate = 1;
									$amount_calculate = $amount_remaining * $in{'currency_exchange'};
									$add_amountcurrency = " AmountCurrency = '$amount_remaining', ";
								}

								# revisamos el currency, si no es igual no se procesa
								# si el amount_remaining > 0 
								
								if (!$is_valid_currency) {
									$id_bills_nopaid .= $arr_id_debdep[$i].',';
									# Log
									$in{'db'} = "sl_bills";
									&auth_logging('bills_nopaid_currency',$arr_id_debdep[$i]);

									$va{'messages_'.$arr_id_debdep[$i]} = &trans_txt('bills_check_currency');

								}elsif ($already_paid) {
									
									$va{'messages_'.$arr_id_debdep[$i]} = &trans_txt('bills_already_paid');

								}elsif ($amount_remaining <= 0 ) {
									
									$va{'messages_'.$arr_id_debdep[$i]} = &trans_txt('bills_amount_invalid');

								}else{

									my $add_amount = ($flag_calculate) ? $amount_calculate : $amount_remaining;
									my $id_banks_movements;
									my $sql_refnumcustom = ($in{'refnumcustom'})? " RefNumCustom = '".&filter_values($in{'refnumcustom'})."', ":" RefNumCustom =NULL, ";
									
									###
									### Se obtiene la cuenta de banco del proveedor
									###
									my $sth_bnk = &Do_SQL("SELECT sl_vendors.BankAccount FROM sl_vendors INNER JOIN sl_bills ON sl_vendors.ID_vendors = sl_bills.ID_vendors WHERE ID_bills = ".int($arr_id_debdep[$i]).";");
									my $bank_account = $sth_bnk->fetchrow();
									my $sql_bank_account = '';
									if( $bank_account ){
										$sql_bank_account = " RefBankAccount = '*".substr($bank_account, -5)."', ";
									}

									# Se genera un bank movement por cada bill que sea pagado								
									my ($sth) = &Do_SQL("INSERT INTO sl_banks_movements 
											SET ID_banks= '".&filter_values($in{'id_banks'})."',
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
												DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");

									$id_banks_movements = $sth->{'mysql_insertid'};
									
									if ($sth->rows() == 1) {
										$va{'bills_total_paid'} += $amount_remaining;

										# Log
										$in{'db'} = "sl_banks_movements";
										&auth_logging('fin_banks_movements_added', $id_banks_movements);

										# Se agregan ID Bills a movimientos de bancos
										my ($sth) = &Do_SQL("INSERT INTO sl_banks_movrel SET 
											ID_banks_movements = '$id_banks_movements', 
											tablename = 'bills', 
											tableid = '".$arr_id_debdep[$i]."', 
											AmountPaid = '".$amount_remaining."',
											DATE = CURDATE(), TIME = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
										my ($this_movrel) = $sth->{'mysql_insertid'};

										$id_banks_movrel .= $this_movrel . ',';

										my ($sth2) = &Do_SQL("UPDATE sl_bills SET Status = 'Paid' WHERE ID_bills = '".$arr_id_debdep[$i]."' LIMIT 1;");

										########################################################
										########################################################
										## Movimientos de contabilidad
										########################################################
										########################################################
										my $id_vendors = &load_name('sl_bills','ID_bills', $arr_id_debdep[$i], 'ID_vendors');
										my $vendor_category = &load_name('sl_vendors','ID_vendors', $id_vendors,'Category');
										my $bill_type = &load_name('sl_bills','ID_bills', $arr_id_debdep[$i], 'Type');
										$in{'currency_exchange'} = 0 if !$in{'currency_exchange'};
										my @params = ($id_vendors,$arr_id_debdep[$i],$ida_banks,$in{'bankdate'},$amount_remaining,$in{'currency_exchange'});
										#&cgierr('vendor_' . lc($bill_type) . '_' . lc($vendor_category) . " $id_vendors,$ida_banks,$amount_remaining,$in{'currency_exchange'} ");
										&accounting_keypoints('vendor_' . lc($bill_type) . '_' . lc($vendor_category), \@params );

					
										# Log
										$in{'db'} = "sl_bills";
										&auth_logging('bills_paid',$arr_id_debdep[$i]);

										$id_bills_paid .= $arr_id_debdep[$i].',';

									}else {
										$id_bills_nopaid .= $arr_id_debdep[$i].',';
									}
								}
							}else {
								$va{'err_amount'.$arr_id_debdep[$i]} = &trans_txt('bills_required');
							}
						}

						chop($id_bills_paid) if($id_bills_paid ne '');
						chop($id_bills_nopaid) if($id_bills_nopaid ne '');
						chop($id_banks_movrel) if($id_banks_movrel ne '');

					}else {
					 	## Enviar mensaje de error, no se puede procesar algo que ya fue procesado
					 	$va{'messages'} = &trans_txt('bills_notprocess');
					 	delete($in{'process'});
					}

			}else {
				$flag=1;
				$va{'messages'} = &trans_txt('reqfields_short');
				delete($in{'process'});
			}
		}else {
			
			$flag=1;
			$va{'messages'} = &trans_txt('bills_required');
			delete($in{'process'});
		}

	}

	if($flag and !$in{'process'}) {
		$va{'div_summary'} = 'display:none;';
		$va{'displayform1'} = '';
		$va{'displayform2'} = 'display:none';
		my ($query);
		
		if($in{'id_vendors'}){
			$query .= " AND ID_vendors = $in{'id_vendors'}";
			$in{'doc_type'} = &load_name("sl_vendors","ID_vendors",$in{'id_vendors'},"PaymentMethod") if (!$in{'doc_type'});
		}
		if($in{'id_bills'} ){
			$query .= " AND ID_bills = $in{'id_bills'}";
		}
		
		if($in{'duedate'}){
			$query .= " AND DueDate >= '$in{'duedate'}'";
			if($in{'toduedate'}){
				$query .= " AND DueDate <= '$in{'toduedate'}'";
			}
		}

		if($in{'from_amount'}){
			$query .= " AND Amount >= '$in{'from_amount'}'";
		}

		if($in{'to_amount'}){
			$query .= " AND Amount <= '$in{'to_amount'}'";
		}
		
		if($in{'id_debdep'}) {
			@arr_bills = $in{'id_debdep'};
			if ($in{'id_debdep'} =~ m/\|/) {
				 @arr_bills = split /\|/, $in{'id_debdep'};
			}
		}

		## list Deposits/Debits to be paid
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills 
		WHERE sl_bills.Status ='Processed' 
		AND Type IN ('Deposit','Debit') 
		AND Amount > 0 
		AND (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills)) > 0 
		AND ID_vendors = '$in{'id_vendors'}' ");
		$va{'dd_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		if ($va{'dd_matches'}>0 and int($in{'id_vendors'}>0)){
			$va{'displayform1'} = 'display:none';
			$va{'displayform2'} = '';

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'dd_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'dd_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT *, (Amount - (
				SELECT IFNULL(SUM(Amount),0)as Amount 
				FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills))as AmountAvailable 
			FROM  sl_bills 
			WHERE sl_bills.Status ='Processed' 
			AND Type IN ('Deposit','Debit','Credit') 
			AND Amount>0 
			AND (Amount - (SELECT IFNULL(SUM(Amount),0)as Amount FROM sl_bills_applies WHERE ID_bills = sl_bills.ID_bills)) > 0 AND ID_vendors = '$in{'id_vendors'}'
			 ORDER BY Type, DueDate LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$va{'forvendor'} = qq|for Vendor: <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a>|;
				$d = 1 - $d;

				# rutina para remarcar checkbox seleccionados
				my $checked = '';
				my $temp_id_bill = $rec->{'ID_bills'};
				if(@arr_bills and grep $_ eq $temp_id_bill, @arr_bills) {
					$checked = ' checked="checked" ';
					$va{'dd_totals_paid'} += $rec->{'AmountAvailable'};
				}

				$va{'dd_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<input type='checkbox' name='id_debdep' class='id_debdep' value='$rec->{'ID_bills'}' $checked>
						<!--input type='hidden' name='id_creddep' class='id_creddep' value='$rec->{'ID_bills'}' $checked-->
						&nbsp;
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext">$rec->{'Type'}</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'Amount'}).qq|</td>
					<td class="smalltext" align="right">|.&format_price($rec->{'AmountAvailable'}).qq|
						<input type="hidden" name="dd_amount_wo_format" id="dd_amount_unformatted_$rec->{'ID_bills'}" value="|.$rec->{'AmountAvailable'}.qq|">
					</td>
				</tr>\n|;

				$va{'dd_totals'} += $rec->{'AmountAvailable'};

			}
			$va{'dd_totals_unformatted'} = $va{'dd_totals'};
			$va{'dd_totals'} = &format_price($va{'dd_totals'});
			$va{'dd_totals_paid_unformatted'} = ($va{'dd_totals_paid'} > 0)? $va{'dd_totals_paid'}:0;
			$va{'dd_totals_paid'} = ($va{'dd_totals_paid'} > 0)? &format_price($va{'dd_totals_paid'}):'';
			
		}else{
			$va{'dd_pageslist'} = 1;
			if (int($in{'id_vendors'}) == 0) {
				$va{'dd_searchresults'} = qq|
					<tr>
						<td colspan='8' align="center">|.&trans_txt('bills_list_deposits_no_vendorid').qq|</td>
					</tr>\n|;
			}else {
				$va{'displayform1'} = 'display:none';
				$va{'displayform2'} = '';
				$va{'dd_searchresults'} = qq|
					<tr>
						<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
					</tr>\n|;
			}
		}
		
		## Vendor Info
		my ($sth) = &Do_SQL("SELECT CompanyName,POTerms,Category,Currency,BankName,BankBranch,BankAccount,BankWT FROM sl_vendors WHERE 1 AND ID_vendors = '$in{'id_vendors'}' ");
		($va{'vinfo_vendor'},$va{'vinfo_terms'},$va{'vinfo_category'},$va{'vinfo_currency'},$va{'vbinfo_name'},$va{'vbinfo_branch'},$va{'vbinfo_account'},$va{'vbinfo_clabe'}) = $sth->fetchrow_array();

		$va{'button_p'} = qq| <p align="center"><input type="submit" class="button" value="Pay" id="btn_pay" style="display:"></p> |;


	}else {		
		$va{'div_main'} = 'display:none;';
		$va{'messages'} = &trans_txt('bills_pays_noapply_verify_currency') if ($id_bills_nopaid ne '');
		$id_bills_paid=-77 if ($id_bills_paid eq '');
		$id_bills_nopaid=-77 if ($id_bills_nopaid eq '');

		################################################################################
		## Resumen de Deposits/Dedits pagados
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills WHERE id_bills IN($id_bills_paid) ");
		$va{'summary_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'summary_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'summary_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'summary_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills WHERE id_bills IN($id_bills_paid)LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;
				my $amount_paided = $va{'bill_amount_remaining_'.$rec->{'ID_bills'}};

				$va{'summary_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($amount_paided).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$amount_paided.qq|">
					</td>
				</tr>\n|;

				$va{'summary_totals'} += $amount_paided;

			}
			$va{'summary_totals'} = &format_price($va{'summary_totals'});
			
		}else{
			$va{'summary_pageslist'} = 1;
			$va{'summary_searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		################################################################################
		## Resumen de Deposits/Credits no pagados
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM  sl_bills WHERE id_bills IN($id_bills_nopaid) ");
		$va{'summaryfail_matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});

		if ($va{'summaryfail_matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'summaryfail_pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'summaryfail_matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM  sl_bills WHERE id_bills IN($id_bills_nopaid)LIMIT $first,$usr{'pref_maxh'}; ");
			while ($rec = $sth->fetchrow_hashref){
				$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
				$d = 1 - $d;
				my $amount_not_paid = $va{'bill_amount_remaining_'.$rec->{'ID_bills'}};

				$va{'summaryfail_searchresults'} .= qq|
				<tr bgcolor='$c[$d]' >
					<td class='smalltext'>
						<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a>
					</td>
					<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>				
					<td class="smalltext">$rec->{'DueDate'}</td>
					<td class="smalltext">$rec->{'Currency'}</td>
					<td class="smalltext" align="right">|.&format_price($amount_not_paid).qq|
						<input type="hidden" name="amount_wo_format" id="amount_unformatted_$rec->{'ID_bills'}" value="|.$amount_not_paid.qq|">
					</td>
				</tr>\n|;

				$va{'summaryfail_totals'} += $amount_not_paid;

			}
			$va{'summaryfail_totals'} = &format_price($va{'summaryfail_totals'});
			
		}else{
			$va{'summaryfail_pageslist'} = 1;
			$va{'summaryfail_searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}

		my ($sth) = &Do_SQL("SELECT BankName,SubAccountOf,Currency, CURDATE() as mydate FROM sl_banks WHERE ID_banks = '$in{'id_banks'}'");
		($va{'summary_bankname'},$va{'summary_bankaccount'},$va{'summary_currency'},$va{'summary_date'}) = $sth->fetchrow_array();
		
	}
	$va{'display_only_internationals'} = ($in{'currency'} ne $cfg{'acc_default_currency'})? '':'display:none;';
	$va{'display_only_internationals'} = 'display:none;' if (!$in{'id_vendors'});

	print "Content-type: text/html\n\n";
	print &build_page('mer_bills_dd_payments.html');
	
}

#############################################################################
#############################################################################
#   Function: js_clear_form
#
#       Es: Autorizacion Masiva de Ordenes de Compra
#       En: Mass released purchase orders
#
#
#    Created on: 2013-05-21
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub mer_po_released{
#############################################################################
#############################################################################

	$va{'display_po_filter'} = '';
	$va{'display_po_process'} = 'display:none;';
	
	if ($in{'action'}){
		$va{'display_po_filter'} = 'display:none;';
		$va{'display_po_process'} = '';

		##Autorizar todas las ordenes
		my @poidval = split /\|/, $in{'po_id'};
		my $auth_type = '';
		my $auth_note = '';
		my $status = ", Status='In Process'";
		if ($in{'auth_type'} eq 'approve') {
			$auth_type = 'Approved';
			$auth_note = 'Authorized by set';
			
		} elsif ($in{'auth_type'} eq 'decline') {
			$auth_type = 'Declined';
			$auth_note = 'Declined by set';
			$status = '';
		}
		
		for my $i (0..$#poidval) {
			if ($poidval[$i] > 0 and $auth_type ne '') {
				
				my ($sth) = &Do_SQL("UPDATE sl_purchaseorders
									 SET AuthBy='".$usr{'id_admin_users'}."', Auth='$auth_type' $status
									 WHERE ID_purchaseorders = '$poidval[$i]';");
				
				my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_auth
									SET id_purchaseorders='$in{'id_purchaseorders'}',
									Notes='$auth_note',
									Type='$auth_type',Date=CURDATE(),
									Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				
				$in{'db'} = "sl_purchaseorders";
				&auth_logging('mer_purchaseorder_auth_noteadded',$poidval[$i]);
				
				$in{'authby'} = $usr{'id_admin_users'};
				&auth_logging('mer_purchaseorder_auth_final',$poidval[$i]);
				
			}
		}
	}

	if ($in{'search'}){
		$va{'display_po_filter'} = 'display:none;';
		$va{'display_po_process'} = '';

		my $add_filters;
		$add_filters = ($in{'from_date'})?" AND PODate >= '$in{'from_date'}'":"";
		$add_filters .= ($in{'to_date'})?" AND PODate <='$in{'to_date'}'":"";

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE Auth='In Process' AND Status IN('New','In Process') AND Type='Purchase Order' $add_filters;");
		if ($sth->fetchrow>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders WHERE Auth='In Process' AND Status IN('New','In Process') AND Type='Purchase Order' $add_filters;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;

				my ($sth2) = &Do_SQL("SELECT ifnull(sum(((Qty * Price)+Tax)),0) AS total_po FROM sl_purchaseorders_items wHERE ID_purchaseorders = '$rec->{'ID_purchaseorders'}';");
				$total_po = $sth2->fetchrow_array();

				my $currency = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'[Currency]');
				my $companyname = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'[CompanyName]');
				$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'polist'} .= "   <td class='smalltext'><input type='checkbox' name='po_id' class='po_checkbox' value='".$rec->{'ID_purchaseorders'}."'></td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='left'>".$rec->{'ID_purchaseorders'}."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='left'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}'>".$companyname."</a></td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='center'>".$rec->{'PODate'}."</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>".$rec->{'Type'}."</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>".$rec->{'Status'}."</td>\n";
				$va{'polist'} .= "   <td class='smalltext'>".$currency."</td>\n";
				$va{'polist'} .= "   <td class='smalltext' align='right'> ".&format_price($total_po)."</td>\n";
				$va{'polist'} .= "</tr>\n";

				$tot_po += $rec->{'Total'};
				$tax_po += $rec->{'Tax'};
				$subtot_po += ($rec->{'Price'}*$rec->{'Qty'});
			}
		}

	}

	

	print "Content-type: text/html\n\n";
	print &build_page('mer_po_released.html');
}


#############################################################################
#############################################################################
#   Function: mer_bills_accounting
#
#       Es: Genera un reporte para mostrar los Bills y si es que tienen contabilidad o no
#       En: 
#
#
#    Created on: 2013-06-23
#
#    Author: _RB_
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub mer_bills_accounting{
#############################################################################
#############################################################################


	if($in{'action'}) {


		my ($query);

		## Filter by Date
		if ($in{'from_date'}){
			$query .= " AND tmp.Date >= '$in{'from_date'}' ";
		}
		
		$in{'to_date'}	= &get_sql_date() if !$in{'to_date'};
		if ($in{'to_date'}){
			$query .= " AND tmp.Date <= '$in{'to_date'}' ";
		}
		
		## Filter by Type
		if ($in{'type'}){
			$in{'type'} =~ s/\|/','/g;
			$query .= " AND tmp.Type IN('$in{'type'}') ";
		}$in{'status'} =~ s/','/\|/g;

		## Filter by Status
		if ($in{'status'}){
			$in{'status'} =~ s/\|/','/g;
			$query .= " AND tmp.Status IN('$in{'status'}') ";
		}$in{'status'} =~ s/','/\|/g;

		my $ida_vendors = '197,198,201,202';


		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills tmp WHERE 1 $query;");
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0) {

			$usr{'pref_maxh'} = 50;
			($va{'pageslist'},$va{'qs'}) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my $to_limit = !$in{'export'} ? "LIMIT $first,$usr{'pref_maxh'}" : '';

			my ($query_f) = "SELECT ID_bills,tmp.Type,tmp.Date,ID_vendors,CompanyName,
					Memo,Currency,currency_exchange,tmp.Status,tmp.Amount, tmp.SubType,Deductible,
					IF(COUNT(*) IS NULL,0,COUNT(*)) AS QtyMovs,
					IF(SUM(IF(tableused = 'sl_bills',sl_movements.Amount,0)) IS NULL,0,SUM(IF(tableused = 'sl_bills',sl_movements.Amount,0))) AS AmtMovs,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit',1,0))AS QtyDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit',sl_movements.Amount,0))AS AmtDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit',1,0))AS QtyCredits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit',sl_movements.Amount,0))AS AmtCredits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Debit' AND ID_accounts IN($ida_vendors),1,0))AS VendorDebits,
					SUM(IF(tableused = 'sl_bills' AND Credebit = 'Credit' AND ID_accounts IN($ida_vendors),1,0))AS VendorCredits,
					SUM(IF(tableused = 'sl_bills' AND sl_movements.Amount < 0,1,0)) AS NegMovs
					FROM
					(
						SELECT 
						sl_bills.ID_bills,sl_bills.Type,sl_bills.Date,
						sl_vendors.ID_vendors,CompanyName,Memo,sl_bills.Currency,
						sl_bills.currency_exchange,sl_bills.Status,
						ROUND(IF(
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)),
							IF(
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)), 
								sl_bills.Amount * IF(currency_exchange > 0,currency_exchange,1)
							)
						),2)AS Amount,
						IF(
							SUM(sl_bills_expenses.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
							'Expenses',
							IF(
								SUM(sl_bills_pos.Amount * IF(currency_exchange > 0,currency_exchange,1)) > 0,
								'PO', 
								'Bill'
							)
						)AS SubType,
						Deductible
						FROM sl_bills 
						LEFT JOIN sl_bills_expenses USING(ID_bills)
						LEFT JOIN sl_bills_pos USING(ID_bills)
						INNER JOIN sl_vendors USING(ID_vendors)
						WHERE 1 
						/*AND sl_bills.Type = 'Bill'
						AND sl_bills.ID_bills = '1419'*/
						GROUP BY sl_bills.ID_bills
						ORDER BY sl_bills.ID_bills
					)tmp
					LEFT JOIN sl_movements ON ID_bills = ID_tableused
					WHERE 1 $query 
					GROUP BY ID_bills
					ORDER BY ID_bills $to_limit;";

			my ($sth) = &Do_SQL($query_f);

			if($in{'export'}) {

				my $cname = lc($cfg{'company_name'});
				$cname =~ s/\s/_/g;
				my $fname =  $cname. '_bills_accounting_' . &get_date();
				chop($fname);

				print "Content-type: application/octet-stream\n";
				print "Content-disposition: attachment; filename=$fname.csv\n\n";
				print "Vendor ID,Company Name,ID,Type,Memo,Bill Date,Status,Billed Amount,Total Movements,Total Debits,Total Credits,Vendor Credit,Vendor Debit,Neg. Movs\n";

			}
			
			while (my ($id_bills, $type, $date, $id_vendors, $company, $memo, $currency, $currency_exchange, $status, $amount, $subtype, $deductible, $qty_movs, $amt_movs, $qty_debits, $amt_debits, $qty_credits, $amt_credits, $vendors_debits_qty, $vendors_credits_qty, $neg_movs) = $sth->fetchrow() ) {
			
				my $vendor_deposits = 0;my $ok = 'OK';my $ok_pr = 'OK';my $ok_pa = 'OK';my $ok_mo = 'OK';	
				my $this_style = abs($amt_debits - $amt_credits) > 0 ? 'style="color:red"' : '';
				($this_style ne '' and $in{'export'}) and ($ok = 'Error');

				
				if($type eq 'Deposit' and $in{'status'} =~ /Paid/){

					#########
					######### Proceso de Busqueda para Deposits
					#########

					my ($sth) = &Do_SQL("SELECT sl_banks_movrel.Date FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements)  WHERE tableid = '$id_bills' AND tablename = 'bills';");
					my ($pdate) = $sth->fetchrow();

					if($pdate) {

						my ($sth) = &Do_SQL("SELECT ID_movements, Reference FROM sl_movements WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND EffDate = '$pdate' AND Credebit = 'Credit' AND (Reference IS NULL OR Reference = '' OR Reference = 'Deposit: $id_bills') AND ABS(Amount - $amount) BETWEEN 0 AND 0.009 LIMIT 1;");
						my ($id_movements, $reference) = $sth->fetchrow();
						($id_movements) and ($vendors_deposits = 1);

					}

				}elsif($type eq 'Bill' and $subtype eq 'PO'){
					
					#########
					######### Proceso de Busqueda POs
					#########
					my $po_error1 = 0;my $po_error2 = 0;
					my ($sth) = &Do_SQL("SELECT ID_purchaseorders FROM sl_bills_pos WHERE ID_bills = '$id_bills' AND Amount > 0;");
					PO: while (my($id_po) = $sth->fetchrow()) {

						my ($sth) = &Do_SQL("SELECT
											SUM(IF(Amount > 0,Amount,0)) AS AmtMovs,
											SUM(IF(Credebit = 'Debit',Amount,0))AS AmtDebits, 
											SUM(IF(Credebit = 'Credit',Amount,0))AS AmtCredits, 
											SUM(IF(Credebit = 'Debit' AND ID_accounts IN($ida_vendors),1,0))AS VendorDebits,
											SUM(IF(Credebit = 'Credit' AND ID_accounts IN($ida_vendors),1,0))AS VendorCredits
											FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders';");
						my ($amt,$debs,$creds,$vdeb,$vcred) = $sth->fetchrow();			
						(!$vcred and $status =~ /Processed|Paid/) and ($po_error1 = 1);
						(!$vdeb and $status eq 'Paid') and ($po_error2 = 1);
						$amt_movs += $amt; $amt_debits += $debs; $amt_credits += $creds;
						
					}
					$vendors_credits_qty = $po_error1 ? 0 : 1;
					$vendors_debits_qty = $po_error2 ? 0 : 1;
					#&cgierr("$id_bills, $amt_movs, $amt_debits, $amt_credits, $vendors_credits_qty, $vendors_debits_qty");

				}

				($status =~ /Processed|Paid/ and $type !~ /Deposit|Credit/ and  !$vendors_credits_qty) and ($ok = 'Error') and ($ok_pr = 'Error');
				($status eq 'Paid' and $type eq 'Deposit' and !$vendors_deposits)  and ($ok = 'Error') and ($ok_pa = 'Error');
				($status eq 'Paid' and $type !~ /Deposit|Credit/ and !$vendors_debits_qty )  and ($ok = 'Error') and ($ok_pa = 'Error');
				($neg_movs) and ($ok = 'Error') and ($ok_mo = 'Error');


				if(!$in{'export'}) {
					
					$d = 1 - $d;
					$va{'searchresults'} .= qq|<tr bgcolor="$c[$d]">\n
													<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$id_bills" title="">$id_bills</a></td>\n
													<td>$type</td>\n
													<td>$date</td>\n
													<td>$status</td>\n
													<td>$company (<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$id_vendors" title="">$id_vendors</a>)<br>$memo</td>\n
													<td align="right">|. &format_price($amount) .qq|</td>\n
													<td align="right">|. &format_price($amt_movs) .qq|</td>\n
													<td align="right">|. &format_price($amt_debits) .qq|</td>\n
													<td align="right">|. &format_price($amt_credits) .qq|</td>\n
													<td>$ok</td>\n
												</tr>\n|;
				}else{				
					print "\"$id_vendors\",\"$company\",\"$id_bills\",\"$type\",\"$memo\",\"$date\",\"$status\",\"$amount\",\"$amt_movs\",\"$amt_debits\",\"$amt_credits\",\"$ok_pr\",\"$ok_pa\",\"$ok_mo\"\n";
				}

			}
			if($in{'export'}) { return; }
			
		}else{
			$va{'matches'} = 0;
			$va{'pageslist'} = 1;
			$va{'searchresults'} =qq|<tr>
										<td colspan='10' align="center">|.&trans_txt('search_nomatches').qq|</td>
									</tr>\n|;
		}

	}

	print "Content-type: text/html\n\n";
	if(!$in{'action'}) { print &build_page('mer_bills_accounting.html') } else { print &build_page('mer_bills_accounting_list.html'); }


}

#################################################################
#     MERCHANDISING : SUPPLIERS CONTACT   	#
##################################################################



sub mer_addparts {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modification: JRG 01/15/2009: Se aÂ¤ade la busqueda por ID_parts
#
	my ($query,$bloked);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_products='$in{'id_sku_products'}';");
	($bloked=1) if ($sth->fetchrow() > 0);

		
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products='$in{'id_sku_products'}';");
	($bloked=1) if ($sth->fetchrow() > 0);

	if ($bloked){
		print "Content-type: text/html\n\n";
		print &build_page('mer_addparts_bloked.html');
		return;
	}else{
		if($in{'title'}){ #RB Start - Adding Keyword - apr2808
		$query = " AND (ID_parts='$in{'title'}' OR Model LIKE '%$in{'title'}%' OR Name LIKE '%$in{'title'}%') ";
		}#RB End
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts WHERE Status='Active' $query;");
		$va{'matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		if ($va{'matches'}>0){
			$id_products = substr($in{'id_sku_products'},3,6);
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			
			my ($sth) = &Do_SQL("SELECT * FROM sl_parts WHERE Status='Active' $query LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=mer_products&view=$id_products&addparts=$in{'id_sku_products'}&id_parts=$rec->{'ID_parts'}&tab=3#tabs')">
					<td class="smalltext">$rec->{'ID_parts'}</td>
					<td class="smalltext">$rec->{'Model'}</td>
					<td class="smalltext">$rec->{'Name'}</td>
				</tr>\n|;
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('mer_addparts.html');
}

sub mer_addpromo {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modification: JRG 01/15/2009: Se aÂ¤ade la busqueda por ID_parts
#
	my ($query,$bloked);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_products='$in{'id_sku_products'}' OR Related_ID_products='$in{'id_products'}';");
	($blocked=1) if ($sth->fetchrow() > 0);

		
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products='$in{'id_sku_products'}';");
	($blocked=1) if ($sth->fetchrow() > 0);

	if ($blocked){
		print "Content-type: text/html\n\n";
		print &build_page('mer_addparts_bloked.html');
		return;
	}else{
		if($in{'title'}){ #RB Start - Adding Keyword - apr2808
		$query = " AND (ID_products='$in{'title'}' OR Model LIKE '%$in{'title'}%' OR Name LIKE '%$in{'title'}%') ";
		}#RB End
		my ($sth) = ($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1)? &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status IN ('Active','On-Air','Pauta Seca') $query;") : &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status IN ('Active','On-Air') $query;");
		
		$va{'matches'} = $sth->fetchrow();
		my (@c) = split(/,/,$cfg{'srcolors'});
		if ($va{'matches'}>0){
			$id_products = substr($in{'id_sku_products'},3,6);
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			
			my ($sth) = ($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1)? &Do_SQL("SELECT * FROM sl_products WHERE Status IN ('Active','On-Air','Pauta Seca') $query LIMIT $first,$usr{'pref_maxh'};") : &Do_SQL("SELECT * FROM sl_products WHERE Status IN ('Active','On-Air') $query LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=mer_products&view=$in{'id_products'}&addpromo=$rec->{'ID_products'}&convert_to_promo=1&tab=3&[va_rndnumber]#tabs')">
					<td class="smalltext">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
					<td class="smalltext">$rec->{'Model'}</td>
					<td class="smalltext">$rec->{'Name'}</td>
					<td class="smalltext">$rec->{'Status'}</td>
				</tr>\n|;
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('mer_addpromo.html');
}

sub mer_change_topay{
#-----------------------------------------
# Created on: 25/06/14  11:39:15 By  Arturo Hernandez
# Forms Involved: 
# Description : Screen Change to Pay
# Parameters : 
	use JSON;
	use CGI;
	use Data::Dumper qw(Dumper);

	if($in{'action'}){
		if(!&check_permissions('change_status_topay','','')){
				$va{'message'} = "<span class='stdtxterr'>".&trans_txt('page_unauth')."</span>"; 
			}else{
			$va{'display'} = 'display:none;';
			$va{'loading'} = 'display:none;';
			$va{'searchresultapply'} .= 'Bills Changed To Pay: <br>';
			$q = new CGI;
			my @matriz = $q->param();
			for my $key (@matriz){
				$i++;
				$value{$key} = $q->param($key);
				if($key =~ /_/){
					my @name_field = split("_", $key);
					my ($id_bill) =  $name_field[1];
					my ($sthcount) = &Do_SQL("SELECT COUNT(*) FROM sl_bills
					WHERE Status IN('Processed', 'Partly Paid')
					AND ID_bills = '$id_bill'");
					if($sthcount->fetchrow == 1){
						my ($sth) = &Do_SQL("UPDATE sl_bills 
						SET Status = 'To Pay'
						WHERE ID_bills = '$id_bill'");
						$va{'searchresultapply'} .= '<tr><td><a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_bills&view='.$id_bill.'">'.$id_bill.'</a></td></tr>';
					}
				}
				
				
			}
		}
	}else{
		$va{'loading'} = 'display:none;';
		$va{'display2'} = 'display:none;';
		my ($sth) = &Do_SQL("SELECT COUNT(*) 
			FROM  sl_bills as bills
			WHERE bills.Status IN('Processed', 'Partly Paid')
			
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
				my ($sth) = &Do_SQL("SELECT bills.ID_vendors
				FROM  sl_bills as bills
				INNER JOIN sl_vendors ON
				sl_vendors.ID_vendors = bills.ID_vendors
				WHERE bills.Status IN('Processed', 'Partly Paid')
				
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
				$query GROUP by bills.ID_vendors ORDER BY sl_vendors.CompanyName, DueDate ");
				$select_creddep = '';
				my @totalAmount;
				my @vendorList;
				my @json ;
				while($rec = $sth->fetchrow_hashref) {
					$i++;
					$vendors = &load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},'([ID_vendors]) [CompanyName]');
					$select_creddep .= qq|<option value="|.$rec->{'ID_bills'}.qq|">|.$rec->{'ID_bills'}.qq|</option>|;
					$d = 1 - $d;
					if(!&in_array(\@vendorList, $rec->{'ID_vendors'})){
						push(@vendorList, $rec->{'ID_vendors'});
						$va{'searchresults'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td><img id="link_$rec->{'ID_vendors'}" class="collapse" style="cursor:pointer;" src="/sitimages/icon-collapse-plus.gif"  /> <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}\">$vendors</a></td>
							<td id="amountTotal_$rec->{'ID_vendors'}" align="right"></td>
							<td id="amountDueTotal_$rec->{'ID_vendors'}" align="right"></td>
							
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
						WHERE bills.Status IN('Processed', 'Partly Paid')
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
						$query ORDER BY ID_bills ASC");
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
							<td class="menu_bar_title">Status</td>
							<td class="menu_bar_title" align="right">Amount</td>
							<td class="menu_bar_title" align="right">Amount Due</td>
							<td class="menu_bar_title">&nbsp;</td>|;
						while($rec = $sth->fetchrow_hashref){
						$a = 1 - $a;
							$va{'searchresults'} .= qq|
							<tr bgcolor='$c[$a]'>
							<td><input type="checkbox" class="checkbill checkbill_$idVendor check_$idVendor" id="check_$rec->{ID_bills}" name="bill_$rec->{'ID_bills'}_$idVendor" /></td>
							<td ><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{ID_bills}</a></td>
							<td >$rec->{DueDate}</td>
							<td >$rec->{Currency}</td>
							<td >$rec->{Type}</td>
							<td >$rec->{Status}</td>
							<td align="right">|.&format_price($rec->{Amount}).qq|</td>
							<td align="right"><span style="color:#ff0f0f;cursor:pointer;" onclick="print_amount('value_$rec->{ID_bills}', $rec->{AmountAvailable})">|.&format_price($rec->{AmountAvailable}).qq|</span><input type="hidden" id="valueAmountDue_$rec->{ID_bills}" value="$rec->{AmountAvailable}" class="classAmountDue_$idVendor a" /> </td>
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
			$va{'button_p'} = qq| <p align="center"><input type="submit" class="button" value="Change To Pay" id="btn_pay" style="display:"></p> |;
	}
	print "Content-type: text/html\n\n";
	print &build_page('mer_change_topay.html');
}

#############################################################################
#############################################################################
#   Function: mer_bills_accounting
#
#       Es: Genera un reporte para mostrar los Bills y si es que tienen contabilidad o no
#       En: 
#
#
#    Created on: 2014-09-11
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub mer_bills_print_journal_vaucher{
#############################################################################
#############################################################################
	
	print "Content-type: text/html\n\n";
	print &build_page('mer_bills_journal_vaucher.html');
}

sub in_array
 {
     my ($arr,$search_for) = @_;
     my %items = map {$_ => 1} @$arr;
     return (exists($items{$search_for}))?1:0;
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

1;