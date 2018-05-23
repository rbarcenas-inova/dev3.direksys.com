<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();

include_once '../../../trsBase.php';
include_once '../../../session.php';

require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dao.catalog.BillsDAO.php';
require_once '../../../common/php/class/dao.catalog.BillsNotesDAO.php';
require_once '../../../common/php/class/dao.catalog.BillsPaymentsBillsDAO.php';
require_once '../../../common/php/class/dao.catalog.BillsPaymentsDAO.php';
require_once '../../../common/php/class/dao.catalog.BillsPaymentsNotesDAO.php';
require_once '../../../common/php/class/dao.catalog.BillsPosDAO.php';

$exito = 0;
$msg = "";

if (isset($_SESSION['ARRAY_PO_PAYMENTS'])) {
    $array_po_payments = $_SESSION['ARRAY_PO_PAYMENTS'];
}

$id_purchaseorders = isset($_POST['txtPOID']) ? $_POST['txtPOID'] : $in['txtPOID'];
$id_vendors = isset($_POST['hdVendorID']) ? $_POST['hdVendorID'] : $in['hdVendorID'];

$id_admin_users = isset($usr['id_admin_users']) ? $usr['id_admin_users'] : 0;

$id_bills = -1;
$id_bills_payments = -1;
$bill_type = 'Deposit';
$bill_status = 'Paid';

$array_bill_params = array(
    "id_purchaseorders" => $id_purchaseorders,
    "id_vendors" => $id_vendors,
    "bill_type" => $bill_type,
    "id_bills" => $id_bills,
    "bill_status" => $bill_status,
    'id_bills_payments' => $id_bills_payments
);



foreach ($array_po_payments as $arr_payments) {
    //-- procesa la informacion del bill
    $id_bills = createBill($array_bill_params, $arr_payments);
    if ($id_bills > 0) {
        $array_bill_params['id_bills'] = $id_bills;

        //-- procesa la informacion del bill pos
        $id_bill_pos = createBillPOS($array_bill_params, $arr_payments);
        if ($id_bill_pos > 0) {
            $id_bills_payments = createBillPayment($array_bill_params, $arr_payments);
            if ($id_bills_payments > 0) {
                $array_bill_params['id_bills_payments'] = $id_bills_payments;

                $id_billpayments_bill = createBillPaymentBill($array_bill_params, $arr_payments);

                if ($id_billpayments_bill > 0) {
                    $exito = 1;
                } else {
                    $msg .= "Ocurrio un error al crear el Bill Payment Bill<br>";
                    $exito = 0;
                    break;
                }
            } else {
                $msg .= "Ocurrio un error al crear el Bill Payment<br>";
                $exito = 0;
                break;
            }
        } else {
            $msg .= "Ocurrio un error al realizar la union del Bill con el PO<br>";
            $exito = 0;
            break;
        }
    } else {
        $msg .= "Ocurrio un error al realizar el registro del Bill<br>";
        $exito = 0;
        break;
    }
} // Foreach

$array_return = array(
    "exito" => $exito,
    "msg" => '' 
);

echo json_encode($array_return);
?>
<?php

/* * ******************************************************************************* */
/* * ************************* FUNCIONES DE OPERACIONES  *************************** */
/* * ******************************************************************************* */

function getPaymentTotal($array_po_payments) {
    $grand_total = 0;

    foreach ($array_po_payments as $arr_payments) {
        $grand_total += $arr_payments['payment_amount'];
    }
    return $grand_total;
}

function createBill($arr_bills_params, $arr_payment) {
    global $id_admin_users;
    
    $id_bills = -1;
    $billDTO = new BillsDTO();
    $billsDAO = new BillsDAO();

    $billDTO->setID_vendors($arr_bills_params['id_vendors']);
    $billDTO->setType($arr_bills_params['bill_type']);
    $billDTO->setCurrency($arr_payment['payment_currency']);
    $billDTO->setAmount($arr_payment['payment_amount']);
    $billDTO->setBillDate($arr_payment['payment_date']);
    $billDTO->setDueDate($arr_payment['payment_date']);
    $billDTO->setStatus($arr_bills_params['bill_status']);
    $billDTO->setID_admin_users($id_admin_users);

    if ($billsDAO->insertRecord($billDTO)) {
        $id_bills = $billsDAO->getLastInsertId();

        $notes = "Anticipo del Purchase Order: " . $arr_bills_params['id_purchaseorders'] . "\n" . $arr_payment['payment_notes'];
        //--- agrega las notas del bill
        $billNotesDTO = new BillsNotesDTO();
        $billsNotesDAO = new BillsNotesDAO();

        $billNotesDTO->setID_bills($id_bills);
        $billNotesDTO->setNotes($notes);
        $billNotesDTO->setID_admin_users($id_admin_users);
        $billsNotesDAO->insertRecord($billNotesDTO);
    }

    return $id_bills;
}

function createBillPOS($arr_bills_params, $arr_payment) {
    global $id_admin_users;
    $id_bills_pos = -1;

    $billPosDTO = new BillsPosDTO();
    $billsPosDAO = new BillsPosDAO();

    $billPosDTO->setID_bills($arr_bills_params['id_bills']);
    $billPosDTO->setID_purchaseorders($arr_bills_params['id_purchaseorders']);
    $billPosDTO->setAmount($arr_payment['payment_amount']);
    $billPosDTO->setID_admin_users($id_admin_users);

    if ($billsPosDAO->insertRecord($billPosDTO)) {
        $id_bills_pos = $billsPosDAO->getLastInsertId();
    }

    return $id_bills_pos;
}

function createBillPayment($arr_bills_params, $arr_payment) {
    global $id_admin_users;
    $id_bills_payments = -1;

    $status = "Posted";

    $billPaymentDTO = new BillsPaymentsDTO();
    $billsPaymentDAO = new BillsPaymentsDAO();

    $billPaymentDTO->setID_banks($arr_payment['payment_bank']);
    $billPaymentDTO->setID_vendors($arr_bills_params['id_vendors']);
    $billPaymentDTO->setName("");
    $billPaymentDTO->setDescription("Anticipo del Purchase Order: " . $arr_bills_params['id_purchaseorders']);
    $billPaymentDTO->setAmount($arr_payment['payment_amount']);
    $billPaymentDTO->setCurrency($arr_payment['payment_currency']);
    $billPaymentDTO->setStatus($status);
    $billPaymentDTO->setID_admin_users($id_admin_users);

    if ($billsPaymentDAO->insertRecord($billPaymentDTO)) {
        $id_bills_payments = $billsPaymentDAO->getLastInsertId();

        //-- crea las notas
        $billPaymentNotesDTO = new BillsPaymentsNotesDTO();
        $billsPaymentsNotesDAO = new BillsPaymentsNotesDAO();

        $notes = "Anticipo del Purchase Order: " . $arr_bills_params['id_purchaseorders'] . "\n" . $arr_payment['payment_notes'];

        $billPaymentNotesDTO->setID_billspayments($id_bills_payments);
        $billPaymentNotesDTO->setNotes($notes);
        $billPaymentNotesDTO->setID_admin_users($id_admin_users);

        $billsPaymentsNotesDAO->insertRecord($billPaymentNotesDTO);
    }
    return $id_bills_payments;
}

function createBillPaymentBill($arr_bills_params, $arr_payment) {
    global $id_admin_users;
    $id_billspayments_bills = -1;
    $status = "Processed";

    $bpbDTO = new BillsPaymentsBillsDTO();
    $bpbDAO = new BillsPaymentsBillsDAO();

    $bpbDTO->setID_billspayments($arr_bills_params['id_bills_payments']);
    $bpbDTO->setID_bills($arr_bills_params['id_bills']);
    $bpbDTO->setStatus($status);
    $bpbDTO->setID_admin_users($id_admin_users);

    if ($bpbDAO->insertRecord($bpbDTO)) {
        $id_billspayments_bills = $bpbDAO->getLastInsertId();
    }
    return $id_billspayments_bills;
}

?>