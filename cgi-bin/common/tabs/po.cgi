#!/usr/bin/perl
####################################################################
########                  Purchase Orders                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 9){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_purchaseorders_notes';
	}elsif($in{'tab'} eq 10){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_purchaseorders';
	}elsif($in{'tab'} eq 8){
		## Movs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_purchaseorders';
		$va{'tab_idvalue'} = $in{'id_purchaseorders'};
	}
}
 



sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : ITEMS
##############################################
# Last Modified RB: 05/15/09  16:35:25 -- Si el producsto es un Set, se cargan sus partes
	my ($authby,$err,$item);
	$authby = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	if ($authby >0){
		$va{'tabmessages'} = &trans_txt('mer_po_blocked'). " ";
	}
	## ITEMS LIST
	my ($choices_on,$tot_qty,$tot_po,$tax_po,$subtot_po,$vendor_sku,$name);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};		
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT *, (Qty - Received) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC LIMIT $first,$usr{'pref_maxh'} ;;");

		while ($rec = $sth->fetchrow_hashref){
		
			my $link_cmd='';
			my $link_overlay_segment;
			$d = 1 - $d;

			# Color in Received
			$color = ($rec->{'quantity'}==0)? ' style="color:#73AB00"' : ' style="color:#FF0000"';
			$id_products = $rec->{'ID_products'};
			my $nsegment = $rec->{'ID_segments'} ? &load_name('sl_accounts_segments','ID_accounts_segments',$rec->{'ID_segments'}, 'Name') : 'N/A';

			## Name Model

			if ($rec->{'ID_products'} =~/^4/){

				## Part
				$link_cmd = 'mer_parts';
				$id_products = ( $rec->{'ID_products'} - 400000000 );
				$name = &load_db_names('sl_parts','ID_parts',$id_products,'[Model]<br>[Name]');


			}elsif($rec->{'ID_products'} =~/^5/){

				## Non Inventory
				$link_cmd = 'mer_noninventory';
				$id_products = ( $rec->{'ID_products'} - 500000000 );
				$name = &load_db_names('sl_noninventory','ID_noninventory',$id_products,'[Name]');
			
				#########
				######### Segment
				$link_overlay_segment = $in{'status'} eq 'New' ?  "   	 	<a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_po_items_segment&id_po=$rec->{'ID_purchaseorders'}&id_row=$rec->{'ID_purchaseorders_items'}&ids=$rec->{'ID_segments'}' rel='#overlay' style='text-decoration:none' title='Choose Segment'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit' title='Edit' border='0'></a>&nbsp;&nbsp;" : '';


			}elsif($rec->{'ID_products'} =~/^6/){
				$link_cmd = 'mer_services';
				$id_products = ( $rec->{'ID_products'} - 600000000 );
				$name = &load_db_names('sl_services','ID_services',$id_products,'[Name]');
				# &cgierr($id_products);
			}


			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top' nowrap>";
			if ($rec->{'Received'} == 0 and $authby == 0){
				$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}&tab=1&vdrop=$rec->{'ID_purchaseorders_items'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>|;
			}
			(!$rec->{'VendorSKU'}) and ($rec->{'VendorSKU'} = '---');

			
			$va{'searchresults'} .= qq| <a href="$script_url?cmd=$link_cmd&view=$id_products"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_view.gif' title='View' alt='' border='0'></a>|;
			$va{'searchresults'} .= "   </td>\n";	
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'VendorSKU'} / $nsegment $link_overlay_segment</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$name </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Qty'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".($rec->{'Tax_percent'}*100)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top' $color>$rec->{'Received'}</td>\n";
			
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'> ".&format_price($rec->{'Price'}*$rec->{'Qty'})."</td>\n";
			
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'> ".&format_price($rec->{'Tax'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'> ".&format_price($rec->{'Total'})."</td>\n";
			
			$va{'searchresults'} .= "</tr>\n";
			$tot_qty += $rec->{'Qty'};
			#$tot_po +=$rec->{'Price'}*$rec->{'Qty'};
			$tot_po += $rec->{'Total'};
			$tax_po += $rec->{'Tax'};
			$subtot_po += ($rec->{'Price'}*$rec->{'Qty'});
		}

		$va{'searchresults'} .= qq|
			<tr>
				<td colspan="11"><hr class="menu_bar_title"></td>
			</tr>						
			<tr>
				<td colspan='9' align="right" class='smalltext' nowrap>|.&format_price($subtot_po).qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tax_po).qq|</td>
				<!-- <td class='smalltext' align="right">|.&trans_txt('mer_po_total').qq|</td> -->
				<td align="right" class='smalltext' nowrap>|.&format_price($tot_po).qq|</td>
			</tr>\n|;
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='10' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : ADJUSTMENTS
##############################################

	my ($err,$item,$query);
	my ($authby) = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	$in{'status'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Status') if (!$in{'status'});
	my ($permadj) = &check_permissions('mer_po_adjustments','','');
	if($in{'drop'} and ($permadj or $authby)){
		$va{'tabmessages'} = &trans_txt('mer_po_adj_del');
		my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_adj WHERE ID_purchaseorders_adj='$in{'drop'}'");
		$va{'searchresults'} .= "<script language=\"JavaScript1.2\">\ntrjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&tab=2&tabmessages=$va{'tabmessages'}')\n</script>";
		&auth_logging('mer_po_adj_del',$in{'id_purchaseorders'});
	}
	
	$in{'type'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Type');

	if( !$permadj and ($authby or $in{'type'} eq 'Return to Vendor') or $in{'status'} eq 'Received' or $in{'status'} eq 'Cancelled') {

		###################
		###################
		### PO Authorized or Return to Vendor
		###################
		###################

		$va{'po_blocked_start'} = '<!--';
		$va{'po_blocked_end'} = '-->';

		$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;

	}else{


		## LIST
		my ($choices_on,$tot_qty,$tot_po,$vendor_sku);
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		$va{'matches'} = $sth->fetchrow;

		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_adj DESC;");
			while ($rec = $sth->fetchrow_hashref) {
				$d = 1 - $d;
				my $id_products_code = substr($rec->{'ID_products'},0,3) .'-'.substr($rec->{'ID_products'},3,3);
				my $vname = &load_name('sl_vendors', 'ID_vendors', $rec->{'ID_vendors'}, 'CompanyName');

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				my ($drop_item) = '';
				$drop_item = "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}&tab=2&drop=$rec->{'ID_purchaseorders_adj'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>"
						if (($authby or $permadj) and $rec->{'Validate'} == 0);
				
				$va{'searchresults'} .= "   <td class='smalltext'>".$drop_item."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Type'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$vname <a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}'>( $rec->{'ID_vendors'} )</a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Description'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount_original'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Tax'})." (".($rec->{'Tax_percent'}*100)." %)</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				$tot_po += $rec->{'Total'};
			}

			$va{'searchresults'} .= qq|
				<tr>
					<td colspan='6' class='smalltext' align="right">|.&trans_txt('mer_po_total').qq|</td>
					<td align="right" class='smalltext'>|.&format_price($tot_po).qq|</td>
				</tr>\n|;

		}else{

			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;

		}
		$in{'tax_percent'} = $cfg{'taxp_default'} * 100 if !$in{'tax_percent'};

	}


}


sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : SHIPPING INSTRUCTIONS
##############################################
	
	## ADD
	if ($in{'action'}){
		if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('reqfields');
		}else{
			$va{'tabmessages'} = &trans_txt('mer_purchaseorders_noteadded');
			my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_shipping SET id_purchaseorders='$in{'id_purchaseorders'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			delete($in{'notes'});
			delete($in{'notestype'});
			&auth_logging('mer_purchaseorders_shpnoteadded',$in{'id_purchaseorders'});
		}
		
	## DROP	
	}elsif($in{'drop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_shipping WHERE ID_purchaseorders_shipping='$in{'drop'}'");
		&auth_logging('mer_purchaseorders_shpnotedeleted',$in{'id_purchaseorders'});
		$va{'tabmessages'} = &trans_txt('mer_purchaseorders_shpnotedeleted');
	}
	
	## Notes
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_shipping WHERE id_purchaseorders='$in{'id_purchaseorders'}' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_purchaseorders_shipping,admin_users WHERE id_purchaseorders='$in{'id_purchaseorders'}' AND sl_purchaseorders_shipping.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_purchaseorders_shipping DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_purchaseorders_shipping,admin_users WHERE id_purchaseorders='$in{'id_purchaseorders'}' AND sl_purchaseorders_shipping.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_purchaseorders_shipping DESC LIMIT $first,$usr{'pref_maxh'};");
		}
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq| <td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}&tab=3&drop=$rec->{'ID_purchaseorders_shipping'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>|;
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
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



sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab4 : AUTHORIZATION
##############################################


	my($sth) = &Do_SQL("SELECT Status FROM sl_purchaseorders WHERE id_purchaseorders='$in{'id_purchaseorders'}'");
	$status = $sth->fetchrow;	
	## ADD
	
	$in{'type'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Type');
	my $authby = &load_name("sl_purchaseorders","ID_purchaseorders",$in{'id_purchaseorders'},"AuthBy");

	### PO Authorized Already
	if ( $authby > 0 or $status ne 'New' ) {

		$va{'strdel_start'} = "<!--";
		$va{'strdel_end'} = "-->";
		
	}else{

		### ID_warehouses. Exclusive of Return to vendor option
		my ($sth) = &Do_SQL("SELECT Currency FROM sl_vendors INNER JOIN sl_purchaseorders USING(ID_vendors) WHERE ID_purchaseorders = '$in{'id_purchaseorders'}';");
		my ($vendor_currency) = $sth->fetchrow();

		$va{'rvendor_style'} = $in{'type'} eq 'Return to Vendor' ? '' : qq|style="display:none;"|;
		$va{'rvendor_currency'} = ($cfg{'acc_default_currency'} and $cfg{'acc_default_currency'} ne $vendor_currency) ?
									qq|Exchange Rate &nbsp;&nbsp;<input type="text" name="currency_exchange" value="[in_currency_exchange]" size="10" onFocus='focusOn( this )' onBlur='focusOff( this )'><br><br>| :
									qq|<input type="hidden" name="currency_exchange" value="1"><br><br>|;

		## ToDo. Se debe permitir ingresar un valor para el Currency Exchange? EL valor ya esta en pesos, deberia no necesitarse
		#$va{'rvendor_currency'} = qq|<input type="hidden" name="currency_exchange" value="1"><br><br>|;

		## LIST
		my ($query);
		if ($in{'filter'}){
			$query = "AND Type='".&filter_values($in{'filter'})."' ";
			$va{'query'} = $in{'filter'};
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_auth WHERE id_purchaseorders='$in{'id_purchaseorders'}' $query");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT sl_purchaseorders_auth.Date as mDate, sl_purchaseorders_auth.Time as mTime,sl_purchaseorders_auth.ID_admin_users,sl_purchaseorders_auth.Type, sl_purchaseorders_auth.Notes, admin_users.Firstname, admin_users.LastName  FROM sl_purchaseorders_auth,admin_users WHERE id_purchaseorders='$in{'id_purchaseorders'}' AND sl_purchaseorders_auth.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_purchaseorders_auth DESC LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$rec->{'Notes'} =~ s/\n/<br>/g;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}


	}
	
	

}

sub load_tabs5 {
# --------------------------------------------------------
##############################################
## tab5 : BILLS
##############################################
# Last Modified RB: 05/15/09  16:35:25 -- Si el producsto es un Set, se cargan sus partes
	my ($authby,$err,$item,$d);
	
	## ITEMS LIST
	my ($choices_on,$tot_qty,$tot_po,$vendor_sku,$name);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills_pos LEFT JOIN sl_bills ON sl_bills.ID_bills=sl_bills_pos.ID_bills WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_bills_pos DESC;");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("
			SELECT bills.ID_bills,CompanyName, bills.BillDate, bills.DueDate, bills.Status, bills.Amount, bills.AuthToPay
			FROM (
					SELECT sl_bills.ID_bills, sl_vendors.CompanyName, sl_bills.BillDate, sl_bills.DueDate, sl_bills.Status, sl_bills.Amount, sl_bills.AuthToPay
					FROM sl_bills
						INNER JOIN sl_vendors ON sl_bills.ID_vendors=sl_vendors.ID_vendors
						INNER JOIN sl_bills_pos ON sl_bills_pos.ID_bills = sl_bills.ID_bills						
					WHERE sl_bills_pos.ID_purchaseorders = ".$in{'id_purchaseorders'}." 
					
					UNION
					
					SELECT DISTINCT sl_bills.ID_bills, sl_vendors.CompanyName, sl_bills.BillDate, sl_bills.DueDate, sl_bills.Status, sl_bills.Amount, sl_bills.AuthToPay
					FROM sl_bills
						INNER JOIN sl_vendors ON sl_bills.ID_vendors=sl_vendors.ID_vendors
						INNER JOIN sl_bills_pos ON sl_bills_pos.ID_bills = sl_bills.ID_bills
						INNER JOIN sl_purchaseorders_adj ON sl_purchaseorders_adj.ID_purchaseorders_adj = sl_bills_pos.ID_purchaseorders_adj
					WHERE sl_purchaseorders_adj.ID_purchaseorders = ".$in{'id_purchaseorders'}."
			)bills
			ORDER BY bills.ID_bills DESC;"
		);
		### PO Type
		$in{'type'} = &load_name('sl_purchaseorders', 'ID_purchaseorders', $in{'id_purchaseorders'}, 'Type') if( !$in{'type'} );
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq| <td class='smalltext'>|;
			$va{'searchresults'} .= qq| 	<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}\">$rec->{'ID_bills'}</a> |;
			$va{'searchresults'} .= qq| </td> |;
			$va{'searchresults'} .= qq| <td class='smalltext'>|;
			if( int($rec->{'AuthToPay'}) == 0 and $in{'type'} eq 'PO Services' ){
				$va{'searchresults'} .= qq| 	<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&id_bills=$rec->{'ID_bills'}&bill_auth_topay=1&tab=5&tabs=1\" onclick=\"return confirm('Est&aacute; seguro de autorizar este Bill para pago?');\"><img src=\"/sitimages/default/b_pauth.gif\" alt="AuthToPay" /></a> |;
			}
			$va{'searchresults'} .= qq| </td> |;
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'CompanyName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'BillDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'DueDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_price($rec->{'Amount'})."</td>\n";			
			$va{'searchresults'} .= "</tr>\n";
			$tot_po += $rec->{'Amount'};
		}

		$va{'searchresults'} .= qq|
			<tr>
				<td colspan="7"><hr class="menu_bar_title"></td>
			</tr>						
			<tr>
				<td colspan='5' class='smalltext' align="left">[va_tabmessages]</td>
				<td class='smalltext' align="right">|.&trans_txt('mer_po_total').qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tot_po).qq|</td>
			</tr>\n|;
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

sub load_tabs6 {
# --------------------------------------------------------
##############################################
## tab6 : WRECEIPTS
##############################################

	my ($sth) = &Do_SQL("SELECT ID_products FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");
	my ($aux_rec);
	my $aux_type = '';
	$va{'style_supplies'} = 'display: none;';
	$va{'style_services'} = 'display: none;';
	$va{'style_skus'} = '';
	
	while ($aux_rec = $sth->fetchrow_hashref) {
		if ($aux_rec->{'ID_products'} =~ /^5/){
			$aux_type = 'supplies';
			$va{'style_skus'} = 'display: none;';
			$va{'style_supplies'} = '';
		}elsif($aux_rec->{'ID_products'} =~ /^6/){
			$aux_type = 'services';
			$va{'style_skus'} = 'display: none;';
			$va{'style_services'} = '';
		}
	}
	
	if ($aux_type eq 'supplies') {
		############################################
		### Supplies
		############################################
		
		if ($usr{'application'} eq 'admin') {
			my $old_received;
			my $po_id_product;
			my $po_id;
			my $max_received;
			my $id_noninventory;
			my $trows = 0;
			
			$va{'rpolist'} = '';
			$va{'polistwr'} = '';
			$va{'received'} = &trans_txt('mer_po_received_list');
			$va{'fset_receipts'} = &trans_txt('mer_po_pending_receipts');
			
			my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}';");
			if ($sth1->fetchrow>0){
				my ($sth2) = &Do_SQL("SELECT sl_purchaseorders_items.*, ID_noninventory, (Qty - Received) as MaxRec, Name FROM sl_purchaseorders_items INNER JOIN sl_noninventory ON ID_noninventory = ID_products - 500000000  WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC;");

				while ($rec = $sth2->fetchrow_hashref){
					
					my $input_status = ($rec->{'Qty'} == 0)?'disabled="disabled"':'';

					if($rec->{'Received'} > 0) {
						
						$va{'rpolist'} .= '<tr>';
						$va{'rpolist'} .= qq|<td><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_noninventory&view=$id_noninventory&second_conn=0'>|;
						$va{'rpolist'} .= &format_sltvid($rec->{ID_products});
						$va{'rpolist'} .= '</a></td>';
						
						$va{'rpolist'} .= '<td>';
						$va{'rpolist'} .= $rec->{Name};
						$va{'rpolist'} .= '</td>';

						$va{'rpolist'} .= '<td align="center">';
						$va{'rpolist'} .= $rec->{'Qty'};
						$va{'rpolist'} .= '</td>';
						
						$va{'rpolist'} .= '<td align="right">';
						$va{'rpolist'} .= $rec->{'Received'};
						$va{'rpolist'} .= '</td>';

					}else{
					
						$va{'pageslist'} = 1;
						$va{'rpolist'} = qq|<tr>
											<td colspan='3' align='center'>|.&trans_txt('search_nomatches').qq|</td>
										</tr>\n|;
					}
					
					$old_received = $rec->{'Received'};
					$po_id_product = $rec->{'ID_products'};
					$po_id = $rec->{'ID_purchaseorders'};
					$max_received = $rec->{'quantity'};
					
					if($rec->{'MaxRec'} > 0) {
					
						++$trows;

						$va{'polistwr'} .= '<tr>';

						$va{'polistwr'} .= '<td>';
						$va{'polistwr'} .= &format_sltvid($rec->{ID_products});
						$va{'polistwr'} .= '</td>';
						
						$va{'polistwr'} .= '<td>';
						$va{'polistwr'} .= $rec->{'Name'};
						$va{'polistwr'} .= '</td>';

						$va{'polistwr'} .= '<td align="center">';
						$va{'polistwr'} .= $rec->{'MaxRec'};
						$va{'polistwr'} .= '</td>';

						my $tmp_value = (!$in{'id_purchaseorders_items_'.$rec->{'ID_purchaseorders_items'}})? $rec->{'MaxRec'}:$in{'id_purchaseorders_items_'.$rec->{'ID_purchaseorders_items'}};
						$va{'polistwr'} .= '<td align="right">';
						$va{'polistwr'} .= qq|<input type='text' value="$tmp_value" name="id_purchaseorders_items_$rec->{'ID_purchaseorders_items'}" id="id_purchaseorders_items_$rec->{'ID_purchaseorders_items'}" $input_status />|;
						$va{'polistwr'} .= '</td>';
						
			
						
						$va{'polistwr'} .= '</tr>';
					}

				}
				
			}	
			$va{'style_form_supplies'} = 'display: none;' if (!$trows or !(&load_name("sl_purchaseorders","ID_purchaseorders",$in{'id_purchaseorders'},"AuthBy") > 0));
		}
	
	} elsif( $aux_type eq 'services' ){
		############################################
		### Services
		############################################

		if ($usr{'application'} eq 'admin') {
			my $trows = 0;
			$va{'rpolist'} = '';
			$va{'polistwr'} = '';

			my ($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}';");
			if ($sth1->fetchrow>0){
				my ($sth2) = &Do_SQL("SELECT sl_purchaseorders_items.*, ID_services, (Qty - Received) as MaxRec, Name 
										FROM sl_purchaseorders_items 
											INNER JOIN sl_services ON ID_services = ID_products - 600000000  
										WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' 
										ORDER BY ID_purchaseorders_items DESC;");

				while ($rec = $sth2->fetchrow_hashref){
					my $input_status = ($rec->{'Qty'} == 0)?'disabled="disabled"':'';

					if($rec->{'Received'} > 0) {
						
						$va{'rpolist'} .= '<tr>';
						$va{'rpolist'} .= qq|<td><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=$rec{'ID_services'}&second_conn=0'>|;
						$va{'rpolist'} .= &format_sltvid($rec->{ID_products});
						$va{'rpolist'} .= '</a></td>';
						
						$va{'rpolist'} .= '<td>';
						$va{'rpolist'} .= $rec->{Name};
						$va{'rpolist'} .= '</td>';

						$va{'rpolist'} .= '<td align="center">';
						$va{'rpolist'} .= $rec->{'Qty'};
						$va{'rpolist'} .= '</td>';
						
						$va{'rpolist'} .= '<td align="right">';
						$va{'rpolist'} .= $rec->{'Received'};
						$va{'rpolist'} .= '</td>';

					}else{
					
						$va{'pageslist'} = 1;
						$va{'rpolist'} = qq|<tr>
											<td colspan='3' align='center'>|.&trans_txt('search_nomatches').qq|</td>
										</tr>\n|;
					}			
					
					
					if($rec->{'MaxRec'} > 0) {
					
						++$trows;

						$va{'polistwr'} .= '<tr>';

						$va{'polistwr'} .= '<td>';
						$va{'polistwr'} .= &format_sltvid($rec->{ID_products});
						$va{'polistwr'} .= '</td>';
						
						$va{'polistwr'} .= '<td>';
						$va{'polistwr'} .= $rec->{'Name'};
						$va{'polistwr'} .= '</td>';

						$va{'polistwr'} .= '<td align="center">';
						$va{'polistwr'} .= $rec->{'MaxRec'};
						$va{'polistwr'} .= '</td>';

						my $tmp_value = (!$in{'id_purchaseorders_items_'.$rec->{'ID_purchaseorders_items'}})? $rec->{'MaxRec'}:$in{'id_purchaseorders_items_'.$rec->{'ID_purchaseorders_items'}};
						$va{'polistwr'} .= '<td align="right">';
						$va{'polistwr'} .= qq|<input type='text' value="$tmp_value" name="id_purchaseorders_items_$rec->{'ID_purchaseorders_items'}" id="id_purchaseorders_items_$rec->{'ID_purchaseorders_items'}" $input_status />|;
						$va{'polistwr'} .= '</td>';
						
			
						
						$va{'polistwr'} .= '</tr>';
					}

				}
			}
		}

		$va{'style_form_services'} = 'display: none;' if (!$trows or !(&load_name("sl_purchaseorders","ID_purchaseorders",$in{'id_purchaseorders'},"AuthBy") > 0));

	} else {
		############################################
		### SKUs
		############################################

		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts INNER JOIN sl_wreceipts_items ON sl_wreceipts.ID_wreceipts = sl_wreceipts_items.ID_wreceipts WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			if ($in{'print'}){
				$sth = &Do_SQL("SELECT sl_wreceipts_items.* FROM sl_wreceipts
													INNER JOIN sl_wreceipts_items ON sl_wreceipts.ID_wreceipts = sl_wreceipts_items.ID_wreceipts
													WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_wreceipts_items;");
			}else{
				(!$in{'nh'}) and ($in{'nh'}=1);
				$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
				($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
				$sth = &Do_SQL("SELECT sl_wreceipts_items.* FROM sl_wreceipts
														INNER JOIN sl_wreceipts_items ON sl_wreceipts.ID_wreceipts = sl_wreceipts_items.ID_wreceipts
														WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_wreceipts_items LIMIT $first,$usr{'pref_maxh'};");			
			}
			
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_wreceipts&view=".$rec->{'ID_wreceipts'}."&second_conn=0'>".$rec->{'ID_wreceipts'}."</a></td>\n";
				if(substr($rec->{'ID_products'},0,1) eq '4'){ 
					$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_parts&view=".($rec->{'ID_products'} - 400000000)."&tab=3'>".format_sltvid($rec->{'ID_products'})."</a></td>\n";
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_products&view=".($rec->{'ID_products'} - 100000000)."&tab=3'>".format_sltvid($rec->{'ID_products'})."</a></td>\n";
				}	
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Qty'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
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

	$va{'id_vendor'} = &load_db_names('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'[id_vendors]');
	$va{'vendor_currency'} = &load_db_names('sl_vendors','ID_vendors',$va{'id_vendor'},'[currency]');
	if($va{'vendor_currency'} eq $cfg{'acc_default_currency'}){
		$va{'displaydate'} = 'display:none;';
	}
	
}


sub load_tabs7 {	
# --------------------------------------------------------
##############################################
## tab7 : POs
##############################################
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders,sl_purchaseorders_items 
											WHERE sl_purchaseorders.ID_purchaseorders =  sl_purchaseorders_items.ID_purchaseorders
											AND sl_purchaseorders.ID_purchaseorders != '$in{'id_purchaseorders'}' AND ID_products IN 
											(SELECT ID_products FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}') ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_purchaseorders.* FROM sl_purchaseorders,sl_purchaseorders_items 
											WHERE sl_purchaseorders.ID_purchaseorders =  sl_purchaseorders_items.ID_purchaseorders
											AND sl_purchaseorders.ID_purchaseorders != '$in{'id_purchaseorders'}' AND ID_products IN 
											(SELECT ID_products FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}')
											ORDER BY sl_purchaseorders.ID_purchaseorders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_purchaseorders.* FROM sl_purchaseorders,sl_purchaseorders_items 
												WHERE sl_purchaseorders.ID_purchaseorders =  sl_purchaseorders_items.ID_purchaseorders
												AND sl_purchaseorders.ID_purchaseorders != '$in{'id_purchaseorders'}' AND ID_products IN 
												(SELECT ID_products FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}')
												ORDER BY sl_purchaseorders.ID_purchaseorders DESC LIMIT $first,$usr{'pref_maxh'};");			
		}

		while ($rec = $sth->fetchrow_hashref){
			$warehouse_name = &load_name("sl_warehouses","ID_warehouses",$rec->{'ID_warehouses'},"Name");
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";						
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PODate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'POTerms'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='$script_url?cmd=opr_warehouse&view=$rec->{'ID_warehouses'}'>$warehouse_name</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Auth'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
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




1;