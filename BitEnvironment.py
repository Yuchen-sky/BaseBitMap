import cv2
import math
import numpy as np
from PIL import Image, ImageDraw

class BitEnvironment:
	def __init__(self):
		self.mapSize = 800
		self.unitNumOnLine = 100
		self.matrixShow = np.ones((self.unitNumOnLine, self.unitNumOnLine))
		self.Point = [math.floor(self.unitNumOnLine/2),math.floor(self.unitNumOnLine/2)]#the position of drone
		self.size = (self.mapSize, self.mapSize)
		self.direct = [[-1, -1],[-1, 0],[-1, 1],[0, -1],[0, 1],[1, -1],[1, 0],[1, 1]]
		self.target = [50, 30]#the position of target
		self.close = 3
		self.symbol = [0, 0.5, 0, 1]#0为无人机，1为障碍，2为目标，3为可行路径
		self.obes = []
		self.matrixShow[self.target[0]][self.target[1]] = self.symbol[2]
		self.value=[-1,-1,-1,-1,-1,-1,-1,-1]
		self.preDirect=[0,0]
		self.misCount=0
		self.getStateLine = 5


	def calculateValue(self,Point,i):
		dx = abs(Point[0] - self.target[0])
		dy = abs(Point[1] - self.target[1])
		self.value[i]=dx+dy

	def getstate(self,dx,dy):
		state = np.ones((self.getStateLine, self.getStateLine))
		i1 = -1
		j1 = -1
		for i in range(dx-math.floor(self.getStateLine/2),dx-math.floor(self.getStateLine/2)+1):
			j1 = -1
			i1 += 1
			if i >= 0 and i < self.unitNumOnLine:
				for j in range(dy - math.floor(self.getStateLine / 2), dy - math.floor(self.getStateLine / 2) + 1):
					j1 += 1
					if j >= 0 and j < self.unitNumOnLine:
						state[i1][j1] = self.matrixShow[i][j]



	def getNextStep(self):
		if self.misCount>=10:
			self.misCount = 0
			return self.direct.index(self.preDirect)
		for	i in range(len(self.direct)):
			PointTemp=np.add(self.direct[i], self.Point)
			self.calculateValue(PointTemp,i)
		sortValue=self.value.copy()
		sortValue.sort(reverse=True)

		while len(sortValue) != 0:
			minIndex=self.value.index(sortValue.pop())
			if self.judgeNextStepCollision(np.add(self.direct[minIndex], self.Point)):
				continue
			else:
				if all(self.direct[minIndex]==np.multiply(self.preDirect,-1))  :
					print("im stuck")
					self.misCount+=1
				return minIndex

		return 0




	def reset(self, target):
		self.matrixShow = np.ones((self.unitNumOnLine, self.unitNumOnLine))
		self.Point = [math.floor(self.unitNumOnLine/2), math.floor(self.unitNumOnLine/2)]
		self.setTarget(target)

	def setObstacle(self, obes):
		for obs in obes:
			if abs(obs[0] - self.Point[0]) <= 1 and abs(obs[1] - self.Point[1]) <= 1 or obs[0] == self.target[0] and obs[1] == self.target[1]:
				print("障碍与目标或无人机重合,故排除该障碍，坐标{} {}".format(obs[0], obs[1]))
			else:
				self.matrixShow[obs[0]][obs[1]] = self.symbol[1]
				self.obes.append(obs)

	def setTarget(self, target):
		self.matrixShow[self.target[0]][self.target[1]] = self.symbol[3]
		self.target = target
		self.matrixShow[self.target[0]][self.target[1]] = self.symbol[2]

	def setPoint(self, Point):
		self.matrixShow[self.Point[0]][self.Point[1]] = self.symbol[3]
		self.Point = Point
		self.matrixShow[self.Point[0]][self.Point[1]] = self.symbol[0]

	def getTarget(self):
		return self.target

	def getPoint(self):
		return self.Point

	def getObstacle(self):
		return self.obes

	def getMap(self):
		return self.matrixShow

	def step(self, direction):
		newPoint = np.add(self.direct[direction], self.Point)
		if newPoint[0] < 0 or newPoint[0] >= self.unitNumOnLine or newPoint[1] < 0 or newPoint[1] >= self.unitNumOnLine:
			print("已超出绝对地图范围")
			return self.Point, False
		self.setPoint(newPoint)
		return self.Point, True

	def judgeNextStepCollision(self,nextPoint):
		for direct in self.direct:
			testPoint = np.add(direct, nextPoint)
			if testPoint[0] < 0 or testPoint[0] >= self.unitNumOnLine or testPoint[1] < 0 or testPoint[1] >= self.unitNumOnLine:
				continue
			if self.matrixShow[testPoint[0]][testPoint[1]] == self.symbol[0]:
				continue
			if self.matrixShow[testPoint[0]][testPoint[1]] != self.symbol[3]:
				return True
		return False

	def judgeCollision(self):
		for direct in self.direct:
			testPoint = np.add(direct, self.Point)
			if testPoint[0] < 0 or testPoint[0] >= self.unitNumOnLine or testPoint[1] < 0 or testPoint[1] >= self.unitNumOnLine:
				continue
			if self.matrixShow[testPoint[0]][testPoint[1]] != self.symbol[3]:
				return True
		return False

	def done(self):
		if abs(self.Point[0] - self.target[0]) < self.close and abs(self.Point[1] - self.target[1]) < self.close:
			return True
		return False

	def distToTarget(self):
		dx = abs(self.Point[0] - self.target[0])
		dy = abs(self.Point[1] - self.target[1])
		realDirect = [self.target[0] - self.Point[0], self.target[1] - self.Point[1]]
		dist = math.sqrt(dx * dx + dy * dy)
		return dist, realDirect

	def showimage(self):
		img = Image.fromarray(self.matrixShow)
		li = img.resize(self.size)
		draw = ImageDraw.Draw(li)
		for i in range(0, self.mapSize, math.floor(self.mapSize/self.unitNumOnLine)):
			draw.line((0, i, self.mapSize, i), fill='#000000')
			draw.line((i, 0, i, self.mapSize), fill='#000000')
		data = li.getdata()
		data = np.matrix(data, dtype='float')
		new_data = np.reshape(data, self.size)
		cv2.imshow("view", new_data )
		cv2.waitKey(1) & 0xFF;

