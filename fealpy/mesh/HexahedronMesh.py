import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix, spdiags, eye, tril, triu
from scipy.sparse import triu, tril, find, hstack
from .mesh_tools import unique_row
from .Mesh3d import Mesh3d, Mesh3dDataStructure 

class HexahedronMeshDataStructure(Mesh3dDataStructure):

    # The following local data structure should be class properties
    localEdge = np.array([
        (0, 1), (1, 2), (2, 3), (0, 3),
        (0, 4), (1, 5), (2, 6), (3, 7),
        (4, 5), (5, 6), (6, 7), (4, 7)])
    localFace = np.array([
        (0, 3, 2, 1), (4, 5, 6, 7), # bottom and top faces
        (0, 4, 7, 3), (1, 2, 6, 5), # left and right faces  
        (0, 1, 5, 4), (2, 3, 7, 6)])# front and back faces
    localFace2edge = np.array([
        (3,  2, 1, 0), (8, 9, 10, 11),
        (4, 11, 7, 3), (1, 6,  9,  5),
        (0,  5, 8, 4), (2, 7, 10,  6)])
    localEdge2face = np.array([
        [4, 0], [3, 0], [5, 0], [0, 2], 
        [2, 4], [4, 3], [3, 5], [5, 2], 
        [1, 4], [1, 3], [1, 5], [2, 1]])
    NVC = 8
    NEC = 12
    NFC = 6
    NVF = 4
    NEF = 4

    def __init__(self, NN, cell):
        super().__init__(NN, cell)

        
    def face_to_edge_sign(self):
        face2edge = self.face_to_edge()
        edge = self.edge
        face = self.face
        NF = self.NF
        face2edgeSign = np.zeros((NF, 4), dtype=np.bool)
        for i in range(4):
            face2edgeSign[:, i] = (face[:, i] == edge[face2edge[:, i], 0])
        return face2edgeSign

class HexahedronMesh(Mesh3d):
    """
    @brief 非结构六面体网格数据结构对象
    """
    def __init__(self, node, cell):
        self.node = node
        NN = node.shape[0]
        self.ds = HexahedronMeshDataStructure(NN, cell)

        self.meshtype = 'hex'

        self.itype = cell.dtype
        self.ftype = node.dtype

        self.celldata = {}
        self.nodedata = {}
        self.edgedata = {}
        self.facedata = {} 
        self.meshdata = {}

    def integrator(self, q, etype='cell'):
        """
        @brief 获取不同维度网格实体上的积分公式 
        """
        qf = GaussLegendreQuadrature(q)
        if etype in {'cell', 3}:
            return TensorProductQuadrature((qf, qf, qf)) 
        elif etype in {'face', 2}:
            return TensorProductQuadrature((qf, qf)) 
        elif etype in {'edge', 1}:
            return qf 

    def bc_to_point(self, bc, index=np.s_[:]):
        """
        @brief 把重心坐标积分点变换为网格实体上的笛卡尔坐标点
        """
        node = self.entity('node')
        if isinstance(bc, tuple):
            if len(bc) == 2:
                face = self.entity('face')[index]
                bc0 = bc[0] # (NQ0, 2)
                bc1 = bc[1] # (NQ1, 2)
                bc = np.einsum('im, jn->ijmn', bc0, bc1).reshape(-1, 4) # (NQ0, NQ1, 2, 2)
                p = np.einsum('...j, cjk->...ck', bc, node[face[:, [0, 3, 1, 2]]]) # (NQ, NC, 2)
            elif len(bc) == 3:
                cell = self.entity('cell')[index]
                bc0 = bc[0] # (NQ0, 2)
                bc1 = bc[1] # (NQ1, 2)
                bc2 = bc[2] # (NQ1, 2)
                bc = np.einsum('im, jn, kl->ijkmnl', bc0, bc1, bc2).reshape(-1, 8) # (NQ0, NQ1, NQ2, 2, 2, 2)
                p = np.einsum('...j, cjk->...ck', bc, node[cell[:, [0, 4, 3, 7, 1, 5, 2, 6]]]) # (NQ, NC, 3)
        else:
            edge = self.entity('edge')[index]
            p = np.einsum('...j, ejk->...ek', bc, node[edge]) # (NQ, NE, 3)
        return p 

    def edge_bc_to_point(self, bc, index=np.s_[:]):
        """
        @brief 把重心坐标积分点变换为网格边上的笛卡尔坐标点
        """
        node = self.node
        entity = self.entity('edge')[index]
        p = np.einsum('...j, ijk->...ik', bc, node[entity])
        return p

    def face_bc_to_point(self, bc, index=np.s_[:]):
        """
        @brief 把重心坐标积分点变换为网格面上的笛卡尔坐标点
        """
        assert len(bc) == 2
        node = self.entity('node')
        face = self.entity('face')[index]
        bc0 = bc[0] # (NQ0, 2)
        bc1 = bc[1] # (NQ1, 2)
        bc = np.einsum('im, jn->ijmn', bc0, bc1).reshape(-1, 4) # (NQ0, NQ1, 2, 2)
        p = np.einsum('...j, cjk->...ck', bc, node[face[:, [0, 3, 1, 2]]]) # (NQ, NC, 2)
        return p

    def cell_bc_to_point(self, bc, index=np.s_[:]):
        """
        @brief 把重心坐标积分点变换为网格单元上的笛卡尔坐标点
        """
        assert len(bc) == 3
        node = self.entity('node')
        cell = self.entity('cell')[index]
        bc0 = bc[0] # (NQ0, 2)
        bc1 = bc[1] # (NQ1, 2)
        bc2 = bc[2] # (NQ2, 2)
        bc = np.einsum('im, jn, kl->ijkmnl', bc0, bc1, bc2).reshape(-1, 8) # (NQ0, NQ1, NQ2, 2, 2, 2)
        p = np.einsum('...j, cjk->...ck', bc, node[cell[:, [0, 4, 3, 7, 1, 5, 2, 6]]]) # (NQ, NC, 3)
        return p

    def uniform_refine(self, n=1):
        """
        @brief 一致加密六面体网格 
        """
        for i in range(n):
            pass

    def number_of_local_ipoints(p, celltype):
        if celltype=='edge':
            return p+1
        elif celltype=='face':
            return (p+1)**2
        elif celltype=='cell':
            return (p+1)**3

    def number_of_global_ipoints(self, p):
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        NF = self.number_of_faces()
        NC = self.number_of_cells()
        return NN+NE*(p-1)+NF*(p-1)**2+NC*(p-1)**3

    def interpolation_points(self, p):
        node = self.entity('node')
        cell = self.entity('cell')
        NC = self.number_of_cells()

        c2ip = self.cell_to_ipoint(p)
        gp = self.number_of_global_ipoints(p)
        ipoint = np.zeros([gp, 3], dtype=np.float_)

        p04 = np.linspace(node[cell[:, 0]], node[cell[:, 4]], p+1, endpoint=True).swapaxes(0, 1)
        p37 = np.linspace(node[cell[:, 3]], node[cell[:, 7]], p+1, endpoint=True).swapaxes(0, 1)
        p15 = np.linspace(node[cell[:, 1]], node[cell[:, 5]], p+1, endpoint=True).swapaxes(0, 1)
        p26 = np.linspace(node[cell[:, 2]], node[cell[:, 6]], p+1, endpoint=True).swapaxes(0, 1)

        p0 = np.linspace(p04, p37, p+1, endpoint=True).swapaxes(0, 1).reshape(NC, -1, 3)
        p1 = np.linspace(p15, p26, p+1, endpoint=True).swapaxes(0, 1).reshape(NC, -1, 3)
        ipoint[c2ip] = np.linspace(p0, p1, p+1, endpoint=True).swapaxes(0, 1).reshape(NC, -1, 3)
        return ipoint

    def edge_to_ipoint(self, p):
        """!
        @brief 生成每条边上的插值点全局编号
        """
        edge = self.entity('edge')
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        e2ip = np.zeros([NE, p+1], dtype=np.int_)
        e2ip[:, 0] = edge[:, 0]
        e2ip[:, -1] = edge[:, -1]
        e2ip[:, 1:-1] = np.arange(NN, NN+NE*(p-1)).reshape(-1, p-1)
        return e2ip

    def face_to_ipoint(self, p):
        """!
        @brief 生成每个面上的插值点全局编号
        """
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        NF = self.number_of_faces()
        edge = self.entity('edge')
        face = self.entity('face')
        face2edge = self.ds.face_to_edge()
        edge2ipoint = self.edge_to_ipoint(p)

        multiIndex = np.zeros([(p+1)**2, 2], dtype=np.int_)
        multiIndex[:, 0] = np.repeat(np.arange(p+1), p+1)
        multiIndex[:, 1] = np.tile(np.arange(p+1), p+1)

        dofidx = np.zeros((4, p+1), dtype=np.int_) #四条边上自由度的局部编号
        dofidx[0], = np.where(multiIndex[:, 1]==0)
        dofidx[1], = np.where(multiIndex[:, 0]==p)
        dofidx[2], = np.where(multiIndex[:, 1]==p)
        dofidx[3], = np.where(multiIndex[:, 0]==0)

        face2ipoint = np.zeros([NF, (p+1)**2], dtype=np.int_)
        localEdge = np.array([[0, 1], [1, 2], [3, 2], [0, 3]], dtype=np.int_)
        for i in range(4): #边上的自由度
            ge = face2edge[:, i]
            idx = np.where(face[:, localEdge[i, 0]] != edge[ge, 0])[0]

            face2ipoint[:, dofidx[i]] = edge2ipoint[ge]
            face2ipoint[idx[:, None], dofidx[i]] = edge2ipoint[ge[idx], ::-1]

        indof = np.all(multiIndex>0, axis=-1)&np.all(multiIndex<p, axis=-1)
        face2ipoint[:, indof] = np.arange(NN+NE*(p-1),
                NN+NE*(p-1)+NF*(p-1)**2).reshape(NF, -1)
        return face2ipoint

    def cell_to_ipoint(self, p):
        """!
        @brief 生成每个单元上的插值点全局编号
        """
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        NF = self.number_of_faces()
        NC = self.number_of_cells()

        edge = self.entity('edge')
        face = self.entity('face')
        cell = self.entity('cell')

        cell2face = self.ds.cell_to_face()
        face2edge = self.ds.face_to_edge()
        cell2edge = self.ds.cell_to_edge()

        face2ipoint = self.face_to_ipoint(p)

        multiIndex = np.zeros([(p+1)**3, 3], dtype=np.int_)
        multiIndex[:, 0] = np.repeat(np.arange(p+1), (p+1)**2)
        multiIndex[:, 1] = np.tile(np.repeat(np.arange(p+1), p+1), (p+1))
        multiIndex[:, 2] = np.tile(np.arange(p+1), (p+1)**2)

        dofidx = np.zeros((6, (p+1)**2), dtype=np.int_) #四条边上自由度的局部编号
        dofidx[0], = np.where(multiIndex[:, 2]==0)
        dofidx[1], = np.where(multiIndex[:, 2]==p)
        dofidx[2], = np.where(multiIndex[:, 0]==0)
        dofidx[3], = np.where(multiIndex[:, 0]==p)
        dofidx[4], = np.where(multiIndex[:, 1]==0)
        dofidx[5], = np.where(multiIndex[:, 1]==p)

        cell2ipoint = np.zeros([NC, (p+1)**3], dtype=np.int_)
        lf2e = np.array([[0, 1, 2, 3], [8, 9, 10, 11], 
                         [3, 7, 11, 4], [1, 6, 9, 5],
                         [0, 5, 8, 4], [2, 6, 10, 7]], dtype=np.int_)

        multiIndex2d = multiIndex[:(p+1)**2, 1:]
        multiIndex2d = np.c_[multiIndex2d, p-multiIndex2d]

        lf2e = lf2e[:, [3, 0, 1, 2]]
        face2edge = face2edge[:, [3, 0, 1, 2]]
        for i in range(6): #面上的自由度
            gfe = face2edge[cell2face[:, i]]
            lfe = cell2edge[:, lf2e[i]]
            idx0 = np.argsort(gfe, axis=-1)
            idx1 = np.argsort(lfe, axis=-1)
            idx1 = np.argsort(idx1, axis=-1)
            idx0 = idx0[np.arange(NC)[:, None], idx1] #(NC, 4)
            idx = multiIndex2d[:, idx0].swapaxes(0, 1) #(NC, NQ, 4)

            idx = idx[..., 0]*(p+1)+idx[..., 1]
            cell2ipoint[:, dofidx[i]] = face2ipoint[cell2face[:, i, None], idx]

        indof = np.all(multiIndex>0, axis=-1)&np.all(multiIndex<p, axis=-1)
        cell2ipoint[:, indof] = np.arange(NN+NE*(p-1)+NF*(p-1)**2, 
                NN+NE*(p-1)+NF*(p-1)**2+NC*(p-1)**3).reshape(NC, -1)
        return cell2ipoint

    def cell_to_ipoint0(self, p):
        """!
        @brief 生成每个单元上的插值点全局编号
        """
        NN = self.number_of_nodes()
        NE = self.number_of_edges()
        NF = self.number_of_faces()
        NC = self.number_of_cells()
        edge = self.entity('edge')
        face = self.entity('face')
        cell = self.entity('cell')
        cell2face = self.ds.cell_to_face()
        face2ipoint = self.face_to_ipoint(p)

        multiIndex = np.zeros([(p+1)**3, 3], dtype=np.int_)
        multiIndex[:, 0] = np.repeat(np.arange(p+1), (p+1)**2)
        multiIndex[:, 1] = np.tile(np.repeat(np.arange(p+1), p+1), (p+1))
        multiIndex[:, 2] = np.tile(np.arange(p+1), (p+1)**2)

        dofidx = np.zeros((6, (p+1)**2), dtype=np.int_) #四条边上自由度的局部编号
        dofidx[0], = np.where(multiIndex[:, 2]==0)
        dofidx[1], = np.where(multiIndex[:, 2]==p)
        dofidx[2], = np.where(multiIndex[:, 1]==0)
        dofidx[3], = np.where(multiIndex[:, 1]==p)
        dofidx[4], = np.where(multiIndex[:, 0]==0)
        dofidx[5], = np.where(multiIndex[:, 0]==p)

        cell2ipoint = np.zeros([NC, (p+1)**3], dtype=np.int_)
        localFace = np.array([[0, 1, 2, 3], [4, 5, 6, 7], 
                              [0, 3, 7, 4], [1, 2, 6, 5], 
                              [0, 1, 5, 4], [3, 2, 6, 7]],dtype=np.int_) 

        multiIndex0 = np.zeros(((p+1)**2, 4, 2), dtype=np.int_)
        multiIndex0[:, 2, 0] = np.repeat(np.arange(p+1), p+1)
        multiIndex0[:, 2, 1] = np.tile(np.arange(p+1), p+1)
        multiIndex0[:, 0] = p - multiIndex0[:, 2]
        multiIndex0[:, 1, 0] = multiIndex0[:, 2, 0]
        multiIndex0[:, 1, 1] = p - multiIndex0[:, 2, 1]
        multiIndex0[:, 3, 0] = p - multiIndex0[:, 2, 0]
        multiIndex0[:, 3, 1] =  multiIndex0[:, 2, 1]

        for i in range(6): #面上的自由度
            gf = face[cell2face[:, i]]
            lf = cell[:, localFace[i]]
            idx0 = np.argsort(gf, axis=-1)
            idx1 = np.argsort(lf, axis=-1)
            idx1 = np.argsort(idx1, axis=-1)
            idx0 = idx0[np.arange(NC)[:, None], idx1] #(NC, 4)
            idx = multiIndex0[:, idx0].swapaxes(0, 1) #(NC, NQ, 4, 2)
            #print('idx', idx)

            idx = idx[..., 2, 0]*(p+1)+idx[..., 2, 1]
            #print('idx0', idx0)
            #print("gf = ", gf)
            #print('lf = ', lf)
            #print('i = ', i)

            cell2ipoint[:, dofidx[i]] = face2ipoint[cell2face[:, i, None], idx]

        indof = np.all(multiIndex>0, axis=-1)&np.all(multiIndex<p, axis=-1)
        cell2ipoint[:, indof] = np.arange(NN+NE*(p-1)+NF*(p-1)**2, 
                NN+NE*(p-1)+NF*(p-1)**2+NC*(p-1)**3).reshape(NC, -1)
        return cell2ipoint

    def cell_volume(self):
        pass

    def face_area(self):
        pass

    def jacobi_at_corner(self):
        pass

    def cell_quality(self):
        pass

    def print(self):
        print("Point:\n", self.node)
        print("Cell:\n", self.ds.cell)
        print("Edge:\n", self.ds.edge)
        print("Face:\n", self.ds.face)
        print("Face2cell:\n", self.ds.face2cell)


