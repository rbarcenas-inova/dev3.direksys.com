<?php
#!/usr/bin/php
/**
*			IMPORTANTE: Este archivo es ejecutado por el crond e e2 event_act_e2_invoice_certify}
*           NO BORRAR - EDITAR CON CUIDADO
*           Genera txt para facturación de acuerdo al ID_invoices recibido por POST/GET
*@author	Oscar Maldonado
*           http://om.direksys.com/cfdi/pages/cfdi/cfdi_gen.php?auth=1&e=2&i=12345
*
*   $v_auth==1 => Web | $v_auth==2 => Comando | $v_auth==3 => Web autorefresh | $v_auth==0 
*/
session_start();
$COMMON_PATH = "../..";
include_once $COMMON_PATH . '/trsBase.php';
require_once $COMMON_PATH . '/common/php/class/db/DbHandler.php';
extract($_GET, EXTR_PREFIX_ALL, "v");
extract($_POST, EXTR_PREFIX_ALL, "v");
if(isset($v_e) && $v_e>=1){
    if($v_auth==1){
        $id_invoice=$v_i;
        $exito=Update_Invoice_Status($id_invoice);
    ?>
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title></title>
                <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>
                <link href="<?php echo $COMMON_PATH ?>/common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>        
                <link href="<?php echo $COMMON_PATH ?>/common/js/css/simplemodal.css" type="text/css" rel="stylesheet" media="screen" />
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.ui.datepicker-es.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.simplemodal.1.4.3.min.js"></script>
                <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jpaginate/jquery.paginate.js"></script>		
        		<script>		
        		$(document).ready(function(){	
        			var ajax_url = "../../common/php/signature/layout_cfdi_builder.php";
                    var ID_invoices = "<?php echo $id_invoice;?>";				
                    var E = "<?php echo $v_e;?>";  
        			//if(ID_invoices!=""){
        				$.ajax({
        			      type: 'POST',
        			      url: ajax_url,
        			      data: {
        			          id_invoice : ID_invoices,
                              e : E
        			      }
        			      
        			      ,success: function(data){   	  
        					alert(data); 	  	                               
        			      }
        			      
        			  	});	
        			//}
        		});
        		</script>
        	</head>
        </html>
    <?php 
    }elseif($v_auth==2){
        #ESTA ES LA OPCIÓN QUE SE EJECUTA CON EL CRON AUTOMATICO.
        $exito=Update_Invoice_Status($id_invoice);
        echo header("location: ../../common/php/signature/layout_cfdi_builder.php?e=".$v_e."&id_invoice=".$id_invoice."&exchange=".$v_exchange);
    }elseif($v_auth==3){
        #$timerefresh=300; //segundos
        $timerefresh=120;
        $exito=Update_Invoice_Status($id_invoice);
        $url=$_SERVER['REQUEST_URI'];        
        header("Refresh: $timerefresh; URL=$url");
        echo "Timbrado autom&aacutetico de facturas para la empresa ".$v_e."<br/>";
        echo "Ejecuci&oacuten cada $timerefresh segs. - &Uacuteltima ejecuci&oacuten a las: ".date('H:i:s').' hrs.';
        echo "<br/><br/>"."<a href='cfdi_gen.php?auth=0'>[Detener Proceso]</a>";
        if($v_exchange){
            echo "<br/><br/>".update_exchagerate(1)."<a href='cfdi_gen.php?auth=3&e=".$v_e."&exchange=0'>[Desactivar ExchangeRate]</a>";
        }else{echo "<br/><br/>"."<a href='cfdi_gen.php?auth=3&e=".$v_e."&exchange=1'>[Activar ExchangeRate]</a>";}
    ?>
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title></title>
            <link href="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>
            <link href="<?php echo $COMMON_PATH ?>/common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>        
            <link href="<?php echo $COMMON_PATH ?>/common/js/css/simplemodal.css" type="text/css" rel="stylesheet" media="screen" />
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-1.6.4.min.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery-ui.min.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.ui.datepicker-es.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.msgbox.min.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/validaciones.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jquery.simplemodal.1.4.3.min.js"></script>
            <script type="text/javascript" src="<?php echo $COMMON_PATH ?>/common/js/jpaginate/jquery.paginate.js"></script>        
            <script>        
            $(document).ready(function(){   
                var ajax_url = "../../common/php/signature/layout_cfdi_builder.php";
                var ID_invoices = "<?php echo $id_invoice;?>";              
                var E = "<?php echo $v_e;?>";
                    $.ajax({
                      type: 'POST',
                      url: ajax_url,
                      data: {
                          id_invoice : ID_invoices,
                          e : E
                      }
                    }); 
            });
            </script>
        </head>
    </html>
    <?php
    }elseif($v_auth==0){
        echo "Proceso de timbrado autom&aacutetico detenido.";
    }else{echo "Autorizaci&oacuten requerida.";} 
}else{echo "Error - Faltan par&aacutemetros";}

function Update_Invoice_Status($ID_invoice=0){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-07-01
# Description : Cambia el estatus a Confirmed, si ID_invoice=0 se aplica a todo lo 'New'
# Parameters : $ID_invoice = 0
# Last Modified on: 
# Last Modified by:
    //--
    global $User;
    global $Password;
    global $Server;
    global $DataBase;  
    $link=mysql_connect($Server, $User, $Password) or die(mysql_error());
    mysql_select_db($DataBase, $link);
    if($ID_invoice>0){$filter=" and ID_invoices='$ID_invoice'";}
    $sql="update cu_invoices set Status = 'Confirmed' where 1 and Status='New' $filter";
    $con=mysql_query($sql, $link) or die(mysql_error());
    return 1;
}

function get_exchagerate_MXP_USD($auth=false){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-09-12
# Description : Obtiene el tipo de cambio MXP-USD del Diario Oficial de la Federación
# Parameters : $auth = 1
# Last Modified on: 
# Last Modified by:
    if($auth){
        $xml = simplexml_load_file('http://www.dof.gob.mx/indicadores.xml');
        foreach($xml->channel->item as $val){
            if($val->title=='DOLAR'){
                $d=explode('/',$val->valueDate);
                $d[2] = ($d[2]<2000) ? $d[2]+2000 : $d[2];
                $d=implode('-',array_reverse($d));
                $Date_exchange_rate=$d;
                $Exchange_rate=$val->description;   
                $Currency=$val->title;
            }       
        }
        return "$Date_exchange_rate|$Exchange_rate|$Currency";
    }else{return "get_exchagerate_MXP_USD - Acceso no autorizado.";}
}

function update_exchagerate($auth=false){
# --------------------------------------------------------
# Author: Oscar Maldonado
# Created on: 2013-09-12
# Description : Actualiza la tabla sl_exchangerates con los valores de la funcion get_exchagerate_MXP_USD()
# Parameters : $auth = 1
# Last Modified on: 
# Last Modified by:
    if($auth){
        $Link=mysql_connect('172.20.27.78', 'root', 'HjsLIwhglOPqw1278') or die(mysql_error());
        ##TMK
        $Table="direksys2_e2";
        $sql="SELECT * FROM $Table.sl_exchangerates ORDER BY Date_exchange_rate DESC LIMIT 1";
        $con=mysql_query($sql, $Link)or die(mysql_error());
        $row=mysql_fetch_array($con);
        if($row[1]<date('Y-m-d')){
            $er=explode('|',get_exchagerate_MXP_USD(1));
            $sql="INSERT INTO $Table.sl_exchangerates SET 
                    Date_exchange_rate='$er[0]',
                    exchange_rate='$er[1]',
                    Currency='US$',
                    Date=CURDATE(),
                    Time=NOW(),
                    ID_admin_users=1";
            $con=mysql_query($sql, $Link)or die(mysql_error());
        }
        ##MUFAR
        $Table="direksys2_e3";
        $sql="SELECT * FROM $Table.sl_exchangerates ORDER BY Date_exchange_rate DESC LIMIT 1";
        $con=mysql_query($sql, $Link)or die(mysql_error());
        $row=mysql_fetch_array($con);
        if($row[1]<date('Y-m-d')){
            $er=explode('|',get_exchagerate_MXP_USD(1));
            $sql="INSERT INTO $Table.sl_exchangerates SET 
                    Date_exchange_rate='$er[0]',
                    exchange_rate='$er[1]',
                    Currency='US$',
                    Date=CURDATE(),
                    Time=NOW(),
                    ID_admin_users=1";
            $con=mysql_query($sql, $Link)or die(mysql_error());
        } 
        $msj='Exchange Rate actualizado: '.get_exchagerate_MXP_USD(1);
    }else{$msj="update_exchagerate - Acceso no autorizado.";}
    return $msj;
}
?>