<?php
/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
session_start();
include_once '../../../trsBase.php';
require_once '../../../common/php/class/db/DbHandler.php';

require_once '../../../common/php/class/dto.catalog.PurchaseOrdersDTO.php';
require_once '../../../common/php/class/dao.catalog.PurchaseOrdersDAO.php';
require_once '../../../common/php/class/dto.catalog.PurchaseOrdersItemsDTO.php';
require_once '../../../common/php/class/dao.catalog.PurchaseOrdersItemsDAO.php';
require_once '../../../common/php/class/dto.catalog.VendorsDTO.php';
require_once '../../../common/php/class/dao.catalog.VendorsDAO.php';
require_once '../../../common/php/class/dto.catalog.PartsDTO.php';
require_once '../../../common/php/class/dao.catalog.PartsDAO.php';

$poID = trim($_POST['poid']);

//-- borra la informacion de los pagos registrados previamente en sesion
unset($_SESSION['ARRAY_PO_PAYMENTS']);

//--- Crea los objetos
$poDAO = new PurchaseOrdersDAO();
$poDTO = new PurchaseOrdersDTO();
$vendorsDTO = new VendorsDTO();
$vendorsDAO = new VendorsDAO();

$poDTO->setID_purchaseorders($poID);

//--- Ejecuta la consulta
$arr_result = $poDAO->selectRecords($poDTO);

//-- informacion de vendor del PO
$vendorsDTO->setID_vendors($arr_result[0]->getID_vendors());
$arr_vendors = $vendorsDAO->selectRecords($vendorsDTO);

//-- informacion de los items del PO
$strItems = getPOitems($poID);

//--- Almacena los resultados en un array tipo JSON
$array_json = array(
    'purchaseOrderID' => $arr_result[0]->getID_purchaseorders(),
    'vendorID' => $arr_result[0]->getID_vendors(),
    'refNumber' => $arr_result[0]->getRefNumber(),
    'poDate' => $arr_result[0]->getPoDate(),
    'cancelDate' => $arr_result[0]->getCancelDate(),
    'poTerms' => $arr_result[0]->getPoTerms(),
    'poTermsDesc' => $arr_result[0]->getPoTermsDesc(),
    'type' => $arr_result[0]->getType(),
    'shipVia' => $arr_result[0]->getShipVia(),
    'otherDesc' => $arr_result[0]->getOtherDesc(),
    'warehouseID' => $arr_result[0]->getID_warehouses(),
    'status' => $arr_result[0]->getStatus(),    
    'vendorName' => $arr_vendors[0]->getCompanyName(),
    'htmlPOItems' => $strItems
);

echo json_encode($array_json);
?>
<?php

function getPOitems($id_purchaseorders) {
    $strHtml = "";

    $poItemsDTO = new PurchaseOrdersItemsDTO();
    $poItemsDAO = new PurchaseOrdersItemsDAO();

    $poItemsDTO->setID_purchaseorders($id_purchaseorders);
    $array_results = $poItemsDAO->selectRecords($poItemsDTO);
        
    $grandTotal = 0;
    if (!empty($array_results)) {

        $strHtml .= '<table width="100%" align="center"  class="List">
                    <tr class="tableListColumn">
                        <td width="3%" align="center">#</td>
                        <td width="10%">SKU</td>
                        <td>Modelo / Descripcion</td>
                        <td style="min-width: 12%;" align="center">Cantidad</td>                       
                        <td style="min-width: 20%;" align="center">Recibido</td>
                        <td style="min-width: 10%;" align="center">Precio</td>
                        <td style="min-width: 10%;" align="center">Sub Total</td>
                        <td></td>
                    </tr>';

        $style = 0;
        $flagCSS = FALSE;
        $itemCount = 0;
        
        $partsDTO = new PartsDTO();
        $partsDAO = new PartsDAO();
        
        foreach ($array_results as $poItemsDTO) {
            $grandTotal += ($poItemsDTO->getQty() * $poItemsDTO->getPrice());
            
            $itemModel = "";
            $itemName = "";
            if(substr($poItemsDTO->getID_products(), 0, 1) == '4'){
                $id_parts = substr($poItemsDTO->getID_products(), -4);
                $partsDTO->setID_parts($id_parts);
                $arr_parts = $partsDAO->selectRecords($partsDTO);                
                if(!empty($arr_parts)){
                    $itemModel = $arr_parts[0]->getModel();
                    $itemName = $arr_parts[0]->getName();
                }
            }
            
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }

            $strHtml .= '<tr class="tableFila' . $style . '">
                            <td align="center">' . ++$itemCount . '</td>
                            <td>' . $poItemsDTO->getID_products() . '</td>
                            <td>'. $itemModel .'<br>'. $itemName .'</td>
                            <td align="right"><input type="hidden" value="'.$poItemsDTO->getQty().'" style="display_none" id="hdqty-'.$poItemsDTO->getID_purchaseorders_items().'"></span>' . number_format($poItemsDTO->getQty(), 0, '.', ',') . ' unidades</td>
                            <td align="right"><span id="sp-rcv-'.$poItemsDTO->getID_purchaseorders_items().'">' . number_format($poItemsDTO->getRecieved(), 0, '.', ',') . '</span><input style="display:none; text-align: right;" class="text-box" size="5" type="text" name="txrcv-'.$poItemsDTO->getID_purchaseorders_items().'" id="txrcv-'.$poItemsDTO->getID_purchaseorders_items().'" value="'.$poItemsDTO->getRecieved().'"/> unidades&nbsp;<span id="img-edit-'.$poItemsDTO->getID_purchaseorders_items().'" style="display:inline;cursor:pointer;" onclick="triggerEditQty(\''.$poItemsDTO->getID_purchaseorders_items().'\')"><img src="../../common/img/b_edit.png" /></span><span id="img-cancelupdate-'.$poItemsDTO->getID_purchaseorders_items().'" style="display:none;"><img style="cursor:pointer;" src="../../common/img/sel_ok.png" height="16px" width="16px" onclick="validateQty('.$poItemsDTO->getID_purchaseorders_items().')" />&nbsp;<img style="cursor:pointer;" src="../../common/img/delete.png" height="16px" width="16px" onclick="triggerEditQty(\''.$poItemsDTO->getID_purchaseorders_items().'\')" /></span></td>
                            <td align="right">$ ' . number_format($poItemsDTO->getPrice(), 2, '.', ',') . '</td>                
                            <td align="right">$ ' . number_format(($poItemsDTO->getQty() * $poItemsDTO->getPrice()), 2, '.', ',') . '</td>                
                            <td align="center"></td>
                        </tr>';           
        }         
        $strHtml .= '<tr><td colspan="7"><hr></td></tr>';
        $strHtml .= '<tr class="tableFila1">
                        <td colspan="5"></td>
                        <td align="right">Total = </td>
                        <td align="right"><strong>$ ' . number_format($grandTotal, 2, '.', ',') . '</strong></td>
                    </tr>';
        $strHtml .= '</table>';        
    }    
    return utf8_encode($strHtml);
}

?>