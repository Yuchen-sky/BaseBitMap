#coding:utf-8
import os
from shenZhenA.BitEnvironment import BitEnvironment
from Persistence import Persistence
import numpy as np
import tensorflow as tf
import time
import random

print(random.randint(0, 9))
def main():
	persistence = Persistence()
	env = BitEnvironment()
	direct = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
	terminal, step_count, e, success, = False, 0, 0, 0
	obes = []
	for i in range(0,80):
		obes.append([random.randint(0, 99),random.randint(0, 99)])
	env.setObstacle(obes)

	while True:
		#direction = random.randint(0, 7)
		# 包含两个，01方向减法，23上次速度
		direction=env.getNextStep()
		Position, move = env.step(direction)
		env.preDirect=direct[direction]
		print("行动否：{} 具体行动方向: {} 当前位置 {}".format(move, direct[direction], Position))
		dist, realDirect = env.distToTarget()
		print("距离目标: {} 目标方位: {}".format(dist, realDirect))
		if env.judgeCollision() or env.done():
			terminal = True
		step_count += 1
		print("阶段 {} 完成, 总成功: {} 当轮步数: {}".format(e, success, step_count))
		env.showimage()
		if terminal:
			if env.done():
				success += 1
				print("-----------------------------success----------------------------------")
			elif env.judgeCollision():
				print("-----------------------------发生碰撞----------------------------------")
			step_count = 0
			e += 1
			infoShow = "time {}, episode {} finish, total success: {} step: {}".format(
				time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), e, success, step_count)
			persistence.saveTerminalRecord("GoInBitMap", infoShow)

			env.reset([random.randint(0, 99),random.randint(0, 99)])
			env.setObstacle(obes)
			terminal = False
		time.sleep(0.2)


if __name__ == "__main__":
	main()