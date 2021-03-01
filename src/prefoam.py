import os, shutil

src = os.getcwd()
build = os.path.join(src, "../build")

if not os.path.exists(build):
    os.makedirs(build)

foamCase = [ "0", "constant", "system" ]

for d in foamCase:
    shutil.copytree("{}/foam/{}".format(src, d), 
                    "{}/simple-cubic/0.1/{}".format(build, d))
