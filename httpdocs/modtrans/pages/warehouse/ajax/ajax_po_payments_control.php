<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();
include_once '../../../trsBase.php';

$RELATIVE_COMMON_PATH = "../..";

$action = isset($_POST['action']) ? $_POST['action'] : $in['action'];

if (isset($_SESSION['ARRAY_PO_PAYMENTS'])) {
    $array_po_payments = $_SESSION['ARRAY_PO_PAYMENTS'];
} else {
    $array_po_payments = array();
}

if ($action == 'add_payment') {
    //--- agrega una parte del widget de busqueda al listado
    $pdate = isset($_POST['pay_date']) ? $_POST['pay_date'] : "0000-00-00";
    $pamount = isset($_POST['pay_amount']) ? $_POST['pay_amount'] : 0;
    $pnotes = isset($_POST['pay_notes']) ? $_POST['pay_notes'] : "";
    $pbank = isset($_POST['pay_bank']) ? $_POST['pay_bank'] : "";
    $pbank_name = isset($_POST['pay_bank_name']) ? $_POST['pay_bank_name'] : "";
    $pcurrency = isset($_POST['pay_currency']) ? $_POST['pay_currency'] : "";
    $pcurrency_name = isset($_POST['pay_currency_name']) ? $_POST['pay_currency_name'] : "";

    $array_po_payment_info = array(
        'payment_date' => $pdate,
        'payment_amount' => $pamount,
        'payment_notes' => $pnotes,
        'payment_bank' => $pbank,
        'payment_bank_name' => $pbank_name,
        'payment_currency' => $pcurrency,
        'payment_currency_name' => $pcurrency_name
    );

    $array_po_payments[] = $array_po_payment_info;
    $_SESSION['ARRAY_PO_PAYMENTS'] = $array_po_payments;

    showPaymentsList($array_po_payments);
} else if ($action == 'del_payment') {
    //-- borra los datos del payment
    $idx = isset($_POST['idx']) ? $_POST['idx'] : $in['idx'];

    unset($array_po_payments[$idx]);
    $_SESSION['ARRAY_PO_PAYMENTS'] = $array_po_payments;
    showPaymentsList($array_po_payments);
} else if ($action == 'show_payments_list') {
    showPaymentsList($array_po_payments);
}
?>
<?php

function showPaymentsList($array_po_payments) {
    global $RELATIVE_COMMON_PATH;
    if (!empty($array_po_payments)) {
        ?>
        <table width="650px" align="center"  class="List">
            <tr class="tableListColumn">
                <td width="3%" align="center">#</td>
                <td width="10%" align="center">Fecha</td>
                <td width="10%" align="center">Entidad Bancaria</td>
                <td style="min-width: 10%;" align="right">Monto</td>
                <td style="min-width: 10%;"></td>
                <td style="width: 5%;"></td>
            </tr>
            <?php
            $style = 0;
            $flagCSS = FALSE;
            $itemCount = 0;
            $grandTotal = 0;

            foreach ($array_po_payments as $idx => $arr_payments) {
                $grandTotal += floatval($arr_payments["payment_amount"]);
                if ($flagCSS) {
                    $style = 1;
                    $flagCSS = FALSE;
                } else {
                    $style = 0;
                    $flagCSS = TRUE;
                }
                ?>
                <tr class="tableFila<?php echo $style; ?>">
                    <td align="center"><?php echo++$itemCount; ?></td>
                    <td align="center"><?php echo $arr_payments["payment_date"]; ?></td>
                    <td align="center"><?php echo $arr_payments["payment_bank_name"]; ?></td>
                    <td align="right" style="padding-right: 5px;">$ <?php echo number_format($arr_payments["payment_amount"], 2, '.', ','); ?></td>
                    <td align="left">                    
                        <?php echo $arr_payments["payment_notes"]; ?>                    
                    </td>
                    <td align="center">
                        <img src="<?php echo $RELATIVE_COMMON_PATH ?>/common/img/delete.png" height="12px" width="12px" style="cursor: pointer" onclick="ajaxPOPayment(<?php echo $idx; ?>)" />
                    </td>
                </tr>
                <?php
            }
            ?>
            <tr><td colspan="6"><hr></td></tr>    
            <tr class="tableFila1">
                <td colspan="2"></td>
                <td align="right">Total = </td>
                <td align="right"><strong>$&nbsp;<?php echo number_format($grandTotal, 2, '.', ','); ?></strong>
                </td>
                <td colspan="3"></td>
            </tr>        
        </table>
        <?php
    }
}
?>