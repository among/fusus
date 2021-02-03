from fusus.lakhnawi import Lakhnawi


def main():
    Lw = Lakhnawi()
    print("Reading PDF")
    Lw.getPages(None)
    print("\nExporting TSV")
    Lw.tsvPages(None)
    print("Closing")
    Lw.close()


if __name__ == "__main__":
    main()
