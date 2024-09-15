import threading
from math import sqrt
from decimal import Decimal
import pygame
import sys
import tkinter as tk
from tkinter import filedialog

LEFTCLICK = 1
class app:
    def __init__(self):
        self.image = None
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main tkinter window
        pygame.init()
        mon = pygame.display.Info()
        self.screenResolution = (mon.current_w,mon.current_h)
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.update()
        pygame.display.set_caption("Image Loader and Square Drawer")
        self.buttons = [{'text': 'Load Image',
                         'function': self.load_image,
                         'colour': [0, 0, 255],
                         'rect': None},
                        #{'text': 'Scale',
                        # 'function': self.set_scale,
                        # 'colour': [255, 128, 0],
                        # 'rect': None},
                        {'text': 'Clear',
                         'function': self.clear,
                         'colour': [0, 128, 0],
                         'rect': None},
                        {'text': 'Undo',
                         'function': self.undo,
                         'colour': [255, 0, 0],
                         'rect': None}]
        self.colours = ((0, 0, 0),
                        (255, 0, 0),
                        (0, 255, 0),
                        (0, 0, 255),
                        (128, 0, 255),
                        (0, 128, 255),
                        (255, 0, 128),
                        (255, 128, 0),
                        (128, 255, 0),
                        (0, 255, 128),
                        (128, 255, 128),
                        (128, 128, 255),
                        (255, 128, 128),
                        (255, 255, 128),
                        (255, 128, 255),
                        (128, 255, 255))
        self.prev = ''
        self.hmargin = 200
        self.vmargin = 50
        self.digits = Decimal('1.23')
        self.dimFontSize = 25
        self.clear()

    def clear(self):
        self.boxes = []
        self.cursor_sq = None
        self.x_origin = 0
        self.y_origin = 0
        self.h_len = 0
        self.y_len = 0
        self.hscale_input = None
        self.vscale_input = None
        self.hscale = Decimal(0)
        self.vscale = Decimal(0)
        self.scaledX = Decimal(0)
        self.scaledY = Decimal(0)

    def main(self):
        draw_lines = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.root.destroy()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTCLICK:
                    draw_lines = True
                    click_origin = event.pos
                elif event.type == pygame.MOUSEMOTION:
                    if draw_lines:
                        self.create_cursor_sq(event, click_origin)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTCLICK:
                    draw_lines = False
                    self.cursor_sq = None
                    clicked_a_button = False
                    for i in self.buttons:
                        if i['rect'].collidepoint(event.pos):
                            i['function']()  # why don't we return to main after this has completed?
                            clicked_a_button = True
                            break
                    if not clicked_a_button:
                        self.create_box()

            self.screen.fill((200, 200, 200))
            if self.image:
                self.screen.blit(self.image, (self.hmargin, self.vmargin))

            if self.cursor_sq:
                pygame.draw.rect(self.screen, (255, 0, 0), self.cursor_sq, 2)

            for index, j, in enumerate(self.boxes):
                square, xlabel, ylabel, slabel = j
                colour = index % len(self.colours)
                pygame.draw.rect(self.screen, self.colours[colour], square, 5)
                self.screen.blit(xlabel, (square.x + 20, square.y + 5))
                for i, j in enumerate(ylabel):
                    self.screen.blit(j, (square.x + 5, square.y + 20 + (15*i)))
                self.screen.blit(slabel, (5, 100 + (index*40)))

            for j, i in enumerate(self.buttons):
                i['rect'] = self.draw_button(i['text'], i['colour'], j)  # Draw list of buttons

            if len(self.boxes) > 0 and self.hscale > 0 and self.vscale > 0:
                area = self.calculate_total_area()
                font = pygame.font.Font(None, 36)
                t = 'Total: {}m^2'.format(area.quantize(self.digits))
                text = font.render(t, True, (0, 0, 0))
                self.screen.blit(text, (5, 50))
            elif len(self.boxes) == 1:
                self.show_scale_window()
            pygame.display.flip()

    def create_cursor_sq(self, event, click_origin):
        if event.pos[0] - click_origin[0] >= 0:  # rightward movement
            self.h_len = event.pos[0] - click_origin[0]
            self.x_origin = click_origin[0]
        else:  # leftward movement
            self.h_len = click_origin[0] - event.pos[0]
            self.x_origin = event.pos[0]
        if event.pos[1] - click_origin[1] >= 0:  # downward movement
            self.v_len = event.pos[1] - click_origin[1]
            self.y_origin = click_origin[1]
        else:  # upward movement
            self.v_len = click_origin[1] - event.pos[1]
            self.y_origin = event.pos[1]
        self.cursor_sq = pygame.Rect(self.x_origin, self.y_origin, self.h_len, self.v_len)

    def create_box(self):
        font = pygame.font.Font(None, self.dimFontSize)
        xpat = ''
        ypat = ''
        if self.scaledX > 0:
            xpat = '<- {}m ->'.format((self.scaledX * self.h_len).quantize(self.digits))
        if self.scaledY > 0:
            ypat = '{}m'.format((self.scaledY * self.v_len).quantize(self.digits))
        colour = len(self.boxes) % len(self.colours)
        self.boxes.append([pygame.Rect(self.x_origin, self.y_origin, self.h_len, self.v_len),
                           font.render(xpat, True, self.colours[colour]),
                           [font.render(('' if ypat == '' else '^'), True, self.colours[colour]),
                            font.render(ypat, True, self.colours[colour]),
                            font.render(('' if ypat == '' else 'v'), True, self.colours[colour])
                           ],
                           font.render('', True, self.colours[colour]),
                           ])
        if self.scaledX > 0:
            sideLabelPat = '{}m^2'.format(self.scaled_rect_area(self.boxes[-1][0]).quantize(self.digits))
            self.boxes[-1][3] = font.render(sideLabelPat, True, self.colours[colour])
        if len(self.boxes) == 2:
            sideLabelPat = '{}m^2'.format(self.scaled_rect_area(self.boxes[0][0]).quantize(self.digits))
            xpat = '<- {}m ->'.format((self.hscale).quantize(self.digits))
            ypat = '{}m'.format((self.vscale).quantize(self.digits))
            self.boxes[0] = [self.boxes[0][0],
                             font.render(xpat, True, self.colours[0]),
                             [font.render('^', True, self.colours[0]),
                              font.render(ypat, True, self.colours[0]),
                              font.render('v', True, self.colours[0])
                             ],
                             font.render(sideLabelPat, True, self.colours[0]),
                            ]


    def overlapping_area(self, r1, r2):
        intersection = r1.clip(r2)
        if intersection.width == 0 or intersection.height == 0:
            return 0
        return self.scaled_rect_area(intersection)

    def scaled_rect_area(self, rect):
        return (self.scaledX * rect.width)*(self.scaledY * rect.height)

    def calculate_total_area(self):
        # Start with an empty list of non-overlapping rectangles
        non_overlapping_rects = []
        rects = [rect for rect, xlabel, ylabel, slabel in self.boxes]
        self.scaledX = self.hscale / Decimal(self.boxes[0][0].width)
        self.scaledY = self.vscale / Decimal(self.boxes[0][0].height)
        gross_area = Decimal(sum([(self.scaled_rect_area(rect)) for rect in rects]))
        overlap_area = Decimal(0)
        for i in range(len(rects)):
            for j in range(i+1, len(rects)):
                overlap_area += self.overlapping_area(rects[i], rects[j])
        net_area = gross_area - overlap_area
        return net_area

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=(
                ("All files", "*.*"),
                #("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("All files", "*.*")
            ),
            initialdir='~/Downloads'
        )
        if file_path:
            try:
                self.image = pygame.image.load(file_path).convert()
            except pygame.error:
                print("Failed to load image.")
        # Scale image
        imW = self.image.get_width()
        imH = self.image.get_height()
        if imW > self.screenResolution[0] or imH > self.screenResolution[1]:
            scale_factor = min((self.screenResolution[1]-self.hmargin)/imH, (self.screenResolution[0]-self.vmargin)/imW)
            self.image = pygame.transform.scale(self.image, (int(imW * scale_factor), int(imH*scale_factor)))
        self.screen = pygame.display.set_mode(
            (self.image.get_width() + self.hmargin, self.image.get_height() + self.vmargin))
        return None

    def draw_button(self, text, colour, offset, padding=10):
        BUTTON_WIDTH = 150 # 15*len(text)
        BUTTON_HEIGHT = 40
        button_rect = pygame.Rect((BUTTON_WIDTH * (offset + 0)) + (padding * (offset + 1)), 10, BUTTON_WIDTH,
                                  BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, colour, button_rect)
        font = pygame.font.Font(None, 36)
        text = font.render(text, True, (255, 255, 255))
        self.screen.blit(text, (button_rect.x + 10, button_rect.y + 5))
        return button_rect

    def undo(self):
        self.boxes = self.boxes[:-1]
        self.x_origin = 0
        self.y_origin = 0
        self.h_len = 0
        self.y_len = 0


    def show_scale_window(self):
        root = tk.Tk()
        self.root1 = root
        root.geometry('200x180')
        root.configure()
        root.title('Scale')
        tk.Label(root, text='Horizontal Scale', font=('arial', 12, 'normal')).place(x=10, y=10)
        tk.Label(root, text='Vertical Scale', font=('arial', 12, 'normal')).place(x=10, y=80)
        self.hscale_input = tk.Entry(root)
        self.hscale_input.place(x=10, y=40)
        self.vscale_input = tk.Entry(root)
        self.vscale_input.place(x=10, y=100)
        tk.Button(root, text='Submit', font=('arial', 12, 'normal'), command=self.scale_submit_button).place(x=20, y=140)
        root.bind('<Return>', self.scale_submit_button)
        root.mainloop()

    def scale_submit_button(self, *args):
        self.hscale = Decimal(self.hscale_input.get())
        self.vscale = Decimal(self.vscale_input.get())
        self.root1.destroy()
        self.main()  # return to main
        #self.threads.join(0)


# Run the game loop
if __name__ == "__main__":
    a = app()
    a.main()
