import sqlite3
import json
from flask import Flask, request, redirect, url_for, send_file

# Создание и подключение к базе данных
conn = sqlite3.connect("judiciary.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.execute("""
CREATE TABLE IF NOT EXISTS Judges (
    JudgeID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Experience INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Cases (
    CaseID INTEGER PRIMARY KEY AUTOINCREMENT,
    CaseName TEXT NOT NULL,
    CaseDate TEXT NOT NULL,
    JudgeID INTEGER,
    FOREIGN KEY (JudgeID) REFERENCES Judges (JudgeID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Participants (
    ParticipantID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Role TEXT NOT NULL,
    CaseID INTEGER,
    FOREIGN KEY (CaseID) REFERENCES Cases (CaseID)
)
""")

conn.commit()

# Flask-приложение
app = Flask(__name__)

# Стиль страницы
STYLE = """
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    h1 {
        text-align: center;
        color: #333;
    }
    ul {
        list-style-type: none;
        padding: 0;
    }
    li {
        background: #ffffff;
        margin: 10px 0;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    a {
        text-decoration: none;
        color: #007BFF;
    }
    form {
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 400px;
        margin: auto;
    }
    input, select, button {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    button {
        background-color: #007BFF;
        color: #fff;
        cursor: pointer;
    }
    .delete-button {
        background-color: #dc3545;
        color: white;
        cursor: pointer;
        padding: 1px 5px;  /* Увеличиваем размер кнопки */
        border-radius: 10px;
        text-align: center;
        display: inline-block;
        margin-left: 20px;  /* Добавляем отступ слева */
    }
    .delete-button:hover {
        background-color: #c82333;
    }
</style>
"""


# Главная страница
@app.route("/")
def home():
    return f"""
    {STYLE}
    <h1>Судебная база данных</h1>
    <ul>
        <li><a href="/judges">Список судей</a></li>
        <li><a href="/cases">Список дел</a></li>
        <li><a href="/participants">Список участников</a></li>
        <li><a href="/export">Экспорт данных в JSON</a></li>
    </ul>
    """


# Список судей с формой добавления и кнопками удаления
@app.route("/judges", methods=["GET", "POST"])
def judges():
    if request.method == "POST":
        name = request.form["name"]
        experience = request.form["experience"]
        cursor.execute("INSERT INTO Judges (Name, Experience) VALUES (?, ?)", (name, experience))
        conn.commit()
        return redirect(url_for("judges"))

    if request.args.get('delete'):
        judge_id = request.args.get('delete')
        cursor.execute("DELETE FROM Judges WHERE JudgeID = ?", (judge_id,))
        conn.commit()
        return redirect(url_for("judges"))

    cursor.execute("SELECT * FROM Judges")
    judges = cursor.fetchall()
    judges_html = "".join(
        f"<li>ID: {judge[0]}, Имя: {judge[1]}, Опыт: {judge[2]} лет <a href='?delete={judge[0]}' class='delete-button'>Удалить</a></li>"
        for judge in judges
    )

    return f"""
    {STYLE}
    <h1>Список судей</h1>
    <ul>{judges_html}</ul>
    <form method="POST">
        <input type="text" name="name" placeholder="Имя судьи" required>
        <input type="number" name="experience" placeholder="Опыт (в годах)" required>
        <button type="submit">Добавить судью</button>
    </form>
    <a href="/">Вернуться на главную</a>
    """


# Список дел с формой добавления и кнопками удаления
@app.route("/cases", methods=["GET", "POST"])
def cases():
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        judge_id = request.form["judge_id"]
        cursor.execute("INSERT INTO Cases (CaseName, CaseDate, JudgeID) VALUES (?, ?, ?)", (name, date, judge_id))
        conn.commit()
        return redirect(url_for("cases"))

    if request.args.get('delete'):
        case_id = request.args.get('delete')
        cursor.execute("DELETE FROM Cases WHERE CaseID = ?", (case_id,))
        conn.commit()
        return redirect(url_for("cases"))

    cursor.execute("SELECT * FROM Cases")
    cases = cursor.fetchall()

    cursor.execute("SELECT JudgeID, Name FROM Judges")
    judges = cursor.fetchall()
    judge_options = "".join(f'<option value="{judge[0]}">{judge[1]}</option>' for judge in judges)

    cases_html = "".join(
        f"<li>ID: {case[0]}, Название: {case[1]}, Дата: {case[2]}, ID судьи: {case[3]} <a href='?delete={case[0]}' class='delete-button'>Удалить</a></li>"
        for case in cases
    )

    return f"""
    {STYLE}
    <h1>Список дел</h1>
    <ul>{cases_html}</ul>
    <form method="POST">
        <input type="text" name="name" placeholder="Название дела" required>
        <input type="date" name="date" required>
        <select name="judge_id" required>
            <option value="">Выберите судью</option>
            {judge_options}
        </select>
        <button type="submit">Добавить дело</button>
    </form>
    <a href="/">Вернуться на главную</a>
    """


# Список участников с формой добавления и кнопками удаления
@app.route("/participants", methods=["GET", "POST"])
def participants():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        case_id = request.form["case_id"]
        cursor.execute("INSERT INTO Participants (Name, Role, CaseID) VALUES (?, ?, ?)", (name, role, case_id))
        conn.commit()
        return redirect(url_for("participants"))

    if request.args.get('delete'):
        participant_id = request.args.get('delete')
        cursor.execute("DELETE FROM Participants WHERE ParticipantID = ?", (participant_id,))
        conn.commit()
        return redirect(url_for("participants"))

    cursor.execute("SELECT * FROM Participants")
    participants = cursor.fetchall()

    cursor.execute("SELECT CaseID, CaseName FROM Cases")
    cases = cursor.fetchall()
    case_options = "".join(f'<option value="{case[0]}">{case[1]}</option>' for case in cases)

    participants_html = "".join(
        f"<li>ID: {participant[0]}, Имя: {participant[1]}, Роль: {participant[2]}, ID дела: {participant[3]} <a href='?delete={participant[0]}' class='delete-button'>Удалить</a></li>"
        for participant in participants
    )

    return f"""
    {STYLE}
    <h1>Список участников</h1>
    <ul>{participants_html}</ul>
    <form method="POST">
        <input type="text" name="name" placeholder="Имя участника" required>
        <input type="text" name="role" placeholder="Роль (например, Истец, Ответчик)" required>
        <select name="case_id" required>
            <option value="">Выберите дело</option>
            {case_options}
        </select>
        <button type="submit">Добавить участника</button>
    </form>
    <a href="/">Вернуться на главную</a>
    """


# Экспорт данных
@app.route("/export", methods=["GET"])
def export_to_json():
    data = {}
    for table in ["Judges", "Cases", "Participants"]:
        cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        data[table] = [dict(zip(columns, row)) for row in rows]
    export_path = "export.json"
    with open(export_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return send_file(export_path, as_attachment=True)


if __name__ == "__main__":
    print("Сервер запущен. Перейдите по адресу: http://127.0.0.1:5000")
    app.run(debug=True)
