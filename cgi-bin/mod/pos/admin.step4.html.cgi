#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 4 : BILLING INFO
##################################################################
# Last Modified on: 02/12/09 17:57:25
# Last Modified by: MCC C. Gabriel Varela S: Se pone país USA como United States
#Last modified on 20 Apr 2011 16:50:11
#Last modified by: MCC C. Gabriel Varela S. :Se hace que se muestren todas las ciudades para el zipcode
#Last modified by RB on 07/24/2013: Se agrega asignacion de zona al recibir el zipcode. En base a esto se valida tambien el tipo de pago

	&pay_type_verification;
	$va{'speechname'}= 'ccinbound:4- Billing Info';
	
	if ($in{'action'}){
	
		###
		### Se obtienen $in{'shp_city'}, $in{'shp_state'} y $cses{'id_zones'}
		###
		&get_shipping_data();


		my (@db_cols,$cols_to_check);
		if ($in{'country_tab'} eq "mx"){
			$in{'urbanization'} = "$in{'settlement_type'}|$in{'settlement'}|$in{'town'}";
			$in{'country'} = 'Mexico';
			@db_cols = ('address1','city','state','zip','urbanization','address2','notes','address3','notes','country','settlement_type','settlement','town');
			$cols_to_check = 4;
		}elsif ($in{'country_tab'} eq "pr"){
			$in{'country'} = 'United States';
			@db_cols = ('address1','city','state','zip','urbanization','address2','notes','address3','notes','country');
			$cols_to_check = 4;
		}else{
			$in{'country'} = 'United States';
			@db_cols = ('address1','city','state','zip','address2','notes','address3','notes','country');
			$cols_to_check = 3;
		}
		for my $i(0..$cols_to_check){
			if (!$in{$db_cols[$i]}){
				$error{$db_cols[$i]} = &trans_txt('required');
				++$err;
			}
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
			$in{'step'} = 5;
			$va{'speechname'}= 'ccinbound:5- Shipping Info';
			for (0..$#db_cols){
				$cses{lc($db_cols[$_])} = $in{lc($db_cols[$_])}
			}

			$cses{'status4'} = 'ok';
		}else{
			$cses{'status4'} = 'err';
			$va{'message'} = &trans_txt('reqfields');
		}
	}		
	#JRG start#
	if($cses{'country_tab'} && !$in{'country_tab'}){
		$in{'country_tab'} = $cses{'country_tab'};
	}elsif (!$in{'country_tab'}){
		$in{'country_tab'} = 'us';
	}
	if($in{'country_tab'} && ($in{'step'} eq 4 || $in{'step'} eq 5)){
		if($in{'country_tab'} eq "us" and $cfg{'payus'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('on','off','off','off');
		} elsif ($in{'country_tab'} eq "mx" and $cfg{'paymx'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','on','off','off');
		} elsif ($in{'country_tab'} eq "pr" and $cfg{'paypr'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','on','off');
		} elsif ($in{'country_tab'} eq "ot" and $cfg{'payot'} eq 1){
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','off','on');
		}else{
			$in{'country_tab'} = 'dis';
			($va{'us'},$va{'mx'},$va{'pr'},$va{'ot'}) = ('off','off','off','off');
		}
		$in{'step'} = $in{'step'}.$in{'country_tab'};
		$cses{'country_tab'} = $in{'country_tab'};
	}
	
	($cses{'zipcode_selected'}) and ($va{'zipcode'} = $cses{'zipcode_selected'});
	($cses{'zipcode'}) and ($va{'zipcode'} = $cses{'zipcode'});
	($in{'zip'} and $in{'sameshipping'} and $in{'sameshipping'} eq 'same') and ($va{'zipcode'} = $in{'zip'});

	if ($in{'zip'}){

		###
		### Datos de City,State
		###

		my ($sth) = &Do_SQL("SELECT * FROM sl_zipcodes WHERE ZipCode='$in{'zip'}' /*AND PrimaryRecord='P'*/ group by city;");
		$in{'city_to_show'} ='';
		while($tmp = $sth->fetchrow_hashref){
			if ($tmp->{'ZipCode'}>0){
				if(uc($cfg{'country'}) ne 'MX')  {
					$in{'city'} = $tmp->{'City'};
					$in{'city_to_show'} .= $tmp->{'City'}.' | ';
					$in{'state'} = $tmp->{'State'}."-".$tmp->{'StateFullName'};
				}
			}
		}
	}


	################################################
	################################################
	#########
	######### Cargado de vartiables de sesion para Direccion de Envio
	#########
	################################################
	################################################


	if (($in{'sameshipping'} and $in{'sameshipping'} eq 'same')) {
		
		####
		#### Billing == Shipping
		####

		$cses{'shp_address1'} =  $in{'address1'};
		$cses{'shp_address2'} =  $in{'address2'};
		$cses{'shp_address3'} =  $in{'address3'};
		$cses{'shp_urbanization'} =  $in{'urbanization'};
		$cses{'shp_city'} =  $in{'city'};
		$cses{'shp_state'} =  $in{'state'};
		$cses{'shp_zip'} =  $in{'zip'};

		$in{'shp_address1'} =  $in{'address1'};
		$in{'shp_address2'} =  $in{'address2'};
		$in{'shp_address3'} =  $in{'address3'};
		$in{'shp_urbanization'} =  $in{'urbanization'};
		$in{'shp_city'} =  $in{'city'};
		$in{'shp_state'} =  $in{'state'};
		$in{'shp_zip'} =  $in{'zip'};

	}else{

		####
		#### Billing != Shipping
		####

		$cses{'shp_address1'} = '';
		$cses{'shp_address2'} = '';
		$cses{'shp_address3'} = '';
		$cses{'shp_urbanization'} = '';
		$cses{'shp_city'} = '';
		$cses{'shp_state'} = '';
		$cses{'shp_zip'} = '';

		$in{'city'} = '';
		$in{'city_to_show'} = '';
		$in{'state'} = '';
	}
	
	$in{'customers.address1'} = ($in{'address1'})? $in{'address1'}:$in{'customers.address1'};
	$in{'customers.address2'} = ($in{'address2'})? $in{'address2'}:$in{'customers.address2'};
	$in{'customers.address3'} = ($in{'address3'})? $in{'address3'}:$in{'customers.address3'};
	$in{'customers.urbanization'} = ($in{'urbanization'})? $in{'urbanization'}:$in{'customers.urbanization'};
	$in{'customers.city'} = ($in{'city'})? $in{'city'}:$in{'customers.city'};


	if(uc($cfg{'country'}) eq 'MX' and $in{'urbanization'} ne '')  {
		$cses{'urbanization'} = $in{'urbanization'};
	}

1;