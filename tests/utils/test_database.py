from contextlib import suppress
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from one_shot_api.utils.database import get_db


def test_get_db() -> None:
    # Create a mock session
    mock_session = MagicMock(spec=Session)
    mock_sessionmaker = MagicMock(return_value=mock_session)

    # Test the generator with a context manager
    with patch(
        "one_shot_api.utils.database.get_session_maker", return_value=mock_sessionmaker
    ):
        db_gen = get_db()
        db = next(db_gen)

        # Verify the session was created
        assert isinstance(db, Session)
        mock_sessionmaker.assert_called_once()

        # Verify close was not called yet
        mock_session.close.assert_not_called()

        # Finish the generator
        with suppress(StopIteration):
            next(db_gen)

        # Verify close was called
        mock_session.close.assert_called_once()


def test_get_db_connection_error():
    # Mock the session maker to raise an exception
    mock_session_maker = MagicMock()
    mock_session_maker.side_effect = Exception("Database error")

    with (
        patch(
            "one_shot_api.utils.database.get_session_maker",
            return_value=mock_session_maker,
        ),
        pytest.raises(OperationalError),
    ):
        next(get_db())


def test_get_db_with_different_config():
    # Mock the settings and engine creation
    with (
        patch("one_shot_api.utils.database.settings") as mock_settings,
        patch("one_shot_api.utils.database.create_database_engine") as mock_engine,
    ):
        # Setup different database configuration
        mock_settings.DB_USER = "test_user"
        mock_settings.DB_PASSWORD = "test_password"
        mock_settings.DB_HOST = "test_host"
        mock_settings.DB_PORT = "5432"
        mock_settings.DB_NAME = "test_db"
        mock_settings.DATABASE_URL = (
            "postgresql://test_user:test_password@test_host:5432/test_db"
        )

        # Mock session
        mock_session = MagicMock(spec=Session)
        mock_sessionmaker_instance = MagicMock(return_value=mock_session)
        mock_engine.return_value = MagicMock()

        with patch(
            "one_shot_api.utils.database.sessionmaker",
            return_value=mock_sessionmaker_instance,
        ):
            # Test the generator
            db_gen = get_db()
            db = next(db_gen)

            # Verify the session was created with the correct configuration
            assert isinstance(db, Session)
            mock_engine.assert_called_once_with(mock_settings.DATABASE_URL)
            mock_sessionmaker_instance.assert_called_once()

            # Finish the generator
            with suppress(StopIteration):
                next(db_gen)

            # Verify close was called
            mock_session.close.assert_called_once()


def test_get_db_session_scope():
    # Create a mock session
    mock_session = MagicMock(spec=Session)
    mock_sessionmaker = MagicMock(return_value=mock_session)

    # Test the generator with a context manager
    with patch(
        "one_shot_api.utils.database.get_session_maker", return_value=mock_sessionmaker
    ):
        db_gen = get_db()
        db = next(db_gen)

        # Verify the session was created
        assert isinstance(db, Session)
        mock_sessionmaker.assert_called_once()

        # Verify close was not called yet
        mock_session.close.assert_not_called()

        # Finish the generator
        with suppress(StopIteration):
            next(db_gen)

        # Verify close was called
        mock_session.close.assert_called_once()
