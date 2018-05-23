#####################################################################
########                   vendors                   		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 5){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_vendors_notes';
	}elsif($in{'tab'} eq 6){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_vendors';
	}elsif($in{'tab'} eq 7){
		## Movs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_vendors';
		$va{'tab_idvalue'} = $in{'id_vendors'};
	}
}

sub load_tabs1 {
# --------------------------------------------------------
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_vendors sv
					INNER JOIN sl_parts sp ON sv.ID_parts = sp.ID_parts
					WHERE sv.id_vendors= '$in{id_vendors}' ORDER BY sp.ID_parts DESC;");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},'/cgi-bin/mod/[ur_application]/dbman',$va{'matches'},$usr{'pref_maxh'});		
		my ($sth) = &Do_SQL("SELECT * FROM sl_parts_vendors sv
					INNER JOIN sl_parts sp ON sv.ID_parts = sp.ID_parts
					WHERE sv.id_vendors= '$in{id_vendors}' ORDER BY sp.ID_parts DESC;");
		while ($rec = $sth->fetchrow_hashref){
			my $link_cmd='';
			$d = 1 - $d;

			$name =  $rec->{'Model'}."<br>".$rec->{'Name'};				
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";	
			(!$rec->{'VendorSKU'}) and ($rec->{'VendorSKU'} = '---');
			$va{'searchresults'} .= qq| <td class="smalltext" $style valign="top" align="right"  onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=$rec->{'ID_parts'}')"><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0"> |.
								&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</td>|;
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'VendorSKU'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$name </td>\n";
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

sub load_tabs2 {
# --------------------------------------------------------
	## POs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders WHERE ID_vendors='$in{'id_vendors'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},'/cgi-bin/mod/[ur_application]/dbman',$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders WHERE ID_vendors='$in{'id_vendors'}' ORDER BY ID_purchaseorders DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$warehouse_name = &load_name("sl_warehouses","ID_warehouses",$rec->{'ID_warehouses'},"Name");
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}'>$rec->{'ID_purchaseorders'}</a></td>\n";						
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PODate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'POTerms'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouse&view=$rec->{'ID_warehouses'}'>$warehouse_name</a></td>\n";
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
	
	## Tables Header/Titles
	$va{'keyname'} = 'POs';
	&load_db_fields_values($in{'db'},'ID_vendors',$in{'id_vendors'},'*');
}

#############################################################################
#############################################################################
#   Function: load_tabs3
#
#       Es: Listado de Pagos realizados al Proveedor
#       En: Payments List to Vendor
#
#
#    Created on: 26/06/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - 
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub load_tabs3{
#############################################################################
#############################################################################
	########## Listado de Payments

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_banks_movements
		INNER JOIN sl_banks_movrel USING(ID_banks_movements)
		INNER JOIN sl_bills ON sl_banks_movrel.tablename='bills' AND sl_banks_movrel.tableid=sl_bills.ID_bills
		INNER JOIN sl_banks USING(ID_banks)
		WHERE sl_banks_movements.Type='Credits'
		AND (SELECT COUNT(*) FROM sl_banks_movements_notes WHERE sl_banks_movements_notes.ID_banks_movements=sl_banks_movements.ID_banks_movements)=0
		AND ID_vendors = '$in{'id_vendors'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},'/cgi-bin/mod/[ur_application]/dbman',$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT 
		sl_banks_movements.ID_banks_movements
		, sl_banks_movements.BankDate
		, sl_banks_movements.Amount
		, sl_banks_movements.AmountCurrency
		, sl_banks_movements.currency_exchange
		, ifnull(sl_banks_movements.RefNumCustom,sl_banks_movements.RefNum)RefNum
		, sl_banks_movements.Type
		, sl_banks_movements.doc_type
		, sl_banks_movements.Memo
		, sl_banks.Name BankName
		, sl_banks.SubAccountOf
		, sl_banks.Currency
		FROM sl_banks_movements
		INNER JOIN sl_banks_movrel USING(ID_banks_movements)
		INNER JOIN sl_bills ON sl_banks_movrel.tablename='bills' AND sl_banks_movrel.tableid=sl_bills.ID_bills
		INNER JOIN sl_banks USING(ID_banks)
		WHERE sl_banks_movements.Type='Credits'
		AND (SELECT COUNT(*) FROM sl_banks_movements_notes WHERE sl_banks_movements_notes.ID_banks_movements=sl_banks_movements.ID_banks_movements)=0
		AND ID_vendors = '$in{'id_vendors'}' ORDER BY sl_banks_movements.BankDate DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$warehouse_name = &load_name("sl_warehouses","ID_warehouses",$rec->{'ID_warehouses'},"Name");
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=fin_banks_movements&view=$rec->{'ID_banks_movements'}'>$rec->{'ID_banks_movements'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'BankDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'BankName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>$rec->{'SubAccountOf'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'doc_type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'RefNum'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Currency'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
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


sub load_tabs4{
#
# Statistics
#

	my ($sth) = &Do_SQL("SELECT SUM(Price*Qty) FROM sl_purchaseorders,sl_purchaseorders_items WHERE sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND ID_vendors='$in{'id_vendors'}';");
	$va{'totpurchases'} = &format_price($sth->fetchrow);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders,sl_purchaseorders_items WHERE sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND ID_vendors='$in{'id_vendors'}';");
	$va{'totqpurchases'} = &format_number($sth->fetchrow);
	my ($sth) = &Do_SQL("SELECT Date,ID_purchaseorders FROM sl_purchaseorders WHERE ID_vendors='$in{'id_vendors'}' ORDER BY Date DESC LIMIT 0,1;");
	($va{'lastpo'},$va{'idlastpo'}) = $sth->fetchrow_array();
	my ($sth) = &Do_SQL("SELECT SUM(Price*Qty) FROM sl_purchaseorders,sl_purchaseorders_items WHERE sl_purchaseorders.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND sl_purchaseorders.ID_purchaseorders='$va{'idlastpo'}';");
	$va{'amnlastpo'} = &format_price($sth->fetchrow);
	
}


sub load_tabs8 {
# --------------------------------------------------------
	## POs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_bills WHERE ID_vendors = '$in{'id_vendors'}';");
	$va{'matches'} = $sth->fetchrow;
	
	if ($va{'matches'}>0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},'/cgi-bin/mod/[ur_application]/dbman',$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_bills WHERE ID_vendors = '$in{'id_vendors'}' ORDER BY ID_bills DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){

		
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=mer_bills&view=$rec->{'ID_bills'}'>$rec->{'ID_bills'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Invoice'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Currency'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'DueDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align = 'right'>$rec->{'Amount'}</td>\n";
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
	
	## Tables Header/Titles
	$va{'keyname'} = 'POs';
	&load_db_fields_values($in{'db'},'ID_vendors',$in{'id_vendors'},'*');
}


1;