import json

from app.models.tortoise import User


def test_get_superuser_me(test_app, super_user_token_headers):
    r = test_app.get("/user/me", headers=super_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_superuser"]
    assert not current_user["is_tutor"]
    assert current_user["email"] == "super_user@southwestern.edu"


def test_get_normal_user(test_app, normal_user_token_headers):
    r = test_app.get("/user/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert not current_user["is_superuser"]
    assert not current_user["is_tutor"]
    assert current_user["email"] == "test_user@southwestern.edu"


def test_get_tutor_user(test_app, tutor_user_token_headers):
    r = test_app.get("/user/me", headers=tutor_user_token_headers)
    current_user = r.json()
    assert current_user
    assert not current_user["is_superuser"]
    assert current_user["is_tutor"]
    assert current_user["email"] == "tutor_user@southwestern.edu"


def test_get_user_id(test_app, tutor_user_token_headers, event_loop):
    r = test_app.get("/user/1", headers=tutor_user_token_headers)
    user_one = r.json()
    assert user_one

    async def get_user_one():
        return await User.get_or_none(id=1)

    user_obj = event_loop.run_until_complete(get_user_one())
    print(user_one)
    assert user_obj.id == user_one["id"]
    assert user_obj.email == user_one["email"]
    assert "password" not in user_one


def test_get_user_id_unauthorized(test_app):
    r = test_app.get("/user/1")
    assert r.status_code == 401


def test_get_user_me_unauthorized(test_app):
    r = test_app.get("/user/me")
    assert r.status_code == 401


def test_patch_user_me(test_app, normal_user_token_headers, event_loop):
    data = {
        "description": "Test user's description",
    }
    r = test_app.patch(
        "/user/me", data=json.dumps(data), headers=normal_user_token_headers
    )
    current_user = r.json()
    print(current_user)
    assert r.status_code == 200
    assert current_user
    assert current_user["email"] == "test_user@southwestern.edu"
    assert current_user["description"] == data["description"]
