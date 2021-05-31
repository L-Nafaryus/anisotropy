from .application import application

def decomposePar(case: str = None):
    application("decomposePar", case = case, stderr = True)

