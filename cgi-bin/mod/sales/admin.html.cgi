#!/usr/bin/perl

##################################################################
############                HELP                 #################
##################################################################
sub help {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('help:'.$in{'page'}.'.html');
}


##################################################################
############                ORDERS                 #################
##################################################################
sub opr_orders {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('opr_orders_home.html');
}

sub rep_orders {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('orders.html');
}


##################################################################
############                HELP                 #################
##################################################################
sub chgexten {
# --------------------------------------------------------
# Last Modification by JRG : 03/04/2009 : Se agrega log al update de password
	if ($in{'action'}){
		$va{'passnum'} = '----';
		my ($sth) = &Do_SQL("SELECT extension FROM admin_users WHERE extenpass='0' AND ID_admin_users='$usr{'id_admin_users'}'");
		$usr{'extension'} = $sth->fetchrow();
		if ($usr{'extension'}){
			&save_auth_data;
			$va{'message'} = &trans_txt('extenlogin_ok');
		}else{
			$va{'message'} = &trans_txt('extenlogin_error');
		}
	}elsif($usr{'extension'}){
		$va{'passnum'} = '----';
		$va{'message'} = &trans_txt('extenlogin_ok');
	}else{
		srand( time() ^ ($$ + ($$ << 15)) );
		$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");
		while ($sth->fetchrow() !=0){
			$va{'passnum'} = substr((int(rand(10000000000)) + 1),4,4);
			$sth = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE extenpass='$va{'passnum'}' AND ID_admin_users='$usr{'id_admin_users'}'");	
		}
		$sth = &Do_SQL("UPDATE admin_users SET extenpass='$va{'passnum'}' WHERE ID_admin_users='$usr{'id_admin_users'}'");	
		&auth_logging("extenpass_updated",'');
	}	
	print "Content-type: text/html\n\n";
	print &build_page("chg_exten.html");
}

sub msglist {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'message'} = &trans_txt('msgd_nomsgs');
	}
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('msgs_search.html');
}

sub flashcalls{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 19 Feb 2010 16:53:29
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified By RB on 3/1/10 6:16 PM :  Se agrega nota de primera asignacion y variable para link del header
#Last modified on 13 Oct 2010 16:28:32
#Last modified by: MCC C. Gabriel Varela S. :Se hace inner de numbers con numbers_assign

	$va{'cdr_notes'} = '&nbsp;';
	$va{'set_unavailable'} = '';
	if($in{'action'}==1){
		$err=0;
 		#valida la calificacion
 		if (!$in{'calification'}){
 			$err++;
 			$error{'calification'} = &trans_txt('required');
 		}else{
 			#&cgierr("UPDATE sl_cdr SET Calification='$in{'calification'}' WHERE ID_admin_users=$usr{'id_admin_users'}");
			#Hace redireccion si elige "No calificar"
			&Do_SQL("UPDATE sl_cdr SET Calification='$in{'calification'}' WHERE ID_admin_users=$usr{'id_admin_users'} AND (Calification='int-assigned' OR Calification='int-answered')");

			my ($tmp_sth) = &Do_SQL("SELECT src FROM sl_cdr WHERE ID_admin_users=$usr{'id_admin_users'} AND (Calification='int-assigned' OR Calification='int-answered') LIMIT 1");
			my ($tmp_src) = $tmp_sth->fetchrow_array();


			&Do_SQL("INSERT INTO sl_cdr_notes VALUES (0,'$tmp_src','".&load_name('admin_users','id_admin_users',$rec2->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")." asigno la calificacion ".&filter_values($in{'calification'})." en la primer llamada','Low',CURDATE(),CURTIME(),$usr{'id_admin_users'} );");
			if ($in{'calification'} eq 'int-answered'){
				#Actualiza
				if ($in{'id_customers'}){
					print "Location:/cgi-bin/mod/sales/admin?cmd=console_order&step=2&id_customers=$in{'id_customers'}&cid=$in{'cid'}&did=$in{'didmx'}&dids7=$in{'dids7'}&updates7=1\n\n";
				}else{
					print "Location:/cgi-bin/mod/sales/admin?cmd=console_order&step=1&action=1&cid=$in{'cid'}&did=$in{'didmx'}&dids7=$in{'dids7'}&updates7=1\n\n";
				}
				return;
			}elsif ($in{'lastcall'}){
				&html_base_home('home.html');
				return;
			}
 		}
	}
	#Verifica que no tenga registros sin calificar
	my $sth=&Do_SQL("SELECT cdr_id,src,Calification,didmx,calldate,accountcode FROM sl_cdr where ID_admin_users=$usr{'id_admin_users'} and (Calification='int-assigned' or Calification='int-answered') ORDER BY /*cdr_id*/calldate desc LIMIT 1;");
	if($sth->rows>0){
		$va{'message'}="A&uacute;n no calificas el n&uacute;mero que se muestra en pantalla. Asigna una calificaci&oacute;n al n&uacute;mero.";
	}else{
		$va{'o'} = 'DESC';
		my $query=" WHERE (isnull(Calification)or Calification='') ";
		## Cargar Datos de  de sl_vars
		my ($sth) = &Do_SQL("SELECT VValue,Subcode FROM sl_vars WHERE VName = 'Setup Calls Super' ");
		if($sth->rows() > 0){
		    while (my($value,$code) = $sth->fetchrow()){
			$va{$code} = $value;
		    }
		}
		if($va{'hf'}){
		    $query = " INNER JOIN
(SELECT AreaCode,Timezone-5 AS DiffLocal FROM sl_zipcodes GROUP BY AreaCode)as tmp
ON  left(src,3) = AreaCode WHERE (isnull(Calification)or Calification='') 
AND TIME(DATE_SUB(NOW(),INTERVAL DiffLocal HOUR)) BETWEEN '$va{'hf'}' AND '$va{'ht'}' ";
		}

		&Do_mSQL("START TRANSACTION;
				SELECT \@A:=src FROM sl_cdr $query ORDER BY calldate $va{'o'} LIMIT 1;
				UPDATE sl_cdr set ID_admin_users=$usr{'id_admin_users'},Calification='int-assigned' WHERE (isnull(Calification)or Calification='') AND src=\@A;
				COMMIT;");
		#query sencillo
		$sth=&Do_SQL("SELECT cdr_id,src,Calification,didmx,calldate,accountcode
						FROM sl_cdr 
						WHERE Calification='int-assigned' AND ID_admin_users=$usr{'id_admin_users'} ORDER BY calldate  $va{'o'} LIMIT 1 ");
	}
	if($sth->rows!=1){
		#no hay numeros por asignar
		$va{'phone_number'}='None';
		$va{'other_info'}="<tr>
					<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
	}else{
		my $rec=$sth->fetchrow_hashref;
		#Verifica que lo haya escrito, sino marca error de asignacion
		$id_admin_users=&load_name('sl_cdr','cdr_id',$rec->{'cdr_id'},'id_admin_users');
		if($usr{'id_admin_users'}==$id_admin_users){
			$va{'phone_number'}=substr($rec->{'src'},0,3)."-". substr($rec->{'src'},3,3)."-".substr($rec->{'src'},6);
			$va{'calldate'}=$rec->{'calldate'};
			$va{'accountcode'}=$rec->{'accountcode'};
			$va{'cdr_id'}=$rec->{'cdr_id'};
			$va{'calification'}='int-assigned';
			$va{'didmx'}=$rec->{'didmx'};
			$va{'src'}=$rec->{'src'};

			## Creamos la variable para cargar en el link del header
			if ($in{'id_customers'}){
				$va{'extracfg'}	= "&step=2&id_customers=$in{'id_customers'}&cid=$rec->{'src'}&did=$rec->{'didmx'}&dids7=$rec->{'accountcode'}&updates7=1";
			}else{
				$va{'extracfg'}	= "&step=1&action=1&cid=$rec->{'src'}&did=$rec->{'didmx'}&dids7=$rec->{'accountcode'}&updates7=1";
			}
			
			### num de veces que llamo
			$sth1=&Do_SQL("SELECT COUNT(*) FROM sl_cdr WHERE src='$rec->{'src'}' AND Calification='int-assigned'");
			$va{'numcalls'} = $sth1->fetchrow();
			
			### Hace cuanto fue la llamada
			$sth1=&Do_SQL("SELECT TIMEDIFF(NOW(),'$va{'calldate'}')");
			$va{'timedif'} = $sth1->fetchrow();
			
			### cargar Time zone y hora local basado en
			$sth1=&Do_SQL("SELECT TIME(DATE_SUB(NOW(),INTERVAL (SELECT timezone-5  FROM `sl_zipcodes` WHERE `AreaCode` LIKE '".substr($rec->{'src'},0,3)."' LIMIT 1) HOUR))");
			$va{'localtime'} = $sth1->fetchrow();
			
			### Cargar Producto y num 800
			if($cfg{'product_assign'}==1)
			{
				$sth1=&Do_SQL("SELECT num800,product_assign as product  FROM `sl_numbers` inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers WHERE didmx ='$va{'didmx'}'");
			}
			else
			{
				$sth1=&Do_SQL("SELECT num800,product  FROM `sl_numbers` WHERE didmx ='$va{'didmx'}'");
			}
			($va{'num800'},$va{'product'}) = $sth1->fetchrow_array();
			if ($rec->{'src'}>0){
				#query de info
				$sth1=&Do_SQL("SELECT orders.ID_orders,Phone1,Phone2,Cellphone,CID,sl_customers.ID_customers,sl_customers.Firstname, sl_customers.Lastname1, sl_customers.Lastname2
		from sl_customers
		inner join (Select ID_orders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet,'orders'as ordertype
		            from sl_orders
								where Status not in('Cancelled','Void','System Error')
		            )as orders on(sl_customers.ID_customers=orders.ID_customers)
		where (right('$rec->{'src'}',8)=right(Phone1,8) or right('$rec->{'src'}',8)=right(Phone2,8) or right('$rec->{'src'}',8)=right(Cellphone,8) or right('$rec->{'src'}',8)=right(CID,8))
		group by ID_orders");
				if ($sth1->rows>0){
					$va{'other_info'}="";
					while(my $rec1=$sth1->fetchrow_hashref){
						#Muestra la informacion adicional
						$va{'other_info'}.="<tr>
						<td><input type='radio' class='radio' name='id_customers' value='$rec1->{'ID_customers'}'> $rec1->{'ID_orders'}</td>
						<td>$rec1->{'Firstname'} $rec1->{'Lastname1'} $rec1->{'Lastname2'}</td>
						</tr>";
					}
				}else{
					$va{'other_info'}.="<tr>
						<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
				}
			}else{
				$va{'other_info'}.="<tr>
						<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}
			## Buscamos llamadas del mismo src
			my ($sth2) = &Do_SQL("SELECT * FROM sl_cdr WHERE src='$rec->{'src'}' AND  Calification IS NOT NULL AND Calification NOT IN('int-assigned','') ");
			if($sth2->rows()>0){
			    while (my $rec2 = $sth2->fetchrow_hashref()){
				$va{'ocalls_info'}.="<tr>
						      <td align='left'>$rec2->{'calldate'}</td>
						      <td align='left'>&nbsp;&nbsp;&nbsp;".&load_name('admin_users','id_admin_users',$rec2->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")."</td>
						      <td align='left'>$rec2->{'Calification'}</td>
						    </tr>";
			    }
			}else{
			    $va{'ocalls_info'}.="<tr>
						  <td colspan='3' align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}
			## Buscamos notas del mismo src
			my ($sth3) = &Do_SQL("SELECT Date,Notes,ID_admin_users FROM sl_cdr_notes WHERE src='$rec->{'src'}'");
			if($sth3->rows()>0){
			    while (my($date,$note,$id_admin_users) = $sth3->fetchrow()){
				$va{'notes_info'}.="<tr>
						      <td align='left'>$date</td>
						      <td align='left'>&nbsp;&nbsp;&nbsp;".&load_name('admin_users','id_admin_users',$id_admin_users,"CONCAT(FirstName,' ',LastName)")."</td>
						      <td align='left'>$note</td>
						    </tr>";
			    }
			}else{
			    $va{'notes_info'}.="<tr>
						  <td colspan='3' align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}

		}else{
			&cgierr("Error al asignar");#Error al asignar
		}
		#Texto para asignar calificacion
	}
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('flashcalls.html');

}
	
sub flashcalls_out{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 19 Feb 2010 16:53:29
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified By RB on 3/1/10 6:17 PM : Se agrega variable para link del header
#Last modified on 13 Oct 2010 16:29:59
#Last modified by: MCC C. Gabriel Varela S. :Se hace inner de numbers con numbers_assign


	## Cargar Datos de  de sl_vars
	my ($sth) = &Do_SQL("SELECT VValue,Subcode FROM sl_vars WHERE VName = 'Setup Calls Super' ");
	if($sth->rows() > 0){
	    while (my($value,$code) = $sth->fetchrow()){
		$va{$code} = $value;
	    }
	}
	
	if($in{'action'}==1){
		$err=0;
 		#valida la calificacion
 		if (!$in{'calification'} or !$in{'notes'}){
		    if(!$in{'calification'}){
 			$err++;
 			$error{'calification'} = &trans_txt('required');
		    }
		    if ($in{'calification'} ne 'int-answered' and !$in{'notes'}){
			$err++;
 			$error{'notes'} = &trans_txt('required');
		    }
		}
		
		if(!$err){
 			#&cgierr("UPDATE sl_cdr SET Calification='$in{'calification'}' WHERE ID_admin_users=$usr{'id_admin_users'}");
			#Hace redireccion si elige "No calificar"

			my ($tmp_sth) = &Do_SQL("SELECT src FROM sl_cdr WHERE ID_admin_users=$usr{'id_admin_users'} AND Calification='int-assigned-out' LIMIT 1");
			my ($tmp_src) = $tmp_sth->fetchrow_array();

			($in{'calification'} ne 'int-answered') and (&Do_SQL("INSERT INTO sl_cdr_notes VALUES(0,'$tmp_src','".&filter_values($in{'notes'})."','Low',CURDATE(),CURTIME(),$usr{'id_admin_users'} )"));

			#Unavailable customer?
			my $cdr_calif = &load_name('sl_vars','Subcode','c','VValue');
			#&cgierr("Calificacion:$cdr_calif  - Calif Actual: $in{'calification'}");
			if($cdr_calif ne '' and $in{'calification'} eq 'Inubicable'){
			    &Do_SQL("UPDATE sl_cdr SET Calification='$in{'calification'}' WHERE src='$in{'cid'}' AND Calification IN ('int-assigned-out','$cdr_calif')");
			}elsif($in{'calification'} eq 'int-answered'){
			    &Do_SQL("UPDATE sl_cdr SET Calification='$va{'c'}' WHERE ID_admin_users=$usr{'id_admin_users'} AND Calification='int-assigned-out' ");
			}else{
			    &Do_SQL("UPDATE sl_cdr SET Calification='$in{'calification'}' WHERE ID_admin_users=$usr{'id_admin_users'} AND Calification='int-assigned-out' ");
			}

			if ($in{'calification'} eq 'int-answered'){
				#Actualiza
				if ($in{'id_customers'}){
					print "Location:/cgi-bin/mod/sales/admin?cmd=console_order&step=2&id_customers=$in{'id_customers'}&cid=$in{'cid'}&did=$in{'didmx'}&dids7=$in{'dids7'}&updates7=1\n\n";
				}else{
					print "Location:/cgi-bin/mod/sales/admin?cmd=console_order&step=1&action=1&cid=$in{'cid'}&did=$in{'didmx'}&dids7=$in{'dids7'}&updates7=1\n\n";
				}
				return;
			}elsif ($in{'lastcall'}){
				&html_base_home('home.html');
				return;
			}
		  delete($in{'notes'});
		  delete($in{'calification'});
 		}
	}

	$va{'o'} = 'DESC';
	my $query=" WHERE (isnull(Calification) or Calification='') ";
	my $got_cal=0;

	if($va{'hf'}){
	    $query = " INNER JOIN
			(SELECT AreaCode,Timezone-5 AS DiffLocal FROM sl_zipcodes GROUP BY AreaCode)as tmp
			ON  left(src,3) = AreaCode WHERE TIME(DATE_SUB(NOW(),INTERVAL DiffLocal HOUR)) BETWEEN '$va{'hf'}' AND '$va{'ht'}' ";
	}
	if($va{'c'} and $va{'c'} ne ''){
	    $query .= " AND  Calification='$va{'c'}' ";
	    $got_cal=1;
	}

	#&cgierr("SELECT \@A:=src FROM sl_cdr $query ORDER BY calldate $va{'o'}  LIMIT 1;");
	&Do_mSQL("START TRANSACTION;
			SELECT \@A:=src FROM sl_cdr $query ORDER BY calldate $va{'o'}  LIMIT 1;
			UPDATE sl_cdr set ID_admin_users=$usr{'id_admin_users'},Calification='int-assigned-out'  WHERE src=\@A AND IF($got_cal > 0 != '',Calification='$va{'c'}',(isnull(Calification) or Calification='')) ORDER BY calldate $va{'o'}  LIMIT 1;
			COMMIT;");
	#&cgierr("UPDATE sl_cdr set ID_admin_users=$usr{'id_admin_users'},Calification='int-assigned-out'  WHERE src=\@A AND IF($got_cal > 0 != '',Calification='$va{'c'}',(isnull(Calification) or Calification='')) ORDER BY calldate $va{'o'}  LIMIT 1");
	#query sencillo 
	$sth=&Do_SQL("SELECT cdr_id,src,Calification,didmx,calldate,accountcode
		      FROM sl_cdr 
		      WHERE Calification='int-assigned-out' AND ID_admin_users=$usr{'id_admin_users'} ORDER BY calldate  $va{'o'} LIMIT 1 ");

	
	if($sth->rows!=1){
		#no hay numeros por asignar
		$va{'phone_number'}='None';
		$va{'other_info'}="<tr>
					<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
	}else{
		my $rec=$sth->fetchrow_hashref;
		#Verifica que lo haya escrito, sino marca error de asignacion
		$id_admin_users=&load_name('sl_cdr','cdr_id',$rec->{'cdr_id'},'id_admin_users');
		if($usr{'id_admin_users'}==$id_admin_users){
			$va{'phone_number'}=substr($rec->{'src'},0,3)."-". substr($rec->{'src'},3,3)."-".substr($rec->{'src'},6);
			$va{'calldate'}=$rec->{'calldate'};
			$va{'accountcode'}=$rec->{'accountcode'};
			$va{'cdr_id'}=$rec->{'cdr_id'};
			$va{'calification'}='int-assigned';
			$va{'didmx'}=$rec->{'didmx'};
			$va{'src'}=$rec->{'src'};

			## Creamos la variable para cargar en el link del header
			if ($in{'id_customers'}){
				$va{'extracfg'}	= "&step=2&id_customers=$in{'id_customers'}&cid=$rec->{'src'}&did=$rec->{'didmx'}&dids7=$rec->{'accountcode'}&updates7=1";
			}else{
				$va{'extracfg'}	= "&step=1&action=1&cid=$rec->{'src'}&did=$rec->{'didmx'}&dids7=$rec->{'accountcode'}&updates7=1";
			}
			
			### num de veces que llamo
			$sth1=&Do_SQL("SELECT COUNT(*) FROM sl_cdr WHERE src='$rec->{'src'}' AND Calification='int-assigned'");
			$va{'numcalls'} = $sth1->fetchrow();
			
			### Hace cuanto fue la llamada
			$sth1=&Do_SQL("SELECT TIMEDIFF(NOW(),'$va{'calldate'}')");
			$va{'timedif'} = $sth1->fetchrow();
			
			### cargar Time zone y hora local basado en
			$sth1=&Do_SQL("SELECT TIME(DATE_SUB(NOW(),INTERVAL (SELECT timezone-5  FROM `sl_zipcodes` WHERE `AreaCode` LIKE '".substr($rec->{'src'},0,3)."' LIMIT 1) HOUR))");
			$va{'localtime'} = $sth1->fetchrow();
			
			### Cargar Producto y num 800
			if($cfg{'product_assign'}==1)
			{
				$sth1=&Do_SQL("SELECT num800,product_assign as product  FROM `sl_numbers` inner join sl_numbers_assign on sl_numbers.ID_numbers=sl_numbers_assign.ID_numbers WHERE didmx ='$va{'didmx'}'");
			}
			else
			{
				$sth1=&Do_SQL("SELECT num800,product  FROM `sl_numbers` WHERE didmx ='$va{'didmx'}'");
			}
			($va{'num800'},$va{'product'}) = $sth1->fetchrow_array();
			if ($rec->{'src'}>0){
				#query de info
				$sth1=&Do_SQL("SELECT orders.ID_orders,Phone1,Phone2,Cellphone,CID,sl_customers.ID_customers,sl_customers.Firstname, sl_customers.Lastname1, sl_customers.Lastname2
		from sl_customers
		inner join (Select ID_orders,ID_customers,City,State, Zip,Country,shp_City,shp_State,shp_Zip,shp_Country,Status,Date as Dateo,Time as Timeo,OrderQty,OrderShp,OrderDisc,OrderTax,OrderNet,'orders'as ordertype
		            from sl_orders
								where Status not in('Cancelled','Void','System Error')
					)as orders on(sl_customers.ID_customers=orders.ID_customers)
		where (right('$rec->{'src'}',8)=right(Phone1,8) or right('$rec->{'src'}',8)=right(Phone2,8) or right('$rec->{'src'}',8)=right(Cellphone,8) or right('$rec->{'src'}',8)=right(CID,8))
		group by ID_orders");
				if ($sth1->rows>0){
					$va{'other_info'}="";
					while(my $rec1=$sth1->fetchrow_hashref){
						#Muestra la informacion adicional
						$va{'other_info'}.="<tr>
						<td><input type='radio' class='radio' name='id_customers' value='$rec1->{'ID_customers'}'> $rec1->{'ID_orders'}</td>
						<td>$rec1->{'Firstname'} $rec1->{'Lastname1'} $rec1->{'Lastname2'}</td>
						</tr>";
					}
				}else{
					$va{'other_info'}.="<tr>
						<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
				}
			}else{
				$va{'other_info'}.="<tr>
						<td colspan=2 align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}
			## Buscamos llamadas del mismo src
			my ($sth2) = &Do_SQL("SELECT * FROM sl_cdr WHERE src='$rec->{'src'}' AND  Calification IS NOT NULL AND Calification NOT IN('int-assigned','') ");
			if($sth2->rows()>0){
			    while (my $rec2 = $sth2->fetchrow_hashref()){
				$va{'ocalls_info'}.="<tr>
						      <td align='left'>$rec2->{'calldate'}</td>
						      <td align='left'>&nbsp;&nbsp;&nbsp;".&load_name('admin_users','id_admin_users',$rec2->{'ID_admin_users'},"CONCAT(FirstName,' ',LastName)")."</td>
						      <td align='left'>$rec2->{'Calification'}</td>
						    </tr>";
			    }
			}else{
			    $va{'ocalls_info'}.="<tr>
						  <td colspan='3' align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}
			## Buscamos notas del mismo src
			my ($sth3) = &Do_SQL("SELECT Date,Notes,ID_admin_users FROM sl_cdr_notes WHERE src='$rec->{'src'}'");
			if($sth3->rows()>0){
			    while (my($date,$note,$id_admin_users) = $sth3->fetchrow()){
				$va{'notes_info'}.="<tr>
						      <td align='left'>$date</td>
						      <td align='left'>&nbsp;&nbsp;&nbsp;".&load_name('admin_users','id_admin_users',$id_admin_users,"CONCAT(FirstName,' ',LastName)")."</td>
						      <td align='left'>$note</td>
						    </tr>";
			    }
			}else{
			    $va{'notes_info'}.="<tr>
						  <td colspan='3' align='center'>".trans_txt('search_nomatches')."</td></tr>";
			}

			my $maxtries = &load_name('sl_vars','Subcode','m','VValue');
			if($maxtries > 0 and $sth3->rows() >= $maxtries and &load_name('sl_vars','Subcode','c','VValue') ne ''){
			    $va{'set_unavailable'} = qq|<input type="radio" class="radio" name="calification" value="Inubicable"><span class="stdtxterr">No contestada - Inubicable</span><br>|;
			}
		}else{
			&cgierr("Error al asignar");#Error al asignar
		}
		#Texto para asignar calificacion
	}

	my $scal = &load_name('sl_vars','Subcode','c','VValue');
	$va{'scal'} = qq|<tr>
			    <td valign="top">Calificaci&oacute;n:</td><td><strong>$scal</strong></td>
			 </tr>|;

	$va{'cdr_notes'} = qq|<tr>
			    <td colspan="2" align="left">	
			    <br><b>Notas :</b> <span class="smallfieldterr">[er_notes]</span><br>
				<textarea name="notes" style="width: 80%" cols="50" rows="3" onFocus='focusOn( this )' onBlur='focusOff( this )'>[in_notes]</textarea>
				<br>
			    </td>
			</tr>|;

	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('flashcalls.html');

}


sub eco_orders{
# --------------------------------------------------------
# Forms Involved:
# Created on: 25 Aug 2010 17:32:37
# Author: MCC C. Gabriel Varela S.
# Description :
# Parameters :
# Last Time Modified By RB on 31/08/2010 : Se agrega Ptype a la orden y captura de pago si es TDC
# Last Time Modified By RB on 03/1/2011 : Se agrega language para el envio de correo de confirmacion y escaneo
#Last modified on 3/25/11 9:56 AM
#Last modified by: MCC C. Gabriel Varela S. : Se cambia 4122 por 4688
# Last Modified by RB on 04/15/2011 12:39:42 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:29:24 PM : Se agrega City como parametro para calculate_taxes
#Last modified on 14 Jun 2011 18:10:33
#Last modified by: MCC C. Gabriel Varela S. : Se evalúa si crea cliente o no
# Last time Modified By RB on 10/07/2011: Se agrega Amazon

	my ($x,$err,$query);

	if($in{'id_customers'}ne'' and !$in{'action'})
	{
		my $sth=&Do_SQL("Select *
		from sl_customers
		where ID_customers='$in{'id_customers'}'
		limit 1");
		$rec=$sth->fetchrow_hashref;
		$in{'firstname'}=$rec->{'FirstName'};
		$in{'lastname1'}=$rec->{'LastName1'};
		$in{'lastname2'}=$rec->{'LastName2'};
		$in{'sex'}=$rec->{'Sex'};
		$in{'phone1'}=$rec->{'Phone1'};
		$in{'address1'}=$rec->{'Address1'};
		$in{'address2'}=$rec->{'Address2'};
		$in{'address3'}=$rec->{'Address3'};
		$in{'urbanization'}=$rec->{'Urbanization'};
		$in{'contact_mode'}=$rec->{'contact_mode'};
		$in{'city'}=$rec->{'City'};
		$in{'state'}=$rec->{'State'};
		$in{'zip'}=$rec->{'Zip'};
		$in{'email'}=$rec->{'Email'};
		print "Content-type: text/html\n\n";
		print &build_page('eco_orders_with_customer.html');
		return;
	}
	if($in{'action'})
	{
		#Valida los datos para la creación de cliente
		$err = &validate_eco_orders();
		&load_cfg('sl_customers');
		($x,$query) = &validate_cols('1');

		if(!$in{'id_admin_users'}){
			$error{'id_admin_users'}=&trans_txt('required');
			$err++;
		}

		$err += $x;
		if ($err==0)
		{
			#Inserta cliente
			if(!$in{'id_customers'})
			{
				$sth=&Do_SQL("Insert into sl_customers
				set FirstName='$in{'firstname'}',
				LastName1='$in{'lastname1'}',
				LastName2='$in{'lastname2'}',
				Sex='$in{'sex'}',
				Phone1='$in{'phone1'}',
				Cellphone='$in{'cellphone'}',
				Email='$in{'email'}',
				Address1='$in{'address1'}',
				Address2='$in{'address2'}',
				Address3='$in{'address3'}',
				urbanization='$in{'urbanization'}',
				contact_mode='$in{'contact_mode'}',
				City='$in{'city'}',
				State='$in{'state'}',
				Zip='$in{'zip'}',
				Country='UNITED STATES',
				Status='Active',
				Type='Retail',
				Date=curdate(),
				Time=curtime(),
				ID_admin_users='$in{'id_admin_users'}'");
				$lastid_cus = $sth->{'mysql_insertid'};
			
			}else{
				$lastid_cus=$in{'id_customers'};
			}

			$orderqty=0;
			for my $i(1..6){
				if($in{"id_products$i"}){
					$orderqty++;
				}
			}

			$ordertax=&calculate_taxes($in{'zip'},$in{'state'},$in{'city'},0);
			$ordershp=0;
			
			for my $i(1..6){
				if($in{"shipping$i"}){
					$ordershp+=$in{"shipping$i"};
				}
			}

			$ordernet=0;
			
			for my $i(1..6){
				if($in{"sprice$i"}){
					$ordernet+=$in{"sprice$i"};
				}
			}
			
			#Language
			$in{'language'}='spanish' if !$in{'language'};
			
			#Inserta la orden
			$sth=&Do_SQL("Insert into sl_orders set ID_customers=$lastid_cus,Address1='$in{'address1'}',Address2='$in{'address2'}',Address3='$in{'address3'}',urbanization='$in{'urbanization'}',City='$in{'city'}',State='$in{'state'}',Zip='$in{'zip'}',Country='UNITED STATES',shp_type=1,shp_Address1='$in{'address1'}',shp_Address2='$in{'address2'}',shp_Address3='$in{'address3'}',shp_urbanization='$in{'urbanization'}',shp_City='$in{'city'}',shp_State='$in{'state'}',shp_Zip='$in{'zip'}',shp_Country='UNITED STATES',StatusPrd='None',StatusPay='None',OrderTax='$ordertax',OrderQty='$orderqty',OrderShp='$ordershp',OrderNet='$ordernet',Ptype=IF('$in{'type'}' = 'COD','COD','Credit-Card'),language='$in{'language'}',Status=IF('$in{'type'}' != 'Credit-Card','Processed','Void'),Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			$lastid_ord = $sth->{'mysql_insertid'};

			
			&add_order_notes_by_type($lastid_ord,"Order Created","Web Creator");
			#Inserta los productos
			#&cgierr("Productos");
			for my $i(1..6){
				if($in{"id_products$i"}){
					#calcular el tax aquí.
					$tax=$in{"sprice$i"}*$ordertax;
					$sth=&Do_SQL("Insert into sl_orders_products set ID_products='".$in{"id_products$i"}."',ID_orders='$lastid_ord',Quantity=1,SalePrice='".$in{"sprice$i"}."',Shipping='".$in{"shipping$i"}."',Tax='$tax',Discount=0,Status='Active',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
				}else{
					#&cgierr("$i:fdfdfd".$in{'id_products1'});
				}
			}
			#Inserta los payments
			if($in{'type'}eq'Credit-Card'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='$in{'type'}',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'pmtfield3'}',PmtField4='$in{'pmtfield4'}',PmtField5='$in{'pmtfield5'}',PmtField6='$in{'pmtfield6'}',PmtField7='CreditCard',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$usr{'id_admin_users'}'");
			}elsif($in{'type'} =~ /PayPal|Google|Amazon/){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='Credit-Card',PmtField1='Visa',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='$in{'type'}',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),AuthCode='$in{'authcode'}',Captured='Yes',CapDate=CURDATE(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}elsif($in{'type'}eq'COD'){
				$sth=&Do_SQL("Insert into sl_orders_payments set ID_orders='$lastid_ord',Type='COD',PmtField1='$in{'pmtfield1'}',PmtField2='".$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'}."',Pmtfield3='',Amount='$in{'amount'}',Reason='Sale',Paymentdate=curdate(),Status='Approved',Date=curdate(),Time=curtime(),ID_admin_users='$in{'id_admin_users'}'");
			}
			$lastid_payment = $sth->{'mysql_insertid'};
			
			my ($status,$statmsg,$codemsg,@params);
			if ($in{'type'} ne 'Credit-Card'){

				## Movimientos Contables
				my ($order_type, $ctype, $ptype,@params);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$lastid_ord';");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = get_deposit_type($lastid_payment,'');
				@params = ($lastid_ord,$lastid_payment, 1);
				&accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params );

				$status='OK';

			}else{

				if(!$va{'from_run_daily'} == 1){
					require ("../../common/apps/cybersubs.cgi");
				}
				($status,$statmsg,$codemsg) = &sltvcyb_auth($lastid_ord,$lastid_payment);
				
			}

			if($status =~ /^ok/i){
				$va{'message'}= &trans_txt('payments_authorized');
			}else{
				$va{'message'}= $statmsg;
			}

			$script_url =~ s/admin$/dbman/;
			$va{'message'}= &trans_txt('orders_added') . ": ID <a href=\"$script_url?cmd=orders&view=$lastid_ord\">$lastid_ord</a>, Customer ID <a href=\"$script_url?cmd=opr_customers&view=$lastid_cus\">$lastid_cus</a><br>$va{'message'}";

			foreach my $key (keys %in){
				delete($in{$key});
			}
			$in{'cmd'}='eco_orders';

			if($va{'from_run_daily'} == 1){
				return $lastid_ord;
			}


		}else{
			if($va{'from_run_daily'} == 1){
				return -1;
			}
			#&cgierr("Errors:$err,$x,$#error");
		}

	}
	print "Content-type: text/html\n\n";
	print &build_page('eco_orders.html');

}


sub validate_eco_orders{
# --------------------------------------------------------
# Forms Involved:
# Created on: 25 Aug 2010 18:32:09
# Author: MCC C. Gabriel Varela S.
# Description :
# Parameters :

	my $err=0;

	$in{'id_products1'} = '100'.$in{'id_products1'} if length($in{'id_products1'})==6;
	$in{'id_products2'} = '100'.$in{'id_products2'} if length($in{'id_products2'})==6;
	$in{'id_products3'} = '100'.$in{'id_products3'} if length($in{'id_products3'})==6;
	$in{'id_products4'} = '100'.$in{'id_products4'} if length($in{'id_products4'})==6;
	$in{'id_products5'} = '100'.$in{'id_products5'} if length($in{'id_products5'})==6;
	$in{'id_products6'} = '100'.$in{'id_products6'} if length($in{'id_products6'})==6;

	$in{'pmtfield4'}=$in{'expdate'};
	$in{'pmtfield2'}=$in{'firstname'}.' '.$in{'lastname1'}.' '.$in{'lastname2'};
	if (!$in{'address1'}){
		$error{'address1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'city'}){
		$error{'city'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'state'}){
		$error{'state'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'zip'}){
		$error{'zip'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'email'}){
		#$error{'email'} = &trans_txt('required');
		#++$err;
	}
	if (!$in{'id_products1'}){
		$error{'id_products1'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'sprice1'}){
		$error{'sprice1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'shipping1'}eq''){
		$error{'shipping1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq''){
		$error{'type'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield1'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield1'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield2'}eq''){
		$error{'pmtfield2'} = &trans_txt('required');
		++$err;
	}
	if ($in{'pmtfield3'}eq'' and $in{'type'}eq'Credit-Card'){
		$error{'pmtfield3'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'expdate'}){
		$error{'pmtfield4'} = &trans_txt('required');
		++$err;
	}
	if ($in{'type'}eq'Credit-Card' and !$in{'pmtfield5'}){
		$error{'pmtfield5'} = &trans_txt('required');
		++$err;
	}
	if (!$in{'amount'}){
		$error{'amount'} = &trans_txt('required');
		++$err;
	}

	if($in{'id_products1'} and length($in{'id_products1'})<9){
		$error{'id_products1'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products2'} and length($in{'id_products2'})<9){
		$error{'id_products2'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products5'} and length($in{'id_products5'})<9){
		$error{'id_products5'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products3'} and length($in{'id_products3'})<9){
		$error{'id_products3'} = &trans_txt('invalid');
		++$err;
	}
	if($in{'id_products4'} and length($in{'id_products4'})<9){
		$error{'id_products4'} = &trans_txt('invalid');
		++$err;
	}

	if($in{'id_products2'} and $in{'sprice2'}eq''){
		$error{'sprice2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products2'} and $in{'shipping2'}eq''){
		$error{'shipping2'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'sprice3'}eq''){
		$error{'sprice3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products3'} and $in{'shipping3'}eq''){
		$error{'shipping3'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'sprice4'}eq''){
		$error{'sprice4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products4'} and $in{'shipping4'}eq''){
		$error{'shipping4'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'sprice5'}eq''){
		$error{'sprice5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products5'} and $in{'shipping5'}eq''){
		$error{'shipping5'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'sprice6'}eq''){
		$error{'sprice6'} = &trans_txt('required');
		++$err;
	}
	if($in{'id_products6'} and $in{'shipping6'}eq''){
		$error{'shipping6'} = &trans_txt('required');
		++$err;
	}

	return $err;
}

#########################################################################################
#########################################################################################
#   Function: sales_channels_selector
#
#       Es: Función encargada de generar/controlar la barra de avance en la consola del modulo sales.
#
#       En: Function responsible for generating / controlling the progress bar in the module console sales.
#
#
#   Created on: 12/05/2016
#
#   Author: Ing Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the HTML with links constructed
#
#   See Also:
#
#      ---
#
sub sales_channels_selector{
#########################################################################################
#########################################################################################
	print "Content-type: text/html\n\n";
	print &build_page('sales_channels.html');
}	

1;