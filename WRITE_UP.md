## What is the rationale for the technologies you have decided to use?

- **nemreader library**: This library was a lucky find: https://github.com/aguinane/nem-reader/tree/main. It's semms like another dev in the energy space purpose-built this for parsing NEM12 & NEM13 files with robust handling of the complex format, edge cases, and Australian energy market specs. If I can avoid re-inventing wheels I absolutely will and nemreader was no brainer.

- **PostgreSQL**: The gen_random_uuid() and unique constraints provided in the sample file led me to believe that this had to be a postgres table.

- **psycopg2 with execute_values**: Efficient bulk insert method for PostgreSQL. Critical for "very large files" requirement for this assessment.

- **Python**: Excellent ecosystem for data processing (tool-wise), native support in nemreader, and strong PostgreSQL integration.

- **pytz**: Reliable timezone conversion library essential for converting Australian Eastern Time to UTC as required.

## What would you have done differently if you had more time?

- **Timestamptz**: The only reason i went thorugh with forcing UTC conversions is becuase the provided technical assessment doc does not say if I can modify or add tables. I would have otherwise opted to make the table with timestamptz - to simply retain any local timestamp info.

- **Parallel processing**: Implement multiprocessing for ZIP files with multiple NEM12 files inside, processing them concurrently would help with speed.

- **Checkpointing**: Implement resume capability by tracking processed files/positions in a separate table, allowing recovery from failures mid-ingestion.

- **Metrics and monitoring**: Add Prometheus metrics or similar for production monitoring (readings/second, failure rates, processing times).

- **Schema validation**: Add validation of NEM12 file structure before attempting full parse (I am leaning on the nemreader library to save me here and letting it deal with malformed files, ideally we have our own validations separate from ingestion logic), with detailed error reporting for malformed files.

- **Unit Testing**: With more time that is where I would have started first. Tests, then allow the tests to dictate logic.

- **[Long term Ideal Implementation]**: My end goal for something like this would actually be having this be implemented as AWS Lambda functions or the like on GCP. That way we get to spin up instances of lambda to process all these large files (only when we need to) and then make available the resources when do not (lambda should automatically spin down once it completes the operation). And any loading of these large files would only be to the buffer of the lambda functions on not any services / micro-services that this implementation might otherwise sit in.

## What is the rationale for the design choices that you have made?

- **Bulk inserts over row-by-row**: Reduces network round trips and transaction overhead. Single batch of 10,000 rows is ~100x faster than individual inserts.

- **ON CONFLICT DO NOTHING**: Handles duplicates at the database level atomically, simpler and more reliable than pre-checking for existence. Idempotent operation supports re-running safely.

- **UTC conversion in Python**: Centralizes timezone logic in application layer where it's easier to test and modify, rather than relying on database timezone settings (my assumption is that I could not modify the database provided in the question)

- **Configurable batch size**: Allows tuning for different hardware and file sizes. Smaller batches use less memory, larger batches are faster but need more RAM.

- **Class-based ingester**: Encapsulates state (failed files, processed files) cleanly and makes it easy to extend with additional features and logging of information.

- **Temporary file extraction for ZIPs**: Processes one file at a time from ZIP archives.

- **Simple logging over complex frameworks**: Print statements are sufficient for the sake of this assessment and avoid the configuration overhead of logging frameworks.

- **Environment variables for config**: Standard practice, keeps credentials out of code, easy to deploy across different environments. Exmaple file provided tells the next dev how to set their own local .env

- **Separate parser and DB modules**: Separation of concerns makes testing easier and allows swapping implementations (e.g., different database or parser) without affecting other components. 