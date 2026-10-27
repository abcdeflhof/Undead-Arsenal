import pygame
import math

class VFX(pygame.sprite.Sprite):
    originalImage = pygame.image.load('hitEffectSprite.png')
    
    x = int()
    y = int()

    appearanceChoices = None
    deathEffect = None

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('hitEffectSprite.png')
        self.rect = self.image.get_rect()
        self.rect.center = 0,0
    
    def create(self,activeVFXGroup,activeSpriteGroup,imageSet,source,angleSet,scaleSet,alphaSet,speedSet,turnRateSet,alphaRateSet,scaleRateSet,lifeTime,deathEffectSet=None,deathEffectParametersSet=None,appearanceChoicesSet=None,appearanceChoiceThreshSet=None):
        #make a new one
        newVFX = VFX()
        activeVFXGroup.add(newVFX)
        activeSpriteGroup.add(newVFX)

        #image stuff
        newVFX.originalImage = pygame.image.load(imageSet)
        newVFX.rect = newVFX.originalImage.get_rect()
        newVFX.x,newVFX.y = newVFX.rect.center

        #starting values
        newVFX.angle = angleSet
        newVFX.scale = scaleSet
        newVFX.alpha = alphaSet

        #moves it
        newVFX.rect.center = source
        newVFX.newImage = pygame.transform.rotozoom(newVFX.originalImage,newVFX.angle,newVFX.scale)
        
        #sets new version of image
        newVFX.image = newVFX.newImage
        newVFX.image.set_alpha(alphaSet)

        #values for changing stuff in update
        newVFX.speed = speedSet
        newVFX.turnRate = turnRateSet
        newVFX.alphaRate = alphaRateSet
        newVFX.scaleRate = scaleRateSet
        newVFX.lifeLeft = lifeTime

        #sets stuff for deathEffect and appearanceChoices (only happens if filled in for performance)
        if (deathEffectSet != None):
            newVFX.deathEffect = deathEffectSet
            newVFX.deathEffectParameters = deathEffectParametersSet
        if (appearanceChoicesSet != None):
            newVFX.appearanceChoices = appearanceChoicesSet
            newVFX.appearanceChoiceThreshholds = appearanceChoiceThreshSet

    #changing all the stuff from create
    def update(self):
        self.rect.move_ip((-math.cos(self.angle * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
        self.x,self.y = self.rect.center

        #mini version of rotate function here since there's no target
        self.angle += self.turnRate
        self.scale += self.scaleRate
        self.newImage = pygame.transform.rotozoom(self.originalImage,self.angle,self.scale)
        self.image = self.newImage

        #changes alpha
        self.alpha += self.alphaRate
        self.image.set_alpha(self.alpha)

        #tick tock, life comes closer to ending
        self.lifeLeft -= 1
        if (self.lifeLeft < 1):
            
            #the actual activation of the death effect
            if (self.deathEffect != None):
                
                self.deathEffect(*self.deathEffectParameters)

            self.kill()
        
        #here's where appearance can change if applicable once only so many life frames are left
        if (self.appearanceChoices != None):
            for i in range(len(self.appearanceChoiceThreshholds)):
                if (self.lifeLeft < self.appearanceChoiceThreshholds[i]):
                    self.x,self.y = self.rect.center[0],self.rect.center[1]
                    self.image = pygame.image.load(self.appearanceChoices[i])
                    self.image = pygame.transform.rotozoom(self.image,self.angle,self.scale)

        #moves back into place, offset due to rotozoom
        self.rect = self.image.get_rect(center = (self.x,self.y))

    def draw(self,surface):
        surface.blit(self.image,self.rect)