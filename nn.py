from spaceinvaders import Start
from random import randint
game = Start(2)
print('done')
while True:
    num = randint(0, 3)
    game.do_action(num)