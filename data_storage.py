from database import db
from sqlalchemy import select
import database

def save_post_details(_post_title: str, _post_content: str, _image_path: str, _post_author: int):
    if not _post_title or not _post_content or not _post_author or not _image_path:
        print("Invalid arguments")
        return        
    
    new_post = database.Post(
        post_title = _post_title,
        post_content = _post_content,
        image_path = _image_path,
        post_author = _post_author
    )

    db.session.add(new_post)
    db.session.commit()


def get_posts_details(first_post_id: int, last_post_id: int):
    if not first_post_id or not last_post_id:
        print("Invalid argument")
        return

    posts = []

    for _post_id in range(first_post_id, last_post_id+1):
        post_details = db.session.scalar(select(database.Post).where(database.Post.post_id == _post_id))

        post_dict = {
            "post_id" : post_details.post_id,
            "post_title" : post_details.post_title,
            "post_content" : post_details.post_content,
            "image_path" : post_details.image_path
        }

        posts.append(post_dict)

    return posts


def get_post_details(_post_id):
    if not _post_id:
        print("Invalid argument")
        return
   
    post_details = db.session.scalar(select(database.Post).where(database.Post.post_id == _post_id))
    post_comments = [] 

    for comments in post_details.post_comments:  
        replies = get_replies(comments.replies)

        comment = {
            "comment_id": comments.comment_id,
            "author_username" : comments.comment_author_info.username,
            "comment_text" : comments.comment_content,
            "replies" : replies
        }

        post_comments.append(comment)

    post_dict = {
        "post_id" : post_details.post_id,
        "post_title" : post_details.post_title,
        "post_content" : post_details.post_content,
        "image_path" : post_details.image_path,
        "author_username" : post_details.post_author_info.username,
        "post_author_id" : post_details.post_author_info.user_id
    }

    return post_dict, post_comments


def get_replies(replies):
    comment_replies = []

    for reply in replies: 
        reply = {
            "author_username" : reply.reply_author_info.username,
            "comment_text" : reply.reply_content
        }

        comment_replies.append(reply)
    
    return comment_replies


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