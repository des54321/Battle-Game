import pygame
pygame.init()
screen = pygame.display.set_mode((300,400))
fps = 60
fps_clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    pygame.display.update()
    fps_clock.tick(fps)
pygame.quit()