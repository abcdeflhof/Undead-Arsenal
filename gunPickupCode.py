import pygame
import math
import random

class gunPickup(pygame.sprite.Sprite):       
    alpha = 255
    gunType = 1

    spawnCount = int()
    currentState = str()
    stateChange = str()
    
    def __init__(self):
            super().__init__()
            self.image = pygame.image.load('shotgunSprite.png')
            self.rect = self.image.get_rect()
            self.rect.center = 0,0
    
    #creates a pickup at a random point of the screen
    def spawn(self,activeSpriteGroup,aGunPckpGroup,doSpawnCount,optionsForSpawn,currentStateSet,boxSprite,uBound,dBound,lBound,rBound,margin,noSpawnSpot,vFXFunc,vFXFuncParameters):
        for i in range(doSpawnCount):
        
            newGunPickup = gunPickup()

            #stuff for interaction so it doesn't crash
            newGunPickup.gotGrabbed = False
            newGunPickup.gotDestroyed = False
            newGunPickup.beingTouched = False

            newGunPickup.mod1Grabbed = False
            newGunPickup.mod2Grabbed = False
            newGunPickup.mod3Grabbed = False

            #adding to groups
            activeSpriteGroup.add(newGunPickup)
            aGunPckpGroup.add(newGunPickup)

            #making the sprite work
            newGunPickup.image = pygame.image.load(boxSprite)
            newGunPickup.currentState = currentStateSet

            #random skin
            skinType = random.choice(optionsForSpawn)

            #tier 1 guns
            if (skinType == 0):
                newGunPickup.gunImage = pygame.image.load('dualPistolsSprite.png')
                newGunPickup.rect = newGunPickup.image.get_rect()
                newGunPickup.gunType = [0,5]
            elif (skinType == 1):
                newGunPickup.gunImage = pygame.image.load('shotgunSprite.png')
                newGunPickup.rect = newGunPickup.image.get_rect()
                newGunPickup.gunType = [1,25]
            elif (skinType == 2):
                newGunPickup.gunImage = pygame.image.load('rifleSprite.png')
                newGunPickup.rect = newGunPickup.image.get_rect()
                newGunPickup.gunType = [2,16]
            elif (skinType == 3):
                newGunPickup.gunImage = pygame.image.load('swordSprite.png')
                newGunPickup.rect = newGunPickup.image.get_rect()
                newGunPickup.gunType = [3,20]
            
            #tier 2 guns
            elif (skinType == 100):
                newGunPickup.gunImage = pygame.image.load('sixerSprite.png')
                newGunPickup.gunType = [100,43,6,6,3,3]
            elif (skinType == 101):
                newGunPickup.gunImage = pygame.image.load('flamethrowerSprite.png')
                newGunPickup.gunType = [101,4]
            elif (skinType == 102):
                newGunPickup.gunImage = pygame.image.load('sniperRifleSprite.png')
                newGunPickup.gunType = [102,22]
            elif (skinType == 103):
                newGunPickup.gunImage = pygame.image.load('flameSwordSprite.png')
                newGunPickup.gunType = [103,20]

            #tier 3 guns
            elif (skinType == 1000):
                newGunPickup.gunImage = pygame.image.load('uziSprite.png')
                newGunPickup.gunType = [1000,2]
            elif (skinType == 1001):
                newGunPickup.gunImage = pygame.image.load('rocketLauncherSprite.png')
                newGunPickup.gunType = [1001,20]
            elif (skinType == 1002):
                newGunPickup.gunImage = pygame.image.load('railgunSprite.png')
                newGunPickup.gunType = [1002,40]
            elif (skinType == 1003):
                newGunPickup.gunImage = pygame.image.load('dualSwordsSprite.png')
                newGunPickup.gunType = [1003,55,3,3,12,12]

            #mods (done in just one elif because they all let you select on pickup)
            elif (skinType < 0):
                newGunPickup.gunImage = pygame.image.load('gunModPickupSprite.png')
                newGunPickup.gunType = -1

            newGunPickup.rect = newGunPickup.image.get_rect()
            
            #spawn randomly not on player
            newGunPickup.rect.center = noSpawnSpot.rect.center
            
            while pygame.sprite.collide_rect(newGunPickup,noSpawnSpot):
                newGunPickup.rect.center = ((random.randint((lBound + margin),(rBound - margin))),(random.randint((uBound + margin),(dBound - margin))))
            
            newGunPickup.x, newGunPickup.y = newGunPickup.rect.center

            for i in range(12):
                vFXFunc(*vFXFuncParameters,'dustParticleSprite.png',newGunPickup.rect.midbottom,random.randint(0,359),1.5,255,2,0,-10,-0.05,20)

    #update waiting for player to pickup/destroy
    def update(self,boxBreakGroup,eventHappens,otherEventHappens):
        
        #must be shot to break box, but doesnt actually die
        if (self.currentState == "box"):
            if (pygame.sprite.spritecollide(self,boxBreakGroup,0)):
                self.stateChange = "gunMade"

        elif (self.currentState == "modBox"):
                    if (pygame.sprite.spritecollide(self,boxBreakGroup,0)):
                        self.stateChange = "modMade"

        elif (self.currentState == "gun"):
            #if player is close,prompts for interaction
            if (self.beingTouched):
                
                #glows/blinks while prompting
                self.alpha = self.image.get_alpha()

                if self.image.get_alpha() > 125:
                    self.image.set_alpha((self.alpha - 10))
                else:
                    self.image.set_alpha(255)
                
                #actual stuff when picked up
                if (self.gotGrabbed):
                    
                    eventHappens(*self.gunType)

                    self.kill()

                elif (self.gotDestroyed):
                    self.stateChange = "death"
            
            #stops glowing when can't interact anymore, but only if player kinda close to reduce lag
            else:
                self.image.set_alpha(255)

        elif (self.currentState == "mod"):
            if (self.beingTouched):
                
                #glows/blinks while prompting
                self.alpha = self.image.get_alpha()

                if self.image.get_alpha() > 125:
                    self.image.set_alpha((self.alpha - 10))
                else:
                    self.image.set_alpha(255)
                
                #adds 1 to the modQuantities list in the respective position
                if (self.mod1Grabbed):
                    otherEventHappens(0,1)
                    self.kill()
                elif (self.mod2Grabbed):
                    otherEventHappens(1,1)
                    self.kill()
                elif (self.mod3Grabbed):
                    otherEventHappens(2,1)
                    self.kill()
                elif (self.gotDestroyed):
                    self.stateChange = "death"
            
            #stops glowing when can't interact anymore, but only if player kinda close to reduce lag
            else:
                self.image.set_alpha(255)

    def draw(self,surface):
        surface.blit(self.image,self.rect)