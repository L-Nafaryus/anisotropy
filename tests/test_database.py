import os
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
        tables = [
            self.database.Execution,
            self.database.Physics,
            self.database.Shape,
            self.database.Mesh,
            self.database.Flow
        ]
        db = self.database.Database(filepath)
        db.setup()

        self.assertTrue(
            os.path.exists(filepath) and os.path.isfile(filepath), 
            "database wasn't created"
        )
        
        for table in tables:
            self.assertTrue(table.table_exists())

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
