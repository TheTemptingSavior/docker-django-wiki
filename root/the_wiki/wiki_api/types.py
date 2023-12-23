from typing import Optional, TypedDict


CreateArticleBodyPermission = TypedDict(
    "CreateArticleBodyPermission",
    {
        "group": int,
        "group_read": bool,
        "group_write": bool,
        "other_read": bool,
        "other_write": bool,
    },
    total=False,
)

CreateArticleBody = TypedDict(
    "CreateArticleBody",
    {
        "parent": int,
        "title": str,
        "slug": Optional[str],
        "content": str,
        "summary": Optional[str],
        "permissions": CreateArticleBodyPermission
    },
    total=False
)

CreateRevisionBody = TypedDict(
    "CreateRevisionBody",
    {"content": str, "user_message": Optional[str]},
    total=False
)
