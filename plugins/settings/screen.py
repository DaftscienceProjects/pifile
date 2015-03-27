import sys
import os
import subprocess
# import pygame
from time import strftime, localtime, time, sleep
from change_time import change_time
from global_variables import COLORS, piscreenevents, ICONS, SWIPE_UP, SWIPE_DOWN
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

        self.default_message = "Please use caution\nEnter: 'F1' to optimize database"
        self.setting_visible = False
        self.clock_dirty = False
        self.minus = ICONS.unicode('down-open')
        self.plus = ICONS.unicode('up-open')
        self.surface.fill(COLORS['CLOUD'])
        self.hint_text.string = self.default_message
        self.title.update()



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
        self.hint_text.string = msg
        self.hint_surface.blit(self.hint_text.update(), (0, 0))
        self.clock.text = ' '
        self.clock.update()
        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()

    def database_size(self):
        text = 'DATABASE SIZE\n'
        tmp = RACK_DB._list_size()
        for key in tmp:
            text += key + ': ' + str(tmp[key]) + '\n'
        self.update_message(text)

    def clean_database(self):
        self.update_message("PURGING DATABASE\nThis might take some time, please don't discconect power.")
        RACK_DB.clean()
        self.hint_text.string = "Finished Optomizing\nIt's now safe to leave this screen"

    def event_handler(self, event):
        if event.type == SWIPE_UP:
            self.dirty = True
            tmp = self.vkey.run('')
            self.run_command(tmp)
            return

    def run_command(self, command):
        if command in self.shell_commands:
            subprocess.call(self.shell_commands[command], shell=True)
        if command in self.commands:
            # print "run command"
            self.commands[command]()

    def show_settings(self):
        self.hint_surface.fill(COLORS['CLOUD'])
        self.clock.text = strftime("%H:%M", localtime(time()))
        self.clock.update()
        for b in self.buttons:
            b.update()
        self.screen.blit(self.surface, (0, 0))

    def showScreen(self):
        if self.setting_visible:
            self.settings_screen = self.show_settings()
            return self.screen
        else:
            self.hint_surface.blit(self.hint_text.update(), (0, 0))
            self.clock.text = strftime("%H:%M", localtime(time()))
            self.clock.update()
            self.screen.blit(self.surface, (0, 0))
            return self.screen

    def exit_function(self):
        self.hint_text.string = self.default_message
