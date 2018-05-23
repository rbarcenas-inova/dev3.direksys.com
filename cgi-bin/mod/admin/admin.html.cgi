#!/usr/bin/perl


##################################################################
#      CUSTOM PAGES       	#
##################################################################
sub custom_page {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my ($fname) = $cfg{'path_templates'};
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if ($vkey{'custom_name'}){
		if (-e "$fname/custpages/$vkey{'custom_name'}/$in{'page'}.html"){
			print "Content-type: text/html\n\n";
			print &build_page("/custpages/$vkey{'custom_name'}/$in{'page'}.html");	
			return;	
		}
	}
	&html_base_home;
}





##################################################################
#    OPERATIONS : ORDERS   	#
##################################################################



sub updtracking_list {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	if ($in{'action'}){
		my ($filename,$key);
		foreach $key (keys %in){
			if ($key =~ /^run(.*)/){
				#GV Inicia modificación 02jun2008: Se agrega parámetro vacío a la función
				#GV Inicia Modifica 03jun2008
				&updtracking_run($1,"$in{'Todo'}");
				#GV Termina Modifica 03jun2008
				#GV Termina modificación 02jun2008: Se agrega parámetro vacío a la función
				return;
			}elsif($key =~ /^del(.*)/){
				$filename = $1;
				$in{'action'} = 'del';
				$file = "$cfg{'path_cybersource'}imports/$filename";
				unlink ($file);
			}
		}
	}
	
	opendir (AUTHDIR, "$cfg{'path_cybersource'}imports/") || &cgierr("Unable to open directory $cfg{'path_cybersource'}",604,$!);
		@files = readdir(AUTHDIR);		# Read in list of files in directory..
	closedir (AUTHDIR);

	if ($#files > 1){
		for (0..$#files){
			next if ($files[$_] =~ /^\./);		# Skip "." and ".." entries..
			$va{'searchresults'} .= qq|
			<tr>
				<td width="20%"><input type="submit" class="button" name="run$files[$_]" value="Run">
					<input type="submit" class="button" name="del$files[$_]" value="Del"></td>
				<td>$files[$_]</td>
			</tr>\n|;
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print &build_page('opr_outbound_upflist.html');
}

#RB Start
####################################
##    SHIP DATE VS 1ST PAYMENT    ##
####################################

sub opr_checkpayshpdate{
#-------------------------------
# Forms Involved: shvspay.html
# Created on: 4/3/2008 9:43AM
# Last Modified on: 4/03/2008 
# Last Modified by: Roberto Barcenas
# Author: Roberto Barcenas
# Description : Takes every order shipped and check if the first payment date is the same than the 1st shpping day
# Parameters : 

		my ($sth) = &Do_SQL("SELECT COUNT( DISTINCT ID_orders ) FROM sl_orders_products WHERE STATUS = 'Active' ");
		$cont_l=$sth->fetchrow;
		if ($cont_l>0){	
			my (@c) = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
			$va{'matches'} = $cont_l;			
			my($cont)=10;
		  ($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		
			$flexpays = 0;
			my $sth = &Do_SQL("SELECT DISTINCT ID_orders,ShpDate FROM sl_orders_products WHERE Status = 'Active' ORDER BY ID_orders LIMIT $first,$usr{'pref_maxh'} ");
			while ($rec = $sth->fetchrow_hashref){
					$err =0;		
					my $sth = &Do_SQL("SELECT Capdate FROM sl_orders_payments WHERE Status = 'Approved' AND ID_orders = $rec->{'ID_orders'} ORDER BY Capdate LIMIT 1");
					$capdate = $sth->fetchrow;
					
					if($rec->{'ShpDate'} ne $capdate or $rec->{'ShpDate'} eq '0000-00-00' or $capdate eq '0000-00-00'){
						$err = 1;

						$va{'searchresults'} .= qq|
											<tr  bgcolor="$c[$d]">										
											<td valign="top" nowrap align="center">
											<a href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2&tabs#">$rec->{'ID_orders'}</a></td>
											<td nowrap valign='top' align="right"> $rec->{'ShpDate'} </td>					  							  
											<td nowrap valign='top' align="right"> $capdate </td>					  							  
											</tr>\n|;
					}
				$va{'error_dates'} += $err;					
			}
	}
		
	print "Content-type: text/html\n\n";
	print &build_page('opr_shvspay.html');	

}	


sub updating_flashcalls{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 25 Feb 2010 13:16:38
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: application/octetstream\n";
	print "Content-disposition: attachment; filename=updatesflash.sql\n\n";
	my $datefrom,$id_orders;
	#Se define fecha de partida: 2010-02-19 15:41:35
	$datefrom='2010-02-19 15:41:35';
	#Primero se buscan todos los registros que no tengan ID_Orders asignado
	#my $sth=&Do_SQL("Select * from sl_cdr where isnull(ID_orders)");
	my $sth=&Do_SQL("Select orders.ID_orders,Dateo,Timeo,ordertype,Phone1,Phone2,Cellphone,CID,orders.ID_admin_users
from sl_customers
inner join (Select ID_orders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet,'orders'as ordertype,ID_admin_users
            from sl_orders
            where concat(date,' ',time)>='$datefrom'
			group by ID_orders");
	while(my $rec=$sth->fetchrow_hashref){
		print "Update sl_cdr set ID_orders=$rec->{'ID_orders'},Calification='Contestada - Venta' where (right(src,8)=right('$rec->{'Phone1'}',8) or right(src,8)=right('$rec->{'Phone1'}',8) or right(src,8)=right('$rec->{'Cellphone'}',8) or right(src,8)=right('$rec->{'CID'}',8)) /*and ID_admin_users=$rec->{'ID_admin_users'}*/;\n";
		&Do_SQL("Update sl_cdr set ID_orders=$rec->{'ID_orders'},Calification='Contestada - Venta' where (right(src,8)=right('$rec->{'Phone1'}',8) or right(src,8)=right('$rec->{'Phone1'}',8) or right(src,8)=right('$rec->{'Cellphone'}',8) or right(src,8)=right('$rec->{'CID'}',8)) /*and ID_admin_users=$rec->{'ID_admin_users'}*/;");
# 		#Busca en orders/preorders
# 		($id_orders,$ordertype)=&get_order_idfc($datefrom,$rec->{'src'},$rec->{'ID_admin_users'});
# 		if($id_orders!=-1)
# 		{
# 			#Actualiza sl_cdr con ID_orders y Calificación
# 			#&Do_SQL("Update sl_cdr set ID_orders='$id_orders',Calification='Contestada - Venta' where cdr_id=$rec->{'cdr_id'};");
# 			$va{'message'}.="Update sl_cdr set ID_orders='$id_orders',Calification='Contestada - Venta' where src=$rec->{'src'};<br>\n";
# 			#Actualiza orders/preorders
# 			#&Do_SQL("Update sl_$ordertype set DNIS='$rec->{'accountcode'}',DIDS7='$rec->{'didmx'}' where cdr_id=$rec->{'cdr_id'};");
# 			$va{'message'}.="Update sl_$ordertype set DNIS='$rec->{'accountcode'}',DIDS7='$rec->{'didmx'}' where ID_$ordertype=$id_orders;<br>\n";
# 		}
# 		else
# 		{
# 			$va{'message'}.="Update sl_cdr set ID_orders='0' where src=$rec->{'src'};<br>\n";
# 		}
	}
	#Actualizar a 0 las anteriores?
	#Busca en sl_cdr las que tienen ID_orders asignados
	print "###############################################\n";
	my $sth=&Do_SQL("Select * from sl_cdr where not isnull(ID_orders);");
	while(my $rec=$sth->fetchrow_hashref){
		if($rec->{'ID_orders'}=~/$1/){
			print "Update sl_orders set DNIS='$rec->{'didmx'}',DIDS7='$rec->{'accountcode'}' where ID_orders=$rec->{'ID_orders'} /*and ID_admin_users=$rec->{'ID_admin_users'}*/;\n";
			&Do_SQL("Update sl_orders set DNIS='$rec->{'didmx'}',DIDS7='$rec->{'accountcode'}' where ID_orders=$rec->{'ID_orders'} /*and ID_admin_users=$rec->{'ID_admin_users'}*/;\n");
		}else{
			print "Update sl_preorders set DNIS='$rec->{'didmx'}',DIDS7='$rec->{'accountcode'}' where ID_orders=$rec->{'ID_orders'} and /*ID_admin_users=$rec->{'ID_admin_users'}*/;\n";
			&Do_SQL("Update sl_preorders set DNIS='$rec->{'didmx'}',DIDS7='$rec->{'accountcode'}' where ID_orders=$rec->{'ID_orders'} and /*ID_admin_users=$rec->{'ID_admin_users'}*/;");
		}
	}
}

# sub fin_billingonoff{
# 		cgierr();
# 		if(&check_permissions('fin_billingonoff','','')){
# 			print "Content-type: text/html\n\n";
# 			print &build_page('fin_billingonoff.html');
# 		}else{
# 			&html_unauth;
# 		}
# }

# sub get_order_idfc{
# # --------------------------------------------------------
# # Forms Involved: 
# # Created on: 25 Feb 2010 13:35:56
# # Author: MCC C. Gabriel Varela S.
# # Description :   
# # Parameters :
# 	my($datefrom,$src,$id_admin_users)=@_;
# 	my $sth=&Do_SQL("Select orders.ID_orders,Dateo,Timeo,ordertype,Phone1,Phone2,Cellphone,CID,orders.ID_admin_users
# from sl_customers
# inner join (Select ID_orders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet,'orders'as ordertype,ID_admin_users
#             from sl_orders
#             where concat(date,' ',time)>='$datefrom'
#             union
#             Select ID_preorders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet,'preorders'as ordertype,ID_admin_users
#             from sl_preorders
#             where concat(date,' ',time)>='$datefrom')as orders on(sl_customers.ID_customers=orders.ID_customers)
# where (right('$src',8)=right(Phone1,8) or right('$src',8)=right(Phone2,8) or right('$src',8)=right(Cellphone,8) or right('$src',8)=right(CID,8))
# and orders.ID_admin_users=$id_admin_users
# group by ID_orders");
# 	my $rec=$sth->fetchrow_hashref;
# 	return (-1,-1) if($rec->{'ID_orders'}eq'');
# 	return ($rec->{'ID_orders'},$rec->{'ordertype'});
# }


sub preview_treasury{
#-------------------------------
# Forms Involved: preview_treasury.html
# Created on: 1/1/2017 12:00AM
# Last Modified on: 4/03/2008 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
	
	$va{'e'} 	= $in{'e'};
	$va{'user'} = $usr{'id_admin_users'};
	print "Content-type: text/html\n\n";
	print &build_page('preview_treasury.html');

}


sub treasury_relations{
#-------------------------------
# Forms Involved: preview_treasury.html
# Created on: 1/1/2017 12:00AM
# Last Modified on: 4/03/2008 
# Author: Roberto Barcenas
# Description : 
# Parameters : 
	
	$va{'e'} 	= $in{'e'};
	$va{'user'} = $usr{'id_admin_users'};

	my $current_bank;
	my $table = '';

	my ($sth3) = &Do_SQL("	
							SELECT 
								if(banco is null, 'Undefined', banco), categoria, campo, texto,  cuenta, idtext, idaccount
							FROM
							    (
									SELECT Description banco, largecode texto, campo, IF(subA IS NULL, code, subA) categoria, subB cuenta, idtext, idaccount
									FROM
							        (
										(
											SELECT *
											FROM 
							                (
												SELECT id_vars_config idtext, Description, largecode, subcode subA, code campo
												FROM sl_vars_config
												WHERE sl_vars_config.command IN ('refreshPreviewTreasury')
												ORDER BY description , subcode , largecode
											) texto_categoria
											LEFT JOIN 
							                (
												SELECT id_vars_config idaccount, code, subcode subB
												FROM sl_vars_config
												WHERE sl_vars_config.command IN ('importTreasury')
												ORDER BY subcode , code
											) categoria_cuenta ON texto_categoria.subA = categoria_cuenta.code
										) 
							            UNION ALL
							            (
											SELECT *
											FROM
											(
												SELECT id_vars_config idtext, Description, largecode, subcode subA, code campo
												FROM sl_vars_config
												WHERE sl_vars_config.command IN ('refreshPreviewTreasury')
												ORDER BY description , subcode , largecode
											) texto_categoria 
							                RIGHT JOIN 
							                (
												SELECT id_vars_config idaccount, code, subcode subB
												FROM sl_vars_config
												WHERE sl_vars_config.command IN ('importTreasury')
												ORDER BY subcode , code
											) categoria_cuenta ON texto_categoria.subA = categoria_cuenta.code
										)
									) todo
									GROUP BY idtext , Description , largecode , subA , idaccount , code , subB
									ORDER BY categoria , texto
								) relation
							ORDER BY banco, categoria, campo, texto
						");


	while ( my( $bank, $category, $field, $text, $account, $idtext, $idaccount ) = $sth3->fetchrow() )
	{
		if( $bank ne $current_bank ){
			$table .= '<tr><td colspan="5" class="bank_name">';
			$table .= ($bank eq 'Undefined')? '': '<img class="logo_bank" src="/sitimages/banks/'.$bank.'.png" >';
			$table .= ($bank eq 'Undefined')? 'Undefinde Bank':$bank.'</td></tr>';
			$table .= '<tr class="column_names">  <!--td>Actions</td--> <td>Category</td> <td>Field</td> <td>Text</td> <td>Account</td> </tr>';
			$current_bank = $bank;
		}

		$table .= '<tr> <!--td class="action_td"><!--img src="/sitimages/default/b_drop.png" data-ids=""><img src="/sitimages/default/b_edit.png" data-ids=""></td--> <td>'.$category.'</td> <td>'.$field.'</td> <td>'.$text.'</td> <td>'.$account.'</td> </tr>';

	}

	$va{'table_relations'} = '<table border="1" class="relations" >'.$table.'</table>';

	print "Content-type: text/html\n\n";
	print &build_page('treasury_relations.html');

}

#############################################################################
#############################################################################
#   Function: load_orders_from_layout
#
#       Es: Permite la carga de Ordenes Retail a Direksys a traves de un layout
#       En: Allows the loading of Retail Orders to Direksys through a layout
#
#
#    Created on: 2017-05-22
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#   Returns:
#
#      - 
#
#   See Also:
#
#
sub load_orders_from_layout{
#############################################################################
#############################################################################

	use CGI; 
	use HTTP::File;
	use Data::Dumper;
	use File::Basename;
	use File::Copy;

	my $err = 0;
	if ($in{'action'}){
		
		if (!$in{'id_customers'}){
			$error{'id_customers'} = trans_txt('required');
			$err++;
		}
		if (!$in{'id_orders_alias'}){
			$error{'id_orders_alias'} = trans_txt('required');
			$err++;
		}
		if (!$in{'branch_detail'}){
			$error{'branch_detail'} = trans_txt('required');
			$err++;
		}
		if (!$in{'product_detail'}){
			$error{'product_detail'} = trans_txt('required');
			$err++;
		}

		if (!$err){
			print "Content-type: text/html\n\n";
			$va{'summary'} .= "<h1>".&trans_txt('load_orders_title')."</h1>";

			$cgi = new CGI;
			$upload_path = $cfg{'path_files_uploads'};
			my $id_customer = int($in{'id_customers'});

			## Se carga el arhico detalle de sucursales
			my $branch_detail_file = $cgi->param('branch_detail'); 
			$basename_branch_detail_file = HTTP::File::upload($branch_detail_file,$upload_path);

			my @exts = qw(.csv);
			
			## Validando archivo de sucursales
			my $branch_detail_location = $upload_path.$basename_branch_detail_file;
			my $branch_detail_uploaded = $upload_path."branch_detail_".$in{'id_orders_alias'}.".csv";
			my $branch_detail_processed = $cfg{'path_files_uploads_processed'}."branch_detail_".$in{'id_orders_alias'}.".csv";

			my ($name, $dir, $ext) = fileparse($branch_detail_location, @exts);

			if ($ext ne '.CSV' and $ext ne '.csv'){
				$error{'branch_detail'} = trans_txt('incorrect_file_extension');
				$err++;
				unlink($branch_detail_location);
			}else{
				rename($branch_detail_location,$branch_detail_uploaded);
			}

			## Se carga el arhico detalle de productos
			$product_detail_file = $cgi->param('product_detail'); 
			my $basename_product_detail_file = HTTP::File::upload($product_detail_file,$upload_path);

			## Validando archivo de productos
			my $product_detail_location = $upload_path.$product_detail_file;
			my $product_detail_uploaded = $upload_path."product_detail_".$in{'id_orders_alias'}.".csv";
			my $product_detail_processed = $cfg{'path_files_uploads_processed'}."product_detail_".$in{'id_orders_alias'}.".csv";

			my ($name, $dir, $ext) = fileparse($product_detail_location, @exts);

			if ($ext ne '.CSV' and $ext ne '.csv'){
				$error{'product_detail'} = trans_txt('incorrect_file_extension');
				$err++;
				unlink($product_detail_location);
			}else{
				rename($product_detail_location,$product_detail_uploaded);
			}

			my $errors = 0;
			if (-r $branch_detail_uploaded and -r $product_detail_uploaded and !$err) {
				my $id_orders_alias = 'NULL';

				# Lee archivo 1 que contiene informacion de los productos
				# Una vez que se encuentre el archivo hay que recorrer primero el que tiene el resumen
				my ($string) = '';
				my ($registers1) = 0;
				my (@product, @cve_product, @product_price, @product_tax);

				if (open (FILE, $product_detail_uploaded)) {
					
					$va{'summary'} .= "<h3>".&trans_txt('load_orders_products_info')."</h3>";
					$va{'summary'} .= "<table width='100%'>";
					$va{'summary'} .= "<tr>";
					$va{'summary'} .= "		<th>#</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_upc')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_product')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_system_price')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_price')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_quantity')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_tax')."</th>";
					$va{'summary'} .= "		<th>".&trans_txt('load_orders_comments')."</th>";
					$va{'summary'} .= "</tr>";

					while ($record = <FILE>) {
						chomp $record;
						$registers1++;

						my ($err_messages);
						if ($record =~ m/\"/) {
							$errors++;
							$err_messages .= qq|<span class='error'>|.&trans_txt('load_orders_quotes_error_invalid_line').qq|: $record </span><br>|;
						}

						my @fields = split "," , $record;
						
						## si el campo 2 empieza con  comillas y hay un campo  3 y 4 esta pasando basura y es necesario corregirlo
						if ($fields[2] =~ m/\"/ and $fields[3] and $fields[4]) {
							$fields[2] = $fields[2].$fields[3];
							$fields[3] = $fields[4];
						}

						my $field_id_product = $fields[0];
						my $field_desc_product = $fields[1];
						my $field_qty_product = $fields[2];
						my $field_price_product = $fields[3];
						my $field_tax_product = $fields[4];
						
						## ORDEN DE COMPRA DEL CLIENTE
						$id_orders_alias = $fields[5] if ($fields[5]);

						if ($field_id_product ne '' and $field_price_product ne '' and $field_tax_product ne ''){
							
							# limpiando campo de caracteres de formato
							$fields[2] =~ s/[\" \$]//g;

							$product[$registers1] = $field_id_product;
							$cve_product[$registers1] = $field_desc_product;
							$product_qty[$registers1] = $field_qty_product;
							$product_price[$registers1] = $field_price_product;
							$product_tax_percent[$registers1] = $field_tax_product;

							## como los costos del producto son sin impuesto, hay que calcular el impuesto y el total
							## precio neto
							my $tax = $field_tax_product / 100;
							my $tax_product = $field_price_product * $tax;
							$tax_product = sprintf("%.".$sys{'fmt_curr_decimal_digits'}."f", $tax_product);
							my $price_product_wtax = $field_price_product + $tax_product;

							$product_tax[$registers1] = $tax_product;
							$product_price_wtax[$registers1] = $price_product_wtax;

							# CLAVE IDENTIFICADOR DEL PRODUCTO | DESCRIPCION DEL PRODUCTO | PRECIO |  IVA % | IVA CANTIDAD | PRECIO CON IMPUESTO

							## Se agrega una validacion extra para detectar que los productos solicitados existan antes de ejecutar cualquier proceso.
							my ($sth) = &Do_SQL("SELECT
								sl_customers_parts.SPrice
								, sl_customers_parts.ID_parts
								, sl_parts.Name
							FROM sl_customers_parts
							INNER JOIN sl_skus ON sl_skus.ID_sku_products = (400000000+sl_customers_parts.ID_parts)
							INNER JOIN sl_parts ON sl_parts.ID_parts = sl_customers_parts.ID_parts
							WHERE sl_customers_parts.ID_customers=".$id_customer."
							AND sl_skus.UPC='".$field_id_product."';");
							my ($price_direksys, $id_parts_direksys, $name_direksys) = $sth->fetchrow_array();
							my $err_messages = '';

							$va{'summary'} .= "<tr>";
							$va{'summary'} .= "		<td align='right'>$registers1</td>";
							$va{'summary'} .= "		<td align='right'>$field_id_product</td>";
							$va{'summary'} .= "		<td>$name_direksys</td>";
							$va{'summary'} .= "		<td align='right'>".$price_direksys."</td>";
							$va{'summary'} .= "		<td align='right'>$field_price_product</td>";
							$va{'summary'} .= "		<td align='right'>$product_qty[$registers1]</td>";
							$va{'summary'} .= "		<td align='right'>$product_tax_percent[$registers1]</td>";
							
							if (!$id_parts_direksys){
								$errors++;
								$err_messages.="<span class='error'>".&trans_txt('load_orders_product_not_found')."</span><br>";
							}elsif ($price_direksys != $field_price_product){
								$errors++;
								$err_messages.="<span class='error'>".&trans_txt('load_orders_product_price_invalid')."</span><br>";
							}
							
							$va{'summary'} .= "		<td>$err_messages</td>";
							$va{'summary'} .= "</tr>";
						}
					}
					close FILE;
					$va{'summary'} .= "</table><br>";

					## Recorriendo el archivo que contiene el detalle de Sucursales
					if (open (FILE, $branch_detail_uploaded)) {
						
						$va{'summary'} .= "<h3>".&trans_txt('load_orders_branchs_info')."</h3>";
						$va{'summary'} .= "<table width='100%'>";
						$va{'summary'} .= "<tr>";
						$va{'summary'} .= "		<th>#</th>";
						$va{'summary'} .= "		<th>".&trans_txt('load_orders_branch')."</th>";
						$va{'summary'} .= "		<th>".&trans_txt('load_orders_comments')."</th>";
						$va{'summary'} .= "</tr>";
						
						$branchs_to_process = 0;
						while ($record = <FILE>) {

							chomp $record;
							$registers2++;
							my $err_messages = '';
							my $rec_customershpaddress;

							if ($record =~ m/\"/) {
								$errors++;
								$err_messages .= qq|<span class='error'>|.&trans_txt('load_orders_quotes_error_invalid_line').qq|: $record</span><br>|;
							}

							my @fields = split "," , $record;

							my $customer_alias = $fields[0];

							$va{'summary'} .= "<tr>";
							$va{'summary'} .= "		<td align='right'>$registers2</td>";
							$va{'summary'} .= "		<td>$customer_alias</td>";

							if ($customer_alias ne ''){ 
								$branchs_to_process++;

								$customer_alias =~ s/^\s+|\s+$//g;
								$query = "SELECT * FROM cu_customers_addresses WHERE ID_customers=$id_customer AND Alias LIKE ('%$customer_alias%') LIMIT 1;";
								my ($sth_customer_shpaddress) = &Do_SQL($query);
								$rec_customershpaddress = $sth_customer_shpaddress->fetchrow_hashref;

							}

							if (!$rec_customershpaddress->{'ID_customers'}){
								$errors++;
								$err_messages.="<span class='error'>".&trans_txt('load_orders_invalid_branch_name')."</span><br>";
								
							}
							
							$va{'summary'} .= "		<td>$err_messages</td>";
							$va{'summary'} .= "</tr>";
						}
						close FILE;
						$va{'summary'} .= "</table><br>";
					}else{
						$errors++;
						$va{'summary'} .= qq|<span class='error'>$branch_detail_uploaded NO ENCONTRADO</span><br>|;
					}

					if (!$registers1 or !$branchs_to_process) {
						$errors++;
						$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_nothing_to_process')."</span><br>";
					}

					
				}else{
					$errors++;
					$va{'summary'} .= "<span class='error'>$product_detail_uploaded NO ENCONTRADO</span><br>";
				}

				## Orden duplicada
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE sl_orders.ID_orders_alias='$id_orders_alias' AND sl_orders.ID_customers='$id_customer'");
				my $file_invalid = $sth->fetchrow_array();

				if ($file_invalid){
					$errors++;
					$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_duplicated')."</span><br>";
					# return if (!$in{'forced'});
				}

				## Orden invalida
				if ($id_orders_alias != $in{'id_orders_alias'}){
					$errors++;					
					$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_po_error')." ($id_orders_alias vs $in{'id_orders_alias'})</span><br>";
				}

				if ($errors > 0){
					$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_stop')."</span><br>";
				}else{
					## Inicia el procesamiento de la carga de la orden a Direksys
					&Do_SQL("START TRANSACTION;");
					my $fail = 0;
					$orders_notes = &trans_txt('load_orders_notes');
					
					# lee archivo 2
					my ($registers2) = 0; # lo limitaremos al no de productos que obtuvimos arriba
					my (@office_key, @office_desc,);
					
					if (-r $branch_detail_uploaded and open (FILE, $branch_detail_uploaded)) {		
						while ($record = <FILE>) {
							chomp $record;
							$registers2++;
							$products_in_order=0;

							my @fields = split "," , $record;
							
							$customer_alias = $fields[0];
							# por cada registro(tienda) se crea una orden
							# hasta  esta parte ya debo conocer el id del cliente y sus respectivos datos
							# voy a ir a buscar su ultima compra y me voy a traer sus datos

							my ($sth_last_order) = &Do_SQL("SELECT * FROM sl_orders WHERE ID_customers = '$id_customer' LIMIT 1;");
							$rec_last_order = $sth_last_order->fetchrow_hashref;
							
							my ($sth_customer) = &Do_SQL("SELECT *, (SELECT ifnull(CreditDays,0) FROM sl_terms WHERE Type='Sales' AND Status='Active' AND Name=sl_customers.Pterms LIMIT 1)CreditDays FROM sl_customers WHERE ID_customers = '$id_customer';");
							$rec_customer = $sth_customer->fetchrow_hashref;

							# datos del envio de la tienda correspondiente
							$customer_alias =~ s/^\s+|\s+$//g;
							$query = "SELECT * FROM cu_customers_addresses WHERE ID_customers=$id_customer AND Alias like ('%$customer_alias%') LIMIT 1;";
							my ($sth_customer_shpaddress) = &Do_SQL($query);
							$rec_customershpaddress = $sth_customer_shpaddress->fetchrow_hashref;							
							
							# revisar si el cliente existe
							# si existe entonces crea la orden con sus datos
							my $id_customers_addresses = int($rec_customershpaddress->{'ID_customers_addresses'});

							##si hay shpaddress entonces shpaddress sino entonces la del customer
							if ($rec_customershpaddress->{'ID_customers_addresses'} > 0) {
								$rec_customer->{'Address1'} = $rec_customershpaddress->{'Address1'};
								$rec_customer->{'Address2'} = $rec_customershpaddress->{'Address2'};
								$rec_customer->{'Address3'} = $rec_customershpaddress->{'Address2'};
								$rec_customer->{'Urbanization'} = $rec_customershpaddress->{'Urbanization'};
								$rec_customer->{'City'} = $rec_customershpaddress->{'City'};
								$rec_customer->{'State'} = $rec_customershpaddress->{'State'};
								$rec_customer->{'Zip'} = $rec_customershpaddress->{'Zip'};
								$rec_customer->{'Country'} = $rec_customershpaddress->{'Country'};
							}

							## sl_orders
							$sth_order = &Do_SQL("INSERT INTO sl_orders SET ID_orders=NULL,  trackordernumber=NULL,  ID_customers=".$id_customer.", ID_orders_alias='".$id_orders_alias."'
								,  Pterms='".$rec_customer->{'Pterms'}."'
								,  Ptype='Deposit'
								,  id_customers_addresses='".$rec_customershpaddress->{'ID_customers_addresses'}."'
								,  Address1='".$rec_customer->{'Address1'}."'
								,  Address2='".$rec_customer->{'Address2'}."'
								,  Address3='".$rec_customer->{'Address3'}."'
								,  Urbanization='".$rec_customer->{'Urbanization'}."'
								,  City='".$rec_customer->{'City'}."'
								,  State='".$rec_customer->{'State'}."'
								,  Zip='".$rec_customer->{'Zip'}."'
								,  Country='".$rec_customer->{'Country'}."'
								,  BillingNotes=NULL,  shp_type=1,  shp_name=NULL
								,  shp_Address1='".$rec_customer->{'Address1'}."'
								,  shp_Address2='".$rec_customer->{'Address2'}."'
								,  shp_Address3='".$rec_customer->{'Address3'}."'
								,  shp_Urbanization='".$rec_customer->{'Urbanization'}."'
								,  shp_City='".$rec_customer->{'City'}."'
								,  shp_State='".$rec_customer->{'State'}."'
								,  shp_Zip='".$rec_customer->{'Zip'}."'
								,  shp_Country='".$rec_customer->{'Country'}."'
								,  shp_Notes=NULL,  ID_zones=0,  OrderNotes='$orders_notes'
								,  OrderQty=0.00,  OrderShp=0.00,  OrderDisc=0.00,  OrderTax=0.16,  OrderNet=NULL,  ID_salesorigins=5,  ID_pricelevels=99,  dayspay=NULL,  ID_orders_related=0
								,  question1=NULL,  answer1=NULL,  question2=NULL,  answer2=NULL,  question3=NULL,  answer3=NULL,  question4=NULL,  answer4=NULL,  question5=NULL,  answer5=NULL,  repeatedcustomer='Yes',  Coupon=0,  Flags=0,  DNIS=0,  ID_mediacontracts=0,  DIDS7=0,  Letter=0,  ID_warehouses=0,  first_call=NULL
								,  language='spanish',  StatusPrd='None',  StatusPay='None',  Status='New',  Date=CURDATE(),  Time=CURTIME(),  ID_admin_users=".$usr{'id_admin_users'});
							$id_orders_new = $sth_order->{'mysql_insertid'};
							
							if (int($id_orders_new)>0) {

								# de 1 hasta el numero de productos indicados arriba, se hace el recorrido de cada producto agregando cuantos quiere para esta tienda de cada uno
								# Inserta los productos	
								my $qty;
								my $total = 0;
								my $tax = 0;
								my $SalePrice = 0;
								my $ID_products = 100000000;

								my $total_OrderQty = 0;
								my $total_OrderTax = 0;
								my $total_OrderNet = 0;					
								for my $i(1..$registers1) {
									$qty = int($fields[$i]);
									$product_price[$i] =~ s/ \$//g;

									$SalePrice = $product_price[$i] * $qty;
									$tax = $SalePrice * ($product_tax_percent[$i] / 100);

									### para que pueda insertar la cantidad debe ser ,mayor que cero
									if ($qty > 0) {

										# una validacion mas, confirmamos que el producto exista y este activo
										my $id_parts = $product[$i];
										$sth_val_parts = &Do_SQL("SELECT (SELECT SPrice FROM sl_customers_parts WHERE ID_customers=100105 AND ID_parts=sl_skus.ID_products)as SPrice, sl_skus.ID_sku_products as ID_parts FROM sl_skus WHERE 1 AND sl_skus.UPC='".$id_parts."' AND sl_skus.Status='Active'");
										 
										$rec_parts = $sth_val_parts->fetchrow_hashref;

										if (int($rec_parts->{'ID_parts'}) > 0) {

											$sth_parts = &Do_SQL("INSERT INTO sl_orders_products SET
												ID_orders_products = NULL
												, ID_products=".$ID_products."
												, ID_orders=".$id_orders_new."
												, ID_packinglist=0
												, Related_ID_products=".$rec_parts->{'ID_parts'}."
												, Quantity=".$qty."
												, SalePrice=".($qty * $product_price[$i])."
												, Shipping=0
												, Cost=0
												, Tax=".$tax."
												, Tax_percent=".($product_tax_percent[$i] / 100)."
												, Discount=0
												, FP=1
												, Status='Active'
												, Date=Curdate()
												, Time=NOW()
												, ID_admin_users=".$usr{'id_admin_users'});
											
											$total_OrderQty += $qty;
											$total_OrderTax += $tax;
											$total_OrderNet += $SalePrice;
											$ID_products+=1000000;
											$products_in_order++;
										}else {
											$fail++;
										}
									}
								}

								# suma las catidades de productos de una misma tienda para generar una orden por tienda
								# hay q sumar y hacer un update sobre sl_orders y listo
								my $total_Order = $total_OrderNet + $total_OrderTax;

								&Do_SQL("UPDATE sl_orders SET OrderQty=$total_OrderQty, OrderNet=$total_OrderNet WHERE ID_orders=".$id_orders_new);
									
								# ---------------------- Pago de la Orden 
								my ($sth_ord_payments) = &Do_SQL("INSERT INTO `sl_orders_payments` (`ID_orders_payments`, `ID_orders`, `Type`, `PmtField1`, `PmtField2`, `PmtField3`, `PmtField4`, `PmtField5`, `PmtField6`, `PmtField7`, `PmtField8`, `PmtField9`, `Amount`, `Reason`, `Paymentdate`, `AuthCode`, `AuthDateTime`, `Captured`, `CapDate`, `PostedDate`, `Status`, `Date`, `Time`, `ID_admin_users`) VALUES
								(NULL, '".$id_orders_new."', 'Deposit', '', '', '', '', '', '', '', '', '', '".$total_Order."', 'Sale', DATE_ADD(CURDATE(), INTERVAL ".$rec_customer->{'CreditDays'}." DAY), '', '', NULL, NULL,'0000-00-00', 'Approved', CURDATE(), 'CURTIME()', ".$usr{'id_admin_users'}." )");
								$id_orders_payments = $sth_ord_payments->{'mysql_insertid'};
								
								if (!$id_orders_payments){
									$fail++;
									$va{'summary'} .= qq|<span class='error'>|.&trans_txt('load_orders_fail_payments').qq|: $id_orders_new</span><br>|;
								}

								if (!$products_in_order){
									$fail++;
									$va{'summary'} .= qq|<span class='error'>|.&trans_txt('load_orders_fail_products').qq|: $id_orders_new</span><br>|;
								}

								# ---------------------- Nota a la Orden 
								&add_order_notes_by_type_admin($id_orders_new, $orders_notes, "Low");

								$va{'summary_processed'} .= "<tr>";
								$va{'summary_processed'} .= "		<td align='right'>".$registers2."</td>";
								$va{'summary_processed'} .= "		<td align='right'>".$id_orders_new."</td>";
								$va{'summary_processed'} .= "		<td>$customer_alias</td>"; #$customer_code - 
								$va{'summary_processed'} .= "		<td align='right'>".&format_price($total_Order)."</td>";								
								$va{'summary_processed'} .= "</tr>";

							}else{
								$fail++;
							}
							
						}
						close FILE;
						
						## Si hubo falla en el procesamiento se deshace todo
						if ($fail) {
							&Do_SQL("ROLLBACK;");
							unlink();
							unlink($branch_detail_uploaded);
						}else{
							&Do_SQL("COMMIT;");
							move($product_detail_uploaded, $product_detail_processed);
							move($branch_detail_uploaded, $branch_detail_processed);

							$va{'summary'} .= "<h3>".&trans_txt('load_orders_processed_nfo')."</h3>";
							$va{'summary'} .= "<table width='100%'>";
							$va{'summary'} .= "<tr>";
							$va{'summary'} .= "		<th>#</th>";
							$va{'summary'} .= "		<th>".&trans_txt('load_orders_id_orders')."</th>";
							$va{'summary'} .= "		<th>".&trans_txt('load_orders_branch')."</th>";
							$va{'summary'} .= "		<th>TOTAL</th>";
							$va{'summary'} .= "</tr>";
							$va{'summary'} .= $va{'summary_processed'};
							$va{'summary'} .= "</table><br>";
							$va{'summary'} .= "<h3 class='greentext'>".&trans_txt('load_orders_completed')."</h3>";
							$va{'summary'} .=qq|<a href="/cgi-bin/mod/admin/admin?cmd=repmans&id=2&action=1&equal_233=$in{'id_orders_alias'}&equal_233_text=1&sortorder=DESC&export=Export" target="_blank">|.&trans_txt('load_orders_download_report').qq|</a>|;
						}

					}else{
						$va{'summary'} .= "<span class='error'>$branch_detail_uploaded NOT FOUND.</span><br>";
					}
				}

			}else{
				$va{'summary'} .= "<span class='error'>ERROR AL LEER LOS ARCHIVOS FUENTE.</span><br>";
			}
		}
		$va{'summary'} = '<div class="resumen">'.$va{'summary'}.'</div>';
	}else{
		## Validacion de permisos en folders requeridos para el correcto funcionamiento
		if ($cfg{'path_files_uploads_processed'} and $cfg{'path_files_uploads_processed'} ne ''){
			if (-d $cfg{'path_files_uploads_processed'}){
				$file_test = $cfg{'path_files_uploads_processed'}."test.txt";

				if (open (OUTFILE, ">$file_test")){
					unlink($file_test);
				}else{
					$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_permissions_error')."</span><br>";
				}
			}else{
				$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_fail_path_files_uploads')."</span><br>";
			}
		}else{
			$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_set_fail_path_files_uploads')."</span><br>";
		}

		if ($cfg{'path_files_uploads'} and $cfg{'path_files_uploads'} ne ''){
			if (-d $cfg{'path_files_uploads'}){
				$file_test = $cfg{'path_files_uploads'}."test.txt";

				if (open (OUTFILE, ">$file_test")){
					unlink($file_test);
				}else{
					$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_permissions_error_path_files_uploads_processed')."</span><br>";
				}
			}else{
				$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_fail_path_files_uploads_processed')."</span><br>";
			}
		}else{
			$va{'summary'} .= "<span class='error'>".&trans_txt('load_orders_set_fail_path_files_uploads_processed')."</span><br>";
		}

		$va{'summary'} = '<div class="resumen">'.$va{'summary'}.'</div>' if ($va{'summary'} ne '');
	}

	print "Content-type: text/html\n\n";
	print &build_page('load_orders_from_layout.html');

}

1;