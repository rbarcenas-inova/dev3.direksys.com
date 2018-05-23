#!/usr/bin/perl
##################################################################
#   REPORTS : FINANCE
##################################################################



#############################################################################
#############################################################################
#   Function: rep_typify_audit
#
#       Es: Reporte para la Auditoria de las Tipificaciones
#       En: 
#
#    Created on: 19/02/2016
#
#    Author: HC
#
#    Modifications:
#
#        - Modified on ** by *** : 
#
#   Parameters:
#  Returns:
#
#   See Also:
#
#
sub rep_typify_audit{

	if($in{'action'}){
		my ($query_tot,$query_list);


		$query = " FROM 
					( 
						SELECT 
							admin_users.Username, 
							CONCAT(admin_users.FirstName, ' ', admin_users.MiddleName, ' ', admin_users.LastName) Name, 
							admin_users.extension, 
							sl_crmtypify.callerid, 
							sl_crmtypify.area, 
							sl_crmtypify.type, 
							sl_crmtypify.subtype, 
							sl_crmtypify.id_orders, 
							sl_orders.ptype, 
							sl_orders.id_admin_users vendor, 
							(	SELECT 
									CONCAT(admin_users.FirstName, ' ', admin_users.MiddleName, ' ', admin_users.LastName) 
								FROM admin_users 
								WHERE 
									id_admin_users = sl_orders.id_admin_users
							) vendor_name, 
							sl_crmtypify.date, 
							sl_crmtypify.time 
						FROM 
							admin_users 
							INNER JOIN sl_crmtypify ON (admin_users.id_admin_users = sl_crmtypify.id_admin_users) 
							LEFT JOIN sl_orders USING (id_orders) 
					) tmp ";

		$query .= " WHERE 1 ";

		####################################################
		# Filtros
		####################################################
		## ID_admin_users
		if( $in{'equal_id_user'} ){
			$query .= " AND tmp.vendor = '$in{'equal_id_user'}' ";	
		}else{
			if( $in{'from_id_user'} ){
				$query .= " AND tmp.vendor >= '$in{'from_id_user'}' ";
			}
			if( $in{'to_id_user'} ){
				$query .= " AND tmp.vendor <= '$in{'to_id_user'}' ";
			}
		}

		## Extension
		if( $in{'equal_extension'} ){
			$query .= " AND tmp.extension = '$in{'equal_extension'}' ";	
		}else{
			if( $in{'from_extension'} ){
				$query .= " AND tmp.extension >= '$in{'from_extension'}' ";
			}
			if( $in{'to_extension'} ){
				$query .= " AND tmp.extension <= '$in{'to_extension'}' ";
			}
		}

		## Callerid
		if( $in{'equal_callerid'} ){
			$query .= " AND tmp.callerid = '$in{'equal_callerid'}' ";	
		}else{
			if( $in{'from_callerid'} ){
				$query .= " AND tmp.callerid >= '$in{'from_callerid'}' ";
			}
			if( $in{'to_callerid'} ){
				$query .= " AND tmp.callerid <= '$in{'to_callerid'}' ";
			}
		}

		## Type
		if( $in{'equal_type'} ){
			$query .= " AND tmp.type = '$in{'equal_type'}' ";	
		}else{
			if( $in{'from_type'} ){
				$query .= " AND tmp.type >= '$in{'from_type'}' ";
			}
			if( $in{'to_type'} ){
				$query .= " AND tmp.type <= '$in{'to_type'}' ";
			}
		}

		## Subtype
		if( $in{'equal_subtype'} ){
			$query .= " AND tmp.subtype = '$in{'equal_subtype'}' ";	
		}else{
			if( $in{'from_subtype'} ){
				$query .= " AND tmp.subtype >= '$in{'from_subtype'}' ";
			}
			if( $in{'to_subtype'} ){
				$query .= " AND tmp.subtype <= '$in{'to_subtype'}' ";
			}
		}

		## Date
		if( $in{'equal_date'} ){
			$query .= " AND tmp.date = '$in{'equal_date'}' ";	
		}else{
			if( $in{'from_date'} ){
				$query .= " AND tmp.date >= '$in{'from_date'}' ";
			}
			if( $in{'to_date'} ){
				$query .= " AND tmp.date <= '$in{'to_date'}' ";
			}
		}


		####################################################

		#$in{'sortorder'}	=	'' if	!$in{'sortorder'};
		$sb = "ORDER BY date DESC";

		$report_name = "Audit Typification";
		$usr{'pref_maxh'} = 30;
		$query_tot  = "SELECT COUNT(*) $query ";
		$query_list = "SELECT Name, Username, extension, callerid, area, type, subtype, vendor, vendor_name, id_orders, date, time, ptype  
						$query 
						$sb";

		foreach $key (keys %in){
			$in{'qs'} .= "$key=$in{$key}&" unless ($key eq 'cmd');
		}

		my ($sth) = &Do_SQL($query_tot);
		$va{'matches'} = $sth->fetchrow();

		if ($va{'matches'} > 0){

			my $workbook,$worksheet;
			my $url = $va{'script_url'};
			$url =~ s/admin/dbman/;

			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			my ($sth) = &Do_SQL($query_list);
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			if ($in{'print'} or $in{'export'}){

				if($in{'export'}){

					my $date_name;
					if( $in{'from_date'} or $in{'to_date'}){
						$date_name = '-'.$in{'from_date'}.'-'.$in{'to_date'};
					}

					my $fname   = 'audit_typification'.$date_name.'.csv';


					#($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
					#($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
					#($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
					#($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
					#$fname =~	s/\///g;

					use Spreadsheet::WriteExcel;

					# Send the content type
					#print "Content-type: application/vnd.ms-excel\n\n";
					print "Content-type: text/csv\n";
					print "Content-disposition: attachment; filename=$fname\n\n";

					# Redirect the output to STDOUT
					$workbook  = Spreadsheet::WriteExcel->new("-");
					$worksheet = $workbook->add_worksheet();
					# Write some text.
					$worksheet->write(0, 0,'Forma Pago');
					$worksheet->write(0, 1,'Orden');
					$worksheet->write(0, 2,'Vendor Name');
					$worksheet->write(0, 3,'Vendor');
					$worksheet->write(0, 4,'Area');
					$worksheet->write(0, 5,'Hora');
					$worksheet->write(0, 6,'Fecha');
					$worksheet->write(0, 7,'Subtipo');
					$worksheet->write(0, 8,'Tipo');
					$worksheet->write(0, 9,'Telefono');
					$worksheet->write(0, 10,'Extension');
					$worksheet->write(0, 11,'Usuario');
					$worksheet->write(0, 12,'Nombre');
				}

				$sth = &Do_SQL($query_list);
			}else{
				$sth = &Do_SQL($query_list ." LIMIT $first,$usr{'pref_maxh'}");
			}

			my (@c) = split(/,/,$cfg{'srcolors'});
			my $row=1;
			while ($data = $sth->fetchrow_hashref()){
				$d = 1 - $d;
				my $num_tarj = "";
				my $date_tarj = "";

				if($in{'export'}){

					# Write data
					$worksheet->write($row, 0, $data->{'ptype'});
					$worksheet->write($row, 1, $data->{'id_orders'});
					$worksheet->write($row, 2, $data->{'vendor_name'});
					$worksheet->write($row, 3, $data->{'vendor'});
					$worksheet->write($row, 4, $data->{'area'});
					$worksheet->write($row, 5, $data->{'time'});
					$worksheet->write($row, 6, $data->{'date'});
					$worksheet->write($row, 7, $data->{'subtype'});
					$worksheet->write($row, 8, $data->{'type'});
					$worksheet->write($row, 9, $data->{'callerid'});
					$worksheet->write($row, 10, $data->{'extension'});
					$worksheet->write($row, 11, $data->{'Username'});
					$worksheet->write($row, 12, $data->{'Name'});

				}else{

					$va{'searchresults'} .= qq|
									<tr bgcolor='$c[$d]' style="height:25px;">
										<td class="smalltext">$data->{'ptype'}</td>
										<td class="smalltext">$data->{'id_orders'}</td>
										<td class="smalltext">$data->{'vendor_name'}</td>
										<td class="smalltext">$data->{'vendor'}</td>
										<td class="smalltext">$data->{'area'}</td>
										<td class="smalltext">$data->{'time'}</td>
										<td class="smalltext">$data->{'date'}</td>
										<td class="smalltext">$data->{'subtype'}</td>
										<td class="smalltext">$data->{'type'}</td>
										<td class="smalltext">$data->{'callerid'}</td>
										<td class="smalltext">$data->{'extension'}</td>
										<td class="smalltext">$data->{'Username'}</td>
										<td class="smalltext">$data->{'Name'}</td>
									</tr>\n|;
									#$data->{'PmtField3'}
				}
				$row++;
			}

		}else{
			#$va{'matches'} = 0;
			#$va{'pageslist'} = 1;
			#$va{'searchresults'} .= qq|<tr><td align="center" colspan="5">|.&trans_txt('search_nomatches').qq|</td></tr>|;
			
			$va{'message'} = &trans_txt('rep_orders_empty_result');
			print "Content-type: text/html\n\n";
			print &build_page('rep_typify_audit.html');		
		}

		### Report Headet
		$va{'report_tbl'} = qq |
						<center>
							<table border="0" cellspacing="0" cellpadding="4" width="70%" class="formtable">
								<tr>
										<td class="menu_bar_title" colspan="2">Report Name : $report_name</td>
								</tr>
								<tr>									
									<td class="menu_bar_title">ID Orden</td>
									<td class="menu_bar_title">Canal de Venta</td>
									<td class="menu_bar_title">ID Pago</td>
									<td class="menu_bar_title">Tipo de Pago</td>
									<td class="menu_bar_title">Monto</td>
									<td class="menu_bar_title">No. de Tarjeta</td>
									<td class="menu_bar_title">Estatus Orden</td>
									<td class="menu_bar_title">Fecha de Vencimiento</td>
									<td class="menu_bar_title">Cod. Autorizacion</td>
									<td class="menu_bar_title">Captura</td>
									<td class="menu_bar_title">Fecha Orden</td>
									<td class="menu_bar_title">Fecha Captura</td>
									<td class="menu_bar_title">Fecha Envio</td>
									<td class="menu_bar_title">Meses a Pagar</td>
									<td class="menu_bar_title">ID Cliente</td>
									<td class="menu_bar_title">Cliente</td>
									<td class="menu_bar_title">Calle Y Numero</td>
									<td class="menu_bar_title">Colonia</td>
									<td class="menu_bar_title">Delegacion/Municipio</td>
									<td class="menu_bar_title">Estado</td>
									<td class="menu_bar_title">CP</td>
									<td class="menu_bar_title">Tipo de Envio</td>
									<td class="menu_bar_title">ID Usuario</td>
									<td class="menu_bar_title">Usuario</td>
									<td class="menu_bar_title">Forma de Pago</td>
									<td class="menu_bar_title">Telefono</td>
								</tr>
								$va{'report_tbl'}
								<tr>
									<td class="smalltext" colspan="2">Created by : ($usr{'id_admin_users'}) $usr{'firstname'} $usr{'lastname'} \@ |.&get_sql_date ." &nbsp;" . &get_time() .qq|</td>
								</tr>
							</table>
						</center>|;


		&auth_logging('report_view','');
		if ($in{'print'}){
			print "Content-type: text/html\n\n";
			print &build_page('header_print.html');
			print &build_page('results_rep_typify_print.html');
		}else{
			print "Content-type: text/html\n\n";
			print &build_page('results_rep_typify_print.html');
		}
	}else{
		print "Content-type: text/html\n\n";
		print &build_page('rep_typify_audit.html');
	}
}

1;