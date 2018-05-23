
##########################################################
##		MEDIA
##########################################################
sub view_mm_stations {
# --------------------------------------------------------
	if ($in{'id_dmas'}){
		$in{'dma_info'} = &load_name('sl_dmas','ID_dmas',$in{'id_dmas'},'DMA');
	}
}

sub view_mm_dmas {
# --------------------------------------------------------
	$in{'htvhh'} = &format_number($in{'htvhh'},0);
	$in{'hyvhh'} = &format_number($in{'hyvhh'},0);
	$in{'wcporc'} = &round($in{'hyvhh'}/$in{'htvhh'}*100,2);
}

sub view_mm_media {
# --------------------------------------------------------
	$in{'amount'} = &format_price($in{'amount'});
}




sub validate_mm_destinations{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12 Aug 2011 17:13:15
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# 	@db_cols=('didusa','FromDate','FromTime','ToDate','ToTime','Destination');
# 	cgierr("dfdfdfdf".$#db_cols);
	if(!$in{'didusa'} and $in{'dnis_i'})
	{
		$in{'didusa'}=$in{'dnis_i'};
	}
	return 0;
}

sub view_mm_destinations{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12 Aug 2011 17:13:15
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# 	@db_cols=('didusa','FromDate','FromTime','ToDate','ToTime','Destination');
# 	cgierr("dfdfdfdf".$#db_cols);
	$in{'second_conn'}=1;
	return 0;
}


sub view_mm_dids{
# --------------------------------------------------------
# Forms Involved:
# Created on: 02 Dec 2011 12:25:22
# Author: Roberto Barcenas.
# Description : Busca en s7 el callcenter al que esta asignado el DID
# Parameters :

	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});

	if($in{'chgd'}){
		my $sth=&Do_SQL("UPDATE sl_numbers SET Destination='$in{'chgd'}' WHERE didmx='$in{'didmx'}';",1);
		if($sth->rows() > 0){
			&auth_logging('destination_updated',$in{'didmx'},1);
			$va{'message'} = 'Destination Updated';
		}else{
			$va{'message'} = 'The Destionation Callcenter was not changed';
		}
	}

	
	$in{'second_conn'}=1;
	my (@callcenters) = load_enum_toarray('sl_numbers','Destination');
	my $sth=&Do_SQL("SELECT Destination From sl_numbers WHERE didmx='$in{'didmx'}' ;",1);
	($in{'destination'}) = $sth->fetchrow();

	my $position;
	for (0..$#callcenters ) {
		$va{'chg_destination'} .= qq|<a href="$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_mediadids'}&chgd=$callcenters[$_]">$callcenters[$_]</a>&nbsp;&nbsp;\n| if($callcenters[$_] ne "$in{'destination'}");
	}
	$va{'chg_destination'} = qq| - Change To $va{'chg_destination'}|;
	$in{'second_conn'}=0;
}


sub view_mm_contracts{
# --------------------------------------------------------
# Forms Involved:
# Created on: 07 Dec 2011 11:12:22
# Author: Roberto Barcenas.
# Description : 
# Parameters :
# Last Time Modified by RB on 02/06/2012: Se agrega nota de edicion y se abren contratos del DID pasado y nuevo
# Last Time Modified by RB on 05/07/2012: Se agrega reseteo de goteo cuando se reasigna did

	if($in{'chgstatus'}){
		my $sth=&Do_SQL("UPDATE sl_mediacontracts SET Status='$in{'chgstatus'}' WHERE ID_mediacontracts='$in{'id_mediacontracts'}';");
		if($sth->rows() > 0){
			&mediacontracts_edit_status();
			$in{'status'}=$in{'chgstatus'};
			&auth_logging('mediacontracts_status_updated',$in{'id_mediacontracts'});
			$va{'message'} = 'Status Updated';
		}else{
			$va{'message'} = 'The Status was not changed';
		}
	}

	## DestinationDID edited
	if($in{'edit_did'}){
		
		## Come from jquery in contracts_view template
		my ($sth)=&Do_SQL("UPDATE sl_mediacontracts SET DestinationDID ='$in{'edit_did'}', Status='Programado' WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
		if($sth->rows() == 1){
			&mediacontracts_edit_did();
			&auth_logging('mediacontracts_did_updated',$in{'id_mediacontracts'});
			$va{'message'}=&trans_txt('contract_updated');
			$in{'destinationdid'} = $in{'edit_did'};
			delete($in{'edit_did'});
		}

	}

	## ESTDay edited
	if($in{'edit_estday'}){

		my @ary_datetime = split(/ /,$in{'edit_estday'});

		my ($sth)=&Do_SQL("UPDATE sl_mediacontracts SET ESTDay ='".$ary_datetime[0]."', ESTTime='".$ary_datetime[1]."' WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
		if($sth->rows() == 1){
			$in{'old_dates'} = "$in{'estday'} $in{'esttime'}";
			$in{'estday'} = $ary_datetime[0];
			$in{'esttime'} = $ary_datetime[1];

			&mediacontracts_edit_estday();
			&auth_logging('mediacontracts_estday_updated',$in{'id_mediacontracts'});
			$va{'message'}=&trans_txt('contract_updated');
			delete($in{'edit_estday'});
		}
	}




	&auth_logging('mediacontracts_viewed',$in{'id_mediacontracts'});

	## Cost
	$in{'cost'} = &format_price($in{'cost'});
	$va{'chg_cost'} = qq|<span id="span_chg_cost"><img id="btn_chg_cost" src="/sitimages/default/b_edit.png" title="Click to edit Cost" style="cursor:pointer;"></span>|;
	
	## ESTDay
	$va{'chg_estday'} = qq|<span id="span_chg_estday"><img id="btn_chg_estday" src="/sitimages/default/b_edit.png" title="Click to edit ESTDay" style="cursor:pointer;"></span>|;

	## Destination
	my @dest;
	$va{'chg_destination'} = qq|<span id="span_chg_destination"><img id="btn_chg_destination" src="/sitimages/default/b_edit.png" title="Click to edit Destination" style="cursor:pointer;"></span>|;
	my $sth=&Do_SQL("SELECT DISTINCT(Destination) FROM sl_mediacontracts WHERE LENGTH(Destination) > 3 ORDER BY Destination;");
	DEST:while(my($name)=$sth->fetchrow()){
		next DEST if $name eq $in{'destination'};
		push(@dest,"'$name':'$name'");
	}
	$va{'destination_options'} = qq|options:{|.join(',',@dest).qq|}|;
	
	$in{'family'} = &product_family($in{'offer'});

	## DestinationDID
	my @dids;
	$va{'chg_destinationdid'} = qq|<span id="span_chg_destinationdid"><img id="btn_chg_destinationdid" src="/sitimages/default/b_edit.png" title="Click to edit DestinationDID" style="cursor:pointer;"></span>|;
	my $sth=&Do_SQL("SELECT didmx,CONCAT(didmx,' -- ',product,'\@',IF(Promocion IS NOT NULL AND Promocion <> '0',Promocion,''))AS name FROM sl_mediadids WHERE Status='Active' ORDER BY didmx;");
	DIDS:while(my($didmx,$name)=$sth->fetchrow()){
		next DIDS if $didmx == $in{'destnationdid'};
		push(@dids,"'$didmx':'$name'");
	}
	$va{'destinationdid_options'} = qq|options:{|.join(',',@dids).qq|}|;


	## Offer

	$va{'chg_offer'} = qq|<span id="span_chg_offer"><img id="btn_chg_offer" src="/sitimages/default/b_edit.png" title="Click to edit Offer" style="cursor:pointer;"></span>|;

	## Status
	my (@ary_status) = load_enum_toarray('sl_mediacontracts','Status');
	for (0..$#ary_status ) {
		$va{'chg_status'} .= qq|<a href="$va{'script_url'}?cmd=$in{'cmd'}&view=$in{'id_mediacontracts'}&chgstatus=$ary_status[$_]">$ary_status[$_]</a>&nbsp;&nbsp;\n| if($ary_status[$_] ne "$in{'status'}");
	}
	$va{'chg_status'} = qq|&nbsp;&nbsp;-&nbsp;&nbsp;Change To $va{'chg_status'}|;

}

sub validate_mm_contracts{
# --------------------------------------------------------
	my ($err);
	$in{'week'} = int($in{'week'});
	if ($in{'week'} > 53 or $in{'week'} < 0){
		$error{'week'} = &trans_txt('invalid');
		++$err;
	}
	if ($in{'addd'}){
		$in{'mediastatus'} = 'Open';
	}
	return $err;
}

1;