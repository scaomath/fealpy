'''
Title: 1D 抛物方程基于C-N格式的有限差分

Author:  梁一茹

Address: 湘潭大学  数学与计算科学学院

'''

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import inv
import matplotlib.pyplot as plt

from fealpy.mesh import UniformMesh1d
from fealpy.timeintegratoralg import UniformTimeLine
from fealpy.tools.show import showmultirate, show_error_table

# 准备模型数据
class moudle:
    def __init__(self, L, R, T0, T1, a, NS, NT):
        self.L = L
        self.R = R

        self.T0 = T0
        self.T1 = T1

        self.a = a

        self.NS = NS
        self.NT = NT
        self.h = (self.R - self.L) / self.NS

    def space_mesh(self):
        mesh = UniformMesh1d((0, self.NS), h=self.h, origin=0.0)
        return mesh

    def time_mesh(self):
        time = UniformTimeLine(self.T0, self.T1, self.NT)
        return time

    def solution(self, x, t):
        val = (x ** 2) * (t ** 2)
        return val

    def source(self, x, t):
        return (2 * t * (x ** 2)) - (2 * t ** 2)

    def left_solution(self, t):
        return self.solution(x=self.L, t=t)

    def right_solution(self, t):
        return self.solution(x=self.R, t=t)

    def init_solution(self, x):
        return self.solution(x, t=0)

# 六点对称格式
def parabolic_fd1d_CrankNicholson(pde, mesh, time):
    NS = mesh.NC
    NT = time.NL - 1
    dt = time.dt
    h = mesh.h

    r = pde.a * dt / h ** 2
    x = mesh.entity('node')

    # 组装矩阵
    d0 = np.ones(NS - 1, dtype=np.float64)
    d0[:] = 1 - r

    d1 = np.zeros(NS - 2, dtype=np.float64)
    d1[:] = r / 2

    d2 = np.zeros(NS - 2, dtype=np.float64)
    d2[:] = r / 2

    A_0 = diags([d0, d1, d2], [0, 1, -1], shape=(NS - 1, NS - 1), format='csr')

    d0 = np.ones(NS - 1, dtype=np.float64)
    d0[:] = 1 + r

    d1 = np.zeros(NS - 2, dtype=np.float64)
    d1[:] = -r / 2

    d2 = np.zeros(NS - 2, dtype=np.float64)
    d2[:] = -r / 2

    B = diags([d0, d1, d2], [0, 1, -1], shape=(NS - 1, NS - 1), format='csr')
    A_1 = inv(B)

    F = np.zeros(NS - 1, dtype=np.float64)

    uh = np.zeros((NT + 1, NS + 1), dtype=np.float64)
    uh[0] = pde.init_solution(x)

    for i in range(NT):
        ct = time.current_time_level()
        nt = time.next_time_level()

        uh[i + 1, 0] = pde.left_solution(nt)
        uh[i + 1, -1] = pde.right_solution(nt)

        F[:] = dt * pde.source(x[1:-1], ct)

        F[0] += r / 2 * (uh[i, 0] + uh[i + 1, 0])
        F[-1] += r / 2 * (uh[i, -1] + uh[i + 1, -1])

        uh[i + 1, 1:-1] = A_1 @ A_0 @ uh[i, 1:-1] + A_1 @ F
        time.advance()
    return uh


if __name__ == '__main__':
    L = 0
    R = 1

    T0 = 0
    T1 = 1

    a = 1

    NS = 10
    NT = 1000

    pde = moudle(L, R, T0, T1, a, NS, NT)
    mesh = pde.space_mesh()
    time = pde.time_mesh()

    maxit = 4
    errorType = ['$|| u - u_h||_{C}$', '$|| u - u_h||_{0}$', '$|| u - u_h||_{\ell_2}$']
    errorMatrix = np.zeros((3, maxit), dtype=np.float64)
    NDof = np.zeros(maxit, dtype=np.float64)

    for n in range(maxit):
        uh = parabolic_fd1d_CrankNicholson(pde, mesh, time)

        emax, e0, e1 = mesh.error(h=mesh.h,
                                  u=lambda x: pde.solution(x, t=T1),
                                  uh=uh[-1, :])

        errorMatrix[0, n] = emax
        errorMatrix[1, n] = e0
        errorMatrix[2, n] = e1

        NDof[n] = mesh.NN

        if n < maxit - 1:
            mesh.uniform_refine()
            time.uniform_refine()

    show_error_table(NDof, errorType, errorMatrix)
    showmultirate(plt, 0, NDof, errorMatrix, errorType, propsize=10)
    plt.show()