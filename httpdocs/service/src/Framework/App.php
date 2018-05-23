<?php
namespace Service\Framework;
use Symfony\Component\HttpFoundation\Request;
use	Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpKernel;
use	Symfony\Component\Routing;
use	Symfony\Component\Routing\RequestContext;
use	Symfony\Component\Routing\Matcher\UrlMatcher;
class App{
	private $routes;
	private $request;
	private $context;
	private $path;
	private $response;
	private $controllerResolver;
	private $argumentResolver;
	public function __construct(Routing\RouteCollection $routes){
		$this->request = Request::createFromGlobals();
		$this->routes = $routes;
		$this->context = new RequestContext();		
		$this->context->fromRequest($this->request);		
		$this->response = new Response();
		$this->path = $this->request->getPathInfo();
		$this->controllerResolver = new HttpKernel\Controller\ControllerResolver();
		$this->argumentResolver = new HttpKernel\Controller\ArgumentResolver();
	}
	public function init(){
		$matcher = new UrlMatcher($this->routes, $this->context);
		$json = 0;
		try{
			// if(!in_array($this->request->getMethod() , explode(',', Config::getApplication('method_avilable'))))
			// 	throw new \Exception('Request '. $this->request->getMethod(). ' is Invalid!');
			
			$this->request->attributes->add($matcher->match($this->path));

			if(is_callable($this->request->attributes->get('_controller')) && gettype($this->request->attributes->get('_controller')) == 'object'){
		    	$html = call_user_func($this->request->attributes->get('_controller'), $this->request);
		    	$this->response->setContent($html);
			}else{
				$controller = $this->controllerResolver->getController($this->request);
				$arguments = $this->argumentResolver->getArguments($this->request, $controller);
				$res = call_user_func_array($controller, $arguments);

		    	if($res instanceof Response){
		    		$this->response = $res;
		    	}elseif(is_string($res)){
		    		$this->response->setContent($res);
		    	}else{
		    		$json = 1;
		    		$this->response->setContent(json_encode($res));
		    	}
			}
			$this->response->setStatusCode(200);
			if($json == 0){
				$this->response->headers->set('Content-Type', 'text/html');
			}else{
				$this->response->headers->set('Content-Type', 'application/json');
			}

		} catch (Routing\Exception\ResourceNotFoundException $e) {
		    $this->response = new Response('Not Found', 404);
		} catch (\Exception $e) {
		    $this->response = new Response($e->getMessage(), 500);
		}

		$this->response->send();
	}
	public function getPath(){
		return $this->path;
	}
}