from sqlmodel import SQLModel, create_engine, Session
from app.config import setting

connection_string: str = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# ? Create Engine
# ? Engine is one for whole application:
engine = create_engine(
    connection_string,
    # connect_args={"sslmode": "require"},
    pool_recycle=300,
    pool_size=10,
    # echo=True,
)


# ? Create function for table creation
def create_tables():
    SQLModel.metadata.create_all(engine)


# ? Create function for session management
# ? Session: separate session for each functionality/transaction
def get_session():
    with Session(engine) as session:
        yield session
