sub validate_opr_returns{
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
# Last Modified on: 11/07/08 10:56:42
# Last Modified by: MCC C. Gabriel Varela S: Se valida existencia de 2 UPCs iguales
# Last Modification by JRG : 03/10/2009 : Se agrega el log

	my ($err);
	if($in{'id_returns'}){
		
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		 $va{'matchpayments'} = $sth0->fetchrow();
		if( $va{'matchpayments'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			
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


sub view_opr_repairret{
#-----------------------------------------
# Forms Involved: repairret_edit
# Created on: 10/21/08  09:56:28
# Last Modified on: 10/21/08  09:56:28
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 

$in{'speech'} =  $in{'workdone'};
	
}


sub validate_opr_repairret{
#-----------------------------------------
# Forms Involved: repairret_edit
# Created on: 10/21/08  10:08:00
# Last Modified on: 10/21/08  10:08:00
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 	

	if($in{'status'} ne 'Repair' and $in{'speech'} eq ''){
		++$err;
		$error{'speech'}= 'Work Done Required';
	}
	$in{'workdone'} = $in{'speech'};
	$in{'workdone'} =~ s/\r|\n//g;		#\r|\n
	
	return $err;
}

sub loading_opr_repairret{
#-----------------------------------------
# Forms Involved: 
# Created on: 10/21/08  10:53:54
# Last Modified on: 10/21/08  10:53:54
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 
	
	$in{'speech'} =  $in{'workdone'};
	
}

sub validate_returns {
# --------------------------------------------------------
	my ($err);
	if ($in{'add'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders_products='$in{'id_orders_products'}' AND Status NOT IN ('Void','Resolved');");
		if ($sth->fetchrow>0){
			$error{'id_orders_products'} = &trans_txt('invalid');
			++$err;
		}
		if ($in{'location'} !~ /^[A-Z]\d{3}[A-Z]/i){
			$error{'location'} = &trans_txt('invalid');
			++$err;
		}
	}
	return $err;
	
}

sub view_qcreturns{
# --------------------------------------------------------
# Created on: 5/30/2008 10:34:29 AM
# Last Modified on:5/30/2008 10:34:33 AM
# Last Modified by: Carlos
# Author: Jose
# Description : Search Customer
# Parameters : None
# Last Modified on:01/14/2009
# Last Modified by: Jose Ramirez
	#if (!$in{'receptionnotes'}){
	#	$in{'receptionnotes'} = '---';
	#}

	&fastbacktoinventory();
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
# Last Modified on: 11/06/08 18:16:58
# Last Modified by: MCC C. Gabriel Varela S: Se valida existencia de dos upcs iguales
# Last Modified by: JRG 01/15/2009: Se agrega id_products_exchange para meraction=reship (el mismo propducto)
# Last Modification by JRG : 03/13/2009 : Se agrega log

	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	} elsif($in{'meraction'} eq "ReShip") {
		$in{'id_products_exchange'} = &load_name("sl_orders_products","ID_orders_products",$in{'id_orders_products'},"ID_products");
	} elsif($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} ne ''){
		#do nothing
	} else {
		$in{'id_products_exchange'} = "";
	}
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	if($in{'id_products_exchange'} ne '')
	{
		if($in{'id_products_exchange'}!~/^\d{9}$/)
		{
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
			else
			{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
				{
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}
		else
		{
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
		if($in{'meraction'} eq "To Be Determined by CR" || $in{'qcreturnfees'} eq "To Be Determined by CR" || $in{'qcrestockfees'} eq "To Be Determined by CR"){
			$in{'qcprocessed'} = "To Be Determined by CR";
		}
	} else {
		$in{'qcprocessed'} = "no";
	}
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
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

sub validate_atcreturns{
	# Last Modified on:11/jun/2008 02:16:33 PM
	# Last Modified by: MCC C Gabriel Varela S
	# Description : Se agrega validación de producto cuando es exchange
	# Last Modified on: 11/07/08 10:16:10
	# Last Modified by: MCC C. Gabriel Varela S: Se permiten 2 UPCs iguales
	# Last Modified by: JRG 01/15/2009: Se agrega id_products_exchange para meraction=reship (el mismo propducto)
	# Last Modification by JRG : 03/13/2009 : Se agrega log

	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	} elsif($in{'meraction'} eq "ReShip") {
		$in{'id_products_exchange'} = &load_name("sl_orders_products","ID_orders_products",$in{'id_orders_products'},"ID_products");
	} elsif($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} ne ''){
		#do nothing
	} else {
		$in{'id_products_exchange'} = "";
	}
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	if($in{'id_products_exchange'} ne '')
	{
		if($in{'id_products_exchange'}!~/^\d{9}$/)
		{
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
			else
			{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
				{
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}
		else
		{
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
	
	if(!$in{'atcreturnfees'}){
		$error{'atcreturnfees'} = &trans_txt('required');
		++$err;
	}
	if(!$in{'atcrestockfees'}){
		$error{'atcrestockfees'} = &trans_txt('required');
		++$err;
	}
	if($in{'atcprocessed'} ne 'yes'){
		$in{'atcprocessed'} = "no";
	}

	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
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

GV Inicia
#GV Inicia 09jun2008
sub validate_sorting{
	# Created on: 09/jun/2008 04:57:18 PM GMT -05:00
	# Last Modified on: 11jun2008
	# Last Modified by: MCC C Gabriel Varela S
	# Author: MCC C. Gabriel Varela S.
	# Description : Actualiza los valores para los UPCs
	# Parameters :
	# Description11jun2008 : Se retorna $err
	
	# Last Modified on: 16jun2008
	# Last Modified by: MCC C Gabriel Varela S
	# Description16jun2008 : Se establece para er_orderdata el texto de error en caso de existir
	# Last Modified on: 11/06/08 16:38:30
	# Last Modified by: MCC C. Gabriel Varela S: Se arregla parte para que permita la existencia de 2 upcs iguales
	# Last Modification by JRG : 03/13/2009 : Se agrega log
	
	
	#GV Inicia 12jun2008
	my ($err);	
	#GV Termina 12jun2008
	
	if($in{'id_returns'}){
		#GV Inicia modificación 24jun2008
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
			my $gvi;
			$gvi=0;
			my ($sth1) = &Do_SQL("SELECT UPC,ID_returns_upcs FROM  sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!='' order by UPC");
			#GV Termina modificación 24jun2008
			while ($rec1 = $sth1->fetchrow_hashref){
				$gvi++;
				$upcs = $rec1->{'UPC'};
				$io = $gvi."io_$upcs";
				$st = $gvi."st_$upcs";
				if($in{$io} eq ""){#&cgierr("MSG: $in{$io}");
					#GV Inicia modificación 16jun2008
					$error{'orderdata'} = &trans_txt('required');
					#GV Termina modificación 16jun2008
					$error{$io} = &trans_txt('required');
					++$err;
				}
				if($in{$st} eq ""){#&cgierr("MSG: $in{$io}");
					#GV Inicia modificación 16jun2008
					$error{'orderdata'} = &trans_txt('required');
					#GV Termina modificación 16jun2008
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

sub validate_crreturns
{
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
	# Last Modified on: 11/06/08 17:59:38
	# Last Modified by: MCC C. Gabriel Varela S: Se arregla para manejar 2 upcs iguales en el mismo return
	
	#GV Inicia 11jun2008: Validación de campo id_products_exchange
	#GV Inicia 12jun2008
	#GV Termina 12jun2008
	
	# Last Modified by: JRG 01/15/2009: Se agrega id_products_exchange para meraction=reship (el mismo propducto)
	# Last Modification by JRG : 03/13/2009 : Se agrega log

	my ($err);
	if($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} eq ''){
		$error{'id_products_exchange'} = &trans_txt('required');
		++$err;
	} elsif($in{'meraction'} eq "ReShip") {
		$in{'id_products_exchange'} = &load_name("sl_orders_products","ID_orders_products",$in{'id_orders_products'},"ID_products");
	} elsif($in{'meraction'} eq "Exchange" && $in{'id_products_exchange'} ne ''){
		#do nothing
	} else {
		$in{'id_products_exchange'} = "";
	}
		
	if($in{'id_products_exchange'} ne '')
	{
		if($in{'id_products_exchange'}!~/^\d{9}$/)
		{
			if($in{'id_products_exchange'}!~/^\d{3}-\d{3}-\d{3}$/)
			{
				++$err;
				$error{'id_products_exchange'}=&trans_txt('invalid');
			}
			else
			{
				$in{'id_products_exchange'}=~/^(\d{3})-(\d{3})-(\d{3})$/;
				$in{'id_products_exchange'}="$1$2$3";
				if(&load_name('sl_products','ID_products',"$2$3",'ID_products')<=0 or &load_name('sl_products','ID_products',"$2$3",'ID_products')eq'')
				{
					++$err;
					$error{'id_products_exchange'}=&trans_txt('invalid');
				}
			}
		}
		else
		{
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
		$va{'matches'} = $sth0->fetchrow();
		if($va{'matches'} > 0){
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
#GV Termina 09jun2008
#GV Termina

#JRG start 16-06-2008
sub advsearch_sorting{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'type'}){
			$qry .= " sl_returns.Type='$in{'type'}' ";
		}
		if($in{'generalpckgcondition'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.generalpckgcondition='$in{'generalpckgcondition'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);			
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}

sub advsearch_repairret{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'type'}){
			$qry .= " sl_returns.Type='$in{'type'}' ";
		}
		if($in{'generalpckgcondition'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.generalpckgcondition='$in{'generalpckgcondition'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}

sub advsearch_qcreturns{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'id_returns'}){
			$qry .= " sl_returns.ID_returns='$in{'id_returns'}' ";
		}
		if($in{'meraction'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.merAction='$in{'meraction'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}

sub advsearch_atcreturns{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'id_returns'}){
			$qry .= " sl_returns.ID_returns='$in{'id_returns'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}

sub advsearch_crreturns{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'type'}){
			$qry .= " sl_returns.Type='$in{'type'}' ";
		}
		if($in{'generalpckgcondition'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.generalpckgcondition='$in{'generalpckgcondition'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.id_customers, sl_customers.FirstName FROM sl_returns, sl_customers WHERE $query AND sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}

sub advsearch_retwarehouse{
	# Created on: 16/jun/2008 12:28
	# Last Modified on:
	# Last Modified by:
	# Author: Jose Ramirez Garcia
	# Description : 
	# Parameters :
	# Description :
	if($in{'action'}){
		if($in{'type'}){
			$qry .= " sl_returns.Type='$in{'type'}' ";
		}
		if($in{'generalpckgcondition'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.generalpckgcondition='$in{'generalpckgcondition'}' ";
		}
		if($in{'id_returns'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.ID_returns='$in{'id_returns'}' ";
		}
		if($in{'meraction'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.merAction='$in{'meraction'}' ";
		}
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers AND sl_returns.Status='$in{'status'}' ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
	
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		#&cgierr("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
		
	}elsif($in{'id_table'}){
		return &query('sl_returns');
	}
}


sub advsearch_returns{
#-----------------------------------------
# Created on: 03/02/09  13:41:00 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	if($in{'action'}){
		if($in{'firstname'}){
			$qry .= " sl_customers.firstname='$in{'firstname'}' ";
		}
		if($in{'lastname1'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_customers.lastname1='$in{'lastname1'}' ";
		}
		if($in{'lastname2'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_customers.lastname2='$in{'lastname2'}' ";
		}
		if($in{'phone1'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " (sl_customers.phone1 LIKE '%$in{'phone'}%' OR  sl_customers.phone2 LIKE '%$in{'phone'}%' OR sl_customers.Cellphone LIKE '%$in{'phone'}%') ";
		}

		if($in{'id_orders'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			my ($sth) = &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}'");
			while ($rec = $sth->fetchrow_hashref){
				$id_orders_products .= $rec->{'ID_orders_products'}.",";
			}
			chop($id_orders_products);
			if($id_orders_products){
				$qry .= " sl_returns.id_orders_products IN($id_orders_products) ";
			}
		}	
			
		if($in{'id_returns'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.id_returns='$in{'id_returns'}' ";
		}		
		if($in{'status'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.status='$in{'status'}' ";
		}
		if($in{'type'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.type='$in{'type'}' ";
		}
		if($in{'meraction'}){
			if($qry){
				$qry .= "$in{'st'} ";
			}
			$qry .= " sl_returns.meraction='$in{'id_meraction'}' ";
		}						
		if($in{'fromdate'} && $in{'todate'}){
			$barra = '/';
			$guion = '-';
			$in{'fromdate'}=~ s/$barra/$guion/g;
			$in{'todate'}=~ s/$barra/$guion/g;
			my ($sth)= &Do_SQL("SELECT '$in{'fromdate'}'<='$in{'todate'}'");
			if($sth->fetchrow){
				if($qry){
					$qry .= "$in{'st'} ";
				}
				$qry .= " sl_returns.Date BETWEEN '$in{'fromdate'}' AND '$in{'todate'}' ";				
			}
		}
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');
		if($qry){
			$qry = " (".$qry.") AND ";
		}
		
		my $query = $qry." sl_returns.id_customers=sl_customers.id_customers ".$qry2;

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
	
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
			$st = $rec->{'Status'};
		}
		if ($numhits == 1 or $in{'status'}){
			$in{'cmd'}	=	'sorting'	if	$st eq 'In Process';
			$in{'cmd'}	=	'repairret'	if	$st eq 'Repair';
			$in{'cmd'}	=	'qcreturns'	if	$st eq 'QC/IT';
			$in{'cmd'}	=	'atcreturns'	if	$st eq 'ATC';
			$in{'cmd'}	=	'atcreturns'	if	$st eq 'ATC';
			$in{'cmd'}	=	'crreturns'	if	$st eq 'Processed';
			$in{'cmd'}	=	'retwarehouse'	if	$st eq 'Back to inventory';
		}
		return ($numhits, @hits);
		
	}
}

sub view_repairret{
#-----------------------------------------
# Forms Involved: repairret_edit
# Created on: 10/21/08  09:56:28
# Last Modified on: 10/21/08  09:56:28
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 
# Last Modified on: 01/14/09
# Last Modified by: Jose Ramirez Garcia: se a¤adieron los movimeintos de fast back to inventory
	$in{'speech'} =  $in{'workdone'};
	&fastbacktoinventory();
}

sub view_sorting{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	&fastbacktoinventory();
}

sub view_atcreturns{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	&fastbacktoinventory();
}

sub view_returns{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	&fastbacktoinventory();
}

sub view_crreturns{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 01/14/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	&fastbacktoinventory();
}

sub validate_repairret{
#-----------------------------------------
# Forms Involved: repairret_edit
# Created on: 10/21/08  10:08:00
# Last Modified on: 10/21/08  10:08:00
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 	

	if($in{'status'} ne 'Repair' and $in{'speech'} eq ''){
		++$err;
		$error{'speech'}= 'Work Done Required';
	}
	$in{'workdone'} = $in{'speech'};
	$in{'workdone'} =~ s/\r|\n//g;		#\r|\n
	
	return $err;
}

sub loading_repairret{
#-----------------------------------------
# Forms Involved: 
# Created on: 10/21/08  10:53:54
# Last Modified on: 10/21/08  10:53:54
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
# Author: Roberto Barcenas
# Description :
# Parameters : 
	
	$in{'speech'} =  $in{'workdone'};
	
}


##################################################################
##########     RMAS     	######################
##################################################################
sub customer_search {
# --------------------------------------------------------
# Created on: 5/30/2008 10:34:29 AM
# Last Modified on: 7/8/2008 4:25 PM
# Last Modified by: Jose Ramirez
# Author: Jose
# Description : Search Customer
# Parameters : None
# Last Modified RB: 01/07/09  16:47:08 -- Fixed search by customer data


	my ($query,$tquery,$tbl_name);
	$in{'id_customers'} = int($in{'id_customers'});
	$in{'id_orders'} = int($in{'id_orders'});
	$query = "WHERE sl_orders.Status NOT IN ('Cancelled','System Error') AND sl_orders.ID_customers=sl_customers.ID_customers";
	if ($in{'id_customers'}>0){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE ID_customers='$in{'id_customers'}'");
		if ($sth->fetchrow()>0){
			#&addreturn("$query AND sl_customers.ID_customers='$in{'id_customers'}'");
			&addreturn;
			return;
		}
	}elsif($in{'id_orders'}>0){
		my ($sth) = &Do_SQL("SELECT ID_customers FROM sl_orders WHERE ID_orders='$in{'id_orders'}'");
		$in{'id_customers'} = $sth->fetchrow();
		if ($in{'id_customers'}>0){
			delete($in{'id_orders'});
			#&addreturn("$query AND sl_customers.ID_customers='$in{'id_customers'}'");
			&addreturn;
			return;
		}
	}else{
		#GV Inicia modificaci?n 06jun2008
		if($in{'lastname'}){
			$in{'lastname1'}= &filter_values($in{'lastname'});
		}
		if($in{'phone'}){
			$in{'phone1'}= &filter_values($in{'phone'});
			$in{'phone2'}= &filter_values($in{'phone'});
			$in{'cellphone'}= &filter_values($in{'phone'});
		}
		#GV Termina modificaci?n 06jun2008
		delete($in{'id_customers'});
		&load_cfg('sl_customers');
		$tquery = &query('sl_customers',1);
		($tquery) and ($query .= " AND ($tquery)");
	}

	#GV Inicia 22may2008
	if($in{'rmanum'}){
		#my $sth =&Do_SQL("Select * from sl_rma where ID_rma=$in{'rmanum'}");
		$query.=" and ID_orders in (SELECT sl_orders.ID_orders
							FROM sl_rma
							left JOIN sl_orders_products ON ( sl_rma.ID_orders_products = sl_orders_products.ID_orders_products ) 
							left JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
							WHERE num_rma =$in{'rmanum'}) ";
	}
	#GV Termina 22may2008
	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;	
	(!$in{'nh'}) and ($in{'nh'}=1);
	$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT(sl_customers.ID_customers)) FROM sl_customers,sl_orders $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		#&cgierr("SELECT DISTINCT(sl_customers.ID_customers) FROM sl_customers,sl_orders $query ORDER BY sl_customers.ID_customers $in{'so'} LIMIT $first,$usr{'pref_maxh'};");
		my ($sth) = &Do_SQL("SELECT DISTINCT(sl_customers.ID_customers),sl_customers.* FROM sl_customers,sl_orders $query ORDER BY sl_customers.ID_customers $in{'so'} LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			if($va{'matches'} == 1){
				$in{'id_customers'} = $rec->{'ID_customers'};
				&addreturn;
				return;
			}
			
			$d = 1 - $d;
			#GV Inicia Modificaci?n 26may2008 Se incluye al final &genrmanum=$in{'rmanum'}
			$cadrma="";
			if($in{'rmanum'})
			{
				my $sthin=&Do_SQL("Select ID_orders_products from sl_rma where num_rma=$in{'rmanum'}");
				my $recin=$sthin->fetchrow();
				#$cadrma="&genrmanum=$in{'rmanum'}";
				$cadrma="&id_orders_products=$recin";
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/wms/admin?cmd=addreturn&id_customers=$rec->{'ID_customers'}$cadrma')\">\n";
			#GV Termina Modificaci?n 26may2008
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>$rec->{'ID_customers'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'FirstName'} $rec->{'LastName1'} $rec->{'LastName2'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'State'}</td>\n";
			$tel = "";
			if($rec->{'Phone1'}){
				$tel .= "$rec->{'Phone1'}<br>";
			}
			if($rec->{'Phone2'}){
				$tel .= "$rec->{'Phone2'}<br>";
			}
			if($rec->{'Cellphone'}){
				$tel .= "$rec->{'Cellphone'}<br>";
			}										
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$tel</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'Status'}</td>\n";
			my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers='$rec->{'ID_customers'}' AND Status NOT IN ('Cancelled','System Error')");
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='center'>".&format_number($sth2->fetchrow)."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	$va{'page_title'} = trans_txt("pageadmin");
	print "Content-type: text/html\n\n";
	print &build_page('opr_returns_custlist.html');
}

sub addreturn {
# --------------------------------------------------------
# Created on: unknown
# Last Modified on:11/jun/2008 12:56:33 PM
# Last Modified by: MCC C Gabriel Varela S
# Author: unknown
# Description : Agrega un registro a returns. Se agrega que valide que se escriba algo en upcs
# Parameters : query

# Last Modified on:12/jun/2008 11:53:33 AM
# Last Modified by: MCC C Gabriel Varela S
# Description : Se valida que el n?mero de items introducido coincida con el n?mero de UPCs introducidos
# Parameters : query
# Last Modified on: 09/05/08 12:19:35
# Last Modified by: MCC C. Gabriel Varela S: Se hacen que se contemple el ID de orden tambi?n en sl_returns
# Last Modified on: 09/11/08 13:10:13
# Last Modified by: MCC C. Gabriel Varela S: Se valida la entrada de las notas
# Last Modified RB: 12/01/08  13:28:33 -- Se agrego la segunda tabla que muestra servicios y productos devueltos en la orden
# Last Modified RB: 02/18/09  12:58:31 -- Se redirecciona a sorting
# Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified RB: 05/21/09  12:10:09 -- Se agrega restriccion de Sets ingresados como UPC.


	my ($err);
	my ($query) = @_;
	if ($query){
		
	}elsif ($in{'id_customers'}){
		$va{'customername'} = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[FirstName] [LastName1] [LastName2]');
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	
	$va{'searchresults'}=&showitemsordered();
	$va{'searchresults2'}=&showservicesordered();
	
	$in{'status'} = 'In process';
	if ($in{'action'} and $in{'cmdaddform'}){
		$in{'id_orders'}=&load_name('sl_orders_products','ID_orders_products',$in{'id_orders_products'},'ID_orders');

		require "../../common/subs/sub.add.html.cgi";
		require "dbman.html.cgi";
		$in{'db'} = 'sl_returns';
		$in{'add'} = 1;
		$in{'cmd'} = 'returns';
		&load_cfg('sl_returns');
		my ($message) = &add_record;
				
		#validating the upcs
		@ary = split(/\n|\s/,$in{'upcs'});
		if($#ary<0){
			++$err;
		}elsif($#ary+1!=$in{'itemsqty'}){
			++$err;
		}
		
		### Cehcking valid UPCs
		for (0..$#ary){
			$ary[$_] =~ s/\n|\r|\s//g;
			my ($sth_chk) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE UPC='$ary[$_]' AND IsSet='N' AND UPC != '' AND UPC >0");
			$va{'upcreg'} = $sth_chk->fetchrow();
			if($va{'upcreg'}<1){
				$invalids .= '&nbsp;&nbsp;'.$ary[$_].'<br>';
				++$err;
			}
		}
		
		if($err > 0){
			$error{'upcs'} = '<br>'.&trans_txt('invalid').':<br>'.$invalids;
			$va{'message'} = &trans_txt('reqfields');
			$va{'page_title'} = trans_txt("pageadmin");
			print "Content-type: text/html\n\n";
			print &build_page('opr_returns_addform.html');
			exit;
		}
		


		if ($message eq "ok"){
			if($in{'receptionnotes'}){
				my ($sth)=&Do_SQL("SELECT last_insert_id(ID_returns)as last from sl_returns order by last desc limit 1");
				$lastid=$sth->fetchrow();
				my ($sth) = &Do_SQL("INSERT INTO sl_returns_notes(ID_returns, Notes, Type, Date, Time, ID_admin_users) VALUES('$lastid','".&filter_values($in{'receptionnotes'})."','Reception',Curdate(),NOW(),'$usr{'id_admin_users'}');");
				&auth_logging('returns_noteadded',$sth->{'mysql_insertid'});
			}
			my ($sth)=&Do_SQL("SELECT last_insert_id(ID_returns)as last from sl_returns order by last desc limit 1");
			$lastid=$sth->fetchrow();
			@ary = split(/\n|\s/,$in{'upcs'});
			for (0..$#ary)
			{
				$ary[$_] =~ s/\n|\r|\s//g;
				my ($sth2) = &Do_SQL("INSERT INTO sl_returns_upcs SET ID_returns='$lastid', UPC='$ary[$_]', Date=Curdate(), Time=Now(), ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('upc_added',$lastid);
			}
			#Se verifican las entradas y/o se modifican los estados de ?rdenes y de productos para ?rdenes seg?n sea el caso
			if($in{'type'}eq'Undeliverable Intercepted' or $in{'type'}eq'Undeliverable Refused by Cust' or $in{'type'}eq'Undeliverable Other')
			{
				#Obtiene el n?mero de orden
				my ($sth)=&Do_SQL("SELECT ID_orders from sl_orders_products where ID_orders_products=$in{'id_orders_products'}");
				$idorder=$sth->fetchrow();
				&Do_SQL("UPDATE sl_orders SET Status='Shipped',StatusPrd='Undeliverable Review' where ID_orders=$idorder");
				&auth_logging('orders_updated',$idorder);
			}
			elsif($in{'type'} eq 'Undeliverable Not Delivery 3 Attempt' or $in{'type'} eq 'Undeliverable Wrong address')
			{
				#Obtiene el n?mero de orden
				my ($sth)=&Do_SQL("SELECT ID_orders from sl_orders_products where ID_orders_products=$in{'id_orders_products'}");
				$idorder=$sth->fetchrow();
				&Do_SQL("UPDATE sl_orders SET Status='Shipped',StatusPrd='Undeliverable ATC' where ID_orders=$idorder");
				&auth_logging('orders_updated',$idorder);
			}
			
			#Se verifican las entradas y/o se modifican los estados de ?rdenes y de productos para ?rdenes seg?n sea el caso
			delete($va{'searchresults'});
			$va{'message'} = &trans_txt('returns_added') . "  " . $in{lc($db_cols[0])};
			print "Location: /cgi-bin/mod/wms/dbman?cmd=sorting&view=$lastid&message=$va{'message'}\n\n";
			return;
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}
	
	$va{'page_title'} = trans_txt("pageadmin");
	print "Content-type: text/html\n\n";
	print &build_page('opr_returns_addform.html');
}


1;