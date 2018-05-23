#!/usr/bin/perl
####################################################################
########                  Purchase Orders                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_claims_notes';
	}elsif($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_claims';
	}
}


1;


