from fusus.lakhnawi import Lakhnawi

Lw = Lakhnawi()
print("Reading PDF")
Lw.getPages(None)
print("\nExporting TSV")
Lw.tsvPages(None)
print("Closing")
Lw.close()
