import os, shutil
import unittest

unittest.TestLoader.sortTestMethodsUsing = None

class TestDatabase(unittest.TestCase):
    def setUp(self):
        from anisotropy import database 

        self.database = database

        self.outputPath = os.path.join(os.path.abspath("."), "tests/test_database_output")
        os.makedirs(self.outputPath, exist_ok = True)

    def test_setup(self):
        filepath = os.path.join(self.outputPath, "test_database.db")
        
        db = self.database.database
        db.setup(filepath)

        self.assertTrue(
            os.path.exists(filepath) and os.path.isfile(filepath), 
            "database wasn't created"
        )
        
        with db:
            for table in db.tables:
                self.assertTrue(table.table_exists())

    def tearDown(self):
        shutil.rmtree(self.outputPath)

if __name__ == "__main__":
    unittest.main()
