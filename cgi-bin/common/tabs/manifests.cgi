#!/usr/bin/perl
####################################################################
########                WAREHOUSE RECEIPT                ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_manifests_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_manifests';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
# Last Modified on: 04/09/09 12:11:01
# Last Modified by: MCC C. Gabriel Varela S: Se crea columna Status
# Last Modified on: 05/20/09 16:15:05
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para poder mostrar partes y además productos con choices.
# Last Modified on: 06/01/09 17:20:30
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para validar también por ID_warehouses_location.
##############################################
## tab1 : ITEMS
##############################################

	my $linkprod = 'mer_products';
	my $linkpart = 'mer_parts';	
	
	## ITEMS LIST
	my ($choices_on,$tot_qty,$vendor_sku);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_manifests_items WHERE ID_manifests='$in{'id_manifests'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'} > 0){
		my ($sth) =  &Do_SQL("SELECT ID_manifests_items, ID_products, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_warehouse_Location,Qty, sl_manifests_items.Status
	                    FROM sl_parts INNER JOIN sl_manifests_items 
	                    ON ID_parts = RIGHT(ID_products,4) 
	                    WHERE ID_manifests = '$in{'id_manifests'}'
	                    ORDER BY ID_manifests_items;");
		while(my($idmi, $id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty, $status) = $sth->fetchrow()){

			my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
			my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');
			my $this_style = $status eq 'Failed' ? 'style="color:red"' : '';

			$va{'searchresults'} .= qq|<tr id="row-$idai" >\n
										<td align="left" $this_style>$status</td>\n 
										<td>|.&format_sltvid($id_parts).qq|</td>\n
										<td>$name</td>\n 
										<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$fwh" title="View $fwh">($fwh)</a> $fwhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$fwh&code=$from_location" title="View $from_location">$from_location</a></td>\n 
										<td><a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_warehouses&view=$twh" title="View $twh">($twh)</a> $twhname / <a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_locations&search=Search&id_warehouses=$twh&code=$to_location" title="View $to_location">$to_location</a></td>\n
										<td  align="right">$qty</td>\n 
									</tr>|;	
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
}

1;