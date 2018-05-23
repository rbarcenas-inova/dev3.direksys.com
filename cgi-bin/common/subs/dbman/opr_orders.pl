##########################################################
##		OPERATIONS : ORDERS
##########################################################
sub del_opr_orders {
# --------------------------------------------------------
# Last Modification by JRG : 06/11/2009 : Se agrega log
	my ($sth) = &Do_SQL("DELETE FROM sl_orders_logs WHERE ID_orders='$in{'delete'}';");
	&auth_logging('opr_orders_logsdel',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$in{'delete'}';");
	&auth_logging('opr_orders_paydroped',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_orders_notes WHERE ID_orders='$in{'delete'}';");
	&auth_logging('opr_orders_notesdel',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_orders_plogs WHERE ID_orders='$in{'delete'}';");
	&auth_logging('opr_orders_plogsdel',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_orders_products WHERE ID_orders='$in{'delete'}';");
	&auth_logging('opr_orders_prodsdel',$in{'delete'});

}

#############################################################################
#############################################################################
#   Function: advsearch_opr_orders
#
#       Es: Contruye Busqueda avanzada de ordenes
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
# Last Modified on: 01/12/09 13:25:18
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para poder buscar en el campo shp_name cuando se introduce un nombre o un apellido
# Last Modified on: 02/04/09 09:29:02
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para que se pueda ir a pánas posteriores cuando se selecciona máde un status de búda en ónes.
# Last Modified on: 03/30/09 17:21:56
# Last Modified by: MCC C. Gabriel Varela S: Se habilita búda de ónes derivadas de cancelacióe preónes que tienen todavípagos pendientes de refund.
# Last Modified on: 07/23/09 16:03:36
# Last Modified by: MCC C. Gabriel Varela S: Se habilita búda para ónes con pagos de créto sin capturar.
# Last Modified by RB 08/19/2009 : Se incluyo busqueda por ultimo AVS Response
# Last Modified RB: 09/17/09  11:09:00 -- Se agrego la opcion para buscar por fecha basado en el posteddate de la orden
# Last Time Modified By RB on 2/9/10 5:13 PM : Se agrega filtrado por Order Type
# Last Time Modified By RB on 10/27/2010 11:13 AM :Se agrega filtrado por email
# Last Modified by RB on 04/11/2011 04:33:51 PM : Se agrega busqueda de ordenes COD con filtros por Fecha,Status, Driver (viene del home)
# Last Modified by RB on 06/01/2011 05:03:11 PM : Se corrige problema en fechas de busqueda avanzada con ID_products  
#  TODO : Verificar si la funcion bystatuscontact , es corrrecta o se elimina.
#  
#  
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub advsearch_opr_orders {
#############################################################################
#############################################################################


	my ($query);

	if ($in{'shp_type'}){
		my $shp_type =~ s/\|/','/g;	
		$query .= " AND shp_type IN($shp_type) ";
	}

	# ## Se agrega restriccion basada a Arbol de Agentes, Supervisores y Coordinadores
	# $custom_id_admin_users = &get_call_center_agents_list();

	# #######
	# ####### Add filter to only search this user records
	# #######
	# my $query_only_my_records='';
	my $query_only_my_records = $in{'only_my_records'} ? " AND sl_orders.ID_admin_users = '$usr{'id_admin_users'}' " : '';

	# if ($in{'only_my_records'}){
	# 	$query_only_my_records = " AND sl_orders.ID_admin_users = ".$usr{'id_admin_users'}." ";
	# }elsif($custom_id_admin_users ne ''){
	# 	$query_only_my_records = " AND sl_orders.ID_admin_users IN (".$custom_id_admin_users.") ";
	# }
	
	#####
	##### Se agrega reestriccion para mostrar solo Orders de Canales de Venta que el usuario tenga asignados.
	#####
	$query_only_my_records .= ($in{'only_records_by_salesorigins'} and $in{'only_records_by_salesorigins'} ne '')? " AND sl_orders.ID_salesorigins IN ($in{'only_records_by_salesorigins'}) ":"";

	if ($in{'tracking'}){

		#####
		##### Busqueda por Tracking Number
		#####

		$db_valid_types{'status'} = "function:ordersproducts_list";
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		$query = "sl_orders LEFT JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders LEFT JOIN sl_orders_parts ON sl_orders_parts.ID_orders_products=sl_orders_products.ID_orders_products WHERE (sl_orders_parts.Tracking='".&filter_values($in{'tracking'})."'  AND sl_orders_products.Status='Active') ";
		$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC ";

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status",$query,'sl_orders.ID_orders',@db_cols);

	}elsif($in{'type'} eq 'cod' and $in{'todo'}){

		#####
		##### Busqueda por COD con datos especiales
		#####

		my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
		
		if ($in{'todo'} eq 'withoutcontacted'){

			#####
			##### No contactados
			#####

			$sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
				FROM (SELECT sl_orders.ID_orders,count(ID_orders_notes)as NNotes
				      FROM sl_orders
				      LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
				      WHERE sl_orders.shp_type=$cfg{'codshptype'}
							and Ptype!='Credit-Card'
				      GROUP BY sl_orders.ID_orders
				      HAVING NNotes=0)as tmp
				GROUP BY NNotes");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');

		}elsif ($in{'todo'} eq 'alreadyconfirmed'){

			#####
			##### Confirmados
			#####

			$sth=&Do_SQL("SELECT group_concat(ID_orders separator '|')as id_table
						FROM (SELECT sl_orders.ID_orders,count(ID_orders_notes)as NNotes
						      FROM sl_orders
						      LEFT JOIN sl_orders_notes ON(sl_orders_notes.ID_orders = sl_orders.ID_orders)
						      WHERE sl_orders.shp_type=$cfg{'codshptype'}
									and Ptype!='Credit-Card'
						      GROUP BY sl_orders.ID_orders
						      HAVING NNotes!=0)as tmp
						GROUP BY NNotes");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');


		}elsif ($in{'todo'} eq 'bystatuscontact'){

			#####
			##### Status del Contacto
			#####

			$in{'id_warehouses'} = 0 if !$in{'id_warehouses'};
			$in{'sx'}=1;
			#$in{'id_table'}=sprintf("%s",&cod_by_status_contact($in{'status'},$in{'contact'},$in{'results'},$in{'id_warehouses'}));
			#delete($in{'id_warehouses'});
			delete($in{'todo'});
			$in{'search'}= 'Search';
			$in{'status'}='Processed' if($in{'status'}=~/^Processed/);
			return &query('sl_orders');
			
		}

	}elsif($in{'todo'} eq 'layaway'){

		#####
		##### Busqueda Layaway
		#####

		$in{'sx'}=1;
		$in{'id_orders'}= &build_query_table_layaway(2);
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');

	}elsif($in{'todo'} eq 'mo'){

		#####
		##### Busqueda Money Order
		#####

		$in{'sx'}=1;
		$in{'id_orders'}= &build_query_table_moneyorder(2,$in{'type'},$in{'mod'});
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');

	}elsif($in{'todo'} eq 'cod_advsearch'){

		#####
		##### Busqueda por COD con datos especiales
		#####
		# Last Modified by RB on 04/11/2011 04:33:51 PM : Busca ordenes COD con filtros por Fecha,Status, Driver
	    
	    # From Date
	    if($in{'from_date'}){
	        $query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
	    }
	    
	    # To Date
	    if($in{'to_date'}){
	        $query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
	    }
	    
	    # Driver
	    if($in{'id_warehouses'}){
            $query .= " AND ID_warehouses = '$in{'id_warehouses'}' "; 
        }
	    
	    
	    # In Transit
	    if($in{'status'} eq 'intransit'){
	        $in{'status'} = 'Processed';
	        $inner_join = " INNER JOIN sl_orders_products USE INDEX(ID_orders)
	                        ON sl_orders.ID_orders = sl_orders_products.ID_orders
	                        INNER JOIN sl_orders_parts USE INDEX(ID_orders_products)
	                        ON sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products";               
	    }

	    my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
        $sth = &Do_SQL("SELECT group_concat(DISTINCT sl_orders.ID_orders separator '|') FROM sl_orders $inner_join WHERE sl_orders.Status = '$in{'status'}' $query ;");
        
        $in{'sx'}=1;
		$in{'id_orders'}=$sth->fetchrow;
		$in{'id_orders'}=-1 if(!$in{'id_orders'});
		return &query('sl_orders');          
	
	}
	

	if($in{'type'}eq'directlink'){

		#####
		##### Busqueda desde un Link Especial en Tab Orders
		#####


		if($in{'todo'}eq'orders_with_credits_payable'){

			my ($sth) = &Do_SQL("SET group_concat_max_len = 204800;");
			$sth=&Do_SQL("Select group_concat(ID_orders separator '|') from
			(
			SELECT sl_orders_payments.ID_orders,
			sum(if(Amount>0 and Captured='Yes' and Capdate!='0000-00-00' and Capdate!='' and not isnull(Capdate) and sl_orders_payments.Status='Approved',1,0))as capturedPos, 
			sum(if(Amount<0 and Captured='Yes' and Capdate!='0000-00-00' and Capdate!='' and not isnull(Capdate) and sl_orders_payments.Status in('Approved','Credit'),1,0))as capturedNeg,
			sum(if(Amount>0 and Captured='No' and (Capdate='0000-00-00' or isnull(Capdate)) and sl_orders_payments.Status='Approved',1,0))as tocapturedPos,
			sum(if(Amount<0 and Captured='No' and (Capdate='0000-00-00' or isnull(Capdate)) and sl_orders_payments.Status in('Approved','Credit'),1,0))as tocapturedNeg
			FROM sl_orders_payments
			INNER JOIN sl_orders ON(sl_orders_payments.ID_orders =sl_orders.ID_orders )
			WHERE sl_orders.Status not in('Cancelled', 'Void', 'System Error')
			/*and Type='Credit-Card'*/
			GROUP BY sl_orders_payments.ID_orders
			HAVING tocapturedNeg >0 
			)as tmp");
			$in{'sx'}=1;
			$in{'id_orders'}=$sth->fetchrow;
			$in{'id_orders'}=-1 if(!$in{'id_orders'});
			return &query('sl_orders');
		}

	}elsif ($in{'id_products'}){

		#####
		##### Busqueda por ID de Producto
		#####

		#delete($in{'from_date'});
		#delete($in{'to_date'});
		$db_valid_types{'status'} = "function:ordersproducts_list";
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		#$in{'id_products'} = int($in{'id_products'});
		
		my ($query);
		if ($in{'status'}){
			my $cadstatus=$in{'status'};
			if ($cadstatus =~ /\|/){
				$cadstatus =~ s/\|/','/g;
				$query = " AND sl_orders.Status IN ('$cadstatus') ";
			}else{
				$query = " AND sl_orders.Status='$cadstatus' ";
			}
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}


		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}else{
			if ($in{'from_date'}){
				$query .= " AND sl_orders.Date>='".&filter_values($in{'from_date'})."' ";
			}
			if ($in{'to_date'}){
				$query .= " AND sl_orders.Date<='".&filter_values($in{'to_date'})."' ";
			}
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter by City
		if ($in{'shp_city'}){
			$query .= " AND sl_orders.shp_City LIKE '%$in{'shp_city'}%' ";
		}

		## Filter by State
		if ($in{'shp_state'}){
			$query .= " AND sl_orders.shp_State = '$in{'shp_state'}' ";
		}

		## Filter by zipcode
		if ($in{'shp_zip'}){
			$query .= " AND sl_orders.shp_Zip = '$in{'shp_zip'}' ";
		}

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;


		if (length($in{'id_products'}) > 6){

			$query = "sl_orders, sl_orders_products WHERE (sl_orders.ID_orders=sl_orders_products.ID_orders AND ID_products='$in{'id_products'}' AND sl_orders_products.Status='Active' $query)";
			$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC";

			return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status",$query,'sl_orders.ID_orders',@db_cols);
		
		}else{

			$query = "sl_orders,sl_orders_products WHERE (sl_orders.ID_orders=sl_orders_products.ID_orders AND RIGHT(ID_products,6)='$in{'id_products'}' AND sl_orders_products.Status='Active' $query)";
			$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC";

			return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status",$query,'sl_orders.ID_orders',@db_cols);

		}


	}elsif($in{'paytbl'}){

		#####
		##### Busqueda por Tabla de Pagos
		#####

		## Crear Query 
		my ($query,@cols,$condtype);
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		
		
		if ($in{'type'}){
			$query .= "AND Type='$in{'type'}'";
		}
		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= " AND sl_orders.Status IN ('$in{'status'}') ";
		}elsif($in{'status'}){
			$query .= " AND sl_orders.Status='$in{'status'}' ";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}') ";
		}elsif($in{'statuspay'}){
			$query .= " AND sl_orders.StatusPay='$in{'statuspay'}' ";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}') ";
		}elsif($in{'statusprd'}){
			$query .= " AND sl_orders.StatusPrd='$in{'statusprd'}' ";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;

		if ($in{'paymentdate'} eq 'due'){
			$query .= "AND (sl_orders_payments.Paymentdate<Curdate() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'today'){
			$query .= "AND (sl_orders_payments.Paymentdate=Curdate() AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'tweek'){
			$query .= "AND (WEEK(sl_orders_payments.Paymentdate)=WEEK(NOW()) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'nweek'){
			$query .= "AND (WEEK(sl_orders_payments.Paymentdate)=(WEEK(NOW())+1) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'tmonth'){
			$query .= "AND (MONTH(sl_orders_payments.Paymentdate)=MONTH(NOW()) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}elsif($in{'paymentdate'} eq 'nmonth'){
			$query .= "AND (MONTH(sl_orders_payments.Paymentdate)=(MONTH(NOW())+1) AND (sl_orders_payments.Status<>'Approved' OR AuthCode='0000') AND Type='Credit-Card')";
		}

		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		$query = " sl_orders,sl_orders_payments WHERE (sl_orders.ID_orders=sl_orders_payments.ID_orders $query)";
		$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC ";

		return &query_sql('DISTINCT(sl_orders.ID_orders),sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status',$query,'sl_orders.ID_orders',@db_cols);

	}elsif($in{'wprod'}){

		#####
		##### Busqueda por producto
		#####

		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= " AND sl_orders.Status IN ('$in{'status'}')";
		}elsif($in{'status'}){
			$query .= "  AND sl_orders.Status='$in{'status'}'";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		if ($in{'dropshipment'}){
			$query .= " AND 1=(Select COUNT(*) FROM sl_products WHERE ID_products=RIGHT(sl_orders_products.ID_products,6) AND DropShipment='Yes') ";
		}

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;
		

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}

		$db_valid_types{'status'} = "function:ordersproducts_list";
		$query = "sl_orders,sl_orders_products WHERE (sl_orders.ID_orders=sl_orders_products.ID_orders $query) ";
		$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC ";

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,sl_orders.shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status",$query,'sl_orders.ID_orders',@db_cols);


	}elsif($in{'wpay'}){

		#####
		##### Busqueda cruzada con tabla de payments
		#####
	
		if ($in{'status'} =~ /\|/){
			$in{'status'} =~ s/\|/','/g;
			$query .= "  AND  sl_orders.Status IN ('$in{'status'}')";
		}elsif($in{'status'}){
			$query .= "  AND  sl_orders.Status='$in{'status'}'";
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND sl_orders.StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND sl_orders.StatusPrd='$in{'statusprd'}'";
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}

		for (1..7){
			if ($in{'pmtfield'.$_}){
				$query .= "  AND  sl_orders_payments.PmtField$_='$in{'pmtfield'.$_}'";
			}
		}


		$db_valid_types{'status'} = "function:orderspayments_list";
		@db_cols = ('ID_orders','Date','ID_customers','StatusPay','StatusPrd','Status');

		$query = " sl_orders,sl_orders_payments WHERE (sl_orders.ID_orders=sl_orders_payments.ID_orders $query) ";
		$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC ";

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status",$query,'sl_orders.ID_orders',@db_cols);
	

	}elsif($in{'firstname'} or $in{'lastname1'} or $in{'lastname2'} or $in{'phone'} or $in{'email'} or $in{'paytype'} or $in{'shp_name'}){

		#####
		##### Busqueda cruzada con customer o tipo de pago
		#####

		my ($query,@cols,$condtype);
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		if ($in{'firstname'}){

			if (index($in{'firstname'}, "(") != -1 || index($in{'firstname'}, ")") != -1) {
				my $err;
				++$err;
			   	$va{'message_error'} = &trans_txt('opr_orders_error_match_against');
			   	return;
			} 

			$in{'firstname'} = &filter_text_match($in{'firstname'});
			$query .=  " ( MATCH(FirstName) AGAINST('*".&filter_values($in{'firstname'})."*' IN BOOLEAN MODE) ) $condtype ";
		}
		if ($in{'lastname1'}){

			if (index($in{'lastname1'}, "(") != -1 || index($in{'lastname1'}, ")") != -1) {
				my $err;
				++$err;
			   	$va{'message_error'} = &trans_txt('opr_orders_error_match_against');
			   	return;
			}

			$in{'lastname1'} = &filter_text_match($in{'lastname1'});
			$query .=  " ( MATCH(LastName1) AGAINST('*".&filter_values($in{'lastname1'})."*' IN BOOLEAN MODE) ) $condtype ";
		}
		if ($in{'lastname2'}){

			if (index($in{'lastname2'}, "(") != -1 || index($in{'lastname2'}, ")") != -1) {
				my $err;
				++$err;
			   	$va{'message_error'} = &trans_txt('opr_orders_error_match_against');
			   	return;
			}
			
			$in{'lastname2'} = &filter_text_match($in{'lastname2'});
			$query .=  " ( MATCH(LastName2) AGAINST('*".&filter_values($in{'lastname2'})."*' IN BOOLEAN MODE) ) $condtype ";
		}
		
		if ($in{'phone'}){
			$query .=  "(CID LIKE '".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Phone1 LIKE '".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Phone2 LIKE '".&filter_values($in{'phone'})."%' OR ";
			$query .=  "Cellphone LIKE '".&filter_values($in{'phone'})."%' OR ";
			$query .=  "CID LIKE '".&filter_values($in{'phone'})."%') $condtype ";
		}
		if ($in{'email'}){
			$query .=  "Email LIKE '%".&filter_values($in{'email'})."%' $condtype ";
		}
		
		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " sl_orders.Ptype IN('$in{'ptype'}') $condtype ";
		}$in{'ptype'} =~ s/','/\|/g;

		if($in{'paytype'}){
			($in{'paytype'} eq 'all') and ($query .= " (SELECT Type FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders LIMIT 0,1) IN ('WesternUnion','Money Order','Layaway','COD') ");
			($in{'paytype'} ne 'all') and ($query .= " (SELECT Type FROM sl_orders_payments WHERE sl_orders_payments.ID_orders=sl_orders.ID_orders LIMIT 0,1)='".$in{'paytype'}."' ");
			$query .= " $condtype ";
		}

		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
			}elsif($in{'from_posteddate'}){
				$query .= " sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
			$query .= " $condtype ";
		}

		## Filter by City
		if ($in{'shp_city'}){
			$query .= " sl_orders.shp_City LIKE '%$in{'shp_city'}%' $condtype ";
		}

		## Filter by State
		if ($in{'shp_state'}){
			$query .= " sl_orders.shp_State = '$in{'shp_state'}' $condtype ";
		}

		## Filter by zipcode
		if ($in{'shp_zip'}){
			$query .= " sl_orders.shp_Zip = '$in{'shp_zip'}' $condtype ";
		}

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;
		
		for my $i(0..$#db_cols){
			($in{lc($db_cols[$i])}) and ($in{'sl_orders.'.lc($db_cols[$i])} = $in{lc($db_cols[$i])});
			($in{lc('from_'.$db_cols[$i])}) and ($in{'from_sl_orders.'.lc($db_cols[$i])} = $in{lc('from_'.$db_cols[$i])});
		}
		my ($query2) = &build_query_str('sl_orders');


		if ($query2 and $query){
			$query = substr($query,0,-4);
			$query = " 1 AND (($query) $condtype ($query2)) ";
		}elsif($query2){
			$query = $query2;
		}elsif($query){
			$query = substr($query,0,-4);
			$query = " 1 AND ($query) ";
		}

		@db_cols = ('ID_orders','Date','ID_customers','StatusPay','StatusPrd','Status');

		$query = " sl_orders INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers WHERE ($query) ";
		$query = $query . $query_only_my_records . " ORDER BY sl_orders.ID_orders DESC ";
		# &cgierr('-->'.$query);
		return &query_sql('ID_orders,sl_orders.Date as Date,sl_customers.ID_customers as ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status',$query,'sl_orders.ID_orders',@db_cols);
	
	}elsif($in{'pmtfield2'} or $in{'pmtfield3'} or $in{'authcode'} or $in{'refid'} or $in{'type'}){

		#####
		##### Busqueda cruzada con datos de pago
		#####


		my ($query, $condtype);
		$in{'from_date'} = &get_sql_date() if !$in{'from_date'};
		
		if ($in{'st'} =~ /or/i){
			$condtype = "OR";
		}else{
			$condtype = "AND";
		}
		if ($in{'pmtfield2'}){
			$query = " $condtype (PmtField2 like '%".&filter_values($in{'pmtfield2'})."%' AND PmtField2 !='' AND PmtField2 IS NOT NULL ) ";
		}elsif($in{'pmtfield3'}){
			$query = " $condtype (PmtField3 like '%".&filter_values($in{'pmtfield3'})."' AND PmtField3 !='' AND PmtField3 IS NOT NULL ) ";
		}elsif($in{'authcode'}){
			$query = " $condtype AuthCode = '".&filter_values($in{'authcode'})."' ";	
		}elsif($in{'type'}){
			$query = " $condtype Type='".&filter_values($in{'type'})."' ";	
		}

		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " $condtype sl_orders.Ptype IN('$in{'ptype'}') ";
		}$in{'ptype'} =~ s/','/\|/g;

		## Filter By shp_type
		if ($in{'shp_type'}){
			$in{'shp_type'} =~ s/\|/','/g;	
			$query .= " AND shp_type IN('$in{'shp_type'}') ";
		}$in{'shp_type'} =~ s/','/\|/g;


		if($in{'bposteddate'}){
			$in{'from_posteddate'} = $in{'from_date'};
			$in{'to_posteddate'} = $in{'to_date'};
			@db_cols = ('ID_orders','Date','ID_customers','StatusPay','StatusPrd','Status');
			if($in{'to_posteddate'} and $in{'from_posteddate'}){
				$query .= " AND (sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}') ";
			}elsif($in{'from_posteddate'}){
				$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
			}elsif($in{'to_posteddate'}){
				$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
			}
		}else{
			if($in{'from_date'}){
				$query .= " AND sl_orders.Date >= '$in{'from_date'}' ";
			}
			if($in{'to_date'}){
				$query .= " AND sl_orders.Date <= '$in{'to_date'}' ";
			}
		}


		if($query){

			## Este if esta sujeto a revision del query, por el momento en desuso (10/18/2010)
			#
			if (!1){#$in{'refid'}){
				my (@hits);
				@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders");
				$numhits = $sth->rows;
				if ($numhits == 0){
					return (0,'');
				}
				(!$in{'nh'}) and ($in{'nh'}=1);
				my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};	
				my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date as Date,shp_State,ID_customers,StatusPay,StatusPrd,sl_orders.Status FROM sl_orders,sl_orders_plogs WHERE sl_orders.ID_orders=sl_orders_plogs.ID_orders AND Data like '%".&filter_values($in{'refid'})."%' GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'}");
				while ($rec = $sth->fetchrow_hashref){
						foreach my $column (@db_cols) {
						push(@hits, $rec->{$column});
					}
				}
				return ($numhits, @hits);
			
			} else {

				my (@hits);
				@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
				$query1 = "SELECT sl_orders.ID_orders FROM sl_orders,sl_orders_payments WHERE (sl_orders.ID_orders=sl_orders_payments.ID_orders $query)";
				$query1 = $query1 . $query_only_my_records . " GROUP BY sl_orders.ID_orders ORDER BY sl_orders.ID_orders DESC ";

				my ($sth) = &Do_SQL($query1);
				my $numhits = $sth->rows;
				if ($numhits == 0){
					return (0,'');
				}
				(!$in{'nh'}) and ($in{'nh'}=1);
				my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};

				$query2 = "SELECT sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,StatusPay,StatusPrd,sl_orders.Status FROM sl_orders,sl_orders_payments WHERE (sl_orders.ID_orders=sl_orders_payments.ID_orders $query)";
				$query2 = $query2 . $query_only_my_records . "  GROUP BY sl_orders.ID_orders LIMIT $first,$usr{'pref_maxh'} ";
				my ($sth) = &Do_SQL($query2);
				while ($rec = $sth->fetchrow_hashref){
						foreach my $column (@db_cols) {
						push(@hits, $rec->{$column});
					}
				}
				return ($numhits, @hits);
			}
		} else {
			return &query('sl_orders');
		}


	}elsif($in{'avs_response'}){
	
		#####
		##### Busqueda por el ultimno paylog
		#####


		delete($in{'from_date'});
		delete($in{'to_date'});
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		
		my ($query);
		if ($in{'status'}){
			my $cadstatus=$in{'status'};
			if ($cadstatus =~ /\|/){
				$cadstatus =~ s/\|/','/g;
				$query = " AND Status IN ('$cadstatus') ";
			}else{
				$query = " AND Status='$cadstatus' ";
			}
		}
		if ($in{'statuspay'} =~ /\|/){
			$in{'statuspay'} =~ s/\|/','/g;
			$query .= " AND StatusPay IN ('$in{'statuspay'}')";
		}elsif($in{'statuspay'}){
			$query .= "  AND sl_orders.StatusPay='$in{'statuspay'}'";
		}
		if ($in{'statusprd'} =~ /\|/){
			$in{'statusprd'} =~ s/\|/','/g;
			$query .= " AND StatusPrd IN ('$in{'statusprd'}')";
		}elsif($in{'statusprd'}){
			$query .= "  AND StatusPrd='$in{'statusprd'}'";
		}
		if ($in{'from_date'}){
			$query .= " AND Date >'".&filter_values($in{'from_date'})."' ";
		}
		if ($in{'to_date'}){
			$query .= " AND Date >'".&filter_values($in{'to_date'})."' ";
		}
		
		## Filter by Order Type
		if ($in{'ptype'}){
			$in{'ptype'} =~ s/\|/','/g;	
			$query .= " AND Ptype IN('$in{'ptype'}') "; 
		}$in{'ptype'} =~ s/','/\|/g;

		my $cadavs = "ccAuthReply_avsCode = [$in{'avs_response'}]";
		$cadavs = "AVS Response = [$in{'avs_response'}]" if($in{'e'} == 2 or $in{'e'} == 4);
		$query .= "  0 < (SELECT COUNT(*) FROM sl_orders_plogs WHERE ID_orders = sl_orders.ID_orders AND Data NOT REGEXP 'AVS VERIFICATION' AND Data REGEXP '$cadavs' ORDER BY ID_orders_plogs DESC LIMIT 1) ";
		$query = "sl_orders WHERE ($cad_nopreorder $query) ";
		$query = $query . $query_only_my_records . " ORDER BY ID_orders DESC";

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status",$query,'ID_orders',@db_cols);
	
	}elsif($in{'bposteddate'}){

		#####
		##### Busqueda por el Posted Date
		#####

		$in{'from_posteddate'} = $in{'from_date'};
		$in{'to_posteddate'} = $in{'to_date'};
		@db_cols = ('ID_orders','Date','ID_customers','shp_State','StatusPay','StatusPrd','Status');
		if($in{'to_posteddate'} and $in{'from_posteddate'}){
			$query .= " AND sl_orders.PostedDate BETWEEN '$in{'from_posteddate'}' AND  '$in{'to_posteddate'}' ";
		}elsif($in{'from_posteddate'}){
			$query .= " AND sl_orders.PostedDate >= '$in{'from_posteddate'}' ";
		}elsif($in{'to_posteddate'}){
			$query .= " AND sl_orders.PostedDate <= '$in{'to_posteddate'}' ";
		}

		$query = "sl_orders WHERE (1 $query) ";
		$query = $query . $query_only_my_records . " ORDER BY ID_orders DESC";

		return &query_sql("sl_orders.ID_orders,sl_orders.Date as Date,ID_customers,shp_State,sl_orders.StatusPay,sl_orders.StatusPrd,sl_orders.Status",$query,'ID_orders',@db_cols);
	}else{
		return &query('sl_orders');
	}
}


sub view_opr_orders {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on: 8/11/2008 9:02:54 AM
# Last Modified by: Carlos Haas
# Author: Carlos Haas
# Description : 
# Parameters : 

# Last Modified on: 10/08/08  16:17:17
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Total_Order = Products + Services - Discounts  + Taxes + Shipping
# Taxes = Products * Taxes Porc.

# Last Modified RB: 11/24/08  11:56:19 - Added link to preorder
# Last Modified RB: 12/18/08  12:35:46 - Added 30 day older capture validation
# Last Modified on: 09/14/09 17:35:34
# Last Modified by: MCC C. Gabriel Varela S: Se agrega variable cmd_did
# Last time Modified by PH on 01/24/20122: Se agrega boton para cambio a Wholesale
# Last time Modified by FC on 12/10/2015: Se agrego cambio automatico en GE.
#&cgierr('P-Nombre:comments');

	#####
	##### Se agrega reestriccion para mostrar solo Orders de Canales de Venta que el usuario tenga asignados.
	#####
	
	if ($in{'only_records_by_salesorigins'} and $in{'only_records_by_salesorigins'} ne ''){
		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$in{'view'}' AND ID_salesorigins IN ($in{'only_records_by_salesorigins'});");
		$view_orders_validation = $sth->fetchrow_array();

		if (!$view_orders_validation){
			return &html_unauth;
		}
	}

	# Prefix dinamic for Print Formats

	my %config_values_prices = (
		'cod',	{1,'shipment_cod_standard',2,'shipment_cod_express',3,'shipment_cod_cod'}, 
		'credit-card',	{1,'shipment_cc_standard',2,'shipment_cc_express',3,'shipment_cc_cod' },
		'referenced deposit',	{1,'shipment_rd_standard',2,'shipment_rd_express',3,'shipment_rd_cod' }
	);

	$va{'e_prefix'} = $cfg{'prefixentershipment'};

	$va{'orders_in_batch'} = 0;
	$va{'reassign_zone'} = qq|<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_orders]&reassign_zone=1"><img src='[va_imgurl]/minireload.png' title='Reassign' alt='Reassign' border='0'></a>|;;	
	if ($in{'reassign_zone'}){
		&update_order_zone($in{'id_orders'});
	}

	## Payment Charge
	if ($in{'payment_charge'} and $in{'pc_id_orders_payments'} and $in{'pc_captured'} eq 'Yes' and &check_permissions('edit_order_cleanup','','')){
		
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Captured='Yes', Authcode='$in{'pc_authcode'}', Capdate='$in{'pc_capdate'}' WHERE ID_orders='$in{'id_orders'}' AND ID_orders_payments='$in{'pc_id_orders_payments'}' AND ROUND(Amount,2)='$in{'pc_amount'}' AND (Captured<>'Yes' OR Captured IS NULL);");
		&auth_logging('payment_charged',$in{'id_orders'});

	}

	if ($in{'update_totals'}){

		########################################
		########################################
		########################################
		######
		###### Update Totals (Button)
		######
		########################################
		########################################
		########################################

		&updateordertotals($in{'id_orders'});
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

	}elsif($in{'recalc_totals'} or $in{'edit_finished'}){

		########################################
		########################################
		########################################
		######
		###### Recalc Totals (Button) 
		######
		########################################
		########################################
		########################################

		&recalc_totals($in{'id_orders'});
		# &group_payments($in{'id_orders'});
		&verify_order_lines($in{'id_orders'});
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

	}elsif($in{'updateprodinfo'} and  &check_permissions('edit_order_cleanup','','')){

		########################################
		########################################
		########################################
		######
		###### Edit Products Cleanup Mode (Pencil)
		######
		########################################
		########################################
		########################################

		my ($query,@cols);
		if(&check_permissions('edit_order_cleanup','','')){	
			@cols = ('SalePrice','Shipping','Cost','SerialNumber','ShpDate','Tracking','ShpProvider','Status');
		}else{
			@cols = ('SalePrice','Shipping','Status');
		}
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET $query WHERE ID_orders_products='$in{'id_orders_products'}'");
		&auth_logging('opr_orders_cu_prdupd',$in{'id_orders'});

	}elsif($in{'updatepayinfo'} and &check_permissions('edit_order_cleanup','','')){

		########################################
		########################################
		########################################
		######
		###### Edit Payments Cleanup Mode (Pencil)
		######
		########################################
		########################################
		########################################

		my ($query,@cols);
		@cols = ('PmtField1','PmtField2','PmtField3','PmtField4','PmtField5','PmtField6','PmtField7','PmtField8','PmtField9','Amount','Reason','Paymentdate','AuthCode','Captured','CapDate','Status');;
		
		if ($in{'partial_update'}) {
			@cols = ('PmtField1','PmtField3','PmtField4','PmtField5','PmtField6','PmtField7','PmtField8','PmtField9','Amount','Reason','Paymentdate','AuthCode','Captured','CapDate','Status');
		}
		
		for(0..$#cols){
			$query .= " $cols[$_]='".&filter_values($in{'ajax'.lc($cols[$_])})."',";
		}		
		chop($query);

		my $saved_captured = &load_name('sl_orders_payments','ID_orders_payments',$in{'id_orders_payments'}, 'Captured');
		my $saved_reason = &load_name('sl_orders_payments','ID_orders_payments',$in{'id_orders_payments'}, 'Reason');
		
		my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET $query WHERE ID_orders_payments = '$in{'id_orders_payments'}';");
		&auth_logging('opr_orders_cu_payupd',$in{'id_orders'});
		
		# Captura de cobros aplicados de forma manual
		# Nota : Que es esa variable partial_update???
		if ( $in{'partial_update'} ) {

			my ($sth_partial) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders_payments='$in{'id_orders_payments'}';");
			$rec_partial = $sth_partial->fetchrow_hashref;
			
			&auth_logging('opr_orders_partial_payupd',$in{'id_orders'});

			&add_order_notes_by_type($usr{'id_admin_users'},&trans_txt('opr_orders_partial_payupd')."From: ".$rec_partial->{'Captured'}." ,".$rec_partial->{'CapDate'}." ,".$rec_partial->{'AuthCode'}." | To: ".$in{'ajaxcaptured'}.", ".$in{'ajaxcapdate'}." ,".$in{'ajaxauthcode'},"Low");





			# Si se captura un cobro de forma manual y no estaba previamente capturado, se registra contabilidad
			if ($in{'ajaxcaptured'} eq 'Yes' and $saved_captured ne 'Yes'){

				$va{'this_accounting_time'} = time();
				my $sqlmod_update_records = (&table_field_exists('sl_movements','MD5Verification') and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;


				&Do_SQL("SET autocommit = 0;");
				&Do_SQL("START TRANSACTION;");
				my $acc_status; my $acc_string; my $flag_acc = 0;				
				my ($mod1, $order_type, $ctype, $ptype,@params);

				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = ". $in{'id_orders'} .";");
				($order_type, $ctype) = $sth->fetchrow();
				$ptype = get_deposit_type($in{'id_orders_payments'},'');
				@params = ($in{'id_orders'}, $in{'id_orders_payments'});
				($in{'ida_banks'}) and (push(@params, $in{'ida_banks'}));
				push(@params,1);

				if($in{'ajaxamount'} >= 0){

					######
					###### Positive Amount 
					######
					( lc($saved_reason) eq 'exchange') and ($ptype = 'COD') and ($in{'overwrite_ptype'} = 'COD');
					($acc_status, $acc_string) = &accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
					++$flag_acc if $acc_status;
					&auth_logging('opr_orders_payments_paid',$in{'id_orders'});
					#&cgierr('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype);

				}else{

					######
					###### Credits (Refund not via api / Chargeback)
					######
					
					my ($sth) = &Do_SQL("SELECT IF(merAction = 'Chargeback',1,0), ID_returns 
											FROM sl_orders_payments INNER JOIN sl_creditmemos_payments ON sl_orders_payments.ID_orders_payments = ID_orders_payments_added
											INNER JOIN sl_creditmemos USING(ID_creditmemos) INNER JOIN sl_returns ON Reference = ID_returns
											WHERE sl_orders_payments.ID_orders_payments = ". $in{'id_orders_payments'} ." AND ABS(sl_creditmemos_payments.Amount) = ABS(sl_orders_payments.Amount);"); 
					my ($is_chargeback, $id_returns) = $sth->fetchrow();
					$ptype = 'COD' if !$is_chargeback;
					$in{'overwrite_ptype'} = 'COD' if !$is_chargeback;
					
					($acc_status, $acc_string) = &accounting_keypoints('order_refund_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
					++$flag_acc if $acc_status;
					&auth_logging('opr_orders_payments_credited',$in{'id_orders'});

					if($is_chargeback){

						#########
						######### Chargeback needs to close return
						#########
						&Do_SQL("UPDATE sl_returns SET PackingListStatus = 'Done' WHERE ID_returns = ". $id_returns .";");
						$mod1 = ", StatusPrd = 'None' ";
						$in{'statusprd'} = 'None';

					}

				}

				if($flag_acc){

					## Problems with Accounting
					&Do_SQL("ROLLBACK;");

				}else{

					## Movements Validation 
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = ". $in{'id_orders'} ." AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records .";");
  					my ($total_records) = $sth->fetchrow();

  					if($total_records > 2 ){

  						## Problems with Movements
						&Do_SQL("ROLLBACK;");

  					}else{

  						&Do_SQL("UPDATE sl_orders_payments SET PostedDate = CURDATE() WHERE ID_orders_payments = ". $in{'id_orders_payments'} .";");
						&Do_SQL("UPDATE sl_orders SET StatusPay = 'None' $mod1 WHERE ID_orders = ". $in{'id_orders'} .";");
						$in{'statuspay'} = 'None';	
						delete($in{'overwrite_ptype'}) if $in{'overwrite_ptype'};
						&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});
						&Do_SQL("COMMIT;");

					}

				}

				&Do_SQL("SET autocommit = 1;");

			}
		}
	}

    ## Scanning Services
    if ($in{'scanning_services'}){
        #Validate Permissions
        if (&check_permissions('opr_orders_scan_services','','')) {
            #Get total paids
            my ($tot_tax,$ordernet,$discount,$shipping,$total_order) = &order_total_paid($in{'id_orders'});
            #Get order status
            my ($order_status) = &load_name('sl_orders','ID_orders', $in{'id_orders'},'Status');
            #Validate total order amounts
            if ((round(($ordernet + $tot_tax + $shipping - $discount),2) == round($total_order,2))) {
                #Validate status order as Processed
                if ($order_status eq 'Processed') {

                    &Do_SQL("START TRANSACTION;");

                    #Update ShpDate, PostedDate with current date
                    my ($sth) = &Do_SQL(
                        "UPDATE sl_orders_products 
                        SET sl_orders_products.ShpDate = CURDATE(),
                        sl_orders_products.PostedDate = CURDATE()
                        WHERE sl_orders_products.ID_orders = '".$in{'id_orders'}."';"
                    );
                    #Change order status as 'Shipped'
                    my ($sth) = &Do_SQL(
                        "UPDATE sl_orders
                        SET sl_orders.PostedDate = CURDATE(),
                        sl_orders.Status = 'Shipped'
                        WHERE sl_orders.ID_orders = '".$in{'id_orders'}."';"
                    );                        
                    $in{'db'}='sl_orders';
                    &auth_logging('opr_orders_stShipped',$in{'id_orders'});

                    #Change order status on variable $in
                    $in{'status'} = &load_name('sl_orders','ID_orders', $in{'id_orders'},'Status');

                    #Save Notes
                    
                    &add_order_notes_by_type($in{'id_orders'},&trans_txt('scan_order_complete'),"Low");
                    &auth_logging('orders_note_added',$in{'id_orders'});

                    #### Acounting Movements
                    my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '".$in{'id_orders'}."';");
                    ($order_type, $ctype) = $sth->fetchrow();

                    my @params = ($in{'id_orders'});
                    my $this_keypoint = 'order_products_scanned_'. $ctype .'_'. $order_type;

                    my ($flag_acc,$msg_open) = &accounting_keypoints($this_keypoint, \@params );

					if($flag_acc == 1){
						## Accounting Problems | End Transaction
						$va{'message'} = &trans_txt('acc_general') . ' ' . $msg_open;
						&Do_SQL("ROLLBACK;");
					} else {
						&Do_SQL("COMMIT;");
						&auth_logging('service_order_scanned',$in{'id_orders'});
					}
                }
            } else {
                $va{'message'} = &trans_txt('scan_order_services_amount');
            }
        } else {
            $va{'message'} = &trans_txt('unauth_action');
        }
    }
	
	
	if ($in{'split_qty'} and &check_permissions('edit_order_cleanup','','')) {
		
		my ($sth_sum) = &Do_SQL("SELECT SUM(sl_orders_products.Quantity) as qty_product
						FROM sl_orders_products
						WHERE ID_orders_products='$in{'id_orders_products'}' AND ID_orders='$in{'id_orders'}'
								AND Quantity= '$in{'current_qty'}' AND Date = '$in{'aux_date'}' AND Time = '$in{'aux_time'}';");
		my $qty_product = $sth_sum->fetchrow;
		$in{'ajaxquantity'} = &filter_values($in{'ajaxquantity'});
		if ($in{'ajaxquantity'} < $qty_product and $in{'ajaxquantity'} > 0) {
			my $new_qty = $qty_product - $in{'ajaxquantity'};
			
			my ($sth) = &Do_SQL("SELECT sl_orders_products.*
						FROM sl_orders_products
						WHERE ID_orders_products='$in{'id_orders_products'}' AND ID_orders='$in{'id_orders'}'
									AND Quantity= '$in{'current_qty'}' AND Date = '$in{'aux_date'}' AND Time = '$in{'aux_time'}';");
					
			while ($rec = $sth->fetchrow_hashref) {
				
				my $prop_qty = $in{'ajaxquantity'} / $rec->{'Quantity'};
				
				my $new_sale_price = $prop_qty * $rec->{'SalePrice'};
				my $new_sale_price_updt = $rec->{'SalePrice'} - $new_sale_price;
				#my $new_sale_price_updt = ($new_qty / $rec->{'Quantity'}) * $rec->{'SalePrice'};
				#my $new_shipping = $prop_qty * $rec->{'Shipping'};
				#my $new_shipping_updt = $rec->{'Shipping'} - $new_shipping;
				#my $new_cost = $prop_qty * $rec->{'Cost'};
				#my $new_cost_updt = $rec->{'Cost'} - $new_cost;
				#my $new_shptax = $prop_qty * $rec->{'ShpTax'};
				#my $new_shptax_updt = $rec->{'ShpTax'} - $new_shptax;
				my $new_tax = $prop_qty * $rec->{'Tax'};
				my $new_tax_updt = $rec->{'Tax'} - $new_tax;
				my $new_discount = $prop_qty * $rec->{'Discount'};
				my $new_discount_updt = $rec->{'Discount'} - $new_discount;
				
				my ($sth_u) = &Do_SQL("UPDATE sl_orders_products
								SET Quantity='$new_qty', SalePrice='$new_sale_price_updt', Tax='$new_tax_updt', Discount='$new_discount_updt'
								WHERE ID_orders_products='$in{'id_orders_products'}' AND ID_orders='$in{'id_orders'}'
										AND Quantity= '$in{'current_qty'}' AND Date = '$in{'aux_date'}' AND Time = '$in{'aux_time'}';");
				
				my ($sth_i) = &Do_SQL("INSERT INTO sl_orders_products SET
				ID_products='$rec->{'ID_products'}',ID_orders='$rec->{'ID_orders'}',ID_packinglist='$rec->{'ID_packinglist'}',
				Related_ID_products='$rec->{'Related_ID_products'}',Quantity='$in{'ajaxquantity'}',SalePrice='$new_sale_price',
				Shipping='$rec->{'Shipping'}',Cost='$rec->{'Cost'}',Tax='$new_tax',
				Tax_percent='$rec->{'Tax_percent'}',Discount='$new_discount',FP='$rec->{'FP'}',
				SerialNumber='$rec->{'SerialNumber'}',ShpDate='$rec->{'ShpDate'}',Tracking='$rec->{'Tracking'}',
				ShpProvider='$rec->{'ShpProvider'}',ShpTax='$rec->{'ShpTax'}',ShpTax_percent='$rec->{'ShpTax_percent'}',
				PostedDate='$rec->{'PostedDate'}',Upsell='$rec->{'Upsell'}',Status='$rec->{'Status'}',
				Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
				
				&auth_logging('orders_product_qty_split',$in{'id_orders'});
			}
			
		} else {
			$va{'tabmessages'} = &trans_txt('opr_orders_quantity_invalid');
		}
	}
	
	my ($fname);
	if ($in{'id_customers'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}';");
		$rec = $sth->fetchrow_hashref;
		foreach my $key (keys %{$rec}){
			#$in{'customers.'.lc($key)} = uc($rec->{$key});
			$in{'customers.'.lc($key)} = $rec->{$key};
		}
	}
	
	for (0..$#db_cols){
		$fname = lc($db_cols[$_]);
		$in{$fname} = $in{$fname};
	}


	########################################
	### Change Ptype
	########################################
	### -----------------------------
	### Change to Credit-Card
	### -----------------------------
	my $is_conv_to_cc = &is_cc_convertible($in{'id_orders'});
	### Normal Mode
	&conver_to_cc($in{'id_orders'}) if ($is_conv_to_cc == 1 and $in{'tocc'}==1 and &check_permissions('edit_order_wholesale_ajaxmode','','')); 
	### Alternative Mode
	if ($in{'alternative_to_cc'} and ($is_conv_to_cc == 1)) {
		
		my ($sth) = &Do_SQL("SELECT count(*) FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Status IN ('Approved','Pending') AND ((Captured='No' OR Captured IS NULL) AND (CapDate='0000-00-00' OR CapDate IS NULL));");
		my $payments = $sth->fetchrow_array;
		if ($payments == 1){

			### Inicializa la transaccion
			&Do_SQL("START TRANSACTION;");

			&Do_SQL("UPDATE sl_orders SET Ptype = 'Credit-Card', Status = 'New', StatusPrd = 'None', StatusPay = 'None', shp_type = 1 WHERE ID_orders = '$in{'id_orders'}' LIMIT 1;");
			&status_logging($in{'id_orders'},'New');
			&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$in{'id_orders'}' AND ((Captured='No' OR Captured IS NULL) AND (CapDate='0000-00-00' OR CapDate IS NULL));");			
			
			## Log
			$va{'message'} = 'The order has been changed to Credit-Card';
			&auth_logging('opr_orders_cod_to_cc',$in{'id_orders'});
			
			&add_order_notes_by_type($in{'id_orders'},"The order has been changed from $in{'ptype'} to Credit-Card","Low");
		
			&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

			$in{'ptype'} = 'Credit-Card';
			$in{'status'} = 'New';
			$in{'statusprd'} = 'None';
			$in{'statuspay'} = 'None';
			$in{'shp_type'} = 1;

			###
			### FC 
			###
			if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'}==1){
				$total_shp = $cfg{$config_values_prices{lc($in{'ptype'})}{$in{'shp_type'}}};
				$total_shp = 0 if( !$total_shp );
				my $query = "select id_orders_products,round( $total_shp  * ShpTax_percent,2) shptax
				from sl_orders_products	 where  id_orders='$in{'id_orders'}' and ID_products not like '6%' and `Status`='Active' order by salePrice desc limit 1";
				my ($sth) = &Do_SQL($query);
				my $price = $sth->fetchrow_hashref();
				if( $price->{'id_orders_products'} ){
					$query = "update sl_orders_products set Shipping = '$total_shp', ShpTax = $price->{'shptax'} where id_orders_products='$price->{'id_orders_products'}'";
					&Do_SQL($query);
					$query = "update sl_orders_products set Shipping = '0', ShpTax =0 where id_orders_products !='$price->{'id_orders_products'}' and id_orders = '$in{'id_orders'}' and ID_products not like '6%'";
					&Do_SQL($query);
				}
			}
			###
			### FC
			###





			### Confirma la transaccion
			&Do_SQL("COMMIT;");
		}else{
			$va{'message'} = &trans_txt('opr_orders_invalid_rd_to_cc');
		}
	}
	### -----------------------------
	### Change to Referenced Deposit
	### -----------------------------
	if ($in{'toreferenced_deposit'} and &check_permissions('change_order_toreferenced_deposit','','')){

		my ($sth) = &Do_SQL("SELECT count(*) FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Status IN ('Approved','Pending');");
		my $payments = $sth->fetchrow_array;

		if ($payments == 1){

			### Change is valid?
			my ($sth) = &Do_SQL("SELECT count(*) FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Status IN ('Approved','Pending') AND ((Captured='No' OR Captured IS NULL) AND (CapDate='0000-00-00' OR CapDate IS NULL));");
			my $is_valid = $sth->fetchrow_array;

			if( $is_valid == 1 ){
				my $pmtfield3 = &ref_banco_azteca($in{'id_orders'});

				$tmp_sth_new_payment = &Do_SQL("SELECT  ID_orders, Amount, PostedDate, ID_admin_users FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Status IN('Approved','Pending') LIMIT 1;");
				my( $tmp_id_orders,$tmp_amount,$tmp_posteddate,$tmp_id_admin_users ) = $tmp_sth_new_payment->fetchrow_array();

				### Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");

				$sth_new_payment = &Do_SQL("INSERT INTO sl_orders_payments (ID_orders_payments,  ID_orders,  Type, PmtField2,  PmtField3,  PmtField4,  PmtField5,  PmtField6,  PmtField7,  PmtField8,  PmtField9,  PmtField10, PmtField11, Amount,  Reason,  Paymentdate,  AuthCode,  AuthDateTime,  Captured,  CapDate,  PostedDate,  Status,  Date,  Time,  ID_admin_users) values
				(NULL,  '$tmp_id_orders',  'Referenced Deposit',  '',  '$pmtfield3',  '',  '',  '',  '',  '',  '',  '',  '',  '$tmp_amount',  'Sale',  CURDATE(),  '',  '',  NULL,  NULL,  '$tmp_posteddate',  'Approved',  CURDATE(),  CURTIME(),  '$tmp_id_admin_users');");
				$new_id_orders_payments = $sth_new_payment->{'mysql_insertid'};

				if ($new_id_orders_payments > 0){

					&Do_SQL("UPDATE sl_orders SET Ptype = 'Referenced Deposit', Status = 'New', StatusPrd = 'None', StatusPay = 'Pending Payment', shp_type = 1 WHERE ID_orders = '$in{'id_orders'}' LIMIT 1;");
					&status_logging($in{'id_orders'},'New');
					&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$in{'id_orders'}' AND  ID_orders_payments <> '$new_id_orders_payments' AND ((Captured='No' OR Captured IS NULL) AND (CapDate='0000-00-00' OR CapDate IS NULL));");
					
					## Log
					$va{'message'} = &trans_txt('opr_orders_toreferenced_deposit_applied');
					&auth_logging('opr_orders_toreferenced_deposit_applied',$in{'id_orders'});
					
					
					&add_order_notes_by_type($in{'id_orders'},"The order has been changed from $in{'ptype'} to Referenced Deposit","Low");
					
					
					&add_order_notes_by_type($in{'id_orders'}, &trans_txt('opr_orders_banking_references').":\n".&trans_txt('opr_orders_banco_azteca').": $pmtfield3\n".&trans_txt('opr_orders_banorte').": $in{'id_orders'}","Low");
					
					&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

					$in{'ptype'} = 'Referenced Deposit';
					$in{'status'} = 'New';
					$in{'statusprd'} = 'None';
					$in{'statuspay'} = 'Pending Payment';
					$in{'shp_type'} = 1;
					###
					### FC 
					###
					if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'}==1){
						$total_shp = $cfg{$config_values_prices{lc($in{'ptype'})}{$in{'shp_type'}}};
						$total_shp = 0 if( !$total_shp );
						my $query = "select id_orders_products,round( $total_shp  * ShpTax_percent,2) shptax
						from sl_orders_products	 where  id_orders='$in{'id_orders'}' and ID_products not like '6%' and `Status`='Active' order by salePrice desc limit 1";
						my ($sth) = &Do_SQL($query);
						my $price = $sth->fetchrow_hashref();
						if( $price->{'id_orders_products'} ){
							$query = "update sl_orders_products set Shipping = '$total_shp', ShpTax = $price->{'shptax'} where id_orders_products='$price->{'id_orders_products'}'";
							&Do_SQL($query);
							$query = "update sl_orders_products set Shipping = '0', ShpTax =0 where id_orders_products !='$price->{'id_orders_products'}' and id_orders = '$in{'id_orders'}' and ID_products not like '6%'";
							&Do_SQL($query);
						}

						$query = "select id_orders_payments, ID_orders, Type, Amount, Reason, Paymentdate, Date, Time, Status, ID_admin_users from sl_orders_payments where ID_orders='$in{'id_orders'}' order by Date desc,Time desc limit 1";
						($sth) = &Do_SQL($query);

						my ($rr) = $sth->fetchrow_hashref();
						$query = "update sl_orders_payments set `Status`='Cancelled' where ID_orders_payments='$rr->{'ID_orders_payments'}'";
						&Do_SQL($query);

						$query = "select sum( SalePrice+Tax ) as total from sl_orders_products where id_orders=$in{'id_orders'}";
						($sth)  = &Do_SQL($query);
						my ($pay) = $sth->fetchrow_hashref();


						$new_payment = $pay->{'total'}+$total_shp+$price->{'shptax'};
						$query = "update sl_orders_payments set Amount = '$new_payment' where id_orders_payments = '$rr->{'id_orders_payments'}'";
						&Do_SQL($query);
						$va{'q1'} = $query;
					}
					###
					### FC
					###

					### Confirma la transaccion
					&Do_SQL("COMMIT;");
					
				}else{
					### Cancela la transaccion
					&Do_SQL("ROLLBACK;");

					$va{'message'} = &trans_txt('opr_orders_invalid_cc_to_rd');
				}
			}else{
				$va{'message'} = &trans_txt('opr_orders_invalid_cc_to_rd');
			}

		}elsif($payments > 1){
			$va{'message'} = &trans_txt('opr_orders_multiple_payments');
		}else{
			$va{'message'} = &trans_txt('opr_orders_no_payments');
		}
	}
	### -----------------------------
	### Change to COD
	### -----------------------------
	if ($in{'tocod'} and $cfg{'cc_to_cod_mode'} == 2) {

		############
		############ CHANGE TO COD MODE2
		############

		my ($sth) = &Do_SQL("SELECT COUNT(*) 
								FROM sl_orders INNER JOIN sl_orders_payments 
								USING(ID_orders)
								WHERE
								ID_orders = '$in{'id_orders'}' 
								AND
								(
									sl_orders_payments.CapDate ='0000-00-00' 
									OR sl_orders_payments.CapDate IS NULL
								) 	
								AND sl_orders_payments.Status = 'Approved'	
								AND (
										sl_orders_payments.Captured IS NULL 
										OR sl_orders_payments.Captured = ''
										OR sl_orders_payments.Captured = 'No'
									)
								AND sl_orders.Status != 'Shipped' 
								AND sl_orders.Ptype IN ('Credit-Card','Referenced Deposit');");	
		my $is_valid = $sth->fetchrow();

		if ($is_valid) {

			my ($sth1) = &Do_SQL("SELECT Amount, Paymentdate  FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}';");
			my $qry_payment = $sth1->fetchrow_hashref();
			
			### Inicializa la transaccion
			&Do_SQL("START TRANSACTION;");

			my ($sth2) = &Do_SQL("UPDATE sl_orders SET Status='New', Ptype='COD', shp_type=3 WHERE ID_orders = '$in{'id_orders'}' LIMIT 1;");
			&status_logging($in{'id_orders'},'New');
			&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

			my ($sth3) = &Do_SQL("UPDATE sl_orders_payments SET Status='Cancelled' WHERE ID_orders = '$in{'id_orders'}' AND Status != 'Cancelled' LIMIT 1;");
			my ($sth4) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$in{'id_orders'}', Type = 'COD', Status='Approved', Amount = '$qry_payment->{'Amount'}', Paymentdate = '$qry_payment->{'Paymentdate'}', Captured = NULL, CapDate = NULL, PostedDate = NULL, Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			&auth_logging('opr_orders_cc_to_cod',$in{'id_orders'});
			
			
			&add_order_notes_by_type($in{'id_orders'},"The order has been changed from CC to COD","Low");

			$va{'message'} = &trans_txt('opr_orders_cc_to_cod');

			$in{'ptype'} = 'COD';
			$in{'shp_type'} = 3;
			###
			### FC 
			###
			if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'}==1){
				$total_shp = $cfg{$config_values_prices{lc($in{'ptype'})}{$in{'shp_type'}}};
				$total_shp = 0 if( !$total_shp );
				my $query = "select id_orders_products,round( $total_shp  * ShpTax_percent,2) shptax
				from sl_orders_products	 where  id_orders='$in{'id_orders'}' and ID_products not like '6%' and `Status`='Active' order by salePrice desc limit 1";
				my ($sth) = &Do_SQL($query);
				my $price = $sth->fetchrow_hashref();
				if( $price->{'id_orders_products'} ){
					$query = "update sl_orders_products set Shipping = '$total_shp', ShpTax = $price->{'shptax'} where id_orders_products='$price->{'id_orders_products'}'";
					&Do_SQL($query);
					$query = "update sl_orders_products set Shipping = '0', ShpTax =0 where id_orders_products !='$price->{'id_orders_products'}' and id_orders = '$in{'id_orders'}' and ID_products not like '6%'";
					&Do_SQL($query);
				}

				$query = "select id_orders_payments, ID_orders, Type, Amount, Reason, Paymentdate, Date, Time, Status, ID_admin_users from sl_orders_payments where ID_orders='$in{'id_orders'}' order by Date desc,Time desc limit 1";
				($sth) = &Do_SQL($query);
				my ($rr) = $sth->fetchrow_hashref();
				$query = "update sl_orders_payments set `Status`='Cancelled' where ID_orders_payments='$rr->{'ID_orders_payments'}'";
				&Do_SQL($query);

				$query = "select sum( SalePrice+Tax ) as total from sl_orders_products where id_orders=$in{'id_orders'}";
				($sth)  = &Do_SQL($query);
				my ($pay) = $sth->fetchrow_hashref();


				$new_payment = $pay->{'total'}+$total_shp+$price->{'shptax'};
				$query = "update sl_orders_payments set Amount = '$new_payment' where id_orders_payments = '$rr->{'id_orders_payments'}'";
				&Do_SQL($query);
				$va{'q1'} = $query;
			}
			###
			### FC
			###

			### Confirma la transaccion
			&Do_SQL("COMMIT;");
		} else {
			$va{'message'} = &trans_txt('opr_orders_invalid_cc_to_cod');
		}		

	} elsif( $in{'tocod'} and &check_permissions('edit_order_wholesale_ajaxmode','','') ){

		############
		############ CHANGE TO COD REGULAR
		############

		### Inicializa la transaccion
		&Do_SQL("START TRANSACTION;");

		&changeto_cod_apply($in{'id_orders'});
		###
		### FC 
		###
		if($cfg{'use_default_shipment'} and $cfg{'use_default_shipment'}==1){
			$total_shp = $cfg{$config_values_prices{lc($in{'ptype'})}{$in{'shp_type'}}};
			$total_shp = 0 if( !$total_shp );
			my $query = "select id_orders_products,round( $total_shp  * ShpTax_percent,2) shptax
			from sl_orders_products	 where  id_orders='$in{'id_orders'}' and ID_products not like '6%' and `Status`='Active' order by salePrice desc limit 1";
			my ($sth) = &Do_SQL($query);
			my $price = $sth->fetchrow_hashref();
			if( $price->{'id_orders_products'} ){
				$query = "update sl_orders_products set Shipping = '$total_shp', ShpTax = $price->{'shptax'} where id_orders_products='$price->{'id_orders_products'}'";
				&Do_SQL($query);
				$query = "update sl_orders_products set Shipping = '0', ShpTax =0 where id_orders_products !='$price->{'id_orders_products'}' and id_orders = '$in{'id_orders'}' and ID_products not like '6%'";
				&Do_SQL($query);
			}

			$query = "select id_orders_payments, ID_orders, Type, Amount, Reason, Paymentdate, Date, Time, Status, ID_admin_users from sl_orders_payments where ID_orders='$in{'id_orders'}' order by Date desc limit 1";
			($sth) = &Do_SQL($query);
			# my ($ID_orders_payments, $ID_orders, $Type, $Amount, $Reason, $Paymentdate, $date, $time, $status, $id_admin_user) = $sth->fetchrow_hashref();
			my ($rr) = $sth->fetchrow_hashref();
			$query = "update sl_orders_payments set `Status`='Cancelled' where ID_orders_payments='$rr->{'ID_orders_payments'}'";
			&Do_SQL($query);

			$query = "select sum( SalePrice+Tax ) as total from sl_orders_products where id_orders=$in{'id_orders'}";
			($sth)  = &Do_SQL($query);
			my ($pay) = $sth->fetchrow_hashref();


			$new_payment = $pay->{'total'}+$total_shp+$price->{'shptax'};
			# use Data::Dumper;
			# print "Content-type: text/html\n\n";
			# print Dumper $total_shp;					
			# exit;
			$query = "insert into sl_orders_payments (ID_orders, Type, Amount, Reason, Paymentdate, Date, Time, Status, ID_admin_users) 
			values('$in{'id_orders'}', '$in{'ptype'}', '$new_payment', '$rr->{'Reason'}', '$rr->{'Paymentdate'}',curdate(), curtime(),'$rr->{'Status'}','$rr->{'ID_admin_users'}' )";
			&Do_SQL($query);
			$va{'q1'} = $query;
		}
		###
		### FC
		###
		### Confirma la transaccion
		&Do_SQL("COMMIT;");

		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

	}

	### -----------------------------
	### Convert to wholesale
	### -----------------------------
	if($in{'wholesale'}==1 and &check_permissions('edit_order_cleanup','','')){		
		&retail_to_wholesale();
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});
	}
	
	########################################
	###### Reactivate COD?
	########################################
	if (&check_permissions('opr_orders_reactivate','','') and $in{'reactivate'}){
		### Inicializa la transaccion
		&Do_SQL("START TRANSACTION;");

		&cod_apply_reactivate($in{'id_orders'});

		### Confirma la transaccion
		&Do_SQL("COMMIT;");
	}

	## Validate COD Orders blocked (for change order type icon block)
	if($in{'ptype'} eq 'COD' and $in{'status'} eq 'Cancelled'){

		my ($sth) =  &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products WHERE sl_orders_products.ID_orders = ". $in{'id_orders'}.";");
		my ($these_parts) = $sth->fetchrow();
		($these_parts) and ($va{'cod_blocked'} = 1);

	}	

	
	$va{'cmd_customer'} = 'opr_customers';
	$va{'cmd_did'} = 'mm_dids';
	### Warning Message
	$va{'waringmsg'} = qq|<a href="/cgi-bin/mod/admin/dbman?cmd=opr_invoices&view=[in_id_orders]"><img src='[va_imgurl]/[ur_pref_style]/warning.gif' title='Warining' alt='Invoice' border='0'></a>|;;
	
	### Station Name
	$va{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');

	### Orders Totals
	my ($sth) = &Do_SQL("SELECT 
	                    	SUM(Tax + ShpTax)AS TotalTax,
	                    	SUM(SalePrice)AS OrderNet,
	                    	SUM(Discount)AS Discount,
	                    	SUM(Shipping)AS Shipping,
	                    	SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal
	                    	FROM sl_orders_products
	                    WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN ('Inactive','Order Cancelled');");
	my ($tot_tax,$ordernet,$discount,$shipping,$total_order) = $sth->fetchrow();

	#$tot_tax = (&taxables_in_order($in{'id_orders'})-$in{'orderdisc'})*$in{'ordertax'};
	#$va{'total_order'} = &format_price($in{'ordernet'}-$in{'orderdisc'}+$in{'ordershp'}+$tot_tax);	
	#$va{'ordernet'} = &format_price($in{'ordernet'});
	#$va{'orderdisc'} = &format_price($in{'orderdisc'});
	#$va{'ordershp'} = &format_price($in{'ordershp'});

	$va{'total_taxes'} = &format_price($tot_tax);
	$va{'total_order'} = &format_price($total_order);
	$va{'ordernet'} = &format_price($ordernet);
	$va{'orderdisc'} = &format_price($discount);
	$va{'ordershp'} = &format_price($shipping);
	if ($in{'toprint'}){
		&get_company_info();
		# my ($sth) = &Do_SQL("SELECT UPPER(CONCAT(Firstname,' 'LastName1,' ',LastName1)) FROM admin_users WHERE ID_admin_users = '$usr{'id_admin_users'}';");
		# my ($last4cc, $authcode, $amount) = $sth->fetchrow_array;
	}
	if($in{'voucher'}){
		my ($sth) = &Do_SQL("SELECT RIGHT(PmtField3,4)PmtField3, AuthCode, Amount FROM sl_orders_payments WHERE ID_orders = '$in{'id_orders'}' AND Captured='Yes' AND PmtField7 IN('CreditCard','Tpv')");
		my ($last4cc, $authcode, $amount) = $sth->fetchrow_array;
		$va{'last4cc'} = $last4cc;
		$va{'authcode'} = $authcode;
		$va{'plaza'} = $rec->{'FirstName'};
		$va{'total_order_payments'} =  &format_price($amount);

	}
		
	################################################################################	
	my ($sth2) = &Do_SQL("SELECT SUM(Tax+ShpTax) Tot_tax, Tax_percent FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' AND Status NOT IN('Order Cancelled', 'Inactive')  GROUP BY Tax_percent ORDER BY Tax_percent DESC");
	my ($rec_tax);
	$va{'tax_lines'} = '';
	my $tax_line_c = 0;

	my $sth_cupon = &Do_SQL("SELECT Name, DiscPerc, DiscValue FROM sl_coupons INNER JOIN sl_coupons_trans on sl_coupons.ID_coupons=sl_coupons_trans.ID_coupons WHERE ID_orders ='$in{'id_orders'}'");
	my $rec_cupon = $sth_cupon->fetchrow_hashref();
	if( $rec_cupon->{'Name'} ){
		$rec_cupon->{'Name'};
		my $disc_cupon = ($rec_cupon->{'DiscPerc'})? $rec_cupon->{'DiscPerc'}.'%' : &format_price($rec_cupon->{'DiscValue'});
		$va{'coupon_discount'} = "<img src='/sitimages/default/discounticon.png' align='right' title='".$rec_cupon->{'Name'}." $disc_cupon'>";
	}

	while ($rec_tax = $sth2->fetchrow_hashref) {
		
		if ($tax_line_c == 0) {
			$va{'tax_lines'} .= qq|
					<tr>
						<td  align="right"><font size=3>|.int($in{'orderqty'}).qq| <input type="hidden" name="orderqty" value="$in{'orderqty'}"></td>
						<td  align="right"><font size=3>$va{'ordernet'} <input type="hidden" name="orderqty" value="$in{'ordernet'}">&nbsp;&nbsp;</td>
						<td  align="right" style="color:red;border:0px; border-left:1px solid #111111;"><font size=3>$va{'orderdisc'} <input type="hidden" name="orderdisc" value="$in{'orderdisc'}"></td>
						<td  align="right"><font size=3>$va{'ordershp'} <input type="hidden" name="ordershp" value="$in{'ordershp'}"></td>
						<td  align="right"><font size=3>|.&format_price($rec_tax->{'Tot_tax'}).' <font color=#888888>('.($rec_tax->{'Tax_percent'}*100).qq|%)</font> <input type="hidden" name="ordertax" value="$in{'ordertax'}">&nbsp;&nbsp;</td>
						<td  align="right" style="border:0px; border-left:1px solid #111111;"><font size=3>[in_currency] $va{'total_order'} &nbsp;&nbsp;</td>
					</tr>|;
					
					
					
		} else {
			$va{'tax_lines'} .= qq|
					<tr>
						<td align="center"><font size=3>&nbsp; </td>
						<td align="center"><font size=3>&nbsp; </td>
						<td align="center" style="color:red;border:0px; border-left:1px solid #111111;"><font size=3>&nbsp; </td>
						<td align="center"><font size=3>&nbsp; </td>
						<td align="right"><font size=3>|.&format_price($rec_tax->{'Tot_tax'}).' ('.($rec_tax->{'Tax_percent'}*100).qq|%) <input type="hidden" name="ordertax" value="$in{'ordertax'}">&nbsp;&nbsp;</td>
						<td align="center" style="border:0px; border-left:1px solid #111111;"><font size=3>&nbsp; </td>
					</tr>|;
		}
		$tax_line_c++;
	}	
	################################################################################
		
	## No Posted Date
	(!$in{'posteddate'}) and ($in{'posteddate'}='---');
	
	$va{'tax'} = $in{'ordertax'}*100;
	$va{'ordertax'} = &format_number($in{'ordertax'}*100);
	

	###################################################
	###################################################
	### Cancelación de pedidos por fraude
	###################################################
	if( int($in{'cfraudulent'}) == 1 and int($cfg{'cancell_fraudulent'}) == 1 ){
		&cancell_fraudulent();
	}
	###################################################


	
	### Reload Order Status
	$in{'status'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Status');
	
	## Batch validation
	my $response = &block_orders_in_batch($in{'id_orders'});
	$va{'orders_in_batch'} = 1 if ($response ne 'OK');

	###################################################
	#############  Status Management

	if ($in{'changestatusto'}){

		if ($in{'changestatusto'} eq 'Processed'  &&  $in{'status'} eq 'Shipped'){
			$va{'message'} = &trans_txt('opr_orders_nochgstatus_shipped_processed');
		}elsif (&check_permissions('edit_order_status_from_'.lc($in{'status'}),'','') and &check_permissions('edit_order_status_to_'.lc($in{'changestatusto'}),'','')){
			my $validation = ($cfg{'validate_change_to_processed'} and $in{'changestatusto'} eq 'Processed')? &review_order($in{'id_orders'}):'OK';

			## Order in Batch
			if ($cfg{'validate_change_from_processed'} and $in{'status'} eq 'Processed'){
				
				if ($response ne 'OK'){
					$validation = '' if ($validation eq 'OK');
					$validation.= $response;
				}
			}
			### Si la orden es COD y está cancellada
			if($in{'status'} eq 'Cancelled' and $in{'ptype'} eq 'COD'){
				my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=".$in{'id_orders'}." AND ShpDate Is Not Null AND ShpDate != '0000-00-00';");
				my $count_shpdate = $sth->fetchrow();
				if( $count_shpdate > 0 ){
					$validation = &trans_txt('opr_orders_nochgstatus_cod');
					$error{'status'} = $validation;
				}
			}

			if ($validation eq 'OK'){

				$in{'status'} = $in{'changestatusto'};
				my ($sth2) = &Do_SQL("UPDATE sl_orders SET Status='$in{'changestatusto'}' WHERE ID_orders='$in{'id_orders'}';");
				&auth_logging('opr_orders_st'.$in{'status'},$in{'id_orders'});
				&status_logging($in{'id_orders'},$in{'changestatusto'});
				&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

			}else{
				$va{'message'} = $validation;
			}
		}else{
			$va{'message'} = &trans_txt('unauth_action');
		}
	}
	
	### -----------------------------
	### Buttons Ptype	 
	### -----------------------------
	### Button COD
	if (&changeto_cod($in{'id_orders'}) == 1 and !$in{'tocod'} and &check_permissions('edit_order_wholesale_ajaxmode','','')){
		$va{'changeto_cod'} = qq|<input type="button" value="Change to COD" class="button" onClick="return confirm_changeto_cod('$va{'script_url'}','$in{'cmd'}',$in{'id_orders'});">|;
	}
	### Button Referenced Deposit
	$va{'changeto_depositref'} = (&check_permissions('change_order_toreferenced_deposit','','')) ? qq|<input type="button" name="toreferenced_deposit" value="Change to Referenced Deposit" class="button" onClick="return confirm_changeto_depositref('$va{'script_url'}','$in{'cmd'}',$in{'id_orders'});">|:'';
	if ($va{'orders_in_batch'} and $va{'orders_in_batch'}==1){
		$va{'changeto_cod'} = '';
		$va{'changeto_depositref'} = '';
	}	
	
	### Button Credit-Card
	if ($is_conv_to_cc == 1 and !$in{'tocc'} and $in{'status'} ne "Cancelled" and &check_permissions('edit_order_wholesale_ajaxmode','','')){
			$va{'conver_to_cc'} = 
			qq|
			<a name="add_paymenu" id="add_paymenu">&nbsp;</a>
			<!--a href='#add_paymenu' onClick="popup_show('popup_addnpay', 'nchrg_drag', 'popup_exitnchrg', 'element-right', -1, -1,'add_paymenu');"><img src='/sitimages//default/b_add.gif' title='Add payments' alt='' border='0'></a-->
			<input type="button" value="Convert to Credit Card" name="conv_to_cc_btn" class="button" onClick="popup_show('popup_addnpay', 'nchrg_drag', 'popup_exitnchrg', 'element-right', -1, -1,'add_paymenu');" />|;

			$va{'conver_to_cc'} = '' if ($va{'orders_in_batch'} and $va{'orders_in_batch'}==1);
	}
	### Button Wholesale
	if (&check_permissions('edit_order_cleanup','','')){
		$va{'changeto_wholesale'} = qq|<input type="button" value="Change to Wholesale" class="button" onClick="confirm_changeto_wholesale('$va{'script_url'}','$in{'cmd'}',$in{'id_orders'});">|;
	}

	### Link to Reactivate COD Cancelled?
	$va{'reactivate_cod'} = &cod_link_reactivate($in{'id_orders'})	if (&check_permissions('opr_orders_reactivate','','') and $in{'status'} eq 'Cancelled' and !$in{'reactivate'});
	
	
	$va{'customers.phone1'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'customers.phone1'},$in{'id_customers'}):$in{'customers.phone1'};
	$va{'customers.phone2'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'customers.phone2'},$in{'id_customers'}):$in{'customers.phone2'};
	$va{'customers.cellphone'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'customers.cellphone'},$in{'id_customers'}):$in{'customers.cellphone'};

	###### Change sales origins
	if ($in{'chgso'}){

		if (&check_permissions('change_salesorigin','','')) {

			my ($sth) = &Do_SQL("UPDATE sl_orders SET id_salesorigins=".int($in{'chgso'})." WHERE ID_orders=$in{'id_orders'};");
			&auth_logging('sl_orders_updated',$in{'id_orders'});
			$in{'id_salesorigins'}=int($in{'chgso'});
			delete($in{'chgso'});
			&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{lc($db_cols[0])});

		}else{
			$va{'message'} = &trans_txt('unauth_action');
		}
	}
	
	my $so = &load_name('sl_salesorigins','ID_salesorigins',$in{'id_salesorigins'},'Channel');
	$va{'channel_name'} = $so;
	my $sth = &Do_SQL("SELECT id_salesorigins,Channel FROM sl_salesorigins WHERE ID_salesorigins != '$in{'id_salesorigins'}' AND sl_salesorigins.Status = 'Active'");
	while(my($id,$c) = $sth->fetchrow()){
		$solink .= qq|<a href="[va_script_url]?cmd=[in_cmd]&view=[in_id_orders]&chgso=$id">$c</a>&nbsp;&nbsp;|; 
	}
	$va{'sales_origins'} = qq|<tr>
								<td valign="top" width="30%" valign="top">Sales Channel: </td> 
								<td class="smalltext" valign="top">$so <span class='private'><span class='smalltext'> -- |.&trans_txt('changeto').qq| :$solink</span></span></td>
							</tr>|;
        
	(!$in{'id_orders_alias'}) and ($in{'id_orders_alias'} = $in{'id_orders'});
        
    ##### Cahnge Order Type
	if (&check_permissions('edit_order_cleanup','','')) {
		my ($sth) = &Do_SQL("SELECT ID_orders_parts FROM sl_orders_products oprod JOIN sl_orders_parts oparts ON oprod.ID_orders_products=oparts.ID_orders_products WHERE ID_orders='$in{'id_orders'}';");
		if ($sth->rows() == 0) {
		    $va{'order_type_ed_perms'}='<span id="span_chg_order_type">
						    <img id="btn_chg_order_type" src="[va_imgurl]/[ur_pref_style]/b_edit.png" title="Click to edit Order Type" style="cursor:pointer;">
					    </span>';
		}
    }

    $va{'id_orders_alias'} = (length($in{'id_orders_alias'}) > 20)?substr ($in{'id_orders_alias'}, 0, 20).'...':$in{'id_orders_alias'};

#@ivanmiranda :: Se anexa campo de folio de facturacion	
	# Prefijo Facturacion @Fabian Cañaveral
	my $prefix = '';
	if($in{'e'} == 2){
		$prefix = 'TK';
	}
	if($in{'e'} == 4){
		$prefix = 'MO';
	}
	my ($sth) = &Do_SQL("SELECT
							sl_customers.Email,
							sl_customers.Currency,
							sl_orders.shp_type,sl_orders.shp_name,sl_orders.shp_Address1,
							sl_orders.shp_Address2,sl_orders.shp_Address3,sl_orders.shp_Urbanization,
							sl_orders.shp_City,sl_orders.shp_State,sl_orders.shp_Zip,sl_orders.shp_Country,
							sl_orders.shp_Notes,sl_orders.OrderNotes,sl_orders.Pterms,
							sl_orders.BillingNotes,sl_orders.Date,sl_orders.ID_orders, concat('$prefix',sl_orders.id_orders,date_format(sl_orders.time,'%s%H%i')) folio_facturacion
						FROM sl_orders
						INNER JOIN sl_customers  ON sl_orders.ID_customers=sl_customers.ID_customers
						WHERE ID_orders='$in{'id_orders'}';");
	($va{'customer_email'}, $va{'int_currency'},$va{'int_shp_type'} ,$va{'int_shp_name'} ,$va{'int_shp_address1'} ,$va{'int_shp_address2'} ,$va{'int_shp_address3'},
	 $va{'int_shpurbanization'} ,$va{'int_shp_city'} ,$va{'int_shp_state'},$va{'int_shp_sip'} ,$va{'int_shp_country'} ,$va{'int_shp_notes'} ,
	 $va{'int_ordernotes'} ,$va{'int_pterms'} ,$va{'int_billingNotes'} ,$va{'int_date'} ,$va{'int_id_orders'}, $va{'folio_facturacion'}) = $sth->fetchrow();

	## Reference Banco Azteca
	$va{'ref_banco_azteca'} = &ref_banco_azteca($in{'id_orders'});
	$va{'show_references'} = '<a id="ref_azteca" href="#refences">'.&trans_txt('opr_orders_show_references').'</a>' if($in{'ptype'} eq 'Referenced Deposit');


	my (@status) 		= ('New','Processed','Pending','Shipped','Cancelled','Void','System Error');
	my (@status_link)	= ('off','off','off','off','off','off','off');
	if ($in{'status'} eq 'New'){
		@status_link = ('this','on','on','off','on','on','on');
	}elsif($in{'status'} eq 'Processed'){
		@status_link = ('on','this','on','off','on','off','on');
	}elsif($in{'status'} eq 'Pending'){
		@status_link = ('off','on','this','off','on','off','on');
	}elsif($in{'status'} eq 'Shipped'){
		@status_link = ('off','off','off','this','off','off','off');
	}elsif($in{'status'} eq 'Cancelled'){
		@status_link = ('off','on','off','off','this','off','on');
	}elsif($in{'status'} eq 'Void'){
		@status_link = ('on','off','off','off','off','this','on');
	}elsif($in{'status'} eq 'System Error'){
		@status_link = ('off','off','off','off','off','off','error');
	}
	## Load Status Logs
	my (%status_logs);
	# SELECT Message,LogDate,LogTime, admin_users.ID_admin_users, FirstName, LastName 
	# 			FROM admin_logs USE INDEX (Action) LEFT JOIN admin_users ON admin_users.ID_admin_users=admin_logs.ID_admin_users 
	# 			WHERE tbl_name='sl_orders'  AND Action=$in{'id_orders'}
	my ($sth2) = &Do_SQL("SELECT admin_logs.Message,admin_logs.LogDate,admin_logs.LogTime, admin_users.ID_admin_users, admin_users.FirstName, admin_users.LastName
				FROM admin_users
				INNER JOIN (
					SELECT ID_admin_users,Message,LogDate,LogTime 
					FROM admin_logs USE INDEX (Action) 
					WHERE tbl_name='sl_orders' 
					AND Action='$in{'id_orders'}'
				) admin_logs ON admin_users.ID_admin_users=admin_logs.ID_admin_users");
	
	while ( my @tmp = $sth2->fetchrow_array()){
		if ($tmp[0] =~ /opr_orders_str(.*)/){
			$va{'statusprd_log'} .= "&bull; $1: ($tmp[3]) $tmp[4] $tmp[5] \@ $tmp[1] $tmp[2]<br>";
		}elsif ($tmp[0] =~ /opr_orders_stp(.*)/){
			$va{'statuspay_log'} .= "&bull; $1: ($tmp[3]) $tmp[4] $tmp[5] \@ $tmp[1] $tmp[2]<br>";		
		}elsif ($tmp[0] =~ /opr_orders_st(.*)/){
			$status_logs{lc($1)} .= "&bull; ($tmp[3]) $tmp[4] $tmp[5] \@ $tmp[1] $tmp[2]<br>";
		}
	}
	for my $i(0..6){
		my ($xinfo) = "width='140'"; $xinfo="width='255' align='center' valign='bottom'" if($status[$i] eq 'Void');
		$status_logs{lc($status[$i])} = "<span>$status_logs{lc($status[$i])}</span>" if($status_logs{lc($status[$i])});
		my($va_name) = 'status_'.lc($status[$i]);
		$va_name =~ s/\s/_/g;
		if ($status_link[$i] eq 'oldoff' or ($status_logs{lc($status[$i])} and $status_link[$i] eq 'off')){
			$va{$va_name} = qq|<td $xinfo><a href='#' onclick='return false;' class="status_old">$status[$i]$status_logs{lc($status[$i])}</a></td>|;
		}elsif($status_link[$i] eq 'oldon' or ($status_logs{lc($status[$i])} and $status_link[$i] eq 'on')){
			$va{$va_name} = qq|<td $xinfo><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&changestatusto=$status[$i]#status" class="status_old">$status[$i]$status_logs{lc($status[$i])}</a></td>|;
		}elsif($status_link[$i] eq 'this'){
			$va{$va_name} = qq|<td $xinfo><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&changestatusto=$status[$i]#status" class="status_this">$status[$i]$status_logs{lc($status[$i])}</a></td>|;
		}elsif($status_link[$i] eq 'error'){
			$va{$va_name} = qq|<td $xinfo><a href='#' onclick='return false;' class="status_err">$status[$i]$status_logs{lc($status[$i])}</a></td>|;
		}elsif		($status_link[$i] eq 'on'){
			$va{$va_name} = qq|<td $xinfo><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$in{'id_orders'}&changestatusto=$status[$i]#status" class="status_on">$status[$i]</a></td>|;
		}else{
			$va{$va_name} = qq|<td $xinfo><span class="status_off">$status[$i]</span></td>|;
		}
	}
	$va{'statuspay_log'} = "<span>".$va{'statuspay_log'}."</span>" if ($va{'statuspay_log'});
	$va{'statusprd_log'} = "<span>".$va{'statusprd_log'}."</span>" if ($va{'statusprd_log'});
	if ($in{'statusprd'} eq 'None'){
		$va{'titlestatusprd'} = 'status_bar_title';
	}else{
		$va{'titlestatusprd'} = 'status_bar_title_err';
	}
	if ($in{'statuspay'} eq 'None'){
		$va{'titlestatuspay'} = 'status_bar_title';
	}else{
		$va{'titlestatuspay'} = 'status_bar_title_err';
	}
	$va{'statusgrph'} = &build_page('order_status.html');
	# $va{'statusgrph'} =~ s/</&lt;/g;
	# $va{'statusgrph'} =~ s/></&gt;/g;
	# $va{'statusgrph'} = "<pre>".$va{'statusgrph'}."</pre>";

	my (@types) = split(/,/,$cfg{'shp_types'});
	foreach my $type (@types) {
		if ($in{'shp_type'} eq 1) {
			$in{'shp_type'} = "$types[0]";
		}elsif ($in{'shp_type'} eq 2) {
			$in{'shp_type'} = "$types[1]";		
		}elsif ($in{'shp_type'} eq 3){
			$in{'shp_type'} = "$types[2]"; 
			## COD Table
			$va{'cod_table'} = &get_cod_table($in{'id_orders'});
		}
	}

	## Fix incorrect driver in multiple batches
	if ($in{'search'} eq 'Print' and $in{'toprint'} and $in{'id_orders'} and $in{'id_warehouses_batches'}){

		$sql = "SELECT sl_warehouses.ID_warehouses, sl_warehouses.Name
		FROM sl_orders_products 
		INNER JOIN sl_warehouses_batches_orders ON sl_orders_products.id_orders_products=sl_warehouses_batches_orders.id_orders_products
		INNER JOIN sl_warehouses_batches ON sl_warehouses_batches_orders.ID_warehouses_batches=sl_warehouses_batches.ID_warehouses_batches
		INNER JOIN sl_warehouses ON sl_warehouses_batches.ID_warehouses=sl_warehouses.ID_warehouses
		WHERE sl_orders_products.id_orders='$in{'id_orders'}'
		AND sl_warehouses_batches.ID_warehouses_batches='$in{'id_warehouses_batches'}'
		GROUP BY sl_warehouses_batches_orders.ID_warehouses_batches
		ORDER BY sl_warehouses_batches_orders.ID_warehouses_batches DESC";
		my ($sth) = &Do_SQL($sql);
		($va{'id_warehouses'}, $va{'warehouses_name'}) = $sth->fetchrow_array();
	}

	## Editor de productos
	$va{'edit_order_products'} = '/cgi-bin/common/apps/e_orders?cmd=stdedition&id_orders='.$in{'id_orders'}.'&path=/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=opr_orders&dototemp=YES&edit_finished=';
	

	## Validacióe permisos para ver otras ordenes
	#&cgierr($in{'id_admin_users'}.'<-'.$usr{'id_admin_users'}.'<-'.$usr{'application'});
	if( $usr{'application'} eq 'sales' and $in{'id_admin_users'} != $usr{'id_admin_users'} ){
		$va{'view_full_ok'} = 0;
	} else {
		$va{'view_full_ok'} = 1;
	}

	## Informacion de Supervisor y Coordinator
	if ($cfg{'use_admin_users_tree'} and $cfg{'use_admin_users_tree'}==1 and $in{'answer1'} and $in{'answer2'}){

		$sql = "SELECT CONCAT (Firstname,' ',LastName,' ',MiddleName)Name FROM admin_users WHERE ID_admin_users='$in{'answer1'}';";
		$sth = &Do_SQL($sql);
		$va{'supervisor'} = $sth->fetchrow_array();
		$va{'supervisor'} = ($va{'supervisor'} ne '')?" / Supervisor : ".$va{'supervisor'}:"";

		$sql = "SELECT CONCAT (Firstname,' ',LastName,' ',MiddleName)Name FROM admin_users  WHERE ID_admin_users='$in{'answer2'}';";
		$sth = &Do_SQL($sql);
		($va{'coordinator'}) = $sth->fetchrow_array();
		$va{'coordinator'} = ($va{'coordinator'} ne '')?" / Coordinator : ".$va{'coordinator'}:"";
	}

	###---------------------------------
	### Shipping info
	###---------------------------------
	my $sql_shp = "SELECT 
					sl_orders_products.ID_orders,
					sl_warehouses_batches.ID_warehouses_batches
					, sl_warehouses_batches.ID_warehouses
					, sl_warehouses.Name
					, sl_warehouses_batches.Status
					, sl_warehouses_batches.Date
					, sl_warehouses_batches_orders.ScanDate
				FROM sl_warehouses_batches_orders
					INNER JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
					INNER JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
					INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_batches.ID_warehouses
				WHERE sl_orders_products.ID_orders=".$in{'id_orders'}."
				GROUP BY sl_orders_products.ID_orders, sl_warehouses_batches_orders.ID_warehouses_batches
				ORDER BY sl_warehouses_batches.ID_warehouses_batches DESC;";
	my $sth_shp = &Do_SQL($sql_shp);
	while( my $rec_shp = $sth_shp->fetchrow_hashref() ){
		$va{'shipping_info_lines'} .= '<tr>';
		$va{'shipping_info_lines'} .= '		<td style="text-align: center;">'.$rec_shp->{'ID_warehouses_batches'}.'</td>';
		$va{'shipping_info_lines'} .= '		<td style="text-align: left;">'.$rec_shp->{'ID_warehouses'}.' - '.$rec_shp->{'Name'}.'</td>';
		$va{'shipping_info_lines'} .= '		<td style="text-align: center;">'.$rec_shp->{'Status'}.'</td>';
		$va{'shipping_info_lines'} .= '		<td style="text-align: center;">'.$rec_shp->{'Date'}.'</td>';
		$va{'shipping_info_lines'} .= '		<td style="text-align: center;">'.$rec_shp->{'ScanDate'}.'</td>';
		$va{'shipping_info_lines'} .= '</tr>';
	}
	###---------------------------------

	## Información de MaxDayArrivals
	$va{'max_days_arrival'} = &load_name('sl_zones','ID_zones',$in{'id_zones'},'MaxDaysArrival');

}

sub validate_opr_orders {
# --------------------------------------------------------
# Last Modified on: 12/12/08 10:17:12
# Last Modified by: MCC C. Gabriel Varela S: Se agrega cáulo de taxes
# Last Modified by RB: 03/18/2010 se agrega validacion para el Ptype al agregar
# Last Modified by RB on 04/15/2011 12:19:13 PM : Se agrega $in{'id_orders'} como parametro para calculate_taxes
# Last Modified by RB on 06/07/2011 12:46:46 PM : Se agrega City como parametro para calculate_taxes  

	my ($old_status) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Status');
	if ($old_status eq 'Returned' or $old_status eq 'Cancelled' or $old_status eq 'Shipped'){
		$in{'status'} = $old_status;
	}
	if ($in{'add'}){
		
		$in{'status'} = 'New';
		$in{'statuspay'} = 'None';
		$in{'statusprd'} = 'None';

		if (!$in{'ptype'} and $cfg{'order_default_ptype'}){
			$in{'ptype'} = $cfg{'order_default_ptype'}
		}

		$in{'shp_type'} = 1 if !$in{'shp_type'};
		$in{'ordertax'} = &calculate_taxes($in{'shp_zip'},$in{'shp_state'},$in{'shp_city'},$in{'id_orders'});

		if(int($in{'id_zones'}) == 0 and length($in{'shp_zip'}) == 5) {
			$in{'id_zones'} = &get_zone_by_zipcode($in{'shp_zip'});
		}
	}

	if($in{'edit'}) {

		if($in{'status'} ne 'Shipped') {
			# No se puede editar una orden si se encuentra en una remesa
			# Can not edit an order if you are in a consignment

			my ($is_editable) = &products_order_vs_product_batch($in{'id_orders'});
			
			if(!$is_editable) {
				++$err;

				my ($sth_id_batch) = &Do_SQL("SELECT ID_warehouses_batches
				FROM sl_orders_products
				LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products)
				LEFT JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				WHERE ID_orders ='$in{'id_orders'}'
				AND (ShpDate IS NOT NULL OR ShpDate != '0000-00-00')
				GROUP BY ID_orders");
				($id_batch) = $sth_id_batch->fetchrow();

				$va{'message'} .= &trans_txt('order_batchsent') . " $id_batch";
			}

			# Se reasigna la zona al editar la orden
			# Zone Assignment
			if(int($in{'id_zones'}) == 0 and length($in{'shp_zip'}) == 5) {
				$in{'id_zones'} = &get_zone_by_zipcode($in{'shp_zip'});
			}
		}


		if(!$err) {

			if($in{'status'} =~ /Processed|Shipped/) {

				my ($sth) = &Do_SQL("SELECT IF(shp_State != '".$in{'shp_state'}."' OR shp_Zip != '".$in{'shp_zip'}."',1,0) FROM sl_orders WHERE ID_orders = '".$in{'id_orders'}."';");
				if($sth->fetchrow == 1){

					if($in{'authcode'} and $in{'authcode'} ne ''){
						
						my ($sth) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4)='".&filter_values($in{'authcode'})."'");
						my ($idorder,$idadmin,$authorization) = split(/,/,$sth->fetchrow,3);
						
						if ($idadmin > 0 or $idorder eq $in{'id_orders'}){

							&recal_order_all($in{'id_orders'},$in{'shp_state'},$in{'shp_city'},$in{'shp_zip'},'orders');
							
							
							&add_order_notes_by_type($in{'id_orders'},&trans_txt('order_shpchange_authorized'),"Low");

							&auth_logging('orders_note_added',$in{'id_orders'});
							## Reinitialize the Value
							my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Auth Order' AND RIGHT(VValue,4)='$in{'authcode'}';");
						
						}else{
							++$err;
							$va{'message'} .= "Invalid authorization code.";
						}
					}else{
						++$err;
						$va{'message'} .= "Invalid authorization code.";
					}
				}

			}
		}
	}

	if ($in{'add'} or $in{'edit'}){
		if (!$in{'ptype'}){
			$error{'ptype'} = &trans_txt('required');
			++$err;
		}
	}
	
	## Fix bug
	$in{'id_zones'} = int($in{'id_zones'});
	
	return $err;
}



sub loaddefault_opr_orders {
# --------------------------------------------------------

	$in{'status'}    = 'New';
	$in{'statuspay'} = 'None';
	$in{'statusprd'} = 'None';
	$in{'id_pricelevels'} = 99;
	$in{'shp_type'} = 1;
	$in{'language'} = 'spanish';

	if ($in{'loadaddress'} and $in{'id_customers'}){

		my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE ID_customers='$in{'id_customers'}' LIMIT 1;");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('Address1','Address2','Address3','Urbanization','City','State','Zip','Country','Pterms');
		for (0..$#cols){
			$in{lc($cols[$_])} = $rec->{$cols[$_]};
			$in{'shp_'.lc($cols[$_])} = $rec->{$cols[$_]};
		}

		if($in{'id_customers_addresses'}) {

			my ($sth) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers='$in{'id_customers'}' AND ID_customers_addresses = '".int($in{'id_customers_addresses'})."'  LIMIT 1;");
			my ($rec) = $sth->fetchrow_hashref;
			my (@cols)= ('Address1','Address2','Address3','Urbanization','City','State','Zip','Country');
			for (0..$#cols){
				$in{'shp_'.lc($cols[$_])} = $rec->{$cols[$_]};
			}
		}
	}

}

#############################################################################
#############################################################################
#   Function: loading_opr_orders
#
#       Es: Se ejecuta antes de cargar el formulario de edició       En: 
#
#
#    Created on: 2013-05-16
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub loading_opr_orders {

	# Obtiene los datos de la sucursal del cliente al mostrar el formulario de edicion, si selecciono una direccion de envio alternativa
	if ($in{'loadaddress'} and $in{'id_customers'} and $in{'id_customers_addresses'}) {

		my ($sth) = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers='$in{'id_customers'}' AND ID_customers_addresses = '".int($in{'id_customers_addresses'})."'  LIMIT 1;");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('Address1','Address2','Address3','Urbanization','City','State','Zip','Country');
		for (0..$#cols){
			$in{'shp_'.lc($cols[$_])} = $rec->{$cols[$_]};
		}

	}

}

#############################################################################
#############################################################################
#   Function: updated_opr_orders
#
#       Es: Se ejecuta despues de modificar una orden
#       En: 
#
#
#    Created on: 2013-03-19
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub updated_opr_orders {
#############################################################################
#############################################################################
	# Update the Zone in Order
	if ($in{'id_orders'}) {
		&update_order_zone($in{'id_orders'});
	}
}

#############################################################################
#############################################################################
#   Function: add_ea_opr_orders
#
#       Es: Se ejecuta despues de agregar una orden. DEjar con el _ea_ ya que hay otra funcion ejecutandose por empresa sin el prefijo
#       En: 
#
#
#    Created on: 2013-03-19
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <add_ea_opr_orders> /cgi-bin/common/subs/e/e3.dbman.pl
#
sub add_ea_opr_orders {
#############################################################################
#############################################################################
	# Update the Zone in Order
	if ($in{'id_orders'}) {
		&update_order_zone($in{'id_orders'});
	}	
}

1;


