# 📘 Facebook GraphQL Scraper

A Python tool to scrape public Facebook posts using the unofficial GraphQL API and export the data to CSV. This script handles login, retries, error handling, and supports scraping multiple accounts or pages with customizable time limits.

> ⚠️ **Note**: This tool is for educational and research purposes only. Scraping content from Facebook may violate their [Terms of Service](https://www.facebook.com/terms.php). Use responsibly.

---

## 🔍 Features

* Scrape public posts from Facebook pages or profiles
* Login using real Facebook credentials (automated headless browser)
* Retry mechanism for handling rate-limiting or network issues
* Extracts reactions, comments, shares, text, and more
* Supports scraping posts from multiple accounts/pages
* Saves clean, structured data to CSV files
* Includes metadata like scrape time, account type, and category

---

## 🧰 Requirements

* Python 3.7+
* Google Chrome
* [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) (matching your Chrome version)
* Facebook account (for login)

Install dependencies:

```bash
pip install pandas facebook-graphql-scraper
```

---

## 🚀 Usage

### 🔹 Scrape a single account

Edit and run the script:

```python
if __name__ == "__main__":
    facebook_user_name = "AWMemorial"  
    fb_account = "your_email@example.com" 
    fb_pwd = "your_password" 
    driver_path = r"Path\To\chromedriver.exe"
    days_limit = 200  # Optional: limit by number of past days

    df = scrape_and_save_to_csv(
        facebook_user_name=facebook_user_name,
        fb_account=fb_account,
        fb_pwd=fb_pwd,
        driver_path=driver_path,
        days_limit=days_limit
    )
```

### 🔹 Scrape multiple accounts

```python
account_list = ["AWMemorial", "NASA", "natgeo"]
df = scrape_multiple_accounts(
    account_list=account_list,
    fb_account="your_email@example.com",
    fb_pwd="your_password",
    driver_path=r"Path\To\chromedriver.exe",
    days_limit=180
)
```

---

## 📁 Output

* CSV files are saved in the `facebook_data/` directory.
* Filenames are timestamped and contain account names.
* Includes fields like:

  * `post_text`
  * `timestamp`
  * `total_reactions`, `total_comments`, `total_shares`
  * Reaction breakdown (Like, Love, Wow, etc.)
  * Account metadata

---

## 📌 Notes

* Script uses a real browser session via ChromeDriver; ensure your Facebook credentials work without extra verification (2FA may break the flow).
* The `facebook_graphql_scraper` package must be installed and available.
* Be aware of Facebook’s limitations and scraping policies.

---

## 🧠 Troubleshooting

If scraping fails:

* Ensure the page has public posts
* Try using a different Facebook account
* Update ChromeDriver to match your browser version
* Watch for Facebook's anti-bot measures (e.g., CAPTCHA, login verification)
* Use a VPN if blocked in your region
