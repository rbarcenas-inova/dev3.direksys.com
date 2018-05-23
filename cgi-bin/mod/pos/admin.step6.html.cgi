#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 6 : SHIPPING TYPE
##################################################################
# Last Modified on: 03/17/09 17:42:45
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta COD Shipping

	&show_shipments;
	&pay_type_verification;
	$va{'speechname'}= 'ccinbound:6- Shipping Type';
	&calculate_shipping;
	if ($cses{'sameshipping'}){
		$va{'billingshipping'} = &trans_txt('samebillshp');
	}else{
		$va{'billingshipping'} = &trans_txt('difbillshp');
	}

	if ($in{'action'}){
		if (!$in{'shp_type'}){
			$error{'shp_type'} = &trans_txt('required');
			$va{'message'} = &trans_txt('reqfields');
		}else{
			if ($cses{'pay_type'} eq 'cc'){
				$in{'step'} = '7a';
				$va{'speechname'}= 'ccinbound:7a- Payment Info Credit Card';
				$in{'month'} = substr($cses{'pmtfield4'},0,2);
				$in{'year'} = substr($cses{'pmtfield4'},2,4);	
			}elsif($cses{'pay_type'} eq 'check'){
				$in{'step'} = '7b';
				$va{'speechname'}= 'ccinbound:7b- Payment Info Check';
				($in{'month'},$in{'day'},$in{'year'}) = split(/-/,$cses{'pmtfield5'});					
			}elsif($cses{'pay_type'} eq 'wu'){
				$va{'speechname'}= 'ccinbound:7c- WesterUnion Agents';
				$in{'step'} = '7c';
			}elsif($cses{'pay_type'} eq 'fp'){
				$va{'speechname'}= 'ccinbound:7c- Flexipago';
				$in{'step'} = '7d';
			}elsif($cses{'pay_type'} eq 'mo'){
				$va{'speechname'}= 'ccinbound:7e- Money Order';
				$in{'step'} = '7e';
			}elsif($cses{'pay_type'} eq 'lay' and $cses{'laytype'} eq 'cc'){
				$in{'step'} = '7f';
				$va{'speechname'}= 'ccinbound:7f- Lay-Away Credit Card';
				$in{'month'} = substr($cses{'pmtfield4'},0,2);
				$in{'year'} = substr($cses{'pmtfield4'},2,4);	
			}elsif($cses{'pay_type'} eq 'lay' and $cses{'laytype'} eq 'mo'){
				$va{'speechname'}= 'ccinbound:7g- Lay-Away Money Order';
				$in{'step'} = '7g';
			}elsif($cses{'pay_type'} eq 'cod' or $cses{'pay_type'} eq 'rd'){
				$in{'step'} = '7h';
				$va{'speechname'}= 'ccinbound:7h- Payment COD';
			}elsif($cses{'pay_type'} eq 'ppc'){
				$in{'step'} = '7i';
				$va{'speechname'}= 'ccinbound:7i- Payment Info Prepaid Card';
				$in{'ppc_customer_name'} ="$cses{'firstname'} $cses{'lastname1'} $cses{'lastname2'}" if !$in{'ppc_customer_name'};
				$in{'ppc_cellphone'} =$cses{'cellphone'} if !$in{'ppc_cellphone'};
				$in{'ppc_this_address1'} = $cses{'address1'} if !$in{'ppc_this_address1'};
				$in{'ppc_this_address2'} = $cses{'address2'} if !$in{'ppc_this_address2'};
				$in{'ppc_this_address3'} = $cses{'address3'} if !$in{'ppc_this_address3'};
				$in{'ppc_this_city'} = $cses{'city'} if !$in{'ppc_this_city'};
				$in{'ppc_this_zip'} = $cses{'zip'} if !$in{'ppc_this_zip'};
				$in{'ppc_this_state'} = $cses{'state'} if !$in{'ppc_this_state'};
				$in{'ppc_same_dir'} = !$in{'ppc_postal_address1'} ? '1' : '0';
				$va{'ajaxbuild'}= $cfg{'pathcgi_lists'};
			}
			
			
			$in{'shp_type'}=$cfg{'codshptype'} if($cses{'pay_type'}eq'cod');
			$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};
			$cses{'shipping_total'} = 0 if $in{'shp_type'} eq 'f';
			$cses{'shp_type'} = $in{'shp_type'};

			### Si se cobra impuesto al envio. Reasignamos costo para shipping
			if ($cfg{'shptax'}) {
				if (lc($cfg{'shptaxtype'}) eq 'net') {
					$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};# + $total_shptax;				

				}elsif (lc($cfg{'shptaxtype'}) eq 'gross') {
				 	$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}} - $total_shptax;

				}
			}			
		}
		
		$va{'shippingtype'} = &trans_txt('shp_type_'.$cses{'shp_type'});
		$in{'shipping_total'} = &format_price($cses{'shipping_total'});
		$cses{'status6'} = 'ok';
	}
	$va{'shptotal_fs'} = &format_price(0);
	$va{'shptotal1'} = &format_price($va{'shptotal1'});
	$va{'shptotal2'} = &format_price($va{'shptotal2'});
	$va{'shptotal3'} = &format_price($va{'shptotal3'});
1;

