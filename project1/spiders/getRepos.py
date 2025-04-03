import scrapy
import csv
import os

from urllib.parse import urlparse
from scrapy_playwright.page import PageMethod
from datetime import datetime, timezone


class ReposSpider(scrapy.Spider):
    name = "getRepos"
    custom_settings = {
    'DOWNLOAD_TIMEOUT': 180,  
    'ROBOTSTXT_OBEY': False,  
    'LOG_LEVEL': 'INFO',

    # Playwright settings
    'PLAYWRIGHT_LAUNCH_OPTIONS': {
        'headless': True,
        'timeout': 60000,
    },
    'PLAYWRIGHT_NAVIGATION_TIMEOUT': 120000,

    # User-Agent Rotation
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',

    # AutoThrottle to avoid detection
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 1,
    'AUTOTHROTTLE_MAX_DELAY': 10,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,

    # Retry Middleware
    'RETRY_ENABLED': True,
    'RETRY_TIMES': 5,

    # Proxy Middleware
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 543,
        'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,  
       
    },
    # Fake User-Agent Providers
    'FAKEUSERAGENT_PROVIDERS': [
        'scrapy_fake_useragent.providers.FakeUserAgentProvider', 
        'scrapy_fake_useragent.providers.FakerProvider',  
        'scrapy_fake_useragent.providers.FixedUserAgentProvider'
    ],
}

    
    def __init__(self, csv_path=None, max_clicks=5, *args, **kwargs):
        super(ReposSpider, self).__init__(*args, **kwargs)
        # Allow custom CSV path and max clicks via command line args
        self.csv_path = csv_path or r"C:\Users\acer\Desktop\web scraping\project1\topics.csv"
        self.max_clicks = int(max_clicks)
        
        # Validate CSV file exists before starting
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
    
    def start_requests(self):
        """Read topic links from CSV and start scraping repositories."""
        try:
            with open(self.csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Validate URL format
                    if not row.get("link") or not urlparse(row["link"]).netloc:
                        self.logger.warning(f"Invalid URL found in CSV: {row.get('link')}")
                        continue
                    
                    # Extract topic name with fallback
                    topic_name = row.get("title", "unknown_topic")
                    
                    yield scrapy.Request(
                        url=row["link"], 
                        callback=self.parse_repos,
                        errback=self.handle_error,
                        meta={
                            "topic_name": topic_name,
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                # First wait for content to be visible
                                PageMethod("wait_for_selector", "article", timeout=30000),
                                # Then execute our optimized JS to handle pagination
                                PageMethod("evaluate", self.get_pagination_script()),
                            ],
                            "download_timeout": 180,  # Extended timeout for this request
                            "dont_filter": True,  # Don't filter out duplicate requests
                        }
                    )
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
    
    def get_pagination_script(self):
        """Return the JavaScript for handling pagination."""
        return f"""async () => {{
            // Helper functions
            const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
            const log = (msg) => console.log(`[GitHub Scraper] ${{msg}}`);
            
            try {{
                let clickCount = 0;
                const maxClicks = {self.max_clicks};
                log(`Starting pagination, will attempt ${{maxClicks}} clicks...`);
                
                // Try to click the button up to maxClicks times
                while (clickCount < maxClicks) {{
                    // Wait for any loading spinners to disappear
                    await wait(1000);
                    
                    // Check if button exists and is visible
                    const button = document.querySelector('button.ajax-pagination-btn');
                    if (!button || !button.offsetParent) {{
                        log('No more Load More button, all content loaded.');
                        break;
                    }}
                    
                    // Check if button is in viewport
                    const rect = button.getBoundingClientRect();
                    if (!(rect.top >= 0 && rect.bottom <= window.innerHeight)) {{
                        log('Scrolling to Load More button...');
                        button.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        await wait(1000);
                    }}
                    
                    log(`Clicking Load More button (${{clickCount + 1}}/${{maxClicks}})...`);
                    button.click();
                    clickCount++;
                    
                    // Wait for new content to load with exponential backoff
                    // Start with 2 seconds, increase up to 8 seconds
                    const waitTime = Math.min(2000 * Math.pow(1.5, Math.min(clickCount, 4)), 8000);
                    log(`Waiting ${{waitTime/1000}} seconds for content to load...`);
                    await wait(waitTime);
                    
                    // Check for no new content - look at the number of repositories
                    const repoCount = document.querySelectorAll('article').length;
                    log(`Found ${{repoCount}} repositories after ${{clickCount}} clicks.`);
                }}
                
                log(`Pagination complete. Clicked Load More ${{clickCount}} times.`);
                return true;
            }} catch (error) {{
                console.error(`Error during pagination: ${{error.message}}`);
                // Continue anyway so we can at least get some data
                return false;
            }}
        }}"""

    def handle_error(self, failure):
        """Handle request failures."""
        request = failure.request
        self.logger.error(f"Request failed for URL: {request.url}")
        self.logger.error(f"Error type: {failure.type}")
        self.logger.error(f"Error value: {failure.value}")
        
        # Extract topic name for reporting
        topic = request.meta.get('topic_name', 'unknown')
        self.logger.error(f"Failed to scrape topic: {topic}")
        
        # You could yield an item with error info if you want to track failures
        yield {
            "status": "error",
            "topic_name": topic,
            "url": request.url,
            "error": str(failure.value)
        }
    
    def parse_repos(self, response):
        """Parse repositories after pagination has been handled."""
        topic_name = response.meta["topic_name"]
        repos = response.css("article")
        # Log number of repositories found
        repo_count = len(repos)
        self.logger.info(f"Found {repo_count} repositories for topic '{topic_name}'")
        
        if repo_count == 0:
            self.logger.warning(f"No repositories found for topic '{topic_name}'. Check selectors.")
            return
            
        for repo in repos:
            try:
                # Extract repository owner and name
                repo_name = self.extract_repo_name(repo)
                if not repo_name:
                    continue
                
                # Extract repository URL with fallback
                repo_link = self.extract_repo_link(response, repo)
                if not repo_link:
                    continue
                
                # Extract other repository details with robust handling
                yield {
                    "repo_name": repo_name,
                    "repo_link": repo_link,
                    "stars": self.extract_stars(repo),
                    "language": self.extract_language(repo),
                    "topic_name": topic_name,
                    "description": self.extract_description(repo),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                self.logger.error(f"Error processing repository: {e}")
                continue
    
    def extract_repo_name(self, repo):
        """Extract repository name with robust handling."""
        try:
            # First try the specific path
            links = repo.css("h3.f3 a::text").getall()
            if links and len(links) >= 1:
                if len(links) == 2:
                    return f"{links[0].strip()} / {links[1].strip()}"
                else:
                    return " / ".join([text.strip() for text in links])
            
            # Fallback method for different layouts
            owner = repo.css("h3.f3 a[data-hovercard-type='user']::text, h3.f3 a[data-hovercard-type='organization']::text").get()
            name = repo.css("h3.f3 a[data-hovercard-type='repository']::text").get()
            
            if owner and name:
                return f"{owner.strip()} / {name.strip()}"
            elif name:
                return name.strip()
            
            # Last resort
            all_text = repo.css("h3.f3::text").getall()
            if all_text:
                return " ".join([t.strip() for t in all_text if t.strip()])
            
            return "Unknown Repository"
        except Exception as e:
            self.logger.error(f"Error extracting repo name: {e}")
            return "Unknown Repository"
    
    def extract_repo_link(self, response, repo):
        """Extract repository link with robust handling."""
        try:
            # Try several selectors to find the repository link
            link = repo.css("h3.f3 a[data-hovercard-type='repository']::attr(href)").get()
            if not link:
                link = repo.css("h3.f3 a:last-child::attr(href)").get()
            if not link:
                link = repo.css("article a[href*='/tree/']::attr(href)").get()
                
            return response.urljoin(link) if link else None
        except Exception:
            return None
    
    def extract_stars(self, repo):
        """Extract star count with robust handling."""
        try:
            stars = repo.css("#repo-stars-counter-star::text, .octicon-star+ span::text").get()
            if stars:
                stars = stars.strip().replace(',', '')
                return stars
            return "0"
        except Exception:
            return "0"
    
    def extract_language(self, repo):
        """Extract programming language with robust handling."""
        try:
            lang = repo.css("span[itemprop='programmingLanguage']::text").get()
            return lang.strip() if lang else "Unknown"
        except Exception:
            return "Unknown"
    
    def extract_description(self, repo):
        """Extract repository description with robust handling."""
        try:
            # Try several selectors to find the description
            desc = repo.css("article > *:last-child div p::text").get()
            if not desc:
                desc = repo.css("p.color-fg-muted::text").get()
            if not desc:
                desc = repo.css("div.color-fg-muted::text").get()
                
            return desc.strip() if desc else "No description"
        except Exception:
            return "No description"