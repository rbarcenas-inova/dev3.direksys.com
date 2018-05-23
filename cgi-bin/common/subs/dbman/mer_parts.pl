
##########################################################
##	MERCHANDISING : PARTS
##########################################################
sub advsearch_mer_parts {
# --------------------------------------------------------
	if ($in{'notinuse'}){
		###query_sql($header_fields,$query,$id,@cols)
		return &query_sql('sl_parts.ID_parts,Model,Name,ID_categories,Status',"sl_parts LEFT JOIN sl_skus_parts ON sl_parts.ID_parts=sl_skus_parts.ID_parts WHERE ISNULL(ID_skus_parts) AND Status='Active' ORDER BY sl_parts.ID_parts",'sl_parts.ID_parts',@db_cols);
	}elsif($in{'novendor'}){
		###query_sql($header_fields,$query,$id,@cols)
		return &query_sql('sl_parts.ID_parts,Model,Name,ID_categories,Status',"sl_parts LEFT JOIN sl_parts_vendors ON sl_parts.ID_parts=sl_parts_vendors.ID_parts WHERE ISNULL(ID_parts_vendors) AND Status='Active' ORDER BY sl_parts.ID_parts",'sl_parts.ID_parts',@db_cols);
	}elsif(exists $in{'inventory'}){
		###query_sql($header_fields,$query,$id,@cols)
		if (!$in{'inventory'}){
			return &query_sql('sl_parts.ID_parts,Model,Name,ID_categories,Status',"sl_parts LEFT JOIN sl_warehouses_location ON ID_products=(400000000+ID_parts) WHERE Status='Active' AND ISNULL(Quantity) ORDER BY ID_parts",'sl_parts.ID_parts',@db_cols);
		}else{
			return &query_sql('sl_parts.ID_parts,Model,Name,ID_categories,Status',"sl_parts WHERE Status='Active' AND $in{'inventory'}(SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_products=(400000000+ID_parts)) ",'sl_parts.ID_parts',@db_cols);
		}
	}else{
		return &query('sl_parts');
	}
}

sub presearch_mer_parts {
# --------------------------------------------------------
	if ($in{'id_parts'} > 400000000){
		$in{'id_parts'} -= 400000000;
	}
	if ($in{'upc'}){
		$in{'id_parts'}= &load_name('sl_skus','UPC',$in{'upc'},'ID_products');
	}
}

sub view_mer_parts {
# --------------------------------------------------------
	if ($in{'action'}) {

		if( $in{'tab'} eq 4 ){

			my ($query);
			$in{'newpurchaseid_accounts'} = int($in{'newpurchaseid_accounts'});
			$in{'newsaleid_accounts'} = int($in{'newsaleid_accounts'});
			$in{'newassetid_accounts'} = int($in{'newassetid_accounts'});
			
			if ($in{'newpurchaseid_accounts'}){
				$query .= "PurchaseID_accounts=$in{'newpurchaseid_accounts'}," ;
				$in{'purchaseid_accounts'} = $in{'newpurchaseid_accounts'};
			}
			if ($in{'newsaleid_accounts'}){
				$query .= "SaleID_accounts=$in{'newsaleid_accounts'},";
				$in{'saleid_accounts'} = $in{'newsaleid_accounts'};
			}
			if ($in{'newassetid_accounts'}){
				$query .= "AssetID_accounts=$in{'newassetid_accounts'}," ;
				$in{'assetid_accounts'} = $in{'newassetid_accounts'};
			}
			if ($in{'newpotax'} ne ''){
				$query .= "Purchase_Tax='".&filter_values($in{'newpotax'})."',";
				$in{'purchase_tax'} = $in{'newpotax'};
			}
			if ($in{'newsaletax'} ne ''){
				$query .= "Sale_Tax='".&filter_values($in{'newsaletax'})."',";
				$in{'sale_tax'} = $in{'newsaletax'};
			}

			chop($query);
			if ($query){
				my ($sth) = &Do_SQL("UPDATE sl_parts SET $query WHERE id_parts='$in{'id_parts'}'");
				&auth_logging('mer_parts_accounting',$in{'id_parts'});
			}

		}
		
	}


	if ($in{'id_categories'}){
		$va{'catname'} = &load_name('sl_categories','ID_categories',$in{'id_categories'},'Title');
	}

	my ($sku) = 400000000+$in{'id_parts'};
	$va{'id_parts'} = &format_sltvid($sku);
	my ($sth) = &Do_SQL("SELECT VendorSKU,UPC,RefCost, RefcostPct FROM sl_skus WHERE ID_sku_products='$sku';");
	($in{'vendorsku'},$in{'upc'},$in{'refcost'},$in{'refcostpct'}) = $sth->fetchrow_array();
	$in{'refcost'} = ($in{'refcost'}) ? &format_price($in{'refcost'},2) : '$ 0.00';
	$in{'refcostpct'} = ($in{'refcostpct'}) ? $in{'refcostpct'} : '0.00 %';
	$va{'paccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'purchaseid_accounts'},'Name');
	$va{'saccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'saleid_accounts'},'Name');
	$va{'aaccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'assetid_accounts'},'Name');


	## Load Inventory
	my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE ID_products='$sku';");
	$in{'inventory'} = &format_number($sth->fetchrow);

	## Load SAT ID
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = $sku
			AND `table` = 'sl_skus'|)->fetchrow();
	$in{'id_product_service'} = $id_product_service;

}

sub loading_mer_parts {
# --------------------------------------------------------
	$va{'id_parts'} = &format_sltvid(400000000+$in{'id_parts'});

	my ($sth) = &Do_SQL("SELECT VendorSKU,UPC,RefCost,RefcostPct FROM sl_skus WHERE ID_sku_products='".(400000000+$in{'id_parts'})."';");
	($in{'vendorsku'},$in{'upc'},$in{'refcost'},$in{'refcostpct'}) = $sth->fetchrow_array();
	$in{'refcost'} = ($in{'refcost'}) ? round($in{'refcost'},2) : '0';
	$in{'refcostpct'} = ($in{'refcostpct'}) ? round($in{'refcostpct'},2) : '0';

	my $sku = 400000000+$in{'id_parts'};
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = $sku
			AND `table` = 'sl_skus'|)->fetchrow();
	$in{'id_product_service'} = $id_product_service;
	$va{'products_services'} = &build_page('products_chosen.html');
}


#############################################################################
#############################################################################
#   Function: validate_mer_parts
#
#       Es: Pre validacion de ingreso de partes
#       En: 
#
#
#    Created on: *11/16/2012*
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <validate_cols>
#
sub validate_mer_parts {
#############################################################################
#############################################################################
	my ($err);

	if ($in{'add'}){
		$in{'purchaseid_accounts'} = 1;
		$in{'saleid_accounts'} = 1;
	}

	if ($in{'upc'} and $in{'upc'} ne ''){
		my $add_sql = " AND ID_sku_products<>'".(400000000+$in{'id_parts'})."' " if ($in{'id_parts'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC='$in{'upc'}' $add_sql;");
		if ($sth->fetchrow > 0){
			$error{'upc'} = &trans_txt('mer_parts_duplicate_upc');
			++$err;
		}
	}

	return $err;	
}


sub updated_mer_parts {
# --------------------------------------------------------
# Last Modification by JRG : 03/10/2009 : Se agrega el log
	$in{'upc'} = &filter_values($in{'upc'});
	my ($sku) = 400000000 + $in{'id_parts'};
	my ($sth) = &Do_SQL("UPDATE sl_skus SET UPC='".$in{'upc'}."',VendorSKU='".&filter_values($in{'vendorsku'})."', RefCost='".$in{'refcost'}."', RefcostPct='".$in{'refcostpct'}."' WHERE  ID_sku_products='".$sku."';");
	
	$exists = &Do_SQL("SELECT count(*) FROM cu_relations_products WHERE id_table = '$sku' and `table` = 'sl_skus' ")->fetchrow();
	if($exists){


	}

	&auth_logging('sku_updated',$sku);
}

sub add_mer_parts {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: Carlos Haas
# Description : This sub add 100 before id_product into sl_skus table
#								Example id_product 123456 = 100123456 in id_sku_products each time 
#								the product is being creating in sl_products
# Parameters : 
# Last Modification by JRG : 03/11/2009 : Se agrega log
	my ($sku) = 400000000 + $in{'id_parts'};
	&Do_SQL("DELETE FROM sl_skus WHERE ID_sku_products='$sku' AND ID_products='$in{'id_parts'}';");
	my ($sth) = &Do_SQL("INSERT INTO sl_skus SET ID_sku_products='$sku',ID_products='$in{'id_parts'}',VendorSKU='$in{'vendorsku'}',UPC='$in{'upc'}',Status='Active',RefCost='$in{'refcost'}',RefcostPct='$in{'refcostpct'}',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

	&Do_SQL("INSERT INTO cu_relations_products (`id_table`, `table`, `ID_products_services`) VALUES ('$sku', 'sl_skus', '$in{'id_product_service'}')");

	&auth_logging('sku_added',$sth->{'mysql_insertid'});
}

sub loaddefault_mer_parts{
	$va{'products_services'} = &build_page('products_chosen.html');
}

1;
