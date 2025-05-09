#导入库
import os
os.system("cls")
import pygame
import pathlib
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import threading
import random
import time
import sys

folder = pathlib.Path(__file__).parent.resolve()

app = Ursina()

window.exit_button.visible = False
window.vsync = False

texture = load_texture("assats/modles/common_car/GFX.png")

class Car(Entity):
    def __init__(self):
        super().__init__(
            model="assets/modles/common_car/car",
            color=color.white,
            texture=texture,
            scale=(0.1,0.1,0.1),
        )

car = Car()
app.run()