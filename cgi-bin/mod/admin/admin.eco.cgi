#!/usr/bin/perl
##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################

sub eco_products {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status='Testing';");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		$id_products = substr($in{'id_sku_products'},3,6);
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
		my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status='testing' ORDER BY Date ASC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/mod/admin/admin?cmd=opq_products_view&view=$rec->{'ID_products'}&tab=6#tabs')">
				<td class="smalltext" nowrap valign="top">|. &format_sltvid($rec->{'ID_products'}) . qq|</td>
				<td class="smalltext">$rec->{'Model'}<br>$rec->{'Name'}</td>
				<td class="smalltext" nowrap valign="top">|. &format_price($rec->{'SPrice'}) . qq|</td>
				<td class="smalltext" nowrap valign="top">$rec->{'Date'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_products.html');
}

sub opq_products_view {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 10/28/08 10:05:47
# Last Modified by: MCC C. Gabriel Varela S: Se corrige error que produc?a cgierrors, se cambia returns por return
	require "dbman.html.cgi";
	$in{'db'} = 'sl_products';
	&load_cfg('sl_products');
	my (%rec) = &get_record($db_cols[0],$in{'view'},$in{'db'}) if ($in{'view'}ne'' and $in{'view'}!=0);
	if (!$rec{'id_products'}){
		&opq_products;
		return;
	}
	foreach $key (sort keys %rec) {
		$in{lc($key)} = $rec{$key};
		($db_valid_types{lc($key)} ne 'html') and ($in{lc($key)} =~ s/\n/<br>\/g);
	}	
	&view_mer_products;
	&get_db_extrainfo('admin_users',$in{'id_admin_users'});
	
	print "Content-type: text/html\n\n";
	print &build_page('opq_products_view.html');
}


sub eco_sendmail {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#

	my $err=0;
	my $dir_emails = 'email_templates/';
	my $str_template = '';
	delete($va{'pname'});
	($va{'from_run_daily'}) and ($str_template = 'mod/admin/');
	
	if ($in{'action'}){
			if (!$in{'id_orders'}){
				$va{'message'}  = &trans_txt('reqfields');
				$error{'id_orders'} = &trans_txt('required');
				$err++;	
			}
			
			$va{'id_customers'} = &load_name('sl_orders','ID_orders',int($in{'id_orders'}),'ID_customers');
			if (!$in{'to_email'} or $in{'to_email'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{'to_email'} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/){
				$to_mail = &load_name('sl_customers','ID_customers',int($va{'id_customers'}),'Email');
				
				if ($to_mail =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $to_mail !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/){ 
						$va{'message'}  = &trans_txt('reqfields');
						$error{'to_email'} = &trans_txt('invalid');
						$err++;
				}
			}
			
			if (!$in{'template'}){
				$va{'template'}  = &trans_txt('reqfields');
				$error{'template'} = &trans_txt('required');
				$err++;
			}
		
			if(!$err){
				
				if (!$in{'subject'}){
						$in{'subject'} = "Mensaje Importante sobre tu orden";
				}

				if (!$in{'from_email'}){
						$in{'from_email'} = $cfg{'from_email'};
				}
				
				my $id_orders = int($in{'id_orders'});
	
				## Order Data
				my ($sth) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders = '$id_orders';");
				my $rec = $sth->fetchrow_hashref;
				
				$va{'id_orders'} = $id_orders;
				$va{'country'} = $rec->{'Country'};
				$va{'state'} = $rec->{'shp_State'};
				$va{'city'} = $rec->{'shp_City'};
				$va{'county'} = '';
				$va{'zip'} = $rec->{'shp_Zip'};
				$va{'address1'} = $rec->{'shp_Address1'};
				$va{'address2'} = $rec->{'shp_Address2'};
				$va{'address3'} = $rec->{'shp_Address3'};
				$va{'urbanization'} = $rec->{'shp_Urbanization'};
				$va{'paytype'} = $rec->{'Ptype'};
	
				
				## Customer Data
				my ($sth2) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers = '$va{'id_customers'}';");
				my $rec2 = $sth2->fetchrow_hashref;
				
				$va{'firstname'} = $rec2->{'FirstName'};
				$va{'lastname1'} = $rec2->{'LastName1'};
				$va{'lastname2'} = $rec2->{'LastName2 '};
				$va{'phone1'} = $rec2->{'Phone1'};
				$va{'cellphone'} = $rec2->{'Cellphone'};
				if($in{'to_email'}){
					$va{'email'} = $in{'to_email'};
				}else{
					$va{'email'} = $to_mail;
				}
				
				## Sender Information
				$va{'contact_phone'} = $cfg{'cservice_phone'};
				$va{'contact_phone'} = '1-888-425-5350';
				$va{'contact_mail'} = $in{'from_email'};
				$va{'sales_name'} = "Innovagroup USA" if (!$in{'e'} or $in{'e'}eq'1');
				$va{'sales_name'} = "Innovagroup Puerto Rico" if ($in{'e'}eq'2');
				$va{'sales_name'} = "Innovagroup USA" if ($in{'e'}eq'3');
				$va{'sales_name'} = "General Trading Services" if ($in{'e'}eq'4');
				$va{'sales_name'} = "General Marketing Solutions" if ($in{'e'}eq'5');
				
				
				## Products Information
				my ($sth3) = &Do_SQL("SELECT RIGHT(ID_products,6) FROM sl_orders_products WHERE ID_orders = '$id_orders' ;");
				while(my($idp) = $sth3->fetchrow()){
					$va{'pname'} .= &load_name('sl_products','ID_products',$idp,'Name') . "<br>";
				}
				
				## Payment Information
				$va{'paymentdata'} = loadPaymentData($id_orders); 
				$va{'ccdata'} = "";
				
				$va{'va_type'} = &load_name('sl_orders_payments','ID_orders',int($va{'ID_orders'}),'Type');
				$va{'ccard_4digits'} = "xxxx - xxxx - xxxx - ".&load_name('sl_orders_payments','ID_orders',int($va{'ID_orders'}),'RIGHT(Pmtfield3,4)');
				

				my $body = &build_page($str_template . $dir_emails . $in{'template'} .".html");
				#$body = '<p>Se han cumplido las 50 reservaciones necesarias para procesar tu orden, en este correo encontrar&aacute;s la informaci&oacute;n de tu producto.</p>' . $body;
				#$body = '<p>En AllNatPro te queremos ofrecer una disculpa. Debido a un error en el sistema de procesamiento, el correo anterior contenia informacion de tu compra erronea. Los datos reales de tu compra son los que a continuacion te estamos enviando, tu tarjeta de credito sera autorizada solamente por los productos y el monto marcado en este correo.</p>' . $body;
				#&cgierr("$va{'paymentdata'}\n\n\n\n $va{'pname'}");
				#&cgierr("$in{'from_email'},$va{'email'},$in{'subject'},$body");

				## Solo enviar email de confirmacion al cliente si es s11(produccion)
				my $uname	= `uname -n`;
				if($uname =~ /s11/){
						#&cgierr("From:$in{'from_email'}\r\nTo:$va{'email'}\r\nSubject:$in{'subject'}\r\nBody:\r\n$body");
						my $status = &send_mail($in{'from_email'},$va{'email'},$in{'subject'},$body);
						&send_mail($in{'from_email'},"rbarcenas\@innovagroupusa.com",$in{'subject'},$body);
						#&send_mail($in{'from_email'},"gvsauceda\@innovagroupusa.com",$in{'subject'},$body);
      

						if($status eq 'ok'){
								
								&auth_logging('email_scan_sent',$id_orders);	
						}else{
								&auth_logging('email_scan_failed',$id_orders);
						}
				}else{
						$status = 'ok';
				}
				$va{'message'} .= "Mail Sent to $va{'email'}: $status";
			}

			if($va{'from_run_daily'} == 1){
				return;
			}

	}

	

	print "Content-type: text/html\n\n";
	print &build_page('eco_sendmail.html');
}


sub eco_techsupp {
# --------------------------------------------------------
# Created by RB on 06/30/2010 14:00 
# Last Update : 
# Locked by : 
# Description :
# Last Time modified by RB on 01/21/2011 :  Se agrego status de la orden y Fecha del mensaje


	if($in{'action'}){
		my $err;
		my $dir_emails = 'email_templates/';
		my $body;

		if(!$in{'answer'}){
			$error{'answer'} = &trans_txt('required');
			$va{'message'}  = &trans_txt('reqfields');
			$err++;
		}

		if(!$in{'view'} or $in{'view'} eq '0'){
			$va{'message'}  = &trans_txt('reqfields');
			$err++;
		}


		if(!$err){
			
			my ($sth) = &Do_SQL("INSERT INTO nsc_customers_support SET ID_customers = '0',ID_orders= '0',ID_parent= '$in{'view'}',Note='". &filter_values($in{'answer'}) ."',Status='Answered',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
			&Do_SQL("UPDATE nsc_customers_support SET Status = 'Answered' WHERE ID_customers_support = '$in{'view'}'");
			## Solo enviar email de confirmacion al cliente si es s11(produccion)
			my $uname	= `uname -n`;
			if(1){#$uname =~ /s11/){
				my $to_email;
				my $id_customers = &load_name('nsc_customers_support','ID_customers_support',$in{'view'},"ID_customers");
				$va{'name'} = &load_name('sl_customers','ID_customers',$id_customers,"FirstName");
				#$to_email = &load_name('sl_customers','ID_customers',$id_customers,"Email");
				$to_email = "roberto.barcenas\@gmail.com";
				$body = &build_page($dir_emails . "techsupport_reply_notification.html");
				my $status = &send_text_mail($in{'from_email'},$to_email,"Hemos respondido a tu pregunta",$body);
			
				if($status eq 'ok'){
						&auth_logging('email_reply_sent',$in{'view'});	
				}else{
						&auth_logging('email_reply_failed',$in{'view'});
				}
			}else{
				$status = 'ok';
			}
			$in{'get_status'} = 'answer';
			$va{'message'} = "Reply Sent";
		}
	}



	(!$in{'get_status'}) and ($in{'get_status'} = 'new');

	if($in{'get_status'} eq 'new'){
	    $modquery = " AND Status = 'New' ";
	    $va{'new'}='gcell_on'; $va{'answer'}='gcell_off'; $va{'continue'}='gcell_off'; $va{'close'}='gcell_off'; $va{'reopen'}='gcell_off'; $va{'void'}='gcell_off';
	}elsif($in{'get_status'} eq 'answer'){
	    $modquery = " AND Status = 'Answered' ";
	    $va{'new'}='gcell_off'; $va{'answer'}='gcell_on'; $va{'continue'}='gcell_off'; $va{'close'}='gcell_off'; $va{'reopen'}='gcell_off'; $va{'void'}='gcell_off';
	}elsif($in{'get_status'} eq 'continue'){
	    $modquery = " AND Status = 'Continued' ";
	    $va{'new'}='gcell_off'; $va{'answer'}='gcell_off'; $va{'continue'}='gcell_on'; $va{'close'}='gcell_off'; $va{'reopen'}='gcell_off'; $va{'void'}='gcell_off';
	}elsif($in{'get_status'} eq 'close'){
	    $modquery = " AND Status = 'Closed' ";
	    $va{'new'}='gcell_off'; $va{'answer'}='gcell_off'; $va{'continue'}='gcell_off'; $va{'close'}='gcell_on'; $va{'reopen'}='gcell_off'; $va{'void'}='gcell_off';
	}elsif($in{'get_status'} eq 'reopen'){
	    $modquery = " AND Status = 'Reopened' ";
	    $va{'new'}='gcell_off'; $va{'answer'}='gcell_off'; $va{'continue'}='gcell_off'; $va{'close'}='gcell_off'; $va{'reopen'}='gcell_on'; $va{'void'}='gcell_off';
	}elsif($in{'get_status'} eq 'void'){
	    $modquery = " AND Status = 'Void' ";
	    $va{'new'}='gcell_off'; $va{'answer'}='gcell_off'; $va{'continue'}='gcell_off'; $va{'close'}='gcell_off'; $va{'reopen'}='gcell_off'; $va{'void'}='gcell_on';
	}

	if($in{'view'}){
		$modquery .= " AND (ID_customers_support = '$in{'view'}' OR ID_parent = '$in{'view'}')";
		&eco_techsupp_detail($modquery);
		return;
	}

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM nsc_customers_support WHERE 1 $modquery AND ID_parent = 0;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		my ($sth) = &Do_SQL("SELECT *,LEFT(Note,70) AS shortquestion FROM nsc_customers_support WHERE 1 $modquery AND ID_parent = 0 ORDER BY Date ASC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			my $linkorder ='';
			my $customer = &load_name('sl_customers','ID_customers',$rec->{'ID_customers'},"CONCAT(FirstName,' ',LastName1)");
			my $order_status = $rec->{'ID_orders'} == 0 ? 'N/A': &load_name('sl_orders','ID_orders',$rec->{'ID_orders'},"Status");
			($rec->{'ID_orders'} > 0) and ($linkorder = qq| <a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}">$rec->{'ID_orders'}</a>|);
			($rec->{'ID_orders'} == 0) and ($linkorder = 'N/A');
			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td class="smalltext" nowrap valign="top">$customer (<a href="/cgi-bin/mod/admin/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}">$rec->{'ID_customers'}</a>)</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" nowrap valign="top">$linkorder</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext"><a href="/cgi-bin/mod/admin/admin?cmd=$in{'cmd'}&get_status=$in{'get_status'}&view=$rec->{'ID_customers_support'}">$rec->{'shortquestion'} ...</a></td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" nowrap valign="top">$order_status</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" nowrap valign="top">$rec->{'Date'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_techsupport.html');
}


sub eco_techsupp_detail{
# --------------------------------------------------------
# Created by RB on 06/30/2010 16:31 
# Last Update : 
# Locked by : 
# Description :
# Last Time modified by RB on 01/21/2011 :  Se agrego status de la orden

        
	my ($modquery) = @_;
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM nsc_customers_support WHERE 1 $modquery;");
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});

		my ($sth) = &Do_SQL("SELECT * FROM nsc_customers_support WHERE 1 $modquery ORDER BY Date ASC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			my $customer;
			my $linkcustomer;
			my $linkorder ='';
			($rec->{'ID_customers'} > 0) and ($customer = &load_name('sl_customers','ID_customers',$rec->{'ID_customers'},"CONCAT(FirstName,' ',LastName1)")) and ($linkcustomer = 'opr_customers');
			($rec->{'ID_customers'} == 0) and ($customer = &load_name('admin_users','ID_admin_users',$rec->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")) and ($rec->{'ID_customers'} = $rec->{'ID_admin_users'}) and ($linkcustomer = 'man_users');
			($rec->{'ID_orders'} > 0) and ($linkorder = qq| <a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}">$rec->{'ID_orders'}</a>|);
			($rec->{'ID_orders'} == 0) and ($linkorder = 'N/A');
			my $order_status = $rec->{'ID_orders'} == 0 ? 'N/A': &load_name('sl_orders','ID_orders',$rec->{'ID_orders'},"Status");  

			$d = 1 - $d;
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]'>
				<td class="smalltext" nowrap valign="top">$customer (<a href="/cgi-bin/mod/admin/dbman?cmd=$linkcustomer&view=$rec->{'ID_customers'}">$rec->{'ID_customers'}</a>)</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" nowrap valign="top">$linkorder</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext">$rec->{'Note'}</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" nowrap valign="top">$order_status</td>
				<td class="smalltext" nowrap valign="top">&nbsp;</td>
				<td class="smalltext" align="right">$rec->{'Date'}  $rec->{'Time'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_techsupport_detail.html');



}

sub eco_orders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 25 Aug 2010 17:32:37
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified By RB on 31/08/2010 : Se agrega Ptype a la orden y captura de pago si es TDC
# Last Time Modified By RB on 03/1/2011 : Se agrega language para el envio de correo de confirmacion y escaneo
#Last modified on 3/25/11 9:56 AM
#Last modified by: MCC C. Gabriel Varela S. : Se cambia 4122 por 4688
# Last Modified by RB on 04/15/2011 12:39:42 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:29:24 PM : Se agrega City como parametro para calculate_taxes
#Last modified on 14 Jun 2011 18:10:33
#Last modified by: MCC C. Gabriel Varela S. : Se eval?a si crea cliente o no
# Last time Modified By RB on 10/07/2011: Se agrega Amazon

	my ($x,$err,$query);

	if($in{'id_customers'} ne '' and !$in{'action'}){
		my $sth=&Do_SQL("Select * 
		from sl_customers
		where ID_customers='$in{'id_customers'}'
		limit 1");
		$rec=$sth->fetchrow_hashref;
		$in{'firstname'}=$rec->{'FirstName'};
		$in{'lastname1'}=$rec->{'LastName1'};
		$in{'lastname2'}=$rec->{'LastName2'};
		$in{'sex'}=$rec->{'Sex'};
		$in{'phone1'}=$rec->{'Phone1'};
		$in{'address1'}=$rec->{'Address1'};
		$in{'address2'}=$rec->{'Address2'};
		$in{'address3'}=$rec->{'Address3'};
		$in{'urbanization'}=$rec->{'Urbanization'};
		$in{'city'}=$rec->{'City'};
		$in{'state'}=$rec->{'State'};
		$in{'zip'}=$rec->{'Zip'};
		$in{'email'}=$rec->{'Email'};
		print "Content-type: text/html\n\n";
		print &build_page('eco_orders_with_customer.html');
		return;
	}
	if($in{'action'}){
		#Valida los datos para la creaci?n de cliente
		$err = &validate_eco_orders();
		&load_cfg('sl_customers');
		($x,$query) = &validate_cols('1');

		if(!$in{'id_admin_users'}){
			$error{'id_admin_users'}=&trans_txt('required');
			$err++;
		}

		$err += $x;
		if ($err==0){
			#Inserta cliente
			if(!$in{'id_customers'}){
				$sth=&Do_SQL("Insert into sl_customers 
				set FirstName='$in{'firstname'}',
				LastName1='$in{'lastname1'}',
				LastName2='$in{'lastname2'}',
				Sex='$in{'sex'}',
				Phone1='$in{'phone1'}',
				Cellphone='$in{'cellphone'}',
				Email='$in{'email'}',
				Address1='$in{'address1'}',
				Address2='$in{'address2'}',
				Address3='$in{'address3'}',
				urbanization='$in{'urbanization'}',
				City='$in{'city'}',
				State='$in{'state'}',
				Zip='$in{'zip'}',
				Country='UNITED STATES',
				Status='Active',
				Type='Retail',
				Date=curdate(),
				Time=curtime(),
				ID_admin_users='$in{'id_admin_users'}'");
				$lastid_cus = $sth->{'mysql_insertid'};
				
			}else{
				$lastid_cus=$in{'id_customers'};
			}
			
			$orderqty=0;
			for my $i(1..6){
				if($in{"id_products$i"}){
					$orderqty++;
				}
			}

			$ordertax=&calculate_taxes($in{'zip'},$in{'state'},$in{'city'},0);
			$ordershp=0;
			
			for my i(1..6){
				if($in{"shipping$i"}){
					$ordershp+=$in{"shipping$i"};
				}
			}

			$ordernet=0;
			
			for my $i(1..6){
				if($in{"sprice$i"}){
					$ordernet+=$in{"sprice$i"};
				}
			}
			
			#Language
			$in{'language'}='spanish' if !$in{'language'};
			
			#Inserta la orden
			$sth=&Do_SQL("Insert into sl_orders set ID_customers=$lastid_cus,Address1='$in{'address1'}',Address2='$in{'address2'}',Address3='$in{'address3'}',urbanization='$in{'urbanization'}',City='$in{'city'}',State='$in{'state'}',Zip='$in{'zip'}',Country='UNITED STATES',shp_type=1,shp_Address1='$in{'address1'}',shp_Address2='$in{'address2'}',shp_Address3='$in{'address3'}',shp_urbanization='$in{'urbanization'}',shp_City='$in{'city'}',shp_State='$in{'state'}',shp_Zip='$in{'zip'}',shp_Country='UNITED STATES',StatusPrd='None',StatusPay='None',OrderTax='$ordertax',OrderQty='$orderqty',OrderShp='$ordershp',OrderNet='$ordernet',Ptype=IF('$in{'type'}' = 'COD','COD','Credit-Card'),language='$in{'language'}',Status=IF('$in{'type'}' != 'Credit-Card','Processed','Void'),Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			$lastid_ord = $sth->{'mysql_insertid'};

			&Do_SQL("INSERT INTO sl_orders_notes SET Notes='Order Created', ID_orders = '$lastid_ord',Type='Web Creator',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

			#Inserta los productos
			#&cgierr("Productos");
			for my $i(1..6){
				if($in{"id_products$i"}){
					#calcular el tax aqu?.
					$tax=$in{"sprice$i"}*$ordertax;
					$sth=&Do_SQL("Insert into sl_orders_products set ID_products='".$in{"id_products$i"}."',ID_orders='$lastid_ord',Quantity=1,SalePrice='".$in{"sprice$i"}."',Shipping='".$in{"shipping$i"}."',Tax='$tax',Discount=0,Status='Active',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
				}else{
					#&cgierr("$i:fdfdfd".$in{'id_products1'});
				}
			}
			#Inserta los payments
			if($in{'type'}eq'Credit-Card'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='$in{'type'}',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'pmtfield3'}',PmtField4='$in{'pmtfield4'}',PmtField5='$in{'pmtfield5'}',PmtField6='$in{'pmtfield6'}',PmtField7='CreditCard',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$usr{'id_admin_users'}'");
			}elsif($in{'type'} =~ /PayPal|Google|Amazon/){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='Credit-Card',PmtField1='Visa',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'type'}',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),AuthCode='$in{'authcode'}',Captured='Yes',CapDate=CURDATE(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}elsif($in{'type'}eq'COD'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='COD',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}
			$lastid_payment = $sth->{'mysql_insertid'};
			
			if ($in{'type'} eq 'Credit-Card'){
				if(!$va{'from_run_daily'} == 1){
					require ("../../common/apps/cybersubs.cgi");
				}
				($status,$statmsg,$codemsg) = &sltvcyb_auth($lastid_ord,$lastid_payment);
			}else{

				## Movimientos Contables
				my ($order_type, $ctype, $ptype,@params);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$lastid_ord';");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = get_deposit_type($lastid_payment,'');
				@params = ($lastid_ord,$lastid_payment,1);
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);

				$status='OK';
				
			}

			if($status =~ /ok/i){
				$va{'message'}= &trans_txt('payments_authorized');
			}else{
				$va{'message'}= $statmsg;
			}

			$script_url =~ s/admin$/dbman/;
			$va{'message'}= &trans_txt('orders_added') . ": ID <a href=\"$script_url?cmd=opr_orders&view=$lastid_ord\">$lastid_ord</a>, Customer ID <a href=\"$script_url?cmd=opr_customers&view=$lastid_cus\">$lastid_cus</a><br>$va{'message'}";

			foreach my $key (keys %in){
				delete($in{$key});
			}

			$in{'cmd'}='eco_orders';

			if($va{'from_run_daily'} == 1){
				return $lastid_ord;
			}


		}else{
			if($va{'from_run_daily'} == 1){
				return -1;
			}
			#&cgierr("Errors:$err,$x,$#error");
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_orders.html');

}

sub validate_eco_orders{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 25 Aug 2010 18:32:09
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :

	my $err=0;

	$in{'id_products1'} = '100'.$in{'id_products1'} if length($in{'id_products1'})==6;
	$in{'id_products2'} = '100'.$in{'id_products2'} if length($in{'id_products2'})==6;
	$in{'id_products3'} = '100'.$in{'id_products3'} if length($in{'id_products3'})==6;
	$in{'id_products4'} = '100'.$in{'id_products4'} if length($in{'id_products4'})==6;
	$in{'id_products5'} = '100'.$in{'id_products5'} if length($in{'id_products5'})==6;
	$in{'id_products6'} = '100'.$in{'id_products6'} if length($in{'id_products6'})==6;

	$in{'pmtfield4'}=$in{'expdate'};
	$in{'pmtfield2'}=$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'};
	if (!$in{'address1'}){
		$error{'address1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'city'}){
		$error{'city'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'state'}){
		$error{'state'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'zip'}){
		$error{'zip'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'email'}){
		#$error{'email'} = &trans_txt('required');
		#++$err;
	}
	if (!$in{'id_products1'}){
		$error{'id_products1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'sprice1'}){
		$error{'sprice1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'shipping1'}eq''){
		$error{'shipping1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq''){
		$error{'type'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield1'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield2'}eq''){
		$error{'pmtfield2'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield3'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield3'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'expdate'}){
		$error{'pmtfield4'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'pmtfield5'}){
		$error{'pmtfield5'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'amount'}){
		$error{'amount'} = &trans_txt('required');
		++$err;
	}
	
	if($in{'id_products1'} and length($in{'id_products1'})<9){
		$error{'id_products1'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products2'} and length($in{'id_products2'})<9){
		$error{'id_products2'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products5'} and length($in{'id_products5'})<9){
		$error{'id_products5'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products3'} and length($in{'id_products3'})<9){
		$error{'id_products3'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products4'} and length($in{'id_products4'})<9){
		$error{'id_products4'} = &trans_txt('invalid');
		++$err;
	}
	
	if($in{'id_products2'} and $in{'sprice2'}eq''){
		$error{'sprice2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products2'} and $in{'shipping2'}eq''){
		$error{'shipping2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'sprice3'}eq''){
		$error{'sprice3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'shipping3'}eq''){
		$error{'shipping3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'sprice4'}eq''){
		$error{'sprice4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'shipping4'}eq''){
		$error{'shipping4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'sprice5'}eq''){
		$error{'sprice5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'shipping5'}eq''){
		$error{'shipping5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'sprice6'}eq''){
		$error{'sprice6'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'shipping6'}eq''){
		$error{'shipping6'} = &trans_txt('required');
		++$err;
	}
	
	return $err;
}

sub eco_rep_campaigns{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 25 Aug 2010 17:32:37
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :

	my ($x,$err,$query);

	if($in{'action'}){
		
	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_rep_campaigns.html');

}


sub eco_websites_chat{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11 November 2010
# Author: Roberto Barcenas.
# Description :   
# Parameters :
#Last modified on 21 Jan 2011 12:59:40
#Last modified by: MCC C. Gabriel Varela S. :Se agrega naturaliv
#Last modified on 15 Feb 2011 11:50:36
#Last modified by: MCC C. Gabriel Varela S. :Se agrega puassance
#Last modified on 16 May 2011 18:38:08
#Last modified by: MCC C. Gabriel Varela S. :Se agrega diabestevia




	$va{'algafit'} = &trans_txt('search_nomatches');
	$va{'charakani'} = &trans_txt('search_nomatches');
	$va{'chardon'} = &trans_txt('search_nomatches');
	$va{'colageina'} = &trans_txt('search_nomatches');
	$va{'innovashop'} = &trans_txt('search_nomatches');
	$va{'moinsage'} = &trans_txt('search_nomatches');
	$va{'rejuvital'} = &trans_txt('search_nomatches');
	$va{'allnatpro'} = &trans_txt('search_nomatches');
	$va{'prostaliv'} = &trans_txt('search_nomatches');
	$va{'naturaliv'} = &trans_txt('search_nomatches');
	$va{'puassance'} = &trans_txt('search_nomatches');
	$va{'diabestevia'} = &trans_txt('search_nomatches');
	$va{'singivitis'} = &trans_txt('search_nomatches');
	$va{'fibraagavera'} = &trans_txt('search_nomatches');
	$va{'buyspineflex'} = &trans_txt('search_nomatches');

	my $sth=&Do_SQL("SELECT * FROM chat_admin_users WHERE ID_admin_users = '$usr{'id_admin_users'}';");
	my($total) = $sth->rows();
	
	if($total > 0){
		while(my($id_chat,$id_admin_users,$username,$passwd,$website,$urlwebsite) = $sth->fetchrow()){
			$urlwebsite .= 'login_direksys.php';
			$va{$website} = qq|<iframe src="$urlwebsite?password=|. &filter_values($passwd) .qq|&login=$username&" id='rcmd_$website' name='$website' title='$website' width='800' height='200' frameborder='0' marginwidth='0' marginheight='0' scrolling='auto'>
				<h2>Unable to do the script</h2>
				<h3>Please update your Browser</h3>
				</iframe>|;	
		}
	}
	

	print "Content-type: text/html\n\n";
	print &build_page('eco_websites_chat.html');

}


1;