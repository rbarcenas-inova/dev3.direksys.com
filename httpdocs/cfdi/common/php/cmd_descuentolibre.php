<?php

	if(preg_match("/ax_validate/",$in['action'],$matches)){ 
		$url_external=$cfg["dlibre_url"];
		$name_external=$cfg["dlibre_name"];
		$idCoupon = trim($_POST["idCoupon"]);
		sleep(1);
		$va["idcoupon"]=$idCoupon;
		 
		#training
		if($cfg["dlibre_training"]=="True"){
		    mysql_select_db("training") or die("Select DB: ".mysql_error());    
		}
		$rstco = mysql_query("SELECT ID_coupons_external FROM sl_coupons_external WHERE  coupon_value='" . mysql_real_escape_string($idCoupon) . "' AND name_external='".$name_external."' AND CURDATE() <= expiration    AND url_external='".$url_external."' AND Status='Active'") or die("Query failed : " . mysql_error());
		$rscoupon = mysql_fetch_assoc($rstco);
		if(isset($rscoupon['ID_coupons_external'])){
			$counter=0;
			$clave_bota = explode("|", $cfg["dlibre_productid"]);
			for($i=0; $i<count($clave_bota);$i++){
			    $counter++;
			    $oproduct = getProductData($clave_bota[$i]);
			    $va['choice'] .= getChoice($clave_bota[$i], $oproduct["Name"], "", $counter,"");
			}
			
			$va["id_count"]=count($clave_bota);
			$va['state'] = getState($selected);
			$va['data_ajax']="cart/coupon_form.html";
		}else{
			$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
			$va['data_ajax']="content/descuentolibre_error.html";
		}
	}elseif(preg_match("/ax_cols/",$in['action'],$matches)){ 
		$firstname = trim($_POST["firstname"]);
		$lastname1 = trim($_POST["lastname1"]);
		$sex = trim($_POST["sex"]);
		$address1 = trim($_POST["address1"]);
		$address2 = trim($_POST["address2"]);
		$state = trim($_POST["state"]);
		$zip = trim($_POST["zip"]);
		$email = trim($_POST["email"]);
		$choice = trim($_POST["choice"]);
		$idproduct = trim($_POST["idproduct"]);
		$phone = trim($_POST["phone"]);
		$password = trim($_POST["password"]);
		$password_confirm = trim($_POST["password_confirm"]);
		$idCoupon = trim($_POST["idCoupon"]);
		$choiceValue = trim($_POST["choiceValue"]);
		
		$id_count = intval($_POST["data_choice"]["id_count"]);
		for($i=1;$i<=$id_count; $i++){
		    $va["id_choice_".$i] = trim($_POST["data_choice"]["choice_".$i]);
		    $va["sel_choice_".$i] = trim($_POST["data_choice"]["selchoice_".$i]);
		}
		
		#training
		if($cfg["dlibre_training"]=="True"){
		    mysql_select_db("training") or die("Select DB: ".mysql_error());
		}
		
		#validate coupon
		$url_external=$cfg["dlibre_url"];
		$name_external=$cfg["dlibre_name"];
		
		$rstco = mysql_query("SELECT ID_coupons_external FROM sl_coupons_external WHERE  coupon_value='" . mysql_real_escape_string($idCoupon) . "' AND name_external='".$name_external."' AND CURDATE() <= expiration    AND url_external='".$url_external."' AND Status='Active'") or die("Query failed : " . mysql_error());
		$rscoupon = mysql_fetch_assoc($rstco);
		if(!isset($rscoupon['ID_coupons_external'])){
		 	$error["couponerror"]="Cup&oacute;n no valido";
		}
 
		$in['firstname']=$firstname;
		$in['lastname1']=$lastname1;
		$in['sex']=$sex;
		$in['address1']=$address1;
		$in['address2']=$address2;
		$in['state']=$state;
		$in['zip']=$zip;
		$in['phone']=$phone;
		$in['choice']=$choice;
		$in["password"]=$password;
		$in["passconfirm"]=$password_confirm;
		$in["email"]=$email;
		$va["idcoupon"]=$idCoupon;
		$va["idproduct"]=$idproduct;
		$va["choicevalue"]=preg_replace("/Â/", "", $choiceValue);
		
	 	#sex
		if($sex=="Male"){
			$va["sextype"]="Hombre";
			$va["male"]="checked='checked'";
		}elseif($sex=="Female"){
			$va["sextype"]="Mujer";
			$va["female"]="checked='checked'";
		}
		
		#pass
		if($password!="" && strlen($password)<6){
			$error["password"] = "<span class='error'>".trans_txt('range_passwd')."</span>";
		}elseif($password!="" && $password_confirm==""){
			$error["password"] = "<span class='error'>Repite la contrasena de acceso</span>";
		}elseif($password!=$password_confirm){
			$error["password"] = "<span class='error'>".trans_txt('invalid_passwd_confirmation')."</span>";
		}
		
		#mask password
		if(strlen($in["password"])>0){
			$va["maskpassw"]="*******";
		}
		
		#Choice
		for($i=1;$i<=$id_count; $i++){
		    if($va["id_choice_".$i]=="--"){
		        $error["choice_".$i] = "<span class='error'>".trans_txt('required')."</span>";
		    }  
		}
 
		#State
		if($state=="--"){
			$error["state"] = "<span class='error'>".trans_txt('required')."</span>";
		}
		
		#validate fields
		$db_cols= array('firstname','lastname1','address1','address2','zip','phone','email','password','state');
		$type=array('','','','','numeric','phone','email','','','');
		$req_cols=array('firstname','lastname1','address1','','zip','phone','email','','state');
	
		# Validate require fields
		$valid=validate_cols($db_cols,$req_cols,$type,"");
	
		//Validate zipcode
		if(!isset($error["zip"])){
			$rstco = mysql_query("SELECT ID_zipcodes FROM sl_zipcodes WHERE ZipCode='" . mysql_real_escape_string($zip) . "' GROUP BY ZipCode") or die("Query failed : " . mysql_error());
			$rspx = mysql_fetch_assoc($rstco);
			if(!isset($rspx['ID_zipcodes'])){
					$error["zip"] = "<span class='error'>".trans_txt('invalid')."</span>";
			}
		}
	
		#Validate phone lengt
		if(!isset($error["phone"])){
			if(strlen($in['phone']) < 10){
				$error["phone"] = "<span class='error'>".trans_txt('invalid')."</span>";
			}
		}
		
		$counter=0;
		$clave_bota = explode("|", $cfg["dlibre_productid"]);
		for($i=0; $i<count($clave_bota);$i++){
		    $counter++;
		    $oproduct = getProductData($clave_bota[$i]);
		    $va['choice'] .= getChoice($clave_bota[$i], $oproduct["Name"], $va["id_choice_".$counter], $counter, $error["choice_".$counter]);
		    $va['hidd_choice'] .= "<input type='hidden' name='id_choice_".$counter."' id='id_choice_".$counter."' value='".$va["id_choice_".$counter]."'>";
		    $va['hidd_selchoice'] .= "<br>".preg_replace("/Â/", "", $va["sel_choice_".$counter]);
		}
		
		$va['state'] = getState($state);
		$va["id_count"]=count($clave_bota);
		
		#error
		if(count($error)>0){
			$va['data_ajax']="cart/coupon_formerror.html";
		}else{#no error
			$va['data_ajax']="cart/coupon_datacheck.html";
		}
	}elseif(preg_match("/ax_update/",$in['action'],$matches)){ 
		$idCoupon = trim($_POST["idCoupon"]);
		$firstname = trim($_POST["firstname"]);
		$lastname1 = trim($_POST["lastname1"]);
		$sex = trim($_POST["sex"]);
		$address1 = trim($_POST["address1"]);
		$address2 = trim($_POST["address2"]);
		$state = trim($_POST["state"]);
		$zip = trim($_POST["zip"]);
		$email = trim($_POST["email"]);
		$phone = trim($_POST["phone"]);
		$password = trim($_POST["password"]);
		$password_confirm = trim($_POST["password_confirm"]);
		
		$in['firstname']=$firstname;
		$in['lastname1']=$lastname1;
		$in['sex']=$sex;
		$in['address1']=$address1;
		$in['address2']=$address2;
		$in['state']=$state;
		$in['zip']=$zip;
		$in['phone']=$phone;
		$in["password"]=$password;
		$in["passconfirm"]=$password_confirm;
		$in["email"]=$email;
		$va["idcoupon"]=$idCoupon;
		
		$id_count = intval($_POST["data_choice"]["id_count"]);
		for($i=1;$i<=$id_count; $i++){
		    $va["id_choice_".$i] = trim($_POST["data_choice"]["choice_".$i]);
		}
		
		#training
		if($cfg["dlibre_training"]=="True"){
		    mysql_select_db("training") or die("Select DB: ".mysql_error());
		}
		
		sleep(1);
		 
		$url_external=$cfg["dlibre_url"];
		$name_external=$cfg["dlibre_name"];
		$rstco = mysql_query("SELECT ID_coupons_external FROM sl_coupons_external WHERE  coupon_value='" . mysql_real_escape_string($idCoupon) . "' AND name_external='".$name_external."' AND CURDATE() <= expiration    AND url_external='".$url_external."' AND Status='Active'") or die("Query failed : " . mysql_error());
		$rscoupon = mysql_fetch_assoc($rstco);
		if(isset($rscoupon['ID_coupons_external']) && is_numeric($rscoupon['ID_coupons_external'])){
		
			#sex
			if($sex=="Male"){
				$va["sextype"]="Hombre";
				$va["male"]="checked='checked'";
			}elseif($sex=="Female"){
				$va["sextype"]="Mujer";
				$va["female"]="checked='checked'";
			}
			 
			$counter=0;
			$clave_bota = explode("|", $cfg["dlibre_productid"]);
			for($i=0; $i<count($clave_bota);$i++){
			    $counter++;
			    $oproduct = getProductData($clave_bota[$i]);
			    $va['choice'] .= getChoice($clave_bota[$i], $oproduct["Name"], $va["id_choice_".$counter], $counter, "");
			}
			
			$va["id_count"]=count($clave_bota);
			$va['state'] = getState($state);
			$va['data_ajax']="cart/coupon_updatedata.html";
		}else{
			$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
			$va['data_ajax']="content/descuentolibre_error.html";
		}
		
	}elseif(preg_match("/ax_order/",$in['action'],$matches)){ 
		$firstname = trim($_POST["firstname"]);
		$lastname1 = trim($_POST["lastname1"]);
		$sex       = trim($_POST["sex"]);
		$address1  = trim($_POST["address1"]);
		$address2  = trim($_POST["address2"]);
		$state     = trim($_POST["state"]);
		$zip       = trim($_POST["zip"]);
		$email     = trim($_POST["email"]);
		$state     = trim($_POST["state"]);
		$phone     = trim($_POST["phone"]);
		$idCoupon  = trim($_POST["idCoupon"]);
		$password  = trim($_POST["password"]);
		#unset($in);
		#unset($cses);
		#unset($va);
		unset($error);
		 
		//training
		if($cfg["dlibre_training"]=="True"){
		    mysql_select_db("training") or die("Select DB: ".mysql_error());
		}else{
		    mysql_select_db($cfg['dbi_db']) or die("Select DB: ".mysql_error());
		}
		
		if(!empty($idCoupon)){
			sleep(1);			
			$url_external=$cfg["dlibre_url"];
			$name_external=$cfg["dlibre_name"];
			
			$rstco = mysql_query("SELECT ID_coupons_external FROM sl_coupons_external WHERE  coupon_value='" . mysql_real_escape_string($idCoupon) . "' AND name_external='".$name_external."' AND CURDATE() <= expiration    AND url_external='".$url_external."' AND Status='Active' FOR UPDATE") or die("Queryx failed : " . mysql_error());
			$rscoupon = mysql_fetch_assoc($rstco);
			if(isset($rscoupon['ID_coupons_external'])){
				$updtCoupon = mysql_query("UPDATE sl_coupons_external  SET Status='Used', Date=CURDATE(), Time=CURTIME() WHERE  ID_coupons_external = " . $rscoupon['ID_coupons_external']) or die("Query failedy : " . mysql_error());
				if($updtCoupon==false){
					$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
					$va['data_ajax']="content/descuentolibre_error.html";
					return;
				}
				
				unset($cses);
				$today=getdate();	
				$va["idcupon"]=$idCoupon;
				$in['cmd']="cart";
				$in['checkout']="1";
				$in['step']="4";
				$in['action']="";
				$in['firstname']=$firstname;
				$in['lastname1']=$lastname1;
				$in['sex']=$sex;
				$in['address1']=$address1;
				$in['address2']=$address2;
				$in['state']=$state;
				$in['zip']=$zip;
				$in['phone']=$phone;
				$in['choice']=$choice;
				$in['btn5_x']="68";
				$in['btn5_y']="18";
				$in['shp_type']="1";
				$in['paytype']="descuentolibre";
				$in['fullquery']="cmd=cart&checkout=1&step=4&action=";
				
				$cses['payments']="1";
				$cses['shp_type']="1"; //tipo de pago
				$cses['random_memorial']="25";
				$cfg['order_status']="Processed"; #status pagado
				
				$counter=0;
				$count_productitem=0;
				$product_prices = explode("|", $cfg["dlibre_productprice"]); # price products
				$product_items = explode("|", $cfg["dlibre_productitem"]); # products items
				$product_id = explode("|", $cfg["dlibre_productid"]); # products items
				$id_count = intval($_POST["data_choice"]["id_count"]);
				
				$cses['items_in_basket'] = $id_count; #items productos
        		
        		for($i=1; $i<=$id_count; $i++){
        		    $aproduct = getProductData($product_id[$counter]);
        		    $va["id_choice_".$i] = trim($_POST["data_choice"]["choice_".$i]);
        		    
        		    $cses['items_'.$i.'_id']=$va["id_choice_".$i];
    				$cses['items_'.$i.'_qty']=$product_items[$counter]; #items por linea de producto
    				$cses['items_'.$i.'_fpago']="1";
    				$cses['items_'.$i.'_payments']="1";
    				$cses['items_'.$i.'_paytype']="Credit-Card-30|COD|paypal|google";
    				$cses['items_'.$i.'_price']=0; //precio
    				$cses['items_'.$i.'_fpprice']=0;
    				$cses['items_'.$i.'_tax']="0";  //total tax calculado
    				$cses['items_'.$i.'_weight']="0.00";
    				$cses['items_'.$i.'_size']="0";
    				$cses['items_'.$i.'_downpayment']="0.00";
    				$cses['items_'.$i.'_desc']=$aproduct["Name"]; //nombre del producto
    				$cses['items_'.$i.'_year']=$today['year'];
    				$cses['items_'.$i.'_month']=trans_txt('mon'.$today['mon']);
    				$cses['items_'.$i.'_day']=$today['mday'];
    				$cses['items_'.$i.'_discount']="0";
    				$cses['items_'.$i.'_shp1'] = 0;
    				$cses['items_'.$i.'_shp2'] = 0;
    				$cses['items_'.$i.'_shp3'] = 0;
    				
    				$count_productitem += $product_items[$counter];
    				$counter++;
        		}
        		
        		$cses['products_in_basket']=$count_productitem;
        		       		 
        		$cses['shipping_total']=$cfg["dlibre_shipping"]; //shipping
				$cses['total_i']=$cfg["dlibre_total"];
				$cses['total_order']=$cfg["dlibre_total"];
					
				$cses['edt']="45";
				$cses['usertype']="new"; //si el susuario es nuevo
				$cses['email']=$email;
				$cses['step1']="done";
				$cses['firstname']=$firstname;
				$cses['lastname1']=$lastname1;
				$cses['sex']=$sex;
				$cses['birthday_month']="00";
				$cses['birthday_day']="00";
				$cses['address1']=$address1;
				$cses['address2']=$address2;
				$cses['address3']="";
				$cses['city']="none";
				$cses['state']=$state;
				$cses['zip']=$zip;
				$cses['shp_address1']=$address1;
				$cses['shp_address2']=$address2;
				$cses['shp_address3']="";
				$cses['shp_city']="none";
				$cses['shp_state']=$state;
				$cses['shp_zip']=$zip;
				$cses['step2']="done";
				$cses['paytype']="descuentolibre";
				$cses['pmtfield6']=$phone;
				$cses['step3']="done";
				$cses['pmtfield1']="Visa"; //tipo tarjeta
				$cses['pmtfield2']=""; //propietario
				$cses['pmtfield3']="descuentolibre.com"; //num tarjeta
				$cses['expmm']="";
				$cses['expyy']="";
				$cses['pmtfield4']="";
				$cses['pmtfield5']="";
				$cses['pmtfield7']="CreditCard";
				$cses['dpio']="0";
					
				$cses['phone1']=$phone;
				$cses['categories']="";
				$cses['dayspay']="1";
			
				$cses['items_discounts']="0";
				$cses['total_disc']="0";
				$cses['fppayments']="1";
				$cses['fppayment1']=$cfg["dlibre_total"];
				 
				#sex
				if($sex=="Male"){
					$va["sextype"]="Hombre";
				}elseif($sex=="Female"){
					$va["sextype"]="Mujer";
				}
					
				$slcdate = mysql_query("SELECT CURDATE() AS CURDATE, CURTIME() AS CURTIME") or die("Query failed : " . mysql_error());
				$rsdate = mysql_fetch_assoc($slcdate);
				if(isset($rsdate['CURDATE'])){
					$cses['fpdate1']  = $rsdate['CURDATE'];
					$va['fpdate1_lib']= $rsdate['CURDATE'];
				}
					
				$tpl['pagetitle']="Innovashop USA : Los mejores productos, como los viste en televisión";
				$tpl['nsFilename']="default.html";
				$tpl['filename']="content/home.html";
					
				#taxes 
				$cses['tax_total']=calculate_taxes($cses['shp_zip'],$cses['shp_state']);

				#Shipping
				#total = total - shipping
				#total = 46.98 - 6.99
				if(isset($cses['shipping_total']) && $cses['shipping_total'] > 0){
				    $va['total_order'] = $cses['total_order'] - $cses['shipping_total'];
				}else{
				    $va['total_order'] = $cses['total_order'];
				}
				
				#subtotal-(subtotal/(1+taxes)) 
				#Taxes 39.99-(39.99/(1+0.065))
				$tax_calc = 0;
				if(isset($cses['tax_total']) && $cses['tax_total'] > 0){
					$tax_calc = $va['total_order'] - ($va['total_order']/(1+$cses['tax_total']));
				}
				
				#Reparte taxes
				$item_tax =0;
				if($tax_calc > 0){
				    $item_tax = $tax_calc/ $cses['products_in_basket'];
				}
                
				$sprice = $cses['total_order'] -  $cses['shipping_total']  - $tax_calc;
				$cses['total_i'] = $sprice; #subtotal
				
				#Reparte el precio
				$item_price=0;
				if($cses['products_in_basket']>0){
				    $item_price = $cses['total_i'] / $cses['products_in_basket'];
				}
					
				
				$item_price_aux = 0;
				$item_tax_aux=0;
				$item_add = 0;
				for ($i=1;$i<=$cses['items_in_basket'];$i++)
				{
				    if ($cses['items_'.$i.'_qty'] > 0  and $cses['items_'.$i.'_id'] > 0)
				    {
				        #producto precios
				        $item_tax_aux = $item_tax * $cses['items_'.$i.'_qty'];
				        $item_price_aux = $item_price * $cses['items_'.$i.'_qty'];
				        $item_add += round($item_price_aux, 2);
				        
				        $cses['items_'.$i.'_price']   = round($item_price_aux, 2); //precio
				        $cses['items_'.$i.'_fpprice'] = round($item_price_aux, 2);
				        $cses['items_'.$i.'_tax']     = round($item_tax_aux, 3);
				    }
				}
				
				#Ajuste de precios de producto
				total_adjust($cses['total_i'], $item_add);
				
				#Agrega shipping al primer producto
				$cses['items_1_shp1'] = $cfg["dlibre_shipping"];
				$cses['items_1_shp2'] = $cfg["dlibre_shipping"];
				$cses['items_1_shp3'] = $cfg["dlibre_shipping"];
				
				if($cses['paytype']=='Credit-Card')
				$req_cols=array('firstname','lastname1','phone1','email','address1','city','state','zip','paytype');
				else if($cses['paytype']=='COD')
				$req_cols=array('firstname','lastname1','phone1','email','address1','city','state','zip','paytype');
				else if($cses['paytype']=='paypal' or $cses['paytype']=='google-checkout')
				$req_cols=array('firstname','lastname1','email','address1','city','state','zip','paytype');

				for ($i = 0; $i < count($req_cols); $i++)
				{
					$col = $req_cols[$i];
					$val = trim($cses[strtolower($col)]);
					if (!$val or $val=='')
					echo ":Missingx fields: $col";
				}

				$ptype = $cses['paytype'];
    			$id_customers=create_customer();
    			
    			$cses['id_customers']=$id_customers;
    			if(!is_numeric($id_customers))
    			echo $id_customers;
    
    			($cses['paytype'] == 'paypal' or $cses['paytype'] == 'google-checkout' or $cses['paytype'] == 'descuentolibre') and ($ptype = 'Credit-Card');
    			$insert = "INSERT INTO sl_orders set ID_customers='$id_customers',Address1='".mysql_real_escape_string($cses['address1'])."',Address2='".mysql_real_escape_string($cses['address2'])."',Address3='".mysql_real_escape_string($cses['address3'])."',Urbanization='".mysql_real_escape_string($cses['urbanization'])."',City='".mysql_real_escape_string($cses['city'])."',State='".mysql_real_escape_string($cses['state'])."',Zip='".mysql_real_escape_string($cses['zip'])."',shp_type='$cses[shp_type]',shp_name='".mysql_real_escape_string($cses['firstname'])." ".mysql_real_escape_string($cses['lastname1'])."',shp_Address1='".mysql_real_escape_string($cses['address1'])."',shp_Address2='".mysql_real_escape_string($cses['address2'])."',shp_Address3='".mysql_real_escape_string($cses['address3'])."',shp_Urbanization='".mysql_real_escape_string($cses['urbanization'])."',shp_City='".mysql_real_escape_string($cses['city'])."',shp_State='".mysql_real_escape_string($cses['state'])."',shp_Zip='".mysql_real_escape_string($cses['zip'])."',Country='".mysql_real_escape_string($cses['country'])."',shp_Country='".mysql_real_escape_string($cses['country'])."',OrderQty=".$cses['items_in_basket'].",OrderShp='$cses[shipping_total]',OrderDisc=0,OrderTax='$cses[tax_total]',OrderNet=".$cses['total_i'].",ID_salesorigins=6,DIDS7='$cfg[dids7]',Ptype='$ptype',StatusPrd='None',StatusPay='None',Status='".$cfg['order_status']."',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$cfg[id_admin_users]'";
    			mysql_query($insert) or die("Query failed : " . mysql_error());
    			$cses[id_orders]=mysql_insert_id();

    			#Producto
    			$item_price_aux = 0;
    			$item_tax_aux = 0;
    			for ($i=1;$i<=$cses['items_in_basket'];$i++)
    			{
        			if ($cses['items_'.$i.'_qty'] > 0  and $cses['items_'.$i.'_id'] > 0)
        			{
        			    $item_price_aux =  $cses['items_'.$i.'_price']; //precio
        			    $item_tax_aux   = $cses['items_'.$i.'_tax']; //tax
        			    
        			    
            			$insert='';
            			($cses['items_'.$i.'_shp'.$cses['shp_type']] == '') and ($cses['items_'.$i.'_shp'.$cses['shp_type']]=0);
            			($cses['items_'.$i.'_fpprice'] == '' or $cses['items_'.$i.'_fpprice'] < $cses['items_'.$i.'_price']) and ($cses['items_'.$i.'_fpprice'] = 0);
            			$insert = "INSERT INTO sl_orders_products set ID_products='".mysql_real_escape_string($cses['items_'.$i.'_id'])."',ID_orders='".mysql_real_escape_string(intval($cses['id_orders']))."',Quantity='".$cses['items_'.$i.'_qty']."', SalePrice=".$item_price_aux.",Shipping='".$cses['items_'.$i.'_shp'.$cses['shp_type']]."',Cost=0,Tax='".$item_tax_aux."',Discount='".$cses['items_'.$i.'_discount']."',FP='".$cses['items_'.$i.'_payments']."',Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users='".$cfg['id_admin_users']."'";
            			 
            			mysql_query($insert) or die("Query failed : " . mysql_error());
            			$id_orders_products=mysql_insert_id();
        			}
    			}

    			// Iserta pago basado en $cses[fppayments]
    			$id_orders_payments=create_payment(1,$cses['total_order']);
    			
    			//add coupon number
    			mysql_query("UPDATE sl_orders_payments  SET AuthCode='".$idCoupon."' WHERE ID_orders_payments=".$id_orders_payments) or die("Query failed : " . mysql_error());
    
    			if(!is_numeric($id_orders_payments)){
    				echo $id_orders_payments;
    			}
				$return .="OK";
    			 
    			mysql_query("insert into sl_orders_notes set ID_orders='".$cses['id_orders']."',notes='Promocion: descuentolibre.com\n Tipo: Descuento\n Coupon: ".$idCoupon."', Type='Ecommerce/Coupon', Date=curdate(),Time=curtime(),ID_admin_users='$cfg[id_admin_users]';") or die("Query failed : " . mysql_error());
    
    			$va["return"]        = $return;
    			$va["tototal_i"]     = format_price($cses['total_i']);
    			$va["totax_total"]   = "(".($cses['tax_total']*100)."%)";
    			$va["totax"]         = format_price($tax_calc);
    			$va["shipping_total"]= format_price($cses['shipping_total']);
    			$va["total_order"]   = format_price($cses['total_order']);
    			$va["fpdate_lib"]    = sqldate_plus(date("Y-m-d"),$cfg['cod_payday']);
    			
    			sendFinalEmail($response);
    			$va['data_ajax']="cart/coupon_order.html";
    			setcookie('ps', 'Off',0,'/');
			}else{
				$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
				$va['data_ajax']="content/descuentolibre_error.html";
			}
		}else{
			$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
			$va['data_ajax']="content/descuentolibre_error.html";
		}
	}	
	else{
		$error["couponerror"]="El Cup&oacute;n no es valido intente de nuevo por favor";
		$va['data_ajax']="content/descuentolibre_error.html";
	}
	
	function getChoice($clave_bota, $name, $selected, $counter, $vaerror){
		#Choice
		$rstcolor =  mysql_query("SELECT  ID_sku_products,ID_parts,choice1,choice2,sum(Quantity) as Quantity
													FROM sl_warehouses_location
													INNER JOIN
													(
    													SELECT sl_skus.ID_sku_products,400000000+ID_parts AS ID_parts,choice1 AS choice1,choice2
    													FROM sl_skus inner join sl_skus_parts
    													USING(ID_sku_products)
    													WHERE sl_skus.ID_products='".mysql_real_escape_string($clave_bota)."'
    													AND sl_skus.Status='Active'
    													GROUP BY sl_skus.ID_sku_products
													)tmp
													on(ID_parts=ID_products)
													WHERE ID_warehouses=1039 AND Quantity!=0 AND Quantity >10
													GROUP BY ID_sku_products
													ORDER BY choice2,choice1 ") or die("Query failed : " . mysql_error());
		
		
		if(mysql_num_rows($rstcolor)){
			$options.="<option value='--'>---</option>";
			while( $Set = mysql_fetch_array($rstcolor) ){
				$str="";
				if($selected==$Set[0]){
					$str="selected";
				}
				$options .="<option ".$str." value='".$Set[0]."'>Color: ".$Set[2]."&nbsp;&nbsp;&nbsp;Talla: ".$Set[3]."</option>";
			}
			$header = "<br>(".$clave_bota.") ".$name."<br><select id='choice_".$counter."' class='inputbox'   onblur='focusOff( this )' onfocus='focusOn( this )' name='choice_".$counter."' style='background-color: rgb(255, 255, 255); cursor: pointer;'>";
			$side   ="</select>".$vaerror;
		}mysql_free_result($rstcolor);
		return $header.$options.$side;
	}
	
	function getState($selected){
		#State
		$rststate = mysql_query("select DISTINCT(State) from sl_orders") or die("Query failed : " . mysql_error());
		if(mysql_num_rows($rststate)){
			$optionstate="<option value='--'>---</option>";
			while( $Setstate = mysql_fetch_array($rststate) ){
				if(!empty($Setstate[0])){
					$str="";
					if($selected==$Setstate[0]){
						$str="selected";
					}
					$optionstate .="<option ".$str." value='".$Setstate[0]."'>".$Setstate[0]."</option>";
				}
			}
			$headerstate ="<select id='state' class='inputbox'  onblur='focusOff( this )' onfocus='focusOn( this )' name='state' style='background-color: rgb(255, 255, 255); cursor: pointer;'>";
			$sidestate   ="</select>";
		}mysql_free_result($rststate);
		return $headerstate.$optionstate.$sidestate;
	}
	
	function getProductData($clave_bota){
	    $sql ="
	    					Select
	    					*
	    					from
	    					(Select
	    							if(not isnull(sl_products_prior.SPrice) and sl_products_prior.SPrice != 0 and sl_products_prior.SPrice != '', sl_products_prior.SPrice, sl_products.SPrice) as SPrice,
	    							if(not isnull(sl_products_prior.MemberPrice) and sl_products_prior.MemberPrice > 0, sl_products_prior.MemberPrice, sl_products.MemberPrice) as MemberPrice,
	    							if(not isnull(sl_products_prior.Status) and sl_products_prior.Status != '', sl_products_prior.Status, sl_products.Status) as Status,
	    							if(not isnull(sl_products_w.Title) and sl_products_w.Title != '', sl_products_w.Title, if(not isnull(sl_categories.Title), sl_categories.Title, 'Otro')) as Title,
	    							sl_products.ID_products,
	    							if(not isnull(sl_products_prior.Name) and sl_products_prior.Name != '', sl_products_prior.Name, sl_products.Name) as Name,
	    							if(not isnull(sl_products_w.Name), sl_products_w.Name, 'Other') as Name_link,
	    							if(not isnull(sl_products_prior.Model) and sl_products_prior.Model != '', sl_products_prior.Model, sl_products.Model) as Model,
	    							if(not isnull(sl_products_prior.SmallDescription) and sl_products_prior.SmallDescription != '', sl_products_prior.SmallDescription, sl_products.SmallDescription) as SmallDescription,
	    							if(not isnull(sl_products_prior.Description) and sl_products_prior.Description != '', sl_products_prior.Description, sl_products.Description) as Description,
	    							if(not isnull(sl_products_prior.Weight) and sl_products_prior.Weight != 0 and sl_products_prior.Weight != '', sl_products_prior.Weight, sl_products.Weight) as Weight,
	    							if(not isnull(sl_products_prior.SizeW) and sl_products_prior.SizeW != 0 and sl_products_prior.SizeW != '', sl_products_prior.SizeW, sl_products.SizeW) as SizeW,
	    							if(not isnull(sl_products_prior.SizeH) and sl_products_prior.SizeH != 0 and sl_products_prior.SizeH != '', sl_products_prior.SizeH, sl_products.SizeH) as SizeH,
	    							if(not isnull(sl_products_prior.SizeL) and sl_products_prior.SizeL != 0 and sl_products_prior.SizeL != '', sl_products_prior.SizeL, sl_products.SizeL) as SizeL,
	    							if(not isnull(sl_products_prior.Flexipago) and sl_products_prior.Flexipago != 0, sl_products_prior.Flexipago, sl_products.Flexipago) as Flexipago,
	    							0 as FPPrice,
	    							if(not isnull(sl_products_prior.PayType) and sl_products_prior.PayType != '', sl_products_prior.PayType, sl_products.PayType) as PayType,
	    							if(not isnull(sl_products_prior.edt) and sl_products_prior.edt != 0 and sl_products_prior.edt != '', sl_products_prior.edt, sl_products.edt) as edt,
	    							if(not isnull(sl_products_prior.ID_packingopts) and sl_products_prior.ID_packingopts != 0 and sl_products_prior.ID_packingopts != '', sl_products_prior.ID_packingopts, sl_products.ID_packingopts) as ID_packingopts,
	    							if(not isnull(sl_products_prior.Downpayment) and sl_products_prior.Downpayment != 0 and sl_products_prior.Downpayment != '', sl_products_prior.Downpayment, sl_products.Downpayment) as Downpayment,
	    							if(not isnull(sl_products_prior.ChoiceName1) and sl_products_prior.ChoiceName1 != '', sl_products_prior.ChoiceName1, sl_products.ChoiceName1) as ChoiceName1,
	    							if(not isnull(sl_products_prior.ChoiceName2) and sl_products_prior.ChoiceName2 != '', sl_products_prior.ChoiceName2, sl_products.ChoiceName2) as ChoiceName2,
	    							if(not isnull(sl_products_prior.ChoiceName3) and sl_products_prior.ChoiceName3 != '', sl_products_prior.ChoiceName3, sl_products.ChoiceName3) as ChoiceName3,
	    							if(not isnull(sl_products_prior.ChoiceName4) and sl_products_prior.ChoiceName4 != '', sl_products_prior.ChoiceName4, sl_products.ChoiceName4) as ChoiceName4,
	    							if(not isnull(sl_products_prior.web_available) and sl_products_prior.web_available != '', sl_products_prior.web_available, sl_products.web_available) as web_available,
	    							maxqty
	    							from
	    							sl_products
	    							left join sl_products_prior ON (sl_products.ID_products = sl_products_prior.ID_products)
	    							inner join sl_products_w ON (sl_products.ID_products = sl_products_w.ID_products)
	    							left join sl_products_categories ON (sl_products.ID_products = sl_products_categories.ID_products)
	    							left join sl_categories ON (sl_products_categories.ID_categories = sl_categories.ID_categories)
	    							where
	    							(((sl_products.Status = 'On-Air' AND sl_products.web_available = 'Yes') OR sl_products.Status = 'Web Only') and ((sl_products_prior.belongsto = 'innovashop' or isnull(sl_products_prior.belongsto)) and (sl_products_w.belongsto = 'innovashop')))) as sl_products
	    							where
	    							1 and  ID_products =
	    					'".$clave_bota."'";
	    $rstproduc = mysql_query($sql)  or die("Query failed : " . mysql_error());
	    return mysql_fetch_assoc($rstproduc);
	}
	
	#Ajusta el shipping para el subtotal
	function total_adjust($subtotal, $price){
	    global $cses;
	    
	    $product_price = 0;
	    $diff=0;
	    if($subtotal!=$price){
	        if($subtotal>$price){
	            $diff = doubleval($subtotal)-doubleval($price);
	            if(isset($cses['items_1_price'])){//suma la diferencia al primer producto
	                $product_price = doubleval($cses['items_1_price']) + doubleval($diff);
	                $cses['items_1_price'] = $product_price; //nuevo precio
	                $cses['items_1_fpprice'] = $product_price; 
	            }      	                        
	        }elseif($subtotal<$price){
	            $diff = doubleval($price)-doubleval($subtotal);
	            if(isset($cses['items_1_price'])){//resta la diferencia al primer producto
	                $product_price = doubleval($cses['items_1_price']) - doubleval($diff);
	                $cses['items_1_price'] = $product_price; //nuevo precio
	                $cses['items_1_fpprice'] = $product_price; 
	            }
	        }
	    }
	}
?>
