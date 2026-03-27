from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from pathlib import Path

from core import (
    BASE_DIR,
    get_report,
    list_people,
    process_saved_path,
    rename_person,
    save_uploaded_file,
    search_people_by_filename,
)


def create_app():
    app = Flask(__name__)
    app.secret_key = 'face-finder-dev'

    @app.route('/')
    def index():
        return render_template('gallery.html', people=list_people())

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            files = request.files.getlist('files')
            uploaded = 0
            for file in files:
                if not file or not file.filename:
                    continue
                saved = save_uploaded_file(file)
                process_saved_path(saved)
                uploaded += 1
            if uploaded:
                flash(f'Uploaded and processed {uploaded} file(s).')
                return redirect(url_for('index'))
            flash('No files were uploaded.')
            return redirect(url_for('upload'))
        return render_template('upload.html')

    @app.route('/rename', methods=['GET', 'POST'])
    def rename():
        if request.method == 'POST':
            person_id = request.form.get('person_id', '')
            display_name = request.form.get('display_name', '')
            if person_id:
                rename_person(person_id, display_name)
                flash(f'Updated {person_id}.')
            return redirect(url_for('rename'))
        return render_template('rename.html', people=list_people())

    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('q', '')
        return render_template('search.html', people=search_people_by_filename(query), query=query)

    @app.route('/report')
    def report():
        return render_template('report.html', report=get_report())

    @app.route('/data/<path:filename>')
    def data_files(filename: str):
        return send_from_directory(BASE_DIR / 'data', filename)

    @app.context_processor
    def utility_processor():
        def public_path(raw_path: str):
            if not raw_path:
                return ''
            path = Path(raw_path).as_posix()
            if path.startswith('data/'):
                return '/' + path
            return '/data/' + path.removeprefix('data/')
        return {'public_path': public_path}

    return app
