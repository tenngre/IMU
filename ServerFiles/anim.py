import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def beta_pdf(x, a, b):
    return (x**(a-1) * (1-x)**(b-1) * math.gamma(a + b)
            / (math.gamma(a) * math.gamma(b)))


class UpdateDist:
    def __init__(self, prob=0.5):
        self.fig, self.ax = plt.subplots()
        self.success = 0
        self.prob = prob
        self.line, = self.ax.plot([], [], 'k-')
        self.x = np.linspace(0, 1, 200)

        # Set up plot parameters
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 10)
        self.ax.grid(True)

        # This vertical line represents the theoretical value, to
        # which the plotted distribution should converge.
        self.ax.axvline(prob, linestyle='--', color='black')

    def __call__(self, i):
        # This way the plot can continuously run and we just keep
        # watching new realizations of the process
        if i == 0:
            self.success = 0
            self.line.set_data([], [])
            return self.line,

        # Choose success based on exceed a threshold with a uniform pick
        if np.random.rand(1,) < self.prob:
            self.success += 1
        y = beta_pdf(self.x, self.success + 1, (i - self.success) + 1)
        self.line.set_data(self.x, y)
        return self.line,

    def run(self):
        ud = UpdateDist(prob=0.7)
        anim = FuncAnimation(self.fig, ud, frames=100, interval=100, blit=True)
        plt.show()


# Fixing random state for reproducibility
np.random.seed(19680801)

if __name__ == '__main__':
    p = UpdateDist()
    p.run()




