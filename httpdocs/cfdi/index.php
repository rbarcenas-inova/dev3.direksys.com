<?php
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
        <script type="text/javascript">
        location.href="<?php echo $ruta; ?>pages/cfdi/cfdi_index.php";
        </script>
    </head>

    <body>
        <div id="contenedor">
            <?php
            include_once 'header_bar.php';
            ?>            
            <div id="spacerx" style="margin: 50px;"></div>
            
            <table width="480px" align="center" >
                <tr>
                    <td align="center">
                        <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_red_on.png');" onclick="location.href='<?php echo $ruta; ?>pages/cfdi/cfdi_index.php'">
                            <div class="txt_button">
                                Listado de Comprobantes Fiscales Digitales
                            </div>
                        </div>
                    </td>
                    <td align="center">
                        <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_green_on.png');" onclick="location.href='<?php echo $ruta; ?>pages/cfdi/cfdi_index.php'">
                            <div class="txt_button">
                                
                            </div>
                        </div>
                    </td>                    
                    <!--
                    <td align="center">
                        <div class="img_button1" style="background: url('<?php echo $ruta; ?>common/img/button_red_blue.png');" onclick="location.href='<?php echo $ruta; ?>pages/warehouse/purchaseorder_recipt.php'">
                            <div class="txt_button">
                                Notas de Cr&eacute;dito
                            </div>
                        </div>
                    </td>
                    -->
                </tr>
            </table>      
                
        </div>
    </body>
</html>