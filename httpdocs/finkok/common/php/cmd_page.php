<?php

function runcmd_login(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
}

function runcmd_tipos_de_envio(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
}

function runcmd_cupon_inauguracion(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos al nuevo Innovashop.tv :: Cupones";
}

function runcmd_innova_tv(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
}


function runcmd_homex(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  #$in['product']=914900;
  #do_for_one_product();
  $tpl['skel'] = 'cart_productf.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
  #$tpl['filename'] = "content/innova_tv12.html";
}

function runcmd_home(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  #$in['product']=914900;
  #do_for_one_product();
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
  #$tpl['filename'] = "content/innova_tv12.html";
}

function runcmd_basket(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  #$in['product']=914900;
  #do_for_one_product();
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
  $tpl['filename'] = "basket.php";
}

function runcmd_invita(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
 
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Innovashop tv - Promociones";
  
  $id_products = $in['op_product'];
  $img_url = $cfg['maindomain'] . '/images/prodimages/iusa/';
  $pimage = $id_products.'b1.jpg';
  $pname = &load_name('sl_products_w','ID_products',$id_products,'Name');

  if(is_readable($cfg['path_imgmanf'] . $pimage )){
  		$va['gift_name'] = $pname . '<br><img src="http://'. $img_url . $pimage .'">';
 	}else{
 			$va['gift_name'] = $pname;
 	}
  $va['id_products_hidden'] = '<input type="hidden" name="id_op_products" value="'.$id_products.'">';
  
  		
  if($usr[type]=='Membership')
  {
	  #$tpl['skel']="cart_product.html";
		$in['message']=trans_txt("no_member");
		#$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
		$tpl['filename']="/cart/content/no_member.html";
		$in['product']=460093;
	  do_for_one_product();
	  $tpl[skel]="no_member.html";
		return -1;
  }
}

function runcmd_invita_view(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
  #$tpl['skel']="cart_product.html";
	$in['message']=trans_txt("no_member");
	#$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
	$tpl['filename']="/openinviter/invita_view.php";
}

function runcmd_felicidades_view(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
  $tpl['pagetitle']="Bienvenidos a Innova tv";
  #$tpl['skel']="cart_product.html";
	$in['message']=trans_txt("no_member");
	#$in['srcfile']="/?cmd=show_description&id=$in[id_products]";
	$tpl['filename']="/openinviter/felicidades_view.php";
}


function runcmd_novedades(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;

	if(!empty($_COOKIE['innovashop_id_products'])){
		$id_products = $_COOKIE['innovashop_id_products'];
	} else {
		$sth = mysql_query("SELECT sl_products.ID_products
FROM sl_products
INNER JOIN sl_products_w
USING ( ID_products )
WHERE (
(
sl_products.Status = 'On-Air'
AND sl_products.web_available = 'Yes'
)
OR sl_products.Status = 'Web Only'
)
AND sl_products_w.belongsto = 'innovashop'
GROUP BY sl_products.ID_products
ORDER BY sl_products_w.Date DESC
LIMIT 5")  or die("Query failed : " . mysql_error());
		while ($rec = mysql_fetch_assoc($sth)) {
			$arr_id_products[] = $rec['ID_products'];
		}  // End while

		$id_products = $arr_id_products[array_rand($arr_id_products)];  // Obtiene un producto aleatorio
		setcookie('innovashop_id_products',$id_products, time() + 3600); // Expira en 1 hora
	}

/*
echo "<pre>";
print_r($_COOKIE);
echo "</pre>";
*/

  $tpl['skel'] = 'cart_product.html';
  //$in['product']=733304;
  $in['product'] = $id_products;
  do_for_one_product();
  $tpl[skel]="novedades.html";
}

function runcmd_contacto(){
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cservice.html';	
}

function runcmd_ayuda(){
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'default_tabs.html';	
}

function runcmd_promociones(){
#-----------------------------------------
  global $cfg,$in,$cses,$va,$tpl,$usr;
  $tpl['skel'] = 'cart_product.html';
}

function runcmd_registration(){
#-----------------------------------------
//Last modified on 20 Dec 2010 12:07:39
//Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
//Last modified on 2 Mar 2011 15:59:27
//Last modified by: MCC C. Gabriel Varela S. : Se integra birthday
//Last modified on 3/21/11 11:52 AM
//Last modified by: MCC C. Gabriel Varela S. :Se cambia birthday por combo
      global $cfg,$in,$cses,$va,$tpl;

      $tpl['skel'] = 'cart_product.html';
      if(isset($in['signin'])){

	      $db_cols  = array('firstname','lastname1','birthday_month','birthday_day','sex','phone1','email','address1','city','state','zip');
	      $req_cols = array('firstname','lastname1','','','sex','phone1','email','address1','city','state','zip');
	      $type     = array('','','','','','phone','email','','','','numeric');
	      
	      $valid ='error';
	      $valid = validate_cols($db_cols,$req_cols,$type,0);
	      
	      if($valid == "ok"){
	      
		      while(list($key,$value) = each($in)){
			      $cses{$key} = $value;
		      }

		      $sth = mysql_query("Select count(*) from sl_customers WHERE email='".filter_values($in[email])."' AND Password IS NOT NULL AND Password!='';");
		      $is_customer = mysql_result($sth,0);

		      if($is_customer > 0){
						    $va{'message'} = trans_txt('pwd_recovery');
						    $in{'fname'} = 'mypassword';
						    $tpl['filename'] = '/content/'.$in{'fname'}.'.html'; 	 
		      }else{
		      ########### Customer Created
			      $cses['usertype']='registration';
			      $id_customers = create_customer();
			      $in{'id_customers'} = $id_customers;
			      $in{'fname'} = 'registration_complete';
		        
			      ### Setting temp password and updating customer table
			      $passwd = gen_passwd();
			      $va{'password'} = $passwd;
			      $va{'temppasswd'} = sha1($passwd);
		        
			      $xupdate_customer = mysql_query("UPDATE sl_customers SET Password = '".$va{'temppasswd'}."', Status='Inactive' WHERE ID_customers = '".$in{'id_customers'}."' ");
		        
			      ### Setting confirmation string in sl_vars
			      $va{'string_confirmation'} = md5(gen_passwd());
			      $va{'signin_urlconfirm'}   = $cfg{'signin_urlconfirm'};
			      $xconfirmation = mysql_query("INSERT INTO sl_vars SET VName='ishop_".$in{'id_customers'}."_conf', VValue='".$va{'string_confirmation'}."', Definition_En = 'Innovashop String Confirmation' ");
		        
			      ### Sending email & displaying the success creation
			      $message_mail = build_page('content/registration_email_confirmation.html');
			      $va{'message_mail'} = $message_mail;
			      $to = $in{'email'};
			      $subject = trans_txt('signin_confirmation');  
		        
						$headers["Reply-To"] = $cfg{'cservice_email'};
						$headers["X-Mailer"] = "PHP/phpversion()";
						$headers["Content-Type"] = 'text/plain; charset="utf-8"';

/*
			      $headers = 'From: Innovashop <' . $cfg{'cservice_email'} . ">\r\n" .
				        'Reply-To: ' . $cfg{'cservice_email'} . "\r\n" .
				        'X-Mailer: PHP/' . phpversion();
*/
			      
						send_mail($to, $subject, $message_mail, $headers);
			      //mail($to, $subject, $message_mail, $headers);
						    
			      $tpl['filename'] = '/content/'.$in{'fname'}.'.html';
					      
		      }
	      }else{
		      $va{'message'} = trans_txt('reqfields_short');
	      }	

      }
}


function runcmd_registration_active(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/25/10 15:53:10
# Author: RB.
# Description :   
# Parameters :
		global $in,$va,$tpl;
		$tpl['skel'] = 'cart_product.html';
		#Busca el token
		#$search_customer = run_port_function('search_token');
		
		$stoken = mysql_query("SELECT ID_vars,VName,VValue FROM sl_vars WHERE VValue = '".mysql_real_escape_string($in['token'])."' ");
		
		if($stoken and mysql_num_rows($stoken) > 0){
					list($id,$name,$value) = mysql_fetch_row($stoken);
					$ary = explode("_",$name);
					$id_customers = $ary[1];
					
					$xactive = mysql_query("UPDATE sl_customers SET Status='Active' WHERE ID_customers = '".$id_customers."' ");
					
					if($xactive){
								$dtoken  = mysql_query("DELETE FROM sl_vars WHERE ID_vars = '$id' ");
					}else{
								$va{'message'} = trans_txt('token_problem');
								$in{'fname'}   = 'mypassword';
					}
		}else{
					$va{'message'} =  trans_txt('token_problem');
					$in{'fname'}   = 'mypassword';
		}
		$tpl['filename'] = '/content/'.$in{'fname'}.'.html';
}


function runcmd_mypassword(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/25/10 15:53:10
# Author: RB
# Description : Set a new password for customer   
# Parameters :
//Last modified on 20 Dec 2010 12:07:59
//Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
//Last modified by RB on 03/21/2011 03:13:32: El proceso cambia. Solo se envia la cadena codificada y el usuario al presionar el link elegira su propia clave de acceso

      global $cfg,$in,$va,$tpl;

      $tpl['skel'] = 'cart_product.html';
      $va{'message'} = trans_txt('pwd_recovery');
      if(check_email_address($in{'email'},'')){

	  $xcust = mysql_query("SELECT ID_customers,firstname FROM sl_customers WHERE email = '".mysql_real_escape_string($in{'email'})."'; ");
        
	  
	  if($xcust and mysql_num_rows($xcust) > 0){

	        ########### email exist?
	        list($id_customers,$firstname) = mysql_fetch_row($xcust);
	        $va{'firstname'} = $firstname;
	        $in{'fname'} = 'mypassword_complete';
	        $va{'maindomain'} = $cfg{'maindomain'};

	        ### Setting temp password and updating customer table
/*	        $passwd = gen_passwd();
	        $va{'password'} = $passwd;
	        $va{'temppasswd'} = sha1($passwd);
*/
	        ### Setting confirmation string in sl_vars
	        $va{'string_confirmation'} = md5(gen_passwd());
	        $va{'signin_urlconfirm'}   = $cfg{'signin_urlconfirm'};
	        mysql_query("DELETE FROM sl_vars WHERE Vname='ishop_".$id_customers."_conf' OR Subcode = '$id_customers'; ");
	        $xconfirmation = mysql_query("INSERT INTO sl_vars SET VName='ishop_newpasswd_code', VValue='".$va{'string_confirmation'}."',Subcode='".$id_customers."', Definition_En = 'Innovashop String Confirmation' ");

	        ### Sending email & displaying the success creation
	        $message_mail = build_page('content/mypassword_email_confirmation.html');
	        $va{'message_mail'} = $message_mail;
	        $to = $in{'email'};
	        $subject = trans_txt('mypassword_confirmation');

					$headers["Reply-To"] = $cfg{'cservice_email'};
					$headers["X-Mailer"] = "PHP/phpversion()";

/*
	        $headers = 'From: Innovashop <' . $cfg{'cservice_email'} . ">\r\n" .
		        'Reply-To: ' . $cfg{'cservice_email'} . "\r\n" .
		        'X-Mailer: PHP/' . phpversion();
*/
					send_mail($to, $subject, $message_mail, $headers);
	        //mail($to, $subject, $message_mail, $headers);

	        $tpl['filename'] = '/content/'.$in{'fname'}.'.html';

	  }else{
	        $va{'message'} = trans_txt('user_not_found');
	  }
      }
}


function runcmd_mypassword_active(){
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/26/10 17:53:10
# Author: RB.
# Description :   
# Parameters :
# Last Modified on: 11/11/10 12:53:20
# Last Modified by: MCC C. Gabriel Varela S: Se adecúa a propuesta de Carlos
# Last Time Modified by RB on 03/21/2011 05:05:42 PM: Se valida la cadena y se muestran campos para elegir nueva clave

	global $in,$va,$tpl;
	$tpl['skel'] = 'cart_product.html';
	#Busca el token
	#$search_customer = run_port_function('search_token');

	$in['fname']   = 'mypassword';
	if(isset($in['token'])){

		$stoken = mysql_query("SELECT ID_vars,Subcode FROM sl_vars WHERE VValue = '".mysql_real_escape_string($in['token'])."' ");

		if($stoken and mysql_num_rows($stoken) > 0){
			list($id_vars,$id_customers) = mysql_fetch_row($stoken);

			if(strlen($id_customers) > 10){
				$qdata = mysql_query("SELECT VName FROM sl_vars WHERE ID_vars = '$id_vars'");
				list($vname) = mysql_fetch_row($qdata);
				$adata = explode($vname);
				$id_customers = $adata[1];
			}

			$sthcust = mysql_query("Select concat(firstname,' ',lastname1) as name,email from sl_customers where ID_customers='$id_customers'");
			$reccust = mysql_fetch_assoc($sthcust);
			$in['name']=$reccust['name'];
			$in['email']=$reccust['email'];

			if(!isset($in['newpasswd'])){
				## User comes from the email link
				$in['fname'] = 'mypassword_reset';

			}else{
				## User comes from new passwd form
				if(strlen($in['newpasswd']) > 0 and $in['newpasswd'] == $in['newpasswdc']){
					$newpasswd = sha1($in['newpasswd']);
					$xactive = mysql_query("UPDATE sl_customers SET Status='Active',Password='".mysql_real_escape_string($newpasswd)."' WHERE ID_customers = '".$id_customers."' ");

					if($xactive){
								$dtoken  = mysql_query("DELETE FROM sl_vars WHERE ID_vars = '".$id_vars."' ");
								$in['fname'] = 'mypassword_active';
					}else{
								$va['message'] = trans_txt('token_problems');
					}
				}else{
					$va['message'] = trans_txt('pwd_nomatch');
					$in['fname'] = 'mypassword_reset';
				}
			}
		}else{
			$va['message'] = trans_txt('token_problems');
		}

	}
	$tpl['filename'] = '/content/'.$in['fname'].'.html';
}


function runcmd_subscribe(){
#-----------------------------------------
      global $cfg,$in,$cses,$va,$tpl;

      $tpl['skel'] = 'cart_product.html';
      if(isset($in['email'])){

	      $db_cols  = array('email');
	      $req_cols = array('email');
	      $type     = array('email');
	      
	      $valid ='error';
	      $valid = validate_cols($db_cols,$req_cols,$type,0);
	      
	      if($valid == "ok"){
	      
		      $group = 'InnovaUSA';
		      $va['message'] = trans_txt('subscribeok');
		      while(list($key,$value) = each($in)){
			      $cses{$key} = $value;
		      }
		      
		      $xsubscribe = mysql_query("INSERT INTO nsc_campaigns_email SET name='".mysql_real_escape_string($in['name'])."', email='".mysql_real_escape_string($in['email'])."', `Group`='$group',Status='Active',Date=CURDATE(),Time=CURTIME(),ID_admin_users='id_admin_users'; ");

		      if(mysql_affected_rows() == 1){
			      ### Sending email & displaying the success creation
			      $message_mail = build_page('content/subscribe_email_confirmation.html');
			      $va{'message_mail'} = $message_mail;
			      $to = $in{'email'};
			      $subject = trans_txt('subscribeok');  

						$headers["Reply-To"] = $cfg{'cservice_email'};
						$headers["X-Mailer"] = "PHP/phpversion()";
		        
/*
			      $headers = 'From: Innovashop <' . $cfg{'cservice_email'} . ">\r\n" .
				        'Reply-To: ' . $cfg{'cservice_email'} . "\r\n" .
				        'X-Mailer: PHP/' . phpversion();
*/			      

							send_mail($to, $subject, $message_mail, $headers);
						//mail($to, $subject, $message_mail, $headers);
		      }

		      $tpl['filename'] = '/content/'.$in{'fname'}.'_confirmation.html';
					      
	      }else{
		      $va['message'] = trans_txt('reqfields_short');
	      }
      }
}


function runcmd_promo_facebook(){
#-----------------------------------------
//Last modified on 12 May 2011 10:59:00
//Last modified by: MCC C. Gabriel Varela S. : Se hace que setcookie aplique a raíz
  global $cfg,$in,$cses,$va,$tpl,$usr;

  do_for_one_product();
  
  if (!$_COOKIE["ps"] ){
	  setcookie('ps', 'On',0,'/');
	  save_callsession();
  }elseif ($_COOKIE["ps"] == 'Off'){
	  save_callsession(1);
	  setcookie('ps', 'On',0,'/');
	  header('Location:'. $cfg['signin_urlconfirm'] . $in['product'].'-fb');
  }
 
 	$pname ='';
  (stristr($in['name_link'],'colageina') !== FALSE) and ($pname = 'colageina');
 
  
  if($pname != ''){

	  if(!isset($cses['coupon_facebook'])){
	  	get_promo_facebook($pname);
	  	save_callsession();
	  }
	  $tpl['skel'] = 'default.html';
	  $tpl['pagetitle']="Innovashop tv - Promociones Facebook";	
	  $tpl['filename'] = 'cart/content/promocion_facebook/'.$pname.'.html';
  }else{
  		header('Location: /novedades-D');
  }
  
	 #print_r($cses);
}

function runcmd_gift_cards(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 26 Apr 2011 13:05:57
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $cfg,$in,$cses,$va,$tpl,$usr;
	$tpl['skel'] = 'default.html';
  $tpl['pagetitle']="Innovashop tv - Promociones Facebook";	
  $tpl['filename'] = 'cart/content/gift_cards/gift_cards.html';
}


function runcmd_ewactivation(){
# --------------------------------------------------------
# Created on: 
# Author: Roberto Barcenas
# Description : Activa la garantia en la fecha registrada por el usuario - Agrega una nota a la orden con la fecha en que la grantia se activo 
# Parameters : 
# Last Modified by RB on 04/08/2011 04:09:43 PM : Se cambia la validacion de amount por LastName1   

  global $cfg,$in,$cses,$va,$tpl,$usr,$error;

  $tpl['skel'] = 'cart_product.html';
  $tpl['filename'] = "content/extended_warranty_activation.html";


  if(isset($in['btn_activate'])){

	      $db_cols  = array('email','id_orders','order_lastname');
	      $req_cols = array('email','id_orders','order_lastname');
	      $type     = array('email','numeric','');

	      unset($va['message']);
	      $valid ='error';
	      $valid = validate_cols($db_cols,$req_cols,$type,0);

	      $xquery = mysql_query("SELECT Notes FROM sl_orders_notes WHERE ID_orders = '". intval($in['id_orders']) ."' AND Notes LIKE '". trans_txt('warranty_activated_date') ."%' ORDER BY Date LIMIT 1;");
	      if(mysql_num_rows($xquery) > 0){
		      list($note) = mysql_fetch_row($xquery);
		      $valid = 'error';
		      $va['message'] = $note;
	      }

	      if($valid == "ok"){
		      $id_orders = intval($in['id_orders']);
		      $email = trim($in['email']);
		      //$amount_paid = trim($in['order_amount']);
		      $lastname=trim($in['order_lastname']);
		      
		      
		      /*$xamount = mysql_query("SELECT SUM(Amount)AS amount_order FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Amount > 0 AND Reason='Sale' GROUP BY ID_orders;");
		      list($amount_order) = mysql_fetch_row($xamount);
		      ($amount_order == '') and ($amount_order=0);*/
		      

		      $query = "SELECT sl_customers.ID_customers,email,IF('$id_orders' = sl_orders.ID_orders AND LOWER('". mysql_real_escape_string($email) ."') = LOWER(email) AND LOWER('". mysql_real_escape_string($lastname) ."') = LOWER(LastName1),'ok',
				   IF(LOWER('". mysql_real_escape_string($email) ."') = LOWER(email) AND LOWER('". mysql_real_escape_string($lastname) ."') != LOWER(LastName1),'lastname',
				   IF(LOWER('". mysql_real_escape_string($email) ."') != LOWER(email) AND LOWER('". mysql_real_escape_string($lastname) ."') = LOWER(LastName1),'email',
				   IF(LOWER('". mysql_real_escape_string($email) ."') != LOWER(email) AND LOWER('". mysql_real_escape_string($lastname) ."') != LOWER(LastName1),'emailandlastname','unknown' )))) AS valid 
			     FROM sl_orders INNER JOIN sl_customers ON sl_customers.ID_customers = sl_orders.ID_customers
			     WHERE sl_orders.ID_orders = '$id_orders' AND sl_orders.Status = 'Shipped';";

		      $xquery = mysql_query($query);

		      $xrows = mysql_num_rows($xquery);
		      list($id_customers,$emailc,$valid_data) = mysql_fetch_row($xquery); 

		      #echo "$query<br>$valid_data    ";

		      if($xrows == 0 or $valid_data == 'unknown'){
			      $error['id_orders'] = trans_txt('invalid');
			      $va['message'] = trans_txt('reqfields_short');

		      }elseif($valid_data == 'emailandlastname' or $valid_data == 'lastname'){
			    	$error['order_lastname'] = trans_txt('invalid');
			    	$va['message'] = trans_txt('reqfields_short');
		      }else{
			      if($valid_data == 'email'){
				        mysql_query("UPDATE sl_customers SET email=TRIM('". mysql_real_escape_string($email) ."') WHERE ID_customers = '$id_customers';");
				        ($emailc != '') and (mysql_query("INSERT INTO sl_customers_notes SET ID_customers='$id_customers', Notes=CONCAT('Customer email changed From:',TRIM('". mysql_real_escape_string($emailc) ."'),' To:',TRIM('". mysql_real_escape_string($email) ."')), Type='Low', Date=CURDATE(),Time=CURTIME(),ID_admin_users='". $cfg['id_admin_users'] ."';"));
			      }
			      mysql_query("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes=CONCAT('". trans_txt('warranty_activated_date') ."',NOW()),Type='Low', Date=CURDATE(),Time=CURTIME(),ID_admin_users='". $cfg['id_admin_users'] ."';");

			      $xquery = mysql_query("SELECT Notes FROM sl_orders_notes WHERE ID_orders = '$id_orders' AND Notes LIKE '". trans_txt('warranty_activated_date') ."%' ORDER BY Date LIMIT 1;");
			      if(mysql_num_rows($xquery) > 0){
				      list($note) = mysql_fetch_row($xquery);
				      auth_logging("warranty_activated",$id_orders);
				      $va['message'] = $note;
				      $tpl['filename'] = "content/garantia.html";
			      }else{
				      $va['message'] =  trans_txt('general_error');
			      }
		      }
	      }else{
		      (!isset($va['message'])) and ($va['message'] = trans_txt('reqfields_short'));
	      }
  }
}

function runcmd_encuesta(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 12 Nov 2010 16:12:48
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $tpl,$in;
	$tpl['pagetitle']="Innovashop tv - Encuesta";	
	if(isset($in['add']) and isset($in['frequency']) and isset($in['revisit']) and isset($in['recommend']) and isset($in['meetus']))
	{
		$sth = mysql_query("Insert into nsc_surveys 
		set site='innovashop',
		frequency='".mysql_real_escape_string($in['frequency'])."',
		revisit='".mysql_real_escape_string($in['revisit'])."',
		recommend='".mysql_real_escape_string($in['recommend'])."',
		revisit_reasons_design='".mysql_real_escape_string($in['revisit_reasons_design'])."',
		revisit_reasons_product_variety='".mysql_real_escape_string($in['revisit_reasons_product_variety'])."',
		revisit_reasons_more_info='".mysql_real_escape_string($in['revisit_reasons_more_info'])."',
		revisit_reasons_prices='".mysql_real_escape_string($in['revisit_reasons_prices'])."',
		revisit_reasons_navigation='".mysql_real_escape_string($in['revisit_reasons_navigation'])."',
		revisit_reasons_promos='".mysql_real_escape_string($in['revisit_reasons_promos'])."',
		revisit_reasons_other='".mysql_real_escape_string($in['revisit_reasons_other'])."',
		revisit_reasons_none='".mysql_real_escape_string($in['revisit_reasons_none'])."',
		improvements_design='".mysql_real_escape_string($in['improvements_design'])."',
		improvements_products_variety='".mysql_real_escape_string($in['improvements_product_variety'])."',
		improvements_more_info='".mysql_real_escape_string($in['improvements_more_info'])."',
		improvements_prices='".mysql_real_escape_string($in['improvements_prices'])."',
		improvements_navigation='".mysql_real_escape_string($in['improvements_navigation'])."',
		improvements_promos='".mysql_real_escape_string($in['improvements_promos'])."',
		improvements_other='".mysql_real_escape_string($in['improvements_other'])."',
		improvements_none='".mysql_real_escape_string($in['improvements_none'])."',
		meetus='".mysql_real_escape_string($in['meetus'])."',
		improvements_text='".mysql_real_escape_string($in['suggestions'])."',
		Date=curdate(),
		Time=curtime(),
		ID_admin_users=1;
		") or die("Query failed : " . mysql_error());
		$in['message']=trans_txt('survey_thank_you');
	}
}

function runcmd_memorial_day(){
// --------------------------------------------------------
// Forms Involved: 
// Created on: 20 May 2011 15:37:02
// Author: MCC C. Gabriel Varela S.
// Description :   
// Parameters :
	global $in,$cses,$tpl;
	//Validar que esté dentro del periodo de promoción
	$sth = mysql_query("Select if(curdate() between '2011-05-20' and '2011-05-30',1,0)as valid") or die("Query failed : " . mysql_error());
	$valid_date=mysql_result($sth,0);
	if($valid_date==1)
	{
		//Validar que exista random_memorial
		if(isset($cses['random_memorial']) and $cses['random_memorial']<26)
		{
			//establecer el mínimo de compra
			if(!isset($cses['memorial_coupon']) and !isset($cses['memorial_minimum_sale']))
			{
				$minimum_external=array(5=>30,10=>50,15=>60,20=>70,25=>80);
				//Generar cupón
				$cses['memorial_coupon']=set_coupon_external('6','','',$cses['random_memorial'],$minimum_external[$cses['random_memorial']],'www.innovashop.tv/memorial_day');
				$cses['memorial_minimum_sale']=$minimum_external[$cses['random_memorial']];
				save_callsession(0);
			}
		}
	}
	else
	{
		$tpl['filename'] = '/content/memorial_day_expired.html';
		//$in['fname']='memorial_day_expired';
	}
}


function runcmd_get_taxes(){
// --------------------------------------------------------
// Forms Involved:
// Created on: 10/14/2011
// Author: RB
// Description : Regresa el valor de los taxes para un zipcode
// Parameters : zipcode

	global $in,$cfg,$tpl;

	$zip=$in['in_zipcode'];
	$ordernet=$in['in_net'];
	$sth = mysql_query("SELECT CONCAT(State,'-',StateFullName)AS State FROM sl_zipcodes WHERE Zipcode='".mysql_real_escape_string($zip)."' LIMIT 1;");
	list($state) = mysql_fetch_row($sth);

	$taxes = calculate_taxes($zip,$state);
	$total_taxes=number_format($taxes*$ordernet,2);
	unlink($tpl);
	
	echo '$'.$total_taxes.' ('.number_format($taxes*100,2).'%)';
	exit;

}


function runcmd_categorias(){
// --------------------------------------------------------
// Forms Involved:
// Created on: 10/14/2011
// Author: RB
// Description : Regresa el valor de los taxes para un zipcode
// Parameters : zipcode

  get_mobile_categories();

}


?>
