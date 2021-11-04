import os
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestFaceCentered(unittest.TestCase):
    def setUp(self):
        self.outputPath = os.path.join(os.path.abspath("."), "tests/test_shaping_output")
        os.makedirs(self.outputPath, exist_ok = True)

    def test_faceCentered_lattice(self):
        from anisotropy.shaping import FaceCentered

        fc = FaceCentered([1, 0, 0], alpha = 0.01, filletsEnabled = True)
        fc.build()
        fc.lattice.WriteStep(os.path.join(self.outputPath, "fc_lattice.step"))

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
