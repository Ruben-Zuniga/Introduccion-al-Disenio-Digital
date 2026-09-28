import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

L = 10000
B = 5
# x = (np.linspace(0,L,L)) / L - 0.5
x = np.zeros(L) + 1
y = np.zeros(L)
y1 = np.zeros(L)
v1 = np.zeros(L)
e1 = np.zeros(L)
y2 = np.zeros(L)
v2 = np.zeros(L)
e2 = np.zeros(L)

for n in range(1,L-1):
    v1[n+1] = x[n] - y1[n] + v1[n]
    if v1[n+1] >= 0:
        y1[n+1] = B
    else:
        y1[n+1] = -B

    v2[n+1] = v1[n] - y1[n] - y2[n] + v2[n]
    if v2[n+1] >= 0:
        y2[n+1] = B
    else:
        y2[n+1] = -B

    y[n+1] = y1[n] + y2[n+1] - y2[n]

print(x,'\n')
print(v1,'\n')
print(y1,'\n')
print(v2,'\n')
print(y2,'\n')
print(y,'\n')


plt.figure()
plt.plot(y2,label='y')
plt.plot(x,label='x')
plt.grid()
plt.legend()
plt.show()