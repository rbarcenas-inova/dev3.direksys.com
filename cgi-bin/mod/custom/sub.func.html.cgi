#!/usr/bin/perl

####################################################################
########              Home Page                     ########
####################################################################

sub load_startconsole {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_operpages WHERE Type='follow-up Start Console' AND Status='Active'");
	if ($sth->fetchrow()>0){
		my ($sth) = &Do_SQL("SELECT Speech FROM sl_operpages WHERE Type='follow-up Start Console' AND Status='Active' ORDER BY ID_operpages DESC");
		return $sth->fetchrow() . "<p align='right' class='smalltxt'>follow-up Start Console</p>" ;
		#return $sth->fetchrow() ;
	}else{
		return "<p align='right' class='smalltxt'>follow-up Start Console</p>";
	}
}

sub header_links(){
# --------------------------------------------------------
	my (@list) = split(/,/, $cfg{'applications'});
	my (@ary_url,@ary_img,$output);
	for my $i(0..$#list/3) {
		$ary_url{$list[$i*3]} = $list[$i*3+2];
		$ary_img{$list[$i*3]} = $list[$i*3+1];
	}
	my (@prefs) = split(/\|/, $usr{'pref_applications'});
 	for my $i(0..$#prefs) {
		if ($ary_img{$prefs[$i]}){
			($ary_url{$prefs[$i]} =~ /^http/) ? ($linkto = "target='blank'"):
										($linkto = "");
			#($ary_url{$prefs[$i]} =~ /egw/) and ($ary_url{$prefs[$i]} .= "?sessionid=$usr{'egw_sessionid'}&kp3=0&domain=default");
			
			$output .= "<a href='".$ary_url{$prefs[$i]}."' $linkto><img src='$va{'imgurl'}/app_bar/".$ary_img{$prefs[$i]}."' title='$prefs[$i]' alt='' border='0'></a>\n";
		}
	}
	return $output;
}

sub validate_year {
# --------------------------------------------------------
	#&cgierr("year: $in{'year'}");
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	$the_year =$year + 1900;
	
	$tmp = $in{'year'};
	if ($in{'year'} < $the_year) {
		$year = $the_year;
	}else{
		$year = $tmp;		
	}
	$in{'year'} = $year;
}



sub build_read_dayhour {
# --------------------------------------------------------
	my ($output);
	my (@ary) = split(/,/,$cfg{'dayhour'});
  $k=0;
	for (0..$#ary){
		$k ++;
	 if ($k == $horar) {
	  $output ="$ary[$_]";
   } 
	}
	return $output;
}



sub list_laybystatus{
#-----------------------------------------
# Created on: 11/25/08  13:09:10 By  Roberto Barcenas
# Forms Involved: opr_preorders_list
# Description : Builds an show active preorder tab by status depends on choice 
# Parameters : 
# Last modification : JRG 01/21/2009 : Se agrega la lista de cod
# Last Time Modified By RB on 2/16/10 2:06 PM : Se cambia para direccionar a Orders y se revisa que funcione para Layaway y COD
	
	my ($cad,$cod,$gen,$proc,$new,$can,$due);
	
	$cad = '';
	#&cgierr("$in{'paytype'}");
	if($in{'ptype'}){
		(!$in{'status'}) and ($gen='on') and ($new='off') and ($proc='off') and ($can='off');
		($in{'status'} and !$in{'statuspay'}) and ($gen='off')  and ($new='on') and ($proc='off') and ($can='off');
		($in{'status'} eq 'Processed') and ($gen='off') and ($new='off') and ($proc='on') and ($can='off');
		($in{'status'} eq 'Cancelled') and ($gen='off') and ($new='off') and ($proc='off') and ($can='on');
		
		if($in{'ptype'} eq 'Layaway'){
		    $due = 'off';
		    ($in{'statuspay'} eq 'Layaway Due') and ($due = 'on') and ($gen='off') and ($new='off') and ($proc='off') and ($can='off');
		    $cad = qq|<td class='gcell_$due' align='center' onClick='trjump("/cgi-bin/mod/crm/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=New&statusPay=Layaway Due&so=DESC&ptype=$in{'ptype'}")'>Due</td>|;
		}

		
		
		$cad = qq|
							<table width="100%" border="0" cellspacing="0" cellpadding="0" class="gtab" align="center">
				  			<tr>
							    <td width="30%" align="center"></td>
							    <td class='gcell_$gen' align='center' onClick='trjump("/cgi-bin/mod/crm/dbman?cmd=opr_orders&search=listall&sb=id_orders&so=DESC&ptype=$in{'ptype'}")'>All</td>
							    <td class='gcell_$new' align='center' onClick='trjump("/cgi-bin/mod/crm/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=New&so=DESC&ptype=$in{'ptype'}")'>New</td>
							    <td class="gcell_$proc" align="center" onClick='trjump("/cgi-bin/mod/crm/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=Processed&so=DESC&ptype=$in{'ptype'}")'>Processed</td>
							    $cad
							    <td class="gcell_$can" align="center" onClick='trjump("/cgi-bin/mod/crm/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=Cancelled&so=DESC&ptype=$in{'ptype'}")'>Cancelled</td>
							  </tr>
							</table>|;
	}
}

sub list_laybypayday{
#-----------------------------------------
# Created on: 11/25/08  13:09:10 By  Roberto Barcenas
# Forms Involved: preorders_payments_list
# Description : Builds an show active preorder tab by payday depends on choice 
# Parameters :
# Last Time Modified By RB on 2/16/10 2:09 PM : Se redirecciona a Orders debido al desuso de Preorders 
	
	my ($cad,$td,$trd,$sd,$fd,$thd);
	$in{'range'} eq 'today' if !$in{'range'};
	($in{'range'} eq 'today') and ($td='on') and ($trd='off') and ($sd='off') and ($fd='off') and ($thd='off');
	($in{'range'} eq '3d') and ($td='off') and ($trd='on') and ($sd='off') and ($fd='off') and ($thd='off');
	($in{'range'} eq '7d') and ($td='off') and ($trd='off') and ($sd='on') and ($fd='off') and ($thd='off');
	($in{'range'} eq '15d') and ($td='off') and ($trd='off') and ($sd='off') and ($fd='on') and ($thd='off');
	($in{'range'} eq '30d') and ($td='off') and ($trd='off') and ($sd='off') and ($fd='off') and ($thd='on');
	
	$cad = qq|
						<table width="100%" border="0" cellspacing="0" cellpadding="0" class="gtab" align="center">
			  			<tr>
						    <td width="30%" align="center"></td>
						    <td class='gcell_$td' align='center' onClick='trjump("/cgi-bin/mod/crm/admin?cmd=orders_payments&range=today")'>Today</td>
						    <td class='gcell_$trd' align='center' onClick='trjump("/cgi-bin/mod/crm/admin?cmd=orders_payments&range=3d")'>Last  3 Days</td>
						    <td class="gcell_$sd" align="center" onClick='trjump("/cgi-bin/mod/crm/admin?cmd=orders_payments&range=7d")'>Last Week</td>
						    <td class="gcell_$fd" align="center" onClick='trjump("/cgi-bin/mod/crm/admin?cmd=orders_payments&range=15d")'>Last 2 Weeks</td>
						    <!--<td class='gcell_$thd' align='center' onClick='trjump("/cgi-bin/mod/crm/admin?cmd=orders_payments&range=30d")'>Last Month</td>-->
						  </tr>
						</table>|;
}


sub build_tracking_templates_list{
# --------------------------------------------------------
# Forms Involved:	eco_sendmail.html
# Created on: 06/03/2010 15:20:51
# Author: RB.
# Description : Genera radio buttons con los templates existentes para envio de email  
# Parameters :
#Last modified on 6 Oct 2010 18:38:44
#Last modified by: MCC C. Gabriel Varela S. :Se copia de administration
# Last Modified on: 11/08/10 13:00:35
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta lang de $usr

		my $dir = $cfg{'path_templates'} . '/app/crm/email_templates';
#		$dir =~	s/\[lang\]/en/;
		$dir=~s/\[lang\]/$usr{'pref_language'}/;
		
		my $strout = '';
	
		if(-d "$dir"){
		
		    opendir(DIR, $dir) or die $!;
				my $i=0;
		    while (my $file = readdir(DIR)) {

		       # We only want files
		        next unless (-f "$dir/$file");
		        # Use a regular expression to find files ending in .txt
		        next unless ($file =~ m/\.txt$/);
		        
		       @fields = split (/\./, $file);
		       my $fname = $fields[0];
						
						#$strout .= "<br>"	if $i%5==0;
						$strout .= qq|<td><input name="template" value="$fname" class="radio" type="radio">|. $fname .qq|</td>|;
						$i++;
						if($i%4==0)
						{
							$strout .= qq|</tr><tr><td>&nbsp;</td></tr><tr>|;
						}
		    }
		    closedir(DIR);
		}else{
				print "No existe la ruta ". $cfg{'path_templates'} . 'email_templates';
		}
		return $strout;
}

sub save_imap_email{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 20 Oct 2010 17:27:37
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	
	use Mail::IMAPClient;
	use Email::MIME;
	
# 	my $imap = Mail::IMAPClient->new(
# 	Server   => $cfg{'imap_server'},
# 	Port     => $cfg{'imap_port'},
# 	Ssl      => $cfg{'ssl'},
# 	User     => $cfg{'user'},
# 	Password => $cfg{'pwd'},
# 	IgnoreSizeErrors => 1
# 	)
# 	or die "new(): $@";
	
	my $imap = Mail::IMAPClient->new(
	Server   => $cfg{'imap_server'},
	Port     => $cfg{'imap_port'},
	Ssl      => $cfg{'imap_ssl'},
	User     => $cfg{'imap_user'},
	Password => $cfg{'imap_pwd'},
	IgnoreSizeErrors => 1
	)
	or die "new(): $@";
	
	my ($from_mail,$to_mail,$subject_mail,$body_mail) = @_;
	my $mail_file="";
	$mail_file.="Date: \n";
	$mail_file.="From: $from_name <$from_mail>\n";
	$mail_file.="To: <$to_mail>\n";
	$mail_file.='Content-type: text/plain; charset=iso-8859-1' . "\n";
	$mail_file.="Subject: $subject_mail\n\n";
	
# 	$mail_file.="Reply-To: $from_mail <$from_mail>\n";
# 	$mail_file.="Return-Path: $from_mail\n\n";
	$mail_file.="$body_mail\n\n";
	
	my $new_msg_uid = $imap->append(
	    '[Gmail]/Sent Mail',
	    $mail_file
	) or die "Could not append: ", $imap->LastError;
	return "$new_msg_uid";

}

sub move_imap_email{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 22 Oct 2010 18:36:31
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#	use Mail::IMAPClient;
#	use Email::MIME;
#	
## 	my $imap = Mail::IMAPClient->new(
## 	Server   => $cfg{'imap_server'},
## 	Port     => $cfg{'imap_port'},
## 	Ssl      => $cfg{'ssl'},
## 	User     => $cfg{'user'},
## 	Password => $cfg{'pwd'},
## 	IgnoreSizeErrors => 1
## 	)
## 	or die "new(): $@";
#	
#	my $imap = Mail::IMAPClient->new(
#	Server   => $cfg{'imap_server'},
#	Port     => $cfg{'imap_port'},
#	Ssl      => $cfg{'imap_ssl'},
#	User     => $cfg{'imap_user'},
#	Password => $cfg{'imap_pwd'},
#	IgnoreSizeErrors => 1
#	)
#	or die "new(): $@";
#	
#	my($oldUid,$newFolder)=@_;
#	$imap->select('INBOX') or die "Could not select: $@\n";
# 	$imap->Uid(true);
# 	#cgierr("$oldUid,$newFolder,".$imap->Uid());
#	$imap->Uid(true);
#	my $newUid = $imap->move($newFolder, $oldUid)
#    or die "Could not move: $@\n";
#  $imap->expunge;
  return $newUid;
}

1;
