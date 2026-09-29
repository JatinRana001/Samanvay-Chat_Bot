import sys
import os
from pathlib import Path
import tempfile
from uuid import uuid4

backend_root = str(Path(__file__).parent.parent.resolve())
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

os.environ["ENVIRONMENT"] = "test"
test_database = Path(tempfile.gettempdir()) / f"samanvay-pytest-{uuid4().hex}.sqlite"
os.environ["DATABASE_URL"] = f"sqlite:///{test_database.as_posix()}"

# The shared legacy unit tests use SessionLocal directly; give them an isolated
# workbook-backed SQLite registry as their session-scoped fixture.
from app.database import Base, engine  # noqa: E402
from seeds.import_maharashtra_data import import_workbook  # noqa: E402

Base.metadata.create_all(bind=engine)
import_workbook(Path(backend_root) / "data" / "Maharashtra_Industry_Approvals_Database.xlsx", reset=True)
