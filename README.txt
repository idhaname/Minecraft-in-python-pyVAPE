pyVAPE客户端，正如它的名字，这是一个作弊客户端。
*提示：请支持源项目：https://github.com/Minecraft-in-python/Minecraft

修改内容：
1.玩家不会掉进虚空中死亡；
2.玩家不会被TNT炸死；
3.客户端默认开启F3调试；
4.客户端默认在创建世界时给予玩家隐藏方块(沙子、基岩、错误方块)；
5.基岩可以被玩家与TNT破坏；
6.语言默认中文;
7.更改了F3调试屏幕的相关样式。
窗口标题、调试屏幕将添加[pyVAPE]字样。

安装方式：
如原版一样。参见Original-README.md了解详情。

具体修改情况：
minecraft\game.py
l82~83 4
l556~558 1
l78 3
minecraft\block\bedrock.py
l6 5
minecraft\entity\item\tnt.py
l22~23 2
至于6，暂时没找出别的好方法。目前的实现方法是：
将原来minecraft\assets\lang\en_us.json重命名为1en_us.json，
并将原来minecraft\assets\lang\zh_cn.json重命名为en_us.json来欺骗游戏加载
minecraft\assets\lang\en_us.json(重命名后)
l35~36 7
