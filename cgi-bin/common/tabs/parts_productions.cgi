#####################################################################
########                   SKUS PRODUCTIONS                   		#########
#####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_parts_productions_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_parts_productions';
	}

}


sub load_tabs1 {
##############################################
## tab1 : ITEMS
##############################################

	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($name,$stlink);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts_productions_items WHERE ID_parts_productions='$in{'id_parts_productions'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			my ($sth) =  &Do_SQL("SELECT sl_parts_productions_items.ID_products, sl_parts.Name, Location,Qty, In_out,
						IF( UPC IS NOT NULL, UPC , 'N/A')
	                    FROM sl_parts INNER JOIN sl_parts_productions_items
	                    ON ID_parts = RIGHT(sl_parts_productions_items.ID_products,4) 
	                    LEFT JOIN sl_skus ON sl_parts_productions_items.ID_products = ID_sku_products
	                    WHERE ID_parts_productions = '$in{'id_parts_productions'}'
	                    ORDER BY In_out,ID_parts_productions_items;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_parts_productions_items.ID_products, sl_parts.Name, Location,Qty, In_out,
						IF( UPC IS NOT NULL, UPC , 'N/A')
	                    FROM sl_parts INNER JOIN sl_parts_productions_items
	                    ON ID_parts = RIGHT(sl_parts_productions_items.ID_products,4)
	                    LEFT JOIN sl_skus ON sl_parts_productions_items.ID_products = ID_sku_products 
	                    WHERE ID_parts_productions = '$in{'id_parts_productions'}' 
	                    ORDER BY In_out,ID_parts_productions_items LIMIT $first,$usr{'pref_maxh'};");
		}	
		
		while (my($id_products,$pname,$location,$qty,$inout,$upc) = $sth->fetchrow()){
			$d = 1 - $d;
		
			$va{'searchresults'} .= qq|<tr>\n
											<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=|.substr($id_products,-4).qq|">|.&format_sltvid($id_products).qq|</a></td>\n
											<td>$pname</td>\n
											<td align="left">$upc</td>\n
											<td align="center">$inout</td>\n
											<td align="center">$location</td>\n
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