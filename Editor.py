from PIL import Image
import PIL
import tkinter as tk
from tkinter.filedialog import askopenfile, asksaveasfile
from tkinter.messagebox import showinfo, askyesno, askokcancel
import enum


class MetaPixelValueType(enum.Enum):
    Bool = 0, "Snow2"
    Int = 1, "cyan"
    Float = 2, "Lime"
    IntPair = 3, "DeepSkyBlue"
    Vec2 = 4, "Tan1"
    NormalizedVec2 = 5, "Maroon1"
    Randomized = 6, "SlateBlue"


class MetaPixelValue:
    def __init__(self, value):
        assert isinstance(value, MetaPixelValueType)
        self.type = value
        self.g = 0
        self.b = 0

    def get_type(self):
        return self.type

    def get_values(self):
        return ()

    def get_colors(self):
        self.calc_colors()
        return self.g, self.b

    def calc_colors(self):
        self.g = 0
        self.b = 0

    def set_colors(self, g: int, b: int):
        pass

    def get_help(self):
        return self.type.name

    def set_value(self, a: float, b: float):
        pass


class Bool(MetaPixelValue):
    def __init__(self):
        super().__init__(MetaPixelValueType.Bool)

    def get_values(self):
        return ()

    def get_help(self):
        return "If this meta pixel exists it's properties are on"


class Vec2(MetaPixelValue):
    def __init__(self, vec_range=128.0, value=(128.0, 128.0)):
        super().__init__(MetaPixelValueType.Vec2)
        self.midpoint = value
        self.range = vec_range
        self.value_x = self.midpoint[0]
        self.value_y = self.midpoint[1]

    def get_values(self):
        self.set_colors(self.g, self.b)
        self.calc_colors()
        return self.value_x, self.value_y

    def calc_colors(self):
        self.g = self.value_x+self.midpoint[0]
        self.b = self.value_y+self.midpoint[1]

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = b
        self.value_x = self.g-self.midpoint[0]
        self.value_y = self.b-self.midpoint[1]
        if self.range < self.value_x: self.value_x = self.range
        if self.range < self.value_y: self.value_y = self.range
        if self.value_x < -self.range: self.value_x = -self.range
        if self.value_y < -self.range: self.value_y = -self.range

    def set_value(self, a: float, b: float):
        self.value_x = a
        self.value_y = b
        self.calc_colors()

    def get_help(self):
        return str(self.midpoint[0])+" is 0, negative numbers are below that value & positive above. This Vec2 has a " \
                                     "range of " \
               + str(self.range)+" which means the min & max are ("+str(self.midpoint[0]-self.range)+", "\
               + str(self.midpoint[1]+self.range)+")"


class Float(MetaPixelValue):
    def __init__(self, float_range=1.0, value=1.0):
        super().__init__(MetaPixelValueType.Float)
        self.range = float_range
        self.value = value

    def get_values(self):
        self.set_colors(self.g, self.b)
        self.calc_colors()
        return self.value,

    def calc_colors(self):
        self.g = int(255 * (self.value / self.range))
        self.b = 0

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = 0
        self.value = (self.g / 255) * self.range

    def set_value(self, a: float, b: float):
        self.value = a
        self.calc_colors()

    def get_help(self):
        return "0 through 255 will be translated into a number between two values. For this float those two values are"\
               + " 0.0 to "+str(self.range)+"."


class Int(MetaPixelValue):
    def __init__(self, int_range=255, value=0):
        super().__init__(MetaPixelValueType.Int)
        self.range = int_range
        self.value = value

    def get_values(self):
        self.set_colors(self.g, self.b)
        self.calc_colors()
        return self.value,

    def calc_colors(self):
        self.g = self.value
        self.b = 0

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = 0
        self.value = g
        if self.range < self.value: self.value = self.range
        if self.value < 0: self.value = 0

    def set_value(self, a: float, b: float):
        self.value = a
        self.calc_colors()

    def get_help(self):
        return "The green RGB value is the value of the integer. This integer has a max value of "+str(self.range)


class IntPair(MetaPixelValue):
    def __init__(self, int_range_x=255, int_range_y=255, value_x=0, value_y=0):
        super().__init__(MetaPixelValueType.IntPair)
        self.value_x = Int(int_range=int_range_x, value=value_x)
        self.value_y = Int(int_range=int_range_y, value=value_y)

    def get_values(self):
        self.set_colors(self.g, self.b)
        self.calc_colors()
        return self.value_x.get_values()[0], self.value_y.get_values()[0]

    def calc_colors(self):
        self.g = self.value_x.get_colors()[0]
        self.b = self.value_y.get_colors()[0]

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = b
        self.value_x.set_colors(g, 0)
        self.value_y.set_colors(b, 0)

    def set_value(self, a: float, b: float):
        self.value_x.set_value(a, 0.0), self.value_y.set_value(b, 0.0)
        self.calc_colors()

    def get_help(self):
        return "The green RGB value is the first value of the integer, the second is the blue RGB value. This IntPair "\
               + "has a max value A & max value B of "+str((self.value_x.range, self.value_y.range))


class NormalizedVec2(MetaPixelValue):
    def __init__(self, vec_range=1.0, value=(0.0, 0.0), allow_negative=True):
        super().__init__(MetaPixelValueType.NormalizedVec2)
        self.offset = (128.0, 128.0) if allow_negative else (0.0, 0.0)
        self.negative = allow_negative
        self.range = vec_range
        self.value_x = value[0]
        self.value_y = value[1]

    def get_values(self):
        self.set_colors(self.g, self.b)
        self.calc_colors()
        return self.value_x, self.value_y

    def calc_colors(self):
        self.g = (255 * (self.value_x / self.range))+self.offset[0]
        self.b = (255 * (self.value_y / self.range))+self.offset[1]

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = b
        self.value_x = (self.g - self.offset[0]) / 255 * self.range
        self.value_y = (self.b - self.offset[1]) / 255 * self.range
        if self.negative:
            if self.value_x < -self.range/2: self.value_x = -self.range/2
            elif self.range/2 < self.value_x: self.value_x = self.range/2

            if self.value_y < -self.range/2: self.value_y = -self.range/2
            elif self.range/2 < self.value_y: self.value_y = self.range/2
        else:
            if self.value_x < 0: self.value_x = 0
            elif self.range < self.value_x: self.value_x = self.range

            if self.value_y < -self.range / 2: self.value_y = -self.range / 2
            elif self.range < self.value_y: self.value_y = self.range / 2

    def set_value(self, a: float, b: float):
        self.value_x = a
        self.value_y = b
        self.calc_colors()

    def get_help(self):
        range_min = -self.range/2 if self.negative else 0.0
        range_max = self.range/2 if self.negative else self.range

        return "A vector that behaves like a float where the green & blue RGB values (0 through 255) are turned into" \
               " a different number range. For this NormalizedVec2 that is ("+str(range_min)+", "+str(range_max)+")"


class Randomize(MetaPixelValue):
    def __init__(self):
        super().__init__(MetaPixelValueType.Randomized)

    def get_values(self):
        return ()

    def set_colors(self, g: int, b: int):
        self.g = g
        self.b = g


class MetaPixelType(enum.Enum):
    # Misc
    HatOffset = 1, Vec2(vec_range=16), \
    "Hat offset position in pixels", 0

    UseDuckColor = 2, Bool(), \
    "If this metapixel exists, White (255, 255, 255) and Grey(157, 157, 157) will be recolored to duck colors.", 0

    # Capes
    CapeOffset = 10, Vec2(vec_range=16), \
    "Cape offset position in pixels", 1

    CapeForeground = 11, Bool(), \
    "If this metapixel exists, the cape will be drawn over the duck.", 1

    CapeSwayModifier = 12, NormalizedVec2(value=(0.3, 1.0)), \
    "Affects cape length, and left to right sway.", 1

    CapeWiggleModifier = 13, NormalizedVec2(value=(1.0, 1.0)), \
    "Affects how much the cape wiggles in the wind.", 1

    CapeTaperStart = 14, Float(value=0.5), \
    "Affects how narrow the cape/trail is at the top/beginning.", 1

    CapeTaperEnd = 15, Float(), \
    "Affects how narrow the cape/trail is at the bottom/end.", 1

    CapeAlphaStart = 16, Float(), \
    "Affects how transparent the cape/trail is at the top/beginning.", 1

    CapeAlphaEnd = 17, Float(), \
    "Affects how transparent the cape/trail is at the bottom/end.", 1

    CapeIsTrail = 20, Bool(), \
    "If this metapixel exists, the cape will be a trail instead of a cape (think of the rainbow trail left by the " \
    "TV object).", 1

    # Particles
    ParticleEmitterOffset = 30, Vec2(vec_range=16.0), \
    "The offset in pixels from the center of the hat where particles will be emitted.", 2

    ParticleDefaultBehavior = 31, Int(int_range=4, value=0), \
    "B defines a particle behavior from a list of presets: 0 = No Behavior, 1 = Spit, 2 = Burst," \
    " 3 = Halo, 4 = Exclamation", 2

    ParticleEmitShape = 32, IntPair(int_range_x=2, int_range_y=2), \
    "G: 0 = Point, 1 = Circle, 2 = Box   B: 0 = Emit Around Shape Border Randomly, 1 = Fill Shape Randomly, " \
    "2 = Emit Around Shape Border Uniformly", 2

    ParticleEmitShapeSize = 33, Vec2(vec_range=24.0, value=(24.0, 24.0)), \
    "X and Y size of the particle emitter (in pixels). Should be IntPair with usage but is this type in docs.", 2

    ParticleCount = 34, Int(int_range=8, value=4), \
    "The number of particles to emit.", 2

    ParticleLifespan = 35, Float(float_range=2.0), \
    "Life span of the particle, in seconds (0 to 2 seconds)", 2

    ParticleVelocity = 36, NormalizedVec2(vec_range=2.0), \
    "Initial velocity of the particle.", 2

    ParticleGravity = 37, NormalizedVec2(vec_range=2.0), \
    "Gravity applied to the particle.", 2

    ParticleFriction = 38, NormalizedVec2(vec_range=2.0, allow_negative=False, value=(1.0, 1.0)), \
    "Friction applied to the particle (The value it's velocity is multiplied by every frame).", 2

    ParticleAlpha = 39, NormalizedVec2(vec_range=2.0, allow_negative=False, value=(1.0, 1.0)), \
    "G = Start alpha, B = End alpha", 2

    ParticleScale = 40, NormalizedVec2(vec_range=2.0, allow_negative=False, value=(1.0, 0.0)), \
    "G = Start scale, B = End scale", 2

    ParticleRotation = 41, NormalizedVec2(vec_range=36.0, allow_negative=False, value=(0.0, 0.0)), \
    "G = Start rotation, B = End rotation", 2

    ParticleOffset = 42, Vec2(vec_range=16), \
    "Additional X Y offset of particle.", 2

    ParticleBackground = 43, Bool(), \
    "If this metapixel exists, particles will be rendered behind the duck.", 2

    ParticleAnchor = 44, Bool(), \
    "If this metapixel exists, particles will stay anchored around the hat position when it's moving.", 2

    ParticleAnimated = 45, Bool(), \
    "If this metapixel exists, particles will animate through their frames. Otherwise, a frame will be picked " \
    "randomly.", 2

    ParticleAnimationLoop = 46, Bool(), \
    "If this metapixel exists, the particle animation will loop.", 2

    ParticleAnimationRandomFrame = 47, Bool(), \
    "If this metapixel exists, the particle animation will start on a random frame.", 2

    ParticleAnimationSpeed = 48, Float(value=0.1), \
    "How quickly the particle animates.", 2

    # Strange
    WetLips = 70, Bool(), \
    "If this metapixel exists, the hat will have 'wet lips'.", 3

    MechanicalLips = 71, Bool(), \
    "If this metapixel exists, the hat will have 'mechanical lips'.", 3

    # Special
    RandomizeParameterX = 100, Randomize(), \
    "If present, the previously defined metapixel value will have a random number between G and B applied to its X " \
    "value each time it's used. This will generally only work with particles..", 4

    RandomizeParameterY = 101, Randomize(), \
    "If present, the previously defined metapixel value will have a random number between G and B applied to its X " \
    "value each time it's used. This will generally only work with particles..", 4

    RandomizeParameter = 102, Randomize(), \
    "If present, the previously defined metapixel value will have a random number between G and B applied to its " \
    "X and Y values each time it's used. This will generally only work with particles..", 4


class MetaPixel:

    TYPES = {
            1: MetaPixelType.HatOffset,
            2: MetaPixelType.UseDuckColor,
            10: MetaPixelType.CapeOffset,
            11: MetaPixelType.CapeForeground,
            12: MetaPixelType.CapeSwayModifier,
            13: MetaPixelType.CapeWiggleModifier,
            14: MetaPixelType.CapeTaperStart,
            15: MetaPixelType.CapeTaperEnd,
            16: MetaPixelType.CapeAlphaStart,
            17: MetaPixelType.CapeAlphaEnd,
            20: MetaPixelType.CapeIsTrail,
            30: MetaPixelType.ParticleEmitterOffset,
            31: MetaPixelType.ParticleDefaultBehavior,
            32: MetaPixelType.ParticleEmitShape,
            33: MetaPixelType.ParticleEmitShapeSize,
            34: MetaPixelType.ParticleCount,
            35: MetaPixelType.ParticleLifespan,
            36: MetaPixelType.ParticleVelocity,
            37: MetaPixelType.ParticleGravity,
            38: MetaPixelType.ParticleFriction,
            39: MetaPixelType.ParticleAlpha,
            40: MetaPixelType.ParticleScale,
            41: MetaPixelType.ParticleRotation,
            42: MetaPixelType.ParticleOffset,
            43: MetaPixelType.ParticleBackground,
            44: MetaPixelType.ParticleAnchor,
            45: MetaPixelType.ParticleAnimated,
            46: MetaPixelType.ParticleAnimationLoop,
            47: MetaPixelType.ParticleAnimationRandomFrame,
            48: MetaPixelType.ParticleAnimationSpeed,
            70: MetaPixelType.WetLips,
            71: MetaPixelType.MechanicalLips,
            100: MetaPixelType.RandomizeParameterX,
            101: MetaPixelType.RandomizeParameterY,
            102: MetaPixelType.RandomizeParameter
        }

    COLORS = {
        0: "Gold",
        1: "LightSkyBlue",
        2: "PaleGreen",
        3: "Wheat1",
        4: "HotPink"
    }

    def __init__(self, meta_pixel_type: MetaPixelType, g, b):
        assert isinstance(meta_pixel_type, MetaPixelType)
        self.type = meta_pixel_type

        value = meta_pixel_type.value[1]
        assert isinstance(value, MetaPixelValue)
        self.value = value

        self.value.set_colors(g, b)

    def get_rgba(self):
        gb = self.value.get_colors()
        r, g, b, a = int(self.type.value[0]), int(gb[0]), int(gb[1]), 255
        g = 0 if g < 0 else 255 if 255 < g else g
        b = 0 if g < 0 else 255 if 255 < g else g
        return r, g, b, a

    def get_value(self):
        return self.value.get_values()


class MetaPixelGui:
    def __init__(self, pixel: MetaPixel, row: int, frame: tk.Frame, label: tk.Label, editor):
        assert isinstance(editor, Editor)
        self.editor = editor
        self.label = label

        self.pixel = pixel

        self.remove_button = tk.Button(frame, text="X", bg="red")
        self.remove_button["command"] = self.click_x
        self.remove_button.grid(column=0, row=row, sticky=tk.NSEW)

        self.meta_pixel_button = tk.Button(frame, text=pixel.type.name, bg=self.pixel.COLORS.get(pixel.type.value[3]))
        self.meta_pixel_button["command"] = self.click_meta
        self.meta_pixel_button.grid(column=1, row=row, sticky=tk.NSEW)

        self.G = tk.Text(frame, width=3, height=1)
        self.G.grid(column=2, row=row, sticky=tk.NSEW)
        self.G.insert(tk.INSERT, str(self.pixel.value.g))

        self.B = tk.Text(frame, width=3, height=1)
        self.B.grid(column=3, row=row, sticky=tk.NSEW)
        self.B.insert(tk.INSERT, str(self.pixel.value.b))

        self.G.edit_modified(False)
        self.B.edit_modified(False)

        self.ValueType = tk.Button(frame, text=pixel.type.value[1].type.name, bg=pixel.type.value[1].type.value[1])
        self.ValueType["command"] = self.click_type
        self.ValueType.grid(column=4, row=row, sticky=tk.NSEW)

        values = self.pixel.value.get_values()
        self.valueA = None
        self.valueB = None

        if 0 < len(values):
            self.valueA = tk.Text(frame, width=6, height=1)
            self.valueA.grid(column=5, row=row, sticky=tk.NSEW)
            self.valueA.insert(tk.INSERT, str(self.pixel.value.get_values()[0]))
            self.valueA.edit_modified(False)

        if 1 < len(values):
            self.valueB = tk.Text(frame, width=6, height=1)
            self.valueB.grid(column=6, row=row, sticky=tk.NSEW)
            self.valueB.insert(tk.INSERT, str(self.pixel.value.get_values()[1]))
            self.valueB.edit_modified(False)

        self.up_button = tk.Button(frame, text="∧", bg="LightBlue")
        self.up_button["command"] = self.click_up
        self.up_button.grid(column=7, row=row, sticky=tk.NSEW)

        self.down_button = tk.Button(frame, text="∨", bg="LightBlue")
        self.down_button["command"] = self.click_down
        self.down_button.grid(column=8, row=row, sticky=tk.NSEW)

        self.on_value_change()
        self.on_color_change()

    def key_event(self):
        if self.G.edit_modified() or self.B.edit_modified():
            self.on_color_change()
            self.G.edit_modified(False)
            self.B.edit_modified(False)
        if self.valueA is not None:
            if self.valueA.edit_modified():
                self.on_value_change()
                self.valueA.edit_modified(False)
        if self.valueB is not None:
            if self.valueB.edit_modified():
                self.on_value_change()
                self.valueB.edit_modified(False)

    def on_value_change(self):
        value_a = 0.0
        value_b = 0.0
        try:
            if self.valueA is not None: value_a = float(self.valueA.get('1.0', tk.END))
            if self.valueB is not None: value_b = float(self.valueB.get('1.0', tk.END))
        except ValueError:
            pass

        self.pixel.value.set_value(value_a, value_b)
        self.G.delete('1.0', tk.END)
        self.G.insert(tk.INSERT, int(self.pixel.value.g))
        self.G.edit_modified(False)

        self.B.delete('1.0', tk.END)
        self.B.insert(tk.INSERT, int(self.pixel.value.b))
        self.B.edit_modified(False)

    def on_color_change(self):
        g = 0
        b = 0
        try:
            g = int(self.G.get('1.0', tk.END))
            b = int(self.B.get('1.0', tk.END))
        except ValueError:
            pass
        g = 0 if g < 0 else 255 if 255 < g else g
        b = 0 if g < 0 else 255 if 255 < g else g
        self.pixel.value.set_colors(g, b)
        values = self.pixel.value.get_values()
        if 0 < len(values):
            value = float("{:.2f}".format(values[0]))
            self.valueA.delete('1.0', tk.END)
            self.valueA.insert(tk.INSERT, int(values[0]) if int(values[0]) == value else value)
            self.valueA.edit_modified(False)

        if 1 < len(values):
            value = float("{:.3f}".format(values[1]))
            self.valueB.delete('1.0', tk.END)
            self.valueB.insert(tk.INSERT, int(values[1]) if int(values[1]) == value else value)
            self.valueB.edit_modified(False)

    def click_meta(self):
        self.label["text"] = self.pixel.type.value[2]

    def click_type(self):
        self.label["text"] = self.pixel.type.value[1].get_help()

    def click_x(self):
        self.editor.remove_meta_pixel(self.pixel)

    def click_up(self):
        self.editor.move_meta_pixel_up(self.pixel)

    def click_down(self):
        self.editor.move_meta_pixel_down(self.pixel)

    def remove(self):
        self.meta_pixel_button.destroy()
        self.G.destroy()
        self.B.destroy()
        self.ValueType.destroy()
        if self.valueA is not None: self.valueA.destroy()
        if self.valueB is not None: self.valueB.destroy()
        self.remove_button.destroy()
        self.up_button.destroy()
        self.down_button.destroy()


class Editor:
    def __init__(self):
        # Image stuff
        self.icon = """iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAABhWlDQ1
 BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9bpUVbHCwoIpihOlkQFXGUKhbBQmkrtOpgcukXNGlIUl
 wcBdeCgx+LVQcXZ10dXAVB8APEydFJ0UVK/F9SaBHjwXE/3t173L0DvI0KU4yuCUBRTT0VjwnZ3K
 rgf0UvBhBACCMiM7REejED1/F1Dw9f76I8y/3cnyMk5w0GeATiOabpJvEG8cymqXHeJw6zkigTnx
 OP63RB4keuSw6/cS7a7OWZYT2TmicOEwvFDpY6mJV0hXiaOCIrKuV7sw7LnLc4K5Uaa92TvzCYV1
 fSXKc5jDiWkEASAiTUUEYFJqK0qqQYSNF+zMU/ZPuT5JLIVQYjxwKqUCDafvA/+N2tUZiadJKCMa
 D7xbI+RgH/LtCsW9b3sWU1TwDfM3Cltv3VBjD7SXq9rUWOgL5t4OK6rUl7wOUOMPikibpoSz6a3k
 IBeD+jb8oB/bdAz5rTW2sfpw9AhrpavgEODoGxImWvu7w70Nnbv2da/f0AYUpyoBrfN9UAAAAGYk
 tHRABYAFgAWPY/mbsAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfkCxcIFCWQpv+pAAAAGX
 RFWHRDb21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAAdFJREFUeNrt3a1OA0EUhuFdUo9BIi
 AkGILAQ4LFI1YgoIQbQIAA2YpeRAmyDtkQDAnFYggGBAgMQTS9AriBOWKShaXleeXJdNuZN2fzZf
 anZVVVBZpjzhIQQAAIIAAEEAACCAABBOD3aOV+YDAYfKXqVVWVllMHEAACCAAB05+CorSzf3qeHH
 /Z60hHOoAAEEAACJiBFBSxtbqcTkGZaQo6gAAQQAABaJQy9+7oulLNZ2+jlgksnDykJ1amt6D6/f
 6PLmi73c76PTrAKYgAEEAAGqJV14F2NteS9eHoKVm/fpnU88VHK7Uc5u75NVmP9r6i8cXFhQ5wCg
 IBBICAqU5B0Z7P7dJ6cvz26DFZj/Ze9g4PG5lwmF4aGq8DnIIIAAEE4K+loFzCdBSknWjvaPfguJ
 bUcdnrJOsf91c6AAQQAAIIQI0p6GY8TtbP5heT9W5wpWw4qmePKHo27a/dra0DCCAABBCAhiiLos
 i68hWlnYju5D0rpUTM6nuKdAABBIAAAjAtKSgiSkdRCsplVt87pAMIIAAEEICGyL4ilpt2vDVRBx
 AAAggAAdOVgrbfHq2ODiAABBAAAmaX0n/K6wACQAABIIAAEEAACCAABPwbvgGpc2uukqDTSwAAAA
 BJRU5ErkJggg=="""
        self.image = None

        self.meta_pixel_keys = []
        self.meta_pixels = {}

        self.pixels = None
        # self.image.save("pixel_grid.png")

        # Gui Stuff
        self.root = tk.Tk()
        self.icon = tk.PhotoImage(data=self.icon)
        self.frame1 = tk.Frame(self.root, borderwidth=4, relief="groove")
        self.frame1.grid(column=0, row=0, sticky=tk.NSEW)

        self.frame2 = tk.Frame(self.root, borderwidth=0)
        self.frame2.grid(column=0, row=1, sticky=tk.NSEW)

        self.label = tk.Label(self.frame2, text="", justify=tk.LEFT, pady=0, borderwidth=1, wraplength=300)
        self.label.pack()

        tk.Label(self.frame1, text="X", justify=tk.LEFT, pady=0, borderwidth=1, bg="red"). \
            grid(column=0, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="MetaPixelType", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=1, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="Green", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=2, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="Blue", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=3, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="ValueType", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=4, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="Value A", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=5, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="Value B", justify=tk.LEFT, pady=0, borderwidth=1, bg="gray"). \
            grid(column=6, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="▲", justify=tk.LEFT, pady=0, borderwidth=1, bg="Aqua"). \
            grid(column=7, row=0, sticky=tk.NSEW)

        tk.Label(self.frame1, text="▼", justify=tk.LEFT, pady=0, borderwidth=1, bg="Aqua"). \
            grid(column=8, row=0, sticky=tk.NSEW)

        self.frame3 = tk.Frame(self.root, borderwidth=0)
        self.frame3.grid(column=1, row=0, sticky=tk.NSEW)

        button = tk.Button(self.frame3, text="+", justify=tk.LEFT, pady=0, borderwidth=1, bg="LightGreen")
        button["command"] = self.click_add
        button.grid(column=0, row=0, sticky=tk.NSEW)

        button = tk.Button(self.frame3, text="Save", justify=tk.LEFT, pady=0, borderwidth=1, bg="Lime")
        button["command"] = self.click_save
        button.grid(column=0, row=1, sticky=tk.NSEW)

        button = tk.Button(self.frame3, text="Load", justify=tk.LEFT, pady=0, borderwidth=1, bg="Orange")
        button["command"] = self.click_load
        button.grid(column=0, row=3, sticky=tk.NSEW)

        # Final Gui pixel stuff
        self.metas = []
        self.gen_meta_pixels()

        self.root.bind_all('<KeyPress>', self.key_stuff)
        self.root.bind_all('<KeyRelease>', self.key_stuff)

        self.root.title("DuckGame hat MetaPixel Editor")
        self.root.iconphoto(False, self.icon)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.resizable(width=False, height=False)
        self.add_open = False
        self.root.mainloop()

    def key_stuff(self, _):
        for meta in self.metas:
            meta.key_event()

    def click_save(self):
        if self.image is None:
            showinfo(title="Can't Save MetaPixels", message="You haven't loaded a hat yet so you aren't able to save a "
                                                          "hat")
            return
        image_file = asksaveasfile(title="Select file to save as", filetypes=[('PNG Files', '*.png')])
        if image_file is None: return
        for p in range(len(self.meta_pixels)):
            meta_pixel = self.meta_pixels[self.meta_pixel_keys[p]]
            assert isinstance(meta_pixel, MetaPixel)
            self.pixels[96, p] = meta_pixel.get_rgba()
        self.image.save(image_file.name)

        image_file.close()

    def click_load(self):
        image_file = askopenfile(mode='r', title="Select file", filetypes=[('PNG Files', '*.png')])
        if image_file is None: return
        try:
            image = Image.open(image_file.name)
        except PIL.UnidentifiedImageError:
            showinfo(title="Can't Open "+image_file.name, message="Wasn't able to identify file as image")
            return

        if image.format != "PNG":
            showinfo(title="Can't Open "+image_file.name, message="Couldn't open file because it wasn't a PNG file")
            return

        if image.size != (97, 56):
            showinfo(title="Can't Open "+image_file.name, message="Couldn't open file because duck game hats need to be"
                                                                  " (97, 56) pixels in size")
            return

        if image.mode != "RGBA":
            showinfo(title="Can't Open "+image_file.name, message="Couldn't open file because it's color mode is "
                                                                  "wrong")
            return

        self.meta_pixel_keys = []
        self.meta_pixels = {}
        self.image = image

        image_file.close()

        self.pixels = self.image.load()
        self.load()
        self.gen_meta_pixels()

    def click_add(self):
        if self.add_open: return
        if self.image is None:
            showinfo(title="Can't Add MetaPixel", message="You haven't loaded a hat yet so you aren't able to add a "
                                                          "MetaPixel")
            return
        root = tk.Tk()

        class Option:
            def __init__(self, pixel_type: MetaPixelType, editor: Editor, r: tk.Tk):
                self.root = r
                self.editor = editor
                self.button = tk.Button(root, text=pixel_type.name, justify=tk.LEFT, pady=0, borderwidth=1,
                                        bg=MetaPixel.COLORS.get(pixel_type.value[3]))
                self.button.pack(fill="x")
                self.button["command"] = self.click

                self.meta_pixel_type = pixel_type

            def click(self):
                meta_pixel = MetaPixel(self.meta_pixel_type, 0, 0)
                self.editor.meta_pixel_keys.append(self.meta_pixel_type)
                self.editor.meta_pixels[self.meta_pixel_type] = meta_pixel
                self.editor.gen_meta_pixels()
                self.editor.add_open = False
                self.root.quit()
                self.root.destroy()

        root.resizable(width=False, height=False)
        for meta_pixel_type in MetaPixel.TYPES.values():
            if self.meta_pixel_keys.__contains__(meta_pixel_type): continue
            Option(meta_pixel_type, self, root)

        self.add_open = True

        root.mainloop(1)
        self.add_open = False

    def load(self):
        for p in range(56):
            r, g, b, a = self.pixels[96, p]

            meta_pixel_type = MetaPixel.TYPES.get(r)
            if meta_pixel_type is not None and not self.meta_pixel_keys.__contains__(meta_pixel_type):
                self.meta_pixel_keys.append(meta_pixel_type)
                self.meta_pixels[meta_pixel_type] = MetaPixel(meta_pixel_type, g, b)
            else: self.pixels[96, p] = 0, 0, 0, 0

    def add_meta_pixel(self, meta_pixel: MetaPixel):
        self.metas.append(MetaPixelGui(meta_pixel, len(self.metas)+1, self.frame1, self.label, self))

    def gen_meta_pixels(self):
        for meta in self.metas:
            meta.remove()
        self.metas = []
        for item in self.meta_pixels.values(): self.add_meta_pixel(item)

    def remove_meta_pixel(self, meta_pixel: MetaPixel):
        if self.meta_pixels.__contains__(meta_pixel.type):
            del self.meta_pixels[meta_pixel.type]
            self.meta_pixel_keys.remove(meta_pixel.type)
            self.gen_meta_pixels()

    def move_meta_pixel_up(self, meta_pixel: MetaPixel):
        if self.meta_pixels.__contains__(meta_pixel.type):
            for i in range(len(self.meta_pixels)):
                if self.meta_pixel_keys[i] == meta_pixel.type:
                    u = i-1 if 0 < i else len(self.meta_pixel_keys)-1
                    move_down = self.meta_pixel_keys[u]
                    self.meta_pixel_keys[i] = move_down
                    self.meta_pixel_keys[u] = meta_pixel.type

                    self.metas[i].remove()
                    self.metas[u].remove()

                    new_meta_pixels = {}
                    for key in self.meta_pixel_keys: new_meta_pixels[key] = self.meta_pixels[key]
                    self.meta_pixels = new_meta_pixels

                    self.metas[i] = MetaPixelGui(self.meta_pixels[move_down], i+1, self.frame1, self.label, self)
                    self.metas[u] = MetaPixelGui(meta_pixel, u+1, self.frame1, self.label, self)
                    return

    def move_meta_pixel_down(self, meta_pixel: MetaPixel):
        if self.meta_pixels.__contains__(meta_pixel.type):
            for i in range(len(self.meta_pixels)):
                if self.meta_pixel_keys[i] == meta_pixel.type:
                    u = i+1 if i < len(self.meta_pixel_keys) - 1 else 0
                    move_down = self.meta_pixel_keys[u]
                    self.meta_pixel_keys[i] = move_down
                    self.meta_pixel_keys[u] = meta_pixel.type

                    self.metas[i].remove()
                    self.metas[u].remove()

                    new_meta_pixels = {}
                    for key in self.meta_pixel_keys: new_meta_pixels[key] = self.meta_pixels[key]
                    self.meta_pixels = new_meta_pixels

                    self.metas[i] = MetaPixelGui(self.meta_pixels[move_down], i+1, self.frame1, self.label, self)
                    self.metas[u] = MetaPixelGui(meta_pixel, u+1, self.frame1, self.label, self)
                    return

    def on_closing(self):
        if self.image is None:
            self.root.destroy()
            return
        if askokcancel("Quit Prompt", "Do you want to exit? Any unsaved data will be lost!"): self.root.destroy()


if __name__ == '__main__':
    Editor()
