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
            elif command=='volume_up':
                self.keyboard.tap(Key.media_volume_up)
              
            elif command=='volume_down':
                 self.keyboard.tap(Key.media_volume_down)