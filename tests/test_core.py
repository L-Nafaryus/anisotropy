import os
from os import path
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestCore(unittest.TestCase):
    def setUp(self):
        try:
            import netgen
            NETGEN_MODULE = True 

        except ImportError:
            NETGEN_MODULE = False

        if not NETGEN_MODULE:
            self.skipTest("Missing Netgen.")

        else:
            from anisotropy import core 

            self.core = core

            self.outputPath = os.path.join(os.path.abspath("."), "tests/test_core_output")
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
        config.expand()
        config.cases = [ config.cases[0] ]

        runner = self.core.UltimateRunner(config = config, exec_id = True)

        runner.computeShape()
        self.assertTrue(path.isfile(path.join(runner.casepath(), "shape.step")))

        runner.computeMesh()
        self.assertTrue(path.isfile(path.join(runner.casepath(), "mesh.mesh")))

        runner.computeFlow()
        #self.assertTrue(path.isfile(path.join(runner.casepath(), "mesh.mesh")))

        os.chdir(pathOld)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
