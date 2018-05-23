#RB Start - Modify sl_noninv => sl_services - apr2408
##########################################################
##	MERCHANDISING : NONINV
##########################################################
sub view_mer_services {
# --------------------------------------------------------
	$va{'id_services'} = &format_sltvid(600000000+$in{'id_services'});
	my ($sth) = &Do_SQL("SELECT VendorSKU,UPC FROM sl_skus WHERE ID_sku_products='".(600000000+$in{'id_services'})."';");
	($in{'vendorsku'},$in{'upc'}) = $sth->fetchrow_array();

	## Packing Options
	if ($in{'id_products_related'}){
		$in{'productname'} = &load_name('sl_products','ID_products',substr($in{'id_products_related'},-6),'Name');
		$va{'product_related'} = qq|(<a href="$script_url?cmd=mer_products&view=|.substr($in{'id_products_related'},-6).qq|">|.&format_sltvid($in{'id_products_related'}).qq|</a>)  [in_productname]|;
	}

	## Packing Options
	if ($in{'id_packingopts'}){
		$in{'pckoptsname'} = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Name');
		$in{'shpcharges'}  = &load_name('sl_packingopts','ID_packingopts',$in{'id_packingopts'},'Shipping');
		$in{'shpcharges'}  = &format_price($in{'shpcharges'});

		$va{'shipping_options'} = qq|([in_shpcharges]) [in_pckoptsname]</td>|;
	}

}

sub loading_mer_services {
# --------------------------------------------------------
	$va{'id_services'} = &format_sltvid(600000000+$in{'id_services'});

	my ($sth) = &Do_SQL("SELECT VendorSKU,UPC FROM sl_skus WHERE ID_sku_products='".(600000000+$in{'id_services'})."';");
	($in{'vendorsku'},$in{'upc'}) = $sth->fetchrow_array();
}

sub validate_mer_services {
# --------------------------------------------------------
# Author: Unknown
# Created on: Unknown
# Last Modified on: 10/10/2008
# Last Modified by: Jose Ramirez Garcia
# Description : 
# Forms Involved: 
# Parameters : validate the id_products_related on refill option

	if ($in{'upc'}){
		$in{'upc'} = int($in{'upc'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC='$in{'upc'}' AND ID_sku_products<>'".(600000000+$in{'id_services'})."';");
		if ($sth->fetchrow>0){
			$error{'upc'} = &trans_txt('invalid');
			++$err;
		}
	}

	## Refill
	if($in{'servicetype'} eq "Refill" and (!$in{'id_products_related'} or !$in{'refill_sprice'} or !$in{'id_packingopts'} or !$in{'days'}) ){
		$va{'message'} = &trans_txt('reqfields');
		$error{'id_products_related'} = &trans_txt('required');
		$error{'refill_sprice'} = &trans_txt('required');
		$error{'id_packingopts'} = &trans_txt('required');
		$error{'days'} = &trans_txt('required');
		++$err;
	} elsif($in{'servicetype'} eq "Refill" and $in{'id_products_related'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_products='".substr($in{'id_products_related'},3,6)."'");
		if ($sth->fetchrow != 1){
			$va{'message'} = &trans_txt('reqfields');
			$error{'id_products_related'} = &trans_txt('invalid');
			++$err;
		}
	}
	if($in{'servicetype'} eq "Refill" && !$in{'days'}){
		$va{'message'} = &trans_txt('reqfields');
		$error{'days'} = &trans_txt('required');
		++$err;
	}
	if($in{'servicetype'} eq "Refill" && $in{'days'}<1){
		$va{'message'} = &trans_txt('reqfields');
		$error{'days'} = &trans_txt('invalid');
		++$err;
	}	
}


sub updated_mer_services {
# --------------------------------------------------------
# Last Modification by JRG : 03/10/2009 : Se agrega el log
	$in{'upc'} = int($in{'upc'});
	my ($sth) = &Do_SQL("UPDATE sl_skus SET UPC='$in{'upc'}',VendorSKU='".&filter_values($in{'vendorsku'})."' WHERE  ID_sku_products='".(600000000+$in{'id_services'})."';");
	&auth_logging('sku_updated',(600000000+$in{'id_services'}));
}


##########################################################
##	MERCHANDISING : PRODUCTS CATEGORIES 		  ##
##########################################################
sub view_mer_categories {
# --------------------------------------------------------
	if (!$in{'id_parent'}){
		$in{'parentname'} = &trans_txt('top_level');
	}else{
		$in{'parentname'} = &load_name('sl_categories','ID_categories',$in{'id_parent'},'Title');
	}
}


sub view_mer_properties {
# --------------------------------------------------------
	if (!$in{'id_parent'}){
		$in{'parentname'} = &trans_txt('top_level');
	}else{
		$in{'parentname'} = &load_name('sl_categories','ID_categories',$in{'id_parent'},'Title');
	}
}

##########################################################
##		MERCHANDISING : PACKING OPTIONS	 		  ##
##########################################################
sub view_mer_packingopts {
# --------------------------------------------------------
	$in{'cost'} = &format_price($in{'cost'});
	$in{'shipping'} = &format_price($in{'shipping'});	
}



##########################################################
##	MERCHANDISING :	ITEM TRANSFER 		  ##
##########################################################

#sub view_mer_itemtransfers {
## --------------------------------------------------------
## Forms Involved: 
## Created on: 1/1/2007 9:43AM
## Last Modified on:
## Last Modified by:
## Author: 
## Description : 
## Parameters : 
## Last Modified on: 06/08/09 13:39:59
## Last Modified by: MCC C. Gabriel Varela S: Se comenta.
#
#	if ($in{'done'}){
#		my ($err,$query);
#		my ($sth) = &Do_SQL("SELECT * FROM  sl_manifests_items WHERE ID_manifests='$in{'id_manifests'}'");
#		while ($rec = $sth->fetchrow_hashref){
#			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE ID_warehouses_location='$rec->{'ID_warehouses_location'}' AND Quantity>=$rec->{'Qty'}");
#			if ($sth2->fetchrow == 0){
#				++$err;
#			}else{
#				$query .= "UPDATE sl_warehouses_location SET Quantity=Quantity-$rec->{'Qty'} WHERE ID_warehouses_location='$rec->{'ID_warehouses_location'}';\n";
#				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_location WHERE Location='$rec->{'Location'}' AND ID_products='$rec->{'ID_products'}'");
#				if ($sth2->fetchrow>0){
#					$query .= "UPDATE sl_warehouses_location SET Quantity=Quantity+$rec->{'Qty'} WHERE ID_warehouses_location='$rec->{'ID_warehouses_location'}';\n";	
#				}else{
#					$query .= "INSERT INTO sl_warehouses_location SET ID_warehouses=$in{'towarehouse'}, ID_products='$rec->{'ID_products'}', Location='$rec->{'Location'}', Quantity=$rec->{'Qty'}, Date=Curdate(), Time=NOW(), ID_admin_users='$usr{'id_admin_users'}';\n";	
#				}
#			}
#		}
#		if ($err){
#			$va{'message'} =&trans_txt('manifest_error');
#		}else{
#			$in{'status'} = 'Processed';
#			$in{'processedby'} = $usr{'id_admin_users'};
#			
#			$query .= "UPDATE sl_manifests SET Status='Processed', ProcessedBy='$usr{'id_admin_users'}', ProcessedDate=Curdate() WHERE ID_manifests='$in{'id_manifests'}';\n";
#			$query .= "DELETE FROM sl_warehouses_location WHERE Quantity=0;\n";
#			
#			#$query =~ s/\n/<br><br><br>/g;
#			#$va{'message'} = $query;
#			
#			my ($sth) = &Do_mSQL("START TRANSACTION;\n$query\nCOMMIT;");
#			&auth_logging('manifest_done',$in{'id_manifests'});
#			$va{'message'} =&trans_txt('manifest_done');
#		}
#	}
#	
#	if ($in{'fromwarehouse'}){
#		$va{'from_name'} = &load_name('sl_warehouses','ID_warehouses',$in{'fromwarehouse'},'Name');
#	}else{
#		$va{'from_name'} = '---';
#	}
#	
#	if ($in{'towarehouse'}){
#		$va{'to_name'} = &load_name('sl_warehouses','ID_warehouses',$in{'towarehouse'},'Name');
#	}else{
#		$va{'to_name'} = '---';
#	}
#	
#	if ($in{'requestedby'}){
#		$va{'reqname'} = &load_db_names('admin_users','ID_admin_users',$in{'requestedby'},'[LastName], [FirstName]');
#	}else{
#		$va{'reqname'} = '---';
#	}
#	
#	if ($in{'authorizedby'}){
#		$va{'reqauth'} = &load_db_names('admin_users','ID_admin_users',$in{'authorizedby'},'[LastName], [FirstName]');
#	}else{
#		$va{'reqauth'} = '---';
#	}
#	
#	if ($in{'status'} eq 'Processed'){
#		$va{'statusmsg'} = " &nbsp;&nbsp; ($in{'processedby'}) ";
#		if ($in{'processedby'}){
#			$va{'statusmsg'} .= &load_db_names('admin_users','ID_admin_users',$in{'processedby'},'[LastName], [FirstName]') . " &nbsp; $in{'processeddate'}";
#		}
#	}else{
#		$in{'status'} = "$in{'status'} &nbsp;&nbsp; ".&trans_txt('change_to'). " : <a href='$script_url?cmd=manifests&view=$in{'id_manifests'}&done=1'>Processed</a>";
#	}
#}




#RB Start
sub add_mer_services {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/27/2008 12:09PM
# Last Modified on:
# Last Modified by: Roberto Barcenas
# Author: Carlos Haas
# Description : This sub add 600000000 before id_product into sl_skus table
#								Example id_product 123456 = 100123456 in id_sku_products each time 
#								the product is being creating in sl_products
# Parameters : 
# Last Modification by JRG : 03/11/2009 : Se agrega log

	my ($sku) = 600000000 + $in{'id_services'};
	my ($sth) = &Do_SQL("INSERT INTO sl_skus SET ID_sku_products='$sku',ID_products='$in{'id_services'}',Status='Active',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
	&auth_logging('sku_added',$sth->{'mysql_insertid'});
}
#RB End


sub load_descriptions {
# --------------------------------------------------------
# Forms Involved: products_view.html
# Created on: 9/10/2007
# Last Modified on: 7/17/2007
# Last Modified by:	Rafael Sobrino
# Author: Rafael Sobrino
# Description : loads all the descriptions and the html editor in mer_products_view.html
	
 ### load links and fields values
	&load_links;				
	
	### passing value to html editor
	if ($in{'field'} eq "smalldescription"){ 
		$in{'speech'} = $in{'smalldescription'};
	}elsif ($in{'field'} eq "description"){ 
		$in{'speech'} = $in{'description'}; 
	}elsif ($in{'field'} eq "smalldescription_en"){ 
		$in{'speech'} = $in{'smalldescription_en'};
	}elsif ($in{'field'} eq "description_en"){
		$in{'speech'} = $in{'description_en'}; 	
	}elsif ($in{'field'} eq "countryorigin"){
		$in{'speech'} = $in{'countryorigin'}; 		
	}else{ 
		$in{'speech'} = $in{'disclaimer'}; 
	}


	### Edit variable values			
	$temp = qq|
		<tr>
			<td colspan="2">		
			  <form action="/cgi-bin/mod/admin/dbman" method="post" name="sitform">
					<input type="hidden" name="cmd" value="mer_products">
					<input type="hidden" name="action" value="1">
					<input type="hidden" name="field_name" value="[in_field]">
					<input type="hidden" name="view" value="[in_id_products]">								
					<input type="hidden" name="update" value="1">				
					<table border="0" cellspacing="0" cellpadding="2" width="100%">
						<tr>
							<td valign="top" class="smalltext">[fc_build_html_textbox]</td>
						</tr>
						<tr>
							<td align="center"><input type="submit" value="Update" class="button"></td>
						</tr>
					</table>
				</form>									
			</td>
		</tr> |;
		
	$va{'edit_smalldescription'} = $in{'field'} eq "smalldescription" ? $temp : "&nbsp;";
	$va{'edit_description'} = $in{'field'} eq "description" ? $temp : "&nbsp;";
	$va{'edit_smalldescription_en'} = $in{'field'} eq "smalldescription_en" ? $temp : "&nbsp;";
	$va{'edit_description_en'} = $in{'field'} eq "description_en" ? $temp : "&nbsp;";	
	$va{'edit_disclaimer'} = $in{'field'} eq "disclaimer" ? $temp : "&nbsp;";	
	$va{'edit_countryorigin'} = $in{'field'} eq "countryorigin" ? $temp : "&nbsp;";	
}

sub validate_mer_categories{
# --------------------------------------------------------
# Created on: 08/06/2016
# Last Modified on:
# Last Modified by:
# Author: Jonathan Alcantara
# Description : Agrega validacion extra al id_parent para que por default salga en 0 y no NULL

	if( ! $in{'id_parent'} or $in{'id_parent'} eq '---'){
		$in{'id_parent'} = 0;
	}
}

1;

