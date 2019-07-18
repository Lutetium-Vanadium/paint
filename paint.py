import pygame as pg
pg.init()
import sys, os
import traceback

#Colours-------------------------------------------------------------------------------------------------------------

white = pg.Color("WHITE")
black = pg.Color("BLACK")
green = pg.Color(0, 255, 0)
orange = pg.Color(255, 128, 0)
red = pg.Color(255, 0, 0)
skyblue = pg.Color("SKYBLUE")
blue = pg.Color("BLUE")
gray = pg.Color(200, 200, 200)
yellow = pg.Color("YELLOW")
select_green = pg.Color("LIGHTGREEN")

#Classes-------------------------------------------------------------------------------------------------------------

class Button():
    def __init__(self, x, y, wd, ht, colour = gray, hovourColour = white, text = '', img = None, hovourImg = None, textHeight = None,
    textColour = black, outline = True, hovour = False, value = None, surfpos = (0,0), enabled_selected = True, isSize = False):
        if not textHeight:
            textHeight = ht//2
        self.textHeight = textHeight
        self.img = img
        self.hovourImg = hovourImg
        self.pos = (x, y)
        self.surfpos = ((surfpos[0] + x), (surfpos[1] + y))
        self.rect = pg.Rect(x, y, wd, ht)
        self.rectcollide = pg.Rect(self.surfpos, (wd, ht))
        self.text = text
        self.textColour = textColour
        self.colour = colour
        self.hovourColour = hovourColour
        self.outline = outline
        self.hovour = hovour
        self.value = value
        self.flag = False
        self.enabled_selected = enabled_selected
        self.selected = False
        self.isSize = isSize
    def onButton(self):
        return self.rectcollide.collidepoint(pg.mouse.get_pos())
    def show(self, surface, canvas = None):
        thickness = 1
        if self.onButton() and self.hovour:
            if self.img:
                image = self.hovourImg
            else:
                colour = self.hovourColour
        else:
            if self.img:
                image = self.img
            else:
                colour = self.colour
        if self.img:
            surface.blit(image, self.pos)
        else:
        	pg.draw.rect(surface, colour, self.rect)
        if self.enabled_selected and self.selected:
            thickness = 3
            col = select_green
        else:
            col = black
        if self.isSize:
            pg.draw.line(surface, black, (450, 50), (550, 50), canvas.thick)
        if self.outline:
            pg.draw.line(surface, col, self.rect.topleft, self.rect.topright, thickness)
            pg.draw.line(surface, col, self.rect.bottomright, self.rect.topright, thickness)
            pg.draw.line(surface, col, self.rect.bottomleft, self.rect.bottomright, thickness)
            pg.draw.line(surface, col, self.rect.bottomleft, self.rect.topleft, thickness)
        textSurf = pg.font.SysFont(pg.font.get_default_font(), self.textHeight).render(self.text, True, self.textColour)
        textRect = textSurf.get_rect()
        textRect.center = self.rect.center
        surface.blit(textSurf, textRect)
    def get_click(self):
        temp = (pg.mouse.get_pressed()[0] and self.onButton())
        if self.flag == False and temp:
            self.flag = True
            return True
        if self.flag and temp == False:
            self.flag = False
        return False

class Canvas():
    def __init__(self, screencol, brushcol, thickness, e_thickness, screenWd, screenHt, pos, butt_undo_redo):
        self.screencol = screencol
        self.brushcol = brushcol
        self.thick = thickness
        self.e_thick = e_thickness
        self.mode = 'b'								 # b for brush, e - eraser, l - line, r - rectangle, c - circel, f - fill and p - colour picker
        self.size = (screenWd - pos[0], screenHt - pos[1])
        self.surf = pg.Surface(self.size)
        self.pos = pos
##        self.pos1 = (370, 100)
##        self.pos2 = (740, 100)
        self.prev_pos = (0,0)
        self.pressed = False
        self.surf2 = pg.Surface(self.size)
        self.surf_swap = 0
        self.current_surf = self.surf
        self.undo_redo_button = butt_undo_redo
        self.prev_screencol = screencol
        self.tempSurf = None
    def fill(self, pos, screen):
        pos = tuple(pos)
        screencol = screen.get_at(pos)
        if self.brushcol == screencol:
            return
        screen.set_at(pos, self.brushcol)
        queue = [pos]
        while len(queue) > 0:
            x,y = queue.pop(0)
            if x-1 >= 0 and screen.get_at((x-1, y)) == screencol: #check if left is still part of canvas and the left pixel should be coloured
                screen.set_at((x-1,y), self.brushcol)
                queue.append((x-1, y))
            if x + 1 < 1120 and screen.get_at((x+1, y)) == screencol:
                screen.set_at((x+1,y), self.brushcol)
                queue.append((x+1, y))
            if y-1 >= 0 and screen.get_at((x, y-1)) == screencol:
                screen.set_at((x,y-1), self.brushcol)
                queue.append((x, y-1))
            if y+1 < 530 and screen.get_at((x, y+1)) == screencol:
                screen.set_at((x,y+1), self.brushcol)
                queue.append((x, y+1))
    def draw(self, screen):
        self.surf_swap %= 2
        if self.mode == 'b':
            thick = self.thick
        else:
            thick = self.e_thick
        pos = list(pg.mouse.get_pos())
        pos[0], pos[1] = pos[0] - self.pos[0], pos[1] - self.pos[1]
        if self.pressed == False:
            self.prev_pos = pos
            if self.surf_swap == 1:
                self.undo_redo_button.text = '<---'
                self.surf_swap += 1
            if self.surf_swap == 0:
                self.surf2 = self.surf.copy()
            else:
                self.surf = self.surf2.copy()
        if self.mode == 'b':
            col = self.brushcol
        elif self.mode == 'p':
            self.brushcol = self.current_surf.get_at(pos)
            self.mode = 'b'
            self.selected = False
            return
        elif self.mode == 'f':
            self.fill(pos, self.current_surf)
            return
        elif self.mode == 'l' or self.mode == 'c' or self.mode == 'r':
            self.pressed = True
            self.tempSurf = pg.Surface(self.size)
            self.tempSurf.fill(self.screencol)
            self.tempSurf.set_colorkey(self.screencol)
            if self.mode == 'l':
                pg.draw.line(self.tempSurf, self.brushcol, self.prev_pos, pos, self.thick)
            elif self.mode == 'c':
                circ_center = ((pos[0] + self.prev_pos[0])//2, (pos[1] + self.prev_pos[1])//2)
                r = int(((pos[0] - circ_center[0])**2 + (pos[1]- circ_center[1])**2)**0.5)
                if self.thick > r:
                    thickness = 0
                else:
                    thickness = self.thick
                pg.draw.circle(self.tempSurf, self.brushcol, circ_center, r, thickness)
            elif self.mode == 'r':
                wd_ht = (pos[0] - self.prev_pos[0], pos[1]- self.prev_pos[1])
                if wd_ht[0] > self.thick and wd_ht[1] > self.thick:
                    thickness = self.thick
                else:
                    thickness = 0
                drawing_rect = pg.Rect(self.prev_pos, wd_ht)
                pg.draw.rect(self.tempSurf, self.brushcol, drawing_rect, thickness)
            return
        else:
            col = self.screencol
        if self.surf_swap == 0:
            self.current_surf = self.surf
        else:
            self.current_surf = self.surf2

        pg.draw.line(self.current_surf, col, self.prev_pos, pos, thick)
        self.prev_pos = pos
        self.pressed = True
        self.tempSurf = None
    def show(self, screen):
        self.surf_swap %= 2
        if self.surf_swap == 0:
            self.current_surf = self.surf
            self.undo_redo_button.text = '<---'
        else:
            self.current_surf = self.surf2
            self.undo_redo_button.text = '--->'
        screen.blit(self.current_surf, self.pos)
        if self.tempSurf != None:
            screen.blit(self.tempSurf, self.pos)
    def new(self, screen):
        self.surf.fill(self.screencol)
        self.surf_swap = 0
        self.mode = 'b'
    def new_col(self, screen):
        temp_surf = self.current_surf.copy()
        temp_surf.set_colorkey(self.prev_screencol)
        self.new(screen)
        self.surf.blit(temp_surf, (0,0))

class Text():
    def __init__(self, x, y,  size, surfsize, text = '', colour = pg.Color("BLACK")):
        self.location = [x, y]
        self.size = size
        self.text = text
        self.colour = colour
        self.surf = pg.Surface(surfsize)
        self.rect = self.surf.get_rect()
    def display(self, screen):
        textSurf = pg.font.SysFont(pg.font.get_default_font(), self.size).render(self.text, True, self.colour)
        textRect = textSurf.get_rect()
        textRect.center = self.rect.center
        screen.blit(textSurf, self.location)

class Slider():
    def __init__(self, pos, screen_pos, col , current_rgb_val, height = 20, width = 265):
        self.pos = pos
        self.col = col
        self.ht = height
        self.wd = width
        self.surf = pg.Surface((width, height))
        self.surfRect = self.surf.get_rect()
        self.surfRect[0] = screen_pos[0]
        self.surfRect[1] = screen_pos[1]
        self.screen_pos = screen_pos
        self.cursor = Button(current_rgb_val, (height//2 - 10), 5, 10, hovour = True)
    def show(self, screen):
        self.surf.fill(gray)
        pg.draw.line(self.surf, self.col, (5, self.ht//2), (self.wd-10, self.ht//2), 3)
        self.cursor.show(self.surf)
        screen.blit(self.surf, self.pos)
    def move(self, prev_col):
        mpos = pg.mouse.get_pos()
        if self.surfRect.collidepoint(mpos) and pg.mouse.get_pressed()[0]:
            self.cursor.rect.center = (mpos[0]-self.screen_pos[0],self.ht//2)
            return mpos[0]-self.screen_pos[0]
        return prev_col

###########################################################################################################################################################

def rgb_col(screen, canvas, rgb_val, pos):
    count = 0
    clock = pg.time.Clock()
    FPS = 20
    surf = pg.Surface((265, 140))
    surf.fill(gray)
    surfRect = surf.get_rect()
    surfRect[0] = pos[0]
    surfRect[1] = pos[1]
    current_col_surf = pg.Surface((265,40))
    current_rgb_text = Text(1, 1, 20, (265, 40), str(rgb_val))
    rgb_val = list(rgb_val)
    while len(rgb_val) > 3:
        rgb_val.pop()

    red_slider = Slider((5, 15), (pos[0]+5, pos[1]+15), red, rgb_val[0])
    green_slider = Slider((5, 40), (pos[0]+5, pos[1]+40), green, rgb_val[1])
    blue_slider =Slider((5, 65), (pos[0]+5, pos[1]+65), blue, rgb_val[2])

    slider_list = [red_slider, green_slider, blue_slider]

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
                if event.key == pg.K_RETURN:
                    return rgb_val

        dark_count = 0
        for i in rgb_val:
            if i < 100:
                dark_count += 1
        if dark_count == 3:
            current_rgb_text.colour = white
        else:
            current_rgb_text.colour = black

        for i in range(len(slider_list)):
            slider_list[i].show(surf)
            rgb_val[i] = slider_list[i].move(rgb_val[i])
        current_rgb_text.text = str(rgb_val)
        for i in range(3):
            if rgb_val[i] > 255:
                rgb_val[i] = 255
            elif rgb_val[i] < 0:
                rgb_val[i] = 0
        if pg.mouse.get_pressed()[0] and (surfRect.collidepoint(pg.mouse.get_pos()) == False) and count>40:
            return rgb_val
        current_col_surf.fill(pg.Color(rgb_val[0], rgb_val[1], rgb_val[2]))
        current_rgb_text.display(current_col_surf)
        surf.blit(current_col_surf, (0, 100))
        screen.blit(surf, pos)
        pg.display.update()
        count+=1
        clock.tick(FPS)

def colchoice(screen, canvas, canvas_col_button):
    rgb_val = list(canvas.screencol)
    clock = pg.time.Clock()
    FPS = 25
    count = 0
    surf = pg.Surface((100, 265))
    surf.fill(gray)
    surfRect = surf.get_rect()
    surfRect[0] = 745
    surfRect[1] = 105

    while len(rgb_val) > 3:
        rgb_val.pop()
    
    templist = [i for i in range(8)]
    templist[0] = Button(12, 12, 25, 25, white, gray, surfpos = (745, 105))
    templist[1] = Button(63, 12, 25, 25, black, surfpos = (745, 105))
    templist[2] = Button(12, 62, 25, 25, red, surfpos = (745, 105))
    templist[3] = Button(63, 62, 25, 25, orange, surfpos = (745, 105))
    templist[4] = Button(12, 112, 25, 25, yellow, surfpos = (745, 105))
    templist[5] = Button(63, 112, 25, 25, green, surfpos = (745, 105))
    templist[6] = Button(12, 162, 25, 25, skyblue, surfpos = (745, 105))
    templist[7] = Button(63, 162, 25, 25, blue, surfpos = (745, 105))
    rgb = Button(25, 205, 50, 50, canvas.screencol, text = 'RGB', surfpos = (745, 105))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
        for button in templist:
            if button.get_click():
                canvas.prev_screencol = canvas.screencol
                canvas.screencol = button.colour
                canvas.new_col(screen)
                canvas_col_button.colour = button.colour
                return
            button.show(surf)
        if pg.mouse.get_pressed()[0] and surfRect.collidepoint(pg.mouse.get_pos()) == False and count>10:
            return
        if rgb.get_click():
            rgb_val = rgb_col(screen, canvas, rgb_val, (662, 375))
            if rgb_val != None:
                canvas.prev_screencol = canvas.screencol
                canvas.screencol = pg.Color(rgb_val[0], rgb_val[1], rgb_val[2])
                canvas.new_col(screen)
                canvas_col_button.colour = canvas.screencol
        rgb.show(surf)
        screen.blit(surf, (745, 105))
        pg.display.update()
        count += 1
        clock.tick(FPS)

def shape_choice(screen, canvas, surfpos = (975, 105)):
    clock = pg.time.Clock()
    FPS = 20
    surf = pg.Surface((80, 200))
    count = 0
    surfRect = surf.get_rect()
    surfRect [0], surfRect[1] = surfpos[0], surfpos[1]


    line_surf = pg.Surface((40, 40))
    line_surf.fill(gray)
    pg.draw.line(line_surf, canvas.brushcol, (5, 5), (35, 35), 2)

    rect_surf = pg.Surface((40, 40))
    rect_surf.fill(gray)
    pg.draw.rect(rect_surf, canvas.brushcol, (5, 10, 30, 20), 2)

    circ_surf = pg.Surface((40, 40))
    circ_surf.fill(gray)
    pg.draw.circle(circ_surf, canvas.brushcol, (20, 20), 15, 2)


    line_button = Button(20, 20, 40, 40, img = line_surf, value = 'l', surfpos = surfpos)
    rect_button = Button(20, 80, 40, 40, img = rect_surf, value = 'r', surfpos = surfpos)
    circ_button = Button(20, 140, 40, 40, img = circ_surf, value = 'c', surfpos = surfpos)

    button_list = [line_button, rect_button, circ_button]

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return

        surf.fill(gray)
        for button in button_list:
            if button.get_click():
                canvas.mode = button.value
                return
            button.show(surf)

        if pg.mouse.get_pressed()[0] and surfRect.collidepoint(pg.mouse.get_pos()) == False and count > 20:
            return

        screen.blit(surf, surfpos)
        pg.display.update()
        count += 1
        clock.tick(FPS)

def brushsize(screen, canvas):
    clock = pg.time.Clock()
    FPS = 20
    surf = pg.Surface((100, 50))
    count = 0
    surfRect = surf.get_rect()

    dct = {pg.K_1:1, pg.K_2:2, pg.K_3:3, pg.K_4:4, pg.K_5:5, pg.K_6:6, pg.K_7:7, pg.K_8:8, pg.K_9:9, pg.K_0:0}
    text_size = Text(0, 30, 25, surfRect.size, str(canvas.thick))
    text_instructions = Text(0, 10, 15, surfRect.size, "Type Size in pixels")
    check = True

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
                if check:
                    text_size.text = ''
                    check = False
                if event.key in dct:
                    text_size.text += str(dct[event.key])
                elif event.key == pg.K_RETURN:
                    canvas.thick = int(text_size.text)
                    canvas.e_thick = int(text_size.text) + 25
                    return
                elif event.key == pg.K_EQUALS:
                    canvas.thick = int(text_size.text)
                    canvas.e_thick = int(text_size.text) + 25
                    return
                elif event.key == pg.K_BACKSPACE:
                    text_size.text = text_size.size[:-1]


        if pg.mouse.get_pressed()[0] and surfRect.collidepoint(pg.mouse.get_pos()) == False and count>40:
            return
        surf.fill(gray)
        text_instructions.display(surf)
        text_size.display(surf)
        screen.blit(surf, (450, 105))
        pg.display.update()
        count += 1
        clock.tick(FPS)

def toolbar(screen, button_list_col, button_list_mode, button_list_misc, canvas, size = (1120, 100), pos = (0,0), col = gray):
    rgb_val = canvas.brushcol
    surf = pg.Surface(size)
    surf.fill(col)
    for button in button_list_col:
            if button.get_click():
                rgb_val = button.colour
                canvas.brushcol = button.colour
                button.selected = True
                if canvas.mode == 'e':
                    canvas.mode = 'b'
            if button.selected and canvas.brushcol != button.colour:
                button.selected = False
            button.show(surf)
    for button in button_list_mode:
            if button.get_click():
                canvas.mode = button.value
                button.selected = True
            if button.selected and canvas.mode != button.value:
                button.selected = False
            button.show(surf)

    if button_list_misc[0].get_click():
        canvas.new(screen)
    elif button_list_misc[1].get_click():
        canvas.surf_swap += 1
        canvas.show(screen)
    for button in button_list_misc:
        button.show(surf, canvas)
    screen.blit(surf, pos)
    if button_list_misc[2].get_click():
        colchoice(screen, canvas, button_list_misc[2])
    elif button_list_misc[3].get_click():
        brushsize(screen, canvas)
    elif button_list_misc[4].get_click():
        rgb_val = rgb_col(screen, canvas, rgb_val, (492, 105))
        if rgb_val != None:
            canvas.brushcol = pg.Color(rgb_val[0], rgb_val[1], rgb_val[2])
    elif button_list_misc[5].get_click():
        shape_choice(screen, canvas)
        pg.time.wait(200)

def mainLoop():
    pg.display.set_caption('Paint')
    screenWd, screenHt = (1120, 630)
    screen = pg.display.set_mode((screenWd, screenHt))
    FPS = 60
    clock = pg.time.Clock()
    screencol = white
    brushcol = black

    white_butt = Button(250, 12, 25, 25, white)
    black_butt = Button(250, 63, 25, 25, black)
    red_butt = Button(300, 12, 25, 25, red)
    orange_butt = Button(300, 63, 25, 25, orange)
    yellow_butt = Button(350, 63, 25, 25, yellow)
    green_butt = Button(350, 12, 25, 25, green)
    skyblue_butt = Button(400, 63, 25, 25, skyblue)
    blue_butt = Button(400, 12, 25, 25, blue)
    
    butt_undo_redo = Button(700, 30, 40, 40, text = "<---", textHeight = 30,  enabled_selected = False)

    canvas = Canvas(screencol, brushcol, 5, 30, screenWd, screenHt, (0,100), butt_undo_redo)
    canvas.new(screen)

    brush = pg.image.load(os.path.join(os.getcwd(), "brush.png"))
    brush_hov = pg.image.load(os.path.join(os.getcwd(), "brush_hov.png"))
    eraser = pg.image.load(os.path.join(os.getcwd(), "eraser.png"))
    slider = pg.image.load(os.path.join(os.getcwd(), "slider.jpeg"))
    eraser_hov = pg.image.load(os.path.join(os.getcwd(), "eraser_hov.png"))
    col_pick_pic = pg.image.load(os.path.join(os.getcwd(), "col_pick.png"))
    fill_pic = pg.image.load(os.path.join(os.getcwd(), "fill.png"))
    
    shapes_surf = pg.Surface((50, 50))
    shapes_surf.fill(gray)
    pg.draw.circle(shapes_surf, black, (25, 25), 15, 2)
    

    brush_butt = Button(100,25, 50, 50, img = brush, hovourImg = brush_hov, hovour = True, value = 'b')
    eraser_butt = Button(175,25, 50, 50, img = eraser, hovourImg = eraser_hov, hovour = True, value = 'e')
    butt_col_pick = Button(840, 25, 50, 50, value = 'p', img = col_pick_pic)
    butt_fill = Button(915, 25, 50, 50, value = 'f', img = fill_pic)
    
    butt_new = Button(25, 25, 50, 50, white, text = 'new', enabled_selected = False)
    butt_canvas_menu = Button(775, 30, 40, 40, canvas.screencol, enabled_selected = False)
    butt_size = Button(450, 25, 100, 50, enabled_selected = False, outline = False, isSize = True)
    butt_slider = Button(575, 25, 100, 50, img = slider, enabled_selected = False)
    butt_shapes = Button(990, 25, 50, 50, img = shapes_surf)

    button_list_col = [white_butt, black_butt, red_butt, orange_butt, yellow_butt,
                            green_butt, skyblue_butt, blue_butt]
    button_list_mode = [brush_butt, eraser_butt, butt_col_pick, butt_fill]
    button_list_misc = [butt_new, butt_undo_redo, butt_canvas_menu, butt_size, butt_slider, butt_shapes]

    brush_butt.selected = True
    black_butt.selected = True

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    return

        mpos = pg.mouse.get_pos()

        if mpos[0] > canvas.pos[0] and mpos[1] > canvas.pos[1]:
            if pg.mouse.get_pressed()[0]:
                if canvas.mode == 'p':
                    brush_butt.selected = True
                canvas.draw(screen)
            else:
                if canvas.pressed == True:
                    pos = (mpos[0], mpos[1] - 100)
                    if canvas.mode == 'l':
                        pg.draw.line(canvas.current_surf, canvas.brushcol, canvas.prev_pos, pos, canvas.thick)
                    elif canvas.mode == 'r':
                        wd_ht = (pos[0] - canvas.prev_pos[0], pos[1]- canvas.prev_pos[1])
                        if wd_ht[0] > canvas.thick and wd_ht[1] > canvas.thick:
                            thickness = canvas.thick
                        else:
                            thickness = 0
                        drawing_rect = pg.Rect(canvas.prev_pos, wd_ht)
                        pg.draw.rect(canvas.current_surf, canvas.brushcol, drawing_rect, thickness)
                    elif canvas.mode == 'c':
                        circ_center = ((pos[0] + canvas.prev_pos[0])//2, (pos[1] + canvas.prev_pos[1])//2)
                        r = int(((pos[0] - circ_center[0])**2 + (pos[1]- circ_center[1])**2)**0.5)
                        if canvas.thick > r:
                            thickness = 0
                        else:
                            thickness = canvas.thick
                        pg.draw.circle(canvas.current_surf, canvas.brushcol, circ_center, r, thickness)
                canvas.pressed = False
            pg.mouse.set_visible(False)
        else:
            canvas.pressed = False
            pg.mouse.set_visible(True)

        screen.fill(screencol)

        canvas.show(screen)

        if canvas.mode == 'e':
            rect = pg.Rect(mpos, (canvas.e_thick, canvas.e_thick))
            rect.center = mpos
            pg.draw.rect(screen, black, rect, 1)
        elif canvas.mode == 'f':
            pg.draw.circle(screen, black, mpos, 2)
        elif canvas.mode == 'p':
            pg.draw.circle(screen, screen.get_at(mpos), mpos, 10)
            pg.draw.circle(screen, black, mpos, 10, 1)
        else:
            pg.draw.circle(screen, canvas.brushcol, mpos, canvas.thick//2)

        toolbar(screen, button_list_col, button_list_mode, button_list_misc, canvas)

        pg.display.update()
        clock.tick(FPS)

try:
    mainLoop()
except:
    traceback.print_exc()
finally:
    pg.quit()