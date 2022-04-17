from minecraft.block.base import Block


class Bedrock(Block):
    #无法破坏基岩
    #hardness = -1
    name = 'bedrock'
    textures = 'bedrock',
