import os
import warnings
from typing import Dict

warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
from fastapi_jwt_auth import AuthJWT
from starlette.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from app.config import Settings, get_settings
from app.main import create_application  # updated
from tests.utils.user import auth_normal_user, auth_super_user, auth_tutor_user


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()  # new
    app.dependency_overrides[get_settings] = get_settings_override
    initializer(["app.models.tortoise"])
    with TestClient(app) as test_client:

        # testing
        yield test_client
    finalizer()
    # tear down


@pytest.fixture(scope="module")
def event_loop(test_app: TestClient):
    yield test_app.task.get_loop()


@pytest.fixture(scope="module")
def authorization():
    return AuthJWT()


@pytest.fixture(scope="module")
def normal_user_token_headers(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    return auth_normal_user(authorization, event_loop)


@pytest.fixture(scope="module")
def super_user_token_headers(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    return auth_super_user(authorization, event_loop)


@pytest.fixture(scope="module")
def tutor_user_token_headers(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    return auth_tutor_user(authorization, event_loop)
