'''
Title: 2D 抛物方程基于向后Euler格式的有限差分方法

Author:  梁一茹

Address: 湘潭大学  数学与计算科学学院

'''

import numpy as np
from scipy.sparse import diags, coo_matrix
import matplotlib.pyplot as plt
from scipy.sparse.linalg import inv

from fealpy.mesh import UniformMesh2d
from fealpy.timeintegratoralg import UniformTimeLine
from fealpy.tools.show import showmultirate, show_error_table


# 准备模型数据
class moudle:
    def __init__(self, T0, T1, NS, NT):
        self.T0 = T0
        self.T1 = T1

        self.NS = NS
        self.NT = NT

        self.h = 1 / self.NS

    def space_mesh(self):
        mesh = UniformMesh2d((0, self.NS, 0, self.NS), (self.h, self.h), origin=(0.0, 0.0))
        return mesh

    def time_mesh(self):
        time = UniformTimeLine(self.T0, self.T1, self.NT)
        return time

    def solution(self, p, t):
        x = p[..., 0]
        y = p[..., 1]
        return (x ** 2) * (y ** 2) * (t ** 2)

    def source(self, p, t):
        x = p[..., 0]
        y = p[..., 1]
        return (2 * t * (x ** 2) * (y ** 2)) - (2 * t ** 2 * (x ** 2 + y **2 ))

    def dirichlet(self, p, t):
        return self.solution(p, t=t)

    def is_dirichlet_boundary(self, p):
        eps = 1e-12
        x0, x1, y0, y1 = 0, 1, 0, 1
        x = p[..., 0]
        y = p[..., 1]
        flag0 = np.abs(x - x0) < eps
        flag1 = np.abs(x - x1) < eps
        flag2 = np.abs(y - y0) < eps
        flag3 = np.abs(y - y1) < eps
        return flag0 | flag1 | flag2 | flag3

# 向后差分格式
def parabolic_fd2d_backward(pde, mesh, time):
        NT = time.NL - 1
        dt = time.dt
        h = 1 / pde.NS

        n0 = pde.NS + 1
        n1 = pde.NS + 1
        c = 1 / (h ** 2)

        # 组装矩阵
        NN = n0 * n1

        k = np.arange(NN).reshape(n0, n1)

        B = diags([1 + 4 * dt * c], [0], shape=(NN, NN), format='coo')

        val = np.broadcast_to(-dt * c, (NN - n1,))
        I = k[1:, :].flat
        J = k[0:-1, :].flat
        B += coo_matrix((val, (I, J)), shape=(NN, NN), dtype=np.float64)
        B += coo_matrix((val, (J, I)), shape=(NN, NN), dtype=np.float64)

        val = np.broadcast_to(-dt * c, (NN - n0,))
        I = k[:, 1:].flat
        J = k[:, 0:-1].flat
        B += coo_matrix((val, (I, J)), shape=(NN, NN), dtype=np.float64)
        B += coo_matrix((val, (J, I)), shape=(NN, NN), dtype=np.float64)
        A = inv(B)

        F = np.zeros(NN, dtype=np.float64)

        uh = np.zeros((NT + 1, NN), dtype=np.float64)
        u = np.zeros((NT + 1, NN), dtype=np.float64)

        p = mesh.entity('node').reshape(NN,2)
        uh[0] = pde.solution(p, t=0)

        for i in range(NT):

            nt = time.next_time_level()

            F[:] = dt * pde.source(p, nt)

            uh[i + 1] = A @ uh[i] + A @ F

            isBdNode = mesh.ds.boundary_node_flag()

            uh[i + 1][isBdNode] = pde.dirichlet(p[isBdNode], nt)
            u[i + 1] = pde.solution(p, nt)
            time.advance()
        return uh, u

if __name__ == '__main__':
    T0 = 0
    T1 = 1

    NS = 10
    NT = 500
    domain = [0, 1, 0, 1]

    pde = moudle(T0, T1, NS, NT)
    mesh = pde.space_mesh()
    time = pde.time_mesh()

    maxit = 4
    errorType = ['$|| u - u_h||_{C}$', '$|| u - u_h||_{0}$', '$|| u - u_h||_{\ell_2}$']
    errorMatrix = np.zeros((3, maxit), dtype=np.float64)
    NDof = np.zeros(maxit, dtype=np.int_)

    for n in range(maxit):
        uh, u = parabolic_fd2d_backward(pde, mesh, time)

        emax, e0, e1 = mesh.error(mesh.h[0], mesh.nx, mesh.ny,
                                  u=u[-1], uh=uh[-1])

        errorMatrix[0, n] = emax
        errorMatrix[1, n] = e0
        errorMatrix[2, n] = e1

        NDof[n] = (mesh.nx + 1) * (mesh.ny + 1)

        if n < maxit - 1:
            mesh.nx *= 2
            mesh.ny *= 2

            time.uniform_refine()

    show_error_table(NDof, errorType, errorMatrix)
    showmultirate(plt, 0, NDof, errorMatrix, errorType, propsize=10)
    plt.show()