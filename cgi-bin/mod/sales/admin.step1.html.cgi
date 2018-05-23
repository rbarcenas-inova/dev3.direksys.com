#!/usr/bin/perl
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia ID_dids por DNIS en sl_orders/
##################################################################
############      CONSOLE STEP 1           #################
##################################################################

	##############################
	#### STEP 1 : NEW CUSTOMER
	##############################
	$va{'speechname'}= 'ccinbound:1a- New Customer';

	### validate cid and did - rafael on 10/25/2007 1:55PM ###
	my ($errors) = 0;
	if (!$in{'cid'}) {
		$error{'cid'} = &trans_txt('required');	
		++$errors;
	}else{
		$in{'cid'} = int($in{'cid'});
		if ($in{'cid'} < 999999999){
			$error{'cid'} = &trans_txt('invalid');	
			$error{'message'} = &trans_txt('tendigitnum');
			++$errors;
		}			
	}
	if (!$in{'did'}){
		$error{'did'} = &trans_txt('required');
		++$errors;	
	}
	
	$in{'id_origins'} = &set_origin_default if !$in{'id_origins'};
	$in{'id_origins'} = 1 if (!$in{'id_origins'} or $in{'id_origins'} <= 0);
			
	if ($errors > 0){
		print "Content-type: text/html\n\n";
		print &build_page("console_newcall.html");	
		exit;
	}
	### end validation ###

	
	##############################
	#### STEP 1 : SPEECH
	##############################
	my ($query);
	if ($in{'cid'}){
		my ($sth) = &Do_SQL("SELECT ID_customers FROM sl_customers WHERE CID='$in{'cid'}' OR sl_customers.Phone1='$in{'cid'}' OR sl_customers.Phone2='$in{'cid'}' OR sl_customers.Cellphone='$in{'cid'}'");
		$in{'id_customers'} = $sth->fetchrow();
		if ($in{'id_customers'}>0){
			$va{'speechname'}= 'ccinbound:1b- Repeat Customer';
		}else{
			$va{'speechname'}= 'ccinbound:1a- New Customer';
		}
	}else{		
		$va{'speechname'} = 'ccinbound:1a- New Customer';	
	}
	if ($in{'did'}) {
		$cses{'id_dids'} = $in{'did'};
	}
	($va{'speech'},$cses{'id_speech'}) = &load_speech($query);

	$cses{'id_salesorigins'} = $in{'id_origins'};
	$cses{'prodfam'} = $in{'prodfam'};
	my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_leads SET ID_leads=$in{'cid'},Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}");
	my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_leads_notes SET ID_leads=$in{'cid'},Comments='$in{'prodfam'}',Date=CURDATE(),Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'}") if ($in{'prodfam'});


1;