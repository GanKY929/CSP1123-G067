from database import db
import database

def save_post_details(_post_title: str, _post_content:str, _post_owner: int):
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

def get_post_details(_post_id: int)-> str:
    if not _post_id:
        print("Invalid argument")
        return
    
    post_returned = db.session.execute(
        db.session.query(database.Post).filter_by(post_id = _post_id).first()
    )

    if not post_returned:
        print("Error: PostID does not exist")
        return
    
    _post_title = post_returned.post_title
    _post_owner = post_returned.post_owner
    _post_content = post_returned.post_content

    return _post_title, _post_owner, _post_content
    
def get_user_details(_user_id: int):
    if not _user_id:
        print("Invalid argument")
        return
    
    user_details = db.session.execute(
        db.session.query(database.User).filter_by(user_id = _user_id).first()
    )

    if not user_details: 
        print("Error: UserID does not exist")
        return
    
    _username = user_details.username
    _email = user_details.email
    _tagged_post = user_details.details.tagged_post

    return _username, _email, _tagged_post