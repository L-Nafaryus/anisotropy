import os
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestShaping(unittest.TestCase):
    def setUp(self):
        try:
            import netgen
            NETGEN_MODULE = True 

        except ImportError:
            NETGEN_MODULE = False

        if not NETGEN_MODULE:
            self.skipTest("Missing Netgen.")

        else:
            from anisotropy import shaping

            self.shaping = shaping

            self.outputPath = os.path.join(os.path.abspath("."), "tests/test_shaping_output")
            os.makedirs(self.outputPath, exist_ok = True)

    def test_simple(self):
        simple100 = self.shaping.Simple(direction = [1, 0, 0], alpha = 0.01)
        simple001 = self.shaping.Simple(direction = [0, 0, 1], alpha = 0.01)
        simple111 = self.shaping.Simple(direction = [1, 1, 1], alpha = 0.01)

        simple100.build()
        simple001.build()
        simple111.build()

        simple100.export(os.path.join(self.outputPath, "simple100.step"))
        simple001.export(os.path.join(self.outputPath, "simple001.step"))
        simple111.export(os.path.join(self.outputPath, "simple111.step"))

    def test_bodyCentered(self):
        bodyCentered100 = self.shaping.BodyCentered(direction = [1, 0, 0], alpha = 0.01)
        bodyCentered001 = self.shaping.BodyCentered(direction = [0, 0, 1], alpha = 0.01)
        bodyCentered111 = self.shaping.BodyCentered(direction = [1, 1, 1], alpha = 0.01)

        bodyCentered100.build()
        bodyCentered001.build()
        bodyCentered111.build()

        bodyCentered100.export(os.path.join(self.outputPath, "bodyCentered100.step"))
        bodyCentered001.export(os.path.join(self.outputPath, "bodyCentered001.step"))
        bodyCentered111.export(os.path.join(self.outputPath, "bodyCentered111.step"))

    def test_faceCentered_lattice(self):
        fc = self.shaping.FaceCentered([1, 0, 0], alpha = 0.01, filletsEnabled = True)
        fc.build()
        fc.lattice.WriteStep(os.path.join(self.outputPath, "fc_lattice.step"))

    def test_faceCentered(self):
        faceCentered100 = self.shaping.FaceCentered(direction = [1, 0, 0], alpha = 0.01)
        faceCentered001 = self.shaping.FaceCentered(direction = [0, 0, 1], alpha = 0.01)
        faceCentered111 = self.shaping.FaceCentered(direction = [1, 1, 1], alpha = 0.01)

        faceCentered100.build()
        faceCentered001.build()
        faceCentered111.build()

        faceCentered100.export(os.path.join(self.outputPath, "faceCentered100.step"))
        faceCentered001.export(os.path.join(self.outputPath, "faceCentered001.step"))
        faceCentered111.export(os.path.join(self.outputPath, "faceCentered111.step"))

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
