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
		$va{'tab_table'} = 'sl_skustransfers_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_skustransfers';
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
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skustransfers_items WHERE ID_skustransfers='$in{'id_skustransfers'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'} > 0){
		my ($sth) =  &Do_SQL("SELECT ID_skustransfers_items, FromSku, ToSku,
									sl_parts.Name,(SELECT Name FROM sl_parts WHERE ID_parts = RIGHT(sl_skustransfers_items.ToSku,4)) as to_name,
									From_warehouse, From_warehouse_Location,
									To_warehouse, To_warehouse_Location,Qty
							   FROM sl_parts
							   INNER JOIN sl_skustransfers_items ON ID_parts = RIGHT(FromSku,4)
							   WHERE ID_skustransfers = '$in{'id_skustransfers'}'
							   ORDER BY ID_skustransfers_items;");
		while(my($idmi, $id_parts, $to_id_parts, $name, $to_name,$fwh, $from_location, $twh, $to_location, $qty) = $sth->fetchrow()){

			my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
			my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');

			$va{'searchresults'} .= qq|<tr id="row-$idai">\n
										<td>&nbsp;</td>\n
										<td>|.&format_sltvid($id_parts).qq|</td>\n
										<td>$name</td>\n 
										<td>|.&format_sltvid($to_id_parts).qq|</td>\n
										<td>$to_name</td>\n 
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