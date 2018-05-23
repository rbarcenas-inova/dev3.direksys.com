<?php

session_start();

include_once '../../../trsBase.php';

require_once '../../../common/php/class/db/DbHandler.php';
require_once '../../../common/php/class/dto.catalog.InvoicesDTO.php';
require_once '../../../common/php/class/dao.catalog.InvoicesDAO.php';

$COMMON_PATH = "../..";
$e=$in['e'];
$file_path = $cfg['path_invoices_tocert'].'e'.$e.'/cfdi/results/';
$total_folios = $cfg['cfdi_tot_folios'];
$ftp_path = $cfg['cfdi_ftp_path'];
if($ftp_path!=''){$ftp_path.='/';}
//---- parametros de paginacion 
$results_per_page = isset($_POST['results_per_page']) ? $_POST['results_per_page'] : (isset($_GET['results_per_page']) ? $_GET['results_per_page'] : $cfg['results_page']);
$page = isset($_POST['pagenum']) ? $_POST['pagenum'] : (isset($_GET['pagenum']) ? $_GET['pagenum'] : 1);
$start = ($page - 1) * $results_per_page;
//----
$total_results = $_SESSION['TOTAL_RESULTADOS_CFDI']; //-- total de resultados de la consulta
$criteria_change = isset($_POST['criteria_change']) ? $_POST['criteria_change'] : "";       //-- recibe si se cambio el criterio

$invoicesDAO = new InvoicesDAO();
if ($criteria_change == "1") {
    //-- si hubo cambio de algun criterio de busqueda recibe los parametros
    $ID_invoices = trim($_POST['id_invoices']);
    $ID_customers = trim($_POST['id_customers']);
    $name_customers = trim($_POST['name_customers']);
    $doc_serial = trim($_POST['doc_serial']);
    $doc_num = trim($_POST['doc_num']);
    $start_date = trim($_POST['date_start']);
    $end_date = trim($_POST['date_end']);
    $doc_type = trim($_POST['doc_type']);
    $doc_status = trim($_POST['doc_status']);
    $uuid = trim($_POST['uuid']);
    $customer_fcode = trim($_POST['customer_fcode']);
    $id_orders = trim($_POST['id_orders']);
    $viewed = trim($_POST['doc_viewed']);

    $invoicesDTO = new InvoicesDTO();
    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setID_customers($ID_customers);
    $invoicesDTO->setCustomerName($name_customers);
    $invoicesDTO->setDocSerial($doc_serial);
    $invoicesDTO->setDocNum($doc_num);
    $invoicesDTO->setDocDate($start_date);
    $invoicesDTO->setExtraField($end_date);
    $invoicesDTO->setInvoiceType($doc_type);
    $invoicesDTO->setStatus($doc_status);
    $invoicesDTO->setUuid($uuid);
    $invoicesDTO->setCustomerFiscalCode($customer_fcode);
    $invoicesDTO->setViewed($viewed);

    //-- calcula las paginas para los resultados
    $invoicesDAO->onlyCountRows(TRUE);
    $invoicesDAO->selectRecords($invoicesDTO);
    $total_results = $invoicesDAO->getNumRows();

    $pages = ceil($total_results / $results_per_page);
    $_SESSION['TOTAL_PAGINAS_CFDI'] = $pages;

    $arr_seach_criteria = array(
        'id_invoices' => $ID_invoices,
        'id_customers' => $ID_customers,
        'name_customers' => $name_customers,
        'doc_serial' => $doc_serial,
        'doc_num' => $doc_num,
        'date_start' => $start_date,
        'date_end' => $end_date,
        'doc_type' => $doc_type,
        'doc_status' => $doc_status,
        'uuid' => $uuid,
        'customer_fcode' => $customer_fcode,
        'id_orders' => $id_orders,
        'viewed' => $viewed
    );

    $_SESSION['ARRAY_SEARCH_CRITERIA'] = $arr_seach_criteria;
}

$arr_seach_criteria = $_SESSION['ARRAY_SEARCH_CRITERIA'];


$invoicesDTO = new InvoicesDTO();

$invoicesDTO->setID_invoices($arr_seach_criteria['id_invoices']);
$invoicesDTO->setID_customers($arr_seach_criteria['id_customers']);
$invoicesDTO->setCustomerName($arr_seach_criteria['name_customers']);
$invoicesDTO->setDocSerial($arr_seach_criteria['doc_serial']);
$invoicesDTO->setDocNum($arr_seach_criteria['doc_num']);
$invoicesDTO->setDocDate($arr_seach_criteria['date_start']);
$invoicesDTO->setExtraField($arr_seach_criteria['date_end']);
$invoicesDTO->setInvoiceType($arr_seach_criteria['doc_type']);
$invoicesDTO->setStatus($arr_seach_criteria['doc_status']);
$invoicesDTO->setUuid($arr_seach_criteria['uuid']);
$invoicesDTO->setCustomerFiscalCode($arr_seach_criteria['customer_fcode']);
$invoicesDTO->setViewed($arr_seach_criteria['viewed']);

$invoicesDAO->setOrderBy("ID_invoices_desc");
$invoicesDAO->setPagerStart($start);
$invoicesDAO->setPagerPerPage($results_per_page);
$vector_invoices = $invoicesDAO->selectRecords($invoicesDTO);

$echo_string = generateHtml($vector_invoices);

echo $echo_string;
?>
<?php

function generateHtml($vector_invoices) {
    global $COMMON_PATH;
    global $file_path;
    global $e;
    global $page;
    global $total_folios;
    global $ftp_path;

    if (!empty($vector_invoices)) {
        $invoicesDTO = new InvoicesDTO();
        
        $str_html = '<table width="99%" align="center"  class="List">
                    <tr class="tableListColumn">
                        <td width="5%" align="center">ID</td>
                        <td width="8%" align="center">Serie / Folio</td>
                        <td width="8%" align="center"></td>
                        <td width="12%" align="center">Fecha y Hora</td>
                        <td style="min-width: 10%;" align="left">RFC</td>
                        <td align="left">Nombre o Raz&oacute;n Social</td>
                        <td style="min-width: 6%;" align="center">Total</td>
                        <td style="min-width: 10%;" align="center">Tipo Documento</td>
                        <td style="min-width: 6%;" align="center">Status</td>
                        <td align="center"></td>
                        <td align="center" colspan="2">Acciones</td>
                        <td align="center" ><input type="checkbox" id="select_all"><input type="hidden" id="ToPrint"></td>'
                        .'<td align="center" colspan="1"><img src="' . $COMMON_PATH . '/common/img/download_file.png" height="16px" width="16px" style="cursor: pointer" onclick="PrintPDF(ToPrint.value,0)" alt="Descargar PDF Seleccionados" /></td>
                        <td align="center" colspan="1"><img src="' . $COMMON_PATH . '/common/img/zip.png" height="16px" width="16px" style="cursor: pointer" onclick="ZipXML(ToPrint.value)" alt="Descargar XML Seleccionados" /></td>
                    </tr>';

        $style = 0;
        $flagCSS = FALSE;

            foreach ($vector_invoices as $invoicesDTO) {
                $_xmlEmision = '';
                $_xmlUUID  = '';
                $_xmlTimbrado = '';
                $objCFD = false;
                if($invoicesDTO->getStatus()!='Transition'){ // Omitir Status especificos
                    if ($flagCSS) {
                        $style = 1;
                        $flagCSS = FALSE;
                    } else {
                        $style = 0;
                        $flagCSS = TRUE;
                    }
                    //--Detecta el tipo de moneda
                    switch(strtoupper($invoicesDTO->getCurrency())){
                      case 'MXP': $Moneda='Pesos'; $Sigla=' M.N.'; $Signo='$'; break;
                      case 'USD': $Moneda='Dolares'; $Sigla=' US Cy'; $Signo='US$';break;
                      default: $Moneda='Pesos'; $Sigla=' M.N.'; $Signo='$';
                    }

                    if($invoicesDTO->getCreditDays()==0 && ($invoicesDTO->getStatus()=='New')){
                        $color1='style="color:red;"'; $txtAut=' - Req. Auth';}
                    else{$color1=''; $txtAut='';}

                    if($invoicesDTO->getStatus()=='Cancelled'){$color='style="color:#BA2B3C;"';}
                    elseif($invoicesDTO->getStatus()=='Certified'){$color='style="color:#0FA311;"';}
                    elseif($invoicesDTO->getStatus()=='New' || $invoicesDTO->getStatus()=='OnEdition'){$color='style="color:#1F9BDE;"';}
                    elseif($invoicesDTO->getStatus()=='InProcess'){$color='style="color:#CCBD49;"';}
                    else{$color='';}
                    $str_html .= '<tr class="tableFila' . $style . '">
                    <td align="center" '.$color1.'>' . $invoicesDTO->getID_invoices() . '</td>
                    <td '.$color1.'>' . $invoicesDTO->getDocSerial() . ' ' . $invoicesDTO->getDocNum() . $txtAut . '</td>
                    <td></td>
                    <td '.$color1.'>' . $invoicesDTO->getDocDate() . '</td>
                    <td align="left" '.$color1.'>' . $invoicesDTO->getCustomerFiscalCode() . '</td>
                    <td align="left" '.$color1.'>' . $invoicesDTO->getCustomerName() . '</td>
                    <td align="right" '.$color1.'>' . $Signo .' ' . number_format($invoicesDTO->getInvoiceTotal(), 2, '.', ',') . '</td>
                    <td align="center" '.$color1.'>' . $invoicesDTO->getInvoiceType() . '</td>
                    <td align="center" '.$color.'>' . $invoicesDTO->getStatus() . '</td>
                    <td align="center">';
                    $str_html .= '<img src="' . $COMMON_PATH . '/common/img/view.png" height="16px" width="16px" style="cursor: pointer" onclick="editCFDI(' . $invoicesDTO->getID_invoices() . ',' . $page . ')" alt="Detalle" target="_blank" />&nbsp;';
                    $str_html .= '</td>';
                    $str_html .= '<td align="center">';            

                    
                    /** Busca por FTP archivos PDF y XML y los copia a /cfdi/results/ para mostrarlos */           
                    $file_pdf=$invoicesDTO->getDocSerial() . '_' . $invoicesDTO->getDocNum(). '.pdf';
                    $file_xml=$invoicesDTO->getDocSerial() . '_' . $invoicesDTO->getDocNum(). '.xml';
                    $file_xml_adenda=$invoicesDTO->getDocSerial() . '_' . $invoicesDTO->getDocNum(). '_A.xml';
                   
                    /**/
                    #if(SearchFile($file_pdf)){
                        /*Establece carpeta correspondiente al folio del invoice*/
                        if($invoicesDTO->getDocNum()>=$total_folios){
                            $Folder=floor($invoicesDTO->getDocNum()/$total_folios)*$total_folios;
                        }else{$Folder=1;} 
                        
                        $FolderName=$Folder; 
                        $FolderSerial='/'.$ftp_path.$invoicesDTO->getDocSerial().'/';                       
                        $FolderNum=$FolderSerial.$FolderName.'/';
                    if($invoicesDTO->getViewed()<1 && $invoicesDTO->getDocSerial()!=''){
                        /*
                        //--Crea Directorio si no existe
                        if(!CheckFolder($FolderSerial)){MakeDir($FolderSerial);}
                        if(!CheckFolder($FolderNum)){MakeDir($FolderNum);}
                        if(SearchFile('/'.$ftp_path.$file_pdf) && SearchFile('/'.$ftp_path.$file_xml) && ($invoicesDTO->getStatus()=='InProcess')){  
                        #LECTURA DE XML (@ivan.miranda);
                            //echo "AQUI";
                            $_cfd = tempnam(sys_get_temp_dir(), "cfd");
                            DownloadFile('/'.$ftp_path.$file_xml, $_cfd);
                            $objCFD = simplexml_load_file($_cfd);
                            #echo "{$ftp_path}{$file_xml}::obj {$objCFD}<br/>";
                            if($objCFD){
                                $objNS = $objCFD->getNamespaces(true);
                                $objCFD->registerXPathNamespace('c', $objNS['cfdi']);
                                $objCFD->registerXPathNamespace('t', $objNS['tfd']);
                                foreach ($objCFD->xpath('//c:Comprobante') as $cfdiComprobante){ 
                                   $_xmlEmision = substr($cfdiComprobante['fecha'],0,10);
                                }
                                foreach ($objCFD->xpath('//t:TimbreFiscalDigital') as $cfdiComprobante){ 
                                    $_xmlUUID = $cfdiComprobante['UUID'];
                                    $_xmlTimbrado = substr($cfdiComprobante['FechaTimbrado'],0,10);
                                }
                            }
                            unlink($_cfd);
                            $exito = updateStatus($invoicesDTO->getID_invoices(),$_xmlUUID,$_xmlTimbrado,$_xmlEmision); // Actualiza Status a Certified    
                            $exit=updateRead($invoicesDTO->getID_invoices(),1);
                            Update_Invoice_logs($ID_Invoices=$invoicesDTO->getID_invoices()); // Actualiza cu_invoices_logs
                        }
                        */
                    }elseif($invoicesDTO->getViewed()>0 && $invoicesDTO->getDocSerial()!=''){ 
                        /*

                        if(SearchFile('/'.$ftp_path.$file_pdf)){
                            MoveFile('/'.$ftp_path.$file_pdf, $FolderNum.$file_pdf); 
                        }                               
                        if(SearchFile('/'.$ftp_path.$file_xml_adenda)){
                            MoveFile('/'.$ftp_path.$file_xml_adenda, $FolderNum.$file_xml_adenda);
                        }
                        if(SearchFile('/'.$ftp_path.$file_xml)){
                        #LECTURA DE XML (@ivan.miranda);
                            $_cfd = tempnam(sys_get_temp_dir(), "cfd");
                            DownloadFile('/'.$ftp_path.$file_xml, $_cfd);
                            $objCFD = simplexml_load_file($_cfd);
                            #echo "{$ftp_path}{$file_xml}::obj {$objCFD}<br/>";
                            if($objCFD){
                                $objNS = $objCFD->getNamespaces(true);
                                $objCFD->registerXPathNamespace('c', $objNS['cfdi']);
                                $objCFD->registerXPathNamespace('t', $objNS['tfd']);
                                foreach ($objCFD->xpath('//c:Comprobante') as $cfdiComprobante){ 
                                   $_xmlEmision = substr($cfdiComprobante['fecha'],0,10);
                                }
                                foreach ($objCFD->xpath('//t:TimbreFiscalDigital') as $cfdiComprobante){ 
                                    $_xmlUUID = $cfdiComprobante['UUID'];
                                    $_xmlTimbrado = substr($cfdiComprobante['FechaTimbrado'],0,10);
                                }
                            }
                            unlink($_cfd);

                            MoveFile('/'.$ftp_path.$file_xml, $FolderNum.$file_xml);
                        }

                        
                        if($invoicesDTO->getViewed()>0 && $invoicesDTO->getDocSerial()!='' && $invoicesDTO->getStatus()=='InProcess'){
                            $exit = updateStatus($invoicesDTO->getID_invoices(),$_xmlUUID,$_xmlTimbrado,$_xmlEmision); // Actualiza Status a Certified    
                            Update_Invoice_logs($ID_Invoices=$invoicesDTO->getID_invoices()); // Actualiza cu_invoices_logs                
                        }
                        */
                        
                        if(SearchFile($FolderNum.$file_xml_adenda)){$file_xml=$file_xml_adenda;}                            
                        $str_html .= '<a href="cfdi_doc.php?f='.$file_pdf.'&id='.$invoicesDTO->getID_invoices().'&m=2" target="_blank"><img src="' . $COMMON_PATH . '/common/img/pdf.gif" height="16px" width="16px" style="cursor: pointer" /></a>&nbsp;';
                        $str_html .= '<a href="cfdi_doc.php?f='.$file_xml.'&id='.$invoicesDTO->getID_invoices().'&m=2" target="_blank" ><img src="' . $COMMON_PATH . '/common/img/xml.gif" height="16px" width="16px" style="cursor: pointer" alt="XML" /></a>&nbsp;';
                        $str_html .= '</td>';
                        $str_html .= '<td align="center">';
                        $str_html .= '<a href="cfdi_doc.php?f='.$file_pdf.'&id='.$invoicesDTO->getID_invoices().'&m=0" target="_blank" alt="Descargar PDF"><img src="' . $COMMON_PATH . '/common/img/pdf_download.gif" height="16px" width="16px" style="cursor: pointer" /></a>&nbsp;';                
                        $str_html .= '<a href="cfdi_doc.php?f='.$file_xml.'&id='.$invoicesDTO->getID_invoices().'&m=0" target="_blank" ><img src="' . $COMMON_PATH . '/common/img/xml_download.gif" height="16px" width="16px" style="cursor: pointer" alt="XML" /></a>&nbsp;';
                        $str_html .= '</td>';
                        $str_html .= '<td align="center" colspan="4">';
                        $str_html .= '<input type="checkbox" id="'.substr($file_pdf,0,strlen($file_pdf)-4).'" value="1" onclick="CheckInOut(this.id,ToPrint.value)" >';
                        $str_html .= '</td></tr>';
                    }  

                }     
            }
        $str_html .= '</table>';
    } else {
        $str_html = "<table width='100%' align='center'><tr><td align='center'>No se encontraron comprobantes fiscales con el criterio seleccionado.</td></td></table>";
    }
    return utf8_encode($str_html);
}

function updateStatus($ID_invoices,$uuid="",$timbrado="",$emision="") {
    $exito = FALSE;
    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();
    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setStatus("Certified");
#Informacion de XML (@ivan.miranda)
    if(strlen(trim($uuid))>0)
        $invoicesDTO->setXml_uuid($uuid);
    if(strlen(trim($timbrado))>0)
        $invoicesDTO->setXml_fecha_emision($timbrado);
    if(strlen(trim($emision))>0)
        $invoicesDTO->setXml_fecha_certificacion($emision);
    $exito = $invoicesDAO->updateRecord($invoicesDTO);
    return $exito;
}

function updateRead($ID_invoices, $value=1) {
    $exito = FALSE;
    $invoicesDTO = new InvoicesDTO();
    $invoicesDAO = new InvoicesDAO();
    $invoicesDTO->setID_invoices($ID_invoices);
    $invoicesDTO->setViewed($value);
    $exit = $invoicesDAO->updateRecord($invoicesDTO);
    return $exit;
}
function Update_Invoice_logs($ID_Invoices='0'){
    global $User;
    global $Password;
    global $Server;
    global $DataBase; 
    $Action='Received';
    #date_default_timezone_set("America/Mexico_City");
    #$Timestamp=date("Y-m-d G:i:s"); 
    $link=mysql_connect($Server, $User, $Password) or die(mysql_error());
    mysql_select_db($DataBase, $link);
    $sql="insert into cu_invoices_logs 
            (Action, ID_invoices, doc_serial, doc_num, doc_date, ID_orders, ID_creditmemos, Timestamp, ID_admin_users)
            select '$Action', a.ID_invoices, a.doc_serial, a.doc_num, a.doc_date, b.ID_orders, b.ID_creditmemos, CURRENT_TIMESTAMP(), a.ID_admin_users
            from cu_invoices a
            left join cu_invoices_lines b using(ID_invoices) 
            where a.ID_invoices=$ID_Invoices
            group by a.ID_invoices";
    $con=mysql_query($sql, $link) or die(mysql_error());
}

?>
<script>
$('#select_all').click(function() {
    var c = this.checked;
    $(':checkbox').prop('checked',c);
    $(':checkbox').each(function(){
        $('#ToPrint').val('');
        $("input:checkbox[id^='M']").click();
        $(':checkbox').prop('checked',c);
    });
});
function CheckInOut(CheckID, FilesPDF){
    var Check=document.getElementById(CheckID).checked;
    if(Check==true){
        FilesPDF = FilesPDF.split(CheckID+'|');
        FilesPDF = FilesPDF.join('',FilesPDF);
        FilesPDF = CheckID+'|'+FilesPDF;
    }else{
        FilesPDF = FilesPDF.split(CheckID+'|');
        FilesPDF = FilesPDF.join('',FilesPDF);
    } 
    document.getElementById('ToPrint').value=FilesPDF;
}
function PrintPDF(FilesPDF,Mode){
    //if(Mode==''){Mode=2;}
    var Len = FilesPDF.length;
    FilesPDF = FilesPDF.substr(0,Len-1);
    var Page='cfdi_pdfprint.php?f='+FilesPDF+'&m='+Mode;
    if(FilesPDF!=''){
        window.open(Page,'Impresion Multiple','toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no,resizable=no, copyhistory=no,width=500,height=630');
    }else{alert('Seleccione al menos un documento.');}
}
function ZipXML(FilesXML){
    var Len = FilesXML.length;
    FilesXML = FilesXML.substr(0,Len-1);
    var Page='cfdi_xmlzip.php?f='+FilesXML;
    if(FilesXML!=''){
        window.open(Page,'Descarga XML Multiple','toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no,resizable=no, copyhistory=no,width=500,height=630');
    }else{alert('Seleccione al menos un documento.');}
}
</script>