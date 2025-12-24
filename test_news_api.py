#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify NewsAPI and GNews.io integration
"""
from services.news_fetcher import fetch_news, fetch_from_newsapi, fetch_from_gnews

def test_news_apis():
    print("=" * 80)
    print("Testing News API Integration")
    print("=" * 80)
    
    # Test NewsAPI
    print("\n1. Testing NewsAPI.org...")
    newsapi_results = fetch_from_newsapi("Technology", max_results=3)
    if newsapi_results:
        print(f"[OK] Successfully fetched {len(newsapi_results)} articles from NewsAPI")
        print(f"     Sample: {newsapi_results[0]['title'][:60]}...")
    else:
        print("[FAIL] Failed to fetch from NewsAPI")
    
    # Test GNews
    print("\n2. Testing GNews.io...")
    gnews_results = fetch_from_gnews("Technology", max_results=3)
    if gnews_results:
        print(f"[OK] Successfully fetched {len(gnews_results)} articles from GNews")
        print(f"     Sample: {gnews_results[0]['title'][:60]}...")
    else:
        print("[FAIL] Failed to fetch from GNews")
    
    # Test combined fetch
    print("\n3. Testing combined fetch...")
    all_news = fetch_news("Technology")
    if all_news:
        print(f"[OK] Successfully fetched {len(all_news)} total articles")
        print("\n     Articles from both sources:")
        for i, article in enumerate(all_news[:5], 1):
            print(f"     {i}. [{article['source']}] {article['title'][:50]}...")
    else:
        print("[FAIL] Failed to fetch combined news")
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_news_apis()
