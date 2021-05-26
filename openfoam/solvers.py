
def potentialFoam(case: str = None):
    application("potentialFoam", "-parallel", useMPI = True, case = case, stderr = True)


def simpleFoam(case: str = None):
    _, returncode = application("simpleFoam", "-parallel", useMPI = True, case = case, stderr = True)

    with open("simpleFoam.log", "r") as io:
        for line in io:
            if re.search("solution converged", line):
                logger.info("simpleFoam:\n\t{}".format(line.strip()))

    return returncode

