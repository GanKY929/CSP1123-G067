from database import db
import database

def save_post(_post_title: str, _post_content:str, _post_owner: int):
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

    return
    
