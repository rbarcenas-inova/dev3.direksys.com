#!/usr/bin/perl

$cfg{'fc_minutes'} = 960;
my $man_rf_dids = '3438800,3438900,3439100,4830900,4832400,4836000,4836900,4837400,4837900,4838000,4838200,4838600,4839600,5570300,5570500,5572000,5572700,2230400,2231700,2232700,5573100,5575100';
local (%rf) = (
		'dnis'  => '9999',
		'dids7' => '9999999',
		'name'  => 'Revenue Frontier',
		'dids'  => $man_rf_dids
		);  ### RF

$id_user_ecommerce = "2";
$id_user_out       = "3";


#########################################################
#########################################################	
#	Function: assign_orders
#   		Reasigna llamadas con su respectiva orden y contrato
# 			Basada en funcion de cron_scripts. Pero esta version recibe un rango de ordenes para reasginar
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#			- assign_leads_no_order
#
sub assign_orders {
########################################################
########################################################
	
	my ($from_date, $to_date) = @_;

	my $r1 = 60 * 24;      # 1 Dia
	my $r2 = 60 * 24 * 7;  # 7 dias
	my $r3 = 60 * 24 * 30; # 30 dias

	my $forders=0;
	my $fleads=0;

		
	$q= "SELECT 
			ID_orders, 
			CID, CONCAT(sl_orders.Date,' ',sl_orders.Time) as OrderDate , 
			sl_customers.ID_customers, 
			sl_orders.ID_admin_users
		FROM sl_orders 
		INNER JOIN sl_customers 
		ON sl_orders.ID_customers = sl_customers.ID_customers 
		WHERE 
			sl_orders.Date BETWEEN DATE('$from_date') AND DATE('$to_date')
			AND ID_mediacontracts = 0
			AND sl_orders.status <> 'System Error';";
	
	
	my $sth = &Do_SQL($q);

	ORDER:while($rec=$sth->fetchrow_hashref){
		++$ccount;

		## Ensure sl_leads_calls sync
		&Do_SQL("UPDATE sl_leads_calls
					SET 
					ID_orders = 0,
					ID_order_assign = 0,
					ID_mediacontracts = 0,
					ID_mediacontract_assign = 0
					WHERE
					ID_orders = '$rec->{'ID_orders'}' OR 
					ID_order_assign = '$rec->{'ID_orders'}';");

		my $next_order;
		my $rf=0;

		($rec->{'CID'},$rec->{'Phone1'},$rec->{'Phone2'},$rec->{'Cellphone'}) = &clean_phones($rec->{'ID_customers'});
		$query =''; $query2='';

		
		if ($rec->{'Phone1'} ne ''){
			$query = "	(ID_leads='".substr($rec->{'Phone1'},-10)."' or ID_leads='1".substr($rec->{'Phone1'},-10)."' or ID_leads='".$rec->{'Phone1'}."') OR ";
			$query2 = " Phone1='".substr($rec->{'Phone1'},-10)."' OR Phone2='".substr($rec->{'Phone1'},-10)."' OR Cellphone='".substr($rec->{'Phone1'},-10)."' OR ";
		}
		
		if ($rec->{'Phone2'}ne '' and $query !~ /$rec->{'Phone2'}/){
			$query .= "	(ID_leads='".substr($rec->{'Phone2'},-10)."' or ID_leads='1".substr($rec->{'Phone2'},-10)."' or ID_leads='".$rec->{'Phone2'}."') OR ";
			$query2 .= " Phone1='".substr($rec->{'Phone2'},-10)."' OR Phone2='".substr($rec->{'Phone2'},-10)."' OR Cellphone='".substr($rec->{'Phone2'},-10)."' OR ";
		}
		
		if ($rec->{'Cellphone'} ne '' and $query !~ /$rec->{'Cellphone'}/){
			$query .= "	(ID_leads='".substr($rec->{'Cellphone'},-10)."' or ID_leads='1".substr($rec->{'Cellphone'},-10)."' or ID_leads='".$rec->{'Cellphone'}."') OR ";
			$query2 .= " Phone1='".substr($rec->{'Cellphone'},-10)."' OR Phone2='".substr($rec->{'Cellphone'},-10)."' OR Cellphone='".substr($rec->{'Cellphone'},-10)."' OR ";
		}

		$rec->{'CID'} =~ s/-|\(|\)|\+|\.|\s//g;
		if ($rec->{'CID'}ne '' and $query !~ /$rec->{'CID'}/){
			$query .= "	(ID_leads='".substr($rec->{'CID'},-10)."' or ID_leads='1".substr($rec->{'CID'},-10)."' or ID_leads='".$rec->{'CID'}."') OR ";
		}

		$query = "(" . substr($query,0,-4) .")" if ($query ne '');
		$query2 = "(" . substr($query2,0,-4) .")" if ($query2 ne '');
		
		if($query eq ''){
			$query='0';
		}


		### Next Order
		if ($query2){
			my $q3 = "SELECT CONCAT(sl_orders.Date,' ', sl_orders.Time) AS orderdatetime FROM sl_orders
						LEFT JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers
						WHERE
						ID_orders<>$rec->{'ID_orders'} AND CONCAT(sl_orders.Date,' ',sl_orders.Time) > '$rec->{'OrderDate'}' AND
						$query2 ORDER BY ID_orders LIMIT 1";
			
			my $sth2 = &Do_SQL($q3);
			$next_order = $sth2->fetchrow;
		}else{
			$next_order = 0;
		}


		###############################################################################
		###############################################################################
		############
		############
		############	SECCION 1) ASIGNACION ID_orders
		############
		############
		################################################################################
		################################################################################


		my $querylead = "SELECT 
								ID_leads_calls,
								DIDUS,
								CONCAT(Date, ' ', Time),
								Duration,
								TIMESTAMPDIFF(MINUTE,CONCAT(Date, ' ', Time), '$rec->{'OrderDate'}')AS Diff,
								IF(TIMESTAMPDIFF(MINUTE,CONCAT(Date, ' ', Time), '$rec->{'OrderDate'}') BETWEEN 0 AND $cfg{'fc_minutes'} OR TIMESTAMPDIFF(minute,CONCAT(Date, ' ', Time), '$rec->{'OrderDate'}') BETWEEN 0 AND ((Duration)/60)+5,'Yes','No') as first_call				
							FROM 
								sl_leads_calls 
							WHERE 
								CONCAT(Date, ' ', Time) <= '$rec->{'OrderDate'}' AND  
								IO='In' AND 
								ID_orders=0 AND 
								ID_order_assign=0 AND 
								$query 
							ORDER BY 
								Diff 
							LIMIT 1";				
		
		my ($sth) = &Do_SQL($querylead);
		my($id,$didusa,$calldate,$duration,$diff,$first_call) = $sth->fetchrow();



		###############################################################################
		###############################################################################
		############
		############
		############	SECCION 1) ASIGNACION REVENUE FRONTIER (ID_orders | ID_mediacontract)
		############
		############
		################################################################################
		################################################################################

		
		if ($rf{'dids'} =~/$didusa/ and $didusa>0 and $id>0){
			++$forders;

			### Podria ser que la llamada sea de un dia diferente de la orden.
			### POr eso uso $calldate para determinar el dia de la Venta y contrato
			my ($sth2) = &Do_SQL("SELECT DATE('$calldate')");#RF
			$sale_date = $sth2->fetchrow;#RF
			
			### Orden de RF
			my $new_contract = &add_contract($sale_date,$rf{'dnis'},$rf{'name'});#RF

			my $q1 = "UPDATE sl_orders SET ID_mediacontracts=$new_contract, DNIS='$rf{'dnis'}', DIDS7='$rf{'dids7'}',first_call='$first_call' WHERE ID_orders=$rec->{'ID_orders'};";
			my $q2 = "UPDATE sl_leads_calls SET ID_orders=$rec->{'ID_orders'}, ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";

			my ($sth2) = &Do_SQL($q1);#RF
			my ($sth2) = &Do_SQL($q2);#RF
			$rf=1; # Bandera RF | Orden y llamada asignadas con contrato. "Saltar Seccion Asignacion de Contrato"

			## Llamadas anteriores.
			my $q3 = "UPDATE sl_leads_calls SET 
						ID_order_assign = '$rec->{'ID_orders'}', 
						ID_mediacontracts = 0, 
						ID_mediacontract_assign = 0
					WHERE $query
					AND DATE('$calldate') = Date
					AND DIDUS = $didusa
					AND ID_orders = 0 AND ID_order_assign = 0
					AND (ID_mediacontracts > 0 OR ID_mediacontract_assign > 0);";

			## Reasignacion llamadas anteriores.
			my ($sth3) = &Do_SQL($q3);
				
		}elsif($id>0){
			++$forders;
			my $didmx;
			###############################################
			### Llamada que originó la Venta Encontrada ###
			###############################################
			if($didusa > 9999990){
				$didmx = substr($didusa,-4);
			}else{
				my $sth2 = &Do_SQL("SELECT didmx FROM sl_mediadids WHERE didusa=$didusa ");
				$didmx = $sth2->fetchrow;
			}
			
			my $q1 = "UPDATE sl_orders SET DNIS='$didmx', DIDS7='$didusa',first_call='$first_call' WHERE ID_orders=$rec->{'ID_orders'};";

			## Se actualiza DNIS y DIDS7 de la orden sin importar el rango de diferencia en la llamada
			my ($sth2) = &Do_SQL($q1);

			if($diff <= $r1){

				my $q2 = "UPDATE sl_leads_calls SET ID_orders=$rec->{'ID_orders'} WHERE ID_leads_calls=$id;";

				## R1 / Orden del mismo dia que la llamada
				my ($sth2) = &Do_SQL($q2);

			}else{
				## R2  / Orden generada con llamada de salida dentro de los 7 dias de la llamada Original
				## R3  / Orden generada con llamada de salida dentro de los 30 dias de la llamada Original
		
				if (load_name('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'user_type') =~ /cc103|Ext01/ ){
					$cc = 'Vixicom';
				}else{
					$cc = 'Mixcoac';
				}
				
				my $q2 = "REPLACE INTO sl_leads SET ID_leads='$rec->{'Phone1'}', Status='Active',Date=DATE('$rec->{'OrderDate'}'), Time=TIME('$rec->{'OrderDate'}'), ID_admin_users=$id_user_out;";
				my $q3 = "REPLACE INTO sl_leads_calls SET ID_leads='$rec->{'Phone1'}',IO='Out',DIDUS='$didusa',ID_orders=$rec->{'ID_orders'},Duration='902',Destination='$cc', Date=DATE('$rec->{'OrderDate'}'), Time=TIME('$rec->{'OrderDate'}'), ID_admin_users=$id_user_out;";

				## sl_leads
				my $sth2 = &Do_SQL($q2);
				## sl_leads_calls
				my $sth2 = &Do_SQL($q3);
				## Al ser la llamada de salida la que origina la orden, cambiar el $id y $calldate para que tome el contrato
				$id = $sth2->{'mysql_insertid'};
				$calldate = $rec->{'OrderDate'};
				
			}
			
			## Asignacion de ID_order_assign | Llamadas de seguimiento misma orden
			## Si hay orden futura, determinar pertenecia ultima llamada
			my $lead_blk;
			if ($next_order){

				$q_order = "CONCAT( Date, ' ', Time ) BETWEEN DATE_SUB('$rec->{'OrderDate'}', INTERVAL 7 DAY) AND '$next_order'";

				## Sacar ultima llamada del Rango Orden1 - Orden2
				my $ql = "SELECT ID_leads_calls,CONCAT(Date,' ',Time) AS LeadDate,
						TIMESTAMPDIFF(MINUTE,'$rec->{'OrderDate'}',CONCAT(Date,' ',Time)) AS R1Diff,
						TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time),'$next_order') AS R2Diff,
						$r3 AS DiffLimit
						FROM sl_leads_calls WHERE
						CONCAT(Date, ' ', Time) > '$rec->{'OrderDate'}' AND CONCAT(Date, ' ', Time) < '$next_order'
						AND IO='In' AND ID_orders=0 AND ID_order_assign=0 AND
						$query ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1";

				$sthq = &Do_SQL($ql);
				my ($idlead,$ld,$d1,$d2,$dl) = $sthq->fetchrow();

				## Diferencia Orden 1 > Diferencia Orden2 y Diferencia Orden2 <= Rango Maximo (30 dias)
				if($d1 > $d2 and $d2 <= $r3){
					## Llamada posible generadora proxima orden
					$lead_blk = " AND ID_leads_calls <> $idlead ";
				}

			}else{
				$q_order = "CONCAT( Date, ' ', Time ) BETWEEN DATE_SUB('$rec->{'OrderDate'}', INTERVAL 7 DAY) AND SUBTIME( NOW( ) , '1 12:00:00' ) ";
			}
			
			my $q2 = "UPDATE 
							sl_leads_calls 
					SET 
						ID_order_assign = '$rec->{'ID_orders'}',
						ID_mediacontracts = 0,
						ID_mediacontract_assign = 0 
					WHERE 
						( 
							/*ID_orders = '$rec->{'ID_orders'}' OR
							(*/ 
								$query AND
								ID_orders = 0 AND 
								ID_order_assign = 0 AND 
								DIDUS = $didusa AND
								$q_order
							/*)*/ 
						) 
					$lead_blk; ";
			
			my ($sth2) = &Do_SQL($q2);
			$fleads += $sth2->rows(); 
			

			###############################################################################
			###############################################################################
			############
			############
			############	SECCION 2) ASIGNACION ID_mediacontracts
			############
			############
			################################################################################
			################################################################################


			## REVENUE FRONTIER ASIGNADA EN SECCION 1
			next ORDER if $rf;

			## Busqueda Contrato
			if ($didmx < 9990 and $didmx>0){

				my $qc = "SELECT ID_mediacontracts, TIMESTAMPDIFF(MINUTE,CONCAT(ESTDay, ' ', ESTTime), '$calldate')AS Diff
						FROM sl_mediacontracts WHERE DestinationDID=$didmx AND Status IN(". $cfg{'contract_valid_status'} .") 
						AND TIMESTAMPDIFF(MINUTE,CONCAT(ESTDay, ' ', ESTTime),'$calldate')>-30 ORDER BY Diff LIMIT 1;";

				#&cgierr("$qc") if $rec->{'ID_orders'} == 287784;

				my $sth2 = &Do_SQL($qc);
				($id_cont,$cont_tdif) = $sth2->fetchrow_array;

				if ($id_cont>0){
				
					if ($cont_tdif <= $r2){ #10080

						my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts=$id_cont, ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";
						my $q2 = "UPDATE sl_orders SET ID_mediacontracts=$id_cont WHERE ID_orders=$rec->{'ID_orders'} ;";

						## Dentro del Contrato <= 7 dias 60*24*7=10080
						my ($sth2) = &Do_SQL($q1);
						my ($sth2) = &Do_SQL($q2);

					}elsif($diff <= $r3){
						
						my $dest_did_fd=9997;
						my $station_name_fd='Fidelizacion';
						$new_contract = &add_contract($rec->{'OrderDate'},$dest_did_fd,$station_name_fd);

						my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts=$new_contract, ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";
						my $q2 = "UPDATE sl_orders SET ID_mediacontracts=$new_contract WHERE ID_orders=$rec->{'ID_orders'} ;";

						## Diferencia entre orden y llamada  60 * 24 * 30
						## Contrato de Fidelizacion
						my ($sth2) = &Do_SQL($q1);
						my ($sth2) = &Do_SQL($q2);

					}else{

						my $dest_did_ni=9996;
						my $station_name_ni='No Identificado';
						$new_contract = &add_contract($rec->{'OrderDate'},$dest_did_ni,$station_name_ni);

						my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts=$new_contract, ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";
						my $q2 = "UPDATE sl_orders SET ID_mediacontracts=$new_contract WHERE ID_orders=$rec->{'ID_orders'} ;";

						## Contrato No identificado
						my ($sth2) = &Do_SQL($q1);
						my ($sth2) = &Do_SQL($q2);

					}
				}else{

					## Contrato no encontrado
					my $dest_did_ni=9996;
					my $station_name_ni='No Identificado';
					$new_contract = &add_contract($rec->{'OrderDate'},$dest_did_ni,$station_name_ni);

					my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts=$new_contract, ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";
					my $q2 = "UPDATE sl_orders SET ID_mediacontracts=$new_contract WHERE ID_orders=$rec->{'ID_orders'} ;";

					## Contrato No identificado
					my ($sth2) = &Do_SQL($q1);
					my ($sth2) = &Do_SQL($q2);
					
				}

			}else{
				if ($didmx > 9990){
					++$did99;

					my $dest_did=$didmx;
					my $station_name;
					($didmx == 9995) and ($station_name = 'Wholesale');
					($didmx == 9996) and ($station_name = 'No Identificado');
					($didmx == 9997) and ($station_name = 'Fidelizacion');
					($didmx == 9998) and ($station_name = 'Ecommerce');
					($didmx == 9999) and ($station_name = 'Revenue Frontier');
					$new_contract = &add_contract($day_to_check,$dest_did,$station_name);

					my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts=$new_contract, ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls=$id ;";
					my $q2 = "UPDATE sl_orders SET ID_mediacontracts=$new_contract WHERE ID_orders=$rec->{'ID_orders'} ;";

					## Contrato > 9990
					my ($sth2) = &Do_SQL($q1);
					my ($sth2) = &Do_SQL($q2);

				}else{
					++$nodid;
				}
			}
			
		}else{

			++$nocall;				
			# No tienen llamada queda disponible a la espera que se le asigne DID y llamada mediante Herramienta Order Without DID

		}
	} # while orders

	return ($forders, $fleads);
}


#########################################################
#########################################################	
#	Function: assign_leads_no_order
#   		Asigna contrato para llamadas del dia anterior sin orden asignada
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub assign_leads_no_order {
########################################################
########################################################

	## $day_to_check generado en 
	my ($from_date, $to_date) = @_;
	
	my $r1 = 60 * 24;      # 1440 = 1 Dia
	my $r2 = 60 * 24 * 7;  # 10080 = 7 dias
	my $r3 = 60 * 24 * 30; # 43200 = 30 dias

	my $trrf=0;
	my $tr1=0;
	my $tr2=0;
	my $tr3=0;
	my $tr4=0;
	my $total = 0;

	my $count=0;
	my $found=0;
	my $revfron=0;
	my $did99=0;
	my $nodid=0;
	my $strout='';

	
	my $q= "SELECT ID_leads_calls, ID_leads, DIDUS, Destination, Duration, CONCAT(Date,' ',Time)AS DateLead FROM sl_leads_calls 
			WHERE Date BETWEEN  DATE('$from_date') AND DATE('$to_date')
			/*AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time), NOW() ) > 30 */
			AND IO='In' 
			AND ID_orders = 0 AND ID_order_assign = 0 
			AND ID_mediacontract_assign = 0 AND ID_mediacontracts = 0 
			ORDER BY CONCAT(Date,' ',Time);";

	my ($sth) = &Do_SQL($q);
	my $this_total = $sth->rows();

	if($this_total > 0){

		LEADS:while(my($id,$idlead,$didus,$destination,$duration,$calldate) = $sth->fetchrow()){
			++$count;

			## Llamada repetida?
			my $qi = "SELECT ID_mediacontracts FROM sl_leads_calls WHERE ID_leads = '$idlead' AND DIDUS = '$didus' 
					AND ID_mediacontracts > 0 AND Date = DATE('$calldate') AND CONCAT(Date,' ',Time) < '$calldate' LIMIT 1;";

			my ($sth_qi) = &Do_SQL($qi);
			my($this_mediacontract) = $sth_qi->fetchrow();

			if($this_mediacontract){
				++$dup;
				my $qd = "UPDATE sl_leads_calls SET ID_mediacontract_assign = '$this_mediacontract' WHERE ID_leads_calls = '$id';";
				my ($sth_qd) = &Do_SQL($qd);
				next LEADS;
			}

			my $didmx =  $didus > 9999990 ? substr($didus,-4)  : &load_name('sl_mediadids', 'didusa',$didus,'didmx');
		
			if ($rf{'dids'} =~/$didus/ and $id>0){
				++$revfron;

				### Revenue Frontier
				########################
				my ($sth2) = &Do_SQL("SELECT DATE('$calldate')"); #RF
				$call_date = $sth2->fetchrow; #RF
				my $new_contract = &add_contract($call_date,$rf{'dnis'},$rf{'name'}); #RF
				
				my $q1 = "UPDATE sl_leads_calls SET ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0  WHERE ID_leads_calls = '$id' ;";
				my $q2 = "UPDATE sl_leads_calls SET ID_mediacontract_assign = '$new_contract' WHERE ID_leads = $idlead AND ID_mediacontracts = 0 AND Date='$day_to_check' ;";

				###Asignacion de la llamada
				my ($sth2) = &Do_SQL($q1);
				### Asignar otras llamadas iguales
				my ($sth2) = &Do_SQL($q2);
				$trrf += $sth2->rows();
				
			}elsif($didmx < 9990 and $didmx>0){
				++$found;

				my $qc = "SELECT ID_mediacontracts,CONCAT(ESTDay,' ',ESTTime)AS contract_date, DestinationDID, TIMESTAMPDIFF(MINUTE,CONCAT(ESTDay, ' ', ESTTime), '$calldate')AS Diff
						FROM sl_mediacontracts WHERE DestinationDID=$didmx AND Status IN(". $cfg{'contract_valid_status'} .") 
						AND TIMESTAMPDIFF(MINUTE,CONCAT(ESTDay, ' ', ESTTime),'$calldate')>-30 ORDER BY Diff LIMIT 1;";

				my $sth2 = &Do_SQL("$qc");
				($id_cont,$cont_date,$cont_did,$cont_tdif) = $sth2->fetchrow();
				if ($id_cont>0){

					my $qnext = "SELECT DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 1 MINUTE)  FROM sl_mediacontracts WHERE DestinationDID='$cont_did' AND CONCAT(ESTDay,' ',ESTTime) > '$cont_date' AND Status IN(". $cfg{'contract_valid_status'} .")  ORDER BY CONCAT(ESTDay, ' ', ESTTime) LIMIT 1;";

					my $sth2 = &Do_SQL($qnext);
					$nextcontract = $sth2->fetchrow;

					my $mod = " AND CONCAT(Date,' ',Time) > '$cont_date' ";
					($nextcontract) and ($mod .= " AND CONCAT(Date,' ',Time) < '$nextcontract' ");
				
					if ($cont_tdif <= $r2){ #10080
						## Dentro del Contrato <= 7 dias 60*24*7=10080

						my $qr1 = "WHERE ID_leads='$idlead' AND DIDUS='$didus' $mod AND IO='In' AND ID_orders = 0 AND ID_order_assign = 0 AND ID_mediacontract_assign = 0 AND ID_mediacontracts = 0 AND TIMESTAMPDIFF(MINUTE,'$cont_date',CONCAT(Date,' ',Time)) >-30";

						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontracts = '$id_cont', ID_mediacontract_assign = 0, ID_order_assign = 0 $qr1 ORDER BY TIMESTAMPDIFF(SECOND,'$cont_date',CONCAT(Date,' ',Time)) LIMIT 1;");
						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontract_assign = '$id_cont' $qr1;");
						$tr1 += $sth2->rows();
						
					}elsif($cont_tdif <= $r3){
						## Diferencia entre orden y llamada  60 * 24 * 30
						## Contrato de Fidelizacion
						
						my $dest_did_fd=9997;
						my $station_name_fd='Fidelizacion';
						$new_contract = &add_contract($day_to_check,$dest_did_fd,$station_name_fd);

						my $qr2 = "WHERE ID_leads='$idlead' AND DIDUS='$didus' $mod AND IO='In' AND ID_orders = 0 AND ID_order_assign = 0 AND ID_mediacontract_assign = 0 AND ID_mediacontracts = 0 AND TIMESTAMPDIFF(MINUTE,'$cont_date',CONCAT(Date, ' ',Time)) <= $r3 ";

						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0 $qr2 ORDER BY TIMESTAMPDIFF(SECOND,'$cont_date',CONCAT(Date,' ',Time)) LIMIT 1;");
						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontract_assign = '$new_contract' $qr2;");
						$tr2 += $sth2->rows();
			
					}else{
						## Contrato No identificado

						my $dest_did_ni=9996;
						my $station_name_ni='No Identificado';
						$new_contract = &add_contract($day_to_check,$dest_did_ni,$station_name_ni);

						my $qr3 = "WHERE ID_leads='$idlead' AND DIDUS='$didus' $mod AND IO='In' AND ID_orders = 0 AND ID_order_assign = 0 AND ID_mediacontract_assign = 0 AND ID_mediacontracts = 0 AND TIMESTAMPDIFF(MINUTE,'$cont_date',CONCAT(Date, ' ',Time)) > $r3 ";

						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0 $qr3 ORDER BY TIMESTAMPDIFF(SECOND,'$cont_date',CONCAT(Date,' ',Time)) LIMIT 1;");
						my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontract_assign = '$new_contract' $qr3;");
						$tr3 += $sth2->rows();
						
					}
				}else{
					## Contrato No identificado
					my $dest_did_ni=9996;
					my $station_name_ni='No Identificado';
					$new_contract = &add_contract($day_to_check,$dest_did_ni,$station_name_ni);

					my $qr3 = "WHERE ID_leads='$idlead' AND DIDUS='$didus' AND Date='$day_to_check' AND IO='In' AND ID_orders = 0 AND ID_order_assign = 0 AND ID_mediacontract_assign = 0 AND ID_mediacontracts = 0";

					my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0 $qr3 ORDER BY CONCAT(Date,' ',Time) LIMIT 1;");
					my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontract_assign = '$new_contract' $qr3;");
					$tr3 += $sth2->rows();

				}
			}else{

				if ($didmx > 9990){
					++$did99;

					## Contrato by Params
					my $station_name='No Identificado';
					#(!$didmx) and ($didmx = 9996);
					($didmx eq '9998') and ($station_name='Ecommerce');
					($didmx eq '9997') and ($station_name='Recuperaciones');
					($didmx eq '9999') and ($station_name='Revenue Frontier');
					($didmx eq '9995') and ($station_name='Wholesale');
					($didmx eq '9994') and ($station_name='Fidelizacion');

					my $new_contract = &add_contract($day_to_check,$didmx,$station_name);

					my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontracts = '$new_contract', ID_mediacontract_assign = 0, ID_order_assign = 0 WHERE ID_leads_calls = '$id'");
					my ($sth2) = &Do_SQL("UPDATE sl_leads_calls SET ID_mediacontract_assign = '$new_contract' WHERE ID_leads=$idlead AND Date=DATE('$calldate') AND ID_mediacontracts = 0;");
					$tr4 += $sth2->rows();

				}else{
					++$nodid;
					$strout .= "ID: $id , Lead: $idlead , DIDUS: $didus , DIDMx: $didmx,  Destination: $destination , Duration: $duration, Fecha: $calldate\n";
				}
			}

		}

	}
	$total = $trrf + $tr1 + $tr2 + $tr3 + $tr4;
	return $total;
}



#########################################################
#########################################################	
#	Function: status_contracts
#   		Actualiza Status de Contratos
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub status_contracts {
########################################################
########################################################

	my ($id_mediacontracts_grouped) = @_;

	if(!$id_mediacontracts_grouped){
		return;
	}

	my $q1 = "SELECT *
				FROM sl_mediacontracts 
				WHERE ID_mediacontracts IN($id_mediacontracts_grouped)
				AND DestinationDID>0 AND DestinationDID < 9991
				AND Status IN(". $cfg{'contract_valid_status'} .")
				ORDER BY CONCAT(ESTDay,' ',ESTTime);";

	my ($sth) = &Do_SQL($q1);

	C: while ($contract = $sth->fetchrow_hashref){
		
		my $q2 = "SELECT DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 1 MINUTE)  FROM sl_mediacontracts WHERE DestinationDID=$contract->{'DestinationDID'} AND Status IN(". $cfg{'contract_valid_status'} .") AND TIMESTAMPDIFF(MINUTE,'$contract->{'ESTDay'} $contract->{'ESTTime'}',CONCAT(ESTDay, ' ', ESTTime)) BETWEEN 1 AND $cfg{'contract_nextmin'} ORDER BY DATE_SUB(CONCAT(ESTDay, ' ', ESTTime),INTERVAL 30 MINUTE) ASC LIMIT 1";
		my $sth2 = &Do_SQL($q2);
		$nextcontract = $sth2->fetchrow;
		if (!$nextcontract){
			## No Next Contract, then end in 7 days
			$nextcontract = &sqldate_plus($contract->{'ESTDay'},7). ' '. $contract->{'ESTTime'};
		}


		## Contract will close?
		my $sthf = &Do_SQL("SELECT IF(TIMESTAMPDIFF(MINUTE,NOW(),'$nextcontract') < 30,'Close','Open') AS Action;");
		my ($action) = $sthf->fetchrow();
		

		### Update Contract Status
		my $sth2 = &Do_SQL("SELECT TIMESTAMPDIFF( HOUR , CONCAT( ESTDay, ' ', ESTTime ) , NOW( ) ) FROM `sl_mediacontracts` WHERE ID_mediacontracts=$contract->{'ID_mediacontracts'}");
		my ($td) = $sth2->fetchrow;
		
		if ($action eq 'Close' or $td > 4){

			### Load Calls
			my $q3 = "SELECT 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,1,0))AS P1, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3,

				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,Duration,0))AS D1, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,Duration,0))AS D2, 
				SUM(IF(TIMESTAMPDIFF(MINUTE, '$contract->{'ESTDay'} $contract->{'ESTTime'}', CONCAT(Date, ' ', Time) ) > 360,Duration,0))AS D3				
				
				FROM sl_leads_calls WHERE ID_mediacontracts = '$contract->{'ID_mediacontracts'}' AND IO='In';";

			
			$sth3 = &Do_SQL($q3);
			($contract->{'P1Calls'},$contract->{'P2Calls'},$contract->{'P3Calls'},$contract->{'P1CallsSec'},$contract->{'P2CallsSec'},$contract->{'P3CallsSec'})=$sth3->fetchrow();
			my $tcalls = $contract->{'P1Calls'} + $contract->{'P2Calls'} + $contract->{'P3Calls'};
			my $tdcalls = $contract->{'P1CallsSec'} + $contract->{'P2CallsSec'} + $contract->{'P3CallsSec'};

			my $q4;
			if ($contract->{'Status'} =~ /Programado|NoTX: Pendiente|Auto Transmitido/){
				if ($contract->{'Cost'}<100){
					$q4 = "/*Cost < 100*/ UPDATE sl_mediacontracts SET Status='Auto Transmitido', MediaStatus='Close' WHERE ID_mediacontracts='$contract->{'ID_mediacontracts'}';";
				}else{
					if ($contract->{'P1Calls'}>0){
						if ($contract->{'Cost'}/$contract->{'P1Calls'} > 50 and $contract->{'P1Calls'} < 4){
							$q4 = "/*Cost > 50 and Calls < 4*/ UPDATE sl_mediacontracts SET Status='NoTX: Pendiente', MediaStatus='Close' WHERE ID_mediacontracts='$contract->{'ID_mediacontracts'}';";
						}else{
							$q4 = "/*Cost < 50 or Calls > 4*/ UPDATE sl_mediacontracts SET Status='Transmitido', MediaStatus='Close' WHERE ID_mediacontracts='$contract->{'ID_mediacontracts'}';";
						}
					}else{
						$q4 =  "/*No calls*/ UPDATE sl_mediacontracts SET Status='NoTX: Pendiente', MediaStatus='Close' WHERE ID_mediacontracts='$contract->{'ID_mediacontracts'}';";
					}
				}
			}elsif ($action eq 'Close' or $contract->{'Status'} eq 'Transmitido'){
				$q4 = "/*To Close*/ UPDATE sl_mediacontracts SET MediaStatus='Close' WHERE ID_mediacontracts='$contract->{'ID_mediacontracts'}';";
			}

			if ($q4 ne ''){
				my $q5 = "/*Replicas*/ UPDATE sl_mediacontracts INNER JOIN sl_mediacontracts_rep USING(ID_mediacontracts) SET repStatus = Status WHERE sl_mediacontracts_rep.ID_mediacontracts = '$contract->{'ID_mediacontracts'}';";

				my $sth4 = Do_SQL($q4); 
				my $sth5 = Do_SQL($q5);
			}

		}
	}
}



#########################################################
#########################################################	
#	Function: add_contract
#   		Busca contrato de acuerdo a un DID y fecha. De no existir lo crea
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub add_contract {
########################################################
########################################################

	my ($d,$dest_did,$station_name) = @_;

	my $q = "SELECT ID_mediacontracts FROM sl_mediacontracts WHERE ESTDay=DATE('$d') AND DestinationDID='$dest_did';";
	my $sth2 = &Do_SQL($q);
	$id_contract = $sth2->fetchrow;
	if (!$id_contract){
		my $sth2 = &Do_SQL("INSERT INTO sl_mediacontracts SET Station='$station_name',Agency='$station_name',Format='28:30 MIN',StationDate='$d',StationTime='00:00:00',Destination='$dest',ESTDay='$d',ESTTime='00:00:00',DestinationDID='$dest_did',Status='Transmitido',Date=CURDATE(),Time=CURTIME(),ID_admin_users=1");
		$id_contract = $sth2->{'mysql_insertid'};
	}
	return $id_contract
}



#########################################################
#########################################################	
#	Function: clean_phones
#   		Limpia telefonos con caracteres no numericos
#
#	Created by:
#		_Carlos Haas_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub clean_phones {
########################################################
########################################################

	my ($id_customers) = @_;

	my $mod = $id_customers ? " WHERE ID_customers = '$id_customers' " : "";

	my ($sth) = Do_SQL("SELECT ID_customers, CID, Phone1, Phone2, Cellphone FROM sl_customers $mod ORDER BY ID_customers;");
	while( $rec2 = $sth->fetchrow_hashref()){
		++$t;
		$rec2->{'Phone1'} =~ s/-|\(|\)|\+|\.|\s//g;
		$rec2->{'Phone2'} =~ s/-|\(|\)|\+|\.|\s//g;
		$rec2->{'Cellphone'} =~ s/-|\(|\)|\+|\.|\s//g;
		$rec2->{'CID'} =~ s/-|\(|\)|\+|\.|\s//g;
		
		my $q1 = "UPDATE sl_customers SET CID='$rec2->{'CID'}', Phone1='$rec2->{'Phone1'}', Phone2='$rec2->{'Phone2'}', Cellphone='$rec2->{'Cellphone'}' WHERE ID_customers='$rec2->{'ID_customers'}';";

		my ($sthn) = Do_SQL($q1);		
		$u += $sthn->rows;

		return ($rec2->{'CID'}, $rec2->{'Phone1'}, $rec2->{'Phone2'}, $rec2->{'Cellphone'}) if $id_customers;

	}
}


##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
	my (@sys_err) = @_;

	print "\nCGI ERROR\n==========================================\n";
	$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
	$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
	$sys_err[2]	and print "System Message      : $sys_err[2]\n";
	$0			and print "Script Location     : $0\n";
	$]			and print "Perl Version        : $]\n";
	$sid		and print "Session ID          : $sid\n";
	
	exit -1;
}

