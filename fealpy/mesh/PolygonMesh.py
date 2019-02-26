import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix, spdiags, eye, tril, triu
from ..common import ranges
from .mesh_tools import unique_row, find_entity, show_mesh_2d
from ..quadrature import TriangleQuadrature
from .Mesh2d import Mesh2d

class PolygonMesh(Mesh2d):

    """ 2d Polygon Mesh data structure from vtk data structure
    """
    def __init__(self, node, cell, cellLocation=None, dtype = np.float64):
        self.node = node
        if cellLocation is None: 
            if len(cell.shape)  == 2:
                NC = cell.shape[0]
                NV = cell.shape[1]
                cell = cell.reshape(-1)
                cellLocation = np.arange(0, (NC+1)*NV, NV)
            else:
                raise(ValueError("Miss `cellLocation` array!"))

        self.ds = PolygonMeshDataStructure(node.shape[0], cell, cellLocation)
        self.meshtype = 'polygon'
        self.itype = cell.dtype
        self.ftype = node.dtype

    def integrator(self, k):
        return TriangleQuadrature(k)

    def number_of_vertices_of_cells(self):
        return self.ds.number_of_vertices_of_cells()

    def to_vtk(self):
        NC = self.number_of_cells()
        cell = self.ds.cell
        cellLocation = self.ds.cellLocation
        NV = self.ds.number_of_vertices_of_cells()
        cells = np.zeros(len(cell) + NC, dtype=np.int)
        isIdx = np.ones(len(cell) + NC, dtype=np.bool)
        isIdx[0] = False
        isIdx[np.add.accumulate(NV+1)[:-1]] = False
        cells[~isIdx] = NV
        cells[isIdx] = cell
        return NC, cells 

    @classmethod
    def from_mesh(cls, mesh):
        node = mesh.node
        cell = mesh.ds.cell
        NC = mesh.number_of_cells()
        NV = cell.shape[1]
        cellLocation = np.arange(0, (NC+1)*NV, NV)
        return cls(node, cell.reshape(-1), cellLocation)

    @classmethod
    def from_quadtree(cls, quadtree):
        node, cell, cellLocation = quadtree.to_pmesh()
        return cls(node, cell, cellLocation)

    def entity_barycenter(self, etype='cell', index=None):
        node = self.node
        dim = self.geo_dimension()

        if etype in ['cell', 2]:
            cell2node = self.ds.cell_to_node()
            NV = self.number_of_vertices_of_cells().reshape(-1,1)
            bc = cell2node*node/NV 
        elif etype in ['edge', 1]:
            edge = self.ds.edge
            bc = np.sum(node[edge, :], axis=1).reshape(-1, dim)/edge.shape[1]
        elif etype in ['node', 1]:
            bc = node
        return bc

    def angle(self):
        node = self.node
        cell = self.ds.cell
        cellLocation = self.ds.cellLocation

        idx1 = np.zeros(cell.shape[0], dtype=np.int)
        idx2 = np.zeros(cell.shape[0], dtype=np.int)

        idx1[0:-1] = cell[1:]
        idx1[cellLocation[1:]-1] = cell[cellLocation[:-1]]
        idx2[1:] = cell[0:-1]
        idx2[cellLocation[:-1]] = cell[cellLocation[1:]-1]
        a = node[idx1] - node[cell]
        b = node[idx2] - node[cell]
        la = np.sum(a**2, axis=1)
        lb = np.sum(b**2, axis=1)
        x = np.arccos(np.sum(a*b, axis=1)/np.sqrt(la*lb))
        return np.degrees(x)

    def node_normal(self):
        node = self.node
        cell = self.ds.cell
        cellLocation = self.ds.cellLocation

        idx1 = np.zeros(cell.shape[0], dtype=np.int)
        idx2 = np.zeros(cell.shape[0], dtype=np.int)

        idx1[0:-1] = cell[1:]
        idx1[cellLocation[1:]-1] = cell[cellLocation[:-1]]
        idx2[1:] = cell[0:-1]
        idx2[cellLocation[:-1]] = cell[cellLocation[1:]-1]

        w = np.array([(0,-1),(1,0)])
        d = node[idx1] - node[idx2] 
        return 0.5*d@w 

    def area(self, index=None):
        #TODO: 3D Case
        NC = self.number_of_cells()
        node = self.node
        edge = self.ds.edge
        edge2cell = self.ds.edge2cell
        isInEdge = (edge2cell[:, 0] != edge2cell[:, 1])
        w = np.array([[0, -1], [1, 0]], dtype=np.int)
        v= (node[edge[:, 1], :] - node[edge[:, 0], :])@w
        val = np.sum(v*node[edge[:, 0], :], axis=1)
        a = np.bincount(edge2cell[:, 0], weights=val, minlength=NC)
        a+= np.bincount(edge2cell[isInEdge, 1], weights=-val[isInEdge], minlength=NC)
        a /=2
        return a

    def cell_area(self, index=None):
        #TODO: 3D Case
        NC = self.number_of_cells()
        node = self.node
        edge = self.ds.edge
        edge2cell = self.ds.edge2cell
        isInEdge = (edge2cell[:, 0] != edge2cell[:, 1])
        w = np.array([[0, -1], [1, 0]], dtype=np.int)
        v= (node[edge[:, 1], :] - node[edge[:, 0], :])@w
        val = np.sum(v*node[edge[:, 0], :], axis=1)
        a = np.bincount(edge2cell[:, 0], weights=val, minlength=NC)
        a+= np.bincount(edge2cell[isInEdge, 1], weights=-val[isInEdge], minlength=NC)
        a /=2
        return a

    def print(self):
        print("Node:\n", self.node)
        print("Cell:\n", self.ds.cell)
        print("Edge:\n", self.ds.edge)
        print("Edge2cell:\n", self.ds.edge2cell)
        print("Cell2edge:\n", self.ds.cell_to_edge())



class PolygonMeshDataStructure():
    def __init__(self, NN, cell, cellLocation):
        self.NN = NN
        self.NC = cellLocation.shape[0] - 1

        self.cell = cell
        self.cellLocation = cellLocation
        self.construct()

    def reinit(self, N, cell, cellLocation):
        self.N = N
        self.NC = cellLocation.shape[0] - 1

        self.cell = cell
        self.cellLocation = cellLocation
        self.construct()

    def clear(self):
        self.edge = None
        self.edge2cell = None

    def number_of_vertices_of_cells(self):
        cellLocation = self.cellLocation 
        return cellLocation[1:] - cellLocation[0:-1] 

    def number_of_edges_of_cells(self):
        cellLocation = self.cellLocation 
        return cellLocation[1:] - cellLocation[0:-1] 

    def total_edge(self):
        cell = self.cell
        cellLocation = self.cellLocation

        NN = self.NN
        NC = self.NC
        NV = self.number_of_vertices_of_cells() 

        totalEdge = np.zeros((cell.shape[0], 2), dtype=np.int)
        totalEdge[:, 0] = cell
        totalEdge[:-1, 1] = cell[1:] 
        totalEdge[cellLocation[1:] - 1, 1] = cell[cellLocation[:-1]]
        return totalEdge

    def construct(self):  
        NC = self.NC
        
        cell = self.cell
        cellLocation = self.cellLocation
        NV = self.number_of_vertices_of_cells() 

        totalEdge = self.total_edge()
        _, i0, j = unique_row(np.sort(totalEdge, axis=1))

        NE = i0.shape[0]
        self.NE = NE
        self.edge2cell = np.zeros((NE, 4), dtype=np.int)

        i1 = np.zeros(NE, dtype=np.int) 
        i1[j] = np.arange(len(cell))

        self.edge = totalEdge[i0]

        cellIdx = np.repeat(range(NC), NV)
        
        localIdx = ranges(NV)

        self.edge2cell[:, 0] = cellIdx[i0] 
        self.edge2cell[:, 1] = cellIdx[i1] 
        self.edge2cell[:, 2] = localIdx[i0] 
        self.edge2cell[:, 3] = localIdx[i1] 

    def cell_to_node(self):
        NN = self.NN
        NC = self.NC
        NE = self.NE

        cell = self.cell
        cellLocation = self.cellLocation
        NV = self.number_of_vertices_of_cells() 
        I = np.repeat(range(NC), NV)
        J = cell

        val = np.ones(len(cell), dtype=np.bool)
        cell2node = csr_matrix((val, (I, J)), shape=(NC, NN), dtype=np.bool)
        return cell2node

    def cell_to_edge(self, sparse=True):
        NE = self.NE
        NC = self.NC

        edge2cell = self.edge2cell
        cell = self.cell
        cellLocation = self.cellLocation

        if sparse:
            J = np.arange(NE)
            val = np.ones((NE,), dtype=np.bool)
            cell2edge = coo_matrix((val, (edge2cell[:,0], J)), shape=(NC, NE), dtype=np.bool)
            cell2edge += coo_matrix((val, (edge2cell[:,1], J)), shape=(NC, NE), dtype=np.bool)
            return cell2edge.tocsr()
        else:
            cell2edge = np.zeros(cell.shape[0], dtype=np.int)
            cell2edge[cellLocation[:-1]+edge2cell[:, 2]] = range(NE)
            cell2edge[cellLocation[:-1]+edge2cell[:, 3]] = range(NE)
            return cell2edge

    def cell_to_edge_sign(self):
        NE = self.NE
        NC = self.NC
        edge2cell = self.edge2cell
        val = np.ones((NE,), dtype=np.bool)
        cell2edgeSign = csr_matrix((val, (edge2cell[:,0], range(NE))), shape=(NC,NE), dtype=np.bool)
        return cell2edgeSign

    def cell_to_cell(self):
        NC = self.NC
        edge2cell = self.edge2cell
        isInEdge = (edge2cell[:, 0] != edge2cell[:, 1])
        val = np.ones(isInEdge.sum(), dtype=np.bool)
        cell2cell = coo_matrix(
                (val, (edge2cell[isInEdge, 0], edge2cell[isInEdge, 1])),
                shape=(NC,NC), dtype=np.bool)
        cell2cell+= coo_matrix(
                (val, (edge2cell[isInEdge, 1], edge2cell[isInEdge, 0])), 
                shape=(NC,NC), dtype=np.bool)
        return cell2cell.tocsr()

    def edge_to_node(self, sparse=False):
        NN = self.NN
        NE = self.NE

        edge = self.edge
        if sparse == False:
            return edge
        else:
            val = np.ones((NE,), dtype=np.bool)
            edge2node = coo_matrix((val, (edge[:,0], edge[:,1])), shape=(NE, NN), dtype=np.bool)
            edge2node+= coo_matrix((val, (edge[:,1], edge[:,0])), shape=(NE, NN), dtype=np.bool)
            return edge2node.tocsr()

    def edge_to_edge(self):
        edge2node = self.edge_to_node()
        return edge2node*edge2node.tranpose()

    def edge_to_cell(self, sparse=False):
        NE = self.NE
        NC = self.NC
        edge2cell = self.edge2cell
        if sparse == False:
            return edge2cell
        else:
            val = np.ones(NE, dtype=np.bool)
            edge2cell = coo_matrix((val, (range(NE), edge2cell[:,0])), shape=(NE, NC), dtype=np.bool)
            edge2cell+= coo_matrix((val, (range(NE), edge2cell[:,1])), shape=(NE, NC), dtype=np.bool)
            return edge2cell.tocsr()

    def node_to_node(self):
        NN = self.NN
        edge = self.edge
        return node_to_node_in_edge(NN, edge)

    def node_to_node_in_edge(self, NN, edge):
        I = edge.flatten()
        J = edge[:, [1, 0]].flatten()
        val = np.ones(2*edge.shape[0], dtype=np.bool)
        node2node = csr_matrix((val, (I, J)), shape=(NN, NN), dtype=np.bool)
        return node2node

    def node_to_edge(self):
        NN = self.NN
        NE = self.NE

        edge = self.edge

        val = np.ones((NE,), dtype=np.bool)
        node2edge = coo_matrix((val, (edge[:,0], range(NE))), shape=(NE, NN), dtype=np.bool)
        node2edge+= coo_matrix((val, (edge[:,1], range(NE))), shape=(NE, NN), dtype=np.bool)
        return node2edge.tocsr()

    def node_to_cell(self):
        NN = self.NN
        NC = self.NC
        NE = self.NE

        cell = self.cell
        NV = self.number_of_vertices_of_cells()
        I = cell
        J = np.repeat(range(NC), NV)
        val = np.ones(cell.shape[0], dtype=np.bool)
        node2cell = csr_matrix((val, (I, J)), shape=(NN, NC), dtype=np.bool)
        return node2cell

    def boundary_node_flag(self):
        NN = self.NN
        edge = self.edge
        isBdEdge = self.boundary_edge_flag()
        isBdNode = np.zeros(NN, dtype=np.bool)
        isBdNode[edge[isBdEdge,:]] = True
        return isBdNode

    def boundary_edge_flag(self):
        NE = self.NE
        edge2cell = self.edge2cell
        return edge2cell[:,0] == edge2cell[:,1]

    def boundary_edge(self):
        edge = self.edge
        return edge[self.boundary_edge_index()]

    def boundary_cell_flag(self):
        NC = self.NC
        edge2cell = self.edge2cell
        isBdEdge = self.boundary_edge_flag()

        isBdCell = np.zeros(NC, dtype=np.bool)
        isBdCell[edge2cell[isBdEdge,0]] = True
        return isBdCell 

    def boundary_node_index(self):
        isBdNode = self.boundary_node_flag()
        idx, = np.nonzero(isBdNode)
        return idx 

    def boundary_edge_index(self):
        isBdEdge = self.boundary_edge_flag()
        idx, = np.nonzero(isBdEdge)
        return idx

    def boundary_cell_index(self):
        isBdCell = self.boundary_cell_flag()
        idx, = np.nonzero(isBdCell)
        return idx
