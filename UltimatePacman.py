# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AttackAgent', second = 'DefendAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]
  
  
##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
      self.start = gameState.getAgentPosition(self.index)
      self.initialFoodCount = len(self.getFood(gameState).asList())
      self.lastAction = Directions.STOP
      self.stuckCount = 0
      self.stuckWall = []
      self.moveAway = 0
      self.coordinate = (0,0)
      CaptureAgent.registerInitialState(self, gameState)

      # get the border for my own territory
      if self.red:
          xCoordinate = (gameState.data.layout.width - 2) / 2
          enemyXCoordinate1 = (((gameState.data.layout.width - 2) / 2) + 1)
          enemyXCoordinate2 = (((gameState.data.layout.width - 2) / 2) + 1) + 1
      else:
          xCoordinate = ((gameState.data.layout.width - 2) / 2) + 1
          enemyXCoordinate1 = ((gameState.data.layout.width - 2) / 2)
          enemyXCoordinate2 = ((gameState.data.layout.width - 2) / 2) - 1
      #yCoordinate = (gameState.data.layout.height / 2)
      # self.center = (xCoordinate, yCoordinate)
      self.border = [(xCoordinate, yCoordinate) for yCoordinate in range(1, gameState.data.layout.height - 1) if
                     not gameState.hasWall(xCoordinate, yCoordinate)]
      self.enemyBorder1 = [(enemyXCoordinate1, enemyYCoordinate) for enemyYCoordinate in range(1, gameState.data.layout.height - 1) if
                      not gameState.hasWall(enemyXCoordinate1, enemyYCoordinate)]
      self.enemyBorder2 = [(enemyXCoordinate2, enemyYCoordinate) for enemyYCoordinate in
                           range(1, gameState.data.layout.height - 1) if
                           not gameState.hasWall(enemyXCoordinate2, enemyYCoordinate)]
      self.border2 = [(xCoordinate, yCoordinate) for yCoordinate in range(1, gameState.data.layout.height - 1) if
                     not gameState.hasWall(xCoordinate, yCoordinate)]


  def chooseAction(self, gameState):
      actions = gameState.getLegalActions(self.index)
      #actions.remove(Directions.STOP)
      featureValues = []
      for a in actions:
          #successor = self.getSuccessor(gameState, a)
          value = self.evaluate(gameState, a)
          featureValues.append(value)

      bestActions = [a for a, v in zip(actions, featureValues) if v == max(featureValues)]
      # carry = gameState.getAgentState(self.index).numCarrying
      # if carry >= 5:
      #     bestDist = 9999
      #     for action in actions:
      #         successor = self.getSuccessor(gameState, action)
      #         pos2 = successor.getAgentPosition(self.index)
      #         dist = self.getMazeDistance(self.start, pos2)
      #         if dist < bestDist:
      #             bestAction = action
      #             bestDist = dist
      #     return bestAction

      chosenAction = random.choice(bestActions)
      return chosenAction

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights


class AttackAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food.
    """

    def getFeatures(self, gameState, action):

        features = util.Counter()
        #get successor
        successor = self.getSuccessor(gameState, action)

        #get current and successor position
        currentPos = gameState.getAgentPosition(self.index)
        successorPos = successor.getAgentPosition(self.index)

        #get a list of enemy food
        foodList = self.getFood(gameState).asList()

        if len(self.border2) == 5:
            self.border2 = list(self.border)
        #get distance to closest food
        if len(foodList) > 2:
            closestCurrentFoodDistance = min([self.getMazeDistance(currentPos,food) for food in foodList])
            closestSuccessorFoodDistance = min([self.getMazeDistance(successorPos,food) for food in foodList])
            features['distanceToFood'] = closestCurrentFoodDistance - closestSuccessorFoodDistance
            if self.stuckCount >= 4:
                randomCurrentFoodDistance = min([self.getMazeDistance(currentPos, food) for food in foodList])
                randomFoodPosition = min([food for food in foodList if self.getMazeDistance(currentPos,food) == closestCurrentFoodDistance])
                # randomSuccessorFoodDistance = self.getMazeDistance(successorPos, randomFoodPosition)
                # features['distanceToFood'] = randomCurrentFoodDistance
                #features['distanceToFood'] = - features['distanceToFood']
                #self.debugDraw([randomFoodPosition], [1, 0, 0], True)
                # get distance to border
                currentDistanceToBorder = max(self.getMazeDistance(currentPos, coordinate) for coordinate in self.border2)
                eCoordinate = max([coordinate for coordinate in self.border2 if self.getMazeDistance(currentPos,coordinate) == currentDistanceToBorder])
                # successorDistanceToBorder = max(
                #     self.getMazeDistance(successorPos, coordinate) for coordinate in self.border2)
                self.border2.remove(eCoordinate)
                self.stuckCount = 0
                self.moveAway = 1
                # currentDistanceToBorder = min(
                #     self.getMazeDistance(currentPos, coordinate) for coordinate in self.border2)
                # currentDistanceToBorder = self.getMazeDistance(currentPos, eCoordinate)
                # successorDistanceToBorder = self.getMazeDistance(successorPos, eCoordinate)
                # eCoordinate = min([coordinate for coordinate in self.border2 if self.getMazeDistance(currentPos,coordinate) == currentDistanceToBorder])
                # self.debugDraw([eCoordinate], [1, 0, 0], True)
                # features['distanceToBorder'] = (currentDistanceToBorder - successorDistanceToBorder)
                # features['distanceToFood'] = 0
                # features['distanceToCapsule'] = 0
                # features['distanceToGhost'] = 0
                currentDistanceToBorder = max(self.getMazeDistance(currentPos, coordinate) for coordinate in self.border2)
                eCoordinate = max([coordinate for coordinate in self.border2 if
                                   self.getMazeDistance(currentPos, coordinate) == currentDistanceToBorder])
                currentDistanceToBorder = self.getMazeDistance(currentPos, eCoordinate)
                successorDistanceToBorder = self.getMazeDistance(successorPos, eCoordinate)
                self.coordinate = eCoordinate
                self.debugDraw([eCoordinate], [1, 1, 0], True)
                features['distanceToBorder'] = (currentDistanceToBorder - successorDistanceToBorder)
                features['distanceToFood'] = 0

            if self.moveAway == 1 and currentPos != self.coordinate:
                self.debugDraw(self.coordinate, [1, 0, 0], True)
                currentDistanceToBorder = self.getMazeDistance(currentPos, self.coordinate)
                successorDistanceToBorder = self.getMazeDistance(successorPos, self.coordinate)
                features['distanceToBorder'] = (currentDistanceToBorder - successorDistanceToBorder)
                features['distanceToFood'] = 0
                self.stuckCount= 0
                return features
                # features['distanceToCapsule'] = 0
                # features['distanceToGhost'] = -100
                # return features
            else:
                self.moveAway = 0
                self.coordinate = 0

        #get information about distance to enemy ghost and distance to border during attack
        # features['distanceToGhost'] = 0
        # features['distanceToBorder'] = 0

        #if attacker carry half the enemy food pellets or all enemy food pellets except two, come back to territory to deposit food
        #while avoid being attacked by enemy ghost
        carry = gameState.getAgentState(self.index).numCarrying
        if carry >= (self.initialFoodCount/3) or len(foodList) <= 2:
            currentDistanceToBorder = min(self.getMazeDistance(currentPos, coordinate) for coordinate in self.border)
            successorDistanceToBorder = min(self.getMazeDistance(successorPos, coordinate) for coordinate in self.border)
            features['distanceToBorder'] = ((currentDistanceToBorder - successorDistanceToBorder) * carry)
            features['distanceToFood'] = 0
            features['distanceToCapsule'] = 0

        #get enemy ghost that nears our attacker
        enemies = [gameState.getAgentState(index) for index in self.getOpponents(successor)]
        # capsuleList = self.getCapsules(gameState)
        # if len(capsuleList) == 1 and enemies[0].scaredTimer > 0:
        #     closestDistanceToCapsule = min([self.getMazeDistance(currentPos, capsule) for capsule in capsuleList])
        #     successorClosestDistanceToCapsule = min(
        #         [self.getMazeDistance(successorPos, capsule) for capsule in capsuleList])
        #     features['distanceToCapsule'] = -0.1 * (closestDistanceToCapsule - successorClosestDistanceToCapsule)

        enemyGhost = [a for a in enemies if not a.isPacman and a.getPosition() is not None]
        encounterGhost = [enemy for enemy in enemyGhost if self.getMazeDistance(currentPos, enemy.getPosition()) < 4 and enemy.scaredTimer < 3]
        #if enemy ghost is nearby, get enemy ghost position and distance
        if len(encounterGhost) > 0:
            ghostPosition = [ghost.getPosition() for ghost in encounterGhost]
            closestDistanceToGhost = 9999
            closestGhostPosition = (0,0)
            for position in ghostPosition:
                distanceToGhost = self.getMazeDistance(currentPos, position)
                if distanceToGhost < closestDistanceToGhost:
                    closestDistanceToGhost = distanceToGhost
                    closestGhostPosition = position
            successorClosestDistanceToGhost = self.getMazeDistance(successorPos, closestGhostPosition)
            #scaryGhost = [ghost for ghost in encounterGhost if ghost.getPosition() == closestGhostPosition]

            #get distance to ghost
            gap = successorClosestDistanceToGhost - closestDistanceToGhost
            if gap > 0:
                features['distanceToGhost'] = 1000
            else:
                features['distanceToGhost'] = -1000
            #get distance to nearest capsule
            capsuleList = self.getCapsules(gameState)
            if len(capsuleList) > 0:
                closestDistanceToCapsule = min([self.getMazeDistance(currentPos,capsule) for capsule in capsuleList])
                successorClosestDistanceToCapsule = min([self.getMazeDistance(successorPos,capsule) for capsule in capsuleList])
                features['distanceToCapsule'] = closestDistanceToCapsule - successorClosestDistanceToCapsule
            else:
                features['distanceToCapsule'] = 0

            #get distance to border
            currentDistanceToBorder = min(self.getMazeDistance(currentPos, coordinate) for coordinate in self.border)
            successorDistanceToBorder = min(self.getMazeDistance(successorPos, coordinate) for coordinate in self.border)
            carry = gameState.getAgentState(self.index).numCarrying
            features['distanceToBorder'] = (currentDistanceToBorder - successorDistanceToBorder)*carry

        return features

    def getWeights(self, gameState, action):
        """
        Get weights for the features used in the evaluation.
        """
        return {'distanceToBorder': 10, 'distanceToFood': 50, 'distanceToGhost': 500, 'distanceToCapsule': 500}

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        actions.remove(Directions.STOP)
        featureValues = []
        for a in actions:
            # successor = self.getSuccessor(gameState, a)
            value = self.evaluate(gameState, a)
            featureValues.append(value)

        bestActions = [a for a, v in zip(actions, featureValues) if v == max(featureValues)]
        # carry = gameState.getAgentState(self.index).numCarrying
        # if carry >= 5:
        #     bestDist = 9999
        #     for action in actions:
        #         successor = self.getSuccessor(gameState, action)
        #         pos2 = successor.getAgentPosition(self.index)
        #         dist = self.getMazeDistance(self.start, pos2)
        #         if dist < bestDist:
        #             bestAction = action
        #             bestDist = dist
        #     return bestAction
        chosenAction = random.choice(bestActions)
        if Directions.REVERSE[self.lastAction] == chosenAction:
            self.stuckCount += 1
        if self.stuckCount == 15 and len(actions) != 0:
            self.stuckCount = 0
        self.lastAction = chosenAction
        return chosenAction

class DefendAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free while defending food pellets
    """
    def getFeatures(self, gameState, action):
        features = util.Counter()
        # get successor
        successor = self.getSuccessor(gameState, action)

        # get current and successor position
        currentPos = gameState.getAgentPosition(self.index)
        successorPos = successor.getAgentPosition(self.index)


        # get distance to enemy pacman
        features['distanceToPacman'] = 0

        # get the food that we are defending
        foodList = self.getFoodYouAreDefending(gameState).asList()

        # for each enemy agent, get closest food (food we defending) to the enemy agent
        enemies = [gameState.getAgentState(index) for index in self.getOpponents(successor)]
        closestDistanceToFood1= min([self.getMazeDistance(enemies[0].getPosition(), food) for food in foodList])
        closestFood1 = min([food for food in foodList if self.getMazeDistance(enemies[0].getPosition(), food) == closestDistanceToFood1])
        closestDistanceToFood2 = min([self.getMazeDistance(enemies[1].getPosition(), food) for food in foodList])
        closestFood2 = min([food for food in foodList if self.getMazeDistance(enemies[1].getPosition(), food) == closestDistanceToFood2])

        # get the closest food among two enemy agents
        closestFood = min(closestFood1, closestFood2)

        #get the distance to closest food from defender
        currentDistanceToFood = self.getMazeDistance(currentPos, closestFood)
        successorDistanceToFood = self.getMazeDistance(successorPos, closestFood)
        features['distanceToFood'] = currentDistanceToFood - successorDistanceToFood


        #get distance to border
        enemies = [gameState.getAgentState(index) for index in self.getOpponents(successor)]
        enemies = [a for a in enemies if a.getPosition() in self.enemyBorder1]
        if len(enemies) > 0:
            closestDistanceToFood = 9999
            for enemy in enemies:
                distanceToFood = min([self.getMazeDistance(enemy.getPosition(), food) for food in foodList])
                if distanceToFood < closestDistanceToFood:
                    closestEnemy = enemy
                    closestDistanceToFood = distanceToFood
            closestFood = min([food for food in foodList if
                                self.getMazeDistance(closestEnemy.getPosition(), food) == closestDistanceToFood])
            currentDistanceToFood = self.getMazeDistance(currentPos, closestFood)
            successorDistanceToFood = self.getMazeDistance(successorPos, closestFood)
            features['distanceToFood'] = currentDistanceToFood - successorDistanceToFood
            closestDistanceToBorder = min([self.getMazeDistance(closestFood, border) for border in self.border])
            closestBorder = min([border for border in self.border if
                                 self.getMazeDistance(closestFood, border) == closestDistanceToBorder])
            currentDistanceToBorder = self.getMazeDistance(currentPos, closestBorder)
            successorDistanceToBorder = self.getMazeDistance(successorPos, closestBorder)
            features['distanceToBorder'] = currentDistanceToBorder - successorDistanceToBorder
            # minDistanceToBorder = 9999
            # closestBorder = (0,0)
            # for enemy in enemies:
            #     closestDistanceToBorder = min([self.getMazeDistance(enemy.getPosition(), border) for border in self.border])
            #     if closestDistanceToBorder < minDistanceToBorder:
            #         minDistanceToBorder = closestDistanceToBorder
            #         closestBorder = min([border for border in self.border if
            #                       self.getMazeDistance(enemy.getPosition(), border) == closestDistanceToBorder])
            # currentDistanceToBorder = self.getMazeDistance(currentPos, closestBorder)
            # successorDistanceToBorder = self.getMazeDistance(successorPos, closestBorder)
            # features['distanceToBorder'] = currentDistanceToBorder - successorDistanceToBorder
            # features['distanceToFood'] = 0
            # self.debugDraw([closestBorder], [1, 1, 0], True)
            #self.debugDraw(self.enemyBorder1, [1, 0, 0], True)
            #self.debugDraw(self.enemyBorder2, [1, 0, 0], True)
            #
            # closestDistanceToBorder1 = min([self.getMazeDistance(enemies[0].getPosition(), border) for enemy in enemies])
            # closestBorder1 = min([border for border in self.border if
            #                     self.getMazeDistance(enemies[0].getPosition(), border) == closestDistanceToBorder1])
            # closestDistanceToBorder2 = min([self.getMazeDistance(enemies[1].getPosition(), border) for border in self.border])
            # closestBorder2 = min([border for border in self.border if
            #                     self.getMazeDistance(enemies[1].getPosition(), border) == closestDistanceToBorder2])
            # closestBorder = min(closestBorder1, closestBorder2)
            # self.debugDraw([closestBorder], [1, 1, 0], True)
            # # get the distance to closest food from defender
            # currentDistanceToBorder = self.getMazeDistance(currentPos, closestBorder)
            # successorDistanceToBorder = self.getMazeDistance(successorPos, closestBorder)
            # features['distanceToBorder'] = currentDistanceToBorder - successorDistanceToBorder
            # currentDistanceToBorder = min(self.getMazeDistance(currentPos, coordinate) for coordinate in self.border)
        # successorDistanceToBorder = min(self.getMazeDistance(successorPos, coordinate) for coordinate in self.border)

        # get distance to center
        # currentDistanceToBorder = self.getMazeDistance(currentPos, self.center)
        # successorDistanceToBorder = self.getMazeDistance(successorPos, self.center)
        # features['distanceToBorder'] = currentDistanceToBorder - successorDistanceToBorder



        enemies = [gameState.getAgentState(index) for index in self.getOpponents(successor)]
        enemyPacman= [a for a in enemies if a.isPacman]
        # if the enemy enter our territory and trying to steal our food
        if len(enemyPacman) > 0:
            #try to get the closest enemy pacman and its distance to our defender
            pacmanPosition = [pacman.getPosition() for pacman in enemyPacman]
            closestDistanceToPacman = 9999
            closestPacmanPosition = (0,0)
            for position in pacmanPosition:
                distanceToPacman = self.getMazeDistance(currentPos,position)
                if distanceToPacman < closestDistanceToPacman:
                    closestDistanceToPacman = distanceToPacman
                    closestPacmanPosition = position
            successorClosestDistanceToPacman = self.getMazeDistance(successorPos, closestPacmanPosition)
            features['distanceToPacman'] = closestDistanceToPacman - successorClosestDistanceToPacman

            # get distance to closest food that enemy trying to steal
            foodList = self.getFoodYouAreDefending(gameState).asList()
            closestDistanceToFood = min([self.getMazeDistance(closestPacmanPosition, food) for food in foodList])
            # successorDistanceToFood = min([self.getMazeDistance(successorPos, food) for food in foodList])
            # features['distanceToFood'] = (currentDistanceToFood - successorDistanceToFood)
            closestFood = min([food for food in foodList if self.getMazeDistance(closestPacmanPosition, food) == closestDistanceToFood])

            #get the distance to closest food that we should defend from our defender
            currentDistanceToFood = self.getMazeDistance(currentPos, closestFood)
            successorDistanceToFood = self.getMazeDistance(successorPos, closestFood)
            features['distanceToFood'] = currentDistanceToFood - successorDistanceToFood

            #if the capsule list that we are defending is not empty, get the distance to closest capsule
            capsuleList = self.getCapsulesYouAreDefending(gameState)
            if len(capsuleList) > 0:
                pacmanDistanceToCapsule = min([self.getMazeDistance(closestPacmanPosition, capsule) for capsule in capsuleList])
                closestCapsule = min([capsule for capsule in capsuleList if self.getMazeDistance(closestPacmanPosition, capsule) == pacmanDistanceToCapsule])
                closestDistanceToCapsule = self.getMazeDistance(currentPos, closestCapsule)
                successorClosestDistanceToCapsule = self.getMazeDistance(successorPos, closestCapsule)
                features['distanceToCapsule'] = closestDistanceToCapsule - successorClosestDistanceToCapsule

                # if pacmanDistanceToCapsule < closestDistanceToFood:
                #     features['distanceToCapsule'] = closestDistanceToCapsule - successorClosestDistanceToCapsule
                #     features['distanceToFood'] = features['distanceToFood'] / 2
                #     self.debugDraw([closestCapsule, closestFood], [1, 0, 0], True)
                #     print("capsule")
                # else:
                #     features['distanceToCapsule'] = 0
            else:
                 features['distanceToCapsule'] = 0

            #if our defender is scared after the enemy ate the capsule, try to suicide by walking towards the closest food or enemy
            myTeamDefender = gameState.getAgentState(self.index)
            if myTeamDefender.scaredTimer > 4:
                features['distanceToPacman'] = 3 * features['distanceToPacman']
                features['distanceToCapsule'] = 0 * features['distanceToCapsule']
                features['distanceToFood'] = 0.01 * features['distanceToFood']
                return features

        return features

    def getWeights(self, gameState, action):
        """
        Get weights for the features used in the evaluation.
        """
        return {'distanceToBorder': 150, 'distanceToPacman': 200, 'distanceToCapsule': 125, 'distanceToFood' : 100}
