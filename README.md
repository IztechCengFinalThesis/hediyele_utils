# Hedileye Utils

Utility for database operations

## Description

This project is designed to handle and process various categories of data, providing tools to write, vectorize, and execute operations on structured data. It includes scripts for managing database tables, vectorizing categories, and writing processed data into different formats.

## Folder Structure

Here’s an overview of the repository's folder and file structure:

all_tables/
│   ├── added_file_names.sql       # SQL file for managing added file names
│   ├── categories.sql             # SQL script for handling categories
│   ├── categories_vectorized.sql  # SQL for vectorized category data
│   └── product.sql                # SQL script for product table
config/                            # Configuration files for the project
│   └── db_config.sql              # For getting the database connection 
data/                              # Placeholder for raw and processed data files
data_writer/                       # Scripts for writing and processing data
│   ├── data_writer_utils.py       # Utility functions for data writing
│   └── main_category_writer.py    # Main script for category data writing
migrations/                        # Database migration files 
table_executor/                    # Tools to execute table operations
│   └── table_executor_utils.py    # Executing the sql files in all tables 
vectorizer_utils/                  # Utilities for data vectorization
│   └── vectorizer_utils.py        # Vectorizing the needed things
.env                               # Environment variables file
.gitignore                         # Git ignore rules
README.md                          # Project documentation
requirements.txt                   # Python dependencies
run.py                             # Main entry point of the project

## Setup and Installation

1. Clone the repository:
   git clone <repository_url>

2. Navigate to the project directory:
   cd <project_directory>

3. Create and activate a virtual environment (optional but recommended):
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install dependencies:
   pip install -r requirements.txt

5. Configure environment variables in the `.env` file.

## Usage

### Running the Project
To execute the main script, run:
   python run.py

### Key Components
- **Data Writing**: Use scripts in `data_writer/` to process and write data.
- **Vectorization**: Utilities in `vectorizer_utils/` are available for handling vectorized representations of categories.
- **SQL Operations**: Scripts in `all_tables/` manage SQL-based operations on the database.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under [Your License]. See the `LICENSE` file for details.

## Contact

For questions or feedback, please contact [your-email@example.com].