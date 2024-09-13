import threading
from math import sqrt

import pygame
import sys
import tkinter as tk
from tkinter import filedialog


# Main loop
class app:
    def __init__(self):
        self.image = None
        self.squares = []
        self.cursor_sq = None
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main tkinter window
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Image Loader and Square Drawer")
        self.buttons = [{'text': 'Load Image',
                         'function': self.load_image,
                         'colour': [0, 0, 255],
                         'rect': None},
                        {'text': 'Scale',
                         'function': self.set_scale,
                         'colour': [255, 128, 0],
                         'rect': None},
                        {'text': 'Clear',
                         'function': self.clear,
                         'colour': [0, 128, 0],
                         'rect': None},
                        {'text': 'Undo',
                         'function': self.undo,
                         'colour': [255, 0, 0],
                         'rect': None}]
        self.x_origin = 0
        self.y_origin = 0
        self.h_len = 0
        self.v_len = 0
        self.hscale_input = None
        self.vscale_input = None
        self.hscale = 0
        self.vscale = 0
        self.set = False
        self.threads = None

    def main(self):
        draw_lines = False
        while True:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.root.destroy()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    draw_lines = True
                    click_origin = event.pos
                    self.cursor_sq = pygame.Rect(click_origin[0], click_origin[1], event.pos[0] - click_origin[0],
                                                 event.pos[1] - click_origin[1])
                elif event.type == pygame.MOUSEMOTION:
                    if draw_lines:
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
                elif event.type == pygame.MOUSEBUTTONUP:
                    draw_lines = False
                    for i in self.buttons:
                        if i['rect'].collidepoint(event.pos):
                            i['function']()
                    else:
                        try:
                            self.squares.append(pygame.Rect(self.x_origin, self.y_origin, self.h_len, self.v_len))
                        except NameError:
                            pass

            if self.image:
                self.screen.blit(self.image, (0, 0))

            if self.cursor_sq:
                pygame.draw.rect(self.screen, (255, 0, 0), self.cursor_sq, 2)
                self.cursor_sq = None

            for square in self.squares:
                pygame.draw.rect(self.screen, (0, 0, 0), square, 5)

            for j, i in enumerate(self.buttons):
                i['rect'] = self.draw_button(i['text'], i['colour'], j)  # Draw list of buttons

            if len(self.squares) > 0 and self.hscale > 0 and self.vscale > 0:
                scaledX = self.hscale / self.squares[0].width
                scaledY = self.vscale / self.squares[0].height
                area = sqrt(scaledX * scaledY)
                font = pygame.font.Font(None, 36)
                text = font.render(f'{area}m2 {scaledX} * {scaledY}', True, (255, 0, 0))
                self.screen.blit(text, (200, 100))

            pygame.display.flip()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*"))
        )
        if file_path:
            try:
                self.image = pygame.image.load(file_path).convert()
            except pygame.error:
                print("Failed to load image.")
        return None

    # Draw button function
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
        self.squares = self.squares[:-2]
        self.x_orgin = 0
        self.y_orgin = 0
        self.h_len = 0
        self.y_len = 0

    def clear(self):
        self.squares = []
        self.cursor_sq = None
        self.x_orgin = 0
        self.y_orgin = 0
        self.h_len = 0
        self.y_len = 0

    def show_scale_window(self):
        def submitButton():
            root.destroy()
        root = tk.Tk()
        root.geometry('340x170')
        root.configure()
        root.title('Scale')

        tk.Label(root, text='Horizontal Scale', font=('arial', 12, 'normal')).place(x=10, y=11)
        tk.Label(root, text='Vertical Scale', font=('arial', 12, 'normal')).place(x=10, y=91)
        self.hscale_input = tk.Entry(root)
        self.hscale_input.place(x=10, y=41)
        self.vscale_input = tk.Entry(root)
        self.vscale_input.place(x=10, y=111)
        tk.Button(root, text='Submit', font=('arial', 12, 'normal'), command=submitButton).place(x=20, y=131)
        root.mainloop()

    def set_scale(self):
        #self.threads = threading.Thread(target=self.show_scale_window)
        #self.threads.start()
        self.show_scale_window()

    def scale_submit_button(self):
        self.hscale = float(self.hscale_input.get())
        self.vscale = float(self.vscale_input.get())
        #self.root.destroy()
        #self.threads.join(0)

    def calc_area(self):
        pass


# Run the game loop
if __name__ == "__main__":
    a = app()
    a.main()
