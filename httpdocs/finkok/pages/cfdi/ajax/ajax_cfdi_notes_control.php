<?php

session_start();

require_once '../../../trsBase.php';
require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dto.catalog.InvoicesNotesDTO.php';
require_once '../../../common/php/class/dao.catalog.InvoicesNotesDAO.php';


$action = isset($_POST['action']) ? $_POST['action'] : "";
$echo_string = "";
//-- arreglo de sesion para manipular las notas;
$array_notes = isset($_SESSION['ARRAY_NOTES']) ? $_SESSION['ARRAY_NOTES'] : array();

$ID_invoices = $_POST['id_invoices'];

if ($action == "add_note") {

    $notes = $_POST['invoice_notes'];
    $type = $_POST['notes_type'];

    //-- buscar si es nota tipo ToPrint
    if ($type == 'ToPrint') {
        $flag = FALSE;

        foreach ($array_notes as $idx => $a_note) {
            if ($a_note['type'] == 'ToPrint') {
                $a_note['notes'] = $notes;
                $array_notes[$idx] = $a_note;
                $flag = TRUE;
                break;
            }
        }
        if (!$flag) {
            $arr_notes = array(
                'type' => $type,
                'notes' => $notes
            );
            $array_notes[] = $arr_notes;
        }
    } else {
        $arr_notes = array(
            'type' => $type,
            'notes' => $notes
        );
        $array_notes[] = $arr_notes;
    }

    $_SESSION['ARRAY_NOTES'] = $array_notes;
} else if ($action == "del_note") {
    $idx = $_POST['idx'];
    unset($array_notes[$idx]);

    $_SESSION['ARRAY_NOTES'] = $array_notes;
} else if ($action == "show_notes_list") {

    $echo_string = showList($array_notes, $ID_invoices);
}

echo $echo_string;
?>
<?php

function showList($array_notes, $ID_invoices) {
    $str_html = "";
    //-- Busca las notas que ya se encuentran almacenadas previamente
    $invoicesNotesDTO = new InvoicesNotesDTO();
    $invoicesNotesDAO = new InvoicesNotesDAO();

    $invoicesNotesDTO->setID_invoices($ID_invoices);
    $vector_invoices_notes = $invoicesNotesDAO->selectRecords($invoicesNotesDTO);

    if (!empty($vector_invoices_notes) || !empty($array_notes)) {
        $str_html = '<table width="99%" align="center" class="List">
                        <tr class="tableListColumn">
                            <td width="10%" align="center">Fecha</td>
                            <td width="8%" align="center">Tipo</td>
                            <td align="center">Notas</td>
                            <td width="30px" align="center"></td>
                        </tr>';
        $style = 0;
        $flagCSS = FALSE;

        foreach ($vector_invoices_notes as $invoicesNotesDTO) {
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }

            $notes_type = "Notas";
            if($invoicesNotesDTO->getType() == 'ToPrint'){
                $notes_type = "Observaciones";
            }
            
            $str_html .= '<tr class="tableFila' . $style . '">
                <td align="left" style="padding-right: 5px;">' . $invoicesNotesDTO->getDate() . '</td>
                <td style="padding-left: 5px;">' . $notes_type . '</td>
                <td>' . $invoicesNotesDTO->getNotes() . '</td>                
                <td align="center"></td>
            </tr>';
        }

        foreach ($array_notes as $idx => $a_notes) {
            if ($flagCSS) {
                $style = 1;
                $flagCSS = FALSE;
            } else {
                $style = 0;
                $flagCSS = TRUE;
            }
            
            $notes_type = "Notas";
            if($a_notes['type']=='ToPrint'){
                $notes_type = "Observaciones";
            }
            
            $str_html .= '<tr class="tableFila' . $style . '">
                <td align="left" style="padding-right: 5px;"></td>
                <td style="padding-left: 5px;">' . $notes_type . '</td>
                <td>' . $a_notes['notes'] . '</td>                
                <td align="center"><img width="16px" height="16px" onclick="deleteNote(' . $idx . ')" style="cursor: pointer" src="../../common/img/delete.png">&nbsp;</td>
            </tr>';
        }
        $str_html .='</table>';
    }
    return $str_html;
}

?>