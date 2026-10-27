import pygame

class background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('level1BGSprite.png')
        self.rect = self.image.get_rect()
        self.rect.center = 0,0
    
    #moves if needed, mainly for initial set as to avoid magic numbers
    def setPlace(self,x,y):
        self.rect.center = (x,y)

    def draw(self,surface):
        surface.blit(self.image,self.rect)