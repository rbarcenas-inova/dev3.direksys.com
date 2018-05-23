#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 7){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_parts_notes';
	}elsif($in{'tab'} eq 8){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_parts';
	}
}
 

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : PRODUCTS
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_parts WHERE ID_parts='$in{'id_parts'}' GROUP BY RIGHT(ID_sku_products,4)");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_skus_parts WHERE ID_parts='$in{'id_parts'}'  GROUP BY RIGHT(ID_sku_products,4) ORDER BY ID_parts DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id = substr($rec->{'ID_sku_products'},3,6);
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$id&tab=3'>".&format_sltvid($rec->{'ID_sku_products'})."</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&load_db_names('sl_products','ID_products',$id,'[Model]<br>[Name]')."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_price(&load_name('sl_products','ID_products',$id,'SPrice'))."</td>\n";
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


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : VENDORS
##############################################

	## DROP
	if ($in{'vdrop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_parts_vendors WHERE ID_parts='$in{'id_parts'}' AND ID_parts_vendors='$in{'vdrop'}'");
		&auth_logging('mer_parts_delvend',$in{'id_parts'});
		$va{'tabmessage'} = &trans_txt('mer_parts_delvend');
	## ADD
	}elsif ($in{'addvendor'}){
		my ($sth) = &Do_SQL("INSERT INTO sl_parts_vendors SET ID_parts='$in{'id_parts'}', ID_vendors='$in{'addvendor'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		$va{'tabmessage'} = &trans_txt('mer_parts_addvend');
		&auth_logging('mer_parts_addvend',$in{'id_parts'});
	}
	
	## VENDOR LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_vendors WHERE id_parts='$in{'id_parts'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_parts_vendors,sl_vendors WHERE ID_parts='$in{'id_parts'}' AND sl_parts_vendors.ID_vendors=sl_vendors.ID_vendors ORDER BY ID_parts_vendors DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>";
			$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&tab=2&vdrop=$rec->{'ID_parts_vendors'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			$va{'searchresults'} .= "</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_vendors'}) $rec->{'CompanyName'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT PODate FROM sl_purchaseorders_items,sl_purchaseorders WHERE sl_purchaseorders_items.ID_purchaseorders=sl_purchaseorders.ID_purchaseorders AND RIGHT(ID_products,4)='$in{'id_parts'}' AND ID_vendors=$rec->{'ID_vendors'} ORDER BY PODate DESC;");
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


sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : POs
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products='".(400000000+$in{'id_parts'})."' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman", $va{'matches'}, $usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_items WHERE ID_products='".(400000000+$in{'id_parts'})."'  $query ORDER BY ID_purchaseorders_items DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'ID_vendors'} = &load_name('sl_purchaseorders','ID_purchaseorders',$rec->{'ID_purchaseorders'},'ID_vendors');
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}'>".&load_db_names('sl_vendors','ID_vendors',$rec->{'ID_vendors'},"([ID_vendors]) [CompanyName]")."</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_number($rec->{'Qty'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_number($rec->{'Received'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
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
	my ($sth) = &Do_SQL("SELECT * FROM sl_parts WHERE id_parts='$in{'id_parts'}'");
	my ($rec) = $sth->fetchrow_hashref;
	$in{'purchaseid_accounts'} =  $rec->{'PurchaseID_accounts'};
	$in{'saleid_accounts'} =  $rec->{'SaleID_accounts'};
	$in{'assetid_accounts'} =  $rec->{'AssetID_accounts'};
	$in{'tax'} =  $rec->{'Tax'};
	$va{'paccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'purchaseid_accounts'},'Name');
	$va{'saccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'saleid_accounts'},'Name');
	$va{'aaccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'assetid_accounts'},'Name');
	
}

sub load_tabs5 {
# --------------------------------------------------------
##############################################
## tab5 : SKUs cost
##############################################
	#cgierr();
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_cost LEFT JOIN sl_warehouses ON sl_skus_cost.ID_warehouses=sl_warehouses.ID_warehouses WHERE Quantity > 0 AND ID_products=('$in{'id_parts'}' + 400000000);");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_skus_cost LEFT JOIN sl_warehouses ON sl_skus_cost.ID_warehouses=sl_warehouses.ID_warehouses  WHERE Quantity > 0 AND ID_products=('$in{'id_parts'}' + 400000000) ORDER BY sl_skus_cost.Date DESC LIMIT $first,$usr{'pref_maxh'};");
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id = $rec->{'ID_products'};
			##'sl_purchaseorders','sl_returns','sl_adjustments','sl_manifests','transfer','sl_parts_productions'
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "<td class='smalltext'>".$rec->{'Date'}."</td>\n";
			$va{'searchresults'} .= "<td class='smalltext'>(<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$rec->{'ID_warehouses'}'>$rec->{'ID_warehouses'}</a>) $rec->{'Name'}</td>\n";
			if ($rec->{'Tblname'}){
				$va{'searchresults'} .= "<td class='smalltext'>".&trans_txt('mer_parts_cost_from_'.$rec->{'Tblname'})."</td>\n"
			}else{
				$va{'searchresults'} .= "<td class='smalltext'>---</td>\n"
			}
			$va{'searchresults'} .= "<td class='smalltext' align='right'>".&format_number($rec->{'Quantity'})."</td>\n";
			$va{'searchresults'} .= "<td class='smalltext' align='right'>".&format_price($rec->{'Cost'})."</td>\n";
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

sub load_tabs6 {
# --------------------------------------------------------
##############################################
## tab6 : Transactions
##############################################

	## ITEMS
	my ($choices_on,$tot_qty,$vendor_sku);
	my (@c) = split(/,/,$cfg{'srcolors'});
	
	my $id_products = (400000000 + $in{'id_parts'});
	my $query_list = "SELECT ID_warehouses, ID_products, Type, Location, Type_trans, tbl_name, ID_trs, Quantity, Cost, Date, Time,ID_admin_users FROM sl_skus_trans WHERE ID_products = '$id_products' ";

	my ($sth) = &Do_SQL($query_list);
	$va{'matches'} = $sth->rows();
	
	if ($va{'matches'}>0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("$query_list ORDER BY sl_skus_trans.ID_products_trans DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			my %cmds = (
			"sl_orders", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_orders&view='.$rec->{'ID_trs'}
			,"sl_returns", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_returns&view='.$rec->{'ID_trs'}
			,"sl_purchases", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_po&view='.$rec->{'ID_trs'}
			,"sl_adjustments", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_adjustments&view='.$rec->{'ID_trs'}
			,"sl_wreceipts", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_wreceipts&view='.$rec->{'ID_trs'}
			,"sl_manifests", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_manifests&view='.$rec->{'ID_trs'}
			,"sl_parts_productions", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_parts_productions&view='.$rec->{'ID_trs'}
			,"sl_skustransfers", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_skustransfers&view='.$rec->{'ID_trs'}
			,"sl_purchaseorders", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_po&view='.$rec->{'ID_trs'}
			,"sl_creditmemos", '/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_creditmemos&view='.$rec->{'ID_trs'});
		
			$d = 1 - $d;
			my $wname = &load_name('sl_warehouses', 'ID_warehouses', $rec->{'ID_warehouses'},'Name');
			my $uname = &load_db_names('admin_users', 'ID_admin_users', $rec->{'ID_admin_users'},"[FirstName] [LastName]");
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='left' valign='top'>$rec->{'Date'} $rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=".$rec->{'ID_warehouses'}."'>(".$rec->{'ID_warehouses'}.") $wname</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='left' valign='top'>$rec->{'Location'}</td>\n";
			$va{'searchresults'} .= qq| <td class='smalltext' align='left' valign='top'><a href="$cmds{$rec->{'tbl_name'}}">$rec->{'Type_trans'}</a></td>\n|;
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Quantity'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$uname (<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrman&view=$rec->{'ID_admin_users'}'>$rec->{'ID_admin_users'}</a>)</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		
		}

	}else{

		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;

	}
}

sub load_tabs9 {
# --------------------------------------------------------
##############################################
## tab9 : Locations
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location LEFT JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses WHERE ID_products=('$in{'id_parts'}' + 400000000);");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT 
			sl_warehouses_location.ID_warehouses
			, sl_warehouses_location.Location
			, SUM(sl_warehouses_location.Quantity)Quantity
			, sl_warehouses.Name
			, sl_warehouses.Type
		FROM sl_warehouses_location 
		INNER JOIN sl_warehouses ON sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses 
		INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
		WHERE ID_products=('$in{'id_parts'}' + 400000000)
		AND sl_warehouses.Status='Active'
		AND sl_locations.Status='Active'
		GROUP BY sl_warehouses_location.ID_warehouses, sl_warehouses_location.ID_products, sl_warehouses_location.Location
		LIMIT $first,$usr{'pref_maxh'};");
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$id = $rec->{'ID_products'};
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "<td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$rec->{'ID_warehouses'}'>($rec->{'ID_warehouses'}) $rec->{'Name'}</a></td>\n";
			$va{'searchresults'} .= "<td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "<td class='smalltext'>$rec->{'Location'}</td>\n";
			$va{'searchresults'} .= "<td class='smalltext' align='right'>".&format_number($rec->{'Quantity'})."</td>\n";
		
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

sub load_tabs10 {
# --------------------------------------------------------
##############################################
## tab10 : Lots
##############################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($newline, $listed_lots,$temp_list,$lot_qtotal,$err,$lot);
	$va{'err'} = 0;
	$in{'vdrop'} = int($in{'vdrop'});
	$in{'fdrop'} = int($in{'fdrop'});
	$in{'toactive'} = int($in{'toactive'});
	if ($in{'vdrop'}>0){
		if(&check_permissions($in{'cmd'},'_lotinact','')){ 
			my ($sth) = &Do_SQL("UPDATE sl_locations_lots SET Status='Inactive' WHERE ID_locations_lots='$in{'vdrop'}'");
			&auth_logging('mer_parts_lotinactive',$in{'id_parts'});
			$va{'tabmessage'} = &trans_txt('mer_parts_lotinactive');
		}else{
			$va{'tabmessage'} = &trans_txt('unauth_action');
		}
	}elsif($in{'fdrop'}>0){
		if(&check_permissions($in{'cmd'},'_lotdel','')){ 
			my ($sth) = &Do_SQL("SELECT * FROM  sl_locations_lots WHERE ID_locations_lots='$in{'fdrop'}'");
			$lot = $sth->fetchrow_hashref;
			$in{'info'} = qq|SKU : $lot->{'ID_products'}\nQty : $lot->{'Quantity'}\nInfo1 : $lot->{'CustomField1'}\nInfo2 : $lot->{'CustomField2'}\nInfo3 : $lot->{'CustomField3'}\nInfo4 : $lot->{'CustomField4'}\nInfo5 : $lot->{'CustomField5'}\nInfo6 : $lot->{'CustomField6'}|;
			my ($sth) = &Do_SQL("INSERT INTO sl_locations_lotslogs SET 
				ID_products=$lot->{'ID_products'},Location='".&filter_values($lot->{'Location'})."',Type='Adj',ID_warehouses=$lot->{'ID_warehouses'},
				Info='".&filter_values($in{'info'})."',
				Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
			my ($sth) = &Do_SQL("DELETE FROM sl_locations_lots WHERE ID_locations_lots='$in{'fdrop'}'");
			&auth_logging('mer_parts_lotdeleted',$in{'id_parts'});
			$va{'tabmessage'} = &trans_txt('mer_parts_lotdeleted');			
		}else{
			$va{'tabmessage'} = &trans_txt('unauth_action');
		}
	}elsif($in{'toactive'}>0){
		if(&check_permissions($in{'cmd'},'_lotact','')){ 
			my ($sth) = &Do_SQL("UPDATE sl_locations_lots SET Status='Active' WHERE ID_locations_lots='$in{'toactive'}'");
			&auth_logging('mer_parts_lotactive',$in{'id_parts'});
			$va{'tabmessage'} = &trans_txt('mer_parts_lotactive');
		}else{
			$va{'tabmessage'} = &trans_txt('unauth_action');
		}
	}elsif($in{'tabaction'} eq 'addlotinfo' and $in{'tabact'}){
		if(&check_permissions($in{'cmd'},'_lotadd','')){ 
			$in{'quantity'} = int($in{'quantity'});
			if (!$in{'quantity'}){
				$error{'quantity'} = &trans_txt('required');
				++$err
			}
			if(!$in{'location'}){
				$error{'quantity'} = &trans_txt('required');
				++$err
			}else{
				$in{'id_warehouses'} = &load_name('sl_locations','Code',$in{'location'},'ID_locations');
				if (!$in{'id_warehouses'}){
					$error{'location'} = &trans_txt('invalid');
					++$err
				}
			}
			if (!$err){
				my ($sth) = &Do_SQL("INSERT INTO sl_locations_lots SET 
				ID_products=400000000 + $in{'id_parts'},Location='".&filter_values($in{'location'})."',Quantity=$in{'quantity'},ID_warehouses=$in{'id_warehouses'},
				CustomField1='".&filter_values($in{'customfield1'})."',CustomField2='".&filter_values($in{'customfield2'})."',CustomField3='".&filter_values($in{'customfield3'})."',CustomField4='".&filter_values($in{'customfield4'})."',CustomField5='".&filter_values($in{'customfield5'})."',CustomField6='".&filter_values($in{'customfield6'})."',
				Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
				
				$in{'info'} = "SKU : ".(400000000 + $in{'id_parts'}).qq|\nQty : $in{'quantity'}\nInfo1 : $in{'customfield1'}\nInfo2 : $in{'customfield2'}\nInfo3 : $in{'customfield3'}\nInfo4 : $in{'customfield4'}\nInfo5 : $in{'customfield5'}\nInfo6 : $in{'customfield6'}|;
				my ($sth) = &Do_SQL("INSERT INTO sl_locations_lotslogs SET 
				ID_products=400000000 + $in{'id_parts'},Location='".&filter_values($in{'location'})."',Type='Adj',ID_warehouses=$in{'id_warehouses'},
				Info='".&filter_values($in{'info'})."',
				Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
				delete($in{'tabaction'});
				&auth_logging('mer_parts_lotadded',$in{'id_parts'});
				$va{'tabmessage'} = &trans_txt('mer_parts_lotadded');
			}else{
				$va{'tabmessage'} = &trans_txt('reqfields_short');
			}
		}else{
			$va{'tabmessage'} = &trans_txt('unauth_action');
		}
	}
	if (&load_name('sl_parts','ID_parts',$in{'id_parts'},'Lots') eq 'Enable'){
		if($in{'tabaction'} eq 'addlotinfo'){
			$va{'new_tbname'} = 'parts_tab10_add';
		}elsif($in{'tabaction'} eq 'lotlogs'){
			$va{'new_tbname'} = 'parts_tab10_logs';
			my (@c) = split(/,/,$cfg{'srcolors'});
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_locations_lotslogs WHERE ID_products=400000000+$in{'id_parts'} ");
			$va{'matches'} = $sth->fetchrow;
			if ($va{'matches'}>0){
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				my ($sth) = &Do_SQL("SELECT * FROM sl_locations_lotslogs WHERE ID_products=400000000+$in{'id_parts'} ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Info'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ID_admin_users'}</td>\n";
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
			return;
		}else{
			my ($sth) = &Do_SQL("SELECT (400000000+ID_parts) AS sku, 
									sl_warehouses_location.Location AS LocLoc,
									sl_warehouses_location.Quantity AS LocQty,
									ID_warehouses
								FROM  sl_warehouses_location
									LEFT JOIN  sl_parts
									ON (400000000+ID_parts)=sl_warehouses_location.ID_products
								WHERE ID_parts='$in{'id_parts'}'");
			$va{'matches'} = $sth->rows();
			if ($va{'matches'}>0){
				### List based ob WH Location
				while ($rec = $sth->fetchrow_hashref){
					$d = 1 - $d;
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "<td class='smalltext'>$rec->{'LocLoc'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' align='right'>".&format_number($rec->{'LocQty'})."</td>\n";
					$va{'searchresults'} .= "<td></td>\n";
					$newline = 0; $lot_qtotal = 0; $temp_list = '';
					my ($sth2) = &Do_SQL("SELECT *
								FROM  sl_locations_lots
								WHERE ID_products=400000000 + $in{'id_parts'} AND ID_warehouses=$rec->{'ID_warehouses'} AND Location='$rec->{'LocLoc'}' AND Status='Active'");
					while ($lot = $sth2->fetchrow_hashref){
						$action = '';
						$listed_lots .= $lot->{'ID_locations_lots'}.',';
						if ($newline){
							$temp_list .= "<tr bgcolor='$c[$d]'>\n";
							$temp_list .= "<td colspan=3></td>\n";
						}
						$temp_list .= qq|<td class='smalltext' align='center'>
										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&tab=10&vdrop=$lot->{'ID_locations_lots'}#initab"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
											</td>\n|;
						$temp_list .= "<td class='smalltext' align='center' StyleColor>$lot->{'Location'}</td>\n";
						$temp_list .= "<td class='smalltext' align='right' StyleColor>".&format_number($lot->{'Quantity'})."</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField1'}</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField2'}</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField3'}</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField4'}</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField5'}</td>\n";
						$temp_list .= "<td class='smalltext' StyleColor>$lot->{'CustomField6'}</td>\n";
						$temp_list .= "</tr>\n";
						$newline = 1;
						$lot_qtotal += $lot->{'Quantity'};
					}
					if (!$temp_list){
						++$va{'err'};
						$temp_list = "<td class='smalltext' style='Color: red' colspan='9' align='center'>".&trans_txt('mer_parts_nolotinfo')."</td>\n";
					}elsif($rec->{'LocQty'} ne $lot_qtotal){
						$temp_list =~ s/StyleColor/style='Color: red'/g;
						++$va{'err'};
					}else{
						$temp_list =~ s/StyleColor/style='Color: green'/g;
					}
					$va{'searchresults'} .= $temp_list;
				}
				### List based on orfan Lots
				chop($listed_lots);
				$listed_lots = 0 if (!$listed_lots);
				my ($sth) = &Do_SQL("SELECT * FROM  sl_locations_lots
							WHERE ID_products=400000000 + $in{'id_parts'} AND ID_locations_lots NOT IN($listed_lots) AND Status='Active'");
				while ($lot = $sth->fetchrow_hashref){
					++$va{'err'};
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "<td colspan=3></td>\n";
					$va{'searchresults'} .= qq|<td class='smalltext' align='center'>
										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&tab=10&vdrop=$lot->{'ID_locations_lots'}#initab"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
											</td>\n|;
					$va{'searchresults'} .= "<td class='smalltext' align='center' style='Color: red'>$lot->{'Location'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' align='right' style='Color: red'>".&format_number($lot->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField1'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField2'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField3'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField4'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField5'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: red'>$lot->{'CustomField6'}</td>\n";
					$va{'searchresults'} .= "</tr>\n";
				}
				### Inactive
				my ($sth) = &Do_SQL("SELECT * FROM  sl_locations_lots
							WHERE ID_products=400000000 + $in{'id_parts'} AND Status='Inactive'");
				while ($lot = $sth->fetchrow_hashref){
					$d = 1 - $d;
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
					$va{'searchresults'} .= "<td colspan=3></td>\n";
					$va{'searchresults'} .= qq|<td class='smalltext' align='center'>
										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&tab=10&toactive=$lot->{'ID_locations_lots'}#initab"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Active' alt='' border='0'></a>
										<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$in{'id_parts'}&tab=10&fdrop=$lot->{'ID_locations_lots'}#initab"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
											</td>\n|;
					$va{'searchresults'} .= "<td class='smalltext' align='center' style='Color: grey'>$lot->{'Location'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' align='right' style='Color: grey'>".&format_number($lot->{'Quantity'})."</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField1'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField2'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField3'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField4'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField5'}</td>\n";
					$va{'searchresults'} .= "<td class='smalltext' style='Color: grey'>$lot->{'CustomField6'}</td>\n";
					$va{'searchresults'} .= "</tr>\n";
				}
				
				if ($va{'err'}>0){
					$va{'searchresults'} .= qq|
						<tr>
							<td colspan='11' align="center">|.&trans_txt('mer_parts_lots_errores').qq|</td>
						</tr>\n|;
				}
				return;
			}
		}
	}
	$va{'matches'} =0;
	$va{'pageslist'} = 1;
	$va{'searchresults'} = qq|
		<tr>
			<td colspan='10' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	
}

1;