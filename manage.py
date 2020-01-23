from flask_script import Manager
from dz import create_app, db
from flask_migrate import Migrate, MigrateCommand

app = create_app("default")
app.host = '0.0.0.0'
app.port = 5000
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
