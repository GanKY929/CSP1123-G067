from database import db
from sqlalchemy import select
import database


def save_post_details(_post_title: str, _post_content: str, _post_owner: int):
    if not _post_title or not _post_content or not _post_owner:
        print("Invalid arguments")
        return        
    
    new_post = database.Post(
        post_title = _post_title,
        post_content = _post_content,
        post_owner = _post_owner
    )

    db.session.add(new_post)
    db.session.commit()


def get_posts_details(first_post_id: int, last_post_id: int):
    if not first_post_id or not last_post_id:
        print("Invalid argument")
        return
   
    posts = []

    for post_id in range(first_post_id, last_post_id+1):
        post_details = db.session.execute(
            select(database.Post).filter_by(post_id)
        )

        post_dict = {
            "post_id" : post_details.post_id,
            "post_title" : post_details.title,
            "post_content" : post_details.content,
            "post_owner" : post_details.owner
        }

        posts.append(post_dict)

    return posts


def get_user_details(_user_id: int):
    if not _user_id:
        print("Invalid argument")
        return
    
    user_details = db.session.query(database.User).filter_by(user_id = _user_id).first() 

    if not user_details: 
        print("Error: UserID does not exist")
        return
    
    _username = user_details.username
    _email = user_details.email
    _tagged_post = user_details.tagged_post

    return _username, _email, _tagged_post