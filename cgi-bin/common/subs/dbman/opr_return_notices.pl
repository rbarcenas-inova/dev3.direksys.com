
#############################################################################
#############################################################################
# Function: view_opr_return_notices
#
# Es: View de Return Notices
# En: 
#
# Created on: 14/08/2015 6:46:39 PM
#
# Author: ISC Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub view_opr_return_notices{
#############################################################################
#############################################################################
	if ($in{'id_customers'}){
		$va{'customer'} = &load_name('sl_customers','ID_customers',$in{'id_customers'},'company_name');
	}
	if ($in{'id_carriers'}){
		$va{'carrier'} = &load_name('sl_carriers','ID_carriers',$in{'id_carriers'},'Name');
	}
	if ($in{'id_customers_addresses'}){
		$sql = ("SELECT
		UPPER(CONCAT(cu_customers_addresses.cu_Street
		,IF(cu_customers_addresses.cu_Num<>'',CONCAT(' ',cu_customers_addresses.cu_Num),'')
		,IF(cu_customers_addresses.cu_Num2<>'',CONCAT(' ',cu_customers_addresses.cu_Num2),'')
		,IF(cu_customers_addresses.cu_Urbanization<>'',CONCAT('<br> COL. ',cu_customers_addresses.cu_Urbanization),'')
		,IF(cu_customers_addresses.cu_City<>'',CONCAT('<br> ',cu_customers_addresses.cu_City),'')
		,IF(cu_customers_addresses.cu_State<>'',CONCAT(', ',cu_customers_addresses.cu_State),'')
		,IF(cu_customers_addresses.cu_Zip<>'',CONCAT('<br> CP ',cu_customers_addresses.cu_Zip),'')))Address
		, Alias
		FROM cu_customers_addresses
		WHERE ID_customers_addresses='$in{'id_customers_addresses'}';");
		my $sth = &Do_SQL($sql);
		my ($address, $alias) = $sth->fetchrow_array();
		$va{'customer_addresses'} = $alias;
		$va{'customer_addresses'} .= ($address ne '')? '<br>'.$address:'';
	}
	if ($in{'id_products'} and $in{'id_products'} ne '' and $in{'update'} != 1){
		$sql = qq|SELECT IF(count(*)>0,'Yes','No')
		FROM sl_orders
		INNER JOIN sl_orders_products on sl_orders_products.ID_orders = sl_orders.ID_orders
		WHERE sl_orders.ID_customers = $in{'id_customers'} 
		AND sl_orders_products.Related_ID_products = (400000000+$in{'id_products'})
		AND sl_orders_products.Status NOT IN('Inactive','Order Cancelled')|;
		my $sth = &Do_SQL($sql);
		my ($sold) = $sth->fetchrow_array();

		&Do_SQL("INSERT INTO sl_return_notices_skus (ID_return_notices,ID_products,Sold) values('$in{'id_return_notices'}',(400000000+$in{'id_products'}),'$sold');");
		&auth_logging('opr_return_notices_sku_added',$in{'id_return_notices'});
	}
	
	## Add SKU
	if ($in{'update'} and $in{'update'}==1){
		$delimiter = quotemeta('|');
		my @id_return_notices_skus = split(/$delimiter/, $in{'ids[]'});
		my @price = split(/$delimiter/, $in{'price[]'});
		my @quantity = split(/$delimiter/, $in{'q[]'});
		my @quantity_received = split(/$delimiter/, $in{'rcp[]'});
		my $i = 0;
		
		foreach $r (@id_return_notices_skus) {
			&Do_SQL("UPDATE sl_return_notices_skus set Qty='@quantity[$i]' ,SalePrice='@price[$i]' ,RcpQty='@quantity_received[$i]' WHERE ID_return_notices_skus='@id_return_notices_skus[$i]'");
			$i++;
		}
	}
	## Remove SKU

	if ($in{'remove'} and $in{'remove'}==1 and $in{'id_return_notices_skus'}){

		&Do_SQL("DELETE FROM sl_return_notices_skus WHERE ID_return_notices_skus = $in{'id_return_notices_skus'} LIMIT 1;");
		&auth_logging('opr_return_notices_sku_removed',$in{'id_return_notices'});
	}

	## Change Status
	if ($in{'chgstatusto'} and $in{'chgstatusto'} ne ''){
		if (&check_permissions('opr_return_notices_chgstatus','','')){
			&Do_SQL("UPDATE sl_return_notices SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_return_notices='$in{'id_return_notices'}'");
			&auth_logging('opr_return_notices_chgstatus_'.lc($in{'chgstatusto'}),$in{'id_return_notices'});
			$in{'status'} = $in{'chgstatusto'};
		}else{
			$va{'message'} = qq| <span class="smallfieldterr">|.&trans_txt('unauth_action').qq|</span>|;
		}

	}

	my (@ary) = &load_enum_toarray('sl_return_notices','Status');
	for (0..$#ary){
		if ($ary[$_] ne $in{'status'}){
			$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_return_notices&view=$in{'id_return_notices'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
		}
	}


	# ($in{'amount'},%fees) = &calculate_fees($in{'id_orders'},$in{'id_orders_products'});
	$in{'amount'} = &format_price($in{'amount'});
	$in{'sprice'} = &format_price($in{'sprice'});

	$va{'div_exchange'} = $in{'meraction'} eq 'Exchange' ? 'block' : 'none';
	$va{'div_reship'} = $in{'meraction'} eq 'ReShip' ? 'block' : 'none';

	$va{'id_products_exchange'} = &format_sltvid($in{'id_products_exchange'});

}

1;