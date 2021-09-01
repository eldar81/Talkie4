import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE Users (
            id int NOT NULL,
            Name TEXT NOT NULL,
            Bio_name TEXT,
            Bio_gender int,
            Bio_age int,
            Bio_hobby TEXT,
            Bio_companion_requirements int,
            is_ignore int DEFAULT 0 NOT NULL,
            is_banned int DEFAULT 0 NOT NULL,
            is_bot_banned int DEFAULT 0 NOT NULL,
            is_bot_paused int DEFAULT 0 NOT NULL,
            Send_to_Matches int,
            in_work int DEFAULT 0 NOT NULL,
            id_date int,
            PRIMARY KEY (id)
            );
"""
        self.execute(sql, commit=True)


    def create_table_match_gen(self):
        sql = """
        CREATE TABLE Match_gen (
            id_date int NOT NULL,
            id int NOT NULL,
            date int,
            age int,
            gender int,
            req int,
            list_of_matches TEXT,
            amount_of_matches int,
            match int,
            id1_id2_date TEXT,
            PRIMARY KEY (id_date)
            );
"""
        self.execute(sql, commit=True)

    def create_table_final_matches(self):
        sql = """
            CREATE TABLE Matches (
                id1_id2_date TEXT NOT NULL,
                id1 int,
                id2 int
                date int,
                notification_1 int,
                notification_2 int,
                was_contact_1 int,
                was_contact_2 int,
                why_was_not_contact_1 int,
                why_was_not_contact_2 int,
                why_did_not_write_1 int,
                why_did_not_write_2 int,
                change_companion_1 int,
                change_companion_2 int,
                meeting_agreed_1 int,
                meeting_agreed_2 int,
                meeting_done_1 int,
                meeting_done_2 int,
                rate_meeting_1 int,
                rate_meeting_2 int,
                comment_meeting_1 TEXT,
                comment_meeting_2 TEXT,
                want_more_1 int,
                want_more_2 int,
                PRIMARY KEY (id1_id2_date)
                );
    """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, name: str):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Users(id, Name) VALUES(?, ?)
        """
        self.execute(sql, parameters=(id, name), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_all_gen_matches(self):
        sql = """SELECT * FROM Match_gen"""
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def update_user_anketa(self, id, Bio_name, Bio_age, Bio_gender, Bio_hobby, Bio_companion_requirements):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_name=?, Bio_age=?, Bio_gender=?, Bio_hobby=?, Bio_companion_requirements=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_name, Bio_age, Bio_gender, Bio_hobby, Bio_companion_requirements, id), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)


    def update_user_name(self, id, Bio_name):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_name=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_name, id), commit=True)


    def update_user_age(self, id, Bio_age):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_age=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_age, id), commit=True)

    def update_user_gender(self, id, Bio_gender):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_gender=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_gender, id), commit=True)


    def update_user_hobby(self, id, Bio_hobby):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_hobby=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_hobby, id), commit=True)


    def update_user_compreq(self, id, Bio_companion_requirements):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET Bio_companion_requirements=? WHERE id=?
        """
        return self.execute(sql, parameters=(Bio_companion_requirements, id), commit=True)


    def update_user_send_to_Mathes(self, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
         UPDATE Users SET Send_to_Matches=? WHERE id=?
         """
        return self.execute(sql, parameters=(1, id), commit=True)


    def update_user_id_date(self, id, date):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
         UPDATE Users SET id_date=? WHERE id=?
         """
        return self.execute(sql, parameters=(date, id), commit=True)

    def transfer_users_to_Match_gen(self, id):
        sql = f"""
        INSERT INTO Match_gen(id_date, id, age, gender, req) SELECT id_date, id, Bio_age, Bio_gender, Bio_companion_requirements FROM Users WHERE id=?
        """
        return self.execute(sql, parameters=id, commit=True)

    def set_date_to_transfered_users(self, date, id_date):
        sql = f"""
                 UPDATE Match_gen SET date=? WHERE id_date=?
                 """
        return self.execute(sql, parameters=(date, id_date), commit=True)


    def set_list_of_matches(self, list, id_date):
        sql = f"""
                 UPDATE Match_gen SET list_of_matches=? WHERE id_date=?
                 """
        return self.execute(sql, parameters=(list, id_date), commit=True)


    def set_amount_of_matches(self, amount, id_date):
        sql = f"""
                 UPDATE Match_gen SET amount_of_matches=? WHERE id_date=?
                 """
        return self.execute(sql, parameters=(amount, id_date), commit=True)


    def set_match(self, match, id_date):
        sql = f"""UPDATE Match_gen SET match=? WHERE id_date=?"""
        return self.execute(sql, parameters=(match, id_date), commit=True)


    def select_user_match(self, id_date):
        sql = f"""SELECT match FROM Match_gen WHERE id_date=?"""
        return self.execute(sql, parameters=id_date, fetchone=True)


    def transfer_matches_to_Match(self, id_date):
        sql = f"""
        INSERT INTO Matches(id1_id2_date, id1, id2) SELECT id1_id2_date, id, match FROM Match_gen WHERE id_date=?
        """
        return self.execute(sql, parameters=id_date, commit=True)


    def set_id1_id2_date(self, id1_id2_date, id_date):
        sql = f"""UPDATE Match_gen SET id1_id2_date=? WHERE id_date=?"""
        return self.execute(sql, parameters=(id1_id2_date, id_date), commit=True)


    def select_all_matches(self):
        sql = """SELECT * FROM Matches"""
        return self.execute(sql, fetchall=True)


    def set_notification_1(self, id):
        sql = f"""UPDATE Matches SET notification_1=? WHERE id1=?"""
        return self.execute(sql, parameters=(1, id), commit=True)


    def set_notification_2(self, id):
        sql = f"""UPDATE Matches SET notification_2=? WHERE id2=?"""
        return self.execute(sql, parameters=(1, id), commit=True)


    def select_ids_from_matches(self, id):
        sql = f"""SELECT match FROM Match_gen WHERE id=?"""
        return self.execute(sql, parameters=id, fetchone=True)


    def update_in_work(self, id):
        sql = f"""UPDATE Users SET in_work=1 WHERE id=?"""
        return self.execute(sql, parameters=(id), commit=True)



def logger(statement):
    print(f"""
____     
Executing: 
{statement}
____
""")
