#!/usr/bin/env python3
# 
import sys

import numpy as np
import matplotlib.pyplot as plt
from fealpy.mesh import HalfEdgeMesh2d, CVTPMesher

from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial import KDTree

class CVTPMesherTest:

    def __init__(self):
        pass

    def uniform_boundary_meshing_test(self, plot = True):
        vertices = np.array([
            ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0)],dtype=np.float)
        facets = np.array([
            (0, 1),(1, 2),(2, 3),(3, 0)], dtype=np.int)
        subdomain = np.array([
            (1, 0),(1, 0),(1, 0),(1, 0)], dtype=np.int)
        dof =np.array([1,1,1,1],dtype=np.bool)
        mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
        uniform_boundary_mesh = CVTPMesher(mesh)
        uniform_boundary_mesh.uniform_boundary_meshing(n=1)
        bnode = uniform_boundary_mesh.bnode
        vor = Voronoi(bnode)
        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, color='k', showindex=False)
            mesh.find_node(axes, node=bnode, showindex=False)
            voronoi_plot_2d(vor, ax=axes,show_vertices = False,point_size = 0.3)
            '''
            cs = [axes.add_artist( plt.Circle(x, r, facecolor='none',
                edgecolor='r')) for x, r in zip(center, radius)]
            '''
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_halfedge_plot(axes, showindex=True)
            mesh.find_node(axes, showindex=True)
            plt.show()
    def uniform_meshing_test(self, domain='square' , plot = True , interior_nodes = True,
            add_cnode = True):

        if domain == 'square':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode
       
        elif domain == 'LShape':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0,  1.0),(0.0,  1.0),
                (-1.0, 1.0),(-1.0, 0.0),(-1.0, -1.0),(0.0, -1.0)],dtype=np.float)
            fixed = np.array([1, 1, 1, 0, 1, 0, 1, 1],dtype=np.bool)
            facets = np.array([
               (0, 1), (1, 2), (2, 3), (3, 4), 
               (4, 5), (5, 6), (6, 7), (7, 0)],dtype=np.int)
            subdomain = np.array([
               (1, 0), (1, 0), (1, 0), (1, 0),
               (1, 0), (1, 0), (1, 0), (1, 0)],dtype=np.int)
        
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain, fixed)
            uniform_mesh = CVTPMesher(mesh,fixed)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode

        elif domain =='circle':
            n = 20
            h = 2*np.pi/n
            theta = np.arange(0, 2*np.pi, h)
            vertices = np.zeros((n, 2), dtype=np.float)
            vertices[:, 0] = np.cos(theta)
            vertices[:, 1] = np.sin(theta)
            fixed = np.zeros(n, dtype=np.bool)
            facets = np.zeros((n,2), dtype=np.int)
            facets[:, 0] = range(0, n)
            facets[:-1, 1] = range(1, n)
            subdomain = np.zeros((n, 2),dtype=np.int)
            subdomain[:, 0] = 1

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh= CVTPMesher(mesh,fixed)
            uniform_mesh.uniform_boundary_meshing(n=0)
            bnode = uniform_mesh.bnode

        elif domain =='sc':
            n = 20
            h = 2*np.pi/n
            theta = np.arange(0, 2*np.pi, h)
            vertices = np.zeros((n, 2), dtype=np.float)
            vertices[:, 0] = np.cos(theta)
            vertices[:, 1] = np.sin(theta)
            fixed = np.zeros(n, dtype=np.bool)
            facets = np.zeros((n,2), dtype=np.int)
            facets[:, 0] = range(0, n)
            facets[:-1, 1] = range(1, n)
            subdomain = np.zeros((n, 2),dtype=np.int)
            subdomain[:, 0] = 1

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain,
                    fixed)
            uniform_mesh= CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=0)
            bnode = uniform_mesh.bnode

        elif domain == 'partition1':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),(0.5,0.5)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0),
                (0, 4),(4, 3),(4, 1),(4, 2)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(2, 0),(3, 0),(4, 0),
                (4, 1),(4, 3),(2, 1),(3, 2)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode

        elif domain == 'partition2':
            vertices = np.array([
                ( 0.0, 0.0),(0.5, 0.0),( 1.0, 0.0),(1.0, 0.5),
                ( 1.0, 1.0),(0.5, 1.0),( 0.0, 1.0),(0.0, 0.5),
                ( 0.5, 0.5)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 4),
                (4, 5),(5, 6),(6, 7),(7, 0),
                (1, 8),(8, 7),(8, 3),(8, 5)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(2, 0),(2, 0),(3, 0),
                (3, 0),(4, 0),(4, 0),(1, 0),
                (1, 2),(1, 4),(3, 2),(4, 3)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode
        elif domain == 'hole1':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),
                ( 0.4, 0.4),( 0.4, 0.8),( 0.8, 0.8),( 0.8, 0.4)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),( 2, 3),( 3, 0),
                (4, 5),(5, 6),( 6, 7),( 7, 4)], dtype=np.int_)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1,-1),(1,-1),(1,-1),(1,-1)], dtype=np.int_)

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            times = np.zeros(len(facets))
            times[:4] = 6
            times[4:] = 3
            uniform_mesh.uniform_boundary_meshing(n=5,times = times)
            bnode = uniform_mesh.bnode
        elif domain == 'hole2':
            #""" 
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 2.0, 0.0),( 2.0, 1.0),
                ( 2.0, 2.0),( 1.0, 2.0),( 0.0, 2.0),( 0.0, 1.0),
                ( 0.4, 0.4),( 0.4, 0.7),( 0.7, 0.7),( 0.7, 0.4),
                ( 1.2, 1.2),( 1.2, 1.5),( 1.5, 1.5),( 1.5, 1.2)],dtype=np.float)
            facets = np.array([
                ( 0, 1),( 1, 2),( 2, 3),( 3, 4),
                ( 4, 5),( 5, 6),( 6, 7),( 7, 0),
                ( 8, 9),( 9,10),(10,11),(11, 8),
                (12,13),(13,14),(14,15),(15,12),], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1,-1),(1,-1),(1,-1),(1,-1),
                (1,-2),(1,-2),(1,-2),(1,-2)], dtype=np.int)

            #"""

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=1)
            bnode = uniform_mesh.bnode

        if domain == 'square2':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),
                ( 2.0, 0.0),( 3.0, 0.0),( 3.0, 1.0),( 2.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0),
                (4, 5),(5, 6),(6, 7),(7, 4)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (2, 0),(2, 0),(2, 0),(2, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode

        if domain == 'triangle':
            vertices = np.array([
                ( 0.0, 0.0),( 2.0, 0.0),( 1.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 0)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            #cs = [axes.add_artist( plt.Circle(x, r, facecolor='none',edgecolor='r')) for x, r in zip(center, radius)]
            mesh.find_node(axes, color='k', showindex=True)
            mesh.find_node(axes, node=bnode, showindex=True)
            #mesh.print()
            plt.show()

       
        if domain == 'trapezoid':
            vertices = np.array([
                ( 0.0, 0.0),( 4.0, 0.0),( 3.8, 4.0),(0.2,4.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3,0)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1,0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_boundary_meshing(n=2)
            bnode = uniform_mesh.bnode
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            #cs = [axes.add_artist( plt.Circle(x, r, facecolor='none',edgecolor='r')) for x, r in zip(center, radius)]
            mesh.find_node(axes, color='k', showindex=True)
            mesh.find_node(axes, node=bnode, showindex=True)
            plt.show()

        if add_cnode == True:
            cnode = uniform_mesh.cnode
            bnode = np.append(bnode, cnode,axis=0)
        
        vor = Voronoi(bnode, incremental = True)
        if interior_nodes:
            uniform_mesh.uniform_init_interior_nodes()
            newnode = uniform_mesh.inode
            for k in newnode:
                vor.add_points(newnode[k])
        
        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, color='k', showindex=False)
            mesh.find_node(axes, node=bnode, showindex=True)
            #mesh.print()
            voronoi_plot_2d(vor, ax=axes,show_vertices = False)
            plt.show()
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_halfedge_plot(axes, showindex=False)
            mesh.find_node(axes, showindex=False)
            plt.show()
    
    def Lloyd_test(self,domain = 'square', plot = True):
        if domain == 'square':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)
       
        elif domain == 'LShape':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0,  1.0),(0.0,  1.0),
               (-1.0, 1.0),(-1.0, 0.0),(-1.0, -1.0),(0.0, -1.0)],dtype=np.float)
            fixed = np.array([1, 1, 1, 0, 1, 0, 1, 1],dtype=np.bool)
            facets = np.array([
               (0, 1), (1, 2), (2, 3), (3, 4), 
               (4, 5), (5, 6), (6, 7), (7, 0)],dtype=np.int)
            subdomain = np.array([
               (1, 0), (1, 0), (1, 0), (1, 0),
               (1, 0), (1, 0), (1, 0), (1, 0),],dtype=np.int)
        
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets,
                    subdomain,fixed)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)
        elif domain =='circle':
            n = 20
            h = 2*np.pi/n
            theta = np.arange(0, 2*np.pi, h)
            vertices = np.zeros((n, 2), dtype=np.float)
            vertices[:, 0] = np.cos(theta)
            vertices[:, 1] = np.sin(theta)
            fixed = np.zeros(n, dtype=np.bool)
            facets = np.zeros((n,2), dtype=np.int)
            facets[:, 0] = range(0, n)
            facets[:-1, 1] = range(1, n)
            subdomain = np.zeros((n, 2),dtype=np.int)
            subdomain[:, 0] = 1

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain,
                    fixed)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)

        elif domain =='circle_hole':
            n = 20
            h = 2*np.pi/n
            theta = np.arange(0, 2*np.pi, h)
            vertices1 = np.array([(-2.0,-2.0),(2.0,-2.0),(2.0,2.0),(-2.0,2.0)])
            vertices2 = np.zeros((n, 2), dtype=np.float)
            vertices2[:, 0] = np.cos(theta)
            vertices2[:, 1] = -np.sin(theta)
            vertices = np.vstack((vertices1,vertices2))
            n = len(vertices)
            fixed = np.ones(n, dtype=np.bool)
            fixed[4:] = False
            facets = np.zeros((n,2), dtype=np.int)
            facets[:4, 0] = range(0, 4)
            facets[:3, 1] = range(1, 4)
            facets[4:, 0] = range(4, n)
            facets[4:-1, 1] = range(5, n)
            facets[-1,1] = 4
            subdomain = np.zeros((n, 2),dtype=np.int)
            subdomain[:4, 0] = 1
            subdomain[4:,0] = 1
            subdomain[4:,1] = -1
            times = np.zeros(n)
            times[:4] = 3
            times[4:] = 1
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain,
                    fixed)
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            plt.show()
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=7,times = times)

        elif domain == 'partition1':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),(0.5,0.5)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0),
                (0, 4),(4, 3),(4, 1),(4, 2)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(2, 0),(3, 0),(4, 0),
                (4, 1),(4, 3),(2, 1),(3, 2)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=3)

        elif domain == 'partition2':
            vertices = np.array([
                ( 0.0, 0.0),(0.5, 0.0),( 1.0, 0.0),(1.0, 0.5),
                ( 1.0, 1.0),(0.5, 1.0),( 0.0, 1.0),(0.0, 0.5),
                ( 0.5, 0.5)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 4),
                (4, 5),(5, 6),(6, 7),(7, 0),
                (1, 8),(8, 7),(8, 3),(8, 5)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(2, 0),(2, 0),(3, 0),
                (3, 0),(4, 0),(4, 0),(1, 0),
                (1, 2),(1, 4),(3, 2),(4, 3)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)

        elif domain == 'hole1':
            
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),
                ( 0.4, 0.4),( 0.4, 0.8),( 0.8, 0.8),( 0.8, 0.4)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),( 2, 3),( 3, 0),
                (4, 5),(5, 6),( 6, 7),( 7, 4)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1,-1),(1,-1),(1,-1),(1,-1)], dtype=np.int)

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            times = np.zeros(len(facets))
            times[:4] = 3
            times[4:] = 2
            uniform_mesh.uniform_meshing(n=5,times = times)
        elif domain == 'square2':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 1.0, 1.0),( 0.0, 1.0),
                ( 2.0, 0.0),( 3.0, 0.0),( 3.0, 1.0),( 2.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),(3, 0),
                (4, 5),(5, 6),(6, 7),(7, 4)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (2, 0),(2, 0),(2, 0),(2, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)

        elif domain == 'hole2':
            #""" 
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, 0.0),( 2.0, 0.0),( 2.0, 1.0),
                ( 2.0, 2.0),( 1.0, 2.0),( 0.0, 2.0),( 0.0, 1.0),
                ( 0.4, 0.4),( 0.4, 0.7),( 0.7, 0.7),( 0.7, 0.4),
                ( 1.2, 1.2),( 1.2, 1.5),( 1.5, 1.5),( 1.5, 1.2)],dtype=np.float)
            facets = np.array([
                ( 0, 1),( 1, 2),( 2, 3),( 3, 4),
                ( 4, 5),( 5, 6),( 6, 7),( 7, 0),
                ( 8, 9),( 9,10),(10,11),(11, 8),
                (12,13),(13,14),(14,15),(15,12),], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1, 0),(1, 0),(1, 0),(1, 0),
                (1,-1),(1,-1),(1,-1),(1,-1),
                (1,-2),(1,-2),(1,-2),(1,-2)], dtype=np.int)

            #"""

            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            #uniform_mesh.uniform_boundary_meshing(n=1)
            uniform_mesh.uniform_meshing(n=2)
            #bnode = uniform_mesh.bnode

        elif domain == 'hexagon':
            vertices = np.array([
                ( 0.0, 0.0),( 1.0, -1.0),( 2.0, -1.0),
                ( 3.0,0.0) ,( 2.0, 1.0 ),( 1.0, 1.0)],dtype=np.float)
            facets = np.array([
                (0, 1),(1, 2),(2, 3),
                (3, 4), (4, 5),(5, 0)], dtype=np.int)
            subdomain = np.array([
                (1, 0),(1, 0),(1, 0),(1, 0),(1, 0),(1, 0)], dtype=np.int)
            mesh = HalfEdgeMesh2d.from_edges(vertices, facets, subdomain)
            uniform_mesh = CVTPMesher(mesh)
            uniform_mesh.uniform_meshing(n=2)

        #mesh.print()
        vor, start = uniform_mesh.voronoi()
        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, color='k', showindex=False)
            mesh.find_node(axes, node=vor.points, showindex=False)
            voronoi_plot_2d(vor, ax=axes,show_vertices = False, point_size =
                    0.3)
            plt.show()
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_halfedge_plot(axes, showindex=False)
            mesh.find_node(axes, showindex=True)
            plt.show()
       
        i =0
        while i<20:
            vor = uniform_mesh.Lloyd(vor,start)
            i+=1
        pmesh = uniform_mesh.to_PolygonMesh(vor) 
        fig = plt.figure()
        axes= fig.gca()
        pmesh.add_plot(axes)
        plt.show()

        if plot:
            fig = plt.figure()
            axes = fig.gca()
            mesh.add_plot(axes)
            mesh.find_node(axes, color='k', showindex=False)
            mesh.find_node(axes, node=vor.points, showindex=False)
            voronoi_plot_2d(vor, ax=axes,show_vertices = False)
            plt.show()
 







test = CVTPMesherTest()
'''
if sys.argv[1] == "UN":
    if sys.argv[2] =="S":
        test.uniform_meshing_test(domain='square')
    elif sys.argv[2] =="LS":
        test.uniform_meshing_test(domain='LShape')
    elif sys.argv[2] =="TL":
        test.uniform_meshing_test(domain='triangle')
    elif sys.argv[2] =="C":
        uniform_meshing_test(domain='circle')

if sys.argv[1] == "Lloyd":
    if sys.argv[2] =="S":
        test.Lloyd_test(domain='square')
    elif sys.argv[2] =="LS":
        test.Lloyd_test(domain='LShape')
    elif sys.argv[2] =="TL":
        test.Lloyd_test(domain='triangle')
    elif sys.argv[2] =="C":
        test.Lloyd_test(domain='circle')
'''

#test.uniform_boundary_meshing_test()
#test.uniform_meshing_test(domain='square')
#test.uniform_meshing_test(domain='square2',interior_nodes = True)
#test.uniform_meshing_test(domain='LShape')
#test.uniform_meshing_test(domain='triangle',interior_nodes = False)
#test.uniform_meshing_test(domain='circle')
#test.uniform_meshing_test(domain='trapezoid',interior_nodes = True)
#test.uniform_meshing_test(domain = 'partition1')
#test.uniform_meshing_test(domain = 'partition2')
#test.uniform_meshing_test(domain = 'hole1',interior_nodes = True)
#test.uniform_meshing_test(domain='hole2',interior_nodes=False)
#test.Lloyd_test(domain='square')
#test.Lloyd_test(domain = 'LShape')
#test.Lloyd_test(domain = 'circle')
test.Lloyd_test(domain='circle_hole')
#test.Lloyd_test(domain='partition1')
#test.Lloyd_test(domain='partition2')
#test.Lloyd_test(domain = 'hole1')
#test.Lloyd_test(domain='hole2')
#test.Lloyd_test(domain='square2')
#test.Lloyd_test(domain = 'hexagon')


