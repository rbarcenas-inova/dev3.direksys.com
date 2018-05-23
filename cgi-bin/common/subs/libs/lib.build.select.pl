#################################
##### Func Revisadas
#################################
sub build_select_table_width{
#-------------------------------------------------------------
# Last Modified RB: 04/08/09  17:36:16
		
		my (@list) = split(/,/, $cfg{'screenres'});
		$output = "<select name='table_width' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
		for my $i(0..$#list) {
			$output .= "<option value='".$list[$i]."'>".$list[$i]."</option>\n";
		}
		$output .= "</select>";
		return $output;
}

sub build_select_style {
# --------------------------------------------------------
	my ($output);
	my (@list) = split(/,/, $cfg{'styles'});
	$output = "<select name='pref_style' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	$output .= "<option value='default'>Default</option>\n";
	for my $i(0..$#list) {
		$output .= "<option value='".lc($list[$i])."'>".$list[$i]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}


sub build_select_accounting {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_accounts, Name, ID_accounting, level, isdetailaccount FROM sl_accounts WHERE Status='Active' ORDER BY ID_accounting");
	my $tab_char = "&nbsp;&nbsp;&nbsp;&nbsp;";
	my $disabled = "";
	while($rec=$sth->fetchrow_hashref){
		my $level_tab = $tab_char x (int($rec->{'level'})-1);
		$disabled = ($rec->{'isdetailaccount'} ne 'Yes')? ' disabled ':'';
		$output .= "<option value='$rec->{'ID_accounts'}' $disabled>".&format_account($rec->{'ID_accounting'})." $level_tab $rec->{'Name'}</option>";
	}
	return $output;
}

sub build_select_accounting_periods {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_accounting_periods AS ID, Short_Name AS Name FROM sl_accounting_periods WHERE 1 ORDER BY ID_accounting_periods");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID'}' $selected>$rec->{'Name'}</option>";
	}
	return $output;
}

sub build_select_closing_accounting_periods {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_accounting_periods AS ID, Short_Name AS Name FROM sl_accounting_periods WHERE 1 AND is_closing_periods = 'Yes' ORDER BY ID_accounting_periods");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID'}' $selected>$rec->{'Name'}</option>";
	}
	return $output;
}

sub build_select_agrupadorsat {
# --------------------------------------------------------
	my ($output);
	my $tab_char = "&nbsp;&nbsp;&nbsp;&nbsp;";

	my ($sth) =&Do_SQL("SELECT id_agrupadorSat, codigoAgrupador, name, levelAccount AS level FROM sl_agrupadorsat ORDER BY id_agrupadorSat ASC;");
	while ($rec=$sth->fetchrow_hashref){
		my $level_tab = $tab_char x (int($rec->{'level'})-1);
		$output .= "<option value='$rec->{'id_agrupadorSat'}' $selected>$level_tab$rec->{'codigoAgrupador'} - ".uc($rec->{'name'})."</option>";
	}
	return $output;
}


sub build_select_accounts_nature{
	my ($output);
	my ($sthItems);
	my ($sth) =&Do_SQL("SELECT ID_accounts_nature, Name FROM sl_accounts_nature where Type='Category'");
	while($rec=$sth->fetchrow_hashref){
		# $output .= "<option value='$rec->{'id_agrupadorSat'}' $selected>$rec->{'codigoAgrupador'} - ".uc($rec->{'name'})."</option>";
		$output.='<optgroup label="'.$rec->{'Name'}.'">';
		$sthItems=Do_SQL("SELECT ID_accounts_nature, Name FROM sl_accounts_nature WHERE ID_parent=".$rec->{'ID_accounts_nature'});
		while($rItems=$sthItems->fetchrow_hashref){
			$output.='<option value="'.$rItems->{'ID_accounts_nature'}.'">'.$rec->{'Name'}.': '.$rItems->{'Name'}.'</option>';
		}
		$output.='</optgroup>';
	}
	return $output;
}

sub name_account_nature{
	my $sth=Do_SQL(qq|select 
		concat(ss.Name, ' ', san.Name) Name
		from sl_accounts_nature san
		inner join sl_accounts_nature ss on ss.ID_accounts_nature = san.ID_parent 
		inner join sl_accounts on sl_accounts.ID_account_nature = san.ID_accounts_nature
		where sl_accounts.ID_accounts =  $in{'view'}|);
	my $row=$sth->fetchrow_hashref;
	return $row->{'Name'};
}

sub parent_categories{
	my $sth=Do_SQL('SELECT sl_accounts.ID_parent FROM sl_accounts WHERE sl_accounts.ID_accounts='.$in{'view'});
	my $row=$sth->fetchrow_hashref;
	my $name = &load_name("sl_accounts","ID_accounts",$row->{'ID_parent'},"Name");	
	return $name;
}

sub build_select_bank {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_banks,Name,Currency FROM sl_banks WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_banks'}' $selected>$rec->{'Name'} ($rec->{'Currency'})</option>";
	}
	return $output;
}

sub build_select_cataccounts {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_accategories,Name FROM sl_accategories WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_accategories'}' $selected>$rec->{'Name'}</option>";
	}
	return $output;
}

sub build_select_warehouses_accounts {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_accounts, ID_accounting, Name FROM sl_accounts WHERE Status='Active' AND ID_accounts >= 1000 ORDER BY Name;");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_accounts'}' $selected>$rec->{'Name'} : [$rec->{'ID_accounting'}]</option>";
	}
	return $output;
}

sub build_select_categories {
# --------------------------------------------------------
	my $output="";
	my ($sth)=&Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$selected="";
		if(('|'.$in{'id_categories'}.'|')=~/\|$rec->{'ID_categories'}\|/){
			$selected="selected=selected";
		}
		$output.="<option value='$rec->{'ID_categories'}' $selected>$rec->{'Title'}</option>";
	}
	return $output;
}

sub build_select_categories_title {
# --------------------------------------------------------
# Created :  Erik Osornio 03/04/2013 11:07:AM
# Last Update : 
# Locked by : 
# Description :
#
#
	my $output="";
	my ($sth)=&Do_SQL("SELECT ID_categories,Title FROM sl_categories WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$selected="";
		if(('|'.$in{'id_categories'}.'|')=~/\|$rec->{'ID_categories'}\|/){
			$selected="selected=selected";
		}
		$output.="<option value='$rec->{'Title'}' $selected>$rec->{'Title'}</option>";
	}
	return $output;
}

sub build_select_poadjustments {
# --------------------------------------------------------
	my $output="";
	my ($sth)=&Do_SQL("SELECT ID_extracharges,Name FROM sl_extracharges WHERE Status='Active' ORDER BY Name");
	while($rec=$sth->fetchrow_hashref){
		$selected="";
		if(('|'.$in{'id_extracharges'}.'|')=~/\|$rec->{'ID_extracharges'}\|/){
			$selected="selected=selected";
		}
		$output.="<option value='$rec->{'ID_extracharges'}' $selected>$rec->{'Name'}</option>";
	}
	return $output;
}

sub build_select_keypoints {
# --------------------------------------------------------
	my $output="";
	my ($sth)=&Do_SQL("SELECT ID_keypoints,Name FROM sl_keypoints WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$output.="<option value='$rec->{'ID_keypoints'}' $selected>$rec->{'Name'}</option>";
	}
	return $output;
}



#################################
##### FIN Func Revisadas
#################################

sub build_select_calification {
# --------------------------------------------------------
	return &build_select_from_enum('Calif','sl_leads_calls');
}

sub build_select_field_ec {
# --------------------------------------------------------
	return &build_select_from_enum('field','nsc_macros');
}

sub build_select_taxcountystate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_taxcounty');
}

sub build_select_taxstatestate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_taxstate');
}

sub build_select_opr_customersstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_customers');
}

sub build_select_fin_accountingtype {
# --------------------------------------------------------
	return &build_select_from_enum('Type','sl_accounting');
}

sub build_select_opr_salesstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_orders');
}

sub build_select_vendorstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_vendors');
}

sub build_select_shpvia {
# --------------------------------------------------------
	return &build_select_from_enum('ShpProvider','sl_orders_products');
}

sub build_select_supstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_vendors');
}



sub build_select_usertype {
# --------------------------------------------------------
# Last Time Modified by RB on 26/12/2014: Se crea para obtener todas las areas sin restricciones
	return &build_select_from_enum('user_type','admin_users');
}


sub build_select_grupo {
# --------------------------------------------------------
#Last modified on 13 Oct 2010 16:48:40
#Last modified by: MCC C. Gabriel Varela S. :Se cambia por sl_numbers_assign
	return &build_select_from_enum('grupo_assign','sl_numbers_assign');
}

sub build_select_ndmas {
# --------------------------------------------------------
	my $return="";
	$sth=&Do_SQL("Select ID_dmas,DMA FROM sl_dmas WHERE Status='Active'");
	while($rec=$sth->fetchrow_hashref){
		$selected="";
		if(('|'.$in{'id_dmas'}.'|')=~/\|$rec->{'ID_dmas'}\|/){
			$selected="selected=selected";
		}
		$return.="<option value='$rec->{'ID_dmas'}' $selected>$rec->{'DMA'}</option>";
	}
	return $return;
}


sub build_select_assignto {
# --------------------------------------------------------
	return &build_select_from_enum('assignto','sl_numbers');
}

sub build_select_fcategory{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/18/09 13:18:57
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($selected)=@_;
	return &build_select_from_enum_with_selected('Category','sl_movementstmp',$selected);
}

########################
#### ORDER STATUS
########################
sub build_select_order_status {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_select_from_enum('status','sl_orders');	
}

sub build_select_order_paystatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 7/22/2008 5:31:21 PM
# Description : 
# Notes : (

	return build_select_from_enum('statuspay','sl_orders');	
}

sub build_select_order_prdstatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 7/22/2008 5:31:58 PM
# Description : 
# Notes : (

	return build_select_from_enum('statusprd','sl_orders');	
}


sub build_select_hr_officemanstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_orders');
}

sub build_select_rfaret_reason {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'rsa_reason'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_search_result {
# --------------------------------------------------------
	my ($color,$db,%rec)=@_;
	my (@cols) = split(/,/,$sys{'srcols_'.$db});
	my ($output) = "\n<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$color'> ";
	for my $i(0..$#cols){
		if ($cols[$i] =~ /^ID/){
			$output .= "   <td nowrap><input type='submit' name='$rec{$cols[$i]}' value='".&trans_txt('btn_view')."' class='button'>
					   <input type='submit' name='$rec{$cols[$i]}' value='".&trans_txt('btn_edit')."' class='button'>
					   <input type='submit' name='$rec{$cols[$i]}' value='".&trans_txt('btn_del')."' class='button' onclick='notest=false;return;'>
					   &nbsp;$rec{$cols[$i]}</td>\n";
		}else{
			$output .= "   <td>$rec{$cols[$i]} </td>\n";
		}
	}
	$output .= "</tr>";
	return $output;
}

sub build_select_pricerange {
# --------------------------------------------------------
	my ($output,$pname);
	my (@ary) = split(/,/,$cfg{'price_range'});
	
	for (0..$#ary){
		($p1,$p2) = split(/-/,$ary[$_],2);
		$pname = &format_price($p1) . " - " . &format_price($p2);
		$output .= "<option value='$ary[$_]'>$pname</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prdtype {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_type'});
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_brands {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_brands WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_brands'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_regular_warehouses {
# --------------------------------------------------------
	my ($output);

	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type IN('Physical','Consigment','Return') AND Status='Active' ORDER BY Type, Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses'}' data-zones='$rec->{'DeliveryZones'}'>[$rec->{'ID_warehouses'}] $rec->{'Name'} &lt;$rec->{'Type'},$rec->{'City'},$rec->{'State'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_virtual_warehouses{
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type='Virtual' AND Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses'}'>[$rec->{'ID_warehouses'}] $rec->{'Name'} &lt;$rec->{'City'},$rec->{'State'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_warehouses{
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE 1 /*Type !='Virtual'*/ AND Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses'}'>[$rec->{'ID_warehouses'}] $rec->{'Name'} &lt;$rec->{'City'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_warehouses_all{
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses'}'>$rec->{'Name'} &lt;$rec->{'City'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_notdropshippers_warehouses {
# --------------------------------------------------------
	my ($selected) = @_;
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type='Physical' AND Status='Active' AND DropShipper = 'No' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_warehouses'} eq $selected){
			$output .= "<option value='$rec->{'ID_warehouses'}' selected>$rec->{'Name'} &lt;$rec->{'City'},$rec->{'State'}&gt;</option>\n";
		}else{
			$output .= "<option value='$rec->{'ID_warehouses'}'>$rec->{'Name'} &lt;$rec->{'City'},$rec->{'State'}&gt;</option>\n";
		}
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_prior_belongsto{
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on:
# Description :
# Notes : (Modified on : Modified by :)

	return build_select_from_enum('BelongsTo','sl_products_prior');
}


sub build_select_contracts_station{
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT DISTINCT Station FROM sl_mediacontracts ORDER BY Station;");
	while (my($station) = $sth->fetchrow){
		$output .= "<option value='$station'>$station</option>\n";
	}
	(!$output) and ($output .= "<option value=''>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prdcategories {
# --------------------------------------------------------
	my ($output,$rec,%cols,$key);
	my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' ORDER BY ID_parent;");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_parent'}>0){
			$cols{$rec->{'ID_categories'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'Title'};
		}else{
			$cols{$rec->{'ID_categories'}} = $rec->{'Title'};
		}
	}
	
	$output .= "<option value='---'>".&trans_txt('top_level')."</option>\n";
	foreach my $key (sort keys %cols) {
		$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
	}
	foreach my $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
		$output .= "<option value='$key'>$cols{$key}</option>\n";
	}	
	
	return $output;
}

sub build_select_maincategories {
# --------------------------------------------------------
	my ($output,$rec,%cols,$key);
	my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' AND ID_parent='0' ORDER BY Title;");
	$output .= "<option value='---'>".&trans_txt('top_level')."</option>\n";
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_categories'}'>$rec->{'Title'}</option>\n";
	}

	return $output;
}

sub build_select_pricelevels {
# --------------------------------------------------------
	my ($output,$rec,%cols,$key);
	my ($sth) = &Do_SQL("SELECT * FROM sl_pricelevels WHERE Status='Active'  ORDER BY Name;");
	$in{'id_pricelevels'}=1 if $sth->rows() == 1;
	while ($rec = $sth->fetchrow_hashref){
			$output .= "<option value='$rec->{'ID_pricelevels'}'>$rec->{'Name'}</option>\n";
	}


	return $output;
}

sub build_select_dids {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediadids WHERE Status='Active' ORDER BY product;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'didmx'}'>$rec->{'product'} &lt;$rec->{'didmx'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_dmas {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
# Last Modified on: 10/01/08 12:12:06
# Last Modified by: 

	my ($output);
	my ($sth) = &Do_SQL("SELECT RANK, `DMA_DESC` FROM `sl_zipdma` GROUP BY `RANK`");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'RANK'}'>$rec->{'RANK'} $rec->{'DMA_DESC'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_mediadmas {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
# Last Modified on: 10/01/08 12:12:06
# Last Modified by: 
	my ($output);
	my ($sth) = &Do_SQL("SELECT DMA FROM `sl_mediacontracts` WHERE DMA NOT IN ('', '0') AND LEFT(DMA,1) <>'\"' GROUP BY DMA");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'DMA'}'>$rec->{'DMA'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;

}

sub build_select_prd_pckopts {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update :
# Locked by :
# Description :
#
#

	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_packingopts WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_packingopts'}'>$rec->{'Name'} ".&format_price($rec->{'Shipping'})."</option>\n";
	}
	return $output;
}

sub build_select_opr_productcategorycb {
# --------------------------------------------------------
	#return &build_select_from_enum('ProdCategory','sl_chargebacks');
}


sub build_select_opr_chargebackto {
# --------------------------------------------------------
	return &build_select_from_enum('ChargeBackTo','sl_chargebacks');
}

sub build_select_opr_statuschargeback {
# --------------------------------------------------------
	return &build_select_from_enum('Status','sl_chargebacks');
}
#GV Termina


#######CLAIMS###
###JOAQUIN NUNEZ E. 23 DE JUNIO 2008

sub build_select_opr_productcategoryclaims {
# --------------------------------------------------------
	return &build_select_from_enum('ProdCategory','sl_claims');
}

sub build_select_opr_claimto {
# --------------------------------------------------------
	return &build_select_from_enum('ClaimTo','sl_claims');
}

sub build_select_opr_statusclaim {
# --------------------------------------------------------
	return &build_select_from_enum('Status','sl_claims');
}

#######REPLACEMENT MEMOS###
###JOAQUIN NUNEZ E. 25 DE JUNIO 2008

sub build_select_opr_reason {
# --------------------------------------------------------
	return &build_select_from_enum('Reason','sl_repmemos');
}

sub build_select_opr_productcategoryrep {
# --------------------------------------------------------
	return &build_select_from_enum('ProdCategory','sl_repmemos');
}

sub build_select_opr_statusrepmemos {
# --------------------------------------------------------
	return &build_select_from_enum('Status','sl_repmemos');
}

sub build_select_coverage_country{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/18/09 15:59:16
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	return &build_select_from_enum('Country','sl_warehouses_coverages');
}

sub build_select_lists{
#-----------------------------------------
# Created on: 02/19/09  16:22:55 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified on: 02/25/09 17:10:02
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para usar para autocomplete
	return &build_autocomplete_from_enum('Name','sl_lists');
}

sub build_select_dids7_type {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	
	$in{'second_conn'}=1;
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	return build_select_from_enum('type','cdr_s7_notes');	
}


sub build_select_accountcode{
# --------------------------------------------------------
# Created on: 3/3/10 3:08 PM
# Author: L.I. Roberto Barcenas.
# Description :
# Parameters :
# Forms Involved:

	my ($output);
	my ($sth) = &Do_SQL("SELECT DIDUS FROM sl_leads_calls WHERE DIDUS>0 GROUP BY DIDUS ORDER BY DIDUS;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'DIDUS'}'>&nbsp;$rec->{'DIDUS'}&nbsp;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_dids7_product {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
#Last modified on 13 Oct 2010 16:58:00
#Last modified by: MCC C. Gabriel Varela S. :Se hace left join con sl_numbers_assign
#Last modified on 8 Dec 2010 15:43:27
#Last modified by: MCC C. Gabriel Varela S. :Se cambia para contemplar grupos US y GTS solamente.
	
# 	my $grupo = "'','US'";
	my $grupo = "'US'";
	$grupo = "'GTS'" if $in{'e'} eq '4';
	$in{'second_conn'}=1;
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	if($cfg{'product_assign'}==1)
	{
	$sth = &Do_SQL("SELECT didusa,CONCAT(product_assign,' -- (',didusa,')') AS product FROM sl_numbers inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers WHERE grupo_assign IN($grupo) AND product_assign Is NOt NULL AND product_assign != '' ORDER BY product_assign,didusa ASC",1);
	}else{
	$sth = &Do_SQL("SELECT didusa,CONCAT(product,' -- (',didusa,')') AS product FROM sl_numbers WHERE grupo IN($grupo) AND product Is NOt NULL AND product != '' ORDER BY product,didusa ASC",1);
	}
	while ($rec = $sth->fetchrow_hashref){
	        $output .= "<option value='$rec->{'didusa'}'>&nbsp;$rec->{'product'}&nbsp;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_destination{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12 Aug 2011 15:29:19
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($output);
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	$in{'second_conn'}=1;
	return &build_select_from_enum('Destination','sl_numbers');
}

sub build_select_didmx{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 18 Aug 2011 18:57:06
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($output);
	my $grupo = "'US'";
	$grupo = "'GTS'" if $in{'e'} eq '4';
	$in{'second_conn'}=1;
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	if($cfg{'product_assign'}==1)
	{
		$sth = &Do_SQL("SELECT didmx FROM sl_numbers inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers WHERE grupo_assign IN($grupo) AND product_assign Is NOt NULL AND product_assign != '' ORDER BY product_assign,didmx ASC",1);
	}
	else
	{
		$sth = &Do_SQL("SELECT didmx FROM sl_numbers WHERE grupo IN($grupo) AND product Is NOt NULL AND product != '' ORDER BY product,didmx ASC",1);
	}
	while ($rec = $sth->fetchrow_hashref){
	        $output .= "<option value='$rec->{'didmx'}'>&nbsp;$rec->{'didmx'}&nbsp;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}




sub build_select_prd_shpqty{
# --------------------------------------------------------
# Created by: RB
# Created on: 11/18/2010
# Description : 
# 

	my ($output);
	my (@ary) = split(/\|/,$cfg{'shipping_prices_quantity'});	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	return $output;
}


sub build_select_prd_shpamount{
# --------------------------------------------------------
# Created by: RB
# Created on: 11/18/2010
# Description : 
# 

	my ($output);
	my (@ary) = split(/\|/,$cfg{'shipping_prices_netsale'});	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	return $output;
}

sub build_select_choices {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/12/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: Rafael Sobrino
# Description : Builds a list of all the choices in a drop-down menu for a particular product given the product id

	my ($id_products,$id_select) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$id_products AND (choice1!='' OR choice2!='' OR choice3!='' OR choice4!='') AND Status='Active';");
	$va{'matches'} = $sth->fetchrow;
		
	my ($drop_menu);	
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$id_products AND Status='Active';");
		$drop_menu = "<select name='choices$id_select'><option value='---'>---</option>\n";
		while ($rec = $sth->fetchrow_hashref){
			$drop_menu .= "  <option value='$rec->{'ID_sku_products'}'>$rec->{'choice1'}:$rec->{'choice2'}:$rec->{'choice3'}:$rec->{'choice4'}</option>\n";							
		}
		$drop_menu .= "</select>\n";	
	}else{
		$drop_menu = &trans_txt('no_choices');
	}
	$drop_menu =~ s/:://g;
	return $drop_menu;	
}
sub build_select_products_vendor {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT * FROM sl_products_vendors,sl_products WHERE sl_products_vendors.ID_products=sl_products.ID_products AND ID_vendors='$in{'id_vendors'}' AND sl_products.Status<>'Inactive';");
	while ($rec = $sth->fetchrow_hashref) {
		$output .= "<option value='$rec->{'ID_products'}'>".substr($rec->{'ID_products'},0,3) .'-'.substr($rec->{'ID_products'},3,3)." : $rec->{'Model'} ". substr($rec->{'Name'},0,20)."</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_vendors {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT ID_vendors,LEFT(CompanyName,30)AS CompanyName FROM sl_vendors WHERE Status = 'Active';");
	while ($rec = $sth->fetchrow_hashref) {
		my $selectedtxt;
		($in{'id_vendors'} and !$in{'id_extvendors'} and $in{'id_vendors'} == $rec->{'ID_vendors'}) and ($selectedtxt = 'selected');
		($in{'id_extvendors'} and $in{'id_extvendors'} == $rec->{'ID_vendors'}) and  ($selectedtxt = 'selected');	
		$output .= "<option value='$rec->{'ID_vendors'}' $selectedtxt>$rec->{'CompanyName'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_vendors_adjustments {
# --------------------------------------------------------
	#my ($add_sql) = ($cfg{'po_vendors_adjustments'} and $cfg{'po_vendors_adjustments'} ne '')? " AND ID_vendors IN($cfg{'po_vendors_adjustments'})":"";
	my ($sth) = &Do_SQL("SELECT ID_vendors,LEFT(CompanyName,30)AS CompanyName, Currency FROM sl_vendors WHERE Status = 'Active' AND Adjustment = 'Yes' /*$add_sql*/ ORDER BY CompanyName, Currency;");
	while ($rec = $sth->fetchrow_hashref) {
		my $selectedtxt;
		($in{'id_vendors'} and !$in{'id_extvendors'} and $in{'id_vendors'} == $rec->{'ID_vendors'}) and ($selectedtxt = 'selected');
		($in{'id_extvendors'} and $in{'id_extvendors'} == $rec->{'ID_vendors'}) and  ($selectedtxt = 'selected');	
		$output .= "<option value='$rec->{'ID_vendors'}' $selectedtxt>$rec->{'CompanyName'}&nbsp;($rec->{'Currency'})</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_products_warehouse {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses_location,sl_products WHERE RIGHT(sl_warehouses_location.ID_products,6)=sl_products.ID_products AND ID_warehouses='$in{'id_warehouses'}' AND sl_warehouses_location.Quantity>0;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses_location'}'>".substr($rec->{'ID_products'},0,3) .'-'.substr($rec->{'ID_products'},3,3)." : $rec->{'Model'} ". substr($rec->{'Name'},0,20)." x $rec->{'Quantity'} \@ $rec->{'Location'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_dayhour {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'dayhour'});
	
	for (0..$#ary){
		$output .= "<option value='".($_+1)."'>$ary[$_]</option>\n";
	}
	return $output;
}


sub build_select_daytime{
# --------------------------------------------------------
# Last Modified on: 12/02/10 12:43:05
# Last Modified by: MCC C. Gabriel Varela S: Se corrige para poner formato de hora con 2 numerales
	my ($output);
	my (@ary);
	my $hour = 0;
	
	for (0..48){
		$min = '00';
		$seg = '00';
		$hour = int(($_) / 2);
		($_ % 2 == 1) and ($min = '30');
		($_ == 48) and ($hour = "23") and ($min = "59");
	
		push(@ary,sprintf("%02d",$hour).":$min");
	}
	
	for (0..$#ary){
		($_ == 48) and ($seg="59");
		$output .= "<option value='$ary[$_]:$seg'>&nbsp;&nbsp;$ary[$_]&nbsp;&nbsp;</option>\n";
	}
	return $output;
}

sub build_select_warehouse_products{
# --------------------------------------------------------
# Author: Jose Ramirez Garcia
# Created on: 02/10/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output) = "";
	my ($sth_w) = &Do_SQL("SELECT ID_warehouses,SUM(Quantity) as Qty FROM sl_warehouses_location WHERE ID_products='".$in{'id_products'}."' AND (SELECT Type FROM sl_warehouses WHERE sl_warehouses.ID_warehouses=sl_warehouses_location.ID_warehouses)='Fisical' GROUP BY ID_warehouses");
	while ($war = $sth_w->fetchrow_hashref){
		if($war->{'Qty'} >= $va{'orders'}){
			$name = &load_name("sl_warehouses","ID_warehouses",$war->{'ID_warehouses'},"Name");
			$output .= "<option value='".$war->{'ID_warehouses'}."'>".$name."</option>\n";
		}
	}
	return $output;
}

sub build_select_all_virtual_warehouse {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	my ($output) = "";
	my ($sthw) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type='Virtual' AND Status='Active' ORDER BY Name");
	while ($war = $sthw->fetchrow_hashref){
		$output .= "<option value='".$war->{'ID_warehouses'}."'>".$war->{'Name'}."</option>";
	}	
	return $output;
}
sub build_select_perms {
# --------------------------------------------------------
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_perms WHERE Node='Yes' ORDER BY Name");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_parent'}){
			$output .= "<option value='$rec->{'ID_perms'}'>".&load_name('admin_perms','ID_perms',$rec->{'ID_parent'},'Name')."/$rec->{'Name'}</option>\n";
		}else{
			$output .= "<option value='$rec->{'ID_perms'}'>$rec->{'Name'}</option>\n";
		}
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_birthcountry {
# --------------------------------------------------------
	return &build_select_from_enum('BirthCountry','sl_customers');
}

sub build_select_dnis{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/19/10 12:08:31
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 8 Dec 2010 15:44:17
#Last modified by: MCC C. Gabriel Varela S. : Se cambia para contemplar solamente los grupos US y GTS (se cambia toda la consulta para contemplar inner)
# Last Modified by RB on 06/15/2011 12:28:25 PM : Se elimina el inner join ya que los campos en la tabla dnis son los mismos que en sl_numbers

	my ($output);
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
# 	my ($sth) = &Do_SQL("Select Number,USDnis from dnis order by USDnis;",1);
	my ($sth) = &Do_SQL("Select `num800`,`didusa`,`didmx`  /*Number,USDnis*/ 
from /*dnis 
inner join*/ sl_numbers /*on (dnis.USDnis=sl_numbers.didusa)*/
where `grupo` IN('US','GTS')
order by `didusa` /*USDnis*/;",1);
	$output.="<select name='dnis_i' onFocus='focusOn( this )' onBlur='focusOff( this )' multiple size=10>";
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'didusa'}'>(".substr($rec->{'num800'},0,3).") ".substr($rec->{'num800'},3,3)."-".substr($rec->{'num800'},-4)." / ".substr($rec->{'didusa'},0,3)."-".substr($rec->{'didusa'},-4). " / ". $rec->{'didmx'}."</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	$output.="</select>";
	return $output;
}

sub build_select_eco_linktable {
# --------------------------------------------------------
	return &build_select_from_enum('linktable','nsc_campaigns');
}

sub build_select_productsw_category {
# --------------------------------------------------------
	return &build_select_from_enum('Title','sl_products_w');
}

sub build_select_internet_users{
# --------------------------------------------------------
	my $return="";
	$sth=&Do_SQL("Select ID_admin_users,CONCAT(FirstName,' ', LastName)AS Name FROM admin_users where user_type='Internet' ORDER BY ID_admin_users DESC;");
	while($rec=$sth->fetchrow_hashref){
		$return.="<option value='$rec->{'ID_admin_users'}'>($rec->{'ID_admin_users'}) $rec->{'Name'}</option>";
	}
	return $return;
}

sub build_select_opr_coveragesstate {
# --------------------------------------------------------
	return &build_select_from_enum('State','sl_warehouses_coverages');
}


sub build_select_receivedfrom {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'receivedfrom'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	return $output;
}

sub build_select_sortby {
# --------------------------------------------------------
	#@fields = split (/\,/, $db_select_fields{'type'});
	#@fields = ('one','two','three');
	@fields = @db_cols;
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		@fields = 'None';
	}
	foreach my $field (@fields) {
		$field eq $value ?
			($output .= "<option value='".lc($field)."' selected>$field</option>\n") :
			($output .= "<option value='".lc($field)."'>$field</option>\n");
	}
	return $output;
}


sub build_select_tables {
# --------------------------------------------------------
	##Load SIP Extension
	my ($output);
	my ($sth) = &Do_SQL("SHOW TABLES");
	while ($rec = $sth->fetchrow()){
		$output .= "<option value='$rec'>$rec</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_virtual_warehouse {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on:
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	my ($output) = "";
	my ($sthw) = &Do_SQL("SELECT DISTINCT(ID_warehouses) FROM sl_warehouses_coverages WHERE lower(Country)='".lc($in{'country'})."' OR
	(lower(Country)='".lc($in{'country'})."' AND lower(State)='".lc($in{'state'})."') OR 
	(lower(Country)='".lc($in{'country'})."' AND lower(State)='".lc($in{'state'})."' AND 
	lower(City)='".lc($in{'city'})."') AND Covered='Covered' ");
	while ($war = $sthw->fetchrow_hashref){
		my ($sthnc) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_coverages WHERE ID_warehouses='".$war->{'ID_warehouses'}."' AND
		(lower(Country)='".lc($in{'country'})."' OR (lower(Country)='".lc($in{'country'})."' AND lower(State)='".lc($in{'state'})."') OR 
		(lower(Country)='".lc($in{'country'})."' AND lower(State)='".lc($in{'state'})."' AND 	lower(City)='".lc($in{'city'})."')) AND 
		Covered='Not Covered' ");
		if ($sthnc->fetchrow == 0){
			$warehouse_name = &load_name("sl_warehouses","ID_warehouses",$war->{'ID_warehouses'},"Name");
			$output .= "<option value='".$war->{'ID_warehouses'}."'>".$warehouse_name."</option>";
		}
	}	
	return $output;
}


#########################################################
#########################################################	
#	Function: 
#   		build_select_prodfam
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- Option values from sl_media_prodfam				
#
#   	See Also:
#
sub build_select_prodfam{
########################################################
########################################################

	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_media_prodfam WHERE Status='Active'  GROUP BY Name ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'Name'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}



#########################################################	
#	Function: 
#   		build_select_repstatus
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- Option values from sl_mediacontracts_rep.repStatus ENUM
#
#   	See Also:
#
sub build_select_repstatus {
########################################################
########################################################
	return &build_select_from_enum('repStatus','sl_mediacontracts_rep');
}


#########################################################	
#	Function: 
#   		build_select_refill_options
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- Refill Type Option values from sl_services
#
#   	See Also:
#
sub build_select_refill_options{
########################################################
########################################################

	my ($sth) = &Do_SQL("SELECT ID_services, Name FROM sl_services WHERE ServiceType='Refill'");
	my ($output) = "";
	while($row=$sth->fetchrow_hashref){
		$output .= "<option value='".$row->{'ID_services'}."'>".$row->{'Name'}."</option>\n";
	}
	return $output;
}


sub build_select_ret_reason {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'rma_reason'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prd_packing {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_packing'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prd_docs {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_docs'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_prd_handlingspecs {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_handling'});
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prd_type {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_type'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prd_handlingwarehouse {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_whandling'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_prd_supplierpacking {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_spacking'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_prd_paytypes {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_paytypes'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_parentcategories {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output,$rec,%cols,$key);
	my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' AND ID_parent=0 ORDER BY ID_parent;");
	while ($rec = $sth->fetchrow_hashref){
		$cols{$rec->{'ID_categories'}} = $rec->{'Title'};
	}
	
	$output .= "<option value='---'>".&trans_txt('top_level')."</option>\n";
	foreach my $key (sort keys %cols) {
		$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
	}
	foreach my $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
		$output .= "<option value='$key'>$cols{$key}</option>\n";
	}	
	
	return $output;
}

sub build_select_prdproperties {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output,$rec,%cols,$key);
	my ($sth) = &Do_SQL("SELECT * FROM sl_properties WHERE Status='Active' ORDER BY ID_parent;");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_parent'}>0){
			$cols{$rec->{'ID_properties'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'Title'};
		}else{
			$cols{$rec->{'ID_properties'}} = $rec->{'Title'};
		}
	}
	
	$output .= "<option value='---'>".&trans_txt('top_level')."</option>\n";
	foreach my $key (sort keys %cols) {
		$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
	}
	foreach my $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
		$output .= "<option value='$key'>$cols{$key}</option>\n";
	}	
	return $output;
}

sub build_select_prdchoices {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_choices WHERE Status='Active' ORDER BY Name;");
	$output .= "<option value='---'>---</option>\n";
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_choices'}'>$rec->{'Name'}</option>\n";
	}
	return $output;
}



sub build_select_departments {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_departments, Name FROM sl_departments WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_departments'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}




sub build_select_states {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_departments, Name FROM sl_departments WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_departments'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;	
}

sub build_select_categories {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_categories, Title FROM sl_categories WHERE ID_parent=0 AND Status='Active' ORDER BY Title;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_categories'}'>$rec->{'Title'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_dids {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediadids WHERE Status='Active' ORDER BY didmx;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'didmx'}'>$rec->{'product'} &lt;$rec->{'didmx'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

####################################################################
########             AGENCY                  ########
####################################################################
sub build_select_agency_paymenttype {
# --------------------------------------------------------
	return &build_select_from_enum('PaymentType','sl_mediaagencies');
}
sub build_select_agency_timezone {
# --------------------------------------------------------
	return &build_select_from_enum('TimeZone','sl_mediaagencies');
}

####################################################################
########             VENDOR                  ########
####################################################################

sub build_select_vendor_type {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_type'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

####################################################################
########             DROP DOWN MENUS                  ########
####################################################################

sub build_select_speechtype {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	@fields = split (/\,/, $db_select_fields{'type'});
	if ($#fields == -1) {
		$db_select_fields{$column} = &trans_txt('none');
		@fields = 'None' ;
	}
	foreach my $field (@fields) {
		$field eq $value ?
			($output .= "<option value='$field' selected>$field</option>\n") :
			($output .= "<option value='$field'>$field</option>\n");
	}
	return $output;
}

sub build_select_pricesnames {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_pricesnames'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		#$output .= "<input type='checkbox' name='paymentterms' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_inventorystatus {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_inventory'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_airprogram {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_dedair'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_specialprogram {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_sprogs'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_developers {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($sth) = &Do_SQL("SELECT DISTINCT FirstName,LastName FROM admin_users WHERE usergroup=1 ORDER BY firstname;");
	
	#$output .= "<option value='---'> </option>\n";
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{ID_admin_users}'>$rec->{FirstName} $rec->{'LastName'}</option>\n";
	}

	return $output;
}
sub build_select_customers {
# --------------------------------------------------------
# Created by: Javier Claros
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
  my ($output);
	my ($sth) = &Do_SQL("SELECT CONCAT(FirstName,' ',LastName1,' ', LastName2)  FROM sl_departments WHERE ID_customers='$in{'id_customers'}';");
	$va{'name'}  = $sth->fetchrow_hashref;
}

sub build_select_products_speech{
# --------------------------------------------------------
# Author: Jose Ramirez Garcia
# Created on: 8/7/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_speech WHERE Type = 'Product Script' AND STATUS = 'Active'");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_speech'}'>$rec->{'Name'}</option>\n";
	}
	return $output;
}

sub build_select_warehouse_type {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output);
	my (@ary) = split(/,/,$cfg{'warehouse_type'});
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_dids {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediadids WHERE Status='Active' ORDER BY didmx;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'didmx'}'>$rec->{'product'} &lt;$rec->{'didmx'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_stations {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediastations WHERE Status='Active' ORDER BY StationName;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'StationName'}'>$rec->{'StationName'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_agency {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediaagencies WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'Name'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_offer {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
	my ($output);
	my ($sth) = &Do_SQL("SELECT Offer FROM sl_mediacontracts WHERE Offer<>'' GROUP BY `Offer`;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'Offer'}'>$rec->{'Offer'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_pricesnames {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	my ($output);
	my (@ary) = split(/,/,$cfg{'prod_pricesnames'});
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		#$output .= "<input type='checkbox' name='paymentterms' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_brands {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_brands WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_brands'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_dayhour {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'dayhour'});
	
	for (0..$#ary){
		$output .= "<option value='".($_+1)."'>$ary[$_]</option>\n";
	}
	return $output;
}
sub build_select_weekdb {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT WEEK(CURDATE()) AS dbname");
	while ($rec = $sth->fetchrow_hashref){
		$in{'weekdb'} = $rec->{dbname};
	}
	$va{'weekdbc'}=$va{'weekdbb'}=$in{'k'}=$va{'weekdb'}=$in{'weekdb'};
	if ($in{'weekdb'} <= 51){
		$in{'weekdbb'}=$va{'weekdbb'}=$va{'weekdbb'}+1;
		$in{'weekdbc'}=$va{'weekdbc'}=$va{'weekdbc'}+2;
	}elsif($in{'weekdb'} == 52){
		$in{'weekdbb'}=$va{'weekdbb'}=$va{'weekdbb'}+1;
		$in{'weekdbc'}=$va{'weekdbc'}= 1;
	}elsif($in{'weekdb'} == 53){
		$in{'weekdbb'}=$va{'weekdbb'}= 1;
		$in{'weekdbc'}=$va{'weekdbc'}= 2;
	}
	$va{'weekdb'}=$in{'weekdb'};
}


sub build_select_warehouses_tobefulfilled{
# --------------------------------------------------------
	my ($output);
	my ($sthw) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type in('Virtual','Outsource') AND Status='Active'");
	while ($war = $sthw->fetchrow_hashref){
		$va{'selectwh'} .= "<option value='".$war->{'ID_warehouses'}."'>".$war->{'Name'}."</option>";
	}
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses WHERE Type in('Virtual','Outsource') AND Status='Active'");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_warehouses'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_select_customers_address {
# --------------------------------------------------------
	my ($output);
	if(int($in{'id_customers'})>0) {

		my ($sth) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers='".int($in{'id_customers'})."' AND Status = 'Active' ORDER BY Alias;");
		while ($rec = $sth->fetchrow_hashref){
			$output .= "<option value='$rec->{'ID_customers_addresses'}'>$rec->{'Code'} - $rec->{'Alias'}</option>\n";
		}

	}
	return $output;
}

sub build_select_customers_address2 {
# --------------------------------------------------------
	my ($output);
	if(int($in{'id_customers'})>0) {

		my ($sth) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers='".int($in{'id_customers'})."' AND Status = 'Active' ORDER BY Alias;");
		while ($rec = $sth->fetchrow_hashref){
			$output .= "<option value='$rec->{'Code'} - $rec->{'Alias'}'>$rec->{'Code'} - $rec->{'Alias'}</option>\n";
		}

	}
	return $output;
}

sub build_select_segments {
# --------------------------------------------------------
	
	my ($id_segments) = @_;
	my ($output);

	#&cgierr("/*$id_segments*/") if $id_segments > 0;
	my ($sth) = &Do_SQL("SELECT * FROM sl_accounts_segments ORDER BY Name;");
	$output .= "<option value='0'>".&trans_txt('none')."</option>\n";
	while ($rec = $sth->fetchrow_hashref){
		my $selectedtxt = $rec->{'ID_accounts_segments'} == $id_segments ? "selected" : '';
		$output .= "<option value='$rec->{'ID_accounts_segments'}' $selectedtxt>$rec->{'Name'}</option>\n";
	}

	return $output;

}


#########################################################	
#	Function: 
#   	build_select_accounts_segments
#
#	Created by:
#		Alejandro Diaz_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_accounts_segments
#
#   	See Also:
#
sub build_select_accounts_segments {
# --------------------------------------------------------
	
	my ($id_accounts_segments) = @_;
	my ($output);

	### Filtro de segmentos por usuario
	my $usr_seg = &load_name('admin_users', 'ID_admin_users', $usr{'id_admin_users'}, 'ID_accounts_segments');
	my $where_usr = '';
	if( $usr_seg ){
		$usr_seg =~ s/\|/,/g;
		$where_usr = " AND ID_accounts_segments In(".$usr_seg.")";
	}

	my ($sth) = &Do_SQL("SELECT * FROM sl_accounts_segments WHERE 1 /*AND ID_parent != 0*/ AND Status='Active' ".$where_usr." ORDER BY /*ID_segments,*/Name;");
	$output .= "<option value='0'>".&trans_txt('none')."</option>\n";
	while ($rec = $sth->fetchrow_hashref){
		my $selectedtxt = $rec->{'ID_accounts_segments'} eq $id_accounts_segments ? "selected" : '';
		$output .= "<option value='$rec->{'ID_accounts_segments'}' $selectedtxt>$rec->{'Name'}</option>\n";
	}

	return $output;

}

#########################################################	
#	Function: 
#   	build_select_bills_accounts
#
#	Created by:
#		Alejandro Diaz_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_accounts
#
#   	See Also:
#
sub build_select_bills_accounts{
########################################################
########################################################
	my ($id_accounts) = @_;
	$id_accounts = int($id_accounts);
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_accounts,Name, ID_accounting FROM sl_accounts WHERE Status='Active' ORDER BY Name,ID_accounting;");
	while($rec = $sth->fetchrow_hashref){
		if ($id_accounts == $rec->{'ID_accounts'}) {
			$output .= "<option value='".$rec->{'ID_accounts'}."' selected='selected'>".$rec->{'ID_accounting'}." - ".$rec->{'Name'}."</option>";
		}else{
			$output .= "<option value='".$rec->{'ID_accounts'}."'>".$rec->{'ID_accounting'}." - ".$rec->{'Name'}."</option>";
		}
	}

	return $output;
}


#########################################################	
#	Function: 
#   	build_select_services
#
#	Created by:
#		Alejandro Diaz_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_services
#
#   	See Also:
#
sub build_select_services{
########################################################
########################################################

	my ($sth) = &Do_SQL("SELECT ID_services, Name FROM sl_services WHERE Status = 'Active';");
	my ($output) = "";
	while($row=$sth->fetchrow_hashref){
		$output .= "<option value='".$row->{'ID_services'}."'>".$row->{'Name'}."</option>\n";
	}
	return $output;
}

#########################################################	
#	Function: 
#   	build_select_custom_bank
#
#	Created by:
#		Alejandro Diaz_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_banks for select
#
#   	See Also:
#
sub build_select_custom_bank{
# --------------------------------------------------------
	my ($output);

	my $cmd = $in{'cmd'};
	(!$in{'cmd'} and $in{'ajaxbuild'}) and ($cmd = $in{'ajaxbuild'});
	my ($sth2) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName = 'setup_bank_cmd_". &filter_values($cmd)."';");
	my ($banklist) = $sth2->fetchrow();
	($banklist) and ($banklist =~ s/\|/,/g);

	my $mod = $banklist ? " AND ID_banks IN($banklist)" : '';

	my ($sth) = &Do_SQL("SELECT ID_banks,Name,Currency,SubAccountOf FROM sl_banks WHERE Status='Active' AND ID_banks > 1000 $mod ;");

	while($rec=$sth->fetchrow_hashref){

		$output .= "<option value='$rec->{'ID_banks'}' $selected>$rec->{'SubAccountOf'}- $rec->{'Name'} ($rec->{'ID_banks'} - $rec->{'Currency'})</option>";

	}
	return $output;
}

#############################################################################
#############################################################################
#   Function: build_select_po_terms
#
#       Es: Genera radio buttons con terminos de pago para PO
#       En: Build radio buttons with payment terms for PO
#
#
#    Created on: 03/05/2013  13:20:10
#
#    Author: RB
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub build_select_po_terms {
#############################################################################
#############################################################################

    my ($strin,$st);
    $st = 'readonly' if $in{'view'};
    my ($sth) = &Do_SQL("SELECT ID_terms,Name FROM sl_terms WHERE Type='Purchases' AND Status='Active' ORDER BY Name");
   	my $i=0; 
    while(my($id,$name) = $sth->fetchrow()){
    	$in{'poterms'} = $name if (!$in{'poterms'} and $i==0);
        $strin .= qq|<span style='white-space:nowrap'><option $sel value="$name" $st> $name </option>\n|;
        $i++;
    }
    return $strin;  
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_locations
#
#	Created by:
#		Oscar Maldonado
#
#	Modified By: 17/04/2013::Alejandro Diaz
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_locations
#
#   	See Also:
#
sub build_select_locations {
#############################################################################
#############################################################################

	my ($id_warehouses) = @_;
	my ($add_sql);
	
	$id_warehouses = int($id_warehouses);
	$add_sql = ($id_warehouses > 0)? " AND ID_warehouses='$id_warehouses' " : "";

	my ($output);
	my ($sth) = &Do_SQL("SELECT Code, ID_warehouses FROM sl_locations WHERE Status='Active' $add_sql ORDER BY Code ASC;");
	while($rec = $sth->fetchrow_hashref) {
			$output .= "<option value='".$rec->{'Code'}."'>".$rec->{'Code'}."</option>";
	}

	return $output;
}


#############################################################################
#############################################################################
#	Function: build_select_po_rvendor
#
#		Es: Genera options para POs de Return to Vendor de acuerdo a los items a devolver
#       En: Generates option values for REturn to Vendor according to itmes to be returned
#
#    Created on: 03/07/2013  12:50:10
#
#    Author: _RB_
#
#    Modifications:
#		
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_locations
#
#   	See Also:
#
sub build_select_po_rvendor {
#############################################################################
#############################################################################

	
	my ($output,$ids,@pos);

	(!$in{'id_vendors'}) and ($in{'id_vendors'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'ID_vendors') );
	my $i=0;
	my ($sth) = &Do_SQL("SELECT ID_products,SUM(Qty) FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$in{'id_purchaseorders'}' GROUP BY ID_products;");
	while(my ($id_products, $quantity) = $sth->fetchrow()){

		my ($sth2) = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders FROM sl_purchaseorders INNER JOIN sl_purchaseorders_items USING(ID_purchaseorders) 
						WHERE ID_vendors = '$in{'id_vendors'}' AND Type = 'Purchase Order' AND ID_products = '$id_products' AND Received >= '$quantity' 
						/* AND sl_purchaseorders.Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) */
						ORDER BY sl_purchaseorders.ID_purchaseorders;");
		
		while (my ($id_po) = $sth2->fetchrow()) {
			
			if ($ids !~ /$id_po/) {
				$ids .= qq|$id_po;|;
			}
			
			$i++;
		}
		
	}


	if($ids){
		@pos = split(/;/, $ids);

		for(0..$#pos){
			my $id_po = int($pos[$_]);
			$output .= qq|<span style='white-space:nowrap'><option value = "$id_po" $st> $id_po </option></span>\n| if $id_po;
		}
	}else{
		$output .= qq|<span style='white-space:nowrap'><option>|.&trans_txt('search_nomatches').qq|</option></span>\n|;
	}

	
	
			

	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_exchangerate
#
#	Created by:
#		CARLOS HAAS
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- id and currency
#
#   	See Also:
#
sub build_select_exchangerate {
#############################################################################
#############################################################################

	my ($id_exchangerates,$currency) = @_;
	my ($output);
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_exchangerates WHERE Currency='$currency' ORDER BY Date_exchange_rate DESC LIMIT 0,250;");
	while($rec = $sth->fetchrow_hashref) {
		if ($rec->{'ID_exchangerates'} eq $id_exchangerates){
			$output .= "<option value='$rec->{'ID_exchangerates'}' selected>$rec->{'Date_exchange_rate'} / ".&format_price($rec->{'exchange_rate'},4)."</option>";
		}else{
			$output .= "<option value='$rec->{'ID_exchangerates'}'>$rec->{'Date_exchange_rate'} / ".&format_price($rec->{'exchange_rate'},4)."</option>";
		}
	}
	if ($output){
		$output = "<select name='id_exchangerates' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>\n$output\n</select>";
	}
	
	return $output;
}


#############################################################################
#############################################################################
#	Function: 
#   	build_banks_accounts
#
#	Es: Carga los bancos que tiene asociada una cuenta contable
#
#
#	Created by: _RB_
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_banks_accounts {
#############################################################################
#############################################################################

	my ($sth) = &Do_SQL("SELECT ID_banks, CONCAT(BankName,' ',SubAccountOf)As BankName FROM sl_banks WHERE ID_accounts > 0 ORDER BY BankName;");
	while($rec = $sth->fetchrow_hashref() ) {
		
		$output .= "<option value='". $rec->{'ID_banks'} ."'>". $rec->{'BankName'} ."</option>";
		
	}

	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_zones
#
#	Created by:
#		Oscar Maldonado
#
#	Created on: 06/09/2013  13:00:00
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_zones
#
#   	See Also:
#
sub build_select_zones {
#############################################################################
#############################################################################

	my ($id_zones) = @_;
	my ($add_sql);
	
	$id_zones = int($id_zones);
	$add_sql = ($id_zones > 0)? " AND ID_zones='$id_zones' " : "";

	my ($output);
	my ($sth) = &Do_SQL("SELECT Name, ID_zones FROM sl_zones WHERE Status='Active' $add_sql ORDER BY ID_zones ASC;");
	while($rec = $sth->fetchrow_hashref) {
			$output .= "<option value='".$rec->{'ID_zones'}."'>".$rec->{'ID_zones'}. ' - '. $rec->{'Name'}."</option>";
	}

	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_zipcode_states_acronym
#
#	Created by:
#		Oscar Maldonado
#
#	Created on: 06/09/2013  13:00:00
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_zipcodes
#
#   	See Also:
#
sub build_select_zipcode_states_acronym {
#############################################################################
#############################################################################

	my ($id_state) = @_;
	my ($add_sql);
	
	$add_sql = ($id_state ne '')? " AND State='$id_state' " : "";

	my ($output);
	my ($sth) = &Do_SQL("SELECT State FROM sl_zipcodes WHERE 1  $add_sql GROUP BY State;");
	while($rec = $sth->fetchrow_hashref) {
			$output .= "<option value='".$rec->{'State'}."'>".$rec->{'State'}."</option>";
	}

	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_zipcode_states
#
#	Created by:
#		Oscar Maldonado
#
#	Created on: 06/09/2013  13:00:00
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_zipcodes
#
#   	See Also:
#
sub build_select_zipcode_states {
#############################################################################
#############################################################################

	my ($id_state) = @_;
	my ($add_sql);
	
	$add_sql = ($id_state ne '')? " AND StateFullName='$id_state' " : "";

	my ($output);
	my ($sth) = &Do_SQL("SELECT StateFullName FROM sl_zipcodes WHERE 1  $add_sql GROUP BY StateFullName;");
	while($rec = $sth->fetchrow_hashref) {
			$output .= "<option value='".$rec->{'StateFullName'}."'>".$rec->{'StateFullName'}."</option>";
	}

	return $output;
}


#############################################################################
#############################################################################
#	Function: 
#   	build_debitmemos_type
#
#	Created by:
#		Oscar Maldonado
#
#	Created on: 08/01/2014  12:00:00
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#			- values from sl_debitmemos.Type [enum]
#
#   	See Also:
#
sub build_select_debitmemos_type {
#############################################################################
#############################################################################
	my ($output);
	my ($sth) = &Do_SQL("SELECT replace(replace(replace(column_type,'enum(',''),')',''),\"'\",'') as enum FROM information_schema.COLUMNS WHERE TABLE_NAME = 'sl_debitmemos' AND column_name = 'Type';");
	my ($rec) = $sth->fetchrow_hashref;
	my @Type = split "," , $rec->{'enum'};
	foreach my $enum (sort @Type) {
			$output .= "<option value='".$enum."'>".$enum."</option>";
	}
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_banks_accounts_by_name
#
#	Es: Carga los bancos que tiene asociada una cuenta contable
#
#
#	Created by: OM
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_banks_accounts_by_name {
#############################################################################
#############################################################################

	my ($sth) = &Do_SQL("SELECT ID_banks, sl_accounts.Name FROM sl_accounts INNER JOIN sl_banks ON sl_accounts.ID_accounts = sl_banks.ID_accounts WHERE sl_banks.Status = 'Active' AND sl_accounts.Status = 'Active' ORDER BY BankName;");
	while($rec = $sth->fetchrow_hashref() ) {
		
		$output .= "<option value='". $rec->{'Name'} ."'>". $rec->{'Name'} ."</option>";
		
	}

	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_orders_ptype
#
#	Es: Carga los tipos de pago de una orden
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_orders_ptype {
	return &build_select_from_enum('Ptype','sl_orders');
}

#############################################################################
#############################################################################
#	Function: 
#   	fc_build_select_orderspay_type
#
#	Es: Carga los tipos de pago de una orden pagada
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_orderspay_type {
	return &build_select_from_enum('Type','sl_orders_payments');
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_orders_state
#
#	Es: Carga los estados(entidades federativas) de una orden
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_orders_state {
	return &build_select_from_enum('State','sl_orders');
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_carrier
#
#	Es: Carga los nombres de los mensajeros
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_carrier {
# --------------------------------------------------------
	my ($output);
	my ($sth) =&Do_SQL("SELECT ID_carriers, Name FROM sl_carriers WHERE Status='Active';");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_carriers'}'>$rec->{'Name'}</option>";
	}
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_customers_addresses
#
#	Es: Carga los nombres de los mensajeros
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_customers_addresses {
# --------------------------------------------------------
	my ($id_customers) = @_;
	my ($output);
	my $add_sql = ($id_customers)?" AND cu_customers_addresses.ID_customers='$id_customers'":"";
	my ($sth) =&Do_SQL("SELECT ID_customers_addresses,Alias FROM cu_customers_addresses WHERE 1 $add_sql");
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_customers_addresses'}'>$rec->{'Alias'}</option>";
	}
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_orders_notes
#
#	Es: Carga los nombres de los mensajeros
#
#	Created by: FC
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_orders_notes{
# --------------------------------------------------------
	use JSON qw(decode_json);
	my $filename = $cfg{'json_orders_notes'};
	my $json_text = do {
	   open(my $json_fh, "<:encoding(UTF-8)", $filename)
	      or die("Can't open \$filename\": $!\n");
	   local $/;
	   <$json_fh>
	};
	my $decoded = decode_json($json_text);
	my $select ='<select name="notestype2" style="position:absolute" onblur="this.size=1;" onfocus="this.size=30;"  onchange="getMsg(this);this.size=1; this.blur();" data-name="notestype" class="select"><option></option>';
	my $test = '';
	for (my $i = 0; $i < @$decoded;$i++) {
    	$select.=qq|<optgroup label="@$decoded[$i]->{'category'}">|;
    	my $el = @$decoded[$i]->{'content'};
    	for (my $j = 0; $j < @$el; $j++) {
    		$select.=qq|<option data-category="$i" data-element="$j" value="@$el[$j]->{'label'}">@$el[$j]->{'label'}</option>|;
    	}
    	$select.=qq|</optgroup>|;
	}

	$select.='</select>';
	return $select;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_orders_notes_db
#
#	Es: Carga las categorias y las subcategorias desde la BD para generar los menus dinamicos de los tipos de notas
#  El formato del menu creado es:
# <div>
# 	<ul class="cd-accordion-menu animated">
# 		<li class="has-children">
# 			<input type="checkbox" name ="group-1" id="group-1">
# 			<label for="group-1">Group 1</label>'
# 	  		<ul>
# 	  			<li class="has-children">
# 	  				<input type="checkbox" name ="sub-group-1" id="sub-group-1">
# 					<label for="sub-group-1">Sub Group 1</label>'
# 					<ul>
# 						<li><a href="#0">Image</a></li>
# 						<li><a href="#0">Image</a></li>
# 						<li><a href="#0">Image</a></li>
# 					</ul>
# 	  			</li>
# 	  			<li class="has-children">
# 	  				<input type="checkbox" name ="sub-group-2" id="sub-group-2">
# 					<label for="sub-group-2">Sub Group 2</label>'
# 					<ul>'
# 						<li><a href="#0">Image</a></li>
# 					</ul>
# 	  			</li>'
# 	  		</ul>
# 		</li>'
# 	</ul> 
# </div>
#
#	Created by: JS
#
#	Modified By: 
#
#   	Parameters: NA
#
#   	Returns: HTML string to parse
#
#   	See Also: NA
#

sub build_select_orders_notes_db{
	my $acc='<fieldset>
    			<legend>Add Notes</legend>';
	my $catcont=1;
	my $subcatcont=1;
	my $mod=$usr{'application'};
	$acc.='<div>';
	$acc.='<ul class="cd-accordion-menu animated">';
		my ($Categories_query) = &Do_SQL('select distinct(ord.Category) as Category from sl_orders_notes_types ord where Status="Active" order by ord.Category ASC');
		while ($row_Category = $Categories_query->fetchrow_hashref){
			$acc.='	<li class="has-children">';
			$acc.='		<input type="checkbox" name ="group-'.$catcont.'" id="group-'.$catcont.'">';
			$acc.='		<label for="group-'.$catcont.'">'.$row_Category->{'Category'}.'</label>';			
			my ($Subcategory_query) = &Do_SQL('	select distinct(ord.Subcategory) as Subcategory 
												from sl_orders_notes_types ord where ord.Status="Active" 
												and ord.Category="'.$row_Category->{'Category'}.'"
												 order by ord.Category,ord.Subcategory'
			);

			$acc.='		<ul>';
			while ($row_Subcategory = $Subcategory_query->fetchrow_hashref){				
				$acc.='  			<li class="has-children">';
				$acc.='  				<input type="checkbox" name ="sub-group-'.$subcatcont.'" id="sub-group-'.$subcatcont.'">';
				$acc.='					<label for="sub-group-'.$subcatcont.'">'.$row_Subcategory->{'Subcategory'}.'</label>';									
				$acc.='					<ul>';
				
				my ($Types_query) = &Do_SQL('select Application,Type,Description,ID_orders_notes_types from sl_orders_notes_types where Status="Active" and Subcategory="'.$row_Subcategory->{'Subcategory'}.'" and Category="'.$row_Category->{'Category'}.'"');
				while ($row_Types = $Types_query->fetchrow_hashref){
					if(($row_Types->{'Application'} eq $mod) || (!$row_Types->{'Application'})){						
						# $html_fieldset.='<option class="optToSelect" value="'.$row_Types->{'Type'}.'" description="'.$row_Types->{'Description'}.'" idnote="'.$row_Types->{'ID_orders_notes_types'}.'">'.$row_Types->{'Type'}.'</option>';			
						$acc.='					<li><a href="#0" class="optToSelect" value="'.$row_Types->{'Type'}.'" description="'.$row_Types->{'Description'}.'" idnote="'.$row_Types->{'ID_orders_notes_types'}.'">'.$row_Types->{'Type'}.'</a></li>';						
					}
				}

				$acc.='					</ul>';
				$acc.='  			</li>';
				$subcatcont++;
			}
			$acc.=		'</ul>';			
			$acc.='	</li>';	
			$catcont++;
		}
	$acc.='</ul> ';
	$acc.='</div>';
	$acc.='</fieldset><br>';
	
	return $acc;
}






#############################################################################
#############################################################################
#	Function: 
#   	build_select_tipificacion
#
#	Es: Carca tipificacion de sl_vars_config para llamadas manuales.
#
#	Created by: FC
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_tipificacion {
#############################################################################
#############################################################################
	my ($output);
	my ($sth) =&Do_SQL("SELECT Largecode FROM sl_vars_config WHERE command='tipificacion_llamada'");
	$output = '<option value="">Seleccione ...</option>';
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'Largecode'}'>$rec->{'Largecode'}</option>";
	}
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_fiscal_year
#
#	Es: Obtiene las opciones para un select, contiene los ejercicios fiscales basados en los periodos contables
#
#	Created by: 22-08-2016 ISC Alejandro Diaz
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_fiscal_year {
#############################################################################
#############################################################################
	my ($output);
	my ($sth) =&Do_SQL("SELECT YEAR(From_Date) 'Year' FROM sl_accounting_periods GROUP BY 1 ORDER BY 1 DESC");
	$output = '';
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'Year'}'>$rec->{'Year'}</option>";
	}
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_warehouses_pos
#
#	Es: Muestra todos los almacenes seleccionando el valor existente por id_admin_users
#
#	Created by: FC
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_warehouses_pos{

	# --------------------------------------------------------
	my $return="";
	my $id_warehouses="";
	$sth=&Do_SQL("SELECT ID_warehouses, Name 
		FROM sl_warehouses 
		ORDER BY Name");

	my $sql1 = &Do_SQL("SELECT sl_vars.Subcode
			FROM sl_vars 
			INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_vars.Subcode 
			WHERE sl_vars.vname = 'pos_config_$in{'id_admin_users'}' AND sl_warehouses.Status = 'Active' ");  
	$vars = $sql1->fetchrow_hashref;
	$id_warehouses = $vars->{'Subcode'};
	      
	#$id_Almacen = $va{'update_warehouses'}; 
	while(my $rec=$sth->fetchrow_hashref){
		if($rec->{'ID_warehouses'} == $id_warehouses){
			$return.="<option selected='selected' value='$rec->{'ID_warehouses'}'>$rec->{'Name'}</option>";
		}else{
			$return.="<option value='$rec->{'ID_warehouses'}'>$rec->{'Name'}</option>";
		}	
	}
	return $return;	


}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_bank_pos
#
#	Es: 
#
#	Created by: FC
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
# 
sub build_select_bank_pos{
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_banks,Name,Currency,SubAccountOf FROM sl_banks WHERE ID_banks = 1013;");
	$output = '<select name="ID_banks" class="input" required><option >---------------</option>';
	while($rec=$sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_banks'}' $selected>$rec->{'Name'}</option>";
	}
	$output.='</select>';
	return $output;
}


#############################################################################
#############################################################################
#	Function: 
#   	build_select_salesorigins
#
#	Es: Muestra los canales de venta activos
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_accounting_periods_code{
	my ($selected) = @_;
	my ($output, $template) = undef;
	$template = qq|<option value="{{value}}">{{value}}</option>|;
	# $output = &build_page();
	### Num ###
	$html = $template;
	$html =~ s/{{value}}//g;
	$va{'num_periods'} = $html;
	$va{'num_year'} = $html;
	for (my $i = 1; $i <= 14; $i++) {
		$html = $template;
		$label = $i < 10 ? "0".$i : $i;
		$html =~ s/{{value}}/$label/g;
		$va{'num_periods'} .= $html;
	}

	for (my $i = 2015; $i <= 2050; $i++) {
		$html = $template;
		$html =~ s/{{value}}/$i/g;
		$va{'num_year'} .= $html;
	}

	return &build_page('id_accounting_periods_code.html');
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_salesorigins
#
#	Es: Muestra los canales de venta activos
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_salesorigins{
	my ($selected) = @_;
	my ($output);

	my ($sth) = &Do_SQL("SELECT ID_salesorigins, Channel FROM sl_salesorigins WHERE `Status`='Active';");	
	while($rec=$sth->fetchrow_hashref){
		if( $selected eq $rec->{'ID_salesorigins'} or $selected eq $rec->{'Channel'} ){
			$output .= "<option value='$rec->{'ID_salesorigins'}' selected>$rec->{'Channel'}</option>";
		} else {
			$output .= "<option value='$rec->{'ID_salesorigins'}'>$rec->{'Channel'}</option>";
		}
	}
	
	return $output;
}

#############################################################################
#############################################################################
#	Function: 
#   	build_select_users_auth
#
#	Es: Carga los usuarios activos para autorizadores
#
#	Created by: GQ
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_users_auth{
# --------------------------------------------------------
	
	my ($selected) = @_;
	my ($output);

	my ($sth) = &Do_SQL("SELECT ID_admin_users, FirstName, LastName, MiddleName FROM admin_users WHERE `Status`='Active' AND Email != '' AND Email IS NOT NULL ORDER BY LastName, MiddleName, FirstName;");
	while($rec=$sth->fetchrow_hashref){
		if( $selected eq $rec->{'ID_admin_users'} or $selected eq $rec->{'Channel'} ){
			$output .= "<option value='$rec->{'ID_admin_users'}' selected>$rec->{'LastName'} $rec->{'MiddleName'} $rec->{'FirstName'}</option>";
		} else {
			$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'} $rec->{'MiddleName'} $rec->{'FirstName'}</option>";
		}
	}
	
	return $output;
}

#############################################################################
#############################################################################
#   	build_select_accounts
#
#	Es: Muestra las cuentas contables
#
#	Created by: HC
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub build_select_accounts {
# --------------------------------------------------------
	use Encode;

	my ($sth) =&Do_SQL("SELECT ID_accounts, ID_accounting, Name FROM sl_accounts WHERE Status='Active' ORDER BY Name;");
	while($rec=$sth->fetchrow_hashref){
		#$output .= "<option value='$rec->{'ID_accounts'}' $selected>[$rec->{'ID_accounting'}] : $rec->{'Name'}</option>";
		$output .= encode("utf-8","<option value='$rec->{'ID_accounts'}' $selected>[$rec->{'ID_accounting'}] : $rec->{'Name'}</option>");
	}
	return $output;
}


sub build_select_payment_method{

	return &build_select_dbfield('payment_method', '', '', 'description', 'cu_metodo_pago', '', 1, '', 1);
}

sub build_select_payment_type{

	return &build_select_dbfield('payment_type', '', '', 'description', 'cu_forma_pago', '', 1, '', '');
}

sub build_select_use_cfdi{

	return &build_select_dbfield('use_cfdi', '', '', 'description', 'cu_uso_cfdi', '', 1, '', 1);
}


sub build_select_use_cfdi_credit{

	return &build_select_dbfield('use_cfdi_credit', '', '', 'description', 'cu_uso_cfdi', '', 1, '', 1);
}

sub build_select_use_cfdi_invoice{

	return &build_select_dbfield('use_cfdi_invoice', '', '', 'description', 'cu_uso_cfdi', '', 1, '', 1);
}

sub build_select_users_groups {
# --------------------------------------------------------
	my $return="";
	$sth=&Do_SQL("SELECT ID_admin_groups, Name FROM admin_groups WHERE Status='Active' AND ID_admin_groups>1;");
	while($rec=$sth->fetchrow_hashref){		
		$return.="<option value='$rec->{'ID_admin_groups'}'>$rec->{'ID_admin_groups'} - $rec->{'Name'}</option>";
	}
	return $return;
}

1;