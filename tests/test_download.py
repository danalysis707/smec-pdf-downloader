import pytest
import requests
from unittest.mock import patch, MagicMock
from pathlib import Path
from download import build_answer_url, build_question_url, download_pdf, build_download_plan


def test_build_answer_url():
    url = build_answer_url(ryear="r03", cyear="2021", letter="a")
    assert url == "https://www.jf-cmca.jp/attach/test/r03/1j_seikai/2021a.pdf"


def test_build_answer_url_r05():
    url = build_answer_url(ryear="r05", cyear="2023", letter="b")
    assert url == "https://www.jf-cmca.jp/attach/test/r05/1j_seikai/2023b.pdf"


def test_build_question_url_r02_lowercase():
    url = build_question_url(ryear="r02", cyear="2020", letter="A")
    assert url == "https://www.jf-cmca.jp/attach/test/shikenmondai/1ji2020/A1ji2020.pdf"


def test_build_question_url_r05_uppercase():
    url = build_question_url(ryear="r05", cyear="2023", letter="A")
    assert url == "https://www.jf-cmca.jp/attach/test/shikenmondai/1ji2023/A1JI2023.pdf"


def test_download_pdf_success(tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"%PDF-fake-content"

    with patch("download.requests.get", return_value=mock_response):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/test.pdf", dest)
        assert result is True
        assert dest.exists()
        assert dest.read_bytes() == b"%PDF-fake-content"


def test_download_pdf_not_found(tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("download.requests.get", return_value=mock_response):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/missing.pdf", dest)
        assert result is False
        assert not dest.exists()


def test_download_pdf_server_error(tmp_path):
    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch("download.requests.get", return_value=mock_response):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/error.pdf", dest)
        assert result is False
        assert not dest.exists()


def test_download_pdf_skip_if_exists(tmp_path):
    dest = tmp_path / "existing.pdf"
    dest.write_bytes(b"already here")

    with patch("download.requests.get") as mock_get:
        result = download_pdf("https://example.com/test.pdf", dest)
        mock_get.assert_not_called()
        assert result is True


def test_download_pdf_timeout(tmp_path):
    with patch("download.requests.get", side_effect=requests.Timeout("timed out")):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/slow.pdf", dest)
        assert result is False
        assert not dest.exists()


def test_download_pdf_connection_error(tmp_path):
    with patch("download.requests.get", side_effect=requests.ConnectionError("no connection")):
        dest = tmp_path / "test.pdf"
        result = download_pdf("https://example.com/down.pdf", dest)
        assert result is False
        assert not dest.exists()


def test_build_download_plan_count():
    plan = build_download_plan()
    # 5年度 × 7科目 × 2種類（問題・解答）= 70件
    assert len(plan) == 70


def test_build_download_plan_entry_structure():
    plan = build_download_plan()
    year_label, subject, kind, url, dest = plan[0]
    assert kind in ("問題", "解答")
    assert url.startswith("https://")
    assert url.endswith(".pdf")
    assert isinstance(dest, Path)
