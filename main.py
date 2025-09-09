from ingest import NEM12Ingester

if __name__ == "__main__":
    ingester = NEM12Ingester()
    ingester.process_all_files()