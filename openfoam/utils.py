import os
import shutil

def foamVersion() -> str:
    return "OpenFOAM-{}".format(os.environ["WM_PROJECT_VERSION"])


def foamClean(case: str = None):
    rmDirs = ["0", "constant", "system", "postProcessing", "logs"]
    rmDirs.extend([ "processor{}".format(n) for n in range(os.cpu_count()) ])
    path = case if case else ""

    for d in rmDirs:
        if os.path.exists(os.path.join(path, d)):
            shutil.rmtree(os.path.join(path, d))


def uniform(value) -> str:
    if type(value) == list or type(value) == tuple:
        return f"uniform ({ value[0] } { value[1] } { value[2] })"

    elif type(value) == int or type(value) == float:
        return f"uniform { value }"

    else:
        return ""
