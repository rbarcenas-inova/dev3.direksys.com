####################################################################
########             CUSTOMERS                  ########
####################################################################
sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : USA TDC
##############################################

	## Data
	my ($query);
	
	my $zone='USA';
	my $method='Credit-Card';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} == 0){
		## Build the initial table	
		my @ary_qty = split(/\|/,$cfg{'shipping_prices_quantity'});
		my @ary_net = split(/\|/,$cfg{'shipping_prices_netsale'});
		my $sth_query;
		my $i=0;
		
		for ($i..$#ary_qty){
			$i = $_;
			my $j=0;
			for ($j..$#ary_net){
				$j=$_;
				$sth_query  .= "INSERT INTO sl_products_shipping SET ID_products='$in{'id_products'}', Zone='$zone', Method='$method', Quantity=$ary_qty[$i], Amount='$ary_net[$j]', Shipping_price='', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
			}
		}

		$xsth = &Do_mSQL($sth_query);
		if($xsth){
			&Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}', Notes='New Shipping Price Table Added for $zone - $method', Type='Low', Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';"); 
			&auth_logging('shipping_table_added',$in{'id_products'});
		}
	}
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} > 0){
		
		$va{'colspan'}=1;
		my @ary_net;
		my ($sth2) = &Do_SQL("SELECT DISTINCT `Amount` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY Amount; ");
		while(my($samount) = $sth2->fetchrow()){
				$va{'header_amount'} .= "<td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;' align='right'>";
				$va{'header_amount'} .= "<input type='hidden' id='hx_$samount' value='$samount'>";
				$va{'header_amount'} .= "<input type='text' id='x_$samount' size='8' onBlur='chg_shptable(this.id)' value='". &format_price($samount,2) ."'></td>\n";
				push(@ary_net,$samount);
				$va{'colspan'}++;	
		}
		
		my $sth3;
		
		if ($in{'print'}){
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity`;");
		}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity` LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while(my($sqty) = $sth3->fetchrow()){
		
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;'>";
			$va{'searchresults'} .= "<input type='hidden' id='hy_$sqty' value='$sqty'>\n";
			$va{'searchresults'} .= "<input type='text' id='y_$sqty' size='6' onBlur='chg_shptable(this.id)' value='$sqty'></td>\n";
		
			my ($sth4) = &Do_SQL("SELECT * FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' AND Quantity='$sqty' ORDER BY Amount; ");
		
		
			my $x=0;
			while ($rec = $sth4->fetchrow_hashref){
				
				while($rec->{'Amount'} < $ary_net[$x]){
					$va{'searchresults'} .= "  <td class='smalltext'>N/A</td>\n";
					$x++;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>";
				$va{'searchresults'} .= "	 <input type='text' id='z_$rec->{'ID_products_shipping'}' size='6' onBlur='chg_shptable(this.id)' value='". &format_price($rec->{'Shipping_price'},2) ."'></td>\n";			
				$x++;
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	

	# ## Tables Header/Titles
	# $va{'keyname'} = $zone . ' ' .$method;
	# $va{'tab_zone'} = $zone;
	# $va{'tab_method'} = $method;
	# &load_db_fields_values($in{'db'},'ID_products',$in{'id_products'},'*');
}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : USA COD
##############################################

	## Data
	my ($query);
	
	my $zone='USA';
	my $method='COD';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} == 0){
		## Build the initial table	
		my @ary_qty = split(/\|/,$cfg{'shipping_prices_quantity'});
		my @ary_net = split(/\|/,$cfg{'shipping_prices_netsale'});
		my $sth_query;
		my $i=0;
		
		for ($i..$#ary_qty){
			$i = $_;
			my $j=0;
			for ($j..$#ary_net){
				$j=$_;
				$sth_query  .= "INSERT INTO sl_products_shipping SET ID_products='$in{'id_products'}', Zone='$zone', Method='$method', Quantity=$ary_qty[$i], Amount='$ary_net[$j]', Shipping_price='', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
			}
		}

		$xsth = &Do_mSQL($sth_query);
		if($xsth){
			&Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}', Notes='New Shipping Price Table Added for $zone - $method', Type='Low', Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';"); 
			&auth_logging('shipping_table_added',$in{'id_products'});
		}
	}
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} > 0){
		
		$va{'colspan'}=1;
		my @ary_net;
		my ($sth2) = &Do_SQL("SELECT DISTINCT `Amount` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY Amount; ");
		while(my($samount) = $sth2->fetchrow()){
				$va{'header_amount'} .= "<td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;' align='right'>";
				$va{'header_amount'} .= "<input type='hidden' id='hx_$samount' value='$samount'>";
				$va{'header_amount'} .= "<input type='text' id='x_$samount' size='8' onBlur='chg_shptable(this.id)' value='". &format_price($samount,2) ."'></td>\n";
				push(@ary_net,$samount);
				$va{'colspan'}++;	
		}
		
		my $sth3;
		
		if ($in{'print'}){
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity`;");
		}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity` LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while(my($sqty) = $sth3->fetchrow()){
		
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;'>";
			$va{'searchresults'} .= "<input type='hidden' id='hy_$sqty' value='$sqty'>\n";
			$va{'searchresults'} .= "<input type='text' id='y_$sqty' size='6' onBlur='chg_shptable(this.id)' value='$sqty'></td>\n";
		
			my ($sth4) = &Do_SQL("SELECT * FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' AND Quantity='$sqty' ORDER BY Amount; ");
		
		
			my $x=0;
			while ($rec = $sth4->fetchrow_hashref){
				
				while($rec->{'Amount'} < $ary_net[$x]){
					$va{'searchresults'} .= "  <td class='smalltext'>N/A</td>\n";
					$x++;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>";
				$va{'searchresults'} .= "	 <input type='text' id='z_$rec->{'ID_products_shipping'}' size='6' onBlur='chg_shptable(this.id)' value='". &format_price($rec->{'Shipping_price'},2) ."'></td>\n";			
				$x++;
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	

	# ## Tables Header/Titles
	# $va{'keyname'} = $zone . ' ' .$method;
	# $va{'tab_zone'} = $zone;
	# $va{'tab_method'} = $method;
	# &load_db_fields_values($in{'db'},'ID_products',$in{'id_products'},'*');

}


sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : PR-Puerto Rico/AK-Alaska/HI-Hawaii TDC
##############################################

	## Data
	my ($query);
	
	my $zone='PR-Puerto Rico/AK-Alaska/HI-Hawaii';
	my $method='Credit-Card';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} == 0){
		## Build the initial table	
		my @ary_qty = split(/\|/,$cfg{'shipping_prices_quantity'});
		my @ary_net = split(/\|/,$cfg{'shipping_prices_netsale'});
		my $sth_query;
		my $i=0;
		
		for ($i..$#ary_qty){
			$i = $_;
			my $j=0;
			for ($j..$#ary_net){
				$j=$_;
				$sth_query  .= "INSERT INTO sl_products_shipping SET ID_products='$in{'id_products'}', Zone='$zone', Method='$method', Quantity=$ary_qty[$i], Amount='$ary_net[$j]', Shipping_price='', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
			}
		}

		$xsth = &Do_mSQL($sth_query);
		if($xsth){
			&Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}', Notes='New Shipping Price Table Added for $zone - $method', Type='Low', Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';"); 
			&auth_logging('shipping_table_added',$in{'id_products'});
		}
	}
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} > 0){
		
		$va{'colspan'}=1;
		my @ary_net;
		my ($sth2) = &Do_SQL("SELECT DISTINCT `Amount` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY Amount; ");
		while(my($samount) = $sth2->fetchrow()){
				$va{'header_amount'} .= "<td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;' align='right'>";
				$va{'header_amount'} .= "<input type='hidden' id='hx_$samount' value='$samount'>";
				$va{'header_amount'} .= "<input type='text' id='x_$samount' size='8' onBlur='chg_shptable(this.id)' value='". &format_price($samount,2) ."'></td>\n";
				push(@ary_net,$samount);
				$va{'colspan'}++;	
		}
		
		my $sth3;
		
		if ($in{'print'}){
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity`;");
		}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity` LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while(my($sqty) = $sth3->fetchrow()){
		
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;'>";
			$va{'searchresults'} .= "<input type='hidden' id='hy_$sqty' value='$sqty'>\n";
			$va{'searchresults'} .= "<input type='text' id='y_$sqty' size='6' onBlur='chg_shptable(this.id)' value='$sqty'></td>\n";
		
			my ($sth4) = &Do_SQL("SELECT * FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' AND Quantity='$sqty' ORDER BY Amount; ");
		
		
			my $x=0;
			while ($rec = $sth4->fetchrow_hashref){
				
				while($rec->{'Amount'} < $ary_net[$x]){
					$va{'searchresults'} .= "  <td class='smalltext'>N/A</td>\n";
					$x++;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>";
				$va{'searchresults'} .= "	 <input type='text' id='z_$rec->{'ID_products_shipping'}' size='6' onBlur='chg_shptable(this.id)' value='". &format_price($rec->{'Shipping_price'},2) ."'></td>\n";			
				$x++;
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	

	# ## Tables Header/Titles
	# $va{'keyname'} = $zone . ' ' .$method;
	# $va{'tab_zone'} = $zone;
	# $va{'tab_method'} = $method;
	# &load_db_fields_values($in{'db'},'ID_products',$in{'id_products'},'*');
}


sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab4 : PR-Puerto Rico/AK-Alaska/HI-Hawaii COD
##############################################

	## Data
	my ($query);
	
	my $zone='PR-Puerto Rico/AK-Alaska/HI-Hawaii';
	my $method='COD';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} == 0){
		## Build the initial table	
		my @ary_qty = split(/\|/,$cfg{'shipping_prices_quantity'});
		my @ary_net = split(/\|/,$cfg{'shipping_prices_netsale'});
		my $sth_query;
		my $i=0;
		
		for ($i..$#ary_qty){
			$i = $_;
			my $j=0;
			for ($j..$#ary_net){
				$j=$_;
				$sth_query  .= "INSERT INTO sl_products_shipping SET ID_products='$in{'id_products'}', Zone='$zone', Method='$method', Quantity=$ary_qty[$i], Amount='$ary_net[$j]', Shipping_price='', Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
			}
		}

		$xsth = &Do_mSQL($sth_query);
		if($xsth){
			&Do_SQL("INSERT INTO sl_products_notes SET ID_products='$in{'id_products'}', Notes='New Shipping Price Table Added for $zone - $method', Type='Low', Date=CURDATE(), Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';"); 
			&auth_logging('shipping_table_added',$in{'id_products'});
		}
	}
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method'; ");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'} > 0){
		
		$va{'colspan'}=1;
		my @ary_net;
		my ($sth2) = &Do_SQL("SELECT DISTINCT `Amount` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY Amount; ");
		while(my($samount) = $sth2->fetchrow()){
				$va{'header_amount'} .= "<td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;' align='right'>";
				$va{'header_amount'} .= "<input type='hidden' id='hx_$samount' value='$samount'>";
				$va{'header_amount'} .= "<input type='text' id='x_$samount' size='8' onBlur='chg_shptable(this.id)' value='". &format_price($samount,2) ."'></td>\n";
				push(@ary_net,$samount);
				$va{'colspan'}++;	
		}
		
		my $sth3;
		
		if ($in{'print'}){
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity`;");
		}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				$sth3 = &Do_SQL("SELECT DISTINCT `Quantity` FROM `sl_products_shipping` WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' ORDER BY `Quantity` LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while(my($sqty) = $sth3->fetchrow()){
		
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' style='background-color:#2f2f2f;color:#ffffff;'>";
			$va{'searchresults'} .= "<input type='hidden' id='hy_$sqty' value='$sqty'>\n";
			$va{'searchresults'} .= "<input type='text' id='y_$sqty' size='6' onBlur='chg_shptable(this.id)' value='$sqty'></td>\n";
		
			my ($sth4) = &Do_SQL("SELECT * FROM sl_products_shipping WHERE ID_products='$in{'id_products'}' AND Zone='$zone' AND Method='$method' AND Quantity='$sqty' ORDER BY Amount; ");
		
		
			my $x=0;
			while ($rec = $sth4->fetchrow_hashref){
				
				while($rec->{'Amount'} < $ary_net[$x]){
					$va{'searchresults'} .= "  <td class='smalltext'>N/A</td>\n";
					$x++;
				}
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>";
				$va{'searchresults'} .= "	 <input type='text' id='z_$rec->{'ID_products_shipping'}' size='6' onBlur='chg_shptable(this.id)' value='". &format_price($rec->{'Shipping_price'},2) ."'></td>\n";			
				$x++;
			}
			$va{'searchresults'} .= "</tr>\n";
		}
	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	

	## Tables Header/Titles
	#$va{'keyname'} = $zone . ' ' .$method;
	#$va{'tab_zone'} = $zone;
	#$va{'tab_method'} = $method;
	#&load_db_fields_values($in{'db'},'ID_products',$in{'id_products'},'*');
}

1;


