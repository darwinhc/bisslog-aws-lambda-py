import os
import zipfile
from pathlib import Path

import pytest

from bisslog_aws_lambda.aws_lambda.lambda_aws_packager import LambdaAWSPackager


@pytest.fixture
def packager():
    return LambdaAWSPackager()


@pytest.fixture
def handler_file(tmp_path):
    handler_folder = tmp_path / "framework" / "lambda_aws"
    handler_folder.mkdir(parents=True)
    handler_path = handler_folder / "my_handler.py"
    handler_path.write_text('def handler(event, context): return "ok"')
    return handler_path


@pytest.fixture
def src_folder(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')")
    (src / "util.py").write_text("def helper(): pass")
    return src


def test_generate_zip_file_creates_valid_zip(packager, handler_file, src_folder, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    zip_path = packager.generate_zip_file(
        handler_name="my_handler",
        src_folders=str(src_folder),
        handlers_folder=str(handler_file.parent)
    )

    assert Path(zip_path).is_file()
    with zipfile.ZipFile(zip_path) as z:
        files = z.namelist()
        assert "lambda_function.py" in files
        assert "src/main.py" in files
        assert "src/util.py" in files


def test_lambda_function_content_is_handler_code(packager, handler_file, src_folder, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    zip_path = packager.generate_zip_file(
        handler_name="my_handler",
        src_folders=str(src_folder),
        handlers_folder=str(handler_file.parent)
    )

    with zipfile.ZipFile(zip_path) as z:
        with z.open("lambda_function.py") as f:
            content = f.read().decode()
            assert 'def handler(event, context)' in content


def test_batch_mode_zips_all_handlers(packager, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    handler_dir = tmp_path / "framework" / "lambda_aws"
    handler_dir.mkdir(parents=True)
    (handler_dir / "handler_a.py").write_text("a = 1")
    (handler_dir / "handler_b.py").write_text("b = 2")

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "common.py").write_text("c = 3")

    zip_files = packager(
        handler_name=None,
        src_folders=str(src_dir),
        handlers_folder=str(handler_dir)
    )

    assert len(zip_files) == 2
    for path in zip_files:
        assert Path(path).is_file()
        with zipfile.ZipFile(path) as z:
            assert "lambda_function.py" in z.namelist()
            assert "src/common.py" in z.namelist()


def test_excludes_handlers_folder_from_sources(packager, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    handler_dir = tmp_path / "framework" / "lambda_aws"
    handler_dir.mkdir(parents=True)
    (handler_dir / "my_handler.py").write_text("print('handler')")

    # src folder includes handler dir, should be ignored
    src_dir = handler_dir

    zip_path = packager.generate_zip_file(
        handler_name="my_handler",
        src_folders=str(src_dir),
        handlers_folder=str(handler_dir)
    )

    with zipfile.ZipFile(zip_path) as z:
        assert "lambda_function.py" in z.namelist()
        # handler dir content should not be duplicated
        assert "framework/lambda_aws/my_handler.py" not in z.namelist()


def test_raises_if_handler_not_found(packager, tmp_path):
    with pytest.raises(FileNotFoundError):
        packager.generate_zip_file(
            handler_name="missing_handler",
            src_folders="src",
            handlers_folder=str(tmp_path)
        )


def test_raises_if_src_folder_not_found(packager, tmp_path):
    handler_dir = tmp_path / "framework" / "lambda_aws"
    handler_dir.mkdir(parents=True)
    (handler_dir / "my_handler.py").write_text("")

    with pytest.raises(FileNotFoundError):
        packager.generate_zip_file(
            handler_name="my_handler",
            src_folders="nonexistent",
            handlers_folder=str(handler_dir)
        )
