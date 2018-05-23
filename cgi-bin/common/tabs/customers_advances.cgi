#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if($in{'tab'} eq 6){
		## Logs Tab
		$va{'tab_type'}  = 'movs';
		$va{'tab_title'} = &trans_txt('movs');
		$va{'tab_table'} = 'sl_customers_advances';
		$va{'tab_idvalue'} = $in{'id_customers_advances'};
	}elsif ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_customers_advances_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_customers_advances';
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs2
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: HC
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs2 {
#############################################################################
#############################################################################
	
	$boledit = 0;
	my ($sth) = &Do_SQL("	SELECT status 
							FROM sl_customers_advances
							WHERE id_customers_advances = ". $in{'id_customers_advances'} .";");  
	my ($customers_advances_status) = $sth->fetchrow();
	
	if($customers_advances_status ne 'Applied'){
		$boledit = 1;
	}


	if($boledit){
		$va{'updatebtn'} = "<input value=' ". &trans_txt('opr_customers_advances_updbtn'). "' class='button' type='submit'>";
		$va{'addorder'} = "<a href='javascript:add_order()'>Add Order</a>";
	}

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers_advances_payments WHERE ID_customers_advances = ". $in{'id_customers_advances'} .";");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my ($sthp1) = &Do_SQL("SELECT SUM(Amount) FROM sl_customers_advances_payments WHERE ID_customers_advances = ". $in{'id_customers_advances'} .";");
		my ($amt_thiscustomers_advances)= $sthp1->fetchrow();
		(!$amt_thiscustomers_advances) and ($amt_thiscustomers_advances = 0);

		my $max_allowed =  $in{'amount'} - $amt_thiscustomers_advances;

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("	SELECT 	sl_orders.ID_orders, sl_orders.Date, sl_orders.OrderNet, sl_orders.Status, 
										sl_customers_advances_payments.Amount, sl_customers_advances_payments.ID_customers_advances_payments,  sl_customers_advances_payments.status cap_status
								FROM 	sl_customers_advances_payments 
										LEFT JOIN sl_orders ON sl_customers_advances_payments.ID_orders=sl_orders.ID_orders 
								WHERE ID_customers_advances = ". $in{'id_customers_advances'} .";");
		$va{'total'} = 0;
		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;
			$va{'total'} += $rec->{'Amount'};

				
			my $amount = &get_paid_unpaid($rec->{'ID_orders'});
			

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>";
			if($rec->{'cap_status'} ne 'Applied'){
				$va{'searchresults'} .= "	<a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers_advances&view=".$in{'id_customers_advances'}."&deladvances=".$rec->{'ID_customers_advances_payments'}."&tab=2'>
												<img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'>
											</a>";
			}

			$va{'searchresults'} .=	"	</td>\n";
			$va{'searchresults'} .= "  	<td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "  	<td class='smalltext'>".&invoices_list($rec->{'ID_orders'})."</td>\n";
			$va{'searchresults'} .= "  	<td class='smalltext' align='right'>".$rec->{'Date'}."</td>\n";
			$va{'searchresults'} .= "  	<td class='smalltext' align='right'>".&format_price($amount->{'total'})."</td>\n";			
			$va{'searchresults'} .= "  	<td class='smalltext' align='right'>".&format_price($amount->{'calculated_unpaid'})."</td>\n";
			$va{'searchresults'} .= "  	<td class='smalltext' align='right'>".$rec->{'Status'}."</td>\n";
			
			if( $rec->{'cap_status'} eq 'Applied'){
				$va{'searchresults'} .= "<td class='smalltext' align='center'>Applied</a></td>";
			}else{
				if($rec->{'Amount'} > 0){
					$va{'searchresults'} .= "<td class='smalltext' align='center'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers_advances&view=".$in{'id_customers_advances'}."&apply=".$rec->{'ID_customers_advances_payments'}."&tab=2'><img src='/sitimages/default/b_addpayment.gif' title='Apply Payment' alt='Apply Payment' height='24' width='24' border='0'></a></td>";
				}else{
					$va{'searchresults'} .= "<td class='smalltext' align='center'></td>";
				}
			}

			if ($boledit and $rec->{'cap_status'} ne 'Applied'){
				$va{'searchresults'} .= qq|  <td class='smalltext' align='right'><input name="orderamount_|. $rec->{'ID_customers_advances_payments'} .qq|" style="text-align:right" value="|. $rec->{'Amount'} .qq|" size="20" onfocus="focusOn( this )" onblur="focusOff( this )" type="text"><span class='smallfieldterr'>|. $error{'order'.$rec->{'ID_customers_advances_payments'}} .qq|</span></td>\n|;
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			}

			$va{'searchresults'} .= "</tr>\n";
		}


		if ($va{'total'} > 0) {

			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='8' align='right'>".&trans_txt('total')."  </td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='border-top:thick double #808080;'>".&format_price($va{'total'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
			
		}

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}




1;