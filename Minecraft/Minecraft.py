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

zxi = 17
print('1.创建一个新世界\n2.游玩过去的世界\n<输入数字>')
a = input()
if a == '1':
    m = input('新世界的名字:')
    z = input('新世界的种子:')
    print(z.isdigit())
    if z.isdigit():
        zc = int(z)
    else:
        zc = random.randint(-99999999999, 99999999999)
    with open(os.path.join(folder, 'saves', m + '.ini'), "w") as f:
        f.write(str(zc))
    asas = ''
if a == '2':
    am = input('过去世界的名字:')
    asas = input('按下回车键开始:')
    if asas == '':
        with open(os.path.join(folder, 'saves', am + '.ini'), "r") as f:
            mmm = f.read()
        zc = int(mmm)
    elif asas == '/middle_ages':
        with open(os.path.join(folder, 'saves', am + '.ini'), "r") as f:
            mmm = f.read()
            zc = int(mmm)
    else:
        sys.exit()

#创建窗口

app = Ursina()

window.exit_button.visible = False  #隐藏关闭按钮
window.vsync = False  #禁用垂直同步

#导入贴图
if asas == '/middle_ages':
    grass = load_texture('assets/textures-middle_ages/grass_block_texture.png')
    stone = load_texture('assets/textures-middle_ages/stone_block_texture.png')
    sand = load_texture('assets/textures-middle_ages/sand_block_texture.png')
    pland = load_texture('assets/textures-middle_ages/pland_block_texture.png')
    dirt = load_texture('assets/textures-middle_ages/dirt_block_texture.png')
    mouseo = load_texture('assets/textures-middle_ages/mouse.png')
    wood = load_texture('assets/textures-middle_ages/wood_block_texture.png')
    leaves = load_texture('assets/textures-middle_ages/leaves_block_texture.png')
else:
    grass = load_texture('assets/textures/grass_block_texture.png')
    stone = load_texture('assets/textures/stone_block_texture.png')
    sand = load_texture('assets/textures/sand_block_texture.png')
    pland = load_texture('assets/textures/pland_block_texture.png')
    dirt = load_texture('assets/textures/dirt_block_texture.png')
    mouseo = load_texture('assets/textures/mouse.png')
    wood = load_texture('assets/textures/wood_block_texture.png')
    leaves = load_texture('assets/textures/leaves_block_texture.png')

block_pick = 1

# 初始化
pygame.init()
pygame.mixer.init()

# 导入音效
sound_dig = {}
def sound():
    global sound_dig
    def load_sound():
        for i in range(1,5):
            sound_dig[f'grass_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'grass_block_dig_{i}.ogg'))
            sound_dig[f'grave_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'grave_block_dig_{i}.ogg'))
            sound_dig[f'stone_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'stone_block_dig_{i}.ogg'))
            sound_dig[f'sand_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'sand_block_dig_{i}.ogg'))
            sound_dig[f'pland_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'pland_block_dig_{i}.ogg'))
            sound_dig[f'leaves_block_{i}'] = pygame.mixer.Sound(os.path.join(folder, 'assets', 'sounds', f'leaves_block_dig_{i}.ogg'))
    sound_thread = threading.Thread(target=load_sound,daemon=True)
    sound_thread.start()

sound()

# 主代码
blocks = {}
visible_blocks = set()

scene.fog_color = color.white
scene.fog_density = 0.02
xyz = 0

frame_counter = 0

def update():
    global block_pick,frame_counter,xyz,render_distance
    frame_counter += 1

    #恢复玩家位置,玩家面向方向
    if a == '2':
        if xyz == 0:
            with open(os.path.join(folder, 'saves', am + '.ini3'), "r") as f:
                rrr = f.read()
            if len(rrr) > 0:
                rrr = rrr.split('+')
                player.position = Vec3(float(rrr[0]), float(rrr[1]), float(rrr[2]))
                xyz = 1
            with open(os.path.join(folder, 'saves', am + '.ini4'), "r") as f:
                rrr = f.read()
            if len(rrr) > 0:
                rrr = rrr.split('+')
                player.rotation = Vec3(float(rrr[0]), float(rrr[1]), float(rrr[2]))
                xyz = 1
            xyz = 1

    if int(player.position.y) < -45:
        player.position = Vec3(0, 0, 0)
    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4
    if held_keys['5']: block_pick = 5
    if held_keys['6']: block_pick = 6
    if held_keys['7']: block_pick = 7

    if held_keys['left mouse'] or held_keys['right mouse']:
        block_hand.active()
    else:
        block_hand.passive()

    update_visible = threading.Thread(target=update_visible_blocks,daemon=True)
    update_visible.start()

    # 限制渲染距离
    render_distance = 8
    for pos, block in blocks.items():
        if block and not block.is_empty():  # 检查实体是否存在
            distance = (Vec3(pos) - player.position).length()
            block.visible = distance <= render_distance

def update_visible_blocks():
    global visible_blocks
    player_pos = player.position
    render_distance = 8  # 渲染距离

    # 延迟更新
    def ppos():
        for pos in list(visible_blocks):
            block = blocks.get(pos)
            if block:
                distance = (Vec3(pos) - player_pos).length()
                block.visible = distance <= render_distance
    ppos = threading.Thread(target=ppos,daemon=True)
    ppos.start()

def input(key):
    if key == 'escape':
        #保存玩家位置
        if a == '2':
            with open(os.path.join(folder, 'saves', am + '.ini3'), "w") as f:
                f.write(str(player.position.x) + '+' + str(player.position.y) + '+' + str(player.position.z))
        if a == '1':
            with open(os.path.join(folder, 'saves', m + '.ini3'), "w") as f:
                f.write(str(player.position.x) + '+' + str(player.position.y) + '+' + str(player.position.z))
        #保存玩家面向方向
        if a == '2':
            with open(os.path.join(folder, 'saves', am + '.ini4'), "w") as f:
                f.write(str(player.rotation.x) + '+' + str(player.rotation.y) + '+' + str(player.rotation.z))
        if a == '1':
            with open(os.path.join(folder, 'saves', m + '.ini4'), "w") as f:
                f.write(str(player.rotation.x) + '+' + str(player.rotation.y) + '+' + str(player.rotation.z))
        quit()

class WhiteCylinder(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='cylinder',
            texture = "assets/textures/cylinder",
            scale=(14, 50, 14),
            position=(0, 0, 0),
            double_sided=True
        )

    def update(self):
        self.position = player.position

class Block(Button):
    def __init__(self, position, texture=grass):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/modles/block',
            origin_y=0.5,
            texture=texture,
            color=color.white,
            highlight_color=color.gray,
            visible=False
        )
        blocks[position] = self

    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':
                if block_pick == 1:
                    block = Block(position=self.position + mouse.normal, texture=grass)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'grass')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'grass')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['grass_block_1'].play()
                    if sss == 2:
                        sound_dig['grass_block_2'].play()
                    if sss == 3:
                        sound_dig['grass_block_3'].play()
                    if sss == 4:
                        sound_dig['grass_block_4'].play()
                if block_pick == 2:
                    block = Block(position=self.position + mouse.normal, texture=stone)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'stone')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'stone')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['stone_block_1'].play()
                    if sss == 2:
                        sound_dig['stone_block_2'].play()
                    if sss == 3:
                        sound_dig['stone_block_3'].play()
                    if sss == 4:
                        sound_dig['stone_block_4'].play()
                if block_pick == 3:
                    block = Block(position=self.position + mouse.normal, texture=sand)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'sand')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'sand')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['sand_block_1'].play()
                    if sss == 2:
                        sound_dig['sand_block_2'].play()
                    if sss == 3:
                        sound_dig['sand_block_3'].play()
                    if sss == 4:
                        sound_dig['sand_block_4'].play()
                if block_pick == 4:
                    block = Block(position=self.position + mouse.normal, texture=pland)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'pland')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'pland')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['pland_block_1'].play()
                    if sss == 2:
                        sound_dig['pland_block_2'].play()
                    if sss == 3:
                        sound_dig['pland_block_3'].play()
                    if sss == 4:
                        sound_dig['pland_block_4'].play()
                if block_pick == 5:
                    block = Block(position=self.position + mouse.normal, texture=dirt)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'dirt')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'dirt')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['grave_block_1'].play()
                    if sss == 2:
                        sound_dig['grave_block_2'].play()
                    if sss == 3:
                        sound_dig['grave_block_3'].play()
                    if sss == 4:
                        sound_dig['grave_block_4'].play()
                if block_pick == 6:
                    block = Block(position=self.position + mouse.normal, texture=wood)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'wood')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'wood')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['pland_block_1'].play()
                    if sss == 2:
                        sound_dig['pland_block_2'].play()
                    if sss == 3:
                        sound_dig['pland_block_3'].play()
                    if sss == 4:
                        sound_dig['pland_block_4'].play()
                if block_pick == 7:
                    block = Block(position=self.position + mouse.normal, texture=leaves)
                    if a == '2':
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'leaves')
                    if a == '1':
                        with open(os.path.join(folder, 'saves', m + '.ini2'), "a") as f:
                            f.write('/' + str(self.position.x) + '+' + str(self.position.y + 1) + '+' + str(self.position.z) + '+' + 'leaves')
                    sss = random.randint(1, 4)
                    if sss == 1:
                        sound_dig['leaves_block_1'].play()
                    if sss == 2:
                        sound_dig['leaves_block_2'].play()
                    if sss == 3:
                        sound_dig['leaves_block_3'].play()
                    if sss == 4:
                        sound_dig['leaves_block_4'].play()
            if key == 'left mouse down':

                block_position = self.position

                # 从blocks字典中移除方块
                if block_position in blocks:
                    del blocks[block_position]
                destroy(self)

                sss = random.randint(1, 4)
                if a == '2':
                    with open(os.path.join(folder, 'saves', am + '.ini2'), "r") as f:
                        rrc = f.read()
                    if len(rrc) > 0:
                        rrc = rrc.split('/')
                        del rrc[0]
                        updated_rrc = []
                        for i in rrc:
                            i3 = i.split('+')
                            saved_block_position = (float(i3[0]), float(i3[1]), float(i3[2]))
                            if saved_block_position != block_position:
                                updated_rrc.append(i)
                        with open(os.path.join(folder, 'saves', am + '.ini2'), "w") as f:
                            f.write('/' + '/'.join(updated_rrc))
                if self.texture == grass:
                    if sss == 1:
                        sound_dig['grass_block_1'].play()
                    if sss == 2:
                        sound_dig['grass_block_2'].play()
                    if sss == 3:
                        sound_dig['grass_block_3'].play()
                    if sss == 4:
                        sound_dig['grass_block_4'].play()
                if self.texture == dirt:
                    if sss == 1:
                        sound_dig['grave_block_1'].play()
                    if sss == 2:
                        sound_dig['grave_block_2'].play()
                    if sss == 3:
                        sound_dig['grave_block_3'].play()
                    if sss == 4:
                        sound_dig['grave_block_4'].play()
                if self.texture == stone:
                    if sss == 1:
                        sound_dig['stone_block_1'].play()
                    if sss == 2:
                        sound_dig['stone_block_2'].play()
                    if sss == 3:
                        sound_dig['stone_block_3'].play()
                    if sss == 4:
                        sound_dig['stone_block_4'].play()
                if self.texture == sand:
                    if sss == 1:
                        sound_dig['sand_block_1'].play()
                    if sss == 2:
                        sound_dig['sand_block_2'].play()
                    if sss == 3:
                        sound_dig['sand_block_3'].play()
                    if sss == 4:
                        sound_dig['sand_block_4'].play()
                if self.texture == pland:
                    if sss == 1:
                        sound_dig['pland_block_1'].play()
                    if sss == 2:
                        sound_dig['pland_block_2'].play()
                    if sss == 3:
                        sound_dig['pland_block_3'].play()
                    if sss == 4:
                        sound_dig['pland_block_4'].play()
                if self.texture == wood:
                    if sss == 1:
                        sound_dig['pland_block_1'].play()
                    if sss == 2:
                        sound_dig['pland_block_2'].play()
                    if sss == 3:
                        sound_dig['pland_block_3'].play()
                    if sss == 4:
                        sound_dig['pland_block_4'].play()
                if self.texture == leaves:
                    if sss == 1:
                        sound_dig['leaves_block_1'].play()
                    if sss == 2:
                        sound_dig['leaves_block_2'].play()
                    if sss == 3:
                        sound_dig['leaves_block_3'].play()
                    if sss == 4:
                        sound_dig['leaves_block_4'].play()

class Block_hand(Entity):
    def __init__(self, texture=grass):
        super().__init__(
            parent=camera.ui,
            model='assets/modles/block',
            origin_y=0.5,
            texture=texture,
            scale=0.27,
            rotation=Vec3(150, 100, 150),
            position=Vec2(0.9, -0.5)
        )

    def input(self, key):
        if block_pick == 1:
            self.texture = grass
        if block_pick == 2:
            self.texture = stone
        if block_pick == 3:
            self.texture = sand
        if block_pick == 4:
            self.texture = pland
        if block_pick == 5:
            self.texture = dirt
        if block_pick == 6:
            self.texture = wood
        if block_pick == 7:
            self.texture = leaves

    def active(self):
        self.position = Vec2(0.7, -0.6)

    def passive(self):
        self.position = Vec2(0.9, -0.5)

class Mouseo(Entity):
    def __init__(self, texture=mouseo):
        super().__init__(
            parent=camera.ui,
            model='quad',
            texture=texture,
            scale=0.05,
            position=Vec3(0, 0, 0),
        )

class Particle(Entity):
    def __init__(self, texture='assets/particles/particle',scale=1,rotation = (0,2,0),position = (0,2,0)):
        super().__init__(
            parent=scene,
            model='assets/modles/particle',
            texture=texture,
            scale=scale,
            double_sided=True,
            rotation = rotation,
            position = position
        )

def create_chunk(x, z, size=16):
    vertices = []
    uvs = []
    normals = []
    for i in range(size):
        for j in range(size):
            y = floor(noise([x + i / 24, z + j / 24]) * 8)
            block_vertices, block_uvs, block_normals = create_block_mesh(x + i, y, z + j)
            vertices.extend(block_vertices)
            uvs.extend(block_uvs)
            normals.extend(block_normals)
    chunk = Entity(
        model=Mesh(vertices=vertices, uvs=uvs, normals=normals),
        texture=grass,
        position=(x, 0, z)
    )
    return chunk

def create_block_mesh(x, y, z):
    vertices = [
        # Front face
        Vec3(x, y, z), Vec3(x + 1, y, z), Vec3(x + 1, y + 1, z), Vec3(x, y + 1, z),
        # Back face
        Vec3(x, y, z + 1), Vec3(x + 1, y, z + 1), Vec3(x + 1, y + 1, z + 1), Vec3(x, y + 1, z + 1),
        # Left face
        Vec3(x, y, z), Vec3(x, y, z + 1), Vec3(x, y + 1, z + 1), Vec3(x, y + 1, z),
        # Right face
        Vec3(x + 1, y, z), Vec3(x + 1, y, z + 1), Vec3(x + 1, y + 1, z + 1), Vec3(x + 1, y + 1, z),
        # Top face
        Vec3(x, y + 1, z), Vec3(x + 1, y + 1, z), Vec3(x + 1, y + 1, z + 1), Vec3(x, y + 1, z + 1),
        # Bottom face
        Vec3(x, y, z), Vec3(x + 1, y, z), Vec3(x + 1, y, z + 1), Vec3(x, y, z + 1),
    ]
    uvs = [
        # Front face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
        # Back face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
        # Left face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
        # Right face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
        # Top face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
        # Bottom face
        Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1),
    ]
    normals = [
        # Front face
        Vec3(0, 0, -1), Vec3(0, 0, -1), Vec3(0, 0, -1), Vec3(0, 0, -1),
        # Back face
        Vec3(0, 0, 1), Vec3(0, 0, 1), Vec3(0, 0, 1), Vec3(0, 0, 1),
        # Left face
        Vec3(-1, 0, 0), Vec3(-1, 0, 0), Vec3(-1, 0, 0), Vec3(-1, 0, 0),
        # Right face
        Vec3(1, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 0), Vec3(1, 0, 0),
        # Top face
        Vec3(0, 1, 0), Vec3(0, 1, 0), Vec3(0, 1, 0), Vec3(0, 1, 0),
        # Bottom face
        Vec3(0, -1, 0), Vec3(0, -1, 0), Vec3(0, -1, 0), Vec3(0, -1, 0),
    ]
    return vertices, uvs, normals

noise = PerlinNoise(octaves=2, seed=zc)
if a == '1':
    for z in range(zxi):
        for x in range(zxi):
            y = floor(noise([x / 24, z / 24]) * 8)
            Block(position=(x, y, z),texture=grass)
            with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                f.write('/' + str(x) + '+' + str(y + 1) + '+' + str(z) + '+' + 'grass')
            Block(position=(x, y - 1, z), texture=dirt)
            with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                f.write('/' + str(x) + '+' + str(y - 1 + 1) + '+' + str(z) + '+' + 'dirt')
            Block(position=(x, y - 2, z), texture=dirt)
            with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                f.write('/' + str(x) + '+' + str(y - 2 + 1) + '+' + str(z) + '+' + 'dirt')
            Block(position=(x, y - 3, z), texture=stone)
            with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                f.write('/' + str(x) + '+' + str(y - 3 + 1) + '+' + str(z) + '+' + 'stone')
            if random.randint(0,35) == 1:
                for i in range(4):
                    Block(position=(x,y+i+1,z),texture=wood)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'wood')
                for i in range(4,7):
                    Block(position=(x,y+i+1,z),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'leaves')
                for i in range(4,6):
                    Block(position=(x-1,y+i+1,z),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x-1) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'leaves')
                    Block(position=(x-2,y+i+1,z),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x-2) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'leaves')

                    Block(position=(x+1,y+i+1,z),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x+1) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'leaves')
                    Block(position=(x+2,y+i+1,z),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x+2) + '+' + str(y+i+1) + '+' + str(z) + '+' + 'leaves')

                    Block(position=(x,y+i+1,z-1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z-1) + '+' + 'leaves')
                    Block(position=(x,y+i+1,z-2),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z-2) + '+' + 'leaves')

                    Block(position=(x,y+i+1,z+1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z+1) + '+' + 'leaves')
                    Block(position=(x,y+i+1,z+2),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x) + '+' + str(y+i+1) + '+' + str(z+2) + '+' + 'leaves')
                    

                    Block(position=(x-1,y+i+1,z-1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x-1) + '+' + str(y+i+1) + '+' + str(z-1) + '+' + 'leaves')

                    Block(position=(x+1,y+i+1,z+1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x+1) + '+' + str(y+i+1) + '+' + str(z+1) + '+' + 'leaves')

                    Block(position=(x-1,y+i+1,z+1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x-1) + '+' + str(y+i+1) + '+' + str(z+1) + '+' + 'leaves')
                    
                    Block(position=(x+1,y+i+1,z-1),texture=leaves)
                    with open('Minecraft/saves/' + m + '.ini2', "a") as f:
                        f.write('/' + str(x+1) + '+' + str(y+i+1) + '+' + str(z-1) + '+' + 'leaves')

if a == '2':
    with open(os.path.join(folder, 'saves', am + '.ini2'), "r") as f:
        rrr = f.read()
    if len(rrr) >= 1:
        rrr = rrr.split('/')
        del rrr[0]
        for i2 in rrr:
            i3 = i2.split('+')
            position = (float(i3[0]), float(i3[1]), float(i3[2]))
            texture = None
            if i3[3] == 'grass':
                texture = grass
            elif i3[3] == 'stone':
                texture = stone
            elif i3[3] == 'sand':
                texture = sand
            elif i3[3] == 'pland':
                texture = pland
            elif i3[3] == 'dirt':
                texture = dirt
            elif i3[3] == 'wood':
                texture = wood
            elif i3[3] == 'leaves':
                texture = leaves
            if texture:
                blocks[position] = Block(position=position, texture=texture)

block_model = Mesh(vertices=[], uvs=[], normals=[])

def create_block(position, texture):
    block = Block(position=position, texture=texture)
    blocks[position] = block
    return block

def threaded_load_blocks(file_path):
    def load():
        with open(file_path, "r") as f:
            rrr = f.read()
        if len(rrr) >= 1:
            rrr = rrr.split('/')
            del rrr[0]
            block_data = []
            for i2 in rrr:
                i3 = i2.split('+')
                position = (float(i3[0]), float(i3[1]), float(i3[2]))
                texture = None
                if i3[3] == 'grass':
                    texture = grass
                elif i3[3] == 'stone':
                    texture = stone
                elif i3[3] == 'sand':
                    texture = sand
                elif i3[3] == 'pland':
                    texture = pland
                elif i3[3] == 'dirt':
                    texture = dirt
                elif i3[3] == 'wood':
                    texture = wood
                elif i3[3] == 'leaves':
                    texture = leaves
                if texture:
                    block_data.append((position, texture))
            #在主线程中创建实体
            invoke(create_blocks, block_data, delay=0)

    load_thread = threading.Thread(target=load,daemon=True)
    load_thread.start()

def create_blocks(block_data):
    vertices = []
    uvs = []
    normals = []
    for position, texture in block_data:
        block_vertices, block_uvs, block_normals = create_block_mesh(*position)
        vertices.extend(block_vertices)
        uvs.extend(block_uvs)
        normals.extend(block_normals)
    combined_model = Mesh(vertices=vertices, uvs=uvs, normals=normals)
    Entity(model=combined_model, texture=grass)

# 运行
player = FirstPersonController()
white_cylinder = WhiteCylinder()
block_hand = Block_hand()
mouseo = Mouseo()
app.run()