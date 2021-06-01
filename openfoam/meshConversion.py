from .application import application

def ideasUnvToFoam(mesh: str, case: str = None) -> (str, int):
    return application("ideasUnvToFoam", mesh, case = case, stderr = True)

