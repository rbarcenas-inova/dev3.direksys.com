#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 7 : PAYMENT INFO
##################################################################

	&show_shipments;
	&pay_type_verification;
	if ($cses{'pay_type'} eq 'cc'){
		$in{'step'} = '7a';
		$va{'speechname'}= 'ccinbound:7a- Payment Info Credit Card';
	}elsif($cses{'pay_type'} eq 'check'){
		$in{'step'} = '7b';
		$va{'speechname'}= 'ccinbound:7b- Payment Info Check';
	}elsif($cses{'pay_type'} eq 'wu'){
		$in{'step'} = '7c';
		$va{'speechname'}= 'ccinbound:7c- WesterUnion Agents';
	}elsif($cses{'pay_type'} eq 'fp'){
		$in{'step'} = '7d';
		$va{'speechname'}= 'ccinbound:7c- Flexipago';
	}elsif($cses{'pay_type'} eq 'mo'){
		$in{'step'} = '7e';
		$va{'speechname'}= 'ccinbound:7e- Money Order';
	}elsif($cses{'pay_type'} eq 'lay' and $cses{'laytype'} eq 'cc'){
		$in{'step'} = '7f';
		$va{'speechname'}= 'ccinbound:7f- Lay-Away Credit Card';
	}elsif($cses{'pay_type'} eq 'lay' and $cses{'laytype'} eq 'mo'){
		$va{'speechname'}= 'ccinbound:7g- Lay-Away Money Order';
		$in{'step'} = '7g';
	}elsif($cses{'pay_type'} eq 'cod'){
		$in{'step'} = '7h';
		$va{'speechname'}= 'ccinbound:7h- Payment COD';
	}elsif($cses{'pay_type'} eq 'ppc'){
	  $in{'step'} = '7i';
	  $va{'speechname'}= 'ccinbound:7i- Payment Info Prepaid Card';
	  $va{'ajaxbuild'}= $cfg{'pathcgi_lists'};
	}
		
	if ($in{'check_payment'}){
		my (%tmp,$cdata);
		if ($cses{'pay_type'} eq 'cc' || $cses{'pay_type'} eq 'lay'){
			$va{'message'} = &trans_txt('cc_problem').": ". &cybersource_codes($in{'reasoncode'},%tmp) . "&nbsp;&nbsp; <br>Intentos: " .$cses{'retries'};
			$va{'speechname'} = 'ccinbound:7a- Payment Info Credit Card';
			$va{'noreties'} = "<input type='button' value='No tiene Otra Forma de pago' class='button' onClick=\"nomoreretries()\">";

			## Correo Orden Void
			&send_text_mail($cfg{'from_email'},"cjmendoza\@innovagroupusa.com","Orden Void $cses{'id_orders'}","");
			&send_text_mail($cfg{'from_email'},"rgomezm\@innovagroupusa.com","Orden Void $cses{'id_orders'}","");
			&send_text_mail($cfg{'from_email'},"rbarcenas\@innovagroupusa.com","Orden Void $cses{'id_orders'}","");

		}elsif($cses{'pay_type'} eq 'check'){
			if (open(AUTH, "<$cfg{'auth_dir_cc'}/$sid")){
				LINE: while (<AUTH>) {
					$line = $_;
					$line =~ s/\r|\n//g;
					$cdata .= "$line\n";
					($line =~ /([^=]+)=(.*)/) or (next LINE);
					$tmp{$1} = $2;
				}
				close AUTH;
				unlink("$cfg{'auth_dir_cc'}/$sid");
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_plogs SET ID_orders='$cses{'id_orders'}',Data='".&filter_values($cdata)."',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			}
			$va{'speechname'}= 'ccinbound:7b- Check Declined';
			$va{'message'} = &trans_txt('ck_problem') . &certegy_codes($tmp{'PayNetResponseSubcode'},%tmp);
		}
	}

	if ($cses{'sameshipping'}){
		$va{'billingshipping'} = &trans_txt('samebillshp');
	}else{
		$va{'billingshipping'} = &trans_txt('difbillshp');
	}
	$va{'shippingtype'} = &trans_txt('shp_type_'.$cses{'shp_type'});

	if ($in{'action'}){
		$cses{'pay_type'} = $in{'pay_type'};
		if (!$in{'pay_type'}){
			++$err;
		}elsif ($in{'pay_type'} eq 'check'){
			####
			#### Validate Checks
			####
			$in{'year'} = int($in{'year'});
			if ($in{'month'} and $in{'day'} and $in{'year'}){
				$in{'pmtfield5'} = "$in{'month'}-$in{'day'}-$in{'year'}";	
			}
			$in{'pmtfield9'} = int($in{'pmtfield9'});
			#GV Inicia Modificación
			$in{'pmtfield1'}.=','.$in{'pmtfield0'}.','.$in{'pmtfield1_1'};
			#GV Termina Modificación
			for my $i(1..9){
				if (!$in{'pmtfield'.$i}){
					$error{'pmtfield'.$i} = &trans_txt('required');
					++$err;
				}
				$cses{'pmtfield'.$i} = $in{'pmtfield'.$i};
			}
			if (length($in{'pmtfield9'}) ne 10){
				$error{'pmtfield9'} = &trans_txt('invalid');
				++$err;
			}
			if ($in{'year'} > 2000 or $in{'year'}<1900){
				$error{'pmtfield5'} = &trans_txt('invalid');
				++$err;
			}
		}elsif ($in{'pay_type'} eq 'cc'){
			####
			#### Validate Credit Card
			####
			my ($tot_fp,$tmonth,$tyear);
			$in{'pmtfield4'} = "$in{'month'}$in{'year'}";
			$in{'pmtfield6'} = int($in{'pmtfield6'});
			($cfg{'acc_deposit_type_default'} and !$in{'pmtfield8'}) and ($in{'pmtfield8'} = $cfg{'acc_deposit_type_default'});
			for my $i(1..7){
				if (!$in{'pmtfield'.$i}){
					$error{'pmtfield'.$i} = &trans_txt('required');
					++$err;
				}
				$cses{'pmtfield'.$i} = $in{'pmtfield'.$i};
			}
			for my $i(1..$cses{'items_in_basket'}){
				#GV Inicia modificación 23jun2008
				if ($in{"fpago$i".$cses{'items_'.$i.'_id'}}){
					$cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}};
					($tot_fp < $in{"fpago$i".$cses{'items_'.$i.'_id'}}) and ($tot_fp =  $in{"fpago$i".$cses{'items_'.$i.'_id'}})
					#GV Termina modificación 23jun2008
				}
			}
			if (length($in{'pmtfield6'}) ne 10){
				$error{'pmtfield6'} = &trans_txt('invalid');
			}
			## Check Month and Year
			my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
			$year -=100;
			if (int($in{'year'}) eq $year and $in{'month'}<=$mon){
				$error{'pmtfield4'} = &trans_txt('invalid');
				++$err;
			}
			
			## Check Expiration
			if ($tot_fp >1){
				if ($cfg{'dayspay'} eq 15){
					$mon = int($mon + $tot_fp/2 + 1); #(1 extra months);
				}else{
					$mon = int($mon + $tot_fp + 1); #(1 extra months);
				}
				if ($mon>12){
					$mon -= 12;
					++$year;
				}
				if (int($in{'year'}) < $year){
					$error{'pmtfield4'} = &trans_txt('invalid');
					++$err;
				}elsif(int($in{'year'}) eq $year  and $in{'month'}<=$mon){
					$error{'pmtfield4'} = &trans_txt('invalid');
					++$err;
				}
			}
		}elsif ($in{'pay_type'} eq 'lay'){
			if($cses{'laytype'} eq 'cc'){
				####
				#### Validate Credit Card
				####
				my ($tot_fp,$tmonth,$tyear);
				$in{'pmtfield4'} = "$in{'month'}$in{'year'}";
				$in{'pmtfield6'} = int($in{'pmtfield6'});
				for my $i(1..7){
					if (!$in{'pmtfield'.$i}){
						$error{'pmtfield'.$i} = &trans_txt('required');
						++$err;
					}
					$cses{'pmtfield'.$i} = $in{'pmtfield'.$i};
				}
				for my $i(1..$cses{'items_in_basket'}){
					#GV Inicia modificación 23jun2008
					if ($in{"fpago$i".$cses{'items_'.$i.'_id'}}){
						$cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}};
						($tot_fp < $in{"fpago$i".$cses{'items_'.$i.'_id'}}) and ($tot_fp =  $in{"fpago$i".$cses{'items_'.$i.'_id'}})
						#GV Termina modificación 23jun2008
					}
				}
				if (length($in{'pmtfield6'}) ne 10){
					$error{'pmtfield6'} = &trans_txt('invalid');
				}
				## Check Month and Year
				my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
				$year -=100;
				if (int($in{'year'}) eq $year and $in{'month'}<=$mon){
					$error{'pmtfield4'} = &trans_txt('invalid');
					++$err;
				}
				
				## Check Expiration
				if ($tot_fp >1){
					if ($cfg{'dayspay'} eq 15){
						$mon = int($mon + $tot_fp/2 + 1); #(1 extra months);
					}else{
						$mon = int($mon + $tot_fp + 1); #(1 extra months);
					}
					if ($mon>12){
						$mon -= 12;
						++$year;
					}
					if (int($in{'year'}) < $year){
						$error{'pmtfield4'} = &trans_txt('invalid');
						++$err;
					}elsif(int($in{'year'}) eq $year  and $in{'month'}<=$mon){
						$error{'pmtfield4'} = &trans_txt('invalid');
						++$err;
					}
				}
			}
		}elsif($in{'pay_type'} eq 'ppc'){
			@ppc_req_fiels = ('ppc_customer_firstname','ppc_customer_lastname',
					'ppc_id_type','ppc_id_number','ppc_id_country','ppc_cellphone',
					'ppc_birthday','ppc_this_address1','ppc_this_city','ppc_this_state',
					'ppc_this_zip','ppc_postal_address1','ppc_postal_city','ppc_postal_state','ppc_postal_zip');
			$in{'ppc_cellphone'} =~ s/-|\s|\///g;
			if($in{'ppc_same_dir'}){
				$in{'ppc_same_dir'}=$in{'ppc_same_dir'};
				$in{'ppc_postal_address1'} = $in{'ppc_this_address1'};
				$in{'ppc_postal_address2'} = $in{'ppc_this_address2'};
				$in{'ppc_postal_address3'} = $in{'ppc_this_address3'};
				$in{'ppc_postal_city'} = $in{'ppc_this_city'};
				$in{'ppc_postal_state'} = $in{'ppc_this_state'};
				$in{'ppc_postal_zip'} = $in{'ppc_this_zip'};		    
			}

			push(@ppc_req_fiels,'ppc_id_state') if($in{'ppc_id_type'} =~ /2|7|8|9|101/ and ($in{'ppc_id_country'} =~ /840/ or !$in{'ppc_id_country'}));
			push(@ppc_req_fiels,'ppc_id_goodthru') if($in{'ppc_id_type'} =~ /2|3|4|5|7|8|9|101/);

			for (0..$#ppc_req_fiels){
				if (!$in{$ppc_req_fiels[$_]}){
					$error{$ppc_req_fiels[$_]} = &trans_txt('required');
					++$err;
				}
			}
			foreach $key (keys %in){
				if ($key =~ /^ppc_/){
					$cses{$key} = $in{$key};
				}
			}

		  
			$cses{'PmtField1'}='Prepaid-Card';
			$cses{'PmtField2'}=$in{'ppc_customer_name'};
			$cses{'PmtField3'}=$in{'ppc_id_number'};
			
			for(4..9){
				$cses{'PmtField'.$_}='N/A';
			}
		  
		}
		
		
		if ($err){
			$cses{'status7'} = 'err';
			$va{'message'} = &trans_txt('reqfields');
		}else{
			$in{'step'} = '8';
			$cses{'status7'} = 'ok';
			if($in{'pay_type'} eq 'lay'){
				$cses{'startdate'} = $in{'startdate'};
			}elsif($cses{'startdate'}){
				delete($cses{'startdate'});
			}
			#RB Start - Add and Extended Warranty for each item
			&service_bydefault();
			#&cgierr;
			#RB End
			#GV Inicia 17abr2008 Si hay flexipagos agregar un porcentaje
			#&calculatetotal;
			#&flexiservice;
			#GV Termina 17abr2008 Si hay flexipagos agregar un porcentaje

			$va{'pdmaxdays'} = $cfg{'postdateddays'};
			#&cgierr("$cfg{'postdateddays'} $in{'e'}");
			$va{'speechname'}= 'ccinbound:8- Confirm Order';
			$va{'shippingtype'} = &trans_txt('shp_type_'.$cses{'shp_type'});
			$va{'paytype'} = &trans_txt('pay_type_'.$cses{'pay_type'}); 
			#for my $i(1..5){
			#	$va{'title'.$i} =  &trans_txt('pay_'.$cses{'pay_type'}.$i);
			#}
			
			### LOAD Services 
			#GV Modificación Se comenta la parte de servicios
			# $in{'op'}=int($in{'op'});
			# my (@c) = split(/,/,$cfg{'srcolors'});
			# my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE Status='Active'");
			# if ($sth->fetchrow>0){		
			# 	my ($sth) = &Do_SQL("SELECT ID_noninventory,Name,Description,SPrice,SalesPrice,Status,ServiceType,Tax FROM sl_services WHERE Status = \'Active\' ORDER BY Name");
			# 	while ($rec = $sth->fetchrow_hashref){
			# 		$d = 1 - $d;
			# 		$rec->{'Comments'} =~ s/\n/<br>/g;
			# 		$va{'searchresults'} .= "<tr >\n";						
			# 		$va{'searchresults'} .= "  <td class='smalltext'><a href='$script_url?cmd=console_order&step=8&ser=1&ID_noninventory=$rec->{'ID_noninventory'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_add.gif' title='Add' alt='' border='0'></a></td>\n";					
			# 		$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'ID_noninventory'}</td>\n";						
			# 		$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Name'}<BR>$rec->{'Description'}</td>\n";
			# 		$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'ServiceType'}</td>\n";		
			#		if($rec->{'SalesPrice'} eq 'Fixed'){
			# 			$total_sp = $rec->{'SPrice'} ;
			# 			$va{'searchresults'} .= "   <td class='smalltext' align='right' nowrap valign='top'>".&format_price($total_sp)."</td>\n";
			# 	  	}else{
			# 	  		$total_sp = $cses{'total_i'} * ($rec->{'SPrice'}/100);
			# 	 		$va{'searchresults'} .= "   <td class='smalltext' align='right' nowrap valign='top'>".&format_price($total_sp)."</td>\n";
			# 		}										
			# 		$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$rec->{'Tax'}</td>\n";													
			# 		$va{'searchresults'} .= "</tr>\n"; 
			#   }	
			#   $cses{'ser'} = $in{'ser'};					
			#   $cses{'id_noninventory'} = $in{'id_noninventory'};					
			# }else{
			# 	$va{'searchresults'} = qq|
			# 	<tr>
			# 		<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			# 	</tr>\n|;
			# }	
			# $va{'serlist'}=$va{'searchresults'};
		}
	}else{
		if ($cses{'pay_type'} eq 'check'){
			($in{'month'},$in{'day'},$in{'year'}) = split(/-/,$cses{'pmtfield5'},3); 
		}else{
			$in{'month'} = substr($cses{'pmtfield4'},0,2);
			$in{'year'} = substr($cses{'pmtfield4'},2,4); 
		}
	}
		
	$in{'shipping_total'} = &format_price($in{'shipping_total'});

1;

