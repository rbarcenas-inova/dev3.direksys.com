<?php
namespace Manga\Framework;
use Windwalker\Renderer\BladeRenderer;
use Manga\Tools\Config;
class View{
	private static $view = null;
	private $renderer;
	private $paths;
	private function __construct(){
		$this->paths = [BASE.Config::getApplication('view')];
		$this->renderer = new BladeRenderer($this->paths, ['cache_path' => BASE . Config::getApplication('view_cache')]);
	}
	public static function getView(){
		if(!isset(self::$view)){
			self::$view = new View();
		}
		return self::$view;
	}
	public static function json($content){
		try{
			return json_encode($content);
		}catch(Exception $e){
			return json_encode([]);
		}
	}
	public static function render($template, $params = []){
		$view = self::getView();		

		if(!isset($params['title']))
			$params['title'] = Config::getApplication('name');
		try{
			return $view->renderer->render($template, $params);
		}
		catch(Exception $e){
			return '';
		}
	}

}

