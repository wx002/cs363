import matplotlib.pyplot as plt
import numpy as np

x = ['Ideal','Good','Medium']
y = [1410.0857887050586, 135.1386281553791, 70.00680633241944]
title = 'Transfer rate in bytes per second benchmarks for RDT'
y_pos = np.arange(len(x))
plt.bar(y_pos, y, align='center')
plt.xticks(y_pos, x)
plt.ylabel('Transfer rate in bytes per second')
plt.xlabel('Network Conditions')
plt.title(title)
plt.show()