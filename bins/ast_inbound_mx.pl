#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
#use DBI;
#use DBD::mysql;


# Load the form information and set the config file and userid.
#local(%in) = &parse_form;
#local($sid,%error,%va,%trs,%perm);
#$in{'sid'} ? ($sid   = $in{'sid'}): ($sid   = '');

# Required Librariers
# --------------------------------------------------------
eval {

};

if ($@) { &cgierr ("Error loading required libraries",100,$@); }
eval { &main; };
if ($@) { &cgierr("Fatal error",101,$@); }

exit;

sub main {
# --------------------------------------------------------
        $|++;
        #&connect_db;


        use Net::Telnet ();
        $tn = new Net::Telnet (Port => 5038,
                      Prompt => '/.*[\$%#>] $/',
                      Output_record_separator => '',
                      Errmode    => 'return'
                     );
        $tn->open("127.0.0.1");
        $tn->waitfor('/0\n$/');                  
        $tn->print("Action: Login\nUsername: direksys\nSecret: Shewgd87623\n\n");

        #print $tn->getlines(All=>1) ."\n";
        $tn->waitfor('/Authentication accept*/');

print "\n\nlogged in\n";

        ## Test 2  OK
        #$tn->print("Action: ExtensionState\nContext: default\nExten: 204\nActionID: $sid\n\n");
        #$tn->waitfor('/Response: Success\n/');
        while (1){
                ($line) = $tn->waitfor('/.*\n\n/');
                &proc_cmd($line.$tn->lastline);
        }
        $tn->print("Action: Logoff\n\n");
        print "\n\nConnection closed\n\n";

}

sub proc_cmd {
# --------------------------------------------------------
        my ($lines) = @_;
        my (@ary) = split(/\n/,$lines);
        my (%cmds,@c,$tmp,$pline,$retcode);

        for (0..$#ary){
                @c = split(/: /,$ary[$_]);
                $cmds{$c[0]} = $c[1]; 
        }

        #print "\n$lines\n\n" if ($lines !~ /Event: VarSet/ and $lines !~ /Event: Newexten/);

        ### Call hungUp
        if ($cmds{'Event'} eq 'Hangup'){
                $pline .= "\n pline('You HungUp your extension') ;\n";
                print "\n Call Hangup\n\n";
                $retcode = "hungup";
        }elsif ($cmds{'Event'} eq 'Newchannel' and $cmds{'State'} eq 'Ring'){
                print "\n Extension Ringing;\n";
                $retcode = "ring";
        }elsif ($cmds{'Event'} eq 'Newstate' and $cmds{'ChannelStateDesc'} eq 'Up'){
                #print $cmds{'ConnectedLineNum'} . ":".length($cmds{'ConnectedLineNum'})."\n";
                if (length($cmds{'ConnectedLineNum'}) == 4){
                        print "OK is an xtension \n";

                #print "\n\n$line\n\n";
                #foreach $key (keys %cmds){
                #       print "$key : $cmds{$key}\n";
                #}
                        print "\ncall Answered by : $cmds{'ConnectedLineNum'} $cmds{'CallerIDNum'} Device: $cmds{'CallerIDName'} eq 'device'  From $cmds{'ConnectedLineNum'}\n\n";
                        $retcode = "answered";
        $exten = $cmds{'ConnectedLineNum'};
        $cid = $cmds{'CallerIDNum'};
        $cdid = 9999;

        ## Check for Image
        use LWP::UserAgent;
        my ($results);
        my ($ua) = new LWP::UserAgent;
        $ua->timeout(10);
        $ua->agent("Mozilla/8.0"); # pretend we are very capable browser
        my ($req) = new HTTP::Request 'GET' => "http://172.20.27.84:8001/?extension=$exten&callerid=$cid&did=$cdid";
        $req->header('Accept' => 'text/html');

        # send request
        $res = $ua->request($req);

        # check the outcome
        if ($res->is_success) {
                $results = $res->content;
                print "$results\n";
        }else{
                print "error\n";
        }



                }

        #}elsif ($cmds{'Event'} eq 'Status'){
        #       foreach $key (keys %cmds){
        #               print "$key : $cmds{$key}\n";
        #       }
        }

        #### Campaign Answered
        if ($cmds{'Event'} eq 'Link' and $cmds{'Channel2'} =~ /$usr{'extension'}/){
                print "$cmds{'Uniqueid1'} \n";
                #my ($sth) = &Do_SQL("SELECT * FROM ccd_campaigns_log WHERE uniqueid='$cmds{'Uniqueid1'}';");
                $tmp = $sth->fetchrow_hashref;
                if ($tmp->{'ID_campaigns'}>0){
                        ##|AppData| = |rg-group|20|GROUP-CAMP1|204-200-224-230|
                        #my ($sth) = &Do_SQL("UPDATE ccd_campaigns_log SET ID_admin_users='$usr{'id_admin_users'}', Channel1='$cmds{'Channel1'}',Channel2='$usr{'extension'}' WHERE ID_campaigns_log='$tmp->{'ID_campaigns_log'}';");
                        $pline .= "\n pline('New Call $tmp->{'ID_campaigns'}');\n";
                        $pline .= qq|\n runcamp($tmp->{'ID_campaigns'},$cmds{'CallerID1'});\n|;
                }
        }
        #### Campaign Hungup
        if ($cmds{'Event'} eq 'Unlink' and $cmds{'Channel2'} =~ /$usr{'extension'}/){
                #my ($sth) = &Do_SQL("SELECT * FROM ccd_campaigns_log WHERE uniqueid='$cmds{'Uniqueid1'}';");
                #$tmp = $sth->fetchrow_hashref;
                #if ($tmp->{'ID_campaigns'}>0){
                        $pline .= "\n pline('Call Ended $tmp->{'ID_campaigns'}');\n";
                #}
        }

        if ($cmds{'Application'} eq 'Dial'){
                if ($cmds{'AppData'} =~ /([^\|]+)\|/){
                        $cmds{'AppData'} = $1;
                }
                if ($cmds{'Channel'} =~ /([^-]+)-/){
                        $cmds{'Channel'} = $1;
                }
                #print "<span class='smalltext'>$cmds{'Channel'} --> $cmds{'AppData'}</span>\n";
                if ($cmds{'AppData'} =~ /$usr{'extension'}/){
                        $pline .= "\n pline('Ext Ringing $usr{'extension'}');\n";
                }
        }
        if ($pline){
                #print qq|\n$pline\n|;
        }
        return $retcode;
}



sub cgierr {
# --------------------------------------------------------
        my (@data) = @_;
        print "\n\n\n CGIERR\n";
        print "0: $data[0]\n";
        print "1: $data[1]\n";
        print "2: $data[2]\n";
        print "3: $data[3]\n";
        exit;
}

1;