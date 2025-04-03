# GitHub Topics and Repositories Scraper

This project utilizes Scrapy spiders to automate the extraction of data from GitHub. It comprises two main components:

1. **Topic Spider**: Scrapes GitHub topics, capturing their names, links, and descriptions.
2. **Repository Spider (`getrepos`)**: For each topic obtained from the Topic Spider, this spider scrapes the top repositories, collecting pertinent details.

## Features

- **Dual Spider Architecture**:
  - **Topic Spider**: Gathers GitHub topics with their respective links and descriptions.
  - **Repository Spider (`getrepos`)**: Extracts top repositories for each topic identified by the Topic Spider.
- **Data Storage**: Saves the extracted information into CSV files for straightforward analysis.
- **Modular Design**: Enables independent operation of each spider, facilitating targeted data collection.

## Installation

To set up the project locally:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Manohar-1-2/git_repos_sraping.git
