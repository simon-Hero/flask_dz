from flask_script import Manager
from dz import create_app, db
from flask_migrate import Migrate, MigrateCommand

app = create_app("default")
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
