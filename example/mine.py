from PyAuto import PyAuto
import time

def get_value(pyauto, x, y):
	x_p, y_p = get_pos(pyauto, x, y)
	color_list = pyauto.getAreaColorList((x_p, y_p), size = 10)
	#print(x_p, y_p, color_list)
	#input(":")
	if pyauto.get_color("bad") in color_list:
		return 99
	elif pyauto.get_color("one") in color_list:
		return 1
	elif pyauto.get_color("two") in color_list:
		return 2
	elif pyauto.get_color("three") in color_list:
		return 3
	elif pyauto.get_color("four") in color_list:
		return 4
	elif pyauto.get_color("five") in color_list:
		return 5
	elif pyauto.get_color("six") in color_list:
		return 6
	else:
		return 0
	return -1

def get_all_numbers(pyauto, x, y, queue, check_list, box_list):
	x_b, x_e = pyauto.gen_bound(x, 1, 0, 15)
	y_b, y_e = pyauto.gen_bound(y, 1, 0, 15)
	#print("x_b, x_e:", x_b, x_e)
	#print("y_b, y_e:", y_b, y_e)
	for y in range(y_b, y_e + 1):
		for x in range(x_b, x_e + 1):
			#print(x, y)
			if (x, y) in check_list:
				continue
			elif box_list[y][x] == -1:
				value = get_value(pyauto, x, y)
				print("   (%d, %d) -> %d"%(x, y, value))
				box_list[y][x] = value
				check_list.append((x, y))
				if value == 0:
					queue.append((x, y))

MINE_SIZE = 24
MINE_SIZE = 30
def get_pos(pyauto, x, y):
	pos00_p = pyauto.get_pos("pos00")
	x_p = pos00_p[0] + x*MINE_SIZE
	y_p = pos00_p[1] + y*MINE_SIZE
	return x_p, y_p

def check_pos(pyauto, x, y):
	x_p, y_p = get_pos(pyauto, x, y)
	pyauto.moveTo(x_p, y_p)

def check(pyauto, x, y, box_list):
	x_p, y_p = get_pos(pyauto, x, y)
	pyauto.moveTo(x_p, y_p, duration = 0, tween = pyauto.easeInOutQuad)
	pyauto.click(x_p, y_p)
	time.sleep(0.3)
	pyauto.click(x_p, y_p)
	#time.sleep(1)

	queue = [(x, y)]
	check_list = []
	while len(queue) > 0:
		(x, y) = queue[0]
		queue = queue[1:]
		value = get_value(pyauto, x, y)
		print("   (%d, %d) -> %d"%(x, y, value))
		if value == 99:
			return False
		box_list[y][x] = value
		check_list.append((x, y))
		if value == 0:
			get_all_numbers(pyauto, x, y, queue, check_list, box_list)
	return True

def add_qz(pyauto, box_list, x, y, val_list):
	x_b, x_e = pyauto.gen_bound(x, 1, 0, 15)
	y_b, y_e = pyauto.gen_bound(y, 1, 0, 15)

	value = box_list[y][x]
	count = 0
	sure_count = 0
	for yi in range(y_b, y_e + 1):
		for xi in range(x_b, x_e + 1):
			if xi == x and yi == y:
				continue
			if box_list[yi][xi] == -1:
				count += 1
			elif box_list[yi][xi] == 99:
				sure_count += 1

	if count != 0:
		qz = (value - sure_count + 0.0) / (count)
	else:
		qz = 0
	for yi in range(y_b, y_e + 1):
		for xi in range(x_b, x_e + 1):
			if xi == x and yi == y:
				continue
			if box_list[yi][xi] == -1:
				#if val_list[yi][xi] == -1:
				#	val_list[yi][xi] = 100
				if val_list[yi][xi] == 99:
					continue
				else:
					print("add_qz:", xi, yi, value, sure_count, count, qz)
					if value == sure_count:
						val_list[yi][xi] = 0
					elif val_list[yi][xi] == -1:
						val_list[yi][xi] = qz
					elif (val_list[yi][xi] < qz and val_list[yi][xi] != 0):
						val_list[yi][xi] = qz
			elif val_list[yi][yi] != 99:
				val_list[yi][xi] = 100



def pick_pos(pyauto, box_list, size = 16):
	while True:
		val_list = []
		for i in range(16):
			row = []
			for j in range(16):
				if box_list[i][j] != -1:
					if box_list[i][j] == 99:
						row.append(1)
					else:
						row.append(100)
				else:
					row.append(-1)
			val_list.append(row)

		for y in range(size):
			for x in range(size):
				if box_list[y][x] == -1:
					continue
				elif box_list[y][x] == 99:
					continue
				add_qz(pyauto, box_list, x, y, val_list)

		min_val = 99
		min_x = -1
		min_y = -1
		normal_list = []
		min_list = []

		mine_list = []
		for y in range(size):
			print(val_list[y])
			for x in range(size):
				if box_list[y][x] == -1:
					if val_list[y][x] != -1:
						if val_list[y][x] >= 1 and val_list[y][x] < 20:
							mine_list.append([x, y])
							#pyauto.rightclick()
							continue
						if int(val_list[y][x]*1000) < int(min_val*1000):
							min_list = []
							min_list.append([x, y])
							min_val = val_list[y][x]
						elif int(val_list[y][x]*1000) == int(min_val*1000):
							min_list.append([x, y])
					else:
						normal_list.append([x, y])

		if len(mine_list) > 0:
			print("mine_list:")
			print(mine_list)
			for items in mine_list:
				x, y = items
				pyauto.moveTo(get_pos(pyauto, x, y))
				pyauto.click(button='right', clicks=1)
				time.sleep(0.5)
				box_list[y][x] = 99
				print("%d, %d -> mine"%(x, y))
			#input(":")
		else:
			break

	if len(min_list) == 0 and len(normal_list) == 0:
		return "pass", None, None

	print("min_val:", min_val)
	print("min_list:")
	print(min_list)
	print("normal_list:")
	print(normal_list)
	if min_val < 0.2 or len(normal_list) == 0:
		size = len(min_list)
		idx = random.randint(0, size - 1)
		return "ok", min_list[idx][0], min_list[idx][1]
	else:
		size = len(normal_list)
		idx = random.randint(0, size - 1)
		return "ok", normal_list[idx][0], normal_list[idx][1]

import random
def mine_sweep():

	#url: https://minesweeper.online/cn/game
	pyauto = PyAuto()
	pyauto.gen_config()
	conf_map = pyauto.load_config("mine.conf")
	pos00_p = pyauto.get_pos("pos00")
	count = 16

	#val_list  = [pyauto.get_color("zero"), pyauto.get_color("one")]
	#val_list += [pyauto.get_color("two"), pyauto.get_color("three")]

	idx = 0
	while True:
		#input("begin:")
		idx += 1
		print("round %d"%idx)

		box_list = []
		for i in range(16):
			row = []
			for j in range(16):
				row.append(-1)
			box_list.append(row)

		pyauto.moveTo("level2")
		pyauto.click()
		time.sleep(1)

		"""
		for i in range(16):
			for j in range(16):
				x, y = j, i
				check_pos(pyauto, x, y)
				input("%d, %d"%(x, y))
		"""

		x = random.randint(0, 15)
		y = random.randint(0, 15)
		while True:

			if check(pyauto, x, y, box_list) == False:
				print("fail")
				break
			for row in box_list:
				print(row)

			print("pic map")
			sign, x, y = pick_pos(pyauto, box_list)
			if sign == "pass":
				#input("passed")
				input("passed")
				break
			else:
				pass
			print(sign, x, y)
			#input(":")
			pass

if __name__ == "__main__":
	mine_sweep()