Scrapy
======
https://docs.scrapy.org/en/latest/intro/install.html


https://docs.scrapy.org/en/latest/intro/tutorial.html

https://medium.com/better-programming/how-to-turn-the-web-into-data-with-python-and-scrapy-7bad725cf5a

# Getting Started
```
scrapy startproject web_scraper .
```

This will create a basic project in the current directory with the following structure:

```
scrapy.cfg
web_scraper/
    __init__.py
    items.py
    middlewares.py
    pipelines.py
    settings.py
    spiders/
        __init__.py
```

# Building Our First Spider With XPath queries

We'll create a new Python file at this path /web_scraper/spiders/live_code_stream.py (View code)

## Run the spider
As we’re already inside the web_scraper folder in the command prompt, let’s execute our spider and fill the result inside a new file lcs.json

```
scrapy crawl lcs -o lcs.json
```

## Results

When the above code executes, we’ll see a new file lcs.json in our project folder.

Here are the contents of this file:

```
[
    {"logo": "Live Code Stream"}
]
```

# Another Spider With CSS Query Selectors
Most of us love sports, and when it comes to football, it’s my personal favorite.

Football tournaments are organized frequently throughout the world. There are several websites that provide a live feed of match results while they’re being played. But most of these websites don’t offer an official API.

In turn, it creates an opportunity for us to use our web-scraping skills to extract meaningful information by directly scraping their website.

For example, let’s have a look at the https://www.livescore.cz/ website.

We can retrieve information like:

    Tournament name
    Match time
    Team 1 name (e.g., country, football club, etc.)
    Team 1 goals
    Team 2 name (e.g., country, football club, etc.)
    Team 2 goals
    Etc.

In our code example, we’ll be extracting tournament names that have matches today.

Let’s create a new spider in our project to retrieve the tournament names. I’ll name this file livescore_t.py. (View code)

## Run the newly created spider
scrapy crawl LiveScoreT -o ls_t.json

## Results

This is what our web spider has extracted on November 18 from livescore.cz. Remember that the output may change every day.


# A More Advanced Use Case
In this section, instead of just retrieving the tournament name, we’ll go the next mile and get the complete details of the tournaments and their matches.

Create a new file inside /web_scraper/web_scraper/spiders/, and name it livescore.py.

# Run the example
scrapy crawl LiveScore -o ls.json


## Conclusion

Data analysts often use web scraping because it helps them in collecting data to predict the future. Similarly, businesses use it to extract emails from web pages, as it’s an effective method for lead generation. We can even use it to monitor the prices of products.

In other words, web scraping has many use cases, and Python is completely capable to do it.


##  Task

https://www.pluralsight.com/guides/implementing-web-scraping-with-scrapy