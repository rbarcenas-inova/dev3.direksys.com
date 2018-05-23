<?php
/**
 * @author L.C.I Eduardo Cesar Cedillo
 * @author Oscar Maldonado
 */
require_once '../../../trsBase.php';
extract($_GET, EXTR_PREFIX_ALL, "v");
extract($_POST, EXTR_PREFIX_ALL, "v");
$e=$in['e'];
if(empty($e)){
    $e=$v_e;
    setcookie('e', $e);
}
require_once '../class/db/DbHandler.php';
require_once '../class/dao.catalog.InvoicesDAO.php';
require_once '../class/dao.catalog.InvoicesLinesDAO.php';
require_once '../class/dao.catalog.InvoicesNotesDAO.php';
require_once 'SignatureLayoutCFDI.php';
require_once '../class/com.common.EnLetras.php';
require_once('../../../ftp01.e'.$e.'.php');
#require_once '../../../ftp01.php';

$id_admin_users = isset($usr['id_admin_users']) ? $usr['id_admin_users'] : 0;
/*
 * Parametros generales para la construccion del layout
 */
$file_handler = NULL;
#$file_path = "/home/www/domains/dev.imiranda/dev2.direksys.com/files/".'e'.$e.'/cfdi/spools/';
$file_path = $cfg['path_invoices_tocert'].'e'.$e.'/cfdi/spools/';  //-- parametrizable cfg
$cfdi_online = $cfg['cfdi_online'];
$GLNemisor = $cfg['gln_'.'e'.$e];
$ReceiverIDs = $cfg['walmart_ReceiverIDs'];
$coppel_account1=$cfg['coppel_account1'];
$coppel_account2=$cfg['coppel_account2'];
$customInfo =( isset($cfg['use_customs_info']) && $cfg['use_customs_info'] == 1) ? true : false;

#$Contacto = $cfg['liverpool_contact'];
$ftp_path = $cfg['cfdi_ftp_path'];
if($ftp_path!=''){$ftp_path.='/';}
$filename = "";

//-- Crea el repositorio del mes 
$file_path.=date('Y').'/';
if(!is_dir($file_path)){mkdir($file_path,0777)or die("Error al crear carpeta $file_path");}
$file_path.=date('Ymd').'/';
if(!is_dir($file_path)){mkdir($file_path,0777)or die("Error al crear carpeta $file_path");}

$id_invoice=$v_id_invoice;
$exito = processConfirmedInvoices($id_invoice,$customInfo);
if ($exito) {
    echo 1;
} else {
    echo 0;
}
?>

<?php

function processConfirmedInvoices($ID_invoices = 0,$customInfo) {
    global $file_path;
    global $filename; 
    global $cfdi_online;
    global $GLNemisor;
    global $ReceiverIDs;
    global $ftp_path;
    global $coppel_account1;
    global $coppel_account2;
    #global $Contacto;

    $arr_tipo_cfd = array(
        'ingreso' => 33,
        'egreso' => 61
    );

    $exito = FALSE;
    $status = "Confirmed";

    $invoicesDAO = new InvoicesDAO();
    $invoicesLinesDAO = new InvoicesLinesDAO();
    $invoicesDTO = new InvoicesDTO();
    //-- objeto para la manipulacion del layout
    $spoolLayout = new SignatureCFDILayout();

    // Limite de 1000
    $invoicesDAO->setPagerStart(0);
    $invoicesDAO->setPagerPerPage(1500);

    //---Actualiza ID_customers en cu_invoices
    Update_ID_Customer(true);

    //---

    if ($ID_invoices > 0) {
        //-- Agrega el parametro del ID_invoices para la busqueda especifica
        $invoicesDTO->setID_invoices($ID_invoices);
    }

    $invoicesDTO->setStatus($status);
    //-- Busca los invoices con el status Confirmed
    $vector_invoices = $invoicesDAO->selectRecords($invoicesDTO);
    #if (!empty($vector_invoices)) {
    if (count($vector_invoices)>0) {

        //-- Itera todos los invoices encontrados en la busqueda
        foreach ($vector_invoices as $invoicesDTO) {
            $invoicesLinesDTO = new InvoicesLinesDTO();
            $invoicesLinesDTO->setID_invoices($invoicesDTO->getID_invoices());

            //-- busca los datos de las linas de los invoices
            $vector_invoices_lines = $invoicesLinesDAO->selectRecords($invoicesLinesDTO);
            //-- Verifica que existan partidas en los invoces
            #if (!empty($vector_invoices_lines)) {
            if (count($vector_invoices_lines)>0) {
                //--------------- comienza el proceso -----------------------------------//
                //--- Obtiene los datos del numero de Serie del Invoice en caso de que no tenga asignado  -----------------------
                if (($invoicesDTO->getDocSerial() == "" && $invoicesDTO->getDocNum() == 0) || $invoicesDTO->getDocNum() == 0) {
                    #$arr_serial_num = getInvoiceSerialNum();
                    $arr_serial_num = getInvoiceSerialNum($invoicesDTO->getInvoiceType());
                    $invoicesDTO->setDocSerial($arr_serial_num['doc_serial']);
                    $invoicesDTO->setDocNum($arr_serial_num['doc_num']);
                }
                //-----------------------------------------------------------------------------------------------------------------
                //-- Ensambla el nombre del archivo: {TIPO}_NPG_{RFC_Serie|Folio_ID_INVOICES}
                $RND = $invoicesDTO->getExpediterFiscalCode() . "_" . $invoicesDTO->getDocSerial() . $invoicesDTO->getDocNum() . "_" . $invoicesDTO->getID_invoices();
                $filename = $arr_tipo_cfd[$invoicesDTO->getInvoiceType()] . "_NPG_" . $RND . ".txt";
                //-- Crea el archivo 
                createFile($filename, $file_path);
                //-- Inicio del Spool
                writeFileLine($spoolLayout->getSpoolStart());
                //**********************************************************
                //-- ================ IdDoc
                //**********************************************************
                writeFileLine($spoolLayout->getHeaderDocumentoIdentificacion());

                $docID = new IdentificacionDocumento();
                $docID->setNumeroInterno($invoicesDTO->getID_invoices());
                $docID->setSerie($invoicesDTO->getDocSerial());
                $docID->setFolio($invoicesDTO->getDocNum());
            #@ivanmiranda - La fecha de emisión es la fecha de la base de datos
                #$docID->setFechaEmis(date('Y-m-d H:i:s'));
                $docID->setFechaEmis($invoicesDTO->getDocDate());
                $docID->setFormaPago(sanitizeStr($invoicesDTO->getPaymentType()));

                /*
                if(sanitizeStr($invoicesDTO->getPaymentMethod())=='Credit-Card'){$PayMethod="TARJETA DE CREDITO";}
                elseif(sanitizeStr($invoicesDTO->getPaymentMethod())=='Referenced Deposit'){$PayMethod="DEPOSITO REFERENCIADO";}
                elseif(sanitizeStr($invoicesDTO->getPaymentMethod())=='COD'){$PayMethod="EFECTIVO";}
                else{$PayMethod=(sanitizeStr($invoicesDTO->getPaymentMethod())!=NULL && sanitizeStr($invoicesDTO->getPaymentMethod())!='')?sanitizeStr($invoicesDTO->getPaymentMethod()):'NO IDENTIFICADO';}
                */
                
                // switch(sanitizeStr($invoicesDTO->getPaymentMethod())){
                //     case 'Credit-Card' : $PayMethod="TARJETA DE CREDITO"; break;
                //     case 'Referenced Deposit' : $PayMethod="DEPOSITO REFERENCIADO"; break;
                //     case 'COD' : $PayMethod="EFECTIVO"; break;
                //     case 'Check' : $PayMethod="CHEQUE"; break;
                //     case 'Wire Transfer' : $PayMethod="TRANSFERENCIA ELECTRONICA"; break;
                //     case 'Deposit' : $PayMethod="DEPOSITO"; break;
                //     default : $PayMethod="NO IDENTIFICADO";
                // }
                // if(trim($invoicesDTO->getPaymentDigits())==''){$PayMethod="NO IDENTIFICADO";}

                // switch($invoicesDTO->getID_customers()){
                //     case '100037': $PayMethod='TRANSFERENCIA ELECTRONICA'; break;    // Coppel Ropa
                //     case '100141': $PayMethod='TRANSFERENCIA ELECTRONICA'; break;    //Coppel Muebles
                // }

                #$docID->setMedioPago(sanitizeStr($invoicesDTO->getPaymentMethod()));
                
                ## ISC Alejandro Diaz :: 05-07-2016
                ## Se modifica mapeo de variable para que funcione transparente el Payment_Methos
                $PayMethod = $invoicesDTO->getPaymentMethod();

                $docID->setMedioPago($PayMethod);
                if($invoicesDTO->getConditions()=='' || $invoicesDTO->getConditions()==NUL){$invoicesDTO->setConditions('CONTADO');}
                $docID->setCondPago(sanitizeStr($invoicesDTO->getConditions()));
                if($invoicesDTO->getCreditDays()=='' || $invoicesDTO->getCreditDays()==NULL){$invoicesDTO->setCreditDays('0');}
                $docID->setTermPagoDias(sanitizeStr($invoicesDTO->getCreditDays()));
                

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_doc = $spoolLayout->getDocumentoIdentificacion($docID);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_doc as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ExEmisor
                //**********************************************************
                writeFileLine($spoolLayout->getEmisorDatosHeader());

                $emObj = new EmisorDatos();
                $emObj->setRFCEmisor($invoicesDTO->getExpediterFiscalCode());
                // echo $e;
            #@ivanmiranda:: Para Liverpool se recorta el nombre a 40 caracteres
                if(trim($invoicesDTO->getCustomerFiscalCode()) == "DLI931201MI9" and strtoupper(sanitizeStr($invoicesDTO->getExpediterName())) == "IMPORTACIONES DE MEXICO Y LATINOAMERICA S DE RL DE CV")
                    $emObj->setNmbEmisor("IMP. DE MEX. Y LATINOAMERICA S RL CV");
                else
                    $emObj->setNmbEmisor(strtoupper(sanitizeStr($invoicesDTO->getExpediterName())));
                $emObj->setCdgGLNEmisor($GLNemisor);
                if($invoicesDTO->getVendorID()!='' && $invoicesDTO->getVendorID()!=NULL){$CdgIntEmisor1='INT';}else{$CdgIntEmisor1='';}
                $emObj->setTpoCdgIntEmisor1($CdgIntEmisor1);
                $emObj->setCdgIntEmisor1($invoicesDTO->getVendorID());
                $emObj->setTpoCdgIntEmisor2('');

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_em_datos = $spoolLayout->getEmisorDatos($emObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_em_datos as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ExEmisorDomFiscal
                //**********************************************************
                writeFileLine($spoolLayout->getEmisorDomicilioFiscalHeader());

                $emDomFisObj = new EmisorDomicilioFisacal();
                $emDomFisObj->setCalle(sanitizeStr($invoicesDTO->getExpediterFAddressStreet()));
                $emDomFisObj->setNroExterior(sanitizeStr($invoicesDTO->getExpediterFAddressNum()));
                $emDomFisObj->setNroInterior(sanitizeStr($invoicesDTO->getExpediterFAddressNum2()));
                $emDomFisObj->setColonia(sanitizeStr($invoicesDTO->getExpediterFAddressUrbanization()));
                $emDomFisObj->setLocalidad(sanitizeStr($invoicesDTO->getExpediterFAddressDistrict()));
                $emDomFisObj->setMunicipio(sanitizeStr($invoicesDTO->getExpediterFAddressCity()));
                $emDomFisObj->setEstado(sanitizeStr($invoicesDTO->getExpediterFAddressState()));
                $emDomFisObj->setPais(sanitizeStr($invoicesDTO->getExpediterFAddressCountry()));
                $emDomFisObj->setCodigoPostal(sanitizeStr($invoicesDTO->getExpediterFAddressZipcode()));
                $emDomFisObj->setGLN($GLNemisor);

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_em_domfis = $spoolLayout->getEmisorDomicilioFiscal($emDomFisObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_em_domfis as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ExEmisorLugarExped
                //**********************************************************                
                writeFileLine($spoolLayout->getEmisorLugarExpedicionHeader());

                $emLuExpObj = new EmisorLugarExp();
                $emLuExpObj->setCalle(sanitizeStr($invoicesDTO->getExpediterAddressStreet()));
                $emLuExpObj->setNroExterior(sanitizeStr($invoicesDTO->getExpediterAddressNum()));
                $emLuExpObj->setNroInterior(sanitizeStr($invoicesDTO->getExpediterAddressNum2()));
                $emLuExpObj->setColonia(sanitizeStr($invoicesDTO->getExpediterAddressUrbanization()));
                $emLuExpObj->setLocalidad(sanitizeStr($invoicesDTO->getExpediterAddressDistrict()));                
                $emLuExpObj->setMunicipio(sanitizeStr($invoicesDTO->getExpediterAddressCity()));
                $emLuExpObj->setEstado(sanitizeStr($invoicesDTO->getExpediterAddressState()));
                $emLuExpObj->setPais(sanitizeStr($invoicesDTO->getExpediterAddressCountry()));
                $emLuExpObj->setCodigoPostal(sanitizeStr($invoicesDTO->getExpediterAddressZipcode()));
                $emLuExpObj->setGLN($GLNemisor);

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_em_luexp = $spoolLayout->getEmisorLugarExpedicion($emLuExpObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_em_luexp as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ ExReceptor
                //**********************************************************                
                writeFileLine($spoolLayout->getReceptorDatosHeader());

                $rcObj = new ReceptorDatos();
                $rcObj->setRFCRecep($invoicesDTO->getCustomerFiscalCode());
                $rcObj->setNmbRecep(sanitizeStr($invoicesDTO->getCustomerName()));

                if($invoicesDTO->getCustomerAddressGln()=='' || $invoicesDTO->getCustomerAddressGln()==NULL){
                    $invoicesDTO->setCustomerAddressGln('9000000000009');}
                if($invoicesDTO->getCustomerShpaddressGln()=='' || $invoicesDTO->getCustomerShpaddressGln()==NULL){$glnshp=$invoicesDTO->getCustomerAddressGln();}else{$glnshp=$invoicesDTO->getCustomerShpaddressGln();}
                $rcObj->setCdgGLNRecep($glnshp);

                $rcObj->setCdgSucursal(sanitizeStr($invoicesDTO->getCustomerShpaddressCode()));
                $rcObj->setSucursal(sanitizeStr($invoicesDTO->getCustomerShpaddressAlias()));

                if($invoicesDTO->getCustomerShpaddressContact()==''){
                    switch($invoicesDTO->getID_customers()){
                        case 100042 : $Contacto='0704'; break; #Liverpool Farmacia
                        case 100043 : $Contacto='0706'; break; #Liverpool Belleza
                        case 100044 : $Contacto='602'; break; #Liverpool Deportes
                        default : $Contacto=sanitizeStr($invoicesDTO->getCustomerShpaddressContact());
                    }
                }else{$Contacto=sanitizeStr($invoicesDTO->getCustomerShpaddressContact());}
                $rcObj->setContacto($Contacto);
                
                #$rcObj->setContacto(sanitizeStr($invoicesDTO->getCustomerShpaddressContact()));

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_rc = $spoolLayout->getReceptorDatos($rcObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_rc as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ ExReceptorDomFiscal
                //**********************************************************                 
                writeFileLine($spoolLayout->getReceptorDomicilioFiscalHeader());

                $rcDomFisObj = new ReceptorDomicilioFiscal();
                $rcDomFisObj->setCalle(sanitizeStr($invoicesDTO->getCustomerFAddressStreet()));
                $rcDomFisObj->setNroExterior(sanitizeStr($invoicesDTO->getCustomerFAddressNum()));
                $rcDomFisObj->setNroInterior(sanitizeStr($invoicesDTO->getCustomerFAddressNum2()));
                $rcDomFisObj->setColonia(sanitizeStr($invoicesDTO->getCustomerFAddressUrbanization()));
                $rcDomFisObj->setLocalidad(sanitizeStr($invoicesDTO->getCustomerFAddressDistrict()));
                /*
                switch($invoicesDTO->getID_customers()){
                    #case 100037: $Referencia=($invoicesDTO->getCustomerShpaddressCode()*1)+30000; break;    //Coppel Ropa
                    case 100141: $Referencia=($invoicesDTO->getCustomerShpaddressCode()*1)+30000; break;    //Coppel Muebles
                    default : $Referencia=sanitizeStr($invoicesDTO->getCustomerShpaddressCode());
                }
                */
                $Referencia=sanitizeStr($invoicesDTO->getCustomerShpaddressCode());
                $rcDomFisObj->setReferencia($Referencia);                
                $rcDomFisObj->setMunicipio(sanitizeStr($invoicesDTO->getCustomerFAddressCity()));
                switch($invoicesDTO->getID_customers()){
                    case 100044 : $CustomerFAddressState='DF'; break; #Liverpool
                    default : $CustomerFAddressState=sanitizeStr($invoicesDTO->getCustomerFAddressState());
                }
                $rcDomFisObj->setEstado($CustomerFAddressState);
                $rcDomFisObj->setPais(sanitizeStr($invoicesDTO->getCustomerFAddressCountry()));
                $rcDomFisObj->setCodigoPostal(sanitizeStr($invoicesDTO->getCustomerFAddressZipcode()));
                $rcDomFisObj->setGLN($invoicesDTO->getCustomerAddressGln());
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_domfis = $spoolLayout->getReceptorDomicilioFiscal($rcDomFisObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_domfis as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ ExReceptorLugarRecep
                //**********************************************************                
                writeFileLine($spoolLayout->getReceptorLugarRecepcionHeader());

                $rcdomrecObj = new ReceptorLugarRecp();  
                $rcdomrecObj->setCalle(sanitizeStr($invoicesDTO->getCustomerShpAddressStreet()));
                $rcdomrecObj->setNroExterior(sanitizeStr($invoicesDTO->getCustomerShpAddressNum()));
                $rcdomrecObj->setNroInterior(sanitizeStr($invoicesDTO->getCustomerShpAddressNum2()));
                $rcdomrecObj->setColonia(sanitizeStr($invoicesDTO->getCustomerShpAddressUrbanization()));
                $rcdomrecObj->setLocalidad(sanitizeStr($invoicesDTO->getCustomerShpAddressDistrict()));
                /*
                switch($invoicesDTO->getID_customers()){
                    #case 100037: $Referencia=($invoicesDTO->getCustomerShpaddressCode()*1)+30000; break;    //Coppel Ropa
                    case 100141: $Referencia=($invoicesDTO->getCustomerShpaddressCode()*1)+30000; break;    //Coppel Muebles
                    default : $Referencia=sanitizeStr($invoicesDTO->getCustomerShpaddressCode());
                }
                */
                $Referencia=sanitizeStr($invoicesDTO->getCustomerShpaddressCode());

                $rcdomrecObj->setReferencia($Referencia);
                $rcdomrecObj->setMunicipio(sanitizeStr($invoicesDTO->getCustomerShpAddressCity()));
                switch($invoicesDTO->getID_customers()){
                    case 100044 : $CustomerShpAddressState='DF'; break; #Liverpool
                    default : $CustomerShpAddressState=sanitizeStr($invoicesDTO->getCustomerShpAddressState());
                }
                $rcdomrecObj->setEstado($CustomerShpAddressState);
                $rcdomrecObj->setPais(sanitizeStr($invoicesDTO->getCustomerShpAddressCountry()));
                $rcdomrecObj->setCodigoPostal(sanitizeStr($invoicesDTO->getCustomerShpAddressZipcode()));
                if($invoicesDTO->getCustomerShpaddressGln()=='' || $invoicesDTO->getCustomerShpaddressGln()==NULL){$glnshp=$invoicesDTO->getCustomerAddressGln();}else{$glnshp=$invoicesDTO->getCustomerShpaddressGln();}
                $rcdomrecObj->setGLN($glnshp);

                $arr_rcdomrec = $spoolLayout->getReceptorLugarRecepcion($rcdomrecObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_rcdomrec as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //-- escribe 2 renglones en blanco despues de los datos previos a detalle
                writeFileLine("\r\n\r\n", FALSE);


                //**********************************************************
                //-- ================ Detalle
                //**********************************************************
                writeFileLine($spoolLayout->getDetalleHeader());
                //-- consulta las cabeceras del detalle para su escritura

                $dbh = new DbHandler();
                $dbh->connect();
                $arr_header_detalle = $spoolLayout->getDetalleHeadersDefinition($dbh,$invoicesDTO->getID_invoices());
                //-- imprime las cabeceras 
                $str_output_header = "";
                foreach ($arr_header_detalle as $namespace => $size) {
                    if($namespace != 'Aduana'){
                        $namespace = replaceHeaderNamespace($namespace);
                        $str_output_header .= str_pad($namespace, $size);
                    }else{
                        if($customInfo){
                            foreach ($size as $key => $value) {
                                foreach ($value as $k => $v) {
                                    $str_output_header .= str_pad($k, $v);
                                    # code...
                                }
                            }
                        }
                    }
                }
                //-- escribe las cabeceras en el file
                writeFileLine($str_output_header);

                $arr_taxes = array();
                $TotalLotes=0;
                $TotQty=0;
                foreach ($vector_invoices_lines as &$invoicesLinesDTO) {
                    //-- almacena el valor de los taxes
                    $arr_taxes[$invoicesLinesDTO->getTaxName()][$invoicesLinesDTO->getTaxRate()] += $invoicesLinesDTO->getTax();

                    $detObj = new DetalleConceptos();

                    $detObj->setDetT("M");
                    $detObj->setTpoCodigo1("EAN");
                    if($invoicesLinesDTO->getUPC()=='' || $invoicesLinesDTO->getUPC()==NULL){$invoicesLinesDTO->setUPC('0');}
                    $detObj->setVlrCodigo1(sanitizeStr($invoicesLinesDTO->getUPC()));
                    $detObj->setTpoCodigo2("INT");
                    if($invoicesLinesDTO->getIdSku()=='' || $invoicesLinesDTO->getIdSku()==NULL){$invoicesLinesDTO->setIdSku('0');}
                    $detObj->setVlrCodigo2(sanitizeStr($invoicesLinesDTO->getIdSku()));
                    $detObj->setTpoCodigo3("EXT");
                    if($invoicesLinesDTO->getIdSkuAlias()=='' || $invoicesLinesDTO->getIdSkuAlias()==NULL){$invoicesLinesDTO->setIdSkuAlias('0');}
                    $detObj->setVlrCodigo3(sanitizeStr($invoicesLinesDTO->getIdSkuAlias()));
                    $detObj->setIn("");
                    $detObj->setTpoLis("");
                    $detObj->setDs("ES");
                    $detObj->setDs("");
                    if($invoicesLinesDTO->getIdSkuAlias()==''){$Sku=$invoicesLinesDTO->getUPC();
                    }else{$Sku=$invoicesLinesDTO->getIdSkuAlias();}
                    if($Sku=='' || $Sku<=0){$Sku=$invoicesLinesDTO->getIdSku();}
                    $detObj->setDscItem($Sku.'-'.sanitizeStr($invoicesLinesDTO->getDescription()));
                    $detObj->setQtyItem($invoicesLinesDTO->getQuantity());
                    $TotQty+=$invoicesLinesDTO->getQuantity();
                    $detObj->setUnmdItem($invoicesLinesDTO->getMeasuringUnit());
                    $detObj->setSubQty("");
                    $detObj->setSubC("");
                    $detObj->setPrcBrutoItem($invoicesLinesDTO->getUnitPrice());
                    $detObj->setPrcNetoItem($invoicesLinesDTO->getUnitPrice());
                    if($invoicesLinesDTO->getDiscount()>0){
                        switch($invoicesDTO->getID_customers()){
                            case 100037: $Descue='ZZZ'; break;    //Coppel Ropa
                            case 100141: $Descue='ZZZ'; break;    //Coppel Muebles
                            default : $Descue='';
                        }
                        $Discount=$invoicesLinesDTO->getDiscount();
                    }else{$Descue=''; $Discount='';}
                    $detObj->setDescue($Descue);
                    $detObj->setDescuentoMonto($Discount);
                    $detObj->setTipo1($invoicesLinesDTO->getTaxName());
                    $detObj->setTasaIm1(number_format(($invoicesLinesDTO->getTaxRate() * 100),2));
                    $detObj->setMontoImp1($invoicesLinesDTO->getTax());

                    $detObj->setMontoBrutoItem($invoicesLinesDTO->getAmount());
                #@ivanmiranda :: Correccion fiscal (detalle de descuento)
                    #$MontoNetoItem = $invoicesLinesDTO->getAmount() - $invoicesLinesDTO->getDiscount();
                    $MontoNetoItem = $invoicesLinesDTO->getAmount();
                    $detObj->setMontoNetoItem(number_format($MontoNetoItem,2,'.',''));
                    $MontoTotalItem = ($invoicesLinesDTO->getAmount() - $invoicesLinesDTO->getDiscount())+$invoicesLinesDTO->getTax();
                    $detObj->setMontoTotalItem(number_format($MontoTotalItem,2,'.',''));
                               

                    /*
                    * Version Anterior Aduanas
                    */         
                    // $detObj->setNmbAduana(sanitizeStr($invoicesLinesDTO->getCustomsName()));
                    // $detObj->setNroDcto(sanitizeStr($invoicesLinesDTO->getCustomsNum()));
                    // $detObj->setFechaDcto(sanitizeStr($invoicesLinesDTO->getCustomsDate()));
                    /*
                    switch($invoicesDTO->getID_customers()){
                        case 100037: $PalletInformation='BOX'; $PrepactCant='60'; break;    //Coppel Ropa
                        case 100141: $PalletInformation='BOX'; $PrepactCant='60'; break;    //Coppel Muebles
                        default : $PalletInformation=''; $PrepactCant='60';
                    }*/
                    // $PalletInformation=$invoicesLinesDTO->getPackingType();
                    // $PrepactCant=$invoicesLinesDTO->getPackingUnit();

                    // if($PrepactCant>0){$Prepak=ceil($invoicesLinesDTO->getQuantity()/$PrepactCant);}else{$Prepak='';}
                    // $TotalLotes += $Prepak;
                    // $detObj->setPalletInformation($PalletInformation);
                    // $detObj->setPrepactCant($PrepactCant);                    
                    // $detObj->setSize(sanitizeStr($invoicesLinesDTO->getSize()));
                    // $detObj->setPrepak($Prepak);

                    /*
                    * Version Anterior Aduanas
                    */

                    $OrderID=$invoicesLinesDTO->getID_orders();

                    //-- obtiene arreglo del layout que se escribira en el file

                    $arr_detalle = $spoolLayout->getDetalle($detObj,$dbh,$invoicesLinesDTO);
                    //-- Itera los elementos del arreglo para escribir cada linea en el file
                    $str_output = "";
                    foreach ($arr_detalle as $namespace => $value) {
                        if($namespace != 'Aduanas')
                            $str_output .= str_pad($value, $arr_header_detalle[$namespace]
                                );
                        else
                            if($customInfo){
                                foreach ($value as $key => $v) {
                                    
                                    $str_output.=str_pad($v['NmbAduana'],$arr_header_detalle['Aduana'][$key]['NmbAduana']);
                                    $str_output.=str_pad($v['NroDcto'],$arr_header_detalle['Aduana'][$key]['NroDcto']);
                                    $str_output.=str_pad($v['FechaDcto'],$arr_header_detalle['Aduana'][$key]['FechaDcto']);
                                    $str_output.=str_pad($v['PalletInformation'],$arr_header_detalle['Aduana'][$key]['PalletInformation']);
                                }
                            }

                    }
                    writeFileLine($str_output);
                }
                //-- escribe 4 renglones en blanco despues de los datos detalle
                writeFileLine("\r\n\r\n\r\n", FALSE);
                //-- escribe el fin de detalle
                writeFileLine($spoolLayout->getDetalleFooter());
                //--- escribe un espacio en blanco
                writeFileLine("\r\n", FALSE);

                //**********************************************************
                //-- ================ Totales
                //**********************************************************                
                writeFileLine($spoolLayout->getTotalesHeader());

                //-- convierte la cantidad total del invoice a letras
                $letrasCls = new EnLetras();
                $letras = $letrasCls->ValorEnLetras($invoicesDTO->getInvoiceTotal(), $invoicesDTO->getCurrency());
                //-----------------------------------

                #@ivanmiranda :: Prueba de correccion para facturas que de pronto genera un monto cero
                if($invoicesDTO->getInvoiceTotal() == 0){
                #las facturas en cero no se termina el timbrado
                    closeFile();
                    unlink($file_path.$filename);
                    continue;
                }

                $totalesDocObj = new TotalesDoc();
                if(trim($invoicesDTO->getCustomerFiscalCode()) == "DLI931201MI9")
                    $totalesDocObj->setMoneda("MXN");
                else
                    $totalesDocObj->setMoneda($invoicesDTO->getCurrency());
                $totalesDocObj->setFctConv($invoicesDTO->getCurrencyExchange());
                $totalesDocObj->setSubTotal($invoicesDTO->getInvoiceNet());
                $totalesDocObj->setMntDcto($invoicesDTO->getDiscount());
                $MntBase = $invoicesDTO->getInvoiceNet() - $invoicesDTO->getDiscount();
                $totalesDocObj->setMntBase($MntBase);
                $totalesDocObj->setMntImp($invoicesDTO->getTotalTaxesTransfered());
                $totalesDocObj->setMntRet($invoicesDTO->getTotalTaxesDetained());
                $totalesDocObj->setVlrPagar($invoicesDTO->getInvoiceTotal());
                $totalesDocObj->setVlrPalabras($letras);
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_totalesdoc = $spoolLayout->getTotales($totalesDocObj);
                foreach ($arr_totalesdoc as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ExImpuestos
                //**********************************************************                
                /*
                  writeFileLine($spoolLayout->getExImpuestosHeader());

                  $exImpObj = new ImpuestosTraslados();
                  $iTax = 0;
                  foreach ($arr_taxes as $tax_name => $arr_tax_rate) {
                  foreach ($arr_tax_rate as $tax_rate => $tax_total) {
                  ++$iTax;
                  call_user_func(array($exImpObj, 'setTipoImp' . $iTax), $tax_name);
                  call_user_func(array($exImpObj, 'setTasaImp' . $iTax), $tax_rate);
                  call_user_func(array($exImpObj, 'setMontoImp' . $iTax), $tax_total);
                  }
                  }
                  //-- obtiene arreglo del layout que se escribira en el file
                  $arr_eximp = $spoolLayout->getExImpuestos($exImpObj);
                  //-- Itera los elementos del arreglo para escribir cada linea en el file
                  foreach ($arr_eximp as $namespace => $value) {
                  $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                  writeFileLine($str_output);
                  }
                 */

                //**********************************************************
                //-- ================ ExRetenciones
                //**********************************************************
                //writeFileLine($spoolLayout->getExRetencionesHeader());

                $exImpObj = new ImpuestosTraslados();
                $retImpObj = new ImpuestosRetenciones();


                if (array_key_exists('IVA', $arr_taxes)) {
                    //-- IVA 16%
                    if (array_key_exists('0.16', $arr_taxes['IVA'])) {
                        $exImpObj->setTipoImp1('IVA');
                        $exImpObj->setTasaImp1('16.00');
                        $exImpObj->setMontoImp1(number_format($arr_taxes['IVA']['0.16'], 2));
                    }
                    //-- IVA 11%
                    if (array_key_exists('0.11', $arr_taxes['IVA'])) {
                        $exImpObj->setTipoImp2('IVA');
                        $exImpObj->setTasaImp2('11.00');
                        $exImpObj->setMontoImp2(number_format($arr_taxes['IVA']['0.11'],2));
                    }
                    //-- IVA 0%
                    if (array_key_exists('0.00', $arr_taxes['IVA'])) {
                        $retImpObj->setTipoRet1('IVA');
                        $retImpObj->setTasaRet1('0.00');
                        $retImpObj->setMontoRet1(number_format($arr_taxes['IVA']['0.00'],2));
                    }
                }

                //-- Excento de IVA
                if (array_key_exists('EX', $arr_taxes)) {
                    $retImpObj->setTipoRet2('EX');
                    $retImpObj->setTasaRet2('0.00');
                    $retImpObj->setMontoRet2($arr_taxes['EX']['0.00']);
                }

                writeFileLine($spoolLayout->getExImpuestosHeader());
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_eximp = $spoolLayout->getExImpuestos($exImpObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_eximp as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                writeFileLine($spoolLayout->getExImpuestosHeader());
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_retimp = $spoolLayout->getExRetenciones($retImpObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_retimp as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                /*
                  $iTax = 0;
                  foreach ($arr_taxes as $tax_name => $arr_tax_rate) {
                  foreach ($arr_tax_rate as $tax_rate => $tax_total) {
                  ++$iTax;
                  call_user_func(array($retImpObj, 'setTipoImp' . $iTax), $tax_name);
                  call_user_func(array($retImpObj, 'setTasaImp' . $iTax), $tax_rate);
                  call_user_func(array($retImpObj, 'setMontoImp' . $iTax), $tax_total);
                  }
                  }
                 * 
                 */
                /*
                  //-- obtiene arreglo del layout que se escribira en el file
                  $arr_retimp = $spoolLayout->getExRetenciones($retImpObj);
                  //-- Itera los elementos del arreglo para escribir cada linea en el file
                  foreach ($arr_retimp as $namespace => $value) {
                  $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                  writeFileLine($str_output);
                  }
                 */
                //**********************************************************
                //-- ================ DscRcgGlobal
                //**********************************************************
                writeFileLine($spoolLayout->getDescuentosGlobalHeader());

                $descGlobObj = new DescuentosGlobales();

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_dscg = $spoolLayout->getDescuentosGlobal($descGlobObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_dscg as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ Addendas
                //**********************************************************
                writeFileLine($spoolLayout->getAddendasHeader());

                $addendasObj = new Addendas();
                switch($invoicesDTO->getID_customers()){
                    case 100089 : $ReceiverIDs=$ReceiverIDs; $SenderID=$invoicesDTO->getExpediterFiscalCode().':ZZ'; break; #Walmart
                    case 100090 : $ReceiverIDs=$ReceiverIDs; $SenderID=$invoicesDTO->getExpediterFiscalCode().':ZZ'; break; #Walmart(Sams)
                    default : $ReceiverIDs="";
                }             
                $addendasObj->setReceiverIDs($ReceiverIDs);
                $addendasObj->setSenderID($SenderID);
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_addendas = $spoolLayout->getAddendas($addendasObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_addendas as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ Personalizados
                //**********************************************************
                writeFileLine($spoolLayout->getPersonalizadosHeader());

                $persObj = new Personalizados();
                $persBanObj = new PersonalizadosBanca();
                $persLibObj = new PersonalizadosLibres();

                //-- REGIMEN FISCAL
                $persLibObj->setPPers01($invoicesDTO->getExpediterRegimen());
                

                $dbh = new DbHandler();
                $dbh->connect();
                $query = "SELECT 
                    Tax_ID 
                FROM 
                    cu_customers_addresses 
                WHERE 
                    cu_customers_addresses.ID_customers=".$invoicesDTO->getID_customers()." AND
                    cu_customers_addresses.PrimaryRecord='Yes'";
                $res = $dbh->selectSQLcommand($query);
                $row= mysql_fetch_array($res);
                $persLibObj->setPPers07($row[0]);

                ## Informacion de los Datos Bancarios del Cliente
                $persLibObj->setPPers02($invoicesDTO->getPaymentDigits());

                //--- Observaciones (2 campos Personalizados)
                $array_obs = getInvoicesNotes($invoicesDTO->getID_invoices());

                if($invoicesDTO->getID_customers()=='100037'){$Comment1='No. Cliente: '.$invoicesDTO->getVendorID().' ';}
                $persLibObj->setPPers03($Comment1.$array_obs[0]);
                #$persLibObj->setPPers04($array_obs[1]);

                //--- No. Pedido CI
                #$persLibObj->setPPers04(sanitizeStr($invoicesDTO->getID_orders_alias()));
                $persLibObj->setPPers04($OrderID);
                
                //--- Tipo de adenda (Coppel)
                switch($invoicesDTO->getID_customers()){
                    case '100037': $PPers05='ROPA'; break;    // Coppel Ropa
                    case '100141': $PPers05='MUEBLES'; break;    //Coppel Muebles
                    default: $PPers05='';
                }
                $persLibObj->setPPers05($PPers05);

                switch($invoicesDTO->getID_customers()){
                    /*
                    case '100037': $TotalLotes=ceil($TotQty / $PrepactCant); break;    // Coppel Ropa
                    case '100141': $TotalLotes=ceil($TotQty / $PrepactCant); break;    //Coppel Muebles
                    case '100125': $TotalLotes=ceil($TotQty / $PrepactCant); break;    //Soriana
                    case '100126': $TotalLotes=ceil($TotQty / $PrepactCant); break;    //CityClub
                    */
                    case '100037': $TotalLotes=$TotalLotes; break;    // Coppel Ropa
                    case '100141': $TotalLotes=$TotalLotes; break;    //Coppel Muebles
                    case '100125': $TotalLotes=$TotalLotes; break;    //Soriana
                    case '100126': $TotalLotes=$TotalLotes; break;    //CityClub
                    default: $TotalLotes='';
                }
                $persLibObj->setPPers06($TotalLotes);                

                //-- obtiene arreglo del layout que se escribira en el file
                $arr_personalizados = $spoolLayout->getPersonalizados($persObj, $persBanObj, $persLibObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_personalizados as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ContactoEmisor
                //**********************************************************                
                writeFileLine($spoolLayout->getContactoEmisorHeader());

                $cntEmObj = new ContactoEmisor();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_cntem = $spoolLayout->getContactoEmisor($cntEmObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_cntem as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ ContactoReceptor
                //**********************************************************                  
                writeFileLine($spoolLayout->getContactoReceptorHeader());

                $cntRecObj = new ContactoReceptor();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_cntre = $spoolLayout->getContactoReceptor($cntRecObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_cntre as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ Poliza
                //**********************************************************                
                writeFileLine($spoolLayout->getPolizaHeader());

                $polizaObj = new Poliza();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_poliza = $spoolLayout->getPoliza($polizaObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_poliza as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ Vehiculo
                //**********************************************************                
                writeFileLine($spoolLayout->getVehiculoHeader());

                $vehObj = new Vehiculo();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_veh = $spoolLayout->getVehiculo($vehObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_veh as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ Servicio
                //**********************************************************                
                writeFileLine($spoolLayout->getServicioHeader());

                $srvObj = new Servicio();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_srv = $spoolLayout->getServicio($srvObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_srv as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }


                //**********************************************************
                //-- ================ Local
                //**********************************************************                
                writeFileLine($spoolLayout->getLocalHeader());

                $localObj = new Local();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_local = $spoolLayout->getLocal($localObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_local as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ TotSubMonto
                //**********************************************************                
                writeFileLine($spoolLayout->getTotalSubMontoHeader());

                $totSubMntObj = new TotalSubMonto();
                //-- obtiene arreglo del layout que se escribira en el file
                $arr_submnt = $spoolLayout->getTotalSubMonto($totSubMntObj);
                //-- Itera los elementos del arreglo para escribir cada linea en el file
                foreach ($arr_submnt as $namespace => $value) {
                    $str_output = str_pad($namespace, $spoolLayout->getCoulmn_blank_spaces()) . $value;
                    writeFileLine($str_output);
                }

                //**********************************************************
                //-- ================ Referencia
                //**********************************************************                
                writeFileLine($spoolLayout->getReferenciaHeader());
                //-- consulta las cabeceras del detalle para su escritura
                $arr_header_ref = $spoolLayout->getReferenciaHeadersDefinition();
                //-- imprime las cabeceras 
                $str_output_header_ref = "";
                foreach ($arr_header_ref as $namespace => $size) {
                    $namespace = replaceHeaderNamespace($namespace);
                    $str_output_header_ref .= str_pad($namespace, $size);
                }
                //-- escribe las cabeceras en el file
                writeFileLine($str_output_header_ref);

                /*
                $line_ref_counter = 0;
                $referenciaObj = new Referencia();
                //--- se tienen que agregar las referencias, maximo 4
                $arr_referencias = array();
                $arr_referencias[] = $referenciaObj;
                foreach ($arr_referencias as $referenciaObj) {
                    if (++$line_ref_counter >= 4) {
                        break;
                    }
                    $arr_ref = $spoolLayout->getReferencia($referenciaObj);
                    //-- Itera los elementos del arreglo para escribir cada linea en el file
                    $str_output = "";
                    foreach ($arr_ref as $namespace => $value) {
                        $str_output .= str_pad($value, $arr_header_ref[$namespace]);
                    }
                    writeFileLine($str_output);
                }
                */
                //--- escribe las lineas de referencia                    

                    //-- obtiene arreglo del layout que se escribira en el file
                    // $arr_detalle = $spoolLayout->getDetalle($detObj);
                for($line_ref_counter=0; $line_ref_counter<4; $line_ref_counter++){
                    $idOrder = new DetalleConceptos();
                    $idOrder->setidOrder($invoicesLinesDTO->getID_orders());
                    $referenciaObj = new Referencia();
                     // No. Orden de Cliente
                     if ($line_ref_counter == 0 && $invoicesDTO->getID_orders_alias()!='') {
                        $referenciaObj->setTpoDocRef('ON');
                        $referenciaObj->setFolioRef(sanitizeStr(substr($invoicesDTO->getID_orders_alias(),0,20)));
                        if($invoicesDTO->getID_orders_alias_date()=='0000-00-00'){$ID_orders_alias_date='';}else{$ID_orders_alias_date=$invoicesDTO->getID_orders_alias_date();}
                        $referenciaObj->setFechaRef($ID_orders_alias_date);
                    }
                    //--- No. Contrarecibo
                    if ($line_ref_counter == 1 && $invoicesDTO->getExchangeReceipt()!='') {
                        $referenciaObj->setTpoDocRef('DQ');
                        $referenciaObj->setFolioRef(sanitizeStr(substr($invoicesDTO->getExchangeReceipt(),0,20)));
                        if($invoicesDTO->getExchangeReceiptDate()=='0000-00-00'){$ExchangeReceiptDate='';}else{$ExchangeReceiptDate=$invoicesDTO->getExchangeReceiptDate();}
                         $referenciaObj->setFechaRef($ExchangeReceiptDate);
                    }
                    $arr_ref = $spoolLayout->getReferencia($referenciaObj);
                    //-- Itera los elementos del arreglo para escribir cada linea en el file
                    $str_output = "";
                    foreach ($arr_ref as $namespace => $value) {
                        $str_output .= str_pad($value, $arr_header_ref[$namespace]);
                    }
                    writeFileLine($str_output);
                }

                //-- el numero de lineas maximo para las referencias debe ser de 4, si no existen llena los espacios
                for ($iRef = $line_ref_counter; $iRef < 4; $iRef++) {
                    writeFileLine("\r\n", FALSE);
                }


                writeFileLine($spoolLayout->getSpoolEnd(), FALSE);
                //-- 4 renglones en blanco para delimitar el archivo
                writeFileLine("\r\n\r\n\r\n\r\n", FALSE);
                //-- cierra el archivo para su escritura
                closeFile();
                

                //-- Actualiza el serie y el folio del Invoice
                updateSerialNum($invoicesDTO->getID_invoices(), $invoicesDTO->getDocSerial(), $invoicesDTO->getDocNum());
                //-- Actualiza el status del registro
                $exito = updateStatus($invoicesDTO->getID_invoices());
                //-- Agrega la Nota al Registro
                addNotes($invoicesDTO->getID_invoices());
                
                // Copia vía FTP a la carpeta destino
                $copy_source_path=$file_path.$filename;
                if(file_exists($copy_source_path)){
                 ### Descomentar para pasar a producción con facturas reales
                    if($cfdi_online==true){
                        UploadFile($copy_source_path,basename($copy_source_path));
                        Update_Invoice_logs($invoicesDTO->getID_invoices());
                    }
                }
            }
        }
    }
    return $exito;
}

/**
 * 
 * @param type $ID_invoices
 * @return type
 */
function updateStatus($ID_invoices) {
    $exito = FALSE;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setStatus("InProcess");

    $exito = $invoicesDAO->updateRecord($invoicesDTO);

    return $exito;
}

/**
 * 
 * @param type $ID_invoices
 * @param type $doc_serial
 * @param type $doc_num
 * @return type
 */
function updateSerialNum($ID_invoices, $doc_serial, $doc_num) {
    $exito = FALSE;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setDocSerial($doc_serial);
    $invoicesDTO->setDocNum($doc_num);

    $exito = $invoicesDAO->updateRecord($invoicesDTO);

    return $exito;
}

/**
 * Obtiene las observaciones de las facturas
 * @param int $ID_invoices
 * @return array
 */
function getInvoicesNotes($ID_invoices) {
    $array_notes = array(
        0 => "",
        1 => ""
    );

    $notes_line1 = "";
    $notes_line2 = "";

    $invoicesNotesDTO = new InvoicesNotesDTO();
    $invoicesNotesDAO = new InvoicesNotesDAO();

    $invoicesNotesDTO->setID_invoices($ID_invoices);
    $invoicesNotesDTO->setType("ToPrint");
    $vector_notes = $invoicesNotesDAO->selectRecords($invoicesNotesDTO);

    $tmp_str = "";
    foreach ($vector_notes as $invoicesNotesDTO) {
        $tmp_str .= sanitizeStr($invoicesNotesDTO->getNotes());
    }

    $tmp_arr = str_split($tmp_str, 100);
    $notes_line1 = $tmp_arr[0];
    if (array_key_exists(1, $tmp_arr)) {
        $notes_line2 = $tmp_arr[1];
    }

    $array_notes[0] = $notes_line1;
    $array_notes[1] = $notes_line2;

    return $array_notes;
}

/**
 * 
 * @return type
 */
function getInvoiceSerialNum($Tipo) {
    $doc_serial = "";
    $doc_num = 0;

    $dbh = new DbHandler();
    $dbh->connect();

    if($Tipo=='ingreso'){
        //-- Obtiene el numero de serie para la factura
        $dbh->selectSQLcommand("SELECT VName, VValue FROM sl_vars WHERE VName = 'invoices_doc_serial'");
        if ($result = $dbh->fetchAssocNextRow()) {
            $doc_serial = $result['VValue'];
        }
        //--- Obtiene el folio para la factura
        $dbh->selectSQLcommand("SELECT VName, VValue FROM sl_vars WHERE VName = 'invoices_doc_num'");
        if ($result = $dbh->fetchAssocNextRow()) {
            $doc_num = $result['VValue'];
        }
        //--- actualiza el dato del folio para generar el consecutivo
        $next_num = intval($doc_num) + 1;
        $dbh->executeSQLcommand("UPDATE sl_vars SET VValue='$next_num' WHERE VName = 'invoices_doc_num'");

    }

    elseif($Tipo=='egreso'){
        //-- Obtiene el numero de serie para la factura
        $dbh->selectSQLcommand("SELECT VName, VValue FROM sl_vars WHERE VName = 'creditnote_doc_serial'");
        if ($result = $dbh->fetchAssocNextRow()) {
            $doc_serial = $result['VValue'];
        }

        //--- Obtiene el folio para la factura
        $dbh->selectSQLcommand("SELECT VName, VValue FROM sl_vars WHERE VName = 'creditnote_doc_num'");
        if ($result = $dbh->fetchAssocNextRow()) {
            $doc_num = $result['VValue'];
        }

        //--- actualiza el dato del folio para generar el consecutivo
        $next_num = intval($doc_num) + 1;
        $dbh->executeSQLcommand("UPDATE sl_vars SET VValue='$next_num' WHERE VName = 'creditnote_doc_num'");
    }

    $dbh->disconnect();

    $arr_doc_serial = array(
        'doc_serial' => $doc_serial,
        'doc_num' => $doc_num,
    );

    return $arr_doc_serial;
}


/**
 * Agrega notas al invoice
 * @global type $id_admin_users
 * @param type $id_invoces
 * @param type $type
 * @return BOOLEAN
 */
function addNotes($id_invoces, $type = 'success'){
    global $id_admin_users;
    
    $exito = FALSE;
    $notes ="";
    if($type == 'success'){
        $notes = "Se genero el archivo para la certificacion de la factura.";
    }else{
        $notes = "Ocurrio un error al generar el archivo para la certificacion de la factura.";
    }
    
    $invNotesDAO = new InvoicesNotesDAO();
    $invNotesDTO = new InvoicesNotesDTO();
    
    $invNotesDTO->setID_invoices($id_invoces);
    $invNotesDTO->setNotes($notes);
    $invNotesDTO->setType('Note');
    $invNotesDTO->setID_admin_users($id_admin_users);
    
    $exito = $invNotesDAO->insertRecord($invNotesDTO);
    
    return $exito;
}

function createFile($file_name, $path) {
    global $file_handler;
    $file_handler = fopen($path . $file_name, 'w');
    chmod($path . $file_name, 0777);
}

function writeFileLine($str, $crlf = TRUE) {
    global $file_handler;
    if ($crlf) {
        $str .="\r\n";
    }
    fwrite($file_handler, $str);
}

function closeFile() {
    global $file_handler;
    fclose($file_handler);
}

function replaceHeaderNamespace($namespace) {
    $namespace = str_replace("Tipo1", "Tipo", $namespace);
    $namespace = str_replace("TasaIm1", "TasaIm", $namespace);
    $namespace = str_replace("Tipo2", "Tipo", $namespace);
    $namespace = str_replace("TasaIm2", "TasaIm", $namespace);
    $namespace = str_replace("TipoRe", "Tipo", $namespace);

    return $namespace;
}

function sanitizeStr($str, $trim_str = TRUE) {
    //$str = utf8_decode($str);
    $str = str_replace(chr(193), 'A', $str);
    $str = str_replace(chr(225), 'a', $str);
    $str = str_replace(chr(201), 'E', $str);
    $str = str_replace(chr(233), 'e', $str);
    $str = str_replace(chr(205), 'I', $str);
    $str = str_replace(chr(237), 'i', $str);
    $str = str_replace(chr(211), 'O', $str);
    $str = str_replace(chr(243), 'o', $str);
    $str = str_replace(chr(218), 'U', $str);
    $str = str_replace(chr(250), 'u', $str);

    $str = str_replace(chr(192), 'A', $str);
    $str = str_replace(chr(224), 'a', $str);
    $str = str_replace(chr(200), 'E', $str);
    $str = str_replace(chr(232), 'e', $str);
    $str = str_replace(chr(204), 'I', $str);
    $str = str_replace(chr(236), 'i', $str);
    $str = str_replace(chr(210), 'O', $str);
    $str = str_replace(chr(242), 'o', $str);
    $str = str_replace(chr(217), 'U', $str);
    $str = str_replace(chr(249), 'u', $str);

    $str = str_replace(chr(220), 'U', $str);
    $str = str_replace(chr(252), 'u', $str);

    $str = str_replace(chr(209), 'N', $str);
    $str = str_replace(chr(241), 'n', $str);

    $str = str_replace(array("\n", "\t", "\r"), ' ', $str);

    if ($trim_str) {
        $str = trim($str);
    }
    return $str;
}

function Update_ID_Customer($v=true){
    global $User;
    global $Password;
    global $Server;
    global $DataBase;  
    $link=mysql_connect($Server, $User, $Password) or die(mysql_error());
    mysql_select_db($DataBase, $link);
    $sql="update cu_invoices a
            left join cu_invoices_lines b using(ID_invoices)
            left join sl_orders c on b.ID_orders=c.ID_orders
            set a.ID_customers = c.ID_customers
            where b.ID_orders=c.ID_orders and a.ID_customers<=0";
    $con=mysql_query($sql, $link) or die(mysql_error());
}

function Update_Invoice_logs($ID_Invoices=''){
    global $User;
    global $Password;
    global $Server;
    global $DataBase; 
    #date_default_timezone_set("America/Mexico_City");
    #$Timestamp=date("Y-m-d G:i:s"); 
    $link=mysql_connect($Server, $User, $Password) or die(mysql_error());
    mysql_select_db($DataBase, $link);
    $sql="insert into cu_invoices_logs 
            (Action, ID_invoices, doc_serial, doc_num, doc_date, ID_orders, ID_creditmemos, Timestamp, ID_admin_users)
            select 'Sent', a.ID_invoices, a.doc_serial, a.doc_num, a.doc_date, b.ID_orders, b.ID_creditmemos, CURRENT_TIMESTAMP(), a.ID_admin_users
            from cu_invoices a
            left join cu_invoices_lines b using(ID_invoices) 
            where a.ID_invoices=$ID_Invoices
            group by a.ID_invoices";
    $con=mysql_query($sql, $link) or die(mysql_error());
}

?>