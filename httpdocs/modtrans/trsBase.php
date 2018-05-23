<?php

//error_reporting(E_ALL);
require("functions.php");
$local = "modtran";

#########################################################
#### INIT System Data
#########################################################
$in = array();
$va = array();
$trs = array();
$usr = array();
$sys = array();
$cfg = array();
$tpl = array();
$cses = array();
$error = array();
$device = array();

## Deteccion de Devices
define('DATE_FORMAT_LONG', '%A %d %B, %Y');

$default_e = 1;
######################################################
##### Configuration File
######################################################
//$cfg_folder = getcwd();
$dir = getcwd();
list($b_cgibin, $a_cgibin) = explode('httpdocs', $dir);
$cfg_folder = $b_cgibin . 'cgi-bin/common/';

/*
if (isset($_COOKIE['e'])) {
    $e = $_COOKIE['e'];
} elseif (isset($_GET['e'])) {
    $e = $_GET['e'];
    setcookie('e', $e);
} elseif (isset($in['e'])) {
    $e = $in['e'];
    setcookie('e', $e);
} else {
    $e = 1;
}

*/
$e=-1;

if (isset($_GET['e'])) {
    $e = $_GET['e'];
    setcookie('e', $e);
} elseif (isset($in['e'])) {
    $e = $in['e'];
    setcookie('e', $e);
} elseif(isset($_COOKIE['e'])) {
    $e = $_COOKIE['e'];
}


//$e = isset($in['e']) ? $in['e'] : isset($_GET['e']) ? $_GET['e'] : $_COOKIE['e'];
//setcookie('e', $e);
//-- set cookie params
//$expire = time()+60*60*24;
//setcookie('e', $e, $expire);
######################################################
##### Load Paths and URLs ############################
######################################################
load_sys_data($e); //Load $sys

if (isset($_COOKIE['sit_lang'])) {
    $usr['pref_language'] = $_COOKIE['sit_lang'];
}
$lang = $usr['pref_language'];
(!$lang) and ($lang = $cfg['default_lang']);

$path_templates = $cfg['path_templates'];
$path_templates = preg_replace("/\[lang\]/", $lang, $path_templates);

$ck_name = $cfg['ckname'];
$sid = "";

$path_sessions = $cfg['auth_dir'];
$in['debug_mode'] = 1;
$va['app_title'] = $cfg['app_title'];


//-- Crea la cookie desde el parametro $_GET para el ID de la sesion
if (isset($_GET['slsid'])) {
    $sid = $_GET['slsid'];
    setcookie($ck_name, $sid);
} elseif (isset($in['slsid'])) {
    $sid = $in['slsid'];
    setcookie($ck_name, $sid);
}

##### Load Data to $in ##############
#####################################
$in['thisurl'] = '';
foreach ($_GET as $key => $value) {
    if (substr(strtolower($key), 0, 4) == "chk:") {
        list ($aux, $name) = split(":", $key);
        $name = str_replace("_", " ", $name);
        if (array_key_exists(strtolower($value), $in)) {
            $in[strtolower($value)] .= "|$name";
        } else {
            $in[strtolower($value)] .= "$name";
        }
    } else {
        $in[strtolower($key)] = $value;
    }
    if (strtolower($key) != 'help') {
        $in['thisurl'] .= strtolower($key) . "=$value&";
    }
}
foreach ($_POST as $key => $value) {
    if (substr(strtolower($key), 0, 4) == "chk:") {
        list ($aux, $name) = split(":", $key);
        $name = str_replace("_", " ", $name);
        if (array_key_exists(strtolower($value), $in)) {
            $in[strtolower($value)] .= "|$name";
        } else {
            $in[strtolower($value)] .= "$name";
        }
    } else {
        $in[strtolower($key)] = $value;
    }
    if (strtolower($key) != 'help') {
        $in['thisurl'] .= strtolower($key) . "=$value&";
    }
}
(!$in['nh']) and ($in['nh'] = 1);

// -------------------------------------------------------------------------
######################################################
##### FUNCTIONS        ############################
######################################################
#// Connect Persistent to DB
if ($cfg['oper_mode'] != 'updating' or $cfg['oper_mode'] == 'closed') {
    (strlen($in['e']) > 1) and ($in['e'] = substr($in['e'], -1));
    if ($in['e'] or $_COOKIE['e']) {
        if ($in['e']) {
            $_COOKIE['e'] = $in['e'];
            setcookie('e', $in['e']);
        }

        $in['e'] = $_COOKIE['e'];
        #echo "DB=".$cfg['emp.'.$in['e'].'.dbi_db']." Host ".$cfg['emp.'.$in['e'].'.dbi_host']."<br>";
        
        //mysql_pconnect ($cfg['emp.'.$in['e'].'.dbi_host'], $cfg['emp.'.$in['e'].'.dbi_user'], $cfg['emp.'.$in['e'].'.dbi_pw']) or die(mysql_error());
        //mysql_select_db ($cfg['emp.'.$in['e'].'.dbi_db']) or die(mysql_error());
        mysql_pconnect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw']) or die(mysql_error());
        mysql_select_db ($cfg['dbi_db']) or die(mysql_error());
        $va['eimg'] = '.e' . $in['e'];
    } else {
        mysql_pconnect ($cfg['dbi_host'], $cfg['dbi_user'], $cfg['dbi_pw']) or die(mysql_error());
        mysql_select_db ($cfg['dbi_db']) or die(mysql_error());
    }
}

function load_sys_data($e = '') {
    global $sys, $cfg, $cfg_folder, $local;

    if (file_exists($cfg_folder . "/general." . $local . ".cfg")) {
        if ($handle = fopen($cfg_folder . "/general." . $local . ".cfg", 'r')) {
            while (!feof($handle)) {
                list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
                if ($type == 'sys') {
                    $sys[$name] = trim($value);
                } elseif ($type == 'conf' or $type == 'conf_local') {
                    $cfg[$name] = trim($value);
                }
            }
        }
    }

    
    if (file_exists($cfg['cfg_dir'] . 'general.e' . $e . '.cfg')) {
        if ($handle = fopen($cfg['cfg_dir'] . 'general.e' . $e . '.cfg', 'r')) {
            while (!feof($handle)) {
                list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
                if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type == 'conf') {
                    $cfg[$name] = trim($value);
                }
            }
        }
    }

    if (file_exists($cfg['cfg_dir'] . 'general.ex.cfg')) {            
        if ($handle = fopen($cfg['cfg_dir'] . 'general.ex.cfg', 'r')) {
            while (!feof($handle)) {
                list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
                if (($name == 'auth_logoff' ) and $type == 'conf') {
                    $cfg[$name] = trim($value);
                }
                
                if (($name == 'gensessiontype' ) and $type == 'conf') {
                    $cfg[$name] = trim($value);
                }                                
            }
        }
    }    
}

function filter_values($input) {
    $output = preg_replace("/\'/", "\\'/", $input);
    return $output;
}

// -------------------------------------------------------------------------
function format_price($num) {
    return ("$ " . number_format($num, 2));
}

// -------------------------------------------------------------------------
function date_to_sql($in_date) {
    global $usr;
    #$months = array ("jan" => array(1,31), "feb" => array(2,28), "mar" => array(3,31), "apr" => array(4,30), "may" => array(5,31), "jun" => array(6,30),
    #              	"jul" => array(7,31), "aug" => array(8,31), "sep" => array(9,30), "oct" => array(10,31), "nov" => array(11,30), "dec" => array(12,31),
    #		  		"ene" => array(1,31), "abr" => array(4,30), "ago" => array(8,31), "dic" => array(12,31));
    #$months = array ("ene" => 1, "feb" => 2, "mar" => 3, "abr" => 4, "may" => 5, "jun" => 6,"jul" => 7, "ago" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dic" =>12);
    #$dmonths = array ("ene" => 31, "feb" => 28, "mar" => 31, "abr" => 30, "may" =>31, "jun" => 30,"jul" => 31, "ago" => 30, "sep" =>30, "oct" =>31, "nov" =>30, "dic" =>31);
    if ($usr['pref_language'] == 'en') {
        $months = array("jan" => 1, "feb" => 2, "mar" => 3, "apr" => 4, "may" => 5, "jun" => 6, "jul" => 7, "aug" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dec" => 12);
        $dmonths = array("jan" => 31, "feb" => 28, "mar" => 31, "apr" => 30, "may" => 31, "jun" => 30, "jul" => 31, "aug" => 30, "sep" => 30, "oct" => 31, "nov" => 30, "dec" => 31);
    } else {
        $months = array("ene" => 1, "feb" => 2, "mar" => 3, "abr" => 4, "may" => 5, "jun" => 6, "jul" => 7, "ago" => 8, "sep" => 9, "oct" => 10, "nov" => 11, "dic" => 12);
        $dmonths = array("ene" => 31, "feb" => 28, "mar" => 31, "abr" => 30, "may" => 31, "jun" => 30, "jul" => 31, "ago" => 30, "sep" => 30, "oct" => 31, "nov" => 30, "dic" => 31);
    }

    $ar = preg_split("/-|\/|:/", $in_date);
    $day = intval($ar[0]);
    $mon = strtolower($ar[1]);
    $year = intval($ar[2]);

    ($year < 100) and ($year += 2000);
    $yy1 = $year / 4;
    $yy2 = intval($year / 4);
    $mon = strtolower($mon);

    // ### Años Viciestos
    if ($yy1 == $yy2) {
        ++$months['feb'];
    }
    // ######## Month ####
    if (!$months[$mon]) {
        return 0;
    }
    // ######## Day ####
    if ($day > $dmonths[$mon]) {
        return 0;
    }
    return ("$year-$months[$mon]-$day");
}

// -------------------------------------------------------------------------
function sql_to_date($date) {
    global $usr;
    if ($usr['pref_language'] == 'en') {
        $months = array('Nul', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
    } else {
        $months = array('Nul', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic');
    }

    list($year, $mon, $day) = split('[/.-]', $date);
    if ($day < 10) {
        $day = "0" . intval($day);
    }
    $mon = intval($mon);
    if ($date) {
        return "$day-$months[$mon]-$year";
    } else {
        return "";
    }
}

// -------------------------------------------------------------------------
function save_auth_data($sid, $sdata) {
    global $path_sessions, $cfg;
    $output = '';
    foreach ($sdata as $key => $value) {
        if ($key != "password" and $key) {
            $value = preg_replace("/\r/", "", $value);
            $value = preg_replace("/\n/", "``", $value);
            $output .= "$key=$value\n";
        }
    }

    if ($cfg['gensessiontype'] == 'mysql') {
        $sth = mysql_query("INSERT INTO admin_sessions SET ses='$sid', Content='" . filter_values($output) . "', CreatedBy=$sdata[id_admin_users], CreatedDateTime=NOW(),ExpDateTime=NOW();");
    } else {
        if ($handle = fopen($path_sessions . $sid, 'w')) {
            fwrite($handle, "$output\n");
            fclose($handle);
        }
    }
}

/*
  function save_auth_data($sid) {
  global $path_sessions, $usr;
  #echo "Saving in $path_sessions$sid<br>";
  if ($handle = fopen($path_sessions . $sid, 'w')) {
  foreach ($usr as $key => $value) {
  if ($key != "password" and $key) {
  $value = preg_replace("/\r/", "", $value);
  $value = preg_replace("/\n/", "``", $value);
  fwrite($handle, "$key=$value\n");
  }
  }
  fclose($handle);
  }
  }
 */

// -------------------------------------------------------------------------

function load_usr_data($sid) {
    global $usr, $cfg, $path_sessions;    
    if ($cfg['gensessiontype'] == 'mysql') {        
        ##print  load_name('admin_sessions','ses',$sid,'Content');

        $ary = preg_split("/\n/", load_name('admin_sessions', 'ses', $sid, 'Content'));
        //print "size:" . sizeof($ary) . "\n\n";
        for ($x = 0; $x < sizeof($ary); $x++) {
            if (preg_match("/([^=]+)=(.*)/", $ary[$x], $matches)) {
                $usr[strtolower($matches[1])] = $matches[2];
            }
        }
        (!$usr['pref_style']) and ($usr['pref_style'] = 'default');
        (!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
        if ($usr['id_admin_users'] > 0) {
            return 'ok';
        } else {
            return 'Please Login';
        }
    } else {
        if (file_exists($path_sessions . $sid)) {
            if ($handle = fopen($path_sessions . $sid, 'r')) {
                while (!feof($handle)) {
                    list($name, $value) = explode('=', fgets($handle), 2);
                    $usr[strtolower($name)] = trim($value);
                }
                (!$usr['pref_style']) and ($usr['pref_style'] = 'default');
                (!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
                return 'ok';
            } else {
                return 'Please Login';
            }
        } else {
            return 'Please Login';
        }
    }
}

/*
  function load_usr_data($sid) {
  global $usr;
  global $path_sessions;
  if (file_exists($path_sessions . $sid)) {
  if ($handle = fopen($path_sessions . $sid, 'r')) {
  while (!feof($handle)) {
  list($name, $value) = explode('=', fgets($handle), 2);
  $usr[strtolower($name)] = trim($value);
  }
  (!$usr['pref_style']) and ($usr['pref_style'] = 'default');
  (!$usr['pref_lang']) and ($usr['pref_lang'] = 'en');
  return 'ok';
  } else {
  return 'Please Login';
  }
  } else {
  return 'Please Login';
  }
  }
 */

// -------------------------------------------------------------------------
function logout($sid) {
    global $ck_name, $path_sessions;
    setcookie($ck_name, '');
    setcookie('sessionid', '');
    setcookie('kp3', '');
    setcookie('gwa', '');
    if (file_exists($path_sessions . $sid)) {
        unlink($path_sessions . $sid);
    }
}

// -------------------------------------------------------------------------
function load_page($fname) {
    global $usr, $cfg;
    (!$usr['pref_language']) and ($usr['pref_language'] = $cfg['default_lang']);
    if (preg_match("/(.*)\/([a-z]*)_(.*)$/", $fname, $matches) and $cfg['path_ns_cgi_' . $matches[2]]) {
        $fname = $matches[1] . "/" . $matches[2] . "/" . $matches[3];
    }
    $fname = preg_replace("/\[lang\]/", $usr['pref_language'], $fname);
    #echo "fname $fname<br>";
    if (file_exists("$fname")) {
        if ($handle = fopen("$fname", 'r')) {
            while (!feof($handle)) {
                $page .= fgets($handle);
            }
            return $page;
        } else {
            return '';
        }
    } else {
        return '';
    }
}

// -------------------------------------------------------------------------
function build_page($tname) {
    global $path_templates, $in, $usr, $va, $error;
    $page = load_page($path_templates . $tname);
    while (preg_match("/\[([^]]+)\]/", $page, $matches) and $num < 99) {
        $field = $matches[1];
        $cmdname = strtolower(substr($field, 3));
        $cmdtype = substr($field, 0, 3);
        if ($cmdtype == 'ck_') {
            $rep_str = $_COOKIE[$cmdname];
        } elseif ($cmdtype == 'in_') {
            $rep_str = $in[$cmdname];
        } elseif ($cmdtype == 'va_') {
            $rep_str = $va[$cmdname];
        } elseif ($cmdtype == 'er_') {
            $rep_str = $error[$cmdname];
        } elseif ($cmdtype == 'ur_') {
            $rep_str = $usr[$cmdname];
        } elseif ($cmdtype == 'ip_') {
            $rep_str = build_page($cmdname . '.html');
        } elseif ($cmdtype == 'fc_') {
            if (function_exists($cmdname)) {
                $rep_str = $cmdname();
            } else {
                $rep_str = '';
            }
        } else {
            $rep_str = '';
        }
        $page = preg_replace("#\[$field\]#i", $rep_str, $page);
        ++$num;
    }
    return $page;
}

// -------------------------------------------------------------------------
function pages_list($this_page, $numhits, $maxhits) {
    global $in;

    if ($numhits == 0) {
        return array('1', '');
    } else {
        ###########################################
        ###### Built Pages Link
        ###########################################
        if (!array_key_exists("nh", $in)) {
            $in['nh'] = 1;
        }

        if ($numhits <= $maxhits) {
            return '1';
        }

        if ($numhits > $maxhits) {
            $next_hit = $in['nh'] + 1;
            $prev_hit = $in['nh'] - 1;

            $left = $in['nh'];
            $right = intval($numhits / $maxhits) - $in['nh'];
            ($left > 7) ? ($lower = $left - 7) : ($lower = 1);
            ($right > 7) ? ($upper = $in['nh'] + 7) : ($upper = intval($numhits / $maxhits) + 1);
            if (7 - $in['nh'] >= 0) {
                $upper = $upper + (8 - $in['nh']);
            }
            if ($in['nh'] > ($numhits / $maxhits - 7)) {
                $lower = $lower - ($in['nh'] - intval($numhits / $maxhits - 7) - 1);
            }
            $output = "";

            if ($in['nh'] > 1) {
                $output .= "<a href='$this_page&nh=$prev_hit'> <<< </a> ";
            }
            for ($i = 1; $i <= intval($numhits / $maxhits) + 1; $i++) {
                if ($i < $lower) {
                    $output .= " ... ";
                    $i = ($lower - 1);
                } else {
                    ($i == $in['nh']) ?
                                    ($output .= "<b>$i</b> ") :
                                    ($output .= "<a href='$this_page&nh=$i'>$i</a> ");
                    if (($i * $maxhits) >= $numhits) {
                        break;
                    }
                }
                if ($i > $upper) {
                    $output .= " ... ";
                    break;
                }
            }
            if ($in['nh'] <= intval($numhits / $maxhits)) {
                $output .= "<a href='$this_page&nh=$next_hit'> >>> </a> ";
            }
        } else {
            $output = "1";
        }
        return $output;
    }
}

// -------------------------------------------------------------------------
function load_cfg($tbl_name) {
    global $db_cols, $db_valid_types, $db_not_null;
    $sth = mysql_query("show tables like '$tbl_name';");
    $ary = mysql_fetch_array($sth);
    if (!$ary[0]) {
        return;
    }
    $db_cols = array();
    $sth = mysql_query("describe $tbl_name;");
    while ($ary = mysql_fetch_array($sth)) {
        #print_r($ary);
        $db_cols[] = $ary[0];
        if ($ary[5] == "auto_increment") {
            $db_valid_types[$ary[0]] = "auto_increment";
            $ary[2] = "YES";
        } elseif (preg_match("/varchar/i", $ary[1])) {
            if ($ary[4] == "email") {
                $db_valid_types[$ary[0]] = "email";
            } else {
                $db_valid_types[$ary[0]] = "alpha";
            }
        } elseif ($ary[1] == "date") {
            $db_valid_types[$ary[0]] = "date";
        } elseif (preg_match("/^int/", $ary[1]) || $ary[1] == "decimal(5,3)") {
            $db_valid_types[$ary[0]] = "numeric";
        } elseif (preg_match("/^dec/", $ary[1])) {
            $db_valid_types[$ary[0]] = "currency";
        } else {
            $db_valid_types[$ary[0]] = "alpha";
        }
        if (!$ary[2] or $ary[2] == 'NO') {
            $db_not_null[$ary[0]] = 1;
        }
    }
    return;
}

// -------------------------------------------------------------------------
function validate_cols($db_cols) {
    global $in, $error;
    $error['return-query'] = '';

    foreach ($db_cols as $col => $value) {
        $lc_col = strtolower($col);
        $val = $in[$lc_col];
        ##### Not Null Check #####
        if (!$val and $value[1]) {
            $error[$lc_col] = trans_txt("required");
            ++$err;
            #echo "$col<br>";
            ##### Valid E-Mail Check #####
        } elseif ($value[0] == "email" and ($val and !check_email_address($val))) {
            $error[$lc_col] = trans_txt("invalid");
            ++$err;
            #echo "$col<br>";
            ##### Valid numeric field Check #####
        } elseif ($value[0] == "numeric" and !is_numeric($val)) {
            $error[$lc_col] = trans_txt("invalid");
            ++$err;
            #echo "$col<br>";
            ##### Valid Date field Check #####
            #}elsif ($db_valid_types[$col] eq "date" and $val !~ /^\s*$/){
            #	if (&date_to_sql($in[$col]) == 0){
            #		$error[$col] = "<span class='error'>Inv lido</span>";
            #		++$err;
            #	}
        }
        $error['return-query'] .= "$col='" . filter_values($val) . "',";
        #echo("$col :  $db_valid_types[$col]  : Req=$db_not_null[$col] : $err : $error[$col] : val=$val : isnull=".is_null($val)."<br>");
    }
    $error['return-query'] = substr($error['return-query'], 0, -1);
    if ($err > 0) {
        $error['return-status'] = 'error';
    } else {
        $error['return-status'] = 'ok';
    }
    return $error;
}

// -------------------------------------------------------------------------
function save_page($fname, $data) {
    if ($handle = fopen($fname, 'w')) {
        fwrite($handle, "$data");
        fclose($handle);
    }
}

// -------------------------------------------------------------------------
function sid_dv($input) {
    $input .= get_ip;
    $lg = strlen($input);
    for ($i = 1; $i <= $lg; $i++) {
        $tot += ord(substr($input, $i, 1)) + ord(substr($input, $i + 1, 1)) - 30 - $i;
    }
    $dv = intval(($tot / 11 - intval($tot / 11)) * 11);
    if ($dv == 10) {
        $dv = 'K';
    }
    return $dv;
}

// -------------------------------------------------------------------------
function get_ip() {
    if (getenv('REMOTE_ADDR')) {
        return getenv('REMOTE_ADDR');
    } elseif (getenv('REMOTE_HOST')) {
        return getenv('REMOTE_HOST');
    } elseif (getenv('HTTP_CLIENT_IP')) {
        return getenv('HTTP_CLIENT_IP');
    } else {
        return "Unknown";
    }
}

function checkip($ipfilter) {
    $ip = get_ip();
    #echo "$ipfilter <br>.. $ip<br><br>";
    $ip1 = preg_split("/\./", $ip, 4);
    $ips = preg_split("/,|\n/", $ipfilter);

    #echo "<br>size".sizeof($ips);
    for ($x = 0; $x < sizeof($ips); $x++) {
        $ips[$x] = preg_replace("/\r/", "", $ips[$x]);
        $ip2 = preg_split("/\./", $ips[$x], 4);
        $ok = 1;
        #echo "<br>cheking: $ips[$x]=?$ip : $x<br>";
        for ($i = 0; $i <= 3; $i++) {
            #echo "&nbsp;&nbsp;&nbsp;&nbsp; $ip1[$i] != $ip2[$i]";
            if ($ip1[$i] != $ip2[$i] and $ip2[$i] != 'x') {
                $ok = 0;
                #echo " : ERR";
            }
            #echo "<br>";
        }
        if ($ok) {
            #echo "IP OKM<br>"; 
            $sth = mysql_query("SELECT COUNT(*) FROM admin_IPlist WHERE Type='Black' AND IP='$ip'");
            $ary = mysql_fetch_array($sth);
            if ($ary[0] > 0) {
                return 0;
            } else {
                return 1;
            }
        }
    }
    return 0;
}

// -------------------------------------------------------------------------
function save_logs($message, $action) {
    global $usr, $in;
    if ($message == 'login' or $message == 'logout') {
        $type = 'Access';
    } else {
        $type = 'Action';
    }
    $sth = mysql_query("INSERT INTO admin_logs SET LogDate=NOW(),LogTime=NOW(),Logcmd='$in[cmd]',Type='$type',Message='$message',Action='" . filter_values($action) . "',ID_admin_users='$usr[id_admin_users]',IP='" . get_ip() . "'");
}

// -------------------------------------------------------------------------
#function save_voxchgs($action){
#	global $usr,$db;
#	$result = $db->query("INSERT INTO vxd_changes SET Date=NOW(),Time=NOW(),Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]'");
#	#echo "INSERT INTO vox_changes SET Date=NOW(),Time=NOW(),Action='".filter_values($action)."',ID_admin_users='$usr[id_admin_users]'";
#}
// -------------------------------------------------------------------------
function nsmail($from, $to, $subject, $body, $html) {
    $headers = "From: $from <$from>\n";
    $headers .= "MIME-Version: 1.0\CRLF\n";
    ##; charset=iso-8859-9
    if ($html) {
        $headers .= "Content-type: text/html\n";
    }
    $headers .= "Reply-To: Comerciototal <$from>\n";
    $headers .= "X-Priority: 1\n";
    $headers .= "X-MSmail-Priority: Low\n";
    #$headers .= "Content-type: text/html\n";
    $headers .= "X-mailer: Comerciototal";

    mail(" $to <$to>", $subject, $body, $headers);
}

// -------------------------------------------------------------------------
function check_email_address($email, $dns) {
    // First, we check that there's one @ symbol, and that the lengths are right
    if (!$email) {
        return false;
    }
    if (!ereg("[^@]{1,64}@[^@]{1,255}", $email)) {
        // Email invalid because wrong number of characters in one section, or wrong number of @ symbols.
        return false;
    }
    // Split it into sections to make life easier
    $email_array = explode("@", $email);
    $local_array = explode(".", $email_array[0]);
    for ($i = 0; $i < sizeof($local_array); $i++) {
        if (!ereg("^(([A-Za-z0-9!#$%&'*+/=?^_`{|}~-][A-Za-z0-9!#$%&'*+/=?^_`{|}~\.-]{0,63})|(\"[^(\\|\")]{0,62}\"))$", $local_array[$i])) {
            return false;
        }
    }
    if (!ereg("^\[?[0-9\.]+\]?$", $email_array[1])) { // Check if domain is IP. If not, it should be valid domain name
        $domain_array = explode(".", $email_array[1]);
        if (sizeof($domain_array) < 2) {
            return false; // Not enough parts to domain
        }
        for ($i = 0; $i < sizeof($domain_array); $i++) {
            if (!ereg("^(([A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9])|([A-Za-z0-9]+))$", $domain_array[$i])) {
                return false;
            }
        }
    }
    if ($dns) {
        $dom = explode('@', $email);
        if (checkdnsrr($dom[1] . '.', 'MX'))
            return true;
        if (checkdnsrr($dom[1] . '.', 'A'))
            return true;
        if (checkdnsrr($dom[1] . '.', 'CNAME'))
            return true;
        return false;
    }
    return true;
}

// -------------------------------------------------------------------------
function build_radio($tbl, $field) {
    global $db;
    $result = $db->query("DESCRIBE $tbl $field;");
    $output = '';
    if (!DB::isError($result)) {
        $rec = $result->fetchRow(DB_FETCHMODE_ASSOC);
        $list = preg_split("/','/", substr($rec[1], 6, -2));
        for ($i = 0; $i < sizeof($list); $i++) {
            $output .= "<input type='radio' name='$field' value='$list[$i]' class='checkbox'>$list[$i]\n";
        }
    }
    return $output;
}

// -------------------------------------------------------------------------
#function load_name($tbl,$where,$resp){
#	global $db;
#	$result = $db->query("SELECT * FROM $tbl WHERE $where;");
#	if (!DB::isError($result)) {
#		$rec = $result->fetchRow(DB_FETCHMODE_ASSOC);
#		foreach ($rec as $key=>$value ) {
#			$resp = preg_replace("/\[$key\]/", $value, $resp);
#		}
#		return $resp;
#	}else{
#		return '';
#	}
#}
// -------------------------------------------------------------------------
function trans_txt($to_trans) {
    global $trs;
    global $path_templates;
    if ($trs[$to_trans]) {
        return $trs[$to_trans];
    } else {
        if (file_exists($path_templates . "messages.txt")) {
            if ($handle = fopen($path_templates . "messages.txt", 'r')) {
                while (!feof($handle)) {
                    $ary = explode("=", fgets($handle), 2);
                    $trs[$ary[0]] = trim($ary[1]);
                }
            }
        }
        return $trs[$to_trans];
    }
}

// -------------------------------------------------------------------------
function php_error($sys_err) {
    global $in, $error, $va;
    require('phperror.php');
    exit;
}

// -------------------------------------------------------------------------
#function addrecord($db_name) {
#	global $db,$in, $usr, $db_cols, $db_valid_types;
#	load_cfg($db_name);
#	$query = '';
#	for ($i = 1; $i < sizeof($db_cols)-3; $i++) {
#		$query .= "$db_cols[$i]='" . filter_values($in[strtolower($db_cols[$i])]) . "',";
#	}
#	$query .= "Date=NOW(), Time=NOW(),ID_admin_users='".$usr[id_admin_users]."'";
#	$result = $db->query("INSERT INTO $db_name SET $query");
#	// Always check that $result is not an error
#	if (DB::isError($result)) {
#		return trans_txt("db_error") . $result->getMessage();
#	}else{
#		return 'ok';
#	}
#}


/*
  $local = "modtran";
  if (file_exists($cfg_folder . "/general." . "$local" . ".cfg")) {
  if ($handle = fopen($cfg_folder . "/general." . $local . ".cfg", 'r')) {
  while (!feof($handle)) {
  list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
  if ($type == 'sys') {
  $sys[$name] = trim($value);
  } elseif ($type == 'conf' or $type == 'conf_local') {
  $cfg[$name] = trim($value);
  }
  }
  }
  }



  if (file_exists($cfg['cfg_dir'] . 'general.e' . $e . '.cfg')) {
  if ($handle = fopen($cfg['cfg_dir'] . 'general.e' . $e . '.cfg', 'r')) {
  while (!feof($handle)) {
  list($type, $name, $value) = preg_split("/\||=/", fgets($handle), 3);
  if (($name == 'auth_dir' or $name == 'dbi_db' or $name == 'dbi_host' or $name == 'dbi_pw' or $name == 'dbi_user' or $name == 'app_title') and $type == 'conf') {
  $cfg[$name] = trim($value);
  }
  }
  } else {
  echo "Error al abrir el archivo";
  }
  } else {
  echo "no se encontro";
  }
 */

//setcookie('e', "una_cookie");
//print_r(
//ini_get('session.cookie_lifetime')
//        );        );
?>