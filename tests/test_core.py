import os, shutil
from os import path
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestCore(unittest.TestCase):
    def setUp(self):
        try:
            import netgen.occ
            _ = netgen.occ.Pnt(0, 0, 0)

        except Exception as e:
            self.skipTest(e)

        else:
            from anisotropy import core

            self.core = core

            self.currentPath = os.path.abspath(".")
            self.outputPath = os.path.join(os.path.dirname(__file__), "test_core_output")
            os.makedirs(self.outputPath, exist_ok = True)

    def test_config(self):
        from copy import deepcopy

        config = self.core.DefaultConfig()
        contentOld = deepcopy(config.content)
        filepath = os.path.join(self.outputPath, "test_config.toml")
        config.dump(filepath)

        config = self.core.Config()
        config.load(filepath)

        self.assertEqual(contentOld, config.content)

    def test_runner(self):
        os.chdir(self.outputPath)

        pathOld = os.path.abspath(".")
        config = self.core.DefaultConfig()
        # TODO: config for solo case
        runner = self.core.UltimateRunner(config = config)
        runner.createRow()

        runner.computeShape()
        self.assertTrue(path.isfile(path.join(runner.casepath(), "shape.step")))

        runner.computeMesh()
        self.assertTrue(path.isfile(path.join(runner.casepath(), "mesh.mesh")))

        runner.computeFlow()
        self.assertTrue(path.isfile(path.join(runner.casepath(), "mesh.mesh")))

        os.chdir(pathOld)

    def tearDown(self):
        os.chdir(self.currentPath)
        shutil.rmtree(self.outputPath)

if __name__ == "__main__":
    unittest.main()
