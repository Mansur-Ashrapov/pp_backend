import sqlalchemy as SA


from app.db.utils import create_id_len_five


metadata = SA.MetaData()

User: SA.Table = SA.Table(
    "user_teacher",
    metadata,
    SA.Column("id", SA.String(length=5), default=create_id_len_five, unique=True, primary_key=True),
    SA.Column("username", SA.String(length=32), unique=True),
    SA.Column("fullname", SA.String(length=40), nullable=False),
    SA.Column("password_hash", SA.String(length=64), nullable=False),
    SA.Column("email", SA.String(length=64), unique=True)
)
