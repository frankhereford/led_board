import sys
from xled_plus.highcontrol import HighControlInterface

from xled_plus.effect_base import Effect
from xled_plus.ledcolor import hsl_color
from xled_plus.pattern import (
    blendcolors
)

import random

class Glowbit:
    def __init__(self, cols, bend, steps, initstep=False, loop=False):
        self.count = 0
        self.lastcol = (0, 0, 0)
        self.nextcol = (0, 0, 0)
        self.currcol = (0, 0, 0)
        self.loop = loop
        self.currind = initstep if initstep else steps
        self.steps = steps
        self.cols = cols
        self.bend = bend
        if self.loop:
            self.initcol1 = hsl_color(
                *self.cols[int((random.random() ** self.bend) * len(self.cols))]
            )
            self.initcol2 = hsl_color(
                *self.cols[int((random.random() ** self.bend) * len(self.cols))]
            )
            self.lastcol = self.initcol1
            self.nextcol = self.initcol2

    def getnext(self):
        if self.currind == self.steps:
            self.lastcol = self.nextcol
            if self.loop and self.count + self.steps >= self.loop:
                self.nextcol = self.initcol2
            elif self.loop and self.count + 2 * self.steps >= self.loop:
                self.nextcol = self.initcol1
            else:
                self.nextcol = hsl_color(
                    *self.cols[int((random.random() ** self.bend) * len(self.cols))]
                )
            self.currind = 0
        self.currind += 1
        self.count += 1
        thing = blendcolors(self.lastcol, self.nextcol, float(self.currind) / self.steps)
        print("Thing: ", thing)
        return thing


class GlowEffect(Effect):
    def __init__(self, ctr, cols, bend, cycles, fps=False):
        super(GlowEffect, self).__init__(ctr)
        if fps:
            self.preferred_fps = fps
        self.cols = cols
        self.bend = bend
        self.cycles = cycles

    def reset(self, numframes):
        if type(self.cycles) == int:
            steps = [self.cycles]
        elif numframes:
            steps = []
            for n in range(self.cycles[0], self.cycles[-1] + 1):
                if numframes % n == 0:
                    steps.append(n)
            if not steps:
                steps = list(range(self.cycles[0], self.cycles[-1] + 1))
        else:
            steps = list(range(self.cycles[0], self.cycles[-1] + 1))
        pr1 = 13 if len(steps) % 13 != 0 else 7
        pr2 = 11 if len(steps) % 11 != 0 else 7
        self.glowarray = [
            Glowbit(
                self.cols,
                self.bend,
                steps[(i * pr1) % len(steps)],
                (i * pr2) % steps[(i * pr1) % len(steps)],
                numframes,
            )
            for i in range(self.ctr.num_leds)
        ]

        #print("array: ", self.glowarray)

    def getnext(self):
        thing = self.ctr.make_func_pattern(lambda i: self.glowarray[i].getnext())
        #print("thing: ", thing)
        return thing

class Fire(GlowEffect):
    def __init__(self, ctr):
        cols = [
            [0.5689, 1.0, -0.2847],
            [0.5413, 1.0, -0.1809],
            [0.5119, 1.0, -0.0685],
            [0.6185, 1.0, -0.4416],
            [0.6206, 1.0, -0.6780],
            [0.5068, 1.0, 0.1797],
            [0.5603, 1.0, -0.0170],
            [0.45, 1.0, 0.1],
        ]
        super(Fire, self).__init__(ctr, cols, 2, [3, 6], 1)


host = sys.argv[1]
board = HighControlInterface(host)

Fire(board).launch_movie()