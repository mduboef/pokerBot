import handprobability as handProb
import matplotlib.pyplot as plt

#x = [i for i in range(10)]
#y = [i**2 for i in x]
#
#plt.plot(x,y)
#plt.show()

yRoyalFlush = []
yStraightFlush = []
yFourKind = []
yFullHouse = []
yFlush = []
yStraight = []
yThreeKind = []
yTwoPair = []
yPair = []
yHigh = []
x = []

#for i in range(1, 2000):
#    dist = handProb.handDistribution([], [], 100000, i)
#    yRoyalFlush.append(dist['with_hole']['Royal Flush'])
#    yStraightFlush.append(dist['with_hole']['Straight Flush'])
#    yFourKind.append(dist['with_hole']['Four Kind'])
#    yFullHouse.append(dist['with_hole']['Full House'])
#    yFlush.append(dist['with_hole']['Flush'])
#    yStraight.append(dist['with_hole']['Straight'])
#    yThreeKind.append(dist['with_hole']['Three Kind'])
#    yTwoPair.append(dist['with_hole']['Two Pair'])
#    yPair.append(dist['with_hole']['Pair'])
#    yHigh.append(dist['with_hole']['High'])
#    x.append(dist['iterations'])

for i in range(1, 30000):
    dist = handProb.handDistribution([], [], i/1000, 100000)
    yRoyalFlush.append(dist['with_hole']['Royal Flush'])
    yStraightFlush.append(dist['with_hole']['Straight Flush'])
    yFourKind.append(dist['with_hole']['Four Kind'])
    yFullHouse.append(dist['with_hole']['Full House'])
    yFlush.append(dist['with_hole']['Flush'])
    yStraight.append(dist['with_hole']['Straight'])
    yThreeKind.append(dist['with_hole']['Three Kind'])
    yTwoPair.append(dist['with_hole']['Two Pair'])
    yPair.append(dist['with_hole']['Pair'])
    yHigh.append(dist['with_hole']['High'])
    x.append(i/1000)

print(x)


plt.plot(x, yRoyalFlush, label='Royal Flush')
plt.plot(x, yStraightFlush, label='Straight Flush')
plt.plot(x, yFourKind, label='Four of a Kind')
plt.plot(x, yFullHouse, label='Full House')
plt.plot(x, yFlush, label='Flush')
plt.plot(x, yStraight, label='Straight')
plt.plot(x, yThreeKind, label='Three of a Kind')
plt.plot(x, yTwoPair, label='Two Pair')
plt.plot(x, yPair, label='Pair')
plt.plot(x, yHigh, label='High')
plt.xlabel("Iterations")
plt.ylabel("Hand Probability")
plt.title("Distribution of 7 Card Hands Over Time")
plt.legend()
plt.show()
