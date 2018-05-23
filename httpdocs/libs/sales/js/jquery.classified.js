(function($){

	$.fn.extend({

		classified: function(options_user){

			var options_default = {
				charReplace: '#',
				eventChange: 'blur',
				nameLocalStorage: 'self',
				encryptValue: false,
				delayTime: 300,
				excludeCount: 0,
			};
			var options = $.extend({}, options_default, options_user);

			// Función para validar los caracteres pulsados por el usuario
			var validate_key = function(event){
				var ctrlkeys = [16,17,18,20,33,34,35,123];
				if( event.which !== 0 && !event.ctrlKey && !event.metaKey && !event.altKey && ctrlkeys.indexOf(event.keyCode) == -1 ){
			        return true;
			    }else{
			    	return false;
			    }
			};

			// Funcionalidad para ocultar los datos
			return this.each(function(index, el) {

				var $this = $(this);
				var this_name_var = '';

				// Define el nombre de la variable que contendrá el valor original en localStorage
				if( options.nameLocalStorage == 'self' ){
					if( $this.attr('id') != undefined )
						this_name_var = $this.attr('id');
					else if( $this.attr('name') != undefined )
						this_name_var = $this.attr('name');
					else
						return "ERROR: Element ID is required";
				}else{
					this_name_var = options.nameLocalStorage;
				}

				// Si el input ya cuenta con un valor en localStorage
				if( localStorage.getItem(this_name_var) != undefined && localStorage.getItem(this_name_var) != '' ){
					var old_string = localStorage.getItem(this_name_var);
					var text_length = old_string.length;
					var this_string = '';
					for(var i=0; i<(text_length - options.excludeCount); i++){
						this_string += options.charReplace;
					}
					var str_exclude = (options.excludeCount > 0) ? old_string.substr(-options.excludeCount) : '';
					$this.val(this_string + str_exclude);
				}

				// Ejecuta la sustitución del valor original por el enmascaramiento
				if( options.eventChange == 'blur' ){

					$this.keypress(function(event) {
						// keyCode = 8 :: Borrar
						if( validate_key(event) && event.keyCode != 8 ){							
							var this_maxlength = ($this.attr('maxlength') != undefined && $this.attr('maxlength') != '') ? $this.attr('maxlength') : 0;
							if( (this_maxlength > 0 && $this.val().length < this_maxlength) || this_maxlength == 0 )
								return true;
							else
								return false;
						// permite borrar
						}else if( event.keyCode == 8 ) {
							var this_val = localStorage.getItem(this_name_var)
							var new_val = this_val.substr(0, (this_val.length-1));
							localStorage.setItem(this_name_var, new_val);

							return true;
						// si no es la tecla de borrado o un caracter válido
						}else{
							return false;
						}
					}).click(function(event) {
						console.log($this.val().indexOf('#'));
						if( $this.val().indexOf('#') >= 0 || $this.val().length == 0 ){
							$this.val('');
						}
					});

					$this.blur(function(event) {

						var text_length = $this.val().length;
						if( text_length > 0 && $this.val().indexOf('#') == -1 ){
							var old_string = $this.val();
							var this_string = '';
							for(var i=0; i<(text_length - options.excludeCount); i++){
								this_string += options.charReplace;
							}
							setTimeout(function(){
								localStorage.setItem(this_name_var, $this.val());
								var str_exclude = (options.excludeCount > 0) ? old_string.substr(-options.excludeCount) : '';
								$this.val(this_string + str_exclude);
							}, options.delayTime);
						}else if( (localStorage.getItem(this_name_var) != 'undefined' || localStorage.getItem(this_name_var) != undefined) && localStorage.getItem(this_name_var) != '' ){
							var old_string = localStorage.getItem(this_name_var);

							text_length = old_string.length;
							var this_string = '';
							for(var i=0; i<(text_length - options.excludeCount); i++){
								this_string += options.charReplace;
							}
							var str_exclude = (options.excludeCount > 0) ? old_string.substr(-options.excludeCount) : '';
							$this.val(this_string + str_exclude);
						}

					});

				}else if( options.eventChange == 'keyup' ){

					// Controla el movimiento del cursor dentro del input
					var limit = false;
					$this.keypress(function(event) {
						// keyCode = 8 :: Borrar
						if( validate_key(event) && event.keyCode != 8 ){
							var this_maxlength = ($this.attr('maxlength') != undefined && $this.attr('maxlength') != '') ? $this.attr('maxlength') : 0;
							console.log(this_maxlength+' -> '+$this.val().length);
							if( (parseInt(this_maxlength) > 0 && parseInt($this.val().length) < parseInt(this_maxlength)) || parseInt(this_maxlength) === 0 ){
								console.log(event.key);
								var this_val = localStorage.getItem(this_name_var);
								this_val = ( this_val === 'null' || this_val === null ) ? '' : this_val;							
								localStorage.setItem(this_name_var, this_val+event.key);

								limit = false;
								event.preventDefault();
							}else{
								limit = true;
								console.log('no');
								return false;
							}
						// permite borrar
						}else if( event.keyCode == 8 ) {
							var this_val = localStorage.getItem(this_name_var)
							var new_val = this_val.substr(0, (this_val.length-1));
							localStorage.setItem(this_name_var, new_val);

							limit = false;

							return true;
						// si no es la tecla de borrado o un caracter válido
						}else{
							return false;
						}
					// Oculta el valor original
					}).keyup(function(event) {
						if( validate_key(event) && event.keyCode != 8 && !limit ){
							var this_val = ($this.val()) ? $this.val() : '';
							$this.val( this_val+event.key );
							setTimeout(function(){					
								var new_val = $this.val().replace(/[^#]/gi, options.charReplace);
								$this.val(new_val);
							}, options.delayTime, this_val);
						}
					// posiciona siempre el cursor al final del texto
					}).click(function(event) {
						var this_val = $this.val();
						$this.val('').val(this_val);
					
					});

				}

			});//Fin foreach			

		}//Fin de la funcion principal classified

	});
	
})(jQuery)