
#############################################################################
#########################														#########################				
#########################					DASHBOARDS				#########################
#########################														#########################
#############################################################################


sub dashboard{
#-----------------------------------------
# Created on: 03/26/09  10:03:23 By  RB & GV
# Forms Involved: 
# Description : main de los diferentes dashboards de ventas
# Parameters : 	
# Last Modified on: 04/07/09 11:45:37
# Last Modified by: MCC C. Gabriel Varela S: Se copia desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\admin.html.cgi
	$in{'type'}	=	'cod'	if !$in{'type'};
	
	my ($cmd)	=	'dashboard_'.$in{'type'};
	&$cmd;
}

sub dashboard_cod{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/26/09 10:11:04
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/27/09 10:48:55
# Last Modified by: MCC C. Gabriel Varela S: Se da formato a tabla y se establecen links
# Last Modified on: 03/27/09 17:12:41
# Last Modified by: MCC C. Gabriel Varela S: Se pasa desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\sub.func.html.cgi
# Last Modified on: 04/07/09 11:46:21
# Last Modified by: MCC C. Gabriel Varela S: Se copia desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\admin.html.cgi y se adapta para poder mandarse a llamar desde cualquier módulo.
# Last Modified RB: 07/01/09  18:23:06 -- Se crea acordion y se discrimna por warehouse virtual(chofer).
# Last Modified by RB on 06/17/2011 02:13:50 PM : Se cambia el proceso, ya no se calculan las cantidades al vuelo con &build_cod_data($id_warehouse), los calculos son diarios via run_daily 

	
	my $sth=&Do_SQL("SELECT * FROM sl_cod_sales ORDER BY ID_cod_sales,ID_warehouses;");
	my $prefix="";
	$prefix="opr_"if($script_module eq'administration');
	my (@c) = split(/,/,$cfg{'srcolors'});
	while(my($id,$id_warehouse,$status,$more,$seven,$two,$one,$never) =  $sth->fetchrow()){
    $cod_table{$id_warehouse} .= "<tr bgcolor='$c[$d]'>";
		$cod_table{$id_warehouse} .= "<td><B>$status</B></td>";
		$cod_table{$id_warehouse} .= "<td align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&type=cod&todo=bystatuscontact&status=$status&contact=One_day&results=$one&id_warehouses=$id_warehouse')\">$one</td>";
		$cod_table{$id_warehouse} .= "<td align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&type=cod&todo=bystatuscontact&status=$status&contact=Two_days&results=$two&id_warehouses=$id_warehouse')\">$two</td>";
		$cod_table{$id_warehouse} .= "<td align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&type=cod&todo=bystatuscontact&status=$status&contact=Seven_days&results=$seven&id_warehouses=$id_warehouse')\">$seven</td>";
		$cod_table{$id_warehouse} .= "<td align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&type=cod&todo=bystatuscontact&status=$status&contact=More_than_7_days&results=$more&id_warehouses=$id_warehouse')\">$more</td>";
		$cod_table{$id_warehouse} .= "<td align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&type=cod&todo=bystatuscontact&status=$status&contact=Never&results=$never&id_warehouses=$id_warehouse')\">$never</td>";
		$cod_table{$id_warehouse} .= "</tr>";
		$d = 1 - $d;
  }
  
  
  my $sth2=&Do_SQL("SELECT DISTINCT sl_cod_sales.ID_warehouses,IF(Name IS NULL,'All Drivers', Name)AS Name FROM sl_cod_sales LEFT JOIN sl_warehouses ON sl_cod_sales.ID_warehouses = sl_warehouses.ID_warehouses ORDER BY ID_cod_sales,sl_cod_sales.ID_warehouses;");
  while(my($idw,$name_warehouse) = $sth2->fetchrow()){
  
      $va{'searchresults'} .= qq|
					<li><h3>$name_warehouse</h3>
					<div>
						<table width=100% border=0 cellpadding=0 cellspacing=0>
							<tr valign=top>
								<td width=76px height=1px><p><br></p></td>
								<td width=76px><p><br></p></td>
								<td><p align=center><B>Tiempo de contacto</B></p></td>
							</tr>
							<tr valign=top>
								<td height=28px><p><br></p></td>
								<td rowspan=2 colspan=2>
									<table width=100% border=0 cellpadding=4 cellspacing=0>
									  <tr>
									    <td></td>
									    <td><B>24 hrs</B></td>
									    <td><B>48 hrs</B></td>
									    <td><B>1 semana</B></td>
									    <td><B>M&aacute;s de 7 d&iacute;as</B></td>
									    <td><B>Sin contactar</B></td>
									  </tr>
									  |. $cod_table{$idw} .qq|
									</table>
								</td>
							</tr>
							<tr valign=top>
								<td valign=Middle><p align=center><B>Status</B></p></td>
							</tr>
						</table>
						&nbsp;
					</div>
				</li>|;

  }
				
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('dashboard_cod.html');
#	}
}



sub dashboard_orders_status_substatus{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/27/09 13:00:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 03/27/09 17:13:02
# Last Modified by: MCC C. Gabriel Varela S: Se pasa desde
# Last Modified on: 03/30/09 12:07:42
# Last Modified by: MCC C. Gabriel Varela S: Se integra accordion
# Last Modified on: 04/07/09 11:46:33
# Last Modified by: MCC C. Gabriel Varela S: Se copia desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\admin.html.cgi y se adapta para poder mandarse a llamar desde cualquier módulo.

	#Asigna encabezados dinámicos para columnas.
	my %titlesbystatus;
	my @status;
	my $sth=&Do_SQL("Select Status,
concat(
if(OutofStock>0,'Out of Stock,',''),
if(InFulfillment>0,'In Fulfillment,',''),
if(InDropshipment>0,'In Dropshipment,',''),
if(DropshipSent>0,'Dropship Sent,',''),
if(PartialShipment>0,'Partial Shipment,',''),
if(PartialDropship>0,'Partial Dropship,',''),
if(ForReturn>0,'For Return,',''),
if(ForExchange>0,'For Exchange,',''),
if(ForReShip>0,'For Re-Ship,',''),
if(Undeliverable>0,'Undeliverable,',''),
if(InClaim>0,'In Claim,',''),
if(None>0,'None','')
)as Titles
from(
SELECT Status,StatusPay,
sum(if(StatusPrd='Out of Stock',1,0))as'OutofStock',
sum(if(StatusPrd='In Fulfillment',1,0))as'InFulfillment',
sum(if(StatusPrd='In Dropshipment',1,0))as'InDropshipment',
sum(if(StatusPrd='Dropship Sent',1,0))as'DropshipSent',
sum(if(StatusPrd='Partial Shipment',1,0))as'PartialShipment',
sum(if(StatusPrd='Partial Dropship',1,0))as'PartialDropship',
sum(if(StatusPrd='For Return',1,0))as'ForReturn',
sum(if(StatusPrd='For Exchange',1,0))as'ForExchange',
sum(if(StatusPrd='For Re-Ship',1,0))as'ForReShip',
sum(if(StatusPrd='Undeliverable',1,0))as'Undeliverable',
sum(if(StatusPrd='In Claim',1,0))as'InClaim',
sum(if(StatusPrd='None',1,0))as'None'
FROM sl_orders
/*WHERE Status='New'*/
GROUP BY Status
)as tmp
GROUP BY Status");
	while($rec=$sth->fetchrow_hashref)
	{
		$titlesbystatus{$rec->{'Status'}}=$rec->{'Titles'};
	}
	

	my $sth=&Do_SQL("SELECT Status,StatusPay,
sum(if(StatusPrd='Out of Stock',1,0))as'Out of Stock',
sum(if(StatusPrd='In Fulfillment',1,0))as'In Fulfillment',
sum(if(StatusPrd='In Dropshipment',1,0))as'In Dropshipment',
sum(if(StatusPrd='Dropship Sent',1,0))as'Dropship Sent',
sum(if(StatusPrd='Partial Shipment',1,0))as'Partial Shipment',
sum(if(StatusPrd='Partial Dropship',1,0))as'Partial Dropship',
sum(if(StatusPrd='For Return',1,0))as'For Return',
sum(if(StatusPrd='For Exchange',1,0))as'For Exchange',
sum(if(StatusPrd='For Re-Ship',1,0))as'For Re-Ship',
sum(if(StatusPrd='Undeliverable',1,0))as'Undeliverable',
sum(if(StatusPrd='In Claim',1,0))as'In Claim',
sum(if(StatusPrd='None',1,0))as'None'
FROM sl_orders
/*WHERE Status='Processed'*/
GROUP BY Status,StatusPay
ORDER BY Status,StatusPay desc");
	my $rec=$sth->fetchrow_hashref;
	my $statusprv,$statuscurr;
	$statusprv=$rec->{'Status'};
#	$va{'tableresults'}="<TABLE WIDTH=100% BORDER=0 CELLPADDING=4 CELLSPACING=0>
#													<TR VALIGN=TOP>
#														<TD><P><BR></TD>
#														<TD COLSPAN=12><P ALIGN=CENTER><B>$statusprv</B></P></TD>
#													</TR>
#													<TR VALIGN=TOP>
#														<TD><P><BR></TD>";
	$va{'tableresults'}="<div class='accordion-products'>
	<ul id='statusaccordion'>
		<li><h3>$statusprv</h3>
			<div class='element'>
				<TABLE  BORDER=0 CELLPADDING=4 CELLSPACING=0>
					<TR VALIGN=TOP>
						<TD><P><BR></TD>
						<!--TD COLSPAN=12><P ALIGN=CENTER><B>$statusprv</B></P></TD-->
					</TR>
					<TR VALIGN=TOP>
						<TD><P><BR></TD>";
	@status=split(/,/,$titlesbystatus{$statusprv});
	for(0..$#status)
	{
		$va{'tableresults'}.="<TD><P ALIGN=CENTER style='font-size:9'><B>$status[$_]</B></P></TD>";
	}
	$va{'tableresults'}.="</TR>";
	my (@c) = split(/,/,$cfg{'srcolors'});
	do
	{
		$statuscurr=$rec->{'Status'};
		if($statuscurr ne $statusprv)#Terminará tabla anterior e insertará nuevo encabezado
		{
			$statusprv=$statuscurr;
#			$va{'tableresults'}.="</TABLE>
#														&nbsp;
#														<BR>
#														&nbsp;
#														<BR>
#														<TABLE WIDTH=100% BORDER=0 CELLPADDING=4 CELLSPACING=0>
#															<TR VALIGN=TOP><TD><P><BR></P></TD>
#																<TD COLSPAN=12><P ALIGN=CENTER><B>$statusprv</B></P></TD>
#															</TR>
#															<TR VALIGN=TOP>
#																<TD><P><BR></TD>";
			$va{'tableresults'}.="</TABLE>
														<br>
														</div>
													</li>
													<li><h3>$statusprv</h3>
														<div class='element'>
															<TABLE  BORDER=0 CELLPADDING=4 CELLSPACING=0>
																<TR VALIGN=TOP>
																	<TD><P><BR></TD>
																	<!--TD COLSPAN=12><P ALIGN=CENTER><B>$statusprv</B></P></TD-->
																</TR>
																<TR VALIGN=TOP>
																	<TD><P><BR></TD>";
			@status=split(/,/,$titlesbystatus{$statusprv});
			for(0..$#status)
			{
				$va{'tableresults'}.="<TD><P ALIGN=CENTER style='font-size:9'><B>$status[$_]</B></P></TD>";
			}
		
			$va{'tableresults'}.="</TR>";
			
		}
		$va{'tableresults'}.="		<TR VALIGN=TOP bgcolor='$c[$d]'>";
		$va{'tableresults'}.="														<TD><P style='font-size:9'><B>$rec->{'StatusPay'}</B></P></TD>";
		for(0..$#status)
		{
			$prefix="";
			$prefix="opr_"if($script_module eq'administration');
			$va{'tableresults'}.="<TD align=center onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/$script_module/dbman?cmd=".$prefix."opr_orders&search=advSearch&status=$statusprv&statusprd=$status[$_]&statuspay=$rec->{'StatusPay'}')\"><P ALIGN=CENTER style='font-size:9'>$rec->{$status[$_]}</P></TD>";
		}
															$va{'tableresults'}.="</TR>";
		$d = 1 - $d;
	}
	while($rec=$sth->fetchrow_hashref);
	$va{'tableresults'}.="</TABLE>
	</div>";

	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('dashboard_orders_status_substatus.html');
}

sub dashboard_layaway{
#-----------------------------------------
# Created on: 03/26/09  10:10:47 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified on: 04/07/09 11:45:57
# Last Modified by: MCC C. Gabriel Varela S: Se copia desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\admin.html.cgi y se adapta para poder mandarse a llamar desde cualquier módulo.

	
	####### NOT CONTACTED
	$in{'mod'}	=1;
	$in{'type'}	=	'tc';
	($va{'tc_contacted'})	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	($va{'mo_contacted'})	= &build_query_table_layaway(1);
	
	######## PAYMENTS 0K
	$in{'mod'}++;
	$in{'type'}	=	'tc';
	$va{'tc_ok'}	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	$va{'mo_ok'}	= &build_query_table_layaway(1);
	
	
	######## PAYMENTS DUE
	$in{'mod'}++;
	$in{'type'}	=	'tc';
	$va{'tc_due'}	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	$va{'mo_due'}	= &build_query_table_layaway(1);
	
	
	######## PAYMENTS NEXT TO BE DUE(1 WEEK)
	$in{'mod'}++;
	$in{'type'}	=	'tc';
	$va{'tc_2days'}	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	$va{'mo_2days'}	= &build_query_table_layaway(1);
	
	$in{'mod'}++;
	$in{'type'}	=	'tc';
	$va{'tc_7days'}	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	$va{'mo_7days'}	= &build_query_table_layaway(1);
	
	$in{'mod'}++;
	$in{'type'}	=	'tc';
	$va{'tc_p7days'}	= &build_query_table_layaway(1);
	$in{'type'}	=	'mo';
	$va{'mo_p7days'}	= &build_query_table_layaway(1);
	

	print "Content-type: text/html\n\n";
	print &build_page('dashboard_layaway.html');
}

sub dashboard_mo{
#-----------------------------------------
# Created on: 03/26/09  10:10:47 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : build_query_table_moneyorder(count=1 group_concat=2 ,paid=1 unpaid=2, 2=48 hrs  7=7 days  8 = >7 days or 0)
# Last Modified on: 04/07/09 11:46:11
# Last Modified by: MCC C. Gabriel Varela S: Se copia desde Y:\domains\dev.direksys.com\cgi-bin\follow-up\admin.html.cgi y se adapta para poder mandarse a llamar desde cualquier módulo.

	
	####### 
	$va{'paid_2days'}	= &build_query_table_moneyorder(1,1,'2');
	$va{'paid_7days'}	= &build_query_table_moneyorder(1,1,'7');
	$va{'paid_contacted'}	= &build_query_table_moneyorder(1,1,'0');
	$va{'unpaid_2days'}	= &build_query_table_moneyorder(1,2,'2');
	$va{'unpaid_7days'}	= &build_query_table_moneyorder(1,2,'7');
	$va{'unpaid_p7days'}	= &build_query_table_moneyorder(1,2,'8');
	$va{'unpaid_contacted'}	= &build_query_table_moneyorder(1,2,'0');


	print "Content-type: text/html\n\n";
	print &build_page('dashboard_mo.html');
}

1;