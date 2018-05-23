<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
include_once '../../trsBase.php';
include_once '../../session.php';

$COMMON_PATH = "../..";
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
        <title></title>
        <link href="../../common/css/main.css" rel="stylesheet" type="text/css" />
        <link href="../../common/css/common.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="../../common/js/jquery-1.6.4.min.js"></script>
        <script type="text/javascript">
            
            function toggle_tc(){
                //-- modulo de Retornos -- //
                var sub_module = "Retornos";
                var module_name = $("#spn-mod-name").html(module_name);
                module_name += " > " + sub_module;
                
                $("#spn-mod-name").html(module_name);
                
                $("#returns_types").hide();
                $("#returns_tc_types").show();
                
            }
            
            function toggle_parcial(){
                var sub_module = "Parciales";
                var module_name = $("#spn-mod-name").html(module_name);
                module_name += " > " + sub_module;
                
                $("#spn-mod-name").html(module_name);
                
                $("#returns_types").hide();
                $("#returns_parcial_types").show();
            }
            
            $(document).ready(function(){
                var module_name = "Devoluciones";
                //-- from header_bar.php
                $("#spn-mod-name").html(module_name);
        
            });
        </script>
    </head>
    <body>
        <div id="contenedor">
            <?php include_once '../includes/header_bar.php'; ?>
            <div id="spacerx" style="margin: 50px;"></div>
            <div id="returns_types" style="width: 100%; position: relative; display: block;">
                <table width="640px" align="center" cellspacing="20">
                    <tr>
                        <td align="center">
                            <div id="tc_returns" class="img_button1" style="background: url('../../common/img/button_green_on.png');" onclick="toggle_tc()">
                                <div class="txt_button">
                                    Retornos
                                </div>
                            </div>
                        </td>
                        <td align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_orange_on.png'); cursor: pointer;" onclick="location.href='retornos_cod.php'">
                                <div class="txt_button">
                                    Retornos de C.O.D
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_red_on.png'); cursor: pointer;" onclick="toggle_parcial()">
                                <div class="txt_button">
                                    Parciales
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            <div id="returns_tc_types" style="width: 100%; position: relative; display: none;">
                <table width="640px" align="center" cellspacing="20">
                    <tr>
                        <td align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_blue_on.png');" onclick="location.href='devoluciones.php?return=Refund&action=chg_totales'">
                                <div class="txt_button">
                                    Totales
                                </div>
                            </div>
                        </td>
                        <td align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_red_on.png');" onclick="location.href='devoluciones.php?return=Exchange&action=chg_fisico'">
                                <div class="txt_button">
                                    Cambio F&iacute;sico
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            <div id="returns_parcial_types" style="width: 100%; position: relative; display: none;">
                <table width="640px" align="center" cellspacing="20">
                    <tr>
                        <td align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_blue_on.png');" onclick="location.href='devoluciones.php?return=Refund&action=chg_totales&type=tc'" >
                                <div class="txt_button">
                                    Tarjeta de Credito
                                </div>
                            </div>
                        </td>
                        <td align="center">
                            <div class="img_button1" style="background: url('../../common/img/button_red_on.png');" onclick="location.href='devoluciones.php?return=Refund&action=chg_totales&type=cod'">
                                <div class="txt_button">
                                    C.O.D
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </body>
</html>