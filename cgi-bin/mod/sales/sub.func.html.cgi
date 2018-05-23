#!/usr/bin/perl

####################################################################
########              Home Page                     ########
####################################################################
sub load_loginpage {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_operpages WHERE Type='ccinbound-Login Page' AND Status='Active'");
	if ($sth->fetchrow()>0){
		my ($sth) = &Do_SQL("SELECT Speech FROM sl_operpages WHERE Type='ccinbound-Login Page' AND Status='Active' ORDER BY ID_operpages DESC");
		return $sth->fetchrow() . "<p align='right' class='smalltxt'>ccinbound-Login Page</p>";
	}else{
		return "<p align='right' class='smalltxt'>ccinbound-Login Page</p>";
	}
}

sub load_startconsole {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_operpages WHERE Type='ccinbound-Start Console' AND Status='Active'");
	if ($sth->fetchrow()>0){
		my ($sth) = &Do_SQL("SELECT Speech FROM sl_operpages WHERE Type='ccinbound-Start Console' AND Status='Active' ORDER BY ID_operpages DESC");
		return $sth->fetchrow() . "<p align='right' class='smalltxt'>ccinbound-Start Console </p>" ;
		#return $sth->fetchrow() ;
	}else{
		return "<p align='right' class='smalltxt'>ccinbound-Start Console</p>";
	}
}


sub load_stepspeech {
# --------------------------------------------------------
# Last Modified on: 07/14/08 16:20:49
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a la función que carga las variables para los speeches

	##my (@ary) = ('null','', '2- Product Search', '3- Customer Info', '4- Billing Info', '5- Shipping Info', '6- Shipping Type', '7- Payment Info', '8- Confirm Order','9- Good Bye');
	
	&load_variables(%cses);
	my ($id_speech,$speech);
	if($cses{'id_dids'} ne ''){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_speech WHERE ID_dids='$cses{'id_dids'}' AND Status='Active'  AND Type='$va{'speechname'}' ");
		if ($sth->fetchrow()>0){
			my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE ID_dids='$cses{'id_dids'}' AND Status='Active'  AND Type='$va{'speechname'}' ORDER BY ID_speech DESC");
			$id_speech = $sth->fetchrow();
		}else{
			my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE Status='Active' AND Type='$va{'speechname'}' ORDER BY ID_speech");
			if ($sth->fetchrow()>0){
				my ($sth) = &Do_SQL("SELECT ID_speech FROM sl_speech WHERE Status='Active' AND Type='$va{'speechname'}' ORDER BY ID_speech");
				$id_speech = $sth->fetchrow();
			}
		}
	}
	
	if ($id_speech){
		$speech = &load_name('sl_speech','ID_speech',$id_speech,'Speech') . "<p align='right' class='smalltxt'>($id_speech) $va{'speechname'}</p>";
	}else{
		$speech = "<p align='center'>" .&trans_txt('no_stepspeech_available') ."</p><p align='right' class='smalltxt'>$va{'speechname'}</p>";
	}
	
	return $speech;
}

sub build_select_dids {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia Number por DNIS en sl_mediadids
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_mediadids WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'didmx'}'>$rec->{'num800'} &lt;$rec->{'didmx'}&gt;</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_select_brands {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_brands WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_brands'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_cc_users {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE Status='Active' AND application like 'cc-%' AND ID_admin_users<>'$usr{'id_admin_users'}'ORDER BY LastName;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_admin_users'}'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub customer_header {
# --------------------------------------------------------
# Last Modified on: 11/06/08 14:06:29
# Last Modified by: MCC C. Gabriel Varela S: Se muestra con una estrella cuando el cliente tiene membresía
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia Number por DNIS en sl_mediadids
# Last Modified by RB on 2011/01/10: Se agrega el zipcode a la sesion
#Last modified on 7 Jun 2011 12:48:34
#Last modified by: MCC C. Gabriel Varela S. :the in address_chosen is considered

	if ($in{'did'}){
		$in{'didname'} = &load_name('sl_mediadids','didmx',$in{'did'},'num800')
	}
	

#	&load_callsession();
	#GV Inicia modificación 11jun2008: Asigna a $in{'id_customers'} el valor de $cses{"id_customers"} siempre que exista
	$in{'id_customers'} = $cses{"id_customers"} if ($cses{"id_customers"});
	#GV Termina modificación 11jun2008

	if($cses{'zip'}) {

		#### Customer Info
		$in{'customers.id_customers'} = ($cses{'id_customers'})? $cses{'id_customers'}:$cses{'customers.id_customers'};
		$in{'customers.firstname'} = ($cses{'firstname'})? $cses{'firstname'}:$cses{'customers.firstname'};
		$in{'customers.lastname1'} = ($cses{'lastname1'})? $cses{'lastname1'}:$cses{'customers.lastname1'};
		$in{'customers.lastname2'} = ($cses{'lastname2'})? $cses{'lastname2'}:$cses{'customers.lastname2'};

		$in{'customers.phone1'} = ($cses{'phone1'})? $cses{'phone1'}:$cses{'customers.phone1'};
		$in{'customers.phone2'} = ($cses{'phone2'})? $cses{'phone2'}:$cses{'customers.phone2'};
		$in{'customers.cellphone'} = ($cses{'cellphone'})? $cses{'cellphone'}:$cses{'customers.cellphone'};


		#### Address
		$in{'customers.address1'} = ($cses{'address1'})? $cses{'address1'}:$cses{'customers.address1'};
		$in{'customers.address2'} = ($cses{'address2'})? $cses{'address2'}:$cses{'customers.address2'};
		$in{'customers.address3'} = ($cses{'address3'})? $cses{'address3'}:$cses{'customers.address3'};
		$in{'customers.urbanization'} = ($cses{'urbanization'})? $cses{'urbanization'}:$cses{'customers.urbanization'};
		$in{'customers.city'} = ($cses{'city'})? $cses{'city'}:$cses{'customers.city'};
		$in{'customers.state'} = ($cses{'state'})? $cses{'state'}:$cses{'customers.state'};
		$in{'customers.zip'} = ($cses{'zip'})? $cses{'zip'}:$cses{'customers.zip'};


		$cses{'zipcode'} = $in{'customers.zip'};
		return &build_page("customer_header.html");

	}elsif ($in{'id_customers'} ){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
		if ($sth->fetchrow() >0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
			my ($tmp) = $sth->fetchrow_hashref();
			foreach my $key (keys %{$tmp}){
# 				if!($in{"customers.".lc($key)}=~/address/ and $in{'address_chosen'}==1 and $in{"customers.".lc($key)}=~/city/ and $in{"customers.".lc($key)}=~/state/ and $in{"customers.".lc($key)}=~/zip/)
				if(!($in{'address_chosen'}==1 and ($key=~/address/gi or $key=~/zip/gi or $key=~/city/gi or $key=~/state/gi)))
				{
					$in{"customers.".lc($key)} = $tmp->{$key};
				}	
			} 		
			if($in{"customers.type"}eq"Membership" or $cses{'type'}eq"Membership")
			{
				$va{'membership'}="<img src='$va{'imgurl'}/app_bar/small_bookmarks.gif' title='Membership' alt='Member' border='0'>";
			}
			$cses{'zipcode'} = $in{'customers.zip'};
			return &build_page("customer_header.html");
		}

	}else{
	    delete($cses{'zipcode'}) if $cses{'zipcode'};
		return &build_page("customer_header_n.html");
	}
}

sub build_origins_list{
#-----------------------------------------
# Created on: 07/06/09  17:26:07 By  Roberto Barcenas
# Forms Involved: 
# Description : Crea los links para iniciar consola de acuerdo a los canales de venta creados
# Parameters : 	
# 01102014::Alejandro DIaz::Se agrega restriccion de consolas por empresa y por usuario
	
	my ($strout);
	my $add_sql;

	if ($cfg{'use_salesorigins_restriction'} and $cfg{'use_salesorigins_restriction'} == 1){

		$sth = &Do_SQL("SELECT ID_salesorigins FROM admin_users WHERE ID_admin_users='$usr{'id_admin_users'}';");
		my ($id_origins_limit) = $sth->fetchrow();
		$id_origins_limit =~ s/\|/\,/g;
		$add_sql = ($id_origins_limit)? " AND ID_salesorigins IN($id_origins_limit)":"";

	}
	
	my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins WHERE Status='Active' $add_sql ORDER BY ID_salesorigins;");
	while(my ($id_origins,$channel) = $sth->fetchrow()){
		$strout .=qq|<a href="/cgi-bin/mod/sales/admin?cmd=console&origin=$id_origins" class=acormenu> &nbsp; <span style="text-transform: capitalize;">$channel</span></a>|;
	}

	return $strout;
}

sub build_origins_list_v2{
#-----------------------------------------
# Created on: 04/04/2016  By  Gilberto Quirino
# Description : Crea los links para iniciar consola de acuerdo a los canales de venta creados para el Nuevo Sales(TMK Trainning)

	
	my ($strout);
	my $add_sql;

	if( $cfg{'new_sales'} and $cfg{'new_sales'} == 1 ){
		if ($cfg{'use_salesorigins_restriction'} and $cfg{'use_salesorigins_restriction'} == 1){

			$sth = &Do_SQL("SELECT ID_salesorigins FROM admin_users WHERE ID_admin_users='$usr{'id_admin_users'}';");
			my ($id_origins_limit) = $sth->fetchrow();
			$id_origins_limit =~ s/\|/\,/g;
			$add_sql = ($id_origins_limit)? " AND ID_salesorigins IN($id_origins_limit)":"";

		}
		
		my ($sth) = &Do_SQL("SELECT ID_salesorigins,LOWER(Channel)Channel FROM sl_salesorigins WHERE Status='Active' $add_sql ORDER BY ID_salesorigins;");
		while(my ($id_origins,$channel) = $sth->fetchrow()){		
			$strout .=qq|<a href="/cgi-bin/mod/sales/admin?cmd=console_sales&id_salesorigins=$id_origins" class="button_channel button_black">$channel</a>|;
		}
		$strout .= '<br>';
	}

	return $strout;
}


sub set_origin_default{
#-----------------------------------------
# Created on: 07/06/09  17:42:06 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	
# Last Time Modified By RB on 3/1/10 5:42 PM : Se concatena la variable $va{'extracfg'} que procede de flash_calls
	
	my ($sth) = &Do_SQL("SELECT ID_salesorigins FROM sl_salesorigins WHERE Status='Active' ORDER BY ID_salesorigins LIMIT 1;");
	
	if($va{'extracfg'}){
	    return $sth->fetchrow().$va{'extracfg'};
	}else{
	    return $sth->fetchrow()
	}
}

sub load_rewards{
#-----------------------------------------
# Created on: 27/02/2012  12:07 By OS
# Forms Involved: 
# Description : Devuelve HTML para presentar las recompensas de la quincena y las recompensas potenciales
# Parameters : 	
# Last Time Modified by RB on 04/10/2012: Se agrega calculo de bonos/descuentos por datos completos
# Last Time Modified by RB on 05/14/2012: Se agrega calculo de bono 2 meses atras

	my $rewards = '';

	if( int($cfg{'rewards_flag'}) == 1 ){

		my $day, $day_start, $day_end, $month, $year, $lastday, $percentage_shipped, $percentage_noshipped,$porc_error;
		my @ary_month = ("","Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre");
		
		## This Period
		my ($day_start,$day_end) = &calculate_dates;
		my ($total_orders_tdc, $base_order, $base_sale, $pot_base_sale, $pbase_order, $pbase_sale, $bonus_data, $discount_data, $bono_ticket, $pot_bono_ticket, $bono_tdc, $pot_bono_tdc, $ticket_prom, $pot_ticket_prom, $Conv_TDC, $pot_Conv_TDC,$orders_data, $bonus_data_qty, $bonus_data_amt, $discount_data_qty, $discount_data_amt,$pot_orders_data, $pot_bonus_data_amt, $pot_discount_data_amt, $qty_sales, $total_sales, $str_orders, @ary_orders) = &agent_reward($usr{'id_admin_users'},$day_start,$day_end);
		
		## Last Period x2
		my ($day_startp2,$day_endp2) = &calculate_dates(0,0,'lastx2');
		my ($table_lastx2_reward)=load_last_rewards('lastx2');
		my ($sth) = &Do_SQL("SELECT MONTH('$day_startp2')AS Period;");
		my ($period_lastx2) = $sth->fetchrow(); 
		
		## Last Period
		my ($day_startp,$day_endp) = &calculate_dates(0,0,'last');
		my ($table_last_reward)=load_last_rewards('last');
		my ($sth) = &Do_SQL("SELECT MONTH('$day_startp')AS Period;");
		my ($period_last) = $sth->fetchrow(); 


		# Rewards this order
		if ($in{'id_orders'}) {
			my $id_orders_num = $in{'id_orders'};
			$id_orders_num =~ s|\D||g;
			$ordernet = &load_name("sl_orders","ID_orders",$id_orders_num,"OrderNet");

			$reward_ao =  $ordernet * $pbase_order/100;
			$reward_potential_ao = $ordernet * ($pbase_sale + $pot_bono_ticket + $pot_bono_tdc)/100;

			$rewards .= "<tr><td colspan='2'><strong><font color='#555555'>Esta Orden $day_start,$day_end</font></strong></td></tr>\n";
			$rewards .= "<tr><td colspan='2'>&nbsp;&nbsp;&nbsp; Comisi&oacute;n ($pbase_order \%) ".&format_price($reward_ao)."</td></tr>\n";
			$rewards .= "<tr><td colspan='2'>&nbsp;&nbsp;&nbsp; Comisi&oacute;n Orden Entregada + ".&format_price($reward_potential_ao)." (Pendiente de Entrega)</td></tr>\n";
		} # End if in{'id_orders'}

		#$rewards .= "<tr><td>Sum Rewards </td><td>".&format_price($base_order)."</td></tr>\n";
		#$rewards .= "<tr><td>Potential Rewards </td><td>".&format_price($pot_base_sale)."</td></tr>\n";


		if ($pbase_order && $pbase_sale) {
			$rewards .= qq|<tr style="background-color:#6D929B;color:#F5FAFA;">
							<td align="center" colspan="2"><h3>Mis Comisiones (MX\$)</h3></td>
						</tr>
						<tr style="background-color:#6D929B;color:#F5FAFA;">
							<td width="50%" align="center"><h3>$ary_month[$period_lastx2]<br>$day_startp2 a $day_endp2</h3></td>
							<td align="center"><h3>$ary_month[$period_last]<br>$day_startp a $day_endp </h3></td>
						</tr>|;

			$rewards .= "<tr><td colspan='2'><table align='center' width='100%'><tr>";

			## Last Period x2
			$rewards .= "<td width='50%' valign='top'><table aling='center'>\n";
			$rewards .= $table_lastx2_reward;
			$rewards .= "</table>\n";
			
			## Last Period
			$rewards .= "<td width='50%' valign='top'><table aling='center'>\n";
			$rewards .= $table_last_reward;
			$rewards .= "</table>\n";

			$rewards .= "</td></tr></table></td></tr>";


			$rewards .= qq|<tr style="background-color:#6D929B;color:#F5FAFA;">
							<td align="center" colspan="2"><h3>Ciclo Actual<br>$day_start a $day_end </h3></td>
						</tr>|;

			## This Period
			$rewards .= "<td valign='top' colspan='2'><table aling='center'>\n";
			$rewards .= "<tr><td><strong><font color='#555555'>Acumulado</font></strong> <a href='#' title='Ver Detalle' rel='#overlay_thisperiod'><img src='$va{'imgurl'}/app_bar/small_phpbrain.gif'></a></td></tr>\n";
			$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Comisi&oacute;n Proyectada: ".&format_price($base_order+$base_sale+$bonus_data_amt)." (*) </td></tr>\n";
			#$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Comisi&oacute;n Proyectada: ".&format_price($base_order+$base_sale+$bonus_data_amt-$discount_data_amt)." (*) </td></tr>\n";
			$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Comisi&oacute;n Potencia + ".&format_price($pot_base_sale+$pot_bonus_data_amt)." (*)</td></tr>\n";
			$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Ticket Promedio: ".&format_price($ticket_prom)."</td></tr>\n";
			$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; \% TDC: ".round(100*$Conv_TDC,2)."%</td></tr>\n";
			$rewards .= "<tr><td>&nbsp;</td></tr>\n";
			$rewards .= "<tr><td><div style='font-size:x-small'>(*) Comisi&oacute;n puede variar basado en \% TDC y Ticket Promedio. </div></td></tr>\n";
			$rewards .= "</table>\n";


			$va{'rewards_this_period'} = '<table border="0" align="center" width="95%" class="container_white" style="background-color:#FDFDF0;">
									<tr style="line-height:30px;" class="menu_bar_title">
										<td align="center" width="30%">Ordenes por Status</td>
										<td align="center" width="15%">Cantidad</td>
										<td align="center" width="25%">Monto</td>
										<td align="center" width="30%">Comision ('.$pbase_order.' %)</td>
									</tr>';

			my @ary_data_orders = split(/\|/,$str_orders);
			my $total_orders_qty=0; my $total_orders_amt=0; my $total_orders_tdc=0; my $total_orders_bonus=0;
			for my $i(0..$#ary_orders){

				$this_status = $ary_orders[$i];
				my ($qty,$amt,$tdc) = split(/;/,$ary_data_orders[$i]);
				my $this_bonus = $this_status !~ /Void|System/ ? ($pbase_order / 100 * $amt) : 0;
				#my $this_bonus = ($pbase_order / 100 * $amt);

				$total_orders_qty += $qty;
				$total_orders_amt += $amt;
				$total_orders_tdc +=  $tdc;
				#$total_orders_tdc +=  $this_status !~ /Void|System/ ? $tdc : 0;
				$total_orders_bonus += $this_bonus;

				$va{'rewards_this_period'} .= '<tr>
										<td valign="bottom" align="left">'.$this_status.'</td>
										<td valign="bottom" align="right">'.$qty.'</td>
										<td valign="bottom" align="right">'.&format_price($amt).'</td>
										<td valign="bottom" align="right">MX'.&format_price($this_bonus).'</td>
									</tr>';
				$i++;
			}
			if ($total_orders_qty>0){
				$porc_error = $discount_data_qty / $total_orders_qty;
			}else{
				$porc_error = 0;
			}
			$va{'rewards_this_period'} .= '<tr style="background-color:#CCC;line-height:15px;">
									<td valign="bottom" align="left"><strong>Total</strog></td>
									<td valign="bottom" align="right"><strong>'.$total_orders_qty.'</strog></td>
									<td valign="bottom" align="right"><strong>'.&format_price($total_orders_amt).'</strog></td>
									<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($total_orders_bonus).'</strog></td>
								</tr>
								</tr><td colspan="4">&nbsp;</td></tr>
								<tr>
									<td valign="bottom" align="left">Ticket Promedio</td>
									<td valign="bottom" align="right">'.&format_price($ticket_prom).'</td>
									<td valign="bottom" align="right">% Bono Ticket</td>
									<td valign="bottom" align="right">'.&round($bono_ticket,2).'%</td>
								</tr>
								<tr>
									<td valign="bottom" align="left">% TDC</td>
									<td valign="bottom" align="right">'.&round($Conv_TDC * 100,2).'%</td>
									<td valign="bottom" align="right">% Bono TDC</td>
									<td valign="bottom" align="right">'.&round($bono_tdc,2).'%</td>
								</tr>
								<tr>
									<td valign="bottom" align="left">Ordenes con Datos</td>
									<td valign="bottom" align="right">'.$bonus_data_qty.' x '.&format_price($bonus_data).'</td>
									<td valign="bottom" align="right">Bono Datos</td>
									<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($bonus_data_amt).'</strong></td>
								</tr>
								<tr>
									<td valign="bottom" align="left">% Error Ordenes</td>
									<td valign="bottom" align="right">'.&round( $porc_error * 100, 2).'%</td>
									<td valign="bottom" align="left" colspan="2">&nbsp;</td>
								</tr>
								</tr><td colspan="4">&nbsp;</td></tr>
								<tr class="menu_bar_title">
									<td align="center">Ordenes Entregadas</td>
									<td align="center">Cantidad</td>
									<td align="center">Monto</td>
									<td align="center" valign="bottom">Comision<br> <span style="font-size:80%;font-weight:normal">( '.$pbase_sale.'% + '.&round($bono_ticket,2).'% + '. &round($bono_tdc,2) .'% )</span></td>
								</tr>
								<tr>
									<td valign="bottom" align="left">Totales</td>
									<td valign="bottom" align="right">'.$qty_sales.'</td>
									<td valign="bottom" align="right">'.&format_price($total_sales).'</td>
									<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($base_sale).'</strong></td>
								</tr>
								</tr><td colspan="4">&nbsp;</td></tr>
								<td colspan="2" align="center"><h2>Comision Total</h2></td>
								<td valign="bottom" align="right" style="color:green;"><h2>MX'.&format_price($base_order+$base_sale+$bonus_data_amt).'</h2></td>
								<td valign="bottom" align="right">&nbsp;</td>
								</table>
								&nbsp
								';

			


		} # End if $pbase_order, $pbase_sale 4641.68

	}
	
	return $rewards;
}


sub load_last_rewards{
#-----------------------------------------
# Created on: 07/03/2012  12:07 By Roberto Barcenas
# Forms Involved:
# Description : Devuelve HTML para presentar los bonos del ciclo pasado
# Parameters :
# Last Time Modified by RB on 04/10/2012: Se agregan bonos/descuentos por datos completos

	my ($period) = @_;

	my ($day_start,$day_end) = &calculate_dates(0,0,$period);
	my ($rewards,$porc_error);

	my ($sth) = &Do_SQL("SELECT * FROM sl_rewards_lastperiod WHERE From_date='$day_start' AND To_date='$day_end' AND ID_admin_users='$usr{'id_admin_users'}';");

	if($sth->rows() == 0){
		return '';
	}

	my($rec) = $sth->fetchrow_hashref();
	#$rec->{'Discount_data'} *= -1;
	 #/ ".&format_price($rec->{'Discount_data'})."

	$rewards .= "<tr><td><strong><font color='#555555'>Completado </font></strong> <a href='#' title='Ver Detalle' rel='#overlay_".$period."period'><img src='$va{'imgurl'}/app_bar/small_phpbrain.gif'></a></td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Ordenes: $rec->{'Orders_qty'} / ".&format_price($rec->{'Orders_amount'})."</td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Ventas: $rec->{'Sales_qty'} / ".&format_price($rec->{'Sales_amount'})."</td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; \% TDC: $rec->{'Conv_tdc'}%</td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Ticket Promedio: ".&format_price($rec->{'Ticket_prom'})."</td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Datos Completos: ".&format_price($rec->{'Bonus_data'})."</td></tr>\n";
	$rewards .= "<tr><td>&nbsp;&nbsp;&nbsp; Comision Asegurada : ".&format_price($rec->{'Bonus_amount'})."</td></tr>\n";

	my ($pbase_order, $pbase_sale, $bono_ticket, $bono_tdc, $bonus_data, $discount_data) = split(/\|/, $rec->{'Bonus_factors'});
	my ($bonus_data_qty, $discount_data_qty) = split(/\|/,$rec->{'Data_factors'});
	my $base_sale  = round($pbase_sale + $bono_ticket + $bono_tdc,2) * $rec->{'Sales_amount'} / 100;

	$va{'rewards_'.$period.'_period'} = '<table border="0" align="center" width="95%" class="container_white" style="background-color:#FDFDF0;">
								<tr style="line-height:30px;" class="menu_bar_title">
									<td align="center" width="30%">Ordenes por Status</td>
									<td align="center" width="15%">Cantidad</td>
									<td align="center" width="25%">Monto</td>
									<td align="center" width="30%">Comision ('.$pbase_order.' %)</td>
								</tr>';

	my $total_orders_qty=0; my $total_orders_amt=0; my $total_orders_tdc=0; my $total_orders_bonus=0;
	my @ary_status = ('New','Processed','Pending','Shipped','Cancelled','Void','System Error');
	
	for my $i(0..$#ary_status){

		$this_status = $ary_status[$i];
		my ($qty,$amt,$tdc) = split(/\|/,$rec->{$ary_status[$i]});
		my $this_bonus = $this_status !~ /Void|System/ ? ($pbase_order / 100 * $amt) : 0;

		$total_orders_qty += $qty;
		$total_orders_amt += $amt;
		$total_orders_tdc +=  $tdc;
		#$total_orders_tdc +=  $this_status !~ /Void|System/ ? $tdc : 0;
		$total_orders_bonus += $this_bonus;

		$va{'rewards_'.$period.'_period'} .= '<tr>
								<td valign="bottom" align="left">'.$this_status.'</td>
								<td valign="bottom" align="right">'.$qty.'</td>
								<td valign="bottom" align="right">'.&format_price($amt).'</td>
								<td valign="bottom" align="right">MX'.&format_price($this_bonus).'</td>
							</tr>';
		$i++;
	}
	my $total_bonus_data = $bonus_data_qty * $bonus_data;
	if ($total_orders_qty>0){
		$porc_error = $discount_data_qty / $total_orders_qty;
	}else{
		$porc_error = 0;
	}
	$va{'rewards_'.$period.'_period'} .= '<tr style="background-color:#CCC;line-height:15px;">
							<td valign="bottom" align="left"><strong>Total</strog></td>
							<td valign="bottom" align="right"><strong>'.$total_orders_qty.'</strog></td>
							<td valign="bottom" align="right"><strong>'.&format_price($total_orders_amt).'</strog></td>
							<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($total_orders_bonus).'</strog></td>
						</tr>
						</tr><td colspan="4">&nbsp;</td></tr>
						<tr>
							<td valign="bottom" align="left">Ticket Promedio</td>
							<td valign="bottom" align="right">'.&format_price($rec->{'Ticket_prom'}).'</td>
							<td valign="bottom" align="right">% Bono Ticket</td>
							<td valign="bottom" align="right">'.&round($bono_ticket,2).'%</td>
						</tr>
						<tr>
							<td valign="bottom" align="left">% TDC</td>
							<td valign="bottom" align="right">'.&round($rec->{'Conv_tdc'},2).'%</td>
							<td valign="bottom" align="right">% Bono TDC</td>
							<td valign="bottom" align="right">'.&round($bono_tdc,2).'%</td>
						</tr>
						<tr>
							<td valign="bottom" align="left">Ordenes con Datos</td>
							<td valign="bottom" align="right">'.$bonus_data_qty.' x '.&format_price($bonus_data).'</td>
							<td valign="bottom" align="right">Bono Datos</td>
							<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($total_bonus_data).'</strong></td>
						</tr>
						<tr>
							<td valign="bottom" align="left">% Error Ordenes</td>
							<td valign="bottom" align="right">'.&round( $porc_error * 100, 2).'%</td>
							<td valign="bottom" align="left" colspan="2">&nbsp;</td>
						</tr>
						</tr><td colspan="4">&nbsp;</td></tr>
						<tr class="menu_bar_title">
							<td align="center">Ordenes Entregadas</td>
							<td align="center">Cantidad</td>
							<td align="center">Monto</td>
							<td align="center" valign="bottom">Comision<br><span style="font-size:80%;font-weight:normal"> ( '.$pbase_sale.'% + '.&round($bono_ticket,2).'% + '. &round($bono_tdc,2) .'% )</span></td>
						</tr>
						<tr>
							<td valign="bottom" align="left">Totales</td>
							<td valign="bottom" align="right">'.$rec->{'Sales_qty'}.'</td>
							<td valign="bottom" align="right">'.&format_price($rec->{'Sales_amount'}).'</td>
							<td valign="bottom" align="right" style="color:green;"><strong>MX'.&format_price($base_sale).'</strong></td>
						</tr>
						</tr><td colspan="4">&nbsp;</td></tr>
						<td colspan="2" align="center"><h2>Comision Total</h2></td>
						<td valign="bottom" align="right" style="color:green;"><h2>MX'.&format_price($total_orders_bonus+$base_sale+$bonus_data_amt+$total_bonus_data).'</h2></td>
						<td valign="bottom" align="right">&nbsp;</td>
						</table>
						&nbsp
						';

	
	return $rewards;
}


sub load_sales_ranking{
##-------------------------------------------------------------------------------
## Forms Involved:
## Created on: 12/29/2011 13:26:39
## Author: Roberto Barcenas
## Description : Busca el ranking de ventas del operador
## Parameters :
# Last Time Modified By OS Se tradujeron las etiquetas al español 01/02/2012

	my $ranking;
	my ($day_start,$day_end) = &calculate_dates;

	my($sth)=&Do_SQL("SELECT SUM(OrderNet) FROM sl_orders WHERE ID_admin_users = '$usr{'id_admin_users'}' AND Status NOT IN ('System Error','Void') AND Date BETWEEN '$day_start' AND '$day_end';");
	$x = $sth->fetchrow();

	if($x > 0){		
		$trank = 1;
		my($sth)=&Do_SQL("SET \@rownum :=0;");

		my($sth)=&Do_SQL("SELECT ID_admin_users, TOrders, QOrders, rank
						FROM(
							SELECT sl_orders.ID_admin_users, SUM(OrderNet) AS TOrders, COUNT(OrderNet) AS QOrders, \@rownum := \@rownum +1 AS rank
							FROM sl_orders 
								INNER JOIN admin_users ON admin_users.ID_admin_users = sl_orders.ID_admin_users
							WHERE admin_users.`Status`='Active' AND sl_orders.Date BETWEEN '$day_start' AND '$day_end' AND user_type = '$usr{'user_type'}' AND sl_orders.Status NOT IN ('System Error','Void')
							GROUP BY sl_orders.ID_admin_users 
							ORDER BY TOrders DESC 
						)AS SaleRace WHERE ID_admin_users = '$usr{'id_admin_users'}';");


		my($idu,$ordernet,$qordernet,$rank) = $sth->fetchrow();

		$ranking .= qq|<tr><td align="center" style="background-color:#B7AFA3;color:#F5FAFA;"><h3>Posision en Ranking</h3></td><td align="center">$rank de $trank</td>|;
		$ranking .= qq|<tr><td align="center" style="background-color:#B7AFA3;color:#F5FAFA;"><h3>Ordenes Tomadas</h3></td><td align="center">|.&format_price($ordernet).qq| / $qordernet</td>|;
	}else{
		$ranking .= qq|<tr><td colspan="2" align="center">|.&trans_txt('notmatch').qq|</td></tr>|;

	}
	return $ranking;
}


#########################################################################################
#########################################################################################
#   Function: load_advbar
#
#       Es: Función encargada de generar/controlar la barra de avance en la consola del modulo sales.
#
#       En: Function responsible for generating / controlling the progress bar in the module console sales.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#      - advbar.- defines whether or not to display the progress bar
#   
#
#   Returns:
#
#      - Returns the HTML for the progress bar
#
#   See Also:
#
#      ---
#
sub load_advbar {
	my ($advbar) = $cses{'advbar'};
	
	if($advbar == 1 or $in{'step'} == 10) {
		my ($step) = int($in{'step'});
		my ($advbar_step) = $step - 1;
		
		if($advbar_step < 0) {
			$advbar_step =0;
		}

		my (@link_list) = (&trans_txt('advbar_0'), &trans_txt('advbar_1'), &trans_txt('advbar_2'), &trans_txt('advbar_3'), &trans_txt('advbar_4'), &trans_txt('advbar_5'), &trans_txt('advbar_6'), &trans_txt('advbar_7'), &trans_txt('advbar_8'), &trans_txt('advbar_9'));
		my ($link_on_p1) = '			<td class="lineOn">';
											
		my ($link_on_p2) = '			</td>
										<td class="lineOn" align=right>
											<img src="[va_imgurl]app_bar/mod/mbbdiv2.png" width="15px" height="45px">
										</td>';
		my ($link_on_end) = '			</td>
										<td class="lineOn" align=right>
											<img src="[va_imgurl]app_bar/mod/mbbdiv.png" width="15px" height="45px">
										</td>';
		my ($link_off_p1) = '			<td class="" align=center><b>';
											
		my ($link_off_end) = '			</td>
										<td class="">
											<img src="[va_imgurl]app_bar/mod/mbbdiv.png" width="15px" height="45px">
										</td>';

		my ($html) = '

					<table border="0" cellspacing="0" cellpadding="0" style="background-image: url(/sitimages/menu/blue.jpg); background-repeat: no-repeat;  background-color:#ffffff;  -moz-border-radius: 10px;border-radius: 10px; width:100%">
						<tr>
							<td height="100%" width="100%" align=center>
								<table cellpadding="0" cellspacing="0" width="97%"  border=0 >
									<tr>';
		my ($stop_in) = @link_list - 1;
		my ($link_guide_advance) = '';
		my ($temp_step) = 0;
		for my $i(0..$stop_in) {
			$temp_step = $i + 1;
			if($temp_step == 1) {
				$temp_step = 0;
			}

				

			#if($i < $advbar_step or $cses{'status'.$i} eq 'ok') {
			if($i < $advbar_step) {
				
				#if($cses{'status'.$i} eq 'ok') {

					#$html .= $link_on_p1.'<a href="#" onClick="trjump(\'/cgi-bin/mod/sales/admin?cmd=console_order&step='.$i.'\')">'.@link_list[$i].'</a>'.$link_on_p2;
					#$html .= $link_on_p1.'<a href="#" onClick="trjump(\'/cgi-bin/mod/sales/admin?cmd=console_order&step='.$temp_step.'\')">'.@link_list[$i].'</a>'.$link_on_p2;

				#}else{

					#$html .= $link_on_p1.'<a href="#" onClick="trjump(\'/cgi-bin/mod/sales/admin?cmd=console_order&step='.$temp_step.'\')">'.@link_list[$i].'</a>'.$link_on_p2;
				
				#}
				$html .= $link_on_p1.'<a href="#" onClick="trjump(\'/cgi-bin/mod/sales/admin?cmd=console_order&step='.$temp_step.'\')">'.@link_list[$i].'</a>'.$link_on_p2;

			}elsif($i == $advbar_step ) {
				
				$html .= $link_on_p1.'<a href="#">'.@link_list[$i].'</a>'.$link_on_end;

			}
			else {
				
				$html .= $link_off_p1.''.@link_list[$i].''.$link_off_end;

			}
		}
		$html .= '					</tr> 
								</table>
							</td>
						</tr>

					</table>
';
		
		return $html;
		
	}else {
		return "";
	}
}

#########################################################################################
#########################################################################################
#   Function: load_areacodes
#
#       Es: Función que extrae los codigos de area del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts the setup area codes to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the area codes
#
#   See Also:
#
#      ---
#
sub load_areacodes {
	my($areacodes) = $cfg{'areacodes'};
	$areacodes =~ s/\|/\'\,\'/g;

	if(substr($areacodes, 1) != "'") {
	
		$areacodes = "'" . $areacodes;
	
	}
	if(substr($areacodes, -1) != "'") {
	
		$areacodes = $areacodes . "'";
	
	}
	
	return $areacodes;
}

#########################################################################################
#########################################################################################
#   Function: tel_lenght
#
#       Es: Función que extrae la longitud valida para un numero de telefono del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts the length valid for a phone number of the setup to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the lenght set for phone numbers or default 10
#
#   See Also:
#
#      ---
#
sub tel_lenght {

	if($cfg{'tel_lenght'}) {
		
		return $cfg{'tel_lenght'};

	}else {
		
		return 10;

	}

}

#########################################################################################
#########################################################################################
#   Function: tel_prefix_lenght
#
#       Es: Función que extrae la longitud valida de "lada" de un numero de telefono del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts validates the length of "Lada" a phone number of the setup to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the lenght set for prefix phone numbers or default 3
#
#   See Also:
#
#      ---
#
sub tel_prefix_lenght {

	if($cfg{'tel_prefix_lenght'}) {
		
		return $cfg{'tel_prefix_lenght'};

	}else {
		
		return 3;

	}
}

#########################################################################################
#########################################################################################
#   Function: load_earcall_interval
#
#       Es: Inserta un script que busca llamadas entrantes cada intervalo de tiempo definido.
#
#       En: Inserts a script that searches incoming calls each time interval defined.
#
#
#
#   Created on: 05/12/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on Oscar Maldonado 2013-09-26
#
#   Parameters:
#
#   Returns:
#
#      - Returns the javascript in a var o empty if user have not a extension.
#
#   See Also:
#
#      ---
#
sub load_earcall_interval {
	if($cfg{'earcalls_onoff'} eq 1){
		use Cwd;
		my ($mydir) = getcwd;
		#my ($path_earcalls) = '/cgi-bin/common/apps/earcalls';
		if($cfg{'earcalls_path'} eq ''){$cfg{'earcalls_path'}='/cgi-bin/common/apps/earcalls';}
		my ($path_earcalls) = $cfg{'earcalls_path'};
		my($jsonp);
		if(substr($path_earcalls,0,5) eq 'http:'){$jsonp='dataType : "jsonp",';}

		my ($earcalls_interval) = 10000;
		if($cfg{'earcalls_interval'} and $cfg{'earcalls_interval'}=int($cfg{'earcalls_interval'})) {
			$earcalls_interval = int($cfg{'earcalls_interval'}) * 1000;
		}

		my $origin, $add_param;
		
		if ($in{'origin'} or $in{'id_origins'} or $in{'ID_salesorigins'} or $cses{'id_salesorigins'}){

			$origin = ($in{'origin'})?$in{'origin'}:$in{'id_origins'};
			$origin = $in{'id_salesorigins'} if(!$origin);
			$origin = $cses{'id_salesorigins'} if(!$origin);

			$add_param = "&id_salesorigins=$origin";

		}

		$va{'ear_calls'} = qq|
		var intervalID = setInterval(function() {
			
			\$.ajax({
				type: "POST",
				url: "$path_earcalls",
				$jsonp
				data: "e=$in{'e'}&cmd=ear_calls&extension=$usr{'extension'}$add_param",
				success: function(msg){
					if(msg != '') {
						\$("#div_fancybox_earcalls").html(msg);
						\$("#fancybox_earcalls").trigger('click');
					}

				}
			});
		}, $earcalls_interval);|;

		if(!$usr{'extension'} || $usr{'extension'}=='') {
			$va{'ear_calls'} = '';
		}
	}
}


sub passdownsale{
#-----------------------------------------
# Created on: 09/08/09  13:39:29 By  Roberto Barcenas
# Forms Involved: 
# Description : Revisa si un authcode es valido para activar precios de downsale
# Parameters :
# Last Modified RB: 09/23/09  10:29:46 -- Se cambia la respuesta "Invalid" por "".
 
 	my ($authcode) = @_;
	
	my $response = -1;
	my ($sth) = &Do_SQL("SELECT IF(VValue !='',VValue,0) FROM sl_vars WHERE VName LIKE 'Downsale Price%' AND RIGHT(VValue,4)='".&filter_values($authcode)."'");
	my ($id_admin,$authorization) = split(/,/,$sth->fetchrow());
	
	if ($authorization > 0){

		$response = $id_admin;
		## Reinitialize the Value
		#$my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName LIKE 'Downsale Price%' AND RIGHT(VValue,4)='".&filter_values($authcode)."';");
	}

	return $response;

}


#############################################################################
#############################################################################
#   Function: get_shipping_data
#
#       Es: Recibe un zipcode y devuelve el shp_city y shp_state. Llamdo por step 4 y 5 de sales. Tambien genera el id_zones
#       En: 
#
#
#    Created on: 10/08/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#      - $in{'shp_zip'}
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_keypoints>
#      <accounting_order_deposit>
#
sub get_shipping_data{
#############################################################################
#############################################################################


	if ($in{'shp_zip'} or $in{'zipcode'}){

		########
		######## Cargado de Datos de Envio
		########

		$in{'shp_zip'}  =  '00'.$in{'shp_zip'}  if  length($in{'shp_zip'}) == 3;
		$in{'shp_zip'}  =  '0'.$in{'shp_zip'}  if  length($in{'shp_zip'}) == 4;

		my ($query);
		if ($cfg{'state_exclude'}){
			$query = "AND State!='$cfg{'state_exclude'}'";
		}elsif	($cfg{'state_only'}){
			$query = "AND State='$cfg{'state_only'}'";
		}

		my ($sth) = &Do_SQL("SELECT * FROM sl_zipcodes WHERE ZipCode='$in{'shp_zip'}' /*AND PrimaryRecord='P'*/ $query group by City;");
		$in{'city_to_show'} ='';

		while($tmp = $sth->fetchrow_hashref){

			if ($tmp->{'ZipCode'}>0){

				if(uc($cfg{'country'}) ne 'MX')  {

					if(!$cses{'country_tab'} || $in{'country_tab'} eq "us" || $in{'country_tab'} eq "pr" || !$in{'country_tab'}){ #JRG if condition added

						$in{'shp_city'} = $tmp->{'City'};
						$in{'city_to_show'} .= $tmp->{'City'}.' | ';
						$in{'shp_state'} = $tmp->{'State'}."-".$tmp->{'StateFullName'};

					}
				}

			}else{
				$error{'shp_zip'} = &trans_txt('required');
				++$err;
			}
		}

		$cses{'id_zones'} = get_zone_by_zipcode($in{'zip'});
		$cses{'id_zones_express_delivery'} = &load_name('sl_zones', 'ID_zones', $cses{'id_zones'}, 'ExpressShipping');

	}

}




1;