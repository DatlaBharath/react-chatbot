from app.core.config import Settings


def test_defaults_to_sqlite():
    assert Settings(_env_file=None).sqlalchemy_url.startswith("sqlite")


def test_builds_mysql_url_and_escapes_password():
    s = Settings(_env_file=None, mysql_host="mysql", mysql_user="u", mysql_password="p@ss/word")
    assert s.sqlalchemy_url == "mysql+pymysql://u:p%40ss%2Fword@mysql:3306/chatbot"


def test_database_url_overrides_parts():
    s = Settings(_env_file=None, database_url="sqlite://", mysql_host="mysql")
    assert s.sqlalchemy_url == "sqlite://"
