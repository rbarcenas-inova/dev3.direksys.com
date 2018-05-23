
var ordersPayments = {
	updateField : function(fieldName){
		$('[name="'+fieldName+'"]').each( (index, element) => {
			element.value = this.data(fieldName);
		});
	},
	updateElement : function(elementSelector, fieldName){
		$(elementSelector).each( (index, element) => {
			element.value = this.data(fieldName);
			element.innerHTML = this.data(fieldName);
		});
	},
	data : function(index, value, elementUpdate){
		if(!localStorage.getItem('points_peso'))
			localStorage.setItem('points_peso', 0);
		if(!localStorage.getItem('points_value'))
			localStorage.setItem('points_value', 0);

		if(typeof elementUpdate === 'undefined'){
			elementUpdate = false;
		}
		if(typeof index ==='undefined' && typeof value === 'undefined')
			return {
				coupon_applied : localStorage.getItem('coupon_applied'),
				coupon_disc : localStorage.getItem('coupon_disc'),
				coupon_id : localStorage.getItem('coupon_id'),
				current_step : localStorage.getItem('current_step'),
				format_number : localStorage.getItem('format_number'),
				id_salesorigins : localStorage.getItem('id_salesorigins'),
				length : localStorage.getItem('length'),
				order_coupon : localStorage.getItem('order_coupon'),
				order_discount : localStorage.getItem('order_discount'),
				order_pay_type : localStorage.getItem('order_pay_type'),
				order_shipping : localStorage.getItem('order_shipping'),
				order_shp_type : localStorage.getItem('order_shp_type'),
				order_taxes_pct : localStorage.getItem('order_taxes_pct'),
				order_total_net : localStorage.getItem('order_total_net'),
				order_total_pmts : localStorage.getItem('order_total_pmts'),
				pay_type_available : localStorage.getItem('pay_type_available'),
				puntos_disponibles : JSON.parse(localStorage.getItem('puntos_disponibles')),
				shop_cart_items : JSON.parse(localStorage.getItem('shop_cart_items')),
				shop_cart_items2 : JSON.parse(localStorage.getItem('shop_cart_items2')),
				step3_complete : localStorage.getItem('step3_complete'),
				points_peso: localStorage.getItem('points_peso'),
				points_value : localStorage.getItem('points_value'),
				order_total : (function(){
					net = parseFloat(localStorage.getItem('order_total_net'));
					shipping = parseFloat(localStorage.getItem('order_shipping'));
					iva = 1 + parseFloat(localStorage.getItem('order_taxes_pct'));
					puntos_peso = parseFloat(localStorage.getItem('points_peso'));
					puntos_value = parseFloat(localStorage.getItem('points_value'));
					discount = parseFloat(localStorage.getItem('order_discount'));
					total = ((net + shipping) * iva) - puntos_peso - puntos_value - discount;
					ftotal = '$ '+ total.toFixed(2);
					return ftotal;

				})(),

			}
		if(typeof index !=='undefined' && typeof value !== 'undefined'){
			localStorage.setItem(index, value);
			if(elementUpdate !== false){
				if(elementUpdate == 1){
					this.updateField(index);
				}else{
					this.updateElement(elementUpdate, index);
				}
			}
			return this;
		}
		if(index)
			if(index == 'puntos_disponibles' || index == 'shop_cart_items' || index == 'shop_cart_items2')
				return JSON.pars(localStorage.getItem(index));
			else if(index == 'order_total'){
				net = parseFloat(localStorage.getItem('order_total_net'));
				shipping = parseFloat(localStorage.getItem('order_shipping'));
				iva = 1 + parseFloat(localStorage.getItem('order_taxes_pct'));
				puntos_peso = parseFloat(localStorage.getItem('points_peso'));
				puntos_value = parseFloat(localStorage.getItem('points_value'));
				total = ((net + shipping) * iva) - puntos_peso - puntos_value ;
				ftotal = '$ '+ total.toFixed(2);
				return ftotal;
			}else
				return localStorage.getItem(index);

	},
	getTotal : function(){
		return this.data.order_total_net
	}
};
$(function() {

	/*
	 * Variables globales del módulo
	 */	
	var submit_ok = false; // Variable que permite la navegación entre los pasos del proceso de la venta
	var submit_toback = false;

	/*
	 * Funcionalidad de la barra de navegación
	 */
	var this_step = $('#step').val() - 1;
	if( this_step >= 2 && this_step <= 5 ){
		$('#step1').removeClass('step_off').addClass('step');
		$('#step2').removeClass('step_off').addClass('step');
		$('#step3').removeClass('step_off').addClass('step');
		$('#step4').removeClass('step_off').addClass('step');
	}
	if( this_step == 6 ){
		/*$('#step1').removeClass('step').addClass('step_off');
		$('#step2').removeClass('step').addClass('step_off');
		$('#step3').removeClass('step').addClass('step_off');
		$('#step4').removeClass('step').addClass('step_off');*/
		$('#step5').removeClass('step_off').addClass('step');
	}
	$('#step'+this_step).removeClass('step_off').addClass('step_on');

	$('.content').on('click', '.step', function(event){
		// Se autoriza el submit entre los pasos del proceso de la venta
		submit_ok = true;

		var step_go = $(this).attr('rel');
		if( step_go == 0 ){
			build_dialog('&#191;Esta seguro de cancelar el proceso actual?', 'confirm');
			dialog_form.dialog({
				buttons: {
					'Aceptar': function(){						
						location.href = '/cgi-bin/mod/sales/admin?cmd='+$('#cmd').val()+'&step='+step_go;
					},
					'Cancelar': function(){
						$(this).dialog('close');
					}
				}
			});			
		}else{			
			var current_step = parseInt($('#step').val())-1;
			// Si el paso actual es: 3->Direccion o 4->Pago
			// y el paso seleccionado es alguno de los anteriores
			// entonces se deshabilita la validación del formulario actual.			
			$('#step').val(step_go);
			if( step_go < current_step && (current_step == 3 || current_step == 4) ){
				submit_toback = true;
				$('#frm_sales_step'+current_step).submit();				
			}else{
				submit_toback = false;
				$('#frm_sales_step'+current_step).submit();
			}
		}
	});

	/*
	 * Oculta el tooltip inferior
	 */
	if( $('#speech_main').length ){
		$('#lnk_hide_speech').click(function(event) {
			$('#speech_main').hide('50');
			$('#div_speech_icon').show('100');
			return false;
		});

		$('#div_speech_icon').click(function(event) {
			$('#div_speech_icon').hide('fast');
			$('#speech_main').show('10');
			return false;
		});

		if( localStorage.getItem('speech_show') == '0' ){
			$('#lnk_hide_speech').click();
			$('#chk_speech_nevershow').attr('checked', true);
		}

		$('#chk_speech_nevershow').click(function(event) {
			if( $(this).is(':checked') )
				localStorage.setItem('speech_show', 0);
			else
				localStorage.setItem('speech_show', 1);	
		});
	}


	/*
	 * ----------------------------------------------------------------
	 * Step 1 :: Llamada
	 * ----------------------------------------------------------------
	 */
	if( $('#frm_sales_step1').length && ('#submit_start').length ){
		// Reglas de validacion del formulario
		$('#frm_sales_step1').validate({
	        rules:{            
	            phone_cid: { 
	                required: {
	            		depends: function(element) {
	            			if( $('#phone_cid').attr('data-required') == '1' || $('#phone_cid').attr('data-required') == 'true' ){
	            				return true;
	            			}
	            			return false;
	            		}
	            	},
	                digits: true,
	                minlength: 10, 
	            },
	            firstname: {
	            	required: {
	            		depends: function(element) {
	            			if( $('#firstname').attr('data-required') == '1' || $('#firstname').attr('data-required') == 'true' ){
	            				return true;
	            			}
	            			return false;
	            		}
	            	},
	            },
	            zipcode: { 
	                required: true,
	                digits: true,
	                minlength: 5,
	            }
	    	},
	    	messages:{   		
	            phone_cid: {
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',  
	                minlength: '<span class="ValidateError"></span>'  
	            },
	            firstname: '<span class="ValidateError"></span>',
	            zipcode: {
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>'
	            },
	    	},
	    	errorClass: "help-inline",
	    	errorElement: "span",
	    	highlight:function(element, errorClass, validClass) {
	            $(element).parents('.line').removeClass('success').addClass('val_error');
	    	},
	    	unhighlight: function(element, errorClass, validClass) {
	    		$(element).parents('.line').removeClass('val_error').addClass('val_success');
	    	}
	    });

		// Convertir a mayusculas
		$('#firstname').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#lastname1').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#lastname2').blur(function(){ $(this).val($(this).val().toUpperCase()); });

		//-------------------------------------------------
		// Buscador de productos
		//-------------------------------------------------
		$('#div_search_products').dialog({
			autoOpen: false,
		    height: 600,
		    width: 900,
		    modal: true,
		    buttons: {
			    'Cerrar': function(){
			    	$(this).dialog('close');
			    }
		    },
		    open: function(){
		    	$('#txt_search').val('').focus();
		    },
		    beforeClose: function(){
		    	
		    }
		});
		$('#prod_search').click(function(evt){
			if( $('#zipcode').val().length == 5 ){
				$('#div_search_products').dialog('open');
			} else {
				$('#zipcode').focus();
			}
		});
		//-------------------------------------------------

		// Controla el submit del form
	    $('#submit_start').click(function(event) {
			var valida = $('#frm_sales_step1').validate().form();

			// --------------
			// Valida que el folio de la promocion corresponda con el cliente
			// --------------
			var valida_promo = true;
			if( $('#folio_promo').length && valida ){
				if( $('#id_customers').val() != $('#id_customers_promo').val() && $('#id_customers_promo').val() != '' &&  $('#id_customers').val() != '' ){
					valida_promo = false;
					build_dialog('El folio de la promoci&oacute;n aunque es v&aacute;lido, no corresponde con el cliente actual.<br />Por lo tanto no se aplicar&aacute; al proceso que est&aacute; por iniciar.<br /></br />&iquest;Est&aacute; seguro de continuar?', 'confirm');
					dialog_form.dialog({ 
						closeOnEscape: false,
						open: function(event, ui) { 
							$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
						},
						buttons: {
							'Si estoy seguro': function(){
								$('#folio_promo').val('');
								$('#folio_valid').val('0');
								$('#id_customers_promo').val('0');
								if( valida == true ){
									submit_ok = true;
									$('#frm_sales_step1').submit();
								}
							},
							'No, validare los datos': function(){
								$(this).dialog('close');
								return false;
							}
						}
					});
				}
			}
			// --------------

			if( valida == true && valida_promo ){
				submit_ok = true;
				$('#frm_sales_step1').submit();
			}
		});
	}	

	// Busqueda de clientes
	if( $('#phone_cid').length && $('#step').val() == '2' ){
		var this_ajax;
		// Busca al cliente mientras se escribe el núm. telefónico
		$('#phone_cid').keyup(function(event) {
			var search = true;

			if( validate_key(event) ){
				if( $('#firstname').val() != '' && $('#firstname').val().length > 3 )		search = false;
				else if( $('#lastname1').val() != '' && $('#lastname1').val().length > 3 )	search = false;
				else if( $('#lastname2').val() != '' && $('#lastname2').val().length > 3 )	search = false;
				else if( $('#zipcode').val() != '' && $('#zipcode').val().length > 4 )		search = false;

				var this_phone = $(this);
				// Se realiza la búsqueda de clientes usando el número telefónico
				if( this_phone.val().length == 10 && search ){
					search_customer({
						'phone': this_phone.val(),
						'type_sch': 1,
					});
					return false;
				}
			}
		});
		// Busca al cliente cuando el campo(phone) pierde el foco
		$('#phone_cid').blur(function(event) {
			if( !this_ajax ){
				var search = true;

				if( $('#firstname').val() != '' && $('#firstname').val().length > 3 )		search = false;
				else if( $('#lastname1').val() != '' && $('#lastname1').val().length > 3 )	search = false;
				else if( $('#lastname2').val() != '' && $('#lastname2').val().length > 3 )	search = false;
				else if( $('#zipcode').val() != '' && $('#zipcode').val().length > 4 )		search = false;

				var this_phone = $(this);
				// Se realiza la búsqueda de clientes usando el número telefónico
				if( this_phone.val().length == 10 && search ){
					search_customer({
						'phone': this_phone.val(),
						'type_sch': 1,
					});
					return false;
				}
			}
		});
		$('#lnk_search_client').click(function(event) {
			if( this_ajax ){
				this_ajax.abort();
			}
			var search = false;

			if( ($('#firstname').val() != '' && $('#firstname').val().length >= 3) || $('#phone_cid').val().length == 10 )	search = true;
			if( ($('#lastname1').val() != '' || $('#lastname1').val().length >= 3) && !search ) search =  true;
			if( ($('#lastname2').val() != '' && $('#lastname2').val().length >= 3) && !search ) search =  true;
			if( $('#id_customers').val() != '' && $('#id_customers').val().length >= 3 && !search ) search = true;
			if( $('#id_orders').val() != '' && $('#id_orders').val().length >= 6 && !search ) search = true;

			// Se realiza la búsqueda de clientes usando el nombre y los apellidos
			if( search ){
				search_customer({
					'phone': $('#phone_cid').val(),
					'id_customers': $('#id_customers').val(),
					'id_orders': $('#id_orders').val(),
					'firstname': $('#firstname').val(),
					'lastname1': $('#lastname1').val(),
					'lastname2': $('#lastname2').val(),
					'type_sch': 2,
				});
				return false;
			}
		});

		function search_customer(params){
			var this_phone = ( params.phone != undefined ) ? params.phone : '';
			var id_customers = ( params.id_customers != undefined ) ? params.id_customers : '';
			var id_orders = ( params.id_orders != undefined ) ? params.id_orders : '';
			var firstname = ( params.firstname != undefined ) ? params.firstname : '';
			var lastname1 = ( params.lastname1 != undefined ) ? params.lastname1 : '';
			var lastname2 = ( params.lastname2 != undefined ) ? params.lastname2 : '';
			var zipcode = ( params.zipcode != undefined ) ? params.zipcode : '';
			this_ajax = $.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',
				dataType: 'json',
				data: {
					'ajaxbuild': 'sales_search_customers',
					'phone': this_phone,
					'id_customers': id_customers,
					'id_orders': id_orders,
					'firstname': firstname,
					'lastname1': lastname1,
					'lastname2': lastname2,
					'zipcode': zipcode,
					'txt_search': params.txt_search,
				},
				beforeSend: function(){
					$('#div_loading_phone').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative; left: -25px; z-index: 10;">');
				},
				success: function(xresponse){
					$('#div_loading_phone').html('');
					/*
					// Si solo hubo una coincidencia, se muestran los datos directos en los campos
					if( xresponse.matches == 1 && params.type_sch == 1 ){
						if( xresponse.items[0].thisphone.length > $('#phone_cid').val().length ){
							$('#phone_cid').val( xresponse.items[0].thisphone );
						}
						$('#id_customers').val(xresponse.items[0].id_customers);
						$('#firstname').val(xresponse.items[0].firstname);
						$('#lastname1').val(xresponse.items[0].lastname1);
						$('#lastname2').val(xresponse.items[0].lastname2);
						$('#zipcode').val(xresponse.items[0].zipcode);
						$('#address1').val(xresponse.items[0].address1);
						$('#urbanization').val(xresponse.items[0].urbanization);							
						$('#city').val(xresponse.items[0].city);							
						$('#state').val(xresponse.items[0].state);
						$('#last_id_order').val(xresponse.items[0].last_id_order);
						$('#last_date_order').val(xresponse.items[0].last_date_order);
						$('#last_status_order').val(xresponse.items[0].last_status_order);
						$('#div_info_address').css('display', 'block');

						$('#id_customers_reset').css('display', 'inline-block');
						$('#id_customers').attr('readonly', true).removeClass('input').addClass('txt_only_info');
						
					// Si existen varias coincidencias, se muestra un listado para seleccionar alguno
					}else if( xresponse.matches >= 2 || params.type_sch == 2 ){
					*/
					if( xresponse.matches >= 1 ){
						// Se genera el listado con los datos encontrados	
						var html_cust = '';
						html_cust += '<tr>';
						html_cust += '	<th>ID</th>';
						html_cust += '	<th>Nombre</th>';
						html_cust += '	<th>Tel&eacute;fono(s)</th>';
						html_cust += '	<th>CP</th>';
						html_cust += '	<th>Estado</th>';
						html_cust += '	<th>Municipio</th>';
						html_cust += '	<th>Ciudad</th>';
						//html_cust += '	<th>&Uacute;ltima Compra</th>';
						//html_cust += '	<th>Status Pedido</th>';
						html_cust += '</tr>';						
						for( var i = 0; i < xresponse.matches; i++ ){

							var row_span = parseInt(xresponse.items[i].orders_matches);
							var html_row_span = '';
							if( parseInt(row_span) > 0 ){
								row_span += 2;
								html_row_span = 'rowspan="'+row_span+'"';
							}

							html_cust += '<tr>';
							html_cust += '	<td '+html_row_span+'><a href="#" class="lnk_customers" style="color: #0431B4; font-weight: bold;" ';
							html_cust += '			data-cust-id="'+xresponse.items[i].id_customers+'" ';
							html_cust += '			data-cust-firstname="'+xresponse.items[i].firstname+'" ';
							html_cust += '			data-cust-thisphone="'+xresponse.items[i].thisphone+'" ';
							html_cust += '			data-cust-lastname1="'+xresponse.items[i].lastname1+'" ';
							html_cust += '			data-cust-lastname2="'+xresponse.items[i].lastname2+'" ';
							html_cust += '			data-cust-zipcode="'+xresponse.items[i].zipcode+'" ';
							html_cust += '			data-cust-address1="'+xresponse.items[i].address1+'" ';
							html_cust += '			data-cust-urbanization="'+xresponse.items[i].urbanization+'" ';
							html_cust += '			data-cust-city="'+xresponse.items[i].city+'" ';
							html_cust += '			data-cust-state="'+xresponse.items[i].state+'" ';
							html_cust += '			data-last-id-order="'+xresponse.items[i].last_id_order+'" ';
							html_cust += '			data-last-date-order="'+xresponse.items[i].last_date_order+'" ';
							html_cust += '			data-last-status-order="'+xresponse.items[i].last_status_order+'" ';
							html_cust += '		>'+xresponse.items[i].id_customers+'</a></td>';
							html_cust += '	<td '+html_row_span+'>'+xresponse.items[i].firstname+' '+xresponse.items[i].lastname1+' '+xresponse.items[i].lastname2+'</td>';
							html_cust += '	<td '+html_row_span+'>';
							html_cust += '		'+xresponse.items[i].phone1
							if( xresponse.items[i].phone1 != xresponse.items[i].phone2 )
								html_cust += '<p>'+xresponse.items[i].phone2+'</p>'
							if( xresponse.items[i].phone1 != xresponse.items[i].cellphone && xresponse.items[i].phone2 != xresponse.items[i].cellphone )
								html_cust += '<p>'+xresponse.items[i].cellphone+'</p>'
							html_cust += '	</td>';
							html_cust += '	<td '+html_row_span+'>'+xresponse.items[i].zipcode+'</td>';
							html_cust += '	<td>'+xresponse.items[i].state+'</td>';
							html_cust += '	<td>'+xresponse.items[i].city+'</td>';
							html_cust += '	<td>'+xresponse.items[i].urbanization+'</td>';
							//html_cust += '	<td style="text-align: center;">'+xresponse.items[i].last_id_order+'<br />'+xresponse.items[i].last_date_order+'</td>';
							//html_cust += '	<td style="text-align: center;">'+xresponse.items[i].last_status_order+'</td>';
							html_cust += '</tr>';

							//-----------------------------
							// Historial de pedidos
							//-----------------------------
							if( xresponse.items[i].orders_matches > 0 ){
								html_cust += '<tr>';
								html_cust += '	<td colspan="3" style="color: gray; font-weight: bold; text-align: center;">Historial de Compras</td>';
								html_cust += '</tr>';
								for(var i3 = 0; i3 < xresponse.items[i].orders_matches; i3++){
									html_cust += '<tr style="color: gray;">';
									html_cust += '	<td>'+xresponse.items[i].orders[i3].id_order+'</td>';
									html_cust += '	<td>'+xresponse.items[i].orders[i3].date+'</td>';
									html_cust += '	<td>'+xresponse.items[i].orders[i3].status+'</td>';
									html_cust += '</tr>';
								}
							}
							//-----------------------------

						}
						//console.log(html_cust);
						// Se muestra el listado de clientes encontrados
						$('#div_customers_result .table_customers_result').html(html_cust);
						$('#div_customers_result').dialog('open');

						// Selección de un cliente de la lista
						$('.lnk_customers').click(function(event) {
							if( xresponse.items[0].thisphone.length > $('#phone_cid').val().length ){
								$('#phone_cid').val( xresponse.items[0].thisphone );
							}
							$('#id_customers').val( $(this).attr('data-cust-id') );
							$('#firstname').val( $(this).attr('data-cust-firstname') );
							$('#lastname1').val( $(this).attr('data-cust-lastname1') );
							$('#lastname2').val( $(this).attr('data-cust-lastname2') );
							$('#zipcode').val( $(this).attr('data-cust-zipcode') );

							$('#address1').val( $(this).attr('data-cust-address1') );
							$('#urbanization').val( $(this).attr('data-cust-urbanization') );
							$('#city').val( $(this).attr('data-cust-city') );
							$('#state').val( $(this).attr('data-cust-state') );
							$('#last_id_order').val( $(this).attr('data-last-id-order') );
							localStorage.setItem('last_id_order', $(this).attr('data-last-id-order'));
							$('#last_date_order').val( $(this).attr('data-last-date-order') );
							localStorage.setItem('last_date_order', $(this).attr('data-last-date-order'));
							$('#last_status_order').val( $(this).attr('data-last-status-order') );
							localStorage.setItem('last_status_order', $(this).attr('data-last-status-order'));
							$('#div_info_address').css('display', 'block');

							$('#id_customers_reset').css('display', 'inline-block');
							$('#id_customers').attr('readonly', true).removeClass('input').addClass('txt_only_info');						

							$('#div_customers_result').dialog('close');
						});					
					}
					
				}
			});
		}

		// Dialog Customers
		$('#div_customers_result').dialog({
			autoOpen: false,
		    minHeight: 250,
		    maxHeight: 500,
		    width: 880,
		    modal: true,
		    buttons: {
			    'Cerrar': function(){
			    	$(this).dialog( "close" );
			    }
			},
			open: function(){
		    	$(this).siblings('.ui-dialog-buttonpane').find("button:contains('Cerrar')").focus();
		    },
			close: function(){}
		});

		// Elimina los datos del cliente seleccionado
		$('#id_customers_reset').click(function(event) {
			$('#id_customers_reset').hide('blind', 500, function(){
				$('#id_customers').val('');
				$('#id_orders').val('');
				$('#firstname').val('');
				$('#lastname1').val('');
				$('#lastname2').val('');
				$('#zipcode').val('');
				$('#address1').val('');
				$('#urbanization').val('');
				$('#city').val('');
				$('#state').val('');
				$('#last_id_order').val('');
				localStorage.removeItem('last_id_order');
				$('#last_date_order').val('');
				localStorage.removeItem('last_date_order');
				$('#last_status_order').val('');
				localStorage.removeItem('last_status_order');
				$('#id_customers').attr('readonly', false).removeClass('txt_only_info').addClass('input');

				$('#div_info_address').hide('slide', 300);
			});

			$('#firstname').focus();
		});

		if( $('#id_customers').val() != '' && $('#id_customers').val() != '0' ){
			$('#id_customers').attr('readonly', true).removeClass('input').addClass('txt_only_info');
			$('#id_customers_reset').css('display', 'inline-block');
		}
		if( $('#state').val() != '' ){
			$('#div_info_address').css('display', 'block');
			if( $('#address1').val() == '' ){
				$('#address1').attr('readonly', false).removeClass('txt_only_info').addClass('input');
			}
		}

		if( localStorage.getItem('last_id_order') != undefined )	$('#last_id_order').val(localStorage.getItem('last_id_order'));
		if( localStorage.getItem('last_date_order') != undefined )	$('#last_date_order').val(localStorage.getItem('last_date_order'));
		if( localStorage.getItem('last_status_order') != undefined )	$('#last_status_order').val(localStorage.getItem('last_status_order'));

		$('#phone_cid').focus();
	}

	// Validación del Folio de promoción
	if( $('#folio_promo').length && ($('#step').val() == '2' || $('#step').val() == '6') ){

		$('#btn_validate_folio').click(function(event){
			var this_folio = $('#folio_promo').val();
			if( this_folio.length > 0 ){
				// Se obtiene el id del cliente si es que ya fue encontrado en la BD
				// para compararlo con el folio
				var id_customers = ( $('#id_customers').length && $('#id_customers').val().length > 0 ) ? $('#id_customers').val() : 0;

				validate_folio(this_folio, id_customers);
			}

			return false;
		});

		$('#div_promo_info').dialog({
			autoOpen: false,
		    //height: 410,
		    width: 500,
		    modal: true,
		    buttons: {
		    	'Cerrar': function(){
		    		$(this).dialog('close');
		    	}
		    }
		});

		function validate_folio(folio, id_customers){

			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',
				dataType: 'json',
				data: {
					'ajaxbuild': 'sales_validate_folio',
					'folio': folio,
					'id_customers': id_customers,
					'step': $('#step').val(),
				},
				beforeSend: function(){
					$('#div_loading_folio_promo').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative; left: -25px; z-index: 10;">');
				},
				success: function(xresponse){
					if( xresponse.result == 'true' ){

						console.log(xresponse);						
						$('#div_loading_folio_promo').html('<img src="/sitimages/default/b_ok.png" alt="loading" style="margin: auto auto; position: relative; left: -25px; z-index: 10;">');

						if( $('#promos_mow').val() == '1' && typeof xresponse.promo_mow !== 'undefined' ){

							$('#firstname').val( xresponse.promo_mow.values.FirstName );
							$('#lastname1').val( xresponse.promo_mow.values.LastName1 );
							$('#lastname2').val( xresponse.promo_mow.values.LastName2 );
							$('#zipcode').val( xresponse.promo_mow.values.Zip );
							$('#address1').val( xresponse.promo_mow.values.Address1 );
							$('#urbanization').val( xresponse.promo_mow.values.Urbanization );
							$('#city').val( xresponse.promo_mow.values.City );
							$('#state').val( xresponse.promo_mow.values.State );

							$('#div_info_address').css('display', 'block');

							$('#folio_valid').val(xresponse.promo_mow.values.ID_promotions);
							$('#id_customers_promo').val('0');

						} else {
							$('#folio_valid').val(xresponse.id_promotions);
							$('#id_customers_promo').val(xresponse.id_customers);
							$('#div_promo_info').html( xresponse.html_promo );
							$('#div_promo_info').dialog('open');

							// Se cargan los datos del cliente
							if( typeof xresponse.customer !== 'undefined' && $('#step').val() == '2' ){
								$('#phone_cid').val( xresponse.customer.phone1 );
								$('#id_customers').val( xresponse.id_customers );
								$('#firstname').val( xresponse.customer.firstname );
								$('#lastname1').val( xresponse.customer.lastname1 );
								$('#lastname2').val( xresponse.customer.lastname2 );
								$('#zipcode').val( xresponse.customer.zipcode );

								$('#address1').val( xresponse.customer.address1 );
								$('#urbanization').val( xresponse.customer.urbanization );
								$('#city').val( xresponse.customer.city );
								$('#state').val( xresponse.customer.state );
								if( typeof xresponse.customer.last_order !== 'undefined' ){
									$('#last_id_order').val( xresponse.customer.last_order.id_orders );
									localStorage.setItem('last_id_order', xresponse.customer.last_order.id_orders);
									$('#last_date_order').val( xresponse.customer.last_order.date );
									localStorage.setItem('last_date_order', xresponse.customer.last_order.date);
									$('#last_status_order').val( xresponse.customer.last_order.status );
									localStorage.setItem('last_status_order', xresponse.customer.last_order.status);
								}

								$('#div_info_address').css('display', 'block');

								$('#id_customers_reset').css('display', 'inline-block');
								$('#id_customers').attr('readonly', true).removeClass('input').addClass('txt_only_info');
							}
						}

					} else {						
						$('#div_loading_folio_promo').html('');

						build_dialog(xresponse.message, 'error');
						dialog_form.dialog({ 
							closeOnEscape: false,
							open: function(event, ui) { 
								$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
							},
							buttons: {
								'Aceptar': function(){
									$(this).dialog('close');
								}
							},
							close: function(){								
								$('#folio_promo').val('');
								$('#folio_valid').val('0');
								$('#id_customers_promo').val('0');
							}
						});						
					}
				}
			});

		}
	}


	/*
	 * ----------------------------------------------------------------
	 * Step 2 :: Productos
	 * ----------------------------------------------------------------	
	 */
	// Variables globales del paso actual
	var shop_cart_items		= []; // Contiene los productos seleccionados para la compra
	var order_pay_type		= ''; // Forma de pago de la orden de acuerdo al primer producto seleccionado
	var order_total_pmts	= ''; // Cantidad de pagos de la orden de acuerdo al primer producto seleccionado
	var order_shipping		= 0; // Costo del envío normal
	var order_shp_type		= 1; // Tipo de envio (1: Standard CC o Ref. Dep., 3: COD Standard)
	var order_total			= 0; // Monto total de la orden
	var order_total_net		= 0; // Monto neto de la orden
	var order_taxes_pct		= 0; // Porcentaje de impuestos
	var order_discount		= 0; // Monto total de descuentos
	var order_coupon		= ''; // Codigo del cupón de descuento
	var total_items_promo	= 0; // Cantidad de items que contiene el promo seleccionado
	var product_selected	= null; // Objeto con las propiedades del producto o promo seleccionado
	var filter_search		= 'topsales'; // Para búsquedas predefinidas
	// Variables para la paginacion
	var prod_per_page		= 10; // Total de productos que se mostrarán por página
	var current_page		= 1; // Página actual
	var cmd_pag				= false; // Bandera que indicará si se ejecutó la paginación
	
	// Controla la busqueda de productos
	if( $('#txt_search').length ){
		// Variable para controlar las llamadas ajax
		var this_ajax;

		// Eventos para el control de escritura en la busqueda de productos
		var key_search = false;
		// Valida el caracter pulsado
		$('#txt_search').keydown(function(event) {
			key_search = validate_key(event);
		});		
		$('#txt_search').keyup(function(event) {
			// Si el caracter pulsado es válido(texto)
			if( key_search && event.keyCode != 27 ){
				var this_obj = $(this);
				
				if( this_obj.val() != '' && this_obj.val().length > 3 ){
					// Si ya existe una peticion ajax, la cancela
					if( this_ajax && this_ajax.readyState != 4 ){ 
					    this_ajax.abort();
					}
					current_page = 1;

					filter_search = '';
					search_products(this_obj.val());

				}else if( this_obj.val() == '' || this_obj.val().length <= 3 ){
					$('#div_search_result').html('');

					// Se reinician los páneles de paginación
					$('#div_pages_info_top').html('');
		            $('#div_pages_info_bottom').html('');
		            $('#div_pages_top').html('');
		            $('#div_pages_bottom').html('');
				}
			// Si el caracter pulsado es ESC, se borra el contenido de la búsqueda anterior
			}else if( event.keyCode == 27 ){
				// Si ya existe una peticion ajax, la cancela
				if( this_ajax && this_ajax.readyState != 4 ){ 
				    this_ajax.abort();
				}

				$(this).val('');
				// Se reinician los páneles de paginación
				$('#div_pages_info_top').html('');
	            $('#div_pages_info_bottom').html('');
	            $('#div_pages_top').html('');
	            $('#div_pages_bottom').html('');
			}
		});

		// Traer los productos mas vendidos
		$('#lnk_prod_topsales').click(function(event) {
			filter_search = 'topsales';
			search_products('');
		});
		// Traer los productos de la última orden
		$('#lnk_prod_last_order').click(function(event) {
			filter_search = 'lastorder';
			search_products('');
		});


		$('.div_pagination').on('click', '.page', function(event){
			$('#page-top-'+current_page).removeClass('page_on').addClass('page');
			$('#page-btm-'+current_page).removeClass('page_on').addClass('page');
			current_page = $(this).attr('rel');
			cmd_pag = true;
			filter_search = '';
			search_products( $('#txt_search').val() );
			$('#page-top-'+current_page).removeClass('page').addClass('page_on');
			$('#page-btm-'+current_page).removeClass('page').addClass('page_on');
		});

		// Funcion que ejecuta la búsqueda de productos via ajax
		function search_products(txt_sch){
			if( txt_sch == '' && filter_search == '' ){
				$('#div_search_result').html('');
			}else{
				// Nueva peticion ajax
				var this_zipcode = ( $('#shp_zipcode').val() != '' && typeof $('#shp_zipcode').val() !== 'undefined' ) ? $('#shp_zipcode').val() : $('#zipcode').val();
				this_ajax = $.ajax({
				    url: '/cgi-bin/common/apps/ajaxbuild',
			        data: {
			        	'ajaxbuild': 'sale_search_products',
			        	'txt_search': txt_sch, 		        	
			        	'zipcode': this_zipcode,
			        	'authcode':	'000',
			        	'id_salesorigins': $('#id_salesorigins').val(),
			        	'pay_type_available': $('#pay_type_available').val(),
			        	'pay_type': order_pay_type,
			        	'fpmts': order_total_pmts,
			        	'filter': filter_search,
			        	'prod_per_page': prod_per_page,
			        	'current_page': current_page,
			        },
			        dataType: 'json',
			        type: 'post',
			        cache: false,
			        async: true,
			        beforeSend: function(){
			            $('#div_search_result').html( loading('Buscando productos... por favor espere') );
			            if( !cmd_pag ){
			            	// Se reinician los páneles de paginación
				            $('#div_pages_info_top').html('');
				            $('#div_pages_info_bottom').html('');
				            $('#div_pages_top').html('');
				            $('#div_pages_bottom').html('');
				        }
			        },
			        success: function(xresponse){			        	

			        	if( xresponse.result == 'OK' ){
			        		list_products(xresponse);
			        	}else if( xresponse.result == 'ERROR' ){

			        	}
				       
				    },
				    error: function(objeto, detalle, masdetalles){                
			            console.log(detalle.toUpperCase() + ': ' + masdetalles);
			        } 
				});
			}
		}

		// Funcion que genera el html con los datos obtenidos en la busqueda
		function list_products(data){

			if( !cmd_pag ){
				// Se muestra la cantidad de productos encontrados			
				$('#div_pages_info_top').html(data.total_matches+' productos encontrados');
				$('#div_pages_info_bottom').html(data.total_matches+' productos encontrados');
				// Se generan las paginas(solo si aplica)
				if( data.total_matches > prod_per_page ){
					var total_pages = parseInt(data.total_matches) / parseInt(prod_per_page);
					if( (parseInt(data.total_matches) % parseInt(prod_per_page)) > 0 )
						total_pages++;
					var html_pages_top = html_pages_btm = '';
					for( var i=1; i<=total_pages; i++ ){
						if( current_page == i ){
							html_pages_top += '<a href="#" id="page-top-'+i+'" class="page_on" rel="'+i+'">'+i+'</a>';
							html_pages_btm += '<a href="#" id="page-btm-'+i+'" class="page_on" rel="'+i+'">'+i+'</a>';
						}
						else{
							html_pages_top += '<a href="#" id="page-top-'+i+'" class="page" rel="'+i+'">'+i+'</a>';
							html_pages_btm += '<a href="#" id="page-btm-'+i+'" class="page" rel="'+i+'">'+i+'</a>';
						}
					}
			    	$('#div_pages_top').html(html_pages_top);
			    	$('#div_pages_bottom').html(html_pages_btm);
			    }			    
			}

			if( data.matches > 0 ){
				var html_list = '';
				for( var i=0; i<data.matches; i++ ){
					html_list += '<div class="div_product">';
					html_list += '	<div class="div_product_photo">';
					html_list += '		<a href="#" id="photo-'+data.products[i].id_products+'" class="lnk_product_photo" data-prod-id="'+data.products[i].id_products+'" data-prod-promo="'+data.products[i].promo+'">';
					html_list += '			<img src="'+data.products[i].image+'" onerror="this.onerror=null;this.src=\'/sitimages/sales/prod/none.jpg\';" width="100%">';
					html_list += '		</a>';
					html_list += '	</div>';
					html_list += '	<div class="div_product_info">';
					var st_pauta = '';
					if( data.products[i].status == 'Pauta Seca' ){
						st_pauta = '<span class="status_prod_pauta">'+data.products[i].status+'</span>';
					}
					html_list += '		<span style="font-size: 12pt;">'+data.products[i].model+st_pauta+'</span><br />';
					html_list += '		<span style="display: block; margin-bottom: 7px;">Product ID: '+data.products[i].id_products+'</span>';
					// Formas de pagos y precios
					var price_old = 0;
					for( var j=0; j<data.products[i].prices_matches; j++ ){						
						if( price_old != data.products[i].prices[j].price ){
							var price = parseFloat(data.products[i].prices[j].price).toFixed(2);
							html_list += '<span style="display: block; font-weight: bold;">Precio: '+format_price(price)+'</span>';
						}

						html_list += '<a href="#" class="product_options" ';
						html_list += '		data-prod-id="'+data.products[i].id_products+'" ';
						html_list += '		data-prod-model="'+data.products[i].model+'" ';
						html_list += '		data-prod-price="'+data.products[i].prices[j].price+'" ';
						html_list += '		data-prod-taxpct="'+data.products[i].prices[j].tax_pct+'" ';
						html_list += '		data-prod-idprice="'+data.products[i].prices[j].id_prod_prices+'" ';
						html_list += '		data-prod-paytype="'+data.products[i].prices[j].pay_type+'" ';
						html_list += '		data-prod-choices="'+data.products[i].choices+'" ';
						html_list += '		data-prod-promo="'+data.products[i].promo+'" ';
						html_list += '		data-prod-pmts="'+data.products[i].prices[j].flexi_pmts+'" ';
						html_list += '		data-prod-shipping="'+data.products[i].prices[j].shipping+'" ';
						html_list += '		data-prod-free-shp="'+data.products[i].free_shp+'" ';
						html_list += '	>';						
						html_list += '	<span style="font-size: 7pt;">'+data.products[i].prices[j].flexi_pmts+' PAGO(S)</span>';
						html_list += '	<img src="/sitimages/sales/icon'+data.products[i].prices[j].pay_type.replace(' ','-')+'.png" style="width: 25px; vertical-align: middle;">';
						html_list += '</a>';

						price_old = data.products[i].prices[j].price;
					}
					html_list += '	</div>';
					html_list += '	<div style="display:block; clear: both;"></div>';
					html_list += '</div>';
				}			
				// Se muestra el listado de productos en pantalla
				$('#div_search_result').html(html_list);

				// Se crea la funcionalidad para seleccionar un producto
				if( $('#frm_sales_step2').length ){
					$('.product_options').click(function(event){
						product_selected = $(this);
						shop_cart({
							'oper': 'add', 
							'obj': $(this),
						});

						return false;
					});

					// Se crea el evento click para mostrar la info. del producto
					$('.lnk_product_photo').click(function(event) {
						show_product_info($(this).attr('data-prod-id'), $(this).attr('data-prod-promo'));
						return false;
					});
				}


			}else{
				var html_no_match = '<div style="text-align: center; padding-top: 15px;"><span style="color: red; margin: auto auto; display: block; position relative;">No existen conincidencias...</span></div>';
				$('#div_search_result').html(html_no_match);
			}

			cmd_pag = false;
		}
	
		// Controla el carro de compras
		function shop_cart(params){	
			
			// Agregar el producto o promo seleccionado al carro de compras
			if( params.oper  == 'add' ){
				
				// Se valida el monto límite para una orden COD
				if( order_pay_type == 'COD' && order_total > 0 ){
					var limit_amt = ( $('#cod_limit_amt').val() != '' ) ? parseFloat($('#cod_limit_amt').val()) : 0;
					var this_price = ( params.obj.attr('data-prod-price') != '' ) ? parseFloat(params.obj.attr('data-prod-price')) : 0;

					var new_total = order_total + this_price;
					// Si el monto total de la orden sumado al precio del nuevo producto seleccionado
					// es mayor que el límite definido, se impide agregar el nuevo producto
					if( new_total > limit_amt ){
						build_dialog('El precio del producto seleccionado sumado al monto actual de la orden, excede el l&iacute;mite permitido para una orden COD ('+format_price(limit_amt.toFixed(2))+')', 'error');
						dialog_form.dialog({
							buttons: {
								'Aceptar': function(){						
									$(this).dialog('close');
								}
							}
						});

						return false;
					}
				}

				// PROMO: Alguno de los productos tiene opciones(talla, color, etc.)
				if( params.obj.attr('data-prod-promo') == 1 && params.obj.attr('data-prod-choices') > 0 ){

					// Se obtienen los Items con sus choices
					get_choices({
						'id_product': params.obj.attr('data-prod-id'), 
						'id_prod_price': params.obj.attr('data-prod-idprice'), 
						'promo': 1,
					});

				// PROMO: Sin opciones(talla, color, etc.)
				}else if( params.obj.attr('data-prod-promo') == 1 ){

					// Se obtienen los productos de la promo
					var response = get_promo({
						'id_product': params.obj.attr('data-prod-id'),
						'id_prod_prices': params.obj.attr('data-prod-idprice'),
						'ids_products': '',
						'pay_type':  params.obj.attr('data-prod-paytype'),
					});					

			    	if( response.result == 'OK' ){
			    		// Genera un random para el id de la promo
			    		var this_parent = get_random();
			    		
			    		for( var i = 0; i < response.matches; i++ ){
			    			var is_main =( i == 0 ) ? 1 : 0;

			    			shop_cart_add({
								'id_prod': product_selected.attr('data-prod-id'),
								'id_sku_prod': response.products[i].id_sku_prod,
								'model': response.products[i].model,
								'price': response.products[i].price,
								'id_price': product_selected.attr('data-prod-idprice'),
								// 'tax_pct': order_taxes_pct,
								'tax_pct': product_selected.attr('data-prod-taxpct'),
								'pay_type': product_selected.attr('data-prod-paytype'),
								'pmts': product_selected.attr('data-prod-pmts'),
								'main_prod': is_main,
								'parent_prod': this_parent,
								'shipping': product_selected.attr('data-prod-shipping'),
								'free_shp': product_selected.attr('data-prod-free-shp'),
							});
			    		}
			    		// Se calculan los totales y se guardan los datos en localStorage
			    		shop_cart_totals();
			    		save_sessionStorage();
			    	}

				// PRODUCTO: Con opciones
				}else if( params.obj.attr('data-prod-choices') > 0 ){

					// Se obtienen los Items con sus choices					
					get_choices({
						'id_product': params.obj.attr('data-prod-id'),
						'id_prod_price': params.obj.attr('data-prod-idprice'),
					});

				// PRODUCTO: Sin opciones
				}else{
					// Genera un random para el id de la promo
			    	var this_parent = get_random();

					// Se agrea el producto al carro de compras
					shop_cart_add({
						'id_prod': params.obj.attr('data-prod-id'),
						'id_sku_prod': '',
						'model': params.obj.attr('data-prod-model'),
						'price': params.obj.attr('data-prod-price'),
						'id_price': product_selected.attr('data-prod-idprice'),
						// 'tax_pct': order_taxes_pct,
						'tax_pct': product_selected.attr('data-prod-taxpct'),
						'pay_type': params.obj.attr('data-prod-paytype'),
						'pmts': product_selected.attr('data-prod-pmts'),
						'main_prod': 1,
						'parent_prod': this_parent,
						'shipping': params.obj.attr('data-prod-shipping'),
						'free_shp': product_selected.attr('data-prod-free-shp'),
					});

					// Se calculan los totales y se guardan los datos en localStorage
		    		shop_cart_totals();
		    		save_sessionStorage();
				}

			// Se elimina el item seleccionado del carro de compras
			}else if( params.oper == 'del' ){

				shop_cart_del(params);

			}

		}	

		// Obtiene las opciones(choices) del producto
		function get_choices(params){
			var promo	= (params.promo != 'undefined') ? params.promo : 0;

			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',
				dataType: 'json',
				data: {
					'ajaxbuild': 'sale_get_choices',
					'id_product': params.id_product,
					'id_prod_price': params.id_prod_price,
					'promo': promo,
				},
				async: false,
				cache: false,
				beforeSend: function(){
					$('#div_choices').dialog('open');
					$('#div_choices').html( loading('Cargando las opciones del productos, por favor espere') );
				},
				success: function(xresponse){
					// Se genera el html para mostrar las opciones(choices)
					if( xresponse.result == 'OK' ){
						var html_choices = '';
						for( var i = 0; i < xresponse.items_matches; i++ ){
							
							html_choices += '<div style="border-top: 1px solid #d8d8d8; margin-top: 10px;">';
							html_choices += '	<span style="background-color: #d8d8d8; max-width: 100%; padding: 3px; display: block; text-align: left;">'+xresponse.choice_list[i].model+'</span>';
							html_choices += '	<span style="min-width: 80px; padding: 3px; margin-left: 30px; display: inline-block; text-align: rigth;">'+xresponse.choice_list[i].descrip+'</span>';
							html_choices += '	<span style="padding: 3px; display: inline-block;">';
							html_choices += '		<select name="cbx_choice-'+i+'" id="cbx_choice-'+i+'" style="max-width: 350px;">';
							if( xresponse.choice_list[i].matches > 0 ){
								for( var j = 0; j < xresponse.choice_list[i].matches; j++ ){
									html_choices += '	<option value="'+xresponse.choice_list[i].items[j].id_sku_prod+'">'+xresponse.choice_list[i].items[j].value+'</option>';
								}
							}else{
								if( xresponse.choice_list[i].id_sku_prod != undefined ){
									html_choices += '		<option value="'+xresponse.choice_list[i].id_sku_prod+'">'+xresponse.choice_list[i].model+'</option>';
								}else{
									html_choices += '		<option value="0">Choices Error !!!</option>';
								}
							}
							html_choices += '		</select>';
							html_choices += '	</span>';
							html_choices += '</div>';
						}

						total_items_promo = xresponse.items_matches;

						var height_modal = ((xresponse.items_matches * 85) + 100) - (xresponse.items_matches * 5);
						$('#div_choices').dialog({height: height_modal});
						$('#div_choices').html(html_choices);						
					}
				},
				error: function(objeto, detalle, masdetalles){                
		            $('#div_choices').html(detalle.toUpperCase() + ': ' + masdetalles);
		        } 
			});
		}

		// Obtienen los datos(id_products, modelo, precio) de los items que componen una promo
		function get_promo(params){
			var result = false;

			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',
				dataType: 'json',
				data: {
					'ajaxbuild': 'sale_get_products_promo',
					'ids_products': params.ids_products,
					'id_product': params.id_product,
					'pay_type': params.pay_type,
					'id_prod_prices': params.id_prod_prices,
					'id_salesorigins': $('#id_salesorigins').val(),
				},
				async: false,
				cache: false,
				success: function(xresponse){
					// Se genera el html para mostrar las opciones
					result = xresponse;
				},
			});

			return result;
		}

		// Ventana modal para seleccion de opciones(talla, color, etc.) de productos
		if( $('#div_choices').length ){
			$('#div_choices').dialog({
				autoOpen: false,
			    height: 400,
			    width: 700,
			    modal: true,
			    buttons: {
				    'Aceptar': function(){
				    	
				    	//------------------------------------------------------------
				    	// Se recogen las opciones seleccionadas por el usuario
				    	var ids = '';
				    	var descrips = '';
				    	var choices_ok = 1;
				    	for( var i=0; i < total_items_promo; i++ ){
				    		if( $('#cbx_choice-'+i+' option:selected').val() != '0' ){
					    		ids += $('#cbx_choice-'+i+' option:selected').val()+',';
					    		descrips += $('#cbx_choice-'+i+' option:selected').text()+',';
					    	}else{
					    		choices_ok = 0;
					    	}
				    	}

				    	if( choices_ok == 1 ){
					    	ids = ids.substr(0, (ids.length - 1));
					    	descrips = descrips.substr(0, (descrips.length - 1));
					    	descrips = descrips.replace(/\s::\s/g, ':');
					    	var ary_choices = descrips.split(',');

					    	// Si es un promo, se obtienen sus productos
					    	if( product_selected.attr('data-prod-promo') == 1 ){
					    		
						    	var response = get_promo({
							    		'id_product': product_selected.attr('data-prod-id'),
							    		'id_prod_prices': product_selected.attr('data-prod-idprice'),
							    		'ids_products': ids,
							    		'pay_type':  product_selected.attr('data-prod-paytype'),
							    	});

						    	if( response.result == 'OK' ){
						    		var this_parent = get_random();

						    		for( var i = 0; i < response.matches; i++ ){

						    			var is_main = ( i == 0 ) ? 1 : 0;
						    			var this_model = '';
						    			this_model = ( ary_choices[i] != response.products[i].model ) ? response.products[i].model+' ('+ary_choices[i]+')' : response.products[i].model;
						    			shop_cart_add({
											'id_prod': product_selected.attr('data-prod-id'),
											'id_sku_prod': response.products[i].id_sku_prod,
											'model': this_model,
											'price': response.products[i].price,
											'id_price': product_selected.attr('data-prod-idprice'),
											// 'tax_pct': order_taxes_pct,
											'tax_pct': product_selected.attr('data-prod-taxpct'),
											'pay_type': product_selected.attr('data-prod-paytype'),
											'pmts': product_selected.attr('data-prod-pmts'),
											'main_prod': is_main,
											'parent_prod': this_parent,
											'shipping': product_selected.attr('data-prod-shipping'),
											'free_shp': product_selected.attr('data-prod-free-shp'),
										});
						    		}
						    		$(this).dialog('close');
						    		// Se calculan los totales y se guardan los datos en localStorage
				    				shop_cart_totals();
				    				save_sessionStorage();
						    	}

						    // Si solo es un producto, se agrega al carro de compras
						    }else{					    	
						    	var this_model = ( ary_choices[0] != product_selected.attr('data-prod-model') ) ? product_selected.attr('data-prod-model')+' ('+ary_choices[0]+')' : product_selected.attr('data-prod-model');
						    	var this_parent = get_random();

								shop_cart_add({
									'id_prod': product_selected.attr('data-prod-id'),
									'id_sku_prod': ids,
									'model': this_model,
									'price': product_selected.attr('data-prod-price'),
									'id_price': product_selected.attr('data-prod-idprice'),
									// 'tax_pct': order_taxes_pct,
									'tax_pct': product_selected.attr('data-prod-taxpct'),
									'pay_type': product_selected.attr('data-prod-paytype'),
									'pmts': product_selected.attr('data-prod-pmts'),
									'main_prod': 1,
									'parent_prod': this_parent,
									'shipping': product_selected.attr('data-prod-shipping'),
									'free_shp': product_selected.attr('data-prod-free-shp'),
								});
					    		$(this).dialog('close');
					    		// Se calculan los totales y se guardan los datos en localStorage
				    			shop_cart_totals();
				    			save_sessionStorage();
						    }
						}else{
							$(this).dialog('close');
							build_dialog('Hay un problema con alg&uacute;n producto(Choices Error), por favor val&iacute;delo con el administrador del sistema', 'error');
							dialog_form.dialog({
								buttons: {
									'Cerrar': function(){
										$(this).dialog('close');
									},
								}
							});
						}
					    //------------------------------------------------------------
				    },
				    'Cancelar': function(){
				    	$(this).dialog( "close" );
				    },
			    },
			    open: function(){
			    	$(this).siblings('.ui-dialog-buttonpane').find("button:contains('Aceptar')").focus();
			    },
			});
		}

		$('#txt_search').focus();

	}
	
	// Agrega y visualiza el producto en el carro de compras
	function shop_cart_add(params){
		// Se calcula el precio sin IVA y su iva correspondiente
		var price_net = 0;
		if( parseFloat(params.tax_pct) > 0 ){
			if( parseFloat(params.tax_pct) > 1 ){
				params.tax_pct = parseFloat(params.tax_pct) / 100;
			}
			price_net = (parseFloat(params.price) / (1 + parseFloat(params.tax_pct))).toFixed(2);
		}else{
			price_net = params.price;
		}

		var html_prod = '';
		if( params.main_prod == 1 ){
			html_prod += '<div id="div_prod-'+params.id_prod+'-'+params.parent_prod+'" class="shop_cart_cont_line" style="display: block; border-top: 1px solid silver;">';
			html_prod += '	<input type="checkbox" id="shop_cart_chk-'+params.parent_prod+'" checked="true" class="shop_cart_chk">';
		}else{
			html_prod += '<div id="div_prod-'+params.id_prod+'-'+params.parent_prod+'" class="shop_cart_cont_line" style="display: block;">';
			html_prod += '<span class="shop_cart_chk" style="width: 22px;">&nbsp;</span>';
		}
		html_prod += '	<span class="shop_cart_prod_name">'+params.model.substr(0,50)+'</span>';
		html_prod += '	<span class="shop_cart_prod_price">'+format_price(price_net)+'</span>';
		if( params.main_prod == 1 && $('#step').val() == 3 ){
			html_prod += '	<a href="#" id="lnk_drop-'+params.id_prod+'-'+params.parent_prod+'" class="shop_cart_drop" rel="'+params.parent_prod+'">';
			html_prod += '		<img src="/sitimages/default/b_drop.png" alt="X" style="border: none; height: 14px; width: 14px;"/>';
			html_prod += '	</a>';
		}else{
			html_prod += '<span class="shop_cart_drop" style="display: inline-block"></span>';
		}
		html_prod += '</div>';
		html_prod += '<div style="display:block; clear: both;"></div>';

		// Se muestra el producto o promo seleccionado en el carro de compras
		if( shop_cart_items.length == 0 ){
			$('#div_shop_cart_cont').html(html_prod);				
		}else{
			$('#div_shop_cart_cont').append(html_prod);	
		}

		var this_free_shp = ( params.free_shp != undefined ) ? params.free_shp : 0;

		// Se agrega al array de productos(id_products, id_sku_prod, model, price, tax_pct, qty, main_prod, parent_prod, id_products_price, free_shp)
		var id_sku_prod = ( params.id_sku_prod != '' ) ? params.id_sku_prod : '100'+params.id_prod;
		shop_cart_items.push([params.id_prod, id_sku_prod, params.model, params.price, params.tax_pct, 1, params.main_prod, params.parent_prod, params.id_price, this_free_shp]);

		// Cantiad de pagos
		if( order_total_pmts == '' ){
			order_total_pmts = params.pmts;
		}

		// Costo de envío
		if( order_shipping == 0 ){
			order_shipping = params.shipping;
			// Este dato servirá para recuperar el costo del envio en caso de requerirlo
			var this_order_shipping_bkp = (localStorage.getItem('order_shipping_bkp') != undefined ) ? localStorage.getItem('order_shipping_bkp') : 0;
			if( order_shipping != this_order_shipping_bkp )
				localStorage.setItem('order_shipping_bkp', order_shipping);
		}
		if( (this_free_shp == 1 || (localStorage.getItem('free_shp') != undefined && localStorage.getItem('free_shp') == '1')) && order_shp_type != 2 ){
			order_shipping = 0;
			localStorage.setItem('free_shp', 1);
		}		

		// Se calculan los totales
		//--> shop_cart_totals();
		
		// Forma de pago
		if( order_pay_type == '' ){
			order_pay_type = params.pay_type;			
			// Se hace visible la forma de pago
			$('#opt_pay_type_cc').removeClass('pay_legend_selected').addClass('pay_legend');
			$('#opt_pay_type_cod').removeClass('pay_legend_selected').addClass('pay_legend');
			$('#opt_pay_type_rd').removeClass('pay_legend_selected').addClass('pay_legend');
			order_shp_type = 1;
			if( order_pay_type == 'Credit-Card' ){
				$('#opt_pay_type_cc').removeClass('pay_legend').addClass('pay_legend_selected');
			}else if( order_pay_type == 'COD' ){
				$('#opt_pay_type_cod').removeClass('pay_legend').addClass('pay_legend_selected');
				order_shp_type = 3;
			}else if( order_pay_type == 'Referenced Deposit' ){
				$('#opt_pay_type_rd').removeClass('pay_legend').addClass('pay_legend_selected');
			}
			// Se hace visible la cantidad de pagos
			$('#div_total_pmts').css('display', 'block').html(order_total_pmts);

			if( filter_search != '' && $('#txt_search').val() != '' ){
				filter_search = '';
			}
			search_products( $('#txt_search').val() );
		}		

		// Se guardan los cambios en la sesion
		//--> save_sessionStorage();
	}

	// Elimina un producto del carro de compras
	function shop_cart_del(params){
		var id_prod_drop = params.obj.attr('id').substr(9);
		var ids = id_prod_drop.split('-');

		var shop_cart_tmp = [];// Array temporal
		var this_free_shp = 0;
		for( var i=0; i<shop_cart_items.length; i++ ){
			if( shop_cart_items[i][0] == ids[0]/*id_prod*/ && shop_cart_items[i][7] == ids[1]/*id_random*/ ){
				$('#div_prod-'+id_prod_drop).remove();
			}else{
				// Se pasan al array temporal aquellos productos que no se van a eliminar
				shop_cart_tmp.push([shop_cart_items[i][0], shop_cart_items[i][1], shop_cart_items[i][2], shop_cart_items[i][3], shop_cart_items[i][4], shop_cart_items[i][5], shop_cart_items[i][6], shop_cart_items[i][7], shop_cart_items[i][8],shop_cart_items[i][9]]);
				if( shop_cart_items[i][9] == 1 )
					this_free_shp = 1;
			}				
		}
		// Se borra completamente el array original
		shop_cart_items.length = 0;
		// Se sobreescribe el array original con el array temporal
		shop_cart_items = shop_cart_tmp.slice();
		if( this_free_shp == 0 && order_shp_type != 2 ){
			order_shipping = localStorage.getItem('order_shipping_bkp');
			if( order_shipping == null || order_shipping == 'null' )	order_shipping = 0;
			localStorage.setItem('free_shp', 0);
		}

		// Si se vacía el carro de compras, se eliminan los datos:
		// -> Forma de pago
		// -> Cantidad de pagos
		if( shop_cart_items.length == 0 ){
			order_pay_type	= '';
			order_total_pmts= '';
			order_shipping	= 0;
			order_shp_type = 1;
			order_discount	= 0;
			//$('#div_order_pay_type').html('');
			//$('#div_shop_cart_cont').html('<div class="border_space">El carro est&aacute; vac&iacute;o</div>');
			$('#opt_pay_type_cc').removeClass('pay_legend_selected').addClass('pay_legend');
			$('#opt_pay_type_cod').removeClass('pay_legend_selected').addClass('pay_legend');
			$('#opt_pay_type_rd').removeClass('pay_legend_selected').addClass('pay_legend');
			$('#div_total_pmts').css('display', 'none').html('');
		}

		// Se calculan los totales
		shop_cart_totals();

		// Se guardan los cambios en la sesion
		save_sessionStorage();
	}

	// Información del producto
	if( $('#div_show_product_info').length ){
		$('#div_show_product_info').dialog({
			autoOpen: false,
		    height: 600,
		    width: 800,
		    modal: false,
		    draggable: true,
		    buttons: {			    
			    'Cerrar': function(){
			    	$(this).dialog( "close" );
			    },
		    },
		    open: function(){
		    	//$(this).siblings('.ui-dialog-buttonpane').find("button:contains('Aceptar')").focus();
		    },
		});
	}
	function show_product_info(id_product, promo){
		//$('#div_show_product_info').dialog('open');
		//$('#div_product_info_content').html('<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=sales_parts_tecs_specs&id_productv='+id_product+'&promo='+promo+'" style="width: 700px; height: 500px; overflow: hidden; border: none; margin: auto auto; position: relative;"></iframe>');
		
		$.ajax({
			url: '/cgi-bin/common/apps/ajaxbuild',
			type: 'post',
			dataType: 'html',
			data: {
				'ajaxbuild': 'sales_product_info',
				'id_product': id_product,
				'promo': promo,
			},
			async: false,
			cache: false,
			beforeSend: function(){
				$('#div_show_product_info').dialog('open');
				$('#div_show_product_info').html( loading('Cargando Informaci&oacute;n del producto, por favor espere') );
			},
			success: function(xresponse){
				$('#div_show_product_info').html(xresponse);

				$('#tabs-prod-info').tabs();
			},
			error: function(objeto, detalle, masdetalles){                
	            $('#div_show_product_info').html(detalle.toUpperCase() + ': ' + masdetalles);
	        } 
		});
		
	}

	// Se crea la funcionalidad del checkbox del carro de compras
	$('#div_shop_cart_cont').on('click', '.shop_cart_chk', function(event){			
		shop_cart_totals();
	});

	// Se crea la funcionalidad del link para eliminar un production del carro de compras
	$('#div_shop_cart_cont').on('click', 'a.shop_cart_drop', function(event){			
		shop_cart({
			'oper': 'del', 
			'obj': $(this),
		});
	});		

	// Calula los montos totales del carro de compras
	function shop_cart_totals(){
		// Se recalculan los totales
		var total = 0, total_net = 0, total_taxes = 0, services_amt = 0, services_tax_amt = 0;
		var ftotal, ftotal_net, ftotal_taxes, fshipping, fdiscount;

		var this_amounts = [];
		for( var i=0; i<shop_cart_items.length; i++ ){
			// Se asegura que contabilice solo los seleccionados
			var st_id = $('#shop_cart_chk-'+shop_cart_items[i][7]).is(':checked');
			if( st_id == true ){
				var this_price_net = (parseFloat(shop_cart_items[i][3]) / (1 + parseFloat(shop_cart_items[i][4]))).toFixed(2);
				var this_tax_amt = parseFloat(this_price_net) * parseFloat(shop_cart_items[i][4]);
				this_tax_amt = this_tax_amt.toFixed(2);
				// Se agregan los montos del precio neto, del IVA y el porcentaje del IVA
				this_amounts.push([this_price_net, this_tax_amt, shop_cart_items[i][4]]);

				total_net = (parseFloat(total_net) + parseFloat(this_price_net)).toFixed(2);
				total_taxes = (parseFloat(total_taxes) + parseFloat(this_tax_amt)).toFixed(2);
				// Si es un servicio, obtiene el precio total para agregarselo 
				// al monto del primer pago cuando aplique el MSI
				if( shop_cart_items[i][1].toString().substr(0, 1) == '6' ){
					services_amt = parseFloat(services_amt) + parseFloat(this_price_net);
					services_tax_amt = parseFloat(services_tax_amt) + parseFloat(this_tax_amt);
				}
			}
		}

		// Subtotal
		order_total_net = total_net;
		ftotal_net = format_price(total_net);
		$('#div_shop_cart_subtotal .shop_cart_prod_price').html(ftotal_net);
		
		// Descuentos
		if( localStorage.getItem('order_coupon') != '' && localStorage.getItem('order_coupon') != undefined ){
			var this_disc_amt = 0;
			if( localStorage.getItem('coupon_applied') == 'Net' ){
				if( localStorage.getItem('coupon_disc_type') == '%' ){
					this_disc_amt = (parseFloat(localStorage.getItem('coupon_disc')) / 100) * parseFloat(order_total_net);
					this_disc_amt = this_disc_amt.toFixed(2);
				}else{
					this_disc_amt = (order_total_net >= parseFloat(localStorage.getItem('coupon_disc'))) ? parseFloat(localStorage.getItem('coupon_disc')) : order_total_net;
				}
			}else{
				var this_order_taxes = parseFloat(total_taxes);// + (parseFloat(order_shipping) * parseFloat(order_taxes_pct));
				this_order_taxes = this_order_taxes.toFixed(2);
				var this_order_total = parseFloat(order_total_net) + parseFloat(this_order_taxes);//+ parseFloat(order_shipping)
				if( localStorage.getItem('coupon_disc_type') == '%' ){		    					
					this_disc_amt = (parseFloat(localStorage.getItem('coupon_disc')) / 100) * parseFloat(this_order_total);
					this_disc_amt = this_disc_amt.toFixed(2);
				}else{
					this_disc_amt = (this_order_total >= parseFloat(localStorage.getItem('coupon_disc'))) ? parseFloat(localStorage.getItem('coupon_disc')) : this_order_total;
				}

				this_disc_amt = this_disc_amt / (1+parseFloat(order_taxes_pct));
			}
			
			order_discount = this_disc_amt;
		}
		
		fdiscount = format_price(order_discount);
		$('#div_shop_cart_discount .shop_cart_prod_price').html(fdiscount);
		total = parseFloat(total_net) - parseFloat(order_discount);
		
		// Se recaulculan los impuestos si existe un descuento
		if( order_discount > 0 ){//&& localStorage.getItem('coupon_applied') == 'Net'
			total_taxes = 0;
			var this_disc_rest = order_discount;
			for( var i=0; i<this_amounts.length; i++ ){
				var this_price_net = parseFloat(this_amounts[i][0]);
				var this_tax_amt = parseFloat(this_amounts[i][1]);
				var this_tax_pct = parseFloat(this_amounts[i][2]);
				// Se calcula el monto del descuento para el producto actual
				var this_discount = 0;
				if( this_disc_rest > 0 ){
					if( this_disc_rest > this_price_net ){
						this_discount = this_price_net;
						this_disc_rest -= this_price_net;
					}else{
						this_discount = this_disc_rest;
						this_disc_rest = 0;
					}
				}
				var this_tax_amt = ((this_price_net - this_discount) * this_tax_pct).toFixed(2);
				total_taxes	= parseFloat(total_taxes) + parseFloat(this_tax_amt);
			}
			//total_taxes = (parseFloat(total) * parseFloat(order_taxes_pct)).toFixed(2);
			
		}
		
		var shipping_tax = parseFloat(order_shipping) * parseFloat(order_taxes_pct);
		total_taxes = parseFloat(total_taxes) + shipping_tax;
		total = (parseFloat(total) + parseFloat(total_taxes)).toFixed(2);

		ftotal_taxes = format_price(total_taxes);
		$('#div_shop_cart_taxes .shop_cart_prod_price').html(ftotal_taxes);

		// Manejo y envío
		var color_shp = (order_shipping > 0) ? '#2E2E2E' : '#21610B';
		fshipping = format_price(order_shipping);
		$('#div_shop_cart_shipping .shop_cart_prod_price').html(fshipping).css({'color': color_shp});
		total = parseFloat(total) + parseFloat(order_shipping);

		// Total general
		order_total = total;
		window.order_total_tmp = order_total;	
		ftotal = format_price(total);
		$('#div_shop_cart_totals_amt').html('Total: '+ftotal);
		$('#div_shop_cart_totals_prod').html( shop_cart_items.length+' Producto(s)');

		// Cálculo de pagos por periodos
		if( order_total_pmts > 1 ){
			// Por mes
			var pago_mensual = parseFloat(total / order_total_pmts).toFixed(2);
			$('#td_pago_mensual').html( format_price(pago_mensual) );
			// Por semana
			var pago_semanal = parseFloat(total / (order_total_pmts * 4)).toFixed(2);
			$('#td_pago_semanal').html( format_price(pago_semanal) );
			// Por día
			var pago_diario = parseFloat(total / (order_total_pmts * 30)).toFixed(2);
			$('#td_pago_diario').html( format_price(pago_diario) );
		}else{
			var total_price = format_price(total);
			$('#td_pago_mensual').html(total_price);
			$('#td_pago_semanal').html(total_price);
			$('#td_pago_diario').html(total_price);
		}

		// Si el paso actual es: 5: Confirmar
		if( $('#step').val() == '6' && $('#span_order_total').html() != ftotal ){
			$('#span_totalnet_amt').html(ftotal_net);
			$('#span_discount_amt').html(fdiscount);
			$('#span_taxes_amt').html(ftotal_taxes);
			$('#span_shipping_amt').html(fshipping);
			$('#span_order_total').html(ftotal);
			
			// Si la forma de pago es Credit-Card y a MSI
			if( order_pay_type == 'Credit-Card' && order_total_pmts > 1 ){
				/*
				var this_pmt_amt = 0;
				var this_first_pmt_amt = 0;
				// Monto original de los pagos
				var pmt_amt_old = $('#fpmt-1').attr('data-value');
				if( services_amt == 0 ){
					this_pmt_amt = ((parseFloat(order_total_net) - parseFloat(order_discount) ) / order_total_pmts).toFixed(2);
					this_first_pmt_amt = (parseFloat(this_pmt_amt) + parseFloat(total_taxes) + parseFloat(order_shipping)).toFixed(2);
					$('#span_order_first_pmt').attr('data-amt', this_pmt_amt);
				}else{
					this_pmt_amt = ((parseFloat(order_total_net) - parseFloat(order_discount) - parseFloat(services_amt)) / order_total_pmts).toFixed(2);
					this_first_pmt_amt = (parseFloat(this_pmt_amt) + parseFloat(total_taxes) + parseFloat(order_shipping)).toFixed(2);
				}
				this_first_pmt_amt = parseFloat(this_first_pmt_amt) + parseFloat(services_amt) ;

				// Se suman todos los montos de los pagos para cuadrar el monto total a pagar
				// -> si existe diferencia de centavos, se lo ajusta al primer pago
				var this_sum_pmts_amt = (parseFloat(pmt_amt_old) * (order_total_pmts - 1)).toFixed(2);
				this_sum_pmts_amt = parseFloat(this_sum_pmts_amt) + parseFloat(this_first_pmt_amt);
				var this_diff = total - this_sum_pmts_amt;
				//console.log(total+' - '+this_sum_pmts_amt+' -> '+pmt_amt_old);
				if( this_diff > 0 && this_diff < 1 ){// Solo centavos
					this_first_pmt_amt = parseFloat(this_first_pmt_amt) + parseFloat(this_diff);
				}else if( this_diff < 0 && Math.abs(this_diff) < 1 ){
					this_first_pmt_amt = parseFloat(this_first_pmt_amt) - Math.abs(this_diff);
				}
				
				$('#span_order_first_pmt').html( format_price(this_first_pmt_amt) );
				*/
				$('#span_order_first_pmt').html( format_price(order_total) );
			}else if( order_total_pmts == 1 ){
				$('#span_order_first_pmt').html( format_price(order_total) );
			}
		}

		if( $('#products').length ){			
			$('#products').val( products_from_shop_cart() );
		}

		// Muestra u oculta el boton: Crear Orden
		if( shop_cart_items.length > 0 && $('#frm_sales_step2').length ){
			$('#submit_shop_cart').css('display', 'block');
		}else{
			$('#submit_shop_cart').css('display', 'none');
		}
	}

	if( $('#submit_shop_cart').length ){
		 $('#submit_shop_cart').click(function(event) {
		 	$('#frm_sales_step2').submit();
		 });
	}
	if( $('#frm_sales_step2').length ){
		$('#frm_sales_step2').submit(function(event) {
			submit_ok = true;

			var prod_list = '';
			for( var i=0; i<shop_cart_items.length; i++ ){
				prod_list += shop_cart_items[i][0]+',';
			}			
			$('#products').val(prod_list);

			$('#pay_type').val(order_pay_type);
		});
	}

	// Genera una cadena con todos los datos de los productos contenidos en el carro de compras
	function products_from_shop_cart(){
		var prod_list = '';

		for( var i=0; i<shop_cart_items.length; i++ ){
			// Se genera la cadena con los datos de los productos que contiene el carro de compras
			// Params-> ID del prod. principal  :  ID_sku_products        :          Precio         :        Impuestos		  :        Cantidad		    : prod. principal: 1 o 0  :   id_products_prices
			prod_list += shop_cart_items[i][0]+':'+shop_cart_items[i][1]+':'+shop_cart_items[i][3]+':'+shop_cart_items[i][4]+':'+shop_cart_items[i][5]+':'+shop_cart_items[i][6]+':'+shop_cart_items[i][7]+';';
		}	

		return prod_list;
	}


	/*
	 * ----------------------------------------------------------------
	 * Step 3 :: Dirección
	 * ----------------------------------------------------------------	
	 */
	// Validación de campos dentro del form
	if( $('#frm_sales_step3').length ){

		$('#birthday').datepicker({
			changeMonth: true,
      		changeYear: true,
      		dateFormat: 'yy-mm-dd',
      		yearRange: '1910:-18Y', // de 1910 hasta 18 años atras
      		maxDate: '-18Y', // 18 años atras
		});

		// Reglas de validacion del formulario
		$('#frm_sales_step3').validate({
	        rules:{   
	        	// Datos del cobro         
	            firstname: 'required',
	            lastname1: 'required',
	            lastname2: 'required',
	            address1: 'required',
	            address2: 'required',
	            address3: 'required',
	            urbanization: 'required',
	            city: 'required',
	            state: 'required',
	            zipcode: { 
	                required: true,
	                digits: true,
	                minlength: 5,
	            },
	            phone: { 
	                required: true,
	                digits: true,
	                minlength: 8, 
	            },
	            phone2: { 
	                digits: true,
	                minlength: 8, 
	            },
	            cellphone: { 
	                required: true,
	                digits: true,
	                minlength: 8, 
	            },
	            email: {
	            	required: {
	            		depends: function(element) {
	            			return ($('#contact_mode_email').is(':checked'));
	            		}
	            	},
	            	email: true,
	            },
	            birthday: {
	            	dateISO: true,
	            	maxbirthday_validate: true,
	            },
	            // Datos del envío
	            shp_name: 'required',
	            shp_address1: 'required',
	            shp_urbanization: 'required',
	            shp_city: 'required',
	            shp_state: 'required',
	            shp_zipcode: { 
	                required: true,
	                digits: true,
	                minlength: 5,
	            },
	            shp_address2: 'required',
	            shp_address3: 'required',
	    	},
	    	messages:{   		
	            firstname: '<span class="ValidateError"></span>',
	            lastname1: '<span class="ValidateError"></span>',
	            lastname2: '<span class="ValidateError"></span>',
	            address1: '<span class="ValidateError"></span>',
	            address2: '<span class="ValidateError"></span>',
	            address3: '<span class="ValidateError"></span>',
	            urbanization: '<span class="ValidateError"></span>',
	            city: '<span class="ValidateError"></span>',
	            state: '<span class="ValidateError"></span>',	            
	            zipcode: {
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>'
	            },
	            phone: {
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',  
	                minlength: '<span class="ValidateError"></span>'  
	            },
	            phone2: { 
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>',
	            },
	            cellphone: { 
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>',
	            },
	            email: {
	            	required: '<span class="ValidateError"></span>',
	            	email: '<span class="ValidateError"></span>',
	            },
	            birthday: {
	            	dateISO: '<span class="ValidateError"></span>',
	            	maxbirthday_validate: '<span class="ValidateError"></span>',
	            },
	            shp_name: '<span class="ValidateError"></span>',
	            shp_address1: '<span class="ValidateError"></span>',
	            shp_urbanization: '<span class="ValidateError"></span>',
	            shp_city: '<span class="ValidateError"></span>',
	            shp_state: '<span class="ValidateError"></span>',
	            shp_zipcode: { 
	                required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>',
	            },
	            shp_address2: '<span class="ValidateError"></span>',
	            shp_address3: '<span class="ValidateError"></span>',
	    	},
	    	errorClass: "help-inline",
	    	errorElement: "span",
	    	highlight:function(element, errorClass, validClass) {
	            $(element).parents('.line').removeClass('success').addClass('val_error');
	    	},
	    	unhighlight: function(element, errorClass, validClass) {
	    		$(element).parents('.line').removeClass('val_error').addClass('val_success');
	    	},
	    	invalidHandler: function(form, validator) {
		        if( submit_toback ){
		        	validator.resetForm();
		        	$(form).submit();
		        }
		    }
	    });
		jQuery.validator.addMethod("maxbirthday_validate", function(value, element) {
			var current_birthday = value.replace(/-/g, '');
			if( parseInt(current_birthday) > parseInt($('#max_birthday').val()) ){
				return false;
			}
			return true;
		}, '<span class="ValidateError"></span>');
		// Convertir a mayusculas
		$('#firstname').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#lastname1').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#lastname2').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#shp_name').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#address1').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#address2').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#address3').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#shp_address1').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#shp_address2').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#shp_address3').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#shp_address1').blur(function(){ $(this).val($(this).val().toUpperCase()); });
		$('#email').blur(function(){ $(this).val($(this).val().toLowerCase()); });
		
		// Copia el mismo número de tel. del CID
		$('#samephone').click(function(event) {
			$('#phone').val( $(this).attr('data-value') );
			return false;
		});

		// Controla el submit del form
	    $('#btn_submit').click(function(event){
	    	var valida_extra = true;
	    	// Validacion adicional
	    	if( !$('input[name=sex]').is(':checked') ){
	    		$('#error_sex').html('Required');
	    		valida_extra = false;
	    	}else{
	    		$('#error_sex').html('');
	    	}
	    	if( !$('input[name=contact_mode]').is(':checked') ){
	    		$('#error_contact_mode').html('Required');
	    		valida_extra = false;
	    	}else{
	    		$('#error_contact_mode').html('');
	    	}
	    	if( !$('input[name=atime]').is(':checked') ){
	    		$('#error_atime').html('Required');
	    		valida_extra = false;
	    	}else{
	    		$('#error_atime').html('');
	    	}

			var valida = $('#frm_sales_step3').validate().form();
			if( valida && valida_extra ){
				localStorage.setItem('step3_complete', '1');
				$('#full_data').val('1');

				var this_free_shp = (localStorage.getItem('free_shp') != undefined && localStorage.getItem('free_shp') == '1') ? 1 : 0;
				if( order_shp_type != 2 && $('#products_express_delivery').val() == 'Yes' && $('#zones_express_delivery').val() == 'Yes' && this_free_shp == 0 ){
					$('#div_express_delivery').dialog('open');
				}else{					
					$('#frm_sales_step3').submit();
				}
			}else{
				localStorage.setItem('step3_complete', '0');
			}
		});

		$('#frm_sales_step3').submit(function(event) {
			if( submit_toback )
				return true;

			if( order_pay_type != 'Credit-Card' ){
				if( shop_cart_items.length > 0 ){
					$('#step').val('5');
								
					$('#products').val( products_from_shop_cart() );

					$('#pay_type').val(order_pay_type);
					$('#shipping').val(order_shipping);
					$('#shp_type').val(order_shp_type);
				}else{

				}
			}
			$('#total_pmts').val(order_total_pmts);

			submit_ok = true;
		});

		// Funcionalidad del Envío Express
		$('#div_express_delivery').dialog({
			autoOpen: false,
		    height: 300,
		    width: 500,
		    modal: true,
		    buttons: {
		    	'Si, por favor': function(){
		    		var cost_shp_express = ( $('#cost_shp_express').val() != '' ) ? $('#cost_shp_express').val() : 0;
		    		// Cambia a envio express
		    		if( cost_shp_express > 0 ){
			    		order_shp_type = 2;
			    		order_shipping = $('#cost_shp_express').val();
			    		save_sessionStorage();
			    	}else{
			    		build_dialog("No se ha difinido el costo de envío express !!!", 'warning');
			    		dialog_form.dialog({
			    			buttons: {
			    				'Aceptar': function(){
			    					$(this).dialog('close');
			    				}
			    			}
			    		});
			    	}

		    		$('#frm_sales_step3').submit();
		    	},
		    	'No, gracias': function(){
		    		$('#frm_sales_step3').submit();	    		
		    	}
		    },
		    open: function(){

		    }
		});

		// Funcionalidad para la copia de info. de cobro a info de envío
		if( $('#lnk_address_copy').length ){

			$('#lnk_address_copy').click(function(event){
				$('#shp_name').val( $('#firstname').val()+' '+$('#lastname1').val()+' '+$('#lastname2').val() );
				// Si el CP del cliente es diferente al CP de envío y además hay productos en el carrito de compras
				if( $('#zipcode').val() != $('#shp_zipcode').val() && $('#shp_zipcode').val().length == 5 && shop_cart_items.length > 0 ){
					
					// Se genera el listado de productos del carro de compras
					// para validar la disponibilidad del cod. postal
					var prod_list = '';
					for( var i=0; i<shop_cart_items.length; i++ ){
						//				id_products			:	id_products_prices
						prod_list += shop_cart_items[i][0]+':'+shop_cart_items[i][8]+',';
					}
					prod_list = prod_list.substr(0, (prod_list.length - 1));

					// Se valida la disponibilidad de los productos
					$.ajax({
						url: '/cgi-bin/common/apps/ajaxbuild',
						type: 'post',
						dataType: 'json',
						async: false,
						data: {
							'ajaxbuild': 'sales_zipcode_products_available',
							'zipcode': $('#zipcode').val(),
							'pay_type': order_pay_type,
							'total_pmts': order_total_pmts,
							'products': prod_list,

						},
						beforeSend: function(){						
						},
						success: function(xresponse){
							// Se pasa el control para que muestre el mensaje correspondiente o asigne los valores				
							validate_sch_zipcode({
								'available': xresponse.available,
								'products_list': xresponse.products_list,
								'express_delivery': xresponse.express_delivery,
								'state': $('#state').val(),
								'city': $('#city').val(),
								'urbanization': $('#urbanization').val(),
								'zipcode': $('#zipcode').val(),
								'address1': $('#address1').val(),
								'address2': $('#address2').val(),
								'address3': $('#address3').val(),
							});
						}
					});
				// Solo se copian los datos
				}else{
					$('#shp_address1').val( $('#address1').val() );
					$('#shp_zipcode').val( $('#zipcode').val() );
					$('#shp_urbanization').val( $('#urbanization').val() );
					$('#shp_city').val( $('#city').val() );
					$('#shp_state').val( $('#state').val() );
					$('#shp_address2').val( $('#address2').val() );
					$('#shp_address3').val( $('#address3').val() );	
				}

				return false;
			});
		}

		// Cuenta la cantidad de caracteres de la nota
		if( $('#shp_notes').length ){
			$('#shp_notes').keyup(function(event) {
				$('#div_count_shp_notes').html( $(this).val().length + ' caracteres' );
			});
			$('#div_count_shp_notes').html( $('#shp_notes').val().length + ' caracteres' );
		}
	}

	
	/*
	 * ----------------------------------------------------------------
	 * Step 4 :: Pago
	 * ----------------------------------------------------------------	
	 */

	var shop_cart_items2 = []; // Contendrá los productos que estaban en el carro de compras antes del cambio en la forma de pago
	if( localStorage.getItem('order_pay_type') == 'Credit-Card' ){
		$('#div_credit_card').css('display', 'block');
	}else if( localStorage.getItem('order_pay_type') == 'Referenced Deposit' ){
		$('#div_referenced_deposit').css('display', 'block');
	}else if( localStorage.getItem('order_pay_type') == 'COD' ){
		$('#div_cod').css('display', 'block');
	}

	// Validación de campos dentro del form
	if( $('#frm_sales_step4').length ){

		if(  $('#div_credit_card').is(':visible') ){
			// Contenido del Speech
			$('#speech_text_cc').css('display', 'block');
			$('#speech_text_other').css('display', 'none');

			// Reglas de validacion del formulario
			$('#frm_sales_step4').validate({
		        rules:{ 
		        	pmtfield7_Debit: {
		        		type_card: true,
		        	},
		        	pmtfield7_Credit: {
		        		type_card: true,
		        	},
		            pmtfield2:{
		                required: true,	                
		                minlength: 7,
		            },		            
		            pmtfield3:{ 
		                required: true,
		                digits: true,
		                minlength: 15,
		            },
		            month: 'required',
		            year: 'required',
		            pmtfield5:{
		            	required: true,
		            	digits: true,
		            	minlength: 3,
		            	//validate_cvn: true,
		            },
		            pmtfield6:{ 
		                digits: true,
		                minlength: 8,
		            },
		    	},
		    	messages:{
		            pmtfield7_Debit: {
		        		type_card: '<span class="ValidateError">Required</span>',
		        	},
		        	pmtfield7_Credit: {
		        		type_card: '<span class="ValidateError">Required</span>',
		        	},		        		        	
		            pmtfield2:{
		                required: '<span class="ValidateError"></span>',
		                minlength: '<span class="ValidateError"></span>',
		            },
		            pmtfield3:{ 
		                required: '<span class="ValidateError"></span>',
		                digits: '<span class="ValidateError"></span>',
		                minlength: '<span class="ValidateError"></span>',
		            },
		            month: '<span class="ValidateError"></span>',
		            year: '<span class="ValidateError"></span>',
		            pmtfield5: {
		            	required: '<span class="ValidateError"></span>',
		                digits: '<span class="ValidateError"></span>',
		                minlength: '<span class="ValidateError"></span>',
		                //validate_cvn: '<span class="ValidateError"></span>',
		            },
		            pmtfield6:{ 
		                digits: '<span class="ValidateError"></span>',
		                minlength: '<span class="ValidateError"></span>',
		            },
		    	},
		    	errorClass: "help-inline",
		    	errorElement: "span",
		    	highlight:function(element, errorClass, validClass) {
		            $(element).parents('.line').removeClass('success').addClass('val_error');
		    	},
		    	unhighlight: function(element, errorClass, validClass) {
		    		$(element).parents('.line').removeClass('val_error').addClass('val_success');
		    	},
		    	invalidHandler: function(form, validator) {
			        if( submit_toback ){
			        	validator.resetForm();
			        	$(form).submit();
			        }
			    }
		    });
			/*
			jQuery.validator.addMethod("validate_cvn", function(value, element) {
				if( value.length < 4 && ($('#pmtfield1').val() == 'American Express' || $('#pmtfield1').val() == '') ){
					return false;
				}else if( value.length == 4 && ($('#pmtfield1').val() == 'Visa' || $('#pmtfield1').val() == 'Mastercard') ){
					return false;
				}

				return true;
			});
			*/			
			
			// Convertir a mayusculas
			$('#pmtfield2').blur(function(){ $(this).val($(this).val().toUpperCase()); });
			// Copiar el nombre del cliente
			$('#samecustomer').click(function(event) {
				$('#pmtfield2').val( $('#customer_name').val() );
				return false;
			});
			/*
			// Se valida la tarjeta
			$('#pmtfield3').keyup(function(event){ 
				if( validate_key(event) && $(this).val().length >= 15 ){
					var type_cc = mod10( $(this).val() );
					switch(type_cc){
						case 'American Express': 
							$('#pmtfield1').val(type_cc);
							$('#div_img_pmtfield1').html('<img src="/sitimages/sales/amex.png" border="0" alt="American Express" title="American Express" style="vertical-align: middle;">');
						break;
						case 'Visa':
							$('#pmtfield1').val(type_cc);
							$('#div_img_pmtfield1').html('<img src="/sitimages/sales/visa.png" border="0" alt="Visa" title="Visa" style="vertical-align: middle;">');
						break;
						case 'Mastercard':
							$('#pmtfield1').val(type_cc);
							$('#div_img_pmtfield1').html('<img src="/sitimages/sales/mastercard.png" border="0" alt="Mastercard" title="Mastercard" style="vertical-align: middle;">');
						break;
						default:
							$('#pmtfield1').val('');
							$('#div_img_pmtfield1').html('<span style="color: #b40404;">Invalid</span>');
					}
				}else if( validate_key(event) && $('#pmtfield1').val() != '' ){
					$('#pmtfield1').val('');
					$('#div_img_pmtfield1').html('');
				}
			});
			$('#pmtfield3').keyup();

			$('#pmtfield5').blur(function(event) {
				
			});
			*/
			if( $('#pmtfield1').val() != '' ){
				switch($('#pmtfield1').val()){
					case 'American Express': 
						$('#div_img_pmtfield1').html('<img src="/sitimages/sales/amex.png" border="0" alt="American Express" title="American Express" style="vertical-align: middle;">');
					break;
					case 'Visa':
						$('#div_img_pmtfield1').html('<img src="/sitimages/sales/visa.png" border="0" alt="Visa" title="Visa" style="vertical-align: middle;">');
					break;
					case 'Mastercard':
						$('#div_img_pmtfield1').html('<img src="/sitimages/sales/mastercard.png" border="0" alt="Mastercard" title="Mastercard" style="vertical-align: middle;">');
					break;					
				}
			}

			// Copiar el nombre del cliente
			$('#samephone').click(function(event) {
				$('#pmtfield6').val( $('#phone').val() );
				return false;
			});
		}else{
			// Contenido del Speech
			$('#speech_text_cc').css('display', 'none');
			$('#speech_text_other').css('display', 'block');
		}

		// Controla el cambio en la forma de pago
		if( $('.lnk_pay_type_chg').length ){
			$('.lnk_pay_type_chg').click(function(event) {

				build_dialog('&iquest;Est&aacute; seguro que desea cambiar el tipo de pago de la orden?', 'confirm');
				dialog_form.dialog({
					buttons: {
						'Si, estoy seguro': function(){
							pay_type_change();
						},
						'No, esperar': function(){
							$(this).dialog('close');
						}
					}
				});
				
			});
		}

		// Controla el submit del form
	    $('#btn_submit').click(function(event) {
	    	if( $('#div_credit_card').is(':visible') ){
	    		var valida_extra = true;
		    	// Validacion adicional
		    	if( !$('input[name=pmtfield7]').is(':checked') ){
		    		$('#error_pmtfield7').html('Required');
		    		valida_extra = false;
		    	}

		    	// Se valida la vigencia de la tarjeta
		    	/*
		    	if( validate_cc_exp() == 0 ){
		    		$('#error_exp_cc').html('Invalid');
		    		valida_extra = false;
		    	}
		    	*/
		    	valida_extra = validate_cc();

		    	// Se valida el tipo de tarjeta
		    	if( $('#pmtfield1').val() == '' ){
		    		valida_extra = false;
		    	}

		    	// Se valida el formulario con los datos de la tarjeta
				var valida = $('#frm_sales_step4').validate().form();

				if( valida && valida_extra ){
					$('#frm_sales_step4').submit();
				}
			}else{
				$('#frm_sales_step4').submit();
			}
		});

		$('#frm_sales_step4').submit(function(event) {
			if( !submit_toback ){
				// Se valida el paso anterior
				var step3_ok = true;
				if( localStorage.getItem('step3_complete') == undefined || localStorage.getItem('step3_complete') == '0' ){
					step3_ok = false;
				}

				if( $('#full_data').val() == '1' && shop_cart_items.length > 0 && step3_ok ){
					submit_ok = true;

					$('#products').val( products_from_shop_cart() );

					$('#pay_type').val(order_pay_type);
					$('#total_pmts').val(order_total_pmts);
					$('#shipping').val(order_shipping);
					$('#shp_type').val(order_shp_type);

				}else{
					var url_go = '/cgi-bin/mod/sales/admin?cmd='+$('#cmd').val()+'&step=3';
					if( !step3_ok ){
						build_dialog('Faltan algunos datos de la direcci&oacute;n del cliente!, por favor compl&eacute;telos para poder continuar', 'warning');
					}else if( shop_cart_items.length <= 0 ){
						build_dialog('El carrito de compras est&aacute; vac&iacute;o, por favor agregue productos para poder continuar', 'warning');
						url_go = '/cgi-bin/mod/sales/admin?cmd='+$('#cmd').val()+'&step=2';
					}
					dialog_form.dialog({
						buttons: {
							'Ir al paso anterior': function(){
								submit_ok = true;
								location.href = url_go;
							},
							'Cancelar': function(){
								$(this).dialog('close');
							}
						}
					});
					return false;
				}
			}
		});

		function validate_cc(){
			var result = true;

			if( $('#pmtfield3').val().length > 14 && $('#month').val() != '' && $('#year').val() != '' && $('#pmtfield5').val().length > 2 ){
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'post',
					dataType: 'json',
					data: {
						'cmd': 'ajax_validate_cc',
						'param': $('#month').val()+$('#year').val()+$('#pmtfield3').val()+$('#pmtfield5').val(),
						'total_pmts': order_total_pmts,
						'lgth': $('#pmtfield3').val().length,
					},
					async: false,
					cache: false,
					beforeSend: function(){
						$('#div_img_pmtfield1').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">');
						$('#error_exp_cc').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">');
						$('#error_pmtfield5').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">');
					},
					success: function(xresponse){
						$('#div_img_pmtfield1').html('');
						$('#error_exp_cc').html('');
						$('#error_pmtfield5').html('');

						// Resultado del núm. de tarjeta
						if( xresponse.pmtfield3.result == 'Invalid' ){
							$('#div_img_pmtfield1').html('<span style="color: #b40404;">Invalid</span>');
							result = false;
						}else if( xresponse.pmtfield3.result != 'Invalid' ){
							switch(xresponse.pmtfield3.network){
								case 'American Express': 
									$('#pmtfield1').val(xresponse.pmtfield3.network);
									$('#div_img_pmtfield1').html('<img src="/sitimages/sales/amex.png" border="0" alt="American Express" title="American Express" style="vertical-align: middle;">');
								break;
								case 'Visa':
									$('#pmtfield1').val(xresponse.pmtfield3.network);
									$('#div_img_pmtfield1').html('<img src="/sitimages/sales/visa.png" border="0" alt="Visa" title="Visa" style="vertical-align: middle;">');
								break;
								case 'Mastercard':
									$('#pmtfield1').val(xresponse.pmtfield3.network);
									$('#div_img_pmtfield1').html('<img src="/sitimages/sales/mastercard.png" border="0" alt="Mastercard" title="Mastercard" style="vertical-align: middle;">');
								break;
								default:
									$('#pmtfield1').val('');
									$('#div_img_pmtfield1').html('<span style="color: #b40404;">Invalid</span>');
									result = false;
							}
						}
						// Resultado de la fecha			
						if( xresponse.pmtfield4.result == 'Invalid' ){
							$('#error_exp_cc').html('<span style="color: #b40404;">Invalid</span>');
							result = false;
						}
						// Resultado del CVN
						if( xresponse.pmtfield5.result == 'Invalid' ){
							$('#error_pmtfield5').html('<span style="color: #b40404;">Invalid</span>');
							result = false;
						}

					},
					error: function(objeto, detalle, otroobj){
						result = false;

						$('#div_img_pmtfield1').html('');
						$('#error_exp_cc').html('');
						$('#error_pmtfield5').html('');

						build_dialog(detalle.toUpperCase()+' :: '+otroobj, 'error');
						dialog_form.dialog({ 
							closeOnEscape: false,
							buttons: {
								'Aceptar': function(){
									$(this).dialog('close');
								}
							}
						});
			        }
				});
			}else{
				result = false;
			}

			return result;
		}

		function validate_cc_exp(){
			var result = 0;
			$.ajax({
				url: '/cgi-bin/mod/sales/admin',
				type: 'post',
				dataType: 'json',
				data: {
					'cmd': 'ajax_validate_exp_cc',
					'date_cc': $('#month').val()+$('#year').val(),
					'total_pmts': order_total_pmts,
				},
				async: false,
				cache: false,
				beforeSend: function(){
					$('#error_exp_cc').html('<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">');
				},
				success: function(xresponse){
					$('#error_exp_cc').html('');
					
					result = xresponse.result;
					if( result == 0 ){
						build_dialog('Vencimiento inv&aacute;lido, la fecha de vencimiento de la tarjeta debe ser al menos '+xresponse.prevent_days+' d&iacute;as despu&eacute;s de la &uacute;ltima cuota('+xresponse.last_date_pay+').', 'error');
						dialog_form.dialog({
							buttons: {							
								'Cerrar': function(){
									$(this).dialog('close');
								}
							}
						});
					}
				},
			});

			return result;
		}
	}
	/* 
	 * Funcion para el control del cambio de la forma de pago
	 */
	function pay_type_change(){
		if( shop_cart_items.length > 0 ){
			shop_cart_items2.length = 0;
			for( var i=0; i<shop_cart_items.length;  i++ ){
				shop_cart_items2.push([shop_cart_items[i][0], shop_cart_items[i][1], shop_cart_items[i][2], shop_cart_items[i][3], shop_cart_items[i][4], shop_cart_items[i][5], shop_cart_items[i][6], shop_cart_items[i][7], shop_cart_items[i][8], shop_cart_items[i][9]]);
			}// fin for()			
			// Se eliminan los datos del array del carro de compras
			shop_cart_items.length = 0;
			// Se reinicia el tipo de pago
			order_pay_type = '';
			// Se reinicia el costo del envio
			order_shipping = 0;
			// Se reinicia el tipo de envio
			order_shp_type = 1;
			// Se reinicial el total de pagos
			order_total_pmts = '';
			// Se guardan los cambios en el localStorage
			save_sessionStorage();

			// Si el paso actual no es el de Productos
			if( $('#step').val() != '3' ){
				// Se crea una bandera para realizar la búsqueda de los productos que contenia el carro de compras
				localStorage.setItem('reset_shop_cart', '1');

				var current_step = parseInt($('#step').val()) - 1;

				submit_ok = true;
				$('#step').val('2');
				location.href = '/cgi-bin/mod/sales/admin?cmd='+$('#cmd').val()+'&step=2&rst_pay_type=1';				
			}
		}
	}// fin de la función pay_type_change


	/*
	 * ----------------------------------------------------------------
	 * Step 5 ::  Confirmar
	 * ----------------------------------------------------------------	
	 */
	var coupon_id = 0;
	var coupon_disc = 0;
	var coupon_disc_type;
	var coupon_min_amt = 0;
	var coupon_applied = 'Net';
	if( $('#frm_sales_step5').length ){
		if( localStorage.getItem('order_pay_type') == 'Credit-Card' ){
			$('#div_credit_card').css('display', 'block');
		}

		$('#span_order_pay_type').html(localStorage.getItem('order_pay_type') + ' a ' + localStorage.getItem('order_total_pmts') + ' PAGO(S)');

		//--------------------------------------------//
		// Funcionalidad para la eleccion de los tipos de envios
		//--------------------------------------------//
		$('#td_delivery_opts').on('click', '.lnk_delivery_types_off', function(event) {
			var this_obj = $(this);

			var new_shipping = (this_obj.attr('data-cost') != '') ? parseFloat(this_obj.attr('data-cost')) : 0;
			order_shp_type = this_obj.attr('data-type');

			var this_free_shp = (localStorage.getItem('free_shp') != undefined && localStorage.getItem('free_shp') == '1') ? 1 : 0;
			if( this_free_shp == 0 || order_shp_type == 2 ){
				order_shipping = new_shipping;
				//localStorage.setItem('free_shp', 0);
			}else if( this_free_shp == 1 ){
				order_shipping = 0;
			}
			shop_cart_totals();

			// Se busca la opcion que tenga actualmente la clase "lnk_delivery_types_on"
			$('.lnk_delivery_types_on').removeClass('lnk_delivery_types_on').addClass('lnk_delivery_types_off');
			this_obj.removeClass('lnk_delivery_types_off').addClass('lnk_delivery_types_on');

			save_sessionStorage();

			return false;
		});

		//--------------------------------------------//
		// Funcionalidad del Cupon de descuento
		//--------------------------------------------//
		$('#div_coupon_info').dialog({
			autoOpen: false,
		    height: 410,
		    width: 500,
		    modal: true,
		    buttons: {
		    	'Aplicar': function(){
		    		$(this).dialog('close');

		    		if( coupon_id > 0 && order_coupon != $('#coupon').val() ){
			    		//------------------------------------//
			    		// Se aplica el descuento			    		
		    			var this_disc_amt = 0;
	    				if( coupon_applied == 'Net' ){
	    					if( coupon_disc_type == '%' ){
		    					this_disc_amt = (parseFloat(coupon_disc) / 100) * parseFloat(order_total_net);
		    					this_disc_amt = this_disc_amt.toFixed(2);
		    				}else{
		    					this_disc_amt = (parseFloat(order_total_net) >= parseFloat(coupon_disc)) ? coupon_disc : order_total_net;
		    				}
	    				}else{
	    					var this_order_total = parseFloat(order_total) - (parseFloat(order_shipping) * (1+parseFloat(order_taxes_pct)));	    					
	    					if( coupon_disc_type == '%' ){		    					
		    					this_disc_amt = (parseFloat(coupon_disc) / 100) * parseFloat(this_order_total);
		    					this_disc_amt = this_disc_amt.toFixed(2);
		    				}else{
		    					this_disc_amt = (parseFloat(order_total) >= parseFloat(coupon_disc)) ? coupon_disc : order_total;
		    				}
		    				this_disc_amt = this_disc_amt / (1+parseFloat(order_taxes_pct));
	    				}

	    				// Se asignan los valores de descuento/cupon a la variables globales
	    				order_discount = this_disc_amt;
	    				order_coupon = $('#coupon').val();

	    				localStorage.setItem('coupon_disc_type', coupon_disc_type);
	    				localStorage.setItem('coupon_applied', coupon_applied);
	    				localStorage.setItem('coupon_disc', coupon_disc);

	    				// Se restringe la edición del cupon
	    				$('#coupon').attr('readonly', true);
	    				$('#lnk_drop_discount').css('display', 'inline-block');
		    			//--------------------------------------//

		    			// Se actualiza el desglose de los pagos
		    			/*
		    			$.ajax({
							url: '/cgi-bin/mod/sales/admin',
							type: 'post',			
							dataType: 'json',
							async: false,
							cache: false,
							data: {
								'cmd': 'ajax_pays_list',
								'coupon': order_coupon,
							},
							success: function(xresponse){
								$('#td_order_pays_list').html(xresponse.html_pmts);
							}
						});	
						*/
						// Se realiza el recálculo de la orden
			    		shop_cart_totals();
	    				// Se guardan los datos en la sesión
	    				save_sessionStorage();

		    		}else{
		    			build_dialog("El cupon no es aplicable o ya se aplico!!", 'warning');
		    			dialog_form.dialog({
			    			buttons: {
			    				'Aceptar': function(){
			    					$(this).dialog('close');
			    				}
			    			}
			    		});
		    		}
		    	},
		    	'Cancelar': function(){
		    		$('#coupon').val('');
		    		$(this).dialog('close');
		    	}
		    },
		    open: function(){

		    }
		});
		if( $('#check_coupon').length ){
			$('#check_coupon').click(function(event) {
				$.ajax({
					url: '/cgi-bin/common/apps/ajaxbuild',
					type: 'get',			
					dataType: 'json',
					data: {
						'ajaxbuild': 'sales_info_coupon',
						'coupon': $('#coupon').val(),
					},
					beforeSend: function(){
						var html_loading = '<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative; z-index: 10;">';
						$('#div_loading_coupon').html(html_loading);						
					},
					success: function(xresponse){
						$('#div_loading_coupon').html('');

						$('#div_coupon_info').html(xresponse.html);
						$('#div_coupon_info').dialog('open');

						if( xresponse.status.toLowerCase() == 'valid' ){
							coupon_id		= xresponse.id_coupon;
							coupon_disc		= xresponse.discount;
							coupon_disc_type= xresponse.discount_type;
							coupon_min_amt	= xresponse.min_amount;
							coupon_applied	= ( xresponse.applied != null ) ? xresponse.applied : 'Net';
						}else{
							$('#coupon').val('');
						}
					}
				});				
			});
		}
		if( $('#coupon').val() != '' && parseFloat(localStorage.getItem('order_discount')) > 0 ){
			$('#coupon').attr('readonly', true);
		}else if( localStorage.getItem('order_coupon') != '' && localStorage.getItem('order_coupon') != undefined ){
			$('#coupon').val(localStorage.getItem('order_coupon'));
			$('#coupon').attr('readonly', true);
		}
		if( parseFloat(localStorage.getItem('order_discount')) == 0 ){
			$('#lnk_drop_discount').css('display', 'none');
		}
		// Eliminar el descuento
		$('#lnk_drop_discount').click(function(event) {			
			order_discount = 0;
			order_coupon = '';
			coupon_id = 0;
			coupon_disc = 0;
			coupon_disc_type = '';
			coupon_min_amt = 0;
			coupon_applied = '';
			localStorage.removeItem('order_coupon');
			localStorage.removeItem('coupon_id');
			localStorage.removeItem('coupon_disc');
			localStorage.removeItem('coupon_disc_type');
			localStorage.removeItem('coupon_applied');

			$('#coupon').val('');
			$('#coupon').attr('readonly', false);


			$(this).css('display', 'none');
			//borra los datos de la session referentes al descuento
			if( order_pay_type == 'Credit-Card' && order_total_pmts > 1 ){
				// Se actualiza el desglose de pagos
				/*
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'post',
					dataType: 'json',
					async: false,
					cache: false,
					data: {
						'cmd': 'ajax_pays_list',
						'coupon': order_coupon,
					},
					success: function(xresponse){
						$('#td_order_pays_list').html(xresponse.html_pmts);
					}
				});
				*/
			}else{
				$.post('/cgi-bin/mod/sales/admin', {'cmd':'ajax_clear_discount'}, function(response,status,xhr){});
			}

			// Se realiza el recálculo de la orden
    		shop_cart_totals();
			// Se guardan los datos en la sesión
			save_sessionStorage();

			return false;
		});

		//--------------------------------------------//
		// Funcionalidad de la Posfecha
		//--------------------------------------------//
		$('#txtPostdate').datepicker({
			changeMonth: true,
      		changeYear: true,
      		dateFormat: 'yy-mm-dd',
      		minDate: '+1D',
      		maxDate: '+15D'
		});
		$('#div_postdate').dialog({
			autoOpen: false,
		    height: 180,
		    width: 400,
		    modal: true,
		    open: function(){
		    	if( order_pay_type == 'COD' ){
		    		$(this).dialog('option', 'title', 'Direksys :: Reprogramar');
		    	}else{
		    		$(this).dialog('option', 'title', 'Direksys :: Posfechar');
		    	}
		    },
		    buttons: {
		    	'Aceptar': function(){
		    		posfechar();
		    	},
		    	'Cancelar': function(){
		    		$(this).dialog('close');
		    	}
		    }
		});
		$('#lnk_postdate').click(function(event) {
			$('#div_postdate').dialog('open');
			return false;
		});
		$('#table_products_list').on('click', '.lnk_drop_services', function(){
			shop_cart_del({
				'oper': 'del', 
				'obj': $(this),
			});
			// Si el servicio era la posfecha
			if( $(this).attr('data-id') == '1001' ){
				$('#postdate').val('No');
				$('#postdate_date').val('');
				$('#txtPostdate').val('');
				localStorage.setItem('postdate', 'No');
				localStorage.removeItem('postdate_date');
			}
			
			var parent = $(this).parent('td').parent('tr');
  			$(parent).remove();

  			// Se actualiza el listado de productos en la sesion
  			var this_products = products_from_shop_cart();
			$.post('/cgi-bin/mod/sales/admin', {'cmd':'ajax_set_shop_cart_products', 'products': this_products}, function(response,status,xhr){});

			return false;
		});

		//--------------------------------------------//
		// Funcionalidad para agregar servicios
		//--------------------------------------------//
		$('#div_services').dialog({
			autoOpen: false,
		    height: 500,
		    width: 900,
		    modal: true,
		    buttons: {		    	
		    	'Cerrar': function(){
		    		$(this).dialog('close');
		    	}
		    },
		    open: function(){
		    	get_services();
		    }
		});
		$('#lnk_addservices').click(function(event) {
			$('#div_services').dialog('open');
			return false;
		});
		$('#table_services tbody').on('click', '.lnk_services_rslt', function(){
			var this_obj = $(this);
			
			add_services({
				'id': this_obj.attr('data-id'),
				'name': this_obj.attr('data-name'),
				'qty': 1,
				'price': this_obj.attr('data-price'),
				'tax_pct': this_obj.attr('data-tax_pct'),
			});

			$('#div_services').dialog('close');

			return false;
		});

		//--------------------------------------------//
		// Confirmar pedido
		//--------------------------------------------//
		if( $('#btn_submit').length ){	
			var order_confirm = false;
			$('#btn_submit').click(function(event) {
		    	build_dialog('&#191;Esta seguro de continuar?', 'confirm');
				dialog_form.dialog({
					buttons: {
						'Si, estoy seguro': function(){		
							$(this).dialog('close');
							order_confirm = true;
		    				$('#frm_sales_step5').submit();
						},
						'No, espera': function(){
							$(this).dialog('close');
						}
					}
				});
				
			});

			$('#frm_sales_step5').submit(function(event) {

				if( order_confirm ){					
					var dialog_wait = $('<div title="Direksys :: Processing">'+ loading('Procesando... por favor espere') +'</div>').dialog({
						minHeight: 100,
						minWidth: 450,
						modal: true,
						resisable: false,
						autoOpen: true,
						closeOnEscape: false,
						open: function(event, ui) { 
							$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
						}
					});
				}
				submit_ok = true;
		
				$('#products').val( products_from_shop_cart() );

				$('#pay_type').val(order_pay_type);
				$('#total_pmts').val(order_total_pmts);
				$('#shipping').val(order_shipping);
				$('#shp_type').val(order_shp_type);

				localStorage.setItem('order_status', 'InProcess');
				
			});
		}

		//--------------------------------------------//
		// Funciones adicionales de este paso
		//--------------------------------------------//
		function posfechar(){
			if( $('#txtPostdate').val() != '' ){
				var this_obj = $('#lnk_postdate');
				// Se valida que no exista el servicio en el carro de compras
				var not_exist = 1;
				for( var i=0; i<shop_cart_items.length; i++ ){
					if( shop_cart_items[i][0] == this_obj.attr('data-id') )
						not_exist = 0;
				}
				
				if( not_exist == 1 ){
					add_services({
						'id': this_obj.attr('data-id'),
						'name': this_obj.attr('data-name'),
						'qty': 1,
						'price': this_obj.attr('data-price'),
						'tax_pct': this_obj.attr('data-tax_pct'),
					});
				}
				var this_postdate_date = $('#txtPostdate').val();
				$('#postdate').val('Yes');
				$('#postdate_date').val( this_postdate_date );
				localStorage.setItem('postdate', 'Yes');
				localStorage.setItem('postdate_date', this_postdate_date);

				$('#div_postdate').dialog('close');
			}
		}

		// Obtiene via ajax el listado de servicios disponibles
		function get_services(){
			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'get',			
				dataType: 'json',
				data: {
					'ajaxbuild': 'sales_search_services',
					'txt_search': '',
				},
				beforeSend: function(){
					$('#table_services tbody').html( '<tr><td colspan="5">'+loading('Cargando el listado de Servicios... por favor espere')+'</td></tr>' );
				},
				success: function(xresponse){
					var html_rlst = '';
					if( xresponse.matches > 0 ){
						for( var i=0; i<xresponse.matches; i++ ){
							html_rlst += '<tr>';
							html_rlst += '	<td style="width: 15%; text-align: center;">';
							html_rlst += '		<a href="#" class="lnk_services_rslt" title="Agregar este servicio" ';
							html_rlst += '			data-id="'+xresponse.items[i].id_services+'" ';
							html_rlst += '			data-name="'+xresponse.items[i].name+'" ';
							html_rlst += '			data-type="'+xresponse.items[i].type+'" ';
							html_rlst += '			data-price="'+xresponse.items[i].price+'" ';
							html_rlst += '			data-tax_pct="'+xresponse.items[i].tax_pct+'" ';
							html_rlst += '		">'+xresponse.items[i].fid_services;
							html_rlst += '		</a>';
							html_rlst += '	</td>';
							html_rlst += '	<td style="width: 45%; text-align: left;">'+xresponse.items[i].name+'<br>'+xresponse.items[i].description+'</td>';
							html_rlst += '	<td style="width: 18%; text-align: left;">'+xresponse.items[i].type+'</td>';
							html_rlst += '	<td style="width: 10%; text-align: right;">'+format_price(parseFloat(xresponse.items[i].price).toFixed(2))+'</td>';
							html_rlst += '	<td style="width: 12%; text-align: right;">'+(xresponse.items[i].tax_pct * 100)+'%</td>';
							html_rlst += '<tr>';
						}
					}else{
						html_rlst += '<tr><td>Sin resultados...</td></tr>';
					}
					$('#table_services tbody').html(html_rlst);
				}
			});
		}

		function add_services(params){

			// Genera un random para el id de la promo
			var this_parent = get_random();

			// Se calcula el precio sin impuestos
			var this_price_net = (parseFloat(params.price) / (1+parseFloat(params.tax_pct))).toFixed(2);

			// Se genera el html y se agrega a la lista
			var html_serv = '';

			html_serv += '<tr>';
			html_serv += '	<td style="border-bottom: 1px solid silver;">&nbsp;</td>';
			html_serv += '	<td style="border-bottom: 1px solid silver; text-align: left;">';
			html_serv += '		<span style="font-size: 12pt;">'+params.name+'</span><br>';
			html_serv += '		<span style="display: inline-block; margin-bottom: 7px;">Service ID: '+params.id+'</span>';
			html_serv += '		<a href="#" id="lnk_drop-'+params.id+'-'+this_parent+'" data-id="'+params.id+'" data-parent="'+this_parent+'" class="lnk_drop_services" title="Cancelar este servicio"><img src="/sitimages/default/b_drop.png" alt="X" class="ico" style="border: none; height: 14px; width: 14px;"/></a>';
			html_serv += '	</td>';
			html_serv += '	<td style="border-bottom: 1px solid silver; text-align: center; vertical-align: top;">'+params.qty+'</td>';
			html_serv += '	<td style="border-bottom: 1px solid silver; text-align: right; vertical-align: top;">'+format_price( this_price_net )+'</td>';
			html_serv += '<tr>';

			$('#table_products_list').append(html_serv);

			// Se agrega al carro de compras
			shop_cart_add({
				'id_prod': params.id,
				'id_sku_prod': '60000'+params.id,
				'model': params.name,
				'price': params.price,
				'id_price': 0,
				'tax_pct': params.tax_pct,
				'pay_type': order_pay_type,
				'pmts': order_total_pmts,
				'main_prod': 1,
				'parent_prod': this_parent,
				'shipping': 0,
			});
			// Se calculan los totales y se guardan los datos en localStorage
			shop_cart_totals();
			save_sessionStorage();

			// Se actualiza el listado de productos en la sesion			
			var this_products = products_from_shop_cart();
			$.post('/cgi-bin/mod/sales/admin', {'cmd':'ajax_set_shop_cart_products', 'products': this_products}, function(response,status,xhr){});
		}

	}


	/*
	 * ----------------------------------------------------------------
	 * Step 6 ::  Info Extra
	 * ----------------------------------------------------------------	
	 */
	if( $('#frm_sales_step6').length ){
		// Se valida el reload de la página mientras se está procesando el cobro
		$(document).bind('keypress keydown keyup', function(event) {
			if( localStorage.getItem('payment_charge') == '1' && localStorage.getItem('payment_charge') != undefined ){
				if( event.which === 116 ){
					return false;
				}
				if( event.which === 82 && event.ctrlKey ){
					return false;
				}
			}
		});

		// Activa el paso actual
		$('#step6').removeClass('step_off').removeClass('step').addClass('step_on');

		// Función para realizar el cobro de la tarjeta
		function payment_charge(){

			if( localStorage.getItem('payment_charge') != '1' || localStorage.getItem('payment_charge') == undefined ){
				localStorage.setItem('payment_charge', '1');

				// Ventana de espera
				var dialog_wait = $('<div title="Direksys :: Processing">'+ loading('Procesando el cobro de la tarjeta... por favor espere') +'</div>').dialog({
					minHeight: 100,
					minWidth: 450,
					modal: true,
					resisable: false,
					autoOpen: true,
					closeOnEscape: false,
					open: function(event, ui) {
						$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
					}
				});
				// Ejecución del cobro
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'get',			
					dataType: 'json',
					data: {
						'cmd': 'ajax_payment_charge',
						'retries': localStorage.getItem('charge_count'),
					},
					beforeSend: function(){
						
					},
					success: function(xresponse){
						dialog_wait.dialog('close');
						console.log('Status -> '+xresponse.status+' :: Code -> '+xresponse.code+' :: Msg -> '+xresponse.msg+' :: AuthCode -> '+xresponse.auth_code);
						if( xresponse.code != null && xresponse.msg != null ){
							if( (xresponse.status.indexOf('OK') >= 0 && xresponse.code == '1') || xresponse.status == 'OK' || xresponse.msg.indexOf('Aprobada') >= 0){
								//-------------------------------------
								// OK
								//-------------------------------------
								$('#span_auth_code').html(xresponse.auth_code);

								localStorage.setItem('order_status', 'Processed');
								build_dialog('Felicidades !!! El cobro se realiz&oacute; exit&oacute;samente<br>C&oacute;digo de autorizaci&oacute;n: '+xresponse.auth_code+'<br>'+xresponse.msg, 'success');
								dialog_form.dialog({								
									buttons: {
										'Aceptar': function(){
											$(this).dialog('close');
										},
									}
								});
								//-------------------------------------
							}else{
								//-------------------------------------
								// Error
								//-------------------------------------
								var msg_extra = '';
								if( parseInt(localStorage.getItem('charge_count')) == 3 ){
									msg_extra = '<br /><br />Su orden no pudo ser cobrada en este momento, por este motivo le informo que usted recibir&aacute; una llamada de parte de nuestro departamento de Confirmaciones para intentar activar la orden y por consiguiente realizar el cobro';
									build_dialog('Error '+xresponse.code+' :: '+xresponse.msg+msg_extra, 'error');
									dialog_form.dialog({
										width: 550,
										closeOnEscape: false,
										open: function(event, ui) { 
											$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
										},
										buttons: {
											'Aceptar': function(){
												$(this).dialog('close');
											}
										}
									});
								// Error Timeout
								}else if( xresponse.status.indexOf('500') >= 0  ){
									msg_extra = '<br />Al parecer el servicio de cobro no está disponible en este momento, puedes:<br>&nbsp;&nbsp;&nbsp;- Reintentar el proceso<br>&nbsp;&nbsp;&nbsp;- Terminar el pedido e intentar el cobro mas tarde';
									build_dialog('Error '+xresponse.code+' :: '+xresponse.msg, 'error');
									dialog_form.dialog({
										closeOnEscape: false,
										open: function(event, ui) { 
											$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
										},
										buttons: {
											'Reintentar el cobro': function(){
												localStorage.removeItem('payment_charge');													
												payment_charge();
												$(this).dialog('close');
											},
											'Finalizar': function(){
												$(this).dialog('close');
											}
										}
									});
								// Cualquier otro error
								}else{
									build_dialog('Error '+xresponse.code+' :: '+xresponse.msg, 'error');
									dialog_form.dialog({
										closeOnEscape: false,
										open: function(event, ui) { 
											$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
										},
										buttons: {
											'Revisar datos del Pago': function(){
												$('#step').val('4');
												submit_ok = true;
												$('#frm_sales_step6').submit();
											}
										}
									});
								}
								//---------------------------------------
							}
						}else{
							//-------------------------------------
							// Error General
							//-------------------------------------
							build_dialog('Error :: '+xresponse.status, 'error');
							dialog_form.dialog({ 
								closeOnEscape: false,
								open: function(event, ui) { 
									$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
								},
								buttons: {
									'Revisar datos del Pago': function(){
										$('#step').val('4');
										submit_ok = true;
										$('#frm_sales_step6').submit();
									}
								}
							});
							//---------------------------------------
						}

						localStorage.removeItem('payment_charge');
					},
					error: function(objeto, detalle, otroobj){
						dialog_wait.dialog('close');
						build_dialog(detalle.toUpperCase()+' :: '+otroobj, 'error');
						dialog_form.dialog({ 
							closeOnEscape: false,
							open: function(event, ui) { 
								$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
							},
							buttons: {
								'Revisar datos del Pago': function(){
									$('#step').val('4');
									submit_ok = true;
									$('#frm_sales_step6').submit();
								},
								'Finalizar': function(){
									$(this).dialog('close');
								}
							}
						});			            
			        }
				});	
			}
		}

		// Credit-Card Info
		order_pay_type = localStorage.getItem('order_pay_type');
		if( order_pay_type == 'Credit-Card' ){
			$('#div_credit_card').css('display', 'block');

			if( localStorage.getItem('charge_count') != undefined ){
				var count = localStorage.getItem('charge_count');
				count++;
				localStorage.setItem('charge_count', count);
			}else{
				localStorage.setItem('charge_count', 1);
			}
			//console.log(localStorage.getItem('charge_count'));

			// Si no se posfechó el pago, entonces se intenta cobrar
			if( $('#postdate').val() != 'Yes' && localStorage.getItem('order_status') == 'InProcess' && parseInt(localStorage.getItem('charge_count')) <= 3  ){
				payment_charge();
			}

		}
		// Rerenced Deposit Info
		else if( order_pay_type == 'Referenced Deposit' ){
			$('#div_referenced_deposit').css('display', 'block');
			localStorage.setItem('order_status', 'Processed');
		}
		// COD Info
		else if( order_pay_type == 'COD' ){
			$('#div_cod').css('display', 'block');
			localStorage.setItem('order_status', 'Processed');
		}

		// Si la orden se procesó correctamente
		if( localStorage.getItem('order_status') == 'Processed' ){
			$('#step6').removeClass('step_off').addClass('step_on');
		}

		$('#btn_submit').click(function(event) {
			submit_ok = true;
			$('#frm_sales_step6').submit();
		});
	}
	// Datos de facturación
	if( $('#div_form_invoice').length ){
		$('#div_form_invoice').dialog({
			width: 700,
			height: 465,
			modal: true,
			autoOpen: false,
			resisable: true,
			draggable: true,
			open: function(){
				$('#td_invoice_saving').html('');
			},
		});
		$('#lnk_invoice').click(function(event) {
			$('#div_form_invoice').dialog({
				buttons: {
					'Guardar datos': function(){
						save_invoice_data();
					},
					'Cancelar': function(){
						$(this).dialog('close');
					}
				}
			});
			$('#div_form_invoice').dialog('open');
		});

		$('#copy_data_customer').click(function(event) {
			$('#invoice_name').val( $('#invoice_name').attr('data-value').toUpperCase() );
			$('#invoice_street').val( $('#invoice_street').attr('data-value').toUpperCase() );
			$('#invoice_urbanization').val( $('#invoice_urbanization').attr('data-value').toUpperCase() );
			$('#invoice_city').val( $('#invoice_city').attr('data-value').toUpperCase() );
			$('#invoice_state').val( $('#invoice_state').attr('data-value').toUpperCase() );			
			$('#invoice_zipcode').val( $('#invoice_zipcode').attr('data-value').toUpperCase() );			
		});

		// Reglas de validacion del formulario
		$('#frm_sales_invoice').validate({
	        rules:{ 
	        	invoice_rfc: {
	        		required: true,
	        		minlength: 13,
	        	},
	        	invoice_name: 'required',
	            invoice_street: 'required',
	            invoice_noext: 'required',
	            invoice_urbanization: 'required',
	            invoice_city: 'required',
	            invoice_state: 'required',
	            invoice_country: 'required',
	            invoice_zipcode:{ 
	            	required: true,
	                digits: true,
	                minlength: 5,
	            },
	    	},
	    	messages:{
	            invoice_rfc: {
	        		required: '<span class="ValidateError"></span>',
	        		minlength: '<span class="ValidateError"></span>',
	        	},
	        	invoice_name: '<span class="ValidateError"></span>',
	        	invoice_street: '<span class="ValidateError"></span>',
	        	invoice_noext: '<span class="ValidateError"></span>',
	        	invoice_urbanization: '<span class="ValidateError"></span>',
	        	invoice_city: '<span class="ValidateError"></span>',
	        	invoice_state: '<span class="ValidateError"></span>',
	        	invoice_country: '<span class="ValidateError"></span>',
	            invoice_zipcode:{ 
	            	required: '<span class="ValidateError"></span>',
	                digits: '<span class="ValidateError"></span>',
	                minlength: '<span class="ValidateError"></span>',
	            },
	    	},
	    	errorClass: "help-inline",
	    	errorElement: "span",
	    	highlight:function(element, errorClass, validClass) {
	            $(element).parents('.line').removeClass('success').addClass('val_error');
	    	},
	    	unhighlight: function(element, errorClass, validClass) {
	    		$(element).parents('.line').removeClass('val_error').addClass('val_success');
	    	},
	    	invalidHandler: function(form, validator) {
		        /*
		        if( submit_toback ){
		        	validator.resetForm();
		        	$(form).submit();
		        }
		        */
		    }
	    });
		$('#invoice_rfc').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_name').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_street').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_noext').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_noint').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_urbanization').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_city').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_state').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		$('#invoice_country').blur(function(event){ $(this).val( $(this).val().toUpperCase() ) });
		
		function save_invoice_data(){			
			if( $('#frm_sales_invoice').validate().form() ){
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'get',			
					dataType: 'json',
					data: $('#frm_sales_invoice').serialize() +'&cmd=ajax_save_invoice_data',
					beforeSend: function(){
						$('#td_invoice_saving').html('<div class="dialog_icon" style="margin: auto auto; padding: 5px; text-align: center;"><img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">Guardando datos... por favor espere</div>');
					},
					success: function(xresponse){
						$('#td_invoice_saving').html('<div class="dialog_icon" style="margin: auto auto; padding: 5px; text-align: center;"><img src="/sitimages/sales/accepted48.png" class="ico" style="width: 24px;">Los datos se guardaron correctamente</div>');
						$('#div_form_invoice').dialog({
							buttons:{
								'Cerrar': function(){
									$(this).dialog('close');
								}
							}
						});
					}
				});
			}
		}
	}

	// Editar Email
	if( $('#div_email_edit').length ){
		$('#div_email_edit').dialog({
			width: 300,
			height: 150,
			modal: true,
			autoOpen: false,
			resisable: true,
			draggable: true,
			open: function(){
				//$('#td_invoice_saving').html('');
			},
			buttons: {
				'Guardar': function(){					
					save_email();
				},
				'Cancelar': function(){
					$(this).dialog('close');
				}
			}
		});
		$('#lnk_edit_email').click(function(event) {
			$('#div_email_edit').dialog('open');
		});

		$('#frm_email').validate({
	        rules:{ 
	        	email: {
	            	/*required: true,*/
	            	email: true,
	            },
	    	},
	    	messages:{
	            email: {
	        		email: '<span class="ValidateError"></span>',
	        	},
	    	},
	    	errorClass: "help-inline",
	    	errorElement: "span",
	    	highlight:function(element, errorClass, validClass) {
	            $(element).parents('.line').removeClass('success').addClass('val_error');
	    	},
	    	unhighlight: function(element, errorClass, validClass) {
	    		$(element).parents('.line').removeClass('val_error').addClass('val_success');
	    	},
	    	invalidHandler: function(form, validator) {
		        /*
		        if( submit_toback ){
		        	validator.resetForm();
		        	$(form).submit();
		        }
		        */
		    }
	    });

		function save_email(email){
			if( $('#frm_email').validate().form() ){
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'get',
					dataType: 'json',
					data: $('#frm_email').serialize() +'&cmd=ajax_save_email',
					beforeSend: function(){
						//$('#td_invoice_saving').html('<div class="dialog_icon" style="margin: auto auto; padding: 5px; text-align: center;"><img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">Guardando datos... por favor espere</div>');
					},
					success: function(xresponse){
						$('#div_email_edit').dialog('close');
						$('#spn_email').html( $('#email').val() );
					}
				});
			}
		}

		$('#lnk_send_email').click(function(event) {
			send_mail( $('#spn_email').html() );
		});
		function send_mail(email){
			if( email != '' ){
				$.ajax({
					url: '/cgi-bin/mod/sales/admin',
					type: 'get',
					dataType: 'json',
					data: {'cmd': 'ajax_send_mail'},
					beforeSend: function(){
						$('#div_msj_send_mail').html('<div class="dialog_icon" style="margin: auto auto; padding: 5px; text-align: center;"><img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative; width: 14px;">Enviando email</div>');
					},
					success: function(xresponse){
						$('#div_msj_send_mail').html('<span style="color: #0B610B;">Email enviado !!</span>');
					}
				});
			}
		}
	}

	/*
	 *-----------------------------------------------------------------
	 * Se cargan los valores almacenados en la sesión
	 *-----------------------------------------------------------------
	 */
	if( $('#step').val() == '1' ){
		localStorage.clear();
	}else{		
		get_sessionStorage();

		var current_step = parseInt($('#step').val()) - 1;
		// Actualiza los valores globales
		if( order_taxes_pct == 0 && $('#taxes').length )	order_taxes_pct = $('#taxes').val();
		if( order_discount == 0 && $('#discount').length )	order_discount = $('#discount').val();

		if( shop_cart_items.length > 0 ){
			// Impuestos			
			if( $('#taxes').length ){
				order_taxes_pct = $('#taxes').val();
				save_sessionStorage();
			}
			if( $('#div_shop_cart_taxes').length ){
				$('#div_shop_cart_taxes .shop_cart_prod_name').html('Impuestos: ('+(order_taxes_pct * 100)+'%)');
			}
			
			
			// Validación extra para el tipo de envío en el paso de confirmación
			if( $('#step').val() == '6' && $('#shipping').val() != order_shipping && $('#shp_type').val() != order_shp_type ){
				order_shipping = $('#shipping').val();
				order_shp_type = $('#shp_type').val();
			}

			// Carro de compras
			var shop_cart_tmp = [];
			shop_cart_tmp = shop_cart_items.slice();
			shop_cart_items.length = 0;
					
			for( var i=0; i<shop_cart_tmp.length; i++ ){
				//console.log('::-> '+shop_cart_tmp[i][0]+', '+shop_cart_tmp[i][1]+', '+shop_cart_tmp[i][2]+', '+shop_cart_tmp[i][3]+', '+shop_cart_tmp[i][4]+', '+shop_cart_tmp[i][5]+', '+shop_cart_tmp[i][6]+', '+shop_cart_tmp[i][7]+', '+shop_cart_tmp[i][8]);

				shop_cart_add({
					'id_prod': shop_cart_tmp[i][0],
					'id_sku_prod': shop_cart_tmp[i][1],
					'model': shop_cart_tmp[i][2],
					'price': shop_cart_tmp[i][3],
					'tax_pct': shop_cart_tmp[i][4],
					'pay_type': order_pay_type,
					'pmts': order_total_pmts,
					'main_prod': shop_cart_tmp[i][6],
					'parent_prod': shop_cart_tmp[i][7],
					'id_price': shop_cart_tmp[i][8],
					'shipping': order_shipping,
				});
			};		

			// Se calculan los totales y se guardan los datos en localStorage
		    shop_cart_totals();
		    save_sessionStorage();

			// Forma de pago
			//var img_icon = '<img src="/sitimages/sales/icon'+order_pay_type.replace(' ','-')+'.png" class="ico_bg" alt="pay_type" title="'+order_pay_type+'" />';
			//$('#div_order_pay_type').html(order_pay_type+' ('+order_total_pmts+ ') '+img_icon);
			// Se hace visible la forma de pago			
			if( order_pay_type == 'Credit-Card' )
				$('#opt_pay_type_cc').removeClass('pay_legend').addClass('pay_legend_selected');
			else if( order_pay_type == 'COD' )
				$('#opt_pay_type_cod').removeClass('pay_legend').addClass('pay_legend_selected');
			else if( order_pay_type == 'Referenced Deposit' )
				$('#opt_pay_type_rd').removeClass('pay_legend').addClass('pay_legend_selected');
			// Se hace visible la cantidad de pagos
			$('#div_total_pmts').css('display', 'block').html(order_total_pmts);

			
			// Si el paso actual es el 1:Llamada y ya hay productos en el carro de compras
			if( $('#step').val() == '2' ){
				$('#step2').removeClass('step_off').addClass('step');
				$('#step3').removeClass('step_off').addClass('step');
				$('#step4').removeClass('step_off').addClass('step');
			}

		}else{
			// Si el paso actual es el 1:Llamada y NO hay productos en el carro de compras
			if( current_step == 1 ){
				$('#div_shop_cart_extras').css('display', 'none');
			}
		}

		// Búsqueda inicial de los mas vendidos
		if( (localStorage.getItem('reset_shop_cart') != '1' || localStorage.getItem('reset_shop_cart') == undefined) && current_step == 2 ){
			filter_search = 'topsales';		
			search_products('');
		}

		// Si existen productos de respaldo, entonces los muestra
		if( shop_cart_items2.length > 0 ){
			if( current_step <= 6 ){
				var html_prod = '';
				var ids_prods = '';
				for( var i=0; i<shop_cart_items2.length;  i++ ){					
					if( shop_cart_items2[i][6] == 1 ){
						html_prod += '<div style="display: block; border-top: 1px solid silver; width: 100%;">';
					}else{
						html_prod += '<div style="display: block; width: 100%;">';
					}
					html_prod += '	<span class="shop_cart_prod_name" style="float: left;">'+shop_cart_items2[i][2]+'</span>';
					html_prod += '	<span class="shop_cart_prod_price" style="float: right;">'+format_price(shop_cart_items2[i][3])+'</span>';
					html_prod += '</div>';
					html_prod += '<div style="display:block; clear: both;"></div>';

					if( ids_prods.indexOf(shop_cart_items2[i][0]) == -1 ){
						ids_prods += shop_cart_items2[i][0]+' ';
					}
				}

				$('#div_list_prod_bkp').html(html_prod);
				$('#table_list_prod_bkp').css('display', 'block');

				if( localStorage.getItem('reset_shop_cart') == '1' ){
					localStorage.setItem('reset_shop_cart', '0');
					$('#txt_search').val( ids_prods.substr(0, (ids_prods.length - 1)) );
					filter_search = '';
					search_products( $('#txt_search').val() );
				}/*else if( $('#step').val() == '3' ){
					filter_search = 'topsales';
					search_products('');
				}*/

			}else{
				shop_cart_items2.length = 0;
			}
		}

		save_sessionStorage();
	}


	/*
	 *-----------------------------------------------------------------
	 * Funciones globales
	 *-----------------------------------------------------------------
	 */

	/*----------------------------------
	 * Controla toda la funcionalidad en la búsqueda y modificación del código postal
	 * en los pasos donde se utilice dicho valor
	 *----------------------------------
	 */
	var zp_search_mode = 'address'; // Búsqueda de código postal: address->Domicilio, shipping: Dirección de envío
	var zp_presearch = 0; // Si hubo una búsqueda previa de código postal y generó mas de un resultado
	var zipcode_search = ''; // Código postal a buscar
	var zipcode_select = false; // Bandera que controla la selección de un código postal
	var shp_zipcode_current = ''; // Valor actual del código postal de envío
	if( $('#div_search_zipcode').length ){
		/*---------------------------------------
		 * Funcionalidad del API de google maps
		 *---------------------------------------
		 */
		var geocoder;
		var map;
		function initialize_gmaps() {
			geocoder = new google.maps.Geocoder();
			var latlng = new google.maps.LatLng(19.4321783, -99.1337639);
			var mapOptions = {
				zoom: 8,
				center: latlng,
				mapTypeId: google.maps.MapTypeId.ROADMAP
			}

			map = new google.maps.Map(document.getElementById('tabs-div_maps'), mapOptions);
		}
		function codeAddress(address) {
			if( address == undefined || address == '' )
				address = 'ciudad mexico+df';

			geocoder.geocode( { 'address': address}, function(results, status) {
				if (status == google.maps.GeocoderStatus.OK) {
					map.setCenter(results[0].geometry.location);
					var marker = new google.maps.Marker({
						map: map,
						position: results[0].geometry.location,
						draggable: true,
						title: results[0].formatted_address,
					});
					google.maps.event.addListener(marker,'drag',function(event) {
						$('[name="Lat"]').val(event.latLng.lat());
						$('[name="Long"]').val(event.latLng.lng());
					});

					google.maps.event.addListener(marker,'dragend',function(event) {
						$('[name="Lat"]').val(event.latLng.lat());
						$('[name="Long"]').val(event.latLng.lng());
					});

					$('[name="Lat"]').val(results[0].geometry.location.A);
					$('[name="Long"]').val(results[0].geometry.location.F);
					map.setZoom(15);
				} else {
					console.log('No se encontro el punto: ' + status);
				}
			});
		}
		//--------------------------------------		

		var ajax_zipcode_search = ajax_zipcode_match = false;
		$('#div_search_zipcode').dialog({
			autoOpen: false,
		    height: 600,
		    width: 800,
		    modal: false,
		    buttons: {
			    'Cerrar': function(){
			    	$(this).dialog('close');
			    }
		    },
		    open: function(){
		    	$('#tabs-zipcode').tabs( "option", "active", 0);
		    	if( zp_presearch == 0 ){
			    	$('#zp_state').val('0');
			    	$('#zp_urbanization').val('');
			    }else{
			    	search_zipcodes();
			    }
		    },
		    beforeClose: function(){
		    	if( zp_presearch == 1 && !zipcode_select ){
		    		if( zp_search_mode == 'address' ){
		    			$('#zipcode').val( $('#spn_zipcode_content').html() );
		    		}else{
		    			$('#shp_zipcode').val(shp_zipcode_current);
		    		}
		    	}

		    	zipcode_select = false;
		    }
		});

		$('#tabs-zipcode').tabs({
			beforeActivate: function(event, ui){
				// Tab SEPOMEX
				if( ui.newPanel.is("#tabs-zipcode2") ){
					$('#tabs-zipcode2').html('<iframe src="http://www.sepomex.gob.mx/servicioslinea/paginas/ccpostales.aspx#ctl00_PlaceHolderMain_ctl00__ControlWrapper_RichHtmlField" style="width: 700px; height: 650px; overflow: hidden; border: none; margin: auto auto; position: relative;"></iframe>');
				}
				// Tab Google Maps
				if( ui.newPanel.is("#tabs-zipcode3") ){
					// Se prepara el texto de busqueda para el Google maps
					var txt_search = '';
					if( $('#zp_city').val() != '' && $('#zp_city').val() != '0' ) 
						txt_search = $('#zp_city').val();

					if( $('#zp_state').val() != '' && $('#zp_state').val() != '0' && txt_search != '' ) 
						txt_search += '+'+$('#zp_state').val();
					else if( $('#zp_state').val() != '' )
						txt_search = $('#zp_state').val();

					if( $('#zp_urbanization').val() != '' && txt_search != '' )
						txt_search += '+'+$('#zp_urbanization').val();
					else if( $('#zp_urbanization').val() != '' )
						txt_search += $('#zp_urbanization').val();

					if( txt_search == '' || txt_search == '0' ){
						if( zp_search_mode == 'address' ){
							if( $('#zipcode').val() != '' ){
								txt_search = $('#urbanization').val()+'+'+$('#zipcode').val()+'+'+$('#state').val();//+'+'+$('#city').val()
							}else{
								txt_search = 'ciudad mexico+df';
							}
						}else{
							if( $('#shp_zipcode').val() != '' ){
								txt_search = $('#shp_urbanization').val()+'+'+$('#shp_zipcode').val()+'+'+$('#shp_state').val();//+'+'+$('#shp_city').val()
							}else{
								txt_search = 'ciudad mexico+df';
							}
						}						
					}

					txt_search = txt_search.replace(' ', '+');					
					initialize_gmaps();
					codeAddress(txt_search);
				}
			},
			activate: function(event, ui){
				if( ui.newTab.context.hash == '#tabs-zipcode3' ){
					google.maps.event.trigger(map,'resize');
				}
			}
		});
				

		// Actualiza el combobox de Municipios
		$('#zp_state').change(function(event) {
			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',
				dataType: 'json',
				async: false,
				data: {
					'ajaxbuild': 'sales_build_select_zipcodes_city',
					'state': $(this).val(),
				},
				beforeSend: function(){
					$('#zp_city').html('<option>Cargando...<option>');
				},
				success: function(xresponse){
					var html_opt = '';
					if( xresponse.matches > 0 ){
						html_opt += '<option value="0">--- Municipios ---</option>';
						for( var i=0; i<xresponse.matches; i++ ){
							html_opt += '<option value="'+xresponse.items[i].city+'">'+xresponse.items[i].city+'</option>';
						}
					}else{
						html_opt = '<option value="0">--- Vacío ---</option>';
					}
					$('#zp_city').html(html_opt);
				}
			});
		});
		// Búsqueda dinámica de codigos postales
		$('#btn_zp_search').click(function(event) {
			search_zipcodes();
		});
		// Funcion que realiza la busqueda de códigos postales y los muestra en un listado
		function search_zipcodes(){
			ajax_zipcode_search = $.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',			
				dataType: 'json',
				data: {
					'ajaxbuild': 'sales_search_zipcodes',
					'state': $('#zp_state').val(),
					'city': $('#zp_city').val(),
					'urbanization': $('#zp_urbanization').val(),
					'zipcode': zipcode_search,
				},
				beforeSend: function(){
					$('#table_zipcode_results tbody').html( loading('Buscando c&oacute;digos postales... por favor espere') );
				},
				success: function(xresponse){
					var html_rlst = '';
					if( xresponse.matches > 0 ){
						for( var i=0; i<xresponse.matches; i++ ){
							html_rlst += '<tr>';
							html_rlst += '	<td style="width: 15%; text-align: center;">';
							html_rlst += '		<a href="#" class="lnk_zipcode_rslt" ';
							html_rlst += '			data-zipcode="'+xresponse.items[i].zipcode+'" ';
							html_rlst += '			data-urbanization="'+xresponse.items[i].urbanization+'" ';
							html_rlst += '			data-city="'+xresponse.items[i].city+'" ';
							html_rlst += '			data-state="'+xresponse.items[i].state+'" ';
							html_rlst += '			data-express="'+xresponse.items[i].express_delivery+'" ';
							html_rlst += '		">'+xresponse.items[i].zipcode;
							html_rlst += '		</a>';
							html_rlst += '	</td>';
							html_rlst += '	<td style="width: 40%;">'+xresponse.items[i].urbanization+'</td>';
							html_rlst += '	<td style="width: 25%;">'+xresponse.items[i].city+'</td>';
							html_rlst += '	<td style="width: 20%;">'+xresponse.items[i].state+'</td>';
							html_rlst += '<tr>';
						}
					}else{
						html_rlst += '<tr><td>Sin resultados...</td></tr>';
					}
					$('#table_zipcode_results tbody').html(html_rlst);
				}
			});
		}

		// Selección de un codigo postal
		$('#table_zipcode_results tbody').on('click', '.lnk_zipcode_rslt', function(){
			zipcode_select = true;
			$('#div_search_zipcode').dialog('close');
			var this_obj = $(this);
			if( zp_search_mode == 'address' ){

				$('#zipcode').val( this_obj.attr('data-zipcode') );
				$('#spn_zipcode_content').html( this_obj.attr('data-zipcode') );
				$('#urbanization').val( this_obj.attr('data-urbanization') ).addClass('do_blink');
				$('#city').val( this_obj.attr('data-city') ).addClass('do_blink');
				$('#state').val( this_obj.attr('data-state') ).addClass('do_blink');

				if( $('#urbanization').is(':visible') ){	
					$('#address1').attr('readonly', false).removeClass('txt_only_info').addClass('input');
					if( $('#address1').val().length < 4 ){
						$('#address1').val('');
					}
					$('#address1').focus();
				}

				// Solo para el paso 3 -> (4): Dirección
				if( $('#shp_zipcode').length && $('#shp_zipcode').val() == '' && shop_cart_items.length > 0 ){
					var this_express_delivery = this_obj.attr('data-express');
					$('#zones_express_delivery').val( this_express_delivery );
					
					if( order_shp_type == 2 && this_express_delivery == 'No' ){
						order_shp_type = ( order_pay_type == 'COD' ) ? 3 : 1;
						order_shipping = $('#cost_shp_standard').val();
						shop_cart_totals();
					}
				}

			// Solo para el paso 3 -> (4): Dirección
			}else if( zp_search_mode == 'shipping' ){

				if( shop_cart_items.length > 0 ){					
					// Se genera el listado de productos del carro de compras
					// para validar la disponibilidad del nuevo cod. postal
					var prod_list = '';
					for( var i=0; i<shop_cart_items.length; i++ ){
						//				id_products			:	id_products_prices
						prod_list += shop_cart_items[i][0]+':'+shop_cart_items[i][8]+',';
					}
					prod_list = prod_list.substr(0, (prod_list.length - 1));

					shp_zipcode_current = $('#shp_zipcode').val();
					// Se valida la disponibilidad de los productos
					$.ajax({
						url: '/cgi-bin/common/apps/ajaxbuild',
						type: 'post',
						dataType: 'json',
						async: false,
						data: {
							'ajaxbuild': 'sales_zipcode_products_available',
							'zipcode': this_obj.attr('data-zipcode'),
							'pay_type': order_pay_type,
							'total_pmts': order_total_pmts,
							'products': prod_list,

						},
						beforeSend: function(){						
						},
						success: function(xresponse){
							// Se pasa el control para que muestre el mensaje correspondiente o asigne los valores				
							validate_sch_zipcode({
								'available': xresponse.available,
								'products_list': xresponse.products_list,
								'express_delivery': xresponse.express_delivery,
								'state': this_obj.attr('data-state'),
								'city': this_obj.attr('data-city'),
								'urbanization': this_obj.attr('data-urbanization'),
								'zipcode': this_obj.attr('data-zipcode'),
							});
							//$('#shp_zipcode').val( this_obj.attr('data-zipcode') );
						}
					});
				}else{
					$('#shp_zipcode').val( this_obj.attr('data-zipcode') );
					asign_shp_address({
						'state': this_obj.attr('data-state'),
						'city': this_obj.attr('data-city'),
						'urbanization': this_obj.attr('data-urbanization'),
					});
				}

			}
		});

		if( $('.lnk_search_zipcode').length ){
			$('.lnk_search_zipcode').click(function(event){
				zp_search_mode = $(this).attr('rel');
				$('#div_search_zipcode').dialog('open');
			});
		}

		// Controla el cambio de código postal(ambos)	
		if( $('#zipcode').length ){			
			$('#zipcode').keyup(function(event){
				// Elimina los caracteres que no sean números
				this.value = (this.value + '').replace(/[^0-9]/g, '');

				var this_val = $(this).val();
				if( (this_val != $('#spn_zipcode_content').html() && this_val.length == 5 && $('#step').val() == '4') || ($('#step').val() == '2' && this_val.length == 5) ){
					zp_search_mode = 'address';
					get_data_zipcode(this_val);
				}else if( $('#spn_zipcode_error').length ){
					$('#spn_zipcode_error').html('');
				}
			});
			$('#zipcode').blur(function(event){
				var this_val = $(this).val();
				if( (this_val != $('#spn_zipcode_content').html() && this_val.length == 5 && $('#step').val() == '4') || ($('#step').val() == '2' && this_val.length == 5 && ($('#state').length && $('#state').val() == '')) ){
					zp_search_mode = 'address';
					get_data_zipcode(this_val);
				}
			});
		}
		if( $('#shp_zipcode').length ){		
			$('#shp_zipcode').focus(function(event){
				if( !ajax_zipcode_match ){
					shp_zipcode_current = $(this).val();					
				}
			});
			$('#shp_zipcode').keyup(function(event){
				// Elimina los caracteres que no sean números
				this.value = (this.value + '').replace(/[^0-9]/g, '');
				
				var this_val = $(this).val();
				if( this_val != shp_zipcode_current && this_val.length == 5 && $('#step').val() == '4' ){
					zp_search_mode = 'shipping';
					get_data_zipcode(this_val);
				}else if( $('#spn_shp_zipcode_error').length ){
					$('#spn_shp_zipcode_error').html('');
				}
			});
			$('#shp_zipcode').blur(function(event){
				var this_val = $(this).val();
				if( shp_zipcode_current != this_val && this_val.length == 5 && !ajax_zipcode_match ){
					zp_search_mode = 'shipping';
					get_data_zipcode(this_val);
				}
			});
		}
		function get_data_zipcode(zipcode){
			// Inactiva el botón que inicia el proceso del pedido mientras se realiza la búsqueda
			if( localStorage.getItem('current_step') == '1' ){
				$('#submit_start').attr('disabled', true);
			}

			// Se genera el listado de productos del carro de compras
			// para validar la disponibilidad del nuevo cod. postal
			var prod_list = '';
			if( shop_cart_items.length > 0 && zp_search_mode == 'shipping' ){
				for( var i=0; i<shop_cart_items.length; i++ ){
					//				id_products			:	id_products_prices
					prod_list += shop_cart_items[i][0]+':'+shop_cart_items[i][8]+',';
				}
				prod_list = prod_list.substr(0, (prod_list.length - 1));
			}

			$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'post',			
				dataType: 'json',
				data: {
					'ajaxbuild': 'sales_search_zipcodes',
					'zipcode': zipcode,
					'pay_type': order_pay_type,
					'shp_type': order_shp_type,
					'total_pmts': order_total_pmts,
					'products': prod_list,
				},
				beforeSend: function(){
					var html_loading = '<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative; left: -25px; z-index: 10;">';
					if( zp_search_mode == 'address' ){	
						$('#div_loading_zipcode').html(html_loading);
						if( $('#spn_zipcode_error').length ) $('#spn_zipcode_error').html('');
					}else if( zp_search_mode == 'shipping' ){
						$('#div_loading_shp_zipcode').html(html_loading);
						if( $('#spn_shp_zipcode_error').length ) $('#spn_shp_zipcode_error').html('');
					}
					ajax_zipcode_match = true;					
				},
				success: function(xresponse){					
					if( zp_search_mode == 'address' ){
						$('#div_loading_zipcode').html('');
						if( xresponse.matches == 1 ){
							// Si el cod. postal de envio aún no se ha difinido, entonces
							// se valida la disponibilidad del envío express
							if( $('#shp_zipcode').val() == '' ){
								validate_sch_zipcode({
									'available': xresponse.available,
									'products_list': xresponse.products_list,
									'express_delivery': xresponse.express_delivery,
									'state': xresponse.items[0].state,
									'city': xresponse.items[0].city,
									'urbanization': xresponse.items[0].urbanization,
									'zipcode': xresponse.items[0].zipcode,
								});
							}else{
								$('#urbanization').val( xresponse.items[0].urbanization ).addClass('do_blink');
								$('#city').val( xresponse.items[0].city ).addClass('do_blink');
								$('#state').val( xresponse.items[0].state ).addClass('do_blink');

								if( $('#spn_zipcode_content').length )
									$('#spn_zipcode_content').html(xresponse.items[0].zipcode);

								if( $('#step').val() == '2' )// Llamada
									$('#div_info_address').show('fast');
							}
						}
					}else{
						$('#div_loading_shp_zipcode').html('');
						if( xresponse.matches == 1 ){						
							// Se pasa el control para que muestre el mensaje correspondiente o asigne los valores
							validate_sch_zipcode({
								'available': xresponse.available,
								'products_list': xresponse.products_list,
								'express_delivery': xresponse.express_delivery,
								'state': xresponse.items[0].state,
								'city': xresponse.items[0].city,
								'urbanization': xresponse.items[0].urbanization,
								'zipcode': xresponse.items[0].zipcode,
							});
						}
					}

					// Si hubo más de un resultado, muestra el listado
					if( xresponse.matches > 1 ){
						zp_presearch = 1;
						$('#zp_state').val(xresponse.items[0].state);
						$('#zp_state').change();
						$('#zp_city').val(xresponse.items[0].city);
			    		$('#zp_urbanization').val('');
			    		zipcode_search = zipcode;
			    		$('#div_search_zipcode').dialog('open');
					}else if( xresponse.matches == 0 ){
						if( $('#spn_zipcode_error').length && zp_search_mode == 'address' ){
							$('#spn_zipcode_error').html('Invalid');
							// Solo en el paso 1(Llamada)
							if( $('#step').val() == '2' ){
								$('#urbanization').val('');
								$('#city').val('');
								$('#state').val('');
							}
						}else if( $('#spn_shp_zipcode_error').length && zp_search_mode == 'shipping' ){
							$('#spn_shp_zipcode_error').html('Invalid');
						}
					}

					// Reactiva el botón para iniciar el proceso del pedido
					if( localStorage.getItem('current_step') == '1' ){
						$('#submit_start').attr('disabled', false);
					}
				}
			});
		}
		/*
		 * Realiza la validación de los resultados de la búsqueda del nuevo código postal
		 */
		function validate_sch_zipcode(params){
			// Si NINGUNO de los productos está disponibles para el nuevo código postal
			if( params.available == 'None' ){
				build_dialog('Ninguno de los productos del carrito de compras est&aacute; disponible para este c&oacute;digo postal', 'warning');
				dialog_form.dialog({
					buttons: {
						'Vaciar carrito': function(){
							dlt_products_noavailable(params.available);
							asign_shp_address(params);

							ajax_zipcode_match = false;
						},
						'Ignorar advertencia': function(){
							$(this).dialog('close');
							asign_shp_address(params);						
							if( $('#shp_address1').val().length < 4 ){
								$('#shp_address1').val('');
							}
							
							ajax_zipcode_match = false;
						},
					}
				});
			// Si solo ALGUNOS productos están disponibles para el nuevo código postal
			}else if( params.available == 'Some' ){
				var products_noavailable = '';
				for( var i=0; i<params.products_list.length; i++ ){
					if( params.products_list[i].available == 'No' )
						products_noavailable += params.products_list[i].model+'<br />';
				}
				build_dialog('Los siguientes productos no est&aacute;n disponibles para este c&oacute;digo postal:<br />'+products_noavailable, 'warning');
				dialog_form.dialog({
					buttons: {
						'Elimniar los no disponibles': function(){
							dlt_products_noavailable(params.available, params.products_list);
							asign_shp_address(params);

							ajax_zipcode_match = false;
						},
						'Ignorar advertencia': function(){
							$(this).dialog('close');
							asign_shp_address(params);
							
							if( $('#shp_address1').val().length < 4 ){
								$('#shp_address1').val('');
							}					

							ajax_zipcode_match = false;
						},
					}
				});
			// Si TODOS los productos están disponibles
			}else{
				// Si el tipo de envío actual es Express y el nuevo código postal no cuenta con ese servicio
				console.log(order_shp_type+' - '+params.express_delivery);
				if( order_shp_type == 2 && params.express_delivery == 'No' ){
					build_dialog('Este c&oacute;digo postal no cuenta con el tipo de env&iacute;o actualmente seleccionado.<br />Al realizar el cambio, se modificar&aacute; el tipo de env&iacute;o a Estandard<br /><br />&#191;Est&aacute; seguro de continuar con el cambio?', 'confirm');
					dialog_form.dialog({
						buttons: {
							'Si estoy seguro': function(){
								$(this).dialog('close');
								asign_shp_address(params);

								order_shp_type = ( order_pay_type == 'COD' ) ? 3 : 1;
								order_shipping = ( $('#cost_shp_standard').length && $('#cost_shp_standard').val() != '') ? $('#cost_shp_standard').val() : '0';							
								localStorage.setItem('order_shp_type', order_shp_type);
								localStorage.setItem('order_shipping', order_shipping);

								shop_cart_totals();
								
								if( $('#shp_address1').val().length < 4 ){
									$('#shp_address1').val('');
								}

								ajax_zipcode_match = false;
							},
							'Cancelar el cambio': function(){
								$('#shp_zipcode').val(shp_zipcode_current);
								$(this).dialog('close');
							},
						}
					});

				// Si no existe ningún otro factor que impida cambiar el código postal
				}else{
					asign_shp_address(params);

					ajax_zipcode_match = false;
				}
			}
		}
		/*
		 * Asgina los valores recibidos en params a los campos de la dirección de envío
		 */
		function asign_shp_address(params){
			$('#shp_urbanization').val( params.urbanization ).addClass('do_blink');
			$('#shp_city').val( params.city ).addClass('do_blink');
			$('#shp_state').val( params.state ).addClass('do_blink');
			if( params.zipcode != undefined ){
				$('#shp_zipcode').val(params.zipcode);
				$('#spn_shp_zipcode_content').html(params.zipcode);
			}
			if( params.address1 != undefined )
				$('#shp_address1').val(params.address1);
			if( params.address2 != undefined )
				$('#shp_address2').val(params.address2);
			if( params.address3 != undefined )
				$('#shp_address3').val(params.address3);
			if( params.express_delivery != undefined )
				$('#zones_express_delivery').val( params.express_delivery );
			console.log(params.express_delivery);
			$('#shp_address1').focus();
		}
		/* 
		 * Elimina los productos del carrito de compras que no estén disponibles para el nuevo código postal
		 */
		function dlt_products_noavailable(available, produts){
			dialog_form.dialog('close');
			
			// Eliminar todos los productos
			if( available == 'None' ){
				// Se borra completamente el array original
				shop_cart_items.length = 0;
				$('#div_shop_cart_cont').html('');

			// Eliminar solo los NO DISPONIBLES
			}else if( products != undefined ){
				var id_prod_drop = params.obj.attr('id').substr(9);
				var ids = id_prod_drop.split('-');

				for( var i=0; i<products.length; i++ ){
					var shop_cart_tmp = [];// Array temporal
					for( var j=0; j<shop_cart_items.length; j++ ){
						if( shop_cart_items[j][0] == products[i].id_products ){
							$("div[id^='div_prod-"+products[i].id_products+"']").remove();
						}else{
							// Se pasan al array temporal aquellos productos que no se van a eliminar
							shop_cart_tmp.push([shop_cart_items[j][0], shop_cart_items[j][1], shop_cart_items[j][2], shop_cart_items[j][3], shop_cart_items[j][4], shop_cart_items[j][5], shop_cart_items[j][6], shop_cart_items[j][7], shop_cart_items[j][8], shop_cart_items[i][9]]);
						}				
					}
					// Se sobreescribe el array original con el array temporal
					shop_cart_items = shop_cart_tmp.slice();
				}
			}

			// Si se vacía el carro de compras, se eliminan los datos:
			// -> Forma de pago
			// -> Cantidad de pagos
			if( shop_cart_items.length == 0 ){
				order_pay_type	= '';
				order_total_pmts= '';
				order_shipping	= 0;
				order_discount	= 0;
				//$('#div_order_pay_type').html('');
				//$('#div_shop_cart_cont').html('<div class="border_space">El carro est&aacute; vac&iacute;o</div>');
				$('#opt_pay_type_cc').removeClass('pay_legend_selected').addClass('pay_legend');
				$('#opt_pay_type_cod').removeClass('pay_legend_selected').addClass('pay_legend');
				$('#opt_pay_type_rd').removeClass('pay_legend_selected').addClass('pay_legend');
				$('#div_total_pmts').css('display', 'none').html('');
			}

			// Se calculan los totales
			shop_cart_totals();

			// Se guardan los cambios en la sesion
			save_sessionStorage();
		}

	}	
	// Fin de la funcionalidad del código postal
	//-----------------------------------


	// Funcionalidad para mostrar la tabla de tiempos de envios
	if( $('#div_zone_delivery').length ){

		if( parseInt($('#step').val()) > 2 ){
			$('#lnk_zone_delivery').css('display', 'block');
		}else{
			$('#lnk_zone_delivery').css('display', 'none');
		}

		$('#div_zone_delivery_content').dialog({
			autoOpen: false,
		    height: 600,
		    width: 800,
		    modal: false,
		    draggable: true,
		    closeOnEscape: true,
		    open: function(){
		    	get_zones_delivery_info();
		    },
		    buttons: {
			    'Cerrar': function(){
			    	$(this).dialog('close');
			    }
		    },
		});

		$('#lnk_zone_delivery').click(function(event) {			
			$('#div_zone_delivery_content').dialog('open');
		});

		function get_zones_delivery_info(){
			// Se genera el listado de productos del carro de compras
			// para validar el envío express
			var prod_list = '';
			if( shop_cart_items.length > 0 ){
				for( var i=0; i<shop_cart_items.length; i++ ){
					//				id_products			:	id_products_prices
					prod_list += shop_cart_items[i][0]+':'+shop_cart_items[i][8]+',';
				}
				prod_list = prod_list.substr(0, (prod_list.length - 1));
			}
			
			var this_zipcode = ( $('#shp_zipcode').val() != '' ) ? $('#shp_zipcode').val() : $('#zipcode').val();
	    	$.ajax({
				url: '/cgi-bin/common/apps/ajaxbuild',
				type: 'get',			
				dataType: 'html',
				data: {
					'ajaxbuild': 'sales_zones_delivery',
					'zipcode': this_zipcode,
					'pay_type': order_pay_type,
					'products': prod_list,
				},
				beforeSend: function(){						
					$('#div_zone_delivery_content').html( loading('') );					
				},
				success: function(xresponse){
					$('#div_zone_delivery_content').html(xresponse);
				}
			});
		}
	}

	/*-----------------------------------
	 * Funciones adicionales
	 *-----------------------------------
	 */

	// Genera el HTML para mostrar un loadding
	function loading(txt){
		var this_txt = ( txt != undefined && txt != '' ) ? txt : 'Cargando...';
		var html_loading = '<div style="border: 1px solid red; padding: 10px; border: none; margin: auto auto; min-height: 40px; text-align: center;">';
            html_loading += '	<img src="/sitimages/load16.gif" alt="loading" style="margin: auto auto; position: relative;">  '+this_txt;
            html_loading += '</div>';

        return html_loading;
	}

	// Formatéa a moneda un número
	function format_price(amt, pres){
		var format = ( $('#format_number').length ) ? $('#format_number').val() : localStorage.getItem('format_number');
		var simbol = format.substr(0,1);
		var separate = format.substr(1,1);
		var point = format.substr(2,1);

		if( pres == undefined ) pres = 2;
		if( amt != '' ){
			amt = parseFloat(amt).toFixed(pres).replace(/(\d)(?=(\d{3})+\.)/g, simbol+'1'+separate);
			return simbol+' '+amt;
		}else{
			amt = 0;
			return simbol+' '+parseFloat(amt).toFixed(pres);
		}
	}

	// Genera una ventana modal para confirmación
	var dialog_form;
	function build_dialog(txt, mode, params){
		var html_cont = '', this_title = '';
		if( mode != undefined ){
			if( mode == 'confirm' ){
				html_cont = '<div class="dialog_icon"><img src="/sitimages/sales/help48.png" class="ico"></div>';
				this_title = 'Confirm';
			}else if( mode == 'success' ){
				html_cont = '<div class="dialog_icon"><img src="/sitimages/sales/accepted48.png" class="ico"></div>';
				this_title = 'Success';
			}else if( mode == 'warning' ){
				html_cont = '<div class="dialog_icon"><img src="/sitimages/sales/warning48.png" class="ico"></div>';
				this_title = 'Warning';
			}else if( mode == 'error' ){
				html_cont = '<div class="dialog_icon"><img src="/sitimages/sales/error48.png" class="ico"></div>';
				this_title = 'Error';
			}else if( mode == 'info' ){
				html_cont = '<div class="dialog_icon"><img src="/sitimages/sales/info48.png" class="ico"></div>';
				this_title = 'Information';
			}
			html_cont += '<div class="dialog_text">'+txt+'</div>';
		}else{
			html_cont = txt;
			this_title = 'Message';
		}

		dialog_form = $('<div title="Direksys :: '+this_title+'">'+html_cont+'</div>').dialog({
			minHeight: 100,
			minWidth: 450,
			modal: true,
			resisable: false,
			autoOpen: true,
			closeOnEscape: false,
			open: function(event, ui) {
				$(".ui-dialog-titlebar-close", ui.dialog | ui).hide(); 
			},
		});
	}

	// Genera un número aleatorio
	function get_random(min, max){
		if( min == '' || min == undefined ) min = 10000;
		if( max == '' || max == undefined ) max = 990000;

		var random = Math.floor((Math.random() * parseInt(max)) + parseInt(min));
		return random;
	}

	// Valida el caracter pulsado en un textbox
	function validate_key(event){
		var ctrlkeys = [16,17,18,20,33,34,35,36,37,38,39,40,45,112,113,114,115,116,117,118,119,120,121,122,123,144];
		if( event.which !== 0 && !event.ctrlKey && !event.metaKey && !event.altKey && ctrlkeys.indexOf(event.keyCode) == -1 ){
	        return true;
	    }else{
	    	return false;
	    }
	}

	// Guarda en Session Storage los valores que se están usando en la venta actual
	function save_sessionStorage(){

		localStorage.setItem('order_pay_type', order_pay_type);
		localStorage.setItem('order_total_pmts', order_total_pmts);
		localStorage.setItem('shop_cart_items', JSON.stringify(shop_cart_items));
		localStorage.setItem('shop_cart_items2', JSON.stringify(shop_cart_items2));
		localStorage.setItem('order_shipping', order_shipping);
		localStorage.setItem('order_shp_type', order_shp_type);
		localStorage.setItem('order_total_net', order_total_net);
		localStorage.setItem('order_taxes_pct', order_taxes_pct);
		localStorage.setItem('order_discount', order_discount);
		localStorage.setItem('order_coupon', order_coupon);
		if( $('#id_salesorigins').length && $('#id_salesorigins').val() != undefined )
			localStorage.setItem('id_salesorigins', $('#id_salesorigins').val());
		if( $('#step').length && $('#step').val() != undefined )
			localStorage.setItem('current_step', parseInt($('#step').val()) - 1);
		if( $('#pay_type_available').length && $('#pay_type_available').val() != undefined )
			localStorage.setItem('pay_type_available', $('#pay_type_available').val());
		if( $('#format_number').length && $('#format_number').val() != undefined )
			localStorage.setItem('format_number', $('#format_number').val());
		// Datos del cupon
		if( coupon_id != undefined )
			localStorage.setItem('coupon_id', coupon_id);
		if( coupon_disc != undefined )
			localStorage.setItem('coupon_disc', coupon_disc);
		if( coupon_disc_type != undefined )
			localStorage.setItem('coupon_disc_type', coupon_disc_type);
		if( coupon_applied != undefined )
			localStorage.setItem('coupon_applied', coupon_applied);	
		
	}

	// Obtiene los valores guardados en Session Storage
	function get_sessionStorage(){

		if( localStorage.length > 0 ){
			order_pay_type	= localStorage.getItem('order_pay_type');
			console.log('order_pay_type: '+order_pay_type);
			order_total_pmts= localStorage.getItem('order_total_pmts');
			console.log('order_total_pmts: '+order_total_pmts);
			shop_cart_items	= JSON.parse(localStorage.getItem('shop_cart_items'));
			console.log('shop_cart_items: '+shop_cart_items);
			shop_cart_items2 = JSON.parse(localStorage.getItem('shop_cart_items2'));
			order_total_net	= (localStorage.getItem('order_total_net') != 'undefined') ? localStorage.getItem('order_total_net') : 0;			
			console.log('order_total_net: '+order_total_net);
			order_shipping	= (localStorage.getItem('order_shipping') != 'undefined') ? localStorage.getItem('order_shipping') : 0;
			console.log('order_shipping: '+order_shipping);
			order_taxes_pct	= (localStorage.getItem('order_taxes_pct') != 'undefined') ? localStorage.getItem('order_taxes_pct') : 0;
			console.log('order_taxes_pct: '+order_taxes_pct);
			order_discount	= (localStorage.getItem('order_discount') != 'undefined') ? localStorage.getItem('order_discount') : 0;
			console.log('order_discount: '+order_discount);
			order_shp_type	= (localStorage.getItem('order_shp_type') != 'undefined') ? localStorage.getItem('order_shp_type') : 1;
			console.log('order_shp_type: '+order_shp_type);
			order_coupon	= (localStorage.getItem('order_coupon') != 'undefined') ? localStorage.getItem('order_coupon') : 0;
			console.log('order_coupon: '+order_coupon);
			coupon_id		= (localStorage.getItem('coupon_id') != 'undefined') ? localStorage.getItem('coupon_id') : 0;
			console.log('coupon_id: '+coupon_id);
			coupon_disc		= (localStorage.getItem('coupon_disc') != 'undefined') ? localStorage.getItem('coupon_disc') : 0;
			console.log('coupon_disc: '+coupon_disc);
			coupon_disc_type= (localStorage.getItem('coupon_disc_type') != 'undefined') ? localStorage.getItem('coupon_disc_type') : '';
			console.log('coupon_disc_type '+coupon_disc_type);
			coupon_applied	= (localStorage.getItem('coupon_applied') != 'undefined') ? localStorage.getItem('coupon_applied') : 1;
			console.log('coupon_applied: '+coupon_applied);

			// Paso de Confirmación(PosFecha)
			if( $('#step').length && $('#step').val() == '6' ){
				if( localStorage.getItem('postdate') != 'undefined' && localStorage.getItem('postdate') != undefined ){
					$('#postdate').val( localStorage.getItem('postdate') );
					console.log('postdate: '+$('#postdate').val());
				}
				if( localStorage.getItem('postdate_date') != 'undefined' && localStorage.getItem('postdate_date') != undefined ){
					var this_pdate = localStorage.getItem('postdate_date');
					$('#postdate_date').val( this_pdate );
					$('#txtPostdate').val( this_pdate );
					console.log('postdate_date: '+this_pdate);
				}
			}
		}

	}


	// Solicita confirmacion de cierre del navegador
	window.onbeforeunload = function exitAlert(){
		if( shop_cart_items.length > 0 && !submit_ok ){
			return "Por favor confirme que desea salir de este sitio.\nLos datos que no se han guardado se perderan";
		}
	}
	window.shop_cart_totals = shop_cart_totals;
	window.order_total_tmp = order_total;
});