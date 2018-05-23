#!/usr/bin/perl
#####################################################################
########                   Carriers	      		    #########
#####################################################################
sub load_tabsconf {
	if ($in{'tab'} eq 1){
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_carriers_notes';
	}elsif($in{'tab'} eq 2){
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_carriers';
	}
}
1;