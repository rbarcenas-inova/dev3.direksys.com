#!/usr/bin/perl
##########################################################
##		PRODUCTS	  ##
##########################################################


sub view_products {
# --------------------------------------------------------
# Last Modified on: 03/17/09 17:09:22
# Last Modified by: MCC C. Gabriel Varela S: parámetros sltv_itemshipping
# Last Modified RB: 12/16/2010  16:58:30 -- parámetros sltv_itemshipping
	$va{'id_products'} = &format_sltvid($in{'id_products'});
	
	### Brands
	if ($in{'id_brands'}){
		$in{'brands_name'} = &load_name('sl_brands','ID_brands',$in{'id_brands'},'Name');
	}else{
		$in{'id_brands'} = '---';
	}
	
	$in{'wholesalepriceorigin'} = &format_price($in{'wholesalepriceorigin'});
	$in{'wholesaleorigin'} = &format_price($in{'wholesaleorigin'});
	$in{'wholesaleprice'} = &format_price($in{'wholesaleprice'});
	$in{'sltv_netcost'} = &format_price($in{'sltv_netcost'});
	$in{'msrp'} = &format_price($in{'msrp'});
	$in{'map'} = &format_price($in{'map'});

	if ($in{'id_products'}){
		$va{'price'} = &load_name('sl_products_sprices','ID_products',$in{'id_products'},'Price');
	}
	
	if (!$in{'testing_authby'}){
		$va{'authby'} = "---";
	}else{
		$va{'authby'} = "($in{'testing_authby'}) ". &load_db_names('admin_users','ID_admin_users',$in{'testing_authby'},'[Firstname] [Lastname]');
	}

	### Calculate Shipping Charges
	($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= 	&sltv_itemshipping($in{'edt'},$in{'sizew'},$in{'sizeh'},$in{'sizel'},$in{'weight'},$in{'id_packingopts'},$in{'shipping_table'},$in{'shipping_discount'},$in{'id_products'});
	$va{'shptotal1'} = &format_price($va{'shptotal1'});
	$va{'shptotal2'} = &format_price($va{'shptotal2'});
	$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
	$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});
	
	## Prices
	$in{'sprice1'} = &format_price($in{'sprice1'});
	$in{'sprice2'} = &format_price($in{'sprice2'});
	$in{'sprice3'} = &format_price($in{'sprice3'});
	$in{'sprice4'} = &format_price($in{'sprice4'});
	
	## Packing Options
	if ($in{'id_packingopts'}){
		$in{'pckoptsname'} = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Name');
		$in{'shpcharges'}  = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Shipping');
		$in{'shpcharges'}  = &format_price($in{'shpcharges'});
	}

	$op_qc1="SELECT COUNT(\'x\') FROM sl_skus  WHERE id_products = \'$in{'id_products'}\' and (choice1 != \'\' or choice2 != \'\' or choice3 != \'\' or choice4 != \'\')";		
	
	my ($sth) = &Do_SQL($op_qc1);
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){ 
		&lista_choice();		
		$va{'searchresults'} .="<table border='0' cellspacing='0' cellpadding='4' width='100%' class='formtable'>\n";
		$va{'searchresults'} .="<tr>\n";
		$va{'searchresults'} .="  <td class='menu_bar_title'>Choices</td>\n";
		$va{'searchresults'} .="  <td class='menu_bar_title'>Opcions</td>\n";
		$va{'searchresults'} .="</tr>\n";
		if($in{'choicename1'}){
			$va{'searchresults'} .= "<tr>\n";					
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$in{'choicename1'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>[va_cho1]</td>\n";
			$va{'searchresults'} .= "</tr>\n";					
		}
		if($in{'choicename2'}){
			$va{'searchresults'} .= "<tr>\n";					
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$in{'choicename2'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>[va_cho2]</td>\n";
			$va{'searchresults'} .= "</tr>\n";					
		}
		if($in{'choicename3'}){
			$va{'searchresults'} .= "<tr>\n";					
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$in{'choicename3'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>[va_cho3]</td>\n";
			$va{'searchresults'} .= "</tr>\n";					
		}					
		if($in{'choicename4'}){
			$va{'searchresults'} .= "<tr>\n";					
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$in{'choicename4'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' valign='top'>[va_cho4]</td>\n";
			$va{'searchresults'} .= "</tr>\n";		
		}
    $va{'searchresults'} .="</table>\n";		    
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'}  ="  <tr><td class='menu_bar_title'>Choices </td>\n";
		$va{'searchresults'} .="  <td class='menu_bar_title'>Opcions</td></tr>\n";
		$va{'searchresults'} .= qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
	    </tr>\n|;
	}	
	$va{'listskus'}=$va{'searchresults'};
		
	## Load Inventory
	my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE RIGHT(ID_products,6)='$in{'id_products'}';");
	$in{'inventory'} = &format_number($sth->fetchrow);
	
	## Flexipago
	$in{'plexipago'} = int($in{'plexipago'});
	($in{'plexipago'} = 1) unless ($in{'plexipago'});
	$va{'payments'} = &format_price($in{'sprice'}/$in{'flexipago'});
}

sub view_parts {
# --------------------------------------------------------
	if ($in{'id_categories'}){
		$va{'catname'} = &load_name('sl_categories','ID_categories',$in{'id_categories'},'Title');
	}
	my ($sku) = 400000000+$in{'id_parts'};
	$va{'id_parts'} = &format_sltvid($sku);
	my ($sth) = &Do_SQL("SELECT VendorSKU,UPC FROM sl_skus WHERE ID_sku_products='$sku';");
	($in{'vendorsku'},$in{'upc'}) = $sth->fetchrow_array();

	## Load Inventory
	my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE ID_products='$sku';");
	$in{'inventory'} = &format_number($sth->fetchrow);
}

sub view_cus_skus {
#-------------------------------------------------------
	my ($sth)=&Do_SQL("SELECT *,(IF(sl_customers.company_name IS NOT NULL,sl_customers.company_name,CONCAT(sl_customers.FirstName,' ',sl_customers.Lastname1)))CustomerName FROM sl_customers_parts
					  INNER JOIN sl_parts USING(ID_parts)
					  INNER JOIN sl_skus ON (sl_skus.ID_products=sl_parts.ID_parts)
					  INNER JOIN sl_customers ON sl_customers.ID_customers=sl_customers_parts.ID_customers
					  WHERE sl_parts.Status !='Inactive'
						AND ID_parts=$in{'id_parts'} AND sl_customers.ID_customers=$in{'id_customers'};");
	my ($sku_data) = $sth->fetchrow_hashref();
	$va{'id_customers_parts'} = $sku_data->{'ID_customers_parts'};
	$va{'id_parts'} = $sku_data->{'ID_parts'};
	$va{'id_customers_parts'} = $sku_data->{'ID_customers_parts'};
	$va{'id_customers'} = $sku_data->{'ID_customers'};
	$va{'customer_name'} = $sku_data->{'CustomerName'};
	$va{'sku_customers'} = $sku_data->{'sku_customers'};
	$va{'size'} = $sku_data->{'size'};
	$va{'packing_type'} = $sku_data->{'packing_type'};
	$va{'packing_unit'} = $sku_data->{'packing_unit'};
	$va{'sprice'} = $sku_data->{'SPrice'};
	$va{'date'} = $sku_data->{'Date'};
	$va{'model'} = $sku_data->{'Model'};
	$va{'name'} = $sku_data->{'Name'};
	$va{'purchase_tax'} = $sku_data->{'Purchase_Tax'};
	$va{'sale_tax'} = $sku_data->{'Sale_Tax'};
	$va{'status'} = $sku_data->{'Status'};
	$va{'upc'} = $sku_data->{'UPC'};

	$in{'sprice'}=&format_price($in{'sprice'});
}

sub list_products {
# --------------------------------------------------------
	$in{'show_only_list'} = 1;
	#$in{'status'} = 'On-Air';	
}

sub advsearch_products {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : 
# Parameters : 
	$in{'id_products_code'} = &format_sltvid($in{'id_products'});
	if ($in{'upc'}){
		my ($sth) = &Do_SQL("SELECT ID_products FROM sl_skus WHERE UPC='$in{'upc'}'");
		$in{'id_products'} = $sth->fetchrow;
		if ($in{'id_products'}>0){
			$in{'tab'}=3;
			return &query('sl_products');
		}else{
			return ();
		}
	}elsif($in{'sl_products_categories.id_categories'}){
		###querydb2($db1,$db2,$jqry,$header_fields)
		my ($hfields);
		$in{'sl_products_categories.sx'}=1;
		$in{'st'} = 'AND';
		for (0..$#headerfields){
			$hfields .= "sl_products.$headerfields[$_],";
		} 
		chop($hfields);

		return &querydb2('sl_products','sl_products_categories','sl_products.ID_products=sl_products_categories.ID_products',$hfields);
	
	}else{
		my ($fname);
		for (0..$#db_cols){
			$fname = lc($db_cols[$_]);
			($in{'sl_products.'.$fname}) and ($in{$fname} = $in{'sl_products.'.$fname});
			delete($in{'sl_products.'.$fname});
		}
		return &query('sl_products');
	}
}

##########################################################
##	  OPERATIONS	: INORDERS        ##
##########################################################
sub view_inorders {
# --------------------------------------------------------
	if ($in{'id_pricelevels'}){
		$va{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');
	}

	### Question/Answer table
	for (1..5){
		(!$in{'question'.$_}) and ($in{'question'.$_}='---');
		(!$in{'answer'.$_}) and ($in{'answer'.$_}='---');
	}
}


##########################################################
##		OPERATIONS : ORDERS
##########################################################



sub view_orders {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on: 8/11/2008 9:02:54 AM
# Last Modified by: Carlos Haas
# Author: Carlos Haas
# Description : 
# Parameters : 

# Last Modified on: 10/08/08  16:17:17
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Total_Order = Products + Services - Discounts  + Taxes + Shipping
# Taxes = Products * Taxes Porc.

# Last Modified RB: 11/24/08  11:56:19 - Added link to preorder
# Last Modified RB: 12/18/08  12:35:46 - Added 30 day older capture validation
# Last Modified on: 09/14/09 17:40:50
# Last Modified by: MCC C. Gabriel Varela S: Se establece variable cmd_did

	$va{'cod_table'}	=	'';
	if ($in{'update_totals'}){
		&updateordertotals($in{'id_orders'});
	}elsif($in{'recalc_totals'}){
		&recalc_totals($in{'id_orders'});
	}elsif($in{'updateprodinfo'} and ($cfg{'oper_mode'} eq 'cleanup' or $usr{'usergroup'} <= 2)){
		my ($query,@cols);
		if ($usr{'usergroup'} eq 1){
			@cols = ('SalePrice','Shipping','SerialNumber','ShpDate','Tracking','ShpProvider','Status');
		}else{
			@cols = ('SalePrice','Shipping','Status');
		}
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET $query WHERE ID_orders_products='$in{'id_orders_products'}'");
		&auth_logging('opr_orders_cu_prdupd',$in{'id_orders'});
	}elsif($in{'updatepayinfo'} and ($cfg{'oper_mode'} eq 'cleanup' or $usr{'usergroup'} <= 2)){
		my ($query,@cols);
		if ($usr{'usergroup'} eq 1){
			@cols = ('PmtField1','PmtField2','PmtField3','PmtField4','PmtField5','PmtField6','PmtField7','PmtField8','PmtField9','Amount','Reason','Paymentdate','AuthCode','Captured','CapDate','Status');;
		}else{
			@cols = ('Amount','Paymentdate');
		}
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}		
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET $query WHERE ID_orders_payments='$in{'id_orders_payments'}'");
		&auth_logging('opr_orders_cu_payupd',$in{'id_orders'});
	}
	
	my ($fname);
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			#$in{'customers.'.lc($key)} = uc($rec->{$key});
			$in{'customers.'.lc($key)} = $rec->{$key};
		}
	}
	
	for (0..$#db_cols){
		$fname = lc($db_cols[$_]);
		$in{$fname} = $in{$fname};
	}
	
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
			## COD Table
			#$va{'cod_table'} = &get_cod_table($in{'id_orders'}); 
		}
	}
	
	$va{'cmd_customer'} = 'customers';
	$va{'cmd_did'} = 'dids';
	### Warning Message
	$va{'waringmsg'} = qq|<a href="/cgi-bin/mod/crm/dbman?cmd=invoices&view=[in_id_orders]"><img src='[va_imgurl]/[ur_pref_style]/warning.gif' title='Warining' alt='Invoice' border='0'></a>|;;
	
	### Station Name
	$va{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');
	
	### Orders Totals
	$tot_tax = (&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'};
	$va{'total_taxes'} = &format_price($tot_tax);
	$va{'total_order'} = &format_price($in{'ordernet'}-$in{'orderdisc'}+$in{'ordershp'}+$tot_tax);
	$va{'ordernet'} = &format_price($in{'ordernet'});
	
	
	$va{'orderdisc'} = &format_price($in{'orderdisc'});
	#$va{'orderdisc'} .= "<div id='field_orderdisc'><div onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"update_field('field_orderdisc','$in{'orderdisc'}','&tbl=sl_orders&id_name=ID_orders&id_value=$in{'id_orders'}&updfield=OrderDisc')\" >".&format_price($in{'orderdisc'})."</div></div>\n";
	
	## No Posted Date
	(!$in{'posteddate'}) and ($in{'posteddate'}='---');
	
	$va{'ordershp'} = &format_price($in{'ordershp'});
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	
	
		####### Checking for preorder
		my ($idpreorder) = &load_name('sl_preorders','ID_orders',$in{'id_orders'},'ID_preorders');
		$va{'was_preorder'} = '';
		
		if($idpreorder > 0){
			$va{'was_preorder'} = qq|
														<tr>
															<td width="30%" class="titletext">&nbsp;</td>
															<td class="smalltext"><span style="color:red;">|.&trans_txt('opr_waspreorder').qq| </span><a href="/cgi-bin/mod/crm/dbman?cmd=preorders&view=$idpreorder">$idpreorder</a>&nbsp;
															</td>
														</tr>	|;
		}
		
	###### Change to COD?
	&changeto_cod_apply($in{'id_orders'}) if (($usr{'user_group'} < 3 or $usr{'user_group'} == 7) and $in{'tocod'}); 
	if (&changeto_cod($in{'id_orders'}) == 1 and ($usr{'user_group'} < 3 or $usr{'user_group'} == 7) and !$in{'tocod'}){
		$va{'changeto_cod'} = qq|<input type="button" value="Change to COD" class="button" onClick="confirm_changeto_cod('$va{'script_url'}','$in{'cmd'}',$in{'id_orders'});">|;
	}
	###### Reactivate COD?
	&cod_apply_reactivate($in{'id_orders'}) if ($usr{'user_group'} < 3 and $in{'reactivate'}); 
	###### Link to Reactivate COD Cancelled?
	$va{'reactivate_cod'} = &cod_link_reactivate($in{'id_orders'})	if ($usr{'user_group'} < 3 and $in{'status'}	eq 'Cancelled' and !$in{'reactivate'});
	
	&conver_to_cc($in{'id_orders'}) if (&is_cc_convertible($in{'id_orders'}) == 1 and $in{'tocc'}==1); 
	if (&is_cc_convertible($in{'id_orders'}) == 1 and !$in{'tocc'}){
			$va{'conver_to_cc'} = 
			qq|
			<a name="add_paymenu" id="add_paymenu">&nbsp;</a>
			<!--a href='#add_paymenu' onClick="popup_show('popup_addnpay', 'nchrg_drag', 'popup_exitnchrg', 'element-right', -1, -1,'add_paymenu');"><img src='/sitimages//default/b_add.gif' title='Add payments' alt='' border='0'></a-->
			<input type="button" value="Convert to Credit Card" class="button" onClick="popup_show('popup_addnpay', 'nchrg_drag', 'popup_exitnchrg', 'element-right', -1, -1,'add_paymenu');">|;
			#&cgierr("ggdfd");
	}
	
	$in{'customers.phone1'} = &format_phone($in{'customers.phone1'},$in{'id_customers'});
	$in{'customers.phone2'} = &format_phone($in{'customers.phone2'},$in{'id_customers'});
	$in{'customers.cellphone'} = &format_phone($in{'customers.cellphone'},$in{'id_customers'});


	###### Change sales origins
	if ($in{'chgso'}){
		my ($sth) = &Do_SQL("UPDATE sl_orders SET id_salesorigins=".int($in{'chgso'})." WHERE ID_orders=$in{'id_orders'};");
		&auth_logging('sl_orders_updated',$in{'id_orders'});
		$in{'id_salesorigins'}=int($in{'chgso'});
		delete($in{'chgso'});
	}
	
	my $so = &load_name('sl_salesorigins','ID_salesorigins',$in{'id_salesorigins'},'Channel');
	my $sth = &Do_SQL("SELECT id_salesorigins,Channel FROM sl_salesorigins WHERE ID_salesorigins != '$in{'id_salesorigins'}';");
	while(my($id,$c) = $sth->fetchrow()){
		$solink .= qq|<a href="[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&chgso=$id">$c</a>&nbsp;&nbsp;|; 
	}
	$va{'sales_origins'} = qq|<tr>
														<td valign="top" width="30%" valign="top">Sales Origins: </td> 
														<td class="smalltext" valign="top">$so Change Origin to : <span class='smalltext'>$solink</span></td>
														</tr>|;
	
		
}

sub list_orders {
# --------------------------------------------------------
	$in{'show_only_list'} = 1;
}

sub advsearch_orders {
# --------------------------------------------------------

# Author: Unknown
# Created on: Unknown
# Last Modified on: 12/11/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters :
# Modif: Add the Credit Card search
# Last Modified on: 01/12/09 13:25:18
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para poder buscar en el campo shp_name cuando se introduce un nombre o un apellido
# Last Modified on: 02/04/09 09:29:02
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para que se pueda ir a páginas posteriores cuando se selecciona más de un status de búsqueda en órdenes.
# Last Modified on: 03/30/09 17:21:56
# Last Modified by: MCC C. Gabriel Varela S: Se habilita búsqueda de órdenes derivadas de cancelación de preórdenes que tienen todavía pagos pendientes de refund.
# Last Modified by RB 08/19/2009 : Se incluyo busqueda por ultimo AVS Response
# Last Modified RB: 09/17/09  11:10:55 -- Se inluye busqueda por fecha basada en el posteddate de la orden
# Last Modified RB: 10/27/2010  11:14:55 -- Se filtra por email
# Last Modified by RB on 04/11/2011 04:33:51 PM : Se agrega busqueda de ordenes COD con filtros por Fecha,Status, Driver (viene del home)

	my ($query);
	
	if($in{'type'} eq 'cod' and $in{'todo'}){
		my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
		if ($in{'todo'} eq 'withoutcontacted'){
			$sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
				FROM (SELECT sl_orders.ID_orders,count(ID_orders_notes)as NNotes
				      FROM sl_orders
				      LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
				      WHERE sl_orders.shp_type=$cfg{'codshptype'}
							and Ptype!='Credit-Card'
				      GROUP BY sl_orders.ID_orders
				      HAVING NNotes=0)as tmp
				GROUP BY NNotes");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}elsif ($in{'todo'} eq 'alreadyconfirmed'){
			$sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
				FROM (SELECT sl_orders.ID_orders,count(ID_orders_notes)as NNotes
				      FROM sl_orders
				      LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
				      WHERE sl_orders.shp_type=$cfg{'codshptype'}
							and Ptype!='Credit-Card'
				      GROUP BY sl_orders.ID_orders
				      HAVING NNotes!=0)as tmp
				GROUP BY NNotes");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}elsif ($in{'todo'} eq 'opwman_inprocess'){
			my $sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
	FROM `sl_orders` 
	WHERE /*ID_orders=0 
	and*/ Status='Processed'
	and shp_type=$cfg{'codshptype'} 
	and Ptype!='Credit-Card'
	and 1 > (
		SELECT COUNT(*) FROM sl_orders_datecod WHERE ID_orders=sl_orders.ID_orders AND Status='Active'
	);");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}elsif ($in{'todo'} eq 'opwman_intransit'){
			my $sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
	FROM `sl_orders`
	WHERE /*ID_orders=0 
	and*/ Status='Processed' 
	and shp_type=$cfg{'codshptype'}
	and Ptype!='Credit-Card'
	and 0 < (
		SELECT COUNT(*) FROM sl_orders_datecod WHERE ID_orders=sl_orders.ID_orders AND Status='Active'
	);");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}elsif ($in{'todo'} eq 'delivery_failed'){
			my $sth=&Do_SQL("SELECT if(not isnull(group_concat(ID_orders separator '|')),group_concat(ID_orders separator '|'),-1)as id_table
	FROM `sl_orders` 
	WHERE /*ID_orders=0 
	and*/ Status='Cancelled' 
	and shp_type=$cfg{'codshptype'}
	and Ptype!='Credit-Card'
	and 1 > (
		SELECT IF(Status='Active',1,0) FROM sl_orders_datecod WHERE ID_orders = sl_orders.ID_orders ORDER BY DateCOD DESC LIMIT 1
	)");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}elsif ($in{'todo'} eq 'bystatuscontact'){
			$in{'id_warehouses'} = 0 if !$in{'id_warehouses'};
			$in{'sx'}=1;
			$in{'id_table'}=sprintf("%s",&cod_by_status_contact($in{'status'},$in{'contact'},$in{'results'},$in{'id_warehouses'}));
			delete($in{'id_warehouses'});
			delete($in{'todo'});
			$in{'search'}= 'Search';
			$in{'status'}='Processed' if($in{'status'}=~/^Processed/);
			return &query('sl_orders');
		}
	}elsif($in{'todo'} eq 'layaway'){
		$in{'sx'}=1;
		$in{'id_orders'}= &build_query_table_layaway(2);
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');
	}elsif($in{'todo'} eq 'mo'){
		$in{'sx'}=1;
		$in{'id_orders'}= &build_query_table_moneyorder(2,$in{'type'},$in{'mod'});
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');
	}elsif($in{'todo'} eq 'cod_advsearch'){
	# Last Modified by RB on 04/11/2011 04:33:51 PM : Busca ordenes COD con filtros por Fecha,Status, Driver
	    
	    # From Date
	    if($in{'from_date'}){
	        $query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
	    }
	    
	    # To Date
	    if($in{'to_date'}){
	        $query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
	    }
	    
	    # Driver
	    if($in{'id_warehouses'}){
            $query .= " AND ID_warehouses = '$in{'id_warehouses'}' "; 
        }
	    
	    
	    # In Transit
	    if($in{'status'} eq 'intransit'){
	        $in{'status'} = 'Processed';
	        $inner_join = " INNER JOIN sl_orders_products USE INDEX(ID_orders)
	                        ON sl_orders.ID_orders = sl_orders_products.ID_orders
	                        INNER JOIN sl_orders_parts USE INDEX(ID_orders_products)
	                        ON sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products";               
	    }

	    my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
        $sth = &Do_SQL("SELECT group_concat(DISTINCT sl_orders.ID_orders separator '|') FROM sl_orders $inner_join WHERE sl_orders.Status = '$in{'status'}' $query ;");
        
        $in{'sx'}=1;
		$in{'id_orders'}=$sth->fetchrow;
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');          
	
	}


	if ($in{'id_products'}){
		#delete($in{'from_date'});
		#delete($in{'to_date'});
		$db_valid_types{'status'} = "function:ordersproducts_list";
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		#$in{'id_products'} = int($in{'id_products'});
		
		my ($query);
		if ($in{'status'}){
			my $cadstatus=$in{'status'};
			if ($cadstatus =~ /\|/){
				$cadstatus =~ s/\|/','/g;
				$query = " AND sl_orders.Status IN ('$cadstatus') ";
			}else{
				$query = " AND sl_orders.Status='$cadstatus' ";
			}
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}else{
			if ($in{'from_date'}){
				$query .= " AND sl_orders.Date>'".&filter_values($in{'from_date'})."' ";
			}
			if ($in{'to_date'}){
				$query .= " AND sl_orders.Date>'".&filter_values($in{'to_date'})."' ";
			}
		}

		## Filter by City
		if ($in{'shp_city'}){
			$query .= " AND sl_orders.shp_City LIKE '%$in{'shp_city'}%' ";
		}

		## Filter by State
		if ($in{'shp_state'}){
			$query .= " AND sl_orders.shp_State = '$in{'shp_state'}' ";
		}

		## Filter by zipcode
		if ($in{'shp_zip'}){
			$query .= " AND sl_orders.shp_Zip = '$in{'shp_zip'}' ";
		}
		
		if (length($in{'id_products'}) >6){
			return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status","sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND ID_products='$in{'id_products'}' AND sl_orders_products.Status='Active' $query ORDER BY sl_orders.ID_orders DESC",'sl_orders.ID_orders',@db_cols);
		}else{
			return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status as Status","sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND RIGHT(ID_products,6)='$in{'id_products'}' AND sl_orders_products.Status='Active' $query ORDER BY sl_orders.ID_orders DESC",'sl_orders.ID_orders',@db_cols);
		}
	}elsif($in{'paytbl'}){
		## Crear Query 
		my ($query,@cols,$condtype);
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		$query = " sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders ";
		if ($in{'type'}){
			$query .= "AND Type='$in{'type'}'";
		}
		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif($in{'status'}){
			$query .= " AND sl_orders.Status='$in{'status'}' ";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}elsif($in{'statuspay'}){
			$query .= " AND sl_orders.StatusPay='$in{'statuspay'}' ";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}elsif($in{'statusprd'}){
			$query .= " AND sl_orders.StatusPrd='$in{'statusprd'}' ";
		}

		if ($in{'paymentdate'} eq 'due'){
			$query .= "AND (sl_orders_payments.Paymentdate<Curdate() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'today'){
			$query .= "AND (sl_orders_payments.Paymentdate=Curdate() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'tweek'){
			$query .= "AND (WEEK(sl_orders_payments.Paymentdate)=WEEK(NOW()) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'nweek'){
			$query .= "AND (WEEK(sl_orders_payments.Paymentdate)=(WEEK(NOW())+1) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'tmonth'){
			$query .= "AND (MONTH(sl_orders_payments.Paymentdate)=MONTH(NOW()) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'nmonth'){
			$query .= "AND (MONTH(sl_orders_payments.Paymentdate)=(MONTH(NOW())+1) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		return &query_sql('DISTINCT(sl_orders.ID_orders),sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status',$query,'sl_orders.ID_orders',@db_cols);
	}elsif($in{'wprod'}){
		my ($query) = " sl_orders,sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders ";
		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= " AND sl_orders.Status IN ('$in{'status'}')";
		}elsif($in{'status'}){
			$query .= "  AND sl_orders.Status='$in{'status'}'";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}
		if ($in{'shp_type'}){
			$query .= " AND sl_orders.shp_type='$in{'shp_type'}'";
		}
		if ($in{'dropshipment'}){
			$query .= " AND 1=(Select COUNT(*) FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6) AND DropShipment='Yes') ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;
	        
		#($query) and ($query = "WHERE $query");
		
		$db_valid_types{'status'} = "function:ordersproducts_list";	
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status as Status"," $query ORDER BY sl_orders.ID_orders DESC",'sl_orders.ID_orders',@db_cols);
	}elsif($in{'wpay'}){
		my ($query) = " sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders ";
		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= "  AND  sl_orders.Status IN ('$in{'status'}')";
		}elsif($in{'status'}){
			$query .= "  AND  sl_orders.Status='$in{'status'}'";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;
		
		if($in{'paytype'}){
			($in{'paytype'} eq 'all') and ($query .= " (SELECT Type FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders LIMIT 0,1) IN ('WesternUnion','Money Order','Layaway','COD') ");
			($in{'paytype'} ne 'all') and ($query .= " (SELECT Type FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders LIMIT 0,1)='".$in{'paytype'}."' ");
			$query .= " $condtype ";
		}
		
		for (1..7){
			if ($in{'pmtfield'.$_}){
				$query .= "  AND  sl_orders_payments.PmtField$_='$in{'pmtfield'.$_}'";
			}
		}
		$db_valid_types{'status'} = "function:orderspayments_list";
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status"," $query ORDER BY sl_orders.ID_orders DESC",'sl_orders.ID_orders',@db_cols);
	
	}elsif($in{'firstname'} or $in{'lastname1'} or $in{'lastname2'} or $in{'phone'}  or $in{'email'} or $in{'paytype'}){
		#delete($in{'from_date'});
		#delete($in{'to_date'});
		my ($query,@cols,$condtype);
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		if ($in{'firstname'}){
			$query .=  "(FirstName LIKE '%".&filter_values($in{'firstname'})."%' or shp_name LIKE '%".&filter_values($in{'firstname'})."%') $condtype ";
		}
		if ($in{'lastname1'}){
			$query .=  "(LastName1 LIKE '%".&filter_values($in{'lastname1'})."%' or shp_name LIKE '%".&filter_values($in{'lastname1'})."%') $condtype ";
		}
		if ($in{'lastname2'}){
			$query .=  "(LastName2 LIKE '%".&filter_values($in{'lastname2'})."%' or shp_name LIKE '%".&filter_values($in{'lastname2'})."%') $condtype ";
		}
		if ($in{'phone'}){
			$query .=  "(CID LIKE '%".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Phone1 LIKE '%".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Phone2 LIKE '%".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Cellphone LIKE '%".&filter_values($in{'phone'})."%' OR ";
			$query .=  "CID LIKE '%".&filter_values($in{'phone'})."%') $condtype ";
		}

		if ($in{'email'}){
			$query .=  "Email LIKE '%".&filter_values($in{'email'})."%' $condtype ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND (sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}') ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}

		## Filter by City
		if ($in{'shp_city'}){
			$query .= " AND sl_orders.shp_City LIKE '%$in{'shp_city'}%' ";
		}

		## Filter by State
		if ($in{'shp_state'}){
			$query .= " AND sl_orders.shp_State = '$in{'shp_state'}' ";
		}

		## Filter by zipcode
		if ($in{'shp_zip'}){
			$query .= " AND sl_orders.shp_Zip = '$in{'shp_zip'}' ";
		}

		for my $i(0..$#db_cols){
			($in{lc($db_cols[$i])}) and ($in{'sl_orders.'.lc($db_cols[$i])} = $in{lc($db_cols[$i])});
			($in{lc('from_'.$db_cols[$i])}) and ($in{'from_sl_orders.'.lc($db_cols[$i])} = $in{lc('from_'.$db_cols[$i])});
		}
		my ($query2) = &build_query_str('sl_orders');
		if ($query2 and $query){
			$query = substr($query,0,-4);
			$query = "sl_orders.ID_customers=sl_customers.ID_customers AND (($query) $condtype ($query2)) ";
		}elsif($query2){
			$query = $query2;
		}elsif($query){
			$query = substr($query,0,-4);
			$query = "sl_orders.ID_customers=sl_customers.ID_customers AND ($query) ";
		}
		$query = " sl_orders,sl_customers WHERE $query ";
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		return &query_sql('ID_orders,sl_orders.Date as Date,sl_customers.ID_customers as ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status',$query,'sl_orders.ID_orders',@db_cols);
	
	}elsif($in{'pmtfield2'} or $in{'pmtfield3'} or $in{'authcode'} or $in{'refid'} or $in{'type'}){
		
		my ($query, $condtype);
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};

		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		if ($in{'pmtfield2'}){
			$query = " $condtype (PmtField2 like '%".&filter_values($in{'pmtfield2'})."%' AND PmtField2 !='' AND PmtField2 IS NOT NULL ) ";
		}elsif($in{'pmtfield3'}){
			$query = " $condtype (PmtField3 like '%".&filter_values($in{'pmtfield3'})."' AND PmtField3 !='' AND PmtField3 IS NOT NULL ) ";
		}elsif($in{'authcode'}){
			$query = " $condtype AuthCode = '".&filter_values($in{'authcode'})."' ";	
		}elsif($in{'type'}){
			$query = " $condtype Type='".&filter_values($in{'type'})."' ";	
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND (sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}') ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		
		}else{

			if ($in{'from_date'}){
				$query .= " AND sl_orders.Date>'".&filter_values($in{'from_date'})."' ";
			}
			if ($in{'to_date'}){
				$query .= " AND sl_orders.Date>'".&filter_values($in{'to_date'})."' ";
			}
		}


		if($query){
			## Este if esta sujeto a revision del query, por el momento en desuso (10/18/2010)
			if (!1){#$in{'refid'}){
				my (@hits);
				@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders");
				$numhits = $sth->rows;
				if ($numhits == 0){
					return (0,'');
				}
				(!$in{'nh'}) and ($in{'nh'}=1);
				my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'}");
				while ($rec = $sth->fetchrow_hashref){
						foreach my $column (@db_cols) {
						push(@hits, $rec->{$column});
					}
				}
				return ($numhits, @hits);
			} else {
				my (@hits);
				@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders $query GROUP BY sl_orders.ID_orders");
				my $numhits = $sth->rows;
				if ($numhits == 0){
					return (0,'');
				}
				(!$in{'nh'}) and ($in{'nh'}=1);
				my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status as Status FROM sl_orders,sl_orders_payments WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders $query GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'}");
				while ($rec = $sth->fetchrow_hashref){
						foreach my $column (@db_cols) {
						push(@hits, $rec->{$column});
					}
				}
				return ($numhits, @hits);
			}
		} else {
			return &query('sl_orders');
		}
	}elsif($in{'avs_response'}){
	##### Busca sobre el ultimo paylog
		delete($in{'from_date'});
		delete($in{'to_date'});
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		
		my $cad_nopreorder = "1 > (SELECT COUNT(*) FROM sl_preorders WHERE ID_orders = sl_orders.ID_orders) ";
		
		my ($query);
		if ($in{'status'}){
			my $cadstatus=$in{'status'};
			if ($cadstatus =~ /\|/){
				$cadstatus =~ s/\|/','/g;
				$query = " AND Status IN ('$cadstatus') ";
			}else{
				$query = " AND Status='$cadstatus' ";
			}
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND StatusPrd='$in{'statusprd'}'";
		}
		if ($in{'from_date'}){
			$query .= " AND Date >'".&filter_values($in{'from_date'})."' ";
		}
		if ($in{'to_date'}){
			$query .= " AND Date >'".&filter_values($in{'to_date'})."' ";
		}
		
		my $cadavs = "ccAuthReply_avsCode = [$in{'avs_response'}]";
		$cadavs = "AVS Response = [$in{'avs_response'}]"	if($in{'e'} == 2 or $in{'e'} == 4);
		$query .= " AND 0 < (SELECT COUNT(*) FROM sl_orders_plogs WHERE ID_orders = sl_orders.ID_orders AND Data NOT REGEXP 'AVS VERIFICATION' AND Data REGEXP '$cadavs' ORDER BY ID_orders_plogs DESC LIMIT 1) ";
		
		
		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status as Status","sl_orders WHERE $cad_nopreorder $query ORDER BY ID_orders DESC",'ID_orders',@db_cols);
	}elsif($in{'bposteddate'}){
		$in{'from_posteddate'} = $in{'from_date'};
		$in{'to_posteddate'} = $in{'to_date'};
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		if($in{'to_posteddate'} and $in{'from_posteddate'}){
			$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
		}elsif($in{'from_posteddate'}){
			$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
		}elsif($in{'to_posteddate'}){
			$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
		}

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status as Status","sl_orders WHERE 1 $query ORDER BY ID_orders DESC",'ID_orders',@db_cols);
	}else{
		return &query('sl_orders');
	}
}



sub view_preorders {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by: Rafael Sobrino
# Author: Carlos Haas
# Description : 
# Parameters :
# Last Modified RB: 11/06/08  11:30:45 - Added update totals,prodinfo,payinfo, recalctotals
# Last Modified RB: 11/24/08  11:56:19 - Added link to order
# Last Modified JRG: 01/21/09 : Se a¤ade la opcion de cod en paytype
# Last Modified on: 02/06/09 16:54:21
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se muestren las pestañas para todos los casos de preorders
# Last Modified RB: 02/11/09  10:44:34 -- Se paso el llamado de pestanas la forma preorders_view, como se hace en orders
# Last Modified on: 03/17/09 15:52:58
# Last Modified by: MCC C. Gabriel Varela S: Se comenta ésta línea:$paytype = &load_name("sl_preorders_payments","ID_preorders",$in{'id_preorders'},"Type");
# Last Modified on: 03/18/09 10:09:38
# Last Modified by: MCC C. Gabriel Varela S: Se comenta ésta línea: $in{'shp_type'} = $paytype;
# Last Modified RB: 03/30/09  12:44:46 -- Se incorpora el formateo de discount
# Last Modified on: 09/14/09 17:41:20
# Last Modified by: MCC C. Gabriel Varela S: Se establece variable cmd_did

	#Convert to order
	if($in{'id_preorders'}>0 and $in{'converttoorder'}==1)
	{
		$id_orders=convert_preorder_to_order($in{'id_preorders'});
		if($id_orders==-1)
		{
			$va{'message'} = "The preorder could not be converted.";
		}
		else
		{
			$va{'message'} = "The preorder was converted and the ID is: $id_orders.";
		}
	}
	
 	$va{'cod_table'}	=	'';
	if ($in{'update_totals'}){
		&updatepreordertotals($in{'id_preorders'});
	}elsif($in{'recalc_totals'}){
		&recalcpreordertotals($in{'id_preorders'});
	}elsif($in{'updateprodinfo'} and ($cfg{'oper_mode'} eq 'cleanup' or $usr{'usergroup'} <= 2)){
		my ($query,@cols);
		if ($usr{'usergroup'} eq 1){
			@cols = ('SalePrice','Cost','Shipping','SerialNumber','ShpDate','Tracking','ShpProvider','Status');
		}else{
			@cols = ('SalePrice','Shipping','Status');
		}
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_preorders_products SET $query WHERE ID_preorders_products='$in{'id_preorders_products'}'");
		&auth_logging('opr_preorders_cu_prdupd',$in{'id_preorders'});
	}elsif($in{'updatepayinfo'} and ($cfg{'oper_mode'} eq 'cleanup' or $usr{'usergroup'} <= 2)){
		my ($query,@cols);
		if ($usr{'usergroup'} eq 1){
			@cols = ('PmtField1','PmtField2','PmtField3','PmtField4','PmtField5','PmtField6','PmtField7','PmtField8','PmtField9','Amount','Paymentdate','AuthCode','Captured','CapDate','Status');;
		}else{
			@cols = ('Amount','Paymentdate');
		}
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}		
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_preorders_payments SET $query WHERE ID_preorders_payments='$in{'id_preorders_payments'}'");
		&auth_logging('opr_preorders_cu_payupd',$in{'id_preorders'});
	}

	my ($fname);
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach $key (keys %{$rec}){
			#$in{'customers.'.lc($key)} = uc($rec->{$key});
			$in{'customers.'.lc($key)} = $rec->{$key};
		}
	}
	
	$va{'cmd_customer'} = 'customers';
	$va{'cmd_did'} = 'dids';
	$paytype = &load_name("sl_preorders_payments","ID_preorders",$in{'id_preorders'},"Type");
	
	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]";
			## COD Table
			#$va{'cod_table'} = &get_cod_table($in{'id_preorders'});
		}
	}
	
	
	### Station Name
	$va{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');
	
	### Orders Totals
	$tot_tax = (&taxables_in_preorder($in{'id_preorders'})-$in{'orderdisc'})*$in{'ordertax'};
	$va{'total_taxes'} = &format_price($tot_tax);
	$va{'total_order'} = &format_price($in{'ordernet'}-$in{'orderdisc'}+$in{'ordershp'}+$tot_tax);
	$va{'ordernet'} = &format_price($in{'ordernet'});
	$va{'orderdisc'} = &format_price($in{'orderdisc'});
	$va{'ordershp'} = &format_price($in{'ordershp'});
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);

	## Comments
	if ($in{'action'}){
		if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('reqfields_short');
		}elsif (!$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('orders_noteadded');
			my ($sth) = &Do_SQL("INSERT INTO sl_preorders_notes SET ID_preorders='$in{'id_preorders'}',Notes='".&filter_values($in{'notes'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			delete($in{'notes'});
			delete($in{'notestype'});
			&auth_logging('preorders_noteadded',$in{'id_preorders'});
		}
	}
	
	## VRM
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_preorders_notes WHERE ID_preorders='$in{'id_preorders'}' $query");
	 $va{'matches'} = $sth->fetchrow;
	if ( $va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman", $va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT sl_preorders_notes.ID_admin_users,sl_preorders_notes.Date as mDate,sl_preorders_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_preorders_notes,admin_users WHERE ID_preorders='$in{'id_preorders'}' AND sl_preorders_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY ID_preorders_notes DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			 $va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			 $va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			 $va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
			 $va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
			 $va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		 $va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	####### Checking for order
		my ($idorder) = &load_name('sl_preorders','ID_preorders',$in{'id_preorders'},'ID_orders');
		$va{'is_order'} = '';
		
		if($idorder > 0){
			$va{'is_order'} = qq|
														<tr>
															<td width="30%" class="titletext">&nbsp;</td>
															<td class="smalltext"><span style="color:red;">|.&trans_txt('opr_isorder').qq| </span><a href="/cgi-bin/mod/crm/dbman?cmd=orders&view=$idorder">$idorder</a>&nbsp;
															</td>
														</tr>	|;
		}
		else
		{
			#$va{'is_order_img'} = qq|<a href="$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_preorders'}&converttoorder=1"><img height=24 witdh=24 src="$va{'imgurl'}/app_bar/workflow.png" title="Convert to Order" alt="Convert to Order" border="0"></a>|;
			$va{'is_order_img'} = qq|
			<script type="text/javascript">
			function validate_convert()
			{
				if(confirm('Once the convertion has been done this can not be undone. Do you really want to do the convertion?'))
					document.location.href="$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_preorders'}&converttoorder=1";
			}
		</script>
			<img height=24 witdh=24 src="$va{'imgurl'}/app_bar/workflow.png" title="Convert to Order" alt="Convert to Order" border="0" onclick="validate_convert()">|;
		}
		
		###### Reactivate COD?
		&cod_apply_reactivate($in{'id_preorders'}) if ($usr{'user_group'} < 3 and $in{'reactivate'}); 
		###### Link to Reactivate COD Cancelled?
		$va{'reactivate_cod'} = &cod_link_reactivate($in{'id_preorders'})	if ($usr{'user_group'} < 3 and $in{'status'}	eq 'Cancelled' and !$in{'reactivate'});
		
}

sub validate_preorders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/10/08 13:42:03
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my $err;
	if($in{'prestatus'}eq"Cancelled"){
		++$err;
		$error{'status'} = &trans_txt("invalid").". No se permite editar una preorden cancelada.";
	}elsif($in{'status'}eq"Cancelled"){
		++$err;
		$error{'status'} = &trans_txt("invalid").". No se puede cancelar por éste medio.";
	}
	
	if($in{'edit'}){
		my ($sth) = &Do_SQL("SELECT IF(shp_State != '$in{'shp_state'}' OR shp_Zip != '$in{'shp_zip'}',1,0) FROM sl_preorders WHERE ID_preorders = '$in{'id_preorders'}';");
		if($sth->fetchrow == 1){
			if($in{'authcode'} and $in{'authcode'}ne''){
				my ($sth) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4)='".&filter_values($in{'authcode'})."'");
				my ($idorder,$idadmin,$authorization) = split(/,/,$sth->fetchrow,3);
				if ($idadmin > 0 or $idorder eq $in{'id_orders'}){
					&recal_order_all($in{'id_preorders'},$in{'shp_state'},$in{'shp_zip'},'preorders');
					my ($sth) = &Do_SQL("INSERT INTO sl_preorders_notes SET Notes='".&trans_txt('order_shpchange_authorized')."',Type='Low',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}', ID_preorders='$in{'id_preorders'}';");
					&auth_logging('preorders_note_added',$in{'id_preorders'});
					## Reinitialize the Value
					my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Auth Order' AND RIGHT(VValue,4)='$in{'authcode'}';");
				}else{
					++$err;
					$va{'message'} .= "Invalid authorization code.";
				}
			}else{
				++$err;
				$va{'message'} .= "Invalid authorization code.";
			}
		}
	}
	
	return $err;
}





sub validate_orders {
# --------------------------------------------------------
# Last Modified on: 07/22/08 11:21:30
# Last Modified by: MCC C. Gabriel Varela S: Se pone una condición para saber si se viene de "Add Orden"
# Last Modified by: JRG : 03/04/2009 se agrega log al update de orders
# Last Modified by: JRG : 03/04/2009 se agrega log al update de orders
# Last Modified by RB: 03/18/2010 se agrega validacion para el Ptype al agregar

	my ($err);
	$err=0;
	if($in{'add'}!=1)
	{
		my ($old_status) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Status');  
		if ($old_status eq 'Returned' or $old_status eq 'Cancelled' or $old_status eq 'Shipped'){
			$in{'status'} = $old_status;
			#$error{'status'} = &trans_txt('invalid');
			#++$err;
		}
		$alfa=0;
		$updated_query="";
		if (!$in{'statuspay'}){
			$updated_query=" StatusPay='None' ";
			$alfa=1;
		} 	
		if (!$in{'statusprd'}){
			if($alfa == 1){
				$updated_query .=", ";
			}
			$updated_query .=" StatusPrd='None' ";
			$alfa=1;
		}
		if($alfa == 1){
			my ($sth) = &Do_SQL("UPDATE sl_orders SET $updated_query WHERE Id_orders = $in{'id_orders'}");				
			&auth_logging('orders_updated',$in{'id_orders'});
			$in{'statuspay'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'StatusPay');
			$in{'statusprd'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'StatusPrd');
		}	
	}
	else
	{
		if ($in{'add'}){
			$in{'status'} = 'New';
			$in{'statuspay'} = 'None';
			$in{'statusprd'} = 'None';

			if(!$in{ptype}){
			    $error{'ptype'} = &trans_txt('required');
			    ++$err
			}
		}
	}
	
	if($in{'edit'}){
		my ($sth) = &Do_SQL("SELECT IF(shp_State != '$in{'shp_state'}' OR shp_Zip != '$in{'shp_zip'}',1,0) FROM sl_orders WHERE ID_orders = '$in{'id_orders'}';");
		if($sth->fetchrow == 1){
			if($in{'authcode'} and $in{'authcode'}ne''){
				my ($sth) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4)='".&filter_values($in{'authcode'})."'");
				my ($idorder,$idadmin,$authorization) = split(/,/,$sth->fetchrow,3);
				if ($idadmin > 0 or $idorder eq $in{'id_orders'}){
					&recal_order_all($in{'id_orders'},$in{'shp_state'},$in{'shp_zip'},$in{'shp_city'},'orders');

					&add_order_notes_by_type($in{'id_orders'},&trans_txt('order_shpchange_authorized'),"Low");

					&auth_logging('orders_note_added',$in{'id_orders'});
					## Reinitialize the Value
					my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Auth Order' AND RIGHT(VValue,4)='$in{'authcode'}';");
				}else{
					++$err;
					$va{'message'} .= "Invalid authorization code.";
				}
			}else{
				++$err;
				$va{'message'} .= "Invalid authorization code.";
			}
		}
	}
	
	
	return $err;
}

sub validate_atcreturns{
	# Last Modified on:11/jun/2008 02:16:33 PM
	# Last Modified by: MCC C Gabriel Varela S
	# Description : Se agrega validación de producto cuando es exchange
	# Last Modified on: 11/07/08 10:31:01
	# Last Modified by: MCC C. Gabriel Varela S: Se valida la existencia de 2 UPCs normales
	# Last Modified by: JRG : 03/04/2009 se agrega log al returns de upcs
	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	}
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	if($in{'id_products_exchange'} ne '')
	{
		if($in{'id_products_exchange'}!~/^\d{9}$/)
		{
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
			else
			{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
				{
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}
		else
		{
			$in{'id_products_exchange'}=~/^(\d{3})(\d{3})(\d{3})$/;
			$in{'id_products_exchange'}="$1$2$3";
			if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
		}
	}
	#GV Termina 11jun2008
	
	if(!$in{'atcreturnfees'}){
		$error{'atcreturnfees'} = &trans_txt('required');
		++$err;
	}
	if(!$in{'atcrestockfees'}){
		$error{'atcrestockfees'} = &trans_txt('required');
		++$err;
	}
	if($in{'atcprocessed'} ne 'yes'){
		$in{'atcprocessed'} = "no";
	}
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			#GV Termina modificación 24jun2008
			while ($rec1 = $sth1->fetchrow_hashref){
				$gvi++;
				$upcs = $rec1->{'UPC'};
				$io = $gvi."io_$upcs";
				$st = $gvi."st_$upcs";
				if($in{$io} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$io} = &trans_txt('required');
					++$err;
				}
				if($in{$st} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$st} = &trans_txt('required');
					++$err;
				}
				if($in{$io} && $in{$st}){
					my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET InOrder='$in{$io}', Status='$in{$st}' WHERE ID_returns=$in{'id_returns'} AND UPC=$upcs and ID_returns_upcs=$rec1->{'ID_returns_upcs'};");
					&auth_logging('returns_upcs_updated',$rec1->{'ID_returns_upcs'});					
				}
			}
		}
	}
	return $err;
}

sub advsearch_atcreturns{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'id_returns'}){
			$qry .= " sl_returns.ID_returns='$in{'id_returns'}' ";
		}
		
		if($in{'id_orders'}){
			$qry .= " sl_returns.ID_orders='$in{'id_orders'}' ";
		}		
		
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}
}



##########################################################
##	ADMINISTRATIONS : ADMIN USERS 		          ##
##########################################################
sub loaddefault_users{
# --------------------------------------------------------
#Last modified on 11 May 2011 13:27:57
#Last modified by: MCC C. Gabriel Varela S. : Se hace que se asigne el mismo ipfilter que el creador
	#Se obtiene ipfilter del creador
	my $created_by_ipfilter=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'ipfilter');
	$in{'ipfilter'} = $created_by_ipfilter;
	$in{'status'} = 'Active';
	$in{'never_expires'} = 'on';
}

sub view_users {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 
# Last Modified on: 9/07/2007 5:01PM
# Last Modified by: Rafael Sobrino
# Author: Rafael Sobrino
# Description : 
#Last modified on 11 May 2011 13:55:54
#Last modified by: MCC C. Gabriel Varela S. : Se hace que se muestre el nombre verdadero del creador

	$in{'createdby.firstname'}=&load_name('admin_users','ID_admin_users',$in{'createdby'},'Firstname');
	$in{'createdby.lastname'}=&load_name('admin_users','ID_admin_users',$in{'createdby'},'LastName');
	if (!$in{'id_parent'}){
		$in{'parentname'} = &trans_txt('top_level');
	}else{
		$in{'parentname'} = &load_name('sl_categories','ID_categories',$in{'id_parent'},'Title');
	}
	
	if ($in{'expiration'} eq ""){
		$va{'expiration'} = &trans_txt("no_expiration");
	}else{
		$va{'expiration'} = $in{'expiration'};
	}
	
	(!$in{'opcnotes'}) and ($in{'opcnotes'} = '---');
	
}


sub validate_users {
# --------------------------------------------------------
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by: Jos‚ Ramirez Garcia
# Author: 
# Description : 
# Parameters :
# Last Modified RB: 03/18/09  10:12:26 -- LastLogin initialization
# Last Modified RB: 04/07/09  13:01:35 -- Se Modifica el acceso para grupos 1,7
# Last Modified RB: 08/23/2010  11:51:35 -- Se requiere el user_type
#Last modified on 16 Dec 2010 11:50:38
#Last modified by: MCC C. Gabriel Varela S. : Se implementa sha1
#Last modified on 11 May 2011 13:28:46
#Last modified by: MCC C. Gabriel Varela S. : Se hace que el ipfilter sea igual al del creador
#Last modified on 17 May 2011 16:31:59
#Last modified by: MCC C. Gabriel Varela S. : Se hace que las x se tomen como *
#Last modified on 20 May 2011 15:20:34
#Last modified by: MCC C. Gabriel Varela S. :Se hace que \r sea opcional
 
	my $err;
	
	#Se evalúa ipfilter
	#Se obtiene ipfilter del creador
	my $created_by_ipfilter;
 	if($in{'id_admin_users'}ne'')
 	{#Si se edita
		#obtiene created by
		my $created_by=&load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'CreatedBy');
		$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$created_by,'ipfilter');
 	}
 	else
 	{#Si se crea
		$created_by_ipfilter=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'ipfilter');
 	}
 	
 	#Se cambia la forma de evaluar la ipfilter de los creados
 	my (@ipfilter_values) = split(/\r?\n/,$created_by_ipfilter);
 	my $ipfilter_turn;
 	my $valid_ip=0;
 	my (@ipfilter_values_in) = split(/\r?\n/,$in{'ipfilter'});
 	foreach $ipfilter_turn (@ipfilter_values)
 	{
# 		if(!$valid_ip or 1)
# 		{
			$ipfilter_turn=~s/\./\\\./g;
			$ipfilter_turn=~s/x/\[\\d\|x\]\*/g;
	 		foreach $ipfilter_turn_in (@ipfilter_values_in)
			{
				if($ipfilter_turn_in=~/$ipfilter_turn/)
				{
# 					$variable="$ipfilter_turn";
					++$valid_ip;
				}
			}
# 		}
	}
#  	cgierr("$variable y valid_ip:$valid_ip y ".($#ipfilter_values_in+1));
	if($valid_ip<($#ipfilter_values_in+1))
	{
		$error{'ipfilter'} = &trans_txt("invalid");
# 		$in{'ipfilter'} = $created_by_ipfilter;
		++$err;
	}
	
	if($usr{'usergroup'} != 1 and $usr{'usergroup'} != 7){
		$error{'message'} = trans_txt('not_auth');
		++$err;
	}
	
	(!$in{'status'}) and ($in{'status'} = 'Active');
	if($in{'username'} and (length($in{'username'})<5 or length($in{'username'})>12)){
		$error{'username'} = &trans_txt("invalid");
		++$err;
	}
	 

	if ($in{'email'}){
		if (!&valid_address($in{'email'})){
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}			
	}
	
	if(!$in{'user_type'}){
		$error{'user_type'} = &trans_txt("required");
		++$err;
	}
	
	$in{'lastlogin'}	=	"NOW()" if $in{'status'} eq 'Active';
	$in{'usergroup'} = 3;
	
		
	
	if ($in{'add'}){
		my ($passwd) = &gen_passwd;
		
			use Digest::SHA1;
			my $sha1= Digest::SHA1->new;
			$sha1->add($passwd);
			$in{'password'} = $sha1->hexdigest;
		
		$in{'temppasswd'} = $passwd;

		if($in{'username'}){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}';");
			$found = $sth->fetchrow();
			if ($found>0){
				$error{'username'} = &trans_txt("repeated");
				++$err;
			}else{
				### send email with password to the newly created user
				$body = "Your password: $passwd";
				$subject = &trans_txt("admin_email_subject");
				if (send_email("admin\@innovagroupusa.com",$in{'email'},$subject,$body) eq "ok"){
					$va{'email_status'} = &trans_txt("admin_email_success");
				}else{
					$va{'email_status'} = &trans_txt("admin_email_err");
				}				
			}
		}
	}else{
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE Username='$in{'username'}' AND ID_admin_users<>'$in{'id_admin_users'}';");
		$found = $sth->fetchrow();
		if ($found>0){
			$error{'username'} = &trans_txt("repeated");
			++$err;
		}
		$in{'password'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'Password');
		$in{'temppasswd'} = &load_name('admin_users','ID_admin_users',$in{'id_admin_users'},'tempPasswd');
	}
	
	if ($in{'never_expires'}){
		$in{'expiration'} = 'NULL';
	}

	return $err;
	
}

sub advsearch_users {
# --------------------------------------------------------
# Created on: 6/3/2008 11:24AM
# Last Modified on:
# Last Modified by:
# Author: Jos‚ Ramirez Garcia
# Description : search users with retrictions to supervisor's module
# Parameters :

	if($in{'subsearch'} eq "listall"){
		@db_cols = ("ID_admin_users","Username","FirstName","LastName","application","Status");
		$query = "admin_users WHERE UserGroup IN(2,3,4,5) AND (application='sales' OR application='crm') ORDER BY ID_admin_users DESC";
		my($numhits, @hits) = &query_sql('ID_admin_users,Username,FirstName,LastName,application,Status',$query, "ID_admin_users", @db_cols);
		return $numhits, @hits;
	} else {
		my ($db)="admin_users";
		my ($i, $column, $value, $query, $condtype, $sort_order, @aux, $xquery);
		
		if ($in{'keyword'}) {
			for my $i(0..$#db_cols){
				$column = lc($db_cols[$i]);
				$in{'keyword'} =~ s/^\s+//g;
				$in{'keyword'} =~ s/\s+$//g;
				if ($db_valid_types{$column} eq 'date' and &date_to_sql($in{'keyword'})){
					$query .= "$db_cols[$i] = '" . &date_to_sql($in{'keyword'}) . "' OR ";
				}elsif ($in{'sx'} or $in{'SX'}){
					$query .= "$db_cols[$i] = '" . &filter_values($in{'keyword'}) . "' OR ";
				}else{
					$query .= "$db_cols[$i] like '%" . &filter_values($in{'keyword'}) . "%' OR ";
				}
			}
			$query = substr($query,0,-3);
		}elsif ($in{lc($db_cols[0])} ne "*" or !$in{'listall'}){
			if ($in{'st'} =~ /or/i){
				$condtype = "OR";
			}else{
				$condtype = "AND";
			}
			for my $i(0..$#db_cols){
				$column = lc($db_cols[$i]);
				$in{$column} =~ s/^\s+//g;
				$in{$column} =~ s/\s+$//g;
				$value = &filter_values($in{$column});
				#($db_valid_types{$column} eq 'date') ?
				#	($value = &date_to_sql($in{$column})):
				#	($value = &filter_values($in{$column}));
				if ($in{$column} !~ /^\s*$/) {
					if ($in{$column} =~ /~~|\|/){
						@aux = split(/~~|\|/, $in{$column});
						$xquery = '';
						for (0..$#aux){
							($db_valid_types{$column} eq 'date') ?
								($value = &date_to_sql($aux[$_])):
								($value = &filter_values($aux[$_]));
							($in{'sx'} or $db_valid_types{$column} eq 'date')?
								($xquery .= "$db_cols[$i] = '$value'  OR "):
								($xquery .= "$db_cols[$i] like '%$value%'  OR ");
						}
						$query = "(" . substr($xquery,0,-4) . " ) $condtype " unless (!$xquery);
					}else{
						if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
							$query .= "$db_cols[$i] = Curdate() $condtype ";
						}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
							$query .= "WEEK($db_cols[$i]) = WEEK(NOW()) $condtype ";
						}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
							$query .= "MONTH($db_cols[$i]) = MONTH(NOW()) $condtype ";
						}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
							$query .= "YEAR($db_cols[$i]) = YEAR(NOW()) $condtype ";
						}elsif($value eq 'NULL'){
							$query .= "ISNULL($db_cols[$i]) $condtype ";						
						}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
							$query .= "$db_cols[$i]  = '$value'  $condtype ";
						}else{
							$query .= "$db_cols[$i] like '%$value%'  $condtype ";
						}
					}
				}
				if ($in{'from_'.$column} !~ /^\s*$/) {
					$in{'from_'.$column} =~ s/^\s+//g;
					$in{'from_'.$column} =~ s/\s+$//g;
					$value = &filter_values($in{'from_'.$column});
					### From To Fields
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] > Curdate() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) > WEEK(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) > MONTH(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) > YEAR(NOW()) $condtype ";
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  > '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] > '$value'  $condtype ";
					}
				}
				if ($in{'to_'.$column} !~ /^\s*$/) {
					$in{'to_'.$column} =~ s/^\s+//g;
					$in{'to_'.$column} =~ s/\s+$//g;
					$value = &filter_values($in{'to_'.$column});
					### From To Fields
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] < Curdate() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) < WEEK(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) < MONTH(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) < YEAR(NOW()) $condtype ";
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  < '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] < '$value'  $condtype ";
					}
				}
			}
			
			$query = substr($query,0,-4);
		}
		### Nothing to Search
		#start modification to be used on supervisor
		if (!$query and ($in{lc($db_cols[0])} ne "*" and !$in{'listall'})){
				$query = "WHERE UserGroup IN(2,3,4,5) AND (application='sales' OR application='crm')";
		}elsif ($query){
				$query = "WHERE ($query) AND UserGroup IN(2,3,4,5) AND (application='sales' OR application='crm')";
		} else {
				$query = "WHERE UserGroup IN(2,3,4,5)) AND (application='sales' OR application='crm')";
		}
	
		### sort Records ###
		if (exists($in{'sb'})) {
			if ($db_valid_types{$in{'sb'}}){
				$sort_order = "ORDER BY $in{'sb'} $in{'so'}";
			}elsif( $db_cols[$in{'sb'}]){
				$sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}";
			}
		}
		
		$qry = "$db $query $sort_order ";
		
		@db_cols = ("ID_admin_users","Username","FirstName","LastName","application","Status");
		my($numhits, @hits) = &query_sql('ID_admin_users,Username,FirstName,LastName,application,Status',$qry, "ID_admin_users", @db_cols);
		return $numhits, @hits;
	}

}

sub view_tracking_email{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/21/10 16:17:57
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	use HTML::Entities ();
	$in{'from'}=HTML::Entities::encode($in{'from'});
	$in{'received'}=HTML::Entities::encode($in{'received'});
	$in{'returnpath'}=HTML::Entities::encode($in{'returnpath'});
	$in{'subject'}=HTML::Entities::encode($in{'subject'});
	$in{'to'}=HTML::Entities::encode($in{'to'});
	#$in{'body'}=HTML::Entities::encode($in{'body'});
	if($in{'id_orders'}){
		$va{'id_orders'}="<a href='/cgi-bin/mod/crm/dbman?cmd=orders&view=$in{'id_orders'}'>$in{'id_orders'}</a>";
	}else{
		$va{'id_orders'}='---'
	}
	&Do_SQL("update sl_tracking_email set Status='Active' where Status='New' and ID_tracking_email=$in{'id_tracking_email'} ");
	&auth_logging('email_viewed',$in{'id_tracking_email'});
	if($in{'email_action'}eq'to_archived'){
		my $moved_status=&move_imap_email($in{'uid'},'[Gmail]/All Mail');
		#&cgierr("Message:".ref($moved_status));
		if(ref($moved_status) ne 'Mail::IMAPClient'){
			$in{'message'}="The email has been moved to the Archived folder with the new id: $moved_status";
			&Do_SQL("update sl_tracking_email set Status='Archived' where ID_tracking_email=$in{'id_tracking_email'}");
			&auth_logging('email_moved_to_archived',$in{'id_tracking_email'});
		}else{
			$in{'message'}="The email has not been moved to the Archived folder. Maybe it was already.";
			&auth_logging('email_moved_to_archived_failed',$in{'id_tracking_email'});
		}
	}elsif($in{'email_action'}eq'to_trash'){
		my $moved_status=&move_imap_email($in{'uid'},'[Gmail]/Trash');
		if(ref($moved_status) ne 'Mail::IMAPClient'){
			$in{'message'}="The email has been moved to the Trash folder with the new id: $moved_status";
			&Do_SQL("update sl_tracking_email set Status='Deleted' where ID_tracking_email=$in{'id_tracking_email'}");
			&auth_logging('email_moved_to_deleted',$in{'id_tracking_email'});
		}else{
			$in{'message'}="The email has not been moved to the Trash folder. Maybe it was already.";
			&auth_logging('email_moved_to_deleted_failed',$in{'id_tracking_email'});
		}
	}
}


##############################################################################
sub validate_leads_flash{
##############################################################################

	if ($in{'action'}){
		
	    my ($errors) = 0;
	   
        #validate phone
        $in{'id_leads'} =~ s/-|\(|\)|\+|\.|\s//g;
		$in{'id_leads'} = int($in{'id_leads'});
		if ($in{'id_leads'} < 999999999){
			$error{'id_leads'} = &trans_txt('invalid');	
			$error{'message'} = &trans_txt('tendigitnum');
			++$errors;
		}			
 
		if($in{'contact_time'} eq ""){
			$error{'contact_time'} = &trans_txt('required');
			++$err;
		}
		if($in{'products'} eq ""){
			$error{'products'} = &trans_txt('required');
			++$err;
		}		 
		if($in{'comments'} eq ""){
			$error{'comments'} = &trans_txt('required');
			++$err;
		}

		(!$in{'status'}) and ($in{'status'}='New');
		
		#errors
		if ($errors > 0){
			print "Content-type: text/html\n\n";
			if($in{'add'}){
				print &build_page("leads_flash.html");
			}
			if($in{'edit'}){
				print &build_page("leads_flash_edit.html");
			}	
			exit;
		}
		
	}
}


sub add_leads_flash{
# --------------------------------------------------------
	if ($in{'action'}){
		if ($in{'add'}){
			$in{'contact_time'} =~ s/\|/|/g;
			$in{'products'} =~ s/\|/|/g;
		}
	}
}

sub view_leads_flash{
# --------------------------------------------------------
	if ($in{'view'}){
		$in{'contact_time'} =~  s/\|/&nbsp;-&nbsp;/g;
		$in{'products'} =~  s/\|/&nbsp;-&nbsp;/g;
		$in{'id_leads'} = &format_phone($in{'id_leads'});
	}

	if ($in{'chgstatus'} and $in{'chgstatus'} ne $in{'status'}){
			my ($sth) = &Do_SQL("UPDATE sl_leads_flash SET Status='$in{'chgstatus'}' WHERE ID_leads_flash = ".int($in{'id_leads_flash'})." ;");
			&auth_logging('leads_flash_st_updated',$in{'id_leads_flash'});
			$va{'message'} = trans_txt('leads_flash_st_updated');
			$in{'status'} = $in{'chgstatus'};
	}

	my (@ary) = ('New','Contacted','DoNotCall','Pending');
	for (0..$#ary){
		if ($in{'status'} ne $ary[$_]){
			$va{'changestatus'} .= qq|<a href="$script_url?cmd=[in_cmd]&view=[in_id_leads_flash]&chgstatus=$ary[$_]&tab=[in_tab]">$ary[$_]</a> : |;
			
		}
	}
	$va{'changestatus'} = substr($va{'changestatus'},0,-2);

}

#############################################################################
#############################################################################
#	Function: 
#   	view_cuaddresscust
#
#	Es: Customers Addresses View
#
#	Created by: ISC Alejandro Diaz
#
#	Modified By: 
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub view_cus_addresscust {
# --------------------------------------------------------
	$va{'company_name'} = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[company_name] / [FirstName] [LastName1] [LastName2]');
	$va{'payment_method'} = &load_name('cu_metodo_pago','ID_metodo_pago',$in{'payment_method'},'description');
	$va{'payment_type'} = &load_name('cu_forma_pago','ID_forma_pago',$in{'payment_type'},'description');
	$va{'use_cfdi_invoice'} = &load_name('cu_uso_cfdi','ID_uso_cfdi',$in{'use_cfdi_invoice'},'description');
	$va{'use_cfdi_credit'} = &load_name('cu_uso_cfdi','ID_uso_cfdi',$in{'use_cfdi_credit'},'description');
# &cgierr('>>'.$va{'payment_method'}.'<<>>'.$in{'payment_method'});
}

1;
