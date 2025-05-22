# Selenium Inventory Submission Automation

This project automates the process of submitting inventory counts to a website using Selenium. The script navigates to the website, selects the appropriate category, matches the jw-id with the correct publication, enters the quantity, and submits the form.

## Project Structure

```
selenium-inventory-submit
├── src
│   ├── main.py            # Main Selenium automation script
│   ├── utilities
│   │   └── __init__.py    # Utility functions for the automation script
│   └── selectors
│       └── __init__.py    # CSS selectors or XPath expressions for webpage elements
├── requirements.txt        # List of dependencies required for the project
└── README.md               # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd selenium-inventory-submit
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Configure WebDriver**:
   Make sure to have the appropriate WebDriver installed for your browser (e.g., ChromeDriver for Google Chrome). Ensure that the WebDriver is in your system's PATH.

## Usage

1. **Edit the `src/main.py` file** to configure the URL of the website and any necessary parameters for the automation.

2. **Run the script**:
   ```
   python src/main.py
   ```

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.