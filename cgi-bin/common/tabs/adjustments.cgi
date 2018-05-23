#####################################################################
########                   ADJUSTMENTS                   		#########
#####################################################################


sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_adjustments_notes';
	}elsif($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_adjustments';
	}elsif($in{'tab'} eq 5){
		## Movs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_adjustments';
		$va{'tab_idvalue'} = $in{'id_adjustments'};
	}
}

sub load_tabs1 {
# --------------------------------------------------------
# Last Modification by JRG : 03/04/2009 : Se quita navegacion para imprimir y se modifica el log
# Last Modified on: 04/15/09 15:29:40
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda ajustar un inventario a cantidad 0
# Last Modified on: 06/08/09 16:18:31
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para no permitir sets.
##############################################
## tab1 : ITEMS
##############################################

	my $linkprod = 'mer_products';
	my $linkpart = 'mer_parts';	
	
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($name,$stlink);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_adjustments_items WHERE id_adjustments='$in{'id_adjustments'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_adjustments_items WHERE id_adjustments='$in{'id_adjustments'}' ORDER BY ID_products DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_adjustments_items WHERE id_adjustments='$in{'id_adjustments'}' ORDER BY ID_products DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
		
			($in{'status'} ne 'Approved') and ($rec->{'Adj'} = 'TBD');
			($in{'status'} ne 'Approved') ? ($rec->{'Price'} = 'TBD'):($rec->{'Price'} = &format_price($rec->{'Price'}));
			($rec->{'Adj'} eq '0') and ($rec->{'Price'} = &format_price(0));
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$linkpart&view=".($rec->{'ID_products'}-400000000) ."'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".&load_db_names('sl_parts','ID_parts',($rec->{'ID_products'}-400000000),'[Model]<br>[Name]')."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$rec->{'ID_warehouses'}\">$rec->{'ID_warehouses'}</a></td>n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_locations&search=Search&id_warehouses=$rec->{'ID_warehouses'}&Code=$rec->{'Location'}\">$rec->{'Location'}</a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top' align='right'>$rec->{'Qty'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top' align='right'>$rec->{'Adj'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'' valign='top' align='right' nowrap>$rec->{'Price'}</td>\n";
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


sub load_tabs2_run {
# --------------------------------------------------------
# Last Modification by JRG : 03/04/2009 : Se agrega el log
##############################################
## tab2 : UPLOAD FILE
##############################################

	if ($in{'status'} eq 'New'){
		if (open (FILE, "<$cfg{'path_upfiles'}adjustments/$in{'id_adjustments'}.txt")){
			my ($sth) = &Do_SQL("DELETE FROM sl_adjustments_items WHERE ID_adjustments='$in{'id_adjustments'}';");
			&auth_logging('sl_adjustments_itemsdeleted',$in{'id_adjustments'});
			my (@ary);
			LINE: while (<FILE>) {
				(/^#/)      and next LINE;
				(/^\s*$/)   and next LINE;
				@ary = split(/\t/,$_);
				$tot = $#ary;
				if ($#ary >= 3){
					next LINE if $ary[0] =~ /^6/;
					$ary[0] =~ s/-//g;
					(length($ary[0])<9) and ($ary[0] = "100$ary[0]");
					($ary[1] < 0) and ($ary[1] = 0);
					### Checking Valid Location
					my ($sth) = &Do_SQL("SELECT ID_locations FROM sl_locations WHERE ID_warehouses='$ary[3]' AND Code='$ary[4]' AND Status='Active'");
					if ($sth->fetchrow >0){
						########################
						my ($sth) = &Do_SQL("INSERT INTO sl_adjustments_items SET ID_adjustments='$in{'id_adjustments'}',ID_warehouses='$ary[3]',Location='$ary[4]',ID_products='$ary[0]',Qty='$ary[1]',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
					}
				}
			}
			$va{'tabmessage'} = 'File processed Succesfully';
			&auth_logging('adjustment_fileprocessed',$in{'id_adjustments'});
		}else{
			$va{'tabmessage'} = 'Unable to open the File'. $!;
		}
	}elsif ($in{'status'} ne 'New'){
		$va{'tabmessage'} = 'The File was already processed';
	}elsif (-e "$cfg{'path_upfiles'}adjustments/$in{'id_adjustments'}.txt"){
		$va{'tabmessage'} = 'The File for this Adjustment Has been already uploaded';
	}

	
	## Tables Header/Titles
	$va{'keyname'} = '';
}


sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab2 : UPLOAD FILE
##############################################
	
	# Left empty, there's no need for code here
	
	## Tables Header/Titles
	$va{'keyname'} = '';
}


1;