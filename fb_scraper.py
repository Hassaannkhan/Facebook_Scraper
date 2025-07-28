import pandas as pd
import json
from fb_graphql_scraper.facebook_graphql_scraper import FacebookGraphqlScraper as fb_graphql_scraper
import os
from datetime import datetime
import time

def scrape_and_save_to_csv(facebook_user_name, fb_account, fb_pwd, driver_path, days_limit=None, max_retries=3):
    """
    Scrape Facebook posts and save the data to a CSV file with enhanced error handling
    
    Args:
        facebook_user_name: Facebook username or page name to scrape
        fb_account: Your Facebook login email
        fb_pwd: Your Facebook password
        driver_path: Path to chromedriver executable
        days_limit: Number of days to look back for posts (None for all posts)
        max_retries: Maximum number of retry attempts
    """
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            
            # Initialize scraper
            fb_spider = fb_graphql_scraper(
                fb_account=fb_account, 
                fb_pwd=fb_pwd, 
                driver_path=driver_path
            )
            
            print(f"Scraping posts for {facebook_user_name}...")
            
            scrape_params = {
                'fb_username_or_userid': facebook_user_name,
                'display_progress': True
            }
            
            if days_limit is not None:
                scrape_params['days_limit'] = days_limit
            
            res = fb_spider.get_user_posts(**scrape_params)
            
            # Check if we got valid data
            if not res or 'data' not in res or not res['data']:
                print(f"No data retrieved on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print("Waiting 30 seconds before retry...")
                    time.sleep(30)
                    continue
                else:
                    print("Failed to retrieve data after all attempts")
                    return None
            
            posts_df = pd.DataFrame(res['data'])
            
            if posts_df.empty:
                print(f"Empty DataFrame on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print("Waiting 30 seconds before retry...")
                    time.sleep(30)
                    continue
                else:
                    print("No posts found after all attempts")
                    return None
            
            print(f"Successfully retrieved {len(posts_df)} posts")
            
            posts_df = process_facebook_data(posts_df, res, facebook_user_name)
            
            # Save to CSV
            filename = save_to_csv(posts_df, facebook_user_name)
            
            print(f"Data saved to {filename}")
            print(f"Total posts scraped: {len(posts_df)}")
            
            # Close the spider
            try:
                fb_spider.driver.quit()
            except:
                pass
                
            return posts_df
            
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print("Waiting 60 seconds before retry...")
                time.sleep(60)
            else:
                print("All attempts failed")
                # Try to close driver if it exists
                try:
                    if 'fb_spider' in locals():
                        fb_spider.driver.quit()
                except:
                    pass
                return None

def process_facebook_data(posts_df, res, facebook_user_name):
    """
    Process and clean the scraped Facebook data
    """
    if 'owing_profile' in posts_df.columns:
        posts_df['profile_type'] = posts_df['owing_profile'].apply(
            lambda x: x.get('__typename') if isinstance(x, dict) else None
        )
        posts_df['profile_name'] = posts_df['owing_profile'].apply(
            lambda x: x.get('name') if isinstance(x, dict) else None
        )
        posts_df['profile_id'] = posts_df['owing_profile'].apply(
            lambda x: x.get('id') if isinstance(x, dict) else None
        )
        posts_df.drop('owing_profile', axis=1, inplace=True)
    
    if 'sub_reactions' in posts_df.columns:
        reaction_types = ['Like', 'Haha', 'Love', 'Care', 'Wow', 'Sad', 'Angry']
        for reaction in reaction_types:
            posts_df[f'reaction_{reaction}'] = posts_df['sub_reactions'].apply(
                lambda x: x.get(reaction, 0) if isinstance(x, dict) else 0
            )
        posts_df.drop('sub_reactions', axis=1, inplace=True)
    
    column_mapping = {
        'reaction_count.count': 'total_reactions',
        'comment_rendering_instance.comments.total_count': 'total_comments',
        'share_count.count': 'total_shares',
        'published_date': 'timestamp',
        'published_date2': 'date',
        'context': 'post_text'
    }
    
    existing_columns = {old: new for old, new in column_mapping.items() if old in posts_df.columns}
    posts_df.rename(columns=existing_columns, inplace=True)
    
    # Add account information
    posts_df['account_name'] = facebook_user_name
    
    try:
        posts_df['account_type'] = res['profile'][2].strip() if len(res.get('profile', [])) > 2 else ""
        posts_df['account_category'] = res['profile'][3].strip() if len(res.get('profile', [])) > 3 else ""
        posts_df['account_website'] = res['profile'][4] if len(res.get('profile', [])) > 4 else ""
        posts_df['account_followers'] = res['profile'][5] if len(res.get('profile', [])) > 5 else ""
    except (IndexError, KeyError):
        posts_df['account_type'] = ""
        posts_df['account_category'] = ""
        posts_df['account_website'] = ""
        posts_df['account_followers'] = ""
    
    posts_df['scrape_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return posts_df

def save_to_csv(posts_df, facebook_user_name):
    """
    Save the DataFrame to a CSV file
    """
    output_dir = "facebook_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{output_dir}/{facebook_user_name}_{timestamp}.csv"
    
    posts_df.to_csv(filename, index=False, encoding='utf-8')
    
    return filename

def scrape_multiple_accounts(account_list, fb_account, fb_pwd, driver_path, days_limit=None):
    """
    Scrape multiple Facebook accounts
    
    Args:
        account_list: List of Facebook usernames/page names to scrape
        fb_account: Your Facebook login email
        fb_pwd: Your Facebook password
        driver_path: Path to chromedriver executable
        days_limit: Number of days to look back for posts (None for all posts)
    """
    all_data = []
    
    for i, username in enumerate(account_list):
        print(f"\n{'='*50}")
        print(f"Scraping account {i+1} of {len(account_list)}: {username}")
        print(f"{'='*50}")
        
        df = scrape_and_save_to_csv(
            facebook_user_name=username,
            fb_account=fb_account,
            fb_pwd=fb_pwd,
            driver_path=driver_path,
            days_limit=days_limit
        )
        
        if df is not None:
            all_data.append(df)
            print(f"✅ Successfully scraped {len(df)} posts from {username}")
        else:
            print(f"❌ Failed to scrape {username}")
        
        if i < len(account_list) - 1:
            print("Waiting 2 minutes before next account...")
            time.sleep(120)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_filename = save_to_csv(combined_df, "combined_accounts")
        print(f"\n📊 Combined data saved to {combined_filename}")
        print(f"Total posts from all accounts: {len(combined_df)}")
        return combined_df
    else:
        print("\n❌ No data was successfully scraped from any account")
        return None

if __name__ == "__main__":
    facebook_user_name = "AWMemorial"  
    
    fb_account = ""
    fb_pwd = "" 
    driver_path = r"C:\Users\hp\Downloads\Hassaan\chromedriver-win64\chromedriver.exe"
    
    days_limit = 200  
    
    print("Starting Facebook scraping...")
    df = scrape_and_save_to_csv(
        facebook_user_name=facebook_user_name,
        fb_account=fb_account,
        fb_pwd=fb_pwd,
        driver_path=driver_path,
        days_limit=days_limit
    )
    
    if df is not None:
        print("\nPreview of the data:")
        print(df.head())
        print(f"\nDataFrame info:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("\n❌ Scraping failed. This could be due to:")
        print("1. Facebook's anti-bot protection")
        print("2. Account restrictions or login issues")
        print("3. The page/user has no public posts")
        print("4. Network connectivity issues")
        print("5. Changes in Facebook's GraphQL API")
        
        print("\n💡 Suggestions:")
        print("- Try using a different Facebook account")
        print("- Make sure the target page/user exists and has public posts")
        print("- Check your internet connection")
        print("- Try scraping a smaller, more active page first")
        print("- Update your chromedriver to the latest version")
    
