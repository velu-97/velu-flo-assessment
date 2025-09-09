import os
import time
import zipfile
import tempfile
from pathlib import Path
from parse import parse_nem12_file
from db import bulk_insert_readings
from config import DATA_FOLDER, BATCH_SIZE

class NEM12Ingester:
    def __init__(self, data_folder=DATA_FOLDER, batch_size=BATCH_SIZE):
        self.data_folder = Path(data_folder)
        self.batch_size = batch_size
        self.failed_files = []
        self.processed_files = []
        
    def process_all_files(self):
        #the spec file linked in the email only mentions csv and zip formats & the nemreader repo itself has zip file examples
        nem_files = list(self.data_folder.glob('*.csv'))
        zip_files = list(self.data_folder.glob('*.zip'))
        
        if not nem_files and not zip_files:
            print(f"No NEM12 csv or ZIP files found in {self.data_folder}")
            return
        
        print(f"Found {len(nem_files)} NEM12 csv file(s) and {len(zip_files)} ZIP file(s) to process")
        
        for file_path in nem_files:
            self.process_file(file_path)
            
        for zip_path in zip_files:
            self.process_zip_file_streaming(zip_path)
            
        self.print_summary()
        
    def process_file(self, file_path):
        print(f"\nProcessing: {file_path.name}")
        start_time = time.time()
        
        readings, error = parse_nem12_file(file_path)
        
        if error:
            print(f"Failed to parse {file_path.name}: {error}")
            self.failed_files.append((file_path.name, error))
            return
            
        if not readings:
            print(f"No readings found in {file_path.name}")
            self.processed_files.append((file_path.name, 0))
            return
            
        print(f"Parsed readings, starting bulk insert...")
        
        inserted_count = bulk_insert_readings(readings, self.batch_size)
        
        elapsed = time.time() - start_time
        self.processed_files.append((file_path.name, inserted_count))
        
        print(f"Inserted {inserted_count} readings in {elapsed:.2f}s")
              
    def process_zip_file_streaming(self, zip_path):
        print(f"\nProcessing ZIP: {zip_path.name}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                nem_files_in_zip = [
                    f for f in zip_ref.namelist()
                ]
                
                if not nem_files_in_zip:
                    print(f"No NEM12 csv files found in {zip_path.name}")
                    return
                    
                print(f"Found {len(nem_files_in_zip)} NEM12 csv file(s) in ZIP")
                
                for file_name in nem_files_in_zip:
                    #i noticed some nem12 files in the example zips actually have no file extenstion ... pain. Temp file route will suffice to read them
                    with tempfile.NamedTemporaryFile(suffix='.csv', delete=True) as temp_file:
                        print(f"Extracting and processing: {file_name}")
                        
                        with zip_ref.open(file_name) as source:
                            temp_file.write(source.read())
                            temp_file.flush()
                            
                        self.process_file(zip_path)
                        
        except Exception as e:
            print(f"Failed to process ZIP {zip_path.name}: {e}")
            self.failed_files.append((zip_path.name, str(e)))
            
    def print_summary(self):
        print("\n====PROCESSING SUMMARY====")

        if self.processed_files:
            print("\nSuccessfully processed files:")
            for filename, inserted in self.processed_files:
                print(f"  {filename}: {inserted} readings inserted")
                
        if self.failed_files:
            print("\nFailed files:")
            for filename, error in self.failed_files:
                print(f"  {filename}: {error}")