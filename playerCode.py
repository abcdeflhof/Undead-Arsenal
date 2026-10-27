import pygame
import math

class player(pygame.sprite.Sprite):
    originalImage = pygame.image.load('playerSprite.png')
    x = int()
    y = int()
    angle = float()
    
    speed = 6
    health = 100
    moneyGive = 0

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('playerSprite.png')
        self.rect = self.image.get_rect()

    #moving the player around
    def move(self,uBound,dBound,lBound,rBound):
        #get keys
        pressedKeys = pygame.key.get_pressed()

        #movement keys w/ requirements of being in bounds
            #LITTLE BUG OF TURNING MAKING YOUR RECT BE DIFFERENT SO THE BOUNDS ARE WEIRD
        if (pressedKeys[pygame.K_w]) and (self.rect.top > uBound):
            self.rect.move_ip(0,-self.speed)
        elif (pressedKeys[pygame.K_s]) and (self.rect.bottom < dBound):
            self.rect.move_ip(0,self.speed)
        if (pressedKeys[pygame.K_a]) and (self.rect.left > lBound):
            self.rect.move_ip(-self.speed,0)
        elif (pressedKeys[pygame.K_d]) and (self.rect.right < rBound):
            self.rect.move_ip(self.speed,0)
        
        #updates coords so that the turning still works, probably transferable too
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

    #a general update outside of movement and turning
    def update(self,damageCollision,damageAnimateFunc,damageAnimateParameters=list):
        #game over collision check
        if pygame.sprite.spritecollide(self,damageCollision,0):
            if pygame.sprite.spritecollide(self,damageCollision,0,pygame.sprite.collide_mask):
                
                #does a little blood animation when getting hit
                damageAnimateFunc(*damageAnimateParameters)
                
                #checks all of what's hitting player
                collisionList = pygame.sprite.spritecollide(self,damageCollision,0,pygame.sprite.collide_mask)
                
                #reduces health for each source of damage
                for enemy in collisionList:
                    if (enemy.IFrames < 1):
                        self.health -= enemy.damage
                        enemy.IFrames = enemy.IFramesGoal

    
    def draw(self,surface):
        surface.blit(self.image,self.rect)