from PyAuto import PyAuto

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