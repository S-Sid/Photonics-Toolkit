import matplotlib.pyplot as plt
import math
import numpy as np

x = None
x = np.linspace(-10,10, num = 1000)
y = [math.exp(i) / (math.exp(i)+1) for i in x]

plt.plot(x,y)
plt.show()