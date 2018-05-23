##################################################################
############              CONSOLE                #################
##################################################################
sub console {
# --------------------------------------------------------
	$cses{'start_sec'} = &get_sec();
	$cses{'items_in_basket'} = 0;
	$cses{'sameshipping'} = "same";
	$cses{'id_salesorigins'} = $in{'origin'} if ($in{'origin'} and !$cses{'id_salesorigins'});
	$cses{'pterms'} = 'Contado' if($in{'e'} == 2 or $in{'e'} == 10 and !$cses{'pterms'});
	$cses{'currency'} = 'MX$' if($in{'e'} == 2 or $in{'e'} == 10 and !$cses{'currency'});
	$va{'salesorigins.channel'} = &load_name("sl_salesorigins","ID_salesorigins",$cses{'id_salesorigins'},"channel") if($cses{'id_salesorigins'});
	&create_inorder();
	&save_callsession();
	
	print "Content-type: text/html\n\n";	
	$va{'tblw'} = $sys{'console_'.$usr{'application'}.'tbl'};

	$va{'mfw'} = $sys{'console_'.$usr{'application'}.'mfw'};
	$va{'mfh'} = $sys{'console_'.$usr{'application'}.'mfh'};
	$va{'stw'} = $sys{'console_'.$usr{'application'}.'stw'};
	$va{'sth'} = $sys{'console_'.$usr{'application'}.'sth'};

	#### WS earcalls
	&load_earcall_interval();

	
	print &build_page("console.html");
}

sub recv_cmd {
# --------------------------------------------------------
# Last Modified on: 05/06/09 17:11:06
# Last Modified by: MCC C. Gabriel Varela S: Se quita inserción en CDR que se había hecho previamente
	print "Content-type: text/html\n\n";
#	for (1..60){
#		if (open (TXT, "<$cfg{'auth_dir_newcall'}$usr{'extension'}.txt")){
#			$line = <TXT>;
#			print $line;
#			close TXT;
#			unlink("$cfg{'auth_dir_newcall'}$usr{'extension'}.txt");
#			@ary = split(/\|/,$line);
#			print qq|<script type="text/javascript">\n
#						parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=1&action=1&cid=$ary[0]&did=$ary[1]";
#					</script>\n|;
##			&Do_SQL("INSERT INTO cdr (calldate ,clid ,src ,dst ,dcontext ,channel ,dstchannel ,lastapp ,lastdata ,duration ,billsec ,disposition ,amaflags ,accountcode ,uniqueid ,userfield )
##VALUES (Curdate(), '$ary[0]', '$ary[1]', '', '', '', '', '', '', '0', '0', '', '0', 'From external PBS', '', '');");
#			exit;
#		}
#		sleep(1);
#	}
#	print qq|<script type="text/javascript">\n
#		this.location.href = "/cgi-bin/mod/sales/admin?cmd=recv_cmd";
#	</script>\n|;
}

sub recv_cc {
# --------------------------------------------------------
	my (%tmp);
	my ($status, $msg, $code);
	my ($num_of_retries) = 2;
	&load_callsession();
	
	if (!$cses{'postdated'}){

		print "Content-type: text/html\n\n";
		#foreach $key (keys %cses){
		#	print "$key : $cses{$key}<br>";
		#}
		#foreach $key (keys %in){
		#	print "IN: $key : $in{$key}<br>";
		#}
		my ($id_orders, $id_orders_payments);
		$id_orders = $cses{'id_orders'};
		
		my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE (Captured != 'Yes' OR Captured IS NULL) AND ID_orders='$id_orders' ORDER BY Paymentdate ASC LIMIT 1");
		$id_orders_payments = $sth->fetchrow;

		require ("../../common/apps/cybersubs.cgi");
		if( $in{'activar_puntos'} and $in{'activar_puntos'} eq 'on' ){
			($status, $msg, $code) = &sltvcyb_auth($id_orders, $id_orders_payments,$in{'activar_puntos'},$in{'used_points'},$in{'consultas'},$in{'auth-codes'});
		}else{
			($status, $msg, $code) = &sltvcyb_auth($id_orders, $id_orders_payments);
		}
		# &cgierr($in{'activar_puntos'});

		# Log in each attempts to collect
		$in{'db'} = "sl_orders";
		&auth_logging(&trans_txt('attempts_to_collect').', ID sent:'.$id_orders_payments, $id_orders);

		$code = int($code);
		
		
		&add_order_notes_by_type($id_orders,"Status=".&filter_values($status).", Msg=".&filter_values($msg).", Code=".&filter_values($code).", Retries=$cses{'retries'}","Low");

	}else{
		# Only for Postdated orders
		$status = 'OK';
	}

	++$cses{'retries'};
	$cses{'status9cc'} = 1 if lc($status) eq 'ok';
	&save_callsession();
	# cgierr("($status, $msg, $code)");

	if ($status ne 'OK' and $cses{'retries'}<=$num_of_retries){
		print qq|<script type="text/javascript">\n
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=7&check_payment=1&reasoncode=$msg";
		</script>\n|;
	}elsif($cses{'retries'}>$num_of_retries or $in{'nomoreretries'}){
		print qq|<script type="text/javascript">\n
			localStorage.clear()
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=9&check_payment=1&reasoncode=$msg";
		</script>\n|;
	}else{
		#$cses{'retries'} = $num_of_retries+1;
		print qq|<script type="text/javascript">\n
			localStorage.clear();
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=9&check_payment=1&reasoncode=$msg";
		</script>\n|;
	}
}


sub recv_ck {
# --------------------------------------------------------
	my (%tmp);
	print "Content-type: text/html\n\n";
	for (1..60){
		if (open (TXT, "<$cfg{'auth_dir_cc'}$sid")){
			LINE: while (<TXT>) {
				$line = $_;
				$line =~ s/\r|\n//g;
				($line =~ /([^=]+)=(.*)/) or (next LINE);
				$tmp{$1} = $2;
			}
			close TXT;
			if ($tmp{'decision'} eq 'REJECT'){
				print qq|<script type="text/javascript">\n
				parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=7&check_payment=1";
			</script>\n|;				
			}else{
				print qq|<script type="text/javascript">\n
				parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=9&check_payment=1";
			</script>\n|;
			}
			exit;
		}
		
		sleep(1);
	}
	print qq|<script type="text/javascript">\n
		this.location.href = "/cgi-bin/mod/sales/admin?cmd=recv_ck";
	</script>\n|;
}

sub recv_lay {
# --------------------------------------------------------
	my (%tmp);
	&load_callsession();
	## Logs
	$in{'db'} = 'sl_orders';
	my ($num_of_retries) = 2;
	print "Content-type: text/html\n\n";
	#foreach $key (keys %cses){
	#	print "$key : $cses{$key}<br>";
	#}
	#foreach $key (keys %in){
	#	print "IN: $key : $in{$key}<br>";
	#}
	my ($id_orders, $id_orders_payments);
	$id_orders = $cses{'id_orders'};
	
	my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders='$id_orders' ORDER BY Paymentdate ASC LIMIT 0,1");
	$id_orders_payments = $sth->fetchrow;
	require "../../common/apps/cybersubs.cgi";
#	use CyberSource::SOAPI;
#	%config = cybs_load_config( $cfg{'path_cybersource'}.'cybs.ini' );
	
	my ($status,$msg,$code) = &sltvcyb_sale($id_orders,$id_orders_payments);
	#print "$id_orders - $id_orders_payments <br>Status : $status<br>msg: $msg<br>code: $code<br>".&trans_txt('cc_problem') . &cybersource_codes($code,%tmp);
	++$cses{'retries'};
	&save_callsession();
	#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders',Notes='$status,$msg,$code $cses{'retries'}',Type='Low',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	if ($status ne 'OK' and $cses{'retries'}<=$num_of_retries){
		print qq|<script type="text/javascript">\n
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=7&check_payment=1&reasoncode=$code";
		</script>\n|;
	}elsif($cses{'retries'}>$num_of_retries or $in{'nomoreretries'}){
		print qq|<script type="text/javascript">\n
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=9&check_payment=1&reasoncode=$code";
		</script>\n|;
	}else{
		$cses{'retries'} = $num_of_retries+1;
		print qq|<script type="text/javascript">\n
			parent.location.href = "/cgi-bin/mod/sales/admin?cmd=console_order&step=9&check_payment=1&reasoncode=$code";
		</script>\n|;
	}
}

1;

