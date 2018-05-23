#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 5 : SHIPPING INFO
##################################################################
# Last Modified by RB on 04/15/2011 12:38:38 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
#Last modified on 27 Apr 2011 16:17:02
#Last modified by: MCC C. Gabriel Varela S. : Se hace que se muestren todas las posibles ciudades
# Last Modified by RB on 06/07/2011 01:24:48 PM : Se agrega City como parametro para calculate_taxes


	&show_shipments;
	$va{'speechname'}= 'ccinbound:5- Shipping Info';

	if ($in{'action'}){

		###
		### Se obtienen $in{'shp_city'}, $in{'shp_state'} y $cses{'id_zones'}
		###
		&get_shipping_data();


		my (@db_cols);
		my (@db_cols, $cols_to_check);

		if ($in{'country_tab'} eq "mx"){

			$in{'shp_urbanization'} = "$in{'shp_settlement_type'}|$in{'shp_settlement'}|$in{'shp_town'}";
			$in{'shp_country'} = 'Mexico';
			@db_cols = ('shp_name','shp_address1','shp_city','shp_state','shp_zip','shp_urbanization','shp_address2','shp_notes','shp_address3','shp_country','shp_settlement_type','shp_settlement','shp_town');
			$cols_to_check = 5;
		}elsif ($in{'country_tab'} eq "pr"){
			$in{'shp_country'} = 'Mexico';
			@db_cols = ('shp_name','shp_address1','shp_city','shp_state','shp_zip','shp_urbanization','shp_address2','shp_notes','shp_address3','shp_country');
			$cols_to_check = 5;
		}else{
			$in{'shp_country'} = 'Mexico';
			@db_cols = ('shp_name','shp_address1','shp_city','shp_state','shp_zip','shp_urbanization','shp_address2','shp_notes','shp_address3','shp_country');
			$cols_to_check = 4;
		}
		# $in{'shp_urbanization'} = "$in{'shp_settlement_type'}|$in{'shp_settlement'}|$in{'shp_town'}";
		# $in{'shp_country'} = 'Mexico';
		# @db_cols = ('shp_name','shp_address1','shp_city','shp_state','shp_zip','shp_urbanization','shp_address2','shp_notes','shp_address3','shp_country','shp_settlement_type','shp_settlement','shp_town');
		# $cols_to_check = 5;
		for my $i(0..$cols_to_check){
			if (!$in{$db_cols[$i]}){
				$error{$db_cols[$i]} = &trans_txt('required');
				++$err;
			}
		}
		@tmpary = split(/\s+/, $in{'shp_name'});
		if ($#tmpary < 1){
			$error{'shp_name'} = &trans_txt('invalid');
			++$err;
		} 
		for my $i(0..$#db_cols){
			$cses{lc($db_cols[$i])} = $in{lc($db_cols[$i])}
		}
		
		###############################################
		#######  CHECK ADDRESS AND ZIP CODE ###########
		###############################################
		if ($in{'check_address'}){
			#### Check Address
		}elsif(!$err){
			delete($in{'action'});
			delete($va{'message'});
			local(%error);
			
			$in{'step'} = 6;
			$va{'speechname'}= 'ccinbound:6- Shipping Type';
			for (1..$#db_cols-3){
				$cses{lc($db_cols[$_])} = $in{lc($db_cols[$_])}
			}
			if ($cses{'sameshipping'}){
				$va{'billingshipping'} = &trans_txt('samebillshp');
			}else{
				$va{'billingshipping'} = &trans_txt('difbillshp');
			}
			&calculate_shipping;
			$va{'shptotalf'} = &format_price(0); ## Free Shipping
			$va{'shptotal1'} = &format_price($va{'shptotal1'});
			$va{'shptotal2'} = &format_price($va{'shptotal2'});
			$va{'shptotal3'} = &format_price($va{'shptotal3'});
			$cses{'status5'} = 'ok';
		}else{
			$va{'message'} = &trans_txt('reqfields');
			$cses{'status5'} = 'err';
		}
	}else{
		if ($in{'country_tab'} eq "mx"){
			($in{'shp_settlement_type'},$in{'shp_settlement'},$in{'shp_town'}) = split(/,/,$in{'shp_urbanization'},3);
		}
	}


	####
	#### Calcular Taxes
	####
	$cses{'tax_total'} = &calculate_taxes($cses{'shp_zip'},$cses{'shp_state'},$cses{'shp_city'},0);

	###	Checking if All Products are Available
	for my $i(1..$cses{'items_in_basket'}){
		if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
			
		}
	}
	
	#JRG start 09-06-2008 Check aviabilty of shipment to Mexico
	$goodshpmx = 0;
	$badshpmx = 0;

	for my $i(1..$cses{'items_in_basket'}){

		if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){

			$duties = &load_name ('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3),'Duties');
			if($duties>0){
				$goodshpmx++;
			} else{
				$badshpmx++;
			}
		}
	}
	if($badshpmx eq 0){
		$mexshp = 1;
	}
	#JRG end 09-06-2008
	
	### Tabs Availables
	if($cses{'country_tab'} && !$in{'country_tab'}){
		$in{'country_tab'} = $cses{'country_tab'};
	}elsif (!$in{'country_tab'}){
		$in{'country_tab'} = 'us';
	}
	if($in{'country_tab'} && ($in{'step'} eq 4 || $in{'step'} eq 5)){
		if($in{'country_tab'} eq "us" and $cfg{'shpus'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('on','off','off','off');
		} elsif ($in{'country_tab'} eq "mx" and ($cfg{'shpmx'} eq 1 || $mexshp eq 1)){ #JRG 09-06-2008
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','on','off','off');
		} elsif ($in{'country_tab'} eq "pr" and $cfg{'shppr'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','on','off');
		} elsif ($in{'country_tab'} eq "ot" and $cfg{'shpot'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','off','on');
		}else{
			$in{'country_tab'} = 'dis';
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','off','off');
		}
		$in{'step'} = $in{'step'}.$in{'country_tab'};
		$cses{'country_tab'} = $in{'country_tab'};
	}
	#JRG end#

	&pay_type_verification;
	&cod_redir;

1;

