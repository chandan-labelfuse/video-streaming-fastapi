from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Optional


@dataclass
class CamObject(ABC):

	cam_id: int
	cam_address: str

	@abstractmethod
	def initialize(self):
		pass
	
	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def update(self):
		pass

	@abstractmethod
	def read(self):
		pass
	
	@abstractmethod
	def stop(self):
		pass


@dataclass
class DetectorObject(ABC):

	@abstractmethod
	def initialize(self):
		pass

	@abstractmethod
	def preprocess(self):
		pass

	@abstractmethod
	def infer(self):
		pass

	@abstractmethod
	def postprocess(self):
		pass


class ActionObject(ABC):

	@abstractmethod
	def initialize(self):
		pass


class DrawObject(ABC):

	@abstractmethod
	def draw(self):
		pass



@dataclass
class ControllerObject(ABC):

	camComp: CamObject
	detectComp: Optional[DetectorObject] = None
	actionComp: Optional[ActionObject] = None
	drawComp: Optional[DrawObject] = None

	@abstractmethod
	def render(self):
		pass

	def addDetect(self, detect: DetectorObject):
		self.detectComp = detect

	def deleteDetect(self):
		del self.detectComp
	
	def addAction(self, action: ActionObject):
		self.actionComp = action
	
	def deleteAction(self):
		del self.actionComp
	
	def addDraw(self, draw: DrawObject):
		self.drawComp = draw

	def deleteDraw(self):
		del self.drawComp