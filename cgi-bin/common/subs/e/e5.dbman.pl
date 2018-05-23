
#############################################################################
#############################################################################
#   Function: loaddefault_mer_vendors
#
#       Es: Carga valores por defecto para sl_vendors
#       En: 
#
#
#    Created on: 
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
#      <>
#
sub loaddefault_mer_vendors{
#############################################################################
#############################################################################

	$in{'country'} = 'Mexico';
	$in{'type'} = 'Bienes';
	$in{'category'} = 'Nacional';
	$in{'paymentmethod'} = 'Check';
	$in{'taxcountry'} = 'Mexico';
	$in{'taxprd'} = '16';
	$in{'taxser'} = '16';
	$in{'accountingtemplate'} = 'Nacionales';
	$in{'status'} = 'Active';

}

#############################################################################
#############################################################################
#   Function: view_ea_mer_po
#
#       Es: Para empresas de MX, se revisa calculo de impuestos en sku agregado
#       En: For Mx companies, adds last PO sku tax
#
#
#    Created on: 2013-02-28
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
#      <>
#
sub view_ea_mer_po {
#############################################################################
#############################################################################
	
	if ($in{'additem'}) {

		my ($sth) = &Do_SQL("SELECT ID_purchaseorders_items FROM sl_purchaseorders_items WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_items DESC LIMIT 1;");
		my ($id_new) = $sth->fetchrow();

		if($id_new) {

			my $tvendor = &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Category');

			if(lc($tvendor) eq 'nacional') {

				my $taxp = substr($in{'additem'},0,1) == 4 ? &load_name('sl_parts','ID_parts',substr($in{'additem'},-4),'Purchase_Tax')/100 : $cfg{'taxp_default'};
				$taxp = 0 if !$taxp;
				my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Tax = Qty * Price * $taxp, Tax_percent = '$taxp' WHERE ID_purchaseorders_items = '$id_new';");
				my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_items SET Total = Qty * Price + Tax  WHERE ID_purchaseorders_items = '$id_new';");
				delete($in{'additem'});
				&build_po_list();

			}

		}		

	}

}


#############################################################################
#############################################################################
#   Function: add_opr_orders
#
#       Es: Para ordenes creadas en administration. Se guarda siempre un ID_customers_address
#       En: For admin orders, ID_customers_addresses must be saved always
#
#
#    Created on: 2013-02-28
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
#      <add_ea_opr_orders> /cgi-bin/common/subs/dbman/opr_orders.pl
#
sub add_opr_orders {
#############################################################################
#############################################################################
	
	if($in{'id_orders'} and !$in{'id_customers_addresses'}) {

		my ($sth) = &Do_SQL("SELECT sl_orders.ID_customers_addresses, cu_customers_addresses.ID_customers_addresses 
		                    FROM sl_orders LEFT JOIN cu_customers_addresses USING(ID_customers) WHERE PrimaryRecord = 'Yes';");
		my ($idca_orders, $idca_customers) = $sth->fetchrow();

		if(!$idca_orders and $idca_customers) {
			my ($sth) = &Do_SQL("UPDATE sl_orders SET ID_customers_addresses = '$idca_customers' WHERE ID_orders = '$in{'id_orders'}';");
		}
	}
	&Do_SQL("UPDATE sl_orders SET ID_salesorigins = IF(ID_salesorigins = 0,1,ID_salesorigins) WHERE ID_orders = '$in{'id_orders'}';");
}


#############################################################################
#############################################################################
#   Function: validate_eb_mer_bills
#
#       Es: Se ejecuta antes de validar el formulario en mer_bills
#       En: 
#
#
#    Created on: 2013-03-15
#
#    Author: Aljandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
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
sub validate_eb_mer_bills {
#############################################################################
#############################################################################
	if($in{'id_vendors'} and !$in{'currency'}) {
		$in{'currency'}= &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency');
		$va{'companyname'}= &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'CompanyName');
	}
}

1;