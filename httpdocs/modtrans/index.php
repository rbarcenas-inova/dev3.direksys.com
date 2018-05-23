<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
include_once 'trsBase.php';
include_once 'session.php';
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
        <title></title>
        <link href="common/css/main.css" rel="stylesheet" type="text/css" />
        <link href="common/css/common.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="common/js/jquery-1.6.4.min.js"></script>
    </head>

    <body>
        <div id="contenedor">
            <?php
            include_once 'header_bar.php';
            ?>
            <div id="spacerx" style="margin: 50px;"></div>
            <table width="480px" align="center">
                <tr>
                    <td align="center">
                        <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_blue_on.png');" onclick="location.href='<?php echo $ruta; ?>pages/devoluciones/index.php'">
                            <div class="txt_button">
                                Devoluciones
                            </div>
                        </div>
                    </td>
                    <td align="center">
                        <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_red_on.png');" onclick="location.href='<?php echo $ruta; ?>pages/warehouse/purchaseorder_recipt.php'">
                            <div class="txt_button">
                                Recepci&oacute;n de Mercancia
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" align="center" style="padding-top: 15px;">
                           <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_orange_on.png');" onclick="location.href='<?php echo $ruta; ?>pages/orders/index.php'">
                            <div class="txt_button">
                                Ordenes de Venta
                            </div>
                        </div>                     
                    </td>
                </tr>
            </table>      
                
        </div>
    </body>
</html>