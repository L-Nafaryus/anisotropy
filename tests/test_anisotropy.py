import os
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestAnisotropy(unittest.TestCase):
    def setUp(self):
        import anisotropy
        self.model = anisotropy.Anisotropy()

    def test_01_create_db(self):
        self.model.setupDB()
        path = os.path.join(self.model.env["db_path"], "anisotropy.db")
        
        self.assertTrue(os.path.exists(path))

    def test_02_load_scratch(self):
        passed = True

        try:
            self.model.loadScratch()
        
        except Exception as e:
            passed = False
        
        self.assertTrue(passed)

    def test_03_load_db(self):
        self.model.setupDB()
        self.model.loadDB("simple", [1.0, 0.0, 0.0], 0.01)

        self.assertEqual(self.model.params["structure"]["type"], "simple")
        
    def test_04_updateDB(self):
        self.model.updateDB()

if __name__ == "__main__":
    unittest.main()
