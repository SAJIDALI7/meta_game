# Meta Store Data Scraper

A web scraping tool that extracts app data from the Meta Store, stores it in a MongoDB database, and provides APIs to serve this data to a frontend application.

## Project Structure

```
meta-store-scraper/
├── scraper.py            # Web scraping module
├── backend/            # Flask API
├── frontend/           # React frontend
└── README.md           # Project documentation
```

## Features

- **Web Scraper**:
  - Extracts app details from Meta Store
  - Handles dynamic content using Selenium
  - Includes error handling and anti-bot measures

- **Backend API**:
  - RESTful endpoints for app data
  - Pagination, filtering, and search
  - MongoDB integration

- **Frontend**:
  - Responsive grid/list display
  - Sorting and filtering options
  - Search functionality

## Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB
- Chrome or Chromium (for Selenium)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/meta-store-scraper.git
cd meta-store-scraper
```


### 3. Set Up MongoDB

Make sure MongoDB is installed and running on your system. The default connection URI is `mongodb://localhost:27017/meta_store`.

You can override this by setting the `MONGO_URI` environment variable:

```bash
# On Windows:
set MONGO_URI=your_mongodb_connection_string
# On macOS/Linux:
export MONGO_URI=your_mongodb_connection_string
```

### 4. Run the Scraper

```bash
python scraper.py
```

This will scrape data from the Meta Store and import it into your MongoDB database via the API.

### 5. Start the Backend Server

```bash
# Navigate to the backend directory
cd backend

# Start the Flask server
python app.py
```

The API will be available at `http://localhost:5000`.

### 6. Set Up and Run the Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/apps` | GET | Get all apps with filtering, pagination, and search |
| `/api/apps/<app_id>` | GET | Get a single app by ID |
| `/api/apps/<app_id>` | PUT | Update an app's details |
| `/api/apps/<app_id>` | DELETE | Delete an app |
| `/api/categories` | GET | Get all unique categories |
| `/api/import` | POST | Import app data |

### Query Parameters for `/api/apps`

- `page`: Page number (default: 1)
- `per_page`: Number of items per page (default: 10)
- `category`: Filter by category
- `min_rating`: Filter by minimum rating
- `q`: Search query (searches in app name and description)
- `sort_by`: Field to sort by (default: app_name)
- `sort_order`: Sort order (1 for ascending, -1 for descending)

## Testing the API with Postman

1. Import the Postman collection from the `postman/` directory.
2. Set the `baseUrl` variable to `http://localhost:5000` or your API URL.
3. Use the different request templates to test the API endpoints.

## Scraper Details

The scraper uses Selenium to handle dynamic content and JavaScript rendering. It includes:

- User-agent rotation to avoid detection
- Proper error handling and retries
- Random delays between requests

You can also import data from a JSON file:

```bash
python scraper/import_data.py --file path/to/your/data.json
```

## Implementation Notes

### Web Scraping

The scraper uses Selenium WebDriver to handle dynamic content on the Meta Store website. It navigates to the gaming section, extracts links to individual app pages, and then visits each page to extract detailed information.

### Backend

The Flask backend provides a RESTful API for accessing the app data. It includes pagination, filtering, and search functionality to efficiently handle large datasets.

### Frontend

The React frontend displays the app data in a responsive grid layout. It allows users to sort, filter, and search for apps based on various criteria.

## Future Improvements

- Add user authentication for the API
- Implement scheduled scraping to keep data up-to-date
- Add more detailed app information
- Improve error handling and monitoring
- Add unit and integration tests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
