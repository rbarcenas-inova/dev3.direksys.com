#############################################################################
#############################################################################
#   Function: calculate_taxes
#
#       Es: Revisa la direccion fiscal, para calcular la tasa de impuesto que se aplicara al cobro
#-
#       En: 
#
#
#    Created on: 20/01/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - 
#
#   Parameters:
#
#      - zip: Codigo Postal
#      - state: Nombre del Estado
#      - city: Nombre del Municipio
#      - id_orders: ID de la orden
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub calculate_taxesssss {
######################################################################
######################################################################
#	
	my ($zip,$state,$city,$id_orders) = @_;
	my ($taxes,$thisdate);
	my ($taxes, $city_tax);

	## Buscamos la fecha base
	if($id_orders > 0){
		my($sth) = &Do_SQL("SELECT Date FROM sl_orders WHERE ID_orders = '$id_orders';");
		$thisdate = $sth->fetchrow();

	}else{
		$thisdate = &get_sql_date();
	}

	if(length($zip) == 5) {
		my ($sth) = &Do_SQL("SELECT StateFullName, City FROM sl_zipcodes WHERE ZipCode='$zip' GROUP BY StateFullName ORDER BY StateFullName LIMIT 1;");
		my ($state_name, $city_name) = $sth->fetchrow();

		my ($sthc) = &Do_SQL("SELECT IF(SUM(Tax) IS NULL,0,SUM(Tax))ASTax FROM sl_taxstate WHERE State = '$state_name' AND Status='Active' AND ToDate >= '$thisdate' ORDER BY ToDate LIMIT 1;");
		$taxes += $sthc->fetchrow() / 100;
		
		my($sth) = &Do_SQL("SELECT IF(SUM(Tax) IS NULL,0,SUM(Tax))AS Tax FROM sl_taxcity WHERE lower(State) = lower('$state_name') AND lower(city)=lower('$city_name') AND Status='Active' AND FromDate <= '$thisdate' AND ToDate >= '$thisdate' ORDER BY ToDate LIMIT 1;");
		$taxes += $sth->fetchrow() / 100;
	}

	
	return $taxes;
}

#############################################################################
#############################################################################
#   Function: view_ea_opr_customers
#
#       Es: Se ejecuta despues de la funcion view_opr_customers
#       En: 
#
#
#    Created on: 2016-07-04
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** : 
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
#      <>
#
sub view_ea_opr_customers {
	## SAT Info for customer
	my $sth = &Do_SQL("SELECT 
		UPPER(RFC)RFC
		, UPPER(cu_customers_addresses.Address1)Address1
		, UPPER(cu_customers_addresses.Address2)Address2
		, UPPER(cu_customers_addresses.Address3)Address3
		, UPPER(cu_customers_addresses.Urbanization)Urbanization
		, UPPER(cu_customers_addresses.City)City
		, UPPER(cu_customers_addresses.State)State
		, UPPER(cu_customers_addresses.Zip)Zip
		, UPPER(cu_customers_addresses.Country)Country
		, UPPER(cu_customers_addresses.Account_Number)Account_Number
		, UPPER(cu_customers_addresses.Payment_Type)Payment_Type
		, UPPER(cu_customers_addresses.Use_Cfdi_invoice)Use_Cfdi_invoice
		, UPPER(cu_customers_addresses.Use_Cfdi_credit)Use_Cfdi_credit
		, UPPER(cu_customers_addresses.FCode_Bank)FCode_Bank
		, UPPER(cu_customers_addresses.Bank)Bank
		, cu_customers_addresses.Payment_Method
		FROM cu_customers_addresses
		INNER JOIN sl_customers ON cu_customers_addresses.ID_customers=sl_customers.ID_customers
		WHERE cu_customers_addresses.ID_customers = $in{'id_customers'}
		AND cu_customers_addresses.PrimaryRecord='Yes'
		LIMIT 1;");
	my $rec = $sth->fetchrow_hashref();
	$va{'legal_rfc'} = $rec->{'RFC'};
	$va{'legal_address'} = ($rec->{'Address1'} ne '')? $rec->{'Address1'}:'';
	$va{'legal_address'} .= ($rec->{'Address2'} ne '')? ' '.$rec->{'Address2'}:'';
	$va{'legal_urbanization'} = $rec->{'Urbanization'};
	$va{'legal_city'} = $rec->{'City'};
	$va{'legal_state'} = $rec->{'State'};
	$va{'legal_zip'} = $rec->{'Zip'};
	$va{'legal_country'} = $rec->{'Country'};
	$va{'payment_method'} = $rec->{'Payment_Method'};

	$va{'payment_method_des'} = &load_name('cu_metodo_pago','ID_metodo_pago',$rec->{'Payment_Method'},'description');
	$va{'payment_type_des'} = &load_name('cu_forma_pago','ID_forma_pago',$rec->{'Payment_Type'},'description');
	$va{'use_cfdi_invoice_des'} = &load_name('cu_uso_cfdi','ID_uso_cfdi',$rec->{'Use_Cfdi_invoice'},'description');
	$va{'use_cfdi_credit_des'} = &load_name('cu_uso_cfdi','ID_uso_cfdi',$rec->{'Use_Cfdi_credit'},'description');

	$va{'customers_sat_info'} = &build_page("func/customers_sat_info.html")

}

1;