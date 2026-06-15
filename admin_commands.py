from database import db
from sqlalchemy import select
import database 

def remove_user(_user_id: int):
    user_to_delete = db.session.query(database.User).filter_by(user_id=_user_id)
    db.session.delete(user_to_delete)

    return

def verify_user(_user_id: int):
    user_to_verify = db.session.query(database.User).filter_by(user_id = _user_id)
    user_to_verify.verified 
    return