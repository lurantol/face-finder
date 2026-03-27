from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZipFile

from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
UPLOADS_DIR = DATA_DIR / 'uploads'
OUTPUT_DIR = DATA_DIR / 'output'
PREVIEWS_DIR = OUTPUT_DIR / 'previews'
DB_FILE = DATA_DIR / 'db.json'
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_ARCHIVE_EXTENSIONS = {'.zip'}


@dataclass
class PersonRecord:
    person_id: str
    display_name: str
    preview_path: Optional[str]
    images: List[str]


@dataclass
class ReportRecord:
    total_files: int
    image_files: int
    archive_files: int
    unsupported_files: List[str]
    unexpected_formats: List[Dict[str, str]]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    PREVIEWS_DIR.mkdir(exist_ok=True)


def load_db() -> Dict:
    ensure_dirs()
    if not DB_FILE.exists():
        return {'people': [], 'report': asdict(ReportRecord(total_files=0, image_files=0, archive_files=0, unsupported_files=[], unexpected_formats=[]))}
    return json.loads(DB_FILE.read_text(encoding='utf-8'))


def save_db(db: Dict) -> None:
    ensure_dirs()
    DB_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')


def list_people() -> List[Dict]:
    return load_db().get('people', [])


def get_report() -> Dict:
    return load_db().get('report', {})


def normalize_filename(name: str) -> str:
    return ''.join(c if c.isalnum() or c in {'-', '_', '.'} else '_' for c in name)


def save_uploaded_file(file_storage) -> Path:
    ensure_dirs()
    filename = normalize_filename(file_storage.filename or 'upload.bin')
    target = UPLOADS_DIR / filename
    counter = 1
    while target.exists():
        stem = target.stem
        suffix = target.suffix
        target = UPLOADS_DIR / f'{stem}_{counter}{suffix}'
        counter += 1
    file_storage.save(target)
    return target


def is_supported_image(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS


def is_supported_archive(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_ARCHIVE_EXTENSIONS


def inspect_image_format(path: Path) -> Optional[str]:
    try:
        with Image.open(path) as img:
            return img.format
    except Exception:
        return None


def make_preview(image_path: Path, person_id: str) -> str:
    ensure_dirs()
    preview_target = PREVIEWS_DIR / f'{person_id}.jpg'
    with Image.open(image_path) as img:
        thumb = ImageOps.exif_transpose(img)
        thumb.thumbnail((320, 320))
        rgb = thumb.convert('RGB')
        rgb.save(preview_target, format='JPEG', quality=90)
    return str(preview_target.relative_to(BASE_DIR)).replace('\\', '/')


def _append_person(db: Dict, image_rel_path: str, display_name: Optional[str] = None) -> None:
    person_index = len(db['people']) + 1
    person_id = f'Person_{person_index}'
    preview_path = make_preview(BASE_DIR / image_rel_path, person_id)
    person = PersonRecord(
        person_id=person_id,
        display_name=display_name or person_id,
        preview_path=preview_path,
        images=[image_rel_path],
    )
    db['people'].append(asdict(person))


def process_saved_path(saved_path: Path) -> Dict:
    db = load_db()
    report = db['report']
    report['total_files'] += 1

    if is_supported_archive(saved_path):
        report['archive_files'] += 1
        extract_dir = saved_path.with_suffix('')
        extract_dir.mkdir(exist_ok=True)
        with ZipFile(saved_path, 'r') as zf:
            zf.extractall(extract_dir)
        for nested in extract_dir.rglob('*'):
            if nested.is_file():
                process_saved_path(nested)
        save_db(db)
        return db

    if is_supported_image(saved_path):
        report['image_files'] += 1
        fmt = inspect_image_format(saved_path)
        if fmt and fmt.upper() != 'JPEG' and saved_path.suffix.lower() in {'.jpg', '.jpeg'}:
            report['unexpected_formats'].append({'file': str(saved_path.relative_to(BASE_DIR)), 'format': fmt})
        rel = str(saved_path.relative_to(BASE_DIR)).replace('\\', '/')
        _append_person(db, rel)
        save_db(db)
        return db

    report['unsupported_files'].append(str(saved_path.relative_to(BASE_DIR)).replace('\\', '/'))
    save_db(db)
    return db


def rename_person(person_id: str, new_name: str) -> None:
    db = load_db()
    for person in db.get('people', []):
        if person['person_id'] == person_id:
            person['display_name'] = new_name.strip() or person_id
            break
    save_db(db)


def search_people_by_filename(query: str) -> List[Dict]:
    q = query.lower().strip()
    if not q:
        return list_people()
    result = []
    for person in list_people():
        images = person.get('images', [])
        if person.get('display_name', '').lower().find(q) >= 0 or any(q in img.lower() for img in images):
            result.append(person)
    return result


def reset_demo_data() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    ensure_dirs()
    save_db({'people': [], 'report': asdict(ReportRecord(total_files=0, image_files=0, archive_files=0, unsupported_files=[], unexpected_formats=[]))})
