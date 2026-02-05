from pynput.keyboard import Controller, Key
from config import GESTURE_COMMANDS, VLC_KEYS

class MediaController:
    def __init__(self):
        self.keyboard = Controller()
    
    def execute_command(self, gesture):
        if gesture in GESTURE_COMMANDS:
            command = GESTURE_COMMANDS[gesture]
            key = VLC_KEYS[command]

            if key == 'space':
                key = Key.space

                self.keyboard.press(key)
                self.keyboard.release(key)

            elif key=='f':
                    self.keyboard.press('f')
                    self.keyboard.release('f')
            elif key=='ctrl+down':
                with self.keyboard.pressed(Key.ctrl):
                    self.keyboard.press(Key.down)
                    self.keyboard.release(Key.down)
            elif key== 'ctrl+up':
                with self.keyboard.pressed(Key.ctrl):
                    self.keyboard.press(Key.up)
                    self.keyboard.release(Key.up)
            elif key=='m':
                self.keyboard.press('m')
                self.keyboard.release('m')
            


            