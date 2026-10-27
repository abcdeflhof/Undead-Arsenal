#playtest notes:
    #indicator for zombie health

#changelog:
    #level 5 made w/ bg
    #fixed weird bug where pierce mod actually made your guns have 0 pierce if it failed and didn't stack properly
        #made sure the fix wouldn't affect the echo mod
    #level 3 length: 900s -> 600s
        #also i slightly reduced enemy counts
    #1 second bootup of quitgame button on main menu to prevent accidental double-clicking into the abyss from the win screen
    #nerfed level 1 and 2, as in made them easier. yeah. less enemies

#---GENERAL SETUP--#
#importing and init()
import pygame
import math
import random

import playerCode
import bulletCode
import enemyCode
import gunPickupCode
import backgroundCode
import HUDStuffCode
import VFXCode

pygame.init()

#display variables
displayWidth = 800
displayHeight = 600

gameDisplay = pygame.display.set_mode((displayWidth,displayHeight))

#simple RGB colors for general purpose
black = (0,0,0)
white = (255,255,255)
red = (200,0,0)
redder = (255,0,0)
green = (0,200,0)
greener = (0,255,0)
blue = (0,0,200)
bluer = (0,0,255)
yellower = (255,255,0)
yellowish = (225,225,125)
lightGray = (180,180,180)
midGray = (120,120,120)
darkGray = (60,60,60)
deepRed = (150,25,25)
deepRedder = (100,0,0)
magenta = (200,0,200)
magentaer = (255,0,255)

#quite broadly important variables
clock = pygame.time.Clock()

gameReset = False
pause = False
bossMode = False
bossSpawned = False
levelReadytoEnd = 0

score = 0
bossModeStart = int()

currentLevel = 0
levelUnlocked = 1

openTimer = 0

money = 0

reloadTime = []
reloadStart = []
roundReloadTime =[]
roundReloadStart = []
roundNum = []
roundNumStart = []

gunsInUse = []
gunsInSlots = []
inventorySlots = []
modsBeingUsed = []

modQuantities = [0,0,0,0,0,0]

healthBarStuff = []
miscHUDStuff = []

shopButtons = []
shopDesc = str()
gunsUnlocked = [0,1,2,3]
gunModsUnlocked = [["Damage Mod",-1],["Pierce Mod",-2],["Bullet Speed Mod",-3]]
gunsSelected = [0,1,2,3]
modsSelected = [["Damage Mod",-1],["Pierce Mod",-2],["Bullet Speed Mod",-3]]

keysPressed = []

spawnCounts = []

gameFont = 'ithacaByGGBotNet.ttf'

mousePos = pygame.mouse.get_pos()

#---SPRITE, SOUND, AND GROUP CREATION--#
p1 = playerCode.player()
e1 = enemyCode.enemy1()
pBSource = bulletCode.bullet()
gP = gunPickupCode.gunPickup()
bG = backgroundCode.background()
hudS = HUDStuffCode.HUDStuff()
vFX = VFXCode.VFX()

#activeSprites is more of a group for "update" and "draw" things to be added to
    #still most useful for copies of sprites tho
activeSprites = pygame.sprite.Group()

activePlayers = pygame.sprite.Group()
activePBullets = pygame.sprite.Group()

activeEnemies = pygame.sprite.Group()
activeEBullets = pygame.sprite.Group()

activeGunPickups = pygame.sprite.Group()
activeHUDThings = pygame.sprite.Group()
activeVFX = pygame.sprite.Group()

gunFireSound = pygame.mixer.Sound('gunFire.mp3')
bulletHitSound = pygame.mixer.Sound('bulletHit.mp3')
gameOverSound = pygame.mixer.Sound('gameOver.mp3')

pygame.mixer.Sound.set_volume(gunFireSound,0.05)
pygame.mixer.Sound.set_volume(bulletHitSound,0.4)
pygame.mixer.Sound.set_volume(gameOverSound,0.2)

#creating custom events 
scoreIncrease = pygame.USEREVENT

#---FUNCTION STUFF--#
def quitGame():
    pygame.quit()
    quit()

def resetGame():
    global gameReset
    global pause
    global gunsInUse
    global gunsInSlots
    global reloadStart
    global reloadTime
    global inventorySlots
    global currentLevel
    global score
    global bossMode
    global bossSpawned
    global roundNum
    global roundNumStart
    global roundReloadTime
    global roundReloadStart
    global levelReadytoEnd
    global healthBarStuff
    global modQuantities
    global modsBeingUsed
    global openTimer

    #resets the quitgame button bootup
    openTimer = 0

    #brings you back to the main menu
    pause = False
    gameReset = True

    #resets values that affect the gameplay in level and stuff
    gunsInUse = []
    gunsInSlots = []
    inventorySlots = []
    modsBeingUsed = []
    healthBarStuff = []
    reloadStart = []
    reloadTime = []
    roundNum = []
    roundNumStart = []
    roundReloadTime = []
    roundReloadStart = []

    modQuantities = [0,0,0,0,0,0]
    currentLevel = 0
    score = 0
    p1.health = 100
    
    bossMode = False
    bossSpawned = False
    levelReadytoEnd = 0

    #kills everything
    for i in activeSprites:
        i.kill()

    #stops the music
    pygame.mixer.music.pause()

def updateActiveSprites():
    global mousePos
    global money
    global keysPressed

    #doesn't run during reset to prevent crashes
    if (gameReset == False):
        
        #player updates
        p1.move(0,displayHeight,0,displayWidth)
        rotate(p1,mousePos)

        #most other updates
        for i in activePBullets:
            i.update(0,displayHeight,0,displayWidth)

            #MONEY IS UPDATED HERE
            localMoneyUpdater = 0

            #damages enemy on collision, kills/reduces pierce for bullet (checks general sprite collision first to control lag)
                #handled here because it requires a bunch of stuff
            if (pygame.sprite.spritecollide(i,i.deathCollision,0)):
                if (pygame.sprite.spritecollide(i,i.deathCollision,0,pygame.sprite.collide_mask)):
                    
                    #gets list to do stuff
                    i.enemiesCollided = pygame.sprite.spritecollide(i,i.deathCollision,0)

                    for enemy in range(len(i.enemiesCollided)):

                        #for now at least, can't hit same enemy twice EVER
                        if not (i.enemiesCollided[enemy] in i.cantDamage):

                            if ("explosion" in i.properties):
                                doExplosion(i.enemiesCollided[enemy].rect.center,activeEnemies,activePBullets,round(i.damage*0.5),4,activeEnemies,1,i.properties)
                            elif ("littleExplosion" in i.properties):
                                doExplosion(i.enemiesCollided[enemy].rect.center,activeEnemies,activePBullets,round(i.damage*0.4),3,activeEnemies,0.7,i.properties)
                            else:
                                pygame.mixer.Sound.play(bulletHitSound)
                                vFX.create(activeVFX,activeSprites,'hitEffectSprite.png',i.enemiesCollided[enemy].rect.center,0,0.4,255,0,0,-15,0.3,8)
                                vFX.create(activeVFX,activeSprites,'bloodSplatterSprite.png',i.enemiesCollided[enemy].rect.center,random.randint(0,360),5,255,7,0,0,-0.1,6)

                            #health reduction, killing if health < or = 0
                            i.enemiesCollided[enemy].health -= i.damage

                            #kills enemy and adds money if its health is 0 or less
                            if (i.enemiesCollided[enemy].health < 1):
                                i.enemiesCollided[enemy].kill()
                                localMoneyUpdater += i.enemiesCollided[enemy].moneyGive
                            
                            #reduces pierce, being destroyed if it runs out
                            i.pierceLeft -= 1
                            if not (i.pierceLeft > 0):
                                i.kill()

                            #adds the enemy to cantDamage so that no repeat hits happen
                            i.cantDamage.append(i.enemiesCollided[enemy])

                            #this is for railgun bullet bouncing. the check distance, for now, is hardcoded in
                            if ("ricochet" in i.properties):
                                tempBulletPos = pygame.math.Vector2(i.rect.center)
                                shortestDistance = i.speed*10
                                tempBulletAngle = i.angle

                                tempTarget = None
                                for seekTarget in activeEnemies:
                                    checkingDistance = tempBulletPos.distance_to(seekTarget.rect.center)
                                    
                                    if (checkingDistance <= shortestDistance):
                                        if not (seekTarget in i.cantDamage) and not (seekTarget in i.enemiesCollided):
                                            rotate(i,seekTarget.rect.center)
                                            seekTargetAngle = i.angle
                                            seekTargetAngle += 360
                                            seekTargetAngle %= 360

                                            i.angle = tempBulletAngle
                                            i.newImage = pygame.transform.rotate(i.originalImage,i.angle)
                                            i.image = i.newImage
                                        
                                            i.rect = i.image.get_rect(center = (i.x,i.y))
                                            tempBulletAngle += 360
                                            tempBulletAngle %= 360
                                            
                                            if (round(abs(seekTargetAngle - tempBulletAngle)) <= 40):
                                                shortestDistance = checkingDistance
                                                tempTarget = seekTarget.rect.center
                                
                                if (tempTarget != None):
                                    rotate(i,tempTarget)

            #actually gives you the money
            money += localMoneyUpdater

            #smoke trail mod
            if ("smokeTrail" in i.properties):
                if (i.smokeTimer > 0):
                    i.smokeTimer -= 1
                elif (i.smokeTimer == 0):
                    pBSource.fire(i.rect.center,mousePos,activeEnemies,0,0,activePBullets,activeSprites,rotate,1,180,2,2,0,round(i.damage/5),20,['fade'],'dustParticleSprite.png',None,None,None,0.6)
                    i.smokeTimer = (round(50*(0.5 ** modQuantities[5])))
                    #i.smokeTimer = 15
                elif (i.smokeTimer == -1):
                    i.smokeTimer = (round(50*(0.5 ** modQuantities[5])))
                    #i.smokeTimer = 15

            #bullet property of fading
            if ('fade' in i.properties):
                i.image.set_alpha((i.image.get_alpha() - 12))
            
            #dies at 0 lifetime. this was moved here to include the particle effect w/o crazy parameters
            if (i.lifetime != None) and (i.lifetime < 1):
                
                #can be set to not do the dust effect if desired (might make more effects too)
                if ("dust" in i.properties):
                    vFX.create(activeVFX,activeSprites,'dustParticleSprite.png',i.rect.center,random.randint(0,359),1,255,2,0,-10,-0.05,20)
                
                i.kill()
        
        for i in activeEBullets:
            
            #same as PBullets
            i.update(0,displayHeight,0,displayWidth)

            #smoke trail for visibility
            if (i.smokeTimer > 0):
                i.smokeTimer -= 1
            elif (i.smokeTimer == 0):
                i.smokeTimer = 15
                vFX.create(activeVFX,activeSprites,'evilDustParticleSprite.png',i.rect.center,random.randint(0,360),0.6,255,2,0,-8,-0.01,25)
            elif (i.smokeTimer == -1):
                i.smokeTimer = 15
            #bullets can home into something
            if (i.doHome == True):
                softRotate(i,p1.rect.center,i.turnSpeed,i.maxTurnSpeed,i.inaccuracy)

            #animation stuff on collision
            if (pygame.sprite.spritecollide(i,i.deathCollision,0,pygame.sprite.collide_mask)):
                if ("explosion" in i.properties):
                    doExplosion(i.rect.center,activePlayers,activeEBullets,20,2,activePlayers)
                else:
                    pygame.mixer.Sound.play(bulletHitSound)
                    vFX.create(activeVFX,activeSprites,'hitEffectSprite.png',i.rect.center,0,0.4,255,0,0,-15,0.3,8)
                    vFX.create(activeVFX,activeSprites,'bloodSplatterSprite.png',i.rect.center,random.randint(0,360),5,255,7,0,0,-0.1,6)

                if not (p1 in i.cantDamage):
                    p1.health -= i.damage

                    i.cantDamage.append(p1)

                if (i.pierce < 2):
                    i.kill()

            #animation stuff on death
            elif (i.lifetime != None) and (i.lifetime < 1): 
                
                if ("explosion" in i.properties):
                    doExplosion(i.rect.center,activePlayers,activeEBullets,20,2,activePlayers)
                if ("evilDust" in i.properties):
                    vFX.create(activeVFX,activeSprites,'evilDustParticleSprite.png',i.rect.center,random.randint(0,359),1,255,2,0,-10,-0.05,20)
                
                i.kill()
            
        p1.update(activeEnemies,vFX.create,[activeVFX,activeSprites,'bloodSplatterSprite.png',p1.rect.center,random.randint(0,360),4,255,7,0,0,-0.1,6])
        
        for pckup in activeGunPickups:
            pckup.update(activePBullets,addGun,addMod)

            #when a pckup is the first gun touching a player, it can be interacted with
            pckupsTouched = pygame.sprite.spritecollide(p1,activeGunPickups,0)

            pckup.beingTouched = False
            if (pckupsTouched != []):
                pckupsTouched[0].beingTouched = True

                #unselects the gun when a new one is touched
                if (pckup is pckupsTouched):
                    pckup.beingTouched = False

            #the actual interaction and text display
            if (pckup.beingTouched == True) and (pckup.currentState == "gun"):
                pckup.gotGrabbed,pckup.gotDestroyed = displayPckupInteract(pckup,keysPressed,
                                                                           ["Pickup [E]","Destroy [Q]"],
                                                                           20,
                                                                           [pygame.K_e,pygame.K_q],
                                                                           [pckup.gotGrabbed,pckup.gotDestroyed],
                                                                           [True,True])
            elif (pckup.beingTouched == True) and (pckup.currentState == "mod"):
                pckup.mod1Grabbed,pckup.mod2Grabbed,pckup.mod3Grabbed,pckup.gotDestroyed = displayPckupInteract(pckup,keysPressed,
                                                                           [modsSelected[0][0] + " [1]",modsSelected[1][0] + " [2]",modsSelected[2][0] + " [3]","Destroy [Q]"],
                                                                           20,
                                                                           [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_q],
                                                                           [pckup.mod1Grabbed,pckup.mod2Grabbed,pckup.mod3Grabbed,pckup.gotDestroyed],
                                                                           [True,True,True,True])

            #when shot, turns into a gun and changes necessary values
            if (pckup.stateChange == "gunMade"):
                pckup.image = pckup.gunImage
                pckup.rect = pckup.image.get_rect()
                pckup.rect.center = (pckup.x,pckup.y)

                pckup.currentState = "gun"
                pckup.stateChange = "none"
                
                for i in range(4):
                    vFX.create(activeVFX,activeSprites,'crateScrapSprite.png',pckup.rect.center,random.randint(0,359),1,255,3,0,-10,0,28)

            elif (pckup.stateChange == "modMade"):
                            pckup.image = pckup.gunImage
                            pckup.rect = pckup.image.get_rect()
                            pckup.rect.center = (pckup.x,pckup.y)
            
                            pckup.currentState = "mod"
                            pckup.stateChange = "none"
                            
                            for i in range(4):
                                vFX.create(activeVFX,activeSprites,'modCrateScrapSprite.png',pckup.rect.center,random.randint(0,359),1,255,3,0,-10,0,28)
            
            elif (pckup.stateChange == "death"):
                gunBreakAnimate(pckup,3,2,2)
                pckup.kill()

        activeVFX.update()

        activeEnemies.update()

        #enemies push each other and turn to player
        for i in activeEnemies:
            
            #enemies can be set to not go at player directly. this can be permanent or temporary
            if (i.turnToPlayer == True):
                #if the softTurn 4th index has a number greater than 0, turns to the player at a gradual rate
                    #4th slot, then, acts as a timer
                if (i.softTurnToPlayer[3] != 0):
                    softRotate(i,p1.rect.center,i.softTurnToPlayer[0],i.softTurnToPlayer[1],i.softTurnToPlayer[2])

                    #ticks down
                    i.softTurnToPlayer[3] -= 1

                #if not, snaps to player
                    #lower priority thing to do
                else:
                    rotate(i,p1.rect.center)

            #enemies push against each other and all have a "pushPriority". the one with lower priority gets pushed
            if (i.pushPriority != -1):
                i.softCollideAmong(activeEnemies)
        
        #change display of each gun slot
        for gun in range(len(gunsInSlots)):
            if (len(gunsInUse) <= gun):
                gunsInSlots[gun].updateDisplay([True],['dualPistolsSprite.png'],[0])
            else:
                gunsInSlots[gun].updateDisplay([gunsInUse[gun] == 0,gunsInUse[gun] == 1,gunsInUse[gun] == 2,gunsInUse[gun] == 3,gunsInUse[gun] == 100,gunsInUse[gun] == 101,gunsInUse[gun] == 102,gunsInUse[gun] == 103,gunsInUse[gun] == 1000,gunsInUse[gun] == 1001,gunsInUse[gun] == 1002,gunsInUse[gun] == 1003],
                                            ['dualPistolsSprite.png','shotgunSprite.png','RifleSprite.png','swordSprite.png','sixerSprite.png','flamethrowerSprite.png','sniperRifleSprite.png','flameSwordSprite.png','uziSprite.png','rocketLauncherSprite.png','railgunSprite.png','dualSwordsSprite.png'],
                                            [255,255,255,255,255,255,255,255,255,255,255,255])

        #health...bar.stuff. yeah. pretty self-explanatory
        healthBarStuff[0].updateDisplay([p1.health == 100,0 < p1.health < 100,p1.health < 1],
                        ['healthBarBloodSprite.png','healthBarBloodSprite.png','healthBarBloodSprite.png'],
                        [255,255,0],
                        [0,0,0],
                        [(270,36),(p1.health*2.7,36),(1,1)],
                        [(displayWidth/2,displayHeight - 60),((displayWidth/2 - 135) + (p1.health * 1.35),displayHeight - 60),(0,0)])

        #updates things that don't quite fit into other categories. in the future, maybe just make ONE big list of HUD items each with indices...
        for HUD in range(len(miscHUDStuff)):
            if (miscHUDStuff[HUD].name == 'theTomb'):
                miscHUDStuff[HUD].updateDisplay([(score < 50),(miscHUDStuff[HUD].timer < 6),(11 > miscHUDStuff[HUD].timer > 7),(miscHUDStuff[HUD].timer > 10)],
                                   ['sleepyTombSprite.png','awakenedTombF1Sprite.png','awakenedTombF2Sprite.png','awakenedTombF3Sprite.png'],
                                   [255,255,255,255])

                if (49 < score < 53) and (currentLevel == 5):
                    for magicDust in range(3):
                        vFX.create(activeVFX,activeSprites,'magicDustSprite.png',miscHUDStuff[HUD].rect.center,random.randint(0,359),1,255,random.randint(4,9),0,-20,0,60)
                
                if (score > 50):
                    #cycles through timer for skin rotation
                    miscHUDStuff[HUD].timer += 1
                    if (miscHUDStuff[HUD].timer >= 16):
                        miscHUDStuff[HUD].timer = 0

#all the sprites being drawn in order
def drawActiveSprites():

    if (gameReset == False):
        bG.draw(gameDisplay)
        activeHUDThings.draw(gameDisplay)
        
        #health display
        displayText(('Humanity Remaining: ' + str(p1.health) + '%'),gameFont,white,30,(displayWidth/2),(displayHeight - 62.5),None)

        #score display
        displayText(('Time: ' + str(score) + "/" + str(bossModeStart)),gameFont,white,40,10,(displayHeight - 30),None,"left")

        #money display
        displayText(('$' + str(money)),gameFont,white,40,10,(displayHeight - 70),None,"left")

        #mod quantities display
        for mod in range(len(modsBeingUsed)):
            displayText(str(modQuantities[-(1 + modsSelected[mod][1])]),gameFont,white,20,(modsBeingUsed[mod].rect.center[0] + 5),(modsBeingUsed[mod].rect.center[1] + 10),None,"left")

        activeVFX.draw(gameDisplay)
        activeGunPickups.draw(gameDisplay)
        activePBullets.draw(gameDisplay)
        activeEBullets.draw(gameDisplay)
        activePlayers.draw(gameDisplay)
        activeEnemies.draw(gameDisplay)
    
    elif (gameReset == True): #DEVNOTE: maybe make a loading screen for this?
        bG.draw(gameDisplay)

#rotates self toward the target, with up to spread degrees of error
def rotate(self, target, spread=0):
    #this is to stop dividing by 0 errors
    if (target[0] == self.x):
        if (target[1] < self.y):
            self.angle = 270
        elif (target[1] > self.y):
            self.angle = 90
        else:
            self.angle = 0

    #this makes it so that if your mouse is to the right, the sprite is flipped
        #cause otherwise it can't turn very well
    elif target[0] > self.x:
        self.angle = (math.atan((target[1] - self.y)/(target[0] - self.x))*(-180/math.pi) + 180)
    else:
        self.angle = (math.atan((target[1] - self.y)/(target[0] - self.x))*(-180/math.pi))
    
    self.angle += random.randint(-spread,spread)
    
    #this is the actual visual turn
    self.newImage = pygame.transform.rotate(self.originalImage,self.angle)
    self.image = self.newImage

    self.rect = self.image.get_rect(center = (self.x,self.y))

#softly rotates towards a target location, with a maxSpeed and allowedError degrees of inacurracy
def softRotate(self,target,speedScale,maxSpeed,allowedError):
    #this all makes a projectedAngle (the target angle) in the same way rotate does its angles
    if (target[0] == self.x):
        if (target[1] < self.y):
            self.projectedAngle = 270
        elif (target[1] > self.y):
            self.projectedAngle = 90
        else:
            self.projectedAngle = 0
    elif (target[0] > self.x):
        self.projectedAngle = (math.atan((target[1] - self.y)/(target[0] - self.x))*(-180/math.pi) + 180)
    else:
        self.projectedAngle = (math.atan((target[1] - self.y)/(target[0] - self.x))*(-180/math.pi))

    #centers the perspective of the thing rotating so that everythign is relative to its angle (self.angle is the middle of the rotation)
        #so much simpler than I was making it out to be ;-;
    angleDiff = self.projectedAngle - self.angle
    angleDiff = (angleDiff + 180) % 360 - 180

    #the actual sprite angle turns towards the chosen possibleAngle a bit
    turnAmount = (abs(angleDiff) * speedScale)
    
        #has a max turning speed
    if (turnAmount > maxSpeed):
        turnAmount = maxSpeed

        #uses angleDiff to go positive or negative, but not if within allowedError degrees (basically inacurracy, has to be high to do much)
    if (abs(angleDiff) > allowedError):
        if (angleDiff > 0) or (angleDiff == -180):
            self.angle += turnAmount
        elif (angleDiff < 0):
            self.angle -= turnAmount
    
    self.newImage = pygame.transform.rotate(self.originalImage,self.angle)
    self.image = self.newImage

    self.rect = self.image.get_rect(center = (self.x,self.y))

#used to roll gun chances, where you can toggle overflow on or off
def rollBulletChance(chance,multVar,overflow=False):
    if (multVar > 0):
        tempChanceVar = random.randint(1,100)
        chanceBarVar = chance*multVar
        #basically, just checks if the chance surpasses the constant*variable total
            #returns true or false
        if (overflow == False):
            if (tempChanceVar >= chanceBarVar):
                return True
            else:
                return False

        tempOutputVar = 1
        #still checks the chance, but leftover chance makes it check again with -100%
            #returns an int, tempOutputVar, that determines the amount of activation
        if (overflow == True):
            while (chanceBarVar > 0):
                if (tempChanceVar <= chanceBarVar):
                    tempOutputVar += 1
                
                chanceBarVar -= 100
                
                #rerolls chance each iteration too
                tempChanceVar = random.randint(1,100)
            return tempOutputVar

    else:
        if overflow:
            return 1
        elif not overflow:
            return False

#adds a gun to gunsInUse if possible, but does have a limit of 3 guns
    #SPECIFIC VALUES FOUND IN PICKUP UPDATE CODE
def addGun(gunType,gunReloadStart,numOfRounds=None,numOfRoundStart=None,roundCooldownTime=None,roundCooldownStart=None):
    global reloadTime
    global reloadStart
    global gunsInUse
    global roundNum
    global roundNumStart
    global roundReloadTime
    global roundReloadStart

    #deletes first (oldest) gun info if at max - OBSOLETE
    # if len(gunsInUse) >= 4:
    #     del gunsInUse[0]
    #     del reloadTime[0]
    #     del reloadStart[0]
    #     del roundNum[0]
    #     del roundNumStart[0]
    #     del roundReloadTime[0]
    #     del roundReloadStart[0]

    #     #resets the gun reload time. needed cause desync otherwise can cause backlog of delay
    #     reloadTime[0] = 0
    #     reloadTime[1] = -1
    #     reloadTime[2] = -2
    
    if (len(gunsInUse) < 4):
        gunsInUse.append(gunType)
        reloadTime.append(0)
        reloadStart.append(gunReloadStart)
    
        if (numOfRounds == None):
            roundNum.append(0)
            roundNumStart.append(0)
            roundReloadTime.append(0)
            roundReloadStart.append(0)
        else:
            roundNum.append(numOfRounds)
            roundNumStart.append(numOfRoundStart)
            roundReloadTime.append(roundCooldownTime)
            roundReloadStart.append(roundCooldownStart)

def addMod(modSlot,numAdd):
    global modsSelected
    global modQuantities

    modQuantities[-(1 + modsSelected[modSlot][1])] += numAdd

#both buyGun and gunsSelectedAdd for the Shop
def buyGun(gunNum,cost):
    global gunsUnlocked
    global money
    
    #simply adds to the list of guns in your unlock list
        #used to make the shop buttons interactable or not
    gunsUnlocked.append(gunNum)

    #also costs money
    money -= cost

def gunsSelectedAdd(gunNum,gunsSelectedSlot):
    global gunsSelected

    #deletes the gun at the slot specified, then adds the ID of the gun
    del gunsSelected[gunsSelectedSlot]
    gunsSelected.insert(gunsSelectedSlot,gunNum)

#both buyGunMod and modsSelectedAdd for the Shop
def buyGunMod(modNum,costButLikeForAModNotAGun):
    global gunModsUnlocked
    global money

    #simply adds to the list of gun mods in your unlock list
        #used to make the shop buttons interactable or not
    gunModsUnlocked.append(modNum)

    #costs money
    money -= costButLikeForAModNotAGun

def gunModsSelectedAdd(modNum):
    global modsSelected

    if (len(modsSelected) > 2):
        del modsSelected[0]

    modsSelected.append(modNum)

#unselects all guns and gun mods. for use in the shop
def shopUnselectAll():
    global gunsSelected
    global modsSelected

    gunsSelected = [None,None,None,None]
    modsSelected = []

#exit the pause menu (duh)
def unpause():
    global pause

    pause = False

    #puts music back to full volume
    pygame.mixer.music.set_volume(1)

#creates a button with...all that stuff to describe it. good luck.
def button(surface,x,y,buttonWidth,buttonHeight,color1,color2,text,textColor,textSize,action,actionParameters=None,actionCondition=None,unfulfilledConditionAction=None,unfulfilledConditionActionParameters=None):
    #getting mouse position and click bool
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    #lights up when hovering
    if ((x + buttonWidth/2) > mouse[0] > (x - buttonWidth/2)) and ((y + buttonHeight/2) > mouse[1] > (y - buttonHeight/2)):
        
        #drawn with x and y parameters as the CENTER, NOT TOP CORNER
        pygame.draw.rect(surface,color2,((x - (buttonWidth/2)),(y - (buttonHeight/2)),buttonWidth,buttonHeight))

        #thing on actual press
            #relies on a condition IF a condition was specified
        if (click[0] == 1) and (action != None) and (actionCondition != None):
            
            if (actionCondition):
                if (actionParameters == None):
                    action()
                else:
                    action(*actionParameters)
            
            else:
                if (unfulfilledConditionAction != None):
                    unfulfilledConditionAction(*unfulfilledConditionActionParameters)
        
        elif (click[0] == 1) and (action != None):
            if (actionParameters == None):
                action()
            else:
                action(*actionParameters)

        hoveringNow = True
    
    #not lit up
    else:
        pygame.draw.rect(surface,color1,((x - (buttonWidth/2)),(y - (buttonHeight/2)),buttonWidth,buttonHeight))

        hoveringNow = False
    
    #text and/or pictures on the button if applicable
    if (text != None):
        displayText(text,gameFont,textColor,textSize,x,y)

    #returns a boolean for specific use in hovering interactions
    return hoveringNow

def shopButton(x,y,shopButtonType,IDNum,slotNum,costText,actualCost,buttonName,buttonPicture,picScale,shopDescSet):
    global shopDesc

    if (shopButtonType == "gun"):
    #if you have bought the gun this happens
        if (IDNum in gunsUnlocked):
            
            #if you have selected the gun
            if (IDNum in gunsSelected):
                currentlyHovering = button(gameDisplay,x,y,60,45,yellower,yellower,None,None,None,None)
            
            #if you DONT have the gun selected
            else:
                currentlyHovering = button(gameDisplay,x,y,60,45,midGray,yellowish,None,None,None,gunsSelectedAdd,[IDNum,slotNum])
        
        #if you havent bought the gun, this happens
        else:
            currentlyHovering = button(gameDisplay,x,y,60,45,green,greener,None,None,None,buyGun,[IDNum,actualCost],money >= actualCost,None)
            displayText(costText,gameFont,white,25,x,(y + 32))

    elif (shopButtonType == "gunMod"):
        if (IDNum in gunModsUnlocked):
                    
            #if you have selected the gun
            if (IDNum in modsSelected):
                currentlyHovering = button(gameDisplay,x,y,60,45,yellower,yellower,None,None,None,None)
            
            #if you DONT have the gun selected
            else:
                currentlyHovering = button(gameDisplay,x,y,60,45,midGray,yellowish,None,None,None,gunModsSelectedAdd,[IDNum])
        
        #if you havent bought the gun, this happens
        else:
            currentlyHovering = button(gameDisplay,x,y,60,45,green,greener,None,None,None,buyGunMod,[IDNum,actualCost],money >= actualCost,None)
            displayText(costText,gameFont,white,25,x,(y + 32))
    
    buttonName.updateDisplay([True],[buttonPicture],[255],[0],[picScale])

    if (currentlyHovering):
        shopDesc = shopDescSet

#creates a text box. pretty self explanatory
def textBox(center=tuple,boxWidth=int,boxHeight=int,boxColor=tuple,borderSize=int,borderColor=tuple,text=str,textSize=int,textColor=tuple,textMargins=int,textLengthMax=int):
    borderBoxWidth = boxWidth + (borderSize*2)
    borderBoxHeight = boxHeight + (borderSize*2)
    topLeftCorner = ((center[0] - boxWidth/2),(center[1] - boxHeight/2))

    pygame.draw.rect(gameDisplay,borderColor,((topLeftCorner[0] - borderSize),(topLeftCorner[1] - borderSize),borderBoxWidth,borderBoxHeight))
    pygame.draw.rect(gameDisplay,boxColor,(topLeftCorner[0],topLeftCorner[1],boxWidth,boxHeight))

    textLines = [text]
    tempTextVar = str()
    currentLine = 0
    lineLimiter = 0

    while (len(textLines[currentLine]) > textLengthMax):
        #duplicates line of text except for the beginning of it. cuts at the last space before the max and chops off that space
        lineLimiter = textLines[currentLine][:textLengthMax].rfind(" ")
        tempTextVar = textLines[currentLine][(lineLimiter + 1):]

        #puts the text just collected into the next line
        textLines.append(tempTextVar)

        #chops off the duplicated text from original line
        textLines[currentLine] = textLines[currentLine][:lineLimiter]

        #iterates to the next line
        currentLine += 1

    for line in range(len(textLines)):
        displayText(textLines[line],gameFont,textColor,textSize,(topLeftCorner[0] + textMargins),(topLeftCorner[1] + (textMargins*(line) + (textSize/2)*(line+1))),None,"left")

#funcs for specific events and such
def doExplosion(sourceSet,killGroup,bulletGroup,damage,pierce,dontKillGroup=None,scale=1,propertiesSet=[]):

    tempProperties = [*propertiesSet]
    #copies the properties of something (parent bullet) but removes either explosion or littleExplosion
        #in that order so big explosions can do little explosions
    if (tempProperties != None):
        if ("explosion" in tempProperties):
            tempProperties.remove("explosion")
        elif ("littleExplosion" in tempProperties):
            tempProperties.remove("littleExplosion")

    if (dontKillGroup == None):
        vFX.create(activeVFX,activeSprites,'explosionFrame1Sprite.png',sourceSet,0,scale,255,0,0,0,0,4,pBSource.fire,[sourceSet,None,killGroup,0,0,bulletGroup,activeSprites,rotate,1,0,pierce,0,0,damage,6,tempProperties,'explosionFrame3Sprite.png',None,None,None,scale],['explosionFrame2Sprite.png'],[3])
    else:
        vFX.create(activeVFX,activeSprites,'explosionFrame1Sprite.png',sourceSet,0,scale,255,0,0,0,0,4,pBSource.fire,[sourceSet,None,killGroup,0,0,bulletGroup,activeSprites,rotate,1,0,pierce,0,0,damage,6,tempProperties,'explosionFrame3Sprite.png',dontKillGroup,None,None,scale],['explosionFrame2Sprite.png'],[3])

def gunBreakAnimate(self,metalScrapNum,woodScrapNum,scrapSpeed):
    for i in range(metalScrapNum):
        vFX.create(activeVFX,activeSprites,'gunScrap1Sprite.png',self.rect.center,random.randint(0,359),1,255,scrapSpeed,0,-15,0,20)
    for i in range(woodScrapNum):
        vFX.create(activeVFX,activeSprites,'gunScrap2Sprite.png',self.rect.center,random.randint(0,359),1,255,scrapSpeed,0,-15,0,20)

#fires an enemy rocket that hones in on the player
def shootZombieRocket(sourceSet,bulletNumSet,bulletSpreadSet,bulletSpeedSet,bulletSpeedVarianceSet,bulletLifetimeSet,homePropertiesSet):
    pBSource.fire(sourceSet,p1.rect.center,activePlayers,0,0,activeEBullets,activeSprites,rotate,bulletNumSet,bulletSpreadSet,1,bulletSpeedSet,bulletSpeedVarianceSet,0,bulletLifetimeSet,["explosion"],"zombieRocketSprite.png",p1,True,homePropertiesSet)

#summon birds with summoner circle
def summonerSummon(goTo,vFXTurnSpeed=int,summonTime=int,summonType=int,summonNum=int,summonRadius=int,summonAngle=int):
    if (isinstance(goTo,pygame.sprite.Sprite)):
        vFX.create(activeVFX,activeSprites,'summonerSpellSprite.png',goTo.rect.center,0,1,255,0,vFXTurnSpeed,0,0,summonTime,doSpawn,[summonType,3,goTo.rect.center,summonRadius,summonAngle])
    elif (isinstance(goTo,tuple)):
        vFX.create(activeVFX,activeSprites,'summonerSpellSprite.png',goTo,0,1,255,0,vFXTurnSpeed,0,0,summonTime,doSpawn,[summonType,summonNum,goTo,summonRadius,summonAngle])
    elif (isinstance(goTo,list)):
        goTo = (random.randint(goTo[0][0],goTo[0][1]),random.randint(goTo[1][0],goTo[1][1]))
        vFX.create(activeVFX,activeSprites,'summonerSpellSprite.png',goTo,0,1,255,0,vFXTurnSpeed,0,0,summonTime,doSpawn,[summonType,summonNum,goTo,summonRadius,summonAngle])

#breaks your primary gun w/ animation
def breakGun(source):
    if (len(gunsInUse) > 1):
        del gunsInUse[0]
        del reloadTime[0]
        del reloadStart[0]
        del roundNum[0]
        del roundNumStart[0]
        del roundReloadTime[0]
        del roundReloadStart[0]
        gunBreakAnimate(source,6,4,4)

#updates the screen at rate FPS
def updateScreen(FPS):
    pygame.display.update()
    clock.tick(FPS)

#how to display text w/ any font,color,size, and center coords
def displayText(text,font,color,size,x,y,sleepyTime=None,alignment=None):
    #getting stuff ready and defined
    theFont = pygame.font.Font(font,size)
    textSurface = theFont.render(text, True, color)
    textRect = textSurface.get_rect()

    #placement and drawing (can have the text be aligned to its left or right side, defaults to not)
    if (alignment == None):
        textRect.center = (x,y)
    elif (alignment == "left"):
        textRect.midleft = (x,y)
    elif (alignment == "right"):
        textRect.midright == (x,y)
    
    gameDisplay.blit(textSurface,textRect)
    #if sleepyTime is specified, game pauses for that many ms
    if (sleepyTime != None):
        if (sleepyTime > 0):
            pygame.time.wait(sleepyTime)

#makes an object display text and be able to be interacted with
def displayPckupInteract(self,keysPressedVar,interactText=list,textMargin=int,interactKey=list,interactVar=list,interactVarChange=list):
    for i in range(len(interactText)):
        displayText(interactText[i],gameFont,white,20,self.rect.center[0],(self.rect.center[1] + (textMargin * (i + 1))))

        if keysPressedVar[interactKey[i]]:
            interactVar[i] = interactVarChange[i]

    return interactVar

#centralized spawn function (defines what different types of the spawns are)
    #also defines what each type of enemy does
def doSpawn(type,spawnNum,whereSpawn=None,whereSpawnRadius=0,initialAngleSet=0):

    #-1 is the gun pickup
    if (type == -1): #gun crate
        tempSpawnVar = gP.spawn(activeSprites,activeGunPickups,spawnNum,gunsSelected,"box","crateSprite.png",0,displayHeight,0,displayWidth,50,p1,vFX.create,[activeVFX,activeSprites])
    elif (type == -2): #gun mod crate
        tempSpawnVar = gP.spawn(activeSprites,activeGunPickups,spawnNum,[-1,-2],"modBox","modCrateSprite.png",0,displayHeight,0,displayWidth,50,p1,vFX.create,[activeVFX,activeSprites])

    #enemies start at 0
    elif (type == 0): #swarmer
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'swarmerSprite.png',spawnNum,0,50,1,2,10,1,1,0,None,None,whereSpawn,whereSpawnRadius)
    elif (type == 1): #bruiser
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'bruiserSprite.png',spawnNum,0,200,2,6,10,10,1,1,None,None,whereSpawn,whereSpawnRadius)
    elif (type == 2): #giant
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'giantSprite.png',spawnNum,0,1200,0.5,15,45,25,1,2,None,None,whereSpawn,whereSpawnRadius)
    elif (type == 3): #gunslinger
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'gunslingerSprite.png',spawnNum,1,150,2,2,10,15,1,1,enemyCode.enemy1.type1Init,[220,p1,2,60,pBSource.fire,[p1,activePlayers,[-10,10],8,activeEBullets,activeSprites,rotate,1,0,1,4,0,10,None,[],'enemyBulletSprite.png',activePlayers],60,60],whereSpawn,whereSpawnRadius)
    elif (type == 4): #charger
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'chargerSprite.png',spawnNum,1,500,3,20,30,25,1,1,enemyCode.enemy1.type1Init,[150,p1,0,None,enemyCode.enemy1.chargerCharge,[8,60,2,vFX.create,activeVFX,activeSprites,3],90,90,False,False,enemyCode.enemy1.chargerStop],whereSpawn,whereSpawnRadius)
    elif (type == 5): #giant gunslinger
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'giantGunslingerSprite.png',spawnNum,1,2200,0.5,15,45,50,1,2,enemyCode.enemy1.type1Init,[250,p1,0,None,pBSource.fire,[p1,activePlayers,12,20,activeEBullets,activeSprites,rotate,1,0,1,3,0,30,None,[],'bigEnemyBulletSprite.png',activePlayers],90,90],whereSpawn,whereSpawnRadius)
    elif (type == 6): #kamikaze
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'kamikazeSprite.png',spawnNum,1,500,4,0,30,50,1,1,enemyCode.enemy1.type1Init,[15,p1,0,None,doExplosion,[activePlayers,activeEBullets,50,2,activePlayers],0,0,True,True],whereSpawn,whereSpawnRadius)
    elif (type == 7): #summoner
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'summonerSprite.png',spawnNum,3,1000,2,10,60,100,1,2,enemyCode.enemy1.type3Init,[summonerSummon,[3,180,1007,3,0,random.randint(0,359)],60,270,True,False,True,[0,displayHeight,0,displayWidth],50],whereSpawn,whereSpawnRadius)

    #bosses start at 100
    elif (type == 100): #elite gunslinger
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'boss1Sprite.png',spawnNum,1,6000,2,25,30,500,1,3,enemyCode.enemy1.type1Init,[300,p1,4,120,pBSource.fire,[p1,activePlayers,[-15,15],10,activeEBullets,activeSprites,rotate,1,0,1,5,0,10,None,[],'enemyBulletSprite.png',activePlayers],6,6],whereSpawn,whereSpawnRadius)
    elif (type == 101): #elite charger
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'boss2Sprite.png',spawnNum,1,7500,4,20,30,400,1,3,enemyCode.enemy1.type1Init,[190,p1,5,90,enemyCode.enemy1.chargerCharge,[10,36,4,vFX.create,activeVFX,activeSprites,6],105,105,False,False,enemyCode.enemy1.chargerStop],whereSpawn,whereSpawnRadius)
    elif (type == 102): #THE OBELISK
        #this one has LOTS of stuff to do, so it shooting rockets is now the shootZombieRocket function
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,"boss3Sprite.png",spawnNum,2,20000,0,5,15,2500,1,4,enemyCode.enemy1.type2Init,[
                                                                                                                                                        [shootZombieRocket,shootZombieRocket,doSpawn],
                                                                                                                                                        [[3,120,6,1,[60,120],[2,5,20]],[8,180,6,2,[15,50],[0,0,360]],[1006,2]],
                                                                                                                                                        [130,240,100],
                                                                                                                                                        [130,240,100],
                                                                                                                                                        [True,True,"absolutely not"],
                                                                                                                                                        [False,False,False],
                                                                                                                                                        False],whereSpawn,whereSpawnRadius)
    elif (type == 103): #the great summoner
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,"boss4Sprite.png",spawnNum,2,50000,1,15,30,3000,1,3,enemyCode.enemy1.type2Init,[
                                                                                                                                                                        [enemyCode.enemy1.toggleMode,summonerSummon,summonerSummon],
                                                                                                                                                                        [[pBSource.fire,[p1,activePlayers,0,10,activeEBullets,activeSprites,rotate,1,10,2,10,3,5,120,['evilDust'],'magicBirdSprite.png',activePlayers,True,[0.1,4,80]],2,200,False,],[[[0,displayWidth],[0,displayHeight]],9,60,11030,1,0,0],[[[0,displayWidth],[0,displayHeight]],9,60,11031,1,0,0]],
                                                                                                                                                                        [320,120,110],
                                                                                                                                                                        [320,120,110],
                                                                                                                                                                        [False,"absolutely not","absolutely not"],
                                                                                                                                                                        [False,False,False],
                                                                                                                                                                        True,
                                                                                                                                                                        True],whereSpawn,whereSpawnRadius)

    #special spawns start at 1000 (vary dependent on use)
    elif (type == 1006): #kamikaze zombie that doesn't give money (used for THE OBELISK fight)
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'kamikazeSprite.png',spawnNum,1,500,4,0,30,0,1,1,enemyCode.enemy1.type1Init,[15,p1,0,None,doExplosion,[activePlayers,activeEBullets,50,2,activePlayers],0,0,True,True],whereSpawn,whereSpawnRadius)
    elif (type == 1007): #zombie birds that summoner zombies summon
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'zombieBirdSprite.png',spawnNum,0,200,7,5,30,0,1,-1,enemyCode.enemy1.setSoftRotate,([0.2,5,30,-1]),whereSpawn,whereSpawnRadius)
    elif (type == 11030): #summoner that gets summoned by the great summoner
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'summonerSprite.png',spawnNum,3,1000,2,10,60,0,1,2,enemyCode.enemy1.type3Init,[summonerSummon,[3,180,1007,3,0,random.randint(0,359)],60,270,True,False,True,[0,displayHeight,0,displayWidth],50],whereSpawn,whereSpawnRadius)
    elif (type == 11031): #giant gunslinger that gets summoned by the great summoner
        tempSpawnVar = e1.spawn(activeEnemies,activeSprites,0,displayHeight,0,displayWidth,'giantGunslingerSprite.png',spawnNum,1,2200,0.5,15,45,0,1,2,enemyCode.enemy1.type1Init,[250,p1,0,None,pBSource.fire,[p1,activePlayers,12,20,activeEBullets,activeSprites,rotate,1,0,1,3,0,30,None,[],'bigEnemyBulletSprite.png',activePlayers],90,90],whereSpawn,whereSpawnRadius)
    
    #can be set to turn to an angle on spawn
    if (initialAngleSet != 0):
        tempSpawnVar.x,tempSpawnVar.y = tempSpawnVar.rect.center

        tempSpawnVar.angle = initialAngleSet

        tempSpawnVar.newImage = pygame.transform.rotate(tempSpawnVar.originalImage,tempSpawnVar.angle)
        tempSpawnVar.image = tempSpawnVar.newImage
        tempSpawnVar.rect = tempSpawnVar.image.get_rect(center = (tempSpawnVar.x,tempSpawnVar.y))

    return tempSpawnVar

#function to handle ALL spawns and spawn increases
def handleSpawns(spawnCountIDs=list,spawnType=list,scoreInterval=list,firstSpawnScore=list,firstSpawnAmount=list,scoreForSpawnIncrease=list,spawnIncreaseAmount=list,lastIncreaseScore=list,lastSpawnScore=list):
    global score

    tempSpawnNumList = spawnCountIDs

    #for each type of enemy...
    for i in range(len(spawnCountIDs)):
        
        #...the first spawn amount is set if at the right score
            #(makes the spawn happen, too, because this is before actual spawn)
        if (score == firstSpawnScore[i]):
            tempSpawnNumList[i] += firstSpawnAmount[i]

        #...the spawn count of that enemy increases if the increase interval is met
            #(and if the first spawn has already occurred)

            #(also doesn't run if the scoreForSpawnIncrease is None)
        if (scoreForSpawnIncrease[i] != None):
            if ((score % scoreForSpawnIncrease[i] == 0) and (score > firstSpawnScore[i]) and (lastIncreaseScore[i] == None)):
                tempSpawnNumList[i] += spawnIncreaseAmount[i]
            elif ((score % scoreForSpawnIncrease[i] == 0) and (score > firstSpawnScore[i]) and (score <= lastIncreaseScore[i])):
                tempSpawnNumList[i] += spawnIncreaseAmount[i]
    
        #...the actual spawn finally happens
        if ((score % scoreInterval[i] == 0) and (score >= firstSpawnScore[i]) and (lastSpawnScore[i] == None)):
            doSpawn(spawnType[i],tempSpawnNumList[i])
        elif ((score % scoreInterval[i] == 0) and (score >= firstSpawnScore[i]) and (score <= lastSpawnScore[i])):
            doSpawn(spawnType[i],tempSpawnNumList[i])

        #another note, both the spawn and increase are locked behind "final scores"
            # if the final scores are set, the last of each may happen up to and at that score
    
    return tempSpawnNumList

#---BIG LOOPS---#
def GAMELOOP(levelSet):
    global score
    global reloadTime
    global reloadStart
    global gameFont
    global gunsInUse
    global mousePos
    global spawnCounts
    global currentLevel
    global levelUnlocked
    global bossMode
    global bossModeStart
    global bossSpawned
    global activeEnemies
    global money
    global roundNum
    global roundNumStart
    global roundReloadTime
    global roundReloadStart
    global gunsSelected
    global levelReadytoEnd
    global keysPressed
    
    #placing sprites
    p1.rect.center = (displayWidth/2,displayHeight/2)
    activePlayers.add(p1)

    inventorySlots.append(hudS.create(activeSprites,activeHUDThings,'primarySlot','primarySlotSprite.png',(displayWidth - 175),40,255))
    inventorySlots.append(hudS.create(activeSprites,activeHUDThings,'secondarySlot','secondarySlotSprite.png',(displayWidth - 125),40,255))
    inventorySlots.append(hudS.create(activeSprites,activeHUDThings,'reserveSlot1','reserveSlotSprite.png',(displayWidth - 75),35,255))
    inventorySlots.append(hudS.create(activeSprites,activeHUDThings,'reserveSlot2','reserveSlotSprite.png',(displayWidth - 35),35,255))

    gunsInSlots.append(hudS.create(activeSprites,activeHUDThings,'gunInSlot1','dualPistolsSprite.png',inventorySlots[0].rect.center[0],inventorySlots[0].rect.center[1],255))
    gunsInSlots.append(hudS.create(activeSprites,activeHUDThings,'gunInSlot2','dualPistolsSprite.png',inventorySlots[1].rect.center[0],inventorySlots[1].rect.center[1],0))
    gunsInSlots.append(hudS.create(activeSprites,activeHUDThings,'gunInSlot3','dualPistolsSprite.png',inventorySlots[2].rect.center[0],inventorySlots[2].rect.center[1],0))
    gunsInSlots.append(hudS.create(activeSprites,activeHUDThings,'gunInSlot4','dualPistolsSprite.png',inventorySlots[3].rect.center[0],inventorySlots[3].rect.center[1],0))

    modsBeingUsed.append(hudS.create(activeSprites,activeHUDThings,'modBeingUsed1','gunModPickupSprite.png',(inventorySlots[0].rect.center[0] - 40),(inventorySlots[0].rect.center[1] - 20),255))
    modsBeingUsed.append(hudS.create(activeSprites,activeHUDThings,'modBeingUsed1','gunModPickupSprite.png',(inventorySlots[0].rect.center[0] - 40),(inventorySlots[0].rect.center[1] + 5),255))
    modsBeingUsed.append(hudS.create(activeSprites,activeHUDThings,'modBeingUsed1','gunModPickupSprite.png',(inventorySlots[0].rect.center[0] - 40),(inventorySlots[0].rect.center[1] + 30),255))

    healthBarStuff.append(hudS.create(activeSprites,activeHUDThings,'healthBarBlood','healthBarBloodSprite.png',(displayWidth/2),(displayHeight - 60),255,1.5))
    healthBarStuff.append(hudS.create(activeSprites,activeHUDThings,'healthBarFrame','healthBarFrameSprite.png',(displayWidth/2),(displayHeight - 60),255,1.5))

    #immediately sets the skins for modsBeingUsed, and only once, since it can't be changed mid-game
    for mod in range(len(modsBeingUsed)):
        modsBeingUsed[mod].updateDisplay([modsSelected[mod][1] == -1,modsSelected[mod][1] == -2,modsSelected[mod][1] == -3,modsSelected[mod][1] == -4,modsSelected[mod][1] == -5,modsSelected[mod][1] == -6],
                                                    ['damageModSprite.png','pierceModSprite.png','speedModSprite.png','explosiveRoundsModSprite.png','bulletEchoModSprite.png','smokeTrailModSprite.png'],
                                                    [255,255,255,255,255,255])
    
    #sets enemy spawn counts
    gP.spawnCount = 1
    e1.swarmerSpawnCount = 0
    e1.giantSpawnCount = 0
    e1.bruiserSpawnCount = 0
    e1.gunslingerSpawnCount = 0
    e1.chargerSpawnCount = 0
    e1.giantGunslingerSpawnCount = 0
    e1.kamikazeSpawnCount = 0

    #gives you your first gun with a properly-defined reload time
        #(and other things as necessary)
    if (gunsSelected[0] == 0):
        tempReloadVar = [5]
    elif (gunsSelected[0] == 100):
        tempReloadVar = [43,6,6,3,3]
    elif (gunsSelected[0] == 1000):
        tempReloadVar = [2]

    addGun(gunsSelected[0],*tempReloadVar)

    #doing timer stuff
    pygame.time.set_timer(scoreIncrease,1000)

    #music
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.load('bGMusic.mp3')
    pygame.mixer.music.play(-1)

    #sets stuff to be correct to the level being played by changing currentLevel
        #right now it sets the timer goal and the background sprite
    currentLevel = levelSet

    if (currentLevel == 1):
        bossModeStart = 300
        bG.image = pygame.image.load('level1BGSprite.png')
    elif (currentLevel == 2):
        bossModeStart = 500
        bG.image = pygame.image.load('level2BGSprite.png')
    elif (currentLevel == 3):
        bossModeStart = 600
        bG.image = pygame.image.load('level3BGSprite.png')
    elif (currentLevel == 4):
        bossModeStart = 400
        bG.image = pygame.image.load('level4BGSprite.png')
    elif (currentLevel == 5):
        bossModeStart = 100
        bG.image = pygame.image.load('level5BGSprite.png')
        miscHUDStuff.append(hudS.create(activeSprites,activeHUDThings,'theTomb','sleepyTombSprite.png',(displayWidth/2),(displayHeight/3),255,1,'theTomb'))

    elif (currentLevel == 6):
        bossModeStart = -1
        
    #runs stuff
    while (gameReset == False):

        #getting keys for press-and-hold controls
        keysPressed = pygame.key.get_pressed()
        mouseClicked = pygame.mouse.get_pressed()

        #some KEYDOWN or MOUSEBUTTONDOWN event resets
        doingGunBreak = False

        #gun cooldown rate
        for i in range(len(reloadTime)):
            if (reloadTime[i] > 0):
                reloadTime[i] -= 1
            
            #basically, for guns not of your first slot, they'll have the reloadTime temporarily negative
                #essentially desynchronizes your duplicate guns, possible with a check in the "if space is held" section below
            if (reloadTime[i] == 0) and (i != 0) and (mouseClicked[0] == False):
                reloadTime[i] = -i
        
        #reduces round reload time of each gun applicable
        for i in range(len(roundReloadTime)):
            
            if (roundReloadStart[i] != 0):
                if (roundReloadTime[i] > 0):
                    roundReloadTime[i] -= 1
        
        #all event stuff
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame()

            #certain controls work better if holding them down is not the case
                #some use temp vars for organizational purposes that are reset later
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    PAUSELOOP()

            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 3):
                    doingGunBreak = True
            
            #ALL SCORE STUFF
                #score only goes up before the boss tries to spawn
            if (bossMode == False):
                if (event.type == scoreIncrease):
                    
                    #actual score increase itself
                    score += 1
                    
                    #in each of these, the spawns are done and then the spawn counts of each are updated
                    if (currentLevel == 1):
                        spawnCounts = handleSpawns([gP.spawnCount,gP.spawnCount,e1.swarmerSpawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.gunslingerSpawnCount],
                                                [-1,-2,0,1,2,3],
                                                [20,15,2,8,30,15],
                                                [20,15,1,24,60,105],
                                                [0,0,2,1,1,2],
                                                [None,None,75,48,75,60],
                                                [None,None,1,1,1,1],
                                                [None,None,150,192,150,180],
                                                [280,285,298,296,270,285])

                        gP.spawnCount,gP.spawnCount,e1.swarmerSpawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.gunslingerSpawnCount = spawnCounts
                     
                    elif (currentLevel == 2):
                        spawnCounts = handleSpawns([gP.spawnCount,gP.spawnCount,e1.swarmerSpawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.chargerSpawnCount,e1.giantGunslingerSpawnCount],
                                                   [-1,-2,0,1,2,4,5],
                                                   [25,20,5,4,25,12,25],
                                                   [25,20,5,4,50,180,325],
                                                   [0,0,3,2,2,2,1],
                                                   [None,None,50,75,150,40,50],
                                                   [None,None,1,1,1,1,1],
                                                   [None,None,50,350,300,320,375],
                                                   [475,480,240,None,475,None,475])
                        
                        gP.spawnCount,gP.spawnCount,e1.swarmerSpawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.chargerSpawnCount,e1.giantGunslingerSpawnCount = spawnCounts
                    
                    elif (currentLevel == 3):
                        spawnCounts = handleSpawns([gP.spawnCount,gP.spawnCount,e1.bruiserSpawnCount,e1.giantGunslingerSpawnCount,e1.swarmerSpawnCount,e1.gunslingerSpawnCount,e1.chargerSpawnCount,e1.giantSpawnCount,e1.kamikazeSpawnCount],
                                                   [-1,-2,1,5,0,3,4,2,6],
                                                   [30,20,5,25,2,15,20,5,12],
                                                   [30,20,5,50,200,225,260,400,432],
                                                   [0,0,3,1,6,2,1,2,1],
                                                   [None,None,25,75,30,50,50,50,75],
                                                   [None,None,1,1,2,1,1,1,1],
                                                   [None,None,175,150,300,350,300,550,525],
                                                   [870,870,190,175,390,375,590,600,])
                        
                        gP.spawnCount,gP.spawnCount,e1.bruiserSpawnCount,e1.giantGunslingerSpawnCount,e1.swarmerSpawnCount,e1.gunslingerSpawnCount,e1.chargerSpawnCount,e1.giantSpawnCount,e1.kamikazeSpawnCount = spawnCounts

                    elif (currentLevel == 4):
                        spawnCounts = handleSpawns([gP.spawnCount,gP.spawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.kamikazeSpawnCount,e1.summonerSpawnCount],
                                                                           [-1,-2,1,2,6,7],
                                                                           [25,12,4,15,8,25],
                                                                           [25,12,4,60,8,125],
                                                                           [0,0,3,3,1,2],
                                                                           [None,None,40,75,40,75],
                                                                           [None,None,2,1,1,1],
                                                                           [None,None,120,225,200,300],
                                                                           [375,396,140,390,392,375])

                        gP.spawnCount,gP.spawnCount,e1.bruiserSpawnCount,e1.giantSpawnCount,e1.kamikazeSpawnCount,e1.summonerSpawnCount = spawnCounts

                    elif (currentLevel == 5):
                        spawnCounts = handleSpawns([gP.spawnCount,gP.spawnCount,e1.gunslingerSpawnCount,e1.chargerSpawnCount,e1.summonerSpawnCount],
                                                                                                   [-1,-2,100,101,7],
                                                                                                   [10,10,8,15,12],
                                                                                                   [10,10,24,15,12],
                                                                                                   [0,1,2,1,1],
                                                                                                   [None,None,None,None,None],
                                                                                                   [None,None,None,None,None],
                                                                                                   [None,None,None,None,None],
                                                                                                   [90,90,96,90,96])

                        gP.spawnCount,gP.spawnCount,e1.gunslingerSpawnCount,e1.chargerSpawnCount,e1.summonerSpawnCount = spawnCounts

                        #special spawns for level 5
                        if (score == 1):
                            vFX.create(activeVFX,activeSprites,"boss3SpawnFrame1.png",(displayWidth/2,displayHeight/7),0,1,255,0,0,0,0,120,doSpawn,[102,1,(displayWidth/2,displayHeight/7)],
                                                                                                                                                    ["boss3SpawnFrame2.png","boss3SpawnFrame3.png","boss3SpawnFrame4.png","boss3SpawnFrame5.png","boss3SpawnFrame6.png"],
                                                                                                                                                    [90,60,30,20,10])                      
                        if (score == 50):
                            doSpawn(103,1,(displayWidth/2,displayHeight/3))
                    
                    #gets the stage ready for a boss spawn at the necessary score
                    if (score == bossModeStart):
                        bossMode = True
        
        #firing gun, but continuous fire works
        if (mouseClicked[0]):

            #goes through each gun you have and does stuff for it
            for gun in range(len(gunsInUse)):
            
                #different types of guns
                    #works either by a gun done with reloading OR when a gun's next round to fire is ready
                if ((reloadTime[gun] == 0) or ((roundReloadTime[gun] == 0) and (roundReloadStart[gun] != 0) and (roundNum[gun] != 0))) and (gun < 2):

                    #saves the values of the fire func so modifying them is easy and not written an ungodly amount of times (aka more than once)
                        #saves this in order: horizOffset,forthOffset,bulletNum,spread,pierce,speed,speedVariance,damage,lifetime,properties,image,dontkillgroup,doHomeSet,homeParameters
                        
                        #(also a second info spot for things that shoot multiple stuff)
                    addlBulletInfo = []

                    #tier 1 guns
                    if (gunsInUse[gun] == 0): #dualpistols (400 range)
                        bulletInfo = [random.choice([-10,10]),0,1,0,1,10,0,20,40,["dust"],'mediumBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 1): #shotgun (120-160 range)
                        bulletInfo = [0,0,6,15,1,7,1,30,20,["dust"],'pelletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 2): #rifle (560 range)
                        bulletInfo = [0,0,1,0,5,14,0,45,40,["dust"],'rifleBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 3): #sword (42(+20) range)
                        bulletInfo = [0,20,1,0,3,6,0,75,7,[],'swordSlashSprite.png',None,None,None]
                    
                        #tier 2 guns
                    elif (gunsInUse[gun] == 100): #sixer (400 range)
                        bulletInfo = [0,0,1,0,1,10,0,40,40,["dust"],'mediumBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 101): #flamethrower (84-225 range)
                        bulletInfo = [0,0,1,12,2,8,1,22,[12,25],["dust"],'thrownFireSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 102): #sniper rifle (560 range)
                        bulletInfo = [0,0,1,0,7,14,0,150,40,["dust"],'rifleBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 103): #flaming sword (42(+20) slash range, 120-150(+5) fire range)
                        bulletInfo = [0,20,1,0,4,6,0,150,7,[],'flameSwordSlashSprite.png',None,None,None]
                        addlBulletInfo = [0,5,3,20,2,5,0,25,[24,30],["dust"],'thrownFireSprite.png',None,None,None]

                        #tier 3 guns
                    elif (gunsInUse[gun] == 1000): #uzi (400(+10) range)
                        bulletInfo = [0,10,1,12,1,10,0,30,40,[],'mediumBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 1001): #rocketlauncher (240 rocket range)
                        bulletInfo = [0,0,1,0,1,12,0,240,20,['explosion'],'rocketSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 1002): #railgun (infinite range; speed up benefits ricochet accuracy instead)
                        bulletInfo = [0,0,1,0,9,20,0,250,None,['ricochet'],'ionBulletSprite.png',None,None,None]
                    elif (gunsInUse[gun] == 1003): #dual swords (30(+10) side slash range, 112(+20) cross slash range)
                        bulletInfo = [[0,20,-20],[20,10,10],1,0,[4,2,2],[8,3,3],0,[300,200,200],[14,10,10],[[],[],[]],['crossSlashSprite.png','rightSlashSprite.png','leftSlashSprite.png'],None,None,None]

                    #if a gun has rounds with bullets of different stats, they can be iterated via lists
                        #each stat is a list and is selected through
                        #only activates if the image index is a list
                    if (roundReloadStart[gun] != 0) and (isinstance(bulletInfo[10],list)):
                        for bulletThing in range(len(bulletInfo)):

                            #the item only iterates if it's a list
                                #ITERATES BACKWARDS CAUSE CODING IS HARD DONT HURT ME ;-;
                            if isinstance(bulletInfo[bulletThing],list):                                
                                bulletInfo[bulletThing] = bulletInfo[bulletThing][roundNum[gun] - 1]
                        
                    #luck based mod effects happen here in this order: pierce, explosive rounds, echo
                        #pierce uses only one temp var, which is both the rng and the mult for pierce
                    pierceChance = rollBulletChance(20,modQuantities[1],True)

                    #rolls chance then adds property of little explosion if successful
                    explosionChance = rollBulletChance(8,modQuantities[3])
                    
                    if (explosionChance == True):
                        bulletInfo[9].append("littleExplosion")
                        if addlBulletInfo != []:
                            addlBulletInfo[9].append("littleExplosion")

                    #same as pierce with one temp var, but is just a boolean now basically
                    echoChance = rollBulletChance(25,modQuantities[4],True)
                    
                    if (modQuantities[5] > 0) and (gun == 0):
                        bulletInfo[9].append("smokeTrail")
                        if (addlBulletInfo != []):
                            addlBulletInfo[9].append("smokeTrail")

                    #actually fires using the saved values, with necessary modifications
                        #also the optional second one
                    if (gun == 0):
                        pBSource.fire(p1,mousePos,activeEnemies,bulletInfo[0],bulletInfo[1],activePBullets,activeSprites,rotate,bulletInfo[2],bulletInfo[3],(bulletInfo[4]*pierceChance),(bulletInfo[5] + (2*modQuantities[2])),bulletInfo[6],(bulletInfo[7] + round(bulletInfo[7]*0.30*modQuantities[0])),bulletInfo[8],bulletInfo[9],bulletInfo[10],bulletInfo[11],bulletInfo[12])
                        if (addlBulletInfo != []):
                            pBSource.fire(p1,mousePos,activeEnemies,addlBulletInfo[0],addlBulletInfo[1],activePBullets,activeSprites,rotate,addlBulletInfo[2],addlBulletInfo[3],(addlBulletInfo[4]*pierceChance),(addlBulletInfo[5] + (2*modQuantities[2])),addlBulletInfo[6],(addlBulletInfo[7] + round(addlBulletInfo[7]*0.25*modQuantities[0])),addlBulletInfo[8],addlBulletInfo[9],addlBulletInfo[10],addlBulletInfo[11],addlBulletInfo[12])
                    else:
                        pBSource.fire(p1,mousePos,activeEnemies,bulletInfo[0],bulletInfo[1],activePBullets,activeSprites,rotate,bulletInfo[2],bulletInfo[3],bulletInfo[4],bulletInfo[5],bulletInfo[6],bulletInfo[7],bulletInfo[8],bulletInfo[9],bulletInfo[10],bulletInfo[11],bulletInfo[12])
                        
                        if (addlBulletInfo != []):
                            pBSource.fire(p1,mousePos,activeEnemies,addlBulletInfo[0],addlBulletInfo[1],activePBullets,activeSprites,rotate,addlBulletInfo[2],addlBulletInfo[3],addlBulletInfo[4],addlBulletInfo[5],addlBulletInfo[6],addlBulletInfo[7],addlBulletInfo[8],addlBulletInfo[9],addlBulletInfo[10],addlBulletInfo[11],addlBulletInfo[12])

                        #repeats shot but with randomized direction and centered on playerif echoed
                    if (echoChance > 1):
                        for echo in range(echoChance - 1):
                            if (gun == 0):
                                pBSource.fire(p1,mousePos,activeEnemies,0,0,activePBullets,activeSprites,rotate,bulletInfo[2],180,(bulletInfo[4]*pierceChance),(bulletInfo[5] + (2*modQuantities[2])),bulletInfo[6],(bulletInfo[7] + round(bulletInfo[7]*0.30*modQuantities[0])),bulletInfo[8],bulletInfo[9],bulletInfo[10],bulletInfo[11],bulletInfo[12])

                                if (addlBulletInfo != []):
                                    pBSource.fire(p1,mousePos,activeEnemies,0,0,activePBullets,activeSprites,rotate,addlBulletInfo[2],180,(addlBulletInfo[4]*pierceChance),(addlBulletInfo[5] + (2*modQuantities[2])),addlBulletInfo[6],(addlBulletInfo[7] + round(addlBulletInfo[7]*0.25*modQuantities[0])),addlBulletInfo[8],addlBulletInfo[9],addlBulletInfo[10],addlBulletInfo[11],addlBulletInfo[12])

                    #plays the noise. notice that above it makes the volume lower cause it's LOUD
                    pygame.mixer.Sound.play(gunFireSound)

                    #if there's round reload time, it resets it
                    if (roundReloadStart[gun] != 0):
                        roundReloadTime[gun] = roundReloadStart[gun]

                        #also resets the amount of rounds you fire when you shoot
                        if (reloadTime[gun] == 0):
                            roundNum[gun] = roundNumStart[gun]
                        
                        roundNum[gun] -= 1
                    
                    #resets normal reload time IF it fired because of that
                    if (reloadTime[gun] == 0):
                        reloadTime[gun] = reloadStart[gun]
                
                #makes the delay in the "for i in reloadTime" thing work, basically each step negative is a one-frame delay
                elif (reloadTime[gun] < 0):
                    reloadTime[gun] += 1

        if (doingGunBreak):
            breakGun(p1)

        if (keysPressed[pygame.K_f]): #DEV BUTTON
            #modQuantities[1] = 5
            modQuantities[4] = 4

        #making it so the boss spawns when bossMode is true and after every enemy has been killed
            #(also only before the boss has spawned)
        if (bossMode == True) and (len(activeEnemies) == 0) and (bossSpawned == False):
            if (currentLevel == 1):
                doSpawn(100,1)
            elif (currentLevel == 2):
                doSpawn(101,3)
            elif (currentLevel == 3):
                vFX.create(activeVFX,activeSprites,"boss3SpawnFrame1.png",(displayWidth/2,displayHeight/2),0,1,255,0,0,0,0,120,doSpawn,[102,1,(displayWidth/2,displayHeight/2)],
                                                                                                                                          ["boss3SpawnFrame2.png","boss3SpawnFrame3.png","boss3SpawnFrame4.png","boss3SpawnFrame5.png","boss3SpawnFrame6.png"],
                                                                                                                                          [90,60,30,20,10])
            elif (currentLevel == 4):
                doSpawn(103,1)

            bossSpawned = True

        #gets the level ready to end
        if (bossSpawned == True):
            if (levelReadytoEnd < 150):
                levelReadytoEnd += 1
            elif (levelReadytoEnd >= 150) and (len(activeEnemies) == 0):
                levelUnlocked = WINLOOP(currentLevel,levelUnlocked)

        if (p1.health < 1):
            LOSELOOP()
        
        #getting mouse coords
        mousePos = pygame.mouse.get_pos()

        #updates and drawing
        drawActiveSprites()

        updateActiveSprites()

        updateScreen(30)

def PAUSELOOP():
    global pause

    #pause variable to keep menu open
    pause = True

    #music quiets down
    pygame.mixer.music.set_volume(0.3)
    
    while pause == True:
        
        #only quit and unpause events matter here
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame()
            
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    unpause()
        
        bG.draw(gameDisplay)

        displayText("Game Paused",gameFont,white,100,(displayWidth/2),(displayHeight/2))

        button(gameDisplay,(displayWidth/3),(4 * displayHeight/5),200,100,green,greener,"Continue",white,40,unpause)
        button(gameDisplay,(2 * displayWidth/3),(4 * displayHeight/5),200,100,red,redder,"Main Menu",white,40,resetGame)

        updateScreen(15)

def WINLOOP(levelBeat,levelGoal):
    global gameReset

    showLevelUnlock = False
    #unlocks next level if applicable
    if (levelGoal == levelBeat):
        levelGoal += 1

        #toggles the "new level unlocked" text to display
        showLevelUnlock = True

    #simple menu where only quit matters
    while gameReset == False:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame() 
        
        bG.draw(gameDisplay)

        displayText("You Win!",gameFont,white,100,(displayWidth/2),(displayHeight/2))

        #displays text if you've unlocked a new level
        if (showLevelUnlock == True):
            displayText("New Level Unlocked",gameFont,white,40,(displayWidth/2),(displayHeight/2 + 70))

        #buttons
        button(gameDisplay,(displayWidth/3),(4 * displayHeight/5),200,100,green,greener,"Main Menu",white,40,resetGame)
        button(gameDisplay,(2 * displayWidth/3),(4 * displayHeight/5),200,100,red,redder,"Quit",white,40,quitGame)

        updateScreen(15)
    
    #returns it so that levelUnlocked goes up
    return levelGoal

def LOSELOOP():
    
    #music quiets down
    pygame.mixer.music.set_volume(0.3)
    
    while gameReset == False:
        
        #only quit and unpause events matter here
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame()

        displayText("Game Over",gameFont,white,100,(displayWidth/2),(displayHeight/2))
        displayText("You joined the Undead Arsenal",gameFont,white,40,(displayWidth/2),(displayHeight/2 + 70))

        button(gameDisplay,(displayWidth/3),(4 * displayHeight/5),200,100,green,greener,"Main Menu",white,40,resetGame)
        button(gameDisplay,(2 * displayWidth/3),(4 * displayHeight/5),200,100,red,redder,"Quit",white,40,quitGame)

        updateScreen(15)

def SHOPLOOP():
    global gameReset
    global shopButtons
    global levelUnlocked
    global gunsSelected
    global gunsUnlocked
    global money
    
    #creates all the HUDStuff for the unlock buttons
    dualPistolsButton = hudS.create(activeSprites,activeHUDThings,'dualPistolsButton','dualPistolsSprite.png',(displayWidth/2 + 100),(displayHeight/4 - 48),0)
    shotgunButton = hudS.create(activeSprites,activeHUDThings,'shotgunButton','shotgunSprite.png',(displayWidth/2 + 180),(displayHeight/4 - 48),0)
    rifleButton = hudS.create(activeSprites,activeHUDThings,'rifleButton','rifleSprite.png',(displayWidth/2 + 260),(displayHeight/4 - 48),0)
    swordButton = hudS.create(activeSprites,activeHUDThings,'swordButton','swordSprite.png',(displayWidth/2 + 340),(displayHeight/4 - 48),0)

    sixerButton = hudS.create(activeSprites,activeHUDThings,'sixerButton','sixerSprite.png',(displayWidth/2 + 100),(displayHeight/4 + 32),0)
    flamethrowerButton = hudS.create(activeSprites,activeHUDThings,'flamethrowerButton','flamethrowerSprite.png',(displayWidth/2 + 180),(displayHeight/4 + 32),0)
    sniperRifleButton = hudS.create(activeSprites,activeHUDThings,'sniperRifleButton','sniperRifleSprite.png',(displayWidth/2 + 260),(displayHeight/4 + 32),0)
    flameSwordButton = hudS.create(activeSprites,activeHUDThings,'flameSwordButton','flameSwordSprite.png',(displayWidth/2 + 340),(displayHeight/4 + 32),0)

    uziButton = hudS.create(activeSprites,activeHUDThings,'uziButton','uziSprite.png',(displayWidth/2 + 100),(displayHeight/4 + 112),0)
    rocketLauncherButton = hudS.create(activeSprites,activeHUDThings,'rocketLauncherButton','rocketLauncherSprite.png',(displayWidth/2 + 180),(displayHeight/4 + 112),0)
    railgunButton = hudS.create(activeSprites,activeHUDThings,'railgunButton','railgunSprite.png',(displayWidth/2 + 260),(displayHeight/4 + 112),0)
    dualSwordsButton = hudS.create(activeSprites,activeHUDThings,'dualSwordsButton','dualSwordsSprite.png',(displayWidth/2 + 340),(displayHeight/4 + 112),0)

    damageModButton = hudS.create(activeSprites,activeHUDThings,'damageModButton','damageModSprite.png',(displayWidth/2 + 100),(displayHeight/2 + 102),0)
    pierceModButton = hudS.create(activeSprites,activeHUDThings,'pierceModButton','pierceModSprite.png',(displayWidth/2 + 220),(displayHeight/2 + 102),0)
    speedModButton = hudS.create(activeSprites,activeHUDThings,'speedModButton','speedModSprite.png',(displayWidth/2 + 340),(displayHeight/2 + 102),0)

    explosiveRoundsModButton = hudS.create(activeSprites,activeHUDThings,'fourthModButton','gunModPickupSprite.png',(displayWidth/2 + 100),(displayHeight/2 + 182),0)
    bulletEchoModButton = hudS.create(activeSprites,activeHUDThings,'fifthModButton','gunModPickupSprite.png',(displayWidth/2 + 220),(displayHeight/2 + 182),0)
    smokeTrailModButton = hudS.create(activeSprites,activeHUDThings,'sixthModButton','gunModPickupSprite.png',(displayWidth/2 + 340),(displayHeight/2 + 182),0)

    #HUDStuff for the "this is locked" stuff
    tier2Lock = hudS.create(activeSprites,activeHUDThings,'tier2Lock','lockSprite.png',(displayWidth/2 + 220),(displayHeight/4 + 32),0)
    tier3Lock = hudS.create(activeSprites,activeHUDThings,'tier3Lock','lockSprite.png',(displayWidth/2 + 220),(displayHeight/4 + 112),0)
    complexLock = hudS.create(activeSprites,activeHUDThings,'complexLock','lockSprite.png',(displayWidth/2 + 220),(displayHeight/2 + 182),0)

    while (gameReset == False):
        
        #only quit matters
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame()
            if (event.type == pygame.KEYDOWN):#DEV BUTTONS
                if event.key == pygame.K_b:
                    gunsUnlocked = []
                elif event.key == pygame.K_c:
                    money += 1000
                elif event.key == pygame.K_d:
                    levelUnlocked += 1
                elif event.key == pygame.K_a:
                    money = 3445 + 24755

        #drawing background
        bG.draw(gameDisplay)

        #money display at the top
        displayText(('$' + str(money)),gameFont,white,40,(displayWidth/5),(displayHeight/5 - 80))
 
        #general buttons on the side
        if (len(modsSelected) == 3) and not (None in gunsSelected):
            button(gameDisplay,(displayWidth/5),(displayHeight/5),200,100,blue,bluer,"Main Menu",white,40,resetGame)
        else:
            button(gameDisplay,(displayWidth/5),(displayHeight/5),200,100,midGray,darkGray,"Main Menu",white,40,None)


        button(gameDisplay,(displayWidth/5),(2 * displayHeight/5),200,100,magenta,magentaer,"Unselect All",white,40,shopUnselectAll)

        textBox((displayWidth/5,7*displayHeight/10),240,180,darkGray,10,white,shopDesc,30,white,5,23)

        #these are the things that are always there in the shop
            #i.e. Most text, the first tier buttons, and simple mods (w/ conditionals ofc)
        if (True):
            #all the text to group buttons together
            displayText("Guns",gameFont,white,60,(displayWidth/2 + 165),35)

            displayText("Tier 1",gameFont,white,40,(displayWidth/2),(displayHeight/4 - 50))
            displayText("Tier 2",gameFont,white,40,(displayWidth/2),(displayHeight/4 + 30))
            displayText("Tier 3",gameFont,white,40,(displayWidth/2),(displayHeight/4 + 110))

            displayText("Gun Mods",gameFont,white,60,(displayWidth/2 + 165),(displayHeight/2 + 35))

            displayText("Simple",gameFont,white,40,(displayWidth/2),(displayHeight/2 + 100))
            displayText("Complex",gameFont,white,40,(displayWidth/2),(displayHeight/2 + 180))
            
            #buttons for tier 1 guns. written so that it checks if they're selected FIRST, THEN if they're not
            shopButton((displayWidth/2 + 100),(displayHeight/4 - 48),"gun",0,0,"$0",0,dualPistolsButton,'dualPistolsSprite.png',1,'A well-rounded, quick-shooting pair of pistols.')
            shopButton((displayWidth/2 + 180),(displayHeight/4 - 48),"gun",1,1,"$0",0,shotgunButton,'shotgunSprite.png',1,'A short range shotgun.')
            shopButton((displayWidth/2 + 260),(displayHeight/4 - 48),"gun",2,2,"$0",0,rifleButton,'rifleSprite.png',1,'A high range rifle that pierces through your enemies.')
            shopButton((displayWidth/2 + 340),(displayHeight/4 - 48),"gun",3,3,"$0",0,swordButton,'swordSprite.png',1,'A very short range, high damage sword.')

            #buttons for simple gun mods
            shopButton((displayWidth/2 + 100),(displayHeight/2 + 102),"gunMod",["Damage Mod",-1],None,"$0",0,damageModButton,'damageModSprite.png',1,'+30% damage per stack.')
            shopButton((displayWidth/2 + 220),(displayHeight/2 + 102),"gunMod",["Pierce Mod",-2],None,"$0",0,pierceModButton,'pierceModSprite.png',1,'+20% chance per stack of a double-pierce bullet per shot. Overflow chance might cause more pierce...')
            shopButton((displayWidth/2 + 340),(displayHeight/2 + 102),"gunMod",["Bullet Speed Mod",-3],None,"$0",0,speedModButton,'speedModSprite.png',1,'+2 bullet speed per stack.')

        #tier 2 guns
        if (levelUnlocked >= 2):
            shopButton((displayWidth/2 + 100),(displayHeight/4 + 32),"gun",100,0,"$1000",1000,sixerButton,'sixerSprite.png',1,'Fires quick 6-shot bursts of bullets.')
            shopButton((displayWidth/2 + 180),(displayHeight/4 + 32),"gun",101,1,"$3000",3000,flamethrowerButton,'flamethrowerSprite.png',1,'Consistent damage with pierce.')
            shopButton((displayWidth/2 + 260),(displayHeight/4 + 32),"gun",102,2,"$5000",5000,sniperRifleButton,'sniperRifleSprite.png',1,'Really high pierce rifle with high damage.')
            shopButton((displayWidth/2 + 340),(displayHeight/4 + 32),"gun",103,3,"$8000",8000,flameSwordButton,'flameSwordSprite.png',1,'A higher damage sword that shoots mid-low range flames too.')
            tier2Lock.updateDisplay([True],['lockSprite.png'],[0],[0],[0])
        else:
            button(gameDisplay,(displayWidth/2 + 220),(displayHeight/4 + 32),320,50,deepRed,deepRedder,None,None,None,None)
            tier2Lock.updateDisplay([True],['lockSprite.png'],[255],[0],[2])

        #tier 3 guns
        if (levelUnlocked >= 4):
            shopButton((displayWidth/2 + 100),(displayHeight/4 + 112),"gun",1000,0,"$3000",3000,uziButton,'uziSprite.png',1,'A REALLY fast-shooting gun.')
            shopButton((displayWidth/2 + 180),(displayHeight/4 + 112),"gun",1001,1,"$5000",5000,rocketLauncherButton,'rocketLauncherSprite.png',1,'High damage, mid-low range rocket with an explosion to boot.')
            shopButton((displayWidth/2 + 260),(displayHeight/4 + 112),"gun",1002,2,"$8000",8000,railgunButton,'railgunSprite.png',1,'A REALLY high pierce rifle with bouncing bullets and INFINITE range. Ricochet range increases with bullet speed.')
            shopButton((displayWidth/2 + 340),(displayHeight/4 + 112),"gun",1003,3,"$10k",10000,dualSwordsButton,'dualSwordsSprite.png',1,'A triple combo of high-damage slices.')
            tier3Lock.updateDisplay([True],['lockSprite.png'],[0],[0],[0])
        else:
            button(gameDisplay,(displayWidth/2 + 220),(displayHeight/4 + 112),320,50,deepRed,deepRedder,None,None,None,None)
            tier3Lock.updateDisplay([True],['lockSprite.png'],[255],[0],[2])

        #complex gun mods
        if (levelUnlocked >= 3):
            shopButton((displayWidth/2 + 100),(displayHeight/2 + 182),"gunMod",["Explosive Rounds Mod",-4],None,"$2500",2500,explosiveRoundsModButton,'explosiveRoundsModSprite.png',1,'Chance of bullets that create small, 40% damage explosions on hit. +8% chance per stack.')
            shopButton((displayWidth/2 + 220),(displayHeight/2 + 182),"gunMod",["Bullet Echo Mod",-5],None,"$2500",2500,bulletEchoModButton,'bulletEchoModSprite.png',1,'+25% hance per stack of shooting an extra bullet in a random direction. Overflow chance might cause retrigger...')
            shopButton((displayWidth/2 + 340),(displayHeight/2 + 182),"gunMod",["Smoke Trail Mod",-6],None,"$2500",2500,smokeTrailModButton,'smokeTrailModSprite.png',1,'Each bullet produces a 10% damage smoke trail. Double rate of smoke production per stack.')
            complexLock.updateDisplay([True],['lockSprite.png'],[0],[0],[0])
        else:
            button(gameDisplay,(displayWidth/2 + 220),(displayHeight/2 + 182),320,50,deepRed,deepRedder,None,None,None,None)
            complexLock.updateDisplay([True],['lockSprite.png'],[255],[0],[2])

        activeHUDThings.draw(gameDisplay)

        updateScreen(15)

def MENULOOP():
    global gameReset
    global levelUnlocked
    global openTimer

    #drawing background
    bG.setPlace((displayWidth/2),(displayHeight/2))

    openTimer = 0

    while True:
        #only checks for quitting
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                quitGame()
        
        #making it so you can go to different loops
        if (gameReset == True):
            gameReset = False

        #drawing backgrounds
        bG.draw(gameDisplay)

        #title
        displayText("Undead",gameFont,white,100,(displayWidth/5),(displayHeight/5))
        displayText("Arsenal",gameFont,white,100,(displayWidth/5),((displayHeight/5) + 100))

        #all buttons for navigation (and are only unlocked when you've beaten the previous level)
        button(gameDisplay,(4 * displayWidth/5),(displayHeight/10),200,75,green,greener,"Level 1",white,40,GAMELOOP,[1])
        if (levelUnlocked > 1):
            button(gameDisplay,(4 * displayWidth/5),((displayHeight/10) + 75 + 10),200,75,green,greener,"Level 2",white,40,GAMELOOP,[2])
            
        if (levelUnlocked > 2):
            button(gameDisplay,(4 * displayWidth/5),((displayHeight/10) + 150 + 20),200,75,green,greener,"Level 3",white,40,GAMELOOP,[3])
        
        if (levelUnlocked > 3):
            button(gameDisplay,(4 * displayWidth/5),((displayHeight/10) + 225 + 30),200,75,green,greener,"Level 4",white,40,GAMELOOP,[4])
        
        if (levelUnlocked > 4):
            button(gameDisplay,(4 * displayWidth/5),((displayHeight/10) + 300 + 40),200,75,green,greener,"Level 5",white,40,GAMELOOP,[5])
        
        if (levelUnlocked > 5):
            button(gameDisplay,(4 * displayWidth/5),(9 * displayHeight/10),200,75,green,greener,"Endless",white,40,GAMELOOP,[6])

        #one second timer to prevent accidental double clicks into the abyss
        if (openTimer < 15):
            button(gameDisplay,(displayWidth/5),(4 * displayHeight/5),200,100,midGray,darkGray,"Quit",white,40,None)
            openTimer += 1
        else:
            button(gameDisplay,(displayWidth/5),(4 * displayHeight/5),200,100,red,redder,"Quit",white,40,quitGame)
        
        button(gameDisplay,(displayWidth/5),(3 * displayHeight/5),200,100,blue,bluer,"Shop",white,40,SHOPLOOP)

        updateScreen(15)

MENULOOP()