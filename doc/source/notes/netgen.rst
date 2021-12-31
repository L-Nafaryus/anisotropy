Salome Netgen parameters
========================

.. ``netgen parameters``
    minSize  
    maxSize  
    growthRate  
    nbSegPerEdge  
    nbSegPerRadius  
    chordalErrorEnabled  
    chordalError  
    secondOrder  
    optimize  
    quadAllowed  
    useSurfaceCurvature  
    fuseEdges  
    checkChartBoundary 
    ``viscous layers parameters``
    thickness  
    numberOfLayers  
    stretchFactor  
    isFacesToIgnore  
    facesToIgnore  
    extrusionMethod 

``Name``
    allows to define the name for the algorithm (NETGEN 2D (or 3D) Parameters by default).
``Max Size``
    maximum linear dimensions for mesh cells.
``Min Size``
    minimum linear dimensions for mesh cells. It is ignored if it is more than ``Max Size``.
``Second Order``
    if this box is checked in, the algorithm will create second order mesh.
``Fineness``
    ranging from Very Coarse to Very Fine allows to set the level of meshing detalization using the three parameters below. You can select Custom to define them manually.
``Growth rate``
    allows to define how much the linear dimensions of two adjacent cells can differ (e.g. 0.3 means 30%).
``Nb. Segs per Edge``
    allows to define the minimum number of mesh segments in which edges will be split. Size of elements computed using this value is trimmed between ``Min Size`` and ``Max Size`` bounds. This parameter is used only if ``Limit Size by Surface Curvature`` is checked.
``Nb Segs per Radius``
    allows to define the size of mesh segments and mesh faces in which curved edges and surfaces will be split. A radius of local curvature divided by this value gives an element size at a given point. Element size computed this way is then trimmed between ``Min Size`` and ``Max Size`` bounds. This parameter is used only if Limit Size by Surface Curvature is checked.
``Chordal Error``
    allows to define the maximum distance between the generated 2D element and the surface. Size of elements computed using this criterion is trimmed between ``Min Size`` and ``Max Size`` bounds.
``Limit Size by Surface Curvature``
    if this box is checked in, then size of mesh segments and mesh faces on curved edges and surfaces is defined using value of ``Nb Segs per Radius`` parameter, and number of segments on straight edges is defined by values of ``Nb. Segs per Edge`` parameter. (``Growth rate`` is also taken into account.) If this box is not checked in, then size of elements is defined by three parameters only: ``Max Size``, ``Min Size`` and ``Growth rate``.
``Allow Quadrangles``
    if this box is checked in, the mesher tries to generate quadrangle 2D mesh. Triangle elements are created where quadrangles are not possible.
``Optimize``
    if this box is checked in, the algorithm will modify initially created mesh in order to improve quality of elements. Optimization process is rather time consuming comparing to creation of initial mesh.
``Fuse Coincident Nodes on Edges and Vertices``
    allows merging mesh nodes on vertices and edges which are geometrically coincident but are topologically different.

``Local sizes``
    allows to define size of elements on and around specified geometrical objects. To define the local size it is necessary to select a geometrical objects in the object browser or in the viewer, and to click a button corresponding to the type of the geometrical objects: **On Vertex**, **On Edge** etc.

``Viscous Layers``
    additional hypothesis can be used together with NETGEN 3D. This hypothesis allows creation of layers of highly stretched prisms near mesh boundary, which is beneficial for high quality viscous computations. The prisms constructed on the quadrangular mesh faces are actually the hexahedrons.

``Quadrangle Preference``
    This additional hypothesis can be used together with Netgen 2D algorithm. It allows Netgen 2D to build quad-dominant meshes.


**NETGEN 2D simple parameters** and **NETGEN 3D simple parameters** allow defining the size of elements for each dimension.

**1D group** allows defining the size of 1D elements in either of two ways:

* ``Number of Segments`` allows specifying number of segments, that will split each edge, with equidistant distribution.
* ``Local Length`` defines length of segments.

**2D group** allows defining the size of 2D elements

* ``Length from edges`` if checked in, size of 2D mesh elements is defined as an average mesh segment length for a given wire, else
* ``Max. Element Area`` specifies expected maximum element area for each 2d element.
* ``Allow Quadrangles`` - allows to generate quadrangle elements wherever possible.

**3D** groups allows defining the size of 3D elements.

* ``Length from faces`` if checked in, the area of sides of volumic elements will be equal to an average area of 2D elements, else
* ``Max. Element Volume`` specifies expected maximum element volume of 3d elements.

.. attention:: 

    NETGEN algorithm does not strictly follow the input parameters. The actual mesh can be more or less dense than required. There are several factors in it:
    
    * NETGEN does not actually use Number of Segments parameter for discretization of edge. This parameter is used only to define the local element size (size at the given point), so local sizes of close edges influence each other.
    * NETGEN additionally restricts the element size according to edge curvature.
    * The local size of segments influences the size of close triangles.
    * The order of elements and their size in the 1D mesh generated by NETGEN differ from those in the 1D mesh generated by Regular_1D algorithm, which results in different 2D and 3D meshes at the same 1D input parameters.

