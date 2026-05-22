import ast
import io
import os
import zipfile
from pathlib import Path


def _load_zip_helpers():
    app_path = Path(__file__).parent.parent / "app.py"
    tree = ast.parse(app_path.read_text())
    helper_names = {"_unique_zip_name", "create_zip"}
    helper_nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in helper_names
    ]
    module = ast.Module(body=helper_nodes, type_ignores=[])
    ast.fix_missing_locations(module)

    namespace = {"io": io, "os": os, "zipfile": zipfile}
    exec(compile(module, str(app_path), "exec"), namespace)
    return namespace["create_zip"]


def test_create_zip_keeps_duplicate_basenames(tmp_path):
    create_zip = _load_zip_helpers()

    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()

    first_file = first_dir / "remixed.png"
    second_file = second_dir / "remixed.png"
    first_file.write_bytes(b"first")
    second_file.write_bytes(b"second")

    zip_data = create_zip([str(first_file), str(second_file)])

    with zipfile.ZipFile(zip_data) as zf:
        assert zf.namelist() == ["remixed.png", "remixed_2.png"]
        assert zf.read("remixed.png") == b"first"
        assert zf.read("remixed_2.png") == b"second"


def test_create_zip_can_use_upload_order_prefix(tmp_path):
    create_zip = _load_zip_helpers()

    generated = tmp_path / "remixed.png"
    generated.write_bytes(b"third upload")

    zip_data = create_zip([(2, str(generated))], filename_prefix="logo_batch")

    with zipfile.ZipFile(zip_data) as zf:
        assert zf.namelist() == ["logo_batch_003.png"]
        assert zf.read("logo_batch_003.png") == b"third upload"
