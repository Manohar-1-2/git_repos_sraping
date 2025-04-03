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

To set up the project locally, follow these steps:

### 1. **Clone the Repository**

```bash
git clone https://github.com/Manohar-1-2/git_repos_sraping.git
```

### 2. **Navigate to the Project Directory**

```bash
cd git_repos_sraping
```

### 3. **Create a Virtual Environment (Optional but Recommended)**

It's good practice to use a virtual environment to manage dependencies. Create and activate one:

- **For Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **For macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. **Install Required Dependencies**

Ensure you have Python 3.9 or higher installed. Then, install the necessary packages:

```bash
pip install -r requirements.txt
```

### 5. **Install Playwright Browsers**

Since this project uses `scrapy-playwright`, you need to install the required browsers:

```bash
playwright install
```

## Running the Scrapers

### 1. **Run the Topic Spider**

Execute the Topic Spider to scrape GitHub topics:

```bash
scrapy crawl getTopics -o topics.csv
```

This will generate a `topics.csv` file containing the names, links, and descriptions of GitHub topics.

### 2. **Run the Repository Spider (`getrepos`)**

With `topics.csv` in place, run the `getrepos` spider to scrape top repositories for each topic:

```bash
scrapy crawl getRepos -o repos.csv
```

The data will be saved into `repos.csv`.

### 3. **Access the Data**

- `topics.csv`: Contains the following fields:
  - **title**: Name of the GitHub topic.
  - **link**: Link to the topic page.
  - **description**: Brief description of the topic.

- `repos.csv`: Contains the following fields:
  - **repo_name**: Name of the repository.
  - **stars**: Number of stars the repository has received.
  - **description**: Brief description of the repository.
  - **repo_link**: Direct link to the repository.
  - **language**: Most used programing language in project.
  - **topic_name**: Topic of repository.



