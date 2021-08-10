from .application import application

def foamDictionary(filepath: str, entry: str, value: str = None, case: str = None):
    args = [filepath, "-entry", entry]

    if value:
        args.extend(["-set", value])

    application("foamDictionary", *args, case = case, stderr = False)

