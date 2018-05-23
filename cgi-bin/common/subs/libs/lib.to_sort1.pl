
sub build_library_names {
# --------------------------------------------------------
# Created by: Rafael Sobrino
# Created on: 12/18/2007
# Description : 
# Notes : (Modified on : Modified by :)

	my ($output);
	my (@ary) = ('sub.base.html.cgi','sub.base_sltv.html.cgi');
	
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}





sub shour_to_txt {
# --------------------------------------------------------
# Author : Carlos Haas
# Notes : Also in production/sub.base.html.cgi & crm/sub.base.html.cgi
	my ($shour) = @_;
	my (@ary) = split(/,/,$cfg{'dayhour'});
	$shourtext = $ary[$shour-1];
	return $shourtext;
}


################################################################
############              ENCRYPTION             ###############
################################################################
sub LeoEncrypt {
# --------------------------------------------------------
    my ($text,$passphrase) = @_;

    return $text if $text =~ /^ok/;

    my ($holder) = chr(127);
    $text =~ s/\r//g;
    $text =~ s/\t/    /g;
    $text =~ s/\n/$holder/g;
    $text = &LeoPermute($text,$passphrase,1);
    $text =~ s/\./a/eg;
    $text =~ s/\:/b/eg;
    $text =~ s/\~/c/eg;
    $text =~ s/\-/d/eg;
    $text =~ s/\_/e/eg;
    $text =~ s/\//f/eg;
    $text =~ s/\\/g/eg;
    return 'ok' . $text;
}

sub LeoDecrypt {
# --------------------------------------------------------
    my ($text,$passphrase) = @_;

    return $text if $text !~ /^ok/;
    $text =~ s/ok//; 

    my ($holder) = chr(127);
    $text =~ s/a/./g;
    $text =~ s/b/:/g;
    $text =~ s/c/\~/g;
    $text =~ s/d/-/g;
    $text =~ s/e/_/g;
    $text =~ s/f/\//g;
    $text =~ s/g/\\/g;   
    $text =~ s/[\r\n]//g;
    $text = &LeoPermute($text,$passphrase,-1);
    $text =~ s/$holder/\n/g;
    $text =~ s/x/Z/eg;
    return $text;
}

sub LeoPermute {
# --------------------------------------------------------
    my ($text,$strphrase,$multFactor) = @_;
    my ($a,$i,$c,$phrase,@chars,%plain,$holder,$character,$new_text,$clen);
   
    #### Calculate Phrase
    while (length($strphrase) < 10) {
        $strphrase .= "x";
    }
    $a=-1;
    for (0..length($strphrase)-1){
        $phrase += $a**$_ * ord(substr($strphrase,$_,1));
        #print $a**$_ ."<br>";
        #print ord(substr($strphrase,$_,1)) ."<br>";
    }
    $phrase = abs($phrase);

    ### Built Chards Array
    undef @chars;
    $c = 'Z1A2Q3W4S5X6C7D8ERF9V0BGTYHNMJUIKLOP.:~-_/\\';
    $clen = length($c);
    for $i(0.. $clen-1) {
        push (@chars, substr($c,$i,1));
    }
    unshift(@chars, 'x');
    for ($i=0; $i<=$#chars; $i++) {
        $plain{$chars[$i]} = $i;
    }
    $holder = chr(127);
   
    ### Permute
    for my $i (0..length($text)-1){
        $character = substr($text,$i,1);
        if ($character ne $holder) {
            my $pos = $plain{$character};
            my $pos2 = abs(int(sin($i+ $phrase)*$clen));
            my $shift = $pos + $multFactor * $pos2;
            if ($shift >= $clen) {
                $shift -= $clen;
            } elsif ($shift < 0) {
                $shift += $clen;
            }
           
            $character = $chars[$shift];
            $new_text .= $character;
        }
    }
    return $new_text;
}



#############################################################################
#############################################################################
#   Function: encrip
#
#       Es: encrip. Codifica una cadena
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - this_string: cadena para codificar 
#
#  Returns:
#
#      - xs: cadena codificada
#
#
#   See Also:
#
#      <decrip>
#
sub encrip {
#############################################################################
#############################################################################

	my ($this_string) = @_;
	return $this_string if $this_string =~ /^ok/;

	my $xs = "";
	my $xc = "";
	my $xn = 0;
	my $xn2 = 0;

	for (my $i = 1; $i <= length($this_string); $i++) {

		$xc = substr ($this_string, ($i - 1), 1);
		$xn = ord ($xc);

		$xn2 = $xn;

		if (($xn >= 48) and ($xn < 58)) {

			$xn2 = (($xn + $i) > 57) ? 
					(48 + ((($xn + $i) - 58) % 10)) :
					($xn + $i);

		}elsif(($xn >= 65) && ($xn < 91)) {

			$xn2 = (($xn + $i) > 90) ?
					(65 + ((($xn + $i) - 91) % 26)) :
					($xn + $i)

		}elsif(($xn >= 97) && ($xn < 123)) {

			$xn2 = (($xn + $i) > 122) ?
					(97 + ((($xn + $i) - 123) % 26)) :
					($xn + $i);

		}

		$xs = $xs . chr($xn2);

	}

	return 'ok' . $xs;

}



################################################################
############        FINNANCE INTEGRATION         ###############
################################################################



sub lista_choice {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 9/13/2007 4:27 PM
# Last Modified on:
# Last Modified by:
# Author: Javier Claros
# Description : Build list all choices inside va var that you can used in your view products list

	if ($in{'choicename1'}){   $cont++;$ind_c =0;
		my($op1)="SELECT COUNT(\'*\') FROM (SELECT DISTINCT(choice1) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice1 != \'\') as k";
		my ($sth1) = &Do_SQL($op1);			  
		$ind_c = $sth1->fetchrow;
		my($op1)="SELECT DISTINCT(choice1) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice1 != \'\'";						
		my ($sth1) = &Do_SQL($op1);			  
		$va{'cho1'} =''; $indice=0;
		while ($rec1 = $sth1->fetchrow_hashref){			  				  	
			$va{'cho1'} .="$rec1->{'choice1'}"; $indice++;
			if($ind_c > $indice){	$va{'cho1'} .=","; 	}else{ $va{'cho1'} .=" "; }
		}			  					  			  
	}		
			if ($in{'choicename2'}){   $cont++;$ind_c =0;
				my($op1)="SELECT COUNT(\'*\') FROM (SELECT DISTINCT(choice2) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice2 != \'\') as k";
				my ($sth1) = &Do_SQL($op1);			  
				$ind_c = $sth1->fetchrow;
			  my($op1)="SELECT DISTINCT(choice2) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice2 != \'\'";						
			  my ($sth1) = &Do_SQL($op1);			  
		    $va{'cho2'} =''; $indice=0;
			  while ($rec1 = $sth1->fetchrow_hashref){			  				  	
			  	$va{'cho2'} .="$rec1->{'choice2'}"; $indice++;
			  	if($ind_c > $indice){	$va{'cho2'} .=","; 	}else{ $va{'cho2'} .=" "; }
			  }			  					  	
			}
			if ($in{'choicename3'}){   $cont++;$ind_c =0;
				my($op1)="SELECT COUNT(\'*\') FROM (SELECT DISTINCT(choice3) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice3 != \'\') as k";
				my ($sth1) = &Do_SQL($op1);			  
				$ind_c = $sth1->fetchrow;
			  my($op1)="SELECT DISTINCT(choice3) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice3 != \'\'";						
			  my ($sth1) = &Do_SQL($op1);			  
		    $va{'cho3'} =''; $indice=0;
			  while ($rec1 = $sth1->fetchrow_hashref){			  				  	
			  	$va{'cho3'} .="$rec1->{'choice3'}"; $indice++;
			  	if($ind_c > $indice){	$va{'cho3'} .=","; 	}else{ $va{'cho3'} .=" "; }
			  }			  					  	
			}
			if ($in{'choicename4'}){   $cont++;$ind_c =0;
				my($op1)="SELECT COUNT(\'*\') FROM (SELECT DISTINCT(choice4) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice4 != \'\') as k";
				my ($sth1) = &Do_SQL($op1);			  
				$ind_c = $sth1->fetchrow;
			  my($op1)="SELECT DISTINCT(choice4) FROM sl_skus  WHERE id_products = \'$in{'id_products'}\'  and choice4 != \'\'";						
			  my ($sth1) = &Do_SQL($op1);			  
		    $va{'cho4'} =''; $indice=0;
			  while ($rec1 = $sth1->fetchrow_hashref){			  				  	
			  	$va{'cho4'} .="$rec1->{'choice4'}"; $indice++;
			  	if($ind_c > $indice){	$va{'cho4'} .=","; 	}else{ $va{'cho4'} .=" "; }
			  }			  					  	
			}
}

sub format_sltvid {
# --------------------------------------------------------
	my ($id) = @_;
	if (length($id) eq 9){
		return substr($id,0,3) .'-'.substr($id,3,3) . '-' . substr($id,6,3);
	}else{
		return substr($id,0,3) .'-'.substr($id,3,3);
	}
}

sub format_account{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/16/09 16:19:08
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($account_code) = @_;
	#return substr($account_code,0,4) .'-'.substr($account_code,4,2);
	return substr($account_code,0,3) . '-' . substr($account_code,3,2) . '-' . substr($account_code,5); 
}

sub build_edit_choices {
# --------------------------------------------------------

	my ($id,$url,$param) = @_;
	my ($output,$family);
	
	if (length($id)>6){
		$family = substr($id,3,6);
	}else{
		$family = $id;
	}	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$family';");
	if ($sth->fetchrow>1){
		$output = "<a href='#tabs' id='ajax_btn' name='choices_btn' onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'tabs');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=choices&id_products=$family&url=$url&$param');\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit' alt='' border='0'></a>";
	}
	return $output;
}
sub build_edit_choices_module {
# --------------------------------------------------------

	my ($id,$url,$param,$module) = @_;
	my ($output,$family);
	
	if (length($id)>6){
		$family = substr($id,3,6);
	}else{
		$family = $id;
	}	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$family' AND Status='Active';");
	if ($sth->fetchrow>1){
		$output = "<a href='#$module' id='ajax_btn' name='choices_btn' onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'$module');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=choices&id_products=$family&url=$url&$param');\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit' alt='' border='0'></a>";
	}
	return $output;
}



sub build_catlist {
# --------------------------------------------------------
	my ($cat) = @_;
	my ($sth) = &Do_SQL("SELECT * FROM sl_categories WHERE Status='Active' ORDER BY ID_parent;");
	while ($rec = $sth->fetchrow_hashref){
		if ($rec->{'ID_parent'}>0){
			$cols{$rec->{'ID_categories'}} = '['.$rec->{'ID_parent'} .']/'. $rec->{'ID_categories'};
		}else{
			$cols{$rec->{'ID_categories'}} = $rec->{'ID_categories'};
		}
	}
	foreach $key (sort keys %cols) {
		$cols{$key} =~ s/\[([^]]+)\]/$cols{$1}/;
	}
	$output = $cat;
	foreach $key (sort {$cols{$a} cmp $cols{$b}} keys %cols ) {
		if ($cols{$key} =~ /^$cat\//){
			$output .= ",$key";
		}
	}
	return $output;
}

sub build_catroot {
# --------------------------------------------------------
	my ($cat) = @_;
	my ($ncat,$output);
	$output .= "$cat";
	$ncat = &load_name('sl_categories','ID_categories',$cat,'ID_parent');
	$output .= ",$ncat";
	while ($ncat >0){
		$ncat = &load_name('sl_categories','ID_categories',$cat,'ID_parent');
		$output .= ",$ncat";
	}
	return $output;
}





sub usps_correct_address{
## --------------------------------------------------------
	my ($address1,$address2,$city,$state,$zip5) = @_;
			use LWP::UserAgent;
			use HTTP::Request::Common;
			$ua=new LWP::UserAgent;
					
$tag = "?API=Verify&XML=<AddressValidateRequest%20USERID='384SHOPL8267'>
<Address ID='0'>
<Address1>$address1</Address1>
<Address2>$address2</Address2>
<City>$city</City>
<State>$state</State>
<Zip5>$zip5</Zip5>
<Zip4></Zip4>
</Address>
</AddressValidateRequest>";
		$tag =~ s/\n|\r//g;	
		
		# Create a request
		  my $req = HTTP::Request->new(GET => "http://Production.ShippingAPIs.com/ShippingAPI.dll$tag");
		  # Pass request to the user agent and get a response back
		  $resp = $ua->request($req);
			
	 	 	if ($resp->is_success){
 	 			$content = 	$resp->content;
 	 			
 	 			## Check Content
 	 			## resp en $ok
 	 			#($nul,$intag,$nul) = split(/<error>|<\/error/,$content,3);
 	 			if ($content =~ /^<error>(.*)/i){
 	 				$ok = 0;
 	 			}elsif($content =~ /^<addressvalidateresponse>(.*)/){
 	 				$ok =1;
 	 			}else{
 	 				$ok = 0;
 	 			}
 	 			
 	 			if ($ok){
 	 				$error{'address'} = '';
 	 				return 0;
 	 			}else{
 	 				return 1; ## Error
 	 			}
 	 			
 	 			##return ($resp->content);
 	 			
	 	 	}else{
	 	 		#Return ($resp->status_line);
	 	 		return 1; ## Error
	 	 			
	 	 	} 
}






sub chkpay_header_sp {
# --------------------------------------------------------
# Created on: 10/25/2007 11:06AM
# Author: Rafael Sobrino
# Description : Builds a header for check payments in spanish (follow-up payment tab and print)
# Notes: 
	
	my ($out) = qq |
		<tr>
			<td class='menu_bar_title'>&nbsp;</td>
			<td class='menu_bar_title'>Nombre en Cheque</td>
			<td class='menu_bar_title'>Cuenta del Banco/ Monto / Cheque</td>
			<td class='menu_bar_title'>P/C</td>
			<td class='menu_bar_title'>Fech Nacimiento<br>Licencia/Estado<br>Tel&eacute;fono</td>
			<td class='menu_bar_title'>Estado<br>Cod. Aut.</td>							
			<td class='menu_bar_title'>Monto</td>
		</tr>	|;
		
	return $out;
}

sub ccardpay_header_sp {
# --------------------------------------------------------
# Created on: 10/25/2007 11:15AM
# Author: Rafael Sobrino
# Description : Builds a header for check payments in spanish (follow-up payment tab and print)
# Notes: 
	
	my ($out) = qq |
		<tr>
			<td class='menu_bar_title'>&nbsp;</td>
			<td class='menu_bar_title'>Tipo</td>
			<td class='menu_bar_title'>Nombre en Tarjeta<br>N&uacute;mero de Tarjeta</td>
			<td class='menu_bar_title'>Exp</td>
			<td class='menu_bar_title'>CVN</td>
			<td class='menu_bar_title'>Estado<br>Cod. Aut.</td>			
			<td class='menu_bar_title'>Total</td>
		</tr>	|;
		
	return $out;
}




sub indexOf {
# --------------------------------------------------------
# Created on: 11/15/2007 2:52PM
# Author: Rafael Sobrino
# Description : finds the index of the first char 'x' found in a string
# Notes: 
	
	my ($str,$char) = @_;
	for ($i =0; $i < length($str)-1; $i++){
		if (substr($str,$i,1) eq $char){		
			return $i;
		}
	}
	return -1;
}

sub checkifcopy {
# --------------------------------------------------------
# Created on: 11/21/2007 4:28PM
# Author: Carlos Haas
# Description : Check if the order has been printed
# Notes:

}

sub format_sltvprice{
# --------------------------------------------------------
# Created on: 11/21/2007 4:28PM
# Author: Carlos Haas
# Description : Check if the order has been printed
# Notes:

	my ($num) = @_;
	if ($num =~ /^(\d+)\.(\d{2})$/){
		return "$1.$2";
	}
	return 0;
}



sub build_desc_page {
# --------------------------------------------------------
	my ($id) = @_;
	my ($status) = &load_prod_info($id);
	if ($status eq 'ok'){
		print &build_page('forms:products_fdsheet_window.html');
		return 'ok';
	}else{
		return 'error';
	}
}

sub build_smalldesc_page {
# --------------------------------------------------------
	my ($id) = @_;
	my ($status) = &load_prod_info($id);
	if ($status eq 'ok'){
		print &build_page('forms:products_dsheet_window.html');
		return 'ok';
	}else{
		return 'error';
	}
}


sub converts_in_to_va{
#-------------------------------------------------------------------------------
	foreach $key (keys %in){
		$va{$key}=$in{$key} if($in{$key});
	}
}




sub converts_cses_to_va(%cses){
#-------------------------------------------------------------------------------
# Forms Involved: 
# Created on: 07/14/08 11:45:02
# Author: MCC C. Gabriel Varela S.
# Description :  
# Parameters : 
# Last Modified on: 07/15/08 12:11:05
# Last Modified by: MCC C. Gabriel Varela S: Se pasa como parámetro cses y si no existe lo toma de cargar la sesión.

	(%cses)=@_;
	&load_callsession() if(keys %cses==0);
	foreach $key (keys %cses){
		$va{$key}=$cses{$key} if($cses{$key});
	}
}






sub operations_day{
#-----------------------------------------
# Created on: 02/04/09  12:27:32 By  Roberto Barcenas
# Forms Involved: ajaxpayments.cgi 
# Description :
# Parameters : id table, amount, #credit-card, table

	my ($idtable,$amount,$ccard,$ntable)=@_;
	my $sth;
	$sth=&Do_SQL("SELECT count(*) FROM sl_".$ntable."_payments
								WHERE ID_".$ntable." = $idtable AND DATEDIFF(AuthDateTime,CURDATE()) = 0 
								AND Amount='$amount' AND PmtField3 = '$ccard' ");

	return $sth->fetchrow;
}




sub scriptexchanges{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/25/08 17:30:22
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 12/01/08 12:51:21
# Last Modified by: MCC C. Gabriel Varela S: Se agrega &returntype=$in{'returntype'}
# Last Modified on: 12/22/08 16:00:39
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta orders
	my ($sth,$rec,$cadtoreturn,$i);
	$cadtoreturn="";
	$i=0;
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	$sth=&Do_SQL("Select *,$cadidorderproducts,$cadidorders from $cadtbproductstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'} and comefrom='Original'");
	while($rec=$sth->fetchrow_hashref)
	{
		$i++;
		$cadtoreturn.="
			<div id='popup_exchangeitem$rec->{$cadidorderproducts}' style='visibility: hidden; display: none; background-color: #ffffff;'>
				<div class='menu_bar_title' id='item_drag$rec->{$cadidorderproducts}'>
				<img id='popup_exiti$rec->{$cadidorderproducts}' src='[va_imgurl]/[ur_pref_style]/popupclose.gif' />
				&nbsp;&nbsp;&nbsp;Exchange Product ID $rec->{'ID_products'}
				</div>
				<div class='formtable'>
				<IFRAME SRC='/cgi-bin/common/apps/ajaxorder?cmd=edit_orders_additems&id_orders=$rec->{$cadidorders}&path=$in{'path'}&exchange=$rec->{$cadidorderproducts}&returntype=$in{'returntype'}&edit_type=$in{'edit_type'}' name='rcmd' TITLE='Recieve Commands' width='546' height='250' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
				<H2>Unable to do the script</H2>
				<H3>Please update your Browser</H3>
				</IFRAME>	
				</div></div>
";
	}
	$va{'cadtoprint'}=$cadtoreturn;
}







sub write_cookie{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/17/09 10:34:47
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($cname,$addvalue,$expdate,$action)=@_;
	my $prevcont;
	$expdate=($expdate*24)+5;
	my $sth=&Do_SQL("Select date_format(date_add(now(),INTERVAL $expdate HOUR),'%W,%d-%b-%Y %H:%i:%s GMT;')");
	#my $sth=&Do_SQL("Select date_format(date_add(now(),INTERVAL 301 MINUTE),'%W,%d-%b-%Y %H:%i:%s GMT;')");
	$expdate=$sth->fetchrow();
	$prevcont=&GetCookies($cname);
	if($prevcont eq "")
	{
		print "Set-Cookie: $cname=$addvalue ; expires=$expdate; path=/;\n";
	}
	elsif($prevcont!~/$addvalue/)
	{
		$prevcont.=",$addvalue";
		print "Set-Cookie: $cname=$prevcont ; expires=$expdate; path=/;\n";
	}
}



sub build_userlists {
#-----------------------------------------
# Created on: 02/19/09  16:23:05 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
# Last Modified on: 02/26/09 11:54:50
# Last Modified by: MCC C. Gabriel Varela S: Se ordena por application también. Se muestra la application.

	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE application IN ('admin','crm') AND Status='Active' ORDER BY application,LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"):
							($ext = "");
		$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'}, $rec->{'FirstName'} $ext: $rec->{'application'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub get_favorites{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/20/09 11:30:34
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($cname,$addvalue)=@_;
	my $favred,$favblue,$favgreen;
	$favred=&GetCookies($cname."red");
	$favgreen=&GetCookies($cname."green");
	$favblue=&GetCookies($cname."blue");
	#&cgierr("$cname $addvalue $favred $favgreen $favblue");
	$va{'bookmarkred'}="off";
	$va{'bookmarkgreen'}="off";
	$va{'bookmarkblue'}="off";
	$va{'bookmarkred'}="on"if($favred=~/$addvalue/);
	$va{'bookmarkgreen'}="on"if($favgreen=~/$addvalue/);
	$va{'bookmarkblue'}="on"if($favblue=~/$addvalue/);
}

sub set_favorites{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/20/09 12:31:35
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($cname,$addvalue)=@_;
	my $prevcont;
	$expdate=($expdate*24)+365;
	my $sth=&Do_SQL("Select date_format(date_add(now(),INTERVAL $expdate HOUR),'%W,%d-%b-%Y %H:%i:%s GMT;')");
	#my $sth=&Do_SQL("Select date_format(date_add(now(),INTERVAL 301 MINUTE),'%W,%d-%b-%Y %H:%i:%s GMT;')");
	$expdate=$sth->fetchrow();
	$prevcont=&GetCookies("$cname");
	#Si ya existe se quita
	if($prevcont=~/$addvalue/)
	{
		$prevcont=~s/($addvalue\,?)//g;
		print "Set-Cookie: $cname=$prevcont ; expires=$expdate; path=/;\n";
	}
	#Si no existe se pone
	elsif($prevcont!~/$addvalue/)
	{
		$prevcont.=",$addvalue";
		print "Set-Cookie: $cname=$prevcont ; expires=$expdate; path=/;\n";
	}
}

sub build_grouplists{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/23/09 13:22:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($output,$ext);
	return $options = &build_select_from_enum('user_type','admin_users');
	
	# #my ($sth) = &Do_SQL("SELECT ID_admin_users_group,Name FROM admin_users_group WHERE Status='Active' ORDER BY ID_admin_users_group");
	# my ($sth) = &Do_SQL("SELECT ID_admin_groups ,Name FROM admin_groups WHERE Status='Active' ORDER BY ID_admin_groups");
	# while ($rec = $sth->fetchrow_hashref){
		# $output .= "<option value='$rec->{'ID_admin_groups'}'>$rec->{'Name'}</option>\n";
	# }
	
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	#return $output;
}





sub transfer_warehouses{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 04/07/09 17:01:21
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 04/09/09 11:57:29
# Last Modified by: MCC C. Gabriel Varela S: Se continúa
# Last Modified on: 06/08/09 17:30:15
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para no admitir sets.
# Last Modified by RB on 06/14/2010: Se modifica por completo la funcion. Los queries se hacen uno por uno y no todos a la vez, ademas cambia la forma de resolucion
# Last Modified by RB on 06/14/2010: Se verifica la cantidad en el Warehouse From y se va descontando lo necesario por cada registro, despues se revisa la existencia en Warehouse To y se actualiza/inserta la cantidad necesaria.
# Last Modified by RB on 06/14/2010: Si la cantidad que se pretende descontar no existe en Warehouse From, el item pasa a un Warehouse de Conciliacion.
# Last Modified by RB on 12/23/2010: Se corrige forma de traspasar el sl_skus_cost, no se debe calcular el costo, se deben traspasar los registros con su costo original
# Last Modified by RB on 04/22/2013: Se agrega busqueda directa sobre el Location pack si se recibe variable
# Last Modified by RB on 04/22/2013: Se agrega metodo de descuentop FIFO | LIFO
# Last Modified by RB on 08/29/2013: Se agrega $in{'to_location'} para poder devolver un inventario a una gaveta especifica

# ToDo: Incluir el Location From para poder usarse en las transferencias en general

	my ($from_wh,$to_wh,$id_products,$qty)=@_;
	my $cost,$amountavail,$qtytoadjust,$qrystr1,$qrystr2,$newtransfer,$query,$sth,$rec;
	my $error = 0;
	#&cgierr("$from_wh,$to_wh,$id_products,$qty");
	### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
	my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
	my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

	### Escanear orden del location Pack?
	my $mod_pack = $in{'scan_from_pack'} ? " AND Location = 'pack' " : '';

	### Enviar el inventario a un location especifico?
	($in{'to_location'}) and ($in{'to_location'} = &filter_values($in{'to_location'}));
	my $mod_pack2 = $in{'to_location'} ? " AND Location = '$in{'to_location'}' " : '';
	my $to_location = $in{'to_location'} ? "$in{'to_location'}" : "A100Z";

	#################################################################
	##################para sl_warehouses_location####################
	#################################################################
	&Do_SQL("/* From Transfer Warehouse */ DELETE FROM sl_warehouses_location WHERE 1 AND ID_products=$id_products AND ID_warehouses = $from_wh AND Quantity <= 0;");
	&Do_SQL("/* From Transfer Warehouse */ DELETE FROM sl_warehouses_location WHERE 1 AND  ID_products=$id_products AND ID_warehouses = $to_wh AND Quantity <= 0;");
	&Do_SQL("/* From Transfer Warehouse */ DELETE FROM sl_skus_cost WHERE 1 AND  ID_products=$id_products  AND ID_warehouses = $from_wh AND Quantity <= 0;");
	&Do_SQL("/* From Transfer Warehouse */ DELETE FROM sl_skus_cost WHERE 1 AND  ID_products=$id_products  AND ID_warehouses = $to_wh AND Quantity <= 0;");

	$sth = &Do_SQL("SELECT SUM(Quantity) AS Quantity,SUM(IF(Isset='Y',1,0)) AS SumY 
					FROM sl_warehouses_location 
					INNER JOIN sl_skus ON(sl_warehouses_location.ID_products=sl_skus.ID_sku_products)
					WHERE sl_warehouses_location.ID_products='$id_products' 
					AND ID_warehouses = '$from_wh';");
	($amountavail,$sumy)=$sth->fetchrow_array;

	if($qty <= $amountavail and $sumy==0){
			$qtytoadjust=$qty;
			$sth = &Do_SQL("SELECT *
							FROM sl_warehouses_location 
							WHERE ID_products = '$id_products' 
							AND ID_warehouses = '$from_wh'
							$mod_pack
							AND Quantity > 0 
							ORDER BY Date $invout_order;");

			while($rec=$sth->fetchrow_hashref and $qtytoadjust > 0){

					if($qtytoadjust < $rec->{'Quantity'}){
							#Se ajusta fila en Wareouse FROM
							&Do_SQL("/* From Transfer Warehouse */ UPDATE sl_warehouses_location SET Quantity = Quantity - $qtytoadjust WHERE 1 AND ID_warehouses_location = '$rec->{'ID_warehouses_location'}' AND ID_warehouses = '$from_wh';");
							$qtytoadjust = 0;
							&sku_logging($id_products,$from_wh,$rec->{'Location'},'Sale',0,'sl_orders',$qtytoadjust);
					}else{
							#Se Elimina fila en Warehouse From
							&Do_SQL("/* From Transfer Warehouse */ DELETE FROM sl_warehouses_location WHERE 1 AND ID_warehouses_location = '$rec->{'ID_warehouses_location'}' AND ID_warehouses = '$from_wh';");
							$qtytoadjust -= $rec->{'Quantity'};
							&sku_logging($id_products,$from_wh,$rec->{'Location'},'Sale',0,'sl_orders',$rec->{'Quantity'});
					}
			}

			## Si $qtytoadjust > 0 , error  Ticket#2013101710000111 — 
			if($qtytoadjust > 0){
				$error = 0;
			}
			
			#Se ajusta/inserta fila en Warehouse To
			my ($sths) = &Do_SQL("SELECT ID_warehouses_location, Location FROM sl_warehouses_location WHERE ID_warehouses = '$to_wh' AND ID_products = '$id_products' AND Quantity > 0 $mod_pack2 ORDER BY Date $invout_order;");
			my ($idwl, $location) = $sths->fetchrow();

			if($idwl > 0){
					&Do_SQL("/* From Transfer Warehouse */ UPDATE sl_warehouses_location SET Quantity = Quantity + $qty WHERE 1 AND ID_warehouses_location = '$idwl' AND ID_warehouses = '$to_wh' AND ID_products = '$id_products' AND Quantity > 0 $mod_pack2 ORDER BY Date $invout_order LIMIT 1;");
			}else{
					&Do_SQL("/* From Transfer Warehouse */ INSERT INTO sl_warehouses_location SET ID_products='$id_products', ID_warehouses='$to_wh',Location='$to_location', Quantity='$qty', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};");
			}
			&sku_logging($id_products,$to_wh,$location,'Sale',0,'sl_orders',$qty);
	
	}else{
			&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Invalid Warehouse Location Quantity $in{'e'}","From Warehouse:$from_wh\r\nTo Warehouse:$to_wh\r\nID_product:$id_products\r\nID_orders:$in{'id_orders'}");
			#$to_wh = &load_name('sl_warehouses','Name','Conciliation','ID_warehouses');	
			$sthil = &Do_SQL("/* From Transfer Warehouse WL Failed*/ INSERT INTO sl_warehouses_location SET ID_products='$id_products', ID_warehouses='$to_wh',Location='999999', Quantity='$qty', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};");
			&auth_logging('bad_wlocation',$sthil->{'mysql_insertid'});
			$error = 0;
	}

		
	#######################################################
	#################para sl_skus_cost#####################
	#######################################################

	$sth = &Do_SQL("SELECT sum(Quantity) as Quantity,sum(if(Isset='Y',1,0)) as SumY 
					FROM sl_skus_cost 
					INNER JOIN sl_skus on(sl_skus_cost.ID_products=sl_skus.ID_sku_products)
					WHERE sl_skus_cost.ID_products='$id_products' 
					AND ID_warehouses = $from_wh;");
	($amountavail,$sumy)=$sth->fetchrow_array;

	if($qty<=$amountavail and $sumy==0){
			$qtytoadjust=$qty;
			$sth = &Do_SQL("SELECT *
							FROM sl_skus_cost 
							WHERE ID_warehouses = '$from_wh' 
							AND ID_products = '$id_products' 
							AND Quantity > 0 ORDER BY Date $invout_order;");
			while($rec=$sth->fetchrow_hashref and $qtytoadjust > 0){

					if($qtytoadjust < $rec->{'Quantity'}){
							#Se ajusta fila en Warehouse From
							&Do_SQL("/* From Transfer Warehouse */ UPDATE sl_skus_cost SET Quantity = Quantity - $qtytoadjust WHERE 1 AND ID_skus_cost = '$rec->{'ID_skus_cost'}' AND ID_warehouses = '$from_wh';");
							
							#Se ajusta/inserta fila en Warehouse To
							my ($sths) = &Do_SQL("SELECT ID_skus_cost,Cost FROM sl_skus_cost WHERE ID_warehouses = '$to_wh' AND ID_products = '$id_products' AND Quantity > 0 ORDER BY Date $invout_order LIMIT 1;");
							if($sths->rows() > 0){
									my($idscost,$scost) = $sths->fetchrow();
									if($scost == $rec->{'Cost'}){
											&Do_SQL("/* From Transfer Warehouse */ UPDATE sl_skus_cost SET Quantity = Quantity + $qtytoadjust WHERE 1 AND ID_skus_cost = '$idscost' AND ID_warehouses = '$to_wh' AND ID_products = '$id_products';");
									}else{
											&Do_SQL("/* From Transfer Warehouse 1 */ INSERT INTO sl_skus_cost SET ID_products='$id_products',ID_purchaseorders=0,ID_warehouses='$to_wh',Tblname='transfer', Quantity='$qtytoadjust', Cost='$rec->{'Cost'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};");
									}
							}else{
									&Do_SQL("/* From Transfer Warehouse 2 */ INSERT INTO sl_skus_cost SET ID_products='$id_products',ID_purchaseorders=0,ID_warehouses='$to_wh',Tblname='transfer', Quantity='$qtytoadjust', Cost='$rec->{'Cost'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};");
							}
							
							$qtytoadjust = 0;
					
					}else{
							#Se Actualiza fila en Warehouse From
							&Do_SQL("/* From Transfer Warehouse */ UPDATE sl_skus_cost SET ID_warehouses = '$to_wh' WHERE 1 AND ID_skus_cost = '$rec->{'ID_skus_cost'}' AND ID_warehouses = '$from_wh';");
							$qtytoadjust -= $rec->{'Quantity'};
					}

			}
			## Si $qtytoadjust > 0 , error
			if($qtytoadjust > 0){
				$error =  0;
			}
	
	}else{
			my $cost_adj = 0;
			($cost, $cost_adj) = load_sltvcost($id_products);
			&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","Invalid Sku Cost Quantity $in{'e'}","From Warehouse:$from_wh\r\nTo Warehouse:$to_wh\r\nID_product:$id_products\r\nID_orders:$in{'id_orders'}");
			#$to_wh = &load_name('sl_warehouses','Name','Conciliation','ID_warehouses');	
			$sthil = &Do_SQL("/* From Transfer Warehouse 3 SC Failed*/ INSERT INTO sl_skus_cost SET ID_products='$id_products',ID_purchaseorders='0',ID_warehouses='$to_wh',Tblname='transfer', Quantity='$qty', Cost='$cost', Cost_Adj='$cost_adj', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};");
			&auth_logging('bad_scost',$sthil->{'mysql_insertid'});
			$error = 0;
	}
	
	
	if(!$error){
		return 0;
	}else{
		return $error;
	}

}


sub hasreturn_ajax{
#-----------------------------------------
# Created on: 04/13/09  11:30:11 By  Roberto Barcenas
# Forms Involved: 
# Description : Returns a link to check the returns an order has in ajax window
# Parameters : 

	my ($id_orders,$mod) = @_;
	my ($str)	=	'';
	$str = qq|<a href="javascript:return false;" id='ajax_rtn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'idorder');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_viewreturns&id_orders=$id_orders&module=$mod');"><img src='$va{'imgurl'}/$usr{'pref_style'}/return.gif' title='View Returns' alt='' border='0'></a>| if &check_returns($id_orders) ne 'OK';
	return $str;
}


#########################################################################################################
#########################################################################################################
#
#	Function: inventory_all
#   		
#		sp: Version alternativa de inventory_by_id Devuelve hash con informacion de inventario/apartado por producto.
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_products: It ould be zero to bring all data
#		id_warehouses, nopack, include_all: Filters
#
#   	Returns:
#		None
#
#   	See Also:
#
sub inventory_all {
#########################################################################################################
#########################################################################################################

	use Data::Dumper;

	my ($id_products, $id_warehouses, $nopack, $include_all) = @_;
	my %response;


	if (!$id_products or ($id_products > 400000000 and $id_products < 500000000) ){

		###############
		###############
		### 1) Quantity In Warehouses
		###############
		###############

		my $modquery;
		$modquery .= " AND sl_warehouses_location.ID_products = '". $id_products ."' " if ($id_products);
		$modquery .= " AND sl_warehouses_location.ID_warehouses = '". $id_warehouses ."' " if ($id_warehouses > 0);
		$modquery .= " AND sl_warehouses_location.Location <> 'PACK' " if ($nopack);
		$modquery .= " AND sl_warehouses.Type = 'Physical'" if (!$include_all);

		my $query = "SELECT
						ID_sku_products
						, SUM(Quantity)as Quantity
					FROM 
						sl_skus
						INNER JOIN sl_warehouses_location ON sl_warehouses_location.ID_products=sl_skus.ID_sku_products
						INNER JOIN sl_warehouses USING(ID_warehouses)
						INNER JOIN sl_locations ON sl_locations.Code = sl_warehouses_location.Location AND sl_locations.ID_warehouses = sl_warehouses_location.ID_warehouses
					WHERE 
						1
						$modquery
						AND sl_skus.Status = 'Active'
						AND sl_warehouses.Status='Active'
						AND sl_locations.Status='Active'
					GROUP 
						BY sl_warehouses_location.ID_products ORDER BY ID_sku_products;";
		my ($sth) = &Do_SQL($query);
		while(my ($this_id_products, $this_inventory) = $sth->fetchrow()){

			my $this_link = "<span name='ajax_inv".$this_id_products."' id='ajax_inv".$this_id_products."'>&nbsp;</span>&nbsp;
						<a class=\"scroll\" href=\"#ajax_inv".$this_id_products."\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'screen-center', -1, -1,'ajax_inv".$this_id_products."');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=".$this_id_products."&cols=ID,Warehouse,In Batch,Qty&extradata=".$id_warehouses.":".$nopack.":".$include_all."');\">
			  				<img id='idajax_inv".$this_id_products."' src='[va_imgurl]/[ur_pref_style]/b_view.png' title='More Info' alt='More Info' border='0'>
			  			</a>" if(!$in{'print'});


			$response{$this_id_products} = {
				'inventory' => $this_inventory
			};

		}
		

		###############
		###############
		### 2) Quantity In Batches (On Hold)
		###############
		###############
		my $modquery = $id_products ? " AND 400000000 + sl_skus_parts.ID_parts = '". $id_products ."' " : '';
		my $delivery_zones = &load_name('sl_warehouses', 'ID_warehouses', $id_warehouses, 'DeliveryZones'); ## All zones in Warehouse
		my $modquery_zones = $delivery_zones ? " AND sl_orders.ID_zones IN (". $delivery_zones .") " : '';

		my $query = "SELECT 
						(400000000 + sl_skus_parts.ID_parts)ID_parts, 
						(COUNT(*) * sl_skus_parts.Qty)ProducsInBatch
					FROM
					(
						SELECT ID_warehouses_batches FROM sl_warehouses_batches 
						WHERE sl_warehouses_batches.Status IN ('New','Assigned','Processed')

					)sl_warehouses_batches 
					INNER JOIN 
					(
						SELECT ID_warehouses_batches, ID_orders_products FROM sl_warehouses_batches_orders
						WHERE sl_warehouses_batches_orders.Status IN ('In Fulfillment')
					)sl_warehouses_batches_orders 
						USING(ID_warehouses_batches)
					INNER JOIN sl_orders_products USING(ID_orders_products)
					INNER JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products=sl_orders_products.ID_products
					INNER JOIN sl_orders USING(ID_orders)
					WHERE 1
					$modquery 
					$modquery_zones
					GROUP BY sl_skus_parts.ID_parts ORDER BY sl_skus_parts.ID_parts;";
		my ($sth) = &Do_SQL($query);
		while(my ($this_id_products, $this_inventory_in_batch) = $sth->fetchrow()){
		
			if(exists($response{$this_id_products})){
			
				$response{$this_id_products}{'inbatch'} = $this_inventory_in_batch;

			}

		}

	}			

	return %response;
}


#########################################################################################################
#########################################################################################################
#
#	Function: inventory_all_auto
#   		
#		sp: Version alternativa de inventory_by_id Devuelve hash con informacion de inventario/apartado por producto.
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_products: It ould be zero to bring all data
#		id_warehouses, nopack, include_all: Filters
#
#   	Returns:
#		None
#
#   	See Also:
#
sub inventory_all_auto {
#########################################################################################################
#########################################################################################################

	use Data::Dumper;

	my ($id_products, $id_warehouses, $nopack, $include_all) = @_;
	my %response;


	if (!$id_products or ($id_products > 400000000 and $id_products < 500000000) ){

		###############
		###############
		### 1) Quantity In Warehouses
		###############
		###############

		my $modquery;
		$modquery .= " AND sl_warehouses_location.ID_products = '". $id_products ."' " if ($id_products);
		$modquery .= " AND sl_warehouses_location.ID_warehouses = '". $id_warehouses ."' " if ($id_warehouses > 0);
		$modquery .= " AND sl_warehouses_location.Location <> 'PACK' " if ($nopack);
		$modquery .= " AND sl_warehouses.Type = 'Physical'" if (!$include_all);

		my $query = "SELECT
						ID_sku_products
						, SUM(Quantity)as Quantity
					FROM 
						sl_skus
						INNER JOIN sl_warehouses_location ON sl_warehouses_location.ID_products=sl_skus.ID_sku_products
						INNER JOIN sl_warehouses USING(ID_warehouses)
						INNER JOIN sl_locations ON sl_locations.Code = sl_warehouses_location.Location AND sl_locations.ID_warehouses = sl_warehouses_location.ID_warehouses
					WHERE 
						1
						$modquery
						AND sl_skus.Status = 'Active'
						AND sl_warehouses.Status='Active'
						AND sl_locations.Status='Active'
					GROUP 
						BY sl_warehouses_location.ID_products ORDER BY ID_sku_products;";
		my ($sth) = &Do_SQL($query);
		while(my ($this_id_products, $this_inventory) = $sth->fetchrow()){

			my $this_link = "<span name='ajax_inv".$this_id_products."' id='ajax_inv".$this_id_products."'>&nbsp;</span>&nbsp;
						<a class=\"scroll\" href=\"#ajax_inv".$this_id_products."\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'screen-center', -1, -1,'ajax_inv".$this_id_products."');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=".$this_id_products."&cols=ID,Warehouse,In Batch,Qty&extradata=".$id_warehouses.":".$nopack.":".$include_all."');\">
			  				<img id='idajax_inv".$this_id_products."' src='[va_imgurl]/[ur_pref_style]/b_view.png' title='More Info' alt='More Info' border='0'>
			  			</a>" if(!$in{'print'});


			$response{$this_id_products} = {
				'inventory' => $this_inventory,
				'freeinventory' => $this_inventory
			};

		}
		

		###############
		###############
		### 2) Quantity In In Fulfillment
		###############
		###############
		my $modquery = $id_products ? " AND 400000000 + sl_skus_parts.ID_parts = '". $id_products ."' " : '';

		my $delivery_zones = &load_name('sl_warehouses', 'ID_warehouses', $id_warehouses, 'DeliveryZones');
		my $modquery_zones = ( $delivery_zones ne '' ) ? " AND sl_orders.ID_zones IN(".$delivery_zones.")" : "";

		my $query = "SELECT 
						(400000000 + sl_skus_parts.ID_parts)ID_parts, 
						(COUNT(*) * sl_skus_parts.Qty)ProducsInFulfillment
					FROM
						sl_orders
					INNER JOIN sl_orders_products USING(ID_orders)
					INNER JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products = sl_orders_products.ID_products
					WHERE 1
						AND sl_orders.Status = 'Processed' 
						AND sl_orders.StatusPrd = 'In Fulfillment' 
						AND sl_orders_products.Status = 'Active' 
					$modquery 
					$modquery_zones
					GROUP BY sl_skus_parts.ID_parts ORDER BY sl_skus_parts.ID_parts;";
		
		my ($sth) = &Do_SQL($query);
		while(my ($this_id_products, $this_inventory_infulfillment) = $sth->fetchrow()){
		
			if(exists($response{$this_id_products})){
			
				$response{$this_id_products}{'infulfillment'} = $this_inventory_infulfillment;
				$response{$this_id_products}{'freeinventory'} = ($response{$this_id_products}{'freeinventory'} - $this_inventory_infulfillment) >= 0 ? $response{$this_id_products}{'freeinventory'} - $this_inventory_infulfillment : 0;
				#undef $response{$this_id_products} if $response{$this_id_products}{'freeinventory'} == 0;

			}

		}

	}			

	#print Dumper(\%response);
	#exit;
	return %response;
}



sub inventory_by_id{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/18/09 16:52:14
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 05/19/09 13:37:40
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar si es set.
# Last Modified RB: 08/13/09  13:54:12 - Solamente se muentran la unidades de inventario si no es set

	my ($id_products,$id_warehouses,$nopack,$include_all) = @_;

	if ($id_products > 400000000 and $id_products < 500000000){

		###############
		###############
		### 1) Quantity In Warehouses
		###############
		###############

		my $modquery;
		$modquery .= " AND sl_warehouses_location.ID_warehouses = $id_warehouses" if ($id_warehouses>0);
		$modquery .= " AND sl_warehouses_location.Location<>'PACK'" if ($nopack);
		$modquery .= " AND sl_warehouses.Type = 'Physical'" if (!$include_all);


		my ($sth) = &Do_SQL("SELECT SUM(Quantity)as Quantity,Isset 
		FROM sl_skus
		INNER JOIN sl_warehouses_location ON sl_warehouses_location.ID_products=sl_skus.ID_sku_products
		INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_location.ID_warehouses
		INNER JOIN sl_locations ON sl_locations.Code=sl_warehouses_location.Location AND sl_locations.ID_warehouses=sl_warehouses_location.ID_warehouses
		WHERE sl_warehouses_location.ID_products = '$id_products'
		$modquery
		AND sl_skus.Status='Active'
		AND sl_warehouses.Status='Active'
		AND sl_locations.Status='Active'
		GROUP BY sl_warehouses_location.ID_products;");
		$rec=$sth->fetchrow_hashref;
		$inventory = &format_number($rec->{'Quantity'})	if $rec->{'Isset'} ne 'Y';


		###############
		###############
		### 2) Quantity In Batches (On Hold)
		###############
		###############
		my ($qty_inbatch) = &skus_quantity_inbatch($id_products);



		###############
		###############
		### 3) Link
		###############
		###############

		$linky = "<span name='ajax_inv$id_products' id='ajax_inv$id_products'>&nbsp;</span>&nbsp;
					<a class=\"scroll\" href=\"#ajax_inv$id_products\" onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'screen-center', -1, -1,'ajax_inv$id_products');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=inventory&id_products=$id_products&cols=ID,Warehouse,In Batch,Qty&extradata=$id_warehouses:$nopack:$include_all');\">
			  			<img id='idajax_inv$id_products' src='[va_imgurl]/[ur_pref_style]/b_view.png' title='More Info' alt='More Info' border='0'>
			  	</a>" if(!$in{'print'});
		

		return ("$linky",$rec->{'Quantity'},$qty_inbatch);
	}
}

sub build_autocomplete_manifest{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/20/09 12:12:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 06/08/09 13:22:50
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para no mostrar 
# Last Modified by RB on 08/24/2010: Se agrega la funcion set_group_wlocation que agrupa todos los registros en uno solo
# Last Modified by RB on 12/23/2010: Se comenta la agrupacion en un solo registro, ahora se agrupara de otra forma.

	#&set_group_wlocation();

	$sth=&Do_SQL("SELECT ID_warehouses_location,sl_warehouses_location.ID_products as ID,
				IF(NOT ISNULL(sl_products.Model),sl_products.Model,sl_parts.Model)as Model,
				IF(NOT ISNULL(sl_products.Name),sl_products.Name,sl_parts.Name)as Name,
				Quantity,
				sl_warehouses_location.Location
				FROM sl_warehouses_location 
				INNER JOIN sl_skus on(sl_warehouses_location.ID_products=sl_skus.ID_sku_products)
				LEFT JOIN sl_products on(RIGHT(sl_warehouses_location.ID_products,6)=sl_products.ID_products and sl_warehouses_location.ID_products like '1%')
				LEFT JOIN sl_parts on(RIGHT(sl_warehouses_location.ID_products,4)=sl_parts.ID_parts and sl_warehouses_location.ID_products like '4%' )
				WHERE ID_warehouses='$in{'id_warehouses'}' 
				AND Isset!='Y'
				AND sl_warehouses_location.Quantity>0 
				ORDER BY Quantity DESC;");
	my $id_warehouses_location,$id,$model,$name,$qty,$location,$output;
	my @tmpo,$i=0;
	$output="";
	while(($id_warehouses_location,$id,$model,$name,$qty,$location)=$sth->fetchrow_array)
	{
		$name=~s/\"|,//g;
		$model=~s/\"|,//g;
		#$tmpo[$i]="\"$id $name $model\"";
		$tmpo[$i]="{name: \"$id $name $model ".&load_choices($id)." x $qty \@ $location \", id: $id_warehouses_location}";
		$output.="";
		++$i;
	}
	$output=join(',',@tmpo);
	$output="[$output]";
	return $output;
}

sub write_to_list{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/08/09 10:48:09
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 07/17/09 11:34:52
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para comparar sin importar minúsculas a la hora de insertar nuevas listas
# Last Modified on: 10/19/09 13:29:45
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se tome el nombre completo de la lista.
#TO DO: REVISAR EL QUERY PARA INSERTAR POR GRUPO
	my ($listname,$command,$user,$group,$id,$tablename)=@_;
	#Obtener los elementos actuales de la lista.
	my $actvalues=&build_autocomplete_from_enum('Name','sl_lists');
	
	#Si no existe la lista
	if($actvalues!~/\"$listname\"/i)
	{
		my $newvalue,$first;
		$newvalue=lc($listname);
		$newvalue=~/(\w{1})/;
		$first=uc($1);
		$newvalue=~s/(\w{1})/$first/;
		$actvalues=~s/\[|\]//g;
		$actvalues=~s/\"/\'/g;
		$actvalues.=",'".$newvalue."'";
		$sth=&Do_SQL("ALTER TABLE `sl_lists` CHANGE `Name` `Name` ENUM( $actvalues ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL");
	}
	my $cadcmd=$command;
	$cadcmd=~/(.+)_(.+)/;
	$cmdn = $command;
	$cmdn =~	s/(.+_)//g;
	#&cgierr("$1 y $2 y $cmdn   --- $command");
	if($user){
		my ($sthil) = &Do_SQL("INSERT INTO sl_lists set Name='$listname',ID_table='$id',cmd='$cmdn',ID_users=$user,tbl_name='$tablename',Status='Active',Date=Curdate(),Time=now(),ID_admin_users=$usr{'id_admin_users'}");
		&auth_logging('list_added',$sthil->{'mysql_insertid'});
	}	
	if($group){
		my ($tmp_sthil2) = &Do_SQL("select ID_admin_users from admin_users where Status='Active' and user_type='$group'");
		
		while ( my($tmp_id_admin_users) = $tmp_sthil2->fetchrow_array() )
		{
			my ($sthil2) = &Do_SQL("INSERT INTO sl_lists (Name,ID_table,cmd,ID_users,tbl_name,Status,Date,Time,ID_admin_users) values ('$listname','$id','$cmdn','$tmp_id_admin_users','$tablename','Active',Curdate(),now(),$usr{'id_admin_users'} )");
			&auth_logging('list_added',$sthil2->{'mysql_insertid'});
		}
	}
}



sub get_cod_delivery_dates{
#-----------------------------------------
# Created on: 07/09/09  18:07:14 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 

	my ($zipcode) = @_;	
	my $strout = '';
	
	my ($sth) = &Do_SQL("SELECT Name,Delivery_days,Delivery_hours,IF(service_days=0,'N/A',service_days) FROM sl_deliveryschs WHERE Zip = '$zipcode' AND Status='Active';");	
	
	while(my ($codagents,$dates,$hours,$sdays) = $sth->fetchrow()){
		$codtakes = 'MO';
		$codtakes .= ',Efectivo' if $codagents !~ /ups|iw|fedex/i;
		$strout .= '<tr><td align="left">'.$codagents.'</td>';
		$strout .= '<td>'.$dates.'</td>';
		$strout .= '<td>'.$hours.'</td>';
		$strout .= '<td align="center">'.$sdays.'</td>';
		$strout .= '<td align="right">'.$codtakes.'</td></tr>';

	}
	return $strout;
}



sub payments_of_postdated{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/10/09 17:52:55
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 07/13/09 13:56:30
# Last Modified by: MCC C. Gabriel Varela S: Se continúa.
# Last Modified on: 07/14/09 11:59:18
# Last Modified by: MCC C. Gabriel Varela S: Se hacen modificaciones generales.
# Last Modified on: 07/20/09 09:51:21
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se evalúe el posted date para hacer una de las siguientes acciones:
#1.Cobrar
#2.Mandar a lista de paymentdate inválido
#3.Mandar a lista de paymentdate atrasado
# Last Modified by RB on 10/12/2010: Se agrega 600000000 al postdatedfeid para la comparacion. Tambien se agrega envio de correo a la gente de Recuperaciones y se cambia sale por auth


	my $str_mail;

	require "cybersubs.cgi";
	my $sth=&Do_SQL("Select *,if(Paymentdate='0000-00-00' or isnull(Paymentdate) or Paymentdate='','Invalid',if(Paymentdate<curdate(),'not_on_time',if(Paymentdate=curdate(),'make_payment','Other')))as todo
from sl_orders_payments
INNER JOIN sl_orders on (sl_orders_payments.ID_orders=sl_orders.ID_orders)
INNER JOIN (Select sl_orders_products.ID_orders
            from sl_orders_products
            INNER JOIN sl_orders_payments on (sl_orders_products.ID_orders=sl_orders_payments.ID_orders and SalePrice=Amount)
            where ID_products=600000000+$cfg{'postdatedfeid'}
            and Captured='Yes'
            and Capdate!='' and NOT ISNULL(Capdate) and Capdate!='0000-00-00'
            and Authcode!=''
            and Authdatetime!=''
            and sl_orders_products.Status='Active'
            and sl_orders_payments.Status='Approved'
            and Reason='Sale')as sub on (sl_orders_payments.ID_orders=sub.ID_orders)
where sl_orders.Status='New'
and StatusPay='Post-Dated'
and StatusPrd='None'
and Type='Credit-Card'
and PmtField3!='' and NOT ISNULL(PmtField3)
and AuthCode=''
and Authdatetime=''
and (Captured='No' or isnull(Captured))
and (Capdate='' or isnull(Capdate) or Capdate='0000-00-00')
and sl_orders_payments.Status='Approved'
and Reason='Sale'
and Paymentdate<=Curdate()
and Amount>0");
	while(my $rec=$sth->fetchrow_hashref)
	{
		$id_orders=$rec->{'ID_orders'};
		$id_orders_payments=$rec->{'ID_orders_payments'};
		if($rec->{'todo'}eq'make_payment')
		{
			my ($status,$msg,$code) = &sltvcyb_auth($id_orders,$id_orders_payments);
			if ($status eq 'OK')
			{
				&Do_SQL("update sl_orders set status='Processed',StatusPay='None' where ID_orders=$id_orders;");
				#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='Se procesa primer pago despu&oacute;s de postdated.', Type='Low', Date=Curdate(), Time=Now(), ID_admin_users='$usr{'id_admin_users'}'");
				&add_order_notes_by_type($id_orders,"Se procesa primer pago despu&oacute;s de postdated.","Low");
			}
			else
			{
				$str_mail .= "Orden: $id_orders\nMonto: $rec->{'Amount'}\nRazon:$msg\r\n\r\n";
				#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='El pago postdated no pudo ser procesado.', Type='Low', Date=Curdate(), Time=Now(), ID_admin_users='$usr{'id_admin_users'}'");
				&add_order_notes_by_type($id_orders,"El pago postdated no pudo ser procesado.","Low");

				&write_to_list($rec->{'todo'},'orders',2241,0,$id_orders,'sl_orders');
				&write_to_list($rec->{'todo'},'orders',2221,0,$id_orders,'sl_orders');
			}
		}
		else
		{
			#&write_to_list($rec->{'todo'},'orders',2241,0,$id_orders,'sl_orders');
			#&write_to_list($rec->{'todo'},'orders',2221,0,$id_orders,'sl_orders');
		}
	}

	### Enviamos correo con ordenes que no pudieron autorizarse
	if($str_mail ne ''){
		&send_text_mail($cfg{'from_email'},"cjmendoza\@inovaus.com","PostDated Fallidas","\r\n$str_mail");
		&send_text_mail($cfg{'from_email'},"rgomezm\@inovaus.com","PostDated Fallidas","\r\n$str_mail");
	}

}

sub calc_parts_inventory{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 07/15/09 16:21:13
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($id_products)=@_;
	my $sth=&Do_SQL("SELECT /*ID_sku_products,choice1,choice2,choice3,choice4,VendorSKU,ID_warehouses,*/sum(Quantity) as Quantity 
FROM sl_skus INNER JOIN sl_warehouses_location on(sl_skus.ID_sku_products=sl_warehouses_location.ID_products  )
WHERE ID_sku_products='$id_products' 
AND Quantity!=0 
group by sl_skus.ID_sku_products;");
	return $sth->fetchrow;
}



sub export_file_format{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/10/09 17:31:23
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my $radios="<tr>\n
					<td align='left'>Other exports  :</td>\n
				<td>\n";
	for(0..9){
		$cfgname="exportfile".$_."_name";
		if($cfg{$cfgname}){
			$radios.="<input type='radio' name='page' value='exportfile".$_."' class='radio'> $cfg{$cfgname}<br>"
		}
	}
	$radios.="</td>\n</tr>\n";
	return $radios;
}


sub build_export_setup{
#-----------------------------------------
# Created on: 09/11/09  13:04:13 By  Roberto Barcenas
# Forms Involved: 
# Description : Genera un archivo de exportacion basado en configuracion del setup.cfg|general.cfg
# Parameters : exportfile$i_name,exportfile$i_fields
	
	my ($prefix,@ids) = @_;
	
	my $titles  = &filter_values($in{'page'}).'_titles';
	my $columns = &filter_values($in{'page'}).'_fields';
	my @header_fields = split(/,/,$cfg{$titles});
	my @db_fields = split(/,/,$cfg{$columns});
	my $ncols = $#header_fields;
	
	
	my $fname   =	'exportfile_sosl_';
		
	($in{'e'} eq '1') and ($fname =~	s/sosl/usa/);
	($in{'e'} eq '2') and ($fname =~	s/sosl/pr/);
	($in{'e'} eq '3') and ($fname =~	s/sosl/training/);
	($in{'e'} eq '4') and ($fname =~	s/sosl/gts/);
	$fname =~	s/\///g;

	print "Content-type: application/vnd.ms-excel\n";
	print "Content-disposition: attachment; filename=$fname".&get_date()."_export.csv\n\n";
	
	print "$cfg{$titles}\r\n";
	
	
	for my $i(0..$#ids){
		my ($sth) = &Do_SQL("SELECT 
		sl_orders.ID_orders AS ID_orders,
		shp_name,
		shp_Address1,
		shp_Address2,
		shp_Address3,
		shp_Urbanization,
		shp_City,
		shp_State,
		shp_Zip,
		shp_Country,
		ID_pricelevels,
		DNIS,
		ID_salesorigins,
		shp_Notes,
		sl_orders.Status AS OrderStatus,
		sl_orders.Date AS OrderDate,
		sl_customers.*,
		ID_products,
		Items,
		SumItem,
		SumService,
		SumTax,
		SumShipping,
		SumDiscount,
		tmpprod.OrderNet AS OrderNet,
		OrderTotal,
		NumItems,
		QtyItems,
		PayType,
		SumPayments,
		QtyPayments
FROM sl_orders
INNER JOIN
sl_customers
ON sl_orders.ID_customers = sl_customers.ID_customers 
INNER JOIN
(
  SELECT 
     ID_orders,
     GROUP_CONCAT(RIGHT(ID_products,6)) AS ID_products,
     GROUP_CONCAT(ID_products SEPARATOR '|') AS Items,
     SUM(IF(LEFT(ID_products,1) <> '6',SalePrice,0))AS SumItem,
     SUM(IF(LEFT(ID_products,1) = '6',SalePrice,0))AS SumService,
     SUM(Tax)AS SumTax,
     SUM(Shipping)AS SumShipping,
     SUM(Discount)AS SumDiscount,
     SUM(SalePrice-Discount)AS OrderNet,
     SUM(SalePrice-Discount+Shipping+Tax)AS OrderTotal,
     COUNT(ID_products) AS NumItems,
     GROUP_CONCAT(Quantity SEPARATOR '|') AS QtyItems
  FROM sl_orders_products 
  WHERE ID_orders = '$ids[$i]' AND Status NOT IN('Order Cancelled','Inactive') GROUP BY ID_orders
)AS tmpprod
ON tmpprod.ID_orders = sl_orders.ID_orders
INNER JOIN
(
  SELECT 
     ID_orders,
     Type AS PayType,
     SUM(Amount)AS SumPayments,
     COUNT(*)AS QtyPayments
  FROM sl_orders_payments 
  WHERE ID_orders = '$ids[$i]' AND Status NOT IN('Order Cancelled', 'Cancelled')
  GROUP BY ID_orders
)AS tmppay
ON tmppay.ID_orders = sl_orders.ID_orders
WHERE sl_orders.ID_orders='$ids[$i]';");

		while ($rec = $sth->fetchrow_hashref()){
			my (@cols);
			
			### Llenamos el arreglo
			for my $i(0..$ncols){
				if($cols[$i] eq ''){
					
					### Si es columna compuesta
					if($db_fields[$i] =~	/\s|-/){
						my @tmpcols = split(/\s|-/,$db_fields[$i]);
						###
						for my $j(0..$#tmpcols){
							$cols[$i] .= $rec->{$tmpcols[$j]} ."-"	if $db_fields[$i] =~	/-/;
							$cols[$i] .= $rec->{$tmpcols[$j]} ." "	if $db_fields[$i] =~	/\s/;
						}
						chop($cols[$i]);
					### Si es columna simple	
					}else{
						if($db_fields[$i] eq 'NameItems' or $db_fields[$i] eq 'ModelItems'){
						
							my $sth = &Do_SQL("SELECT GROUP_CONCAT(Model SEPARATOR '|')AS ModelItems,GROUP_CONCAT(Name SEPARATOR '|') AS NameItems FROM sl_products WHERE ID_products IN($rec->{'ID_products'});");
							($rec->{'ModelItems'},$rec->{'NameItems'}) = $sth->fetchrow();
						}

						$cols[$i] = $rec->{$db_fields[$i]};
					}
				}
			}
			print join(',', @cols)."\r\n";
		}#end while			
	}#end for ids	
}

sub check_posteddate {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/18/2008
# Last Modified on: 
# Last Modified by: 
# Description : Search and set posteddate by orders_products
# Forms Involved: 
# Parameters : id_orders_products
	
	my ($id_orders_products) = @_;
	my ($sthop) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products=$id_orders_products");
	while ($col = $sthop->fetchrow_hashref){
		$orders_op = $col->{'ID_orders'};
		$posted_op = $col->{'PostedDate'};
		$date_op = $col->{'Date'};
	}
	if($posted_op eq "0000-00-00" || $posted_op eq "NULL" || !$posted_op){
		my ($stho) = &Do_SQL("SELECT PostedDate, ID_orders FROM sl_orders WHERE ID_orders=$orders_op AND Date='$date_op' UNION SELECT PostedDate, ID_orders_products FROM sl_orders_products WHERE ID_orders=$orders_op AND Date='$date_op' UNION SELECT PostedDate, ID_orders_payments FROM sl_orders_payments WHERE ID_orders=$orders_op AND Date='$date_op' ORDER BY PostedDate");
		while ($col = $stho->fetchrow_hashref){
			$posted = $col->{'PostedDate'};
		}
	} else {
		$posted = $posted_op;
	}
	return $posted;
}





sub add_mm_numbers{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 22 Jan 2010 17:43:40
# Author: MCC C. Gabriel Varela S.
# Description :   Sincroniza con S7
# Parameters :
	($x,$query) = &validate_cols('1');
	$err += $x;
	if ($err==0)
	{
		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		my $sth = &Do_SQL("INSERT INTO $in{'db'} SET $query,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';",1);
	}
}

sub updated_mm_numbers{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 22 Jan 2010 18:04:58
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	($x,$query) = &validate_cols('1');
	$err += $x;
	if ($err==0)
	{
		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		my ($sth) = &Do_SQL("UPDATE $in{'db'} SET $query WHERE $db_cols[1]='$in{lc($db_cols[1])}';",1);
	}
}

sub del_mm_numbers{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 22 Jan 2010 18:11:53
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	my ($sth) = &Do_SQL("DELETE FROM $in{'db'} WHERE $db_cols[0]='$in{'delete'}';",1);

}






sub get_coupon_external{
#-----------------------------------------
# Created on: 05/12/2010  12:05:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Check wethear  a coupon exists or must be created
# Parameters :


	my ($table,$id_table) = @_;
	my $result=-1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_external WHERE linktable = '$table' AND ID_table = '$id_table' AND Status= 'Active';");
    
	if($sth->fetchrow() > 0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_coupons_external WHERE linktable = '$table' AND ID_table = '$id_table' AND Status= 'Active';");
		my($rec) = $sth->fetchrow_hashref();

		$va{'ordernet'} = &format_price($in{'ordernet'});
		$va{'coupon_value'} = $rec->{'coupon_value'};
		$va{'coupon_expiration'} =  $rec->{'expiration'};
		$va{'coupon_percentage'} = int($rec->{'percentage'});
		$va{'coupon_externalname'} = $rec->{'name_external'};
		$va{'coupon_externalurl'} = $rec->{'url_external'};
		$va{'coupon_maxdiscount'} = &format_price($rec->{'maxdiscount'});
		$va{'coupon_minexternal'} = &format_price($rec->{'minimum_external'});
		$result = 100;
	}else{
		#&cgierr("SELECT * FROM sl_coupons_external WHERE linktable = '$table' AND ID_table = '$id_table' AND Status= 'Active';");
		if($va{'coupon_value'}){
			delete($va{'coupon_value'});
		}
		$result = &set_coupon_external($table,$id_table);
	}
	return $result;
}


sub set_coupon_external{
#-----------------------------------------
# Created on: 05/12/2010  12:05:02 By  Roberto Barcenas
# Forms Involved: 
# Description : Creates new coupon
# Parameters :


	my ($table,$id_table) = @_;
	my $count=0;
          my $str='';
	my $ini=0;

	while (!$va{'coupon_value'} and $count<300){
		$va{'coupon_value'} = &promocode_generate($ini);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons_external WHERE coupon_value = '$va{'coupon_value'}';");
		my ($exist) = $sth->fetchrow();
	
		if ($exist or $va{'coupon_value'} <= 0){
			$ini= $va{'coupon_value'};
			$str .= "$va{'coupon_value'} - ";
			delete($va{'coupon_value'});
		}
		++$count;
	}

	if($va{'coupon_value'}){
		
		if($cfg{'coupons_externalname'} ne '' and $cfg{'coupons_externalname'} ne '0'){
			$query .= " name_external= '$cfg{'coupons_externalname'}' , ";
		}

		if($cfg{'coupons_expiration'} eq '' or $cfg{'coupons_expiration'} eq '0'){
			$cfg{'coupons_expiration'} = 365;
		}
		$query .= " expiration= DATE_ADD(CURDATE(), INTERVAL $cfg{'coupons_expiration'} day),";

		if($cfg{'coupons_idpromo'} ne '' and $cfg{'coupons_idpromo'} ne '0'){
			$query .= " ID_promo = $cfg{'coupons_idpromo'} ,";
		}

		if($cfg{'coupons_percentage'} ne '' and $cfg{'coupons_percentage'} ne '0'){
			$query .= " percentage = $cfg{'coupons_percentage'} ,";
		}

		if($cfg{'coupons_maxdiscount'} ne '' and $cfg{'coupons_maxdiscount'} ne '0'){
			$query .= " maxdiscount = $cfg{'coupons_maxdiscount'} , ";
		}

		if($cfg{'coupons_minexternal'} ne '' and $cfg{'coupons_minexternal'} ne '0'){
			$query .= " minimum_external = $cfg{'coupons_minexternal'} , ";
		}

		if($cfg{'coupons_externalurl'} ne '' and $cfg{'coupons_externalurl'} ne '0'){
			$query .= " url_external = '$cfg{'coupons_externalurl'}' , ";
		}


		$va{'coupon_expiration'} =  $cfg{'coupons_expiration'};
		$va{'coupon_percentage'} = int($cfg{'coupons_percentage'});
		$va{'coupon_externalname'} = $cfg{'coupons_externalname'};
		$va{'coupon_externalurl'} = $cfg{'coupons_externalurl'};
		$va{'coupon_maxdiscount'} = &format_price($cfg{'coupons_maxdiscount'});
		$va{'coupon_minexternal'} = &format_price($cfg{'coupons_minexternal'});

		my $sth=&Do_SQL("INSERT INTO sl_coupons_external SET coupon_value = '$va{'coupon_value'}', linktable='$table', ID_table= '$id_table', $query Status='Active',Date=CURDATE(), Time=CURTIME(),ID_admin_users=$usr{'id_admin_users'};");
		return 100;
	}

	return -1;
}



sub set_group_wlocation{
#-----------------------------------------
# Created on: 06/28/10  11:03:32 By  Roberto Barcenas
# Forms Involved: 
# Description : Agrupa el inventario en un solo registro de wlocation y skus_cost para un mismo id_products/id_warehouses
# Parameters :
# Last Time Modification by RB on 12/22/2010. Se corrige problema de costos incorrectos, las lineas se agrupan por costo 

		return;
		my $query ='';
		$query = "  ID_warehouses='$in{'id_warehouses'}' AND " if ($in{'id_warehouses'});
	
		my ($sth) = &Do_SQL("SELECT ID_products, ID_warehouses, COUNT(*), SUM(Quantity) FROM sl_warehouses_location WHERE $query Quantity > 0 GROUP BY ID_products,ID_warehouses ORDER BY ID_warehouses, ID_products;");
		
		if($sth->rows() > 0){
				
				while(my($id_products,$id_warehouses,$rows,$quantity) = $sth->fetchrow()){
							
						if($rows > 1){
							## Cual es el registro mas viejo en wlocation?
							my ($sth) = &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products ORDER BY Date;");
							my($wlocation_base) = $sth->fetchrow();
							
							my ($sth2) = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = $quantity, Location='A100A' WHERE ID_warehouses_location = $wlocation_base;");
							my ($sth3) = &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND ID_warehouses_location != $wlocation_base;");
						}else{
							my ($sth2) = &Do_SQL("UPDATE sl_warehouses_location SET Location='A100A' WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products;");
						}
						
						## Separara por costos
						my ($sthsc) = &Do_SQL("SELECT Cost,SUM(Quantity) FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products GROUP BY ID_warehouses,ID_products,Cost;"); 

						if($sthsc->rows() > 0){

								while(my($costc,$qtyc) = $sthsc->fetchrow()){
								
										## Cual es el registro mas viejo en skus_cost?
										my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc' ORDER BY Date;");
										my($scost_base) = $sth->fetchrow();
										
										if($quantity > 0){
										
												($qtyc > $quantity) and ($qtyc = $quantity);
												
												if($scost_base and $scost_base >0){
														my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = $qtyc WHERE ID_skus_cost = $scost_base;");
														my ($sth3) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc' AND ID_skus_cost != $scost_base;");
														
												}else{
														my ($cost, $cost_adj) = &load_sltvcost($id_products);
														$cost = 0 if !$cost;
														$cost_adj = 0 if !$cost_adj;
														my ($sth2) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_products',ID_purchaseorders='0',ID_warehouses='$id_warehouses',Tblname='sl_manifests',Quantity='$quantity',Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='2';");
												}
												
												$quantity -= $qtyc;
										
										}else{
												my ($sth3) = &Do_SQL("DELETE FROM sl_skus_cost WHERE ID_warehouses = $id_warehouses AND ID_products = $id_products AND Cost='$costc'; ");
										}
								}
						}
						
						if($quantity > 0){
							my ($cost, $cost_adj) = &load_sltvcost($id_products);
							$cost = 0 if !$cost;
							$cost_adj = 0 if !$cost_adj;
							my ($sth2) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_products = '$id_products',ID_purchaseorders='0',ID_warehouses='$id_warehouses',Tblname='sl_manifests',Quantity='$quantity',Cost='$cost',Cost_Adj='$cost_adj',Date=CURDATE(),Time=CURTIME(),ID_admin_users='2';");
						}
						$it++;
				}
		}
}


sub loadPaymentData {
# --------------------------------------------------------
# Last Modified on: 07/24/08 11:14:33
# Last Modified by: MCC C. Gabriel Varela S: Se verifica que la tarjeta no expire antes del Ãºltimo pago
# Last Modified on: 08/04/08 10:12:10
# Last Modified by: MCC C. Gabriel Varela S
# Last Modified on: 08/06/08 15:20:55
# Last Modified by: MCC C. Gabriel Varela S: Verificar que las cantidades en los pagos sea correcta cuando se mezclan pagos mensuales con 0-15-30
# Last Modified on: 10/28/08 14:51:50
# Last Modified by: MCC C. Gabriel Varela S: Se quita mensaje de son cada tal dÃ­as si es un sÃ³lo pago
# Last Modified on: 10/30/08 10:30:50
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales
# Last Modified on: 11/11/08 17:17:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si el tipo de pago es lay away el primer pago sea el Ãºltimo y como dice el dicho, los Ãºltimos serÃ¡n los primeros
# Last Modified RB: 12/02/08  18:56:30 Se agrego el template para layaway M.O.
# Last Modified on: 12/18/08 13:49:41
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando sea membership, y lay away, el primer pago incluya el precio de la membresÃ­a
# Last Modified RB: 03/12/09  11:32:31 -- Agregue &save_callsession(); al final de la funcion
# Last Modified on: 06/03/10 18:29:56
# Last Modified by: MCC C. Gabriel Varela S: Es paysummary de console.func.cgi y con modificaciones no usar con otro propÃ³sito que para emails
# Last Modified RB: 09/11/2010  11:32:31 -- Esta funcion se ha trasladado desde sub.func.html.cgi de administration hacia aca porque se utiliza en el run_daily
#Last modified on 4 Feb 2011 16:36:50
#Last modified by: MCC C. Gabriel Varela S. : Se pone por parámetro de configuración los días mínimos previos al vencimiento de la tarjeta y se cambia mensaje
	
	my ($id_orders)=@_;


	delete($va{'amount'});
	#pagos
	my $sth=&Do_SQL("Select count(*),sum(Amount),pmtfield1,pmtfield1,pmtfield3,pmtfield4,pmtfield5,pmtfield6,pmtfield7 from sl_orders_payments where ID_orders=$id_orders and Status not in('Order Cancelled','Cancelled','Void') group by ID_orders");
	($payments_number,$cses{'total_order'},$cses{'pmtfield1'},$cses{'pmtfield2'},$cses{'pmtfield3'},$cses{'pmtfield4'},$cses{'pmtfield5'},$cses{'pmtfield6'},$cses{'pmtfield7'})=$sth->fetchrow_array;
	for(1..7)
	{
		$in{"pmtfield$_"}=$cses{"pmtfield$_"};
	}
	 $in{"pmtfield3"}="xxxx-xxxx-xxxx-".substr($in{'pmtfield3'},-4);
	#total_order
#	my $sth=&Do_SQL("Select count(*) from sl_orders_payments where ID_orders=$id_orders and Status not in('Order Cancelled','Cancelled','Void')");
#	$payments_number=$sth->fetchrow;

	my $sth=&Do_SQL("Select * from sl_orders where ID_orders=$id_orders");
	$rec=$sth->fetchrow_hashref;
	$cses{'pmtfield7'}='COD';
	$cses{'pay_type'}='cod';
	$cses{'pmtfield7'}='CreditCard' if($rec->{'Ptype'}eq'Credit-Card');
	$cses{'pay_type'}='cc' if($rec->{'Ptype'}eq'Credit-Card');
	$in{'pay_type'}=$cses{'pay_type'};
	
	
	my $sth=&Do_SQL("Select * 
	from sl_orders_products
	where ID_orders_products=$id_orders
	and Status in('Active')");
	$i=1;
	while($rec=$sth->fetchrow_hashref)
	{
		$cses{'items_in_basket'}++;
		$cses{'items_'.$i.'_price'}=$rec->{'SalePrice'};
		$cses{'items_'.$i.'_id'}=$rec->{'ID_products'};
		$cses{'items_'.$i.'_payments'}=$payments_number;
		$i++;
	}
	$cses{'dayspay'}=1;
	
	
	#return "Argumentos: ".$cses{'dayspay'};

	if ($in{'pay_type'} eq 'cc' or $in{'pay_type'} eq 'lay'){
		my (@payments,$maxpaym,$fpdate,$tofp,$stfp,$price,$promo_cont,$onepay);
		my ($fpdias)= $cses{'dayspay'};
		$maxpaym = 1;
		
		$downpaymentinorder=0;
		$cses{'dpio'} = 0;
		if($cses{'dayspay'} eq 15){
			$downpaymentinorder=1;
			$cses{'dpio'} = 1;
		}else{
			for my $i(1..$cses{'items_in_basket'}){
				if ($cses{'items_'.$i.'_downpayment'}>0 && $cses{'items_'.$i.'_payments'} >= $cses{'items_'.$i.'_fpago'} && $cses{'items_'.$i.'_payments'} >1) {
					$downpaymentinorder=1;
					$cses{'dpio'} = 1;
				}
			}			
		}
		########################################
		########### Items
		########################################
		PLINE: for my $i(1..$cses{'items_in_basket'}){
			(!$cses{'items_'.$i.'_qty'}) and (next PLINE);

			##########################################
			#########  CALCULAR PAGO CONTADO
			##########################################
#			if($cses{'pay_type'} ne 'lay'){
				if($cfg{'membership'} and $cses{'type'}eq"Membership")
				{
					$onepay = $cses{'items_'.$i.'_msprice'};
				}
				elsif ($cses{'items_'.$i.'_fpprice'}>0){
					$onepay = $cses{'items_'.$i.'_price'};
				}elsif($cses{'items_'.$i.'_id'} =~ /$cfg{'disc40'}/){
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*(40/100));
				}elsif ($cses{'items_'.$i.'_id'} =~ /$cfg{'disc30'}/){
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*(30/100));
				}else{
					$onepay = $cses{'items_'.$i.'_price'} - ($cses{'items_'.$i.'_price'}*$cfg{'fpdiscount'.$cses{'items_'.$i.'_fpago'}}/100);
				}
#			}
			
			if ($cses{'items_'.$i.'_id'} and $cses{'items_'.$i.'_payments'}==1){
				$payments[$_] += round($onepay,2);
			}elsif ($cses{'items_'.$i.'_payments'} eq '3c'){
				## Skip
				$promo_cont += $onepay/3;
			}elsif ($cses{'items_'.$i.'_id'} and $cses{'items_'.$i.'_payments'}>1){
				if ($cses{'items_'.$i.'_downpayment'}>0) {
					$tofp = $cses{'items_'.$i.'_payments'}+1;
					$stfp = 2;
				}
#				elsif($cses{'items_'.$i.'_downpayment1'}>0 and $cses{'dayspay'}!=30)
#					{
#						$tofp = $cses{'items_'.$i.'_payments'}+1;
#						$stfp = 2;
#				}
				else{
					$tofp = $cses{'items_'.$i.'_payments'};
					$stfp = 1;
				}
				if($cfg{'membership'} and $cses{'type'}eq"Membership")
				{
					$price = $cses{'items_'.$i.'_price'};
				}
				elsif ($cses{'items_'.$i.'_fpprice'}>0){
					$price = $cses{'items_'.$i.'_fpprice'};
				}else{
					$price = $cses{'items_'.$i.'_price'};
				}
				($maxpaym = $tofp) unless ($maxpaym > $tofp);
				for ($stfp..$tofp){
					if ($cses{'items_'.$i.'_payments'} eq '3c'){
						$payments[$_] += round($price/3,2);
					}elsif($cses{'items_'.$i.'_payments'} and $cses{'items_'.$i.'_downpayment'}>0) {
						$payments[$_] += round(($price-$cses{'items_'.$i.'_downpayment'})/($cses{'items_'.$i.'_payments'}),2);
					}
#					elsif($cses{'items_'.$i.'_payments'} and $cses{'items_'.$i.'_downpayment1'}>0 and ($cses{'dayspay'}!=30)){
#						$payments[$_] += round(($price-$cses{'items_'.$i.'_downpayment1'})/($cses{'items_'.$i.'_payments'}),2);
#					}
					elsif ($cses{'items_'.$i.'_payments'}){
						$payments[$_] += round($price/$cses{'items_'.$i.'_payments'},2);
					}
				}
			}
		}
		
		########################################
		########### Service
		########################################
		for my $i(1..$cses{'servis_in_basket'}){
			@itemsessionid=&getsessionfieldid('items_','_id',$cses{'servis_'.$i.'_relid'},''); #JRG 29-05-2008
			
			if ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}==1){
#				if($downpaymentinorder>0) {
#					$payments[2] += round($cses{'servis_'.$i.'_price'},2);
#					$payments[1] += 0;
#				} else {
					$payments[$_] += round($cses{'items_'.$i.'_price'},2);
#				}
			}elsif ($cses{'servis_'.$i.'_id'} and $cses{'servis_'.$i.'_payments'}>1){
#				if($cses{'servis_'.$i.'_downpayment1'}>0 && $cses{'servis_'.$i.'_payments'} > $cses{'servis_'.$i.'_fpago'}){
#					$tofp = $cses{'servis_'.$i.'_payments'}+1;
#					$stfp = 2;	
#					$cses{'total_order'} += $cses{'servis_'.$i.'_downpayment1'};				
#				}
#				 elsif ($cses{'servis_'.$i.'_downpayment1'}>0) {
#					$tofp = $cses{'servis_'.$i.'_payments'}+1;
#					$stfp = 2;
#				}
#				else{
					$tofp = $cses{'servis_'.$i.'_payments'};
					$stfp = 1;
#				}

				($maxpaym = $tofp) unless ($maxpaym > $tofp);
				for ($stfp..$tofp){
					if ($cses{'servis_'.$i.'_payments'} and $cses{'servis_'.$i.'_downpayment'}>0) {
						$payments[$_] += round(($cses{'servis_'.$i.'_price'}-$cses{'servis_'.$i.'_downpayment'})/($cses{'servis_'.$i.'_payments'}),2);
					}elsif ($cses{'servis_'.$i.'_payments'}){
						$payments[$_] += round($cses{'servis_'.$i.'_price'}/$cses{'servis_'.$i.'_payments'},2);
					}
				}
			}
		}
		if ($promo_cont>0 and $maxpaym>=2){
			$payments[2] += $promo_cont;
			$fpdias = 30;
			$payments[1] = $cses{'total_order'}- round($promo_cont,2);
		}elsif ($promo_cont>0 and $maxpaym<2){
			$payments[2] = $promo_cont;
			$maxpaym = 2;
			$fpdias = 30;
			$payments[1] = $cses{'total_order'} - round($promo_cont,2);
		}else{
			$payments[1] = $cses{'total_order'} - round($promo_cont,2)*2;
			#$payments[2] = $promo_cont;
		}
		
		
		for (2..$maxpaym){
			$payments[1] -= round($payments[$_],2);
		}
	
		#Si el tipo de pago es layaway se cambian los pagos primero por el Ãºltimo.
		if($cses{'pay_type'}eq"lay")
		{
			my $temp;
			$temp=$payments[1];
			$payments[1]=$payments[$maxpaym];
			$payments[$maxpaym]=$temp;
			if($cfg{'membership'} and $cses{'type'}eq"Membership")
			{
				$pricetoapply=&load_name ('sl_services','ID_services',$cfg{'membershipservid'},'SPrice');
				$payments[1]+=$pricetoapply;
				$payments[$maxpaym]-=$pricetoapply;
			}
		}
		
		#&cgierr($payments[2]);
	
		my ($today) = &get_sql_date();
		$today = &sqldate_plus($today,$cses{'days'})	if	($cses{'days'} > 0 and $cses{'postdated'} eq '1');
		($cses{'pay_type'} eq 'lay' and $cses{'startdate'}) and ($today = $cses{'startdate'});
		for my $i(1..$maxpaym){
			$fpdate = &sqldate_plus($today,$fpdias*($i-1));
			if ($promo_cont>0 and $i >1){
				if ($i == 2){
					$cses{'fppayment2'} = round($promo_cont,2);
					$cses{'fpdate2'} = &sqldate_plus($today,15);
					$va{'amount'} .= &format_price($promo_cont) . " &nbsp; \@ &nbsp; $cses{'fpdate2'}<br>";
					#$payments[2] += round($promo_cont,2);
				}
				$cses{'fppayment'.($i+1)} =  round($payments[$i],2);
				$cses{'fpdate'.($i+1)} = $fpdate;
				$va{'amount'} .= &format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}else{
				$cses{'fppayment'.$i} =  round($payments[$i],2);
				$cses{'fpdate'.$i} = $fpdate;
				$va{'amount'} .= &format_price($payments[$i]) . " &nbsp; \@ &nbsp; $fpdate<br>";
			}
		}
		#CompararÃ¡ la fecha de Ãºltimo pago con la de expiraciÃ³n de la tarjeta
		if($cses{'pmtfield7'}eq"CreditCard" or $cses{'pmtfield7'}eq"DebitCard")	{
			$fpdate=~/^(\d{2})(\d{2})-(\d{2})-(\d{2})$/;
			my $lpday=$4;
			$cses{'pmtfield4'}=~/^(\d{2})(\d{2})$/;
			my $edyear=$2;
			my $edmonth=$1;
			my $edday=28;
			if($edmonth==1 or $edmonth==3 or $edmonth==5 or $edmonth==7 or $edmonth==8 or $edmonth==10 or $edmonth==12)		{
				$edday=31;
			}elsif($edmonth==4 or $edmonth==6 or $edmonth==9 or $edmonth==11){
				$edday=30;
			}
			my ($diffs)=&Do_SQL("SELECT datediff('20$edyear-$edmonth-$edday','$fpdate')");
			my $diff=$diffs->fetchrow;
			if($diff<$cfg{'prevent_days'}){
				$va{'amount'}.="<table border='0' cellspacing='0' cellpadding='2' width='100%'>
							<tr>
		  					<td class='stdtxterr' colspan='2'>Error: No se debe de Confirmar la Orden debido a que el Ãºltimo pago es igual o supera a la fecha de expiraciÃ³n de la tarjeta($edmonth/20$edyear).</td>
							</tr>
						 </table>
						 <script language='javascript'>
						 var str=''+self.location;
							str=str.replace(/#tabs/, '');
							str+='?cmd=console_order&step=8&restartpayments=1#tabs';
							alert('Vencimiento Invalido, la fecha de vencimiento de la tarjeta debe ser al menos $cfg{'prevent_days'} dias despues del la ultima cuota($edmonth/20$edyear).');
						 window.location=str;
						 </script>
						 "
			}
		}
		
		$cses{'fppayments'} = $maxpaym;
		($promo_cont) and (++$cses{'fppayments'});
		$va{'fpdias'} = "";#$fpdias;
		$va{'fpdias'} ="SON CADA $fpdias DIAS." if($fpdias!=1);
		&save_callsession();
		
		if($cses{'pay_type'} eq 'cc' or $cses{'laytype'} eq 'cc'){
			$va{'last4dig'} = substr($cses{'pmtfield3'},-4);
			if ($cses{'pmtfield7'} eq 'DebitCard'){
				$va{'cardtype'} = 'debito';
				$va{'cardtype_en'} = 'debit';
			}else{
				$va{'cardtype'} = 'credito';
				$va{'cardtype_en'} = 'credit';
			}
			
			return &build_page("func/console_order8amail.html");
		}else{
			return &build_page("func/console_order8m.html");
		}
	}elsif ($in{'pay_type'} eq 'cod'){
		for (1..$cses{'fppayments'}){
			delete($cses{'fppayment'.$_});
			delete($cses{'fpdate'.$_});
		}
		delete($cses{'fppayments'});
		
		return &build_page("func/console_order8cod.html");
	}
}

sub build_common_header{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 28 Oct 2010 18:24:48
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my $header;
	$header=qq|<table border="0" cellspacing="0" cellpadding="0" width="100%" class=tabs height="48">
			<tr>
				<td align=right>
					<table cellspacing="0" cellpadding="0">
						<tr>
							<td valign=top>
								<img src=/sitimages/aco/t.jpg>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/admin?cmd=$in{'cmd'}_home")' valign="center"  style="cursor:pointer;">
								<img src=/sitimages/aco/home3.png hspace=15 alt='Home'>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/admin?cmd=$in{'cmd'}_home")' valign="center" width=60  style="cursor:pointer;">
								Home&nbsp;&nbsp;&nbsp;
							</td>
							<td valign=top>
								<img src=/sitimages/aco/t.jpg>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&add=1")' valign="center"  style="cursor:pointer;">
								<img src=/sitimages/aco/add.png hspace=15 alt='Add'>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&add=1")' valign="center" width=60  style="cursor:pointer;">
								Add&nbsp;&nbsp;&nbsp;
							</td>
							<td valign=top>
								<img src=/sitimages/aco/t.jpg>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=form")' valign="center"  style="cursor:pointer;">
								<img src=/sitimages/aco/search.png hspace=15 alt='Search'>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=form")' valign="center" width=60  style="cursor:pointer;">
								Search&nbsp;&nbsp;&nbsp;
							</td>
							<td valign=top>
								<img src=/sitimages/aco/t.jpg>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=advform")' valign="center" bgcolor="#ffffff"  style="cursor:pointer;">
								<img src=/sitimages/aco/searchadv.png hspace=15 alt='Adv Search'>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=advform")' valign="center" bgcolor="#ffffff" width=90  style="cursor:pointer;">
								Adv Search&nbsp;&nbsp;&nbsp;
							</td>
							<td valign=top>
								<img src=/sitimages/aco/t.jpg>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=listall&amp;sb=id_orders&amp;so=DESC")' valign="center"  style="cursor:pointer;">
								<img src=/sitimages/aco/edit.png hspace=15 alt='View/Edit/Delete'>
							</td>
							<td onclick='trjump("/cgi-bin/mod/admin/dbman?cmd=$in{'cmd'}&search=listall&amp;sb=id_orders&amp;so=DESC")' valign="center" width=140  style="cursor:pointer;">
								View / Edit / Delete&nbsp;&nbsp;&nbsp;
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>|;
	return $header;

}




sub build_exp_date_opts{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11 Jan 2011 11:04:19
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my @timest=localtime(time);
	my $year=$timest[5]+1900;
	my $output='';
	for(0..14)
	{
		$yearv = sprintf("%02d", $year % 100);
		$output.="<option value=$yearv>$year</option>\n";
		$year++;
	}
	return $output;
}


sub format_phone{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 128 Jan 2011 10:38:19
# Author: Roberto Barcenas.
# Description :  Format a phone number string 
# Parameters :
# 13-04-2015::ISC Alejandro Diaz::Se agrega parametro para enceder/apagar el clicktocall

	my ($phone_number, $id_cust) = @_;
	$phone_number =~ s/\D//g;
	my ($click_to_call);
	if (length($phone_number) > 10 and substr($phone_number,0,1) == 1){
			$phone_number = substr($phone_number,-10);
	}elsif(length($phone_number) > 10){
			$phone_number = substr($phone_number,0,10)
	}
	if ($usr{'extension'} and $cfg{'clicktocall_enabled'} and $cfg{'clicktocall_enabled'} == 1){
		$click_to_call = " &nbsp;&nbsp; <a href='#clicktocall' id='clicktocall' onClick=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'clicktocall');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=click_to_call&num=$phone_number&id=$id_cust');\">";

		if($in{'toprint'}) {
			$click_to_call .= "</a>";
		}else {
			$click_to_call .= "<img src='/sitimages/tree/m_ext.png'></a>";
		}
		
	}
	if(length($phone_number) == 10){
		return '('.substr($phone_number,0,3).') '.substr($phone_number,3,3) . ' - ' . substr($phone_number,-4). $click_to_call;
	}else{
		return $phone_number;
	}
}

sub send_cmd_to_ast {
# --------------------------------------------------------
#Last modified on 11 Aug 2011 10:28:46
#Last modified by: MCC C. Gabriel Varela S. :it Notifies when it falls
	my ($end,$username,$password,$server,%command) = @_;
	my (@output);
	$uname	=	 `uname -n`;
	if($uname =~ /n4/){
		return;
	}
	use Asterisk::Manager;
	# Connect to Asterisk
	$asterisk = new Asterisk::Manager;
	$asterisk->user($username);
	$asterisk->secret($password);
	$asterisk->host($server);
	$asterisk->connect || ((&notify_asterisk_fail("Could not connect to Asterisk on $server: ". $asterisk->error. "\n"))and(die "Could not connect to Asterisk on $server: ", $asterisk->error, "\n"));
	@output = $asterisk->sendcommand(%command);

	if ($end){
		while( 1 ){
			++$c;
			last  if ($c>500);
			my @ary = $asterisk->read_response;
		  	last  if $ary[0] =~ /$end/;
		  	push (@output, '=========');
		  	push (@output, @ary);
		}
	}
	
	
	return @output;
}

sub set_reward_points{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/28/11 11:50 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 25 May 2011 12:31:20
#Last modified by: MCC C. Gabriel Varela S. :Se incluye expiration
#Last modified on 25 May 2011 18:13:36
#Last modified by: MCC C. Gabriel Varela S. :Se agrega automáticamente el producto
	my ($id_orders)=@_;
	my $id_customers,$points;
	return 0 if(!$cfg{'points_use'});
	return "Missing order id" if(!$id_orders);
	my $order_total=&check_ord_totals($id_orders);
	if($order_total eq 'OK')
	{
		$id_customers=&load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
		#Verifica si no tiene ya puntos para esa orden y cliente.
		$points=&get_reward_points($id_orders,$id_customers);
		return $points if($points!=0);
		if($cfg{'points_mode'}==1)
		{
			#Obtiene el total de la orden y calcula los puntos.
			$order_total=&load_name('sl_orders','ID_orders',$id_orders,'OrderNet');
			$points=$order_total/100*$cfg{'points_percentage'};
			
			#Aquí se determina el producto a dar
			my ($sth_product)=&Do_SQL("SELECT ID_products
			FROM sl_reward_points_gifts
			WHERE Points_needed<=$points
			AND Status='Active'
			ORDER BY Points_needed desc
			LIMIT 1");
			my $id_products=$sth_product->fetchrow;
			
			#Hace el insert
			my ($sth)=&Do_SQL("INSERT INTO sl_customers_points SET 
			ID_customers='$id_customers',
			ID_orders='$id_orders', 
			Points='$points', 
			ID_products='$id_products',
			Status='Active', 
			expiration= DATE_ADD(CURDATE(), INTERVAL $cfg{'points_expiration_days'} day),
			Date=curdate(),
			Time=curtime(),
			ID_admin_users='$usr{'id_admin_users'}';");
			return $points;
		}
		elsif($cfg{'points_mode'}==2)
		{
			$points=$cfg{'points_fixed'};
			
			#Aquí se determina el producto a dar
			my ($sth_product)=&Do_SQL("SELECT ID_products
			FROM sl_reward_points_gifts
			WHERE Points_needed<=$points
			AND Status='Active'
			ORDER BY Points_needed desc
			LIMIT 1");
			my $id_products=$sth_product->fetchrow;
			
			#hace el insert
			my ($sth)=&Do_SQL("INSERT INTO sl_customers_points SET 
			ID_customers='$id_customers',
			ID_orders='$id_orders', 
			Points='$points', 
			ID_products='$id_products',
			Status='Active', 
			expiration= DATE_ADD(CURDATE(), INTERVAL $cfg{'points_expiration_days'} day),
			Date=curdate(),
			Time=curtime(),
			ID_admin_users='$usr{'id_admin_users'}';");
			return $points;
		}
	}
	else
	{
		return $order_total;
	}
	return 0;
}

sub get_reward_points{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/28/11 12:54 PM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 25 May 2011 12:35:48
#Last modified by: MCC C. Gabriel Varela S. :Se incluye expiration
	my ($id_orders,$id_customers)=@_;
	my ($sth)=&Do_SQL("Select * 
	from sl_customers_points 
	where ID_orders='$id_orders' 
	and ID_customers='$id_customers' 
	and Status='Active'
	and expiration>=curdate()");
	my $rec=$sth->fetchrow_hashref;
	return $rec->{'Points'};
}

sub build_coupons_products_info{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/30/11 11:52 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 04/12/11 02:45:24 PM
# Last Modified by: MCC C. Gabriel Varela S: Se cambia para mostrar model
	my @products;
	@products=split(/,/,$cfg{'coupons_products'});
	my $product_name,$product_desc;
	for (0..$#products){
		$product_name=&load_name('sl_products','ID_products',$products[$_],'Name');
		$product_desc=&load_name('sl_products','ID_products',$products[$_],'Model');
		$output .= "<input type=radio name=id_products value=$products[$_] class=radio> $product_desc ($products[$_])<br>\n";
	}
	return $output;
}

sub put_cses{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/31/11 9:47 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my $cses_string='&here=1';
	foreach $key (keys %cses) 
	{
		$cses_string.="&$key=$cses{$key}";
	}
}

sub get_points_info{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 4/6/11 10:27 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 29 Apr 2011 13:13:27
#Last modified by: MCC C. Gabriel Varela S. : Se evalúan los premios que podría ganar en su próxima compra tomando en cuenta los puntos actuales más los a acumular para mostrar texto asignado por Carlos
#Last modified on 6 May 2011 10:53:06
#Last modified by: MCC C. Gabriel Varela S. :Se pone id de cliente en caso de que no existan puntos acumulados
#Last modified on 25 May 2011 13:44:42
#Last modified by: MCC C. Gabriel Varela S. :Se hace que no se mencione nada referente a puntos
#Last modified on 26 May 2011 18:04:05
#Last modified by: MCC C. Gabriel Varela S. :the part of possible_gifts is now commented
#Last modified on 1 Jul 2011 12:40:14
#Last modified by: MCC C. Gabriel Varela S. :the text "Válido sólo para compras hechas por internet a través de www.innovashop.tv" is included
#Last modified by: MCC C. Gabriel Varela S. :the text "Vï¿½lido sï¿½lo para compras hechas por internet a travï¿½s de www.innovashop.tv" is included
# Last Time Modified by RB on 09/01/2011: Se eliminan todos los textos de salida y solo se devuelve el id_products de regalo

	my ($id_customers,$id_orders)=@_;
	return '' if($id_customers eq'' or $id_orders eq'' or $cfg{'points_use'}==0);
	my $this_points=get_reward_points($id_orders,$id_customers);
	my $total_points=get_total_reward_points($id_customers);
	$this_points=0 if(!$this_points);
	my $output='';
	my $points;
	if($this_points!=0)
	{
		$va{'this_points'}=$this_points;
	}
	else
	{
		if(&check_ord_totals($id_orders) eq 'OK')
		{
			$id_customers=&load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
			#Verifica si no tiene ya puntos para esa orden y cliente.
			$points=&get_reward_points($id_orders,$id_customers);
			if($points==0)
			{
				if($cfg{'points_mode'}==1)
				{
					#Obtiene el total de la orden y calcula los puntos.
					$order_total=&load_name('sl_orders','ID_orders',$id_orders,'OrderNet');
					$points=$order_total/100*$cfg{'points_percentage'};
				}
				elsif($cfg{'points_mode'}==2)
				{
					$points=$cfg{'points_fixed'};
				}
			}
			$points=int($points);
			$va{'this_points'}=$points;
		}
	}
	
	$total_points=0 if(!$total_points);
	$va{'total_points'}=$total_points;
	$va{'gift'}='default';
	
	if($this_points!=0 or $total_points!=0)
	{
		$output.="<span style='font-size:14px;color:#2f2f2f;'>En su pr&oacute;xima compra utilice su n&uacute;mero de cliente <strong>$id_customers</strong>, para continuar recibiendo grandes premios.</span>";
		#tiene correo electronico?
		my $email=&load_name('sl_customers','ID_customers',$id_customers,'Email');
		if($email eq'' or $email!~/\@/)
		{
			#$output.="<span style='font-size:14px;color:#2f2f2f;'><br>No olvide suscribirse en https://www.innovashop.tv/registration-D para tener registro de todas sus compras.</span>";
		}
		
# 		my $possible_gifts='';
# 		if($this_points!=0)
# 		{
# 			$possible_gifts=&get_possible_gifts_by_points($total_points+$this_points);
# 		}
# 		elsif($points!=0)
# 		{
# 			$possible_gifts=&get_possible_gifts_by_points($total_points+$points);
# 		}
# 		
# 		if($possible_gifts ne'')
# 		{
# 			$output.=$possible_gifts;
# 		}
		
		my $gifts='';
		$gifts=&get_gifts_by_points($total_points);
		if($gifts ne'')
		{
			$va{'gift'}=$gifts;
		}
		#Verifica si es primera compra:
#		if($this_points==$total_points){
# 			$output.="<br>Cada compra le da puntos y mientras m&oacute;s puntos acumule, se puede llevar productos Gratis, descuentos especiales, promociones, etc.";
##			$output.="<span style='font-size:14px;color:#2f2f2f;'><br>Cada compra cuenta, entre m&aacute;s &oacute;rdenes m&aacute;s oportunidad tiene de llevarse productos Gratis, descuentos especiales, promociones, etc.</span>";
#		}
# 		$output.="<br>Recuerde que para saber el status de sus puntos en cualquier momento, puede consultarlo iniciando sesi&oacute;n con su correo electr&oacute;nico y contrase&oacute;a en https://www.innovashop.tv en la secci&oacute;n 'Mi cuenta'";
##		$output.="<span style='font-size:14px;color:#2f2f2f;'><br>Recuerde que para saber el estado de sus &oacute;rdenes en cualquier momento, puede consultarlo iniciando sesi&oacute;n con su correo electr&oacute;nico y contrase&ntilde;a en https://www.innovashop.tv en la secci&oacute;n 'Mi cuenta'</span>";
	}
	
##	$output.="<br>*V&aacute;lido s&oacute;lo para compras hechas por internet a trav&eacute;s de www.innovashop.tv. Algunas restricciones pueden aplicar. Para m&aacute;s informaci&oacute;n p&oacute;ngase en contacto con nosotros.";
	
##	return $output;
}

sub get_possible_gifts_by_points{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 29 Apr 2011 13:22:11
# Author: MCC C. Gabriel Varela S.
# Description :   Muestra un mensaje si los puntos dados son suficientes para poder canjear un regalo
# Parameters :
#Last modified on 25 May 2011 15:25:50
#Last modified by: MCC C. Gabriel Varela S. :Se quita lo referente a puntos
	my ($points)=@_;
	my $gifts;
	$points=0 if($points<=0 or $points eq '');
	my ($sth)=&Do_SQL("Select * from sl_reward_points_gifts where Points_needed<=$points;");
	if($sth->rows>0)
	{
# 		$gifts="<br>Con los puntos totales que acumular&oacute; esta orden ya puede reclamar un regalo en su pr&oacute;xima compra.<br>";
		$gifts="<br>Ya puede reclamar su regalo en su pr&oacute;xima compra.<br>";
	}
	else
	{
		$gifts='';
	}
	return $gifts;
}

sub get_total_reward_points{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 4/6/11 11:43 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 25 May 2011 12:48:32
#Last modified by: MCC C. Gabriel Varela S. :Se incluye expiration
	my ($id_customers)=@_;
	my ($sth)=&Do_SQL("Select sum(Points)as Points 
	from sl_customers_points 
	where ID_customers='$id_customers' 
	and Status='Active'
	and expiration>=curdate()");
	my $rec=$sth->fetchrow_hashref;
	return $rec->{'Points'};
}

sub get_gifts_by_points{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 4/6/11 12:11 PM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 25 May 2011 15:26:50
#Last modified by: MCC C. Gabriel Varela S. :Se cambia mensaje de puntos
#Last modified on 26 May 2011 18:08:41
#Last modified by: MCC C. Gabriel Varela S. :Only one product will be displayed, the nearest and lesser than to the points
#Last modified on 29 Jun 2011 17:08:51
#Last modified by: MCC C. Gabriel Varela S. :The text are formated and the id_products is removed. The model is showed instead of the name

	my ($points)=@_;
	my $gifts;
	$points=0 if($points<=0 or $points eq '');
	#Aquí se determina el producto a dar
	my ($sth)=&Do_SQL("Select ID_products
from sl_reward_points_gifts
where Points_needed<=$points
and Status='Active'
order by Points_needed desc
limit 1");
	if($sth->rows>0)
	{
# 		$gifts="<br>Con los puntos acumulados que tiene hasta ahora, puede llevarse cualquiera de los siguientes premios en su pr&oacute;xima compra:<br>";
##		$gifts="<span style='font-size:14px;color:#2f2f2f;'><br>Felicidades!!. En su pr&oacute;xima orden ll&eacute;vese el siguiente regalo absolutamente gratis:<br>";
		my $id_products=$sth->fetchrow;
# 			$gifts.="<li>$rec->{'ID_products'}&nbsp;".&load_name('sl_products','ID_products',$rec->{'ID_products'},'Name')." ($rec->{'Points_needed'} puntos)</li><br>";
##		$gifts.="<img valign=center src='$va{'imgurl'}/gift-bn-lowres.png'><strong>".&load_name('sl_products','ID_products',$id_products,'Model')." </strong><br>";
##		$gifts.="</span>";
		$gifts=$id_products;
	}
	else
	{
		$gifts='';
	}
	return $gifts;
}


sub is_postdated {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 04/18/11 11:58:23 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($id_orders)=@_;
	my $sth=Do_SQL("Select count(*) as is_postdated
	from sl_orders_products
	where ID_products='600001001'
	and saleprice=$cfg{'postdatedfesprice'}
	and Status='Active'
	");
	$rec=$sth->fetchrow_hashref;
	return $rec->{'is_postdated'};
}

sub sendsms{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 6 May 2011 12:50:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 18 May 2011 12:04:29
#Last modified by: MCC C. Gabriel Varela S. :Se cambia a twilio
#Last modified on 19 May 2011 13:01:51
#Last modified by: MCC C. Gabriel Varela S. :$id_customers and $in{'e'} parameter is included to be sent
	my $Browser = LWP::UserAgent->new;
	(my $id_customers, my $Recipient, my $Message) = @_;

	my $URL = $cfg{'sms_url'};
	my $Response = $Browser->post($URL,
		['recipient' => $Recipient,
		'id_customers' => $id_customers,
		'e' => $in{'e'},
		'print_succes' => 1,
		'Message' => $Message]);

	return $Response->content;

}

sub shipping_notification{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 6 May 2011 17:51:27
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 9 May 2011 13:39:22
#Last modified by: MCC C. Gabriel Varela S. : Se calculan campos va
#Last modified on 18 May 2011 12:52:25
#Last modified by: MCC C. Gabriel Varela S. :Se inserta nota de status
#Last modified on 19 May 2011 12:58:21
#Last modified by: MCC C. Gabriel Varela S. :The id_customers is sent too in sendsms in order to match the cellphone with the id_customers and improve security
#Last modified on 24 May 2011 18:34:31
#Last modified by: MCC C. Gabriel Varela S. :Se ponen variables adicionales $va, que sólo se ponían cuando existía email
#Last modified :11-02-2015 ISC Alejandro Diaz :Se rehace funcion para Inova
	my ($shpdate,$tracking,$provider,$id_orders,$num,%ids)=@_;

	my $status=0;
	my ($pname) = "step3";

	my ($sth) = &Do_SQL("SELECT sl_customers.ID_customers, sl_customers.contact_mode, sl_customers.Cellphone
	FROM sl_orders
	INNER JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers
	WHERE sl_customers.contact_mode='sms'
	AND sl_orders.ID_orders='$id_orders';");
	my ($id_customers,$contact_mode,$cellphone)=$sth->fetchrow_array();

	if ($id_customers){
		
		if ($cellphone ne '' and length($cellphone) == 10){
			# Area Code
			$cellphone =($cfg{'sms_area_code'} and $cfg{'sms_area_code'} ne '')? $cfg{'sms_area_code'}.$cellphone : $cellphone;
			
			#calcula los vas
			$va{'shpdate'}=$shpdate;
			$va{'id_orders'} = $id_orders;
			$va{'shpprovider'} = $provider;
			$va{'tracking'} = $tracking;
			
			$message = &build_page('sms/'.$pname.'.html');
			# Template por ID_sales_origin?

			$status = &sendsms($id_customers,$cellphone,$message);
				
			if ($status == 1){
				&auth_logging('sms_scan_sent',$id_orders);
				#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='".&trans_txt('entershipment_scan_order_csms').":".filter_values($message)."', Type='Low', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
				&add_order_notes_by_type($id_orders,&trans_txt('entershipment_scan_order_csms').":".filter_values($message),"Low");
			}else{
				&auth_logging('sms_scan_failed',$id_orders);
				#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='".&trans_txt('entershipment_scan_order_csms_failed').":".filter_values($status)."', Type='Low', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
				&add_order_notes_by_type($id_orders,&trans_txt('entershipment_scan_order_csms_failed').":".filter_values($status),"Low");
			}	

			if($cfg{'debug_cellphone'} and $cfg{'to_cellphone_debug'} ne ''){
				my $status_debug = &sendsms($id_customers,$cfg{'to_cellphone_debug'},$message);
				#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='SMS Notification status:$status_debug', Type='Low', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
				&add_order_notes_by_type($id_orders,"SMS Notification status:$status_debug","Low");
			}

		}else{
			&auth_logging('sms_scan_failed',$id_orders);
			#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='".&trans_txt('entershipment_scan_order_csms_failed').":$cellphone', Type='Low', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
			&add_order_notes_by_type($id_orders,&trans_txt('entershipment_scan_order_csms_failed').":".$cellphone,"Low");
		}
	}

 	return $status;
}

sub search_address_m{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1 Jun 2011 15:19:10
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 2 Jun 2011 14:11:44
#Last modified by: MCC C. Gabriel Varela S. :The content is parsed
#Last modified on 3 Jun 2011 12:15:31
#Last modified by: MCC C. Gabriel Varela S. :The string $addresses_to_parse is parsed
#Last modified on 6 Jun 2011 11:12:17
#Last modified by: MCC C. Gabriel Varela S. :An array is returned
#Last modified on 13 Jun 2011 18:09:19
#Last modified by: MCC C. Gabriel Varela S. :Cookies are implemented

	#use HTTP::Cookies;
	my $Browser = LWP::UserAgent->new;
	$Browser->cookie_jar( {} );
	#my $cookie_jar = HTTP::Cookies->new(file     => "./cookies.lwp",autosave => 1, );
	#$Browser->cookie_jar( $cookie_jar );
	(my $number, my $zip) = @_;

	my $URL = "https://www.melissadata.com/lookups/zipnumber.asp?Zip=$zip&Number=$number&submit=Search";
# 	cgierr($URL);
	my $Response = $Browser->get($URL);
	my $to_parse=$Response->content;
	my $addresses=-1;
	my $address_number=-1;
	my $address_city=-1;
	my $address_state=-1;
	my $address_zip=-1;
	my $addresses_information;
	my @possible_addresses;
	my @to_cycle;
	
	if($to_parse=~/\<b.*\> (\d+) \<\/b\> Addresses with House Number \<b.*\> (\d+) \<\/b\> in.*\<b.*\>([\s|\w]+)\,\&nbsp\;(\w+)\&nbsp\;(\d+)/gi) {
		$addresses=$1;
		$address_number=$2;
		$address_city=$3;
		$address_state=$4;
		$address_zip=$5;
 		#cgierr( "Addresses: $1,Number: $2, City:$3, State: $4, Zip:$5<br>$to_parse");
	}
	
	if($addresses==-1)	{
		#&send_mail("gvsauceda\@inovaus.com","gvsauceda\@inovaus.com","No info found in melissa","Number:$number\r\nZip:$zip\r\nReturn:$to_parse\r\n");
		return($addresses,$address_number,$address_city,$address_state,$address_zip,@possible_addresses);
	}
	
	my $addresses_to_parse=$Response->content;
	
	#$addresses_to_parse=~s/\n//ig;
	
	#### OLD if($addresses_to_parse=~/\<tr\>\<td height\=\"5\" colspan\=\"4\" \>\<\/td\>\<\/tr\>(.*)\<tr\>\<td height\=\"5\" colspan\=\"4\" \>\<\/td\>\<\/tr\>/gi)	{
	@ary = split(/<tr><td height="5" colspan="4" ><\/td><\/tr>/,$addresses_to_parse);
	##if($addresses_to_parse=~/<tr><td height="5" colspan="4" ></td></tr>/gi)	{
	if($ary[1]){
		@lines = split(/\n/,$ary[1]);
		for (0..$#lines){
			if ($lines[$_] =~ /<td height="25" align="left" style="text-align:left; padding-left:5px;">(.*)/){
				push(@possible_addresses,substr($1,0,-6));
			}
		}
# 		$addresses_to_parse=~s/\n|\r|\t//ig;
		#split <td height="25" align="left" style="text-align:left; padding-left:5px;">
		###@to_cycle=split(/\<td height\=\"25\" align\=\"left\" style\=\"text\-align\:left\; padding\-left\:5px\;\"\> ([\s|\w]*)  \<\/td\>/gi,$addresses_to_parse);
		#@to_cycle = split(/<td height="25" align="left" style="text-align:left; padding-left:5px;">|<\/td>/i,$addresses_to_parse);
# 		cgierr("N:$#to_cycle\n 1:$to_cycle[0]\n2:$to_cycle[1]\n3:$to_cycle[2]\n4:$to_cycle[3]\n5:$to_cycle[4]\n6:$to_cycle[5]\n");
		#Possible addresses
		
		#for(1..($#to_cycle/2))		{
		#	$possible_addresses[$_]=$to_cycle[$_*2-1] if($to_cycle[$_*2-1]ne'');
		#}
# 		cgierr("N:$#possible_addresses\n 1:$possible_addresses[1]\n2:$possible_addresses[2]\n3:$possible_addresses[3]\n4:$possible_addresses[4]\n5:$possible_addresses[5]\n6:$possible_addresses[6]\n");
		
# 		if($addresses_to_parse=~/\<td height\=\"25\" align\=\"left\" style\=\"text\-align\:left\; padding\-left\:5px\;\"\> ([\s|\w]*)  \<\/td\>/gi)
# # 		if($addresses_to_parse=~/$regexp/gi)
# 		{
# # 		$addresses_to_parse=~s/\<tr bgcolor\=\'\#\w{6}\' onMouseOver\=\"this\.bgColor\=\'\#\w{6}\'\;\" onMouseOut\=\"this\.bgColor\=\'\#\w{6}\'\;\" \>\s*\<td height\=\"25\" align\=\"left\" style\=\"text\-align\:left\; padding\-left\:5px\;\"\> /washy/ig;
# 			cgierr("YES:1:$1,2:$2,3:$3,4:$4,pos:".pos());
# 		}
	}
	#cgierr( "Aqui:<pre>.$addresses,$address_number,$address_city,$address_state,$address_zip");
	return($addresses,$address_number,$address_city,$address_state,$address_zip,@possible_addresses);
# 	return $Response->content;
}

sub notify_asterisk_fail{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11 Aug 2011 10:35:01
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($ast_error)=@_;
	&send_text_mail("rbsrcenas\@inovaus.com","rbarcenas\@inovaus.com","Asterisk failed","From id: $in{'id'},\r\nnum: $in{'num'},\r\n usr=$usr{'id_admin_users'}");
	&send_text_mail("rbarcenas\@inovaus.com","carloshaas\@inovaus.com","Asterisk failed","From id: $in{'id'},\r\nnum: $in{'num'},\r\n usr=$usr{'id_admin_users'}");
	return 1;
}





sub mod_cod_sales_table{
# --------------------------------------------------------
# Forms Involved: sl_cod_sales table (Any process that modifies the table)
# Created on: 15 Sep 2011 13:18:19
# Author: Roberto Barcenas.
# Description : Suma y Resta cantidades de la tabla sl_cod_sales para mantener actualizados los numeros durante el dia
# Parameters : $id_orders | $n_status:El nuevo status

	my ($id_orders,$n_status,$from_process) = @_;


	my($o_status,$never,$more,$seven,$two,$one,$id_warehouses) = &get_cod_sale_status($id_orders);

	my $query;
	#my @ary_ware = split(/\|/,$id_warehouses);
	$id_warehouses =~ s/\|/,/g;
	$o_status = 'Processed-To be fulfilled' if $n_status eq 'Processed-In transit';
	$o_status = 'Processed-In transit' if $n_status eq 'Shipped';

	## Posibles Sumas
	$query .="UPDATE sl_cod_sales SET More=More+1 WHERE Status='$n_status' AND ID_warehouses IN($id_warehouses);" if $more;
	$query .="UPDATE sl_cod_sales SET Seven=Seven+1 WHERE Status='$n_status' AND ID_warehouses IN($id_warehouses);" if $seven;
	$query .="UPDATE sl_cod_sales SET Two=Two+1 WHERE Status='$n_status' AND ID_warehouses IN($id_warehouses);" if $two;
	$query .="UPDATE sl_cod_sales SET One=One+1 WHERE Status='$n_status' AND ID_warehouses IN($id_warehouses);" if $one;
	$query .="UPDATE sl_cod_sales SET Never=Never+1 WHERE Status='$n_status' AND ID_warehouses IN($id_warehouses);" if $never;

	## Posibles Restas
	if($from_process ne 'sales: New Order'){
		$query .="UPDATE sl_cod_sales SET More=IF(More=0,0,More-1) WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);" if $more;
		$query .="UPDATE sl_cod_sales SET Seven=IF(Seven=0,0,Seven-1) WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);" if $seven;
		$query .="UPDATE sl_cod_sales SET Two=IF(Two=0,0,Two-1) WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);" if $two;
		$query .="UPDATE sl_cod_sales SET One=IF(One=0,0,One-1) WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);" if $one;
		$query .="UPDATE sl_cod_sales SET Never=IF(Never=0,0,Never-1) WHERE Status='$o_status' AND ID_warehouses IN($id_warehouses);" if $never;
	}

	if($query ne''){
		&Do_mSQL("START TRANSACTION; $query COMMIT;");
		#&send_text_mail("rbarcenas\@inovaus.com","rbarcenas\@inovaus.com","COD Order Movement","ID Order:$id_orders\nFrom Process:$from_process\n$query");
	}

}





sub str_to_date{
# --------------------------------------------------------
# Forms Involved:
# Created on: 02/25/09 16:10:29
# Author: MCC C. Gabriel Varela S.
# Description :
# Parameters :

	my ($str_date,$string_format,$rtype) = @_;
	my ($sth);

	if($rtype eq 'date'){
		$sth = &Do_SQL("SELECT DATE(STR_TO_DATE('$str_date','$string_format'));");
	}elsif($rtype eq 'time'){
		$sth = &Do_SQL("SELECT TIME(STR_TO_DATE('$str_date','$string_format'));");
	}else{
		$sth = &Do_SQL("SELECT STR_TO_DATE('$str_date','$string_format');");
	}
	return $sth->fetchrow();
}


sub getWebsiteSales{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 29/11/2011 13:10:29
# Author: RB
# Description : Extrae informacion de las ventas Web para contabilizar bonos
# Description : Se puede usar de manera manual desde Developer Tools, o desde el cron de manera automatica
# Parameters :

	
	my ($modDates) = @_;
	if($in{'automatic'}){
		$modDates = " AND sl_orders.Date BETWEEN IF(MONTH(CURDATE())-1 = 0,CONCAT(YEAR(CURDATE())-1,'-12-01'),CONCAT(YEAR(CURDATE()),'-',MONTH(CURDATE())-1,'-01')) ";
		$modDates .= " AND LAST_DAY(IF(MONTH(CURDATE())-1 = 0,CONCAT(YEAR(CURDATE())-1,'-12-01'),CONCAT(YEAR(CURDATE()),'-',MONTH(CURDATE())-1,'-01'))) ";
	}


		my ($sth)= Do_SQL("SELECT sl_orders.ID_orders,
		sl_orders.Status,
	IF(sl_orders.ID_admin_users = 5020,'Algafit',
	IF(sl_orders.ID_admin_users = 5022,'Charakani',
	IF(sl_orders.ID_admin_users = 4122,'Chardon',
	IF(sl_orders.ID_admin_users = 5024,'Colageina',
	IF(sl_orders.ID_admin_users = 4688,'Innovashop',
	IF(sl_orders.ID_admin_users = 5027,'Naturaliv',
	IF(sl_orders.ID_admin_users = 5030,'Moinsage',
	IF(sl_orders.ID_admin_users = 5031,'Botas',
	IF(sl_orders.ID_admin_users = 5026,'Rejuvital',
	IF(sl_orders.ID_admin_users = 5201,'Puassance',
	IF(sl_orders.ID_admin_users = 5285,'AllNatPro',
	IF(sl_orders.ID_admin_users = 5288,'DreamBody',
	IF(sl_orders.ID_admin_users = 5368,'Diabestevia',
	IF(sl_orders.ID_admin_users = 5723,'NaturistaShop',
	IF(sl_orders.ID_admin_users = 5711,'Amazon',
	IF(sl_orders.ID_admin_users = 5725,'Keraorganiq','Unknown'))))))))))))))))AS Source,
	sl_orders.Date AS OrderDate,
	IF(sl_orders.PostedDate IS NULL OR sl_orders.PostedDate ='0000-00-00','N/A',sl_orders.PostedDate)AS ShippDate,
	GROUP_CONCAT(IF(sl_products.Name IS NULL,sl_parts.Name,sl_products.Name) SEPARATOR ' || ') As Products,
	SUM(sl_orders_products.Quantity)AS TotalProducts,
	IF(sl_orders.ID_admin_users IN(5027,5029),'Wholesale','Retail')AS SaleType,
	SUM(SalePrice-sl_orders_products.Discount)AS Price,
	SUM(sl_orders_products.Tax)AS Taxes,
	SUM(sl_orders_products.Shipping)AS Shipping,
	SUM(sl_orders_products.Cost)AS Cost,
	sl_orders.Status,IDCreator,NameCreator
	FROM
	(
		SELECT ID_orders,
		CONCAT(admin_users.FirstName,' ',admin_users.LastName)AS NameCreator,
		admin_users.ID_admin_users AS IDCreator
		FROM sl_orders_notes INNER JOIN admin_users
		ON sl_orders_notes.ID_admin_users = admin_users.ID_admin_users
		WHERE sl_orders_notes.Type='Web Creator'
	)AS sl_orders_notes
	INNER JOIN sl_orders
	ON sl_orders.ID_orders = sl_orders_notes.ID_orders
	INNER JOIN sl_orders_products
	ON sl_orders.ID_orders = sl_orders_products.ID_orders
	LEFT JOIN sl_products
	ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)
	LEFT JOIN sl_parts
	ON sl_parts.ID_parts = RIGHT(sl_orders_products.Related_ID_products,4)
	WHERE sl_orders.Status NOT IN('Void','Cancelled','System Error')
	AND sl_orders_products.Status='Active'
	$modDates
	GROUP BY sl_orders.ID_orders
	ORDER BY IDCreator,SaleType,sl_orders.Date,sl_orders.ID_orders;");

	if($sth->rows() == 0){
		$va{'matches'}=$sth->rows();
		$va{'message'} = &trans_txt('notmatch');
	}else{

		my $workbook,$worksheet,$date_format,$data_required,$data_extra;
		use Spreadsheet::WriteExcel;

		my $fname   = 'sosl_weborder_bonus.xls';

		($in{'e'} eq '1') and ($fname =~ s/sosl/usa/);
		($in{'e'} eq '2') and ($fname =~ s/sosl/pr/);
		($in{'e'} eq '3') and ($fname =~ s/sosl/training/);
		($in{'e'} eq '4') and ($fname =~ s/sosl/gts/);
		$fname =~	s/\///g;

		if($in{'automatic'}){
			## Save the File
			my $fpath = $cfg{'path_upfiles'} . 'xls_reports/weborders/';
			unlink $fpath . $fname if (-e $fpath . $fname);
			$workbook  = Spreadsheet::WriteExcel->new($fpath . $fname);

		}else{
			## On the fly
			print "Content-type: application/octetstream\n";
			print "Content-disposition: attachment; filename=$fname\n\n";
			$workbook  = Spreadsheet::WriteExcel->new("-");
		}


		$worksheet = $workbook->add_worksheet();
		my $format = $workbook->add_format();
		$format->set_text_wrap();
		## Formats
		my $date_format = $workbook->add_format(num_format => 'mm/dd/yy;@');
		my $time_format = $workbook->add_format(num_format => '[$-409]h:mm AM/PM;@');
		my $price_format = $workbook->add_format(align => 'right', num_format => '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)');
		my $porc_format = $workbook->add_format(num_format => '0.00%');
		my $n2_format = $workbook->add_format(num_format => '0.00');
		my $hformat = $workbook->add_format(border  => 0,valign  => 'vcenter',align   => 'center',bg_color   => 'blue',color   => 'white');
		
		# Headers.
		$worksheet->write(0, 0,'ID Order',$hformat);
		$worksheet->write(0, 1,'Date Order',$hformat);
		$worksheet->write(0, 2,'Date Shipped',$hformat);
		$worksheet->write(0, 3,'Source',$hformat);
		$worksheet->write(0, 4,'Type',$hformat);
		$worksheet->write(0, 5,'Products',$hformat);
		$worksheet->write(0, 6,'Quantity',$hformat);
		$worksheet->write(0, 7,'OrderNet',$hformat);
		$worksheet->write(0, 8,'Taxes',$hformat);
		$worksheet->write(0, 9,'Shipping',$hformat);
		$worksheet->write(0, 10,'Cost',$hformat);
		$worksheet->write(0, 11,'ID Operator',$hformat);
		$worksheet->write(0, 12,'Name Operator',$hformat);
		$worksheet->write(0, 13,'Status',$hformat);
		$worksheet->write(0, 14,'Status',$hformat);

		$row=1;
		ORDERS:while(my($id_orders,$status,$source,$orderDate,$shipDate,$products,$qty,$type,$price,$tax,$shp,$cost,$status,$id_creator,$name_creator) = $sth->fetchrow()){

			$products =~ s/\|\|/<br>/g;

			$worksheet->write_number($row,0,$id_orders); #1
			$worksheet->write_string($row,1,$orderDate,$date_format); #1
			$worksheet->write_string($row,2,$shipDate,$date_format); #1
			$worksheet->write_string($row,3,$source); #1
			$worksheet->write_string($row,4,$type); #1
			$worksheet->write_string($row,5,$products,$format); #1
			$worksheet->write_number($row,6,$qty); #1
			$worksheet->write_number($row,7,$price, $price_format ); #1
			$worksheet->write_number($row,8,$tax, $price_format); #1
			$worksheet->write_number($row,9,$shp, $price_format); #1
			$worksheet->write_number($row,10,$cost, $price_format); #1
			$worksheet->write_number($row,11,$id_creator); #1
			$worksheet->write_string($row,12,$name_creator); #1
			$worksheet->write_string($row,13,$status); #1
			$worksheet->write_formula($row,14,"=TEXT(B".($row+1).",\"yy-mm\")");
			$row++;
		}
		$workbook->close();
	}

}





sub product_family {
# --------------------------------------------------------
	my ($prod) = @_;
	my ($key,$n,$p);
	if (!$famprod{'loaded'}){
		$famprod{'loaded'} = 1;
		my ($sth) = &Do_SQL("SELECT Name, Pattern FROM sl_media_prodfam WHERE Status='Active'");
		while(($n,$p)=$sth->fetchrow_array()){
			$famprod{$p} = $n;
		}

	}
	foreach $key (keys %famprod){
		if ($prod =~ /$key/i and $key ne 'loaded'){
			return $famprod{$key};
		}
	}
	return 'Others';
}





sub set_urlfixed_ecommerce{
# --------------------------------------------------------
# Created :  Roberto Barcenas 02/09/2012 7:021:28 PM
# Last Update :
# Description : Modifca el nombre de los productos en sl_products_w para presentarlos en la url

	&Do_SQL("update `sl_products_w` set Name=replace(Name,'   ',' ');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'  ',' ');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,' ','-');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'á','a');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'é','e');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'í','i');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'ó','o');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'ú','u');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'+','mas');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'&','-');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'?','');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'ñ','n');");
	&Do_SQL("update `sl_products_w` set Name=replace(Name,'.','');");


}

sub calculate_dates{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11 Jan 2011 11:04:19
# Author: 
# Description :   
# Parameters :
# Last Time Modified by RB on 05/14/2012: Se cambia calculo de fechas por rango mensual

	my($lowlimit,$highlimit,$period) = @_;
	my ($query_period);

	$lowlimit = 7 if !$lowlimit;
	$highlimit = 21 if !$highlimit;
	$period = 'this' if !$period;

	if($period eq 'this'){
		
		$query_period = "SELECT CONCAT( CONCAT(DATE_FORMAT(LAST_DAY(CURDATE()),'%Y-%m-'),'01'),';;', LAST_DAY(CURDATE()));"; 
		
#		$query_period = "SELECT IF( DAYOFMONTH( CURDATE() ) BETWEEN $lowlimit AND $highlimit,
#					/* Si el dia del mes en curso esta entre el rango del 7-21, se entrega reporte de este rango */
#					CONCAT( YEAR(CURDATE()),'-',MONTH(CURDATE()),'-$lowlimit;;',YEAR(CURDATE()),'-',MONTH(CURDATE()),'-$highlimit') ,
#					IF( DAYOFMONTH( CURDATE() ) < $lowlimit,
#					/* Si dia de mes en curso menor que 7, se entrega reporte mes anterior(22) con mes actual (6) */
#					CONCAT(YEAR(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',MONTH(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',$highlimit+1,';;',YEAR(CURDATE()),'-',MONTH(CURDATE()),'-',$lowlimit-1) ,
#					/* Si dia de mes en curso mayor que 21, se entrega mes actual (22) con mes siguiente (6) */
#					CONCAT( YEAR(CURDATE()),'-',MONTH(CURDATE()),'-',$highlimit+1,';;',YEAR(DATE_ADD(CURDATE(), INTERVAL 1 MONTH)),'-',MONTH(DATE_ADD(CURDATE(), INTERVAL 1 MONTH)),'-',$lowlimit-1)
#					));";
	}else{
		
		my $interval = $period eq 'lastx2' ? 2 : 1;
		$query_period = "SELECT CONCAT( CONCAT(DATE_FORMAT(LAST_DAY(CURDATE() - INTERVAL $interval MONTH),'%Y-%m-'),'01'),';;',  LAST_DAY(CURDATE() - INTERVAL $interval MONTH) );";
		
#		$query_period = "SELECT IF( DAYOFMONTH( CURDATE() ) BETWEEN $lowlimit AND $highlimit,
#					/* Si el dia del mes en curso esta entre el rango del 7-21, se entrega reporte mes anterior(22) con mes actual (6) */
#					CONCAT(YEAR(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',MONTH(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',$highlimit+1,';;',YEAR(CURDATE()),'-',MONTH(CURDATE()),'-',$lowlimit-1),
#					IF( DAYOFMONTH( CURDATE() ) < $lowlimit,
#					/* Si dia de mes en curso menor que 7, se entrega mes anterior (7-21) */
#					CONCAT(YEAR(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',MONTH(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-$lowlimit;;',YEAR(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-',MONTH(DATE_SUB(CURDATE(),INTERVAL 1 MONTH)),'-$highlimit' ) ,
#					/* Si dia de mes en curso mayor que 21, se entrega mes actual (7-21) */
#					CONCAT( YEAR(CURDATE()),'-',MONTH(CURDATE()),'-$lowlimit;;',YEAR(CURDATE()),'-',MONTH(CURDATE()),'-$highlimit')
#					));";
	}

	my ($sth) = Do_SQL($query_period);
	my($dates) = $sth->fetchrow();
	my($day_start,$day_end) = split(/;;/,$dates,2);
	return($day_start,$day_end);
	
}



###############################################################################
#	Function: media_reset_drip
#
#		- Resetea contratos de ordenes que habian sido asignadas a goteo dentro de un rango de fechas recibidas
#
#	Created by: _Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		from_date, to_date
#
#   	Returns:
#
#   	See Also:
#
#      None
sub media_reset_drip{
###############################################################################

	my($from_date, $to_date) = @_;

	my ($sth) = Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts WHERE DestinationDID = 9996 AND ESTDay BETWEEN '$from_date' AND '$to_date' ORDER BY ID_mediacontracts;");
	my ($total) = $sth->fetchrow();
	
	if($total > 0){

		my ($sth) = Do_SQL("SELECT GROUP_CONCAT(ID_mediacontracts) FROM sl_mediacontracts WHERE DestinationDID = 9996 AND ESTDay BETWEEN '$from_date' AND '$to_date' ORDER BY ID_mediacontracts;");
		my ($ids) = $sth->fetchrow();
	
		my ($sth) = Do_SQL("UPDATE sl_orders SET sl_orders.ID_mediacontracts = 0 WHERE ID_mediacontracts IN($ids);");
		my ($sth) = Do_SQL("UPDATE sl_leads_calls SET sl_leads_calls.ID_mediacontracts = 0 WHERE ID_mediacontracts IN($ids);");
	}

}

sub template_bulkprnbutton{
# --------------------------------------------------------
	## ToDO: Revisar permisos (Solo de View), vercuantos templates hay disponibles, si hay mas de 1 llamar a ventana en Ajax
	## Si hay uno directo se puede llamar.
	##
	my ($output,$c);&cgierr;
	$in{'cmd'} = 'opr_orders';
	if(&check_permissions($in{'cmd'},'_print','')){	
		(!$sys{'db_'.$in{'cmd'}.'_prntemp'}) and ($sys{'db_'.$in{'cmd'}.'_prntemp'} = $sys{'db_'.$in{'cmd'}.'_form'});
		my (@ary) = split(/,/, $sys{'db_'.$in{'cmd'}.'_prntemp'});
		if ($#ary >= 1){
			$output .= qq| <tr><td align='left'>Print Type:</td><td>|;
			my $fname = $cfg{'path_templates'}.'print/dbman/';
			$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
			for my $i(0..$#ary){
				if ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.e'.$in{'e'}.'.html') and $i eq 0){
					$output  .= qq|<input type="radio" name="f" value="|.$i.qq|" class="radio"> $ary[$i]<br>|;
					#$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=Print&toprint=$in{lc($db_cols[0])}')\" class=menu>$ary[$i]</a>\n";
					++$c;
				}elsif ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.e'.$in{'e'}.'.html') and $i>0){
					$output  .= qq|<input type="radio" name="f" value="|.($i+1).qq|" class="radio"> $ary[$i]<br>|;
					#$output .= " <a href=\"javascript:prnwin('/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&search=Print&toprint=$in{lc($db_cols[0])}&f=".($i+1)."')\" class=menu>$ary[$i]</a>\n";
					++$c;
				}
			}
			
			$output .= qq| </tr></td>|;
			if ($c eq 1){
				$output  .= qq|<input type="radio" name="f" value="|.($i+1).qq|" class="radio"> $ary[$i] <br>|;
			}
			$output .= qq| <tr><td align="center" colspan="2"><br><input type="button" onclick="toprn();" value="Print" class="button"></td></tr> |;
			$output .= qq| <script type="text/javascript">
					
					function toprn(){
						var orders = \$('#id_orders_bulk').val();
						var format = \$('input:radio[name=f]:checked').val();						
						if(orders!="" && format!=""){
							
							prnwin("/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&search=Print&toprint="+orders+"&f="+format+"")\							
						}else{
							alert("Favor de ingresar id de las ordenes y formato valido.");
						}
					}
			
			
			
					</script>|;
			
		}
	}
	return $output;
}

sub template_prnbutton_wh{
# --------------------------------------------------------
	## ToDO: Revisar permisos (Solo de View), vercuantos templates hay disponibles, si hay mas de 1 llamar a ventana en Ajax
	## Si hay uno directo se puede llamar.
	##
	my ($output,$c);
	$in{'cmd'} = 'opr_orders';
	if(&check_permissions($in{'cmd'},'_print','')){	
		(!$sys{'db_'.$in{'cmd'}.'_prntemp'}) and ($sys{'db_'.$in{'cmd'}.'_prntemp'} = $sys{'db_'.$in{'cmd'}.'_form'});
		my (@ary) = split(/,/, $sys{'db_'.$in{'cmd'}.'_prntemp'});
		if ($#ary >= 1){
			$output .= qq| <tr><td align='left'>Print Type:</td><td>|;
			my $fname = $cfg{'path_templates'}.'print/dbman/';
			$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
			for my $i(0..$#ary){
				if ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.'.e'.$in{'e'}.'.html') and $i eq 0){
					$output  .= qq|<input type="radio" name="f" value="|.$i.qq|" class="radio"> $ary[$i] <br>|;
					++$c;
				}elsif ((-e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.html' or -e $fname.$sys{'db_'.$in{'cmd'}.'_form'}.($i+1).'.e'.$in{'e'}.'.html') and $i>0){
					$output  .= qq|<input type="radio" name="f" value="|.($i+1).qq|" class="radio"> $ary[$i] <br>|;
					++$c;
				}
			}
			
			$output .= qq| </tr></td>|;
			if ($c eq 1){
				$output  .= qq|<input type="radio" name="f" value="|.($i+1).qq|" class="radio"> $ary[$i] <br>|;
			}
			$output .= qq| <tr><td align="center" colspan="2"><br><input type="button" onclick="toprn();" value="Print" class="button"></td></tr> |;
			$output .= qq| <script type="text/javascript">
					
					function toprn(){						
						var allVals = [];
						\$('[name=id_ordersttia]:checked').each(function() {
							allVals.push(\$(this).val());
						});

						var orders = allVals != '' ? allVals : \$('#id_orders_bulk').val();
						var format = \$('input:radio[name=f]:checked').val();						
						if(orders!="" && format!=""){
							prnwin("/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&search=Print&toprint="+orders+"&f="+format+"")\							
						}else{
							alert("Favor de ingresar id de las ordenes y formato valido.");
						}
					}
					</script>|;
			
		}
	}
	return $output;
}


#############################################################################
#############################################################################
#   Function: skus_quantity_inbatch
#
#       Es: Recibe un sku y devuelve la suma total en batches
#       En: 
#
#    Created on: 09/24/2008  16:21:10
#
#    Author: _RB_
#
#    Modifications: 03/02/2016 Se modifica Query
#
#   Parameters:
#
#
#  Returns:
#
#
#   See Also:
#
#
sub skus_quantity_inbatch {
#############################################################################
#############################################################################

	my ($id_products) = @_;
	my ($qty_inbatch) = 0;
	
	if ($id_products){

		my ($sth) = &Do_SQL("SELECT * FROM vw_products_in_batch WHERE ID_parts = '$id_products';");
		$qty_inbatch = $sth->fetchrow();

	}

	return $qty_inbatch;

}


#############################################################################
#############################################################################
#   Function: run_sp_users
#
#       Es: 
#       En: Fast Check order Alert
#
#
#    Created on: 04/08/2015
#
#    Author: _RB_ 
#
#    Modifications:
#    
#
#   Parameters:
#
#      - All $in{}
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub run_sp_users {
#############################################################################
#############################################################################

	if(&table_exists('sl_vars_config')){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_vars_config WHERE Command = 'fastCheckOrder' AND Code LIKE '%". $usr{'id_admin_users'} ."%';");
		my ($this_user) = $sth->fetchrow();

		if($this_user){

			## Suspicious User Viewing the order
			my $status;
			my $subject = &trans_txt('internal_system_alert');
			my $body = $in{'id_orders'} . '       ' . $va{'status'} . '        ' . $va{'statusprd'} . '        ' . $usr{'firstname'} . ' ' . $usr{'lastname'} . ' (' . $usr{'id_admin_users'} . ')';
			my $from_email = 'info@inova.com.mx';
			my $to_email = $cfg{'environment'} eq 'production' ? &load_name('sl_vars_config', 'Command', 'to_email_suspicious_users','Code') : $cfg{'to_email_debug'};

			if($to_email){

				$status = &send_mandrillapp_email($from_email,$to_email,$subject,$body,$body,'');
				
				if($status eq 'ok'){
					
				}else{
						
				}

			}

		}


	}

}



1;