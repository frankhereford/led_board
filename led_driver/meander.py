from xled_plus.samples.sample_setup import *
import random

def generate_tuples(n):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]


class MyColorMeanderEffect(Effect):
    def __init__(self, ctr, style):
        super(MyColorMeanderEffect, self).__init__(ctr)
        # styles: solid, sequence, scattered, multi, blend, tandem, (whites?)
        self.style = style
        self.pat = None
        self.cm = None
        self.updatefunc = None
        self.preferred_fps = 120
        self.preferred_frames = 500

    def reset(self, numframes):
        self.pat = self.ctr.make_func_pattern(lambda i: hsl_color(0, 0, 1))
        self.cm = ColorMeander(speed=.01)
        if numframes:
            self.cm.steplen *= 10
            self.cm.noiselev *= 3
            self.preferred_fps /= 10
        if self.style == "solid":
            self.updatefunc = self.update_solid
        elif self.style == "sequence":
            self.updatefunc = self.update_sequence
        elif self.style == "scattered":
            self.updatefunc = self.update_scattered
            self.perm = list(range(self.ctr.num_leds))
            random.shuffle(self.perm)
            self.pat0 = self.pat
        elif self.style == "tandem":
            self.updatefunc = self.update_tandem
        elif self.style == "multi":
            self.cms = [ColorMeander() for i in range(3)]
            self.updatefunc = self.update_multi
        elif self.style == "blend":
            self.cm2 = ColorMeander()
            self.props = [random.random() for i in range(self.ctr.num_leds)]
            self.updatefunc = self.update_blend
        else:
            print("Bad Meander style")
            self.update_func = lambda: None

    def update_solid(self):
        self.cm.step()
        self.pat = self.ctr.make_func_pattern(lambda i: self.cm.get())

    def update_sequence(self):
        self.cm.step()
        self.pat = self.ctr.shift_pattern(self.pat, 1, self.cm.get(), circular=True)

    def update_scattered(self):
        self.cm.step()
        self.pat0 = self.ctr.shift_pattern(self.pat0, 1, self.cm.get())
        self.pat = self.ctr.permute_pattern(self.pat0, self.perm)

    def update_tandem(self):
        self.cm.step()
        (h, s, l) = self.cm.get_hsl()
        col1 = hsl_color(h, s, l)
        col2 = hsl_color((h + 0.5) % 1.0, s, l)
        self.pat = self.ctr.make_func_pattern(
            lambda i: col1 if i < self.ctr.num_leds // 2 else col2
        )

    def update_multi(self):
        for cm in self.cms:
            cm.step()
        self.pat = self.ctr.make_func_pattern(
            lambda i: self.cms[i % len(self.cms)].get()
        )

    def update_blend(self):
        self.cm.step()
        self.cm2.step()
        self.pat = self.ctr.make_func_pattern(
            lambda i: blendcolors(self.cm.get(), self.cm2.get(), self.props[i])
        )

    def getnext(self):
        self.updatefunc()
        return self.pat

ctr = setup_control()
oldmode = ctr.get_mode()["mode"]
eff = MyColorMeanderEffect(ctr, "blend")
eff.launch_rt()
print("Started continuous effect - press Return to stop it")
input()
eff.stop_rt()
ctr.set_mode(oldmode)