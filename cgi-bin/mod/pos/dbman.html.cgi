##########################################################
##		OPERATIONS : ORDERS
##########################################################


########################################################################################
sub validate_atcreturns{
########################################################################################
# Last Modified on:11/jun/2008 02:16:33 PM
# Last Modified by: MCC C Gabriel Varela S
# Description : Se agrega validación de producto cuando es exchange
# Last Modified on: 11/07/08 10:31:01
# Last Modified by: MCC C. Gabriel Varela S: Se valida la existencia de 2 UPCs normales
# Last Modified by: JRG : 03/04/2009 se agrega log al returns de upcs

	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	}
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	if($in{'id_products_exchange'} ne ''){
		if($in{'id_products_exchange'}!~/^\d{9}$/){
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}else{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq''){
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}else{
			$in{'id_products_exchange'}=~/^(\d{3})(\d{3})(\d{3})$/;
			$in{'id_products_exchange'}="$1$2$3";
			if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq''){
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
		}
	}
	#GV Termina 11jun2008
	
	if(!$in{'atcreturnfees'}){
		$error{'atcreturnfees'} = &trans_txt('required');
		++$err;
	}
	if(!$in{'atcrestockfees'}){
		$error{'atcrestockfees'} = &trans_txt('required');
		++$err;
	}
	if($in{'atcprocessed'} ne 'yes'){
		$in{'atcprocessed'} = "no";
	}
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			#GV Termina modificación 24jun2008
			while ($rec1 = $sth1->fetchrow_hashref){
				$gvi++;
				$upcs = $rec1->{'UPC'};
				$io = $gvi."io_$upcs";
				$st = $gvi."st_$upcs";
				if($in{$io} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$io} = &trans_txt('required');
					++$err;
				}
				if($in{$st} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$st} = &trans_txt('required');
					++$err;
				}
				if($in{$io} && $in{$st}){
					my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET InOrder='$in{$io}', Status='$in{$st}' WHERE ID_returns=$in{'id_returns'} AND UPC=$upcs and ID_returns_upcs=$rec1->{'ID_returns_upcs'};");
					&auth_logging('returns_upcs_updated',$rec1->{'ID_returns_upcs'});					
				}
			}
		}
	}
	return $err;
}

##############################################################################
sub validate_leads_flash{
##############################################################################

	if ($in{'action'}){
		
	    my ($errors) = 0;
	   
        #validate phone
        $in{'id_leads'} =~ s/-|\(|\)|\+|\.|\s//g;
		$in{'id_leads'} = int($in{'id_leads'});
		if ($in{'id_leads'} < 999999999){
			$error{'id_leads'} = &trans_txt('invalid');	
			$error{'message'} = &trans_txt('tendigitnum');
			++$errors;
		}			
 
		if($in{'contact_time'} eq ""){
			$error{'contact_time'} = &trans_txt('required');
			++$err;
		}
		if($in{'products'} eq ""){
			$error{'products'} = &trans_txt('required');
			++$err;
		}		 
		if($in{'comments'} eq ""){
			$error{'comments'} = &trans_txt('required');
			++$err;
		}

		(!$in{'status'}) and ($in{'status'}='New');
		
		#errors
		if ($errors > 0){
			return $err;
		}
		
	}
}

sub add_leads_flash{
# --------------------------------------------------------
	if ($in{'action'}){
		if ($in{'add'}){
			$in{'contact_time'} =~ s/\|/|/g;
			$in{'products'} =~ s/\|/|/g;
		}
	}
}

sub view_leads_flash{
# --------------------------------------------------------
	if ($in{'view'}){
		$in{'contact_time'} =~  s/\|/&nbsp;-&nbsp;/g;
		$in{'products'} =~  s/\|/&nbsp;-&nbsp;/g;
		$in{'id_leads'} = &format_phone($in{'id_leads'});
	}

	if ($in{'chgstatus'} and $in{'chgstatus'} ne $in{'status'}){
			my ($sth) = &Do_SQL("UPDATE sl_leads_flash SET Status='$in{'chgstatus'}' WHERE ID_leads_flash = ".int($in{'id_leads_flash'})." ;");
			&auth_logging('leads_flash_st_updated',$in{'id_leads_flash'});
			$va{'message'} = trans_txt('leads_flash_st_updated');
			$in{'status'} = $in{'chgstatus'};
	}

	my (@ary) = ('New','Contacted','DoNotCall','Pending');
	for (0..$#ary){
		if ($in{'status'} ne $ary[$_]){
			$va{'changestatus'} .= qq|<a href="$script_url?cmd=[in_cmd]&view=[in_id_leads_flash]&chgstatus=$ary[$_]&tab=[in_tab]">$ary[$_]</a> : |;
			
		}
	}
	$va{'changestatus'} = substr($va{'changestatus'},0,-2);

}
 
1;
