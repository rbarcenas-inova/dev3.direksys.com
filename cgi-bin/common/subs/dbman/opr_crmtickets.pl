

#############################################################################
#############################################################################
#   Function: view_opr_crmtickets
#
#       Es: Maneja el View de sl_zones
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _CH_
#
#    Modifications:
#
#   Parameters:
#
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_zones>
#
sub view_opr_crmtickets {
#############################################################################
#############################################################################
	if($in{'id_type'} eq 'orders'){
		$va{'refurl'} = "cmd=opr_orders&view=$in{'id_ref'}&tab=15#tabs";
		$in{'id_orders'} = $in{'id_ref'};
	}else{
		## locate ID_orders	
	}

	$in{'type'} = &load_db_names('sl_crmtickets_type','ID_crmtickets_type', $in{'id_crmtickets_type'}, '[Type]');	

	my ($sth) = &Do_SQL("SELECT CONCAT(FirstName, ' ', LastName) AS FullName, Email FROM admin_users WHERE id_admin_users = '$in{'id_admin_users_assigned'}';");
	($va{'name_users_assigned'}, $in{'email'} )=  $sth->fetchrow();

	
	## Update Status
	if ($in{'chgto'} and $in{'status'} !~ /closed/i and( ( $in{'chgto'} eq 'In Process' and $in{'id_admin_users_assigned'} > 0 )  or ( $in{'chgto'} =~/Closed successful|Closed unsuccessful/ ) ) ){
		
		if( $in{'chgto'} eq 'In Process') {

			if ($in{'email'} and $in{'email'} =~ /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}/) {

				$date_field = ', Date_Process = curdate() ';
				my $from_mail = ($cfg{'default_email_sender'})?$cfg{'default_email_sender'}:'info@inova.com.mx';
				my $to_mail = $in{'email'};
				my $subject_mail = 'Se te ha asignado el CRM Ticket # '.$in{'id_crmtickets'};
				my $body_mail = "
					<table border=0>
						<tr>
							<td colspan='2'><a href='http://mx.direksys.com/cgi-bin/mod/admin/dbman?cmd=opr_crmtickets&view=$in{'id_crmtickets'}'>CRM Ticket # $in{'id_crmtickets'}</a></td>
						</tr>
						<tr>
							<td><b>Created:</b></td>
							<td>$in{'date'} $in{'time'}</td>
						</tr>
						<tr>
							<td><b>ID:</b></td>
							<td>$in{'id_ref'}</a> / $in{'id_type'}</td>
						</tr>
						<tr>
							<td><b>Phone:</b></td>
							<td>$in{'caller_id'}</td>
						</tr>
						<tr>
							<td><b>Type:</b></td>
							<td>$in{'type'}</td>
						</tr>
						<tr>
							<td><b>Description:</b></td>
							<td>$in{'description'}</td>
						</tr>
					</table>
				";
				my $text_mail = '';
				
				#Se inhabilita el envio de correos temporalmente.
				#&send_mandrillapp_email($from_mail, $to_mail, $subject_mail, $body_mail, $text_mail,'none');
			}

		}elsif( $in{'chgto'} =~/Closed successful|Closed unsuccessful/ ){
			$date_field = ', Date_Close = curdate() ';
		}

		$in{'status'} = $in{'chgto'};

		my ($sth) = &Do_SQL("UPDATE sl_crmtickets SET Status='$in{'chgto'}' $date_field WHERE ID_crmtickets=$in{'id_crmtickets'}");
		&auth_logging('crmstatus_change_to'.$in{'chgto'},$in{'id_crmtickets'});
	}elsif($in{'chgto'} eq 'In Process' and $in{'id_admin_users_assigned'} eq 0){
		$va{'err_assigned'} = 'El ticket debe asignarse primero.';
	}
	## Customer Info
	my ($sth) = &Do_SQL("SELECT FirstName,LastName1,LastName2,sl_customers.Status AS CStatus,
						sl_orders.Date, sl_orders.Time, OrderNet, sl_orders.Ptype,
						sl_orders.Status AS OStatus, StatusPay, StatusPrd
						FROM sl_customers LEFT JOIN sl_orders ON sl_orders.ID_customers=sl_customers.ID_customers WHERE ID_orders = '$in{'id_orders'}' ");
	my ($rec) = $sth->fetchrow_hashref();
	$va{'custname'} = "$rec->{'FirstName'} $rec->{'LastName1'} $rec->{'LastName2'}  / $rec->{'CStatus'} ";
	$va{'orderinfo'} = "$rec->{'Time'} $rec->{'Date'}  / $rec->{'Ptype'} / ".&format_price($rec->{'OrderNet'});
	$va{'orderstatus'} = " $rec->{'OStatus'} / $rec->{'StatusPrd'} / $rec->{'StatusPay'}";
	
	## items in Order
	my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(
							CONCAT(	Quantity,' x ',Name ,'  \@ \$',SalePrice, ' + \$', Shipping, ' (',
									IF(ShpDate IS NULL,'N/A',ShpDate),' - ', sl_orders_products.Status,')')
						SEPARATOR '<br>' )
					FROM `sl_orders_products` 
							LEFT JOIN sl_products ON  sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
							WHERE ID_orders='$in{'id_orders'}'");
	$va{'orderitems'} =  $sth->fetchrow();
	if ($in{'status'} !~ /closed/i){
		$va{'change_status'} .= "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_crmtickets&view=$in{'id_crmtickets'}&chgto=In Process'>".&trans_txt('crmIn Process')."</a>" if ($in{'status'} ne 'In Process');
		$va{'change_status'} .= " <br>" if ($in{'status'} ne 'In Process');
		$va{'change_status'} .= "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_crmtickets&view=$in{'id_crmtickets'}&chgto=Closed successful'>".&trans_txt('crmClosed successful')."</a>";
		$va{'change_status'} .= " <br>";
		$va{'change_status'} .= "<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_crmtickets&view=$in{'id_crmtickets'}&chgto=Closed unsuccessful'>".&trans_txt('crmClosed unsuccessful')."</a>";
	}
	$va{'status'} = &trans_txt('crm'.$in{'status'});
	$in{'type'} = &trans_txt('opr_crmtickets_'.$in{'type'});


	my ($sth) = &Do_SQL("SELECT DATEDIFF(Date_Process, Date) AS T_ASIGNACION, 
							DATEDIFF(Date_Close, Date_Process) AS T_GESTION, 
							DATEDIFF(Date_Close, Date) AS T_SOLUCION,
							Date, Date_Process, Date_Close
						FROM sl_crmtickets WHERE ID_crmtickets = '$in{'id_crmtickets'}';");
	
	($va{'t_asignacion'}, $va{'t_gestion'}, $va{'t_solucion'}, $in{'date'}, $in{'date_process'}, $in{'date_close'}) =  $sth->fetchrow();	
	##-----------------------------------------------
	## Calcula los dias transcurridos: Asignación
	##-----------------------------------------------	
	my $dias_asig = $va{'t_asignacion'};	
	my $total_dias_asig = 0;
	if( $dias_asig ){
		for( my $i=1; $i<=$dias_asig; $i++ ){
			my $sth = &Do_SQL("SELECT DAYOFWEEK(ADDDATE('$in{'date'}', INTERVAL $i DAY)) AS xday");
			my $day = $sth->fetchrow();
			if( $day > 1 and $day < 7 ){
				$total_dias_asig++;
			}
		}
	}
	$va{'t_asignacion'} = $total_dias_asig;

	##-----------------------------------------------
	## Calcula los dias transcurridos: Gestión
	##-----------------------------------------------	
	my $dias_gest = $va{'t_gestion'};	
	my $total_dias_gest = 0;
	if( $dias_gest and $in{'date_process'} ne '0000-00-00' ){
		for( my $i=1; $i<=$dias_gest; $i++ ){
			my $sth = &Do_SQL("SELECT DAYOFWEEK(ADDDATE('$in{'date_process'}', INTERVAL $i DAY)) AS xday");
			my $day = $sth->fetchrow();
			if( $day > 1 and $day < 7 ){
				$total_dias_gest++;
			}
		}
	}
	$va{'t_gestion'} = $total_dias_gest;

	##-----------------------------------------------
	## Calcula los dias transcurridos: Solución
	##-----------------------------------------------
	my $dias_solucion = $va{'t_solucion'};
	my $total_dias_sol = 0;
	for( my $i=1; $i<=$dias_solucion; $i++ ){
		my $sth = &Do_SQL("SELECT DAYOFWEEK(ADDDATE('$in{'date'}', INTERVAL $i DAY)) AS xday");
		my $day = $sth->fetchrow();
		if( $day > 1 and $day < 7 ){
			$total_dias_sol++;
		}
	}
	$va{'t_solucion'} = $total_dias_sol;
}

#############################################################################
#############################################################################
#   Function: validate_opr_crmtickets
#
#       Es: Maneja el View de sl_zones
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _CH_
#
#    Modifications:
#
#   Parameters:
#
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_zones>
#
sub validate_opr_crmtickets { 
#############################################################################
#############################################################################
	my ($err);
	if ($in{'add'}){
		$in{'status'} = 'New';
		$in{'id_ref'} = int($in{'id_ref'});
		if ($in{'id_ref'}>0 and $in{'id_type'} eq 'orders'){
			if (load_name('sl_orders','ID_orders',$in{'id_ref'},'ID_orders') >0){
				## OK
			}else{
				$error{'id_ref'} = &trans_txt('invalid');
				++$err;
			}
		}		
	}else{
		if ($in{'status'} eq 'New' ){
		}elsif ($in{'status'} eq 'In Process' ){
			
		}else{
			$error{'status'} = &trans_txt('case_closed');
			++$err;
		}
	}
	
	return $err;
}

#############################################################################
#############################################################################
#   Function: loaddefault_opr_crmtickets
#
#       Es: Maneja el View de sl_zones
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _CH_
#
#    Modifications:
#
#   Parameters:
#
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_zones>
#
sub loaddefault_opr_crmtickets {
# --------------------------------------------------------
	$in{'status'} = 'New';
}

1;