#!/usr/bin/perl
use Data::Dumper;
use CGI;
#####################################################################
########                   Notices	      		    #########
#####################################################################
sub load_tabsconf {
	if ($in{'tab'} eq 1){
		$va{'tab_type'}  = 'skus';
		$va{'tab_title'} = &trans_txt('skus');
		$va{'tab_table'} = 'sl_return_notices_skus';
	}elsif($in{'tab'} eq 2){
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_return_notices_notes';
	}elsif($in{'tab'} eq 3){
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_return_notices';
	}
}

sub load_tabs1{
	my ($choices_on,$tot_qty,$vendor_sku);
	my (@c) = split(/,/,$cfg{'srcolors'});


	#$my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses='$in{'id_warehouses'}'");

	my ($sth) = &Do_SQL("
		SELECT 
			COUNT(*) 
		FROM 
			sl_return_notices_skus 
		WHERE 
			ID_return_notices = '$in{'id_return_notices'}';");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my($sth) = &Do_SQL("SELECT sl_return_notices_skus.ID_return_notices_skus,
		    sl_return_notices_skus.ID_return_notices,
		    sl_return_notices_skus.ID_products,
		    sl_return_notices_skus.Qty,
		    sl_return_notices_skus.SalePrice,
		    sl_return_notices_skus.RcpQty,
		    sl_return_notices_skus.Status,
		    sl_return_notices_skus.Date,
		    sl_return_notices_skus.Time,
		    sl_return_notices_skus.ID_admin_users,
		    sl_skus.UPC,
		    sl_parts.Name
		FROM sl_return_notices_skus
		LEFT JOIN sl_parts ON (400000000+sl_parts.ID_parts)=sl_return_notices_skus.ID_products
		LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_return_notices_skus.ID_products
		WHERE ID_return_notices = '$in{'id_return_notices'}'
		ORDER BY `ID_return_notices` LIMIT $first,$usr{'pref_maxh'};");


		# my ($sth) = &Do_SQL("SELECT ID_parts,ID_products,Model,Name,SUM(Quantity) AS Quantity FROM sl_warehouses_location INNER JOIN sl_parts ON ID_parts  = RIGHT(ID_products,4)  WHERE ID_warehouses = '$in{'id_warehouses'}' GROUP BY ID_parts ORDER BY ID_parts LIMIT $first,$usr{'pref_maxh'};");
	

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my $total = $rec->{'Qty'} * $rec->{'SalePrice'};
			my $total_rec = $rec->{'RcpQty'} * $rec->{'SalePrice'};
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'><a href='/cgi-bin/mod/[ur_application]/dbman?cmd=opr_return_notices&view=$in{'id_return_notices'}&remove=1&id_return_notices_skus=$rec->{'ID_return_notices_skus'}'/>X</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'ID_return_notices_skus'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_products'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'UPC'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><input type='hidden' name='ids[]' value='$rec->{'ID_return_notices_skus'}' ><input type='text' class='update l1' name='q[]' value='".$rec->{'Qty'}."' ></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><input type='text' class='update l2' name='price[]' value='".$rec->{'SalePrice'}."' /> </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><input type='text' class='update l3' name='rcp[]' value='".$rec->{'RcpQty'}."' > </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext total1'>".&format_price($total)."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext total2'>".&format_price($total_rec)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}


}
1;