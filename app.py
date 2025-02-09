from pathlib import Path
from flask import Flask, abort
from todoical import parse_todo_file, todo_to_ical, pretty_format

TODO_PATH = Path("/ical")

app = Flask(__name__)

@app.route('/<path:ical_name>')
def serve_ical_files(ical_name):
    if not str(ical_name).endswith(".ics"):
        abort(400, description="Non-iCalendar file requested")

    todo_file = TODO_PATH / Path(ical_name.removesuffix(".ics"))

    if not todo_file.is_file():
        abort(400, description="TODO.txt base file not found")

    return pretty_format(todo_to_ical(parse_todo_file(todo_file)))

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
