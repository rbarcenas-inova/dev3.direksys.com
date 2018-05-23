#####################################################################
########                   NON INVENTORY	                   ########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_wreceipts_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_wreceipts';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
	## Items List				
	my ($err,$item);	
	my ($choices_on,$tot_qty,$vendor_sku);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts_items WHERE ID_wreceipts='$in{'id_wreceipts'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT ID_wreceipts, ID_wreceipts_items, sl_wreceipts_items.ID_products AS ID_products, Model, Name, sl_wreceipts_items.Qty, Price
		FROM sl_wreceipts 
		INNER JOIN sl_wreceipts_items USING(ID_wreceipts)
		INNER JOIN sl_parts ON ID_products = 400000000 + sl_parts.ID_parts 
		INNER JOIN sl_purchaseorders_items USING(ID_purchaseorders) 
		WHERE ID_wreceipts = '$in{'id_wreceipts'}'
		AND sl_purchaseorders_items.ID_products = sl_wreceipts_items.ID_products
		AND sl_wreceipts_items.ID_products LIKE '4%'
		GROUP BY ID_wreceipts_items ORDER BY ID_wreceipts_items DESC ;");

		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			#$status_wreceipt = &load_name('sl_wreceipts','ID_wreceipts',$rec->{'ID_wreceipts'},'Status');
			(!$rec->{'Serial'}) and ($rec->{'Serial'} = '---');
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>";
			if (!$va{'block_edition'}) {
				$va{'searchresults'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_wreceipts&view=$rec->{'ID_wreceipts'}&tab=1&drop=$rec->{'ID_wreceipts_items'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Edit' alt='' border='0'></a>|;
			}
			
			$va{'searchresults'} .= "   </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='$script_url?cmd=mer_parts&view=".($rec->{'ID_products'} - 400000000)."'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Model'}<br>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>".&format_price($rec->{'Price'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Qty'})."</td>\n";
			# $va{'searchresults'} .= "   <td class='smalltext'><input type='text' name='rcp[]' value='".$rec->{'RcpQty'}."' > </td>\n";			
			$va{'searchresults'} .= "</tr>\n";
			$tot_qty += $rec->{'Qty'};
			$tot_po +=$rec->{'SPrice'}*$rec->{'Qty'};
		}
		
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='4' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' style="border-top:thick double #808080;">$tot_qty</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;