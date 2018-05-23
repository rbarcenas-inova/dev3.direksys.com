#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 10           #################
##################################################################

# Last Modified RB: 03/20/09  16:57:00 -- Se direcciono a la tabla correspondiente dependiendo de order/preorder
# Last Modified on: 04/12/11 12:06:55 PM
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la cadena de confirmation_string para utilizar codificación base64 y se pone variable para el nombre en el correo
#Last modified on 1 Jun 2011 17:46:48
#Last modified by: MCC C. Gabriel Varela S. :The confirmation_string is removed from notes
# &cgierr;


	$va{'question1'}='Que le Pareció Nuestra Programación?';  
	$va{'question2'}='Que Productos le gustaría ver en SLTV?';
	$va{'question3'}='';
	$va{'question4'}='';
	$va{'question5'}='';
	#cgierr("$in{'id_customers'}");
	$in{'id_customers'} = $cses{'id_customers'} if (!$in{'id_customers'});
	my $id = $in{'id_customers'};
	$id = substr($id,1) if $id !~	/^[0-9]/;
	$in{'email'} = &load_name('sl_customers','ID_customers',$id,'Email') if !$in{'add_extrainfo'};
	$in{'bday_day'} = &load_name('sl_customers','ID_customers',$id,'bday_day') if !$in{'add_extrainfo'};
	$in{'bday_month'} = &load_name('sl_customers','ID_customers',$id,'bday_month') if !$in{'add_extrainfo'};
	
	my $birthday = &load_name('sl_customers','ID_customers',$id,'birthday') if !$in{'add_extrainfo'};
	$birthday = &filter_values($in{'bday_year'}).'-'.$in{'bday_month'}.'-'.$in{'bday_day'} if(!$birthday);
	
	($cses{'id_salesorigins'}) and ($va{'id_salesorigins'} = $cses{'id_salesorigins'});
	($in{'id_salesorigins'}) and ($va{'id_salesorigins'} = $in{'id_salesorigins'});
	
	my ($output,$pname,$question,$question0,$question1,$question2,$question3,$question4);
		
	&save_callsession('delete');
	$va{'speechname'}= 'ccinbound:9- Good Bye';
	$err = 0; 
	#&cgierr("Email: $in{'email'}, ID_customers=$in{'id_customers'}");

	if ($in{'add_extrainfo'}){
		
		##########
		########## 1) Adding Extra Info
		##########


		$in{'step'} = 10;
		if ($in{'email'} and($in{'email'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{'email'} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )){
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}
		
		if(!$err){
			$type = substr($in{'id_customers'},0,1);
			($type !~	/[0-9]/) and ($in{'id_customers'} = substr($in{'id_customers'},1)) and ($in{'id_orders'} = substr($in{'id_orders'},1));
		}
		
		if (!$err and $in{'id_customers'}){ 
			my ($sth) = &Do_SQL("UPDATE sl_customers SET Email='".&filter_values($in{'email'})."' WHERE ID_customers='$in{'id_customers'}'"); 
			#Aquí se enviará el email
			
			if($in{'secret_cupon_applied'}==1)
			{
				$va{'firstname'}=$cses{'firstname'};
				use MIME::Base64;
				my $varcustomer,$varorder;
				$varcustomer=encode_base64($in{'id_customers'});
				$varorder=encode_base64($in{'id_orders'});
				$varcustomer=substr($varcustomer,0,length($varcustomer)-1);
				$varorder=substr($varorder,0,length($varorder)-1);
				$va{'confirmation_string'}=$varcustomer.'-g-'.$varorder;
				$va{'name'}=&load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[FirstName] [LastName1] [LastName2]');
				$message_mail = &build_page('secret_cupon_email.html');
				$sendmail=&send_text_mail($cfg{'cservice_email'},$in{'email'},$cfg{'coupons_secret_subject'},$message_mail);
				if($sendmail eq 'ok')
				{
					my ($sth)=&Do_SQL("insert into sl_customers_notes set ID_customers='$in{'id_customers'}',notes='Se ha enviado el email de confirmación de producto gratis. ',Type='Low',Date=curdate(),Time=curtime(),ID_admin_users=1");
				}
				else
				{
					my ($sth)=&Do_SQL("insert into sl_customers_notes set ID_customers='$in{'id_customers'}',notes='No se pudo enviar el email de confirmación, razón: $sendmail. ',Type='Low',Date=curdate(),Time=curtime(),ID_admin_users=1");
				}
			}
			$in{'step'} = 11;
		}
	
		if (!$err and ($in{'answer1'} or $in{'answer2'} or $in{'answer3'} or $in{'answer4'} or $in{'answer5'}) ){      
			my ($sth) = &Do_SQL("UPDATE sl_orders SET question1='$va{'question1'}',question2='$va{'question2'}',question3='$va{'question3'}',question4='$va{'question4'}',question5='$va{'question5'}',answer1='$in{'answer1'}',answer2='$in{'answer2'}',answer3='$in{'answer3'}',answer4='$in{'answer4'}',answer5='$in{'answer5'}' WHERE ID_orders = '$in{'id_orders'}'");
			$in{'step'} = 11;
		}
		
		if (!$err) {
			$in{'step'} = 11;
		}
		
		
	}elsif ($in{'req_invoice'}) {

		###########
		########### 2) Adding Invoice Data
		###########


		# Invoice info
		$in{'step'} = 10;
		
		if (!$in{'invoice_rfc'}){
			$error{'invoice_rfc'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_name'}){
			$error{'invoice_name'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_street'}){
			$error{'invoice_street'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_urbanization'}){
			$error{'invoice_urbanization'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_city'}){
			$error{'invoice_city'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_state'}){
			$error{'invoice_state'} = &trans_txt("invalid");
			++$err;
		}
		if (!$in{'invoice_zipcode'}){
			$error{'invoice_zipcode'} = &trans_txt("invalid");
			++$err;
		}
		
		if(!$err){

			my ($sth) = &Do_SQL("UPDATE sl_customers SET RFC='".&filter_values($in{'invoice_rfc'})."', company_name='".&filter_values($in{'invoice_name'})."' 
				WHERE ID_customers='".&filter_values($in{'id_customers'})."' LIMIT 1;");
			
			my ($sth) = &Do_SQL("DELETE FROM cu_customers_addresses WHERE ID_customers='".&filter_values($in{'id_customers'})."';");
			
			my $address = &filter_values($in{'invoice_street'});
			$address .= " ".&filter_values($in{'invoice_noext'}) if ($in{'invoice_noext'});
			$address .= " ".&filter_values($in{'invoice_noint'}) if ($in{'invoice_noint'});
			
			my ($sth) = &Do_SQL("INSERT INTO  cu_customers_addresses SET 
				ID_customers_addresses=NULL
				,  ID_customers='".&filter_values($in{'id_customers'})."'
				,  Code=NULL
				,  Alias=NULL
				,  Address1='".$address."'
				,  Address2='".&filter_values($in{'id_customers'})."'
				,  Address3=NULL
				,  Urbanization='".&filter_values($in{'invoice_urbanization'})."'
				,  City='".&filter_values($in{'invoice_city'})."'
				,  State='".&filter_values($in{'invoice_state'})."'
				,  Zip='".&filter_values($in{'invoice_zipcode'})."'
				,  Country='".&filter_values($in{'invoice_country'})."'
				,  cu_Street='".&filter_values($in{'invoice_street'})."'
				,  cu_Num='".&filter_values($in{'invoice_noext'})."'
				,  cu_Num2='".&filter_values($in{'invoice_noint'})."'
				,  cu_Urbanization='".&filter_values($in{'invoice_urbanization'})."'
				,  cu_District='".&filter_values($in{'invoice_location'})."'
				,  cu_City='".&filter_values($in{'invoice_city'})."'
				,  cu_State='".&filter_values($in{'invoice_state'})."'
				,  cu_Country='".&filter_values($in{'invoice_country'})."'
				,  cu_Zip='".&filter_values($in{'invoice_zipcode'})."'
				,  gln=NULL
				,  PrimaryRecord='Yes'
				,  Date=CURDATE()
				,  Time=CURTIME()
				,  ID_admin_users='$usr{'id_admin_users'}'
			");

			my ($id_customers_addresses) = $sth->{'mysql_insertid'};
			
			if ($id_customers_addresses){
				$va{'message'} = &trans_txt('invoice_info_saved');
				$va{'display_invoice_info'} = 'display:none;'
			}else{
				$va{'message'} = &trans_txt('invoice_info_error_when_saving');
				$va{'display_invoice_info'} = ''

			}
		}else{
			$va{'message'} = &trans_txt('reqfields_short');
		}
		
		if (!$err) {
			$in{'step'} = 11;
		}
	
	}elsif($in{'reprocessed'}){

		$va{'id_orders'} = int($in{'id_orders'});
		$va{'message'} = &trans_txt('step_10_order_previously_processed');

	}


1;

