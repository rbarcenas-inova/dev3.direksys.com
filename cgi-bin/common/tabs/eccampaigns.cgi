#!/usr/bin/perl
####################################################################
########                  eccampaign                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if($in{'tab'} eq 2){
		## logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_campaigns_notes';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab2 :  Reports
##############################################
	
	my $scheduledate=&load_name('nsc_campaigns','ID_campaigns',int($in{'id_campaigns'}),'Date_From');
	my $scheduletime=&load_name('nsc_campaigns','ID_campaigns',int($in{'id_campaigns'}),'Time_From');
	my $expirationdate=&load_name('nsc_campaigns','ID_campaigns',int($in{'id_campaigns'}),'Date_To');
	my $expirationtime=&load_name('nsc_campaigns','ID_campaigns',int($in{'id_campaigns'}),'Time_To');
	my $id_admin_users=&load_name('nsc_campaigns','ID_campaigns',int($in{'id_campaigns'}),'campaign_user');
	my ($sth) = &Do_SQL("Select concat('$scheduledate',' ',sec_to_time($scheduletime*3600)),concat('$expirationdate',' ',sec_to_time($expirationtime*3600))");
	my ($date_from,$date_to)=$sth->fetchrow_array();
	
	my($sales_totalf, $ordersf, $orders_ratiof,$sales_ratiof,$orders_openedf,$orders_emailsf,$ticketf);
	(!$id_admin_users or $id_admin_users eq '') and ($id_admin_users = 4122);
	my $uname	= `uname -n`;
	
	my ($sth) = &Do_SQL("Select
												database_campaign,
												landingpage,
												IF(emails_sent IS NULL OR emails_sent=0,1,emails_sent)as emails_sent,
												IF(emails_opened IS NULL OR emails_opened=0,1,emails_opened)as emails_opened,
												IF(clicked IS NULL OR clicked=0,1,clicked)as clicked,
												t_clicked.period
											from nsc_campaigns
											left join (Select nsc_opentracks.ID_campaigns,nsc_opentracks.period,opened as emails_opened,clicked
																	from (Select ID_campaigns,period,count(*) as opened
																				from (Select 
																							ID_campaigns,
																							if(concat(Date,' ',Time) between '$date_from' and '$date_to','In',
																							if(concat(Date,' ',Time) < '$date_from','Before',
																							if(concat(Date,' ',Time) > '$date_to','After','Undefined')))as period
																						from nsc_opentracks
																						where ID_campaigns=$in{'id_campaigns'}
																						group by email) as nsc_opentracks
																				group by ID_campaigns,period) as nsc_opentracks
																	left join (Select ID_campaigns,period,count(*) as clicked
																							from (Select 
																										ID_campaigns,
																										if(concat(Date,' ',Time) between '$date_from' and '$date_to','In',
																										if(concat(Date,' ',Time) < '$date_from','Before',
																										if(concat(Date,' ',Time) > '$date_to','After','Undefined')))as period
																									from nsc_redirecttrack
																									where ID_campaigns=$in{'id_campaigns'}
																									group by email) as nsc_redirecttrack
																							group by ID_campaigns,period) as nsc_redirecttrack on nsc_opentracks.ID_campaigns=nsc_redirecttrack.ID_campaigns and nsc_opentracks.period=nsc_redirecttrack.period)as t_clicked on nsc_campaigns.ID_campaigns= t_clicked.ID_campaigns
											where nsc_campaigns.ID_campaigns=$in{'id_campaigns'} ORDER BY t_clicked.period='After',t_clicked.period='In',t_clicked.period='Before'");
	my (@c) = split(/,/,$cfg{'srcolors'});
	$tot_opened=0;
	$tot_clicked=0;
	while($rec=$sth->fetchrow_hashref)
	{
		$d = 1 - $d;
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'period'}</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$rec->{'emails_sent'}</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$rec->{'emails_opened'}</td>\n";
		$tot_opened+=$rec->{'emails_opened'};
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>".round(100*$rec->{'emails_opened'}/$rec->{'emails_sent'},2)."%</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$rec->{'clicked'}</td>\n";
		$tot_clicked+=$rec->{'clicked'};
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>".round(100*$rec->{'clicked'}/$rec->{'emails_opened'},2)."%</td>\n";
		
		if($rec->{'period'}ne'In')
		{
			$sales_total='--';
			$orders='--';
			$orders_ratio='--';
			$sales_ratio='--';
			$orders_opened='--';
			$orders_emails='--';
			$ticket='--';
		}
		else
		{
			($uname =~ /sltv|n3|n4/) and ($rec->{'database_campaign'} = 'direksys_'.$rec->{'database_campaign'});
			($rec->{'landingpage'} eq 'www.innovashop.tv') and ($id_admin_users = 4688);
			my $dbase = $rec->{'database_campaign'};
			#calcula las ventas
			$sales_q=&Do_SQL("Select sum(amount)
												from
												(Select sl_orders.ID_orders,count(ID_orders_payments),sum(amount)as amount
												from ".$dbase.".sl_orders_payments
												inner join ".$dbase.".sl_orders on (sl_orders_payments.ID_orders=sl_orders.ID_orders)
												where concat(sl_orders.Date,' ',sl_orders.Time) between '$date_from' and '$date_to'
												and sl_orders.id_admin_users=$id_admin_users
												and sl_orders.Date<='$date_to'
												and sl_orders.Status not in('system error')
												and amount>0
												group by sl_orders.ID_orders)as orders");
			$sales_total=$sales_q->fetchrow;
			
			#calcula las órdenes
			$orders_q=&Do_SQL("Select count(*)
													from sl_orders
													where concat(sl_orders.Date,' ',sl_orders.Time) between '$date_from' and '$date_to'
													and id_admin_users=4688
													and Status not in('system error')
													and Date<='$date_to'");
			$orders=$orders_q->fetchrow;
			$orders_ratio= $rec->{'emails_opened'} == 0 ? 0 : round(100*$orders/$rec->{'emails_opened'},2);
			$sales_ratio= $rec->{'clicked'} == 0 ? 0 : round(100*$orders/$rec->{'clicked'},2);
			$orders_opened= $rec->{'emails_opened'} == 0 ? 0 : round(100*$orders/$rec->{'emails_opened'},2);
			$orders_emails= $orders == 0 ? 0 : round(100*$orders/$rec->{'emails_sent'},2);
			$ticket = $orders == 0 ? 0 : format_price(round($sales_total/$orders,2));
			
			$sales_totalf=$sales_total;
			$ordersf=$orders;
			$orders_ratiof=$orders_ratio;
			$sales_ratiof=$sales_ratio;
			#$orders_openedf=$orders_opened;
			$orders_emailsf=$orders_emails;
			$ticketf=$ticket;
		}
		
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>". format_price($sales_total) ."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$orders</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$orders_ratio%</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$sales_ratio%</td>\n";
		#$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$orders_opened</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$orders_emails</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$ticket</td>\n";
		
		$va{'searchresults'} .= "</tr>\n";
		$sent=$rec->{'emails_sent'};
		$opened=$rec->{'emails_opened'};
	}
	$va{'searchresults'} .= "<tr bgcolor='#D4D4D4'>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' style='font-weight:bold;font-size:13px;'>Total</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$sent</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$tot_opened</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>".round(100*$tot_opened/$sent,2)."%</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$tot_clicked</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>".round(100*$tot_clicked/$tot_opened,2)."%</td>\n";
	$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>". format_price($sales_totalf) ."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$ordersf</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$orders_ratiof%</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$sales_ratiof%</td>\n";
		#$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right>$orders_openedf</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$orders_emailsf</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' valign='top' align=right style='font-weight:bold;font-size:13px;'>$ticketf</td>\n";
	$va{'searchresults'} .= "</tr>\n";
}

1;