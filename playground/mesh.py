
class MeshAlgorithm(object):
    pass

class Netgen3D(MeshAlgorithm):
    def __init__(self, **kwargs):
        self.key = smeshBuilder.NETGEN_3D
    
    def initialize(self, algo):
        self.algo = algo
        self.hypo = self.algo.Parameters()
    
    
    @property
    def minSize(self):
        return self.hypo.GetMinSize()
    
    @minSize.setter
    def minSize(self, value):
        self.hypo.SetMinSize(value)

class MEFISTO(MeshAlgorithm):
    pass 
    
class Mesh(object):
    def __init__(self, geom):
        
        self.smesh = smeshBuilder.New()
        self.geom = geom
        self.mesh = self.smesh.Mesh(self.geom.shape, self.geom.name)
    
    def algo3d(self, algo: MeshAlgorithm, type = "tetrahedron"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm3d = algo()
        self.meshAlgorithm3d.initialize(smeshAlgo(algo = self.meshAlgorithm3d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm3d.hypo)
        
        return self.meshAlgorithm3d
    
    def algo2d(self, algo: MeshAlgorithm, type = "triangle"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm2d = algo()
        self.meshAlgorithm2d.initialize(smeshAlgo(algo = self.meshAlgorithm2d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm2d.hypo)
        
        return self.meshAlgorithm2d
    
    def algo1d(self, algo: MeshAlgorithm, type = "segment"):
        smeshAlgo = self.mesh.__dict__.get(type.capitalize())
        self.meshAlgorithm1d = algo()
        self.meshAlgorithm1d.initialize(smeshAlgo(algo = self.meshAlgorithm1d.key))
        self.mesh.AddHypothesis(self.meshAlgorithm1d.hypo)
        
        return self.meshAlgorithm1d
    
    def createGroups(self, prefix = None):
        prefix = prefix or ""
        
        for group in self.shape.groups:
            name = group.GetName()
            
            if name:
                name = prefix + name
                self.mesh.GroupOnGeom(group, name, SMESH.FACE)
    
    def compute(self):
        """Compute mesh.
        """
        isDone = self.mesh.Compute()
        out = ""
        err = self.mesh.GetComputeErrors()
        returncode = int(not isDone)
        
        return out, err, returncode
    
    def stats(self):
        return {
            "elements":     self.mesh.NbElements(),
            "edges":        self.mesh.NbEdges(),
            "faces":        self.mesh.NbFaces(),
            "volumes":      self.mesh.NbVolumes(),
            "tetrahedrons": self.mesh.NbTetras(),
            "prisms":       self.mesh.NbPrisms(),
            "pyramids":     self.mesh.NbPyramids()
        }
    
    def export(
        filename: str
    ):
        """Export a mesh.
        
        Supported formats: unv.
        
        :param filename:
            Name of the file to store the given mesh in.
        
        :return:
            Output, error messages and returncode
        """
        out, err, returncode = "", "", 0
        ext = os.path.splitext(filename)[1][1: ]
        
        try:
            if ext == "unv":
                self.mesh.ExportUNV(self.mesh, filename)
            
            else:
                raise NotImplementedError(f"{ ext } is not supported")
            
        except NotImplementedError as e:
            err = e
            returncode = 1
        
        except Exception as e:
            err = e.details.text
            returncode = 1
        
        return out, err, returncode
        
