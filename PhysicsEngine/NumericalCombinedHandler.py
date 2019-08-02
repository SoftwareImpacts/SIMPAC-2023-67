# Red Ciudadana de Estaciones Meteorologicas
#
# Copyright @ 2019
#
# Author: Santiago Nunez-Corrales <snunezcr@gmail.com>

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.integrate import cumtrapz
from PhysicsEngine import PhysicsHandler


class NumericalCombinedHandler(PhysicsHandler):
    sa_norm = 1.6075

    def __init__(self, v0=0, theta=0, m=1, rho=1, a=0.0, b=0.0, c=0.0, Cd=1, height=0, distance=0):
        self.v0 = v0
        self.theta = theta
        self.m = m
        self.m = m
        self.rho = rho
        self.a = a
        self.b = b
        self.c = c
        self.Cd = Cd
        self.height = height
        self.distance = distance
        self.windx = 0
        self.windz = 0
        self.data = None
        self.computeIdeal = False

    @staticmethod
    def norm(a, b):
        return np.sqrt(np.power(a, 2) + np.power(b, 2))

    @property
    def surfArea(self):
        projareap = np.power(self.a*self.b, self.sa_norm) + np.power(self.a*self.c, self.sa_norm) + np.power(self.b*self.c, self.sa_norm)
        return 4*np.pi*np.power(projareap/3.0, 1.0/self.sa_norm)

    def E(self, v):
        return (self.rho*v*v*self.surfArea)/(2*self.m)

    def compute(self):
        tstart = 0
        tend = 200
        tsamples = 10001
        trng = np.linspace(tstart, tend, tsamples)

        vx0 = self.v0 * np.cos(self.theta)
        vy0 = self.v0 * np.sin(self.theta)

        def acc(t, v):
            vx = v[0]
            vy = v[1]

            v = self.norm(vx, vy)
            Enow = self.E(v)

            dvxdt = -Enow * self.Cd * (vx - self.windx)/v
            dvydt = -Enow * self.Cd * (vy / v) - self.g
            return [dvxdt, dvydt]

        # Integrate velocities
        vel0 = [vx0, vy0]
        vel = solve_ivp(acc, [0, 200], vel0, method='RK45', t_eval=trng).y
        vxrng = vel[0]
        vyrng = vel[1]

        # Integrate positions
        xrng = cumtrapz(vxrng, trng, initial=0)
        yrng = cumtrapz(vyrng, trng, initial=0)

        vrng = np.sqrt(np.power(vxrng, 2) + np.power(vyrng, 2))
        darray = np.transpose(np.array([trng, xrng, yrng, vxrng, vyrng, vrng]))
        self.data = pd.DataFrame(
            {'t': darray[:, 0], 'x': darray[:, 1], 'y': darray[:, 2], 'vx': darray[:, 3], 'vy': darray[:, 4],
             'v': darray[:, 5]})
        self.data = self.data[self.data['y'] >= self.height]

    def save_csv(self, filename):
        if (filename == '') or (self.data is None):
            return
        else:
            self.data.to_csv(filename)

    def maxT(self):
        if self.data is None:
            return 0.0
        else:
            return self.data[self.data['y'] == self.data['y'].max()]['t'].values[0]

    def maxH(self):
        if self.data is None:
            return 0.0
        else:
            return self.data[self.data['y'] == self.data['y'].max()]['y'].values[0]

    def totalR(self):
        if self.data is None:
            return 0.0
        else:
            return self.data.tail(1)['x'].values[0]

    def totalT(self):
        if self.data is None:
            return 0.0
        else:
            return self.data.tail(1)['t'].values[0]

    def finalTheta(self):
        if self.data is None:
            return 0.0
        else:
            if self.data.tail(1)['vx'].values[0] == 0:
                return 90.0
            else:
                return -1 * np.rad2deg(np.arctan(self.data.tail(1)['vy'].values[0] / self.data.tail(1)['vx'].values[0]))

    def finalV(self):
        if self.data is None:
            return 0.0
        else:
            return self.data.tail(1)['v'].values[0]
