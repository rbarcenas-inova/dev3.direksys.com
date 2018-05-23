###############################################################
############            CALCULATE TAXES         ###############
###############################################################

#############################################################################
#############################################################################
#   Function: get_deposit_type
#
#       Es: Devuelve el tipo al que pertenece el pago
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *10/07/2011* by _Roberto Barcenas_ : Se agrega Amazon
#        - Modified on *02/15/2012* by _Roberto Barcenas_ : Se agrega Descuentolibre
#		 - Modified on *06/13/2014* by _Roberto Barcenas_ : Se integra variable overwrite_ptype para especificar un tipo de pago a devolver
#
#   Parameters:
#
#      - idpayment: ID Payment  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_deposit_type {
#############################################################################
#############################################################################

	my($idpayment,$keypoint) = @_;
	my ($type);
	my $this_field = $cfg{'acc_deposit_type'} ? $cfg{'acc_deposit_type'} : 'Type';

	####
	#### CC Type Detection (based on bines)
	####
	my $this_cc_type = &get_bin_creditcard_type($idpayment, 'Keypoint_Type');
	$in{'overwrite_ptype'} = $this_cc_type if $this_cc_type ne '';


	if($in{'overwrite_ptype'}){

		$type = $in{'overwrite_ptype'};

	}elsif($idpayment) {
		
		if($in{'ida_banks'}) {
			
			### Recibimos id del banco que recibio el pago.
			my ($sth) = &Do_SQL("SELECT Type FROM sl_keypoints_movements WHERE ID_accounts_debit = '$in{'ida_banks'}' AND Keypoint = '".$keypoint."';");
			$type = $sth->fetchrow();

		}else{

			###  Tenemos que buscar el banco de acuerdo a campos en sl_orders_payments.
			# my $sth = &Do_SQL("/*  */ SELECT LOWER(IF($this_field IS NOT NULL AND $this_field <> '',$this_field,Type)) As PType FROM sl_orders_payments WHERE ID_orders_payments = $idpayment ");
			my $sth = &Do_SQL("/*  */ SELECT LOWER(IF($this_field IS NOT NULL AND $this_field <> '',$this_field,IF('$cfg{'acc_deposit_type_default'}' != '', '$cfg{'acc_deposit_type_default'}',Type))) As PType FROM sl_orders_payments WHERE ID_orders_payments = '$idpayment';");
			$type =  $sth->fetchrow();

		}

		## If type is a number, change to default
		((!$type or $type =~ /^\d/) and $cfg{'acc_deposit_type_default'}) and ($type = $cfg{'acc_deposit_type_default'});

	}
	
	return $type;
}


sub calculate_taxes {
# --------------------------------------------------------
# Last Modified by RB on 04/15/2011 11:15:54 AM : Se agrega $idorders para buscar posible fecha de envio y basar los taxes en ella 
# Last Modified by RB on 07/01/2011 03:39:13 PM : Se cambia la regla de fecha de calculo. La fecha de calculo para el tax rate es la fecha de creacion de la orden.
	my ($zip,$state,$city,$id_orders) = @_;
	my ($taxes,$thisdate);

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

		my ($sthc) = &Do_SQL("SELECT IF(SUM(Tax) IS NULL,0,SUM(Tax))ASTax FROM sl_taxstate WHERE State = '$state_name' AND Status='Active' AND (ToDate >= '$thisdate' OR ToDate IS NULL) ORDER BY ToDate LIMIT 1;");
		my ($this_s) = $sthc->fetchrow(); 
		($this_s > 0) and ($taxes +=  $this_s / 100);
		
		my($sth) = &Do_SQL("SELECT IF(SUM(Tax) IS NULL,0,SUM(Tax))AS Tax FROM sl_taxcity WHERE lower(State) = lower('$state_name') AND lower(city)=lower('$city_name') AND Status='Active' AND (FromDate <= '$thisdate' OR FromDate IS NULL) AND (ToDate >= '$thisdate' OR ToDate IS NULL) ORDER BY ToDate LIMIT 1;");
		my ($this_c) = $sthc->fetchrow(); 
		($this_c >0) and ($taxes +=  $this_c / 100);

	}
	
	return $taxes;
	

}

sub ordersproducts_list {
# --------------------------------------------------------
	my ($status,$id,$color) = @_;
	my ($rec,$output);
	$output = "</td></tr><tr bgcolor='$color'><td colspan='8' class='smalltext'>";
	my ($sth) = &Do_SQL("SELECT * FROM sl_products,sl_orders_products WHERE ID_orders='$id' AND RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products AND sl_orders_products.Status='Active'");
	while ($rec = $sth->fetchrow_hashref){
		$output .=  &format_sltvid(substr($rec->{'ID_products'},3,6))." $rec->{'Name'}<br>\n";
	}
	return $output;
}

sub orderspayments_list {
# --------------------------------------------------------
	my ($status,$id,$color) = @_;
	my ($rec,$output);
	$output = "</td></tr><tr bgcolor='$color'><td colspan='8' class='smalltext'>";
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$id'");
	while ($rec = $sth->fetchrow_hashref){
		$output .=  " $rec->{'Type'} ".&format_price($rec->{'Amount'})." $rec->{'Paymentdate'} $rec->{'Status'} $rec->{'AuthCode'}<br>\n";
	}
	return $output;
}


sub insert_prn_manifest {
# --------------------------------------------------------
	my ($type,$idorder,$idpayment,$idprod)= @_;

	if ($type eq 'toprocess'){
		my ($ds,$prds);
		## Check if is a DS Order
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_orders`,sl_orders_products WHERE sl_orders.ID_orders='$idorder' AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active' AND 'Yes'=(SELECT DropShipment FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6))");
		$ds = $sth->fetchrow;
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_orders`,sl_orders_products WHERE sl_orders.ID_orders='$idorder' AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders_products.Status='Active'");
		$prds = $sth->fetchrow;
		if ($ds>1 and $ds==$prds){
			## All DS
			## Print Order
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='order',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Invoice w/Logo
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='inv_pdf',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Import Excel
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='export',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Print paylog
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='paylog',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		}elsif ($ds>1 and $ds =! $prds){
			## Partial DS
			## Print Order
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='order',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Invoice w/Logo
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='inv_pdf',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Import Excel
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='export',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Print paylog
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='paylog',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## PL manifest
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='pl_man',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Invoice
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='inv',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		}else{
			## All DS
			## Print Order
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='order',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## PL manifest
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='pl_man',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Invoice
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='inv',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			## Print paylog
			my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='paylog',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");			
		}
		#my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$in{'id_orders'}',ID_orders_payments='$in{'id_orders_payments'}',Type=''");
	}elsif ($type eq 'captured'){
		## Print Order
		my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='fin-inv',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
		## Invoice w/Logo
		my ($sth) = &Do_SQL("INSERT INTO sl_prnmanifest SET ID_orders='$idorder',ID_orders_payments='$idpayment',Type='fin-set',Printed='No',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	}
}



sub sltv_itemshipping {
# --------------------------------------------------------
# Created on: 07/10/08 @ 16:21:10
# Author: Carlos Haas
# Last Modified on: 07/10/08 @ 16:21:10
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
# Last Modified on: 03/17/09 16:00:32
# Last Modified by: MCC C. Gabriel Varela S: Se considera total3
# Last Modified RB: 12/06/2010  18:35:30 -- Pendiente completar nueva tabla de shipping
#

	my ($edt,$sizew,$sizeh,$sizel,$weight,$idpacking,$shpcal,$shpmdis,$id_products) = @_;
	my (%tmp);

	### Shipping US continental
	($tmp{'shptype1'},$tmp{'shptype2'},$tmp{'shptype3'}) = split(/,/,$cfg{'shp_types'});	
	($tmp{'shptype1_min'},$tmp{'shptype2_min'},$tmp{'shptype3_min'}) = split(/,/,$cfg{'shp_edt_min'});
	($tmp{'shptype1_max'},$tmp{'shptype2_max'},$tmp{'shptype3_max'}) = split(/,/,$cfg{'shp_edt_max'});	

	### Shipping Puerto Rico
	($tmp{'shptype1pr_min'},$tmp{'shptype2pr_min'},$tmp{'shptype3pr_min'}) = split(/,/,$cfg{'shppr_edt_min'});
	($tmp{'shptype1pr_max'},$tmp{'shptype2pr_max'},$tmp{'shptype3pr_max'}) = split(/,/,$cfg{'shppr_edt_max'});	
	($tmp{'shptype1pr'},$tmp{'shptype2pr'},$tmp{'shptype3pr'}) = split(/,/,$cfg{'shppr_types'});

	if ($shpcal eq 'Table'){
		##

		###
		###
		### Falta revisar toda esta parte para cuando no es inbound y no existen $cses
		###
		###


		## Zone?
		my $zone = 'USA';
		if ($cses{'shp_state'} ne ''){
			my @ary_zones = split(/:/,$cfg{'shipping_zones'}); 

			ZONES:for($i=$#ary_zones ; $i>0;$i--){
				if ($ary_zones[$i] =~ /$cses{'shp_state'}/){
					$zone = $ary_zones[$_];
					last ZONES;
				}
			}
		}

		## Method?
		my $method = 'credit-card';
		$method = lc($cses{'pay_type'}) if $cses{'pay_type'} ne '';
		$method = 'credit-card' if $method ne 'cod'; 

		## Amount ?
		my $amount = '0.01';
		$amount = $cses{'total_i'} if ($shpmdis eq 'Yes' and $cses{'total_i'} > 0);

		## Quantity
		my $quantity = 1;

		if ($shpmdis eq 'Yes'){
			## Revisar cantidad en 
			if ($cses{'items_in_basket'} > 0 ){
				for my $i(1..$cses{'items_in_basket'}){
					if ($cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0 and substr($cses{'items_'.$i.'_id'},3,6) == $id_products){
						$quantity++;
					}
				}
				$quantity--;
			}
			## 
		}

		my ($sth) = &Do_SQL("SELECT Shipping_price FROM `sl_products_shipping` WHERE ID_products = '$id_products' AND `Zone` = '$zone' AND LOWER(`Method`) = '$method' AND `Quantity` <= $quantity AND Amount <= $amount ORDER BY Amount DESC, Quantity DESC LIMIT 1; ");
		my($shprice)= $sth->fetchrow();

		$shptotal1 = $shprice;
		$shptotal2 = $shprice;	
		$shptotal3 = $shprice;	
		$shptotal1pr = $shprice;
		$shptotal2pr = $shprice;
		$shptotal3pr = $shprice;

	}elsif ($idpacking>0){
		## US Continental
		$shptotal1 = &load_name('sl_packingopts','ID_packingopts',$idpacking,'Shipping');
		$shptotal2 = $shptotal1+14;
		($cfg{'express_delivery'} and $cfg{'express_delivery_' . $cses{'pay_type'}}) and ($shptotal2 = $cfg{'express_delivery_' . $cses{'pay_type'}});
		$shptotal3 = $shptotal1;		
		#$shptotal2 = 16;
		## Puerto Rico
		$shptotal1pr = $shptotal1;
		$shptotal2pr = $shptotal1+14;
		($cfg{'express_delivery'} and $cfg{'express_delivery_' . $cses{'pay_type'}}) and ($shptotal2pr = $cfg{'express_delivery_' . $cses{'pay_type'}});
		$shptotal3pr = $shptotal1;
		##return ($shptotal1,$shptotal2,$shptotal1pr,$shptotal2pr,$shp_text1,$shp_text2,$shp_textpr1,$shp_textpr2);
		$tmp{'shptype1_min'}	+= $edt;
		$tmp{'shptype1_max'}	+= $edt;
		$tmp{'shptype2_min'}	+= $edt;
		$tmp{'shptype2_max'}	+= $edt;		
		$tmp{'shptype3_min'}	+= $edt;
		$tmp{'shptype3_max'}	+= $edt;
	}else{
		### Shipping US continental
		($tmp{'shptype1_1lb'},$tmp{'shptype2_1lb'},$tmp{'shptype3_1lb'}) = split(/,/,$cfg{'shp_factors1'});
		($tmp{'shptype1_add'},$tmp{'shptype2_add'},$tmp{'shptype3_add'}) = split(/,/,$cfg{'shp_factors2'});	
		($tmp{'shpconv1'},$tmp{'shpconv2'},$tmp{'shpconv3'}) = split(/,/,$cfg{'shp_wvconv'});

		$tmp{'shptype1_min'}	+= $edt;
		$tmp{'shptype1_max'}	+= $edt;
		$tmp{'shptype2_min'}	+= $edt;
		$tmp{'shptype2_max'}	+= $edt;
		$tmp{'shptype3_min'}	+= $edt;
		$tmp{'shptype3_max'}	+= $edt;

		## Shipping type 1
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv1'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal1 = int($tmp{'shptype1_1lb'} + $tmp{'shptype1_add'}*($weight -1 + 0.9));
		}else{
			$shptotal1 = $tmp{'shptype1_1lb'};
		}

		## Shipping type 2
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv2'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal2 = int($tmp{'shptype2_1lb'} + $tmp{'shptype2_add'}*($weight-1 + 0.9));
		}else{
			$shptotal2 = $tmp{'shptype2_1lb'};
		}
		($cfg{'express_delivery'} and $cfg{'express_delivery_' . $cses{'pay_type'}}) and ($shptotal2 = $cfg{'express_delivery_' . $cses{'pay_type'}});

		## Shipping type 3
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv3'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal3 = int($tmp{'shptype3_1lb'} + $tmp{'shptype3_add'}*($weight -1 + 0.9));
		}else{
			$shptotal3 = $tmp{'shptype3_1lb'};
		}

		### Shipping Puerto Rico
		($tmp{'shptype1pr_1lb'},$tmp{'shptype2pr_1lb'},$tmp{'shptype3pr_1lb'}) = split(/,/,$cfg{'shppr_factors1'});
		($tmp{'shptype1pr_add'},$tmp{'shptype2pr_add'},$tmp{'shptype3pr_add'}) = split(/,/,$cfg{'shppr_factors2'});	
		($tmp{'shpconv1pr'},$tmp{'shpconv2pr'},$tmp{'shpconv3pr'}) = split(/,/,$cfg{'shp_wvconv'});

		## Shipping type 1
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv1pr'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal1pr = int($tmp{'shptype1pr_1lb'} + $tmp{'shptype1pr_add'}*($weight -1 + 0.9));
		}else{
			$shptotal1pr = $tmp{'shptype1pr_1lb'};
		}

		## Shipping type 2
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv2pr'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal2pr = int($tmp{'shptype2pr_1lb'} + $tmp{'shptype2pr_add'}*($weight-1 + 0.9));
		}else{
			$shptotal2pr = $tmp{'shptype2pr_1lb'};
		}
		($cfg{'express_delivery'} and $cfg{'express_delivery_' . $cses{'pay_type'}}) and ($shptotal2pr = $cfg{'express_delivery_' . $cses{'pay_type'}});

		## Shipping type 3
		$aux = int($sizew*$sizeh*$sizel/$tmp{'shpconv3pr'}+0.9);
		if ($aux > $weight){
			$weight = $aux;
		}
		if ($weight>1){
			$shptotal3pr = int($tmp{'shptype3pr_1lb'} + $tmp{'shptype3pr_add'}*($weight -1 + 0.9));
		}else{
			$shptotal3pr = $tmp{'shptype3pr_1lb'};
		}

	}

	$tmp{'shptype1pr_min'}	+= $edt;
	$tmp{'shptype1pr_max'}	+= $edt;
	$tmp{'shptype2pr_min'}	+= $edt;
	$tmp{'shptype2pr_max'}	+= $edt;	
	$tmp{'shptype3pr_min'}	+= $edt;
	$tmp{'shptype3pr_max'}	+= $edt;



	my ($now) = &get_sql_date();
	#######  Shipping in Dates
	$shp_text1 = " $tmp{'shptype1'} ($tmp{'shptype1_min'}-$tmp{'shptype1_max'} ".&trans_txt('days').")";
	$shp_text2 = " $tmp{'shptype2'} ($tmp{'shptype2_min'}-$tmp{'shptype2_max'} ".&trans_txt('days').")";	
	$shp_text3 = " $tmp{'shptype3'} ($tmp{'shptype3_min'}-$tmp{'shptype3_max'} ".&trans_txt('days').")";	
	##$tmp{'shptype1_min'} = &sqldate_plus($now,$tmp{'shptype1_min'});
	##$tmp{'shptype1_max'} = &sqldate_plus($now,$tmp{'shptype1_max'});
	##$shp_text1 = " $tmp{'shptype1'}<br> ($tmp{'shptype1_min'} - $tmp{'shptype1_max'})";
	##$tmp{'shptype2_min'} = &sqldate_plus($now,$tmp{'shptype2_min'});
	##$tmp{'shptype2_max'} = &sqldate_plus($now,$tmp{'shptype2_max'});
	##$shp_text2 = " $tmp{'shptype2'}<br> ($tmp{'shptype2_min'} - $tmp{'shptype2_max'})";	

	#######  Shipping-PR in Dates
	$shp_textpr1 = " $tmp{'shptype1pr'} ($tmp{'shptype1pr_min'}-$tmp{'shptype1pr_max'} ".&trans_txt('days').")";
	$shp_textpr2 = " $tmp{'shptype2pr'} ($tmp{'shptype2pr_min'}-$tmp{'shptype2pr_max'} ".&trans_txt('days').")";		
	$shp_textpr3 = " $tmp{'shptype3pr'} ($tmp{'shptype3pr_min'}-$tmp{'shptype3pr_max'} ".&trans_txt('days').")";		
	##$tmp{'shptype1pr_min'} = &sqldate_plus($now,$tmp{'shptype1pr_min'});
	##$tmp{'shptype1pr_max'} = &sqldate_plus($now,$tmp{'shptype1pr_max'});
	##$shp_textpr1 = " $tmp{'shptype1pr'}<br> ($tmp{'shptype1pr_min'} - $tmp{'shptype1pr_max'})";
	##$tmp{'shptype2pr_min'} = &sqldate_plus($now,$tmp{'shptype2pr_min'});
	##$tmp{'shptype2pr_max'} = &sqldate_plus($now,$tmp{'shptype2pr_max'});
	##$shp_textpr2 = " $tmp{'shptype2pr'}<br> ($tmp{'shptype2pr_min'} - $tmp{'shptype2pr_max'})";	
	#&cgierr("$shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3");
	return ($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$shp_text1,$shp_text2,$shp_text3,$shp_textpr1,$shp_textpr2,$shp_textpr3);
}

sub check_ord_totals {
# --------------------------------------------------------
	#Acci�n: Creaci�n
	#Comentarios:
	# Created on: unknown
	# Last Modified on: 30/jun/2008
	# Last Modified by: MCC C. Gabriel Varela S.
	# Author: unknown
	# Description :  
	# Parameters : $id_orders: Es el ID de una orden

	# Description30jun2008 :  Se agregan validaciones para comparar en base a los montos de env�os
	# Last Modified on: 09/10/08 13:52:05
	# Last Modified by: MCC C. Gabriel Varela S: Se cambia la funci�n para agregar m�s tipos de errores
	# Last Modified on: 09/19/08 11:29:49
	# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta para mostrar N�mero de productos y servicios
	# Last Modified on: 10/02/08 15:55:01
	# Last Modified by: MCC C. Gabriel Varela S: Se cambian los pagos que s� se cuentan
	# Last Modified on: 10/20/08 17:33:31
	# Last Modified by: MCC C. Gabriel Varela S: Temporalmente se quitan validaciones ErrorTax, ErrorDiscount, ErrorShipping. Importante: Volver a tomar en cuenta lo m�s pronto posible.
	# Last Modified on: 11/19/08 12:41:28
	# Last Modified by: MCC C. Gabriel Varela S: Se corrige para contemplar los totales de products contra payments. Tambi�n se quita el filtrado de productos dependiendo de su status.
	# Last Modified on: 11/20/08 13:28:31
	# Last Modified by: MCC C. Gabriel Varela S: Se valida el status del rengl�n del producto
	# Last Modified on: 06/08/09 10:33:38
	# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para poder validar cuando no hay productos y/o no hay pagos.
	# Last Modified on: 08/10/09 15:28:23
	# Last Modified by: MCC C. Gabriel Varela S: Se hace compatible con �rdenes al mayoreo.
	# Last Modified RB: 09/22/09  17:49:11 -- Se modifica para funcionar para orders/preorders
	# Last Modified AD: 21/08/2013  02:09:11 -- Se agrega parametro "calc_tax_in_services" de configuracion para calcular tax en servicios
	# Last Modified AD: 21/08/2013  02:09:11 -- Se agrega omision de error, para pedido COD sin pago
	# Last Modified RB: 27/06/2017  11:58 -- Se modifica el query para buscar la suma de los productos directamente de sl_orders_products, debido a que devolvia PaymentsError cuando no los habia.

	my ($id_orders) = @_;

	my ($rec,$retcad,$prefix);
	#	my ($sth)=&Do_SQL("SELECT sl_orders.ID_orders, if(abs(OrderNet-Sum(SalePrice))>0.02,1,0) as ErrorProducts,if(OrderTax!=0 and sum( Tax )=0,1,0) AS ErrorTax, if(abs(OrderDisc-sum( Discount ))>0.02,1,0) AS ErrorDiscount, if(abs(OrderShp-sum( Shipping ))>0.02,1,0) AS ErrorShipping, sum(if(ID_products not like '6%',1,0))as NumProds,sum(if(ID_products like '6%',1,0))as NumServ,if(abs(round((Sum(if(ID_products not like '6%',SalePrice,0))-OrderDisc)*(1+OrderTax)+OrderShp+Sum(if(ID_products like '6%',SalePrice,0)),2)-SumPay)>0.02,1,0) as ErrorPayments
	#FROM sl_orders_products
	#INNER JOIN sl_orders ON ( sl_orders.ID_orders = sl_orders_products.ID_orders ) 
	#inner join (select ID_orders,sum(amount)as SumPay from sl_orders_payments where ID_orders=$id_orders and Status not in ('Cancelled','Void','Order Cancelled') group by ID_orders)as tempo on (tempo.ID_orders=sl_orders.ID_orders)
	#where sl_orders.id_orders=$id_orders AND sl_orders_products.Status!='Inactive'
	#GROUP BY sl_orders.ID_orders
	#having ErrorProducts=1 /*or ErrorTax=1 or ErrorDiscount=1 or ErrorShipping=1*/ or ErrorPayments=1");

	$prefix = "Related_" if (&is_adm_order($id_orders));
	my ($sth);
	my $val_errorzone = (!$in{'tracking'})? " or ErrorZone=1":"";
	my $pmt_difference = 0.02;
	my $is_valid = 0;


	####
	#### Regla de +- % de Monto capturado diferente de Producto Vendido
	####
	if($cfg{'porcerror'}){

		my $sth = &Do_SQL("SELECT
							ProdAmount AS ToPay 
							, ROUND(ProdAmount * (1 - $cfg{'porcerror'} / 100),2) AS MinPay 
							, ROUND(ProdAmount * (1 + $cfg{'porcerror'} / 100),2) AS MaxPay
							, PayAmount
							, IF( ABS(PayAmount - ProdAmount) BETWEEN 0 AND 1 OR 
								(PayAmount <= ProdAmount * ( 1 + $cfg{'porcerror'} / 100) 
									AND PayAmount >= ProdAmount * ( 1 - $cfg{'porcerror'} / 100)
								) ,1,0
							)AS Valid 
							FROM 
							(
								SELECT
									ID_orders, 
									SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS ProdAmount
									FROM sl_orders_products 
									WHERE ID_orders = '$id_orders'
									AND Status NOT IN ('Order Cancelled','Inactive')
							)Prod		
							INNER JOIN
							(
								SELECT
									ID_orders, 
									SUM(Amount)AS PayAmount 
								FROM sl_orders_payments 
								WHERE ID_orders = '$id_orders'
								AND Status NOT IN ('Void','Order Cancelled','Cancelled')
							)Paym 
							USING(ID_orders)
							WHERE ID_orders = '$id_orders'; ");
		my( $tprod, $minpay, $maxpay, $tpay, $valid ) = $sth->fetchrow();
		$is_valid = ($valid eq '')? 0 : $valid;

	}


	if ($cfg{'calc_tax_in_services'}){

		# /*if(abs(round((Sum(if(".$prefix."ID_products not like '6%' and not isnull(".$prefix."ID_products),if(not isnull(SalePrice),SalePrice,0),0))-OrderDisc)*(1+OrderTax)+OrderShp+(sum(ShpTax))+Sum(if(".$prefix."ID_products like '6%' and not isnull(".$prefix."ID_products),if(not isnull(SalePrice),SalePrice,0),0)),2)-if(not isnull(SumPay),SumPay,0))>0.02,1,0) as ErrorPayments*/
		$sth=&Do_SQL("SELECT sl_orders.ID_orders AS ID_orders, 
			if(abs(OrderNet-Sum(if(not isnull(SalePrice),SalePrice,0))) > $pmt_difference,1,0) as ErrorProducts,
			if(OrderTax!=0 and SUM( if(not isnull(Tax),Tax+ShpTax,0) )= 0,1,0) AS ErrorTax, 
			if(abs(OrderDisc-SUM( if(not isnull(Discount),Discount,0) )) > $pmt_difference,1,0) AS ErrorDiscount, 
			if(abs(OrderShp-SUM( if(not isnull(Shipping),Shipping,0) )) > $pmt_difference,1,0) AS ErrorShipping, 
			SUM(if(".$prefix."ID_products not like '6%' and not isnull(".$prefix."ID_products),1,0))as NumProds,
			SUM(if(".$prefix."ID_products like '6%' and not isnull(".$prefix."ID_products),1,0))as NumServ,
			IF( $is_valid = 0 AND ABS(ROUND(OrderNet - OrderDisc + (SUM(Tax)) + (SUM(Shipping)) + (SUM(ShpTax)), 2) - if(not isnull(SumPay), SumPay, 0)) > $pmt_difference, 1, 0) as ErrorPayments,
			(SELECT COUNT(*) FROM sl_skus WHERE sl_skus.ID_sku_products=sl_orders_products.ID_products AND Status='Inactive') as ErrorSkuInactive,
			(SELECT IF(COUNT(*)=0,1,0) FROM sl_zipcodes INNER JOIN sl_zones USING(ID_zones) WHERE sl_zipcodes.ID_zones=sl_orders.ID_zones AND sl_zipcodes.ZipCode=sl_orders.shp_zip AND sl_zones.Status='Active' LIMIT 1) as ErrorZone
		FROM sl_orders
		LEFT JOIN sl_orders_products ON ( sl_orders.ID_orders = sl_orders_products.ID_orders ) 
		LEFT JOIN (select ID_orders,SUM(amount)as SumPay 
		           FROM sl_orders_payments 
		           WHERE ID_orders=$id_orders 
		           AND Status not in ('Cancelled','Void','Order Cancelled') 
		           GROUP BY ID_orders)AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
		WHERE sl_orders.ID_orders=$id_orders AND (sl_orders_products.Status not in('Inactive')OR isnull(sl_orders_products.Status))
		GROUP BY sl_orders.ID_orders
		HAVING ErrorProducts=1 /*or ErrorTax=1 or ErrorDiscount=1 or ErrorShipping=1*/ or ErrorPayments=1 /*or ErrorSkuInactive>0*/ $val_errorzone");

		# print "SELECT sl_orders.ID_orders AS ID_orders, 
		# 	if(abs(OrderNet-Sum(if(not isnull(SalePrice),SalePrice,0))) > $pmt_difference,1,0) as ErrorProducts,
		# 	if(OrderTax!=0 and SUM( if(not isnull(Tax),Tax+ShpTax,0) )= 0,1,0) AS ErrorTax, 
		# 	if(abs(OrderDisc-SUM( if(not isnull(Discount),Discount,0) )) > $pmt_difference,1,0) AS ErrorDiscount, 
		# 	if(abs(OrderShp-SUM( if(not isnull(Shipping),Shipping,0) )) > $pmt_difference,1,0) AS ErrorShipping, 
		# 	SUM(if(".$prefix."ID_products not like '6%' and not isnull(".$prefix."ID_products),1,0))as NumProds,
		# 	SUM(if(".$prefix."ID_products like '6%' and not isnull(".$prefix."ID_products),1,0))as NumServ,
		# 	IF( $is_valid = 0 AND ABS(ROUND(OrderNet - OrderDisc + (SUM(Tax)) + (SUM(Shipping)) + (SUM(ShpTax)), 2) - if(not isnull(SumPay), SumPay, 0)) > $pmt_difference, 1, 0) as ErrorPayments,
		# 	(SELECT COUNT(*) FROM sl_skus WHERE sl_skus.ID_sku_products=sl_orders_products.ID_products AND Status='Inactive') as ErrorSkuInactive,
		# 	(SELECT IF(COUNT(*)=0,1,0) FROM sl_zipcodes INNER JOIN sl_zones USING(ID_zones) WHERE sl_zipcodes.ID_zones=sl_orders.ID_zones AND sl_zipcodes.ZipCode=sl_orders.shp_zip AND sl_zones.Status='Active' LIMIT 1) as ErrorZone
		# FROM sl_orders
		# LEFT JOIN sl_orders_products ON ( sl_orders.ID_orders = sl_orders_products.ID_orders ) 
		# LEFT JOIN (select ID_orders,SUM(amount)as SumPay 
		#            FROM sl_orders_payments 
		#            WHERE ID_orders=$id_orders 
		#            AND Status not in ('Cancelled','Void','Order Cancelled') 
		#            GROUP BY ID_orders)AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
		# WHERE sl_orders.ID_orders=$id_orders AND (sl_orders_products.Status not in('Inactive')OR isnull(sl_orders_products.Status))
		# GROUP BY sl_orders.ID_orders
		# HAVING ErrorProducts=1 /*or ErrorTax=1 or ErrorDiscount=1 or ErrorShipping=1*/ or ErrorPayments=1 /*or ErrorSkuInactive>0*/ $val_errorzone"
		
	}else{

		$sth=&Do_SQL("SELECT 
						sl_orders.ID_orders AS ID_orders, 
						IF(abs(OrderNet-Sum(if(not isnull(SalePrice),SalePrice,0))) > $pmt_difference,1,0) as ErrorProducts,
						IF(OrderTax!=0 and SUM( if(not isnull(Tax),Tax+ShpTax,0) ) = 0,1,0) AS ErrorTax, 
						IF(abs(OrderDisc-SUM( if(not isnull(Discount),Discount,0) )) > $pmt_difference,1,0) AS ErrorDiscount, 
						IF(ABS(OrderShp-SUM( if(not isnull(Shipping),Shipping,0) )) > $pmt_difference,1,0) AS ErrorShipping, 
						SUM(IF(".$prefix."ID_products not like '6%' and not isnull(".$prefix."ID_products),1,0))as NumProds,
						SUM(IF(".$prefix."ID_products like '6%' and not isnull(".$prefix."ID_products),1,0))as NumServ,
						IF(
							". $is_valid ." = 0 
							AND
							ABS(
								ROUND(
										SUM(sl_orders_products.SalePrice + sl_orders_products.Shipping + sl_orders_products.Tax + sl_orders_products.ShpTax - sl_orders_products.Discount) 
										#ABS(ROUND(
										#		(SUM( 
										#			IF(".$prefix."ID_products not like '6%' and not isnull(".$prefix."ID_products), IF(NOT ISNULL(SalePrice),SalePrice,0),0))
										#			- OrderDisc ) 
										#			* ( 1 + OrderTax ) 
										#			+ OrderShp + ( SUM( ShpTax ) 
										#		) 
										#			
										#		+ SUM(
										#			IF(".$prefix."ID_products like '6%' AND NOT ISNULL(".$prefix."ID_products), IF(not isnull(SalePrice),SalePrice,0),0)),2)
										- IF(NOT ISNULL(SumPay),SumPay,0)
									)
								) > ". $pmt_difference .", 1, 0
							) as ErrorPayments,
						(SELECT COUNT(*) FROM sl_skus WHERE sl_skus.ID_sku_products=sl_orders_products.ID_products AND Status='Inactive') as ErrorSkuInactive,
						(SELECT IF(COUNT(*) = 0,1,0) FROM sl_zipcodes INNER JOIN sl_zones USING(ID_zones) WHERE sl_zipcodes.ID_zones=sl_orders.ID_zones AND sl_zipcodes.ZipCode=sl_orders.shp_zip AND sl_zones.Status='Active' LIMIT 1) as ErrorZone
					FROM sl_orders
					LEFT JOIN sl_orders_products ON ( sl_orders.ID_orders = sl_orders_products.ID_orders ) 
					LEFT JOIN (SELECT ID_orders,SUM(amount)as SumPay 
					           FROM sl_orders_payments 
					           WHERE ID_orders = ". $id_orders ."
					           AND Status not in ('Cancelled','Void','Order Cancelled') 
					           GROUP BY ID_orders)AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
					WHERE sl_orders.ID_orders = ". $id_orders ." AND (sl_orders_products.Status not in('Inactive')OR isnull(sl_orders_products.Status))
					GROUP BY sl_orders.ID_orders
					HAVING ErrorProducts=1 /*or ErrorTax=1 or ErrorDiscount=1 or ErrorShipping=1*/ or ErrorPayments=1 /*or ErrorSkuInactive>0*/ $val_errorzone");	
	}

	$rec=$sth->fetchrow_hashref;
	if (!$rec->{'ID_orders'}){

		$retcad="OK";

	}else{

		my $ptype = &load_db_names('sl_orders','ID_orders',$id_orders,"Ptype");

		$retcad.=" <li>Products Error </li>" if ($rec->{'ErrorProducts'});
		$retcad.=" <li>Tax Error </li>" if ($rec->{'ErrorTax'});
		$retcad.=" <li>Discount Error </li>" if ($rec->{'ErrorDiscount'});
		$retcad.=" <li>Shipping Error </li>" if ($rec->{'ErrorShipping'});
		$retcad.=" <li>Payments Error </li>" if ($rec->{'ErrorPayments'} and $ptype ne 'COD');
		$retcad.=" <li>Inactive SKUs Error </li>" if ($rec->{'ErrorSkuInactive'});
		$retcad.=" <li>Zone Error </li>" if ($rec->{'ErrorZone'} and $cfg{'zones_validation'} == 1);

		#$retcad.=" <li>Products Number: $rec->{'NumProds'}</li>";
		#$retcad.=" <li>Services Number: $rec->{'NumServ'}</li>";
		# Response OK for COD
		$retcad="OK" if $retcad eq "";
	}


	return $retcad;

}

sub check_ord_status {
# --------------------------------------------------------
	my ($id_orders,$statusprd,$statuspay,$status) = @_;
	my ($count);
	if ($status ne 'Shipped'){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE (ShpDate<>'0000-00-00' OR ShpDate IS NULL) AND ID_orders=$id_orders and Status='Active'");
		if ($sth->fetchrow()>0){
			return "Shipped Item Not Shipped Status";
		}
		## contar Item en Orden
		## Comparar con Items Shipped
		## Sino es Igual : StatusProd debe ser  Partial Shipment', 'Partial Dropship
	}
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE (CapDate<>'0000-00-00' AND CapDate IS NOT NULL) AND ID_orders=$id_orders and Status<>'Cancelled'");
	$count = $sth->fetchrow();
	if ($count == 0 and $status eq 'Shipped'){
		return "Shipped Nothing Captured";
	}elsif ($count>0 and $status ne 'Shipped'){
		return "Captured but Not Shipped";
	}	
	if ($status eq 'Shipped' and ($statuspay =~ /^Review Order|^Review Address|^Payment Declined|^Insufficient Funds|^Post-Dated/)){
		return "Wrong Payment Exception";
	}

	if ($status eq 'Cancelled' and $statuspay !~ /^None|^ChargeBack|^For Refund/){
		return "Wrong Payment Exception";
	}
	if ($status eq 'Shipped' and ($statusprd =~ /^Out of Stock|^In Fulfillment|^In Dropshipment|^Dropship Sent/)){
		return "Wrong Product Exception";
	}	
	return "OK";
}


#################################################################################################
#################################################################################################
#
#	Function: check_rman
#
#   		Main Function. Creates a txt file with journal entries to be posted in Accounting SW
#
#	Created by:_RB_
#
#	Modified By:
#
#
# 		Last Modified RB: 12/15/08  16:01:39 -- Added check authorization date. If a payment has an authorization older than 45 days and is not capture, the operator should ask for an administration code to procced with capture
# 		Last Modified RB: 01/07/09  15:56:01 -- Modified aut->capture window from 45 to 30 days
# 		Last Modified RB: 05/21/09  17:13:06 -- Se incorpora chequeo de posible duplicidad en ordenes y se revisa si existe un check avs previo exitoso
# 		Last Modified on: 06/05/09 12:48:15
# 		Last Modified by: MCC C. Gabriel Varela S: Se corrige verificaci�n de AVS
# 		Last Modified RB: 07/07/09  19:02:11 -- Se inactiva el registro de la informacion en archivo
# 		Last Modified RB: 07/30/09  14:09:29 -- Se modifico el check avs para aceptar varias respuestas como validas
# 		Last Modified by RB on 06/21/2011 11:31:32 AM : En la busqueda del PmtField3 se agrega que el Status del pago no sea Cancelado.
#		Last Modified RB: 08/06/2014 -- Se agrega riesgo por cantidad de ordenes risk_quantity
#
#
#   	Parameters:
#
#
#   	Returns:
#
#		Creates a xls file
#
#   	See Also:
#
#	
#			##############################
#			##############################
#
#
#			ATENCION!!!! Esta funcion sera copiada al cron, revisar <fn_low> y actualizar en ambos lados
#
#
sub check_rman {
#################################################################################################
#################################################################################################



	my ($id_orders) = @_;
	my ($output, $status,$str_qty_where);
	$output = '';
	my $risk_type = 'Credit-Card';
	my $id_customers = $in{'id_customers'} ? $in{'id_customers'} : &load_name('sl_orders', 'ID_orders', $id_orders, 'ID_customers' );

	#######
	####### RiskMan Disabled?
	#######	
	return ('OK') if ($cfg{'risk_management'} eq 'disable');


	my ($sth) = &Do_SQL("SELECT PType, Status FROM sl_orders WHERE ID_orders = '". $id_orders ."';");
	my ($ptype, $order_status) = $sth->fetchrow();

	#######
	####### RiskMan COD | Shipped?
	#######
	return ('OK') if ($ptype and $ptype ne $risk_type);
	return ('OK') if ($order_status and $order_status !~ /New|Pending|Processed/);

	#######
	####### RiskMan Match Fraudulent Data
	#######
	($status, $output) = &check_fraudulent($id_orders, $id_customers);
	if( $status eq 'ERROR' ){
		return ( $output );
	}


	#######
	####### Risk Note?
	#######
	my ($sth) = &Do_SQL("SELECT Notes FROM sl_orders_notes WHERE ID_orders = '". $id_orders ."' AND Notes LIKE '%Risk Order%' ORDER BY ID_orders_notes DESC LIMIT 1;");
	my ($risk_order_note) = $sth->fetchrow();
	return $risk_order_note if $risk_order_note;


	### Check Authorization Code
	$va{'authrisk_'.$id_orders} =  '';
	my ($sth)= &Do_SQL("SELECT ID_orders_payments,DATEDIFF(CURDATE(),AuthDateTime) AS Period FROM sl_orders_payments WHERE ID_orders=$id_orders AND Type='Credit-Card' AND PmtField3>0 AND AuthDateTime IS NOT NULL AND (Captured  = 'No') AND (CapDate ='0000-00-00')");
	while(my ($idop,$period) = $sth->fetchrow()){
		if ($period > 30 and (!$va{'authok_'.$id_orders} or $va{'authok_'.$id_orders} !~ /^$idop$/)){
			$output .= "\nAuthorization Payments Not Captured older than 30 days ";
			$status = 'ERROR';
			$va{'authrisk_'.$id_orders} .= "$idop|"; 
		}
	}

	### Check Duplicate Order
	#### Prevent Duplicate Order
	my ($sth) = &Do_SQL("SELECT IF( TRIM( SUBSTR(DATA , LOCATE( 'ID Order :',DATA ) +11, 6 ) ) >0, TRIM( SUBSTR(DATA , LOCATE( 'ID Order :',DATA ) +11, 6 ) ) , IF( TRIM( SUBSTR(DATA , LOCATE( 'ID Preorder :',DATA ) +14, 6 ) ) >0, TRIM( SUBSTR(DATA , LOCATE( 'ID Preorder :',DATA ) +14, 6 ) ) , 0 ) ) FROM sl_orders_plogs WHERE ID_orders = $id_orders AND (LOCATE( 'ID Order :',Data) > 0 OR LOCATE( 'ID Preorder :',DATA ) > 0) LIMIT 1 ;");
	my ($id_orders_previous) = int($sth->fetchrow());
	if ($id_orders_previous > 500000 ){
		my ($sth) =  &Do_SQL("SELECT IF(GROUP_CONCAT(DISTINCT(sl_orders.ID_orders)) IS NOT NULL,GROUP_CONCAT(DISTINCT(sl_orders.ID_orders)),0) FROM sl_orders_plogs INNER JOIN sl_orders ON sl_orders_plogs.ID_orders = sl_orders.ID_orders WHERE sl_orders_plogs.ID_admin_users = 1 AND sl_orders.ID_orders != $id_orders AND (`Data` LIKE '%ID Order : $id_orders_previous  ID Payments%' OR `Data` LIKE '%ID Preorder : $id_orders_previous  ID Payments%') AND sl_orders.Status NOT  IN ( 'System Error', 'Cancelled', 'Void');"); 
		my $id_duplicates = $sth->fetchrow();

		if ($id_duplicates > 0){
			$output .= "\nRisk : Duplicate Orders $id_duplicates";
			$status = 'ERROR';

			if ($in{'status'} ne 'Shipped') {

				&Do_SQL("UPDATE sl_orders SET Status='Pending' WHERE ID_orders='$id_orders';");
				&auth_logging('opr_orders_stPending',$id_orders);
				&status_logging($id_orders,'Pending');

			}	

		}
	}

	
#	if ((stat("$cfg{'auth_dir'}/.orders/$id_orders"))[9] + 300 < time) {
#		unlink ("$cfg{'auth_dir'}/.orders/$id_orders");
#	}
#	if (open(AUTH, "+<$cfg{'auth_dir'}/.orders/$id_orders")){
#		($status,$va{'authrisk_'.$id_orders},$output)= split(/~~/,join("",<AUTH>),3);
#		print AUTH " ";
#		close AUTH;
#	}else{
	
	
	##############
	############## Orders Data + Customer Phone's
	##############
	my ($sth)= &Do_SQL("SELECT sl_orders.*,Phone1,Phone2,Cellphone FROM sl_orders LEFT JOIN sl_customers USING(ID_customers) WHERE ID_orders = $id_orders;");
	my ($rec) = $sth->fetchrow_hashref();


	## Check Order
	if ($rec->{'OrderNet'} > $cfg{'risk_maxorder'}){

		$output .= "Risk : Order Amount ".&format_price($rec->{'OrderNet'})." >  $cfg{'risk_maxorder'}   ";
		$status = 'ERROR';

	}



	## Credit Limit CHECK WITH CUSTOMER ID
	##my ($sth)= &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders!=$id_orders AND (AuthCode='' OR AuthCode IS NULL OR AuthCode='0000')");
	##my ($total) =  $sth->fetchrow();
	##if ($total > 1000){
	##	$output .= "Risk : Credit Limit ".&format_price($total)."    ";
	##	$status = 'ERROR';
	##}

	## Payment Denied CHECK WITH CUSTOMER ID
	##my ($sth)= &Do_SQL("SELECT COUNT(Amount) FROM sl_orders_payments WHERE ID_orders != $id_orders AND Status='Denied' AND (AuthCode='' OR ISNULL(AuthCode) OR AuthCode='0000')");
	##my ($total) =  $sth->fetchrow();
	##if ($total > 0){
	##	$output .= " Risk : Payment Denied $total    ";
	##	$status = 'ERROR';
	##}

	## Checking Addresss
	if ($rec->{'OrderNet'}>=$cfg{'risk_billshp'} and ($rec->{'Address1'} ne $rec->{'shp_Address1'} or $rec->{'Zip'} ne $rec->{'shp_Zip'})){
		$output .= "Risk : Shipping Addres <> Billing Address and Order>\$$cfg{'risk_billshp'} ";
		$status = 'ERROR';
	}


	## Check Order / Address
	push(@ary_qty_index, 'Zip'); push(@ary_qty_index, 'shp_Zip');
	$str_qty_where .= " ((sl_orders.Address1='". &filter_values($rec->{'Address1'}) ."' AND sl_orders.Zip = '$rec->{'Zip'}') OR (shp_Address1='".&filter_values($rec->{'shp_Address1'})."' AND shp_Zip='$rec->{'shp_Zip'}'))";
	my $sub_address = "SELECT 
						ID_orders 
					FROM 
						sl_orders 
					WHERE 
						(sl_orders.Address1 = '". &filter_values($rec->{'Address1'}) ."' AND sl_orders.Zip = '". $rec->{'Zip'} ."') 
						OR (shp_Address1 = '".&filter_values($rec->{'shp_Address1'})."' AND shp_Zip = '". $rec->{'shp_Zip'} ."') ";

	my ($sth) = &Do_SQL("SELECT SUM(OrderNet) FROM sl_orders USE INDEX ( Zip, shp_Zip ) WHERE $str_qty_where AND ID_orders <> $rec->{'ID_orders'};");
	my ($total) =  $sth->fetchrow();
	if ($total > $cfg{'risk_creditlimit'}){
		$output .= "Risk Sales with Same Address : ".&format_price($total)."    ";
		$status = 'ERROR';
	}

	## Check Order / Phone
	my @aryp;
	my @phones;
	my $sub_customer;

	($rec->{'Phone1'}) 	and ( push(@phones,  qq|'|. &filter_values($rec->{'Phone1'}) .qq|'|) );
	($rec->{'Phone2'}) 	and ( push(@phones,  qq|'|. &filter_values($rec->{'Phone2'}) .qq|'|) );
	($rec->{'CellPhone'}) 	and ( push(@phones,  qq|'|. &filter_values($rec->{'CellPhone'}).qq|'|) );

	if( @phones > 0 ){	
		$sub_customer =  qq|SELECT 
								ID_orders 
							FROM 
								sl_customers INNER JOIN sl_orders USING(ID_customers) 
							WHERE 
								Phone1 IN (|. join(',', @phones).qq|) 
								OR Phone2 IN (|. join(',', @phones).qq|) 
								OR CellPhone IN (|. join(',', @phones).qq|)
							UNION|;
	}

	if(scalar @aryp) {

		push(@ary_qty_index, 'ID_customers');
		$str_qty_where .= " OR (". join(' OR ', @aryp) .") ";
		my ($sth) = &Do_SQL("SELECT SUM(OrderNet) FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders <> $rec->{'ID_orders'}  AND (". join(' OR ', @aryp) .")");
		my ($total) =  $sth->fetchrow();
		if ($total > $cfg{'risk_creditlimit'}){
			$output .= "Risk Sales with Same Phone : ".&format_price($total)."    ";
			$status = 'ERROR';
		}
	}

	## Check Order / Address and Cancelled Orders
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders USE INDEX(Zip,shp_Zip) WHERE ((Address1='".&filter_values($rec->{'Address1'})."' AND Zip='$rec->{'Zip'}') OR (shp_Address1='".&filter_values($rec->{'shp_Address1'})."' AND shp_Zip='$rec->{'shp_Zip'}')) AND ID_orders<>$rec->{'ID_orders'} AND Status='Cancelled'");
	my ($total) =  $sth->fetchrow();
	if ($total>$cfg{'risk_canceled'}){
		$output .= "Risk : Too Many Cancelled Orders (Same Address): $total    ";
		$status = 'ERROR';
	}

	### Check Credit Card
	my ($ccnum, $pmtfield3);
	if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){
		my ($sth)= &Do_SQL("SELECT sl_orders_cardsdata.card_number, sl_orders_payments.PmtField3 
							FROM sl_orders_payments 
								INNER JOIN sl_orders_cardsdata USING(ID_orders_payments)
							WHERE sl_orders_payments.ID_orders='$id_orders' AND sl_orders_payments.Type='Credit-Card' AND sl_orders_payments.PmtField3>0 AND sl_orders_payments.`Status` NOT IN('Order Cancelled','Cancelled');");
		($ccnum, $pmtfield3) = $sth->fetchrow();		
	}else{
		my ($sth)= &Do_SQL("SELECT PmtField3 FROM sl_orders_payments WHERE ID_orders=$id_orders AND Type='Credit-Card' AND PmtField3>0 AND Status NOT IN('Order Cancelled','Cancelled');");
		$ccnum = $sth->fetchrow();
	}


	my $sub_cardsdata;
	if ($ccnum ne ''){

		my ($total);
		### Credit Card Risk
		if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){

			my ($sth)= &Do_SQL("SELECT SUM(Amount) 
								FROM sl_orders_payments 
									INNER JOIN sl_orders_cardsdata USING(ID_orders_payments)
								WHERE sl_orders_payments.ID_orders = '". $id_orders ."' AND sl_orders_cardsdata.card_number = '". $ccnum ."' AND sl_orders_payments.`Status` IN ('Approved', 'Denied', 'Pending', 'Insufficient Funds')");
			$total =  $sth->fetchrow();
			$sub_cardsdata = "SELECT sl_orders_payments.ID_orders FROM sl_orders_cardsdata INNER JOIN sl_orders_payments USING(ID_orders_payments) WHERE sl_orders_cardsdata.card_number = '$ccnum' UNION ";

		}else{

			my ($sth)= &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '". $id_orders ."' AND PmtField3 = '". $ccnum ."' AND Status IN ('Approved', 'Denied', 'Pending', 'Insufficient Funds')");
			$total =  $sth->fetchrow();
			$sub_cardsdata = "SELECT sl_orders_payments.ID_orders FROM sl_orders_payments WHERE PmtField3 = '$ccnum'";

		}

		if ($total>$cfg{'risk_maxorder'}){

			$output .= "Risk with Credit Card XXXX-XXXX-XXXX-".substr($pmtfield3,-4)." : ".&format_price($total)."    ";
			$status = 'ERROR';

		}

		### Credit Card Risk / Cancelled
		if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){

			my ($sth)= &Do_SQL("SELECT COUNT(Amount) 
								FROM sl_orders_payments 
									INNER JOIN sl_orders USING(ID_orders)
									INNER JOIN sl_orders_cardsdata USING(ID_orders_payments)
								WHERE sl_orders.ID_orders<>$id_orders AND sl_orders_cardsdata.card_number='$ccnum' AND sl_orders.`Status`='Cancelled';");
			$total =  $sth->fetchrow();

		}else{

			my ($sth)= &Do_SQL("SELECT COUNT(Amount) FROM sl_orders_payments INNER JOIN sl_orders USING(ID_orders) WHERE sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.ID_orders<>$id_orders AND PmtField3='$ccnum' AND sl_orders.Status='Cancelled';");
			$total =  $sth->fetchrow();

		}

		if ($total>$cfg{'risk_canceled'}){

			$output .= "Risk : Too Many Cancelled Orders (Same CC XXXX-XXXX-XXXX-".substr($pmtfield3,-4).") : $total    ";
			$status = 'ERROR';

		}

		## Credit Limit CHECK WITH CUSTOMER ID
		if( $cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1 ){

			my ($sth)= &Do_SQL("SELECT SUM(Amount) 
								FROM sl_orders_payments 
									INNER JOIN sl_orders_cardsdata USING(ID_orders_payments)
								WHERE sl_orders_cardsdata.card_number='$ccnum' AND sl_orders_payments.Status NOT IN('Cancelled','Void','Order Cancelled') AND LENGTH(Authcode) > 3 AND Authcode <> '0000' /*AND sl_orders_payments.ID_orders!=$id_orders AND (AuthCode='' OR AuthCode IS NULL OR AuthCode='0000')*/;");
			$total =  $sth->fetchrow();

		}else{

			my ($sth)= &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE  PmtField3='$ccnum' AND sl_orders_payments.Status NOT IN('Cancelled','Void','Order Cancelled') AND LENGTH(Authcode) > 3 AND Authcode <> '0000' /*AND ID_orders!=$id_orders AND (AuthCode='' OR AuthCode IS NULL OR AuthCode='0000')*/;");
			$total =  $sth->fetchrow();

		}

		if ($total > $cfg{'risk_creditlimit'}){

			$output .= "Risk : Credit Limit ".&format_price($total)."    ";
			$status = 'ERROR';

		}

		## Check AVS
		###a|b|D|h|k|l|o|t|w|x|Y|Z  = Approved
		$sth=&Do_SQL("SELECT ID_orders,
					    /* count(ID_orders_plogs)as PLogs,
					     sum(if(Data like '%cAuthReply_avsCode = Y%',1,0))as Y,
					     sum(if(Data like '%cAuthReply_avsCode%' and Data not like '%cAuthReply_avsCode = Y%',1,0))as NotY,*/
					     sum(if(Data REGEXP  'ccAuthReply_avsCode = [a|b|D|h|k|l|o|t|w|x|Y|Z]',1,0))as AVSY
					    /* sum(if(Data like '%AVS VERIFICATION%cAuthReply_avsCode%' and Data not like '%AVS VERIFICATION%cAuthReply_avsCode = Y%',1,0))as AVSNotY*/
					FROM sl_orders_plogs 
					WHERE ID_orders=$id_orders
					group by ID_orders;");
		$rec=$sth->fetchrow_hashref;
		# Si hay checkav OK?
		if ($rec->{'AVSY'}>0){
			# saltar
		}else{
			# Verficar avs NO en checkavs_paylogs.. Ultimo Paylog
			$sth=&Do_SQL("Select Data from sl_orders_plogs where ID_orders=$id_orders and Data like '%cAuthReply_avsCode%' order by ID_orders_plogs desc limit 1;");
			$rec=$sth->fetchrow_hashref;
			if ($rec->{'Data'}=~/cAuthReply_avsCode = [^Y]/){
				$output .= " AVS not match    ";
				if ($total >=$cfg{'risk_avslimit'}){
					$status = 'ERROR';
				}
			}
		}
	}


	if($cfg{'risk_quantity'} > 0){

		## Check Quantity with Adress/Phone/CCard
		$sub_address .= $id_customers ? " OR ID_customers = '". $id_customers ."' " : '';
		my $query = "SELECT 
						COUNT(DISTINCT ID_orders) 
					FROM 
					( 
						$sub_cardsdata 
						$sub_customer 
						$sub_address
					)tmp;";
		my ($sth)= &Do_SQL($query);

		my ($sum_qty) = $sth->fetchrow();
		if($sum_qty >= $cfg{'risk_quantity'}){

			$output .= "Risk : Limit order quantity: $sum_qty > " . $cfg{'risk_quantity'};
			$status = 'ERROR'; 
		}

	}

	if ($status eq 'ERROR'){
		return ($output);
	}else{
		return ('OK');
	}

}


sub check_fraudulent {
# --------------------------------------------------------
# Created on: 09/26/2017 @ 19:54
# Author: Huitzilihuitl Ceja
# Description : Verifica si el usuario se encuentra en tabla de Fraudulentos
# Parameters : ID Orders & ID Customers
#			   	

	my ($id_orders, $id_customers) = @_;


	### Check Fraudulent Customer DataBase
	if( $cfg{'risk_fraudulent_db'} > 0 )
	{
		my @reject = ('el','la','los','las', 'no', '#', 'y');

		my $query = "SELECT
						LOWER(FirstName), 
						LOWER(LastName1), 
						LOWER(LastName2), 
						LOWER(Phone1), 
						LOWER(Phone2), 
						LOWER(Cellphone), 
						LOWER(Email), 
						LOWER(Address1), 
						LOWER(Address2), 
						LOWER(Address3), 
						LOWER(Urbanization), 
						LOWER(City), 
						LOWER(State), 
						LOWER(Zip), 
						LOWER(Country)
					FROM sl_customers WHERE ID_customers = $id_customers;";

		my ($sth)= &Do_SQL($query);
		my ($firstname, $lastname1, $lastname2, $phone1, $phone2, $cellphone, $email, $address1, 
			$address2, $address3, $urbanization, $city, $state, $zip, $country) = $sth->fetchrow_array();


		my $matches, $set, $select, $tolerance = '0.75';
		my %having;


		#---------- $address1
		foreach my $string ( @reject )
		{
			$address1 =~ s/$string//g;		
		}
		$address1 =~ s/\s+/ /g;

		my @address = split ' ', $address1;
		my $qty = scalar(@address);


		for( my $i=1; $i<=4; $i++ )
		{
			foreach my $part (@address)
			{
				$matches .= "\nIF( INSTR( LOWER(Street$i), ' $part ' ) > 0, 1, 0)+";
			}

			chop($matches);
			$matches = "\n((".$matches.")/$qty) street_a$i,";
			$having{"street_a"} .= " street_a$i >= $tolerance or ";

			$set .= $matches;
			$matches = '';
		}

		$select = $set;
		$having{"street_a"} = "(".substr($having{"street_a"}, 0, -4).")";


		#---------- $address2
		$having{"street_b"} = " FALSE ";
		if( $address2 ne '')
		{
			$having{"street_b"} = "";

			foreach my $string ( @reject )
			{
				$address2 =~ s/$string//g;		
			}
			$address2 =~ s/\s+/ /g;

			my @address = split ' ', $address2;
			$qty = scalar(@address);
			$matches = '', $set  = '';

			for( my $i=1; $i<=5; $i++ )
			{
				foreach my $part (@address)
				{
					$matches .= "\nIF( INSTR( LOWER(Street$i), ' $part ' ) > 0, 1, 0)+";
				}

				chop($matches);
				$matches = "\n((".$matches.")/$qty) street_b$i,";
				$having{"street_b"} .= " street_b$i >= $tolerance or ";

				$set .= $matches;
				$matches = '';

			}
			$select .= $set;
			$having{"street_b"} = "(".substr($having{"street_b"}, 0, -4).")";
		}


		#---------- $address3
		$having{"reference"} = " FALSE ";
		if( $address3 ne '')
		{
			$having{"reference"} = "";
			foreach my $string ( @reject )
			{
				$address3 =~ s/$string//g;		
			}
			$address3 =~ s/\s+/ /g;

			my @address = split ' ', $address3;
			$qty = scalar(@address);
			$matches = '', $set  = '';

			for( my $i=1; $i<=3; $i++ )
			{
				foreach my $part (@address)
				{
					$matches .= "\nIF( INSTR( LOWER(Reference$i), ' $part ' ) > 0, 1, 0)+";
				}

				chop($matches);
				$matches = "\n((".$matches.")/$qty) reference$i,";
				$having{"reference"} .= " reference$i >= $tolerance or ";

				$set .= $matches;
				$matches = '';
			}

			$select .= $set;		
			$having{"reference"} = "(".substr($having{"reference"}, 0, -4).")";
		}



		#---------- $Name

		my @name = ($firstname, $lastname1, $lastname2);
		$qty = scalar( @name );
		$matches = '', $set  = '';

		for( my $i=1; $i<=6; $i++ )
		{
			foreach my $part (@name)
			{
				$matches .= "\nIF( INSTR( LOWER(Name$i), ' $part ' ) > 0, 1, 0)+";
			}

			chop($matches);
			$matches = "\n((".$matches.")/$qty) name$i,";
			$having{"name"} .= " name$i >= $tolerance or ";

			$set .= $matches;
			$matches = '';

		}
		
		$select .= $set;
		$having{"name"} = "(".substr($having{"name"}, 0, -4).")";



		#--------- $zip
		for( my $i=1; $i<=4; $i++ )
		{
			$matches .= "IF('$zip' = Zip$i , 1, 0)+";
		}
		chop($matches);
		$select .= " ($matches) zip, ";
		$having{"zip"} = "( zip >= 1 )";

		#--------- $city
		$select .= "\n(IF('$city' = LOWER(Urbanization1) , 1, 0)+";
		$select .=    "IF('$city' = LOWER(Urbanization2) , 1, 0)) city,";
		$having{"city"} = "( city >= 1 )";


		#--------- $phone1
		$having{"phone1"} = " FALSE ";
		if( $phone1 ne '')
		{
			$having{"phone1"} = "";
			$matches = '', $set  = '';
			for( my $i=1; $i<=8; $i++ )
			{
				$matches .= "\nIF('$phone1' = Phone$i , 1, 0)+";
			}
			chop($matches);
			$select .= "\n($matches) phone1,";
			$having{"phone1"} = "( phone1 >= 1 )";
		}


		#--------- $phone2
		$having{"phone2"} = " FALSE ";
		if( $phone2 ne '')
		{
			$having{"phone2"} = "";
			$matches = '', $set  = '';
			for( my $i=1; $i<=8; $i++ )
			{
				$matches .= "\nIF('$phone2' = Phone$i , 1, 0)+";
			}
			chop($matches);
			$select .= "\n($matches) phone2,";
			$having{"phone2"} = "( phone2 >= 1 )";

		}

		#--------- $phone3
		$having{"cellphone"} = " FALSE ";
		if( $cellphone ne '')
		{
			$having{"cellphone"} = "";
			$matches = '', $set  = '';
			for( my $i=1; $i<=8; $i++ )
			{
				$matches .= "\nIF('$cellphone' = Phone$i , 1, 0)+";
			}
			chop($matches);
			$select .= "\n($matches) cellphone,";
			$having{"cellphone"} = "( cellphone >= 1 )";
		}

		#--------- $email
		$having{"email"} = " FALSE ";
		if( $email ne '')
		{
			$having{"email"} = '';
			$matches = '', $set  = '';
			for( my $i=1; $i<=6; $i++ )
			{
				$matches .= "\nIF('$email' = Email$i , 1, 0)+";
			}
			chop($matches);
			$select .= "\n($matches) email,";
			$having{"email"} = "( email >= 1 )";
		}

		chop($select);
		$having = substr $having, 0, -4;

		$query = "SELECT ID_banned_customers, \n".$select."\nFROM cu_banned_customers\n HAVING \n".
		$having{"phone1"}." OR ".$having{"phone2"}." OR ".$having{"cellphone"}." OR ".$having{"email"}.
		"\n OR (\n". 
		"(".$having{"street_a"} ."\n OR ". $having{"street_b"} ."\n OR ". $having{"reference"} ."\n OR ". $having{"city"} ."\n OR ". $having{"zip"} ."\n)\n".
		" AND ". $having{"name"} ."\n)\n".
		"LIMIT 1;";

		my ($sth)= &Do_SQL($query);
		my ($banned_registry) = $sth->fetchrow_hashref();

	    if($sth->rows() > 0){
			my @response = ("ERROR","The data matches a FRAUDULENT customer registry.");
			return @response;
		}else{
			my @response = ("OK","");
			return @response;
		}
	}	
}

sub check_returns {
# --------------------------------------------------------
# Created on: 08/27/08 @ 15:39:40
# Author: Carlos Haas
# Last Modified on: 08/27/08 @ 15:39:40
# Last Modified by: Carlos Haas
# Description : 
# Parameters : falta diferenciar entre returns resolved y no
#			   
	my ($id) = @_;
	my ($sth)= &Do_SQL("SELECT COUNT(*) FROM sl_orders_products,sl_returns WHERE sl_orders_products.ID_orders=$id AND sl_orders_products.ID_orders_products=sl_returns.ID_orders_products");
	if ($sth->fetchrow() >0){
		return "Has Returns";
	}else{
		return "OK";
	}
}


sub update_flexipago {
# --------------------------------------------------------
## Esta rutina actualiza las fechas. Debe ser modificada
## con MUCHA precaucion y avisar a Carlos Haas
## de cualquier cambio
# Last Modification by JRG : 03/13/2009 : Se agrega log
# Last Modification by RB on 04/26/2010 : Por orden de Carlos Haas, se hace el update de los pagos en rangos de 30 dias
# Last Time Modified By RB on 02/08/2011 : Si existen pagos capturados y ya contienen un Capdate y Paymentdate, entonces el Paymentdate no se actualiza

	my ($id_orders,$date,$offset) = @_;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders=$id_orders AND Status IN ('Approved','Denied','Pending')");
	if ($sth->fetchrow() eq 1 and !$in{'postdated'} and !$cses{'postdated'}){
		return;
	}else{
		#return;
		my ($payments);
		my ($sth) = &Do_SQL("SELECT *,IF(Capdate > '2005-01-01' AND Paymentdate > '2005-01-01','Yes',IF(Capdate > '2005-01-01' AND Paymentdate < '2005-01-01','Update','No'))AS Skip FROM sl_orders_payments WHERE ID_orders=$id_orders AND Status IN ('Approved','Denied','Pending') ORDER BY Capdate DESC,ID_orders_payments DESC,Paymentdate");	
		PAYMENTS:while ($rec = $sth->fetchrow_hashref()){
			++$payments;

			next PAYMENTS if $rec->{'Skip'} eq 'Yes';

			if ($payments eq 1){

				if ($rec->{'Skip'} eq 'Update'){
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate=CapDate WHERE ID_orders_payments=$rec->{'ID_orders_payments'}");
				}else{
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate='$date' WHERE ID_orders_payments=$rec->{'ID_orders_payments'}");					
				}

			}else{

				if ($rec->{'Skip'} eq 'Update'){
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate=CapDate WHERE ID_orders_payments=$rec->{'ID_orders_payments'}"); 
				}else{
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate=ADDDATE('$date',".(30*($payments-1)).") WHERE ID_orders_payments=$rec->{'ID_orders_payments'}");
				}

			}
#			}elsif($id_orders <= 35250 or ($id_orders>=54177 and $id_orders<56592 or $offset == 30)){
#				## Flexipagos de 30 Dias
#				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate=ADDDATE('$date',".(30*($payments-1)).") WHERE ID_orders_payments=$rec->{'ID_orders_payments'}");
#				&auth_logging('orders_payments_updated',$id_orders);
#			}elsif(($id_orders>3250 and $id_orders<54177) or () or $offset == 15){	 
#				## Flexipagos de 15 Dias
#				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Paymentdate=ADDDATE('$date',".(15*($payments-1)).") WHERE ID_orders_payments=$rec->{'ID_orders_payments'}");					
#				&auth_logging('orders_payments_updated',$id_orders);
#			}
		}
		&auth_logging('orders_payments_updated',$id_orders);
	}
}

sub build_tracking_link {
# --------------------------------------------------------

# Author: Unknown
# Created on:  Unknown
# Description : More info was added to show stock, po and po notes
# Forms Involved: 
# Parameters :
# Last Modified RB: 10/14/08  16:21:15 void if call comes from returns 
# Last Modified RB: 10/27/08  15:38:36 Added Fedex Link
# Last Modified RB: 01/07/09  12:04:08 remove "<td>" in $link
# Last Modified on: 07/09/09 11:00:00
# Last Modified by: MCC C. Gabriel Varela S: Se agrega compatibilidad con IW

	my ($Tracking,$ShpProvider,$ShpDate,$id_products)=@_;
	my ($output,$link);
	if (!$in{'toprint'}){
		
		## Tracking Mexico
		if ($cfg{'use_shipping_tracking_mx'} and $cfg{'use_shipping_tracking_mx'}==1){
			if (!$Tracking or !$ShpProvider or $ShpDate eq '0000-00-00'){
				$link = '';
			}elsif ($ShpProvider eq 'ESTAFETA'){
				$link = qq|<a href="http://rastreo3.estafeta.com/RastreoWebInternet/consultaEnvio.do?&method=&forward=&idioma=es&pickUpId=&dispatch=doRastreoInternet&tipoGuia=ESTAFETA&guias=$Tracking" target="_blank" title="Go to ESTAFETA">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'UPS'){
				$link = qq|<a href="http://wwwapps.ups.com/WebTracking/track?loc=en_MX&tbifl=1&tracknum=$Tracking&track.x=Track&trackSelectedOption=" target="_blank" title="Go to UPS">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'FEDEX'){
				$link = qq|<a href="https://www.fedex.com/fedextrack/?tracknumbers=$Tracking&locale=es_MX" target="_blank" title="Go to Fedex">$ShpProvider</a>|;
			}else{
				$link = '';
			}
		}else{

			if (!$Tracking or !$ShpProvider or $ShpDate eq '0000-00-00'){
				$link = '';
			}elsif ($ShpProvider eq 'ESTAFETA'){
				$link = qq|<a href="http://rastreo3.estafeta.com/RastreoWebInternet/consultaEnvio.do?&method=&forward=&idioma=es&pickUpId=&dispatch=doRastreoInternet&tipoGuia=REFERENCE&guias=$Tracking" target="_blank" title="Go to UPS">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'UPS'){
				$link = qq|<a href="http://wwwapps.ups.com/tracking/tracking.cgi?tracknum=$Tracking" target="_blank" title="Go to UPS">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'FEDEX'){
				$link = qq|<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcom&cntry_code=us&language=english&tracknumbers=$Tracking" target="_blank" title="Go to Fedex">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'USPS'){						
				$link = qq|<a href="http://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?strOrigTrackNum=$Tracking" target="_blank" title="Go to USPS">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'DHL Ground' or $ShpProvider eq 'DHL'){						
				$link = qq|<a href="http://track.dhl-usa.com/TrackByNbr.asp?nav=Tracknbr&txtTrackNbrs=$Tracking" target="_blank" title="Go to DHL">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'Fedex'){						
				$link = qq|<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcomreg&cntry_code=us_espanol&language=espanol&tracknumbers=$Tracking" target="_blank" title="Go to Fedex">$ShpProvider</a>|;
			}elsif ($ShpProvider eq 'IW'){						
				$link = qq|<a href="http://www.islandwide.com/TrackResult.asp?num=$Tracking" target="_blank" title="Go to IW">$ShpProvider</a>|;
			}else{
				$link = '';
			}
		}

		if ($link){
			$output = " $ShpDate<br>$link<br>";
			$output .= (!$cfg{'use_shipping_tracking_mx'})? "<a href='#tabs' id='ajax_btn' title='Track' onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=check_shipping_status&provider=$ShpProvider&tracking=$Tracking');\">$Tracking</a><br>":$Tracking;
		}elsif ($ShpProvider eq 'By Parts' or ($ShpDate ne '0000-00-00' and $ShpDate)){
			$output = " $ShpDate";

		}elsif ($in{'ajaxbuild'} and $in{'ajaxbuild'} eq 'showpackinglist'){
			$output = "";
		}else{
			$va{'cnt_mi'}++;
			$id_moreinfo=$va{'cnt_mi'};
			if ($id_products =~/^1/ or int($id_products) > 600000000) {
				$link_info = qq| <a href='#moreinfo_$id_moreinfo' OnClick=""></a>|;
			}else {
				$link_info = qq| <a href='#moreinfo_$id_moreinfo' OnClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=moreinfotrackinglink&id_moreinfo=$id_products&urlscr=$script_url')">More Info</a>|;
			}
			
			$link_info = '' if ($cfg{'use_shipping_tracking_mx'});
			$output = qq|&nbsp;<a name="result" id="result">&nbsp;</a>N/A &nbsp;&nbsp;<a class="scroll" name="moreinfo_$id_moreinfo" id="moreinfo_$id_moreinfo">&nbsp;</a><br> $link_info|;

		}
	}
	return $output;
}


sub check_kit_shipped {
# --------------------------------------------------------
# Last Modified RB: 02/10/09  16:56:48 -- Se agrego prefix(tabla) para buscar sobre ordenes/preordenes de manera indistinta
# Last Modified RB: 03/06/09  11:48:29 -- Se saca la informacion agrupada por id_parts para corregir error en el update de shpDate
# Last Modified RB: 07/29/09  17:33:34 -- Se corrige suma de qty agrupada por parts para comparar con lo enviado.


	my ($id_orders_products,$prefix) = @_;
	my ($id_parts,$qty,$qty2,@ary);

	$prefix = 'orders' if !$prefix;

	my ($id_products) = &load_name('sl_'.$prefix.'_products','ID_'.$prefix.'_products',$id_orders_products,'ID_products');
	my ($sth2) = &Do_SQL("SELECT ID_parts,SUM(Qty) FROM sl_skus_parts WHERE ID_sku_products='$id_products' GROUP BY ID_parts");	
	#GV Inicia 11jun2008
	$bandshipped=0;
	my $sth1,$rec1;
	#GV Termina 11jun2008
	while (($id_parts,$qty) = $sth2->fetchrow_array()){
		#GV Inicia modificaci�n 11jun2008
		my ($sth) = &Do_SQL("SELECT SUM( Quantity ),STATUS , IF(COUNT( ShpDate ) = SUM( Quantity),ShpDate,0) FROM sl_".$prefix."_parts WHERE ID_parts='$id_parts' AND ID_".$prefix."_products='$id_orders_products' AND ShpDate IS NOT NULL AND ShpDate != '0000-00-00' GROUP BY ID_parts;");		
		@ary = $sth->fetchrow_array();
		#GV Termina modificaci�n 11jun2008

		if ($qty ne $ary[0]){
			return 'ERROR';
		}

		#GV Inicia 11jun2008
		if ($ary[1] ne "Shipped" or $ary[2] == 0)
		{
			$bandshipped=1;
		}
	}
	if (!$bandshipped)
	{
		$sth3=&Do_SQL("Update sl_".$prefix."_products set ShpDate='$ary[2]' where ID_".$prefix."_products=$id_orders_products");
	}
	#GV Termina 11jun2008
	return 'OK';
}



sub updateordertotals{
#Acci�n: Creaci�n
#Comentarios:
# --------------------------------------------------------
# Forms Involved: 
# Created on: 18/jun/2008 02:55PM GMT -0600
# Last Modified on: 19jun2008
# Last Modified by: MCC C. Gabriel Varela S.
# Author: MCC C. Gabriel Varela S.
# Description : Actualizar� los totales de �rdenes
# Parameters :
# $idorder: ID de la orden
# Last Modified by RB on 04/15/2011 12:58:40 PM : Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:02:36 PM : Se agrega City como parametro para calculate_taxes

	# Description 19jun2008: Se incluye una condici�n para actualizar la orden cuando se est� en retwarehouse de wms, incluyendo el env�o
	($idorder)=@_;
	delete($in{'orderqty'});
	delete($in{'ordernet'});
	delete($in{'ordershp'});
	delete($in{'ordertax'});
	#GV Inicia modificaci�n 19jun2008
	$cond="or Status='Exchange'" if ($in{'cmd'}eq"retwarehouse");
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$idorder' AND (Status='Active' $cond);");
	#&cgierr("SELECT * FROM sl_orders_products WHERE ID_orders='$idorder' AND (Status='Active' $cond);");
	#GV Termina modificaci�n 19jun2008
	while ($tmp = $sth->fetchrow_hashref){

		$in{'orderqty'} += $tmp->{'Quantity'};
		$in{'ordernet'} += $tmp->{'SalePrice'};
		$in{'ordershp'} += $tmp->{'Shipping'};

	}
	#GV Inicia modificaci�n 19jun2008
	#&cgierr("Qty: $in{'orderqty'}, NeT: $in{'ordernet'}, Shp: $in{'ordershp'}");
	
	if (!$in{'ordershp'} or $in{'cmd'}eq"retwarehouse"){

		#GV Termina modificaci�n 19jun2008
		## Calculate Tax
		$in{'shp_zip'}=&load_name('sl_orders','ID_orders',$idorder,'shp_Zip') if (!$in{'shp_zip'});
		$in{'shp_state'}=&load_name('sl_orders','ID_orders',$idorder,'shp_State') if (!$in{'shp_state'});
		$in{'ordertax'} = &calculate_taxes($in{'shp_zip'},$in{'shp_state'},$in{'shp_city'},$idorder);
		$in{'orderdisc'}=&load_name('sl_orders','ID_orders',$idorder,'Discount') if (!$in{'orderdisc'});
		## Cargar Shipping
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$idorder' AND Status<>'Cancelled';");
		$va{'total_order'} = $sth->fetchrow();
		#&cgierr("$in{'ordershp'}   $va{'total_order'}-$in{'ordernet'}+$in{'orderdisc'}-$in{'ordertax'}*($in{'ordernet'}-$in{'orderdisc'})");
		#GV Inicia modificaci�n 19jun2008: S�lo se calcular� el env�o de �sta forma cuando no sea en returns
		$in{'ordershp'} = $va{'total_order'}-$in{'ordernet'}+$in{'orderdisc'}-$in{'ordertax'}*($in{'ordernet'}-$in{'orderdisc'}) if ($in{'cmd'}ne"retwarehouse");
		#GV Termina modificaci�n 19jun2008: S�lo se calcular� el env�o de �sta forma cuando no sea en returns
		my ($sth) = &Do_SQL("UPDATE sl_orders SET OrderQty='$in{'orderqty'}',OrderShp='$in{'ordershp'}',OrderTax='$in{'ordertax'}',OrderNet='$in{'ordernet'}' WHERE ID_orders='$idorder'");
		&auth_logging('opr_orders_totals',$idorder);
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $idorder,0);

	}	

}

sub recalc_totals{
#Acci�n: Creaci�n
#Comentarios:
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/27/2008 07:41AM GMT -0600
# Last Modified on: 06/27/2008
# Last Modified by: 
# Author: MCC C. Gabriel Varela S.
# Description : Recalcula los totales de �rdenes
# Parameters :
#							$idorder: ID de la orden
# Last Modified on: 09/02/08 12:29:20
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando el shipping sea 0, se deje como est�
# Last Modified on: 09/10/08 11:37:20
# Last Modified by: MCC C. Gabriel Varela S: Se hace que tambi�n se contemple el descuento
# Last Modified on: 03/13/09 09:44:08
# Last Modified by: MCC C. Gabriel Varela S: Se cambia condici�n a if ($rec->{'SalePrice'}!=0 or 1) porque no consideraba los casos que no tienen costo, pero s� shipping.
# Last Modified on: 03/17/09 16:21:59
# Last Modified by: MCC C. Gabriel Varela S: Se incluyen par�metros para sltv_itemshipping
# Last Modified RB: 12/07/2010  19:06:44 -- Se agregan parametros para calculo de shipping
# Last modified on 25 Apr 2011 17:16:47
# Last modified by: MCC C. Gabriel Varela S. :Se hace que el producto sea 000000000 si no existe
# Last Modified by RB on 06/07/2011 01:03:01 PM : Se agrega City como parametro para calculate_taxes
# Last Modified by AD on 08/08/2013 12:30:01 PM : Se elimina tax de shipping
# Last Modified by RB on 01/21/2014 01:03:01 PM : Se agrega memcached_delete

	($idorders)=@_;
	delete($in{'orderqty'});
	delete($in{'ordernet'});
	delete($in{'ordershp'});
	delete($in{'ordertax'});
	delete($in{'orderdisc'});
	#&cgierr("SELECT * FROM sl_orders_products WHERE ID_orders='$idorders' AND Status<>'Inactive';");
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$idorders' AND Status<>'Inactive';");
	my ($prd);
	while ($rec = $sth->fetchrow_hashref){

		$aa .= "$rec->{'ID_products'} <br>";
		$in{'shp_type'}=1 if (!$in{'shp_type'});
		$rec->{'ID_products'}='000000000'if ($rec->{'ID_products'}eq'' or $rec->{'ID_products'}==0);
		$in{'edt'}=&load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'edt') if (!$in{'edt'});
		$in{'orderqty'} += $rec->{'Quantity'};
		$in{'ordernet'} = round($in{'ordernet'},2) + round($rec->{'SalePrice'},2);
		$in{'orderdisc'} += $rec->{'Discount'};

		if ($rec->{'ID_products'} =~ /^1/){

			## Load Product Info
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE ID_products='".substr($rec->{'ID_products'},3,6)."';");
			if ($sth2->fetchrow >0){
				my ($sth2) = &Do_SQL("SELECT sl_products.edt, sl_products.SizeW, sl_products.SizeH, sl_products.SizeL, sl_products.Weight, sl_products.ID_packingopts, sl_products.shipping_table, sl_products.shipping_discount, sl_products.ID_products FROM sl_products WHERE ID_products='".substr($rec->{'ID_products'},3,6)."';");
				$prd = $sth2->fetchrow_hashref;
			}

			## Calcular Shipping
			if ($rec->{'SalePrice'}!=0 or 1){
				if ($rec->{'Status'} eq 'Returned'){
					$in{'ordershp'} += $rec->{'Shipping'};
				}elsif ($rec->{'Shipping'} eq ''){#elsif($rec->{'Shipping'} <= 0 or $rec->{'Shipping'} eq ''){
					($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($prd->{'edt'},$prd->{'SizeW'},$prd->{'SizeH'},$prd->{'SizeL'},$prd->{'Weight'},$prd->{'ID_packingopts'},$prd->{'shipping_table'},$prd->{'shipping_discount'},$prd->{'ID_products'});
					$in{'ordershp'} += $va{'shptotal'.$in{'shp_type'}};
				}else{
					$in{'ordershp'} += $rec->{'Shipping'};
				}

			}
		#$aa .= "Output:$va{'shptotal1'},$va{'shptotal2'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_textpr1'},$va{'shp_textpr2'}<br><br>";

			## Si el producto no lleva envio se debe limpiar el tax del envio
			if ($rec->{'Shipping'} == 0){
				my ($sth3) = &Do_SQL("UPDATE sl_orders_products SET ShpTax=0 WHERE ID_orders_products='".$rec->{'ID_orders_products'}."' LIMIT 1;");
			}

			## Se detectan y corrigen problemas de Tax
			my $Tax = (($rec->{'SalePrice'} - $rec->{'Discount'}) * $rec->{'Tax_percent'});
			if ($Tax != $rec->{'Tax'}){
				my ($sth3) = &Do_SQL("UPDATE sl_orders_products SET Tax='$Tax' WHERE ID_orders_products='".$rec->{'ID_orders_products'}."' LIMIT 1;");
			}

		}else{
			$in{'ordershp'} += $rec->{'Shipping'};
		}

	}

	$in{'ordertax'} = &calculate_taxes($in{'shp_zip'},$in{'shp_state'},$in{'shp_city'},$idorders);

	my ($sth) = &Do_SQL("UPDATE sl_orders SET OrderQty='$in{'orderqty'}',OrderShp='$in{'ordershp'}',OrderTax='$in{'ordertax'}',OrderNet='$in{'ordernet'}',OrderDisc='$in{'orderdisc'}' WHERE ID_orders='$idorders'");
	&auth_logging('opr_orders_recalc',$idorders);
	&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $idorders,0);

}

sub taxables_in_order{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/10/2008 04:50PM GMT -0600
# Last Modified on: 07/10/2008
# Last Modified by: 
# Author: 
# Description : Returns the total amount of taxable goods in order
# Parameters :	idorder

	my ($idorders) = @_;

	my ($sth) = &Do_SQL("SELECT SUM(SalePrice) FROM sl_orders_products WHERE ID_orders='$idorders' AND LEFT(ID_products,1) != 6 AND Status<>'Inactive';");
	my ($taxables) = $sth->fetchrow;

	return $taxables;
}




sub calc_tax_disc_shp{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/04/08 13:43:57
# Author: MCC C. Gabriel Varela S.
# Description : Calcula los valores para tax, discount y shp para un id_orders_products recibido. Basada en admin_rep_estabdisctaxshp de Y:\domains\dev.direksys.com\cgi-bin\administration\admin.reports.cgi
# Parameters :
# Last Modified on: 09/05/08 10:12:48
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta ahora tambi�n FP
# Last Modified on: 09/08/08 17:21:12
# Last Modified by: MCC C. Gabriel Varela S: 
# Last Modified on: 09/09/08 12:56:06
# Last Modified by: MCC C. Gabriel Varela S: Se actualiza la forma en que se calcular�n las cosas
# Last Modified on: 09/10/08 10:11:45
# Last Modified by: MCC C. Gabriel Varela S: Se actualiza la forma en que se calcular� o no el descuento
# Last Modified on: 09/15/08 11:59:22
# Last Modified by: MCC C. Gabriel Varela S: Se filtra para cuando no exista id de producto
# Last Modified on: 09/19/08 11:32:50
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la forma de contar productos, los servicios no contar�n
# Last Modified on: 01/05/09 13:30:38
# Last Modified by: MCC C. Gabriel Varela S: Se cambia el criterio para determinar si est� bien establecido el tax
# Last Modified on: 03/17/09 10:18:11
# Last Modified by: MCC C. Gabriel Varela S: Par�metros para sltv_itemshipping
# Last Modified RB: 08/07/09  13:33:03 -- $discb se verifica que no sea una cadena vacia.
# Last Modified RB: 09/01/09  15:25:28 ShippingB,TaxB,DiscB. Cuando son iguales a "0" es un posible error y se recalcula el valor, de lo contrario se salta. $shippingf sirve para no calcular el shipping nuevamente
# Last Modified RB: 12/16/2010  16:40:30 -- Par�metros para sltv_itemshipping
#Last modified on 25 Apr 2011 17:17:18
#Last modified by: MCC C. Gabriel Varela S. :Se hace que el producto sea 000000000 si no existe


	my($id_orders_products,$shippingf,$discountf)=@_;
	my ($sth1,$sth,$rec,$idpacking,$edt,$sizeq,$sizeh,$sizel,$discflex,$size,$weight,$shptotal1,$shptotal2,$shptotal1pr,$shptotal2pr,$shptype,$comillitas,$totshpord,$ntax,$ndisc,$shippingb,$taxb,$discb,$fpb,$shippingcad,$fpago);
	if (!$id_orders_products)
	{
		$sth1=&Do_SQL("select last_insert_id(ID_orders_products)as last from sl_orders_products order by last desc limit 1");
		$id_orders_products=$sth1->fetchrow;
	}
	$sth=&Do_SQL("Select sl_orders_products.ID_orders_products,sl_orders_products.ID_products,sl_products.edt,sl_products.SizeW,sl_products.SizeH,sl_products.SizeL,sl_products.flexipago,sl_products.Weight,sl_orders_products.ID_orders,sl_orders.shp_type,if((sl_orders_products.Discount=0 and sl_orders.OrderDisc!=0 and not isnull(OrderDisc)),0,1) as DiscB,if((sl_orders_products.Tax=0 and OrderTax!=0 and not isnull(OrderTax) and SalePrice!=0)or isnull(Tax),0,1) as TaxB,if(sl_orders_products.Shipping=0 and OrderShp!=0 and not isnull(OrderShp),0,1)as ShippingB, Products, Payments, OrderTax, SalePrice, OrderShp, OrderDisc,sl_orders_products.Discount, Tax,Shipping,Quantity
	from sl_orders_products inner join sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders) inner join sl_products on (right(sl_orders_products.ID_products,6)=sl_products.ID_products) inner join(Select sl_orders_products.ID_orders, count(ID_orders_products) as Products, Payments
	from sl_orders_products inner join (Select sl_orders_payments.ID_orders, count(ID_orders_payments) as Payments
	from sl_orders_payments
	group by sl_orders_payments.ID_orders)as tempt on (tempt.ID_orders=sl_orders_products.ID_orders)
	where id_products not like '6%'
	group by sl_orders_products.ID_orders)as tempo on(tempo.ID_orders=sl_orders.ID_orders)
	where sl_orders_products.ID_products not like '6%' and sl_orders_products.ID_orders_products=$id_orders_products");
	$rec=$sth->fetchrow_hashref;

	$discb=$rec->{'Discount'};
	$taxb=$rec->{'Tax'};
	$shippingb=$rec->{'Shipping'};
	if ($rec->{'ID_products'} ne '')	{
		#########################
		#Se establece el Shipping
		#########################
		if ($rec->{'ShippingB'}==0)		{
			if ($rec->{'Products'}==1)			{
				$totshpord=$rec->{'OrderShp'};
			}else{
				if ($rec->{'ID_products'} eq'' or $rec->{'ID_products'}==0){
					$rec->{'ID_products'}='000000000';
				}
				$idpacking = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'ID_packingopts');
				$edt= $rec->{'edt'};
				$sizew=$rec->{'SizeW'};
				$sizeh=$rec->{'SizeH'};
				$sizel=$rec->{'SizeL'};
				$discflex=$rec->{'flexipago'};
				$size=$sizew*$sizeh*$sizel;
				$weight=$rec->{'Weight'};

				## Fixed/Variable/Table Shipping ? 
				my $shpcal  = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'shipping_table');
				my $shpmdis = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'shipping_discount');
				($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$weight,$idpacking,$shpcal,$shpmdis,substr($rec->{'ID_products'},3,6));
				$va{'shptotal1'}=$shptotal1;
				$va{'shptotal2'}=$shptotal2;
				$va{'shptotal1pr'}=$shptotal1pr;
				$va{'shptotal2pr'}=$shptotal2pr;
				$comillitas=$rec->{'shp_type'};
				$totshpord=$va{'shptotal'.$comillitas.''};
			}
			$shippingb=$totshpord;
		}
		##########################
		#Se establece el Descuento
		##########################
		if ($rec->{'DiscB'}==0 and $discountf==1){
			if ($rec->{'ID_products'} =~ /$cfg{'disc40'}/){
				$discb=$rec->{'SalePrice'}*$rec->{'Quantity'}*(40/100);
			}elsif ($rec->{'ID_products'} =~ /$cfg{'disc30'}/){
				$discb=$rec->{'SalePrice'}*$rec->{'Quantity'}*(30/100);
			}else{
				$fpago=&load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'flexipago');
				$discb=($rec->{'SalePrice'}*$cfg{'fpdiscount'.$fpago}/100);
			}
		}


		####################
		#Se establece el Tax
		####################
		#&cgierr("MES: $rec->{'TaxB'}: $taxb=$rec->{'OrderTax'}*($rec->{'SalePrice'}-$discb)");
		if ($rec->{'TaxB'}==0)
		{
			$taxb=$rec->{'OrderTax'}*($rec->{'SalePrice'}-$discb);
		}
		################
		#Se establece FP
		################
		$fpb=1;
		$discb=0	if $discb	eq '';
		$taxb=0	if $taxb	eq '';
		$shippingb=0	if $shippingb	eq '';
		$shippingcad="Shipping=$shippingb," if $shippingf;
		&Do_SQL("update sl_orders_products set $shippingcad Tax=$taxb, Discount=$discb, FP=$fpb where ID_orders_products=$rec->{'ID_orders_products'};");
	}
	#return ($taxb,$discb,$shippingb);
}

sub showcreditcards{
# --------------------------------------------------------
# Created by: Jose Ramirez Garcia
# Created on: 25jun2008
# Description : It shows customer's credit cards
# Notes : (Modified on : Modified by :)
# Last Modified on: 09/17/08 12:46:31
# Last Modified by: MCC C. Gabriel Varela S: Copiada y borrada desde: Y:\domains\dev.direksys.com\cgi-bin\administration\sub.base.html.cgi
# Last Modified on: 11/25/08 12:27:29
# Last Modified by: MCC C. Gabriel Varela S: Se hace que tambi�n pueda ser llamada desde edici�n de �rdenes.
# Last Modified on: 12/23/08 16:20:25
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta orders
# Last Modified on: 01/09/09 10:16:19
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta el comando opr_orders para pre�rdenes tambi�n.


	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($type,$field);
	$type = '';
	$tpay = 'Credit-Card';
	my $tmp;
	$tmp="";
	$tmp="tmp" if ($in{'addpa'});

	my ($sth1)=&Do_SQL("SELECT COUNT(DISTINCT(PmtField3)) FROM sl_".$type."orders_payments$tmp WHERE id_".$type."orders=$in{'id_'.$type.'orders'} AND type='$tpay'");
	$va{'matches'} = $sth1->fetchrow;
	if ($va{'matches'}>1){
		$va{'searchresultscc'} .= "<tr>\n";
		$va{'searchresultscc'} .= "   <td class='menu_bar_title'>&nbsp;</td>\n";
		$va{'searchresultscc'} .= "   <td class='menu_bar_title'>Type</td>\n";
		$va{'searchresultscc'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
		$va{'searchresultscc'} .= "   <td class='menu_bar_title'>Exp</td>\n";
		$va{'searchresultscc'} .= "   <td class='menu_bar_title'>CVN</td>\n";
		$va{'searchresultscc'} .= " </tr>\n";
		my ($sth) = &Do_SQL("SELECT DISTINCT * FROM sl_".$type."orders_payments$tmp WHERE id_".$type."orders=$in{'id_'.$type.'orders'} AND type='$tpay' GROUP BY PmtField3 order by id_".$type."orders_payments desc");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresultscc'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresultscc'} .= " 	<td class='smalltext' valign='top'><input type='radio' class='radio' name='id_".$type."orders_payments' value='$rec->{'ID_'.$type.'orders_payments'}'></td>";
			$va{'searchresultscc'} .= "   <td class='smalltext' valign='top'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
			$va{'searchresultscc'} .= "   <td class='smalltext' valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
			$va{'searchresultscc'} .= "   <td class='smalltext' valign='top'>$rec->{'PmtField4'}</td>\n";
			$va{'searchresultscc'} .= "   <td class='smalltext' valign='top'>$rec->{'PmtField5'}</td>\n";
			$va{'searchresultscc'} .= "</tr>\n";
		}
	}elsif ($va{'matches'}==1){
		my ($sth) = &Do_SQL("SELECT DISTINCT PmtField3, max(ID_".$type."orders_payments)as ID_".$type."orders_payments  FROM sl_".$type."orders_payments$tmp WHERE id_".$type."orders=$in{'id_'.$type.'orders'} AND type='$tpay' GROUP BY PmtField3 order by ID_".$type."orders_payments desc");
		$rec = $sth->fetchrow_hashref;
		$cc = $rec->{'PmtField3'};
		$id = $rec->{'ID_'.$type.'orders_payments'};
		$va{'searchresultscc'} .= " 	<input type='hidden' name='id_".$type."orders_payments' value='$id'>";
	}else{
		$va{'searchresultscc'} = qq|
		   <tr>
				<td colspan='4' class='menu_bar_title' align="center">&nbsp;</td>
			</tr>
			<tr>
				<td colspan='4' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $va{'searchresultscc'};
}

sub orders_payments_a_day{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/03/08 17:17:07
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters : Ver orden 103881
# Last Modified RB: 11/05/08  16:19:59 Added Amount and CC number

	my ($idorders,$amount,$ccard)=@_;
	my $sth;
	$sth=&Do_SQL("SELECT count(*) FROM sl_orders_payments
								INNER JOIN sl_orders_plogs ON sl_orders_payments.ID_orders_payments = sl_orders_plogs.ID_orders_payments
								WHERE sl_orders_payments.ID_orders = $idorders AND sl_orders_plogs.Date = CURDATE()
								AND Amount>='$amount' AND PmtField3 = '$ccard' ");

	return $sth->fetchrow;
}






sub cancelorder{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/07/08 16:37:31
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/10/08 11:11:04
# Last Modified by: MCC C. Gabriel Varela S: Se contin�a.
# Last Modified on: 11/12/08 12:07:43
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a preorder_to_order
# Last Modified on: 11/13/08 10:16:46
# Last Modified by: MCC C. Gabriel Varela S: Se hace que la funci�n regrese un valor para manifestar la existencia de un error en su caso
# Last Modified on: 11/24/08 12:53:00
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a recalc_totals
# Last Modified RB: 11/26/08  14:47:55 -- Se incorpora excludefee para no cobrar el cancellation fee y se manda a StatusPay 'Pending Refund'
# Last Modified on: 01/22/09 18:09:50
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si la cantidad a cobrar/acreditar es 0, s�lo se cancele la preorden, sin crear orden.
# Last Modified on: 01/23/09 09:46:17
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para poder tomar en cuenta pagos que son Lawaway con MO
# Last Modified on: 02/16/09 15:51:39
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se consideren diferencias basadas en 2 decimales.
# Last Modified RB: 02/23/09  13:19:12 -- Los paagos no cobrados de la preorden se pasan a "Void"
# Last Modification by JRG : 03/13/2009 : Se agrega log


	my ($id_orders,$excludefee)=@_;
	my $sth,$rec,$cancelprice,$amounttorefund;
	$sth=&Do_SQL("Select * from sl_orders where ID_orders=$id_orders and Ptype!='Credit-Card'");
	$rec=$sth->fetchrow_hashref;
	$cancelprice = 0;


	### Orders Totals
	my $tot_tax,$total_order,$ordernet,$ordershp,$tax,$ordertax,$success;
	$tot_tax = (&taxables_in_order($rec->{'ID_orders'})-$rec->{'Orderisc'})*$rec->{'OrderTax'};
	$total_order = int(($rec->{'OrderNet'}+$rec->{'OrderShp'}+$rec->{'OrderNet'}*$rec->{'OrderTax'})*100+0.9)/100;
	$ordernet = &format_price($rec->{'OrderNet'});
	$ordershp = &format_price($rec->{'OrderShp'});
	$tax = $rec->{'OrderTax'}*100;
	$ordertax = &format_number($rec->{'OrderTax'}*100);
	if (!$excludefee){
		if ($total_order*.10<10)
		{
			$cancelprice=10;
		}
		else
		{
			$cancelprice=$total_order*.10;
		}
	}

	$sth=&Do_SQL("Select round(if(not isnull(sum(Amount)),sum(Amount),0)*-1+$cancelprice,2)
from sl_orders_payments 
where ID_orders=$id_orders 
and Captured='Yes' and CapDate!='0000-00-00' 
and IF((Type='Credit-Card' or Type='Layaway') AND PmtField3!='',AuthCode!='0000' and not isnull(AuthCode) 
and AuthCode!='' and AuthDateTime!='0000-00-00' and not isnull(AuthDateTime) and AuthDateTime!='', 
Status in ('Approved')) AND Status in ('Approved')");

	$amounttorefund=$sth->fetchrow;
	if ($amounttorefund!=0)
	{
		my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders =$id_orders
													AND (Status NOT IN ('Approved', 'Chargeback')
													OR (AuthCode IS NULL OR AuthCode = '' OR AuthCode != '0000'))
													ORDER BY ID_orders_payments LIMIT 1 ");
		my ($rec2) = $sth2->fetchrow_hashref;
		my $queryPmt;
		$queryPmt = '';
		for my $i(1..9){
				$queryPmt .= ",PmtField$i = '".$rec2->{'PmtField'.$i.''}."' ";
		}



		if ($id_orders>0)
		{
			&Do_SQL("Update sl_orders SET PostedDate=CURDATE(), StatusPay='Pending Refund' WHERE ID_orders = '$id_orders' ");
			&Do_SQL("Update sl_orders_payments set Status='Void' where id_orders=$id_orders and (Captured='No') and (isnull(CapDate)or CapDate='0000-00-00')");

			&Do_SQL("Insert into sl_orders_products set ID_products=600000000+$cfg{'cancelfee'},ID_orders=$id_orders,Quantity=1,SalePrice=$cancelprice,PostedDate=CURDATE(),Status='Active',Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
			&Do_SQL("Insert into sl_orders_payments set ID_orders=$id_orders,
								Type= 'Credit-Card' $queryPmt , Amount =$amounttorefund, Reason='Other',PaymentDate = CURDATE(),PostedDate=CURDATE(),
								Status='Approved',Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
			#&Do_SQL("Update sl_orders set Status='Cancelled' where ID_orders=$id_orders");
			&auth_logging('orders_to_can',$id_orders);
			&recalc_totals($id_orders);
			$success=1;
		}
		else
		{
			$success=0;
		}
	}
	else
	{
		$success=1;
		&Do_SQL("Update sl_orders_payments set Status='Void' where id_orders=$id_orders and (Captured='No') and (isnull(CapDate)or CapDate='0000-00-00')");
		&Do_SQL("Update sl_orders set Status='Cancelled' where ID_orders=$id_orders");
		&auth_logging('orders_to_can',$id_orders);
	}
	return $success;
}

sub showcreditncards{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12/11/08 12:25:19
# Author: MCC C. Gabriel Varela S.
# Description :   Basada en showcreditcards
# Parameters :
# Last Modified on: 12/23/08 16:23:18
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta pre�rdenes


	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($type,$field);
	$type = '';
	$tpay = 'Credit-Card';
	my $tmp;
	$tmp="";
	$tmp="tmp" if ($in{'addnpa'});

	my ($sth) = &Do_SQL("SELECT DISTINCT Type,PmtField1,PmtField2,PmtField3,PmtField4,PmtField5,PmtField6,PmtField7,PmtField8,PmtField9,date_format( now( ) , '%Y/%m/%d' ) FROM sl_".$type."orders_payments$tmp WHERE id_".$type."orders=$in{'id_'.$type.'orders'} AND type='$tpay' GROUP BY PmtField3 order by id_".$type."orders_payments desc limit 1");
	@rec = $sth->fetchrow_array;
	$in{'type'}=$rec[0];
	for(1..9)
	{
		$cadpmt="pmtfield$_";
		$in{$cadpmt}=$rec[$_];
	}
	$rec[4]=~/(\d{2})(\d{2})/;
	$in{'month'}=$1;
	$in{'year'}=$2;
	$in{'paymentdate'}=$rec[10];
	return;
}


sub remove_tracking {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on:  01/07/2009
# Last Modified on: 
# Last Modified by: 
# Description : it shows the icon to remove tracking info
# Forms Involved: 
# Parameters :
# Last Modified RB: 01/15/09  11:31:44 - Only developers can remove the tracking info


	my ($Tracking,$ShpProvider,$ShpDate,$id_orders_products)=@_;
	my ($output,$link);
	$output = '';
	if (!$Tracking or !$ShpProvider or $ShpDate eq '0000-00-00'){
		$link = '';
	}elsif ($ShpProvider eq 'UPS'){
		$link = qq|<a href="http://wwwapps.ups.com/tracking/tracking.cgi?tracknum=$Tracking" target="_blank" title="Go to UPS">$ShpProvider</a>|;
	}elsif ($ShpProvider eq 'FEDEX'){
		$link = qq|<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcom&cntry_code=us&language=english&tracknumbers=$Tracking" target="_blank" title="Go to Fedex">$ShpProvider</a>|;
	}elsif ($ShpProvider eq 'USPS'){						
		$link = qq|<a href="http://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?strOrigTrackNum=$Tracking" target="_blank" title="Go to USPS">$ShpProvider</a>|;
	}elsif ($ShpProvider eq 'DHL Ground' or $ShpProvider eq 'DHL'){						
		$link = qq|<a href="http://track.dhl-usa.com/TrackByNbr.asp?nav=Tracknbr&txtTrackNbrs=$Tracking" target="_blank" title="Go to DHL">$ShpProvider</a>|;
	}elsif ($ShpProvider eq 'Fedex'){						
		$link = qq|<a href="http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcomreg&cntry_code=us_espanol&language=espanol&tracknumbers=$Tracking" target="_blank" title="Go to Fedex">$ShpProvider</a>|;
	}else{
		$link = '';
	}		

	if ($link and $usr{'usergroup'} eq '1'){
		$output = "<a href='[va_script_url]?cmd=opr_orders&view=[in_id_orders]&remove_tracking_info=$id_orders_products#tabs'><img src='[va_imgurl]/[ur_pref_style]/tracking_remove.png' title='Remove Tracking Info' alt='' border='0'></a>";
	}
	#&cgierr("$usr{'usergroup'} y $output");
	return $output;
}

sub products_sum_in_order{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/08/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified by RB: Se agrega busqueda por producto en especifico
# Last Modified by RB on 2012/05/30: Se suma tax solo para productos SalePrice > 0.05
# Last Modified by RB on 2014/09/10: Se comenta /*AND LEFT(ID_products,1) != 6*/ porque es llamado en invoices. Por lo que ahora tambien se incluyen los servicios.

	my ($idorders, $field) = @_;

	$query  ='';
	$query = " AND ID_products  =  $in{'id_products'} "  if ($in{'id_products'} and  length($in{'id_products'})	== 9 and substr($in{'id_products'},0,1)==4);
	my $mod = $field eq 'Shipping' ? " SUM($field + ShpTax) " : " SUM($field) ";


	my ($sth) = &Do_SQL("SELECT $mod FROM sl_orders_products WHERE ID_orders='$idorders' /*AND LEFT(ID_products,1) != 6*/ AND Status<>'Inactive' AND IF('$field' = 'Tax', ABS(SalePrice) > 0.05,1) $query;");
	my ($sum) = $sth->fetchrow;

	return $sum;
}

sub total_orders_products{
# --------------------------------------------------------
# Author: Jose Ramirez Garci
# Created on: 08/01/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified by RB: Se agrega busqueda por producto en especifico
# Last Modified by RB on 2012/05/30: Se suma tax solo para productos SalePrice > 0.05

	my ($idorders) = @_;

	$query  ='';
	$query = " AND ID_products  =  $in{'id_products'} "  if ($in{'id_products'} and  length($in{'id_products'})	== 9 and substr($in{'id_products'},0,1)==4);
	#$query .="_"	if $idorders	eq '8192';	
	my $sql = "SELECT (Sum(if(ID_products not like '6%' and sl_orders_products.Status!='Inactive',SalePrice-Discount+IF(ABS(SalePrice) > 0.05,Tax,0)+Shipping+ShpTax,0)))+Sum(if(ID_products like '6%' and sl_orders_products.Status!='Inactive',SalePrice,0)) as OrderTotal FROM sl_orders_products WHERE ID_orders='$idorders' $query GROUP BY ID_orders";		
	if ($cfg{'calc_tax_in_services'}){
		$sql = "SELECT (Sum(if(sl_orders_products.Status!='Inactive',SalePrice-Discount+IF(ABS(SalePrice) > 0.05,Tax,0)+Shipping+ShpTax,0))) as OrderTotal FROM sl_orders_products WHERE ID_orders='$idorders' $query GROUP BY ID_orders";
	}
	
	my ($sth) = &Do_SQL($sql);
	my ($total) = $sth->fetchrow;

	return $total;	
}

sub check_balance{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/29/09 14:00:48
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	($id,$source)=@_;
	$in{'edit_type'}=$source;
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();

	$sth=&Do_SQL("SELECT (Sum(if(ID_products not like '6%' and $cadtbproducts.Status!='Inactive',SalePrice-Discount+Tax+Shipping,0)))+Sum(if(ID_products like '6%' and $cadtbproducts.Status!='Inactive',SalePrice,0))-if(not isnull(Sumpay),Sumpay,0) as Diff
FROM $cadtbproducts
LEFT JOIN (select $cadidorders,sum(amount)as SumPay from $cadtbpayments where $cadidorders=$id and Status not in ('Cancelled','Void','Order Cancelled') group by $cadidorders)as tempo on (tempo.$cadidorders=$cadtbproducts.$cadidorders)
where $cadtbproducts.$cadidorders=$id
GROUP BY $cadtbproducts.$cadidorders");
	return $sth->fetchrow();
}




sub repairOrderDates{
# Last Modification by JRG : 03/13/2009 : Se agrega log	

	my ($id_orders) = @_;

	$sth = &Do_SQL("SELECT Date,Status FROM sl_orders WHERE ID_orders = $id_orders ");
	my ($orddate,$status) = $sth->fetchrow();
	$posteddate = '';
	#### Order with Shipping Date
	$sth_prd = &Do_SQL("SELECT ShpDate,Date FROM sl_orders_products WHERE ID_orders='$id_orders' AND ShpDate IS NOT NULL AND ShpDate<>'0000-00-00' ORDER BY ShpDate ASC");	
	($shpdate,$prd_date) = $sth_prd->fetchrow_array();

	### Parts Shipping Date
	#### Check Shipping Date From Notes
	$sth_prd = &Do_SQL("SELECT sl_orders_parts.ShpDate FROM sl_orders_products, sl_orders_parts WHERE ID_orders = '$id_orders' and sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products and sl_orders_parts.ShpDate IS NOT NULL and sl_orders_parts.ShpDate <> '0000-00-00' ORDER BY sl_orders_parts.ShpDate ASC");
	$part_date = $sth_prd->fetchrow();
	if ((&date_to_unixtime($part_date) < &date_to_unixtime($shpdate) or !$shpdate) and $part_date and $part_date ne '0000-00-00'){
		 $shpdate = $part_date;
	}

	#### Check Shipping Date From Notes
	$sth_notes = &Do_SQL("SELECT Date FROM sl_orders_notes WHERE ID_orders='$id_orders' AND Notes like 'The Status of the Order has been changed to Shipped%' ORDER BY Date ASC");
	$note_date = $sth_notes->fetchrow();


	### Determining the posteddate
	if ($note_date and $shpdate and &date_to_unixtime($prd_date)>&date_to_unixtime($note_date)){
		$posteddate = $note_date;
	}elsif ($shpdate){
		$posteddate = $shpdate;
	}elsif ($note_date){
		$posteddate = $note_date;
	}else{
		$posteddate = $orddate;
	}


	## Update Orders
	&Do_SQL ("UPDATE sl_orders SET PostedDate='$posteddate' WHERE ID_orders=$id_orders");
	&auth_logging('orders_posteddate_updated',$id_orders);

	## Update Products in Order
	$sth_prd = &Do_SQL("SELECT ID_orders_products,Date,SalePrice,ShpDate,ID_products FROM sl_orders_products WHERE ID_orders='$id_orders'");
	while(($id_orders_prd,$ldate,$sprice,$shpdate,$idprod) = $sth_prd->fetchrow_array()){
		if ((&date_to_unixtime($ldate)-&date_to_unixtime($orddate))>1){
			if ($sprice<0 or $idprod =~ /^4|^6/){
				&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$ldate' WHERE ID_orders_products=$id_orders_prd");
			}elsif (!$shpdate and $shpdate ne '0000-00-00'){
				&Do_SQL ("UPDATE sl_orders_products SET PostedDate=NULL WHERE ID_orders_products=$id_orders_prd");
			}elsif ($shpdate){
				&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$shpdate' WHERE ID_orders_products=$id_orders_prd");
			}
		}else{
			&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$posteddate' WHERE ID_orders_products=$id_orders_prd");
		}
	}

 	## Update Payments in Order
 	&Do_SQL ("UPDATE sl_orders_payments SET PostedDate=NULL WHERE ID_orders=$id_orders");
	$sth_pay = &Do_SQL("SELECT ID_orders_payments,Date,Amount,Paymentdate FROM sl_orders_payments WHERE ID_orders='$id_orders' AND PostedDate IS NULL");# AND Status NOT IN ('Order Cancelled', 'Cancelled')
	LINE: while( ($id_orders_pay,$ldate,$amt,$pdate) = $sth_pay->fetchrow_array()){
		$sth2 = &Do_SQL("SELECT PostedDate FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Amount='$amt' AND Status='Cancelled' AND Paymentdate='$pdate'");
		$pdc = $sth2->fetchrow;
		if ($pdc ne ''){
			&Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$pdc' WHERE Paymentdate='$pdate' AND ID_orders=$id_orders");
			next LINE;
		}elsif ((&date_to_unixtime($ldate)-&date_to_unixtime($orddate))>1){
			&Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$ldate' WHERE ID_orders_payments=$id_orders_pay");
		}else{
      &Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$posteddate' WHERE ID_orders_payments=$id_orders_pay");
		}
	}
	return $posteddate;
}


sub recal_order_all{
#-----------------------------------------
# Created on: 03/19/09  13:43:37 By  Roberto Barcenas
# Forms Involved: opr_orders, opr_ 
# Description : Recalcula toda la orden/preorden
# Parameters : 	$id_orders, $prefix
# Last Modified RB: 12/06/2010  18:35:30 -- Parametros para sltv_itemshipping
# Last Modified by RB on 04/15/2011 01:01:30 PM : Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:05:29 PM : Se agrega City como parametro para calculate_taxes
# Last Modified by RB on 04/03/2016 11:35:29 PM : Se agrega City como parametro para calculate_taxes
#
	if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'} == 1){
		return;
	}

	my ($id_orders,$state,$city,$zip,$prefix) = @_;
	my ($total_shipping,$total_taxes);
	my $pct_taxes = &calculate_taxes($zip,$state,$city,$id_orders);

	if ($pct_taxes ne "$in{'ordertax'}"){

		my ($sth) = &Do_SQL("SELECT ID_".$prefix."_products,ID_products,RIGHT(ID_products,6),SalePrice FROM sl_".$prefix."_products WHERE ID_".$prefix." = '". $id_orders ."' AND LEFT(ID_products,1) <> 6 AND Status IN('Active','Exchange') AND (ShpDate IS NULL OR ShpDate = '0000-00-00') AND Cost >= 0 ORDER BY ID_".$prefix."_products "); 
		while(my($id_orders_products,$id_sku,$id_products,$sale_price) = $sth->fetchrow()){

			my $shipping = 0;
			my $tax 	= 0;

			my $sh_t = &load_name("sl_$prefix","ID_$prefix",$id_orders,'shp_type');
			my $idpacking = &load_name('sl_products','ID_products',$id_products,'ID_packingopts');
			my $edt= &load_name('sl_products','ID_products',$id_products,'edt');
			my $sizew=&load_name('sl_products','ID_products',$id_products,'SizeW');
			my $sizeh=&load_name('sl_products','ID_products',$id_products,'SizeH');
			my $sizel=&load_name('sl_products','ID_products',$id_products,'SizeL');
			my $size=$sizew*$sizeh*$sizel;
			my $weight=&load_name('sl_products','ID_products',$id_products,'Weight');

			## Fixed/Variable/Table Shipping ? 
			my $shpcal  = &load_name('sl_products','ID_products',$id_products,'shipping_table');
			my $shpmdis = &load_name('sl_products','ID_products',$id_products,'shipping_discount');
			($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$weight,$idpacking,$shpcal,$shpmdis,$id_products);

			$shipping = $va{'shptotal'.$sh_t};
			$tax = $sale_price * $pct_taxes;

			&Do_SQL("UPDATE sl_".$prefix."_products SET Shipping = '". $shipping ."',Tax = '". $tax ."' WHERE ID_".$prefix."_products = '". $id_orders_products ."';");

		}

		($prefix eq 'orders') ? &recalc_totals($id_orders) : &recalcpreordertotals($id_orders);
	}
}



sub build_query_table_layaway{
#-----------------------------------------
# Created on: 03/26/09  15:11:34 By  Roberto Barcenas
# Forms Involved: dashboard_layaway
# Description : Genera y retorna los ids para pasarlos al advsearch de  y formar la tabla dashboard de layaway
# Parameters :
# Last Modified RB: 04/08/09  12:43:28 -- Se agrega rango mayor a 7 dias para conctactados
 

	my ($res) = @_;
	my ($query,$type,$rows);
	$type = '=';
	$type = '!'.$type	if $in{'type'} eq 'tc';
	$rows = "COUNT(sl_orders.ID_orders) "	if $res == 1;
	$rows = "GROUP_CONCAT(sl_orders.ID_orders SEPARATOR '|') "	if $res != 1;

	$rows =~	s/sl_orders\.//	if	$in{'mod'}==1;	

	if ($in{'mod'} == 1){
	####### NOT CONTACTED
		$query = "SELECT $rows FROM (SELECT sl_orders.ID_orders,count(ID_orders_notes)as NNotes
											FROM sl_orders LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
											WHERE /*ID_orders = 0 AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders.ID_orders 
											AND Type='Layaway' AND PmtField3 $type '' AND Status NOT IN('Void', 'Cancelled')) GROUP BY sl_orders.ID_orders HAVING NNotes=0)as tmp GROUP BY NNotes;";

	}elsif ($in{'mod'} == 2){
	######## PAYMENTS 0K
		$query = "SELECT $rows FROM sl_orders INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Layaway' AND PmtField3 $type '' GROUP BY ID_orders) AS tmp 
											ON sl_orders.ID_orders = tmp.ID_orders WHERE /*ID_orders = 0  AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 1 > 
											(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders.ID_orders AND Amount > 0 AND Status NOT IN('Cancelled','Void') AND Paymentdate <= CURDATE() AND Captured ='No');";

	}elsif ($in{'mod'} == 3){
	######## PAYMENTS DUE
		$query = "SELECT $rows FROM sl_orders INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Layaway' AND PmtField3 $type '' GROUP BY ID_orders) AS tmp 
											ON sl_orders.ID_orders = tmp.ID_orders WHERE /*ID_orders = 0  AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 0 < 
											(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = sl_orders.ID_orders AND Amount > 0 AND Status NOT IN('Cancelled','Void') AND Paymentdate <= CURDATE() AND Captured ='No');";

	}elsif ($in{'mod'} == 4){
	######## 2 DAYS
		$query = "SELECT $rows FROM sl_orders INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Layaway' AND PmtField3 $type '' AND PaymentDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 7 DAY) GROUP BY ID_orders) AS tmp 
											ON sl_orders.ID_orders = tmp.ID_orders WHERE /*ID_orders = 0  AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 0 < 
											(SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_orders.ID_orders AND DATEDIFF(CURDATE(),Date) <= 2);";

	}elsif ($in{'mod'} == 5){
	######## 7 DAYS
		$query = "SELECT $rows FROM sl_orders INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Layaway' AND PmtField3 $type '' AND PaymentDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 7 DAY) GROUP BY ID_orders) AS tmp 
											ON sl_orders.ID_orders = tmp.ID_orders WHERE /*ID_orders = 0  AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 0 < 
											(SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_orders.ID_orders AND DATEDIFF(CURDATE(),Date) BETWEEN 3 AND 7);";

	}elsif ($in{'mod'} == 6){
	######## > 7 DAYS
		$query = "SELECT $rows FROM sl_orders INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Layaway' AND PmtField3 $type '' AND PaymentDate BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 7 DAY) GROUP BY ID_orders) AS tmp 
											ON sl_orders.ID_orders = tmp.ID_orders WHERE /*ID_orders = 0  AND*/Ptype!='Credit-Card' and sl_orders.Status NOT IN('Expired', 'Void', 'Cancelled') AND 0 < 
											(SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_orders.ID_orders AND DATEDIFF(CURDATE(),Date) > 7 ORDER BY Date DESC LIMIT 1);";
	}
	my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
	my ($sth) = &Do_SQL($query);
	return $sth->fetchrow();
}


sub build_query_table_moneyorder{
#-----------------------------------------
# Created on: 03/26/09  17:45:28 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : build_query_table_moneyorder(count=1 group_concat=2 ,paid=1 unpaid=2, 2=48 hrs  7=7 days  8 = >7 days or 0) 
# Last Modified RB: 04/08/09  12:45:59 -- Se incluye rango mayor a 7 dias para contactados no pagados


	my ($res,$type,$days) = @_;
	my ($rows,$diff,$range,$mod);
	my $rows = $rows = "COUNT(sl_orders.ID_orders) ";
	$rows = "GROUP_CONCAT(sl_orders.ID_orders SEPARATOR '|') "	if $res != 1;
	$diff = '=';
	$diff = '!'.$diff	if $type == 2;
	($days == 0) and ($range = " ") and ($mod = "1 > ");
	($days == 2) and ($range = " AND DATEDIFF(CURDATE(),Date) <= 2 ") and ($mod = "0 < ");
	($days == 7) and ($range = " AND DATEDIFF(CURDATE(),Date) BETWEEN 3 AND 7 ") and ($mod = "0 < ");
	($days == 8) and ($range = " AND DATEDIFF(CURDATE(),Date) > 7 ") and ($mod = "0 < ");


	my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
	my ($sth) = &Do_SQL("SELECT $rows FROM sl_orders
											INNER JOIN (SELECT ID_orders FROM sl_orders_payments WHERE Type='Money Order' AND Status NOT IN('Void','Cancelled') 
											AND Captured $diff 'Yes' GROUP BY ID_orders) AS tmp ON sl_orders.ID_orders = tmp.ID_orders 
											WHERE Status NOT IN('Void', 'Cancelled') AND /*ID_orders = 0 AND*/Ptype!='Credit-Card' AND $mod (SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders = sl_orders.ID_orders $range );");

	return $sth->fetchrow();
}

sub links_orders_info{
# --------------------------------------------------------
# Created on: 2/16/10 12:29 PM
# Author: L.I. Roberto Barcenas.
# Description :   Build Links to Specific order lists group by status
# Parameters : None	
# Forms Involved: All Sales Tables in Orders Home

	my (@status) = &load_enum_toarray('sl_orders','Status');
	for (0..$#status){
		$va{'orders_wpayinfo'} .= qq|<li><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&search=advSearch&wprod=1&Status=$status[$_]&sb=id_orders&so=DESC">$status[$_]</a></li>\n|;
	}
	for (0..$#status){
		$va{'orders_wprodinfo'} .= qq|<li><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&search=advSearch&wpay=1&Status=$status[$_]&sb=id_orders&so=DESC">$status[$_]</a></li>\n|;
	}

}

sub is_codorder_in_transit{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/10/10 18:14:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 10/19/2010: Se agrega verificacion de partes escaneadas

	my ($id_orders)=@_;
	my ($in_transit) = 0;

	my $sth=&Do_SQL("SELECT IF(COUNT(*) > 0,1,0) AS in_transit
			        FROM sl_orders_products INNER JOIN sl_orders_parts 
			        ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
			        WHERE ID_orders = '$id_orders';");
	$in_transit = $sth->fetchrow;
	
	if (!$in_transit){
					
			my $sth=&Do_SQL("Select if(sl_orders.Status='Processed',if(not isnull(NULL),1,0),0)as InTransit
					from sl_orders
					where sl_orders.ID_orders='$id_orders'
					and Status='Active'");
			
			$in_transit = $sth->fetchrow;
	}
	return $in_transit; 
}



sub delivery_status_order {
# --------------------------------------------------------
# Created on: 
# Author: L.I. Roberto Barcenas.
# Description : Returns 0=Unshipped,1=Shipped,2=COD in transit
# Parameters : id_orders	

	my ($id_orders) = @_;

	my ($sth_shp) = &Do_SQL("SELECT 
								IF(Status='Shipped',1,IF(PartSent > 0,2,0)) AS exchange 
							FROM sl_orders 
							LEFT JOIN
								(
									SELECT ID_orders,COUNT(*) AS PartSent FROM sl_orders_products INNER JOIN sl_orders_parts
									ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products
									WHERE ID_orders = ". $id_orders ."  GROUP BY ID_orders
								)tmp
								USING(ID_orders)
								WHERE sl_orders.ID_orders = ". $id_orders ."; ");
	my $status =  $sth_shp->fetchrow();

	return $status;

}



#############################################################################
#############################################################################
#   Function: get_zone_by_zipcode
#
#       Es: Obtiene el ID_zone en base a un ZipCode
#       En: English description if possible
#
#
#    Created on: 05/12/2012  13:20:10
#
#    Author: Cesar Cedillo
#
#    Modifications:
#
#        - Modified on 
#        - Modified on 
#
#   Parameters:
#
#      - ZipCode  Codigo postal del cual se requiere buscar la zona
#      
#
#  Returns:
#
#      - ID_zone del ZipCode enviado
#      
#
#   See Also:
#
#
sub get_zone_by_zipcode{
#############################################################################
#############################################################################
	
   	my ($zipCode) = @_;
   	my ($ID_zones) = 0;

   	(!$zipCode and $cses{'shp_zip'}) and ($zipCode = $cses{'shp_zip'});
   	(!$zipCode and $in{'shp_zip'}) and ($zipCode = $in{'shp_zip'});
   	(!$zipCode and $in{'zip'}) and ($zipCode = $in{'zip'});
   	(!$zipCode and $in{'zipcode'}) and ($zipCode = $in{'zipcode'});
   	(length($zipCode) == 4) and ($zipCode = "0$zipCode");
	
	
	my ($sth)=&Do_SQL("SELECT DISTINCT ID_zones FROM sl_zipcodes WHERE ZipCode = '$zipCode' LIMIT 1; ");
	$ID_zones = $sth->fetchrow();
	
	return $ID_zones;
}


#############################################################################
#############################################################################
#   Function: update_order_zone
#
#       Es: Actualiza el ID_zone en base al ID de la orden
#       En: English description if possible
#
#
#    Created on: 05/12/2012  13:20:10
#
#    Author: Cesar Cedillo
#
#    Modifications:
#
#        - Modified on 
#        - Modified on 
#
#   Parameters:
#
#      - ID_orders de la orden que se desea actuaizar el ID_zone
#      
#
#  Returns:
#
#      - 
#      
#
#   See Also:
#
#
sub update_order_zone{
#############################################################################
#############################################################################
	my ($id_orders);
   	($id_orders) = @_;	
	
	my ($sth)=&Do_SQL("SELECT shp_Zip FROM sl_orders WHERE ID_orders = $id_orders; ");
	if (my ($zipCode) = $sth->fetchrow){
		my($ID_zones) = &get_zone_by_zipcode($zipCode);

		# Actualiza ID_zones en sl_orders
		if ($ID_zones and $in{'id_zones'} ne $ID_zones){
			my ($sth) = &Do_SQL("UPDATE sl_orders SET ID_zones = '$ID_zones' WHERE ID_orders = $id_orders; ");	
			&auth_logging('opr_orders_zone_updated',$id_orders);
			$in{'id_zones'} = $ID_zones;
		}
	}
}

sub get_cod_sale_status{
#-----------------------------------------
# Created on: 07/01/09  16:31:42 By  Roberto Barcenas
# Forms Involved: 
# Description : Construye la tabla de COD por cada Chofer(Warehouse Virtual)
# Parameters : 	$id_warehouses, $id_orders_payments
# Last Modified by RB on 06/22/2011 04:31:48 PM : Se modifica para devolver solamente una linea especifica por orden

	
	my ($id_orders) = @_;
	my $strout = '';
	
	my $sth=&Do_SQL("Select Status,Sum(if(KindOfContact='Never',1,0))as Never,Sum(if(KindOfContact='>7 days',1,0))as More_than_7_days,Sum(if(KindOfContact='7 days',1,0))as Seven_days,Sum(if(KindOfContact='2 days',1,0))as Two_days,Sum(if(KindOfContact='1 days',1,0))as One_day,drivers_id
	from(
	SELECT sl_orders.ID_orders,
	if(sl_orders.Status='Processed',if(not isnull(sl_orders_datecod.ID_orders),'Processed-In transit','Processed-To be fulfilled'),sl_orders.Status)as Status,
	count(ID_orders_notes)as NNotes,Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)) as LastTimeOfContact,
	if(isnull(Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time))),'Never',
	if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>7,'>7 days',
	if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>2,'7 days',
	if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>1,'2 days',
	if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>=0,'1 days',0)
	)
	)
	)
	)as KindOfContact,
	datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))as diff,
	IF(sl_orders.ID_warehouses > 0,sl_orders.ID_warehouses, concat(0,'|',group_concat(DISTINCT sl_deliveryschs.ID_warehouses SEPARATOR '|')) )AS drivers_id
	FROM sl_orders
	INNER JOIN sl_deliveryschs ON sl_deliveryschs.Zip = sl_orders.shp_Zip
	LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
	LEFT JOIN sl_orders_datecod on(sl_orders.ID_orders=sl_orders_datecod.ID_orders)
	WHERE sl_orders.shp_type=$cfg{'codshptype'} and Ptype='COD' 
	AND sl_orders.ID_orders = '$id_orders'
	GROUP BY sl_orders.ID_orders
	)as tmp");

	if ($sth->rows() > 0){
	
	  my($status,$never,$more,$seven,$two,$one,$id_warehouses) = $sth->fetchrow();
	  return ($status,$never,$more,$seven,$two,$one,$id_warehouses);
		
	}
	
	return (-1,-1,-1,-1,-1,-1,-1);
}


#############################################################################
#############################################################################
#   Function: cod_sales_execute
#
#       Es: Ejecuta el query que consulta cada warehouse virtual y guarda los datos resultantes en la tabla sl_cod_sales
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - $id_warehouses
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub cod_sales_execute {
#############################################################################
#############################################################################


    my ($id_warehouses) = @_;

    ($id_warehouses) and ($innerWarehouse=' INNER JOIN sl_deliveryschs USE INDEX(Zip) ON sl_deliveryschs.Zip = sl_orders.shp_Zip ') and ($modWarehouse=" AND sl_deliveryschs.ID_warehouses = $id_warehouses ") and ($linkwarehouse = "&id_warehouses=$id_warehouses");

    my $sth=&Do_SQL("Select Status,
    Sum(if(KindOfContact='Never',1,0))as Never,
    Sum(if(KindOfContact='>7 days',1,0))as More_than_7_days,
    Sum(if(KindOfContact='7 days',1,0))as Seven_days,
    Sum(if(KindOfContact='2 days',1,0))as Two_days,
    Sum(if(KindOfContact='1 days',1,0))as One_day
  from(
    SELECT sl_orders.ID_orders,
    if(sl_orders.Status='Processed',if(not isnull(sl_orders_datecod.ID_orders),'Processed-In transit','Processed-To be fulfilled'),sl_orders.Status)as Status,
    count(ID_orders_notes)as NNotes,Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)) as LastTimeOfContact,
    if(isnull(Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time))),'Never',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>7,'>7 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>2,'7 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>1,'2 days',
    if(datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))>=0,'1 days',0)
    )
    )
    )
    )as KindOfContact,
    datediff(Curdate(),Max(concat(sl_orders_notes.Date,' ',sl_orders_notes.Time)))as diff
    FROM sl_orders
    $innerWarehouse
    LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
    LEFT JOIN sl_orders_datecod on(sl_orders.ID_orders=sl_orders_datecod.ID_orders)
    WHERE sl_orders.shp_type=$cfg{'codshptype'} and Ptype='COD' $modWarehouse
    GROUP BY sl_orders.ID_orders
  )as tmp
  GROUP BY Status");

    if($sth->rows() > 0){

      while($rec=$sth->fetchrow_hashref()){

		    &Do_SQL("INSERT INTO sl_cod_sales SET ID_warehouses='".$id_warehouses."', Status='$rec->{'Status'}', More='$rec->{'More_than_7_days'}',Seven='$rec->{'Seven_days'}',Two='$rec->{'Two_days'}',One='$rec->{'One_day'}',Never='$rec->{'Never'}';");
		    print "Warehouse: $id_warehouses\nMore than Seven:$rec->{'More_than_7_days'}\nSeven Days:$rec->{'Seven_days'}\nTwo Days:$rec->{'Two_days'}\nOne Day:$rec->{'One_day'}\nNever:$rec->{'Never'}\n\n";

		  }

    }else{

      print "Warehouse: $id_warehouses\nNo Data...\n\n";

    }

}


sub cod_link_reactivate{
#-----------------------------------------
# Created on: 07/24/09  16:27:34 By  Roberto Barcenas
# Forms Involved: 
# Description : Devuelve un link que permite reactivar las ordenes COD para reenvio
# Parameters : 


	my ($id_orders) = @_;
	my $str = '';
	
	$sth = &Do_SQL("SELECT 
					IF(TInactive IS NULL,0,TInactive)AS TInactive,
					IF(TActive IS NULL,0,TActive)AS TActive 
					FROM sl_orders
					LEFT JOIN (
						SELECT ID_orders,
						SUM(IF(Status='Inactive',1,0)) AS TInactive, 
						SUM(IF(Status='Active',1,0)) AS TActive
						FROM sl_orders_datecod
						WHERE ID_orders = '$id_orders'
						GROUP BY ID_orders
					)AS tmp
					USING(ID_orders)
					WHERE sl_orders.ID_orders = '$id_orders'
					AND sl_orders.Status='Cancelled';");	  							
	
	my($inactive,$active) = $sth->fetchrow();
	
	if($inactive > 0){
		$str = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$id_orders&reactivate=1" onclick="return confirm_continue();"><img src="$va{'imgurl'}/$usr{'pref_style'}/reload.png" title="Reactivate" alt="Reactivate" border="0"></a>|;
	}

	return $str;
}

sub cod_apply_reactivate{
#-----------------------------------------
# Created on: 07/24/09  17:33:40 By  Roberto Barcenas
# Forms Involved: 
# Description : Aplica la reactivacion de una orden COD para permitir que sea reactivada
# Parameters : 	
	
	my ($id_orders) = @_;
	my $ids;
	
	if(&cod_link_reactivate($id_orders) ne ''){
		
		my ($sthp) = &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders = '$id_orders';");
		while(my($idp) = $sthp->fetchrow()){
			$ids .= "$idp,";
			my $sth1 = &Do_SQL("UPDATE sl_orders_products SET ShpDate = NULL ,Tracking = NULL ,ShpProvider = NULL, Cost = 0, DeliveryDate = NULL WHERE ID_orders_products = '$idp';");
			my $sth2 = &Do_SQL("DELETE FROM sl_orders_parts WHERE ID_orders_products = '$idp';"); 
		}

		chop($ids);
		my $validation = &review_order($id_orders);
		my $add_sql = ($validation eq 'OK')? ", Status='Processed'":"";
		my ($sth) = &Do_SQL("UPDATE sl_orders SET ID_warehouses=0 $add_sql WHERE ID_orders = '$id_orders';");
		
		
		&add_order_notes_by_type($id_orders,&trans_txt('cod_reactivated'),"Medium");


		#my ($sth) = &Do_SQL("UPDATE sl_preorders_datecod SET DateCancelled=CURDATE(),Status='Inactive' WHERE ID_preorders=$id_orders AND Status='Active';");
		my ($sth) = &Do_SQL("UPDATE sl_orders_datecod SET DateCancelled=CURDATE(),Status='Inactive' WHERE ID_orders='$id_orders' AND Status='Active';");
		$va{'message'} = &trans_txt('opr_orders_cod_reactivated');

		#Despues de reactivar una orden los registros pasan a estatus Cancelled
		my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status='Cancelled' WHERE ID_orders_products IN ($ids) AND Status = 'In Transit';");

		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

	}
}

sub is_adm_order{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/05/09 17:50:59
# Author: MCC C. Gabriel Varela S.
# Description :   Determina si una orden es o no creada desde el m�dulo de administration.
# Parameters :
# Last Modified on: 08/13/09 13:08:41
# Last Modified by: MCC C. Gabriel Varela S: Se toman en cuenta productos.
# Last Modified on: 08/28/09 15:39:39
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta application follow-up
	my($id_orders)=@_;
	my $sth=&Do_SQL("SELECT IF((( application IN('admin','crm','ecom') ) AND SUM(IF(ID_products like '%000000' AND sl_orders_products.Status IN('Active','Reship'),1,0))>0)  or count(ID_products)=0,1,0)
FROM sl_orders
LEFT JOIN sl_orders_products ON(sl_orders.ID_orders=sl_orders_products.ID_orders)
INNER JOIN admin_users ON (sl_orders.ID_admin_users=admin_users.ID_admin_users)
WHERE sl_orders.ID_orders = '$id_orders'
GROUP BY sl_orders.ID_orders");
	
#	my $sth=&Do_SQL("Select if(application='administration',1,0)
#from sl_orders
#inner join admin_users on (sl_orders.ID_admin_users=admin_users.ID_admin_users)
#where ID_orders=$id_orders;");

	return $sth->fetchrow;
}

sub is_exportation_order{
#-----------------------------------------
# Created on: 08/11/09  11:45:23 By  Roberto Barcenas
# Forms Involved: 
# Description : Determina si una orden es de multiples items para exportacion
# Parameters : 	
	
	my($id_orders)=@_;
	my $sth=&Do_SQL("SELECT
					IF( SUM( IF( Quantity >0 AND RIGHT( ID_products, 6 ) = '000000'
					AND LEFT( Related_ID_products, 1 ) > 0 AND LENGTH(Related_ID_products) = 9, 1, 0 ) ) > 0, 1, 0 ) AS IsExportation	
					FROM sl_orders_products where ID_orders = '$id_orders' AND Status IN('Active','Exchange','Undeliverable','Lost','ReShip');");
	
	return $sth->fetchrow();
}

sub is_services_order{
#-----------------------------------------
# Created on: 07/07/14  11:45:23 By  Arturo Hernandez
# Forms Involved: 
# Description : 
# Parameters : 	

	my($id_orders)=@_;
	my $sth=&Do_SQL("SELECT
					1
					FROM sl_orders_products 
					where ID_orders = '$id_orders' 
					AND (ID_products >= 600000000 AND ID_products < 700000000)
					AND Status IN('Active','Exchange','Undeliverable','Lost','ReShip');");
	$error = 0;
	while($row = $sth->fetchrow()){
		if($row != 1){
			$error++; 
		}
	}
	return $error == 0 ? 1 : 0;

}


#############################################################################
#############################################################################
#   Function: changeto_cod
#
#       Es: Define si una orden es candidata a cambiarse a COD
#       En: 
#
#
#    Created on: *09/02/09*
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *01/19/2011* by _Roberto Barcenas_ : Se agrega posibilidad de cambiar a COD cuando se tiene un pago postdated 
#
#   Parameters:
#
#      - id_orders: ID Order  
#      - y  
#
#  Returns:
#
#       - 1 : La orden es candidata para cambio
#		- 0 : La orden no se puede cambiar 
#
#   See Also:
#
#      <changeto_cod_apply>
#
sub changeto_cod {
#############################################################################
#############################################################################


	my ($id_orders)	=	@_;
	
	my $sth=&Do_SQL("SELECT IF(sl_orders.Status != 'Shipped' AND Ptype!='COD' 
					AND IF(Payments IS NULL,0,Payments) = 0,1,0)AS ChangeCOD
FROM sl_orders 
LEFT JOIN
(
   SELECT ID_orders,
   SUM(IF(CapDate IS NOT NULL AND CapDate!='0000-00-00' AND Captured='Yes' 
   AND Amount > '$cfg{'postdatedfesprice'}',1,0)) AS Payments
   FROM sl_orders_payments WHERE ID_orders = '$id_orders'
   GROUP BY ID_orders
)AS tmp
ON tmp.ID_orders = sl_orders.ID_orders
WHERE sl_orders.ID_orders = $id_orders;");

	return $sth->fetchrow();
	
}


#############################################################################
#############################################################################
#   Function: changeto_cod_apply
#
#       Es: Cambia una orden a tipo de venta COD. Si la orden es TDC y tiene pagos (Postdated Fees), se separa la venta de lo ya pagado y se genera una nueva venta tipo COD con el restante
#       En: 
#
#
#    Created on: *09/02/09* 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *09/23/09* by _Roberto Barcenas_ : Se verifica que la nueva preorden haya sido creada
#        - Modified on *02/01/10* by _Roberto Barcenas_ : Se cambia a orden COD
#        - Modified on *01/19/2011* by _Roberto Barcenas_ : Se agrega posibilidad de cambiar a COD cuando se tiene un pago postdated
#        - Modified on *01/20/2011* by _Roberto Barcenas_ : Se cambio el proceso. La orden original queda como la COD , la nueva orden es la venta del servicio y queda con el id del usuario que la cambio.
#        - Modified on *03/24/2011* by _Roberto Barcenas_ : Para ordenes TDC con Postfecha se agrega nota descriptiva de la venta del servicio con referencia a la orden antigua y y se traspasan los paylogs.
#
#   Parameters:
#
#      - id_orders: ID Order  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <changeto_cod>
#
sub changeto_cod_apply {
#############################################################################
#############################################################################


	my ($id_orders)	=	@_;
	
	$va{'message'} = trans_txt('notappliead');
	if(&changeto_cod($id_orders) == 1){
		
		my ($new_order_txt) = '';	
		##### Calculamos el pago unico
		my $stp = &Do_SQL("SELECT SUM(SalePrice + Shipping + Tax + ShpTax - Discount) FROM sl_orders_products WHERE ID_orders = '$id_orders' AND ID_products != 600000000 + $cfg{'postdatedfeid'} AND Status NOT IN('Order Cancelled','Inactive');");
		my($amount) = $stp->fetchrow();
		$amount	=	0	if	(!$amount	or $amount eq'');
		
		my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders='$id_orders' LIMIT 1");
		$prepa = $sth2->fetchrow_hashref();
		
		
		##########
		########## Order PostDated?
		##########
		
		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Captured='Yes' AND CapDate IS NOT NULL AND CapDate != '' AND CapDate !='0000-00-00' GROUP BY ID_orders;");
		my($amount_paid) = $sth->fetchrow();
				
		if($amount_paid > $cfg{'postdatedfeid'}){
				$va{'message'} = qq|Error: Order have payments captured|;
				return;
		}elsif($amount_paid > 0 and $amount_paid <= $cfg{'postdatedfeid'}){
				
				## Creating New Order
				my($sthor) = &Do_SQL(" SELECT * FROM sl_orders WHERE ID_orders='$id_orders'; ");
				$old_ord = $sthor->fetchrow_hashref();
				my (@dbcols) = ('ID_customers','Address1','Address2','Address3','Urbanization','City','State','Zip','Country','BillingNotes','shp_type','shp_name','shp_Address1','shp_Address2','shp_Address3','shp_Urbanization','shp_City','shp_State','shp_Zip','shp_Country','shp_Notes','ID_pricelevels','question1','answer1','question2','answer2','question3','answer3','question4','answer4','question5','answer5','Ptype','ID_admin_users');
				my ($query) = "";
				for (0..$#dbcols){
					if($old_ord->{$dbcols[$_]}){
						$query .= "$dbcols[$_]='$old_ord->{$dbcols[$_]}',";
					}
				}
				my ($sth_ord) = &Do_SQL("INSERT INTO sl_orders SET $query ID_orders_related='$id_orders',StatusPrd='None',StatusPay='None',Status='New',Date=CURDATE(),Time=CURTIME()");
				$new_id_orders = $sth_ord->{'mysql_insertid'};
				
				## New Order Created?
				if(!$new_id_orders){
						$va{'message'} = trans_txt('notappliead');
						return;
				}
				
				$in{'db'}="sl_orders";
				&auth_logging('order_created', $new_id_orders);
				$new_order_txt = trans_txt('actionapplied') . trans_txt('reports_id_orders') . qq|: <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$new_id_orders">$new_id_orders</a>|;

				## Order / Customer Type
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$new_id_orders';");
				my ($order_type, $ctype) = $sth->fetchrow();

				
				## Updating Products
				my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ID_orders = '$new_id_orders' WHERE ID_orders = '$id_orders' AND ID_products = 600000000 + $cfg{'postdatedfeid'} AND Status='Active' ;");
				## Updating Payments
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET ID_orders = '$new_id_orders' WHERE ID_orders = '$id_orders' AND Captured='Yes' AND CapDate IS NOT NULL AND CapDate != '' AND CapDate !='0000-00-00' AND Amount <= '$cfg{'postdatedfesprice'}' ;");
				## Updating Paylogs
				my ($sth) = &Do_SQL("UPDATE sl_orders_plogs SET ID_orders = '$new_id_orders' WHERE ID_orders = '$id_orders';");
				## Updating Movements
				my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_tableused = '$new_id_orders',ID_admin_users='$usr{'id_admin_users'}' WHERE ID_tableused = '$id_orders' AND tableused='sl_orders' ;");
				
				
				## Closing old order
				my ($sth) = &Do_SQL("UPDATE sl_orders_products SET ID_admin_users='$usr{'id_admin_users'}', PostedDate=CURDATE(),Status=IF(ID_products <> 600000000+$cfg{'postdatedfeid'},'Inactive',Status), ShpDate=IF(ID_products = 600000000+$cfg{'postdatedfeid'},CURDATE(),ShpDate) WHERE ID_orders = $new_id_orders;");
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET ID_admin_users='$usr{'id_admin_users'}', PostedDate=CURDATE(),Status=IF((CapDate IS NULL OR CapDate='0000-00-00') AND (Captured ='No' OR Captured IS NULL OR Captured=''),'Cancelled',Status) WHERE ID_orders = $new_id_orders;");
				my ($sth) = &Do_SQL("UPDATE sl_orders SET ID_admin_users='$usr{'id_admin_users'}', PostedDate=CURDATE(),Status='Shipped',Ptype='Credit-Card',StatusPrd='None',StatusPay='None' WHERE ID_orders = $new_id_orders;");
				
				
				&add_order_notes_by_type($new_id_orders,"PostDated Service Sale From order ($id_orders)","Low");		
				&auth_logging('orders_pdtocod',$id_orders);
				&recalc_totals($new_id_orders);
				
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$new_id_orders',Notes='Service Sale From Old PostDated Order  $id_orders changed to COD',Type='Low',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

				#### Accounting Movements
				my @params = ($new_id_orders);
				&accounting_keypoints('system_posteddate_sale_'. $ctype .'_'. $order_type, \@params );
				
		}
		
		## Inactivating All Payments
		&Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders = '$id_orders' AND (Captured = 'No' OR Captured IS NULL) AND (CapDate IS NULL OR CapDate='0000-00-00');");
		
		## Creating New Payment
		$query_pay='';
		@db_cols = ('PmtField2','Date','Time','ID_admin_users');
		foreach my $column (@db_cols) {
			if($prepa->{$column}){
		  	$query_pay .= " ".$column."='".$prepa->{$column}."',";
		  }
		}
		my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders = '$id_orders' , PmtField1='',PmtField3='',PmtField4='',PmtField5='',Type='COD', Reason='Sale',Amount='$amount', $query_pay Paymentdate=CURDATE(), Status='Approved'");
		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='New',Ptype='COD',shp_type=3,StatusPay='None',StatusPrd='None' WHERE ID_orders = $id_orders;");
		&auth_logging('opr_orders_stNew',$id_orders);
		&status_logging($id_orders,'New');
		$in{'status'} = 'New';

		###### Ingresamos las notas de cambio en Orden y Preorden
		
		&add_order_notes_by_type($id_orders,"Change to COD","Low");		
		&auth_logging('cc_to_cod',$id_orders);
		
		###### Recalculamos la Orden
		&recalc_totals($id_orders);

		$va{'message'} = qq|Regular to COD Order Successfull<br>$new_order_txt|;
		
	}

}


sub is_cc_convertible{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/10/10 17:17:10
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :

	my $sth = &Do_SQL("SELECT count(*) FROM sl_orders WHERE ID_orders='$in{'id_orders'}' AND Ptype!='Credit-Card' AND Status NOT IN ('Shipped','System Error')");
	return $sth->fetchrow;
}


#############################################################################
#############################################################################
#   Function: conver_to_cc
#
#       Es: Convierte una orden de cualquier tipo a CC, intenta realizar el cobro. Si la orden es COD en la calle
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - x  
#      - y  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub conver_to_cc {
#############################################################################
#############################################################################

# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/10/10 17:47:21
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified by RB on 12/24/2010 : Se agrega sl_skus_trans y se busca item por costo para descargar del inventario
# Last Modified by RB on 06/28/2011 11:51:42 AM : Si sltvcyb_sale devuelve Pending(Error con Authcode), se ejecuta de inmediato la captura del pago

	my (@cols) = ('id_orders','amount','notes','pmtfield1','pmtfield2','pmtfield3','month','year','pmtfield5','pmtfield6','paymentdate');
	my $err=0;
	$in{'notes'}="Added from convertion button";
	for my $i(0..$#cols){
		$in{$cols[$i]}=&filter_values($in{$cols[$i]});
		if (!$in{$cols[$i]}){
			$error{$cols[$i]} = &trans_txt('required');
			++$err;
			#&cgierr("$cols[$i]");
		}
	}

	if ($in{'id_orders'}){
		$in{'id_orders'} = int($in{'id_orders'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$in{'id_orders'}' AND Status<>'Shipped' and Ptype!='Credit-Card'");
		my ($matches) = $sth->fetchrow;
		if ($matches>0){
			my ($sth) = &Do_SQL("SELECT ID_customers,OrderNet,Status FROM sl_orders WHERE ID_orders='$in{'id_orders'}' and Ptype!='Credit-Card'");	
			($id_customer,$ordernet,$status) = $sth->fetchrow_array();
			$va{'order_info'} = "($id_customer) " . &load_db_names('sl_customers','ID_customers',$id_customer,'[FirstName] [LastName1] [LastName2]') ."<br>Order : <a href='/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$in{'id_orders'}'>$in{'id_orders'}</a> &nbsp;&nbsp; Status: $status";
		}else{
			$error{'id_orders'} = &trans_txt('invalid');
			++$err;
		}
	}

	if (!$err){
		$in{'id_orders'} = int($in{'id_orders'});
		$in{'notes'} = &filter_values('Converted from COD to CC by using the convertion button');
		$in{'refid'} = &filter_values($in{'refid'});
		$in{'refid'} = '' if !$in{'refid'};
		$in{'pmtfield4'}="$in{'month'}$in{'year'}";
		$in{'amount'} =~	s/\$//; 
		
		#&Do_SQL("START TRANSACTION");
			
		### Create Order from preorder
		my ($rec,$rec_cust,$query,$id_orders,$id_customers,$amount,$idpp,$oldamount);
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' 
							AND (/*$in{'amount'}<=Amount*(1+$cfg{'porcerror'}/100) AND*/ 
							(Captured = 'No' OR Captured IS NULL) AND (CapDate = '0000-00-00' OR CapDate IS NULL) 
							AND $in{'amount'}>=Amount*(1-$cfg{'porcerror'}/100))");

		$rec=$sth->fetchrow_hashref;
		$idpp=$rec->{'ID_orders_payments'};
		$oldamount=$rec->{'Amount'};

		if ($idpp){
			##Insert Note:
			my $querydata = "RefID=$in{'refid'}\nPaid method=COD\n$in{'notes'}\nOrder ID:$in{'id_orders'}";
			
			my ($sth) = &add_order_notes_by_type($in{'id_orders'},"COD to CC. Old amount=".&format_price($oldamount),"Low") if($in{'amount'}>$oldamount*(1+$cfg{'porcerror'}/100));
			
			$in{'db'} = 'sl_orders';

			if($in{'cc'}){
				#borra pago anterior
				#&Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders_payments = $idpp");
				
				#crea pago nuevo con cc
				my $sth=&Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}',Type='Credit-Card',PmtField1='$in{'pmtfield1'}',PmtField2='$in{'pmtfield2'}',PmtField3='$in{'pmtfield3'}',PmtField4='$in{'pmtfield4'}',PmtField5='$in{'pmtfield5'}',PmtField6='$in{'pmtfield6'}',PmtField7='$in{'pmtfield7'}',PmtField8='$in{'refid'}',PmtField9='$in{'pmtfield9'}',Amount=$in{'amount'},Reason='$rec->{'Reason'}',Paymentdate='$in{'paymentdate'}',Status='Approved',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				#Se asigna a $idpp nuevo pago.
				$idpp = $sth->{'mysql_insertid'};
				
				
				#Se determina si se pagó la orden: Mandar a llamar a autorizar o a capturar.
				require ("../../common/apps/cybersubs.cgi");
				my ($status,$msg,$code);
				if(&is_codorder_in_transit($in{'id_orders'})){
					($status,$msg,$code) = &sltvcyb_sale($in{'id_orders'}, $idpp);
					
					if($status ne 'OK' and $msg =~ /^Auth Code/){
					  ($status,$msg,$code) = &sltvcyb_capture($in{'id_orders'}, $idpp);
					}
					
				}else{
					($status,$msg,$code) = &sltvcyb_auth($in{'id_orders'}, $idpp);
				}
				
				if($status eq'OK'){
					&Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders='$in{'id_orders'}' AND ID_orders_payments!=$idpp");
					my ($sthup) = &Do_SQL("UPDATE sl_orders SET Status='Processed',Ptype='Credit-Card' WHERE ID_orders='$in{'id_orders'}'");
					&auth_logging('opr_orders_payments_paid',$in{'id_orders'});
					&auth_logging('opr_orders_stProcessed',$in{'id_orders'});
					&status_logging($in{'id_orders'},'Processed');
					$va{'message'} = "Payment Updated";
					$cod_order_paid =1;
					### Creating PayLog
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$in{'id_orders'}',ID_orders_payments = $idpp,Data='$querydata', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				}else{
					$va{'message'} = "$status\n$msg\n";
					$cod_order_paid =0;
					#Se cancela pago
					my $sth=&Do_SQL("UPDATE sl_orders_payments set Status='Cancelled' where ID_orders_payments=$idpp;");
				}
			}else{
				## Pago dentro del Rango
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET PmtField8='$in{'refid'}',Amount=$in{'amount'},Paymentdate='$in{'date'}',Captured='Yes',Status='Approved',CapDate='$in{'date'}' WHERE ID_orders_payments = $idpp");
				&auth_logging('opr_orders_payments_paid',$in{'id_orders'});
				$va{'message'} = "Payment Updated";
				$cod_order_paid =1;
				### Creating PayLog
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$in{'id_orders'}',ID_orders_payments = $idpp,Data='$querydata', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			}
			&auth_logging('cod_to_cc',$id_orders);
		}else{
			$va{'message'} .= "Invalid Payment Amount";
			$error{'amount'} = &trans_txt('invalid');
			++$err
		}


		if($cod_order_paid and &is_codorder_in_transit($in{'id_orders'})){
			
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders='".$in{'id_orders'}."'  AND Captured!='Yes' AND (CapDate IS NULL OR CapDate='0000-00-00') ;"); 
			my ($sth) = &Do_SQL("SELECT *,ID_customers as ID_customers FROM sl_orders WHERE ID_orders='".$in{'id_orders'}."'");
			while ($pro = $sth->fetchrow_hashref){
				
				
				### INSERT NOTE FROM THIS ORDER.
				
				&add_order_notes_by_type_admin($in{'id_orders'},'COD to CC. cod_to_order','Low');

				$in{'db'}="sl_orders";
				&auth_logging('opr_orders_added',$lastid_ord);
				my ($sthup) = &Do_SQL("UPDATE sl_orders SET Status='Shipped',Ptype='Credit-Card' WHERE ID_orders='$pro->{'ID_orders'}'");
				&auth_logging('opr_orders_updated',$pro->{'ID_orders'});
				&auth_logging('opr_orders_stShipped',$pro->{'ID_orders'});
				&status_logging($pro->{'ID_orders'},'Shipped');

				
				# Salida del inventario
				my ($sth3) = &Do_SQL("SELECT IsSet,sl_orders_products.* FROM sl_orders_products LEFT JOIN sl_skus 
													ON sl_orders_products.ID_products = sl_skus.ID_sku_products
													WHERE ID_orders = '$pro->{'ID_orders'}' AND sl_orders_products.Status='Active';");
													
				while ($prepr = $sth3->fetchrow_hashref){
					
					if(substr($prepr->{'ID_products'},0,1) != '6'){

						#### Descarga del WH Virtual
						if($prepr->{'IsSet'} eq 'Y'){
							### PARTS
							my ($sth4) = &Do_SQL("SELECT ID_sku_products,Cost FROM sl_orders_parts INNER JOIN sl_skus ON sl_orders_parts.ID_parts = sl_skus.ID_products WHERE ID_orders_products = '$prepr->{'ID_orders_products'}' AND LEFT(ID_sku_products,1) != 6 ;");
							while(my($id_products,$cost) = $sth4->fetchrow()){

								$cost=0 if(!$cost);
								#### sl_warehouses_location
								my ($sth) = &Do_SQL("SELECT ID_warehouses_location, Location FROM sl_warehouses_location WHERE ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $id_products AND Quantity > 0 LIMIT 1;");
								my ($idwl,$location) = $sth->fetchrow();
								$location = '00000' if !$location;

								if($idwl > 0){

									my ($sth) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity - 1 WHERE 1 AND ID_warehouses_location = '$idwl' AND ID_warehouses = '$pro->{'ID_warehouses'}'  AND ID_products = $id_products AND Quantity > 0 LIMIT 1;");
									&auth_logging('warehouses_location_updated',$pro->{'ID_warehouses'});
									&sku_logging($id_products, $pro->{'ID_warehouses'},$location,'Sale',$in{'id_orders'},'sl_orders',1);
								}else{
									## There's no SKU Quantity in the Warehouse
									&write_to_list("Bad VWarehouse","orders","3000","",$in{'id_orders'},"sl_orders") if $is_wh;
									&auth_logging('list_added',$sth->{'mysql_insertid'});
									
									
									&add_order_notes_by_type_admin($in{'id_orders'},"VWarehouse Location: $pro->{'ID_warehouses'} - SKU:$id_products","High");
									my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_notes SET ID_warehouses = '$pro->{'ID_warehouses'}', Notes='Bad Quantity for Product:$id_products',Date=CURDATE(), Time=NOW(), ID_admin_users='$usr{'id_admin_users'}';");
									&auth_logging('warehouses_location_note_added',$sth->{'mysql_insertid'});
								}

								#### sl_skus_cost
								my ($sth) = &Do_SQL("SELECT Quantity FROM sl_skus_cost WHERE ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $id_products AND Quantity > 0 AND Cost='$cost';");
								if($sth->fetchrow() > 0){
									my ($sth) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity - 1 WHERE 1 AND   ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $id_products AND Quantity > 0 AND Cost='$cost' ORDER BY Date LIMIT 1;");
									&auth_logging('skus_cost_updated',$pro->{'ID_warehouses'});
								}else{
									my ($sth) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity - 1 WHERE 1 AND   ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $id_products AND Quantity > 0 ORDER BY ABS(ROUND(Cost,2) - ROUND($cost,2)),Date  LIMIT 1;");
									&auth_logging('skus_cost_updated',$pro->{'ID_warehouses'});
								}
								#my ($sth) = &Do_SQL("INSERT INTO sl_skus_trans SET ID_products='$id_products', Type='Sale', ID_trs='$in{'id_orders'}', tbl_name='sl_orders',Quantity=1,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
							}
							#### PRODUCTS
						}else{
							#### sl_warehouses_location
							my ($sth) = &Do_SQL("SELECT ID_warehouses_location,Location FROM sl_warehouses_location WHERE ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $prepr->{'ID_products'} AND Quantity > 0 ;");
							my ($idwl,$location) = $sth->fetchrow();
							$location = '00000' if !$location;

							if($idwl > 0){
									my ($sth) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity - 1 WHERE 1 AND ID_warehouses_location = '$idwl' AND ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $prepr->{'ID_products'} AND Quantity > 0 LIMIT 1;");
									&auth_logging('warehouses_location_updated',$pro->{'ID_warehouses'});
									&sku_logging($prepr->{'ID_products'},$pro->{'ID_warehouses'},$location,'Sale', $in{'id_orders'},'sl_orders',1);
							}else{
									&write_to_list("Bad VWarehouse","orders","3000","",$in{'id_orders'},"sl_orders") if $is_wh;
									&auth_logging('list_added',$sth->{'mysql_insertid'});
									
									my ($sth) = &add_order_notes_by_type_admin($in{'id_orders'},"Bad VWarehouse Location: $pro->{'ID_warehouses'} - Product:$prepr->{'ID_products'}","High") if $is_wh;

									
									my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_notes SET ID_warehouses = '$pro->{'ID_warehouses'}', Notes='Bad Quantity for Product:$prepr->{'ID_products'}',Date=CURDATE(), Time=NOW(), ID_admin_users='$usr{'id_admin_users'}';");
									&auth_logging('warehouses_location_note_added',$sth->{'mysql_insertid'});
							}

							#### sl_skus_cost
							my ($sth) = &Do_SQL("SELECT Quantity FROM sl_skus_cost WHERE ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $prepr->{'ID_products'} AND Quantity > 0 ;");
							if($sth->fetchrow() > 0){
								my ($sth) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = Quantity - 1 WHERE 1 AND   ID_warehouses = '$pro->{'ID_warehouses'}' AND ID_products = $prepr->{'ID_products'} AND Quantity > 0 ORDER BY ABS(ROUND(Cost,2) - ROUND($prepr->{'Cost'},2)),Date LIMIT 1;");
								&auth_logging('skus_cost_updated',$pro->{'ID_warehouses'});
							}
							#my ($sth) = &Do_SQL("INSERT INTO sl_skus_trans SET ID_products='$prepr->{'ID_products'}', Type='Sale', ID_trs='$in{'id_orders'}', tbl_name='sl_orders',Quantity=1,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
						}
					}
				}
			}

			#######
			####### Movimientos de contabilidad
			#######
			my ($order_type, $ctype, $ptype,@params);
			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';");
			($order_type, $ctype) = $sth->fetchrow();


			@params = ($in{'id_orders'}, $idpp, 1);
			### Deposit
			if(!$in{'cc'}){
				$ptype = get_deposit_type($idpp,'');
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );
			}

			### Sale
			&accounting_keypoints('order_cod_delivered', \@params );

		}
	}
	
	if (!$err){
		### Reset Form
		for my $i(0..$#cols){
			#delete($in{$cols[$i]});
		}
	}
	&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

	return;
}


sub retail_to_wholesale{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 16 Sep 2011 12:18:19
# Author: Roberto Barcenas.
# Description : Busca ordenes Retail con mas de 10 productos y los convierte a wholesale
# Parameters

	my $str_out;
	my $mod = $in{'id_orders'} ? " AND ID_orders = '$in{'id_orders'}' " : "";
	$in{'id_orders'} = 0 if !$in{'id_orders'};
	my $query = "SELECT tmp.ID_orders, tmp.Date,tmp2.Tproducts,tmp.Status
			FROM
			(
				SELECT ID_orders,Date,Status
				FROM sl_orders WHERE Status NOT IN('Shipped','Cancelled','Void','System Error') $mod
			)as tmp
			INNER JOIN
			(
				SELECT ID_orders,COUNT(*)AS TProducts
				FROM sl_orders_products WHERE Status='Active' $mod
				GROUP BY ID_orders
				HAVING TProducts > 10 OR $in{'id_orders'} > 0
			)as tmp2
			ON tmp.ID_orders=tmp2.ID_orders
			ORDER BY tmp2.TProducts DESC";


	my $sth = &Do_SQL($query);
	my $total = $sth->rows();

	if($total > 0){

		$str_out .= "Found $total orders to change\n";
		while(my ($id_orders,$date,$nitems,$status) = $sth->fetchrow()){

			$str_out .= "ID_order:$id_orders\n";
			## Agrupamos
			my $sth2 = &Do_SQL("SELECT ID_products,400000000+ID_parts AS ID_parts,SUM(sl_orders_products.Quantity * sl_skus_parts.Qty)AS Quantity,SUM(SalePrice),SUM(Shipping),SUM(Tax),SUM(Discount) FROM sl_orders_products INNER JOIN sl_skus_parts ON RIGHT(sl_orders_products.ID_products,6) = RIGHT(sl_skus_parts.ID_sku_products,6) WHERE ID_orders = '$id_orders' AND Status='Active' GROUP BY ID_products;");

			if($sth2->rows() > 0){

				my $idp=100000000;
				my $xquery = "START TRANSACTION; ";
				while(my($id_products,$id_parts,$qty,$price,$shp,$tax,$dis) = $sth2->fetchrow()){

					## Creamos los inserts nuevos
					$xquery .= "INSERT INTO sl_orders_products SET ID_products='$idp', ID_orders='$id_orders', Related_ID_products='$id_parts', Quantity='$qty', SalePrice='$price', Shipping='$shp', Tax='$tax', Discount='$dis', FP=1, Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users=1;";
					$idp+=1000000;
				}
				$xquery .= "COMMIT;";

				$str_out .= "QueryProd:$xquery\n";
				## Ejecutamos los inserts multiples
				$sth3 = Do_mSQL($xquery);

				if($sth3){

					$str_out .= "Result:Done";
					## Eliminamos los registros pasados.
					my $id_admin_users = &load_name('sl_orders','ID_orders',$id_orders,'ID_admin_users');
					my ($sthf1) = &Do_SQL("DELETE FROM sl_orders_products WHERE ID_orders='$id_orders' AND ID_admin_users != 1");
					my ($sthf2) = &Do_SQL("UPDATE sl_orders_products SET ID_admin_users = '$id_admin_users'  WHERE ID_orders = '$id_orders'; ");
					
					&add_order_notes_by_type_admin($id_orders,"The order was changed to Wholesale due to its multiple products","Low")

					&auth_logging('orders_updated',$id_orders);
				}

			}else{
				$str_out .= "Result:No Products\n";
			}
			$str_out .= "\n";
		}
		&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Retail to Wholesale","$str_out");
	}
}


sub get_cod_table{
#-----------------------------------------
# Created on: 07/27/09  09:51:18 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($id_orders) = @_;
	my $str ='';
	
	$str = qq|<table class=stit cellpadding=0 cellspacing=0 border=0 height=25>
		<td valign=top align=left width=9><img src=/sitimages/aco/1.png></td>
		<td rowspan=2><font class=stit>COD Info</font></td>
		<td valign=top align=right width=9><img src=/sitimages/aco/2.png></td>
		<tr>
		<td valign=bottom align=left width=9><img src=/sitimages/aco/3.png></td>
		<td valign=bottom align=right width=9><img src=/sitimages/aco/4.png></td>
	</table>
    						<table border="0" cellspacing="1" cellpadding="2" width="100%">|;
    						
    						
   $sth=&Do_SQL("SELECT COUNT(*) FROM sl_orders_datecod WHERE ID_orders = '$id_orders';");
   my ($count) = $sth->fetchrow();
   
   if(!$count){
   		$str .=	qq|<tr><td class="gcell_on" align="center">Chofer</td><td class="gcell_on" align="center">D&iacute;as de Entrega</td><td class="gcell_on" align="center">Horario de Servicio</td><td class="gcell_on" align="center">Pronostico en dias</td><td class="gcell_on" align="center">Acepta</td></tr>|;
   		$str .= &get_cod_delivery_dates($in{'shp_zip'});
  }else{
  		$str .=	qq|<tr><td class="gcell_on" align="center">Chofer</td><td class="gcell_on" align="center">D&iacute;as de Entrega</td><td class="gcell_on" align="center">Horario de Servicio</td><td class="gcell_on" align="center">En Tr&aacute;nsito</td><td class="gcell_on" align="center">Pronostico de Entrega</td><td class="gcell_on" align="center">Cancelada</td><td class="gcell_on" align="center">Acepta</td></tr>|;
  		$str .=	&get_cod_history($id_orders);
  }
  
  $str .= qq|</table></fieldset>|;
  		
	return $str;
}

sub get_cod_history{
#-----------------------------------------
# Created on: 07/27/09  10:19:12 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($id_orders)	=	@_;
	$strout = '';

	my ($sth) = &Do_SQL("SELECT DateCOD,DateCancelled,ID_warehouses
			    FROM sl_orders_datecod
			    WHERE ID_orders = '$id_orders' ORDER BY Status,DateCOD;");
												
	my (@c) = split(/,/,$cfg{'srcolors'});											
	while(my ($datecod,$datecancell,$id_warehouses) = $sth->fetchrow()){
		$d = 1 - $d;
	
		my ($sth2) = &Do_SQL("SELECT Name,Delivery_days,Delivery_hours,IF(service_days >0,DATE_ADD('$datecod', INTERVAL service_days DAY),'N/A')
					FROM sl_deliveryschs WHERE ID_warehouses = '$id_warehouses'  AND Zip = '$in{'shp_zip'}';");
		
		if($sth2->rows() == 0){
			my ($sth3) = &Do_SQL("SELECT Name,Delivery_days,Delivery_hours
						FROM sl_deliveryschs WHERE ID_warehouses = '$id_warehouses' LIMIT 1;");
			($codagents,$dates,$hours) = $sth3->fetchrow();										
		}else{
			($codagents,$dates,$hours,$sdays) = $sth2->fetchrow();
		}
		$sdays='- - -'	if $datecancell ne '0000-00-00';
		
		my $codtakes = 'MO';
		$codtakes .= ',Efectivo' if $codagents !~ /ups|fedex|iw/i;
		
		$strout .= '<tr bgcolor="'.$c[$d].'"><td align="left">'.$codagents.'</td>';
		$strout .= '<td align="left">'.$dates.'</td>';
		$strout .= '<td align="left">'.$hours.'</td>';
		$strout .= '<td nowrap style="color:green;">'.$datecod.'</td>';
		$strout .= '<td align="center">'.$sdays.'</td>';
		$strout .= '<td nowrap style="color:red;">'.$datecancell.'</td>';
		$strout .= '<td align="right">'.$codtakes.'</td></tr>';
		
	}
	return $strout;
}


#############################################################################
#############################################################################
#   Function: products_order_vs_product_batch
#
#       Es: Valida el numero de productos en la orden para permitir editar una orden
#       En: Validates the number of products in order to allow editing an order
#
#
#    Created on: 23/01/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve 1 si la ordern se puede editar o 0 si  no se puede
#
#   See Also:
#
#      <>
#
sub products_order_vs_product_batch {
#############################################################################
#############################################################################
	my ($id_orders)	=	@_;
	$id_orders = int($id_orders);
	my $result = 0;
	
	if ($id_orders and $id_orders != 0) {
		
		my ($sth) = &Do_SQL("SELECT group_concat(ID_orders_products) FROM sl_orders_products WHERE ID_orders='$id_orders' GROUP BY ID_orders_products");
		my ($id_orders_products) = $sth->fetchrow_array();

		my $add_sql = ($id_orders_products ne '')? " AND ID_orders_products IN ($id_orders_products)":"";

		my ($sth) = &Do_SQL("SELECT
		IF(tosent > sent OR tprod = 0,1,0)AS Valid
		FROM 
		(
			SELECT 
			SUM(IF(Status NOT IN('Inactive', 'Order Cancelled') AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate = '0000-00-00'),1,0)) AS tosent,
			COUNT(ID_orders_products) AS tprod
			FROM sl_orders_products 
			WHERE ID_orders = '$id_orders'
			AND Status IN ('Active','ReShip', 'Exchange')
			AND SalePrice >= 0
		) AS productsinorder,
		(
			SELECT COUNT(*) AS sent
			FROM sl_warehouses_batches_orders
			WHERE 1 $add_sql
			AND status NOT IN ('Cancelled','Returned','Error')
		) AS productsinbatch");
		($result) = $sth->fetchrow();
	}


	return $result;
}

#############################################################################
#############################################################################
#   Function: export_info_for_invoices
#
#       Es: Exporta los datos de la orden a la tabla cu_invoices
#       En: Export data table order cu_invoices
#
#
#    Created on: 30/01/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on *2015-08-28* by _RB_ : Se quita la restriccion de gasto de envio devuelto en notas de credito
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#      <>
#
sub export_info_for_invoices {
#############################################################################
#############################################################################
	my ($id_orders)	=	@_;
	my ($id_invoices);

	## Adecuacion para CFDI 3.3
	$payment_type = 'PAGO EN UNA SOLA EXHIBICION';
	if($cfg{'cfdi_version'} == 3.3 ){
		$payment_type = $cfg{'cfdi_payment_type_default'};
	}
	## ToDo: Aplicacion de Descuento

	## TMK Orders must be Shipped.
	my $order_status = &load_name('sl_orders','ID_orders',$id_orders,'Status');
	if ($order_status eq 'Shipped' or &check_permissions('orders_toinvoice_not_shipped','','')){

		# Validation: ordered vs invoiced
		my ($sth) = &Do_SQL("SELECT COUNT(*)pend_invoiced
		,(SELECT COUNT(*) FROM sl_orders_products WHERE sl_orders_products.ID_orders = '$id_orders' AND Status NOT IN('Order Cancelled','Inactive'))ordered
		FROM sl_orders_products WHERE sl_orders_products.ID_orders = '$id_orders' AND Status NOT IN('Order Cancelled','Inactive')
		AND ID_orders_products NOT IN (
			SELECT ID_orders_products FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices)  WHERE cu_invoices_lines.ID_orders = '$id_orders' AND cu_invoices.`Status` NOT IN ('Void','Cancelled') AND cu_invoices.invoice_type != 'traslado'
		);	
		");
		my ($pend_invoiced,$prods_ordered) = $sth->fetchrow_array();

		## Already Sent?
		## Se debe bloquear si ya existe previa, siempre y cuando no sea una factura cacelada o si existen elementos por facturar
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) WHERE cu_invoices_lines.ID_orders = '$id_orders' AND cu_invoices.Status NOT IN ('Void','Cancelled') AND cu_invoices.invoice_type != 'traslado' GROUP BY ID_invoices)AS invoices;");
		my $is_invalid_invoice = int($sth->fetchrow_array);
		
		if ($is_invalid_invoice and $pend_invoiced==0){
			return &trans_txt('opr_orders_invoice_already_exists'), "ERROR"; 
		}
		
		if ($prods_ordered==0){
			return &trans_txt('opr_orders_invoice_noitems'), "ERROR";
		}

		## 1) Custom Invoice
		## Definicion del campo payment_method
		## Para IMPORTACIONES y MUFAR este dato debe ser definido con los datos fiscales del cliente
		my $id_customers = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		my ($sth_cuad) = &Do_SQL("SELECT COUNT(*), IFNULL( ID_customers_addresses, 0 ) ID_customers_addresses, Payment_Method FROM cu_customers_addresses WHERE id_customers='$id_customers' AND PrimaryRecord='Yes' LIMIT 1");
		my ($has_fiscal_data, $id_customers_addresses, $payment_method) = $sth_cuad->fetchrow_array;

		my ($sth) = &Do_SQL("SELECT PersonalID, b.gln as gln, c.GLN as glnshp, Code, Alias 
		FROM sl_orders a
		LEFT JOIN sl_customers b USING(ID_customers) 
		LEFT JOIN cu_customers_addresses c ON a.ID_customers_addresses=c.ID_customers_addresses 
		WHERE ID_orders = '$id_orders' ;");
		($VendorID, $gln, $glnshp, $shpcode, $shpalias) = $sth->fetchrow();

		my ($id_customer_generic);
		if($cfg{'validate_customer_payment'}){
			$generate_payment_invoice = &Do_SQL(qq|SELECT GeneratePaymentInvoice FROM cu_customers_addresses WHERE cu_customers_addresses.PrimaryRecord = 'Yes' AND ID_customers = '$id_customers' LIMIT 1|)->fetchrow();
			if(!$generate_payment_invoice){
				$has_fiscal_data = 0;
			}	
		}

		## 2) Generic Invoice
		if(!$has_fiscal_data) {

			#obtengo el tipo de cliente
			my ($sth) = &Do_SQL("SELECT Ptype, Type, shp_Zip, PersonalID FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype, $shp_zip, $VendorID) = $sth->fetchrow();

			#revisar si ese tipo de cliente tiene un parametro con un id definido de customer generico
			if($cfg{'id_customer_generic_'.lc($ctype)} and int($cfg{'id_customer_generic_'.lc($ctype)}) > 0) {
				$id_customer_generic = int($cfg{'id_customer_generic_'.lc($ctype)});
				
				# revisamos si el id es valido 
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE ID_customers = '$id_customer_generic';");
				($is_valid_id_customer) = $sth->fetchrow_array();

			}

		}

		## If custom invoice, change customer_generic for real id_customers
		($id_customers_addresses) ? ($id_customer_generic = $id_customers) : ($id_customer_generic = $id_customer_generic);

		# Obtener datos de Company 
		my ($sth_ci) = &Do_SQL("SELECT * FROM cu_company_legalinfo WHERE PrimaryRecord = 'Yes'");
		$rec_company_legal = $sth_ci->fetchrow_hashref;
		
		my ($sth_cr) = &Do_SQL("SELECT * FROM cu_company_addresses WHERE PrimaryRecord = 'Yes'");
		$rec_company_addr = $sth_cr->fetchrow_hashref;

		## Obtener datos fiscales del cliente
		### Para Cliente solo si es $id_customers_addresses
		#	2.1. Sacar customers_addresses LEFT JOIN legalinfo  - Primary Record para Datos Fiscales
		#	2.2. sacar customers_addresses solo donde el ID = $id_customers_addresses
		if($has_fiscal_data){
			my ($sth_cr) = &Do_SQL("SELECT IF(RFC IS NULL , 'XAXX010101000' , RFC) AS RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
						FROM cu_customers_addresses
						LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
						WHERE ID_customers_addresses = '".$id_customers_addresses."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
		}elsif($is_valid_id_customer) {
			my ($sth_cr) = &Do_SQL("SELECT RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
				FROM cu_customers_addresses
				LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
				WHERE sl_customers.ID_customers = '".$id_customer_generic."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
		}

		## Place Consignment
		my $place_consignment = $rec_company_addr->{'City'}.', '.$rec_company_addr->{'State'};
		my $invoice_type = ($in{'creditnote'})? 'egreso':'ingreso';

		# Detalle de la orden
		my ($sth_order_detail) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders = '$id_orders';");
		$rec_order_detail = $sth_order_detail->fetchrow_hashref;
		
		## Definicion del campo payment_method
		## Para TMK/MOW Efectivo -> Referenced Deposit o COD y Tarjeta de Credito -> Credit-Card
		if ($rec_order_detail->{'Ptype'} eq 'Credit-Card'){
			$payment_method = 'Tarjeta de Credito';
		}
		if ($rec_order_detail->{'Ptype'} eq 'Referenced Deposit'){
			$payment_method = 'Efectivo';
		}
		if ($rec_order_detail->{'Ptype'} eq 'COD'){
			$payment_method = 'Efectivo';
		}
		## Como se requiere la Clave obtenemos su valor
		$sth = &Do_SQL("SELECT sl_vars_config.Code FROM sl_vars_config WHERE sl_vars_config.Command='sat_formadepago' AND sl_vars_config.Subcode='$payment_method';");
		my ($payment_method_code) = $sth->fetchrow();

		if($has_fiscal_data){
			($payment_method_code, $payment_type) = &Do_SQL("SELECT LPAD(cu_customers_addresses.payment_type, 2, '0'), cu_customers_addresses.Payment_Method FROM cu_customers_addresses WHERE  ID_customers_addresses = $rec_custom_info->{'ID_customers_addresses'}")->fetchrow();
		}

		if ($payment_method_code and ($has_fiscal_data or $is_valid_id_customer)) {

			my $id_invoices;
			
			#si es valido entonces grabamos sus datos en cu_invoices
			#pero primero revisamos si ya hay facturas de este cliente

			my $conditions = $rec_order_detail->{'Pterms'};

			my $credit_days = &load_name('sl_terms','Name',$conditions,'CreditDays');

			# Obtener los datos de direccion de envio
			my $has_shipping_data = ($rec_order_detail->{'ID_customers_addresses'} and int($rec_order_detail->{'ID_customers_addresses'}) != 0) ? $rec_order_detail->{'ID_customers_addresses'} : 0;
			if ($has_shipping_data) {
				my ($sth_shipping_data) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers_addresses = '".$rec_order_detail->{'ID_customers_addresses'}."';");
				$rec_shipping_data = $sth_shipping_data->fetchrow_hashref;
			}else{

				# Los Datos de envio deben ser tomados de la orden
				my ($sth_shipping_data) = &Do_SQL("SELECT  
						shp_Address1 as cu_Street
						,  '' as cu_Num
						,  '' as cu_Num2
						,  shp_Urbanization as cu_Urbanization
						,  '' as cu_District
						,  shp_City as cu_City
						,  shp_State as cu_State
						,  shp_Country as cu_Country
						,  shp_Zip as cu_Zip
						FROM sl_orders
						WHERE id_orders = '".$rec_order_detail->{'ID_orders'}."';");
				$rec_shipping_data = $sth_shipping_data->fetchrow_hashref;

				$add_sql_id_orders_alias_date = "ID_orders_alias_date=CURDATE(),";
			}

			# Datos de pago
			my $cpay = &load_name('sl_orders_payments','ID_orders',$id_orders,'PmtField3');
			($cpay) ? ($cpay = substr($cpay,-4)) : ($cpay = '');

			## Se valida si el cliente cuenta con la informacion de Cuenta Bancaria
			## Solicitan que se force si viene vacion al texto 'NO IDENTIFICADO'
			my $sth_digits = &Do_SQL("SELECT cu_customers_addresses.Account_Number FROM cu_customers_addresses WHERE cu_customers_addresses.ID_customers =	".$id_customers." AND cu_customers_addresses.PrimaryRecord='yes';");
			my ($account_number) = $sth_digits->fetchrow_array();
			$cpay = ($cpay eq '' and $account_number ne '')? substr($account_number,-4) : $cpay;
			$cpay = ($cpay eq '')? 'NO IDENTIFICADO' : $cpay;

			# Detalle de ultima factura
			my ($sth_last_invoice) = &Do_SQL("SELECT ID_invoices FROM cu_invoices WHERE ID_customers = '".$id_customer_generic."' ORDER BY ID_invoices DESC LIMIT 1;");
			$rec_last_invoice = $sth_last_invoice->fetchrow_hashref;
			

			my ($id_invoices);
			if (int($rec_last_invoice->{'ID_invoices'}) > 0) {				
				#Obtiene el tipo de moneda que corresponda al cliente

				my $order_currency = &load_name('sl_customers','ID_customers',$id_customers,'Currency');
				if(!$order_currency){
					$order_currency = 'MXP';
					$exchangerate = 1;
				}else{
					my $sth= &Do_SQL("select exchange_rate from sl_exchangerates where Currency='$order_currency' AND Date_exchange_rate=CURDATE()");	
					$exchangerate = $sth->fetchrow;

					$exchangerate = 1 if($order_currency eq $cfg{'acc_default_currency'});
					if ($order_currency eq 'US$'){
						$order_currency = 'USD';
					}elsif ($order_currency eq 'EU$'){
						$order_currency = 'EUR';
					}elsif ($order_currency eq 'CO$'){
						$order_currency = 'COLP';
					}else {
						$order_currency = 'MXP';
					}

				}

				if ($exchangerate eq ''){
					return &trans_txt('exchangerate_not_found'), "ERROR";
				}

				# Copiar datos de ultima factura
				$previous_invoice = &Do_SQL("SELECT ID_customers, payment_digits, total_taxes_detained, total_taxes_transfered, expediter_fcode, expediter_fname, expediter_fregimen, expediter_faddress_street, expediter_faddress_num, expediter_faddress_num2,  expediter_faddress_urbanization,  expediter_faddress_district,  expediter_faddress_city,  expediter_faddress_state, expediter_faddress_country, expediter_faddress_zipcode, expediter_address_street, expediter_address_num,  expediter_address_num2,  expediter_address_urbanization,  expediter_address_district,  expediter_address_city, expediter_address_state,  expediter_address_country,  expediter_address_zipcode,  customer_fcode,  customer_fname,  customer_address_street, customer_address_num,  customer_address_num2,  customer_address_urbanization,  customer_address_district,  customer_address_city, customer_address_state,  customer_address_country,  customer_address_zipcode,  xml_cfd,  xml_cfdi, xml_addenda,  uuid,  original_string, related_ID_invoices FROM cu_invoices WHERE ID_customers = '$id_customer_generic' ORDER BY date DESC LIMIT 1");
				my ($prv_ID_customers,$prv_payment_digits,$prv_total_taxes_detained,$prv_total_taxes_transfered,$prv_expediter_fcode,$prv_expediter_fname,$prv_expediter_fregimen,$prv_expediter_faddress_street,$prv_expediter_faddress_num,$prv_expediter_faddress_num2,$prv_expediter_faddress_urbanization,$prv_expediter_faddress_district,$prv_expediter_faddress_city,$prv_expediter_faddress_state,$prv_expediter_faddress_country,$prv_expediter_faddress_zipcode,$prv_expediter_address_street,$prv_expediter_address_num,$prv_expediter_address_num2,$prv_expediter_address_urbanization,$prv_expediter_address_district,$prv_expediter_address_city,$prv_expediter_address_state,$prv_expediter_address_country,$prv_expediter_address_zipcode,$prv_customer_fcode,$prv_customer_fname,$prv_customer_address_street,$prv_customer_address_num,$prv_customer_address_num2,$prv_customer_address_urbanization,$prv_customer_address_district,$prv_customer_address_city,$prv_customer_address_state,$prv_customer_address_country,$prv_customer_address_zipcode,$prv_xml_cfd,$prv_xml_cfdi,$prv_xml_addenda,$prv_uuid,$prv_original_string,$prv_related_ID_invoices) = $previous_invoice->fetchrow_array();
				
				$sth_invoice = &Do_SQL("
				INSERT INTO cu_invoices (ID_invoices,  ID_customers,    doc_date,  payment_type,  payment_method, payment_digits,  invoice_net,  invoice_total,  discount,  total_taxes_detained,  total_taxes_transfered,  currency,  currency_exchange,  invoice_type,  place_consignment,  expediter_fcode,  expediter_fname,  expediter_fregimen,  expediter_faddress_street,  expediter_faddress_num,  expediter_faddress_num2,  expediter_faddress_urbanization,  expediter_faddress_district,  expediter_faddress_city,  expediter_faddress_state,  expediter_faddress_country,  expediter_faddress_zipcode,  expediter_address_street,  expediter_address_num,  expediter_address_num2,  expediter_address_urbanization,  expediter_address_district,  expediter_address_city,  expediter_address_state,  expediter_address_country,  expediter_address_zipcode,  customer_fcode,  customer_fname,  customer_address_street,  customer_address_num,  customer_address_num2,  customer_address_urbanization,  customer_address_district,  customer_address_city,  customer_address_state,  customer_address_country,  customer_address_zipcode, customer_shpaddress_code, customer_shpaddress_alias, xml_cfd,  xml_cfdi,  xml_addenda,  uuid, related_ID_invoices,  ID_orders_alias,  Status, VendorID, customer_address_gln, customer_shpaddress_gln,  Date,  Time,  ID_admin_users, credit_days, conditions)
				values (NULL, '".$prv_ID_customers."',NOW(),'$payment_type','".$payment_method_code."','".$prv_payment_digits."','0.00','0.00','".$rec_order_detail->{'OrderDisc'}."','".$prv_total_taxes_detained."','".$prv_total_taxes_transfered."','$order_currency','$exchangerate','".$invoice_type."','".$place_consignment."','".$prv_expediter_fcode."','".$prv_expediter_fname."','".$prv_expediter_fregimen."','".$prv_expediter_faddress_street."','".$prv_expediter_faddress_num."','".$prv_expediter_faddress_num2."','".$prv_expediter_faddress_urbanization."','".$prv_expediter_faddress_district."','".$prv_expediter_faddress_city."','".&filter_values($rec_company_addr->{'State'})."','".$prv_expediter_faddress_country."','".$prv_expediter_faddress_zipcode."','".$prv_expediter_address_street."','".$prv_expediter_address_num."','".$prv_expediter_address_num2."','".$prv_expediter_address_urbanization."','".$prv_expediter_address_district."','".$prv_expediter_address_city."','".$prv_expediter_address_state."','".$prv_expediter_address_country."','".$prv_expediter_address_zipcode."','".$prv_customer_fcode."','".&filter_values($prv_customer_fname)."','".$prv_customer_address_street."','".$prv_customer_address_num."','".$prv_customer_address_num2."','".$prv_customer_address_urbanization."','".$prv_customer_address_district."','".$prv_customer_address_city."','".$prv_customer_address_state."','".$prv_customer_address_country."','".$prv_customer_address_zipcode."','".$shpcode."','".$shpalias."','".$prv_xml_cfd."','".$prv_xml_cfdi."','".$prv_xml_addenda."','".$prv_uuid."','".$prv_related_ID_invoices."','".$rec_order_detail->{'ID_orders_alias'}."','New','".$VendorID."','".$gln."','".$glnshp."',CURDATE(),CURTIME(), '".$usr{'id_admin_users'}."','".$credit_days."','".$conditions."');");
				$id_invoices = $sth_invoice->{'mysql_insertid'};


				## Especifico: Actualizar campos especificos de direccion de envio
				if ($has_shipping_data or $is_valid_id_customer){
					#UPDATE cu_invoices con datos de $rec_company
					&Do_SQL("UPDATE cu_invoices SET 
			        expediter_fcode = '".&filter_values($rec_company_legal->{'RFC'})."',
					expediter_fname = '".&filter_values($rec_company_legal->{'Name'})."',
					expediter_fregimen = '".$rec_company_legal->{'Regime'}."',
					expediter_faddress_street = '".&filter_values($rec_company_addr->{'Street'})."', 
					expediter_faddress_num = '".&filter_values($rec_company_addr->{'Num'})."', 
					expediter_faddress_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
					expediter_faddress_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
					expediter_faddress_district = '".&filter_values($rec_company_addr->{'District'})."', 
					expediter_faddress_city = '".&filter_values($rec_company_addr->{'City'})."', 
					expediter_faddress_state = '".&filter_values($rec_company_addr->{'State'})."', 
					expediter_faddress_country = '".&filter_values($rec_company_addr->{'Country'})."', 
					expediter_faddress_zipcode = '$rec_company_addr->{'Zip'}', 
					expediter_address_street = '".&filter_values($rec_company_addr->{'Street'})."', 
					expediter_address_num = '".&filter_values($rec_company_addr->{'Num'})."', 
					expediter_address_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
					expediter_address_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
					expediter_address_district = '".&filter_values($rec_company_addr->{'District'})."', 
					expediter_address_city = '".&filter_values($rec_company_addr->{'City'})."', 
					expediter_address_state = '".&filter_values($rec_company_addr->{'State'})."', 
					expediter_address_country = '".&filter_values($rec_company_addr->{'Country'})."', 
					expediter_address_zipcode = '$rec_company_addr->{'Zip'}', 							
					
					customer_fcode = '".&filter_values($rec_custom_info->{'RFC'})."', 
					customer_fname = '".&filter_values($rec_custom_info->{'lname'})."', 
					customer_address_street = '".&filter_values($rec_custom_info->{'cu_Street'})."',
					customer_address_num = '".&filter_values($rec_custom_info->{'cu_Num'})."',
					customer_address_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."',
					customer_address_urbanization = '".&filter_values($rec_custom_info->{'Urbanization'})."',
					customer_address_district = '".&filter_values($rec_custom_info->{'cu_District'})."',
					customer_address_city = '".&filter_values($rec_custom_info->{'City'})."', 
					customer_address_state = '".&filter_values($rec_custom_info->{'State'})."', 
					customer_address_country = '".&filter_values($rec_custom_info->{'Country'})."', 
					customer_address_zipcode = '$rec_custom_info->{'Zip'}', 
					
					use_cfdi = '$rec_custom_info->{'Use_Cfdi_invoice'}',

					customer_shpaddress_street = '".&filter_values($rec_shipping_data->{'cu_Street'})."', 
					customer_shpaddress_num	= '".&filter_values($rec_shipping_data->{'cu_Num'})."', 
					customer_shpaddress_num2 = '".&filter_values($rec_shipping_data->{'cu_Num2'})."', 
					customer_shpaddress_urbanization = '".&filter_values($rec_shipping_data->{'cu_Urbanization'})."', 
					customer_shpaddress_district = '".&filter_values($rec_shipping_data->{'cu_District'})."', 
					customer_shpaddress_city = '".&filter_values($rec_shipping_data->{'cu_City'})."', 
					customer_shpaddress_state = '".&filter_values($rec_shipping_data->{'cu_State'})."', 
					customer_shpaddress_country	= '".&filter_values($rec_shipping_data->{'cu_Country'})."', 
					customer_shpaddress_zipcode	= '$rec_shipping_data->{'cu_Zip'}',
					payment_digits = '$cpay'
			        WHERE ID_invoices = '$id_invoices' LIMIT 1;");

				}

			}else {
				# Factura nueva

				# Datos del Currency
				my $order_currency = &load_name('sl_customers','ID_customers',$id_customers,'Currency');
				if(!$order_currency){
					$order_currency = 'MXP';
					$exchangerate = 1;
				}else{
					#Obtiene tipo de cambio peso/dolar
					my $sth= &Do_SQL("select exchange_rate from sl_exchangerates where Currency='$order_currency' AND  Date_exchange_rate=CURDATE()");	
					$exchangerate = $sth->fetchrow;
						
					$exchangerate = 1 if($order_currency eq $cfg{'acc_default_currency'});
					if ($order_currency eq 'US$'){
						$order_currency = 'USD';
					}elsif ($order_currency eq 'EU$'){
						$order_currency = 'EUR';
					}elsif ($order_currency eq 'CO$'){
						$order_currency = 'COLP';
						$order_currency = 'MXP';
					}

				}

				if ($exchangerate eq ''){
					return &trans_txt('exchangerate_not_found'), "ERROR";
				}
				
				#$order_currency = 'MXP' if ($id_customer_generic);
				my $invoice_type = ($in{'creditnote'})? 'egreso':'ingreso';
				my $use_cfdi = ($in{'creditnote'}) ? $rec_custom_info->{'Use_Cfdi_credit'} : $rec_custom_info->{'Use_Cfdi_invoice'};
				## ToDo: Hacer nuevo INSERT con datos especificos
				$sth_invoice = &Do_SQL("INSERT INTO cu_invoices SET 
				ID_customers = '".$in{'id_customers'}."',
				expediter_fcode = '".&filter_values($rec_company_legal->{'RFC'})."',
				expediter_fname = '".&filter_values($rec_company_legal->{'Name'})."',
				expediter_fregimen = '".$rec_company_legal->{'Regime'}."',    
				ID_orders_alias	= '".&filter_values($in{'id_orders_alias'})."',
				$add_sql_id_orders_alias_date
				payment_method = '".$payment_method_code."',
				discount = '".$rec_order_detail->{'OrderDisc'}."',
				invoice_net = '00.00',  
				invoice_total = '00.00',
				doc_date =  NOW() ,
				currency = '".$order_currency."',
				currency_exchange = '".$exchangerate."',
				credit_days = '".$credit_days."',
				invoice_type = '".$invoice_type."',
				use_cfdi = '$use_cfdi',
				place_consignment = '".&filter_values($place_consignment)."',
				expediter_faddress_street = '".&filter_values($rec_company_addr->{'Street'})."', 
				expediter_faddress_num  = '".&filter_values($rec_company_addr->{'Num'})."', 
				expediter_faddress_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
				expediter_faddress_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
				expediter_faddress_district = '".&filter_values($rec_company_addr->{'District'})."', 
				expediter_faddress_city = '".&filter_values($rec_company_addr->{'City'})."', 
				expediter_faddress_state = '".&filter_values($rec_company_addr->{'State'})."', 
				expediter_faddress_country = '".&filter_values($rec_company_addr->{'Country'})."', 
				expediter_faddress_zipcode = '".$rec_company_addr->{'Zip'}."', 
				expediter_address_street = '".&filter_values($rec_company_addr->{'Street'})."', 
				expediter_address_num = '".&filter_values($rec_company_addr->{'Num'})."', 
				expediter_address_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
				expediter_address_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
				expediter_address_district = '".&filter_values($rec_company_addr->{'District'})."', 
				expediter_address_city = '".&filter_values($rec_company_addr->{'City'})."', 
				expediter_address_state = '".&filter_values($rec_company_addr->{'State'})."', 
				expediter_address_country = '".&filter_values($rec_company_addr->{'Country'})."', 
				expediter_address_zipcode = '".$rec_company_addr->{'Zip'}."', 						
				
				customer_fcode = '".&filter_values($rec_custom_info->{'RFC'})."', 
				customer_fname = '".&filter_values($rec_custom_info->{'lname'})."', 
				customer_address_street = '".&filter_values($rec_custom_info->{'cu_Street'})."',
				customer_address_num = '".&filter_values($rec_custom_info->{'cu_Num'})."',
				customer_address_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."',
				customer_address_urbanization = '".&filter_values($rec_custom_info->{'Urbanization'})."',
				customer_address_district = '".&filter_values($rec_custom_info->{'cu_District'})."',
				customer_address_city = '".&filter_values($rec_custom_info->{'City'})."', 
				customer_address_state = '".&filter_values($rec_custom_info->{'State'})."', 
				customer_address_country = '".&filter_values($rec_custom_info->{'Country'})."', 
				customer_address_zipcode = '$rec_custom_info->{'Zip'}', 

				customer_shpaddress_code = '".&filter_values($shpcode)."',
				customer_shpaddress_alias = '".&filter_values($shpalias)."',

				customer_shpaddress_street = '".&filter_values($rec_custom_info->{'cu_Street'})."', 
				customer_shpaddress_num	= '".&filter_values($rec_custom_info->{'cu_Num'})."', 
				customer_shpaddress_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."', 
				customer_shpaddress_urbanization = '".&filter_values($rec_custom_info->{'cu_Urbanization'})."', 
				customer_shpaddress_district = '".&filter_values($rec_custom_info->{'cu_District'})."', 
				customer_shpaddress_city = '".&filter_values($rec_custom_info->{'cu_City'})."', 
				customer_shpaddress_state = '".&filter_values($rec_custom_info->{'cu_State'})."', 
				customer_shpaddress_country = '".&filter_values($rec_custom_info->{'cu_Country'})."', 
				customer_shpaddress_zipcode	= '".$rec_custom_info->{'cu_Zip'}."',
				
				payment_digits = '".$cpay."',
				conditions = '".&filter_values($conditions)."',
				payment_type = '$payment_type',
				STATUS = 'New' , 
				VendorID = '".$VendorID."',
				customer_address_gln='".$gln."', 
				customer_shpaddress_gln='".$glnshp."',
				DATE = CURDATE(), TIME = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."' ");
				$id_invoices = $sth_invoice->{'mysql_insertid'};

				## Especifico: Actualizar campos especificos de direccion de envio
				if (($has_shipping_data or $is_valid_id_customer) and $id_invoices){
					&Do_SQL("UPDATE cu_invoices SET
					customer_shpaddress_street = '$rec_shipping_data->{'cu_Street'}', 
					customer_shpaddress_num	= '$rec_shipping_data->{'cu_Num'}', 
					customer_shpaddress_num2 = '$rec_shipping_data->{'cu_Num2'}', 
					customer_shpaddress_urbanization = '$rec_shipping_data->{'cu_Urbanization'}', 
					customer_shpaddress_district = '$rec_shipping_data->{'cu_District'}', 
					customer_shpaddress_city = '$rec_shipping_data->{'cu_City'}', 
					customer_shpaddress_state = '$rec_shipping_data->{'cu_State'}', 
					customer_shpaddress_country	= '$rec_shipping_data->{'cu_Country'}', 
					customer_shpaddress_zipcode	= '$rec_shipping_data->{'cu_Zip'}'
			        WHERE ID_invoices = '".$id_invoices."' LIMIT 1;");
				}

			}

			if ($id_invoices) {
				## En esta parte vamos agregar una validacion solo lineas que no hayan sido facturadas		
				# Por cada producto agregamos una registro en cu_invoices_line
				# 'Active','Exchange','Returned','Undeliverable','Order Cancelled','Inactive','Lost','ReShip'
				

				###
				### Buscamos fecha de ultima devolucion para agregar validacion
				### 
				my ($sth) = &Do_SQL("SELECT DATE( IF(PostedDate IS NOT NULL AND PostedDate <> '0000-00-00',PostedDate,Date) ) FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Status = 'Returned' AND SalePrice < 0 AND LEFT(ID_products,1) = 8 ORDER BY PostedDate DESC LIMIT 1;");
				my ($last_return_date) = $sth->fetchrow();
				
				my $add_sql = ($in{'creditnote'})? ' AND SalePrice < 0 ':'';
				$add_sql .= "AND IF(sl_orders_products.PostedDate IS NOT NULL AND sl_orders_products.PostedDate <> '0000-00-00', DATE(sl_orders_products.PostedDate) >= '". $last_return_date ."', DATE(sl_orders_products.Date) >= '". $last_return_date ."')" if $last_return_date;

				my ($sth_lines) = &Do_SQL("SELECT ID_orders_products, Quantity, SalePrice, Tax, Tax_percent, ShpTax, Shipping, sl_orders_products.Discount as Discount,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products
					, sl_skus.ID_sku_products AS ID_sku
					, if(sl_customers_parts.sku_customers is null or sl_customers_parts.sku_customers='', sl_skus.UPC,sl_customers_parts.sku_customers) AS ID_sku_alias
					, sl_skus.UPC as UPC
					, sl_customers_parts.size as size
					, sl_customers_parts.packing_type as packing_type
					, sl_customers_parts.packing_unit as packing_unit
					, sl_orders_products.Cost Cost
				FROM sl_orders
					LEFT JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
					LEFT JOIN sl_customers_parts ON sl_customers_parts.ID_parts=SUBSTR(sl_orders_products.Related_ID_products,2,8)*1 AND sl_customers_parts.ID_customers=sl_orders.ID_customers
					LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_orders_products.Related_ID_products
				WHERE sl_orders.ID_orders = '$id_orders' 
					AND sl_orders_products.Status IN('Active','Exchange','Returned') 
					AND sl_orders_products.ID_products NOT LIKE('8%')
					$add_sql
					AND ID_orders_products NOT IN (
						SELECT ID_orders_products FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices)  WHERE cu_invoices_lines.ID_orders = '$id_orders' AND cu_invoices.`Status` NOT IN ('Void','Cancelled') AND cu_invoices.invoice_type != 'traslado'
					) 
				GROUP BY ID_orders_products;");
				my $total_net = 0;
				my $total_tax = 0;
				my $total_discount = 0;			
				my $total = 0;
				my $total_shipping = 0;
				my $total_shipping_tax = 0;

				while(my $rec=$sth_lines->fetchrow_hashref) {

					## ToDo: Comparar ID_products
					#	1) Tipo Distribuidor: ID_products=100000001 + Related_ID_products = 4000001029 - sacar datos de sl_parts
					#	2) Tipo Servicio: 600001001 - sacar datos de sl_services
					#	3) Tipo Producto: 100123456 - sacar datos de sl_products
					my ($idp,$link_ts,$sku,$packing_type);

					if (substr($rec->{'ID_products'},0,1) == 6){				
						#Services
						$link_ts = "mer_services";
						$idp = $rec->{'ID_products'}-600000000;
						$va{'Name'}	= &load_name("sl_services","ID_services",$idp,"Name");
						$rec->{'ID_sku'} = $rec->{'ID_products'};
						
					}elsif (substr($rec->{'ID_products'},0,1) == 4){
						#Skus
						$idp=$rec->{'ID_products'}-400000000;
						$link_ts 	= "mer_parts";
						$va{'Name'} = &load_name("sl_parts","ID_parts",$idp,"Name");
						$va{'Model'} = &load_name("sl_parts","ID_parts",$idp,"Model");
					
					}else{
						#Products
						$idp = substr($rec->{'ID_products'},3,9);
						$link_ts = "mer_products";
						$va{'Name'}	= &load_name("sl_products","ID_products",$idp,"Name");
						$va{'Model'} = &load_name("sl_products","ID_products",$idp,"Model");
						$rec->{'ID_sku'} = $rec->{'ID_products'};
					}

					if ($cfg{'customers_parts_use'} and $cfg{'customers_parts_use'}==1) {
						my ($sth) = &Do_SQL("SELECT sku_customers, packing_type FROM sl_customers_parts WHERE ID_customers = '$in{'id_customers'}' AND ID_parts = '$idp';");
						($sku, $packing_type) = $sth->fetchrow();
					}
					$sku = (!$sku)? $rec->{'ID_products'} : $sku;
					$packing_type = (!$packing_type)? &trans_txt('invoices_measuring_unit') : $packing_type;

					$line++;
					$rec->{'SalePrice'} = ($rec->{'SalePrice'}*-1) if($rec->{'SalePrice'} < 0);
					$rec->{'Tax'} = ($rec->{'Tax'}*-1) if($rec->{'Tax'} < 0);
					$rec->{'Quantity'} = ($rec->{'Quantity'}*-1) if($rec->{'Quantity'} < 0);
					my $amount = $rec->{'SalePrice'};
					$rec->{'Tax_percent'} = 0 if (!$rec->{'Tax_percent'});
					
					
					$add_sql = ($rec->{'SalePrice'} == 0)? "`tax`='0',`tax_rate`='0'," : "`tax`='".$rec->{'Tax'}."',`tax_rate`='".$rec->{'Tax_percent'}."',";
					&Do_SQL("INSERT INTO cu_invoices_lines SET 
						`ID_orders`='$id_orders',
						`ID_orders_products`='".$rec->{'ID_orders_products'}."',
						`ID_invoices`='$id_invoices',  
						`line_num`='$line',  
						`quantity`='".$rec->{'Quantity'}."',  
						`measuring_unit`='".$packing_type."',
						`description`='".$va{'Name'}."',
						`unit_price`='".($rec->{'SalePrice'}/$rec->{'Quantity'})."',  
						`amount`='".$amount."',
						$add_sql
						`discount`='".$rec->{'Discount'}."',
						`ID_sku`='".$rec->{'ID_sku'}."',
						`ID_sku_alias`='".$rec->{'ID_sku_alias'}."',
						`UPC`='".$rec->{'UPC'}."',
						`size`='".$rec->{'size'}."',
						`packing_type`='".$rec->{'packing_type'}."',
						`packing_unit`='".$rec->{'packing_unit'}."',
						`Date`=CURDATE(),  
						`Time`=CURTIME(),
						Cost = '$rec->{'Cost'}' ,
						`ID_admin_users`='".$usr{'id_admin_users'}."' ");
						

					$total_shipping += $rec->{'Shipping'};
					$total_shipping_tax += $rec->{'ShpTax'};
					$total_net += $rec->{'Shipping'};
					$total_tax += $rec->{'ShpTax'};
					$total_net += $amount;
					$total_tax += $rec->{'Tax'};
					$total_discount += $rec->{'Discount'};
					
				}
				##calcular el total de la orden
				$total = $total_net + $total_tax - $total_discount;

				#Se tiene que insertar siempre la primer linea con los datos de SHIPPING
				# #calculo el tax utilizado en shipping
				if ($total_shipping > 0) { # and !$in{'creditnote'} se quita esta restriccion, parece que no es necesaria
					# my ($tax_shipping_percent) = &calculate_taxes($shp_zip, 0, 0, 0);
					# $tax_shipping_percent = 0 if (!$tax_shipping_percent);
					my ($tax_shipping_percent) = ($cfg{'shptax_percent_default'})?$cfg{'shptax_percent_default'}:'0';
					my ($add_id_sku) = ($cfg{'ID_shipping_service'})? qq| `ID_sku`="|.(600000000+int($cfg{'ID_shipping_service'})).qq|",| : '';

					&Do_SQL("INSERT INTO cu_invoices_lines SET 
					`ID_orders`='$id_orders',
					`ID_invoices`=$id_invoices,  
					`line_num`=1,  
					`quantity`=1,  
					`measuring_unit`='".&trans_txt('invoices_measuring_unit')."',
					`description`='".&trans_txt('invoices_shipping')."',
					`unit_price`=".$total_shipping.",
					`amount`=".$total_shipping.",
					`tax`=".$total_shipping_tax.",
					`tax_rate`=".$tax_shipping_percent.",
					$add_id_sku
					`Date`=CURDATE(),  
					`Time`=CURTIME(),  
					`ID_admin_users`='".$usr{'id_admin_users'}."'
					");	
				}

				&Do_SQL("UPDATE cu_invoices SET invoice_net = '$total_net', total_taxes_transfered = '$total_tax', invoice_total = '$total', discount = '$total_discount' WHERE `ID_invoices`=$id_invoices");			

				## Nota + Log
				
				&add_order_notes_by_type($id_orders,&trans_txt('opr_orders_invoice_added').": $id_invoices","Low");

				&auth_logging('opr_orders_invoice_added',$id_orders);
				if($invoice_type eq 'ingreso'){
					&payment_logging(0, $id_customers, 'In', $total, 'cu_invoices', $id_invoices, 0);
				}

				$va{'message'} = &trans_txt('opr_orders_invoice_added') .":$id_invoices";

				return ( &trans_txt('opr_orders_invoice_added') .": $id_invoices", "OK", $id_invoices );

			}else {
				return ( &trans_txt('invoices_error_generating'), "ERROR", 0 );
			}

		}else {
			return ( &trans_txt('invoices_cust_data_not_found'), "ERROR", 0 );
		}
	}else{
		return ( &trans_txt('invoices_order_not_shipped'), "ERROR", 0 );
	}
}


#############################################################################
#############################################################################
#   Function: data_customers_address
#
#       Es: Genera un select con los distintos datos de envio del cliente
#       En: Generates a select with individual customer data costs
#
#
#    Created on: 14/02/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 03/04/2013 by Ale Diaz : Se condiciona campo de custom adresses para add y edit
#
#   Parameters:
#
#      - id_customers_address
#
#  Returns:
#
#      Options for Select of customer address
#
#   See Also:
#
#      <>
#
sub data_customers_address {
# --------------------------------------------------------
	my $output;
	if ($in{'add'} or $in{'edit'} or $in{'modify'}) {
		$output = &build_page('func:orders_custom_addresses.html');
	}

	if (int($in{'id_customers_addresses'}) > 0 ) {

		my ($sth) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers_addresses='".int($in{'id_customers_address'})."' AND Status = 'Active' ORDER BY Code, Alias;");
		while ($rec = $sth->fetchrow_hashref){
			$output .= "<option value='$rec->{'ID_customers_address'}'>$rec->{'Code'} - $rec->{'Alias'} $rec->{'City'}, $rec->{'State'}</option>\n";
			$in{'shp_address1'} = $rec->{'Address1'};
			$in{'shp_address2'} = $rec->{'Address2'};
			$in{'shp_address3'} = $rec->{'Address3'};
			$in{'shp_urbanization'} = $rec->{'Urbanization'};
			$in{'shp_city'} = $rec->{'City'};
			$in{'shp_state'} = $rec->{'State'};
			$in{'shp_country'} = $rec->{'Country'};
			$in{'shp_zip'} = $rec->{'Zip'};
		}
	}

	return $output;
}

#############################################################################
#############################################################################
#   Function: group_payments
#
#       Es: Agrupa los pagos de un a orden de venta
#       En: Groups the payment of a sales order
#
#
#    Created on: 2013-05-03
#
#    Author: Alejandro Diaz
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
#      - None
#
#   See Also:
#
#
sub group_payments{
#############################################################################
#############################################################################

	($idorders)=@_;
	if ($idorders > 0) {
		my ($sth) = &Do_SQL("SELECT
		(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$idorders' AND Status IN ('Credit') AND (Captured != 'Yes' OR Captured IS NULL))credits,
		(SELECT SUM(Amount)Amount FROM sl_orders_payments WHERE ID_orders='$idorders' AND Status IN ('Credit') AND (Captured != 'Yes' OR Captured IS NULL))total_credits,
		(SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$idorders' AND Status IN ('Approved') AND (Captured != 'Yes' OR Captured IS NULL))approved,
		(SELECT SUM(Amount)Amount FROM sl_orders_payments WHERE ID_orders='$idorders' AND Status IN ('Approved') AND (Captured != 'Yes' OR Captured IS NULL))total_approved;");
		my ($credits, $total_credits, $approved, $total_approved) = $sth->fetchrow_array();
		my $difference = ($total_approved + $total_credits);
		
		my ($sth) = &Do_SQL("SELECT SUM(Amount)Amount, MIN(ID_orders_payments)ID_orders_payments FROM sl_orders_payments WHERE ID_orders='$idorders' AND Status IN ('Approved','Credit') AND (Captured != 'Yes' OR Captured IS NULL);");
		my ($total, $id_orders_payments) = $sth->fetchrow_array();
		my $limit = ($approved + $credits) - 1;

		if ($difference > 0) {

			if ($approved >= 1 and $credits >= 1) {
				my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Amount='$total' WHERE ID_orders='$idorders' AND ID_orders_payments='$id_orders_payments' LIMIT 1;");
				my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$idorders' AND ID_orders_payments NOT IN($id_orders_payments) AND (Captured != 'Yes' OR Captured IS NULL) LIMIT $limit;");
				&auth_logging('opr_orders_group_payments',$idorders);
			}

		}elsif ($difference < 0) {
			# generar un credit con el resultado
			$total = $total * (-1);
			my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Amount='$total', Status='Credit' WHERE ID_orders='$idorders' AND ID_orders_payments='$id_orders_payments' LIMIT 1;");
			my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$idorders' AND ID_orders_payments NOT IN($id_orders_payments) AND (Captured != 'Yes' OR Captured IS NULL) LIMIT $limit;");
			&auth_logging('opr_orders_group_payments',$idorders);

		}elsif ($difference == 0) {
			# borrar todos
			my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$idorders' AND (Captured != 'Yes' OR Captured IS NULL);");
			&auth_logging('opr_orders_group_payments',$idorders);
			
		}
	}
}


#############################################################################
#############################################################################
#   Function: verify_order_lines
#
#       Es: Revisa los Status de Products y Payments
#       En: Check Products and Payments Status'
#
#
#    Created on: 2013-05-20
#
#    Author: RB
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
#      - None
#
#   See Also:
#
#
sub verify_order_lines{
#############################################################################
############################################################################# 

	&Do_SQL("UPDATE sl_orders_products SET Status = 'Active' WHERE Status  = '' OR Status IS NULL;");
	&Do_SQL("UPDATE sl_orders_payments SET Status = 'Approved' WHERE Status  = '' OR Status IS NULL;");
	($cfg{'payments_default_type'}) and (&Do_SQL("UPDATE sl_orders_payments SET Type = '$cfg{'payments_default_type'}' WHERE Type  = '' OR Type IS NULL;"));

}


#############################################################################
#############################################################################
#   Function: invoices_list
#
#       Es: Devuelve un string con la lista de invoices que tiene una orden
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *10/07/2011* by _Roberto Barcenas_ : Se agrega Amazon
#        - Modified on *02/15/2012* by _Roberto Barcenas_ : Se agrega Descuentolibre
#
#   Parameters:
#
#      - idpayment: ID Payment  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub invoices_list {
#############################################################################
	my ($id_orders) = @_;
	## Invoices
	my ($invoice_info) = '';
	$sth_inv = &Do_SQL("SELECT * FROM cu_invoices_lines LEFT JOIN cu_invoices ON cu_invoices_lines.ID_invoices=cu_invoices.ID_invoices WHERE ID_orders=$id_orders AND cu_invoices.Status<>'Cancelled' GROUP BY cu_invoices.ID_invoices;");
	while (my $invoice = $sth_inv->fetchrow_hashref){
		$invoice_info .= "<br>" if ($invoice_info );
		$invoice->{'doc_num'} = '' if(!$invoice->{'doc_num'});
		$invoice_info .= qq|$invoice->{'ID_invoices'} $invoice->{'doc_serial'}$invoice->{'doc_num'} $invoice->{'imr_code'}  $invoice->{'currency'}|. &format_price($invoice->{'invoice_total'}). qq|<br><i>($invoice->{'Status'}/$invoice->{'invoice_type'})</i>|;
	}
	return $invoice_info;
}


#############################################################################
#############################################################################
#   Function: export_info_for_credits_notes
#
#       Es: Genera una nota de credito
#       En: Credis Notes Generate
#
#
#    Created on: 24/06/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - 
#
#   Parameters:
#
#      - id_creditmemos: ID creditmemos  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub export_info_for_credits_notes {
#############################################################################
#############################################################################
	my ($id_creditmemos) = shift;
	my ($id_customers_advances) = shift;
	my ($id_invoices);

	## Adecuacion para CFDI 3.3
	$payment_type = 'PAGO EN UNA SOLA EXHIBICION';
	if($cfg{'cfdi_version'} == 3.3 ){
		$payment_type = $cfg{'cfdi_payment_type_default'};
	}

	# Validation: ordered vs invoiced
	my ($sth) = &Do_SQL("SELECT COUNT(*)pend_invoiced
			, (SELECT COUNT(*) FROM sl_creditmemos_products WHERE sl_creditmemos_products.ID_creditmemos = '$id_creditmemos' AND Status NOT IN('Inactive'))ordered
		FROM sl_creditmemos_products 
		WHERE sl_creditmemos_products.ID_creditmemos = '$id_creditmemos' 
		AND Status NOT IN('Inactive')
		AND ID_creditmemos_products NOT IN (
			SELECT ID_orders_products FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices)  WHERE cu_invoices_lines.ID_creditmemos = '$id_creditmemos' AND cu_invoices.`Status` NOT IN ('Void','Cancelled')
		);");
	my ($pend_invoiced,$prods_ordered) = $sth->fetchrow_array();

	## Se debe bloquear si ya existe previa, siempre y cuando no sea una factura cacelada o si existen elementos por facturar
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices INNER JOIN cu_invoices_lines USING(ID_invoices) WHERE cu_invoices_lines.ID_creditmemos = '$id_creditmemos' AND cu_invoices.Status NOT IN ('Void','Cancelled') GROUP BY ID_invoices)AS invoices;");
	my $is_invalid_invoice = int($sth->fetchrow_array);
	
	if ($is_invalid_invoice and $pend_invoiced==0){
		return &trans_txt('opr_orders_invoice_already_exists'), "ERROR";
	}

	if ($prods_ordered==0){
		return &trans_txt('opr_orders_invoice_noitems') , "ERROR";
	}

	## 1) Custom Info for Invoice

	## Definicion del campo payment_method
	## Para IMPORTACIONES y MUFAR este dato debe ser definido con los datos fiscales del cliente
	my $id_customers = &load_name('sl_creditmemos','ID_creditmemos',$id_creditmemos,'ID_customers');

	my ($sth_cuad) = &Do_SQL("SELECT COUNT(*), IFNULL( ID_customers_addresses, 0 ) ID_customers_addresses, Payment_Method FROM cu_customers_addresses WHERE id_customers='$id_customers' AND PrimaryRecord='Yes' LIMIT 1");
	my ($has_fiscal_data, $id_customers_addresses, $payment_method) = $sth_cuad->fetchrow_array;
	## Generic info for Invoice
	if($cfg{'validate_customer_payment'}){
		$generate_payment_invoice = &Do_SQL(qq|SELECT GeneratePaymentInvoice FROM cu_customers_addresses WHERE cu_customers_addresses.PrimaryRecord = 'Yes' AND ID_customers = '$id_customers' LIMIT 1|)->fetchrow();
		if(!$generate_payment_invoice){
			$has_fiscal_data = 0;
		}	
	}
	if(!$has_fiscal_data) {

		
		my ($sth) = &Do_SQL("SELECT sl_customers.Type  
		FROM sl_creditmemos INNER JOIN sl_customers ON sl_creditmemos.ID_customers=sl_customers.ID_customers
		WHERE 1 AND sl_creditmemos.ID_creditmemos='$id_creditmemos';");
		($ctype) = $sth->fetchrow();

		#revisar si ese tipo de cliente tiene un parametro con un id definido de customer generico
		if($cfg{'id_customer_generic_'.lc($ctype)} and int($cfg{'id_customer_generic_'.lc($ctype)}) > 0) {
			$id_customers = int($cfg{'id_customer_generic_'.lc($ctype)});
			
			# revisamos si el id es valido 
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE ID_customers = '$id_customers';");
			($is_valid_id_customer) = $sth->fetchrow_array();
			$id_customers = ($is_valid_id_customer) ? $id_customers : 0;

			if ($id_customers){
				my ($sth_cuad) = &Do_SQL("SELECT COUNT(*), IFNULL( ID_customers_addresses, 0 ) ID_customers_addresses FROM cu_customers_addresses WHERE id_customers='$id_customers' AND PrimaryRecord='Yes' LIMIT 1");
				($has_fiscal_data, $id_customers_addresses) = $sth_cuad->fetchrow_array;
			}
		}
	}

	## Definicion del campo payment_method
	## Para TMK/MOW Efectivo -> Referenced Deposit o COD y Tarjeta de Credito -> Credit-Card
	if (!$payment_method || !$has_fiscal_data){
		$sth = &Do_SQL("SELECT sl_orders.Ptype FROM sl_creditmemos_payments INNER JOIN sl_orders ON sl_creditmemos_payments.ID_orders=sl_orders.ID_orders WHERE sl_creditmemos_payments.ID_creditmemos=".$id_creditmemos." GROUP BY sl_creditmemos_payments.ID_creditmemos");
		my ($rec_order_ptype) = $sth->fetchrow();
		$payment_method = ($rec_order_ptype eq 'Credit-Card')? 'Tarjeta de Credito':'Efectivo';
	}

	my ($payment_method_code) = '99';
	if(!$has_fiscal_data){
		$sth = &Do_SQL("SELECT sl_vars_config.Code FROM sl_vars_config WHERE sl_vars_config.Command='sat_formadepago' AND sl_vars_config.Subcode='".$payment_method."';");		 +
	 	$payment_method_code = $sth->fetchrow();
	}



	if ($payment_method_code and $has_fiscal_data) {

		## Sacar datos de cliente real
		# 1) Para Company siempre sacar datos
		my ($sth_ci) = &Do_SQL("SELECT * FROM cu_company_legalinfo WHERE PrimaryRecord = 'Yes'");
		$rec_company_legal = $sth_ci->fetchrow_hashref;
		
		my ($sth_cr) = &Do_SQL("SELECT * FROM cu_company_addresses WHERE PrimaryRecord = 'Yes'");
		$rec_company_addr = $sth_cr->fetchrow_hashref;

		### 2) Para Cliente solo si es $id_customers_addresses
		#	2.1. Sacar customers_addresses LEFT JOIN legalinfo  - Primary Record para Datos Fiscales
		#	2.2. sacar customers_addresses solo donde el ID = $id_customers_addresses
		if($has_fiscal_data){
			my ($sth_cr) = &Do_SQL("SELECT IF(RFC IS NULL , 'XAXX010101000' , RFC) AS RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
			FROM cu_customers_addresses
			LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
			WHERE ID_customers_addresses = '".$id_customers_addresses."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
			$payment_type =  $rec_custom_info->{'Payment_type'};
			$payment_method_code = $rec_custom_info->{'Payment_Method'};
		}elsif($is_valid_id_customer) {
			my ($sth_cr) = &Do_SQL("SELECT RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
				FROM cu_customers_addresses
				LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
				WHERE sl_customers.ID_customers = '".$id_customers."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
		}
		
		# Datos del Currency
		my $order_currency = &load_name('sl_customers','ID_customers',$id_customers,'Currency');
		if(!$order_currency){
			$order_currency = 'MXP';
			$exchangerate = 1;
		}else{
			#Obtiene tipo de cambio peso/dolar
			my $sth= &Do_SQL("select exchange_rate from sl_exchangerates where Currency='$order_currency' AND Date_exchange_rate=CURDATE()");	
			$exchangerate = $sth->fetchrow;

			$exchangerate = 1 if($order_currency eq $cfg{'acc_default_currency'});
			if ($order_currency eq 'US$'){
				$order_currency = 'USD';
			}elsif ($order_currency eq 'EU$'){
				$order_currency = 'EUR';
			}elsif ($order_currency eq 'CO$'){
				$order_currency = 'COLP';
			}else{
				$order_currency = 'MXP';		
			}
			
		}

		if ($exchangerate eq ''){
			return &trans_txt('exchangerate_not_found'), "ERROR";
		}
			
		my $invoice_type = 'egreso';

		## Place Consignment
		my $place_consignment = $rec_company_addr->{'City'}.', '.$rec_company_addr->{'State'};

		my $use_cfdi = $rec_custom_info->{'Use_Cfdi_credit'};

		## ToDo: Hacer nuevo INSERT con datos especificos
		$sth_invoice = &Do_SQL("INSERT INTO cu_invoices SET 
			ID_customers = '".$id_customers."',
			expediter_fcode = '".$rec_company_legal->{'RFC'}."',
			expediter_fname = '".$rec_company_legal->{'Name'}."',
			expediter_fregimen = '".$rec_company_legal->{'Regime'}."',    
			ID_orders_alias	= NULL,
			use_cfdi = '$use_cfdi',
			payment_method = '".$payment_type."',
			discount = NULL,
			place_consignment = '".$place_consignment."',
			invoice_net = '00.00',  
			invoice_total = '00.00',
			doc_date =  NOW() ,
			currency = '".$order_currency."',
			currency_exchange = '".$exchangerate."',
			credit_days = NULL,
			invoice_type = '".$invoice_type."',
			expediter_faddress_street = '".$rec_company_addr->{'Street'}."', 
			expediter_faddress_num  = '".$rec_company_addr->{'Num'}."', 
			expediter_faddress_num2 = '".$rec_company_addr->{'Num2'}."', 
			expediter_faddress_urbanization = '".$rec_company_addr->{'Urbanization'}."', 
			expediter_faddress_district = '".$rec_company_addr->{'District'}."', 
			expediter_faddress_city = '".$rec_company_addr->{'City'}."', 
			expediter_faddress_state = '".$rec_company_addr->{'State'}."', 
			expediter_faddress_country = '".$rec_company_addr->{'Country'}."', 
			expediter_faddress_zipcode = '".$rec_company_addr->{'Zip'}."', 
			expediter_address_street = '".$rec_company_addr->{'Street'}."', 
			expediter_address_num = '".$rec_company_addr->{'Num'}."', 
			expediter_address_num2 = '".$rec_company_addr->{'Num2'}."', 
			expediter_address_urbanization = '".$rec_company_addr->{'Urbanization'}."', 
			expediter_address_district = '".$rec_company_addr->{'District'}."', 
			expediter_address_city = '".$rec_company_addr->{'City'}."', 
			expediter_address_state = '".$rec_company_addr->{'State'}."', 
			expediter_address_country = '".$rec_company_addr->{'Country'}."', 
			expediter_address_zipcode = '".$rec_company_addr->{'Zip'}."', 						
			customer_fcode = '".$rec_custom_info->{'RFC'}."', 
			customer_fname = '".$rec_custom_info->{'lname'}."',
			customer_address_street = '".$rec_custom_info->{'Address1'}." ".$rec_custom_info->{'Address2'}." ".$rec_custom_info->{'Address3'}."', 
			customer_address_urbanization = '".$rec_custom_info->{'Urbanization'}."',
			customer_address_city = '".$rec_custom_info->{'City'}."', 
			customer_address_state = '".$rec_custom_info->{'State'}."', 
			customer_address_country = '".$rec_custom_info->{'Country'}."', 
			customer_address_zipcode = '".$rec_custom_info->{'Zip'}."', 					
			
			customer_shpaddress_code = NULL,
			customer_shpaddress_alias = NULL,

			customer_shpaddress_street = '".$rec_custom_info->{'cu_Street'}."', 
			customer_shpaddress_num	= '".$rec_custom_info->{'cu_Num'}."', 
			customer_shpaddress_num2 = '".$rec_custom_info->{'cu_Num2'}."', 
			customer_shpaddress_urbanization = '".$rec_custom_info->{'cu_Urbanization'}."', 
			customer_shpaddress_district = '".$rec_custom_info->{'cu_District'}."', 
			customer_shpaddress_city = '".$rec_custom_info->{'cu_City'}."', 
			customer_shpaddress_state = '".$rec_custom_info->{'cu_State'}."', 
			customer_shpaddress_country = '".$rec_custom_info->{'cu_Country'}."', 
			customer_shpaddress_zipcode	= '".$rec_custom_info->{'cu_Zip'}."',
			
			payment_digits = NULL,
			conditions = NULL,
			payment_type = '$payment_method_code',
			STATUS = 'New' , 
			VendorID = NULL,
			customer_address_gln=NULL, 
			customer_shpaddress_gln=NULL,
			DATE = CURDATE(), TIME = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."' ");
		$id_invoices = $sth_invoice->{'mysql_insertid'};
		
		if ($id_invoices) {
			# Por cada producto agregamos una registro en cu_invoices_line
			# 'Active','Exchange','Returned','Undeliverable','Order Cancelled','Inactive','Lost','ReShip'
			# my $add_sql = ($in{'creditnote'})? ' AND SalePrice < 0 ':' AND SalePrice > 0 ';
			my ($sth_lines) = &Do_SQL("
			SELECT
				ID_creditmemos_products
				, sl_creditmemos_products.ID_products
				, Quantity
				, SalePrice
				, Tax
				, Tax_percent
				, ShpTax
				, Shipping
				, sl_creditmemos_products.Discount as Discount
				, IF(sl_creditmemos_products.ID_products>600000000 AND sl_creditmemos_products.ID_products<700000000, sl_creditmemos_products.ID_products, sl_skus.ID_sku_products) AS ID_sku
				, if(sl_customers_parts.sku_customers is null or sl_customers_parts.sku_customers='', sl_skus.UPC,sl_customers_parts.sku_customers) AS ID_sku_alias
				, sl_skus.UPC as UPC
				, sl_customers_parts.size as size
				, sl_creditmemos_products.Cost
			FROM sl_creditmemos
			LEFT JOIN sl_creditmemos_products ON sl_creditmemos.ID_creditmemos=sl_creditmemos_products.ID_creditmemos
			LEFT JOIN sl_customers_parts ON sl_customers_parts.ID_parts=SUBSTR(sl_creditmemos_products.ID_products,2,8)*1 AND sl_customers_parts.ID_customers=sl_creditmemos.ID_customers
			LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_creditmemos_products.ID_products
			WHERE sl_creditmemos.ID_creditmemos = '$id_creditmemos'
			AND sl_creditmemos_products.Status IN('Active')
			AND ID_creditmemos_products NOT IN (
				SELECT ID_orders_products FROM cu_invoices_lines INNER JOIN cu_invoices USING(ID_invoices)  WHERE cu_invoices_lines.ID_creditmemos = '$id_creditmemos' AND cu_invoices.`Status` NOT IN ('Void','Cancelled')
			); ");
			my $total_net = 0;
			my $total_tax = 0;
			my $total_discount = 0;			
			my $total = 0;
			my $total_shipping = 0;
			my $total_shipping_tax = 0;

			while(my $rec=$sth_lines->fetchrow_hashref) {
				my ($idp,$link_ts,$idp,$sku,$packing_type);

				if ($rec->{'ID_products'} < 99999 or substr($rec->{'ID_products'},0,1) == 6){				
					#Services
					$link_ts = "mer_services";
					$idp = $rec->{'ID_products'}-600000000;
					$va{'Name'}	= &load_name("sl_services","ID_services",$idp,"Name");
					
				}elsif (substr($rec->{'ID_products'},0,1) == 4){
					#Skus
					$idp=$rec->{'ID_products'}-400000000;
					$link_ts 	= "mer_parts";
					$va{'Name'} = &load_name("sl_parts","ID_parts",$idp,"Name");
					$va{'Model'} = &load_name("sl_parts","ID_parts",$idp,"Model");
				
				}else{
					#Products
					$idp=$rec->{'ID_products'}-100000000;
					$link_ts 	= "mer_products";
					$va{'Name'}	= &load_name("sl_products","ID_products",$idp,"Name");
					$va{'Model'}	= &load_name("sl_products","ID_products",$idp,"Model");
				}
				
				if ($cfg{'customers_parts_use'} and $cfg{'customers_parts_use'}==1) {
					my ($sth) = &Do_SQL("SELECT sku_customers, packing_type FROM sl_customers_parts WHERE ID_customers = '$in{'id_customers'}' AND ID_parts = '$idp';");
					($sku, $packing_type) = $sth->fetchrow();
				}
				$sku = (!$sku)? $rec->{'ID_products'} : $sku;
				$packing_type = (!$packing_type)? &trans_txt('invoices_measuring_unit') : $packing_type;

				
				$line++;
				$rec->{'SalePrice'} = ($rec->{'SalePrice'}*-1) if($rec->{'SalePrice'} < 0);
				$rec->{'Tax'} = ($rec->{'Tax'}*-1) if($rec->{'Tax'} < 0);
				$rec->{'Quantity'} = ($rec->{'Quantity'}*-1) if($rec->{'Quantity'} < 0);
				my $amount = $rec->{'SalePrice'}*$rec->{'Quantity'};
				$rec->{'Tax_percent'} = 0 if (!$rec->{'Tax_percent'});
				$rec->{'Tax_percent'} = $rec->{'Tax_percent'}/100 if ($rec->{'Tax_percent'});
				
				
				&Do_SQL("INSERT INTO cu_invoices_lines SET 
					`ID_orders`=0,
					`ID_creditmemos`=$id_creditmemos,
					`ID_orders_products`='".$rec->{'ID_creditmemos_products'}."',
					`ID_invoices`='$id_invoices',  
					`line_num`='$line',  
					`quantity`='".$rec->{'Quantity'}."',  
					`measuring_unit`='".$packing_type."',
					`description`='".$va{'Name'}."',
					`unit_price`='".($rec->{'SalePrice'})."',  
					`amount`='".$amount."',
					`tax`='".$rec->{'Tax'}."',
					`tax_rate`='".$rec->{'Tax_percent'}."',
					`discount`='".$rec->{'Discount'}."',
					`ID_sku`='".$rec->{'ID_sku'}."',
					`ID_sku_alias`='".$rec->{'ID_sku_alias'}."',
					`UPC`='".$rec->{'UPC'}."',
					`size`='".$rec->{'size'}."',
					`Cost`='".$rec->{'Cost'}."',
					`Date`=CURDATE(),  
					`Time`=CURTIME(),  
					`ID_admin_users`='".$usr{'id_admin_users'}."' ");
					

				$total_shipping += $rec->{'Shipping'};
				if($rec->{'ShpTax'} > 0){
					$total_shipping_tax += $rec->{'ShpTax'};
				}
				
				$total_net += $rec->{'Shipping'};
				$total_tax += $rec->{'ShpTax'};
				$total_net += $amount;
				$total_tax += $rec->{'Tax'};
				$total_discount += $rec->{'Discount'};
				
			}
			##calcular el total de la orden
			$total = $total_net + $total_tax - $total_discount;

			#Se tiene que insertar siempre la primer linea con los datos de SHIPPING
			# #calculo el tax utilizado en shipping
			if ($total_shipping > 0 ) {
				my ($tax_shipping_percent) = ($cfg{'shptax_percent_default'})?$cfg{'shptax_percent_default'}:'0';
				my ($add_id_sku) = ($cfg{'ID_shipping_service'})? qq| `ID_sku`="|.(600000000+int($cfg{'ID_shipping_service'})).qq|",| : '';

				&Do_SQL("INSERT INTO cu_invoices_lines SET 
				`ID_orders`= 0,
				`ID_creditmemos`=$id_creditmemos,
				`ID_invoices`=$id_invoices,  
				`line_num`= 1,  
				`quantity`= 1,  
				`measuring_unit`='".&trans_txt('invoices_measuring_unit')."',
				`description`='".&trans_txt('invoices_shipping')."',
				`unit_price`=".$total_shipping.",
				`amount`=".$total_shipping.",
				`tax`=".$total_shipping_tax.",
				`tax_rate`=".$tax_shipping_percent.",
				$add_id_sku
				`Date`=CURDATE(),  
				`Time`=CURTIME(),  
				`ID_admin_users`='".$usr{'id_admin_users'}."'
				");	
			}

			&Do_SQL("UPDATE cu_invoices SET invoice_net=$total_net, total_taxes_transfered=$total_tax, invoice_total=$total, discount=$total_discount WHERE `ID_invoices`=$id_invoices");

			## Nota + Log
			&Do_SQL("INSERT INTO sl_creditmemos_notes SET ID_creditmemos = '$id_creditmemos', Notes='".&trans_txt('opr_orders_invoice_added').": $id_invoices',Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;");
			&auth_logging('opr_creditmemos_invoice_added',$id_creditmemos);

			#########################################################################
			############  Relacionamos nota de Credito con factura de Orden  ########
			############  Se toma la primer factura que encuetra 
			#########################################################################
			if($cfg{'cfdi_version'} == 3.3){
				if($id_customers_advances){
					$query = qq|
										select 
						cu_invoices_lines.ID_orders
						, cu_invoices.ID_invoices
						, cu_invoices.xml_uuid 
					from sl_customers_advances_payments
					inner join cu_invoices_lines on sl_customers_advances_payments.ID_orders = cu_invoices_lines.ID_orders
					inner join cu_invoices on cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
					where sl_customers_advances_payments.ID_customers_advances = $id_customers_advances
					group by cu_invoices_lines.ID_invoices;|;
					$rs = &Do_SQL($query);
					while($row = $rs->fetchrow_hashref()){
						if($row->{'ID_invoices'}){
							&Do_SQL(qq|
							INSERT INTO `cu_related_cfdi` (`id_cfdi`, `id_related`, `uuid_related`, `relation_type`) VALUES
													($id_invoices, $row->{'ID_invoices'}, '$row->{'xml_uuid'}', '01');
							|);
						}
					}

				}elsif($id_creditmemos){
					$query = qq|select 
						cu_invoices_lines.ID_orders
						, cu_invoices.ID_invoices
						, cu_invoices.xml_uuid 
						, sl_creditmemos_payments.Amount
						, cu_invoices.ID_customers
					from sl_creditmemos_payments
					inner join cu_invoices_lines on sl_creditmemos_payments.ID_orders = cu_invoices_lines.ID_orders
					inner join cu_invoices on cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
					where sl_creditmemos_payments.ID_creditmemos = $id_creditmemos
					group by cu_invoices_lines.ID_invoices;|;
					$rs = &Do_SQL($query);
					while($row = $rs->fetchrow_hashref()){
						if($row->{'ID_invoices'}){
							&Do_SQL(qq|
							INSERT INTO `cu_related_cfdi` (`id_cfdi`, `id_related`, `uuid_related`, `relation_type`) VALUES
													($id_invoices, $row->{'ID_invoices'}, '$row->{'xml_uuid'}', '01');
							|);
							#$id_banks_movements, $id_customers, $type, $amount, $tableused, $id_tableused, $id_related_invoices
							&payment_logging(0, $row->{'ID_customers'}, 'Out', $row->{'Amount'}, 'cu_invoices', $id_invoices, $row->{'ID_invoices'});
						}

					}
				}
			}

			#########################################################################
			#########################################################################


			$va{'message'} = &trans_txt('opr_orders_invoice_added') .":$id_invoices";

			return &trans_txt('opr_orders_invoice_added') .": $id_invoices", "OK", $id_invoices;

		}else {
			return &trans_txt('invoices_error_generating'), "ERROR", 0;
		}

	}else {
		return &trans_txt('invoices_cust_data_not_found'), "ERROR", 0;
	}
}

sub warningsinorder {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on:  07/24/2008
# Last Modified on: 08/14/2008
# Last Modified by: MCC C. Gabriel Varela S.
# Description : it shows icon warnings  for returns, claims, repmemos y fraucheck
# Forms Involved: opr_orders_view
# Parameters : 
	return &hasreturn().&fraudcheck().&hasclaim().&hasrepmemo().&haschargeback();
}


sub fraudcheck {
# --------------------------------------------------------
# Last Modified on: 11/19/08 15:51:05
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar cuando hay errores en totales tambi?n en el texto alternativo
	my ($totals) = &check_ord_totals($in{'id_orders'});
	my ($rmsg) = &check_rman($in{'id_orders'});
	
	if ($rmsg eq 'OK' and $totals eq 'OK'){
		return '';
	}else{
		($rmsg eq 'OK') and ($rmsg = "");
		($totals eq 'OK') and ($totals = "");
		return  qq|<a href='#top' id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'top');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=show_risk_orders&id_orders=$in{'id_orders'}');"><img src='[va_imgurl]/[ur_pref_style]/warning.gif' title='$rmsg. $totals' alt='$rmsg. $totals' border='0'></a>|;
	}
}


sub haschargeback {
# --------------------------------------------------------

# Author: MCC C. Gabriel Varela S.
# Created on: 08/14/2008
# Description :  it shows if the order has chargebacks
# Forms Involved: 
# Parameters : 

	my $sth=&Do_SQL("SELECT sl_orders_products.ID_orders FROM sl_chargebacks INNER JOIN sl_chargebacks_items USING(ID_chargebacks) INNER JOIN sl_orders_products USING(ID_orders_products) WHERE sl_orders_products.ID_orders = $in{'id_orders'} AND sl_chargebacks.Status='Opened';");
	my $chargeback=$sth->fetchrow();
	return qq|<a href='#'><img src='[va_imgurl]/[ur_pref_style]/claims.png' title='Esta orden tiene registros de Charge Backs' alt='chargebacksinorder' border='0' onClick='trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&tab=11&tabs=1#tabs")'></a>| if ($chargeback);
}

sub hasclaim {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 07/24/2008
# Last Modified on: 
# Last Modified by:
# Description :  it shows if the order has claims
# Forms Involved: 
# Parameters : 

	my $sth=&Do_SQL("SELECT sl_orders_products.ID_orders FROM sl_claims, sl_orders_products WHERE sl_claims.ID_orders_products=sl_orders_products.ID_orders_products AND sl_orders_products.ID_orders=$in{'id_orders'} AND sl_claims.Status='Opened';");
	my $claim=$sth->fetchrow();
	return qq|<a href='#'><img src='[va_imgurl]/[ur_pref_style]/claims.png' title='Esta orden tiene registros de Claims' alt='claimsinorder' border='0' onClick='trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&tab=10&tabs=1#tabs")'></a>| if ($claim);
}

sub hasrepmemo {
# --------------------------------------------------------
 
# Author: Jose Ramirez Garcia
# Created on: 07/24/2008
# Last Modified on: 
# Last Modified by: 
# Description :  it shows if the order has claims
# Forms Involved: 
# Parameters : 
	
	my $sth=&Do_SQL("SELECT ID_orders FROM sl_repmemos WHERE ID_orders=$in{'id_orders'} AND Status='New'");
	my $repmemo=$sth->fetchrow();	
	return qq|<a href='#'><img src='[va_imgurl]/[ur_pref_style]/repmemos.png' title='Esta orden tiene registros de Replacement Memo' alt='repmemoinorder' border='0' onClick='trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&tab=9&tabs=1#tabs")'></a>| if ($repmemo);
}

#############################################################################
#############################################################################
#   Function: review_order
#
#       Es: Evalua la orden si se detecta algun problema la pasa a estatus Pending para que sea revisada
#       En: Evaluate the order if a problem is detected, the status becomes Pending for review
#
#
#    Created on: 12/09/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#
#   See Also:
#
#      <>
#
sub review_order {
#############################################################################
#############################################################################
	my ($id_orders) = @_;

	my ($response) = &check_ord_totals($id_orders);
	
	###
	## Pauta Seca
	###
	if ($cfg{'pauta_seca_enabled'} and $cfg{'pauta_seca_enabled'} == 1 ){
		my ($sth2) = &Do_SQL("SELECT COUNT(*)pauta_seca FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders) INNER JOIN sl_products ON right(sl_orders_products.ID_products,6)=sl_products.ID_products
		WHERE sl_products.Status='Pauta Seca' AND sl_orders.ID_orders='$id_orders' AND sl_orders.Status NOT IN('Cancelled','System Error') AND sl_orders_products.Status='Active';");

		$rec = $sth2->fetchrow_hashref;
		if ($rec->{'pauta_seca'} > 0){
            ## Cancel Order        
            &Do_SQL("UPDATE sl_orders SET Status='Cancelled', StatusPrd='None', StatusPay='None' WHERE ID_orders='$id_orders';");
            &auth_logging('opr_orders_stCancelled',$id_orders);
			&status_logging($id_orders,'Cancelled');

            $in{'status'} = 'Cancelled';
            $in{'statusprd'} = 'None';
            $in{'statuspay'} = 'None';
            
            ## Log
            $in{'db'} = "sl_orders";
            &auth_logging(&trans_txt('opr_orders_cancelled_automatically'), $id_orders);

            &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders',Notes='Order Cancelled: Pauta Seca',Type='Low',ID_orders_notes_types='1',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
       

			$response = '' if ($response eq 'OK');
			$response.=" <li>Order is Pauta Seca </li>";
			$response.=" <li>Order Automatically Canceled </li>";
			return $response
		}
	}

	###
	## Payment Captured
	###
	if ($in{'ptype'} ne 'COD'){

		$response = '' if ($response eq 'OK');
		my ($sth2) = &Do_SQL("SELECT 
								ID_orders
								, SUM(IF(Status NOT IN('Credit','ChargeBack','Void','On Collection','Claim','Order Cancelled','Cancelled') AND (Captured IS NULL OR Captured <> 'Yes') AND ( LENGTH(Authcode) = 0 OR AuthCode='0000'), Amount,0))AS SumNotPay 
							FROM 
								sl_orders_payments 
							WHERE 1 
								 AND ID_orders = '$id_orders' AND Type IN ('Credit-Card','Referenced Deposit')
						GROUP BY ID_orders");

		$rec = $sth2->fetchrow_hashref;
		if ($rec->{'SumNotPay'} > 0){
			$response.=" <li>Payment amount of ".&format_price($rec->{'SumNotPay'}) ." is not captured </li>";
			
		}else{
			$response="OK";
		}
	}

	if ($response ne 'OK' and $in{'ptype'} eq 'COD') {
		my ($sth2) = &Do_SQL("UPDATE sl_orders SET Status='Pending', StatusPay='Review Order' WHERE ID_orders='$id_orders';");
		
		## Log
		my $clean_response = $response;
		$clean_response =~ s|<.+?>||g;
		

		&add_order_notes_by_type($id_orders,&trans_txt('opr_orders_stPending')." for review: $clean_response","Low");

		$in{'db'} = "sl_orders";
		&auth_logging('opr_orders_stPending',$id_orders);
		&status_logging($id_orders,'Pending');

	}

	return $response;
}



#########################################################################################################
#########################################################################################################
#
#	Function: order_scan_check_shpdate
#   		
#		sp: Revisa lineas de sl_orders_parts que no tengan ShpDate y actualiza el campo en sl_orders_parts y sl_orders_products
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also: 110102
#
sub order_scan_check_shpdate {
#########################################################################################################
#########################################################################################################


	my ($id_orders) = @_;
	$id_orders = int($id_orders);
	my $modquery;

	if($id_orders){

		my ($sthp) = &Do_SQL("SELECT GROUP_CONCAT(ID_orders_products) FROM sl_orders_products 
							WHERE ID_orders = '$id_orders' AND Status IN('Active','Exchange','Reship')
							AND SalePrice >= 0; ");
		my ($grouped_id_orders) = $sthp->fetchrow();
		$modquery = "ID_orders_products IN ($grouped_id_orders) AND ";
	}


	&Do_SQL("UPDATE sl_orders_products INNER JOIN
			(
			    SELECT ID_orders_products, Date, SUM(Cost) AS FCost FROM `sl_orders_parts`
			    WHERE $modquery 1 /*`ShpDate` = '0000-00-00'*/
			    GROUP BY ID_orders_products
			)tmp
			USING(ID_orders_products)
			SET 
			sl_orders_products.ShpDate = IF(sl_orders_products.ShpDate IS NULL OR sl_orders_products.ShpDate = '' OR sl_orders_products.ShpDate = '0000-00',tmp.Date,ShpDate), 
			Cost = IF(Cost IS NULL OR Cost <= 0,FCost,Cost);");


	&Do_SQL("UPDATE `sl_orders_parts`
			SET `ShpDate` = Date
		    WHERE $modquery `ShpDate` = '0000-00-00';");


}

#############################################################################
#############################################################################
#   Function: block_orders_in_batch
#
#       Es: Valida el numero de productos en la orden para permitir editar una orden
#       En: Validates the number of products in order to allow editing an order
#
#
#    Created on: 18/10/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve OK si la ordern se puede editar o el error si  no se puede
#
#   See Also:
#
#      <>
#
sub block_orders_in_batch{
#############################################################################
#############################################################################
	my ($id_orders) = @_;
	my ($validation);
	
	my ($sth2) = &Do_SQL("SELECT COUNT(*)order_in_batch FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products WHERE sl_warehouses_batches_orders.Status IN ('In Fulfillment','In Transit','Shipped') AND ID_orders = '$id_orders';");
	$rec = $sth2->fetchrow_hashref;
	if ($rec->{'order_in_batch'} == 0){
		$validation="OK";
	}else{
		$validation.=" <li>Order in Batch </li>";
	}

	return $validation;
}


#############################################################################
#############################################################################
#   Function: orders_payments_risk_status
#
#       Es: Cambia Status de ordena Pending basado en configuracion y check_rman
#       En: 
#
#
#    Created on: 08/07/2014
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve OK o error
#
#   See Also:
#
#      <>
#
sub orders_payments_risk_status{
#############################################################################
#############################################################################

	my ($id_orders) = @_;
	my $this_status = $cfg{'risk_status'} ne '' ? $cfg{'risk_status'} : 0;
	my $riskorder_msg = '...';
	return $riskorder_msg if !$this_status;

	(!$id_orders and $cses{'id_orders'}) and ($id_orders = $cses{'id_orders'});
	(!$id_orders and $in{'id_orders'}) and ($id_orders = $in{'id_orders'});

	$riskorder = &check_rman($id_orders);

	if ($riskorder ne 'OK'){
		&Do_SQL("UPDATE sl_orders SET Status = '$this_status', StatusPay = 'Review Order' WHERE ID_orders = '$id_orders'; ");

		&add_order_notes_by_type($id_orders,"Risk Order\n$riskorder\n","High");
		&add_order_notes_by_type($id_orders,"Order ".$this_status,"High");
		&status_logging($id_orders,$this_status);
		&auth_logging('opr_orders_st'.$this_status,$id_orders);

		$riskorder_msg = &trans_txt('riskorder_pending');

	}
	return $riskorder_msg;
}

#############################################################################
#############################################################################
#   Function: orders_folio_cfdi_online
#
#       Es: Generate Folio by Invoice Online 
#       En: Genera el folio unico para facturacion en linea
#
#
#    Created on: 01/01/2014
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve el Folio
#
#   See Also:
#
#      <>
#
sub orders_folio_cfdi_online{
#############################################################################
#############################################################################
	my ($folio);
	
	if ($cfg{'use_folio_cfdi_online'} and $cfg{'use_folio_cfdi_online'}==1 and $in{'id_orders'}){
		$sql = "SELECT CONCAT('$cfg{'prefixentershipment'}', id_orders,date_format(time,'%s%H%i')) FROM sl_orders WHERE status='Shipped' AND ID_orders='$in{'id_orders'}';";
		my ($sth) = &Do_SQL($sql);
		$folio = $sth->fetchrow_array();
	}

	return $folio;
}

#############################################################################
#############################################################################
#   Function: validate_scan
#
#       Es: Valida escaneo de pedido
#       En: 
#
#
#    Created on: 24/03/2015
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_orders: ID orders  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub validate_scan {
#############################################################################
#############################################################################

	my ($id_orders) = @_;
	my ($validation) = 0;

	if ($id_orders){

		my ($sth) = &Do_SQL("SELECT COUNT(*) totals, GROUP_CONCAT(sl_orders_products.Related_ID_products) prods
		FROM sl_orders_products 
		WHERE 
		    ID_orders='$id_orders' 
		    AND IF(
		        LENGTH(sl_orders_products.Related_ID_products) > 0 
		        AND sl_orders_products.Related_ID_products > 0,
		            IF( 
		                LENGTH(sl_orders_products.Related_ID_products) = 9, 
		                    sl_orders_products.Related_ID_products NOT LIKE '6%'
		                    AND LEFT(sl_orders_products.ID_products,1) = 1,
		                    LENGTH(sl_orders_products.Related_ID_products) = 6
		            ),
		        LEFT(sl_orders_products.ID_products,1) = 1
		    ) 
		    AND (sl_orders_products.ShpDate IS NULL OR sl_orders_products.ShpDate = '0000-00-00')
		    AND sl_orders_products.Status IN ('Active','Exchange','ReShip'); ");
		my($totals, $prods) = $sth->fetchrow();
		return ($totals, $prods);

	}
	return (0,"_");
}


#############################################################################
#############################################################################
#   Function: validate_scan_skus
#
#       Es: Valida escaneo de pedido basado en los skus que debian salir vs los skus que salieron (solamente en escaneos originales)
#       En: 
#
#
#    Created on: 16/06/2016
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_orders: ID orders  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub validate_scan_skus {
#############################################################################
#############################################################################

	my ($id_orders) = @_;
	my $parts_difference = 0;
	my $this_str;

	## Must vs Done
	# $q1 = Lo que salió
	# $q2 = Lo que debió salir
	
	my $log;
	my $query = "SELECT 
					sl_skus_parts.ID_parts
					,SUM(sl_orders_products.Quantity * sl_skus_parts.Qty) AS TQty2 
				FROM sl_orders_products 
					LEFT JOIN sl_skus_parts ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
				WHERE sl_orders_products.ID_orders = " . $id_orders . " AND sl_orders_products.Status = 'Active'	
				GROUP BY sl_skus_parts.ID_parts 
				ORDER BY sl_skus_parts.ID_parts;";
	my ($sth) = &Do_SQL($query);
	$log .= $query . qq|<br>\n|;

	TMvTD:while(my($id_parts, $q2) = $sth->fetchrow()){

		if( $id_parts ){
			my $query2 = "SELECT 
									SUM(sl_orders_parts.Quantity) Quantity
								FROM sl_orders_parts
									INNER JOIN sl_orders_products USING(ID_orders_products)
								WHERE sl_orders_products.ID_orders = " . $id_orders . " 
									AND sl_orders_parts.ID_parts = " . $id_parts . "
								GROUP BY sl_orders_parts.ID_parts;";
			$log .= $query2 . qq|<br>\n|;					
			my $sth_q1 = &Do_SQL($query2);
			my $q1 = $sth_q1->fetchrow();

			if($q1 ne $q2){

				++$parts_difference;
				$this_str .= qq|IDP:$id_parts = OP:$q1 vs SP:$q2<br>|;
				$log .= qq|     IDP:$id_parts = OP:$q1 vs SP:$q2<br>\n|;

			}
		}
		
	}

	$log = qq|<br>\n######### VALIDATE SCAN ###########<br>\n\n| . $log;
	return ($parts_difference, $this_str, $log);
}


#############################################################################
#############################################################################
#   Function: validate_scan_duplicated
#
#       Es: Valida para evitar un escaneo del pedido doble
#       En: 
#
#
#    Created on: 24/03/2015
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_orders: ID orders  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub validate_scan_duplicated {
#############################################################################
#############################################################################

	my ($id_orders, $type) = @_;
	my ($validation) = 0;

	if ($id_orders){

		my $add_sql = ($type ne '')? " AND Type='$type' ":"";

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus_trans WHERE id_trs='$id_orders' AND tbl_name='sl_orders' $add_sql AND Date=CURDATE() AND TIMESTAMPDIFF(SECOND, CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 120;");
		$validation = $sth->fetchrow();

	}
	
	# return $validation;
	return 0;
}


#############################################################################
#############################################################################
#   Function: get_bin_creditcard_type
#
#       Es: Regresa el tipo de una tarjeta de Credito basada en los bines
#       En: 
#
#
#    Created on: 30/04/2015
#
#    Author: _RB_ 
#
#    Modifications:
#		- Last time Modified by _RB_ on 2015-07-15: Se permite buscar campos diferentes. Recibido como segundo parametro
#
#
#   Parameters:
#
#      - id_orders_payments: ID orders Payments  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_bin_creditcard_type {
#############################################################################
#############################################################################

	my ($id_orders_payments, $field) = @_;
	my $banktype;

	my $ccnumber = &load_name('sl_orders_payments', 'ID_orders_payments', $id_orders_payments,'PmtField3');
	return if length($ccnumber) < 15;

	if(&table_exists('cu_cardprefix')){

		my ($sth) = &Do_SQL("SELECT LOWER($field) FROM cu_cardprefix 
							WHERE LEFT(Prefix,3) = LEFT('$ccnumber',3) AND Status='Active'
							ORDER BY Date DESC LIMIT 1;");
		$banktype = $sth->fetchrow();

	}

	###
	### Si no existe la tabla de bines, tratar de extraerlo de la tabla de payments
	###
	if($field eq 'Bank'){
		$banktype = &load_name('sl_orders_payments', 'ID_orders_payments', $id_orders_payments,'PmtField2') if !$banktype;
	}

	return $banktype;

}


#############################################################################
#############################################################################
#   Function: get_refund_chargeback_link
#
#       Es: Evalua si una orden puede contener un chargeback y devuelve link en la vista de la orden
#       En: 
#
#
#    Created on: 04/08/2015
#
#    Author: _RB_ 
#
#    Modifications:
#    
#    				Last Time Modified by _RB_: Cambia de nombre de get_chargeback_link   --> get_refund_chargeback_link . Se agrega funcionalidad para trabajar con refunds
#
#
#   Parameters:
#
#      - All $in{}
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_refund_chargeback_link {
#############################################################################
#############################################################################

	my $this_events_string;
	my @ary_events = ('Refund','Chargeback');
	my $err = 0;
	my $validChargeBack = true;

	if ($in{'id_orders'} > 0){

		###
		### Evaluamos si la orden tiene productos que no hayan sido motivo de
		###
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders INNER JOIN sl_orders_payments USING(ID_orders) WHERE sl_orders.ID_orders = '". $in{'id_orders'} ."' AND Ptype = 'Credit-Card' AND sl_orders.Status NOT IN('System Error') AND Captured = 'Yes' AND CapDate != '0000-00-00';");
		if (!$sth->fetchrow()){
			++$err;
		}

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_chargebacks INNER JOIN sl_chargebacks_items USING(ID_chargebacks) INNER JOIN sl_orders_products USING(ID_orders_products) WHERE sl_orders_products.ID_orders = '". $in{'id_orders'} ."' AND sl_chargebacks_items. ID_orders_products = sl_orders_products.ID_orders_products AND sl_chargebacks.Status <> 'Denied' AND sl_chargebacks_items.Status = 'Active';");
		if ($sth->fetchrow()){
			++$err;
		}		

		my ($sth) = &Do_SQL("
			SELECT a.orderStatus, a.totalReturns, op2.`Status` statusLastProd
			FROM (
				SELECT o.`Status` orderStatus, COUNT(DISTINCT r.ID_returns) totalReturns, 
				MAX(op.ID_orders_products) max_ID_orders_products
				FROM sl_orders o
				INNER JOIN sl_orders_products op ON op.ID_orders = o.ID_orders
				LEFT JOIN sl_returns r ON r.ID_orders = o.ID_orders
					AND r.`Status` IN('New', 'In Process', 'Back to inventory')
				WHERE o.ID_orders = ". $in{'id_orders'} ."
				GROUP BY o.`Status`
			)a
			INNER JOIN sl_orders_products op2 ON op2.ID_orders_products = a.max_ID_orders_products
			;"
		);
		my ($orderStatus, $totalReturns, $statusLastProd) = $sth->fetchrow();

		if ($orderStatus eq 'Shipped') {
			if ($totalReturns == 0) {
				if ($statusLastProd eq 'Returned') {
					$validChargeBack = false;
				}
			} else {
				$validChargeBack = false;
			}
		}

	}else{

		++$err;

	}

	ACTIONS:for(0..$#ary_events){

		next ACTIONS if ( lc($ary_events[$_]) eq 'refund' and lc($in{'status'}) eq 'shipped');

		my $this_event_link = '/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_refund_chargeback&id_orders='.$in{'id_orders'};
		my $this_event = $ary_events[$_];

		if (!$err and &check_permissions('opr_orders_'. lc($this_event) .'s','','') ){

			$this_event_link .= qq|&refund=1| if $this_event eq 'Refund';
			$this_event_link .= qq|&isshipped=1| if ( lc($ary_events[$_]) eq 'chargeback' and lc($in{'status'}) eq 'shipped' and $validChargeBack);
			$this_event_link .= qq|&path=/cgi-bin/mod/|. $usr{'application'} .qq|/dbman?cmd=opr_orders|;
			$this_events_string .= qq|
									<a href="|. $this_event_link .qq|" class="fancy_modal_iframe">
										<img src="[va_imgurl]/orders/|. lc($this_event) .qq|.png" title="Start |. $this_event .qq| Process" alt='' border='0'>
									</a>\n|;
		}

	}

	return $this_events_string;
}

############################################################################################
############################################################################################
#	Function: order_paid_total

#   	Es: Obtiene los montos totales de pago
#       En: Gets the total payment amounts
#
#       Created on: 12/08/15  13:11:25 By Jonathan Alcantara
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub order_total_paid {
    ### Orders Totals
    my ($id_orders) = @_;
    my $sql = "SELECT 
        SUM(Tax + ShpTax)AS TotalTax,
        SUM(SalePrice)AS OrderNet,
        SUM(Discount)AS Discount,
        SUM(Shipping)AS Shipping,
        SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal
        FROM sl_orders_products
        WHERE ID_orders = '".$id_orders."' AND Status NOT IN ('Inactive','Order Cancelled');";
    my ($sth) = &Do_SQL($sql);
    #&cgierr("sql= ".$sql);
    return my ($tot_tax,$ordernet,$discount,$shipping,$total_order) = $sth->fetchrow();
}

############################################################################################
############################################################################################
#	Function: order_total_products_services

#   	Es: Obtiene el total de productos incluyendo servicios
#       En: Gets the total of products including services
#
#       Created on: 12/08/15  13:11:25 By Jonathan Alcantara
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub order_total_products_services {
    my ($id_orders)= @_;

    my $sth = &Do_SQL("
        SELECT COUNT(*) AS totalProducts
        FROM sl_orders_products
        WHERE sl_orders_products.id_orders=".$id_orders." 
        AND sl_orders_products.Status IN ('Active','Exchange','ReShip');");
    my ($totalProducts) = $sth->fetchrow_array();

    return $totalProducts;
}

############################################################################################
############################################################################################
#	Function: order_total_services

#   	Es: Obtiene el total de servicios
#       En: Gets the total services
#
#       Created on: 12/08/15  13:11:25 By Jonathan Alcantara
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub order_total_services {
    my ($id_orders)= @_;

    my $sth = &Do_SQL(
        "SELECT COUNT(*) AS totalServices
		FROM sl_orders_products
		WHERE sl_orders_products.id_orders='".$id_orders."' 
		AND (sl_orders_products.ID_products >= 600000000 OR sl_orders_products.Related_ID_products >= 600000000)
		AND (sl_orders_products.ID_products < 700000000 OR sl_orders_products.Related_ID_products < 700000000) 
		AND sl_orders_products.Status IN ('Active','Exchange','Reship');"
	);
    my ($totalServices) = $sth->fetchrow_array();

    return $totalServices;
}

#############################################################################
#############################################################################
#   Function: validate_express_delivery
#
#       Es: Valida si un CP aplica para Express Delivery
#       En: Validate ZipCode to Express Delivery
#
#
#    Created on: 24/09/2015  16:03:10
#
#    Author: Jonathan Alcantara Martinez
#    Modifications:
#
#        -
#
#   Parameters:
#
#       -
#
#   See Also:
#
sub validate_express_delivery {
#############################################################################
#############################################################################
	
	my ($shp_zip) = @_;
	my $sql = "
		SELECT IF(COUNT(DISTINCT sl_zipcodes.ID_zipcodes)>0, 1,0)AS express_delivery
		FROM sl_zipcodes
		INNER JOIN sl_zones 
			ON sl_zones.ID_zones = sl_zipcodes.ID_zones
			AND sl_zones.ExpressShipping = 'Yes'
			AND sl_zones.`Status` = 'Active'
		WHERE sl_zipcodes.ZipCode = '".$shp_zip."'
		AND sl_zipcodes.`Status` = 'Active';
	";
	my ($sth) = &Do_SQL($sql);
	my ($express_delivery) = $sth->fetchrow();
	return $express_delivery;
}

#############################################################################
#############################################################################
#   Function: get_invoice_data
#
#       Es: Genera hash %in y %va para impresion de invoices
#       En: Generates %in and %va for invoice print
#
#
#    Created on: 01/18/2016
#
#    Author: _RB_ 
#
#    Modifications:
#    
#    				
#
#
#   Parameters:
#
#      - All $in{}
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		- opr_invoices
#
sub get_invoice_data {
#############################################################################
#############################################################################
#
	my ($sth_inv_type) = &Do_SQL("
		SELECT i.invoice_type
		FROM cu_invoices i
		WHERE i.ID_invoices = ". $in{'id_invoices'} .";");
	my $rec_inv_type = $sth_inv_type->fetchrow_hashref();
	
	if ($rec_inv_type->{'invoice_type'} eq 'egreso') {
		my ($sth) = &Do_SQL("
			SELECT DISTINCT cp.ID_orders ID_orders
			FROM cu_invoices_lines il
			INNER JOIN sl_creditmemos_payments cp ON cp.ID_creditmemos = il.ID_creditmemos
			WHERE il.ID_invoices = ". $in{'id_invoices'} ." ;"
		);
		my $rec = $sth->fetchrow_hashref();
		$in{'id_order'} = $va{'id_order'} = $rec->{'ID_orders'};
	} elsif ($rec_inv_type->{'invoice_type'} eq 'ingreso') {
		my ($sth) = &Do_SQL("
			SELECT op.ID_orders ID_orders
			FROM cu_invoices_lines il
			INNER JOIN sl_orders_products op ON op.ID_orders_products = il.ID_orders_products
			WHERE il.ID_invoices = ". $in{'id_invoices'} ." 
			GROUP BY op.ID_orders;"
		);
		my $rec = $sth->fetchrow_hashref();
		$in{'id_order'} = $va{'id_order'} = $rec->{'ID_orders'};
	}
	my ($sth) = &Do_SQL("SELECT ID_orders,ID_orders_alias,Pterms,
						shp_Address1,shp_Address2,shp_Address3,
						shp_Urbanization,shp_City,shp_State,shp_Zip, Ptype 
			    FROM sl_orders WHERE ID_orders = '". $va{'id_order'} ."';");
	my $rec=$sth->fetchrow_hashref;
			
	$va{'id_order_alias'} = $rec->{'ID_orders_alias'};
	$va{'ptype'} = $rec->{'Ptype'};
	#$va{'credit_days'} = $rec_terms->{'CreditDays'};
	#$va{'terms'} = $rec->{'Pterms'};

	my ($sth) = &Do_SQL("
		SELECT IFNULL(p.CapDate, '') CapDate
		FROM sl_orders_payments p
		WHERE 1
		AND p.ID_orders = ". $va{'id_order'} ."
		AND p.`Status` = 'Approved'
		ORDER BY p.ID_orders_payments 
		DESC LIMIT 1;
	");
	my ($cap_date) = $sth->fetchrow();

	$va{'cap_date'} = $in{'cap_date'} = $cap_date;

	my ($sth) = &Do_SQL("SELECT Phone1, Phone2, CellPhone FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE ID_orders = '". $va{'id_order'} ."';");
	my ($phone1, $phone2, $cellphone) = $sth->fetchrow();
	
	$va{'phone'} = 'Tel: ';

	if ($phone1 ne '') {
		$va{'phone'} .= $phone1;
	} elsif ($phone2 ne ''){
		$va{'phone'} .= $phone2;
	} elsif ($cellphone ne '') {
		$va{'phone'} .= $cellphone;
	} else {
		$va{'phone'} .= 'Sin numero telefonico.';
	}

	my ($sth) = &Do_SQL("SELECT Phone1, Phone2, CellPhone FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE ID_orders = '". $va{'id_order'} ."';");
	my ($phone1, $phone2, $cellphone) = $sth->fetchrow();
	
	$va{'phone'} = 'Tel: ';

	if ($phone1 ne '') {
		$va{'phone'} .= $phone1;
	} elsif ($phone2 ne ''){
		$va{'phone'} .= $phone2;
	} elsif ($cellphone ne '') {
		$va{'phone'} .= $cellphone;
	} else {
		$va{'phone'} .= 'Sin numero telefonico.';
	}
	
	##############################################################################################################
	my ($sth_invoices) = &Do_SQL("SELECT * 
			    FROM cu_invoices WHERE ID_invoices = '". $in{'id_invoices'} ."';");
	my $rec_invoices = $sth_invoices->fetchrow_hashref();
	
	$va{'expediter_fregimen'} = $rec_invoices->{'expediter_fregimen'};
	$va{'expediter_fregimen'} =~ s/\\n/<br>/g;
	$va{'street'} = $rec_invoices->{'customer_shpaddress_street'};
	$va{'urbanization'} = $rec_invoices->{'customer_shpaddress_urbanization'};
	$va{'state'} = $rec_invoices->{'customer_shpaddress_state'};
	$va{'num'} = $rec_invoices->{'customer_shpaddress_num'};
	$va{'district'} = $rec_invoices->{'customer_shpaddress_district'};
	$va{'city'} = $rec_invoices->{'customer_shpaddress_city'};
	$va{'num2'} = $rec_invoices->{'customer_shpaddress_num2'};
	$va{'zipcode'} = $rec_invoices->{'customer_shpaddress_zipcode'};
	$va{'country'} = $rec_invoices->{'customer_shpaddress_country'};
	$va{'batch'} = $rec_invoices->{'batch_num'};
	$va{'serial'} = $rec_invoices->{'doc_serial'};
	$va{'exchange_receipt'} = $rec_invoices->{'exchange_receipt'};
	$va{'conditions'} = $rec_invoices->{'conditions'};
	$va{'credit_days'} = $rec_invoices->{'credit_days'};
	$va{'folio'} = $rec_invoices->{'doc_serial'}.'-'.$rec_invoices->{'doc_num'};
	$va{'uuid'} = $rec_invoices->{'xml_uuid'};
	$va{'xml_certificacion'} = $rec_invoices->{'xml_fecha_certificacion'};
	$va{'metodo'} = $rec_invoices->{'payment_method'};
	$va{'regimen'} = $rec_invoices->{'expediter_fregimen'};
	$va{'results'} = '';


	$va{'label'} = $rec_invoices->{'invoice_type'} == 'ingreso' ? 'Factura' : 'Nota de Crédito';


	my $pdf_name = $rec_invoices->{'doc_serial'}.'_'.$rec_invoices->{'doc_num'};
	my $link_pdf = "/cfdi/pages/cfdi/cfdi_doc.php?f=".$pdf_name.".pdf";
		
	if ($rec_invoices->{'Status'} eq 'Certified') {
		$va{'link_to_pdf'} = qq|<a href='$link_pdf' target='_blank'><img src='/cfdi/common/img/pdf.gif' title='PDF' alt='PDF' border='0'></a>
|;
	}
	##############################################################################################################
	
	
	my ($sth) = &Do_SQL("SELECT COUNT(*)
			    FROM cu_invoices_lines WHERE ID_invoices = '$in{'id_invoices'}'");	
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		
		my($subtotal);
		my ($sth) = &Do_SQL("SELECT op.ID_products, il.* 
				FROM cu_invoices_lines il
				LEFT JOIN sl_orders_products op ON op.ID_orders_products = il.ID_orders_products
				WHERE il.ID_invoices = '". $in{'id_invoices'} ."';");
		my $cadparts="";
		my $format_product = "";
		while ($rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_products'} and $rec->{'ID_products'} > 0) {
				$cadparts="";
				$format_product = &format_sltvid($rec->{'ID_products'});
				my ($sthDetail) = &Do_SQL("
					SELECT sk.UPC, spa.ID_parts, spa.Qty, pa.Model
					FROM sl_skus_parts spa
					LEFT JOIN sl_parts pa ON pa.ID_parts = spa.ID_parts
					LEFT JOIN sl_skus sk ON sk.ID_sku_products = spa.ID_parts + 400000000
					WHERE spa.ID_sku_products = ".$rec->{'ID_products'}.";"
				);
				while ($recDetail = $sthDetail->fetchrow_hashref) {

					$d = 1 - $d;
					$va{'reference_id'} = $rec->{'UPC'} if !$va{'reference_id'};

					$cadparts.= "<tr>\n";
					$cadparts.= "	<td valign='top' align='center'></td>\n
						<td valign='top' align='center'></td>\n
						<td valign='top' align='center'><span style='font-size:xx-small;'>".$recDetail->{'UPC'}." | </span></td>\n
						<td valign='top' align='center'><span style='font-size:xx-small;'>".$recDetail->{'Qty'}." x ".&format_sltvid(400000000+$recDetail->{'ID_parts'}). "</span></td>\n
					    <td valign='top'><span style='font-size:xx-small;'>".$recDetail->{'Model'}."</span></td>\n
					    <td valign='top'></td>\n
						<td valign='top'></td>\n
					    <td valign='top'></td>\n
					  </tr>\n";
				}
				my $tmp_cadparts = '<table border=0>'.$cadparts.'</table>';
				$cadparts = $tmp_cadparts;
			} else {
				$cadparts = "";
				$format_product = "";
			}
			$va{'results'} .= qq| <tr bgcolor='$c[$d]'><td>
						<span style="font-size:xx-small;">$rec->{'quantity'}</span>
						</td>
						<td style="border-left:1px solid #333333;">
							<span style="font-size:xx-small;">$rec->{'measuring_unit'}</span>
						</td>
						<td style="border-left:1px solid #333333;">
							<span style="font-size:xx-small;">|.$format_product.qq|</span>
							<span style="font-size:xx-small;">
								$rec->{'reference_id'} $rec->{'description'}
								<br>
									$cadparts
							</span>
							<span style="font-size:xx-small;">$rec->{'customs'}</span>
							<span style="font-size:xx-small;">$rec->{'customs_broker'}</span>
						</td>
						<td style="border-left:1px solid #333333;" align=right valign=top>
							<span style="font-size:xx-small;">|.&format_price($rec->{'unit_price'}).qq|</span>
						</td>
						<td style="border-left:1px solid #333333;" align=right valign=top>
							<span style="font-size:xx-small;">|.&format_price($rec->{'amount'}).qq|</span>
						</td>
						</tr>|;			
			$subtotal += $rec->{'amount'};
		}

		my ($total_taxes,$tax_name, $tax);
		my ($sth) = &Do_SQL("SELECT tax_name,tax_rate, SUM(tax) AS TotalV
					FROM cu_invoices_lines
					WHERE ID_invoices = '". $in{'id_invoices'} ."'
					GROUP BY tax_name,tax_rate
					ORDER BY tax_rate ASC");			
		while ($rec = $sth->fetchrow_hashref){
			$tax_name .= $rec->{'tax_name'}." ".($rec->{'tax_rate'}*100)."% <BR>";
			$tax      .= $rec->{'TotalV'}."<BR>";
			$total_taxes += $rec->{'TotalV'};
		}

		$va{'total'}    	= &format_price($subtotal - $in{'discount'});
		$va{'gran_total'} 	= &format_price(($subtotal - $in{'discount'}) + $total_taxes);
		$va{'subtotal'} 	= &format_price($subtotal);		
		$in{'discount'} 	= &format_price($in{'discount'});			
		$va{'tax_names'} 	= $tax_name;
		$va{'taxes'} 	 	= $tax;
		$va{'taxes_total'}  = &format_price($total_taxes);
	}else{
		$va{'results'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;		
	}	
	#my ($sth) = &Do_SQL("SELECT OrderNotes 
	#		    FROM cu_invoices_lines 
	#		    left join sl_orders using(ID_Orders)
	#		    WHERE ID_invoices = '". $in{'id_invoices'} ."' GROUP BY ID_orders;");
	#my $rec_notes = $sth->fetchrow_hashref();

	my ($sth) = &Do_SQL("
		SELECT o.shp_Notes
		FROM sl_orders o
		WHERE o.ID_orders = ".$va{'id_order'}."
		;"
	);
	my $rec_notes = $sth->fetchrow_hashref();
	$va{'ordernotes'} = $rec_notes->{'shp_Notes'};

	if (!$in{'customer_fname'}){

		my ($sth) = &Do_SQL("SELECT CONCAT(FirstName, ' ', LastName1, ' ', LastName2) FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE ID_orders = '". $va{'id_order'} ."';");
		my ($cname) = $sth->fetchrow();
		$in{'customer_fname'} = $cname;

		&Do_SQL("UPDATE cu_invoices SET customer_fname = '". &filter_values($cname) ."' WHERE ID_invoices = '". $in{'id_invoices'} ."';");

	}

}


#############################################################################
#############################################################################
#   Function: get_paid_unpaid
#       Es: Devuelve el monto que queda sin pagar de una orden en particular
#       En: Returns the amount left unpaid a particular order
#
#    Created on: 24/032016 13:56
#
#    Author: HC
#
#    Modifications:
#        -
#
#   Parameters:
#       - id_orders
#
#   See Also:
#
sub get_paid_unpaid {
#############################################################################
#############################################################################

	my ($id_orders) = @_;
	my $sql = "	SELECT 
					IFNULL((
						SELECT SUM(Amount) FROM sl_orders_payments 
						WHERE 
							ID_orders = '". $id_orders ."' 
							AND Captured = 'Yes' 
							AND CapDate IS NOT NULL 
							AND CapDate != '0000-00-00'
							AND Status != 'Cancelled'
					),0) AS paid,
					IFNULL((
						SELECT SUM(Amount) FROM sl_orders_payments 
						WHERE 
							ID_orders = '". $id_orders ."' 
							AND ( Captured != 'Yes' OR Captured is null ) 
							AND ( CapDate is null OR CapDate ='0000-00-00')
							AND Status != 'Cancelled'
					),0) AS unpaid,	
					IFNULL((	
						SELECT SUM(SalePrice - Discount + Shipping + Tax + ShpTax) FROM sl_orders_products 
						WHERE 
							ID_orders = '". $id_orders ."' 
							AND Status NOT IN ('Inactive','Order Cancelled')
					),0) AS total_products;";

	my ($sth) = &Do_SQL($sql);
	my ($paid, $unpaid, $total_products) = $sth->fetchrow();

	my $difference = round(abs(($paid+$unpaid) - $total_products), 2);
	my %result;

	$result{'correct'} 				= ($difference <= 1) ? 1 : 0;
	$result{'paid'} 				= round($paid, 2);
	$result{'calculated_unpaid'} 	= round($total_products - $paid, 2);
	$result{'registered_unpaid'} 	= round($unpaid, 2);
	$result{'total'} 				= round($total_products, 2);
	$result{'string'}				= $sql;

	return \%result;
}


#############################################################################
#############################################################################
#   Function: apply_advances
#
#       Es: apply_advances
#       En: 
#
#
#    Created on: 
#
#    Author: HC
#
#    Modifications:
#		- 
#
#   Parameters:
#      - 
#
#  Returns:
#      - 
#
#   See Also:
#
#
sub apply_customers_advances{
#############################################################################
#############################################################################

	my ($id_customers_advances, $total_applied, $id_customers_advances_payments, $id_orders_payments, $total_amount, $eff_date ) = @_;

	my $err = 0;
	my $add_msg = '';
	my $this_res = 0;
	my $message;

	my $eff_date = 'NULL';

	if ($in{'eff_date'} and $in{'eff_date'} ne "") {
		$eff_date = "'".$in{'eff_date'}."'";
	}

	# Obtiene el monto y la orden sobre la que se aplicara esta porción del Advance
	my ($sth) = &Do_SQL("SELECT Amount, ID_orders, Status 
						FROM sl_customers_advances_payments 
						WHERE ID_customers_advances_payments = ". $id_customers_advances_payments .";");
	my ($amount_to_apply, $id_orders, $status_customers_advances) = $sth->fetchrow();
	$amount_to_apply = round($amount_to_apply,2);

	############ Validacion Currency / Exchange Rate
	my $currency_exchange = 1;
	my $idexr = 0; 
	my ($sth) =  &Do_SQL("SELECT 
							B.Currency
							, CA.Exchangerates
							, B.ID_accounts	
						FROM 
							sl_banks_movrel BV INNER JOIN sl_customers_advances CA ON BV.tableid = CA.ID_customers_advances AND tablename = 'customers_advances'			 
						INNER JOIN sl_banks_movements BM USING(ID_banks_movements)  
						INNER JOIN sl_banks B USING(ID_banks)
						WHERE 
							ID_customers_advances = '". $id_customers_advances ."'; ");
	( $this_customers_advances_currency, $ca_exchangerates, $ida_banks) = $sth->fetchrow();

	if( $cfg{'acc_default_currency'} ne '' and uc($this_customers_advances_currency) ne uc($cfg{'acc_default_currency'}))
	{

		##
		## Si la moneda de este Advance no es igual a la moneda por default del sistema, extraemos el tipo de cambio del pedido en la venta
		##

		#&cgierr("$cfg{'acc_default_currency'} ne '' and uc($this_customers_advances_currency) ne uc($cfg{'acc_default_currency'})");
		my ($sth) =  &Do_SQL("	SELECT ID_exchangerates, exchange_rate 
								FROM sl_exchangerates 
								WHERE 
									UPPER(Currency) = '". uc($this_customers_advances_currency) ."' 
									AND Date_exchange_rate <= 
									(
										SELECT PostedDate FROM sl_orders WHERE ID_orders = ". $id_orders ."	
									)
								ORDER BY Date_exchange_rate DESC LIMIT 1;");


		($idexr, $currency_exchange) = $sth->fetchrow();
		$currency_exchange = 0 if !$currency_exchange;

		if(!$currency_exchange){
			$add_msg .= qq|<br>No Exchange Rate Found|;
			++$err;
		}

	}

	my ($amounts) = &get_paid_unpaid($id_orders);

	if( !$amounts->{'correct'} ){
		$add_msg .= '<br>'.&trans_txt('opr_customers_advances_orders_error').'/'.$id_orders;
		$err++;
	}

	if($status_customers_advances ne 'New'){
		$add_msg .= '<br>'.&trans_txt('opr_customers_advances_already_applied');
		$err++;
	}

	# Verifica que no se supere el monto total del Advances
	if(($total_applied + $amount_to_apply) > ($total_amount + 1) ){
		$add_msg .= '<br>'.&trans_txt('opr_customers_advances_exceed_advances') . qq|($total_applied + $amount_to_apply) > $total_amount|;
		$err++;		
	}


	# Verifica que no se aplique un monto 0 sobre una orden
	if($amount_to_apply <= 0){
		$add_msg .= '<br>'.&trans_txt('opr_customers_advances_zero_amount');
		$err++;		
	}

	# Verifica que el total del monto de los pagos resgistrados y en condiciones de ser pagados no sea menor al monto que predente acreditarse
	if( $amounts->{'calculated_unpaid'} < $amount_to_apply ){
		$add_msg .= '<br>'.&trans_txt('opr_customers_advances_exceed_payment');
		$add_msg .= '<br>'. $amounts->{'calculated_unpaid'} .' < '. $amount_to_apply; #$amounts->{'string'} . '<br>' .
		$err++;		
	}

	# Si el monto de lo que se desea aplicar es mayor a cero y tambien es menor o igual a lo que falta por pagar en la orden
	if(!$err){
	
		my $flag_max_amount = 0; my $flag_acc = 0; my $str_acc;

		## Inicializa la transaccion en la funcion que lo llama
		my $amount_to_apply_final = round($amount_to_apply,2);
		my $i = 0; my $applied_payment = 0; my $new_applied_payment = 0;

		do{

			my $modsql = '';
			if($id_orders_payments){ $modsql = " AND ID_orders_payments = ". $id_orders_payments; $id_orders_payments = 0;  }
			++$i;
			my ($sth_p) = &Do_SQL("SELECT ID_orders_payments, ABS(Amount) 
									FROM sl_orders_payments 
									WHERE ID_orders = '". $id_orders ."' ". $modsql ." 
										AND ROUND(Amount, 2) > 0.1 
										AND (Captured IS NULL OR Captured = 'No' OR Captured = '') 
										AND (CapDate IS NULL OR CapDate = '0000-00-00') 
										AND Status IN('Approved','Financed','Denied','Pending','Insufficient Funds') 
									ORDER BY Amount - ". $amount_to_apply .", ID_orders_payments, Paymentdate ;");
			my ($this_id, $total_amount) = $sth_p->fetchrow();

			if($this_id){
				
				$applied_payment = $this_id;
				#########
				######### 2.1.1) Order has Payments to Pay
				#########

				if($amount_to_apply >= $total_amount){

					#########
					######### 2.1.1.1) Customer Advance Amount > Payment Amount
					#########

					############ Accounting Key Point
					my ($sth) = &Do_SQL("SELECT Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."';");
					my ($ctype) = $sth->fetchrow();
					@params = (	$id_customers_advances, $id_orders, $applied_payment, $total_amount, $ca_exchangerates, $currency_exchange);
					my ($this_acc, $this_acc_str) = &accounting_keypoints('customer_deposit_apply_' . $ctype, \@params);
					if ($this_acc){  $str_acc .= qq| \| | . $this_acc_str; $flag_acc++; }

					&Do_SQL("UPDATE sl_orders_payments SET Status = 'Approved', Paymentdate = CURDATE(), CapDate = CURDATE(), Captured = 'Yes', AuthCode = 'CA-". $id_customers_advances ."', Reason = 'Sale', AccountingDate = ".$eff_date." WHERE ID_orders_payments = '". $this_id ."';");
					$amount_to_apply -= round($total_amount,2);

				}else{

					#########
					######### 2.1.1.2) Payment Amount greater than Customer Advance
					#########
					&Do_SQL("UPDATE sl_orders_payments SET Amount = (Amount - ". $amount_to_apply ."), AccountingDate = ".$eff_date." WHERE ID_orders_payments = '". $this_id ."';");
					my (%overwrite) = ('amount' => $amount_to_apply, 'pmtfield8' => '1' ,'authcode' => 'CA-' . $id_customers_advances, 'authdatetime' => 'NOW()', 'captured' => 'Yes', 'capdate' => 'CURDATE()', 'status' => 'Approved', 'reason' => 'Sale');
					$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '". $this_id ."'", "", "", %overwrite);

					############ Accounting Key Point
					my ($sth) = &Do_SQL("SELECT Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."';");
					my ($ctype) = $sth->fetchrow();
					@params = (	$id_customers_advances, $id_orders, $applied_payment, $amount_to_apply, $ca_exchangerates, $currency_exchange);
					my ($this_acc, $this_acc_str) = &accounting_keypoints('customer_deposit_apply_' . $ctype, \@params);
					if ($this_acc){  $str_acc .= qq| \| | . $this_acc_str; $flag_acc++; }
					
					$amount_to_apply = 0;

				}

			}else{
				
				#########
				######### 2.1.2) Order Has Not more Payments to Pay
				#########
				if($amount_to_apply < 1) {

					my (%overwrite) = ('amount' => $amount_to_apply, 'pmtfield8' => '1' ,'authcode' => 'CA-' . $id_customers_advances, 'authdatetime' => 'NOW()', 'captured' => 'Yes', 'capdate' => 'CURDATE()', 'status' => 'Approved', 'reason' => 'Sale');
					$new_applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '". $id_orders ."' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
					&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '". $new_applied_payment ."';");

					############ Accounting Key Point
					my ($sth) = &Do_SQL("SELECT Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."';");
					my ($ctype) = $sth->fetchrow();
					@params = (	$id_customers_advances, $id_orders, $new_applied_payment, $amount_to_apply, $ca_exchangerates, $currency_exchange);
					my ($this_acc, $this_acc_str) = &accounting_keypoints('customer_deposit_apply_' . $ctype, \@params);
					if ($this_acc){  $str_acc .= qq| \| | . $this_acc_str; $flag_acc++; }

				}else{

					$flag_max_amount = 1;

				}
				$amount_to_apply = 0;

			}

		}while($amount_to_apply > 0 or $i > 20);
		# Especifica que esta porción del Advance ya fue aplicada
		&Do_SQL("UPDATE sl_customers_advances_payments SET ID_orders_payments = '". $applied_payment ."', Status = 'Applied' WHERE ID_customers_advances_payments = '". $id_customers_advances_payments ."';");
		

		##
		### Final Validations
		##
		my ($amounts) = &get_paid_unpaid($id_orders);

		if( !$amounts->{'correct'} ){ 

			## Applied Amounts incorrect
			++$this_res;
			$message = '<br>'.&trans_txt('opr_customers_advances_orders_error').'/'.$id_orders;
		
		}elsif($flag_acc){

			## Accounting Problems | End Transaction
			++$this_res;
			$message = &trans_txt('acc_general') . ' ' . $str_acc;
			

		}elsif($flag_max_amount){

			## El pedido no tenia el monto que se queria aplicar
			++$this_res;
			$message = &trans_txt('opr_customers_advances_ordermaxamount');

		}else{

			## All OK
			$message = 'ok';

		}

	}else{

		++$this_res;
		$message = &trans_txt('opr_customers_advances_applied_err') . $add_msg ;

	}

	return ($this_res, $message);
}


#############################################################################
#############################################################################
#   Function: set_fake_delivery_adjustment
#
#       Es: Genera un ajuste de inventario derivado de una entrega pirata
#       En: 
#
#
#    Created on: 04/12/2016
#
#    Author: _RB_ 
#
#    Modifications:
#    
#    	Last Time Modified by _RB_:
#
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		</cgi-bin/mod/admin/admin.fin2.cgi &fin_enter_cod>
#
sub set_fake_delivery_adjustment {
#############################################################################
#############################################################################

	my ($id_orders) = @_;

	return 0;

}


#############################################################################
#############################################################################
#   Function: get_customers_ar_debtcancellation
#				
#       Es: Devuelve invoices para posible cancelacion de deuda
#       En: 
#
#
#    Created on: 02/12/2017  12:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - List of invoices able to debt cancellation
#
#   See Also:
#
#	</cgi-bin/common/subs/sub.func.html.cgi -> func_customers_ar>>
#
sub get_customers_ar_debtcancellation {
#############################################################################
#############################################################################

	my ($this_type) = @_;

	$cfg{'ar_maxamount_cancellation'} = 1 if !$cfg{'ar_maxamount_cancellation'};
	my $query = "SELECT 
					cu_invoices.ID_invoices
	  				, sl_orders.ID_orders
	  				, CONCAT(doc_serial,doc_num)
			    	, CONCAT( MONTHNAME(xml_fecha_certificacion), ' ', YEAR(xml_fecha_certificacion))
					, invoice_total
					, AmtDue 
				FROM cu_invoices_lines INNER JOIN cu_invoices 
					ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
				INNER JOIN 
				(
					SELECT 
						sl_orders.ID_orders
						, SUM(Amount) AS AmtDue 
					FROM 
						sl_orders INNER JOIN sl_orders_payments 
						ON sl_orders.ID_orders = sl_orders_payments.ID_orders
					WHERE 
						sl_orders.ID_customers = ". $in{'id_customers'} ."
						AND sl_orders.Status NOT IN ('Cancelled','Void','System Error')
						AND sl_orders_payments.Status NOT IN ('Void','Order Cancelled','Cancelled')
						AND (CapDate IS NULL OR CapDate = '0000-00-00')
					GROUP BY 
						sl_orders.ID_orders
					HAVING
						AmtDue > 0 
						AND AmtDue <= ". $cfg{'ar_maxamount_cancellation'} ."
				)sl_orders
				ON cu_invoices_lines.ID_orders = sl_orders.ID_orders
				WHERE 
					cu_invoices.Status = 'Certified'
					AND invoice_type = 'ingreso'
				GROUP BY 
					cu_invoices.ID_invoices
					, sl_orders.ID_orders
				ORDER BY 
					CONCAT(doc_serial,doc_num)
					, invoice_total
					, AmtDue ;";

	if($this_type eq 'query'){

		## Returns only the query
		return $query;

	}

	my ($sth) =  &Do_SQL($query);
	my $numrows = $sth->rows();

	if($this_type eq 'rows'){

		## Return only the count of invoices
		return $numrows;

	}

}

#############################################################################
#############################################################################
#   Function: export_info_for_transfer_invoice
#
#       Es: Exporta los datos de la orden a la tabla cu_invoices y generar cfdi de traslado
#       
#
#
#    Created on: 24/07/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#      <>
#
sub export_info_for_transfer_invoice {
#############################################################################
#############################################################################
	my ($id_orders)	= shift;
	my ($id_invoices);

	# Order Basic Info
	my ($sth_order_info) = &Do_SQL("SELECT sl_orders.ID_customers, sl_orders.ID_zones FROM sl_orders WHERE ID_orders = ".$id_orders.";");
	$rec_order_info = $sth_order_info->fetchrow_hashref;
	
	## Zone in Borde Zone?
	my $id_zones = $rec_order_info->{'ID_zones'};
	$sql = "SELECT IF(COUNT(*)>0,1,0) AS 'BorderZone' FROM sl_zones WHERE BorderZone='Yes' AND ID_zones='".$id_zones."'";
	my ($sth_borderzone) = &Do_SQL($sql);
	my ($isborderzone) = $sth_borderzone->fetchrow_array;

	## Transfer Invoice is only for Zipcodes in Border Zone
	if ($isborderzone) {

		my $id_customers = $rec_order_info->{'ID_customers'};
		my ($sth_cuad) = &Do_SQL("SELECT COUNT(*), IFNULL( ID_customers_addresses, 0 ) ID_customers_addresses, Payment_Method FROM cu_customers_addresses WHERE id_customers='$id_customers' AND PrimaryRecord='Yes' LIMIT 1");
		my ($has_fiscal_data, $id_customers_addresses, $payment_method) = $sth_cuad->fetchrow_array;

		my ($sth) = &Do_SQL("SELECT PersonalID, b.gln as gln, c.GLN as glnshp, Code, Alias 
		FROM sl_orders a
		LEFT JOIN sl_customers b USING(ID_customers) 
		LEFT JOIN cu_customers_addresses c ON a.ID_customers_addresses=c.ID_customers_addresses 
		WHERE ID_orders = '$id_orders' ;");
		($VendorID, $gln, $glnshp, $shpcode, $shpalias) = $sth->fetchrow();

		my ($id_customer_generic);


		if($cfg{'validate_customer_payment'}){
			$generate_payment_invoice = &Do_SQL(qq|SELECT GeneratePaymentInvoice FROM cu_customers_addresses WHERE cu_customers_addresses.PrimaryRecord = 'Yes' AND ID_customers = '$id_customers' LIMIT 1|)->fetchrow();
			if(!$generate_payment_invoice){
				$has_fiscal_data = 0;
			}	
		}

		## 2) Generic Invoice
		if(!$has_fiscal_data) {

			#obtengo el tipo de cliente
			my ($sth) = &Do_SQL("SELECT Ptype, Type, shp_Zip, PersonalID FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			($order_type, $ctype, $shp_zip, $VendorID) = $sth->fetchrow();

			#revisar si ese tipo de cliente tiene un parametro con un id definido de customer generico
			if($cfg{'id_customer_generic_'.lc($ctype)} and int($cfg{'id_customer_generic_'.lc($ctype)}) > 0) {
				$id_customer_generic = int($cfg{'id_customer_generic_'.lc($ctype)});
				
				# revisamos si el id es valido 
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE ID_customers = '$id_customer_generic';");
				($is_valid_id_customer) = $sth->fetchrow_array();

			}

		}

		## If custom invoice, change customer_generic for real id_customers
		($id_customers_addresses) ? ($id_customer_generic = $id_customers) : ($id_customer_generic = $id_customer_generic);

		# Obtener datos de Company 
		my ($sth_ci) = &Do_SQL("SELECT * FROM cu_company_legalinfo WHERE PrimaryRecord = 'Yes'");
		$rec_company_legal = $sth_ci->fetchrow_hashref;
		
		my ($sth_cr) = &Do_SQL("SELECT * FROM cu_company_addresses WHERE PrimaryRecord = 'Yes'");
		$rec_company_addr = $sth_cr->fetchrow_hashref;

		## Obtener datos fiscales del cliente
		### Para Cliente solo si es $id_customers_addresses
		#	2.1. Sacar customers_addresses LEFT JOIN legalinfo  - Primary Record para Datos Fiscales
		#	2.2. sacar customers_addresses solo donde el ID = $id_customers_addresses
		if($has_fiscal_data){
			my ($sth_cr) = &Do_SQL("SELECT IF(RFC IS NULL , 'XAXX010101000' , RFC) AS RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
						FROM cu_customers_addresses
						LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
						WHERE ID_customers_addresses = '".$id_customers_addresses."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
		}elsif($is_valid_id_customer) {
			my ($sth_cr) = &Do_SQL("SELECT RFC, IF(sl_customers.company_name IS NULL,'GENERICO',sl_customers.company_name) AS lname, cu_customers_addresses.*
				FROM cu_customers_addresses
				LEFT JOIN sl_customers  ON cu_customers_addresses.ID_customers = sl_customers.ID_customers
				WHERE sl_customers.ID_customers = '".$id_customer_generic."';");
			$rec_custom_info = $sth_cr->fetchrow_hashref;
		}

		## Place Consignment
		my $place_consignment = $rec_company_addr->{'City'}.', '.$rec_company_addr->{'State'};
		my $invoice_type = 'traslado';

		# Detalle de la orden
		my ($sth_order_detail) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders = '$id_orders';");
		$rec_order_detail = $sth_order_detail->fetchrow_hashref;
		
		## Definicion del campo payment_method
		## Para TMK/MOW Efectivo -> Referenced Deposit o COD y Tarjeta de Credito -> Credit-Card
		if ($rec_order_detail->{'Ptype'} eq 'Credit-Card'){
			$payment_method = 'Tarjeta de Credito';
		}
		if ($rec_order_detail->{'Ptype'} eq 'Referenced Deposit'){
			$payment_method = 'Efectivo';
		}
		if ($rec_order_detail->{'Ptype'} eq 'COD'){
			$payment_method = 'Efectivo';
		}
		
		## Como se requiere la Clave obtenemos su valor
		$sth = &Do_SQL("SELECT sl_vars_config.Code FROM sl_vars_config WHERE sl_vars_config.Command='sat_formadepago' AND sl_vars_config.Subcode='$payment_method';");
		my ($payment_method_code) = $sth->fetchrow();

		$payment_method_code = '99' unless($payment_method_code);

		if ($payment_method_code and ($has_fiscal_data or $is_valid_id_customer)) {

			my $id_invoices;
			
			#si es valido entonces grabamos sus datos en cu_invoices
			#pero primero revisamos si ya hay facturas de este cliente

			my $conditions = $rec_order_detail->{'Pterms'};

			my $credit_days = &load_name('sl_terms','Name',$conditions,'CreditDays');

			# Obtener los datos de direccion de envio
			my $has_shipping_data = ($rec_order_detail->{'ID_customers_addresses'} and int($rec_order_detail->{'ID_customers_addresses'}) != 0) ? $rec_order_detail->{'ID_customers_addresses'} : 0;
			if ($has_shipping_data) {
				my ($sth_shipping_data) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers_addresses = '".$rec_order_detail->{'ID_customers_addresses'}."';");
				$rec_shipping_data = $sth_shipping_data->fetchrow_hashref;
			}else{

				# Los Datos de envio deben ser tomados de la orden
				my ($sth_shipping_data) = &Do_SQL("SELECT  
						shp_Address1 as cu_Street
						,  '' as cu_Num
						,  '' as cu_Num2
						,  shp_Urbanization as cu_Urbanization
						,  '' as cu_District
						,  shp_City as cu_City
						,  shp_State as cu_State
						,  shp_Country as cu_Country
						,  shp_Zip as cu_Zip
						FROM sl_orders
						WHERE id_orders = '".$rec_order_detail->{'ID_orders'}."';");
				$rec_shipping_data = $sth_shipping_data->fetchrow_hashref;

				$add_sql_id_orders_alias_date = "ID_orders_alias_date=CURDATE(),";
			}

			# Datos de pago
			my $cpay = &load_name('sl_orders_payments','ID_orders',$id_orders,'PmtField3');
			($cpay) ? ($cpay = substr($cpay,-4)) : ($cpay = '');

			## Se valida si el cliente cuenta con la informacion de Cuenta Bancaria
			## Solicitan que se force si viene vacion al texto 'NO IDENTIFICADO'
			my $sth_digits = &Do_SQL("SELECT cu_customers_addresses.Account_Number FROM cu_customers_addresses WHERE cu_customers_addresses.ID_customers =	".$id_customers." AND cu_customers_addresses.PrimaryRecord='yes';");
			my ($account_number) = $sth_digits->fetchrow_array();
			$cpay = ($cpay eq '' and $account_number ne '')? substr($account_number,-4) : $cpay;
			$cpay = ($cpay eq '')? 'NO IDENTIFICADO' : $cpay;

			# Detalle de ultima factura
			my ($sth_last_invoice) = &Do_SQL("SELECT ID_invoices FROM cu_invoices WHERE ID_customers = '".$id_customer_generic."' ORDER BY ID_invoices DESC LIMIT 1;");
			$rec_last_invoice = $sth_last_invoice->fetchrow_hashref;
			

			my ($id_invoices);
			if (int($rec_last_invoice->{'ID_invoices'}) > 0) {				
				#Obtiene el tipo de moneda que corresponda al cliente

				my $order_currency = &load_name('sl_customers','ID_customers',$id_customers,'Currency');
				if(!$order_currency){
					$order_currency = 'MXP';
					$exchangerate = 1;
				}else{
					my $sth= &Do_SQL("select exchange_rate from sl_exchangerates where Currency='$order_currency' AND Date_exchange_rate=CURDATE()");	
					$exchangerate = $sth->fetchrow;

					$exchangerate = 1 if($order_currency eq $cfg{'acc_default_currency'});
					if ($order_currency eq 'US$'){
						$order_currency = 'USD';
					}elsif ($order_currency eq 'EU$'){
						$order_currency = 'EUR';
					}elsif ($order_currency eq 'CO$'){
						$order_currency = 'COLP';
					}else {
						$order_currency = 'MXP';
					}

				}

				if ($exchangerate eq ''){
					return &trans_txt('exchangerate_not_found'), "ERROR";
				}

				# Copiar datos de ultima factura
				$previous_invoice = &Do_SQL("SELECT ID_customers, payment_digits, total_taxes_detained, total_taxes_transfered, expediter_fcode, expediter_fname, expediter_fregimen, expediter_faddress_street, expediter_faddress_num, expediter_faddress_num2,  expediter_faddress_urbanization,  expediter_faddress_district,  expediter_faddress_city,  expediter_faddress_state, expediter_faddress_country, expediter_faddress_zipcode, expediter_address_street, expediter_address_num,  expediter_address_num2,  expediter_address_urbanization,  expediter_address_district,  expediter_address_city, expediter_address_state,  expediter_address_country,  expediter_address_zipcode,  customer_fcode,  customer_fname,  customer_address_street, customer_address_num,  customer_address_num2,  customer_address_urbanization,  customer_address_district,  customer_address_city, customer_address_state,  customer_address_country,  customer_address_zipcode,  xml_cfd,  xml_cfdi, xml_addenda,  uuid,  original_string, related_ID_invoices FROM cu_invoices WHERE ID_customers = '$id_customer_generic' ORDER BY date DESC LIMIT 1");
				my ($prv_ID_customers,$prv_payment_digits,$prv_total_taxes_detained,$prv_total_taxes_transfered,$prv_expediter_fcode,$prv_expediter_fname,$prv_expediter_fregimen,$prv_expediter_faddress_street,$prv_expediter_faddress_num,$prv_expediter_faddress_num2,$prv_expediter_faddress_urbanization,$prv_expediter_faddress_district,$prv_expediter_faddress_city,$prv_expediter_faddress_state,$prv_expediter_faddress_country,$prv_expediter_faddress_zipcode,$prv_expediter_address_street,$prv_expediter_address_num,$prv_expediter_address_num2,$prv_expediter_address_urbanization,$prv_expediter_address_district,$prv_expediter_address_city,$prv_expediter_address_state,$prv_expediter_address_country,$prv_expediter_address_zipcode,$prv_customer_fcode,$prv_customer_fname,$prv_customer_address_street,$prv_customer_address_num,$prv_customer_address_num2,$prv_customer_address_urbanization,$prv_customer_address_district,$prv_customer_address_city,$prv_customer_address_state,$prv_customer_address_country,$prv_customer_address_zipcode,$prv_xml_cfd,$prv_xml_cfdi,$prv_xml_addenda,$prv_uuid,$prv_original_string,$prv_related_ID_invoices) = $previous_invoice->fetchrow_array();
				
				$sth_invoice = &Do_SQL("
				INSERT INTO cu_invoices (ID_invoices,  ID_customers,    doc_date,  payment_type,  payment_method, payment_digits,  invoice_net,  invoice_total,  discount,  total_taxes_detained,  total_taxes_transfered,  currency,  currency_exchange,  invoice_type,  place_consignment,  expediter_fcode,  expediter_fname,  expediter_fregimen,  expediter_faddress_street,  expediter_faddress_num,  expediter_faddress_num2,  expediter_faddress_urbanization,  expediter_faddress_district,  expediter_faddress_city,  expediter_faddress_state,  expediter_faddress_country,  expediter_faddress_zipcode,  expediter_address_street,  expediter_address_num,  expediter_address_num2,  expediter_address_urbanization,  expediter_address_district,  expediter_address_city,  expediter_address_state,  expediter_address_country,  expediter_address_zipcode,  customer_fcode,  customer_fname,  customer_address_street,  customer_address_num,  customer_address_num2,  customer_address_urbanization,  customer_address_district,  customer_address_city,  customer_address_state,  customer_address_country,  customer_address_zipcode, customer_shpaddress_code, customer_shpaddress_alias, xml_cfd,  xml_cfdi,  xml_addenda,  uuid,  original_string,  related_ID_invoices,  ID_orders_alias,  Status, VendorID, customer_address_gln, customer_shpaddress_gln,  Date,  Time,  ID_admin_users, credit_days, conditions)
				values (NULL, '".$prv_ID_customers."',NOW(),'PAGO EN UNA SOLA EXHIBICION','".$payment_method_code."','".$prv_payment_digits."','0.00','0.00','".$rec_order_detail->{'OrderDisc'}."','".$prv_total_taxes_detained."','".$prv_total_taxes_transfered."','$order_currency','$exchangerate','".$invoice_type."','".$place_consignment."','".$prv_expediter_fcode."','".$prv_expediter_fname."','".$prv_expediter_fregimen."','".$prv_expediter_faddress_street."','".$prv_expediter_faddress_num."','".$prv_expediter_faddress_num2."','".$prv_expediter_faddress_urbanization."','".$prv_expediter_faddress_district."','".$prv_expediter_faddress_city."','".&filter_values($rec_company_addr->{'State'})."','".$prv_expediter_faddress_country."','".$prv_expediter_faddress_zipcode."','".$prv_expediter_address_street."','".$prv_expediter_address_num."','".$prv_expediter_address_num2."','".$prv_expediter_address_urbanization."','".$prv_expediter_address_district."','".$prv_expediter_address_city."','".$prv_expediter_address_state."','".$prv_expediter_address_country."','".$prv_expediter_address_zipcode."','".$prv_customer_fcode."','".&filter_values($prv_customer_fname)."','".$prv_customer_address_street."','".$prv_customer_address_num."','".$prv_customer_address_num2."','".$prv_customer_address_urbanization."','".$prv_customer_address_district."','".$prv_customer_address_city."','".$prv_customer_address_state."','".$prv_customer_address_country."','".$prv_customer_address_zipcode."','".$shpcode."','".$shpalias."','".$prv_xml_cfd."','".$prv_xml_cfdi."','".$prv_xml_addenda."','".$prv_uuid."','".$prv_original_string."','".$prv_related_ID_invoices."','".$rec_order_detail->{'ID_orders_alias'}."','New','".$VendorID."','".$gln."','".$glnshp."',CURDATE(),CURTIME(), '".$usr{'id_admin_users'}."','".$credit_days."','".$conditions."');");
				$id_invoices = $sth_invoice->{'mysql_insertid'};


				## Especifico: Actualizar campos especificos de direccion de envio
				if ($has_shipping_data or $is_valid_id_customer){
					#UPDATE cu_invoices con datos de $rec_company
					&Do_SQL("UPDATE cu_invoices SET 
			        expediter_fcode = '".&filter_values($rec_company_legal->{'RFC'})."',
					expediter_fname = '".&filter_values($rec_company_legal->{'Name'})."',
					expediter_fregimen = '".$rec_company_legal->{'Regime'}."',
					expediter_faddress_street = '".&filter_values($rec_company_addr->{'Street'})."', 
					expediter_faddress_num = '".&filter_values($rec_company_addr->{'Num'})."', 
					expediter_faddress_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
					expediter_faddress_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
					expediter_faddress_district = '".&filter_values($rec_company_addr->{'District'})."', 
					expediter_faddress_city = '".&filter_values($rec_company_addr->{'City'})."', 
					expediter_faddress_state = '".&filter_values($rec_company_addr->{'State'})."', 
					expediter_faddress_country = '".&filter_values($rec_company_addr->{'Country'})."', 
					expediter_faddress_zipcode = '$rec_company_addr->{'Zip'}', 
					expediter_address_street = '".&filter_values($rec_company_addr->{'Street'})."', 
					expediter_address_num = '".&filter_values($rec_company_addr->{'Num'})."', 
					expediter_address_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
					expediter_address_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
					expediter_address_district = '".&filter_values($rec_company_addr->{'District'})."', 
					expediter_address_city = '".&filter_values($rec_company_addr->{'City'})."', 
					expediter_address_state = '".&filter_values($rec_company_addr->{'State'})."', 
					expediter_address_country = '".&filter_values($rec_company_addr->{'Country'})."', 
					expediter_address_zipcode = '$rec_company_addr->{'Zip'}', 							
					
					customer_fcode = '".&filter_values($rec_custom_info->{'RFC'})."', 
					customer_fname = '".&filter_values($rec_custom_info->{'lname'})."', 
					customer_address_street = '".&filter_values($rec_custom_info->{'cu_Street'})."',
					customer_address_num = '".&filter_values($rec_custom_info->{'cu_Num'})."',
					customer_address_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."',
					customer_address_urbanization = '".&filter_values($rec_custom_info->{'Urbanization'})."',
					customer_address_district = '".&filter_values($rec_custom_info->{'cu_District'})."',
					customer_address_city = '".&filter_values($rec_custom_info->{'City'})."', 
					customer_address_state = '".&filter_values($rec_custom_info->{'State'})."', 
					customer_address_country = '".&filter_values($rec_custom_info->{'Country'})."', 
					customer_address_zipcode = '$rec_custom_info->{'Zip'}', 

					customer_shpaddress_street = '".&filter_values($rec_shipping_data->{'cu_Street'})."', 
					customer_shpaddress_num	= '".&filter_values($rec_shipping_data->{'cu_Num'})."', 
					customer_shpaddress_num2 = '".&filter_values($rec_shipping_data->{'cu_Num2'})."', 
					customer_shpaddress_urbanization = '".&filter_values($rec_shipping_data->{'cu_Urbanization'})."', 
					customer_shpaddress_district = '".&filter_values($rec_shipping_data->{'cu_District'})."', 
					customer_shpaddress_city = '".&filter_values($rec_shipping_data->{'cu_City'})."', 
					customer_shpaddress_state = '".&filter_values($rec_shipping_data->{'cu_State'})."', 
					customer_shpaddress_country	= '".&filter_values($rec_shipping_data->{'cu_Country'})."', 
					customer_shpaddress_zipcode	= '$rec_shipping_data->{'cu_Zip'}',
					payment_digits = '$cpay'
			        WHERE ID_invoices = '$id_invoices' LIMIT 1;");

				}

			}else {
				# Factura nueva

				# Datos del Currency
				my $order_currency = &load_name('sl_customers','ID_customers',$id_customers,'Currency');
				if(!$order_currency){
					$order_currency = 'MXP';
					$exchangerate = 1;
				}else{
					#Obtiene tipo de cambio peso/dolar
					my $sth= &Do_SQL("select exchange_rate from sl_exchangerates where Currency='$order_currency' AND  Date_exchange_rate=CURDATE()");	
					$exchangerate = $sth->fetchrow;
						
					$exchangerate = 1 if($order_currency eq $cfg{'acc_default_currency'});
					if ($order_currency eq 'US$'){
						$order_currency = 'USD';
					}elsif ($order_currency eq 'EU$'){
						$order_currency = 'EUR';
					}elsif ($order_currency eq 'CO$'){
						$order_currency = 'COLP';
						$order_currency = 'MXP';
					}

				}

				if ($exchangerate eq ''){
					return &trans_txt('exchangerate_not_found'), "ERROR";
				}
				
				#$order_currency = 'MXP' if ($id_customer_generic);

				## ToDo: Hacer nuevo INSERT con datos especificos
				$sth_invoice = &Do_SQL("INSERT INTO cu_invoices SET 
				ID_customers = '".$in{'id_customers'}."',
				expediter_fcode = '".&filter_values($rec_company_legal->{'RFC'})."',
				expediter_fname = '".&filter_values($rec_company_legal->{'Name'})."',
				expediter_fregimen = '".$rec_company_legal->{'Regime'}."',    
				ID_orders_alias	= '".&filter_values($in{'id_orders_alias'})."',
				$add_sql_id_orders_alias_date
				payment_method = '".$payment_method_code."',
				discount = '".$rec_order_detail->{'OrderDisc'}."',
				invoice_net = '00.00',  
				invoice_total = '00.00',
				doc_date =  NOW() ,
				currency = '".$order_currency."',
				currency_exchange = '".$exchangerate."',
				credit_days = '".$credit_days."',
				invoice_type = '".$invoice_type."',
				place_consignment = '".&filter_values($place_consignment)."',
				expediter_faddress_street = '".&filter_values($rec_company_addr->{'Street'})."', 
				expediter_faddress_num  = '".&filter_values($rec_company_addr->{'Num'})."', 
				expediter_faddress_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
				expediter_faddress_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
				expediter_faddress_district = '".&filter_values($rec_company_addr->{'District'})."', 
				expediter_faddress_city = '".&filter_values($rec_company_addr->{'City'})."', 
				expediter_faddress_state = '".&filter_values($rec_company_addr->{'State'})."', 
				expediter_faddress_country = '".&filter_values($rec_company_addr->{'Country'})."', 
				expediter_faddress_zipcode = '".$rec_company_addr->{'Zip'}."', 
				expediter_address_street = '".&filter_values($rec_company_addr->{'Street'})."', 
				expediter_address_num = '".&filter_values($rec_company_addr->{'Num'})."', 
				expediter_address_num2 = '".&filter_values($rec_company_addr->{'Num2'})."', 
				expediter_address_urbanization = '".&filter_values($rec_company_addr->{'Urbanization'})."', 
				expediter_address_district = '".&filter_values($rec_company_addr->{'District'})."', 
				expediter_address_city = '".&filter_values($rec_company_addr->{'City'})."', 
				expediter_address_state = '".&filter_values($rec_company_addr->{'State'})."', 
				expediter_address_country = '".&filter_values($rec_company_addr->{'Country'})."', 
				expediter_address_zipcode = '".$rec_company_addr->{'Zip'}."', 						
				
				customer_fcode = '".&filter_values($rec_custom_info->{'RFC'})."', 
				customer_fname = '".&filter_values($rec_custom_info->{'lname'})."', 
				customer_address_street = '".&filter_values($rec_custom_info->{'cu_Street'})."',
				customer_address_num = '".&filter_values($rec_custom_info->{'cu_Num'})."',
				customer_address_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."',
				customer_address_urbanization = '".&filter_values($rec_custom_info->{'Urbanization'})."',
				customer_address_district = '".&filter_values($rec_custom_info->{'cu_District'})."',
				customer_address_city = '".&filter_values($rec_custom_info->{'City'})."', 
				customer_address_state = '".&filter_values($rec_custom_info->{'State'})."', 
				customer_address_country = '".&filter_values($rec_custom_info->{'Country'})."', 
				customer_address_zipcode = '$rec_custom_info->{'Zip'}', 

				customer_shpaddress_code = '".&filter_values($shpcode)."',
				customer_shpaddress_alias = '".&filter_values($shpalias)."',

				customer_shpaddress_street = '".&filter_values($rec_custom_info->{'cu_Street'})."', 
				customer_shpaddress_num	= '".&filter_values($rec_custom_info->{'cu_Num'})."', 
				customer_shpaddress_num2 = '".&filter_values($rec_custom_info->{'cu_Num2'})."', 
				customer_shpaddress_urbanization = '".&filter_values($rec_custom_info->{'cu_Urbanization'})."', 
				customer_shpaddress_district = '".&filter_values($rec_custom_info->{'cu_District'})."', 
				customer_shpaddress_city = '".&filter_values($rec_custom_info->{'cu_City'})."', 
				customer_shpaddress_state = '".&filter_values($rec_custom_info->{'cu_State'})."', 
				customer_shpaddress_country = '".&filter_values($rec_custom_info->{'cu_Country'})."', 
				customer_shpaddress_zipcode	= '".$rec_custom_info->{'cu_Zip'}."',
				
				payment_digits = '".$cpay."',
				conditions = '".&filter_values($conditions)."',
				payment_type = 'PAGO EN UNA SOLA EXHIBICION',
				STATUS = 'New' , 
				VendorID = '".$VendorID."',
				customer_address_gln='".$gln."', 
				customer_shpaddress_gln='".$glnshp."',
				DATE = CURDATE(), TIME = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."' ");
				$id_invoices = $sth_invoice->{'mysql_insertid'};

				## Especifico: Actualizar campos especificos de direccion de envio
				if (($has_shipping_data or $is_valid_id_customer) and $id_invoices){
					&Do_SQL("UPDATE cu_invoices SET
					customer_shpaddress_street = '$rec_shipping_data->{'cu_Street'}', 
					customer_shpaddress_num	= '$rec_shipping_data->{'cu_Num'}', 
					customer_shpaddress_num2 = '$rec_shipping_data->{'cu_Num2'}', 
					customer_shpaddress_urbanization = '$rec_shipping_data->{'cu_Urbanization'}', 
					customer_shpaddress_district = '$rec_shipping_data->{'cu_District'}', 
					customer_shpaddress_city = '$rec_shipping_data->{'cu_City'}', 
					customer_shpaddress_state = '$rec_shipping_data->{'cu_State'}', 
					customer_shpaddress_country	= '$rec_shipping_data->{'cu_Country'}', 
					customer_shpaddress_zipcode	= '$rec_shipping_data->{'cu_Zip'}'
			        WHERE ID_invoices = '".$id_invoices."' LIMIT 1;");
				}

			}

			if ($id_invoices) {
				## En esta parte vamos agregar una validacion solo lineas que no hayan sido facturadas		
				# Por cada producto agregamos una registro en cu_invoices_line
				# 'Active','Exchange','Returned','Undeliverable','Order Cancelled','Inactive','Lost','ReShip'
				

				###
				### Buscamos fecha de ultima devolucion para agregar validacion
				### 
				my ($sth) = &Do_SQL("SELECT DATE( IF(PostedDate IS NOT NULL AND PostedDate <> '0000-00-00',PostedDate,Date) ) FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Status = 'Returned' AND SalePrice < 0 AND LEFT(ID_products,1) = 8 ORDER BY PostedDate DESC LIMIT 1;");
				my ($last_return_date) = $sth->fetchrow();
				
				my $add_sql = ($in{'creditnote'})? ' AND SalePrice < 0 ':'';
				$add_sql .= "AND IF(sl_orders_products.PostedDate IS NOT NULL AND sl_orders_products.PostedDate <> '0000-00-00', DATE(sl_orders_products.PostedDate) >= '". $last_return_date ."', DATE(sl_orders_products.Date) >= '". $last_return_date ."')" if $last_return_date;

				my ($sth_lines) = &Do_SQL("SELECT ID_orders_products, Quantity, SalePrice, Tax, Tax_percent, ShpTax, Shipping, sl_orders_products.Discount as Discount,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products
					, sl_skus.ID_sku_products AS ID_sku
					, if(sl_customers_parts.sku_customers is null or sl_customers_parts.sku_customers='', sl_skus.UPC,sl_customers_parts.sku_customers) AS ID_sku_alias
					, sl_skus.UPC as UPC
					, sl_customers_parts.size as size
					, sl_customers_parts.packing_type as packing_type
					, sl_customers_parts.packing_unit as packing_unit
					, sl_orders_products.Cost Cost
				FROM sl_orders
					LEFT JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
					LEFT JOIN sl_customers_parts ON sl_customers_parts.ID_parts=SUBSTR(sl_orders_products.Related_ID_products,2,8)*1 AND sl_customers_parts.ID_customers=sl_orders.ID_customers
					LEFT JOIN sl_skus ON sl_skus.ID_sku_products=sl_orders_products.Related_ID_products
				WHERE sl_orders.ID_orders = '$id_orders' 
					AND sl_orders_products.Status IN('Active','Exchange','Returned') 
					AND sl_orders_products.ID_products NOT LIKE('8%')
					$add_sql
					
					
				GROUP BY ID_orders_products;");

				my $total_net = 0;
				my $total_tax = 0;
				my $total_discount = 0;			
				my $total = 0;
				my $total_shipping = 0;
				my $total_shipping_tax = 0;

				while(my $rec=$sth_lines->fetchrow_hashref) {

					## ToDo: Comparar ID_products
					#	1) Tipo Distribuidor: ID_products=100000001 + Related_ID_products = 4000001029 - sacar datos de sl_parts
					#	2) Tipo Servicio: 600001001 - sacar datos de sl_services
					#	3) Tipo Producto: 100123456 - sacar datos de sl_products
					my ($idp,$link_ts,$sku,$packing_type);

					if (substr($rec->{'ID_products'},0,1) == 6){				
						#Services
						$link_ts = "mer_services";
						$idp = $rec->{'ID_products'}-600000000;
						$va{'Name'}	= &load_name("sl_services","ID_services",$idp,"Name");
						$rec->{'ID_sku'} = $rec->{'ID_products'};
						
					}elsif (substr($rec->{'ID_products'},0,1) == 4){
						#Skus
						$idp=$rec->{'ID_products'}-400000000;
						$link_ts 	= "mer_parts";
						$va{'Name'} = &load_name("sl_parts","ID_parts",$idp,"Name");
						$va{'Model'} = &load_name("sl_parts","ID_parts",$idp,"Model");
					
					}else{
						#Products
						$idp = substr($rec->{'ID_products'},3,9);
						$link_ts = "mer_products";
						$va{'Name'}	= &load_name("sl_products","ID_products",$idp,"Name");
						$va{'Model'} = &load_name("sl_products","ID_products",$idp,"Model");
						$rec->{'ID_sku'} = $rec->{'ID_products'};
					}

					if ($cfg{'customers_parts_use'} and $cfg{'customers_parts_use'}==1) {
						my ($sth) = &Do_SQL("SELECT sku_customers, packing_type FROM sl_customers_parts WHERE ID_customers = '$in{'id_customers'}' AND ID_parts = '$idp';");
						($sku, $packing_type) = $sth->fetchrow();
					}
					$sku = (!$sku)? $rec->{'ID_products'} : $sku;
					$packing_type = (!$packing_type)? &trans_txt('invoices_measuring_unit') : $packing_type;

					$line++;
					$rec->{'SalePrice'} = 0;
					$rec->{'Tax'} = 0;
					$rec->{'Quantity'} = ($rec->{'Quantity'}*-1) if($rec->{'Quantity'} < 0);
					my $amount = $rec->{'SalePrice'};
					$rec->{'Tax_percent'} = 0;
					
					
					$add_sql = ($rec->{'SalePrice'} == 0)? "`tax`='0',`tax_rate`='0'," : "`tax`='".$rec->{'Tax'}."',`tax_rate`='".$rec->{'Tax_percent'}."',";
					&Do_SQL("INSERT INTO cu_invoices_lines SET 
						`ID_orders`='$id_orders',
						`ID_orders_products`='".$rec->{'ID_orders_products'}."',
						`ID_invoices`='$id_invoices',  
						`line_num`='$line',  
						`quantity`='".$rec->{'Quantity'}."',  
						`measuring_unit`='".$packing_type."',
						`description`='".$va{'Name'}."',
						`unit_price`='".($rec->{'SalePrice'}/$rec->{'Quantity'})."',  
						`amount`='".$amount."',
						$add_sql
						`discount`='".$rec->{'Discount'}."',
						`ID_sku`='".$rec->{'ID_sku'}."',
						`ID_sku_alias`='".$rec->{'ID_sku_alias'}."',
						`UPC`='".$rec->{'UPC'}."',
						`size`='".$rec->{'size'}."',
						`packing_type`='".$rec->{'packing_type'}."',
						`packing_unit`='".$rec->{'packing_unit'}."',
						`Date`=CURDATE(),  
						`Time`=CURTIME(),
						Cost = '$rec->{'Cost'}' ,
						`ID_admin_users`='".$usr{'id_admin_users'}."' ");
						

					$total_shipping += 0;
					$total_shipping_tax += 0;
					$total_net += 0;
					$total_tax += 0;
					$total_net += 0;
					$total_tax += 0;
					$total_discount += 0;
					
				}
				##calcular el total de la orden
				$total = $total_net + $total_tax - $total_discount;

				#Se tiene que insertar siempre la primer linea con los datos de SHIPPING
				# #calculo el tax utilizado en shipping
				if ($total_shipping > 0) { # and !$in{'creditnote'} se quita esta restriccion, parece que no es necesaria
					# my ($tax_shipping_percent) = &calculate_taxes($shp_zip, 0, 0, 0);
					# $tax_shipping_percent = 0 if (!$tax_shipping_percent);
					my ($tax_shipping_percent) = ($cfg{'shptax_percent_default'})?$cfg{'shptax_percent_default'}:'0';

					&Do_SQL("INSERT INTO cu_invoices_lines SET 
					`ID_orders`='$id_orders',
					`ID_invoices`=$id_invoices,  
					`line_num`=1,  
					`quantity`=1,  
					`measuring_unit`='".&trans_txt('invoices_measuring_unit')."',
					`description`='".&trans_txt('invoices_shipping')."',
					`unit_price`=".$total_shipping.",
					`amount`=".$total_shipping.",
					`tax`=".$total_shipping_tax.",
					`tax_rate`=".$tax_shipping_percent.",
					`Date`=CURDATE(),  
					`Time`=CURTIME(),  
					`ID_admin_users`='".$usr{'id_admin_users'}."'
					");	
				}

				&Do_SQL("UPDATE cu_invoices SET invoice_net = '$total_net', total_taxes_transfered = '$total_tax', invoice_total = '$total', discount = '$total_discount' WHERE `ID_invoices`=$id_invoices");			

				## Nota + Log
				
				&add_order_notes_by_type($id_orders,&trans_txt('opr_orders_transfer_invoice_added').": $id_invoices","Low");

				&auth_logging('opr_orders_transfer_invoice_added',$id_orders);

				$va{'message'} = &trans_txt('opr_orders_transfer_invoice_added') .":$id_invoices";

				return &trans_txt('opr_orders_transfer_invoice_added') .": $id_invoices", "OK", $id_invoices;

			}else {
				return &trans_txt('invoices_error_generating'), "ERROR";
			}

		}else {
			return &trans_txt('invoices_cust_data_not_found'), "ERROR";
		}

	}
}


#############################################################################
#############################################################################
#   Function: btn_cancell_fraudulent
#
#       Es: Muestra el botón para cancelar un pedido por fraude
#       
#
#
#    Created on: 28/09/2017
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#
sub btn_cancell_fraudulent{
#############################################################################

	if( int($cfg{'cancell_fraudulent'}) == 1 and &check_permissions('order_cancell_fraudulent','','') ) {

		my $btn = '';
		if( $in{'status'} eq 'New' or $in{'status'} eq 'Pending' ){
			$btn = '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=opr_orders&view=[in_id_orders]&cfraudulent=1" onclick="return confirm_continue()"><img src="[va_imgurl]/[ur_pref_style]/b_tocancelled.gif" title="Cancell for fraud" alt="fraud" border="0"></a>';
		}
		return $btn;

	}

}

#############################################################################
#   Function: cancell_fraudulent
#
#       Es: Cancela un pedido por fraude
#       
#
#
#    Created on: 28/09/2017
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#
sub cancell_fraudulent{
#############################################################################

	my $check_perm = &check_permissions('order_cancell_fraudulent','','');
	if ( $check_perm ){
		
		if( $in{'status'} eq 'New' or $in{'status'} eq 'Pending' ){

			my $process = 1;

			# Si es COD y está en processed, se valida si está dentro de un batch
			# if( $in{'status'} eq 'Processed' and $in{'ptype'} eq 'COD' ){
			# 	my $qry = "SELECT sl_warehouses_batches_orders.ScanDate, sl_warehouses_batches_orders.`Status`
			# 				FROM sl_warehouses_batches_orders
			# 					INNER JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products
			# 				WHERE sl_orders_products.ID_orders = ".$in{'id_orders'}.";";
			# 	my $sth = &Do_SQL($qry);
			# 	ROWS: while (my $rec = $sth->fetchrow_hashref()) {
			# 		if( $rec->{'ScanDate'} and $rec->{'Status'} eq 'In Transit' ){
			# 			$process = 0;
			# 			last ROWS;
			# 		}
			# 	}

			# 	if( $process == 0 ){
			# 		$va{'message'} = '<div class="error">'.&trans_txt('opr_orders_chargebacks_activebacth').'</div>';
			# 	}
			# }

			if( $process == 1 ){

				&Do_SQL("START TRANSACTION;");
				&Do_SQL("UPDATE sl_orders SET `Status`='Cancelled' WHERE ID_orders = ".$in{'id_orders'}.";");
				
				&add_order_notes_by_type($in{'id_orders'},"Cancelado por posible fraude","FRAUDE");
				&auth_logging('opr_orders_to_can',$in{'id_orders'});
				&Do_SQL("COMMIT;");

				$va{'message'} = '<div class="good">'.&trans_txt('actionapplied').'</div>';

			}

		} else {
			$va{'message'} = '<div class="error">'.&trans_txt('scan_order_invalid_status').'</div>';
		}			

	} elsif( !$check_perm  ) {

		$va{'message'}  = '<div class="error">'.&trans_txt('unauth_action').'</div>';

	}

}


#############################################################################
#############################################################################
#   Function: payment_logging
#
#       Es: Registra los movimientos de los pagos ya sea anticipo customer advance aplicaion de pagos.
#       
#
#
#    Created on: 22/08/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#      <>
#
sub payment_logging {
#############################################################################
#############################################################################
	my ($id_banks_movements, $id_customers, $type, $amount, $tableused, $id_tableused, $id_related_invoices) = @_;
	my $balance = 0;
	my $prevPayments = 0;
	my $base = 0;
	if($tableused eq 'cu_invoices'){
		if($type eq 'Apply'){
			$base = &Do_SQL(qq|SELECT balance
								FROM cu_customers_payments_trans cpt
								WHERE (cpt.ID_tableused = '$id_tableused' OR cpt.ID_invoices_related = '$id_tableused') 
									AND cpt.tableused = 'cu_invoices'
								ORDER BY DATE DESC, TIME DESC
								LIMIT 1;|)->fetchrow();
			#### -----------------------------------
			#### Si no existe registro inicial
			#### -----------------------------------
			if( !$base ){
				$base = &payment_logging_init($id_customers, $id_tableused);
			}
			#### -----------------------------------
			$balance = $base - $amount;
		}elsif($type eq 'Out'){
			$base = &Do_SQL(qq|SELECT balance
								FROM cu_customers_payments_trans cpt
								WHERE (cpt.ID_tableused = '$id_related_invoices' OR cpt.ID_invoices_related = '$id_related_invoices') 
									AND cpt.tableused = 'cu_invoices'
								ORDER BY DATE DESC, TIME DESC
								LIMIT 1;|)->fetchrow();
			#### -----------------------------------
			#### Si no existe registro inicial
			#### -----------------------------------
			if( !$base ){
				$base = &payment_logging_init($id_customers, $id_related_invoices);
			}
			#### -----------------------------------
			$balance = $base - $amount;
		}elsif($type eq 'In'){
			$base = $amount;
			$amount = 0;
			$balance = $base;
		}else{
			return 0;			
		}
	}
	$insert = qq|INSERT INTO `cu_customers_payments_trans` (`ID_banks_movements`, `ID_invoices_related`,`ID_customers`, `type`, `tableused`, `id_tableused`, `base`,`amount`, `balance`, `status`, `date`, `time`, `ID_admin_users`) VALUES (
			'$id_banks_movements'
			, '$id_related_invoices'
			, '$id_customers'
			, '$type'
			, '$tableused'
			, '$id_tableused'
			, '$base'
			, '$amount'
			, '$balance'
			, 'Active'
			, curdate()
			, curtime()
			, $usr{'id_admin_users'}
		);|;
	# &cgierr($insert);
	$sth = &Do_SQL($insert);
	$id_customers_payments_trans = $sth->{'mysql_insertid'};

	return $id_customers_payments_trans;
	
}

#############################################################################
#############################################################################
#   Function: payment_logging_init
#
#       Es: Registra el primer movimiento de la factura inicial cuando no existe
#       
#
#
#    Created on: 12/01/2018
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#		- id_customers
#		- id_invoices
#
#  Returns:
#
#		- base
#
#   See Also:
#
#      <>
#
sub payment_logging_init{
#############################################################################
#############################################################################
	my ($id_customers, $id_invoices) = @_;
	my $this_id_tableused = 0;

	my $query = "SELECT cu_invoices.invoice_total AS base, DATE(cu_invoices.doc_date), TIME(cu_invoices.doc_date)
				FROM cu_invoices 
				WHERE cu_invoices.ID_invoices='$id_invoices' 
					AND cu_invoices.`Status`='Certified' 
					AND cu_invoices.invoice_type = 'ingreso'
				ORDER BY Date, Time
				LIMIT 1;";
	my($base, $date, $time) = &Do_SQL($query)->fetchrow();

	if( $base > 0 ){
		&Do_SQL("INSERT INTO cu_customers_payments_trans SET 
						ID_banks_movements = 0
						, ID_invoices_related = 0
						, ID_customers = '$id_customers'
						, type = 'In'
						, tableused = 'cu_invoices'
						, id_tableused = '$id_invoices'
						, base = '$base'
						, amount = 0
						, balance = '$base'
						, status = 'Active'
						, date = '$date'
						, time = '$time'
						, ID_admin_users = $usr{'id_admin_users'};");
	}

	return $base;
}

#############################################################################
#############################################################################
#   Function: export_info_for_payment_invoices
#
#       Es: Crea un CFDI de Tipo Pago.
#       
#
#
#    Created on: 24/08/2017
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#        - Modified on 
#
#   Parameters:
#
#      - id_orders
#
#  Returns:
#
#      Devuelve ...
#
#   See Also:
#
#      <>
#
sub export_info_for_payment_invoices {
#############################################################################
#############################################################################
	my ($id_banks_movements)	=	@_;
	$query = qq|SELECT 
		sl_customers.ID_customers,
		'->' AS 'BANCO ORDENANTE',
		sl_banks_movements.RefNum
		,sl_banks_movements.fcode_bank
		,sl_banks_movements.bank
		,sl_banks_movements.account_number
		,'->' AS 'BANCO BENEFICIARIO'
		,sl_banks.BankFiscalCode
		,sl_banks.BankName
		,sl_banks.SubAccountOf
		FROM sl_banks_movements
		INNER JOIN sl_banks_movrel on sl_banks_movements.ID_banks_movements = sl_banks_movrel.ID_banks_movements
		INNER JOIN cu_customers_payments_trans on sl_banks_movements.ID_banks_movements = cu_customers_payments_trans.ID_banks_movements
		INNER JOIN sl_banks on sl_banks_movements.ID_banks = sl_banks.ID_banks
		INNER JOIN sl_customers on sl_customers.ID_customers = cu_customers_payments_trans.ID_customers
		WHERE 
			sl_banks_movements.ID_banks_movements = $id_banks_movements LIMIT 1;|;
	$queryInvoices = qq|SELECT * FROM cu_customers_payments_trans WHERE id_banks_movements = $id_banks_movements|;
	$bankInfo = &Do_SQL($query)->fetchrow_hashref();
	$invoicesRset = &Do_SQL($queryInvoices);

	# Obtener datos de Company 
	my ($sth_ci) = &Do_SQL("SELECT * FROM cu_company_legalinfo WHERE PrimaryRecord = 'Yes'");
	$rec_company_legal = $sth_ci->fetchrow_hashref;
	my ($sth_cr) = &Do_SQL("SELECT * FROM cu_company_addresses WHERE PrimaryRecord = 'Yes'");
	$rec_company_addr = $sth_cr->fetchrow_hashref;

	$rec_customer_legal = &Do_SQL(qq|SELECT * FROM cu_customers_addresses WHERE ID_customers = $bankInfo->{'ID_customers'} AND PrimaryRecord = 'Yes' LIMIT 1|)->fetchrow_hashref();
	($customer_name, $customer_fcode) = &Do_SQL(qq|SELECT company_name, RFC FROM sl_customers WHERE ID_customers = $bankInfo->{'ID_customers'}|)->fetchrow();

	$insertInvoice = qq|INSERT INTO `cu_invoices` (`ID_customers`, `doc_serial`, `doc_num`, `doc_date`, `use_cfdi`, `payment_type`, `payment_method`, `payment_digits`, `invoice_net`, `invoice_total`, `discount`, `total_taxes_detained`, `total_taxes_transfered`, `Cost`, `currency`, `currency_exchange`, `invoice_type`, `expediter_fcode`, `expediter_fname`, `expediter_fregimen`, `expediter_address_country`, `expediter_faddress_zipcode`, 
	`customer_fcode`, `customer_fname`,`customer_address_country`, `customer_address_zipcode`,`Status`, `Date`, `Time`, `ID_admin_users`, `operation_num`, `expediter_fcode_bank`, `expediter_bank`, `expediter_account_number`, `customer_fcode_bank`, `customer_bank`, `customer_account_number`
 	) VALUES ($bankInfo->{'ID_customers'}, '', 0, now(), '$bankInfo->{'use_cfdi'}', '$bankInfo->{'payment_method'}','$bankInfo->{'payment_type'}', '', 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 'XXX', '1', 'pago', '$rec_company_legal->{'RFC'}', '$rec_company_legal->{'Name'}', '$rec_company_legal->{'regime'}', 'ESTADOS UNIDOS MEXICANOS', '$rec_company_addr->{'Zip'}', '$customer_fcode', '$customer_name', '$rec_customer_legal->{'Country'}','$rec_customer_legal->{'Zip'}', 'New', curdate(), curtime(), '$usr{'id_admin_users'}', '$bankInfo->{'RefNum'}', '$bankInfo->{'fcode_bank'}', '$bankInfo->{'bank'}', '$bankInfo->{'account_number'}', '$bankInfo->{'BankFiscalCode'}', '$bankInfo->{'BankName'}', '$bankInfo->{'SubAccountOf'}');|;
 	$id_invoices = &Do_SQL($insertInvoice)->{'mysql_insertid'};
 	$insertLine = qq|INSERT INTO `cu_invoices_lines` (`ID_invoices`, `quantity`, `measuring_unit`, `description`, `unit_price`, `Cost`, `amount`, `tax`, `tax_type`, `tax_name`, `tax_rate`, `discount`, `ID_sku_alias`, `Date`, `Time`, `ID_admin_users`) 
 	    VALUES ($id_invoices, 1, 'PZA', 'Pago', 0.00, 0.00, 0.00, 0.00, 'Traslado', 'IVA', 0.00, 0.00, '84111506', curdate(), curtime(), '$usr{'id_admin_users'}'); |;

 	### Relacionamos Nueva Factura de pago con los registros de banks_movements.
 	$query = qq|
 		UPDATE cu_customers_payments_trans SET cu_customers_payments_trans.id_invoices = '$id_invoices'
 		WHERE cu_customers_payments_trans.ID_banks_movements = '$id_banks_movements'
 	|;
 	&Do_SQL($query);

 	### Relacionamos Notas de Credito a la aplicación de Pagos.
 	$invoices = &Do_SQL(qq|SELECT group_concat(ID_tableused) FROM cu_customers_payments_trans cpt WHERE ID_invoices = '$id_invoices'|)->fetchrow();
 	&Do_SQL(qq|
 		UPDATE cu_customers_payments_trans SET
 		cu_customers_payments_trans.id_invoices = '$id_invoices'
 		WHERE ( cu_customers_payments_trans.ID_tableused in ($invoices) 
 		OR cu_customers_payments_trans.ID_invoices_related in ($invoices) )
 		AND cu_customers_payments_trans.id_invoices is NULL|);


	&Do_SQL($insertLine);

}


#############################################################################
#############################################################################
#   Function: btn_upload_order_pdf
#       Es: Muestra el botón para cargar el archivo PDF de comprobación de la Orden.
#
#    Created on: 28/09/2017
#
#    Author: LI Huitzilihuitl Ceja
#
#    Modifications:
#        - Modified on 
#
#   Parameters:
#      - id_orders
#
#  Returns:
#      Devuelve ...
#
#   See Also:
#
#
sub btn_upload_order_pdf{
#############################################################################

    if( &check_permissions('upload_order_pdf','','') )
    {
        my $img, $status, $btn = '';

        if( -f $cfg{'path_upfiles'}.'e'.$in{'e'}.'/orders_pdf/'.$in{'id_orders'}.'.pdf' ){
            $img = 'pdf_file.png';
            $status = '1';
        }else{
            $img = 'paperclip.png';
            $status = '0';
        }

        $btn = '<a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=download_pdf_order_file&name='.$in{'id_orders'}.'.pdf" download="'.$in{'id_orders'}.'.pdf" taget="_blank" id="pdf_link">
                    <img src="[va_imgurl]/orders/'.$img.'" title="Download PDF File" alt="" style="height:24px; cursor:pointer;" id="pdf_button" data-exist="'.$status.'">
                </a>';

        $btn .= '
                <form method="post" enctype="multipart/form-data" id="form_file" style="display:none;">
                    <input type="file" name="fileToUpload" id="fileToUpload"> 
                </form>
                
                <script>
                    $("#pdf_link").on("click", function(e){

                        console.log("pdf_link click")

                        if( $("#pdf_button").data("exist") == 0 )
                        {
                            e.preventDefault();
                            $("#fileToUpload").trigger("click");
                        }
                        else if( $("#pdf_button").data("exist") == 1 )
                        {
                            if(e.ctrlKey) {
                                e.preventDefault();
                                response = confirm("Esta orden ya tienen un archivo PDF asociado. Desea sustituirlo?");
                                if( response ){
                                    $("#fileToUpload").trigger("click");
                                }
                            }
                        }
                    });

                    
                    function change_status(exist){

                        if(exist == undefined){
                            exist = $("#pdf_button").data("exist");
                        }

                        if(exist == 1){
                            $("#pdf_button").data("exist","1");
                            $("#pdf_button").attr("src","[va_imgurl]/orders/pdf_file.png");
                            $("#pdf_button").css("height","24px");
                        }else if(exist == 0){
                            $("#pdf_button").data("exist","0");
                            $("#pdf_button").attr("src","[va_imgurl]/orders/paperclip.png");
                            $("#pdf_button").css("height","20px");
                        }

                    }

                    change_status();


                    $("#fileToUpload").on( "change", 
                        function()
                        { 
                            var inputFileImage = document.getElementById("fileToUpload");
                            var file = inputFileImage.files[0];

                            var formData = new FormData();
                            formData.append("file",file);
                            formData.append("e",'.$in{'e'}.');
                            formData.append("id_orders",'.$in{'id_orders'}.');
                          
                            $.ajax({
                                url: "/apps/order_pdf.php",
                                type: "post",
                                contentType: false,
                                data: formData,
                                processData: false,
                                cache:false
                            }).done(
                                function(response){
                                    if( response == "'.$in{'id_orders'}.'.pdf" ){
                                        change_status(1);
                                    }else{
                                        alert( response );
                                    }
                                }
                            );
                        }
                    );
                </script>';


        return $btn;
    }

}

1;
