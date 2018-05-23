
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
	print &build_page('reports_products.html');
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


#################################################################
#  MERCHANDISE : SETUP   #
#################################################################
sub mer_setup {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";
	print &build_page('mer_setup.html');	
}

##################################################################
#     MERCHANDISING : VENTYPE    	#
##################################################################
sub mer_setup_ventype {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_type'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET Type='".&filter_values($in{$key})."' WHERE Type='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_type_upd');
		$cfg{'vendor_type'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_type_upd','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_type'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Type='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_ventype&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}		
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_ventype.html');
}


##################################################################
#     MERCHANDISING : VENPOPT    	#
##################################################################
sub mer_setup_venpopt {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_popt'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET PaymentTerms='".&filter_values($in{$key})."' WHERE PaymentTerms='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_popt_upd');
		$cfg{'vendor_popt'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_popt_upd','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_popt'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE PaymentTerms='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_venpopt&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_venpopt.html');
	
}

##################################################################
#     MERCHANDISING : VEN SHIPPING    	#
##################################################################
sub mer_setup_venshp {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_shpopt'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET ShippingOptions='".&filter_values($in{$key})."' WHERE ShippingOptions='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_shpopt_upd');
		$cfg{'vendor_shpopt'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_shpopt_upd','');
		$in{'field_new'} = '';
		
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_shpopt'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE ShippingOptions='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_venshp&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_venshp.html');
	
}

##################################################################
#     MERCHANDISING : VEN INVENTORY    	#
##################################################################
sub mer_setup_veninv {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_inventory'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET InventoryStatus='".&filter_values($in{$key})."' WHERE InventoryStatus='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_veninv_upd');
		$cfg{'vendor_inventory'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_type_upd','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_inventory'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE InventoryStatus='$ary[$i]';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_ventype&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_veninv.html');
	
}


##################################################################
#     MERCHANDISING : VENRET    	#
##################################################################
sub mer_setup_venret {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_rpolicy'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET ReturnPolicy='".&filter_values($in{$key})."' WHERE ReturnPolicy='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_venret');
		$cfg{'vendor_rpolicy'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_venret','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_rpolicy'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE ReturnPolicy='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_venret&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_venret.html');
}

##################################################################
#     MERCHANDISING : VENDISC    	#
##################################################################
sub mer_setup_vendisc {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_disc'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET Discounts='".&filter_values($in{$key})."' WHERE Discounts='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_disc');
		$cfg{'vendor_disc'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_disc','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_disc'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE Discounts='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_vendisc&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_vendisc.html');
}

##################################################################
#     MERCHANDISING : VENDED    	#
##################################################################
sub mer_setup_vended {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_dedair'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET AirProgram='".&filter_values($in{$key})."' WHERE AirProgram='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_dair');
		$cfg{'vendor_dedair'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_dair','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_dedair'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE AirProgram='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_vended&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_vended.html');
}

##################################################################
#     MERCHANDISING : VENSPP    	#
##################################################################
sub mer_setup_venspp {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_sprogs'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET SpecialProgram='".&filter_values($in{$key})."' WHERE SpecialProgram='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_sprog');
		$cfg{'vendor_sprogs'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_sprog','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_sprogs'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" value="$ary[$i]" size="60" style="width:100%" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE SpecialProgram='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_venspp&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_venspp.html');
	
}

##################################################################
#     MERCHANDISING : VEN FORM    	#
##################################################################
sub mer_setup_venmform {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'vendor_mformat'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_vendors SET MerchandiseFormat='".&filter_values($in{$key})."' WHERE MerchandiseFormat='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_vendor_mformat');
		$cfg{'vendor_mformat'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_vendor_mformat','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'vendor_mformat'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vendors WHERE MerchandiseFormat='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_venmform&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_venmform.html');
	
}

##################################################################
#     MERCHANDISING : VENDED    	#
##################################################################
sub mer_setup_prdpacking {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_packing'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET Packing='".&filter_values($in{$key})."' WHERE Packing='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_packing');
		$cfg{'prod_packing'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_packing','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_packing'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Packing='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_prdpacking&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_prdpacking.html');
	
}

##################################################################
#     MERCHANDISING : PRODUCTIONS DOC    	#
##################################################################
sub mer_setup_prddocs {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_docs'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET ProductDocs='".&filter_values($in{$key})."' WHERE ProductDocs='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_docs');
		$cfg{'prod_docs'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_docs','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_docs'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ProductDocs='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_prddocs&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_prdinst.html');
	
}

##################################################################
#     MERCHANDISING : PRODUCTS HAND    	#
##################################################################
sub mer_setup_prdhand {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_handling'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET HandlingSpecs='".&filter_values($in{$key})."' WHERE HandlingSpecs='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_handling');
		$cfg{'prod_handling'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_handling','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_handling'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE HandlingSpecs='$ary[$i]';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_ventype&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_prdhand.html');
}

##################################################################
#     MERCHANDISING : PRODUCTS TYPE    	#
##################################################################
sub mer_setup_prdtype {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";
	my (@ary) = split(/,/,$cfg{'prod_type'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET ProductType='".&filter_values($in{$key})."' WHERE ProductType='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_type');
		$cfg{'prod_type'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_type','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_type'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ProductType=\"$ary[$i]\";");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_prdtype&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_prdtype.html');
		
}

##################################################################
#     MERCHANDISING : PRODUCTS WAREHOUSEHAND    	#
##################################################################
sub mer_setup_prdwhand {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_whandling'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET WarehouseHandling='".&filter_values($in{$key})."' WHERE WarehouseHandling='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_whandling');
		$cfg{'prod_whandling'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_whandling','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_whandling'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE WarehouseHandling='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_prdwhand&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_prdwhand.html');	
}


##################################################################
#     MERCHANDISING : PRODUCTS PACKING   	#
##################################################################
sub mer_setup_prdspacking {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_spacking'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products SET SupplierPacking='".&filter_values($in{$key})."' WHERE SupplierPacking='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_spacking');
		$cfg{'prod_spacking'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_spacking','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_spacking'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE SupplierPacking='$ary[$i]';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_ventype&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_prdspacking.html');	
}


##################################################################
#     MERCHANDISING : PRODUCTS WAREHOUSEHAND    	#
##################################################################
sub mer_setup_prdpayments {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'prod_paytypes'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_products_vendors SET PaymentTerms='".&filter_values($in{$key})."' WHERE PaymentTerms='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_pterms');
		$cfg{'prod_paytypes'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_pterms','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'prod_paytypes'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_vendors WHERE PaymentTerms='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_prdpayments&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	
	print &build_page('mer_setup_prdpayments.html');
}

##################################################################
#     MERCHANDISING : PRODUCTS SHIPPING    	#
##################################################################
sub mer_setup_poship {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	
	print "Content-type: text/html\n\n";

	my (@ary) = split(/,/,$cfg{'po_shpvia'});
	if ($in{'action'}){
		my ($aux) = '';
		if ($in{'drop'}){
			for my $i(0..$#ary){
				if ($in{'drop'} ne $ary[$i]){
					$aux .= $ary[$i] . ",";
				}
			}
		}else{
			foreach $key (sort keys %in) {
				if ($key eq 'field_new'){
					(!$in{$key}) and (next);
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
				}elsif($key =~ /^field_(.*)/ and $in{$key}){
					$in{$key} =~ s/,//g;
					$aux .= $in{$key} . ",";
					## Update Vendors Types
					my ($sth) = &Do_SQL("UPDATE sl_purchaseorders SET Shipvia='".&filter_values($in{$key})."' WHERE Shipvia='$ary[$i]';");
					
				}elsif ($key =~ /^field_(.*)/){
					$aux .= $ary[$1] . ",";
				}
			}
		}
		chop($aux);
		$va{'message'} =  &trans_txt('admin_prd_pterms');
		$cfg{'po_shpvia'} = $aux;
		&update_system('./setup.cfg');
		&auth_logging('admin_prd_pterms','');
		$in{'field_new'} = '';
	}

	$va{'options_list'} = '';
	my (@ary) = split(/,/,$cfg{'po_shpvia'});
	for my $i(0..$#ary){
		$va{'options_list'} .= "  <tr>\n";
		$va{'options_list'} .= qq|  <td class='small_txt'>$ary[$i]</td>\n|;
		$va{'options_list'} .= qq|  <td class='small_txt'><input type="text" name="field_$i" style="width:100%" value="$ary[$i]" size="60" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE Shipvia='".&filter_values($ary[$i])."';");
		my ($count) = $sth->fetchrow();
		if ($count>0){
			$va{'options_list'} .= qq|  <td class='small_txt' align="center">$count</td>\n|;
		}else{
			$va{'options_list'} .= qq|  <td align="center"><a href="/cgi-bin/mod/admin/admin?cmd=mer_setup_poship&action=1&drop=$ary[$i]"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n|;
		}
		$va{'options_list'} .= "  <tr>\n";
	}
	print &build_page('mer_setup_poship.html');
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


sub mer_addparts {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modification: JRG 01/15/2009: Se a¤ade la busqueda por ID_parts
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
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/admin/dbman?cmd=mer_products&view=$id_products&addparts=$in{'id_sku_products'}&id_parts=$rec->{'ID_parts'}&tab=3#tabs')">
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
		my $sth=&Do_SQL("Select * 
from 
sl_purchaseorders 
inner join sl_purchaseorders_items on sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders
where sl_purchaseorders.ID_purchaseorders='$in{'id_purchaseorders'}'
and ID_products='$in{'id_supplies'}'");
		if($sth->rows==0)
		{
			$err++;
		}
		$rec=$sth->fetchrow_hashref;
		$max_received=$rec->{'Qty'}-$rec->{'Received'};
		#Valida cantidad
		if($in{'received'}>$max_received or $in{'received'}=='' or $in{'received'}<=0)
		{
			$err++;
			$error{'received'}=&trans_txt("invalid");
		}
		if($err>0)
		{
			$va{'message'}="The information entered is invalid. The max value for received is $max_received";
		}
		else
		{
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
#   Function: get_iomovement_category
#
#       Es: Devuelve la categoria de un inventory out basado en el postedDate de la orden
#       En: 
#
#
#    Created on: 06/17/09  10:08:34
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#		- $id_orders_products
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<general_deposits>
#
#
sub setup_bank_cmd {
#############################################################################
#############################################################################


	if($in{'action'}){

		if($in{'field_new_cmd'} and $in{'field_new_banks'}){

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vars WHERE VName = 'setup_bank_cmd_". &filter_values($in{'field_new_cmd'}) ."';");
			my ($t) = $sth->fetchrow();

			if(!$t){

				&Do_SQL("INSERT INTO sl_vars SET VName = 'setup_bank_cmd_". &filter_values($in{'field_new_cmd'}) ."', VValue = '". &filter_values($in{'field_new_banks'}) ."';");
				$va{'message'} = &trans_txt('done');

			}

		}elsif($in{'drop'}){

			&Do_SQL("DELETE FROM sl_vars WHERE ID_vars = '". int($in{'drop'}) ."' ;");
			$va{'message'} = &trans_txt('done');			

		}

	}

	######
	###### Bank Cmd List
	######
	$va{'banks_cmd'} = '';
	my $x = 0;
	my ($sth) = &Do_SQL("SELECT ID_vars, VName, VValue FROM sl_vars WHERE VName LIKE 'setup_bank_cmd_%' ORDER BY VName;");
	while(my ($id_vars, $vname, $vvalue) = $sth->fetchrow()){

		my ($a, $this_cmd) = split(/setup_bank_cmd_/, $vname);
		$vvalue =~ s/\|/,/g;

		$va{'banks_cmd'} .= qq|</tr>| if $x%2 == 0 and $x > 0;

		$va{'banks_cmd'} .= qq|<td valign="top"><table class="formtable" align="left" border = "0" width="100%" cellpadding="2" cellspacing="2">\n<tr><th colspan="2" align="center" class="tbltextttl"><a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=setup_bank_cmd&action=1&drop=$id_vars" title="Drop">$this_cmd</a></th></tr>\n|;
		$va{'banks_cmd'} .= qq|<tr><td align="center" class="smalltext">Bank Account</td><td align="center" class="smalltext">Bank Name</td></tr>|;
		
		my ($sth) = &Do_SQL("SELECT sl_accounts.ID_accounts, sl_accounts.Name, ID_banks, sl_banks.Name FROM sl_accounts INNER JOIN sl_banks ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE ID_banks IN (". $vvalue .") AND sl_accounts.Status = 'Active' AND sl_banks.Status = 'Active';");
		while(my ($id_accounts, $aname, $id_banks, $bname) = $sth->fetchrow()){			

			$va{'banks_cmd'} .= qq|<tr><td align="left" class="">$aname ($id_accounts)</td>\n<td align="left">$bname ($id_banks)</td></tr>|;
			
		}

		$va{'banks_cmd'} .= qq|</table></td>|;
		$x++;


	}
	$va{'banks_cmd'} .= qq|</tr>| if $va{'banks_cmd'} ne '';
	($va{'banks_cmd'} eq '') and ($va{'banks_cmd'} = qq|<tr><td align="center">|. &trans_txt('search_nomatches') .qq|</td></tr>|);

	print "Content-type: text/html\n\n";
	print &build_page('setup_bank_cmd.html');

}



1;

