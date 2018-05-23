#!/usr/bin/perl
####################################################################
########             CUSTOMERS                  ########
####################################################################

# Last Modified on: 07/15/08  13:02:41
# Last Modified by: Roberto Barcenas
# Last Modified Desc: empty notes were fixed

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_inorders_notes';
	}elsif($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_inorders';
	}
}

1;
