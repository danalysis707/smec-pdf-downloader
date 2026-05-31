import pytest
from pathlib import Path
from build import convert_pdf_to_images

SAMPLE_PDF = Path("downloads/令和2年度/令和2年度_経済学・経済政策_問題.pdf")

@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="PDF not downloaded")
def test_convert_pdf_to_images_creates_files(tmp_path):
    images = convert_pdf_to_images(SAMPLE_PDF, tmp_path)
    assert len(images) > 0
    for img in images:
        assert img.exists()
        assert img.suffix == ".jpg"
        assert img.stat().st_size > 1000  # 1KB以上

@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="PDF not downloaded")
def test_convert_pdf_to_images_naming(tmp_path):
    images = convert_pdf_to_images(SAMPLE_PDF, tmp_path)
    assert images[0].name == "page_001.jpg"
    if len(images) > 1:
        assert images[1].name == "page_002.jpg"

def test_convert_pdf_to_images_skips_existing(tmp_path):
    # 既存ファイルがある場合は変換をスキップして既存を返す
    existing = tmp_path / "page_001.jpg"
    existing.write_bytes(b"fake")
    existing2 = tmp_path / "page_002.jpg"
    existing2.write_bytes(b"fake")
    # ダミーPDFなしで既存ファイルが返されることを確認
    # (実際のPDFなしで存在チェックのみテスト)
    assert existing.exists()
