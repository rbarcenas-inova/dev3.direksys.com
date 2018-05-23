<?php

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description of com
 *
 * @author ccedillo
 */
class DetalleConceptos {

    private $DetT;
    private $TpoCodigo1;
    private $VlrCodigo1;
    private $TpoCodigo2;
    private $VlrCodigo2;
    private $TpoCodigo3;
    private $VlrCodigo3;
    private $In;
    private $TpoLis;
    private $Ds;
    private $DscItem;
    private $QtyItem;
    private $UnmdItem;
    private $SubQty;
    private $SubC;
    private $PBIMXN;
    private $PrcBrutoItem;
    private $PrcNetoItem;
    private $Descue;
    private $DescuentoMonto;
    private $Tipo1;      //-- Tipo
    private $TasaIm1;        //-- TasaIm
    private $MontoImp1;
    private $Tipo2;      //-- Tipo
    private $TasaIm2;       //-- TasaIm
    private $MontoImp2;
    private $TipoRe;        //-- Tipo
    private $TasaRe;
    private $MontoRet1;
    private $MontoBrutoItem;
    private $MontoNetoItem;
    private $MontoTotalItem;
    private $TpoDocRef;
    private $FolioRef;
    private $NmbAduana;
    private $NroDcto;
    private $FechaDcto;
    private $idOrder;
    private $palletInformation;
    private $prepactCant;    
    private $size;
    private $Prepak;

    function __construct() {
        $this->DetT = "";
        $this->TpoCodigo1 = "";
        $this->VlrCodigo1 = "";
        $this->TpoCodigo2 = "";
        $this->VlrCodigo2 = "";
        $this->TpoCodigo3 = "";
        $this->VlrCodigo3 = "";
        $this->In = "";
        $this->TpoLis = "";
        $this->Ds = "";
        $this->DscItem = "";
        $this->QtyItem = "";
        $this->UnmdItem = "";
        $this->SubQty = "";
        $this->SubC = "";
        $this->PBIMXN = "";
        $this->PrcBrutoItem = "";
        $this->PrcNetoItem = "";
        $this->Descue = "";
        $this->DescuentoMonto = "";
        $this->Tipo1 = "";
        $this->TasaIm1 = "";
        $this->MontoImp1 = "";
        $this->Tipo2 = "";
        $this->TasaIm2 = "";
        $this->MontoImp2 = "";
        $this->TipoRe = "";
        $this->TasaRe = "";
        $this->MontoRet1 = "";
        $this->MontoBrutoItem = "";
        $this->MontoNetoItem = "";
        $this->MontoTotalItem = "";
        $this->TpoDocRef =  "";
        $this->FolioRef = "";
        $this->NmbAduana = "";
        $this->NroDcto = "";
        $this->FechaDcto = "";
        $this->idOrder = "";
        $this->palletInformation = "";
        $this->prepactCant = "";              
        $this->size = "";
        $this->Prepak = "";  
    }

    public function getDetT() {
        return $this->DetT;
    }

    public function setDetT($DetT) {
        $this->DetT = $DetT;
    }

    public function getTpoCodigo1() {
        return $this->TpoCodigo1;
    }

    public function setTpoCodigo1($TpoCodigo1) {
        $this->TpoCodigo1 = $TpoCodigo1;
    }

    public function getVlrCodigo1() {
        return $this->VlrCodigo1;
    }

    public function setVlrCodigo1($VlrCodigo1) {
        $this->VlrCodigo1 = $VlrCodigo1;
    }

    public function getTpoCodigo2() {
        return $this->TpoCodigo2;
    }

    public function setTpoCodigo2($TpoCodigo2) {
        $this->TpoCodigo2 = $TpoCodigo2;
    }

    public function getVlrCodigo2() {
        return $this->VlrCodigo2;
    }

    public function setVlrCodigo2($VlrCodigo2) {
        $this->VlrCodigo2 = $VlrCodigo2;
    }

    public function getTpoCodigo3() {
        return $this->TpoCodigo3;
    }

    public function setTpoCodigo3($TpoCodigo3) {
        $this->TpoCodigo3 = $TpoCodigo3;
    }

    public function getVlrCodigo3() {
        return $this->VlrCodigo3;
    }

    public function setVlrCodigo3($VlrCodigo3) {
        $this->VlrCodigo3 = $VlrCodigo3;
    }

    public function getIn() {
        return $this->In;
    }

    public function setIn($In) {
        $this->In = $In;
    }

    public function getTpoLis() {
        return $this->TpoLis;
    }

    public function setTpoLis($TpoLis) {
        $this->TpoLis = $TpoLis;
    }

    public function getDs() {
        return $this->Ds;
    }

    public function setDs($Ds) {
        $this->Ds = $Ds;
    }

    public function getDscItem() {
        return $this->DscItem;
    }

    public function setDscItem($DscItem) {
        $this->DscItem = $DscItem;
    }

    public function getQtyItem() {
        return $this->QtyItem;
    }

    public function setQtyItem($QtyItem) {
        $this->QtyItem = $QtyItem;
    }

    public function getUnmdItem() {
        return $this->UnmdItem;
    }

    public function setUnmdItem($UnmdItem) {
        $this->UnmdItem = $UnmdItem;
    }

    public function getSubQty() {
        return $this->SubQty;
    }

    public function setSubQty($SubQty) {
        $this->SubQty = $SubQty;
    }

    public function getSubC() {
        return $this->SubC;
    }

    public function setSubC($SubC) {
        $this->SubC = $SubC;
    }

    public function getPBIMXN() {
        return $this->PBIMXN;
    }

    public function setPBIMXN($PBIMXN) {
        $this->PBIMXN = $PBIMXN;
    }

    public function getPrcBrutoItem() {
        return $this->PrcBrutoItem;
    }

    public function setPrcBrutoItem($PrcBrutoItem) {
        $this->PrcBrutoItem = $PrcBrutoItem;
    }

    public function getPrcNetoItem() {
        return $this->PrcNetoItem;
    }

    public function setPrcNetoItem($PrcNetoItem) {
        $this->PrcNetoItem = $PrcNetoItem;
    }

    public function getDescue() {
        return $this->Descue;
    }

    public function setDescue($Descue) {
        $this->Descue = $Descue;
    }

    public function getDescuentoMonto() {
        return $this->DescuentoMonto;
    }

    public function setDescuentoMonto($DescuentoMonto) {
        $this->DescuentoMonto = $DescuentoMonto;
    }

    public function getTipo1() {
        return $this->Tipo1;
    }

    public function setTipo1($Tipo1) {
        $this->Tipo1 = $Tipo1;
    }

    public function getTasaIm1() {
        return $this->TasaIm1;
    }

    public function setTasaIm1($TasaIm1) {
        $this->TasaIm1 = $TasaIm1;
    }

    public function getMontoImp1() {
        return $this->MontoImp1;
    }

    public function setMontoImp1($MontoImp1) {
        $this->MontoImp1 = $MontoImp1;
    }

    public function getTipo2() {
        return $this->Tipo2;
    }

    public function setTipo2($Tipo2) {
        $this->Tipo2 = $Tipo2;
    }

    public function getTasaIm2() {
        return $this->TasaIm2;
    }

    public function setTasaIm2($TasaIm2) {
        $this->TasaIm2 = $TasaIm2;
    }

    public function getMontoImp2() {
        return $this->MontoImp2;
    }

    public function setMontoImp2($MontoImp2) {
        $this->MontoImp2 = $MontoImp2;
    }

    public function getTipoRe() {
        return $this->TipoRe;
    }

    public function setTipoRe($TipoRe) {
        $this->TipoRe = $TipoRe;
    }

    public function getTasaRe() {
        return $this->TasaRe;
    }

    public function setTasaRe($TasaRe) {
        $this->TasaRe = $TasaRe;
    }

    public function getMontoRet1() {
        return $this->MontoRet1;
    }

    public function setMontoRet1($MontoRet1) {
        $this->MontoRet1 = $MontoRet1;
    }

    public function getMontoBrutoItem() {
        return $this->MontoBrutoItem;
    }

    public function setMontoBrutoItem($MontoBrutoItem) {
        $this->MontoBrutoItem = $MontoBrutoItem;
    }

    public function getMontoNetoItem() {
        return $this->MontoNetoItem;
    }

    public function setMontoNetoItem($MontoNetoItem) {
        $this->MontoNetoItem = $MontoNetoItem;
    }

    public function getMontoTotalItem() {
        return $this->MontoTotalItem;
    }

    public function setMontoTotalItem($MontoTotalItem) {
        $this->MontoTotalItem = $MontoTotalItem;
    }

    public function getTpoDocRef() {
        return $this->TpoDocRef;
    }

    public function setTpoDocRef($TpoDocRef) {
        $this->TpoDocRef = $TpoDocRef;
    }

    public function getFolioRef() {
        return $this->FolioRef;
    }

    public function setFolioRef($FolioRef) {
        $this->FolioRef = $FolioRef;
    }

    public function getNmbAduana() {
        return $this->NmbAduana;
    }

    public function setNmbAduana($NmbAduana) {
        $this->NmbAduana = $NmbAduana;
    }

    public function getNroDcto() {
        return $this->NroDcto;
    }

    public function setNroDcto($NroDcto) {
        $this->NroDcto = $NroDcto;
    }

    public function getFechaDcto() {
        return $this->FechaDcto;
    }

    public function setFechaDcto($FechaDcto) {
        $this->FechaDcto = $FechaDcto;
    }

    public function getIdOrder() {
        return $this->idOrder;
    }

    public function setIdOrder($idOrder) {
        $this->idOrder = $idOrder;
    }

    public function getPalletInformation() {
        return $this->palletInformation;
    }

    public function setPalletInformation($palletInformation) {
        $this->palletInformation = $palletInformation;
    }

    public function getPrepactCant() {
        return $this->prepactCant;
    }

    public function setPrepactCant($prepactCant) {
        $this->prepactCant = $prepactCant;
    }

    public function getSize() {
        return $this->size;
    }

    public function setSize($size) {
        $this->size = $size;
    }

    public function getPrepak() {
        return $this->Prepak;
    }

    public function setPrepak($Prepak) {
        $this->Prepak = $Prepak;
    }

}

?>
