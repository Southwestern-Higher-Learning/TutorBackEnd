import logging

import google_auth_oauthlib.flow
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import Settings, get_settings

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


@router.get("/swap")
def swap_code(request: Request):
    return request.headers


@router.get("/callback")
def callback(
    request: Request,
    google_info=Depends(get_google_info),
    settings: Settings = Depends(get_settings),
):
    flow = google_auth_oauthlib.flow.Flow.from_client_config(google_info, scopes=SCOPES)
    flow.redirect_uri = request.url_for("callback")

    flow.fetch_token(authorization_response=str(request.url))

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
