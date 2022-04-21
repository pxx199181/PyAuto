#encoding: utf-8
import time
import sys
import pyautogui
import os

try:
	import pytesseract
	text_ocr_support = True
except Exception as e:
	text_ocr_support = False


def example_test():
	pyautogui.click(550, 190)
	for i in range(1, 500):
		time.sleep(1)		
		pyautogui.click(550, 285)
		time.sleep(1)						  # 为了方便看效果，让每次操作后停留1秒
		pyautogui.hotkey('ctrl','a')		   #按键ctrl+a		
		time.sleep(1)
		pyautogui.click(420, 90)		
		time.sleep(1)
		pyautogui.typewrite("{}-timeseries-20210328.xls".format(i))	   #输入文件名
		time.sleep(1)
		pyautogui.hotkey('enter')		   #按键enter		
		time.sleep(1)
		pyautogui.click(550, 190)
		time.sleep(1)
		pyautogui.hotkey('down')		   #按下方向键

import hashlib
def md5sum(data):
	a = hashlib.md5()
	a.update(data)
	return a.hexdigest()

class PyAuto(object):
	"""docstring for PyAuto"""
	def __init__(self, conf_file = None):
		self.conf_map = {}
		self.conf_map["pos"] 	= {}
		self.conf_map["color"] 	= {}
		self.conf_map["area"] 	= {}

		if conf_file is not None:
			self.load_config(conf_file)
		pass

	
	def __getattr__(self, key):
		#print "__getattr__", key
		if key in self.__dict__:
			return self.__dict__[key]

		if key in PyAuto.__dict__:
			return PyAuto.__dict__[key]

		#@if key in pyautogui.__dict__[key]:
		if True:
			def wrap(*args, **kwrds):
				func = getattr(pyautogui, key)
				#args = [pyautogui] + list(args)
				return func(*args, **kwrds)
			return wrap

	def clear_text(self, pos = None, duration = 1):
		pos = self.wrap_pos(pos)
		if pos is not None:
			pyautogui.moveTo(pos[0], pos[1], duration = duration, tween = pyautogui.easeInOutQuad)
		pyautogui.click()
		pyautogui.hotkey('ctrl', 'a')
		pyautogui.press('delete')

	def wrap_pos(self, pos):
		if type(pos) == str:
			pos = self.get_pos(pos)
		return pos

	def write_text(self, data, pos = None, clear = True, duration = 0, interval = 0):
		pos = self.wrap_pos(pos)
		if pos is not None:
			pyautogui.moveTo(pos[0], pos[1], duration = duration, tween = pyautogui.easeInOutQuad)
			pos = None
		if clear == True:
			self.clear_text(pos = pos, duration = duration)
		pyautogui.click()
		pyautogui.typewrite(data, interval = interval)

	def calc_sumall(self, pos, size = 10):
		pos = self.wrap_pos(pos)
		x = pos[0]
		y = pos[1]
		max_pos = pyautogui.size()
		x_b = x - size
		x_e = x + size
		y_b = y - size
		y_e = y + size
		if x_b < 0:
			x_b = 0
		if x_e >= max_pos[0]:
			x_e = max_pos[0]
		if y_b < 0:
			y_b = 0
		if y_e >= max_pos[1]:
			y_e = max_pos[1]
		x_pos  = x_b
		y_pos  = y_b
		width  = x_e - x_b
		height = y_e - y_b
		region = (x_pos, y_pos, width, height)
		im = pyautogui.screenshot(region = region)

		sumall = 0
		for i in range(x_b, x_e):
			for j in range(y_b, y_e):
				#print(region)
				#print(i, j)
				color = im.getpixel((i - x_b, j - y_b))
				sumall += (color[0]*255 +color[1])*255 + color[2]
		return sumall

	def areaMatchesColor(self, pos, sumall):
		t_sumall = self.calc_sumall(pos)
		return t_sumall == sumall

	def set_conf_map(self, ttype, name):
		x, y = pyautogui.position()
		if ttype == "pos":
			print(self.conf_map[ttype][name], [x, y])
			self.conf_map[ttype][name] = [x, y]
		elif ttype == "color":
			color = pyautogui.pixel(x, y)
			self.conf_map[ttype][name] = [[x, y], color]
		elif ttype == "area":
			sumall = self.calc_sumall((x, y))
			self.conf_map[ttype][name] = [[x, y], sumall]

	def set_conf_file(self, conf_file, ttype, name, x, y, value = None):
		if ttype == "pos":
			content = "%s. (%d, %d)"%(name, x, y)
		elif ttype == "color":
			content = "%s. (%d, %d) -> %s"%(name, x, y, repr(tuple(value)))
		elif ttype == "area":
			content = "%s. (%d, %d) -> %d"%(name, x, y, value)
		else:
			return
		print("record: " + content)
		self.appendfile(conf_file, "%s: "%(ttype) + content + "\n")


	def reconfig(self):

		conf_file = input("model config:").strip()
		if conf_file == "":
			conf_file = "pyauto.conf"
		if os.path.exists(conf_file) == False:
			print('not exists')
			return
		self.load_config(conf_file)
		ch = input("all or select, (1:all, 0:select. default->0)? ").strip()
		if ch == "1":
			for ttype in self.conf_map.keys():
				if len(self.conf_map[ttype].keys()) > 0:
					for name in self.conf_map[ttype].keys():
						value = input("%s.%s(%s): "%(ttype, name, repr(self.conf_map[ttype][name])))
						if value == "exit":
							break
						if value != "":
							continue
						self.set_conf_map(ttype, name)
						print("  change(%s.%s) -> (%s)"%(ttype, name, repr(self.conf_map[ttype][name])))
		else:
			while True:
				ttype = input("type: ").strip()
				if ttype == "exit":
					break
				old_data = repr(self.conf_map[ttype][name])
				self.set_conf_map(ttype, name)
				print("  change(%s.%s) %s -> (%s)"%(ttype, name, old_data, repr(self.conf_map[ttype][name])))

		new_conf = input("new conf: ").strip()
		if new_conf != "":
			conf_file = new_conf
		self.writefile(conf_file, "")

		for ttype in self.conf_map.keys():
			if len(self.conf_map[ttype].keys()) > 0:
				for name in self.conf_map[ttype].keys():
					items = self.conf_map[ttype][name]
					print(ttype, name, items)
					if ttype != "pos":
						[x, y], value = items
					else:
						[x, y] = items
						value = None
					self.set_conf_file(conf_file, ttype, name, x, y, value)

	def gen_config(self):
		conf_file = ""
		while True:
			print("menu:")
			print("1. scan")
			print("2. pick pos")
			print("3. pick color")
			print("4. pick area")
			print("5. reconfig")
			print("99. return")
			choice = input("choice: ").strip()
			if choice == "":
				break

			choice = int(choice)
			if choice not in [1, 5, 6] and conf_file == "":
				conf_file = input("config file:").strip()
				if conf_file == "":
					conf_file = "pyauto.conf"
				if os.path.exists(conf_file):
					ch = input("conf exists, (1:overwrite, 0:append. default->0)? ").strip()
					if ch == "1":
						self.writefile(conf_file, "")

			if choice == 1:
				last_len = 0
				while True:
					x, y = pyautogui.position()
					color = pyautogui.pixel(x, y)
					sumall = self.calc_sumall((x, y))
					content = "\r(%d,%d) -> color: %s, area: %d"%(x, y, repr(color), sumall)
					sys.stdout.write(content.ljust(last_len, " "))
					last_len = len(content)

			elif choice == 2:
				while True:
					name = input("name:")
					if name == "exit":
						break
					x, y = pyautogui.position()
					self.set_conf_file(conf_file, "pos", name, x, y)

			elif choice == 3:
				while True:
					name = input("name:")
					if name == "exit":
						break
					x, y = pyautogui.position()
					color = pyautogui.pixel(x, y)
					self.set_conf_file(conf_file, "color", name, x, y, color)

			elif choice == 4:
				while True:
					name = input("name:")
					if name == "exit":
						break
					x, y = pyautogui.position()
					sumall = self.calc_sumall((x, y))
					self.set_conf_file(conf_file, "area", name, x, y, sumall)

			elif choice == 5:
				self.reconfig()

			elif choice == 99:
				break
			else:
				print('error')

	def get_pos(self, name):
		if name in self.conf_map["pos"].keys():
			return self.conf_map["pos"][name]
		elif name in self.conf_map["color"].keys():
			return self.conf_map["color"][name][0]
		elif name in self.conf_map["area"].keys():
			return self.conf_map["area"][name][0]
		else:
			return None

	def get_color(self, pos):
		if type(pos) == str:
			return self.conf_map["color"][pos][1]
		else:
			return self.pixel(pos[0], pos[1])

	def get_area(self, pos, size = 10):
		if type(pos) == str:
			return self.conf_map["area"][pos][1]
		else:
			return self.calc_sumall(pos, size = size)

	def pixelMatchesColorEx(self, pos, name = None):
		if type(pos) == str:
			if name is None:
				name = pos
			pos = self.get_pos(pos)
		if type(name) == str:
			color = self.get_color(name)
		else:
			color = name
		#print(pos[0], pos[1], color, self.pixel(pos))
		return self.pixelMatchesColor(pos[0], pos[1], color)

	def areaMatchesColorEx(self, pos, name = None, size = 10):
		if type(pos) == str:
			if name is None:
				name = pos
			pos = self.get_pos(pos)
		if type(name) == str:
			sumall = self.get_area(name, size = size)
		else:
			sumall = name
		return self.calc_sumall(pos, size = size) == self.get_area(name, size = size)

	def load_config(self, conf = "pyauto.conf"):
		content = self.readfile(conf).strip()
		self.conf_map = {}
		self.conf_map['pos'] = {}
		self.conf_map['color'] = {}
		self.conf_map['area'] = {}
		for line in content.split("\n"):
			line = line.strip()
			if line.startswith("pos: "):
				line = line[5:].strip()
				items = line.split(". ")
				name = items[0].strip()
				line = items[1].strip()
				items = line.split(" -> ")
				items[0] = items[0].strip()[1:-1]
				x, y = items[0].split(", ")
				x, y = int(x), int(y)
				self.conf_map['pos'][name] = [x, y]

			elif line.startswith("color: "):
				line = line[7:].strip()
				items = line.split(". ")
				name = items[0].strip()
				line = items[1].strip()
				items = line.split(" -> ")
				items[0] = items[0].strip()[1:-1]
				x, y = items[0].split(", ")
				x, y = int(x), int(y)
				color = items[1].strip()[1:-1]
				color = tuple([int(c.strip()) for c in color.split(",")])
				self.conf_map['color'][name] = [[x, y], color]

			elif line.startswith("area: "):
				line = line[6:].strip()
				items = line.split(". ")
				name = items[0].strip()
				line = items[1].strip()
				items = line.split(" -> ")
				items[0] = items[0].strip()[1:-1]
				x, y = items[0].split(", ")
				x, y = int(x), int(y)
				sumall = int(items[1].strip())
				self.conf_map['area'][name] = [[x, y], sumall]
		return self.conf_map

	def readfile(self, filename, md = "r+", encoding = "utf-8"):
		with open(filename, md, encoding = encoding) as fd:
			return fd.read()

	def writefile(self, filename, data, md = "w+", encoding = "utf-8"):
		with open(filename, md, encoding = encoding) as fd:
			return fd.write(data)

	def get_text(self, b_pos, e_pos, lang = "eng", img_path = None):
		im = self.get_pic(b_pos, e_pos)
		if img_path is not None:
			im.save(img_path)
		
		if text_ocr_support == False:
			print("ocr not support")
			return None

		text = pytesseract.image_to_string(im, lang=lang)
		#print(text)
		return text.strip()	

	def wrap_args(self, args):
		if len(args) > 0:
			if type(args[0]) == str:
				pos = self.get_pos(args[0])
				#print(args)
				#print(pos)
				#print([pos[0], pos[1]] + list(args[1:]))
				return [pos[0], pos[1]] + list(args[1:])
			elif type(args[0]) in [list, tuple]:
				pos = args[0]
				return [pos[0], pos[1]] + list(args[1:])
		return args

	def moveTo(self, *args, **kwrds):
		args = self.wrap_args(args)
		return pyautogui.moveTo(*args, **kwrds)

	def click(self, *args, **kwrds):
		args = self.wrap_args(args)
		return pyautogui.click(*args, **kwrds)

	def pixel(self, *args, **kwrds):
		args = self.wrap_args(args)
		return pyautogui.pixel(*args, **kwrds)

	def pixelMatchesColor(self, *args, **kwrds):
		args = self.wrap_args(args)
		return pyautogui.pixelMatchesColor(*args, **kwrds)

	def appendfile(self, filename, data, md = "a+", encoding = "utf-8"):
		self.writefile(filename, data, md, encoding)

	def get_pic(self, b_pos = None, e_pos = None):
		b_pos = self.wrap_pos(b_pos)
		e_pos = self.wrap_pos(e_pos)
		if b_pos is None:
			pos = (0, 0)
		if e_pos is None:
			size = pyautogui.size()
			e_pos = (size[0], size[1])
		x_pos  = b_pos[0]
		y_pos  = b_pos[1]
		width  = e_pos[0] - b_pos[0]
		height = e_pos[1] - b_pos[1]
		region = (x_pos, y_pos, width, height)
		#print(region)
		im = pyautogui.screenshot(region = region)
		return im

	def save_pic(self, b_pos = None, e_pos = None, img_path = "pic.png"):
		im = self.get_pic(b_pos, e_pos)
		#im = pyautogui.screenshot()
		im.save(img_path)

def test():
	pyauto = PyAuto()
	pyauto.gen_config()
	conf_map = pyauto.load_config("test.conf")
	print(conf_map)
	#input(":")
	username = "tesd@qq.com"
	password = "qwe"

	flush_pos = pyauto.get_pos("flush")

	pic_pos1 = pyauto.get_pos("pic_b")
	pic_pos2 = pyauto.get_pos("pic_e")

	pyauto.moveTo("flush")
	pyauto.click()
	time.sleep(1)

	pyauto.moveTo("ready")
	while True:
		if pyauto.areaMatchesColorEx("ready") == True:
			print("ready")
			break
		print("in flush")
		time.sleep(1)

	pyauto.moveTo(flush_pos[0], flush_pos[1] + 0x200)
	time.sleep(1)

	pyauto.write_text(username, "user")#pyauto.get_pos("user"))
	pyauto.write_text(password, "pass")#pyauto.get_pos("pass"))

	#key_pos = pyauto.get_pos("enter")

	pyauto.moveTo("enter", duration=2, tween=pyautogui.easeOutQuad)
	pyauto.click()

	time.sleep(2)
	while True:
		if pyauto.pixelMatchesColorEx("warn") == True:
			#text = pyauto.get_text("warn", "warn_e")#, lang = 'chi_sim', img_path = "chk.png")
			#print("text:", text)
			break
		print("check fail, continue")
		time.sleep(1)

	if pyauto.pixelMatchesColorEx("error", "error") == True:
		print("get res ok")
	else:
		print("401 find")

	pyauto.save_pic(pic_pos1, pic_pos2, img_path = "%s.png"%username)

if __name__ == "__main__":
	test()