<?php
namespace FacturasCFDI;
class Autoloader{
	private $directorios;
    private $path;
    private $namespace;
    private $separador;
    final public function __construct(){
        $this->directorios = array(__DIR__);
        $this->path = __DIR__;
        $this->namespace = explode(',',LIBS_NAMESPACES);
        $this->separador = '\\';
    }
    final public function register(){
        spl_autoload_register(array($this, 'loadClass'));
        foreach(scandir(__DIR__) as $dir) {
            if(is_dir(__DIR__.DIRECTORY_SEPARATOR.$dir) and $dir != '.' and $dir !='..'){
                if(is_file(__DIR__.DIRECTORY_SEPARATOR.$dir.DIRECTORY_SEPARATOR.'Autoloader.php')){
                    require_once __DIR__.DIRECTORY_SEPARATOR.$dir.DIRECTORY_SEPARATOR.'Autoloader.php';
                }
            }
        }
    }
    final public function unregister(){
        spl_autoload_unregister(array($this, 'loadClass'));
    }
    final public function addIncludePath($nuevoUrl){
        $this->directorios[] = $nuevoUrl;
    }
     final public function getIncludePath(){
        return $this->directorios;
    }
    final public function loadClass($className){
        if (strlen($className) === 0) return false;
        $className = str_replace($this->separador, DIRECTORY_SEPARATOR, $className);
        $r = explode(DIRECTORY_SEPARATOR,$className);
        if(count($r)> 1){
            if(count($r)>2){
                $tmp = array_shift($r);
                $r = array($tmp,join(DIRECTORY_SEPARATOR,$r));
            }
            list($classNamespace,$class) = $r;
            foreach ($this->directorios as $dir) {
                if(is_file($dir .DIRECTORY_SEPARATOR . $classNamespace.DIRECTORY_SEPARATOR . 'config.php')){
                    require_once $dir .DIRECTORY_SEPARATOR . $classNamespace .DIRECTORY_SEPARATOR. 'config.php';
                }else{
                    die('Debes tener un config.php dentro de la libreria');
                }
                if (is_file($dir .DIRECTORY_SEPARATOR . $classNamespace .DIRECTORY_SEPARATOR.constant($classNamespace.'\\'.'CLASS_FOLDER'). DIRECTORY_SEPARATOR . $class . '.php')) {
                    require_once $dir .DIRECTORY_SEPARATOR . $classNamespace .DIRECTORY_SEPARATOR.constant($classNamespace.'\\'.'CLASS_FOLDER'). DIRECTORY_SEPARATOR . $class . '.php';
                    return true;
                }
            }
        }
        return false;
    }
}