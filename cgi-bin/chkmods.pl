#!/usr/bin/perl

@modules = ("### Asterisk",
			"use Asterisk::Manager;",
			"### DBs",
			"use DBI;",
			"use DBIx::Connector;",
			"use DBD::mysql;",
			"### LWP",
			"use LWP::UserAgent ;",
			"use HTTP::Request;",
			"use HTTP::Request::Common;",
			"use HTTP::Response;",
			"use HTTP::Headers;",
			"use URI::Escape; ",
			"use Data::Dumper;",
			"use Switch;",
			"use LWP::Debug qw( + ); ",
			"### File Handling",
			"use FileHandle; ",
			"use File::Copy;",
			"## Varios",
			"use Data::Dumper;",
			"use HTML::Entities;",
			"use Cwd;",
			"use Benchmark;",
			"use HTTP::Cookies;",
			"use CGI qw/:standard :html3/;",
			"### Excel",
			"use Spreadsheet::WriteExcel;",
			"### Emails",
			"use MIME::Base64;",
			"use Mail::IMAPClient;",
			"use Email::MIME;",
			"### Passwords",
			"use Digest::Perl::MD5 'md5_hex';",
			"use Digest::SHA1;",
			"### Barcode & Images",
			"use GD;",
			"use Barcode::Code128;",
			"use constant;",
			"use Image::Magick;",
			"### Certegy",
			"use HTTP::Request::Common qw(POST);",
			"use HTML::Form;",
			"use LWP::UserAgent;",
			"use Switch;",
			"### Twilio",
			"use WWW::Twilio::API;",
			"use XML::Simple;",
			"use Data::Dumper;");

	for my $i (0..$#modules){
		if ($modules[$i] =~ /#/){
			print "\n\nChecking Modules for : $modules[$i]\n";
		}else{
			print "    Loading : $modules[$i]";
			eval $modules[$i] ;
			if ($@){
				print "\n";
				print $@;
				if ($@ =~ /Magick/){
					print `apt-get -y install perlmagick`;
				}
				eval $modules[$i] ;
				if ($@){
					print "    Unable to load : $modules[$i]\n";
					exit;
				}
			}else{
				print "  OK\n";
			}
		}
	}
			
	print "\n\ndone! Everything seems to be OK\n\n";
	
	##
	#Image/Magick.pm    apt-get install perlmagick
	
1;