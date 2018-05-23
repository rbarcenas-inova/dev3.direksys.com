/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 * Author: Eduardo Cesar Cedillo Jimenez
 */


function validar_email(field)
{
    with (field)
    {
        return (/^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.([a-z]){2,4})$/).test(value);
        }
}

function validar_noempty(field)
{
    with (field)
    {
        if (value==null||value=="")
        {
            return false;
        }
        else {
            return true
        }
        }
}

function validar_status(field){
    with(field){
        if(value=="1"){
            return false;
        }else{
            return true;
        }
        }
}

function validar_numerico(field){
    with(field){
        if(IsNumeric(value) == false){
            return false;
        }else{
            return true;
        }
        }
}

function validar_numerico_keyup(value){
    var cadena="";

    for(i=0; i<value.length; i++){
        if(("0123456789.").indexOf(value.charAt(i))!=-1){
            cadena=(cadena+value.charAt(i));
        }
    }

    return cadena;
}

function validar_flotante(value){   
    return (/^[-+]?([0-9]*\.)?[0-9]+$/).test(value);
}

function validar_flotante_keyup(value){   
    if((/^[-+]?([0-9]*\.)?[0-9]+$/).test(value)){
        return value;
    }else{
        return 0;
    }
}


function validar_numero_sinpunto(evt){
    //Validar la existencia del objeto event
    evt = (evt) ? evt : event;

    //Extraer el codigo del caracter de uno de los diferentes grupos de codigos
    var charCode = (evt.charCode) ? evt.charCode : ((evt.keyCode) ? evt.keyCode : ((evt.which) ? evt.which : 0));

    //Predefinir como valido
    var respuesta = true;

    //Validar si el codigo corresponde a los No Aceptables
    if ( !(charCode <= 13 || (charCode >= 48 && charCode <= 57))){
        //Asignar FALSE a la respuesta si es de los NO aceptables
        respuesta = false;
    }

    //Regresar la respuesta
    return respuesta;
}

// Devuelve la cadena sin caracteres diferentes a alfanumericos y _
function validar_idKey(){
    var valorRetorno="";

    // VALIDACION DE ID'S GENERAL
    if(arguments.length==1){
        valorRetorno=arguments[0].replace(/[\W]/g, "");

    // VALIDACIONES DE ID'S 'ESPECIALES'
    }else if(arguments.length==2){
        var charsExtra="";

        if(arguments[1]=="serie") charsExtra="-";
        else if(arguments[1]=="marcaVeh") charsExtra="-_ ().áéíóúÁÉÍÓÚÑñ";
        else if(arguments[1]=="user") charsExtra="-_.@";
        else if(arguments[1]=="historial") charsExtra=" áéíóúÁÉÍÓÚÑñ_-";
        else if(arguments[1]=="catSubcat") charsExtra="-_ ()!¡¿?.áéíóúÁÉÍÓÚÑñ";

        var cadena="";

        for(i=0; i<arguments[0].length; i++){
            if(("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"+charsExtra).indexOf(arguments[0].charAt(i))!=-1){
                cadena=(cadena+arguments[0].charAt(i));
            }
        }

        valorRetorno=cadena;
    }

    return valorRetorno;
}
function isNumberKey(evt)
{
    var charCode = (evt.which) ? evt.which : event.keyCode
    if (charCode > 31 && (charCode < 48 || charCode > 57))
        return false;
    return true;
}

function justNum(id)
{
    var info = document.getElementById(''+id).value;
    var filtered = info.replace(/[^0-9]+/g, '');
    document.getElementById(''+id).value = filtered;

}