from minecraft.block.base import Block
from minecraft.utils.utils import *


class Dirt(Block):
    name = 'dirt'
    textures = 'dirt',

    def on_ticking(self, pos):
        pos = (pos[0], pos[1] + 1, pos[2])
        if (pos not in get_game().world.world) or ((pos in get_game().world.world) and (get_game().world.get(pos).transparent)):
            get_game().world.add_block(pos, 'grass')
