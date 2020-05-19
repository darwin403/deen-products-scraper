# [deen.nl](https://www.deen.nl/boodschappen) Product Scraper

> A [scrapy](https://scrapy.org/) bot that scrapes all available products from [deen.nl](https://www.deen.nl/boodschappen)

The above screenshot is a sample of one product entry scraped by bot. A total of `23,206` products are available and were scraped successfully by this bot as of this writing `May 19 2020`.

![](screenshot.png)

# Install

You will require `python3` and `pip3` installed. Further, to work with `pyodbc` you will need to install [windows](https://github.com/mkleehammer/pyodbc/wiki/Install#installing-on-windows) or [linux](https://github.com/mkleehammer/pyodbc/wiki/Install#installing-on-linux).

Clone and install python project dependencies:

```bash
git clone 
cd 
pip3 install -r requirements.txt
```

# Usage

Run the scrapy bot:

```bash
scrapy crawl deen --loglevel=ERROR
```

# Features

You can enable and disable various pipelines through `scrapy_deen/settings.py` by commenting/un-commenting the following lines.

```python 
# scrapy_deen/settings.py

ITEM_PIPELINES = {
   'scrapy.pipelines.images.ImagesPipeline':1
}
```

- The images pipeline downloads product images concurrently to `dump/images`
- The SQL pipeline creates / inserts / updates products to a table `products` under a database `deen`

- You can  ``

# Notes

- You can retrieve all their products by changing the items parameter: [https://www.deen.nl/boodschappen?items=10000](https://www.deen.nl/boodschappen?items=10000)
- You can create a local MS SQL Server 2017 instance for Ubuntu through [docker](https://hub.docker.com/_/microsoft-mssql-server) by running:

   ```bash
   docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=yourStrong(!)Password' -p 1433:1433 -d mcr.microsoft.com/mssql/server:2017-CU8-ubuntu
   ```

   However, you will run into an error `[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server' : file not found (0) (SQLDriverConnect)`. This is because the configuration files that `pyodbc` library is looking for are not mounted on your host system on default. You can see [here](https://stackoverflow.com/questions/44527452/cant-open-lib-odbc-driver-13-for-sql-server-sym-linking-issue) why this error occurs when the **host has installed SQL Server**. However, in our case, these files from the docker container should be me mounted to the host file system.

   More complications might arise after this is fixed. Using docker SQL server container with `pyodbc` on host is not be recommended for the faint hearted.