<?php

session_start();

require_once '../../../trsBase.php';
require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dao.catalog.InvoicesDAO.php';
require_once '../../../common/php/class/dto.catalog.InvoicesDTO.php';
require_once '../../../common/php/class/dao.catalog.InvoicesLinesDAO.php';
require_once '../../../common/php/class/dto.catalog.InvoicesLinesDTO.php';
require_once '../../../common/php/class/dto.catalog.InvoicesNotesDTO.php';
require_once '../../../common/php/class/dao.catalog.InvoicesNotesDAO.php';
require_once '../../../common/php/class/dto.common.SerialDTO.php';
require_once '../../../common/php/class/dao.common.SerialDAO.php';

require_once '../../../common/php/class/dao.catalog.AdminLogsDAO.php';
require_once '../../../common/php/functions/auth_functions.php';
require_once '../../../common/php/functions/http_functions.php';

$_POST = decodeUTF8($_POST);

$exito = 0;
$id_admin_users = isset($usr['id_admin_users']) ? $usr['id_admin_users'] : 0;

$invoicesDTO = new InvoicesDTO();
$invoicesDAO = new InvoicesDAO();

$id_invoices = trim($_POST['hdIdInvoice']);
$Invoice_Type = trim($_POST['InvoiceType']);

$action = $_POST['action'];
//-- ********************* paso de parametros *****************

if ($action == 'save_invoice') {
    //-- datos generales de la factura
    $orderAlias = trim($_POST['txtOrderAlias']);
    $orderAliasDate = trim($_POST['txtOrderAliasDate']);
    $exchangeReceipt = trim($_POST['txtExchangeReceipt']);
    $exchangeReceiptDate = trim($_POST['txtExchangeReceiptDate']);
    $creditDays = trim($_POST['txtCreditDays']);
    $conditions = trim($_POST['txtConditions']);
    $batch = trim($_POST['txtBatch']);
    $paymentDigits = trim($_POST['txtPaymentDigits']);

    $invoicesDTO->setID_orders_alias($orderAlias);
    $invoicesDTO->setID_orders_alias_date($orderAliasDate);
    $invoicesDTO->setExchangeReceipt($exchangeReceipt);
    $invoicesDTO->setExchangeReceiptDate($exchangeReceiptDate);
    $invoicesDTO->setCreditDays($creditDays);
    $invoicesDTO->setConditions($conditions);
    $invoicesDTO->setBatchNum($batch);    
    $invoicesDTO->setPaymentDigits($paymentDigits);
    
    //-- datos fiscales del emisor
    $expediterFCode = trim($_POST['txtExpediterFCode']);
    $expediterFName = trim($_POST['txtExpediterFName']);
    $expediterFRegimen = trim($_POST['txtExpediterFRegimen']);

    $invoicesDTO->setID_invoices($id_invoices);
    $invoicesDTO->setExpediterFiscalCode($expediterFCode);
    $invoicesDTO->setExpediterName($expediterFName);
    $invoicesDTO->setExpediterRegimen($expediterFRegimen);

//-- domicilio fiscal
    $expediterFStreet = trim($_POST['txtExpediterFAddressStreet']);
    $expediterFNum = trim($_POST['txtExpediterFAddressNum']);
    $expediterFNum2 = trim($_POST['txtExpediterFAddressNum2']);
    $expediterFUrbanization = trim($_POST['txtExpediterFAddressUrbanization']);
    $expediterFDistrict = trim($_POST['txtExpediterFAddressDistrict']);
    $expediterFState = trim($_POST['txtExpediterFAddressState']);
    $expediterFCity = trim($_POST['txtExpediterFAddressCity']);
    $expediterFCountry = trim($_POST['txtExpediterFAddressCountry']);
    $expediterFZip = trim($_POST['txtExpediterFAddressZipcode']);

    $invoicesDTO->setExpediterFAddressStreet($expediterFStreet);
    $invoicesDTO->setExpediterFAddressNum($expediterFNum);
    $invoicesDTO->setExpediterFAddressNum2($expediterFNum2);
    $invoicesDTO->setExpediterFAddressUrbanization($expediterFUrbanization);
    $invoicesDTO->setExpediterFAddressDistrict($expediterFDistrict);
    $invoicesDTO->setExpediterFAddressState($expediterFState);
    $invoicesDTO->setExpediterFAddressCity($expediterFCity);
    $invoicesDTO->setExpediterFAddressCountry($expediterFCountry);
    $invoicesDTO->setExpediterFAddressZipcode($expediterFZip);


//-- lugar de expedicion
    $expediterStreet = trim($_POST['txtExpediterAddressStreet']);
    $expediterNum = trim($_POST['txtExpediterAddressNum']);
    $expediterNum2 = trim($_POST['txtExpediterAddressNum2']);
    $expediterUrbanization = trim($_POST['txtExpediterAddressUrbanization']);
    $expediterDistrict = trim($_POST['txtExpediterAddressDistrict']);
    $expediterState = trim($_POST['txtExpediterAddressState']);
    $expediterCity = trim($_POST['txtExpediterAddressCity']);
    $expediterCountry = trim($_POST['txtExpediterAddressCountry']);
    $expediterZip = trim($_POST['txtExpediterAddressZipcode']);

    $invoicesDTO->setExpediterAddressStreet($expediterStreet);
    $invoicesDTO->setExpediterAddressNum($expediterNum);
    $invoicesDTO->setExpediterAddressNum2($expediterNum2);
    $invoicesDTO->setExpediterAddressUrbanization($expediterUrbanization);
    $invoicesDTO->setExpediterAddressDistrict($expediterDistrict);
    $invoicesDTO->setExpediterAddressState($expediterState);
    $invoicesDTO->setExpediterAddressCity($expediterCity);
    $invoicesDTO->setExpediterAddressCountry($expediterCountry);
    $invoicesDTO->setExpediterAddressZipcode($expediterZip);


//-- Datos del Cliente
    $customerFiscalCode = trim($_POST['txtCustomerFCode']);
    $customerName = trim($_POST['txtCustomerFName']);
    $customerContact = trim($_POST['txtCustomerShpAddressContact']);

    $invoicesDTO->setCustomerFiscalCode($customerFiscalCode);
    $invoicesDTO->setCustomerName($customerName);
    $invoicesDTO->setCustomerShpaddressContact($customerContact);

//-- Direccion del cliente
    $customerStreet = trim($_POST['txtCustomerAddressStreet']);
    $customerNum = trim($_POST['txtCustomerAddressNum']);
    $customerNum2 = trim($_POST['txtCustomerAddressNum2']);
    $customerUrbanization = trim($_POST['txtCustomerAddressUrbanization']);
    $customerDistrict = trim($_POST['txtCustomerAddressDistrict']);
    $customerState = trim($_POST['txtCustomerAddressState']);
    $customerCity = trim($_POST['txtCustomerAddressCity']);
    $customerCountry = trim($_POST['txtCustomerAddressCountry']);
    $customerZipcode = trim($_POST['txtCustomerAddressZipcode']);

    $invoicesDTO->setCustomerFAddressStreet($customerStreet);
    $invoicesDTO->setCustomerFAddressNum($customerNum);
    $invoicesDTO->setCustomerFAddressNum2($customerNum2);
    $invoicesDTO->setCustomerFAddressUrbanization($customerUrbanization);
    $invoicesDTO->setCustomerFAddressDistrict($customerDistrict);
    $invoicesDTO->setCustomerFAddressState($customerState);
    $invoicesDTO->setCustomerFAddressCity($customerCity);
    $invoicesDTO->setCustomerFAddressCountry($customerCountry);
    $invoicesDTO->setCustomerFAddressZipcode($customerZipcode);

    //-- Lugar de Entrega
    $shpStreet = trim($_POST['txtCustomerShpAddressStreet']);
    $shpNum = trim($_POST['txtCustomerShpAddressNum']);
    $shpNum2 = trim($_POST['txtCustomerShpAddressNum2']);
    $shpUrbanization = trim($_POST['txtCustomerShpAddressUrbanization']);
    $shpDistrict = trim($_POST['txtCustomerShpAddressDistrict']);
    $shpState = trim($_POST['txtCustomerShpAddressState']);
    $shpCity = trim($_POST['txtCustomerShpAddressCity']);
    $shpCountry = trim($_POST['txtCustomerShpAddressCountry']);
    $shpZipcode = trim($_POST['txtCustomerShpAddressZipcode']);
    
    $invoicesDTO->setCustomerShpAddressStreet($shpStreet);
    $invoicesDTO->setCustomerShpAddressNum($shpNum);
    $invoicesDTO->setCustomerShpAddressNum2($shpNum2);
    $invoicesDTO->setCustomerShpAddressUrbanization($shpUrbanization);
    $invoicesDTO->setCustomerShpAddressDistrict($shpDistrict);
    $invoicesDTO->setCustomerShpAddressState($shpState);
    $invoicesDTO->setCustomerShpAddressCity($shpCity);
    $invoicesDTO->setCustomerShpAddressCountry($shpCountry);
    $invoicesDTO->setCustomerShpAddressZipcode($shpZipcode);
    
    $invoicesDTO->setID_admin_users($id_admin_users);

    //--Validación para campos requeridos para generar el XML
    if($Invoice_Type=='egreso'){
        #No. Pedido de Cliente y Fecha Pedido de Cliente
        if($orderAlias=='' && ($orderAliasDate!='' && $orderAliasDate!='0000-00-00')){
            $orderAlias = 'CMx';  
            $invoicesDTO->setID_orders_alias($orderAlias);
        }elseif($orderAlias!='' && ($orderAliasDate=='' || $orderAliasDate=='0000-00-00')){
            $orderAliasDate = date('Y-m-d');    ;
            $invoicesDTO->setID_orders_alias_date($orderAliasDate);
        }elseif($orderAlias=='' && ($orderAliasDate=='' || $orderAliasDate=='0000-00-00')){
            $orderAlias = 'CMx';
            $orderAliasDate = date('Y-m-d');    
            $invoicesDTO->setID_orders_alias($orderAlias);
            $invoicesDTO->setID_orders_alias_date($orderAliasDate);
        }
        #No. Contrarecibo y Fecha de Contrarecibo
        if($exchangeReceipt==''){
            $exchangeReceipt = 'CMx';
            $exchangeReceiptDate = date('Y-m-d');
            $invoicesDTO->setExchangeReceipt($exchangeReceipt);
            $invoicesDTO->setExchangeReceiptDate($exchangeReceiptDate);
        }
        #Días de crédito
        if($creditDays='' || $creditDays==NULL){
            $creditDays="0";
            $invoicesDTO->setCreditDays($creditDays);
        }
        #Condiciones de pago
        if($conditions=='' || $conditions==NUL){
            $conditions="CONTADO";            
            $invoicesDTO->setConditions($conditions);
        }
        #Clave de Contacto o Depto.
        if($customerContact==''){
            $customerContact = 'X';
            $invoicesDTO->setCustomerShpaddressContact($customerContact);
        }        
    }
    //-- actualiza el registro en la base de datos
    if ($invoicesDAO->updateRecord($invoicesDTO)) {
        auth_logging('opr_invoices_updated', $id_invoices, $id_admin_users, 'sl_invoices', 'modcfdi');

        $exito = 1;
    }
    foreach ($_POST['MeasuringUnit'] as $unidad) {
        list($id_invoices_lines, $id_unidad) = explode('-', $unidad, 2);
        $query = "UPDATE cu_invoices_lines SET measuring_unit = '$id_unidad' WHERE ID_invoices_lines = $id_invoices_lines";
        $dbh = new DbHandler();
        $dbh->connect();
        $dbh->executeSQLcommand($query);

    }

    //-- agrega los registro de las notas
    insertNotes($id_invoices);
        
} elseif ($action == 'save_notes') {
    $exito = insertNotes($id_invoices);
    
} elseif ($action == 'update_status') {
    $status = $_POST['status'];
    $exito = updateStatus($id_invoices, $status);
    
} elseif ($action == "duplicate_invoice") {
    $arr_duplicate_exito = duplicateInvoice($id_invoices);
    $exito = json_encode($arr_duplicate_exito);

} elseif ($action == "credit_note") {
    $arr_duplicate_exito = creditNote($id_invoices);
    $exito = json_encode($arr_duplicate_exito);
      
} elseif ($action == "save_customs") {
    
    $idInvoiceLines = trim($_POST['idInvoiceLines']);
    if(!empty($idInvoiceLines)){

        $customsDAO = new InvoicesLinesDAO();
        $customsDTO = new InvoicesLinesDTO();

        $customsDTO->setID_invoices_lines($idInvoiceLines);
        #$customsDTO->setCustomsGLN(trim($_POST['glnCustoms']));
        $customsDTO->setCustomsName(trim($_POST['nameCustoms']));
        $customsDTO->setCustomsNum(trim($_POST['numCustoms']));
        $customsDTO->setCustomsDate(trim($_POST['dateCustoms']));
        
        if ($customsDAO->updateRecord($customsDTO)) {
            #auth_logging('opr_invoices_updated', $id_invoices, $id_admin_users, 'sl_invoices', 'modcfdi');
            $exito = 1;
        }        
    } 

} elseif ($action == "save_series") {    
    $ISerial = trim($_POST['ISeries']);
    $INumber = trim($_POST['INumbers']);
    $CSerial = trim($_POST['CSeries']);
    $CNumber = trim($_POST['CNumbers']);
    $exito = updateSerials($ISerial,$INumber,$CSerial,$CNumber);

} elseif ($action == "onedition_invoice") {
    $arr_duplicate_exito = oneditionInvoice($id_invoices);    
    $exito = json_encode($arr_duplicate_exito);
}

echo $exito;

?>
<?php

function updateSerials($ISerial,$INumber,$CSerial,$CNumber){
    $exito = 0;
    if($ISerial!=''){
        $serialDAO = new InvoicesSerialDAO();
        $serialDTO = new InvoicesSerialDTO();
        $serialDTO->setVname('IS');
        $serialDTO->setVvalue($ISerial);
        $serialDAO->updateRecord($serialDTO);
        $exito = 1;
    }
    if($INumber!=''){
        $serialDAO = new InvoicesSerialDAO();
        $serialDTO = new InvoicesSerialDTO();
        $serialDTO->setVname('IN');
        $serialDTO->setVvalue($INumber);
        $serialDAO->updateRecord($serialDTO);
        $exito = 1;
    }
    if($CSerial!=''){
        $serialDAO = new InvoicesSerialDAO();
        $serialDTO = new InvoicesSerialDTO();
        $serialDTO->setVname('CS');
        $serialDTO->setVvalue($CSerial);
        $serialDAO->updateRecord($serialDTO);
        $exito = 1;
    }
    if($CNumber!=''){
        $serialDAO = new InvoicesSerialDAO();
        $serialDTO = new InvoicesSerialDTO();
        $serialDTO->setVname('CN');
        $serialDTO->setVvalue($CNumber);
        $serialDAO->updateRecord($serialDTO);
        $exito = 1;
    }
    return $exito;
}


function insertNotes($ID_invoices) {
    global $id_admin_users;
    global $id_invoices;

    $exito = 0;

    $array_notes = $_SESSION['ARRAY_NOTES'];

    if (!empty($array_notes)) {
        $invoicesNotesDAO = new InvoicesNotesDAO();

        foreach ($array_notes as $a_note) {

            $invoicesNotesDTO = new InvoicesNotesDTO();
            $invoicesNotesDTO->setID_invoices($ID_invoices);
            $invoicesNotesDTO->setType($a_note['type']);
            $invoicesNotesDTO->setNotes($a_note['notes']);
            $invoicesNotesDTO->setID_admin_users($id_admin_users);

            if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
                auth_logging('opr_invoices_notes_added', $id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
                $exito = 1;
            }
        }
    }
    return $exito;
}

function updateStatus($ID_invoices, $status) {
    global $id_admin_users;
    $exito = 0;

    // Verifica si se encuentra en algun status que ya no se puede modificar
    if (!verifyNonModifyStatus($ID_invoices)) {

        $invoicesDTO = new InvoicesDTO();
        $invoicesDAO = new InvoicesDAO();

        $invoicesDTO->setID_invoices($ID_invoices);
        $invoicesDTO->setStatus($status);
        $invoicesDTO->setDocDate(date("Y-m-d H:i:s"));
        $invoicesDTO->setID_admin_users($id_admin_users);
        if ($invoicesDAO->updateRecord($invoicesDTO)) {
            auth_logging('opr_invoices_updated', $ID_invoices, $id_admin_users, 'sl_invoices', 'modcfdi');
            $exito = 1;
        }
    } else {
        $exito = -1;
    }

    return $exito;
}

function verifyNonModifyStatus($ID_invoices) {
    $isNonModify = FALSE;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);
    $vector_invoices = $invoicesDAO->selectRecords($invoicesDTO);
    if (!empty($vector_invoices)) {
        $invoicesDTO = $vector_invoices[0];

        if ($invoicesDTO->getStatus() == 'InProcess' || $invoicesDTO->getStatus() == 'Cancelled') {
            $isNonModify = TRUE;
        }
    }

    return $isNonModify;
}

function duplicateInvoice($ID_invoices) {
    global $id_admin_users;

    $exito = 0;
    $last_id_invoices = 0;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);

    if ($invoicesDAO->duplicateRecord($invoicesDTO)) {
        $last_id_invoices = $invoicesDAO->getLastInsertId();

        $invoicesDTO = new InvoicesDTO();
        $invoicesDTO->setID_invoices($last_id_invoices);
        $invoicesDTO->setRelatedID_invoice($ID_invoices);
        $invoicesDTO->setDocSerial("");
        $invoicesDTO->setDocNum("0");
        $invoicesDTO->setDocDate(date("Y-m-d H:i:s"));
        $invoicesDTO->setDate(date("Y-m-d"));
        $invoicesDTO->setTime(date("H:i:s"));
        $invoicesDTO->setStatus("New");
        $invoicesDTO->setID_admin_users($id_admin_users);

        if ($invoicesDAO->updateRecord($invoicesDTO)) {
            $invoicesLinesDAO = new InvoicesLinesDAO();
            $invoicesLinesDTO = new InvoicesLinesDTO();

            //-- id invoice del cual se va a duplicar los datos
            $invoicesLinesDTO->setID_invoices($ID_invoices);
            //-- Campo auxiliar que contiene el ID del nuevo invoice
            $invoicesLinesDTO->setExtraID_field($last_id_invoices);
            $invoicesLinesDTO->setID_admin_users($id_admin_users);

            if ($invoicesLinesDAO->duplicateRecord($invoicesLinesDTO)) {
                $exito = 1;
            }
        }

        $notes="Se ha duplicado la informaci&oacuten de este documento con el ID: ".$last_id_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($ID_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }

        $notes="Esta informaci&oacuten ha sido duplicada de la factura ID: ".$ID_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($last_id_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $last_id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }
    }

    $array_response = array(
        'exito' => $exito,
        'id_new_invoices' => $last_id_invoices
    );
    return $array_response;
}

function creditNote($ID_invoices) {
    global $id_admin_users;

    $exito = 0;
    $last_id_invoices = 0;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);

    if ($invoicesDAO->duplicateRecord($invoicesDTO)) {
        $last_id_invoices = $invoicesDAO->getLastInsertId();

        $invoicesDTO = new InvoicesDTO();
        $invoicesDTO->setID_invoices($last_id_invoices);
        $invoicesDTO->setRelatedID_invoice($ID_invoices);
        $invoicesDTO->setStatus("New");
        $invoicesDTO->setInvoiceType("egreso");
        $invoicesDTO->setDocSerial("");
        $invoicesDTO->setDocNum("");
        $invoicesDTO->setDocDate(date("Y-m-d H:i:s"));
        $invoicesDTO->setDate(date("Y-m-d"));
        $invoicesDTO->setTime(date("H:i:s"));
        $invoicesDTO->setID_admin_users($id_admin_users);

        if ($invoicesDAO->updateRecord($invoicesDTO)) {
            $invoicesLinesDAO = new InvoicesLinesDAO();
            $invoicesLinesDTO = new InvoicesLinesDTO();

            //-- id invoice del cual se va a duplicar los datos
            $invoicesLinesDTO->setID_invoices($ID_invoices);
            //-- Campo auxiliar que contiene el ID del nuevo invoice
            $invoicesLinesDTO->setExtraID_field($last_id_invoices);
            $invoicesLinesDTO->setID_admin_users($id_admin_users);

            if ($invoicesLinesDAO->duplicateRecord($invoicesLinesDTO)) {
                $exito = 1;
            }
        }
        #updateStatus($ID_invoices, 'Cancelled');

        #$notes="Se ha cancelado esta factura para generar la Nota de Credito: ".$last_id_invoices;
        $notes="Se ha generado para esta factura la Nota de Credito: ".$last_id_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($ID_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }

    #GENERA CONTABILIDAD DE REFACTURACION
        $invoicesDAO->movementsReInvocing($ID_invoices);


        $notes="Esta Nota de Credito esta asociada con la factura ID: ".$ID_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($last_id_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $last_id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }
    }

    $array_response = array(
        'exito' => $exito,
        'id_new_invoices' => $last_id_invoices
    );
    return $array_response;
}

function oneditionInvoice($ID_invoices) {
    global $id_admin_users;

    $exito = 0;
    $last_id_invoices = 0;

    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();

    $invoicesDTO->setID_invoices($ID_invoices);

    if ($invoicesDAO->duplicateRecord($invoicesDTO)) {
        $last_id_invoices = $invoicesDAO->getLastInsertId();

        $invoicesDTO = new InvoicesDTO();
        $invoicesDTO->setID_invoices($last_id_invoices);
        $invoicesDTO->setRelatedID_invoice($ID_invoices);
        $invoicesDTO->setDocSerial("");
        $invoicesDTO->setDocNum("0");
        $invoicesDTO->setDocDate(date("Y-m-d H:i:s"));
        $invoicesDTO->setDate(date("Y-m-d"));
        $invoicesDTO->setTime(date("H:i:s"));
        $invoicesDTO->setStatus("OnEdition");
        $invoicesDTO->setID_admin_users($id_admin_users);

        if ($invoicesDAO->updateRecord($invoicesDTO)) {
            $invoicesLinesDAO = new InvoicesLinesDAO();
            $invoicesLinesDTO = new InvoicesLinesDTO();

            //-- id invoice del cual se va a duplicar los datos
            $invoicesLinesDTO->setID_invoices($ID_invoices);
            //-- Campo auxiliar que contiene el ID del nuevo invoice
            $invoicesLinesDTO->setExtraID_field($last_id_invoices);
            $invoicesLinesDTO->setID_admin_users($id_admin_users);

            if ($invoicesLinesDAO->duplicateRecord($invoicesLinesDTO)) {
                $exito = 1;
            }
        }

        $notes="Se ha duplicado la informaci&oacuten de este documento con el ID: ".$last_id_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($ID_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }

        $notes="Esta informaci&oacuten ha sido duplicada de la factura ID: ".$ID_invoices;
        $invoicesNotesDAO = new InvoicesNotesDAO();
        $invoicesNotesDTO = new InvoicesNotesDTO();
        $invoicesNotesDTO->setID_invoices($last_id_invoices);
        $invoicesNotesDTO->setType('Note');
        $invoicesNotesDTO->setNotes($notes);
        $invoicesNotesDTO->setID_admin_users($id_admin_users);
        if ($invoicesNotesDAO->insertRecord($invoicesNotesDTO)) {
            auth_logging('opr_invoices_notes_added', $last_id_invoices, $id_admin_users, 'sl_invoices_notes', 'modcfdi');
        }
    }

    $array_response = array(
        'exito' => $exito,
        'id_new_invoices' => $last_id_invoices
    );
    return $array_response;
}

?>