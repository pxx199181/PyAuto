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
		if pos is not None:
			pyautogui.moveTo(pos[0], pos[1], duration = duration, tween = pyautogui.easeInOutQuad)
		pyautogui.click()
		pyautogui.hotkey('ctrl', 'a')
		pyautogui.press('delete')

	def write_text(self, data, pos = None, clear = True, duration = 1, interval = 0.1):
		if pos is not None:
			pyautogui.moveTo(pos[0], pos[1], duration = duration, tween = pyautogui.easeInOutQuad)
			pos = None
		if clear == True:
			self.clear_text(pos = pos, duration = duration)
		pyautogui.click()
		pyautogui.typewrite(data, interval = interval)

	def calc_sumall(self, pos, size = 10):
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

	def gen_config(self):
		conf_file = ""
		while True:
			print("menu:")
			print("1. scan")
			print("2. pick pos")
			print("3. pick color")
			print("4. pick area")
			print("5. return")
			choice = input("choice: ").strip()
			if choice == "":
				break

			choice = int(choice)
			if choice not in [1, 5] and conf_file == "":
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
					content = "%s. (%d, %d)"%(name, x, y)
					print("record: " + content)
					self.appendfile(conf_file, "pos: " + content + "\n")

			elif choice == 3:
				while True:
					name = input("name:")
					if name == "exit":
						break
					x, y = pyautogui.position()
					color = pyautogui.pixel(x, y)
					content = "%s. (%d, %d) -> %s"%(name, x, y, repr(color))
					print("record: " + content)
					self.appendfile(conf_file, "color: " + content + "\n")

			elif choice == 4:
				while True:
					name = input("name:")
					if name == "exit":
						break
					x, y = pyautogui.position()
					color = pyautogui.pixel(x, y)
					sumall = self.calc_sumall((x, y))
					content = "%s. (%d, %d) -> %d"%(name, x, y, sumall)
					print("record: " + content)
					self.appendfile(conf_file, "area: " + content + "\n")

			elif choice == 5:
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
			return self.calc_sumall(pos[0], pos[1], size = size)

	def pixelMatchesColorEx(self, pos, name):
		if type(pos) == str:
			pos = self.get_pos(pos)
		return self.pixelMatchesColor(pos[0], pos[1], self.get_color(name))

	def areaMatchesColorEx(self, pos, name, size = 10):
		if type(pos) == str:
			pos = self.get_pos(pos)
		return self.calc_sumall(pos[0], pos[1], size = size) == self.get_area(name, size = size)

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
		b_pos = self.get_pos(b_pos)
		e_pos = self.get_pos(e_pos)
		im = self.get_pic(b_pos, e_pos)
		if img_path is not None:
			im.save(img_path)
		
		if text_ocr_support == False:
			print("ocr not support")
			return None

		text = pytesseract.image_to_string(im, lang=lang)
		#print(text)
		return text.strip()

	def appendfile(self, filename, data, md = "a+", encoding = "utf-8"):
		self.writefile(filename, data, md, encoding)

	def get_pic(self, b_pos = None, e_pos = None):
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
	input(":")
	username = "userqqq@qq.com"
	password = "pass111"

	flush_pos = pyauto.get_pos("flush")

	pic_pos1 = pyauto.get_pos("pic_b")
	pic_pos2 = pyauto.get_pos("pic_e")

	pyauto.moveTo(flush_pos[0], flush_pos[1])
	pyauto.click()
	time.sleep(1)
	while True:
		if pyauto.pixelMatchesColorEx("ready", "ready") == True:
			print("ready")
			break
		print("in flush")
		time.sleep(1)

	pyauto.moveTo(flush_pos[0], flush_pos[1] + 0x200)
	time.sleep(1)

	pyauto.write_text(username, pyauto.get_pos("user"))
	pyauto.write_text(password, pyauto.get_pos("pass"))

	key_pos = pyauto.get_pos("enter")

	pyauto.moveTo(key_pos[0], key_pos[1], duration=2, tween=pyautogui.easeOutQuad)
	pyauto.click()

	time.sleep(2)
	while True:
		if pyauto.pixelMatchesColorEx("warn", "warn") == True:
			text = pyauto.get_text("warn", "warn_e")#, lang = 'chi_sim', img_path = "chk.png")
			print("text:", text)
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