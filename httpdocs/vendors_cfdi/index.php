<?php
include_once 'Facturas/autoload.php';

$user_full_name = $usr['firstname'];
$user_full_name .= " " . $usr['lastname'];
$user_full_name .= (trim($usr['middlename']) != "")?" " . $usr['middlename']:"";

?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="iso-8859-1">
	<title>Consulta de CFDI de Proveedores :: Direksys</title>
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
		#invoices td {
	    	padding: 0 5px;
	    	vertical-align: middle;
		}
		#invoices td:nth-child(8){
			text-align: left;
		}

		#invoices tbody td:last-child {
		    text-align: center;
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

		a.grid_icons{
			height: 20px;
			width: 20px;
			cursor: pointer;
			margin: 2px 0px 0px 1px;
		}
		a.grid_icons img{
			height: 20px;
			width: 20px;
		}
		a.grid_link{
			font-weight: bold;
		}
		a.grid_link:hover{
			text-decoration: underline;
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

		.botones {
		    text-align: center;
		}

		.dataTables_empty {
		    height: 20px;
		}
		#invoices tbody td {
		    white-space: nowrap;
		}
		#invoices tbody td:nth-child(7) {
			white-space: normal;
		}
		#invoices tbody td:nth-child(8) {
		    /*white-space: nowrap;*/
		    text-align: right;
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

		.dataTables_processing .cargando {
		    background: yellow none repeat scroll 0 0;
		    border: 2px solid #000;
		    font-weight: bold;
		    left: 0;
		    padding: 10px;
		}
		#invoices td:nth-child(8) {
		    text-align: left;
		    white-space: normal;
		}
		.w94 {
			width: 94%
		}
		.w70 {
			width: 70%
		}
	</style>
	<script src="common/js/jquery.js"></script>
	<script src="common/js/jquery.mask.min.js"></script>
	<script src="common/js/msgBox/Scripts/jquery.msgBox.js"></script>
	<script src="common/js/jquery.dataTables.min.js"></script>
	<script src="common/js/jquery-ui.min.js"></script>
    <script src="common/js/jquery.ui.datepicker-es.js"></script>
    <script src="common/js/jquery.msgbox.min.js"></script>
    <script src="common/js/js.js"></script>
</head>
<body>
	<div id="fly" >
	  <table border="0" cellspacing="0" cellpadding="0" style="background-color:#ffffff;  -moz-border-radius: 0px 0px 10px 10px;border-radius: 0px 0px 10px 10px; position:fixed;top:0px;z-index:90;-moz-box-shadow: 0 0px 10px #bbbbbb;   -webkit-box-shadow: 0 0px 10px #bbbbbb;  box-shadow: 0 0px 10px #bbbbbb; height:40px; min-width:930px;">
	    <tr>
	      <td width=100% >
	        <table border="0" cellspacing="0" cellpadding="0">
	          <td valign=middle align=left nowrap>&nbsp; <a href='/'><img src=/sitimages/app_bar/mod/direksysRN.png border=0 height=25px></a></td>
	          <td><img src="/sitimages/banderamexico.jpg" border=0></td>
	          <td valign=middle align=left nowrap>
	            <font class="compania"><?php echo $cfg['app_title']; ?> </font>
	            </td>
	          <td valign=middle align=left><img src=/sitimages/app_bar/mod/menubgdiv.png></td>
	          <td valign=middle align=left nowrap>

	            <font class="modulo1">Vendors CFDI</font>
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
	           	    <a href="<?php echo $cfg['admin_url'] . $usr['application']; ?>/admin?cmd=home"><img border="0" alt="Home Page" title="Home Page" src="/sitimages/app_bar/mod/ico-home.jpg"></a> 
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
      <div class="column">[fc_header_menucompanies]</div>
    </div>
 
    <div id="submenu2" class="anylinkcsscols">
      <div class="column">[fc_header_menumod]</div>
    </div>

    <table border="0" cellspacing="0" cellpadding="0" width="98%" align=center style="background-color: #ffffff; border: 1px solid #dedede; margin-left:1%;margin-right:1%;min-width:930px;">
	    <tr>
	    	<td>
				<div style="background-color:#ffffff;margin:15px;">
					<fieldset>
						<legend>Filtros de b&uacute;squeda</legend>
						
						<form action="" name="frmFiltros" id="frmFiltros" method="post">
						<table id="advancedSearch" style="padding: 10px; font-weight: bold; border: 0px solid silver;" width="100%" border="0" cellpadding="1" cellspacing="0" >
							<tbody>
								<tr>
									<td>UUID : </td>
									<td colspan="2">
										<input type="text" data-type="directo_global" data-column="10" id="xml_uuid" name="xml_uuid" class="input" placeholder="AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA">
									</td>									
									<td style="text-align: right;">Folio de Recepci&oacute;n : &nbsp;<input data-type="directo" data-column="1" id="id_document" name="id_document" type="text" class="input" placeholder="Folio"></td>
									<td style="text-align: right;">ID Bill : &nbsp;<input data-type="directo" data-column="1" id="id_bills" name="id_bills" type="text" class="input" placeholder="Bill"></td>
									<td style="width: 150px;">&nbsp;</td>
								</tr>
								<tr>			
									<td>RFC : &nbsp; </td>
									<td><input data-type="directo" id="rfc" data-column="5" type="text" class="input" name="rfc" placeholder="RFC Proveedor"></td>
									<td style="text-align: right;" colspan="3" nowrap>Raz&oacute;n Social : &nbsp;<input data-type="directo" data-column="6" id="razon_social" name="razon_social" type="text" placeholder="Raz&oacute;n Social Proveedor" class="input w70">
									<td style="width: 150px;">&nbsp;</td>
								</tr>
								<tr id="filter_col4" data-column="3">
									<td>Serie y Folio : </td>
									<td colspan="5">
										<input data-column="2" id="serie" name="serie" type="text" data-type="directo" placeholder="Serie" class="input"> - 
										<input data-type="rango-folio" id="folio1" name="folio1" data-column="3" type="text" placeholder="Desde el Folio" class="input"> a 
										<input data-column="3" data-type="rango-folio" id="folio2" name="folio2" type="text" placeholder="Hasta el Folio" class="input"></td>
								</tr>
								<tr id="filter_col5" data-column="4">
									<td>Rango de Fecha : </td>
									<td colspan="5">
										<input  data-type="rango-fecha" data-column="4" id="date1" name="date1" type="text" class="input" placeholder="Desde"> - 
										<input data-type="rango-fecha"  data-column="4" id="date2" name="date2" type="text" class="input" placeholder="Hasta">
										<span style="display: inline-block; margin-left: 50px;">Fecha de recepci&oacute;n:</span>
										<input  data-type="rango-fecha" data-column="4" id="date3" name="date3" type="text" class="input" placeholder="Desde"> - 
										<input data-type="rango-fecha"  data-column="4" id="date4" name="date4" type="text" class="input" placeholder="Hasta">
									</td>
								</tr>
								<tr id="filter_col2">
									<td>Tipo : </td>
									<td>
										<select id="tipo_doc" data-column="8" data-type="directo" name="lstDocType"  class="input" style="width: 145px;">
			                            	<option selected="" value="">--- Todos ---</option>
			                                <option value="ingreso">Factura</option>
			                                <option value="egreso">Nota de Credito</option>
			                            </select>
			                       	</td>
									<td style="text-align: left;">Estatus : &nbsp;
										<select id="status_doc" data-column="9" data-type="directo"  class="input" name="lstDocStatus">
			                                <option selected="" value="">--- Todos ---</option>
			                                <option value="Certified">Certified</option>
			                                <option value="Cancelled">Cancelled</option>
			                                <option value="Failed">Void</option>
			                            </select>
									</td>
									<td colspan="2" styel="text-align: right;">
										<input type="button" class="button_blue" value="Exportar" id="btnExportarCSV" style="float:right" name="">								
									</td>
									<td>
										<input type="button" onclick="resetSearchForm()" class="button_black" value="Limpiar Filtros"  style="float:right" name="">								
									</td>
								</tr>
							</tbody>
						</table>
						</form>
					</fieldset>
					<br/>
					<table id="invoices" class="display" cellspacing="0" width="100%" style="border:1px solid black; ">
				        <thead>
				            <tr>
				                <th nowrap>
				                	<input type="checkbox" class="checkall" style="">
				                	<img width="24px" height="24px" alt="Descargar PDF Seleccionados" onclick="downloadSelect('pdf')" style="cursor: pointer" src="common/img/download_file.png" title="Descargar PDF Seleccionados">
				                	<img width="24px" height="24px" alt="Descargar XML Seleccionados" onclick="downloadSelect('xml')" style="cursor: pointer" src="common/img/zip.png" title="Descargar XML Seleccionados">
				                	Acciones
				                </th>
				                <th nowrap>ID</th>
				                <th nowrap>Serie</th>
				                <th nowrap>Folio</th>
				                <th nowrap>Fecha y Hora</th>
				                <th nowrap>RFC</th>
				                <th nowrap>Nombre o Raz&oacute;n Social</th>
				                <th nowrap>Total</th>
				                <th nowrap>Tipo</th>
				                <th nowrap>Estatus</th>
				                <th nowrap>F. Recepci&oacute;n</th>
				            </tr>
				        </thead>
				        <tfoot>
				           <tr>
				                <th><input type="checkbox" class="checkall">Acciones</th>
				                <th>ID</th>
				                <th>Serie</th>
				                <th>Folio</th>
				                <th>Fecha y Hora</th>
				                <th>RFC</th>
				                <th>Nombre o Raz&oacute;n Social</th>
				                <th>Total</th>
				                <th>Tipo</th>
				                <th>Estatus</th>
				                <th>F. Recepci&oacute;n</th>
				            </tr>
				        </tfoot>
				    </table>
				</div>
			</td>
		</tr>
	</table>

	<table border="0" cellspacing="0" cellpadding="0" width="98%" bgcolor="#000000" align="center"  background="/sitimages/app_bar/mod/botbg.jpg">
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
	
	<script type="text/javascript">
		config.urlService = 'Facturas';

		$('#xml_uuid').mask('AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA');

		var refresh = function(){
			$('#invoices').DataTable().search('').draw();
		}
		$('#global_filter,[data-type="directo_global"],[data-type="directo"],[data-type="rango-folio"],[data-type="rango-fecha"]').each(function(i,el){
				$(el).val('');
		});
		var resetSearchForm = function(){
			$('#global_filter,[data-type="directo_global"],[data-type="directo"],[data-type="rango-fecha"]').each(function(i,el){
				$(el).val('');
			});
			for (var i =0 ; i < 12; i++) {
		  		$('#invoices').DataTable().column(i+1).search('').draw()
			};
		  	$('#invoices').DataTable().search('').draw();
		};

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
			var dates = $( "#date1,#date2,#date3,#date4" ).datepicker({
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
				filterColumn( current.data('column'), current.val() );
			}

		    $('input#global_filter').on( 'keyup', function () {
		        filterGlobal();
		    });

		    $('input[data-type="directo_global"]').on('keyup',function(){
		 		$('#invoices').DataTable().search($(this).val()).draw();
		 	});

		 	$('select[data-type="directo"]').on('change',function(){
		 		filterColumn( $(this).data('column'),$(this).val() );
		 	});

		    $('[data-type="rango-fecha"]').on('change',function(){
		    	filterColumn($(this).data('column'),($('#date1').val() || '')+'|'+($('#date2').val() || '')+'|'+($('#date3').val() || '')+'|'+($('#date4').val() || ''));
		    });

		    $('[data-type="rango-folio"]').on('keyup',function(){
		    	filterColumn($(this).data('column'),($('#folio1').val() || '')+'|'+($('#folio2').val() || ''));
		    });

		    $('#btnExportarCSV').click(function(event) {
		    	document.location.href = 'Facturas/invoices_export.php?'+$('#frmFiltros').serialize();
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

		var cancelInvoice = function(ele){
			var url = config.urlService+'/?action=cancelInvoice&id_invoices='+ele.dataset.id;
			$.msgBox({
				title:"Pregunta",
				content: "&#191;Realmente desea Cancelar la siguiente factura: "+ele.dataset.id+'? <br><textarea id="noteFacturaCancel" placeholder ="Escriba las razones de la cancelaci&oacute;n" style="height: 50px; width: 300px;" required></textarea>' ,
				type:"confirm",
				opacity:0.5,
				buttons: [{ value: "Si" }, { value: "No" }],
				success: function (result){
					if(result == "Si"){
						if($('#noteFacturaCancel').val() != ''){
							$.post(url,{nota:$('#noteFacturaCancel').val()}, function(data){
								if(data.code == 200){
									$('#invoices').DataTable().search('').draw();
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
                                content:"Debe de escribir una nota para cancelaci&oacute;n de Factura",
                                success: function (data) {}
                            });
						}
					}
				}
			});
		}

		var viewInvoice = function(ele){
			var url = config.urlService+'/?action=viewInvoice&id_invoices='+ele.dataset.id;
			$.msgBox({
				title:"Pregunta",
				content: "&#191;Realmente desea Cancelar la siguiente factura: "+ele.dataset.id+'? <br><textarea id="noteFacturaCancel" placeholder ="Escriba las razones de la cancelaci&oacute;n" style="height: 50px; width: 300px;" required></textarea>' ,
				type:"confirm",
				opacity:0.5,
				buttons: [{ value: "Si" }, { value: "No" }],
				success: function (result){
					if(result == "Si"){
						if($('#noteFacturaCancel').val() != ''){
							$.post(url,{nota:$('#noteFacturaCancel').val()}, function(data){
								if(data.code == 200){
									$('#invoices').DataTable().search('').draw();
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
                                content:"Debe de escribir una nota para cancelaci&oacute;n de Factura",
                                success: function (data) {}
                            });
						}
					}
				}
			});
		}

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
		    	// abortAll();
		        ajaxRequests.push(jqXHR);
		    },
		    complete: function(jqXHR) {
		        var index = ajaxRequests.indexOf(jqXHR);
		        if (index > -1) {
		            ajaxRequests.splice(index, 1);
		        }
		    }
		});

		var buttonCommon = {
	        exportOptions: {
	            format: {
	                body: function ( data, column, row, node ) {
	                    // Strip $ from salary column to make it numeric
	                    return column === 7 ?
	                        data.replace( /[\$\,]/g, '' ) :
	                        data;
	                }
	            }
	        }
	    };
		
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
	            { "data": "acciones", "width": "12%"},
	            { "data": "id", "width": "6%" },
	            { "data": "serie", "width": "5%" },
	            { "data": "folio", "width": "6%" },
	            { "data": "fecha_hora", "width": "12%" },
	            { "data": "rfc", "width": "10%" },
	            { "data": "razon_social", "width": "20%" },
	            { "data": "total", "width": "10%" },
	            { "data": "tipo", "width": "7%" },
	            { "data": "status", "width": "7%" },
	            { "data": "fh_recep", "width": "6%" },
        	],
        	order: [[ 1, "desc" ]],
        	columnDefs: [ {
	            targets: [ 0, 9 ],
	            orderable: false
	        }],	        
	    });
	    
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


	    function logoff(){
			if (confirm("Are you sure want to Exit?    ")){
				this.location.href = '/index.php?logoff=1';
			}
		}
	</script>
</body>
</html>
