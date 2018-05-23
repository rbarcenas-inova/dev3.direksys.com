#!/usr/bin/perl
##################################################################
############                HOME                 #################
##################################################################


sub console_newcall {
# --------------------------------------------------------
	## Delete session variables
	&save_callsession('delete');
	
	## Checking Permission

	$cses{'start_sec'} = &get_sec();
	$cses{'advbar'} = 1;
	$cses{'items_in_basket'} = 0;
	$cses{'sameshipping'} = "same";
	$cses{'id_salesorigins'} = $in{'id_origins'} if ($in{'id_origins'} and !$cses{'id_salesorigins'});
	$cses{'pterms'} = 'Contado' if($in{'e'} == 2 or $in{'e'} == 10 and !$cses{'pterms'});
	$cses{'currency'} = 'MX$' if($in{'e'} == 2 or $in{'e'} == 10 and !$cses{'currency'});
	$va{'salesorigins.channel'} = &load_name("sl_salesorigins","ID_salesorigins",$cses{'id_salesorigins'},"channel") if($cses{'id_salesorigins'});
	&create_inorder();
	&save_callsession();

	$va{'active_sognare_poll'} = ($cfg{'active_sognare_poll'} and $usr{'email2'} eq 'encuesta@sognare.com')? 1:0;

	## WS earcalls
	&load_earcall_interval();
	print "Content-type: text/html\n\n";
	print &build_page("console_newcall.html");
}

sub wuagents {
# --------------------------------------------------------
	my (@c) = split(/,/,$cfg{'srcolors'});
	$in{'zip'} = int($in{'zip'});
	if ($in{'zip'}){
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wuagents WHERE ZipCode='$in{'zip'}'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			#$usr{'pref_maxh'} = 2;
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/sales/admin",$va{'matches'},$usr{'pref_maxh'});
			#5551212
			my ($sth) = &Do_SQL("SELECT * FROM sl_wuagents WHERE ZipCode='$in{'zip'}' ORDER BY AgentName DESC LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$rec->{'Notes'} =~ s/\n/<br>/g;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'AgentName'}<br>$rec->{'Address1'}<br>$rec->{'Address2'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='top'>$rec->{'Phone'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "Content-type: text/html\n\n";
		print &build_page("console_wulist.html");		
	}else{
		print "Content-type: text/html\n\n";
		print &build_page("console_wuform.html");			
	}
}

##################################################################
############                ORDER                 ################
##################################################################
sub console_order {
# --------------------------------------------------------
#Last modified on 5 May 2011 11:37:28
#Last modified by: MCC C. Gabriel Varela S. : Se hace que se pase a in la variable cfg de email_and_cellphone_use

	### Order Prefix
	$va{'e_prefix'} = $cfg{'prefixentershipment'};

	# indica si lleva barra de avance
	$cses{'advbar'} = 1;

	$va{'active_sognare_poll'} = ($cfg{'active_sognare_poll'} and $usr{'email2'} eq 'encuesta@sognare.com')? 1:0;
	
	## Checking Permission
	$cses{'pterms'} = $in{'pterms'} if ($in{'pterms'});
	$cses{'id_salesorigins'} = $in{'id_salesorigins'} if ($in{'id_salesorigins'});
	$cses{'id_salesorigins'} = $in{'origin'} if (!$cses{'id_salesorigins'});
		
	&load_callsession();
	
	## --------------------------------------------------------
	## Debug Only
	if (%in){
		foreach my $key (keys %in){
			$vars_in .= "$key=$in{$key}\n";
		}	
	}
	$cses{'debug_lines'} .="\n- - - - - - - - - - - - - - - - - - - - - - - >\nstep = ".$in{'step'}."\ncmd = ".$in{'cmd'}."\n\n$vars_in";
	## --------------------------------------------------------
	
	$in{'step'} = int($in{'step'});
	
	delete ($cses{'id_customers'}) if ($in{'clr_cust'});

	if ($in{'step'} > 3 and !$cses{'total_order'} and $in{'step'} ne 10){
		$in{'step'} = 2;
	}elsif($in{'step'} eq 3 and !$cses{'total_order'}){
		$va{'speechname'} = 'ccinbound:2- Product Searchxxx';
		$va{'message'} = &trans_txt('empty_cart');
		$in{'step'} = 2;
	}

	&cod_redir if($in{'step'} > 4 and (lc($cses{'pay_type'}) eq "cod" or lc($cses{'pay_type'}) eq "rd") );

	## Fix lost of callerid in customer new
	if ($in{'cid'}){
		$cses{'cid'} = $in{'cid'};
	}elsif($cses{'cid'}) {
		$in{'cid'} = $cses{'cid'}; 
	}

	if ($in{'did'}) {
		$cses{'did'} = $in{'did'};
	}elsif($cses{'did'}) {
		$in{'did'} = $cses{'did'}; 
	}


	## Run Step Command
	my ($cmd) = 'admin.step'.$in{'step'}.'.html.cgi';
	if (-e $cmd){
		require($cmd);
	}else{
		require('admin.step3.html.cgi');
	}	
	
	&save_callsession();
	&load_callsession();
	####  Load In
	foreach my $key (keys %cses){
		$in{$key} = $cses{$key};
		$va{'debug_ad'} .= qq|$key -> $cses{$key}<br>|;
	}

	$in{'email_and_cellphone_use'}=$cfg{'email_and_cellphone_use'};

	## WS earcalls
	&load_earcall_interval();

	### Update Bar
	for my $i(0..10){
		if ($in{'step'} >= 9){
			if ($i >=9){
				$va{'classstep'.$i} = '_red';
			}else{
				$va{'classstep'.$i} = '_ok';
			}
			$va{'linkstep'.$i} = '';
		}elsif($in{'step'} eq $i){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif($i eq 8 and ($in{'step'} eq '8c' or $in{'step'} eq '8rd')){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif($i eq 7 and ($in{'step'} eq '7a' or $in{'step'} eq '7b' or $in{'step'} eq '7f' or $in{'step'} eq '7i')){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif($i eq 3 and ($in{'step'} eq '3a')){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif($i eq 4 and ($in{'step'} eq '4us' or $in{'step'} eq '4mx' or $in{'step'} eq '4pr' or $in{'step'} eq '4ot' or $in{'step'} eq '4dis')){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif($i eq 5 and ($in{'step'} eq '5us' or $in{'step'} eq '5mx' or $in{'step'} eq '5pr' or $in{'step'} eq '5ot' or $in{'step'} eq '5dis')){
			$va{'classstep'.$i} = '_red';
			$va{'linkstep'.$i} = '';
		}elsif ($i < $in{'step'} or $cses{'status'.$i} eq 'ok'){
			$va{'classstep'.$i} = '_ok';
			$va{'linkstep'.$i} = "onClick=\"trjump('/cgi-bin/mod/sales/admin?cmd=console_order&step=$i')\"";
			$va{'linkstep'.$i} = "" if($cses{'session_closed'});
		}else{
			$va{'classstep'.$i} = '';
			$va{'linkstep'.$i} = '';
		}
	}
	if ($in{'step'} == 11) {
		$va{'id_salesorigins'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_salesorigins');
	}

	$in{'step'} = $in{'step'}.'rd' if ($in{'step'} >= 8 and $in{'step'} != 11 and lc($cses{'pay_type'}) eq "rd");

	$va{'salesorigins.channel'} = &load_name("sl_salesorigins","ID_salesorigins",$cses{'id_salesorigins'},"channel") if($cses{'id_salesorigins'});

	###
	print "Content-type: text/html\n\n";
	print &build_page("console_order$in{'step'}.html");

	(!$cses{'step'.$in{'step'}.'_time'}) and($cses{'step'.$in{'step'}.'_time'} = &get_sec());

	&save_callsession();
}


##################################################################
############                HOME                 #################
##################################################################
sub chgmode {
# --------------------------------------------------------
	if ($usr{'mode'} eq 'in'){
		$usr{'mode'} = 'out';
	}else{
		$usr{'mode'} = 'in';
	}
	&save_auth_data;
	&console;
}

sub chgexten {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'passnum'} = '----';
		my ($sth) = &Do_SQL("SELECT extension FROM admin_users WHERE extenpass='0' AND ID_admin_users='$usr{'id_admin_users'}'");
		$usr{'extension'} = $sth->fetchrow();
		if ($usr{'extension'}){
			&save_auth_data;
			$va{'message'} = &trans_txt('extenlogin_ok');
		}else{
			$va{'message'} = &trans_txt('extenlogin_error');
		}
	}elsif($usr{'extension'}){
		$va{'passnum'} = '----';
		$va{'message'} = &trans_txt('extenlogin_ok');
	}else{
		srand( time() ^ ($$ + ($$ << 15)) );
		$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");
		while ($sth->fetchrow() !=0){
			$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
			$sth = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");	
		}
		$sth = &Do_SQL("UPDATE admin_users SET extenpass='$va{'passnum'}' WHERE ID_admin_users='$usr{'id_admin_users'}'");	
	}
	
	print "Content-type: text/html\n\n";
	print &build_page("chg_exten.html");
}


##################################################################
############          GENERAL COMMANDS           #################
##################################################################
sub mypass {
# --------------------------------------------------------
#Last modified on 16 Dec 2010 11:16:39
#Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
#Last modified on 17 Dec 2010 14:02:02
#Last modified by: MCC C. Gabriel Varela S. :Se actualiza también campo de tabla change_pass a 'No'
	if ($in{'action'}){
        ### Check Permissions
        #GV Modificación: Se incluye segundo parámetro a la función _ccinb
		if ($in{'oldpass'}){
			use Digest::SHA1;
			my $sha1= Digest::SHA1->new;
			$sha1->add($in{'oldpass'});
			my $password = $sha1->hexdigest;
			my ($sth) = &Do_SQL("SELECT Password FROM admin_users WHERE ID_admin_users=$usr{'id_admin_users'}");
			my ($pass) = $sth->fetchrow();
			if ((length($pass)==13 and $pass eq crypt($in{'oldpass'},substr(crypt($in{'oldpass'},'ns'),3,7)))or(length($pass)==40 and $pass=$password)){
				if ($in{'newpass1'} eq $in{'newpass2'} and length($in{'newpass1'})>=5 and length($in{'newpass1'})<=10){
					$sha1->reset;
					$sha1->add($in{'newpass1'});
					my ($cpass) = $sha1->hexdigest;
					my ($sth) = &Do_SQL("UPDATE admin_users SET Password='".&filter_values($cpass)."',change_pass='No' WHERE ID_admin_users=$usr{'id_admin_users'}");
					$usr{'change_pass'}='No';
					&save_auth_data;
					$va{'message'} = &trans_txt("password_updated");
					&auth_logging("password_updated",'');
					&chg_multipass(&load_name("admin_users","ID_admin_users",$usr{'id_admin_users'},"userName"),$cpass);
				}else{
					$va{'message'} = &trans_txt("invalid_new_pass");
				}
			}else{
				$va{'message'} = &trans_txt("invalid_old_pass");
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page("mypass.html");
}

sub mylogs {
# --------------------------------------------------------
    ### Check Permissions


	&connect_db;
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE ID_admin_users='$usr{'id_admin_users'}';");
	$va{'matches'} = $sth->fetchrow();

	if ($va{'matches'}>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_admin'}", $va{'matches'}, $usr{'pref_maxh'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE admin_logs.ID_admin_users='$usr{'id_admin_users'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'LogDate'}."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})." $rec->{'Action'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}

	}else{
		$va{'searchresults'} = "		<tr>\n		    <td align='center' colspan='6'><p>&nbsp;</p>" . trans_txt('search_nomatches') . "<p>&nbsp;</p></td>\n		 </tr>\n";
		$va{'pageslist'} = 0;
		$va{'matches'}     = 0;
	}


	print "Content-type: text/html\n\n";
	print &build_page("mylogs.html");
}

sub mycdr {
# --------------------------------------------------------
    ### Check Permissions
    #GV Modificación: Se incluye segundo parámetro a la función _ccinb

    my ($tech,$num) = split(/\//,$usr{'extension'});
    if ($num>0){
        &connect_db;
        $sth = &Do_SQL("SELECT COUNT(*) FROM cdr WHERE src='$num' or dst='$num';");
        $va{'matches'} = $sth->fetchrow();
    }
	if ($va{'matches'}>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_admin'}", $va{'matches'}, $usr{'pref_maxh'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($sth) = &Do_SQL("SELECT * FROM cdr WHERE  src='$num' or dst='$num' ORDER BY calldate DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'calldate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'src'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'dst'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'channel'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'disposition'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'duration'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'searchresults'} = "		<tr>\n		    <td align='center' colspan='6'><p>&nbsp;</p>" . trans_txt('search_nomatches') . "<p>&nbsp;</p></td>\n		 </tr>\n";
		$va{'pageslist'} = 0;
		$va{'matches'}     = 0;
	}


	print "Content-type: text/html\n\n";
	print &build_page("mycdr.html");
}


##################################################################
############                HELP                 #################
##################################################################
sub help {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page("help.html");
}

sub html_console_unauth {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page("unauth.html");
}

#GV Inicia
sub newregisterorders
{
	#Acción: Creación
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 11/abr/2008 10:57AM GMT -0500
	# Last Modified on:
	# Last Modified by:
	# Author: MCC C. Gabriel Varela S.
	# Description :  Es la función que se encargará de hacer una orden por cada producto con su servicio ligado en caso de que exista
	# Parameters :
	# Last Modified on: 03/17/09 16:39:42
	# Last Modified by: MCC C. Gabriel Varela S: Parámetros para sltv_itemshipping
	# Last Modified by RB on 12/07/2010: Se agregan parámetros para sltv_itemshipping

	$trackordernumber=&gettrackordernumber();
	$cses{'trackordernumber'}=$trackordernumber;
	#Productos normales
	my $j=0;
	for my $i(1..$cses{'items_in_basket'})
	{
		$tot_qty=0;
		$total=0;
		if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0)
		{
			$j++;
			##########################################################3
			
			##########################################################
			#################Crea la orden o preorden#################
			##########################################################
			$query = '';
			&load_cfg('sl_orders');
			for my $i(1..$#db_cols-6)
			{
				$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
			}
			#ADG
			# Voy a insertar el did dependiendo si es para mx o usa
			$add_query = '';
			$cses{'did'} = &filter_values($cses{'did'});
			$cses{'did'} = int($cses{'did'});
			if($cses{'did'} and $cses{'did'} > 9999) {				
				#$add_query .= " dnis='$cses{'did'}', ";
			}else {
				#$add_query .= " dids7='$cses{'did'}', ";
			}

			my ($sth) = &Do_SQL("INSERT INTO sl_orders SET $query $add_query StatusPrd='None',StatusPay='None',Status='Void',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			$cses{'id_orders'} =  $sth->{'mysql_insertid'};

			$relord{$cses{'items_'.$i.'_id'}}=$cses{'id_orders'};
			
			#### Creating Products

			$tot_qty += $cses{'items_'.$i.'_qty'};
			$total += $cses{'items_'.$i.'_price'}*$cses{'items_'.$i.'_qty'};
			my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'items_'.$i.'_id'}', Quantity='$cses{'items_'.$i.'_qty'}',SalePrice='$cses{'items_'.$i.'_price'}', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");

			
			#GV Inicia Modificación 22abr2008
			my @payments;
			#Calcula el número de payments para la orden: Será el número más grande de pagos entre el producto y el servicio asociado
			if($cses{'items_'.$i.'_fpago'}>1){
				$gvfppayments=$cses{'items_'.$i.'_payments'};
				@servislinked=&getsessionfieldid('servis_', '_relid', $cses{'items_'.$i.'_id'}, '');
				for(my $l=0..$#servislinked)
				{
					if($cses{'servis_'.$servislinked[$l].'_qty'}>0 and $cses{'servis_'.$servislinked[$l].'_id'}>0)
					{
						if($cses{'servis_'.$servislinked[$l].'_payments'}>$gvfppayments)
						{
							$gvfppayments=$cses{'servis_'.$servislinked[$l].'_payments'};
						}
					}
				}
			}else{
				$gvfppayments=1;
			}
			
			#Calcula el monto de los payments para los productos
			if(!$cses{'items_'.$i.'_payments'}){
				$cses{'items_'.$i.'_payments'}=1;
			}
			for (1..$cses{'items_'.$i.'_payments'}){
					($cses{'items_'.$i.'_payments'}) and ($payments[$_] += round($cses{'items_'.$i.'_price'}/$cses{'items_'.$i.'_payments'},2));
				}
			#GV Termina Modificación 22abr2008
			
			############################################################
			##################Parte de Servicios########################
			############################################################
			#Servicios
			#### Creating Services as Products
			#GV Modifica Se comenta la parte de crear servicios como producto
			#GV Modifica Se descomenta la parte de crear servicios como producto
			#Provisional
#			$tot_qty=0;
#			$total=0;
			
			for my $k(1..$cses{'servis_in_basket'}){
				if ($cses{'servis_'.$k.'_qty'}>0 and $cses{'servis_'.$k.'_id'}>0){
					if($cses{'servis_'.$k.'_relid'} eq $cses{'items_'.$i.'_id'}){
						#GV Inicia Modificación 22abr2008
						#Calcula el monto de los payments para los servicios
						if(!$cses{'servis_'.$k.'_payments'}){
							$cses{'servis_'.$k.'_payments'}=1;
						}
						for (1..$cses{'servis_'.$k.'_payments'}){
								($cses{'servis_'.$k.'_payments'}) and ($payments[$_] += round($cses{'servis_'.$k.'_price'}/$cses{'servis_'.$k.'_payments'},2));
						}
						#GV Termina Modificación 22abr2008
						
						$tot_qty += $cses{'servis_'.$k.'_qty'};
						$total += $cses{'servis_'.$k.'_price'}*$cses{'servis_'.$k.'_qty'};
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='".$relord{$cses{'servis_'.$k.'_relid'}}."',ID_products='$cses{'servis_'.$k.'_id'}', Quantity='$cses{'servis_'.$k.'_qty'}',SalePrice='$cses{'servis_'.$k.'_price'}', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					}elsif(!$cses{'servis_'.$k.'_relid'} and $j==1){
						#GV Inicia Modificación 22abr2008
						#Calcula el monto de los payments para los servicios
						if(!$cses{'servis_'.$k.'_payments'}){
							$cses{'servis_'.$k.'_payments'}=1;
						}
						for (1..$cses{'servis_'.$k.'_payments'}){
								($cses{'servis_'.$k.'_payments'}) and ($payments[$_] += round($cses{'servis_'.$k.'_price'}/$cses{'servis_'.$k.'_payments'},2));
							}
						#GV Termina Modificación 22abr2008
						$tot_qty += $cses{'servis_'.$k.'_qty'};
						$total += $cses{'servis_'.$k.'_price'}*$cses{'servis_'.$k.'_qty'};
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='".$cses{'id_orders'}."',ID_products='$cses{'servis_'.$k.'_id'}', Quantity='$cses{'servis_'.$k.'_qty'}',SalePrice='$cses{'servis_'.$k.'_price'}', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					}
				}
			}
			#GV Inicia Modificación 22abr2008
			
			my $idpacking = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3,6),'ID_packingopts');
			my $shpcal = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3,6),'shipping_table');
			my $shpdis = &load_name('sl_products','ID_products',substr($cses{'items_'.$i.'_id'},3,6),'shipping_discount');
			
			($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpdis,substr($cses{'items_'.$i.'_id'},3,6));
			$va{'shptotal1'} = $shptotal1;
			$va{'shptotal2'} = $shptotal2;
#			#$cses{'shipping_total'} = $va{'shptotal'.$in{'shp_type'}};
#			#$totshpord=$va{'shptotal'.$in{'shp_type'}};
			$totshpord=$va{'shptotal'.$cses{'shp_type'}};
#			print "St1: ".$shptotal1.", St2: ".$shptotal2.",";
#			print "A: ".$va{'shptotal'.$in{'shp_type'}}.",";
#			print "P: ".$idpacking.",";
#			print "W: ".$cses{'items_'.$i.'_weight'}.", EDT: ".$cses{'edt'}.",S: ".$cses{'items_'.$i.'_size'}."\n";
#			$in{'idpacking'}=$idpacking;
#			$in{'shptotal1'}=$shptotal1;
#			$in{'shptotal2'}=$shptotal2;
#			$in{'shptotal1pr'}=$shptotal1pr;
#			$in{'shptotal2pr'}=$shptotal2pr;
#			$in{'shp_text1'}=$va{'shp_text1'};
#			$in{'shp_text2'}=$va{'shp_text2'};
#			$in{'shp_textpr1'}=$va{'shp_textpr1'};
#			$in{'shp_textpr2'}=$va{'shp_textpr2'};
#			&cgierr;
			
			
			####Creating payment
			#print "algo";
			%paytype = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'WesternUnion','mo'=> 'Money Order','fp'=> 'Fexipago');
			#GV Modificación 22abr2008 se cambia $cses{'fppayments'} por $gvfppayments
			#GV Inicia modificación 23abr2008 se incluye en el primer payment el shipment, se quita el descuento y se incluyen los impuestos
			#GV Inicia Se calcula el descuento
			$cupon=0;
			if ($cses{'cupon'} and !$cses{'categories'})
			{
				my ($sth) = &Do_SQL("SELECT * FROM sl_coupons WHERE PublicID='$cses{'cupon'}' AND Status='Active' AND (ValidFrom <= CURDATE() AND ValidTo >= CURDATE())");
				$rec = $sth->fetchrow_hashref;
				if ($rec->{'DiscPerc'})
				{
					$cupon = int($total * $rec->{'DiscPerc'})/100;
				}
				elsif($j==1)
				{
					$cupon = $rec->{'DiscValue'};
				}
			}
			if ($cses{'items_'.$i.'_payments'} eq 1 and $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}})
			{
				$cupon += ($cses{'items_'.$i.'_price'} * $cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}})/100;
			}
			#GV Termina Se calcula el descuento
			#GV Inicia Se calculan los impuestos
			$taxes=($total-$cupon)*$cses{'tax_total'};#+0.009;
			#GV Termina Se calculan los impuestos
			$payments[1]+=$totshpord-$cupon+$taxes;
			#GV Termina modificación 23abr2008 se incluye en el primer payment el shipment, se quita el descuento y se incluyen los impuestos
			if ($cses{'pay_type'} eq 'cc' and $gvfppayments>1){
				#GV Modificación 22abr2008 se cambia $cses{'fppayments'} por $gvfppayments
				for ($p = $gvfppayments; $p >= 1; $p--){
					$query = '';
					for my $i(1..9){
						$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
					}
					#GV Inicia modificación 23abr2008 Sólo se hará cuando la orden sea la primera
					if($j==1)
					{
						#RB Start - Update the postdated fee to the 1st payment - apr2208 -
						($p == 1) and ($cfg{'postdatedfesprice'} > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($payments[$p] -= $cfg{'postdatedfesprice'}) and ($cses{'postdatedfesprice'} = $cfg{'postdatedfesprice'});
						($p == 1) and ($cfg{'postdatedfesprice'} > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($payments[$p] -= $cfg{'postdatedfesprice350'}) and ($cses{'postdatedfesprice'} = $cfg{'postdatedfesprice350'});
						#RB End
					}
					#GV Termina modificación 23abr2008 Sólo se hará cuando la orden sea la primera
					chop($query);#GV Modifica 22abr2008 Se cambia $cses{'fppayment'.$p} por $payments[$p]
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$payments[$p]',Paymentdate='$cses{'fpdate'.$p}', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				}
			}else{
				#GV Inicia modificación 23abr2008 Sólo se hará cuando la orden sea la primera
				if($j==1)
				{
					#RB Start - Update the postdated fee to the 1st payment - apr2208 -
					#GV Inicia moficiación 23abr2008 se cambia $cses{'total_order'} por $payments[$p] 
					($cfg{'postdatedfesprice'} > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($payments[1] -= $cfg{'postdatedfesprice'}) and ($cses{'postdatedfesprice'} = $cfg{'postdatedfesprice'});
					($cfg{'postdatedfesprice'} > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($payments[1] -= $cfg{'postdatedfesprice350'}) and ($cses{'postdatedfesprice'} = $cfg{'postdatedfesprice350'});
					#GV Termina moficiación 23abr2008 se cambia $cses{'total_order'} por $payments[$p] 
					#RB End
				}
				#GV Termina modificación 23abr2008 Sólo se hará cuando la orden sea la primera
				$query = '';
				for my $i(1..9){
					$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
				}
				chop($query);
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$payments[1]', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			}
			## Update Totals
			my ($sth) = &Do_SQL("UPDATE sl_orders SET OrderDisc='$cupon',OrderQty='$tot_qty',OrderShp='$totshpord',OrderTax='$cses{'tax_total'}',OrderNet='$total' WHERE ID_orders='$cses{'id_orders'}'");
			#GV Termina Modificación 23abr2008 se ponen los totales de descuento e impuestos de acuerdo a cálculos
			#GV Termina Modificación 22abr2008
			## Logs
			$in{'db'} = 'sl_orders';
			&auth_logging('opr_orders_added',$cses{'id_orders'});
			#GV Inicia 23abr2008
#			$in{'cupon'}=$cupon;
#			$in{'taxes'}=$taxes;
#			$in{'payments1'}=$payments[1];
#			&cgierr;
			#GV Termina 23abr2008			
			##########################################################3
		}
	}
}

sub gettrackordernumber{
	#Acción: Creación
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: 
	# Created on: 11/abr/2008 11:07AM GMT -0500
	# Last Modified on:
	# Last Modified by:
	# Author: MCC C. Gabriel Varela S.
	# Description :  Obtiene el número siguiente de trackingordernumber siguiente a utilizar
	# Parameters :
	my ($sth)=&Do_SQL("SELECT `trackordernumber`+1 FROM `sl_orders` order by `trackordernumber` desc limit 1");
	return $sth->fetchrow();
}

#GV Termina


1;

