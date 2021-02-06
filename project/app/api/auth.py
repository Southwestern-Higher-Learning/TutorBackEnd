import datetime
import json
import logging

import google_auth_oauthlib.flow
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import Settings, get_settings
from app.models.pydnatic import SwapCodeIn
from app.models.tortoise import Credentials, User, User_Pydnatic, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("uvicorn")

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


def get_google_info(settings: Settings = Depends(get_settings)):
    return {
        "web": {
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.google_client_secret,
            "client_id": settings.google_client_id,
            "project_id": settings.google_project_id,
            "redirect_uris": settings.google_redirect_uris,
            "javascript_origins": settings.google_js_origins,
        }
    }


@router.get("/code/client")
def get_client_auth(request: Request, google_info=Depends(get_google_info)):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(google_info, scopes=SCOPES)
    flow.redirect_uri = request.url_for("callback")
    logger.info(request.url_for("callback"))

    authorization_url, _ = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        prompt="consent",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    return RedirectResponse(authorization_url)


@router.get("/code/url")
def get_auth_url(google_info=Depends(get_google_info)):
    return {"scopes": SCOPES, "client_id": google_info["web"]["client_id"]}


def verify_creds(
    flow: google_auth_oauthlib.flow.Flow, google_info, settings: Settings
) -> dict:
    creds = flow.credentials

    req = requests.Request()
    id_info = id_token.verify_oauth2_token(
        creds._id_token, req, google_info["web"]["client_id"]
    )

    if "hd" not in id_info or id_info["hd"] != settings.top_domain:
        raise HTTPException(
            status_code=403,
            detail=f"Not an authorized domain {id_info.get('hd', '')},{settings.top_domain}",
        )

    return id_info


@router.post("/swap")
async def swap_code(
    request: Request,
    swap_info: SwapCodeIn,
    google_info=Depends(get_google_info),
    settings: Settings = Depends(get_settings),
    Authorize: AuthJWT = Depends(),
):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(google_info, scopes=SCOPES)
    flow.redirect_uri = swap_info.redirect_uri
    logger.info(swap_info.redirect_uri)
    flow.fetch_token(code=swap_info.code)

    info = verify_creds(flow, google_info, settings)

    return await get_or_create_user(flow, info, Authorize)


@router.get("/callback", response_model=UserCreate)
async def callback(
    request: Request,
    google_info=Depends(get_google_info),
    settings: Settings = Depends(get_settings),
    Authorize: AuthJWT = Depends(),
):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(google_info, scopes=SCOPES)
    flow.redirect_uri = request.url_for("callback")

    flow.fetch_token(authorization_response=str(request.url))

    info = verify_creds(flow, google_info, settings)

    return await get_or_create_user(flow, info, Authorize)


async def get_or_create_user(
    flow: google_auth_oauthlib.flow.Flow, info, Authorize: AuthJWT
) -> UserCreate:
    google_creds = flow.credentials
    temp = {
        "token": google_creds.token,
        "refresh_token": google_creds.refresh_token,
        "token_uri": google_creds.token_uri,
        "scopes": google_creds.scopes,
        "expiry": datetime.datetime.strftime(google_creds.expiry, "%Y-%m-%d %H:%M:%S"),
    }

    user = await User.get_or_none(email=info["email"]).first()

    if user is None:
        user = User()
        user.username = info["email"].split("@")[0]
        user.first_name = info["given_name"]
        user.last_name = info["family_name"]
        user.profile_url = info["picture"]
        user.email = info["email"]

        await user.save()

    creds, bo = await Credentials.get_or_create(user=user)
    creds.json_field = json.dumps(temp)
    await creds.save()

    return UserCreate(
        user=await User_Pydnatic.from_tortoise_orm(user),
        access_token=Authorize.create_access_token(subject=user.email),
        refresh_token=Authorize.create_refresh_token(subject=user.email),
    )
