from fusus.book import Book
from fusus.parameters import UR_DIR


AFFIFI_PATH = f"{UR_DIR}/affifi"


B = Book(cd=AFFIFI_PATH)
# print("Processing page images and OCRing them")
# B.process()
print("Exporting data as single TSV file")
B.exportTsv()