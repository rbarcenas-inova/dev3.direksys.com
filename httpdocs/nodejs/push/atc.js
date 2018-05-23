var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
//var mysql = require('mysql');
var html_salida = '';
app.get('/', function(req, res) {
  var url = req.url.split('?')[0];
  var pars = req.url.split('?')[1];
  if(req.url.split('?').length > 1)
          var param = req.url.split('?')[1].split('&');
  else
          var param = '';
  if(param.length > 0){
    var extension = param[0].split('=');
    var cliente = param[1].split('=');
    cliente = cliente.replace('+','');
    var origen = param[2].split('=');
    var fecha = new Date();
    console.log("LLAMADA -->"+fecha.toString());
    console.log("Cliente::"+cliente[1]+" | Destino::"+extension[1]);
    var DB = require('./modulos/mysql.js');
    var MySQL = new DB();
    var html_tipificar = "<script>$(\"#fancybox-overlay\").unbind(\"click\");" +
      "$(\"#tipificar\" ).click(function() { \n" +
        "var tipo = $(\"#tipo option:selected\").text();\n" + 
        "var subtipo = $(\"#subtipo option:selected\").text();\nvar error = 0;" +
        "if(tipo == ''){error = 1;} if(subtipo == ''){error = 1;}\n" +
        "if(error == 1) {\n" +
          "alert('Primero selecciona un tipo y subtipo para clasificar la llamada');\n" +
        "}else{\n" +
          //"console.log($('#tipificacion').serialize());\n" +
          "$.ajax({ url: \"http://mx.direksys.com/cgi-bin/common/apps/tipificacion_crm?user=\" + $('#admin_users').html() + \"&\" + $('#tipificacion').serialize() ," +
          "context: document.body}).done(function( data ) {" + 
          "if(data){ $(\"#tipificar\" ).css('visibility', 'hidden'); };});\n" + 
        "}\n" +
      "});\n" + 
      "$(\"#tipo\" ).change(function() { " +
        "$(\"select option:selected\").each(function() { " +
            "if($( this ).text() == 'Informativo'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Llamada cortada'         >Llamada cortada         </option>\");\n" +
              "subtipos.append(\"<option value='Contingencia'            >Contingencia            </option>\");\n" +
              "subtipos.append(\"<option value='Pura Oferta'             >Pura Oferta             </option>\");\n" +
              "subtipos.append(\"<option value='Mercado Libre'           >Mercado Libre           </option>\");\n" +
              "subtipos.append(\"<option value='Call Center MTY'         >Call Center MTY         </option>\");\n" +
              "subtipos.append(\"<option value='Broma'                   >Broma                   </option>\");\n" +
              "subtipos.append(\"<option value='Incidencia en sistema'   >Incidencia en sistema   </option>\");\n" +
              "subtipos.append(\"<option value='Producto de otra empresa'>Producto de otra empresa</option>\");\n" +
              "subtipos.append(\"<option value='Informacion de Garantias'>Informacion de Garantias</option>\");\n" +
              "subtipos.append(\"<option value='Orden VIP'               >Orden VIP               </option>\");\n" +
              "subtipos.append(\"<option value='Informacion de Productos'>Informacion de Productos</option>\");\n" +
              "subtipos.append(\"<option value='Citas'  >Citas  </option>\");\n" +
              "subtipos.append(\"<option value='Fedex'  >Fedex  </option>\");\n" +
              "subtipos.append(\"<option value='Carssa'  >Carssa  </option>\");\n" +
              "subtipos.append(\"<option value='Estafeta'  >Estafeta  </option>\");\n" +
              "subtipos.append(\"<option value='UPS'  >UPS  </option>\");\n" +
              "subtipos.append(\"<option value='Verkko'  >Verkko  </option>\");\n" +
              "subtipos.append(\"<option value='TDL'  >TDL  </option>\");\n" +
              "subtipos.append(\"<option value='Promos'  >Promos  </option>\");\n" +
              "subtipos.append(\"<option value='Atc Entregas Directas'  >Atc Entregas Directas  </option>\");\n" +
              "subtipos.append(\"<option value='Informacion de entrega dentro de tiempo' >Informacion de entrega dentro de tiempo</option>\");\n" +
              "subtipos.append(\"<option value='Informacion de entrega sin inventario' >Informacion de entrega sin inventario</option>\");\n" +
              "subtipos.append(\"<option value='Informacion de entrega en transito' >Informacion de entrega en transito</option>\");\n" +
            "} \n" +
            "if($( this ).text() == 'Tramites'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Garantias'              >Garantias              </option>\");\n" +
              "subtipos.append(\"<option value='Cancelacion de llamada' >Cancelacion de llamada </option>\");\n" +
              "subtipos.append(\"<option value='Cambio Mayor'           >Cambio Mayor           </option>\");\n" +
              "subtipos.append(\"<option value='Manuales e instructivos'>Manuales e instructivos</option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Tickets'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Envio urgente'                 >Envio urgente                 </option>\");\n" +
              "subtipos.append(\"<option value='Envio Drop Shipping'           >Envio Drop Shipping           </option>\");\n" +
              "subtipos.append(\"<option value='Envio de piezas Body Crunch'   >Envio de piezas Body Crunch   </option>\");\n" +
              "subtipos.append(\"<option value='Cancelacion de Inova Club'     >Cancelacion de Inova Club     </option>\");\n" +
              "subtipos.append(\"<option value='Envio por cobro no registrado' >Envio por cobro no registrado </option>\");\n" +
              "subtipos.append(\"<option value='Envio parcial con reembolso'   >Envio parcial con reembolso   </option>\");\n" +
              "subtipos.append(\"<option value='Reenvio'                       >Reenvio                       </option>\");\n" +
              "subtipos.append(\"<option value='Cambio fisico'                 >Cambio fisico                 </option>\");\n" +
              "subtipos.append(\"<option value='Reposiciones'                  >Reposiciones                  </option>\");\n" +
              "subtipos.append(\"<option value='Pedimentos'                    >Pedimentos                    </option>\");\n" +
              "subtipos.append(\"<option value='Guia sin movimiento'           >Guia sin movimiento           </option>\");\n" +
              "subtipos.append(\"<option value='Grabacion de promesa falsa RVT'>Grabacion de promesa falsa RVT</option>\");\n" +
              "subtipos.append(\"<option value='Siniestro'                     >Siniestro                     </option>\");\n" +
              "subtipos.append(\"<option value='Entrega con faltante'          >Entrega con faltante          </option>\");\n" +
              "subtipos.append(\"<option value='Cliente no reconoce firma'     >Cliente no reconoce firma     </option>\");\n" +
              "subtipos.append(\"<option value='Factura'                       >Factura                       </option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Supervision'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Matutino'  >Matutino  </option>\");\n" +
              "subtipos.append(\"<option value='Vespertino'>Vespertino</option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Transferencia'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Ventas'                                   >Ventas                                   </option>\");\n" +
              "subtipos.append(\"<option value='Fidelizacion'                             >Fidelizacion                             </option>\");\n" +
              "subtipos.append(\"<option value='Internet'                                 >Internet                                 </option>\");\n" +
              "subtipos.append(\"<option value='Validaciones'                             >Validaciones                             </option>\");\n" +
              "subtipos.append(\"<option value='Garantias'                                >Garantias                                </option>\");\n" +
              "subtipos.append(\"<option value='Area de Atencion y Solucion Especializada'>Area de Atencion y Solucion Especializada</option>\");\n" +
              "subtipos.append(\"<option value='Confirmaciones'                           >Confirmaciones                           </option>\");\n" +
              "subtipos.append(\"<option value='Atencion a Clientes'                      >Atencion a Clientes                      </option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Confirmado con error'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Nombre'>Nombre</option>\");\n" +
            "subtipos.append(\"<option value='Ortografia'>Ortografia</option>\");\n" +
            "subtipos.append(\"<option value='Falta de Apellidos'>Falta de Apellidos</option>\");\n" +
            "subtipos.append(\"<option value='Apellidos Invertidos'>Apellidos Invertidos</option>\");\n" +
            "subtipos.append(\"<option value='Telefono'>Telefono</option>\");\n" +
            "subtipos.append(\"<option value='Sin Lada'>Sin Lada</option>\");\n" +
            "subtipos.append(\"<option value='Error en Lada'>Error en Lada</option>\");\n" +
            "subtipos.append(\"<option value='Error de Captura'>Error de Captura</option>\");\n" +
            "subtipos.append(\"<option value='Calle'>Calle</option>\");\n" +
            "subtipos.append(\"<option value='Numero'>Numero</option>\");\n" +
            "subtipos.append(\"<option value='Colonia'>Colonia</option>\");\n" +
            "subtipos.append(\"<option value='Entre Calles'>Entre Calles</option>\");\n" +
            "subtipos.append(\"<option value='Referencias'>Referencias</option>\");\n" +
            "subtipos.append(\"<option value='Codigo Postal'>Codigo Postal</option>\");\n" +
            "subtipos.append(\"<option value='Estado'>Estado</option>\");\n" +
            "subtipos.append(\"<option value='Ortografia'>Ortografia</option>\");\n" +
            "subtipos.append(\"<option value='Posfecha mayor a 15 dias'>Posfecha mayor a 15 dias</option>\");\n" +
            "subtipos.append(\"<option value='Error en dias Solicitados'>Error en dias Solicitados</option>\");\n" +
            "subtipos.append(\"<option value='No se indica posfecha'>No se indica posfecha</option>\");\n" +
            "subtipos.append(\"<option value='Dia exacto de entrega'>Dia exacto de entrega</option>\");\n" +
            "subtipos.append(\"<option value='Tiempo menor a sistema'>Tiempo menor a sistema</option>\");\n" +
            "subtipos.append(\"<option value='Promete Regalos'>Promete Regalos</option>\");\n" +
            "subtipos.append(\"<option value='Talla'>Talla</option>\");\n" +
            "subtipos.append(\"<option value='Color'>Color</option>\");\n" +
            "subtipos.append(\"<option value='Cantidad'>Cantidad</option>\");\n" +
            "subtipos.append(\"<option value='Producto Diferente'>Producto Diferente</option>\");\n" +
            "subtipos.append(\"<option value='Sin gastos de envio'>Sin gastos de envio</option>\");\n" +
            "subtipos.append(\"<option value='Precio Diferente'>Precio Diferente</option>\");\n" +
            "subtipos.append(\"<option value='Tipo de pago (COD y PP)'>Tipo de pago (COD y PP)</option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Cancelado'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Tiempos de envio'>Tiempos de envío</option>\");\n" +
            "subtipos.append(\"<option value='Forma de pago'>Forma de pago</option>\");\n" +
            "subtipos.append(\"<option value='Precio Diferente'>Precio Diferente</option>\");\n" +
            "subtipos.append(\"<option value='Datos insuficientes'>Datos insuficientes</option>\");\n" +
            "subtipos.append(\"<option value='Solo pidio informes'>Solo pidio informes</option>\");\n" +
            "subtipos.append(\"<option value='Pedido Duplicado'>Pedido Duplicado</option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'No confirmado'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value=''>--seleccionar--</option>\");\n" +
              "subtipos.append(\"<option value='Error en transferencia'>Error en transferencia</option>\");\n" +
            "subtipos.append(\"<option value='Cliente cuelga'>Cliente cuelga</option>\");\n" +
            "subtipos.append(\"<option value='Cliente tiene prisa'>Cliente tiene prisa</option>\");\n" +
            "subtipos.append(\"<option value='Error de sistema'>Error de sistema</option>\");\n" +
            "}\n" +
            "if($( this ).text() == 'Confirmado'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
              "subtipos.append(\"<option value='Confirmado'>N/A</option>\");\n" +
            "}\n" +
            "if($( this ).text() == '-- seleccionar --'){ \n" + 
              "var subtipos = $(\"#subtipo\"); subtipos.empty();\n" +
            "}\n" +
          "});" +
      "});" +
    "</script>";
    html_tipificar = html_tipificar + "\n<center><h2>Nueva llamada de "+cliente[1]+"</h2></center>\n<center><h3>Tipificar la llamada</h3>\n<form id='tipificacion' name=\"tipificacion\" >\n<label>Area&nbsp;</label><select name=\"area\" id=\"area\"><option value=\"Telemarketing\" >Telemarketing</option><option value=\"Fidelizacion\" >Fidelizacion</option><option value=\"Internet\" >Internet</option></select>\n" + 
      "<br/><br/><label>Tipo&nbsp;</label><select name=\"tipo\" id=\"tipo\"><option value=\"\" >-- seleccionar --</option><option value=\"Informativo\" >Informativo</option><option value=\"Tramites\" >Tramites</option><option value=\"Tickets\" >Tickets</option><option value=\"Supervision\" >Supervision</option><option value=\"Transferencia\" >Transferencia</option><option value=\"Confirmado con error\" >Confirmado con error</option><option value=\"Cancelado\" >Cancelado</option><option value=\"No confirmado\" >No confirmado</option><option value=\"Confirmado\" >Confirmado</option></select><br/>\n" + 
      "<br/><label>Sub Tipo&nbsp;</label><select name=\"subtipo\" id=\"subtipo\"></select>\n" + 
      "<br/><br/><label>Pedido</label><input type=\"text\" name=\"id_order\" id=\"id_order\" value=\"\" />\n";
    html_tipificar = html_tipificar + "\n<br/><br/><input type='button' class='button' name='tipificar' id='tipificar' value='Tipificar'><input type=\"hidden\" value=\"" + cliente[1] + "\" name=\"caller_id\"/>";
    var html_cola = "<center><input type=\"button\" href=\"/cgi-bin/mod/crm/dbman?cmd=opr_crmtickets&add=1&caller_id=" + cliente[1] + "\" " +
                      "onclick=\"window.open(this.getAttribute('href'));return false;\" value=\"Crear un nuevo ticket\" class=\"button\"></center>";
    //</form>";
  //-------------------
  // TMK
  //-------------------
    var ordenes = MySQL.query("SELECT cus.ID_customers, cus.FirstName, cus.LastName1, cus.LastName2, cus.Phone1, cus.Phone2, cus.Cellphone, ord.ID_orders, date_format(ord.Date,'%d/%m%Y') Date, ord.Status " +
      "FROM direksys2_e2.sl_customers cus " +
      "INNER JOIN direksys2_e2.sl_orders ord using(ID_customers) "+
      "WHERE cus.CID='"+cliente[1]+"' AND cus.Status='Active' OR cus.Phone1='"+cliente[1]+"' OR cus.Phone2='"+cliente[1]+"' OR cus.Cellphone='"+cliente[1]+"' "+
      "ORDER BY ord.Date DESC LIMIT 3;", function(rst_ordenes){
      var int_ordenes = 0;
      var html_ordenes = '<center><h3>Ordenes de ese numero</h3><table><tr><td>Nombre</td><td>Apellidos</td><td>Orden</td><td>Fecha</td><td>Estatus</td><td>&nbsp;</td></tr>';
      rst_ordenes.forEach(function(orden) {
        int_ordenes++;
        if(orden.Status == 'Cancelled') {
          var color = "<span style=\"color:red;\">"+orden.Status+"</span>";
        }
        if(orden.Status == 'Processed') {
          var color = "<span style=\"color:blue;\">"+orden.Status+"</span>";
        }
        if(orden.Status == 'Shipped') {
          var color = "<span style=\"color:green;\"><strong>"+orden.Status+"</strong></span>";
        }
        html_ordenes = html_ordenes + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\">\n";
        html_ordenes = html_ordenes + "<td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">"+orden.FirstName+"</td><td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.open(this.getAttribute('href'));return false;\">"+orden.LastName1+" "+orden.LastName2+"</td><td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">"+orden.ID_orders+"</td><td>"+orden.Date+"</td><td>"+color+"</td><td><a href=\"#\" onclick='window.open(\"http://mx.direksys.com/cgi-bin/common/apps/ajaxbuild?ajaxbuild=fastCheckOrder&id_order="+orden.ID_orders+"&noajax=yes\",\"_blank\",\"toolbar=no, scrollbars=yes, resizable=no, location=no, top=50, left=50, width=400, height=400\");'><img src=\"http://mx.direksys.com/sitimages//default/view.png\"/></a></td></tr>\n";
      });
      html_ordenes = html_ordenes + "</table></center>";
      var int_tickets = 0;
      var tickets = MySQL.query("SELECT ID_crmtickets,ID_ref,Type,Description,Status FROM direksys2_e2.sl_crmtickets where caller_id='"+cliente[1]+"' ORDER BY Date DESC;"
      , function(rst_tickets){
        var html_tickets = '<center><h3>Tickets de ese numero</h3><table width=800px><tr><td>Ticket</td><td>Referencia</td><td>Tipo</td><td>Descipcion</td><td>Estatus</td><td></td></tr>';
        rst_tickets.forEach(function(ticket) {
          int_tickets++;
          if(ticket.Status == 'Closed unsuccessful') {
            var color = "<span style=\"color:red;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'In Process') {
            var color = "<span style=\"color:blue;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'New') {
            var color = "<span style=\"color:blue;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'Closed successful') {
            var color = "<span style=\"color:green;\"><strong>"+ticket.Status+"</strong></span>";
          }
          html_tickets = html_tickets + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+ticket.ID_orders+"\" onclick=\";window.open(this.getAttribute('href'));return false;\">\n";
          html_tickets = html_tickets + "<td>"+ticket.ID_crmtickets+"</td><td>"+ticket.ID_ref+"</td><td>"+ticket.Type+"</td><td>"+ticket.Description+"</td><td>"+color+"</td><td><a href=\"#\" onclick='window.open(\"http://mx.direksys.com/cgi-bin/mod/crm/dbman?cmd=opr_crmtickets&view="+ticket.ID_crmtickets+"\",\"_blank\",\"toolbar=no, scrollbars=yes, resizable=no, location=no, top=50, left=50, width=400, height=400\");'><img src=\"http://mx.direksys.com/sitimages//default/view.png\"/></a></td></tr>\n";
        });
        html_tickets = html_tickets + "</table></center>";
        io.emit('atc_cia2',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" + html_tickets + "<br/><hr/>" + html_cola);
        io.emit('atc_cia10',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" + html_tickets + "<br/><hr/>" + html_cola);
      });
      if(int_tickets ==0) {
        io.emit('atc_cia2',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" +  html_cola);
        io.emit('atc_cia10',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" +  html_cola);
      }
      if(int_ordenes == 0) {
        io.emit('atc_cia2',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_cola); 
        io.emit('atc_cia10',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"2\" /></center></form>\n<br/><hr/>" + html_cola); 
      }
    });
  //-------------------
  // MOW
  //-------------------
    var ordenes = MySQL.query("SELECT cus.ID_customers, cus.FirstName, cus.LastName1, cus.LastName2, cus.Phone1, cus.Phone2, cus.Cellphone, ord.ID_orders, date_format(ord.Date,'%d/%m%Y') Date, ord.Status " +
      "FROM direksys2_e4.sl_customers cus " +
      "INNER JOIN direksys2_e4.sl_orders ord using(ID_customers) "+
      "WHERE cus.CID='"+cliente[1]+"' AND cus.Status='Active' OR cus.Phone1='"+cliente[1]+"' OR cus.Phone2='"+cliente[1]+"' OR cus.Cellphone='"+cliente[1]+"' "+
      "ORDER BY ord.Date DESC LIMIT 3;", function(rst_ordenes){
      var int_ordenes = 0;
      var html_ordenes = '<center><h3>Ordenes de ese numero</h3><table><tr><td>Nombre</td><td>Apellidos</td><td>Orden</td><td>Fecha</td><td>Estatus</td><td>&nbsp;</td></tr>';
      rst_ordenes.forEach(function(orden) {
        int_ordenes++;
        if(orden.Status == 'Cancelled') {
          var color = "<span style=\"color:red;\">"+orden.Status+"</span>";
        }
        if(orden.Status == 'Processed') {
          var color = "<span style=\"color:blue;\">"+orden.Status+"</span>";
        }
        if(orden.Status == 'Shipped') {
          var color = "<span style=\"color:green;\"><strong>"+orden.Status+"</strong></span>";
        }
        html_ordenes = html_ordenes + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\">\n";
        html_ordenes = html_ordenes + "<td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">"+orden.FirstName+"</td><td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.open(this.getAttribute('href'));return false;\">"+orden.LastName1+" "+orden.LastName2+"</td><td href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+orden.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">"+orden.ID_orders+"</td><td>"+orden.Date+"</td><td>"+color+"</td><td><a href=\"#\" onclick='window.open(\"http://mx.direksys.com/cgi-bin/common/apps/ajaxbuild?ajaxbuild=fastCheckOrder&id_order="+orden.ID_orders+"&noajax=yes\",\"_blank\",\"toolbar=no, scrollbars=yes, resizable=no, location=no, top=50, left=50, width=400, height=400\");'><img src=\"http://mx.direksys.com/sitimages//default/view.png\"/></a></td></tr>\n";
      });
      html_ordenes = html_ordenes + "</table></center>";
      var int_tickets = 0;
      var tickets = MySQL.query("SELECT ID_crmtickets,ID_ref,Type,Description,Status FROM direksys2_e4.sl_crmtickets where caller_id='"+cliente[1]+"' ORDER BY Date DESC;"
      , function(rst_tickets){
        var html_tickets = '<center><h3>Tickets de ese numero</h3><table width=800px><tr><td>Ticket</td><td>Referencia</td><td>Tipo</td><td>Descipcion</td><td>Estatus</td></tr>';
        rst_tickets.forEach(function(ticket) {
          int_tickets++;
          if(ticket.Status == 'Closed unsuccessful') {
            var color = "<span style=\"color:red;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'In Process') {
            var color = "<span style=\"color:blue;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'New') {
            var color = "<span style=\"color:blue;\">"+ticket.Status+"</span>";
          }
          if(ticket.Status == 'Closed successful') {
            var color = "<span style=\"color:green;\"><strong>"+ticket.Status+"</strong></span>";
          }
          html_tickets = html_tickets + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+ticket.ID_orders+"\" onclick=\";window.open(this.getAttribute('href'));return false;\">\n";
          html_tickets = html_tickets + "<td>"+ticket.ID_crmtickets+"</td><td>"+ticket.ID_ref+"</td><td>"+ticket.Type+"</td><td>"+ticket.Description+"</td><td>"+color+"</td><td><a href=\"#\" onclick='window.open(\"http://mx.direksys.com/cgi-bin/mod/crm/dbman?cmd=opr_crmtickets&view="+ticket.ID_crmtickets+"\",\"_blank\",\"toolbar=no, scrollbars=yes, resizable=no, location=no, top=50, left=50, width=400, height=400\");'><img src=\"http://mx.direksys.com/sitimages//default/view.png\"/></a></td></tr>\n";
        });
        html_tickets = html_tickets + "</table></center>";
        io.emit('atc_cia4',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"4\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" + html_tickets + "<br/><hr/>" + html_cola);
      });
      if(int_tickets ==0) {
        io.emit('atc_cia4',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"4\" /></center></form>\n<br/><hr/>" + html_ordenes + "<br/><hr/>" +  html_cola);
      }
      if(int_ordenes == 0) {
        io.emit('atc_cia4',extension[1] + '|' + html_tipificar + "<input type=\"hidden\" name=\"e\" value=\"4\" /></center></form>\n<br/><hr/>" + html_cola); 
      }
    });
    res.sendFile('/home/www/node/push/vacio.html');
  }else{
    res.sendFile('/home/www/node/push/index.html');
  }
  MySQL.query("INSERT INTO direksys2_e2.sl_crmcalls SET origen='" + cliente[1] + "', destino='" + extension[1] + "', Date=CURDATE(), Time=CURTIME();",
    function(rst_ordenes){
      console.log("Insertar en estadisticas direksys2_e2.sl_crmcalls\n");
  });
  console.log("<-- FIN PROCESO\n");
});

io.on('connection', function(socket){
  socket.on('atc_cia2', function(msg){
    var tmp = msg.split(":");
        io.emit('atc_cia2', msg);
  });
  socket.on('atc_cia4', function(msg){
    var tmp = msg.split(":");
        io.emit('atc_cia4', msg);
  });
  socket.on('atc_cia10', function(msg){
    var tmp = msg.split(":");
        io.emit('atc_cia10', msg);
  });
});

http.listen(8001, function(){
  console.log('listening on *:8001');
});
