#!/usr/bin/perl
####################################################################
########              Home Page                     ########
####################################################################
#sub calculate_itemshipping {
## --------------------------------------------------------
#	my ($edt,$sizew,$sizeh,$sizel,$weight) = @_;
#	
#	### Shipping US continental
#	($va{'shptype1'},$va{'shptype2'},$va{'shptype3'}) = split(/,/,$cfg{'shp_types'});
#	($va{'shptype1_min'},$va{'shptype2_min'},$va{'shptype3_min'}) = split(/,/,$cfg{'shp_edt_min'});
#	($va{'shptype1_max'},$va{'shptype2_max'},$va{'shptype3_max'}) = split(/,/,$cfg{'shp_edt_max'});
#	($va{'shptype1_1lb'},$va{'shptype2_1lb'},$va{'shptype3_1lb'}) = split(/,/,$cfg{'shp_factors1'});
#	($va{'shptype1_add'},$va{'shptype2_add'},$va{'shptype3_add'}) = split(/,/,$cfg{'shp_factors2'});	
#	($va{'shpconv1'},$va{'shpconv2'},$va{'shpconv3'}) = split(/,/,$cfg{'shp_wvconv'});
#	
#	$va{'shptype1_min'}	+= $edt;
#	$va{'shptype1_max'}	+= $edt;
#	$va{'shptype2_min'}	+= $edt;
#	$va{'shptype2_max'}	+= $edt;
#	
#	## Shipping type 1
#	$aux = int($sizew*$sizeh*$sizel/$va{'shpconv1'}+0.9);
#	if ($aux > $weight){
#		$weight = $aux;
#	}
#	if ($weight>1){
#		$va{'shptotal1'} = int($va{'shptype1_1lb'} + $va{'shptype1_add'}*($weight -1 + 0.99));
#	}else{
#		$va{'shptotal1'} = $va{'shptype1_1lb'};
#	}
#
#	## Shipping type 2
#	$aux = int($sizew*$sizeh*$sizel/$va{'shpconv2'}+0.999);
#	if ($aux > $weight){
#		$weight = $aux;
#	}
#	if ($weight>1){
#		$va{'shptotal2'} = int($va{'shptype2_1lb'} + $va{'shptype2_add'}*($weight-1 + 0.99));
#	}else{
#		$va{'shptotal2'} = $va{'shptype2_1lb'};
#	}
#	
#	### Shipping Puerto Rico
#	($va{'shptype1pr'},$va{'shptype2pr'},$va{'shptype3pr'}) = split(/,/,$cfg{'shppr_types'});
#	($va{'shptype1pr_min'},$va{'shptype2pr_min'},$va{'shptype3pr_min'}) = split(/,/,$cfg{'shppr_edt_min'});
#	($va{'shptype1pr_max'},$va{'shptype2pr_max'},$va{'shptype3pr_max'}) = split(/,/,$cfg{'shppr_edt_max'});
#	($va{'shptype1pr_1lb'},$va{'shptype2pr_1lb'},$va{'shptype3pr_1lb'}) = split(/,/,$cfg{'shppr_factors1'});
#	($va{'shptype1pr_add'},$va{'shptype2pr_add'},$va{'shptype3pr_add'}) = split(/,/,$cfg{'shppr_factors2'});	
#	($va{'shpconv1pr'},$va{'shpconv2pr'},$va{'shpconv3pr'}) = split(/,/,$cfg{'shp_wvconv'});
#
#	$va{'shptype1pr_min'}	+= $edt;
#	$va{'shptype1pr_max'}	+= $edt;
#	$va{'shptype2pr_min'}	+= $edt;
#	$va{'shptype2pr_max'}	+= $edt;
#	
#	## Shipping type 1
#	$aux = int($sizew*$sizeh*$sizel/$va{'shpconv1pr'}+0.9);
#	if ($aux > $weight){
#		$weight = $aux;
#	}
#	if ($weight>1){
#		$va{'shptotal1pr'} = int($va{'shptype1pr_1lb'} + $va{'shptype1pr_add'}*($weight -1 + 0.99));
#	}else{
#		$va{'shptotal1pr'} = $va{'shptype1pr_1lb'};
#	}
#
#	## Shipping type 2
#	$aux = int($sizew*$sizeh*$sizel/$va{'shpconv2pr'}+0.999);
#	if ($aux > $weight){
#		$weight = $aux;
#	}
#	if ($weight>1){
#		$va{'shptotal2pr'} = int($va{'shptype2pr_1lb'} + $va{'shptype2pr_add'}*($weight-1 + 0.99));
#	}else{
#		$va{'shptotal2pr'} = $va{'shptype2pr_1lb'};
#	}
#	
#}

sub calculate_shipping {
# --------------------------------------------------------
# Last Modified on: 03/17/09 16:40:55
# Last Modified by: MCC C. Gabriel Varela S: Parámetros para sltv_itemshipping. Se toma en cuenta COD Shipping
# Last Modified on: 07/06/09 18:00:06
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta shpf (Free Shipping)
# Last Modified on: 07/10/09 18:19:46
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta también para COD
# Last Modified RB: 09/03/09  18:34:36 -- Se agrego descuento en shipping basado en configuracion(para TC)
# Last Modified RB: 10/09/09  16:51:30 -- Se toma un solo shipping para productos Promo y no shipping por producto
# Last Modified RB: 12/06/2010  18:35:30 -- Se agregaron parametros para calculo de shipping
# Last Modified RB: 12/09/2010  11:20:30 -- El descuento en el shipping aplica por producto y solo para calculo Fixed
#Last modified on 4/4/11 7:37 AM
#Last modified by: MCC C. Gabriel Varela S. :Se hace que no se tome en cuenta el shipping si el producto agregado es de secret cupon.
# Last Modified by RB on 06/03/2011 05:57:52 PM : Se agrega tipo de pago Prepaid-Card al descuento con pago de tarjeta

	## Calculate Shipping
	$va{'shptotal1'} = 0;
	$va{'shptotal2'} = 0;
	$va{'shptotal3'} = 0;
	$va{'shptotalf'} = 0;
	my $flag=0;
	
	if ($cses{'items_in_basket'} > 0){
		PRODUCTS:for my $i(1..$cses{'items_in_basket'}){
			#cgierr("$cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0 and $cses{'items_'.$i.'_id'} > 0 and  $cses{'items_'.$i.'_promo'} eq $flag")	if($cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0 and $flag == $cses{'items_'.$i.'_promo'}); 
			next PRODUCTS	if($cses{'items_'.$i.'_promo'} and $cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0 and $flag == $cses{'items_'.$i.'_promo'});
			
			if ($cses{'items_'.$i.'_qty'}>0  and $cses{'items_'.$i.'_id'}>0){
				my $tprod='id';
				($cses{'items_'.$i.'_promo'}) and ($tprod = 'promo') and ($flag=$cses{'items_'.$i.'_promo'});
				
				## Fixed/Variable/Table Shipping ? 
				my $shpcal  = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'	shipping_table');
				my $shpmdis = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'	shipping_discount');
				$bulk_discount=1 if($shpcal eq 'Table' and $shpmdis eq 'Yes');
				
				$cses{'items_'.$i.'_shp_cal'} = $shpcal;
				$cses{'items_'.$i.'_shp_mdis'} = $shpmdis;
				
				my $idpacking = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_'.$tprod},3,6),'ID_packingopts');
				($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpmdis,substr($cses{'items_'.$i.'_'.$tprod},3,6));
				
				## general.cfg discount?
				if($cfg{'shpdis_cc'} and $cses{'pay_type'} =~ /cc|ppc/ and $shpcal eq 'Fixed'){
					$shptotal1 *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$shptotal2 *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$shptotal3 *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$shptotal1pr *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$shptotal2pr *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
					$shptotal3pr *= $cfg{'shpdis_cc'} if(!$cses{'items_'.$i.'_secret_cupon'});
				}
				
				if ($shpcal ne 'Table' and ($cses{'shp_state'} eq 'PR-Puerto Rico' or $cses{'shp_state'} eq 'AK-Alaska' or $cses{'shp_state'} eq 'HI-Hawaii')){
					$va{'shptotal1'} += $shptotal1pr if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
					$va{'shptotal2'} += $shptotal2pr if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
					$va{'shptotal3'} += $shptotal3pr if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
				}else{
					$va{'shptotal1'} += $shptotal1 if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
					$va{'shptotal2'} += $shptotal2 if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
					$va{'shptotal3'} += $shptotal3 if(!$cses{'items_'.$i.'_shpf'} and !$cses{'items_'.$i.'_secret_cupon'} );
				}
				$str .="shptotal1 = $va{'shptotal1'} + $shptotal1\n";
				$str .="shptotal2 = $va{'shptotal2'} + $shptotal2\n";
				$str .="shptotal3 = $va{'shptotal3'} + $shptotal3\n\n";
			}
		}
		#&cgierr($str." $cfg{'shpdis_cc'} and $cses{'pay_type'}");
		#&cgierr("1:$va{'shptotal1'} - 2:$va{'shptotal2'}  - 3:$va{'shptotal3'}   --- shp_type:$in{'shp_type'}   --- $cfg{'shpdis_cc'}");
		$va{'shptotal1'} = round($va{'shptotal1'},3);	
		$va{'shptotal2'} = round($va{'shptotal2'},3);
		$va{'shptotal3'} = round($va{'shptotal3'},3);
	}
}




###############################################################
############             EXTENSION SUBS         ###############
###############################################################

sub load_speech {
# --------------------------------------------------------
	my ($speech,$id_speech);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_speech WHERE ID_dids='$cses{'id_dids'}' AND Status='Active' $query");
	if ($sth->fetchrow()>0){
		my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE ID_dids='$cses{'id_dids'}' AND Status='Active' AND Type='$va{'speechname'}' ORDER BY ID_speech");
		$id_speech = $sth->fetchrow();
	}else{
		my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE Status='Active' AND Type='$va{'speechname'}' ORDER BY ID_speech");
		if ($sth->fetchrow()>0){
			my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE Status='Active' AND Type='$va{'speechname'}' ORDER BY ID_speech");
			$id_speech = $sth->fetchrow();
		}else{
			my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE Status='Active' ORDER BY ID_speech");
			$id_speech = $sth->fetchrow();
		}
	}
	if ($id_speech){
		$speech = &load_name('sl_speech','ID_speech',$id_speech,'Speech') ."</p><p align='right' class='smalltxt'>$va{'speechname'}</p>";
		#$speech =~ s/\n/<br>/g;
	}else{
		$speech = &trans_txt('no_speech_available') ."</p><p align='right' class='smalltxt'>$va{'speechname'}</p>";
	}
	return ($speech,$id_speech);
}

sub prodquery {
#-----------------------------------------
# Forms Involved: Console Step 2 -> Search Products
# Created on: 
#
# Author: 
# Description :
# Parameters :
#
# Last Modified on: 09/15/08  11:14:49
# Last Modified by: Roberto Barcenas
# Last Modified Desc: $in{'tuser} . sltv web users are allowed to search and Add On-Air and Web Only Products
# Last Modified RB: 04/17/09  16:01:10 -- Se filtra la busqueda por DID.
# Last Modified on: 04/24/09 10:09:00
# Last Modified by: MCC C. Gabriel Varela S: Se corrige filtrado por DID para cuando no exista $cses{'id_dids'}
#Last modified on 6 May 2011 16:06:06
#Last modified by: MCC C. Gabriel Varela S. :Se hace que se filtre por el mismo grupo user_type
	my $user_type;
	$user_type=&load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},'user_type');
	my ($db)=@_;
	my ($i,$column,$maxhits,$numhits,$nh,$first,@hits,$value,$query, $condtype,$sort_order,@aux,$sth);
#@ivanmiranda: orden desde listado de productos
	if($in{'orderby'}) {
		$sort_order = "Order By $in{'orderby'} ASC";
	}
	if ($in{'keyword'}) {
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			($column eq 'sprice') and (next);
			$in{'keyword'} =~ s/^\s+//g;
			$in{'keyword'} =~ s/\s+$//g;
			if ($db_valid_types{$column} eq 'date' and &date_to_sql($in{'keyword'})){
				$query .= "$db_cols[$i] = '" . &date_to_sql($in{'keyword'}) . "' OR ";
			}elsif ($in{'sx'} or $in{'SX'}){
				$query .= "$db_cols[$i] = '" . &filter_values($in{'keyword'}) . "' OR ";
			}else{
				$query .= "$db_cols[$i] like '%" . &filter_values($in{'keyword'}) . "%' OR ";
			}
		}
		$query = substr($query,0,-3);
	}elsif ($in{lc($db_cols[0])} ne "*" or !$in{'listall'}){
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		for my $i(0..$#db_cols){
			$column = lc($db_cols[$i]);
			$in{$column} =~ s/^\s+//g;
			$in{$column} =~ s/\s+$//g;
			$value = &filter_values($in{$column});
			#($db_valid_types{$column} eq 'date') ?
			#	($value = &date_to_sql($in{$column})):
			#	($value = &filter_values($in{$column}));

			if ($in{$column} !~ /^\s*$/) {
				if ($in{$column} =~ /~~|\|/){
					@aux = split(/~~|\|/, $in{$column});
					$query .= "(";
					for (0..$#aux){
						($db_valid_types{$column} eq 'date') ?
							($value = &date_to_sql($aux[$_])):
							($value = &filter_values($aux[$_]));
							($in{'sx'} or $db_valid_types{$column} eq 'date')?
							($query .= "$db_cols[$i] = '$value' $condtype "):
							($query .= "$db_cols[$i] like '%$value%' $condtype ");
					}
					$query = substr($query,0,-4) . " ) $condtype ";
				
				}else{
					if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
						$query .= "$db_cols[$i] = Curdate() $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
						$query .= "WEEK($db_cols[$i]) = WEEK(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
						$query .= "MONTH($db_cols[$i]) = MONTH(NOW()) $condtype ";
					}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
						$query .= "YEAR($db_cols[$i]) = YEAR(NOW()) $condtype ";
					}elsif($value eq 'NULL'){
						$query .= "ISNULL($db_cols[$i]) $condtype ";			
					}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
						$query .= "$db_cols[$i]  = '$value' $condtype ";
					}else{
						$query .= "$db_cols[$i] like '%$value%'  $condtype ";
					}
				}
			}
			if ($in{'from_'.$column} !~ /^\s*$/) {
				$in{'from_'.$column} =~ s/^\s+//g;
				$in{'from_'.$column} =~ s/\s+$//g;
				$value = &filter_values($in{'from_'.$column});
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
					$query .= "$db_cols[$i] > Curdate() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisweek'){
					$query .= "WEEK($db_cols[$i]) > WEEK(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thismonth'){
					$query .= "MONTH($db_cols[$i]) > MONTH(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $value eq 'thisyear'){	
					$query .= "YEAR($db_cols[$i]) > YEAR(NOW()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db_cols[$i]  > '$value' $condtype ";
				}else{
					$query .= "$db_cols[$i] > '$value'  $condtype ";
				}
			}
			if ($in{'to_'.$column} !~ /^\s*$/) {
				$in{'to_'.$column} =~ s/^\s+//g;
				$in{'to_'.$column} =~ s/\s+$//g;
				$value = &filter_values($in{'to_'.$column});
				### From To Fields
				if ($db_valid_types{$column} eq 'date' and $value eq 'today'){
					$query .= "$db_cols[$i] < Curdate() $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisweek'){
					$query .= "WEEK($db_cols[$i]) < WEEK(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thismonth'){
					$query .= "MONTH($db_cols[$i]) < MONTH(NOW()) $condtype ";
				}elsif($db_valid_types{$column} eq 'date' and $in{$column} eq 'thisyear'){	
					$query .= "YEAR($db_cols[$i]) < YEAR(NOW()) $condtype ";
				}elsif($in{'sx'} or $db_valid_types{$column} eq 'date'){
					$query .= "$db_cols[$i]  < '$value' $condtype ";
				}else{
					$query .= "$db_cols[$i] < '$value'  $condtype ";
				}
			}
		}
		$query = substr($query,0,-4);
	}
	## El producto debe estar ligado al DID o bien no estar ligado a ningun DID para poderse mostrar
	$query_did = " AND (0 < (SELECT COUNT(ID_products) FROM sl_products_dids WHERE ID_products = sl_products.ID_products AND ID_dids = $cses{'id_dids'}) 
									OR 1 > (SELECT COUNT(ID_products) FROM sl_products_dids WHERE ID_products = sl_products.ID_products)) "if($cses{'id_dids'});
	############################
	#### Search parameters #####
	############################
	####
	#### Sort by
	#### sb = ##  (## = field order) 
	####
	#### Sort Type
	#### st = or/and  (## = field order) 
	####
	#### Exact Sort
	#### sx = 1
	####
	#### From/To
	#### from_{field-name} To_{field-name}
	####
	#### Multiples Search
	#### fieldname=value1|value2|value...
	#### 
	#### Date Search (only valid for Date type fields)
	#### date_field=today
	#### date_field=thisweek 
	#### date_field=thismonth 
	#### date_field=thisyear
	#### 
	#### Null Data
	#### fieldname=NULL
	#### 
	### Nothing to Search
	if (!$query and $in{to_sprices.price} = 0){
		$query = "WHERE Status $in{'tuser'} AND Price>0 $query_did";
	}elsif ($in{'from_sprices'} != 0 or $in{'to_sprices'} != 0){
		$query = "WHERE Price BETWEEN $in{'from_sprices'} AND $in{'to_sprices'} AND Status $in{'tuser'} $query_did ";
	}elsif ($query){
		$query = "WHERE ($query) AND Status $in{'tuser'} $query_did";
	}else{
		$query = "WHERE Status $in{'tuser'} $query_did";
	}

	$query =~ s/SPrice/Price/g;

	#if($in{'orderby'} eq 'Price') {
		$db.=" INNER JOIN (SELECT ID_products, MIN(Price) Price FROM sl_products_prices GROUP BY ID_products) sl_products_prices USING (ID_products) ";
	#}

	#&cgierr("SELECT COUNT(*) FROM $db $query and (user_type like '%$user_type%' or user_type='' or isnull(user_type));");

	$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
	$numhits = 0;
	### Count Records ###
	(exists($in{'sb'}) and $db_cols[$in{'sb'}]) and ($sort_order = "ORDER BY $db_cols[$in{'sb'}] $in{'so'}");
	$sth = &Do_SQL("SELECT COUNT(*) FROM $db $query and (user_type like '%$user_type%' or user_type='' or isnull(user_type));");

	$numhits = $sth->fetchrow();
	#RB End

	if ($numhits == 0){
		return (0,'');
	}

#@ivanmiranda, orden por defecto
	if($sort_order eq '') {
		$sort_order = 'Order By Model ASC';
	}
	if ($in{'printingmode'}){
		$sth = &Do_SQL("SELECT * FROM $db $query and (user_type like '%$user_type%' or user_type='' or isnull(user_type)) $sort_order");
		#RB Start
	# Top Sales	
	}else{
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		$sth = &Do_SQL("SELECT * FROM $db $query and (user_type like '%$user_type%' or user_type='' or isnull(user_type)) $sort_order LIMIT $first,$usr{'pref_maxh'}");
	}

	while ($rec = $sth->fetchrow_hashref){
		foreach $column (@db_cols) {
			push(@hits, $rec->{$column});
		}
	}
	return ($numhits, @hits);
}

1;
