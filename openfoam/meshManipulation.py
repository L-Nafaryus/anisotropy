
def createPatch(dictfile: str = None, case: str = None):
    args = ["-overwrite"]

    if dictfile:
        args.extend(["-dict", dictfile])

    application("createPatch", *args, case = case, stderr = True)


def transformPoints(scale: tuple, case: str = None):
    scale_ = "{}".format(scale).replace(",", "")

    application("transformPoints", "-scale", scale_, case = case, stderr = True)


def checkMesh(case: str = None):
    application("checkMesh", "-allGeometry", "-allTopology", case = case, stderr = True)

    with open("checkMesh.log", "r") as io:
        warnings = []
        for line in io:
            if re.search("\*\*\*", line):
                warnings.append(line.replace("***", "").strip())

        if warnings:
            logger.warning("checkMesh:\n\t{}".format("\n\t".join(warnings)))


def renumberMesh(case: str = None):
    application("renumberMesh", "-parallel", "-overwrite", useMPI = True, case = case, stderr = True)

