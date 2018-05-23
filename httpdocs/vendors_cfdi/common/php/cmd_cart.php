<?php

	//Parte de agregación, edición, eliminación, etc para el cart
	if(preg_match("/cart_update/",$in['action'],$matches)){
		foreach($in as $key=>$value)
			if(preg_match("/qty_(\d*)/",$key,$matches))
				if(is_numeric($value)===TRUE)
					$cses['items_'.$matches[1].'_qty']=$value;
		update_cart_session();
		save_callsession(0);
	}elseif(preg_match("/delete_(\d*)/",$in['action'],$matches)){
		$in['do']=$matches[1];
		drop_item();
		update_cart_session();
		verify_discount();
		verify_gifts();
		verify_reward_points();
		//verify_freeshp_bytotals();
		save_callsession(0);
	}elseif(preg_match("/exchange_(\d*)_(\d*)/",$in['action'],$matches)){
		$in['do']=$matches[1];
		#print_r($in);
		$cses['items_'.$in['do'].'_id']=$matches[2];
		update_cart_session();
		save_callsession(0);
	}elseif(preg_match("/exchange_(\d*)/",$in['action'],$matches)){
		$in['do']=$matches[1];
		#print_r($in);
		$cses['items_'.$in['do'].'_id']=$in['id_products_exchange'];
		update_cart_session();
		save_callsession(0);
	}elseif($in['action']=='cart_add'){
// 		$band_exists=0;
// 		for ($i=1;$i<=$cses[items_in_basket];$i++){
// 			if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
// 				if(substr($cses['items_'.$i.'_id'],3,6)==$in[id_products] and($in[choicename1]=='' and $in[choicename2]=='' and $in[choicename3]=='' and $in[choicename4]==''))
// 					$band_exists=$i;
// 			}
// 		}
// 		if($band_exists==0)
// 		++$cses[items_in_basket];
// 		else
// 			$cses[items_in_basket]=$band_exists;
		if($in['id_products']!='')
			$in['product']=$in['id_products'];
		if($in[do_product]==1 or 1)
		  if(do_for_one_product()==-1)
		  	return;
		if(is_numeric($in['quantity']) and $in['quantity']!=0){
			$band_error=0;
		    set_data_profiler($cfg['prof_itemcart'], $in['id_products']);
			for($j=1;$j<=$in['quantity'] and $band_error==0;$j++){
				if(validate_qty()==1)
				{
					++$cses['items_in_basket'];
					++$cses['products_in_basket'];
					//if(($in[choicename1]=='' and $in[choicename2]=='' and $in[choicename3]=='' and $in[choicename4]==''))
					if(build_edit_choices_module($in['id_products'],'','','')==''){
						$cses['items_'.$cses['items_in_basket'].'_id']="100$in[id_products]";
					}else{
						$cses['items_'.$cses['items_in_basket'].'_id']="999$in[id_products]";
					}
					//$cses['items_'.$cses[items_in_basket].'_qty']+=$in[quantity];
					$cses['items_'.$cses['items_in_basket'].'_qty']+=1;
					$cses['items_'.$cses['items_in_basket'].'_fpago']=$in['flexipago'];
					$cses['items_'.$cses['items_in_basket'].'_fpprice']=$in['fpprice'];
					$cses['items_'.$cses['items_in_basket'].'_payments']=1;
					$cses['items_'.$cses['items_in_basket'].'_paytype']=$in['paytype'];
					$cses['items_'.$cses['items_in_basket'].'_price']=$in['sprice'];
					$cses['items_'.$cses['items_in_basket'].'_weight']=$in['weight'];
					$cses['items_'.$cses['items_in_basket'].'_size']=$in['size'];
					$cses['items_'.$cses['items_in_basket'].'_downpayment']=$in['downpayment'];
					$cses['items_'.$cses['items_in_basket'].'_desc']=$in['model'];
					
					$today=getdate();
					$cses['items_'.$cses['items_in_basket'].'_year']=$today['year'];
					$cses['items_'.$cses['items_in_basket'].'_month']=trans_txt('mon'.$today['mon']);
					$cses['items_'.$cses['items_in_basket'].'_day']=$today['mday'];
					
					if($cses['items_'.$cses['items_in_basket'].'_fpprice']==0)
						$cses['items_'.$cses['items_in_basket'].'_fpprice']=$cses['items_'.$cses['items_in_basket'].'_price'];
					
					//Calcular shipping
					//insertar edt
					if(!isset($in['edt'])){
						$in['edt']=3;
					}
					if($in['edt']>$cses['edt']){
						$cses['edt']=$in['edt'];
					}
					
					## By Table?
					$shpcal = load_name('sl_products','ID_products',$in['id_products'],'shipping_table');
					$shpmdis = load_name('sl_products','ID_products',$in['id_products'],'shipping_discount');
					$shpcalp = load_name('sl_products_prior','ID_products',$in['id_products'],'shipping_table');
					
					if($shpcalp != ''){
						$shpcal = $shpcalp;
						$shpmdis = load_name('sl_products_prior','ID_products',$in['id_products'],'shipping_discount');
					}
					
					$shippings=itemshipping($cses['edt'],$cses['items_'.$cses['items_in_basket'].'_size'],1,1,$cses['items_'.$cses['items_in_basket'].'_weight'],$in['id_packingopts'],$shpcal,$shpmdis,$in['id_products']);
					$cses['items_'.$cses['items_in_basket'].'_shp1']=$shippings[0];
					$cses['items_'.$cses['items_in_basket'].'_shp2']=$shippings[1];
					$cses['items_'.$cses['items_in_basket'].'_shp3']=$shippings[2];
					
					//Calcular tax
					$cses['items_'.$cses['items_in_basket'].'_tax']=($cses['items_'.$cses['items_in_basket'].'_price']-$cses['items_'.$cses['items_in_basket'].'_discount']-$cses['items_'.$cses['items_in_basket'].'_coupon_discount'])*$cses['items_'.$cses['items_in_basket'].'_qty']*$cses['tax_total'];

					//2x1 Promotion
					if(!empty($cfg['is2x1_valid']) and (stripos($cfg['products2x1'],$in['id_products'])!==false or (!empty($cfg['productsnot2x1']) and stripos($cfg['productsnot2x1'],$in['id_products'])===false)) and $in['sprice'] >= $cfg['products2x1_minprice'] ){
						++$cses['items_in_basket'];
						++$cses['products_in_basket'];
						//if(($in[choicename1]=='' and $in[choicename2]=='' and $in[choicename3]=='' and $in[choicename4]==''))
						if(build_edit_choices_module($in['id_products'],'','','')==''){
							$cses['items_'.$cses['items_in_basket'].'_id']="100$in[id_products]";
						}else{
							$cses['items_'.$cses['items_in_basket'].'_id']="999$in[id_products]";
						}
						//$cses['items_'.$cses[items_in_basket].'_qty']+=$in[quantity];
						$cses['items_'.$cses['items_in_basket'].'_qty']+=1;
						$cses['items_'.$cses['items_in_basket'].'_fpago']=$in['flexipago'];
						$cses['items_'.$cses['items_in_basket'].'_fpprice']=$cfg['second_item_price'];
						$cses['items_'.$cses['items_in_basket'].'_payments']=1;
						$cses['items_'.$cses['items_in_basket'].'_paytype']=$in['paytype'];
						$cses['items_'.$cses['items_in_basket'].'_price']=$cfg['second_item_price'];
						$cses['items_'.$cses['items_in_basket'].'_weight']=$in['weight'];
						$cses['items_'.$cses['items_in_basket'].'_size']=$in['size'];
						$cses['items_'.$cses['items_in_basket'].'_downpayment']=$in['downpayment'];
						$cses['items_'.$cses['items_in_basket'].'_desc']=$in['model'];
						$cses['items_'.$cses['items_in_basket'].'_free']=1;
						
						$today=getdate();
						$cses['items_'.$cses['items_in_basket'].'_year']=$today['year'];
						$cses['items_'.$cses['items_in_basket'].'_month']=trans_txt('mon'.$today['mon']);
						$cses['items_'.$cses['items_in_basket'].'_day']=$today['mday'];
						
						if($cses['items_'.$cses['items_in_basket'].'_fpprice']==0)
							$cses['items_'.$cses['items_in_basket'].'_fpprice']=$cses['items_'.$cses['items_in_basket'].'_price'];


						$cses['items_'.$cses['items_in_basket'].'_shp1']=0;
						$cses['items_'.$cses['items_in_basket'].'_shp2']=0;
						$cses['items_'.$cses['items_in_basket'].'_shp3']=0;

					/*
						//Calcular shipping
						//insertar edt
						if(!isset($in['edt'])){
							$in['edt']=3;
						}
						if($in['edt']>$cses['edt']){
							$cses['edt']=$in['edt'];
						}
						
						## By Table?
						$shpcal = load_name('sl_products','ID_products',$in['id_products'],'shipping_table');
						$shpmdis = load_name('sl_products','ID_products',$in['id_products'],'shipping_discount');
						$shpcalp = load_name('sl_products_prior','ID_products',$in['id_products'],'shipping_table');
						
						if($shpcalp != ''){
							$shpcal = $shpcalp;
							$shpmdis = load_name('sl_products_prior','ID_products',$in['id_products'],'shipping_discount');
						}
						
						$shippings=itemshipping($cses['edt'],$cses['items_'.$cses['items_in_basket'].'_size'],1,1,$cses['items_'.$cses['items_in_basket'].'_weight'],$in['id_packingopts'],$shpcal,$shpmdis,$in['id_products']);
						$cses['items_'.$cses['items_in_basket'].'_shp1']=$shippings[0];
						$cses['items_'.$cses['items_in_basket'].'_shp2']=$shippings[1];
						$cses['items_'.$cses['items_in_basket'].'_shp3']=$shippings[2];
					*/
					
						$cses['items_'.$cses['items_in_basket'].'_discount']=$cses['items_'.$cses['items_in_basket'].'_price']-$cfg['second_item_price'];
						$cses['items_'.($cses['items_in_basket']-1).'_relid']=$cses['items_in_basket'];
						
						//Calcular tax
						$cses['items_'.$cses['items_in_basket'].'_tax']=($cses['items_'.$cses['items_in_basket'].'_price']-$cses['items_'.$cses['items_in_basket'].'_discount']-$cses['items_'.$cses['items_in_basket'].'_coupon_discount'])*$cses['items_'.$cses['items_in_basket'].'_qty']*$cses['tax_total'];
					}
				}
				else
				{
					$in['message']=trans_txt('itemnotadded')."<br>";
					$band_error=1;
				}
			}
			if($band_error==0)
			{
				$in['message']=trans_txt('itemadded')."<br>";
				update_cart_session();
				## Cupon para agregar producto automatico a la orden en el step3
				if(array_key_exists('coupon_to_apply',$in) and strlen($in['coupon_to_apply']) == 16){
						$cses['coupon_to_apply'] = $in['coupon_to_apply'];
						unset($in['coupon_to_apply']);
						$in['message'] .= trans_txt('coupon_to_apply_text')."<br><br>";
				}
				save_callsession(0);
			}
		}
		unset($in['action']);
	}
	
	#(!isset($cses['pmtfield4'])) and ($cses['pmtfield4']=$cses['expmm'].$cses['expyy']);
	if($in['cmd']=='cart' and $in['checkout']==1){
		if (!$cses['products_in_basket']){
  			$tpl['skel']="cart_product.html";
			$in['message']=trans_txt("empty_cart");
			$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
			$tpl['filename']="/cart/content/no_product.html";
			return;
		}
		
		#Verifica que no haya productos sin choices
		$wchoice=check_products_wochoices();
		if($wchoice!=0){
			$in[wchoice]=$wchoice;
			$in['message'] = trans_txt('wchoice').build_edit_choices_module(substr($cses['items_'.$wchoice.'_id'],3),"index.php","cmd=cart&step=$in[step]&to_do=drop&do=$wchoice&checkout=1#tabs","tabchoice$wchoice","<img src='/images/help.png' title='Elegir' alt='' border='0'></td></table></td></table><br>");
			show_cart();
			return;
		}

		if(stristr($in['cmd'],"ppresponse") !== "FALSE"){
			for($stepc=1;$stepc < $in['step'] ;$stepc++){
				$cses['step'.$stepc] = 'done';
 			}
		}


		//Verifica que el paso anterior ya esté hecho.
 		$bandcont=0;
 		for($stepc=1;$stepc<$in['step'] and $bandcont==0;$stepc++){
 			if($cses['step'.$stepc]!='done'){
 				$bandcont=1;
 			}
 		}
 		if($bandcont==1){
 			$in['step']=$stepc-1;
		}
		
		$cmdname = "checkout_step".$in['step'];
		if (function_exists($cmdname)){
			$rep_str = $cmdname();
		}
		
		$tpl['pagetitle'] = trans_txt("step".$in['step']."cart");
		$tpl['filename']="cart/content/checkout_step".$in['step'].".html";
		($in['step'] == 4 and ($in['paytype'] == 'paypal' or $cses['paytype'] == 'paypal')) and ($tpl['filename'] = "cart/content/checkout_step".$in['step']."_noedit.html");
		if($in['step'] == 4 and ($in['paytype'] == 'paypal' or $cses['paytype'] == 'paypal') and (!isset($usr['id_customers']) or $usr['id_customers'] == 0 ) /*and !isset($in['skip_shipinfo_paypal']) and !isset($cses['skip_shipinfo_paypal'])*/){
			$in['ask_customer'] = 'checkout_step4_askcustomer.html';
			if(!isset($in['ask_email']) or strlen($in['ask_email']) < 6){
				$in['ask_email'] = $cses['email'];
			}
		}
		//if ($in[step]>=2){
			$tpl[skel]="cart_product.html";
// 		}else{
// 			$tpl[skel]="cart_product.html";
// 		}
		update_cart_session();
		save_callsession(0);
		
	}elseif($in['cmd']=='cart' and $in['view_cart']==1){
		
		##############################################################
		######################Show cart###############################
		##############################################################
		
		show_cart();
		return;
	}elseif($in['cmd']=='cart'){
		show_cart();
		#do_search();
	}elseif($in['log-in']==1){
		load_object('/skeleton/admincart.html');
	}

	//$va['cart_image']	= load_cartimage();


function checkout_step1(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/07/10 13:02:44
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 08/06/2010 : Se agrega template con informacion de bloqueo de PayPal y Google
//Last modified on 2 Mar 2011 15:27:36
//Last modified by: MCC C. Gabriel Varela S. :Se agrega Birthday
//Last modified on 3/21/11 11:42 AM
//Last modified by: MCC C. Gabriel Varela S. :Se cambia birthday por combos

	global $cfg,$cses,$va,$in,$error,$usr,$message;

    set_data_profiler($cfg['prof_email'], $in['email']);
	//PayPal - Google Permitidos?
	$cadpaytypes = paytypes_for_products();

	$va['paypal_google_allowed'] = (($cfg['paytypespaypal'] == 1 or $cfg['paytypesgoogle'] == 1) and preg_match("/paypal|google/i",$cadpaytypes)) ? 'checkout_paypal_google.html' : 'checkout_paypal_google_blocked.html';

	//Validaciones
	$prefix='';
	$is_customer=0;
	$db2_cols= array('firstname','lastname1','birthday_month','birthday_day','address1','address2','address3','city','state','zip');
	#print_r($usr);

	## Si usuario viene de step4
	if($cses['step3'] == 'done' and isset($in['edit_cfn']) and $in['edit_cfn'] == 1){
		$in['firstname']	=    $cses['firstname'];
		$in['lastname1']	=    $cses['lastname1'];
		if(isset($cses['birthday_month'])and $cses['birthday_month']!='' and isset($cses['birthday_day'])and $cses['birthday_day']!='')
		{
			$in['birthday_month']	=    $cses['birthday_month'];
			$in['birthday_day']	=    $cses['birthday_day'];
			$in['birthday']='2011-'.$cses['birthday_month'].'-'.$cses['birthday_day'];
		}
		for($i = 0; $i < 2; $i++){
			if($i > 0){ $prefix='shp_';}
			$in[$prefix . 'address1'] = $cses[$prefix . 'address1'];
			$in[$prefix . 'address2'] = $cses[$prefix . 'address2'];
			$in[$prefix . 'address3'] = $cses[$prefix . 'address3'];
			$in[$prefix . 'city'] = $cses[$prefix . 'city'];
			$in[$prefix . 'state'] = $cses[$prefix . 'state'];
			$in[$prefix . 'zip'] = $cses[$prefix . 'zip'];
		}

	## Si usuario estaba logueado
	}elseif($usr['id_customers'] > 0){
		$in['firstname']	=    $usr['firstname'];
		$in['lastname1']	=    $usr['lastname1'];
		if(isset($usr['birthday_month']) and $usr['birthday_month']!='' and isset($usr['birthday_day']) and $usr['birthday_day']!='')
		{
			$in['birthday_month']	=    $usr['birthday_month'];
			$in['birthday_day']	=    $usr['birthday_day'];
			$in['birthday']='2011-'.$usr['birthday_month'].'-'.$usr['birthday_day'];
		}
		for($i = 0; $i < 2; $i++){
	  		if($i > 0){ $prefix='shp_';}
			$in[$prefix . 'address1']= $usr[$prefix . 'address1'];
			$in[$prefix . 'address2']= $usr[$prefix . 'address2'];
			$in[$prefix . 'address3']= $usr[$prefix . 'address3'];
			$in[$prefix . 'city']= $usr[$prefix . 'city'];
			$in[$prefix . 'state']= $usr[$prefix . 'state'];
			$in[$prefix . 'zip']= $usr[$prefix . 'zip'];
		}
		$cses['usertype']='member';
		$cses['email']=$usr['email'];
		$cses['id_customers']=$usr['id_customers'];
		$cses['step1']='done';
		$in['step']='2';

	## Si usuario viene de step1 (formulario de acceso)
	}elseif(isset($in['btn1_x'])){
		## IF user comes from inside the form
		if($in['usertype']=='member'){
			$db_cols= array('email','usertype','password');
			$type=array('email','','');
			$req_cols=array('email','usertype','password');
		}else{
			$db_cols= array('email','usertype');
			$type=array('email','','email');
			$req_cols=array('email','usertype');
		}
		$valid=validate_cols($db_cols,$req_cols,$type,0);
		
		if(isset($in['email']) and $in['email'] != ''){
			$sth = mysql_query("Select IF(Password IS NOT NULL AND Password!='',1,2)AS tcustomer from sl_customers WHERE email='".filter_values($in[email])."';");
			if($sth and mysql_num_rows($sth) > 0){
				$is_customer = mysql_result($sth,0);
			}
		}
			
		if ($in['usertype'] !='member' and $is_customer == 1){
			$va{'message'} = trans_txt('alreadymember');
			$valid="error";
		}elseif($in['usertype'] !='member' and $is_customer == 2){
			header("Location:/mypassword-D");
		}
			
		if($valid=="error"){
			$in['step']='1';
			return;
		}else{
			//si es guest
			if(isset($in['usertype']) and $in['usertype'] != 'member'){
				$cses['usertype']=$in['usertype'];
				$cses['email']=$in['email'];
				$cses['step1']='done';
				$in['step']='2';
				for ($i = 0; $i < count($db2_cols); $i++){
					$col = $db2_cols[$i];
					$in[$col] = $cses[$col];
				}
				return;

			//si es member
			}elseif(isset($in['usertype']) and $in['usertype'] == 'member'){
			
				if(start_login($in['email'],$in['password'])=='ok'){
					if($in['step2']!='done'){
						$in[$prefix . 'firstname'] = $usr['firstname'];
						$in[$prefix . 'lastname1'] = $usr['lastname1'];
						if(isset($usr['birthday_month'])and $usr['birthday_month']!='' and isset($usr['birthday_day'])and $usr['birthday_day']!='')
						{
							$in[$prefix . 'birthday_month'] = $usr['birthday_month'];
							$in[$prefix . 'birthday_day'] = $usr['birthday_day'];
							$in[$prefix . 'birthday'] = '2011-'.$usr['birthday_month'].'-'.$usr['birthday_day'];
						}
	                	
						for($i = 0; $i < 2; $i++){
							if($i > 0){ $prefix='shp_';}
							$in[$prefix . 'address1'] = $usr['address1'];
							$in[$prefix . 'address2'] = $usr['address2'];
							$in[$prefix . 'address3'] = $usr['address3'];
							$in[$prefix . 'city'] = $usr['city'];
							$in[$prefix . 'state'] = $usr['state'];
							$in[$prefix . 'zip'] = $usr['zip'];
						}
					}
					$cses['usertype'] = $in['usertype'];
					$cses['email'] = $in['email'];
					$cses['id_customers'] = $usr['id_customers'];
					$cses['step1'] = 'done';
					$in['step'] = '2';
            		
					for ($i = 0; $i < count($db_cols); $i++){
						$col = $db_cols[$i];
						$in[$col] = $cses[$col];
					}
					return;
				}else{
					$in['step'] = '1';
					$va['message'] = trans_txt('user_not_found');
					return;
				}
			}
			$cses['usertype']=$in['usertype'];
			$cses['email']=$in['email'];
		}

	## Si usuario Viene de step1 (paypal expresscheckout)
	}elseif(isset($in['subcmd']) and $in['subcmd'] == 'paypal'){
		$cses['usertype'] = 'guest';
		$cses['paytype'] = 'paypal';
		require("cmd_paypal_flow1_step1.php");
	}
}

function checkout_step2(){
# --------------------------------------------------------
//Last modified on 2 Mar 2011 15:57:24
//Last modified by: MCC C. Gabriel Varela S. :Se agrega birthday
//Last modified on 3/21/11 11:48 AM
//Last modified by: MCC C. Gabriel Varela S. :Se cambia birthday por combos
	global $cfg,$cses,$in,$va,$usr,$error;

	$db_cols= array('firstname','lastname1','sex','birthday_month','birthday_day','address1','address2','address3','city','state','zip');
	$type=array('','','','','','','','','','','numeric');
	$req_cols=array('firstname','lastname1','','','','address1','','','city','state','zip');

	if ($in['btn2_x']){
		$error['message'] = trans_txt('reqfields_short');
	}else{
		for ($i = 0; $i < count($db_cols); $i++){
			$col = $db_cols[$i];
			$in[$col] = $cses[$col];
		}
	}
	# Validate require fields
	$valid=validate_cols($db_cols,$req_cols,$type,1);
	
	## 
	$cses['shp_address1']	=	$in['address1'];
	$cses['shp_address2']	=	$in['address2'];
	$cses['shp_address3']	=	$in['address3'];
	$cses['shp_city']		=	$in['city'];
	$cses['shp_state']	=	$in['state'];
	$cses['shp_zip']		=	$in['zip'];
	($cses['paytype']) ? $in['paytype'] = $cses['paytype'] :  $in['paytype']='Credit-Card';
#print_r($in);
/* Deshabilitado 2011-05-27	


	# Validate zipcode vs city 
	$sth = mysql_query("SELECT * FROM sl_zipcodes WHERE ZipCode='".mysql_real_escape_string($in[zip])."' AND PrimaryRecord='P';");
	if(mysql_num_rows($sth) > 0){	
		$tmp = mysql_fetch_assoc($sth);
		$dbState = $tmp['State'] . '-' . $tmp['StateFullName'];
      
		## Zipcode/City did not match
		if (strtolower($tmp['City']) != strtolower($in['city']) or $dbState != $in['state']){
			$in['city'] 	= 	ucwords(strtolower($tmp['City']));
			$in['state'] 	= 	$dbState;
			$valid="error";
			$error['message']	= trans_txt('zipcode_unmatch');
		}
    
	## Zipcode unknown
	}else{
		$valid="error";
		$error['message']	= trans_txt('zipcode_unknown');	
	}		
 */ 
  
	($in['sex']=='Male')?	$va['sex']= trans_txt('male')	: $va['sex']= trans_txt('female');
	## Step 2 got errors, Showing same step
	if($valid=="error"){
		$in['step']='2';
		return;
	}elseif ($in['btn4_x']){
		$cses['gotoend']=1;
		$in['step']='2';
		return;
	}elseif ($cses['gotoend']){
		$cses['gotoend'] = 0;
		update_cart_session();
		if($cses['step3']=='done'){
			$in['step']='4';
			$va['products_inorder']	= products_inorder();
			($cses['paytype'] == 'Credit-Card') and ($va['step4_msg'] = trans_txt('info_step_confirm_cc'));
		}else{
			$in['step']='3';
			display_paytypesav();
		}
	}else{
		$db_cols= array('paytype','pmtfield1','pmtfield2','pmtfield3','expmm','expyy','pmtfield5','pmtfield6','pmtfield7');
		#$db_cols= array('paytype','pmtfield1','pmtfield2','creditcard','expmm','expyy','pmtfield5','pmtfield6','pmtfield7');
		for ($i = 0; $i < count($db_cols); $i++){
			$col = $db_cols[$i];
			$in[$col] = $cses[$col];
		}
		$cses['step2']='done';
		$in['step']='3';
		display_paytypesav();
		(isset($cses['paytype'])) ? $in['paytype']=$cses['paytype'] : $in['paytype']='Credit-Card';
	}
}



function checkout_step3(){
# --------------------------------------------------------
	#### Esto es para mostrar en el step4 de confirmacion
	#### Si el tipo de pago es COD no se muestra la informacion de tarjeta de credito
	#### Si el tipo de pago es CC se muestra una leyenda para informar que la tarjeta sera procesada
	#### Si el tipo de pago es Paypal, hay 2 posibilidades
	########### 1: El cliente ingreso sus datos de shipping en Paypal y paypal nos esta devolviendo la informacion.
	########### 2: El cliente eligion tipo de pago mediante paypal y tenemos que enviar la informacion a Paypal.
	
	# Las time Modified by RB on 08/16/2010 :  Se agrega validacion de cupon para agregar producto de manera automatica a la orden.
	//Last modified on 04-11-2011 14:56:00
//Last modified by: MCC C. Gabriel Varela S. :Se integran points

	global $cfg,$cses,$in,$va,$usr,$error;

	$va['message']  =  '';
	$valid = 'error';

	// Check to see if the Request object contains a variable named 'token'	
	$token = "";
	if (isset($_REQUEST['token'])){
		$token = $_REQUEST['token'];
		$in['paytype'] = 'paypal';
		require("cmd_paypal_review_step2.php");
		update_cart_session();
	}
	
	#print_r($cses);

	if (isset($in['btn3_x'])){
		$error['message'] = trans_txt('reqfields_short');
	}else{
		$db_cols= array('paytype','pmtfield1','pmtfield2','pmtfield3','expmm','expyy','pmtfield5','pmtfield6','pmtfield7');
		for ($i = 0; $i < count($db_cols); $i++){
			$col = $db_cols[$i];
			$in[$col] = $cses[$col];
		}
		if(!isset($in['paytype'])){
			$in['paytype'] = "Credit-Card";
		}
	}
	
	if ($in['paytype']=="Credit-Card") {
	        $va['cod_div']  =  "display:none;";
	        $va['ccard_div']  =  "display:block;";
	}else{
	        $va['ccard_div']  =  "display:none;";
	        $va['cod_div']  =  "display:block;";
	}

	if(isset($in['paytype'])){
		if($in['paytype'] == 'COD'){
			## COD
			$va['hidde_start']  =  '<!--';
			$va['hidde_stop']  =  '-->';
			$db_cols= array('paytype','pmtfield6');
			$type=array('','numeric');
			$req_cols=array('paytype','pmtfield6');
		}elseif($in['paytype'] == 'paypal'){
			$db_cols= array('paytype');
			$type=array('');
			$req_cols=array('paytype');
		}else{
			## Credit Card
			$year   = date("y");
			$month  = date("n");
		
			if ($in['expyy'] == $year and intval($in['expmm']) <= $month){
				$error['expmm'] = &trans_txt('invalid');
				$error['expyy'] = &trans_txt('invalid');
				return;
			}
			
			$db_cols= array('paytype','pmtfield1','pmtfield2','pmtfield3','expmm','expyy','pmtfield5','pmtfield6','pmtfield7');
			$type=array('','','','numeric','numeric','numeric','numeric','numeric','');
			$req_cols=array('paytype','pmtfield1','pmtfield2','pmtfield3','expmm','expyy','pmtfield5','pmtfield6','pmtfield7');
			#$va['message']  =  trans_txt('info_step_confirm_cc');
		}
		# Validate require fields
		$valid=validate_cols($db_cols,$req_cols,$type,1);
	}else{
		$error['paytype'] = trans_txt('required');
	}


	## Step 3 got errors, Showing same step
	if($valid=="error"){
		$va['message']  =  trans_txt('reqfields_short');
		$in['step']='3';
		display_paytypesav();
	}elseif($in['paytype'] == 'paypal' and !isset($_REQUEST['token'])){
		### Si el cliente eligio pagar por Paypal(ingresando su shipping info con nosotros)
		$cses['pmtfield6'] = $in['pmtfield6'];
		save_callsession(0);
		require("cmd_paypal_flow2_step1.php");
	}elseif ($in['btn4_x']){
		$cses['gotoend']=1;
		$in['step']='3';
		display_paytypesav();
		return;
	}elseif ($cses['gotoend']){
		$cses['gotoend'] = 0;
		$in['step']='4';
		$cses['pmtfield4'] = $in['expmm'] . $in['expyy'];
		($cses['paytype'] == 'Credit-Card') and ($va['step4_msg'] = trans_txt('info_step_confirm_cc'));
		($cses['sex']=='Male')?	$va['sex']= trans_txt('male')	: $va['sex']= trans_txt('female');
	}else{
		$in['step']='4';
		$cses['step3']='done';
		$cses['pmtfield4'] = $in['expmm'] . $in['expyy'];
		($cses['paytype'] == 'Credit-Card') and ($va['step4_msg'] = trans_txt('info_step_confirm_cc'));
		#print_r($cses);
		($cses['sex']=='Male')?	$va['sex']= trans_txt('male')	: $va['sex']= trans_txt('female');
		
		if(array_key_exists('coupon_to_apply',$cses) === TRUE and !isset($cses['coupon_used']) )
		{
				/*Valida cupon*/
				$valid_coupon = check_coupon();
				if($valid_coupon[0]>0)
				{
					$va['message']	=	trans_txt('good_coupon');
				}
				else
				{
					$index=-1;
					switch(abs($valid_coupon[0]))
					{
						case 2:
							$index=8;
						break;
						case 5:
							$index=4;
						break;
					}
					$va['message'] = trans_txt('bad_coupon').abs($valid_coupon[0]).$valid_coupon[$index];
					$error['coupon'] = trans_txt('bad_coupon').abs($valid_coupon[0]).$valid_coupon[$index];
				}
		}


		/*Inicia Sección de reward points*/

		if($in['reward_points_action'] == 1 and !isset($cses['reward_points_used']) )
		{
			/*Valida reward points*/
			$valid_reward_points = check_reward_points($in['id_products']);
			if($valid_reward_points[0]>0)
			{
				$va['message']	=	trans_txt('good_reward_points');
			}
			else
			{
				$index=-1;
				switch(abs($valid_reward_points[0]))
				{
					case 2:
						$index=4;
					break;
					case 5:
						$index=3;
					break;
				}
				$va['message'] = trans_txt('bad_reward_points'.abs($valid_reward_points[0])).$valid_reward_points[$index];
				$error['reward_points'] = trans_txt('bad_reward_points'.abs($valid_reward_points[0])).$valid_reward_points[$index];
			}

			$in['step']='4';
			$in['paytype']=$cses['paytype'];
			$va['products_inorder'] = products_inorder();
			$va['paymentData'] = showPaymentData($cses['zip'],$cses['state']);
			return;
		}
		/*Termina Sección de reward points*/


		if(array_key_exists('reward_id_products_to_apply',$cses) === TRUE and !isset($cses['reward_points_used']) )
		{
				/*Valida reward_points*/
				$valid_reward_points = check_reward_points();
				if($valid_reward_points[0]>0)
				{
					$va['message']	=	trans_txt('good_reward_points');
				}
				else
				{
					$index=-1;
					switch(abs($valid_reward_points[0]))
					{
						case 2:
							$index=4;
						break;
						case 5:
							$index=3;
						break;
					}
					$va['message'] = trans_txt('bad_reward_points').abs($valid_reward_points[0]).$valid_reward_points[$index];
					$error['reward_products'] = trans_txt('bad_reward_points').abs($valid_reward_points[0]).$valid_reward_points[$index];
				}
		}
		
	}
	update_cart_session();
	$cses['phone1'] = $cses['pmtfield6'];	
	$va['products_inorder'] = products_inorder();
	save_callsession(0);
}

function checkout_step4(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/11/10 11:05:45
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
//Last modified on 20 Dec 2010 12:07:03
//Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
//Last modified on 04-11-2011 14:58:00
//Last modified by: MCC C. Gabriel Varela S. :Se integran points
//Last modified on 2 May 2011 13:22:12
//Last modified by: MCC C. Gabriel Varela S. : Se incorpora promo_campaign
//Last modified on 12 May 2011 10:56:31
//Last modified by: MCC C. Gabriel Varela S. : Se hace que setcookie aplique a raíz
//Last modified on 26 May 2011 15:43:51
//Last modified by: MCC C. Gabriel Varela S. : Se incluyen condiciones if(($error==1 or $error==4 or $error==5) and $cses['coupon_used']!='' and $cses['id_orders']=='')
//Last modified on 27 May 2011 13:56:58
//Last modified by: MCC C. Gabriel Varela S. : expiration is now considered for reward_points
//Last modified on 22 Jul 2011 16:06:41
//Last modified by: MCC C. Gabriel Varela S. :remote google-checkout site is consider
//Last modified by RB on 07/19/2012 :Se agrega nota de dispositivo de conexion

	global $cfg,$cses,$va,$in,$error,$usr,$tpl;
	
	#it evaluates if redirection is needed
	if(isset($_COOKIE['google_order_remote']) and $_COOKIE['google_order_remote']!='0')
	{
		$google_checkout_remote=explode(":", $_COOKIE['google_order_remote']);
		setcookie('google_order_remote', "0",0,'/');
		save_callsession(1);
		header("Location:http://$google_checkout_remote[0]/".base64_encode($google_checkout_remote[1])."-".base64_encode($google_checkout_remote[2])."-".base64_encode($google_checkout_remote[3]));
	}
	
	$va['pname']="";
	$va['paymentData']="";
	($cses['paytype'] == 'Credit-Card') and ($va['step4_msg'] = trans_txt('info_step_confirm_cc'));
	
	for ($i=1;$i<=$cses['items_in_basket'];$i++){
		if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
			$name=load_name('sl_products',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
			$namep=load_name('sl_products_prior',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
			if($namep!='')
				$name=$namep;
			$va['pname'] .= $name."<br>";
		}
	}
	
	$va['paymentData'] = showPaymentData($cses['zip'],$cses['state']);
	$va['style_paytype'] = '';
	$va['style_paytype'] = 'display:none';
	$va['zipcode'] = $cses['shp_zip'];
	$va['products_inorder'] = products_inorder();

	if(!isset($cses['final'])){
		/*Inicia Sección de cupones*/
			
			if($in['coupon_action'] == 1 and !isset($cses['coupon_used']) )
			{
				/*Valida cupon*/
				$valid_coupon = check_coupon($in['coupon']);
				if($valid_coupon[0]>0)
				{
					$va['message']	=	trans_txt('good_coupon');
				}
				else
				{
					$index=-1;
					switch(abs($valid_coupon[0]))
					{
						case 2:
							$index=8;
						break;
						case 5:
							$index=4;
						break;
					}
					$va['message'] = trans_txt('bad_coupon'.abs($valid_coupon[0])).$valid_coupon[$index];
					$error['coupon'] = trans_txt('bad_coupon'.abs($valid_coupon[0])).$valid_coupon[$index];
				}
				
				$in['step']='4';
				$in['paytype']=$cses['paytype'];
				$va['products_inorder'] = products_inorder();
				$va['paymentData'] = showPaymentData($cses['zip'],$cses['state']);
				return;
			}
				
		/*Termina Sección de cupones*/

		
		//Revisa que no existan productos sin choice
		$wchoice=check_products_wochoices();
		$cses['step04']='done';
		if($wchoice!=0){
			#$va['message']	=	trans_txt('wchoice')."<img src='/images/help.png' title='Elegir' alt='' border='0' onClick=\"alert(getElementById('ajax_btn').value);\"></a>";
			$in['step']='4';
			$in['wchoice']=$wchoice;
			#$va['billing_info'] = billing_info_cc();
			$in['paytype']=$cses['paytype'];
			$va['products_inorder'] = products_inorder();
			$va['message'] = trans_txt('wchoice').build_edit_choices_module(substr($cses['items_'.$wchoice.'_id'],3),"index.php","cmd=cart&step=$in[step]&to_do=drop&do=$wchoice&checkout=1#tabs","tabchoice$wchoice","<img src='/images/help.png' title='Elegir' alt='' border='0'>");
		}elseif(!isset($cses['step5'])){

			## Si el cliente es paypal e ingreso datos de su cuenta en Innovashop
			if( !empty($in['ask_password']) and strlen($in['ask_password']) > 4  and check_email_address($in['ask_email']) and empty($usr['id_customers']) ){
				if(start_login($in['ask_email'],$in['ask_password'])=='ok'){
					########## Usuario Valido
					$cses['usertype'] = 'member';
					$cses['id_customers'] = $usr['id_customers'];
					$va['message'] = trans_txt('welcome') .' '. $usr['firstname'];
				}else{
					$in['step']='4';
					$in['paytype']=$cses['paytype'];
					$va['message'] = trans_txt('password_error');
					save_logs("log_invalidlogin", $in['username']);
					return;
				}
			}
			
			/*Inicia Se verifica información de cupones*/
			if($usr['type']!='Membership' and (!isset($cfg['promo_campaign']) or $cfg['promo_campaign']==0))
			{
				$sth = mysql_query("Select 
				if(Status='Active',1,0)as isactive,
        if(curdate()<=expiration,1,0)as isvalid,
        coupon_value,
        expiration,
        ID_promo,
        percentage,
        maxdiscount,
        minimum_external,
        Status 
				from sl_coupons_external 
				where coupon_value='".mysql_real_escape_string($cses['coupon_used'])."';") or die("Query failed : S" . mysql_error());
				$rec = mysql_fetch_assoc($sth);
				$error='';
				if(mysql_num_rows($sth) == 0)
				{
					$error=1;
				}
				if($rec['isactive']==0)
				{
					$error=4;
				}
				if($rec['isvalid']==0)
				{
					$error=5;
				}
				if($cses['total_i'] < $rec['minimum_external']){
					$error=2;
				}
				if(!(($in['coupon']!='' or $cses['coupon_to_apply'] != '') and !isset($cses['discount_applied'])))
				{
					$error=3;
				}
				if(($error==1 or $error==4 or $error==5) and $cses['coupon_used']!='' and $cses['id_orders']=='')
				{
					$in['step']='4';
					#$va['billing_info'] = billing_info_cc();
					$in['paytype']=$cses['paytype'];
					$va['message']	=	trans_txt('bad_coupon'.$error);
					$cses['coupons_discounts']=0;
					#$cses[total_disc]=0;
					$error['coupon']=trans_txt('bad_coupon'.$error);
					$cses['coupon_used']='';
					$cses['discount_applied']=0;
					$cses['coupon_minimum_external']=0;
					$va['products_inorder'] = products_inorder();
					return;
				}
				elseif(mysql_num_rows($sth) == 1 and $cses['coupon_used'] !=''){
					mysql_query("Update sl_coupons_external set Status='Used' where coupon_value='".mysql_real_escape_string($cses['coupon_used'])."' and Status='Active' and curdate()<=expiration;") or die("Query failed : g$rec[ID_coupons_external]" . mysql_error());
					@mail("rbarcenas@inovaus.com","cupon utilizado","$cses[coupon_used]");
				}
			}
			/*Termina Se verifica información de cupones*/
			
			/*Inicia Se verifica información de reward_points*/
			if($usr['type']!='Membership' and (!isset($cfg['promo_campaign']) or $cfg['promo_campaign']==0))
			{
				$sth = mysql_query("Select 
				if(Status='Active',1,0)as isactive,
				/*if(curdate()<=expiration,1,0)as isvalid,
				expiration,*/
				id_products,
				Points_needed,
				minimum_external,
				Status 
				from sl_reward_points_gifts 
				where id_products='".mysql_real_escape_string($cses['reward_points_used'])."';") or die("Query failed : S" . mysql_error());
				$rec = mysql_fetch_assoc($sth);
				$error='';
				if(mysql_num_rows($sth) == 0)
				{
					$error=1;
				}
				if($rec['isactive']==0)
				{
					$error=4;
				}
				if($cses['total_i'] < $rec['minimum_external']){
					$error=2;
				}
				if(!(($in['id_products']!='' or $cses['reward_id_products_to_apply'] != '') and !isset($cses['reward_points_applied'])))
				{
					$error=3;
				}
				if(($error==1 or $error==4 or $error==5) and $cses['reward_points_used']!='' and $cses['id_orders']=='')
				{
					$in['step']='4';
					#$va['billing_info'] = billing_info_cc();
					$in['paytype']=$cses['paytype'];
					$va['message']	=	trans_txt('bad_reward_points'.$error);
					#$cses[total_disc]=0;
					$error['reward_products']=trans_txt('bad_reward_points'.$error);
					$cses['reward_points_used']='';
					$cses['reward_points_applied']=0;
					$cses['reward_points_minimum_external']=0;
					$va['products_inorder'] = products_inorder();
					return;
				}
				elseif(mysql_num_rows($sth) == 1 and $cses['reward_points_used'] !=''){
					sub_reward_points($usr['id_customers'],$rec['Points_needed']);
				}
			}
			/*Termina Se verifica información de reward_points*/
			
			
			/*	Creamos la Orden	*/
			$response = create_order();
			
			
			

			/* Si el API de cobro falla, ingresamos el paylog a mano */
			if(strpos($response,"APIFailed")!== FALSE){
				mysql_query("INSERT INTO sl_orders_plogs SET ID_orders='$cses[id_orders]',Data='APIFailed',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr[id_admin_users]';");
			}
			/* Contamos los intentos */
			$ntries = get_tries($cses['id_orders']);
			/*	Pago Denegado	 < 3 intentos*/
			if(strpos($response,"OK")=== false && $ntries <= 2){
				//write_record('Failed',$response);
				if(strpos($response,"APIFailed")=== FALSE){
					$va['message']	=	$response;
					$in['edit_cfn']=1;
					$in['step']='3';
					($cses['paytype'] == 'paypal') and ($in['step'] = '4') and ($in['paytype'] = $cses['paytype']);
  
					if($cses['paytype']  == 'COD'){
						$in['paytype'] = 'COD';
					}else {
						$in['paytype'] = 'Credit-Card';
						$in['pmtfield1'] = $cses['pmtfield1'];
						$in['pmtfield2'] = $cses['pmtfield2'];
						$in['pmtfield3'] = $cses['pmtfield3'];
						$in['expmm'] = $cses['expmm'];
						$in['expyy'] = $cses['expyy'];
						$in['pmtfield5'] = $cses['pmtfield5']; 
						$in['pmtfield7'] =$cses['pmtfield7'];
					}
					$in['pmtfield6'] = $cses['phone1'];
					//return;
				}else{
					$va['message'] = trans_txt('payment_apifailed');	
					$in['step']='4';
					#$va['billing_info'] = billing_info_cc();
					$in['paytype'] = $cses['paytype'];
					$va['products_inorder'] = products_inorder();
					//return;
				}
				$va['message'] = str_replace(array("\r\n","\r","\n"),array("<br>","<br>","<br>"),$va['message']);
				//echo "Algo malo $in[step]: $response";
			}else{
				/*Bandera preventiva para prevencion de tecleo F5	*/
				$cses['final']=1;
				$cses['step5']='done';
				$in['step']='5';

				/*Pago Denegado >=	3 intentos	*/
				if($ntries > 2){
					//write_record($failedstatus,$response);
					if(strpos($response,"APIFailed")!== FALSE){
						$response = trans_txt('response_apifailed'); 
					}else{
						$response = trans_txt('response_paymentfailed');
					}
					$cses['step_final'] = "checkout_denied";
					$cses['response'] = $response;
					set_device_note($cses['id_orders']);
				}else{
					general_tracker('CreateOrder');
				/* Pago Aceptado	*/
					//write_record('Processed',$response);
					$cses['step_final'] = "checkout_neworder";
					/* Prevenimos compra de pruebas gratis pasadas */
					//get_trial_duplicate();

					if($cses['paytype'] == 'COD'){
						mysql_query("UPDATE sl_orders SET Status='New' WHERE ID_orders = '$cses[id_orders]';");
					}

					$va['pname']="";
					$va['paymentData']="";
					
					for ($i=1;$i<=$cses['items_in_basket'];$i++){
						if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
							$name=load_name('sl_products',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
							$namep=load_name('sl_products_prior',"ID_products",substr($cses['items_'.$i.'_id'],3),"Name");
							if($namep!='')
								$name=$namep;
							$va['pname'] .= $name.$cses['items_'.$i.'_id']."<br>";
						}
					}
					
					$va['paymentData'] = showPaymentData($cses['zip'],$cses['state']);
					
					/*Aqui comienza la generacion de tarjeta de regalo*/
					if(is_gift_cardable())
					{
						$gift_card_value=0;
						$gift_card_values=calculate_gift_card_values();
						$cses['gift_card_number']=set_coupon_external($gift_card_values['expiration_days'],$gift_card_values['id_promo'],$gift_card_values['percentage'],$gift_card_values['value'],$gift_card_values['sale_min'],$gift_card_values['url_external']);
						$va['gift_card']="Se ha ganado una tarjeta de regalo por un monto de $ $gift_card_values[value] y con vigencia por $gift_card_values[expiration_days] d&iacute;as que puede utilizar en su siguente compra.<br>
															El monto m&iacute;nimo de su compra debe ser de $ $gift_card_values[value] y el n&uacute;mero de su tarjeta de regalo es: $cses[gift_card_number] (&eacute;ste le ser&aacute; solicitado en la confirmaci&oacute;n de su siguiente compra en el &aacute;rea de cupones.)";
					}
					/*Aqui termina*/
					
					/* Enviamos correo de confirmacion	*/
					if(!isset($cses['emailConfirm'])){
						sendFinalEmail($response);
						$cses['emailConfirm']=1;
					}
					send_dropship_alert($cses['id_orders']);
					set_device_note($cses['id_orders']);

				}
				setcookie('ps', 'Off',0,'/');
			}
		}else{
			$in['step']=5;
		}
	}else{
		$in['step']=5;
		$va{'password'} = $cses['password'];
		## New Customer's Password
		if(isset($in['btncust_x']) and !isset($cses['password'])){
			$va['newcust_message']='';

			if(!isset($in['password']) or strlen($in['password']) < 6 or strlen($in['password'])>12){
				$va['newcust_message'] = &trans_txt("reqfields_short");
				$error['password'] = &trans_txt("range_passwd");
				++$err;
			}

			if(!isset($in['password2']) or strlen($in['password2']) < 6 or strlen($in['password2'])>12){
				$va['newcust_message'] = &trans_txt("reqfields_short");
				$error['password2'] = &trans_txt("range_passwd");
				++$err;
			}

			if($in['password'] !== $in['password2']){
				$va['newcust_message'] = &trans_txt("invalid_passwd_confirmation");
				$error['password'] = &trans_txt("invalid");
				$error['password2'] = &trans_txt("invalid");
				++$err;
			}

			if($err > 0){
				return;
			}else{
				$cses['new_customer']='';
				unset($cses['new_customer']);
				$cses['new_password'] = 'checkout_newpasswd';
				$to = $cses['email'];
				$va{'firstname'} = $cses['firstname'];
				$va{'maindomain'} = $cfg{'maindomain'};
				$va['newcust_message'] = &trans_txt("email_activation");
				$cses['password']= $in['password'];
				$va{'password'} = $in['password'];
				$va{'temppasswd'} = sha1($in['password']);

				### Setting confirmation string in sl_vars
				$va{'string_confirmation'} = md5(gen_passwd());
				$va{'signin_urlconfirm'}   = $cfg{'signin_urlconfirm'};
				mysql_query("DELETE FROM sl_vars WHERE Vname='ishop_".$cses['id_customers']."_conf'; ");
				$xconfirmation = mysql_query("INSERT INTO sl_vars SET VName='ishop_".$cses['id_customers']."_conf', VValue='".$va{'string_confirmation'}."',Subcode='".$va{'temppasswd'}."', Definition_En = 'Innovashop String Confirmation' ");

				### Sending email & displaying the success creation
				$message_mail = build_page('content/mypassword_email_confirmation.html');
				$va{'message_mail'} = $message_mail;
				$subject = trans_txt('mypassword_confirmation');  

				$headers = 'From: Innovashop <' . $cfg{'cservice_email'} . ">\r\n" .
					'Reply-To: ' . $cfg{'cservice_email'} . "\r\n" .
					'X-Mailer: PHP/' . phpversion();

				mail($to, $subject, $message_mail, $headers);

			}
		}
	}
}

function show_cart(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/29/10 16:16:49
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
//Last modified on 04-11-2011 14:59:00
//Last modified by: MCC C. Gabriel Varela S. : Se integran points
	global $tpl,$cses,$va,$cfg,$in,$device;

	$tpl['pagetitle'] = trans_txt('editcart');
	$tpl['skel'] = $device['is_mobile_device'] ? $tpl['skel'] : "cart_product.html";
	$tpl['filename'] = $device['is_mobile_device'] ? "content/comprar.html" : "cart/content/editing_cart.html";
	
	if($cses['products_in_basket'] > 0){
		check_gift();
		check_reward_points();
		
		//check_freeshp_bytotals();
			for ($i=1;$i<=$cses['items_in_basket'];$i++){
					if ($cses['items_'.$i.'_qty']>0  and $cses['items_'.$i.'_id']>0){
						
							$warning_choice = '';
							## Item has choices and user hasn't choose yet.
							if(substr($cses['items_'.$i.'_id'],0,3) == '999' or build_edit_choices_module($cses['items_'.$i.'_id'],'','','')!=''){
							    $warning_choice	=	'<br><span style="color:#b83333;font-size:10px;">'.build_edit_choices_module($cses['items_'.$i.'_id'],"index.php","cmd=cart&do=$i&view_cart=1&action=$i#tabs","tabchoice$i").'</span>';
							}
						
							++$qty;
							$n = $qty % 2;
							$total += $cses['items_'.$i.'_price']*$cses['items_'.$i.'_qty'];
							$q = mysql_query("SELECT Name FROM sl_products_w WHERE ID_products = '".substr($cses['items_'.$i.'_id'],-6)."' AND BelongsTo = '".$cfg['owner']."';");
							list($id_name) = mysql_fetch_row($q);
							
							if(!$id_name){
								$id_name = load_name('sl_products','ID_products',substr($cses['items_'.$i.'_id'],3,6),'Name');
							}


							if($device['is_mobile_device']){

									###############################################################
									###############################################################
									###############################################################
									##### Mobile Content
									###############################################################
									###############################################################
									###############################################################

									$va['searchresults'] .= '<tr>'."\n".'
																<td colspan=5>'."\n".'
																	<img src=/mobile/images/hr.gif width=100% height=1px style="margin-bottom:5px;" border="0">'."\n".'
																</td>'."\n".'
															</tr>'."\n".'
															<tr>'."\n".'
																<td align=center width=25px>'."\n".'
																	<a href="delete_'.$i.'-editing_cart" class="m_text">
																		<img src="/mobile/images/delete.png" border="0">'."\n".'
																	</a>
																</td>'."\n".'
																<td align=left width=55px>'."\n".'
																	<a href="'.specialsum($id_name,0).'-a" class="text">
																		<img src="/cgi-bin/showimages.cgi?id='.substr($cses['items_'.$i.'_id'],3,6).'&img=1&type=b&spict=1" width="50px" align="left" border"=0">'."\n".'
																	</a>	
																</td>'."\n".'
																<td align=left>'."\n".
																	'<b>'. $id_name .'</b><br> ID: '. format_sltvid($cses['items_'.$i.'_id']) .'
																</td>'."\n".'
																<td align="right" nowrap>'.$cses['items_'.$i.'_qty'].'</td>'."\n".'
																<td align="right" nowrap>'."\n".
																	format_price($cses['items_'.$i.'_price']).
																'</td>'."\n".'
															</tr>'."\n".'

															<tr>'."\n".'
																<td colspan=5>'."\n".'
																	<img src=/mobile/images/hr.gif width=100% height=1px style="margin-bottom:5px;" border=0>'."\n".'
																</td>
															</tr>'."\n";

							}else{

									###############################################################
									###############################################################
									###############################################################
									##### PC/Laptop Content
									###############################################################
									###############################################################
									###############################################################

							
									$va['searchresults'] .= "<tr  style='background-image:url(images/deg.jpg); background-repeat:repeat-x; background-color:#ffffff ;'>
														<td align='center'>
															<a href='delete_$i-editing_cart' class='m_text' >
																<img src='$cfg[url_images]delete.png' alt='Delete' style='border:0px;'>
															</a>
														</td>
														<td align='center'>
															<div style='margin-top:7px;'>".show_image_in_page(substr($cses['items_'.$i.'_id'],3,6),1,'b',$cses['items_'.$i.'_gift'])."</div>
															<!--<span class='l1_text'>".trans_txt('added')." ".$cses['items_'.$i.'_month']."/".$cses['items_'.$i.'_day']."/".$cses['items_'.$i.'_year']."</span>-->
														</td>
														<td id='tabchoice$i'><a href='/".specialsum($id_name,0)."-a' class='text'>
																<font size=2> $id_name </font><br>
																(".format_sltvid($cses['items_'.$i.'_id']) .")
																</a>
																$warning_choice
														</td>
														<td align='right'>".$cses['items_'.$i.'_qty']."</td>
														<td align='right' class='l1_text' nowrap><strong>".format_price($cses['items_'.$i.'_price'])."</strong>
														</td>
													</tr>
													<tr>
														<td colspan='5' style='border-bottom:1px solid #ccc;'> </td>
													</tr>\n";
							}

					}
			}
															
	}else{

			$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
			$tpl['filename'] = $device['is_mobile_device'] ? "content/no_product.html" : "/cart/content/no_product.html";

			$va['searchresults'] .= '<tr>
										<td colspan="5" align="center" class="l_text"><br><br><br><strong>'.trans_txt('empty_cart').'</strong></td>
									</tr>';
							
			$in['message']=trans_txt("empty_cart");
							
	}
}

?>
