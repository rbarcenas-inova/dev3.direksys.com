<?php
/**
** Descripcion: Une varios documentos PDF en uno solo.
** Requiere: Clase FPDF y clase FPDI con FPDF_TPL
** @author: Oscar Maldonado
** @date: 2013/05/28
** @params:
**  $Path => Ruta de Origen/detino para los archivos pdf's
**  $FilesSource => cadena de nombres de archivos a unir, ejem: arc1.pdf|arc2.pdf ejem2: arc_sd|as_sd
**  $Separator => Caracter que separa los nombres en $FilesSource
**  $FileResult => Nombre de archivo que resultara
**  $PathSrc => Ruta en donde esta las librerias FPDF y FPDI
**  $Timestamp => True para imprimir fecha-hora en el nombre del archivo
**  $Mode  0/I=> Abrir; 1/D=> Descargar; 2/F=> Crear archivo en carpeta
*/
function ImplodePDF($Path='/', $FilesSource, $Separator='|', $FileResult='Implode-PDF', $PathSrc='/', $Timestamp=true,$Mode=0){
	if(trim($FilesSource)!=''){			
		require_once($PathSrc.'fpdf/fpdf.php');
		require_once($PathSrc.'fpdi/fpdi.php');
		class Concat_pdf extends FPDI {        
			var $files = array();  
			function setFiles($files) {  
				$this->files = $files;  
			}  
			function Concat() {  
				foreach($this->files as $file) {  
					$pagecount = $this->setSourceFile($file);  
					for ($i = 1; $i <= $pagecount; $i++) {                    
						$tplidx = $this->ImportPage($i);  
						 $s = $this->getTemplatesize($tplidx);  
						 $this->AddPage('P', array($s['w'], $s['h']));  
						 $this->useTemplate($tplidx);  
					}  
				}  
			}  
		} 
		$FilesSource=explode($Separator,$FilesSource);	
		for($x=0; $x<count($FilesSource); $x++){
			if(substr($FilesSource[$x],strlen($FilesSource[$x])-4,4)!='.pdf'){$FilesSource[$x].='.pdf';}			
			$FilesSource[$x]=$Path.$FilesSource[$x];
		}
		$pdf = new Concat_pdf();   
		$pdf->setFiles($FilesSource);
		$pdf->Concat(); 
		if($Timestamp){$Timestamp = '_'.date('Ymd-His');}else{$Timestamp='';}
		$FileResult=explode('.pdf',$FileResult);
		$FileResult=$FileResult[0].$Timestamp.'.pdf';
		switch($Mode){
			case 0 : $Mode='D'; break;
			case 1 : $Mode='I'; break;
			case 2 : $Mode='F'; break;
			default: $Mode='D';
		}
		$pdf->Output($FileResult, $Mode);
		return $FileResult;
	}else{return 'Error: Los archivos ORIGEN no existen.';}
}
?>