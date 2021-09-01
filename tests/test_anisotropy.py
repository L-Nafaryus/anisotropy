import os
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

# TODO: update tests
class TestAnisotropy(unittest.TestCase):
    def setUp(self):
        from anisotropy.core.main import Anisotropy
        self.model = Anisotropy()

    def test_01_create_db(self):
        self.model.db.setup()
        path = os.path.join(self.model.env["db_path"], "anisotropy.db")

        self.assertTrue(os.path.exists(path))

    def test_02_load_from_scratch(self):
        passed = True

        try:
            paramsAll = self.model.loadFromScratch()

            for entry in paramsAll:
                self.model.update(entry)

        except Exception as e:
            passed = False
            print(e)

        self.assertTrue(passed)

    def test_03_load_db(self):
        self.model.load("simple", [1.0, 0.0, 0.0], 0.01)

        self.assertEqual(self.model.params["structure"]["type"], "simple")

    def tearDown(self):
        #os.removedirs(self.model.env["BUILD"])
        #os.removedirs(self.model.env["LOG"])
        pass

if __name__ == "__main__":
    unittest.main()
