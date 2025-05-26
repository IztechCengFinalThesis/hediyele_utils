# Hediyele Utils

A comprehensive product management and price tracking system built with Streamlit.

## Description

Hediyele Utils is a web-based application designed to manage products, track prices, and perform various data operations. The system includes features for product management, price tracking, category management, and administrative functions, all wrapped in a user-friendly Streamlit interface with authentication.

## Features

- **User Authentication**: Secure login system for authorized access
- **Product Management**:
  - Add products manually or automatically
  - Bulk product upload via CSV
  - Delete products
  - View and manage existing products
- **Category Management**:
  - Edit main categories
  - Category vectorization
- **Price Tracking**:
  - Monitor price changes
  - View price charts and trends
  - Blind test analysis
- **Admin Features**:
  - User management
  - Database setup and configuration
  - System administration

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL
- **Data Processing**: Pandas, scikit-learn
- **Web Scraping**: Selenium
- **Additional Tools**: OpenAI integration

## Project Structure

```
├── config/                 # Database and configuration settings
├── data/                  # Data storage and processing
├── data_writer/           # Data writing utilities
├── db_operations/         # Database operation modules
├── price_tracking/        # Price monitoring functionality
├── selenium_utils/        # Web scraping utilities
├── st_pages/             # Streamlit page components
├── table_executor/       # Database table operations
├── utils/                # General utility functions
├── constants.py          # Global constants
├── create_initial_admin.py # Admin setup script
├── prompts.py            # System prompts
├── requirements.txt      # Project dependencies
└── run.py               # Main application entry point
```

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd hediyele_utils
   ```

2. **Set Up Python Environment**:
   ```bash
   python -m venv venv
   # For Windows
   venv\Scripts\activate
   # For Unix/MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   Create a `.env` file in the root directory with the following variables:
   ```
   DB_HOST=your_database_host
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   OPENAI_API_KEY=your_openai_api_key (if using OpenAI features)
   ```

## Usage

1. **Start the Application**:
   ```bash
   streamlit run run.py
   ```

2. **First-time Setup**:
   - Run the database setup from the sidebar menu
   - Create an initial admin user using `create_initial_admin.py`
   - Log in with your admin credentials

3. **Available Operations**:
   - Add/Delete Products
   - Bulk Upload Products
   - View and Manage Products
   - Track Price Changes
   - Manage Categories
   - View Analytics and Charts

## Development

- The project uses Streamlit for the web interface
- Database operations are handled through SQLAlchemy
- Price tracking utilizes Selenium for web scraping
- Data processing is done using Pandas and scikit-learn

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary and confidential. All rights reserved.

## Support

For support and queries, please contact the development team or raise an issue in the repository.