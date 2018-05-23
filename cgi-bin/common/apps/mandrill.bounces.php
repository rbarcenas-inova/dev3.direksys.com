<?php

    $dir = getcwd();
    list($b_cgibin,$a_cgibin) = strpos( $dir, 'httpdocs' ) !== false ?
        explode('httpdocs',$dir) :
        explode('cgi-bin/',$dir);
    $cfg_folder = $b_cgibin.'cgi-bin/common/';

    #########################################################
    #### INIT System Data
    #########################################################
    $in  = array();
    $va  = array();
    $usr = array();
    $sys = array();
    $cfg = array();
    $mysqli;
    $dbPort;

    // Var Data
    //load_in_data();

    (!$in['nh']) and ($in['nh']=1);
    (!isset($in['e']) or intval($in['e']) <= 0) and ($in['e']=2); #($in['e']=$cfg['def_e']);
    $in['e'] = intval($in['e']);

    // Sys Data
    load_sys_data();

    // DB Connection
    dbConnect();

    // Parse the POST to json
    $data = json_decode($_POST['mandrill_events'], true);

    // Debug file
    $log_file = $cfg['path_logtxt'] . 'mandrill_bounces.' . date('Ymd') . '.log';
    file_put_contents($log_file, print_r($data, true), FILE_APPEND | LOCK_EX );

    $time = time();

    if (is_array($data)) {

        foreach ($data as $bounce){

            $type = trim($bounce['event']);
            $problem_email = trim($bounce['msg']['email']);
            $problem_desc = trim($bounce['msg']['bounce_description']);
            $from_email = trim($bounce['msg']['sender']);


            // Validate email
            #if(!filter_var($problem_email, FILTER_VALIDATE_EMAIL)) exit;

            if($type == 'hard_bounce' || $type == 'soft_bounce' || $type == 'reject'){

                // Searching ID_orders
                $qo = "SELECT ID_orders, ID_customers FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE email = '". mysqli_real_escape_string($mysqli, $problem_email) ."' ORDER BY ID_orders DESC LIMIT 1;";
                $rid = mysqli_query($mysqli, $qo);
                list($id_orders,$id_customers) = mysql_fetch_row($rid);
                $id_orders = (int)$id_orders;
                $id_customers = (int)$id_customers;

                // Trying to insert (email filed is unique)
                $qp = "INSERT IGNORE cu_emails_blacklist SET email = '".mysqli_real_escape_string($mysqli, $problem_email)."', event = '". mysqli_real_escape_string($mysqli, $type) ."', description = '". mysqli_real_escape_string($mysqli, $problem_desc) ."', soft_bounce = 0, bounce = 0, ID_orders = '".$id_orders."', Date = CURDATE(), TIME = CURTIME(), ID_admin_users = 1;";
                $rp = mysqli_query($mysqli, $qp);

                // Update database
                $modquery = ($type == 'soft_bounce' || $type == 'reject') ? " soft_bounce = (soft_bounce+1) " : " bounce = '1' ";
                $q = "UPDATE cu_emails_blacklist SET ". $modquery .", event = '". mysqli_real_escape_string($mysqli, $type) ."', description = '". mysqli_real_escape_string($mysqli, $problem_desc) ."', ID_orders = IF($id_orders > 0,$id_orders,ID_orders), Date = CURDATE(), TIME = CURTIME()  WHERE email = '".mysqli_real_escape_string($mysqli, $problem_email)."';";
                $r = mysqli_query($mysqli, $q);

                if ($r){

                    //check if recipient has soft bounced 3 times
                    if($type == 'soft_bounce'){

                        $q = "UPDATE cu_emails_blacklist SET bounce = IF(soft_bounce >= 3,1,0) WHERE email = '".mysqli_real_escape_string($mysqli, $problem_email)."';";
                        $r = mysqli_query($mysqli, $q);
                        if($r){}

                    }
                }

                if ($id_orders > 0 and $type == 'hard_bounce'){
                    
                    // Add Notes to Order
                    $q = "INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='Email Invalido ".mysqli_real_escape_string($mysqli, $problem_email).":".mysqli_real_escape_string($mysqli, $problem_desc)."', Type='Low',ID_orders_notes_types=1, Date=CURDATE(), Time=CURTIME(), ID_admin_users='1'";
                    mysqli_query($mysqli, $q);

                    // Email is marked
                    $q = "UPDATE sl_customers SET Email=CONCAT('invalid::',Email) WHERE ID_customers='$id_customers'";
                    mysqli_query($mysqli, $q);
                
                }
            }

            ## AD Debug
            // $qp = "INSERT INTO cu_emails_blacklist_debug SET email = '".mysqli_real_escape_string($mysqli, $problem_email)."', event = '". mysqli_real_escape_string($mysqli, $type) ."', description = '". mysqli_real_escape_string($mysqli, $problem_desc) ."', soft_bounce = 0, bounce = 0, ID_orders = '".$id_orders."', Date = CURDATE(), TIME = CURTIME(), ID_admin_users = 1;";
            // $rp = mysqli_query($mysqli, $qp);

        }

    }

    //Reparamos registros pasados
    $qp = "SELECT ID_emails_blacklist, email FROM cu_emails_blacklist WHERE ID_orders = 0 ORDER BY ID_emails_blacklist DESC LIMIT 50;";
    echo "$qp<br><br>";
    $r1 = mysqli_query($mysqli, $qp);

    while(list($id,$email) = mysqli_fetch_row($r1)){

        // Searching ID_orders
        $qo = "SELECT ID_orders FROM sl_customers INNER JOIN sl_orders USING(ID_customers) WHERE email = '". mysqli_real_escape_string($mysqli, $email) ."' ORDER BY ID_orders DESC LIMIT 1;";
        echo "$qo<br>";
        $rid = mysqli_query($mysqli, $qo);
        list($id_orders) = mysqli_fetch_row($rid);

        $qf = "UPDATE cu_emails_blacklist SET ID_orders = IF($id_orders > 0,$id_orders,ID_orders) WHERE ID_emails_blacklist = '$id';";
        echo "$qf<br>";
        if ($id_orders > 0){
            mysqli_query($mysqli, $qf);
        }

    }


    if(get_magic_quotes_gpc()){
      $json = stripslashes($_POST['mandrill_events']);
    }else{
      $json = $_POST['mandrill_events'];
    }

    $data = json_decode($json, true);
    


/****************************************************************************
 *
 *
 *
 *
 *                      FUNCIONES DE USO
 *
 *
 *
 *
 * 
 *****************************************************************************/


    function dbConnect() { //Connect to database

        // Access global variables
        global $cfg, $in, $mysqli, $dbPort;

        $dbHost = $cfg['emp.'.$in['e'].'.dbi_host'];
        $dbUser = $cfg['emp.'.$in['e'].'.dbi_user'];
        $dbPass = $cfg['emp.'.$in['e'].'.dbi_pw'];
        $dbName = $cfg['emp.'.$in['e'].'.dbi_db'];

        // Attempt to connect to database server
        #echo "$dbHost, $dbUser, $dbPass, $dbName";
        if(isset($dbPort)) $mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName, $dbPort);
        else $mysqli = new mysqli($dbHost, $dbUser, $dbPass, $dbName);

        // If connection failed...
        if ($mysqli->connect_error) {
            fail();
        }

        global $charset; mysqli_set_charset($mysqli, isset($charset) ? $charset : "utf8");
        return $mysqli;

    }

    //Database connection fails
    function fail() { 
    
        print 'Database error';
        exit;
    }

    // Load CFG Data
    function load_sys_data() {

        global $sys, $cfg, $cfg_folder;
        
    #   echo $cfg_folder."/general.ex.cfg";
        if (file_exists($cfg_folder."/general.ex.cfg")){
            if ($handle = fopen($cfg_folder."/general.ex.cfg",'r')){
                #echo "file OK<br>";
                while (!feof($handle)) {
                    @list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
                    if ($type=='sys'){
                        $sys[$name]=trim($value);
                        #echo "$name = $value <br>";
                    }elseif ($type=='conf' or $type=='conf_local'){
                        $cfg[$name]=trim($value);
                        #echo "$name = $value <br>";
                    }
                }
                $max_e = $cfg['max_e'];
                $def_e = $cfg['def_e'];
            }else
                echo "no lee el file";
        }
        #php_error("$max_e  $def_e ");

        for ($i = 1; $i <= $cfg['max_e']; $i++) {
            if (file_exists($cfg_folder .'general.e'.$i.'.cfg')) {
                if ($handle = fopen($cfg_folder .'general.e'.$i.'.cfg','r')){
                    #print $cfg_folder .'general.e'.$i.'.cfg';
                    while (!feof($handle)) {
                        @list($type,$name,$value) = preg_split("/\||=/", fgets($handle),3);
                        #print "$type $name,$value<br>";
                        if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type=='conf'){
                            $cfg['emp.'.$i.'.'.$name]= trim($value);
                        }
                        if ($type=='sys' and $i == $cfg['def_e']){
                            $sys[$name]=trim($value);
                        }elseif (($type=='conf' or $type=='conf_local') and $i == $cfg['def_e']){
                            $cfg[$name]=trim($value);
                        }
                    }
                }
            }
        }
    }


    // Load Var Data
    function load_in_data() {

        global $in;

        foreach ($_GET as $key=>$value ) {
            if (substr(strtolower($key), 0,4)=="chk:"){
                list ($aux,$name) = explode(":",$key);
                $name = str_replace("_"," ",$name);
                if (array_key_exists(strtolower($value), $in)){
                    $in[strtolower($value)] .= "|$name";
                }else{
                    $in[strtolower($value)] .= "$name";
                }
            }else{
                $in[strtolower($key)] = $value;
            }
            if (strtolower($key) != 'help'){
                $in['thisurl'] .= strtolower($key)."=$value&";
            }
        }

        foreach ($_POST as $key=>$value ) {
            if (substr(strtolower($key), 0,4)=="chk:"){
                list ($aux,$name) = explode(":",$key);
                $name = str_replace("_"," ",$name);
                if (array_key_exists(strtolower($value), $in)){
                    $in[strtolower($value)] .= "|$name";
                }else{
                    $in[strtolower($value)] .= "$name";
                }
            }else{
                $in[strtolower($key)] = $value;
            }
            if (strtolower($key) != 'help'){
                $in['thisurl'] .= strtolower($key)."=$value&";
            }
        }

    }


?>