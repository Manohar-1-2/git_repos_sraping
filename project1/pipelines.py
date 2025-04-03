# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import csv

class CSVPipeline:
    def open_spider(self, spider):
        """Open CSV file and write header."""
        self.file = open("topics.csv", "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=["title", "description", "link"])
        self.writer.writeheader()

    def process_item(self, item, spider):
        """Write item to CSV."""
        self.writer.writerow(item)
        return item

    def close_spider(self, spider):
        """Close CSV file."""
        self.file.close()