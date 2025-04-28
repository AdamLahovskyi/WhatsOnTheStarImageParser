## Installation Guide

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

### Step 1: Clone or Download the Repository

```bash
git clone [your-repository-url]
cd whatsoncelebparser
```

### Step 2: Create and Activate Virtual Environment

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install playwright
pip install beautifulsoup4
pip install customtkinter
pip install pytz
```
## Usage

1. Start the application:
```bash
python main.py
```

2. Enter the https://whatsonthestar.com/ URL in the input field

3. Click "Fetch Data" to start scraping

4. View the results in the output area
