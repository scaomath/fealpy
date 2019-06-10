import numpy as np

from types import ModuleType
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix, spdiags, eye, tril, triu
from .mesh_tools import unique_row, find_entity, show_mesh_3d, find_node
from ..common import ranges


class Mesh3d():
    def __init__(self):
        pass

    def number_of_nodes(self):
        return self.node.shape[0]

    def number_of_edges(self):
        return self.ds.NE

    def number_of_faces(self):
        return self.ds.NF

    def number_of_cells(self):
        return self.ds.NC

    def number_of_nodes_of_cells(self):
        return self.ds.number_of_nodes_of_cells()

    def number_of_edges_of_cells(self):
        return self.ds.number_of_edges_of_cells()

    def number_of_faces_of_cells(self):
        return self.ds.number_of_faces_of_cells()

    def geo_dimension(self):
        return self.node.shape[1]

    def top_dimension(self):
        return 3

    def boundary_face(self, threshold=None):
        face = self.entity('face')
        isBdFace = self.ds.boundary_face_flag()
        if threshold is None:
            return face[isBdFace]
        else:
            bc = self.entity_barycenter('cell')
            isKeepCell = threshold(bc)
            face2cell = self.ds.face_to_cell()
            isInterfaceFace = np.sum(
                    isKeepCell[face2cell[:, 0:2]],
                    axis=-1) == 1
            isBdFace = (np.sum(
                    isKeepCell[face2cell[:, 0:2]],
                    axis=-1) == 2) & isBdFace
            return face[isBdFace | isInterfaceFace]

    def to_vtk(self, vtk, vns, filename=None):
        nodes = vtk.vtkPoints()
        nodes.SetData(vns.numpy_to_vtk(node))

        NC = len(cell)
        cells = vtk.vtkCellArray()
        cells.SetCells(NC, vns.numpy_to_vtkIdTypeArray(cell))

        celltype = self.vtk_cell_type()

        vmesh = vtk.vtkUnstructuredGrid()
        vmesh.SetPoints(points)
        vmesh.SetCells(celltype, cells)

        if len(self.celldata) > 0:
            cdata = vmesh.GetCellData()
            for key, value in self.celldata.items():
                data = vns.numpy_to_vtk(value)
                data.SetName(key)
                cdata.AddArray(data)

        if len(self.nodedata) > 0:
            ndata = vmesh.GetPointData()
            for key, value in self.nodedata.items():
                data = vns.numpy_to_vtk(value)
                data.SetName(key)
                ndata.AddArray(data)

        if len(self.edgedata) > 0:
            ndata = vmesh.GetPointData()
            for key, value in self.edgedata.items():
                data = vns.numpy_to_vtk(value)
                data.SetName(key)
                ndata.AddArray(data)

        if len(self.facedata) > 0:
            ndata = vmesh.GetPointData()
            for key, value in self.facedata.items():
                data = vns.numpy_to_vtk(value)
                data.SetName(key)
                ndata.AddArray(data)
        return vmesh

    def entity(self, etype='cell'):
        if etype in ['cell', 3]:
            return self.ds.cell
        elif etype in ['face', 2]:
            return self.ds.face
        elif etype in ['edge', 1]:
            return self.ds.edge
        elif etype in ['node', 0]:
            return self.node
        else:
            raise ValueError("`etype` is wrong!")

    def entity_measure(self, etype=3):
        if etype in ['cell', 3]:
            return self.cell_volume()
        elif etype in ['face', 2]:
            return self.face_area()
        elif etype in ['edge', 1]:
            return self.edge_length()
        elif etype in ['node', 0]:
            NN = self.number_of_nodes()
            return np.zeros(NN, dtype=self.ftype)
        else:
            raise ValueError("`entitytype` is wrong!")

    def entity_barycenter(self, etype='cell'):
        node = self.node
        if etype in ['cell', 3]:
            cell = self.ds.cell
            bc = np.sum(node[cell, :], axis=1).reshape(-1, 3)/cell.shape[1]
        elif etype in ['face', 2]:
            face = self.ds.face
            bc = np.sum(node[face, :], axis=1).reshape(-1, 3)/face.shape[1]
        elif etype in ['edge', 1]:
            edge = self.ds.edge
            bc = np.sum(node[edge, :], axis=1).reshape(-1, 3)/edge.shape[1]
        elif etype in ['node', 0]:
            bc = node
        else:
            raise ValueError("`etype` is wrong!")

        return bc

    def edge_unit_tagent(self):
        edge = self.ds.edge
        node = self.node
        v = node[edge[:, 1], :] - node[edge[:, 0], :]
        length = np.sqrt(np.square(v).sum(axis=1))
        return v/length.reshape(-1, 1)

    def add_plot(
            self, plot,
            nodecolor='k', edgecolor='k', facecolor='w', cellcolor='w',
            aspect='equal',
            linewidths=0.5, markersize=20,
            showaxis=False, alpha=0.8, shownode=False, showedge=False, threshold=None):

        if isinstance(plot, ModuleType):
            fig = plot.figure()
            fig.set_facecolor('white')
            axes = fig.gca()
        else:
            axes = plot

        return show_mesh_3d(
                axes, self,
                nodecolor=nodecolor, edgecolor=edgecolor,
                facecolor=facecolor, cellcolor=cellcolor,
                aspect=aspect,
                linewidths=linewidths, markersize=markersize,
                showaxis=showaxis, alpha=alpha, shownode=shownode,
                showedge=showedge,
                threshold=threshold)

    def find_node(
            self, axes,
            node=None,
            index=None, showindex=False,
            color='r', markersize=40,
            fontsize=24, fontcolor='k'):

        if node is None:
            node = self.node
        find_node(
                axes, node,
                index=index, showindex=showindex,
                color=color, markersize=markersize,
                fontsize=fontsize, fontcolor=fontcolor)

    def find_edge(
            self, axes,
            index=None, showindex=False,
            color='g', markersize=80,
            fontsize=24, fontcolor='k'):

        find_entity(
                axes, self, entity='edge',
                index=index, showindex=showindex,
                color=color, markersize=markersize,
                fontsize=fontsize, fontcolor=fontcolor)

    def find_face(
            self, axes,
            index=None, showindex=False,
            color='k', markersize=120,
            fontsize=24, fontcolor='k'):
        find_entity(
                axes, self,  entity='face',
                index=index, showindex=showindex,
                color=color, markersize=markersize,
                fontsize=fontsize, fontcolor=fontcolor)

    def find_cell(
            self, axes,
            index=None, showindex=False,
            color='r', markersize=20,
            fontsize=24, fontcolor='k'):
        find_entity(
                axes, self, entity='cell',
                index=index, showindex=showindex,
                color=color, markersize=markersize,
                fontsize=fontsize, fontcolor=fontcolor)

    def print(self):
        print('cell:\n', self.ds.cell)
        print('face:\n', self.ds.face)
        print('face2cell:\n', self.ds.face2cell)


class Mesh3dDataStructure():
    def __init__(self, NN, cell):
        self.itype = cell.dtype
        self.NN = NN
        self.NC = cell.shape[0]
        self.cell = cell
        self.construct()

    def reinit(self, NN, cell):
        self.NN = NN
        self.NC = cell.shape[0]
        self.cell = cell
        self.construct()

    def clear(self):
        self.face = None
        self.face2cell = None
        self.edge = None
        self.cell2edge = None

    def number_of_nodes_of_cells(self):
        return self.V

    def number_of_edges_of_cells(self):
        return self.E

    def number_of_faces_of_cells(self):
        return self.F

    def total_edge(self):
        cell = self.cell
        localEdge = self.localEdge
        totalEdge = cell[:, localEdge].reshape(-1, localEdge.shape[1])
        return totalEdge

    def total_face(self):
        cell = self.cell
        localFace = self.localFace
        totalFace = cell[:, localFace].reshape(-1, localFace.shape[1])
        return totalFace

    def construct(self):
        NC = self.NC

        totalFace = self.total_face()

        _, i0, j = np.unique(
                np.sort(totalFace, axis=1),
                return_index=True,
                return_inverse=True,
                axis=0)

        self.face = totalFace[i0]

        NF = i0.shape[0]
        self.NF = NF

        self.face2cell = np.zeros((NF, 4), dtype=self.itype)

        i1 = np.zeros(NF, dtype=self.itype)
        F = self.F
        i1[j] = np.arange(F*NC)

        self.face2cell[:, 0] = i0 // F
        self.face2cell[:, 1] = i1 // F
        self.face2cell[:, 2] = i0 % F
        self.face2cell[:, 3] = i1 % F

        totalEdge = self.total_edge()
        self.edge, i2, j = np.unique(
                np.sort(totalEdge, axis=1),
                return_index=True,
                return_inverse=True,
                axis=0)
        E = self.E
        self.cell2edge = np.reshape(j, (NC, E))
        self.NE = self.edge.shape[0]

    def cell_to_node(self):
        """
        """
        NN = self.NN
        NC = self.NC
        V = self.V

        cell = self.cell
        cell2node = csr_matrix(
                (
                    np.ones(self.V*NC, dtype=np.bool),
                    (
                        np.repeat(range(NC), V),
                        cell.flat
                    )
                ), shape=(NC, NN), dtype=np.bool)
        return cell2node

    def cell_to_edge(self, sparse=False):
        """ The neighbor information of cell to edge
        """
        if sparse is False:
            return self.cell2edge
        else:
            NC = self.NC
            NE = self.NE
            cell2edge = coo_matrix((NC, NE), dtype=np.bool)
            E = self.E
            cell2edge = csr_matrix(
                    (
                        np.ones(E*NC, dtype=np.bool),
                        (
                            np.repeat(range(NC), E),
                            self.cell2edge.flat
                        )
                    ), shape=(NC, NE), dtype=np.bool)
            return cell2edge

    def cell_to_edge_sign(self, cell):
        NC = self.NC
        E = self.E
        cell2edgeSign = np.zeros((NC, E), dtype=np.bool)
        localEdge = self.localEdge
        for i, (j, k) in zip(range(E), localEdge):
            cell2edgeSign[:, i] = cell[:, j] < cell[:, k]
        return cell2edgeSign

    def cell_to_face(self, sparse=False):
        NC = self.NC
        NF = self.NF
        face2cell = self.face2cell
        if sparse is False:
            F = self.F
            cell2face = np.zeros((NC, F), dtype=self.itype)
            cell2face[face2cell[:, 0], face2cell[:, 2]] = range(NF)
            cell2face[face2cell[:, 1], face2cell[:, 3]] = range(NF)
            return cell2face
        else:
            cell2face = csr_matrix(
                    (
                        np.ones((2*NF, ), dtype=np.bool),
                        (
                            face2cell[:, [0, 1]].flat,
                            np.repeat(range(NF), 2)
                        )
                    ), shape=(NC, NF), dtype=np.bool)
            return cell2face

    def cell_to_cell(
            self, return_sparse=False,
            return_boundary=True, return_array=False):
        """ Get the adjacency information of cells
        """
        if return_array:
            return_sparse = False
            return_boundary = False

        NC = self.NC
        NF = self.NF
        face2cell = self.face2cell
        if (return_sparse is False) & (return_array is False):
            F = self.F
            cell2cell = np.zeros((NC, F), dtype=self.itype)
            cell2cell[face2cell[:, 0], face2cell[:, 2]] = face2cell[:, 1]
            cell2cell[face2cell[:, 1], face2cell[:, 3]] = face2cell[:, 0]
            return cell2cell

        val = np.ones((NF,), dtype=np.bool)
        if return_boundary:
            cell2cell = coo_matrix(
                    (val, (face2cell[:, 0], face2cell[:, 1])),
                    shape=(NC, NC), dtype=np.bool)
            cell2cell += coo_matrix(
                    (val, (face2cell[:, 1], face2cell[:, 0])),
                    shape=(NC, NC), dtype=np.bool)
            return cell2cell.tocsr()
        else:
            isInFace = (face2cell[:, 0] != face2cell[:, 1])
            cell2cell = coo_matrix(
                    (
                        val[isInFace],
                        (face2cell[isInFace, 0], face2cell[isInFace, 1])
                    ),
                    shape=(NC, NC), dtype=np.bool)
            cell2cell += coo_matrix(
                    (
                        val[isInFace],
                        (face2cell[isInFace, 1], face2cell[isInFace, 0])
                    ), shape=(NC, NC), dtype=np.bool)
            cell2cell = cell2cell.tocsr()
            if return_array is False:
                return cell2cell
            else:
                nn = cell2cell.sum(axis=1).reshape(-1)
                _, adj = cell2cell.nonzero()
                adjLocation = np.zeros(NC+1, dtype=np.int32)
                adjLocation[1:] = np.cumsum(nn)
                return adj.astype(np.int32), adjLocation

    def face_to_node(self, return_sparse=False):

        face = self.face
        FE = self.localFace.shape[1]
        if return_sparse is False:
            return face
        else:
            NN = self.NN
            NF = self.NF
            face2node = csr_matrix(
                    (
                        np.ones(FE*NF, dtype=np.bool),
                        (
                            np.repeat(range(NF), FE),
                            face.flat
                        )
                    ), shape=(NF, NN), dtype=np.bool)
            return face2node

    def face_to_edge(self, return_sparse=False):
        cell2edge = self.cell2edge
        face2cell = self.face2cell
        localFace2edge = self.localFace2edge
        FE = localFace2edge.shape[1]
        face2edge = cell2edge[
                face2cell[:, [0]],
                localFace2edge[face2cell[:, 2]]
                ]
        if return_sparse is False:
            return face2edge
        else:
            NF = self.NF
            NE = self.NE
            f2e = csr_matrix(
                    (
                        np.ones(FE*NF, dtype=np.bool)
                        (
                            np.repeat(range(NF), FE),
                            face2edge.flat
                        )
                    ), shape=(NF, NE), dtype=np.bool)
            return f2e

    def face_to_face(self):
        face2edge = self.face_to_edge()
        return face2edge*face2edge.transpose()

    def face_to_cell(self, return_sparse=False):
        if return_sparse is False:
            return self.face2cell
        else:
            NC = self.NC
            NF = self.NF
            face2cell = csr_matrix(
                    (
                        np.ones(2*NF, dtype=np.bool),
                        (
                            np.repeat(range(NF), 2),
                            self.face2cell[:, [0, 1]].flat
                        )
                    ), shape=(NF, NC), dtype=np.bool)
            return face2cell

    def edge_to_node(self, return_sparse=False):
        NN = self.NN
        NE = self.NE
        edge = self.edge
        if return_sparse is False:
            return edge
        else:
            edge = self.edge
            edge2node = csr_matrix(
                    (
                        np.ones(2*NE, dtype=np.bool),
                        (
                            np.repeat(range(NE), 2),
                            edge.flat
                        )
                    ), shape=(NE, NN), dtype=np.bool)
            return edge2node

    def edge_to_edge(self):
        edge2node = self.edge_to_node()
        return edge2node*edge2node.transpose()

    def edge_to_face(self):
        NF = self.NF
        NE = self.NE
        face2edge = self.face_to_edge()
        FE = face2edge.shape[1]
        edge2face = csr_matrix(
                (
                    np.ones(FE*NF, dtype=np.bool),
                    (
                        face2edge.flat,
                        np.repeat(range(NF), FE)
                    )
                ), shape=(NE, NF), dtype=np.bool)
        return edge2face

    def edge_to_cell(self, localidx=False):
        NC = self.NC
        NE = self.NE
        cell2edge = self.cell2edge
        E = self.E
        edge2cell = csr_matrix(
                (
                    np.ones(E*NC, dtype=np.bool),
                    (
                        cell2edge.flat,
                        np.repeat(range(NC), E)
                    )
                ), shape=(NE, NC), dtype=np.bool)
        return edge2cell

    def node_to_node(self):
        """ The neighbor information of nodes
        """
        NN = self.NN
        NE = self.NE
        edge = self.edge
        node2node = csr_matrix(
                (
                    np.ones((2*NE,), dtype=np.bool),
                    (
                        edge.flat,
                        edge[:, [1, 0]].flat
                    )
                ), shape=(NN, NN), dtype=np.bool)
        return node2node

    def node_to_edge(self):
        NN = self.NN
        NE = self.NE
        edge = self.edge
        node2edge = csr_matrix(
                (
                    np.ones(2*NE, dtype=np.bool),
                    (
                        edge.flat,
                        np.repeat(range(NE), 2)
                    )
                ), shape=(NE, NN), dtype=np.bool)
        return node2edge

    def node_to_face(self):
        NN = self.NN
        NF = self.NF

        face = self.face
        FV = face.shape[1]
        node2face = csr_matrix(
                (
                    np.ones(FV*NF, dtype=np.bool)
                    (
                        face.flat,
                        np.repeat(range(NF), FV)
                    )
                ), shape=(NF, NN), dtype=np.bool)
        return node2face

    def node_to_cell(self, return_local_index=False):
        """
        """
        NN = self.NN
        NC = self.NC
        V = self.V

        cell = self.cell

        if return_local_index is True:
            node2cell = csr_matrix(
                    (
                        ranges(V*np.ones(NC, dtype=self.itype), start=1),
                        (
                            cell.flatten(),
                            np.repeat(range(NC), V)
                        )
                    ), shape=(NN, NC), dtype=self.itype)
        else:
            node2cell = csr_matrix(
                    (
                        np.ones(V*NC, dtype=np.bool),
                        (
                            cell.flatten(),
                            np.repeat(range(NC), V)
                        )
                    ), shape=(NN, NC), dtype=np.bool)
        return node2cell

    def boundary_node_flag(self):
        NN = self.NN
        face = self.face
        isBdFace = self.boundary_face_flag()
        isBdPoint = np.zeros((NN,), dtype=np.bool)
        isBdPoint[face[isBdFace, :]] = True
        return isBdPoint

    def boundary_edge_flag(self):
        NE = self.NE
        face2edge = self.face_to_edge()
        isBdFace = self.boundary_face_flag()
        isBdEdge = np.zeros((NE,), dtype=np.bool)
        isBdEdge[face2edge[isBdFace, :]] = True
        return isBdEdge

    def boundary_face_flag(self):
        face2cell = self.face_to_cell()
        return face2cell[:, 0] == face2cell[:, 1]

    def boundary_cell_flag(self):
        NC = self.NC
        face2cell = self.face_to_cell()
        isBdFace = self.boundary_face_flag()
        isBdCell = np.zeros((NC,), dtype=np.bool)
        isBdCell[face2cell[isBdFace, 0]] = True
        return isBdCell

    def boundary_node_index(self):
        isBdNode = self.boundary_node_flag()
        idx, = np.nonzero(isBdNode)
        return idx

    def boundary_edge_index(self):
        isBdEdge = self.boundary_edge_flag()
        idx, = np.nonzero(isBdEdge)
        return idx

    def boundary_face_index(self):
        isBdFace = self.boundary_face_flag()
        idx, = np.nonzero(isBdFace)
        return idx

    def boundary_cell_index(self):
        isBdCell = self.boundary_cell_flag()
        idx, = np.nonzero(isBdCell)
        return idx
