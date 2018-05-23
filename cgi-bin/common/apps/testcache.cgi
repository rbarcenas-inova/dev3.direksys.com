#!/usr/bin/perl

use Cache::Memcached;
my $cache =  new Cache::Memcached {
    #'servers' => ['127.0.0.1:11211'],
    'servers' => ['172.16.1.39:11211'],
 };

# Get the value from Memcached
my $value = $cache->get("test");


print "Content-type: text/html\n\n";

if(!$value){

	print "Key Not saved before, saving it: ";
	# Save (set) something in your cache:
	$value = "test123";
	$cache->set("test", $value);


}else{

	print "Key saved before: ";

}


print $value;

1;