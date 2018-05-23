<?php

require_once 'com.IdentificacionDocumento.php';
require_once 'com.EmisorDatos.php';
require_once 'com.EmisorDomicilioFiscal.php';
require_once 'com.EmisorLugarExp.php';
require_once 'com.ReceptorDatos.php';
require_once 'com.ReceptorDomicilioFiscal.php';
require_once 'com.ReceptorLugarRecp.php';
require_once 'com.DetalleConceptos.php';
require_once 'com.TotalesDoc.php';
require_once 'com.ImpuestosRetenciones.php';
require_once 'com.ImpuestosTraslados.php';
require_once 'com.DescuentosGlobales.php';
require_once 'com.Addendas.php';
require_once 'com.Personalizados.php';
require_once 'com.PersonalizadosBanca.php';
require_once 'com.PersonalizadosLibres.php';
require_once 'com.ContactoEmisor.php';
require_once 'com.ContactoReceptor.php';
require_once 'com.Poliza.php';
require_once 'com.Vehiculo.php';
require_once 'com.Servicio.php';
require_once 'com.Local.php';
require_once 'com.TotalSubMonto.php';
require_once 'com.Referencia.php';


//--- definicion de las estructuras que conforman el layout para signature

class SignatureCFDILayout {

    private $coulmn_blank_spaces;

    function __construct() {
        $this->coulmn_blank_spaces = 17;    //-- numero de caracteres del ancho de la columna;
    }

    public function getCoulmn_blank_spaces() {
        return $this->coulmn_blank_spaces;
    }

    private function getDomicilio($objectDir) {
        $objectDir instanceof Direccion;


        $DOMICILIO = array(
            'Calle' => $objectDir->getCalle(),
            'NroExterior' => $objectDir->getNroExterior(),
            'NroInterior' => $objectDir->getNroInterior(),
            'Colonia' => $objectDir->getColonia(),
            'Localidad' => $objectDir->getLocalidad(),
            'Referencia' => $objectDir->getReferencia(),
            'Municipio' => $objectDir->getMunicipio(),
            'Estado' => $objectDir->getEstado(),
            'Pais' => $objectDir->getPais(),
            'CodigoPostal' => $objectDir->getCodigoPostal(),
            'GLN' => $objectDir->getGLN()
        );

        return $DOMICILIO;
    }

    function getSpoolStart() {
        $spoolStart = "XXXINICIO";
        return $spoolStart;
    }

    function getHeaderDocumentoIdentificacion() {
        $header_idDocumento = "================ IdDoc";
        return $header_idDocumento;
    }

    function getDocumentoIdentificacion(&$objectIdDoc) {
        $objectIdDoc instanceof IdentificacionDocumento;

        $IDENTIFICACION_DOCUMENTO = array(
            'NumeroInterno' => $objectIdDoc->getNumeroInterno(),
            'NroAprob' => $objectIdDoc->getNroAprob(),
            'AnoAprob' => $objectIdDoc->getAnoAprob(),
            'Tipo' => $objectIdDoc->getTipo(),
            'Serie' => $objectIdDoc->getSerie(),
            'Folio' => $objectIdDoc->getFolio(),
            'Estado' => $objectIdDoc->getEstado(),
            'FechaEmis' => $objectIdDoc->getFechaEmis(),
            'FormaPago' => $objectIdDoc->getFormaPago(),
            'MedioPago' => $objectIdDoc->getMedioPago(),
            'CondPago' => $objectIdDoc->getCondPago(),
            'TermPagoCdg' => $objectIdDoc->getTermPagoCdg(),
            'TermPagoDias' => $objectIdDoc->getTermPagoDias(),
            'FechaVenc' => $objectIdDoc->getFechaVenc()
        );

        return $IDENTIFICACION_DOCUMENTO;
    }

    function getEmisorDatosHeader() {
        $header_datosEmisor = "================ ExEmisor";
        return $header_datosEmisor;
    }

    function getEmisorDatos(&$obj) {
        $obj instanceof EmisorDatos;

        $DATOS_EMISOR = array(
            'RFCEmisor' => $obj->getRFCEmisor(),
            'NmbEmisor' => $obj->getNmbEmisor(),
            'CdgGLNEmisor' => $obj->getCdgGLNEmisor(),
            'TpoCdgIntEmisor1' => $obj->getTpoCdgIntEmisor1(),
            'CdgIntEmisor1' => $obj->getCdgIntEmisor1(),
            'TpoCdgIntEmisor2' => $obj->getTpoCdgIntEmisor2(),
            'CdgIntEmisor2' => $obj->getCdgIntEmisor2(),
            'CdgSucursal' => $obj->getCdgSucursal(),
            'Sucursal' => $obj->getSucursal(),
            'CdgVendedor' => $obj->getCdgVendedor()
        );

        return $DATOS_EMISOR;
    }

    function getEmisorDomicilioFiscalHeader() {
        $header = "================ ExEmisorDomFiscal";

        return $header;
    }

    function getEmisorDomicilioFiscal(&$obj) {
        return $this->getDomicilio($obj);
    }

    function getEmisorLugarExpedicionHeader() {
        $header = "================ ExEmisorLugarExped";
        return $header;
    }

    function getEmisorLugarExpedicion(&$obj) {
        return $this->getDomicilio($obj);
    }

    function getReceptorDatosHeader() {
        $header = "================ ExReceptor";
        return $header;
    }

    function getReceptorDatos(&$obj) {
        $obj instanceof ReceptorDatos;

        $DATOS_RECEPTOR = array(
            'RFCRecep' => $obj->getRFCRecep(),
            'NmbRecep' => $obj->getNmbRecep(),
            "CdgGLNRecep" => $obj->getCdgGLNRecep(),
            "TpoCdgIntRecep1" => $obj->getTpoCdgIntRecep1(),
            "CdgIntRecep1" => $obj->getCdgIntRecep1(),
            'CdgSucursal' => $obj->getCdgSucursal(),
            'Sucursal' => $obj->getSucursal(),
            'Contacto' => $obj->getContacto()
        );

        return $DATOS_RECEPTOR;
    }

    function getReceptorDomicilioFiscalHeader() {
        $header = "================ ExReceptorDomFiscal";
        return $header;
    }

    function getReceptorDomicilioFiscal(&$obj) {
        return $this->getDomicilio($obj);
    }

    function getReceptorLugarRecepcionHeader() {
        $header = "================ ExReceptorLugarRecep";
        return $header;
    }

    function getReceptorLugarRecepcion(&$obj) {
        return $this->getDomicilio($obj);
    }

    function getDetalleHeader() {
        $header = "================ Detalle";
        return $header;
    }

    function getDetalleHeadersDefinition($con,$ID_invoices) {

        $ARRAY_DETALLE_DEFINITION = array(
            'DetT' => 5,
            'TpoCodigo1' => 17,
            'VlrCodigo1' => 15,
            'TpoCodigo2' => 17,
            'VlrCodigo2' => 15,
            'TpoCodigo3' => 17,
            'VlrCodigo3' => 21,
            'In' => 3,
            'TpoLis' => 7,
            'Ds' => 3,
            'DscItem' => 151,
            'QtyItem' => 17,
            'UnmdItem' => 33,
            'SubQty' => 17,
            'SubC' => 5,
            'PBIMXN' => 17,
            'PrcBrutoItem' => 17,
            'PrcNetoItem' => 17,
            'Descue' => 7,
            'DescuentoMonto' => 17,
            'Tipo1' => 5, //Tipo
            'TasaIm1' => 7, //TasaIm
            'MontoImp1' => 17,
            'Tipo2' => 5, //Tipo
            'TasaIm2' => 7, //TasaIm
            'MontoImp2' => 17,
            'TipoRe' => 5, //Tipo
            'TasaRe' => 7,
            'MontoRet1' => 17,
            'MontoBrutoItem' => 17,
            'MontoNetoItem' => 17,
            'MontoTotalItem' => 17,
            'TpoDocRef' => 11,
            'FolioRef' => 21,
            'Aduana'=>array(),
            // 'PrepactCant' => 13,
            // 'Size' => 7,
            // 'Prepak' => 7
        );

        // $query = "select
        //     ID_orders,
        //     ID_orders_products,
        //     ID_invoices,
        //     (select 
        //         count(sl_skus_trans.ID_products)
        //     from
        //         sl_skus_trans
        //     where
        //         sl_skus_trans.ID_trs = cu_invoices_lines.ID_orders and
        //         sl_skus_trans.tbl_name='sl_orders'
            
        //     limit
        //         1
        //     ) NUM
        // from 
        //     cu_invoices_lines
        // where 
        //     ID_invoices=$ID_invoices
        // limit 100";
        // $result = $con->selectSQLcommand($query);
        // $response = '';
        // $row = mysql_fetch_array($result);
        // $numero = $row[3];
        $numero = 15;
        for ($i=0; $i < $numero; $i++) { 
            $ARRAY_DETALLE_DEFINITION['Aduana'][] = array(
                'NmbAduana' => 41,
                'NroDcto' => 17,
                'FechaDcto' => 12,
                'PalletInformation' => 35
            );
        }
        return $ARRAY_DETALLE_DEFINITION;
    }

    /**
     * 
     * @param DetalleConceptos $obj
     * @return type
     */
    function getDetalle(&$obj,$con,$line) {
        $obj instanceof DetalleConceptos;

        $ARRAY_DETALLE = array(
            'DetT' => $obj->getDetT(),
            'TpoCodigo1' => $obj->getTpoCodigo1(),
            'VlrCodigo1' => $obj->getVlrCodigo1(),
            'TpoCodigo2' => $obj->getTpoCodigo2(),
            'VlrCodigo2' => $obj->getVlrCodigo2(),
            'TpoCodigo3' => $obj->getTpoCodigo3(),
            'VlrCodigo3' => $obj->getVlrCodigo3(),
            'In' => $obj->getIn(),
            'TpoLis' => $obj->getTpoLis(),
            'Ds' => $obj->getDs(),
            'DscItem' => $obj->getDscItem(),
            'QtyItem' => $obj->getQtyItem(),
            'UnmdItem' => $obj->getUnmdItem(),
            'SubQty' => $obj->getSubQty(),
            'SubC' => $obj->getSubC(),
            'PBIMXN' => $obj->getPBIMXN(),
            'PrcBrutoItem' => $obj->getPrcBrutoItem(),
            'PrcNetoItem' => $obj->getPrcNetoItem(),
            'Descue' => $obj->getDescue(),
            'DescuentoMonto' => $obj->getDescuentoMonto(),
            'Tipo1' => $obj->getTipo1(), //Tipo
            'TasaIm1' => $obj->getTasaIm1(), //TasaIm
            'MontoImp1' => $obj->getMontoImp1(),
            'Tipo2' => $obj->getTipo2(), //Tipo
            'TasaIm2' => $obj->getTasaIm2(), //TasaIm
            'MontoImp2' => $obj->getMontoImp2(),
            'TipoRe' => $obj->getTipoRe(), //Tipo
            'TasaRe' => $obj->getTasaRe(), //TasaRe
            'MontoRet1' => $obj->getMontoRet1(),
            'MontoBrutoItem' => $obj->getMontoBrutoItem(),
            'MontoNetoItem' => $obj->getMontoNetoItem(),
            'MontoTotalItem' => $obj->getMontoTotalItem(),
            'TpoDocRef' => $obj->getTpoDocRef(),
            'FolioRef' => $obj->getFolioRef(),
            'Aduanas'=>array(),
            // 'NmbAduana' => $obj->getNmbAduana(),
            // 'NroDcto' => $obj->getNroDcto(),
            // 'FechaDcto' => $obj->getFechaDcto(),
            // 'PalletInformation' => $obj->getPalletInformation(),
            // 'PrepactCant' => $obj->getPrepactCant(),
            // 'Size' => $obj->getSize(),
            // 'Prepak' => $obj->getPrepak()
        );
        $table = ($line->getID_orders() == '') ? 'sl_creditmemos' : 'sl_orders';
        $id_trs = ($line->getID_orders() == '') ? $line->getID_creditmemos() : $line->getID_orders();
        $id_product = $line->getIdSku();
        $query = "SELECT 
            sl_skus_trans.ID_products_trans,
            cu_customs_info.import_declaration_number ,
            cu_customs_info.import_declaration_date ,
            cu_customs_info.customs ,
            sl_vendors.CompanyName 
        FROM 
            sl_skus_trans 
            LEFT JOIN cu_customs_info ON sl_skus_trans.ID_customs_info=cu_customs_info.ID_customs_info 
            LEFT JOIN sl_vendors ON sl_vendors.ID_vendors=cu_customs_info.ID_vendors 
        WHERE  
            sl_skus_trans.tbl_name='$table' and
            sl_skus_trans.ID_trs=$id_trs and 
            sl_skus_trans.ID_products=$id_product 
        GROUP BY sl_skus_trans.ID_products, sl_skus_trans.ID_customs_info 
        ORDER BY sl_skus_trans.ID_products_trans;";
        $result = $con->selectSQLcommand($query);
        while($row = mysql_fetch_array($result)) {
            $ARRAY_DETALLE['Aduanas'][] = array(
                'NmbAduana' => $row[3],
                'NroDcto' => $row[1],
                'FechaDcto' => $row[2],
                'PalletInformation' => substr($row[4],0,35)
            );
        }
        return $ARRAY_DETALLE;
    }

    function getDetalleFooter() {
        $footer = "XXXFINDETA";

        return $footer;
    }

    function getTotalesHeader() {
        $header = "================ Totales";
        return $header;
    }

    function getTotales(&$obj) {
        $obj instanceof TotalesDoc;

        $ARRAY_TOTALES = array(
            #'TotalLotes' => $obj->getTotalLotes(),
            'Moneda' => $obj->getMoneda(),
            'FctConv' => $obj->getFctConv(),
            'IndLista' => $obj->getIndLista(),
            'TipoLista' => $obj->getTipoLista(),
            'SubTotal' => $obj->getSubTotal(),
            'MntDcto' => $obj->getMntDcto(),
            'PctDcto' => $obj->getPctDcto(),
            'MntRcgo' => $obj->getMntRcgo(),
            'PctRcgo' => $obj->getPctRcgo(),
            'MntBase' => $obj->getMntBase(),
            'MntImp' => $obj->getMntImp(),
            'MntRet' => $obj->getMntRet(),
            'VlrPagar' => $obj->getVlrPagar(),
            'VlrPalabras' => $obj->getVlrPalabras()
        );

        return $ARRAY_TOTALES;
    }

    function getExImpuestosHeader() {
        $header = "================ ExImpuestos";
        return $header;
    }

    function getExImpuestos(&$obj) {
        $obj instanceof ImpuestosTraslados;


        $ARRAY_EXIMPUESTOS = array(
            'TipoImp1' => $obj->getTipoImp1(),
            'TasaImp1' => $obj->getTasaImp1(),
            'MontoImp1' => $obj->getMontoImp1(),
            'TipoImp2' => $obj->getTipoImp2(),
            'TasaImp2' => $obj->getTasaImp2(),
            'MontoImp2' => $obj->getMontoImp2()
        );

        return $ARRAY_EXIMPUESTOS;
    }

    /*
    function getExRetencionesHeader() {
        $header = "================ ExRetenciones";
        return $header;
    }
    */
    
    function getExRetencionesHeader() {
        $header = "================ ExImpuestos";
        return $header;
    }

    function getExRetenciones(&$obj) {
        $obj instanceof ImpuestosRetenciones;

        $ARRAY_RETENCIONES = array(
            'TipoImp3' => $obj->getTipoRet1(),
            'TasaImp3' => $obj->getTasaRet1(),
            'MontoImp3' => $obj->getMontoRet1(),
            'TipoImp4' => $obj->getTipoRet2(),
            'TasaImp4' => $obj->getTasaRet2(),
            'MontoImp4' => $obj->getMontoRet2()
        );

        return $ARRAY_RETENCIONES;
    }    
    
    /*
    function getExRetenciones(&$obj) {
        $obj instanceof ImpuestosRetenciones;

        $ARRAY_RETENCIONES = array(
            'TipoRet1' => $obj->getTipoRet1(),
            'TasaRet1' => $obj->getTasaRet1(),
            'MontoRet1' => $obj->getMontoRet1(),
            'TipoRet2' => $obj->getTipoRet2(),
            'TasaRet2' => $obj->getTasaRet2(),
            'MontoRet2' => $obj->getMontoRet2()
        );

        return $ARRAY_RETENCIONES;
    }
    */

    function getDescuentosGlobalHeader() {
        $header = "================ DscRcgGlobal";
        return $header;
    }

    function getDescuentosGlobal(&$obj) {
        $obj instanceof DescuentosGlobales;

        $ARRAY_DESCUENTOS = array(
            'TpoMov1' => $obj->getTpoMov1(),
            'CodigoDR1' => $obj->getCodigoDR1(),
            'GlosaDR1' => $obj->getGlosaDR1(),
            'TpoValor1' => $obj->getTpoValor1(),
            'ValorDR1' => $obj->getValorDR1(),
            'TpoMov2' => $obj->getTpoMov2(),
            'CodigoDR2' => $obj->getCodigoDR2(),
            'GlosaDR2' => $obj->getGlosaDR2(),
            'TpoValor2' => $obj->getTpoValor2(),
            'ValorDR2' => $obj->getValorDR2(),
        );

        return $ARRAY_DESCUENTOS;
    }

    function getAddendasHeader() {
        $header = "================ Addendas";
        return $header;
    }

    function getAddendas(&$obj) {
        $obj instanceof Addendas;


        $ARRAY_ADDENDAS = array(
            'IdAreaOld' => $obj->getIdAreaOld(),
            'IdArea' => $obj->getIdArea(),
            'IdRevision' => $obj->getIdRevision(),
            'Banderas' => $obj->getBanderas(),
            'ReceiverIDs' => $obj->getReceiverIDs(),
            'SenderIDGeneric' => $obj->getSenderIDGeneric(),
            'SenderID' => $obj->getSenderID(),
            'SenderIDCorvi' => $obj->getSenderIDCorvi(),
            'EmisorRI' => $obj->getEmisorRI(),
            'Addendas1' => $obj->getAddendas1(),
            'Addendas2' => $obj->getAddendas2(),
            'Addendas3' => $obj->getAddendas3(),
            'Addendas4' => $obj->getAddendas4(),
            'Addendas5' => $obj->getAddendas5(),
            'Addendas6' => $obj->getAddendas6()
        );

        return $ARRAY_ADDENDAS;
    }

    function getPersonalizadosHeader() {
        $header = "================ Personalizados";
        return $header;
    }

    function getPersonalizados(&$obj1, &$obj2, &$obj3) {
        $obj1 instanceof Personalizados;
        $obj2 instanceof PersonalizadosBanca;
        $obj3 instanceof PersonalizadosLibres;


        $ARRAY_PERSONALIZADOS = array(
            'TpoDocRefON' => $obj1->getTpoDocRefON(),
            'FolioRefON' => $obj1->getFolioRefON(),
            'FechaRefON' => $obj1->getFechaRefON(),
            'TpoDocRefDQ' => $obj1->getTpoDocRefDQ(),
            'FolioRefDQ' => $obj1->getFolioRefDQ(),
            'FechaRefDQ' => $obj1->getFechaRefDQ(),
            'FolioPedido' => $obj1->getFolioPedido(),
            'FechaPedido' => $obj1->getFechaPedido(),
            'ElaboradoPor' => $obj1->getElaboradoPor(),
            'ViaEmbarque' => $obj1->getViaEmbarque(),
            'NumEmbarque' => $obj1->getNumEmbarque(),
            'NumEmbarqueInt' => $obj1->getNumEmbarqueInt(),
            'EmURL' => $obj1->getEmURL(),
            'EmMarca' => $obj1->getEmMarca(),
            'EmRefBanBanca' => $obj2->getEmRefBanBanca(),
            'EmRefBanTitular' => $obj2->getEmRefBanTitular(),
            'EmRefBanCuenta' => $obj2->getEmRefBanCuenta(),
            'EmRefBanCLABE' => $obj2->getEmRefBanCLABE(),
            'EmRefBanConvenio' => $obj2->getEmRefBanConvenio(),
            'EmRepLegNombre' => $obj2->getEmRepLegNombre(),
            'EmRepLegRFC' => $obj2->getEmRepLegRFC(),
            'RecRepLegNombre' => $obj2->getRecRepLegNombre(),
            'RecRepLegRFC' => $obj2->getRecRepLegRFC(),
            'RecRefBanRef' => $obj2->getRecRefBanRef(),
            'RecEmailDist' => $obj2->getRecEmailDist(),
            'pPers01' => $obj3->getPPers01(),
            'pPers02' => $obj3->getPPers02(),
            'pPers03' => $obj3->getPPers03(),
            'pPers04' => $obj3->getPPers04(),
            'pPers05' => $obj3->getPPers05(),
            'pPers06' => $obj3->getPPers06(),
            'pPers07' => $obj3->getPPers07(),
            'pPers08' => $obj3->getPPers08(),
            'pPers09' => $obj3->getPPers09(),
            'pPers10' => $obj3->getPPers10(),
            'pPers11' => $obj3->getPPers11(),
            'pPers12' => $obj3->getPPers12()
        );
        return $ARRAY_PERSONALIZADOS;
    }

    function getContactoEmisorHeader() {
        $header = "================ ContactoEmisor";
        return $header;
    }

    function getContactoEmisor(&$obj) {
        $obj instanceof ContactoEmisor;

        $ARRAY_CONTACTO = array(
            'Tipo1' => $obj->getTipo1(),
            'Nombre1' => $obj->getNombre1(),
            'Descripcion1' => $obj->getDescripcion1(),
            'eMail1' => $obj->getEMail1(),
            'Telefono1' => $obj->getTelefono1(),
            'Extension1' => $obj->getExtension1(),
            'Fax1' => $obj->getFax1(),
            'Tipo2' => $obj->getTipo2(),
            'Nombre2' => $obj->getNombre2(),
            'Descripcion2' => $obj->getDescripcion2(),
            'eMail2' => $obj->getEMail2(),
            'Telefono2' => $obj->getTelefono2(),
            'Extension2' => $obj->getExtension2(),
            'Fax2' => $obj->getFax2()
        );

        return $ARRAY_CONTACTO;
    }

    function getContactoReceptorHeader() {
        $header = "================ ContactoReceptor";
        return $header;
    }

    function getContactoReceptor(&$obj) {
        $obj instanceof ContactoReceptor;

        $ARRAY_CONTACTO = array(
            'Tipo1' => $obj->getTipo1(),
            'Nombre1' => $obj->getNombre1(),
            'Descripcion1' => $obj->getDescripcion1(),
            'eMail1' => $obj->getEMail1(),
            'Telefono1' => $obj->getTelefono1(),
            'Extension1' => $obj->getExtension1(),
            'Fax1' => $obj->getFax1()
        );
        return $ARRAY_CONTACTO;
    }

    function getPolizaHeader() {
        $header = "================ Poliza";
        return $header;
    }

    function getPoliza(&$obj) {
        $obj instanceof Poliza;


        $ARRAY_POLIZA = array(
            'TipoPol' => $obj->getTipoPol(),
            'Numero' => $obj->getNumero(),
            'INC' => $obj->getINC(),
            'TpoCliente' => $obj->getTpoCliente(),
            'NroReporte' => $obj->getNroReporte(),
            'NroSint' => $obj->getNroSint(),
            'Tramitador' => $obj->getTramitador(),
            'NroExp' => $obj->getNroExp(),
            'NmbCont' => $obj->getNmbCont(),
            'CdgCont' => $obj->getCdgCont(),
            'DireccionCont' => $obj->getDireccionCont(),
            'NmbAseg' => $obj->getNmbAseg(),
            'CdgAseg' => $obj->getCdgAseg(),
            'DireccionAseg' => $obj->getDireccionAseg(),
            'NmbAfect' => $obj->getNmbAfect(),
            'CdgAfect' => $obj->getCdgAfect(),
            'DireccionAfect' => $obj->getDireccionAfect(),
            'VigDesde' => $obj->getVigDesde(),
            'VigHasta' => $obj->getVigHasta()
        );
        return $ARRAY_POLIZA;
    }

    function getVehiculoHeader() {
        $header = "================ Vehiculo";
        return $header;
    }

    function getVehiculo(&$obj) {
        $obj instanceof Vehiculo;

        $ARRAY_VEHICULO = array(
            'TipoVeh' => $obj->getTipoVeh(),
            'Marca' => $obj->getMarca(),
            'Modelo' => $obj->getModelo(),
            'Ano' => $obj->getAno(),
            'Color' => $obj->getColor(),
            'NroChasis' => $obj->getNroChasis(),
            'NroSerie' => $obj->getNroSerie(),
            'Placa' => $obj->getPlaca()
        );

        return $ARRAY_VEHICULO;
    }

    function getServicioHeader() {
        $header = "================ Servicio";
        return $header;
    }

    function getServicio(&$obj) {
        $obj instanceof Servicio;

        $ARRAY_SERVICIO = array(
            'TipoSrv' => $obj->getTipoSrv(),
            'Numero' => $obj->getNumero(),
            'NroExp' => $obj->getNroExp(),
            'Mandante' => $obj->getMandante(),
            'Ejecutor' => $obj->getEjecutor(),
            'Frecuencia' => $obj->getFrecuencia(),
            'Duracion' => $obj->getDuracion(),
            'Origen' => $obj->getOrigen(),
            'Destino' => $obj->getDestino(),
            'PeriodoDesde' => $obj->getPeriodoDesde(),
            'PeriodoHasta' => $obj->getPeriodoHasta(),
            'RazonServ' => $obj->getRazonServ()
        );

        return $ARRAY_SERVICIO;
    }

    function getLocalHeader() {
        $header = "================ Local";
        return $header;
    }

    function getLocal(&$obj) {
        $obj instanceof Local;

        $ARRAY_LOCAL = array(
            'Tipo' => $obj->getTipo(),
            'SecTipo' => $obj->getSecTipo(),
            'SecNro' => $obj->getSecNro()
        );

        return $ARRAY_LOCAL;
    }

    function getTotalSubMontoHeader() {
        $header = "================ TotSubMonto";
        return $header;
    }

    function getTotalSubMonto(&$obj) {        
        $obj instanceof TotalSubMonto;
        
        $ARRAY_SUBMONTO = array(
            'Tipo1' => $obj->getTipo1(),
            'Monto1' => $obj->getMonto1(),
            'Tipo2' => $obj->getTipo2(),
            'Monto2' => $obj->getMonto2(),
            'Tipo3' => $obj->getTipo3(),
            'Monto3' => $obj->getMonto3(),
            'Tipo4' => $obj->getTipo4(),
            'Monto4' => $obj->getMonto4(),
            'Tipo5' => $obj->getTipo5(),
            'Monto5' => $obj->getMonto5(),
            'Tipo6' => $obj->getTipo5(),
            'Monto6' => $obj->getMonto6()
        );

        return $ARRAY_SUBMONTO;
    }

    function getReferenciaHeader() {
        $header = "================ Referencia";
        return $header;
    }

    function getReferenciaHeadersDefinition() {
        $ARRAY_HEADERS = array(
            'TpoDocRef' => 11,
            'FolioRef' => 21,
            'FechaRef' => 12,
            'RazonRef' => 101,
            'MontoRef1' => 17,
            'MontoRef2' => 17
        );
        return $ARRAY_HEADERS;
    }

    function getReferencia(&$obj) {
        $obj instanceof Referencia;

        $ARRAY_HEADERS = array(
            'TpoDocRef' => $obj->getTpoDocRef(),
            'FolioRef' => $obj->getFolioRef(),
            'FechaRef' => $obj->getFechaRef(),
            'RazonRef' => $obj->getRazonRef(),
            'MontoRef1' => $obj->getMontoRef1(),
            'MontoRef2' => $obj->getMontoRef2()
        );
        return $ARRAY_HEADERS;
    }

    function getSpoolEnd() {
        $spoolEnd = "XXXFINDO";
        return $spoolEnd;
    }

}

?>