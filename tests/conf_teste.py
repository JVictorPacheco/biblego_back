from unittest.mock import MagicMock, patch

def mock_db():
    """ Mock da conexão com o banco de dados """
    with patch("app.Config.database.get_db_connection") as mock_get_db:
        db = MagicMock()
        mock_get_db.return_value = db
        yield db