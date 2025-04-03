import scrapy
from scrapy_playwright.page import PageMethod

class PlaywrightSpider(scrapy.Spider):
    name = "getTopics"
    start_urls = ["https://github.com/topics"]

    def start_requests(self):
        """Initial request with Playwright enabled."""
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "button.ajax-pagination-btn"),  # Wait for button
                    PageMethod(self.click_load_more, max_clicks=5),  # Custom function to click button
                ],
            },
            callback=self.parse,
        )

    async def click_load_more(self, page, max_clicks=50):
        """Clicks 'Load More' button multiple times."""
        for _ in range(max_clicks):
            try:
                button = await page.query_selector("button.ajax-pagination-btn")
                if not button:
                    self.logger.info("No 'Load More' button found, stopping...")
                    break

                await button.click()
                await page.wait_for_timeout(3000)  # Wait for content to load
                self.logger.info("Clicked 'Load More' button")
            except Exception as e:
                self.logger.warning(f"Error clicking 'Load More': {e}")
                break

    def parse(self, response):
        """Extracts repository details after 'Load More' clicks."""
        repos = response.css("a.no-underline.flex-1")
        for repo in repos:
            title = repo.css("p.f3::text").get(default="No title").strip()
            description = repo.css("p.f5::text").get(default="No description").strip()
            link = response.urljoin(repo.attrib["href"])
            
            yield {
                "title": title,
                "description": description,
                "link": link,
            }
