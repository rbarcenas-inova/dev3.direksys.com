#!/usr/bin/perl

##################################################################
############                HELP                 #################
##################################################################
sub inventory {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";

	(!$in{'page'}) and ($in{'page'} = 'home');
	my ($choices_on,$tot_qty,$vendor_sku);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my $data = loadDataPos();

	$id_customers = $data->{'id_admin_users'};
	$id_warehouses = $data->{'id_warehouse'};

	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(ID_products)) 
		FROM sl_warehouses_location LEFT JOIN sl_locations ON sl_locations.ID_warehouses = sl_warehouses_location.ID_warehouses 
		AND sl_locations.Code = sl_warehouses_location.Location 
		WHERE 1
		AND sl_locations.ID_warehouses = '$id_warehouses';");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'} > 0){

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		my ($sth) = &Do_SQL("SELECT ID_parts,ID_products,Model,Name,SUM(Quantity) AS Quantity 
			FROM sl_warehouses_location INNER JOIN sl_parts ON ID_parts = RIGHT( ID_products, 4 ) INNER JOIN sl_locations ON sl_locations.ID_warehouses = sl_warehouses_location.ID_warehouses 
			AND sl_locations.Code = sl_warehouses_location.Location 
			WHERE 1
			AND sl_locations.ID_warehouses = '". $id_warehouses ."'
			GROUP BY ID_parts ORDER BY ID_parts LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Model'}<br>$rec->{'Name'}</td>\n";
			#$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Location'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Quantity'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			$tot_qty += $rec->{'Quantity'};
		}
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='2' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' style="border-top:thick double #808080;">|.&format_number($tot_qty).qq|</td>
			</tr>\n|;
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	print &build_page('inventory.html');
}


##################################################################
############                ORDERS                 #################
##################################################################
sub transfers {
# --------------------------------------------------------

	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('opr_orders_home.html');
}


	
1;

