  // el código se ejecutará cuando la página esté totalmente cargada
  $(document).ready( function(){
  
    // obtenemos el botón de búsqueda y le aÃ±adimos un comportamiento al evento onClick
    $("input:submit").click(function () {
    
      // obtenemos el valor del campo de búsqueda, el que contiene el texto de la misma
      var tags = $("input:tags").val();

      // hacemos uso del soporte de Ajax que evalua el resultado como un objeto JSON, pasándole como parámetro la url del
      // servicio web de flickr, asignando el texto de la búsqueda. El segundo parámetro de la función es un método de callback
      // que se ejecutará tras la respuesta del servicio y que recibe el objeto JSON en el parámetro data.
      $.getJSON("http://www.dof.gob.mx/indicadores.xml?tags="+tags+"&tagmode=any&format=json&jsoncallback=?",
        function(data){
	
          // limpiamos el contenedor del resultado de la búsqueda.
          $("#doll").empty();
	  
          // por cada uno de los items que contiene el objeto JSON obtenido invoca a una función que recibe el ordinal y el propio item
          $.each(data.items, function(i,item){
	  
            // creamos un nodo de tipo img al que asociamos en su atributo src una referencia a la imagen del item
            // que se encuentra en el campo media.m; 
            // y en sus atributos alt y title el título de la misma.
            // y aÃ±adimos, en la misma línea, el nodo img creado al contenedor de imágenes
            $("<img/>").attr("src", item.media.m).attr("alt", item.title).attr("title", item.title).appendTo("#images");
	    
            // cortamos el proceso al llegar a 20 imágenes
            if ( i == 20 ) return false;
        });
      });
      
      // asignamos el texto de búsqueda al campo de salida del resultado
      $("#tagsToSearch").text(tags);
    });

   // registramos sobre el nodo imagen que mostrará la actividad el comportamiento de mostrarse
   // cuando exista una petición activa
   $("#loading").ajaxStart(function(){
     $(this).show();
   });
       
   // del mismo modo, cuando termine una petición se ocultará
   $("#loading").ajaxComplete(
      function(event,request, settings) {
        $(this).hide();
      }
   );
   
  });