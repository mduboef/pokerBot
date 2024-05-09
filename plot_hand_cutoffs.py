import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


data = [[0.6, 0.8, 0.6, 0.7, 0.9, 0.7, 0.7, 0.3, 0.6, 0.3], [0.3, 0.6, 0.6, 0.4, 0.3, 0.3, 0.1, 0.3, 0.3, 0.2], [0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

ax = plt.axes(projection="3d")

z = np.array(data)

y = np.arange(len(z))
x = np.arange(len(z[0]))

(x ,y) = np.meshgrid(x,y)

ax.plot_surface(x,y,z)
ax.set(xlabel = "MID HAND", ylabel = "BAD HAND", zlabel = "WIN RATE", title= "WIN RATE over HAND CUTOFFS")
plt.show()

