<?php
session_start();

$COMMON_PATH = "../..";

include_once '../../trsBase.php';
include_once '../../session.php';
include_once 'includes/cfdi_load_list.php';
global $vector_cfdi;
global $total_results;
global $pages;
$page = isset($_POST['pagenum']) ? $_POST['pagenum'] : (isset($_GET['pagenum']) ? $_GET['pagenum'] : 1);

$invoicesDTO = new InvoicesDTO();
$url_ajax_listado = 'ajax/ajax_cfdi_listado.php?pagenum='.$page;
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title></title>
        <link href="<?php echo $COMMON_PATH ?>/common/css/common.css" rel="stylesheet" type="text/css" />
        <link href="<?php echo $COMMON_PATH ?>/common/js/jpaginate/css/style.css" rel="stylesheet" type="text/css" />
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
        <script src="<?php echo $COMMON_PATH ?>/common/js/msgBox/Scripts/jquery.msgBox.js" type="text/javascript"></script>
        <link href="<?php echo $COMMON_PATH ?>/common/js/msgBox/Styles/msgBoxLight.css" rel="stylesheet" type="text/css">

  <link rel="stylesheet" type="text/css" href="/sitimages/app_bar/mod/Xtyle<?php echo $in{'e'}; ?>.css" />
  <link rel="stylesheet" type="text/css" href="/sitimages/default/main.css" />
        <script type="text/javascript">
            $(document).ready(function(){
                $("#popup-customers").hide();
                resetSearchPopUp('resCustomerSearch','customer-table-results');
                buscarParametro();
                /* Fecha txtDocDateIni, txtDocDateLast */
                var t = new Date();
                var today = t.getFullYear() + '-' + (t.getMonth()+1) + '-' + t.getDate();
                $("#txtDocDateLast").val('')
                var dates = $( "#txtDocDateIni,#txtDocDateLast" ).datepicker({
                    dateFormat: 'yy-mm-dd',
                    setDate: new Date(),
                    defaultDate: new Date(),
                    changeMonth: true,
                    numberOfMonths: 3
                });
                /* Fin Fecha */

                $('#QuitaFiltro').click(function() {
                    //location.reload();
                    location.href='cfdi_index.php';
                });
            });
            
            function triggerPopupCustomers(){
                resetSearchPopUp('resCustomerSearch','customer-table-results');
                
                $("#popup-customers").modal({                    
                    position: ['40',]
                });
                
                $("#popup-customers").show();
            }
            
            function resetSearchPopUp(idBtnReset,idTableResults){
                $("#"+ idBtnReset).click();
                $("#"+ idTableResults).html("");
            }
            
 

            function cambiarPaginador(datos){                
                /*if(datos==""){
                    $("#paginador-contenedor").html("");                    
                }else{
                    $("#paginador-contenedor").load("ajax/ajax_paginador.php?pagenum=<?php echo $page; ?>",{'url':'ajax/buscar.php'});
                }*/                
                $("#paginador-contenedor").load("ajax/ajax_paginador.php?pagenum=<?php echo $page; ?>&url=<?php echo $url_ajax_listado ?>",{'url':'<?php echo $url_ajax_listado ?>'});
            }
            
            function generarLayoutCFDI(){
                //-- Guardar los datos de las notas            
                $.msgBox({
                    title: "Pregunta",
                    content: "¿Desea enviar a timbrar todas las facturas Confirmadas?",
                    type: "confirm",
                    opacity: 0.5,
                    buttons: [{ value: "Si" }, { value: "No" }]
                    ,success: function (result) {
                        if(result == "Si"){
                            //-- ajax para modificar el status
                            var ajax_url = '/finkok/common/php/Facturas/?action=all&type=cmd';
                            $.ajax({
                                type: 'POST',
                                url: ajax_url,
                                success: function(data){
                                    console.log(data);                     
                                    if(data.code == '200'){                                
                                        $.msgBox({
                                            type: "info",
                                            title:"Resultado",
                                            content:"Se han enviado a timbrar Correctamente."
                                            ,success: function (data) {location.href="cfdi_index.php";}
                                        });
                                    }else{
                                        $.msgBox({
                                            type: "error",
                                            title:"Error",
                                            content:"Error al procesar la peticion."
                                            ,success: function (data) {location.href="cfdi_index.php";}
                                        });
                                    }                                
                                }
                            });
                        }
                    }                
                });               
            }
            
        </script>
        <script type="text/javascript">
            function buscarParametro(Opc){
                $("#resultados-consulta").html('<div style="width:300px;margin:auto;text-align:center;"><img  src="../../../sitimages/processing.gif" /><br />Cargando...</div>');
                switch (Opc) {
                    case 1:
                       var docStatus = 'New'; 
                       break;
                    case 2:
                       var docStatus = 'Confirmed';
                       break;
                    case 3:
                       var docStatus = 'Certified';
                       var docViewed = 0;
                       break;
                    default:  
                        var idInvoices = $("#txtIdInvoices").val();
                        var idCustomers = $("#txtIdCustomers").val();
                        var nameCustomers = $("#txtNameCustomers").val();
                        var docSerial = $("#txtDocSerial").val();                
                        var docNum = $("#txtDocNum").val();
                        var dateStart = $("#txtDocDateIni").val();
                        var dateEnd = $("#txtDocDateLast").val();
                        var docType = $("#lstDocType").val();
                        var docStatus = $("#lstDocStatus").val();
                        var docUuid= $("#txtUUID").val();
                        var rfc = $("#txtCustomerFiscalCode").val();
                        var idOrders = $("#txtIdOrders").val();             
                }
                $.ajax({
                    type: 'POST',
                    url: '<?php echo $url_ajax_listado ?>',
                    data: {
                        //pagenum: 1,
                        criteria_change: 1,
                        id_invoices : idInvoices,
                        id_customers: idCustomers,
                        name_customers: nameCustomers,
                        customer_fcode : rfc,
                        id_orders : idOrders,
                        doc_serial: docSerial,
                        doc_num: docNum,
                        date_start: dateStart,
                        date_end: dateEnd,
                        doc_type: docType,
                        doc_status: docStatus,
                        uuid: docUuid,
                        doc_viewed : docViewed
                        },
                    success:function(data){
                        $("#resultados-consulta").html(data);
                        cambiarPaginador(data);
                    }
                });
            }

            
            function cambiarPaginador(datos){                
               /* if(datos==""){
                    //$("#paginador-contenedor").html("");
                    $("#paginador-contenedor").load("ajax/ajax_paginador.php?pagenum=1",{'url':'<?php echo $url_ajax_listado ?>'});
                }else{
                    $("#paginador-contenedor").load("ajax/ajax_paginador.php?pagenum=<?php echo $page; ?>&url=<?php echo $url_ajax_listado ?>",{'url':'<?php echo $url_ajax_listado ?>'});
                }*/
                $("#paginador-contenedor").load("ajax/ajax_paginador.php?pagenum=<?php echo $page; ?>&url=<?php echo $url_ajax_listado ?>",{'url':'<?php echo $url_ajax_listado ?>'});
            }
            
            function editCFDI(id_invoice, page){
                var url = 'cfdi_edit.php';
                var data = [];
                data["id_invoice"] = id_invoice;
                data["pagenum"] = page;
                
                postData(url, data);
            }
            
            function postData(url,data){
                var form = $('<form></form>');
                $(form).hide().attr('method','post').attr('action',url);
                for (i in data)
                {
                    var input = $('<input type="hidden" />').attr('name',i).val(data[i]);
                    $(form).append(input);
                }
                $(form).appendTo('body').submit();                
            }

            function loadPopupSerials(){                
                var src = "includes/popup_add_serials.php";
                function setSrc(){
                    $('#iframeid').attr("src", src);
                }

                $.modal('<iframe src="" id="iframeid" width="540" height="270" style="border:0" frameBorder="0">', {
                    opacity:80,
                    overlayCss: {backgroundColor:"#fff"},
                    closeHTML:"",
                    containerCss:{
                        backgroundColor:"#fff",
                        borderColor:"#fff",
                        height:270,
                        width:560,
                        padding:0
                    },
                    overlayClose:true,
                    onShow: function(dialog) {
                        setSrc();
                    }
                });
            }

            function closePopUp()
            {
                $.modal.close();
            }

        </script>
        <script>        
            function SendToCertified(){                   
                $.msgBox({
                    title: "Generando",
                    content: "Espere un momento por favor.",
                    type: "alert",
                    showButtons: false,
                    opacity: 0.5
                    //,autoClose:true
                    ,afterShow: function (data) {  
                        var ajax_url = "cfdi_gen.php";            
                        var E = "<?php echo $in['e'];?>";  
                        $.ajax({
                          type: 'POST',
                          url: ajax_url,
                          data: {
                              e : E,
                            auth : 2
                          }          
                          ,success: function(data){ 
                            console.log(data);   
                            if(data.code){                                
                                if(data.code == 200){ 
                                    $.msgBox({
                                        type: "info",
                                        title:"Resultado",
                                        content:"Se generaron los archivos de los comprobantes para timbrado."
                                        ,success: function (data) {location.href="cfdi_index.php";}
                                    });
                                }else{
                                    $.msgBox({
                                        type: "error",
                                        title:"Error",
                                        content:"Error al generar los archivos."
                                        ,success: function (data) {location.href="cfdi_index.php";}
                                    });
                                }
                            }else{
                                $.msgBox({
                                    type: "error",
                                    title:"Error",
                                    content:"Error al procesar la peticion."
                                    ,success: function (data) {location.href="cfdi_index.php";}
                                });
                            }                                        
                          }
                        });
                    }
                });
            }
        </script>
    </head>
    <body>
        <div id="contenedor">
            <?php
            include_once '../includes/header_bar.php';
            ?>  
            <div id="main-container" class="form-container" style="">
                <?php
                include_once $COMMON_PATH . '/common/php/popup/popup_customers.php';
                ?>      
                    <table border="0" cellspacing="0" cellpadding="0" width="100%" bgcolor="#bbbbbb">
                        <tr  bgcolor="#ffffff">
                            <td  valign=top align=left>
                                <div style="background-color:#ffffff;margin:15px;">    


       
                                    <table style="width: 100%; background-color: #FFFFFF"  >
                                        <!--tr>
                                            <td >                            
                                                <fieldset class="field-set" style="min-width: 450px;">
                                                    <legend>Ver listados</legend>
                                                    <table width="100%">
                                                        <tr>
                                                            <td width="90%">
                                                                <label><a href="#" onclick="buscarParametro()" style="text-decoration:none; color: #555555;">Ver todo</a></label><br>
                                                                <label><a href="/cgi-bin/mod/admin/admin?cmd=repmans&id=14&action=1" target="_blank" style="text-decoration:none; color: #555555;">Listado de Ordenes con estatus de facturaci&oacuten</a></label><br>
                                                                <label><a href="#" onclick="buscarParametro(2)" style="text-decoration:none; color: #555555;">Listos para timbrar</a></label><br>
                                                                <label><a href="#" onclick="buscarParametro(3)" style="text-decoration:none; color: #555555;">Timbrados sin imprimir</a></label><br>
                                                            </td>

                                                        </tr> 
                                                       
                                                    </table>
                                                </fieldset>
                                            </td>
                                        </tr-->

                                        <tr>
                                            <td>    <br>                        
                                                <fieldset class="field-set" style="min-width: 450px;">
                                                    <legend>Filtro para la B&uacute;squeda</legend>
                                                    <table cellpadding=0 cellspacing="5px">
                                                        <tr>
                                                            <td width="180px"><label>ID del Documento:</label></td>
                                                            <td width="45%">
                                                                <input type="text" name="txtIdInvoices" id="txtIdInvoices" value="" size="10" placeholder="ID Factura"  class="inputs" />
                                                            </td>
                                                        </tr>                                    
                                                        <tr>
                                                            <td><label>ID del Cliente: </label></td>
                                                            <td>
                                                                <input type="text" name="txtIdCustomers" id="txtIdCustomers" value="" size="10" placeholder="ID Cliente"  class="inputs" />&nbsp;&nbsp;<!--<img src="<?php echo $COMMON_PATH ?>/common/img/icsearchsmall.gif" border="0" style="cursor: pointer;" onclick="triggerPopupCustomers()" />-->
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td><label>Razon Social del Cliente: </label></td>
                                                            <td>
                                                                <input type="text" name="txtNameCustomers" id="txtNameCustomers" value="" size="30"  placeholder="Razon social" class="inputs" />&nbsp;&nbsp;<!--<img src="<?php echo $COMMON_PATH ?>/common/img/icsearchsmall.gif" border="0" style="cursor: pointer;" onclick="triggerPopupCustomers()" />-->
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td><label>RFC del Cliente: </label></td>
                                                            <td>
                                                                <input type="text" name="txtCustomerFiscalCode" id="txtCustomerFiscalCode" value="" placeholder="RFC" size="18"  class="inputs" />&nbsp;&nbsp;
                                                            </td>
                                                        </tr>                                
                                                        <tr style="display: none;">
                                                            <td><label>No. Orden de Venta: </label></td>
                                                            <td>
                                                                <input type="text" name="txtIdOrders" id="txtIdOrders" value="" size="10" placeholder="No. de Orden" class="inputs" />&nbsp;&nbsp;
                                                            </td>
                                                        </tr>                                 
                                                        <tr>
                                                            <td><label>Serie y Folio: </label></td>
                                                            <td>
                                                                <input type="text" name="txtDocSerial" id="txtDocSerial" size="6" placeholder="Serie" class="inputs"  autofocus />
                                                                -
                                                                <input type="text" name="txtDocNum" id="txtDocNum" size="10" placeholder="Folio" class="inputs" />
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td><label>Fecha del Documento: </label></td>
                                                            <td>
                                                                <input type="text" name="txtDocDateIni" id="txtDocDateIni" size="10"  placeholder="Desde" class="inputs" />
                                                                &nbsp;
                                                                <input type="text" name="txtDocDateLast" id="txtDocDateLast" size="10"  placeholder="Hasta" class="inputs" />
                                                            </td>
                                                        </tr>                                
                                                        <tr>
                                                            <td><label>Tipo: </label></td>
                                                            <td>
                                                                <select name="lstDocType" id="lstDocType" class="inputs" >
                                                                    <option value="" selected>--- Todos ---</option>
                                                                    <option value="ingreso">Factura</option>
                                                                    <option value="egreso">Nota de Credito</option>
                                                                </select>                                        
                                                            </td>
                                                        </tr> 
                                                        <tr>
                                                            <td><label>Estatus: </label></td>
                                                            <td>
                                                                <select name="lstDocStatus" id="lstDocStatus" class="inputs" >
                                                                    <option value="" selected>--- Todos ---</option>                                            
                                                                    <option value="New">Nuevo</option>
                                                                    <option value="OnEdition">En Edici&oacuten</option>
                                                                    <option value="Confirmed">Confirmada para Facturar</option>
                                                                    <option value="InProcess">En Proceso de Timbrado</option>
                                                                    <option value="Certified">Timbrada</option>
                                                                    <option value="Cancelled">Cancelada</option>
                                                                    <option value="Failed">Error de Timbrado</option>
                                                                    <option value="Void">Error en Datos</option>                                                
                                                                </select>                                                                                
                                                            </td>
                                                        </tr> 
                                                        <tr style="display: none;">
                                                            <td><label>UUID del SAT: </label></td>
                                                            <td>
                                                                <input type="text" name="txtUUID" id="txtUUID"  class="text-box" size="60" />
                                                            </td>
                                                        </tr> 
                                                        <tr>
                                                            <td></td>
                                                            <td align="left" >
                                                                <input type="button" name="" value="Aplicar Filtro"  class="button" onclick="buscarParametro()"/>
                                                                &nbsp;
                                                                &nbsp;
                                                                <input type="button" id="QuitaFiltro" value="Quitar Filtro"  class="button" />
                                                            </td> 
                                                            <!-- temporal --> 
                                                            <td colspan="2" align="right" style="width: 40%">
                                                                <?php if($in['e']==2 || $in['e']==4 || $in['e']==12){?>
                                                                <input type="button" name="" value="Timbrar Confirmadas"  class="button" onclick="generarLayoutCFDI()"/>
                                                                <input type="button" name="" value="Timbrar Todo lo Nuevo"  class="button" onclick="SendToCertified()"/>
                                                                <?php }else{?>
                                                                <input type="button" name="" value="Timbrar Confirmadas"  class="button" onclick="generarLayoutCFDI()"/>
                                                                <?php }?>
                                                            </td>                                    
                                                            <!-- temporal -->
                                                        </tr>
                                                    </table>
                                                </fieldset>
                                            </td>
                                        </tr>
                                    </table>

                                    <br>
                                    <div style="width: 100%" id="resultados-consulta"></div>
                                    <br>
                                    <div id="paginador-contenedor"></div>


                                </div>
                            </td>
                        </tr>
                    </table>
            </div>


            <?php
            include_once '../includes/footer.php';
            ?>  
 
        </div>
    </body>
</html>
