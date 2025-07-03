import shutil
import tempfile
import json
from pathlib import Path
import pytest
from Python_file_automation import move_file, create_subdir, unique_filename

@pytest.fixture
def setup_environment():
    temp_dir = Path(tempfile.mkdtemp())

    extension_map = {
        ".pdf": "Documents",
        ".jpg": "Images",
        ".py": "Scripts",
        ".txt": "Texts"
    }

    test_files = {
        "file1.pdf": ".pdf",
        "file2.jpg": ".jpg",
        "file3.py": ".py",
        "file4.txt": ".txt",
        "unknown.xyz": ".xyz"
    }

    for filename in test_files:
        (temp_dir / filename).write_text("sample content")

    config_path = temp_dir / "config.json"
    ext_path = temp_dir / "extensions.json"

    with open(ext_path, "w") as ef:
        json.dump(extension_map, ef)

    with open(config_path, "w") as cf:
        json.dump({
            "Main_folder": str(temp_dir),
            "log_file": str(temp_dir / "log.txt"),
            "file_extensions": str(ext_path)
        }, cf)

    yield temp_dir, extension_map, test_files

    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def patch_globals(monkeypatch, setup_environment):
    temp_dir, ext_map, _ = setup_environment
    monkeypatch.setattr("Python_file_automation.Main_Folder", temp_dir)
    monkeypatch.setattr("Python_file_automation.extension_map", ext_map)

def test_create_subdir_creates_folder(setup_environment):
    temp_dir, _, _ = setup_environment
    from Python_file_automation import Main_Folder
    Main_Folder = temp_dir
    create_subdir("TestFolder")
    assert (Main_Folder / "TestFolder").exists()


def test_move_file_to_correct_folder(setup_environment):
    temp_dir, ext_map, test_files = setup_environment
    test_file = temp_dir / "file1.pdf"
    move_file(test_file)
    expected_path = temp_dir / ext_map[".pdf"] / "file1.pdf"
    assert expected_path.exists()


def test_skip_unrecognized_extension(setup_environment, caplog):
    temp_dir, _, _ = setup_environment
    unknown_file = temp_dir / "unknown.xyz"
    move_file(unknown_file)
    assert unknown_file.exists()  # Should remain unmoved
    assert "Unrecognized extension" in caplog.text


def test_handle_duplicate_filenames(setup_environment):
    temp_dir, ext_map, _ = setup_environment
    category = ext_map[".txt"]
    dest_folder = temp_dir / category
    dest_folder.mkdir(exist_ok=True)

    (dest_folder / "file4.txt").write_text("original")

    duplicate = temp_dir / "file4.txt"
    duplicate.write_text("duplicate")

    new_path = unique_filename(dest_folder, "file4.txt")
    assert new_path.name == "file4(1).txt"
