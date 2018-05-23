##########################################################
##		PERM MANAGER
##########################################################
sub validate_eco_productsw{
# --------------------------------------------------------
# Created on: 09/23/08 @ 15:13:52
# Author: Carlos Haas
# Last Modified on: 09/23/08 @ 15:13:52
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#
	#$in{'not_autoincrement'}=1;
	return 0;
}


sub validate_eco_campaigns{
# --------------------------------------------------------
# Created on: 09/23/08 @ 15:13:52
# Author: Carlos Haas
# Last Modified on: 09/23/08 @ 15:13:52
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 

	if($in{'send_coupon'}){		   
		my ($sth)	= &Do_SQL("SELECT DATEDIFF('$in{'expiration'}' , '$in{'scheduledate'}')");
		$in{'expiration_days'} = int($sth->fetchrow());
		
		if(!$in{'expiration_days'} or $in{'expiration_days'} < 0){
			++$err;
			$error{'expiration'} = &trans_txt('invalid');
			$va{'message'} .= "<br> Invalid Expiration Day";
		}
		
		if((!$in{'id_promo'} and !$in{'percentage'} and !$in{'maxdiscount'}) or !$in{'minsale'} ){
			++$err;
			$error{'send_coupon'} = &trans_txt('invalid');
		}
		
		$in{'sqlemails'} = filter_values($in{'sqlemails'});
		
	}else{
		$in{'send_coupon'} = 0;
	}
}


sub view_eco_campaigns{
# --------------------------------------------------------
# Created on: 09/23/08 @ 15:13:52
# Author: Carlos Haas
# Last Modified on: 09/23/08 @ 15:13:52
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 

	($in{'send_coupon'} eq '0') and ($in{'send_coupon'} = 'No');
	($in{'send_coupon'} eq '1') and ($in{'send_coupon'} = 'Yes');
}








1;