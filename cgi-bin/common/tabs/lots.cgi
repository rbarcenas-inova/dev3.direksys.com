#!/usr/bin/perl
#####################################################################
########                   Lots	      		    #########
#####################################################################
sub load_tabsconf {
	if ($in{'tab'} eq 1){
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_lots';
	}
}

#########################################################	
#	Function: 
#   	load_tabs2
#	Description:
#		Es: Inicializa el tab items solo si el lot es tipo Custom
#		En: Initialize the item tab only if the lot is custom type
#
#	Created by:
#		Josue Miranda
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub load_tabs2{

	my ($sth) = &Do_SQL("SELECT Type, Status FROM sl_lots WHERE ID_lots='".$in{'id_lots'}."';");
	
	while ($type=$sth->fetchrow_hashref){
	$type_val=$type->{'Type'};
	$status_val=$type->{'Status'};
	}

	if($type_val eq "Vendor"){
		$va{'display_tab'}='display:none;';
	}

	if($status_val ne "New"){
		$va{'edit_validation'}='display:none;';
	}else{
		$va{'addorder'} = qq| <a style='font-size: 12px;font-weight:600;' href=\"/cgi-bin/common/apps/schid?cmd=lots_additem&id_lots=[in_id_lots]&path=[va_script_url]&cmdo=[in_cmd]&dototemp=YES\" title=\"List Item\" class=\"fancy_modal_iframe\">
		Add Item</a><a name='top' id='top'>|;
	}
		
	

	($sth) = &Do_SQL("SELECT c.*, i.Status AS Status_item FROM sl_lots c, sl_lots_items i WHERE c.ID_lots=i.ID_lots_children AND c.Type='Vendor' AND i.Status='Active' AND i.ID_lots='".$in{'id_lots'}."';");
	$va{'total'} = 0;

	while ($rec = $sth->fetchrow_hashref){
		$va{'searchresults'} .= " <tr> <td class='smalltext' valign='top'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_lots&view=".($rec->{'ID_lots'})."\">". $rec->{'ID_lots'}."</a></td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$rec->{'LotName'}."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$rec->{'ExpirationDate'}."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$rec->{'Type'}."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".$rec->{'Status_item'}."</td>\n";
		if ($status_val eq "New") {
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_lots&view=".$in{'id_lots'}."&id_lots=".$in{'id_lots'}."&tab=2&action=1&dropitem=$rec->{'ID_lots'}''><img src='/sitimages//default/b_drop.png' title='Drop' alt='' border='0'></a></td></tr></tr>\n";
		}
	}
}



1;