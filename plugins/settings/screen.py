import sys
import os
import subprocess
# import pygame
from time import strftime, localtime, time, sleep
from change_time import change_time
from global_variables import COLORS, piscreenevents, ICONS, SWIPE
from displayscreen import PiInfoScreen
from database import RACK_DB
from button import button
sys.dont_write_bytecode = True

# For more information on the variables and functions in this file view
# displayscreen.py in the root folder of this project


class myScreen(PiInfoScreen):

    refreshtime = 1
    displaytime = 5
    pluginname = "File Accn"
    plugininfo = "place to file things. "
    accn = ''

    def __init__(self, *args, **kwargs):
        PiInfoScreen.__init__(self, args[0], kwargs)
        self.vkey_surface = pygame.display.get_surface()
        self.vkey = VirtualKeyboard(self.vkey_surface, self.color_name, False)

        self.dirty = True

        self.default_message = "Please use caution\nEnter: 'F1' to optimize database"

        self.screen.fill(COLORS['CLOUD'])
        self.hint_text.update_string(self.default_message)

        # self.title.update()


        self.shell_commands = {
            'backup': 'cp racks.sqlite racks.sqlite.bak',
            'update': 'git pull',
            'restart': "sudo reboot -n"
        }
        self.commands = {
            'F1': self.clean_database,
            'F2': self.database_size,
            'F3': self.toggle_fps,
            'F8': self.apply_patch,
            'F22': self.quit
        }
        for thing in self.screen_objects:
            thing.update()

    def quit(self):
        pygame.quit()

    def toggle_fps(self):
        pygame.event.post(self.piscreenevents['toggle_fps'])

    def apply_patch(self):
        # message = "Starting Update..."
        # self.update_message(message)
        message ="-Backing up database"
        # sleep(1)
        self.update_message(message)
        subprocess.call(self.shell_commands['backup'], shell=True)
        # sleep(1)
        message +="\n -Downloading patch"
        self.update_message(message)
        # subprocess.call(self.shell_commands['update'], shell=True)
        # sleep(1)
        message += "\n -Downloading modules"
        self.update_message(message)
        subprocess.call('pip install -r requirements.txt', shell=True)
        self.update_message('Update Complete\nRestarting now')
        sleep(2)
        subprocess.call(self.shell_commands['restart'], shell=True)

    def update_message(self,msg):
        self.hint_text.update_string(msg)
        self.screen.blit(self.hint_text.screen, self.hint_text.rect)
        self.hint_text.dirty = True

    def database_size(self):
        text = 'DATABASE SIZE\n'
        tmp = RACK_DB._list_size()
        for key in tmp:
            text += key + ': ' + str(tmp[key]) + '\n'
        self.update_message(text)

    def clean_database(self):
        self.update_message("PURGING DATABASE\nThis might take some time, please don't discconect power.")
        RACK_DB.clean()
        self.hint_text.update_string("Finished Optomizing\nIt's now safe to leave this screen")

    def event_handler(self, event):
        if event.type == SWIPE and event.value == 'up':
            self.dirty = True
            tmp = self.vkey.run('')
            self.run_command(tmp)
            return True
        return False

    def run_command(self, command):
        if command in self.shell_commands:
            subprocess.call(self.shell_commands[command], shell=True)
        if command in self.commands:
            self.commands[command]()

    def showScreen(self):
            self.refresh_objects()
            
            return self.screen

    def exit_function(self):
        # self.screen.fill(COLORS['CLOUD'])
        self.dirty = True
        self.hint_text.update_string(self.default_message)
