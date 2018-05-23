<?php
include_once 'Facturas/autoload.php';

$user_full_name = $usr['firstname'];
$user_full_name .= " " . $usr['lastname'];
if (trim($usr['middlename']) != "") {
    $user_full_name .= " " . $usr['middlename'];
}

?>
<!DOCTYPE html>
<html lang="en"> 
<head>
	<meta charset="utf-8">
	<title></title>
	<link href="common/css/common.css" rel="stylesheet" type="text/css" />
    <link href="common/js/jpaginate/css/style.css" rel="stylesheet" type="text/css" />
    <link href="common/js/jquery.msgbox.css" type="text/css" rel="stylesheet"/>
    <link href="common/js/css/smoothness/jquery-ui-1.8.17.custom.css" type="text/css" rel="stylesheet"/>        
    <link href="common/js/css/simplemodal.css" type="text/css" rel="stylesheet" media="screen" />
	<link href="common/js/msgBox/Styles/msgBoxLight.css" rel="stylesheet" type="text/css">
	<link rel="stylesheet" type="text/css" href="/sitimages/app_bar/mod/Xtyle<?php echo EMPRESA; ?>.css" />
	<link rel="stylesheet" type="text/css" href="/sitimages/default/main.css" />
	<link rel="stylesheet" type="text/css" href="common/css/jquery.dataTables.min.css" />
	<link rel="stylesheet" type="text/css" href="common/js/jquery.msgbox.css">
	<style type="text/css">
		.salaryright { text-align: right; !important}
		.alignright { text-align: right; !important}
		#invoices td {
	    	padding: 0 5px;
	    	vertical-align: middle;
		}

		#invoices thead th:last-child{
		    width: 1px !important;
		}

		#invoices tbody td:last-child img {
		    margin-top: 2px;
		    width: 16px;
		}

		.icons {
    		margin-left: 12px;
		}

		.dataTables_filter,#invoices_length {
		    display: none;
		}
		.column_filter,.global_filter{
		    width: 136px;
		}
		#invoices th:first-child {
		    padding-left: 3px;
		}
		#invoices th {
		    font-size: 12px;
		}
		#invoices [type="checkbox"] {
		    float: left;
		}

		/*.icons > img {
		    float: left;
		}*/
		#invoices td span img {
		  width: 15px;
		  height: auto;
		}
		
		#invoices th img {
		  width: 15px;
		  height: auto;
		}

		.botones {
		    text-align: center;
		}

		.dataTables_empty {
		    height: 20px;
		}
		#invoices tbody td {
		    white-space: nowrap;
		    font-size: 11px;
		}
		.icons {
		    margin: 0 15px 0 0;
		}
		a:link, a:active, a:visited {
		    color: #0071e0;
		    font-family: Arial;
		    font-size: 12px;
		    font-weight: normal;
		    text-decoration: none;
		}
		
		#xml_uuid {
		    text-align: center;
		    text-transform: uppercase;
		    width: 98%;
		}

		.dataTables_processing {
		    background: rgba(255, 255, 255, 0.9) none repeat scroll 0 0 !important;
		    height: 100% !important;
		    left: 0 !important;
		    margin: 0 !important;
		    right: 0 !important;
		    top: 0 !important;
		    text-align: left;
		}

		#invoices_processing > img {
		    width: 20px;
		}
		#invoices th {
		    font-size: 11px;
		}
		.dataTables_processing .cargando {
		    background: yellow none repeat scroll 0 0;
		    border: 2px solid #000;
		    font-weight: bold;
		    left: 0;
		    padding: 10px;
		}
		.w94 {
			width: 94%
		}
		.no-close .ui-dialog-titlebar-close {display: none }
	</style>
</head>
<body>
<div id="fly" >
  <table border="0" cellspacing="0" cellpadding="0" style="background-color:#ffffff;  -moz-border-radius: 0px 0px 10px 10px;border-radius: 0px 0px 10px 10px; position:fixed;top:0px;z-index:90;-moz-box-shadow: 0 0px 10px #bbbbbb;   -webkit-box-shadow: 0 0px 10px #bbbbbb;  box-shadow: 0 0px 10px #bbbbbb; height:40px; min-width:930px;">
    <tr>
      <td width=100% >
        <table border="0" cellspacing="0" cellpadding="0">
          <td valign=middle align=left nowrap>&nbsp; <a href="<?php echo $cfg['admin_url'] . $usr['application']; ?><?php echo "/admin?cmd=home&e=$in[e]"?>"><img src=/sitimages/app_bar/mod/direksysRN.png border=0 height=25px></a></td>
          <td><img src="/sitimages/banderamexico.jpg" border=0></td>
          <td valign=middle align=left nowrap>
            <font class="compania"><?php echo $cfg['app_title']; ?> </font>
            </td>
          <td valign=middle align=left><img src=/sitimages/app_bar/mod/menubgdiv.png></td>
          <td valign=middle align=left nowrap>

            <font class="modulo1">CFDI</font>
            </td>
          <td valign=middle align=left><img src=/sitimages/app_bar/mod/menubgdiv.png></td>
        </table>


      </td>
      <td>

        <table border="0" cellspacing="0" cellpadding="0" align=right style="margin-right:15px;">
          <td valign=bottom nowrap>
          </td>
          <td nowrap>
            Hi <b><?php echo $user_full_name; ?></b><br>
             ID: <?php echo $usr['id_admin_users']; ?> | Ext: <?php echo $usr['extension']; ?>
              
          </td>
          <td width=15px nowrap>&nbsp;&nbsp;<td>
          <td valign=bottom nowrap>
           	    <a href="<?php echo $cfg['admin_url'] . $usr['application']; ?>/admin?cmd=home?e=<?php echo $in['e'] ?>"><img border="0" alt="Home Page" title="Home Page" src="/sitimages/app_bar/mod/ico-home.jpg"></a> 
				<a href="/manuals/"><img border="0" alt="Manuals" title="Manuals" src="/sitimages/app_bar/mod/ico-manuals.jpg"></a> 
				<a href="javascript:logoff()"><img border="0" alt="Logoff" title="Logoff" src="/sitimages/app_bar/mod/ico-exit.jpg"></a>
          </td>
        </table>

      </td>
    </tr>
  </table>
</div>


<div style="height:55px;"></div>


    <div id="submenu1" class="anylinkcsscols">
      <div class="column">
        [fc_header_menucompanies]

        <!-- <img src=[va_imgurl]app_bar/mod/menushadowfin.png> -->

      </div>
    </div>
 
    <div id="submenu2" class="anylinkcsscols">
      <div class="column">
        [fc_header_menumod]

        <!-- <img src=[va_imgurl]app_bar/mod/menushadowfin.png> -->

      </div>
    </div>


    <table border="0" cellspacing="0" cellpadding="0"   width=98% align=center style="background-color: #ffffff; border: 1px solid #dedede; margin-left:1%;margin-right:1%;min-width:930px;">
    <tr>
      <td>

		<div  style="background-color:#ffffff;margin:15px;">




			<table cellspacing="0" cellpadding="0" width=100% border=0 style="margin-bottom:5px;">
			<td align="left" valign="top">

				<table id="advancedSearch" style="width: 900px; padding: 10px; font-weight: bold;display:block; border: 0px solid silver; " border="0" cellpadding="3" cellspacing="0" >
					<tbody>
						<tr>
							<td>
								UUID
							</td>
							<td colspan="5">
								<input type="text" data-type="directo" data-column="5" id="xml_uuid" class="input" placeholder="AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA">
							</td>
						</tr>
						<tr>
							<td>No. Referencia</td>
							<td>
								<input type="text" class="input" data-type="directo" data-column="" placeholder="No. Referencia">
							</td>
							<td>Id Documento</td>
							<td><input   data-type="directo" data-column="1" id="id_document" type="text" class="input" placeholder="Id Documento"></td>
							<td>Id Cliente</td>
							<td><input data-type="directo" data-column="0" id="id_cliente" type="text" class="input" placeholder="Id Cliente"></td>
						</tr>
						<tr id="filter_global">
							<td>Raz&oacute;n Social</td>
							<td colspan="2"><input data-type="directo" data-column="6" id="razon_social" type="text" placeholder="Raz&oacute;n Social" class="input w94">
							<td>RFC Cliente</td>
							<td colspan="2"><input data-type="directo" id="rfc" data-column="5" type="text" class="input w94" placeholder="RFC Cliente"></td>
						</tr>

						<tr id="filter_col4" data-column="3">
							<td>Serie y Folio</td>

							<td colspan="5">
								<input data-column="2" id="serie" type="text" data-type="directo" placeholder="Serie" class="input"> - del
								<input data-type="rango-folio" id="folio1" data-column="3" type="text" placeholder="Folio inicial" class="input"> al 
								<input data-column="3" data-type="rango-folio" id="folio2" type="text" placeholder="Folio final" class="input"></td>
						</tr>
						<tr id="filter_col5" data-column="4">
							<td>Rango de Fecha</td>
							<td colspan="5">
								<input  data-type="rango-fecha" data-column="4" id="date1" type="text" class="input" placeholder="Desde"> - 
								<input data-type="rango-fecha"  data-column="4" id="date2" type="text" class="input" placeholder="Hasta">

							</td>
						</tr>

						<tr id="filter_col2">

							<td>Tipo de Comprobante</td>
							<td><select id="tipo_doc" data-column="8" data-type="directo" name="lstDocType"  class="input" style="width: 145px;">
	                            	<option selected="" value="">--- Todos ---</option>
	                                <option value="ingreso">Factura</option>
	                                <option value="egreso">Nota de Credito</option>
	                                <option value="pago">Pago</option>
	                                <option value="traslado">Traslado</option>
	                            </select></td>
							<td>Estatus</td>
							<td>
								<select id="status_doc" data-column="9" data-type="directo"  class="input" name="lstDocStatus">
	                                <option selected="" value="">--- Todos ---</option>
	                                <option value="New">New</option>
	                                <option value="OnEdition">OnEdition</option>
	                                <option value="Confirmed">Confirmed</option>
	                                <option value="InProcess">InProcess</option>
	                                <option value="Certified">Certified</option>
	                                <option value="Cancelled">Cancelled</option>
	                                <option value="Failed">Failed</option>
	                            </select>
							</td>
							<td colspan="2">
								<input type="button" onclick="resetSearchForm()" class="button_black" value="Limpiar Filtros"  style="float:right" name="">
								
							</td>
						</tr>
					</tbody>
				</table>

	
			</td>
			<td align="right" valign="top">

					<input type="button" onclick="refresh()" value="Recargar" name="" class="button_blue">

					<input type="button" onclick="generarLayoutCFDI()" value="Timbrar Confirmadas" name="" class="button_blue">
				<div class="botones">
				</div>

			</td>
		</table>






			<!-- <div class="error"> Los siguientes XML tienen errores:</div> -->

			<table id="invoices" class="display" cellspacing="0" width="100%" style="border:1px solid black; ">
		        <thead>
		            <tr>
		                <th>
		                	<input type="checkbox" class="checkall" style="">

		                	<img width="24px" height="24px" alt="Descargar PDF Seleccionados" onclick="downloadSelect('pdf')" style="cursor: pointer" src="common/img/download_file.png">
		                	<img width="24px" height="24px" alt="Descargar XML Seleccionados" onclick="downloadSelect('xml')" style="cursor: pointer" src="common/img/zip.png">
		                	Acciones
		                </th>
		                <th>ID</th>
		                <th>Ref</th>
		                <th>Folio</th>
		                <!-- <th>Folio</th> -->
		                <th>Fecha y Hora</th>
		                <th>UUID</th>
		                <!-- <th>RFC</th> -->
		                <th>Nombre o Raz&oacute;n Social</th>
		                <th>Total</th>
		                <th>Documento</th>
		                <th>Estatus</th>
		                <th></th>
		            </tr>
		        </thead>
		 
		        <tfoot>
		           <tr>
		                <th><input type="checkbox" class="checkall">Acciones</th>
		                <th>ID</th>
		                <th>Ref</th>
		                <th>Folio</th>
		                <!-- <th>Serie</th> -->
		                <!-- <th>Folio</th> -->
		                <th>Fecha y Hora</th>
		                <!-- <th>RFC</th> -->
		                <th>Nombre o Raz&oacute;n Social</th>
		                <th>UUID</th>
		                <th>Total</th>
		                <th>Documento</th>
		                <th>Estatus</th>
		                <th></th>
		            </tr>
		        </tfoot>
		    </table>
		</div>

		</div>
	</td>
</table>

		<table border="0" cellspacing="0" cellpadding="0"   width="98%" bgcolor="#000000" align="center"  background=/sitimages/app_bar/mod/botbg.jpg>
		    <tr>
		      <td>
		        <table cellpadding="0" cellspacing="0" width="100%" border="0">
		          <td width="150px">&nbsp;</td>
		          <td valign="top" align="center">
		            <img src="/sitimages/app_bar/mod/logo2.png" border="0" width="160px"> 
		          </td>
		          <td width="150px">&nbsp;</td>
		        </table>
		      </td>
		    </tr>
	   	</table>

	   	<div id="contEditInvoice" style="display: none;" title="Edición de CFDI">
	   			<p>
		   			<span style="display: inline-block; width: 150px;">Método de pago: </span>
		   			<select name="metodopago" id="metodopago" style="max-width: 350px;">
		   				<?php echo build_select_metodo_pago(); ?>
		   			</select>
		   		</p>
	   			<p>
		   			<span style="display: inline-block; width: 150px;">Forma de pago: </span>
		   			<select name="formapago" id="formapago" style="max-width: 350px;">
		   				<?php echo build_select_forma_pago(); ?>
		   			</select>
	   			</p>
	   			<p id="usocfdi_line">
		   			<span style="display: inline-block; width: 150px;">Uso de CFDI: </span>
		   			<select name="usocfdi" id="usocfdi" style="max-width: 350px;">
		   				<?php echo build_select_uso_cfdi(); ?>
		   			</select>
		   		</p>
	   			<div id="div_cfdi_pago">		   			
			   		<p>
			   			<span style="display: inline-block; width: 150px;">Banco: </span>
			   			<input type="text" name="nombre_banco" id="nombre_banco" maxlength="50" style="width: 200px;" />
			   		</p>
			   		<p>
			   			<span style="display: inline-block; width: 150px;">RFC Banco: </span>
			   			<input type="text" name="rfc_banco" id="rfc_banco" maxlength="15" style="width: 200px;" />
			   		</p>
			   		<p>
			   			<span style="display: inline-block; width: 150px;">Número de cuenta: </span>
			   			<input type="text" name="cuenta_banco" id="cuenta_banco" maxlength="30" style="width: 200px;" />
			   		</p>
			   	</div>
	   	</div>






    	<br> 
	</div>
	<script src="common/js/jquery.js"></script>
	<script src="common/js/jquery.mask.min.js"></script>
	<script src="common/js/msgBox/Scripts/jquery.msgBox.js"></script>
	<script src="common/js/jquery.dataTables.min.js"></script>
	<script src="common/js/jquery-ui.min.js"></script>
    <script src="common/js/jquery.ui.datepicker-es.js"></script>
    <script src="common/js/jquery.msgbox.min.js"></script>
    <script src="common/js/js.js"></script>
	<script type="text/javascript">
		config.urlService = '/finkok/Facturas';

		$('#xml_uuid').mask('AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA');

		var refresh = function(){
			$('#invoices').DataTable().search('').draw();
		}
		$('#global_filter,[data-type="directo"],[data-type="rango-folio"],[data-type="rango-fecha"]').each(function(i,el){
				$(el).val('');
		});
		var resetSearchForm = function(){
			$('#global_filter,[data-type="directo"],[data-type="rango-folio"],[data-type="rango-fecha"]').each(function(i,el){
				$(el).val('');
			});
			for (var i =0 ; i < 12; i++) {
		  	  $('#invoices').DataTable().column(i+1).search('');
			};
		  	  $('#invoices').DataTable().search('').draw()
		};
		var cancelInvoice = function(ele){
			var url = config.urlService+'/?action=cancelInvoice&id_invoices='+ele.dataset.id;			
			$.msgBox({
				title:"Pregunta",
				content: "¿Realmente desea Cancelar la siguiente factura: "+ele.dataset.factura+'?<br><textarea id="noteFacturaCancel" placeholder ="Escriba las razones de la cancelación" style="height: 50px; width: 300px;" required></textarea>' ,
				type:"confirm",
				opacity:0.5,
				buttons: [{ value: "Si" }, { value: "No" }],
				success: function (result){
					if(result == "Si"){
						if($('#noteFacturaCancel').val() != ''){
							$.post(url,{nota:$('#noteFacturaCancel').val()}, function(data){
								if(data.code == 200){
									$.msgBox({
		                                type: "info",
		                                title:"Resultado",
		                                content:"Se Cancelo correctamente la factura",
		                                success: function (data) {}
		                            });
								}else{
									$.msgBox({
		                                type: "error",
		                                title:"Error",
		                                content:"Error al procesar Cancelar Factura",
		                                success: function (data) {}
		                            });
								}
							});
						}else{
							$.msgBox({
                                type: "error",
                                title:"Error",
                                content:"Debe de escribir una nota para cancelación de Factura",
                                success: function (data) {}
                            });
						}
					}
				}
			});
		}
		//-----------------------------------------
		// Función para editar el cfdi
		//-----------------------------------------
		var this_invoice = null;
		$('#contEditInvoice').dialog({
			autoOpen: false,
			width: 600,
			modal: false,
			closeOnEscape: false,
			dialogClass: 'no-close',
			open: function(){
				$(this).dialog('option', 'title', 'Edición de CFDI ['+$(this_invoice).data('id')+']');
				
				$('#metodopago').removeAttr('selected');
				$('#metodopago').val($(this_invoice).data('pmethod'));
				$('#formapago').removeAttr('selected');
				$('#formapago').val($(this_invoice).data('ptype'));
				$('#usocfdi').removeAttr('selected');
				$('#usocfdi').val($(this_invoice).data('use'));

				$('#nombre_banco').val($(this_invoice).data('cusbank'));
				$('#rfc_banco').val($(this_invoice).data('cusfcode_bank'));
				$('#cuenta_banco').val($(this_invoice).data('cusaccount_number'));

				if( $(this_invoice).data('doctype') == 'Pago' ){
					$('#div_cfdi_pago').css('display', 'inline-block');
					$('#usocfdi_line').css('display', 'none');
				} else {
					$('#div_cfdi_pago').css('display', 'none');
					$('#usocfdi_line').css('display', 'inline-block');
				}
			},
			buttons:{
				'Aceptar': function(){
					var url = config.urlService+'/?action=editInvoice&id_invoices='+this_invoice.dataset.id;

					if($('#metodopago').val() != '' && $('#formapago').val() != '' && $('#usocfdi').val() != ''){
						$.post(url,
							{
								metodopago:$('#metodopago').val(),
								formapago:$('#formapago').val(),
								usocfdi:$('#usocfdi').val(),
								banco:$('#nombre_banco').val(),
								rfc_banco:$('#rfc_banco').val(),
								cuenta_banco:$('#cuenta_banco').val(),
							}, 
							function(data){
								$('#contEditInvoice').dialog('close');
								if(data.code == 200){
									$.msgBox({
		                                type: "info",
		                                title:"Resultado",
		                                content:"La Factura se modificó correctamente",
		                                success: function (data) {
		                                	refresh();
		                                }
		                            });
								}else{
									$.msgBox({
		                                type: "error",
		                                title:"Error",
		                                content:"Error al procesar la modificación de la Factura",
		                                success: function (data) {}
		                            });
								}
							}
						);
					}else{
						$.msgBox({
                            type: "error",
                            title:"Error",
                            content:"Debe completar todos los cambios para editar la Factura",
                            success: function (data) {}
                        });
					}
				},
				'Cancelar': function(){
					$(this).dialog('close');
				}
			}
		});
		var editInvoice = function(ele){
			this_invoice = ele;
			$('#contEditInvoice').dialog('open');
			return;			
		}

		// Cambia el status del invoice
		var changeStatus = function(ele){
			var url = config.urlService+'/?action=changeStatus&id_invoices='+ele.dataset.id+'&chg_status=New';

			$.post(url,null, 
				function(data){
					if(data.code == 200){
						$.msgBox({
                            type: "info",
                            title:"Resultado",
                            content:"La Factura se modificó correctamente",
                            success: function (data) {
                            	refresh();
                            }
                        });
					}else{
						$.msgBox({
                            type: "error",
                            title:"Error",
                            content:"Error: "+data.response,
                            success: function (data) {}
                        });
					}
				}
			);			
		}


        function generarLayoutCFDI(){
                $.msgBox({
                    title: "Pregunta",
                    content: "¿Desea enviar a timbrar todas las facturas Confirmadas?",
                    type: "confirm",
                    opacity: 0.5,
                    buttons: [{ value: "Si" }, { value: "No" }],
                    success: function (result) {
                        if(result == "Si"){

                        	$.post(config.urlService+'/?action=all', {}, function(data, textStatus, xhr) {

                                if(data.code == '200'){                                
                                    $.msgBox({
                                        type: "info",
                                        title:"Resultado",

                                        content:"Se han enviado a timbrar Correctamente.",
                                        success: function (data) {}

                                    });
                                }else{
                                    $.msgBox({
                                        type: "error",
                                        title:"Error",

                                        content:"Error al procesar la peticion.",
                                        success: function (data) {}

                                    });
                                }                                
							});
                        }
                    }                
                });               
            }
		
		function filterGlobal () {
		    $('#invoices').DataTable().search(
		        $('#global_filter').val(),
		        $('#global_regex').prop('checked'),
		        $('#global_smart').prop('checked')
		    ).draw();
		}
		function filterColumn ( i,value) {
		    $('#invoices').DataTable().column( i ).search(value).draw();
		}
		$(document).ready(function() {
			var dates = $( "#date1,#date2" ).datepicker({
                dateFormat: 'yy-mm-dd',
                setDate: new Date(),
                defaultDate: new Date(),
                changeMonth: true,
                numberOfMonths: 3
            });


			var typingTimer;              
			var doneTypingInterval = 500;
			var $input = $('input[data-type="directo"]');
			var current = null;
			$input.on('keyup', function () {
			  clearTimeout(typingTimer);
			  current = $(this);
			  typingTimer = setTimeout(doneTyping, doneTypingInterval);
			});


			$input.on('keydown', function () {
			  clearTimeout(typingTimer);
			});

			function doneTyping () {
				console.log(current.data('column'));
				console.log(current.val());
				filterColumn( current.data('column'), current.val() );
			}
		    $('input#global_filter').on( 'keyup', function () {

		        filterGlobal();
		    });
		 	// $('input[data-type="directo"]').on('keyup',function(){
		 	// 	filterColumn( $(this).data('column'),$(this).val() );
		 	// });
		 	$('select[data-type="directo"]').on('change',function(){
		 		filterColumn( $(this).data('column'),$(this).val() );
		 	});
		    $('[data-type="rango-fecha"]').on('change',function(){
		    	filterColumn($(this).data('column'),($('#date1').val() || '')+'|'+($('#date2').val() || ''));
		    });
		    $('[data-type="rango-folio"]').on('keyup',function(){
		    	filterColumn($(this).data('column'),($('#folio1').val() || '')+'|'+($('#folio2').val() || ''));
		    });
		} );

		$('.checkall').on('click',function(){
			if($(this).prop('checked')){
				$(this).prop('checked','checked');
				$('.checkall,[data-check="s"]').each(function(i,el){
					$(el).prop('checked','checked');
				});
			}else{
				$(this).removeProp('checked');
				$('.checkall,[data-check="s"]').each(function(i,el){
					$(el).removeProp('checked');
				});
			}
		});

		var downloadSelect = function(type){
			var ids = [];
			$('[data-check="s"]:checked').each(function(i,el){
				ids.push(el.dataset.id);
			});
			console.log(ids.join(','));
			if(type == 'xml'){
				window.open(config.urlService+'/?action=downloadXML&id_invoices='+ids.join(','));
			}else if(type == 'pdf'){
				window.open(config.urlService+'/?action=downloadPDF&id_invoices='+ids.join(','));
			}
		}
		ajaxRequests = [];
		abortAll = function() {
		    $(ajaxRequests).each(function(idx, jqXHR) {
		        jqXHR.abort();
		    });
		    ajaxRequests = [];
		};

		$.ajaxSetup({
		    beforeSend: function(jqXHR) {
		    	abortAll();
		        ajaxRequests.push(jqXHR);
		    },
		    complete: function(jqXHR) {
		        var index = ajaxRequests.indexOf(jqXHR);
		        if (index > -1) {
		            ajaxRequests.splice(index, 1);
		        }
		    }
		});
		table = $('#invoices').DataTable( {
	        processing: true,
	        serverSide: true,
	        iDisplayLength: <?php echo $usr['maxhits'] != '' ? $usr['maxhits'] : '50' ?>,
			"oLanguage": { 
      			"sProcessing": "<span class='cargando'>Buscando ...</span>" 
    		},
	        ajax: {
	            "url": "Facturas/invoices_page.php",
	            "type": "POST"
	        },
	        columns: [
	            { "data": "acciones"},
	            { "data": "id" },
	            { "data": "orden" },
	            { "data": "serie_folio" },
	            // { "data": "folio" },
	            { "data": "fecha_hora" },
	            { "data": "uuid" },
	            // { "data": "rfc" },
	            { "data": "razon" },
	            { "data": "total","sClass":"salaryright alignright" },
	            { "data": "tipodoc" },
	            { "data": "status" },
	            { "data": "usuario"}
        	],
        	order: [[ 1, "desc" ]],
        	columnDefs: [ {
	            targets: [ 0, 3, 5, 9 ],
	            orderable: false
	        }]
	    });
	    function editCFDI(id_invoice, page){
	        var url = '/finkok/pages/cfdi/cfdi_edit.php';
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

	    function openModal(content){
	    	$div = $('<div style="position: fixed;width: 40%;height: 350px;z-index: 9999;padding: 20px;background: #fff;top: 10px;left: 0;right: 0;margin: 6% auto;border: 1px solid #ccc;box-shadow: 1px 1px 8px 3px;overflow: auto;"></div>');
	    	$div.attr('id', 'div_modal');
	    	$divContent = $('<div style="overflow:auto;height: 64%;border: 1px solid #ccc;padding: 15px;" ></div>')
	    	$divContent.html(content);
	    	$boton = $('<div style="text-align:center;padding: 10px;"><button>Cerrar</button></div>')
	    	$boton.on('click', function(){
	    		$('#div_modal').remove();
	    	});
	    	$div.append($divContent);
	    	$div.append($boton);
	    	$('body').append($div);

	    }

	    function logoff(){
			if (confirm("Are you sure want to Exit?    ")){
				this.location.href = '/index.php?logoff=1';
			}
		}
	</script>
</body>
</html>
