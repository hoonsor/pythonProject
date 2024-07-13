import pyautogui
import time

# 模拟按下 Caps Lock 键
pyautogui.keyDown('capslock')
# 模拟按下 Z 键
pyautogui.keyDown('z')

# 等待一小段时间以确保键被同时按下
time.sleep(0.1)

# 模拟释放 Z 键
pyautogui.keyUp('z')
# 模拟释放 Caps Lock 键
pyautogui.keyUp('capslock')
