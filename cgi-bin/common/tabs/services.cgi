#####################################################################
########                  SERVICES	                   ########
#####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_services_notes';
	}elsif($in{'tab'} eq 5){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_services';
	}
}
 

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : PRODUCTS
##############################################
	$va{'tab_headers'} = qq|
				<tr>
				  <td class="menu_bar_title">ID</td>
				  <td class="menu_bar_title">Model/Name</td>
					<td class="menu_bar_title" colspan="2">Price</td>
				</tr>\n|;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services_related WHERE ID_services='$in{'id_services'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_services_related LEFT JOIN sl_products ON sl_services_related.ID_products=sl_products.ID_products WHERE ID_services='$in{'id_services'}' LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='$script_url?cmd=mer_products&view=$id&tab=3'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Model'}<br>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price($rec->{'SPrice'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'matches'} =0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : ORDENES
##############################################
	$va{'tab_headers'} = qq|
				<tr>
					<td class="menu_bar_title">Order ID</td>
					<td class="menu_bar_title">Customer</td>
					<td class="menu_bar_title">Order Date</td>
					<td class="menu_bar_title">ShipDate</td>
					<td class="menu_bar_title">Status</td>
				</tr>\n|;
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT sl_orders.ID_orders) FROM sl_orders_products
											INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders
											AND RIGHT( ID_products, 4 ) = '$in{'id_services'}' AND sl_orders_products.Status = 'Active'
											INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers  ");
											
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT DISTINCT sl_orders_products.ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
												ShpDate, sl_orders.Date, sl_orders.Status  
												FROM sl_orders_products INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders AND
												RIGHT(ID_products,4) = '$in{'id_services'}' AND sl_orders_products.Status = 'Active' 
												INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers 
												ORDER BY sl_orders.ID_orders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		
			$sth = &Do_SQL("SELECT DISTINCT sl_orders_products.ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
													ShpDate, sl_orders.Date, sl_orders.Status  
													FROM sl_orders_products INNER JOIN sl_orders ON sl_orders_products.ID_orders = sl_orders.ID_orders AND
													RIGHT(ID_products,4) = '$in{'id_services'}' AND sl_orders_products.Status = 'Active' 
													INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers 
													ORDER BY sl_orders.ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while ($rec = $sth->fetchrow_hashref){
			($rec->{'ShpDate'} eq '0000-00-00') and ($rec->{'ShpDate'} = '');
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"$script_url?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"$script_url?cmd=opr_customers&view=$rec->{'ID_customers'}\">$rec->{'Name'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ShpDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'matches'} = 0;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}


sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab3 : POs
##############################################
	my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE id_services='$in{'id_services'}'");
	my ($rec) = $sth->fetchrow_hashref;
	$in{'saleid_accounts'} =  $rec->{'SaleID_accounts'};
	$in{'purchaseid_accounts'} =  $rec->{'PurchaseID_accounts'};
	# $in{'taxpurchaseid_accounts'} =  $rec->{'TaxPurchaseID_accounts'};
	$in{'tax'} =  $rec->{'Tax'};
	
	$in{'servicetype'} = &load_name('sl_services','ID_services',$in{'id_services'},'ServiceType');
	if( $in{'servicetype'} eq 'Purchase' ){
		$va{'paccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'purchaseid_accounts'},'Name');
		# $va{'taxpaccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'taxpurchaseid_accounts'},'Name');
		$va{'show_account_purchase'} = 'display: table-row;';
		$va{'show_account_sale'} = 'display: none;';
	}else{
		$va{'saccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'saleid_accounts'},'Name');
		$va{'show_account_purchase'} = 'display: none;';
		$va{'show_account_sale'} = 'display: table-row;';
	}
	
}

sub load_tabs6 {
# --------------------------------------------------------
##############################################
## tab6 : VENDORS
##############################################

	## DROP
	if ($in{'vdrop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_services_vendors WHERE ID_services='$in{'id_services'}' AND ID_services_vendors='$in{'vdrop'}'");
		&auth_logging('mer_services_delvend',$in{'id_services'});
		$va{'tabmessage'} = &trans_txt('mer_services_delvend');
	## ADD
	}elsif ($in{'addvendor'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_services_vendors SET ID_services='$in{'id_services'}', ID_vendors='$in{'addvendor'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		$va{'tabmessage'} = &trans_txt('mer_services_addvend');
		&auth_logging('mer_services_addvend',$in{'id_services'});
	}
	
	## VENDOR LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services_vendors WHERE ID_services='$in{'id_services'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_services_vendors INNER JOIN sl_vendors ON sl_services_vendors.ID_vendors=sl_vendors.ID_vendors WHERE ID_services='$in{'id_services'}' ORDER BY ID_services_vendors DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=$in{'id_services'}&tab=6&vdrop=$rec->{'ID_services_vendors'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_vendors'}) $rec->{'CompanyName'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT PODate 
									FROM sl_purchaseorders_items 
										INNER JOIN sl_purchaseorders ON sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders
											AND RIGHT(ID_products, 4) = ".$in{'id_services'}."
											AND ID_vendors = ".$rec->{'ID_vendors'}."
									WHERE 1 
									ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext'>".$sth2->fetchrow."</td>\n";
			my ($sth2) = &Do_SQL("SELECT SUM(Qty*Price) FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_parts'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

sub load_tabs7 {
# --------------------------------------------------------
##############################################
## tab7 : Accountin Retention
##############################################

	my $command = 'service_account_retention';
	my $allow_perm = 0;
	if( &check_permissions('services_retention_setup','','') ){
		$allow_perm = 1;
	}

	my $sth = &Do_SQL("SELECT sl_vars_config.ID_vars_config
							, sl_vars_config.Code 
							, sl_vars_config.Subcode
							, sl_vars_config.Largecode
							, sl_vars_config.Description
							, sl_accounts.Name
							, sl_accounts.ID_accounting
						FROM sl_vars_config 
							INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_vars_config.Code 
						WHERE Command = '".$command."' AND IDValue = ".$in{'id_services'}.";");
	my $ind = 0;
	while( my $rec = $sth->fetchrow_hashref() ){
		$va{'accounts_ret_list'} .= '<tr>';
		$va{'accounts_ret_list'} .= '<td>['.$rec->{'ID_accounting'}.'] - '.$rec->{'Name'}.'</td>';
		$va{'accounts_ret_list'} .= '<td style="text-align: center;">'.$rec->{'Subcode'}.' %</td>';
		$va{'accounts_ret_list'} .= '<td style="text-align: center;">'.$rec->{'Largecode'}.'</td>';
		$va{'accounts_ret_list'} .= '<td style="text-align: center;">'.$rec->{'Description'}.'</td>';
		$va{'accounts_ret_list'} .= '<td style="text-align: right;">';
		if( $allow_perm == 1 ){
			$va{'accounts_ret_list'} .= '<a href="#" data-id="'.$rec->{'ID_vars_config'}.'" class="lnk_drop_retention" title="Eliminar esta cuenta"><img src="/sitimages/default/b_drop.png" alt="delete" /></a>';
		} else {
			$va{'accounts_ret_list'} .= '&nbsp;';
		}
		$va{'accounts_ret_list'} .= '</td>';
		$va{'accounts_ret_list'} .= '</tr>';
	}
	
}

1;