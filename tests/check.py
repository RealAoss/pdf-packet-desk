from pathlib import Path

import runpy
from tempfile import TemporaryDirectory
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]

assemble = runpy.run_path(str(ROOT / "app.py"))["assemble"]
with TemporaryDirectory() as temp:
    root = Path(temp)

    def make(name, widths):
        writer = PdfWriter()
        for width in widths:
            writer.add_blank_page(width, 600)
        path = root / name
        with path.open("wb") as file:
            writer.write(file)
        return path

    cover = make("cover.pdf", [301])
    report = make("report.pdf", [401, 402, 403, 404])
    out = root / "packet.pdf"
    assert assemble([(cover, "all"), (report, "4, 1-3, 4")], out) == 6
    assert [p.mediabox.width for p in PdfReader(out).pages] == [
        301,
        404,
        401,
        402,
        403,
        404,
    ]
    before = out.read_bytes()
    try:
        assemble([(cover, "all")], out)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Overwrite allowed")
    assert out.read_bytes() == before
    for invalid in ("0", "2-1", "9", "1,"):
        try:
            assemble([(cover, invalid)], root / "invalid.pdf")
        except ValueError:
            pass
        else:
            raise AssertionError(invalid)
    assert not (root / "invalid.pdf").exists()
