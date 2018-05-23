## Load Dbman
opendir (LIBDIR, "./") || &cgierr("Unable to open directory ./",604,$!);
	@files = readdir(LIBDIR);		# Read in list of files in directory..
closedir (LIBDIR);
FILE: foreach $file (@files) {
	next if ($file !~ /^dbman_/);
	require "./$file";
}


##########################################################
##		DEVELOPER JOBS 		  ##
##########################################################
sub view_dev_jobs {
# --------------------------------------------------------
	if ($in{'responsible'}){
		$in{'responsible_name'} = &load_db_names('admin_users','ID_admin_users',$in{'responsible'},'[Firstname] [Lastname]');
	}
}



##########################################################
##		CUSTOMERS	 		  ##
##########################################################
sub validate_customers {
# --------------------------------------------------------
	my $err;
	if (!$in{'status'}){
		$error{'status'} = &trans_txt('required');
		++$err;
	}	
	return $err;
}


# sub plist_opr_polls{
# 	$query  = "select customer_id, id_customers, id_orders Date, Time from cu_polls_answers group by customer_id;";
# 	$count = "select count(DISTINCT customer_id) from cu_polls_answers;";
# 	my @rs;
# 	my $results = &Do_SQL($query);
# 	while($row = $results->fetchrow_hashref()){
# 		foreach my $key (keys %{$row}) {
# 			push(@rs, $row->{$key});
# 		}
# 	}
# 	$num_row = &Do_SQL($count)->fetchrow();
# 	return ($num_row, @rs);
# }


##########################################################
##		OPERATIONS : ZIP CODES	  ##
##########################################################

sub list_pla_shows {
# --------------------------------------------------------
#Last modified on 18 Aug 2011 15:41:25
#Last modified by: MCC C. Gabriel Varela S. :show_only_list is commented
# $in{'show_only_list'} =1;
}

sub view_pla_shows {
# --------------------------------------------------------
# Created on : 1/1/2007 9:43AM
# Author : Rafael Sobrino
# Description :
#Last modified on 18 Aug 2011 15:41:25
#Last modified by: MCC C. Gabriel Varela S. :show_only_list is commented 
#  	$in{'show_only_list'} =1;
	$in{'dmas'}=&load_name('sl_dmas','ID_dmas',$in{'id_dmas'},'DMA');
	&view_shows;
}


sub validate_crreturns{
# --------------------------------------------------------
# Created on: 09/jun/2008 04:57:18 PM GMT -05:00
# Last Modified on: 11jun2008
# Last Modified by: MCC C Gabriel Varela S
# Author: MCC C. Gabriel Varela S.
# Description : Actualiza los valores para los UPCs
# Parameters :
# Description11jun2008 : Se retorna $err

# Last Modified on:11/jun/2008 02:16:33 PM
# Last Modified by: MCC C Gabriel Varela S
# Description : Se agrega validación de producto cuando es exchange
# Last Modified on: 11/06/08 18:11:35
# Last Modified by: MCC C. Gabriel Varela S: Se arregla para aceptar más de un UPC repetido
# Last Modification by JRG : 03/10/2009 : Se agrega el log

#GV Inicia 11jun2008: Validación de campo id_products_exchange
#GV Inicia 12jun2008
	my ($err);
	#GV Termina 12jun2008
	if($in{'id_products_exchange'} ne ''){
		if($in{'id_products_exchange'}!~/^\d{9}$/){
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}else{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq''){
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}else{
			$in{'id_products_exchange'}=~/^(\d{3})(\d{3})(\d{3})$/;
			$in{'id_products_exchange'}="$1$2$3";
			if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
		}
	}
	#GV Termina 11jun2008
	
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		 $va{'matchpayments'} = $sth0->fetchrow();
		if( $va{'matchpayments'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			#GV Termina modificación 24jun2008
			while ($rec1 = $sth1->fetchrow_hashref){
				$gvi++;
				$upcs = $rec1->{'UPC'};
				$io = $gvi."io_$upcs";
				$st = $gvi."st_$upcs";
				if($in{$io} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$io} = &trans_txt('required');
					++$err;
				}
				if($in{$st} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$st} = &trans_txt('required');
					++$err;
				}
				if($in{$io} && $in{$st}){
					my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET InOrder='$in{$io}', Status='$in{$st}' WHERE ID_returns=$in{'id_returns'} AND UPC=$upcs and ID_returns_upcs=$rec1->{'ID_returns_upcs'};");
					&auth_logging('returns_upcs_updated',$in{'id_returns'});
				}
			}
		}
	}

	#GV Inicia 11jun2008
	return $err;
	#GV Termina 11jun2008
}

sub validate_qcreturns{
# --------------------------------------------------------
# Created on: 5/30/2008 10:34:29 AM
# Last Modified on:5/30/2008 10:34:33 AM
# Last Modified by: Carlos
# Author: Jose
# Description : Search Customer
# Parameters : None

# Last Modified on:11/jun/2008 02:16:33 PM
# Last Modified by: MCC C Gabriel Varela S
# Description : Se agrega validación de producto cuando es exchange
# Last Modified on: 11/06/08 18:19:57
# Last Modified by: MCC C. Gabriel Varela S: Existencia de 2 upcs iguales
# Last Modification by JRG : 03/10/2009 : Se agrega el log

	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	}
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	if($in{'id_products_exchange'} ne ''){
		if($in{'id_products_exchange'}!~/^\d{9}$/){
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/){
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}else{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
				{
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}else{
			$in{'id_products_exchange'}=~/^(\d{3})(\d{3})(\d{3})$/;
			$in{'id_products_exchange'}="$1$2$3";
			if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
		}
	}
	#GV Termina 11jun2008
	
	#GV Inicia modificación 04jun2008
	#if($in{'status'} eq "New" || $in{'status'} eq ""){
	if($in{'status'} eq ""){
		#GV Termina modificación 04jun2008
		$in{'status'} = 'In Process';
	}
	if(!$in{'qcreturnfees'}){
		$error{'qcreturnfees'} = &trans_txt('required');
		++$err;
	}
	if(!$in{'qcrestockfees'}){
		$error{'qcrestockfees'} = &trans_txt('required');
		++$err;
	}
	if($in{'qcprocessed'} eq 'yes'){
		if($in{'meraction'} eq "To Be Determined by ATC" || $in{'qcreturnfees'} eq "To Be Determined by ATC" || $in{'qcrestockfees'} eq "To Be Determined by ATC"){
			$in{'qcprocessed'} = "To Be Determined by ATC";
		}
	} else {
		$in{'qcprocessed'} = "no";
	}
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		 $va{'matchpayments'} = $sth0->fetchrow();
		if( $va{'matchpayments'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			#GV Termina modificación 24jun2008
			while ($rec1 = $sth1->fetchrow_hashref){
				$gvi++;
				$upcs = $rec1->{'UPC'};
				$io = $gvi."io_$upcs";
				$st = $gvi."st_$upcs";
				if($in{$io} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$io} = &trans_txt('required');
					++$err;
				}
				if($in{$st} eq ""){
					$error{'orderdata'} = &trans_txt('required');
					$error{$st} = &trans_txt('required');
					++$err;
				}
				if($in{$io} && $in{$st}){
					my ($sth) = &Do_SQL("UPDATE sl_returns_upcs SET InOrder='$in{$io}', Status='$in{$st}' WHERE ID_returns=$in{'id_returns'} AND UPC=$upcs and ID_returns_upcs=$rec1->{'ID_returns_upcs'};");
					&auth_logging('returns_upcs_updated',$in{'id_returns'});
				}
			}
		}
	}
	return $err;
}

sub view_mkt_speech{
# --------------------------------------------------------
#  	$in{'show_only_list'} =1;
	$in{'did_info'}= &load_name('sl_mediadids','didmx',$in{'id_dids'},'product');
}


##########################################################
##		PROMOTIONS 		  ##
##########################################################
sub view_mkt_promotions{
# --------------------------------------------------------
	
	### Genera el listado de clientes prospectos para la promoci�n
	if( int($in{'clist'}) == 1 && $in{'status'} eq 'New' ){

		## Se valida que exista el prefijo y el folio inicial
		if( ($in{'prefix'} and $in{'prefix'} ne '') and int($in{'start'}) > 0 ){

			my $limit_cust = 100000;

			$in{'start'} = int($in{'start'}) - 1;
			&Do_SQL("SET \@rank=".$in{'start'}.";");
			my $sql_ins = "INSERT INTO cu_customer_promotions(ID_promotions, ID_customers, Unique_code, Date, Time, ID_admin_users)
							SELECT ".$in{'id_promotions'}.", sl_customers.ID_customers, CONCAT('M', \@rank:=\@rank+1), CURDATE(), CURTIME(), ".$usr{'id_admin_users'}."
							FROM (
								SELECT sl_customers.ID_customers, Max(sl_orders.ID_orders)
								FROM sl_customers
									INNER JOIN sl_orders ON sl_orders.ID_customers = sl_customers.ID_customers
									LEFT JOIN sl_returns ON sl_orders.ID_orders = sl_returns.ID_orders
									LEFT JOIN sl_chargebacks ON sl_orders.ID_orders = sl_chargebacks.ID_orders 
										AND sl_chargebacks.`Status` != 'Denied'
									INNER JOIN sl_salesorigins ON sl_orders.ID_salesorigins = sl_salesorigins.ID_salesorigins 
										AND sl_salesorigins.ID_salesorigins != 29
								WHERE sl_orders.Date < CURDATE() 
									AND sl_orders.`Status` = 'Shipped' 
									AND sl_returns.ID_returns IS NULL 
									AND sl_chargebacks.ID_chargebacks IS NULL
								GROUP BY sl_orders.ID_customers
								ORDER BY sl_orders.Date DESC
								LIMIT ".$limit_cust."
							)sl_customers;";
			my $sth_ins = &Do_SQL($sql_ins);


			my $sql = "SELECT sl_customers.ID_customers
						, cu_customer_promotions.Unique_code
						, sl_customers.FirstName
						, sl_customers.LastName1 
						, sl_customers.LastName2 
						, sl_customers.Address1 
						, sl_customers.Urbanization 
						, sl_customers.City 
						, sl_customers.State 
						, sl_customers.Zip 
					FROM sl_customers
						INNER JOIN cu_customer_promotions ON cu_customer_promotions.ID_customers = sl_customers.ID_customers
						/*
						INNER JOIN sl_orders ON sl_orders.ID_customers = sl_customers.ID_customers
						LEFT JOIN sl_returns ON sl_orders.ID_orders = sl_returns.ID_orders
						LEFT JOIN sl_chargebacks ON sl_orders.ID_orders = sl_chargebacks.ID_orders 
							AND sl_chargebacks.`Status` != 'Denied'
						INNER JOIN sl_salesorigins ON sl_orders.ID_salesorigins = sl_salesorigins.ID_salesorigins 
							AND sl_salesorigins.ID_salesorigins != 29
						*/
					WHERE cu_customer_promotions.ID_promotions = ".$in{'id_promotions'}."
						/*
						sl_orders.Date < CURDATE() 
						AND sl_orders.`Status` = 'Shipped' 
						AND sl_returns.ID_returns IS NULL 
						AND sl_chargebacks.ID_chargebacks IS NULL
						*/
					;";
			my $sth = &Do_SQL($sql);

			my $file_content = q|"NUMERO PERSONAL","NOMBRE","APELLIDO PATERNO","APELLIDO MATERNO","DOMICILIO","COLONIA","CIUDAD / MUNICIPIO","ESTADO","C.P."\n|;
			while( my $rec = $sth->fetchrow_hashref() ){
				$file_content .= q|"|.$rec->{'Unique_code'}.q|","|.$rec->{'Firstname'}.q|",|.$rec->{'LastName1'}.q|",|.$rec->{'LastName2'}.q|",|.$rec->{'Address1'}.q|",|.$rec->{'Urbanization'}.q|",|.$rec->{'City'}.q|",|.$rec->{'State'}.q|",|.$rec->{'Zip'}.q|"\n|;
			}

			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=customers_promo".$in{'id_promotions'}.".csv\n\n";
			print "$file_content\r\n";

		} else {
			$va{'message'} = &trans_txt('mkt_promotions_prefix_required');
		}

	}

	if( $in{'status'} eq 'New' ){
		$va{'btn_generate_csv'} = '<a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mkt_promotions&view='.$in{'id_promotions'}.'&clist=1"><img src="/sitimages//default/b_xls.gif" title="Generate Customer List" alt="" border="0"></a>';
	}

}


1;
