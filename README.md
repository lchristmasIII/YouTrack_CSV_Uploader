# YouTrack Issue Importer

A Python script to import issues from a CSV file into YouTrack in batches.

## Prerequisites

- Python 3.x
- YouTrack instance with API access
- CSV file containing issues to import

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your specific values:
   - `YOUTRACK_URL`: Your YouTrack instance API endpoint
   - `AUTH_TOKEN`: Your YouTrack authentication token (generate from profile settings)
   - `PROJECT_ID`: The ID of the project where issues will be created
   - `BATCH_SIZE`: Number of issues to process in each batch (default: 50)
   - `BATCH_DELAY`: Delay between batches in seconds (default: 2)
   - `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
   - `INITIAL_RETRY_DELAY`: Initial delay for retry attempts (default: 1)
   - `CSV_FILE_PATH`: Path to your CSV file containing issues

## CSV File Format

Your CSV file should contain the following columns:
- `summary`: The issue summary/title
- `description`: The issue description

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Load issues from your CSV file
2. Process them in batches
3. Create issues in YouTrack
4. Display a summary of successful and failed batches

## Error Handling

The script includes:
- Rate limit handling with exponential backoff
- Text sanitization for YouTrack compatibility
- Batch processing to handle large datasets
- Detailed error reporting

## Notes

- Make sure your CSV file is properly formatted and contains the required columns
- The script includes retry logic for handling API rate limits
- Large datasets are processed in batches to prevent memory issues
- Text is automatically sanitized to ensure compatibility with YouTrack 