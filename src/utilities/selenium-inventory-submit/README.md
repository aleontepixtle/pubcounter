# Selenium Inventory Submission Automation

This project automates the process of submitting inventory counts to a website using Selenium. The script navigates to the website, selects the appropriate category, matches the jw-id with the correct publication, enters the quantity, and submits the form.

## Project Structure

```
selenium-inventory-submit
├── src
│   ├── main.py              # Main Selenium automation script
│   ├── publication_input.py # Publication data handling
│   └── utils.py             # Utility functions
├── data                      # Data directory for inventory files
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image configuration
├── docker-compose.yml        # Docker Compose configuration
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd selenium-inventory-submit
   ```

2. **Configure environment variables**:
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env with your credentials and language
   nano .env  # or use your preferred editor
   ```

   Set your credentials and optionally the language:
   ```env
   JW_USERNAME=your_username
   JW_PASSWORD=your_password
   JW_TOTP_SECRET=your_totp_secret
   LANGUAGE=en  # Optional: language code or full name
   ```

3. **Build and run with Docker Compose**:
   ```bash
   # Build the Docker image
   docker-compose build

   # Run the automation
   docker-compose up
   ```

   The script will run in headless mode inside the container.

### Available Languages

The script supports the following languages (use either the code or full name):

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| ar | Arabic |
| bn | Bengali |
| ceb | Cebuano |
| zh-CN | Chinese Mandarin (Simplified) |
| zh-TW | Chinese Mandarin (Traditional) |
| hr | Croatian |
| ka | Georgian |
| gu | Gujarati |
| hil | Hiligaynon |
| hi | Hindi |
| ilo | Iloko |
| id | Indonesian |
| it | Italian |
| ja | Japanese |
| jv | Javanese |
| ko | Korean |
| ml | Malayalam |
| my | Myanmar |
| pl | Polish |
| ro | Romanian |
| ru | Russian |
| si | Sinhala |
| tl | Tagalog |
| ta | Tamil |
| th | Thai |
| tr | Turkish |
| uk | Ukrainian |
| ur | Urdu |
| vi | Vietnamese |

### Language Selection Methods

You have three options for specifying the language:

**Method 1: Environment Variable (Recommended for Docker)**
```bash
# In your .env file
LANGUAGE=en  # or 'English', 'es', 'Spanish', etc.

# Then run
docker-compose up
```

**Method 2: Command-Line Argument**
```bash
# Edit docker-compose.yml and change the command line:
command: python src/main.py --non-interactive --language en

# Or run directly with docker:
docker-compose run --rm selenium-automation python src/main.py --non-interactive --language Spanish
```

**Method 3: One-off Override**
```bash
# Run with a specific language without editing files
docker-compose run --rm selenium-automation python src/main.py --non-interactive --language fr
```

### Docker Commands

```bash
# Build the image
docker-compose build

# Run once and exit
docker-compose up

# Run with a different language (one-time)
docker-compose run --rm selenium-automation python src/main.py --non-interactive --language es

# Run in background (if you modified docker-compose.yml for continuous running)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild and run
docker-compose up --build
```

## Alternative: Local Python Setup

If you prefer to run without Docker:

### Prerequisites
- Python 3.11+ installed
- Chrome browser installed

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd selenium-inventory-submit
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the script**:

   Interactive mode (with prompts):
   ```bash
   python src/main.py
   ```

   Non-interactive mode with language selection:
   ```bash
   # Using language code
   python src/main.py --non-interactive --language en

   # Using full language name
   python src/main.py --non-interactive --language Spanish

   # Or set in .env file and run
   python src/main.py --non-interactive
   ```

   **Note**: The script runs in headless mode by default (no visible browser). To see the browser in action, you'll need to comment out the headless arguments in `src/main.py:25-28`.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.