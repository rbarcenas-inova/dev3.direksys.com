<?php
class ExecutionTime{
	private $startTime;
	private $endTime;
	public function __construct(){
		$this->startTime = microtime(true);
		$this->endTime = 0;
	}
	public function start(){
		$this->startTime = microtime(true);
		return $this;
	}
	public function end(){
		$this->endTime = microtime(true);
		return $this;
	}
	public function reset(){
		$this->startTime = 0;
		$this->endTime = 0;
		return $this;
	}
	public function __toString(){
		if($this->endTime == 0){
			$this->end();
		}
		return $this->endTime - $this->startTime . ' s.';
	}
}