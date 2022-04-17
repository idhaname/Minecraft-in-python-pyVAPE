import json
import os
import re
import shutil
from string import punctuation
import sys
import time
from tkinter import Listbox, Tk, Toplevel, messagebox
import tkinter.ttk as ttk
import traceback

from minecraft.utils.utils import *
import minecraft.utils.tests
from minecraft.utils.opengl import setup_opengl
from minecraft.game import *
from minecraft.saves import load_window
from minecraft.source import saves_path, player, settings
log_info('Start game')

import pyglet
from pyglet.gl import gl_info

def is_game_restore(name):
    """
    判断一个目录是否为游戏存档

    :param: name 要检查的游戏目录
    """
    if os.path.isdir(os.path.join(saves_path, name)):
        if not os.path.isfile(os.path.join(saves_path, name, 'level.json')):
            return False
        if not os.path.isfile(os.path.join(saves_path, name, 'world.json')):
            return False
        if not os.path.isdir(os.path.join(saves_path, name, 'players')):
            return False
        return True
    else:
        return False


class StartScreen(Tk):

    def __init__(self):
        try:
            Tk.__init__(self)
        except:
            log_err('no display, exit')
            exit(1)
        self.title(resource_pack.get_translation('start.title') % VERSION['str'])
        if settings['use-theme'] != 'ttk' and not sys.platform.startswith('win'):
            theme_path = os.path.dirname(os.path.abspath(__file__)) + '/theme/' + settings['use-theme']
            self.tk.eval('lappend auto_path {%s}' % theme_path)
            ttk.Style().theme_use(settings['use-theme'])
        # 小部件
        self.new_button = ttk.Button(self, text=resource_pack.get_translation('start.new'), command=self.new)
        self.start_button = ttk.Button(self, text=resource_pack.get_translation('start.start'), command=self.start_game)
        self.exit_button = ttk.Button(self, text=resource_pack.get_translation('start.exit'),  command=lambda: exit())
        self.game_item_list = Listbox(self, height=12)
        self.vscroll = ttk.Scrollbar(self, orient='vertical', command=self.game_item_list.yview)
        self.game_item_list.configure(yscrollcommand=self.vscroll.set)
        self.repair_button = ttk.Button(self, text=resource_pack.get_translation('start.multiplayer'))
        self.del_button = ttk.Button(self, text=resource_pack.get_translation('start.delete'), command=self.delete)
        self.rename_button = ttk.Button(self, text=resource_pack.get_translation('start.rename'), command=self.rename)
        # 显示
        self.new_button.grid(column=0, row=0, padx=5, pady=5)
        self.start_button.grid(column=1, row=0, padx=5, pady=5)
        self.exit_button.grid(column=2, row=0, padx=5, pady=5)
        self.game_item_list.grid(column=0, columnspan=4, row=1, padx=3, pady=5, sticky='news')
        self.vscroll.grid(column=4, row=1, padx=2, pady=5, sticky='nes')
        self.repair_button.grid(column=0, row=2, padx=5, pady=5)
        self.del_button.grid(column=1, row=2, padx=5, pady=5)
        self.rename_button.grid(column=2, row=2, padx=5, pady=5)
        self.resizable(False, False)
        self.refresh()

    def delete(self, event=None):
        # 删除世界
        if self.game_item_list.curselection() == ():
            select = self.game_item_list.get(0)
        else:
            select = self.game_item_list.get(self.game_item_list.curselection()[0])
        if messagebox.askyesno(message=resource_pack.get_translation('start.dialog.text.delete') % select,
                title=resource_pack.get_translation('start.dialog.title.delete')):
            shutil.rmtree(os.path.join(saves_path, select))
        self.refresh()

    def new(self, event=None):
        # 新的世界对话框
        self.new_dialog = Toplevel(self)
        self.new_dialog.title(resource_pack.get_translation('start.dialog.title.new'))
        self.new_dialog_label_name = ttk.Label(self.new_dialog, text=resource_pack.get_translation('start.dialog.text.name'))
        self.new_dialog_entry_name = ttk.Entry(self.new_dialog)
        self.new_dialog_label_seed = ttk.Label(self.new_dialog, text=resource_pack.get_translation('general.seed'))
        self.new_dialog_entry_seed = ttk.Entry(self.new_dialog)
        self.new_dialog_label_type = ttk.Label(self.new_dialog, text=resource_pack.get_translation('start.dialog.text.type'))
        self.new_dialog_combobox_type = ttk.Combobox(self.new_dialog, values =resource_pack.get_translation('start.worldtype'),
                width=18)
        self.new_dialog_combobox_type.state(['readonly'])
        self.new_dialog_button_ok = ttk.Button(self.new_dialog,
                text=resource_pack.get_translation('start.dialog.text.ok'), command=self.new_world
                                               )
        self.new_dialog_label_name.grid(column=0, row=0, padx=5, pady=5)
        self.new_dialog_entry_name.grid(column=1, row=0, columnspan=2, padx=5,
                                        pady=5)
        self.new_dialog_label_seed.grid(column=0, row=1, padx=5, pady=5)
        self.new_dialog_entry_seed.grid(column=1, row=1, columnspan=2, padx=5,
                                        pady=5)
        self.new_dialog_label_type.grid(column=0, row=2, padx=5, pady=5)
        self.new_dialog_combobox_type.grid(column=1, row=2, columnspan=2, padx=5, pady=5)
        self.new_dialog_button_ok.grid(column=2, row=3, padx=5, pady=5)
        self.new_dialog.resizable(False, False)
        self.new_dialog.geometry('+%d+%d' % (self.winfo_x() + 50,
                                 self.winfo_y() + 50))
        self.new_dialog.transient(self)
        self.new_dialog.deiconify()
        self.new_dialog.grab_set()
        self.new_dialog.wait_window()

    def new_world(self, event=None):
        # 创建一个新的世界
        name = self.new_dialog_entry_name.get() 
        seed = self.new_dialog_entry_seed.get()
        if self.new_dialog_combobox_type.get() == resource_pack.get_translation('start.worldtype'):
            world_type = 'flat'
        else:
            world_type = 'random'
        if seed == '':
            seed = hash(time.ctime())
        else:
            seed = hash(seed)
        is_valid_char = lambda c: any([c.isalpha(), c.isdigit(), c == '-', c == '_'])
        if not all([c for c in map(is_valid_char, name)]):
            log_err('invalid world name')
        else: 
            if not os.path.isdir(os.path.join(saves_path, name)):
                if (('懒' in name) or ('懶' in name)) and ('zh' in settings['lang']):
                    messagebox.showinfo(title=resource_pack.get_translation('start.egg.title'),
                            message=resource_pack.get_translation('start.egg.message'))
                os.mkdir(os.path.join(saves_path, name))
                world = open(os.path.join(saves_path, name, 'world.json'), 'w+')
                world.write('{}\n')
                world.close()
                world_level = {'data_version': VERSION['data'], 'seed': seed, 'type': world_type,
                        'time': 400, 'weather': {'now': 'clear', 'duration': 600}}
                json.dump(world_level, open(os.path.join(saves_path, name, 'level.json'), 'w+'))
                os.mkdir(os.path.join(saves_path, name, 'players'))
                player_info = {'position': '0', 'respawn': '0', 'now_block': 0}
                json.dump(player_info, open(os.path.join(saves_path, name, 'players', '%s.json' % player['id']), 'w+'))
                self.new_dialog.destroy()
                log_info('create world successfully')
            else:
                log_warn('Save existed')
        self.refresh()

    def refresh(self):
        # 刷新
        self.game_item_list.delete(0, 'end')
        for item in [i for i in os.listdir(saves_path) if is_game_restore(i)]:
            self.game_item_list.insert('end', item)

    def rename(self):
        # 重命名对话框
        self.rename_dialog = Toplevel(self)
        self.rename_dialog.title(resource_pack.get_translation('start.dialog.title.rename'))
        self.rename_dialog_label = ttk.Label(self.rename_dialog,
            style='TLabel', text=resource_pack.get_translation('start.dialog.text.name'))
        self.rename_dialog_entry = ttk.Entry(self.rename_dialog)
        name = self.game_item_list.curselection()
        name = self.game_item_list.get(0) if name == () else self.game_item_list.get(name)
        self.rename_dialog_entry.insert(0, name)

        def send_name():
            self.rename_world(name)

        self.old = os.path.join(saves_path, self.rename_dialog_entry.get())
        self.rename_dialog_button = ttk.Button(self.rename_dialog,
                text=resource_pack.get_translation('start.dialog.text.ok'), command=send_name)
        self.rename_dialog_label.grid(column=0, row=0, padx=5, pady=5)
        self.rename_dialog_entry.grid(column=1, row=0, columnspan=2, padx=5, pady=5)
        self.rename_dialog_button.grid(column=2, row=1, padx=5, pady=5)
        self.rename_dialog.resizable(False, False)
        self.rename_dialog.geometry('+%d+%d' % (self.winfo_x() + 50, self.winfo_y() + 50))
        self.rename_dialog.transient(self)
        self.rename_dialog.deiconify()
        self.rename_dialog.grab_set()
        self.rename_dialog.wait_window()

    def rename_world(self, name):
        # 重命名世界
        shutil.move(os.path.join(saves_path, name), os.path.join(saves_path, self.rename_dialog_entry.get()))
        self.rename_dialog.destroy()
        self.refresh()

    def start_game(self, event=None):
        # 启动游戏
        select = self.game_item_list.curselection()
        if  select == ():
            log_warn('no world selected')
            return
        select = self.game_item_list.get(select[0])
        self.destroy()
        try:
            data = load_window()
            game = Game(width=max(data['width'], 800), height=max(data['height'], 600),
                    caption='Minecraft %s [pyVAPE]' % VERSION['str'], resizable=True)
            game.set_name(select)
            setup_opengl()
            pyglet.app.run()
        except SystemExit:
            pass
        except:
            name = time.strftime('error-%Y-%m-%d_%H.%M.%S.log')
            log_err('Catch error, saved in: log/%s' % name)
            with open(os.path.join(search_mcpy(), 'log', name), 'a+') as err_log:
                err_log.write('Minecraft version: %s\n' % VERSION['str'])
                err_log.write('python version: %s for %s\n' % ('.'.join([str(s) for s in sys.version_info[:3]]), sys.platform))
                err_log.write('pyglet version: %s(OpenGL %s)\n' % (pyglet.version, gl_info.get_version()))
                err_log.write('time: %s\n' % time.ctime())
                err_log.write('save: %s\n' % select)
                err_log.write('traceback:\n' + '=' * 34 + '\n')
                traceback.print_exc(file=err_log)
                err_log.write('=' * 34 + '\n')
            with open(os.path.join(search_mcpy(), 'log', 'error-latest.log'), 'w+') as latest_log:
                with open(os.path.join(search_mcpy(), 'log', name), 'r+') as err_log:
                    latest_log.write(err_log.read())
            exit(1)

