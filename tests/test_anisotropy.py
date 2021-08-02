import os

class TestAnisotropy:
    def test_import(self):
        import anisotropy

    def test_db(self):
        import anisotropy

        a = anisotropy.Anisotropy()
        a.setupDB()
        a.evalEnvParameters()
        a.updateDB()

        if os.path.exists("build/anisotropy.db"):
            os.remove("build/anisotropy.db")
        
