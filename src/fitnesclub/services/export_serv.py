import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from ..repositories.records_rep import read_export_rows
from .access_control import require_admin


OUTPUT_DIR = Path(__file__).resolve().parents[3] / "out"


def _nested_row(columns, row):
    record = {}
    for column, value in zip(columns, row):
        *parents, field = column.split(".")
        target = record
        for parent in parents:
            target = target.setdefault(parent, {})
        target[field] = value
    return record


def _add_xml_fields(element, fields):
    for name, value in fields.items():
        child = ET.SubElement(element, name)
        if isinstance(value, dict):
            _add_xml_fields(child, value)
        elif value is not None:
            child.text = str(value)


def write_exports(columns, rows, output_dir, item_name):
    try:
        import yaml
    except ModuleNotFoundError as exc:
        if exc.name != "yaml":
            raise
        raise ValueError("Установите PyYAML командой python -m pip install -r requirements.txt") from exc

    records = [_nested_row(columns, row) for row in rows]
    root = ET.Element("data")
    for record in records:
        _add_xml_fields(ET.SubElement(root, item_name), record)
    ET.indent(root)

    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output_dir) as staging_dir:
        staging = Path(staging_dir)
        with (staging / "data.csv").open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([column.replace(".", "_") for column in columns])
            writer.writerows(rows)
        (staging / "data.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        ET.ElementTree(root).write(staging / "data.xml", encoding="utf-8", xml_declaration=True)
        (staging / "data.yaml").write_text(
            yaml.safe_dump(records, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        for file in staging.iterdir():
            file.replace(output_dir / file.name)


def export_records(actor):
    require_admin(actor)
    columns, rows = read_export_rows()
    try:
        write_exports(columns, rows, OUTPUT_DIR, "record")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Не удалось сохранить файлы экспорта: {exc}") from exc
    return len(rows), OUTPUT_DIR
