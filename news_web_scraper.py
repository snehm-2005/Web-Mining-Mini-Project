# WEB MINING MINI PROJECT: News Website Scraper and Trending Topic Analyzer Using Python


# 1. Import required libraries

import requests
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

from bs4 import BeautifulSoup
from collections import Counter
from wordcloud import WordCloud


# 2. Create output directory

os.makedirs("output", exist_ok=True)


# 3. Select the news website RSS feed

NEWS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"


# 4. Stop words to remove during text preprocessing

stop_words = {
    "the", "is", "are", "was", "were", "a", "an",
    "and", "or", "of", "in", "on", "at", "to",
    "for", "from", "with", "by", "as", "that",
    "this", "it", "its", "be", "been", "being",
    "has", "have", "had", "will", "would", "can",
    "could", "should", "their", "they", "them",
    "he", "she", "his", "her", "we", "our",
    "you", "your", "i", "who", "what", "when",
    "where", "why", "how", "but", "not", "after",
    "before", "over", "under", "into", "about",
    "more", "than", "also", "up", "out", "new",
    "says", "said"
}


# 5. Function to scrape news data

def scrape_news():

    print("\nConnecting to BBC News RSS Feed...")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NewsAnalyzer/1.0)"
    }

    try:

        response = requests.get(
            NEWS_URL,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")

        articles = soup.find_all("item")

        news_list = []

        for article in articles:

            title = article.find("title")
            link = article.find("link")
            description = article.find("description")
            pub_date = article.find("pubDate")

            news_list.append({

                "Headline": title.get_text(strip=True) if title else "",

                "URL": link.get_text(strip=True) if link else "",

                "Description": description.get_text(
                    " ", strip=True
                ) if description else "",

                "Publication_Date": pub_date.get_text(
                    strip=True
                ) if pub_date else ""

            })

        # Remove duplicate headlines

        unique_news = []
        seen = set()

        for news in news_list:

            if news["Headline"] and news["Headline"] not in seen:

                unique_news.append(news)
                seen.add(news["Headline"])

        print("News scraping completed successfully!")
        print("Total articles extracted:", len(unique_news))

        return unique_news

    except requests.exceptions.RequestException as e:

        print("Error while connecting to website:", e)

        return []


# 6. Save extracted data into CSV

def save_news_data(news_list):

    if not news_list:
        print("No news data available.")
        return None

    df = pd.DataFrame(news_list)

    df.to_csv(
        "output/news_data.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nNews dataset saved successfully!")
    print("\nExtracted News Data:\n")

    print(df[["Headline", "Publication_Date"]].to_string(index=False))

    return df


# 7. Text preprocessing function

def preprocess_text(text):

    # Convert text into lowercase

    text = text.lower()

    # Remove URLs

    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove numbers, punctuation and special characters

    text = re.sub(r"[^a-z\s]", " ", text)

    # Split text into individual words

    words = text.split()

    # Remove stop words and very short words

    cleaned_words = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    return cleaned_words


# 8. Perform keyword frequency analysis

def analyze_keywords(df):

    all_words = []

    # Combine headlines and descriptions

    for _, row in df.iterrows():

        text = str(row["Headline"]) + " " + str(row["Description"])

        words = preprocess_text(text)

        all_words.extend(words)

    # Calculate word frequency

    word_counts = Counter(all_words)

    # Select top 20 keywords

    top_keywords = word_counts.most_common(20)

    keyword_df = pd.DataFrame(
        top_keywords,
        columns=["Keyword", "Frequency"]
    )

    # Save keyword frequency data

    keyword_df.to_csv(
        "output/keyword_frequency.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nTop 20 Frequently Occurring Keywords:\n")

    print(keyword_df.to_string(index=False))

    return word_counts, keyword_df


# 9. Generate keyword frequency bar chart

def generate_bar_chart(keyword_df):

    if keyword_df.empty:
        print("No keywords available for bar chart.")
        return

    plt.figure(figsize=(12, 6))

    plt.bar(
        keyword_df["Keyword"],
        keyword_df["Frequency"]
    )

    plt.title("Top 20 News Keywords Frequency")

    plt.xlabel("Keywords")

    plt.ylabel("Frequency")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    plt.savefig("output/keyword_bar_chart.png", dpi=300)

    plt.show()

    print("Bar chart generated successfully!")


# 10. Generate keyword distribution pie chart

def generate_pie_chart(keyword_df):

    if keyword_df.empty:
        print("No keywords available for pie chart.")
        return

    # Select top 5 keywords

    top_five = keyword_df.head(5).copy()

    # Calculate remaining frequency

    other_frequency = (
        keyword_df["Frequency"].sum()
        - top_five["Frequency"].sum()
    )

    if other_frequency > 0:

        other_row = pd.DataFrame({
            "Keyword": ["Other"],
            "Frequency": [other_frequency]
        })

        top_five = pd.concat(
            [top_five, other_row],
            ignore_index=True
        )

    plt.figure(figsize=(8, 8))

    plt.pie(
        top_five["Frequency"],
        labels=top_five["Keyword"],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Distribution of Top News Keywords")

    plt.tight_layout()

    plt.savefig("output/keyword_pie_chart.png", dpi=300)

    plt.show()

    print("Pie chart generated successfully!")


# 11. Generate word cloud

def generate_wordcloud(word_counts):

    if not word_counts:
        print("No words available for word cloud.")
        return

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=100
    ).generate_from_frequencies(word_counts)

    plt.figure(figsize=(14, 7))

    plt.imshow(wordcloud, interpolation="bilinear")

    plt.axis("off")

    plt.title("News Trending Topics Word Cloud")

    plt.tight_layout()

    plt.savefig("output/news_wordcloud.png", dpi=300)

    plt.show()

    print("Word cloud generated successfully!")


# 12. Main function

def main():

    print("=" * 55)

    print(" NEWS WEBSITE SCRAPER AND TRENDING TOPIC ANALYZER")

    print("=" * 55)

    # Step 1: Scrape news

    news_list = scrape_news()

    if not news_list:

        print("\nProject stopped because no news data was collected.")

        return

    # Step 2: Save news dataset

    df = save_news_data(news_list)

    if df is None:
        return

    # Step 3: Analyze keyword frequencies

    word_counts, keyword_df = analyze_keywords(df)

    # Step 4: Generate visualizations

    generate_bar_chart(keyword_df)

    generate_pie_chart(keyword_df)

    generate_wordcloud(word_counts)

    # Final message

    print("\n" + "=" * 55)

    print(" PROJECT EXECUTION COMPLETED SUCCESSFULLY!")

    print("=" * 55)

    print("\nGenerated files are available in the output folder.")

    print("1. news_data.csv")

    print("2. keyword_frequency.csv")

    print("3. keyword_bar_chart.png")

    print("4. keyword_pie_chart.png")

    print("5. news_wordcloud.png")


# 13. Execute main function

if __name__ == "__main__":

    main()
