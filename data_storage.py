from database import db
from sqlalchemy import select
import database


def get_posts_details():
    posts = db.session.execute(select(database.Post)).scalars().all()

    return [
        {
            "post_id": p.post_id,
            "post_title": p.post_title,
            "post_content": p.post_content,
            "image_path": p.image_path,
            "author_username": p.post_author_info.username if p.post_author_info else "Unknown"
        }
        for p in posts
    ]


def get_post_details(_post_id):
    if not _post_id:
        print("Invalid argument")
        return {}, []

    post_details = db.session.scalar(select(database.Post).where(database.Post.post_id == _post_id))

    if not post_details:
        return {}, []

    post_comments = [
        {
            "comment_id": c.comment_id,
            "author_username": c.comment_author_info.username if c.comment_author_info else "Unknown",
            "comment_text": c.comment_content,
            "replies": [
                {
                    "author_username": r.reply_author_info.username if r.reply_author_info else "Unknown",
                    "comment_text": r.reply_content
                }
                for r in c.replies
            ]
        }
        for c in post_details.post_comments
    ]

    post_dict = {
        "post_id": post_details.post_id,
        "post_title": post_details.post_title,
        "post_content": post_details.post_content,
        "image_path": post_details.image_path,
        "author_username": post_details.post_author_info.username if post_details.post_author_info else "Unknown",
        "post_author_id": post_details.post_author_info.user_id if post_details.post_author_info else None
    }

    return post_dict, post_comments


def get_user_details(_user_id: int):
    if not _user_id:
        print("Invalid argument")
        return

    user_details = db.session.query(database.User).filter_by(user_id=_user_id).first()

    if not user_details:
        print("Error: UserID does not exist")
        return

    return user_details.username, user_details.email, user_details.tagged_post