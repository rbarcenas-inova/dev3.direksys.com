<?php
/*
########## SMS Sender ##########
By: Alejandro Diaz García
Date: 2017/12/14
########## SMS Sender ##########
*/

// Use the Config on general files
global $cfg;
require("nsAdmBase.php");
require("functions.php");

// Require the bundled autoload file - the path may need to change
// based on where you downloaded and unzipped the SDK
//require 'libs/twilio/Twilio/autoload.php';
require __DIR__ . '/service/vendor/autoload.php';

// Use the REST API Client to make requests to the Twilio REST API
use Twilio\Rest\Client;

// Your Account SID and Auth Token from twilio.com/console
$sid = $cfg['twilio_accountsid'];
$token = $cfg['twilio_authtoken'];
$from = $cfg['twilio_from'];

$client = new Client($sid, $token);
// Use the client to do fun stuff like send text messages!
$client->messages->create(
    // the number you'd like to send the message to
    // '+525576100011',
    $in['recipient'],
    array(
        // A Twilio phone number you purchased at twilio.com/console
        // 'from' => '+15594008692',
        'from' => $from,
        // the body of the text message you'd like to send
        // 'body' => "Hey Bob! Good luck on the exam!"
        'body' => urldecode($in['message'])
    )
);

if ($in['print_succes']) {
    echo "1";
}