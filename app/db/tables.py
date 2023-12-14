import sqlalchemy as SA

metadata = SA.MetaData()

User: SA.Table = SA.Table(
    "user_teacher",
    metadata,
    SA.Column("id", SA.String(length=5), unique=True, primary_key=True),
    SA.Column("username", SA.String(length=32), unique=True),
    SA.Column("fullname", SA.String(length=40), nullable=False),
    SA.Column("password_hash", SA.String(length=64), nullable=False),
    SA.Column("email", SA.String(length=64), unique=True)
)

Class: SA.Table = SA.Table(
    "class",
    metadata,
    SA.Column("id", SA.Integer, autoincrement=True, unique=True, primary_key=True),
    SA.Column("name", SA.String(length=32), nullable=False),
    SA.Column("teacher_id", SA.ForeignKey('user_teacher.id', ondelete="CASCADE"), nullable=False)
)

Student: SA.Table = SA.Table(
    "student",
    metadata,
    SA.Column("id", SA.String(length=5), unique=True, primary_key=True),
    SA.Column("fullname", SA.String(length=40), nullable=False),
    SA.Column("class_id", SA.ForeignKey('class.id', ondelete="CASCADE"), nullable=False)
)

Test: SA.Table = SA.Table(
    "test",
    metadata,
    SA.Column("id", SA.Integer, autoincrement=True, unique=True, primary_key=True),
    SA.Column("name", SA.String(length=32), nullable=False),
    SA.Column("answers", SA.ARRAY(SA.String(length=1)), nullable=False),
    SA.Column("teacher_id", SA.ForeignKey('user_teacher.id', ondelete="CASCADE"), nullable=False)
)

TestResult: SA.Table = SA.Table(
    "test_result",
    metadata,
    SA.Column("id", SA.Integer, autoincrement=True, unique=True, primary_key=True),
    SA.Column("test_id", SA.ForeignKey('test.id', ondelete="CASCADE"), nullable=False),
    SA.Column("student_id", SA.ForeignKey('student.id', ondelete="CASCADE"), nullable=False),
    SA.Column("class_id", SA.ForeignKey('class.id', ondelete="CASCADE"), nullable=False),
    SA.Column("score", SA.Integer, nullable=False),
    SA.Column("answers", SA.ARRAY(SA.String(length=1)), nullable=False)
)