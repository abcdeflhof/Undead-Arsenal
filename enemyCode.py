import pygame
import math
import random

class enemy1(pygame.sprite.Sprite):
    enemyWidth = 15
    enemyHeight = 15
    originalImage = pygame.image.load('swarmerSprite.png')

    #spawn amounts (set at beginning of game loop)
    swarmerSpawnCount = int()
    giantSpawnCount = int()
    bruiserSpawnCount = int()
    gunslingerSpawnCount = int()
    chargerSpawnCount = int()
    giantGunslingerSpawnCount = int()
    kamikazeSpawnCount = int()
    summonerSpawnCount = int()

    #basic stats (set in respective spawn functions)
    speed = int()
    health = int()
    damage = int()

    type = int()

    moneyGive = int()

    turnToPlayer = True
    softTurnToPlayer = [0,0,0,0]

    #a timer that can be used for special actions sometimes
    specialTimer = None

    #pushPriority has to do with softCollideAmong (set in spawn functions)
        #if it's higher than another's pushPriority, then only the other gets pushed. otherwise, both get pushed
    pushPriority = int()

    angle = float()
    x = int()
    y = int()

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('swarmerSprite.png')
        self.rect = self.image.get_rect()
        self.rect.center = 0,0
    
    #creates a new enemy
    def spawn(self,activeEnemyGroup,activeSpritesGroup,uBound,dBound,lBound,rBound,enemyImage,enemySpawnCount,enemyType,enemyHealth,enemySpeed,enemyDamage,enemyIFrames,enemyMoneyGive,enemyScale,enemyPushPriority,initializationFunc,initFuncParameters,enemyGoTo=None,enemyGoToRad=0):
        for i in range(enemySpawnCount):
            #making a new one
            newEnemy = enemy1()
            activeEnemyGroup.add(newEnemy)
            activeSpritesGroup.add(newEnemy)

            #setting characteristics of enemy
            newEnemy.health = enemyHealth
            newEnemy.baseHealth = enemyHealth
            newEnemy.speed = enemySpeed
            newEnemy.damage = enemyDamage
            newEnemy.IFrames = enemyIFrames
            newEnemy.IFramesGoal = enemyIFrames
            
            newEnemy.pushPriority = enemyPushPriority
            newEnemy.scale = enemyScale
            newEnemy.type = enemyType

            #amount of money it gives on death
            newEnemy.moneyGive = enemyMoneyGive

            #image stuff and width/height stuff (width and height are switched cause they were all drawn vertically)
            newEnemy.originalImage = pygame.transform.scale_by(pygame.image.load(enemyImage),newEnemy.scale)
            newEnemy.image = newEnemy.originalImage
            newEnemy.rect = newEnemy.image.get_rect()

            newEnemy.enemyWidth = newEnemy.originalImage.get_height()
            newEnemy.enemyHeight = newEnemy.originalImage.get_width()

            #chooses to spawn at one of the four sides of the screen (offscreen)
            spawnLocation = random.randint(0,3)

            if (spawnLocation == 0):
                newEnemy.rect.center = ((random.randint(lBound,rBound)),(uBound - (newEnemy.enemyHeight/2)))
            elif (spawnLocation == 1):
                newEnemy.rect.center = ((random.randint(lBound,rBound)),(dBound + (newEnemy.enemyHeight/2)))
            elif (spawnLocation == 2):
                newEnemy.rect.center = ((lBound - (newEnemy.enemyWidth/2)),(random.randint(uBound,dBound)))
            else:
                newEnemy.rect.center = ((rBound + (newEnemy.enemyWidth/2)),(random.randint(uBound,dBound)))

            if (enemyGoTo != None):
                    newEnemy.rect.center = (random.randint(round(enemyGoTo[0]) + enemyGoToRad,round(enemyGoTo[0]) - enemyGoToRad),random.randint(round(enemyGoTo[1]) + enemyGoToRad,round(enemyGoTo[1]) - enemyGoToRad))
            
            #setting initial x and y
            newEnemy.x = newEnemy.rect.center[0]
            newEnemy.y = newEnemy.rect.center[1]

            #special initialization stuff if applicable
            if (initializationFunc != None):
                initializationFunc(newEnemy,*initFuncParameters)

        return newEnemy
    
    #initializes type 1 enemies' values for the update function
    def type1Init(self,standingRadiusSet,standingSubjectSet,strafeSpeedSet,strafeChangeTimeSet,actionSet,actionParametersSet,actionCooldownSet,actionCooldownStartSet,actionCenteringSet=False,dieOnActionSet=False,specialTimerActionSet=None,specialTimerActionParametersSet=None):
        self.standingRadius = standingRadiusSet
        self.standingSubject = standingSubjectSet

        self.strafeSpeed = strafeSpeedSet
        self.strafeDirection = random.choice([1,-1])
        self.strafeChangeTime = strafeChangeTimeSet
        self.strafeChangeStart = self.strafeChangeTime
        self.strafeChange = 0

        self.action = actionSet
        self.actionParameters = actionParametersSet
        self.actionCooldown = actionCooldownSet
        self.actionCooldown = actionCooldownSet
        self.actionCooldownStart = actionCooldownStartSet
        self.doCenterAction = actionCenteringSet
        self.doDieOnAction = dieOnActionSet

        self.specialTimerAction = specialTimerActionSet
        self.specialTimerActionParameters = specialTimerActionParametersSet
        if (specialTimerActionSet != None):
            self.specialTimer = 0
    
    #initializes type 2 enemies' values for the update function
    def type2Init(self,actionSet,actionParametersSet,actionCooldownSet,actionCooldownStartSet,actionCenteringSet,dieOnActionSet,doTurnToPlayer,doMoveSet=False):
        self.action = actionSet
        self.actionParameters = actionParametersSet
        self.actionCooldown = actionCooldownSet
        self.actionCooldownStart = actionCooldownStartSet
        self.doCenterAction = actionCenteringSet
        self.doDieOnAction = dieOnActionSet
        self.turnToPlayer = doTurnToPlayer
        self.doMoveToPlayer = doMoveSet

    def type3Init(self,actionSet,actionParametersSet,actionCooldownSet,actionCooldownStartSet,actionCenteringSet,dieOnActionSet,doTurnToPlayer,udlrBoundSet=list,margin=int):
        self.action = actionSet
        self.actionParameters = actionParametersSet
        self.actionCooldown = actionCooldownSet
        self.actionCooldownStart = actionCooldownStartSet
        self.doCenterAction = actionCenteringSet
        self.turnToPlayer = doTurnToPlayer
        self.doDieOnAction = dieOnActionSet

        self.uBound = (udlrBoundSet[0] + margin)
        self.dBound = (udlrBoundSet[1] - margin)
        self.lBound = (udlrBoundSet[2] + margin)
        self.rBound = (udlrBoundSet[3] - margin)

    #these next few are for charger-type enemies specifically
    def chargerCharge(self,tempSpeed,timeCharging,tempPushPriority,vFXFunc,activeVFXgroup,activeSpritesGroup,dustParticleCount=0):
        #saves the actual speed (to be reset in chargerStop) and then speeds up and stops turning
        self.speedSave = self.speed
        self.speed = tempSpeed
        self.turnToPlayer = False

        #same thing as speed but with push priority
        self.pushPrioritySave = self.pushPriority
        self.pushPriority = tempPushPriority

        #temporarily changes type so it can just go forward
        self.type = 0

        #creates timer to stop at
        self.specialTimer = timeCharging

        #creates dust particles for visual indicator of start
        for i in range(dustParticleCount):
            vFXFunc(activeVFXgroup,activeSpritesGroup,'evilDustParticleSprite.png',self.rect.center,random.randint((round(self.angle) + 100),(round(self.angle) + 260)),2,255,3,0,-10,-0.05,30)

    def chargerStop(self):
        #just resets values related to charging basically
        self.x,self.y = self.rect.center
        self.speed = self.speedSave
        self.pushPriority = self.pushPrioritySave
        self.type = 1
        self.turnToPlayer = True
        self.softTurnToPlayer = [1,10,2,45]
        self.rect.center = (self.x,self.y)

    #temporarily adds an action to the enemy. can only be used if the actions of the enemy are a list
    def toggleMode(self,toggledAction,toggledActionPars,actionFrequency,timeStayToggled,doCenterSet,doDieSet=False):
        self.action.append(toggledAction)
        self.actionParameters.append(toggledActionPars)
        self.actionCooldown.append(actionFrequency)
        self.actionCooldownStart.append(actionFrequency)
        self.doCenterAction.append(doCenterSet)
        self.doDieOnAction.append(doDieSet)

        self.actionLength = len(self.action)

        self.specialTimer = timeStayToggled
        self.specialTimerAction = enemy1.untoggleMode
        self.specialTimerActionParameters = [self.actionLength]

    #removes the added action from toggleMode
    def untoggleMode(self,indexToRemove):
        actualRemoval = indexToRemove - 1
        if (len(self.action) == indexToRemove):
            del self.action[actualRemoval]
            del self.actionParameters[actualRemoval]
            del self.actionCooldown[actualRemoval]
            del self.actionCooldownStart[actualRemoval]
            del self.doCenterAction[actualRemoval]
            del self.doDieOnAction[actualRemoval]

        #if the indexToRemove isn't the last one, it shifts which one to delete 
            #hopefully works? probably won't ever be checked but I wanted to make it anyway
        else:
            del self.action[actualRemoval - (indexToRemove - len(self.action))]
            del self.actionParameters[actualRemoval - (indexToRemove - len(self.action))]
            del self.actionCooldown[actualRemoval - (indexToRemove - len(self.action))]
            del self.actionCooldownStart[actualRemoval - (indexToRemove - len(self.action))]
            del self.doCenterAction[actualRemoval - (indexToRemove - len(self.action))]
            del self.doDieOnAction[actualRemoval - (indexToRemove - len(self.action))]

    #just sets soft rotate values
    def setSoftRotate(self,speedScale,maxSpeed,allowedError,time):
        self.softTurnToPlayer = [speedScale,maxSpeed,allowedError,time]
    
    #easy, centralized function for actions to work for any type
    def doActionStuff(self):
        #works with lists of actions
        if (isinstance(self.action,list)):
            for i in range(len(self.action)):
                self.actionCooldown[i] -= 1

                if not (self.actionCooldown[i] > 0): 
                    
                    #does the stuff
                    if (self.doCenterAction[i] == True):
                        self.action[i](self.rect.center,*self.actionParameters[i])
                    elif (self.doCenterAction[i] == False):
                        self.action[i](self,*self.actionParameters[i])
                    else: #can be made to not use self parameter by putting anything else in the parameter (like a str)
                        self.action[i](*self.actionParameters[i])

                    if (self.doDieOnAction[i]):
                        self.kill()

                    #resets cooldown for action
                    self.actionCooldown[i] = self.actionCooldownStart[i]
        
        #also works if there's only one aciton
        else:
            self.actionCooldown -= 1

            if not (self.actionCooldown > 0): 
                
                #does the stuff
                if (self.doCenterAction == True):
                    self.action(self.rect.center,*self.actionParameters)
                elif (self.doCenterAction == False):
                    self.action(self,*self.actionParameters)
                else: #can be made to not use self parameter by putting anything else in the parameter (like a str)
                    self.action(*self.actionParameters)
                
                if (self.doDieOnAction):
                    self.kill()

                #resets cooldown for action
                self.actionCooldown = self.actionCooldownStart

    #movement and some collisions
    def update(self):
        #basic, walk straight at you type
        if (self.type == 0):
            self.rect.move_ip((-math.cos(self.angle  * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
            self.x += (-math.cos(self.angle * -math.pi/180) * self.speed)
            self.y += (-math.sin(self.angle * -math.pi/180) * self.speed)

        #enemy stands at a certain radius and does an action at that radius
        if (self.type == 1):

            #moves until the radius is reached, then does special stuff
            if ((math.dist(self.rect.center,self.standingSubject.rect.center)) > self.standingRadius):
                self.rect.move_ip((-math.cos(self.angle * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
                self.x += (-math.cos(self.angle * -math.pi/180) * self.speed)
                self.y += (-math.sin(self.angle * -math.pi/180) * self.speed)
            else:
                #strafes if it has strafe speed
                if (self.strafeSpeed != 0):

                    #gets one tick closer to changing strafe direction
                    self.strafeChangeTime -= 1
                    
                    #has a chance of changing strafing direction or standing still at end of cooldown
                    if not (self.strafeChangeTime > 0):

                        #0 = continue with current direction, 1 = change direction, 2 = stop
                        self.strafeChange = random.randint(0,2)

                        if (self.strafeChange == 1):
                            self.strafeDirection = -self.strafeDirection
                        
                        #resets cooldown
                        self.strafeChangeTime = self.strafeChangeStart
                    
                    #actually strafes (the number 76.8 is some mathematical bs magic that i dont know. but it works.)
                    if (self.strafeChange != 2):
                        self.rect.move_ip((-math.cos((self.angle * -math.pi/180) + (76.8 * self.strafeDirection)) * self.strafeSpeed),(-math.sin((self.angle * -math.pi/180) + (76.8 * self.strafeDirection)) * self.strafeSpeed))
                        self.x += (-math.cos((self.angle * -math.pi/180) + (76.8 * self.strafeDirection)) * self.strafeSpeed)
                        self.y += (-math.sin((self.angle * -math.pi/180) + (76.8 * self.strafeDirection)) * self.strafeSpeed)
                
                #actually does the action(s)
                self.doActionStuff()

        #enemy stays still and does stuff occasionally
        if (self.type == 2):
            self.doActionStuff()

            if (self.doMoveToPlayer == True):
                self.rect.move_ip((-math.cos(self.angle  * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
                self.x += (-math.cos(self.angle * -math.pi/180) * self.speed)
                self.y += (-math.sin(self.angle * -math.pi/180) * self.speed)

        #enemy does action occasionally when in a certain area
        if (self.type == 3):
            if (self.uBound < self.rect.center[1] < self.dBound) and (self.lBound < self.rect.center[0] < self.rBound):
                self.doActionStuff()
            else:
                self.rect.move_ip((-math.cos(self.angle  * -math.pi/180) * self.speed),(-math.sin(self.angle * -math.pi/180) * self.speed))
                self.x += (-math.cos(self.angle * -math.pi/180) * self.speed)
                self.y += (-math.sin(self.angle * -math.pi/180) * self.speed)

        #counts down on a special timer if applicable, then does special thing at the end
        if (self.specialTimer != None):
            self.specialTimer -= 1

            if (self.specialTimer == 0):

                if (self.specialTimerActionParameters == None):
                    self.specialTimerAction(self)
                else:
                    self.specialTimerAction(self,*self.specialTimerActionParameters)

        #the player's i-frames to each zombie counts down
        if (self.IFrames > 0):
            self.IFrames -= 1

    #enemies push each other away
    def softCollideAmong(self,othersGroup):
        if pygame.sprite.spritecollide(self,othersGroup,0):
            #gets the sprites enemy collided with
            colList = pygame.sprite.spritecollide(self,othersGroup,0)
            
            #pushes away for each of those sprites
            for i in colList:
                colPoint = self.rect.clip(i)

                if (i != self) and not (self.pushPriority > i.pushPriority):
                    #like a second version of rotating, just only making the vector
                    if (colPoint[0] == self.x):
                        if (colPoint[1] < self.y):
                            self.softColVector = 270
                        elif (colPoint[1] > self.y):
                            self.softColVector = 90
                        else:
                            self.softColVector = 0

                    elif colPoint[0] > self.x:
                        self.softColVector = (math.atan((colPoint[1]-self.y)/(colPoint[0]-self.x))*(-180/math.pi) + 180)
                    else:
                        self.softColVector = (math.atan((colPoint[1]-self.y)/(colPoint[0]-self.x))*(-180/math.pi))
                    
                    #movement from collision
                    self.rect.move_ip((math.cos(self.softColVector*-math.pi/180)*self.speed),(math.sin(self.softColVector*-math.pi/180) * self.speed))
                    self.x += (math.cos(self.softColVector*-math.pi/180) * self.speed)
                    self.y += (math.sin(self.softColVector*-math.pi/180) * self.speed)

    def draw(self,surface):
        surface.blit(self.image)