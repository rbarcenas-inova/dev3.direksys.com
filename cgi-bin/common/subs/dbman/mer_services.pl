
sub view_mer_services {
# --------------------------------------------------------
	if ($in{'action'} and $in{'tab'} eq 4){
		my ($query);
		$in{'newsaleid_accounts'} = int($in{'newsaleid_accounts'});
		if ($in{'newsaleid_accounts'}){
			$query .= "SaleID_accounts=$in{'newsaleid_accounts'},";
			$in{'saleid_accounts'} = $in{'newsaleid_accounts'};
		}
		if ($in{'newtax'}){
			$query .= "Tax='".&filter_values($in{'newtax'})."',";
			$in{'tax'} = $in{'newtax'};
		}

		if( $in{'servicetype'} eq 'Purchase' ){
			$in{'newpurchaseid_accounts'} = int($in{'newpurchaseid_accounts'});
			if ($in{'newpurchaseid_accounts'}){
				$query = "PurchaseID_accounts=$in{'newpurchaseid_accounts'},";
				$in{'purchaseid_accounts'} = $in{'newpurchaseid_accounts'};
			}
			# $in{'newtaxpurchaseid_accounts'} = int($in{'newtaxpurchaseid_accounts'});
			# if ($in{'newtaxpurchaseid_accounts'}){
			# 	$query .= "TaxPurchaseID_accounts=$in{'newtaxpurchaseid_accounts'},";
			# 	$in{'purchasetaxid_accounts'} = $in{'newtaxpurchaseid_accounts'};
			# }
			if ($in{'purchase_newtax'}){
				$query .= "Tax='".&filter_values($in{'purchase_newtax'})."',";
				$in{'tax'} = $in{'purchase_newtax'};
			}			
		}

		chop($query);
		if ($query){
			my ($sth) = &Do_SQL("UPDATE sl_services SET $query WHERE id_services='$in{'id_services'}'");
			&auth_logging('mer_services_accounting',$in{'id_services'});
		}

	}
	if ($in{'salesprice'} eq 'Fixed'){
		$in{'sprice'} = &format_price($in{'sprice'});
	}else{
		$in{'sprice'} = $in{'sprice'} . " %";
	}

	if( $in{'servicetype'} eq 'Purchase' ){
		$va{'paccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'purchaseid_accounts'},'Name');
		$va{'show_account_purchase'} = 'display: table-row;';
		$va{'show_account_sale'} = 'display: none;';
	} else {
		$va{'saccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'saleid_accounts'},'Name');
		$va{'show_account_purchase'} = 'display: none;';
		$va{'show_account_sale'} = 'display: table-row;';
	}

	## Load SAT ID
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = $in{'view'}
			AND `table` = 'sl_services'|)->fetchrow();
	
	$in{'id_product_service'} = $id_product_service;
 
}


sub loading_mer_services {
	my $id_product_service = &Do_SQL(qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		FROM cu_relations_products
		INNER JOIN cu_products_services on cu_products_services.ID_product_service = cu_relations_products.ID_products_services
		WHERE 1
			AND id_table = $in{'modify'}
			AND `table` = 'sl_services'|)->fetchrow();
	$in{'id_product_service'} = $id_product_service;

	$va{'products_services'} = &build_page('products_chosen.html');
}

sub updated_mer_services {

	$exists = &Do_SQL("SELECT count(*) FROM cu_relations_products WHERE id_table = '$in{'id_services'}' and `table` = 'sl_services' ")->fetchrow();
	if($exists){
		$in{'id_product_service'} =~ s/\D//g;
		&Do_SQL("UPDATE cu_relations_products SET `ID_products_services` = '$in{'id_product_service'}' WHERE `id_table` = '$in{'id_services'}' AND `table` = 'sl_services'");
	}else{
		&Do_SQL("INSERT INTO cu_relations_products (`id_table`, `table`, `ID_products_services`) VALUES ($in{'id_services'}, 'sl_services', '$in{'id_product_service'}')");
		
	}
}

sub add_mer_services {
	$in{'id_product_service'} =~ s/\D//g;
	&Do_SQL("INSERT INTO cu_relations_products (`id_table`, `table`, `ID_products_services`) VALUES ( $in{'id_services'}, 'sl_services', '$in{'id_product_service'}')");
}
sub loaddefault_mer_services{
	$va{'products_services'} = &build_page('products_chosen.html');
}
1;
