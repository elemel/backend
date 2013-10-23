from bromine.maths import clamp, mix

import colorsys
import math
import random

class ConstantGenerator(object):
    def __init__(self, value=0.0):
        self._value = value

    def generate(self):
        return self._value

class UniformGenerator(object):
    def __init__(self, min_value=-1.0, max_value=1.0, random=random):
        self._min_value = min_value
        self._max_value = max_value
        self._random = random

    def generate(self):
        return self._random.uniform(self._min_value, self._max_value)

class GaussGenerator(object):
    def __init__(self, mu=0.0, sigma=0.0, random=random):
        self._mu = mu
        self._sigma = sigma
        self._random = random

    def generate(self):
        return self._random.gauss(self._mu, self._sigma)

class ClampedGaussGenerator(object):
    def __init__(self, mu=0.0, sigma=0.0, random=random):
        self._mu = mu
        self._sigma = sigma
        self._random = random

    def generate(self):
        return clamp(self._random.gauss(self._mu, self._sigma),
                     self._mu - 2.0 * self._sigma,
                     self._mu + 2.0 * self._sigma)

class ColorGenerator(object):
    def __init__(self, hue_generator=UniformGenerator(0.0, 1.0),
                 lightness_generator=ConstantGenerator(0.5),
                 saturation_generator=ConstantGenerator(1.0),
                 alpha_generator=ConstantGenerator(1.0)):
        self._hue_generator = hue_generator
        self._lightness_generator = lightness_generator
        self._saturation_generator = saturation_generator
        self._alpha_generator = alpha_generator

    def generate(self):
        hue = self._hue_generator.generate()
        lightness = self._lightness_generator.generate()
        saturation = self._saturation_generator.generate()
        alpha = self._alpha_generator.generate()

        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)

        return red, green, blue, alpha
