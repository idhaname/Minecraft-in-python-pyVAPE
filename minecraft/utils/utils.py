import atexit
import math
import time

start_time = time.strftime('%Y-%m-%d_%H.%M.%S')
log_str = list()
_have_color = None
try:
    from colorama import Fore, Style, init
    init()
except ModuleNotFoundError:
    _have_color = False
else:
    _have_color = True

import pyglet

def cube_vertices(x, y, z, bottom, height, offset=(0, 0, 0)):
    # 返回在 x, y, z 坐标的方形顶点
    b, h = bottom / 2, height / 2
    ox, oy, oz = [i / 2 for i in offset]
    return [
            x-b+ox,y+h+oy,z-b+oz, x-b+ox,y+h+oy,z+b+oz, x+b+ox,y+h+oy,z+b+oz, x+b+ox,y+h+oy,z-b+oz,  # 顶部
            x-b+ox,y-h+oy,z-b+oz, x+b+ox,y-h+oy,z-b+oz, x+b+ox,y-h+oy,z+b+oz, x-b+ox,y-h+oy,z+b+oz,  # 底部
            x-b+ox,y-h+oy,z-b+oz, x-b+ox,y-h+oy,z+b+oz, x-b+ox,y+h+oy,z+b+oz, x-b+ox,y+h+oy,z-b+oz,  # 左边
            x+b+ox,y-h+oy,z+b+oz, x+b+ox,y-h+oy,z-b+oz, x+b+ox,y+h+oy,z-b+oz, x+b+ox,y+h+oy,z+b+oz,  # 右边
            x-b+ox,y-h+oy,z+b+oz, x+b+ox,y-h+oy,z+b+oz, x+b+ox,y+h+oy,z+b+oz, x-b+ox,y+h+oy,z+b+oz,  # 前面
            x+b+ox,y-h+oy,z-b+oz, x-b+ox,y-h+oy,z-b+oz, x-b+ox,y+h+oy,z-b+oz, x+b+ox,y+h+oy,z-b+oz,  # 后面
        ]

def tex_coords(top, bottom, side0, side1=None, n=1):

    def tex_coord(x, y):
        m = 1.0 / n
        dx = x * m
        dy = y * m
        return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m

    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side0 = tex_coord(*side0)
    if side1 is not None:
        side1 =tex_coord(*side1)
    result = list()
    result.extend(top)
    result.extend(bottom)
    if side1 is None:
        result.extend(side0)
    else:
        result.extend(side1)
    result.extend(side0 * 3)
    return result

def get_size():
    # 返回窗口大小
    for w in pyglet.canvas.get_display().get_windows():
        if str(w).startswith('Game'):
            return w.width, w.height
    else:
        return 800, 600

def get_game():
    # 获取 Game 类
    for w in pyglet.canvas.get_display().get_windows():
        if str(w).startswith('Game'):
            return w

def get_color_by_brightness(brightness, color=None):
    # 获取不同亮度下的颜色
    brightness = int(min(16, max(1, brightness)))
    if color is None:
        # 0.9 / 16 = 0.05625
        return [0.1 + brightness * 0.05625] * 3
    else:
        return [(i / 16) * brightness for i in color]

def log_err(text, name='client', where='cl'):
    # 打印错误信息
    # 于何处: where
    # c(onsole) - 于标准输出中打印
    # l(og)     - 保存至日志文件
    if 'l' in where:
        log_str.append('[ERR  %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))
    if 'c' in where:
        if _have_color:
            print('%s[ERR  %s %s]%s %s' % (Fore.RED, time.strftime('%H:%M:%S'), name, Style.RESET_ALL, text))
        else:
            print('[ERR  %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))

def log_info(text, name='client', where='cl'):
    # 打印信息
    if 'l' in where:
        log_str.append('[INFO %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))
    if 'c' in where:
        if _have_color:
            print('%s[INFO %s %s]%s %s' % (Fore.GREEN, time.strftime('%H:%M:%S'), name, Style.RESET_ALL, text))
        else:
            print('[INFO %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))

def log_warn(text, name='client', where='cl'):
    # 打印警告信息
    if 'l' in where:
        log_str.append('[WARN %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))
    if 'c' in where:
        if _have_color:
            print('%s[WARN %s %s]%s %s' % (Fore.YELLOW, time.strftime('%H:%M:%S'), name, Style.RESET_ALL, text))
        else:
            print('[WARN %s %s] %s' % (time.strftime('%H:%M:%S'), name, text))

def mdist(p, q):
    # 曼哈顿距离
    assert len(p) == len(q), 'both points must have the same number of dimensions'
    total = 0
    for i in range(len(p)):
        total += abs(p[i] + q[i])
    return total

def normalize(position):
    pos = []
    for n in position:
        pos.append(int(round(n)))
    else:
        return tuple(pos)

@atexit.register
def on_exit():
    _os  = __import__('os')
    log_info("Save logs to 'log/log-%s.log'" % start_time)
    log_info('Exit')
    with open(_os.path.join(search_mcpy(), 'log', 'log-%s.log' % start_time), 'w+') as log:
        log.write('\n'.join(log_str))
    with open(_os.path.join(search_mcpy(), 'log', 'log-latest.log'), 'w+') as latest_log:
        latest_log.write('\n'.join(log_str))

def pos2str(position):
    # 将坐标转换为字符串
    return ' '.join([str(s) for s in position])

def search_mcpy():
    # 寻找文件存储位置
    _os  = __import__('os')
    _sys = __import__('sys')
    platform = _sys.platform
    environ, path = _os.environ, _os.path
    if 'MCPYPATH' in environ:
        MCPYPATH = environ['MCPYPATH']
    elif platform == 'darwin':
        MCPYPATH = path.join(path.expanduser('~'), 'Library', 'Application Support', 'mcpy')
    elif platform.startswith('win'):
        MCPYPATH = path.join(path.expanduser('~'), 'mcpy')
    else:
        MCPYPATH = path.join(path.expanduser('~'), '.mcpy')
    return MCPYPATH

def sectorize(position):
    # 返回坐标所在的区块
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)

def str2pos(string, float_=False):
    # pos2str 的逆函数
    if float_:
        return tuple([float(i) for i in string.split(' ')])
    else:
        return tuple([int(float(i)) for i in string.split(' ')])

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

VERSION = {
        'major': 0,
        'minor': 3,
        'patch': 2,
        'str': '0.3.2',
        'data': 1
    }

TICKS_PER_SEC = 60
SECTOR_SIZE = 16

MAX_SIZE = 32
SEA_LEVEL = 10

STEALING_SPEED = 3
WALKING_SPEED = 5
RUNNING_SPEED = 8
FLYING_SPEED = 10

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 36
