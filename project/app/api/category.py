from fastapi import APIRouter

router = APIRouter(prefix="/category", tags=["category"])


# GET /
# Must be normal user (find_current_user)
# Get all categories

# GET /{id}
# Must be normal user
# Get category by ID

# POST /
# Must be superuser (find_current_superuser)
# Create new category

# PUT /{id}
# Must be superuser
# Update individual category