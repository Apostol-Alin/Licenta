import numpy as np
import matplotlib.pyplot as plt

k = np.arange(35, 46)
squarings_per_second = pow(2, 30)

time_in_minutes = [2**ki / squarings_per_second / 60 for ki in k]

plt.plot(k, time_in_minutes, marker='o')
plt.xlabel('k')
plt.ylabel('Timp (minute)')
plt.title('Timp in minute vs 2^k (Ridicari modulare la patrat / secunda)')
plt.grid(True)

plt.xticks(k)

for i, txt in enumerate(time_in_minutes):
    plt.annotate(f'{txt:.2f}', (k[i], time_in_minutes[i]), textcoords="offset points", xytext=(0, 5), ha='center')

plt.savefig('time_analysis.png')
