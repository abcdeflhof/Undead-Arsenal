import pygame

class HUDStuff(pygame.sprite.Sprite):
    x = int()
    y = int()
    
    originalImage = pygame.image.load('inventorySlotSprite.png')
    newImage = pygame.image.load('inventorySlotSprite.png')

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('inventorySlotSprite.png')
        self.rect = self.image.get_rect()
        self.rect.center = 0,0

    #creates a new one centered on (xGo,yGo).
    def create(self,activeSpriteGroup,activeHUDGroup,newHUDThing,imageType,xGo,yGo,alphaSet,scaleSet=None,nameID=None):
        newHUDThing = HUDStuff()
        activeSpriteGroup.add(newHUDThing)
        activeHUDGroup.add(newHUDThing)
        newHUDThing.name = nameID
        newHUDThing.image = pygame.image.load(imageType)
        newHUDThing.timer = int()
        
        if (scaleSet != None):
            newHUDThing.originalImage = pygame.transform.scale_by(newHUDThing.image,scaleSet)
            newHUDThing.image = newHUDThing.originalImage

        else:
            newHUDThing.originalImage = newHUDThing.image
        
        newHUDThing.newImage = newHUDThing.image
        newHUDThing.rect = newHUDThing.image.get_rect()
        
        newHUDThing.image.set_alpha(alphaSet)

        newHUDThing.rect.center = (xGo,yGo)
        newHUDThing.x = xGo
        newHUDThing.y = yGo

        return(newHUDThing)

    #changes image and alpha of image by iterating through list of conditions
        #sets image and alpha to same index as condition
        #only works w/ True/False conditions for now
    def updateDisplay(self,conditionsList=list,imagesList=list,alphasList=list,turnList=None,scaleList=None,goToList=None):
        for i in range(len(conditionsList)):
            if (conditionsList[i]):
                if (goToList == None):
                    self.x,self.y = self.rect.center
                else:
                    self.x,self.y = goToList[i]
                
                self.image = pygame.image.load(imagesList[i])
                self.image.set_alpha(alphasList[i])

                #also rotozooms if desired
                if (scaleList != None) and (turnList != None):
                    if (isinstance(scaleList[0],float)):
                        self.newImage = pygame.transform.rotozoom(self.originalImage,turnList[i],scaleList[i])
                        self.image = self.newImage
                    elif (isinstance(scaleList[0],tuple)):
                        self.newImage = pygame.transform.rotate(self.newImage,turnList[i])
                        self.newImage = pygame.transform.scale(self.newImage,scaleList[i])
                        self.image = self.newImage
                
                self.rect = self.image.get_rect()
                self.rect.center = (self.x,self.y)
                
                #exits upon finding a true condition. can arrange conditions in least-most priority bc of this
                return()
    
    def draw(self,surface):
        surface.blit(self.image,self.rect)