import pygame
import math
import random

class bullet(pygame.sprite.Sprite):
    originalImage = pygame.image.load('mediumBulletSprite.png')
    newImage = pygame.image.load('mediumBulletSprite.png')
    
    speed = int()
    pierceLeft = int()
    pierce = int()
    damage = int()
    lifetime = int()

    x = int()
    y = int()
    
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('mediumBulletSprite.png')
        self.rect = self.image.get_rect()
        self.rect.center = 0,0

    #takes a source to fire from and adds to the active group
    def fire(self,source,target,deathCollisionSet,horizOffsets,forthOffsets,activePBullet,activeSprites,rotateFunc,bulletNum,bulletSpread,newBulletPierce,newBulletSpeed,newBulletSpeedVariance,newBulletDamage,newBulletLifetime,bulletProperties,newBulletImage,dontKillGroupSet=None,doHomeSet=None,homeProperties=None,scaleSet=1):
        for i in range(bulletNum):
            
            #creation
            newBullet = bullet()
            activePBullet.add(newBullet)
            activeSprites.add(newBullet)

            #image stuff
            newBullet.image = pygame.image.load(newBulletImage)
            newBullet.image = pygame.transform.scale_by(newBullet.image,scaleSet)
            newBullet.rect = newBullet.image.get_rect()
            
            newBullet.originalImage = newBullet.image

            #placement
            if (isinstance(source,tuple)):
                newBullet.rect.center = source
                newBullet.angle = 0
            else:
                newBullet.rect.center = source.rect.center
                newBullet.angle = source.angle

            #offsets itself as according to parameters
                #OFFSET PARAMETERS WORK WITH AN INT OR A LIST
            if (type(horizOffsets) is int):
                newBullet.rect.move_ip((math.cos((newBullet.angle + 90) * -math.pi/180) * horizOffsets),(math.sin((newBullet.angle + 90) * -math.pi/180) * horizOffsets))
            else:
                newBullet.rect.move_ip((math.cos((newBullet.angle + 90) * -math.pi/180) * random.choice(horizOffsets)),(math.sin((newBullet.angle + 90) * -math.pi/180) * random.choice(horizOffsets)))

            if (type(forthOffsets) is int):
                newBullet.rect.move_ip((-math.cos((newBullet.angle) * -math.pi/180) * forthOffsets),(-math.sin((newBullet.angle) * -math.pi/180) * forthOffsets))
            else:
                    newBullet.rect.move_ip((-math.cos((newBullet.angle) * -math.pi/180) * random.choice(forthOffsets)),(-math.sin((newBullet.angle) * -math.pi/180) * random.choice(forthOffsets)))

            newBullet.x = newBullet.rect.center[0]
            newBullet.y = newBullet.rect.center[1]

            #attributes
                #some attributes can be put as a list or integer. if list, randint's between them
            newBullet.pierceLeft = newBulletPierce
            newBullet.pierce = newBulletPierce
            newBullet.damage = newBulletDamage
            
            newBullet.speed = newBulletSpeed
            newBullet.speed += random.randint(-newBulletSpeedVariance,newBulletSpeedVariance)
            
            if (isinstance(newBulletLifetime,list)):
                newBullet.lifetime = random.randint(*newBulletLifetime)
            else:
                newBullet.lifetime = newBulletLifetime

            newBullet.deathCollision = deathCollisionSet
            newBullet.properties = bulletProperties
            newBullet.doHome = doHomeSet
            newBullet.target = target
            if (homeProperties != None):
                newBullet.turnSpeed,newBullet.maxTurnSpeed,newBullet.inaccuracy = homeProperties

            #timer for enemy bullet smoke effect and the smoke trail mod
            newBullet.smokeTimer = -1

            #a group where the .kill and give money thing in update dont run
            newBullet.dontKillGroup = dontKillGroupSet

            #local list creation
            newBullet.cantDamage = []
            newBullet.enemiesCollided = []
            
            #turn to center of target, or to mousePos if specified
            if (target != None):
                if (target in deathCollisionSet):
                    rotateFunc(newBullet,target.rect.center,bulletSpread)
                else:
                    rotateFunc(newBullet,target,bulletSpread)
            
            newBullet.originalAngle = newBullet.angle
                 
    def update(self,uBound,dBound,lBound,rBound):
        #vector movement
        self.rect.move_ip((-math.cos(self.angle * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
        self.x,self.y = self.rect.center

        #ticks down lifetime, dies if this hits 0 (checked below)
            #putting "None" into parameter means infinite life
        if (self.lifetime != None):
            self.lifetime -= 1
        
        #deletion offscreen
        elif (self.rect.bottom < uBound) or (self.rect.top > dBound) or (self.rect.right < lBound) or (self.rect.left > rBound):
            self.kill()  

    def draw(self,surface):
        surface.blit(self.image,self.rect)