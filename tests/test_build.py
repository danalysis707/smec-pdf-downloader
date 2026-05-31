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

@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="PDF not downloaded")
def test_convert_pdf_to_images_skips_existing(tmp_path):
    # First run: convert normally
    images_first = convert_pdf_to_images(SAMPLE_PDF, tmp_path)
    assert len(images_first) > 0
    # Record modification times
    mtimes_before = {img: img.stat().st_mtime for img in images_first}
    # Second run: should skip all existing files
    images_second = convert_pdf_to_images(SAMPLE_PDF, tmp_path)
    assert len(images_second) == len(images_first)
    # Files should not have been modified
    for img in images_second:
        assert img.stat().st_mtime == mtimes_before[img], f"{img.name} was overwritten"
